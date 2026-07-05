# Codex re-check — Unit R2 dispositions — RUN A (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 157,293.
Prompt: docs/autofit/codex/refpop_unit2_recheck_prompt.txt

Finding 1: CLOSED. `cdx_snapshots()` now returns `(snapshots, error)` and CDX failures classify as `cdx-query-failed-UNPROVEN`; the committed pin would fail on that class via `reasons <= {...}` in [tests/test_coverage_exhaustion.py](/Users/skyefortier/xps-app/tests/test_coverage_exhaustion.py:43). Current summary regenerates exactly and has `24 no-archive-snapshot`, `26 artifact-has-no-starred-value`, zero unproven rows.

Finding 2: CLOSED for first-artifact exhaustion, but see new finding. `acquire()` now iterates the returned snapshot list and only promotes the decision artifact. Lu is recovered end-to-end: [elements-machine.json](/Users/skyefortier/xps-app/data/xps/elements-machine.json:1707) has `Lu-4f7/2 = 7.19`; provenance has `evaluated: true`, `agent_cross_checked: true`, and sha `8bbf8fc2...b680` at [elements-machine.provenance.json](/Users/skyefortier/xps-app/data/xps/elements-machine.provenance.json:898). The on-disk `.stage9/expand_artifacts/Lu_nist.html` sha matches, and a fresh parser run found 12 PE lines with exactly one starred PE line: `4f7/2 7.19 Powe95`.

Finding 3: CLOSED. [tests/test_coverage_exhaustion.py](/Users/skyefortier/xps-app/tests/test_coverage_exhaustion.py:95) now asserts every machine element has a manifest row and `status == OK`; a missing manifest row must fail.

New finding: MAJOR [scripts/acquire_nist_archive.py](/Users/skyefortier/xps-app/scripts/acquire_nist_archive.py:94): CDX is hard-capped at `limit=12`, but failed rows are recorded as “ANY archived snapshot” at [scripts/acquire_nist_archive.py](/Users/skyefortier/xps-app/scripts/acquire_nist_archive.py:190) and the committed certificate says no starred line in “ANY listed snapshot” without recording whether the cap was non-binding. Concrete scenario: an element has a starred ASP snapshot at CDX result 13; the pipeline checks the first 12, records `artifact-has-no-starred-value`, and the current count pin still passes. Fix by removing/raising the cap with pagination, or record CDX total/cap status and caveat the certificate so capped rows are not treated as proven exhaustion.

Other checks: targeted pytest pins passed with capture disabled: `9 passed`. Data drift from pre-fix commit is exactly one new machine/provenance/fit-physics transition: `Lu-4f7/2`; no existing machine/provenance/fit entries mutated.

VERDICT: NO-GO
