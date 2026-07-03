"""Criteria-panel unit tests (Codex Stage-2 findings #5, #6, #9)."""

import numpy as np

from autofit.criteria import build_criteria_panel, f_test, ic_values
from autofit.engine import (
    AbsentSlotReport,
    FitOutcome,
    ModelReport,
    ModelStability,
    PlausibilityFlags,
    ResidualDiagnostics,
)
from autofit.grammar import (
    BackgroundType,
    CandidateModel,
    ComponentSlot,
    LineShape,
)


def _slot(role):
    return ComponentSlot(role=role, region="T", phase_id="t",
                         be_window=(0.0, 10.0),
                         line_shape=LineShape.PSEUDO_VOIGT,
                         fwhm_range=(0.5, 3.0))


def _report(roles, rss, k, n=200, absent=()):
    model = CandidateModel(name="+".join(roles),
                           background=BackgroundType.SHIRLEY,
                           slots=tuple(_slot(r) for r in roles))
    fit = FitOutcome(converged=True, components=[], residual_sum_sq=rss,
                     weighted_chi_sq=rss, n_params=k, n_data=n)
    return ModelReport(
        model=model, primary_fit=fit, bic=0.0,
        stability=ModelStability(per_slot={}, orphan_rate=0.0,
                                 convergence_rate=1.0),
        residuals=ResidualDiagnostics(0.0, False, {}, []),
        plausibility=PlausibilityFlags(),
        absent_slots=[AbsentSlotReport(role=a, persistence=0.1, fitted_area=0.0,
                                       main_area=1.0, area_fraction=0.0,
                                       threshold=0.02, removed_n_params=3)
                      for a in absent],
    )


def test_f_test_requires_true_nesting():
    a = _report(["main"], rss=100.0, k=4)
    b = _report(["main", "extra"], rss=80.0, k=8)
    res = f_test(a, b)
    assert res is not None and res.extra_params == 4
    # not nested: disjoint roles
    c = _report(["other"], rss=90.0, k=4)
    assert f_test(c, b) is None


def test_f_test_skips_absent_slot_adjusted_models():
    a = _report(["main"], rss=100.0, k=4)
    b = _report(["main", "extra"], rss=80.0, k=8, absent=("extra",))
    assert f_test(a, b) is None
    assert f_test(b, a) is None


def test_aicc_uses_actual_k_and_bic_star_uses_adjusted():
    a = _report(["main"], rss=100.0, k=4)
    b = _report(["main", "extra"], rss=95.0, k=8, absent=("extra",))
    panel = build_criteria_panel([a, b], [a, b])
    pb = panel["per_candidate"][b.model.name]
    n = 200
    assert pb["n_params"] == 8 and pb["n_params_adjusted"] == 5
    assert np.isclose(pb["aicc"], ic_values(95.0, 8, n)["aicc"])
    assert np.isclose(pb["bic_star"], ic_values(95.0, 5, n)["bic_star"])
    assert "not independent tests" in panel["statement"]
