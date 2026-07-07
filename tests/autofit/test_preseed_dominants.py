"""
Units F1 (pre-fit out-of-grammar dominant seeding), F2 (iterative proposal
rounds), F3 (two-phase screen→stabilize sweep) — always-on pins.

Motivating evidence: PROGRESS.md "Real multi-environment C 1s — MEASURED
DIAGNOSIS (2026-07-07)".  The real spectra stay local-only (privacy rail);
`multi_env_low_be_dominant_case` in stress_cases.py is the committed
ground-truth stand-in for the class.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from stress_cases import (  # noqa: E402
    STEP,
    _cand,
    _grammar,
    _grid,
    _linear_bg,
    _noisy,
    _pv,
    _slot,
    multi_env_low_be_dominant_case,
)

import autofit.engine as eng  # noqa: E402
from autofit.methods import get_method  # noqa: E402

ETA = 0.30
IC_OPTS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
           "enable_proposal_pass": True}


def _ic(case, **extra):
    return get_method("ic_model_comparison").run(
        case.x, case.y, grammar=case.grammar, options={**IC_OPTS, **extra})


def _covered_spectrum(seed=11):
    """Both features inside grammar windows — detection must return []."""
    x = _grid()
    truth = [{"center": 196.5, "fwhm": 1.2, "height": 9000.0},
             {"center": 199.5, "fwhm": 1.4, "height": 4000.0}]
    sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
    y = _noisy(sig + _linear_bg(x), seed)
    cands = [_cand("P2", [_slot("main_a", (195.5, 197.5)),
                          _slot("comp_b", (198.5, 200.5))])]
    return x, y, _grammar(cands)


# ── F1: detection ──────────────────────────────────────────────────────────

def test_no_preseed_on_covered_spectrum():
    """Grammar-covered spectra must run byte-identically: zero detections,
    no '+preseed' candidates, empty preseeded_features."""
    x, y, grammar = _covered_spectrum()
    bg = eng._compute_background(x, y, grammar.candidates[0].background)
    specs = eng.detect_out_of_grammar_dominants(
        x, y, bg, grammar.candidates, dict(grammar.diagnostic_windows))
    assert specs == []

    case_like = type("C", (), {"x": x, "y": y, "grammar": grammar})
    res = _ic(case_like)
    assert res.analysis["preseeded_features"] == []
    assert not any(c["name"].endswith("+preseed")
                   for c in res.analysis["candidates"])


def test_detects_out_of_window_dominant_and_gates_weak_bump():
    """A dominant peak below every window is detected at its position; a
    weak out-of-window bump (below the fraction-of-max gate) is NOT —
    that regime stays the proposal pass's job."""
    x = _grid(186.0, 205.0)
    sig = (_pv(x, 30000.0, 191.0, 1.3, ETA)          # dominant, out-of-window
           + _pv(x, 30000.0 * 0.10, 188.5, 1.2, ETA)  # weak bump, below gate
           + _pv(x, 9000.0, 196.5, 1.2, ETA))         # in-window main
    y = _noisy(sig + _linear_bg(x), 7)
    cands = [_cand("P1", [_slot("main_a", (195.5, 197.5))])]
    grammar = _grammar(cands)
    bg = eng._compute_background(x, y, grammar.candidates[0].background)
    specs = eng.detect_out_of_grammar_dominants(
        x, y, bg, grammar.candidates, dict(grammar.diagnostic_windows))
    assert len(specs) == 1
    assert specs[0].center_init == pytest.approx(191.0, abs=0.3)
    assert specs[0].role == "preseed_dominant_0"
    # in-window features are never seeded, however large
    assert all(not (195.5 <= s.center_init <= 197.5) for s in specs)


def test_detection_descending_grid_equivalence():
    """Real raw_be grids DESCEND — detection must be order-invariant
    (np.interp-class bug family; the noise-model unit's lesson)."""
    x = _grid(186.0, 205.0)
    sig = (_pv(x, 30000.0, 191.0, 1.3, ETA)
           + _pv(x, 9000.0, 196.5, 1.2, ETA))
    y = _noisy(sig + _linear_bg(x), 7)
    cands = [_cand("P1", [_slot("main_a", (195.5, 197.5))])]
    grammar = _grammar(cands)
    bg = eng._compute_background(x, y, grammar.candidates[0].background)
    asc = eng.detect_out_of_grammar_dominants(
        x, y, bg, grammar.candidates, dict(grammar.diagnostic_windows))
    desc = eng.detect_out_of_grammar_dominants(
        x[::-1], y[::-1], bg[::-1], grammar.candidates,
        dict(grammar.diagnostic_windows))
    assert len(asc) == len(desc) == 1
    assert asc[0].center_init == pytest.approx(desc[0].center_init, abs=1e-9)


# ── F1+F2 end-to-end: the committed multi-environment regression case ─────

def test_multi_env_low_be_dominant_recovered():
    """THE committed stand-in for the real unpublished C 1s class: dominant
    below every window (F1 preseed) + weaker low-BE neighbor below the
    dominance gate (F2 iterative proposal) + in-window ladder.  The winning
    decomposition must place a component near EVERY truth peak, and the
    honesty surface must say what was seeded/proposed."""
    case = multi_env_low_be_dominant_case(seed=23)
    res = _ic(case)
    assert res.success

    # (a) the dominant was PRE-seeded, not left to the residual pass
    feats = res.analysis["preseeded_features"]
    assert len(feats) == 1
    assert feats[0]["center_be"] == pytest.approx(191.2, abs=0.4)
    # (b) the neighbor arrived through an accepted proposal round
    accepted = [p for c in res.analysis["candidates"]
                for p in c.get("proposed_peaks", []) if p["accepted"]]
    assert any(p["fitted_center"] == pytest.approx(193.0, abs=0.5)
               for p in accepted)
    # (c) every truth component is represented in the emitted peaks
    centers = sorted(p["center"] for p in res.peaks)
    for t in case.truth:
        assert min(abs(c - t["center"]) for c in centers) < 0.5, \
            f"no fitted component near truth {t['center']}"
    # (d) honesty surface: unassigned regions + human-review message
    unassigned = [p for p in res.peaks if p["region"] == "unassigned"]
    assert len(unassigned) >= 2          # the seed + the proposal
    assert "human review" in res.message


# ── F2: iterative rounds add MULTIPLE missing peaks ────────────────────────

def test_iterative_proposals_add_two_missing_peaks():
    """Two discrete unmodeled peaks, both below the preseed dominance gate:
    round 1 accepts one, detection re-runs on the augmented residual, round
    2 accepts the other (the old single-accept cap structurally could not
    do this — PROGRESS.md diagnosis, cause c)."""
    x = _grid(186.0, 206.0)
    sig = (_pv(x, 9000.0, 196.5, 1.2, ETA)            # in-window main
           + _pv(x, 9000.0 * 0.18, 190.5, 1.3, ETA)   # missing peak 1
           + _pv(x, 9000.0 * 0.15, 203.5, 1.3, ETA))  # missing peak 2
    y = _noisy(sig + _linear_bg(x), 31)
    cands = [_cand("P1", [_slot("main_a", (195.5, 197.5))])]
    grammar = _grammar(cands)
    res = get_method("ic_model_comparison").run(
        x, y, grammar=grammar, options=dict(IC_OPTS))
    accepted = [p for c in res.analysis["candidates"]
                for p in c.get("proposed_peaks", []) if p["accepted"]]
    fitted = sorted(p["fitted_center"] for p in accepted)
    assert len(fitted) == 2, f"expected both peaks accepted, got {fitted}"
    assert fitted[0] == pytest.approx(190.5, abs=0.4)
    assert fitted[1] == pytest.approx(203.5, abs=0.4)
    assert res.diagnostics["winner"].endswith("+prop+prop")
    # roles stay unique across rounds (param-prefix collision guard)
    roles = [p["role"] for p in res.peaks if p["role"].startswith("proposed")]
    assert len(roles) == len(set(roles)) == 2


# ── F3: two-phase sweep ────────────────────────────────────────────────────

def _many_candidate_grammar(x, y):
    """SCREEN_TOP_K+2 candidates: a ladder of window variants, several of
    which cannot express the data (wrong windows)."""
    good = [
        _cand("G1", [_slot("main_a", (195.5, 197.5))]),
        _cand("G2", [_slot("main_a", (195.5, 197.5)),
                     _slot("comp_b", (198.5, 200.5))]),
    ]
    bad = [
        _cand(f"B{i}", [_slot("main_a", (200.5 + i * 0.2, 202.5 + i * 0.2))])
        for i in range(eng.SCREEN_TOP_K)
    ]
    return _grammar(good + bad)


def test_screen_phase_records_and_selects():
    """More candidates than SCREEN_TOP_K → the screen runs, every candidate
    appears in the record (nothing silent), at most TOP_K are selected, and
    the winner is still the structurally right model."""
    x, y, _ = _covered_spectrum(seed=13)
    grammar = _many_candidate_grammar(x, y)
    case_like = type("C", (), {"x": x, "y": y, "grammar": grammar})
    res = _ic(case_like)
    screen = res.analysis["screen"]
    assert screen is not None
    assert len(screen) == len(grammar.candidates)
    assert sum(1 for r in screen if r["selected"]) <= eng.SCREEN_TOP_K
    # every non-selected candidate is visible with its screen outcome
    for r in screen:
        assert set(r) >= {"name", "converged", "bic", "selected"}
    assert res.diagnostics["winner"].startswith("G2")


def test_small_candidate_set_takes_classic_path():
    """≤ SCREEN_TOP_K candidates → no screen phase (screen is None) — every
    existing gate/battery path is unchanged."""
    x, y, grammar = _covered_spectrum(seed=13)
    case_like = type("C", (), {"x": x, "y": y, "grammar": grammar})
    res = _ic(case_like)
    assert res.analysis["screen"] is None
