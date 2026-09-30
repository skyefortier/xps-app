# A2 round 8 — run A (commit 01cbb80; codex exec, reasoning high)

1. **MAJOR — Alternative comparisons reject equivalent Lorentzian fits using fictitious Gaussian curves.** [tests/fit_equality.py:226](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:226), [line 79](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:79).

   Gaussian and Lorentzian functions have identical parameter names. The helper reconstructs—and requires agreement between—both shapes.

   Reproduced with **two complete, certified responses**, controlling only scattered-start initialization:
   - 2,001 samples over −10…10; held Gaussian height **1e12**, FWHM **3000**.
   - Data additionally contain Lorentzians at **0/−3/+3**, heights **10/5/5**, FWHM **1**.
   - Fit the Gaussian plus one Lorentzian initially centred at **3**, holding its amplitude and width. Trust-Region, seed **123**, no background or perturbations.
   - Scatter the Lorentzian to **−0.00037 versus +0.00037**.

   Alternatives have equal areas and χ²ᵣ ≈ **2.0162910699e−12**. Their actual curves differ by **0.096127%**, within the accepted **0.1%** resolution. Nevertheless, both comparison directions reject solely because the fictitious Gaussian curves differ by **0.105679%**. Removing that comparison makes both complete responses pass.

   Resolve the component’s actual lineshape instead of requiring every signature-compatible shape.

2. **MINOR — Reconstruction exceptions silently disable alternative-curve checking.** [tests/fit_equality.py:83](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:83), [line 226](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:226).

   Recreated round 7’s real LA alternatives with **(α,β)=(1.002,0.998)** versus **(0.998,1.002)**. HEAD correctly rejects their **0.147%** curve difference. With fault injection making LA reconstruction raise, the helper **accepts those same complete responses**: exceptions become empty curve lists, and `zip` performs no comparisons. Reconstruction failure should fail the comparison explicitly.

Validation: **98 Python tests and 122 JavaScript tests passed**, including parity, V3 ordering, and focused certificate/equality checks. Additional certificate-exit, evaluation-limit, and restart-cancellation probes passed. Narrow-bound repeats passed down to spans of **1e−11**. Production code matches the recorded hash; displacement counts remain **0/202** per method. Broader sweeps were stopped for budget. No files changed.

The accepted finite-resolution ruling stands; finding 1 rejects fits within that resolution.

**VERDICT: NO-GO**
