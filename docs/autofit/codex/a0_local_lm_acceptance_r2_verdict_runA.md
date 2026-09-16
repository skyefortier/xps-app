# Codex adversarial CODE review — unit A0 — round 2 (recheck), RUN A (2026-09-15)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck_prompt.txt
Branch state reviewed: 01a0e66. Outcome: NO-GO x2 — one surviving BLOCKER (clipped joint step lets a tiny agreed step pass ftol at a non-stationary point; needs a constrained/active-set step), upload null-body fallback, scanner/note/CLAUDE.md wording. Dispositioned in a0_local_lm_acceptance_recheck2_prompt.txt (round 3).

Reviewed `origin/main..01a0e66` in full, including tests. No files changed.

1. **BLOCKER — Round-1 finding 2 survives: tiny, accurately predicted steps still produce false convergence.**  
   The [termination test](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7454) accepts small actual/predicted reductions despite a substantial feasible gradient.

   Reproduction using the extracted shipped functions: grid **283–287 eV, spacing 0.01**; Gaussian data with **center 285, FWHM 0.3, amplitude 1**; starting model **center 284, FWHM 0.3, amplitude 1**, all three parameters free.

   It returns `success:true` after **15 iterations**, at center **284.000002944**, FWHM **0.299035048**, amplitude **1**. At termination:
   - Actual relative reduction: **3.893157e-7**.
   - Predicted relative reduction: **3.893149e-7**—excellent agreement.
   - Feasible gradient cosine: **0.407917**, versus `GTOL=1e-6`.
   - Reducing only FWHM to **0.1** lowers RSS from **45.08887 to 30.10767**, a **33.2%** improvement.

   The [normal-equation solve](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7431) retains blocked parameters, then clips the resulting step. Agreement describes that ineffective step; it does not establish constrained stationarity. Changing FTOL to `1e-8` still falsely succeeds after 150 iterations. This requires a constrained-step or stationarity safeguard, not merely a tighter tolerance.

   The replacement test also explicitly accepts `prered <= 0`. Starting the same example at FWHM **0.5** succeeds with **negative predicted reduction** and gradient cosine **0.451**. That is an additional defect in the new “agreement” gate.

2. **MINOR — Upload error classification remains incomplete for malformed successful responses.**  
   In [uploadToBackend](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:6166), HTTP 200 with valid JSON `null` throws at `json.error`, before the missing-session guard. The enclosing `TypeError` classification then invokes local fallback. I reproduced this with the real extracted upload function.

   Validate the parsed response before dereferencing it, and classify transport exceptions at their originating operations. The specified HTTP 502, HTML-body, error-object and missing-session-object cases are fixed.

3. **MINOR — Scanner and recovery wording still exceed the evidence.**  
   The scanner’s levels are substantially improved, and the repository scan reproduces **two suspected tabs, zero unreadable files**. However:
   - [Identical models](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/scripts/scan_batch_fit_signature.py:130) still claim “copying is proven”; identical locked models need not establish copying.
   - [Nonexistent input paths](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/scripts/scan_batch_fit_signature.py:143) silently produce exit **0**, with zero files scanned.
   - The no-hits caveat is [printed only when hits exist](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/scripts/scan_batch_fit_signature.py:176).
   - The [student note](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/docs/comms/2026-09-15-batch-fit-student-note.md:43) still promises that the scanner catches fallback results and that backend non-convergence appears as an unusually poor fit. Neither is guaranteed.

4. **MINOR — Scope disposition 5 is defensible, but the documented guarantee should match it.**  
   Deferring pre-existing Find Peaks, undo/redo and legacy-provenance problems is acceptable for this incident unit. They need separate model/result consistency work; they do not justify blocking A0 independently.

   [CLAUDE.md](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/CLAUDE.md:245) nevertheless states a universal acceptance guarantee and retains obsolete **1000 iterations / `1e-8` / stalled-gradient** descriptions. Narrow and update those claims.

5. **MINOR — Regression coverage improves substantially but misses the surviving blocker.**  
   Verified the gradient-sign repair, central differences, width-scaled center probes, explicit stall failure, sensitivity guard, documented `caM` treatment, active-target reset, strict auto-fit success gate, three statistic-label repairs, and locked-parent synchronization. Existing boundary tests vary amplitude alone; they miss coupled free parameters at a bound.

   All **21 targeted JS tests pass**. All **18 committed targets report success in 5–288 iterations**; this does not establish optimality. Full JS execution produced **194 passes, 12 failures from unavailable writable temporary directories, and 3 TODOs**. Python/browser-suite claims and the backend comparison were not independently reproduced.

VERDICT: NO-GO — The local optimizer still commits materially non-stationary models as converged despite near-perfect actual/predicted reduction agreement.
