# Codex review — fit_full_window opt-in feature — ROUND 3 RECHECK RUN B (2026-07-13)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/fit_full_window_recheck2_prompt.txt (recheck of round 2's two new findings)

**Findings**: None.

Verified the two round-2 fixes against current disk state at a9e2b0e:
- `match_components_to_slots()` still uses widened bounds only in `_accepts()` via `bound_overrides` (engine.py:1022). `_window_center()` now calls `_effective_be_window(slot, components)` with no override (engine.py:1029). For the 284.65 eV case, graphitic center is 284.4 (distance 0.25); aliphatic center is 285.0 (distance 0.35), so graphitic wins.
- `_proposal_blocked()` and `_detect_residual_proposals()` have no `fit_full_window`/`bound_overrides` parameters, and `compare_models()` calls `_detect_residual_proposals()` without them (engine.py:2829). `_proposal_blocked()` uses intrinsic effective windows only (engine.py:1924).
- The two new regressions target consuming code, not just helper output.
- Prior invariants rechecked: curated interior slots unchanged, linked slots excluded, offset ranges not widened, starting center/amplitude use `slot.be_window`, stability builds and matches against the same widened accept bounds, widening uses min/max so it cannot narrow or invert, `/api/fit` still calls `fitting.run_fit()` directly, `_detect_boundary_hits()` reads live lmfit bounds.

VERDICT: GO
