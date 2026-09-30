# A2 round 1 — run A (commit 79dfa58; codex exec, reasoning high)

1. **MAJOR — The equality helper accepts distinct certified minima.** [tests/fit_equality.py:69](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:69), [line 85](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:85).

   Reproduced with real `run_fit` responses, both using seed 123: a held Gaussian of amplitude 1,000,000 plus a small Gaussian of amplitude 10 and FWHM 0.1 eV, fitted over −500…500 eV. The small component reaches separate certified minima at −0.25 and +0.25 eV. Both have χ² ≈ 41.839; the intervening point has χ² ≈ 384.558. **`assert_same_fit` accepts the complete responses.**

   The centre tolerance is 1 eV, while every component curve receives the dominant signal’s tolerance. This hides a five-linewidth relocation of the small component. The owner’s explicit different-minimum rejection condition is unmet. Component comparisons need scales that preserve small components’ identity.

2. **MAJOR — Non-finite curve regressions silently pass.** [tests/fit_equality.py:70](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:70).

   Starting from a real successful response, replacing one `fitted_y` sample with NaN passes. Replacing one component’s `y` sample with `None` also passes: NumPy converts it to NaN, `max` becomes NaN, and `NaN > tolerance` is false. One invalid sample can therefore hide arbitrary differences elsewhere in that curve. Validate element types and finite-value masks before computing differences.

3. **MINOR — The different-minimum proof can pass solely because the seeds differ.** [tests/test_fit_equality.py:43](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/test_fit_equality.py:43).

   The two-basin test produces seeds `1228785762` and `1978416682`. I confirmed that otherwise identical numerical responses with those seeds satisfy its expected rejection. Thus this test still passes if numerical discrimination breaks. Pin the same explicit seed and require rejection attributable to fitted quantities; add the counterexample above.

The focused checks passed: **19 Python tests and 122 JavaScript tests**. Additional probes confirmed cancellation during a certificate restart raises `FitCancelled`, and the non-finite, raising, capped and exhausted exits return the expected verdicts. V3’s pre-certificate search order appears preserved.

The committed measurements support **0/202 displacement notices**, with maxima **0.04299 eV TR / 0.01059 eV LM**. The four parity exceptions remain constrained by regenerated numerical fixtures; Scan_6’s 50-restart failure is explicitly pinned. That cap remains an acknowledged limitation for “Refit my current peaks,” rather than a false success.

**Scan_5 check: No, not reliably for the specific 33.9/51.9 pair.** The recorded check names 51.9 from 33.9; from 51.9 it finds 17.26 instead. It signals non-uniqueness both ways.

No files changed.

**VERDICT: NO-GO.**
