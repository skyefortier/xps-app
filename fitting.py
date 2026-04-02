"""
fitting.py – XPS peak fitting engine using lmfit.

Supported lineshapes
--------------------
  gaussian        – pure Gaussian (amplitude at peak max, FWHM parameterised)
  lorentzian      – pure Lorentzian
  pseudo_voigt_gl – linear GL mix: (1‑η)·G + η·L  (η = Lorentzian fraction)
  asymmetric_gl   – GL mix with independent left/right FWHM
  doniach_sunjic  – metallic asymmetric lineshape
  la_casaxps      – CasaXPS LA(α,β,m): DS core convolved with Gaussian

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
    fwhm_l: float,
    fwhm_r: float,
    gl_ratio: float,
) -> np.ndarray:
    """
    Asymmetric GL pseudo‑Voigt: left and right halves have independent FWHM.

    Both halves meet at x = center with value = amplitude.
    gl_ratio applies to both sides (common Lorentzian fraction).
    """
    result = np.empty_like(x, dtype=float)
    left = x <= center
    result[left] = _pseudo_voigt_gl(x[left], amplitude, center, fwhm_l, gl_ratio)
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


def _la_casaxps(
    x: np.ndarray,
    amplitude: float,
    center: float,
    alpha: float,    # CasaXPS: dimensionless asymmetry index, 0 ≤ α < 0.5
    beta: float,     # CasaXPS: Lorentzian half-width (eV)
    m_gauss: float,  # CasaXPS: Gaussian FWHM (eV) for convolution
) -> np.ndarray:
    """
    CasaXPS LA(α,β,m) lineshape — Doniach-Šunjić core convolved with Gaussian.

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
        total = trapezoid(signal, xs)
        if total <= 0.0:
            break
        # Vectorised right‑side integrals using cumulative trapezoid (reversed)
        cum_right = np.zeros(len(ys))
        for i in range(len(ys)):
            cum_right[i] = trapezoid(signal[i:], xs[i:])
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
    """
    Smart/Dynamic background: Shirley with the constraint that the
    background never exceeds the measured data at any point.
    Prevents overshoot in regions between peaks or at noisy endpoints.
    """
    if len(x) < 2:
        return np.zeros_like(y)

    if x[0] > x[-1]:
        xs, ys = x[::-1].copy(), y[::-1].copy()
        flipped = True
    else:
        xs, ys = x.copy(), y.copy()
        flipped = False

    b_low = ys[0]
    b_high = ys[-1]

    B = np.linspace(b_low, b_high, len(ys))

    for _ in range(n_iter):
        B_prev = B.copy()
        signal = np.maximum(ys - B, 0.0)
        total = trapezoid(signal, xs)
        if total <= 0.0:
            break
        cum_right = np.zeros(len(ys))
        for i in range(len(ys)):
            cum_right[i] = trapezoid(signal[i:], xs[i:])
        B = b_high + (b_low - b_high) * cum_right / total
        # Smart constraint: background must never exceed data
        B = np.minimum(B, ys)
        if np.max(np.abs(B - B_prev)) < tol:
            break

    return B[::-1] if flipped else B


def linear_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Straight‑line background connecting the first and last data points."""
    slope = (y[-1] - y[0]) / (x[-1] - x[0]) if x[-1] != x[0] else 0.0
    return y[0] + slope * (x - x[0])


# ─────────────────────────────────────────────────────────────────────────────
# lmfit Model factory
# ─────────────────────────────────────────────────────────────────────────────

_SHAPE_FUNCS = {
    "gaussian": _gaussian,
    "lorentzian": _lorentzian,
    "pseudo_voigt_gl": _pseudo_voigt_gl,
    "asymmetric_gl": _asymmetric_gl,
    "doniach_sunjic": _doniach_sunjic,
    "la_casaxps": _la_casaxps,
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
    fwhm_min       : float – lower bound   (default 0.01)
    fwhm_max       : float – upper bound   (optional)
    gl_ratio       : float – Lorentzian fraction for *_gl shapes  [0–1]
    fwhm_l         : float – left FWHM for asymmetric_gl
    fwhm_r         : float – right FWHM for asymmetric_gl
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
    fwhm_l = spec.get("fwhm_l", fwhm)
    fwhm_r = spec.get("fwhm_r", fwhm)

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
             min_=spec.get("fwhm_min", 0.01), max_=spec.get("fwhm_max"))
        if shape in ("pseudo_voigt_gl", "asymmetric_gl"):
            _set("gl_ratio", spec.get("gl_ratio", 0.3),
                 expr=f"{m_prefix}gl_ratio" if spec.get("fix_fwhm", True) else None,
                 min_=0.0, max_=1.0)
        if shape == "asymmetric_gl":
            _set("fwhm_l", fwhm_l, expr=f"{m_prefix}fwhm_l" if spec.get("fix_fwhm", True) else None,
                 min_=spec.get("fwhm_min", 0.01))
            _set("fwhm_r", fwhm_r, expr=f"{m_prefix}fwhm_r" if spec.get("fix_fwhm", True) else None,
                 min_=spec.get("fwhm_min", 0.01))
        if shape == "doniach_sunjic":
            _set("alpha", spec.get("alpha", 0.1),
                 expr=f"{m_prefix}alpha" if spec.get("fix_fwhm", True) else None,
                 min_=0.0, max_=0.5)
            _set("gamma_asym", spec.get("gamma_asym", 0.0),
                 expr=f"{m_prefix}gamma_asym" if spec.get("fix_fwhm", True) else None,
                 min_=0.0, max_=1.0)
        if shape == "la_casaxps":
            fix = spec.get("fix_fwhm", True)
            _set("alpha",   spec.get("alpha",   0.10), expr=f"{m_prefix}alpha"   if fix else None, min_=0.0,  max_=0.49)
            _set("beta",    spec.get("beta",    0.3),  expr=f"{m_prefix}beta"    if fix else None, min_=0.05, max_=2.0)
            _set("m_gauss", spec.get("m_gauss", 0.4),  expr=f"{m_prefix}m_gauss" if fix else None, min_=0.0,  max_=4.0)
        return p

    # Free (master or unconstrained) peak
    # Non-LA peaks (satellites, etc.) get a default ±2 eV constraint to prevent
    # the optimizer from drifting to physically unreasonable positions.
    c_min = spec.get("center_min")
    c_max = spec.get("center_max")
    if shape != "la_casaxps" and c_min is None:
        c_min = center - 2.0
    if shape != "la_casaxps" and c_max is None:
        c_max = center + 2.0
    _set("center", center, min_=c_min, max_=c_max, vary=not spec.get("fix_center", False))
    _set("amplitude", amp,
         min_=spec.get("amplitude_min", 0.0), max_=spec.get("amplitude_max"),
         vary=not spec.get("fix_amplitude", False))
    _set("fwhm", fwhm,
         min_=spec.get("fwhm_min", 0.01), max_=spec.get("fwhm_max"),
         vary=not spec.get("fix_fwhm", False))

    if shape in ("pseudo_voigt_gl", "asymmetric_gl"):
        _set("gl_ratio", spec.get("gl_ratio", 0.3), min_=0.0, max_=1.0,
             vary=not spec.get("fix_gl_ratio", False))
    if shape == "asymmetric_gl":
        _set("fwhm_l", fwhm_l, min_=spec.get("fwhm_min", 0.01), max_=spec.get("fwhm_max"))
        _set("fwhm_r", fwhm_r, min_=spec.get("fwhm_min", 0.01), max_=spec.get("fwhm_max"))
    if shape == "doniach_sunjic":
        # DS asymmetry parameters are set by the user (prior knowledge) and held
        # fixed during fitting.  Only center, amplitude, and fwhm are optimised.
        # This prevents the optimizer from trading off alpha/gamma_asym against
        # fwhm/amplitude in unphysical ways.
        _set("alpha", spec.get("alpha", 0.1), vary=False)
        _set("gamma_asym", spec.get("gamma_asym", 0.0), vary=False)
    if shape == "la_casaxps":
        # α and m_gauss are free to vary within physical bounds.
        _set("alpha",   spec.get("alpha",   0.10), min_=0.01, max_=0.35)
        _set("beta",    spec.get("beta",    0.3),  min_=0.05, max_=2.0)
        _set("m_gauss", spec.get("m_gauss", 0.4),  min_=0.05, max_=4.0)

    return p


# ─────────────────────────────────────────────────────────────────────────────
# Charge correction helpers
# ─────────────────────────────────────────────────────────────────────────────

# Canonical reference binding energies (eV)
CHARGE_REFERENCES = {
    "c1s": 284.8,   # adventitious carbon C 1s
    "au4f": 83.96,  # Au 4f₇/₂ (Fermi‑level calibrated)
}


def charge_shift(method: str, measured_be: float) -> float:
    """Return the shift (eV) to add to all energies to correct charging."""
    reference = CHARGE_REFERENCES.get(method.lower())
    if reference is None:
        raise ValueError(f"Unknown charge‑correction method '{method}'. "
                         f"Choices: {list(CHARGE_REFERENCES)}")
    return reference - measured_be


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

    # Select background region
    i0 = bg_start_idx if bg_start_idx is not None else 0
    i1 = bg_end_idx if bg_end_idx is not None else len(energy)
    i0 = max(0, i0)
    i1 = min(len(energy), i1)
    if i0 >= i1:
        i0, i1 = 0, len(energy)

    x = energy[i0:i1]
    y = counts[i0:i1]

    # ── Background ────────────────────────────────────────────────────────────
    bg_method = background_method.lower()
    if bg_method == "shirley":
        bg = shirley_background(x, y)
    elif bg_method == "smart":
        bg = smart_background(x, y)
    elif bg_method == "linear":
        bg = linear_background(x, y)
    elif bg_method in ("none", "flat", ""):
        bg = np.zeros_like(y)
    else:
        raise ValueError(f"Unknown background method '{background_method}'")

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
    import sys as _sys
    def _flog(msg): print(msg, file=_sys.stderr, flush=True)
    _flog(f"═══ FIT START ═══  method={kws.get('method')}  n_data={len(y_sub)}")
    for pname, par in sorted(all_params.items()):
        _flog(f"  BEFORE  {pname:<30s} value={par.value:12.6f}  vary={str(par.vary):<5s}  expr={par.expr}  "
              f"min={f'{par.min:.4f}' if np.isfinite(par.min) else '-inf'}  "
              f"max={f'{par.max:.4f}' if np.isfinite(par.max) else 'inf'}")

    try:
        result = composite_model.fit(y_sub, all_params, x=x, weights=weights, **kws)
    except Exception as exc:
        raise RuntimeError(f"lmfit fitting failed: {exc}") from exc

    # ── Diagnostic logging: AFTER optimisation ───────────────────────────────
    _flog(f"═══ FIT DONE ═══  success={result.success}  nfev={result.nfev}  message={result.message}")
    for pname, par in sorted(result.params.items()):
        init = all_params[pname].value if pname in all_params else None
        delta = f"  Δ={par.value - init:+.6f}" if init is not None and abs(par.value - init) > 1e-10 else ""
        _flog(f"  AFTER   {pname:<30s} value={par.value:12.6f}  "
              f"stderr={f'{par.stderr:.6f}' if par.stderr is not None else 'None'}{delta}")

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
                _flog(f"  PERTURB {attempt+1}/{n_perturb}  redchi={trial_redchi:.4f}  (best={best_redchi:.4f})")
                if trial.success and trial_redchi < best_redchi:
                    best_result = trial
                    best_redchi = trial_redchi
                    _flog(f"  *** New best found! redchi improved to {best_redchi:.4f}")
            except Exception:
                _flog(f"  PERTURB {attempt+1}/{n_perturb}  failed (exception)")
                continue

        if best_result is not result:
            _flog(f"═══ PERTURB IMPROVED FIT ═══  redchi: {result.redchi:.4f} → {best_redchi:.4f}")
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
) -> dict[str, Any]:
    """Return just the background array without fitting peaks."""
    i0 = start_idx if start_idx is not None else 0
    i1 = end_idx if end_idx is not None else len(energy)
    x, y = energy[i0:i1], counts[i0:i1]

    if method == "shirley":
        bg = shirley_background(x, y)
    elif method == "smart":
        bg = smart_background(x, y)
    elif method == "linear":
        bg = linear_background(x, y)
    elif method in ("none", "flat", ""):
        bg = np.zeros_like(y)
    else:
        raise ValueError(f"Unknown background method '{method}'")

    return {
        "energy": x.tolist(),
        "background": bg.tolist(),
        "net_counts": (y - bg).tolist(),
    }
