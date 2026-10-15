**Two MINOR findings remain. No BLOCKER or MAJOR found.**

1. **Round-5 findings**

   - **Cross-side width overflow: resolved.** The longest curve or energy array is now bounded against `a`’s span before comparison. [app.py:1544](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1544)
   - **Duplicate component IDs: resolved for that reproduction.** Duplicate IDs are rejected before expressions are collected. A related collision remains below. [app.py:1468](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1468)
   - **Scientific-notation links: resolved.** Parsed numeric literals no longer contribute an erroneous `e` identifier. [app.py:1490](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1490)
   - **Held bounds of ±1e308: stated limit.** Explicitly documented; I reconfirmed a successful real fit whose self-comparison returns 400. [plan:67](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/docs/superpowers/plans/2026-10-15-seal-1d-rerun.md:67)

2. **Remaining accepted-input paths**

   **MINOR — distinct IDs can still overwrite a parameter’s link.** Uniqueness of component IDs does not guarantee uniqueness of `p{id}_{name}`. Component `1`, parameter `gl_ratio`, and component `1_gl`, parameter `ratio`, both produce `p1_gl_ratio`. The latter overwrites the former in `exprs`. Arbitrary parameter names pass the form check. [app.py:1475](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1475), [app.py:1483](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1483), [fitting.py:192](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:192)

   Reproduced with the first expression `nothing_here * 2` and the second `p1_center`: **200 on either side; identical malformed responses return `same: true`**. Validate constructed-name uniqueness before inserting expressions.

   **MINOR — validation and comparison follow different link graphs.** Validation uses AST names, but `linked_bounds` still scans expression text with a regex, including names inside string literals. [app.py:1490](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1490), [same_fit.py:143](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:143)

   Reproduction: add 1,100 unbounded parameters whose expressions are `'p1_l1' and p1_center`, `'p1_l2' and p1_center`, etc., ending at `p1_center`. AST validation sees one-step links to the center; the comparator follows the quoted names recursively. Placement only in **`b` returns 200**, although self-comparison returns **400 for excessive recursion**. Thus the promised up-front depth check still misses a structure the comparator cannot follow. Both paths need consistent reference extraction.

   I reproduced no additional numerical-scale overflow or input-driven HTTP 500.

3. **Real-fit compatibility**

   Beyond the documented extreme-bound limit, I found no refusal of a page-supported fit. **22 additional successful real fits self-compared `same`**, covering all seven lineshapes, linked widths locked/unlocked, exponent-form offsets and ratios, and eight additional background configurations. The producer’s links use the single-master forms accepted by the new parser. [fitting.py:1730](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:1730)

4. **Regression tests**

   **Yes, the new tests fail when their corresponding fixes are removed in memory:**

   - Removing the cross-side guard fails its test. [test:244](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:244)
   - Removing duplicate-ID rejection fails its test. [test:219](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:219)
   - Restoring regex validation fails both exponent-form offset cases; the two ordinary-decimal controls still pass. [test:206](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:206)

   Focused suite: **77 passed, 1 skipped**. The 328-record test skipped because `SEAL_1B_RECORDS` was unset here. Tests and mutations used in-memory substitutions; no checkout files changed. The two remaining paths lack regression coverage.

VERDICT: NO-GO
