# Background math foundation round 4 — run A (commit 84f3ee0; codex exec, reasoning high)

**No fitted numbers changed.** `fitting.py`’s executable AST matches `main` after removing docstrings. `index.html` differs only in comments and the two Smart tooltips. Working tree unchanged.

1. **MAJOR — F12’s convergence qualification is still incomplete.** [README.md:248](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:248), [index.html:2003](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/templates/index.html:2003).

   F9 still says implementations “return the solution reached”; Smart Experimental’s tooltip still says “solved directly,” without a convergence condition.

   For `E=[0,1,2,3]`, `I=[2,3,10,13]`, both Smart methods return `[2,3,9.071429,13]`, with **14.2857% of span** equation residual. Increasing to 2,000 iterations changes nothing. The round-3 table’s claim that *every* occurrence was qualified is therefore false.

2. **MAJOR — F12’s blanket corpus residual bound contradicts the measurements.** [README.md:268](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:268).

   “Every implementation … residual ≤1.7e-11” includes:
   
   - `smart`: **1.1122423e-3**, `B4C-UCl4 / B1s Scan_3`, averaging 31.
   - `shirley_linear`: **3.2625072e-11**, `UCl4_on_graphite / U4f Scan_4`.

   Both reproduce. State bounds separately and retain Smart’s averaging exception. An iteration stopping does not certify its defining equation.

3. **MINOR — Tougaard’s approximation magnitude is overgeneralized.** [fitting.py:675](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/fitting.py:675), [README.md:144](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:144).

   The wording presents “~1e-8 of span at that tolerance” as a general accuracy characterization. With:
   ```text
   E = [0, 1.0000009, 2.0000018, 3.0000018]
   I = [10, 11, 11, 20]
   ```
   the fast branch is selected, but its discrepancy from the stated sum is **2.51093e-7 of span**. Net intensities are nonnegative; cancellation is unnecessary. Label `~1e-8` as the measured example, not a tolerance-derived accuracy guarantee.

4. **MINOR — F12’s proposed solver replacement has an unsupported change-scope guarantee.** [README.md:272](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:272).

   “Changes numbers on those inputs only” does not follow. For the already-converging `E=0…3`, `I=[1,1.72,1.98,2]`, production returns interior values approximately `[1.39999732,1.89999732]`; a root finder from the same line returns `[1.4,1.9]`. Net area changes from **0.40000537 to 0.4**.

   Restrict the proposal explicitly to a fallback after failed certification, or acknowledge and measure changes from replacing the solver generally.

The other round-3 repairs hold: F11’s λ=0 family member, averaging-10 increment, both page-comment numbers, and F5/F7 bounds. No resemblance-based defence found. F1/F2/F12 explicitly say “Owner decision”; F4/F5/F10/F11 should receive equally explicit labeling.

**Validation:** 33 Python tests and 4 JavaScript tests passed; all 121 measurement records reproduced. The 1,000-draw Monte Carlo reproduced, including the averaging reduction **0.3049 ± 0.0380 percentage points**; all positive-part outputs passed residual checks. Full application suites were not rerun.

**VERDICT: NO-GO.**
