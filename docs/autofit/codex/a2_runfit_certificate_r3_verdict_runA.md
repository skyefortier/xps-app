# A2 round 3 — run A (commit 03916fa; codex exec, reasoning high)

1. **MAJOR — Distinct certified minima still compare equal.** [tests/fit_equality.py:96](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:96), [line 152](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:152).

   Reproduced using `_unsupported_pair`’s construction with both narrow lines reduced to height **10**, starting amplitude **10**, and FWHM fixed at **0.1 eV**. Both complete `run_fit` responses use seed **123**, LM, and no perturbations. They certify at **−0.25 and +0.25 eV**, five linewidths apart, yet **`assert_same_fit` accepts them**.

   Both have χ² ≈ **249842.5162271602**. Profiling amplitude at the intervening centre gives χ² **249842.5163779412**; nearby positions also have higher objectives, confirming separate minima.

   Their weighted curve separation is **0.000301562**, below the helper’s **0.024984252** allowance. Centre σ ≈ **17.489 eV** gives an allowed displacement ≈ **0.782 eV**, exceeding the actual **0.5 eV** relocation.

   Thus `10 × ftol × χ²` exceeds a constructible separation between distinct minima. A restart’s stopping criterion does not establish basin identity; the local quadratic/Cauchy–Schwarz argument cannot supply that guarantee. The owner’s explicit condition remains unmet.

2. **MAJOR — Component curves and areas can regress arbitrarily without detection.** [tests/fit_equality.py:179](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:179), [line 240](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:240).

   Starting from the tests’ real `_two_peaks()` response, independently:
   - Adding **1,000,000 counts** to `individual_peaks[0].y[40]` passes.
   - Multiplying `individual_peaks[0].params.area.value` by **100** passes.

   Determined components receive only a non-finite-mask check on their curves; area values are skipped altogether. Nothing verifies consistency with parameters or the total curve. Consequently, the rewritten reproducibility tests can miss broken component rendering and quantification output.

   The new flat-direction test changes component arrays while leaving parameters unchanged, so it does not validate the claimed sigma-based treatment of an actual fitted trade.

3. **MINOR — Different non-finite uncertainties compare equal.** [tests/fit_equality.py:250](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:250).

   On copies of a real response, setting the same centre’s `stderr` to **NaN** in one and **+∞** in the other passes. Both fail `_finite`, and neither subsequent branch compares their values. This violates the stated non-finite correspondence rule.

Validation: **40 focused Python tests, 59 parity-battery tests, and 122 JavaScript tests passed**. I stopped the broader sweep to bound review time. Direct certificate-exit and restart-cancellation probes behaved correctly. Production certificate/UI code is unchanged since round 2; V3 ordering remains intact. Committed measurements confirm the corrected note’s counts and **0/202 displacement notices**, with maxima **0.04299 eV TR / 0.01059 eV LM**. Scan_5 still flags non-uniqueness without reliably identifying the specific 33.9/51.9 pair in both directions. No files changed.

**VERDICT: NO-GO**
