# Codex review — "fit the entire window" fit-range-crop fix — ROUND 1 RUN A (2026-07-13)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/full_window_crop_fix_review_prompt.txt (commit e0d3185)

**Finding**

High: the fix clears `state.fitResult`, but leaves the old fit status UI intact.
In `applyFindPeaks()` (templates/index.html:14078), `state.fitResult = null` is
set before `updatePlot()`, fixing the chart render path — but `_updateROIDisplay(null)`,
`_updateRFactorUI(null)`, and the `fit-quality`/`sb-chi` DOM fields are never reset.
Concrete scenario: prior fit has `roiRange: 278.0-290.4`; user checks "Fit the entire
window", applies. Background/fit dataset now spans the wider ROI, but the header/status
can still show the old `ROI: 278.0-290.4 eV` and old chi/R values — the exact
bug-report symptom, uncaught by the new tests.

**Verified**

`fitFullWindow` captured from the same `options` object sent in the request body
(templates/index.html:13823, 13841, 13876). Clear correctly ordered after
`state.peaks = ...` and before `renderPeakList()`/`updatePlot()` (14055).
`getROIData()` reads live `#roi-min`/`#roi-max`, same fields used for the analyze
request (4637). `updatePlot()`'s `haveFit` check false when `state.fitResult === null`,
correctly falls back to `getROIData()` + `computeBackground()` (7885). No backend
Python/`/api/fit` touched. Provenance stamp (`autoSuggested`/`verified`) and toast
unchanged. Could not run browser tests in this read-only sandbox (no pytest); by trace,
the checked test deterministically catches the pre-fix chart-crop bug.

VERDICT: NO-GO
