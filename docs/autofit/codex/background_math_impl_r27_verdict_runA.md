# Background math implementation — Codex round 27, run A (commit fba30f5)

Reviewed `bg-math-implement` at `fba30f5`, read-only. **Two MAJOR findings.**

1. **MAJOR — The step cap drops a uniquely identifiable current fit.** [templates/index.html:10257](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10257)

   Backend-verified reproducer: fit ten samples at 281 eV followed by 280.9…280.0 eV, using Gaussian `(center=280.5, FWHM=0.5, amplitude=1e6)`, alternating ±0.01 count noise, and background None. Include ten excluded samples at 281.00001 eV with counts `fittedY[0] + j × 1e-5`. Save the keyed, full-precision fit using normal project rounding.

   The fit succeeds with RMSE **0.010090351823**. Every alternative reading reduces RMSE by at least **0.0002465**, so the original reading is uniquely identifiable. However, too-small failures cannot enter the revised memo, and the search exhausts its **86,016-step budget**, incorrectly reporting ambiguity and dropping the fit.

   **Removing only the step cap in memory restores it as current after 381,336 steps.** The round-26 memo correction fixes dominance but leaves this reachable failure.

2. **MAJOR — Unrelated raw counts inflate RMSE agreement and drop a current fit.** [templates/index.html:10147](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10147)

   Backend-verified reproducer: eleven samples at `280 + 0.1i`, exactly matching Gaussian `(center=280.5, FWHM=0.5, amplitude=1000)`, background None, fitted RMSE **0**. Include an excluded sample at 279.99999 with count `fittedY[0] + 1e-7`, plus an unrelated sample at 300 eV with intensity `1e8`. Preserve the key, full-precision marker, and project-rounded counts.

   The unrelated sample raises the tolerance from approximately **5.33e-12 to 8.88e-8**, admitting the wrong reading’s **3.02e-8** RMSE. Reload reports “cannot be told apart” and drops the unchanged fit. Removing only the unrelated sample restores it as current. That sample cannot participate in either reading and contributes no rounding error to the recorded RMSE.

Verification: **84 Python tests and 66 JS tests passed**, with in-memory accommodations for sandbox import restrictions. Census reproduced **0 current / 81 stale / 40 peaks-only**; Python twin verdicts agree. All five measurement summaries and student-note figures reproduce. All **202** upload inputs, seeds, and background arrays match the measurement records. The narrowed test checks actual draws; CI floor is **563**.

Full/browser suites were not rerun. No files changed.

**VERDICT: NO-GO**
