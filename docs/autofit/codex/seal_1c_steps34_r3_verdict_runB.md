**GO for steps 3–4, with one remaining MINOR test-coverage finding.** I found no BLOCKER or MAJOR correctness defect in this round. No files changed.

1. **Round-2 findings, both runs**

| Finding | Status |
|---|---|
| **MAJOR:** staged answers lost across `_makeSeal`’s deep copy | **Resolved.** Commit matches the seal’s R/O by content. [index.html:9125](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9125) |
| **MAJOR:** staged contents change while verification is outstanding | **Resolved.** Both objects are cloned and deeply frozen before sending; answers retain those snapshots. [index.html:9111](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9111) |
| **MINOR:** explicit retry blocked by an outstanding attempt | **Resolved.** Only background triggers take the deduplication branch. [index.html:9166](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9166) |
| **MINOR:** sparse arrays compare incorrectly/asymmetrically | **Resolved.** Every index is visited; holes compare as JSON nulls. [index.html:8863](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8863) |
| **MINOR:** deleted samples escape memo invalidation | **Resolved.** Missing indices invalidate the memo. [index.html:8936](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8936) |
| Staged success test bypasses pre-seal handoff | **Resolved.** Producer objects are checked before `_makeSeal`; the test requires a cached verdict and zero additional requests. [test_browser_seal_step4.py:505](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step4.py:505) |
| Lock/link/held-value tests fail prematurely at inventory | **Resolved.** Inventory is rebuilt and the expected failure is specifically `model`. [test_browser_seal_step4.py:284](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step4.py:284) |
| Wrong-spectrum E test also creates R/O disagreement | **Resolved.** E remains internally coherent; only an anchor-only raw sample changes. [test_browser_seal_step4.py:366](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step4.py:366) |
| Missing unreachable-plus-outstanding coverage | **Resolved.** The new test requires PENDING, then checks both mismatch and consistent partners. [test_browser_seal_step4.py:447](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step4.py:447) |
| Retry coverage exercises completed attempts only | **Resolved.** The new test holds the first attempt, starts another, and delivers a superseded mismatch. [test_browser_seal_step4.py:465](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step4.py:465) |
| **MINOR:** remaining JSON-stringified identity assertions, identified by run B | **Still open.** Step-3 Auto-Fit request/context/O assertions still stringify. These cannot establish strict identity for signed zero, undefined fields or non-finite values. [test_browser_seal_step3.py:105](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step3.py:105) |

The previously resolved signed-zero, producer-continuity, anchor-identity and verdict-precedence fixes remain intact.

2. **Staged lifecycle and content matching**

For the application’s JSON-shaped records, content matching is sound: it compares the entire R/O pair, preserves meaningful differences, and accepts the transport equivalences intentionally defined by the record rule. It no longer depends on object identity surviving `_makeSeal`. [index.html:8858](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8858)

An incomplete or nonmatching handoff returns `{committed:false}` **before deleting the transaction or writing either cache**. I exercised zero-answer, one-answer and complete two-answer commits. [index.html:9122](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9122)

A changed caller object can still receive a returned verdict **about its original snapshot**; that is intentional. The changed contents cannot inherit that answer at commit. Superseded owner/operation/transaction checks return null and append no answer. [index.html:9105](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9105)

`committed:true` means the answer handoff completed, not that Auto-Fit was accepted: the returned verdict can be mismatch or unreachable. Producer acceptance/rollback integration remains step 7’s responsibility, consistent with this review’s scope. [index.html:9128](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9128), [plan:358](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/docs/superpowers/plans/2026-10-14-seal-1c-page.md:358)

3. **“Check again” and ownership**

Explicit retry installs a new attempt synchronously. Attachment compares attempt IDs **before clearing the entry**, so an older reply cannot attach or remove the newer attempt. I exercised both reply orders. Existing owner, seal and producer-operation guards remain. [index.html:9137](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9137)

Background calls still suppress duplicate attempts and repeats after an answer; they do not claim a fit operation. [index.html:9163](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9163)

4. **Switch-off regression**

None found. The authority switch remains false, and this diff changes verification helpers rather than shipped producer calculations. [index.html:8851](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8851)

The local-engine replay against `70e1097`, with artifact writes suppressed, produced **121 bit-identical results, zero differences, zero skips**.

5. **Do the revised tests isolate their defects?**

Yes, for the round-3 cases inspected:

- The staged tests exercise deep-copy handoff and mutation during an outstanding check.
- Retry checks both request count and rejection of the old mismatch.
- Unreachable-plus-outstanding checks the intermediate state and final precedence.
- Wrong-spectrum E preserves R/O coherence.
- Lock/link/held-value cases specifically require `model`. In extracted-function execution using the test’s spectrum/model setup, all three reached that check. Removing projection validation in memory changed their failures to `statistics` or `components`, making their assertions fail.

The remaining MINOR identity-assertion gap above is unchanged.

Validation: **37 existing JS tests passed**, seven controlled verification/memo probe groups passed, and the three projection mutation checks passed. The browser suite could not start because the read-only sandbox denied Chromium’s temporary-directory creation; browser execution remains unverified in this run.

VERDICT: GO
