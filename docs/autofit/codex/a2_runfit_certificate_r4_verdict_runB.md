# A2 round 4 — run B (commit 711da78; codex exec, reasoning high)

1. **MAJOR — Linked parameters falsely reject recorded same-fit repeats.** [tests/fit_equality.py:127](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:127), [line 144](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:144).

   Concrete case: **4-GTA UCl4-BN / U4f Scan_4**, seed **3861813319**, in [V3 TR, line 63](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/docs/findings/runfit-certificate/data/V3_least_squares.jsonl:63) and [repeat, line 63](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/docs/findings/runfit-certificate/data/rep_V3_least_squares.jsonl:63).

   Both certify. χ² differs by **8.07e−11 relatively**; every regenerated component curve differs by **less than 5.8e−6 of its height**. However, LA’s `m` changes **0.4769747758 → 0.0010740077**.

   The master passes against its **0–499 bound span**: allowance **0.499**. Its linked component, `m = p2_m`, has no emitted bounds and receives an allowance of only **0.000476975**. **The identical underlying parameter passes once and fails once.**

   Replaying recorded parameters with production-generated bounds and regenerated curves reproduces this rejection on **four TR targets**, at JSONL lines **59, 63, 151 and 157**. Linked parameters should inherit the appropriate scale from their dependency; add these repeat cases as regression coverage.

**Proportionality ruling:** The stated finite resolution satisfies the owner’s operational requirement of “equal within rounding.” Sub-resolution distinct minima alone are not a finding. I did **not** reproduce distinct returned minima exceeding that resolution that the helper accepts.

**Flakiness ruling:** No failure appeared in the completed checks on the tests’ models, or in the recorded LM parameter/curve comparisons. The four committed TR repeat rejections above remain a concrete defect. Recorded data are partial responses, so those replays do not establish acceptance of every response field.

Validation: **102 Python tests and 122 JavaScript tests passed**, including all **59 battery tests**. Certificate exit, evaluation-cap and restart-cancellation probes passed. Production code matches the recorded final hash; displacement measurements remain **0/202** for both methods. Longer sweeps were stopped to bound review time; filesystem-writing tests were excluded. No files changed.

**VERDICT: NO-GO**
