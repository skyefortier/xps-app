# Codex re-check verdict — Stage 9 (resolution enhancement / MaxEnt slot), 2026-07-04

Re-check of the 6 Stage-9 dispositions (prompt: `stage9_recheck_prompt.txt`).

**Findings**

- **BLOCKER** [tests/autofit/test_max_entropy.py:67](/Users/skyefortier/xps-app/tests/autofit/test_max_entropy.py): residual MaxEnt claim remains in the tests: "MaxEnt inherently amplifies background noise." The implementation is now explicitly not MaxEnt, so this fails the "MaxEnt claims removed everywhere / tests pinned" disposition. Failure scenario: future readers still learn that this algorithm is MaxEnt-like rather than an iterative deconvolution slot. Fix: reword to "This iterative deconvolution..." or "resolution enhancement...".

- **MAJOR** [autofit/methods/max_entropy.py:130](/Users/skyefortier/xps-app/autofit/methods/max_entropy.py): emitted-spectrum χ² is only exact on the converged break path. If `max_iter` is exhausted, the loop computes `chi_r`, then updates `f`, exits, and reports the stale pre-update χ² with the post-update `sharpened_spectrum`. Failure scenario: unreachable target or low `max_iter` makes `reduced_chi_sq_reconvolution` not correspond to the emitted model, reopening the floor/χ² bookkeeping issue for nonconverged runs. Fix: recompute `model` and `chi_r` from final `f` after the loop before populating payload/diagnostics.

**Disposition check**

Items 3, 4, and 5 are closed in implementation: the warning includes "UNCALIBRATED" plus repeat-sweep recommendation, convolution is edge-normalized with `edge_margin_ev`, and the payload uses `negative_kl_to_flat`.

Item 6 is mostly closed: the new interior prominence/top-2 test catches prominent false peaks and the broad-kernel length bug is covered by rejecting kernels as wide as the spectrum. It still does not catch every non-max shoulder distortion, but it discriminates the specific local-maximum artifact failure mode named.

Could not run the focused tests: `pytest` is not installed, and direct import also fails in this environment because `lmfit` is missing.

VERDICT: NO-GO (blockers: residual MaxEnt claim remains in tests)
