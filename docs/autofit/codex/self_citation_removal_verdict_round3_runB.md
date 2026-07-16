# Codex review — self-citation removal — ROUND 3 RECHECK RUN B (2026-07-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/self_citation_removal_recheck2_prompt.txt (recheck of
round 2's docstring-accuracy findings, commit aad7ebb)

**Finding**

tests/test_chem_state_tier.py:137 still overclaims: says the docstring
is a "COMPLETE accounting of every remaining `Fortier` occurrence in the
tracked repo" — not literally true. git grep -n "Fortier" also returns
unlisted non-test/non-fixture files: docs/autofit/WORKING-PLAN-peak-
fit-feature.md, docs/autofit/phase1-grammar-architecture-spec-v2.md, and
several docs/superpowers/plans/*.md files. For the narrower literal
string "Fortier 2026" specifically, the three .stage9 files named are
the expected retained historical files, aside from review-prompt/test/
fixture discussion and the C 1s curator-attribution files — the problem
is the wording says every "Fortier" occurrence, not every retained
"Fortier 2026" self-citation occurrence in the audited provenance scope.

Recommended wording fix: scope the docstring to the literal "Fortier
2026" self-citation/provenance-scope occurrences, not every bare
"Fortier" occurrence in the tracked repo.

**Verified**

Corrected test_legacy_parity.py wording now scopes fixture-vs-original-
constants as a one-time historical claim; `_raw()`'s comment correctly
says the current live assertion is legacy JSON == frozen fixture, not
fixture == deleted historical constants. The three retained .stage9
files are not referenced by name from app.py, xps_reference.py,
autofit/, or fitting.py. Scope for aad7ebb: only the two named test
files changed.

VERDICT: NO-GO
