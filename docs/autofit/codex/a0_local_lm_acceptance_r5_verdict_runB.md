# Codex adversarial CODE review — unit A0 — round 5 (fourth recheck), RUN B (2026-09-15)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck4_prompt.txt
Branch state reviewed: 9090255. Outcome: NO-GO x2 — one MAJOR: the certificate probe scale read a stale working width left by the Jacobian loop. Dispositioned in a0_local_lm_acceptance_recheck5_prompt.txt (round 6).

Reviewed `origin/main..9090255` in full, including tests and archived dispositions. No files changed.

1. **MAJOR — The certificate can use a stale width and accept a point rejected by the stated oracle.** At [index.html:7361](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7361), `paramScale()` reads the mutable working peak. The Jacobian leaves that peak at its last perturbation; certification restores the baseline only **after** probing.

   Reproduction using the unmodified extracted functions:
   
   - Grid: **−50 to 50**, spacing **0.1**, zero background.
   - Data: two Gaussians, centers **−11.999999 and 12.000001**, each FWHM **15**, amplitude **1.28063417**.
   - Starting model: one Gaussian, center **0**, FWHM **15**, amplitude **1 locked**; center and width free.

   Returns **`success:true`, one iteration, zero accepted steps**, with the starting model unchanged.

   | Center probe | Relative RSS improvement |
   |---|---:|
   | Certificate’s stale-width probe: `−0.0149985` | `9.99850014e-7` |
   | Required oracle probe: `−0.015` | **`1.00005000e-6`** |
   | Positive probe: `+0.015` | `9.99783356e-7` |

   The committed `assertConstrainedStationary(..., 1e-6)` fails. The threshold excess is small, but this directly violates the explicit acceptance criterion. This defect predates the round-4 edits.

   Restore `applyParams(params)` before computing certificate scales, or derive scales from the candidate parameter vector. An in-memory baseline-restoration change made this reproduction take a certificate restart and subsequently pass the oracle.

All three round-4 dispositions are verified: both near-zero exits route through certification, failed gtol certification restarts the iteration, and code/documentation describe a coordinate check. Earlier sign, active-set, cutoff-removal, HTTP, batch-result, statistic-label, and scanner repairs remain present. The documented exclusions for model replacement and legacy provenance remain defensible.

Validation: **32 targeted tests passed** (the prompt says 34); **18/18 committed targets converged and passed the `1e-6` oracle**. The full JS run encountered Python temporary-directory failures in this read-only sandbox. Python/browser suite claims were not independently reproduced.

VERDICT: NO-GO — A stale working width changes the certificate’s center probe and reproducibly permits success at a point that fails the stated coordinate oracle.
