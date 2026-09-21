Reviewed HEAD `a9c0b91`, read-only.

- **BLOCKER:** None found.
- **MAJOR — Reachable false failure remains for narrow exact peaks at requested center bounds.** [fitting.py:1063](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1063)

  Reproducer:
  ```python
  x = np.linspace(1499., 1501., 201)
  y = 1000 + 1e6*np.exp(-4*np.log(2)*((x-1500)/0.05)**2)
  ```
  One Gaussian: center `1500`, requested center bounds `[1500,1500.1]`; amplitude `1e6`, minimum `0`, open maximum; fixed FWHM `0.05`, `fwhm_min=0.01`. Manual background `[[1499,1000],[1501,1000]]`.

  | Stage | χ² | Solver success |
  |---|---:|---|
  | DE | 3.09040e-25 | true |
  | Refinement | 6.54742e-5 | true |
  | Direct least_squares, same request | 6.54742e-5 | true |

  The allowance is **5.52334e-5**, so `run_fit` returns **success=false**, blaming generated amplitude limits. Refinement moves the center only **7.5e-8 eV**; its maximum residual is **0.00303 sigma**.

  Reproduced with seeds **0, 1, 4**, both **0 and 3 perturbations**, without altering solver outputs. Also reproduces at center **3000 eV**, fixed FWHM **0.1 eV**.

  The comment’s assumed bound on displacement cost is insufficient: the cost depends on peak width and center magnitude, so raw weighted power alone does not establish that ceiling. Handle the actual bound displacement rather than relying on this universal coefficient.

- **MINOR:** No additional findings. No reachable materially worse acceptance observed; no new fault-injection-only finding.

Validation: **46 tests passed; one upload test excluded to preserve read-only execution.** No files changed.

**VERDICT: NO-GO.**
