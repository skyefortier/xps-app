Reviewed HEAD `720649d`, read-only. **No BLOCKER; one MAJOR and one MINOR.**

1. **MAJOR — Peak IDs still change the numerical fit.** [fitting.py:1152](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1152)

   Parameter names embed peak IDs and enter the hash. Deleting and recreating the last peak with identical settings changes its ID through [defaultPeak](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/templates/index.html:5009), while preserving the numerical model and fitting order.

   Reproduced through `/api/fit` using `_crowded_c1s()`, four-decimal energies, page-style IDs/fix flags, linear background, LM and three perturbations:

   | Last peak ID | Seed | Second component fraction | Reduced χ² |
   |---|---:|---:|---:|
   | `"5"` | 3360525232 | 22.1339% | 1.359391 |
   | `"6"` | 3165242880 | 38.7029% | 1.345381 |

   **16.57 percentage points from an ID-only change.** Forcing caller seed 7 makes the complete results byte-identical after normalizing the returned ID. Canonicalize parameter names and expression references by component position, preserving fitting order.

2. **MINOR — Float32/float64 counts structurally alias despite different optimizer weights.** [fitting.py:1157](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1157), [fitting.py:1322](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1322)

   Equal integer-valued counts supplied as float32 versus float64 hash identically because hashing converts both to float64. Weight calculation retains the original precision. A 20-point Gaussian probe with background `none` produced seed **758295987** for both, but weights differed by up to **9.30 × 10⁻⁹**, and fitted amplitudes differed.

   Non-blocking: the page’s parser produces float64, and seeds are explicitly not identities. Weights are covered by counts **provided the computation dtype is fixed**. Normalize dtype before computation or hash the actual weights.

The Round 3 regressions pass. All background branches matched `main` in unperturbed LM probes; manual `None` versus `[]` now yields different seeds. NaN backgrounds retained the same solver failures. Endianness and array layout normalized correctly. No additional findings in the remaining diff.

Validation: **36 passed, 2 upload-writing tests excluded**; additional API probes used in-memory sessions. No files changed.

**VERDICT: NO-GO.**
