# Endpoint averaging refusal — Codex round 5, run B (commit 1c5b49c)

Reviewed `c643c5f..1c5b49c`, including the round-5 delta after `26a7ad2`. **No BLOCKER or MAJOR found.**

The one-line change in [_restoreUI](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/templates/index.html:3893) closes the malformed-array gap. Saved arrays and objects restore as blank and are refused. Removing that line in memory reproduced `[3]`, `["3"]` and `[[3]]` becoming accepted `"3"`. This was a modeled input-setter probe, not a browser run. **Non-physical inputs: yes; now resolved.**

The earlier findings are resolved:

| Finding | Disposition |
|---|---|
| Exponent key aliasing and blank edits during upload/fallback | Raw capture and validated key comparison prevent acceptance |
| Saved zero/blank substitution; restoration and stack bypasses | Defaults apply only to absent/null settings; invalid values reach the core refusal |
| Direct autofit engine and parity bypasses | Both validate |
| Python clamping and reader discrepancies | Tested spellings agree, including whitespace, signs, radix prefixes, exponents, long strings and JSON numbers |
| Valid saved spellings lost in the number input | Already-valid values restore as plain decimals |
| Non-scalar disagreement | Helpers and restoration now refuse |
| Batch mutation before initial refusal | Source preflight precedes target mutation; later failures retain the target’s name |
| Archived Find Peaks coercion; async analyze job creation | Validation precedes conversion/request or job creation |
| Auto-Fit and spinner tests passing for the wrong reason | Violating mutations fail their intended assertions |

I found no remaining production bypass across Run Fit, alternative adoption, Auto-Fit and its post-shift check, Batch Fit, local fallback, stack reconstruction, restored fits, save/export consumers or the requested server entries. Remaining production `parseInt(... ) || 1` calls are downstream of validation.

**Compatibility:** 488 background comparisons against `main` were bit-identical, including certificates and recorded effects, across eight methods. Coverage included every integer 1–50, absent/null settings, JSON numbers, `"3.0"`, `"+3"`, `" 7 "`, hex and long zero-prefixed strings. NumPy integers pass. Blank and spellings such as `"1e1"` are deliberately newly refused—the latter because `Number` and `parseInt` disagree. API numeric strings are also deliberately refused.

**One previously logged MINOR remains:** measurement tools retain independent conversions, including the [Python parity bridge](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/tests/js/local_lm_server_parity_backend.py:28) and [optimizer measurement script](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/scripts/optimizer_disagreement_targets.js:37). They are unsuitable as general reader-parity proofs. **Non-physical inputs: no**—`"3.0"` exposes the Python mismatch. These are outside production paths.

The **LACX test-only adjustment is reasonable and honestly scoped**: the replacement cases retain fit, lock and envelope assertions without relaxing tolerances. The comment explicitly admits that β’s lower bound alone is uncovered. The reported main-branch failures support treating the old case as an unreliable fixture; 12/12 successes do not establish permanent stability. I did not independently repeat those browser measurements.

Validation: **101 JavaScript tests and 42 Python tests passed without skips**, 337 additional reader comparisons agreed, 45 invalid HTTP probes returned plain 400s without job IDs, and five valid/absent fits succeeded. Seven JavaScript and five Python mutations failed their intended tests. Harness defaults and quarter-window fixture substitutions preserve their claims.

Browser integration was not run under the read-only restrictions. Python temporary-directory discovery and HTTP session storage were adapted in memory. No files changed.

VERDICT: GO
