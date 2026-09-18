# Codex adversarial CODE review — unit W1 (local-engine Poisson weighting) — round 2 (recheck), RUN A (2026-09-18)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/w1_local_weighting_recheck_prompt.txt
Outcome: GO x2. MINORs (note preamble still overstated; CLAUDE.md lacked the upload-rounding qualification) fixed in the same commit that archives these verdicts. Final suites on the owner machine: JS 246 pass / 3 known TODO; pytest tests/ (single invocation) 845 passed / 7 skipped; :5151 browser check pass (Batch Fit chi2r 4.353 vs server 4.357 on C1s Scan_0).

1. **MINOR — The draft preamble retains the withdrawn overclaim.** [Follow-up note, line 5](/Users/skyefortier/xps-app/.claude/worktrees/feature-local-lm-poisson-weighting/docs/comms/2026-09-18-batch-fit-weighting-followup-note.md:5) still says the “more than 100%” warning stops being true at deployment. This contradicts the corrected body, which explicitly preserves that possibility. Restrict the preamble to the measured scans too.

2. **MINOR — The upload-rounding disposition is only partially documented.** The plan records “same formula, not bit-identical inputs,” but [CLAUDE.md](/Users/skyefortier/xps-app/.claude/worktrees/feature-local-lm-poisson-weighting/CLAUDE.md:256) omits that qualification. Its CPS caveat is present. Add the rounding qualification to match the stated disposition.

No round-one **MAJOR** survives in the implementation. TSV/sidebar provenance selection is correct; `caM` is excluded from degrees of freedom while continuous parameters at bounds still count. I found no additional designation/statistic mismatch or regression introduced by the fixes. Apart from the preamble above, the revised evidence claims retain the necessary limitations.

Validation: **246 JavaScript tests passed, 3 TODOs**, including behavioral TSV export, `caM` invariance and server parity. **10 scanner logic tests passed**. Independent numerical checks confirmed weighted chi-square, unweighted RMSE and bound-parameter counting. Tests used in-memory adaptations for the read-only sandbox; browser rendering and filesystem-based scanner CLI tests were not exercised.

VERDICT: GO
