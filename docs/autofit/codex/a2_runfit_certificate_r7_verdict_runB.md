# A2 round 7 — run B (commit 577e6aa; codex exec, reasoning high)

1. **MAJOR — The round-6 bounds fix admits alternative curves beyond the stated resolution.** [tests/fit_equality.py:223](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:223), [line 198](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:198).

   Alternative curves are reconstructed only to obtain centre tolerances; their shapes are never compared.

   Reproduced with **two complete `run_fit` responses**, controlling only scattered-start initialization:
   
   - 1,001 samples over −5…5; a held Gaussian of height **1e12**, FWHM **3000**, plus true LA lines at **0 and ±2**, heights **10/5/5**, FWHM **0.5**, α=β=1, m=0.
   - Fit the Gaussian and one LA component, initially centred at **0.4**. Trust-Region, seed **123**, no background or perturbations, one scattered start.
   - Both scattered starts use centre **0**, amplitude **10**, FWHM **0.5**; swap **(α, β) = (1.002, 0.998)** to **(0.998, 1.002)**.

   Both alternatives certify, with χ²ᵣ ≈ **2.001331335394111e−12** and equal areas. Their component curves differ by **0.147146% of their own height**, exceeding the documented **0.1%** resolution.

   **HEAD accepts both complete responses in either comparison direction.** Commit `2157625` rejects them. The new bound-span allowance accepts the parameter changes, while the missing alternative-curve check lets the above-resolution shape change escape. Compare reconstructed alternative curves against their own heights too.

The accepted finite-resolution ruling stands; this counterexample exceeds it.

Validation: **145 Python tests and 122 JavaScript tests passed**, plus **398 recorded parameter/curve replays**. Identifier/link, certificate-exit, evaluation-cap and restart-cancellation probes passed. The broader sweep was stopped for budget; two upload-test setups hit read-only filesystem restrictions. Recorded displacement notices remain **0/202** for each method. No files changed.

**VERDICT: NO-GO**
