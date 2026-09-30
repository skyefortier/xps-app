# A2 round 3 — run B (commit 03916fa; codex exec, reasoning high)

1. **MAJOR — Distinct certified minima still compare equal.** [tests/fit_equality.py:96](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:96), [line 152](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:152).

   Reproduced with complete `run_fit` responses, both seed **123**: use the existing `_unsupported_pair` construction, reducing both true narrow lines from height 500 to **10**, with initial amplitude 10. Both fits certify at centres **−0.25 and +0.25 eV**, five linewidths apart.

   - χ² at either minimum: **249842.516227160**.
   - χ² at centre zero, after profiling amplitude and width: **249842.516377928**. Nearby centre displacements also increase χ².
   - Weighted curve separation: **0.000301562**, below the allowed **0.0249843**.
   - Allowed centre difference from sigma: **0.782115 eV**, exceeding the actual **0.5 eV**.

   **`assert_same_fit` accepts them.** These are separate minima, not zero-amplitude jitter. Certification supplies no lower bound on separation between distinct minima; the local covariance argument cannot establish global basin identity. The owner’s explicit condition remains unmet.

2. **MAJOR — The stderr rule rejects recorded same-minimum repeat presses.** [tests/fit_equality.py:254](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:254).

   The committed [V3 LM run, line 117](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/docs/findings/runfit-certificate/data/V3_leastsq.jsonl:117) and [repeat, line 117](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/docs/findings/runfit-certificate/data/rep_V3_leastsq.jsonl:117) contain identical requests for **B4C-UCl4 / U4f Scan_1**, seed **2733638148**, both certified.

   Component 5’s GL ratio changes only **0.9999999461 → 0.9999999999999563**, and relative χ² change is **8.87e−9**. However, its stderr changes **0.544386 → 0.129395**, necessarily failing the **0.1%** stderr comparison. The committed TR repeats also contain violations. Objective convergence does not guarantee covariance reproducibility, particularly near bounds or poorly determined directions.

3. **MAJOR — Component areas and finite component-curve regressions can pass unchecked.** [tests/fit_equality.py:179](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:179), [line 240](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:240).

   Starting from the real `_two_peaks()` response, each independent mutation passes:

   - Double one component’s reported area.
   - Replace its area with **NaN**.
   - Replace its area stderr with **infinity**.
   - Add **1,000,000 counts** to one finite component-curve sample.

   Area comparison checks only whether stderr is `None`; determined component curves receive only mask checks. Consequently, regressions in displayed areas or component curves escape the rewritten tests. The flat-direction test changes curves without updating parameters or areas, so it does not validate two internally consistent fitted solutions.

Validation: **96 focused Python tests and 122 JavaScript tests passed**; the **59-test battery passed again in a separate process**. Additional certificate exit and cancellation probes passed. V3 ordering remains covered. Production fitting code matches the recorded final-code hash. The corrected note’s counts and displacement maxima agree with committed data. No files changed.

**VERDICT: NO-GO**
