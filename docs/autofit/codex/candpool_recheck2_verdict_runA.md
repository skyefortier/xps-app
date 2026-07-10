# Codex re-check ROUND 2 — candidate-pool residual
*Run A, 2026-07-10, codex exec read-only, effort=high, gtimeout 600.
Prompt: candpool_recheck2_prompt.txt (against commit b67e007).*

VERDICT: GO

The live frozen-tunables row is fixed: [docs/autofit/cwt-detector-calibration.md](/Users/skyefortier/xps-app/docs/autofit/cwt-detector-calibration.md:48) now says q95 `6.73`, pool-level FP `4.2%/spectrum`, scopes `≥ 8.5` to `HIGH-COUNT`, and notes the low-count `~7.1` case.

The remaining `3.7` hits are not stale FP claims: they are gate-margin ratios in [docs/autofit/cwt-detector-calibration.md](/Users/skyefortier/xps-app/docs/autofit/cwt-detector-calibration.md:119) and [docs/autofit/PROGRESS.md](/Users/skyefortier/xps-app/docs/autofit/PROGRESS.md:2191), plus the PROGRESS re-check record describing the old defect at [docs/autofit/PROGRESS.md](/Users/skyefortier/xps-app/docs/autofit/PROGRESS.md:2278).

All `8.5` sensitivity claims in the checked files are high-count-scoped: calibration table/doc at [docs/autofit/cwt-detector-calibration.md](/Users/skyefortier/xps-app/docs/autofit/cwt-detector-calibration.md:48) and [docs/autofit/cwt-detector-calibration.md](/Users/skyefortier/xps-app/docs/autofit/cwt-detector-calibration.md:103), PROGRESS at [docs/autofit/PROGRESS.md](/Users/skyefortier/xps-app/docs/autofit/PROGRESS.md:2171), and code comment at [autofit/candidates.py](/Users/skyefortier/xps-app/autofit/candidates.py:62).

The `~7.1` floor matches the committed JSONL row: `sh:2000:1.3:0.15:4` has `prom_z: 7.1327` at [docs/autofit/inventory/cwt_calibration.jsonl](/Users/skyefortier/xps-app/docs/autofit/inventory/cwt_calibration.jsonl:835).

The fix commit `b67e007` touches only `docs/autofit/PROGRESS.md`, `docs/autofit/cwt-detector-calibration.md`, the two archived verdicts, and `docs/autofit/codex/candpool_recheck2_prompt.txt`. No code or evidence JSONL files are in that commit.
