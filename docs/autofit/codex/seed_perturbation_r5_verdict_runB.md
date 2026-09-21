Reviewed HEAD `d98777d`, read-only. **No BLOCKER or MAJOR; one non-blocking MINOR.**

1. **MINOR — Signed zero in arrays still changes the seed.** [fitting.py:1172](/Users/skyefortier/xps-app/.claude/worktrees/fix-seed-perturbation/fitting.py:1172)

   Array hashing preserves the sign bit of zero. With `_two_peaks()`, first count set to `0.0` versus `-0.0`, background `none`, LM, and one perturbation, seeds are **1380581364 versus 3880120117**. Both fits succeed with identical fitted curves.

   The CSV path preserves this distinction: the page formats `-0.001` as `-0.00`, and the backend parser retains negative zero. This is separate from the previously cleared JSON parameter normalization. Normalize zero signs in arrays before hashing. No material fit excursion was demonstrated.

The requested adversarial checks otherwise cleared:

- **Component order:** not a numerical no-op. Reversing `_crowded_c1s()` changes unperturbed LM reduced χ² from **1.501267335 to 1.497448725** on both `main` and HEAD. Preserving order in the seed is justified. Reordering across the master/slave partition preserves seed and result when sorting restores fitting order.
- **Prefix rewriting:** alias-like IDs, underscores, embedded prefixes, and Unicode IDs preserved seeds and fitted curves. Regex metacharacters are rejected by lmfit before hashing.
- **Entry conversion:** numeric lists and object arrays now succeed where `main` raised errors. Masks are discarded; however, `main` already mishandled masked counts, and no repository caller supplying masked arrays was found.
- **Remaining diff:** no additional findings.

Validation: **41 passed, 2 upload-writing tests excluded**. Additional probes compared `main` and HEAD in memory. No files changed.

**VERDICT: GO.**
