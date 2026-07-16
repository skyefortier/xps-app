# Stage 9 Phase 7 — Parity gate + allowlist (for Checkpoint B review)

The cutover deletes the `XPS_ELEMENTS` / `CHEMICAL_STATES` JS constants; the
unified accessor then serves the verbatim legacy JSON instead. This gate
asserts the cutover preserves behavior, with an explicit allowlist of the
ONE intended change.

## What the parity gate asserts (all GREEN — 38 tests pass)

1. **Legacy JSON reconstructs the constants EXACTLY.**
   `tests/test_legacy_parity.py` rebuilds `XPS_ELEMENTS` and `CHEMICAL_STATES`
   from `data/xps/legacy/*.json` and asserts byte-equality against the live
   constants extracted from the template (53 elements / 62 lines / 11 groups /
   52 states at Checkpoint B time; 51 states after the 2026-07-16 provenance-
   audit removal below). Auger KLL kept as legacy BE markers (not converted).

2. **The real JS accessor deep-equals the constants.**
   `tests/test_legacy_hardening.py::test_js_accessor_functions_deep_equal_constants`
   renders the page and runs the actual `_accSurveyElements()` /
   `_accChemicalStates()` against the injected `LEGACY_REFERENCE`, asserting
   deep parity with the retained constants. So after deletion the accessor
   serves identical values.

3. **Tamper-evidence + uniqueness + axis convention** are locked
   (`content_sha256` checksum, symbol/orbital_key uniqueness, survey markers
   draw at `be` not `be+ccShift`).

## Allowlist — intended changes (everything NOT on this list must be parity)

- **A1. be+ccShift marker fix.** Survey reference markers now draw at the
  reference `be` directly on the corrected-BE axis, not `be+ccShift`. This is
  the documented legacy bug fix (CLAUDE.md). It changes marker PIXEL position
  only when a charge correction is active; the reference VALUES are unchanged.
  Locked by `test_survey_marker_axis_convention_locked`.

## Explicitly NOT changed at cutover (no value drift)

- **Legacy reference VALUES are unchanged.** The extraction/tiering (Phase 4–6)
  produces *advisory metadata* (which legacy values are corroborated, which
  conflict). It does **not** rewrite the legacy JSON, which stays verbatim for
  parity. The accessor serves the same legacy numbers it always did.

- **The 8 survey conflicts are FLAGGED, not applied.** Ti/V/Cr/Fe/P 2p (oxide-
  positioned) and Na/Mg KLL (KE-frame) and U 5d disagree with corroborated
  NIST values, and carry a resolution (`elemental-nominal-with-oxidation-range`
  / `auger-ke-frame`). That resolution is recorded as guidance for a future
  re-curation step — it is **not** auto-written into the served data. So the
  cutover does not move these markers; the conflict is documented, not erased.

- **The 6 curated NIST elements (C, O, Cl, Cu, Nb, U) remain ADDED, separate
  observations.** They live in `data/xps/elements-*.json` and feed the new
  Reference-Lines overlay. They do **not** replace legacy survey values:
  e.g. U 4f legacy 380 and the curated/extracted metal nominal 377.3 are both
  preserved as distinct observations — there is no 380→377.3 replacement.

## Behavioral-diff result

Accessor-vs-constants deep parity is proven by the committed JS accessor test
(#2 above) — i.e. the before/after of every survey marker and NIST-modal row
is identical except the allowlisted be+ccShift fix. No masked regression: the
only delta is A1.

## Tier adjudication summary (advisory metadata, all 113 legacy quantitative fields)

| | survey (62) | chem (51) |
|---|---|---|
| transcription-corroborated | 49 | 30 |
| conflict (resolved, flagged) | 8 | 0 |
| single-source | 0 | 2 |
| context-unconfirmed | 0 | 5 |
| insufficient-evidence (stay legacy-unverified) | 5 | 14 |

`machine-source-corroborated` is **not** claimed anywhere (both passes read
the same source, NIST). Unresolved values stay flagged indefinitely.

POST-CHECKPOINT UPDATE (2026-07-16, provenance audit): the U 4f7/2 UCl₄
chemical-state entry (id legacy-cs-U-4f72-4, transcription-corroborated
tier) was removed — its `ref` field was the literal self-citation "Fortier
2026", not an external literature source (see
tests/test_chem_state_tier.py::test_no_self_citation_in_any_ref_string).
This is the ONE change to the chem counts since the original Checkpoint B
review (52→51 states, transcription-corroborated 31→30); every other
number and qualitative claim in this document is unchanged from Checkpoint
B and remains accurate.
