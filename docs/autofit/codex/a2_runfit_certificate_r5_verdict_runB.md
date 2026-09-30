# A2 round 5 — run B (commit 68fbf47; codex exec, reasoning high)

1. **MAJOR — DS+G alternatives still borrow the returned fit’s width, accepting distinct minima.** [tests/fit_equality.py:154](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:154)

   `alternative_widths()` only replaces the inherited scale when a component has `fwhm`. DS+G has `beta` and `m_gauss` instead.

   Reproduced with **two complete `run_fit` responses**, seed 123, controlling only `_scattered_start`; fitting, certification and reporting remained real. Construction: 20,001 points over −500…500, a held Gaussian of height 1e6/FWHM 3000, baseline 0.05, and two height-10 DS+G lines at ±0.15 (`alpha=0`, `beta=0.05`, `m_gauss=0`). The fitted DS+G component starts at −10000 with centre bounds ±1e6.

   The certified alternatives reach **−0.145181 and +0.145182 eV**, each with sampled width **0.1 eV**. Profiling amplitude gives χ² ≈ **0.000213461** at either minimum versus **0.000351638** at centre zero; nearby displacements also increase χ².

   **`assert_same_fit` accepts both complete responses.** Their 0.290363 eV separation exceeds the alternatives’ stated allowance, **0.0001 eV**, by approximately **2,900×**. The helper instead permits **1.00005 eV**, inherited from the returned component. Derive alternative widths from their actual lineshapes and parameters.

2. **MAJOR — Bounds inheritance stops after one link, rejecting equivalent chained fits.** [tests/fit_equality.py:96](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:96)

   Reproduced with three LA components linked **`p4_m → p3_m → p2_m`**, including production-generated amplitude factors **0.75** and centre offsets **10.9 eV**.

   Two real fits initialized with master `m=0.001` and `m=0.300` both certify, with **identical component curves and χ² = 1588.686916887097**. The master’s `[0,499]` bounds permit a difference of **0.499**. The helper accepts the master and first linked copy, but rejects **only `individual_peaks.2.params.m.value`**: `p3_m` has no bounds, so the second link falls back to a relative allowance of **0.0003**. Resolve dependencies transitively to their bounded master.

Validation: **99 focused Python tests and 122 JavaScript tests passed**; a broader sweep was stopped after two additional passes. Certificate exit, cancellation and V3-order checks passed. All **398 eligible recorded parameter/curve replays** passed, including the four round-4 failures; these records contain partial responses. Production fitting code matches the recorded hash, and displacement measurements remain **0/202** for both methods. No files changed.

The accepted finite-resolution ruling stands; finding 1 substantially exceeds that resolution.

**VERDICT: NO-GO**
