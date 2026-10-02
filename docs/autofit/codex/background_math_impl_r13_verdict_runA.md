# Background math implementation round 13 — run A (commit 81234c4; codex exec, reasoning high)

Reviewed `81234c4`, read-only. **Two MAJOR findings.**

1. **MAJOR — Tougaard certifies cancellation error exceeding the predicate.** [fitting.py:1001](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:1001), [index.html:4661](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4661).

   Full window, endpoint averaging 1:

   ```text
   E = [280, 281, 282, 283]
   I = [200, 300, 0.73, 300]
   ```

   At 282 eV, both implementations return **4840194.861419698**. Exact Fraction evaluation of the stated sum on those same binary inputs gives **4840194.861336416**.

   The error is **8.32829e-5**, against an allowed **2.9927e-10**—approximately **278,287 times the tolerance**. All intermediates remain finite. Cancellation corrupts the high-edge loss sum; anchoring amplifies that error. The certificate accepts whenever that sum is nonzero, without bounding the resulting error.

   Reproduced in both energy orders, through `/api/background` returning HTTP 200, and through the page’s producer, save function and restore check. Numerical error must be bounded against the span-relative predicate; otherwise refuse.

2. **MAJOR — Shirley-family certificates round away an out-of-tolerance residual.** [fitting.py:1022](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:1022), [index.html:4677](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4677).

   Full window, endpoint averaging 1:

   ```text
   E = [0, 1, 2, 3]
   I = [1000000000000, 1000000000004,
        1000000000008, 1000000000002]
   ```

   Shirley, Smart and Smart experimental return the background with exact offsets from `1e12`:

   ```text
   [0, 1451/4096, 5547/4096, 2]
   ```

   Both certificates report **residual 0**. Evaluating the defining relation exactly at this returned background gives a maximum residual of **57/86331392 ≈ 6.60247e-7**. The span is **8**, so the allowance is **8e-12**—the error exceeds it by approximately **82,531 times**.

   Adding the large baseline rounds the target back onto the candidate before subtraction. Both energy orders certify and restore; the server returns HTTP 200 and the page saves without a failure. Shirley + linear also falsely certifies this input. The residual calculation must preserve enough precision to enforce the stated predicate or refuse.

Verification: **86 Python checks passed**, one filesystem-dependent fixture was blocked; **54 JavaScript checks passed**. All four measurement summaries, the **3/62/56 census**, **376 Smart comparisons**, and **2,424 upload-rounding measurements** reproduced. API probes used in-memory session data. Full browser and full suites were not rerun.

The round-12 overflow refusal works. Neither finding re-raises the accepted large-span rounding case, legacy pin, or dispositioned issues. No files changed.

**VERDICT: NO-GO.**
