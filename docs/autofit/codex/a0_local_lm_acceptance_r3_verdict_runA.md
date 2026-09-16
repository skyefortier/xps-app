# Codex adversarial CODE review — unit A0 — round 3 (second recheck), RUN A (2026-09-15)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck2_prompt.txt
Branch state reviewed: b105606. Outcome: NO-GO x2 — the 1e-4 column-norm cutoff froze determined satellites; the undamped-Newton ftol gate still passed points where a 1e-3 scaled move gained > 1e-6. Dispositioned in a0_local_lm_acceptance_recheck3_prompt.txt (round 4): both mechanisms removed, replaced by an explicit feasible-descent certificate.

Reviewed `origin/main..b105606` in full, including tests and archived verdicts. No files changed.

1. **BLOCKER — The new “undetermined” cutoff can freeze a clearly determined satellite and accept the unchanged starting model.**  
   The [column cutoff and active-only gradient check](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7435) reproduce this with the unmodified extracted functions:

   Grid **280–300 eV, spacing 0.05**, zero background, two Gaussians, both FWHM **1**, all parameters free. Data: main peak **center 285, amplitude 100,000**; satellite **center 295, amplitude 1,000**. Start at those values except satellite amplitude **1**.

   Result: **`success:true`, one iteration, zero accepted steps**. All three satellite parameters are reported as undetermined. Moving satellite amplitude from **1 to 1.001** reduces RSS from **15,023,744.335710** to **15,023,714.258159**: relative reduction **2.002001e-6**, exceeding the requested threshold.

   Locking the already-correct main peak makes the same satellite converge to amplitude **1,000 in seven iterations**. Its amplitude derivative is measurable; exclusion depends on another component’s scale and the satellite’s starting amplitude. A relative column-norm cutoff does not establish non-identifiability or finite-difference failure, and is not generally equivalent to an SVD cutoff. Reporting the exclusion does not make the convergence claim valid. Held continuous parameters need a feasible-descent check before success.

2. **BLOCKER — The undamped Gauss–Newton prediction gate still accepts a non-stationary point without any “undetermined” parameters.**  
   The [ftol gate](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7480) fails this independent replay:

   Grid **283–287 eV, spacing 0.01**, zero background. Gaussian data: **center 285, FWHM 1.5, amplitude 0.1**. Starting Gaussian: **center 285.3, FWHM 1, amplitude 8**, all three parameters free.

   The unmodified function returns success after **1,756 iterations**, at **center 285.031691905, FWHM 0.1, amplitude 1**, with `undetermined: []`. Decreasing center by **0.0001 eV**—exactly the oracle’s scaled `1e-3` move—reduces RSS from **6.534343640417** to **6.534327168831**, a relative reduction of **2.520771e-6**.

   Diagnostic instrumentation identifies **ftol**, with actual reduction **9.99804e-7**, predicted reduction **5.00213e-7**, and undamped prediction **5.00214e-7**. Gradient cosine remains **7.07258e-4**, versus `GTOL=1e-6`. Removing damping does not make the linearized residual model a sufficient stationarity certificate. The round-2 examples are repaired, but the blocker survives.

3. **MINOR — The claimed generic stationarity oracle omits supported continuous parameters.**  
   [freeParamsOf](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/tests/js/local_lm_descent.test.js:253) omits `DS.dsAlpha/dsGamma` and `DSG_LA.laAlpha/laBeta/laM`, although the optimizer varies them. Linked-child perturbations also omit those shape parameters. Extend enumeration and synchronization, and add both reproductions above.

The other dispositions check out: upload null/non-object bodies are classified as server errors; scanner wording, missing-path exit **2**, and unconditional caveat are present; maintainer documentation and student-note wording are corrected. Deferring Find Peaks, undo/redo, and legacy provenance remains defensible.

**Validation:** 54 targeted JS tests passed. All 18 committed targets reported success in **5–532 iterations**; Scan_1 and Scan_4 report held **amplitude as well as width**, contrary to the width-only description. The scanner reproduced two suspected tabs and zero unreadable files. Python/browser suites were not rerun.

VERDICT: NO-GO — The optimizer still certifies non-stationary fits, both through the new sensitivity cutoff and through the undamped Gauss–Newton ftol gate.
