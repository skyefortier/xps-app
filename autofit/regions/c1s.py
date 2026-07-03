"""
C 1s region module — the Stage-2 parity anchor (spec §3.1).

Ported from fitalg's ``build_c1s_graphite_candidates`` (validated there on
HOPG-like graphite and PET), with two changes for main:

1. fitalg's asymmetric main used its then-``la_casaxps`` shape, which is
   TODAY's ``ds_g`` (DS core ⊗ Gaussian; β = Lorentzian HWHM in eV).  The
   port maps those slots to :attr:`LineShape.DS_G`, preserving the math —
   fixed β at the C 1s core-hole lifetime, α capped, ``m_gauss`` carrying
   the slot's fwhm_range.
2. an ``AG*`` family with an ``asym-GL`` graphitic main is added.  The
   expert reference fits in docs/autofit/test_data model graphitic carbon
   as asym-GL (+ GL contaminants/satellite); the engine must be able to
   EXPRESS the expert model for the parity gate.  asym-GL is an empirical
   asymmetric envelope (no lit-derived parameterization) — flagged
   UNVERIFIED-empirical below.

Citations for constants are inline; everything without a citation is an
UNVERIFIED tunable per spec §9.
"""

from __future__ import annotations

from typing import Optional

from ..grammar import (
    BackgroundType,
    CandidateModel,
    ComponentSlot,
    LineShape,
    Phase,
)
from . import register_region

REGION = "C 1s"

# Canonical BE windows (eV, corrected frame). Generous prototype widths —
# tighten against lab data during calibration (fitalg provenance).
C1S_WINDOWS: dict[str, tuple[float, float]] = {
    "graphitic":   (284.0, 284.8),   # sp² graphitic C-C
    "aliphatic":   (284.6, 285.4),   # adventitious C-C/C-H
    "CO":          (285.8, 286.8),   # C-O / C-OH
    "C=O":         (287.3, 288.3),
    "OC=O":        (288.5, 289.6),
    "shake_up_pi": (290.0, 292.0),   # π→π* shake-up
}

# FWHM priors (eV):
# graphitic main — ordered single species, may be narrow.
FWHM_RANGE_GRAPHITIC = (0.4, 1.2)
# aromatic-polymer main — Beamson & Briggs, "High Resolution XPS of Organic
# Polymers — The Scienta ESCA300 Database", Wiley (1992): aromatic C 1s
# 0.9–1.5 eV; (0.8, 1.8) is the generous cross-instrument envelope.
FWHM_RANGE_AROMATIC_POLYMER = (0.8, 1.8)
# π→π* satellite — intrinsically broad (multi-electron excitation).
FWHM_RANGE_SATELLITE = (1.0, 3.0)
# adventitious carbon (incl. aliphatic main): 0.8 eV floor per Biesinger,
# Appl. Surf. Sci. 597 (2022) 153681 and Greczynski & Hultman (2020);
# 1.6 eV ceiling per Biesinger's tighter-convention recommendation.
FWHM_RANGE_CONTAMINATION = (0.8, 1.6)

# DS+G Lorentzian HWHM fixed at the C 1s core-hole lifetime:
# Campbell & Papp, At. Data Nucl. Data Tables 77 (2001) 1–56
# (DOI 10.1006/adnd.2000.0848): Γ_K(C) ≈ 0.10 eV FWHM → 0.05 eV HWHM.
# VERIFIED (spec §9). Breaks the α/β/m_gauss broadening degeneracy.
DSG_LORENTZIAN_HWHM_C1S = 0.05

# Graphitic asymmetry-index cap ≤ 0.3 — UNVERIFIED numeric guard (fitalg;
# keeps the optimizer away from the α→0.5 singularity).
DSG_ALPHA_RANGE_GRAPHITIC = (0.0, 0.3)

# asym-GL graphitic parameter windows — UNVERIFIED-empirical: chosen to
# bracket the expert reference fits (asymmetry ≈ 0.10, glMix ≈ 0.08–0.5)
# rather than derived from literature. The AG family exists so the engine
# can express the analysts' asym-GL practice; treat its constants as
# calibration targets, not physics.
ASYMGL_ASYMMETRY_RANGE = (0.0, 0.5)

# Adventitious-carbon chemical shifts from the C-C/C-H reference — soft
# priors/windows per Biesinger (2022): C-O +1.5±0.3, C=O +3.0±0.3,
# O-C=O +4.0±0.4 (CONDITIONAL per spec §9 — convention, not universal).
CONTAM_OFFSETS = {"CO": (1.5, 0.3), "C=O": (3.0, 0.3), "OC=O": (4.0, 0.4)}

# π→π* satellite offset window from the graphitic main (fitalg; UNVERIFIED
# tunable).
SATELLITE_OFFSET_RANGE = (5.5, 7.0)

_MAIN_FWHM_BY_MATERIAL = {
    "graphite": FWHM_RANGE_GRAPHITIC,
    None: FWHM_RANGE_GRAPHITIC,          # default material for a conductor
    "polymer": FWHM_RANGE_AROMATIC_POLYMER,
}

_SHARED_CONTAM_FWHM = "shared_contamination_fwhm"


class C1sModule:
    region = REGION

    def diagnostic_windows(self) -> dict[str, tuple[float, float]]:
        return dict(C1S_WINDOWS)

    def build_candidates(
        self, phase: Phase, oxidation_state: Optional[str] = None
    ) -> list[CandidateModel]:
        """
        Model families (admissibility encoded structurally, fitalg §):

        - A0–A3:  DS+G asymmetric graphitic main + π→π* satellite
                  + 0–3 contaminants (absolute windows)
        - A1–A3_linked:         shared contamination FWHM (Biesinger 2022)
        - A1–A3_linked_offset:  + contaminant centers as bounded offsets
        - AG0–AG3_linked:       asym-GL graphitic main variants (expert-fit
                                parity family; UNVERIFIED-empirical shape)
        - M0–M3:  mixed graphitic (DS+G) + aliphatic (PV) two-main models
        - B2/B3 (+_linked):     symmetric adventitious-carbon models
        - shake-up satellite only with an asymmetric main (admissibility)

        ``oxidation_state`` is accepted for the Layer-C seam; C 1s defines
        no oxidation-state overrides.
        """
        if oxidation_state is not None:
            raise KeyError(
                f"C 1s defines no oxidation-state override {oxidation_state!r}"
            )
        pid = phase.id
        main_fwhm = _MAIN_FWHM_BY_MATERIAL.get(phase.material, FWHM_RANGE_GRAPHITIC)

        def slot(role, window, shape, fwhm_range, **kw) -> ComponentSlot:
            return ComponentSlot(
                role=role, region=REGION, phase_id=pid,
                be_window=window, line_shape=shape, fwhm_range=fwhm_range, **kw,
            )

        def graphitic_main_dsg() -> ComponentSlot:
            return slot(
                "main_graphitic", C1S_WINDOWS["graphitic"], LineShape.DS_G,
                main_fwhm,
                fixed_params=(("beta", DSG_LORENTZIAN_HWHM_C1S),),
                param_ranges=(("alpha", DSG_ALPHA_RANGE_GRAPHITIC),),
            )

        def graphitic_main_asymgl() -> ComponentSlot:
            return slot(
                "main_graphitic", C1S_WINDOWS["graphitic"], LineShape.ASYM_GL,
                main_fwhm,
                param_ranges=(("asymmetry", ASYMGL_ASYMMETRY_RANGE),),
            )

        def aliphatic_main() -> ComponentSlot:
            return slot("main_aliphatic", C1S_WINDOWS["aliphatic"],
                        LineShape.PSEUDO_VOIGT, FWHM_RANGE_CONTAMINATION)

        shake_up = slot(
            "satellite_pi", C1S_WINDOWS["shake_up_pi"], LineShape.PSEUDO_VOIGT,
            FWHM_RANGE_SATELLITE,
            linked_to="main_graphitic", linked_offset_range=SATELLITE_OFFSET_RANGE,
        )

        def contam(key, linked_fwhm=None, offset=None) -> ComponentSlot:
            kw = {}
            if linked_fwhm:
                kw["fwhm_linked_to"] = linked_fwhm
            if offset:
                mid, hw = offset
                kw["linked_to"] = "main_graphitic"
                kw["linked_offset_range"] = (mid - hw, mid + hw)
            return slot(f"contamination_{key}", C1S_WINDOWS[key],
                        LineShape.PSEUDO_VOIGT, FWHM_RANGE_CONTAMINATION, **kw)

        shared_decl = ((_SHARED_CONTAM_FWHM,
                        FWHM_RANGE_CONTAMINATION[0], FWHM_RANGE_CONTAMINATION[1]),)
        keys = ["CO", "C=O", "OC=O"]

        candidates: list[CandidateModel] = []

        def add(name, slots, shared=()):
            candidates.append(CandidateModel(
                name=name, background=BackgroundType.SHIRLEY,
                slots=tuple(slots), shared_fwhm_params=tuple(shared),
            ))

        # --- A family: DS+G asymmetric main + satellite + contaminants ---
        base_a = [graphitic_main_dsg(), shake_up]
        plain = [contam(k) for k in keys]
        add("A0_graphite_asym_satellite", base_a)
        for n in (1, 2, 3):
            add(f"A{n}_graphite_asym_sat_plus_{'_'.join(keys[:n])}",
                base_a + plain[:n])

        # --- A_linked: shared contamination width (Biesinger 2022) ---
        linked = [contam(k, linked_fwhm=_SHARED_CONTAM_FWHM) for k in keys]
        for n in (1, 2, 3):
            add(f"A{n}_linked", base_a + linked[:n], shared_decl)

        # --- A_linked_offset: + offset-parameterized contaminant centers ---
        offset_linked = [
            contam(k, linked_fwhm=_SHARED_CONTAM_FWHM, offset=CONTAM_OFFSETS[k])
            for k in keys
        ]
        for n in (1, 2, 3):
            add(f"A{n}_linked_offset", base_a + offset_linked[:n], shared_decl)

        # --- AG family: asym-GL graphitic main (expert-fit parity family) ---
        base_ag = [graphitic_main_asymgl(), shake_up]
        add("AG0_graphite_asymGL_satellite", base_ag)
        for n in (1, 2, 3):
            add(f"AG{n}_graphite_asymGL_sat_plus_{'_'.join(keys[:n])}",
                base_ag + plain[:n])
        for n in (1, 2, 3):
            add(f"AG{n}_linked", base_ag + linked[:n], shared_decl)

        # --- M family: mixed graphitic (DS+G) + aliphatic (PV) two mains ---
        base_m = [graphitic_main_dsg(), aliphatic_main(), shake_up]
        add("M0_graph_asym_aliph_sym_satellite", base_m)
        for n in (1, 2, 3):
            add(f"M{n}_graph_asym_aliph_sym_sat_{'_'.join(keys[:n])}",
                base_m + plain[:n])

        # --- B family: symmetric adventitious-carbon models (no satellite —
        #     admissibility: shake-up requires an asymmetric sp² main) ---
        aliph = aliphatic_main()
        aliph_fwhm_param = "s_main_aliphatic_fwhm"
        blinked = [contam(k, linked_fwhm=aliph_fwhm_param) for k in keys]
        add("B2_linked", [aliph] + blinked[:2])
        add("B3_linked", [aliph] + blinked[:3])
        # plain-window symmetric variants (low-priority but admissible)
        graph_sym = slot("main_graphitic", C1S_WINDOWS["graphitic"],
                         LineShape.PSEUDO_VOIGT, main_fwhm)
        add("B2_graphite_sym_CO_C=O", [graph_sym] + plain[:2])
        add("B3_graphite_sym_CO_C=O_OC=O", [graph_sym] + plain[:3])

        return candidates


register_region(C1sModule())
