# Codex review — "Best fit" tooltip HTML-leak fix — ROUND 2 RECHECK RUN B (2026-07-14)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/tooltip_markup_leak_recheck_prompt.txt (recheck of round 1's
test-payload finding, commit 550cf6d)

**Finding**

`tests/test_browser_find_peaks_tooltip_markup.py:165` still has a backend-shape
realism issue: `winner_boundary_hits` uses `"s_main_graphitic_fwhm@max"`, and the
synthetic `filter_reason` repeats that same value (line 174). The real backend
boundary-hit format from `_detect_boundary_hits()` is `role:param@min|max`, e.g.
`"main_graphitic:fwhm@max"` (autofit/engine.py:687, 714) — a real `filter_reason`
would use that form, not the `s_..._...@max` frontend-display-transformed form used
here.

**Verified**

The main no-clean-survivor trigger is otherwise correctly modeled: `rank_and_filter()`
appends plausibility failures to `filtered_out`, adds stable ones to
`conditional_pool`, then promotes that pool to `survivors` with
`conditional_reason = "no_clean_survivor"` when there are no clean survivors
(autofit/engine.py:1637, 1656). `build_analysis_record()` derives both
`filter_reason` and `survived` by the same exact model name
(ic_model_comparison.py:248, 267). Production fix remains unchanged and correct:
`statusText` plain, `<b>` only in `statusHtml`, cell uses `statusHtml`, tooltip title
built from `statusText` only (templates/index.html:13988). The two other payloads
look plausible. Could not run the focused pytest file here (not installed for the
available Python).

VERDICT: NO-GO (stricter of the two round-2 runs; governs per project standing rule)
