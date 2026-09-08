# Codex adversarial review — Find Peaks endpoint averaging (feature-find-peaks-endpoint-avg) — round 1, RUN B (2026-09-08, reviewed at ae2c7f3 / code 29ce18d)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 67,090.
Prompt: docs/autofit/codex/find_peaks_endpoint_avg_review_prompt.txt
Evidence at review time: tests/autofit/test_endpoint_avg_wiring.py 20 passed + methods seam; node 164 pass / 0 fail / 3 known-gap todo; browser find_peaks_endpoint_avg (2) + endpoint_avg_default (10) pass; full pytest + C1s parity gate result recorded in the round-2 header.
Round 1: NO-GO x2 — wiring completeness, byte-stability by inspection and the frontend rule all verified (both); MAJOR (both): pop_endpoint_avg coerces strings/bools (int('1_0') == 10, True -> 1) and lets a non-finite float raise OverflowError (500 not 400), so an Advanced-JSON string can fit at 10 while _fpLast records 1; MINOR (both): the structural guard is a fixed file/callee list with substring matching — a new module escapes it and endpoint_avg=1 would pass.

**Findings**

1. **MAJOR — Accepted strings can recreate the fit/panel divergence.** [base.py:100](/Users/skyefortier/xps-app/.claude/worktrees/feature-find-peaks-endpoint-avg/autofit/methods/base.py:100) coerces values with `int(raw)`: `"3"` and `true` are accepted despite the stated validation contract. More seriously, isolated execution confirmed that `"endpoint_avg": "1_0"` becomes **10** in Python, while the [frontend expression](/Users/skyefortier/xps-app/.claude/worktrees/feature-find-peaks-endpoint-avg/templates/index.html:14215) records **1**. Applying a successful result then sets the panel to the wrong averaging with a misleading notice. Reject strings and booleans before conversion and test this request/record/apply case. Nonfinite values also need rejection: infinity currently raises uncaught `OverflowError`, producing a 500 instead of 400.

2. **MINOR — The structural guard does not enforce its package-wide claim.** [test_endpoint_avg_wiring.py:73](/Users/skyefortier/xps-app/.claude/worktrees/feature-find-peaks-endpoint-avg/tests/autofit/test_endpoint_avg_wiring.py:73) checks a fixed file/callee list using substring matching. A new module’s background call escapes coverage, and `endpoint_avg=1` would satisfy the guard despite dropping the requested value. Recursively inspect Python AST calls and add behavioral coverage for nondefault averaging through refits.

The remaining wiring checks out: all 10 current fitting/background calls explicitly forward the option. Perturbation, augmentation, detection, and pool net signals use the appropriate background; CWT consumes raw-signal curvature. MaxEntropy/MCR introduce no competing endpoint anchors. Omitting `fit_full_window` at refit calls remains safe because their supplied initial parameters already carry the bounds.

For ordinary integer settings, the frontend reads the panel at run time, preserves explicit JSON overrides, and avoids capturing a stale default when opening the modal. The apply guard is normally a no-op.

Default-1 arithmetic appears unchanged by inspection. I did not run pytest/Playwright, and no archived verdict for this unit was present to verify the reported parity-gate result. Current HEAD `ae2c7f3` adds only the review prompt after `29ce18d`.

VERDICT: NO-GO — Accepted string values can make the engine fit at averaging 10 while the frontend records and applies averaging 1.
