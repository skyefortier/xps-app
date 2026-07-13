# Codex review — Find Peaks periodic-table picker (unit 2) — ROUND 1 RUN A (2026-07-13)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 113,130.
Prompt: docs/autofit/codex/fp_periodic_table_picker_review_prompt.txt

**Finding**
- [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:13474): the type-ahead dropdown rows are focusable `role="button"` controls, but their key handler only activates on `Enter`; `Space` does nothing. [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:1356) also explicitly removes the focus outline for these focused rows. Concrete failure: a keyboard user types `Fe 2p`, tabs into the first search result, gets no visible focus indicator, and pressing Space does not select the result. Since the live search dropdown is a primary alternative selector path, this misses the accessibility bar.

**Verified**
- `/api/fit` and `runFit()` were not touched in the current worktree diff; `region_coverage_index()` is only wired through `/api/analyze/meta`.
- `practical` is additive on coverage entries; I did not see removed/renamed existing entry fields or `/api/fit` shape changes.
- `_fpRegionsSelected` remains the source of truth. I found no exact leftover `#fp-regions` select, `_fpRenderRegionOptions`, `_fpRegionsChanged`, or `selectedOptions` references in `templates/index.html` or tests.
- Grid/chip honesty looks sound: tiers come from `_fpMeta.coverage`, labels/tags/tooltips/legend carry tier meaning in words, and ROI fill only happens for a single selected entry with an existing `roi`.
- `_is_practically_fittable()` reads already-derived `st["configuration"]`, `lv["n"]`, and `lv["partially_filled"]`. Direct helper spot check: `H 1s=False`, `Fe 1s=False`, `Fe 2p/2s/3p/4s=True`, `Fe 3d=False`, `Mg 2p=True`, `U 1s=False`, `U 4f=True`.

**Tests**
- Passed: `node --test tests/js/find_peaks_periodic_table.test.js`.
- Could not run Python/Playwright tests in this environment: system Python lacks `jsonschema` and `pytest`; no local venv was present.

VERDICT: NO-GO
