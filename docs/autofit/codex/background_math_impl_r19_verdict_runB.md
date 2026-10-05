# Background math implementation — Codex round 19, run B (commit 59e0610)

Reviewed `59e0610`, read-only. **Three MAJOR findings:**

1. **MAJOR — Project-save rounding selects the wrong samples for an unchanged fit.** [templates/index.html:10075](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10075)  
   Reproducer: energies `280 + 0.001i`, `i=0…9`; counts exactly a Gaussian with center `280.004`, FWHM `10`, amplitude `1e6`; background None; fitted ROI `280…280.003`, RMSE zero. Project saving rounds all four stored counts to `1000000`. Restoration then selects indices `[3,4,5,6]` instead of `[0,1,2,3]` and reports **100% background-stale**. The scoring treats rounded counts as exact and ignores the available RMSE whenever those counts exist.

2. **MAJOR — Charge shifts still misalign noncontiguous samples in unsorted records.** [templates/index.html:10058](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10058)  
   With raw energies `[0,99,1,2,88,3,4]`, fitting ROI `1…3` uses indices `[2,3,5]`. Apply charge correction `+1`, shifting the ROI and peaks accordingly, then save/reload. The correct offset subsequence is excluded because offset candidates must be contiguous. Restoration selects `[3,5,6]` instead, despite stored counts identifying the original samples. A Gaussian with unchanged None background reloads **100% background-stale**. Reproduced with reversed record order too.

3. **MAJOR — Stale-spectrum saves contain residuals inconsistent with their preserved envelope.** [templates/index.html:11449](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:11449)  
   Restore a fit made against constant manual background `10` when today’s anchors give `20`, then Save Spectrum without editing. The production saver correctly preserves background `10` and the original envelope, but writes residuals computed against background `20`. Every saved residual is therefore **10 counts wrong relative to the saved envelope**. The `_ownFit` branch must preserve corresponding residuals and sample alignment as well.

Verification: the page census and serialized Python twin reproduce exactly: **10 current / 71 stale / 40 peaks-only**. Measurement analysis and student-note numbers reproduce; all 202 targets parse to identical inputs before and after the upload-format fix. The narrowed draws test passes and actually compares the draws. **78 JS and 91 Python checks passed**; two HTTP fixtures were blocked by read-only permissions, and the longer Python run was stopped for budget. CI floor is exactly **543**. No files changed.

**VERDICT: NO-GO.**
