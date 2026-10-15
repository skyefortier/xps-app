**Two MINOR findings remain. No BLOCKER or MAJOR found.**

1. **Round-5 findings**

| Finding | Status |
|---|---|
| Cross-side width overflow | **Resolved:** the longest curve or energy array is bounded against `a`’s span before comparison. [app.py:1544](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1544) |
| Duplicate component IDs overwrite links | **Original case resolved:** duplicate IDs are refused. A related parameter-key collision remains below. [app.py:1468](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1468) |
| Legitimate exponent-form offsets refused | **Resolved:** AST names exclude numeric literals; the real-fit regression cases pass. [app.py:1489](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1489) |
| Held bounds of ±1e308 refused | **Explicitly stated limit.** [plan:69](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/docs/superpowers/plans/2026-10-15-seal-1d-rerun.md:69) |

2. **Remaining accepted-input paths**

**MINOR — distinct IDs can still overwrite a link before validation.** The generated key `p{id}_{name}` is ambiguous: component `1`, parameter `x_fwhm`, and component `"1_x"`, parameter `fwhm`, both become `p1_x_fwhm`. The ID check passes, and the later expression overwrites the earlier one. The response schema permits these IDs and parameter names. [app.py:1475](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1475), [app.py:1483](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1483), [fitting.py:193](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:193)

Reproduced with the earlier expression `nothing_here * 2` and the later expression `p1_center`: **200 on either side; 200, `same: true` on both**. Reject duplicate synthesized parameter names before building the expression map.

**MINOR — validation and comparison follow different link graphs.** Validation uses AST names, but `linked_bounds` still extracts identifiers using regex, including identifiers inside string literals. For example, `("p1_l1" and p1_center)` names only `p1_center` to validation, while the comparator follows `p1_l1` first. [app.py:1490](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1490), [same_fit.py:143](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:143)

Reproduced a **300-link chain returning 200, `same: true`**, despite exceeding the validator’s 250-step limit. A **1,100-link chain placed only in `b` returns 200**; self-comparison reaches the recursion catch and returns 400. The validator must bound the graph the comparator actually follows, or restrict expressions to the producer’s grammar.

I reproduced **no additional non-finite-scale acceptance or HTTP 500**.

3. **Real-fit compatibility**

No additional page-produced refusal found beyond the documented arithmetic limit. The producer writes a master parameter with an optional numeric offset or multiplier, which the AST check handles across the supported linked shapes. [fitting.py:1727](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:1727)

I independently confirmed **all 328 real records self-compare as `same`**. [tests/test_seal_1d_compare.py:188](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:188)

4. **Regression tests**

**Yes, the new tests detect their named regressions.** In-memory mutations confirmed:

- Restoring the regex fails both exponent-form offset cases.
- Removing duplicate-ID rejection fails its test.
- Removing the cross-side bound fails its test.

The `1e5` and `10.9` cases remain passing controls under the old regex. These tests omit the two remaining paths above. [tests/test_seal_1d_compare.py:206](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:206)

Validation: **41 endpoint tests passed, zero skipped**, using in-memory upload/session substitution for read-only execution. No files changed.

VERDICT: NO-GO
