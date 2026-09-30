# Background math foundation round 2 — run B (commit 4af19e7; codex exec, reasoning high)

**No fitted numbers changed.** `fitting.py`’s executable AST is identical to `main` after removing docstrings. `index.html` differs only in comments and two tooltip texts. Working tree untouched.

All **121 measurement records reproduce** within numerical tolerance; **24 Python tests and 2 JS tests pass**. The main Monte Carlo table reproduces, as do the headline corpus statistics and F5/F6/F7 measurements. The independence, returned-point convergence, and non-uniqueness fixes are real. Remaining findings:

1. **MAJOR — F2’s signed-integrand comparison mixes solver failure with estimator bias.** [README.md:169](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:169).

   Removing the positive-part clamp from the otherwise same iteration reproduces the quoted **−3.6139% ± 0.9399%**, with **29.72%** spread. But **19/1000 draws stop on a nonpositive integral and another exhausts 200 iterations**.

   Concrete case: seed 1, step 4000, zero-based draw 162 stops at iteration 25 with **−605.90% area error** and a signed-equation residual of **1.6443 times the data span**. This is not a solved signed Shirley background.

   The comparison therefore does not support the stated inference about the integrand’s statistical bias. Report numerical failures separately and validate the signed outputs, or remove that inference. The main positive-part Monte Carlo table remains supported.

2. **MAJOR — `shirley_linear`’s defining statement omits an executable exception.** [fitting.py:576](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/fitting.py:576), [fitting.py:613](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/fitting.py:613).

   With `E=[0,1,2,3,4]`, `I=[10,5,20,5,10]`, production returns `[10,10,10,10,10]`: equal edge levels trigger an early return **before clamping**. The claimed equation instead gives `[10,5,10,5,10]`, with a positive integral and zero residual. Production’s residual is **1/3 of span**.

   Also, `L` needs an explicit **index-affine** definition. The checker silently uses `np.linspace` at [checker:163](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/scripts/background_defining_statements.py:163). On `E=[0,.1,.2,1,4]`, `I=[10,20,30,25,12]`, it certifies approximately zero residual, while interpreting the documented “line” as affine in energy gives **5% of span** discrepancy.

3. **MAJOR — F11 conflates an undetermined normalization with an unsatisfiable equation.** [README.md:214](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:214), [checker:234](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/scripts/background_defining_statements.py:234).

   For `E=[0,1]`, `I=[10,10]`, the loss sum vanishes, but production’s `[10,10]` **satisfies both the equation and anchor**. The checker returns `None`; F11 incorrectly says the anchor is missed. Here λ is undetermined, and the background is valid.

   Distinguish zero loss with unequal versus equal anchor levels. Also distinguish the discrete sum from the continuum integral: for the two-point example `[10,20]`, linearly interpolated intensity gives a **strictly positive continuum integral**; the zero denominator arises from the sampled quadrature.

4. **MINOR — The revised tooltips still overstate Smart’s defining equation.** [index.html:2002](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/templates/index.html:2002).

   They present both methods as solving the same constrained problem without clearly stating Smart’s failure when averaging exceeds one. On `B4C-UCl4 / B1s Scan_3`, `n_avg=31`, Smart’s residual is **1.112e-3** under “data” and **1.023e-3** under “levels.” The README correctly reports this; the user-facing explanation needs the same qualification.

5. **MINOR — The Shirley docstring retains a stale F1 bound.** [fitting.py:389](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/fitting.py:389).

   It says **≤0.32%**, but record 52, `B4C-UCl4 / B1s Scan_0`, measures **0.322527%**. Use the README’s conservative **≤0.33%**.

**VERDICT: NO-GO.**
