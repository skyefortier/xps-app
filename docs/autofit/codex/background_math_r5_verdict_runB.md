# Background math foundation round 5 — run B (commit 26fc9e2; codex exec, reasoning high)

**Confirmed: no fitted numbers changed.** `fitting.py`’s executable AST matches `main` after removing docstrings. `templates/index.html` changes only comments and two tooltip texts. Working tree unchanged.

1. **MAJOR — Smart’s tooltip still states a fixed-point property without requiring convergence.** [templates/index.html:2002](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/templates/index.html:2002).

   It says wherever the Shirley relation exceeds measured counts, the background equals those counts. For `E=0…5`, `I=[2,6,10,17,34,34]`, default `smart` returns:
   ```
   B = [2, 4.008368, 10, 17, 28.761506, 34]
   ```
   At `E=1`, `T(B)=6.407407 > I=6`, but `B=4.008368`, contradicting the tooltip. The constrained-equation residual is **19.8566% of span**. Smart Experimental’s tooltip now carries the convergence condition; Smart’s needs it too.

2. **MINOR — Another unconditional “solves” claim survived.** [tests/js/shirley_linear_statement.test.js:5](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/tests/js/shirley_linear_statement.test.js:5).

   The header says the page solves the equation on ascending grids, without requiring convergence. For ascending `E=0…4`, `I=[20,44,34,41,47]`, the actual page function returns `[20,43.625,34,41,47]`, with **12.5% residual**, at both 200 and 2,000 iterations. Qualify this comment consistently with the corrected page comment.

3. **MINOR — The independent checker’s header assigns Shirley-linear the wrong averaging rule.** [scripts/background_defining_statements.py:9](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/scripts/background_defining_statements.py:9).

   It lists `shirley_linear` under replacement of the endpoint **data**. Production and the checker’s actual residual function instead average only the **levels**, integrating raw intensities.

   With `E=0…7`, `I=[10,12,30,20,25,18,16,20]`, `n_avg=2`, production’s residual is approximately **4.7e-9** under the implemented raw-data equation, versus **1.1846% of span** under the header’s averaged-data reading. Move Shirley-linear to the “levels” category.

The remaining round-4 repairs hold: F12’s method-specific bounds and three option scopes, Tougaard’s measured errors and cancellation amplification, and the requested owner-decision labels. No resemblance-based mathematical defence found.

Validation: **35 Python tests and 4 JavaScript tests passed; all 121 measurement records reproduced within numerical tolerance.** The 1,000-draw Monte Carlo reproduced, including the averaging reduction **0.304906 ± 0.037975 percentage points**. Full application suites were not rerun.

**VERDICT: NO-GO.**
