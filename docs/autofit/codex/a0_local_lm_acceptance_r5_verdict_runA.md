# Codex adversarial CODE review — unit A0 — round 5 (fourth recheck), RUN A (2026-09-15)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck4_prompt.txt
Branch state reviewed: 9090255. Outcome: NO-GO x2 — one MAJOR: the certificate probe scale read a stale working width left by the Jacobian loop. Dispositioned in a0_local_lm_acceptance_recheck5_prompt.txt (round 6).

1. **MAJOR — The certificate can use a stale width and accept a point that fails its coordinate oracle.**  
   [The Jacobian calculation](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7431) leaves `work` at its last perturbed point. At the gtol exit, [certify()](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7355) reads that working width through `paramScale` before restoring the current parameters.

   Reproduced with the unmodified extracted functions:
   - Grid **−3…3, spacing 0.01**, zero background.
   - One LACX peak: center **0.00599995**, FWHM **1**, amplitude **10**, `caAlpha=0.5`, `caBeta=2`, `caM=10`. Only center and width free.
   - Positive synthetic data constructed as `y = m + 10(I−P)d`, where `m` is the starting model, `d = model(center−0.001)−m`, and `P` projects onto the two centered model-difference columns for center and width, using **±0.0001**.

   The fitter returns **success after one iteration, zero accepted steps**, with unchanged parameters. The committed oracle fails:

   | Probe | RSS |
   |---|---:|
   | Starting model | 0.9763977983 |
   | Certificate’s incorrect center move, −0.0009999 | 0.9938116141 |
   | Required center move, −0.001 | **0.8188950706** |

   The required move improves RSS by **16.131%**. LACX’s nearest-grid normalization makes the two probes cross different sides of a discontinuity. Every synthetic data value is positive.

   Restore `work` from `params` before calculating certificate scales, or derive scales directly from the current parameter vector. An in-memory `applyParams(params)` at certificate entry eliminates this false success; the reproduction then reports non-convergence. Add this regression.

All three round-4 dispositions are correctly implemented: the absolute-residual bypasses are removed, failed gtol certificates restart derivative construction, and the coordinate-only limitation is documented. The finding above predates those changes; I found no separate regression introduced by round 4. Earlier repaired findings remain closed; the explicitly deferred Find Peaks, undo/redo, and legacy-provenance gaps remain outside A0.

Validation: **32 targeted tests passed**—not 34. Independently replayed **18/18 batch targets**, all passing the `1e-6` oracle. The scanner reproduced two suspected tabs. Full JS execution yielded **205 passes, 12 temporary-directory-related failures, and 3 TODOs**. Python/browser suites were not independently rerun. No files changed.

VERDICT: NO-GO — A stale width changes the certificate’s center probe, allowing success where the required single-parameter move reduces RSS by 16.131%.
