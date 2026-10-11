# Endpoint averaging refusal — Codex round 3, run B (commit 21274ad)

Reviewed `c643c5f..21274ad`, focusing on `8415dc7..21274ad`. **One MAJOR compatibility issue remains.**

1. **MAJOR — Valid saved spellings are accepted by reconstruction/Python but refused after restoration into the page.**  
   [`_restoreUI`](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/templates/index.html:3888) assigns saved text directly to the `type="number"` input. HTML sanitizes strings outside its floating-point grammar to blank—including leading `+`, surrounding whitespace and hexadecimal notation. [HTML specification](https://html.spec.whatwg.org/multipage/input.html#number-state-(type=number)), [numeric grammar](https://html.spec.whatwg.org/multipage/common-microsyntaxes.html#valid-floating-point-number).

   | Saved `ui.endpointAvg` | Source reader / Python | Restored live field |
   |---|---:|---|
   | `"+3"` | 3 | Blank; refused |
   | `" 7 "` | 7 | Blank; refused |
   | `"0x10"` | 16 | Blank; refused |
   | `"1."` | 1 | Blank; refused |
   | `"3.0"` / JSON `3.0` | 3 | Accepted |

   Round 3 now preserves that sanitized blank through capture. Thus source reconstruction can accept a saved value that Run Fit refuses after activation; subsequent capture also loses the saved spelling.

   The [parity test](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/tests/js/endpoint_avg_readers.test.js:34) compares Python with `_endpointAvgFailure` directly, bypassing restoration into the real input. It proves helper agreement, not agreement through this boundary.

   **Non-physical inputs required: no**—ordinary numeric spellings expressly included in this review. Normalize already-validated saved values to their decimal representation when populating the control, and test save/load/activation round trips. This finding is supported by source inspection, the specification, and the actual restore/capture functions with a specification-modeled setter; **not a real-browser reproduction**.

2. **MINOR — Synthetic saved arrays still disagree between twins.**  
   [`_endpointAvgFailure`](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/templates/index.html:3156) accepts `[3]` and `["3"]` through JavaScript string coercion; Python refuses both. **Non-physical inputs required: yes.** Logged under the owner’s rule; a one-line type refusal could close this discrepancy. It does not drive the verdict.

Prior findings:

| Round-1/2 finding | Disposition |
|---|---|
| Exponent fit-key aliasing and cleared-field in-flight acceptance/local fallback | Resolved |
| Saved zero/blank bypass in source reconstruction and restoration | Resolved |
| Direct autofit engine and parity bypasses | Resolved |
| Python clamping/`"3.0"` mismatch | Resolved at helper level; restoration gap above remains |
| Python whitespace, Unicode digits, long strings and radix overflow | Listed reproductions resolved |
| Batch mutation before initial averaging refusal | Resolved; global refusal is accurate, later target summaries name the target |
| Archived Find Peaks coercion | Resolved |
| Auto-Fit/spinner tests and asynchronous analyze validation | Resolved |

Remaining page `parseInt(... ) || 1` conversions are protected by synchronous preflight/core checks. Batch’s module still substitutes for blank, but its page entry refuses blank first. Historical measurement scripts retain independent conversions.

Validation: **257 JavaScript checks and 42 Python tests passed**; one additional JS/Python-helper check was blocked by temporary-directory restrictions. Forty HTTP probes across five routes returned plain 400 refusals. Seven test mutations failed as intended; reverting capture/source fixes reproduced both round-2 bypasses. **464 background comparisons against `main` were bit-identical**, including all integers 1–50 and absent settings. Browser integration was not run. No files changed.

**VERDICT: NO-GO**
