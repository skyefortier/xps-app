# Codex adversarial CODE review — unit A0 — round 18 (delta: labelling, twelfth pass), RUN B (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck17_prompt.txt
Outcome: NO-GO x2 — one MAJOR: stack visibility/fit toggles repainted without refreshing the banner; MINOR: harnesses lacked the banner helper (fixed in 0b5d6ad/2c44c27 during review). Dispositioned in a0_local_lm_acceptance_recheck18_prompt.txt (round 19).

1. **MAJOR — Stack toggles can reveal local curves without refreshing the banner.** The [checkbox handlers](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:2507) call `_updateStackChart()`, which neither rebuilds the legend nor refreshes the banner. Reproduced: activate a stack with the local entry’s `showFit` off → enable it → local envelope becomes visible while the banner remains hidden. Scrolling the legend row away removes the remaining designation. Enabling entry visibility has the same defect. Refresh the banner on both transitions and test the actual handlers.

2. **MINOR — The new banner dependency breaks existing tests.** `_applyStatDisplay()` now calls `_updateLocalModelBanner()`, but the [statistic tests](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/tests/js/fit_acceptance.test.js:293) and [local-optimizer harness](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/tests/js/local_lm_descent.test.js:37) omit that dependency. **21 tests fail** with `_updateLocalModelBanner is not defined`. Include the helper with its dependencies or stub it where appropriate.

Validation: **45/66 targeted tests passed**; extracted-function probes confirmed both toggle failures. No additional in-scope export/save gap identified. Browser layout was not exercised.

VERDICT: NO-GO — Stack visibility and fit toggles can leave local curves displayed without a persistent starting-point designation.
