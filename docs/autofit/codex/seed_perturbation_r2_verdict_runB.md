Reviewed HEAD `86a5b62` against `main`, read-only.

1. **MAJOR — Inactive shape settings still change the scientific result.** [fitting.py:1142](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1142)

   The whitelist includes keys ignored by the selected shape. This is page-reachable: [peakToBackendSpec:6203](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/templates/index.html:6203) always sends `fix_gl_ratio`, including after switching a GL peak to Gaussian.

   **Reproduced through `/api/fit`:** use `_crowded_c1s()`, make the second component Gaussian, remove its `gl_ratio`, use page-style IDs/fix flags and four-decimal energies, Shirley background, `leastsq`, three perturbations. Changing only that Gaussian’s ignored `fix_gl_ratio` flag produced:

   | | `false` | `true` |
   |---|---:|---:|
   | Seed | 3345909016 | 33467748 |
   | Reduced χ² | 1.489252 | 1.433802 |
   | Third component area fraction | 8.101% | 52.990% |

   This isolates seed selection from Trust-Region jitter. Disposition 2 fixes names but leaves equivalent models dependent on hidden shape history. **Shape-aware hashing is worth doing**, including inactive flags and parameters ignored by constraints. Hashing the effective constructed parameters would avoid maintaining a second interpretation of the specs.

2. **MINOR — The draw pin does not pin production perturbations.** [tests/test_fit_reproducibility.py:340](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/tests/test_fit_reproducibility.py:340)

   It constructs an independent generator, never observing `run_fit`. In an in-memory mutation, I replaced production `rng = perturb_rng` with `np.random.default_rng(123)`: the seed pin, draw pin, and actual-start repeatability test all still passed. Pin draws observed from `run_fit` for a known request or caller seed, and verify another seed changes them. The revised Trust-Region ratio comparison itself correctly addresses Round 1.

3. **MINOR — Reproducibility disclosure remains contradictory in two places.** [fitting.py:1226](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1226), [tests/test_fit_reproducibility.py:12](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/tests/test_fit_reproducibility.py:12)

   The implementation comment still promises an “identical fit”; the test docstring still attributes the observed arithmetic to OpenBLAS. This installation reports Apple Accelerate. Both should agree with CLAUDE.md’s narrower claim.

The remaining checks were satisfactory:

- **Methods and randomness:** unsupported analyze methods returned HTTP 400; mixed-case basinhopping ran seeded. All five supported methods preserved NumPy’s global RNG state in the API probe. Autofit’s other sampling paths use their own explicit `rng_seed`. I found no existing caller relying on a newly rejected method.
- **Caller seeds:** copied, consumed, validated and reinjected correctly. The deterministic methods work with overrides.
- **Hash coverage:** no currently consumed spec key was missing. However, absent and null are not universally equivalent to fitting: absent `amplitude_min` gives a zero floor; explicit null leaves it open. Both receive the same seed. Sharing draws is harmless here, but the documentation’s equivalence explanation is inaccurate.
- **Trust-Region:** I reproduced `norm` returning different output for identical input in the instrumented TRF trace. Five identical seeded fits differed by up to **0.00408 pp** locally; I did not independently reproduce the reported 29 pp event. Recomputing the saved final-run records matched **145/202** identical Trust-Region targets, **two above 0.01 pp**, worst **0.29765 pp**, and **202/202** identical LM targets.

I found no sound small change that guarantees Trust-Region repeatability. A deterministic restart base removes one amplification path, but solver arithmetic and candidate selection can still diverge. A controlled reproducible numerical backend requires end-to-end validation; [oneMKL’s guarantees are conditional](https://www.intel.com/content/www/us/en/docs/onemkl/developer-reference-c/2026-0/conditional-numerical-reproducibility-control.html). The NumPy upgrade caveat is also [correct](https://numpy.org/doc/2.0/reference/random/compatibility.html).

Validation: **31 passed, 2 upload-writing tests excluded** to preserve read-only operation; additional API probes used in-memory sessions. No files changed.

**VERDICT: NO-GO — disposition 2 still permits a page-reachable no-op setting to change component fractions materially.**
