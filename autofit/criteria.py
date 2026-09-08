"""
Pluralistic model-selection criteria panel (spec v2.1 §6).

From each candidate's shared ``(RSS, k, n)`` compute — near-free — a panel:
weighted χ²ᵣ, BIC* (ranking default), AICc, and descriptive nested-model
F statistics. Nominal F probabilities are unavailable for added peaks.

Hard rules encoded here (Codex re-review items):

- ONE likelihood convention throughout: fitalg's
  ``IC = n·ln(RSS/n) + penalty`` (never mix with the ``χ² + penalty`` form).
- The panel is a **diagnostic, not independent corroboration** — all
  members share the Gaussian residual assumption on processed (non-count)
  data.  Every payload carries ``"not independent tests"``.
- Structural nesting requires matching shared bounds and linkage.
- Added nonnegative peaks have a nonregular boundary null; ordinary
  F-distribution significance is suppressed until independently calibrated.
- Two distinct flags, never merged: ``bic_ambiguous`` (|ΔBIC*| < τ) and
  ``criteria_conflict`` (top-by-BIC* ≠ top-by-AICc).
- No single scalar decides.  Trust order for this data:
  parity → stability/persistence → residual structure → BIC* tie-break.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from .engine import ModelReport

NOT_INDEPENDENT = (
    "not independent tests — BIC*, AICc, χ²ᵣ and F share the Gaussian "
    "residual/noise assumption on processed data; treat as correlated views "
    "of one likelihood"
)

TRUST_ORDER = (
    "parity to expert fits → stability/persistence → residual structure → "
    "BIC* as a relative tie-breaker only"
)


def ic_values(rss: float, k: int, n: int) -> dict[str, Optional[float]]:
    """BIC* and AICc in the fitalg likelihood convention."""
    if n <= 0 or rss <= 0:
        return {"bic_star": None, "aicc": None}
    base = n * np.log(rss / n)
    bic = base + k * np.log(n)
    aic = base + 2 * k
    denom = n - k - 1
    aicc = aic + (2.0 * k * (k + 1) / denom) if denom > 0 else None
    return {"bic_star": float(bic), "aicc": (float(aicc) if aicc is not None else None)}


def is_nested(smaller: ModelReport, larger: ModelReport) -> bool:
    """Conservative structural nesting, not calibration of an F distribution.

    Shared slots must have identical bounds, fixed parameters and linkage.
    Added slots must be able to disappear together at zero amplitude.
    More general bound containment is deliberately not inferred here.
    """
    if smaller.model.background is not larger.model.background:
        return False
    if smaller.model.shared_fwhm_params != larger.model.shared_fwhm_params:
        return False
    small = {s.role: s for s in smaller.model.slots}
    large = {s.role: s for s in larger.model.slots}
    if len(small) != len(smaller.model.slots) or len(large) != len(larger.model.slots):
        return False
    if not set(small) < set(large) or any(small[r] != large[r] for r in small):
        return False
    for role in set(large) - set(small):
        slot = large[role]
        if "amplitude" in dict(slot.fixed_params):
            return False
        if dict(slot.param_ranges).get("amplitude", (0, 1))[0] > 0:
            return False
        if slot.linked_to in small and (slot.area_ratio is not None
                                       or slot.area_ratio_range is not None):
            return False
    return True


@dataclass
class FTestResult:
    smaller: str
    larger: str
    f_stat: Optional[float]
    p_value: Optional[float]
    extra_params: int
    rejects_extra_peak: bool
    calibrated: bool = False
    reason: str = ""


def f_test(smaller: ModelReport, larger: ModelReport) -> Optional[FTestResult]:
    """
    Descriptive F improvement; no nominal significance for added peaks.
    None when the pair is not structurally nested OR when
    either model carries absent-slot adjustments (spec §6 v2.1: absent-slot-
    adjusted models are outside F-test validity — their effective parameter
    count was reduced arithmetically, not by a reduced-model refit).
    """
    if smaller.absent_slots or larger.absent_slots:
        return None
    if not is_nested(smaller, larger):
        return None
    rss_s = smaller.primary_fit.residual_sum_sq
    rss_l = larger.primary_fit.residual_sum_sq
    k_s = smaller.primary_fit.n_params
    k_l = larger.primary_fit.n_params
    n = larger.primary_fit.n_data
    dk = k_l - k_s
    dof = n - k_l
    if (smaller.primary_fit.n_data != n or dk <= 0 or dof <= 0
            or not np.isfinite([rss_s, rss_l]).all() or rss_s < 0 or rss_l <= 0):
        return None
    f = ((rss_s - rss_l) / dk) / (rss_l / dof)
    # A nonnegative added amplitude has a boundary null. Its center/width
    # are unidentified when amplitude=0; ordinary F critical values do not
    # apply (Protassov et al. 2002, doi:10.1086/339856). Report improvement
    # descriptively until a model-specific null simulation is calibrated.
    return FTestResult(
        smaller=smaller.model.name, larger=larger.model.name,
        f_stat=float(f), p_value=None, extra_params=dk,
        rejects_extra_peak=False, calibrated=False,
        reason="Nominal F significance unavailable: added nonnegative peaks "
               "have a boundary null with unidentified shape parameters; "
               "a calibrated null simulation is required.",
    )


def build_criteria_panel(
    reports: list[ModelReport],
    survivors: list[ModelReport],
    bic_ambiguity_threshold: float = 2.0,
) -> dict:
    """
    Serializable criteria panel over the survivor set.

    Rankings use the absent-slot-adjusted parameter count for BIC* (matching
    the engine ranking), and the actual fitted parameter count for AICc.
    """
    per_candidate: dict[str, dict] = {}
    for r in reports:
        fit = r.primary_fit
        # BIC* uses the absent-slot-adjusted k (matching the engine ranking);
        # AICc uses the ACTUAL fitted k so the two criteria are genuinely
        # different views — computing both from adjusted k suppressed the
        # intended BIC*/AICc disagreement signal (Codex finding #6).
        bic_vals = ic_values(fit.residual_sum_sq, r.adjusted_n_params, fit.n_data)
        aicc_vals = ic_values(fit.residual_sum_sq, fit.n_params, fit.n_data)
        per_candidate[r.model.name] = {
            "reduced_chi_sq": float(r.reduced_chi_sq),
            "bic_star": bic_vals["bic_star"],
            "aicc": aicc_vals["aicc"],
            "n_params": int(fit.n_params),
            "n_params_adjusted": int(r.adjusted_n_params),
            "n_components": int(r.model.n_components),
        }

    flags = {"bic_ambiguous": False, "criteria_conflict": False}
    top_by_bic = top_by_aicc = None
    if survivors:
        ranked_bic = sorted(survivors, key=lambda r: r.bic_adjusted)
        top_by_bic = ranked_bic[0].model.name
        with_aicc = [r for r in survivors
                     if per_candidate[r.model.name]["aicc"] is not None]
        if with_aicc:
            top_by_aicc = min(
                with_aicc, key=lambda r: per_candidate[r.model.name]["aicc"]
            ).model.name
        if len(ranked_bic) >= 2:
            gap = abs(ranked_bic[0].bic_adjusted - ranked_bic[1].bic_adjusted)
            # <= to match the engine's ambiguous-pair convention exactly
            flags["bic_ambiguous"] = bool(gap <= bic_ambiguity_threshold)
        if top_by_aicc is not None and top_by_aicc != top_by_bic:
            flags["criteria_conflict"] = True

    # F-tests on genuinely nested survivor pairs
    f_tests: list[dict] = []
    for i, a in enumerate(survivors):
        for b in survivors[i + 1:]:
            for small, big in ((a, b), (b, a)):
                res = f_test(small, big)
                if res is None:
                    continue
                f_tests.append({
                    "smaller": res.smaller, "larger": res.larger,
                    "f_stat": res.f_stat, "p_value": res.p_value,
                    "extra_params": res.extra_params,
                    "rejects_extra_peak": bool(res.rejects_extra_peak),
                    "alpha": None,
                    "calibrated": res.calibrated,
                    "reason": res.reason,
                })
                # F rejecting a larger model that BIC* prefers → conflict
                if res.rejects_extra_peak and top_by_bic == res.larger:
                    flags["criteria_conflict"] = True

    return {
        "statement": NOT_INDEPENDENT,
        "trust_order": TRUST_ORDER,
        "per_candidate": per_candidate,
        "top_by_bic_star": top_by_bic,
        "top_by_aicc": top_by_aicc,
        "bic_ambiguous": flags["bic_ambiguous"],
        "criteria_conflict": flags["criteria_conflict"],
        "bic_ambiguity_threshold": bic_ambiguity_threshold,
        "f_tests": f_tests,
    }
