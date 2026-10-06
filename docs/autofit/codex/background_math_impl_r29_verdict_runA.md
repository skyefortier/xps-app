# Background math implementation — Codex round 29, run A (commit dedeace)

Reviewed `dedeace`, read-only. **One MAJOR finding.**

1. **MAJOR — Spectrum reload mistakes exact saved values for rounded project data and drops a current fit.** [templates/index.html:10106](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10106), [count precision:10125](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10125)

   Save Spectrum preserves full-precision energies and counts, but restore infers rounding from their numerical appearance.

   Backend-verified reproducer: energies `[280, 280.5, 281, 281.5, 282]`, counts `[62.5, 500, 1000, 500, 62.5001]`; Gaussian with locked center `281`, locked FWHM `1`, fitted amplitude; background None. Include an excluded raw neighbor `(279.99999, 62.5)` below the ROI.

   Executing the production save/load functions in memory saves this fit as current, then **drops it as “cannot be told apart.”** The invented ±0.00005 eV allowance admits the neighbor despite the exact saved energy identifying `280`. Using exact spectrum energies restores the fit.

   A second variant, neighbor intensity `62.5000058823438`, also exposes the six-significant-figure count heuristic: honoring the spectrum’s exact counts restores it.

   These are synthetic near-duplicate sampling cases, involving only two readings—not search-budget exhaustion. Preserve the file format’s precision when identifying samples.

Verification: census **0 current / 81 stale / 40 peaks-only** and Python twin reproduce; all five measurement summaries and student-note figures reproduce. All **202** upload round trips, request seeds, background arrays and net areas match. **10,000** search comparisons against a variant without numerical pruning or memoization found no discrepancy.

**145 focused JS tests and 60 Python tests passed.** The narrowed scattered-starts test checks actual draws and passes. CI floor is exactly **566**. Full-suite verification was limited by read-only filesystem restrictions; three Python fixtures were blocked. No files changed.

**VERDICT: NO-GO**
