# Shape-switch fix RE-CHECK — run A

Date: 2026-07-08. Commit: 120385f. VERDICT: GO (none found).
Prompt: docs/autofit/codex/shape_switch_recheck_prompt.txt

```
1. Severity: none; file: n/a; concrete scenario: none found; fix: n/a. Verified `_shapeExportCols` is shape-gated, export row wiring uses `sc.gl/sc.alpha/sc.beta/sc.m` in unchanged header order, and the LACX stale-param scenario exports `caAlpha/caBeta/caM`. The pinned JS test discriminates against the old fallback chain and `node --test tests/js/shape_switch_roundtrip.test.js` passes 6/6. Original shape-switch scope remains confined to template/test changes; `runFit`, fitting math, `evalPeak/evalPeakArray`, backend `/api/fit`, save/load spread-copy, results, and backend-result application did not reveal a new stale inactive-param consumer.

VERDICT: GO
```
