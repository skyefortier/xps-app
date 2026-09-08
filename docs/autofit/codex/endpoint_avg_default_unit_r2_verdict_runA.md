# Codex adversarial review — endpoint-averaging default 3 (feature-endpoint-avg-default-3) — round 2, RUN A (2026-09-08, reviewed at 55bd9d1 / code 15e16e4)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 77,585.
Prompt: docs/autofit/codex/endpoint_avg_default_unit_r2_review_prompt.txt
Evidence correction: the round-2 prompt claimed the batch-ROI and find-peaks-full-window browser files passed; the author's chained run had actually reported 1 failed / 11 passed (tests/test_browser_find_peaks_full_window.py::test_checkbox_off_preserves_todays_cropped_behavior — the new _invalidateBgCache() call in applyFindPeaks un-froze the cropped fit display). The chain did not stop on it; caught by re-reading the log after launch. Fixed in the round-3 commit.
Round 2: NO-GO x2 — Save Fit writer, v1 no-background path and batch propagation CLOSED (both); engine-wiring deferral ACCEPTED as a separate unit (both); NEW MAJOR (both): apply changes endpoint averaging but pushUndo/undo restore peaks only, so undo leaves the restored peaks at 1. MINORs: record write conditional on the DOM changing (B2); follow-up memo checklist places whitelists in app.py (they live in autofit/methods/*.py) and omits the direct _compute_background calls in bayesian_exchange_mc.py and sparse_map.py (A5).

**Findings**

One new MAJOR regression remains. Deferring full Find Peaks engine wiring is reasonable for this unit, provided applying and undoing suggestions preserve consistent background settings.

1. **BLOCKER — resolved: Save Fit persistence.** [_doSaveFit()](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/templates/index.html:8799) writes `background.endpointAvg`. The browser test intercepts the actual downloaded blob, parses it, reloads through `fromJSON`, and checks `'3'` in the artifact, record, and DOM.

2. **MAJOR — resolved: v1 files without background.** [The assignment](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/templates/index.html:3308) precedes and is independent of `if (data.background)`. Missing values resolve to `'1'`; saved `'9'` survives. The browser test covers a fresh target receiving `{version:1, peaks:[]}` and checks both record and DOM.

3. **MAJOR — open: Find Peaks introduces an undo regression.** [Applying suggestions](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/templates/index.html:14405) changes averaging and invalidates the stored background, but [`pushUndo`/`undo`](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/templates/index.html:2315) save and restore only peaks. I reproduced Apply → Undo using the actual functions from both revisions: main restores the original peaks with averaging `'3'` and the stored background; HEAD restores those peaks with averaging `'1'` and `bgIntensity=null`. The original peaks therefore redraw against a different background, and Save Fit persists the wrong setting. Restore the averaging and affected fit state through undo/redo, with regression coverage. The new browser test stops after Apply and misses this.

   The immediate preview adjustment otherwise works: `_fpLast` records averaging, and cache invalidation forces recomputation when the panel changes. Full engine threading need not accompany this default change.

4. **MINOR — resolved: batch propagation.** [The propagated settings](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/static/js/batch_propagation.js:39) include `endpointAvg`; absent or blank source values become `'1'`. Tests cover the changed propagated set and legacy sources, consistent with R3-B5.

5. **MINOR — open: follow-up wiring checklist is incomplete.** [The memo](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/docs/superpowers/plans/2026-09-03-endpoint-averaging-default.md:130) places method whitelists in `app.py`, but they reside in `autofit/methods/*.py`. It also omits direct `_compute_background` calls in `bayesian_exchange_mc.py:348` and `sparse_map.py:198`. Add those to make the deferred work’s coverage explicit.

No additional default leakage found in project/ZIP restoration, tab organization/activation/closure, spectrum loading, auto-fit rollback, or stack reconstruction. The rebase preserves the `shirley_linear` restoration hook.

The 11 focused Node tests passed. The full Node run encountered sandbox failures in Python-backed tests; browser/pytest results remain author-reported. Archived verdicts were not read. Reviewed HEAD `55bd9d1`, whose only addition beyond `15e16e4` is the round-2 prompt.

VERDICT: NO-GO — Find Peaks undo restores the original peaks without restoring their endpoint averaging or invalidated background.
