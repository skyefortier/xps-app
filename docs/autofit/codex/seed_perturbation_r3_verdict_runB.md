Reviewed HEAD `2fcee60` against `main`, read-only. **No BLOCKER; one MAJOR and two MINOR findings.**

1. **MAJOR — Inactive background settings still change component fractions.** [fitting.py:1149](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1149)

   `endpoint_avg` is hashed even when the selected background ignores it.

   Reproduced through `/api/fit` using `_crowded_c1s()`, four-decimal energies, page-style string IDs/fix flags, full-window **linear** background, LM, and three perturbations:

   | Endpoint average | Seed | Reduced χ² | Third component fraction |
   |---|---:|---:|---:|
   | 1 | 1846958903 | 1.459443 | 16.9378% |
   | 3 | 577378209 | 1.368019 | 45.8342% |

   Background arrays were identical. Forcing caller seed 7 made the **entire returned results byte-identical**, isolating seed selection as the cause.

   **Page-reachable:** select Shirley, change endpoint averaging, then return to Linear. The control becomes disabled, but [the request builder still sends its retained value](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/templates/index.html:7122). This recreates the previous hidden-setting problem, with a **28.90 percentage-point** excursion. Hash the computed background or normalize settings according to their actual effect.

2. **MINOR — Expression evaluation during hashing changes an API failure from 422 to 500.** [fitting.py:1147](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1147)

   Concrete request: Gaussian master, linked `pseudo_voigt_gl` child, `fix_fwhm=true`. The child references the nonexistent `p1_gl_ratio`.

   Against `main`, `/api/fit` returns **422** through the solver’s exception wrapper. HEAD evaluates `par.value` while hashing, raising `NameError` outside that wrapper and returning **500**. Confirmed using the same in-memory API session. Validate expression dependencies or preserve exception translation around this evaluation.

3. **MINOR — Parameter hashing still includes mathematically irrelevant or stale state.** [fitting.py:1147](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1147)

   Two concrete `_two_peaks()` probes, linear background, LM, no perturbations:

   - Fix the first center at 284.6; change its lower bound from 282 to 283. Seeds change **1363686243 → 3826073377**, while results are byte-identical apart from the echoed bound and seed.
   - Use fitting order `[1,2,3]`, with constraints `2→3→1`. Change peak 3’s overridden starting center from 283 to 287. Seeds change **2843999469 → 282325545** because hashing reads peak 2’s value before resolving peak 3. The fitted solution is unchanged.

   These were API-level probes; I established neither an ordinary page workflow nor a material excursion. Resolve constraints before hashing and normalize irrelevant fixed-parameter bounds.

The requested **structural same-seed counterexample** also exists at [fitting.py:1144](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1144): with manual background, `manual_bg=None` produces zero background, while `manual_bg=[]` selects the linear fallback. Both receive seed **3265821032** on `_two_peaks()` with LM and no perturbations. This is deterministic aliasing, not a 32-bit collision; sharing draws is harmless while the seed remains explicitly unsuitable as an identity.

No use of `random_seed` before assignment was found. The inactive-shape fix and revised disclosures check out. The production draw pin correctly failed when I replaced the production generator in memory.

Validation: **33 passed, 2 upload-writing tests excluded**. No files changed; full suite not independently rerun.

**VERDICT: NO-GO.**
