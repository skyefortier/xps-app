# Background math implementation round 11 — run B (commit 60025c7; codex exec, reasoning high)

Reviewed `60025c7`, read-only.

1. **MAJOR — Linear and Manual’s no-anchor fallback still certify an incorrect finite curve.** [fitting.py:579](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:579), [templates/index.html:4928](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4928).

   Use ascending energies `[-1e20,280,281,…,290,300]` and counts `[1e20,50,50,60,100,500,100,60,50,50,50,50,1]`, with the full background window. Select Linear, or Manual without anchors.

   The endpoint-defined line rounds to **21,20,…,11** at energies 280–290 and **1** at 300. Both implementations instead return **zero at all those points**. The slope rounds to −1; subsequent subtraction and cancellation erase the smaller values. Every intermediate remains finite, so the finiteness guard accepts the result.

   Reproduced through production functions:
   - Page reports `converged:true`.
   - Spectrum saving writes the incorrect zeros with `backgroundFailure:null`.
   - Restoration accepts that stored background.
   - Server `run_fit` returns `success:true` against it.

   Round 10 fixes interpolation with two or more manual anchors, but leaves this reachable affine-background path unchecked. Evaluate the line reliably or report failure when its defining statement cannot be satisfied.

Verification: **75 Python and 61 JavaScript tests passed** using read-only wrappers; **128 loader cases** covered every method, both formats and both orders. The new manual evaluator passed **15,000 bitwise value comparisons**, **5,006 decompositions**, and **13,392 rounding probes**, including ties around every finite power of two. A 4,000-point/12-anchor evaluation averaged **36 ms page / 67 ms server**.

All four measurement summaries, the **3/62/56 census**, **376 Smart comparisons**, and **2,424 upload-rounding cases** reproduced. The two dispositioned issues remain unchanged. Full HTTP/browser suites were not rerun. No files changed.

**VERDICT: NO-GO.**
