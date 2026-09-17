# Codex adversarial CODE review — unit A0 — round 10 (delta: labelling, fourth pass), RUN B (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck9_prompt.txt
Outcome: run A GO, run B NO-GO (stricter governs) — spectrum reload skipped renderResults; Save Fit .fit.json carried no designation. Dispositioned in a0_local_lm_acceptance_recheck10_prompt.txt (round 11).

1. **MAJOR — Spectrum reload bypasses the designation refresh.** [_loadSpectrumFile](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:9588) installs the saved result after tab activation cleared the displays, then calls only `renderPeakList()` and `updatePlot()`. Runtime reproduction showed local peak areas displayed without a starting-point designation, while the header/status remained empty. Call `renderResults()` after restoring the result.

2. **MAJOR — Save Fit still omits the designation.** [_doSaveFit](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:9203) exports local fitted parameters to `.fit.json` without objective, caveat or reportability metadata. Executing the serializer confirmed those numerical parameters survive while their designation disappears. Include the local provenance and starting-point caveat in this save format.

All **53 targeted tests passed**. The round-9 statistic transition, preview glow and success-harness fixes check out. No additional delta-induced regression identified; browser layout was not exercised.

VERDICT: NO-GO — Local values remain undesignated immediately after spectrum reload and in Save Fit output.
