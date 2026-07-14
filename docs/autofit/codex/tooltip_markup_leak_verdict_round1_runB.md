# Codex review — "Best fit" tooltip HTML-leak fix — ROUND 1 RUN B (2026-07-14)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/tooltip_markup_leak_review_prompt.txt (commit 2ae4340)

**Finding**

NO-GO: the new test's claimed backend shape is not realistic for
`decisive_override +bfix`. The synthetic payload says a `decisive_override` winner
named `A0_graphite_only+bfix` carries a truthy `filter_reason`
(tests/test_browser_find_peaks_tooltip_markup.py:132), but the backend doesn't emit
that shape: `_bound_fixed_refit()` renames the promoted report to `original+bfix`
(autofit/engine.py:2416), `_apply_decisive_override()` appends that refit and makes it
the survivor (2480), but `build_analysis_record()` assigns `filter_reason` by exact
candidate name from `result.filtered_out` (ic_model_comparison.py:248, 269). The
filtered row is `X`; the promoted survivor is `X+bfix`, so the real `+bfix` row gets
`filter_reason: null`. The real winner-with-filter_reason path is `no_clean_survivor`,
where `rank_and_filter()` promotes the same plausibility-filtered report names into
survivors.

**Verified**

The frontend fix is correct (templates/index.html:13988): `statusText` plain text for
all three branches, `statusHtml` the only value receiving `<b>...</b>`, cell content
uses `statusHtml`. Tooltip title (13995) built only from `statusText`. Swept `title="`
occurrences in the Find Peaks block — no other partially pre-marked-up tooltip
source found; other titles come from literals or plain escaped sources. Display-only
frontend change: no backend Python, `/api/fit`, math, or candidate-selection code
changed. Could not run tests (no pytest in this environment).

VERDICT: NO-GO
