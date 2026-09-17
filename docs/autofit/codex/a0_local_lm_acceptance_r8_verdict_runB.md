# Codex adversarial CODE review — unit A0 — round 8 (delta: labelling, second pass), RUN B (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck7_prompt.txt
Outcome: NO-GO x2 — stack envelope/legend and history preview undesignated; older local results re-saved without the fields; auto-fit left the status caption stale; CSV/XLSX assertion combined. Dispositioned in a0_local_lm_acceptance_recheck8_prompt.txt (round 9).

1. **MAJOR — Stack and preview curves remain undesignated.** [Stack rendering](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:8237) still emits `C1s (fit)` for a local envelope, while the visible stack legend provides no starting-point warning. Confirmed by executing the dataset builder with a local result. [History previews](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:8642) likewise say only `Preview`; closing History leaves that local curve unqualified. Key these presentations on the source/snapshot objective.

2. **MAJOR — Re-saving older local results omits the designation.** [Spectrum saves](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:9277) and [project saves](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:9366) copy the new fields without deriving them from the objective. A pre-delta local result therefore saves with `reportable: null` and `caveat: null`; both outputs were reproduced. Normalize known local results during loading or serialization to `false` and the canonical caveat.

3. **MAJOR — The new status caption becomes stale after Auto-fit.** [applyAutoFitResult](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:6852) updates the statistic without calling `_applyStatCaption`. Reproduced local → successful weighted Auto-fit: the status bar displays `Residual variance (starting point): 1.250`, although `1.250` is the server’s reduced χ². Refresh the caption on this transition and when clearing/restoring results.

4. **MINOR — CSV/XLSX assertions are still combined.** [The test](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/tests/js/fit_acceptance.test.js:196) contains one broad match for both exports, contrary to disposition 4. Removing either warning would still pass. Assert each branch independently.

Validation: **44/44 targeted tests passed**, supplemented by the runtime probes above. No new Quantify escaping defect, invalid status-bar markup, or incompatibility with the additive JSON fields was identified. The TSV round-tripped through the browser parser; the Python reader also explicitly skips comments. Browser layout and external consumers were not exercised.

VERDICT: NO-GO — Local results remain undesignated in stack/preview displays and older-result re-saves, and weighted Auto-fit can retain an incorrect local status caption.
