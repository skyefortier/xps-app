The original three reproductions are addressed, but the rework has three remaining issues.

Validation: **13 tests passed**; the upload test was replaced with a read-only, in-memory API check, which returned **200/success=true**. Generated bounds are omitted correctly; other methods retain their bounds. lmfit rebuilds its internal transforms before refitting. `/api/analyze` preserves failure status and message, and all-NaN intensities produce HTTP 400. The `0.995 × original cap` case succeeds after one expansion, including with negative finite `amplitude_min`.

1. **MAJOR — A generated zero lower bound silently excludes valid negative amplitudes.** [fitting.py:1033](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1033)

   Reproduced with `x=linspace(280,290,101)`, counts `200 − 100*exp(-4*log(2)*(x−285)**2)`, manual background 200, and a Gaussian with fixed centre 285/FWHM 1, starting amplitude 10, **`amplitude_min=null`**.

   DE returns **success=true, amplitude 0, reduced χ² 6.51724**. Least-squares recovers **−100**, with essentially zero residual.

   The request leaves the lower side open, but the helper generates zero and the exemption prevents widening or refusal. Both returned bounds are `None`, concealing the restriction. A request-specified zero already remains outside `search_box`; a **generated** zero cannot safely receive that exemption.

2. **MAJOR — Whole-interval tolerance rejects exact fits beside broad one-sided centre bounds.** [fitting.py:1028](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1028), [fitting.py:1045](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1045)

   Reproduced with `x=linspace(284.8,285.2,41)` and exact DS+G data: centre 285, amplitude 1000, α=.05, β=.3, Gaussian width=.4. Fix everything except centre and set `center_min=0`.

   Every minimisation recovers **centre 285 with zero residual**. Nevertheless, three expansions only move the generated maximum from 285.2 to 286.4. Its distance from the solution is 1.4, still below the **2.864 eV tolerance**. `/api/fit` returns **200/success=false**, including with three perturbations.

   `center_max=1000` reproduces the symmetric failure. Removing the one-sided bound succeeds. The tolerance and expansion distance need compatible scales.

3. **MINOR — A winning perturbation can cause refusal without receiving any expansion.** [fitting.py:1294](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1294), [fitting.py:1372](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1372)

   Reproduced with NumPy seed 36, ROI `linspace(280,290,501)`, background 1000, and two DS+G components at 280/285 with amplitudes 100/75, α=0, β=.05, Gaussian width=.05. Fit one component with amplitude/shape fixed and centre free.

   The first search finds centre 285, χ²ᵣ=.058874. Perturbations improve it to **280.000017, χ²ᵣ=.050588**, but the final check rejects it without widening. Explicitly widening the centre interval to `[270,290]` returns the same better solution successfully.

   The final guard prevents false acceptance, but winning perturbations should receive the remaining expansion budget before refusal.

**VERDICT: NO-GO.**
