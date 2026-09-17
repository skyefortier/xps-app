# Codex adversarial CODE review — unit A0 — round 8 (delta: labelling, second pass), RUN A (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck7_prompt.txt
Outcome: NO-GO x2 — stack envelope/legend and history preview undesignated; older local results re-saved without the fields; auto-fit left the status caption stale; CSV/XLSX assertion combined. Dispositioned in a0_local_lm_acceptance_recheck8_prompt.txt (round 9).

1. **MAJOR — Stack displays remain unqualified.** The [stack envelope](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:8237) still uses `C1s (fit)`, and the visible stack legend provides no starting-point designation. Executing `_buildStackDatasets()` confirmed a visible local envelope without the restriction. Label each local source in the visible stack legend; changing the dataset label alone is insufficient because envelope tooltips are filtered out.

2. **MAJOR — Resaving older local results omits the designation.** [Spectrum saves](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:9277) and [project saves](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:9366) copy the new fields without deriving them from `objective`. Both executed serializers produced `reportable: null, caveat: null` for an older, objectively identifiable local result. Normalize these fields during loading or serialization.

3. **MINOR — Auto Fit leaves the new status caption stale.** [applyAutoFitResult()](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:6852) updates the statistic without calling `_applyStatCaption()`. Reproduced local → successful Auto Fit: the header reads `χ²ᵣ = 1.25`, while the status bar reads `Residual variance (starting point): 1.250`. Refresh the caption on this path.

4. **MINOR — The claimed separate CSV/XLSX assertions are absent.** The [test](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/tests/js/fit_acceptance.test.js:196) still performs one shared warning match across both branches. Removing either warning can pass. Assert each export independently and cover older-result resaves and caption transitions behaviorally.

Validation: **44/44 targeted tests passed.** Runtime probes confirmed escaped Quantify peak names, both table-export warnings, the unchanged 16-column CSV header, and successful TSV parsing by the app. No additional save-reader incompatibility was identified; external consumers and browser layout were not tested.

VERDICT: NO-GO — Local stack displays and resaved older local results still lack the required designation, and Auto Fit leaves a stale statistic caption.
