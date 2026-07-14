# Codex review — "Best fit" tooltip HTML-leak fix — ROUND 3 RECHECK RUN A (2026-07-14)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/tooltip_markup_leak_recheck2_prompt.txt (recheck of round 2's
boundary-hit-format finding, commit 8ce1a7f)

**Findings**

None blocking.

**Verified**

Re-derived `_detect_boundary_hits()` from autofit/engine.py:687: it appends
`f"{role or '?'}:{short}@{'min' if at_min else 'max'}"` (714), so the raw backend
shape is `role:param@min|max`. Payload now uses `main_graphitic:fwhm@max` in both
relevant places (tests/test_browser_find_peaks_tooltip_markup.py:165, 174) — no
`s_..._...@max` frontend-display artifact remains in the executable payload. Rest of
`_NO_CLEAN_SURVIVOR_WINNER_PAYLOAD` matches the backend mechanism: `rank_and_filter()`
puts plausibility-failed stable reports into both `filtered_out` and
`conditional_pool`, then promotes that same object as `survivors` with
`conditional_reason = "no_clean_survivor"` (autofit/engine.py:1637, 1656).
`build_analysis_record()` keys both `filtered_reason` and `survivor_rank` by exact
`model.name` (ic_model_comparison.py:248, 267). The `filter_reason` string matches
`f"plausibility: {r.plausibility}"` with the dataclass field order from
`PlausibilityFlags`. Production fix unchanged: `statusText` plain, `statusHtml` only
place `<b>` applied, tooltip built from `statusText` (templates/index.html:13996,
14003). Checked for lingering transformed boundary-hit strings — none found. Did not
rerun pytest (read-only sandbox).

VERDICT: GO
