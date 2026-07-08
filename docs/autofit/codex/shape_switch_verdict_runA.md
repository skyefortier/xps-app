# Shape-switch fix review — run A

Date: 2026-07-08. Commit: d5c3222.
Prompt: docs/autofit/codex/shape_switch_review_prompt.txt

```
1. MAJOR, [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:9536): `exportFitTable` is not shape-gated, so the new never-delete switcher can export stale inactive params. Concrete failing scenario: peak starts as `DS` with `dsAlpha=0.22`, stale/previous DS+G fields `laBeta=0.55`, `laM=0.66`, and active LACX fields `caAlpha=1.70`, `caBeta=0.80`, `caM=37`; sequence `DS -> DSG_LA -> LACX`, then export CSV/XLSX. The active LACX curve uses `caAlpha/caBeta/caM`, but the export writes `Alpha=0.22`, `Beta=0.55`, `M_Gauss=0.66` via `p.dsAlpha ?? p.laAlpha ?? p.caAlpha`, etc. The old delete-then-default path would have deleted DS fields on `DS -> DSG_LA` and DS+G fields on `DSG_LA -> LACX`, so this is an introduced accumulation regression. Fix: make fit-table export choose Alpha/Beta/M by `p.shape`, matching `evalPeak`/`peakToBackendSpec`, instead of fallback chains.

VERDICT: NO-GO
```
