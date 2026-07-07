# R2 (element-coverage exhaustion) re-check ROUND 2 — run A

Date: 2026-07-07 (relaunched post-quota-reset per the committed handoff).
Prompt: docs/autofit/codex/refpop_unit2_recheck2_prompt.txt
Runner: codex exec --sandbox read-only, high effort, gtimeout 600s rails.

```
Residual 1: CLOSED. `HEAD` is self-consistent for the Lu/Sm evidence artifacts. `Lu_nist.html` at `HEAD` hashes to `8bbf8fc2be371d61db62f0bb1c536bcff75496bf0eda1258f5c21aa43b83b680`, matching provenance at [elements-machine.provenance.json](/Users/skyefortier/xps-app/data/xps/elements-machine.provenance.json:898). `agent_crosscheck.json` carries `Lu-4f7/2: 7.19` at [agent_crosscheck.json](/Users/skyefortier/xps-app/.stage9/expand_artifacts/agent_crosscheck.json:20). Sm’s artifact hash matches its manifest row at [acquire_manifest.json](/Users/skyefortier/xps-app/.stage9/expand_artifacts/acquire_manifest.json:1160). Targeted oracle passed: `11 passed in 0.07s`.

Residual 2: NOT-CLOSED as stated. The no-starred subset itself is reverified under the new path: `limit=200` is in [acquire_nist_archive.py](/Users/skyefortier/xps-app/scripts/acquire_nist_archive.py:100), all 26 no-starred rows have `cdx_rows`, and max per-format count among them is 4. But the committed manifest does not record `cdx_rows` in every row: 77/103 rows lack it, including all 24 `no-archive-snapshot` rows and 53 OK rows. Example: H has no `cdx_rows` at [acquire_manifest.json](/Users/skyefortier/xps-app/.stage9/expand_artifacts/acquire_manifest.json:4), and Lu has no `cdx_rows` at [acquire_manifest.json](/Users/skyefortier/xps-app/.stage9/expand_artifacts/acquire_manifest.json:1321). The skip logic preserves those stale rows without backfilling at [acquire_nist_archive.py](/Users/skyefortier/xps-app/scripts/acquire_nist_archive.py:238) and [acquire_nist_archive.py](/Users/skyefortier/xps-app/scripts/acquire_nist_archive.py:245). Concrete scenario: a reviewer cannot verify the claimed “max CDX listing across all 103 elements is 4” from committed evidence, and the no-archive rows still certify empty CDX results without recorded per-format zero counts.

Other checks: summary regeneration is covered by the passing targeted test at [test_coverage_exhaustion.py](/Users/skyefortier/xps-app/tests/test_coverage_exhaustion.py:77). Counts match: `103 = 53 + 24 + 26`, machine `52/79`, fit-physics `99`. Fix commit `cf32da4` does not touch `data/xps`, and later `HEAD` changes do not touch `data/xps` or `.stage9/expand_artifacts`.

VERDICT: NO-GO
```
