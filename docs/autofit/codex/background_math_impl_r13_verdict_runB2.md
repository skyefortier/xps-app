# Background math implementation round 13 — run B2 (commit 81234c4; codex exec, reasoning high; rerun of B, which hit model capacity)

Reviewed **`81234c4`**, read-only. Findings and line numbers refer to that commit; concurrent workspace edits were excluded.

1. **MAJOR — Tougaard certifies cancellation errors outside the predicate.** [fitting.py:1001](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:1001), [templates/index.html:4661](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4661).

   Select Tougaard, averaging 1, full window:

   ```text
   E = [280, 281, 282, 283]
   I = [2, 3, 0.0072794, 3]
   ```

   Both sides certify `[2, 2, 16345490.482835678, 3]`. Exact Fraction evaluation of the **same input doubles** gives **16345490.46488903** at the third point. The error is approximately **0.60% of the intensity span**, far outside `BG_REL_TOL = 1e-12`.

   All intermediates remain finite. The certificate accepts any nonzero high-edge loss sum without checking the amplified numerical error. This is distinct from the accepted, within-predicate `1e20` case.

2. **MAJOR — Shirley-family underflow produces false zero-residual certificates.** [fitting.py:409](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:409), [templates/index.html:4469](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4469).

   Select Shirley, averaging 1, full window:

   ```text
   E = [280, 281, 282, 283]
   I = [1e-200, 5e-200, 4e-200, 2e-200]
   ```

   Both sides return the constant **`2e-200`**, certified with residual zero. Evaluating the defining relation on that returned curve gives approximately `[1, 1.3, 1.8, 2] × 1e-200`: an error of **25% of the span**.

   Multiplication before division underflows; the certificate repeats the corrupted arithmetic. The same input also falsely certifies Smart, Smart experimental, and Shirley + linear, with equation errors around **17% of the span**.

For both findings, the production page functions certify, save without `backgroundFailure`, and accept restoration in both energy orders. `/api/background` returns **HTTP 200** with the incorrect curve.

Verification: **86 Python and 64 JavaScript checks passed** against committed code. Four measurement summaries, the **3/62/56 restore census**, **376 Smart comparisons**, and **2,424 upload-rounding cases** reproduced. CI’s floor is **538**. Two filesystem-dependent Python tests were excluded; full browser and full-suite runs were not repeated. No files changed by this review.

**VERDICT: NO-GO.**
