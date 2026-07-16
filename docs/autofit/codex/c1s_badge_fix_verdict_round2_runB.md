# Codex review — C 1s VERIFIED-badge fix — ROUND 2 RECHECK RUN B (2026-07-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/c1s_badge_fix_recheck_prompt.txt (recheck of round 1's
stale Stage-9 reports, commit 90276aa)

**Finding**

NO-GO: a third stale derived Stage-9 artifact. .stage9/manifest/tiers_chem.json
still contains the deleted UCl4 chemical-state row (legacy_be: 380.2) and
still has 52 rows while regenerated manifest.json has 51 legacy chemical-
state fields. Running .stage9/phase5_tier_chem.py in-memory from the current
manifest produces 51 rows, removes UCl4, and shifts downstream field IDs —
proving tiers_chem.json is stale derived output. The evidence report is
therefore only byte-identical to gen_evidence_report.py WITH stale upstream
input: it still says "114 legacy quantitative fields", "chem (52)", and
"transcription-corroborated | 49 | 31" (would become 30 with regenerated
tiers_chem.json). The generator also hardcodes "114"/"chem (52)" literally,
so that header needs code attention, not just data regeneration.

**Verified Good**

C 1s itself is fixed in the two named artifacts (284.44 in both). git grep no
longer returns manifest.json for "Fortier 2026". Scope checks pass: commit
90276aa changes only the three named files; no diff in autofit/engine.py,
autofit/methods, fitting.py, app.py, or templates/index.html.

VERDICT: NO-GO
