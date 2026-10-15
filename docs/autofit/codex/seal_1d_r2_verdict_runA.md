**Two MINOR correctness gaps remain in malformed-input handling. No remaining BLOCKER or MAJOR found.** The page isolation fixes hold, but `/api/compare-fits` still has reproducible HTTP 500 paths.

**1. Round-1 findings**

| Finding | Status |
|---|---|
| **MAJOR:** re-run changes page numerics, invalidates verdicts and restarts checks | **Resolved.** Replay passes `noteSoftware: false`, and the shared completion path honors it. [index.html:9721](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/templates/index.html:9721), [index.html:8658](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/templates/index.html:8658) |
| **MAJOR:** numerics describe the comparison worker | **Resolved.** Every `NUMERICS_IDENTITY_KEYS` field is compared between `a.software` and `b.software`. [app.py:1493](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1493) |
| **MINOR:** `10**400` produces 500 | **Specific defect resolved:** both sides now return 400. Broader arithmetic safety remains incomplete; see answer 4. [app.py:1474](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1474) |
| **MINOR:** late comparison retained after replacement | **Resolved.** Ownership is checked after the final await and before storing either success or failure. [index.html:9740](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/templates/index.html:9740) |
| Edit/tab-switch behavior contradicts discard requirement | **Explicitly amended limit.** These operations retain the record’s outcome; display requires that seal to be shown as recorded. [plan:41](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/docs/superpowers/plans/2026-10-15-seal-1d-rerun.md:41) |
| Tests miss the reported triggers | **Resolved for those triggers**, with execution limits described in answer 5. |

**2. Can replay change state outside its outcome?**

I found no remaining path changing the model, seal state, cached verdict, page numerics, save or export. Replay clones the recorded request, never installs its result, and stores its outcome in a separate WeakMap. The changed-software harness preserved the epoch, numerics and cached verdict and triggered no verification. Restoring the old software-note behavior broke those invariants. [index.html:9705](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/templates/index.html:9705), [index.html:9719](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/templates/index.html:9719)

**3. Can an outcome belong to the wrong fit?**

No path found. Storage uses the captured seal’s identity; the final ownership check discards outcomes after replacement or tab closure. Rendering reads that same seal’s entry and requires a current, pending or unconfirmed recorded display. An edited fit therefore hides the outcome; returning to its recorded state may show it again, as specified. [index.html:9740](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/templates/index.html:9740), [index.html:9752](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/templates/index.html:9752), [index.html:9621](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/templates/index.html:9621)

**4. Is every malformed/hostile input refused with 4xx? No.**

- **MINOR — representable operands can still overflow.** In a real response, set an amplitude’s integer bounds to `min = -(2**1023)`, `max = 2**1023`, then compare that response with itself. Both bounds are exactly float-representable and pass validation. Their integer difference overflows when multiplied by the floating tolerance, producing **HTTP 500**. `_floats_only` checks individual values, not this arithmetic. [app.py:1454](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1454), [same_fit.py:199](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:199)

- **MINOR — parameter-link recursion bypasses the nesting protection.** A shallow response containing approximately 1,100 sequentially linked parameter entries passes form and float validation. `linked_bounds` recursively follows those links and raises `RecursionError`; the endpoint returns **HTTP 500**. Catching recursion during JSON parsing and `_floats_only` does not cover this path. [fitting.py:193](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:193), [same_fit.py:141](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:141), [app.py:1488](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1488)

Both need controlled refusal without changing the inherited comparison rules.

**5. Do the new tests catch their named defects?**

Yes, for the specific regressions. The server tests exercise oversized numbers on both sides and the re-run’s own identity; in-memory mutations restoring the defects failed their assertions. [test_seal_1d_compare.py:113](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:113)

The browser tests now alter the actual polling result’s software and hold the comparison until after replacement—the correct triggers. Extracted actual-page functions independently confirmed both fixes and failed when each fix was removed. [test_browser_seal_1d.py:146](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_browser_seal_1d.py:146), [test_browser_seal_1d.py:172](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_browser_seal_1d.py:172)

Validation: **50 Python tests passed** using in-memory upload/session substitution; **19 JavaScript transport tests passed**. Full browser tests were not run under the read-only constraints. Neither remaining 500 case is covered. No files changed.

VERDICT: NO-GO.
