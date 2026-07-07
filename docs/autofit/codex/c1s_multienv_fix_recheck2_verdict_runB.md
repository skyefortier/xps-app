# C1s multi-env fix (F1/F2/F3) RE-CHECK ROUND 2 — run B

Date: 2026-07-07. Commit reviewed: d7585eb. VERDICT: GO.
Prompt: docs/autofit/codex/c1s_multienv_fix_recheck2_prompt.txt

```
1. No open finding, `autofit/engine.py:1844`: the run-B residual scenario is closed. The guard uses dynamic post-fit `remaining = budget_remaining - (time.perf_counter() - attempt_start)` and rejects at `< PROPOSAL_MIN_FIT_BUDGET_SEC`; the rejection is a visible `ProposedPeakReport` appended/counted by `compare_models`. Fix: none.

2. No open finding, `autofit/engine.py:2291`: proposal attempts receive live remaining pass/sweep budget via `budget_remaining=pass_budget - elapsed`; no proposal augmented primary fit starts with `<15s`. Stability can still overrun its deadline by one max-nfev refit if a later refit begins just before deadline, but that bounds wall to roughly `TOTAL + one worst-case fit`, not the old unbounded residual case. Fix: none.

3. No open finding, `tests/autofit/test_preseed_dominants.py:234`: the fake-clock pin discriminates the fix. With old `remaining <= 0`, `remaining=7` would call the monkeypatched `run_stability_analysis` and fail; HEAD fast-rejects before stability. Fix: none.

4. No open finding, `autofit/engine.py:1696`: F2 role collision remains closed. `_next_proposal_index` is max-suffix-plus-one, no count suffix call site remains, and accepted/rejected proposal reports are carried/appended once. Fix: none.

5. No open finding, `autofit/engine.py:1439`, `autofit/engine.py:2154`: F1 covered-spectrum no-op/honesty and F3 screen/classic behavior remain additive; 287.7 honest-limitation behavior is documented unchanged. I could not run pytest locally because `pytest` is unavailable in this environment. Fix: none.

VERDICT: GO
```
