# A2 round 9 — run B (commit fe2120f; codex exec, reasoning high)

1. **MAJOR — Ambiguous lineshape inference rejects an identical certified response.** [tests/fit_equality.py:103](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:103), [comparison:248](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:248).

   Reproduced using `_two_basin_problem()`, adding a fixed Gaussian to the model and data: centre **287**, amplitude **1**, FWHM **1e7**. Run LM with linear background, three perturbations, six scattered starts, seed **123**.

   The complete response certifies and contains one alternative. Gaussian and Lorentzian reconstructions of the added component differ by only **7.76e−13**, so both match and `_lineshape_of` returns `None`. **`assert_same_fit(a, deepcopy(a))` rejects**, solely because that alternative component cannot be reconstructed.

   Numerical agreement cannot reliably identify a lineshape. Preserve its explicit identity rather than requiring unique inference from sampled curves.

2. **MINOR — Non-finite reconstruction still silently disables alternative-curve checking.** [tests/fit_equality.py:89](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:89), [curve check:155](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:155).

   Reproduced round 7’s real LA alternatives: **(α,β)=(1.002,0.998)** versus **(0.998,1.002)**, with identical alternative χ²ᵣ ≈ **2.00133e−12**. Their curves differ by **0.147146%** of their own height, exceeding the **0.1%** resolution; normal comparison rejects.

   Injecting an evaluator that returns NaNs **only at the alternative parameters**, while preserving successful returned-component identification, makes those same complete responses **pass**. `_evaluate` accepts the correctly shaped NaN array, and matching non-finite masks bypass comparison. Treat non-finite reconstruction as failure.

Validation: **73 certificate/parity tests, four targeted round-8/bound regressions, and 122 JavaScript tests passed**. Additional certificate-exit, evaluation-cap and restart-cancellation probes passed. Recorded displacement notices remain **0/202** per method. Broader Python sweeps were stopped for budget; no files changed.

The accepted finite-resolution ruling stands.

**VERDICT: NO-GO**
