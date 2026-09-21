Reviewed HEAD `720649d`, read-only. **No BLOCKER; one MAJOR and one MINOR.**

1. **MAJOR — Internal peak IDs still materially change the fit.** [fitting.py:1152](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1152)

   Parameter names retain raw peak IDs in the hash. Reproduced through `/api/fit` using `_crowded_c1s()`, four-decimal energies, page-style flags, linear background, LM and three perturbations. Changing only IDs:

   | IDs | Seed | Third component fraction | Reduced χ² |
   |---|---:|---:|---:|
   | `1–5` | 3360525232 | 39.1723% | 1.359391 |
   | `2–6` | 784463613 | 5.1693% | 1.603333 |

   Both requests succeeded. A shared caller seed produced **byte-identical fitted curves**, isolating seed selection as the cause.

   **Page-reachable:** add and delete a temporary peak before constructing the same model. [ID allocation increments `nextId`](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/templates/index.html:5009), and deletion does not restore it. The numerical model therefore depends on editing history.

   Canonicalize parameter prefixes and constraint references by component order when hashing.

2. **MINOR — Dtype normalization hides differences in the actual weights.** [fitting.py:1157](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1157)

   With `_two_peaks()`, background `none`, LM and no perturbations, identical count values stored as float32 versus float64 both receive seed **2146306204**. However, [weight computation preserves the input precision](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1322): the first weights are `0.07537783682346344` versus `0.07537783614444091`.

   This is structural aliasing, not a hash collision. Weights are determined by count values **and computation dtype**. Page uploads use float64, so this is a direct-caller gap and non-blocking. Hash the computed weights or normalize dtype before computing them.

The four round-3 dispositions check out. Every background branch assigns `bg`; manual `None` versus `[]` now differs; NaN backgrounds introduce no hashing exception and retain solver failure handling.

Validation: **36 passed, 2 upload-writing tests excluded**. Additional probes used in-memory sessions. No files changed.

**VERDICT: NO-GO.**
