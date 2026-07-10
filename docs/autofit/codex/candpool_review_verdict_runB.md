# Codex review — candidate-generation layer + CWT ridge detector
*Run B, 2026-07-10, codex exec read-only, model_reasoning_effort=high, gtimeout 600 rails.  Prompt: candidate_pool_review_prompt.txt.*

Reviewed by reading code/artifacts only; pytest could not be run in this read-only sandbox.

1. **MAJOR** [scripts/calibrate_cwt_detector.py](/Users/skyefortier/xps-app/scripts/calibrate_cwt_detector.py:88) uses Python’s salted `hash(...)` to derive H0 RNG seeds, while the calibration doc presents the generator as the committed reproducer for `cwt_calibration.jsonl` ([docs/autofit/cwt-detector-calibration.md](/Users/skyefortier/xps-app/docs/autofit/cwt-detector-calibration.md:3)). Without a pinned `PYTHONHASHSEED`, regenerating the H0 battery can produce different spectra and therefore different q95/FP statistics. The committed JSONL itself does support q95=6.70, FP@7=3.7%, and broad spurious 0/20, but the generator is not independently reproducible. Fix by replacing `hash(...)` with a stable seed derivation, then regenerate/commit the evidence.

Non-finding checks: `/api/fit`, `fitting.py`, and frontend Run Fit are absent from the candidate-generation commit diff; `enable_preseed=False` leaves `candidate_pool` null; descending grids are normalized in detector and pool; residual merge only mutates payload post-fit; `autofit/` has no hard-coded 278/279/280 detector logic beyond an existing comment.

VERDICT: NO-GO
