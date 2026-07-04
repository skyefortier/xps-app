"""
Always-on stress-honesty net — the KEY-CRITERION invariants from the
synthetic hard-case suite (run-brief item 2), pinned on the fast subset
(IC n_refits=4 + LS + sparse; the full battery incl. Bayesian and noise
replicates is scripts/run_stress_battery.py → stress_battery_runs.jsonl,
summarized in docs/autofit/stress-test-report.md).

Where there IS a right answer the engine must recover it; where the truth
is outside the model space the mismatch must be machine-visible; an
over-specified menu must be pruned, not populated.  Values pinned from the
2026-07-04 measurement run.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from stress_cases import (  # noqa: E402
    asym_truth_case,
    bg_matched_control_case,
    bg_mismatch_case,
    overlap_case,
    overspecified_case,
)
from autofit.methods import get_method  # noqa: E402

IC_OPTS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
           "enable_proposal_pass": True}


def _ic(case):
    return get_method("ic_model_comparison").run(
        case.x, case.y, grammar=case.grammar, options=dict(IC_OPTS))


@pytest.fixture(scope="module")
def sep1():
    case = overlap_case(1.0, 9000.0, seed=11, expectation="recover")
    return case, _ic(case)


def test_resolved_doublet_recovered_clean(sep1):
    """Separation 1×FWHM at 9000 counts: distinguishable → must recover."""
    case, res = sep1
    assert res.success
    assert res.diagnostics["winner"] == "P2"
    assert res.diagnostics["conditional"] is False
    by_role = {p["role"]: p for p in res.peaks}
    for t, role in zip(case.truth, ("main_a", "main_b")):
        assert by_role[role]["center"] == pytest.approx(t["center"], abs=0.05)


def test_resolved_doublet_ls_baseline(sep1):
    case, _ = sep1
    res = get_method("least_squares").run(
        case.x, case.y, peak_specs=case.ls_specs,
        options={"background_method": "linear"})
    assert res.success
    for t, p in zip(case.truth, res.peaks):
        assert p["center"] == pytest.approx(t["center"], abs=0.05)
        assert p["fwhm"] == pytest.approx(t["fwhm"], abs=0.1)


def test_resolved_doublet_sparse_count(sep1):
    """Sparse must find the true component COUNT here (its position bias
    under Gaussian-atom/PV-truth mismatch is a documented weakness,
    recorded in the battery — the count is the invariant)."""
    case, _ = sep1
    res = get_method("sparse_map").run(case.x, case.y, grammar=case.grammar)
    assert res.success
    assert len(res.peaks) == 2


def test_overspecified_menu_prunes_not_invents():
    """Truth 2 peaks, menu offers up to 5: the winner must carry exactly
    the true structure — no invented components."""
    case = overspecified_case(seed=31)
    res = _ic(case)
    assert res.diagnostics["winner"] == "P2"
    assert len(res.peaks) == 2
    by_role = {p["role"]: p for p in res.peaks}
    matched = 0
    for t in case.truth:
        if any(abs(p["center"] - t["center"]) < 0.3 for p in by_role.values()):
            matched += 1
    assert matched == 2


def test_bg_matched_control_recovers():
    case = bg_matched_control_case(seed=62)
    res = _ic(case)
    assert res.diagnostics["winner"] == "P2"
    assert res.diagnostics["conditional"] is False
    wc = next(c for c in res.analysis["candidates"] if c["name"] == "P2")
    assert wc["reduced_chi_sq"] < 2.0


def test_bg_mismatch_surfaces_loudly():
    """Shirley-shaped truth fit with a straight line: the mismatch must be
    machine-visible (conditional tier + grossly elevated χ²ᵣ), never a
    clean confident result."""
    case = bg_mismatch_case(seed=61)
    res = _ic(case)
    assert res.diagnostics["conditional"] is True
    wc = next(c for c in res.analysis["candidates"]
              if c["name"] == res.diagnostics["winner"])
    assert wc["reduced_chi_sq"] > 10.0


def test_asym_truth_recovered_when_expressible():
    case = asym_truth_case(seed=52, with_asym_candidate=True)
    res = _ic(case)
    assert res.diagnostics["winner"] == "asym_main"


def test_asym_truth_symmetric_only_flags_mismatch():
    """DS truth, symmetric-only menu: the model-space gap must be machine-
    visible — residual autocorrelation flag + elevated χ²ᵣ on the winner."""
    case = asym_truth_case(seed=51, with_asym_candidate=False)
    res = _ic(case)
    wc = next(c for c in res.analysis["candidates"]
              if c["name"] == res.diagnostics["winner"])
    assert wc["autocorr_flag"] is True
    assert wc["reduced_chi_sq"] > 3.0


def test_subfwhm_alternative_never_silently_lost():
    """KNOWN-DEFICIENCY pin (stress report finding 0 — evidence burial):
    on the high-count sub-FWHM doublet the EVIDENCE decisively favors P2
    (ΔBIC* 74-97, every noise draw) but the filter pipeline orphan-filters
    it and emits clean P1.  This test pins the HONESTY FLOOR while the
    deficiency stands: the dominant alternative's fit, its BIC*, and its
    non-survival reason must remain machine-readable in the candidate
    table.  REVISE deliberately when the result-level
    filtered_dominant_alternative flag lands (criteria/stability unit)."""
    case = overlap_case(0.4, 9000.0, seed=13, expectation="recover")
    res = _ic(case)
    assert res.diagnostics["winner"] == "P1"        # current deficient pick
    p1 = next(c for c in res.analysis["candidates"] if c["name"] == "P1")
    p2 = next(c for c in res.analysis["candidates"] if c["name"] == "P2")
    # the buried alternative dominates on evidence — and the trace of that
    # burial is fully present: fit quality, BIC*, explicit filter reason
    assert p2["bic_star"] < p1["bic_star"] - 10
    assert p2["reduced_chi_sq"] is not None
    assert p2["survived"] is False
    assert p2["filter_reason"]
