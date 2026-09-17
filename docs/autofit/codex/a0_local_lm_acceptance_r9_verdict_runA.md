# Codex adversarial CODE review — unit A0 — round 9 (delta: labelling, third pass), RUN A (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck8_prompt.txt
Outcome: NO-GO x2 — caption-only refresh could pair a retained local value with a chi-square caption on history restore/clear; renamed preview lost its glow; runFit success test passed through an exception. Dispositioned in a0_local_lm_acceptance_recheck9_prompt.txt (round 10).

1. **MAJOR — History restore can relabel a local statistic as χ²ᵣ.** [renderResults()](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7643) refreshes only the caption. Reproduced: restore a weighted snapshot with χ²ᵣ = 1.25 after a local result of 1234; the status bar displays **χ²ᵣ: 1234.000**, stripping the local designation from the retained local value. The header also remains stale. Refresh the caption, value, header and tooltip together on restore and clear.

2. **MINOR — Renaming local previews removes their glow.** The [preview plugin](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:8837) still requires the exact label `Preview`. Runtime probing confirmed that `Preview (local, starting point)` skips both callbacks. Identify preview datasets independently of their display label.

3. **MINOR — The backend-success test now passes through an exception.** The [test harness](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/tests/js/fit_acceptance.test.js:44) omits `_applyStatCaption`. Its successful-response test actually emits `Fit failed: _applyStatCaption is not defined`, yet passes because its assertions inspect only earlier mutations. Include the helper and assert successful completion.

Validation: **46/46 targeted tests passed**, with the coverage defect above. Independent probes confirmed older-local spectrum-save normalization and separate CSV/XLSX warnings. No additional export or persistence designation gap was identified. Browser layout was not exercised.

VERDICT: NO-GO — History restoration can display a retained local residual variance as χ²ᵣ without its starting-point designation.
