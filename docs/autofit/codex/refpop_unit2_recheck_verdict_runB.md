# Codex re-check — Unit R2 dispositions — RUN B (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 117,202.
Prompt: docs/autofit/codex/refpop_unit2_recheck_prompt.txt

**Disposition**
Finding 1: CLOSED. `cdx_snapshots()` now returns `(snapshots, error)`, CDX failures become `cdx query failed`, summary classifies them as `cdx-query-failed-UNPROVEN`, and the count pin only admits the two proven classes. An UNPROVEN row would fail [tests/test_coverage_exhaustion.py](/Users/skyefortier/xps-app/tests/test_coverage_exhaustion.py:46).

Finding 2: CLOSED on the core failure. `acquire()` now iterates listed snapshots earliest-first and only records no-starred after exhausting that list. Current manifest has zero CDX errors, 24 no-snapshot, 26 no-starred, 53 OK. Lu is recovered in current worktree: `Lu-4f7/2 = 7.19`, `Powe95`, artifact SHA `8bbf8fc2be371d61db62f0bb1c536bcff75496bf0eda1258f5c21aa43b83b680`.

Finding 3: CLOSED. The manifest consistency test now requires `m is not None` and `status == OK` for every machine element at [tests/test_coverage_exhaustion.py](/Users/skyefortier/xps-app/tests/test_coverage_exhaustion.py:95).

Data drift check: `d13b6cd^..d13b6cd` adds exactly `Lu-4f7/2`, removes nothing, and changes no existing machine transition. Counts match: machine `52/79`, fit-physics `99`, exhaustion `103 = 53 + 24 + 26`.

**New Findings**
BLOCKER [data/xps/elements-machine.provenance.json](/Users/skyefortier/xps-app/data/xps/elements-machine.provenance.json:909), [tests/test_expand_coverage.py](/Users/skyefortier/xps-app/tests/test_expand_coverage.py:88): the committed HEAD is not self-consistent for the evidence artifacts. `.stage9/expand_artifacts/*` files are tracked, not gitignored. Clean HEAD’s tracked `Lu_nist.html` is still the old 2016 ASPX artifact, SHA `cd2adb...`, with no `Powe95` and no star; HEAD’s tracked `agent_crosscheck.json` also lacks `Lu-4f7/2`. Current working tree has the corrected `.stage9` files dirty, which is why local direct probes pass. Concrete scenario: fresh checkout of HEAD runs `test_every_emitted_value_literally_in_committed_artifact`; Lu fails both independent starred-HTML extraction and provenance SHA match.

MINOR [scripts/acquire_nist_archive.py](/Users/skyefortier/xps-app/scripts/acquire_nist_archive.py:94): `limit=12` remains. I would accept the cap only with an explicit certification caveat, because [scripts/acquire_nist_archive.py](/Users/skyefortier/xps-app/scripts/acquire_nist_archive.py:190) still says “ANY archived snapshot” while the real guarantee is “any listed snapshot under the CDX cap.” Raise/remove the cap or document that boundary.

Could not run pytest in this read-only profile: Python could not create any temporary file for pytest capture. I used direct read-only probes instead.

VERDICT: NO-GO
