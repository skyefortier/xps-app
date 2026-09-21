Reviewed HEAD `a9c0b91`, read-only. **Two MAJOR findings, both reachable without modifying solver outputs.**

- **BLOCKER:** None found.

- **MAJOR — The tighter allowance still rejects converged exact fits.** [fitting.py:1063](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1063)

  Reproducer: NumPy seed `4`; `x=linspace(1399.75,1400.25,101)`; `y=1000 + 1e6*exp(-4*log(2)*((x-1400)/0.05)**2)`; manual background `1000`. One Gaussian:
  ```python
  dict(id=1, shape="gaussian",
       center=1400., center_min=1400.,
       amplitude=1e6, amplitude_min=0,
       fwhm=0.05, fwhm_min=0.05, fix_fwhm=True)
  ```
  With `n_perturb=0`, DE finds χ² **6.59249e-25**. Successful refinement nudges the centre to **1400.0000000700002**, giving χ² **0.00011407081**. The allowance is only **0.00010745670**, so `run_fit` returns **`success=false`**. Direct `least_squares` accepts the same request with essentially identical refinement χ².

  The bound-nudge cost depends on peak width and sampled region; the comment’s assumed power-relative ceiling does not hold generally. I also reproduced false rejection with the default **0.1 eV** width on a cropped Gaussian tail.

- **MAJOR — Perturbation ranking can replace that exact candidate with a catastrophically worse successful fit.** [fitting.py:1313](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1313)

  Use the same request and seed with **`n_perturb=3`**. The routine holds the exact candidate above but marks it unverified. A later DE search and its refinement both converge at χ² **10,613,408.48967**, with centre **1401.736927**—outside the sampled region—and effectively zero peak contribution.

  Because verification status precedes χ² in candidate ranking, this result displaces the exact candidate and returns **`success=true`**. Reproduced in three repeated traced runs; the trace only observed real solver results. An uninstrumented run also reproduced it.

- **MINOR / fault-injection-only:** No additional findings reported.

Validation: **46 tests passed; one upload test excluded to preserve read-only execution.** NumPy `2.4.4`, SciPy `1.17.1`, lmfit `1.3.4`. No files changed.

**VERDICT: NO-GO.**
