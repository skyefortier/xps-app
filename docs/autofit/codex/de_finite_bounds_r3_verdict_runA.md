1. **MAJOR — Post-perturb widening discards a better winner and reports success.** [fitting.py:1332](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1332)

   Reproduced with NumPy seed **36**, `n_perturb=1`, ROI `linspace(280,290,501)`, background 1000, and two DS+G components at 280/285 with amplitudes 100/75, α=0, β=.05, Gaussian width=.05. Fit one component starting at 285, amplitude 100, with only centre varying.

   | Search | Centre | Reduced χ² |
   |---|---:|---:|
   | Initial | 285.000000 | 0.058873881 |
   | Winning perturbation | 280.000018 | **0.050587926** |
   | Widened refit | 285.000000 | **0.058873883** |

   The final response is **success=true**, despite losing the better solution and increasing reduced χ² by **16.4%**. `n_perturb=2` also reproduces this. These are real optimizer results, without mocked outcomes.

   Stochastic optimization explains the worse draw; it does not justify discarding a known better feasible candidate. Preserve the incumbent while widening, and refine/check it under the enlarged bounds.

2. **MINOR — The amplitude proximity rule can still reject an exact fit.** [fitting.py:1042](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1042), [fitting.py:1402](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1402)

   Gaussian: true amplitude **10⁸**, centre 285, FWHM 1; fix centre/width, start amplitude 1000, request `amplitude_min=0`. Use `x=linspace(285+sqrt(log(9950)/(4*log(2))),290,81)` and exact Gaussian data.

   After three widenings, the ceiling is **100,502,512.56**. DE recovers **100,000,000 with zero residual**, including three perturbations, but returns **success=false** because the answer is within 1% of that ceiling.

   This is a conservative limitation of the documented proximity/budget policy, rather than the previous centre-scale bug. A legitimate optimum can indeed occupy that final 1%.

3. **MINOR — The perturbation regression test never exercises widening.** [tests/test_differential_evolution_bounds.py:289](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/tests/test_differential_evolution_bounds.py:289)

   With seed 0, this test passes even when `_expand_active_search_box` is replaced with a function that raises immediately; it receives **zero calls**. Counting boundary checks does not establish that a winning perturbation receives its remaining budget. Force that trajectory and assert both widening and retention of the better objective.

All four dispositions are implemented, including the updated `CLAUDE.md` paragraph. The negative-amplitude reproduction now recovers −100; explicit `amplitude_min=0` remains enforced. DS+G centres at either ROI edge and 0.02 eV outside recover exactly after one widening. Forced budget scenarios neither double-count nor skip the final refusal check. All four other supported methods retain an empty `search_box`.

Validation: **18 tests passed**, plus an in-memory page-like API request returning **200/success=true**. The upload test was excluded to preserve read-only execution. No files changed.

**VERDICT: NO-GO.**
