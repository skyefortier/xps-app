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


def test_free_parameters_are_owned_by_the_longest_prefix():
    """Codex round 1 (MAJOR): roles "main" and "main_extra" give component
    prefixes where one starts the other; counting by a plain startswith gave
    "main" both components' free parameters and halved its F."""
    model = CandidateModel(name="m", background=BackgroundType.LINEAR,
                           slots=(_slot("main", (286.0, 287.0)), _slot("main_extra", (284.0, 285.0))))
    y = _spectrum(1e4, 1e4, 0.0) + _g(X, 286.5, 150.0, 1.2)     # a weak 'main' beside a strong 'main_extra'
    w = 1.0 / np.sqrt(np.maximum(y, 1.0))
    out = fit_candidate(X, y, w, model)
    assert out.converged
    res = out.lmfit_result
    comps = res.eval_components()
    data, best = np.asarray(res.data, float), np.asarray(res.best_fit, float)
    wr = np.broadcast_to(np.asarray(res.weights if res.weights is not None else 1.0, float), data.shape)
    got = {c.slot_role: c.support for c in out.components}
    for role in ("main", "main_extra"):
        prefix = _slot_prefix(role)
        assert prefix in comps
        own = [n for n, par in res.params.items() if par.vary and par.expr is None
               and max((p for p in comps if n.startswith(p)), key=len) == prefix]
        assert len(own) == 3, (role, own)                 # centre, amplitude, width — its own only
        want = fitting._component_support(data, best, np.asarray(comps[prefix], float), wr, 3, int(res.nvarys))
        assert got[role]["f"] == pytest.approx(want["f"], rel=1e-12), role


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
    unsupported = {"f": 3.0, "delta_chi2": 5.0, "supported": False}
    promoted = dataclasses.replace(
        real, weighted_chi_sq=0.0, boundary_hits=[],
        components=[dataclasses.replace(c, support=unsupported) if c.slot_role == spec.role else c
                    for c in real.components])
    fake_stab = eng.ModelStability(per_slot={}, orphan_rate=0.0, convergence_rate=1.0,
                                   best_outcome=promoted, best_basin_support=1, n_attempted=2)
    monkeypatch.setattr(eng, "run_stability_analysis", lambda *a, **k: fake_stab)
    _, pr, outcome = eng._attempt_proposal(
        x=x, y=y, weights=w, base_report=base, spec=spec,
        noise_floor=1.0, n_refits=2, rng_seed=0,
        absent_slot_area_fraction=0.02, absent_slot_persistence_threshold=0.7,
        diagnostic_windows=dict(case.grammar.diagnostic_windows), budget_remaining=1e6)
    assert outcome == "stability_rejected"
    assert "not supported by the data in the promoted refit" in (pr.rejection_reason or "")
