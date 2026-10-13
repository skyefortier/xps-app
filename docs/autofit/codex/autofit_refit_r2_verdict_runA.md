Reviewed `b804968..b27f366`, focusing on round 2 (`947f4b4..b27f366`), read-only. **Two transaction defects remain.**

1. **MAJOR — Undo restores the old frame but retains the final fit’s arrays.**  
   The new [_historyContext()](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/templates/index.html:2412) captures neither `fitResult` nor `nextId`. Undo restores peaks, correction, fields and anchors, but leaves Auto-Fit’s final result attached.

   An in-memory probe using the actual history functions restored `ccShift` from **0.2 to 0**, while retaining the final grid **[284.8, 284.3, 283.8]** instead of the previous **[285, 284.5, 284]**. [Plotting still selects that frozen grid and background](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/templates/index.html:11353), combining them with restored peaks and raw data in the old frame. Marking statistics stale does not repair that display.

   Carry and restore the previous result and allocation state through Undo/Redo. The [browser Undo test](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/tests/test_browser_autofit_refit.py:174) misses this because it compares only peaks, correction, anchors and fields. **Non-physical inputs: no.**

2. **MAJOR — Rollback can delete an earlier slider edit’s undo history.**  
   [Auto-Fit snapshots history](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/templates/index.html:8324) before its later `pushUndo()` [flushes a pending slider burst](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/templates/index.html:2450). On failure, restoring the captured stacks removes both Auto-Fit’s entry and that older edit’s newly flushed entry; the pending burst has already been cleared.

   Reproduction with the actual functions: amplitude **20 → 25**, pending slider history; Auto-Fit produces undo entries **[20, 25]**; rollback leaves amplitude **25**, **zero undo entries**, and no pending burst. The earlier edit is no longer undoable.

   Flush pending history before taking the transaction snapshot, or preserve it explicitly. **Non-physical inputs: no; requires starting/confirming Auto-Fit within the 500 ms debounce interval.**

3. **MINOR — Cancel is inaccessible by keyboard.**  
   The [busy keyboard guard](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/templates/index.html:6382) prevents every key’s default action, including Tab, Enter and Space. The overlay does not focus Cancel, and even a focused Cancel cannot activate normally by keyboard. Preserve keyboard operation within the busy dialog while refusing application shortcuts. **Non-physical inputs: no.**

Other review results:

- The anchor request preserves main’s numerical inputs/settings by inspection. The final request rereads shifted points, re-rounded bounds and manual anchors, retaining overlays, amplitude floor, method, three perturbations and captured anchor ID.
- Both Δ branches reach the final fit. Both responses use the same anchor gates; only the first derives the shift. Auto-Fit builds GL/asym-GL, not LA/DS+G.
- Both uploads now receive the abort signal. Save/export guards and the overlay address the previously exposed ordinary interaction paths.
- `confirm.json` and `summary.json` reproduce exactly. The B4C table matches its files. The corrected **16 high-R cases plus two B4C cases** and revised student-note numbers agree with measurements. Confirmation remains **49 close comparisons, one 11.516 pp outlier and three acceptance mismatches**.
- The browser tests add useful real-state checks, but the simulated harness still stubs core transaction functions. The exact-points test proves stored energy-array equality for one spectrum, not rendered background/model identity across all requested paths.
- Q5 remains measurement-only; no unrelated production change found.

**Validation:** 163 selected JavaScript tests passed; actual-function probes demonstrated both history defects. Browser/server tests were inspected but not rerun under the read-only sandbox. No files changed.

**VERDICT: NO-GO**
