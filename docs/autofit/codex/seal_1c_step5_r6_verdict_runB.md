No BLOCKER found. **One MAJOR regression remains, plus MINOR legacy-metadata and coverage limits.**

**MAJOR — the new guards bypass the authority switch.** `_SEAL_AUTHORITATIVE` still ships as `false`, and Run Fit already attaches a seal. Nevertheless, the new `!state.fitResult.seal` / `!fr.seal` conditions disable the existing frozen-data paths even with the switch OFF. The chart now recomputes instead of drawing the stored fit; the stack recomputes its background/components while potentially retaining the stored envelope. The exclusion should require **both** an enabled switch and a seal. [index.html:8884](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:8884), [index.html:10066](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10066), [index.html:12369](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12369), [index.html:11854](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11854).

Focused execution of the actual branches confirmed this regression and confirmed that restoring the previous guards restores switch-OFF behavior.

1. **Round-5 findings**

   - **STALE chart/stack legacy-array dependence: resolved with authority ON.** Both now bypass the poisoned arrays. An isolated stack mutation check confirmed that removing its new guard restores the discrepancy. [index.html:11854](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11854), [index.html:12369](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12369).
   - **Sigma-dependent rule coverage: substantially resolved.** The new test changes only the record’s sigma to `null` and requires the corresponding warning. It can skip if no suitable parameter exists. [test_browser_seal_step5.py:721](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:721).
   - **Poisoned R coverage: resolved for the tested CURRENT status-bar/Results paths.** Both are checked for `99.9`. [test_browser_seal_step5.py:710](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:710).
   - **PNG coordinates: stated MINOR limit remains.** Annotation text is checked; coordinates are not. The PNG test also still leaves recorded and legacy χ² agreeing, so it does not independently discriminate that statistic’s source. [test_browser_seal_step5.py:654](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:654).
   - **Broader duplicate coverage: still incomplete.** The new stale-poison test exercises the main chart, not the stack. [test_browser_seal_step5.py:694](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:694).

2. **Does any consumer still read a legacy duplicate beside a seal?**

   **Yes, literally, even with authority ON.** `_shownStats` reads legacy statistics for STALE results, although the reviewed display paths suppress those values. More materially, `.fit.json` still exports legacy `status`, `startsModelKey`, and a fallback `caveat`. A focused execution with a CURRENT server designation exported poisoned values for all three. **MINOR:** this prevents claiming complete consumer migration, although it does not reproduce the numerical-preview defect. [index.html:9425](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9425), [index.html:13138](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13138), [index.html:13145](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13145).

3. **Unsealed fits: exactly today’s behavior?**

   The new chart/stack guards preserve their unsealed paths; no new regression found there. **Literal equivalence remains qualified:** CSV/XLSX now substitutes `—` for missing/nonfinite statistics instead of the former unconditional formatting. Unsealed compatibility does not resolve the switch-OFF regression affecting newly produced fits that already carry seals. [index.html:14497](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14497).

4. **Do the new tests catch their named defects?**

   Their assertions discriminate the targeted chart, R, and sigma defects, subject to the sigma test’s skip condition. Isolated executions confirmed that restoring legacy R/sigma readers produces the poisoned R and removes the expected sigma warning. The stale chart test does **not** establish stack coverage or switch-OFF compatibility.

Validation: **199/200 JavaScript tests passed**; one backend parity check was blocked by temporary-directory permissions. Chromium launch was also blocked by the read-only sandbox, so browser tests were not executed. No files changed.

**VERDICT: NO-GO**
tokens used
103,500
No BLOCKER found. **One MAJOR regression remains, plus MINOR legacy-metadata and coverage limits.**

**MAJOR — the new guards bypass the authority switch.** `_SEAL_AUTHORITATIVE` still ships as `false`, and Run Fit already attaches a seal. Nevertheless, the new `!state.fitResult.seal` / `!fr.seal` conditions disable the existing frozen-data paths even with the switch OFF. The chart now recomputes instead of drawing the stored fit; the stack recomputes its background/components while potentially retaining the stored envelope. The exclusion should require **both** an enabled switch and a seal. [index.html:8884](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:8884), [index.html:10066](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10066), [index.html:12369](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12369), [index.html:11854](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11854).

Focused execution of the actual branches confirmed this regression and confirmed that restoring the previous guards restores switch-OFF behavior.

1. **Round-5 findings**

   - **STALE chart/stack legacy-array dependence: resolved with authority ON.** Both now bypass the poisoned arrays. An isolated stack mutation check confirmed that removing its new guard restores the discrepancy. [index.html:11854](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11854), [index.html:12369](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12369).
   - **Sigma-dependent rule coverage: substantially resolved.** The new test changes only the record’s sigma to `null` and requires the corresponding warning. It can skip if no suitable parameter exists. [test_browser_seal_step5.py:721](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:721).
   - **Poisoned R coverage: resolved for the tested CURRENT status-bar/Results paths.** Both are checked for `99.9`. [test_browser_seal_step5.py:710](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:710).
   - **PNG coordinates: stated MINOR limit remains.** Annotation text is checked; coordinates are not. The PNG test also still leaves recorded and legacy χ² agreeing, so it does not independently discriminate that statistic’s source. [test_browser_seal_step5.py:654](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:654).
   - **Broader duplicate coverage: still incomplete.** The new stale-poison test exercises the main chart, not the stack. [test_browser_seal_step5.py:694](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:694).

2. **Does any consumer still read a legacy duplicate beside a seal?**

   **Yes, literally, even with authority ON.** `_shownStats` reads legacy statistics for STALE results, although the reviewed display paths suppress those values. More materially, `.fit.json` still exports legacy `status`, `startsModelKey`, and a fallback `caveat`. A focused execution with a CURRENT server designation exported poisoned values for all three. **MINOR:** this prevents claiming complete consumer migration, although it does not reproduce the numerical-preview defect. [index.html:9425](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9425), [index.html:13138](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13138), [index.html:13145](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13145).

3. **Unsealed fits: exactly today’s behavior?**

   The new chart/stack guards preserve their unsealed paths; no new regression found there. **Literal equivalence remains qualified:** CSV/XLSX now substitutes `—` for missing/nonfinite statistics instead of the former unconditional formatting. Unsealed compatibility does not resolve the switch-OFF regression affecting newly produced fits that already carry seals. [index.html:14497](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14497).

4. **Do the new tests catch their named defects?**

   Their assertions discriminate the targeted chart, R, and sigma defects, subject to the sigma test’s skip condition. Isolated executions confirmed that restoring legacy R/sigma readers produces the poisoned R and removes the expected sigma warning. The stale chart test does **not** establish stack coverage or switch-OFF compatibility.

Validation: **199/200 JavaScript tests passed**; one backend parity check was blocked by temporary-directory permissions. Chromium launch was also blocked by the read-only sandbox, so browser tests were not executed. No files changed.

**VERDICT: NO-GO**
