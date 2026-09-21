Reviewed HEAD `3ab564c` against `35b950e`, read-only. **18 tests passed**; the upload test was excluded. Additional API checks used in-memory sessions. No files changed.

1. **MAJOR — Widening discards a better fit and reports success.** [fitting.py:1332](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1332)

   Reproduced twice with NumPy seed **36**, `n_perturb=1`, ROI `linspace(280,290,501)`, manual background 1000, and two DS+G components at 280/285 with amplitudes 100/75, α=0, β=.05, Gaussian width=.05. Fit one component with amplitude 100 and shape fixed, centre free, starting at 284.7.

   | Stage | Centre | Reduced χ² |
   |---|---:|---:|
   | Initial search | 285.000000 | 0.058874 |
   | Winning perturbation | 280.000018 | **0.050588** |
   | Widened refit, returned successfully | 285.000000 | **0.058874** |

   Stochastic variation explains the worse draw, but does not justify discarding a known better candidate. Preserve the incumbent and revalidate/refine it under the expanded bounds before selecting the result. Merely changing its bounds would not establish convergence.

   The initial widening assignment at [fitting.py:1264](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1264) has the same problem: seed **2**, `n_perturb=0`, replaces χ²ᵣ≈0.050588 with **0.082684**, returning centre **279.048961**, `success=true`.

2. **MAJOR — The amplitude tolerance still rejects an exact fit after exhausting widening.** [fitting.py:1042](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1042), [fitting.py:1402](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1402)

   Reproduction: Gaussian centre 285/FWHM 1 fixed, true amplitude **995,000**, starting amplitude 1, `amplitude_min=0`; ROI `linspace(286.8221197003983,287.8221197003983,81)`. Add a manual background of 1000; use seed 4 and three perturbations.

   Generated ceilings progress **1,000 → 10,000 → 100,000 → 1,000,000**. DE recovers **995,000**, χ²ᵣ≈**1.22×10⁻³⁰**, but returns `success=false`: the 5,000 gap is inside the 10,000 tolerance.

   Thus a legitimate exact amplitude can occupy the final ceiling’s 1% band. Proximity alone does not establish that the search bound constrained the answer.

3. **MINOR — The perturbation regression test does not exercise widening.** [tests/test_differential_evolution_bounds.py:289](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/tests/test_differential_evolution_bounds.py:289)

   The test still passes when the entire post-perturb widening block is replaced **in memory** with one `_active_search_sides` call. It needs a controlled winning boundary result, assertions about expanded bounds and remaining budget, and a worse-refit case.

Dispositions 1, 2, and 4 match the code and fix their archived reproductions. Disposition 3 supplies the remaining budget, but introduces finding 1. Page-style `amplitude_min=0` remains nonnegative; `null` recovers −100. DS+G centres at either ROI edge and just outside either edge recover exactly after one widening. Controlled budget checks confirmed three total expansions across both phases and final refusal on exhaustion. No other-method path populates `search_box`.

**VERDICT: NO-GO.**
