"""
fitting.py – XPS peak fitting engine using lmfit.

Supported lineshapes
--------------------
  gaussian        – pure Gaussian (amplitude at peak max, FWHM parameterised)
  lorentzian      – pure Lorentzian
  pseudo_voigt_gl – linear GL mix: (1‑η)·G + η·L  (η = Lorentzian fraction)
  asymmetric_gl   – GL mix with independent left/right FWHM
  doniach_sunjic  – metallic asymmetric lineshape
  ds_g            – DS+G: DS core × Gaussian convolution (formerly "la_casaxps")
  la_casaxps      – TRUE CasaXPS LA(α,β,m): asymmetric base Lorentzian + integer-kernel Gauss conv

Backgrounds
-----------
  shirley         – iterative Shirley (Proctor & Sherwood 1982)
  linear          – straight‑line between endpoints
  none            – flat zero

Spin‑orbit constraints are handled via lmfit parameter expressions.
"""

from __future__ import annotations

import logging
import warnings
from typing import Any

import numpy as np
from lmfit import Model, Parameters
from scipy.integrate import trapezoid

log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Lineshape functions (all FWHM‑parameterised, amplitude = peak maximum)
# ─────────────────────────────────────────────────────────────────────────────

_LN2 = np.log(2.0)
_SQRT_PI_4LN2 = np.sqrt(np.pi / (4.0 * _LN2))  # ≈ 1.06447


def _gaussian(x: np.ndarray, amplitude: float, center: float, fwhm: float) -> np.ndarray:
    """Gaussian; amplitude is the peak maximum value."""
    return amplitude * np.exp(-4.0 * _LN2 * ((x - center) / fwhm) ** 2)


def _lorentzian(x: np.ndarray, amplitude: float, center: float, fwhm: float) -> np.ndarray:
    """Lorentzian; amplitude is the peak maximum value."""
    hwhm = fwhm / 2.0
    return amplitude * hwhm ** 2 / ((x - center) ** 2 + hwhm ** 2)


def _pseudo_voigt_gl(
    x: np.ndarray,
    amplitude: float,
    center: float,
    fwhm: float,
    gl_ratio: float,
) -> np.ndarray:
    """
    Pseudo‑Voigt as a linear combination of Gaussian and Lorentzian.

    gl_ratio : Lorentzian fraction  (0 = pure Gaussian, 1 = pure Lorentzian)
    """
    eta = float(np.clip(gl_ratio, 0.0, 1.0))
    return (1.0 - eta) * _gaussian(x, amplitude, center, fwhm) + eta * _lorentzian(
        x, amplitude, center, fwhm
    )


def _asymmetric_gl(
    x: np.ndarray,
    amplitude: float,
    center: float,
    fwhm: float,
    asymmetry: float,
    gl_ratio: float,
) -> np.ndarray:
    """
    Asymmetric GL pseudo‑Voigt with independent asymmetry parameter.

    fwhm      : base FWHM (used on the low‑BE side, i.e. x ≤ center)
    asymmetry : broadening factor for the high‑BE side;
                fwhm_right = fwhm × (1 + asymmetry).  0 = symmetric.
    gl_ratio  : common Lorentzian fraction for both sides.

    Both halves meet at x = center with value = amplitude.
    """
    asym = float(np.clip(asymmetry, 0.0, 1.0))
    fwhm_r = fwhm * (1.0 + asym)
    result = np.empty_like(x, dtype=float)
    left = x <= center
    result[left] = _pseudo_voigt_gl(x[left], amplitude, center, fwhm, gl_ratio)
    result[~left] = _pseudo_voigt_gl(x[~left], amplitude, center, fwhm_r, gl_ratio)
    return result


def _doniach_sunjic(
    x: np.ndarray,
    amplitude: float,
    center: float,
    fwhm: float,
    alpha: float,
    gamma_asym: float = 0.0,
) -> np.ndarray:
    """
    Doniach‑Sunjic lineshape for metallic core‑level spectra.

      DS(x) = A · N · cos(πα/2 + (1‑α)·arctan((c‑x)/γ))
                    ─────────────────────────────────────────
                         ((c‑x)² + γ²)^((1‑α)/2)
              × exp(−gamma_asym · max(0, x−c))

    where γ = fwhm/2,  N = γ^(1‑α)/cos(πα/2)  so that DS(c) = A.
    dx = c − x so the power-law tail extends toward HIGHER BE (inelastic losses).
    gamma_asym > 0 adds an exponential envelope that limits how far the
    high-BE tail extends (0 = pure DS power-law tail, no limit).

    alpha     : asymmetry index  (0 = symmetric Lorentzian, typical 0–0.3)
    gamma_asym: exponential tail-decay rate (eV⁻¹).  0 = standard DS.
    """
    alpha      = float(np.clip(alpha, 0.0, 0.995))
    gamma_asym = max(float(gamma_asym), 0.0)
    gamma      = max(fwhm / 2.0, 1e-12)
    cos0 = np.cos(np.pi * alpha / 2.0)
    if abs(cos0) < 1e-12:
        cos0 = 1e-12
    norm = gamma ** (1.0 - alpha) / cos0
    # dx = center − x  →  positive on LOW-BE side, negative on HIGH-BE side.
    # The arctan and power-law terms produce a tail toward HIGH-BE (dx < 0).
    dx = center - x
    phase = np.pi * alpha / 2.0 + (1.0 - alpha) * np.arctan(dx / gamma)
    denom = (dx ** 2 + gamma ** 2) ** ((1.0 - alpha) / 2.0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = amplitude * norm * np.cos(phase) / denom
    # Exponential envelope to gently limit the HIGH-BE tail extent.
    # dx = center - x: negative on the HIGH-BE side (x > center).
    # We want: decay = 1 at center, tapering toward zero far into the tail.
    # Use |dx| on the high-BE side only: exp(-gamma_asym * max(x - center, 0))
    if gamma_asym > 0.0:
        tail_decay = np.exp(-gamma_asym * np.maximum(x - center, 0.0))
        result = result * tail_decay
    result = np.where(np.isfinite(result), result, 0.0)
    return result


def _ds_g_dscore_gauss(
    x: np.ndarray,
    amplitude: float,
    center: float,
    alpha: float,    # CasaXPS: dimensionless asymmetry index, 0 ≤ α < 0.5
    beta: float,     # CasaXPS: Lorentzian half-width (eV)
    m_gauss: float,  # CasaXPS: Gaussian FWHM (eV) for convolution
) -> np.ndarray:
    """
    DS+G lineshape (formerly mislabeled "LA(α,β,m) [CasaXPS]") —
    Doniach-Šunjić asymmetric core convolved analytically with a Gaussian
    instrument-broadening kernel. NOT to be confused with the true CasaXPS
    LA shape (see _la_casaxps_true), which uses a piecewise-asymmetric
    Lorentzian with point-domain Gaussian convolution.

    The DS core with asymmetry index α and Lorentzian half-width β is convolved
    with a Gaussian of FWHM m for instrument broadening.

    Tail direction: eps = x − center > 0 → HIGHER binding energy (physically
    correct: low-energy electron-hole pair excitations produce intensity on the
    high-BE side only).

    Parameters
    ----------
    alpha   : dimensionless asymmetry index, 0 ≤ α < 0.5
              (0 = symmetric Lorentzian, ~0.1–0.3 for metallic systems)
    beta    : Lorentzian half-width at half-maximum (eV); controls core width
    m_gauss : Gaussian FWHM (eV) for instrument/phonon broadening (0 = none)

    Fixes (v2)
    ----------
    1. Convolution uses a padded grid (±10·m on each side) with cosine taper
       to eliminate cliff artifacts at array boundaries.
    2. Explicit FFT convolution with a properly normalised Gaussian kernel,
       so DS tail direction is preserved regardless of m value.
    """
    alpha   = float(np.clip(alpha, 0.0, 0.495))
    beta    = max(float(beta),    1e-6)
    m_gauss = max(float(m_gauss), 0.0)

    # ── DS core evaluator (independent of m_gauss) ───────────────────────────
    #
    # eps = x − center: positive on HIGH-BE side (where tail belongs)
    # DS formula:  cos(πα/2 − (1−α)·arctan2(ε, β)) / (ε² + β²)^((1−α)/2)
    #
    # Sign convention proof:
    #   At ε >> β (high BE):  arctan2(ε, β) → +π/2
    #     phase → πα/2 − (1−α)·π/2 → −π(1−2α)/2  (negative for α < 0.5)
    #     cos(phase) > 0, and denominator grows as |ε|^(1−α)
    #     → slow power-law decay toward HIGH BE  ✓
    #   At ε << −β (low BE): arctan2(ε, β) → −π/2
    #     phase → πα/2 + (1−α)·π/2 → π/2  (for small α)
    #     cos(phase) → 0, faster falloff
    #     → steeper decay toward LOW BE  ✓

    def _ds_core(xgrid):
        """Evaluate DS kernel on arbitrary grid. Independent of m_gauss."""
        eps = xgrid - center
        r2 = eps ** 2 + beta ** 2
        r2 = np.maximum(r2, 1e-30)
        rPow = r2 ** ((1.0 - alpha) / 2.0)
        phase = np.pi * alpha / 2.0 - (1.0 - alpha) * np.arctan2(eps, beta)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            core = np.cos(phase) / rPow
        core = np.where(np.isfinite(core), core, 0.0)
        return core

    # ── No Gaussian broadening — just return normalised DS core ──────────────
    if m_gauss < 0.001:
        ds_core = _ds_core(x)
        peak_val = float(np.interp(center, x if x[-1] > x[0] else x[::-1],
                                   ds_core if x[-1] > x[0] else ds_core[::-1]))
        if peak_val <= 0.0:
            peak_val = np.max(np.abs(ds_core))
        if peak_val <= 0.0:
            return np.zeros_like(x)
        return amplitude * ds_core / peak_val

    # ── Build padded grid for convolution ─────────────────────────────────────
    # Pad by ±10·m_gauss (≈ ±4.25σ) to avoid truncation artifacts.
    # The DS power-law tail decays as |ε|^(α−1), which is slow for small α,
    # so generous padding is essential.
    step = float(np.median(np.abs(np.diff(x)))) if len(x) > 1 else 0.05
    step = max(step, 1e-6)

    pad_ev = max(10.0 * m_gauss, 20.0 * beta)  # eV of padding on each side
    n_pad = int(np.ceil(pad_ev / step))
    n_pad = max(n_pad, 1)

    # Determine sort direction of input x
    ascending = (x[-1] > x[0]) if len(x) > 1 else True

    # Create padded energy grid extending beyond the data range
    if ascending:
        x_pad_lo = x[0] - n_pad * step
        x_pad_hi = x[-1] + n_pad * step
    else:
        x_pad_lo = x[-1] - n_pad * step
        x_pad_hi = x[0] + n_pad * step

    n_total = len(x) + 2 * n_pad
    x_padded = np.linspace(x_pad_lo, x_pad_hi, n_total)  # always ascending

    # Evaluate DS core on padded grid
    ds_padded = _ds_core(x_padded)

    # ── Cosine taper on pad regions ───────────────────────────────────────────
    # Smoothly ramp to zero at the array edges to kill any residual signal
    # that would cause Gibbs-like ringing in FFT convolution.
    taper = np.ones(n_total)
    if n_pad > 1:
        # Left taper: 0→1 over n_pad points (half cosine)
        taper[:n_pad] = 0.5 * (1.0 - np.cos(np.linspace(0, np.pi, n_pad)))
        # Right taper: 1→0 over n_pad points
        taper[-n_pad:] = 0.5 * (1.0 + np.cos(np.linspace(0, np.pi, n_pad)))
    ds_padded *= taper

    # ── FFT convolution with Gaussian kernel ──────────────────────────────────
    # σ_eV = m_gauss / (2√(2·ln2))  (convert FWHM to sigma)
    sigma_ev = m_gauss / (2.0 * np.sqrt(2.0 * np.log(2.0)))

    # Kernel grid centred at zero, same length as padded array (for FFT)
    n_k = len(x_padded)
    k_half = (n_k - 1) / 2.0
    k_grid = (np.arange(n_k) - k_half) * step  # eV relative to centre
    gauss_kernel = np.exp(-0.5 * (k_grid / sigma_ev) ** 2)
    gauss_kernel /= gauss_kernel.sum()  # normalise to unit area

    # FFT convolution (circular, but padding makes edge effects negligible)
    ft_ds = np.fft.rfft(ds_padded)
    ft_gk = np.fft.rfft(np.fft.ifftshift(gauss_kernel))
    ds_conv = np.fft.irfft(ft_ds * ft_gk, n=n_total)

    # ── Interpolate back to original x grid ───────────────────────────────────
    # x_padded is always ascending; np.interp handles arbitrary query points.
    result = np.interp(x, x_padded, ds_conv)

    # ── Normalise so value at x = center equals amplitude ─────────────────────
    # Interpolate at exact center rather than nearest grid point to avoid
    # normalization error when center falls between data points.
    peak_val = float(np.interp(center, x_padded, ds_conv))
    if peak_val <= 0.0:
        peak_val = np.max(np.abs(result))
    if peak_val <= 0.0:
        return np.zeros_like(x)

    result = amplitude * result / peak_val

    # Final safety: suppress any NaN/Inf
    return np.where(np.isfinite(result), result, 0.0)


# ─────────────────────────────────────────────────────────────────────────────
# Background functions
# ─────────────────────────────────────────────────────────────────────────────

def shirley_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = 1e-6,
) -> np.ndarray:
    """
    Iterative Shirley background (Proctor & Sherwood, Surf. Sci. 1982).

    Works on ascending or descending binding energy arrays.

    At each energy Eᵢ the background equals:
        B(Eᵢ) = B_high + (B_low – B_high) · ∫_{Eᵢ}^{E_max} s(E) dE
                                               ─────────────────────────
                                               ∫_{E_min}^{E_max} s(E) dE
    where s(E) = max(y(E) – B(E), 0) is the net signal.
    B_low  = y(E_min),  B_high = y(E_max)  (the endpoint levels).
    """
    if len(x) < 2:
        return np.zeros_like(y)

    # Work on ascending copy
    if x[0] > x[-1]:
        xs, ys = x[::-1].copy(), y[::-1].copy()
        flipped = True
    else:
        xs, ys = x.copy(), y.copy()
        flipped = False

    b_low = ys[0]    # background at low‑BE end
    b_high = ys[-1]  # background at high‑BE end

    B = np.linspace(b_low, b_high, len(ys))  # linear initial guess

    for _ in range(n_iter):
        B_prev = B.copy()
        signal = np.maximum(ys - B, 0.0)
        # O(n) cumulative integral from high-x end back to each point
        cum_right = np.zeros(len(ys))
        for i in range(len(ys) - 2, -1, -1):
            cum_right[i] = cum_right[i + 1] + 0.5 * (signal[i] + signal[i + 1]) * (xs[i + 1] - xs[i])
        total = cum_right[0]
        if total <= 0.0:
            break
        B = b_high + (b_low - b_high) * cum_right / total
        if np.max(np.abs(B - B_prev)) < tol:
            break

    return B[::-1] if flipped else B


def smart_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = 1e-6,
) -> np.ndarray:
    """Smart (constrained Shirley): standard Shirley clamped to never exceed data."""
    if len(x) < 2:
        return np.zeros_like(y)
    shir = shirley_background(x, y, n_iter, tol)
    return np.minimum(shir, y)


def linear_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Straight‑line background connecting the first and last data points."""
    slope = (y[-1] - y[0]) / (x[-1] - x[0]) if x[-1] != x[0] else 0.0
    return y[0] + slope * (x - x[0])


def smart_experimental_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = 1e-6,
    n_avg: int = 1,
) -> np.ndarray:
    """Experimental constrained Shirley background, closer to public Avantage
    Smart description.  The data constraint is enforced *during* iteration,
    not as a post-hoc clamp.  Where the background would exceed the data it
    locks to the data, effectively moving the Shirley start inward.  Better
    for narrow spectral windows with sloped baselines."""
    if len(x) < 2:
        return np.zeros_like(y)

    # Work on ascending copy
    if x[0] > x[-1]:
        xs, ys = x[::-1].copy(), y[::-1].copy()
        flipped = True
    else:
        xs, ys = x.copy(), y.copy()
        flipped = False

    n = len(ys)
    cap = max(1, min(n_avg, n // 4))
    b_low = float(np.mean(ys[:cap]))      # low-BE endpoint
    b_high = float(np.mean(ys[-cap:]))     # high-BE endpoint
    step = b_low - b_high

    # Linear initial guess
    B = np.linspace(b_low, b_high, n)

    for _ in range(n_iter):
        B_prev = B.copy()
        signal = np.maximum(ys - B, 0.0)
        # Cumulative integral from high-BE end (right) back to each point
        cum_right = np.zeros(n)
        for i in range(n - 2, -1, -1):
            dx = xs[i + 1] - xs[i]
            cum_right[i] = cum_right[i + 1] + (signal[i] + signal[i + 1]) / 2 * dx
        total = cum_right[0]
        if total <= 0.0:
            break

        B = b_high + step * (cum_right / total)

        # Constrain during iteration: lock to data where bg exceeds it
        B = np.minimum(B, ys)

        if np.max(np.abs(B - B_prev)) < tol:
            break

    B = np.minimum(B, ys)  # final safety clamp
    return B[::-1] if flipped else B


def _apply_endpoint_averaging(y: np.ndarray, n_avg: int) -> np.ndarray:
    """Return a copy of *y* with the first/last *n_avg* points replaced by their mean."""
    n = len(y)
    if n_avg <= 1 or n < 4:
        return y.copy()
    cap = min(n_avg, n // 4)
    if cap < 1:
        return y.copy()
    out = y.copy()
    out[:cap] = np.mean(y[:cap])
    out[-cap:] = np.mean(y[-cap:])
    return out


def shirley_linear_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = 1e-6,
    n_avg: int = 1,
) -> np.ndarray:
    """Hybrid Shirley + Linear background.

    1. Average *n_avg* points at each endpoint.
    2. Compute a linear baseline between the averaged endpoints.
    3. Subtract the linear baseline → flattened data.
    4. Iteratively compute a Shirley‑like cumulative correction on the
       flattened data, scaled by the endpoint step height.
    5. Add the correction back onto the linear baseline.
    6. Clamp so the background never exceeds the data.
    """
    if len(x) < 2:
        return np.zeros_like(y)

    # Work on ascending copy
    if x[0] > x[-1]:
        xs, ys = x[::-1].copy(), y[::-1].copy()
        flipped = True
    else:
        xs, ys = x.copy(), y.copy()
        flipped = False

    n = len(ys)
    cap = max(1, min(n_avg, n // 4))
    IL = float(np.mean(ys[:cap]))      # low‑BE endpoint
    IH = float(np.mean(ys[-cap:]))     # high‑BE endpoint

    # Linear baseline
    linear = np.linspace(IL, IH, n)

    # Flatten
    flat = ys - linear

    step_h = abs(IL - IH)
    if step_h < 1e-12:
        return linear[::-1] if flipped else linear

    B = np.zeros(n)
    for _ in range(n_iter):
        B_prev = B.copy()
        signal = np.maximum(flat - B, 0.0)
        # O(n) cumulative integral from high-x end back to each point
        cum_right = np.zeros(n)
        for i in range(n - 2, -1, -1):
            cum_right[i] = cum_right[i + 1] + 0.5 * (signal[i] + signal[i + 1]) * (xs[i + 1] - xs[i])
        total = cum_right[0]
        if total <= 0.0:
            break
        B = step_h * cum_right / total
        if np.max(np.abs(B - B_prev)) < tol:
            break

    result = np.minimum(linear + B, ys)
    return result[::-1] if flipped else result


def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Simplified Tougaard universal-cross-section background.

    Uses the three-parameter universal loss function approximation
    K(T) = B·T / (C + T²)² with B = 2866, C = 1643² (eV²). The result
    is scaled so the trailing endpoint matches the data, matching the
    frontend JS implementation in ``tougaardBackground``.
    """
    n = len(x)
    if n < 2:
        return np.zeros_like(y, dtype=float)

    B_coef, C_coef = 2866.0, 1643.0 ** 2
    xa = np.asarray(x, dtype=float)
    ya = np.asarray(y, dtype=float)
    dx = float(abs(xa[1] - xa[0]))

    # bg[i] = Σ_{j>=i} K(|x[j]-x[i]|)·y[j],  K(T) = B·T / (C + T²)².
    #
    # On a uniformly spaced grid |x[j]-x[i]| = (j-i)·dx, so the kernel depends
    # only on the index gap and this one-sided correlation collapses to a
    # convolution against a single precomputed kernel vector — evaluated in C
    # via np.convolve instead of an n-iteration Python loop (audit F7). On a
    # NONUNIFORM grid that identity does not hold, so we keep the exact
    # per-point separation loop (slower, but numerically unchanged). Never
    # substitute (j-i)·dx for the true separation unless uniformity is verified.
    diffs = np.diff(xa)
    uniform = bool(dx > 0.0 and np.max(np.abs(diffs - diffs[0])) <= 1e-6 * dx)

    if uniform:
        m = np.arange(n, dtype=float)
        T = m * dx
        k = (B_coef * T) / (C_coef + T * T) ** 2          # k[m] = K(m·dx)
        # bg[i] = Σ_{m=0}^{n-1-i} k[m]·y[i+m]  =  conv(y, reverse(k))[n-1+i]
        bg = np.convolve(ya, k[::-1])[n - 1:]
    else:
        bg = np.zeros(n)
        for i in range(n):
            T = np.abs(xa[i:] - xa[i])
            kernel = (B_coef * T) / (C_coef + T * T) ** 2
            bg[i] = float(np.sum(kernel * ya[i:]))

    bg = bg * dx
    denom = bg[-1] if bg[-1] != 0.0 else 1.0
    return bg * (float(ya[-1]) / denom)


def _la_casaxps_true(
    x: np.ndarray,
    amplitude: float,
    center: float,
    fwhm: float,
    alpha: float,
    beta: float,
    m: float,
) -> np.ndarray:
    """
    True CasaXPS LA(α, β, m) lineshape.

    Built in two steps per the CasaXPS LA manual:

    1.  Asymmetric base Lorentzian. Start with a unit-amplitude Lorentzian
        of FWHM `fwhm` centered at `center`:
            L(x) = 1 / (1 + 4·((x − center)/fwhm)²)
        Apply piecewise exponents to introduce asymmetry. CasaXPS defines
        these on a kinetic-energy axis. We use a binding-energy axis, so
        the sides flip:
            LA_base(x) = L(x)^α   for x ≥ center  (high-BE side)
            LA_base(x) = L(x)^β   for x <  center  (low-BE side)
        Increasing α relative to β SUPPRESSES the high-BE tail; decreasing
        α extends it.

    2.  Gaussian convolution with an integer-point kernel of width `m`.
        m=0 means no convolution. For m>0, build a discrete Gaussian
        kernel of length 2m+1 with σ_pts = m/3 (so the 3σ tail just
        reaches the kernel edge). Convolve with mode='same' on the
        uniform x grid.

    With α=β=1 and m=0, this reduces exactly to amplitude × L(x) (a pure
    Lorentzian of peak height = amplitude, FWHM = `fwhm`).

    Parameters
    ----------
    fwhm  : Lorentzian FWHM in eV (must be > 0)
    alpha : high-BE-side exponent, dimensionless, default 1.0, bounds (0.1, 5.0)
    beta  : low-BE-side exponent, dimensionless, default 1.0, bounds (0.1, 5.0)
    m     : Gaussian convolution kernel width in DATA POINTS (not eV);
            integer 0–499. Stored as float in lmfit, rounded to int here.
    """
    fwhm = max(float(fwhm), 1e-9)
    alpha = max(float(alpha), 1e-3)
    beta = max(float(beta), 1e-3)
    # Continuous-σ kernel: m flows through to the kernel weights as a real
    # number, so the Jacobian column for m is well-defined under lmfit's
    # finite-difference perturbation. Previously m was rounded with
    # int(round(m)), making the function locally constant in m and
    # producing a singular Hessian whenever m varied — that poisoned
    # covariance estimation for every other free param too.
    # Defensive guard preserves the prior [0, 499] cap in case a saved
    # spec or caller bypasses the lmfit bound.
    m_cont = max(0.0, min(499.0, float(m)))

    eps = x - center
    # Base unit-amplitude Lorentzian
    L = 1.0 / (1.0 + 4.0 * (eps / fwhm) ** 2)
    # Piecewise exponentiation. BE-axis: high-BE side is eps ≥ 0.
    high = eps >= 0
    base = np.where(high, np.power(L, alpha), np.power(L, beta))

    # Below ε, treat as un-convolved Lorentzian so an optimizer that lands
    # exactly at m=0 returns the bare base curve rather than degenerating.
    if m_cont < 1e-3:
        return amplitude * base

    sigma_pts = m_cont / 3.0
    # Kernel half-width: ±3.5σ captures > 99.95% of the Gaussian. Use 3.5
    # rather than 3 specifically so the kernel-length quantization step
    # `ceil(3.5σ)` doesn't coincide with integer m — that would put a
    # discrete jump in the output exactly at integer m and re-break
    # backwards compat with previously-saved (integer-m) fits. With 3.5
    # the next jump from m=N is at m = 6(N+1)/7 ≠ integer.
    half = max(1, int(np.ceil(3.5 * sigma_pts)))
    k = np.arange(-half, half + 1, dtype=float)
    kern = np.exp(-(k ** 2) / (2.0 * sigma_pts ** 2))
    kern = kern / kern.sum()

    convolved = np.convolve(base, kern, mode='same')
    # np.convolve mode='same' returns max(len(base), len(kern)) — not
    # len(base). When the input grid is shorter than the kernel, trim
    # back to len(base) so the function's len(output) == len(x) contract
    # holds. lmfit's composite-fit residual path will broadcast the
    # per-peak arrays against the data grid, so a kernel-length return
    # surfaces as a cryptic shape mismatch downstream.
    if len(convolved) > len(base):
        excess = len(convolved) - len(base)
        start = excess // 2
        convolved = convolved[start:start + len(base)]

    peak_idx = int(np.argmin(np.abs(eps)))
    peak_val = convolved[peak_idx]
    if peak_val <= 0:
        peak_val = float(np.max(convolved))
    if peak_val <= 0:
        return np.zeros_like(x)
    return amplitude * convolved / peak_val


# ─────────────────────────────────────────────────────────────────────────────
# lmfit Model factory
# ─────────────────────────────────────────────────────────────────────────────

_SHAPE_FUNCS = {
    "gaussian": _gaussian,
    "lorentzian": _lorentzian,
    "pseudo_voigt_gl": _pseudo_voigt_gl,
    "asymmetric_gl": _asymmetric_gl,
    "doniach_sunjic": _doniach_sunjic,
    "ds_g": _ds_g_dscore_gauss,
    "la_casaxps": _la_casaxps_true,
}

AVAILABLE_SHAPES = list(_SHAPE_FUNCS.keys())


def _make_peak_params(
    model: Model,
    spec: dict[str, Any],
    prefix: str,
    all_specs: list[dict],
) -> Parameters:
    """
    Build lmfit Parameters for one peak from a spec dict.

    Spec keys
    ---------
    shape          : str   – one of AVAILABLE_SHAPES
    center         : float – initial centre (eV)
    center_min     : float – lower bound   (optional)
    center_max     : float – upper bound   (optional)
    amplitude      : float – peak maximum counts
    amplitude_min  : float – lower bound   (default 0)
    fwhm           : float – full width at half max (eV)
    fwhm_min       : float – lower bound   (default 0.1)
    fwhm_max       : float – upper bound   (default 15.0)
    gl_ratio       : float – Lorentzian fraction for *_gl shapes  [0–1]
    asymmetry      : float – high-BE broadening factor for asymmetric_gl [0–1]
    alpha          : float – DS asymmetry index
    constrain_to   : str   – id of master peak (spin‑orbit slave)
    splitting      : float – centre offset from master (eV)
    area_ratio     : float – amplitude = master_amplitude × area_ratio
    fix_fwhm       : bool  – if True, lock FWHM to master value
    """
    shape = spec["shape"]
    p = model.make_params()

    center = spec.get("center", 285.0)
    amp = spec.get("amplitude", 1000.0)
    fwhm = spec.get("fwhm", 1.5)
    asymmetry = spec.get("asymmetry", 0.0)

    def _set(name, value, min_=None, max_=None, expr=None, vary=True):
        full = prefix + name
        if full not in p:
            return
        p[full].set(value=value)
        if expr is not None:
            p[full].expr = expr
            p[full].vary = False
        else:
            if min_ is not None:
                p[full].min = min_
            if max_ is not None:
                p[full].max = max_
            p[full].vary = vary

    # Constrain to a master peak (spin‑orbit doublet)?
    master_id = spec.get("constrain_to")
    if master_id is not None:
        # Find the master spec to get its prefix
        master_spec = next((s for s in all_specs if s["id"] == master_id), None)
        if master_spec is None:
            raise ValueError(f"Master peak '{master_id}' not found for spin‑orbit constraint")
        m_prefix = f"p{master_spec['id']}_"
        splitting = float(spec.get("splitting", 0.0))
        area_ratio = float(spec.get("area_ratio", 1.0))

        _set("center", center, expr=f"{m_prefix}center + {splitting}")
        _set("amplitude", amp, expr=f"{m_prefix}amplitude * {area_ratio}")
        _set("fwhm", fwhm, expr=f"{m_prefix}fwhm" if spec.get("fix_fwhm", True) else None,
             min_=spec.get("fwhm_min", 0.1), max_=spec.get("fwhm_max", 15.0))
        if shape in ("pseudo_voigt_gl", "asymmetric_gl"):
            _set("gl_ratio", spec.get("gl_ratio", 0.3),
                 expr=f"{m_prefix}gl_ratio" if spec.get("fix_fwhm", True) else None,
                 min_=0.0, max_=1.0)
        if shape == "asymmetric_gl":
            _set("asymmetry", asymmetry,
                 expr=f"{m_prefix}asymmetry" if spec.get("fix_fwhm", True) else None,
                 min_=spec.get("asymmetry_min", 0.0),
                 max_=spec.get("asymmetry_max", 1.0))
        if shape == "doniach_sunjic":
            _set("alpha", spec.get("alpha", 0.1),
                 expr=f"{m_prefix}alpha" if spec.get("fix_fwhm", True) else None,
                 min_=0.0, max_=0.5)
            _set("gamma_asym", spec.get("gamma_asym", 0.0),
                 expr=f"{m_prefix}gamma_asym" if spec.get("fix_fwhm", True) else None,
                 min_=0.0, max_=1.0)
        if shape == "ds_g":
            fix = spec.get("fix_fwhm", True)
            _set("alpha",   spec.get("alpha",   0.10), expr=f"{m_prefix}alpha"   if fix else None, min_=0.0,  max_=0.49)
            _set("beta",    spec.get("beta",    0.3),  expr=f"{m_prefix}beta"    if fix else None, min_=0.05, max_=2.0)
            _set("m_gauss", spec.get("m_gauss", 0.4),  expr=f"{m_prefix}m_gauss" if fix else None, min_=0.0,  max_=4.0)
        if shape == "la_casaxps":
            fix = spec.get("fix_fwhm", True)
            _set("alpha", spec.get("alpha", 1.0),
                 expr=f"{m_prefix}alpha" if fix else None,
                 min_=0.1, max_=5.0)
            _set("beta",  spec.get("beta",  1.0),
                 expr=f"{m_prefix}beta" if fix else None,
                 min_=0.1, max_=5.0)
            _set("m",     spec.get("m",    50.0),
                 expr=f"{m_prefix}m" if fix else None,
                 min_=0.0, max_=499.0)
        return p

    # Free (master or unconstrained) peak
    # Non-DS+G peaks (satellites, etc.) get a default ±2 eV constraint to prevent
    # the optimizer from drifting to physically unreasonable positions.
    c_min = spec.get("center_min")
    c_max = spec.get("center_max")
    if shape != "ds_g" and c_min is None:
        c_min = center - 2.0
    if shape != "ds_g" and c_max is None:
        c_max = center + 2.0
    _set("center", center, min_=c_min, max_=c_max, vary=not spec.get("fix_center", False))
    _set("amplitude", amp,
         min_=spec.get("amplitude_min", 0.0), max_=spec.get("amplitude_max"),
         vary=not spec.get("fix_amplitude", False))
    _set("fwhm", fwhm,
         min_=spec.get("fwhm_min", 0.1), max_=spec.get("fwhm_max", 15.0),
         vary=not spec.get("fix_fwhm", False))

    if shape in ("pseudo_voigt_gl", "asymmetric_gl"):
        _set("gl_ratio", spec.get("gl_ratio", 0.3), min_=0.0, max_=1.0,
             vary=not spec.get("fix_gl_ratio", False))
    if shape == "asymmetric_gl":
        _set("asymmetry", asymmetry,
             min_=spec.get("asymmetry_min", 0.0),
             max_=spec.get("asymmetry_max", 1.0),
             vary=not spec.get("fix_asymmetry", False))
    if shape == "doniach_sunjic":
        _set("alpha", spec.get("alpha", 0.1), min_=0.0, max_=0.5,
             vary=not spec.get("fix_alpha", False))
        _set("gamma_asym", spec.get("gamma_asym", 0.0), min_=0.0, max_=5.0,
             vary=not spec.get("fix_gamma_asym", False))
    if shape == "ds_g":
        _set("alpha",   spec.get("alpha",   0.10), min_=0.0,  max_=0.49,
             vary=not spec.get("fix_alpha", False))
        _set("beta",    spec.get("beta",    0.3),  min_=0.05, max_=2.0,
             vary=not spec.get("fix_beta", False))
        _set("m_gauss", spec.get("m_gauss", 0.4),  min_=0.05, max_=4.0,
             vary=not spec.get("fix_m_gauss", False))
    if shape == "la_casaxps":
        _set("alpha", spec.get("alpha", 1.0), min_=0.1, max_=5.0,
             vary=not spec.get("fix_alpha", False))
        _set("beta",  spec.get("beta",  1.0), min_=0.1, max_=5.0,
             vary=not spec.get("fix_beta", False))
        _set("m",     spec.get("m",    50.0), min_=0.0, max_=499.0,
             vary=not spec.get("fix_m", True))

    return p


# ─────────────────────────────────────────────────────────────────────────────
# Main fitting API
# ─────────────────────────────────────────────────────────────────────────────

def run_fit(
    energy: np.ndarray,
    counts: np.ndarray,
    peak_specs: list[dict[str, Any]],
    background_method: str = "shirley",
    bg_start_idx: int | None = None,
    bg_end_idx: int | None = None,
    charge_shift_ev: float = 0.0,
    fit_kws: dict | None = None,
    n_perturb: int = 0,
    manual_bg: list | None = None,
    endpoint_avg: int = 1,
) -> dict[str, Any]:
    """
    Run XPS peak fitting and return a serialisable result dict.

    Parameters
    ----------
    energy            : 1‑D array of binding energies (eV)
    counts            : 1‑D array of intensities (counts / CPS)
    peak_specs        : list of peak specification dicts (see _make_peak_params)
    background_method : 'shirley' | 'linear' | 'none'
    bg_start_idx      : slice start for background region (None → 0)
    bg_end_idx        : slice end for background region   (None → len)
    charge_shift_ev   : shift to apply to energy axis before fitting
    fit_kws           : extra kwargs forwarded to lmfit minimize

    Returns
    -------
    dict with keys: energy, fitted_y, background_y, residuals,
                    individual_peaks, statistics, charge_shift_applied, success
    """
    if len(energy) != len(counts):
        raise ValueError("energy and counts must have the same length")
    if not peak_specs:
        raise ValueError("At least one peak specification is required")

    # Apply charge correction
    energy = energy + charge_shift_ev

    # The fit runs on the ENTIRE incoming ROI; bg_start_idx / bg_end_idx
    # narrow only the anchor window used to construct the background
    # curve. Reusing the slice for both was the bug where putting bg
    # anchors inside the ROI silently chopped the fit window — and the
    # reported χ², residuals, and σ — down to that same sub-slice.
    i0 = bg_start_idx if bg_start_idx is not None else 0
    i1 = bg_end_idx if bg_end_idx is not None else len(energy)
    i0 = max(0, i0)
    i1 = min(len(energy), i1)
    # Normalize the user-supplied anchor pair: reversed order is a valid
    # choice — the frontend sends bg-start = higher BE and bg-end = lower
    # BE, so the index order depends on whether the data array is
    # BE-ascending or BE-descending. Treat the pair as an unordered
    # anchor window regardless of direction.
    if i0 > i1:
        i0, i1 = i1, i0
    # Bail to the full ROI only if the normalized window is genuinely
    # unusable (< 2 points): the integral / interp / linear-fit
    # functions below all need at least two distinct anchor points.
    if i1 - i0 < 2:
        i0, i1 = 0, len(energy)

    x = energy
    y = counts
    x_bg = energy[i0:i1]
    y_bg = counts[i0:i1]

    # ── Background ────────────────────────────────────────────────────────────
    # Integral backgrounds (Shirley, Tougaard, Smart variants) are
    # physically defined only between the user's two anchor points: the
    # integral represents inelastic-loss cumulation through the peaks
    # *between* those anchors. Computing them over the full ROI would
    # let peaks outside the anchor window contribute to the loss
    # integral, which violates the model's premise. We therefore
    # compute them on [i0:i1] and flat-hold the endpoint value across
    # the rest of the ROI — Shirley/Tougaard asymptote to the anchor
    # values by construction, so constant extension is the least-bad
    # continuation. Linear backgrounds are extrapolated across the
    # full ROI (the line is well-defined outside the anchor window).
    bg_method = background_method.lower()
    bg_inner: np.ndarray | None = None

    if manual_bg is not None and bg_method == "manual":
        # manual_bg is a list of [be, intensity] anchor points from the
        # frontend. The anchors are BE-anchored (independent of i0/i1),
        # so interpolate them across the full ROI grid.
        anchors = sorted(manual_bg, key=lambda a: a[0])
        if len(anchors) >= 2:
            anchor_x = np.array([a[0] for a in anchors])
            anchor_y = np.array([a[1] for a in anchors])
            bg = np.interp(x, anchor_x, anchor_y)
        else:
            bg = linear_background(x, y)
    elif bg_method == "shirley":
        bg_inner = shirley_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
    elif bg_method == "smart":
        bg_inner = smart_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
    elif bg_method == "smart_exp":
        bg_inner = smart_experimental_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "shirley_linear":
        bg_inner = shirley_linear_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "tougaard":
        bg_inner = tougaard_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
    elif bg_method == "linear":
        # Extrapolate the line through (E[i0], y[i0]) ↔ (E[i1-1], y[i1-1])
        # across the full ROI. The line is well-defined everywhere, so
        # constant extension would discard real information.
        if x[i1 - 1] != x[i0]:
            slope = (y[i1 - 1] - y[i0]) / (x[i1 - 1] - x[i0])
        else:
            slope = 0.0
        bg = y[i0] + slope * (x - x[i0])
    elif bg_method in ("none", "flat", "", "manual"):
        bg = np.zeros_like(y)
    else:
        raise ValueError(f"Unknown background method '{background_method}'")

    if bg_inner is not None:
        # Embed the anchor-window integral background into a full-ROI
        # array; flat-hold the endpoint value outside [i0, i1]. In the
        # common case where the user keeps bg anchors at the ROI edges
        # this is a no-op (i0=0, i1=len(y)).
        bg = np.zeros_like(y)
        if len(bg_inner) > 0:
            bg[i0:i1] = bg_inner
            if i0 > 0:
                bg[:i0] = bg_inner[0]
            if i1 < len(y):
                bg[i1:] = bg_inner[-1]

    y_sub = y - bg

    # Poisson weights: σ = √(raw counts), weight = 1/σ
    # Use raw counts (before background subtraction) for uncertainty estimate,
    # since the noise comes from the total photon counting statistics.
    # Floor at 1.0 to avoid division by zero for zero-count channels.
    sigma = np.sqrt(np.maximum(y, 1.0))
    weights = 1.0 / sigma

    # ── Build composite lmfit model ───────────────────────────────────────────
    # Sort so unconstrained (master) peaks come before constrained ones
    ordered = sorted(
        peak_specs,
        key=lambda s: 0 if s.get("constrain_to") is None else 1,
    )

    composite_model: Model | None = None
    all_params = Parameters()

    for spec in ordered:
        shape = spec.get("shape", "pseudo_voigt_gl")
        if shape not in _SHAPE_FUNCS:
            raise ValueError(f"Unknown peak shape '{shape}'. Choices: {AVAILABLE_SHAPES}")
        func = _SHAPE_FUNCS[shape]
        prefix = f"p{spec['id']}_"
        m = Model(func, prefix=prefix)
        p = _make_peak_params(m, spec, prefix, ordered)
        all_params.update(p)
        composite_model = m if composite_model is None else composite_model + m

    if composite_model is None:
        raise RuntimeError("No peaks were built")

    # ── Fit ───────────────────────────────────────────────────────────────────
    kws = {"method": "leastsq", "nan_policy": "omit"}
    if fit_kws:
        kws.update(fit_kws)

    # ── Diagnostic logging: BEFORE optimisation ──────────────────────────────
    if log.isEnabledFor(logging.DEBUG):
        log.debug("═══ FIT START ═══  method=%s  n_data=%d", kws.get('method'), len(y_sub))
        for pname, par in sorted(all_params.items()):
            log.debug("  BEFORE  %-30s value=%12.6f  vary=%-5s  expr=%s  min=%s  max=%s",
                      pname, par.value, str(par.vary), par.expr,
                      f"{par.min:.4f}" if np.isfinite(par.min) else '-inf',
                      f"{par.max:.4f}" if np.isfinite(par.max) else 'inf')

    try:
        result = composite_model.fit(y_sub, all_params, x=x, weights=weights, **kws)
    except Exception as exc:
        raise RuntimeError(f"lmfit fitting failed: {exc}") from exc

    # ── Diagnostic logging: AFTER optimisation ───────────────────────────────
    if log.isEnabledFor(logging.DEBUG):
        log.debug("═══ FIT DONE ═══  success=%s  nfev=%s  message=%s",
                  result.success, result.nfev, result.message)
        for pname, par in sorted(result.params.items()):
            init = all_params[pname].value if pname in all_params else None
            delta = f"  Δ={par.value - init:+.6f}" if init is not None and abs(par.value - init) > 1e-10 else ""
            log.debug("  AFTER   %-30s value=%12.6f  stderr=%s%s",
                      pname, par.value,
                      f"{par.stderr:.6f}" if par.stderr is not None else 'None', delta)

    # ── Perturb and refit to escape local minima ─────────────────────────
    if n_perturb > 0 and result.success:
        best_result = result
        best_redchi = result.redchi if result.redchi is not None else float('inf')
        rng = np.random.default_rng()

        for attempt in range(n_perturb):
            perturbed_params = result.params.copy()
            for pname, par in perturbed_params.items():
                if par.vary and par.value != 0:
                    # Perturb by ±15% random
                    scale = 1.0 + rng.uniform(-0.15, 0.15)
                    new_val = par.value * scale
                    # Respect bounds
                    if np.isfinite(par.min):
                        new_val = max(new_val, par.min)
                    if np.isfinite(par.max):
                        new_val = min(new_val, par.max)
                    perturbed_params[pname].set(value=new_val)
                elif par.vary and par.value == 0:
                    # For zero-valued params, add small absolute perturbation
                    perturbed_params[pname].set(value=rng.uniform(0.001, 0.05))

            try:
                trial = composite_model.fit(y_sub, perturbed_params, x=x, weights=weights, **kws)
                trial_redchi = trial.redchi if trial.redchi is not None else float('inf')
                log.debug("  PERTURB %d/%d  redchi=%.4f  (best=%.4f)",
                          attempt + 1, n_perturb, trial_redchi, best_redchi)
                if trial.success and trial_redchi < best_redchi:
                    best_result = trial
                    best_redchi = trial_redchi
                    log.debug("  *** New best found! redchi improved to %.4f", best_redchi)
            except Exception:
                log.debug("  PERTURB %d/%d  failed (exception)", attempt + 1, n_perturb)
                continue

        if best_result is not result:
            log.debug("═══ PERTURB IMPROVED FIT ═══  redchi: %.4f → %.4f",
                      result.redchi, best_redchi)
            result = best_result

    fitted_sub = result.best_fit
    fitted_y = fitted_sub + bg

    # ── Per‑peak results ──────────────────────────────────────────────────────
    individual_peaks = []
    for spec in peak_specs:
        pid = spec["id"]
        prefix = f"p{pid}_"
        peak_y = composite_model.components[
            next(i for i, c in enumerate(composite_model.components)
                 if c.prefix == prefix)
        ].eval(result.params, x=x)

        # Area by numerical integration
        area = float(trapezoid(peak_y, x))

        # Parameter extraction with stderr
        param_info: dict[str, Any] = {}
        for pname in result.params:
            if pname.startswith(prefix):
                short = pname[len(prefix):]
                par = result.params[pname]
                param_info[short] = {
                    "value": float(par.value),
                    "stderr": float(par.stderr) if par.stderr is not None else None,
                    "vary": par.vary,
                    "expr": par.expr,
                    "min": float(par.min) if np.isfinite(par.min) else None,
                    "max": float(par.max) if np.isfinite(par.max) else None,
                }

        param_info["area"] = {"value": area, "stderr": None}

        # Approximate area stderr via amplitude + fwhm propagation
        amp_par = result.params.get(prefix + "amplitude")
        fwhm_par = result.params.get(prefix + "fwhm")
        if (amp_par and fwhm_par and amp_par.stderr and fwhm_par.stderr
                and amp_par.value and fwhm_par.value):
            rel_err = np.sqrt(
                (amp_par.stderr / amp_par.value) ** 2
                + (fwhm_par.stderr / fwhm_par.value) ** 2
            )
            param_info["area"]["stderr"] = abs(area) * rel_err

        individual_peaks.append({
            "id": pid,
            "y": peak_y.tolist(),
            "params": param_info,
        })

    # ── Statistics ────────────────────────────────────────────────────────────
    n_data = len(y_sub)
    n_free = result.nvarys
    chi_sq = float(result.chisqr) if result.chisqr is not None else None
    red_chi_sq = float(result.redchi) if result.redchi is not None else None

    residuals = (y_sub - fitted_sub).tolist()

    # R‑factor (like in crystallography: sum|obs-calc| / sum|obs|)
    r_factor = (float(np.sum(np.abs(y_sub - fitted_sub)) / np.sum(np.abs(y_sub)))
                if np.sum(np.abs(y_sub)) > 0 else None)

    return {
        "success": result.success,
        "message": result.message,
        "energy": x.tolist(),
        "counts": y.tolist(),
        "fitted_y": fitted_y.tolist(),
        "background_y": bg.tolist(),
        "residuals": residuals,
        "individual_peaks": individual_peaks,
        "statistics": {
            "chi_square": chi_sq,
            "reduced_chi_square": red_chi_sq,
            "r_factor": r_factor,
            "n_data": n_data,
            "n_free_params": n_free,
            "aic": float(result.aic) if result.aic is not None else None,
            "bic": float(result.bic) if result.bic is not None else None,
        },
        "charge_shift_applied": charge_shift_ev,
    }


def compute_background_only(
    energy: np.ndarray,
    counts: np.ndarray,
    method: str = "shirley",
    start_idx: int | None = None,
    end_idx: int | None = None,
    endpoint_avg: int = 1,
) -> dict[str, Any]:
    """Return just the background array without fitting peaks."""
    i0 = start_idx if start_idx is not None else 0
    i1 = end_idx if end_idx is not None else len(energy)
    x, y = energy[i0:i1], counts[i0:i1]

    if method == "shirley":
        bg = shirley_background(x, _apply_endpoint_averaging(y, endpoint_avg))
    elif method == "smart":
        bg = smart_background(x, _apply_endpoint_averaging(y, endpoint_avg))
    elif method == "smart_exp":
        bg = smart_experimental_background(x, y, n_avg=endpoint_avg)
    elif method == "shirley_linear":
        bg = shirley_linear_background(x, y, n_avg=endpoint_avg)
    elif method == "tougaard":
        bg = tougaard_background(x, _apply_endpoint_averaging(y, endpoint_avg))
    elif method == "linear":
        bg = linear_background(x, y)
    elif method in ("none", "flat", "", "manual"):
        bg = np.zeros_like(y)
    else:
        raise ValueError(f"Unknown background method '{method}'")

    return {
        "energy": x.tolist(),
        "background": bg.tolist(),
        "net_counts": (y - bg).tolist(),
    }
