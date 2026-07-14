# Codex review — "fit the entire window" fit-range-crop fix — ROUND 3 RECHECK RUN A (2026-07-14)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/full_window_crop_fix_recheck2_prompt.txt (recheck of round 2's
Results-panel fix, commit 550cf6d)

**Finding**

NO-GO: `#quantify-area` is still a stale DOM surface after `state.fitResult` is
cleared. `renderResults()` (templates/index.html:7033) handles `!state.fitResult` by
updating only `#results-area` and returning — it never clears `#quantify-area`; the
normal quantify refresh only happens later via `renderQuantify()` (7117), reached
only on the non-null path. Concrete scenario: run a fit, render Quantify so it's
populated, then run Find Peaks with "Fit the entire window" checked and apply.
`applyFindPeaks()` clears `state.fitResult` and calls `renderResults()` (14088), but
that returns after resetting only Results. Switching to Quantify calls
`renderResults()` again (9941), which still returns before clearing Quantify. The old
quantification table remains visible.

**Verified**

`renderResults();` correctly inside `if (_fpLast && _fpLast.fitFullWindow)` (14088),
not unconditional. `renderResults()` cleanly handles `state.fitResult === null` for
`#results-area` (7033). Synthetic test fit without `backendResult` and with empty
`state.peaks` is safe: `_buildStderrMap()` optional-chains `backendResult`,
`_renderRFactorPanel()` returns empty for missing R-factor, empty peaks produce empty
area/table loops. Extended test would catch the round-2 Results-panel bug (setup
populates stale content, checked test requires "Run the fit" in `resultsArea` after
apply). No backend Python or `/api/fit` path changes. Could not run pytest here (not
installed in this sandbox).

VERDICT: NO-GO
