# Background math foundation round 3 — run B (commit e1077be; codex exec, reasoning high)

**No fitted numbers changed.** `fitting.py`’s executable AST is identical to `main` after removing docstrings. `index.html` differs only in comments and the two Smart tooltips. Working tree unchanged.

All **121 measurement records reproduce** within numerical tolerance. **27 Python cases and 4 JavaScript tests pass.** The 1,000-draw Monte Carlo reproduces both tables, including averaging 10: **+1.4307% ± 0.0555** unconstrained and **+2.4032% ± 0.0456** constrained. All positive-part outputs passed residual checks. I did not rerun the full application suites.

1. **MAJOR — The implementations can cycle indefinitely; “returns the solution reached” remains an overclaim.** [README.md:238](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:238), [fitting.py:582](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/fitting.py:582).

   With `E=[0,1,2,3,4]`, `I=[11,14,1,33,40]`, default Shirley returns approximately:
   ```
   [11, 15.142857, 19.285714, 29.642857, 40]
   ```
   Its equation residual is **21.2454% of span**. Both Smart methods have **10.6227%** residual. Iteration 201 switches to the other member of a two-cycle; 2,000 iterations reproduce iteration 200. The integral remains positive.

   `shirley_linear` also cycles: `I=[20,44,34,41,47]` gives **12.5%** residual after either 200 or 2,000 iterations. Neither documented exception—equal edge levels or nonpositive integral—applies.

   These are positive counts on uniform ascending grids with increasing edge levels. Explicitly report nonconvergence and qualify solution claims throughout; pin these cases. Merely increasing the iteration cap cannot fix them.

2. **MINOR — F11’s revised “flat C0 solves for every λ” is still false.** [README.md:244](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:244), [fitting.py:662](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/fitting.py:662), [checker:234](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/scripts/background_defining_statements.py:234).

   Take `E=[0,1,2,3]`, `I=[10,11,10−r,10]`, where `r=2(1644/1647)²≈1.99272066`. All counts are positive. The high-edge loss sum cancels exactly, but the interior loss at `E=2` is nonzero.

   The flat background solves the relation for **λ=0**. With the documented kernel and **λ=1644²**, the solution is instead `[10,10,11,10]`, still meeting both anchors. Thus λ is undetermined, but the background generally varies with λ. “Flat for every λ” requires the **entire loss vector** to vanish. The two-point test misses this distinction.

3. **MINOR — Averaging does reduce the measured constraint increment.** [README.md:192](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:192).

   “Cuts … both biases, not the increment” contradicts the rerun. At step 4000, the increment falls from **1.2774%** to **0.9725%**. Across the same draws, the reduction is **0.3049 percentage points ± 0.0380 SE**, approximately **24%**.

   Say “reduces but does not eliminate the increment.” The reported individual biases and withdrawal of the signed-integrand inference are supported.

4. **MINOR — Tougaard’s near-uniform fast path is an undocumented approximation to the defining sum.** [fitting.py:772](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/fitting.py:772), [README.md:41](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:41).

   For `E=[0,1,2.0000009,3.0000009,4.0000009]`, `I=[10,20,30,25,12]`, the uniformity tolerance selects convolution using index separations and one spacing. Its discrepancy from the stated actual-grid sum is **1.0342e−8 of span**.

   The corpus bound remains reproducible, but the branch is not universally a “pure optimization.” Document its approximation and pin its boundary.

The other round-2 repairs hold: index-affine `L`, the unclamped equal-edge exception, the page’s descending-grid limitation, the Smart averaging qualification, and the corrected 0.33% bound. Short-window returns, averaging caps, equal-energy linear fallback and zero-integral exits are documented; ordinary repeated-energy intervals retain valid zero-width quadrature contributions. The principal missing behavior is nonconvergence despite a positive integral.

**VERDICT: NO-GO.**
