# Codex adversarial CODE review — unit A0 (local LM descent + fit acceptance rule) — round 1, RUN A (2026-09-15)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_review_prompt.txt
Branch state reviewed: 7850ce7 (+ e6beb54). Outcome: NO-GO x2 — projected-gradient sign inverted; forward-difference step too coarse for centres; stall accepted as convergence; HTTP errors with non-JSON bodies reached the local fallback; already-active batch target kept a foreign live result; three chi-square label sites; scanner overclaimed. All dispositioned in a0_local_lm_acceptance_recheck_prompt.txt (round 2).

Reviewed the full diff through `7850ce7`, including the commit that landed during review. No files changed by me.

1. **BLOCKER — The projected-gradient test has the wrong sign and can accept the unchanged starting model.**  
   At [index.html:7370](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7370), `J` is the derivative of the residual, so `∂SS/∂p = 2 * Jtr`, not `-2 * Jtr`. The bound test consequently ignores feasible descent directions and retains blocked ones.

   Replayed with the extracted functions: Gaussian center/FWHM locked, amplitude initially **1**, data amplitude **10**. Result: **success, one iteration, zero accepted steps, amplitude still 1**. Conversely, data amplitude **0.5** makes amplitude 1 the legitimate constrained optimum, but the fitter reports failure after 24 iterations. Fix the gradient sign and test both boundary cases.

2. **BLOCKER — Accepted movement followed by stagnation does not establish convergence.**  
   The termination logic at [index.html:7392](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7392) accepts either a tiny improvement/step or excessive damping after *any* accepted step. Biased finite differences can satisfy these conditions far from stationarity.

   Concrete replay: grid 998–1002 eV at 0.005 eV spacing; Gaussian data centered at 1000, FWHM 0.3, amplitude 5; model FWHM/amplitude locked at 0.3/10, only center free:
   - Start 999.8: success after 28 iterations and three accepted steps, ending at **1000.013536**, with numerical objective derivative approximately **1878**.
   - Start 1000.2: success at **1000.069260**, residual SS **1450.70**, versus **1129.04** at the actual optimum—approximately **28.5% worse**.

   The finite-difference center increment is about 0.1 eV here. Being inside the parameter box does not make that derivative accurate. Require credible stationarity/termination evidence; otherwise report stalled non-convergence. The rounded `caM` parameter also needs explicit treatment: both finite-difference probes can round back to the same integer, producing a zero derivative without establishing optimality.

3. **MAJOR — HTTP server errors still reach the local fallback.**  
   [runFit:7113](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7113) parses JSON before checking HTTP status. A **502 HTML response** throws during parsing and is marked `transportFailure`; I reproduced the local fallback. [uploadToBackend:6154](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:6154) likewise parses first and never checks `resp.ok`.

   Check known HTTP failure status before letting body-parsing failures trigger fallback; parse its message opportunistically. Ordinary fetch rejection and `AbortError` correctly fall back. A 200 JSON object lacking `success` correctly fails without fallback. I found no reverse misclassification for ordinary native fetch/JSON exceptions, but the broad upload catch also incorrectly treats local preparation/programming errors as transport failures.

4. **MAJOR — Batch Fit can restore the previous result onto newly propagated peaks.**  
   [runPropagation:10896](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:10896) clears `tgt.fitResult`, but its already-active-target branch copies peaks/settings into live state **without clearing `state.fitResult`**. If fitting fails, `runFitLocal` correctly preserves that stale live result, and `_syncActiveToRecord()` writes it back onto the propagated model. The summary then says “NOT fitted” and “no result stored” despite a stored foreign result.

   Clear the live result in that branch and test an already-active target whose local attempt fails. The latest change to read summary statistics from the return value does not repair this.

5. **MAJOR — The acceptance rule is still incomplete across model replacement and restoration.**  
   The requested write-path audit is:

   | Path | Result |
   |---|---|
   | `runFit` → `applyBackendResult` → `state.fitResult` | Explicit boolean success gate now present; HTTP classification remains defective above. |
   | `runFitLocal` | Copy/commit isolation works, but its convergence decision is unsound above. |
   | `runPropagation` | Replaces target peaks before fitting; active-target result leak above. |
   | `runAutoFitC1sGraphite` → `applyAutoFitResult` | Rejects false/missing success and restores its snapshot on failure. Uses truthiness rather than the new exact-boolean contract; ordinary backend boolean responses are handled correctly. |
   | `applyFindPeaks` | Replaces peaks but clears the previous result **only when `fitFullWindow` is true**. Default application can retain another model’s curve, statistics and uncertainties. |
   | Undo/redo | Restores peaks alone, retaining the subsequent fit’s result. Undoing a successful fit therefore creates a mismatched peaks/result pair. |
   | History restore | Restores a matching saved peaks/result pair, but does not independently validate convergence or restore all fitting settings. |
   | Project/spectrum load | Restores saved results without a convergence gate; historical broken local results remain presented as fits. The v1 settings loader correctly clears results. |

   The concrete Find Peaks gap is at [index.html:14826](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:14826); undo/redo at [index.html:2429](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:2429). These are pre-existing completeness gaps, not newly introduced regressions. Legacy-file handling needs an explicit compatibility policy; absence of historical success metadata alone cannot identify a failed fit.

6. **MAJOR — Local residual variance is still exported and displayed as chi-square.**  
   [Figure export:10006](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:10006) unconditionally annotates `chiReduced` as χ². History rows also unconditionally label the snapshot statistic χ², and tab activation attaches the chi-square tooltip even when its text says “Residual variance.”

   `renderResults`, CSV/XLSX labels and saved engine/objective metadata are corrected. `_autoSnapshot` preserves that metadata and runs once after local success, but the history renderer ignores it. Route these remaining consumers through the statistic identity.

7. **MAJOR — The scanner provides useful triage, but its definitive claims are unsupported.**  
   [scan_batch_fit_signature.py:93](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/scripts/scan_batch_fit_signature.py:93) has these limitations:
   - Backend weights use `sqrt(max(counts, 1))`. At low counts, legitimate server statistics can have the **same ratio** as local statistics. I reproduced a “flagged local optimiser” classification for `chiReduced=1.015, rmse=1`.
   - A weighted reduced chi-square above 1000 is possible; it does not establish engine identity.
   - Missing RMSE with `chiReduced <= 1000` is silently unflagged, even with identical-model twins.
   - Recomputed RMSE can destroy the signature. I found no current in-app assignment that independently recomputes a local result’s RMSE, but the scanner cannot resolve files where this happened.
   - Explicit engine/status metadata is ignored; corrected local fits remain grouped with incident candidates.

   The current ZIP/project/spectrum containers are covered, and I reproduced the two B1s hits. Call these **suspected affected results**, distinguish explicit post-fix metadata, and report insufficient evidence rather than implying “clean.” Identical centers/widths corroborate copying; they do not prove failed optimization.

8. **MINOR — The recovery note incorrectly excludes ordinary Run Fit results.**  
   [Student note](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/docs/comms/2026-09-15-batch-fit-student-note.md) says anything fitted with ordinary Run Fit is unaffected, then later acknowledges local fallback. Historically that fallback also followed server errors, not just an unreachable server. Correct the categorical exclusion before sending the note.

9. **MINOR — Compatibility and scope are mostly sound, with specific follow-ups.**  
   Both production callers handle the new return value; `_statIsChi` is function-local and does not introduce shared module state. Removing committed peaks’ stale `_backendParams` is appropriate.

   Linked synchronization is **not identical to previous behavior**: it now updates every child and fixed-parent relationships. For normal app-created doublets this agrees with the backend constraints because `peakToBackendSpec` forces linked `fix_fwhm=true`. Copying inactive shape-key caches goes beyond the backend’s active-shape expressions and belongs in a separate cleanup/parity follow-up if unnecessary.

   The empty undo entry on failure is a minor UX issue—it also clears redo—not a release blocker. Scanner, proof and communication documents are incident-response additions outside the runtime acceptance rule, but justified. Broader optimizer parity, uncertainty estimation and legacy provenance migration should remain explicit follow-ups.

10. **MINOR — Tests catch the original defect, but do not establish the new acceptance guarantee.**  
    The five local-fit tests passed, including committed-project replay; the acceptance and module/per-tab structural tests also passed. Gaussian recovery would catch the original ascent sign and first-accepted-step termination defects.

    Missing coverage includes boundary stationarity, false stall convergence, HTTP HTML errors, actual upload failure handling, already-active failed batch targets, Find Peaks/undo result invalidation, and figure/history labels. Save/load coverage checks source text rather than executing a round trip. The full JS run was not clean in this read-only sandbox: Python-dependent checks encountered unavailable temporary-directory errors. I did not independently reproduce the claimed full Python-suite pass.

VERDICT: NO-GO — The optimizer can still announce unchanged or materially non-stationary models as converged, and server-error and stale-result paths still violate the acceptance rule.
