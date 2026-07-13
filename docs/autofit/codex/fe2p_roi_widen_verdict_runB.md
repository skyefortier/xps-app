# Codex review — Find Peaks Fe 2p ROI-widen fix (commit b205f73) — RUN B (2026-07-13)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 141,085.
Prompt: docs/autofit/codex/fe2p_roi_widen_review_prompt.txt

**Findings:** none for the ROI-widening fix.

I verified the failure path is ROI width, not fit budget/timeout. `/api/analyze/meta` exposes `region_coverage_index()` ([app.py](/Users/skyefortier/xps-verify/app.py:858)), the Find Peaks UI copies a single selected entry's `roi` into `roi-min/max` ([templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:13290)), and `/api/analyze` masks the spectrum to that ROI before structural fallback/detection runs ([app.py](/Users/skyefortier/xps-verify/app.py:261)). Structural fallback then depends on detected features; if the cropped window has none, `build_detection_candidate()` returns no model ([autofit/candidates.py](/Users/skyefortier/xps-verify/autofit/candidates.py:429)).

The subset direction is correct: current code detects partial coverage with `not component_labels <= covered_orbitals` ([autofit/coverage_index.py](/Users/skyefortier/xps-verify/autofit/coverage_index.py:125)). That matters for Fe 2p because the bridge has machine `2p3/2` plus a legacy generic `2p` marker, but no `2p1/2`; the reverse subset test would be wrong. The widening is a union only: `lo, hi = min(lo, widened_lo), max(hi, widened_hi)` ([autofit/coverage_index.py](/Users/skyefortier/xps-verify/autofit/coverage_index.py:137)), so an already-wide `expected_region_ev` cannot be narrowed.

I independently re-derived Fe 2p from data: machine `Fe-2p3/2` has nominal `706.86` and `expected_region_ev` `706.5-711` ([data/xps/elements-machine.json](/Users/skyefortier/xps-verify/data/xps/elements-machine.json:431)); the legacy generic marker is `2p` at `711` ([survey-lines.json](/Users/skyefortier/xps-verify/data/xps/legacy/survey-lines.json:419)). With `_NOMINAL_ROI_MARGIN_EV = 12.0`, current Fe 2p ROI becomes `694.9-723.0`, widened from the old `706.5-711`.

I could not run pytest normally because this sandbox lacks `pytest` and `jsonschema`. I traced and replicated the two new assertions with a minimal `jsonschema` stub: current code passes, and simulating the old `_sourced_roi()` produces 79 partial-multicomponent failures including Mg 2p, Al 2p, and Fe 2p. Singlets are effectively exempted by the same coverage check, and fully-covered doublets I found, such as Cu 2p, Nb 3d, and U 6p, keep the narrow source-recorded ROI.

Scope check: the committed ROI fix touches only `autofit/coverage_index.py`, the coverage-index test, and a review prompt doc. `/api/fit` remains the separate manual route at [app.py](/Users/skyefortier/xps-verify/app.py:738), and this change feeds only `/api/analyze/meta` coverage. Note: the current worktree has additional uncommitted `practical`-flag edits in the same files; they are separate from the committed ROI fix and also do not touch `/api/fit`.

VERDICT: GO
