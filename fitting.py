"""
fitting.py – XPS peak fitting engine using lmfit.

Supported lineshapes
--------------------
  gaussian        – pure Gaussian (amplitude at peak max, FWHM parameterised)
  lorentzian      – pure Lorentzian
  pseudo_voigt_gl – linear GL mix: (1‑η)·G + η·L  (η = Lorentzian fraction)
  asymmetric_gl   – GL mix with independent left/right FWHM
  doniach_sunjic  – metallic asymmetric lineshape
  ds_g            – DS+G: DS core convolved with Gaussian
  la_casaxps      – app LA(α,β,m): Lorentzian powers + continuous-m Gaussian convolution

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
from functools import lru_cache
from typing import Any

import numpy as np
from lmfit import Model, Parameters
from scipy.integrate import trapezoid

log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Lineshape functions (amplitude = value at center; asymmetric max may differ)
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
    x: np.ndarray, amplitude: float, center: float, alpha: float,
    beta: float, m_gauss: float,
) -> np.ndarray:
    """DS core convolved with a Gaussian of FWHM m_gauss (eV).

    Amplitude is the value at the continuous center, not the asymmetric
    maximum. Integrate the analytic core at Gaussian-displaced energies,
    including outside the ROI. The symmetric kernel has an exact zero
    sample, independent of input length, direction, spacing and cropping.
    The quadrature resolves both beta and Gaussian sigma with >=4 samples
    per scale; Gaussian support is +/-8 sigma (negligible discarded mass).
    """
    x = np.asarray(x, dtype=float)
    alpha = float(np.clip(alpha, 0., .495))
    beta = max(float(beta), 1e-6)
    m_gauss = max(float(m_gauss), 0.)

    def core(eps):
        phase = np.pi * alpha / 2 - (1 - alpha) * np.arctan2(eps, beta)
        return np.cos(phase) / (eps ** 2 + beta ** 2) ** ((1 - alpha) / 2)

    if m_gauss < .001:
        return amplitude * core(x - center) / core(0.)
    sigma = m_gauss / np.sqrt(8 * _LN2)
    half = max(32, int(np.ceil(8 * sigma / (beta / 4))))
    if half > 16384:
        raise ValueError("DS+G Gaussian/core width ratio exceeds supported quadrature resolution")
    if len(x) > 16 and half > 128:
        # Broad-Gaussian/narrow-core fits otherwise cost O(N*sigma/beta)
        # at every optimizer evaluation. Use analytically padded FFT
        # convolution on a center-anchored lattice, then cubic interpolation.
        # Resolve the smooth convolved curve by >=64 points per sigma;
        # beta/4 still resolves the narrow core. Center is an exact node.
        from scipy.interpolate import CubicSpline
        from scipy.signal import fftconvolve
        step = min(beta / 4, sigma / 64)
        radius = int(np.ceil(8 * sigma / step))
        step = 8 * sigma / radius
        lo = int(np.floor(min(float(np.min(x - center)), 0.) / step)) - 2
        hi = int(np.ceil(max(float(np.max(x - center)), 0.) / step)) + 2
        if hi - lo + 2 * radius < 1000000:
            offsets = np.arange(-radius, radius + 1) * step
            kernel = np.exp(-.5 * (offsets / sigma) ** 2)
            padded = np.arange(lo - radius, hi + radius + 1) * step
            values = fftconvolve(core(padded), kernel, mode="valid")
            lattice = np.arange(lo, hi + 1) * step
            return amplitude * CubicSpline(lattice, values)(x - center) / values[-lo]
    shifts = np.arange(-half, half + 1) * (8 * sigma / half)
    kernel = np.exp(-.5 * (shifts / sigma) ** 2)
    norm = float(np.dot(kernel, core(-shifts)))
    result = np.empty_like(x)
    # Vectorized, bounded-memory quadrature; this has exactly the same
    # nodes/weights as the scalar JS evaluator, including off-grid centers.
    chunk = max(1, 131072 // len(shifts))
    for start in range(0, len(x), chunk):
        eps = x[start:start + chunk, None] - center - shifts[None, :]
        result[start:start + chunk] = core(eps) @ kernel
    return amplitude * result / norm


@lru_cache(maxsize=256)
def ds_g_fwhm(alpha: float, beta: float, m_gauss: float) -> float:
    """Actual convolved DS+G FWHM, including alpha's asymmetric broadening."""
    from scipy.optimize import brentq, minimize_scalar
    scale = max(2 * beta, m_gauss, .001)
    def value(t):
        return float(_ds_g_dscore_gauss(np.array([t]), 1., 0., alpha, beta, m_gauss)[0])
    mode = minimize_scalar(lambda t: -value(t), bounds=(-scale, 3 * scale),
                           method="bounded", options={"xatol": 1e-8}).x
    half_height = value(mode) / 2
    def residual(t):
        return value(t) - half_height
    bounds = []
    for direction in (-1, 1):
        distance = scale
        for _ in range(30):
            bound = mode + direction * distance
            if residual(bound) < 0:
                bounds.append(bound)
                break
            distance *= 2
        else:
            return float("inf")  # cannot certify a finite narrow component
    return float(brentq(residual, mode, bounds[1]) - brentq(residual, bounds[0], mode))


# ─────────────────────────────────────────────────────────────────────────────
# Background functions
# ─────────────────────────────────────────────────────────────────────────────

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


def shirley_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = 1e-6,
    n_avg: int = 1,
) -> np.ndarray:
    """
    Iterative Shirley background (Proctor & Sherwood, Surf. Sci. 1982).

    Works on ascending or descending binding energy arrays.

    ``n_avg`` averages the first/last ``n_avg`` points before the endpoint
    levels B_low/B_high are read (audit F3, 2026-07-17). Shirley scales the
    ENTIRE background off those two levels, so a single noisy endpoint
    sample propagates straight into the net area. n_avg=1 = raw endpoints =
    previous behaviour. Callers previously had to pre-average the input
    array themselves via _apply_endpoint_averaging; that convention was
    easy to forget (autofit/engine.py did), so the knob now lives here,
    matching smart_experimental_background / shirley_linear_background.

    At each energy Eᵢ the background equals:
        B(Eᵢ) = B_high + (B_low – B_high) · ∫_{Eᵢ}^{E_max} s(E) dE
                                               ─────────────────────────
                                               ∫_{E_min}^{E_max} s(E) dE
    where s(E) = max(y(E) – B(E), 0) is the net signal.
    B_low  = y(E_min),  B_high = y(E_max)  (the endpoint levels).
    """
    if len(x) < 2:
        return np.zeros_like(y)

    if n_avg > 1:
        y = _apply_endpoint_averaging(np.asarray(y, dtype=float), n_avg)

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
    n_avg: int = 1,
) -> np.ndarray:
    """Smart (constrained Shirley): standard Shirley clamped to never exceed data.

    ``n_avg`` is forwarded to shirley_background (audit F3). The clamp is
    applied against the RAW data, not the endpoint-averaged copy, so
    averaging only ever moves the background — never the reported net
    counts.
    """
    if len(x) < 2:
        return np.zeros_like(y)
    shir = shirley_background(x, y, n_iter, tol, n_avg=n_avg)
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


def tougaard_background(
    x: np.ndarray,
    y: np.ndarray,
    n_avg: int = 1,
) -> np.ndarray:
    """Single-pass Tougaard universal-cross-section background, with the
    constant (pre-loss) term the window-limited integral cannot generate.

    Uses the two-parameter universal loss function
    K(T) = B·T / (C + T²)² with B = 2866 eV², C = 1643 eV²
    (S. Tougaard, Surf. Interface Anal. 11, 453 (1988): universal
    cross-section fitted to noble/transition-metal optical data; the
    kernel maximum sits at T = sqrt(C/3) ~= 23.4 eV energy loss).

    FORMULATION (2026-07-17 background audit, finding F1).  The idealized
    Tougaard integral B(E) = Σ_{E' < E} K(E-E')·J(E') assumes the analysis
    window BEGINS in a loss-free region, so that J at the low-BE edge is
    the zero-loss level.  Real windows never satisfy this: at (say) Fe 2p
    there is a large inelastic baseline produced by every lower-BE
    (higher-KE) transition OUTSIDE the window, which a window-limited
    integral structurally cannot reproduce.  Because K(0) = 0, the bare
    integral is identically zero at the low-BE edge REGARDLESS OF THE DATA
    — the background visibly dove to ~0 there, and a flat featureless
    window produced a full-amplitude phantom "signal".

    So the low-BE edge level is taken as a constant offset C0 (the
    out-of-window baseline the kernel cannot see), the kernel runs over the
    net (J - C0), and the amplitude is then anchored so the background
    meets the measured intensity at the HIGH-BE edge — the standard
    practical Tougaard criterion (B is effectively fitted, which is why the
    nominal B_coef cancels; C alone sets the kernel shape).  Equivalent to
    fitting B together with an offset rather than B alone.

    ``n_avg`` averages the first/last ``n_avg`` points before the endpoint
    levels are read, so neither C0 nor the high-BE anchor rests on a single
    noisy sample (see ``_apply_endpoint_averaging``).  n_avg=1 = raw
    endpoints = previous behaviour.

    The background at each binding energy accumulates loss contributions
    from electrons emitted at LOWER BE (higher kinetic energy), so the
    one-sided sum requires a descending-BE grid; input in either BE order
    is normalized internally.  Mirrors the frontend JS twin
    ``tougaardBackground``.
    """
    n = len(x)
    if n < 2:
        return np.zeros_like(y, dtype=float)

    # Universal cross-section constants, Tougaard (1988): B = 2866 eV²,
    # C = 1643 eV². A long-standing transcription slip shipped C = 1643²
    # (~2.7e6 eV²), which pushed the kernel maximum from ~23 eV to ~949 eV
    # of energy loss and flattened the background to ~zero over any real
    # XPS window. Fixed 2026-07-04 together with the JS twin.
    B_coef, C_coef = 2866.0, 1643.0

    xa = np.asarray(x, dtype=float)
    ya = np.asarray(y, dtype=float)
    if n_avg > 1:
        ya = _apply_endpoint_averaging(ya, n_avg)

    # The one-sided loss sum below (j >= i) is physical only when BE
    # DESCENDS along the array: the loss contributions at x[i] must come
    # from lower-BE (higher-KE) emitters, which sit at higher indices only
    # on a descending grid. Normalize to descending internally and flip
    # the result back — the mirror of shirley_background's ascending
    # normalization — so both BE orderings give identical output.
    flipped = bool(xa[0] < xa[-1])
    if flipped:
        xa, ya = xa[::-1].copy(), ya[::-1].copy()

    # C0: the low-BE edge level = index -1 on the descending working array.
    # This is the out-of-window (pre-loss) baseline; the kernel integral is
    # run on the net above it.
    c0 = float(ya[-1])
    net = ya - c0

    dx = float(abs(xa[1] - xa[0]))

    # bg[i] = Σ_{j>=i} K(|x[j]-x[i]|)·net[j]·w[j],  K(T) = B·T / (C + T²)²,
    # w[j] = the local quadrature weight (energy spacing) at point j.
    #
    # On a uniformly spaced grid |x[j]-x[i]| = (j-i)·dx and w[j] == dx, so the
    # kernel depends only on the index gap and this one-sided correlation
    # collapses to a convolution against a single precomputed kernel vector —
    # evaluated in C via np.convolve instead of an n-iteration Python loop
    # (audit F7). On a NONUNIFORM grid neither identity holds, so we keep the
    # exact per-point separation loop AND per-point weights (audit F2,
    # 2026-07-17: the loop previously used exact separations but omitted the
    # spacing weights, silently applying a uniform-grid quadrature inside the
    # branch written precisely because the grid is not uniform — up to ~24%
    # error on a genuinely nonuniform grid). np.gradient returns dx exactly
    # on a uniform grid, so both branches agree to floating point and the
    # uniformity test is a pure optimization, not a semantic fork.
    diffs = np.diff(xa)
    uniform = bool(dx > 0.0 and np.max(np.abs(diffs - diffs[0])) <= 1e-6 * dx)

    if uniform:
        m = np.arange(n, dtype=float)
        T = m * dx
        k = (B_coef * T) / (C_coef + T * T) ** 2          # k[m] = K(m·dx)
        # bg[i] = Σ_{m=0}^{n-1-i} k[m]·net[i+m]  =  conv(net, reverse(k))[n-1+i]
        bg = np.convolve(net, k[::-1])[n - 1:] * dx
    else:
        w = np.abs(np.gradient(xa))
        bg = np.zeros(n)
        for i in range(n):
            T = np.abs(xa[i:] - xa[i])
            kernel = (B_coef * T) / (C_coef + T * T) ** 2
            bg[i] = float(np.sum(kernel * net[i:] * w[i:]))

    # Amplitude anchor: scale the loss integral so the background equals the
    # measured intensity at the HIGH-BE edge (index 0 on the descending
    # working array), then sit it on the C0 pedestal. Guard semantics: if NO
    # net loss signal accumulates at the high-BE edge (bg[0] == 0 — e.g. a
    # flat or empty window), the honest background is the flat pre-loss level
    # C0 itself, NOT zeros: a featureless window contains no loss signal to
    # model, and returning zeros would report the entire baseline as net
    # signal (the pre-F1 behaviour). Negative counts (physically invalid
    # input) pass through signed; no clamping policy is imposed here.
    if bg[0] == 0.0:
        out = np.full(n, c0)
    else:
        out = c0 + bg * ((float(ya[0]) - c0) / bg[0])
    return out[::-1] if flipped else out


def _la_casaxps_true(
    x: np.ndarray, amplitude: float, center: float, fwhm: float,
    alpha: float, beta: float, m: float,
) -> np.ndarray:
    """App's LA profile: piecewise Lorentzian powers, Gaussian convolution.

    Retains the app convention sigma_points=m/3, with continuous m in
    [0,499]. This is not a certification of proprietary CasaXPS equivalence.
    Gaussian offsets use median channel spacing (0.05 eV for a singleton).
    The base is evaluated beyond both ROI edges, rather than zero-padded.
    Normalization evaluates the same convolution at the continuous center.
    Amplitude thus means value at center, not necessarily peak maximum.
    """
    x = np.asarray(x, dtype=float)
    if len(x) == 0:
        return np.zeros_like(x)
    fwhm = max(float(fwhm), 1e-9)
    alpha, beta = max(float(alpha), 1e-3), max(float(beta), 1e-3)
    m = float(np.clip(m, 0., 499.))
    def base(eps):
        lorentz = 1 / (1 + 4 * (eps / fwhm) ** 2)
        return np.where(eps >= 0, lorentz ** alpha, lorentz ** beta)
    if m < .001:
        return amplitude * base(x - center)
    step = float(np.median(np.abs(np.diff(x)))) if len(x) > 1 else .05
    if not np.isfinite(step) or step <= 0:
        raise ValueError("LA convolution requires positive channel spacing")
    sigma_pts = m / 3
    half = max(1, int(np.ceil(8 * sigma_pts)))
    k = np.arange(-half, half + 1)
    weights = np.exp(-.5 * (k / sigma_pts) ** 2)
    shifts = k * step
    norm = float(np.dot(weights, base(-shifts)))
    if len(x) > 1 and np.allclose(np.diff(x), x[1] - x[0], rtol=1e-7, atol=1e-10):
        # Fast path for normal acquisition grids. Both tails are evaluated
        # analytically before convolution; valid cropping returns only the
        # requested samples. Normalize analytically as on the general path.
        padded_x = x[0] + np.arange(-half, len(x) + half) * (x[1] - x[0])
        convolved = np.convolve(base(padded_x - center), weights, mode="valid")
        return amplitude * convolved / norm
    result = np.zeros_like(x)
    for shift, weight in zip(shifts, weights):
        result += weight * base(x - center - shift)
    return amplitude * result / norm


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


def _validate_constraint_graph(peak_specs: list[dict]) -> None:
    """Reject self-referential or circular spin-orbit constraints (audit F11).

    A peak whose ``constrain_to`` names its own id — or a cycle such as
    A→B→A — produces a self-referencing lmfit expression that recurses to
    "maximum recursion depth exceeded". Catch it here with a clean ValueError
    (→ 400) before any lmfit parameter/expression is built. A ``constrain_to``
    that names a non-existent peak is left for ``_make_peak_params`` to report.
    """
    parent: dict = {}
    for s in peak_specs:
        sid = s.get("id")
        master = s.get("constrain_to")
        if master is None:
            continue
        if master == sid:
            raise ValueError(f"Peak '{sid}' cannot constrain to itself")
        parent[sid] = master

    # Walk each constrained peak's master chain; a repeat is a cycle.
    for start in parent:
        chain = [start]
        cur = parent[start]
        while cur is not None:
            chain.append(cur)
            if cur == start or cur in chain[:-1]:
                pretty = " → ".join(str(x) for x in chain)
                raise ValueError(f"Circular peak constraint detected: {pretty}")
            cur = parent.get(cur)


def _analytic_area_factor_expr(shape: str, prefix: str) -> str | None:
    """Full-domain area / height as an lmfit expression (not ROI area)."""
    if shape == "gaussian":
        return f"{prefix}fwhm * {float(_SQRT_PI_4LN2)!r}"
    if shape == "lorentzian":
        return f"{prefix}fwhm * {float(np.pi / 2)!r}"
    if shape in ("pseudo_voigt_gl", "asymmetric_gl"):
        factor = (f"{prefix}fwhm * ((1 - {prefix}gl_ratio) * "
                  f"{float(_SQRT_PI_4LN2)!r} + {prefix}gl_ratio * {float(np.pi / 2)!r})")
        if shape == "asymmetric_gl":
            factor += f" * (1 + {prefix}asymmetry / 2)"
        return factor
    return None


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
    area_ratio     : float – ratio of full-domain component areas for supported
                     analytic profiles; finite ROI integrals may differ.
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

        if not np.isfinite(area_ratio) or area_ratio < 0:
            raise ValueError("area_ratio must be finite and nonnegative")
        master_shape = master_spec["shape"]
        if master_shape != shape:
            raise ValueError("Linked peaks must use the same lineshape family")
        factor = _analytic_area_factor_expr(shape, prefix)
        master_factor = _analytic_area_factor_expr(master_shape, m_prefix)
        if factor is not None:
            amplitude_expr = f"{m_prefix}amplitude * {area_ratio} * ({master_factor}) / ({factor})"
        elif not spec.get("fix_fwhm", True):
            raise ValueError(
                "Independent-width area-ratio links are supported only for Gaussian, "
                "Lorentzian and GL profiles; DS/DS+G/LA require shared shape parameters")
        else:
            # Identical profiles have a shared scale factor. This preserves
            # established shared-shape links, including DS's finite-window
            # convention; it does not assert DS has a finite infinite-tail area.
            amplitude_expr = f"{m_prefix}amplitude * {area_ratio}"
        _set("center", center, expr=f"{m_prefix}center + {splitting}")
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
        # Width/shape parameters must exist before the area expression is
        # evaluated; lmfit resolves dependencies again after parameter merging.
        _set("amplitude", amp, expr=amplitude_expr)
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
        _set("m_gauss", spec.get("m_gauss", 0.4),  min_=0.0, max_=4.0,
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

def _area_stderr(component: Model, result, x: np.ndarray) -> float | None:
    """Delta-method uncertainty of a finite-window area, using full covariance."""
    if result.covar is None or not result.var_names:
        return None
    covariance = np.asarray(result.covar, dtype=float)
    if not np.all(np.isfinite(covariance)):
        return None
    params = result.params.copy()
    gradient = []
    for name in result.var_names:
        par = params[name]
        original = par.value
        step = np.cbrt(np.finfo(float).eps) * max(abs(original), 1.)
        lower, upper = max(par.min, original - step), min(par.max, original + step)
        if upper <= lower:
            return None
        values = []
        for value in (lower, upper):
            par.value = value
            params.update_constraints()
            values.append(float(abs(trapezoid(component.eval(params, x=x), x))))
        par.value = original
        params.update_constraints()
        gradient.append((values[1] - values[0]) / (upper - lower))
    grad = np.asarray(gradient)
    variance = float(grad @ covariance @ grad)
    return float(np.sqrt(max(variance, 0.))) if np.isfinite(variance) else None


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
    weights: np.ndarray | None = None,
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
    weights           : optional finite positive inverse-sigma values on the
                        entire incoming grid; default is Poisson-like intensity weighting

    Returns
    -------
    dict with keys: energy, fitted_y, background_y, residuals,
                    individual_peaks, statistics, charge_shift_applied, success
    """
    energy, counts = np.asarray(energy, dtype=float), np.asarray(counts, dtype=float)
    if len(energy) != len(counts):
        raise ValueError("energy and counts must have the same length")
    if not peak_specs:
        raise ValueError("At least one peak specification is required")
    # Reject self/cyclic spin-orbit constraints before building lmfit exprs (F11)
    _validate_constraint_graph(peak_specs)

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
        bg_inner = shirley_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "smart":
        bg_inner = smart_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "smart_exp":
        bg_inner = smart_experimental_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "shirley_linear":
        bg_inner = shirley_linear_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "tougaard":
        bg_inner = tougaard_background(x_bg, y_bg, n_avg=endpoint_avg)
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
    # since counting noise comes from the total detected signal.
    # Floor at 1.0 to avoid division by zero for zero-count channels.
    supplied_weights = weights is not None
    if weights is None:
        weights = 1.0 / np.sqrt(np.maximum(y, 1.0))
    else:
        weights = np.asarray(weights, dtype=float)
        if weights.ndim != 1 or weights.shape != y.shape:
            raise ValueError("weights must be a one-dimensional array matching counts")
        if not np.all(np.isfinite(weights)) or np.any(weights <= 0):
            raise ValueError("weights must be finite and strictly positive")

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

        # Area by numerical integration. abs(): real XPS grids are
        # BE-descending, which makes the raw trapezoid integral negative —
        # the area is a magnitude by convention (matches autofit/engine.py).
        area = float(abs(trapezoid(peak_y, x)))

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

        # Propagate the actual finite-window integral through ALL free
        # parameters and their covariance. Re-evaluate constraints on each
        # perturbation so linked component uncertainty includes its parent.
        component = next(c for c in composite_model.components if c.prefix == prefix)
        param_info["area"]["stderr"] = _area_stderr(component, result, x)

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
            "weighting": "supplied_inverse_sigma" if supplied_weights else "observed_intensity_poisson_like",
            "area_definition": "trapezoidal_integral_over_fit_window",
            "uncertainty_scope": "conditional_on_background_and_model",
            "covariance_scaled_by_reduced_chi_square": bool(kws.get("scale_covar", True)),
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
        bg = shirley_background(x, y, n_avg=endpoint_avg)
    elif method == "smart":
        bg = smart_background(x, y, n_avg=endpoint_avg)
    elif method == "smart_exp":
        bg = smart_experimental_background(x, y, n_avg=endpoint_avg)
    elif method == "shirley_linear":
        bg = shirley_linear_background(x, y, n_avg=endpoint_avg)
    elif method == "tougaard":
        bg = tougaard_background(x, y, n_avg=endpoint_avg)
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
