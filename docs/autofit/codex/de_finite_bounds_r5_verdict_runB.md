Reviewed HEAD `fdb2898` against `35b950e`, read-only. **27 tests passed; upload test excluded.** Additional checks exercised both APIs with in-memory sessions. No files changed.

1. **MAJOR — Numerical noise after successful refinement rejects an exact fit.** [fitting.py:1052](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1052)

   Reproduced with NumPy seed **4**, for both `n_perturb=0` and `3`:

   ```python
   x = np.linspace(280, 290, 101)
   y = 1000 + 1000*np.exp(-4*np.log(2)*(x-285)**2)
   specs = [{
       "id": 1, "shape": "gaussian",
       "center": 285, "center_min": 285,
       "amplitude": 1000, "amplitude_min": 0,
       "fwhm": 1, "fix_fwhm": True,
   }]
   ```
   Use manual background `[[280,1000],[290,1000]]`.

   | Stage | Centre | χ² | Solver success |
   |---|---:|---:|---|
   | DE | 285 | 4.19×10⁻²⁸ | true |
   | Refinement | 285.0000000285 | 1.13×10⁻¹¹ | true |

   `least_squares` moves the centre slightly inside the **requested** lower bound. The relative-only χ² comparison rejects this numerically equivalent refinement. Both `/api/fit` and `/api/analyze` return **HTTP 200 / success=false**, blaming generated amplitude limits. The amplitude is approximately **1000**, well below its generated ceiling **10,000**. Direct `least_squares` succeeds.

   This also reproduces with a DS+G centre at its requested minimum and with background-only data. Treat numerical equivalence near zero using an appropriate absolute-plus-relative tolerance, while retaining the better incumbent.

2. **MINOR — The helper documentation still describes the removed mechanism.** [fitting.py:971](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:971)

   `_finite_search_box` still promises that generated sides never determine the answer, describes refinement only near a side, references deleted `_polish_outside_search_box`, and defines returned scales as nearness thresholds. These statements contradict HEAD and the revised `CLAUDE.md`.

The remaining requested checks:

- **(a): Yes.** With seed 36 in the existing two-DS+G edge scenario, injecting failures into later refinements replaces a verified χ² **29.43694** candidate with an unverified χ² **25.29396** candidate and returns `success=false`. This is conservative and consistent with the stated contract; preferring verification would knowingly return a worse fit. I do not count it as another correctness defect.
- **(b–d):** No additional regression found. Other methods retain their original calls. Perturb clipping influences subsequent search proposals, but resetting bounds and refining prevents inherited boxes becoming request constraints. The outside-ROI amplitude probe agrees with direct local fitting.
- **(e):** Exercised statistics, residuals, uncertainties, messages, and API failure propagation were consistent. Generated bounds stayed out of responses. `nfev` is not serialized.
- **(f):** The revised `CLAUDE.md` mechanism matches implementation. Timing claims were not independently rebenchmarked.

No BLOCKER found.

**VERDICT: NO-GO.**
