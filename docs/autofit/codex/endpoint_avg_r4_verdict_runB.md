# Endpoint averaging refusal — Codex round 4, run B (commit ef92109)

Reviewed `c643c5f..ef92109`, focusing on `21274ad..ef92109`. **No release-blocking finding remains for ordinary inputs.** Two MINOR limitations remain.

1. **MINOR — Restoration can undo the non-scalar refusal.**  
   [`_restoreUI`](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/templates/index.html:3893) passes a refused value unchanged to the number input. Saved `[3]`, `["3"]`, or `[[3]]` therefore becomes `"3"` through input string conversion. Both helpers refuse the original array, but the restored live field accepts it.

   Reproduced using the actual restoration function with a modeled input setter; this was not a real-browser reproduction. **Non-physical inputs required: yes**, malformed saved arrays. Log under the owner’s rule; a one-line refusal that restores objects as blank would close it. The new helper test does not exercise this restoration boundary.

2. **MINOR — Previously logged measurement tools retain different readers.**  
   The [Python parity bridge](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/tests/js/local_lm_server_parity_backend.py:28) still uses `int(value or 1)`; the [optimizer measurement script](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/scripts/optimizer_disagreement_targets.js:37) uses `parseInt(value) || 1`. These remain unsuitable as general reader-parity proofs. **Non-physical inputs required: no**—saved `"3.0"` exposes the Python discrepancy. These are pre-existing tooling limitations, outside the production paths.

Prior-finding disposition:

| Finding | Round 4 |
|---|---|
| Exponent fit-key aliasing; cleared field during upload/local fallback | Resolved; actual-capture probes discard both response and fallback |
| Saved zero/blank/out-of-range restoration and stack reconstruction | Resolved; matching saved keys still receive the background refusal |
| Direct autofit engine and parity bypasses | Resolved |
| Python clamping, `"3.0"`, whitespace, Unicode digits, long strings and radix overflow | Resolved in the tested twins |
| Batch refusal after target mutation | Resolved for initial invalid averaging; later target failures retain the target’s name |
| Archived Find Peaks conversion before validation | Resolved |
| Async analyze job creation before refusal | Resolved |
| Auto-Fit/spinner test-proof defects | Resolved |
| Valid saved spellings sanitized to blank | Resolved by decimal normalization |
| Non-scalar helper disagreement | Resolved between helpers; restoration caveat above |

The reviewed production paths—Run Fit, alternative adoption, Auto-Fit and its post-shift check, Batch Fit, local fallback, restoration, stack reconstruction, and save/export consumers—have the expected guards. Remaining production `parseInt(... ) || 1` conversions are downstream of validation. Initial averaging refusals precede undo entries, spinners, requests, local fitting, and cancellation of an existing fit.

**Compatibility:** 488 background comparisons against `main` were bit-identical, including certificates and recorded effects. Coverage included every integer 1–50, absent/null settings, JSON numbers, accepted spellings and long zero-prefixed strings across eight methods. NumPy integers and JSON `3.0` pass. Blank and disagreeing exponent spellings such as `"1e1"` are deliberately newly refused.

**Validation:** 310 JavaScript tests and 42 selected Python tests passed; 493 additional twin comparisons agreed. Forty invalid HTTP probes across five routes returned plain 400s without job IDs; five valid/absent fits matched backgrounds. Nine JavaScript and five Python refusal mutations failed their intended tests. Harness defaults and quarter-window fixture substitutions are justified.

Browser integration tests were not run. Broader Python-helper checks passed after adjusting temporary-directory discovery in memory; numerical code was unchanged. No files changed.

**VERDICT: GO**
