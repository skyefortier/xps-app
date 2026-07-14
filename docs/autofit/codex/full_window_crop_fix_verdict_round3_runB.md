# Codex review — "fit the entire window" fit-range-crop fix — ROUND 3 RECHECK RUN B (2026-07-14)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/full_window_crop_fix_recheck2_prompt.txt (recheck of round 2's
Results-panel fix, commit 550cf6d)

**Finding**

`renderResults()` (templates/index.html:7033) clears `#results-area` when
`state.fitResult` is null, then immediately returns, leaving `#quantify-area`
untouched even though the non-null path later calls `renderQuantify()` (7117).
Concrete stale-DOM scenario: run a real fit so Quantify is populated, switch to
Quantify, then run Find Peaks with "Fit the entire window" checked and Apply.
`applyFindPeaks()` nulls `state.fitResult` and calls `renderResults()` inside the
checked branch (14114), but only `#results-area` resets — the Quantify panel keeps
showing the old fit's area/RSF/At% table instead of "Run fit to quantify."
(2202). Switching back to Quantify doesn't fix it either, since `switchRightTab()`
calls `renderResults()` for `quantify` (9941) via the same null-return path.

**Verified**

New browser assertions well-targeted for the round-2 Results-panel bug (would fail
without `renderResults()`); they just don't cover the Quantify stale surface.
`renderResults()` handles `state.fitResult === null` cleanly for `#results-area`; the
synthetic test fixture without `backendResult` is safe (`_buildStderrMap()` uses
optional chaining). No backend Python, `/api/fit`, peak position/width/chemical-anchor
changes. Commit 550cf6d also includes an unrelated tooltip test change (Unit 3), so
"only templates plus this test file" isn't strictly true at the commit level — noted,
not blocking. Could not run pytest here (read-only sandbox).

VERDICT: NO-GO
