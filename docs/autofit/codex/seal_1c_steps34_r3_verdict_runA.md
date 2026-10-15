No BLOCKER or MAJOR findings remain in this round’s fix. One previously reported MINOR test gap remains. No files changed.

**1. Round-2 findings, both runs**

| Finding | Status |
|---|---|
| Staged answers lost across `_makeSeal`’s deep copy; apparent success without cached answers | **Resolved.** Commit matches by content and refuses incomplete coverage before deleting the transaction or writing caches. [index.html:9122](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9122) |
| Staged contents mutable during verification | **Resolved.** Each check sends and retains its own deep-frozen snapshots. [index.html:9110](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9110) |
| Outstanding attempt blocks “check again” | **Resolved.** Explicit retry bypasses background deduplication. [index.html:9163](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9163) |
| Sparse-array equality skips holes | **Resolved.** Every index is compared, with holes treated as null. [index.html:8863](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8863) |
| Sample memo misses deleted elements | **Resolved.** A missing index invalidates the memo. [index.html:8936](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8936) |
| Staged success test bypasses pre-seal handoff | **Resolved.** Checks now precede construction of the destination seal. [test_browser_seal_step4.py:505](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step4.py:505) |
| Lock/link/held-value tests stop at inventory | **Resolved.** Inventory is rebuilt; assertions require `model`. [test_browser_seal_step4.py:284](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step4.py:284) |
| Wrong-spectrum E caught by R/O disagreement | **Resolved.** E remains internally coherent; only an anchor-exclusive raw sample changes. [test_browser_seal_step4.py:366](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step4.py:366) |
| Missing unreachable-plus-outstanding case | **Resolved.** Both subsequent mismatch and consistent outcomes are covered. [test_browser_seal_step4.py:447](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step4.py:447) |
| Missing retry during an outstanding attempt | **Resolved.** The test checks request counts and rejection of the superseded mismatch. [test_browser_seal_step4.py:465](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step4.py:465) |
| Run B’s remaining JSON-stringified identity assertions | **Unresolved — MINOR.** Auto-Fit request reconstruction, derived context and O₂ still use `JSON.stringify`, which can conceal signed-zero and undefined-field differences. Use the strict comparator for these internal identity assertions. [test_browser_seal_step3.py:105](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/tests/test_browser_seal_step3.py:105) |

Previously resolved producer continuity, anchor identity, verification precedence and ownership checks remain intact. [index.html:8958](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8958), [index.html:9074](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9074), [index.html:9141](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9141)

**2. Staged lifecycle**

For the intended JSON-shaped records, content matching is sound: it allows the seal’s independent deep copy while requiring equality of the complete R/O snapshots. Signed zero, absent undefined fields and array holes follow the stated record rule. [index.html:8853](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8853)

A changed caller object can still receive a returned verdict **about its original snapshot**, but that verdict cannot transfer to a seal containing the changed content. Superseded transactions return null and record no answer. An incomplete commit returns `{committed:false}`, preserves the transaction and writes neither cache. [index.html:9111](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9111), [index.html:9123](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9123)

`committed:true` reports completion of the answer handoff; its accompanying verdict can still be mismatch/unconfirmed/unreachable. The eventual Auto-Fit caller must enforce §6.3’s consistent-only installation rule when producer integration occurs. [index.html:9128](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9128), [plan:154](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/docs/superpowers/plans/2026-10-14-seal-1c-page.md:154)

**3. Retry and ownership**

A superseded reply cannot attach or delete the newer attempt: attempt identity is checked before deletion. Background triggers still deduplicate an outstanding check and suppress repeats of answered checks. I verified both reply orders. [index.html:9142](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9142), [index.html:9166](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:9166)

**4. Switch-off regression**

None found. This diff changes verification helpers without activating them in shipped producer flows; the authoritative switch remains false. [index.html:8847](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s34/templates/index.html:8847)

**5. Test strength and validation**

The revised scenarios now target the named defects: staged mutation checks cache transfer directly, projection cases require `model`, and wrong-spectrum evidence preserves R/O coherence. The remaining strict-identity gap is nonblocking for this fix.

Validation: **129 focused JavaScript tests passed**, plus **41 direct assertions against extracted page functions**. Browser execution was blocked at Chromium startup by the read-only sandbox’s temporary-directory restriction; the browser tests were inspected, not successfully rerun.

VERDICT: GO
