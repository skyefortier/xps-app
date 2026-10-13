Reviewed `b804968..41f3496`, focusing on round 3 (`b27f366..41f3496`), read-only. **No remaining BLOCKER or MAJOR found.**

One **MINOR** remains: [confirmation matching](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/scripts/q8_confirm.py:22) ignores unmatched components on the measured side when it has more components than the shipped result. A probe returned zero difference despite an extra measured component; reversing the comparison returned infinity. Check unmatched components on both sides. **Non-physical inputs: no.** All committed comparisons have equal component counts, so this does not change the reported confirmation.

Review results:

- Actual-function probes confirm Undo/Redo restores the previous result arrays, ID counter, peaks, correction, fields and anchors. Rollback now preserves—and can undo—a preceding pending slider edit.
- Both shift branches reach the final fit. Request probes covered Δ = 0 and a nonzero shift that changes the selected window from three points to two, including rounded bounds and moved manual anchors.
- The anchor request preserves main’s numerical inputs/settings by inspection. The final request rereads the shifted page, retaining bounds overlays, amplitude floor, method, three perturbations and the captured anchor ID. Both responses face the same anchor gates; only the first determines the shift. Auto-Fit builds GL/asym-GL, not LA/DS+G.
- The overlay, keyboard handling, save/export guards and abort signals address the ordinary between-fit interaction paths. Publication and the history snapshot occur only after final acceptance.
- `summary.json` and `confirm.json` reproduce exactly; the B4C table matches its files. The **16 + 2 = 18/51** R count and student-note numbers agree with measurements. Confirmation retains **49 close comparisons, one 11.516 pp outlier and three acceptance mismatches**.
- Q5 remains measurement-only; no unrelated production change found.

**Validation:** 154 targeted JavaScript tests passed, plus the actual-function probes above. Browser tests were inspected, not rerun under the read-only sandbox. Their exact-points assertion genuinely checks stored grid equality for one spectrum; it does not establish rendered background/model identity across every path. The simulated harness proves orchestration, not exact restoration through its stubs.

No files changed.

**VERDICT: GO**
