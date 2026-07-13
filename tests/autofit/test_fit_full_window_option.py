"""Opt-in "fit the entire window" option (2026-07-13, Find Peaks UI
improvements round 3, unit 1).

Today, a CURATED region's grammar slots each carry a fixed,
literature-anchored ``be_window`` that hard-bounds where lmfit can place
that component's center — independent of how wide the user's ROI is (see
docs/autofit/PROGRESS.md's entry for this unit for the full trace). That's
the right default for a region like C 1s, where each of the 6 chemical
states (graphitic/aliphatic/C-O/C=O/OC=O/shake-up) has its own narrow,
chemically-anchored window — but it means an unusually-shifted extreme
component just outside the outermost window is unreachable no matter how
wide the user's ROI is.

``fit_full_window=True`` widens ONLY the outer envelope for a curated
multi-component model (the lowest-BE slot's lower bound and the
highest-BE slot's upper bound extend to the ROI edges; interior slots
keep their chemically-anchored windows exactly as today — never letting
one chemical state wander into another's territory) — and widens fully
to the ROI for a detection/structural-fallback slot (``region ==
"unassigned"``, e.g. Fe 2p or an out-of-grammar preseed), since those
already have no cited per-component window to preserve. Linked slots
(spin-orbit partners, satellites) are NEVER touched — their offset from
the parent is a cited physical constant, unrelated to ROI cropping.

Default is unchanged (``fit_full_window`` defaults to False everywhere)
so every existing call site's behavior is byte-for-byte identical unless
a caller opts in.
"""

import numpy as np
import pytest

from autofit.engine import (_default_params_from_slots, _slot_prefix,
                            fit_candidate, run_stability_analysis)
from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot, LineShape


def _slot(role, region, be_window, **kw):
    return ComponentSlot(role=role, region=region, phase_id="p",
                         be_window=be_window, line_shape=LineShape.GAUSSIAN,
                         fwhm_range=(0.6, 2.2), **kw)


def _model(*slots):
    return CandidateModel(name="m", background=BackgroundType.LINEAR, slots=tuple(slots))


def _bounds(params, role):
    par = params[f"{_slot_prefix(role)}center"]
    return par.min, par.max


def _value(params, role):
    return params[f"{_slot_prefix(role)}center"].value


def test_default_leaves_curated_bounds_untouched():
    model = _model(_slot("graphitic", "C 1s", (284.0, 284.8)),
                   _slot("co", "C 1s", (285.8, 286.8)))
    x = np.arange(270.0, 300.0, 0.1)
    params = _default_params_from_slots(model, x=x, y_net=None)
    assert _bounds(params, "graphitic") == (284.0, 284.8)
    assert _bounds(params, "co") == (285.8, 286.8)


def test_fit_full_window_defaults_to_false():
    """Calling without the kwarg at all must behave identically to
    explicit False — no accidental behavior change for any existing
    caller that doesn't know about the new parameter."""
    model = _model(_slot("graphitic", "C 1s", (284.0, 284.8)))
    x = np.arange(270.0, 300.0, 0.1)
    implicit = _default_params_from_slots(model, x=x, y_net=None)
    explicit = _default_params_from_slots(model, x=x, y_net=None, fit_full_window=False)
    assert _bounds(implicit, "graphitic") == _bounds(explicit, "graphitic")


def test_full_window_widens_only_outer_envelope_for_multi_slot_curated_model():
    """The C 1s-shaped case: 3 chemically-anchored slots. Only the
    lowest-BE slot's LOWER bound and the highest-BE slot's UPPER bound
    move to the ROI edges — the interior slot (co) and the untouched
    sides of the outer slots keep their literature windows exactly, so
    a component can never wander into a neighboring chemical state's
    territory."""
    model = _model(
        _slot("graphitic", "C 1s", (284.0, 285.0)),
        _slot("co", "C 1s", (286.0, 287.0)),
        _slot("shake_up", "C 1s", (290.0, 292.0)),
    )
    x = np.arange(270.0, 300.0, 0.1)
    params = _default_params_from_slots(model, x=x, y_net=None, fit_full_window=True)
    lo, hi = _bounds(params, "graphitic")
    assert lo == pytest.approx(270.0) and hi == pytest.approx(285.0)
    assert _bounds(params, "co") == (286.0, 287.0)          # interior: untouched
    lo, hi = _bounds(params, "shake_up")
    assert lo == pytest.approx(290.0) and hi == pytest.approx(299.9, abs=0.05)


def test_full_window_never_narrows_or_inverts_a_bound_when_roi_is_shifted():
    """Regression (2026-07-13 Codex review, round 1 BLOCKER): a ROI that
    does NOT fully contain a slot's own literature window (e.g. the user
    set a narrower/shifted window than the region's full literature
    span) must leave that untouched side EXACTLY as it was — never
    assign a bare ROI edge that could sit on the wrong side of the
    slot's own bound and invert it (min > max), and never narrow an
    already-correct bound."""
    model = _model(
        _slot("graphitic", "C 1s", (284.0, 285.0)),
        _slot("co", "C 1s", (286.0, 287.0)),
        _slot("shake_up", "C 1s", (290.0, 292.0)),
    )
    # ROI's low edge (287.0) sits ABOVE the lowest slot's own upper bound
    # (285.0) — the pre-fix code assigned roi_lo=287.0 as graphitic's
    # lower bound unconditionally, producing (287.0, 285.0): min > max.
    x = np.arange(287.0, 300.0, 0.1)
    params = _default_params_from_slots(model, x=x, y_net=None, fit_full_window=True)
    lo, hi = _bounds(params, "graphitic")
    assert lo <= hi, (lo, hi)
    assert (lo, hi) == (284.0, 285.0)          # untouched: ROI doesn't reach it
    lo, hi = _bounds(params, "shake_up")
    assert lo == 290.0 and hi == pytest.approx(299.9, abs=0.05)  # this side still widens


def test_full_window_widens_a_single_curated_slot_on_both_sides():
    """A region with exactly one primary curated slot (e.g. Cl 2p3/2) has
    no "interior" component to protect — both bounds widen."""
    model = _model(_slot("main_p32", "Cl 2p", (196.0, 199.0)))
    x = np.arange(190.0, 210.0, 0.1)
    params = _default_params_from_slots(model, x=x, y_net=None, fit_full_window=True)
    lo, hi = _bounds(params, "main_p32")
    assert lo == pytest.approx(190.0) and hi == pytest.approx(209.9, abs=0.05)


def test_full_window_widens_detection_slot_fully_to_roi():
    """A detection/structural-fallback slot (region == 'unassigned', e.g.
    the out-of-grammar preseed channel or Fe 2p) has no cited
    per-component window to preserve — it widens fully to the ROI on
    BOTH sides, not just an outer envelope."""
    model = _model(_slot("detected_peak_0", "unassigned", (200.0, 201.0)))
    x = np.arange(190.0, 210.0, 0.1)
    params = _default_params_from_slots(model, x=x, y_net=None, fit_full_window=True)
    lo, hi = _bounds(params, "detected_peak_0")
    assert lo == pytest.approx(190.0) and hi == pytest.approx(209.9, abs=0.05)


def test_full_window_mixed_model_branches_per_slot_not_per_region():
    """A curated model with an ADDED out-of-grammar preseed slot in the
    SAME candidate (the real "low-BE C1s" scenario from the run brief):
    the curated slots get outer-envelope treatment, the unassigned slot
    gets the full ROI — branching on how EACH SLOT was solved, not on
    whether the region as a whole has grammar."""
    model = _model(
        _slot("graphitic", "C 1s", (284.0, 285.0)),
        _slot("shake_up", "C 1s", (290.0, 292.0)),
        _slot("proposed_peak_0", "unassigned", (279.0, 280.0)),
    )
    x = np.arange(270.0, 300.0, 0.1)
    params = _default_params_from_slots(model, x=x, y_net=None, fit_full_window=True)
    lo, hi = _bounds(params, "graphitic")
    assert lo == pytest.approx(270.0) and hi == pytest.approx(285.0)
    lo, hi = _bounds(params, "proposed_peak_0")
    assert lo == pytest.approx(270.0) and hi == pytest.approx(299.9, abs=0.05)


def test_full_window_leaves_linked_slot_offset_and_curated_starting_guess_untouched():
    """A spin-orbit doublet's offset is a cited physical splitting, not a
    cropping artifact — it must NEVER widen. And a curated slot's
    STARTING value (the optimizer's initial guess) stays at the original
    literature midpoint even when its bound widens — only the hard
    constraint relaxes, not where the search starts."""
    parent = _slot("main_p32", "Cl 2p", (196.0, 199.0))
    child = _slot("main_p12", "Cl 2p", (198.0, 201.0),
                 linked_to="main_p32", linked_offset_range=(1.5, 1.7))
    model = _model(parent, child)
    x = np.arange(190.0, 210.0, 0.1)
    default_params = _default_params_from_slots(model, x=x, y_net=None)
    full_params = _default_params_from_slots(model, x=x, y_net=None, fit_full_window=True)

    offset_name = f"{_slot_prefix('main_p12')}offset"
    assert (full_params[offset_name].min, full_params[offset_name].max) == \
        (default_params[offset_name].min, default_params[offset_name].max) == (1.5, 1.7)

    # starting guess for the widened parent stays at its own literature
    # midpoint (197.5), never the ROI midpoint (200.0)
    assert _value(full_params, "main_p32") == pytest.approx(197.5)


def test_full_window_no_op_when_x_is_none():
    """The option can never invent a window when there's no data to
    derive an ROI extent from — falls back to the slot's own window,
    same as the default path."""
    model = _model(_slot("graphitic", "C 1s", (284.0, 285.0)))
    params = _default_params_from_slots(model, x=None, y_net=None, fit_full_window=True)
    assert _bounds(params, "graphitic") == (284.0, 285.0)


# ── End-to-end: a real lmfit fit, not just params construction ──────────

def _c1s_shaped_spectrum(outer_true_center):
    """Two-component spectrum mimicking C 1s's graphitic (inner, well
    within its window) + an unusually-shifted oxidized state (outer) that
    may sit OUTSIDE its literature window — a wide user-set ROI (275-300)
    that a clean, flat baseline makes safe to fit in full."""
    rng = np.random.default_rng(7)
    x = np.arange(275.0, 300.0, 0.05)

    def g(c, a, w):
        return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)

    y = 300.0 + g(284.5, 5000, 0.8) + g(outer_true_center, 4000, 1.0)
    return x, y + rng.normal(0, 10, len(x))


def _c1s_shaped_model():
    return _model(
        _slot("graphitic", "C 1s", (284.0, 285.0)),
        _slot("shake_up", "C 1s", (290.0, 292.0)),
    )


def test_default_clamps_an_out_of_window_component_to_the_bound():
    """The outer slot's TRUE peak (294.0 eV) sits outside its literature
    window (290-292) — by default the fit can only reach as far as the
    window's own edge, landing well short of the true position. This is
    today's behavior, unchanged."""
    x, y = _c1s_shaped_spectrum(outer_true_center=294.0)
    w = 1 / np.sqrt(np.maximum(y, 1))
    model = _c1s_shaped_model()
    out = fit_candidate(x, y, w, model)
    assert out.converged
    by_role = {c.slot_role: c for c in out.components}
    assert by_role["shake_up"].position == pytest.approx(292.0, abs=0.05)
    assert by_role["shake_up"].position < 293.0   # nowhere near the true 294.0


def test_full_window_lets_the_fit_reach_the_true_out_of_window_position():
    """Same spectrum, ``fit_full_window=True``: the outer slot's upper
    bound now extends to the ROI edge (300.0), so the fit can actually
    reach the true peak at 294.0 — while the INNER (graphitic) slot,
    never near a boundary, lands in the same place either way."""
    x, y = _c1s_shaped_spectrum(outer_true_center=294.0)
    w = 1 / np.sqrt(np.maximum(y, 1))
    model = _c1s_shaped_model()
    out = fit_candidate(x, y, w, model, fit_full_window=True)
    assert out.converged
    by_role = {c.slot_role: c for c in out.components}
    assert by_role["shake_up"].position == pytest.approx(294.0, abs=0.15)
    assert by_role["graphitic"].position == pytest.approx(284.5, abs=0.1)


def test_full_window_stability_does_not_orphan_a_widened_component():
    """Regression (2026-07-13 Codex review, round 1 BLOCKER): identity-
    matching during stability re-fits (``match_components_to_slots`` /
    ``_effective_be_window``) must agree with the SAME widened bound the
    fit was actually built with — otherwise a refit that correctly
    places the outer slot at its true, out-of-literature-window position
    (294.0) gets rejected as an "orphan" against the slot's UNWIDENED
    original window (290-292) every time, tanking persistence and
    defeating the whole point of the option even though the fit itself
    is working exactly as intended."""
    x, y = _c1s_shaped_spectrum(outer_true_center=294.0)
    w = 1 / np.sqrt(np.maximum(y, 1))
    model = _c1s_shaped_model()
    primary = fit_candidate(x, y, w, model, fit_full_window=True)
    assert primary.converged
    stability = run_stability_analysis(
        x, y, w, model, primary, noise_floor=1.0, n_refits=6, rng_seed=0,
        fit_full_window=True,
    )
    shake_up = stability.per_slot["shake_up"]
    assert shake_up.persistence >= 0.8, (
        f"shake_up persistence={shake_up.persistence} — the widened "
        "component is being falsely orphaned against its original window")
    assert stability.orphan_rate < 0.2, stability.orphan_rate
