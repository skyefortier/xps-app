# Background math implementation round 8 — run B (commit b4c5e25; codex exec, reasoning high)

Reviewed `b4c5e25`, read-only.

1. **MAJOR — Stack alignment still substitutes samples after charge correction and history restore.** [templates/index.html:9642](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9642), reached through [history restoration:14900](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:14900).

   Use energies `[8,7,6,5,4,3,2,1,0]`, counts `[1000,900,20,22,25,35,40,10,5]`, ROI `[1,6]`, and Linear. Fit, change the charge correction to subtract 1 eV, then restore the original history snapshot and view its background-subtracted stack.

   Alignment matches the frozen fit grid against **currently corrected** energies, selecting counts `[900,20,22,25,35,40]`. The stack therefore displays `[880,2,6,11,23,30]` instead of the fit’s `[0,4,9,21,28,0]`. Reproduced through extracted production snapshot, charge-correction, restoration and stack functions; the server fit succeeds. Preserve fit-time sample identities or use the frozen background-subtracted counts.

2. **MINOR — Empty Linear/Manual windows produce an internal error.** [fitting.py:555](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:555).

   On a valid session, `/api/background` with `start_idx=1`, `end_idx=1` and either method raises `IndexError`, returning HTTP 500 with “Internal background error.” The page accepts the empty array; integral methods give a descriptive refusal. No incorrect numerical result escapes, but the empty-window handling should be explicit.

Verification: **81 Python and 62 JavaScript tests passed**. All four measurement summaries, the **3/62/56 restore census**, and **376 bit-identical Smart comparisons** reproduced. `_fmt3` matched on **29,988 additional random finite doubles**. Full browser suites were not rerun. No files changed.

**VERDICT: NO-GO.**
