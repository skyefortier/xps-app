"""
Engine wiring of the candidate-generation layer (`autofit.candidates`)
into `compare_models` / the IC method — strictly additive:

- the reviewed F1 dominant channel (detect_out_of_grammar_dominants) is
  UNCHANGED; the pool's curvature channel adds seeds it cannot produce
  (shoulders, resolved close pairs discarded by duplicate suppression);
- every seed flows through the same PreseedSpec -> region-unassigned,
  absent-eligible slot path (selection judges);
- the pool (with provenance + gate outcomes + residual-gap merge) lands in
  analysis.candidate_pool for the honesty surface.

Synthetic only; deterministic seeds.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from stress_cases import (  # noqa: E402
    _cand,
    _grammar,
    _linear_bg,
    _noisy,
    _pv,
    _slot,
    multi_env_low_be_dominant_case,
)

from autofit.methods import get_method  # noqa: E402

ETA = 0.30
IC_OPTS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
           "enable_proposal_pass": True}


def _ic(x, y, grammar, **extra):
    return get_method("ic_model_comparison").run(
        x, y, grammar=grammar, options={**IC_OPTS, **extra})


def _shoulder_case(seed=42):
    """ds8-class stand-in: OOG dominant + no-local-max shoulder on its
    low-BE flank + one in-window species.  SYN scaffold positions — nothing
    encodes the real spectra's energies."""
    x = np.arange(186.0, 205.0, 0.05)
    dom_c, f = 191.0, 1.2
    sh_c = dom_c - 0.9 * f
    truth = [{"center": sh_c, "fwhm": f, "height": 12000.0},
             {"center": dom_c, "fwhm": f, "height": 40000.0},
             {"center": 196.5, "fwhm": 1.2, "height": 9000.0}]
    sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
    y = _noisy(sig + _linear_bg(x), seed)
    grammar = _grammar([_cand("P1", [_slot("main_a", (195.5, 197.5),
                                           fwhm=(0.6, 2.0))])])
    return x, y, grammar, truth


def test_engine_seeds_shoulder_end_to_end():
    """DETECTION+INTEGRATION on the shoulder class: the shoulder enters the
    pool (curvature provenance), is seeded, and the winning decomposition
    places a component at BOTH the dominant and the shoulder."""
    x, y, grammar, truth = _shoulder_case()
    res = _ic(x, y, grammar)
    assert res.success

    feats = res.analysis["preseeded_features"]
    assert len(feats) == 2
    by_role = {f["role"]: f for f in feats}
    assert set(by_role) == {"preseed_dominant_0", "preseed_curvature_0"}
    assert by_role["preseed_dominant_0"]["provenance"] == "local_max"
    assert by_role["preseed_curvature_0"]["provenance"] == "curvature_shoulder"
    assert by_role["preseed_curvature_0"]["center_be"] == \
        pytest.approx(truth[0]["center"], abs=0.35)
    assert by_role["preseed_curvature_0"]["prom_z"] >= 7.0

    pool = res.analysis["candidate_pool"]
    assert pool is not None
    assert pool["sources_run"] == ["local_max", "curvature_shoulder",
                                   "grammar", "residual_gap"]
    seeded = [f for f in pool["features"]
              if f["seeded_role"] == "preseed_curvature_0"]
    assert seeded and "curvature_shoulder" in seeded[0]["provenance"]

    # INTEGRATION: the existing selection layer keeps both components
    emitted = {p["role"]: p for p in res.peaks}
    dom = emitted.get("preseed_dominant_0")
    sh = emitted.get("preseed_curvature_0")
    assert dom is not None and sh is not None, \
        f"seeded components missing from winner: {sorted(emitted)}"
    assert dom["center"] == pytest.approx(truth[1]["center"], abs=0.3)
    assert sh["center"] == pytest.approx(truth[0]["center"], abs=0.35)
    assert sh["region"] == "unassigned"
    assert "human review" in res.message


def test_engine_covered_spectrum_pool_reports_no_seeds():
    """Grammar-covered spectrum: pool present (honesty surface) but seeds
    NOTHING — candidate set unmodified (the F1 no-op pin extended to the
    curvature channel)."""
    x = np.arange(190.0, 205.0, 0.05)
    sig = (_pv(x, 9000.0, 196.5, 1.2, ETA)
           + _pv(x, 4000.0, 199.5, 1.4, ETA))
    y = _noisy(sig + _linear_bg(x), 11)
    grammar = _grammar([_cand("P2", [_slot("main_a", (195.5, 197.5)),
                                     _slot("comp_b", (198.5, 200.5))])],
                       windows={"SYN:main_a": (195.5, 197.5),
                                "SYN:comp_b": (198.5, 200.5)})
    res = _ic(x, y, grammar)
    assert res.analysis["preseeded_features"] == []
    assert not any(c["name"].endswith("+preseed")
                   for c in res.analysis["candidates"])
    pool = res.analysis["candidate_pool"]
    assert pool["curvature_seeds"] == []
    assert all(f["seeded_role"] is None for f in pool["features"])
    # grammar reference entries present with provenance
    assert any(f["provenance"] == ["grammar"] for f in pool["features"])


def test_engine_residual_gap_merged_into_pool(monkeypatch):
    """The F2 residual-proposal source merges into the pool payload
    post-fit: the accepted proposal position carries residual_gap
    provenance and its accept/attempt bookkeeping.  The Stage-2 operating
    point pre-seeds the multi-env neighbor, so this pin restores the OLD
    fraction gate via monkeypatch to force the F2 path while the pool is
    live — the merge machinery is what's under test."""
    import autofit.engine as eng

    monkeypatch.setattr(eng, "CURVATURE_SEED_MIN_FRACTION", 0.25)
    case = multi_env_low_be_dominant_case(seed=23)
    res = _ic(case.x, case.y, case.grammar)
    accepted = [p for c in res.analysis["candidates"]
                for p in c.get("proposed_peaks", []) if p["accepted"]]
    assert accepted, "the multi-env neighbor must arrive via a proposal"
    pool = res.analysis["candidate_pool"]
    rg = [f for f in pool["features"]
          if "residual_gap" in f["provenance"]]
    assert rg, "accepted proposal missing from the pool payload"
    near = [f for f in rg if abs(f["center_be"] - 193.0) < 0.6]
    assert near and near[0]["residual_gap"]["n_accepted"] >= 1


def test_engine_preseed_disabled_omits_pool():
    """enable_preseed=False must disable the WHOLE candidate-generation
    layer (dominant + curvature channels): no pool, no seeds — the
    pre-existing escape hatch keeps its meaning."""
    x = np.arange(190.0, 205.0, 0.05)
    y = _noisy(_pv(x, 9000.0, 196.5, 1.2, ETA) + _linear_bg(x), 3)
    grammar = _grammar([_cand("P1", [_slot("main_a", (195.5, 197.5))])])
    res = _ic(x, y, grammar, enable_preseed=False)
    assert res.analysis["candidate_pool"] is None
    assert res.analysis["preseeded_features"] == []


def test_pool_failure_degrades_not_kills_analysis(monkeypatch):
    """Defense-in-depth: the candidate-generation layer is an ADD-ON — an
    unexpected exception inside it must degrade to dominant-channel-only
    seeding with the error surfaced, never kill the whole analysis."""
    import autofit.engine as eng

    def boom(*a, **k):
        raise RuntimeError("synthetic detector failure")

    monkeypatch.setattr(eng, "build_candidate_pool", boom)
    case = multi_env_low_be_dominant_case(seed=23)
    res = _ic(case.x, case.y, case.grammar)
    assert res.success                      # the analysis still completes
    feats = res.analysis["preseeded_features"]
    assert len(feats) == 1                  # dominant channel still seeded
    assert feats[0]["provenance"] == "local_max"
    pool = res.analysis["candidate_pool"]
    assert pool is not None and "error" in pool
    assert "synthetic detector failure" in pool["error"]


def test_engine_no_hallucination_on_peakless_step():
    """NO-HALLUCINATION e2e: a peakless smooth step (charging-artifact
    class) with a matched Shirley-family candidate must gain NO seeded or
    proposed peaks in the emitted decomposition."""
    from autofit.grammar import BackgroundType

    x = np.arange(190.0, 205.0, 0.05)
    step = 3000.0 / (1.0 + np.exp(-(x - 200.0) / 1.0))
    y = _noisy(step + 500.0, 91)
    grammar = _grammar([_cand("P1", [_slot("main_a", (195.5, 197.5))],
                              bg=BackgroundType.SHIRLEY)])
    res = _ic(x, y, grammar)
    assert res.analysis["preseeded_features"] == []
    for p in res.peaks:
        assert not p["role"].startswith("preseed_")
        assert not p["role"].startswith("proposed_")
