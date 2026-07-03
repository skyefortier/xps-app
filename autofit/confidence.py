"""
Per-peak, per-parameter confidence vectors (spec v2.1 §5).

Rules encoded:

- **Typed statistical σ** — ``uncertainty_kind ∈ {covariance, stability_mad,
  unavailable}``; kinds are NEVER mixed in one numeric field.  ``covariance``
  = lmfit stderr; ``stability_mad`` = raw median-absolute-deviations from
  the perturbation refits (reported as MADs, not silently rescaled to σ);
  ``unavailable`` otherwise.
- **Stability/persistence** — refit survival fraction + parameter MADs.
- **Detectability** — amplitude vs the noise floor; the ``5×`` floor is a
  TUNABLE validation parameter (UNVERIFIED), not a constant.
- **Identifiability** — boundary hits + max parameter correlation.
- ``reference_sensitivity_range`` is a SEPARATE field (never combined with
  σ_stat, no quadrature).  A single-spectrum fit cannot populate it — it
  needs the corrected-BE spread across admissible references for the phase —
  so it is ``None`` here with an explanatory kind, filled by the (later)
  charge-reference machinery.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from .engine import ModelReport, _slot_prefix, _width_param

# UNVERIFIED tunable (spec §9): detection floor as a multiple of the noise
# estimate. Calibrate on the labeled set; do not treat as physics.
DETECTION_FLOOR_MULTIPLE = 5.0


def _sigma_stat_for_slot(report: ModelReport, role: str) -> dict:
    """σ_stat for center/width/amplitude with an explicit kind."""
    result = report.primary_fit.lmfit_result
    slot = report.model.slot_by_role(role)
    wname = _width_param(slot.line_shape) if slot is not None else "fwhm"
    prefix = _slot_prefix(role)

    if result is not None:
        stderr = {}
        for short, pname in (("center", f"{prefix}center"),
                             ("fwhm", f"{prefix}{wname}"),
                             ("amplitude", f"{prefix}amplitude")):
            par = result.params.get(pname)
            stderr[short] = (float(par.stderr)
                             if par is not None and par.stderr is not None else None)
        if any(v is not None for v in stderr.values()):
            return {"uncertainty_kind": "covariance", "values": stderr}

    sstab = report.stability.per_slot.get(role)
    if sstab is not None and sstab.position_mad is not None:
        return {
            "uncertainty_kind": "stability_mad",
            # raw MADs from the perturbation refits — NOT rescaled to a
            # Gaussian σ; consumers must not compare across kinds.
            "values": {"center": sstab.position_mad,
                       "fwhm": sstab.fwhm_mad,
                       "amplitude": sstab.amplitude_mad},
        }
    return {"uncertainty_kind": "unavailable", "values": None}


def _max_correlation(report: ModelReport, role: str) -> Optional[float]:
    """Max |correlation| between this slot's varying params and any other."""
    result = report.primary_fit.lmfit_result
    if result is None or result.covar is None:
        return None
    var_names = list(result.var_names)
    covar = np.asarray(result.covar, dtype=float)
    d = np.sqrt(np.diag(covar))
    with np.errstate(invalid="ignore", divide="ignore"):
        corr = covar / np.outer(d, d)
    prefix = _slot_prefix(role)
    idx = [i for i, n in enumerate(var_names) if n.startswith(prefix)]
    others = [i for i in range(len(var_names)) if i not in idx]
    if not idx or not others:
        return None
    sub = np.abs(corr[np.ix_(idx, others)])
    sub = sub[np.isfinite(sub)]
    return float(np.max(sub)) if sub.size else None


def build_confidence_vector(
    report: ModelReport,
    role: str,
    noise_floor: float,
    detection_floor_multiple: float = DETECTION_FLOOR_MULTIPLE,
) -> dict:
    """The per-peak `_confidence` payload for one grammar slot."""
    sstab = report.stability.per_slot.get(role)
    comp = next((c for c in report.primary_fit.components if c.slot_role == role), None)
    boundary = [h for h in report.primary_fit.boundary_hits
                if h.startswith(f"{role}:")]

    amplitude = float(comp.amplitude) if comp is not None else None
    floor = detection_floor_multiple * noise_floor
    if amplitude is None:
        detect_status = "not_fitted"
    elif amplitude >= floor:
        detect_status = "above_floor"
    elif amplitude > noise_floor:
        detect_status = "present_but_poorly_constrained"
    else:
        detect_status = "not_confidently_detected"

    return {
        "sigma_stat": _sigma_stat_for_slot(report, role),
        # Systematic reference envelope — SEPARATE from σ_stat by design
        # (spec §4 M2: no quadrature). Not derivable from a single fit.
        "reference_sensitivity_range": {
            "kind": "unavailable_single_fit",
            "range_ev": None,
        },
        "stability": None if sstab is None else {
            "persistence": sstab.persistence,
            "position_mad": sstab.position_mad,
            "fwhm_mad": sstab.fwhm_mad,
            "amplitude_mad": sstab.amplitude_mad,
        },
        "detectability": {
            "amplitude": amplitude,
            "noise_floor": noise_floor,
            "floor_multiple": detection_floor_multiple,
            "floor_multiple_is_tunable": True,
            "status": detect_status,
        },
        "identifiability": {
            "boundary_hits": boundary,
            "max_cross_correlation": _max_correlation(report, role),
        },
    }
