# Codex review — C 1s VERIFIED-badge fix — ROUND 5 RECHECK RUN B (2026-07-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/c1s_badge_fix_recheck4_prompt.txt (recheck of round 4's
reference-identify-workspace.md stale count, commit c29652f)

**Findings**

1. docs/superpowers/plans/2026-06-19-reference-identify-workspace.md:1025
   still has an unqualified stale count: "compounds in Identify, all 52,
   tier-capped, no evidence filter." Current disk state is 11/51. Lines 11,
   110, 117 in the same plan are now qualified correctly; this fourth
   location was missed.
2. docs/mockups/reference-identify-mockup.html:388 still implies C 1s's
   reference-line value is 284.5 eV under curated/NIST presentation:
   tierOf(C) falls through to curated, the curated tier is described as
   checked against NIST/papers, the C line is 284.5 eV, and the rendered
   card shows the curated badge/source footer. The separate "Graphite
   charge reference 284.5 eV" note is legitimate, but the element line
   itself is still presented as the curated reference line.

**Other Checks**

Live data path correct: elements-main.json, legacy/corrections.json,
fit-physics.json, curated_records_snapshot.json, manifest.json,
phase8_evidence_report.md all show C-1s curated/reference value as 284.44
where relevant. Remaining 284.5 hits are legacy chemical-state rows, frozen
extraction inputs, CC code, fit outputs, or explanatory prose distinguishing
convention from verified value. Scope: c29652f changes only the plan doc; no
forbidden runtime-path changes.

VERDICT: NO-GO
