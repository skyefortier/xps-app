# Codex adversarial CODE review — unit A0 — round 14 (delta: labelling, eighth pass), RUN A (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck13_prompt.txt
Outcome: NO-GO x2 — undo/redo restored provenance without re-rendering Results; Auto-Fit rollback dropped provenance; no persistent designation outside the Results panel. Dispositioned in a0_local_lm_acceptance_recheck14_prompt.txt (round 15).

1. **MAJOR — Auto Fit rollback can discard model provenance.** [`_autoFitSnapshot()` and its restore path](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:6683) omit `modelProvenance`. Runtime reproduction: import a local `.fit.json` → start Auto Fit → Clear All while the request is pending → request fails. Rollback restores the original local parameters, but `_isLocalModel()` returns false and Save Fit writes `fitStatistics:null`. No later result is retained: `fitResult` remains null throughout. Capture and restore provenance alongside the rollback model.

2. **MAJOR — Imported local models remain visibly undesignated in the default Peaks view.** [`renderResults()`](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7679) places the warning inside the hidden Results panel while clearing the persistent statistic designation. Peak cards display centers, widths and area percentages without qualification. The chart’s designation exists only in its tooltip because [its legend is disabled](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:8903). Show a persistent model designation outside the Results panel.

Both round-13 dispositions passed behavioral probes. At HEAD `3578ec7`, **61/61 targeted tests pass**, including the concurrently corrected test harness. Browser layout was not exercised.

VERDICT: NO-GO — Local-derived models can still lose their designation through Auto Fit rollback and appear without a visible designation in the default Peaks view.
