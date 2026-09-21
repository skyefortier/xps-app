Reviewed HEAD `c3965a4`, read-only. **One reachable MAJOR finding.**

- **BLOCKER:** None found.

- **MAJOR — DE can discard an excellent requested start and return a materially worse successful fit.** [fitting.py:1038–1049](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1038)

  Unmodified-solver reproducer:
  ```python
  np.random.seed(0)
  x = np.linspace(1399.5, 1400.5, 101)
  y = 1000 + 1e6*np.exp(-4*np.log(2)*((x-1400)/0.1)**2)
  spec = dict(
      id=1, shape="gaussian",
      center=1400., center_min=1400.,
      amplitude=1e6, amplitude_min=0,
      fwhm=0.1, fix_fwhm=True,
  )
  ```
  Use manual background `[[1399.5,1000],[1400.5,1000]]`, `n_perturb=0`, and compare methods on this identical request:

  | Method | Success | χ² |
  |---|---|---:|
  | `differential_evolution` | true | **10,613,408.48969** |
  | `least_squares` | true | **0.00002851770** |

  DE returns centre **1400.893149 eV**, outside the sampled region, effectively losing the peak. The original starting parameters are never retained as a local-fit candidate.

  The round-8 **0.05 eV** request also fails with seed **0**: an observation-only trace shows DE converging at χ² **10,613,408.48967**, followed by refinement terminating on `gtol` after **3 evaluations**, with identical parameters and χ². Direct least-squares gives **0.00011407081**.

  This satisfies criterion **(b)**. The refinement itself does not worsen DE’s result; the loss occurs before refinement. Comparing against a converged local candidate from the requested start would address this independently of gate removal.

- **MINOR / fault-injection-only:** No additional findings.

Validation: **49 tests passed; one upload test excluded to preserve read-only execution.** The committed round-8 regressions pass. Fifty three-perturbation runs of the 0.05 eV request showed no catastrophic result; the finding above reproduces with zero perturbations. No files changed.

**VERDICT: NO-GO.**
