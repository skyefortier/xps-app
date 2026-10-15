The round-3 MAJOR activation failure is fixed. **Two concrete MINOR defects remain, plus MINOR coverage gaps. No BLOCKER or additional MAJOR production defect found.**

**1. Round-3 findings**

| Finding | Status |
|---|---|
| Frozen seal-only activation throws | **Resolved.** Activation skips the legacy R write. [index.html:3325](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:3325) |
| Tab-switch test only enters an unfitted tab | **Resolved.** The new test returns to frozen `{seal}` and checks successful activation and preserved shape. [test:598](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:598) |
| “Undo” merely reverses an assignment | **Resolved by additional coverage.** The new test invokes `pushUndo()` and `undo()`. [test:614](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:614) |
| Bounds tested, sigma source untested | **Resolved for displayed sigma; partial for uncertainty rules.** The added test changes recorded sigma and checks Results, but does not assert sigma-dependent validation warnings. [test:628](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:628) |
| Stale XLSX might retain a statistic row | **Resolved.** Explicit absence assertion added. [test:548](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:548) |
| Preview verdict test checks only its label | **Resolved.** It now rejects retention of the recorded envelope after failure. [test:579](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:579) |
| PNG tests inspect metadata only | **Partially resolved.** `fillText` assertions cover visible state/check annotations; plotted curves remain unchecked. [test:654](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:654) |
| Agreeing legacy duplicates conceal incorrect readers | **Partially resolved.** Disagreeing duplicates now exercise chart and Results, but not all affected consumers or fields. [test:638](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:638) |

**2. Switch ON**

No remaining write/throw on frozen `{seal}` was found in the reviewed step-5 activation and consumer paths. The background, envelope and support-key writes are guarded. Extracted-function checks preserved exactly `["seal"]` through activation and those mutators for CURRENT, PENDING, UNCONFIRMED and STALE. [index.html:5038](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:5038), [index.html:8047](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:8047)

**MINOR — ROI status still reads a legacy duplicate.** Activation passes `fitResult.roiRange` directly; `_updateROIDisplay` prints it without consulting the record. A frozen seal-only result consequently clears the ROI status, while a disagreeing duplicate supplies incorrect displayed limits. The extracted activation check reproduced the blank status. Derive the displayed fit range from the sealed view. [index.html:3329](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:3329), [index.html:14624](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14624)

Persistence/loaders remain outside step 5.

**3. Switch OFF**

No new production regression found for today’s supported result shapes. The readers retain early OFF gates. [index.html:9313](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9313)

Literal equivalence remains **false**: CSV/XLSX substitutes `—` for missing/non-finite statistics instead of the former formatting behavior, as round 3 already noted. Also, the new frozen-seal guards operate independently of the switch, although that is not today’s normal result shape. [index.html:14426](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14426), [index.html:5038](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:5038)

**4. Do all tests fail on their named defect?**

**No.** The activation, real undo, displayed sigma, stale XLSX and preview replacement additions discriminate their targeted failures by inspection. Remaining **MINOR** gaps:

- The duplicate test poisons R to 99% but never asserts R’s value. It also does not exercise exports with disagreeing duplicates. [test:643](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:643)
- The PNG annotation test leaves recorded and legacy χ² agreeing, so replacing its statistic reader with `state.fitResult.chiReduced` would still pass. It checks no drawing coordinates. [test:661](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:661)

**MINOR — Round 4 breaks an existing regression test.** The standalone `_restampSupport` harness omits the newly required `_isInstalledSeal`, producing `ReferenceError: _isInstalledSeal is not defined` before its assertions. Include the real helper in that harness. [stale_statistics.test.js:117](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/js/stale_statistics.test.js:117)

Validation: **156/157 selected JavaScript tests passed**; the failure above was reproduced separately. Browser tests could not start because Chromium’s temporary-directory creation was denied by the read-only sandbox. No files changed.

The prior MAJOR is resolved, but the failing regression test and remaining legacy ROI consumer prevent approval of this checkout.

VERDICT: NO-GO
