# Codex review — candidate-generation layer + CWT ridge detector
*Run A, 2026-07-10, codex exec read-only, model_reasoning_effort=high, gtimeout 600 rails.  Prompt: candidate_pool_review_prompt.txt.*

**Findings**

1. MINOR: H0 calibration regeneration is not deterministic. The generator seeds H0 with Python `hash(...)`, which is randomized per process unless `PYTHONHASHSEED` is pinned, so a fresh regeneration may not reproduce the committed JSONL exactly. Use a stable digest or explicit integer seed formula. See [scripts/calibrate_cwt_detector.py](/Users/skyefortier/xps-app/scripts/calibrate_cwt_detector.py:88).

2. MINOR: The sensitivity-envelope prose is too broad for low-count cases. PROGRESS claims `sep >= 1.1xFWHM at ratio >= 0.15, all >= 8.5 prom_z`, but the committed JSONL has the 2000-count `1.1/0.15` case at 0/5 detections. The calibration doc’s low-count caveat is closer, but the “guaranteed envelope” sentence should explicitly scope the `1.1/0.15` claim to high counts. See [docs/autofit/PROGRESS.md](/Users/skyefortier/xps-app/docs/autofit/PROGRESS.md:2171), [docs/autofit/cwt-detector-calibration.md](/Users/skyefortier/xps-app/docs/autofit/cwt-detector-calibration.md:94), and [docs/autofit/inventory/cwt_calibration.jsonl](/Users/skyefortier/xps-app/docs/autofit/inventory/cwt_calibration.jsonl:806).

3. MINOR: The tests do not directly discriminate a curvature seeding path that ignores `below_fraction_of_max`. The code has the gate at [autofit/candidates.py](/Users/skyefortier/xps-app/autofit/candidates.py:556), and tests cover window gating, cap surfacing, gate-fails presence, short-input guards, and shoulder/no-local-max behavior, but I do not see a dedicated sub-0.25 curvature candidate assertion. This is a narrow test gap, not a runtime defect.

No BLOCKER or MAJOR findings. The runtime layering looks sound: `enable_preseed=False` disables the whole layer, pool construction is before `sweep_start`, pool-only FPs do not feed fitting, residual merge is payload-only post-sweep, descending grids are normalized in detector and pool paths, real ds7/ds8 data is untracked, and the committed JSONL supports the headline H0 FP and broad-peak claims. I could not run pytest due the read-only review constraint.

VERDICT: GO
