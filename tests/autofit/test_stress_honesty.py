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
    isolated_missing_peak_case,
    overlap_case,
    overspecified_case,
    overspecified_decoy_case,
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


def test_resolved_doublet_sparse_count_only():
    """Sparse COUNT-ONLY pin — explicitly NOT a recovery claim: on this
    PV-truth case the selected atoms sit 0.45-0.75 eV off (Gaussian-atom /
    30%-Lorentzian mismatch, its documented weakness; classified
    count_ok_param_biased in the battery, never PASS).  The invariant
    worth pinning is only that the component COUNT does not hallucinate on
    a clean, well-separated doublet."""
    case = overlap_case(1.0, 9000.0, seed=11, expectation="recover")
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


def test_inroi_decoy_pruned_not_populated():
    """The harder over-specification test (Codex stress review): a decoy
    'shoulder' window BETWEEN the true peaks, where real tail intensity
    lives — the winner must carry the true 2-component structure with the
    decoy hypothesis rejected, not a populated 3-component invention.
    Measured 2026-07-04: P2 clean, χ²ᵣ 1.10, exact recovery ON THIS BASE
    DRAW.  The battery shows the prune is noise-draw-DEPENDENT (offset
    2000 promotes the bound-fixed decoy via decisive_override, k=3,
    conditional-flagged) — stress report finding 8; this pin covers the
    base draw only."""
    case = overspecified_decoy_case(seed=32)
    res = _ic(case)
    assert res.diagnostics["winner"] == "P2"
    assert len(res.peaks) == 2
    by_role = {p["role"]: p for p in res.peaks}
    for t, role in zip(case.truth, ("main_a", "main_b")):
        assert by_role[role]["center"] == pytest.approx(t["center"], abs=0.1)


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


def test_preseed_catches_isolated_missing_peak():
    """Unit F1 (2026-07-07): the isolated unmodeled peak (28% of the main —
    above the preseed dominance gate) is now caught by the PRE-FIT seeding
    channel: same honesty contract as the proposal pass (region-unassigned
    component, human adjudication), reached before the fit so the landscape
    is sane.  The peak must be seeded, fitted at the true position, and
    surfaced in analysis.preseeded_features."""
    case = isolated_missing_peak_case(seed=71)
    res = _ic(case)
    assert res.diagnostics["winner"].endswith("+preseed")
    feats = res.analysis["preseeded_features"]
    assert len(feats) == 1
    assert feats[0]["center_be"] == pytest.approx(201.5, abs=0.3)
    seeded = [p for p in res.peaks if p["role"].startswith("preseed_dominant")]
    assert len(seeded) == 1
    assert seeded[0]["center"] == pytest.approx(201.5, abs=0.3)
    assert seeded[0]["region"] == "unassigned"
    assert "human review" in res.message


def test_proposal_pass_fires_on_isolated_missing_peak():
    """The residual-guided proposal pass's designed regime (3d): with the
    preseed channel disabled, a discrete isolated real peak the menu
    doesn't model must still be proposed, accepted, and fitted at the true
    position (measured on every noise draw; 0 false positives across the
    battery's 66 covered rows)."""
    case = isolated_missing_peak_case(seed=71)
    res = get_method("ic_model_comparison").run(
        case.x, case.y, grammar=case.grammar,
        options={**IC_OPTS, "enable_preseed": False})
    assert res.diagnostics["winner"].endswith("+prop")
    accepted = [p for c in res.analysis["candidates"]
                for p in c.get("proposed_peaks", []) if p["accepted"]]
    assert len(accepted) == 1
    assert accepted[0]["fitted_center"] == pytest.approx(201.5, abs=0.3)


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


def test_subfwhm_dominant_alternative_never_silently_lost():
    """INVARIANT (not a pin of the current deficient winner — Codex stress
    review): on the high-count sub-FWHM doublet the EVIDENCE decisively
    favors P2 (ΔBIC* 74-97 on every noise draw; stress report finding 0).
    Whatever the pipeline emits, the dominant evidence must never be
    silently lost:
    - if the engine picks P2 (a future fix), its centers must be sane; or
    - if it picks anything else, the dominant P2 record must remain fully
      machine-readable (fit quality, BIC* dominance, explicit non-survival
      reason) OR the result must carry an ambiguity/conditional signal."""
    case = overlap_case(0.4, 9000.0, seed=13, expectation="recover")
    res = _ic(case)
    winner = res.diagnostics["winner"]
    cands = {c["name"]: c for c in res.analysis["candidates"]}
    if winner.startswith("P2"):
        by_role = {p["role"]: p for p in res.peaks}
        assert len(by_role) == 2
    else:
        p2, w = cands["P2"], cands[winner]
        dominated = p2["bic_star"] < w["bic_star"] - 10
        # the engine now carries the RESULT-LEVEL burial flag (change
        # driven by stress finding 0) — when the dominant alternative is
        # filtered, the flag must name it
        result_flagged = (res.diagnostics.get("conditional")
                          or res.analysis.get("ambiguous_pairs")
                          or res.diagnostics.get(
                              "filtered_dominant_alternative"))
        assert (not dominated) or result_flagged, (
            "dominant alternative buried without any RESULT-level signal")
        if dominated and res.diagnostics.get("filtered_dominant_alternative"):
            assert (res.diagnostics["filtered_dominant_alternative"]["name"]
                    == "P2")
