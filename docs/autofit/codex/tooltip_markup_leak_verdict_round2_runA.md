# Codex review — "Best fit" tooltip HTML-leak fix — ROUND 2 RECHECK RUN A (2026-07-14)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/tooltip_markup_leak_recheck_prompt.txt (recheck of round 1's
test-payload finding, commit 550cf6d)

**Findings**

None.

**Verified**

Re-derived the payload shape from current code: `rank_and_filter()` records
plausibility failures in `filtered_out`, also puts stable ones into `conditional_pool`,
then promotes that same object list to `survivors` when there are no clean survivors,
with `conditional_reason = "no_clean_survivor"` (autofit/engine.py:1637, 1656).
`build_analysis_record()` keys both `filtered_reason` and `survivor_rank` by exact
`model.name`, so the same `"A0_graphite_only"` candidate can be both `survived: True`
and have a truthy `filter_reason` (ic_model_comparison.py:248, 267). The current
`_NO_CLEAN_SURVIVOR_WINNER_PAYLOAD` matches that shape
(tests/test_browser_find_peaks_tooltip_markup.py:158). `winner_boundary_hits`
non-empty is consistent (one valid plausibility-violation path into the conditional
pool; `unphysical_widths`/`orphan_peaks` also qualify). Decisive-override
impossibility reconfirmed (engine.py:2416, 2480). Production fix intact: `statusText`
plain, `statusHtml` only place `<b>` applied, tooltip built from `statusText`
(templates/index.html:13989). Swept `title=` occurrences again — no other same-class
leak. The other two test payloads remain plausible. Could not rerun tests (no pytest
here).

VERDICT: GO
