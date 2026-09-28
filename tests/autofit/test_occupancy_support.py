"""Find Peaks occupancy is the server's support F test, not a 1-count floor
(noise-floor unit, 2026-09-27; plan
docs/superpowers/plans/2026-09-27-occupancy-f-test.md).

A slot is OCCUPIED by a component the data support: with the other components
held as fitted, removing it makes the fit significantly worse
(``fitting._component_support``, F >= SUPPORT_MIN_F) — the statistic Run Fit's
"not supported by the data" outcome uses. The old rule, ``amplitude > 1.0``,
judged a slot occupied at 1.5 counts and empty at 0.5 whatever the data's
scale. Pinned here:

* the verdict is carried on every fitted component and is invariant to a
  uniform rescaling of the intensities (while every channel stays above the
  Poisson variance floor), where the old floor flips;
* residue at high counts (above 1 count, removing it costs nothing) is not an
  occupant — the old floor accepted it;
* an unsupported component occupies no slot and is NOT an orphan (an orphan is
  a supported peak no slot expects); a supported component outside every
  window still is;
* the proposal gate and the detectability status read the same verdict.
"""
import numpy as np
import pytest

import fitting
from autofit.confidence import build_confidence_vector
from autofit.engine import (FittedComponent, _occupies, _slot_prefix, fit_candidate,
                            match_components_to_slots)
from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot, LineShape


def _slot(role, be_window, fwhm_range=(0.5, 2.5)):
    return ComponentSlot(role=role, region="C 1s", phase_id="p", be_window=be_window,
                         line_shape=LineShape.GAUSSIAN, fwhm_range=fwhm_range)


MODEL = CandidateModel(name="m", background=BackgroundType.LINEAR,
                       slots=(_slot("main", (284.0, 285.0)), _slot("minor", (286.0, 287.0))))
X = np.arange(280.0, 292.0, 0.05)
Z = np.random.default_rng(20260927).standard_normal(X.size)   # one fixed noise pattern


def _g(x, c, a, w):
    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)


def _spectrum(baseline, main_amp, minor_amp):
    truth = baseline + _g(X, 284.5, main_amp, 1.0) + _g(X, 286.5, minor_amp, 1.2)
    return truth + np.sqrt(truth) * Z


def _fit(y):
    w = 1.0 / np.sqrt(np.maximum(y, 1.0))     # the server's / the engine's Poisson weights
    out = fit_candidate(X, y, w, MODEL)
    assert out.converged
    return {c.slot_role: c for c in out.components}


def test_every_fitted_component_carries_the_servers_support_verdict():
    comps = _fit(_spectrum(1e4, 2e4, 2e3))
    for role in ("main", "minor"):
        s = comps[role].support
        assert s is not None and set(s) >= {"f", "delta_chi2", "supported"}, (role, s)
        assert s["supported"] is True
        assert s["f"] >= fitting.SUPPORT_MIN_F


def test_the_verdict_is_invariant_to_rescaling_where_the_old_floor_flips():
    y = _spectrum(1e4, 2e4, 2e3)
    c = 4e-4          # counts -> a rate: the minor line's amplitude drops from ~2000 to ~0.8
    assert np.min(c * y) > 1.0, "every channel stays above the Poisson variance floor"
    a, b = _fit(y), _fit(c * y)
    assert a["minor"].amplitude > 1.0 > b["minor"].amplitude, "the old rule would flip here"
    for role in ("main", "minor"):
        assert a[role].support["supported"] == b[role].support["supported"] is True, role
        assert b[role].support["f"] == pytest.approx(a[role].support["f"], rel=1e-4), role
        assert _occupies(a[role]) and _occupies(b[role])


def test_residue_above_one_count_is_not_an_occupant():
    # 5 counts on a 1e5-count baseline: the old floor called it occupied
    comps = _fit(_spectrum(1e5, 2e5, 5.0))
    minor = comps["minor"]
    assert minor.support["supported"] is False, minor.support
    assert not _occupies(minor)


def _comp(pos, amp, support):
    return FittedComponent(slot_role="?", position=pos, fwhm=1.0, amplitude=amp,
                           shape_params={}, line_shape=LineShape.GAUSSIAN, support=support)


def test_an_unsupported_component_leaves_its_slot_empty_and_is_not_an_orphan():
    main = _comp(284.5, 1e4, {"f": 1e5, "delta_chi2": 1e6, "supported": True})
    weak = _comp(286.5, 40.0, {"f": 2.1, "delta_chi2": 12.0, "supported": False})
    m = match_components_to_slots([main, weak], MODEL, noise_floor=1.0)
    assert m["main"] is not None and m["main"].support["supported"]
    assert m["minor"] is None, "the slot is EMPTY"
    assert m["__orphans__"] == [], "and the component is not an unexpected extra peak"
    assert m["__unsupported__"] == [weak]


def test_a_supported_component_no_slot_accepts_is_still_an_orphan():
    main = _comp(284.5, 1e4, {"f": 1e5, "delta_chi2": 1e6, "supported": True})
    stray = _comp(289.0, 900.0, {"f": 300.0, "delta_chi2": 5e3, "supported": True})
    m = match_components_to_slots([main, stray], MODEL, noise_floor=1.0)
    assert [o.position for o in m["__orphans__"]] == [289.0]
    assert m["__unsupported__"] == []


def test_without_a_fit_behind_it_occupancy_is_the_sign_of_the_amplitude():
    assert _occupies(_comp(284.5, 0.3, None)), "0.3 > 0: no floor"
    assert not _occupies(_comp(284.5, 0.0, None))
    m = match_components_to_slots([_comp(284.5, 0.0, None)], MODEL, noise_floor=1.0)
    assert m["main"] is None and m["__orphans__"] == []


class _Report:
    """The fields build_confidence_vector reads."""
    def __init__(self, comp):
        class _S:  # stability
            per_slot = {}
        class _P:  # primary fit
            components = [comp]
            boundary_hits = []
            lmfit_result = None
        self.stability, self.primary_fit, self.model = _S(), _P(), MODEL


@pytest.mark.parametrize("support,status", [
    ({"f": 50.0, "delta_chi2": 900.0, "supported": True}, "above_floor"),
    ({"f": 3.0, "delta_chi2": 40.0, "supported": False}, "present_but_poorly_constrained"),
    ({"f": 0.0, "delta_chi2": -1.0, "supported": False}, "not_confidently_detected"),
])
def test_detectability_reads_the_same_verdict(support, status):
    comp = FittedComponent(slot_role="minor", position=286.5, fwhm=1.0, amplitude=0.4,
                           shape_params={}, line_shape=LineShape.GAUSSIAN, support=support)
    d = build_confidence_vector(_Report(comp), "minor", noise_floor=1.0)["detectability"]
    assert d["status"] == status
    assert d["basis"] == "support_f_test" and d["support_min_f"] == fitting.SUPPORT_MIN_F


def test_an_amplitude_tied_partner_follows_its_parents_verdict():
    """A spin-orbit partner at a fixed area ratio has no amplitude of its own:
    it follows its root, as the server's support check makes a linked
    component follow its root."""
    x = np.arange(370.0, 400.0, 0.05)
    main = ComponentSlot(role="main_7_2", region="U 4f", phase_id="p", be_window=(380.0, 382.0),
                         line_shape=LineShape.GAUSSIAN, fwhm_range=(0.8, 2.5))
    partner = ComponentSlot(role="main_5_2", region="U 4f", phase_id="p", be_window=(390.0, 393.5),
                            line_shape=LineShape.GAUSSIAN, fwhm_range=(0.8, 2.5),
                            linked_to="main_7_2", linked_offset_range=(10.7, 11.1), area_ratio=0.75)
    model = CandidateModel(name="d", background=BackgroundType.LINEAR, slots=(main, partner))
    truth = 500.0 + _g(x, 380.9, 8000.0, 1.6) + _g(x, 391.8, 6000.0, 1.6)
    y = truth + np.sqrt(truth) * np.random.default_rng(3).standard_normal(x.size)
    out = fit_candidate(x, y, 1.0 / np.sqrt(np.maximum(y, 1.0)), model)
    assert out.converged
    comps = {c.slot_role: c for c in out.components}
    assert comps["main_5_2"].support["follows"] == "main_7_2"
    assert comps["main_5_2"].support["supported"] == comps["main_7_2"].support["supported"] is True
    assert "follows" not in comps["main_7_2"].support


def _manual_support(res, prefix, n_own):
    comps = res.eval_components()
    data, best = np.asarray(res.data, float), np.asarray(res.best_fit, float)
    wr = np.broadcast_to(np.asarray(res.weights if res.weights is not None else 1.0, float), data.shape)
    return fitting._component_support(data, best, np.asarray(comps[prefix], float), wr, n_own, int(res.nvarys))


@pytest.mark.parametrize("strong_role,strong_shape,n_strong", [
    ("main_extra", LineShape.GAUSSIAN, 3),   # round 1: "main" is a prefix of "main_extra"
    ("main_gl", LineShape.GAUSSIAN, 3),      # round 2: "s_main_gl_ratio" is main's gl_ratio, not main_gl's
])
def test_free_parameters_are_owned_by_declaration_not_by_prefix(strong_role, strong_shape, n_strong):
    """Codex rounds 1-2 (MAJOR): prefix matching — plain or longest — assigned
    a parameter to the wrong component and halved an F. A weak pseudo-Voigt
    'main' (4 own parameters) beside a strong component whose role extends
    'main'."""
    weak = ComponentSlot(role="main", region="C 1s", phase_id="p", be_window=(286.0, 287.0),
                         line_shape=LineShape.PSEUDO_VOIGT, fwhm_range=(0.5, 2.5))
    strong = ComponentSlot(role=strong_role, region="C 1s", phase_id="p", be_window=(284.0, 285.0),
                           line_shape=strong_shape, fwhm_range=(0.5, 2.5))
    model = CandidateModel(name="m", background=BackgroundType.LINEAR, slots=(weak, strong))
    y = _spectrum(1e4, 1e4, 0.0) + _g(X, 286.5, 165.0, 1.2)
    out = fit_candidate(X, y, 1.0 / np.sqrt(np.maximum(y, 1.0)), model)
    assert out.converged
    res = out.lmfit_result
    assert int(res.nvarys) == 4 + n_strong
    got = {c.slot_role: c.support for c in out.components}
    for role, n_own in (("main", 4), (strong_role, n_strong)):
        want = _manual_support(res, _slot_prefix(role), n_own)
        assert got[role]["f"] == pytest.approx(want["f"], rel=1e-12), (role, got[role], want)


def test_absent_slot_bic_removes_only_the_slots_own_parameters():
    """Codex round 2 (MAJOR): the absent-slot BIC* adjustment counted by
    prefix too — roles minor / minor_extra removed six parameters for a
    three-parameter slot (a 16.9-point BIC* bias from naming alone)."""
    from autofit.engine import _count_slot_free_params
    for extra in ("minor_extra", "extra"):
        slots = (_slot("main", (284.0, 285.0)), _slot("minor", (286.0, 287.0)), _slot(extra, (288.0, 289.0)))
        model = CandidateModel(name="m", background=BackgroundType.LINEAR, slots=slots)
        y = _spectrum(1e4, 1e4, 150.0) + _g(X, 288.5, 3000.0, 1.0)
        out = fit_candidate(X, y, 1.0 / np.sqrt(np.maximum(y, 1.0)), model)
        assert out.converged
        assert [_count_slot_free_params(s, out, model) for s in slots] == [3, 3, 3], extra


def test_every_built_in_grammar_declares_each_parameter_exactly_once():
    """Declared ownership is complete and unambiguous on every built-in
    grammar: each parameter the engine creates is declared by exactly one
    slot, or is a shared width parameter owned by none."""
    from autofit import grammar as G
    from autofit.engine import _default_params_from_slots, _param_owner_by_name, _slot_param_names
    n = 0
    for reg, mats in [("C 1s", ["graphite", "x"]), ("U 4f", ["UCl4", "x"]), ("B 1s", ["BN", "B2O3", "B4C", "x"]),
                      ("Cl 2p", ["UCl4", "x"]), ("N 1s", ["BN", "x"])]:
        for mc in G.MaterialClass:
            for mat in mats:
                try:
                    gr = G.resolve([G.Phase(id="p", material_class=mc, regions=(reg,), material=mat)], reg)
                except Exception:
                    continue
                for cand in gr.candidates:
                    lo = min(s.be_window[0] for s in cand.slots) - 5
                    hi = max(s.be_window[1] for s in cand.slots) + 5
                    params = _default_params_from_slots(cand, x=np.arange(lo, hi, 0.1), y_net=None)
                    declared = [nm for s in cand.slots for nm in _slot_param_names(s)]
                    assert len(declared) == len(set(declared)), (cand.name, "a name two slots declare")
                    owner = _param_owner_by_name(cand)
                    shared = {nm for nm, _, _ in cand.shared_fwhm_params}
                    stray = [nm for nm in params if nm not in owner and nm not in shared]
                    assert not stray, (reg, cand.name, stray)
                    n += 1
    assert n >= 40, n


def test_a_proposal_whose_promoted_refit_does_not_support_it_is_rejected(monkeypatch):
    """Codex round 1 (MAJOR): the stability pass can promote a deeper refit;
    the proposal must be supported in THAT fit (what would be emitted), not
    only in the initial augmented one — as the boundary pegs already were."""
    import dataclasses
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    import autofit.engine as eng
    from autofit.methods.base import poisson_like_weights
    from stress_cases import isolated_missing_peak_case

    case = isolated_missing_peak_case(seed=71)
    x, y = case.x, case.y
    w = poisson_like_weights(y)
    res = eng.compare_models(x, y, w, case.grammar, n_refits=2, rng_seed=0,
                             enable_proposal_pass=False, enable_preseed=False)
    base = res.reports[0]
    y_fit = base.primary_fit.lmfit_result.best_fit + base.primary_fit.background
    spec = eng._detect_residual_proposals(x, y, y_fit, 1.0, base.model,
                                          fitted_components=base.primary_fit.components)[0]
    aug_model = eng._augmented_candidate(base.model, spec)
    bg = eng._compute_background(x, y, aug_model.background)
    init = eng._initial_params_for_augmented(aug_model, base.primary_fit, spec, x, y - bg)
    real = eng.fit_candidate(x, y, w, aug_model, initial_params=init)
    assert next(c for c in real.components if c.slot_role == spec.role).support["supported"], \
        "the initial augmented fit supports the proposal (else this test proves nothing)"
    def attempt(support):
        promoted = dataclasses.replace(
            real, weighted_chi_sq=0.0, boundary_hits=[],
            components=[dataclasses.replace(c, support=support) if c.slot_role == spec.role else c
                        for c in real.components])
        # a PASSING stability entry for the proposal (round 2 MINOR: with none,
        # the old code rejected for another reason and the test proved nothing)
        ok = eng.SlotStability(role=spec.role, persistence=1.0, position_median=1.0,
                               position_mad=0.0, fwhm_median=1.0, fwhm_mad=0.0, amplitude_median=1.0)
        fake_stab = eng.ModelStability(per_slot={spec.role: ok}, orphan_rate=0.0, convergence_rate=1.0,
                                       best_outcome=promoted, best_basin_support=1, n_attempted=2)
        monkeypatch.setattr(eng, "run_stability_analysis", lambda *a, **k: fake_stab)
        return eng._attempt_proposal(
            x=x, y=y, weights=w, base_report=base, spec=spec,
            noise_floor=1.0, n_refits=2, rng_seed=0,
            absent_slot_area_fraction=0.02, absent_slot_persistence_threshold=0.7,
            diagnostic_windows=dict(case.grammar.diagnostic_windows), budget_remaining=1e6)

    _, pr, outcome = attempt({"f": 3.0, "delta_chi2": 5.0, "supported": False})
    assert outcome == "stability_rejected"
    assert "not supported by the data in the promoted refit" in (pr.rejection_reason or "")
    # the counterpart: the same promotion WITH support is accepted
    _, pr, outcome = attempt({"f": 300.0, "delta_chi2": 5e3, "supported": True})
    assert outcome == "accepted", pr.rejection_reason


def test_one_ownership_map_for_every_attribution_site():
    """The support F, the absent-slot BIC*, boundary-hit labels, the per-slot
    correlation, the payload's σ and the Bayesian intervals all attribute a
    parameter through _param_owner_by_name — never a prefix."""
    from autofit.engine import _param_owner_by_name, _role_for_param
    weak = ComponentSlot(role="main", region="C 1s", phase_id="p", be_window=(286.0, 287.0),
                         line_shape=LineShape.PSEUDO_VOIGT, fwhm_range=(0.5, 2.5))
    strong = ComponentSlot(role="main_gl", region="C 1s", phase_id="p", be_window=(284.0, 285.0),
                           line_shape=LineShape.GAUSSIAN, fwhm_range=(0.5, 2.5))
    owner = _param_owner_by_name(CandidateModel(name="m", background=BackgroundType.LINEAR, slots=(weak, strong)))
    p_main, p_gl = _slot_prefix("main"), _slot_prefix("main_gl")
    assert _role_for_param(p_main + "gl_ratio", owner) == "main"      # == p_gl + "ratio"
    assert _role_for_param(p_gl + "fwhm", owner) == "main_gl"
    assert _role_for_param("shared_contamination_fwhm", owner) is None
    import inspect
    import autofit.confidence as conf
    import autofit.methods.bayesian_exchange_mc as bx
    import autofit.methods.ic_model_comparison as ic
    for fn in (conf._max_correlation, ic._peaks_from_report, bx):
        src = inspect.getsource(fn)
        assert "_param_owner_by_name" in src, fn
