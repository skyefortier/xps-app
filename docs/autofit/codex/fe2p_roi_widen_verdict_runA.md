# Codex review — Find Peaks Fe 2p ROI-widen fix (commit b205f73) — RUN A (2026-07-13)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 141,781.
Prompt: docs/autofit/codex/fe2p_roi_widen_review_prompt.txt

No NO-GO findings.

I verified the root cause and fix direction against disk. Pre-fix `HEAD^` used `expected_region_ev` whenever present and skipped the nominal margin entirely, so Fe 2p auto-filled to `706.5..711`. Current `_sourced_roi()` checks `component_labels <= covered_orbitals` and widens only when the sourced positions do not cover the full derived component set: [coverage_index.py](/Users/skyefortier/xps-verify/autofit/coverage_index.py:106). The call site passes the full level component labels from `lv["components"]`: [coverage_index.py](/Users/skyefortier/xps-verify/autofit/coverage_index.py:198).

The widening is union-only. It computes the source span, then applies `lo = min(lo, widened_lo)` / `hi = max(hi, widened_hi)`, so it cannot shrink an already-wide ROI: [coverage_index.py](/Users/skyefortier/xps-verify/autofit/coverage_index.py:132). No spin-orbit splitting, partner BE, or citation is invented; it reuses the existing nominal `± 12.0 eV` practical margin documented in the module: [coverage_index.py](/Users/skyefortier/xps-verify/autofit/coverage_index.py:51).

Independent data check: `data/xps/elements-machine.json` has Fe `2p3/2` only, nominal `706.86`, expected region `706.5..711`, and no `2p1/2`: [elements-machine.json](/Users/skyefortier/xps-verify/data/xps/elements-machine.json:431). With margin `12.0`, the widened ROI is `694.9..718.9`; the old ROI would fail both new test assertions. Mg 2p and Al 2p similarly widen from `49.8..49.8` to `37.8..61.8`, and `71.8..73.0` to `60.9..84.9`.

Scope checks also look right. Singlets are effectively exempt because their single derived label matches the sourced orbital; fully-covered non-curated doublets I found (`Cu 2p`, `Nb 3d`) satisfy `component_labels <= covered`, so they keep the expected-region union. I found no shrink path across sourced records. The changed commit touches only `autofit/coverage_index.py`, `tests/autofit/test_coverage_index.py`, and the review prompt doc; `/api/fit` remains separate, while `coverage_index` is imported only by `/api/analyze/meta`: [app.py](/Users/skyefortier/xps-verify/app.py:738), [app.py](/Users/skyefortier/xps-verify/app.py:858). The UI copies that meta ROI into Find Peaks inputs only on single-region selection: [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:13290).

I could not run pytest in this sandbox: `pytest` is unavailable and system Python lacks `jsonschema`, so `region_coverage_index()` cannot execute end-to-end here. I did statically trace the tests and independently re-derived the failing pre-fix numbers from JSON.

VERDICT: GO
