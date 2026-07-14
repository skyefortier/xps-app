# Codex review — "Best fit" tooltip HTML-leak fix — ROUND 3 RECHECK RUN B (2026-07-14)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/tooltip_markup_leak_recheck2_prompt.txt (recheck of round 2's
boundary-hit-format finding, commit 8ce1a7f)

**Findings**

None blocking.

**Verified**

`_detect_boundary_hits()` emits `f"{role or '?'}:{short}@{'min' if at_min else 'max'}"`
(autofit/engine.py:714) — current payload's `main_graphitic:fwhm@max` in both
`winner_boundary_hits` and the `PlausibilityFlags(...)` repr matches the backend
format exactly; no `s_...` prefix or frontend underscore-transformed form remains.
The no-clean-survivor shape is realistic: `rank_and_filter()` appends
plausibility-failed stable reports to both `filtered_out` and later `survivors` when
no clean survivor exists (autofit/engine.py:1637, 1656); `build_analysis_record()`
keys `filter_reason` and `survived` by the same exact `model.name`
(ic_model_comparison.py:248, 267). Payload's `winner`, candidate `name`,
`conditional_reason`, empty `winner_boundary_fixed_params`, and PlausibilityFlags
field order all line up with the backend. Production renderer remains correctly
split: `statusText` plain, `statusHtml` only place `<b>` applied, cell HTML uses
`statusHtml`, tooltip title built from `statusText` only (templates/index.html:13996,
14003). Re-swept Find Peaks `title` sites — no other HTML-fragment-as-tooltip
instance. Did not rerun tests (read-only sandbox).

VERDICT: GO
