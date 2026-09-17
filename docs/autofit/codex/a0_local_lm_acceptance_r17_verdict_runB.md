# Codex adversarial CODE review — unit A0 — round 17 (delta: labelling, eleventh pass), RUN B (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck16_prompt.txt
Outcome: NO-GO x2 — one MAJOR: stack views drawing a local source fit had no non-scrolling designation. Dispositioned in a0_local_lm_acceptance_recheck17_prompt.txt (round 18).

1. **MAJOR — Stack view can still hide the only visible designation.** The [sticky banner helper](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7265) checks the active model and history preview, but not stack sources. Add a local fit and enough other spectra to a stack, then scroll its [legend row](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:2485) out of view: local curves remain displayed without a visible designation. The chart legend is disabled, and envelope tooltips are filtered out. An execution probe confirmed the local envelope is visible while the sticky banner is hidden. Make the persistent banner account for displayed local stack sources.

**65/65 targeted tests passed.** No additional in-scope save/export gap or delta regression identified. Scrolling visibility follows from DOM/CSS inspection; browser layout was not independently exercised.

VERDICT: NO-GO — Local fit curves in Stack view can remain visible after their only starting-point designation scrolls out of view.
