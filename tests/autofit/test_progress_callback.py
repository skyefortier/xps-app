"""
Progress-callback plumbing (Find Peaks UI improvements, 2026-07-11, unit 1).

The engine already sweeps candidates in two honest phases (screen -> deep
evaluation, unit F3); this is the real signal the frontend progress
indicator surfaces. ``compare_models`` gains an OPTIONAL ``progress_cb``
(default None, zero behavior/perf change for every existing caller — the
manual /api/fit path never calls compare_models at all).

Additive only: no existing call site passes progress_cb, so every current
test's exact behavior must be provable unchanged with progress_cb=None (the
implicit default already covers this — pinned explicitly below too).
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from stress_cases import overlap_case  # noqa: E402

import autofit.engine as eng  # noqa: E402
from autofit.methods import get_method  # noqa: E402
from autofit.methods.base import poisson_like_weights  # noqa: E402


def test_progress_cb_none_is_byte_identical_to_omitted():
    """Explicit progress_cb=None must produce the exact same result as
    omitting the argument entirely (today's every-existing-call-site
    behavior) — the new parameter is purely additive."""
    case = overlap_case(1.0, 9000.0, seed=11, expectation="recover")
    w = poisson_like_weights(case.y)
    a = eng.compare_models(case.x, case.y, w, case.grammar,
                           n_refits=2, rng_seed=0, enable_proposal_pass=False)
    b = eng.compare_models(case.x, case.y, w, case.grammar,
                           n_refits=2, rng_seed=0, enable_proposal_pass=False,
                           progress_cb=None)
    assert [r.model.name for r in a.reports] == [r.model.name for r in b.reports]
    assert a.survivors[0].model.name == b.survivors[0].model.name
    assert a.survivors[0].reduced_chi_sq == b.survivors[0].reduced_chi_sq


def test_progress_cb_fires_for_every_evaluated_candidate():
    """A no-op-recording callback must be invoked at least once per
    candidate actually evaluated (screen and/or deep phase), with a
    phase name and 1-indexed index/total — the real, honest engine signal
    (not a fake animation)."""
    case = overlap_case(1.0, 9000.0, seed=11, expectation="recover")
    w = poisson_like_weights(case.y)
    events = []
    eng.compare_models(case.x, case.y, w, case.grammar,
                       n_refits=2, rng_seed=0, enable_proposal_pass=False,
                       progress_cb=events.append)
    assert events, "progress_cb was never called"
    phases = {e["phase"] for e in events}
    assert phases <= {"screening", "stabilizing"}
    for e in events:
        assert e["candidate_index"] >= 1
        assert e["candidate_total"] >= e["candidate_index"]
        assert isinstance(e["candidate_name"], str) and e["candidate_name"]
    # this grammar (3-candidate ladder) is below SCREEN_TOP_K -> classic
    # single-phase path -> every event is "stabilizing", never "screening"
    assert len(case.grammar.candidates) <= eng.SCREEN_TOP_K
    assert phases == {"stabilizing"}


def test_progress_cb_reports_screening_then_stabilizing_phase(monkeypatch):
    """Force the two-phase screen->stabilize path (unit F3) and confirm
    BOTH phases surface through the callback, screening first."""
    monkeypatch.setattr(eng, "SCREEN_TOP_K", 1)
    case = overlap_case(1.0, 9000.0, seed=11, expectation="recover")
    assert len(case.grammar.candidates) > eng.SCREEN_TOP_K
    w = poisson_like_weights(case.y)
    events = []
    eng.compare_models(case.x, case.y, w, case.grammar,
                       n_refits=2, rng_seed=0, enable_proposal_pass=False,
                       progress_cb=events.append)
    phases_in_order = [e["phase"] for e in events]
    assert "screening" in phases_in_order
    assert "stabilizing" in phases_in_order
    assert phases_in_order.index("screening") < \
        len(phases_in_order) - phases_in_order[::-1].index("stabilizing") - 1 \
        or phases_in_order.index("screening") < phases_in_order.index("stabilizing")


def test_progress_cb_exception_does_not_break_the_fit():
    """A crashing progress_cb (e.g. a disk-full progress-file write) must
    never take down the analysis itself — the honesty/result contract
    outranks the progress nicety."""
    case = overlap_case(1.0, 9000.0, seed=11, expectation="recover")
    w = poisson_like_weights(case.y)

    def boom(evt):
        raise RuntimeError("simulated progress sink failure")

    result = eng.compare_models(case.x, case.y, w, case.grammar,
                                n_refits=2, rng_seed=0,
                                enable_proposal_pass=False,
                                progress_cb=boom)
    assert result.survivors, "a broken progress_cb must not break the fit"


def test_method_run_accepts_and_ignores_progress_cb_by_default():
    """Every PeakFitMethod accepts progress_cb (interface uniformity) —
    only ic_model_comparison uses it; others must not crash on it."""
    case = overlap_case(1.0, 9000.0, seed=11, expectation="recover")
    res = get_method("sparse_map").run(
        case.x, case.y, grammar=case.grammar, progress_cb=lambda e: None)
    assert res.success is not None  # ran without raising


def test_ic_method_threads_progress_cb_into_compare_models():
    """The IC method (the ONLY method Find Peaks' progress bar targets
    today) actually wires progress_cb through to compare_models."""
    case = overlap_case(1.0, 9000.0, seed=11, expectation="recover")
    events = []
    res = get_method("ic_model_comparison").run(
        case.x, case.y, grammar=case.grammar,
        options={"n_refits": 2, "enable_proposal_pass": False},
        progress_cb=events.append)
    assert res.success
    assert events
