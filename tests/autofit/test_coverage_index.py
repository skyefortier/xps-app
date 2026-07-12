"""
autofit.coverage_index — the Find-Peaks region-selector coverage index
(2026-07-11, UI improvements unit 3).

Verifies the tier classification (curated / machine / structure_only) is
honest and consistent with the underlying Phase D framework, and that
ROI hints never assert a position that isn't actually sourced.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from autofit.coverage_index import region_coverage_index  # noqa: E402
from autofit.regions import registered_regions  # noqa: E402


@pytest.fixture(scope="module")
def index():
    return region_coverage_index()


def test_index_covers_the_full_periodic_table_span(index):
    """Every real Z=1..96 element is represented. A SUPERSET check: the
    index may ALSO contain a defensive-completeness entry for a region
    module registered outside the periodic-table framework entirely
    (symbol=None) — see test_the_five_existing_curated_regions_unchanged
    for why (test_resolver.py's shared-process 'Fk 2p')."""
    from autofit.coverage import PERIODIC_TABLE
    symbols = {e["symbol"] for e in index if e["symbol"] is not None}
    assert symbols == set(PERIODIC_TABLE)
    for e in index:
        if e["symbol"] is not None:
            assert 1 <= e["z"] <= 96


def test_every_entry_is_a_valid_parseable_region(index):
    """Every entry with a real symbol parses back to itself; a
    defensive-completeness entry for a NON-periodic-table region
    (symbol=None, e.g. a shared-process test registration) is honestly
    symbol/level=None, matching parse_region's own None for that label."""
    from autofit.coverage import parse_region
    for e in index:
        parsed = parse_region(e["region"])
        if parsed is None:
            assert e["symbol"] is None and e["level"] is None, e
        else:
            assert parsed == (e["symbol"], e["level"])


def test_the_five_existing_curated_regions_unchanged(index):
    """Do not change the existing five elements' behavior (goal rail):
    every currently-registered region module shows tier='curated'. A
    SUBSET check (not equality) against registered_regions(): other test
    modules sharing this process may register their OWN synthetic region
    (e.g. test_resolver.py's module-level `register_region(_FakeRegion())`
    for 'Fk 2p') — real in the shared test process, out of this unit's
    scope, and correctly still surfaced as 'curated' (see the defensive-
    completeness fallback in region_coverage_index)."""
    curated_regions = {e["region"] for e in index if e["tier"] == "curated"}
    assert {"B 1s", "C 1s", "Cl 2p", "N 1s", "U 4f"} <= curated_regions
    assert set(registered_regions()) <= curated_regions


def test_curated_regions_have_a_grammar_derived_roi(index):
    for e in index:
        if e["tier"] != "curated":
            continue
        assert e["roi"] is not None, e["region"]
        assert e["roi"]["be_min"] < e["roi"]["be_max"]
        assert "grammar" in e["roi"]["basis"]


def test_structure_only_never_carries_a_roi_or_a_curated_label(index):
    """HONESTY rail: a region with nothing sourced must show tier=
    'structure_only' with roi=None — never dressed up as curated or
    handed a fabricated window."""
    for e in index:
        if e["tier"] == "structure_only":
            assert e["roi"] is None, e["region"]
            assert e["region"] not in set(registered_regions())


def test_machine_tier_never_shown_as_curated(index):
    """The core honesty rail: a structural-fallback region with a
    SOURCED position (even a data/xps 'curated'-tier one) must still be
    labeled 'machine' here, never 'curated' — that label is reserved for
    a registered deep grammar module."""
    curated_modules = set(registered_regions())
    for e in index:
        if e["tier"] == "machine":
            assert e["region"] not in curated_modules


def test_fe_2p_is_a_plausible_machine_tier_entry(index):
    """Fe 2p: no deep grammar module, but data/xps carries a machine-tier
    2p3/2 reference position (measured in the Stage-2 session) — the
    canonical 'across-the-periodic-table' example from the goal. Asserted
    as an exact 'machine' pin (not `in ("machine", "structure_only")`) —
    a regression that silently dropped Fe 2p's sourced position must FAIL
    this test, per a 2026-07-11 Codex review finding."""
    fe2p = next((e for e in index if e["region"] == "Fe 2p"), None)
    assert fe2p is not None, "Fe 2p must be enumerated (Z=26, occupied 2p)"
    assert fe2p["tier"] == "machine"
    assert fe2p["roi"] is not None
    assert fe2p["roi"]["be_min"] < fe2p["roi"]["be_max"]


def test_a_genuinely_uncovered_region_is_structure_only(index):
    """Some element/level combos have NOTHING in data/xps at all (most
    of the periodic table, per the coverage sweep's own honest
    accounting) — those must land in structure_only with no invented
    position."""
    structure_only = [e for e in index if e["tier"] == "structure_only"]
    assert structure_only, "expected at least one genuinely bare region"
    for e in structure_only:
        assert e["roi"] is None


def test_index_is_cached_and_returns_independent_copies(index):
    from autofit.coverage_index import region_coverage_index as f
    a = f()
    b = f()
    assert a == b
    a[0]["tier"] = "MUTATED"
    c = f()
    assert c[0]["tier"] != "MUTATED"    # caller can't corrupt the cache


def test_cached_copies_are_deep_not_shallow(index):
    """Regression (2026-07-11 Codex review, unit 3 round 1 NO-GO): a
    shallow `dict(e)` per entry left the nested `roi` sub-dict SHARED with
    the cache, so mutating a returned entry's roi corrupted every future
    caller's (including /api/analyze/meta's) result. Must be a true deep
    copy — pick an entry that actually HAS a roi (curated ones always do)."""
    from autofit.coverage_index import region_coverage_index as f
    a = f()
    entry_with_roi = next(e for e in a if e["roi"] is not None)
    original_be_min = entry_with_roi["roi"]["be_min"]
    entry_with_roi["roi"]["be_min"] = -99999.0
    b = f()
    same_entry = next(e for e in b if e["region"] == entry_with_roi["region"])
    assert same_entry["roi"]["be_min"] == original_be_min


def test_every_entry_has_a_human_note(index):
    for e in index:
        assert isinstance(e["note"], str) and e["note"]
