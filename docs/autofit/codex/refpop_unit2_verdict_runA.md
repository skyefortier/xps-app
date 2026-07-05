# Codex review — Unit R2 exhaustion certification (commit 324b793) — RUN A (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 160,820.
Prompt: docs/autofit/codex/refpop_unit2_exhaustion_prompt.txt

1. BLOCKER [scripts/acquire_nist_archive.py](/Users/skyefortier/xps-app/scripts/acquire_nist_archive.py:91): `cdx_snapshots()` still converts any CDX/network/JSON failure into `[]`, and `acquire()` then records that as “no archive snapshot.” Concrete failure: Wayback CDX times out for `F` during the 2026-07-05 re-probe; the manifest gets a fresh `fetch_utc` and `no archive snapshot`, `summarize_acquisition.py` classifies it as `no-archive-snapshot`, and the R2 tests pass. The re-probe proves retry execution, not successful CDX absence.

2. MAJOR [scripts/acquire_nist_archive.py](/Users/skyefortier/xps-app/scripts/acquire_nist_archive.py:89): the no-starred class is not archive-exhaustive. CDX is capped at `limit=12`, and [the loop returns after the first usable artifact](/Users/skyefortier/xps-app/scripts/acquire_nist_archive.py:139), even if that artifact has no starred lines. Concrete failure: an early `V`/`Li`/`O` snapshot has no star, but a later archived `.asp` snapshot does; the pipeline records `artifact-has-no-starred-value` and never checks the later snapshot.

3. MAJOR [tests/test_coverage_exhaustion.py](/Users/skyefortier/xps-app/tests/test_coverage_exhaustion.py:90): `test_every_machine_element_is_manifest_ok` does not actually require every machine element to be in the manifest; missing entries are silently ignored. Concrete failure: a hand-edited machine element with plausible provenance but no manifest row can pass this R2 certification if counts are preserved and it is not in the dark set.

VERDICT: NO-GO
