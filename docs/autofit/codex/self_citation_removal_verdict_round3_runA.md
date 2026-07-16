# Codex review — self-citation removal — ROUND 3 RECHECK RUN A (2026-07-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/self_citation_removal_recheck2_prompt.txt (recheck of
round 2's docstring-accuracy findings, commit aad7ebb)

**Finding**

tests/test_chem_state_tier.py:137 still overclaims: "COMPLETE accounting
of every remaining `Fortier` occurrence in the tracked repo." A literal
`git grep -n "Fortier"` finds the three intended .stage9 historical
files, but also unrelated tracked docs outside the named exemptions,
including docs/autofit/WORKING-PLAN-peak-fit-feature.md,
docs/autofit/phase1-grammar-architecture-spec-v2.md, and several
docs/superpowers/plans/*.md files with ordinary "Fortier Lab" mentions.
These aren't the same citation bug, but the docstring's absolute claim
("every remaining Fortier occurrence") is not literally true. Cleaner
wording would scope it to the literal self-citation string or the audit
target specifically.

**Verified**

test_legacy_parity.py now correctly distinguishes historical fixture
creation from current live assertions. git grep "Fortier 2026" shows the
three .stage9 historical files plus fix-discussion/curator text.
chemical-states.json has 11 groups / 51 states, no Fortier refs. No
runtime path in app.py, xps_reference.py, autofit/, or fitting.py reads
the three .stage9 files by name. aad7ebb itself only touched
tests/test_chem_state_tier.py and tests/test_legacy_parity.py.

VERDICT: NO-GO
