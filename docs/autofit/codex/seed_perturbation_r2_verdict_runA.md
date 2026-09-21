Reviewed HEAD `86a5b62` against `main`. No files changed. **No BLOCKER or MAJOR found in the disclosed seeding scope.**

1. **MINOR — Ignored shape parameters still change the fit.** [fitting.py:1142](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1142)

   Reproduced using `_crowded_c1s()`, with the fifth peak changed to Gaussian, page-style IDs/fix flags, full-window Shirley background, LM, and three perturbations. Changing only that Gaussian’s ignored `fix_gl_ratio` from `false` to `true` produced:

   | | `false` | `true` |
   |---|---:|---:|
   | Seed | 179791185 | 2288030602 |
   | Reduced χ² | 1.476951 | 1.460414 |
   | Third component fraction | 9.017805% | 23.379956% |

   The constructed parameters, bounds and vary flags were identical. This is page-reachable: [peakToBackendSpec](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/templates/index.html:6203) always sends `fix_gl_ratio`, including after switching away from GL.

   Per-shape filtering is worthwhile given the **14.36 percentage-point** change. Prefer hashing effective constructed parameters, including expressions and bounds, over maintaining another partial list: constrained peaks also ignore otherwise active fields. This does not break replay of literally identical requests, but disposition 2 only partially resolves semantic no-op edits.

2. **MINOR — Some reproducibility statements still contradict the disclosure.** [fitting.py:1228](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1228), [test_fit_reproducibility.py:12](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/tests/test_fit_reproducibility.py:12), [CLAUDE.md:329](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/CLAUDE.md:329)

   The implementation comment still promises an “identical fit”; the test docstring still attributes the observed behavior to OpenBLAS. Both installed libraries report Apple Accelerate.

   Also, a deterministic perturbation base should be described as a **mitigation**, not an established cure. In an in-memory experiment replacing `result.params.copy()` with `all_params.copy()`, all four starting points were exactly identical across three runs, but the returned results still differed. Trust-Region arithmetic and candidate selection remain relevant.

Dispositions **1, 3 and 4 check out**: central normalization/validation closes the method bypass; caller seeds are validated and consumed from copied dictionaries; the revised test recovers factors from each press’s own first solution. Name exclusion, sorted anchors and the stated seed normalizations are implemented.

For the requested adversarial checks:

- **Randomness:** unsupported analyze methods returned HTTP 400. `BasinHopping`, `basinhopping` and differential evolution completed without changing NumPy’s global RNG state. I found no uncontrolled numerical RNG path. Other analyze algorithms use their separate explicit `rng_seed`, rather than `run_fit.random_seed`.
- **Whitelist:** a broader source audit found no consumed peak-spec key missing. However, absent/null are not universally fit-equivalent: absent `amplitude_min` produces a zero lower bound; explicit null leaves it unbounded. Both hash identically. Sharing draws is harmless here because the seed is not an identity.
- **Callers:** no repository caller relies on a newly rejected method.
- **Trust-Region:** eight identical crowded-model requests retained seed `2213317210` but returned differing results. I also reproduced alignment-dependent dot products. The disclosure’s mechanism is supported; I did not independently reproduce the 29-point excursion or rerun the 202-target measurements. I found no sound, small change guaranteeing repeatability. A controlled arithmetic backend needs end-to-end validation; [oneMKL’s guarantees are conditional](https://www.intel.com/content/www/us/en/docs/onemkl/developer-reference-c/2026-0/conditional-numerical-reproducibility-control.html). The revised version caveat agrees with [NumPy’s compatibility policy](https://numpy.org/doc/stable/reference/random/compatibility.html).

Validation: **31 passed, 2 upload tests excluded** to preserve read-only operation. I did not independently rerun the full suite.

This approves the disclosed seeding improvement; it does **not** certify completion of the original identical-answer requirement for Trust-Region.

**VERDICT: GO.**
