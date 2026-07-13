# Codex review — fit_full_window opt-in feature — ROUND 1 RUN B (2026-07-13)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/fit_full_window_review_prompt.txt

**Finding**

BLOCKER: `_full_window_bound_overrides()` can tighten or even invert curated outer-slot bounds when `fit_full_window=True` and the selected ROI is not wider than the literature envelope. It assigns ROI edges directly instead of min/max-wrapping against the original bound.

Concrete failure: a C 1s candidate with a lowest slot window `(284.0, 285.0)` and ROI `287.0..300.0` gets center bounds `(287.0, 285.0)` for that slot — min > max, violating the stated "only ever widens" contract. The curated override should relax with `min(slot.be_window[0], roi_lo)` for the low outer slot and `max(slot.be_window[1], roi_hi)` for the high outer slot.

**Confirmed**

The intended outer-envelope logic is otherwise present: primary slots only, `region == "unassigned"` gets full ROI, curated interior slots keep both original bounds exactly in the normal wider-ROI case. Linked slots excluded. Starting center/amplitude estimates anchored to original `slot.be_window`. No missed fresh-parameter call inside `compare_models`. Default behavior additive. `_detect_boundary_hits()` reads live bounds. Manual `/api/fit` untouched.

VERDICT: NO-GO
