# Codex review — fit_full_window opt-in feature — ROUND 3 RECHECK RUN A (2026-07-13)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/fit_full_window_recheck2_prompt.txt (recheck of round 2's two new findings)

No findings.

Verified on current disk at commit a9e2b0e:
- autofit/engine.py:1022: `_accepts()` still uses `bound_overrides` for widened acceptance.
- autofit/engine.py:1029: `_window_center()` no longer receives or passes an override. In the 284.65 eV case, graphitic center is 284.4, aliphatic center is 285.0, so graphitic wins.
- autofit/engine.py:1924: `_proposal_blocked()` has no full-window parameter and uses intrinsic slot windows only.
- autofit/engine.py:1970: `_detect_residual_proposals()` has no full-window parameter, and its `compare_models()` call site passes none.
- tests/autofit/test_fit_full_window_option.py:278: both new regression tests exist and exercise the consuming code paths, not just helper output.
- Prior invariants still hold: curated interiors remain exact, linked offsets untouched, initial center/amplitude estimation uses original `be_window`, stability acceptance uses widened bounds, `/api/fit` and manual Run Fit untouched, `_detect_boundary_hits()` reads live lmfit bounds.

VERDICT: GO
