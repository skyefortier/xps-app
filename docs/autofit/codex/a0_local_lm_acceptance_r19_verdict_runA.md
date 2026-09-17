# Codex adversarial CODE review — unit A0 — round 19 (delta: labelling, thirteenth pass), RUN A (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck18_prompt.txt
Outcome: run B GO; run A NO-GO (stricter governs) — one MAJOR: closing a local source tab pruned the active stack legend but not the chart. Dispositioned in a0_local_lm_acceptance_recheck19_prompt.txt (round 20).

1. **MAJOR — Closing a stack’s local source removes its designation while leaving its curves visible.** In [`closeTab()`](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:3267), closing an inactive source prunes its stack entry and rebuilds the legend, hiding the banner, but never rebuilds the active chart. Reproduced with extracted functions: activate a stack containing local and weighted fits → close the local source tab. The banner changes from `block` to `none`, while the local envelope remains visible. Rebuild the stack datasets when pruning source entries and add a behavioral regression test. This is source deletion, outside the excluded model-replacement RESULT-retention case.

Both round-18 fixes are present; **67/67 targeted tests pass**. Full-suite execution produced 228 passes, 12 failures from Python parity tests lacking a writable temporary directory, and 3 TODOs. No additional in-scope export/save gap identified. Browser layout was not exercised.

VERDICT: NO-GO — Closing a local source tab can leave its stack curves visible after both the legend designation and sticky banner disappear.
