Reviewed HEAD `2fcee60`, read-only. **No BLOCKER; one MAJOR and three MINOR findings.**

1. **MAJOR — Ignored background settings still materially change the fit.** [fitting.py:1149](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1149)

   `endpoint_avg` enters the hash even for a linear background, which ignores it. The [page always sends it](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/templates/index.html:7122).

   Reproduced through `/api/fit` using `_crowded_c1s()`, page-style IDs/fix flags, four-decimal energies, full-window linear background, LM and three perturbations. Changing only endpoint averaging:

   | `endpoint_avg` | Seed | Third component fraction | Reduced χ² |
   |---|---:|---:|---:|
   | 3 | 577378209 | 45.834% | 1.368019 |
   | 4 | 3262776583 | 26.088% | 1.344761 |

   That is a **19.75 percentage-point** change from a page-reachable no-op. A separate direct-call comparison with a shared caller seed produced byte-identical fitted curves. Hashing the computed background, instead of inactive/raw background settings, would address this.

2. **MINOR — Expression evaluation during hashing changes an API failure from 422 to 500.** [fitting.py:1354](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1354)

   Concrete request: a Gaussian master and a constrained `pseudo_voigt_gl` child with default `fix_fwhm=True`. The child references nonexistent `p1_gl_ratio`.

   Against `main`, evaluation occurs inside the fitting exception boundary: `RuntimeError` → **HTTP 422**. On HEAD, hashing reads `par.value` outside that boundary: `NameError` → **HTTP 500**. Confirmed through the API. Validate expression dependencies or preserve the exception boundary around their evaluation.

3. **MINOR — Irrelevant fixed-parameter bounds still change the seed.** [fitting.py:1147](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1147)

   With `_crowded_c1s()`, fix the first peak’s asymmetry at `0.1`; change only its `asymmetry_max` from `0.5` to `1.0`. Seeds change from `2442189631` to `291841696`, although the bound cannot affect this fixed value. Fitted curves happened to remain identical in this probe. This is an API-level canonicalization gap; I did not establish a normal page action that edits these bounds.

4. **MINOR — Chained constraints can hash stale, overridden starting values.** [fitting.py:1147](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1147)

   For Gaussian peaks ordered `[1, 3, 2]`, constrain `2.center = 1.center + 1` and `3.center = 2.center + 1`. Changing the ignored requested `2.center` from `4` to `7` changes seeds `3811630938` → `429646976`: peak 3 is evaluated before peak 2’s dependency resolves. The unperturbed fitted curves are byte-identical. Calling `params.update_constraints()` before hashing makes both hashes agree. No normal page workflow producing this chain was established.

The requested structural-alias check also found `background_method="manual"` with `manual_bg=None` versus `[]`: both hash identically, but produce zero versus linear backgrounds. This is non-blocking because the seed is explicitly not an identity.

No use-before-assignment of `random_seed` was found. The Gaussian regression passes, the production draw pin rejects an in-memory generator replacement, and the requested wording corrections are present.

Validation: **33 passed; two upload-writing tests excluded** to preserve read-only operation. Additional API probes used in-memory sessions. No files changed.

**VERDICT: NO-GO.**
