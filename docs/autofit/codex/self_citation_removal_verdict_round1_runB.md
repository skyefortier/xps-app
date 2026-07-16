# Codex review — self-citation removal — ROUND 1 RUN B (2026-07-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/self_citation_removal_review_prompt.txt (commit e7b32f5)

**Findings**

None blocking (GO).

**Non-blocking notes**

- tests/test_chem_state_tier.py:24 still says "The tier therefore stays
  at 11 groups / 52 states" before the new disclosed-deviation paragraph
  says it's now 51 — docstring cleanup only, assertions themselves are
  correct.
- A broader grep found historical/stale copies outside runtime,
  including .stage9/manifest/manifest.json and a tracked temp file
  templates/index.html.tmp.19861.1774892271848 — the live app renders
  templates/index.html only, so this doesn't affect runtime behavior,
  but the tracked temp file may confuse future provenance grep audits.

**Verified**

U 4f7/2 group has 4 states with correct ids/BE/refs, no Fortier ref
anywhere. Independently recomputed chemical `content_sha256` and fixture
`sha256` — both match. curated_records_snapshot.json embedded legacy
payload also has 51 total states and the same 4-state U group. Grepping
tests/ for "52" found no remaining chemical-state count assertions at
52. test_no_self_citation_in_any_ref_string reads the correct live file
and would have caught the original bug. git show --name-status e7b32f5
shows only the five intended changed files — no app.py, autofit/
engine.py, autofit/methods/*, fitting.py, or live templates/index.html
changes. The parity-test reframing (disclose the deviation rather than
break parity) is the right call.

VERDICT: GO
