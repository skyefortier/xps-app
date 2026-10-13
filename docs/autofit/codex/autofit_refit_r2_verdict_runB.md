Reviewed `b804968..b27f366`, focusing on round 2 (`947f4b4..b27f366`), read-only. **The fit-request changes look sound, but undo and rollback remain incomplete.**

1. **MAJOR — Undo restores the old frame while retaining the final fit’s result.**  
   [_historyContext()](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/templates/index.html:2412) captures correction, fields and anchors, but neither `fitResult` nor `nextId`. Undo therefore restores old peaks and correction while retaining Auto-Fit’s final result.

   An in-memory probe using the actual history functions restored correction **0.6 → 0.4**, but retained the final result’s energy array and background. [updatePlot()](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/templates/index.html:11353) uses those frozen arrays even when statistics are stale. The chart consequently mixes the restored frame with the later fit’s background; the previous result is lost.

   The [browser undo test](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/tests/test_browser_autofit_refit.py:174) explicitly excludes the result and `nextId` from its comparisons, so it does not prove “the whole spectrum.” Carry and restore the complete transaction state through undo/redo. **Non-physical inputs: no.**

2. **MAJOR — Failure can erase a preceding slider edit’s undo history.**  
   [_autoFitSnapshot()](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/templates/index.html:7571) captures the stacks before `pushUndo()` flushes `_undoDebounce`. Rollback restores those earlier stacks, but the pending buffer has already been cleared.

   Reproduced with the actual functions: slider amplitude **100 → 120**, then Auto-Fit starts before the 500 ms debounce expires. Its history contains `[100, 120]`; after failure, both entries disappear and Undo leaves amplitude at **120**. Flush the preceding edit before capturing rollback history, or preserve the pending buffer too. **Non-physical inputs: no; sufficiently quick confirmation is enough.**

3. **MINOR — The student note promises an unavailable diagnostic.**  
   [Line 21](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/docs/superpowers/plans/2026-10-12-autofit-refit-student-note.md:21) directs students to Auto-Fit’s “scattered starts” line. Auto-Fit sends no `n_starts`, and `_autoFitPublish()` does not populate `fitResult.starts`; that panel therefore does not appear. Remove or qualify this guidance. **Non-physical inputs: no.**

4. **MINOR — Confirmation matching is not one-to-one.**  
   [q8_confirm.py](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/scripts/q8_confirm.py:19) independently selects each component’s nearest centre. In committed B4C Scan_1, both shipped Unknown components match measured Unknown 1, leaving Unknown 2 unmatched. Use a bijective assignment or explicitly report unmatched components. The headline **11.516 pp** maximum happens to remain unchanged with a one-to-one assignment. **Non-physical inputs: no; committed measurements.**

Other checks:

- The anchor request preserves main’s numerical inputs/settings by inspection. The final request freshly reads shifted/re-rounded points, background bounds and manual anchors, retaining overlays, amplitude floor, method, three perturbations and the captured anchor ID.
- Both Δ branches reach the final fit. Both responses use the same anchor gates; only the anchor fit derives the shift. Auto-Fit builds GL/asym-GL, not LA/DS+G.
- Both uploads now receive the abort signal. Save/export entry guards and the keyboard guard address the ordinary round-1 interaction paths.
- `summary.json` and `confirm.json` reproduce exactly. The corrected **16 + 2 = 18** R count and B4C table agree with the data. Confirmation retains **49 close comparisons, one outlier and three acceptance mismatches**.
- The note’s paired area changes (**median 0.56 pp, maximum 3.85 pp**), χ²ᵣ range (**−34.8% to +35.2%**) and extra time (**median 0.9 s**) match.
- The exact-points browser assertion is genuine for its successful case, but does not inspect rendered background/model identity. The simulated harness still stubs restoration and publication.
- Q5 remains measurement-only; no unrelated production change found.

**Validation:** 163 targeted JavaScript tests passed; additional in-memory probes reproduced findings 1–2. Browser/server tests were inspected, not rerun under the read-only sandbox. No files changed.

**VERDICT: NO-GO.**
