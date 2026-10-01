# Background math implementation round 10 — run B (commit ad80814; codex exec, reasoning high)

Reviewed `ad80814`, read-only.

1. **MAJOR — Manual interpolation still certifies a finite but incorrect curve after catastrophic cancellation.** [fitting.py:626](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:626), [templates/index.html:15085](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:15085).

   Load Manual anchors `(-1e20, 1e20)` and `(300, 1)`, with energies `280..290`. Their affine background is approximately `[21,20,…,11]` counts. Both implementations instead return **eleven zeros**. Every intermediate remains finite, so round 9’s overflow checks miss the cancellation.

   Reproduced through the page producer, spectrum saver, restore check, and `/api/fit`: the page reports `converged:true`, saves zeros without a failure, and restores them; the API returns **HTTP 200, `success:true`**.

   With counts `[50,50,60,100,500,100,60,50,50,50,50]`, fitting one Gaussian gives area **703.46**, versus **650.97** against the intended line. This violates owner item 2 and changes fitted and saved numbers. The interpolation needs a numerical-validity check beyond finiteness, with refusal when it cannot satisfy the affine relation.

Verification: **84 Python and 63 JavaScript tests passed** using read-only wrappers; two filesystem-dependent Python tests were excluded. **64 loader round trips** covered all eight methods, both formats and both orders. The four measurement summaries, **3/62/56 census**, **376 Smart comparisons**, and **2,424 upload-rounding cases** reproduced. The specific round-9 overflow refusal works. Neither dispositioned pre-existing issue is re-raised. Full browser and full-suite runs were not repeated.

**VERDICT: NO-GO.**
