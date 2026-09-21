Reviewed HEAD `fdb2898` against `35b950e`, read-only. **27 tests passed; the upload test was excluded.** Additional API probes used in-memory sessions. No files changed. No BLOCKER found.

1. **MAJOR — An unverified perturbation discards an already verified fit.** [fitting.py:1298](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1298)

   Reproduced with real solver results:

   ```python
   x = np.linspace(284, 286, 81)
   y = (1000
        + 100*np.exp(-4*np.log(2)*((x-285)/0.1)**2)
        + 1e-5*np.random.default_rng(42).normal(size=81))
   ```

   Fit one Gaussian: fixed centre **285**, starting amplitude **10**, `amplitude_min=0`, open ceiling, starting FWHM **0.2**, default width bounds. Manual background: `[[280,1000],[290,1000]]`. Set NumPy seed **1** and force the perturb RNG to `default_rng(0)`.

   | `n_perturb` | Returned χ² | Success |
   |---|---:|---|
   | 0 | 4.7237293503×10⁻¹² | true |
   | 1 | 4.7237293503×10⁻¹² | true |
   | 3 | 4.7235616026×10⁻¹² | **false** |

   The final DE candidate has lower χ² but its refinement is rejected. Its retained `success=True` lets it replace the verified incumbent; serialization subsequently changes success to false. Both `/api/fit` and `/api/analyze` reproduce this, and the page rejects the result.

   **Verified candidates should take priority**, with rejected candidates retained for diagnostics. An unsuccessful optional restart should not invalidate a successful fit. Simply setting the unverified candidate’s `success=False` inside the helper would also require fixing the initial perturb-loop gate, so an unverified first candidate can still be rescued.

2. **MINOR — The acceptance tolerance rejects numerically equivalent, converged refinements.** [fitting.py:1052](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1052)

   Remove the noise from the fixture above; use seed **0**, `n_perturb=0`. DE returns χ² **3.8095×10⁻²⁹**, with FWHM exactly at the requested **0.1** floor. Least-squares succeeds, shifting FWHM to **0.1000000000601** and returning χ² **5.2273×10⁻¹⁸**.

   The purely relative comparison rejects this effectively exact fit and reports a generated-amplitude-limit failure. Add an appropriately scaled absolute numerical tolerance alongside the relative tolerance.

3. **MINOR — Documentation still describes inconsistent refinement rules.** [fitting.py:973](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:973), [CLAUDE.md:252](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/CLAUDE.md:252)

   The helper docstring still describes nearness, its scale, and deleted `_polish_outside_search_box`. CLAUDE’s “UNCONDITIONAL” statement also needs the qualification **when generated sides exist**: fully bounded requests return directly at line 1039.

Other requested checks found no additional defects: all four other methods matched the parent’s complete responses in seeded checks with zero/one perturbation; bound resetting and clipping did not preserve generated constraints; outside-ROI Gaussian and DS+G comparisons agreed with direct least-squares. Successful response curves, statistics, messages, and uncertainties were consistent; generated bounds remained absent. `nfev` describes the retained solver stage internally and is not serialized. The documented historical timing range was not independently re-benchmarked.

**VERDICT: NO-GO.**
