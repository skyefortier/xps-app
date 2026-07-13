# Codex review — fit_full_window opt-in feature — ROUND 2 RECHECK RUN A (2026-07-13)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/fit_full_window_recheck_prompt.txt (recheck of round 1's two blockers)

**Findings**

1. autofit/engine.py:1029: `match_components_to_slots()` now uses the widened effective window center for disambiguation. That can relabel a component into a neighboring slot even when it is still inside its original literature window. Example: C 1s graphitic `(284.0, 284.8)` widened low to ROI `270..300`, adjacent aliphatic `(284.6, 285.4)`, fitted component at `284.65`. It is accepted by both, but graphitic's widened center becomes `277.4`, so the disambiguation chooses aliphatic. This can tank graphitic persistence in stability. Acceptance needs widened bounds; identity tie-breaking should stay anchored to the original slot window.

2. autofit/engine.py:1947: proposal blocking now uses full-window overrides for populated `region == "unassigned"` slots. Since `_full_window_bound_overrides()` maps unassigned primary slots to the full ROI, any accepted proposal/preseed/detection slot blocks every later residual proposal in the ROI when `fit_full_window=True`. That breaks the documented iterative proposal behavior (`PROPOSAL_MAX_PER_CANDIDATE = 3`) under this option.

**Verified**

Run 2's curated-bound fix (min/max wrapping) is correct: cannot narrow or invert the touched side. Interior curated slots and linked slots remain untouched. Run 1's direct orphaning bug is mostly dispositioned: `run_stability_analysis()` computes bound overrides once for matching, and refit params are built with equivalent deterministic overrides. The new stability regression test does call `run_stability_analysis()` directly. Flag threading, `/api/fit` isolation, and `_detect_boundary_hits()` all confirmed correct.

VERDICT: NO-GO
