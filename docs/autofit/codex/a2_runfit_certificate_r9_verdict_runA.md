# A2 round 9 — run A (commit fe2120f; codex exec, reasoning high)

1. **MAJOR — Ambiguous lineshape identification rejects byte-identical certified fits.** [tests/fit_equality.py:103](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:103), [rejection at line 249](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:249).

   Reproduced with two ordinary `run_fit` calls, without fault injection or controlled scattered starts:

   - 1,001 samples over −5…5; data contain a held Gaussian of height **50**, FWHM **1e9**, plus Gaussians at **−0.25/+0.25**, heights **10/8**, FWHM **0.1**.
   - Fit the held component (`fwhm_max=1e10`) plus one Gaussian initially at **+0.25**, amplitude **8**, fixed FWHM **0.1**, centre bounds **[−1,1]**.
   - LM, seed **123**, no background or perturbations, **10 scattered starts**.

   Both responses certify, list one alternative, and are **byte-identical when JSON-serialized**. Nevertheless, `assert_same_fit(a, b)`—and comparison with a deep copy—fails solely at `starts.alternatives.0.components.0`.

   The broad Gaussian and corresponding Lorentzian differ by only **7.1e−15 counts** on this grid. Both satisfy the identification tolerance, so `_lineshape_of` returns `None`. The fail-closed path mistakes ambiguous identity for an unreconstructible curve.

   Preserve the actual lineshape identity in the comparison’s inputs. Curve matching cannot always recover it uniquely.

Validation: the **59-test parity battery plus 12 certificate tests passed**, as did focused equality checks and **122 JavaScript tests**. Missing/unmatched shapes, non-finite returned curves, mismatched alternative parameters, reconstruction exceptions, evaluation caps, and restart cancellation behaved as intended. Production code matches the recorded hash; displacement notices remain **0/202** for each method. Broader sweeps were stopped for budget. No files changed.

The accepted finite-resolution ruling stands; this finding rejects identical responses.

**VERDICT: NO-GO**
