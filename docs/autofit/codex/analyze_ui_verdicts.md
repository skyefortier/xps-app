# Codex verdict trail — analyze backend / Find Peaks UI / fit-physics wiring / BIC companions, 2026-07-05

Combined review of the units without a prior trail (run ×2; stricter
verdict governs). Prompts committed alongside
(`analyze_ui_wiring_review_prompt.txt`, `analyze_ui_recheck_prompt.txt`).

## Round 1 — combined review: NO-GO ×2
Blockers/highs (converged): `/api/analyze` 500-able on non-object JSON
body/roi/phase; Find Peaks apply destructive (no pushUndo — the UI's own
"undo-able" claim was FALSE) and the named review record was transient
(not serialized); `bic_weighted` used the absent-slot-adjusted k (letting
the heuristic shape the disagreement criterion that exists to expose it);
`filtered_dominant_alternative` could flag a promoted decisive-override
winner's own free original ("X" behind "X+bfix"). Mediums/lows:
fit-physics cross-checks compared only provenance prose (stale-prose
hole) and implied broader coverage than implemented; unescaped meta
option interpolation; non-finite floats emitted as invalid JSON.
Checked OK: exposure-only claim (candidate construction untouched),
/api/fit additive, corrected-frame convention consistency, lineshape
mapping, option pass-through, screenshots, and the 195-record JSONL
support for finding 9.

→ ALL FIXED (commit 5b4d099): dict validation (clean 400s, pinned);
pushUndo + per-peak durable `_findPeaks` review records (in-browser
re-verified: undoStack 0→1); full-k bic_weighted; promotion-lineage skip
(pinned on the measured sep-0.7 case: buried P3 may be named, promoted P2
never); resolved-slot cross-checks + narrowed claim; escapes;
non-finite→null sanitization (pinned).

## Round 2 — re-check: GO + NO-GO (stricter governs)
Run B: GO (all dispositions verified). Run A found the tail of the
validation surface: malformed option VALUES ({"n_refits": []}) raise
TypeError past the route's ValueError handler → 500; and `or {}`
swallowed present-but-falsy non-objects (roi: [], "", false) as omitted.
→ FIXED: (ValueError, TypeError) both handled as validation; missing
distinguished from present for roi/options/phase; pinned
(test_analyze_malformed_option_values_are_400s + falsy-variant cases).

## Round 3 — final narrow check: COULD NOT RUN (Codex quota exhausted)
Both attempts hit the Codex usage limit (reset 18:22). Logged per the run
rails (no verdict → kill + log + proceed). Standing evidence: round-2 run
B was a full GO; the two round-2 run-A findings are FIXED and pinned by
tests that run in the suite and in CI
(test_analyze_malformed_option_values_are_400s;
test_analyze_non_object_bodies_are_clean_400s truthy+falsy variants).
The narrow re-check prompt is preserved in the session scratchpad and in
this trail — re-run it when quota allows.
