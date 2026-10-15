**Three MINOR findings remain. No BLOCKER or MAJOR found.**

1. **Round-4 status**

   - **Position-scale overflow: partially resolved.** The original reproductions are refused by `n × span`, but that bound misses a scale assembled from different operands; see item 2. [app.py:1465](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1465)
   - **Breadth-first versus recursive link traversal: resolved for validated, uniquely named chains.** The new walk follows individual chains and stops cycles. Duplicate identifiers can bypass link validation, however; see item 2. [app.py:1484](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1484)
   - **Server-produced extreme held bounds: remains an arithmetic compatibility limit.** I reconfirmed a successful fit with fixed FWHM bounds `[-1e308, 1e308]` whose self-comparison returns 400. This follows the finite-span restriction. [fitting.py:1781](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:1781), [app.py:1477](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1477)

2. **Remaining accepted-input paths**

   **MINOR — cross-operand position scale still overflows.** Validation bounds each response separately, but the comparator measures **both components using `a`’s grid**. [app.py:1524](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1524), [same_fit.py:131](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:131)

   Reproduction: `a.energy = [0, 8e307]`, with zero component curves; `b.energy = [0, 0, 0]`, with component curves `[1, 1, 1]`. Resize each response’s other arrays accordingly. Both pass validation: their bounds are `1.6e308` and zero. During comparison, `a` supplies no component width, while `b` supplies `3 × 8e307 = inf`. The endpoint returns **200**, using that infinite position scale. It reports **`same: false` because of the length differences**, so this reproduction does not falsely equate the complete responses. [same_fit.py:112](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:112)

   **MINOR — duplicate peak IDs hide invalid links.** `exprs[key]` overwrites an earlier expression with the same synthesized parameter name. Append a duplicate peak whose FWHM expression is `p1_center`; the original peak’s FWHM expression can then be `nothing_here * 2` or `p1_center + p1_fwhm` without refusal. I reproduced **200 on either side and 200, `same: true` on both**. Without the duplicate, both expressions return 400. [app.py:1472](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1472), [app.py:1480](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1480)

   I reproduced no additional input-driven HTTP 500.

3. **Yes, a valid page-supported fit can now be refused.**

   **MINOR — scientific notation is mistaken for another parameter.** The offset control accepts `0.00001`; the fitter writes `p1_center + 1e-05`. The regex extracts `p1_center` and `e`, then rejects the expression. I reproduced `/api/fit` returning **200, `success: true`**, followed by self-comparison returning **400, “not one a fit writes.”** [templates/index.html:6819](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/templates/index.html:6819), [fitting.py:1730](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:1730), [app.py:1485](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1485)

4. **The tests detect their named checks, but miss these cases.**

   All **21 refusal cases passed**, and individually disabling their corresponding checks in memory made **all 21 fail**. They omit unequal-length cross-operand scales, duplicate identifiers, and valid exponent-form expressions. [tests/test_seal_1d_compare.py:165](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:165)

   Focused validation: **71 passed, 1 skipped**, using in-memory session storage. The 328-record test skipped because `SEAL_1B_RECORDS` was unavailable. No files changed. [tests/test_seal_1d_compare.py:193](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:193)

VERDICT: NO-GO
