"""
Method 6 — resolution enhancement by iterative deconvolution
(the decision-matrix "max-entropy" menu slot; registry id kept for menu
stability).

HONEST LABELING (Codex Stage-9 blocker): the implemented update is a
DAMPED EXPONENTIATED ISRA/RL-STYLE multiplicative deconvolution step with
a reduced-χ² stopping rule.  It is NOT a constrained maximum-entropy
solve — no entropy gradient/Lagrange multiplier appears in the update, so
nothing here "maximizes entropy"; the χ² stop is the only regularizer.
The classic MaxEnt treatments are cited as the field's reference methods;
implementing a true entropy-regularized objective (explicit α, line
search) is logged as future work in the payload.

Literature basis (decision matrix, verified DOIs):
- Vasquez, Klein, Barton & Grunthaner, JESRP 23 (1981) 63,
  DOI 10.1016/0368-2048(81)85037-2 — the original MaxEnt deconvolution of
  XPS spectra (the reference method this slot is named for);
- Aspnes, Entropy 24 (2022) 1238, DOI 10.3390/e24091238 (deconvolution
  practice review);
- χ²ᵣ-target stopping in the Skilling-Bryan spirit (UNVERIFIED as applied
  to processed XPS data).

THIS METHOD'S JOB IS DIFFERENT from the fitters: given a single spectrum
and a known instrument broadening kernel, it estimates a non-negative
sharpened estimate whose reconvolution matches the data at the χ² target.
It does NOT quantify components — `peaks` is empty by design; the
sharpened spectrum lives in the analysis payload.  It AMPLIFIES NOISE and
can generate artifact structure (the decision matrix's documented
weakness) — the payload carries that warning verbatim.

THE KERNEL IS USER PHYSICS, NOT INVENTED: ``kernel_fwhm_ev`` is a REQUIRED
option (the instrument Gaussian response FWHM).  This implementation ships
no default — supplying it is the user's calibration claim, and it is
echoed into the payload as provenance.  Convolution is edge-normalized
(flux-preserving at the boundaries).  Fully deterministic.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

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
    # registry id kept for decision-matrix menu stability; the label is
    # honest about what the implemented algorithm actually is
    label = "Resolution enhancement (iterative deconvolution; MaxEnt slot)"
    requires_grammar = False

    def run(
        self,
        x: np.ndarray,
        y: np.ndarray,
        weights: Optional[np.ndarray] = None,
        grammar: Optional[CandidateGrammar] = None,
        peak_specs: Optional[list[dict]] = None,
        options: Optional[dict[str, Any]] = None,
        progress_cb: Optional[Callable[[dict], None]] = None,
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

        if not np.isfinite(kernel_fwhm):
            raise ValueError("kernel_fwhm_ev must be finite")
        K = _gaussian_kernel(x, kernel_fwhm)
        if len(K) >= n:
            raise ValueError(
                f"kernel ({len(K)} points at fwhm {kernel_fwhm:g} eV) is as "
                f"wide as the spectrum ({n} points) — nothing recoverable")
        # flux-preserving boundary correction: divide by K⊛1 so a constant
        # spectrum stays constant at the edges (mode='same' zero-padding
        # otherwise depresses the boundary — Codex Stage-9 finding)
        edge = np.convolve(np.ones(n), K, mode="same")

        def conv(f):
            return np.convolve(f, K, mode="same") / edge

        m_prior = max(float(np.mean(y_pos)), 1e-12)
        f = np.full(n, m_prior)
        for it in range(cfg["max_iter"]):
            model = conv(f)
            chi_r = float(np.sum(((y_pos - model) / sigma) ** 2) / n)
            if chi_r <= cfg["chi_sq_target"]:
                break
            # damped exponentiated ISRA/RL-style multiplicative step (the
            # kernel is symmetric so Kᵀ-correlation == convolution).  This
            # is NOT an entropy-regularized ascent — see the class docstring
            # (Codex Stage-9 blocker: honest labeling).
            ratio = conv(y_pos - model) / np.maximum(sigma ** 2, 1e-30)
            f = f * np.exp(cfg["step_damping"] * ratio * sigma ** 2
                           / np.maximum(conv(np.maximum(model, 1e-30)), 1e-30))
            f = np.clip(f, 1e-30, None)

        # χ² must describe the EMITTED f: when max_iter is exhausted the
        # loop's last chi_r predates the final multiplicative update
        # (Codex Stage-9 re-check major)
        chi_r = float(np.sum(((y_pos - conv(f)) / sigma) ** 2) / n)
        converged = chi_r <= cfg["chi_sq_target"]
        p = f / f.sum()
        neg_kl_to_flat = float(-np.sum(p * np.log(np.maximum(p, 1e-300) * n)))

        analysis = {
            "method": self.id,
            "algorithm": "damped exponentiated ISRA/RL-style multiplicative "
                         "deconvolution with reduced-χ² stopping — NOT a "
                         "constrained maximum-entropy solve (no entropy "
                         "gradient in the update); a true entropy-"
                         "regularized objective is FUTURE WORK",
            "basis": "reference MaxEnt treatments this menu slot is named "
                     "for: Vasquez 1981 DOI 10.1016/0368-2048(81)85037-2; "
                     "Aspnes 2022 DOI 10.3390/e24091238",
            "kernel": {"shape": "gaussian", "fwhm_ev": kernel_fwhm,
                       "provenance": "USER-SUPPLIED instrument calibration "
                                     "(this method ships no default kernel)",
                       "boundary": "edge-normalized (flux-preserving for "
                                   "constants); deconvolution remains "
                                   "ill-posed near the ends"},
            # values within one kernel FWHM of either end are boundary-
            # affected — do not interpret structure there
            "edge_margin_ev": kernel_fwhm,
            "noise_sigma": sigma,
            "noise_sigma_source": sigma_source,
            "iterations": it + 1,
            # constant offsets cancel: χ² on (y_pos − K·f) equals χ² on
            # (y − (K·f + baseline_offset)) — the emitted model is the
            # sharpened_spectrum reconvolved
            "reduced_chi_sq_reconvolution": chi_r,
            "chi_sq_target_reached": bool(converged),
            "baseline_offset": floor,
            "negative_kl_to_flat": neg_kl_to_flat,
            "sharpened_spectrum": [float(v) for v in (f + floor)],
            "be_grid": [float(v) for v in x],
            "unverified_tunables": {k: cfg[k] for k in DEFAULTS},
            "warning": ("resolution enhancement AMPLIFIES NOISE and can "
                        "produce artifact structure, especially past the χ² "
                        "target or with an over-wide kernel; features that "
                        "appear only after sharpening are NOT evidence — "
                        "confirm on the raw data (decision-matrix entry 6). "
                        "σ-ESTIMATED STOPPING IS UNCALIBRATED: the sharpening "
                        "severity is set by noise_sigma — for production use "
                        "supply a repeat-sweep-derived noise_sigma; the MAD "
                        "estimate is biased by peak curvature and correlated "
                        "noise."),
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
