# Codex adversarial CODE review — unit A0 — round 9 (delta: labelling, third pass), RUN B (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck8_prompt.txt
Outcome: NO-GO x2 — caption-only refresh could pair a retained local value with a chi-square caption on history restore/clear; renamed preview lost its glow; runFit success test passed through an exception. Dispositioned in a0_local_lm_acceptance_recheck9_prompt.txt (round 10).

1. **MAJOR — Caption refresh can relabel an old local statistic as χ²ᵣ.** [renderResults()](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7643) updates the caption without updating `sb-chi` or `fit-quality`. Runtime reproduction: restore a weighted snapshot (`1.25`) after a local fit (`12345`); the status bar displays **χ²ᵣ: 12345.000**. Clearing the local result and opening Results similarly removes its designation while retaining its number. Refresh the caption, value and header together; clear them when no result exists.

2. **MINOR — Local history previews lose their glow.** The [new preview label](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:8645) no longer matches the [glow plugin’s exact `Preview` comparison](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:8837). Runtime probes confirmed both glow hooks skip local previews. Use a stable dataset identifier independent of display text.

Validation: **46/46 targeted tests passed**; the probes above exposed gaps those tests miss. The other round-8 dispositions are present.

VERDICT: NO-GO — Caption-only refresh can display a local residual variance as unqualified χ²ᵣ, and the renamed local preview loses its glow.
