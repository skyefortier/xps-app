**All actionable round-5 findings from both runs are resolved. I found no remaining BLOCKER or MAJOR, and no new regression in `seal-1c-page..HEAD`.**

1. Findings, combining both round-5 verdicts:

| Rank | Finding | Status and evidence |
|---|---|---|
| MAJOR | Overlapping checks permit unlimited automatic numerics changes | **Remains resolved.** Allowance returns only after a counting reply with no check outstanding. [index.html:9121](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9121) |
| MAJOR | Earlier staged answers acquire the current epoch at commit | **Remains resolved.** Every constituent must retain current send-epoch and answer-numerics provenance. [index.html:9129](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9129), [index.html:9212](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9212) |
| MAJOR | Split permits cached confirmation or staged commit | **Remains resolved.** Both paths refuse during a split. [index.html:9145](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9145), [index.html:9209](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9209), [index.html:9292](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9292) |
| MAJOR | Background triggers continue checking during a split | **Remains resolved.** `_ensureVerified` stops them. [index.html:9261](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9261) |
| MINOR | Background-effect form, including manual anchor cardinality | **Resolved.** Exact fields/dimensions remain checked; `manual` now requires at least two anchors, matching the producer. [fitting.py:3353](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:3353), [fitting.py:2192](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:2192) |
| MINOR | A → B → A test misses the vulnerable interval | **Resolved.** It asserts after A returns while Y still retains its epoch-0 answer. [test_browser_seal_step4.py:761](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:761) |
| MINOR | Concurrent-worker test leaves completion order uncontrolled | **Resolved.** B completes while A remains held; allowance is checked before releasing A. [test_browser_seal_step4.py:812](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:812) |

The inherited digest limitations remain **stated limitations**, including excluded verifier arithmetic, function-only app closure, reviewed equivalence entries, and history protection conditional on `main` having a manifest. [numerics_digest.py:42](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/scripts/numerics_digest.py:42), [test_numerics_version.py:49](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_numerics_version.py:49)

2. **Both revised scenarios pass with their guards and fail without them in controlled replays of the actual page functions.**

- Removing the cache epoch guard changes Y from `pending` to `current` at epoch 2 using its epoch-0 answer, violating the assertion at [test_browser_seal_step4.py:762](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:762).
- Removing the in-flight condition changes allowance from `0` to `1` with one check outstanding, violating [test_browser_seal_step4.py:814](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:814).

**Full Playwright execution as written was not independently established in this read-only run.** The mutation evidence above uses controlled transport and ownership adapters.

3. **No remaining BLOCKER / MAJOR or reproduced regression.** A combined three-seal replay rejected an old staged anchor, ignored an old transport failure, stopped background checks during mixed-worker split, and recovered through retry. An ordinary deployment passed all 120 tested completion orders without a spurious split.

Validation: **113 targeted JavaScript tests passed; 113 verifier/lineshape/background cases passed using in-memory fits and the real verification endpoint; 14 digest tests passed, one skipped.** Both new anchor cases failed when their cardinality guard was removed. The fitting-math digest is unchanged from `seal-1c-page`. Checkout unchanged.

VERDICT: GO
tokens used
101,988
**All actionable round-5 findings from both runs are resolved. I found no remaining BLOCKER or MAJOR, and no new regression in `seal-1c-page..HEAD`.**

1. Findings, combining both round-5 verdicts:

| Rank | Finding | Status and evidence |
|---|---|---|
| MAJOR | Overlapping checks permit unlimited automatic numerics changes | **Remains resolved.** Allowance returns only after a counting reply with no check outstanding. [index.html:9121](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9121) |
| MAJOR | Earlier staged answers acquire the current epoch at commit | **Remains resolved.** Every constituent must retain current send-epoch and answer-numerics provenance. [index.html:9129](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9129), [index.html:9212](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9212) |
| MAJOR | Split permits cached confirmation or staged commit | **Remains resolved.** Both paths refuse during a split. [index.html:9145](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9145), [index.html:9209](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9209), [index.html:9292](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9292) |
| MAJOR | Background triggers continue checking during a split | **Remains resolved.** `_ensureVerified` stops them. [index.html:9261](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9261) |
| MINOR | Background-effect form, including manual anchor cardinality | **Resolved.** Exact fields/dimensions remain checked; `manual` now requires at least two anchors, matching the producer. [fitting.py:3353](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:3353), [fitting.py:2192](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:2192) |
| MINOR | A → B → A test misses the vulnerable interval | **Resolved.** It asserts after A returns while Y still retains its epoch-0 answer. [test_browser_seal_step4.py:761](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:761) |
| MINOR | Concurrent-worker test leaves completion order uncontrolled | **Resolved.** B completes while A remains held; allowance is checked before releasing A. [test_browser_seal_step4.py:812](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:812) |

The inherited digest limitations remain **stated limitations**, including excluded verifier arithmetic, function-only app closure, reviewed equivalence entries, and history protection conditional on `main` having a manifest. [numerics_digest.py:42](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/scripts/numerics_digest.py:42), [test_numerics_version.py:49](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_numerics_version.py:49)

2. **Both revised scenarios pass with their guards and fail without them in controlled replays of the actual page functions.**

- Removing the cache epoch guard changes Y from `pending` to `current` at epoch 2 using its epoch-0 answer, violating the assertion at [test_browser_seal_step4.py:762](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:762).
- Removing the in-flight condition changes allowance from `0` to `1` with one check outstanding, violating [test_browser_seal_step4.py:814](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:814).

**Full Playwright execution as written was not independently established in this read-only run.** The mutation evidence above uses controlled transport and ownership adapters.

3. **No remaining BLOCKER / MAJOR or reproduced regression.** A combined three-seal replay rejected an old staged anchor, ignored an old transport failure, stopped background checks during mixed-worker split, and recovered through retry. An ordinary deployment passed all 120 tested completion orders without a spurious split.

Validation: **113 targeted JavaScript tests passed; 113 verifier/lineshape/background cases passed using in-memory fits and the real verification endpoint; 14 digest tests passed, one skipped.** Both new anchor cases failed when their cardinality guard was removed. The fitting-math digest is unchanged from `seal-1c-page`. Checkout unchanged.

VERDICT: GO
