# Codex adversarial CODE review — unit A0 — round 16 (delta: labelling, tenth pass), RUN A (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck15_prompt.txt
Outcome: NO-GO x2 — one MAJOR: the banner could scroll out of view inside the sidebar panel body. Dispositioned in a0_local_lm_acceptance_recheck16_prompt.txt (round 17): sticky.

1. **MAJOR — Scrolling hides the model’s only visible designation.** The [banner](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:2183) remains inside `.panel-body`, which has `overflow-y: auto`; it is not sticky. Import a local `.fit.json`, expand peak cards, then scroll down: the warning leaves view while local-derived parameters and curves remain visible. With `fitResult === null`, statistic widgets carry no designation, and the chart legend is disabled. Place the warning outside the scrolling container or make it sticky, and test visibility after scrolling.

All **70 targeted tests passed**. Behavioral probes confirmed the history preview/clear/restore fixes. No additional in-scope export/save gap or regression identified. The scrolling finding follows from DOM/CSS inspection; browser layout was not exercised.

VERDICT: NO-GO — Scrolling the sidebar can hide the only visible starting-point designation while local-derived parameters and curves remain displayed.
