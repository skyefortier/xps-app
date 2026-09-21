Reviewed `f2ff96a` against `35b950e`, read-only. **32 tests passed; the upload test was excluded.** Additional API probes used in-memory sessions. No files changed.

1. **MAJOR — Numerically exact fits can still be rejected.** [fitting.py:1057](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1057)

   Disposition 1 fixes the committed examples but leaves the same failure at higher intensity:

   ```python
   x = np.linspace(999, 1001, 101)
   y = 1000 + 1e6*np.exp(-4*np.log(2)*((x-1000)/0.5)**2)
   ```

   Fit one Gaussian: centre **1000**, `center_min=1000`; amplitude **1e6**, `amplitude_min=0`, open ceiling; FWHM **0.5**, fixed. Manual background: `[[999,1000],[1001,1000]]`. NumPy seed **4**; perturb RNG fixed to `default_rng(0)`.

   | Stage | Centre | χ² | Solver success |
   |---|---:|---:|---|
   | DE | 1000 | 1.5816×10⁻²⁴ | true |
   | Refinement | 1000.00000005 | 1.45498×10⁻⁶ | true |

   The acceptance ceiling is **1.01×10⁻⁶**. Refinement is rejected despite moving the centre only **5×10⁻⁸ eV**, with maximum residual **0.000202 sigma**. The generated amplitude ceiling is **10 million**, far above the solution.

   Both `n_perturb=0` and `3` return **success=false**, including through `/api/fit` and `/api/analyze`, blaming generated limits. Direct `least_squares` succeeds. This remains a false failure caused by displacement from a **requested** bound. Add a scaled regression and handle that numerical displacement without blaming the search box.

   Scope: this reproduces on noise-free data; all twelve Poisson-noisy versions tested passed.

The other requested checks:

- **(a)** No materially worse accepted refinement found. At χ² per point of 1–100, the permitted increase per point is approximately **1.01×10⁻⁶–1.0001×10⁻⁴**. The remaining problem is false rejection.
- **(b)** Verified-first ranking is defensible and preferable for preserving a usable converged fit. Injecting later refinement failures retained verified χ² **29.43694** over unverified **25.29396**. That higher χ² is reported accurately; success denotes convergence, not global optimality. The alternative conservative failure policy is also defensible, so this is **not a defect**. All four other methods produced complete responses identical to the parent with zero and three perturbations.
- **(c)** No additional defect found in the remaining diff. The documentation corrections match the mechanism.

No BLOCKER or separate MINOR findings.

**VERDICT: NO-GO.**
