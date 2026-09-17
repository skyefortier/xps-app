# Codex adversarial CODE review — unit A0 — round 18 (delta: labelling, twelfth pass), RUN A (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck17_prompt.txt
Outcome: NO-GO x2 — one MAJOR: stack visibility/fit toggles repainted without refreshing the banner; MINOR: harnesses lacked the banner helper (fixed in 0b5d6ad/2c44c27 during review). Dispositioned in a0_local_lm_acceptance_recheck18_prompt.txt (round 19).

1. **MAJOR — Stack checkbox changes leave the sticky designation stale.** The [legend handlers](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:2507) call `_updateStackChart()`, which refreshes neither the banner nor the legend. Reproduced with extracted handlers: activate a stack with a local source’s `showFit` off → enable it → envelope becomes visible while the banner remains `display:none`. Scrolling the labelled legend row away then leaves the local curves without a visible designation. Refresh the banner on visibility and fit-toggle changes, including chart early-return paths; test the actual handlers.

2. **MINOR — The new banner dependency breaks existing tests.** [_applyStatDisplay()](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7323) now calls `_updateLocalModelBanner()`, but the statistic-transition and local-descent harnesses omit it. The four targeted suites produced **45 passes and 21 failures**, all failures reporting `_updateLocalModelBanner is not defined`. Supply the dependency in those harnesses.

No additional in-scope export/save gap identified. The stack reproduction used extracted functions and DOM/chart stubs; browser layout was not exercised.

VERDICT: NO-GO — Enabling local stack fit curves can leave the sticky designation hidden, allowing scrolling to remove their only visible warning.
