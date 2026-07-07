# C1s multi-env fix (F1/F2/F3) RE-CHECK — run B

Date: 2026-07-07. Commit reviewed: 56527f9. Prompt:
docs/autofit/codex/c1s_multienv_fix_recheck_prompt.txt
Runner: codex exec --sandbox read-only, high effort, gtimeout 600s.

```
1. MAJOR, `autofit/engine.py:1849`: Disposition 2 is still open. Scenario: `_attempt_proposal` starts with `budget_remaining=15.1`, passes the new 15s guard, the augmented `fit_candidate()` takes ~12s, then `remaining` is ~3s. The code still calls `run_stability_analysis()` with that tiny deadline, and `run_stability_analysis` can start another unbounded `fit_candidate()` before the deadline check trips, finishing after `TOTAL_ANALYSIS_TIMEOUT_SEC`. Fix: reserve budget for stability too, or fast-reject before stability when `remaining < PROPOSAL_MIN_FIT_BUDGET_SEC`; add a pin for post-primary insufficient budget, not only the top guard.

VERDICT: NO-GO
```
