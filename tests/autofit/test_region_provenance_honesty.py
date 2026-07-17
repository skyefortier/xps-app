"""Provenance-audit fixes (2026-07-16), Units 4-5: two region modules'
``provenance()`` outputs conflated a literature-derived bound with a
lab-derived bound under one status tag (Unit 4), and two constants used
in ``build_candidates`` had real disclosure in code comments that never
made it into the structured ``provenance()`` list the UI reads (Unit 5).

No existing test exercised ``C1sModule.provenance()`` or
``U4fModule.provenance()`` directly before this file.
"""
from __future__ import annotations

from autofit.regions.c1s import (
    C1sModule, FWHM_RANGE_AROMATIC_POLYMER, FWHM_RANGE_CONTAMINATION,
)
from autofit.regions.u4f import U4fModule, U4F_SAT_OFFSET_RANGE


def _by_constant(records, name):
    hits = [r for r in records if r["constant"] == name]
    assert len(hits) == 1, f"expected exactly one {name!r} record, got {len(hits)}"
    return hits[0]


def test_c1s_fwhm_contamination_floor_and_ceiling_are_separate_records():
    """Unit 4: the floor (0.8 eV) is Biesinger 2022 / Greczynski & Hultman
    2020 (published) while the ceiling (2.0 eV) is an explicit lab
    adjudication (2026-07-03, docs/autofit/adjudication-decisions.md #5)
    -- two different sources with two different confidence levels,
    previously merged under one CONDITIONAL tag that read as "fully
    literature" when only the floor is."""
    records = C1sModule().provenance()
    names = {r["constant"] for r in records}
    assert "fwhm_contamination_ev" not in names, (
        "the old combined record should be split, not merely relabeled")

    floor = _by_constant(records, "fwhm_contamination_floor_ev")
    assert floor["value"] == FWHM_RANGE_CONTAMINATION[0] == 0.8
    assert floor["status"] == "CONDITIONAL"
    assert "biesinger" in floor["source"].lower()
    assert "greczynski" in floor["source"].lower()
    assert "adjudicat" not in floor["source"].lower(), (
        "the floor's source must be purely literature, no lab-adjudication text")

    ceiling = _by_constant(records, "fwhm_contamination_ceiling_ev")
    assert ceiling["value"] == FWHM_RANGE_CONTAMINATION[1] == 2.0
    assert ceiling["status"] == "UNVERIFIED"
    assert "2026-07-03" in ceiling["source"]
    assert "adjudicat" in ceiling["source"].lower()
    assert "biesinger" not in ceiling["source"].lower(), (
        "the ceiling's source must be purely the lab decision, no literature citation")


def test_c1s_aromatic_polymer_fwhm_has_provenance_entry():
    """Unit 5: FWHM_RANGE_AROMATIC_POLYMER has a real citation in its code
    comment (Beamson & Briggs, Wiley 1992: 0.9-1.5 eV, widened to
    0.8-1.8) that never reached provenance(). Add it as CONDITIONAL,
    citing Beamson & Briggs, noting the widening beyond the cited range
    is editorial."""
    records = C1sModule().provenance()
    rec = _by_constant(records, "aromatic_polymer_fwhm_ev")
    assert rec["value"] == list(FWHM_RANGE_AROMATIC_POLYMER) == [0.8, 1.8]
    assert rec["status"] == "CONDITIONAL"
    assert "beamson" in rec["source"].lower()
    assert "0.9" in rec["source"] and "1.5" in rec["source"], (
        "the cited literature range (0.9-1.5) must be stated, distinct "
        "from the wider stored bound (0.8-1.8)"
    )


def test_c1s_aliphatic_linked_offset_range_has_provenance_entry():
    """Unit 5: the MG-family aliphatic linked-offset window (0.2, 0.6) is
    labeled UNVERIFIED-empirical in its code comment ("labeled-set +
    convention") but was absent from provenance(). Add it as UNVERIFIED."""
    records = C1sModule().provenance()
    rec = _by_constant(records, "aliphatic_linked_offset_range_ev")
    assert rec["value"] == [0.2, 0.6]
    assert rec["status"] == "UNVERIFIED"


def test_u4f_satellite_offset_source_distinguishes_literature_from_labeled_set():
    """Unit 4: the stored envelope (5.5, 8.5) BRACKETS two genuinely
    different sources -- literature U(IV) satellite-to-main separation
    6.8-7.1 eV (Ilton & Bagus 2011; Schindler 2009) and this lab's own
    labeled-set fitted separations 6.07-6.38 eV -- previously blended
    into one CONDITIONAL source string with no indication of which
    number came from which source. Neither endpoint of the stored range
    equals either cited sub-range directly (both are further widened for
    safety margin), so this is fixed by making the source string
    explicit about the two distinct sources and their sub-ranges, not by
    splitting into two records (there is only one true fitting bound
    here, not two independently-sourceable numbers like C1s's floor/
    ceiling)."""
    records = U4fModule().provenance()
    rec = _by_constant(records, "satellite_offset_ev")
    assert rec["value"] == list(U4F_SAT_OFFSET_RANGE)
    assert rec["status"] == "CONDITIONAL"
    src = rec["source"].lower()
    assert "6.8" in rec["source"] and "7.1" in rec["source"], (
        "the literature sub-range must be stated")
    assert "6.07" in rec["source"] and "6.38" in rec["source"], (
        "the labeled-set sub-range must be stated")
    assert "ilton" in src or "bagus" in src, "literature citation must be named"
    assert "labeled" in src or "lab" in src, (
        "the labeled-set sub-range must be attributed to the lab, not "
        "left unattributed alongside the literature citation")
