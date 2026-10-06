# Background math implementation — Codex round 27, run B (commit fba30f5)

Reviewed `fba30f5`, read-only. **One MAJOR finding.**

1. **MAJOR — The step cap drops a uniquely identifiable fit when alternative readings fail below the RMSE interval.** [templates/index.html:10257](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10257)

   Backend-verified reproducer: eighteen samples at `280 + 0.1i`, Gaussian `(center=280.85, FWHM=1, amplitude=1000)`, manual background `12345.6`, and alternating `±0.02` count noise. Fit with the legacy two-decimal upload and save a keyless project with normal count rounding. The successful fit’s RMSE is **0.0202539170556**.

   Include another raw region containing two samples at each `300 + 0.1i`, with counts `fittedY[i]` and `fittedY[i] + 0.001`. Both choices satisfy the rounded count evidence, but all **262,144** alternative readings have RMSE too small to agree—even with the legacy `0.005` allowance.

   The backward least-remainder and `ssMax` checks cannot eliminate these lower-side failures. Round 26 correctly prevents memoising them, but their expansion exceeds the **77,824-step** budget. Restore therefore reports “too many sets of samples … to be told apart” and drops the fit.

   **Raising only the cap in memory restores the unique original reading**, marked stale-unconfirmed with `matches: true`. This violates §7’s retention of checkable historical fits. Budget exhaustion still does not establish ambiguity.

Verification: census reproduced exactly at **0 current / 81 stale / 40 peaks-only**; Python twin verdicts agree. All five measurement summaries and student-note figures reproduce. All **202** upload inputs parse bit-exactly; request seeds and background arrays match committed measurements. The narrowed scattered-starts test still checks actual draws; CI floor is **563**.

**114 targeted JS checks passed.** Python testing reached **84 passed**, with two filesystem-blocked fixture errors, before stopping the longer run. Full/browser suites were not completed. No files changed.

**VERDICT: NO-GO**
