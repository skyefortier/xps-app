"""
Quantification lint (spec §8) — region-mismatched ``_rsfKey`` flags.

Pins the adjudicated real-data picture (adjudication-decisions.md #1/#2)
across the whole labeled set, and the rule branches on synthetic inputs.
Flag-only: the lint never mutates its input (pinned).
"""

import copy
import glob
import os

import numpy as np
import pytest

from autofit.lint import FIT_PHYSICS_TOL_EV, lint_project, lint_rsf_tags
from autofit.reference import ReferenceFit, load_reference_fits

REPO = os.path.join(os.path.dirname(__file__), "..", "..")
DATA = os.path.join(REPO, "docs", "autofit", "test_data")


@pytest.fixture(scope="module")
def all_findings():
    out = []
    for zp in sorted(glob.glob(os.path.join(DATA, "*.proj.zip"))):
        out.extend(lint_project(load_reference_fits(zp)))
    return out


def test_k2p_satellite_mistags_all_flagged(all_findings):
    """Adjudication #2: K 2p on every C 1s π→π* satellite — 44 tabs across
    5 projects, all confirmed erroneous (no K in any sample)."""
    hits = [f for f in all_findings
            if f["level"] == "flag" and f["rsf_key"] == "K 2p"]
    assert len(hits) == 44
    assert all(f["tab_region"] == "C 1s" for f in hits)
    assert all(f["category"] == "region_mismatch" for f in hits)
    # π→π* territory (~290.5-291.2 corrected) — evidence recorded per flag
    assert all(290.0 <= f["center_ev"] <= 292.0 for f in hits)


def test_zr3d_b1s_mistags_all_flagged(all_findings):
    """Adjudication #1: Zr 3d on B4C-UCl4 B-B/B-C — 2 peaks × 10 tabs, all
    confirmed erroneous (no Zr in any sample); the B2O3-type peak is tagged
    correctly and must NOT be flagged."""
    hits = [f for f in all_findings
            if f["level"] == "flag" and f["rsf_key"] == "Zr 3d"]
    assert len(hits) == 20
    assert all(f["tab_region"] == "B 1s" for f in hits)
    assert all(f["project"] == "B4C-UCl4.proj.zip" for f in hits)
    # distance evidence from the machine-tier Zr-3d window is carried
    assert all(f["evidence"]["distance_to_nearest_territory_ev"] > 5.0
               for f in hits)


def test_n1s_u4f_satellite_tag_left_alone(all_findings):
    """Adjudication: LEAVE the N 1s tag on the ~397 eV U 4f satellite —
    positionally justified (genuinely N 1s territory).  info, never flag."""
    n1s = [f for f in all_findings if f["rsf_key"] == "N 1s"]
    assert n1s, "expected N 1s cross-region tags in the labeled set"
    assert all(f["level"] == "info" for f in n1s)
    assert all(f["evidence"]["inside_module_window"] for f in n1s)


def test_no_other_flags(all_findings):
    """The adjudicated set contains exactly the two mis-tag patterns."""
    flagged_keys = {f["rsf_key"] for f in all_findings if f["level"] == "flag"}
    assert flagged_keys == {"K 2p", "Zr 3d"}
    assert len([f for f in all_findings if f["level"] == "flag"]) == 64


def _mk_rf(peaks, roi=(280.0, 295.0)):
    be = np.linspace(roi[0], roi[1], 50)
    return ReferenceFit(
        project="synthetic", tab_file="t", name="t",
        raw_be=be, raw_intensity=np.ones_like(be), cc_shift=0.0,
        peaks=peaks, fit_result={},
        ui={"roiMin": str(roi[0]), "roiMax": str(roi[1])},
    )


def test_same_region_key_not_flagged():
    rf = _mk_rf([{"name": "a", "center": 284.8, "_rsfKey": "C 1s"}])
    assert lint_rsf_tags(rf) == []


def test_missing_or_unparseable_key_skipped():
    rf = _mk_rf([{"name": "a", "center": 284.8},
                 {"name": "b", "center": 284.8, "_rsfKey": "banana"},
                 {"name": "c", "center": None, "_rsfKey": "K 2p"}])
    assert lint_rsf_tags(rf) == []


def test_foreign_key_inside_module_window_is_info():
    # N 1s window (396.5, 400.0) contains 398.0 — U 4f tab (real U 4f scans
    # span ~35 eV, ROI midpoint ~387 → the "U 4f" coarse bin)
    rf = _mk_rf([{"name": "sat", "center": 398.0, "_rsfKey": "N 1s"}],
                roi=(370.0, 405.0))
    (f,) = lint_rsf_tags(rf)
    assert f["level"] == "info" and f["tab_region"] == "U 4f"


def test_foreign_key_with_db_window_flagged_by_distance():
    # Zr 3d machine window ~178.3-179.3; peak at 188.5 is far outside
    rf = _mk_rf([{"name": "B-B", "center": 188.5, "_rsfKey": "Zr 3d"}],
                roi=(180.0, 194.0))
    (f,) = lint_rsf_tags(rf)
    assert f["level"] == "flag"
    d = f["evidence"]["distance_to_nearest_territory_ev"]
    assert d > FIT_PHYSICS_TOL_EV


def test_foreign_key_inside_db_window_with_tol_is_info():
    # just above the Zr-3d window max (179.3) but within the ±3 eV allowance
    rf = _mk_rf([{"name": "x", "center": 181.0, "_rsfKey": "Zr 3d"}],
                roi=(178.0, 194.0))
    (f,) = lint_rsf_tags(rf)
    assert f["level"] == "info"
    assert f["evidence"]["inside_fit_physics_window_with_tol"]


def test_unknown_tab_and_unknown_key_skipped():
    # survey-like ROI (midpoint outside every coarse bin) + a key with no
    # module and no DB entry → conservatively skipped
    rf = _mk_rf([{"name": "x", "center": 500.0, "_rsfKey": "K 2p"}],
                roi=(0.0, 1200.0))
    assert lint_rsf_tags(rf) == []


def test_lint_never_mutates_input():
    peaks = [{"name": "sat", "center": 290.9, "_rsfKey": "K 2p"}]
    rf = _mk_rf(peaks)
    before = copy.deepcopy(peaks)
    lint_rsf_tags(rf)
    assert peaks == before
