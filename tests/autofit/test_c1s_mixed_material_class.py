"""MIXED material class (2026-07-20 unit): analyte-in-matrix samples can
show DIFFERENTIAL CHARGING between phases -- the sample charges
non-uniformly under X-ray illumination, so a distribution of local surface
potentials broadens observed peaks (inhomogeneous broadening). That
broadening voids the single-species-homogeneity assumption behind the C 1s
adventitious/contamination FWHM ceiling, so MIXED relaxes it.

The provenance-audit trap this unit must NOT fall into: asserting a new
numeric position/width value derived from this lab's own spectra (e.g.
"MIXED widens the cap to 3.5 eV because that's what our UCl4-in-graphite
samples do") would reintroduce exactly the self-reference the provenance
audit removed -- wearing a feature label instead of a tier badge.
Withdrawing an assumption needs no citation; asserting a new numeric
window does, and this feature has none. So MIXED only RELAXES an existing
constraint (widens toward the engine's own pre-existing numeric-stability
ceiling) -- it never asserts a new position or width VALUE.

Citations for the physical rationale (see also C1sModule.provenance()):
Baer, Artyushkova, Cohen, Easton, Engelhard, Gengenbach, Greczynski, Mack,
Morgan, Roberts, "XPS Guide: Charge neutralization and binding energy
referencing for insulating samples," J. Vac. Sci. Technol. A 38, 031204
(2020), DOI 10.1116/6.0000057 -- differential charging broadens peaks
(examining the leading edge across analysis points/time "identif[ies]
peak broadening as a result of differential charging"), and a single
charge correction is insufficient once differential charging is present:
internal referencing has "limited accuracy... often including multiphase
and other complex samples." Greczynski & Hultman, "X-ray photoelectron
spectroscopy: Towards reliable binding energy referencing," Prog. Mater.
Sci. 107 (2020) 100591, DOI 10.1016/j.pmatsci.2019.100591 (referencing
reliability, general).
"""
from __future__ import annotations

import pytest

from autofit.grammar import MaterialClass, Phase, resolve
from autofit.regions.c1s import C1sModule, FWHM_RANGE_CONTAMINATION

NON_MIXED = [MaterialClass.CONDUCTOR, MaterialClass.SEMICONDUCTOR,
             MaterialClass.INSULATOR]


def _by_constant(records, name):
    hits = [r for r in records if r["constant"] == name]
    assert len(hits) == 1, f"expected exactly one {name!r} record, got {len(hits)}"
    return hits[0]


def _resolve(material_class):
    phase = Phase(id="sample", material_class=material_class, regions=("C 1s",))
    return resolve([phase], "C 1s")


def _contamination_slots(grammar):
    """Every slot governed by FWHM_RANGE_CONTAMINATION under the DEFAULT
    (non-MIXED) convention -- identified by its FLOOR, which MIXED never
    changes, so this selector is stable across material classes."""
    out = []
    for c in grammar.candidates:
        for s in c.slots:
            if s.fwhm_range[0] == FWHM_RANGE_CONTAMINATION[0]:
                out.append((c.name, s))
    return out


@pytest.mark.parametrize("material_class", NON_MIXED)
def test_non_mixed_candidate_pool_unchanged(material_class):
    """Non-regression, structural pin: conductor/semiconductor/insulator
    must build EXACTLY the pre-MIXED contamination fwhm_range -- byte
    (tuple) identical, not just close."""
    g = _resolve(material_class)
    slots = _contamination_slots(g)
    assert slots, "fixture assumption: at least one contamination-governed slot"
    for name, slot in slots:
        assert slot.fwhm_range == FWHM_RANGE_CONTAMINATION, (
            f"{name}/{slot.role}: fwhm_range changed for non-MIXED "
            f"material_class {material_class}"
        )


@pytest.mark.parametrize("material_class", NON_MIXED)
def test_non_mixed_candidate_names_unchanged(material_class):
    """Non-regression at the coarsest level: the SET of candidate model
    names build_candidates() produces must be identical across every
    non-MIXED material class (it always was -- material_class was
    previously read nowhere in this module)."""
    names_conductor = {c.name for c in _resolve(MaterialClass.CONDUCTOR).candidates}
    names_other = {c.name for c in _resolve(material_class).candidates}
    assert names_conductor == names_other


def test_mixed_relaxes_contamination_fwhm_ceiling():
    """The one concrete, falsifiable claim: MIXED must actually widen the
    contamination FWHM ceiling in the generated candidates -- otherwise
    the feature is decorative. The FLOOR must NOT move: differential
    charging only broadens a peak, it never narrows one, so there is no
    physical basis to touch 0.8 eV."""
    slots = _contamination_slots(_resolve(MaterialClass.MIXED))
    assert slots, "fixture assumption: at least one contamination-governed slot"
    for name, slot in slots:
        assert slot.fwhm_range[0] == FWHM_RANGE_CONTAMINATION[0], (
            f"{name}/{slot.role}: MIXED changed the FLOOR -- no physical "
            "justification for narrowing under differential charging"
        )
        assert slot.fwhm_range[1] > FWHM_RANGE_CONTAMINATION[1], (
            f"{name}/{slot.role}: MIXED did not widen the ceiling -- decorative"
        )


def test_mixed_does_not_touch_position_windows_or_offsets():
    """The provenance-audit trap, enforced structurally: MIXED relaxes
    WIDTH only. Every BE window and every linked-offset (contaminant
    center position, expressed relative to the graphitic main) must be
    byte-identical to the conductor default -- tempting as it is to widen
    a position window to admit an uncited differential-charging shift,
    doing so would convert a known-unknown into a silently-permitted fit."""
    g_conductor = _resolve(MaterialClass.CONDUCTOR)
    g_mixed = _resolve(MaterialClass.MIXED)

    windows = lambda g: {(c.name, s.role): s.be_window
                         for c in g.candidates for s in c.slots}
    assert windows(g_conductor) == windows(g_mixed), (
        "MIXED must not alter any component's BE window"
    )

    offsets = lambda g: {(c.name, s.role): s.linked_offset_range
                         for c in g.candidates for s in c.slots}
    assert offsets(g_conductor) == offsets(g_mixed), (
        "MIXED must not alter any linked-offset (contaminant center) range"
    )


def test_mixed_does_not_touch_unrelated_fwhm_families():
    """Scope discipline: only the contamination/adventitious FWHM family
    relaxes. The graphitic main, aromatic-polymer main, and satellite FWHM
    ranges are untouched -- this unit's own instructions name the
    adventitious cap as the one clear, in-scope case."""
    g_conductor = _resolve(MaterialClass.CONDUCTOR)
    g_mixed = _resolve(MaterialClass.MIXED)

    def other_family_ranges(g):
        return {(c.name, s.role): s.fwhm_range
                for c in g.candidates for s in c.slots
                if s.fwhm_range[0] != FWHM_RANGE_CONTAMINATION[0]}

    assert other_family_ranges(g_conductor) == other_family_ranges(g_mixed)


def test_mixed_provenance_relaxation_record_asserts_no_new_value():
    """provenance() must document the relaxation itself: CONDITIONAL,
    citing the differential-charging literature, and its `value` must
    read as an ACTION (relax/remove a constraint) -- never a specific new
    BE or width number. This is the literal test of the provenance-audit
    design constraint: withdrawing an assumption needs no citation,
    asserting a new numeric window does, and this record must not smuggle
    one in under CONDITIONAL cover."""
    records = C1sModule().provenance()
    rec = _by_constant(records, "mixed_material_class_width_relaxation")
    assert rec["status"] == "CONDITIONAL"
    assert isinstance(rec["value"], str), (
        "the relaxation record's value must be a descriptive action, not "
        "a bare number that could read as a newly-asserted window"
    )
    assert "10.1116/6.0000057" in rec["source"], "Baer et al. 2020 DOI"
    assert "baer" in rec["source"].lower()
    assert "10.1016/j.pmatsci.2019.100591" in rec["source"], \
        "Greczynski & Hultman 2020 DOI"
    assert "greczynski" in rec["source"].lower()
    assert "hultman" in rec["source"].lower()


def test_mixed_provenance_numeric_guard_record_is_honestly_labeled():
    """The residual finite ceiling (unavoidable -- the optimizer needs a
    finite initial-value midpoint) must be labeled UNVERIFIED and
    described as a numeric guard for fit stability, not a chemistry or
    physics claim -- the same footing as dsg_alpha_cap's 'fitalg numeric
    guard' language."""
    records = C1sModule().provenance()
    rec = _by_constant(records, "mixed_fwhm_ceiling_numeric_guard")
    assert rec["status"] == "UNVERIFIED"
    assert "numeric guard" in rec["source"].lower()
    assert ("not a chemistry" in rec["source"].lower()
            or "not a physical" in rec["source"].lower()
            or "not a physics" in rec["source"].lower())
    # the guard's own value must equal whatever ceiling build_candidates()
    # actually uses under MIXED -- no drift between the doc and the code
    slots = _contamination_slots(_resolve(MaterialClass.MIXED))
    actual_ceiling = slots[0][1].fwhm_range[1]
    assert rec["value"] == actual_ceiling
