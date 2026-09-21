Reviewed HEAD `c3965a4`, read-only.

- **BLOCKER:** None found.
- **MAJOR — DE can return a materially worse successful fit than direct least-squares from the same start.** [fitting.py:1038](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1038)

  Reproducer: NumPy seed **0**, `n_perturb=0`:
  ```python
  x = np.linspace(1399.75, 1400.25, 101)
  y = 1000 + 1e6*np.exp(-4*np.log(2)*((x-1400)/0.05)**2)
  spec = dict(
      id=1, shape="gaussian", center=1400., center_min=1400.,
      amplitude=1e6, amplitude_min=0,
      fwhm=.05, fwhm_min=.05, fix_fwhm=True,
  )
  ```
  Use manual background `[[x[0],1000],[x[-1],1000]]`.

  | Result | Success | χ² |
  |---|---|---:|
  | DE search | true | 10,613,408.489669 |
  | Refinement / returned result | true | 10,613,408.489669 |
  | Direct least_squares | true | 0.000114071 |

  DE places the centre at **1401.121546**, outside the ROI. Refinement terminates on `gtol` after **3 evaluations**, retaining effectively zero peak contribution. The original start’s useful solution is never fitted locally or retained as a competing candidate.

  Reproduced without modifying solver outputs. Also persists with **three perturbations** when passing the supported DE option `fit_kws={"seed": 0}`. This meets criterion **(b)**; it is a search-basin failure, not deterioration during refinement. Competing against a local fit from the request’s original start would address this case without restoring the removed gate.

- **MINOR / fault-injection-only:** No additional findings.

Validation: **49 tests passed; one upload test excluded to preserve read-only execution.** Round 8 regression tests pass. No files changed.

**VERDICT: NO-GO.**
