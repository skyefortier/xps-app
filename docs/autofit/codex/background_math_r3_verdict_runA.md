# Background math foundation round 3 — run A (commit e1077be; codex exec, reasoning high)

**No fitted numbers changed.** `fitting.py`’s executable AST matches `main` after removing docstrings. `index.html` matches after removing comments and exactly the two Smart tooltip values. Working tree unchanged.

1. **MAJOR — Iteration can cycle indefinitely; “returns the solution reached” remains false.** [README.md:238](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:238), [fitting.py:361](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/fitting.py:361), [CLAUDE.md:877](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/CLAUDE.md:877).

   With `E=[0,1,2,3]`, `I=[2,3,10,13]`, Shirley cycles between:
   ```
   [2, 2,        7.5,       13]
   [2, 3.571429, 9.071429,  13]
   ```
   The default 200-iteration output has defining-equation residual **0.142857 of span**. Both Smart methods also cycle, with the same residual. Increasing the cap to 2,000 does not help.

   An exact solution exists: `[2,z,z+5.5,13]`, where `z=(17−√37)/4`; its measured residual is `1.6e-16`.

   This is neither F10’s undefined first step nor merely non-uniqueness. Mentioning the iteration cap does not qualify the repeated claim that the returned object is a solution. Document nonconvergence explicitly across the statements and pin this case without changing production behavior.

2. **MAJOR — Tougaard’s nearly-uniform branch does not implement the stated quadrature, and can change whether the anchor is satisfiable.** [fitting.py:775](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/fitting.py:775), [README.md:134](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:134).

   Let `K(t)=2866t/(1643+t²)²`, and use:
   ```
   E = [0, 1, 2.0000005, 3.0000005]
   I = [2, 3, 2−K(2)/K(1), 3]
   ```
   All intensities are positive. The uniformity tolerance accepts this grid, and the convolution substitutes index-based separations and constant spacing. Its high-edge sum cancels exactly, so production returns `[2,2,2,2]`, missing the anchor by **33.414% of span**.

   The independently stated quadrature has a **nonzero** high-edge sum, `5.2314e-10`, and therefore an anchored solution. That solution is badly conditioned, but it exists.

   The findings omit this executable approximation branch. State its effective grid and failure mode; F11’s explanation based on the stated sum being zero does not cover this example.

3. **MINOR — F11’s new “flat C0 solves … for every λ” claim is still overgeneralized.** [README.md:244](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:244), [fitting.py:662](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/fitting.py:662), [background_defining_statements.py:234](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/scripts/background_defining_statements.py:234).

   On the uniform grid `E=[0,1,2,3]`, use `I=[2,3,2−K(2)/K(1),2]`. The high-edge loss sum is exactly zero, but an interior loss sum is nonzero.

   The anchor leaves λ undetermined; **different λ give different backgrounds**. Production’s flat return satisfies the full equation only for **λ=0**, not every λ. The two-point tests miss cancellation cases. The revised equal/unequal-anchor distinction is valid, but this additional assertion needs correction everywhere, including the round-2 table.

4. **MINOR — Some measurement labels and bounds remain inaccurate.** [index.html:4631](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/templates/index.html:4631), [README.md:207](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:207), [README.md:230](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:230).

   - The descending Shirley-linear example’s **7.6327%** is its equation residual. Its actual **page/server difference is 7.8221%**. The page comment labels 7.6% as that gap.
   - F5’s `≤1.4e-5` bound is exceeded by **1.44198385e-5**, on `Cl2p_projfit_test / U4f Scan_3`.
   - F7’s `8.5e-5` bound is exceeded by **8.51743034e-5**, on `1-GTA … / U4f Scan_8`.

   Use correctly identified metrics and upward-rounded bounds.

The other round-2 fixes hold: signed-integrand inference withdrawn; index-affine `L`, its unclamped equal-level exception, and the page’s direction limitation documented; Smart tooltips qualified; Shirley’s 0.33% bound corrected. The short-window returns, averaging cap, linear equal-energy fallback, and manual fallback are covered. Tested monotone grids with repeated energies satisfy the applicable discrete statements; zero-width intervals themselves introduce no discrepancy.

**Validation:** all **121 measurement records reproduce**; **27 Python cases and 4 JavaScript tests pass**. The 1,000-draw Monte Carlo reproduces both step sizes and averaging 10:

| Step 4000, averaging 10 | Mean area error ± SE |
|---|---:|
| Unconstrained | +1.4307% ± 0.0555 |
| Constrained | +2.4032% ± 0.0456 |

All positive-part Monte Carlo outputs passed their defining-equation checks. I did not rerun the full commit suites.

**VERDICT: NO-GO.**
