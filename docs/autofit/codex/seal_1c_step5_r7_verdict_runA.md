No BLOCKER or MAJOR found. **MINOR gaps remain in legacy-field isolation and test coverage.**

1. **Round-6 findings**

| Finding | Status |
|---|---|
| Switch-OFF chart/stack regression | **Resolved.** `_readsSeal` requires both the switch and a seal; both frozen-data exclusions use it. [index.html:9423](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9423), [index.html:11859](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11859), [index.html:12374](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12374) |
| `.fit.json` legacy metadata/statistic fallbacks | **Resolved in the implementation**, including when designation extraction fails. [index.html:13138](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13138) |
| `_shownStats` reading stale legacy statistics | **Resolved.** Sealed results without a displayable record return null statistics. [index.html:9424](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9424) |
| Stale-preview test omitted stack | **Resolved.** It now compares the stack’s energies, background, envelopes, counts and components. [test_browser_seal_step5.py:725](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:725) |
| Sigma test skipped/accepted another parameter’s warning | **Resolved.** Qualification is mandatory and the selected parameter’s warning is required. [test_browser_seal_step5.py:765](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:765) |
| Poisoned R coverage | **Retained.** CURRENT Results and status-bar assertions remain. [test_browser_seal_step5.py:738](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:738) |
| PNG coordinates/statistic-source discrimination | **Remaining MINOR coverage limit.** The test captures text, not coordinates, and leaves recorded/legacy reduced χ² agreeing. The stale chart comparison also still excludes Data and the separate residual chart. [test_browser_seal_step5.py:675](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:675), [test_browser_seal_step5.py:720](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:720) |

2. **Switch OFF:** I found no additional observable regression beyond the stated exceptions. Focused execution confirmed stored chart/stack curves are preserved; restoring the round-5 guards changes the chart envelope and both backgrounds. The new regression test distinguishes these paths. [test_browser_seal_step5.py:170](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:170)

3. **Switch ON, ANY state: legacy dependence remains.**

   - **MINOR — unreadable-seal designation fallback.** When `_sealDesignation` returns null, `_isLocalFit` and `_isUnweightedLocal` consult legacy `engine`/`objective`. With the same unreadable seal, adding those duplicates changed my extracted-function result from nonlocal/“χ²ᵣ” to local/“Residual variance”. These readers control visible captions and banners. Results also falls back to legacy `backendResult` for its engine card. [index.html:10140](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10140), [index.html:10167](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10167), [index.html:10922](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10922)
   - **MINOR — provenance still copies duplicates.** `_provenanceOf` copies `fr.status` even for a readable local seal. When its view is unreadable, the fallback also copies legacy objective, engine, weighting and χ². Focused execution preserved poisoned status and, in the unreadable case, poisoned χ². [index.html:10218](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10218)

4. **The tests discriminate their main defects, but not every claimed fallback.**

   The switch-off assertions distinguish stored curves from recomputation; the stale test now covers stack data; and a focused sigma-reader mutation removes the selected warning.

   **MINOR — the “unreadable-record” fixture misses designation failure.** It changes only `seal.v`. `sealedState` rejects that version, but `_sealDesignation` calls `_sealView` directly and still obtains a designation. Restoring the old engine/objective/weighting/reportable fallbacks therefore leaves this fixture’s output unchanged—I confirmed that in memory. Add a case where view construction itself fails and assert null designation fields. [test_browser_seal_step5.py:781](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:781), [index.html:9355](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9355), [index.html:10143](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10143)

Validation: **199/200 selected JavaScript tests passed**; the remaining backend parity test and browser startup were blocked by temporary-directory permissions. No files changed.

The switch-off regression is fixed, but the requested universal legacy-isolation guarantee remains unmet.

**VERDICT: NO-GO**
