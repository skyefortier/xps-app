# Background math implementation — Codex round 20, run B (commit ae9e04e)

Reviewed `ae9e04e`, read-only. **Three MAJOR findings:**

1. **MAJOR — Rounded project energies exclude the correct offset alignment.** [templates/index.html:10062](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10062)  
   Use raw energies `[0.00004,1.00006,2.00004,3.00006,4.00004,5.00006]`, fit ROI `1…4.1`, then apply charge correction `+0.5` and save a project. The stored fitted energies become `[1.0001,2,3.0001,4]`. Anchoring the offset exactly to the first rounded energy makes the remaining samples fail the rounded comparison. Restoration returns “not points of its raw data” and drops this checkable fit. Reproduced in both record orders.

2. **MAJOR — RMSE rounding noise selects the wrong samples for an unchanged fit.** [templates/index.html:10095](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10095)  
   Reproduced with a successful backend Gaussian fit on energies `2…5`, fixed center `3.5`, FWHM `2`, and manual background `0.1`. Put almost identical counts at `10…13`, lowering only the first count by one floating-point unit. Saved RMSE uses `(counts − background) − model`; restoration uses `counts − envelope`. Their rounding differs: the correct run’s RMSE discrepancy is `1.44e-17`, versus `1.22e-17` for the wrong run. Exact ranking selects `10…13`, despite the correct stored counts, and falsely reports **89.38% background staleness**. Numerically indistinguishable RMSE scores need tie handling.

3. **MAJOR — Restored-stale spectrum saves still mix different models’ curves.** [templates/index.html:11419](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:11419)  
   Fit a Gaussian `(center=2.5, FWHM=1, amplitude=100)` against background `10`. Before saving the project, change amplitude to `200` and manual background to `20`. Reload, then Save Spectrum without further edits. Restoration correctly reconstructs the original background using the key, but the saver evaluates `peakCurves` from today’s peaks. At energy `2`, the file contains **envelope 60, background 10, component 100**; its component area is also doubled. The preserved envelope and exported component curves describe different models.

Verification: **80 targeted JS checks and 142 Python checks passed**; 10 Python fixtures were blocked by read-only permissions. Census **10/71/40**, Python twin, committed measurement analysis, and student-note numbers reproduced. All **202** upload inputs remain bit-exact. The narrowed test passes and compares the actual draws; CI floor is **545**. Full browser suites were not rerun. No files changed.

**VERDICT: NO-GO.**
