# Background math implementation round 7 — run B (commit 11733d8; codex exec, reasoning high)

Reviewed `11733d8`, read-only.

1. **MAJOR — A sorted background window inside an unsorted ROI certifies an incorrectly extended curve.** [templates/index.html:4930](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4930), [fitting.py:2107](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:2107).  
   Use `E=[5,0,1,2,3,-1]`, `I=[20,10,10,40,20,10]`, Shirley, averaging 1, background window `[1,3]`. Both sides certify `[10,10,10,15,20,20]`. The extension assigns **10 at energy 5 instead of the high-edge 20**, and **20 at energy −1 instead of the low-edge 10**. The window passes the order check; extension still assumes the entire ROI follows array order. Reproduced `run_fit` returning `success:true`; Smart, Smart-experimental and Tougaard also exhibit the reversed extension. Extend by energy or refuse incompatible ROI ordering.

2. **MAJOR — Rounded matching lets an excluded sample replace an exact fit-grid sample in stacks.** [templates/index.html:9623](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9623).  
   Load `rawBE=[3.00001,3,2,1,0]`, counts `[100,10,40,20,5]`, ROI maximum 3, manual anchors `(0,1),(4,1)`, and a current fit. The fit restores correctly. However, `3.00001` rounds to 3 and wins before the actual energy-3 sample. The stack displays background-subtracted counts **`[99,39,19,4]` instead of `[9,39,19,4]`**. Reproduced through the extracted spectrum-loader and stack-dataset functions. Matching must preserve the selected sample identities.

3. **MINOR — `_pyG3` does not reproduce Python’s tie rounding.** [templates/index.html:4675](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4675).  
   For certificate input `E=[0,1,2]`, `I=[0,100,0]`, `B=[0,1.125,0]`, Shirley, both sides reject with residual `0.01125`. The page’s reason reports **1.13%**, Python’s **1.12%**. JavaScript’s formatting rounds exact ties differently. Only refusal text changes.

Verification: **80 Python and 61 JS tests passed** using read-only, in-memory wrappers. All four measurement summaries, the **3 restored / 62 differing / 56 missing-curve census**, and **376 bit-identical Smart comparisons** reproduced. HTTP/browser suites were not rerun. No files changed.

**VERDICT: NO-GO.**
