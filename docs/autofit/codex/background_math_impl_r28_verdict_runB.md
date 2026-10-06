# Background math implementation — Codex round 28, run B (commit a0aafb9)

Reviewed `bg-math-implement` at `a0aafb9`, read-only. **One MAJOR finding.**

1. **MAJOR — An RMSE-impossible sample still widens the tolerance and drops an identifiable current fit.** [templates/index.html:10219](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10219)

   Backend-verified reproducer: eleven samples at `280 + 0.1i`, exactly matching Gaussian `(center=280.5, FWHM=0.5, amplitude=1000)`, background None. The fit succeeds with RMSE **0**. Include two excluded raw samples before the ROI:

   - `279.99998 eV`, intensity `1e6`.
   - `279.99999 eV`, intensity `62.5 + 1e-9`.

   Load an older spectrum save carrying its fit key and `uploadFull`, but predating `fitCounts`.

   The million-count sample enters the backward table, although its residual makes it impossible under the recorded RMSE. Its magnitude nevertheless raises the shared tolerance from **5.33e-12 to 8.93e-10**, admitting the other neighbor’s incorrect reading, whose RMSE is **3.02e-10**. Restore reports “cannot be told apart” and drops the unchanged fit.

   **Removing only the million-count neighbor restores the fit as current.** This is a synthetic boundary-sampling case, but a reachable saved-file input. It examines only three readings in approximately **2 ms**; neither bounded-search cap is involved. Round 27’s magnitude restriction therefore remains insufficient.

Verification: census and Python twin reproduce exactly (**0 / 81 / 40**); all five measurement summaries and student-note figures reproduce. All **202** upload inputs, seeds, and background arrays match. **127 focused JS tests passed**; **114 Python tests passed**, with four filesystem-blocked fixtures before interrupting the longer run. An additional **2,000** small-search comparisons found no discrepancy when disabling sum pruning and memoization. The narrowed test still compares actual draws; CI floor is **565**.

No files changed. Full/browser suites were not completed.

**VERDICT: NO-GO**
