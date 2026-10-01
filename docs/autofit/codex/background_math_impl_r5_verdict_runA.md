# Background math implementation round 5 — run A (commit dd1259a; codex exec, reasoning high)

Reviewed `dd1259a`, read-only.

1. **MAJOR — Conflicting manual anchors still certify an impossible curve.** [templates/index.html:4833](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4833), [fitting.py:2013](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:2013).  
   With `E=[0,1,2,3,4,5]`, `I=[10,12,40,30,22,20]`, and anchors `(0,0),(2,1),(2,20),(5,0)`, no function passes through both anchors at energy 2. Nevertheless, the page marks the interpolated curve converged, restoration accepts it, and `run_fit` returns `success:true`. The round-4 check covers only manual backgrounds with fewer than two anchors. Conflicting duplicate anchors also need refusal.

2. **MAJOR — Ascending spectrum files with duplicate energies still lose current fits.** [templates/index.html:11281](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:11281).  
   Use `E=[0,1,2,2,3,4,5]`, `I=[10,12,40,15,30,22,20]`, Shirley, averaging 1, full window. The current certified background at energy 2 is `14.802679624392315`. Loading its spectrum file recomputes `11.112240327606633` and drops the fit—a **12.3% intensity-span difference**. Stable descending sorting preserves duplicate-point order, while the solver’s ascending normalization reverses it, changing the trapezoids. Reproduced through the actual loader and `createTab`; Smart, Smart experimental and Shirley + linear also fail.

3. **MINOR — Explicit linear backgrounds bypass finiteness checks.** [templates/index.html:4860](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4860), [fitting.py:568](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:568).  
   For finite inputs `E=[0,1,2]`, `I=[1e308,1,-1e308]`, arithmetic overflows to `[NaN,-Infinity,-Infinity]`. The page marks this converged, and its throwing producer returns it normally. `compute_background_only(..., method="linear")` likewise returns those values without `BackgroundNotConverged`. Explicit methods need result validation too.

4. **MINOR — The offline parity helper retains the forbidden linear fallback.** [autofit/parity.py:95](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/autofit/parity.py:95).  
   With `E=[3,2,1,1,0]`, `I=[20,25,10,30,5]`, indices `[2:4]`, `background_like_run_fit` returns `[10,10,10,10,10]`, while `run_fit` correctly raises. The helper feeds model-plus-background parity evaluation, so that consumer still evaluates an impossible background as valid. Reuse `_line_through`.

5. **MINOR — The new refusal messages are not identical.** [templates/index.html:4538](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4538), [fitting.py:567](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:567).  
   Equal endpoint energies `1e-5` with unequal intensities produce `(0.00001 eV)` on the page versus `(1e-05 eV)` on the server. At `1e6`, they produce `(1000000 eV)` versus `(1e+06 eV)`. Verdicts agree; the claimed identical wording does not.

Verification: **74 Python and 47 JS focused tests passed**, including numerical, certificate and manual parity. One HTTP test was blocked by read-only temporary-directory restrictions; browser suites were not rerun. All four measurement summaries, the **3/62/56 restore census**, and **376 bit-identical Smart pairs** reproduced. Another **128 project-record round trips** passed. No files changed.

**VERDICT: NO-GO.**
