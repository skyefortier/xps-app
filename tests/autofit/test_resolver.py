"""Resolver + grammar unit tests (spec v2.1 §2 preconditions)."""

import pytest

from autofit.grammar import (
    BackgroundType,
    CandidateModel,
    ComponentSlot,
    LineShape,
    MaterialClass,
    Phase,
    PhaseAmbiguityError,
    UnknownRegionError,
    resolve,
)
from autofit.regions import get_region_module, register_region, registered_regions

GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
                 regions=("C 1s",), material="graphite")
B4C = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
            regions=("B 1s", "C 1s"))
BN = Phase(id="BN", material_class=MaterialClass.INSULATOR,
           regions=("B 1s", "N 1s"))


def test_c1s_registered():
    assert "C 1s" in registered_regions()


def test_single_phase_resolves():
    g = resolve([GRAPHITE], "C 1s")
    assert g.regions == ("C 1s",)
    assert g.phase_ids == ("graphite",)
    assert len(g.candidates) >= 20
    names = {c.name for c in g.candidates}
    # families present: DS+G asymmetric, expert-parity asym-GL, mixed, symmetric
    assert "A1_linked" in names
    assert "AG1_linked" in names
    assert "M0_graph_asym_aliph_sym_satellite" in names
    assert "B2_linked" in names
    # every slot tagged with phase + region
    for c in g.candidates:
        for s in c.slots:
            assert s.phase_id == "graphite"
            assert s.region == "C 1s"
    assert g.diagnostic_windows  # region-prefixed labels
    assert all(k.startswith("C 1s:") for k in g.diagnostic_windows)


def test_admissibility_satellite_needs_asymmetric_main():
    g = resolve([GRAPHITE], "C 1s")
    for c in g.candidates:
        roles = {s.role for s in c.slots}
        if "satellite_pi" in roles:
            main = c.slot_by_role("main_graphitic")
            assert main is not None
            assert main.line_shape in (LineShape.DS_G, LineShape.ASYM_GL), c.name


def test_dsg_main_has_fixed_core_hole_beta():
    g = resolve([GRAPHITE], "C 1s")
    a1 = next(c for c in g.candidates if c.name == "A1_linked")
    main = a1.slot_by_role("main_graphitic")
    assert dict(main.fixed_params)["beta"] == pytest.approx(0.05)
    assert dict(main.param_ranges)["alpha"] == (0.0, 0.3)


def test_phase_ambiguity_requires_target():
    with pytest.raises(PhaseAmbiguityError):
        resolve([GRAPHITE, B4C], "C 1s")
    # disambiguated by target_phases → resolves to the named phase
    g = resolve([GRAPHITE, B4C], "C 1s", target_phases={"C 1s": "graphite"})
    assert g.phase_ids == ("graphite",)
    with pytest.raises(PhaseAmbiguityError):
        # target names a non-contributor
        resolve([GRAPHITE, B4C], "C 1s", target_phases={"C 1s": "BN"})


def test_unknown_or_uncovered_region():
    with pytest.raises(UnknownRegionError):
        resolve([GRAPHITE], "Xe 3d")           # no phase contributes it
    with pytest.raises(UnknownRegionError):
        # phase claims it but no module registered
        xe = Phase(id="x", material_class=MaterialClass.CONDUCTOR, regions=("Xe 3d",))
        resolve([xe], "Xe 3d")


def test_duplicate_phase_ids_rejected():
    with pytest.raises(ValueError, match="duplicate phase ids"):
        resolve([GRAPHITE, GRAPHITE], "C 1s")


def test_oxidation_state_seam():
    with pytest.raises(KeyError):
        resolve([GRAPHITE], "C 1s", oxidation_state="C(IV)")


# ── joint co-fit composition, using a minimal synthetic second region ──────

class _FakeRegion:
    region = "Fk 2p"

    def diagnostic_windows(self):
        return {"main": (100.0, 105.0)}

    def build_candidates(self, phase, oxidation_state=None):
        main = ComponentSlot(
            role="main_fk", region=self.region, phase_id=phase.id,
            be_window=(100.0, 105.0), line_shape=LineShape.PSEUDO_VOIGT,
            fwhm_range=(0.5, 2.0),
        )
        doublet = ComponentSlot(
            role="main_fk_p12", region=self.region, phase_id=phase.id,
            be_window=(101.0, 107.0), line_shape=LineShape.PSEUDO_VOIGT,
            fwhm_range=(0.5, 2.0),
            linked_to="main_fk", linked_offset_range=(1.5, 1.7),
            area_ratio=0.5,
        )
        return [
            CandidateModel(name="FK1", background=BackgroundType.SHIRLEY,
                           slots=(main,)),
            CandidateModel(name="FK2", background=BackgroundType.SHIRLEY,
                           slots=(main, doublet)),
        ]


register_region(_FakeRegion())


def test_joint_composition():
    both = Phase(id="mix", material_class=MaterialClass.CONDUCTOR,
                 regions=("C 1s", "Fk 2p"), material="graphite")
    g = resolve([both], ["C 1s", "Fk 2p"])
    n_c1s = len(resolve([both], "C 1s").candidates)
    assert len(g.candidates) == n_c1s * 2
    joint = next(c for c in g.candidates if c.name.endswith("+FK2"))
    roles = [s.role for s in joint.slots]
    # region-slug prefixes keep roles unique; linkage rewritten
    assert "C1s__main_graphitic" in roles
    assert "Fk2p__main_fk" in roles and "Fk2p__main_fk_p12" in roles
    doublet = joint.slot_by_role("Fk2p__main_fk_p12")
    assert doublet.linked_to == "Fk2p__main_fk"
    assert doublet.area_ratio == 0.5
    sat = joint.slot_by_role("C1s__satellite_pi")
    if sat is not None:
        assert sat.linked_to == "C1s__main_graphitic"
    # shared fwhm params rewritten and fwhm_linked_to follows
    linked_cand = next(c for c in g.candidates if c.name.startswith("A1_linked+"))
    shared_names = [n for n, _, _ in linked_cand.shared_fwhm_params]
    assert shared_names == ["C1s__shared_contamination_fwhm"]
    co = linked_cand.slot_by_role("C1s__contamination_CO")
    assert co.fwhm_linked_to == "C1s__shared_contamination_fwhm"


def test_same_region_from_two_phases_cofits():
    """Codex Stage-2 blocker #1: a BN/B4C-style sample must be able to co-fit
    BOTH phases' contributions of the same region in one window."""
    p1 = Phase(id="ph1", material_class=MaterialClass.INSULATOR, regions=("Fk 2p",))
    p2 = Phase(id="ph2", material_class=MaterialClass.SEMICONDUCTOR, regions=("Fk 2p",))
    g = resolve([p1, p2], [("Fk 2p", "ph1"), ("Fk 2p", "ph2")])
    # 2 candidates per phase → 4 joint candidates
    assert len(g.candidates) == 4
    assert set(g.phase_ids) == {"ph1", "ph2"}
    joint = next(c for c in g.candidates if c.name == "FK2+FK2")
    phase_by_role = {s.role: s.phase_id for s in joint.slots}
    # roles are phase-qualified and each phase's slots keep THEIR phase_id
    ph1_roles = [r for r, p in phase_by_role.items() if p == "ph1"]
    ph2_roles = [r for r, p in phase_by_role.items() if p == "ph2"]
    assert len(ph1_roles) == 2 and len(ph2_roles) == 2
    assert set(ph1_roles).isdisjoint(ph2_roles)
    # linkage stays within the owning phase
    for c in g.candidates:
        for s in c.slots:
            if s.linked_to is not None:
                parent = c.slot_by_role(s.linked_to)
                assert parent is not None and parent.phase_id == s.phase_id
    # phase-qualified diagnostic windows
    assert any("@ph1:" in k for k in g.diagnostic_windows)
    assert any("@ph2:" in k for k in g.diagnostic_windows)


def test_same_region_duplicate_request_rejected():
    p1 = Phase(id="ph1", material_class=MaterialClass.INSULATOR, regions=("Fk 2p",))
    with pytest.raises(ValueError, match="duplicate region request"):
        resolve([p1], [("Fk 2p", "ph1"), ("Fk 2p", "ph1")])
    with pytest.raises(ValueError, match="does not contribute"):
        resolve([p1], [("Fk 2p", "nope")])
