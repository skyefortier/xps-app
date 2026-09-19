Reviewed HEAD `6b8cecc` against `35b950e`, read-only. **22 tests passed**; the upload test was excluded. API checks used in-memory sessions. No files changed.

1. **MAJOR — A successful, box-limited fit can skip refinement.** [fitting.py:1026](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1026), [fitting.py:1300](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1300)

   Reproduced twice through `/api/fit`, using **NumPy seed 3 and `n_perturb=3`**:

   - `x = np.linspace(287, 288, 81)`
   - `y = 1000 + 1e6 * np.exp(-4*np.log(2)*(x-285)**2)`
   - Manual background: `[[280,1000],[290,1000]]`
   - One Gaussian starting at centre 285, amplitude 1000, FWHM 1; all three varying; `amplitude_min=0`.

   The generated ceiling is **2,000**. The winning perturbation returns amplitude **1,968.711**, centre **286.082513**, FWHM **0.692385**. Its distance from the ceiling is **31.289**, exceeding the **20** threshold, so refinement never runs. HTTP **200**, `success=true`, “Optimization terminated successfully.”

   Refining that same incumbent with open amplitude bounds gives:

   | Result | Amplitude | Centre | FWHM | χ² |
   |---|---:|---:|---:|---:|
   | Returned DE | 1,968.711 | 286.082513 | 0.692385 | 9.16818×10⁻⁵ |
   | Open-bound refinement | 999,999.991 | 285.000000 | 1.000000 | 1.31160×10⁻¹⁹ |

   This answers **(a)**: DE’s success flag does not ensure coordinate proximity to an influential bound. Centre and width compensate for the amplitude restriction. Refining whenever generated bounds exist would address this reproduction without restoring widening.

   The “never a constraint” claim in [CLAUDE.md:252](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/CLAUDE.md:252) consequently remains too strong.

2. **MINOR — DE-specific solver options break the local refinement.** [fitting.py:1040](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1040)

   Direct Python reproduction: `x=linspace(286,290,81)`, Gaussian amplitude 10,000, centre 285/FWHM 1 fixed, starting amplitude 1000, background `none`, and:

   ```python
   fit_kws={
       "method": "differential_evolution",
       "fit_kws": {"seed": 4},
   }
   ```

   DE succeeds at the generated ceiling. Refinement then raises **`least_squares() got an unexpected keyword argument 'seed'`**, wrapped as `RuntimeError`. Switching only `method` retains incompatible solver options and prevents the documented incumbent/failure response. Build compatible refinement kwargs. The browser’s current requests are unaffected.

Other requested checks found no additional branch-specific defects: an outside-ROI DS+G centre matched standalone least-squares; budget-exhausted DE successfully transitioned to a converged local result; polished response fields remained consistent; `/api/analyze` does not depend on lmfit’s `result.method`; generated bounds stayed out of serialized bounds. Partial-NaN data still causes an output-length error, but the same failure reproduces on the parent’s least-squares path.

**VERDICT: NO-GO.**
