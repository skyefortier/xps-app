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

ADJUDICATION #7 (2026-07-03) — IMPLEMENTED, HYPOTHESIS REJECTED BY THE DATA
(2026-07-04): the ruling ordered independent doublet widths (2p1/2 >=
2p3/2, Coster-Kronig) with the expectation the area ratio returns to ~0.5.
The machinery is implemented (``fwhm_excess_range`` + width-aware AREA-ratio
linkage, validated on synthetic truth) and the free-width candidates are
enumerated below — but on BOTH corrected real anchors the excess pegs at 0
(width freedom buys nothing: χ²ᵣ 2.41/3.27 vs 2.40/3.25 shared-width) and
the relaxed ratio still pegs at 0.55 with or without width freedom.  The
ratio anomaly is therefore NOT a shared-FWHM artifact.  Per the ruling's
fallback, secondary diagnostics were run and logged in PROGRESS.md (no
scan-order ratio trend → no beam-damage signal; shallow ratio↔excess
identifiability valley on Scan; residual dipole in the doublet valley plus
positive low-BE shoulders at −2…−4.8 eV — differential-charging candidate,
for Skye).  Consequently Δso/ratio REMAIN CONDITIONAL — the adjudicated
lift was contingent on the ratio returning to ~0.5, which did not occur.
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
# 2p1/2 Coster-Kronig width EXCESS over the 2p3/2 (adjudication 2026-07-03,
# docs/autofit/adjudication-decisions.md #7: the 2p1/2 is intrinsically
# broader — the shared-FWHM constraint was mis-partitioning doublet area and
# pushing the apparent ratio above 0.5).  Widths are INDEPENDENT under the
# physical inequality fwhm(2p1/2) = fwhm(2p3/2) + excess, excess >= 0.
# The excess UPPER bound is an UNVERIFIED bounded-relaxation tunable
# (~45% of the labeled shared width); the data decides within it.
CL2P_12_FWHM_EXCESS_RANGE = (0.0, 0.8)
# containment range for the free-width 2p1/2 (32-range + excess cap)
CL2P_12_FWHM_RANGE = (CL2P_FWHM_RANGE[0],
                      CL2P_FWHM_RANGE[1] + CL2P_12_FWHM_EXCESS_RANGE[1])
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
            {"constant": "p12_fwhm_excess_range_ev",
             "value": list(CL2P_12_FWHM_EXCESS_RANGE),
             "status": "UNVERIFIED",
             "source": "bounded-relaxation tunable; independence itself per "
                       "expert adjudication 2026-07-03 "
                       "(docs/autofit/adjudication-decisions.md #7 — "
                       "Coster-Kronig 2p1/2 broadening)"},
            {"constant": "background", "value": "smart_exp",
             "status": "UNVERIFIED", "source": "expert practice for this data set"},
        ]

    def build_candidates(
        self, phase: Phase, oxidation_state: Optional[str] = None
    ) -> list[CandidateModel]:
        """
        - ``Cl0_doublet``           — fixed 2:1 ratio, shared FWHM
        - ``Cl0r_doublet_relaxed``  — bounded-relaxed ratio, shared FWHM
        - ``Cl0w_doublet_freewidth``          — fixed 2:1 ratio, independent
          widths (2p1/2 >= 2p3/2, Coster-Kronig — adjudication #7)
        - ``Cl0rw_doublet_relaxed_freewidth`` — relaxed ratio + independent
          widths (the full test: with width freedom the fitted ratio is
          expected back at ~0.5)

        The enumeration decides which hypothesis the data pays for.
        """
        if oxidation_state is not None:
            raise KeyError(
                f"Cl 2p defines no oxidation-state override {oxidation_state!r}"
            )
        pid = phase.id

        _empirical_justification = (
            "UNVERIFIED-empirical: labeled-set calibration only (labeled "
            "fits 1.65-1.80 eV) -- no region-specific physical broadening "
            "mechanism is cited"
        )
        _coster_kronig_justification = (
            "2p1/2 Coster-Kronig broadening is a genuine physical "
            "mechanism (an additional non-radiative decay channel "
            "unavailable to 2p3/2 shortens the 2p1/2 core-hole lifetime "
            "and broadens its linewidth; adjudication 2026-07-03, "
            "docs/autofit/adjudication-decisions.md #7), but the specific "
            "excess bound (0.8 eV, ~45% of the labeled shared width) is "
            "itself an UNVERIFIED bounded-relaxation tunable, not a cited "
            "magnitude"
        )

        def p32() -> ComponentSlot:
            return ComponentSlot(
                role="main_cl2p32", region=REGION, phase_id=pid,
                be_window=CL2P_32_WINDOW, line_shape=LineShape.PSEUDO_VOIGT,
                fwhm_range=CL2P_FWHM_RANGE,
                broad_justification=_empirical_justification,
            )

        def p12(ratio, ratio_range, free_width=False) -> ComponentSlot:
            if free_width:
                # independent width under the Coster-Kronig inequality
                # (adjudication #7): fwhm12 = fwhm32 + excess, excess >= 0
                return ComponentSlot(
                    role="main_cl2p12", region=REGION, phase_id=pid,
                    be_window=CL2P_12_WINDOW, line_shape=LineShape.PSEUDO_VOIGT,
                    fwhm_range=CL2P_12_FWHM_RANGE,
                    linked_to="main_cl2p32",
                    linked_offset_range=CL2P_SPLITTING_RANGE,
                    area_ratio=ratio,
                    area_ratio_range=ratio_range,
                    share_parent_params=("gl_ratio",),
                    fwhm_excess_range=CL2P_12_FWHM_EXCESS_RANGE,
                    broad_justification=_coster_kronig_justification,
                )
            return ComponentSlot(
                role="main_cl2p12", region=REGION, phase_id=pid,
                be_window=CL2P_12_WINDOW, line_shape=LineShape.PSEUDO_VOIGT,
                fwhm_range=CL2P_FWHM_RANGE,
                linked_to="main_cl2p32",
                linked_offset_range=CL2P_SPLITTING_RANGE,
                area_ratio=ratio,
                area_ratio_range=ratio_range,
                share_parent_params=("gl_ratio", "fwhm"),
                broad_justification=_empirical_justification,
            )

        return [
            CandidateModel(name="Cl0_doublet", background=CL2P_BACKGROUND,
                           slots=(p32(), p12(CL2P_RATIO, None))),
            CandidateModel(name="Cl0r_doublet_relaxed",
                           background=CL2P_BACKGROUND,
                           slots=(p32(), p12(CL2P_RATIO, CL2P_RATIO_RANGE))),
            # Free-width variants (adjudication #7).  Cl0w carries the
            # adjudicated physics: statistical 2:1 ratio held, widths
            # independent — the enumeration arbitrates it against the
            # shared-width and relaxed-ratio hypotheses.
            CandidateModel(name="Cl0w_doublet_freewidth",
                           background=CL2P_BACKGROUND,
                           slots=(p32(), p12(CL2P_RATIO, None,
                                             free_width=True))),
            CandidateModel(name="Cl0rw_doublet_relaxed_freewidth",
                           background=CL2P_BACKGROUND,
                           slots=(p32(), p12(CL2P_RATIO, CL2P_RATIO_RANGE,
                                             free_width=True))),
        ]


register_region(Cl2pModule())
