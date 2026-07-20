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
    below every window + weaker low-BE neighbor + in-window ladder.  The
    winning decomposition must place a component near EVERY truth peak with
    the honesty surface intact.

    UPDATED for the Stage-2 operating point (2026-07-10): the 22.5%
    neighbor — historically below the 0.25 dominance gate and rescued by
    an F2 proposal round — now PRE-SEEDS through the curvature channel
    (trivia floor 0.02), which is the intended improvement: the fit starts
    from a sane landscape instead of relying on a post-fit rescue.  The F2
    iteration machinery keeps its own isolated pin below
    (test_iterative_proposals_add_two_missing_peaks, enable_preseed=False)."""
    case = multi_env_low_be_dominant_case(seed=23)
    res = _ic(case)
    assert res.success

    # (a) BOTH out-of-grammar species pre-seed: the dominant via the F1
    # local-max channel, the neighbor via the curvature channel
    feats = res.analysis["preseeded_features"]
    by_prov = {f["provenance"]: f["center_be"] for f in feats}
    assert len(feats) == 2, feats
    assert by_prov.get("local_max") == pytest.approx(191.2, abs=0.4)
    assert by_prov.get("curvature_shoulder") == pytest.approx(193.0, abs=0.5)
    # (b) every truth component is represented in the emitted peaks
    centers = sorted(p["center"] for p in res.peaks)
    for t in case.truth:
        assert min(abs(c - t["center"]) for c in centers) < 0.5, \
            f"no fitted component near truth {t['center']}"
    # (c) honesty surface: unassigned regions + human-review message
    unassigned = [p for p in res.peaks if p["region"] == "unassigned"]
    assert len(unassigned) >= 2          # both seeds
    assert "human review" in res.message
    # (d) widths are all physical (≤ ordinary cap) — the ordinary neighbour
    # and dominant recovered without a fat peak
    for p in res.peaks:
        if "satellite" in p["role"]:
            continue
        assert p["fwhm"] <= eng.FWHM_MAX_ORDINARY_EV + 1e-6, \
            f"{p['role']} fwhm {p['fwhm']} exceeds the ordinary cap"


# ── Physical FWHM caps (2026-07-08) ────────────────────────────────────────

def test_unphysical_width_flags_helper():
    """The width-flag helper: an ordinary slot pegging the 2.0 cap is
    flagged; a narrow main and a grammar-sanctioned-broad slot (explicit
    ``broad_justification``, e.g. a satellite) are NOT.

    2026-07-20 (Unit A, broad_justification refactor): the exemption used
    to be inferred from ``fwhm_range``'s own magnitude (declared max >
    2.0 eV) — this test originally built its synthetic "satellite_pi" slot
    with only a wide range and no explicit vouch, which is now correctly
    NOT exempt (that numeric-only inference is exactly the bug the MIXED
    material-class Codex review caught: widening a bound for an unrelated
    reason silently asserted "this is vouched physics" as a side effect).
    Updated to set broad_justification explicitly, matching how every real
    region module now grants this exemption."""
    from autofit.grammar import (CandidateModel, ComponentSlot, LineShape,
                                 BackgroundType)
    from autofit.engine import FittedComponent

    def slot(role, lo, hi, broad_justification=None):
        return ComponentSlot(role=role, region="r", phase_id="p",
                             be_window=(199., 201.), line_shape=LineShape.PSEUDO_VOIGT,
                             fwhm_range=(lo, hi),
                             broad_justification=broad_justification)

    def comp(role, fwhm):
        return FittedComponent(slot_role=role, position=200.0, fwhm=fwhm,
                               amplitude=1e3, shape_params={})

    m = CandidateModel(name="M", background=BackgroundType.LINEAR, slots=(
        slot("contamination_CO", 0.8, 2.0), slot("main_graphitic", 0.4, 1.2),
        slot("satellite_pi", 1.0, 5.5,
             broad_justification="synthetic: pi->pi* shake-up, physically broad"),
        slot("proposed_peak_0", 0.5, 2.0)))
    flags = eng._unphysical_width_flags(
        [comp("contamination_CO", 1.99), comp("main_graphitic", 1.2),
         comp("satellite_pi", 5.16), comp("proposed_peak_0", 2.0)], m)
    flagged_roles = {f.split(":")[0] for f in flags}
    assert flagged_roles == {"contamination_CO", "proposed_peak_0"}
    # a satellite at 5.16 (explicitly vouched-broad slot) is NEVER flagged —
    # this is exactly the "wide contamination" the fat-peak report was
    # really about
    assert not any("satellite" in f for f in flags)
    # a component comfortably under the cap → no flag at all
    assert eng._unphysical_width_flags([comp("contamination_CO", 1.5)], m) == []


def test_unphysical_width_flags_wide_range_alone_no_longer_exempts():
    """The bug this refactor fixes, pinned directly: a slot with a WIDE
    declared fwhm_range but NO broad_justification must be flagged when it
    fits wide — the bound's magnitude alone must never grant exemption.
    Mirrors the real MIXED material-class scenario (a relaxed contamination
    ceiling with no physics vouch) at the helper level, region-agnostic."""
    from autofit.grammar import (CandidateModel, ComponentSlot, LineShape,
                                 BackgroundType)
    from autofit.engine import FittedComponent

    slot = ComponentSlot(role="wide_unvouched", region="r", phase_id="p",
                         be_window=(199., 201.), line_shape=LineShape.PSEUDO_VOIGT,
                         fwhm_range=(0.8, 15.0))
    m = CandidateModel(name="M", background=BackgroundType.LINEAR, slots=(slot,))
    comp = FittedComponent(slot_role="wide_unvouched", position=200.0,
                           fwhm=8.0, amplitude=1e3, shape_params={})
    flags = eng._unphysical_width_flags([comp], m)
    assert flags, "a wide-but-unvouched slot must be flagged, not exempted"


def test_preseed_and_proposal_slots_capped_at_ordinary():
    """F1 pre-seed slots and F2/F3 proposal slots must be built with the
    ordinary physical FWHM ceiling as their upper bound — not the old
    looser 3.0 that let residual proposals grow to fat widths."""
    spec = eng.PreseedSpec(role="preseed_dominant_0", center_init=279.0,
                           fwhm_init=1.0, amplitude_net=1e4, fraction_of_max=1.0,
                           local_snr=100.0)
    from autofit.grammar import CandidateModel, BackgroundType
    base = CandidateModel(name="B", background=BackgroundType.SHIRLEY, slots=())
    seeded = eng._preseed_augmented(base, [spec])
    assert seeded.slots[-1].fwhm_range[1] == eng.FWHM_MAX_ORDINARY_EV

    pspec = eng.ProposalSpec(role="proposed_peak_0", detection_windows=[],
                             detection_energy=1.0, detection_ratio=9.0,
                             center_init=281.0, fwhm_init=1.0, amplitude_init=5e3,
                             line_shape=eng.PROPOSED_PEAK_SHAPE)
    aug = eng._augmented_candidate(base, pspec)
    assert aug.slots[-1].fwhm_range[1] == eng.FWHM_MAX_ORDINARY_EV


def test_wide_proposal_capped_and_flagged():
    """A genuinely BROAD (3 eV) out-of-window feature with no known-broad
    justification: the proposal must be held at the 2.0 physical cap
    (not fit at 3 eV), still MODEL the feature (accepted, center recovered),
    and the result must be flagged low-confidence (width_capped +
    unphysical_widths + conditional + a plain-language message) — the exact
    real-data situation (a ~281 eV feature wanting 3 eV) the user flagged."""
    x = _grid(185.0, 206.0)
    sig = (_pv(x, 9000.0, 196.5, 1.2, ETA)            # in-window main (ordinary)
           + _pv(x, 3200.0, 190.0, 3.0, ETA))         # broad out-of-window feature
    y = _noisy(sig + _linear_bg(x), 41)
    cands = [_cand("P1", [_slot("main_a", (195.5, 197.5))])]
    grammar = _grammar(cands)
    # preseed off so the broad feature goes through the residual-proposal
    # path (the channel with the accept gates); with preseed on it would be
    # a pre-seed slot, ALSO capped at 2.0 — covered by the slot-cap pin above
    res = get_method("ic_model_comparison").run(
        x, y, grammar=grammar, options={**IC_OPTS, "enable_preseed": False})
    prop = [p for c in res.analysis["candidates"]
            for p in c.get("proposed_peaks", []) if p["accepted"]]
    assert prop, "the broad feature should still be modelled (accepted), not dropped"
    p = prop[0]
    assert p["fitted_center"] == pytest.approx(190.0, abs=0.6)
    assert p["fitted_fwhm"] <= eng.FWHM_MAX_ORDINARY_EV + 1e-6   # NOT 3 eV
    assert p["width_capped"] is True
    # flagged: unphysical_widths on the winner + conditional + honest message
    assert res.diagnostics["winner_unphysical_widths"]
    assert res.diagnostics["conditional"] is True
    assert "physical" in res.message.lower() and "confidence" in res.message.lower()
    # every emitted non-satellite width is physical
    for pk in res.peaks:
        if "satellite" not in pk["role"]:
            assert pk["fwhm"] <= eng.FWHM_MAX_ORDINARY_EV + 1e-6


def test_shape_endpoint_pegs_do_not_reject_proposals():
    """Codex fwhm-cap review, run A: a proposed peak reaching a SHAPE
    endpoint (pure-Gaussian gl_ratio=0 / pure-Lorentzian gl_ratio=1) is
    valid physics — the shared detector excludes it, so it does NOT count as
    a spurious peg and must not reject the proposal (rejecting it regressed
    the two-narrow-peak F2 case to zero accepted proposals).  A SUBSTANTIVE
    peg (center at a window edge, fwhm@max, fwhm@min) IS surfaced."""
    from lmfit import Parameters
    from autofit.grammar import (CandidateModel, ComponentSlot, LineShape,
                                 BackgroundType)
    role = "proposed_peak_0"
    prefix = eng._slot_prefix(role)
    slot = ComponentSlot(role=role, region="unassigned", phase_id="unassigned",
                         be_window=(199., 201.), line_shape=LineShape.PSEUDO_VOIGT,
                         fwhm_range=(0.5, 2.0))
    model = CandidateModel(name="M", background=BackgroundType.LINEAR, slots=(slot,))
    p = Parameters()
    p.add(f"{prefix}center", value=200.0, min=199.0, max=201.0)      # interior
    p.add(f"{prefix}amplitude", value=5000.0, min=0.0, max=1e5)      # interior
    p.add(f"{prefix}fwhm", value=2.0, min=0.5, max=2.0)             # fwhm@max
    p.add(f"{prefix}gl_ratio", value=1.0, min=0.0, max=1.0)         # shape endpoint
    hits = eng._detect_boundary_hits(p, model)
    assert f"{role}:gl_ratio@max" not in hits      # valid pure-Lorentzian, excluded
    assert f"{role}:fwhm@max" in hits              # the tolerated width-cap peg
    p[f"{prefix}center"].set(value=199.0)          # drifted to the window edge
    assert f"{role}:center@min" in eng._detect_boundary_hits(p, model)  # substantive


def test_proposal_rejected_when_stability_promotes_spurious_center_peg(monkeypatch):
    """Codex fwhm-cap review, run B BLOCKER: the proposed-slot peg decision
    must be RE-EVALUATED after run_stability_analysis promotes a deeper
    best_outcome — a stability-promoted center@min (spurious) must still
    reject, even though the initial augmented fit was clean."""
    import dataclasses
    from autofit.methods.base import poisson_like_weights
    from stress_cases import isolated_missing_peak_case

    case = isolated_missing_peak_case(seed=71)
    x, y = case.x, case.y
    w = poisson_like_weights(y)
    res = eng.compare_models(x, y, w, case.grammar, n_refits=2, rng_seed=0,
                             enable_proposal_pass=False, enable_preseed=False)
    base = res.reports[0]
    y_fit = (base.primary_fit.lmfit_result.best_fit + base.primary_fit.background)
    spec = eng._detect_residual_proposals(
        x, y, y_fit, 1.0, base.model,
        fitted_components=base.primary_fit.components)[0]

    # a REAL augmented fit, promoted as a "deeper" best_outcome that carries a
    # spurious center@min peg (the detector reads outcome.boundary_hits)
    aug_model = eng._augmented_candidate(base.model, spec)
    bg = eng._compute_background(x, y, aug_model.background)
    init = eng._initial_params_for_augmented(aug_model, base.primary_fit, spec, x, y - bg)
    real = eng.fit_candidate(x, y, w, aug_model, initial_params=init)
    promoted = dataclasses.replace(
        real, weighted_chi_sq=0.0,                       # guarantees promotion
        boundary_hits=[f"{spec.role}:center@min"])       # stability-introduced peg

    fake_stab = eng.ModelStability(
        per_slot={}, orphan_rate=0.0, convergence_rate=1.0,
        best_outcome=promoted, best_basin_support=1, n_attempted=2)
    monkeypatch.setattr(eng, "run_stability_analysis", lambda *a, **k: fake_stab)

    _, pr, outcome = eng._attempt_proposal(
        x=x, y=y, weights=w, base_report=base, spec=spec,
        noise_floor=1.0, n_refits=2, rng_seed=0,
        absent_slot_area_fraction=0.02, absent_slot_persistence_threshold=0.7,
        diagnostic_windows=dict(case.grammar.diagnostic_windows),
        budget_remaining=1e6)
    assert outcome == "stability_rejected"
    assert "post-stability" in (pr.rejection_reason or "")
    assert any("center@min" in h for h in pr.boundary_hits)


# ── F2: iterative rounds add MULTIPLE missing peaks ────────────────────────

def test_iterative_proposals_add_two_missing_peaks():
    """Two discrete unmodeled peaks: round 1 accepts one, detection re-runs
    on the augmented residual, round 2 accepts the other (the old
    single-accept cap structurally could not do this — PROGRESS.md
    diagnosis, cause c).  Stage-2 note: with the recalibrated seeding both
    peaks would PRE-seed, so this pin isolates the F2 iteration machinery
    with enable_preseed=False (the designed escape hatch, same pattern as
    test_proposal_pass_fires_on_isolated_missing_peak)."""
    x = _grid(186.0, 206.0)
    sig = (_pv(x, 9000.0, 196.5, 1.2, ETA)            # in-window main
           + _pv(x, 9000.0 * 0.18, 190.5, 1.3, ETA)   # missing peak 1
           + _pv(x, 9000.0 * 0.15, 203.5, 1.3, ETA))  # missing peak 2
    y = _noisy(sig + _linear_bg(x), 31)
    cands = [_cand("P1", [_slot("main_a", (195.5, 197.5))])]
    grammar = _grammar(cands)
    res = get_method("ic_model_comparison").run(
        x, y, grammar=grammar,
        options={**IC_OPTS, "enable_preseed": False})
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


def test_next_proposal_index_is_max_suffix_plus_one():
    """Codex c1s-fix BLOCKER (both runs): the F2 round renumbering must be
    max-suffix+1, NOT a slot COUNT.  After a round rejects proposed_peak_0
    but accepts proposed_peak_1, the model carries proposed_peak_1 while
    proposed_peak_0 never materialized — a count (1) would re-issue
    proposed_peak_1 next round, colliding the slot role and its lmfit param
    prefix.  This pins the helper directly on that exact gap."""
    from autofit.grammar import CandidateModel, ComponentSlot, LineShape

    def slot(role):
        return ComponentSlot(role=role, region="unassigned", phase_id="unassigned",
                             be_window=(199.0, 201.0), line_shape=LineShape.PSEUDO_VOIGT,
                             fwhm_range=(0.5, 3.0))
    # a model with proposed_peak_1 present but NOT proposed_peak_0 (the
    # reject-first-accept-later state) — count would say 1, max+1 says 2
    m = CandidateModel(name="X", background=eng.BackgroundType.LINEAR,
                       slots=(slot("main_a"), slot("proposed_peak_1")))
    assert eng._next_proposal_index(m) == 2
    # and after augmenting, all slot roles stay unique (no collision)
    spec = eng.ProposalSpec(
        role=f"proposed_peak_{eng._next_proposal_index(m)}",
        detection_windows=[], detection_energy=1.0, detection_ratio=9.0,
        center_init=200.0, fwhm_init=1.0, amplitude_init=5000.0,
        line_shape=eng.PROPOSED_PEAK_SHAPE)
    aug = eng._augmented_candidate(m, spec)
    aug_roles = [s.role for s in aug.slots]
    assert len(aug_roles) == len(set(aug_roles)), f"role collision: {aug_roles}"
    assert "proposed_peak_2" in aug_roles
    # no-proposal model → index 0
    m0 = CandidateModel(name="Y", background=eng.BackgroundType.LINEAR,
                        slots=(slot("main_a"),))
    assert eng._next_proposal_index(m0) == 0


def test_proposal_pass_respects_sweep_budget(monkeypatch):
    """Codex c1s-fix MAJOR (run B): an augmented fit has no internal wall
    clock, so a proposal attempt must fast-reject when too little sweep
    budget remains rather than running an unbounded fit past the total
    timeout.  With the fit-budget floor raised above any real remaining
    budget, EVERY proposal attempt must be 'insufficient_budget' — no
    augmented fit runs, no proposal is accepted, and the sweep still
    returns cleanly."""
    monkeypatch.setattr(eng, "PROPOSAL_MIN_FIT_BUDGET_SEC", 10_000.0)
    x = _grid()
    truth = [{"center": 196.5, "fwhm": 1.2, "height": 9000.0},
             {"center": 201.5, "fwhm": 1.2, "height": 2500.0}]
    sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
    y = _noisy(sig + _linear_bg(x), 71)
    cands = [_cand("single_main", [_slot("main_a", (195.5, 197.5))])]
    grammar = _grammar(cands)
    res = get_method("ic_model_comparison").run(
        x, y, grammar=grammar,
        options={**IC_OPTS, "enable_preseed": False})
    assert not res.diagnostics["winner"].endswith("+prop")
    reasons = [p["rejection_reason"] for c in res.analysis["candidates"]
               for p in c.get("proposed_peaks", [])]
    assert reasons, "expected at least one attempted-then-rejected proposal"
    assert all("insufficient_budget" in (r or "") for r in reasons), reasons


def test_stability_not_started_without_budget_after_augmented_fit(monkeypatch):
    """Codex c1s-fix RE-CHECK (run B): the top budget guard alone did NOT
    close the overrun — an augmented fit that PASSES the top guard then
    consumes most of the budget must not let run_stability_analysis start
    an unbounded refit with only a few seconds left.  The pre-stability
    guard now fast-rejects when the DYNAMIC remaining budget is below the
    fit floor.  Deterministic via a fake clock: attempt_start = 1000 s,
    every later perf_counter reads 1013 s, so with budget_remaining=20 the
    post-fit remaining is 7 s < 15 s floor — stability must NOT run."""
    from autofit.methods.base import poisson_like_weights
    from stress_cases import isolated_missing_peak_case

    case = isolated_missing_peak_case(seed=71)
    x, y = case.x, case.y
    w = poisson_like_weights(y)
    model = case.grammar.candidates[0]
    # real base report (unpatched clock), proposal + preseed off
    res = eng.compare_models(x, y, w, case.grammar, n_refits=2, rng_seed=0,
                             enable_proposal_pass=False, enable_preseed=False)
    base_report = res.reports[0]
    y_fit = (base_report.primary_fit.lmfit_result.best_fit
             + base_report.primary_fit.background)
    specs = eng._detect_residual_proposals(
        x, y, y_fit, 1.0, model,
        fitted_components=base_report.primary_fit.components)
    assert specs, "expected a residual proposal at the unmodeled peak"

    calls = {"n": 0}

    def fake_pc():
        calls["n"] += 1
        return 1000.0 + (0.0 if calls["n"] == 1 else 13.0)

    def boom(*a, **k):
        raise AssertionError("run_stability_analysis started without budget")

    monkeypatch.setattr(eng.time, "perf_counter", fake_pc)
    monkeypatch.setattr(eng, "run_stability_analysis", boom)

    aug_report, pr, outcome = eng._attempt_proposal(
        x=x, y=y, weights=w, base_report=base_report, spec=specs[0],
        noise_floor=1.0, n_refits=4, rng_seed=0,
        absent_slot_area_fraction=0.02, absent_slot_persistence_threshold=0.7,
        diagnostic_windows=dict(case.grammar.diagnostic_windows),
        budget_remaining=20.0)          # passes the 15 s TOP guard...
    assert outcome == "fast_rejected"   # ...but post-fit remaining 7 s < 15
    assert aug_report is None
    assert "insufficient_budget before stability" in (pr.rejection_reason or "")


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
