# Codex adversarial CODE review — unit A0 — round 4 (third recheck), RUN B (2026-09-15)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck3_prompt.txt
Branch state reviewed: f6dcf09. Outcome: NO-GO x2 — no BLOCKER; MAJOR: the two chi<1e-20 exits bypassed the certificate; MINOR: stale derivatives after a gtol certificate move; MINOR: state the certificate is a coordinate check. Dispositioned in a0_local_lm_acceptance_recheck4_prompt.txt (round 5).

1. **MAJOR — Two success paths bypass the certificate.** Both the [initial convergence flag](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7404) and the [accepted-step exit](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7499) accept `chi < 1e-20` without calling `certify()`.

   Reproductions using the unmodified extracted functions: grid **280–281 eV, spacing 0.05**, zero background, one Gaussian, **FWHM 2**, center/width locked, amplitude free and initially **1**.

   | Center | Data amplitude | Returned result | Permitted amplitude probe |
   |---|---|---|---|
   | 287 | 2 | Success, **0 iterations**, amplitude unchanged | `1 → 1.001`: RSS **3.725033e-22 → 3.717587e-22**, relative reduction **0.001999** |
   | 286 | 3 | Success, **1 accepted step**, amplitude **2.9980019980024233** | Multiply amplitude by `1.001`: RSS **7.020492e-21 → 1.758635e-21**, relative reduction **0.74949975** |

   Both exceed `1e-6`; the committed oracle rejects the first reproduction. These are tiny absolute errors, but explicit counterexamples to the promised relative acceptance criterion. Route both shortcuts through the certificate and add regressions for both exits.

2. **MINOR — A rejected gtol certificate continues with stale derivatives.** At [the gtol branch](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7468), `certify()` can change `params` and `chi`, then return false. Execution immediately solves using `Jtr`, `JtJ`, and the active set calculated at the previous point. The resulting step and predicted reduction therefore refer to different starting points. Restart the iteration after this certificate move so derivatives are rebuilt. Subsequent acceptance checks limit the consequence, but this is a new numerical inconsistency.

3. **MINOR — “Stationarity certificate” needs the stated operational qualification.** The fixed coordinate probes are acceptable for the explicitly defined acceptance rule. They do **not** establish mathematical stationarity, exclude smaller improving moves, or exclude coupled descent directions. LM’s coupled steps help optimization but do not certify those omissions at termination. That limitation alone is not an additional release blocker under the narrowed guarantee.

The other round-3 dispositions check out: the column cutoff, Newton gate, and `undetermined` field are gone; DS/DS+G oracle enumeration and linked synchronization are present. All **58 focused/structural/batch JS tests passed**. Independently replayed **18/18 targets** converged in **5–288 iterations**, and all passed the `1e-6` oracle. Those replays required zero certificate restarts except one target requiring one; no material certificate-performance problem appeared. Python/browser suites were not rerun.

VERDICT: NO-GO — Both absolute-residual success shortcuts bypass the certificate and reproducibly accept points that fail the stated feasible-descent criterion.
