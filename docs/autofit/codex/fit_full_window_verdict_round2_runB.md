# Codex review — fit_full_window opt-in feature — ROUND 2 RECHECK RUN B (2026-07-13)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/fit_full_window_recheck_prompt.txt (recheck of round 1's two blockers)

No GO-blocking findings in the current disk state.

Verified the two dispositions in autofit/engine.py:413:
- Curated bound widening now cannot narrow or invert: for a touched low side, `min(original_lo, roi_lo) <= original_lo <= original_hi`; for a touched high side, `max(original_hi, roi_hi) >= original_hi >= original_lo`. Interior curated slots keep `(original_lo, original_hi)` exactly. Unassigned slots still intentionally use the full ROI.
- Stability matching now uses widened bounds via `_effective_be_window()` and `match_components_to_slots()`. One precision note: `run_stability_analysis()` builds the matching dict once, while `perturb_initial_params()` recomputes equivalent deterministic bounds from the same `model` and `x`; not the same dict object, but values cannot drift in this code path.
- Proposal blocking threaded consistently at the time of this review (later found wrong — see round 2 run A's finding #2, which this run missed).
- The regression test does exercise `run_stability_analysis()` and would plausibly catch the orphaning failure.
- Original invariants hold: linked slots excluded, offsets untouched, starting center/amplitude use original `be_window`, default False additive, `/api/fit` not wired, `_detect_boundary_hits()` reads live bounds.

VERDICT: GO (superseded by run A's NO-GO per the stricter-governs rule — see round 3 recheck)
