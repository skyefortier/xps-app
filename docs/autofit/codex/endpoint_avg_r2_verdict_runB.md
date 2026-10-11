# Endpoint averaging refusal — Codex round 2, run B (commit 8415dc7)

Reviewed `8415dc7`, with the unit against `c643c5f` and round 2 against `64c3376`. Two ordinary-input bypasses remain.

1. **MAJOR — Clearing the field still bypasses in-flight checks.**  
   [`_captureUI`](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/templates/index.html:3868) converts blank to `"1"` before the repaired fit-key reader sees it. Using the actual capture function, I reproduced starting at `1`, clearing the field during upload, and receiving **“Fit complete”**, an applied result, and a key recording `"1"`. With a transport failure, **local fitting still ran**. The same key permits current statistics and project-save classification. Preserve the typed value through capture; apply the legacy default only when the setting is absent.  
   **Non-physical inputs required: no**—clearing an ordinary field suffices.

2. **MAJOR — Saved/source settings still silently substitute `1`.**  
   [`_computeBackgroundForSource`](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/templates/index.html:10028) uses `endpointAvg || LEGACY_ENDPOINT_AVG` before reaching the new core refusal. I reproduced numeric JSON `0` and `""` producing certified backgrounds at `1`, although `computeBackgroundCore` directly refuses both. Actual restoration returned **`failure: null`, no `backgroundStale`** for records carrying those settings and matching previously computed envelopes. Stack reconstruction shares this reader. Restore/load boundaries also contain the same substitution.  
   **Non-physical inputs required: no**—ordinary spectra and saved settings suffice. The additional `false → 1` case is synthetic.

3. **MAJOR — The Python twin still disagrees with the page on synthetic spellings.**  
   [`page_endpoint_avg`](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/autofit/reference.py:336) uses Python whitespace, Unicode-digit and integer-conversion rules:
   - `"\uFEFF3"`: page accepts `3`; Python refuses.
   - `"\u00853"` and `"3e٠"`: page refuses; Python accepts `3`.
   - 5,000 leading zeroes followed by `3`: page accepts; Python raises its 4,300-digit conversion-limit error.
   - A sufficiently long hexadecimal string raises `OverflowError`, rather than the plain refusal.

   **Non-physical/synthetic inputs required: yes.** Log these under the owner’s rule; they are not needed for this NO-GO. The parity test’s 400-zero example misses the previously reported long-string failure.

Round-1 disposition:

| Finding | Round-2 result |
|---|---|
| Fit-key aliasing | Exponent cases fixed; blank bypass remains |
| Restoration/stack/export readers | Truthy invalid values refused; falsey substitution remains |
| Direct engine and parity | Resolved |
| Saved-project Python twin | Ordinary spellings fixed; synthetic discrepancies remain |
| Batch mutation before refusal | Source refusal now precedes target mutation; blank checked directly; late target summaries retain the target name |
| Archived Find Peaks coercion | Resolved |
| Auto-Fit/spinner test defects | Resolved; both violating mutations now fail |
| Async analyze job creation | Resolved; invalid averaging rejected before a job ID is returned |

For compatibility, **472 page-background comparisons against `main` were bit-identical**, covering all integers 1–50, absent/null settings, JSON numbers, `"3.0"`, `"+3"`, `" 7 "`, hex and long zero-prefixed valid strings across eight background methods. Blank is newly refused directly, as documented. NumPy integers and integral floats passed. Python’s `"3.0" → 3` intentionally corrects its previous disagreement.

Remaining page `parseInt(field) || 1` calls in Run Fit and Auto-Fit are downstream of their preflight checks; the background/effect readers are protected by the core check. Historical measurement scripts still contain independent readers, including [`optimizer_disagreement_targets.js`](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/scripts/optimizer_disagreement_targets.js:37).

Validation: **74 focused JavaScript tests and 42 Python tests passed**. Six JavaScript mutations failed the intended tests. Read-only, in-memory session probes confirmed plain 400s for 40 invalid combinations across all five API routes; valid/absent fit backgrounds matched exactly. Browser integration was not run; broader JavaScript testing encountered sandbox temporary-directory failures. No files changed.

**VERDICT: NO-GO**
