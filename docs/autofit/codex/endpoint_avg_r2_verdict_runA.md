# Endpoint averaging refusal — Codex round 2, run A (commit 8415dc7)

Reviewed `c643c5f..8415dc7`, focusing on the changes after `64c3376`. **Two blocking MAJOR findings remain.**

1. **MAJOR — Blank averaging still passes the in-flight fit checks.**  
   [`_captureUI`](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/templates/index.html:3868) converts blank to `"1"` before `_startsLiveKey` reaches the repaired canonicalizer.

   Using the actual capture/key functions, I reproduced `1 → blank` during upload: the server response was applied, “Fit complete” was announced, and the stored key recorded averaging `"1"`. With a transport failure, the local fitter ran instead. A completed fit likewise remains `current` after this edit, preserving statistics and save/export eligibility despite Run Fit refusing the field.

   Preserve the raw text through capture and key generation; default only an absent field. **Non-physical inputs: no**—clearing the field suffices.

2. **MAJOR — Saved numeric zero and blank still bypass the core refusal.**  
   [`_computeBackgroundForSource`](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/templates/index.html:10028) uses `endpointAvg || LEGACY_ENDPOINT_AVG`. Consequently, numeric `0` and `""` become 1 before validation. Similar defaults remain in [`_restoreUI`](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/templates/index.html:3888) and the spectrum loader.

   I exercised the actual restoration functions: records with numeric `0` or blank returned **`failure: null`, `stale: false`**. Direct core computation refuses both; stack/source reconstruction accepts both at `k=1`. Thus the readers still disagree and restored fits can remain current.

   Default only missing saved values. **Non-physical inputs: no**—ordinary spectra and saved numeric settings suffice. The additional Boolean variant is synthetic.

3. **MAJOR reader mismatch — Python’s twin is still inexact; log these synthetic cases under the owner’s rule.**  
   In [`page_endpoint_avg`](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/autofit/reference.py:358), I reproduced:

   | Saved text | Page | Python |
   |---|---|---|
   | 5,000 zeros followed by `3` | 3 | Integer-conversion-limit error |
   | `"\ufeff3\ufeff"` | 3 | Refused |
   | `"\u00853\u0085"` | Refused | 3 |
   | `"0x"` followed by 1,000 `f`s | Plain refusal | Uncaught `OverflowError` |

   Python `strip()` differs from JavaScript `trim()`, and the integer conversions introduce limits/overflow. **Non-physical inputs: yes, for these crafted spellings.** These are logged, not additional release blockers under the stated rule; catching radix-conversion overflow permits a one-line refusal.

Round-1 disposition:

| Finding | Round 2 |
|---|---|
| Fit-key aliasing/in-flight acceptance | **Partial:** exponent cases fixed; blank bypass remains |
| Restored fits and stack reconstruction | **Partial:** `"51"` refused; falsy saved values bypass |
| Direct engine and parity | Resolved |
| Saved-project Python reader | Ordinary cases resolved; synthetic discrepancies above |
| Batch mutation before refusal/blank bypass | Resolved: source preflight precedes target changes; global refusal correctly reports that the batch did not run |
| Archived Find Peaks coercion | Resolved |
| Auto-Fit/spinner test-proof defects | Resolved; corresponding mutations fail |
| Async analyze creates job before refusal | Resolved |

Compatibility checks found **456 bit-identical background comparisons against `main`**, covering valid 1–50 values, absent settings, and accepted spellings across eight methods. JSON `3.0` and NumPy integers passed. Auto-Fit’s post-shift recheck inherits the core refusal. Blank and disagreeing exponent spellings are intentionally newly refused by the design.

`parseInt(field) || 1` remains in both request builders and background internals, but their synchronous preflight/core checks protect accepted values. A pre-existing fixed-fixture [worked-example script](/Users/skyefortier/xps-app/.claude/worktrees/endpoint-avg/scripts/bg_window_worked_example.py:63) still uses generic `int(ui['endpointAvg'])`.

Validation: 220 JavaScript tests and 42 selected Python tests passed; one additional parity test was blocked by temporary-directory access. Seven in-memory mutations failed their relevant tests. All five HTTP entries produced plain 400 refusals in memory-backed probes. Harness default changes and quarter-window test substitutions are reasonable. Browser integration tests were not run. No files changed.

**VERDICT: NO-GO**
