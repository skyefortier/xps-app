# C1s multi-env fix (F1/F2/F3) review — run A

Date: 2026-07-07. Commit reviewed: ad4acc3. Prompt:
docs/autofit/codex/c1s_multienv_fix_review_prompt.txt
Runner: codex exec --sandbox read-only, high effort, gtimeout 600s.

```
1. **BLOCKER** [autofit/engine.py:2230](/Users/skyefortier/xps-app/autofit/engine.py:2230): Proposal role renumbering can collide after “reject first, accept later” in a round.  
   Concrete failing scenario: one-main grammar, `enable_preseed=False`, residual proposals sorted as `spike, real_peak_A, real_peak_B`; the spike is attempted first and rejected on boundary cleanliness, `real_peak_A` is accepted as `proposed_peak_1`, then round 2 computes `n_prior == 1` and renames the next proposal to `proposed_peak_1` again. `_augmented_candidate` then appends a duplicate slot/prefix, so lmfit params collide or the fit is rejected/corrupted, and `real_peak_B` is lost despite being acceptable.  
   Fix: derive the next suffix from `max(existing proposed_peak_(\\d+) suffix) + 1`, not the count, and add a duplicate-role guard after augmentation.

VERDICT: NO-GO
```
