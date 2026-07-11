"""
Stage-2 completeness recalibration pins (2026-07-10) — the measured
chokepoints from the Step-1 diagnosis (PROGRESS.md "Stage-2 calibration —
STEP-1 DIAGNOSIS"), fixed and pinned:

Chokepoint 2 — F2 proposal eligibility keyed on WINDOW MEMBERSHIP, so a
residual inside a canonical window was blocked even when the current
model had no slot there (measured: ds8 winner B3 lacks a satellite slot;
the 290.76 eV satellite intensity was detected at prom_z 23 and
permanently unreachable).  New rule: a residual cluster is blocked only
by (i) proximity to a FITTED component (0.5 × that component's own
fitted width — transferable units) or (ii) sitting inside a POPULATED
slot's window (that slot owns its window's residuals — this preserves
the distributed-mismatch honesty behavior: a lineshape-mismatch tail
inside an occupied window must surface as flags, never as an invented
tail-fixer peak).

All synthetic, deterministic.
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
)

import autofit.engine as eng  # noqa: E402
from autofit.methods import get_method  # noqa: E402
from autofit.methods.base import poisson_like_weights  # noqa: E402

ETA = 0.30
IC_OPTS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
           "enable_proposal_pass": True}


def _fit_base(x, y, grammar):
    w = poisson_like_weights(y)
    res = eng.compare_models(x, y, w, grammar, n_refits=2, rng_seed=0,
                             enable_proposal_pass=False,
                             enable_preseed=False)
    rep = res.reports[0]
    y_fit = rep.primary_fit.lmfit_result.best_fit + rep.primary_fit.background
    return rep, y_fit


def test_proposal_eligible_when_model_lacks_the_slot():
    """A canonical window EXISTS for the region but THIS candidate has no
    slot there: residual intensity inside that window must be proposal-
    eligible (the old window-membership test blocked it — chokepoint 2)."""
    x = np.arange(190.0, 206.0, 0.05)
    sig = (_pv(x, 9000.0, 196.5, 1.2, ETA)
           + _pv(x, 2600.0, 203.0, 1.4, ETA))     # inside the 202-204 window
    y = _noisy(sig + _linear_bg(x), 41)
    grammar = _grammar(
        [_cand("P1", [_slot("main_a", (195.5, 197.5))])],
        windows={"SYN:main_a": (195.5, 197.5),
                 "SYN:satellite": (202.0, 204.0)})   # no P1 slot here
    rep, y_fit = _fit_base(x, y, grammar)
    specs = eng._detect_residual_proposals(
        x, y, y_fit, 1.0, rep.model,
        fitted_components=rep.primary_fit.components)
    assert any(abs(s.center_init - 203.0) < 0.5 for s in specs), (
        "unmodeled intensity inside an unpopulated canonical window must "
        f"be proposal-eligible; got {[round(s.center_init, 2) for s in specs]}")


def test_proposal_blocked_inside_populated_window():
    """Residual structure INSIDE a populated slot's window (a lineshape /
    width mismatch flank) stays proposal-INELIGIBLE: that slot owns its
    window's residuals, and the mismatch must surface as flags, not as an
    invented tail-fixer peak."""
    x = np.arange(190.0, 206.0, 0.05)
    # truth: main + a flank bump INSIDE the main window, 0.9 eV from the
    # main center (outside the 0.5×fwhm proximity zone — only the
    # populated-window rule can block it)
    sig = (_pv(x, 9000.0, 196.3, 1.2, ETA)
           + _pv(x, 1400.0, 197.2, 0.9, ETA))
    y = _noisy(sig + _linear_bg(x), 43)
    grammar = _grammar([_cand("P1", [_slot("main_a", (195.5, 197.5))])],
                       windows={"SYN:main_a": (195.5, 197.5)})
    rep, y_fit = _fit_base(x, y, grammar)
    comp = next(c for c in rep.primary_fit.components
                if c.slot_role == "main_a")
    assert abs(197.2 - comp.position) > 0.5 * comp.fwhm, \
        "test geometry must isolate the populated-window rule"
    specs = eng._detect_residual_proposals(
        x, y, y_fit, 1.0, rep.model,
        fitted_components=rep.primary_fit.components)
    assert not any(abs(s.center_init - 197.2) < 0.4 for s in specs), (
        "in-populated-window residual must stay the slot's job; got "
        f"{[round(s.center_init, 2) for s in specs]}")


def test_proposal_blocked_near_fitted_component():
    """Proximity rule in transferable units: a residual argmax within
    0.5 × the fitted component's own width is that component's business
    (position/width refinement), never a new-peak proposal."""
    x = np.arange(190.0, 206.0, 0.05)
    sig = _pv(x, 9000.0, 196.5, 1.6, ETA)
    y = _noisy(sig + _linear_bg(x), 47)
    grammar = _grammar([_cand("P1", [_slot("main_a", (195.5, 197.5))])])
    rep, y_fit = _fit_base(x, y, grammar)
    comp = next(c for c in rep.primary_fit.components
                if c.slot_role == "main_a")
    # synthetic residual cluster right on the component's flank
    y_fit_deficit = np.array(y_fit)
    flank = comp.position + 0.4 * comp.fwhm
    mask = np.abs(x - flank) < 0.15
    y_fit_deficit[mask] -= 12.0 * np.sqrt(np.maximum(y[mask], 1.0))
    specs = eng._detect_residual_proposals(
        x, y, y_fit_deficit, 1.0, rep.model,
        fitted_components=rep.primary_fit.components)
    assert not any(abs(s.center_init - flank) < 0.3 for s in specs), (
        f"flank residual at {flank:.2f} (0.4×fwhm from the component) must "
        "be blocked by proximity")


def test_e2e_winner_lacks_slot_rescued_by_proposal():
    """End-to-end chokepoint-2 pin: a candidate family WITHOUT a slot for
    real in-window intensity must gain it through the proposal pass, and
    the emitted model must carry the component."""
    x = np.arange(190.0, 206.0, 0.05)
    sig = (_pv(x, 9000.0, 196.5, 1.2, ETA)
           + _pv(x, 2600.0, 203.0, 1.4, ETA))
    y = _noisy(sig + _linear_bg(x), 41)
    grammar = _grammar(
        [_cand("P1", [_slot("main_a", (195.5, 197.5))])],
        windows={"SYN:main_a": (195.5, 197.5),
                 "SYN:satellite": (202.0, 204.0)})
    res = get_method("ic_model_comparison").run(
        x, y, grammar=grammar,
        options={**IC_OPTS, "enable_preseed": False})
    emitted = [p for p in res.peaks if abs(p["center"] - 203.0) < 0.5]
    assert emitted, (
        "satellite-window intensity missing from the final model: "
        f"{[(p['role'], round(p['center'], 2)) for p in res.peaks]}")
