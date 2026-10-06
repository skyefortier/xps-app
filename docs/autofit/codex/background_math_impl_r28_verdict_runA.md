# Background math implementation — Codex round 28, run A (commit a0aafb9)

Reviewed `a0aafb9`, read-only. **One MAJOR finding.**

1. **MAJOR — An unreachable sample still inflates RMSE agreement and drops a current fit.** [templates/index.html:10219](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10219)

   The backward table establishes suffix reachability, but its magnitude calculation includes samples that no complete in-order reading can reach.

   Backend-verified reproducer: fit eleven samples at `280 + 0.1i`, exactly matching Gaussian `(center=280.5, FWHM=0.5, amplitude=1000)`, background None. The backend succeeds with RMSE **0**. Prepend these excluded raw samples, in this order:

   - `(281.00001, 1e8)`
   - `(279.99999, fittedY[0] + 1e-7)`

   Reload a keyed, full-precision spectrum saved before round 25, when spectrum files lacked `fitCounts`. The first prepended sample enters the backward table for the last fitted point, although its position before every possible first point prevents any complete reading from using it.

   Its intensity nevertheless raises the tolerance from **5.329 × 10⁻¹²** to **8.882 × 10⁻⁸**. The second prepended sample then creates an incorrectly agreeing reading with RMSE **3.015 × 10⁻⁸**. Restore reports “cannot be told apart” and drops the unchanged fit.

   Excluding only the unreachable sample from the magnitude calculation restores the unique correct reading. This is a synthetic near-exact fit accepted by the actual backend; only two readings are involved, so search-budget exhaustion is not the cause.

Verification: census reproduced exactly at **0 current / 81 stale / 40 peaks-only**; Python twin verdicts agree. All five measurement summaries and student-note figures reproduce. All **202** upload inputs, request seeds, backgrounds and background net areas match. The narrowed scattered-starts test still checks actual draws; CI floor is **565**.

**96 targeted JS tests passed.** Python testing reached **95 passed**, with two filesystem-blocked fixture errors, before I stopped the longer run. Another **5,000** search comparisons found no discrepancy against an in-memory variant with forward numerical pruning and memoization disabled. Full/browser suites were not completed. No files changed.

**VERDICT: NO-GO**
