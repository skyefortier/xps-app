Two **MAJOR** lifecycle defects prevent approval. No BLOCKER found.

1. **Producers and reinstalls — MAJOR: retained seals can become stranded PENDING.**  
   Reproduction: Run Fit A installs a seal with verification outstanding; Run Fit B claims the tab and then fails. A’s reply is discarded, deleting its attempt without caching or restarting verification ([index.html:9477](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:9477)). B’s failure path retains A’s result but never calls `_ensureVerified` ([index.html:10348](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:10348)). The fit remains PENDING indefinitely.

   Rollback has two related gaps: inactive-tab rollback returns before its verification trigger ([index.html:8046](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8046)); active rollback can find an obsolete producer attempt and incorrectly treat it as sufficient ([index.html:9509](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:9509)). I reproduced the missing inactive trigger and discarded-attempt state with extracted page functions.

   Normal producer call sites finish with frozen seal-only results. Strictly, `runFitLocal` still temporarily installs a legacy result, and retains it when called without `options.seal` ([index.html:10914](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:10914)); both page callers supply a seal. History, contextual undo, activation, and loaders otherwise preserve or install seals correctly.

2. **Auto-Fit — MAJOR: Cancel and timeout do not cover staged verification.**  
   The final-fit timeout is cleared before verification ([index.html:8880](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8880)). Auto-Fit then awaits both checks before inspecting `userCancelled` ([index.html:8913](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8913)), while verification’s `fetch` has neither the transaction’s abort signal nor a timeout ([index.html:9359](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:9359)). A stalled check leaves the provisional workspace and blocking overlay in place after Cancel. My flow reproduction remained unfinished and unrestored after cancellation; rollback occurred only after releasing the replies.

   The publication gate itself correctly requires counting outcomes under current numerics/epoch and a CURRENT `sealedState` ([index.html:8922](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8922)). Superseded operations correctly avoid overwriting their successors.

   **MINOR: transaction cleanup does not meet the “nothing cached unless published” requirement.** `_commitStaged` caches the verdict before the CURRENT gate; rejection afterward does not remove it ([index.html:9464](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:9464), [index.html:8935](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8935)). Earlier failures also leave `_stagedTxns` entries behind. Make rejection and cancellation explicitly terminate the staged transaction.

3. **Old authorities and legacy behavior — no additional defect found.**  
   Sealed support, starts, statistics, and uncertainty readers dispatch to the seal before using legacy authorities ([index.html:8234](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8234), [index.html:9701](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:9701), [index.html:15103](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:15103)).

   The committed census contains 121 rows: 81 LEGACY, 40 dropped, zero seals, zero restore differences, zero unexpected re-save differences, and no page errors. Its comparison excludes only the declared new fields ([seal_legacy_census.py:104](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/scripts/seal_legacy_census.py:104)). This supports parity for those fixtures; it is not proof for every possible legacy save.

4. **Spectrum and export fixes — correct on inspection.**  
   STALE spectrum convenience fields now use the live ROI, background, model, residuals, and area grid while retaining the original seal ([index.html:13553](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:13553)). This satisfies the stated Q5/F1 rules.

   State/provenance now precede the record within the appended block in both TSV paths, CSV, and XLSX Info ([index.html:14349](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:14349), [index.html:14371](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:14371), [index.html:14893](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:14893), [index.html:14913](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:14913)).

5. **Tests — useful ports, but incomplete lifecycle discrimination.**  
   **MINOR:** the Auto-Fit notification assertion was weakened from an exact statistic to any three-decimal number, despite its stub supplying a known value ([autofit_refit.test.js:90](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/tests/js/autofit_refit.test.js:90)).

   The new failure test rejects both checks together and compares only peaks, fit, and three charge controls; it does not establish restoration of the entire workspace/history or cancellation during verification ([test_browser_seal_step7.py:144](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/tests/test_browser_seal_step7.py:144)). The existing supersession test manually calls `_ensureVerified`, masking missing producer recovery ([test_browser_seal_step4.py:187](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/tests/test_browser_seal_step4.py:187)). Add held verification replies, independent anchor/final failures, and failed-successor recovery through actual UI flows.

Validation: 227 targeted Node tests passed; three Python-backed checks failed because the read-only sandbox provides no writable temporary directory. Browser tests and the live two-server census were not rerun. No files changed.

**VERDICT: NO-GO.**
