No BLOCKER or MAJOR found. **Two MINOR issues remain:** a status-bar dependency on legacy `rFactor`, and incomplete regression coverage.

**1. Round-7 findings**

| Finding | Status |
|---|---|
| `_sealDesignation` bypasses readability checks | **Resolved.** `_sealReadableView` checks version, required payloads and successful view construction. [index.html:10144](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10144) |
| Unreadable seal falls back to local/unweighted designation and caveat | **Resolved.** The sealed branches return false; the caveat consequently stays empty. [index.html:10141](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10141), [index.html:10178](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10178) |
| Results engine card falls back to `backendResult` | **Resolved in implementation; coverage gap below.** [index.html:10934](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10934) |
| Unreadable-seal provenance fallback; readable local provenance copies `fr.status` | **Resolved in implementation.** Unreadable seals return no derived provenance; readable local seals supply `'converged'`. Coverage remains incomplete. [index.html:10229](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10229) |
| Fit-file fixture never reaches null designation | **Resolved.** Both unknown-version and missing-O cases now require null designation and null saved designation fields. [test_browser_seal_step5.py:782](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:782) |
| PNG coordinates/statistic-source discrimination | **Retained coverage limit.** The test captures text, and recorded/legacy χ² still agree. [test_browser_seal_step5.py:675](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:675) |
| Stale chart comparison excludes Data and residual chart | **Retained stated limit.** [test_browser_seal_step5.py:719](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:719) |

**2. Switch OFF**

I found no additional observable regression within the stated exceptions. `_readsSeal` requires the switch, and both chart and stack preserve their legacy stored-curve paths when it is off. [index.html:9423](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9423), [index.html:11871](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11871), [index.html:12386](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12386)

The existing qualifications remain: frozen-seal mutation guards and CSV/XLSX’s `—` for missing/nonfinite statistics. [index.html:5038](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:5038), [index.html:14515](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14515)

**3. Switch ON: does any consumer still read beside the seal?**

**Yes — MINOR: stale/unreadable R status still depends on legacy `rFactor`.** `_refreshStatsState` passes that field into `_updateRFactorUI`. For the same sealed state, extracted execution produced:

- Without the duplicate: blank R status, no tooltip.
- With `rFactor: {rPct: 99.9, level: 'red'}`: `R: —`, with the stale explanation.

No poisoned numeric R appears, but the visible presentation still depends on a field beside the seal. Handle sealed stale/unreadable state before inspecting `rf`. [index.html:9544](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9544), [index.html:14690](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14690)

**4. Do the new tests detect their named defects?**

**Partly — MINOR coverage gap.** In-memory mutations of extracted production functions/conditions confirmed:

- Restoring local/unweighted fallbacks fails both unreadable cases.
- Restoring direct view access defeats the unknown-version assertion.
- **Restoring the old engine-card fallback survives:** the fixture omits `backendResult`, so the old fallback also hides the card. Add a truthy poisoned `backendResult`. [test_browser_seal_step5.py:784](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:784)
- **Restoring `status: fr.status || null` survives:** the fixture uses a server seal, so provenance is null. Add a readable local seal with poisoned status and require `'converged'`. The existing local test checks only provenance truthiness. [test_browser_seal_step5.py:778](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:778), [test_browser_seal_step5.py:356](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:356)

Validation: **199/200 selected JavaScript tests passed**; backend parity and Chromium startup were blocked by temporary-directory permissions. Browser assertions were not executed. No files changed.

VERDICT: NO-GO
