# Shape-switch fix RE-CHECK — run B

Date: 2026-07-08. Commit: 120385f. VERDICT: GO (none found).
Prompt: docs/autofit/codex/shape_switch_recheck_prompt.txt

```
1. Severity: none; file: n/a; concrete scenario: no failing scenario found. `templates/index.html:9512` shape-gates export cols correctly, and `templates/index.html:9550` wires all four export columns through `_shapeExportCols` with unchanged header order/count. The pinned test at `tests/js/shape_switch_roundtrip.test.js:161` discriminates: the old fallback would export `0.22/0.55/0.66` instead of active LACX `ca*`. Original shape-switch behavior remains scoped at `templates/index.html:4718`; no harmful non-shape-gated accumulated-param consumer found. `node --test tests/js/shape_switch_roundtrip.test.js` passes 6/6. Fix: none.

VERDICT: GO
```
