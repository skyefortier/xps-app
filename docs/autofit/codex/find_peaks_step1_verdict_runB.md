# Find Peaks math-first architecture — Step 1 review, Run B

Reviewed commit: 854c40a ("feat(autofit): decouple CWT detector
characterization from the chemistry constant"), branch
feature-autofit-stage2.

## Findings

1. **MAJOR** [autofit/engine.py](/Users/skyefortier/xps-verify/autofit/engine.py:1907): `PreseedSpec.fwhm_init` is still not used to initialize `_preseed_augmented` fit slots. The slot is built with `fwhm_range=(PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX)`, and `_default_params_from_slots` initializes width from the slot midpoint, not from the seed's `fwhm_init` ([autofit/engine.py](/Users/skyefortier/xps-verify/autofit/engine.py:517)). So step 1(ii) currently decouples a surfaced diagnostic/payload value, not "the optimizer's starting estimate" as claimed. Concrete failure: a broad curvature seed can report `fwhm_init=4.5 eV`, but grammar augmentation still starts that preseed slot near `1.25 eV` under a `0.5-2.0 eV` fit bound.

2. **MAJOR** [tests/autofit/test_cwt_width_ceiling.py](/Users/skyefortier/xps-verify/tests/autofit/test_cwt_width_ceiling.py:210): the false-positive guard is too permissive for the explicitly named risk. It only checks one 181-point ROI size and allows `fp_rate <= 0.15`, while the documented baseline is about `1.7-4.4%`. A regression that increases featureless detections from ~2% to 14% would still pass. It also does not cover low-point ROIs, quadratic/concave backgrounds, steps, or edge sigmoids, where the wider scale ladder is most likely to resolve broad non-peak curvature.

3. **MINOR** [autofit/candidates.py](/Users/skyefortier/xps-verify/autofit/candidates.py:160): `cwt_scale_range_ev()` overstates the actual usable detector ceiling. `_cwt_max_sigma_pts` uses the continuous `(n-1)/(2*TRUNC)` bound, but the detector later applies `ceil(TRUNC*s)` and then excludes `radius + 2` margins ([autofit/candidates.py](/Users/skyefortier/xps-verify/autofit/candidates.py:251), [autofit/candidates.py](/Users/skyefortier/xps-verify/autofit/candidates.py:274)). For even-length or tiny ROIs, the public ceiling can include a top rung that is filtered out or has no valid interior maxima. This weakens the "same exact kernel-fits-in-window bound" provenance claim.

Confirmed scope isolation: `_preseed_augmented`'s free-parameter bound is untouched and still uses `PROPOSAL_FWHM_MIN/MAX`; `build_detection_candidate`'s `DETECTION_SLOT_FWHM_HI_FRACTION` path is unchanged and is a separate mechanism.

VERDICT: NO-GO

## Claude's post-hoc verification (2026-07-21)

- Finding 1 CONFIRMED against the real repo. Traced every consumption site of `.fwhm_init` in engine.py: the ONLY place a spec's `fwhm_init` sets an actual lmfit parameter value is `_initial_params_for_augmented` (engine.py:2150), which takes a `ProposalSpec` (the residual-guided proposal-pass mechanism) — a completely different code path from `_preseed_augmented`/`PreseedSpec`. `_preseed_augmented` (unmodified by this commit) never references `spec.fwhm_init` at all. This gap is **pre-existing** — present identically before step 1, since `_preseed_augmented` was not touched by this diff. Step 1(ii) computes a more honest `fwhm_init` value and surfaces it in diagnostics, but that value was never wired to the optimizer's starting guess for preseed slots, before or after this commit. The claim in the new code comment ("the starting estimate handed to the optimizer") is therefore inaccurate for this consumption path and needs correcting, independent of whether the underlying gap gets fixed.
- Finding 2: same false-positive-guard weakness Run A also flagged independently — corroborating signal, worth fixing regardless of the specific step-background numeric case (see runA's verdict file for that reproduction).
- Finding 3: plausible on inspection (the derivation is a continuous approximation of a bound the detector applies with ceiling+margin exclusions afterward); not independently re-derived in detail, but the direction of the discrepancy (public ceiling can slightly overstate what's truly usable) is a conservative-direction gap, not a silent-degradation one.
