# Background math foundation round 4 — run B (commit 84f3ee0; codex exec, reasoning high)

Confirmed: **no fitted numbers changed**. `fitting.py`’s executable AST matches `main`; `templates/index.html` differs only in comments and the two Smart tooltips. Working tree unchanged.

1. **MAJOR — Tougaard’s near-uniform accuracy claim remains overgeneralized.** [fitting.py:675](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/fitting.py:675), [README.md:144](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:144).

   “~1e-8 of the span at that tolerance” is one example’s measurement, not an accuracy guarantee. With `K(t)=2866t/(1643+t²)²`, take:
   ```
   E = [0, 1, 2.0000005, 3.0000005]
   I = [2, 3, 2−K(2)/K(1)+0.001, 3]
   ```
   All counts are positive. Both high-edge sums are **nonzero**, and both backgrounds meet the anchor. Nevertheless, production returns approximately `[2,2,1002,3]`, versus `[2,2,1001.507401,3]` from the stated quadrature: **16.4654% of span** difference.

   The documented exact-zero exception does not cover this case. Label `~1e-8` as the tested example and explain that anchoring amplifies quadrature error near cancellation, even without a zero denominator. Correct the code comment and round-3 table too.

2. **MINOR — F12 introduces a corpus bound contradicted by the committed measurements.** [README.md:267](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:267).

   “Every implementation … residual ≤1.7e-11” fails for:
   - `smart`, `B4C-UCl4 / B1s Scan_3`, averaging 31: **1.1122423e-3**.
   - `shirley_linear`, `UCl4_on_graphite / U4f Scan_4`: **3.2625072e-11**.

   Distinguish convergence of Smart’s underlying iteration from satisfaction of its constrained statement, retain F1’s averaging exception, and use method-specific bounds.

3. **MINOR — The promised convergence qualification was not applied everywhere.** [README.md:248](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:248), [tests:78](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/tests/test_background_defining_statements.py:78), [index.html:2003](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/templates/index.html:2003).

   F9 and the test comment still say the implementation returns a solution; the experimental Smart tooltip still says “solved directly” without qualification. The pinned `E=[0,1,2,3]`, `I=[2,3,10,13]` case returns a non-solution with **14.2857% residual**. The round-3 table’s assertion that every such claim was qualified is therefore false.

4. **MINOR — F12 overpromises the scope of a future solver change.** [README.md:270](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:270).

   A replacement solver does not inherently change numbers “on those inputs only.” For the already-pinned `I=[1,1.45,1.90,2]`, two valid solutions have net areas **0.25 and 0.10**. A root finder may select either. Preserving successful outputs requires explicitly restricting the new solver to a fallback after a defined failure check. Keep that choice with the owner.

The F11 λ-family correction, averaging-10 increment, two Shirley-linear metrics, and corrected F5/F7 bounds hold. No resemblance-based mathematical defence found.

Validation: **33 Python cases and 4 JavaScript tests passed; all 121 measurement records reproduced.** The 1,000-draw Monte Carlo reproduced both step sizes and averaging 10, including the increment reduction **0.3049 ± 0.0380 percentage points**. Full application suites were not rerun.

**VERDICT: NO-GO.**
