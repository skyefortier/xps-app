# Codex adversarial CODE review — unit A0 — round 15 (delta: labelling, ninth pass), RUN A (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck14_prompt.txt
Outcome: NO-GO x2 — banner sat inside the Peaks panel (hidden on Quantify); a local history preview overlay lacked a visible designation; history restore kept stale imported provenance. Dispositioned in a0_local_lm_acceptance_recheck15_prompt.txt (round 16).

1. **MAJOR — The “persistent” banner disappears in Quantify.** [The banner](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:2194) sits inside `#tab-peaks`, which becomes hidden when another panel opens. Reproduced: import local `.fit.json` → open Quantify. The local-derived curves remain displayed, but Quantify says only “Run fit to quantify”; Results is hidden, and the chart’s designation requires hovering. Move the banner outside the switchable panels.

2. **MAJOR — A local history preview can remain displayed without a visible designation.** [_historyPreviewSnap()](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:13055) leaves its overlay active after History closes. Reproduced with a weighted current fit and a local history snapshot: closing History hides the snapshot’s warning, while the preview’s designation exists only in its dataset label—the chart legend is disabled. Add a visible designation for the active local preview. This involves a separate historical overlay, not model-replacement result retention.

3. **MINOR — Restoring weighted history can propagate stale local provenance.** [_historyRestoreSnap()](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:13084) restores matching peaks and result without clearing imported provenance. [_provenanceOf()](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7269) then prioritizes that stale provenance. Reproduced: import local model → restore weighted snapshot → obtain batch source provenance. The weighted model is classified as local; a failed batch target preserves that false designation. Reconcile provenance when restoring history.

All **69 targeted tests passed**. Extracted-function probes confirmed these findings and successful Auto-Fit provenance rollback on both owner paths. Visibility was checked against DOM structure and CSS; no browser layout test was run.

VERDICT: NO-GO — Local-derived models and local history previews can still appear without a visible starting-point designation.
