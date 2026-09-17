# Codex adversarial CODE review — unit A0 — round 12 (delta: labelling, sixth pass), RUN A (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck11_prompt.txt
Outcome: NO-GO x2 — provenance lost through undo/redo and Save Spectrum; figure export/chart label keyed on fitResult only; import did not re-render Results; Find Peaks apply kept superseded provenance. Dispositioned in a0_local_lm_acceptance_recheck12_prompt.txt (round 13).

1. **MAJOR — Save Spectrum drops imported local provenance.** Import a local `.fit.json` → Save Spectrum: [`_doSaveSpectrum()`](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:9300) writes the peaks, curves and areas with `statistics: null` and no `modelProvenance`. Runtime reproduction confirmed reloading that `.spec.json` makes `_isLocalModel()` false. Preserve provenance through spectrum save/load.

2. **MAJOR — Undo restores local parameters without their designation.** [Snapshots](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:2355) contain peaks but omit provenance. Reproduced both local import → Clear All → Undo and local import → weighted import → Undo: the local peaks return, `_isLocalModel()` is false, and Save Fit writes `fitStatistics: null`. Capture and restore provenance with the model in undo/redo.

3. **MAJOR — Imported local curves remain unlabelled in figures.** [Publication export](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:10202) gates its warning on `state.fitResult`, which is null after fit-file import. A canvas probe confirmed individual local-derived peaks are drawn and labelled without any designation. The main chart’s envelope label likewise checks only `fitResult`. Apply model provenance to these display/export paths.

4. **MAJOR — Import does not display the new Results warning immediately.** [`fromJSON()`](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:3438) renders peaks and the plot but never calls `renderResults()`. Importing while Results is already open leaves previous results and statistic widgets visible; the new placeholder appears only after another refresh. Refresh Results and its associated widgets when installing the imported model.

5. **MINOR — Find Peaks retains superseded provenance.** [`applyFindPeaks()`](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:14988) replaces all peaks without clearing `modelProvenance`. Reproduction with full-window apply showed the new suggestions still described as imported local parameters, and Save Fit retained the old local statistic. Replace provenance with the model, while preserving it in undo history.

The direct `.fit.json` re-save and TSV warning now work, and tab switching preserves the designation correctly. All **59 targeted tests passed**; extracted-function probes reproduced the gaps above. Browser layout was not exercised.

VERDICT: NO-GO — Local-derived models still lose their designation through spectrum saves and undo, remain unlabelled in figure exports, and can display stale provenance or results.
