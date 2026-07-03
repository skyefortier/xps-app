"""
B 1s region module — the weak exemplar (spec §3.3).

IMPORTANT — component-assignment conflict (PROGRESS.md discrepancy #8): the
two expert sources SWAP the chemical labels of the two sub-oxide components
(spec §3.3 quotes B-C 189.41 / B-B 187.39 from the 4-GTA analysis; the
good-quality B4C-UCl4 fits label B-C 187.10–187.24 / B-B 188.12–188.77).
This module therefore uses POSITION-NEUTRAL role names (``main_b_low``,
``main_b_mid``, ``main_b_oxide``) and defers chemical assignment to the
analyst.  All windows are UNVERIFIED-calibration, anchored on the
GOOD-QUALITY labeled exemplar (B4C-UCl4, χ²ᵣ 1.4–2.5, graphite-referenced
frame); the 4-GTA B 1s fits (χ²ᵣ 17–10⁵) are excluded as suspect per the
run brief.

Insulator/semiconductor boron phases → symmetric lineshapes only (Layer A);
the labeled fits use GL/Gaussian.
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

REGION = "B 1s"

# Windows (corrected frame of the labeled exemplar) — UNVERIFIED-calibration:
# low  : labeled 187.10–187.24
# mid  : labeled 188.12–188.77
# oxide: labeled pinned 193.00 (analyst fixed); window allows freedom
# low/mid OVERLAP deliberately (187.8–188.0): a knife-edge shared boundary
# puts a component at the edge in both windows with tie-breaking left to
# window ordering (Codex cookbook finding #7).  With overlap, the engine's
# nearest-window-center rule owns the ambiguity band explicitly.  Role-swap
# detection for symmetric overlapping components remains future work
# (logged in PROGRESS.md).
B1S_LOW_WINDOW = (186.4, 188.0)
B1S_MID_WINDOW = (187.8, 189.4)
B1S_OXIDE_WINDOW = (192.2, 193.8)

# UNVERIFIED-empirical (labeled set 1.49–2.27 eV).
B1S_FWHM_RANGE = (1.2, 2.5)

# Expert practice for this data set (ui.bgType 'smart_exp') — UNVERIFIED
# methodological choice.
B1S_BACKGROUND = BackgroundType.SMART_EXP


class B1sModule:
    region = REGION

    def diagnostic_windows(self) -> dict[str, tuple[float, float]]:
        return {"low": B1S_LOW_WINDOW, "mid": B1S_MID_WINDOW,
                "oxide": B1S_OXIDE_WINDOW}

    def provenance(self) -> list[dict]:
        return [
            {"constant": "low_window_ev", "value": list(B1S_LOW_WINDOW),
             "status": "UNVERIFIED",
             "source": "labeled-set calibration (B4C-UCl4 exemplar); chemical "
                       "assignment DISPUTED between expert sources "
                       "(PROGRESS.md discrepancy #8)"},
            {"constant": "mid_window_ev", "value": list(B1S_MID_WINDOW),
             "status": "UNVERIFIED", "source": "same as low_window_ev"},
            {"constant": "oxide_window_ev", "value": list(B1S_OXIDE_WINDOW),
             "status": "UNVERIFIED",
             "source": "labeled-set calibration (analyst-pinned 193.00)"},
            {"constant": "fwhm_range_ev", "value": list(B1S_FWHM_RANGE),
             "status": "UNVERIFIED", "source": "labeled-set calibration"},
            {"constant": "background", "value": "smart_exp",
             "status": "UNVERIFIED", "source": "expert practice for this data set"},
        ]

    def build_candidates(
        self, phase: Phase, oxidation_state: Optional[str] = None
    ) -> list[CandidateModel]:
        """Component-count ladder over the three observed positions."""
        if oxidation_state is not None:
            raise KeyError(
                f"B 1s defines no oxidation-state override {oxidation_state!r}"
            )
        pid = phase.id

        def pv(role, window) -> ComponentSlot:
            return ComponentSlot(
                role=role, region=REGION, phase_id=pid,
                be_window=window, line_shape=LineShape.PSEUDO_VOIGT,
                fwhm_range=B1S_FWHM_RANGE,
            )

        low = pv("main_b_low", B1S_LOW_WINDOW)
        mid = pv("main_b_mid", B1S_MID_WINDOW)
        oxide = pv("main_b_oxide", B1S_OXIDE_WINDOW)

        def cand(name, slots):
            return CandidateModel(name=name, background=B1S_BACKGROUND,
                                  slots=tuple(slots))

        return [
            cand("B1_low", [low]),
            cand("B2_low_mid", [low, mid]),
            cand("B2b_low_oxide", [low, oxide]),
            cand("B3_low_mid_oxide", [low, mid, oxide]),
        ]


register_region(B1sModule())
