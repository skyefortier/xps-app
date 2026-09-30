# Background math round 1 — run A (commit 8436631; codex exec, reasoning high)

Confirmed: **no fitted-number behavior changed**. `fitting.py` has an identical executable AST after removing docstrings; `index.html` changes only comments and the two Smart tooltips. Working tree remains clean.

The 18 new Python tests and 2 JS tests pass. I regenerated all 121 measurement records in memory; they match the committed JSONL within numerical tolerance. Nevertheless, the mathematical conclusions have substantive failures.

1. **BLOCKER — The uniqueness claim is false.** [README.md:69](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:69), [test_background_defining_statements.py:125](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/tests/test_background_defining_statements.py:125).

   For `E=[0,1,2,3]`, `I=[1,1.72,1.98,2]`, all three backgrounds satisfy the discrete, positive-part Shirley relation:
   ```
   [1, 1.40, 1.90, 2]
   [1, 1.45, 1.95, 2]
   [1, 1.50, 2.00, 2]
   ```
   The checker reports zero residual for each. Clamping them produces three distinct constrained fixed points, with net areas **0.40, 0.30 and 0.22**. Both tested starts converge to the first, so the proposed “uniqueness test” misses the other solutions.

   The clamp identity itself is correct. It establishes a correspondence between solutions, **not uniqueness**. F3, the docstrings and `CLAUDE.md` must distinguish those claims.

2. **MAJOR — The implementation can miss an existing solution, and the checker’s convergence flag does not certify its equation.** [README.md:39](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:39), [background_defining_statements.py:102](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/scripts/background_defining_statements.py:102).

   On the existing parity-test case `E=[0,1,2,3,4]`, `I=[10,5,5,17,20]`, production Shirley stops immediately at `[10,12.5,15,17.5,20]`: its positive-part integral is zero. Both Smart methods return the data themselves. Their defining relations are undefined, despite valid solutions existing: unconstrained `[10,10,10,15,20]`, constrained `[10,5,5,15,20]`, each with zero residual.

   Separately, `constrained_solution([0,1,2], [1.1,.5,.2], B0=[-99.8]*3)` returns `converged=True` with a **NaN residual**. The stop checks the preceding update, not the returned point’s equation. With `I=1e15+[0,10,20,7,5]`, it accepts one iteration despite a residual of **0.00625 of span**. The uniqueness tests discard convergence flags altogether.

   Report zero-integral fallback, existence and finite-stop limitations explicitly; require finite residuals before calling a reference result converged.

3. **MAJOR — The Tougaard checker can certify the wrong statement.** [background_defining_statements.py:143](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/scripts/background_defining_statements.py:143), [fitting.py:623](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/fitting.py:623).

   The docstring defines `J` as measured intensity, but the reference shares production’s endpoint-data replacement. With `E=0…7`, `I=[10,20,50,100,100,70,25,35]`, `n_avg=2`, the checker reports approximately **4e-17**, while evaluating its stated raw-`J` relation with the same averaged edge levels gives **9.56e-4 of span** discrepancy.

   It also copies the zero-denominator fallback: `E=[0,1]`, `I=[10,20]` returns `[10,10]` and scores **zero reference error**, although the required high-edge anchor misses by 10.

   The refined reference calls `fitting.tougaard_background` itself. Independent analytic integration does support the corpus discretisation scale—maximum error **8.485e-6 of span**—but that does not validate shared preprocessing or fallback semantics. Define those independently. F1’s two preprocessing conventions are both mathematically coherent; preferring levels-only averaging requires a modeling justification.

4. **MAJOR — “Unconstrained Shirley unbiased” is demonstrably false as a general conclusion.** [test_background_defining_statements.py:135](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/tests/test_background_defining_statements.py:135), [README.md:142](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:142).

   The supplied “truth” uses `cumsum(peaks)`, whereas the defining statement uses trapezoids. Its noise-free residual is **4.02e-4 of span**, causing **0.0405%** area error before noise.

   Correcting that construction preserves the example’s constrained bias: **+0.829% ± 0.069% SE**. However, using the same peaks, baseline, seed and 300 draws with an exact trapezoidal Shirley step of **4000 instead of 400**, unconstrained Shirley shows **+2.871% ± 0.336% SE** bias. Every output satisfies the equation to within **2.25e-11 of span**.

   Thus this is estimator bias, not failed convergence. Failure to reject zero bias in one simulation cannot establish unbiasedness. F2 must separate the incremental effect of clamping from the unconstrained estimator’s own bias.

5. **MAJOR — F6’s kernel-sampling premise is false on the committed spectra.** [README.md:169](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:169).

   The reported widths are correct, but **31–35 eV exceeds the 23.4 eV kernel maximum**. In `1-GTA UCl4-graphite one set of U doublets.proj.zip`, `U4f Scan_1`, the background window is approximately **370.51–405.21 eV**. About **29.7%** of its high-edge discrete loss integral comes from losses *beyond* the kernel maximum.

   “Samples only its rising part” is false; “λ absorbs the rest” does not establish shape insensitivity. The recommendation needs a measured kernel-shape sensitivity comparison.

6. **MAJOR — F4 substitutes “no defining statement” for an incorrect derivation.** [fitting.py:560](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/fitting.py:560), [README.md:89](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:89).

   At convergence, its mathematical statement can be written
   `B=min(L+Δ(1−Q(B)/Qn(B)), I)`,
   where `Q(B)` integrates `max(I−B,0)` and `Δ=|b_low−b_high|`. The documented cumulative fraction “above L” omits the iterated correction.

   For `E=0…4`, `I=[10,20,30,25,12]`, production satisfies the former relation to **7e-15**, while the documented above-`L` reading differs by **0.0458 intensity units**. The unclamped high edge also equals `b_high`, contradicting “meets neither edge condition.”

   Its reversed loss direction and low-edge mismatch can justify keeping it off the menu. They do not establish that no mathematical defining statement exists.

7. **MINOR — F5/F7’s saved measurements mix endpoint-preprocessing error with stopping error.** [background_defining_statements.py:227](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/scripts/background_defining_statements.py:227), [background_defining_statements.py:259](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/scripts/background_defining_statements.py:259).

   With averaging enabled, these fields compare production’s modified-data result against the raw-data reference. Consequently JSONL maxima reach **0.32254%** for F7 and **0.32264%** for F5, rather than the advertised stopping-only bounds.

   Recomputing comparisons with consistent preprocessing reproduces the advertised **0.00637%** and **0.002286%** bounds. Preserve those correctly isolated measurements in the artifact.

The integration direction and positive-part clamp algebra are correct, subject to identical input data and an actual fixed point. F8’s index-versus-energy distinction is also correct.

All three bibliographic citations check out: [Shirley, PRB 5, 4709 (1972)](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.5.4709); [Proctor & Sherwood, Analytical Chemistry 54(1), 13–19 (1982)](https://pubs.acs.org/doi/10.1021/ac00238a008); [Tougaard, Surface and Interface Analysis 11, 453–472 (1988)](https://analyticalsciencejournals.onlinelibrary.wiley.com/doi/10.1002/sia.740110902). This verifies bibliographic attribution, not the unverified coefficient provenance.

**VERDICT: NO-GO.**
