# Background math implementation round 6 — run A (commit 65da2c7; codex exec, reasoning high)

Reviewed `65da2c7`, read-only.

1. **MAJOR — Unsorted grids can certify and fit a background that violates its defining statement.** [fitting.py:934](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:934), [templates/index.html:4441](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4441).  
   With `E=[0,2,1,3]`, `I=[10,40,12,20]`, Shirley certifies `[10,30,20,20]` on both sides. The value **30 exceeds both edge levels**, impossible for the stated normalized integral of nonnegative signal. The computation and certificate both integrate the unsorted sequence using signed spacings. I reproduced `run_fit` returning `success:true`; the actual spectrum loader also preserves this order, restores the fit and supplies the invalid background to stacks. Preserving file order needs an explicit refusal where the integral’s grid assumptions fail.

2. **MAJOR — Stacks subtract from the wrong samples after loading an unsorted spectrum.** [templates/index.html:9594](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9594), [subtraction:9850](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9850).  
   Load `rawBE=[5,1,4,0,3,2]`, counts `[20,12,22,10,30,40]`, ROI `[1,4]`, with manual anchors `(0,1),(5,1)`. Its valid fit restores. The selected energies are `[1,4,3,2]`, with counts `[12,22,30,40]`, but `_alignRawToFitBe` assumes a contiguous slice and returns `[12,22,10,30]`. Consequently, the stack’s background-subtracted trace displays **9 and 29 instead of 29 and 39** at energies 3 and 2. Reproduced through the actual loader and stack functions. Alignment must preserve the selected samples, including noncontiguous selections.

3. **MINOR — Manual fallback overflow still produces different refusal words.** [templates/index.html:4839](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4839), [fitting.py:2054](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:2054).  
   Manual mode with no anchors, `E=[0,1e-309]`, `I=[0,1]`: the page reports **“Manual background not converged…”**, while the server reports **“Linear background not converged…”**. Both refuse; no numerical result changes.

Verification: **77 Python and 59 JS focused tests passed**. All four measurement summaries, the **3 restored / 62 differing / 56 missing-curve census**, and **376 bit-identical Smart comparisons** reproduced. Lifecycle probes used extracted page functions; HTTP/browser suites were not rerun under the read-only restrictions. No files changed.

**VERDICT: NO-GO.**
