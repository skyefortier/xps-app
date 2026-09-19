Reviewed HEAD `6b8cecc` against `35b950e`, read-only. **22 tests passed; the upload test was excluded.** Additional API checks used in-memory sessions. No files changed.

1. **MAJOR — Selecting the winner before polishing can hide a box-limited solution.** [fitting.py:1299](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1299)

   Reproduction: NumPy seed **0**, `x=linspace(286.8,290.8,81)`, and:

   ```python
   y = (1000
        + 1e7 * np.exp(-4*np.log(2)*(x-285)**2)
        + 310 * np.exp(-4*np.log(2)*(x-289)**2))
   ```

   Fit one Gaussian: centre initially **287**, bounds **[284,291]**; amplitude initially **1000**, minimum **0**, maximum open; FWHM **1**, fixed. Use manual background **1000** and DE.

   | `n_perturb` | Returned centre | Returned amplitude | χ² | Success |
   |---|---:|---:|---:|---|
   | 0 | 285.000122 | 9,987,689 | **1157.545422** | true |
   | 1 or 3 | 288.999978 | 310.001927 | **1249.561359** | true |

   The generated ceiling is **12,550.222218**. The initial search lands near it with χ²≈1269.75. A perturbation finds the interior solution with χ²≈1249.56, wins selection, and **suppresses polishing entirely**. Polishing the initial boundary candidate produces χ²≈1157.55. An explicit larger ceiling also recovers that better basin.

   This repeats and reaches `/api/fit` as **HTTP 200/success=true**. It answers (a): successful convergence far from the generated side does not establish that the box was harmless. Here perturbation increases the returned χ² by **7.95%** compared with zero perturbations.

   Refine boundary candidates under the requested bounds before discarding them through candidate selection. The current regression only compares candidates actually produced by `Model.fit`, so it misses this skipped refinement. The documentation’s “never a constraint” assurance is consequently too strong.

2. **MINOR — DE-specific options crash the automatic local refinement.** [fitting.py:1040](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1040)

   Use the existing Gaussian-tail scenario: `x=linspace(286,290,81)`, true amplitude **10,000**, centre **285** and FWHM **1** fixed, starting amplitude **1000**, background `none`. Pass:

   ```python
   fit_kws={"method": "differential_evolution",
            "fit_kws": {"seed": 4}}
   ```

   DE succeeds, but polishing raises `RuntimeError: lmfit fitting failed: least_squares() got an unexpected keyword argument 'seed'`. The method switch preserves solver-specific options. Filter those options when constructing the local call. This affects direct `run_fit` callers; the page supplies only the method.

No BLOCKER found. Polished response fields and `/api/analyze` were consistent in the exercised cases. Recovering an exhausted DE run through successful local refinement is defensible; it returns the local convergence message. All four other methods bypass both helpers, and generated bounds remained absent from responses. NaN omission exposed an existing array-length failure shared with ordinary `least_squares`, not a new regression.

**VERDICT: NO-GO.**
