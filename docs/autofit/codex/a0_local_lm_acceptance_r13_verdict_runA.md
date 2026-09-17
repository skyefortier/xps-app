# Codex adversarial CODE review — unit A0 — round 13 (delta: labelling, seventh pass), RUN A (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck12_prompt.txt
Outcome: NO-GO x2 — undo snapshots taken while a live local result existed carried no provenance; batch clones of a local-derived source carried none. Dispositioned in a0_local_lm_acceptance_recheck13_prompt.txt (round 14).

1. **MAJOR — Undo loses provenance from a live local fit.** [_peaksSnapshot()](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:2355) captures only `modelProvenance`, which `runFitLocal()` clears. Reproduced: converged local fit → Clear All → Undo restores identical parameters, but `_isLocalModel()` is false, Save Fit writes `fitStatistics:null`, and TSV omits the warning. Capture designation from the current local result too. This reproduction has no retained later result.

2. **MAJOR — Failed batch propagation drops the copied model’s designation.** [runPropagation()](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:11110) copies source peaks without source provenance. Reproduced with an imported local model and an empty target ROI: fitting fails, copied parameters remain, and Save Fit writes `fitStatistics:null`. Carry source provenance with the copied model until a successful fit supersedes it.

All **59 targeted tests passed**; extracted-function probes confirmed both gaps. No regression from enumeration of snapshot properties was identified: inspected peak consumers use array iteration or array methods. Browser layout was not exercised.

VERDICT: NO-GO — Local-derived parameters still lose their starting-point designation through Clear All → Undo and failed batch propagation.
