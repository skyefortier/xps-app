# Background math implementation — Codex round 20, run A (commit ae9e04e)

Reviewed `ae9e04e`, read-only. **Two MAJOR findings:**

1. **MAJOR — RMSE roundoff can select the wrong samples.** [templates/index.html:10094](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10094)  
   The server computes residuals as `(counts − background) − model`; alignment uses `counts − fittedY`. Their rounding differs, but candidate ranking treats every difference as decisive.

   Reproducer: energies `[0,1,2,3,10,11,12,13]`; fit `0…3` with a locked Gaussian `(center=1.5, FWHM=2, amplitude=100)`, manual background `10000`, and residuals approximately `[1,-2,3,-4]`. Give the second run corresponding counts perturbed by `[0,+u,-u,-u]`, where `u=2^-39`. The actual successful server fit stores RMSE `2.738612787525718`; alignment recomputes `2.7386127875258306` for the correct run and `2.7386127875256645` for the wrong run. It selects `10…13` and falsely reports **0.833884% background staleness**. Reproduces with both full-precision and project-rounded stored counts.

2. **MAJOR — Greedy rounded matching excludes a valid exact sample alignment.** [templates/index.html:10067](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10067)  
   Reproducer: raw energies `[0,1.00001,1.00002,2.00002,3.00002,4.00002]`, Gaussian counts `(center=2, FWHM=2, amplitude=100)`, background None, ROI `1.000015…3.1`. The fit uses indices `[2,3,4]`. Apply charge correction `+0.5`, then save/reload.

   At the correct offset, the matcher consumes `1.00001` because its rounded energy matches, excluding the exact `1.00002` sample. It selects `[1,3,4]` and falsely reports **100% background staleness**, despite stored counts/RMSE identifying the correct samples. Reproduces with full-precision and four-decimal saved energies.

Verification: census **10/71/40**, Python twin, measurement analysis, and student-note numbers reproduced. All **202** upload inputs, seeds, and background curves match the measurement records. The narrowed test still compares actual draws; CI floor is **545**. **63 JS and 103 Python checks passed**; eight Python fixtures required forbidden writes, and the longer run was stopped for budget. No files changed.

**VERDICT: NO-GO.**
