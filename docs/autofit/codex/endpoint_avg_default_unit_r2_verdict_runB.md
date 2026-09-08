# Codex adversarial review — endpoint-averaging default 3 (feature-endpoint-avg-default-3) — round 2, RUN B (2026-09-08, reviewed at 55bd9d1 / code 15e16e4)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 76,204.
Prompt: docs/autofit/codex/endpoint_avg_default_unit_r2_review_prompt.txt
Evidence correction: the round-2 prompt claimed the batch-ROI and find-peaks-full-window browser files passed; the author's chained run had actually reported 1 failed / 11 passed (tests/test_browser_find_peaks_full_window.py::test_checkbox_off_preserves_todays_cropped_behavior — the new _invalidateBgCache() call in applyFindPeaks un-froze the cropped fit display). The chain did not stop on it; caught by re-reading the log after launch. Fixed in the round-3 commit.
Round 2: NO-GO x2 — Save Fit writer, v1 no-background path and batch propagation CLOSED (both); engine-wiring deferral ACCEPTED as a separate unit (both); NEW MAJOR (both): apply changes endpoint averaging but pushUndo/undo restore peaks only, so undo leaves the restored peaks at 1. MINORs: record write conditional on the DOM changing (B2); follow-up memo checklist places whitelists in app.py (they live in autofit/methods/*.py) and omits the direct _compute_background calls in bayesian_exchange_mc.py and sparse_map.py (A5).

**Findings**

Reviewed current HEAD `55bd9d1`; its only addition after `15e16e4` is the round-2 prompt. Archived verdict files were not read.

1. **MAJOR — New regression: undo leaves the changed averaging behind.** [applyFindPeaks](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/templates/index.html:14405) changes endpoint averaging, but `pushUndo`/`undo` preserve only peaks. Executing the actual functions reproduced: original peaks at **3 → apply suggestions at 1 → undo restores original peaks at 1**. This redraws the restored model against a different background. Include averaging in this action’s undo/redo state, restore DOM and record, and invalidate the cache. The new browser test never exercises undo.

2. **MINOR — Record synchronization is conditional on the DOM changing.** At the same location, `active.ui.endpointAvg` is assigned only when `epEl.value !== usedEp`. A fresh tab whose field was manually changed from 3 to 1 retains record value 3 after applying suggestions fitted at 1. Reproduced with the actual function. Save/tab-switch synchronization eventually repairs this, but the disposition’s immediate record-and-DOM guarantee is false. Assign the record independently of the DOM comparison.

3. **BLOCKER — CLOSED: production Save Fit writer.** [_doSaveFit](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/templates/index.html:8799) writes `background.endpointAvg`. The browser test intercepts the actual downloaded blob, parses it, checks `'3'`, reloads that artifact through `fromJSON`, and checks record and DOM. This addresses the original writer gap.

4. **MAJOR — CLOSED: v1 files without a background block.** [fromJSON](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/templates/index.html:3308) resolves averaging before and independently of the background conditional. The test covers a fresh target loading `{version:1, peaks:[]}` and checks record/DOM `'1'`; saved `'9'` wins. The shared `_restoreUI` call also restores that saved value into the DOM.

5. **MAJOR — Find Peaks disposition is only partially closed.** Actual-function checks confirmed default options record `'1'` and least-squares `endpoint_avg:9` records `'9'`. Application updates the field, invalidates the background, and emits the notice. **Full engine wiring may reasonably remain a separate unit**, given the explicit caveat and documented follow-up; it need not ship merely to change fresh-tab defaults. However, the new undo regression must be fixed before this narrower solution ships.

6. **MINOR — CLOSED: batch propagation.** [propagateFitUi](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/static/js/batch_propagation.js:39) copies the source averaging and resolves absent/blank values to `'1'`, consistent with R3-B5. Tests cover the propagated field set and legacy source.

No additional regression found in project/ZIP/spectrum restoration, activation ordering, stack fallbacks, auto-fit handling, or the rebased `shirley_linear` de-list integration. The two focused Node files passed **11/11**. Full-suite confirmation was blocked by Python temporary-directory requirements in this read-only sandbox; browser/pytest results remain author-reported.

VERDICT: NO-GO — Applying Find Peaks changes endpoint averaging without undo restoring it, so restored peaks can be rendered against the wrong background.
