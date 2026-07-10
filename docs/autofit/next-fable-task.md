# Next Fable task — fix autofit CANDIDATE GENERATION (peak detection)

Saved 2026-07-08 for a future session.  **EXECUTED 2026-07-10 —
COMPLETE.**  See PROGRESS.md "Candidate-generation fix" sections (audit +
implementation + Codex trail, REVIEW-COMPLETE; detection/integration/
no-hallucination bars all passed).  Kept for the record; do not re-run.

```
/goal "Continue the XPS autofit engine on the current feature branch. FIRST read docs/autofit/PROGRESS.md. GOAL: fix CANDIDATE GENERATION (peak detection) — the real weakness. On a real C 1s spectrum the obvious shoulder at ~279.3 eV never entered the candidate pool, so no selection method (LS/IC/Bayesian/sparse) could recover it. Run Fit is NOT the problem and must not be constrained. Reframe: generate an OVERCOMPLETE, provenance-tagged candidate pool and let the EXISTING fitting/model-selection layer prune it. Detection proposes generously; selection judges.

SCOPE (tight):
1. AUDIT current Find Peaks candidate generation and DETERMINE why 279.3 was missed — do NOT presuppose. Possible causes: shoulder geometry, smoothing scale, detection threshold, baseline subtraction, energy-axis orientation, region crop, duplicate suppression, or a hard-coded width/amplitude rule. Find the actual cause and log it before fixing.
2. Build a PLUGGABLE candidate-generation layer, separate from Run Fit, merging proposals from multiple sources.
3. Add ONE detector first: prefer CWT ridge detection if the deps already exist (e.g. scipy) or it's cheap to add; otherwise Savitzky-Golay smoothed curvature. Do NOT implement both — a second detector only after the first passes acceptance. Never raw derivatives (extrema shift under overlap/asymmetry/baseline/noise); treat all detections as candidates to prune, not truth.
4. MERGE proposals from local maxima, the new curvature/CWT detector, residual gaps, and domain grammar, with duplicate suppression, into the overcomplete pool.
5. ATTACH PROVENANCE to every candidate (local_max, curvature_shoulder, residual_gap, grammar, ...), flowing to the honesty surface.
6. Let the EXISTING selection/fitting machinery prune the pool — detection must not try to output \"the true peaks.\"

ACCEPTANCE — separate bars, all proven by tests:
- DETECTION (the fix): on the real test_data/ scan, the ~279.3 feature ENTERS the candidate pool with provenance. This is THE bar for whether detection was fixed — keep it independent of selection.
- INTEGRATION (secondary): the existing selection layer then produces a sensible final model that includes it.
- NO HALLUCINATION: the overcomplete pool MAY hold false candidates by design; the rule is that negative controls gain NO spurious FINAL SELECTED peaks — any false candidate is pruned by selection or visibly flagged low-confidence. Tests: the exact 279.3 case + synthetic overlapping peaks, noisy negatives, broad peaks, baseline drift, close doublets.

RAILS: branch-only, additive, no merge/deploy/force-push. INVARIANT: do NOT change manual Run Fit behavior or the fit API contract (additive metadata / test-harness code near that boundary is fine; behavior and contract stay fixed). Keep neutral \"Suggested peak N\" labels. Commit AND push per unit; full suite green + zero regressions on synthetic suite and lab anchors; Codex ×2 (stricter governs, 10-min timeout then kill+log+proceed). Fourier self-deconvolution and further detectors are OUT OF SCOPE now (queued as later provenance sources). Work highest-impact-first and COMMIT each unit so a partial run still delivers. Keep PROGRESS.md current. Stop when the DETECTION + NO-HALLUCINATION bars pass + Codex-cleared, or you top out." --turns 500
```
