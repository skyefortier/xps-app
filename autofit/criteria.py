"""
Pluralistic model-selection criteria panel (spec v2.1 §6).

From each candidate's shared ``(RSS, k, n)`` compute — near-free — a panel:
weighted χ²ᵣ, BIC* (ranking default), AICc, and nested-model F-tests.

Hard rules encoded here (Codex re-review items):

- ONE likelihood convention throughout: fitalg's
  ``IC = n·ln(RSS/n) + penalty`` (never mix with the ``χ² + penalty`` form).
- The panel is a **diagnostic, not independent corroboration** — all
  members share the Gaussian residual assumption on processed (non-count)
  data.  Every payload carries ``"not independent tests"``.
- F-test only on genuinely nested pairs (same shapes on shared roles,
  strict slot-subset).
- Two distinct flags, never merged: ``bic_ambiguous`` (|ΔBIC*| < τ) and
  ``criteria_conflict`` (top-by-BIC* ≠ top-by-AICc, or an F-test rejects a
  peak BIC* keeps).
- No single scalar decides.  Trust order for this data:
  parity → stability/persistence → residual structure → BIC* tie-break.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy import stats

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

# α for the nested-model F-test — UNVERIFIED tunable (conventional 0.05).
F_TEST_ALPHA = 0.05


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
    """
    True when ``smaller``'s slot set is a strict subset of ``larger``'s with
    identical line shapes on the shared roles (and identical backgrounds).
    Absent-slot-adjusted models and shape swaps are NOT nested.
    """
    if smaller.model.background is not larger.model.background:
        return False
    small = {s.role: s.line_shape for s in smaller.model.slots}
    large = {s.role: s.line_shape for s in larger.model.slots}
    if not (set(small) < set(large)):
        return False
    return all(large[r] is small[r] for r in small)


@dataclass
class FTestResult:
    smaller: str
    larger: str
    f_stat: Optional[float]
    p_value: Optional[float]
    extra_params: int
    rejects_extra_peak: bool     # True → the extra component is NOT justified


def f_test(smaller: ModelReport, larger: ModelReport) -> Optional[FTestResult]:
    """Nested-model F-test; None when the pair is not genuinely nested."""
    if not is_nested(smaller, larger):
        return None
    rss_s = smaller.primary_fit.residual_sum_sq
    rss_l = larger.primary_fit.residual_sum_sq
    k_s = smaller.primary_fit.n_params
    k_l = larger.primary_fit.n_params
    n = larger.primary_fit.n_data
    dk = k_l - k_s
    dof = n - k_l
    if dk <= 0 or dof <= 0 or rss_l <= 0:
        return None
    f = ((rss_s - rss_l) / dk) / (rss_l / dof)
    p = float(stats.f.sf(max(f, 0.0), dk, dof))
    return FTestResult(
        smaller=smaller.model.name, larger=larger.model.name,
        f_stat=float(f), p_value=p, extra_params=dk,
        rejects_extra_peak=p >= F_TEST_ALPHA,
    )


def build_criteria_panel(
    reports: list[ModelReport],
    survivors: list[ModelReport],
    bic_ambiguity_threshold: float = 2.0,
) -> dict:
    """
    Serializable criteria panel over the survivor set.

    Rankings use the absent-slot-adjusted parameter count for BIC* (matching
    the engine's ranking) and the same adjusted k for AICc so the two
    criteria see identical inputs.
    """
    per_candidate: dict[str, dict] = {}
    for r in reports:
        fit = r.primary_fit
        vals = ic_values(fit.residual_sum_sq, r.adjusted_n_params, fit.n_data)
        per_candidate[r.model.name] = {
            "reduced_chi_sq": float(r.reduced_chi_sq),
            "bic_star": vals["bic_star"],
            "aicc": vals["aicc"],
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
            flags["bic_ambiguous"] = bool(gap < bic_ambiguity_threshold)
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
                    "alpha": F_TEST_ALPHA,
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
