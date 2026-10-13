Reviewed `b804968..41f3496`, focusing on round 3 (`b27f366..41f3496`). **No BLOCKER or MAJOR found. One MINOR remains.**

**MINOR — Confirmation ignores unmatched components on the measured side.**  
[q8_confirm.py:23](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/scripts/q8_confirm.py:23) now assigns components one-to-one, but checks unmatched components only in `a`. An extra component in `b` can go unreported. Reproduced: adding a zero-amplitude measured component yields `max_dpp = 0`; reversing the comparison yields infinity. Check unmatched components on both sides. **Non-physical inputs: no.** All 50 committed comparisons have equal component counts, so this does **not** invalidate the current confirmation.

Review conclusions:

- **Round 2 history defects are fixed.** Probes using the actual functions confirmed that Undo/Redo restore the previous/final result arrays, correction and ID counter. A pending slider edit survives rollback and remains undoable. Keyboard Cancel now receives focus and permits activation.
- **Final-fit construction is consistent by inspection.** Both Δ branches reach the second fit. It rereads shifted points, re-rounded ROI/background bounds and migrated manual anchors, retaining bounds overlays, amplitude floor, method, three perturbations and `require_component`. Auto-Fit builds GL/asym-GL, not LA/DS+G. Backend handling preserves locked centres even outside retained bounds.
- **The anchor request matches main.** Extracted request-builder probes matched across none, linear, Shirley, Tougaard and manual backgrounds. The anchor ID is captured before upload; both responses use the same gates, and only the first response derives the shift.
- **Transaction paths look sound.** Ordinary pointer/keyboard interactions and save/export entry points are blocked while busy. Both uploads receive the timeout/cancellation signal. Owned failures restore the snapshot and history; superseded responses skip publication and rollback. Successful publication makes one undo entry and one history snapshot.
- **Measurements check out.** `summary.json` and `confirm.json` reproduce exactly; the B4C table matches its files. Confirmation remains **49 close comparisons, one 11.516 pp outlier and three acceptance mismatches**. The **16 + 2 = 18 of 51** R count and student-note area, χ²ᵣ and timing numbers agree with the measurements.
- **Tests have limits.** The simulated harness proves orchestration through stubs. Browser tests now inspect real rollback/history state, including result arrays and `nextId`; the exact-points test proves stored energy-array identity for its case, not every rendered curve or background path.
- Q5 remains measurement-only; no unrelated production change found.

**Validation:** 163 targeted JavaScript tests passed, plus the actual-function probes and measurement recalculations. Browser/server tests were inspected, not rerun under the read-only sandbox. No files changed.

**VERDICT: GO**
