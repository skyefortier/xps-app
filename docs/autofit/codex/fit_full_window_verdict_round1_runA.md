# Codex review — fit_full_window opt-in feature — ROUND 1 RUN A (2026-07-13)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/fit_full_window_review_prompt.txt

**Finding**

BLOCKER: widened curated fits are not accepted by the stability/identity layer. The optimizer bounds widen, but `run_stability_analysis()` still classifies refit components against the original `slot.be_window`.

Relevant path:
- `_effective_be_window()` returns `slot.be_window` for every primary slot: autofit/engine.py:978
- `match_components_to_slots()` only accepts a component if its fitted position is inside that effective window: autofit/engine.py:1000
- stability uses that matcher for every converged refit: autofit/engine.py:1161
- `rank_and_filter()` then rejects on `orphan_peaks` or low active persistence: autofit/engine.py:1593

Concrete failure scenario: with `fit_full_window=True`, a highest-BE curated primary slot can fit just above its original literature window, exactly as intended. But in stability, that same fitted component is outside `_effective_be_window()`, becomes an orphan, the slot's persistence stays low/zero, and the candidate is filtered or marked implausible.

**Checks That Passed**

The bound override rule itself matches the requested design: primary slots only, `region == "unassigned"` gets full ROI, curated slots get only lowest lower / highest upper widened, and interior curated slots keep exact original windows. Linked slots excluded correctly. Starting center/amplitude estimates stay anchored to `slot.be_window`. Threading through `compare_models()` looked complete for parameter construction. `_detect_boundary_hits()` reads live lmfit parameter bounds. Manual Run Fit `/api/fit` not touched.

VERDICT: NO-GO
