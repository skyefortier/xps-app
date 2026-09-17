# Codex adversarial CODE review — unit A0 — round 17 (delta: labelling, eleventh pass), RUN A (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck16_prompt.txt
Outcome: NO-GO x2 — one MAJOR: stack views drawing a local source fit had no non-scrolling designation. Dispositioned in a0_local_lm_acceptance_recheck17_prompt.txt (round 18).

1. **MAJOR — Stack scrolling can still hide the only designation.** [Stack legend labels](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:2485) sit in ordinary scrolling rows, while [the sticky banner](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7265) ignores stack sources. Add a local fit followed by enough weighted spectra to overflow the legend, then scroll its row away: the local curves remain visible without a designation. The chart legend is disabled, and envelope tooltips are filtered out. An extracted-function probe confirmed the local envelope remains visible while the banner is hidden. Extend the persistent banner to identify displayed local stack sources and test scrolling that legend.

**Validation:** 87 tests passed. The round-16 spectrum-banner fix is present; no additional in-scope export/save gap or regression identified. Stack scrolling was assessed through source inspection and behavioral probes, without browser layout execution.

VERDICT: NO-GO — Stack scrolling can leave local fit curves visible without their starting-point designation.
