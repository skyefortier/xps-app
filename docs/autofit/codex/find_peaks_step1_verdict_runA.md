# Find Peaks math-first architecture — Step 1 review, Run A

Reviewed commit: 854c40a ("feat(autofit): decouple CWT detector
characterization from the chemistry constant"), branch
feature-autofit-stage2.

Sandbox note (from the run): pytest/scipy/olefile unavailable in the
Codex sandbox; findings are from diff/static trace plus a standalone
NumPy reconstruction of the detector for the background-step probe.

## Findings

1. MAJOR: D0 fit bounds changed indirectly, despite the claimed scope boundary.
[autofit/candidates.py](/Users/skyefortier/xps-verify/autofit/candidates.py:756) replaces a coincident local-max half-height width with the CWT ridge width, and [autofit/candidates.py](/Users/skyefortier/xps-verify/autofit/candidates.py:533) / [autofit/candidates.py](/Users/skyefortier/xps-verify/autofit/candidates.py:550) turn that width into the `D0_detected` slot's free-parameter bounds. But the commit documents that sharp, high-SNR peaks can have monotonic `prom_z` versus scale and chase the new ROI ceiling, not their true width. Concrete failure: a narrow 1.2 eV peak in a wide ROI can inflate `D0_detected`'s upper FWHM bound from the old effective ~6 eV to much larger values, letting D0 absorb background/tails or nearby structure before migration step 6's degeneracy-control work. The stress-test winner flip is already evidence this is fit-visible, not just characterization-visible. This is effectively a fourth width-bound role of the retired detector ceiling.

2. MAJOR: The background false-positive guard does not stress the named risk.
[tests/autofit/test_cwt_width_ceiling.py](/Users/skyefortier/xps-verify/tests/autofit/test_cwt_width_ceiling.py:196) only tests a 181-point ROI with flat/slope/smooth sigmoid backgrounds and allows `fp_rate <= 0.15`. The zero-mean Ricker argument covers constant/linear backgrounds, but not sharp steps or sharper sigmoid/edge-like bad backgrounds; those produce real wavelet curvature. In a low-point ROI, the new derived ladder/density can provide linked scales for a central step that the old filtered fixed ladder did not. Concrete failure scenario: a ~30-point, 0.1 eV-step no-peak ROI with a background step can emit high-prominence ridge detections, while this test never exercises that shape or point-count regime. The current tolerance is too loose to catch a meaningful regression even if a missing background family starts firing.

3. MINOR: The "main peak still sharp" regression test does not assert sharpness.
[tests/autofit/test_cwt_width_ceiling.py](/Users/skyefortier/xps-verify/tests/autofit/test_cwt_width_ceiling.py:175) says the dominant real N 1s peak must retain an "essentially unchanged, narrow width estimate," but the body only asserts `prom_z > 500`. A regression where the main peak's `fwhm_est_ev` chases the derived ceiling would pass. This matters because that inflated width is exactly what feeds the D0 bound path above.

VERDICT: NO-GO

## Claude's post-hoc verification (2026-07-21)

- Finding 1 CONFIRMED against the real repo (not just traced): `PoolFeature.fwhm_est` (candidates.py:857) is populated directly from the raw, unclipped `RidgeFeature.fwhm_est_ev` (candidates.py:760, 768) — completely independent of `fwhm_clip`/(ii). `build_detection_candidate` sizes `detected_peak_i`'s `fwhm_range` ceiling directly from this value. This is a real, NEW consequence of step 1(i) alone: a 4th consumption path the (i)/(ii)/(iii) scope split did not name.
- Finding 2's specific numeric claim (step background, n=30: FP 0.00→1.00) reproduced exactly against the real repo code (not Codex's reimplementation). Comparison against the parent commit (877bb31) shows this pathology is **pre-existing**: FP rate is already 1.000 at n>=40 under the OLD fixed ladder too, identically. Step 1 only extends it to one additional small-ROI boundary case (n=30). The FP-guard test's narrow coverage (one ROI size, tolerant threshold) is independently valid to fix regardless.
- Finding 3 MINOR: confirmed as written; already independently flagged in PROGRESS.md's step-1 entry before this review ran.
