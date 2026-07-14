# Codex review — "Best fit" tooltip HTML-leak fix — ROUND 1 RUN A (2026-07-14)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/tooltip_markup_leak_review_prompt.txt (commit 2ae4340)

**Finding**

NO-GO: the test payload's claimed backend shape is not realistic for
`decisive_override`. The test injects a winning `A0_graphite_only+bfix` candidate
with a non-null `filter_reason` (tests/test_browser_find_peaks_tooltip_markup.py:137),
but the backend doesn't emit that shape. `_bound_fixed_refit()` renames the promoted
refit to `X+bfix` (autofit/engine.py:2416); `_apply_decisive_override()` appends that
refit to `result.reports` and promotes it into `result.survivors` (2480), but never
appends the `+bfix` report to `filtered_out`. `build_analysis_record()` assigns
`filter_reason: filtered_reason.get(name)` (ic_model_comparison.py:248) — for a
promoted `X+bfix` row, that lookup returns `None`. The real winner-with-filter_reason
path is `no_clean_survivor`, where the same original model name is both in
`filtered_out` and promoted to `survivors` — the test should use that shape.

**Verified**

The frontend fix itself is correctly structured: `statusText` is plain text in all
three branches (Best fit / Alternative / `_fpFilterReasonLabel(...)`); `statusHtml` is
the only variable that receives `<b>...</b>` and is used for the cell body
(templates/index.html:13989). The tooltip is built from `statusText`, not
`statusHtml` (13995) — fixes the double-escape/visible-`<b>` bug for any row with a
truthy `filter_reason`. Swept every `title="` in the Find Peaks section — no other
tooltip source uses a pre-marked-up fragment. Commit 2ae4340 changes
docs/autofit/PROGRESS.md, templates/index.html, and the new browser test only — no
backend Python, `/api/fit`, `/api/analyze`, analysis math, or candidate-selection
logic. Did not run the browser tests (read-only sandbox, no pytest).

VERDICT: NO-GO
