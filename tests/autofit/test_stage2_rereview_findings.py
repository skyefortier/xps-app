"""Pinning tests for the Stage-2 Codex RE-REVIEW findings (verdict GO,
docs/autofit/codex/stage2_rereview_verdict.md):

1. criteria panel must use the SAME bic_ambiguity_threshold as the ranking
   (was: silently fell back to the 2.0 default);
2. phase-qualified role slugs must not collide after sanitization
   (was: 'B-4C' and 'B4C' collapsed into one lmfit param namespace);
3. orphan_peaks is a plausibility violation — never a clean survivor
   (was: recorded but ignored by rank_and_filter and dropped from payload);
4. best-minimum promotion carries a basin-support honesty diagnostic
   (was: a one-off deeper minimum was indistinguishable from a reproducible
   one in the payload).
"""

import numpy as np
import pytest

from autofit.engine import (
    BASIN_SUPPORT_RTOL,
    ModelReport,
    PlausibilityFlags,
    fit_candidate,
    rank_and_filter,
    run_stability_analysis,
)
from autofit.grammar import MaterialClass, Phase, resolve
from autofit.methods import get_method

from test_engine_doublet import _doublet_model, _doublet_spectrum


def _doublet_report(orphan=False):
    x, y = _doublet_spectrum()
    w = 1 / np.sqrt(np.maximum(y, 1))
    model = _doublet_model()
    fit = fit_candidate(x, y, w, model)
    assert fit.converged
    stability = run_stability_analysis(x, y, w, model, fit,
                                       noise_floor=1.0, n_refits=3, rng_seed=0)
    from autofit.engine import compute_bic, compute_residual_diagnostics
    y_fit = fit.lmfit_result.best_fit + fit.background
    residuals = compute_residual_diagnostics(x, y, y_fit, 1.0, {})
    return ModelReport(
        model=model, primary_fit=fit, bic=compute_bic(fit),
        stability=stability, residuals=residuals,
        plausibility=PlausibilityFlags(orphan_peaks=orphan),
    )


# ── finding 3: orphan_peaks gates clean survivorship ─────────────────────────

def test_orphan_peaks_never_clean_survivor():
    clean = _doublet_report(orphan=False)
    orphaned = _doublet_report(orphan=True)

    res = rank_and_filter([clean, orphaned])
    names = [r.model.name for r in res.survivors]
    # the orphaned report must not be a clean survivor; the clean one is
    assert clean in res.survivors
    assert orphaned not in res.survivors or res.conditional
    reasons = {id(r): why for r, why in res.filtered_out}
    assert "orphan_peaks=True" in reasons[id(orphaned)]


def test_orphan_only_pool_is_conditional_tier():
    orphaned = _doublet_report(orphan=True)
    res = rank_and_filter([orphaned])
    # stable-but-orphaned: promoted only as the CONDITIONAL tier, never clean
    assert res.conditional is True
    assert res.conditional_reason == "no_clean_survivor"
    assert res.survivors and res.survivors[0] is orphaned


# ── finding 4: basin-support honesty diagnostic ──────────────────────────────

def test_basin_support_counts_reproducible_minimum():
    x, y = _doublet_spectrum()
    w = 1 / np.sqrt(np.maximum(y, 1))
    model = _doublet_model()
    fit = fit_candidate(x, y, w, model)
    st = run_stability_analysis(x, y, w, model, fit,
                                noise_floor=1.0, n_refits=4, rng_seed=0)
    # a well-behaved synthetic doublet: every start lands in the same basin
    assert 1 <= st.best_basin_support <= 5
    assert st.best_basin_support >= 2, (
        "trivially reproducible minimum should be supported by >1 start; "
        f"got {st.best_basin_support} (rtol {BASIN_SUPPORT_RTOL})"
    )


# ── finding 2: sanitized slug collision guard ────────────────────────────────

def test_sanitized_slug_collision_raises():
    pa = Phase(id="B-4C", material_class=MaterialClass.SEMICONDUCTOR,
               regions=("B 1s",))
    pb = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
               regions=("B 1s",))
    with pytest.raises(ValueError, match="collide after sanitization"):
        resolve([pa, pb], [("B 1s", "B-4C"), ("B 1s", "B4C")])


def test_distinct_slugs_still_resolve():
    pa = Phase(id="BN", material_class=MaterialClass.INSULATOR,
               regions=("B 1s",))
    pb = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
               regions=("B 1s",))
    g = resolve([pa, pb], [("B 1s", "BN"), ("B 1s", "B4C")])
    assert g.candidates


# ── finding 1: criteria panel threshold wiring ───────────────────────────────

def _synthetic_c1s(seed=1):
    rng = np.random.default_rng(seed)
    x = np.arange(280.0, 294.0, 0.1)

    def g(c, a, w):
        return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)

    y = 400 + g(284.4, 12000, 0.8) + g(286.2, 1500, 1.2) + g(290.8, 600, 2.0)
    return x, y + rng.normal(0, 20, len(x))


GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
                 regions=("C 1s",), material="graphite")


def test_criteria_panel_uses_method_threshold():
    x, y = _synthetic_c1s()
    grammar = resolve([GRAPHITE], "C 1s")
    m = get_method("ic_model_comparison")
    res = m.run(x, y, grammar=grammar, options={
        "n_refits": 4, "noise_floor": 25.0,
        "candidate_filter": ["A1_linked", "AG1_linked", "B2_linked"],
        "bic_ambiguity_threshold": 1e9,
    })
    assert res.success
    panel = res.analysis["criteria_panel"]
    survivors = [c for c in res.analysis["candidates"] if c.get("rank")]
    if len(survivors) >= 2:
        # with an enormous threshold the top-2 BIC* gap is ALWAYS within it;
        # pre-fix the panel silently used 2.0 and reported False
        gaps = sorted(c["bic_star"] for c in survivors if c.get("bic_star") is not None)
        assert panel["bic_ambiguous"] is True
        # the test only discriminates when the real gap exceeds the old
        # hardcoded default — keep it that way or pick different candidates
        assert (gaps[1] - gaps[0]) > 2.0, "gap fell within old default; test no longer discriminates"
    else:
        pytest.skip("synthetic produced <2 survivors — threshold wiring not exercisable")
