# Codex adversarial CODE review — unit A0 — round 16 (delta: labelling, tenth pass), RUN B (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck15_prompt.txt
Outcome: NO-GO x2 — one MAJOR: the banner could scroll out of view inside the sidebar panel body. Dispositioned in a0_local_lm_acceptance_recheck16_prompt.txt (round 17): sticky.

1. **MAJOR — The persistent designation scrolls out of view.** The [banner](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:2183) remains inside `.panel-body`, whose [CSS enables scrolling](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:182), without sticky positioning. Import a local `.fit.json`, expand peak cards, then scroll down: local-derived parameters and chart curves remain visible while the banner disappears. With `fitResult === null`, the statistic widgets provide no designation, Results is hidden, and the chart legend is disabled. A local history preview over a weighted fit has the same exposure. Place the designation outside the scrolling body or make it sticky, and test visibility after scrolling.

**64/64 targeted tests passed.** Independent runtime probes confirmed preview start/clear and local/weighted history restoration. No additional in-scope export/save gap or delta regression identified. The scrolling finding is established from DOM ancestry and CSS; browser layout was not exercised.

VERDICT: NO-GO — Scrolling the sidebar can hide the only visible starting-point designation while a local-derived model or local history preview remains displayed.
