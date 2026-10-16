**Three MINOR findings remain. No BLOCKER or MAJOR found.**

1. **The concrete round-11 findings are resolved.** Large integer IDs pass; incomplete links, `-0.0`, and bogus support relationships are refused. The oracle now determines optionality by path. I also confirmed that it catches an in-memory mutant allowing a missing top-level `message`. [fitting.py:225](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:225), [fitting.py:271](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:271), [tests/test_seal_1d_compare.py:423](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:423)

2. **No: validation still rejects a server-written response and accepts structures the producer cannot write.**

   - **MINOR — a successful fit with an equivalent numeric master reference is refused.** With component IDs `1` and `2`, and the second component’s `constrain_to: 1.0`, `/api/fit` returns **200, `success: true`**. Its centre expression is `p1_center + 0.5`, but `individual_peaks[1].support.follows` is absent. Parameter construction matches IDs using equality; support traversal instead uses their string spellings (`"1.0"` versus `"1"`). The new validator therefore rejects the unmodified response: self-comparison returns **400**. [fitting.py:1870](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:1870), [fitting.py:3197](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:3197), [fitting.py:312](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:312)

   - **MINOR — an impossible link to a null ID is accepted.** Starting from a real response with IDs `null` and `"c"`, I added complete links to `pNone_center`, `pNone_amplitude`, and the matching shape parameters, with `support.follows: null` and null linked bounds. Validation accepts it. The producer cannot write this arrangement: `constrain_to: null` selects the **unlinked** branch. The validator does not exclude a null-ID master. [fitting.py:284](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:284), [fitting.py:1867](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:1867)

   - **MINOR — fabricated bounds on linked parameters are accepted.** In a real linked response, changing `individual_peaks[1].params.center.min/max` from null to `280.0/300.0` passes validation. The producer’s expression branch leaves bounds open, and response extraction writes them as null. The validator checks `vary` and expression arrangements without enforcing this metadata relationship. [fitting.py:1855](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:1855), [fitting.py:3158](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:3158), [fitting.py:281](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:281)

   Both fabricated structures return **200 on a, b, and both**, with self-comparison reporting **`same: true`**.

3. **I did not reproduce a body-triggered 500.** The 3,000-mutation fuzz passed; additional malformed JSON, deeply nested JSON, and oversized-integer bodies returned 400. This is bounded evidence, not proof for every body. Unexpected comparison exceptions still explicitly return 500. [app.py:1486](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1486)

4. **The tests establish their sampled regressions, but not producer-exact acceptance.** In particular, `_linked_as_written` retains the original finite bounds when adding expressions. Consequently, the positive controls and oracle base themselves contain the third finding above. Use producer-written linked metadata for those controls. [tests/test_seal_1d_compare.py:158](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:158), [tests/test_seal_1d_compare.py:283](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:283), [tests/test_seal_1d_compare.py:442](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:442)

Read-only verification with in-memory upload sessions: **258 passed, 1 skipped** across comparison, comparator, and numerics tests, including all **328 records**. The corpus hash matches its manifest. I did not repeat the full thirteen-mutant campaign.

No files changed.

VERDICT: NO-GO
