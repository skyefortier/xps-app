1. **MAJOR — A generated zero floor still excludes valid solutions while reporting success.** [fitting.py:1033](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1033)

   Reproduced through `/api/fit`: `x=linspace(280,290,101)`, counts `1000 − 100·exp(−4·ln(2)·(x−285)²)`, manual background 1000. Gaussian centre 285 and FWHM 1 fixed; starting amplitude 10; `amplitude_min: null`, maximum omitted, `n_perturb: 3`.

   Least-squares returns amplitude **−100** with effectively zero residual. DE returns **0**, χ² **81.9995**, and **HTTP 200 / success=true**. Both serialized bounds are `null`.

   The helper generates zero as the lower search limit, but this exemption prevents widening or rejecting it. A **requested** zero bound is already absent from `search_box`; remove the exemption for generated zero floors.

2. **MAJOR — The range-based tolerance rejects an exact fit after all three expansions.** [fitting.py:1028](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1028), [fitting.py:1045](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1045)

   Reproduced with `x=linspace(284.6,285,81)` and exact DS+G data: centre **285**, amplitude **1000**, α **0.05**, β **0.3**, Gaussian width **0.2**. Fix everything except centre; request `center_min: 0`, maximum omitted.

   Every minimization finds centre **285** with zero residual. Upper limits progress **285 → 285.4 → 285.8 → 286.2**. The final solution is **1.2 eV inside** the box, but tolerance is **2.862 eV**, so it remains “active.”

   `/api/fit` and `/api/analyze` both return **success=false**, including with three perturbations. Least-squares succeeds. Boundary detection and expansion size need compatible scales; the current test does not establish that the generated limit constrained the answer.

The original three reproductions are addressed, but these counterexamples leave disposition 1 incomplete. Dispositions 2–7 otherwise match the inspected code. lmfit rebuilds bound transforms on refit; other methods retain their bounds. Perturb winners receive the final check, and analyze preserves failure status/message. Find Peaks still permits explicitly applying failed-result peaks—existing behavior at [templates/index.html:15082](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/templates/index.html:15082).

Validation: **13 non-upload tests passed**, plus an equivalent in-memory page API request. Near-original-cap widening, finite negative amplitude minima, natural expansion exhaustion, and all-NaN HTTP 400 behaved as intended. No files changed.

**VERDICT: NO-GO.**
