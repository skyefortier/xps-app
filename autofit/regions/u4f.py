"""
U 4f region module (spec v2.1 §3.2 — the Stage-3 deliverable).

Model decision (Skye, domain expert; spec §3.2): U(IV) 5f² is an open-shell
final state whose multiplet manifold is an unknown number of closely-spaced,
individually unresolvable lines — the **asymmetric LACX lineshape is the
physically-correct envelope of that manifold** (multiplet/final-state
origin, NOT metallic screening — Ilton & Bagus, Surf. Interface Anal. 43
(2011) 1549, DOI 10.1002/sia.3836; VERIFIED per spec §9).  The engine does
not force a multiplet-peak decomposition; oxidation-state ASSIGNMENT is out
of scope (parked).

Structure (validated against 40+ expert U 4f fits in docs/autofit/test_data;
see PROGRESS.md "U 4f design extraction"):

- **Main doublet**: LACX 4f7/2 (free α/β/m — "FitAllFree" expert practice)
  + 4f5/2 amplitude- and shape-linked at the spin-orbit splitting.
- **Satellite doublet**: the U(IV) shake-up satellite rides BOTH mains — one
  Voigt pair (sat7/2 offset-linked to the main; sat5/2 linked to sat7/2 at
  the same splitting).  This one pair explains both observed satellites
  (main+~6.3 eV and main+~17.2 eV = 6.3 + Δso).
- Everything fits JOINTLY in one window; N 1s overlap is handled by
  composing this module with the N 1s module via ``resolve`` (spec §2).

Safeguards (spec §3.2, retained):
- **Bounded asymmetry**: LACX α/β confined to a labeled-set-calibrated
  window so the tail cannot silently absorb a genuinely separable feature.
- The residual/proposal pass (engine-level) flags unexplained tail
  structure as a possible separate component without forcing
  over-parameterization.
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

REGION = "U 4f"

# ── Constants (cited or flagged) ────────────────────────────────────────────

# Spin-orbit splitting: 10.8–10.9 eV — VERIFIED (Ilton & Bagus 2011,
# 10.1002/sia.3836; NIST SRD 20 gives 10.8, see data/xps/elements-actinides.json
# U-4f7/2.spin_orbit).  Expert fits use 10.90 exactly.  Bounded, not fixed,
# so small calibration deviations remain expressible.
U4F_SPLITTING_RANGE = (10.75, 10.95)

# Theoretical 4f7/2:4f5/2 area ratio 4:3 → 0.75 — VERIFIED (Bagus et al.,
# 10.1063/1.4846135; NIST SRD 20 area_ratio 0.75).  Expert fits use a
# RELAXED empirical ratio 0.65–0.75 (spec §3.2: "relaxed empirical ratio,
# not a contradiction").  Default 0.75, bounded relaxation; the bounds are
# UNVERIFIED-empirical (labeled set ± margin).
U4F_RATIO_DEFAULT = 0.75
U4F_RATIO_RANGE = (0.60, 0.85)

# 4f7/2 BE window (corrected frame): inside the NIST-curated, oxidation-
# widened expected region 375.5–383.0 eV (data/xps/elements-actinides.json,
# nist-srd-20; metal nominal 377.3, real samples oxidized → higher).
# Tightened to the U(IV)-like practice of the labeled set (379.5–380.6):
# UNVERIFIED-calibration widths around cited anchors.
U4F72_WINDOW = (378.0, 382.5)
# 4f5/2 fallback window = 7/2 window + splitting (matching only; the fitted
# center is expression-driven).
U4F52_WINDOW = (388.75, 393.45)

# Main FWHM range — UNVERIFIED-empirical (labeled set 2.44–2.74 eV).
U4F_MAIN_FWHM_RANGE = (1.5, 3.5)

# Bounded-asymmetry safeguard (spec §3.2): LACX exponents confined around
# the labeled set (α 0.96–1.24, β 2.23–2.85) with margin.  UNVERIFIED-
# empirical — deliberately narrower than the generic (0.1, 5.0) so the tail
# cannot silently absorb a separable overlapping feature; the residual pass
# flags what the bounded tail cannot express.
U4F_LACX_ALPHA_RANGE = (0.5, 2.0)
U4F_LACX_BETA_RANGE = (1.0, 4.5)
# Gaussian kernel width in DATA POINTS (labeled set 0–8.2) — UNVERIFIED.
U4F_LACX_M_RANGE = (0.0, 100.0)

# Shake-up satellite offset from its main line: literature U(IV)
# satellite-to-main separation ≈ 6.8–7.1 eV (Ilton & Bagus 2011; Schindler
# et al., GCA 73 (2009) 2488, 10.1016/j.gca.2009.02.008); labeled set fits
# 6.07–6.38 eV.  Envelope brackets both — UNVERIFIED-calibration.
U4F_SAT_OFFSET_RANGE = (5.5, 8.5)
# Satellite-PAIR separation window for the free-separation candidates: the
# labeled set fits the pair 11.2 eV apart while the core splitting is 10.9
# (satellite separations need not track the core splitting) — bracketed
# around both; UNVERIFIED-calibration.
U4F_SATPAIR_SEP_RANGE = (10.5, 12.0)
# Satellite width — UNVERIFIED-empirical (labeled set 2.09–3.30 eV).
U4F_SAT_FWHM_RANGE = (1.5, 4.5)
# Satellite absolute fallback windows: DERIVED from the cited/flagged
# constants above (main window ± satellite offsets; used for slot MATCHING
# only — fitted centers are expression-driven off the mains).
U4F_SAT72_WINDOW = (U4F72_WINDOW[0] + U4F_SAT_OFFSET_RANGE[0],
                    U4F72_WINDOW[1] + U4F_SAT_OFFSET_RANGE[1])
U4F_SAT52_WINDOW = (U4F_SAT72_WINDOW[0] + U4F_SATPAIR_SEP_RANGE[0],
                    U4F_SAT72_WINDOW[1] + U4F_SATPAIR_SEP_RANGE[1])

# Background: the labeled U 4f fits all use the 'smart' (constrained
# Shirley) background — adopted to match expert practice; UNVERIFIED
# methodological choice (plain Shirley is the spec default elsewhere).
U4F_BACKGROUND = BackgroundType.SMART


class U4fModule:
    region = REGION

    def diagnostic_windows(self) -> dict[str, tuple[float, float]]:
        return {
            "main_72": U4F72_WINDOW,
            "main_52": U4F52_WINDOW,
            "satellite_72": U4F_SAT72_WINDOW,
            "satellite_52": U4F_SAT52_WINDOW,
        }

    def build_candidates(
        self, phase: Phase, oxidation_state: Optional[str] = None
    ) -> list[CandidateModel]:
        """
        Candidates (a controlled ladder of satellite-pair freedom, so model
        comparison can isolate WHICH freedom the data pays for — Codex
        Stage-3 finding #1):

        - ``U0_mains``            — main doublet only (reduced model for IC)
        - ``U1_mains_satpair``    — + satellite doublet locked to the core
                                    splitting (shape + amplitude tied)
        - ``U1b_mains_satpair_freesep`` — satellite doublet with FREE pair
                                    separation but shape + amplitude still
                                    tied: the clean test of "pair separation
                                    ≠ core splitting"
        - ``U2_mains_satfree``    — two fully independent satellites (each
                                    rides its own main; robustness variant)

        ``oxidation_state`` is accepted for the Layer-C seam; assignment is
        parked (spec §3.2) so no overrides are defined.
        """
        if oxidation_state is not None:
            raise KeyError(
                f"U 4f defines no oxidation-state override {oxidation_state!r} "
                "(oxidation-state assignment is parked, spec §3.2)"
            )
        pid = phase.id

        def slot(role, window, shape, fwhm_range, **kw) -> ComponentSlot:
            return ComponentSlot(
                role=role, region=REGION, phase_id=pid,
                be_window=window, line_shape=shape, fwhm_range=fwhm_range, **kw,
            )

        main_72 = slot(
            "main_u4f72", U4F72_WINDOW, LineShape.LACX, U4F_MAIN_FWHM_RANGE,
            param_ranges=(("alpha", U4F_LACX_ALPHA_RANGE),
                          ("beta", U4F_LACX_BETA_RANGE),
                          ("m", U4F_LACX_M_RANGE)),
        )
        main_52 = slot(
            "main_u4f52", U4F52_WINDOW, LineShape.LACX, U4F_MAIN_FWHM_RANGE,
            linked_to="main_u4f72",
            linked_offset_range=U4F_SPLITTING_RANGE,
            area_ratio=U4F_RATIO_DEFAULT,
            area_ratio_range=U4F_RATIO_RANGE,
            share_parent_params=("alpha", "beta", "m", "fwhm"),
        )

        sat_72 = slot(
            "satellite_u4f72", U4F_SAT72_WINDOW, LineShape.PSEUDO_VOIGT,
            U4F_SAT_FWHM_RANGE,
            linked_to="main_u4f72",
            linked_offset_range=U4F_SAT_OFFSET_RANGE,
        )
        sat_52 = slot(
            "satellite_u4f52", U4F_SAT52_WINDOW, LineShape.PSEUDO_VOIGT,
            U4F_SAT_FWHM_RANGE,
            linked_to="satellite_u4f72",
            linked_offset_range=U4F_SPLITTING_RANGE,
            area_ratio=U4F_RATIO_DEFAULT,
            area_ratio_range=U4F_RATIO_RANGE,
            share_parent_params=("gl_ratio", "fwhm"),
        )
        # Free pair separation, everything else still tied (U1b).
        sat_52_freesep = slot(
            "satellite_u4f52", U4F_SAT52_WINDOW, LineShape.PSEUDO_VOIGT,
            U4F_SAT_FWHM_RANGE,
            linked_to="satellite_u4f72",
            linked_offset_range=U4F_SATPAIR_SEP_RANGE,
            area_ratio=U4F_RATIO_DEFAULT,
            area_ratio_range=U4F_RATIO_RANGE,
            share_parent_params=("gl_ratio", "fwhm"),
        )

        # Robustness variant: satellites ride their own mains independently
        # (free amplitudes, independent offsets — no pair linkage).
        sat_72_free = slot(
            "satellite_u4f72", U4F_SAT72_WINDOW, LineShape.PSEUDO_VOIGT,
            U4F_SAT_FWHM_RANGE,
            linked_to="main_u4f72",
            linked_offset_range=U4F_SAT_OFFSET_RANGE,
        )
        sat_52_free = slot(
            "satellite_u4f52", U4F_SAT52_WINDOW, LineShape.PSEUDO_VOIGT,
            U4F_SAT_FWHM_RANGE,
            linked_to="main_u4f52",
            linked_offset_range=U4F_SAT_OFFSET_RANGE,
        )

        return [
            CandidateModel(name="U0_mains", background=U4F_BACKGROUND,
                           slots=(main_72, main_52)),
            CandidateModel(name="U1_mains_satpair", background=U4F_BACKGROUND,
                           slots=(main_72, main_52, sat_72, sat_52)),
            CandidateModel(name="U1b_mains_satpair_freesep",
                           background=U4F_BACKGROUND,
                           slots=(main_72, main_52, sat_72, sat_52_freesep)),
            CandidateModel(name="U2_mains_satfree", background=U4F_BACKGROUND,
                           slots=(main_72, main_52, sat_72_free, sat_52_free)),
        ]


register_region(U4fModule())
