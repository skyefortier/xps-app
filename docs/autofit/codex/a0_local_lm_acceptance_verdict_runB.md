# Codex adversarial CODE review — unit A0 (local LM descent + fit acceptance rule) — round 1, RUN B (2026-09-15)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_review_prompt.txt
Branch state reviewed: 7850ce7 (+ e6beb54). Outcome: NO-GO x2 — projected-gradient sign inverted; forward-difference step too coarse for centres; stall accepted as convergence; HTTP errors with non-JSON bodies reached the local fallback; already-active batch target kept a foreign live result; three chi-square label sites; scanner overclaimed. All dispositioned in a0_local_lm_acceptance_recheck_prompt.txt (round 2).

Reviewed `origin/main..e6beb54` in full, plus the subsequent `7850ce7` changes made during review. Those changes do not resolve the findings below.

1. **BLOCKER — The projected-gradient sign still permits the original false-success outcome.**  
   At [index.html:7371](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7371), `J` differentiates the residual, so the objective gradient is **`+2 * Jtr`**, not `-2 * Jtr`. Its magnitude is unaffected, but the bound-blocking decision is reversed.

   Replaying the extracted function with a Gaussian’s center/width fixed:
   - Starting amplitude **1**, target amplitude **10**: returns `success:true`, **one iteration, zero accepted steps**, amplitude remains **1**.
   - Starting amplitude **1**, target amplitude **0.5**: amplitude 1 is the legitimate constrained optimum, but returns failure after **24 iterations**.

   Correct the sign and add both boundary regression tests.

2. **MAJOR — “Accepted something, then stalled” is insufficient evidence of convergence.**  
   [index.html:7394](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7394) accepts a stall regardless of the remaining feasible gradient. The forward difference for a center near 285 eV is **0.0285 eV**, large enough to give a materially misleading direction for narrow peaks.

   Extracted-function replay: Gaussian amplitude 10, fixed FWHM 0.1, target FWHM 0.2, only center free, target center 285:
   - Starting at 284.9 stalls successfully at **285.0014834**, with a numerical objective derivative around **1566**.
   - Starting at 285.02 reports convergence at **285.0138903**, RSS **1870.82**, although center 285 gives **1769.50**.

   Fixed, imperfect model shapes are legitimate fitting inputs. Require a credible feasible-stationarity check before converting damping exhaustion into success; tiny damped steps alone also cannot establish it. Separately, `caM`’s integer clamp makes both finite-difference probes identical throughout its allowed range, so its free derivative is always zero. That is inherited optimizer behavior, but the new convergence claim must account for it.

3. **MAJOR — HTTP failures still reach local fallback.**  
   [index.html:7113](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7113) parses JSON before checking `resp.ok`. I reproduced **502 + HTML → JSON exception → local fallback**.

   [uploadToBackend](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:6154) never checks HTTP status. An upload error containing `json.error` is classified correctly, but an HTML error triggers fallback; a JSON HTTP error without `error` can return an undefined session ID.

   Check HTTP status before classifying body-parsing failures. The requested cases otherwise behave correctly: fetch rejection and `AbortError` reach fallback; a 200 object lacking `success` is rejected without fallback. I found no ordinary fetch/JSON exception incorrectly classified as a server error.

4. **MAJOR — An already-active batch target can retain and re-save its previous result after failure.**  
   [index.html:10896](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:10896) clears `tgt.fitResult`, but the already-active branch copies peaks/settings into live state **without clearing `state.fitResult`**. If local fitting fails, it intentionally preserves that old live result; `_syncActiveToRecord()` then copies it back onto the newly propagated model.

   The summary says “NOT fitted … no result stored,” while the record contains a foreign result. Clear live and recorded results together before fitting. Reading the summary statistic from the return value in `7850ce7` does not fix this.

5. **MAJOR — Local statistics still escape as chi-square.**  
   The new labels work in Results, CSV/XLSX tables, and the persisted objective fields. However:
   - [Figure export](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:10006) unconditionally prints `χ²_r`.
   - [Fit history](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:12750) unconditionally prints `χ²`.
   - [Tab activation](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:3220) attaches the weighted chi-square tooltip to local residual variance.

   `_autoSnapshot()` correctly preserves the objective metadata, so history can use it. Apply the label distinction to these remaining consumers.

6. **MAJOR — The scanner is a useful heuristic, but its definitive diagnosis is incorrect.**  
   In [scan_batch_fit_signature.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/scripts/scan_batch_fit_signature.py:95):
   - Low-count server fits can have exactly the same signature: backend weights are `1/sqrt(max(counts,1))`, becoming unweighted for counts ≤1.
   - `chiReduced > 1000` independently flags a file. Weighted reduced chi-square has no such upper bound.
   - Missing RMSE and `chiReduced ≤1000` silently produce no hit; recomputed RMSE can likewise hide a local result.
   - Identical centers/widths corroborate similarity, not failed optimization: locked or legitimately repeated models can match.
   - Unsupported/unreadable files can produce an overall exit code **0**.
   - Explicitly identified, converged post-fix local results receive the same flagged diagnosis.

   I reproduced these false positives/negatives and confirmed the two reported B1s repository hits. Supported project/spectrum containers are read correctly, but the scanner cannot establish that every flagged result was unfitted or that every clean file is unaffected. Report provenance and uncertainty separately; do not call unreadable files clean.

7. **MAJOR — The acceptance rule is not complete across result-writing paths.**  
   Several remaining gaps predate this diff; they should be distinguished from newly introduced defects.

   | Path | Acceptance/result handling |
   |---|---|
   | `runFit` | Explicit `success === true` gate and owner check work; HTTP classification remains defective. |
   | `runFitLocal` | Copy-before-commit and preservation on reported failure work; convergence decision is unsound. |
   | `runPropagation` | Clears recorded result, but misses live result in the already-active branch. |
   | `runAutoFitC1sGraphite` | Rejects false/missing success and restores its snapshot on failure. Uses truthiness rather than strict `true`, and lacks an HTTP-status gate. Normal backend boolean responses are handled. |
   | `applyFindPeaks` | Replaces peaks but retains the previous `fitResult` when `fitFullWindow` is false. Old statistics/curve remain associated with new suggestions. |
   | Undo/redo | Restore peaks only; retain the later fit result and statistics. Undoing a successful fit can therefore display its result alongside pre-fit peaks. |
   | Fit-history restore | Restores paired peaks/result, but does not establish convergence provenance or restore the associated charge/background/ROI settings. |
   | Project/spectrum load | Restore saved results without acceptance validation. Previously affected files remain presented as fits; untagged local statistics default to chi-square. |

   The Find Peaks and undo mismatches are concrete existing foreign-result paths. Legacy loading needs an explicit compatibility/provenance policy, rather than treating absence of metadata as proof of convergence.

8. **MINOR — Linked synchronization is reasonable for ordinary doublets, but not semantically identical to the old implementation.**  
   [index.html:7304](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7304) now synchronizes every child, including properties whose parent parameters are locked. Previously only the first child and the currently varied property were updated. This repairs meaningful inconsistencies, including propagated linked amplitudes with locked parents.

   For normal same-shape, one-level UI doublets, the active constraints match the backend’s expressions. Copying every inactive shape key goes further than those expressions, however, and the single pass is not a general dependency-graph evaluator for loaded chains. Document this behavioral change and test locked parents; broader constraint-graph work belongs in follow-up.

9. **MINOR — Regression coverage catches the original defect, but misses the failures above.**  
   The five local tests pass, including committed-project replay and multi-step Gaussian recovery. They would catch restoration of the original ascent sign or first-accepted-step termination. The six acceptance tests and 21 module/per-tab structural tests also pass.

   Missing coverage includes bound stationarity, genuine stalled failure, actual upload handling, non-JSON HTTP errors, an already-active failed batch target, and figure/history labels. Save/load coverage checks source text rather than executing a round trip.

   I could not independently confirm the full-suite claims: the full JS run encountered Python dependency failures because this read-only sandbox cannot create temporary files. I did not rerun the full Python/browser suites. `7850ce7` appropriately fixes the browser test that assumed a free fitted center would remain unchanged.

10. **MINOR — Scope and compatibility are mostly controlled; incident documentation overclaims.**  
    Both production callers handle `runFitLocal`’s return value; `_statIsChi` is function-local and introduces no module-state regression. Successful local fits clear stale backend parameters and snapshot correctly; batch snapshot suppression remains intact. An empty undo entry on failure is a usability issue, including clearing redo history, not itself a release blocker.

    Scanner, incident proof, review prompt, and student note are incident-support additions beyond the runtime acceptance rule. The linked synchronization expansion is the substantive extra behavior. No unrelated backend/statistical redesign is needed here.

    Correct the [student note](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/docs/comms/2026-09-15-batch-fit-student-note.md:33): ordinary Run Fit was also affected through fallback and unchecked backend non-convergence. “Lists every affected tab” also exceeds the scanner’s demonstrated capability.

VERDICT: NO-GO — The optimizer can still certify an unchanged non-optimal starting model as converged, HTTP failures still trigger fallback, and failed batch targets can retain foreign fit results.
