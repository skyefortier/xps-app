No BLOCKER found. **One new MAJOR regression prevents GO:** the stale-preview fix also changes the shipped switch-off behavior.

**MAJOR — the new guards bypass the authority switch.** `_SEAL_AUTHORITATIVE` remains `false`, but Run Fit already attaches a seal. Consequently, `!state.fitResult.seal` makes the chart reject its stored server curve even with sealed readers disabled. The stack similarly recomputes its background, but can still use the legacy `fittedY`, mixing the two paths. See [index.html:8884](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:8884), [index.html:10066](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10066), [index.html:12369](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12369), and [index.html:11881](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11881).

Executing the extracted chart calculations with identical inputs and the switch OFF changed the envelope from `[12,14]` to `[4,6]`. The stack retained `[12,14]` while changing its background. Gate the new exclusions on the authority switch as well as seal presence.

**1. Round-5 findings**

| Finding | Status |
|---|---|
| STALE chart consumes legacy arrays | **Resolved with readers ON**, but introduces the MAJOR above. The new guard forces live-preview arrays. [index.html:12369](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12369) |
| STALE stack consumes legacy arrays | **Resolved with readers ON.** Path B reconstructs from the source tab’s persisted settings; the stale-state check rejects its legacy envelope. [index.html:11854](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11854) |
| Sigma-dependent rule coverage | **Improved; MINOR limitation remains.** The new test changes recorded sigma independently, but can skip and asserts any matching warning rather than the selected parameter’s warning. [test:728](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:728) |
| Poisoned R value never asserted | **Resolved for CURRENT Results/status display.** Both are now checked for `99.9`. [test:710](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:710) |
| PNG coordinates and statistic-source discrimination | **MINOR, remaining coverage limits.** Annotation text is checked; coordinates are not, and the recorded/legacy statistic still agrees in that test. [test:654](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:654) |
| Broader disagreeing-duplicate coverage | **Partial.** The new stale regression exercises only the main chart, excluding Data and the separate residual chart; it does not exercise the stack. [test:698](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:698) |

**2. Does any sealed consumer still read a legacy duplicate?**

**Literally, yes.** For STALE fits, `_shownStats` still reads legacy statistics, and Results calls it before suppressing their presentation. These reads do not establish another displayed-statistic defect. [index.html:9425](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9425), [index.html:10873](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10873).

The “ANY state” guarantee also has an unreadable-record exception: `_sealDesignation` returns null on failure, so `.fit.json`’s `sd && stale` suppression can fall through to legacy `chiReduced`. The file still carries stale-state qualification, making this a **MINOR residual fallback**, rather than an unqualified current result. [index.html:10138](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10138), [index.html:13134](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13134).

With readers ON and a readable seal, I found no remaining chart/stack numerical dependence on the poisoned copies. With readers OFF, the stack dependence described above remains.

**3. Unsealed fits: exactly today’s behavior?**

The new chart/stack guards preserve unsealed behavior. Across the whole step-5 diff, literal equivalence retains the previously stated qualification: CSV/XLSX now substitutes `—` for missing/nonfinite statistics. [index.html:14497](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14497). This does not excuse the separate regression affecting newly produced, seal-bearing fits while the switch is OFF.

**4. Do the new tests fail on their named defects?**

Focused in-memory mutation checks confirmed that restoring the old chart read breaks duplicate equivalence, restoring the R read exposes `99.9`, and reading legacy sigma suppresses the intended warning in a discriminating fixture. The committed sigma test retains the qualifications above; the committed stale test does not protect the stack. The existing switch-off test asserts the stored envelope and should detect the new regression when the recomputed curve differs. [test:159](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:159).

Validation: **186/187 selected JavaScript tests passed**; one backend parity check required a writable temporary directory. Browser tests were blocked at Chromium startup by the same filesystem restriction. No files changed.

VERDICT: NO-GO
tokens used
108,301
No BLOCKER found. **One new MAJOR regression prevents GO:** the stale-preview fix also changes the shipped switch-off behavior.

**MAJOR — the new guards bypass the authority switch.** `_SEAL_AUTHORITATIVE` remains `false`, but Run Fit already attaches a seal. Consequently, `!state.fitResult.seal` makes the chart reject its stored server curve even with sealed readers disabled. The stack similarly recomputes its background, but can still use the legacy `fittedY`, mixing the two paths. See [index.html:8884](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:8884), [index.html:10066](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10066), [index.html:12369](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12369), and [index.html:11881](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11881).

Executing the extracted chart calculations with identical inputs and the switch OFF changed the envelope from `[12,14]` to `[4,6]`. The stack retained `[12,14]` while changing its background. Gate the new exclusions on the authority switch as well as seal presence.

**1. Round-5 findings**

| Finding | Status |
|---|---|
| STALE chart consumes legacy arrays | **Resolved with readers ON**, but introduces the MAJOR above. The new guard forces live-preview arrays. [index.html:12369](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12369) |
| STALE stack consumes legacy arrays | **Resolved with readers ON.** Path B reconstructs from the source tab’s persisted settings; the stale-state check rejects its legacy envelope. [index.html:11854](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11854) |
| Sigma-dependent rule coverage | **Improved; MINOR limitation remains.** The new test changes recorded sigma independently, but can skip and asserts any matching warning rather than the selected parameter’s warning. [test:728](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:728) |
| Poisoned R value never asserted | **Resolved for CURRENT Results/status display.** Both are now checked for `99.9`. [test:710](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:710) |
| PNG coordinates and statistic-source discrimination | **MINOR, remaining coverage limits.** Annotation text is checked; coordinates are not, and the recorded/legacy statistic still agrees in that test. [test:654](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:654) |
| Broader disagreeing-duplicate coverage | **Partial.** The new stale regression exercises only the main chart, excluding Data and the separate residual chart; it does not exercise the stack. [test:698](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:698) |

**2. Does any sealed consumer still read a legacy duplicate?**

**Literally, yes.** For STALE fits, `_shownStats` still reads legacy statistics, and Results calls it before suppressing their presentation. These reads do not establish another displayed-statistic defect. [index.html:9425](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9425), [index.html:10873](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10873).

The “ANY state” guarantee also has an unreadable-record exception: `_sealDesignation` returns null on failure, so `.fit.json`’s `sd && stale` suppression can fall through to legacy `chiReduced`. The file still carries stale-state qualification, making this a **MINOR residual fallback**, rather than an unqualified current result. [index.html:10138](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10138), [index.html:13134](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13134).

With readers ON and a readable seal, I found no remaining chart/stack numerical dependence on the poisoned copies. With readers OFF, the stack dependence described above remains.

**3. Unsealed fits: exactly today’s behavior?**

The new chart/stack guards preserve unsealed behavior. Across the whole step-5 diff, literal equivalence retains the previously stated qualification: CSV/XLSX now substitutes `—` for missing/nonfinite statistics. [index.html:14497](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14497). This does not excuse the separate regression affecting newly produced, seal-bearing fits while the switch is OFF.

**4. Do the new tests fail on their named defects?**

Focused in-memory mutation checks confirmed that restoring the old chart read breaks duplicate equivalence, restoring the R read exposes `99.9`, and reading legacy sigma suppresses the intended warning in a discriminating fixture. The committed sigma test retains the qualifications above; the committed stale test does not protect the stack. The existing switch-off test asserts the stored envelope and should detect the new regression when the recomputed curve differs. [test:159](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:159).

Validation: **186/187 selected JavaScript tests passed**; one backend parity check required a writable temporary directory. Browser tests were blocked at Chromium startup by the same filesystem restriction. No files changed.

VERDICT: NO-GO
