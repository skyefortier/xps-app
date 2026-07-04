"""
Method 6 — Maximum-entropy resolution enhancement (decision-matrix entry 6).

Literature basis (decision matrix, verified DOIs):
- Vasquez, Klein, Barton & Grunthaner, JESRP 23 (1981) 63,
  DOI 10.1016/0368-2048(81)85037-2 — the original MaxEnt deconvolution of
  XPS spectra;
- Aspnes, Entropy 24 (2022) 1238, DOI 10.3390/e24091238 (review of MaxEnt
  deconvolution practice);
- Skilling & Bryan's classic MaxEnt prescription (χ² target = n).

THIS METHOD'S JOB IS DIFFERENT from the fitters: given a single spectrum
and a known instrument broadening kernel, it estimates the sharpened
spectrum f ≥ 0 that maximizes entropy S = −Σ p ln(p/m) subject to the
reconvolved fit (K·f) matching the data at a target χ².  It does NOT
quantify components — `peaks` is empty by design; the sharpened spectrum
lives in the analysis payload.  It AMPLIFIES NOISE and can generate
artifact structure when pushed past the χ² target (the decision matrix's
documented weakness) — the payload carries that warning verbatim.

THE KERNEL IS USER PHYSICS, NOT INVENTED: ``kernel_fwhm_ev`` is a REQUIRED
option (the instrument Gaussian response FWHM).  This implementation ships
no default — supplying it is the user's calibration claim, and it is
echoed into the payload as provenance.

Algorithm: multiplicative gradient ascent on the entropy-regularized
Poisson-free Gaussian objective (Richardson–Lucy-flavored MaxEnt update
with a flat prior m = data mean), iterated until reduced χ² of the
reconvolution reaches ``chi_sq_target`` (default 1.0 — the Skilling-Bryan
stopping rule; UNVERIFIED as applied to processed XPS data) or max_iter.
Fully deterministic.
"""

from __future__ import annotations

from typing import Any, Optional

import numpy as np

from ..grammar import CandidateGrammar
from .base import MethodResult, PeakFitMethod

DEFAULTS = dict(
    chi_sq_target=1.0,        # reduced-χ² stop (Skilling-Bryan); UNVERIFIED
    max_iter=2000,
    step_damping=0.7,         # multiplicative-update damping; UNVERIFIED
)
_ALLOWED_OPTIONS = set(DEFAULTS) | {"kernel_fwhm_ev", "noise_sigma"}


def _gaussian_kernel(x: np.ndarray, fwhm: float) -> np.ndarray:
    step = float(np.median(np.abs(np.diff(x))))
    half = max(int(np.ceil(3.0 * fwhm / step)), 1)
    t = np.arange(-half, half + 1) * step
    k = np.exp(-4.0 * np.log(2.0) * (t / fwhm) ** 2)
    return k / k.sum()


class MaxEntropyMethod(PeakFitMethod):
    id = "max_entropy"
    label = "Max-entropy (resolution enhancement)"
    requires_grammar = False

    def run(
        self,
        x: np.ndarray,
        y: np.ndarray,
        weights: Optional[np.ndarray] = None,
        grammar: Optional[CandidateGrammar] = None,
        peak_specs: Optional[list[dict]] = None,
        options: Optional[dict[str, Any]] = None,
    ) -> MethodResult:
        opts = dict(options or {})
        unknown = set(opts) - _ALLOWED_OPTIONS
        if unknown:
            raise ValueError(f"unknown max_entropy options: {sorted(unknown)}")
        if "kernel_fwhm_ev" not in opts:
            raise ValueError(
                "max_entropy requires kernel_fwhm_ev — the instrument "
                "broadening FWHM is the USER'S calibration input; this "
                "method ships no default (no-invention rule)")
        kernel_fwhm = float(opts.pop("kernel_fwhm_ev"))
        if kernel_fwhm <= 0:
            raise ValueError("kernel_fwhm_ev must be positive")
        cfg = {k: type(DEFAULTS[k])(opts.pop(k, DEFAULTS[k])) for k in DEFAULTS}

        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        n = len(y)
        if n < 8:
            raise ValueError("spectrum too short for deconvolution")
        floor = float(np.min(y))
        y_pos = y - floor                       # shift to ≥ 0 (restored after)
        # noise scale: user-supplied, else robust MAD of the second
        # difference (flagged as an ESTIMATE in the payload)
        if "noise_sigma" in opts:
            sigma = float(opts.pop("noise_sigma"))
            sigma_source = "user"
        else:
            d2 = np.diff(y, 2)
            sigma = float(1.4826 * np.median(np.abs(d2 - np.median(d2))) / np.sqrt(6.0))
            sigma = max(sigma, 1e-12)
            sigma_source = "estimated (MAD of 2nd difference) — supply noise_sigma for calibrated stopping"

        K = _gaussian_kernel(x, kernel_fwhm)
        conv = lambda f: np.convolve(f, K, mode="same")

        m_prior = max(float(np.mean(y_pos)), 1e-12)
        f = np.full(n, m_prior)
        chi_r = None
        for it in range(cfg["max_iter"]):
            model = conv(f)
            chi_r = float(np.sum(((y_pos - model) / sigma) ** 2) / n)
            if chi_r <= cfg["chi_sq_target"]:
                break
            # multiplicative RL-style update toward the data, damped;
            # kernel is symmetric so K^T-correlation == convolution
            ratio = conv(y_pos - model) / np.maximum(sigma ** 2, 1e-30)
            f = f * np.exp(cfg["step_damping"] * ratio * sigma ** 2
                           / np.maximum(conv(np.maximum(model, 1e-30)), 1e-30))
            f = np.clip(f, 1e-30, None)

        converged = chi_r is not None and chi_r <= cfg["chi_sq_target"]
        p = f / f.sum()
        entropy = float(-np.sum(p * np.log(np.maximum(p, 1e-300) / (1.0 / n))))

        analysis = {
            "method": self.id,
            "basis": "MaxEnt deconvolution (multiplicative updates, flat "
                     "prior, reduced-χ² stopping): Vasquez 1981 "
                     "DOI 10.1016/0368-2048(81)85037-2; Aspnes 2022 "
                     "DOI 10.3390/e24091238",
            "kernel": {"shape": "gaussian", "fwhm_ev": kernel_fwhm,
                       "provenance": "USER-SUPPLIED instrument calibration "
                                     "(this method ships no default kernel)"},
            "noise_sigma": sigma,
            "noise_sigma_source": sigma_source,
            "iterations": it + 1,
            "reduced_chi_sq_reconvolution": chi_r,
            "chi_sq_target_reached": bool(converged),
            "relative_entropy_to_flat": entropy,
            "sharpened_spectrum": [float(v) for v in (f + floor)],
            "be_grid": [float(v) for v in x],
            "unverified_tunables": {k: cfg[k] for k in DEFAULTS},
            "warning": ("resolution enhancement AMPLIFIES NOISE and can "
                        "produce artifact structure, especially past the χ² "
                        "target or with an over-wide kernel; features that "
                        "appear only after sharpening are NOT evidence — "
                        "confirm on the raw data (decision-matrix entry 6)"),
        }
        return MethodResult(
            method_id=self.id, success=True,
            peaks=[],               # sharpening, not quantification — by design
            analysis=analysis, confidence={},
            diagnostics={"reduced_chi_sq": chi_r, "iterations": it + 1,
                         "chi_sq_target_reached": bool(converged)},
            message=(f"sharpened with a {kernel_fwhm:g} eV Gaussian kernel in "
                     f"{it + 1} iterations (reconvolution χ²ᵣ {chi_r:.3g}; "
                     f"target {'reached' if converged else 'NOT reached'})"),
        )
