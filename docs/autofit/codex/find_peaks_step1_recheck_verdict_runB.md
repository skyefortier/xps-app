# Find Peaks math-first architecture — Step 1 RECHECK, Run B

Recheck of commit 47bf77b ("fix(autofit): apply Skye's dispositions on
step-1 Codex review findings"), against the original NO-GO/NO-GO review of
854c40a (see `find_peaks_step1_verdict_run{A,B}.md`).

## Judgments

1. **Run A finding 1 / D0_detected bound leak: VERIFIED.** No guard was added. `build_detection_candidate` still derives `width` directly from `PoolFeature.fwhm_est` and sets `hi_w = 2.5 * width`. `PoolFeature.fwhm_est` still traces to raw CWT `rf.fwhm_est_ev`. The new step 6 obligation explicitly names the ~2.5x bound scaling, uncapped ceiling-chasing exposure, neighbor absorption risk, and future k+1/statistics responsibility — enough for a future step 5/6 implementer. The rewritten test docstring argues the architecture reason for accepting either winner, not just BIC-tie mechanics.

2. **Run B finding 1 / `fwhm_init` claim: VERIFIED.** `_preseed_augmented` still does not read `spec.fwhm_init`; it only creates slots with `fwhm_range=(PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX)`. The generic initializer still uses slot midpoints. The corrected comments/doc text now accurately say diagnostics-only. The separate proposal-pass exception is also true: `ProposalSpec.fwhm_init` sets a parameter at a different call site.

3. **False-positive guard widening: VERIFIED.** The test now covers 5 sizes and aggregate tolerance `<=0.08`. Arithmetic checks: stated baseline `6/900 = 0.00667`; `0.08/0.00667 = 12x`, so the ">10x headroom" claim is not inflated. 600 deterministic trials, so the assertion allows up to 48 false-positive spectra; a genuine double-digit aggregate FP rate across these ROI sizes would fail. Hard step backgrounds remain deliberately excluded, and that omission is documented with rationale.

4. **Two minor fixes: VERIFIED.** The main-peak test now asserts width, not just `prom_z`; not tautological — a ceiling-chasing result would fail `f.fwhm_est_ev < 0.9 * ceiling`. The `cwt_scale_range_ev` overstatement direction is correct — filters can remove top-rung usability, they cannot create a resolvable scale larger than the reported ceiling.

5. **Regression/scope check: VERIFIED.** `git show --stat 47bf77b` shows exactly the six requested files. `git diff 854c40a..47bf77b -- autofit/candidates.py autofit/engine.py` is comment/docstring only. No production behavior change found beyond documentation.

## Findings

None.

VERDICT: GO

## Note

Run A (see `find_peaks_step1_recheck_verdict_runA.md`) returned NO-GO on
this same commit, catching a real MAJOR (aggregate-only FP assertion can
mask a per-background-kind regression) and a real MINOR (one stale
docstring occurrence) that this run did not surface. Per this session's
"stricter verdict governs" convention, both are fixed in the next commit
regardless of this GO.
