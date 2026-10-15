The round-3 **MAJOR activation failure is resolved**. No additional BLOCKER or MAJOR runtime defect found, but MINOR issues remain: a broken regression-test harness, a legacy statistic read in stale `.fit.json` output, and incomplete coverage repairs.

1. **Round-3 findings**

| Finding | Status and evidence |
|---|---|
| **MAJOR:** activating frozen `{seal}` throws | **Resolved.** Activation skips the lazy write through `_isInstalledSeal`. Extracted-method checks reached rendering for CURRENT, PENDING, UNCONFIRMED and STALE without modifying the result. [index.html:3325](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:3325) |
| Tab test only enters an unfitted tab | **Resolved.** The new test returns to the frozen seal-only tab. It would encounter the original exception. [test_browser_seal_step5.py:598](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:598) |
| “Undo” merely reverses an assignment | **Resolved by an additional test.** It calls `pushUndo()` and `undo()`, checks CURRENT, then checks recorded curves. [test:614](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:614) |
| Bounds tested, sigma not distinguished | **Partially resolved.** The new test distinguishes the Results sigma source. It does not exercise sigma-dependent uncertainty-rule behavior; the original rule test still changes only bounds. [test:628](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:628), [test:257](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:257) |
| Stale XLSX could retain a statistic row | **Resolved.** The test explicitly rejects a `Chi-squared` row. [test:548](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:548) |
| Preview test checks label, not curve replacement | **Resolved for retaining the rejected record’s curve.** It now requires the curve to differ from that record. [test:579](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:579) |
| PNG only checks metadata | **Partially resolved.** `fillText` assertions cover visible pending/stale annotation. Drawn curves remain unchecked. [test:654](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:654) |
| Agreeing legacy duplicates conceal wrong readers | **Partially resolved.** Disagreement now tests chart arrays and Results statistics/sigma, but not exports; even the changed legacy R value is not asserted. [test:638](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:638) |

2. **Switch ON**

I found no further write/throw on a frozen seal-only result in the reviewed step-5 consumers. The three mutators also passed focused strict-mode checks without changing the result. [index.html:5038](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:5038), [index.html:8044](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:8044). Persistence/loaders remain step 6.

**MINOR — stale `.fit.json` still reads a legacy statistic.** `_shownStats` falls back to `fr.chiReduced` when `_sealedDisplay` rejects STALE, and `_doSaveFit` writes that value unconditionally. In an extracted-function reproduction with the stale judgment stubbed, a record containing χ²ᵣ `1.25` and legacy duplicate `999.5` exported `999.5`; the same seal-only result exported `null`. The stale designation prevents a current-result claim, but the output still depends on the duplicate. [index.html:9352](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9352), [index.html:13063](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13063)

3. **Switch OFF**

No runtime regression found for today’s supported mutable results. The new guards preserve their mutation behavior.

Literal equivalence remains **false**: CSV/XLSX substitutes `—` for missing/non-finite statistics instead of the previous unconditional formatting. This is the round-3 qualification, not a newly introduced defect. [index.html:14426](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14426)

4. **Do the tests fail on their named defects?**

**Not all.** The targeted activation, real undo, displayed sigma, stale XLSX, preview retention and annotation assertions discriminate the defects described above. The remaining MINOR coverage limitations are listed in the table.

**MINOR — this round breaks an existing JavaScript test.** Its harness extracts `_restampSupport` without the newly required `_isInstalledSeal`, producing `ReferenceError: _isInstalledSeal is not defined` before checking legacy restamping. Include the real helper in that harness. [stale_statistics.test.js:117](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/js/stale_statistics.test.js:117)

Validation: **198/200 selected JavaScript tests passed**. One failed because of that harness regression; the other required a writable temporary directory. Chromium startup was likewise blocked by temporary-directory permissions, so the browser assertions were inspected, not executed. No files changed.

**VERDICT: NO-GO**
