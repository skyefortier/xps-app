# Find Peaks UI unit 3 (commit 07e685a, fix fa085f4) — Codex re-check verdicts (round 2)

## Run A
```
1. **FIXED CONFIRMED** — filtered-selection loss.  
   Evidence: [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:13267) now syncs only rendered options into `_fpRegionsSelected`; hidden selections are untouched. Deselection/toggle-off of a visible option is handled by the delete branch at [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:13276). `runFindPeaks()` now submits `Array.from(_fpRegionsSelected)` at [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:13431), and the request body carries `regions` at [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:13451). `openFindPeaksModal()` resets the Set at [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:13153), so no stale cross-open state. The new browser test reproduces the original mechanism and asserts both Set state and DOM checked state at [tests/test_browser_find_peaks_coverage.py](/Users/skyefortier/xps-verify/tests/test_browser_find_peaks_coverage.py:227). Pre-fix `07e685a` had `_fpRegionsSelected = new Set(values)` and DOM `selectedOptions` submit.

2. **FIXED CONFIRMED** — shallow-copy cache corruption.  
   Evidence: [autofit/coverage_index.py](/Users/skyefortier/xps-verify/autofit/coverage_index.py:119) and [autofit/coverage_index.py](/Users/skyefortier/xps-verify/autofit/coverage_index.py:181) both return `copy.deepcopy(...)`; no production `dict(e)` remains. `_curated_roi()` / `_sourced_roi()` return only `None` or plain JSON-safe dicts of numbers/strings at [autofit/coverage_index.py](/Users/skyefortier/xps-verify/autofit/coverage_index.py:67) and [autofit/coverage_index.py](/Users/skyefortier/xps-verify/autofit/coverage_index.py:77). The new test mutates a real nested `roi["be_min"]` at [tests/autofit/test_coverage_index.py](/Users/skyefortier/xps-verify/tests/autofit/test_coverage_index.py:133). Pre-fix `07e685a` returned `[dict(e) for e in ...]` on both paths, so this test would fail. Deep-copying ~980 small entries is not a meaningful `/api/analyze/meta` performance concern.

3. **FIXED CONFIRMED** — Fe 2p tier test permissiveness.  
   Evidence: exact `== "machine"` pins are now at [tests/autofit/test_coverage_index.py](/Users/skyefortier/xps-verify/tests/autofit/test_coverage_index.py:107) and [tests/test_api_analyze_coverage.py](/Users/skyefortier/xps-verify/tests/test_api_analyze_coverage.py:57); the old permissive `tier in ("machine", "structure_only")` pattern is gone from both test call sites. Independent data check: `data/xps/elements-machine.json` has Fe `2p3/2`, tier `machine`, nominal `706.86`, expected region `706.5-711`.

4. **FIXED CONFIRMED** — honesty-note browser-test permissiveness.  
   Evidence: assertion is now `re.search(r"not (a )?cited( fitting)? grammar", note.lower())` at [tests/test_browser_find_peaks_coverage.py](/Users/skyefortier/xps-verify/tests/test_browser_find_peaks_coverage.py:181). Real displayed text is built from `FP_TIER_META.machine.label` at [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:12832) plus backend note text at [autofit/coverage_index.py](/Users/skyefortier/xps-verify/autofit/coverage_index.py:143), and matches. The regex rejects `"sourced cited fitting grammar"` and `"Sourced position with cited fitting grammar"` because there is no negation. It would reject a future shortened `"not cited"` note, but the shipped text is not shaped that way.

5. **FIXED CONFIRMED / scope clean**.  
   `git show fa085f4 --stat` touches only `autofit/coverage_index.py`, `templates/index.html`, the three test files, `docs/autofit/PROGRESS.md`, and archived `docs/autofit/codex/` artifacts. No `app.py`, manual Run Fit, `/api/fit`, core math, or reviewed-apply gate drift.

6. **FIXED CONFIRMED** — PROGRESS memory-link artifact.  
   `[[xps-autofit-session-ops]]` is gone. Remaining `[[...]]` hits are unrelated prose/type examples: `[[none]]` and `Callable[[dict], None]]`.

VERDICT: GO

```

## Run B
```
1. **FIXED CONFIRMED — filtered-selection loss**  
   [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:13267): `_fpRegionsChanged()` now syncs only currently rendered options, adding selected rendered values and deleting rendered values that are no longer selected. Hidden selections are left untouched. `runFindPeaks()` now submits `Array.from(_fpRegionsSelected)` at [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:13431), so filtered-out co-fit members enter the request body. Deselect/toggle-off is handled by the delete branch for visible unselected options. `_fpRenderRegionOptions()` re-applies `selected` from the Set at [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:13257), so filter-clear/re-filter sequences remain coherent. The new browser test at [tests/test_browser_find_peaks_coverage.py](/Users/skyefortier/xps-verify/tests/test_browser_find_peaks_coverage.py:227) reproduces the original mechanism and asserts both Set preservation and checked DOM restoration. `git show 07e685a` confirms the old wholesale `new Set(selectedOptions)` and DOM-only `runFindPeaks()` bug.

2. **FIXED CONFIRMED — shallow-copy cache corruption**  
   [autofit/coverage_index.py](/Users/skyefortier/xps-verify/autofit/coverage_index.py:119) and [autofit/coverage_index.py](/Users/skyefortier/xps-verify/autofit/coverage_index.py:181) both return `copy.deepcopy(...)`; no live `dict(e)` remains in the implementation. `_curated_roi()` and `_sourced_roi()` return plain JSON-safe dicts or `None` at [autofit/coverage_index.py](/Users/skyefortier/xps-verify/autofit/coverage_index.py:67) and [autofit/coverage_index.py](/Users/skyefortier/xps-verify/autofit/coverage_index.py:77), so `deepcopy` protects the vulnerable nested `roi` dict. I directly seeded the cache and confirmed mutating a returned nested `roi` no longer corrupts the next result. The new test at [tests/autofit/test_coverage_index.py](/Users/skyefortier/xps-verify/tests/autofit/test_coverage_index.py:133) mutates real `roi["be_min"]`; the old `[dict(e) for e in ...]` version would fail that exact mutation. Performance risk looks negligible for about 980 small dicts.

3. **FIXED CONFIRMED — Fe 2p tier test permissiveness**  
   Both assertions are now exact `== "machine"` pins at [tests/autofit/test_coverage_index.py](/Users/skyefortier/xps-verify/tests/autofit/test_coverage_index.py:107) and [tests/test_api_analyze_coverage.py](/Users/skyefortier/xps-verify/tests/test_api_analyze_coverage.py:57). Grep finds the old permissive tuple only in explanatory comments, not assertions. Raw `data/xps/elements-machine.json` confirms Fe 2p is machine-tier with `expected_region_ev` 706.5-711 at [data/xps/elements-machine.json](/Users/skyefortier/xps-verify/data/xps/elements-machine.json:421); independent raw-data counting still gives 980 total / 5 curated / 111 machine / 864 structure-only.

4. **FIXED CONFIRMED — honesty-note browser-test permissiveness**  
   [tests/test_browser_find_peaks_coverage.py](/Users/skyefortier/xps-verify/tests/test_browser_find_peaks_coverage.py:181) now requires `not (a )?cited( fitting)? grammar`. The displayed note is built from `FP_TIER_META.machine.label` at [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:12833) plus backend note text via `_fpTierNoteFor()` at [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:12875); both shipped strings match the regex. A direct regex check rejects `"sourced cited fitting grammar"`. The regex would reject a future shorter `"not cited"` phrasing, but the current shipped text contains `grammar`, so this is not a current issue.

5. **FIXED CONFIRMED — scope check**  
   `git show fa085f4 --stat` / name-only touches only `autofit/coverage_index.py`, `templates/index.html`, the three test files, `docs/autofit/PROGRESS.md`, and archived `docs/autofit/codex/` artifacts. No drift into `app.py`, `/api/fit`, manual Run Fit, core math, or the honesty/reviewed-apply gate.

6. **FIXED CONFIRMED — PROGRESS.md memory-link artifact**  
   `docs/autofit/PROGRESS.md` no longer contains `[[xps-autofit-session-ops]]`; the relevant prose is clean at [docs/autofit/PROGRESS.md](/Users/skyefortier/xps-verify/docs/autofit/PROGRESS.md:2671). Grep for `[[` only finds unrelated text examples: `"[[none]]"` and `Callable[[dict], None]`.

I could not run full pytest in this read-only/missing-`jsonschema` environment, but the requested dispositions were re-derived from code, commit diffs, raw data, and read-only one-liners.

VERDICT: GO

```
