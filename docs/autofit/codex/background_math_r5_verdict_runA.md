# Background math foundation round 5 — run A (commit 26fc9e2; codex exec, reasoning high)

**No fitted numbers changed.** `fitting.py`’s executable AST matches `main` after removing docstrings; `templates/index.html` differs only in comments and the two Smart tooltips. Working tree unchanged.

1. **MAJOR — F2’s averaging-10 comparison does not isolate the constraint’s effect.** [README.md:203](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:203).

   It compares unconstrained Shirley using averaged **data** against `smart_exp` using averaged **levels**. The claimed “constraint’s increment” therefore includes F1’s change of integrand.

   Repeating the specified seed-1, 1,000-draw, step-4000 experiment with **levels-only averaging for both equations** gives:

   | Measurement | Mean ± SE |
   |---|---:|
   | Unconstrained bias, averaging 10 | 1.56977% ± 0.05594 |
   | Constrained bias, averaging 10 | 2.40317% ± 0.04561 |
   | Constraint-only increment | **0.83341% ± 0.01141** |
   | Paired reduction from averaging 1 | **0.44402 ± 0.03778 percentage points** |

   The reported **0.97252%** increment includes **0.13911 percentage points** from changing the endpoint-data convention. Its reported **0.30491-point** reduction likewise mixes effects.

   All counterfactual unconstrained solutions had residual ≤`9.94e-14`; their clamps agreed with production `smart_exp` within `3.16e-11` of span. This is not failed convergence. Preserve the production-method comparison, but label it accurately and report the isolated constraint effect separately. F2’s qualitative conclusion survives.

2. **MINOR — The checker’s preprocessing description incorrectly classifies `shirley_linear`.** [background_defining_statements.py:8](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/scripts/background_defining_statements.py:8).

   It lists `shirley_linear` under replacement of endpoint **data**. Production and the actual residual checker average only the **levels**, integrating raw intensities.

   For `E=0…7`, `I=[10,20,50,100,100,70,25,35]`, `n_avg=2`, production’s actual-equation residual is `4.69e-11`; interpreting the header literally gives **0.00187446 of span**. Correct the header’s classification.

The requested round-4 repairs otherwise hold: convergence qualifications, method-specific corpus bounds, Tougaard’s measured errors and cancellation amplification, solver-option scopes, and explicit owner-decision labels. No resemblance-based mathematical defence found.

Validation: **35 Python tests and 4 JavaScript tests passed; all 121 measurement records reproduced exactly.** The reported Monte Carlo numbers reproduce, subject to finding 1’s attribution correction. Full application suites were not rerun.

Bibliographic entries check against [Shirley](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.5.4709), [Proctor–Sherwood](https://pubs.acs.org/doi/10.1021/ac00238a008), and [Tougaard](https://analyticalsciencejournals.onlinelibrary.wiley.com/doi/abs/10.1002/sia.740110902); coefficient provenance remains unverified as disclosed.

**VERDICT: NO-GO.**
