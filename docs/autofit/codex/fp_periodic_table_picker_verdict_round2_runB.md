# Codex review — Find Peaks periodic-table picker (unit 2) — ROUND 2 RECHECK RUN B (2026-07-13)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 121,391.
Prompt: docs/autofit/codex/fp_periodic_table_picker_recheck_prompt.txt

No GO-blocking findings.

Run 1's finding is closed. Current [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:13475) builds search rows as focusable `role="button"` controls, and [line 13478](/Users/skyefortier/xps-verify/templates/index.html:13478) now handles both `Enter` and Space with `preventDefault()` before `_fpPickFromSearch(...)`. The focused row also has a real visible indicator at [line 1359](/Users/skyefortier/xps-verify/templates/index.html:1359): `outline: 2px solid var(--accent); outline-offset: -2px;`. The inset offset is appropriate here because the dropdown scroll container uses `overflow-y: auto`; keeping the outline inside avoids clipping and still gives a visible full-row focus ring.

The regression test exists at [tests/test_browser_find_peaks_coverage.py](/Users/skyefortier/xps-verify/tests/test_browser_find_peaks_coverage.py:203). It targets the dropdown item with `pg.focus("#fp-search-dropdown .fp-search-dropdown-item")`, sends `pg.keyboard.press(" ")`, and asserts `_fpRegionsSelected` changed, so it would catch the original Enter-only keydown bug.

The rest of the run 1 verified section still holds from inspection:
- `/api/fit` current route remains the manual `fitting.run_fit(...)` path at [app.py](/Users/skyefortier/xps-verify/app.py:740), while `region_coverage_index()` is only pulled into `/api/analyze/meta` at [app.py](/Users/skyefortier/xps-verify/app.py:858).
- `practical` is additive and present in all coverage entry construction paths at [autofit/coverage_index.py](/Users/skyefortier/xps-verify/autofit/coverage_index.py:184), [line 201](/Users/skyefortier/xps-verify/autofit/coverage_index.py:201), [line 212](/Users/skyefortier/xps-verify/autofit/coverage_index.py:212), and [line 232](/Users/skyefortier/xps-verify/autofit/coverage_index.py:232).
- `_fpRegionsSelected` is mutated through `_fpNextSelection` / `_fpToggleRegion`, and `runFindPeaks()` submits `Array.from(_fpRegionsSelected)` rather than scraping DOM state at [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:13675).
- Tier meaning is not color-only: legend text, tags like `[sourced]`, and grid/chip titles carry words.
- Spot values from `region_coverage_index()` with an in-memory `jsonschema` validator stub matched: H 1s / Fe 1s / Fe 3d / U 1s false; Fe 2p/2s/3p/4s, Mg 2p, U 4f true.

Verification run: `node --test tests/js/find_peaks_periodic_table.test.js` passed 11/11, and `git diff --check` was clean. pytest/Playwright unavailable in this sandbox.

VERDICT: GO
