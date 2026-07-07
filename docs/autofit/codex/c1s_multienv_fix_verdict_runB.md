# C1s multi-env fix (F1/F2/F3) review — run B

Date: 2026-07-07. Commit reviewed: ad4acc3. Prompt:
docs/autofit/codex/c1s_multienv_fix_review_prompt.txt
Runner: codex exec --sandbox read-only, high effort, gtimeout 600s.

```
1. BLOCKER [autofit/engine.py](/Users/skyefortier/xps-app/autofit/engine.py:2230): F2 proposal roles can collide across rounds. Scenario: round 1 flags `[A, B]`; `A` is rejected, `B` is accepted as `proposed_peak_1`. Round 2 sees one existing proposed slot, sets `n_prior = 1`, and renames the next spec to `proposed_peak_1` again. `_augmented_candidate` then builds duplicate slot roles/prefixes, so lmfit params collide and the real second proposal is rejected/lost. Fix: allocate from `max(existing proposed_peak_<n> suffix) + 1`, or maintain a monotonic per-candidate proposal counter including rejected attempts.

2. MAJOR [autofit/engine.py](/Users/skyefortier/xps-app/autofit/engine.py:1772): F2 can exceed the sweep budget despite the new `pass_budget`. Scenario: a candidate starts just under the deep precheck limit, stability consumes most of the remaining sweep time, proposal pass starts with ~1s left, then `_attempt_proposal` runs an unbounded augmented `fit_candidate()` before any effective deadline check. That fit can burn seconds past `TOTAL_ANALYSIS_TIMEOUT_SEC`, and the stability deadline is then computed from the post-fit time using the stale positive `budget_remaining`. Fix: check remaining budget immediately before the augmented fit, skip when it cannot fit a worst-case attempt, and/or pass a reduced `max_nfev`/deadline-aware fit path before stability.

VERDICT: NO-GO
```
