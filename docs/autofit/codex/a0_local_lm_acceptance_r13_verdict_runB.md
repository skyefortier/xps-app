# Codex adversarial CODE review — unit A0 — round 13 (delta: labelling, seventh pass), RUN B (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck12_prompt.txt
Outcome: NO-GO x2 — undo snapshots taken while a live local result existed carried no provenance; batch clones of a local-derived source carried none. Dispositioned in a0_local_lm_acceptance_recheck13_prompt.txt (round 14).

1. **MAJOR — Undo still loses a live local fit’s designation.** [_peaksSnapshot()](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:2355) captures only `tab.modelProvenance`, which `runFitLocal()` clears. Reproduced: converged local fit → Clear All → Undo restores the local parameters with `fitResult: null` and no provenance. `_isLocalModel()` becomes false, Save Fit writes `fitStatistics: null`, and TSV export omits the warning. Capture local provenance from the current result as well as imported provenance. This involves no retained later result.

2. **MAJOR — Failed batch propagation drops the source model’s designation.** [runPropagation()](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:11109) copies source peaks without copying their provenance. An extracted-function probe with an imported local source, equal intensity scaling, and a failed fit left identical parameters on the target, but no result or provenance. Subsequent Save Fit and TSV output carried no designation. Transfer source provenance with the copied model so it survives failure or interruption.

**67/67 targeted tests passed.** No snapshot-property iteration regression identified: inspected consumers use indexed array operations, iteration over elements, or JSON serialization. Browser layout was not exercised.

VERDICT: NO-GO — Live-local undo and failed batch propagation can save and export local-derived parameters without their starting-point designation.
