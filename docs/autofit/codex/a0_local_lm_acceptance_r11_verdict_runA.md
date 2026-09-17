# Codex adversarial CODE review — unit A0 — round 11 (delta: labelling, fifth pass), RUN A (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck10_prompt.txt
Outcome: NO-GO x2 — one MAJOR: reloading a local .fit.json dropped the designation (parameters re-saved/exported unlabelled). Dispositioned in a0_local_lm_acceptance_recheck11_prompt.txt (round 12): the designation now follows the model (tab.modelProvenance).

1. **MAJOR — Save Fit’s designation does not survive reload.** [`fromJSON()`](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:3386) ignores the new `fitStatistics` block and clears `fitResult`. Runtime reproduction: save a local fit → reload onto the same spectrum → save again. Parameters remain unchanged, but `fitStatistics` becomes `null`; TSV export also omits the warning. Preserve imported local provenance through display, export and subsequent saves, and add a behavioral round-trip test.

All **55 targeted tests passed**. Runtime probes confirmed the spectrum-reload fix updates both banners and the statistic display correctly. No additional delta regression identified; browser layout was not exercised.

VERDICT: NO-GO — Reloading a saved local fit discards its designation, allowing unchanged local parameters to be saved and exported without the required warning.
