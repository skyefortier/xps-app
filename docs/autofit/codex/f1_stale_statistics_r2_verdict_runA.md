OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0dc5f-1e35-77d1-851d-dd76dcd8125d
--------
user
Re-review unit F1 (stale statistics after an edit), round 2: branch fix-stale-statistics. The round-1 commit is ececf7e; the fixes are the commit after it (git diff ececf7e..HEAD; the whole unit is git diff main..HEAD). Round-1 verdicts: docs/autofit/codex/f1_stale_statistics_verdict_runA.md / runB.md; the round-1 prompt (brief, creators and consumers tables): docs/autofit/codex/f1_stale_statistics_review_prompt.txt. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

ROUND-1 FINDINGS AND FIXES (plan section 5, verbatim):

**Round 1 — NO-GO ×2** (`docs/autofit/codex/f1_stale_statistics_verdict_run{A,B}.md`).
All findings reproduced and fixed:

| # | finding (run) | fix |
|---|---|---|
| 1 | Auto-Fit stamps a response over a context edited while it ran as `current` (A) | `runAutoFitC1sGraphite` captures the key with the other request inputs, before the first await; after the owner check a different live key DISCARDS and rolls back (amber notice), as `runFit` already did. Behavioural test drives the real function. |
| 2 | Local fallback after a transport failure fits the press-time arrays and stamps the EDITED key (A, B) | `ctxAtRequest` hoisted out of the `try`; a transport failure with a changed key runs no local fit ("Fit discarded (model edited)"). Behavioural test in `fit_acceptance`. |
| 3 | Stale spectrum save → reload → restore the value: the edited-model `fittedY` sits under the original key and becomes "current" (A) | the loader installs neither `fittedY` nor `rFactor` from a save marked `statisticsState: 'stale'` (the file keeps them for its readers). |
| 4 | Project saves dropped `rFactor`; tab activation recomputed it from the EDITED peaks and cached it under the original key (B) | both saves persist the fit's own `rFactor`; activation computes a missing R only when not stale. Browser: stale project → reload → restore amplitude → R 3.087 % = the fit's. |
| 5 | Lock toggle / Lock All leave the visible statistics current (A, B) | `_refreshStatsState()` is now the first statement of `_refreshStartsEvidence`, which the lock toggles, Lock All and `updatePlot` all call (the separate call in `updatePlot` removed). |
| 6 | Clear All leaves the previous Results table (B) | the refresh also handles the transition to `none` (only when a state was rendered before: a fresh page is left alone). |
| 7 | MINOR: "280" vs "280.0" reads stale (A, B) | `_sameFitKey` compares keys after canonicalising the form-field numbers; keys are COMPARED canonically, never rewritten, so keys already in saved files keep matching. Used by every key comparison (statistics, starts evidence, support verdicts, both mid-fit discards). |


TRY TO BREAK
a. Each fix: is it complete (every path of that class), and does it introduce a regression? E.g. the Auto-Fit discard: does anything Auto-Fit ITSELF changes between the captured key and the check (provisional charge shift, the model it builds, _af bounds, ROI/background it sets) make every Auto-Fit discard itself? (The browser check ran Auto-Fit on C1s Scan_3 before the discard was added; verify the order in runAutoFitC1sGraphite.) The runFit fallback: a transport failure BEFORE ctxAtRequest is set.
b. _sameFitKey: can canonicalisation make two DIFFERENT fits compare equal (a field where '1e3' vs '1000', '0x10', ' 280', '280 ' or '' vs '0' change what the fit reads; parseInt vs parseFloat readers like shirleyIter '3.5' vs '3.50'; the ROI read by getROIData vs the key)? Is every comparison of the key now through it (grep ===/!== on startsModelKey, fitKey, ctxAtRequest, altKey)? Memo growth.
c. The refresh inside _refreshStartsEvidence: re-entrancy (renderResults -> ... -> updatePlot -> _refreshStartsEvidence), render count per edit, a Quantify RSF input being typed while Results re-renders, stack tabs, the 'none' transition on tab switch / close / empty tab.
d. Reload: a CURRENT save (no statisticsState) still installs fittedY and rFactor; an unverified older file; project saves (whose loader takes the fitResult object whole - does statisticsState ride into memory and matter later?).
e. Anything round 1 raised that is still reachable, and anything new in the consumers table (plan section 3) the fixes touched.
f. Tests: the new behavioural tests (fit_acceptance fallback discard, stale_statistics Auto-Fit discard / canonical key / Clear All) - would each fail without its fix?

Finish with VERDICT: GO or VERDICT: NO-GO.
codex
I’ll read the round-1 findings, inspect the fixes and surrounding paths, and check whether the new tests catch the reported failures. I’ll keep the review read-only and finish with a verdict.
exec
/bin/zsh -lc "pwd; rg --files -g AGENTS.md -g '*f1_stale_statistics*' -g '*stale_statistics*' -g '*fit_acceptance*'; git status --short; git log -3 --oneline; git diff --stat ececf7e..HEAD" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
tests/js/stale_statistics.test.js
tests/js/fit_acceptance.test.js
docs/autofit/codex/f1_stale_statistics_r2_verdict_runA.md
docs/autofit/codex/f1_stale_statistics_recheck_prompt.txt
docs/autofit/codex/f1_stale_statistics_verdict_runB.md
docs/autofit/codex/f1_stale_statistics_verdict_runA.md
docs/autofit/codex/f1_stale_statistics_review_prompt.txt
docs/autofit/codex/f1_stale_statistics_r2_verdict_runB.md
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-dTPak7yH' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Sn9k5Rrm' (errno=Operation not permitted)
?? docs/autofit/codex/f1_stale_statistics_r2_verdict_runA.md
?? docs/autofit/codex/f1_stale_statistics_r2_verdict_runB.md
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-a3aVn0pH' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-seUyoz1g' (errno=Operation not permitted)
9c94347 fix(F1): Codex round 1 (NO-GO x2) - mid-fit edits, reload paths, lock refresh, Clear All, key spelling
ececf7e fix(F1): statistics after an edit belong to the previous model - bound by the step (b) key
4475023 docs(caM): deploy-log entry and the owner's decisions at deploy
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-c90tZmFs' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-TwwZIG1q' (errno=Operation not permitted)
 CLAUDE.md                                          |    7 +-
 .../codex/f1_stale_statistics_recheck_prompt.txt   |   27 +
 .../codex/f1_stale_statistics_verdict_runA.md      | 6652 ++++++++++++++++++++
 .../codex/f1_stale_statistics_verdict_runB.md      | 6412 +++++++++++++++++++
 .../plans/2026-09-25-f1-stale-statistics.md        |   14 +-
 templates/index.html                               |   67 +-
 tests/js/fit_acceptance.test.js                    |   25 +-
 tests/js/local_lm_descent.test.js                  |    2 +-
 tests/js/scattered_starts.test.js                  |    6 +-
 tests/js/stale_statistics.test.js                  |   88 +-
 tests/js/unsupported_components.test.js            |    6 +-
 11 files changed, 13282 insertions(+), 24 deletions(-)

exec
/bin/zsh -lc "rg -n 'BLOCKER|MAJOR|MINOR|VERDICT:' docs/autofit/codex/f1_stale_statistics_verdict_runA.md docs/autofit/codex/f1_stale_statistics_verdict_runB.md | tail -55; sed -n '7310,7650p' templates/index.html; sed -n '7850,8120p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
docs/autofit/codex/f1_stale_statistics_verdict_runB.md:13:Review unit F1 (stale statistics after an edit): branch fix-stale-statistics, git diff main..HEAD (templates/index.html, tests/js/stale_statistics.test.js, tests/js/fit_acceptance.test.js, tests/js/local_lm_descent.test.js, tests/js/unsupported_components.test.js, tests/test_browser_find_peaks_full_window.py, CLAUDE.md, docs/superpowers/plans/2026-09-25-f1-stale-statistics.md). Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.
docs/autofit/codex/f1_stale_statistics_verdict_runB.md:79:Finish with VERDICT: GO or VERDICT: NO-GO.
docs/autofit/codex/f1_stale_statistics_verdict_runB.md:4319:  // round-2 MINOR).
docs/autofit/codex/f1_stale_statistics_verdict_runB.md:6375:1. **MAJOR — Fallback can certify statistics against the wrong ROI.** [templates/index.html:8546](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:8546)  
docs/autofit/codex/f1_stale_statistics_verdict_runB.md:6378:2. **MAJOR — Reload can attach the edited model’s R-factor to the original fit key.** [templates/index.html:3250](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:3250), [templates/index.html:10402](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:10402)  
docs/autofit/codex/f1_stale_statistics_verdict_runB.md:6381:3. **MAJOR — Lock edits bypass statistics refresh.** [templates/index.html:6038](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:6038), [templates/index.html:6065](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:6065)  
docs/autofit/codex/f1_stale_statistics_verdict_runB.md:6384:4. **MAJOR — Clear All retains the previous Results table.** [templates/index.html:7668](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:7668)  
docs/autofit/codex/f1_stale_statistics_verdict_runB.md:6387:5. **MINOR — Numeric formatting falsely invalidates statistics.** [templates/index.html:7618](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:7618)  
docs/autofit/codex/f1_stale_statistics_verdict_runB.md:6392:**VERDICT: NO-GO.**
docs/autofit/codex/f1_stale_statistics_verdict_runB.md:6395:1. **MAJOR — Fallback can certify statistics against the wrong ROI.** [templates/index.html:8546](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:8546)  
docs/autofit/codex/f1_stale_statistics_verdict_runB.md:6398:2. **MAJOR — Reload can attach the edited model’s R-factor to the original fit key.** [templates/index.html:3250](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:3250), [templates/index.html:10402](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:10402)  
docs/autofit/codex/f1_stale_statistics_verdict_runB.md:6401:3. **MAJOR — Lock edits bypass statistics refresh.** [templates/index.html:6038](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:6038), [templates/index.html:6065](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:6065)  
docs/autofit/codex/f1_stale_statistics_verdict_runB.md:6404:4. **MAJOR — Clear All retains the previous Results table.** [templates/index.html:7668](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:7668)  
docs/autofit/codex/f1_stale_statistics_verdict_runB.md:6407:5. **MINOR — Numeric formatting falsely invalidates statistics.** [templates/index.html:7618](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:7618)  
docs/autofit/codex/f1_stale_statistics_verdict_runB.md:6412:**VERDICT: NO-GO.**
docs/autofit/codex/f1_stale_statistics_verdict_runA.md:13:Review unit F1 (stale statistics after an edit): branch fix-stale-statistics, git diff main..HEAD (templates/index.html, tests/js/stale_statistics.test.js, tests/js/fit_acceptance.test.js, tests/js/local_lm_descent.test.js, tests/js/unsupported_components.test.js, tests/test_browser_find_peaks_full_window.py, CLAUDE.md, docs/superpowers/plans/2026-09-25-f1-stale-statistics.md). Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.
docs/autofit/codex/f1_stale_statistics_verdict_runA.md:79:Finish with VERDICT: GO or VERDICT: NO-GO.
docs/autofit/codex/f1_stale_statistics_verdict_runA.md:3534:  // round-2 MINOR).
docs/autofit/codex/f1_stale_statistics_verdict_runA.md:6615:1. **MAJOR — Auto-Fit stamps edits made during the request as current.** [templates/index.html:7345](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:7345)  
docs/autofit/codex/f1_stale_statistics_verdict_runA.md:6618:2. **MAJOR — Local fallback binds old data to the new ROI.** [templates/index.html:8546](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:8546)  
docs/autofit/codex/f1_stale_statistics_verdict_runA.md:6621:3. **MAJOR — Stale spectrum saves put a different curve under the original fit key.** [templates/index.html:10294](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:10294)  
docs/autofit/codex/f1_stale_statistics_verdict_runA.md:6624:4. **MAJOR — Lock changes leave visible statistics current until another repaint.** [templates/index.html:6037](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:6037)  
docs/autofit/codex/f1_stale_statistics_verdict_runA.md:6627:5. **MINOR — Equivalent numeric formatting falsely invalidates statistics.** [templates/index.html:7618](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:7618)  
docs/autofit/codex/f1_stale_statistics_verdict_runA.md:6632:**VERDICT: NO-GO**
docs/autofit/codex/f1_stale_statistics_verdict_runA.md:6635:1. **MAJOR — Auto-Fit stamps edits made during the request as current.** [templates/index.html:7345](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:7345)  
docs/autofit/codex/f1_stale_statistics_verdict_runA.md:6638:2. **MAJOR — Local fallback binds old data to the new ROI.** [templates/index.html:8546](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:8546)  
docs/autofit/codex/f1_stale_statistics_verdict_runA.md:6641:3. **MAJOR — Stale spectrum saves put a different curve under the original fit key.** [templates/index.html:10294](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:10294)  
docs/autofit/codex/f1_stale_statistics_verdict_runA.md:6644:4. **MAJOR — Lock changes leave visible statistics current until another repaint.** [templates/index.html:6037](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:6037)  
docs/autofit/codex/f1_stale_statistics_verdict_runA.md:6647:5. **MINOR — Equivalent numeric formatting falsely invalidates statistics.** [templates/index.html:7618](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:7618)  
docs/autofit/codex/f1_stale_statistics_verdict_runA.md:6652:**VERDICT: NO-GO**
  // 2. Validate within ±0.3 of 284.50 (the LA center bound).
  if (Math.abs(gPeak.center - 284.50) > 0.30 + 1e-6) {
    notify('Fit failed to converge or produced an unphysical graphite position.', 'red', true);
    return false;
  }
  // 3. Compute fitted raw center using APP CONVENTION:
  //    raw = corrected + state.ccShift (state.ccShift is the provisional value).
  const graphiteFittedRaw = gPeak.center + (Number.isFinite(state.ccShift) ? state.ccShift : 0);

  // 4. Drive updateChargeCorrection() to refine the shift.
  // Self-consistency: cc-obs = graphite_fitted_raw (NOT graphite_raw_BE),
  // approved design point.
  const cm = document.getElementById('cc-method');
  const co = document.getElementById('cc-obs');
  const cl = document.getElementById('cc-lit');
  if (cm && co && cl) {
    cm.value = 'c1s';
    co.value = graphiteFittedRaw.toFixed(3);
    cl.value = '284.50';
    if (typeof updateChargeCorrection === 'function') updateChargeCorrection();
  }

  // 5. Build state.fitResult exactly as runFit() does.
  const { be: be2, inten: inten2 } = getROIData();
  const bgI2 = computeBackground(be2, inten2);
  const bgSub2 = inten2.map((v, i) => v - bgI2[i]);
  const stats = json.statistics || {};
  const chiReduced = stats.reduced_chi_square || 0;
  const rmse = Math.sqrt((json.residuals || []).reduce((s, v) => s + v * v, 0) / Math.max(1, be2.length));
  const roiRange = { min: _arrMin(be2).toFixed(1), max: _arrMax(be2).toFixed(1) };
  state.fitResult = {
    chi: chiReduced * Math.max(1, be2.length - state.peaks.length * 3),
    chiReduced, rmse,
    be: be2, bgSubtracted: bgSub2, bgIntensity: bgI2,
    backendResult: json,
    fittedY: json.fitted_y,
    roiRange,
    startsModelKey: _startsLiveKey(),   // F1: binds the statistics to this model; re-stamped below with the locks
  };
  state.fitResult.rFactor = _computeRFactor(state.fitResult);

  // 6. Update the same DOM elements runFit() updates.
  const fq = document.getElementById('fit-quality');
  if (fq) {
    fq.textContent = 'χ²ᵣ = ' + chiReduced.toFixed(2);
    if (typeof _CHISQ_TOOLTIP !== 'undefined') fq.setAttribute('data-xps-tip', _CHISQ_TOOLTIP);
  }
  { const _t = typeof _activeTab === 'function' ? _activeTab() : null; if (_t) _t.modelProvenance = null; }
  if (typeof _applyStatDisplay === 'function') _applyStatDisplay(state.fitResult);
  const sbChi = document.getElementById('sb-chi');
  if (sbChi) sbChi.textContent = chiReduced.toFixed(3);
  const sbMsg = document.getElementById('sb-msg');
  if (sbMsg) sbMsg.textContent = 'Auto-fit complete';
  if (typeof _updateRFactorUI === 'function') _updateRFactorUI(state.fitResult.rFactor);
  if (typeof _updateROIDisplay === 'function') _updateROIDisplay(roiRange);
  // Lock all peak centers after a successful auto-fit. Users frequently
  // run "Run Fit" again to refine FWHMs/amplitudes; without this lock the
  // converged auto-fit positions can drift. The user can manually unlock
  // any center via the existing padlock icon in the peak editor.
  for (const p of state.peaks) p.fixCenter = true;
  // the locks and the refined charge shift are part of THIS result: the
  // support verdicts describe the model as finalised here
  if (typeof _restampSupport === 'function') _restampSupport();
  if (typeof renderPeakList === 'function') renderPeakList();
  if (typeof updatePlot === 'function') updatePlot();
  if (typeof renderResults === 'function') renderResults();
  if (typeof _autoSnapshot === 'function') _autoSnapshot();

  // 7. Sync to tab record so tab switching preserves the result.
  if (typeof tabManager !== 'undefined' && tabManager._syncActiveToRecord) {
    tabManager._syncActiveToRecord();
  }

  // 8. Sanity check: warn if graphite area fraction is below 40%. The fit
  // is kept regardless — this is a triage signal, not a fit-quality gate.
  // Uses _peakArea so the warning matches the user-visible AREA column
  // exactly (and so it doesn't depend on backend response shape).
  const gPeak2 = state.peaks.find(p => p.name === 'Graphite') || state.peaks[0];
  if (gPeak2) {
    const check = _autoFitCheckGraphiteFraction(gPeak2.id);
    if (check) notify(check.warning, 'amber', true);
  }

  return true;
}

// Top-level entry point. Wired to the Actions menu item.
async function runAutoFitC1sGraphite() {
  // Pre-conditions
  if (!state.rawBE || !state.rawBE.length) { notify('Load a spectrum first.', 'amber'); return; }
  const tab = tabManager._getTab(tabManager.activeId);
  if (!tab) { notify('No active tab.', 'amber'); return; }
  if (!isC1sTab(tab)) {
    notify('Auto-Fit C1s Graphite is only available for C1s spectra (ROI midpoint 270–315 eV).', 'amber');
    return;
  }
  // OWNER FIRST: the confirmation below is an await; the tab that is active
  // when it resolves may not be the one the user asked to auto-fit.
  const fittingTab = _opOwner();
  if (!fittingTab) { notify('No active spectrum tab.', 'amber'); return; }
  // Confirmation if existing peaks
  if (state.peaks.length >= 1) {
    const proceed = await _showAutoFitConfirmModal(state.peaks.length);
    if (!proceed) return;
    if (!_ownerActive(fittingTab)) {
      notify('Auto-fit cancelled — the tab changed while the confirmation was open.', 'amber');
      return;
    }
  }

  // Snapshot for failure rollback (separate from pushUndo, which only covers peaks).
  const snap = _autoFitSnapshot();

  // Step 1: find graphite in raw BE
  const { be: corrBE, inten } = getROIData();
  if (!corrBE.length) {
    notify('ROI is empty. Set roi-min and roi-max before auto-fit.', 'red', true);
    return;
  }
  const bgI = computeBackground(corrBE, inten);
  const bgSub = inten.map((v, i) => v - bgI[i]);
  // App convention: raw = corrected + state.ccShift
  const curShift = Number.isFinite(state.ccShift) ? state.ccShift : 0;
  const rawBE = corrBE.map(b => b + curShift);
  const graphiteRaw = findGraphiteRawBE(rawBE, bgSub);
  if (graphiteRaw == null) {
    notify('No strong peak found in the C1s ROI; Auto-Fit cannot proceed.', 'red', true);
    return;
  }

  // Step 2: provisional shift (APP CONVENTION).
  const provisionalShift = graphiteRaw - 284.50;

  // Step 3: assess low-BE region using provisional shift (no state mutation yet).
  const assessment = assessLowBERegion(rawBE, bgSub, provisionalShift);

  // Step 4: build the peak model (in corrected frame after provisional shift).
  pushUndo();
  state.peaks = [];
  state.fitResult = null;
  // Apply provisional shift via updateChargeCorrection so ROI/bg DOM fields
  // shift along with state.ccShift.
  const cm = document.getElementById('cc-method');
  const co = document.getElementById('cc-obs');
  const cl = document.getElementById('cc-lit');
  cm.value = 'c1s';
  co.value = graphiteRaw.toFixed(3);
  cl.value = '284.50';
  updateChargeCorrection();
  // Now build the peak list (graphite center 284.50 in this frame).
  const newPeaks = buildAutoFitModel(assessment);
  state.peaks = newPeaks;
  state.nextId = Math.max(0, ...state.peaks.map(p => p.id)) + 1;
  renderPeakList();

  // Step 5: run /api/fit with AbortController + spinner.
  _showFitSpinner();
  const spinLabel = document.getElementById('fit-spinner-label');
  if (spinLabel) spinLabel.textContent = 'Auto-fitting…';
  const runBtn = document.querySelector('.btn-green');
  if (runBtn) runBtn.disabled = true;

  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(new DOMException('timeout', 'AbortError')), 120000);

  try {
    const { be: be2, inten: inten2 } = getROIData();
    const bgType = document.getElementById('bg-type').value;
    const bgStart = parseFloat(document.getElementById('bg-start').value);
    const bgEnd = parseFloat(document.getElementById('bg-end').value);
    // Inclusive bg window — the same point set computeBackgroundCore draws;
    // the backend slices end-exclusive, so the request sends i1 + 1.
    const bgWin = _bgWindowIndices(be2, bgStart, bgEnd);
    const epAvg = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
    const fitMethod = document.getElementById('fit-method').value;

    // The anchor whose necessity the server must test — captured with the
    // other request inputs, before the first await (a tab switch during the
    // upload must not send another tab's id).
    const anchorId = String((state.peaks.find(p => p.name === 'Graphite') || state.peaks[0]).id);
    // the model and its fit context as sent (F1, Codex round 1): a result must
    // not be applied, and stamped current, over a model edited while it ran
    const ctxAtRequest = _startsLiveKey();
    // Build peak specs and overlay the per-peak bounds we attached in buildAutoFitModel.
    const peakSpecs = state.peaks.map(p => {
      const spec = peakToBackendSpec(p);
      if (Number.isFinite(p._afCenterMin)) spec.center_min = p._afCenterMin;
      if (Number.isFinite(p._afCenterMax)) spec.center_max = p._afCenterMax;
      if (Number.isFinite(p._afFwhmMin))   spec.fwhm_min   = p._afFwhmMin;
      if (Number.isFinite(p._afFwhmMax))   spec.fwhm_max   = p._afFwhmMax;
      spec.amplitude_min = 0;
      return spec;
    });

    const bgPayload = { method: bgType, start_idx: bgWin.i0, end_idx: bgWin.i1 + 1, endpoint_avg: epAvg };
    if (bgType === 'manual') {
      // Anchors are stored in corrected-BE space, same frame as the uploaded
      // session data; backend expects [x, y] pairs.
      bgPayload.manual_bg = _getManualAnchors().map(a => [a.x, a.y]);
    }
    const sessionId = await uploadToBackend(be2, inten2);   // after EVERY input above is captured
    const resp = await fetch('/api/fit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        background: bgPayload,
        peaks: peakSpecs,
        fit_method: fitMethod,
        n_perturb: 3,
        // step (c): is the charge-reference anchor REQUIRED? The server refits
        // the model without it; a redundant anchor must not set the energy
        // reference of a whole spectrum (see applyAutoFitResult).
        require_component: anchorId,
      }),
      signal: ctrl.signal,
    });
    clearTimeout(timer);
    const json = await resp.json();
    if (json.error) throw new Error(json.error);
    if (json.success !== true) throw new Error(json.message || 'fit did not converge');
    if (!_ownerActive(fittingTab)) {
      _hideFitSpinner();
      notify('Auto-fit discarded — tab switched during fit.', 'amber');
      _autoFitRestore(snap, fittingTab);
      return;
    }
    if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
      _hideFitSpinner();
      notify('Auto-fit discarded because the model or its background / ROI settings were edited while it was running. Previous peaks and result restored. Run it again.', 'amber', true);
      _autoFitRestore(snap, fittingTab);
      return;
    }

    applyBackendResult(json);

    const ok = applyAutoFitResult(json, graphiteRaw, { be: be2, inten: inten2, bgIntensity: bgI, bgSubtracted: bgSub });
    if (!ok) {
      _hideFitSpinner();
      _autoFitRestore(snap, fittingTab);
      return;
    }

    _hideFitSpinner();
    notify('Auto-fit complete. χ²ᵣ = ' + (state.fitResult?.chiReduced?.toFixed(3) || '?'), 'green');
  } catch (e) {
    clearTimeout(timer);
    _hideFitSpinner();
    // The catch path can also fire after a mid-flight tab switch (fetch
    // error/timeout after the user moved on) — same wrong-tab hazard as
    // the explicit discard branch, so it gets the same tab-aware restore.
    _autoFitRestore(snap, fittingTab);
    let msg;
    if (e && (e.name === 'AbortError' || (e.message && e.message.toLowerCase().includes('aborted')))) {
      msg = 'Auto-fit exceeded the 2-minute timeout.';
    } else if (e && e.message) {
      msg = 'Fit failed to converge or produced an unphysical graphite position.';
      console.warn('Auto-fit error:', e);
    } else {
      msg = 'Auto-fit failed.';
    }
    notify(msg, 'red', true);
  }
}

function isC1sTab(tab) {
  if (!tab || !tab.rawBE || !tab.rawBE.length) return false;
  const ui = tab.ui || {};
  let lo = parseFloat(ui.roiMin);
  let hi = parseFloat(ui.roiMax);
  if (!Number.isFinite(lo) || !Number.isFinite(hi)) {
    // Fall back to full raw range (no UI ROI set yet)
    let rmin = Infinity, rmax = -Infinity;
    for (const v of tab.rawBE) {
      if (v < rmin) rmin = v;
      if (v > rmax) rmax = v;
    }
    lo = rmin; hi = rmax;
  }
  if (!Number.isFinite(lo) || !Number.isFinite(hi)) return false;
  const mid = (lo + hi) / 2;
  return mid >= 270.0 && mid <= 315.0;
}

// ── Scattered-starts check (2026-09-21) ───────────────────────────────────────
// Every Run Fit with two or more unlinked components asks the server for three
// more fits of the SAME method from scattered starts. The student's result
// stays THE FIT; a solution with a lower reduced chi-square is listed beside it
// with its own areas and how far each component moved from the student's start
// (a relocated component must be visible at a glance: on a committed C 1s scan
// the better-scoring solution slid C-O 1.4 eV under the main line). Solutions
// that are not better are only counted. Measured on the lab's 202 fit targets:
// an alternative appears on 0 % of re-fits of a saved solution and 7 % of
// not-yet-fitted starts, for a median +0.5 s. No certification language: the
// check can show a decomposition is not unique, never that one is correct.
const _STARTS_N = 3;
const _STARTS_SHIFT_AMBER_EV = 0.5, _STARTS_SHIFT_RED_EV = 1.0;
const _STARTS_TOOLTIP = "After your fit, the same method is run again from a few scattered starting points. If they all come back to your solution, that is what those starts found, no more: other starts or another method might not. If one finds a different solution with a lower χ²ᵣ it is listed here with how far each component moved from where you put it. Your fit is never replaced. A lower χ²ᵣ is not a better chemical model. Identical requests give identical results on real data in practice, but the underlying arithmetic is not bit-reproducible, so a fit sitting near a boundary between two solutions can still resolve differently; that is the situation this check is designed to surface.";

function _startsUnlinkedCount(peaks) { return (peaks || []).filter(p => !p.linked).length; }

// The evidence belongs to the FIT THAT PRODUCED IT: the model (everything the
// request reads from a peak) AND its context (background type and window,
// endpoint averaging, Shirley iterations, ROI, manual anchors, charge shift).
// The key is taken when the result is stored; it is compared, never
// invalidated by hand, so no edit path can be forgotten: after any change to
// a parameter, lock, shape, link, the peak list, the background, the ROI, the
// anchors or the charge correction — or an undo / history restore that brings
// back other values — the panel says the comparison no longer applies,
// nothing can be previewed or applied, and saves/exports carry no counts. A
// name, colour or visibility is not part of a fit and does not invalidate it.
const _STARTS_MODEL_FIELDS = ['id', 'shape', 'center', 'fwhm', 'amplitude', 'glMix', 'asymmetry', 'dsAlpha', 'dsGamma',
  'laAlpha', 'laBeta', 'laM', 'caAlpha', 'caBeta', 'caM', 'linked', 'linkOffset', 'linkRatio', '_afAsymMin', '_afAsymMax',
  'fixCenter', 'fixFwhm', 'fixAmplitude', 'fixGlMix', 'fixAsymmetry', 'fixDsAlpha', 'fixDsGamma',
  'fixLaAlpha', 'fixLaBeta', 'fixLaM', 'fixCaAlpha', 'fixCaBeta', 'fixCaM'];
const _STARTS_UI_FIELDS = ['bgType', 'bgStart', 'bgEnd', 'shirleyIter', 'endpointAvg', 'roiMin', 'roiMax'];
function _startsModelKey(peaks, ui, ccShift, anchors) {
  return JSON.stringify({
    p: (peaks || []).map(q => _STARTS_MODEL_FIELDS.map(k => (q[k] === undefined ? null : q[k]))),
    u: _STARTS_UI_FIELDS.map(k => String((ui || {})[k] ?? '')),
    s: Number(ccShift) || 0,
    a: (anchors || []).map(v => [v.x, v.y]),
  });
}
// Two keys describe the same fit when they are equal after the form fields'
// numbers are canonicalised: '280' and '280.0' select the same data and send
// the same request (F1, Codex round 1). Compared, never rewritten, so keys
// already persisted in saved files keep matching.
function _fitKeyCanon(k) {
  if (typeof k !== 'string') return k;
  const memo = _fitKeyCanon._memo || (_fitKeyCanon._memo = new Map());
  let c = memo.get(k);
  if (c !== undefined) return c;
  try {
    const o = JSON.parse(k);
    if (o && Array.isArray(o.u)) o.u = o.u.map(v => (typeof v === 'string' && v.trim() !== '' && Number.isFinite(Number(v))) ? String(Number(v)) : v);
    c = JSON.stringify(o);
  } catch (_) { c = k; }
  if (memo.size > 256) memo.clear();
  memo.set(k, c);
  return c;
  if (!_startsIfCurrent(state.fitResult, _startsLiveKey())) return null;
  const peaks = JSON.parse(JSON.stringify(state.peaks));
  if (peaks.length !== alt.components.length) return null;
  for (const c of alt.components) {
    const p = peaks.find(q => String(q.id) === String(c.id));
    if (!p) return null;
    const par = {};
    for (const k in c.params) par[k] = { value: c.params[k] };
    _applyBackendParams(p, par);
  }
  return peaks;
}

function _currentAlternative(k) {
  const st = _startsIfCurrent(state.fitResult, _startsLiveKey());
  return (st && st.ran && st.alternatives && st.alternatives[k]) || null;
}

const _STARTS_STALE_MSG = 'The model has changed since this fit. Run the fit again to compare solutions.';

function previewAlternative(k) {
  const alt = _currentAlternative(k);
  const peaks = alt && _altPeaks(alt);
  if (!peaks) { notify(_STARTS_STALE_MSG, 'amber', true); return; }
  const key = 'alt:' + k;
  if (_historyPreview && _historyPreview.snapId === key) { _historyClearPreview(); return; }
  _historyPreview = { snapId: key, altKey: state.fitResult.startsModelKey, peaks, fitResult: { chiReduced: alt.chi2r } };
  _updateLocalModelBanner();
  document.querySelectorAll('.hist-row').forEach(r => r.classList.remove('hist-preview-active'));
  updatePlot();
}

// Adopting an alternative is the student's decision: explicit, undoable, and
// recorded. It is ATOMIC by construction: the alternative is only the START of
// an ordinary server fit (runFit's opts.startPeaks); the live model is written
// by that fit's success path and by nothing else, so a fit that fails, does
// not converge, is discarded because the tab changed, or cannot reach the
// server leaves peaks and result exactly as they were (no local fallback
// here: the local engine would start from the live model, not from the
// alternative). runFit's own pushUndo is the single undo entry. A solution
// that moves a component more than 1 eV from where the student put it is the
// measured trap (a lower chi-square bought by a chemically absurd relocation),
// so that case — and only that case — asks first, naming the component and
// the distance.
async function useAlternative(k) {
  const alt = _currentAlternative(k);
  const peaks = alt && _altPeaks(alt);
  if (!peaks) { notify(_STARTS_STALE_MSG, 'amber', true); return; }
  const shift = alt.largest_centre_shift_from_start;
  const name = _startsPeakName(shift.id);
  if (Math.abs(shift.ev) > _STARTS_SHIFT_RED_EV &&
      !confirm(`This solution moves ${name} by ${_startsEv(shift.ev)} from where you placed it. Apply?`)) return;
  const chosen = { fromChi: state.fitResult.starts.fit.chi2r, toChi: alt.chi2r, shiftName: name, shiftEv: shift.ev };
  if (_historyPreview) _historyClearPreview();
  await runFit({ startPeaks: peaks, chosenAlternative: chosen });
}

async function runFit(opts = {}) {
  if (!state.rawBE.length) { notify('Load a spectrum first.', 'red', true); return; }
  if (!state.peaks.length) { notify('Add at least one peak.', 'red'); return; }
  pushUndo();

  _showFitSpinner();
  document.getElementById('sb-msg').textContent = 'Fitting\u2026';

  // Capture the tab that owns this fit so that if the user switches tabs
  // mid-request, we can discard the stale result instead of corrupting the
  // now-active tab's state.
  const fittingTab = _opOwner();

  const { be, inten } = getROIData();
  const bgIntensity = computeBackground(be, inten);
  const bgSubtracted = inten.map((v, i) => v - bgIntensity[i]);

  // Try Flask backend first
  let backendResult = null;
  let ctxAtRequest = null;   // set with the other request inputs; read again by the local fallback
  try {
    const bgType  = document.getElementById('bg-type').value;
    const bgStart = parseFloat(document.getElementById('bg-start').value);
    const bgEnd   = parseFloat(document.getElementById('bg-end').value);
    // Inclusive bg window — the same point set computeBackgroundCore draws;
    // the backend slices end-exclusive, so the request sends i1 + 1.
    const bgWin = _bgWindowIndices(be, bgStart, bgEnd);
    // EVERY request input is read from the owner before the upload await:
    // peaks, method, endpoint averaging and manual anchors (Codex round 2: a
    // request could carry A's spectrum with B's averaging and anchors).
    // opts.startPeaks: the request starts from an adopted alternative; the live
    // model is still the student's until this fit succeeds (useAlternative).
    const startModel = opts.startPeaks || state.peaks;
    const peakSpecs = startModel.map(peakToBackendSpec);
    // scattered-starts check: decided HERE, with the other request inputs,
    // before the first await (a tab switch during the upload must not turn it off)
    const nStarts = _startsUnlinkedCount(startModel) >= 2 ? _STARTS_N : 0;
    // the live model and its fit context as the student pressed the button: a
    // result must not be written over a model that was edited while it ran
    ctxAtRequest = _startsLiveKey();
    const fitMethod = document.getElementById('fit-method').value;
    const epAvgVal = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
    const bgPayload = { method: bgType, start_idx: bgWin.i0, end_idx: bgWin.i1 + 1, endpoint_avg: epAvgVal };
    if (bgType === 'manual') {
      // Anchors are stored in corrected-BE space, same frame as the uploaded
      // session data; backend expects [x, y] pairs.
      bgPayload.manual_bg = _getManualAnchors().map(a => [a.x, a.y]);
    }
    // Transport failures (server unreachable, timeout, non-JSON reply) are
    // the ONLY reason to fall back to the local optimiser. A server-side
    // validation error or a non-converged optimisation surfaces its message
    // and leaves the model untouched (unit A0: nothing is shown as a fit
    // result unless it converged; an HTTP 400 is not a reason to silently
    // switch engines).
    // Only a genuine transport failure (network rejection, abort, unparsable
    // 2xx body) is marked for fallback; server errors carry `serverError`.
    const _asTransport = (e) => {
      if (e && !e.serverError && (e instanceof TypeError || e.name === 'AbortError' || e instanceof SyntaxError)) e.transportFailure = true;
      throw e;
    };
    let sessionId;
    try { sessionId = await uploadToBackend(be, inten); } catch (e) { _asTransport(e); }
    const fitReq = {
      session_id: sessionId,
      background: bgPayload,
      peaks: peakSpecs,
      fit_method: fitMethod,
      n_perturb: 3,
      n_starts: nStarts       // the server also skips it for the global methods
    };
    let resp, json;
    try {
      resp = await fetch('/api/fit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(fitReq)
      });
    } catch (e) { _asTransport(e); }
    if (resp.ok === false) {
      // HTTP failure: read a message if the body is JSON, but a 502 HTML
      // page is still a SERVER failure, never a reason to switch engines.
      let msg = null;
      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
      const err = new Error(msg || ('Fit request failed (HTTP ' + resp.status + ').'));
      err.serverError = true;
      throw err;
    }
    try { json = await resp.json(); } catch (e) { _asTransport(e); }
    if (json.error) {
      const err = new Error(json.error);
      err.serverError = true;
      throw err;
    }
    // ACCEPTANCE RULE: the backend reports lmfit's own convergence flag. A
    // result that did not converge is a failed fit, not a result (audit A08:
    // until this unit success:false was applied and announced as complete).
    if (json.success !== true) {
      const err = new Error(json.message || 'the optimizer did not converge.');
      err.notConverged = true;
      throw err;
    }
    backendResult = json;

    // If the user switched tabs while the fit was running, discard the result
    // rather than overwriting the now-active tab's peaks.
    if (!_ownerActive(fittingTab)) {
      _hideFitSpinner();
      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
      notify('Fit result discarded because you switched tabs during the fit.', 'amber');
      return;
    }

    // The peak controls stay editable while the fit runs. A result computed for
    // the model as it was must not be applied over an edited one (a newly locked
    // centre would keep its edited value under the server's statistics).
    if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
      _hideFitSpinner();
      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
      notify('Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.', 'amber', true);
      return;
    }

    // Capture pre-fit values for uncertainty validation
    const _preFit = {};
    for (const p of state.peaks) {
      _preFit[p.id] = { center: p.center, fwhm: p.fwhm, amplitude: p.amplitude, glMix: p.glMix };
    }
    applyBackendResult(backendResult);
    { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }   // a new result supersedes imported provenance
    const stats = backendResult.statistics || {};
    const chiReduced = stats.reduced_chi_square || 0;
    const rmse = Math.sqrt((backendResult.residuals || []).reduce((s, v) => s + v * v, 0) / Math.max(1, be.length));
    const roiRange = { min: _arrMin(be).toFixed(1), max: _arrMax(be).toFixed(1) };
    state.fitResult = { chi: chiReduced * Math.max(1, be.length - state.peaks.length * 3),
                        chiReduced, rmse, be, bgSubtracted, bgIntensity, backendResult,
                        fittedY: backendResult.fitted_y, roiRange, _preFit,
                        starts: backendResult.starts || null,
                        startsModelKey: _startsLiveKey(),     // model + context, taken AFTER the result was applied
                        chosenAlternative: opts.chosenAlternative || null };
    // a preview of an alternative always belongs to the PREVIOUS result (an identical
    // key does not make it this one's): clear it unconditionally
    if (_historyPreview && typeof _historyPreview.snapId === 'string' && _historyPreview.snapId.startsWith('alt:')) _historyPreview = null;
    state.fitResult.rFactor = _computeRFactor(state.fitResult);
    _applyStatDisplay(state.fitResult);
    document.getElementById('sb-msg').textContent = 'Fit complete (lmfit)';
    _updateRFactorUI(state.fitResult.rFactor);
    _updateROIDisplay(roiRange);
    _hideFitSpinner();
    notify('Fit complete. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3), 'green');
  } catch (e) {
    // Fall back to local Levenberg-Marquardt
    _hideFitSpinner();
    if (!_ownerActive(fittingTab)) {
      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
      notify('Fit cancelled — tab switched during fit.', 'amber');
      return;
    }
    if (e && e.transportFailure && opts.startPeaks) {
      // Adopting an alternative needs the server: the local engine would start
      // from the live model, not from the alternative. Nothing was changed.
      document.getElementById('sb-msg').textContent = 'Fit failed';
      notify('The server could not be reached, so the alternative was not applied. Previous peaks and result kept.', 'red', true);
      return;
    }
    if (e && e.transportFailure && ctxAtRequest !== null && !_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
      // The fallback would fit the arrays captured at the press over a model or
      // context edited since, and stamp the edited one (F1, Codex round 1).
      _hideFitSpinner();
      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
      notify('The server could not be reached, and the model or its background / ROI settings were edited while the fit was running, so no local fit was run. Previous peaks and result kept. Run the fit again.', 'amber', true);
      return;
    }
    if (e && e.transportFailure) {
      // Server unreachable: the local optimiser is the honest fallback, and
      // the overlay saying so opens only if it actually converged.
      if (e.message) console.warn('Backend unreachable, falling back to local LM:', e.message);
      const local = runFitLocal(be, bgSubtracted, bgIntensity);
      if (local && local.success && !_snapshotSuppressed) {
        document.getElementById('localfit-warn-overlay').classList.add('open');
      }
      return;
    }
    // Server-side error or non-converged optimisation: report it; the
    // previous peaks and fit result stay exactly as they were.
    const notConverged = !!(e && e.notConverged);
    document.getElementById('sb-msg').textContent = notConverged ? 'Fit did not converge' : 'Fit failed';
    notify((notConverged ? 'Fit did not converge: ' : 'Fit failed: ') + ((e && e.message) || 'unknown error') +
           ' Previous peaks and result kept.', 'red', true);
    return;
  }

  renderPeakList();
  updatePlot();
  renderResults();
  _autoSnapshot();
}

// Label for the goodness-of-fit statistic a fit result carries. The server
// and (since unit W1, 2026-09-18) the local engine both minimise a
// counting-noise-weighted chi-square; local results saved by unit A0 were
// UNWEIGHTED and keep the label "Residual variance", never chi-square.
function _isUnweightedLocal(fr) { return !!(fr && fr.objective === 'unweighted_residual_variance'); }
function _fitStatLabel(fr) {
  return _isUnweightedLocal(fr) ? 'Residual variance' : 'χ²ᵣ';
}
// A LOCAL result is a STARTING POINT, not a reportable result. Measured in
// unit W1 (docs/superpowers/plans/2026-09-18-local-engine-poisson-weighting.md):
// with Poisson weighting the local engine matches the server on GL-type
// models (<= 4 meV, <= 1.4 % area on the lab's C1s scans) and, since A03
// (2026-09-22: Voigt = fixed eta 0.5 on BOTH sides), on Voigt components
// wherever the two engines reach the same minimum (5 of 9 committed U 4f
// targets: every component within 4.3 meV, 2.6 % FWHM, 2 % area, 0.12 pp);
// it still differs where an LA component's m moves on the server (held,
// exactly, at its start locally - LA is discontinuous in m, caM unit) and

exec
/bin/zsh -lc "rg -n 'function (getROIData|computeBackground|renderResults|renderQuant|_dropStaleAltPreview|_computeRFactor|_doSaveFit)|shirleyIter|shirley-iter|endpointAvg|altKey|startsModelKey|ctxAtRequest|fitKey' templates/index.html; rg --files tests | head -60; git diff main..HEAD --stat" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
2045:                <input type="number" id="shirley-iter" value="5" min="1" max="50" step="1" oninput="_clampShirleyIter(); _invalidateBgCache(); updatePlot()" title="Number of iterations for the Shirley background calculation. The algorithm converges quickly — most of the change happens between 1 and 5 iterations. Values above 10 rarely produce visible differences. Default: 5.">
2369:// panel to what the engine fitted at) passes { endpointAvg } so the snapshot
2374:  if (extra && extra.endpointAvg !== undefined) snap._endpointAvg = String(extra.endpointAvg);
2387:  if (!snap || snap._endpointAvg === undefined) return;
2389:  if (el) el.value = snap._endpointAvg;
2390:  if (tab && tab.ui) tab.ui.endpointAvg = snap._endpointAvg;
2412:  if (extra && extra.endpointAvg !== undefined) snap._endpointAvg = String(extra.endpointAvg);
2454:  t.redoStack.push(_peaksSnapshot(snap._endpointAvg !== undefined
2455:    ? { endpointAvg: document.getElementById('bg-endpoint-avg')?.value } : null));
2470:  t.undoStack.push(_peaksSnapshot(snap._endpointAvg !== undefined
2471:    ? { endpointAvg: document.getElementById('bg-endpoint-avg')?.value } : null));
3124:// lacks endpointAvg must resolve to: such fits were made before the field
3176:        shirleyIter: '5', endpointAvg: NEW_TAB_ENDPOINT_AVG,
3209:      ui: { bgType: 'shirley', bgStart: '', bgEnd: '', shirleyIter: '5',
3210:            endpointAvg: '1', roiMin: '', roiMax: '',
3393:        shirleyIter: document.getElementById('shirley-iter').value,
3394:        endpointAvg: document.getElementById('bg-endpoint-avg').value
3421:      pushUndo({ endpointAvg: document.getElementById('bg-endpoint-avg')?.value });
3453:      active.ui.endpointAvg = (data.background && data.background.endpointAvg) || LEGACY_ENDPOINT_AVG;
3460:        active.ui.shirleyIter = data.background.shirleyIter || '5';
3831:      shirleyIter: document.getElementById('shirley-iter')?.value || '5',
3832:      endpointAvg: document.getElementById('bg-endpoint-avg')?.value || LEGACY_ENDPOINT_AVG,
3851:    set('shirley-iter', ui.shirleyIter);
3852:    set('bg-endpoint-avg', ui.endpointAvg || LEGACY_ENDPOINT_AVG);
3872:      const si = document.getElementById('shirley-iter');
4666:  const el = document.getElementById('shirley-iter');
4708:// (matches the shape of tab.ui — bgType, bgStart, bgEnd, shirleyIter,
4709:// endpointAvg) instead of reading from DOM. Used by stack-view render
4713:function computeBackgroundCore(be, intensity, settings) {
4715:  const iter = parseInt(settings.shirleyIter) || 5;
4716:  const nAvg = parseInt(settings.endpointAvg) || 1;
4763:function computeBackground(be, intensity) {
4766:    shirleyIter: document.getElementById('shirley-iter').value,
4767:    endpointAvg: document.getElementById('bg-endpoint-avg').value,
5084:function getROIData() {
6581:// `shirley-iter` is gated when bg-type doesn't need iteration.
6672:    // obvious — matches the shirley-iter / bg-endpoint-avg pattern.
7157:// `p.support.fitKey`, the key of the model and fit context at that time, and
7198:function _applySupportVerdicts(peaks, verdictOf, fitKey) {
7202:    p.support = v ? { f: v.f ?? null, delta_chi2: v.delta_chi2 ?? null, supported: !!v.supported, fitKey,
7206:function _applySupport(peaks, json, fitKey) {
7207:  _applySupportVerdicts(peaks, id => _componentSupportFromResponse(json, id), fitKey);
7212:  if (!p.support.fitKey) return false;                              // a verdict from before keys existed: not applied
7214:  return _sameFitKey(p.support.fitKey, key);
7218:  if (!(p && p.support && p.support.fitKey)) return null;
7219:  return _sameFitKey(p.support.fitKey, _startsLiveKey()) ? p.support : null;
7226:  for (const p of state.peaks) if (p.support) p.support.fitKey = key;
7227:  if (state.fitResult) state.fitResult.startsModelKey = key;   // F1: the statistics are the same result's
7347:    startsModelKey: _startsLiveKey(),   // F1: binds the statistics to this model; re-stamped below with the locks
7492:    const ctxAtRequest = _startsLiveKey();
7537:    if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
7625:const _STARTS_UI_FIELDS = ['bgType', 'bgStart', 'bgEnd', 'shirleyIter', 'endpointAvg', 'roiMin', 'roiMax'];
7626:function _startsModelKey(peaks, ui, ccShift, anchors) {
7638:function _fitKeyCanon(k) {
7640:  const memo = _fitKeyCanon._memo || (_fitKeyCanon._memo = new Map());
7652:function _sameFitKey(a, b) { return !!a && !!b && (a === b || _fitKeyCanon(a) === _fitKeyCanon(b)); }
7656:  return _startsModelKey(state.peaks, ui, state.ccShift, typeof _getManualAnchors === 'function' ? _getManualAnchors() : []);
7659:function _startsRecordKey(t) { return _startsModelKey(t.peaks, t.ui, t.ccShift, t.manualAnchors); }
7663:  if (!st || !fr.startsModelKey || !_sameFitKey(fr.startsModelKey, key)) return null;
7679:  if (!fr.startsModelKey) return 'unverified';
7680:  return _sameFitKey(fr.startsModelKey, key) ? 'current' : 'stale';
7737:function _dropStaleAltPreview() {
7739:      !(state.fitResult && _historyPreview.altKey === state.fitResult.startsModelKey && _startsIfCurrent(state.fitResult, _startsLiveKey()))) {
7876:  _historyPreview = { snapId: key, altKey: state.fitResult.startsModelKey, peaks, fitResult: { chiReduced: alt.chi2r } };
7926:  let ctxAtRequest = null;   // set with the other request inputs; read again by the local fallback
7946:    ctxAtRequest = _startsLiveKey();
8022:    if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
8044:                        startsModelKey: _startsLiveKey(),     // model + context, taken AFTER the result was applied
8071:    if (e && e.transportFailure && ctxAtRequest !== null && !_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
8589:                      startsModelKey: _startsLiveKey() };   // F1: the statistics describe the committed model
8654:function renderResults() {
8820:function renderQuantify(areas, totalArea) {
9026:    shirleyIter: (srcUi && srcUi.shirleyIter) || '5',
9027:    endpointAvg: (srcUi && srcUi.endpointAvg) || LEGACY_ENDPOINT_AVG,
10268:function _doSaveFit() {
10284:      shirleyIter: document.getElementById('shirley-iter').value,
10287:      endpointAvg: document.getElementById('bg-endpoint-avg').value,
10305:      startsModelKey: state.fitResult.startsModelKey || null,
10367:    startsModelKey: state.fitResult.startsModelKey || null,
10464:        startsModelKey: t.fitResult.startsModelKey || null,
10674:  // Saved-ui boundary: a file whose ui lacks endpointAvg was fitted at 1
10678:  const savedEp = data.ui && data.ui.endpointAvg;
10679:  active.ui = { ...active.ui, ...(data.ui || {}), endpointAvg: savedEp || LEGACY_ENDPOINT_AVG };
10685:    for (const k of ['engine', 'objective', 'weighting', 'status', 'caveat', 'starts', 'startsModelKey', 'chosenAlternative']) if (data.statistics[k]) fr[k] = data.statistics[k];
10821:        ui: { bgType: 'shirley', bgStart: '', bgEnd: '', shirleyIter: '5',
10822:              endpointAvg: '1', roiMin: '', roiMax: '',
10847:        shirleyIter: '5', roiMin: '', roiMax: '',
11580:function _computeRFactor(fitResult) {
12223:    _pushUndoFor(tgt, { endpointAvg: tgt.ui && tgt.ui.endpointAvg });
14278:  const shirleyIter = document.getElementById('shirley-iter');
14279:  if (shirleyIter) {
14280:    shirleyIter.disabled = !needsIter;
14281:    shirleyIter.style.opacity = needsIter ? '1' : '0.4';
15390:      ((stored.regions || []).join(', ') || '?') + ', endpoint averaging ' + (stored.endpointAvg || '?') +
15924:    _fpSetLast({ body, method, regions, fitFullWindow: !!options.fit_full_window, endpointAvg: engineEndpointAvg }, owner);
16119:  pushUndo({ endpointAvg: document.getElementById('bg-endpoint-avg')?.value });
16149:  const usedEp = (_fpLast && _fpLast.endpointAvg) || LEGACY_ENDPOINT_AVG;
16153:  if (active) active.ui.endpointAvg = usedEp;   // unconditional: the record must match the fit even if the field was hand-edited
tests/test_component_required.py
tests/test_tougaard_background.py
tests/test_browser_overlay_zip_roundtrip.py
tests/test_browser_find_peaks_drag.py
tests/test_scan_batch_fit_signature.py
tests/test_coverage_exhaustion.py
tests/test_api_analyze_progress.py
tests/test_browser_endpoint_avg_default.py
tests/test_browser_palette.py
tests/test_scattered_starts.py
tests/test_xps_reference.py
tests/test_legacy_parity.py
tests/test_api_analyze.py
tests/test_browser_find_peaks_method_tooltips.py
tests/fixtures/curated_records_snapshot.json
tests/fixtures/xps_legacy_snapshot.json
tests/fixtures/regen_curated_snapshot.py
tests/test_cutover.py
tests/fixtures/machine_records_snapshot.json
tests/test_api_analyze_coverage.py
tests/test_la_continuous_m.py
tests/test_expand_coverage.py
tests/test_browser_legacy_auger.py
tests/test_browser_reference_mode.py
tests/test_conflict_resolution.py
tests/test_browser_find_peaks_progress.py
tests/test_component_support.py
tests/test_legacy_hardening.py
tests/test_browser_bg_window_request.py
tests/test_browser_manual_anchor_cc_migration.py
tests/test_browser_per_tab_state.py
tests/conftest.py
tests/test_browser_find_peaks_coverage.py
tests/test_browser_batch_roi.py
tests/test_chem_state_tier.py
tests/test_browser_identify_frame.py
tests/test_api_fit_full_window_option.py
tests/test_browser_shirley_linear_delist.py
tests/test_browser_find_peaks_tooltip_markup.py
tests/test_short_caveat.py
tests/test_browser_find_peaks_full_window.py
tests/test_shirley_linear_kept.py
tests/test_fit_reproducibility.py
tests/test_differential_evolution_bounds.py
tests/test_background_n_avg.py
tests/test_browser_cc_overlay_repaint.py
tests/test_voigt_contract.py
tests/test_area_sign.py
tests/test_dsg_outside_centre.py
tests/test_browser_find_peaks_endpoint_avg.py
tests/test_la_short_input.py
tests/test_mixed_ds_lacx_e2e.py
tests/test_machine_tier.py
tests/autofit/test_b1s_cl2p_batteries.py
tests/autofit/test_stage2_rereview_findings.py
tests/autofit/test_browser_schema_roundtrip.py
tests/autofit/test_u4f_parity_gate.py
tests/autofit/test_cl2p_freewidth.py
tests/autofit/test_noise_model.py
tests/autofit/test_resolver.py
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-zVEvhsOL' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-juZt6odT' (errno=Operation not permitted)
 CLAUDE.md                                          |   30 +-
 .../codex/f1_stale_statistics_recheck_prompt.txt   |   27 +
 .../codex/f1_stale_statistics_review_prompt.txt    |   67 +
 .../codex/f1_stale_statistics_verdict_runA.md      | 6652 ++++++++++++++++++++
 .../codex/f1_stale_statistics_verdict_runB.md      | 6412 +++++++++++++++++++
 .../plans/2026-09-25-f1-stale-statistics.md        |  123 +
 templates/index.html                               |  191 +-
 tests/js/fit_acceptance.test.js                    |   37 +-
 tests/js/local_lm_descent.test.js                  |    4 +-
 tests/js/scattered_starts.test.js                  |    6 +-
 tests/js/stale_statistics.test.js                  |  384 ++
 tests/js/unsupported_components.test.js            |    7 +-
 tests/test_browser_find_peaks_full_window.py       |   32 +
 13 files changed, 13927 insertions(+), 45 deletions(-)

codex
Auto-Fit captures the key after its provisional shift and model construction, so those changes should not make it discard its own result. I’m checking two remaining risks: whether numeric canonicalisation can equate inputs the fit reads differently, and whether stale save/reload paths preserve the original statistics.
exec
/bin/zsh -lc "sed -n '6615,6632p' docs/autofit/codex/f1_stale_statistics_verdict_runA.md; sed -n '6375,6392p' docs/autofit/codex/f1_stale_statistics_verdict_runB.md; sed -n '4655,4788p' templates/index.html; sed -n '5075,5125p' templates/index.html; sed -n '7610,7770p' templates/index.html; sed -n '7890,7975p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
1. **MAJOR — Auto-Fit stamps edits made during the request as current.** [templates/index.html:7345](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:7345)  
   Start Auto-Fit with background None, then select Linear while the request is pending. Completion checks the tab owner but never compares the request’s model/context key. It stamps the old response with the edited context, then re-stamps it again. Reproduced: request background `none`, live background `linear`, statistics state `current`. χ², uncertainties and the stored curve consequently bypass every stale guard. Compare the captured request key before applying the response.

2. **MAJOR — Local fallback binds old data to the new ROI.** [templates/index.html:8546](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:8546)  
   Start Run Fit, edit the ROI while upload is pending, then let upload fail with a transport error. The fallback receives the original `be/bgSubtracted/bgIntensity` arrays but stamps the current UI key. Running the actual local optimizer reproduced a converged, `current` result fitted over **101 points**, while the current ROI contained **51 points**. The request-context check must also cover the fallback path.

3. **MAJOR — Stale spectrum saves put a different curve under the original fit key.** [templates/index.html:10294](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:10294)  
   Fit ROI 280–290, change it to 281–291, save the stale spectrum, reload, then restore ROI 280–290. Saving replaces `fittedY` with the edited-window curve but retains the original statistics key; loading installs that curve into `fitResult`. Restoring the original ROI now classifies it as `current`. With equal-length windows, figure export and stack rendering accept the wrong curve. Reproduced with a Gaussian: matching key and array length, but maximum curve error approximately **93.77** for amplitude 100. Keep the recomputed export curve out of the restored fit result.

4. **MAJOR — Lock changes leave visible statistics current until another repaint.** [templates/index.html:6037](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:6037)  
   After a fit with supported components and no alternative preview, toggle a parameter lock or Lock All. These paths call `_refreshStartsEvidence`, which need not repaint or render Results. F1’s refresh runs only through `updatePlot`. Reproduced: the accessor returned `stale`, with **zero Results renders and zero plot refreshes**. χ², σ and R remain visible, while exports correctly classify them as stale. Wire these paths into the statistics refresh.

5. **MINOR — Equivalent numeric formatting falsely invalidates statistics.** [templates/index.html:7618](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:7618)  
   Changing an ROI bound from `280` to `280.0` changes the string-based key although the selected data and fit request are identical. Reproduced with the real key function. F1 then hides valid statistics and adds stale-save warnings. Normalize numeric values within the existing shared key.

Validation: **106/107 targeted JS tests passed**; the remaining Python parity subprocess failed because the read-only sandbox has no writable temporary directory. Additional in-memory reproductions confirmed the failures above. The new mocked-key and source-regex tests do not exercise these lifecycle interactions. No files changed.

**VERDICT: NO-GO**
1. **MAJOR — Fallback can certify statistics against the wrong ROI.** [templates/index.html:8546](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:8546)  
   Start Run Fit with ROI 280–290, change it to 284–286 while the request is pending, then encounter a transport failure. The fallback receives the original arrays at line 8040 but stamps the **new live key**. Reproduced with the actual local solver: fit ROI `280.0–290.0`, live ROI `284–286`, statistics state **current**. Check request context before fallback or recompute its inputs.

2. **MAJOR — Reload can attach the edited model’s R-factor to the original fit key.** [templates/index.html:3250](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:3250), [templates/index.html:10402](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:10402)  
   Fit a Gaussian, halve its amplitude, save the stale project, then reload. Project serialization omits `rFactor`; activation recomputes it using the edited peaks because the amplitude edit cleared `fittedY`. Restore the original amplitude: the key becomes current, exposing the wrong cached R. Reproduced **displayed R = 50%, correct R = 0%**. Preserve the original R or prevent stale recomputation from being stored under its key.

3. **MAJOR — Lock edits bypass statistics refresh.** [templates/index.html:6038](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:6038), [templates/index.html:6065](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:6065)  
   After a fit with supported components and no alternative preview, toggle a lock or use Lock All. These handlers only call `_refreshStartsEvidence`, which need not repaint or render Results. Reproduced **actual state stale, rendered state current, zero refreshes**. χ², σ and R remain visible until another action refreshes them. Both handlers need to reach the statistics refresh.

4. **MAJOR — Clear All retains the previous Results table.** [templates/index.html:7668](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:7668)  
   Fit, then Clear All. `clearAllPeaks` nulls the result and calls `updatePlot`, but `_refreshStatsState` explicitly excludes null results from re-rendering. The header clears while Results retains the old statistics and peak table. Reproduced **actual state none, rendered state current**. Handle the transition to `none`; `renderResults` already implements its empty state.

5. **MINOR — Numeric formatting falsely invalidates statistics.** [templates/index.html:7618](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:7618)  
   Change ROI text from `280.0` to `280`. The selected data and model remain identical, but literal string comparison marks statistics stale and suppresses exports. Reproduced unchanged ROI arrays with state **stale**. Canonicalize numeric values within the existing shared key.

Validation: 106 JavaScript tests passed; one Python parity test failed because the read-only sandbox cannot create temporary files. The findings above were reproduced with source-extracted functions; browser tests were not run. No files changed.

**VERDICT: NO-GO.**
// Clear stored background so updatePlot recomputes it
function _invalidateBgCache() {
  if (state.fitResult) state.fitResult.bgIntensity = null;
}

// Clear stored fit envelope so the fallback (modelFull + bg) is used after a manual peak edit
function _invalidateFittedY() {
  if (state.fitResult) state.fitResult.fittedY = null;
}

function _clampShirleyIter() {
  const el = document.getElementById('shirley-iter');
  let v = parseInt(el.value);
  if (isNaN(v)) return;
  if (v < 1) el.value = 1;
  else if (v > 50) el.value = 50;
}

// The background window. The user types two binding energies; the window
// is every grid point with lo <= BE <= hi, INCLUSIVE at both ends — the same
// rule getROIData uses for the ROI. This is the single definition shared by
// the preview (computeBackgroundCore) and both /api/fit request builders,
// which send end_idx = i1 + 1 because the backend slices Python-end-exclusive
// (unit 1c of docs/superpowers/plans/2026-09-02-background-architecture-
// sealed-fit-record.md, round-5 amendment — before 1c the builders sent the
// nearest grid index per bound and end_idx = i1, so the fit anchored one
// point inside the window the user drew).
// Returns inclusive indices { i0, i1 }. A blank/NaN bound, or fewer than two
// grid points inside the bounds, falls back to the full range.
// Contract notes (Codex round 1, both runs): (a) the window is the contiguous
// index span from the FIRST to the LAST in-range point — exact on a monotonic
// grid, which is what createTab guarantees (it sorts descending) and what
// every saved project written by this app carries; a hand-edited
// non-monotonic rawBE would make the span include out-of-window rows, and
// the preview and the request would still agree. (b) Indices are computed on
// the frontend grid before uploadToBackend rounds BE to 4 decimals; the
// backend only ever applies the indices to that same-length, same-order
// session grid, so rounding cannot change which rows are used.
function _bgWindowIndices(be, bgStart, bgEnd) {
  const n = be.length;
  const full = { i0: 0, i1: n - 1 };
  const a = parseFloat(bgStart), b = parseFloat(bgEnd);
  if (!Number.isFinite(a) || !Number.isFinite(b)) return full;
  const lo = Math.min(a, b), hi = Math.max(a, b);
  let i0 = -1, i1 = -1;
  for (let i = 0; i < n; i++) {
    if (be[i] >= lo && be[i] <= hi) { if (i0 < 0) i0 = i; i1 = i; }
  }
  if (i0 < 0 || i1 - i0 < 1) return full;
  return { i0, i1 };
}

// Pure-functional background computation. Takes explicit `settings`
// (matches the shape of tab.ui — bgType, bgStart, bgEnd, shirleyIter,
// endpointAvg) instead of reading from DOM. Used by stack-view render
// to reproduce a source tab's background from its persisted ui state.
// computeBackground() below is a thin DOM-reading wrapper for callers
// in the single-tab plot path.
function computeBackgroundCore(be, intensity, settings) {
  const type = settings.bgType;
  const iter = parseInt(settings.shirleyIter) || 5;
  const nAvg = parseInt(settings.endpointAvg) || 1;

  // Manual anchor background uses its own anchor points, not bg-start/end
  if (type === 'manual') return manualAnchorBackground(be, intensity);

  // The background window — the one definition shared with both /api/fit
  // request builders (see _bgWindowIndices). A blank bound or a window with
  // fewer than two points falls back to the full range inside the helper;
  // slicing the full range below is then a no-op.
  const { i0, i1 } = _bgWindowIndices(be, settings.bgStart, settings.bgEnd);

  // Slice data to background region
  const beSub = be.slice(i0, i1 + 1);
  const inSub = intensity.slice(i0, i1 + 1);

  // Compute background on the sliced region — apply endpoint averaging for Shirley types
  let bgSub;
  if (type === 'shirley') bgSub = shirleyBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
  else if (type === 'smart') bgSub = smartBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
  else if (type === 'smart_exp') bgSub = smartExperimentalBackground(beSub, inSub, iter, nAvg);
  else if (type === 'shirley_linear') bgSub = shirleyLinearBackground(beSub, inSub, iter, nAvg);
  else if (type === 'linear') bgSub = linearBackground(beSub, inSub);
  // Averaged for the same reason as Shirley types: the Tougaard amplitude
  // is anchored at the high-BE edge, so endpoint noise feeds the anchor
  // directly. Mirrors fitting.py's run_fit / compute_background_only.
  else if (type === 'tougaard') bgSub = tougaardBackground(beSub, _applyEndpointAveraging(inSub, nAvg));
  else return new Array(be.length).fill(0);

  // Extend background across full data range:
  // - Points before bg region: hold first bg value (flat)
  // - Points inside bg region: use computed bg
  // - Points after bg region: hold last bg value (flat)
  const full = new Array(be.length).fill(0);
  const bgLeft  = bgSub[0];
  const bgRight = bgSub[bgSub.length - 1];

  for (let i = 0; i < be.length; i++) {
    if (i < i0) full[i] = bgLeft;
    else if (i <= i1) full[i] = bgSub[i - i0];
    else full[i] = bgRight;
  }

  return full;
}

// Thin DOM-reading wrapper used by single-tab updatePlot. Stack render
// path calls computeBackgroundCore directly with source-tab settings.
function computeBackground(be, intensity) {
  return computeBackgroundCore(be, intensity, {
    bgType:      document.getElementById('bg-type').value,
    shirleyIter: document.getElementById('shirley-iter').value,
    endpointAvg: document.getElementById('bg-endpoint-avg').value,
    bgStart:     document.getElementById('bg-start').value,
    bgEnd:       document.getElementById('bg-end').value,
  });
}

// ═══════════════════════════════════════════════════
// FILE PARSING
// ═══════════════════════════════════════════════════
function parseCSV(text) {
  const lines = text.trim().split('\n');
  const be = [], inten = [];
  for (const line of lines) {
    if (!line.trim() || line.startsWith('#') || line.startsWith('%')) continue;
    const parts = line.trim().split(/[\s,\t;]+/);
    if (parts.length < 2) continue;
    const x = parseFloat(parts[0]), y = parseFloat(parts[1]);
    if (isFinite(x) && isFinite(y)) { be.push(x); inten.push(y); }
  }
  return { be, inten };
}


function getCorrectedBE() {
  const shift = isNaN(state.ccShift) ? 0 : state.ccShift;
  return state.rawBE.map(b => b - shift);
}

// ═══════════════════════════════════════════════════
// ROI FILTERING
// ═══════════════════════════════════════════════════
function getROIData() {
  const roiMinRaw = parseFloat(document.getElementById('roi-min').value);
  const roiMaxRaw = parseFloat(document.getElementById('roi-max').value);
  // NaN bounds mean the field is empty — use full range rather than filtering everything out
  const roiMin = isNaN(roiMinRaw) ? -Infinity : roiMinRaw;
  const roiMax = isNaN(roiMaxRaw) ?  Infinity : roiMaxRaw;
  const corrBE = getCorrectedBE();
  const be = [], inten = [];
  for (let i = 0; i < corrBE.length; i++) {
    if (corrBE[i] >= roiMin && corrBE[i] <= roiMax) {
      be.push(corrBE[i]);
      inten.push(state.rawIntensity[i]);
    }
  }
  return { be, inten };
}

// ── ROI past the data / centre outside the data (2026-09-25) ─────────────
// WARN, NEVER REINTERPRET. getROIData() already selects the corrected
// energies inside [roi-min, roi-max], so an ROI past the data is clamped to
// the data in every fit, background, area and export — the defect was that
// nothing said so. This reports the window actually used; it writes nothing
// back into the fields, the peaks or the fit-evidence key. Find Peaks sends
// the same two numbers against the same corrected energies to a server mask
// of the same inclusive form, so this one window is the one both use.
// Plan: docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md.
function _roiWindowStatus() {
  const corrBE = (typeof getCorrectedBE === 'function' && state.rawBE && state.rawBE.length) ? getCorrectedBE() : [];
  if (!corrBE.length) return { state: 'no-data' };
  let dMin = Infinity, dMax = -Infinity;
  for (const v of corrBE) { if (v < dMin) dMin = v; if (v > dMax) dMax = v; }
  const lo = parseFloat(document.getElementById('roi-min').value);
  const hi = parseFloat(document.getElementById('roi-max').value);
  const { be } = getROIData();
  let sMin = Infinity, sMax = -Infinity;
  for (const v of be) { if (v < sMin) sMin = v; if (v > sMax) sMax = v; }
  const base = { dMin, dMax, lo, hi, sMin, sMax, n: be.length };
  if (Number.isFinite(lo) && Number.isFinite(hi) && lo > hi) return { ...base, state: 'inverted' };
  if (!be.length) return { ...base, state: 'no-overlap' };
  // one sampling step = median |Δ corrected BE|: within a step there is no
  // sample the window could have included, so a toFixed(1) rounding of an
  // edge is not "past the data" (a grid-relative criterion, not a threshold

// The evidence belongs to the FIT THAT PRODUCED IT: the model (everything the
// request reads from a peak) AND its context (background type and window,
// endpoint averaging, Shirley iterations, ROI, manual anchors, charge shift).
// The key is taken when the result is stored; it is compared, never
// invalidated by hand, so no edit path can be forgotten: after any change to
// a parameter, lock, shape, link, the peak list, the background, the ROI, the
// anchors or the charge correction — or an undo / history restore that brings
// back other values — the panel says the comparison no longer applies,
// nothing can be previewed or applied, and saves/exports carry no counts. A
// name, colour or visibility is not part of a fit and does not invalidate it.
const _STARTS_MODEL_FIELDS = ['id', 'shape', 'center', 'fwhm', 'amplitude', 'glMix', 'asymmetry', 'dsAlpha', 'dsGamma',
  'laAlpha', 'laBeta', 'laM', 'caAlpha', 'caBeta', 'caM', 'linked', 'linkOffset', 'linkRatio', '_afAsymMin', '_afAsymMax',
  'fixCenter', 'fixFwhm', 'fixAmplitude', 'fixGlMix', 'fixAsymmetry', 'fixDsAlpha', 'fixDsGamma',
  'fixLaAlpha', 'fixLaBeta', 'fixLaM', 'fixCaAlpha', 'fixCaBeta', 'fixCaM'];
const _STARTS_UI_FIELDS = ['bgType', 'bgStart', 'bgEnd', 'shirleyIter', 'endpointAvg', 'roiMin', 'roiMax'];
function _startsModelKey(peaks, ui, ccShift, anchors) {
  return JSON.stringify({
    p: (peaks || []).map(q => _STARTS_MODEL_FIELDS.map(k => (q[k] === undefined ? null : q[k]))),
    u: _STARTS_UI_FIELDS.map(k => String((ui || {})[k] ?? '')),
    s: Number(ccShift) || 0,
    a: (anchors || []).map(v => [v.x, v.y]),
  });
}
// Two keys describe the same fit when they are equal after the form fields'
// numbers are canonicalised: '280' and '280.0' select the same data and send
// the same request (F1, Codex round 1). Compared, never rewritten, so keys
// already persisted in saved files keep matching.
function _fitKeyCanon(k) {
  if (typeof k !== 'string') return k;
  const memo = _fitKeyCanon._memo || (_fitKeyCanon._memo = new Map());
  let c = memo.get(k);
  if (c !== undefined) return c;
  try {
    const o = JSON.parse(k);
    if (o && Array.isArray(o.u)) o.u = o.u.map(v => (typeof v === 'string' && v.trim() !== '' && Number.isFinite(Number(v))) ? String(Number(v)) : v);
    c = JSON.stringify(o);
  } catch (_) { c = k; }
  if (memo.size > 256) memo.clear();
  memo.set(k, c);
  return c;
}
function _sameFitKey(a, b) { return !!a && !!b && (a === b || _fitKeyCanon(a) === _fitKeyCanon(b)); }
// The key of the ACTIVE tab as it stands now (live model, live controls).
function _startsLiveKey() {
  const ui = (typeof tabManager !== 'undefined' && tabManager && tabManager._captureUI) ? tabManager._captureUI() : {};
  return _startsModelKey(state.peaks, ui, state.ccShift, typeof _getManualAnchors === 'function' ? _getManualAnchors() : []);
}
// The key of a tab RECORD (project save runs after _syncActiveToRecord).
function _startsRecordKey(t) { return _startsModelKey(t.peaks, t.ui, t.ccShift, t.manualAnchors); }
// The starts evidence of `fr` if it still describes the fit whose key is `key`, else null.
function _startsIfCurrent(fr, key) {
  const st = fr && fr.starts;
  if (!st || !fr.startsModelKey || !_sameFitKey(fr.startsModelKey, key)) return null;
  return st;
}
// Unit F1 (2026-09-25): the fit STATISTICS (chi-square, sigma, R-factor, RMSE
// and the stored fitted curve) are bound to the fit that produced them by the
// SAME key — no second mechanism. One accessor classifies a result:
//   'current'    the key matches: they describe the model shown;
//   'stale'      the key differs: they belong to the previous model (an edit,
//                a Find Peaks apply, an undo or a history restore since);
//   'unverified' the result carries no key (saved before this unit): whether
//                it described the saved model cannot be known — shown, with a
//                note to re-run;
//   'none'       no result.
// The sealed fit record absorbs this: its record carries key and statistics.
function _statsState(fr, key) {
  if (!fr) return 'none';
  if (!fr.startsModelKey) return 'unverified';
  return _sameFitKey(fr.startsModelKey, key) ? 'current' : 'stale';
}
function _statsLiveState() { return _statsState(state.fitResult, _startsLiveKey()); }
// A record's result judged against the RECORD's key (project save, stack tabs).
function _statsRecordState(t) { return _statsState(t && t.fitResult, t ? _startsRecordKey(t) : ''); }
const _STATS_STALE_NOTE = 'The model or its fit settings changed after this fit: its \u03c7\u00b2, R-factor, RMSE and uncertainties belong to the previous model and are not reported. Run Fit to obtain statistics for this model.';
const _STATS_UNVERIFIED_NOTE = 'This result was saved without the record that binds it to its model, so it cannot be confirmed that its \u03c7\u00b2, R-factor and uncertainties describe the model shown. Run Fit to confirm.';
function _statsNote(st) { return st === 'stale' ? _STATS_STALE_NOTE : st === 'unverified' ? _STATS_UNVERIFIED_NOTE : ''; }
// Fields a save adds beside the result (the key itself is saved as always).
function _statsSaveFields(st) {
  return (st === 'stale' || st === 'unverified') ? { statisticsState: st, statisticsNote: _statsNote(st) } : {};
}
// Keep the visible statistics honest after an edit that only repainted the
// chart: re-render Results when the state it rendered differs; re-apply the
// header / status bar / R always (cheap, no inputs there).
function _refreshStatsState() {
  const st = _statsLiveState();
  const el = document.getElementById('results-area');
  // 'none' too: Clear All nulls the result and only repaints (Codex round 1)
  if (el && el.getAttribute('data-stats-state') !== st && (state.fitResult || el.getAttribute('data-stats-state')) && typeof renderResults === 'function') renderResults();   // applies the header / status bar too
  else _applyStatDisplay(state.fitResult);
  if (typeof _updateRFactorUI === 'function') _updateRFactorUI(state.fitResult ? state.fitResult.rFactor : null);
}

// After anything that may have changed the model or its context without going
// through a Results re-render (a lock toggle, Lock All, a background or ROI
// control): take a stale alternative overlay off the chart and bring the
// VISIBLE panel up to date (counts -> "the model has changed since this fit").
function _refreshStartsEvidence(repaint, fromPlot) {
  // F1: chi-square / sigma / R follow the same key, from every caller (lock
  // toggles and Lock All reach here without a repaint; Codex round 1)
  _refreshStatsState();
  const hadAlt = !!(_historyPreview && typeof _historyPreview.snapId === 'string' && _historyPreview.snapId.startsWith('alt:'));
  _dropStaleAltPreview();
  if (repaint && hadAlt && !_historyPreview && typeof updatePlot === 'function') updatePlot();
  // The support verdicts are keyed the same way. If any is now stale (or
  // current again after an undo), every consumer that renders it must follow:
  // the Results table, the Quantify tab and the sidebar cards, not only the
  // starts panel. Rendered once, only when the visible state would change.
  // Each consumer is compared with ITS OWN rendering (a caller may have
  // redrawn the sidebar already, so the sidebar cannot vouch for the tables).
  const key = _startsLiveKey();
  const flaggedNow = state.peaks.filter(p => _isUnsupported(p, key)).map(p => String(p.id)).sort().join(',');
  const shownIn = sel => Array.from(document.querySelectorAll(sel)).map(e => e.getAttribute('data-peak-id')).sort().join(',');
  let rendered = false;
  if (shownIn('#peak-list .unsupported-badge') !== flaggedNow) { _patchPeakCardsForSupport(); rendered = true; }
  if (state.fitResult && shownIn('.results-table .unsupported-row') !== flaggedNow && typeof renderResults === 'function') { renderResults(); rendered = true; }   // renders Quantify and the starts panel too
  if (!fromPlot && state.chart && state.chart.data && typeof updatePlot === 'function') {
    const chartFlagged = (state.chart.data.datasets || []).filter(d => d._unsupported).map(d => String(d._peakId)).sort().join(',');
    if (chartFlagged !== flaggedNow) { updatePlot(); return; }
  }
  if (rendered) return;
  const el = document.querySelector('.starts-panel');
  if (el && state.fitResult) el.outerHTML = _startsPanelHtml(state.fitResult);
}

// An alternative's preview overlay is only valid beside the result it came from.
function _dropStaleAltPreview() {
  if (_historyPreview && typeof _historyPreview.snapId === 'string' && _historyPreview.snapId.startsWith('alt:') &&
      !(state.fitResult && _historyPreview.altKey === state.fitResult.startsModelKey && _startsIfCurrent(state.fitResult, _startsLiveKey()))) {
    _historyPreview = null;
  }
}

// What is persisted with a saved fit: the counts, never the alternatives'
// parameter sets (regenerable: the starts are a pure function of the request).
function _startsForSave(st) {
  if (!st) return null;
  if (!st.ran) return { ran: false, reason: st.reason || null };
  const alts = st.alternatives || [];
  return { ran: true, n_run: st.n_run, n_converged: st.n_converged, n_same_as_fit: st.n_same_as_fit,
           n_not_better_elsewhere: st.n_not_better_elsewhere,
           n_in_alternatives: st.n_in_alternatives ?? alts.reduce((n, a) => n + a.n_starts, 0),
           n_alternatives: alts.length || st.n_alternatives || 0,
           best_alternative_chi2r: alts.length ? alts[0].chi2r : (st.best_alternative_chi2r ?? null) };
}

// Counts STARTS and SOLUTIONS separately: three starts reaching one different
// solution is "3 starts found a DIFFERENT solution", not "one start".
function _startsSummaryText(st) {
  if (!st || !st.ran) return '';
  const nSol = (st.alternatives ? st.alternatives.length : st.n_alternatives) || 0;
  const nIn = st.n_in_alternatives ?? (st.alternatives || []).reduce((n, a) => n + a.n_starts, 0);
  const nb = st.n_not_better_elsewhere || 0, failed = st.n_run - st.n_converged;
  let t = `${st.n_same_as_fit} of ${st.n_run} scattered starts reached this solution`;
  const parts = [];
  if (nSol) parts.push(`${nIn} found ${nSol === 1 ? 'a DIFFERENT solution' : nSol + ' DIFFERENT solutions'} with a lower χ²ᵣ`);
  if (nb) {
    const worst = (st.not_better_chi2r && st.not_better_chi2r.length) ? ` (χ²ᵣ ${st.not_better_chi2r.map(c => c.toFixed(2)).join(', ')})` : '';
    parts.push(`${nb} ended in a solution that is not better${worst}`);
  }
// that moves a component more than 1 eV from where the student put it is the
// measured trap (a lower chi-square bought by a chemically absurd relocation),
// so that case — and only that case — asks first, naming the component and
// the distance.
async function useAlternative(k) {
  const alt = _currentAlternative(k);
  const peaks = alt && _altPeaks(alt);
  if (!peaks) { notify(_STARTS_STALE_MSG, 'amber', true); return; }
  const shift = alt.largest_centre_shift_from_start;
  const name = _startsPeakName(shift.id);
  if (Math.abs(shift.ev) > _STARTS_SHIFT_RED_EV &&
      !confirm(`This solution moves ${name} by ${_startsEv(shift.ev)} from where you placed it. Apply?`)) return;
  const chosen = { fromChi: state.fitResult.starts.fit.chi2r, toChi: alt.chi2r, shiftName: name, shiftEv: shift.ev };
  if (_historyPreview) _historyClearPreview();
  await runFit({ startPeaks: peaks, chosenAlternative: chosen });
}

async function runFit(opts = {}) {
  if (!state.rawBE.length) { notify('Load a spectrum first.', 'red', true); return; }
  if (!state.peaks.length) { notify('Add at least one peak.', 'red'); return; }
  pushUndo();

  _showFitSpinner();
  document.getElementById('sb-msg').textContent = 'Fitting\u2026';

  // Capture the tab that owns this fit so that if the user switches tabs
  // mid-request, we can discard the stale result instead of corrupting the
  // now-active tab's state.
  const fittingTab = _opOwner();

  const { be, inten } = getROIData();
  const bgIntensity = computeBackground(be, inten);
  const bgSubtracted = inten.map((v, i) => v - bgIntensity[i]);

  // Try Flask backend first
  let backendResult = null;
  let ctxAtRequest = null;   // set with the other request inputs; read again by the local fallback
  try {
    const bgType  = document.getElementById('bg-type').value;
    const bgStart = parseFloat(document.getElementById('bg-start').value);
    const bgEnd   = parseFloat(document.getElementById('bg-end').value);
    // Inclusive bg window — the same point set computeBackgroundCore draws;
    // the backend slices end-exclusive, so the request sends i1 + 1.
    const bgWin = _bgWindowIndices(be, bgStart, bgEnd);
    // EVERY request input is read from the owner before the upload await:
    // peaks, method, endpoint averaging and manual anchors (Codex round 2: a
    // request could carry A's spectrum with B's averaging and anchors).
    // opts.startPeaks: the request starts from an adopted alternative; the live
    // model is still the student's until this fit succeeds (useAlternative).
    const startModel = opts.startPeaks || state.peaks;
    const peakSpecs = startModel.map(peakToBackendSpec);
    // scattered-starts check: decided HERE, with the other request inputs,
    // before the first await (a tab switch during the upload must not turn it off)
    const nStarts = _startsUnlinkedCount(startModel) >= 2 ? _STARTS_N : 0;
    // the live model and its fit context as the student pressed the button: a
    // result must not be written over a model that was edited while it ran
    ctxAtRequest = _startsLiveKey();
    const fitMethod = document.getElementById('fit-method').value;
    const epAvgVal = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
    const bgPayload = { method: bgType, start_idx: bgWin.i0, end_idx: bgWin.i1 + 1, endpoint_avg: epAvgVal };
    if (bgType === 'manual') {
      // Anchors are stored in corrected-BE space, same frame as the uploaded
      // session data; backend expects [x, y] pairs.
      bgPayload.manual_bg = _getManualAnchors().map(a => [a.x, a.y]);
    }
    // Transport failures (server unreachable, timeout, non-JSON reply) are
    // the ONLY reason to fall back to the local optimiser. A server-side
    // validation error or a non-converged optimisation surfaces its message
    // and leaves the model untouched (unit A0: nothing is shown as a fit
    // result unless it converged; an HTTP 400 is not a reason to silently
    // switch engines).
    // Only a genuine transport failure (network rejection, abort, unparsable
    // 2xx body) is marked for fallback; server errors carry `serverError`.
    const _asTransport = (e) => {
      if (e && !e.serverError && (e instanceof TypeError || e.name === 'AbortError' || e instanceof SyntaxError)) e.transportFailure = true;
      throw e;
    };
    let sessionId;
    try { sessionId = await uploadToBackend(be, inten); } catch (e) { _asTransport(e); }
    const fitReq = {
      session_id: sessionId,
      background: bgPayload,
      peaks: peakSpecs,
      fit_method: fitMethod,
      n_perturb: 3,
      n_starts: nStarts       // the server also skips it for the global methods

exec
/bin/zsh -lc 'node --test tests/js/stale_statistics.test.js tests/js/fit_acceptance.test.js tests/js/local_lm_descent.test.js tests/js/scattered_starts.test.js tests/js/unsupported_components.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 exited 1 in 5941ms:
# Subtest: A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
ok 1 - A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
  ---
  duration_ms: 10.8636
  type: 'test'
  ...
# Subtest: a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
ok 2 - a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
  ---
  duration_ms: 6.085366
  type: 'test'
  ...
# Subtest: a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
ok 3 - a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
  ---
  duration_ms: 2.911769
  type: 'test'
  ...
# Subtest: a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
ok 4 - a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
  ---
  duration_ms: 8.371754
  type: 'test'
  ...
# Subtest: a converged backend result is applied (sanity)
ok 5 - a converged backend result is applied (sanity)
  ---
  duration_ms: 2.81376
  type: 'test'
  ...
# Subtest: the engine/objective labels of a fit result survive spectrum and project save/load
ok 6 - the engine/objective labels of a fit result survive spectrum and project save/load
  ---
  duration_ms: 0.789452
  type: 'test'
  ...
# Subtest: an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
ok 7 - an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
  ---
  duration_ms: 2.718957
  type: 'test'
  ...
# Subtest: an HTTP 502 on the upload is a server failure, not a transport failure
ok 8 - an HTTP 502 on the upload is a server failure, not a transport failure
  ---
  duration_ms: 2.553755
  type: 'test'
  ...
# Subtest: uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
ok 9 - uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
  ---
  duration_ms: 1.618857
  type: 'test'
  ...
# Subtest: every consumer that prints the goodness-of-fit statistic routes through the statistic identity
ok 10 - every consumer that prints the goodness-of-fit statistic routes through the statistic identity
  ---
  duration_ms: 0.861926
  type: 'test'
  ...
# Subtest: uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
ok 11 - uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
  ---
  duration_ms: 0.632118
  type: 'test'
  ...
# Subtest: a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
ok 12 - a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
  ---
  duration_ms: 1.501567
  type: 'test'
  ...
# Subtest: starting-point helpers: keyed on the persisted objective, weighted results untouched
ok 13 - starting-point helpers: keyed on the persisted objective, weighted results untouched
  ---
  duration_ms: 2.973301
  type: 'test'
  ...
# Subtest: Quantify shows the starting-point banner for a local result and not for a weighted one
ok 14 - Quantify shows the starting-point banner for a local result and not for a weighted one
  ---
  duration_ms: 3.935038
  type: 'test'
  ...
# Subtest: every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
ok 15 - every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
  ---
  duration_ms: 1.651916
  type: 'test'
  ...
# Subtest: project save derives the designation from the objective for an older local result lacking the new fields
ok 16 - project save derives the designation from the objective for an older local result lacking the new fields
  ---
  duration_ms: 6.872652
  type: 'test'
  ...
# Subtest: stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
ok 17 - stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
  ---
  duration_ms: 1.013938
  type: 'test'
  ...
# Subtest: _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
ok 18 - _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
  ---
  duration_ms: 3.377541
  type: 'test'
  ...
# Subtest: history preview glow is keyed on the dataset flag, not the label text
ok 19 - history preview glow is keyed on the dataset flag, not the label text
  ---
  duration_ms: 0.676383
  type: 'test'
  ...
# Subtest: spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
ok 20 - spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
  ---
  duration_ms: 0.407886
  type: 'test'
  ...
# Subtest: _applyStatDisplay clears header, tooltip, caption and value together on local → none
ok 21 - _applyStatDisplay clears header, tooltip, caption and value together on local → none
  ---
  duration_ms: 3.021382
  type: 'test'
  ...
# Subtest: _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
ok 22 - _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
  ---
  duration_ms: 1.596983
  type: 'test'
  ...
# Subtest: fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
ok 23 - fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
  ---
  duration_ms: 1.236043
  type: 'test'
  ...
# Subtest: undo/redo snapshots carry and restore model provenance
ok 24 - undo/redo snapshots carry and restore model provenance
  ---
  duration_ms: 3.170645
  type: 'test'
  ...
# Subtest: round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
ok 25 - round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
  ---
  duration_ms: 1.1295
  type: 'test'
  ...
# Subtest: _provenanceOf derives a designation from a live local result, and undo snapshots use it
ok 26 - _provenanceOf derives a designation from a live local result, and undo snapshots use it
  ---
  duration_ms: 2.421303
  type: 'test'
  ...
# Subtest: batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
ok 27 - batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
  ---
  duration_ms: 0.308229
  type: 'test'
  ...
# Subtest: the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
ok 28 - the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
  ---
  duration_ms: 2.105811
  type: 'test'
  ...
# Subtest: round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
ok 29 - round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
  ---
  duration_ms: 0.744975
  type: 'test'
  ...
# Subtest: the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
ok 30 - the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
  ---
  duration_ms: 2.407637
  type: 'test'
  ...
# Subtest: the sidebar banner is sticky at the top of the scrolling panel body
ok 31 - the sidebar banner is sticky at the top of the scrolling panel body
  ---
  duration_ms: 0.247031
  type: 'test'
  ...
# Subtest: the sidebar banner shows on a stack tab whose visible entries draw a local source fit
ok 32 - the sidebar banner shows on a stack tab whose visible entries draw a local source fit
  ---
  duration_ms: 2.352168
  type: 'test'
  ...
# Subtest: every stack chart repaint path refreshes the sidebar designation before any early return
ok 33 - every stack chart repaint path refreshes the sidebar designation before any early return
  ---
  duration_ms: 0.348854
  type: 'test'
  ...
# Subtest: closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
ok 34 - closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
  ---
  duration_ms: 0.172361
  type: 'test'
  ...
# Subtest: W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
ok 35 - W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
  ---
  duration_ms: 2.48537
  type: 'test'
  ...
# Subtest: TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
ok 36 - TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
  ---
  duration_ms: 3.886225
  type: 'test'
  ...
# Subtest: adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
ok 37 - adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
  ---
  duration_ms: 2.478044
  type: 'test'
  ...
# Subtest: adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
ok 38 - adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
  ---
  duration_ms: 2.747779
  type: 'test'
  ...
# Subtest: adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
ok 39 - adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
  ---
  duration_ms: 2.500031
  type: 'test'
  ...
# Subtest: adoption: success records the choice, the starts evidence and the key of the model it describes
ok 40 - adoption: success records the choice, the starts evidence and the key of the model it describes
  ---
  duration_ms: 2.337944
  type: 'test'
  ...
# Subtest: an ordinary Run Fit on one unlinked component does not ask for the starts check
ok 41 - an ordinary Run Fit on one unlinked component does not ask for the starts check
  ---
  duration_ms: 2.518876
  type: 'test'
  ...
# Subtest: a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
ok 42 - a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
  ---
  duration_ms: 3.171049
  type: 'test'
  ...
# Subtest: a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
ok 43 - a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
  ---
  duration_ms: 6.195349
  type: 'test'
  ...
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/tests/js/local_lm_server_parity_backend.py", line 12, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics']
# Subtest: A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
ok 44 - A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
  ---
  duration_ms: 1297.422367
  type: 'test'
  ...
# Subtest: A01 replay: the linked U 4f pair also descends
ok 45 - A01 replay: the linked U 4f pair also descends
  ---
  duration_ms: 238.851552
  type: 'test'
  ...
# Subtest: noiseless Gaussian: amplitude 10 started at 5 is recovered
ok 46 - noiseless Gaussian: amplitude 10 started at 5 is recovered
  ---
  duration_ms: 13.141943
  type: 'test'
  ...
# Subtest: acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
ok 47 - acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
  ---
  duration_ms: 9.022666
  type: 'test'
  ...
# Subtest: a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
ok 48 - a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
  ---
  duration_ms: 13.02289
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
ok 49 - bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
  ---
  duration_ms: 11.025661
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
ok 50 - bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
  ---
  duration_ms: 8.545056
  type: 'test'
  ...
# Subtest: a weak component the data DO hold is no longer forced up to an amplitude of 1
ok 51 - a weak component the data DO hold is no longer forced up to an amplitude of 1
  ---
  duration_ms: 8.669859
  type: 'test'
  ...
# Subtest: derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
ok 52 - derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
  ---
  duration_ms: 42.34
  type: 'test'
  ...
# Subtest: derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
ok 53 - derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
  ---
  duration_ms: 25.51341
  type: 'test'
  ...
# Subtest: a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
ok 54 - a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
  ---
  duration_ms: 8.2653
  type: 'test'
  ...
# Subtest: linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
ok 55 - linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
  ---
  duration_ms: 12.41741
  type: 'test'
  ...
# Subtest: round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
ok 56 - round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
  ---
  duration_ms: 11.374583
  type: 'test'
  ...
# Subtest: round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
ok 57 - round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
  ---
  duration_ms: 10.004974
  type: 'test'
  ...
# Subtest: round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
ok 58 - round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
  ---
  duration_ms: 11.067673
  type: 'test'
  ...
# Subtest: A01 replay targets converge to constrained stationary points (C1s and U 4f)
ok 59 - A01 replay targets converge to constrained stationary points (C1s and U 4f)
  ---
  duration_ms: 1361.257638
  type: 'test'
  ...
# Subtest: round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
ok 60 - round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
  ---
  duration_ms: 56.797943
  type: 'test'
  ...
# Subtest: round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
ok 61 - round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
  ---
  duration_ms: 21.923631
  type: 'test'
  ...
# Subtest: round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
ok 62 - round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
  ---
  duration_ms: 12.035087
  type: 'test'
  ...
# Subtest: round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
ok 63 - round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
  ---
  duration_ms: 74.059126
  type: 'test'
  ...
# Subtest: round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
ok 64 - round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
  ---
  duration_ms: 1164.357569
  type: 'test'
  ...
# Subtest: round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
ok 65 - round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
  ---
  duration_ms: 22.198208
  type: 'test'
  ...
# Subtest: round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
ok 66 - round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
  ---
  duration_ms: 11.488342
  type: 'test'
  ...
# Subtest: weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
ok 67 - weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
  ---
  duration_ms: 8.766636
  type: 'test'
  ...
# Subtest: server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
not ok 68 - server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
  ---
  duration_ms: 1324.410765
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/tests/js/local_lm_descent.test.js:455:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/tests/js/local_lm_server_parity_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/tests/js/local_lm_server_parity_backend.py", line 12, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/tests/js/local_lm_descent.test.js:468:31)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom
ok 69 - the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom
  ---
  duration_ms: 23.306704
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
ok 70 - an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
  ---
  duration_ms: 26.593098
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
ok 71 - an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
  ---
  duration_ms: 18.676384
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
ok 72 - round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
  ---
  duration_ms: 8.395436
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
ok 73 - round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
  ---
  duration_ms: 8.461947
  type: 'test'
  ...
# Subtest: recovery from an amplitude of exactly zero (the new floor is not a trap)
ok 74 - recovery from an amplitude of exactly zero (the new floor is not a trap)
  ---
  duration_ms: 9.88959
  type: 'test'
  ...
# Subtest: summary wording: counts of STARTS and of SOLUTIONS, never certification
ok 75 - summary wording: counts of STARTS and of SOLUTIONS, never certification
  ---
  duration_ms: 18.309939
  type: 'test'
  ...
# Subtest: no alternative: one line, no table
ok 76 - no alternative: one line, no table
  ---
  duration_ms: 11.997338
  type: 'test'
  ...
# Subtest: alternatives: "Your fit" first, own areas per component, the moved component named and coloured
ok 77 - alternatives: "Your fit" first, own areas per component, the moved component named and coloured
  ---
  duration_ms: 8.539037
  type: 'test'
  ...
# Subtest: RED band: applying asks first and NAMES the component and the distance
ok 78 - RED band: applying asks first and NAMES the component and the distance
  ---
  duration_ms: 8.563933
  type: 'test'
  ...
# Subtest: adoption never writes the live model itself: the alternative is only the START of a fit, and the choice rides along
ok 79 - adoption never writes the live model itself: the alternative is only the START of a fit, and the choice rides along
  ---
  duration_ms: 8.215703
  type: 'test'
  ...
# Subtest: below the red band there is no dialog
ok 80 - below the red band there is no dialog
  ---
  duration_ms: 22.718208
  type: 'test'
  ...
# Subtest: a locked parameter is never moved by an alternative
ok 81 - a locked parameter is never moved by an alternative
  ---
  duration_ms: 7.444891
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a peak deleted: the panel says so and nothing can be applied
ok 82 - evidence is bound to the fitted model — a peak deleted: the panel says so and nothing can be applied
  ---
  duration_ms: 8.11274
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a shape changed (GL -> DS) and the centre moved: the panel says so and nothing can be applied
ok 83 - evidence is bound to the fitted model — a shape changed (GL -> DS) and the centre moved: the panel says so and nothing can be applied
  ---
  duration_ms: 8.725251
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a lock toggled: the panel says so and nothing can be applied
ok 84 - evidence is bound to the fitted model — a lock toggled: the panel says so and nothing can be applied
  ---
  duration_ms: 10.159103
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a link added: the panel says so and nothing can be applied
ok 85 - evidence is bound to the fitted model — a link added: the panel says so and nothing can be applied
  ---
  duration_ms: 9.605785
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — an undo that restored other values: the panel says so and nothing can be applied
ok 86 - evidence is bound to the fitted model — an undo that restored other values: the panel says so and nothing can be applied
  ---
  duration_ms: 9.097121
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — an auto-fit asymmetry bound changed: the panel says so and nothing can be applied
ok 87 - evidence is bound to the fitted model — an auto-fit asymmetry bound changed: the panel says so and nothing can be applied
  ---
  duration_ms: 9.651805
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — the background type changed: the panel says so and nothing can be applied
ok 88 - evidence is bound to the fitted model — the background type changed: the panel says so and nothing can be applied
  ---
  duration_ms: 7.479329
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — the background window moved: the panel says so and nothing can be applied
ok 89 - evidence is bound to the fitted model — the background window moved: the panel says so and nothing can be applied
  ---
  duration_ms: 6.89161
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — endpoint averaging changed: the panel says so and nothing can be applied
ok 90 - evidence is bound to the fitted model — endpoint averaging changed: the panel says so and nothing can be applied
  ---
  duration_ms: 7.20498
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — the ROI changed: the panel says so and nothing can be applied
ok 91 - evidence is bound to the fitted model — the ROI changed: the panel says so and nothing can be applied
  ---
  duration_ms: 6.857475
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a manual anchor was added: the panel says so and nothing can be applied
ok 92 - evidence is bound to the fitted model — a manual anchor was added: the panel says so and nothing can be applied
  ---
  duration_ms: 7.121869
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — the charge correction changed: the panel says so and nothing can be applied
ok 93 - evidence is bound to the fitted model — the charge correction changed: the panel says so and nothing can be applied
  ---
  duration_ms: 7.230058
  type: 'test'
  ...
# Subtest: a cosmetic edit (name, colour, visibility) does not invalidate the evidence
ok 94 - a cosmetic edit (name, colour, visibility) does not invalidate the evidence
  ---
  duration_ms: 6.990033
  type: 'test'
  ...
# Subtest: preview overlays a COPY and toggles off; the model is untouched
ok 95 - preview overlays a COPY and toggles off; the model is untouched
  ---
  duration_ms: 7.5078
  type: 'test'
  ...
# Subtest: a record is keyed like the live tab (project save of a non-active tab)
ok 96 - a record is keyed like the live tab (project save of a non-active tab)
  ---
  duration_ms: 7.267125
  type: 'test'
  ...
# Subtest: what is saved: the counts, never the alternatives' parameter sets
ok 97 - what is saved: the counts, never the alternatives' parameter sets
  ---
  duration_ms: 7.258956
  type: 'test'
  ...
# Subtest: a loaded summary (no parameter sets) still renders its line and offers nothing to apply
ok 98 - a loaded summary (no parameter sets) still renders its line and offers nothing to apply
  ---
  duration_ms: 6.654682
  type: 'test'
  ...
# Subtest: wiring: the trigger is decided with the other request inputs, BEFORE the first await
ok 99 - wiring: the trigger is decided with the other request inputs, BEFORE the first await
  ---
  duration_ms: 10.438254
  type: 'test'
  ...
# Subtest: persistence and export sites carry the summary
ok 100 - persistence and export sites carry the summary
  ---
  duration_ms: 1.959655
  type: 'test'
  ...
# Subtest: the tooltip reports what the starts found and claims nothing about the data
ok 101 - the tooltip reports what the starts found and claims nothing about the data
  ---
  duration_ms: 0.521941
  type: 'test'
  ...
# Subtest: the recorded adoption is worded once, for the exports
ok 102 - the recorded adoption is worded once, for the exports
  ---
  duration_ms: 7.054107
  type: 'test'
  ...
# Subtest: one accessor classifies a result against a key: none / unverified / current / stale
ok 103 - one accessor classifies a result against a key: none / unverified / current / stale
  ---
  duration_ms: 18.686687
  type: 'test'
  ...
# Subtest: the key is the step (b) key: F1 adds no second binding mechanism and no new key field
ok 104 - the key is the step (b) key: F1 adds no second binding mechanism and no new key field
  ---
  duration_ms: 3.795679
  type: 'test'
  ...
# Subtest: Results panel, current: statistic, RMSE, R and sigma are shown
ok 105 - Results panel, current: statistic, RMSE, R and sigma are shown
  ---
  duration_ms: 8.927621
  type: 'test'
  ...
# Subtest: Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
ok 106 - Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
  ---
  duration_ms: 7.140269
  type: 'test'
  ...
# Subtest: Results panel, unverified (older save, no key): values shown with a plain note
ok 107 - Results panel, unverified (older save, no key): values shown with a plain note
  ---
  duration_ms: 7.056829
  type: 'test'
  ...
# Subtest: status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
ok 108 - status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
  ---
  duration_ms: 7.045463
  type: 'test'
  ...
# Subtest: the stored fitted curve is never drawn, saved or stacked as the fit once stale
ok 109 - the stored fitted curve is never drawn, saved or stacked as the fit once stale
  ---
  duration_ms: 2.971893
  type: 'test'
  ...
# Subtest: saves keep the key and say plainly when the statistics are stale or unverified
ok 110 - saves keep the key and say plainly when the statistics are stale or unverified
  ---
  duration_ms: 2.592521
  type: 'test'
  ...
# Subtest: CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
ok 111 - CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
  ---
  duration_ms: 13.278301
  type: 'test'
  ...
# Subtest: XLSX: stale writes a WARNING row instead of the statistic, and no sigma
ok 112 - XLSX: stale writes a WARNING row instead of the statistic, and no sigma
  ---
  duration_ms: 4.279574
  type: 'test'
  ...
# Subtest: TSV: stale says the Model / Residual columns are the current, unfitted model
ok 113 - TSV: stale says the Model / Residual columns are the current, unfitted model
  ---
  duration_ms: 7.001152
  type: 'test'
  ...
# Subtest: the refresh re-renders Results only when its rendered state differs
ok 114 - the refresh re-renders Results only when its rendered state differs
  ---
  duration_ms: 2.836972
  type: 'test'
  ...
# Subtest: an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
ok 115 - an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
  ---
  duration_ms: 2.572799
  type: 'test'
  ...
# Subtest: Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
ok 116 - Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
  ---
  duration_ms: 2.893059
  type: 'test'
  ...
# Subtest: Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
ok 117 - Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
  ---
  duration_ms: 6.894405
  type: 'test'
  ...
# Subtest: reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
ok 118 - reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
  ---
  duration_ms: 1.277554
  type: 'test'
  ...
# Subtest: the twin reproduces the server verdict on real responses, and defers to the server field when present
ok 119 - the twin reproduces the server verdict on real responses, and defers to the server field when present
  ---
  duration_ms: 10.71962
  type: 'test'
  ...
# Subtest: _applySupport writes every peak, follows ancestry to the root, stamps the fit key, and leaves null where the response says nothing
ok 120 - _applySupport writes every peak, follows ancestry to the root, stamps the fit key, and leaves null where the response says nothing
  ---
  duration_ms: 5.434877
  type: 'test'
  ...
# Subtest: the verdict applies only to the model and context it was computed for
ok 121 - the verdict applies only to the model and context it was computed for
  ---
  duration_ms: 5.26855
  type: 'test'
  ...
# Subtest: the local engine computes the same statistic from its own residuals
ok 122 - the local engine computes the same statistic from its own residuals
  ---
  duration_ms: 6.323516
  type: 'test'
  ...
# Subtest: sidebar card: badge; centre and width shown as a dash; area % excluded and the others renormalised
ok 123 - sidebar card: badge; centre and width shown as a dash; area % excluded and the others renormalised
  ---
  duration_ms: 6.317498
  type: 'test'
  ...
# Subtest: results table: greyed row, no centre / width / sigma, area kept, percentage dash, and the note beneath
ok 124 - results table: greyed row, no centre / width / sigma, area kept, percentage dash, and the note beneath
  ---
  duration_ms: 11.330685
  type: 'test'
  ...
# Subtest: uncertainty panel: one rule-0 warning for the component, no per-parameter alarms and no "locked" note for it
ok 125 - uncertainty panel: one rule-0 warning for the component, no per-parameter alarms and no "locked" note for it
  ---
  duration_ms: 4.888518
  type: 'test'
  ...
# Subtest: Quantify: excluded from the body, listed beneath with the reason; total and percentages over the rest
ok 126 - Quantify: excluded from the body, listed beneath with the reason; total and percentages over the rest
  ---
  duration_ms: 4.943541
  type: 'test'
  ...
# Subtest: CSV / XLSX export: Status column, suppressed cells, At% empty, WARNING line
ok 127 - CSV / XLSX export: Status column, suppressed cells, At% empty, WARNING line
  ---
  duration_ms: 7.22935
  type: 'test'
  ...
# Subtest: publication figure: no label at the (zero) component, legend entry says so; chart and stack labels say so
ok 128 - publication figure: no label at the (zero) component, legend entry says so; chart and stack labels say so
  ---
  duration_ms: 2.661338
  type: 'test'
  ...
# Subtest: write-back: a server result sets support; the local engine and a propagated model reset it
ok 129 - write-back: a server result sets support; the local engine and a propagated model reset it
  ---
  duration_ms: 1.356721
  type: 'test'
  ...
# Subtest: persistence: support travels with the peak object through every save (the peak is spread whole)
ok 130 - persistence: support travels with the peak object through every save (the peak is spread whole)
  ---
  duration_ms: 0.867803
  type: 'test'
  ...
# Subtest: CSV / XLSX: an unsupported DS+G component exports no width of any kind (beta, m)
ok 131 - CSV / XLSX: an unsupported DS+G component exports no width of any kind (beta, m)
  ---
  duration_ms: 5.136663
  type: 'test'
  ...
# Subtest: the scattered-starts table: an unsupported component shows neither area % nor a move in "Your fit", and is not the largest move
ok 132 - the scattered-starts table: an unsupported component shows neither area % nor a move in "Your fit", and is not the largest move
  ---
  duration_ms: 6.11396
  type: 'test'
  ...
# Subtest: exports: a stale or keyless verdict is "not established", never "supported"
ok 133 - exports: a stale or keyless verdict is "not established", never "supported"
  ---
  duration_ms: 7.91177
  type: 'test'
  ...
# Subtest: Auto-Fit finalisation (locks, charge shift) keeps its own verdicts: _restampSupport, called after the locks
ok 134 - Auto-Fit finalisation (locks, charge shift) keeps its own verdicts: _restampSupport, called after the locks
  ---
  duration_ms: 4.441035
  type: 'test'
  ...
# Subtest: a .fit.json import onto this tab's data carries no verdict
ok 135 - a .fit.json import onto this tab's data carries no verdict
  ---
  duration_ms: 0.121889
  type: 'test'
  ...
# Subtest: _isUnsupported is never handed an array index as its key (Array.filter passes one)
ok 136 - _isUnsupported is never handed an array index as its key (Array.filter passes one)
  ---
  duration_ms: 4.352086
  type: 'test'
  ...
# Subtest: a key change re-renders every consumer of the verdict — each compared with ITS OWN rendering
ok 137 - a key change re-renders every consumer of the verdict — each compared with ITS OWN rendering
  ---
  duration_ms: 2.499775
  type: 'test'
  ...
# Subtest: stack tabs judge a source component against the SOURCE record's key
ok 138 - stack tabs judge a source component against the SOURCE record's key
  ---
  duration_ms: 3.470641
  type: 'test'
  ...
# Subtest: "Your fit" percentages are over supported components; an empty Quantify shows no 100 %
ok 139 - "Your fit" percentages are over supported components; an empty Quantify shows no 100 %
  ---
  duration_ms: 13.969067
  type: 'test'
  ...
# Subtest: the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
ok 140 - the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
  ---
  duration_ms: 5.134581
  type: 'test'
  ...
1..140
# tests 140
# suites 0
# pass 139
# fail 1
# cancelled 0
# skipped 0
# todo 0
# duration_ms 5994.417976

exec
/bin/zsh -lc "sed -n '2040,2068p' templates/index.html; sed -n '8654,8725p' templates/index.html; sed -n '8780,8908p' templates/index.html; sed -n '10268,10390p' templates/index.html; sed -n '11580,11638p' templates/index.html; sed -n '3190,3270p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
              </div>
            </div>
            <div class="field-row">
              <div class="field">
                <label>Shirley iterations</label>
                <input type="number" id="shirley-iter" value="5" min="1" max="50" step="1" oninput="_clampShirleyIter(); _invalidateBgCache(); updatePlot()" title="Number of iterations for the Shirley background calculation. The algorithm converges quickly — most of the change happens between 1 and 5 iterations. Values above 10 rarely produce visible differences. Default: 5.">
              </div>
              <div class="field">
                <label>Endpoint avg</label>
                <input type="number" id="bg-endpoint-avg" value="3" min="1" max="50" step="1" oninput="_invalidateBgCache(); updatePlot()" title="Number of points to average at each endpoint for smoother background anchoring">
              </div>
            </div>
          </div>
        </div>

        <div class="section">
          <div class="section-head" onclick="toggleSection(this)" title="The Region of Interest (ROI) defines the energy range used for all fitting operations. Only data points within this range are included when you click Run Fit — this affects peak fitting, background subtraction, and fit quality metrics (χ² and R-factor). The ROI is independent of the chart zoom — you can zoom in or out freely without affecting which data is fitted.">
            Region of Interest
            <span style="font-size:10px">&#9660;</span>
          </div>
          <div class="section-body">
            <div class="field-row">
              <div class="field">
                <label>BE min (eV)</label>
                <input type="number" id="roi-min" value="706" step="0.5" oninput="updatePlot();_recomputeAutoFitMenuState()">
              </div>
              <div class="field">
                <label>BE max (eV)</label>
                <input type="number" id="roi-max" value="726" step="0.5" oninput="updatePlot();_recomputeAutoFitMenuState()">
function renderResults() {
  const el = document.getElementById('results-area');
  const _stats = _statsLiveState();   // F1: current / stale / unverified / none
  if (el) el.setAttribute('data-stats-state', _stats);
  _applyStatDisplay(state.fitResult);   // header + status bar track every result change (clear, restore, auto-fit) as one unit
  _updateLocalModelBanner();
  if (!state.fitResult) {
    el.innerHTML = _isLocalModel()
      ? '<p style="color:var(--amber,#f59e0b);font-size:11px;text-align:center;padding:20px 0">&#9888; This model was imported from a local fit: a starting point, not a reportable result. Run Fit to obtain results.</p>'
      : '<p style="color:var(--text3);font-size:11px;text-align:center;padding:20px 0">Run the fit to see results.</p>';
    // Quantify (#quantify-area) is populated by renderQuantify(), called
    // only from the non-null path below — without this it kept showing
    // a PRIOR fit's area/RSF/At% table after state.fitResult was cleared
    // elsewhere (Codex review finding, 2026-07-14: same class of stale-
    // DOM bug as the Results panel itself). Reset it to the same
    // no-fit placeholder as its initial static markup.
    const qEl = document.getElementById('quantify-area');
    if (qEl) qEl.innerHTML = '<p style="color:var(--text3);font-size:11px;text-align:center;padding:20px 0;">Run fit to quantify.</p>';
    return;
  }

  const { chiReduced, rmse, backendResult } = state.fitResult;
  const _statIsChi = _fitStatLabel(state.fitResult) !== 'Residual variance';
  const _stale = _stats === 'stale';
  // F1: a stale result's sigma belongs to the previous model: none is shown
  const stderrMap = _stale ? {} : _buildStderrMap(state.fitResult);
  const _statsBanner = _stale ? `
    <div class="stats-stale-note" style="background:rgba(245,158,11,0.12);border:1px solid var(--amber,#f59e0b);border-radius:var(--radius);padding:8px 10px;margin-bottom:10px;font-size:11px;line-height:1.5;color:var(--text)">
      &#9888; <strong>The model has changed since this fit.</strong> Its &#967;&#178;, RMSE, R-factor and uncertainties belong to the previous model and are not shown. The table below is the current model, not a fitted result. Press <strong>Run Fit</strong> to obtain statistics for it.
    </div>` : _stats === 'unverified' ? `
    <div class="stats-unverified-note" style="font-size:11px;line-height:1.5;color:var(--text2);margin-bottom:8px">${_escHtml(_STATS_UNVERIFIED_NOTE)}</div>` : '';
  // A local (unweighted) result is a STARTING POINT: its areas can differ
  // from the server's Poisson-weighted fit by more than 100 % (measured on
  // the lab's C1s scans, unit A0). It is shown as such, never as a result.
  const _localBanner = !_isLocalFit(state.fitResult) ? '' : `
    <div style="background:rgba(245,158,11,0.12);border:1px solid var(--amber,#f59e0b);border-radius:var(--radius);padding:8px 10px;margin-bottom:10px;font-size:11px;line-height:1.5;color:var(--text)">
      &#9888; <strong>${_escHtml(_localFitCaveat(state.fitResult))}</strong>
      ${_localFitDetail(state.fitResult)} Press <strong>Run Fit</strong> before quantifying, exporting or reporting.
    </div>`;

  function fmtVal(val, se, decimals) {
    if (se != null && se > 0) return val.toFixed(decimals) + ' \u00b1 ' + se.toFixed(decimals);
    return val.toFixed(decimals);
  }

  const _dash = '<span style="color:var(--text3)">&mdash;</span>';
  let html = _statsBanner + _localBanner + `
    <div style="display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap">
      <div style="flex:1;background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);padding:8px 10px">
        <div style="font-size:9px;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px">${_escHtml(_fitStatLabel(state.fitResult))}</div>
        <div style="font-family:var(--mono);font-size:16px;color:${_stale ? 'var(--text3)' : _statIsChi ? (chiReduced<2?'var(--green)':chiReduced<5?'var(--amber)':'var(--red)') : 'var(--text)'}">${_stale ? _dash : chiReduced.toFixed(3)}</div>
      </div>
      <div style="flex:1;background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);padding:8px 10px">
        <div style="font-size:9px;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px">RMSE</div>
        <div style="font-family:var(--mono);font-size:16px;color:var(--accent2)">${_stale ? _dash : rmse.toFixed(1)}</div>
      </div>
      ${backendResult ? `<div style="flex:1;background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);padding:8px 10px">
        <div style="font-size:9px;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px">Engine</div>
        <div style="font-family:var(--mono);font-size:11px;color:var(--green)">lmfit</div>
      </div>` : ''}
    </div>
    ${_stale ? '' : _renderRFactorPanel(state.fitResult.rFactor)}
    <table class="results-table">
      <thead><tr>
        <th>Peak</th><th>Center (eV)</th><th>FWHM (eV)</th><th>Area</th><th>%</th>
      </tr></thead>
      <tbody>
  `;

  // Fit grid for area integration. Current-format fits carry fitResult.be; older
  // saves omit it, and without a guard _peakArea(p, be) throws on be.length —
  // leaving the panel stale and aborting the tab switch. Fall back to the live ROI
  if (uncInfo.length) {
    html += `<div class="unc-info-box">
      <div class="uw-title">&#128274; Locked Parameters</div>
      <ul>${uncInfo.join('')}</ul>
    </div>`;
  }

  el.innerHTML = html;

  renderQuantify(areas, totalArea);
}

// Auto-detect element/orbital from peak name, then by center BE
function _detectPeakRSF(p) {
  // Try parsing the name: "Fe 2p", "Fe2p", "Fe 2p3/2", "O1s", "U 4f7/2", etc.
  const name = (p.name || '').trim();
  // Match patterns like "Fe 2p", "Fe2p", "U 4f", "O 1s", "Cu 2p3/2"
  const m = name.match(/^([A-Z][a-z]?)\s*(\d[spdf])/i);
  if (m) {
    const elem = m[1].charAt(0).toUpperCase() + m[1].slice(1).toLowerCase();
    const orb = m[2].toLowerCase();
    const key = elem + ' ' + orb;
    if (SCOFIELD_RSF[key] != null) return { key, rsf: SCOFIELD_RSF[key] };
  }
  // Fall back to center BE matching
  const center = p.center;
  let bestKey = null, bestDist = 6;
  for (const [elem, data] of Object.entries(_accSurveyElements())) {
    for (const [orb, be] of Object.entries(data.lines)) {
      const dist = Math.abs(be - center);
      if (dist < bestDist) {
        const key = elem + ' ' + orb;
        if (SCOFIELD_RSF[key] != null) { bestDist = dist; bestKey = key; }
      }
    }
  }
  if (bestKey) return { key: bestKey, rsf: SCOFIELD_RSF[bestKey] };
  return { key: null, rsf: 1.000 };
}

function renderQuantify(areas, totalArea) {
  const el = document.getElementById('quantify-area');
  // Preserve user's RSF source choice
  const savedSource = el._rsfSource || 'scofield';

  const infoTooltip = `<span title="Relative Sensitivity Factor — corrects for different photoionization probabilities between elements" style="cursor:help;color:var(--text3);border-bottom:1px dotted var(--text3);font-size:10px">RSF &#9432;</span>`;

  const _localQBanner = _isLocalFit(state.fitResult) ? `
    <div style="background:rgba(245,158,11,0.12);border:1px solid var(--amber,#f59e0b);border-radius:var(--radius);padding:8px 10px;margin-bottom:10px;font-size:11px;line-height:1.5;color:var(--text)">
      &#9888; <strong>${_escHtml(_localFitCaveat(state.fitResult))}</strong> ${_localFitDetail(state.fitResult)}
    </div>` : '';
  let html = _localQBanner + `
    <div style="margin-bottom:10px;font-size:11px;color:var(--text2)">
      Relative atomic concentrations from peak areas.
    </div>
    <div style="background:var(--amber-dim);border:1px solid var(--amber);border-radius:var(--radius);padding:8px 10px;font-size:11px;color:var(--amber);margin-bottom:10px">
      ⚠ Semi-quantitative — atomic percentages assume uniform sample composition, no transmission correction, and no matrix effects. RSFs are practical Scofield-based factors (Kratos/CasaXPS-family, C 1s = 1); Th 4f and U 4f are derived/lab-dependent. Treat results as approximate; for publication, validate against reference standards.
    </div>
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
      <label style="margin:0;font-size:11px;color:var(--text2)">RSF Source:</label>
      <select id="rsf-source" style="font-size:11px;padding:2px 6px;background:var(--bg3);border:1px solid var(--border2);color:var(--text);border-radius:var(--radius)" onchange="onRSFSourceChange(this.value)">
        <option value="scofield"${savedSource==='scofield'?' selected':''}>Scofield (Al K\u03b1)</option>
        <option value="wagner"${savedSource==='wagner'?' selected':''}>Wagner (coming soon)</option>
        <option value="custom"${savedSource==='custom'?' selected':''}>Custom (manual)</option>
      </select>
    </div>
    <table class="results-table">
      <thead><tr><th>Peak</th><th>Area</th><th>${infoTooltip}</th><th>Element</th><th>Norm. Area</th><th>At. %</th></tr></thead>
      <tbody>
  `;

  state.peaks.forEach((p, i) => {
    if (_isUnsupported(p)) return;            // listed beneath the table, not quantified
    const { key, rsf } = _detectPeakRSF(p);
    // Use stored RSF if present, otherwise detected
    const storedRSF = p._rsf != null ? p._rsf : rsf;
    const storedElem = p._rsfKey != null ? p._rsfKey : key;
    const useRSF = savedSource === 'custom' ? (p._rsf != null ? p._rsf : 1.000) : storedRSF;

    // Build element dropdown
    const allKeys = Object.keys(SCOFIELD_RSF);
    const ddOptions = allKeys.map(k =>
      `<option value="${k}"${k === storedElem ? ' selected' : ''}>${k}</option>`
    ).join('');

    html += `<tr>
      <td><span style="display:inline-block;width:8px;height:8px;border-radius:2px;background:${p.color};margin-right:5px"></span>${_escHtml(p.name)}</td>
      <td>${areas[i].toFixed(0)}</td>
      <td><input type="number" value="${useRSF.toFixed(3)}" step="0.001" min="0.001" style="width:62px;font-size:11px;padding:2px 4px" onchange="onRSFInputChange(${p.id},this.value)" id="rsf-${p.id}"></td>
      <td>
        <select style="font-size:10px;padding:1px 3px;background:var(--bg3);border:1px solid var(--border);color:var(--text2);border-radius:var(--radius);max-width:80px" onchange="onRSFElemChange(${p.id},this.value)" id="rsf-elem-${p.id}">
          <option value="">— none —</option>
          ${ddOptions}
        </select>
      </td>
      <td id="qnorm-${p.id}">&mdash;</td>
      <td id="qpct-${p.id}" style="font-weight:500">&mdash;</td>
    </tr>`;
  });

  html += '</tbody><tfoot><tr><td colspan="4" style="font-weight:500;color:var(--text2)">Total</td><td id="qtotal-norm">&mdash;</td><td id="qtotal-pct" style="font-weight:500">&mdash;</td></tr></tfoot></table>';
  const qUnsupported = state.peaks.filter(p => _isUnsupported(p));
  if (qUnsupported.length) {
    html += `<div class="unsupported-note" style="font-size:11px;line-height:1.5;color:var(--text2);margin-top:8px" title="${_escAttr(_UNSUPPORTED_TIP)}">Not quantified — <b>${_UNSUPPORTED_LABEL}</b>: ${qUnsupported.map(q => _escHtml(q.name)).join(', ')}. The fit did not determine ${qUnsupported.length === 1 ? 'this component' : 'these components'}; an atomic percentage of 0.0 % would be a measurement claim.</div>`;
  }
  html += `<button class="btn btn-sm btn-accent" style="margin-top:10px" onclick="recalcQuantify()">Recalculate</button>`;
  el.innerHTML = html;
  el._areas = areas;
  el._rsfSource = savedSource;

  // Save detected RSF to peak objects for persistence
  state.peaks.forEach(p => {
    const { key, rsf } = _detectPeakRSF(p);
    if (p._rsfKey == null) p._rsfKey = key;
    if (p._rsf == null) p._rsf = rsf;
  });

  recalcQuantify();
}

function onRSFSourceChange(source) {
  const el = document.getElementById('quantify-area');
  el._rsfSource = source;
  if (source === 'wagner') {
    notify('Wagner RSFs coming soon — using Scofield values.', 'amber');
    // Fall through to Scofield
    el._rsfSource = 'scofield';
    document.getElementById('rsf-source').value = 'scofield';
  }
function _doSaveFit() {
  tabManager._syncActiveToRecord();
  const data = {
    version: 1,
    timestamp: new Date().toISOString(),
    peaks: state.peaks.map(p => ({...p})),
    nextId: state.nextId,
    chargeCorrection: {
      method: document.getElementById('cc-method').value,
      observedBE: document.getElementById('cc-obs').value,
      shift: state.ccShift
    },
    background: {
      type: document.getElementById('bg-type').value,
      start: document.getElementById('bg-start').value,
      end: document.getElementById('bg-end').value,
      shirleyIter: document.getElementById('shirley-iter').value,
      // Recorded since 2026-09-08: without it a fit saved at the new default
      // (3) reloaded as a legacy file (1) — Codex round 1, both runs.
      endpointAvg: document.getElementById('bg-endpoint-avg').value,
      bgSubtractedView: !!document.getElementById('bg-sub-toggle')?.checked,
    },
    roi: {
      min: document.getElementById('roi-min').value,
      max: document.getElementById('roi-max').value
    },
    notes: document.getElementById('spectrum-notes')?.value || '',
    manualAnchors: _getManualAnchors(),
    // Provenance of the parameters being saved: a local (unweighted) result
    // is a starting point, not a reportable result (unit A0).
    fitStatistics: state.fitResult ? {
      chiReduced: state.fitResult.chiReduced ?? null,
      engine: state.fitResult.engine || null,
      objective: state.fitResult.objective || null,
      weighting: state.fitResult.weighting || null,
      status: state.fitResult.status || null,
      starts: _startsForSave(_startsIfCurrent(state.fitResult, _startsLiveKey())),
      startsModelKey: state.fitResult.startsModelKey || null,
      chosenAlternative: _startsIfCurrent(state.fitResult, _startsLiveKey()) ? (state.fitResult.chosenAlternative || null) : null,
      reportable: _isLocalFit(state.fitResult) ? false : (state.fitResult.reportable ?? null),
      caveat: _localFitCaveat(state.fitResult) || state.fitResult.caveat || null,
      ..._statsSaveFields(_statsLiveState()),   // F1: says plainly when the statistics belong to the previous model
    } : ((_activeTab() && _activeTab().modelProvenance) ? {
      ..._activeTab().modelProvenance, reportable: false, caveat: _localFitCaveat(_activeTab().modelProvenance),
    } : null),
  };
  const fname = document.getElementById('save-fname').value.trim() || 'spectrum';
  _downloadBlob(
    new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'}),
    fname + '.fit.json'
  );
  notify('Fit parameters saved.', 'green');
}

// ── 2. Save Spectrum (v2) — active tab only ──────────
function _doSaveSpectrum() {
  tabManager._syncActiveToRecord();
  const tab = tabManager._getTab(tabManager.activeId);

  // Compute current curves
  const { be, inten } = getROIData();
  const bgIntensity = computeBackground(be, inten);
  const modelFull = evalAllPeaks(be, state.peaks);
  const bgSub = inten.map((v, i) => v - bgIntensity[i]);
  const residuals = bgSub.map((v, i) => v - modelFull[i]);
  // F1: a stale result's stored curve is the previous model's; the file's
  // fittedY then matches its residuals (the current model), as with no fit
  const _saveStats = _statsLiveState();
  const fittedY = (_saveStats !== 'stale' && state.fitResult?.fittedY) || modelFull.map((v, i) => v + bgIntensity[i]);

  // Per-peak curves and areas. evalPeakArray(), not per-point evalPeak:
  // for LACX with caM > 0, only the array evaluator applies the shape's
  // Gaussian convolution — evalPeak silently ignores caM. These curves
  // and areas are written into the saved .spec.json file.
  const peakCurves = state.peaks.map(p => {
    const yArr = evalPeakArray(be, p);
    return {
      id: p.id, name: p.name,
      y: yArr,
      area: yArr.reduce((sum, y, i) => {
        if (i === 0) return 0;
        const dx = Math.abs(be[i] - be[i - 1]);
        return sum + 0.5 * (yArr[i - 1] + y) * dx;
      }, 0)
    };
  });

  const stats = state.fitResult ? {
    chi: state.fitResult.chi,
    chiReduced: state.fitResult.chiReduced,
    rmse: state.fitResult.rmse,
    rFactor: state.fitResult.rFactor || null,   // F1: the fit's own R (restored only while current)
    // Engine identity travels with the statistic so a reloaded local-engine
    // result is never relabelled as chi-square (unit A0).
    engine: state.fitResult.engine || null,
    objective: state.fitResult.objective || null,
    weighting: state.fitResult.weighting || null,
    status: state.fitResult.status || null,
    starts: _startsForSave(_startsIfCurrent(state.fitResult, _startsLiveKey())),
    startsModelKey: state.fitResult.startsModelKey || null,
    chosenAlternative: _startsIfCurrent(state.fitResult, _startsLiveKey()) ? (state.fitResult.chosenAlternative || null) : null,
    // Derived from the objective so an older local result (saved before
    // these fields existed) is designated on re-save too.
    reportable: _isLocalFit(state.fitResult) ? false : (state.fitResult.reportable ?? null),
    caveat: _localFitCaveat(state.fitResult) || state.fitResult.caveat || null,
    ..._statsSaveFields(_saveStats),
  } : null;

  const data = {
    version: 2,
    timestamp: new Date().toISOString(),
    spectrumName: tab.name,
    rawBE: tab.rawBE,
    rawIntensity: tab.rawIntensity,
    ccShift: tab.ccShift,
    peaks: tab.peaks.map(p => ({...p})),
    nextId: tab.nextId,
    ui: {...tab.ui},
    roiBE: be,
    background: bgIntensity,
    fittedY: fittedY,
    residuals: residuals,
    peakCurves: peakCurves,
function _computeRFactor(fitResult) {
  if (!fitResult || !fitResult.be) return null;
  const be = fitResult.be;
  const bgSub = fitResult.bgSubtracted;
  if (!bgSub || bgSub.length !== be.length) return null;
  let residuals;
  if (fitResult.fittedY && fitResult.fittedY.length === be.length) {
    const bgI = fitResult.bgIntensity;
    if (bgI && bgI.length === be.length) {
      residuals = bgSub.map((v, i) => (v + bgI[i]) - fitResult.fittedY[i]);
    } else {
      residuals = bgSub.map((v, i) => v - (fitResult.fittedY[i] - (bgI ? bgI[i] : 0)));
    }
  } else {
    const modelY = evalAllPeaks(be, state.peaks);
    residuals = bgSub.map((v, i) => v - modelY[i]);
  }
  const sumAbsResid = residuals.reduce((s, v) => s + Math.abs(v), 0);
  const sumAbsData = bgSub.reduce((s, v) => s + Math.abs(v), 0);
  if (sumAbsData === 0) return null;
  const rPct = (sumAbsResid / sumAbsData) * 100;
  let level;
  if (rPct < 5) level = 'good';
  else if (rPct <= 10) level = 'amber';
  else level = 'red';
  return { rPct, level };
}

const _RFACTOR_TOOLTIP = "The R-factor (reliability factor) measures the overall agreement between the fit and the data as a percentage. Computed within the ROI range.\n\nR = \u03a3|residual| / \u03a3|data| \u00d7 100%\n\n\u2022 R < 5% = excellent fit\n\u2022 R = 5\u201310% = acceptable fit, check residuals visually\n\u2022 R > 10% = poor fit, the model is likely incomplete\n\nUnlike chi-squared, the R-factor is intuitive \u2014 it represents the fraction of the total signal that is unexplained by the model.";

function _renderRFactorPanel(rf) {
  if (!rf) return '';
  const pct = rf.rPct.toFixed(1);
  const color = rf.level === 'good' ? 'var(--green)' : rf.level === 'amber' ? 'var(--amber)' : 'var(--red)';
  const label = rf.level === 'good' ? 'Excellent fit' : rf.level === 'amber' ? 'Acceptable \u2014 check residuals' : 'Poor fit \u2014 model likely incomplete';
  return `<div data-xps-tip="${_RFACTOR_TOOLTIP.replace(/"/g, '&quot;')}" style="background:var(--bg3);border:1px solid ${color};border-radius:var(--radius);padding:8px 10px;margin-bottom:12px;font-size:11px;color:${color};cursor:help">
    R-factor: <span style="font-family:var(--mono)">${pct}%</span> \u2014 ${label}
  </div>`;
}

function _updateRFactorUI(rf) {
  const el = document.getElementById('sb-runs');
  if (!el) return;
  if (rf && state.fitResult && rf === state.fitResult.rFactor && _statsLiveState() === 'stale') {
    // F1: the previous model's R-factor is not shown beside the edited model
    el.style.color = 'var(--text3)';
    el.textContent = 'R: \u2014';
    el.setAttribute('data-xps-tip', _STATS_STALE_NOTE);
    return;
  }
  if (!rf) {
    el.textContent = '';
    el.removeAttribute('data-xps-tip');
    return;
  }
  const pct = rf.rPct.toFixed(1);
  el.style.color = rf.level === 'good' ? 'var(--green)' : rf.level === 'amber' ? 'var(--amber)' : 'var(--red)';
  el.textContent = `R: ${pct}%`;
  el.setAttribute('data-xps-tip', _RFACTOR_TOOLTIP);
    return tab;
  }

  createStackTab() {
    const id = 'tab_' + Math.random().toString(36).slice(2, 9);
    const tab = {
      id,
      name: '▦ Stack ' + (_nextStackNum++),
      color: '#7a7a7a',           // inert — stack tabs render no dot
      isStack: true,
      entries: [],
      _nextColorIdx: 0,
      lineWidth: 1.5,
      verticalOffset: 0,
      // Inert spectrum-tab fields kept to satisfy existing lifecycle code paths.
      isSurvey: false, chargeVerified: true,
      rawBE: [], rawIntensity: [], ccShift: 0,
      peaks: [], nextId: 1, fitResult: null,
      markedElements: [], notes: '', sourcePath: null,
      ui: { bgType: 'shirley', bgStart: '', bgEnd: '', shirleyIter: '5',
            endpointAvg: '1', roiMin: '', roiMax: '',
            ccMethod: 'none', ccObs: '', ccLit: '' },
    };
    this.tabs.push(tab);
    this.activateTab(id);
    return tab;
  }

  activateTab(id) {
    if (this.activeId === id) return;
    const tab = this._getTab(id);
    if (!tab) return;
    // Cancel any armed placement mode so a click on the new tab's chart
    // isn't consumed by a placement aimed at the previous spectrum.
    if (placeMode) togglePlaceMode(placeMode);
    // Clear stale history preview from previous tab
    if (typeof _historyPreview !== 'undefined') _historyPreview = null;
    // Save current tab's live state
    this._syncActiveToRecord();
    this.activeId = id;

    // Swap global state fields — peaks uses reference sharing
    state.rawBE = tab.rawBE;
    state.rawIntensity = tab.rawIntensity;
    state.ccShift = tab.ccShift;
    state.peaks = tab.peaks;
    state.nextId = tab.nextId;
    state.fitResult = tab.fitResult;
    state.lineWidth = tab.lineWidth ?? 1.5;

    // Restore DOM form fields
    this._restoreUI(tab.ui);
    _updateUndoButtons();   // history is per tab: buttons reflect the incoming record
    const notesEl = document.getElementById('spectrum-notes');
    if (notesEl) notesEl.value = tab.notes || '';
    this._updateCCVerifiedUI(tab.chargeVerified ?? true);
    this._updateInfoBadge(tab);
    if (typeof _recomputeAutoFitMenuState === 'function') _recomputeAutoFitMenuState();
    // Update chi-squared display for this tab's fit result
    _applyStatDisplay(state.fitResult);
    // F1: never computed over an edited model and cached under the fit's key
    // (without a stored curve _computeRFactor evaluates the CURRENT peaks)
    if (state.fitResult && state.fitResult.rFactor == null && _statsLiveState() !== 'stale') {
      state.fitResult.rFactor = _computeRFactor(state.fitResult);
    }
    _updateRFactorUI(state.fitResult ? state.fitResult.rFactor : null);
    _updateROIDisplay(state.fitResult ? state.fitResult.roiRange : null);
    // Reset Y zoom so chart auto-scales to this tab's data range
    // (prevents survey zoom from squishing narrow-region spectra)
    state._mainYMax = tab.yZoom || null;
    state._mainXMin = tab.xZoomMin ?? null;
    state._mainXMax = tab.xZoomMax ?? null;

    this.renderTabBar();
    renderPeakList();
    renderResults();
    _applyRightPanelMode(tab);
    if (typeof _refOnTabChange === 'function') _refOnTabChange();
    updatePlot();
  }


exec
/bin/zsh -lc "sed -n '1,90p' tests/js/fit_acceptance.test.js; sed -n '10435,10486p' templates/index.html; sed -n '10645,10725p' templates/index.html; sed -n '3830,3885p' templates/index.html; sed -n '8910,8978p' templates/index.html; rg -n 'statisticsState|_stats|chiReduced|fittedY|rFactor' static/js | head -65; git diff main..HEAD -- templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
// Fit acceptance rule for the backend path (unit A0, 2026-09-15): nothing is
// shown, stored or exported as a fit result unless it converged, and a
// server-side error surfaces its message instead of silently handing the
// model to the local optimiser.
//
// Before this unit runFit checked `json.error` only: an lmfit result with
// success:false was applied and announced as "Fit complete (lmfit)" (audit
// A08), and ANY thrown error — a 400 validation error included — fell back
// to runFitLocal, which then returned the starting model (A01).
//
// runFit is extracted verbatim from templates/index.html; its collaborators
// are stubbed at the boundary (DOM, fetch, upload, chart/list renderers).

const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const REPO_ROOT = path.join(__dirname, '../..');
const html = fs.readFileSync(path.join(REPO_ROOT, 'templates/index.html'), 'utf8');
const lines = html.split('\n');
function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name + '\\(');
  const start = lines.findIndex(l => re.test(l));
  assert.ok(start >= 0, `function ${name} not found`);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail('unbalanced ' + name);
}

function makeEnv({ fetchImpl, uploadImpl, specImpl, ownerActive }) {
  const dom = {};
  const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, disabled: false,
    setAttribute() {}, removeAttribute() {}, classList: { add(c) { this._c = c; }, remove() { this._c = null; }, contains() { return false; }, _c: null } });
  const document = { getElementById: el, querySelector: () => el('.btn-green'), querySelectorAll: () => [] };
  const be = Array.from({ length: 50 }, (_, i) => 280 + 0.2 * i);
  const state = { rawBE: be.slice(), rawIntensity: be.map(() => 100), ccShift: 0, fitResult: { marker: 'previous' },
    peaks: [{ id: 1, name: 'p', shape: 'Gaussian', center: 285, fwhm: 1.2, amplitude: 50, glMix: 50, asymmetry: 0 }] };
  const owner = { id: 7 };
  const calls = { notify: [], local: 0, applied: 0 };
  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n');
  const factory = new Function('document', 'state', 'fetch', 'uploadToBackend', 'notify', 'pushUndo', '_showFitSpinner', '_hideFitSpinner',
    '_opOwner', '_ownerActive', 'getROIData', 'computeBackground', 'peakToBackendSpec', '_getManualAnchors', 'applyBackendResult',
    '_computeRFactor', '_CHISQ_TOOLTIP', '_updateRFactorUI', '_updateROIDisplay', 'renderPeakList', 'updatePlot', 'renderResults',
    '_autoSnapshot', 'runFitLocal', '_snapshotSuppressed', 'console', '_applyStatDisplay', '_activeTab',
    src + '\nreturn { runFit };');
  const noop = () => {};
  const { runFit } = factory(document, state, fetchImpl, uploadImpl || (async () => 'sid'), (msg, kind) => calls.notify.push({ msg, kind }),
    noop, noop, noop, () => owner, ownerActive || (o => o === owner), () => ({ be: state.rawBE.slice(), inten: state.rawIntensity.slice() }),
    b => b.map(() => 0), specImpl || (p => ({ id: p.id, shape: 'gaussian' })), () => [], () => { calls.applied++; },
    () => 0.1, '', noop, noop, noop, noop, noop, noop,
    () => { calls.local++; return { success: true, engine: 'local' }; }, false, { warn: noop, error: noop, log: noop }, noop, () => owner);
  return { runFit, state, dom, calls };
}

const okResponse = body => async () => ({ ok: true, status: 200, json: async () => body });

test('A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown', async () => {
  const env = makeEnv({ fetchImpl: okResponse({ success: false, message: 'Fit did not converge: max evaluations', statistics: { reduced_chi_square: 999 }, individual_peaks: [] }) });
  const before = JSON.stringify(env.state.peaks);
  await env.runFit();
  assert.equal(env.calls.applied, 0, 'applyBackendResult must not run');
  assert.equal(env.calls.local, 0, 'no silent local fallback');
  assert.equal(JSON.stringify(env.state.peaks), before, 'peaks unchanged');
  assert.equal(env.state.fitResult.marker, 'previous', 'previous fit result retained');
  assert.ok(env.calls.notify.some(n => n.kind === 'red' && /did not converge/i.test(n.msg)), JSON.stringify(env.calls.notify));
  assert.ok(!/complete/i.test(env.dom['sb-msg'].textContent), env.dom['sb-msg'].textContent);
});

test('a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser', async () => {
  const env = makeEnv({ fetchImpl: async () => ({ ok: false, status: 400, json: async () => ({ error: 'peak 1: fwhm_min must be positive' }) }) });
  const before = JSON.stringify(env.state.peaks);
  await env.runFit();
  assert.equal(env.calls.local, 0, 'a 400 is not a reason to run the local fitter');
  assert.equal(env.calls.applied, 0);
  assert.equal(JSON.stringify(env.state.peaks), before);
  assert.ok(env.calls.notify.some(n => n.kind === 'red' && /fwhm_min must be positive/.test(n.msg)), JSON.stringify(env.calls.notify));
  assert.notEqual(env.dom['localfit-warn-overlay']?.classList._c, 'open', 'no "local fit performed" overlay');
});

test('a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay', async () => {
  const env = makeEnv({ fetchImpl: async () => { throw new TypeError('Failed to fetch'); } });
  await env.runFit();
  assert.equal(env.calls.local, 1, 'local fallback used for a genuine network failure');
  assert.equal(env.dom['localfit-warn-overlay'].classList._c, 'open');
});

          showFit: !!e.showFit,
        })),
      };
    }
    const rec = {
      id: t.id, name: t.name, color: t.color, isSurvey: t.isSurvey,
      rawBE: t.rawBE, rawIntensity: t.rawIntensity,
      ccShift: t.ccShift, chargeVerified: t.chargeVerified ?? true,
      peaks: t.peaks.map(p => ({...p})),
      nextId: t.nextId,
      fitResult: t.fitResult ? {
        chi: t.fitResult.chi, chiReduced: t.fitResult.chiReduced,
        rmse: t.fitResult.rmse, fittedY: t.fitResult.fittedY || null,
        rFactor: t.fitResult.rFactor || null,   // F1: the fit's own R, not one recomputed from edited peaks on reload
        // Frozen fit grid: persisted so post-load updatePlot() renders the
        // recorded fit (haveFit path) instead of recomputing background and
        // residuals from current settings. Absent in older saves — loaders
        // fall back to reconstruction.
        be: _roundBE(t.fitResult.be),
        bgIntensity: _roundIntensity(t.fitResult.bgIntensity),
        bgSubtracted: _roundIntensity(t.fitResult.bgSubtracted),
        roiRange: t.fitResult.roiRange || null,
        // Engine identity (unit A0): a local-engine result stays labelled
        // "Residual variance" after reload instead of becoming chi-square.
        engine: t.fitResult.engine || null,
        objective: t.fitResult.objective || null,
        weighting: t.fitResult.weighting || null,
        status: t.fitResult.status || null,
        starts: _startsForSave(_startsIfCurrent(t.fitResult, _startsRecordKey(t))),
        startsModelKey: t.fitResult.startsModelKey || null,
        chosenAlternative: _startsIfCurrent(t.fitResult, _startsRecordKey(t)) ? (t.fitResult.chosenAlternative || null) : null,
        iterations: t.fitResult.iterations ?? null,
        reportable: _isLocalFit(t.fitResult) ? false : (t.fitResult.reportable ?? null),
        caveat: _localFitCaveat(t.fitResult) || t.fitResult.caveat || null,
        ..._statsSaveFields(_statsRecordState(t)),   // F1: judged against the RECORD's key
      } : null,
      modelProvenance: t.modelProvenance || null,
      notes: t.notes || '',
      manualAnchors: t.manualAnchors || [],
      lineWidth: t.lineWidth ?? 1.5,
      ui: {...t.ui},
    };
    // B2: per-tab element overlays. Additive + optional — serializeRefOverlays
    // returns null when the tab has no valid selection, and we omit the key
    // entirely then so old-shaped saves stay byte-clean. Identify transient
    // state (_refIdentify / tolEv) is structurally never serialized here.
    const _ov = RefCore.serializeRefOverlays(t._refSel);
    if (_ov) rec.refOverlays = _ov;
    // Autofit engine candidate-set annotations (spec v2.1 §1): whitelisted on
    // BOTH save and load, staying on version 3. Omitted when absent so
    // pre-engine saves stay byte-clean. REGENERABLE data only — older clients
    // silently drop this key on resave, so durable facts (human decisions,
  // Audit F1/F4/F5: reject unsafe peak ids/links/colors before rendering.
  const pe = _peaksLoadError(data && data.peaks);
  if (pe) { notify('Spectrum not loaded: ' + pe + '.', 'red', true); return; }
  // Create a new tab with the saved spectrum data
  const srcPath = data.sourcePath || (sessionFile ? sessionFile : '(restored)');
  const active = tabManager.createTab(
    (data.spectrumName || 'Spectrum') + '.json',
    data.rawBE,
    data.rawIntensity,
    srcPath
  );
  if (!active) return;
  // Apply saved settings on top of the created tab
  active.ccShift = data.ccShift || 0;
  state.ccShift = active.ccShift;
  active.peaks = _normalizePeaksCRef((data.peaks || []).map(p => ({...p})));
  state.peaks = active.peaks;
  active.nextId = data.nextId || 1;
  state.nextId = active.nextId;
  // Manual bg anchors: saved by _doSaveSpectrum but previously never read
  // back here — the one anchor-persisting load path that dropped them (the
  // v1 fit-file loader and the project tab deserializer both restore).
  // Same verbatim convention as those two paths. Assigned BEFORE the ui
  // restore below: _restoreUI refreshes the manual-anchor count label from
  // the active tab, so assigning after it left the label stale (Codex
  // round-2 MINOR).
  if (Array.isArray(data.manualAnchors)) {
    active.manualAnchors = data.manualAnchors;
  }
  // Saved-ui boundary: a file whose ui lacks endpointAvg was fitted at 1
  // (the field did not exist), so it must NOT inherit the new-tab default;
  // saved values are honoured verbatim. Restore the DOM either way so the
  // record and the inputs agree before any switch-away capture.
  const savedEp = data.ui && data.ui.endpointAvg;
  active.ui = { ...active.ui, ...(data.ui || {}), endpointAvg: savedEp || LEGACY_ENDPOINT_AVG };
  tabManager._restoreUI(active.ui);
  if (data.notes) active.notes = data.notes;
  active.modelProvenance = _isLocalProvenance(data.modelProvenance) ? data.modelProvenance : null;
  if (data.statistics) {
    const fr = { chi: data.statistics.chi, chiReduced: data.statistics.chiReduced, rmse: data.statistics.rmse };
    for (const k of ['engine', 'objective', 'weighting', 'status', 'caveat', 'starts', 'startsModelKey', 'chosenAlternative']) if (data.statistics[k]) fr[k] = data.statistics[k];
    if (data.statistics.reportable !== undefined && data.statistics.reportable !== null) fr.reportable = data.statistics.reportable;
    // F1: a stale save's fittedY is the EDITED model's curve (written for the
    // file's readers); it is never installed under the original fit's key
    if (data.fittedY && data.statistics.statisticsState !== 'stale') fr.fittedY = data.fittedY;
    if (data.statistics.rFactor && data.statistics.statisticsState !== 'stale') fr.rFactor = data.statistics.rFactor;
    active.fitResult = fr;
    state.fitResult = fr;
  }
  const notesEl = document.getElementById('spectrum-notes');
  if (notesEl) notesEl.value = active.notes || '';
  renderPeakList();
  updatePlot();
  renderResults();   // installs the restored result's designation in Results/Quantify and the statistic display (unit A0)
  notify('Spectrum loaded as new tab: ' + active.name, 'green');
}

// ── Project-load resource caps (audit F8) ─────────────────────────────
// Generous bounds, far above any real spectrum (a Thermo Nexsa survey is
// well under 10^6 points), so no legitimate file is ever rejected. They
// exist only to stop a crafted file from inflating the JS heap and freezing
// the tab. Adjust here if a genuinely larger dataset ever needs to load.
const MAX_PROJECT_TABS      = 100;                  // tabs per project
const MAX_SPECTRUM_POINTS   = 1000000;              // rawBE / rawIntensity length per tab
const MAX_ZIP_SPECTRA       = 100;                  // manifest.spectra entries (zip path)
const MAX_ZIP_UNCOMPRESSED  = 500 * 1024 * 1024;    // 500 MB total inflated (zip-bomb guard)
const MAX_ZIP_COMPRESSED_FALLBACK = 50 * 1024 * 1024; // 50 MB, used only if sizes are unreadable

function _loadProjectJSON(data, sessionFile) {
  // Per-tab peaks live under data.tabs[i].peaks (v2+) and/or top-level
  // data.peaks (v1). Migrate both shapes.
  if (data && Array.isArray(data.peaks)) _migrateLineshapeAliases(data.peaks);
  if (data && Array.isArray(data.tabs)) {
    for (const t of data.tabs) {
      if (t && Array.isArray(t.peaks)) _migrateLineshapeAliases(t.peaks);
    }
  }

  // Audit F1–F5: validate untrusted ids/colors before building anything, so
  // a hostile/hand-edited file is rejected wholesale rather than partially
  // loaded. Tab ids and stack-entry ids must be slugs (they land in onclick=
      bgEnd:       document.getElementById('bg-end')?.value || '',
      shirleyIter: document.getElementById('shirley-iter')?.value || '5',
      endpointAvg: document.getElementById('bg-endpoint-avg')?.value || LEGACY_ENDPOINT_AVG,
      roiMin:      document.getElementById('roi-min')?.value || '',
      roiMax:      document.getElementById('roi-max')?.value || '',
      ccMethod:    document.getElementById('cc-method')?.value || 'none',
      ccObs:       document.getElementById('cc-obs')?.value || '',
      ccLit:       document.getElementById('cc-lit')?.value || '',
      bgSubtractedView: !!document.getElementById('bg-sub-toggle')?.checked,
    };
  }

  _restoreUI(ui) {
    const set = (id, val) => {
      const el = document.getElementById(id);
      if (el && val !== undefined) el.value = val;
    };
    set('bg-type', ui.bgType);
    _syncLegacyBgOption();
    set('bg-start', ui.bgStart);
    set('bg-end', ui.bgEnd);
    set('shirley-iter', ui.shirleyIter);
    set('bg-endpoint-avg', ui.endpointAvg || LEGACY_ENDPOINT_AVG);
    set('roi-min', ui.roiMin);
    set('roi-max', ui.roiMax);
    set('cc-method', ui.ccMethod);
    set('cc-obs', ui.ccObs);
    set('cc-lit', ui.ccLit);
    // Update cc field visibility without dispatching change event
    // (which would overwrite state.ccShift and trigger a double updatePlot)
    const refField = document.getElementById('cc-ref-field');
    const targetField = document.getElementById('cc-target-field');
    if (refField) refField.style.display = (ui.ccMethod === 'none') ? 'none' : 'block';
    if (targetField) targetField.style.display = (ui.ccMethod === 'custom') ? 'block' : 'none';
    // Update shift display from the already-restored state.ccShift
    const shift = -state.ccShift;
    document.getElementById('cc-shift-display').textContent = (shift >= 0 ? '+' : '') + shift.toFixed(3) + ' eV';
    // Update manual bg controls and Shirley iteration state for restored bg type
    if (typeof _onBgTypeChange === 'function') {
      const mc = document.getElementById('manual-bg-controls');
      if (mc) mc.style.display = ui.bgType === 'manual' ? 'block' : 'none';
      const needsIter = (ui.bgType === 'shirley' || ui.bgType === 'smart' || ui.bgType === 'smart_exp' || ui.bgType === 'shirley_linear');
      const si = document.getElementById('shirley-iter');
      if (si) {
        si.disabled = !needsIter;
        si.style.opacity = needsIter ? '1' : '0.4';
      }
      // Endpoint averaging also applies to Tougaard (it sets the high-BE
      // amplitude anchor), not just the Shirley iteration family.
      const needsEpAvg = needsIter || ui.bgType === 'tougaard';
      const epAvg = document.getElementById('bg-endpoint-avg');
      if (epAvg) {
        epAvg.disabled = !needsEpAvg;
        epAvg.style.opacity = needsEpAvg ? '1' : '0.4';
      }
      if (typeof _updateManualAnchorCount === 'function') _updateManualAnchorCount();
  if (!el._areas) return;
  state.peaks.forEach(p => {
    const inp = document.getElementById('rsf-' + p.id);
    if (!inp) return;
    if (el._rsfSource === 'custom') {
      inp.value = (p._rsf != null ? p._rsf : 1.000).toFixed(3);
    } else {
      const { rsf } = _detectPeakRSF(p);
      p._rsf = rsf;
      inp.value = rsf.toFixed(3);
    }
  });
  recalcQuantify();
}

function onRSFInputChange(peakId, val) {
  const p = state.peaks.find(pk => pk.id === peakId);
  if (p) p._rsf = parseFloat(val) || 1;
  recalcQuantify();
}

function onRSFElemChange(peakId, elemKey) {
  const p = state.peaks.find(pk => pk.id === peakId);
  if (!p) return;
  p._rsfKey = elemKey || null;
  const rsf = elemKey && SCOFIELD_RSF[elemKey] ? SCOFIELD_RSF[elemKey] : 1.000;
  p._rsf = rsf;
  const inp = document.getElementById('rsf-' + peakId);
  if (inp) inp.value = rsf.toFixed(3);
  recalcQuantify();
}

function recalcQuantify() {
  const el = document.getElementById('quantify-area');
  if (!el._areas) return;
  const areas = el._areas;

  const normAreas = state.peaks.map((p, i) => {
    if (_isUnsupported(p)) return 0;          // not quantified (no row either)
    const rsf = parseFloat(document.getElementById('rsf-' + p.id)?.value || 1);
    return areas[i] / (rsf || 1);
  });
  const total = normAreas.reduce((s, v) => s + v, 0);
  const maxPct = total > 0 ? Math.max(...normAreas.map(v => v / total * 100)) : 1;

  state.peaks.forEach((p, i) => {
    const pct = total > 0 ? (normAreas[i] / total * 100) : 0;
    const ne = document.getElementById('qnorm-' + p.id);
    const pe = document.getElementById('qpct-' + p.id);
    if (ne) ne.textContent = normAreas[i].toFixed(0);
    if (pe) {
      pe.textContent = pct.toFixed(1) + '%';
      // Color saturation proportional to percentage
      const sat = maxPct > 0 ? pct / maxPct : 0;
      pe.style.color = sat > 0.6
        ? 'var(--accent2)'
        : sat > 0.3
          ? 'var(--text)'
          : 'var(--text2)';
    }
  });

  const tn = document.getElementById('qtotal-norm');
  if (tn) tn.textContent = total.toFixed(0);
  const tp = document.getElementById('qtotal-pct');
  if (tp) tp.textContent = total > 0 ? '100%' : '\u2014';
}

// ═══════════════════════════════════════════════════
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-YiDBjFbn' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-91bJn6L2' (errno=Operation not permitted)
diff --git a/templates/index.html b/templates/index.html
index 0b9268d..e1f08fc 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -3247,7 +3247,9 @@ class TabManager {
     if (typeof _recomputeAutoFitMenuState === 'function') _recomputeAutoFitMenuState();
     // Update chi-squared display for this tab's fit result
     _applyStatDisplay(state.fitResult);
-    if (state.fitResult && state.fitResult.rFactor == null) {
+    // F1: never computed over an edited model and cached under the fit's key
+    // (without a stored curve _computeRFactor evaluates the CURRENT peaks)
+    if (state.fitResult && state.fitResult.rFactor == null && _statsLiveState() !== 'stale') {
       state.fitResult.rFactor = _computeRFactor(state.fitResult);
     }
     _updateRFactorUI(state.fitResult ? state.fitResult.rFactor : null);
@@ -7209,12 +7211,12 @@ function _isUnsupported(p, key) {
   if (!(p && p.support && p.support.supported === false)) return false;
   if (!p.support.fitKey) return false;                              // a verdict from before keys existed: not applied
   if (key === undefined) key = typeof _startsLiveKey === 'function' ? _startsLiveKey() : null;
-  return p.support.fitKey === key;
+  return _sameFitKey(p.support.fitKey, key);
 }
 // A CURRENT verdict, either way (for exports: a stale or keyless verdict is "not established", never "supported").
 function _currentSupport(p) {
   if (!(p && p.support && p.support.fitKey)) return null;
-  return p.support.fitKey === _startsLiveKey() ? p.support : null;
+  return _sameFitKey(p.support.fitKey, _startsLiveKey()) ? p.support : null;
 }
 // Re-stamp every verdict with the live key: for a caller that changes the
 // model or context AS PART OF producing the result (Auto-Fit locks every
@@ -7222,6 +7224,7 @@ function _currentSupport(p) {
 function _restampSupport() {
   const key = _startsLiveKey();
   for (const p of state.peaks) if (p.support) p.support.fitKey = key;
+  if (state.fitResult) state.fitResult.startsModelKey = key;   // F1: the statistics are the same result's
 }
 // Patch the sidebar cards in place for the current verdicts (a re-render would
 // replace an input the student is typing in): header centre, the three summary
@@ -7341,6 +7344,7 @@ function applyAutoFitResult(json, graphiteRaw, roi) {
     backendResult: json,
     fittedY: json.fitted_y,
     roiRange,
+    startsModelKey: _startsLiveKey(),   // F1: binds the statistics to this model; re-stamped below with the locks
   };
   state.fitResult.rFactor = _computeRFactor(state.fitResult);
 
@@ -7483,6 +7487,9 @@ async function runAutoFitC1sGraphite() {
     // other request inputs, before the first await (a tab switch during the
     // upload must not send another tab's id).
     const anchorId = String((state.peaks.find(p => p.name === 'Graphite') || state.peaks[0]).id);
+    // the model and its fit context as sent (F1, Codex round 1): a result must
+    // not be applied, and stamped current, over a model edited while it ran
+    const ctxAtRequest = _startsLiveKey();
     // Build peak specs and overlay the per-peak bounds we attached in buildAutoFitModel.
     const peakSpecs = state.peaks.map(p => {
       const spec = peakToBackendSpec(p);
@@ -7527,6 +7534,12 @@ async function runAutoFitC1sGraphite() {
       _autoFitRestore(snap, fittingTab);
       return;
     }
+    if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
+      _hideFitSpinner();
+      notify('Auto-fit discarded because the model or its background / ROI settings were edited while it was running. Previous peaks and result restored. Run it again.', 'amber', true);
+      _autoFitRestore(snap, fittingTab);
+      return;
+    }
 
     applyBackendResult(json);
 
@@ -7618,6 +7631,25 @@ function _startsModelKey(peaks, ui, ccShift, anchors) {
     a: (anchors || []).map(v => [v.x, v.y]),
   });
 }
+// Two keys describe the same fit when they are equal after the form fields'
+// numbers are canonicalised: '280' and '280.0' select the same data and send
+// the same request (F1, Codex round 1). Compared, never rewritten, so keys
+// already persisted in saved files keep matching.
+function _fitKeyCanon(k) {
+  if (typeof k !== 'string') return k;
+  const memo = _fitKeyCanon._memo || (_fitKeyCanon._memo = new Map());
+  let c = memo.get(k);
+  if (c !== undefined) return c;
+  try {
+    const o = JSON.parse(k);
+    if (o && Array.isArray(o.u)) o.u = o.u.map(v => (typeof v === 'string' && v.trim() !== '' && Number.isFinite(Number(v))) ? String(Number(v)) : v);
+    c = JSON.stringify(o);
+  } catch (_) { c = k; }
+  if (memo.size > 256) memo.clear();
+  memo.set(k, c);
+  return c;
+}
+function _sameFitKey(a, b) { return !!a && !!b && (a === b || _fitKeyCanon(a) === _fitKeyCanon(b)); }
 // The key of the ACTIVE tab as it stands now (live model, live controls).
 function _startsLiveKey() {
   const ui = (typeof tabManager !== 'undefined' && tabManager && tabManager._captureUI) ? tabManager._captureUI() : {};
@@ -7628,14 +7660,55 @@ function _startsRecordKey(t) { return _startsModelKey(t.peaks, t.ui, t.ccShift,
 // The starts evidence of `fr` if it still describes the fit whose key is `key`, else null.
 function _startsIfCurrent(fr, key) {
   const st = fr && fr.starts;
-  if (!st || !fr.startsModelKey || fr.startsModelKey !== key) return null;
+  if (!st || !fr.startsModelKey || !_sameFitKey(fr.startsModelKey, key)) return null;
   return st;
 }
+// Unit F1 (2026-09-25): the fit STATISTICS (chi-square, sigma, R-factor, RMSE
+// and the stored fitted curve) are bound to the fit that produced them by the
+// SAME key — no second mechanism. One accessor classifies a result:
+//   'current'    the key matches: they describe the model shown;
+//   'stale'      the key differs: they belong to the previous model (an edit,
+//                a Find Peaks apply, an undo or a history restore since);
+//   'unverified' the result carries no key (saved before this unit): whether
+//                it described the saved model cannot be known — shown, with a
+//                note to re-run;
+//   'none'       no result.
+// The sealed fit record absorbs this: its record carries key and statistics.
+function _statsState(fr, key) {
+  if (!fr) return 'none';
+  if (!fr.startsModelKey) return 'unverified';
+  return _sameFitKey(fr.startsModelKey, key) ? 'current' : 'stale';
+}
+function _statsLiveState() { return _statsState(state.fitResult, _startsLiveKey()); }
+// A record's result judged against the RECORD's key (project save, stack tabs).
+function _statsRecordState(t) { return _statsState(t && t.fitResult, t ? _startsRecordKey(t) : ''); }
+const _STATS_STALE_NOTE = 'The model or its fit settings changed after this fit: its \u03c7\u00b2, R-factor, RMSE and uncertainties belong to the previous model and are not reported. Run Fit to obtain statistics for this model.';
+const _STATS_UNVERIFIED_NOTE = 'This result was saved without the record that binds it to its model, so it cannot be confirmed that its \u03c7\u00b2, R-factor and uncertainties describe the model shown. Run Fit to confirm.';
+function _statsNote(st) { return st === 'stale' ? _STATS_STALE_NOTE : st === 'unverified' ? _STATS_UNVERIFIED_NOTE : ''; }
+// Fields a save adds beside the result (the key itself is saved as always).
+function _statsSaveFields(st) {
+  return (st === 'stale' || st === 'unverified') ? { statisticsState: st, statisticsNote: _statsNote(st) } : {};
+}
+// Keep the visible statistics honest after an edit that only repainted the
+// chart: re-render Results when the state it rendered differs; re-apply the
+// header / status bar / R always (cheap, no inputs there).
+function _refreshStatsState() {
+  const st = _statsLiveState();
+  const el = document.getElementById('results-area');
+  // 'none' too: Clear All nulls the result and only repaints (Codex round 1)
+  if (el && el.getAttribute('data-stats-state') !== st && (state.fitResult || el.getAttribute('data-stats-state')) && typeof renderResults === 'function') renderResults();   // applies the header / status bar too
+  else _applyStatDisplay(state.fitResult);
+  if (typeof _updateRFactorUI === 'function') _updateRFactorUI(state.fitResult ? state.fitResult.rFactor : null);
+}
+
 // After anything that may have changed the model or its context without going
 // through a Results re-render (a lock toggle, Lock All, a background or ROI
 // control): take a stale alternative overlay off the chart and bring the
 // VISIBLE panel up to date (counts -> "the model has changed since this fit").
 function _refreshStartsEvidence(repaint, fromPlot) {
+  // F1: chi-square / sigma / R follow the same key, from every caller (lock
+  // toggles and Lock All reach here without a repaint; Codex round 1)
+  _refreshStatsState();
   const hadAlt = !!(_historyPreview && typeof _historyPreview.snapId === 'string' && _historyPreview.snapId.startsWith('alt:'));
   _dropStaleAltPreview();
   if (repaint && hadAlt && !_historyPreview && typeof updatePlot === 'function') updatePlot();
@@ -7850,6 +7923,7 @@ async function runFit(opts = {}) {
 
   // Try Flask backend first
   let backendResult = null;
+  let ctxAtRequest = null;   // set with the other request inputs; read again by the local fallback
   try {
     const bgType  = document.getElementById('bg-type').value;
     const bgStart = parseFloat(document.getElementById('bg-start').value);
@@ -7869,7 +7943,7 @@ async function runFit(opts = {}) {
     const nStarts = _startsUnlinkedCount(startModel) >= 2 ? _STARTS_N : 0;
     // the live model and its fit context as the student pressed the button: a
     // result must not be written over a model that was edited while it ran
-    const ctxAtRequest = _startsLiveKey();
+    ctxAtRequest = _startsLiveKey();
     const fitMethod = document.getElementById('fit-method').value;
     const epAvgVal = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
     const bgPayload = { method: bgType, start_idx: bgWin.i0, end_idx: bgWin.i1 + 1, endpoint_avg: epAvgVal };
@@ -7945,7 +8019,7 @@ async function runFit(opts = {}) {
     // The peak controls stay editable while the fit runs. A result computed for
     // the model as it was must not be applied over an edited one (a newly locked
     // centre would keep its edited value under the server's statistics).
-    if (_startsLiveKey() !== ctxAtRequest) {
+    if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
       _hideFitSpinner();
       document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
       notify('Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.', 'amber', true);
@@ -7994,6 +8068,14 @@ async function runFit(opts = {}) {
       notify('The server could not be reached, so the alternative was not applied. Previous peaks and result kept.', 'red', true);
       return;
     }
+    if (e && e.transportFailure && ctxAtRequest !== null && !_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
+      // The fallback would fit the arrays captured at the press over a model or
+      // context edited since, and stamp the edited one (F1, Codex round 1).
+      _hideFitSpinner();
+      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
+      notify('The server could not be reached, and the model or its background / ROI settings were edited while the fit was running, so no local fit was run. Previous peaks and result kept. Run the fit again.', 'amber', true);
+      return;
+    }
     if (e && e.transportFailure) {
       // Server unreachable: the local optimiser is the honest fallback, and
       // the overlay saying so opens only if it actually converged.
@@ -8125,8 +8207,14 @@ function _applyStatCaption(fr) {
 function _applyStatDisplay(fr) {
   const fq = document.getElementById('fit-quality');
   const sb = document.getElementById('sb-chi');
-  if (fr && Number.isFinite(fr.chiReduced)) {
-    if (fq) { fq.textContent = _fitStatusText(fr); fq.setAttribute('data-xps-tip', _isLocalFit(fr) ? _LOCALFIT_TOOLTIP : _CHISQ_TOOLTIP); }
+  const st = (fr && fr === state.fitResult) ? _statsLiveState() : 'current';
+  if (fr && Number.isFinite(fr.chiReduced) && st === 'stale') {
+    // F1: the statistic belongs to the previous model: say so, show no number
+    if (fq) { fq.textContent = _fitStatLabel(fr) + ' \u2014 (model changed)'; fq.setAttribute('data-xps-tip', _STATS_STALE_NOTE); }
+    if (sb) sb.textContent = '\u2014';
+  } else if (fr && Number.isFinite(fr.chiReduced)) {
+    const tip = (_isLocalFit(fr) ? _LOCALFIT_TOOLTIP : _CHISQ_TOOLTIP) + (st === 'unverified' ? '\n\n' + _STATS_UNVERIFIED_NOTE : '');
+    if (fq) { fq.textContent = _fitStatusText(fr); fq.setAttribute('data-xps-tip', tip); }
     if (sb) sb.textContent = fr.chiReduced.toFixed(3);
   } else {
     if (fq) { fq.innerHTML = '&#967;&#178; &mdash;'; fq.removeAttribute('data-xps-tip'); }
@@ -8497,7 +8585,8 @@ function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
   state.fitResult = { chi, chiReduced, rmse, be, bgSubtracted, bgIntensity, roiRange,
                       engine: 'local', status: 'converged',
                       objective: 'poisson_weighted_chi_square', weighting: '1/sqrt(max(counts,1))', iterations,
-                      reportable: false, caveat: _LOCAL_FIT_CAVEAT };
+                      reportable: false, caveat: _LOCAL_FIT_CAVEAT,
+                      startsModelKey: _startsLiveKey() };   // F1: the statistics describe the committed model
   state.fitResult.rFactor = _computeRFactor(state.fitResult);
 
   _applyStatDisplay(state.fitResult);
@@ -8564,6 +8653,8 @@ function _peakArea(p, be) {
 
 function renderResults() {
   const el = document.getElementById('results-area');
+  const _stats = _statsLiveState();   // F1: current / stale / unverified / none
+  if (el) el.setAttribute('data-stats-state', _stats);
   _applyStatDisplay(state.fitResult);   // header + status bar track every result change (clear, restore, auto-fit) as one unit
   _updateLocalModelBanner();
   if (!state.fitResult) {
@@ -8583,7 +8674,14 @@ function renderResults() {
 
   const { chiReduced, rmse, backendResult } = state.fitResult;
   const _statIsChi = _fitStatLabel(state.fitResult) !== 'Residual variance';
-  const stderrMap = _buildStderrMap(state.fitResult);
+  const _stale = _stats === 'stale';
+  // F1: a stale result's sigma belongs to the previous model: none is shown
+  const stderrMap = _stale ? {} : _buildStderrMap(state.fitResult);
+  const _statsBanner = _stale ? `
+    <div class="stats-stale-note" style="background:rgba(245,158,11,0.12);border:1px solid var(--amber,#f59e0b);border-radius:var(--radius);padding:8px 10px;margin-bottom:10px;font-size:11px;line-height:1.5;color:var(--text)">
+      &#9888; <strong>The model has changed since this fit.</strong> Its &#967;&#178;, RMSE, R-factor and uncertainties belong to the previous model and are not shown. The table below is the current model, not a fitted result. Press <strong>Run Fit</strong> to obtain statistics for it.
+    </div>` : _stats === 'unverified' ? `
+    <div class="stats-unverified-note" style="font-size:11px;line-height:1.5;color:var(--text2);margin-bottom:8px">${_escHtml(_STATS_UNVERIFIED_NOTE)}</div>` : '';
   // A local (unweighted) result is a STARTING POINT: its areas can differ
   // from the server's Poisson-weighted fit by more than 100 % (measured on
   // the lab's C1s scans, unit A0). It is shown as such, never as a result.
@@ -8598,22 +8696,23 @@ function renderResults() {
     return val.toFixed(decimals);
   }
 
-  let html = _localBanner + `
+  const _dash = '<span style="color:var(--text3)">&mdash;</span>';
+  let html = _statsBanner + _localBanner + `
     <div style="display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap">
       <div style="flex:1;background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);padding:8px 10px">
         <div style="font-size:9px;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px">${_escHtml(_fitStatLabel(state.fitResult))}</div>
-        <div style="font-family:var(--mono);font-size:16px;color:${_statIsChi ? (chiReduced<2?'var(--green)':chiReduced<5?'var(--amber)':'var(--red)') : 'var(--text)'}">${chiReduced.toFixed(3)}</div>
+        <div style="font-family:var(--mono);font-size:16px;color:${_stale ? 'var(--text3)' : _statIsChi ? (chiReduced<2?'var(--green)':chiReduced<5?'var(--amber)':'var(--red)') : 'var(--text)'}">${_stale ? _dash : chiReduced.toFixed(3)}</div>
       </div>
       <div style="flex:1;background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);padding:8px 10px">
         <div style="font-size:9px;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px">RMSE</div>
-        <div style="font-family:var(--mono);font-size:16px;color:var(--accent2)">${rmse.toFixed(1)}</div>
+        <div style="font-family:var(--mono);font-size:16px;color:var(--accent2)">${_stale ? _dash : rmse.toFixed(1)}</div>
       </div>
       ${backendResult ? `<div style="flex:1;background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);padding:8px 10px">
         <div style="font-size:9px;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px">Engine</div>
         <div style="font-family:var(--mono);font-size:11px;color:var(--green)">lmfit</div>
       </div>` : ''}
     </div>
-    ${_renderRFactorPanel(state.fitResult.rFactor)}
+    ${_stale ? '' : _renderRFactorPanel(state.fitResult.rFactor)}
     <table class="results-table">
       <thead><tr>
         <th>Peak</th><th>Center (eV)</th><th>FWHM (eV)</th><th>Area</th><th>%</th>
@@ -9015,8 +9114,9 @@ function _buildEntryRenderData(entry) {
 
   // Envelope (raw-level)
   let fittedY;
-  if (Array.isArray(fr.fittedY) && fr.fittedY.length === be.length) {
-    // Path A: backend fittedY directly (already raw-level).
+  if (Array.isArray(fr.fittedY) && fr.fittedY.length === be.length && _statsRecordState(src) !== 'stale') {
+    // Path A: backend fittedY directly (already raw-level). Never a stale
+    // result's curve (F1: judged against the SOURCE record's key).
     fittedY = fr.fittedY.slice();
   } else {
     // Path A2/B: compose envelope from peaks + bg.
@@ -9491,8 +9591,11 @@ function updatePlot() {
   const modelFull = evalAllPeaks(plotBE, state.peaks);
   // Use backend fitted_y when available (authoritative lmfit result);
   // fall back to JS-recomputed modelFull + bg for pre-fit / local-LM fits.
+  // F1: never a stale result's curve (Find Peaks apply / undo keep the old
+  // result over a replaced model): the envelope is then the current peaks
   const fittedYBacked = haveFit && state.fitResult.fittedY &&
-                        state.fitResult.fittedY.length === plotBE.length
+                        state.fitResult.fittedY.length === plotBE.length &&
+                        _statsLiveState() !== 'stale'
                         ? state.fitResult.fittedY : null;
   const rawResiduals = fittedYBacked
     ? plotInten.map((v, i) => v - fittedYBacked[i])
@@ -10203,6 +10306,7 @@ function _doSaveFit() {
       chosenAlternative: _startsIfCurrent(state.fitResult, _startsLiveKey()) ? (state.fitResult.chosenAlternative || null) : null,
       reportable: _isLocalFit(state.fitResult) ? false : (state.fitResult.reportable ?? null),
       caveat: _localFitCaveat(state.fitResult) || state.fitResult.caveat || null,
+      ..._statsSaveFields(_statsLiveState()),   // F1: says plainly when the statistics belong to the previous model
     } : ((_activeTab() && _activeTab().modelProvenance) ? {
       ..._activeTab().modelProvenance, reportable: false, caveat: _localFitCaveat(_activeTab().modelProvenance),
     } : null),
@@ -10226,7 +10330,10 @@ function _doSaveSpectrum() {
   const modelFull = evalAllPeaks(be, state.peaks);
   const bgSub = inten.map((v, i) => v - bgIntensity[i]);
   const residuals = bgSub.map((v, i) => v - modelFull[i]);
-  const fittedY = state.fitResult?.fittedY || modelFull.map((v, i) => v + bgIntensity[i]);
+  // F1: a stale result's stored curve is the previous model's; the file's
+  // fittedY then matches its residuals (the current model), as with no fit
+  const _saveStats = _statsLiveState();
+  const fittedY = (_saveStats !== 'stale' && state.fitResult?.fittedY) || modelFull.map((v, i) => v + bgIntensity[i]);
 
   // Per-peak curves and areas. evalPeakArray(), not per-point evalPeak:
   // for LACX with caM > 0, only the array evaluator applies the shape's
@@ -10249,6 +10356,7 @@ function _doSaveSpectrum() {
     chi: state.fitResult.chi,
     chiReduced: state.fitResult.chiReduced,
     rmse: state.fitResult.rmse,
+    rFactor: state.fitResult.rFactor || null,   // F1: the fit's own R (restored only while current)
     // Engine identity travels with the statistic so a reloaded local-engine
     // result is never relabelled as chi-square (unit A0).
     engine: state.fitResult.engine || null,
@@ -10262,6 +10370,7 @@ function _doSaveSpectrum() {
     // these fields existed) is designated on re-save too.
     reportable: _isLocalFit(state.fitResult) ? false : (state.fitResult.reportable ?? null),
     caveat: _localFitCaveat(state.fitResult) || state.fitResult.caveat || null,
+    ..._statsSaveFields(_saveStats),
   } : null;
 
   const data = {
@@ -10336,6 +10445,7 @@ async function _doSaveProject() {
       fitResult: t.fitResult ? {
         chi: t.fitResult.chi, chiReduced: t.fitResult.chiReduced,
         rmse: t.fitResult.rmse, fittedY: t.fitResult.fittedY || null,
+        rFactor: t.fitResult.rFactor || null,   // F1: the fit's own R, not one recomputed from edited peaks on reload
         // Frozen fit grid: persisted so post-load updatePlot() renders the
         // recorded fit (haveFit path) instead of recomputing background and
         // residuals from current settings. Absent in older saves — loaders
@@ -10356,6 +10466,7 @@ async function _doSaveProject() {
         iterations: t.fitResult.iterations ?? null,
         reportable: _isLocalFit(t.fitResult) ? false : (t.fitResult.reportable ?? null),
         caveat: _localFitCaveat(t.fitResult) || t.fitResult.caveat || null,
+        ..._statsSaveFields(_statsRecordState(t)),   // F1: judged against the RECORD's key
       } : null,
       modelProvenance: t.modelProvenance || null,
       notes: t.notes || '',
@@ -10573,7 +10684,10 @@ function _loadSpectrumFile(data, sessionFile) {
     const fr = { chi: data.statistics.chi, chiReduced: data.statistics.chiReduced, rmse: data.statistics.rmse };
     for (const k of ['engine', 'objective', 'weighting', 'status', 'caveat', 'starts', 'startsModelKey', 'chosenAlternative']) if (data.statistics[k]) fr[k] = data.statistics[k];
     if (data.statistics.reportable !== undefined && data.statistics.reportable !== null) fr.reportable = data.statistics.reportable;
-    if (data.fittedY) fr.fittedY = data.fittedY;
+    // F1: a stale save's fittedY is the EDITED model's curve (written for the
+    // file's readers); it is never installed under the original fit's key
+    if (data.fittedY && data.statistics.statisticsState !== 'stale') fr.fittedY = data.fittedY;
+    if (data.statistics.rFactor && data.statistics.statisticsState !== 'stale') fr.rFactor = data.statistics.rFactor;
     active.fitResult = fr;
     state.fitResult = fr;
   }
@@ -10917,7 +11031,11 @@ function exportResults() {
   }
 
   const warning = _isLocalModel() ? '# WARNING: ' + _localFitCaveat(_governingProvenance()) + '\n' : '';
-  const csv = warning + rows.map(r => r.join('\t')).join('\n');
+  // F1: the columns are computed from the CURRENT peaks; after an edit they
+  // are the edited, unfitted model, not the last fit's curve
+  const staleNote = _statsLiveState() === 'stale'
+    ? '# NOTE: the model has changed since the last fit: Model, Residual and the component columns are the current (unfitted) model, not a fitted result. Run Fit before reporting.\n' : '';
+  const csv = warning + staleNote + rows.map(r => r.join('\t')).join('\n');
   const blob = new Blob([csv], { type: 'text/tab-separated-values' });
   const url = URL.createObjectURL(blob);
   const a = document.createElement('a');
@@ -10951,7 +11069,9 @@ function _doPublicationExport() {
   if (!be.length) { notify('No data in ROI.', 'red'); return; }
 
   const bgArr   = computeBackground(be, inten);
-  const fittedY = (state.fitResult?.fittedY?.length === be.length) ? state.fitResult.fittedY : null;
+  // F1: a stale result's fitted curve is the previous model's: not drawn as "Fit"
+  const _figStats = _statsLiveState();
+  const fittedY = (_figStats !== 'stale' && state.fitResult?.fittedY?.length === be.length) ? state.fitResult.fittedY : null;
   const residArr = fittedY ? inten.map((v, i) => v - fittedY[i]) : null;
   const invert   = document.getElementById('invert-be').checked;
   const showIndiv = document.getElementById('show-individual').checked;
@@ -11160,10 +11280,12 @@ function _doPublicationExport() {
   if (state.fitResult || _isLocalModel()) {
     ctx.font = '38px Arial,sans-serif';
     ctx.fillStyle = '#555555'; ctx.textAlign = 'left'; ctx.textBaseline = 'top';
-    if (state.fitResult) {
+    if (state.fitResult && _figStats === 'stale') {
+      ctx.fillText('Model changed since the fit: no statistics, not a fitted result', plotX + 14, mainTop + 14);
+    } else if (state.fitResult) {
       const statLabel = !_isLocalFit(state.fitResult) ? '\u03c7\u00b2_r'
         : (_isUnweightedLocal(state.fitResult) ? 'Residual variance (local fit, not reportable)' : '\u03c7\u00b2_r (local fit, not reportable)');
-      ctx.fillText(statLabel + '\u2009=\u2009' + state.fitResult.chiReduced.toFixed(3),
+      ctx.fillText(statLabel + '\u2009=\u2009' + state.fitResult.chiReduced.toFixed(3) + (_figStats === 'unverified' ? ' (unverified)' : ''),
                    plotX + 14, mainTop + 14);
     } else {
       ctx.fillText('Imported local fit: starting point, not reportable', plotX + 14, mainTop + 14);
@@ -11322,7 +11444,10 @@ function _shapeExportCols(p) {
 function exportFitTable(fmt) {
   if (!state.fitResult) { notify('Run a fit first.', 'red'); return; }
   const { be } = state.fitResult;
-  const stderrMap = _buildStderrMap(state.fitResult);
+  // F1: a stale result's chi-square and sigma belong to the previous model:
+  // neither is written; a WARNING line says why
+  const _stats = _statsLiveState();
+  const stderrMap = _stats === 'stale' ? {} : _buildStderrMap(state.fitResult);
   const areas = state.peaks.map(p => _peakArea(p, be));
   const totalArea = areas.reduce((s,v)=>s+v,0);
   const rsfVals = state.peaks.map(p => {
@@ -11371,7 +11496,9 @@ function exportFitTable(fmt) {
     const wb = XLSX.utils.book_new();
     const metaWS = XLSX.utils.aoa_to_sheet([
       ['XPS Fitting Studio Export'], ['Date', date],
-      [_statName, chiStr], ['Background type', bgType],
+      ...(_stats === 'stale' ? [['WARNING', _STATS_STALE_NOTE]] : [[_statName, chiStr]]),
+      ...(_stats === 'unverified' ? [['NOTE', _STATS_UNVERIFIED_NOTE]] : []),
+      ['Background type', bgType],
       ...(_isLocalFit(state.fitResult) ? [['WARNING', _localFitCaveat(state.fitResult)]] : []),
       ...(unsupportedNames.length ? [['WARNING', 'Not supported by the data (centre, width, uncertainties and At% not reported): ' + unsupportedNames.join(', ')]] : []),
       ...(_startsSummaryText(_startsIfCurrent(state.fitResult, _startsLiveKey())) ? [['Scattered starts', _startsSummaryText(_startsIfCurrent(state.fitResult, _startsLiveKey()))]] : []),
@@ -11384,7 +11511,9 @@ function exportFitTable(fmt) {
     notify('Exported XLSX table', 'green');
   } else {
     let csv = `# XPS Fitting Studio Export\n# Date: ${date}\n`;
-    csv += `# ${_statName}: ${chiStr}\n# Background: ${bgType}\n`;
+    csv += _stats === 'stale' ? `# WARNING: ${_STATS_STALE_NOTE}\n` : `# ${_statName}: ${chiStr}\n`;
+    if (_stats === 'unverified') csv += `# NOTE: ${_STATS_UNVERIFIED_NOTE}\n`;
+    csv += `# Background: ${bgType}\n`;
     if (_isLocalFit(state.fitResult)) csv += `# WARNING: ${_localFitCaveat(state.fitResult)}\n`;
     if (unsupportedNames.length) csv += `# WARNING: Not supported by the data (centre, width, uncertainties and At% not reported): ${unsupportedNames.join(', ')}\n`;
     if (_startsSummaryText(_startsIfCurrent(state.fitResult, _startsLiveKey()))) csv += `# Scattered starts: ${_startsSummaryText(_startsIfCurrent(state.fitResult, _startsLiveKey()))}\n`;
@@ -11491,6 +11620,13 @@ function _renderRFactorPanel(rf) {
 function _updateRFactorUI(rf) {
   const el = document.getElementById('sb-runs');
   if (!el) return;
+  if (rf && state.fitResult && rf === state.fitResult.rFactor && _statsLiveState() === 'stale') {
+    // F1: the previous model's R-factor is not shown beside the edited model
+    el.style.color = 'var(--text3)';
+    el.textContent = 'R: \u2014';
+    el.setAttribute('data-xps-tip', _STATS_STALE_NOTE);
+    return;
+  }
   if (!rf) {
     el.textContent = '';
     el.removeAttribute('data-xps-tip');
@@ -11556,6 +11692,9 @@ const _CHISQ_TOOLTIP = "Reduced chi-squared (\u03c7\u00b2\u1d63) measures the go
 // ═══════════════════════════════════════════════════
 function _validateUncertainties() {
   if (!state.fitResult?.backendResult?.individual_peaks) return { warnings: [], info: [] };
+  // F1: a stale result's sigma and bounds describe the previous model; the
+  // Results banner says so once — no per-parameter rule is judged on them
+  if (_statsLiveState() === 'stale') return { warnings: [], info: [] };
   const warnings = [];
   const info = [];
   const stderrMap = _buildStderrMap(state.fitResult);

exec
/bin/zsh -lc "sed -n '3270,3360p' templates/index.html; sed -n '9470,9558p' templates/index.html; sed -n '7120,7158p' templates/index.html; sed -n '1,75p' tests/js/stale_statistics.test.js; rg -n 'function _autoFitRestore|function _autoFitSnapshot|function clearAllPeaks|function updatePeak|_restampSupport\\(' templates/index.html; rg -n '(startsModelKey|fitKey|altKey|ctxAtRequest).*(===|"'!==)|(===|!==).*(startsModelKey|fitKey|altKey|ctxAtRequest)'"' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:

  closeTab(id) {
    const idx = this.tabs.findIndex(t => t.id === id);
    if (idx === -1) return;
    const closing = this.tabs[idx];
    const closingName = closing.name;
    const wasStack = !!closing.isStack;
    this.tabs.splice(idx, 1);

    // Prune stack entries that referenced the closed tab (skip if it was
    // itself a stack — stacks don't reference each other).
    if (!wasStack) {
      for (const t of this.tabs) {
        if (!t.isStack) continue;
        const before = t.entries.length;
        t.entries = t.entries.filter(e => e.sourceTabId !== id);
        const removed = before - t.entries.length;
        if (removed > 0) {
          notify('Removed "' + closingName + '" from "' + t.name + '" (source tab closed).', 'amber');
          if (t.id === this.activeId) {
            renderStackLegend(t);
            // The chart holds datasets keyed to the removed entry: rebuild
            // it, or the closed source's curves (and, for a local source,
            // their only designation) outlive the entry (Codex A0 round 19).
            _renderStackChart(t);
          }
        }
      }
    }

    if (this.tabs.length === 0) {
      this.activeId = null;
      _updateUndoButtons();
      if (typeof _historyPreview !== 'undefined') _historyPreview = null;
      state.rawBE = []; state.rawIntensity = [];
      state.peaks = []; state.fitResult = null;
      state.ccShift = 0; state.nextId = 1;
      document.getElementById('data-info').textContent = 'no data';
      const _cl = document.getElementById('spec-combo-label');
      if (_cl) _cl.textContent = 'no data';
      document.getElementById('sb-pts').textContent = '\u2014';
      document.getElementById('sb-range').textContent = '\u2014';
      renderPeakList();
      renderEmptyChart();
      this.renderTabBar();
      this._updateSurveyPanel();
      this._updateCCVerifiedUI(true);
      _updateRFactorUI(null);
      _updateROIDisplay(null);
      const notesEl = document.getElementById('spectrum-notes');
      if (notesEl) notesEl.value = '';
      return;
    }

    if (this.activeId === id) {
      const nextIdx = Math.min(idx, this.tabs.length - 1);
      this.activeId = null; // force re-activate
      this.activateTab(this.tabs[nextIdx].id);
    } else {
      this.renderTabBar();
    }
    this._updateSurveyPanel();
  }

  // ── Folder upload ───────────────────────────────

  async loadFolder(fileList) {
    const files = Array.from(fileList);
    if (!files.length) return;

    const eligible = this._filterFiles(files);
    if (!eligible.length) {
      notify('No XPS data files found in folder.', 'amber');
      return;
    }

    const prog = document.getElementById('folder-progress');
    prog.classList.add('active');
    let done = 0;
    const update = () => { prog.textContent = 'Loading ' + done + '/' + eligible.length + '\u2026'; };
    update();

    for (const file of eligible) {
      await this._loadOneFile(file);
      done++;
      update();
    }

    prog.classList.remove('active');
    notify('Loaded ' + done + ' spectra', 'green');
  }
      let pi = 0;
      for (const pc of rd.peaks) {
        const pbgIdx = dsByKey.get(e.id + ':pbg:' + pc.peak.id);
        if (pbgIdx !== undefined) {
          const ds = state.chart.data.datasets[pbgIdx];
          // BG-sub view: pbg flattens to zero so peak fills anchor at baseline.
          ds.data = useBgSub
            ? rd.be.map((b, i) => ({ x: b, y: 0 + yShift }))
            : rd.be.map((b, i) => ({ x: b, y: rd.bg[i] + yShift }));
          // pbg stays "not hidden" so its fill anchor still works; it's
          // transparent so nothing is drawn anyway.
          const m = state.chart.getDatasetMeta(pbgIdx);
          if (m) m.hidden = false;
        }
        const pkIdx = dsByKey.get(e.id + ':peak:' + pc.peak.id);
        if (pkIdx !== undefined) {
          const ds = state.chart.data.datasets[pkIdx];
          ds.borderWidth = lineWidth;
          ds.data = useBgSub
            ? rd.be.map((b, i) => ({ x: b, y: pc.peakOnly[i] + yShift }))
            : rd.be.map((b, i) => ({ x: b, y: pc.y[i]        + yShift }));
          // Fill pill: mutate fill config in place. Chart.js v4 picks
          // this up on update('none') for the filler plugin. If a future
          // Chart.js version regresses on that, fall back by calling
          // _updateStackChart(stack, { invalidate: 'datasets' }) from
          // the show-fill onchange handler instead.
          ds.fill = pills.showFill
            ? { target: pbgIdx !== undefined ? pbgIdx : (pi), above: pc.peak.color + '40', below: 'transparent' }
            : false;
          const m = state.chart.getDatasetMeta(pkIdx);
          if (m) m.hidden = !peaksShown;
        }
        pi++;
      }
    }
    if (isVisible) visIdx++;
  }
  // Sync Y-axis label/ticks for offset state, and X-axis reverse for
  // the Invert BE pill. Mutate leaf fields only — assigning back
  // y.ticks / y.title would round-trip through Chart.js's options
  // resolver proxy and store a self-referencing object whose scriptable
  // callback property cycles when next resolved ("Recursion detected:
  // callback->callback"). _renderStackChart creates both ticks and
  // title at construction, so they always exist here. scales.x.reverse
  // is a boolean leaf — safe to mutate directly.
  const offsetActive = (stackTab.verticalOffset || 0) > 0;
  if (state.chart.options && state.chart.options.scales) {
    const sc = state.chart.options.scales;
    if (sc.x) {
      const invert = document.getElementById('invert-be')?.checked ?? true;
      sc.x.reverse = invert;
    }
    if (sc.y) {
      if (sc.y.ticks) sc.y.ticks.display = !offsetActive;
      if (sc.y.title) {
        sc.y.title.display = true;
        sc.y.title.text = offsetActive ? 'Intensity (offset stacked)' : 'Intensity (counts/s)';
      }
    }
  }
  state.chart.update('none');
}

function updatePlot() {
  // Stack-tab early branch: render multi-spectrum overlay, no peaks/fits.
  // Route through _updateStackChart so toolbar-pill toggles (Envelope,
  // Individual Peaks, Fill, Bkgrd Sub) and other state changes preserve
  // zoom by in-place updating. _updateStackChart delegates to
  // _renderStackChart automatically when no chart exists.
  {
    const _activeTab = (typeof tabManager !== 'undefined') ? tabManager._getTab(tabManager.activeId) : null;
    const _emptyEl = document.getElementById('stack-empty-state');
    const _canvas = document.getElementById('mainChart');
    if (isStackTab(_activeTab)) {
      _refreshRoiHint(null);   // a stack tab has no ROI of its own
      _updateStackChart(_activeTab);
      return;
    } else {
      if (_canvas) _canvas.style.display = '';
      if (_emptyEl) _emptyEl.style.display = 'none';
    }
  }

  // Full corrected spectrum (for raw data display and axis range)
  const corrBE = getCorrectedBE();
  const fullInten = state.rawIntensity;

  // ROI-filtered data (for fitting, background, peaks)
  const { be, inten } = getROIData();
// unit-free, ignores the background level and choice, and a spike adds to both
// chi-squares. 10 is the conventional "clearly significant" level for a nested
// model (p ~ 1e-9 at these sizes) and sits a factor 17 below the weakest
// resolved anchor seen.
// SCOPE: it answers "do the data support this component?", not "is it graphite?"
// — a one-channel spike or a plateau under background None is supported.
// KNOWN LIMITS (owner decision 2026-09-21: ship with these, write no seventh rule):
//   - It REJECTS A REAL ANCHOR when the fitted region carries a gross
//     single-channel artefact — a spike of millions of counts, or a dead
//     (zero-count) channel: that channel's misfit dominates chi2_with and
//     drags F under 10. The user gets the red notice and the model is rolled
//     back; removing the artefact or narrowing the ROI recovers. A recoverable
//     refusal beats main's failure mode, a non-existent component silently
//     setting the energy reference of a whole spectrum.
//   - It does NOT ask whether the anchor is REQUIRED. With strong overlap the
//     other components could absorb it if refitted (chi2_without holds them at
//     their fitted values). That is fit determinacy, out of scope here: the
//     unsupported-component unit gets the refit-without-the-component test.
//   - Residue can still pass when an UNROUNDED manual background sits a
//     rounding step under data the upload flattened (Codex round 6, F ~ 280).
// ── "Not supported by the data" (unit step (b), 2026-09-22) ───────────────────
// A component whose amplitude the fit drove to its floor, pinned on a bound, or
// fitted to numerical residue is an explicit OUTCOME: the fit did not determine
// it. Owner decision 2026-09-18: flag it, and do not report its centre, width
// or sigma as if they were determined. The statement that needs no intensity
// floor (six were tried and failed): with the OTHER components held at their
// fitted values, removing this one must make the fit significantly worse — the
// F statistic the Auto-Fit anchor check uses (F >= 10). The SERVER computes it
// per component (`support: {f, delta_chi2, supported}`); the LOCAL engine
// computes the same statistic from its own residuals (_componentSupportCore);
// the twin below recomputes it from any response carrying counts, fitted_y
// and the component's curve. Known limits are the anchor check's: a gross
// single-channel artefact can mark a real component unsupported; redundancy
// under overlap is not detected. A linked component follows its parent.
//
// The verdict is a property of THE FIT THAT PRODUCED IT, conditional on the
// other components as fitted: peaks carry it as `p.support` together with
// `p.support.fitKey`, the key of the model and fit context at that time, and
// every consumer reads it through _isUnsupported, which compares that key
// Unit F1 (2026-09-25): the fit STATISTICS (chi-square, sigma, R-factor, RMSE
// and the stored fitted curve) are bound to the fit that produced them by the
// SAME model-plus-context key step (b) uses — no second mechanism. After an
// edit (or a Find Peaks apply / undo that keeps the old result over a replaced
// model) they belong to the previous model: the Results panel, header, status
// bar, R, uncertainty panel, CSV/XLSX, TSV, figure and saves say so or omit
// them. Plan: docs/superpowers/plans/2026-09-25-f1-stale-statistics.md.
//
// Functions are extracted verbatim from templates/index.html and run against
// a small DOM stub.

const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
const lines = html.split('\n');
function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name + '\\(');
  const start = lines.findIndex(l => re.test(l));
  assert.ok(start >= 0, `function ${name} not found`);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail('unbalanced ' + name);
}
const constLine = name => { const l = lines.find(x => x.startsWith('const ' + name)); assert.ok(l, name); return l; };

// ── a DOM stub: elements by id, attributes, textContent / innerHTML ─────────
function makeDoc() {
  const els = {};
  const mk = id => ({
    id, textContent: '', innerHTML: '', style: {}, attrs: {},
    setAttribute(k, v) { this.attrs[k] = String(v); }, getAttribute(k) { return k in this.attrs ? this.attrs[k] : null; },
    removeAttribute(k) { delete this.attrs[k]; },
  });
  for (const id of ['results-area', 'fit-quality', 'sb-chi', 'sb-runs', 'sb-chi-caption', 'quantify-area']) els[id] = mk(id);
  return { els, getElementById: id => els[id] || null, querySelector: () => null, querySelectorAll: () => [] };
}

const STATE_FNS = ['_fitKeyCanon', '_sameFitKey', '_statsState', '_statsLiveState', '_statsRecordState', '_statsNote', '_statsSaveFields'];
const STATE_CONSTS = ['_STATS_STALE_NOTE', '_STATS_UNVERIFIED_NOTE'];

// Build a sandbox with the F1 accessor, the display functions and renderResults.
function sandbox({ liveKey = 'K1' } = {}) {
  const doc = makeDoc();
  const env = { key: liveKey, quantified: null };
  const fns = [...STATE_FNS, '_fitStatLabel', '_isUnweightedLocal', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay',
    '_updateRFactorUI', '_renderRFactorPanel', 'renderResults', '_validateUncertainties'];
  const src = [...STATE_CONSTS.map(constLine), constLine('_RFACTOR_TOOLTIP'), constLine('_LOCALFIT_TOOLTIP'), constLine('_CHISQ_TOOLTIP'),
    ...fns.map(extractFn)].join('\n');
  const state = { peaks: [], fitResult: null, rawBE: [1] };
  const api = new Function('document', 'state', 'env', `
    const _startsLiveKey = () => env.key;
    const _startsRecordKey = t => t.key;
    const _isLocalFit = fr => !!(fr && fr.engine === 'local');
    const _isLocalModel = () => false;
    const _localFitCaveat = () => '';
    const _localFitDetail = () => '';
    const _updateLocalModelBanner = () => {};
    const _escHtml = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
    const _escAttr = _escHtml;
    const _buildStderrMap = fr => {
      const out = {};
      for (const ip of ((fr && fr.backendResult && fr.backendResult.individual_peaks) || [])) out[String(ip.id)] = ip.params;
      return out;
    };
    const _peakArea = p => p.amplitude;
    const _isUnsupported = () => false;
    const _unsupportedBadge = () => '';
    const _startsPanelHtml = () => '';
    const renderQuantify = (a, t) => { env.quantified = [a, t]; };
5949:function clearAllPeaks() {
5990:function updatePeakParam(id, key, value) {
6969:function _autoFitSnapshot() {
6994:function _autoFitRestore(snap, owner) {
7224:function _restampSupport() {
7372:  if (typeof _restampSupport === 'function') _restampSupport();
7652:function _sameFitKey(a, b) { return !!a && !!b && (a === b || _fitKeyCanon(a) === _fitKeyCanon(b)); }
7656:  return _startsModelKey(state.peaks, ui, state.ccShift, typeof _getManualAnchors === 'function' ? _getManualAnchors() : []);
7739:      !(state.fitResult && _historyPreview.altKey === state.fitResult.startsModelKey && _startsIfCurrent(state.fitResult, _startsLiveKey()))) {
8071:    if (e && e.transportFailure && ctxAtRequest !== null && !_sameFitKey(_startsLiveKey(), ctxAtRequest)) {

codex
I found a canonicalisation collision: `30` and `3e1` compare equal, but endpoint averaging uses `parseInt`, so they mean 30 and 3 points. That can leave statistics marked current after a real change. I’m reproducing the effect through the request path and checking the final-tab close path for stale display state.
exec
/bin/zsh -lc "sed -n '5580,5595p' templates/index.html; rg -n 'function renderPeakList|function renderEmptyChart' templates/index.html; sed -n '5940,5975p' templates/index.html; sed -n '6955,7055p' templates/index.html; sed -n '9556,9594p' templates/index.html; rg -n 'renderResults|_refreshStartsEvidence|_applyStatDisplay|_refreshStatsState' templates/index.html | head -45" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
    dragStart = null;
  });
}

// ═══════════════════════════════════════════════════
// CLICK-TO-PLACE PEAKS
// ═══════════════════════════════════════════════════
let placeMode = null; // null, 'peak', or 'multiplet'

// ── Multiplet preset modal ───────────────────────────────────────────────
let _pendingMultipletPreset = null; // set when user picks from modal

function _getSuggestedPresets() {
  // Look at current BE range to suggest matching elements
  const roiMin = parseFloat(document.getElementById('bg-end')?.value || 0);
  const roiMax = parseFloat(document.getElementById('bg-start')?.value || 9999);
6112:function renderPeakList() {
10031:function renderEmptyChart() {

function removePeak(id) {
  pushUndo();
  state.peaks = state.peaks.filter(p => p.id !== id && p.linked !== id);
  _invalidateFittedY();
  renderPeakList();
  updatePlot();
}

function clearAllPeaks() {
  if (!state.peaks.length) return;
  if (!confirm('Are you sure you want to clear all peaks?')) return;
  pushUndo();
  state.peaks = [];
  state.fitResult = null;
  { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }
  renderPeakList();
  updatePlot();
}

function getPeak(id) { return state.peaks.find(p => p.id === id); }

function unlinkPeak(id) {
  if (!confirm('Unlink this peak? It will become fully independent.')) return;
  pushUndo();
  const p = getPeak(id);
  if (!p) return;
  p.linked = null;
  renderPeakList();
  updatePlot();
}

// Handler for the linked-peak "Ratio (I₂/I₁)" input.
// Clamps to [0.01, 2] so the user can't accidentally zero out both peaks by
// typing 0 (which historically back-propagated a zero amplitude to the parent).
// A ratio of 0 is not physically meaningful for a linked multiplet anyway —
  peaks[3]._afFwhmMin   = 0.80;          peaks[3]._afFwhmMax   = 3.50;
  peaks[4]._afCenterMin = 291.00 - 1.00; peaks[4]._afCenterMax = 291.00 + 1.00;
  peaks[4]._afFwhmMin   = 1.00;          peaks[4]._afFwhmMax   = 4.00;
  for (let i = 5; i < peaks.length; i++) {
    peaks[i]._afCenterMin = peaks[i].center - 0.80;
    peaks[i]._afCenterMax = peaks[i].center + 0.80;
    peaks[i]._afFwhmMin   = 0.50;
    peaks[i]._afFwhmMax   = 3.00;
  }
  return peaks;
}

// Capture exactly the bits of state Auto-Fit will mutate, so a failure can
// cleanly restore the tab. Returns an opaque snapshot object.
function _autoFitSnapshot() {
  return {
    // The snapshot is taken before the auto-fit's first await, so it is the
    // natural carrier of the owning record OBJECT (async ownership rule).
    owner:        _opOwner(),
    peaks:        JSON.parse(JSON.stringify(state.peaks || [])),
    fitResult:    state.fitResult ? { ...state.fitResult } : null,
    ccShift:      state.ccShift,
    // The provisional cc shift migrates manual anchors along with peak
    // centers (data-attached convention), so rollback must restore them too
    // — omitting this left anchors stranded in the provisional frame when
    // the auto-fit failed (Codex round-1 MAJOR, both runs).
    manualAnchors: JSON.parse(JSON.stringify(_getManualAnchors())),
    modelProvenance: (() => { const o = _opOwner(); return o && o.modelProvenance ? JSON.parse(JSON.stringify(o.modelProvenance)) : null; })(),
    nextId:       state.nextId,
    ccMethodDom:  document.getElementById('cc-method')?.value || 'none',
    ccObsDom:     document.getElementById('cc-obs')?.value || '',
    ccLitDom:     document.getElementById('cc-lit')?.value || '',
    roiMinDom:    document.getElementById('roi-min')?.value || '',
    roiMaxDom:    document.getElementById('roi-max')?.value || '',
    bgStartDom:   document.getElementById('bg-start')?.value || '',
    bgEndDom:     document.getElementById('bg-end')?.value || '',
  };
}

function _autoFitRestore(snap, owner) {
  // owner is the record OBJECT the auto-fit started on — normally the one
  // the snapshot itself carries (taken before the first await). Anything
  // that is not a record object (an id from an older caller, undefined) is
  // ignored in favour of the snapshot's owner. A closed tab's id comes back
  // on a NEW object after a project reload, so an id lookup would restore a
  // stale snapshot into the reopened tab (Codex 2026-09-09).
  if (!snap) return;
  if (!owner || typeof owner !== 'object') owner = snap.owner;
  if (!_ownerLive(owner)) return;
  // If the fitting tab is no longer active (the user switched tabs while
  // the auto-fit request was in flight), restore into that tab's RECORD.
  // Writing the snapshot into live state/DOM here would clobber the newly
  // active tab with the fitting tab's pre-auto-fit state while leaving
  // the fitting tab's record in the provisional cc frame (Codex round-2
  // MAJOR — a pre-existing defect for peaks/ccShift/DOM, not just the
  // newly-migrating anchors). activateTab already synced the provisional
  // live state into the record at switch-away, so overwriting the record
  // fields with the snapshot undoes exactly that.
  if (_activeTab() !== owner) {
    const t = owner;
    if (t.isStack) return;
    t.peaks = snap.peaks;
    t.fitResult = snap.fitResult;
    t.ccShift = snap.ccShift;
    t.manualAnchors = snap.manualAnchors || [];
    t.modelProvenance = snap.modelProvenance || null;
    t.nextId = snap.nextId;
    t.ui = { ...t.ui,
      ccMethod: snap.ccMethodDom, ccObs: snap.ccObsDom, ccLit: snap.ccLitDom,
      roiMin: snap.roiMinDom, roiMax: snap.roiMaxDom,
      bgStart: snap.bgStartDom, bgEnd: snap.bgEndDom };
    return;
  }
  state.peaks     = snap.peaks;
  state.fitResult = snap.fitResult;
  state.ccShift   = snap.ccShift;
  _setManualAnchors(snap.manualAnchors || []);
  { const _t = _activeTab(); if (_t) _t.modelProvenance = snap.modelProvenance || null; }
  state.nextId    = snap.nextId;
  const set = (id, v) => { const el = document.getElementById(id); if (el) el.value = v; };
  set('cc-method', snap.ccMethodDom);
  set('cc-obs',    snap.ccObsDom);
  set('cc-lit',    snap.ccLitDom);
  // The provisional 'c1s' correction hid the custom-target field; putting the
  // method back without its field left Custom with no visible input (same
  // rule as the tab-restore path, no change event).
  { const rf = document.getElementById('cc-ref-field'), tf = document.getElementById('cc-target-field');
    if (rf) rf.style.display = (snap.ccMethodDom === 'none') ? 'none' : 'block';
    if (tf) tf.style.display = (snap.ccMethodDom === 'custom') ? 'block' : 'none'; }
  set('roi-min',   snap.roiMinDom);
  set('roi-max',   snap.roiMaxDom);
  set('bg-start',  snap.bgStartDom);
  set('bg-end',    snap.bgEndDom);
  const disp = document.getElementById('cc-shift-display');
  if (disp) {
    const sh = -state.ccShift;
    disp.textContent = (sh >= 0 ? '+' : '') + sh.toFixed(3) + ' eV';
  }
  if (typeof renderPeakList === 'function') renderPeakList();
  if (typeof updatePlot === 'function') updatePlot();
}

  // ROI-filtered data (for fitting, background, peaks)
  const { be, inten } = getROIData();
  const invert = document.getElementById('invert-be').checked;
  const showIndividual = document.getElementById('show-individual').checked;
  const showResiduals = document.getElementById('show-residuals').checked;

  const _ob = document.getElementById('main-chart-wrap').querySelector('.onboard-wrap');
  if (_ob) _ob.remove();

  if (!corrBE.length) {
    renderEmptyChart();
    return;
  }

  // After a fit, freeze all curve data to the stored fit state so that
  // changing ROI never re-draws or recomputes the fit, background, or peaks.
  const haveFit = !!(state.fitResult && Array.isArray(state.fitResult.be) &&
                     state.fitResult.be.length > 0 &&
                     Array.isArray(state.fitResult.bgIntensity) &&
                     state.fitResult.bgIntensity.length === state.fitResult.be.length);

  // plotBE/plotBG/plotInten drive all fit-related curves (peaks, background, envelope).
  // When a fit exists, they come from the frozen fit state — ROI changes don't affect them.
  // Before fitting, they come from the current ROI so live peak previews still work.
  const plotBE = haveFit ? state.fitResult.be : be;
  const plotBG = haveFit ? state.fitResult.bgIntensity
                         : (be.length ? computeBackground(be, inten) : []);
  const plotInten = haveFit && Array.isArray(state.fitResult.bgSubtracted)
                    ? state.fitResult.bgSubtracted.map((v, i) => v + plotBG[i])
                    : inten;
  const bgSubtracted = haveFit && Array.isArray(state.fitResult.bgSubtracted)
                       ? state.fitResult.bgSubtracted
                       : plotInten.map((v, i) => v - plotBG[i]);

  const modelFull = evalAllPeaks(plotBE, state.peaks);
  // Use backend fitted_y when available (authoritative lmfit result);
  // fall back to JS-recomputed modelFull + bg for pre-fit / local-LM fits.
  // F1: never a stale result's curve (Find Peaks apply / undo keep the old
2461:  renderResults();   // the restored model's designation (or its absence) must be visible immediately
2477:  renderResults();   // the restored model's designation (or its absence) must be visible immediately
3249:    _applyStatDisplay(state.fitResult);
3265:    renderResults();
3483:      renderResults();   // installs the imported model's designation (or the plain placeholder) and clears stale widgets
6040:  _refreshStartsEvidence(true);      // a lock is part of the fitted model
6067:  _refreshStartsEvidence(true);
7358:  if (typeof _applyStatDisplay === 'function') _applyStatDisplay(state.fitResult);
7375:  if (typeof renderResults === 'function') renderResults();
7695:function _refreshStatsState() {
7699:  if (el && el.getAttribute('data-stats-state') !== st && (state.fitResult || el.getAttribute('data-stats-state')) && typeof renderResults === 'function') renderResults();   // applies the header / status bar too
7700:  else _applyStatDisplay(state.fitResult);
7708:function _refreshStartsEvidence(repaint, fromPlot) {
7711:  _refreshStatsState();
7726:  if (state.fitResult && shownIn('.results-table .unsupported-row') !== flaggedNow && typeof renderResults === 'function') { renderResults(); rendered = true; }   // renders Quantify and the starts panel too
8050:    _applyStatDisplay(state.fitResult);
8100:  renderResults();
8207:function _applyStatDisplay(fr) {
8592:  _applyStatDisplay(state.fitResult);
8599:  renderResults();
8654:function renderResults() {
8658:  _applyStatDisplay(state.fitResult);   // header + status bar track every result change (clear, restore, auto-fit) as one unit
9700:  _refreshStartsEvidence(false, true);   // background / ROI controls only repaint the chart: keep the visible consumers honest (fromPlot: the chart itself is being rebuilt)
10698:  renderResults();   // installs the restored result's designation in Results/Quantify and the statistic display (unit A0)
11802:  if (name === 'results' || name === 'quantify') renderResults();
14189:  renderResults();
16197:    // happened to re-render it. renderResults() already handles
16200:    renderResults();

exec
/bin/zsh -lc "node -e '
const fs = require('\\''fs'\\''), path = require('\\''path'\\'');
let src = fs.readFileSync('\\''tests/js/fit_acceptance.test.js'\\'','\\''utf8'\\'').split(\"test('\\''A08:\")[0];
src = src.replace(\"const { test } = require('\\''node:test'\\'');\",'\\'''\\'');
src = src.replace(\"src + '\\''\\\\nreturn { runFit };'\\''\", \"'\\''const tabManager = { _captureUI: () => ({ endpointAvg: document.getElementById(\\\"bg-endpoint-avg\\\").value }) };\\\\n'\\'' + src + '\\''\\\\nreturn { runFit };'\\''\");
const api = new Function('\\''require'\\'','\\''__dirname'\\'',src + '\\''\\nreturn { makeEnv, extractFn, lines };'\\'')(require,path.resolve('\\''tests/js'\\''));
(async () => {
let env, request;
env=api.makeEnv({uploadImpl:async()=>{env.dom['\\''bg-endpoint-avg'\\''].value='\\''3e1'\\'';return '\\''sid'\\'';}, fetchImpl:async(url,opts)=>{request=JSON.parse(opts.body);return {ok:true,json:async()=>({success:true,statistics:{reduced_chi_square:1},residuals:[]})};}});
env.dom['\\''bg-endpoint-avg'\\'']={value:'\\''30'\\''};
await env.runFit();
console.log({requestAvg:request.background.endpoint_avg,liveAvg:parseInt(env.dom['\\''bg-endpoint-avg'\\''].value),applied:env.calls.applied,message:env.dom['\\''sb-msg'\\''].textContent});
const funcs=['\\''_startsModelKey'\\'','\\''_sameFitKey'\\'','\\''_fitKeyCanon'\\'','\\''_statsState'\\''].map(api.extractFn).join('\\''\\n'\\'');
const constants=api.lines.slice(api.lines.findIndex(l=>l.startsWith('\\''const _STARTS_MODEL_FIELDS'\\'')),api.lines.findIndex(l=>l.startsWith('\\''const _STARTS_UI_FIELDS'\\''))+1).join('\\''\\n'\\'');
const keys=new Function(constants+'\\''\\n'\\''+funcs+'\\''\\nreturn {_startsModelKey,_sameFitKey,_statsState,_fitKeyCanon};'\\'')();
for(const field of ['\\''endpointAvg'\\'','\\''shirleyIter'\\'']){
const a=keys._startsModelKey([],{[field]:'\\''30'\\''},0,[]),b=keys._startsModelKey([],{[field]:'\\''3e1'\\''},0,[]);
console.log({field,state:keys._statsState({startsModelKey:a},b),readBefore:parseInt('\\''30'\\''),readAfter:parseInt('\\''3e1'\\'')});
}
for(let i=0;i<1000;i++)keys._fitKeyCanon(JSON.stringify({u:[String(i)]}));
console.log({memoSize:keys._fitKeyCanon._memo.size});
})().catch(e=>{console.error(e);process.exitCode=1});
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
{
  requestAvg: 30,
  liveAvg: 3,
  applied: 1,
  message: 'Fit complete (lmfit)'
}
{
  field: 'endpointAvg',
  state: 'current',
  readBefore: 30,
  readAfter: 3
}
{
  field: 'shirleyIter',
  state: 'current',
  readBefore: 30,
  readAfter: 3
}
{ memoSize: 233 }

exec
/bin/zsh -lc "sed -n '6112,6137p' templates/index.html; sed -n '10031,10103p' templates/index.html; sed -n '14162,14195p' templates/index.html; sed -n '11792,11808p' templates/index.html; sed -n '3820,3836p' templates/index.html; nl -ba templates/index.html | sed -n '7638,7652p'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
function renderPeakList() {
  _clearDisallowedChargeRef();
  _updateLocalModelBanner();
  const el = document.getElementById('peak-list');
  const empty = document.getElementById('peak-empty');
  // Preserve which peak cards are expanded before clearing
  const expandedIds = new Set();
  el.querySelectorAll('.peak-body.open').forEach(b => {
    const m = b.id.match(/peak-body-(\d+)/);
    if (m) expandedIds.add(Number(m[1]));
  });
  el.innerHTML = '';
  empty.style.display = state.peaks.length ? 'none' : 'block';
  const clearWrap = document.getElementById('peak-clear-wrap');
  if (clearWrap) clearWrap.style.display = state.peaks.length ? 'block' : 'none';
  document.getElementById('sb-peaks').textContent = state.peaks.length;
  _updateLockAllBtn();

  // Compute total area for percentage (using ROI data if available)
  const { be: _roiBE } = (typeof getROIData === 'function' && state.rawBE.length) ? getROIData() : { be: [] };
  const _peakAreas = {};
  let totalArea = 0;
  if (_roiBE.length) {
    for (const p of state.peaks) { const a = _peakArea(p, _roiBE); _peakAreas[p.id] = a; if (!_isUnsupported(p)) totalArea += a; }
  }

function renderEmptyChart() {
  if (typeof _refreshRoiHint === 'function') _refreshRoiHint(null);   // no data: no window to describe
  // Reference mode (A7): overlays selected + no spectrum loaded (palette open or
  // closed) → draw markers on a labeled 0–1200 eV axis instead of the onboarding
  // card. No overlays → the onboarding card (the chart is torn down below).
  if (typeof _refReferenceModeWanted === 'function' && _refReferenceModeWanted()) {
    _refRenderReferenceChart();
    return;
  }
  if (state.chart) { state.chart.destroy(); state.chart = null; }
  if (state.residChart) { state.residChart.destroy(); state.residChart = null; }
  document.getElementById('resid-wrap').classList.add('hidden');
  document.getElementById('resid-handle').classList.add('hidden');

  const wrap = document.getElementById('main-chart-wrap');
  const canvas = document.getElementById('mainChart');
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Remove any existing onboarding overlay
  const existing = wrap.querySelector('.onboard-wrap');
  if (existing) existing.remove();

  const ob = document.createElement('div');
  ob.className = 'onboard-wrap';
  ob.innerHTML = `
    <svg class="onboard-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
      <path d="M9 13h6"/><path d="M9 17h3"/>
    </svg>
    <div class="onboard-title">Load a spectrum to begin</div>
    <div class="onboard-steps">
      <div class="onboard-step">
        <div class="onboard-num">1</div>
        <div class="onboard-label">Drop a file</div>
      </div>
      <div class="onboard-step">
        <div class="onboard-num">2</div>
        <div class="onboard-label">Add peaks</div>
      </div>
      <div class="onboard-step">
        <div class="onboard-num">3</div>
        <div class="onboard-label">Run fit</div>
      </div>
    </div>
  `;
  wrap.appendChild(ob);
}

function updateResiduals(be, residuals, invert, show) {
  const _cc = _chartColors();
  const wrap = document.getElementById('resid-wrap');
  const handle = document.getElementById('resid-handle');
  if (!show) {
    if (state.residChart) { state.residChart.destroy(); state.residChart = null; }
    wrap.classList.add('hidden');
    handle.classList.add('hidden');
    return;
  }
  wrap.classList.remove('hidden');
  handle.classList.remove('hidden');
  // Preserve residuals zoom state before destroying
  const _savedResidYMax = state._residYMax || null;
  if (state.residChart) { state.residChart.destroy(); state.residChart = null; }
  const beMin = _arrMin(be);
  const beMax = _arrMax(be);
  const ctx = document.getElementById('residChart').getContext('2d');
  state.residChart = new Chart(ctx, {
    type: 'line',
    data: {
      datasets: [
        {
  const row = document.getElementById('hist-row-' + snapId);
  if (row) row.classList.add('hist-preview-active');
  updatePlot();
}

function _historyClearPreview() {
  _historyPreview = null;
  _updateLocalModelBanner();
  document.querySelectorAll('.hist-row').forEach(r => r.classList.remove('hist-preview-active'));
  updatePlot();
}

function _historyRestoreSnap(snapId) {
  const tab = tabManager._getTab(tabManager.activeId);
  if (!tab || !tab.snapshots) return;
  const snap = tab.snapshots.find(s => s.id === snapId);
  if (!snap) return;

  pushUndo();
  state.peaks = _normalizePeaksCRef(JSON.parse(JSON.stringify(snap.peaks)));
  state.fitResult = snap.fitResult ? { ...snap.fitResult } : null;
  tab.modelProvenance = null;   // the restored result governs the designation (unit A0)
  tabManager._syncActiveToRecord();

  _historyClearPreview();
  renderPeakList();
  updatePlot();
  renderResults();
  _closeHistoryPanel();
  notify('Snapshot restored.', 'green');
}

function _historyDeleteSnap(snapId) {
  const tab = tabManager._getTab(tabManager.activeId);
  const wasSurvey = document.getElementById('tab-survey').classList.contains('active');
  if (wasSurvey && name !== 'survey' && typeof tabManager !== 'undefined') {
    tabManager._restoreFromSurvey();
  }

  document.querySelectorAll('.panel-body > .tabs .tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.panel-body > .tab-panel').forEach(p => p.classList.remove('active'));
  el.classList.add('active');
  document.getElementById('tab-' + name).classList.add('active');

  if (name === 'results' || name === 'quantify') renderResults();
  if (name === 'survey' && typeof tabManager !== 'undefined') tabManager._showSurveyInMain();
}

function notify(msg, type, prominent) {
  if (prominent) {
    const toast = document.getElementById('prominent-toast');
    t.xZoomMin = state._mainXMin ?? null;
    t.xZoomMax = state._mainXMax ?? null;
    t.notes = document.getElementById('spectrum-notes')?.value || '';
    t.ui = this._captureUI();
  }

  _captureUI() {
    return {
      bgType:      document.getElementById('bg-type')?.value || 'shirley',
      bgStart:     document.getElementById('bg-start')?.value || '',
      bgEnd:       document.getElementById('bg-end')?.value || '',
      shirleyIter: document.getElementById('shirley-iter')?.value || '5',
      endpointAvg: document.getElementById('bg-endpoint-avg')?.value || LEGACY_ENDPOINT_AVG,
      roiMin:      document.getElementById('roi-min')?.value || '',
      roiMax:      document.getElementById('roi-max')?.value || '',
      ccMethod:    document.getElementById('cc-method')?.value || 'none',
      ccObs:       document.getElementById('cc-obs')?.value || '',
  7638	function _fitKeyCanon(k) {
  7639	  if (typeof k !== 'string') return k;
  7640	  const memo = _fitKeyCanon._memo || (_fitKeyCanon._memo = new Map());
  7641	  let c = memo.get(k);
  7642	  if (c !== undefined) return c;
  7643	  try {
  7644	    const o = JSON.parse(k);
  7645	    if (o && Array.isArray(o.u)) o.u = o.u.map(v => (typeof v === 'string' && v.trim() !== '' && Number.isFinite(Number(v))) ? String(Number(v)) : v);
  7646	    c = JSON.stringify(o);
  7647	  } catch (_) { c = k; }
  7648	  if (memo.size > 256) memo.clear();
  7649	  memo.set(k, c);
  7650	  return c;
  7651	}
  7652	function _sameFitKey(a, b) { return !!a && !!b && (a === b || _fitKeyCanon(a) === _fitKeyCanon(b)); }

exec
/bin/zsh -lc "node -e '
const fs=require('\\''fs'\\''),path=require('\\''path'\\'');
const original=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const cases=[
['\\''Auto-Fit discard'\\'','\\''tests/js/stale_statistics.test.js'\\'','\\''Auto-Fit discards'\\'',h=>h.replace(\"if ("'!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {","if (false) {")],
['"'\\''fallback discard'\\'','\\''tests/js/fit_acceptance.test.js'\\'','\\''a transport failure after the model was edited'\\'',h=>h.replace(\"if (e && e.transportFailure && ctxAtRequest "'!== null && !_sameFitKey(_startsLiveKey(), ctxAtRequest)) {","if (false) {")],
['"'\\''numeric spelling'\\'','\\''tests/js/stale_statistics.test.js'\\'','\\''an equivalent spelling'\\'',h=>h.replace(\"(a === b || _fitKeyCanon(a) === _fitKeyCanon(b))\",\"(a === b)\")],
['\\''none transition'\\'','\\''tests/js/stale_statistics.test.js'\\'','\\''Clear All (result -> none)'\\'',h=>h.replace(\"(state.fitResult || el.getAttribute('\\''data-stats-state'\\''))\",\"state.fitResult\")]
];
(async()=>{
for(const [label,file,prefix,mutate] of cases){
 const registered=[];
 const req=id=>id==='\\''node:test'\\''?{test:(name,fn)=>registered.push({name,fn})}:id==='\\''node:fs'\\''?{...fs,readFileSync:(p,...args)=>String(p).endsWith('\\''templates/index.html'\\'')?mutate(original):fs.readFileSync(p,...args)}:require(id);
 new Function('\\''require'\\'','\\''__dirname'\\'',fs.readFileSync(file,'\\''utf8'\\''))(req,path.dirname(path.resolve(file)));
 const t=registered.find(t=>t.name.startsWith(prefix));
 try { await t.fn();console.log(label+'\\'': SURVIVED'\\''); } catch(e){console.log(label+'\\'': detected ('\\''+e.message.split('\\''\\n'\\'')[0]+'\\'')'\\'');}
}
})();
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
Auto-Fit discard: detected (nothing applied over the edited model)
fallback discard: detected (no local fit over the edited model)
numeric spelling: detected (same data, same request)
none transition: detected (the shown result was cleared: back to the empty state)

exec
/bin/zsh -lc "node -e '
const fs=require('\\''fs'\\''),path=require('\\''path'\\'');
const source=fs.readFileSync('\\''tests/js/stale_statistics.test.js'\\'','\\''utf8'\\'');
const req=id=>id==='\\''node:test'\\''?{test:()=>{}}:require(id);
const {sandbox}=new Function('\\''require'\\'','\\''__dirname'\\'',source+'\\''\\nreturn {sandbox};'\\'')(req,path.resolve('\\''tests/js'\\''));
const env=sandbox();
console.log('\\''env keys'\\'',Object.keys(env));
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
env keys [ 'api', 'doc', 'state', 'env' ]

exec
/bin/zsh -lc "sed -n '74,111p' tests/js/stale_statistics.test.js; sed -n '140,175p' tests/js/stale_statistics.test.js; sed -n '6330,6355p' templates/index.html; git diff ececf7e..HEAD -- tests/js/local_lm_descent.test.js tests/js/scattered_starts.test.js tests/js/unsupported_components.test.js" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
    const _startsPanelHtml = () => '';
    const renderQuantify = (a, t) => { env.quantified = [a, t]; };
    const getROIData = () => ({ be: [1, 2, 3] });
    const getPeak = id => state.peaks.find(p => p.id === id);
    const _UNSUPPORTED_LABEL = 'not supported by the data', _UNSUPPORTED_TIP = '';
    ${src}
    return { ${[...STATE_FNS, '_applyStatDisplay', '_updateRFactorUI', 'renderResults', '_validateUncertainties'].join(', ')} };
  `)(doc, state, env);
  return { api, doc, state, env };
}

function serverResult(key) {
  return {
    chi: 12, chiReduced: 1.2346, rmse: 7.5, be: [1, 2, 3], bgIntensity: [0, 0, 0], bgSubtracted: [1, 2, 1],
    fittedY: [1, 2, 1], rFactor: { rPct: 3.21, level: 'good' },
    backendResult: { individual_peaks: [{ id: '1', params: {
      center: { value: 284.5, stderr: 0.0123, vary: true }, fwhm: { value: 1.1, stderr: 0.0456, vary: true },
      amplitude: { value: 100, stderr: 1.5, vary: true } } }] },
    startsModelKey: key,
  };
}
const PEAK = { id: 1, name: 'C-C', color: '#f00', center: 284.5, fwhm: 1.1, amplitude: 100, shape: 'GL' };

test('one accessor classifies a result against a key: none / unverified / current / stale', () => {
  const { api } = sandbox();
  assert.strictEqual(api._statsState(null, 'K'), 'none');
  assert.strictEqual(api._statsState({ chiReduced: 1 }, 'K'), 'unverified', 'saved before this unit: no key');
  assert.strictEqual(api._statsState({ startsModelKey: 'K' }, 'K'), 'current');
  assert.strictEqual(api._statsState({ startsModelKey: 'K' }, 'K2'), 'stale');
  assert.strictEqual(api._statsRecordState({ key: 'R', fitResult: { startsModelKey: 'R' } }), 'current', 'a record is judged against ITS key');
  assert.strictEqual(api._statsRecordState({ key: 'R2', fitResult: { startsModelKey: 'R' } }), 'stale');
  assert.deepStrictEqual(api._statsSaveFields('current'), {});
  assert.strictEqual(api._statsSaveFields('stale').statisticsState, 'stale');
  assert.match(api._statsSaveFields('stale').statisticsNote, /previous model/);
  assert.strictEqual(api._statsSaveFields('unverified').statisticsState, 'unverified');
});

test('the key is the step (b) key: F1 adds no second binding mechanism and no new key field', () => {

test('Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma', () => {
  const { api, doc, state } = sandbox({ liveKey: 'EDITED' });
  state.peaks = [{ ...PEAK, center: 285.0 }];
  state.fitResult = serverResult('K1');
  api.renderResults();
  const h = doc.els['results-area'].innerHTML;
  assert.strictEqual(doc.els['results-area'].getAttribute('data-stats-state'), 'stale');
  assert.match(h, /stats-stale-note/);
  assert.match(h, /belong to the previous model/);
  assert.ok(!/1\.23/.test(h), 'no chi-square value');
  assert.ok(!/>7\.5</.test(h), 'no RMSE value');
  assert.ok(!/R-factor:/.test(h), 'no R panel');
  assert.ok(!/±/.test(h), 'no sigma');
  assert.match(h, /285\.000 eV/, 'the table shows the current model');
  // header + status bar
  assert.match(doc.els['fit-quality'].textContent, /model changed/);
  assert.ok(!/1\.2/.test(doc.els['fit-quality'].textContent));
  assert.strictEqual(doc.els['sb-chi'].textContent, '—');
  assert.match(doc.els['fit-quality'].getAttribute('data-xps-tip'), /previous model/);
  // uncertainty panel judges no per-parameter rule on the previous model's sigma
  assert.deepStrictEqual(api._validateUncertainties(), { warnings: [], info: [] });
});

test('Results panel, unverified (older save, no key): values shown with a plain note', () => {
  const { api, doc, state } = sandbox({ liveKey: 'K1' });
  state.peaks = [{ ...PEAK }];
  const fr = serverResult('K1'); delete fr.startsModelKey;
  state.fitResult = fr;
  api.renderResults();
  const h = doc.els['results-area'].innerHTML;
  assert.strictEqual(doc.els['results-area'].getAttribute('data-stats-state'), 'unverified');
  assert.match(h, /stats-unverified-note/);
  assert.match(h, /1\.235/);
  assert.match(h, /± 0\.012/);
  assert.match(doc.els['fit-quality'].getAttribute('data-xps-tip'), /cannot be confirmed/);
      <div class="field">
        <label data-xps-tip="Gaussian full width at half maximum in eV. Represents instrumental and phonon broadening. Typical values: 0.2-1.5 eV depending on your spectrometer pass energy.">m Gauss FWHM (eV)
          ${!isLinked ? `<button class="lock-btn${p.fixLaM ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixLaM',this)" title="${p.fixLaM ? 'Unlock' : 'Lock'} during fitting">${p.fixLaM ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
        </label>
        <input type="number" value="${p.laM.toFixed(3)}" step="0.01" min="0.05" max="4.0"
          oninput="updatePeakParam(${p.id},'laM',parseFloat(this.value))">
      </div>
    `;
  } else if (p.shape === 'LACX') {
    return `
      <div style="font-size:10px;color:var(--text3);margin-bottom:6px">
        True CasaXPS LA — &alpha;/&beta; are exponents (BE convention: &alpha; applies to high-BE side)
      </div>
      <div class="field-row">
        <div class="field">
          <label data-xps-tip="High-BE-side exponent. CasaXPS-equivalent α. Smaller α extends the high-BE tail. Default 1.0 (symmetric Lorentzian). Bounds 0.1–5.0.">&alpha; (high-BE exp)
            ${!isLinked ? `<button class="lock-btn${p.fixCaAlpha ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixCaAlpha',this)" title="${p.fixCaAlpha ? 'Unlock' : 'Lock'} during fitting">${p.fixCaAlpha ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
          </label>
          <input type="number" value="${(p.caAlpha ?? 1.0).toFixed(3)}" step="0.05" min="0.1" max="5.0"
            oninput="updatePeakParam(${p.id},'caAlpha',parseFloat(this.value))">
        </div>
        <div class="field">
          <label data-xps-tip="Low-BE-side exponent. CasaXPS-equivalent β. Default 1.0 (symmetric). Bounds 0.1–5.0.">&beta; (low-BE exp)
            ${!isLinked ? `<button class="lock-btn${p.fixCaBeta ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixCaBeta',this)" title="${p.fixCaBeta ? 'Unlock' : 'Lock'} during fitting">${p.fixCaBeta ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
          </label>
          <input type="number" value="${(p.caBeta ?? 1.0).toFixed(3)}" step="0.05" min="0.1" max="5.0"
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-O3NVZPS8' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-9OnYQk3h' (errno=Operation not permitted)
diff --git a/tests/js/local_lm_descent.test.js b/tests/js/local_lm_descent.test.js
index 342ad9f..37c2127 100644
--- a/tests/js/local_lm_descent.test.js
+++ b/tests/js/local_lm_descent.test.js
@@ -40,7 +40,7 @@ const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'a
   'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
   'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
   '_computeRFactor', '_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel', '_governingProvenance', '_localFitCaveat', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay', '_updateLocalModelBanner',
-  '_componentSupportCore', '_supportRootOf', '_applySupportVerdicts', '_statsState', '_statsLiveState'];
+  '_componentSupportCore', '_supportRootOf', '_applySupportVerdicts', '_fitKeyCanon', '_sameFitKey', '_statsState', '_statsLiveState'];
 const CAVEAT_CONST = (html.match(/^const (_LOCAL_FIT_CAVEAT\w*|_STATS_\w+_NOTE) = .*$/mg) || []).join('\n');
 
 // One isolated environment per test: a fresh `state`, a stub DOM, and the
diff --git a/tests/js/scattered_starts.test.js b/tests/js/scattered_starts.test.js
index ba7256b..cb52b9e 100644
--- a/tests/js/scattered_starts.test.js
+++ b/tests/js/scattered_starts.test.js
@@ -30,7 +30,7 @@ function extractFn(name) {
 }
 const constLine = name => { const l = lines.find(x => x.startsWith('const ' + name)); assert.ok(l, name); return l; };
 
-const FNS = ['_isUnsupported', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_startsRecordKey', '_startsIfCurrent', '_dropStaleAltPreview',
+const FNS = ['_fitKeyCanon', '_sameFitKey', '_isUnsupported', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_startsRecordKey', '_startsIfCurrent', '_dropStaleAltPreview',
   '_startsChosenText', '_startsForSave', '_startsSummaryText', '_startsPeakName',
   '_startsShiftColour', '_startsEv', '_startsShiftHtml', '_startsPanelHtml', '_altPeaks', '_currentAlternative',
   'previewAlternative', 'useAlternative', '_applyBackendParams'];
@@ -257,9 +257,9 @@ test('wiring: the trigger is decided with the other request inputs, BEFORE the f
   assert.match(runFit, /const startModel = opts\.startPeaks \|\| state\.peaks;\n\s*const peakSpecs = startModel\.map\(peakToBackendSpec\);/);
   assert.match(runFit, /startsModelKey: _startsLiveKey\(\),/);
   assert.ok(runFit.indexOf('applyBackendResult(backendResult);') < runFit.indexOf('startsModelKey: _startsLiveKey()'), 'the key describes the model AFTER the result was applied');
-  const captured = runFit.indexOf('const ctxAtRequest = _startsLiveKey();');
+  const captured = runFit.indexOf('ctxAtRequest = _startsLiveKey();');
   assert.ok(captured > 0 && captured < runFit.indexOf('await uploadToBackend('), 'context captured before the first await');
-  assert.ok(runFit.indexOf('if (_startsLiveKey() !== ctxAtRequest)') < runFit.indexOf('applyBackendResult(backendResult);'), 'and checked before anything is applied');
+  assert.ok(runFit.indexOf('if (!_sameFitKey(_startsLiveKey(), ctxAtRequest))') > 0 && runFit.indexOf('if (!_sameFitKey(_startsLiveKey(), ctxAtRequest))') < runFit.indexOf('applyBackendResult(backendResult);'), 'and checked before anything is applied');
   assert.match(runFit, /chosenAlternative: opts\.chosenAlternative \|\| null/);
   assert.match(extractFn('renderResults'), /_startsPanelHtml\(state\.fitResult\)/);
   assert.doesNotMatch(extractFn('_invalidateFittedY'), /starts/, 'validity is by key comparison: a rename (which calls this) must not delete evidence');
diff --git a/tests/js/unsupported_components.test.js b/tests/js/unsupported_components.test.js
index 5de224f..2a0eb9e 100644
--- a/tests/js/unsupported_components.test.js
+++ b/tests/js/unsupported_components.test.js
@@ -30,7 +30,7 @@ function extractFn(name) {
 const constLine = name => { const l = lines.find(x => x.startsWith('const ' + name)); assert.ok(l, name); return l; };
 const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
 
-const CORE = ['_componentSupportCore', '_componentSupportFromResponse', '_supportRootOf', '_applySupportVerdicts', '_applySupport', '_isUnsupported', '_currentSupport', '_restampSupport', '_unsupportedBadge'];
+const CORE = ['_componentSupportCore', '_componentSupportFromResponse', '_supportRootOf', '_applySupportVerdicts', '_applySupport', '_fitKeyCanon', '_sameFitKey', '_isUnsupported', '_currentSupport', '_restampSupport', '_unsupportedBadge'];
 function core() {
   const src = [constLine('_SUPPORT_MIN_F'), constLine('_UNSUPPORTED_LABEL'), constLine('_UNSUPPORTED_TIP'), ...CORE.map(extractFn)].join('\n');
   return new Function('_escAttr', '_startsLiveKey', 'state', src + '\nreturn { ' + CORE.join(', ') + ' };')(esc, () => 'KEY', { peaks: [] });
@@ -311,9 +311,9 @@ test('a key change re-renders every consumer of the verdict — each compared wi
   const calls = [];
   const state = { peaks: [{ id: 2, support: { supported: false, fitKey: 'OLD' } }], fitResult: {}, chart: { data: { datasets: [{ _peakId: 2, _unsupported: true }] } } };
   const document = { querySelectorAll: sel => sel.includes('peak-list') ? [] : [{ getAttribute: () => '2' }], querySelector: () => null };
-  const fn = new Function('state', 'document', '_startsLiveKey', '_isUnsupported', '_historyPreview', '_dropStaleAltPreview', '_patchPeakCardsForSupport', 'renderResults', 'updatePlot', '_startsPanelHtml',
+  const fn = new Function('state', 'document', '_startsLiveKey', '_isUnsupported', '_historyPreview', '_dropStaleAltPreview', '_patchPeakCardsForSupport', 'renderResults', 'updatePlot', '_startsPanelHtml', '_refreshStatsState',
     src + '\nreturn _refreshStartsEvidence;')(state, document, () => 'NEW', (p, k) => p.support.supported === false && p.support.fitKey === k, null, () => {},
-    () => calls.push('sidebar'), () => calls.push('results'), () => calls.push('plot'), () => '');
+    () => calls.push('sidebar'), () => calls.push('results'), () => calls.push('plot'), () => '', () => {});   // F1's refresh: stale_statistics.test.js
   fn(false);
   assert.deepStrictEqual(calls, ['results', 'plot'], 'sidebar already clean; Results and the chart still stale');
   for (const fn of ['toggleLock', 'toggleAllLocks']) assert.match(extractFn(fn), /_refreshStartsEvidence\(true\);/, fn);

exec
/bin/zsh -lc "node -e '
const fs=require('\\''fs'\\''),path=require('\\''path'\\'');
const src=fs.readFileSync('\\''tests/js/stale_statistics.test.js'\\'','\\''utf8'\\'');
const req=id=>id==='\\''node:test'\\''?{test:()=>{}}:require(id);
const {sandbox,serverResult,PEAK}=new Function('\\''require'\\'','\\''__dirname'\\'',src+'\\''\\nreturn {sandbox,serverResult,PEAK};'\\'')(req,path.resolve('\\''tests/js'\\''));
const {api,doc,state}=sandbox();
state.fitResult=serverResult('\\''K1'\\'');state.peaks=[{...PEAK}];
api.renderResults();
const original=doc.getElementById.bind(doc);
doc.getElementById=id=>original(id)||(doc.els[id]={textContent:'\\'''\\'',value:'\\'''\\'',style:{}});
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const start=html.indexOf('\\''  closeTab(id) {'\\''), end=html.indexOf('\\''  // ── Folder upload'\\'',start);
const method=html.slice(start,end).trim();
const deps={state,document:doc,_updateUndoButtons:()=>{},renderPeakList:()=>{},renderEmptyChart:()=>{},_updateRFactorUI:api._updateRFactorUI,_updateROIDisplay:()=>{}};
const manager=new Function(...Object.keys(deps),'\\''return {'\\''+method+'\\''};'\\'')(...Object.values(deps));
Object.assign(manager,{tabs:[{id:'\\''A'\\'',name:'\\''A'\\''}],activeId:'\\''A'\\'',renderTabBar(){},_updateSurveyPanel(){},_updateCCVerifiedUI(){}});
manager.closeTab('\\''A'\\'');
console.log({actualState:api._statsLiveState(),renderedState:doc.els['\\''results-area'\\''].getAttribute('\\''data-stats-state'\\''),stillShowsChi:doc.els['\\''results-area'\\''].innerHTML.includes('\\''1.235'\\''),header:doc.els['\\''fit-quality'\\''].textContent,statusChi:doc.els['\\''sb-chi'\\''].textContent});
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
{
  actualState: 'none',
  renderedState: 'current',
  stillShowsChi: true,
  header: 'χ²ᵣ = 1.23',
  statusChi: '1.235'
}

codex
Both reproductions confirmed failures. A request sent with endpoint averaging 30 was accepted after the field changed to `3e1` (read as 3). Closing the last fitted tab also left χ² and the Results table visible, although the live state was `none`.

The targeted suite passed 139 tests; one Python parity test could not run because the read-only sandbox has no writable temporary directory. In-memory mutation checks also confirmed that each of the four new behavioural tests fails when its corresponding fix is disabled.
exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '3300,3330p'; nl -ba templates/index.html | sed -n '7942,7952p'; git status --short" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
  3300	    if (this.tabs.length === 0) {
  3301	      this.activeId = null;
  3302	      _updateUndoButtons();
  3303	      if (typeof _historyPreview !== 'undefined') _historyPreview = null;
  3304	      state.rawBE = []; state.rawIntensity = [];
  3305	      state.peaks = []; state.fitResult = null;
  3306	      state.ccShift = 0; state.nextId = 1;
  3307	      document.getElementById('data-info').textContent = 'no data';
  3308	      const _cl = document.getElementById('spec-combo-label');
  3309	      if (_cl) _cl.textContent = 'no data';
  3310	      document.getElementById('sb-pts').textContent = '\u2014';
  3311	      document.getElementById('sb-range').textContent = '\u2014';
  3312	      renderPeakList();
  3313	      renderEmptyChart();
  3314	      this.renderTabBar();
  3315	      this._updateSurveyPanel();
  3316	      this._updateCCVerifiedUI(true);
  3317	      _updateRFactorUI(null);
  3318	      _updateROIDisplay(null);
  3319	      const notesEl = document.getElementById('spectrum-notes');
  3320	      if (notesEl) notesEl.value = '';
  3321	      return;
  3322	    }
  3323	
  3324	    if (this.activeId === id) {
  3325	      const nextIdx = Math.min(idx, this.tabs.length - 1);
  3326	      this.activeId = null; // force re-activate
  3327	      this.activateTab(this.tabs[nextIdx].id);
  3328	    } else {
  3329	      this.renderTabBar();
  3330	    }
  7942	    // before the first await (a tab switch during the upload must not turn it off)
  7943	    const nStarts = _startsUnlinkedCount(startModel) >= 2 ? _STARTS_N : 0;
  7944	    // the live model and its fit context as the student pressed the button: a
  7945	    // result must not be written over a model that was edited while it ran
  7946	    ctxAtRequest = _startsLiveKey();
  7947	    const fitMethod = document.getElementById('fit-method').value;
  7948	    const epAvgVal = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
  7949	    const bgPayload = { method: bgType, start_idx: bgWin.i0, end_idx: bgWin.i1 + 1, endpoint_avg: epAvgVal };
  7950	    if (bgType === 'manual') {
  7951	      // Anchors are stored in corrected-BE space, same frame as the uploaded
  7952	      // session data; backend expects [x, y] pairs.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-AEUeO7wy' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-JO8iGVsF' (errno=Operation not permitted)
?? docs/autofit/codex/f1_stale_statistics_r2_verdict_runA.md
?? docs/autofit/codex/f1_stale_statistics_r2_verdict_runB.md

codex
1. **MAJOR — Canonicalisation equates different fit settings.** [templates/index.html:7645](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:7645)  
   `_fitKeyCanon` uses `Number`, while endpoint averaging and Shirley iterations use `parseInt`. Thus `30` and `3e1` compare equal but select **30 versus 3**. After fitting with endpoint averaging 30, entering `3e1` incorrectly leaves statistics current. Reproduced through the actual `runFit`: request averaging **30**, live averaging **3**, response **applied**, status **“Fit complete (lmfit)”**. This also undermines the new mid-flight discard guards. Canonicalisation must respect each field’s reader.

2. **MAJOR — Closing the last tab still leaves its statistics visible.** [templates/index.html:3305](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:3305)  
   Fit the only open spectrum, display Results, then close its tab. This branch clears `fitResult` but calls neither `renderResults` nor the new refresh path. Reproduced: live state **`none`**, Results state **`current`**, header **χ²ᵣ = 1.23**, status **1.235**, and the previous Results table retained. This pre-existing lifecycle gap remains uncovered by the Clear All fix.

Validation: **139/140 targeted tests passed**; the Python parity test was blocked by the sandbox’s lack of writable temporary storage. In-memory mutation checks confirmed that the new Auto-Fit discard, fallback discard, numeric-spelling and Clear All tests each fail without their corresponding fix. Browser tests were not run. No files changed.

**VERDICT: NO-GO**
tokens used
89,036
1. **MAJOR — Canonicalisation equates different fit settings.** [templates/index.html:7645](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:7645)  
   `_fitKeyCanon` uses `Number`, while endpoint averaging and Shirley iterations use `parseInt`. Thus `30` and `3e1` compare equal but select **30 versus 3**. After fitting with endpoint averaging 30, entering `3e1` incorrectly leaves statistics current. Reproduced through the actual `runFit`: request averaging **30**, live averaging **3**, response **applied**, status **“Fit complete (lmfit)”**. This also undermines the new mid-flight discard guards. Canonicalisation must respect each field’s reader.

2. **MAJOR — Closing the last tab still leaves its statistics visible.** [templates/index.html:3305](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:3305)  
   Fit the only open spectrum, display Results, then close its tab. This branch clears `fitResult` but calls neither `renderResults` nor the new refresh path. Reproduced: live state **`none`**, Results state **`current`**, header **χ²ᵣ = 1.23**, status **1.235**, and the previous Results table retained. This pre-existing lifecycle gap remains uncovered by the Clear All fix.

Validation: **139/140 targeted tests passed**; the Python parity test was blocked by the sandbox’s lack of writable temporary storage. In-memory mutation checks confirmed that the new Auto-Fit discard, fallback discard, numeric-spelling and Clear All tests each fail without their corresponding fix. Browser tests were not run. No files changed.

**VERDICT: NO-GO**
