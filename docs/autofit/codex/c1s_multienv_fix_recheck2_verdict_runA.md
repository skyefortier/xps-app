# C1s multi-env fix (F1/F2/F3) RE-CHECK ROUND 2 — run A

Date: 2026-07-07. Commit reviewed: d7585eb. VERDICT: GO.
Prompt: docs/autofit/codex/c1s_multienv_fix_recheck2_prompt.txt

```
1. No open finding, [autofit/engine.py](/Users/skyefortier/xps-app/autofit/engine.py:1854): residual scenario `budget_remaining=15.1`, augmented fit consumes ~12 s, post-fit remaining ~3 s. Fix confirmed: guard uses dynamic `remaining = budget_remaining - elapsed` and rejects when `< PROPOSAL_MIN_FIT_BUDGET_SEC`, returning a visible `ProposedPeakReport`.

2. No open finding, [autofit/engine.py](/Users/skyefortier/xps-app/autofit/engine.py:2291): proposal attempts now receive current `pass_budget - elapsed`; top guard blocks augmented fits with `<15 s`, post-fit guard blocks stability with `<15 s`. Remaining worst case is bounded to roughly `TOTAL_ANALYSIS_TIMEOUT_SEC` plus one nfev-capped fit. The pre-existing classic candidate stability path can still start a refit late in a candidate’s 25 s budget, but that is not the F2 residual and does not add an extra proposal overrun.

3. No open finding, [tests/autofit/test_preseed_dominants.py](/Users/skyefortier/xps-app/tests/autofit/test_preseed_dominants.py:234): the fake-clock pin discriminates the fix. With old `remaining <= 0`, post-fit remaining 7 s would call monkeypatched `run_stability_analysis` and fail; with HEAD it fast-rejects. Top-guard and role-suffix pins are present at lines 208 and 174.

4. No open finding, [autofit/engine.py](/Users/skyefortier/xps-app/autofit/engine.py:1696): F2 role uniqueness remains max-suffix+1, accepted/rejected proposal reports remain accounted and serialized, F1 covered-spectrum no-op and F3 screen/classic behavior remain pinned, and the documented 287.7 limitation remains intentionally flagged rather than relitigated. I could not rerun pytest here because the read-only sandbox has no writable temp directory; HEAD records 516 passed / 3 skipped.

VERDICT: GO
```
