# Codex adversarial CODE review — unit A0 — round 12 (delta: labelling, sixth pass), RUN B (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck11_prompt.txt
Outcome: NO-GO x2 — provenance lost through undo/redo and Save Spectrum; figure export/chart label keyed on fitResult only; import did not re-render Results; Find Peaks apply kept superseded provenance. Dispositioned in a0_local_lm_acceptance_recheck12_prompt.txt (round 13).

1. **MAJOR — Undo loses the designation.** Import a local `.fit.json` → Clear All → Undo restores the local peaks, but `_isLocalModel()` returns false and Save Fit writes `fitStatistics:null`. [clearAllPeaks](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:5686) clears provenance; undo snapshots never restore it. Capture and restore provenance alongside peaks for undo/redo.

2. **MAJOR — Save Spectrum drops imported provenance.** [The serializer](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:9300) writes `statistics:null` when an imported model has no result, and omits `modelProvenance`. Runtime reproduction produced local-derived curves and areas without any designation; reloading that spectrum and saving a fit also produced `fitStatistics:null`. Preserve model provenance through spectrum save/load.

3. **MAJOR — Publication export emits imported local components without a warning.** After importing a local `.fit.json`, PNG export draws its component curves, but [the annotation](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:10202) requires `state.fitResult`. A canvas probe confirmed component rendering with no starting-point designation. The [main chart label](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:8645) likewise checks only the result. Use model provenance for these displays.

4. **MAJOR — Import does not display the new Results warning immediately.** [fromJSON’s refresh sequence](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:3438) calls neither `renderResults()` nor `_applyStatDisplay()`. Runtime reproduction retained the ordinary “Run the fit to see results” placeholder after importing local parameters; explicitly rendering Results installed the warning. Existing Results/Quantify content and statistic widgets can remain stale until another refresh.

5. **MINOR — Find Peaks retains superseded provenance.** [Applying suggestions](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:14988) replaces every peak without clearing `modelProvenance`. Runtime reproduction then saved the new model with the imported local fit’s objective, residual variance, and caveat. Clear superseded provenance during replacement and preserve it in the undo entry.

The direct `.fit.json` import → TSV export and Save Fit paths now preserve the warning and `reportable:false`; display remains incomplete as above. Project persistence and tab ownership appear correct on inspection. All **52 targeted tests passed**; extracted-function probes reproduced these gaps. Browser layout was not exercised.

VERDICT: NO-GO — Local-model designation is still lost through undo and spectrum save/load, omitted from publication exports, and inconsistently refreshed or cleared during model replacement.
