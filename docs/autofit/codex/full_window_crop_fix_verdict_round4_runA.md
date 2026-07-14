# Codex review — "fit the entire window" fit-range-crop fix — ROUND 4 RECHECK RUN A (2026-07-14)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/full_window_crop_fix_recheck3_prompt.txt (recheck of round 3's
Quantify-panel fix, commit 8ce1a7f)

**Findings**

None blocking.

**Verified**

Quantify reset is inside `renderResults()`'s existing `if (!state.fitResult)` branch,
before the `return` (templates/index.html:7031). Inserted `#quantify-area` placeholder
string matches the static initial Quantify markup exactly (2201). The full-window
Apply path is now covered end to end: `applyFindPeaks()` clears `state.fitResult`,
resets status widgets, calls `renderResults()`, then redraws peak list and plot
(14096). Grepped remaining `state.fitResult` readers — no other persistent visible DOM
surface found outside `renderPeakList()`, `updatePlot()`, `renderResults()`/Quantify,
or the status reset; Survey, export/download, history preview, and Auto-Fit menu
state don't create another stale surface. Scope: the crop-fix range doesn't touch
`autofit/engine.py`, `autofit/methods/*.py`, `fitting.py`, `/api/fit`, peak math,
widths, positions, or chemical anchors (commit 8ce1a7f also changes
tests/test_browser_find_peaks_tooltip_markup.py for the separate Unit 3 test-format
correction — test-only, unrelated). `test_u4f_n1s_cofit`'s pre-existing failure is
consistent with being unrelated (this fix range touches no autofit/fitting math
files). Could not rerun pytest here (not installed for the available Python).

VERDICT: GO
