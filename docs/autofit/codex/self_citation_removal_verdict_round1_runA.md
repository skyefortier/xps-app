# Codex review — self-citation removal — ROUND 1 RUN A (2026-07-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/self_citation_removal_review_prompt.txt (commit e7b32f5)

**Findings**

1. tests/test_chem_state_tier.py:8,24 still says "the existing
   11-group/52-state tier" / "The tier therefore stays at 11 groups / 52
   states" directly contradicting the new 51-state assertions and
   disclosed-deviation paragraph right below. A future reader could
   believe 52 remains the intended invariant.
2. tests/test_legacy_parity.py:7,30 still says expected values are
   extracted "directly from templates/index.html by evaling the real JS
   literals," but `_raw()` reads tests/fixtures/xps_legacy_snapshot.json.
   Also claims the fixture was "mechanically verified equal to the
   original constants" and proves JSON equals "frozen original values" —
   no longer literally true after the disclosed manual deletion.

**Verified**

Data edit correct: U 4f7/2 has only 4 states (U metal, UO2, U3O8, UO3),
no Fortier ref remains anywhere in chemical-states.json. Independently
recomputed both the chemical-state checksum (_canon_chem shape) and the
fixture self-check hash — both match committed values. New
test_no_self_citation_in_any_ref_string is correctly targeted and
non-vacuous. Scope for e7b32f5: only the 5 expected files changed, no
app.py/xps_reference.py/autofit/fitting.py/templates/index.html changes.

VERDICT: NO-GO
