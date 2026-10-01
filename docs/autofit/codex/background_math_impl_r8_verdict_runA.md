# Background math implementation round 8 — run A (commit b4c5e25; codex exec, reasoning high)

Reviewed `b4c5e25`, read-only.

1. **MAJOR — Changing charge correction makes stacks subtract from different samples.** [templates/index.html:9642](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9642).  
   Use `E=[5,4,3,2,1,0]`, counts `[900,10,40,35,20,5]`, ROI `[1,4]`, linear background. Fit successfully, then change charge correction from 0 to 1 eV and open the stack’s background-subtracted view. The fit grid/background remain frozen, but alignment uses the **current** correction. It selects counts `[900,10,40,35]` instead of `[10,40,35,20]`. The trace becomes **`[890,-3.333,23.333,15]` instead of `[0,26.667,18.333,0]`**. Reproduced through the production correction and stack-dataset functions. Use frozen fit counts or preserved fit-time sample identities; an exact energy match under a different correction is insufficient.

2. **MINOR — Empty linear/manual windows return an internal error instead of a plain refusal.** [fitting.py:555](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:555).  
   For an existing session, request `/api/background` with `start_idx:1,end_idx:1` and method `linear` or `manual`. Unconditional endpoint indexing raises `IndexError`; both return **HTTP 500, “Internal background error”**. Reproduced with Flask’s test client and in-memory session data. No invalid curve is returned, so this alone would not prevent GO.

Verification: **82 Python and 62 JS checks passed**. All four measurement summaries and the **3/62/56 census** reproduced exactly; **256 loader round trips**, **376 Smart comparisons**, and **104,207 finite-double `_fmt3` comparisons** passed. Full browser suites were not rerun. No files changed.

**VERDICT: NO-GO.**
