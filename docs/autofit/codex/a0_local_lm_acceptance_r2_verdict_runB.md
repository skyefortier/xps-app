# Codex adversarial CODE review — unit A0 — round 2 (recheck), RUN B (2026-09-15)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck_prompt.txt
Branch state reviewed: 01a0e66. Outcome: NO-GO x2 — one surviving BLOCKER (clipped joint step lets a tiny agreed step pass ftol at a non-stationary point; needs a constrained/active-set step), upload null-body fallback, scanner/note/CLAUDE.md wording. Dispositioned in a0_local_lm_acceptance_recheck2_prompt.txt (round 3).

Reviewed `origin/main..01a0e66`; no files changed.

1. **BLOCKER — Round-1 finding 2 survives: the new ftol gate accepts materially non-stationary fits.** At [index.html:7454](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7454), agreement between actual and predicted reductions describes the **clipped step**, not whether a useful feasible descent direction remains.

   Reproduction using the unmodified extracted functions: grid 283–287 eV, spacing 0.01; Gaussian data centered at 285, FWHM 1, amplitude 0.5; model center locked at 285, initial FWHM 1.5 and amplitude 5, both free. Returns **success after 20 iterations**, amplitude 1, FWHM **0.99999898**, residual SS **18.81726**. Keeping amplitude 1 and changing only FWHM to 0.51 gives **8.84307**, a **53% reduction**.

   Instrumentation shows `actred ≈ prered ≈ 2.45233e-7`, ratio approximately 1, but projected gradient cosine **0.57735**, versus `GTOL=1e-6`. The unconstrained solve proposes movement through the amplitude wall; clipping leaves an ineffective width step. Thus **yes, FTOL=1e-6 admits the failure asked about in question (b)**. An in-memory change to FTOL=1e-8 escapes this particular premature stop. The required repair is credible termination for the constrained problem—such as solving with blocked variables held fixed—not merely reduction agreement. Add this regression.

2. **MAJOR — Upload response validation still permits unintended fallback.** [uploadToBackend:6165](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:6165) dereferences `json.error` before checking whether the parsed body is an object. An **HTTP 200 containing JSON `null`** throws TypeError; [runFit:7111](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7111) classifies it as transport failure. Replayed with the actual upload function: **local fallback called once**. The promised missing-session server-error handling therefore remains incomplete. Validate the parsed response before accessing properties, and restrict transport classification to the fetch/body-reading operations.

3. **MINOR — Scanner overclaiming is reduced, not eliminated.** [Scanner:114](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/scripts/scan_batch_fit_signature.py:114) uses residual magnitude as a proxy for count level. Low-count server fits can have large residuals: `chiReduced=400`, `rmse=20` still produces **SUSPECTED**. This is tolerable for triage, but contradicts “low-count server fits … never SUSPECTED.” Output also still says **“copying is proven”** and **“Suspected tabs hold a local-optimiser result.”** Neither follows from the heuristic. Additionally, the no-hits caveat prints only when some candidate exists. Keep all diagnosis wording conditional and print that caveat unconditionally.

4. **MINOR — Maintainer documentation describes superseded termination rules.** [CLAUDE.md:246](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/CLAUDE.md:246) still specifies 1000 iterations, `1e-8` objective tolerance, and stalled-gradient termination. The implementation uses 3000 iterations, FTOL `1e-6`, and explicit stalled failure.

The other claimed repairs are present: correct bound-gradient sign, central differences and width-scaled center probes, sensitivity rejection, explicit damping-exhaustion failure, documented `caM` exclusion, HTTP-error checks before parsing, active-target result clearing, strict auto-fit success, statistic labels, and locked-parent synchronization.

**Item 5’s scope ruling is defensible** for this incident unit. Find Peaks, undo/redo, and legacy provenance remain real pre-existing gaps; they need their separate work, and A0 must not claim universal result integrity.

The **21 focused tests passed**. My batch replay confirmed **18/18 success in 5–288 iterations**; that does not establish stationarity, as finding 1 demonstrates. The full JS run encountered Python temporary-directory failures in this sandbox; Python/browser suite claims were not independently verified.

VERDICT: NO-GO — The revised convergence gate still certifies materially non-stationary fits, and malformed upload responses can still trigger unintended local fallback.
