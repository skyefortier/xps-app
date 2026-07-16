# Codex review — self-citation removal — ROUND 2 RECHECK RUN B (2026-07-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/self_citation_removal_recheck_prompt.txt (recheck of
round 1's docstring + stray-file findings, commit c37e902)

**Findings**

1. tests/test_legacy_parity.py:9 still overclaims what test_cutover.py
   proves. `_raw()` is now correctly described as reading
   tests/fixtures/xps_legacy_snapshot.json, but the docstring says
   test_cutover.py "proves the fixture matches what the template used to
   contain." Current test_cutover.py explicitly tests the post-deletion
   state using the fixture as oracle; it cannot currently prove parity
   against deleted historical template literals.
2. .stage9/manifest/manifest.json is a tracked additional exact
   "Fortier 2026" occurrence outside the allowed list in the recheck
   request. Not runtime-loaded (rg only found .stage9 scripts
   reading/generating the manifest) — historical transcription evidence,
   but the disclosure/list was incomplete.

**Verified OK**

test_chem_state_tier.py's tier docstring now reads consistently:
original 52-state transcription, current 51-state tier after the
disclosed removal. UCl4 entry gone from chemical-states.json; U 4f7/2
has 4 states, 11 groups / 51 states total, zero fortier refs.
Independently recomputed both checksums — match. Stray temp file gone
from working tree and git ls-files; templates/ only has index.html and
index.html.pre-audit. Scope clean otherwise: no app.py, xps_reference.py,
autofit/engine.py, autofit/methods, fitting.py, or templates/index.html
changes.

VERDICT: NO-GO
