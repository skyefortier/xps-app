No BLOCKER found. **One MAJOR consumer-migration defect remains.** The three concrete round-4 fixes are resolved.

**MAJOR — STALE chart and stack previews still depend on legacy duplicates.** When `_sealedDisplay` rejects a stale seal, the main chart falls through to `fr.be`, `fr.bgIntensity` and `fr.bgSubtracted`; the stack does likewise. Consequently, identical seals and live models can draw different previews depending on whether legacy duplicates exist. [index.html:12367](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12367), [index.html:12386](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12386), [index.html:11853](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11853)

With the STALE judgment stubbed, executing the real `_buildEntryRenderData` produced envelope `[13, 24]` for `{seal}`, but `[1003, 2004]` after adding disagreeing legacy background/count arrays. This changes the plotted numerical content. Sealed stale results should use the live-preview path independently of those duplicates; preserve the legacy fallback for unsealed results.

1. **Round-4 findings**

| Finding | Status |
|---|---|
| Status-bar range reads legacy `roiRange` | **Resolved.** Activation uses `_fitRoiRange`, which reads recorded energies. [index.html:3329](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:3329), [index.html:14695](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14695) |
| Stale `.fit.json` exports legacy χ² | **Resolved for readable sealed fits.** The stale branch writes `null`. [index.html:13132](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13132) |
| `_restampSupport` harness lacks `_isInstalledSeal` | **Resolved; test passes.** The harness includes the real helper. [stale_statistics.test.js:117](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/js/stale_statistics.test.js:117) |
| Sigma-dependent uncertainty warnings untested | **Remaining MINOR coverage limit.** The added sigma test checks displayed Results text. [test_browser_seal_step5.py:628](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:628) |
| PNG curves unchecked; statistic duplicates agree | **Remaining MINOR coverage limit.** The test observes annotation text, without distinguishing the statistic’s source or checking drawing coordinates. [test:654](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:654) |
| Disagreeing-duplicate coverage incomplete, including R | **Partially resolved.** Stale `.fit.json` now has coverage. The broader duplicate test still checks CURRENT chart/Results only and never asserts the poisoned R value; it misses the MAJOR above. [test:638](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:638), [test:683](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:683) |

2. **Switch ON**

Yes: the stale chart/stack paths above still consume legacy duplicates. I found no additional throw or mutation of frozen `{seal}` in the reviewed step-5 paths. Strict-mode checks of the background, envelope and support mutators preserved exactly `["seal"]`. [index.html:5037](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:5037), [index.html:8044](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:8044)

Focused checks of the rebased detached verifier passed for counting answers, obsolete epochs/numerics, splits, and epoch-specific unreachable outcomes. Persistence/loaders remain outside step 5. [index.html:9303](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9303)

3. **Switch OFF**

No new regression found for today’s supported mutable results. Literal equivalence remains qualified as in round 4: CSV/XLSX substitutes `—` for missing/nonfinite statistics, and frozen-seal mutation guards operate independently of the switch. [index.html:14495](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14495), [index.html:5037](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:5037)

4. **Do the new tests catch their named defects?**

**Yes, by inspection and focused mutation checks.** Restoring the old activation expression clears the range; restoring the old save expression exports `999.5` instead of `null`. Both violate the new assertions. [test:674](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:674)

Validation: **186/187 selected JavaScript tests passed**; one backend parity test was blocked by temporary-directory permissions. Chromium startup was also blocked by the read-only sandbox, so the browser test itself was not executed. No files changed.

**VERDICT: NO-GO**
