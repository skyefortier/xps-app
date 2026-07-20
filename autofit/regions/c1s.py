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
    MaterialClass,
    Phase,
)
from . import register_region

REGION = "C 1s"

# BE windows (eV, corrected frame). UNVERIFIED-calibration: the window
# CENTERS are anchored on cited values — graphite C 1s 284.4 (Leiro,
# 10.1016/S0368-2048(02)00284-0), adventitious C-C/C-H 284.8 and the
# +1.5/+3.0/+4.0 oxidised-carbon shifts (Biesinger 2022, CONDITIONAL soft
# priors per spec §9) — but the window WIDTHS are generous prototype bins
# from fitalg with no primary source; they gate candidate admissibility and
# must be sensitivity-tested before publication claims.
C1S_WINDOWS: dict[str, tuple[float, float]] = {
    "graphitic":   (284.0, 284.8),   # sp² graphitic C-C
    "aliphatic":   (284.6, 285.4),   # adventitious C-C/C-H
    "CO":          (285.8, 286.8),   # C-O / C-OH
    "C=O":         (287.3, 288.3),
    "OC=O":        (288.5, 289.6),
    "shake_up_pi": (290.0, 292.0),   # π→π* shake-up
}

# FWHM priors (eV):
# graphitic main — ordered single species, may be narrow.  UNVERIFIED
# (fitalg; instrument-dependent; no primary source — labeled expert fits
# put the graphitic main at 0.61–0.73 eV on this instrument, consistent
# with but not derived from this range).
FWHM_RANGE_GRAPHITIC = (0.4, 1.2)
# aromatic-polymer main — Beamson & Briggs, "High Resolution XPS of Organic
# Polymers — The Scienta ESCA300 Database", Wiley (1992): aromatic C 1s
# 0.9–1.5 eV; (0.8, 1.8) is the generous cross-instrument envelope.
FWHM_RANGE_AROMATIC_POLYMER = (0.8, 1.8)
# π→π* satellite — intrinsically broad (multi-electron excitation).
# fitalg's (1.0, 3.0) was an UNVERIFIED tunable; CALIBRATED 2026-07-03 on the
# labeled expert set: 44 expert C 1s fits across 5 projects / 2 analysts fit
# the satellite at 1.9–5.0 eV (median 4.17).  With the 3.0 cap every gate
# candidate pegged satellite_pi:fwhm@max and was filtered — zero survivors.
FWHM_RANGE_SATELLITE = (1.0, 5.5)
# adventitious carbon (incl. aliphatic main): 0.8 eV floor per Biesinger,
# Appl. Surf. Sci. 597 (2022) 153681 and Greczynski & Hultman (2020);
# ~2.0 eV UNIFORM CAP per expert adjudication 2026-07-03
# (docs/autofit/adjudication-decisions.md #5) — a literature-reasonable
# upper bound, instrument/pass-energy-dependent; a CAP, not a target.
# Replaces the previous SPLIT convention (Biesinger 1.6 ceiling for the
# A/M/B families vs a 3.5 labeled-set-calibrated ceiling for the AG/MG
# expert-practice families).  NOTE the labeled expert set fits adventitious
# components at median 2.08 eV (70% above 1.6, max 5.46): under the
# adjudicated cap, exact width parity with the broadest expert components
# is not expressible by construction — the cap is the ruling.
FWHM_RANGE_CONTAMINATION = (0.8, 2.0)

# MIXED material class (2026-07-20): FWHM_RANGE_CONTAMINATION's ceiling is
# justified by a single, well-referenced HOMOGENEOUS surface. That
# condition is not met for an analyte embedded in a different matrix —
# analyte and matrix can charge differently under X-ray illumination
# (differential charging), and a non-uniform spatial distribution of
# charging potentials broadens the observed peak (inhomogeneous
# broadening; see provenance() for the citations). Withdrawing that
# homogeneity assumption needs no citation — it is the removal of a
# claim, not a new one — so this widens the ceiling toward
# "unconstrained" rather than asserting a second, chemistry-flavored
# magic number (the provenance-audit trap this unit exists to avoid: a
# cap derived from THIS LAB'S OWN mixed-phase spectra would be exactly
# the self-reference the audit removed, wearing a feature label instead
# of a tier badge). The floor is untouched: differential charging only
# broadens a peak, it never narrows one.
#
# A fully unconstrained (infinite) ceiling is not viable with the current
# engine: autofit/engine.py seeds the initial FWHM guess at the MIDPOINT
# of fwhm_range, so an infinite upper bound would seed an infinite
# initial value and break the optimizer outright. Some finite ceiling is
# therefore unavoidable for numerical stability — so this reuses
# fitting.py's OWN existing fwhm_max default (15.0 eV), the ceiling the
# manual /api/fit path already applies to literally every peak, everywhere
# in this app, rather than inventing a new number. Purely a numeric guard
# for optimizer stability, not a chemistry or physics claim (same footing
# as DSG_ALPHA_RANGE_GRAPHITIC's "fitalg numeric guard" below) — if a
# fitted component pegs this ceiling under MIXED, that is the numerical
# guard doing its job, not a measurement.
#
# KNOWN RISK (flag for review, do not silently paper over): the "_linked"
# candidate families share ONE width parameter across all 3 contaminant
# slots (see shared_decl below) — under MIXED that shared width relaxes
# to this same wide ceiling, so a single fat shared-width component could
# in principle absorb signal across the whole ~280-292 eV C 1s contaminant
# span. c1s.py's own MG-family comments already document an analogous
# overlap-degeneracy failure mode (see aliphatic_main_offset below); this
# is the same class of risk, now reachable through a wider ceiling instead
# of a free position. Should be adversarially fit-tested, not just read.
FWHM_MIXED_CEILING_NUMERIC_GUARD_EV = 15.0


def _contamination_fwhm_range(material_class: MaterialClass) -> tuple[float, float]:
    """FWHM_RANGE_CONTAMINATION, widened under MIXED. See the constant
    comment above — this relaxes a constraint, it never asserts a new one."""
    if material_class is MaterialClass.MIXED:
        return (FWHM_RANGE_CONTAMINATION[0], FWHM_MIXED_CEILING_NUMERIC_GUARD_EV)
    return FWHM_RANGE_CONTAMINATION


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

    def provenance(self) -> list[dict]:
        return [
            {"constant": "graphite_reference_ev", "value": 284.4,
             "status": "VERIFIED",
             "source": "Leiro DOI 10.1016/S0368-2048(02)00284-0; HOPG SSS "
                       "10.1116/1.1247695 (window anchor)"},
            {"constant": "adventitious_reference_ev", "value": 284.8,
             "status": "CONDITIONAL",
             "source": "Biesinger 2022 10.1016/j.apsusc.2022.153681; "
                       "Greczynski 10.1002/anie.201916000 — convention"},
            {"constant": "dsg_core_hole_beta_ev", "value": DSG_LORENTZIAN_HWHM_C1S,
             "status": "VERIFIED",
             "source": "Campbell & Papp 2001 DOI 10.1006/adnd.2000.0848 "
                       "(Γ_K(C) ≈ 0.10 eV FWHM → 0.05 HWHM)"},
            {"constant": "contamination_offsets_ev",
             "value": {k: list(v) for k, v in CONTAM_OFFSETS.items()},
             "status": "CONDITIONAL",
             "source": "Biesinger 2022 soft priors (+1.5/+3.0/+4.0)"},
            {"constant": "window_widths", "value": {k: list(v) for k, v in C1S_WINDOWS.items()},
             "status": "UNVERIFIED", "source": "fitalg prototype bins around cited anchors"},
            {"constant": "fwhm_graphitic_ev", "value": list(FWHM_RANGE_GRAPHITIC),
             "status": "UNVERIFIED", "source": "fitalg; instrument-dependent"},
            {"constant": "fwhm_contamination_floor_ev",
             "value": FWHM_RANGE_CONTAMINATION[0],
             "status": "CONDITIONAL",
             "source": "Biesinger, Appl. Surf. Sci. 597 (2022) 153681; "
                       "Greczynski & Hultman (2020) — published lower "
                       "bound for adventitious/aliphatic carbon FWHM"},
            {"constant": "fwhm_contamination_ceiling_ev",
             "value": FWHM_RANGE_CONTAMINATION[1],
             "status": "UNVERIFIED",
             "source": "lab-adjudicated cap, not a literature value — "
                       "expert adjudication 2026-07-03 "
                       "(docs/autofit/adjudication-decisions.md #5); a "
                       "literature-reasonable upper bound but a cap, not "
                       "a target; replaces the prior split 1.6/3.5 caps"},
            {"constant": "fwhm_satellite_ev", "value": list(FWHM_RANGE_SATELLITE),
             "status": "UNVERIFIED",
             "source": "labeled-set calibration (44 fits, 1.9–5.0 eV)"},
            {"constant": "dsg_alpha_cap", "value": list(DSG_ALPHA_RANGE_GRAPHITIC),
             "status": "UNVERIFIED", "source": "fitalg numeric guard"},
            {"constant": "asymgl_family", "value": "empirical asymmetric envelope",
             "status": "UNVERIFIED", "source": "expert-practice family (AG/MG)"},
            {"constant": "asymgl_asymmetry_range", "value": list(ASYMGL_ASYMMETRY_RANGE),
             "status": "UNVERIFIED",
             "source": "UNVERIFIED-empirical: chosen to bracket the expert "
                       "reference fits (asymmetry ≈ 0.10, glMix ≈ "
                       "0.08–0.5) rather than derived from literature; "
                       "treat as a calibration target, not physics"},
            {"constant": "satellite_offset_range_ev", "value": list(SATELLITE_OFFSET_RANGE),
             "status": "UNVERIFIED",
             "source": "fitalg tunable — the π→π* satellite "
                       "offset window from the graphitic main"},
            {"constant": "aromatic_polymer_fwhm_ev",
             "value": list(FWHM_RANGE_AROMATIC_POLYMER),
             "status": "CONDITIONAL",
             "source": "Beamson & Briggs, High Resolution XPS of Organic "
                       "Polymers — The Scienta ESCA300 Database, Wiley "
                       "(1992): aromatic C 1s 0.9–1.5 eV; widened to "
                       "0.8–1.8 as the generous cross-instrument envelope "
                       "(the widening beyond the cited range is editorial, "
                       "not itself literature-derived)"},
            {"constant": "aliphatic_linked_offset_range_ev", "value": [0.2, 0.6],
             "status": "UNVERIFIED",
             "source": "UNVERIFIED-empirical (labeled-set + convention): "
                       "brackets both expert practice (+0.30: graphitic "
                       "284.5 vs aliphatic 284.8) and Biesinger's "
                       "adventitious C-C/C-H convention (284.8 vs "
                       "graphite 284.4, +0.4)"},
            {"constant": "mixed_material_class_width_relaxation",
             "value": "under MaterialClass.MIXED (analyte embedded in a "
                      "different matrix), the contamination/adventitious "
                      "FWHM ceiling's single-species-homogeneity "
                      "assumption is withdrawn and the ceiling is relaxed "
                      "toward unconstrained; no new position or width "
                      "value is asserted — position windows and every "
                      "other FWHM family are unchanged",
             "status": "CONDITIONAL",
             "source": "differential charging between analyte and matrix "
                       "causes inhomogeneous broadening (Baer, "
                       "Artyushkova, Cohen, Easton, Engelhard, Gengenbach, "
                       "Greczynski, Mack, Morgan, Roberts, \"XPS Guide: "
                       "Charge neutralization and binding energy "
                       "referencing for insulating samples,\" J. Vac. Sci. "
                       "Technol. A 38, 031204 (2020), DOI "
                       "10.1116/6.0000057 — differential charging "
                       "broadens peaks, and a single charge correction is "
                       "insufficient once it is present; internal "
                       "referencing has \"limited accuracy ... often "
                       "including multiphase and other complex samples\"; "
                       "Greczynski & Hultman, \"X-ray photoelectron "
                       "spectroscopy: Towards reliable binding energy "
                       "referencing,\" Prog. Mater. Sci. 107 (2020) "
                       "100591, DOI 10.1016/j.pmatsci.2019.100591)"},
            {"constant": "mixed_fwhm_ceiling_numeric_guard",
             "value": FWHM_MIXED_CEILING_NUMERIC_GUARD_EV,
             "status": "UNVERIFIED",
             "source": "a fully unconstrained (infinite) ceiling breaks "
                       "the engine's initial-value seeding (the FWHM "
                       "guess is the fwhm_range midpoint); this reuses "
                       "fitting.py's own existing fwhm_max default, the "
                       "ceiling the manual /api/fit path already applies "
                       "to every peak in this app — a numeric guard for "
                       "optimizer stability, not a chemistry or physics "
                       "claim (same footing as dsg_alpha_cap above)"},
        ]

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
        contam_fwhm = _contamination_fwhm_range(phase.material_class)

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
                        LineShape.PSEUDO_VOIGT, contam_fwhm)

        shake_up = slot(
            "satellite_pi", C1S_WINDOWS["shake_up_pi"], LineShape.PSEUDO_VOIGT,
            FWHM_RANGE_SATELLITE,
            linked_to="main_graphitic", linked_offset_range=SATELLITE_OFFSET_RANGE,
        )

        def contam(key, linked_fwhm=None, offset=None,
                   fwhm_range=None) -> ComponentSlot:
            kw = {}
            if linked_fwhm:
                kw["fwhm_linked_to"] = linked_fwhm
            if offset:
                mid, hw = offset
                kw["linked_to"] = "main_graphitic"
                kw["linked_offset_range"] = (mid - hw, mid + hw)
            return slot(f"contamination_{key}", C1S_WINDOWS[key],
                        LineShape.PSEUDO_VOIGT,
                        fwhm_range if fwhm_range is not None else contam_fwhm, **kw)

        shared_decl = ((_SHARED_CONTAM_FWHM, contam_fwhm[0], contam_fwhm[1]),)
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

        # --- AG family: asym-GL graphitic main (expert-fit parity family).
        #     Contamination widths use the UNIFORM adjudicated cap — the
        #     former split lab-practice (0.8, 3.5) convention was replaced
        #     per adjudication #5; AG/MG now differ from A/M only in the
        #     graphitic main lineshape. ---
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

        # --- MG family: the expert-practice STRUCTURE — asym-GL graphitic +
        #     aliphatic + satellite + contaminants (uniform adjudicated
        #     contamination cap).  The
        #     reference C 1s fits are exactly MG2-shaped (graphitic asym-GL
        #     284.5 + adventitious 284.8/285.9/287.6 + π→π* ~290.9).
        #     The aliphatic center is OFFSET-LINKED to the graphitic main
        #     (+0.2…+0.6 eV): with a free center the optimizer slides the
        #     aliphatic into the graphitic flank and pegs the window floor
        #     (overlap degeneracy, fitalg LIMITATIONS §9).  The offset window
        #     brackets both the expert practice (+0.30: 284.8 vs 284.5) and
        #     Biesinger's adventitious C-C/C-H at 284.8 vs graphite 284.4
        #     (+0.4).  UNVERIFIED-empirical (labeled-set + convention). ---
        def aliphatic_main_offset() -> ComponentSlot:
            return slot("main_aliphatic", C1S_WINDOWS["aliphatic"],
                        LineShape.PSEUDO_VOIGT, contam_fwhm,
                        linked_to="main_graphitic",
                        linked_offset_range=(0.2, 0.6))

        base_mg = [graphitic_main_asymgl(), aliphatic_main_offset(), shake_up]
        add("MG0_graphAsymGL_aliph_satellite", base_mg)
        for n in (1, 2, 3):
            add(f"MG{n}_graphAsymGL_aliph_sat_{'_'.join(keys[:n])}",
                base_mg + plain[:n])

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
