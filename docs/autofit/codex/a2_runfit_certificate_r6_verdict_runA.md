# A2 round 6 — run A (commit 2157625; codex exec, reasoning high)

1. **MAJOR — Scattered-start alternatives lose parameter bounds, rejecting equivalent minima.** [tests/fit_equality.py:204](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:204), [line 170](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:170).

   Bounds are retrieved only from `{value, min, max}` records. Alternatives contain bare parameter values, so their bounded parameters fall back to relative comparison.

   Reproduced with **two complete `run_fit` responses**, seed **123**, controlling only `_scattered_start`; fitting, certification, and reporting remained real:

   - 1,001 samples over −5…5 eV; a held Gaussian of height **1e6**, FWHM **3000**, plus LA lines at **±0.25 eV**, heights **10/20**, FWHM **0.1**, α=β=1.
   - Fit the dominant Gaussian and one LA component, initially at the left line. No background or perturbations; one controlled scattered start at the right line.
   - Change only that start’s free LA `m`: **0.001 → 0.300**.

   Both returned fits have χ² **0.0031365232793750344**. Both alternatives certify at χ²ᵣ **7.857136370332042e−7**, with **exactly identical component curves**.

   Nevertheless, the helper rejects **only** `starts.alternatives.0.components.1.params.m`. The stated `[0,499]` bound-span rule permits **0.499**, but the alternative receives an allowance of **0.0003**. Recover alternatives’ parameter bounds and linked dependencies from the corresponding model metadata.

Validation: **106 Python tests and 122 focused JavaScript tests passed**. All **398 eligible recorded parameter/curve replays** passed. Seven-shape, negative/zero-curve, unmatched/raising-shape, certificate-exit, cap, and restart-cancellation probes passed. Real three-component link chains passed with free and fixed masters, including amplitude factors and centre offsets. Production code matches the recorded hash; displacement notices remain **0/202** for both methods.

The accepted finite-resolution ruling stands. Full-suite completion was not claimed: the broader Python sweep was stopped for budget; full JavaScript backend-parity checks encountered the read-only temporary-directory restriction. No files changed.

**VERDICT: NO-GO**
