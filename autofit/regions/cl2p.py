"""
Cl 2p region module — the doublet exemplar (spec §3.4).

Constants:
- Δso = 1.60 eV and 2p3/2:2p1/2 = 2:1 (ratio 0.5): **CONDITIONAL** per spec
  §9 (NaCl, Surf. Sci. Spectra — DOI 10.1116/1.1247741) until a
  chloride-source primary fit is cited.  The labeled fits use exactly
  1.60 / 0.5 with shared FWHM + GL mix.
- 2p3/2 window: UNVERIFIED-calibration around the labeled chloride fits
  (197.83–197.92, corrected frame).  NOTE the labeled set's uncorrected tab
  (Cl2p Scan_1, ccShift 0, 2p3/2 at 193.38 raw) is OUT of this window by
  construction — the engine consumes charge-corrected data.
- The labeled Cl 2p fits carry the documented elevated χ²ᵣ (2.85/4.94) —
  unmodeled structure is expected; the residual diagnostics/proposal pass
  reports it rather than the grammar inventing an uncited second species.
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

REGION = "Cl 2p"

CL2P_32_WINDOW = (196.8, 199.0)     # UNVERIFIED-calibration (labeled 197.8–197.9)
# Δso window around the CONDITIONAL 1.60 eV (10.1116/1.1247741).
CL2P_SPLITTING_RANGE = (1.55, 1.65)
CL2P_RATIO = 0.5                    # 2:1 statistical — CONDITIONAL (same source)
CL2P_RATIO_RANGE = (0.45, 0.55)     # bounded relaxation variant — UNVERIFIED
CL2P_FWHM_RANGE = (1.2, 2.2)        # UNVERIFIED-empirical (labeled 1.65–1.80)
# 2p1/2 fallback window (matching only; center is expression-driven).
CL2P_12_WINDOW = (CL2P_32_WINDOW[0] + CL2P_SPLITTING_RANGE[0],
                  CL2P_32_WINDOW[1] + CL2P_SPLITTING_RANGE[1])

# Expert practice for this data set (ui.bgType 'smart_exp') — UNVERIFIED.
CL2P_BACKGROUND = BackgroundType.SMART_EXP


class Cl2pModule:
    region = REGION

    def diagnostic_windows(self) -> dict[str, tuple[float, float]]:
        return {"p32": CL2P_32_WINDOW, "p12": CL2P_12_WINDOW}

    def provenance(self) -> list[dict]:
        return [
            {"constant": "spin_orbit_splitting_ev", "value": 1.60,
             "status": "CONDITIONAL",
             "source": "NaCl, Surf. Sci. Spectra, DOI 10.1116/1.1247741 — "
                       "conditional until a chloride-source primary fit is cited"},
            {"constant": "area_ratio_2p12_over_2p32", "value": CL2P_RATIO,
             "status": "CONDITIONAL", "source": "2:1 statistical; same source"},
            {"constant": "p32_window_ev", "value": list(CL2P_32_WINDOW),
             "status": "UNVERIFIED",
             "source": "labeled-set calibration (197.83–197.92 corrected)"},
            {"constant": "fwhm_range_ev", "value": list(CL2P_FWHM_RANGE),
             "status": "UNVERIFIED", "source": "labeled-set calibration"},
            {"constant": "ratio_relaxation_range", "value": list(CL2P_RATIO_RANGE),
             "status": "UNVERIFIED", "source": "bounded-relaxation tunable"},
            {"constant": "background", "value": "smart_exp",
             "status": "UNVERIFIED", "source": "expert practice for this data set"},
        ]

    def build_candidates(
        self, phase: Phase, oxidation_state: Optional[str] = None
    ) -> list[CandidateModel]:
        """
        - ``Cl0_doublet``          — fixed 2:1 statistical ratio
        - ``Cl0r_doublet_relaxed`` — bounded-relaxed ratio (enumeration
                                     decides whether the data pays for it)
        """
        if oxidation_state is not None:
            raise KeyError(
                f"Cl 2p defines no oxidation-state override {oxidation_state!r}"
            )
        pid = phase.id

        def p32() -> ComponentSlot:
            return ComponentSlot(
                role="main_cl2p32", region=REGION, phase_id=pid,
                be_window=CL2P_32_WINDOW, line_shape=LineShape.PSEUDO_VOIGT,
                fwhm_range=CL2P_FWHM_RANGE,
            )

        def p12(ratio, ratio_range) -> ComponentSlot:
            return ComponentSlot(
                role="main_cl2p12", region=REGION, phase_id=pid,
                be_window=CL2P_12_WINDOW, line_shape=LineShape.PSEUDO_VOIGT,
                fwhm_range=CL2P_FWHM_RANGE,
                linked_to="main_cl2p32",
                linked_offset_range=CL2P_SPLITTING_RANGE,
                area_ratio=ratio,
                area_ratio_range=ratio_range,
                share_parent_params=("gl_ratio", "fwhm"),
            )

        return [
            CandidateModel(name="Cl0_doublet", background=CL2P_BACKGROUND,
                           slots=(p32(), p12(CL2P_RATIO, None))),
            CandidateModel(name="Cl0r_doublet_relaxed",
                           background=CL2P_BACKGROUND,
                           slots=(p32(), p12(CL2P_RATIO, CL2P_RATIO_RANGE))),
        ]


register_region(Cl2pModule())
