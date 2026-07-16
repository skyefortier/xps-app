# Codex review — C 1s VERIFIED-badge fix — ROUND 5 RECHECK RUN A (2026-07-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/c1s_badge_fix_recheck4_prompt.txt (recheck of round 4's
reference-identify-workspace.md stale count, commit c29652f)

**Findings**

1. docs/superpowers/plans/2026-06-19-reference-identify-workspace.md:1025
   still has a stale count: "compounds in Identify, all 52". This is in the
   completed Self-Review/spec-coverage section and lacks the "52 at
   authoring, now 51" qualifier added at lines 11, 110, 117.
2. docs/mockups/reference-identify-mockup.html:388 still implies C 1s 284.5
   is a curated/NIST-style elemental reference in a tracked mockup:
   tierOf('C') defaults to curated, the curated tooltip says "Checked by
   hand against NIST or published papers", the C card renders a curated
   badge, and the C line is "284.5 eV" with "source: NIST SRD 20" rendered
   on the card. Matches the stale C 1s VERIFIED-badge class this fix
   eliminates.

**Verified**

The three edited locations in the plan (lines 11, 110, 117) are accurate.
Live curated C-1s artifacts consistent at 284.44: elements-main.json,
corrections.json, fit-physics.json, curated_records_snapshot.json,
manifest.json, phase8_evidence_report.md. Remaining 284.5 hits in
templates/index.html, CLAUDE.md, C1s fitting docs/tests, and legacy
chemical-state records are CC/fitted-peak/legacy contexts. Scope: c29652f
changes only the plan doc; no forbidden runtime-path changes across
29e922c^..c29652f.

VERDICT: NO-GO
