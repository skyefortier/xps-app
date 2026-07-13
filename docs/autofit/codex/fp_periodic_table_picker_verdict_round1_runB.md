# Codex review — Find Peaks periodic-table picker (unit 2) — ROUND 1 RUN B (2026-07-13)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 148,143.
Prompt: docs/autofit/codex/fp_periodic_table_picker_review_prompt.txt

**Findings**

No blocking issues found in the current worktree replacement.

Key checks:
- Current dirty diff is scoped to `autofit/coverage_index.py`, `templates/index.html`, and tests. `/api/fit` is not touched by the replacement; `region_coverage_index()` is consumed by `/api/analyze/meta` in [app.py](/Users/skyefortier/xps-verify/app.py:858).
- `practical` is additive and present on all coverage entry paths in [coverage_index.py](/Users/skyefortier/xps-verify/autofit/coverage_index.py:176), [coverage_index.py](/Users/skyefortier/xps-verify/autofit/coverage_index.py:189), [coverage_index.py](/Users/skyefortier/xps-verify/autofit/coverage_index.py:203), and [coverage_index.py](/Users/skyefortier/xps-verify/autofit/coverage_index.py:220).
- Selection state is not rebuilt from rendered DOM. `_fpToggleRegion()` updates `_fpRegionsSelected` through `_fpNextSelection()`, `_fpSyncSelectionUI()` only reads that Set, and `runFindPeaks()` submits `Array.from(_fpRegionsSelected)`.
- Exact grep found no remaining removed `#fp-regions` select, `_fpRenderRegionOptions`, `_fpRegionsChanged`, or `selectedOptions` references in `templates/index.html`/`tests`.
- Honesty rail looks intact: grid/chips/search use `_fpMeta.coverage` entries, chip text includes tier tags, tooltip text includes tier wording, legend carries tier wording, and ROI fill only uses `entries[0].roi`.
- Accessibility basics for grid cells/chips are present: Enter/Space handlers, focus-visible outlines, `aria-expanded` on cells and `aria-pressed` on chips.

**Note**: this run did NOT catch run A's finding (the search-dropdown-item keydown handler only wired `Enter`, not `Space`, and its `:focus-visible` rule removed the outline). Per this project's "stricter verdict governs" convention, run A's NO-GO is the operative verdict for round 1; see the round-2 recheck for disposition.

Runtime checks:
- JS tests passed: `node --test tests/js/find_peaks_periodic_table.test.js tests/js/find_peaks_coverage.test.js` showed 28/28 passing.
- Python pytest could not run in this shell: `pytest` is not installed and system `python3` lacks `jsonschema`. Spot-checked the practical heuristic with a local no-op `jsonschema` stub: `region_coverage_index()` returned H 1s false, Fe 1s false, Fe 2p/2s/3p/4s true, Fe 3d false, Mg 2p true, U 1s false, U 4f true.

VERDICT: GO (superseded by run A's NO-GO per the stricter-governs rule — see round 2 recheck)
