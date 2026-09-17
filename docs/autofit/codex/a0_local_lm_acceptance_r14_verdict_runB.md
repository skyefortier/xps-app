# Codex adversarial CODE review — unit A0 — round 14 (delta: labelling, eighth pass), RUN B (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck13_prompt.txt
Outcome: NO-GO x2 — undo/redo restored provenance without re-rendering Results; Auto-Fit rollback dropped provenance; no persistent designation outside the Results panel. Dispositioned in a0_local_lm_acceptance_recheck14_prompt.txt (round 15).

1. **MAJOR — Undo/redo restores provenance without refreshing its visible designation.** In [undo/redo](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:2441), `_restoreSnapshotProvenance()` is followed by peak-list and plot updates, but no `renderResults()`. Reproduced: converged local fit → Clear All → open Results → Undo. Local parameters return and `_isLocalModel()` is true, but Results still displays “Run the fit to see results” without the starting-point warning. `fitResult` remains null, so this is within scope. Refresh Results after restoring provenance and add a behavioral assertion for the displayed warning.

At HEAD `3578ec7`, all **69 targeted tests passed**, including the corrected extraction harness. No additional in-scope export/save gap or numerical regression identified. Browser layout was not exercised.

VERDICT: NO-GO — Undo/redo can restore a local-derived model without refreshing its visible starting-point designation.
