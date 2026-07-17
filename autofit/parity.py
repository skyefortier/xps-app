"""
Parity / characterization utilities for the autofit engine.

Two independent parity notions, both against the expert reference fits in
``docs/autofit/test_data``:

1. **Eval parity** — evaluating the saved peak parameters through
   ``fitting.py``'s lineshape functions (+ the exact background
   reconstruction ``run_fit`` performs) reproduces the saved
   ``fitResult.fittedY``.  This proves the spec mirror
   (``peak_to_backend_spec``) and the lineshape math agree with what
   produced the expert fits.

2. **Refit stability** — re-running ``fitting.run_fit`` seeded at the saved
   parameters stays at the same minimum (no parameter drift, same χ²ᵣ).
   Frozen into a fixture, this is the regression net that pins today's
   manual-fit behavior.

Neither imports anything from ``app.py`` and nothing here is reachable from
the production request path.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from fitting import (
    _SHAPE_FUNCS,
    linear_background,
    shirley_background,
    shirley_linear_background,
    smart_background,
    smart_experimental_background,
    tougaard_background,
    run_fit,
)
from .reference import ReferenceFit


def evaluate_peak(be: np.ndarray, spec: dict[str, Any]) -> np.ndarray:
    """Evaluate one backend peak spec at its own parameter values."""
    f = _SHAPE_FUNCS[spec["shape"]]
    a, c, s = spec["amplitude"], spec["center"], spec["shape"]
    if s in ("gaussian", "lorentzian"):
        return f(be, a, c, spec["fwhm"])
    if s == "pseudo_voigt_gl":
        return f(be, a, c, spec["fwhm"], spec["gl_ratio"])
    if s == "asymmetric_gl":
        return f(be, a, c, spec["fwhm"], spec["asymmetry"], spec["gl_ratio"])
    if s == "doniach_sunjic":
        return f(be, a, c, spec["fwhm"], spec["alpha"], spec["gamma_asym"])
    if s == "ds_g":
        return f(be, a, c, spec["alpha"], spec["beta"], spec["m_gauss"])
    if s == "la_casaxps":
        return f(be, a, c, spec["fwhm"], spec["alpha"], spec["beta"], spec["m"])
    raise ValueError(f"Unknown backend shape {s!r}")


def evaluate_model(be: np.ndarray, specs: list[dict]) -> np.ndarray:
    """Sum of all peak evaluations (no background)."""
    total = np.zeros_like(np.asarray(be, dtype=float))
    for s in specs:
        total = total + evaluate_peak(be, s)
    return total


def background_like_run_fit(
    x: np.ndarray,
    y: np.ndarray,
    method: str,
    bg_start_idx: int,
    bg_end_idx: int,
    endpoint_avg: int = 1,
) -> np.ndarray:
    """
    Reproduce exactly the background array ``run_fit`` constructs — including
    the anchor-window normalization (swap reversed indices, bail to full ROI
    below 2 points), the ``[i0:i1]`` slice semantics, and the flat-hold
    extension outside the anchor window.  Kept in lockstep with
    ``fitting.run_fit``; the eval-parity battery fails if they diverge.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    i0, i1 = bg_start_idx, bg_end_idx
    i0 = max(0, i0)
    i1 = min(len(x), i1)
    if i0 > i1:
        i0, i1 = i1, i0
    if i1 - i0 < 2:
        i0, i1 = 0, len(x)

    xb, yb = x[i0:i1], y[i0:i1]
    m = (method or "shirley").lower()

    if m == "shirley":
        bg_inner = shirley_background(xb, yb, n_avg=endpoint_avg)
    elif m == "smart":
        bg_inner = smart_background(xb, yb, n_avg=endpoint_avg)
    elif m == "smart_exp":
        bg_inner = smart_experimental_background(xb, yb, n_avg=endpoint_avg)
    elif m == "shirley_linear":
        bg_inner = shirley_linear_background(xb, yb, n_avg=endpoint_avg)
    elif m == "tougaard":
        bg_inner = tougaard_background(xb, yb, n_avg=endpoint_avg)
    elif m == "linear":
        if x[i1 - 1] != x[i0]:
            slope = (y[i1 - 1] - y[i0]) / (x[i1 - 1] - x[i0])
        else:
            slope = 0.0
        return y[i0] + slope * (x - x[i0])
    elif m in ("none", "flat", "", "manual"):
        return np.zeros_like(y)
    else:
        raise ValueError(f"Unknown background method {method!r}")

    bg = np.zeros_like(y)
    if len(bg_inner) > 0:
        bg[i0:i1] = bg_inner
        if i0 > 0:
            bg[:i0] = bg_inner[0]
        if i1 < len(y):
            bg[i1:] = bg_inner[-1]
    return bg


# ─────────────────────────────────────────────────────────────────────────────
# Parity records
# ─────────────────────────────────────────────────────────────────────────────

def battery_eligible(rf: ReferenceFit, region: str = "C 1s") -> tuple[bool, str]:
    """
    Single source of truth for battery/roster eligibility, shared by the
    fixture generator and the pytest battery so they can never disagree.

    Returns (eligible, reason-if-not).
    """
    if rf.region_guess() != region:
        return False, f"not {region}"
    fr = rf.fit_result
    if not fr.get("fittedY") or not fr.get("be"):
        return False, "legacy fitResult (no be/fittedY)"
    if len(fr["fittedY"]) != len(fr["be"]):
        return False, (
            f"internally inconsistent fitResult (fittedY {len(fr['fittedY'])} "
            f"pts vs be {len(fr['be'])} pts — stale fittedY from an earlier ROI)"
        )
    if not grid_matches(rf):
        return False, "fit-time grid drifted from current ui state"
    return True, ""


def grid_matches(rf: ReferenceFit, tol: float = 1e-3) -> bool:
    """
    True when the saved fit-time grid (``fitResult.be``) equals the ROI grid
    reconstructed from the tab's current ui state.  False means the tab's
    charge correction / ROI moved after the fit (the app shifts ui fields and
    peaks together but keeps ``fitResult`` in the fit-time frame) — those
    tabs are excluded from strict parity and logged instead.
    """
    saved_be = rf.fit_result.get("be")
    if not saved_be:
        return False
    roi = rf.roi_be
    if len(saved_be) != len(roi):
        return False
    return float(np.max(np.abs(np.asarray(saved_be, dtype=float) - roi))) <= tol


def eval_parity_relmax(rf: ReferenceFit) -> float:
    """
    Max |python_eval − saved fittedY| / max|fittedY| on the reconstructed
    ROI grid.  Requires ``grid_matches(rf)``.
    """
    fittedY = np.asarray(rf.fit_result["fittedY"], dtype=float)
    specs = rf.backend_peak_specs()
    model = evaluate_model(rf.roi_be, specs)
    i0, i1 = rf.bg_indices()
    bg = background_like_run_fit(
        rf.roi_be, rf.roi_intensity, rf.bg_method, i0, i1, rf.endpoint_avg
    )
    scale = max(float(np.max(np.abs(fittedY))), 1.0)
    return float(np.max(np.abs(model + bg - fittedY)) / scale)


def refit_record(rf: ReferenceFit) -> dict[str, Any]:
    """
    Deterministic seeded refit (leastsq, no perturbation) from the saved
    parameters.  Returns a serializable record for fixture freezing.
    """
    i0, i1 = rf.bg_indices()
    res = run_fit(
        rf.roi_be,
        rf.roi_intensity,
        rf.backend_peak_specs(),
        background_method=rf.bg_method,
        bg_start_idx=i0,
        bg_end_idx=i1,
        endpoint_avg=rf.endpoint_avg,
        n_perturb=0,
    )
    peaks = []
    for ip in res["individual_peaks"]:
        par = ip["params"]
        peaks.append({
            "id": ip["id"],
            "center": par["center"]["value"],
            "fwhm": par["fwhm"]["value"],
            "amplitude": par["amplitude"]["value"],
            "area": par["area"]["value"],
        })
    return {
        "project": rf.project,
        "name": rf.name,
        "reduced_chi_square": res["statistics"]["reduced_chi_square"],
        "r_factor": res["statistics"]["r_factor"],
        "success": bool(res["success"]),
        "peaks": peaks,
    }
