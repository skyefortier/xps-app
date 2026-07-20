"""Unit A (2026-07-20): decouples two meanings that ``fwhm_range``'s upper
bound used to carry at once:

  1. the optimizer's own search bound ("the width parameter may search up
     to here");
  2. a semantic claim consumed by quality reporting ("this region module
     VOUCHES that a component this wide is legitimate physics, not an
     optimizer papering over a missed feature").

``autofit/engine.py``'s ``_unphysical_width_flags`` used to infer (2) from
(1) via a bare numeric test (``declared_hi > FWHM_MAX_ORDINARY_EV``). The
MIXED material-class unit (77bf3a8) relaxed (1) for C 1s contamination
slots to make room for differential-charging broadening, and thereby
silently asserted (2) as a side effect -- exactly backwards, since MIXED's
entire premise is that we do NOT know how broad differential charging
makes the peak, the opposite of vouching for it. Both Codex reviews of
77bf3a8 independently caught this (see docs/autofit/codex/
mixed_material_class_verdict_run{A,B}.md).

The fix: ``ComponentSlot.broad_justification`` makes meaning (2) an
explicit, independent field. ``_unphysical_width_flags`` keys its
exemption off ``broad_justification is not None``, never off the bound's
magnitude. This file is the safety net for that refactor: it encodes, as
an explicit and auditable fixture, EXACTLY which slots are exempt today
(under the old numeric rule) so the same set stays exempt under the new
field-based rule -- pure refactor, behavior-neutral, proven rather than
asserted.
"""
from __future__ import annotations

import pytest

from autofit.engine import FittedComponent, _unphysical_width_flags
from autofit.grammar import LineShape, MaterialClass, Phase, resolve

# ── Ground truth: which slots are grammar-sanctioned-broad TODAY ───────────
# (declared_hi > FWHM_MAX_ORDINARY_EV == 2.0 eV, the pre-refactor rule),
# derived by reading every region module's build_candidates(). Each entry
# names the region, the exact CandidateModel to fetch it from, and the
# slot role. This is the fixture the refactor must reproduce exactly.

_CONDUCTOR_C1S = Phase(id="s", material_class=MaterialClass.CONDUCTOR,
                       regions=("C 1s",))
_INSULATOR_B1S = Phase(id="s", material_class=MaterialClass.INSULATOR,
                       regions=("B 1s",))
_INSULATOR_CL2P = Phase(id="s", material_class=MaterialClass.INSULATOR,
                        regions=("Cl 2p",))
_INSULATOR_N1S = Phase(id="s", material_class=MaterialClass.INSULATOR,
                       regions=("N 1s",))
_INSULATOR_U4F = Phase(id="s", material_class=MaterialClass.INSULATOR,
                       regions=("U 4f",))


def _slot(phase, region, candidate_name, role):
    g = resolve([phase], region)
    cand = next(c for c in g.candidates if c.name == candidate_name)
    slot = cand.slot_by_role(role)
    assert slot is not None, f"{candidate_name}/{role} not found"
    return slot


# (phase, region, candidate_name, role, currently_exempt)
EXEMPTION_FIXTURE = [
    # C 1s: only the pi->pi* satellite is exempt (declared 1.0-5.5).
    (_CONDUCTOR_C1S, "C 1s", "A0_graphite_asym_satellite", "satellite_pi", True),
    (_CONDUCTOR_C1S, "C 1s", "A0_graphite_asym_satellite", "main_graphitic", False),
    (_CONDUCTOR_C1S, "C 1s", "B2_linked", "main_aliphatic", False),
    (_CONDUCTOR_C1S, "C 1s", "A1_linked", "contamination_CO", False),
    # B 1s: all three mains share B1S_FWHM_RANGE (1.2-2.5) -- all exempt.
    (_INSULATOR_B1S, "B 1s", "B1_low", "main_b_low", True),
    (_INSULATOR_B1S, "B 1s", "B2_low_mid", "main_b_mid", True),
    (_INSULATOR_B1S, "B 1s", "B2b_low_oxide", "main_b_oxide", True),
    # Cl 2p: both p32 (shared-width family) and p12 exempt at CL2P_FWHM_RANGE
    # (1.2-2.2) / CL2P_12_FWHM_RANGE (free-width family, up to 3.0).
    (_INSULATOR_CL2P, "Cl 2p", "Cl0_doublet", "main_cl2p32", True),
    (_INSULATOR_CL2P, "Cl 2p", "Cl0_doublet", "main_cl2p12", True),
    (_INSULATOR_CL2P, "Cl 2p", "Cl0w_doublet_freewidth", "main_cl2p12", True),
    # N 1s: main_n1s exempt at N1S_FWHM_RANGE (0.7-2.5) in both shape variants.
    (_INSULATOR_N1S, "N 1s", "N0_pv", "main_n1s", True),
    (_INSULATOR_N1S, "N 1s", "N0_asymGL", "main_n1s", True),
    # U 4f: mains (1.5-3.5) and satellites (1.5-4.5) both exempt, incl.
    # the pair-linked / free-separation / independent satellite variants
    # (Codex-caught gap, round 1 of this refactor's own review: the
    # original fixture only covered U0_mains, not U1/U1b/U2's satellites).
    (_INSULATOR_U4F, "U 4f", "U0_mains", "main_u4f72", True),
    (_INSULATOR_U4F, "U 4f", "U0_mains", "main_u4f52", True),
    (_INSULATOR_U4F, "U 4f", "U1_mains_satpair", "satellite_u4f72", True),
    (_INSULATOR_U4F, "U 4f", "U1_mains_satpair", "satellite_u4f52", True),
    (_INSULATOR_U4F, "U 4f", "U1b_mains_satpair_freesep", "satellite_u4f52", True),
    (_INSULATOR_U4F, "U 4f", "U2_mains_satfree", "satellite_u4f72", True),
    (_INSULATOR_U4F, "U 4f", "U2_mains_satfree", "satellite_u4f52", True),
]

# ── Composed (multi-region joint co-fit) coverage ──────────────────────────
# The actual bug this section guards against (Codex-caught, round 1 of this
# refactor's own review): resolve() with >1 region composes candidates via
# autofit.grammar._retag_slot, which used to reconstruct each ComponentSlot
# by manually re-listing every field -- broad_justification wasn't in that
# list, so EVERY composed candidate silently lost EVERY exemption. Fixed by
# switching _retag_slot to dataclasses.replace(). This fixture exercises the
# exact U 4f + N 1s co-fit scenario both Codex reviews used to demonstrate
# the bug (this lab's real UCl4-in-BN samples).

_U4F_PHASE = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
                   regions=("U 4f",))
_N1S_PHASE = Phase(id="BN", material_class=MaterialClass.INSULATOR,
                   regions=("N 1s",))

# (candidate_name, role, currently_exempt) -- resolved via [_U4F_PHASE, _N1S_PHASE]
COMPOSED_EXEMPTION_FIXTURE = [
    ("U0_mains+N0_pv", "U4f__main_u4f72", True),
    ("U0_mains+N0_pv", "U4f__main_u4f52", True),
    ("U0_mains+N0_pv", "N1s__main_n1s", True),
    ("U1_mains_satpair+N0_pv", "U4f__satellite_u4f72", True),
    ("U1_mains_satpair+N0_pv", "U4f__satellite_u4f52", True),
    ("U1b_mains_satpair_freesep+N0_asymGL", "U4f__satellite_u4f52", True),
    ("U2_mains_satfree+N0_asymGL", "U4f__satellite_u4f72", True),
]


def _composed_slot(candidate_name, role):
    g = resolve([_U4F_PHASE, _N1S_PHASE], ["U 4f", "N 1s"])
    cand = next(c for c in g.candidates if c.name == candidate_name)
    slot = cand.slot_by_role(role)
    assert slot is not None, f"{candidate_name}/{role} not found"
    return slot


@pytest.mark.parametrize("candidate_name,role,exempt", COMPOSED_EXEMPTION_FIXTURE)
def test_composed_candidate_preserves_broad_justification(
        candidate_name, role, exempt):
    """The exact regression: a slot that is grammar-sanctioned-broad in its
    OWN region module must stay that way after _retag_slot composes it into
    a multi-region joint-fit candidate."""
    slot = _composed_slot(candidate_name, role)
    if exempt:
        assert slot.broad_justification is not None, (
            f"{candidate_name}/{role} lost its broad_justification during "
            "multi-region composition (_retag_slot regression)"
        )
    else:
        assert slot.broad_justification is None


def test_retag_slot_preserves_all_fields_except_the_three_rewritten():
    """Structural guard against this bug class recurring: _retag_slot must
    carry every ComponentSlot field forward unchanged except role/
    linked_to/fwhm_linked_to (deliberately rewritten for region-prefixing).
    Driven off dataclasses.fields(ComponentSlot) rather than a hardcoded
    list, so this test automatically covers any field added to
    ComponentSlot later -- a class-level guard, not another point fix."""
    import dataclasses

    from autofit.grammar import ComponentSlot, _retag_slot

    rewritten = {"role", "linked_to", "fwhm_linked_to"}

    sentinel_by_field = {
        "role": "orig_role",
        "region": "orig_region",
        "phase_id": "orig_phase",
        "be_window": (100.0, 200.0),
        "line_shape": LineShape.PSEUDO_VOIGT,
        "fwhm_range": (0.5, 9.99),
        "linked_to": "orig_role",
        "linked_offset_range": (1.0, 2.0),
        "area_ratio": 0.123456,
        "area_ratio_range": (0.1, 0.9),
        "fixed_params": (("beta", 0.05),),
        "param_ranges": (("alpha", (0.0, 0.3)),),
        "fwhm_linked_to": None,
        "fwhm_excess_range": (0.0, 0.8),
        "share_parent_params": ("alpha", "beta"),
        "broad_justification": "sentinel justification text",
    }
    field_names = {f.name for f in dataclasses.fields(ComponentSlot)}
    missing = field_names - set(sentinel_by_field)
    assert not missing, (
        f"ComponentSlot gained new field(s) {missing} this test doesn't "
        "sentinel-fill -- add a case above so the guard covers it"
    )

    original = ComponentSlot(**sentinel_by_field)
    rename = {"orig_role": "PhaseX__orig_role"}
    retagged = _retag_slot(original, rename, shared_rename={})

    for name in field_names:
        if name in rewritten:
            continue
        assert getattr(retagged, name) == getattr(original, name), (
            f"_retag_slot lost field {name!r}: "
            f"{getattr(original, name)!r} -> {getattr(retagged, name)!r}"
        )
    assert retagged.role == "PhaseX__orig_role"
    assert retagged.linked_to == "PhaseX__orig_role"


@pytest.mark.parametrize("phase,region,candidate_name,role,exempt",
                         EXEMPTION_FIXTURE)
def test_exemption_fixture_matches_broad_justification(
        phase, region, candidate_name, role, exempt):
    """Each currently-exempt slot must carry a real broad_justification;
    each currently-non-exempt slot must not. This IS the byte-identical
    proof requested: the exemption SET, read directly off the grammar,
    matches the pre-refactor numeric rule exactly."""
    slot = _slot(phase, region, candidate_name, role)
    if exempt:
        assert slot.broad_justification is not None, (
            f"{region}/{candidate_name}/{role} was grammar-sanctioned-broad "
            f"under the old numeric rule (fwhm_range={slot.fwhm_range}) but "
            "lost its exemption in the refactor"
        )
        assert slot.fwhm_range[1] > 2.0, (
            "fixture sanity: this entry's OWN historical exemption basis "
            "was declared_hi > 2.0 -- if this fails, the fixture itself is "
            "wrong, not the code"
        )
    else:
        assert slot.broad_justification is None, (
            f"{region}/{candidate_name}/{role} was NOT grammar-sanctioned-"
            f"broad under the old numeric rule (fwhm_range={slot.fwhm_range}) "
            "but gained an unjustified exemption in the refactor"
        )


def _fitted(role, fwhm, line_shape=LineShape.PSEUDO_VOIGT, **shape_params):
    return FittedComponent(slot_role=role, position=0.0, fwhm=fwhm,
                           amplitude=1.0, shape_params=shape_params,
                           line_shape=line_shape)


class _FakeModel:
    """Minimal stand-in for CandidateModel -- _unphysical_width_flags only
    reads .slots."""
    def __init__(self, slots):
        self.slots = slots


@pytest.mark.parametrize("phase,region,candidate_name,role,exempt",
                         EXEMPTION_FIXTURE)
def test_flag_behavior_matches_pre_refactor_rule_at_the_ceiling(
        phase, region, candidate_name, role, exempt):
    """The actual OUTPUT of _unphysical_width_flags for a component fitted
    right at its slot's declared ceiling must match what the pre-refactor
    numeric rule would have produced: no flag for an exempt slot even
    though it pegs a wide ceiling; a flag for a non-exempt slot pegging
    the ordinary 2.0 eV cap."""
    slot = _slot(phase, region, candidate_name, role)
    g = resolve([phase], region)
    cand = next(c for c in g.candidates if c.name == candidate_name)
    fwhm_at_ceiling = slot.fwhm_range[1] if exempt else 2.0
    comp = _fitted(role, fwhm_at_ceiling, line_shape=slot.line_shape)
    flags = _unphysical_width_flags([comp], cand)
    if exempt:
        assert not flags, (
            f"{region}/{candidate_name}/{role}: exempt slot got flagged "
            f"at its own ceiling -- {flags}"
        )
    else:
        assert flags, (
            f"{region}/{candidate_name}/{role}: non-exempt slot pegging "
            "the ordinary 2.0 eV cap should be flagged"
        )


# ── The actual bug fix, tested generically at the engine level ────────────

def test_wide_declared_range_without_justification_is_no_longer_exempt():
    """THE FIX, encoded directly: a slot with a wide fwhm_range (would have
    been auto-exempt under the old numeric rule) but broad_justification
    left None must now be flagged when fitted well above the ordinary
    2.0 eV cap -- this is the MIXED contamination scenario, tested here
    independent of MIXED or C 1s at all."""
    from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot

    wide_no_justification = ComponentSlot(
        role="wide_slot", region="Test", phase_id="s",
        be_window=(280.0, 295.0), line_shape=LineShape.PSEUDO_VOIGT,
        fwhm_range=(0.8, 15.0), broad_justification=None,
    )
    model = CandidateModel(name="synthetic", background=BackgroundType.SHIRLEY,
                           slots=(wide_no_justification,))
    comp = _fitted("wide_slot", 8.0)   # well above 2.0, well below 15.0
    flags = _unphysical_width_flags([comp], model)
    assert flags, (
        "a slot with a wide bound but NO broad_justification must still "
        "be flagged when it fits wide -- the bound alone must never grant "
        "exemption"
    )


def test_narrow_declared_range_with_justification_is_exempt():
    """Mirror case: an explicit broad_justification grants exemption even
    for a slot whose declared ceiling never exceeded the ordinary cap --
    proving exemption is governed by the field, not a numeric side effect
    of the bound's magnitude."""
    from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot

    narrow_but_justified = ComponentSlot(
        role="narrow_slot", region="Test", phase_id="s",
        be_window=(280.0, 295.0), line_shape=LineShape.PSEUDO_VOIGT,
        fwhm_range=(0.5, 2.0), broad_justification="synthetic test justification",
    )
    model = CandidateModel(name="synthetic", background=BackgroundType.SHIRLEY,
                           slots=(narrow_but_justified,))
    comp = _fitted("narrow_slot", 2.0)   # pegs its own (narrow) ceiling
    flags = _unphysical_width_flags([comp], model)
    assert not flags, (
        "an explicit broad_justification must exempt a slot even when its "
        "declared ceiling never exceeded the ordinary cap"
    )


def test_component_slot_broad_justification_defaults_to_none():
    from autofit.grammar import ComponentSlot

    s = ComponentSlot(role="r", region="Test", phase_id="s",
                      be_window=(0.0, 1.0), line_shape=LineShape.PSEUDO_VOIGT,
                      fwhm_range=(0.5, 1.0))
    assert s.broad_justification is None
