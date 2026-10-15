**Three MINOR findings remain. No BLOCKER or MAJOR found.**

1. **Round-4 findings**

   - **Original width-overflow reproductions resolved:** `n × span` now rejects those grids before comparison. The broader guarantee remains incomplete for differing sample counts, described below. [app.py:1465](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1465)
   - **Breadth-first shortcut defect resolved:** multi-reference expressions are rejected, and the validator follows individual chains with cycle detection and a depth limit. Expression overwriting leaves a separate validation gap below. [app.py:1483](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1483)
   - **Server-produced responses with overflowing locked bounds remain a stated compatibility limit.** I reconfirmed `/api/fit` returning 200, `success: true`, with locked FWHM bounds `[-1e308, 1e308]`; self-comparison returns 400. [fitting.py:1781](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:1781), [app.py:1477](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1477)
   - **Missing regression coverage was added**, but does not cover the cases below. [tests/test_seal_1d_compare.py:165](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:165)

2. **Remaining accepted inputs**

   **MINOR — different sample counts can still produce an infinite position scale.** Each side passes its own `n × span` check, but the comparator measures **both components using `a`’s grid**. Consequently, `b`’s half-height sample count is not bounded by `len(a.energy)`. [same_fit.py:118](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:118), [same_fit.py:131](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:131)

   Reproduced with `a.energy = [0, 2.5e307, 5e307]`, zero component curves in `a`, and ten samples with unit component curves in `b`. Both checks pass; the selected width is `10 × 2.5e307 = inf`. The endpoint returns **200, `same: false`** because array lengths differ. Thus it still compares using an infinite scale, although this reproduction does not falsely declare equality.

   **MINOR — duplicate component IDs hide invalid links.** Expressions are stored by constructed parameter name, so a later component can overwrite an earlier expression before validation. [app.py:1472](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1472), [app.py:1480](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1480)

   Reproduced with an unbounded FWHM expression `nothing_here * 2`, followed by a component with the same ID whose FWHM expression is `p1_center`. The missing reference escapes validation. Placement in **either side returns 200**; identical malformed responses return **200, `same: true`**. The comparator silently skips the missing reference. [same_fit.py:145](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:145)

   I reproduced **no additional input-driven 500**.

3. **Can a real fit response be refused? Yes—beyond the stated arithmetic limit.**

   **MINOR — scientific notation in a legitimate link is rejected.** The regex treats the `e` in `1e-05` as another identifier. [app.py:1485](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1485)

   The page accepts a linked offset of `0.00001`; the producer writes `p1_center + 1e-05`. I reproduced **200, `success: true`** from `/api/fit`, followed by **400** on self-comparison: “not one a fit writes.” This is a finite, single-parameter expression the producer actually writes. [templates/index.html:6818](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/templates/index.html:6818), [fitting.py:1730](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:1730)

4. **Do the new tests detect their named defects? Yes, for their concrete cases.**

   All **21 refusal cases passed**. Each failed when its corresponding guard condition was removed in memory; bypassing the entire guard also failed all 21. They miss differing sample counts, overwritten expressions, and valid scientific-notation links. [tests/test_seal_1d_compare.py:175](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:175)

Validation: **71 passed, 1 skipped**, using in-memory session substitution for read-only execution. The 328-record test skipped because `SEAL_1B_RECORDS` was unavailable, so I could not independently confirm that claim. No files changed.

VERDICT: NO-GO
