# Background math implementation — Codex round 19, run A (commit 59e0610)

Reviewed `59e0610`, read-only. **Three MAJOR findings:**

1. **MAJOR — Project-save rounding can select the wrong samples.** [templates/index.html:10075](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10075)  
   On energies `0…15`, fit ROI `2…5` with a Gaussian `(center=3.5, FWHM=2, amplitude=10000)` over background `1000000.4`. Put a second run at `10…13` matching the first run’s rounded background-plus-net counts. The production project saver rounds away the identifying difference; restoration chooses `10…13`, moves the fit eight energy steps, and falsely reports **0.833884% background staleness**. Alignment treats rounded counts as exact and ignores the available RMSE evidence.

2. **MAJOR — Restored-stale spectrum saves contain incorrect residuals.** [templates/index.html:11449](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:11449)  
   Restore an unchanged Gaussian fit made against background `10`, with today’s manual anchors giving `20`. Save Spectrum correctly preserves background `10` and the historical envelope, but writes residuals calculated against background `20`. Reproduced through the production saver: at the peak center, `rawIntensity − fittedY = 0`, while the saved residual is **−10**. Every residual is displaced by ten counts.

3. **MAJOR — Charge shifts drop checkable fits on noncontiguous ROI samples.** [templates/index.html:10058](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10058)  
   Use raw energies `[0,9,1,9,2,9,3,9,4,9,5]`, a Gaussian, background `none`, and ROI `1…4`. The fitted samples are indices `[2,4,6,8]`. After a `0.5` charge correction, with peaks and ROI shifted accordingly, restoration rejects the fit as “not points of its raw data.” Those samples remain identifiable, but offset matching considers only contiguous runs. This violates §7’s retention of checkable historical fits.

Verification: census **10/71/40**, Python twin, and `final_analysis.json` reproduced exactly; student-note measurements reproduced. All **202** upload inputs remain unchanged. The narrowed test still records the actual four scattered starts; CI floor is **543**.

**71 targeted JS checks and 134 Python checks passed.** Four Python fixtures were blocked by read-only permissions; the remaining run was stopped for the time budget. No files changed.

**VERDICT: NO-GO.**
