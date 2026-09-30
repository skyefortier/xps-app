# A2 round 7 — run A (commit 577e6aa; codex exec, reasoning high)

1. **MAJOR — Absolute parameter values override the stated bound-span resolution.** [tests/fit_equality.py:170](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:170)

   The tolerance uses `rel * max(bound_span, abs(a), abs(b))`, allowing tightly bounded parameters away from zero to exceed their documented resolution.

   Reproduced with **two complete, certified `run_fit` responses**, seed **123**:
   
   - 2,001 samples over −50…50; two Gaussians with fixed centre 0 and amplitude 100.
   - Both widths bounded to `[1.1, 1.101]`.
   - Data: their sum at widths **1.1003/1.1007**, plus a unit residual where `abs(x) > 20`.
   - LM, no background or perturbations; reverse the two starting widths.

   Both fits certify at χ² **1200**, preserving the swapped widths. **`assert_same_fit` accepts them.** The width difference **0.0004** exceeds the documented allowance **0.000001 by 400×**. The midpoint and nearby displacements have higher objectives, confirming separate minima.

   Use the bound span without enlarging it by the absolute value, and cover narrow bounds away from zero. This finding exceeds the accepted finite resolution; it does not challenge that ruling.

Validation: **98 focused Python tests and 122 JavaScript tests passed**. Round-6 lookup probes, certificate exits, evaluation caps, and restart cancellation passed. Production code matches the recorded hash; measurement counts and displacement maxima match the documentation. Full-suite completion was not attempted. No files changed.

**VERDICT: NO-GO**
