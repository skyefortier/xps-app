# Codex re-check ROUND 2 — candidate-pool residual
*Run B, 2026-07-10, codex exec read-only, effort=high, gtimeout 600.
Prompt: candpool_recheck2_prompt.txt (against commit b67e007).*

VERDICT: GO

The residual is closed. The frozen tunables row now says q95 `6.73`, pool-level FP `4.2%/spectrum`, and scopes `≥ 8.5` to `HIGH-COUNT target regimes`, with the low-count `~7.1` caveat: [docs/autofit/cwt-detector-calibration.md](/Users/skyefortier/xps-app/docs/autofit/cwt-detector-calibration.md:48).

Checked the target files for stale current claims. Remaining `3.7` hits are not stale FP claims: they are held-out real-data margin text in the calibration doc and PROGRESS ([docs/autofit/cwt-detector-calibration.md](/Users/skyefortier/xps-app/docs/autofit/cwt-detector-calibration.md:119), [docs/autofit/PROGRESS.md](/Users/skyefortier/xps-app/docs/autofit/PROGRESS.md:2191)), plus the PROGRESS historical re-check record describing the old failure and its fix ([docs/autofit/PROGRESS.md](/Users/skyefortier/xps-app/docs/autofit/PROGRESS.md:2276)).

All current `≥ 8.5` claims are high-count scoped in the doc row, PROGRESS calibration text, and code comment: [docs/autofit/cwt-detector-calibration.md](/Users/skyefortier/xps-app/docs/autofit/cwt-detector-calibration.md:48), [docs/autofit/PROGRESS.md](/Users/skyefortier/xps-app/docs/autofit/PROGRESS.md:2171), [autofit/candidates.py](/Users/skyefortier/xps-app/autofit/candidates.py:62). The low-count floor matches the committed JSONL row `sh:2000:1.3:0.15:4` with `prom_z: 7.1327`: [docs/autofit/inventory/cwt_calibration.jsonl](/Users/skyefortier/xps-app/docs/autofit/inventory/cwt_calibration.jsonl:835).

Commit-scope check on `HEAD~1..HEAD` showed only `PROGRESS.md`, `candpool_recheck2_prompt.txt`, the two archived round-1 verdicts, and `cwt-detector-calibration.md`; no code or evidence JSONL changes. Git emitted read-only temp-cache warnings, but the commands completed.
