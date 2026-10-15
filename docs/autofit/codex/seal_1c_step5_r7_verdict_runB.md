The round-6 MAJOR is fixed. **No BLOCKER or MAJOR found; two MINOR issues remain**, so the complete consumer-migration claim is not yet satisfied.

1. **Round-6 findings**

| Finding | Status |
|---|---|
| Switch-OFF chart/stack regression | **Resolved.** Both exclusions now require `_readsSeal`, which checks the switch and seal. [index.html:9423](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9423), [11859](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11859), [12374](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12374). |
| `.fit.json` legacy metadata/statistic fallback | **Resolved in the saver**, including when designation is null. Its regression coverage remains incomplete, below. [index.html:13138](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13138). |
| `_shownStats` reads STALE legacy statistics | **Resolved.** Sealed results not displayed as recorded return null statistics. [index.html:9429](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9429). |
| Stale-preview test omits stack | **Resolved.** It now compares stack energies, background, envelopes, counts and component curves. [test_browser_seal_step5.py:727](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:727). |
| Sigma test skips / accepts another parameter’s warning | **Resolved.** Fixture selection must succeed, and the assertion names the selected parameter. [test_browser_seal_step5.py:759](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:759). |
| Poisoned R coverage | **Retained:** Results and status bar are checked. [test_browser_seal_step5.py:738](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:738). |
| PNG / broader duplicate coverage | **Remaining MINOR limits.** PNG checks annotation text, not coordinates, and leaves legacy/recorded χ² agreeing. The stale chart comparison excludes Data and the separate residual chart. [test_browser_seal_step5.py:675](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:675), [719](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:719). |

2. **Switch OFF**

I found no remaining user-visible regression within the stated exceptions. Focused execution confirmed both chart and stack retain stored envelope `[12,14]` and background `[8,9]`. Reinstating the round-5 guards changes the chart envelope to `[4,6]` and the stack background to `[1,2]`. The new assertions distinguish these failures. [test_browser_seal_step5.py:170](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:170).

3. **Switch ON, ANY sealed state: legacy reads remain**

**MINOR — designation/provenance still falls back beside a seal.**

- Even with a readable local seal, `_provenanceOf` copies `fr.status`. Extracted execution reproduced `status: "POISON"`. [index.html:10224](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10224).
- When `_sealView` throws, `_isLocalFit` and `_isUnweightedLocal` use adjacent legacy engine/objective fields. `_provenanceOf` can then copy legacy weighting, status and χ². Extracted execution reproduced a `peaks-only` record labelled “Residual variance” and provenance containing poisoned χ². [index.html:10140](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10140), [10167](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10167), [10226](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10226).
- Results similarly falls back to legacy `backendResult` for its engine card. [index.html:10922](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10922).

These consumers need the same “sealed but unreadable means no legacy fallback” distinction as the saver.

4. **Do the tests detect their named defects?**

The chart/stack assertions discriminate the guard defects; focused mutations of the actual consumer code confirmed this. The selected-parameter sigma assertion is also substantially stronger.

**MINOR — the unreadable-file fixture misses the null-designation defect.** It changes only `seal.v`. `sealedState` rejects that version, but `_sealDesignation` calls `_sealView` directly, which still reads the intact payload and returns a designation. [test_browser_seal_step5.py:781](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:781), [index.html:9355](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9355), [10145](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10145).

An isolated mutation restoring only the old engine/objective/weighting/reportable fallbacks survives both committed fixture variants. Removing `O` reaches the missing branch and exposes the poison. Add that case and assert designation is null.

Validation: **199/200 selected JavaScript tests passed**; backend parity and Chromium startup were blocked by temporary-directory permissions. Browser tests were not executed. No files changed.

**VERDICT: NO-GO**
