# Codex adversarial CODE review — unit A0 — round 4 (third recheck), RUN A (2026-09-15)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck3_prompt.txt
Branch state reviewed: f6dcf09. Outcome: NO-GO x2 — no BLOCKER; MAJOR: the two chi<1e-20 exits bypassed the certificate; MINOR: stale derivatives after a gtol certificate move; MINOR: state the certificate is a coordinate check. Dispositioned in a0_local_lm_acceptance_recheck4_prompt.txt (round 5).

Reviewed the full diff through `f6dcf09`, tests, and archived dispositions. No files changed.

1. **MAJOR — Two success paths bypass the certificate and fail the committed oracle.**  
   Both the [initial convergence check](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7404) and [accepted-step check](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7499) accept `chi < 1e-20` without calling `certify()`.

   Reproduction using the unmodified extracted functions: grid **283–287 eV, spacing 0.01**; background and background-subtracted data both zero; one Gaussian with **FWHM 1, amplitude 1**, both locked, and center free.

   | Starting center | Returned success | Final center | RSS before → after center −0.001 |
   |---|---|---|---|
   | 280 | 0 iterations | 280 | `7.420096e-22 → 7.175270e-22` |
   | 280.5 | 432 iterations | 280.078521748 | `9.992631e-21 → 9.671261e-21` |

   These feasible oracle-sized moves improve RSS by **3.30% and 3.22%**, respectively. Both fail `assertConstrainedStationary(..., 1e-6)`.

   The absolute errors are negligible; this is a concrete violation of the explicitly relative acceptance contract, not evidence of materially bad experimental fits. Require certification on both nonzero-RSS exits, or explicitly document and test an absolute-tolerance exception.

2. **MINOR — A rejected gtol certificate continues with stale derivatives.**  
   At the [gtol gate](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7468), `certify()` can change `params` and `chi`, but execution then builds the step using `JtJ`, `Jtr`, and the active set computed at the previous point. The predicted reduction consequently describes a different starting point.

   I exercised this branch with a center-only Gaussian fitting symmetric double-peak data. That reproduction ultimately converged, so this is not an independently demonstrated false-success defect. After an unsuccessful certificate, `continue` to recompute the residual, Jacobian, and active set.

3. **MINOR — The certificate supports the stated coordinate-probe guarantee, not a general local-minimum guarantee.**  
   Excluding coupled probes is acceptable for the explicitly narrowed acceptance rule. However, LM’s coupled step does not eliminate the limitation.

   Concrete example: grid **−3–3, spacing 0.01**; data comprise two Gaussians at **±0.3**, each amplitude **10**, FWHM **1**. Start both centers at **0**, with amplitudes and widths locked. The fitter succeeds after one iteration and passes the coordinate oracle. Moving the centers together to **−0.001/+0.001** lowers RSS from **1148.3888323 to 1148.3606542**, a relative improvement of **2.4537e-5**. This satisfies the stated acceptance rule despite an available coupled improvement. Keep the documentation precise about what “stationary” means here.

The round-3 removals and oracle extensions are present; the four regression tests pass, and `undetermined` is gone. **58 focused/structural JS tests passed.** All **18 committed targets** converged in **5–288 iterations** and passed the oracle at `1e-6`. Seventeen needed no certificate restart; one needed one. These replays show no material certificate-related performance problem. Python/browser suites were not rerun.

VERDICT: NO-GO — Two nonzero-residual success paths bypass certification and demonstrably violate the stated single-parameter acceptance criterion.
