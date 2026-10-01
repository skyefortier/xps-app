# Background math implementation round 5 — run B (commit dd1259a; codex exec, reasoning high)

1. **MAJOR — Current ascending spectrum fits still fail restoration.** [templates/index.html:11281](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:11281), [comparison:9620](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9620).  
   Reordering assumes recomputation is invariant under sorting. Two confirmed failures:
   - Linear, `E=[0,1,3]`, `I=[0.1,10,3.2]`: the saved middle background is `1.1333333333333335`; descending recomputation gives `1.1333333333333333`. The exact comparison drops this current fit.
   - Shirley/Smart/Smart experimental, averaging 1, `E=[0,1,1,2,3,4,5]`, `I=[10,12,14,40,30,22,20]`: stable descending sorting preserves duplicate order, whereas the algorithms’ internal reversal reverses it. Recomputed backgrounds differ by **0.70% of the intensity span**, dropping current fits.

2. **MAJOR — Conflicting manual anchors still certify an impossible curve.** [templates/index.html:4833](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4833), [fitting.py:2013](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:2013).  
   Load manual anchors `(1,10)` and `(1,30)` with `E=[3,2,1,0]`, `I=[20,25,30,5]`. No function passes through both anchors. Nevertheless, the page certifies `[30,30,30,10]`, restoration accepts it, and **`run_fit` returns success** against that background. Round 4 guards only the fewer-than-two-anchor fallback.

3. **MINOR — Explicit backgrounds still bypass non-finite-result rejection.** [templates/index.html:4860](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4860), [fitting.py:568](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:568).  
   Finite inputs `E=[0,1e-309]`, `I=[0,1]` overflow the slope. The page returns `[NaN,Infinity]` with `converged:true`; `compute_background_only(..., method="linear")` returns those values without raising. The throwing producers therefore hand out a failed background.

4. **MINOR — The parity evaluator retains the removed impossible-line fallback.** [autofit/parity.py:95](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/autofit/parity.py:95).  
   For round 4’s `E=[3,2,1,1,0]`, `I=[20,25,10,30,5]`, window indices `[2:4]`, `background_like_run_fit` returns `[10,10,10,10,10]`. Production `run_fit` now refuses. The reference evaluator no longer reproduces production behavior.

5. **MINOR — The promised identical linear refusal messages differ.** [templates/index.html:4538](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4538), [fitting.py:567](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:567).  
   Equal endpoint energies `1e-5` with different intensities produce `(0.00001 eV)` on the page and `(1e-05 eV)` on the server. Verdicts agree; message formatting does not.

Verification: **74 Python and 47 JS checks passed**. All four measurement summaries and the **3/62/56 census** reproduced exactly. Across 484 committed-spectrum/averaging comparisons, Smart and Smart experimental matched bit-for-bit and in verdict. One HTTP test was blocked by read-only temporary-directory restrictions; browser suites were not rerun. Lifecycle reproductions used extracted page functions. No files changed.

**VERDICT: NO-GO.**
