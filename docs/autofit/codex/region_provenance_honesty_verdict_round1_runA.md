# Codex review — region-module provenance honesty (Units 4-5) — ROUND 1 RUN A (2026-07-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/region_provenance_honesty_review_prompt.txt (commit e8bf31c)

**Finding**

NO-GO: there are still fit-active constants in c1s.py/u4f.py with explicit
comment provenance/disclosure absent, or not concretely represented, in
provenance(). ASYMGL_ASYMMETRY_RANGE (0.0, 0.5) — used in candidate slots;
provenance() only has a generic 'asymgl_family' string, not the numeric
bound. SATELLITE_OFFSET_RANGE (5.5, 7.0) — UNVERIFIED tunable, used as
linked_offset_range, no provenance entry. U4F_LACX_M_RANGE (0.0, 100.0) —
labeled-set disclosure, used in LACX param_ranges, but provenance() lists
alpha/beta only. U4F_SAT_FWHM_RANGE (1.5, 4.5) — UNVERIFIED-empirical
labeled-set comment, used by satellite slots, absent from provenance.

**Checks Passed**

The requested C1s contamination split is clean (floor 0.8/CONDITIONAL
literature-only; ceiling 2.0/UNVERIFIED lab-adjudication-only; old combined
key gone). FWHM_RANGE_CONTAMINATION unchanged; commit e8bf31c changes only
C1sModule.provenance() plus the test file. U4f satellite_offset_ev source
already distinguishes lit 6.8-7.1 from labeled set 6.07-6.38; no change
needed. The two Unit-5 additions match constants/comments. The four new
tests call the real provenance() methods; three C1s tests would fail
against the parent, the U4f test would pass.

VERDICT: NO-GO
