1. **MAJOR — Retained transitive links still disable the check.** [fitting.py:1381](/Users/skyefortier/xps-app/.claude/worktrees/feature-autofit-required-refit/fitting.py:1381) adds expressions in parameter order, which is not necessarily dependency order. Reproduced with request order `[1, 2, 4, 3]`, links `4 → 3 → 2`, and removal of unrelated peak `1`. The full fit succeeds, but rebuilding the reduced parameters raises `NameError: p3_amplitude`, returning nonblocking `ran:false`. Create **all** retained parameters without expressions first, then assign their expressions.

2. **MAJOR — The power floor rejects statistically required anchors.** [fitting.py:1393](/Users/skyefortier/xps-app/.claude/worktrees/feature-autofit-required-refit/fitting.py:1393) overrides a significant F statistic based on the total signal’s power. Reproduced with Poisson noise, seed 17, on 280–295 eV at 0.02-eV spacing: asymmetric-GL anchor `(amplitude=10⁶, center=284.5, width=0.7)` beside GL `(10¹⁰, 285.1, 2.5)`, with constant background `10⁷`. Both fits converge:
   - χ² with anchor: **679.50**; without: **1888.63**
   - **F = 264.07**, support F = **972.50**
   - Δχ² = **1209.13**, below the power floor **1444.84**, so `required:false`.

   The fitted anchor center is **284.4997 ± 0.0171 eV**. This is a resolved signal, not numerical residue. A lower-count, two-decimal synthetic case also reproduces the rejection with F ≈ 57 million. The floor needs a numerical-error justification that preserves significant removals.

The DE bounds mapping, request-derived refit seed, and pre-await anchor capture look correct. Non-DE scattered-start calls retain the same fitting behavior.

Validation: three JS tests passed. The interrupted Python selection recorded 34 passes, five read-only fixture errors, and one support-premise assertion failure that passed when rerun alone. No files changed.

**VERDICT: NO-GO.**
