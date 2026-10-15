No new BLOCKER, MAJOR or MINOR correctness findings within step 5’s scope.

1. **Round-8 findings**

| Finding | Status |
|---|---|
| Stale/unreadable R status depended on legacy `rFactor` | **Resolved.** The sealed branch now displays `R: —` and its reason before testing legacy-value truthiness. [index.html:14691](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14691) |
| Engine-card test could not catch the old fallback | **Resolved.** The fixture supplies a truthy `backendResult` and requires no engine card for unreadable seals. [test_browser_seal_step5.py:787](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:787), [assertion:808](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:808) |
| Provenance test could not catch legacy status | **Resolved.** A readable local seal carries poisoned adjacent fields; assertions require `converged`, recorded χ²ᵣ and recorded designation. [test_browser_seal_step5.py:822](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:822) |
| PNG drawing coordinates and statistic-source discrimination | **Retained coverage limit.** The test checks annotation text; recorded and legacy χ² still agree. [test_browser_seal_step5.py:675](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:675) |
| Stale chart comparison excludes Data and residual chart | **Retained stated limit.** [test_browser_seal_step5.py:719](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:719) |

2. **Switch OFF:** I found no additional observable change beyond the previously accepted exceptions. Authority gates preserve the legacy chart, stack and fit-file paths. [index.html:9423](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9423), [11871](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11871), [12386](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12386), [13150](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13150).

3. **Switch ON, any sealed state:** No remaining observable dependence on adjacent legacy fields was found in the migrated consumers. Strictly speaking, property accesses remain: the R caller passes `rFactor` and the renderer compares its identity; uncertainty validation inspects `backendResult` before its stale return. These do not change the displayed result for the reviewed fixtures and call paths. Thus the claim is independence of output, not literally zero property reads. [index.html:9544](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9544), [14691](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14691), [14785](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14785). Spectrum/project persistence and loaders remain deferred to step 6.

4. **Named defects are discriminated.** In-memory execution of extracted production functions/conditions confirmed that restoring each defect violates the corresponding assertion:
   - Old R code: blank without the duplicate versus `R: —` with it; fails the equality assertion. [test:796](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:796)
   - Old engine fallback: unreadable seal shows `lmfit`; fails the absence assertion. [test:808](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:808)
   - Old provenance status: returns `POISON`; fails the convergence assertion. [test:829](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:829)

Validation: **157/157 selected JavaScript tests passed.** The four targeted browser cases were blocked at Chromium startup by temporary-directory permissions; their browser assertions were not executed. No files changed.

VERDICT: GO
