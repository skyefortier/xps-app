# Codex review — C 1s VERIFIED-badge fix — ROUND 1 RUN A (2026-07-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/c1s_badge_fix_review_prompt.txt (commit 29e922c)

**Finding**

NO-GO: two tracked Stage-9 provenance artifacts still carry the old C 1s curated
nominal as 284.5. .stage9/manifest/manifest.json's C-1s record still says
current_value: 284.5, current_tier: "curated-hand-verified", current_source:
"nist-srd-20" — build_manifest.py generates that value from the live curated
transition energy, so if retained as current generated evidence it should now
be 284.44. .stage9/reports/phase8_evidence_report.md still reports the C 1s
curated-nominal row as 284.5/284.5 — its generator reads current data/xps
curated values, so it would not be consistent with the new source data if
regenerated.

**Confirmed Good**

The requested six-file diff in 29e922c is otherwise as described: elements-
main.json has nominal_be_ev 284.44 with honest notes; corrections.json,
curated_records_snapshot.json, and fit-physics.json are internally consistent
at 284.44 (both generators re-run in-memory match committed files). The
bridge copies nominal_be_ev and maps curated to VERIFIED; level_reference("C",
"1s") returns 284.44/VERIFIED. templates/index.html remains uncoupled (all
284.5/284.50 hits are local CC/Auto-Fit literals). autofit/regions/c1s.py and
c1s_battery_expected.json have no diff. The browser repaint test edits are
logically correct.

VERDICT: NO-GO
