# Codex review — "fit the entire window" fit-range-crop fix — ROUND 4 RECHECK RUN B (2026-07-14)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/full_window_crop_fix_recheck3_prompt.txt (recheck of round 3's
Quantify-panel fix, commit 8ce1a7f)

**Findings**

None blocking.

**Verified**

`renderResults()` resets Quantify inside the existing `if (!state.fitResult)` branch,
before the `return` (templates/index.html:7033). Placeholder string matches the
static initial `#quantify-area` markup exactly (2202, 7041). Full-window apply path
clears `state.fitResult`, resets status DOM, calls `renderResults()`, then
`renderPeakList()`/`updatePlot()` (14096). Browser test now snapshots `quantifyArea`
and asserts the stale content is replaced with the no-fit placeholder (173, 275, 304).
No other current-fit visible DOM surface missed: Survey doesn't consume
`state.fitResult`; Auto-Fit menu enablement is C1s/ROI based; export/download compute
on demand; history entries are saved snapshots. Active-tab persistence covered since
later tab switches call `_syncActiveToRecord()`, writing the cleared `state.fitResult`
back (3632). Scope: neither 8ce1a7f nor the crop-fix range since e0d3185 touches
`autofit/engine.py`, `autofit/methods/*.py`, or `fitting.py` — `test_u4f_n1s_cofit`'s
failure is unrelated to this UI fix. Could not run pytest (read-only sandbox).

VERDICT: GO
