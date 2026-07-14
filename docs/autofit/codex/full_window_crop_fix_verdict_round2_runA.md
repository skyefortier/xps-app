# Codex review — "fit the entire window" fit-range-crop fix — ROUND 2 RECHECK RUN A (2026-07-14)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/full_window_crop_fix_recheck_prompt.txt (recheck of round 1's
status-bar-reset fix, commit c3fe41f)

**Finding**

High: the full-window apply path still leaves another fit-result DOM surface stale —
the right-side Results panel. The checked path clears `state.fitResult` and manually
clears the status bar, then only calls `renderPeakList()` and `updatePlot()`
(templates/index.html:14107). It never calls `renderResults()`. Since `renderResults()`
clears `#results-area` to "Run the fit to see results" only when `!state.fitResult`
(7031), the existing results panel can keep showing the previous fit's
chi/RMSE/R-factor/table after the state has been invalidated. Concrete scenario: run
a fit, open the results panel, run Find Peaks with "Fit the entire window", apply.
Chart and status bar clear, but `#results-area` remains old DOM until some later
action re-renders it.

**Verified**

Status-bar reset correctly inside `if (_fpLast && _fpLast.fitFullWindow)` (14088), so
unchecked path unaffected. Reset values match `TabManager.activateTab`'s no-fit branch
exactly: `fit-quality.innerHTML = '&#967;&#178; &mdash;'`, `removeAttribute('data-xps-tip')`,
`sb-chi` set to U+2014 em dash. `_updateRFactorUI(null)` clears `#sb-runs` text/tooltip;
`_updateROIDisplay(null)` clears `#sb-roi`. Checked test requires both `#sb-roi` and
`#sb-chi` to change. Minor secondary note: the status-bar snapshot helper only
captures `sb-roi`/`sb-chi`, not `fit-quality`/`sb-runs` — a partial regression there
could still pass. No backend Python or `/api/fit` changes. Could not run tests here
(no pytest in this sandbox).

VERDICT: NO-GO
