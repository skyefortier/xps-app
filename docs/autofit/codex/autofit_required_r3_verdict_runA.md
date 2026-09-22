- **MINOR — The “exactness” guard still rejects a resolved synthetic anchor.** [fitting.py:1398](/Users/skyefortier/xps-app/.claude/worktrees/feature-autofit-required-refit/fitting.py:1398). Reproduced using the existing test grid, bounds, background and `n_perturb=3`: Graphite amplitude **1**, plus GL components `(amplitude, center, width) = (1e10, 285.1, 1.9)` and `(2300, 286.4, 1.4)`, with counts rounded to two decimals.

  Both local methods converge and support passes, yet both return `required:false`:
  
  | Method | χ² with | χ² without | F |
  |---|---:|---:|---:|
  | LM | 5.804e−11 | 1.713e−9 | 4208 |
  | Trust-Region | 5.804e−11 | 4.276e−10 | 940 |

  The exactness threshold is **1.116e−8**. LM resolves the anchor amplitude to **1.009 ± 0.023**, but its reduced fit differs from the data by up to **0.586**, changing **318 channels** after two-decimal rounding. This is not floating-point-exact reproduction. The remaining power-relative tolerance can therefore override significant removal costs. This reproduction is a high-dynamic-range synthetic case, not a Poisson-noise failure.

The expression fix clears the reported reverse-order chains. I found no page-generated expression path outside the `constrain_to` closure. Both round-2 anchor regressions pass; genuinely lossless, unrounded duplicate components remain correctly rejected under both local methods.

Validation: **12 Python tests and 23 JavaScript tests passed**; one API fixture was blocked by read-only filesystem restrictions. No files changed.

**VERDICT: NO-GO.**
