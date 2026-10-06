# Background math implementation — Codex round 30, run B (commit 6bd34db)

Reviewed `6bd34db`, read-only. **One MAJOR finding.**

1. **MAJOR — Exact spectrum energies still admit a distinguishable neighbor, dropping a current fit.** [templates/index.html:10114](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10114), [10257](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10257)

   `beExact` removes decimal rounding but retains the arithmetic energy allowance—even with zero charge shift, where the saved and raw energies can be compared exactly.

   Concrete reproducer:

   - Fit energies `[280, 280.5, 281, 281.5, 282]`, counts `[62.5, 500, 1000, 500, 62.5001]`.
   - Gaussian: locked center `281`, locked FWHM `1`, fitted amplitude; background None.
   - Include raw neighbor `(279.99999999999994, 62.5)`, excluded by ROI minimum `280`.

   The backend successfully fits this input. Executing production Save Spectrum/load functions in memory saves it **current**, then drops it as **“cannot be told apart.”** The allowance admits the excluded neighbor despite the exact saved energy identifying `280`. An in-memory control using exact matching for this zero-shift case restores the fit.

   This is a synthetic adjacent-double case, atypical of instrument sampling, but reachable and record-identifiable. Only two readings compete; neither search cap is involved.

Verification: census and Python twin reproduce **0 current / 81 stale / 40 peaks-only**. All five measurement summaries and student-note figures reproduce. All **202** upload round trips, seeds, background arrays and net areas match. **20,000** generated comparisons found no discrepancies from disabling numerical pruning and memoization.

**72 focused Python and 103 focused JS tests passed.** The narrowed scattered-starts test checks actual draws and passes. Full suites were not certified under the read-only restrictions. No files changed.

**VERDICT: NO-GO**
