# A2 round 8 — run B (commit 01cbb80; codex exec, reasoning high)

1. **MAJOR — Lorentzian alternatives are also compared as Gaussians, falsely rejecting equivalent fits.** [tests/fit_equality.py:226](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:226), [shape selection:80](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:80).

   Both shapes have identical parameter names, so reconstruction returns—and compares—both curves.

   Reproduced with complete certified responses, seed **123**, controlling only scattered-start initialization. On 1,001 samples over −5…5, use a held Gaussian of height **1e12**, FWHM **3000**, plus Lorentzians at 0 and ±2 with heights 10/5/5 and FWHM 1. Fit the dominant component and one Lorentzian initially centred at 0.4; scatter the latter to **−0.00037 versus +0.00037**.

   The alternatives have equal χ²ᵣ ≈ **4.15199845e−12**. Their actual Lorentzian curves differ by **0.0961273%** of their height, within the stated **0.1%** resolution; other comparisons pass. Nevertheless, the hypothetical Gaussian curves differ by **0.1056793%**, producing the sole rejection. Comparing only the actual shape passes. Reconstruction must preserve the component’s lineshape identity.

2. **MINOR — Very narrow bounds make a one-ULP rounding difference fail.** [tests/fit_equality.py:171](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:171).

   Reproduced with real Gaussian fits: fixed centre 0 and FWHM 1.1, amplitude bounded to **[100, 100 + 1.1e−11]**. Data are that Gaussian plus a unit residual where `abs(x) > 20`, on 2,001 samples over −50…50.

   Initializing amplitude at **100.0000000000055** and its next representable float produces two certified responses at **χ² = 1200**. Only amplitude fails: its **1.4211e−14** difference exceeds the span allowance **1.0999e−14**. This needs a machine-precision floor without restoring the previous broad `max(span, |value|)` allowance.

3. **MINOR — Reconstruction exceptions silently remove the alternative-curve check.** [tests/fit_equality.py:83](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:83), [comparison:226](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:226).

   In a comparison-time fault-injection probe, two real LA alternatives with swapped **(α, β) = (1.002, 0.998)** differ by approximately **0.147%** of their height and are correctly rejected normally. Making their evaluator raise `ValueError` changes that rejection to acceptance: reconstruction returns empty lists and `zip` performs zero curve checks. An unavailable reconstruction must fail closed.

Validation: **111 Python tests and 122 JavaScript tests passed**, plus **398 eligible recorded parameter/curve replays**. Certificate exit, cap, restart-cancellation and V3-order checks passed. Recorded displacement notices remain **0/202** for each method. Broader Python sweeps were stopped for the review budget; full-suite completion is not claimed. No files changed.

The accepted finite-resolution ruling stands.

**VERDICT: NO-GO**
