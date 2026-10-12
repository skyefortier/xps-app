# Endpoint averaging refusal — Codex round 5, run A (commit 1c5b49c)

Reviewed `c643c5f..1c5b49c`, focusing on `26a7ad2..1c5b49c`. **No BLOCKER or MAJOR finding remains.**

The round-5 line closes the malformed-array restoration gap. Executing the actual `_restoreUI` with a string-converting input stub now makes `[3]`, `["3"]`, and `[[3]]` blank and refused. Reverting that line restores the accepted `"3"` bypass. Valid saved spellings still normalize correctly. **The closed finding required non-physical saved inputs.**

| Earlier finding | Disposition |
|---|---|
| Exponent fit-key aliasing; blank edits during upload or local fallback | Resolved: capture preserves blank; invalid spellings no longer compare equal to valid averaging. |
| Saved zero/blank substitution; restored-fit and stack bypasses | Resolved: defaults apply only to absent/null settings; source reconstruction reaches the core refusal. |
| Direct autofit engine and parity bypasses | Resolved; both validate. |
| Python clamping and `"3.0"` disagreement | Resolved. |
| Whitespace, Unicode digits, long strings and radix overflow | Tested cases agree between twins. |
| Batch mutation before initial refusal | Resolved: source preflight precedes target changes. Later target failures retain the target’s name. |
| Archived Find Peaks conversion before validation | Resolved. |
| Async analyze creating a job before refusal | Resolved. |
| Auto-Fit/spinner tests passing for unrelated reasons | Resolved; violating mutations fail their intended tests. |
| Valid saved spellings lost by the number input | Resolved through decimal normalization. |
| Non-scalar refusal lost during restoration | Closed by round 5. |

Run Fit, alternative adoption, Auto-Fit—including its post-shift recheck—Batch Fit, local fallback, restored fits, stack reconstruction and save/export eligibility reach the refusal or corrected context checks. Remaining production `parseInt(field) || 1` conversions are downstream of validation. Initial averaging refusals precede undo entries, spinners, requests, local fitting and cancellation of an existing fit.

**Compatibility:** 480 main/HEAD background comparisons were identical, including arrays, certificates and recorded effects. Coverage included every integer 1–50, absent/null settings, numeric values, accepted spellings and long zero-prefixed strings across eight methods. Another 480 JS/Python reader comparisons agreed. NumPy integers and JSON `3.0` pass. Blank and disagreeing exponent spellings such as `"1e1"` are deliberately newly refused; they are not clamped.

The LACX test change is reasonable for the stated envelope-identity claim. Assertions still require a server result, locked parameter values and the drawn/server curve checks. Coverage is now **alpha 5, alpha 0.1 and beta 5 individually**; **beta 0.1 alone is uncovered**, explicitly documented. The reported browser-path failures on main distinguish this from an averaging regression, but I did **not** independently reproduce the 12-run measurements. Twelve successes establish observed stability, not guaranteed stability.

One previously logged **MINOR** remains: measurement tooling uses independent conversions in the [parity bridge](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/tests/js/local_lm_server_parity_backend.py:28), [optimizer script](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/scripts/optimizer_disagreement_targets.js:37) and [worked example](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/scripts/bg_window_worked_example.py:63). **Non-physical inputs required: no**—saved `"3.0"` exposes the Python discrepancy. These remain tooling limitations, not production bypasses.

Validation: **81 focused JavaScript tests and 42 Python tests passed without skips**; seven JavaScript and five Python mutations failed their intended tests. Forty-five invalid HTTP probes returned plain 400s without job IDs; five valid/absent fits succeeded with exact backgrounds. Harness defaults and quarter-window fixture substitutions preserve their claims.

Browser integration was not run under read-only restrictions. One broader parity test was blocked by temporary-directory discovery; HTTP probes used in-memory session storage. No files changed.

**VERDICT: GO**
