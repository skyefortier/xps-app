# Endpoint averaging refusal — Codex round 3, run A (commit 21274ad)

Reviewed `c643c5f..21274ad` on `feat-endpoint-avg-refusal`, focusing on the commit after `8415dc7`. **No BLOCKER or MAJOR finding remains in the requested production paths.**

| Previous finding | Round-3 disposition |
|---|---|
| Fit-key aliasing; blank edits accepted during upload or local fallback | Resolved. Actual capture/key probes discard both results. Reverting the capture fix reproduces both failures. |
| Restored fits and stack/source reconstruction accepting invalid settings | Resolved. Saved blank, numeric zero, `51` and `1e21` receive plain refusals. Reverting the source-reader fix restores the blank/zero bypass. |
| Direct autofit engine and parity bypasses | Resolved; both validate before background computation. |
| Python saved-project reader clamping or misreading values | Reported string/number cases resolved, including Unicode whitespace, Unicode digits, long leading-zero strings and radix overflow. |
| Batch refusal after target mutation | Resolved for invalid source averaging. Preflight precedes target undo/model changes; later target failures retain the target’s name. |
| Archived Find Peaks coercion | Resolved; validates the original field before conversion. |
| Auto-Fit/spinner test defects | Resolved. Exact refusal and spinner activity are asserted; removing the checks fails the selected tests. |
| Async analyze creating a job before refusal | Resolved; invalid requests return 400 without a job ID. |

Run Fit, “Use this solution,” Auto-Fit and its post-shift recheck, Batch Fit, local fallback, restoration, stack reconstruction and save/export eligibility inherit the validation or repaired key comparison. Remaining production `parseInt(field) || 1` calls are downstream of validation.

**Compatibility:** 472 background comparisons against `main` were bit-identical, including certificates and recorded effects. These covered integers 1–50, absent/null settings, JSON numbers, `"3.0"`, `"+3"`, `" 7 "`, hex and long leading-zero strings across eight methods. NumPy integers and JSON `3.0` pass. Blank and disagreeing exponent spellings such as `"1e1"` are intentionally newly refused; they are not silently converted.

Two minor limitations remain:

- **MINOR — malformed saved arrays differ between readers.** The page coerces `[3]` to `3`; [`page_endpoint_avg`](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/autofit/reference.py:390) refuses it. **Non-physical inputs: yes.** Logged under the owner’s rule; a one-line non-scalar refusal could close this discrepancy.
- **MINOR — pre-existing tooling retains independent conversions.** The [local/server parity bridge](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/tests/js/local_lm_server_parity_backend.py:28) uses `int(value or 1)`; [measurement tooling](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/scripts/optimizer_disagreement_targets.js:37) uses `parseInt(value) || 1`. These are not production readers or full reader-parity proofs. **Non-physical inputs: no**—`"3.0"` exposes the Python bridge discrepancy.

Validation: **278 JavaScript tests and 42 Python tests passed, without skips**; 388 additional reader comparisons passed; 40 invalid HTTP requests across five endpoints returned plain 400 refusals; five valid/absent-value fits succeeded. In-memory mutations exercised the capture, source reader, key, core, Run Fit, spinner and Auto-Fit checks. Harness default changes and quarter-window test substitutions are reasonable.

Browser integration tests were not run under the read-only restrictions. Temporary-directory discovery was bypassed in memory for Python tests; route probes mocked session storage. No files changed.

**VERDICT: GO**
