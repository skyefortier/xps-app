# Background math foundation round 2 — run A (commit 4af19e7; codex exec, reasoning high)

**No fitted numbers changed.** `fitting.py`’s executable AST is identical to `main` after removing docstrings. `index.html` is identical after removing standalone comments and exactly the two changed tooltip values. Working tree unchanged.

I reproduced all **121 measurement records** within numerical tolerance and the **1,000-draw Monte Carlo table**. All **24 Python tests and 2 JS tests passed**. The revised independence, returned-point convergence check, non-uniqueness counterexamples, F6 measurements, and F5/F7 preprocessing fixes hold up. Remaining findings:

1. **MAJOR — F2’s signed-integrand comparison mixes failed solves into its claimed bias.** [README.md:170](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:170)

   Using the exact truth, seed 1, 1,000 draws and signed iteration reproduces **−3.6139% mean, 0.9394% SE, 29.7072% spread**. But **20 outputs fail the signed defining equation**. Zero-based draw 497 stops after seven iterations with a negative total integral, **−100.35% area error**, and residual **34.78 times the data span**.

   Those failed outputs contribute **−3.3067 percentage points** to the reported mean. These figures therefore do not establish that the signed *solution estimator* is worse. Report solver failures separately and certify the solutions before interpreting estimator bias; discarding failures alone would also introduce selection.

   The adjacent **+1.4% with averaging 10** reproduces for the **positive-part** method; identify that explicitly. It does not describe the signed comparison.

2. **MAJOR — The page’s new `shirley_linear` comment states the backend equation, which the descending-grid implementation does not solve.** [index.html:4628](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/templates/index.html:4628)

   For:
   ```text
   E = [4, 3, 2, 1, 0]
   I = [12, 25, 30, 20, 10]
   ```
   with 200 iterations and averaging 1, the page returns approximately:
   ```text
   [12, 13.198398, 11.935130, 10.736732, 10]
   ```
   Its residual against the newly claimed reversed-step equation is **0.0763268 of span**. The page accumulates in the opposite energy direction on this input. The known divergence is acknowledged elsewhere, but this new comment incorrectly certifies it. State the page’s actual behavior and limitation.

3. **MAJOR — The backend’s `shirley_linear` statement omits a branch that violates its constraint.** [fitting.py:577](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/fitting.py:577), [README.md:102](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:102)

   For `E=[0,1,2,3,4]`, `I=[10,15,5,15,10]`, equal endpoint levels trigger the early return:
   ```text
   B = [10,10,10,10,10]
   ```
   Here the positive integral exists and `d=0`, so the stated equation requires `min(L,I)=[10,10,5,10,10]`. The implementation’s residual is **0.5 of span**. Document and pin this exception without changing production behavior.

   Also specify that `L` is affine **in index**. On `E=[0,.1,.2,2,4]`, `I=[10,20,30,25,12]`, interpreting “line” as affine in energy produces **4.5% of span** discrepancy; the checker silently uses index interpolation.

4. **MINOR — F11 conflates an impossible anchor with an undetermined coefficient.** [README.md:214](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:214), [background_defining_statements.py:234](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/scripts/background_defining_statements.py:234)

   For `E=[0,1]`, `I=[10,10]`, the loss integral vanishes, but production’s `[10,10]` **satisfies the relation and anchor for every finite λ**. The checker returns `None`, and the prose incorrectly says the anchor is missed.

   Distinguish `loss=0, D_high≠C0`—no solution—from `loss=0, D_high=C0`—the anchor does not determine λ. The existing unequal-endpoint counterexample remains valid.

5. **MINOR — Shirley’s docstring retains the incorrect F1 upper bound.** [fitting.py:389](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/fitting.py:389)

   It says **≤0.32%**, but `B4C-UCl4.proj.zip / B1s Scan_0` measures **0.322527154%**. Use the README’s **≤0.33%**.

The main positive-part Monte Carlo conclusions survive, as do the corpus’s “neither reading” result for Smart, the constrained-area statistics, and F9’s appropriately limited second-start observation. The signed comparison and remaining defining-statement errors prevent approval.

**VERDICT: NO-GO.**
