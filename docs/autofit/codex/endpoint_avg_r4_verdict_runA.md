# Endpoint averaging refusal — Codex round 4, run A (commit ef92109)

Reviewed `c643c5f..ef92109`, focusing on `21274ad..ef92109`. **No BLOCKER or MAJOR remains in the ordinary production paths. Two MINOR findings remain.**

1. **MINOR — Non-scalar refusal is lost when restoring into the input.**  
   [_restoreUI](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/templates/index.html:3893) assigns the original value when `_endpointAvgFailure(ep)` rejects it. For saved `[3]`, `["3"]`, or `[[3]]`, the input’s string conversion produces `"3"`, which Run Fit accepts. The source reader and Python twin reject the original array.

   Reproduced with the extracted restoration function and a string-coercing input stub; no real-browser reproduction. This does **not** permit averaging outside 1–50, but the round-3 non-scalar fix is incomplete across restoration. **Non-physical inputs required: yes.** A one-line restoration refusal falls within the owner’s exception; add a malformed-array restoration test.

2. **MINOR — Previously logged measurement readers still differ.**  
   The [parity bridge](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/tests/js/local_lm_server_parity_backend.py:28) and [worked-example script](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/scripts/bg_window_worked_example.py:63) use `int(...)`; [measurement request generation](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/scripts/optimizer_disagreement_targets.js:37) uses `parseInt(...) || 1`. Saved `"3.0"` exposes the Python discrepancy. **Non-physical inputs required: no.** These remain tooling limitations, already logged, rather than production-page bypasses.

Prior-finding disposition:

| Finding | Round-4 result |
|---|---|
| Exponent fit-key aliasing; blank edits during upload/fallback | Resolved |
| Saved zero/blank substitution; restored-fit and stack bypasses | Resolved |
| Direct autofit engine and parity bypasses | Resolved |
| Python clamping and ordinary spelling disagreement | Resolved |
| Whitespace, Unicode digits, long strings, radix overflow | Reported cases resolved |
| Batch refusal after initial target mutation | Resolved; source preflight precedes target changes, later failures name the target |
| Archived Find Peaks coercion | Resolved |
| Async analyze creating a job before refusal | Resolved |
| Auto-Fit/spinner tests passing for the wrong reason | Resolved |
| Valid saved spellings lost in the number input | Resolved by decimal normalization |
| Non-scalar disagreement | Helpers agree; restoration gap above remains |

Run Fit, “Use this solution,” Auto-Fit and its post-shift recheck, Batch Fit, local fallback, restoration, stack reconstruction, and fit save/export eligibility reach the refusal or corrected key checks. Remaining production `parseInt(field) || 1` conversions are downstream of validation.

**Compatibility:** 472 background comparisons against `main` were bit-identical, including certificates/effects, all integers 1–50, absent/null settings, JSON numbers, `"3.0"`, `"+3"`, `" 7 "`, hex, and long zero-prefixed strings across eight methods. NumPy integers and JSON `3.0` pass. Blank and disagreeing exponent spellings are deliberately refused.

**Validation:** 103 focused JavaScript tests and 42 Python tests passed without skips. Another 684 reader comparisons agreed. Forty-five invalid HTTP probes across five routes returned plain 400 refusals; five valid/absent-value fits succeeded. Six guard/spinner mutations failed their relevant tests; separate capture/source probes detected both earlier regressions. Harness default changes and quarter-window substitutions preserve their intended claims.

Browser integration was not run under read-only restrictions. HTTP probes mocked session storage. Broader background testing encountered temporary-directory restrictions; its adapted rerun was stopped to bound review time. No files changed.

**VERDICT: GO**
