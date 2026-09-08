# Codex adversarial review — Find Peaks endpoint averaging (feature-find-peaks-endpoint-avg) — round 1, RUN A (2026-09-08, reviewed at ae2c7f3 / code 29ce18d)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 68,820.
Prompt: docs/autofit/codex/find_peaks_endpoint_avg_review_prompt.txt
Evidence at review time: tests/autofit/test_endpoint_avg_wiring.py 20 passed + methods seam; node 164 pass / 0 fail / 3 known-gap todo; browser find_peaks_endpoint_avg (2) + endpoint_avg_default (10) pass; full pytest + C1s parity gate result recorded in the round-2 header.
Round 1: NO-GO x2 — wiring completeness, byte-stability by inspection and the frontend rule all verified (both); MAJOR (both): pop_endpoint_avg coerces strings/bools (int('1_0') == 10, True -> 1) and lets a non-finite float raise OverflowError (500 not 400), so an Advanced-JSON string can fit at 10 while _fpLast records 1; MINOR (both): the structural guard is a fixed file/callee list with substring matching — a new module escapes it and endpoint_avg=1 would pass.

**Findings**

The averaging plumbing is complete on inspection: refits, proposals, detection, and bound-fixed fits receive the requested value. Perturbation seeds reuse the primary background; candidate-pool net heights use the detection background. CWT intentionally operates on raw counts, and max-entropy/MCR do not participate in these background-based model comparisons.

For absent/1, I found no arithmetic, operation-order, or numerical-default change. The omitted `fit_full_window` arguments on refits are harmless here because those calls supply parameters already constructed with the appropriate bounds. I did not run pytest/Playwright or find this unit’s archived parity verdict, so byte-stability remains unverified experimentally.

Normal frontend behavior follows the stated rule: the panel supplies a numeric value at **run time**, explicit JSON wins, and the apply guard normally does nothing.

1. **MAJOR — Accepted strings can recreate the engine/preview mismatch.** [base.py:100](/Users/skyefortier/xps-app/.claude/worktrees/feature-find-peaks-endpoint-avg/autofit/methods/base.py:100) coerces values with `int(raw)` instead of rejecting strings. I executed the actual helper independently: `"3"` becomes `3`, `"1_0"` becomes `10`, and `true` becomes `1`. However, [index.html:14215](/Users/skyefortier/xps-app/.claude/worktrees/feature-find-peaks-endpoint-avg/templates/index.html:14215) evaluates `"1_0"` as `NaN` and records `_fpLast.endpointAvg = "1"`. Thus Advanced JSON `{"endpoint_avg":"1_0"}` fits at **10**, then Apply sets the panel to **1** and announces the wrong averaging. Reject strings and booleans before conversion, and add a regression covering request validation and recorded averaging. Nonfinite values also need rejection: infinity currently raises uncaught `OverflowError`, which the API maps to 500 rather than 400.

2. **MINOR — The structural test does not enforce its advertised package-wide guarantee.** [test_endpoint_avg_wiring.py:72](/Users/skyefortier/xps-app/.claude/worktrees/feature-find-peaks-endpoint-avg/tests/autofit/test_endpoint_avg_wiring.py:72) enumerates specific file/callee pairs and checks text for `endpoint_avg=`. A new call in another module escapes coverage; passing `endpoint_avg=1` also passes. My independent AST scan found no currently missing arguments, but the claimed protection against future omissions is overstated. Discover calls across `autofit/**/*.py` and supplement that check with a nondefault-value assertion through a stability/proposal refit.

VERDICT: NO-GO — Accepted string options can make the engine fit at averaging 10 while Apply records and displays averaging 1.
