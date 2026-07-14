# Codex review — "fit the entire window" fit-range-crop fix — ROUND 1 RUN B (2026-07-13)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/full_window_crop_fix_review_prompt.txt (commit e0d3185)

**Finding**

NO-GO: the chart range is fixed, but the reported status-bar symptom can remain
stale after Apply. `applyFindPeaks()` (templates/index.html:14070) clears
`state.fitResult`, then only calls `renderPeakList(); updatePlot(); closeFindPeaksModal();
notify(...)` — it never clears/updates `#sb-roi`, `#sb-chi`, `#sb-runs`, `#fit-quality`,
or the results panel. Concrete scenario: prior manual fit sets status ROI to
`278.0-290.4` (templates/index.html:6973); Find Peaks with `fit_full_window=true`
applies and clears `state.fitResult`; chart now uses the live 278-298 ROI, but the
status bar can still display the old `ROI: 278.0-290.4 eV` until some unrelated
later action refreshes those widgets. Exact bug-report symptom, unasserted by the
new tests.

**Verified**

`fitFullWindow` captured from the same local `options` object assigned into the
analyze request payload (13817, 13828, 13868). Clearing ordered correctly relative
to `state.peaks`/provenance and `updatePlot()` (14047, 14070). `getROIData()` reads
live `#roi-min`/`#roi-max`, same fields used for the request ROI (4637, 13830) — the
modal overlay blocks pointer access to those inputs between run and apply, so no
race. `updatePlot()`'s `haveFit` check false when `state.fitResult === null`, uses
`getROIData()` + `computeBackground()` + `evalAllPeaks()` over the live ROI (7885).
No backend Python changed. Could not run tests in this sandbox (no pytest); by
trace, the tests deterministically catch the chart-dataset pre-fix bug but not the
stale status-bar issue above.

VERDICT: NO-GO
