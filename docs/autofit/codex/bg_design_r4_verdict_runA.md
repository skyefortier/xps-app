# Codex adversarial DESIGN review — background architecture (v4) — round 4, RUN A (2026-09-02)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 75,340.
Prompt: docs/autofit/codex/bg_design_r4_review_prompt.txt
Design under review: docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md (this file records the round-4 state; the committed memo is the final v4+amendments)
Round 4: GO x2 — sealed-record class rules approved; amendments (precise shift transform, non-dirty hydration writer, allowlist structural guard, legacy adapter, local-LM seal contract) folded into the memo as part of the approved design.

**Findings**

1. MAJOR: The auto-fit rigid-shift rule is valid, but the seal spec should state the transform precisely. Shift all energy-coordinate fields by the final CC delta: `sealed.be`, peak center values, any center-like bounds/initials, `settingsSnapshot.bgStart/bgEnd`, ROI/range labels, and manual-anchor `x` if anchors are captured. Do not shift `counts`, `bgIntensity`, `bgSubtracted`, `fittedY`, per-peak `y`, amplitudes, areas, FWHM/width parameters, center stderr/σ, χ², RMSE, or R-factor. If `settingsSnapshot` is “literal request settings,” shifted bg endpoints are not literal; define it instead as “settings expressed in the sealed frame.”

2. MAJOR: The dirty funnel needs a non-dirty hydration path, not raw restore writes “outside” the rule. Project/spec load, tab activation, undo restore, and history restore must restore saved bg/cc fields without dirtying the restored seal, but they should still pass through an allowlisted writer such as `_writeBgInput(field, value, { dirty: false })`. Otherwise a future mutator can hide behind the same restore exception.

3. MAJOR: A source-grep guard can close the missed-call-site class only if it is allowlist-based, not just literal rogue-id grep. It must catch writes to DOM fields, `tab.ui` bg fields, `state.ccShift`, and `manualAnchors`; otherwise dynamic helpers like `setBgField(id, v)`, model-first writes later restored to DOM, or synthetic `dispatchEvent('input')` paths can evade a narrow guard. This is implementable with the same structural-test philosophy, but the design should name the guarded write surfaces.

4. MINOR: The local-LM seal is coherent. Its invariant is “store exactly what local LM fit”: JS background, JS bg-subtracted array, JS per-peak `y`, final peak params, and local stats, with missing backend stderr explicitly absent. This does not conflict with the parity suite; parity alignment changes future JS backgrounds, not the seal contract.

5. MAJOR: Legacy shape migration needs to be a first-class adapter. Existing saves/history/undo paths expect top-level `fitResult.be/bgIntensity/bgSubtracted/fittedY/backendResult`; new consumers expect `fitResult.sealed`. Add a single `normalizeFitResult(raw, peaks, ui, ccShift)` at load/restore boundaries. Old project files that lack `peakResults` should become a flagged partial legacy seal or reconstruct per-peak curves with an explicit “legacy reconstructed” marker, not silently pretend they are authoritative backend peak records.

6. MINOR: Ship order is sound: 1a-1d should stay one branch because mixed sealed/unsealed consumers are a transient hazard. 1c is technically separable and can land first, provided its byte-stability and numeric-shift expectations are documented.

VERDICT: GO
