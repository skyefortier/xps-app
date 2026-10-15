No new **BLOCKER or MAJOR** found. The three concrete round-4 defects are resolved; remaining **MINOR** coverage limits are stated below.

**1. Round-4 findings**

| Finding | Status |
|---|---|
| Status bar reads legacy `roiRange` | **Resolved.** Activation calls `_fitRoiRange`, which derives endpoints from the readable record, including STALE. [index.html:3329](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:3329), [index.html:14695](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14695) |
| Stale `.fit.json` exports legacy `chiReduced` | **Resolved.** A readable stale seal exports `null` before evaluating the statistic fallback. [index.html:13132](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13132) |
| `_restampSupport` harness omits `_isInstalledSeal` | **Resolved.** The harness includes the real helper; its regression test passes. [stale_statistics.test.js:117](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/js/stale_statistics.test.js:117) |
| Sigma-dependent uncertainty-rule coverage | **MINOR, stated limit.** Displayed sigma is distinguished, but the rule test changes bounds only. [test:257](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:257), [test:628](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:628) |
| PNG coverage | **MINOR, stated limit.** Visible annotations are checked; drawing coordinates are not. Recorded and legacy χ² still agree in that test. [test:654](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:654) |
| Disagreeing-duplicate coverage | **Partially resolved; MINOR limit remains.** Stale `.fit.json` now has a discriminating assertion. The broader test still does not assert the poisoned R value or distinguish every export reader. [test:638](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:638), [test:683](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:683) |
| Literal switch-OFF equivalence | **Stated qualification remains**, described below. |

**2. Switch ON**

No further incorrect displayed/exported fit value, or write/throw on frozen `{seal}`, was found in the reviewed step-5 paths. The activation and cache/support mutator guards remain intact. [index.html:3325](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:3325), [index.html:5038](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:5038), [index.html:8047](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:8047)

This is not a claim that every legacy-field access is gone: STALE deliberately retains today’s preview paths, including cached grid/background reads where present; general persistence/loaders remain step 6. That matches the migration boundary. [plan:203](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/docs/superpowers/plans/2026-10-14-seal-1c-page.md:203), [index.html:11853](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11853)

The rebased detached verifier uses the counting-answer cache gate, epoch-scoped unreachable marks and split suppression. Focused in-memory checks passed for these cases, including an epoch change and a split during an outstanding request. [index.html:9303](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9303)

**3. Switch OFF**

Today’s supported mutable-result behavior is preserved by the new fixes. `_fitRoiRange` returns the legacy range without consulting page state; the stale-save suppression requires a sealed designation. [index.html:14697](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14697), [index.html:13132](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13132)

**Literal equivalence remains false:** CSV/XLSX handles missing/non-finite statistics with `—`, and frozen-seal mutation guards operate independently of the switch. These are the previously identified qualifications. [index.html:14495](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14495), [index.html:5042](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:5042)

**4. New tests**

**Yes, the new assertions distinguish their named defects.** Reverting the ROI fix leaves the seal-only status blank; reverting the stale-save expression exports `999.5`, failing the required `None`. [test:679](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:679), [test:685](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:685)

Validation: **186/187 selected JavaScript tests passed**; the remaining failure required a writable temporary directory. Chromium startup was blocked by the same sandbox restriction, so browser assertions were inspected rather than executed. Extracted-function checks reproduced both old defects and verified the fixes. No files changed.

VERDICT: GO
