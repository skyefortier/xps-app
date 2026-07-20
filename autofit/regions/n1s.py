"""
N 1s region module — Stage-3 MINIMAL version.

Exists at this stage primarily as the co-fit partner for the U 4f window
(in U-in-BN samples the BN N 1s line at ~398.3 eV sits inside the U 4f scan
and overshadows the U 4f5/2 shake-up satellite — spec §2/§3.2: the two
grammars are composed and fit jointly).  The full N 1s cookbook module
(charge-reference exemplar, spec §3.5) is a later unit.

Constants:
- h-BN N 1s ~398.0–398.3 eV: **UNVERIFIED** per spec §9 ("pull a primary
  table") — the window below brackets the spec range and the labeled expert
  fit (398.30 after N-referenced charge correction).  Do not cite until a
  primary source is pulled.
- Widths/shape: UNVERIFIED-empirical from the single labeled exemplar
  (asym-GL, fwhm 1.05 eV, asymmetry 0.064).
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

REGION = "N 1s"

N1S_WINDOW = (396.5, 400.0)       # UNVERIFIED (see module docstring)
N1S_FWHM_RANGE = (0.7, 2.5)       # UNVERIFIED-empirical (exemplar 1.05 eV)
N1S_ASYM_RANGE = (0.0, 0.3)       # UNVERIFIED-empirical (exemplar 0.064)

# Matches the U 4f family so joint co-fit candidates share one background
# (composition requires background agreement).  UNVERIFIED choice.
N1S_BACKGROUND = BackgroundType.SMART


class N1sModule:
    region = REGION

    def diagnostic_windows(self) -> dict[str, tuple[float, float]]:
        return {"main": N1S_WINDOW}

    def provenance(self) -> list[dict]:
        return [
            {"constant": "main_window_ev", "value": list(N1S_WINDOW),
             "status": "UNVERIFIED",
             "source": "spec §9: h-BN N 1s ~398.0–398.3 pending a primary "
                       "table; window brackets spec range + labeled exemplar"},
            {"constant": "fwhm_range_ev", "value": list(N1S_FWHM_RANGE),
             "status": "UNVERIFIED", "source": "single labeled exemplar (1.05 eV)"},
            {"constant": "asymmetry_range", "value": list(N1S_ASYM_RANGE),
             "status": "UNVERIFIED", "source": "single labeled exemplar (0.064)"},
            {"constant": "background", "value": "smart",
             "status": "UNVERIFIED", "source": "matches U 4f family for co-fit"},
        ]

    def build_candidates(
        self, phase: Phase, oxidation_state: Optional[str] = None
    ) -> list[CandidateModel]:
        if oxidation_state is not None:
            raise KeyError(
                f"N 1s defines no oxidation-state override {oxidation_state!r}"
            )
        pid = phase.id
        _justification = (
            "UNVERIFIED-empirical: single labeled exemplar only (fwhm "
            "1.05 eV) -- no physical broadening mechanism cited; this is "
            "Stage-3 minimal N 1s support, not the full cookbook module"
        )
        pv_main = ComponentSlot(
            role="main_n1s", region=REGION, phase_id=pid,
            be_window=N1S_WINDOW, line_shape=LineShape.PSEUDO_VOIGT,
            fwhm_range=N1S_FWHM_RANGE,
            broad_justification=_justification,
        )
        ag_main = ComponentSlot(
            role="main_n1s", region=REGION, phase_id=pid,
            be_window=N1S_WINDOW, line_shape=LineShape.ASYM_GL,
            fwhm_range=N1S_FWHM_RANGE,
            param_ranges=(("asymmetry", N1S_ASYM_RANGE),),
            broad_justification=_justification,
        )
        return [
            CandidateModel(name="N0_pv", background=N1S_BACKGROUND,
                           slots=(pv_main,)),
            CandidateModel(name="N0_asymGL", background=N1S_BACKGROUND,
                           slots=(ag_main,)),
        ]


register_region(N1sModule())
