# Codex adversarial CODE review — unit A0 — round 15 (delta: labelling, ninth pass), RUN B (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck14_prompt.txt
Outcome: NO-GO x2 — banner sat inside the Peaks panel (hidden on Quantify); a local history preview overlay lacked a visible designation; history restore kept stale imported provenance. Dispositioned in a0_local_lm_acceptance_recheck15_prompt.txt (round 16).

1. **MAJOR — The persistent banner disappears outside Peaks.** [The banner](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:2194) is nested inside `#tab-peaks`, which becomes hidden when Quantify opens. Reproduction: import a local `.fit.json` → select Quantify. With `fitResult === null`, Quantify displays only “Run fit to quantify”; the chart continues showing the local-derived model, with its designation confined to a tooltip because the legend is disabled. This is within scope and contradicts “visible whatever panel is open.” Move the banner outside the switchable panels and test ancestor visibility, rather than only its own `style.display`.

All **69 targeted tests passed**. Additional runtime probes confirmed undo/redo refreshes Results and Auto-Fit rollback restores provenance on both live and inactive-record paths. No additional in-scope export/save gap or regression identified. Browser layout was not exercised.

VERDICT: NO-GO — An imported local-derived model remains visible without a persistent starting-point designation when Quantify is selected.
