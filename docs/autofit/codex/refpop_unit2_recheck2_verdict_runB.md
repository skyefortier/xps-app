# R2 (element-coverage exhaustion) re-check ROUND 2 — run B

Date: 2026-07-07 (relaunched post-quota-reset per the committed handoff).
Prompt: docs/autofit/codex/refpop_unit2_recheck2_prompt.txt
Runner: codex exec --sandbox read-only, high effort, gtimeout 600s rails.

```
**Residuals**

Residual 1: CLOSED. From `HEAD`, `Lu_nist.html` SHA is `8bbf8fc2...b680`, matching both manifest and provenance; `agent_crosscheck.json` has `Lu-4f7/2 = 7.19`; `Sm_nist.html` SHA matches its manifest row. `tests/test_expand_coverage.py` passed: 7/7.

Residual 2: CLOSED for the blocker scenario. The acquisition path now uses `limit=200` and records `cdx_rows`; all 26 `artifact-has-no-starred-value` rows have `cdx_rows`, max per-format rows is 4, and no row is near 200. No no-starred conclusion still rests on a truncated listing.

**New Finding**

MINOR: [scripts/acquire_nist_archive.py](/Users/skyefortier/xps-app/scripts/acquire_nist_archive.py:238) skips prior OK rows before adding `cdx_rows`, so the claim “every manifest row” / “all 103 elements” is not literally supported. Example: [acquire_manifest.json](/Users/skyefortier/xps-app/.stage9/expand_artifacts/acquire_manifest.json:1321) has Lu with no `cdx_rows`. Concrete scenario: a future reviewer cites repo-wide max-CDX proof from the manifest, but 77 rows lack that field. This does not reopen R2 because the no-starred exhaustion subset is fully recorded and non-binding.

Confirmed: summary regenerates exactly from manifest; counts are `103 = 53 + 24 + 26`; machine tier is `52/79`; fit-physics is `99`; `cf32da4` changed no `data/xps/*` files.

Tests run: `tests/test_coverage_exhaustion.py` 4/4, `tests/test_machine_tier.py` 18/18, `tests/test_expand_coverage.py` 7/7.

VERDICT: GO
```
