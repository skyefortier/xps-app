OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0dc5f-1e72-79a3-8439-7807b44bba68
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
I’ll read the round-1 findings, trace the changed paths, and run focused checks where possible. I’ll keep the review read-only and finish with a verdict.
exec
/bin/zsh -lc "pwd; rg --files -g AGENTS.md -g '*stale_statistics*' -g '*fit_acceptance*'; git status --short; git log -3 --oneline; git diff --stat ececf7e..HEAD" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 11ms:
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
/bin/zsh -lc 'for p in /AGENTS.md /Users/AGENTS.md /Users/skyefortier/AGENTS.md /Users/skyefortier/xps-app/AGENTS.md /Users/skyefortier/xps-app/.claude/AGENTS.md /Users/skyefortier/xps-app/.claude/worktrees/AGENTS.md; do if test -f "$p"; then cat "$p"; fi; done
cat docs/autofit/codex/f1_stale_statistics_review_prompt.txt
cat docs/autofit/plans/2026-09-25-f1-stale-statistics.md
 git diff ececf7e..HEAD -- templates/index.html tests/js/stale_statistics.test.js tests/js/fit_acceptance.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
Review unit F1 (stale statistics after an edit): branch fix-stale-statistics, git diff main..HEAD (templates/index.html, tests/js/stale_statistics.test.js, tests/js/fit_acceptance.test.js, tests/js/local_lm_descent.test.js, tests/js/unsupported_components.test.js, tests/test_browser_find_peaks_full_window.py, CLAUDE.md, docs/superpowers/plans/2026-09-25-f1-stale-statistics.md). Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

OWNER'S BRIEF (verbatim): "Reuse step (b)'s fit key (model + background/ROI/anchors/charge shift). When the current key does not match the key the statistics came from, mark chi2, sigma and R stale in the Results panel, CSV, XLSX, TSV, figure export and saves - say plainly they belong to the previous model, or omit them. Do not build a second binding mechanism; this is a down payment on the sealed fit record and must be absorbable by it. Enumerate every consumer of the statistics first."

Source finding: sweep H1 (docs/findings/2026-09-25-fail-open-guards-sweep.md on branch sweep-fail-open-guards): after an edit, a Find Peaks apply in the default window, or an undo, the previous fit's chi2, sigma, R and fittedY stayed on screen, in exports and in saves beside a model they do not describe.

THE CREATORS AND CONSUMERS TABLES (plan sections 2-3, verbatim):

## 2. Creators of a fit result

| creator | stamps the key today | after |
|---|---|---|
| `runFit` (server) | yes, after `applyBackendResult` | unchanged |
| `runFitLocal` (fallback; Batch Fit targets) | no | yes, after the values are committed |
| `applyAutoFitResult` | no; and it locks every centre and refines the charge shift AFTER applying (so its verdicts are re-stamped by `_restampSupport`) | stamped at creation AND re-stamped by `_restampSupport` (those changes are part of its result) |
| `_loadSpectrumFile` | restores a saved `startsModelKey` if present | unchanged (an older file has none → `unverified`) |
| project load (`fromJSON` / tab records) | the saved `fitResult` object, key included if present | unchanged |
| `_historyRestoreSnap`, `_autoFitRestore` | restore an older result WITH its key | unchanged — the comparison judges it |
| `applyFindPeaks` (default mode), undo / redo | keep the old result over a replaced model | unchanged — the key comparison now makes that result `stale` (CLAUDE.md lists these as "not covered"; they are covered here for the statistics) |
| `clearAllPeaks`, `closeTab`, Batch Fit's copy, `.fit.json` import | set `fitResult = null` | unchanged |

## 3. Consumers of χ², σ, R (and the stored fitted curve)

| # | consumer | reads | `stale` | `unverified` |
|---|---|---|---|---|
| 1 | Results panel (`renderResults`): statistic card, RMSE card, R panel, σ in the peak table | `chiReduced`, `rmse`, `rFactor`, `backendResult` σ | amber banner: the statistics belong to the previous model, Run Fit; statistic, RMSE and R shown as "—"; σ omitted | a plain note; values shown |
| 2 | Header statistic + status bar (`_applyStatDisplay`, `_fitStatusText`, caption) | `chiReduced` | "χ²ᵣ — (model changed)"; status value "—"; tooltip says why | value shown; tooltip adds the note |
| 3 | Status-bar R (`_updateRFactorUI`) | `rFactor` | cleared, tooltip says why | shown |
| 4 | Uncertainty panel (`_validateUncertainties`) | `backendResult` σ, bounds | nothing: no per-parameter rule is judged on the previous model's σ (the Results banner is the one line; the panel's boxes are titled "Uncertainty Warnings" / "Locked Parameters", neither fits) | unchanged |
| 5 | CSV / XLSX (`exportFitTable`) | `chiReduced`, σ | statistic line omitted, σ cells empty, a WARNING line naming why | values kept, a NOTE line |
| 6 | TSV (`exportResults`) | no statistics; Model / Residual computed from the current peaks | a NOTE: those columns are the edited, unfitted model | unchanged |
| 7 | Publication figure (`_doPublicationExport`) | `chiReduced` | χ² annotation omitted | "(unverified)" appended |
| 8 | `_doSaveSpectrum`, `_doSaveFit` | `chi`, `chiReduced`, `rmse`, key, `fittedY` | key saved as always, so a reload judges the result again (a stale save reloads stale); `statisticsState: 'stale'` and a plain `statisticsNote` added; the spectrum file's `fittedY` is the current model + background (it then matches the file's `residuals`, which were always the current model) | `statisticsState: 'unverified'` |
| 9 | `_doSaveProject` (per tab) | the tab's `fitResult` | the same two fields, judged against the RECORD's key | the same |
| 10 | History snapshots (`_autoSnapshot`, `_renderHistoryList`) | `chiReduced`, `rFactor` at snapshot | NOT a consumer: a snapshot is taken only by the three creators, right after a result is applied, so peaks, result and key are one state; restoring one brings back its key and the comparison judges it | — |
| 11 | Chart (`updatePlot`, stored `fittedY` → envelope and residuals) | `fittedY` | not used (edits already null it; Find Peaks apply and undo did not): the envelope is composed from the current peaks | used |
| 12 | Stack tabs (`_buildEntryRenderData` Path A) | the source's `fittedY` | not used; Path A2/B (from the source's peaks) | used |
| 13 | Scattered-starts panel, support verdicts | already keyed by the same key | unchanged | unchanged |
| 14 | Batch Fit summary | the fit's own return value (fresh) | not a consumer of a stored result | — |
| 15 | Quantify | areas from the current peaks, no statistics | not a consumer | — |

Refresh: when the live key changes the Results panel re-renders if its
rendered state differs (it carries `data-stats-state`), and the header,
status bar and R are re-applied — from `updatePlot`, next to
`_refreshStartsEvidence`, so every edit path that repaints reaches it.

Residual, logged for the sealed fit record: each peak carries
`p._backendParams` (the server's per-parameter value, σ and bounds of the
LAST fit), persisted whole with the peak. It is not displayed anywhere
(the σ above come from `fitResult.backendResult`), but it rides in a stale
save; the save's `statisticsState` / `statisticsNote` cover the file.
`autofit/parity.py` reads `_backendParams.gl_ratio.value` from saved peaks,
so it is not stripped here — the sealed record owns per-parameter results.


TRY TO BREAK
a. Completeness: grep every read of chiReduced, chi, rmse, rFactor, backendResult (sigma, bounds), fittedY, _buildStderrMap and startsModelKey in templates/index.html (and static/js/*) - is any consumer that SHOWS, EXPORTS or SAVES a statistic missing from the table or unguarded? (e.g. the history list, the Batch Fit summary, notifications, the stack legend, the scattered-starts panel, the local-model banner, a clipboard/report path, the Quantify tab, _computeRFactor recomputation on tab activation.)
b. Creators: is there any path that creates or REPLACES state.fitResult (or a tab record's fitResult) without stamping the key, or stamps it BEFORE the model/context is final (Auto-Fit's centre lock + charge refinement; runFit's alternative adoption; runFitLocal's commit; Batch Fit's target writes to a record, not state)? A result stamped too early reads stale immediately; one stamped too late (after an edit) reads current wrongly.
c. False stale: anything that changes the live key WITHOUT changing the model the fit saw - _captureUI string formatting after a tab switch or project reload (the browser check shows a project round trip stays current - try other UI states: manual background with anchors, Tougaard, a charge shift, an ROI typed as '280' vs '280.0', endpoint avg), undo after a fit, a name/colour edit, ccShift float noise, the Find Peaks full-window apply path.
d. False current: an edit that changes what the fit would compute but NOT the key (a field missing from _STARTS_MODEL_FIELDS / _STARTS_UI_FIELDS that the request reads - e.g. the fit method, a bound field, amplitude min, LA/DS+G shape switch leftovers, 'visible', the ROI when getROIData clamps) - is the key's coverage enough for the STATISTICS (it was designed for the starts evidence)?
e. Refresh: the visible state after each edit path - peak param edit, lock toggle, Lock All, add/delete peak, background controls, ROI fields, charge correction, manual anchors, undo/redo, history restore, tab switch, stack tab active, Find Peaks apply both modes, clearAllPeaks. Does every path end with header, status bar, R and Results agreeing? Any path that re-renders Results while an RSF input in Quantify is being typed (renderResults re-renders Quantify)?
f. Saves and reloads: the three saves (_doSaveFit, _doSaveSpectrum, _doSaveProject), their loaders; a stale save reloads stale, a current one current; older files (no key) unverified - and is 'unverified' shown honestly without hiding values on every committed project? Is the spectrum save's fittedY change (current model when stale) safe for its loader and for autofit/* readers of .spec.json?
g. Absorbable by the sealed fit record: is anything here a second binding mechanism (a new key, a hand invalidation, a flag set on edit)?
h. Tests: are the new assertions real (not vacuous) - the stubbed sandboxes, the source-regex checks - and do the edited existing tests still test what they tested?
i. Docs vs code (CLAUDE.md, plan).

Finish with VERDICT: GO or VERDICT: NO-GO.cat: docs/autofit/plans/2026-09-25-f1-stale-statistics.md: No such file or directory
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-yXYAwW1r' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-1hUITy44' (errno=Operation not permitted)
diff --git a/templates/index.html b/templates/index.html
index 9f032ae..e1f08fc 100644
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
@@ -7485,6 +7487,9 @@ async function runAutoFitC1sGraphite() {
     // other request inputs, before the first await (a tab switch during the
     // upload must not send another tab's id).
     const anchorId = String((state.peaks.find(p => p.name === 'Graphite') || state.peaks[0]).id);
+    // the model and its fit context as sent (F1, Codex round 1): a result must
+    // not be applied, and stamped current, over a model edited while it ran
+    const ctxAtRequest = _startsLiveKey();
     // Build peak specs and overlay the per-peak bounds we attached in buildAutoFitModel.
     const peakSpecs = state.peaks.map(p => {
       const spec = peakToBackendSpec(p);
@@ -7529,6 +7534,12 @@ async function runAutoFitC1sGraphite() {
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
 
@@ -7620,6 +7631,25 @@ function _startsModelKey(peaks, ui, ccShift, anchors) {
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
@@ -7630,7 +7660,7 @@ function _startsRecordKey(t) { return _startsModelKey(t.peaks, t.ui, t.ccShift,
 // The starts evidence of `fr` if it still describes the fit whose key is `key`, else null.
 function _startsIfCurrent(fr, key) {
   const st = fr && fr.starts;
-  if (!st || !fr.startsModelKey || fr.startsModelKey !== key) return null;
+  if (!st || !fr.startsModelKey || !_sameFitKey(fr.startsModelKey, key)) return null;
   return st;
 }
 // Unit F1 (2026-09-25): the fit STATISTICS (chi-square, sigma, R-factor, RMSE
@@ -7647,7 +7677,7 @@ function _startsIfCurrent(fr, key) {
 function _statsState(fr, key) {
   if (!fr) return 'none';
   if (!fr.startsModelKey) return 'unverified';
-  return fr.startsModelKey === key ? 'current' : 'stale';
+  return _sameFitKey(fr.startsModelKey, key) ? 'current' : 'stale';
 }
 function _statsLiveState() { return _statsState(state.fitResult, _startsLiveKey()); }
 // A record's result judged against the RECORD's key (project save, stack tabs).
@@ -7665,7 +7695,8 @@ function _statsSaveFields(st) {
 function _refreshStatsState() {
   const st = _statsLiveState();
   const el = document.getElementById('results-area');
-  if (el && state.fitResult && el.getAttribute('data-stats-state') !== st && typeof renderResults === 'function') renderResults();   // applies the header / status bar too
+  // 'none' too: Clear All nulls the result and only repaints (Codex round 1)
+  if (el && el.getAttribute('data-stats-state') !== st && (state.fitResult || el.getAttribute('data-stats-state')) && typeof renderResults === 'function') renderResults();   // applies the header / status bar too
   else _applyStatDisplay(state.fitResult);
   if (typeof _updateRFactorUI === 'function') _updateRFactorUI(state.fitResult ? state.fitResult.rFactor : null);
 }
@@ -7675,6 +7706,9 @@ function _refreshStatsState() {
 // control): take a stale alternative overlay off the chart and bring the
 // VISIBLE panel up to date (counts -> "the model has changed since this fit").
 function _refreshStartsEvidence(repaint, fromPlot) {
+  // F1: chi-square / sigma / R follow the same key, from every caller (lock
+  // toggles and Lock All reach here without a repaint; Codex round 1)
+  _refreshStatsState();
   const hadAlt = !!(_historyPreview && typeof _historyPreview.snapId === 'string' && _historyPreview.snapId.startsWith('alt:'));
   _dropStaleAltPreview();
   if (repaint && hadAlt && !_historyPreview && typeof updatePlot === 'function') updatePlot();
@@ -7889,6 +7923,7 @@ async function runFit(opts = {}) {
 
   // Try Flask backend first
   let backendResult = null;
+  let ctxAtRequest = null;   // set with the other request inputs; read again by the local fallback
   try {
     const bgType  = document.getElementById('bg-type').value;
     const bgStart = parseFloat(document.getElementById('bg-start').value);
@@ -7908,7 +7943,7 @@ async function runFit(opts = {}) {
     const nStarts = _startsUnlinkedCount(startModel) >= 2 ? _STARTS_N : 0;
     // the live model and its fit context as the student pressed the button: a
     // result must not be written over a model that was edited while it ran
-    const ctxAtRequest = _startsLiveKey();
+    ctxAtRequest = _startsLiveKey();
     const fitMethod = document.getElementById('fit-method').value;
     const epAvgVal = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
     const bgPayload = { method: bgType, start_idx: bgWin.i0, end_idx: bgWin.i1 + 1, endpoint_avg: epAvgVal };
@@ -7984,7 +8019,7 @@ async function runFit(opts = {}) {
     // The peak controls stay editable while the fit runs. A result computed for
     // the model as it was must not be applied over an edited one (a newly locked
     // centre would keep its edited value under the server's statistics).
-    if (_startsLiveKey() !== ctxAtRequest) {
+    if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
       _hideFitSpinner();
       document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
       notify('Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.', 'amber', true);
@@ -8033,6 +8068,14 @@ async function runFit(opts = {}) {
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
@@ -9654,7 +9697,6 @@ function updatePlot() {
     });
   }
 
-  _refreshStatsState();                  // F1: chi-square / sigma / R follow the same key
   _refreshStartsEvidence(false, true);   // background / ROI controls only repaint the chart: keep the visible consumers honest (fromPlot: the chart itself is being rebuilt)
   _refreshRoiAndCentreWarnings();         // ROI past the data / centre outside the data: warn, never move
   // History snapshot preview overlay (cyan dashed, drawn on top)
@@ -10314,6 +10356,7 @@ function _doSaveSpectrum() {
     chi: state.fitResult.chi,
     chiReduced: state.fitResult.chiReduced,
     rmse: state.fitResult.rmse,
+    rFactor: state.fitResult.rFactor || null,   // F1: the fit's own R (restored only while current)
     // Engine identity travels with the statistic so a reloaded local-engine
     // result is never relabelled as chi-square (unit A0).
     engine: state.fitResult.engine || null,
@@ -10402,6 +10445,7 @@ async function _doSaveProject() {
       fitResult: t.fitResult ? {
         chi: t.fitResult.chi, chiReduced: t.fitResult.chiReduced,
         rmse: t.fitResult.rmse, fittedY: t.fitResult.fittedY || null,
+        rFactor: t.fitResult.rFactor || null,   // F1: the fit's own R, not one recomputed from edited peaks on reload
         // Frozen fit grid: persisted so post-load updatePlot() renders the
         // recorded fit (haveFit path) instead of recomputing background and
         // residuals from current settings. Absent in older saves — loaders
@@ -10640,7 +10684,10 @@ function _loadSpectrumFile(data, sessionFile) {
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
diff --git a/tests/js/fit_acceptance.test.js b/tests/js/fit_acceptance.test.js
index 995460c..44acd50 100644
--- a/tests/js/fit_acceptance.test.js
+++ b/tests/js/fit_acceptance.test.js
@@ -41,7 +41,7 @@ function makeEnv({ fetchImpl, uploadImpl, specImpl, ownerActive }) {
     peaks: [{ id: 1, name: 'p', shape: 'Gaussian', center: 285, fwhm: 1.2, amplitude: 50, glMix: 50, asymmetry: 0 }] };
   const owner = { id: 7 };
   const calls = { notify: [], local: 0, applied: 0 };
-  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_startsIfCurrent'].map(extractFn).join('\n');
+  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n');
   const factory = new Function('document', 'state', 'fetch', 'uploadToBackend', 'notify', 'pushUndo', '_showFitSpinner', '_hideFitSpinner',
     '_opOwner', '_ownerActive', 'getROIData', 'computeBackground', 'peakToBackendSpec', '_getManualAnchors', 'applyBackendResult',
     '_computeRFactor', '_CHISQ_TOOLTIP', '_updateRFactorUI', '_updateROIDisplay', 'renderPeakList', 'updatePlot', 'renderResults',
@@ -95,7 +95,7 @@ test('a transport failure whose local fallback does NOT converge shows no "local
   failing.calls.local = 0;
   // rebuild with a failing runFitLocal
   const dom = failing.dom;
-  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_startsIfCurrent'].map(extractFn).join('\n');
+  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n');
   const noop = () => {};
   const owner = { id: 1 };
   const state = failing.state;
@@ -260,7 +260,7 @@ test('project save derives the designation from the objective for an older local
   const src = html.slice(start, end) + ';';
   const constLine = html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n');
   const fieldsAt = lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS'));
-  const helpers = lines.slice(fieldsAt, lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\n' + ['_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_localFitCaveat', '_startsForSave', '_startsIfCurrent', '_startsModelKey', '_startsRecordKey', '_statsState', '_statsRecordState', '_statsNote', '_statsSaveFields'].map(extractFn).join('\n');
+  const helpers = lines.slice(fieldsAt, lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\n' + ['_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_localFitCaveat', '_startsForSave', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent', '_startsModelKey', '_startsRecordKey', '_statsState', '_statsRecordState', '_statsNote', '_statsSaveFields'].map(extractFn).join('\n');
   const statsConsts = html.match(/^const _STATS_\w+_NOTE = .*$/mg).join('\n');
   const build = new Function('RefCore', '_roundBE', '_roundIntensity', constLine + '\n' + statsConsts + '\n' + helpers + '\n' + src + '\nreturn buildTabData;')(
     { serializeRefOverlays: () => null }, a => a, a => a);
@@ -626,3 +626,22 @@ test('a model edited WHILE the fit runs does not receive the result (Codex round
   assert.ok(env.calls.notify.some(n => n.kind === 'amber' && /edited while the fit was running/.test(n.msg)), JSON.stringify(env.calls.notify));
   assert.match(env.dom['sb-msg'].textContent, /discarded/);
 });
+
+// ── F1 Codex round 1: the local fallback never fits the press-time arrays over an edited model ──
+test('a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)', async () => {
+  let envRef = null;
+  const env = makeEnv({
+    uploadImpl: async () => { envRef.state.peaks[0].center = 286; return 'sid'; },   // the student edits while the upload runs
+    fetchImpl: async () => { throw new TypeError('Failed to fetch'); },
+  });
+  envRef = env;
+  await env.runFit();
+  assert.equal(env.calls.local, 0, 'no local fit over the edited model');
+  assert.equal(env.state.fitResult.marker, 'previous', 'previous result kept');
+  assert.match(env.dom['sb-msg'].textContent, /discarded \(model edited\)/);
+  assert.ok(env.calls.notify.some(n => n.kind === 'amber' && /edited while the fit was running/.test(n.msg)), JSON.stringify(env.calls.notify));
+  // unchanged model: the fallback still runs (the earlier test) — and an equivalent ROI spelling is not an edit
+  const same = makeEnv({ fetchImpl: async () => { throw new TypeError('Failed to fetch'); } });
+  await same.runFit();
+  assert.equal(same.calls.local, 1);
+});
diff --git a/tests/js/stale_statistics.test.js b/tests/js/stale_statistics.test.js
index d2c2667..e505962 100644
--- a/tests/js/stale_statistics.test.js
+++ b/tests/js/stale_statistics.test.js
@@ -41,7 +41,7 @@ function makeDoc() {
   return { els, getElementById: id => els[id] || null, querySelector: () => null, querySelectorAll: () => [] };
 }
 
-const STATE_FNS = ['_statsState', '_statsLiveState', '_statsRecordState', '_statsNote', '_statsSaveFields'];
+const STATE_FNS = ['_fitKeyCanon', '_sameFitKey', '_statsState', '_statsLiveState', '_statsRecordState', '_statsNote', '_statsSaveFields'];
 const STATE_CONSTS = ['_STATS_STALE_NOTE', '_STATS_UNVERIFIED_NOTE'];
 
 // Build a sandbox with the F1 accessor, the display functions and renderResults.
@@ -190,7 +190,9 @@ test('status-bar R: the previous model\'s R is not shown on a stale result; an u
 test('the stored fitted curve is never drawn, saved or stacked as the fit once stale', () => {
   const up = extractFn('updatePlot');
   assert.match(up, /fittedYBacked = haveFit[\s\S]*?_statsLiveState\(\) !== 'stale'/, 'chart envelope / residuals');
-  assert.match(up, /_refreshStatsState\(\)/, 'every repaint keeps the visible statistics honest');
+  assert.match(up, /_refreshStartsEvidence\(false, true\)/, 'every repaint reaches the refresh');
+  assert.match(extractFn('_refreshStartsEvidence'), /^function _refreshStartsEvidence[^\n]*\n(\s*\/\/[^\n]*\n)*\s*_refreshStatsState\(\);/, 'first thing, for EVERY caller (lock toggles, Lock All, updatePlot)');
+  for (const fn of ['toggleLock', 'toggleAllLocks']) assert.match(extractFn(fn), /_refreshStartsEvidence\(true\);/, fn + ' reaches the statistics refresh');
   assert.match(extractFn('_buildEntryRenderData'), /_statsRecordState\(src\) !== 'stale'/, 'stack Path A judged against the SOURCE record');
   assert.match(extractFn('_doPublicationExport'), /_figStats !== 'stale' && state\.fitResult\?\.fittedY/, 'figure');
   assert.match(extractFn('_doSaveSpectrum'), /_saveStats !== 'stale' && state\.fitResult\?\.fittedY/, 'spectrum save');
@@ -298,3 +300,85 @@ test('the refresh re-renders Results only when its rendered state differs', () =
   refresh();
   assert.strictEqual(env.renders, 2, 'current again');
 });
+
+// ── Codex round 1 ───────────────────────────────────────────────────────────
+function keyFns() {
+  const src = lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n')
+    + '\n' + ['_startsModelKey', '_fitKeyCanon', '_sameFitKey', '_statsState'].map(extractFn).join('\n');
+  return new Function(src + '\nreturn { _startsModelKey, _sameFitKey, _statsState };')();
+}
+
+test('an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not', () => {
+  const k = keyFns();
+  const peaks = [{ id: 1, shape: 'GL', center: 284.5, fwhm: 1, amplitude: 10 }];
+  const ui = { bgType: 'shirley', bgStart: '295', bgEnd: '280', shirleyIter: '10', endpointAvg: '3', roiMin: '280', roiMax: '295' };
+  const a = k._startsModelKey(peaks, ui, 0, []);
+  assert.ok(k._sameFitKey(a, k._startsModelKey(peaks, { ...ui, roiMin: '280.0', roiMax: '295.00' }, 0, [])), 'same data, same request');
+  assert.ok(!k._sameFitKey(a, k._startsModelKey(peaks, { ...ui, roiMin: '280.5' }, 0, [])), 'a real ROI change');
+  assert.ok(!k._sameFitKey(a, k._startsModelKey(peaks, { ...ui, bgType: 'linear' }, 0, [])), 'a background change');
+  assert.ok(!k._sameFitKey(a, k._startsModelKey(peaks, { ...ui, roiMin: '' }, 0, [])), 'an emptied field is not "0"');
+  assert.strictEqual(k._statsState({ startsModelKey: a }, k._startsModelKey(peaks, { ...ui, roiMin: '280.0' }, 0, [])), 'current');
+  assert.ok(!k._sameFitKey(null, null) && !k._sameFitKey(a, null), 'no key never matches');
+  assert.ok(!k._sameFitKey('not json', 'not json ') && k._sameFitKey('not json', 'not json'));
+});
+
+test('Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone', () => {
+  const src = [...STATE_CONSTS.map(constLine), ...['_fitKeyCanon', '_sameFitKey', ...STATE_FNS].map(extractFn), extractFn('_refreshStatsState')].join('\n');
+  const doc = makeDoc();
+  const env = { renders: 0 };
+  const state = { fitResult: null };
+  const refresh = new Function('document', 'state', 'env', `
+    const _startsLiveKey = () => 'K', _startsRecordKey = t => t.key;
+    const renderResults = () => { env.renders++; document.getElementById('results-area').setAttribute('data-stats-state', _statsLiveState()); };
+    const _applyStatDisplay = () => {}, _updateRFactorUI = () => {};
+    ${src}
+    return _refreshStatsState;`)(doc, state, env);
+  refresh();
+  assert.strictEqual(env.renders, 0, 'fresh page: nothing rendered yet, nothing to clear');
+  doc.els['results-area'].setAttribute('data-stats-state', 'current');   // a fit was shown
+  refresh();
+  assert.strictEqual(env.renders, 1, 'the shown result was cleared: back to the empty state');
+  refresh();
+  assert.strictEqual(env.renders, 1);
+});
+
+test('Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies', async () => {
+  const constants = lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n');
+  const run = async (editDuringUpload) => {
+    const state = { peaks: [], ccShift: 0, rawBE: [285, 284.5, 284], rawIntensity: [10, 20, 10] };
+    const dom = {};
+    const document = { getElementById: id => (dom[id] ??= { value: ({ 'bg-type': 'none', 'bg-start': '285', 'bg-end': '284', 'bg-endpoint-avg': '3', 'fit-method': 'leastsq' })[id] || '', style: {}, textContent: '', setAttribute() {}, classList: { add() {}, remove() {} } }), querySelector: () => ({}) };
+    const tab = { id: 1 };
+    const out = { restored: false, applied: 0, notes: [] };
+    const tabManager = { activeId: 1, _getTab: () => tab, _captureUI: () => ({ bgType: document.getElementById('bg-type').value, roiMin: '284', roiMax: '285' }), _syncActiveToRecord() {} };
+    const deps = { state, document, tabManager, notify: (m, k) => out.notes.push([m, k]), _opOwner: () => tab, _ownerActive: () => true, isC1sTab: () => true,
+      _autoFitSnapshot: () => ({}), _autoFitRestore: () => { out.restored = true; }, _showAutoFitConfirmModal: async () => true,
+      getROIData: () => ({ be: state.rawBE, inten: state.rawIntensity }), computeBackground: be => be.map(() => 0),
+      findGraphiteRawBE: () => 284.5, assessLowBERegion: () => ({}), pushUndo() {}, updateChargeCorrection() {},
+      buildAutoFitModel: () => [{ id: 1, name: 'Graphite', shape: 'Gaussian', center: 284.5, fwhm: 1, amplitude: 20 }],
+      renderPeakList() {}, _showFitSpinner() {}, _hideFitSpinner() {}, AbortController, setTimeout: () => 1, clearTimeout() {},
+      peakToBackendSpec: p => ({ ...p }), _getManualAnchors: () => [],
+      uploadToBackend: async () => { if (editDuringUpload) document.getElementById('bg-type').value = 'linear'; return 'sid'; },
+      fetch: async () => ({ json: async () => ({ success: true, statistics: { reduced_chi_square: 1 }, fitted_y: [10, 20, 10], residuals: [0, 0, 0] }) }),
+      applyBackendResult: () => { out.applied++; }, applyAutoFitResult: () => true };
+    const src = constants + '\n' + ['runAutoFitC1sGraphite', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
+    await new Function(...Object.keys(deps), src + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
+    return out;
+  };
+  const edited = await run(true);
+  assert.strictEqual(edited.applied, 0, 'nothing applied over the edited model');
+  assert.strictEqual(edited.restored, true, 'rolled back');
+  assert.ok(edited.notes.some(([m, k]) => k === 'amber' && /edited while it was running/.test(m)), JSON.stringify(edited.notes));
+  const clean = await run(false);
+  assert.strictEqual(clean.applied, 1, 'an unedited run is applied as before');
+  assert.strictEqual(clean.restored, false);
+});
+
+test('reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model', () => {
+  const load = extractFn('_loadSpectrumFile');
+  assert.match(load, /if \(data\.fittedY && data\.statistics\.statisticsState !== 'stale'\) fr\.fittedY = data\.fittedY;/);
+  assert.match(load, /if \(data\.statistics\.rFactor && data\.statistics\.statisticsState !== 'stale'\) fr\.rFactor = data\.statistics\.rFactor;/);
+  assert.match(html, /state\.fitResult\.rFactor == null && _statsLiveState\(\) !== 'stale'\) \{\s*state\.fitResult\.rFactor = _computeRFactor/, 'tab activation');
+  assert.match(extractFn('_doSaveProject'), /rFactor: t\.fitResult\.rFactor \|\| null/, 'project saves keep the fit\'s own R');
+  assert.match(extractFn('_doSaveSpectrum'), /rFactor: state\.fitResult\.rFactor \|\| null/, 'spectrum saves keep it too');
+});

exec
/bin/zsh -lc "rg -n 'BLOCKER|MAJOR|MINOR|VERDICT:' docs/autofit/codex/f1_stale_statistics_verdict_runA.md docs/autofit/codex/f1_stale_statistics_verdict_runB.md | tail -45
sed -n '7370,7595p' templates/index.html
sed -n '7810,8130p' templates/index.html
rg -n 'shirleyIter|endpointAvg|roiMin|parseInt.*(shirley|endpoint)|function getROIData|altKey|startsModelKey.*["'!=]==|fitKey.*[!=]=='"' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
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
  const comps = st.fit.components;
  const head = comps.map(c => `<th style="text-align:right;padding:2px 4px">${_escHtml(_startsPeakName(c.id))}<br><span style="font-weight:400;color:var(--text3)">area % &middot; move</span></th>`).join('');
  // every component: its OWN area fraction and its OWN move from the student's start.
  // A component this fit did not support shows neither (the same rule as the
  // Results table); an alternative's components are unjudged (no verdict was
  // computed for that solution) and are shown as they are.
  const cell = (c, judged, scale) => {
    const pk = getPeak(Number(c.id)) || getPeak(c.id);
    if (judged && pk && _isUnsupported(pk)) return `<td style="text-align:right;padding:2px 4px;color:var(--text3)" title="${_escAttr(_UNSUPPORTED_TIP)}">${_UNSUPPORTED_LABEL}</td>`;
    return `<td style="text-align:right;padding:2px 4px;font-family:var(--mono)">${(c.area_percent * scale).toFixed(1)}<br><span style="color:${_startsShiftColour(c.center_shift_from_start)}">${_startsEv(c.center_shift_from_start)}</span></td>`;
  };
  const largest = (cs, judged) => {
    // the largest move among components this fit supports (an unsupported one has no position to move)
    const eligible = cs.filter(c => { const pk = getPeak(Number(c.id)) || getPeak(c.id); return !(judged && pk && _isUnsupported(pk)); });
    return eligible.length ? eligible.reduce((m, c) => Math.abs(c.center_shift_from_start) > Math.abs(m.center_shift_from_start) ? c : m) : null;
  };
  const row = (label, chi, n, cs, judged, actions) => { const big = largest(cs, judged);
    // the judged row's percentages are over the components this fit supports (as in the Results table)
    const supportedPct = judged ? cs.reduce((t, c) => { const pk = getPeak(Number(c.id)) || getPeak(c.id); return t + ((pk && _isUnsupported(pk)) ? 0 : c.area_percent); }, 0) : 100;
    const scale = supportedPct > 0 ? 100 / supportedPct : 1;
    return `<tr style="border-top:1px solid var(--border)">
      <td style="padding:2px 4px">${label}</td><td style="text-align:right;padding:2px 4px;font-family:var(--mono)">${chi.toFixed(2)}</td>
      <td style="text-align:right;padding:2px 4px">${n}</td>
      ${cs.map(c => cell(c, judged, scale)).join('')}
      <td style="padding:2px 4px">${big ? _startsShiftHtml({ id: big.id, ev: big.center_shift_from_start }) : '&mdash;'}</td><td style="padding:2px 4px;white-space:nowrap">${actions}</td></tr>`; };
  html += `<h4 style="font-size:11px;margin:8px 0 4px" title="Solutions other starts reached with a lower reduced chi-square than your fit. A lower value is not a better chemical model: look at where the components went.">Other solutions found</h4>
    <div style="overflow-x:auto"><table style="width:100%;font-size:10px;border-collapse:collapse">
    <thead><tr><th style="text-align:left;padding:2px 4px">solution</th><th style="text-align:right;padding:2px 4px">χ²ᵣ</th><th style="text-align:right;padding:2px 4px" title="how many of the scattered starts ended here">starts here</th>${head}<th style="text-align:left;padding:2px 4px">largest move from your start</th><th></th></tr></thead><tbody>`;
  html += row('<b>Your fit</b>', st.fit.chi2r, st.n_same_as_fit, comps, true, '');
  alts.forEach((a, k) => {
    html += row('Alternative ' + (k + 1), a.chi2r, a.n_starts, a.components, false,
      `<button class="btn btn-sm" onclick="previewAlternative(${k})" title="Overlay this solution on the chart; click again to clear">Preview</button>
       <button class="btn btn-sm" onclick="useAlternative(${k})" title="Run the fit again starting from this solution. Your model changes only if that fit succeeds; you can undo it.">Use this solution</button>`);
  });
  return html + '</tbody></table></div></div>';
}

// The alternative's parameters on a COPY of the current peaks (null when the
// evidence no longer describes the current model).
function _altPeaks(alt) {
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
// where the model has several minima; and it gives no uncertainties. Unweighted A0-era results differed by more than 100 %.
// Every site that shows, exports or saves a fit result carries the
// designation, keyed on persisted identity so reloaded results are labelled.
const _LOCAL_FIT_CAVEAT = 'Local fit (Poisson-weighted like the server, no uncertainties): a starting point, not a reportable result. Run Fit before reporting.';
const _LOCAL_FIT_CAVEAT_UNWEIGHTED = 'Local unweighted fit: a starting point, not a reportable result. Run Fit before reporting.';
function _isLocalProvenance(p) {
  return !!(p && (p.engine === 'local' || p.objective === 'unweighted_residual_variance' || p.objective === 'poisson_weighted_chi_square'));
}
function _isLocalFit(fr) { return _isLocalProvenance(fr); }
// The record that governs the active model's designation: its live result,
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
3177:        roiMin: minBE, roiMax: maxBE,
3209:      ui: { bgType: 'shirley', bgStart: '', bgEnd: '', shirleyIter: '5',
3210:            endpointAvg: '1', roiMin: '', roiMax: '',
3393:        shirleyIter: document.getElementById('shirley-iter').value,
3394:        endpointAvg: document.getElementById('bg-endpoint-avg').value
3421:      pushUndo({ endpointAvg: document.getElementById('bg-endpoint-avg')?.value });
3453:      active.ui.endpointAvg = (data.background && data.background.endpointAvg) || LEGACY_ENDPOINT_AVG;
3460:        active.ui.shirleyIter = data.background.shirleyIter || '5';
3467:        active.ui.roiMin = data.roi.min || '';
3831:      shirleyIter: document.getElementById('shirley-iter')?.value || '5',
3832:      endpointAvg: document.getElementById('bg-endpoint-avg')?.value || LEGACY_ENDPOINT_AVG,
3833:      roiMin:      document.getElementById('roi-min')?.value || '',
3851:    set('shirley-iter', ui.shirleyIter);
3852:    set('bg-endpoint-avg', ui.endpointAvg || LEGACY_ENDPOINT_AVG);
3853:    set('roi-min', ui.roiMin);
4708:// (matches the shape of tab.ui — bgType, bgStart, bgEnd, shirleyIter,
4709:// endpointAvg) instead of reading from DOM. Used by stack-view render
4715:  const iter = parseInt(settings.shirleyIter) || 5;
4716:  const nAvg = parseInt(settings.endpointAvg) || 1;
4766:    shirleyIter: document.getElementById('shirley-iter').value,
4767:    endpointAvg: document.getElementById('bg-endpoint-avg').value,
5017:    const roiMinEl = document.getElementById('roi-min');
5019:    const roiMinVal = parseFloat(roiMinEl.value);
5021:    if (!isNaN(roiMinVal)) roiMinEl.value = (roiMinVal - delta).toFixed(1);
5084:function getROIData() {
5085:  const roiMinRaw = parseFloat(document.getElementById('roi-min').value);
5088:  const roiMin = isNaN(roiMinRaw) ? -Infinity : roiMinRaw;
5093:    if (corrBE[i] >= roiMin && corrBE[i] <= roiMax) {
5468:  const roiMin = parseFloat(document.getElementById('roi-min').value);
5470:  if (isNaN(roiMin) || isNaN(roiMax)) return;
5471:  const xMin = Math.min(roiMin, roiMax);
5472:  const xMax = Math.max(roiMin, roiMax);
5594:  const roiMin = parseFloat(document.getElementById('bg-end')?.value || 0);
5596:  const beMin = Math.min(roiMin, roiMax);
5597:  const beMax = Math.max(roiMin, roiMax);
6987:    roiMinDom:    document.getElementById('roi-min')?.value || '',
7024:      roiMin: snap.roiMinDom, roiMax: snap.roiMaxDom,
7044:  set('roi-min',   snap.roiMinDom);
7483:    const epAvg = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
7578:  let lo = parseFloat(ui.roiMin);
7625:const _STARTS_UI_FIELDS = ['bgType', 'bgStart', 'bgEnd', 'shirleyIter', 'endpointAvg', 'roiMin', 'roiMax'];
7652:function _sameFitKey(a, b) { return !!a && !!b && (a === b || _fitKeyCanon(a) === _fitKeyCanon(b)); }
7656:  return _startsModelKey(state.peaks, ui, state.ccShift, typeof _getManualAnchors === 'function' ? _getManualAnchors() : []);
7739:      !(state.fitResult && _historyPreview.altKey === state.fitResult.startsModelKey && _startsIfCurrent(state.fitResult, _startsLiveKey()))) {
7876:  _historyPreview = { snapId: key, altKey: state.fitResult.startsModelKey, peaks, fitResult: { chiReduced: alt.chi2r } };
7948:    const epAvgVal = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
9026:    shirleyIter: (srcUi && srcUi.shirleyIter) || '5',
9027:    endpointAvg: (srcUi && srcUi.endpointAvg) || LEGACY_ENDPOINT_AVG,
9048://       by ROI-filtering corrBE using src.ui.roiMin/roiMax, recompute
9096:    // Path B: post-load — derive ROI-window be from rawBE + ui.roiMin/Max,
9099:    const roiMinV = parseFloat(src.ui && src.ui.roiMin);
9102:    if (isFinite(roiMinV) && isFinite(roiMaxV)) {
9103:      const lo = Math.min(roiMinV, roiMaxV);
9104:      const hi = Math.max(roiMinV, roiMaxV);
10284:      shirleyIter: document.getElementById('shirley-iter').value,
10287:      endpointAvg: document.getElementById('bg-endpoint-avg').value,
10674:  // Saved-ui boundary: a file whose ui lacks endpointAvg was fitted at 1
10678:  const savedEp = data.ui && data.ui.endpointAvg;
10679:  active.ui = { ...active.ui, ...(data.ui || {}), endpointAvg: savedEp || LEGACY_ENDPOINT_AVG };
10821:        ui: { bgType: 'shirley', bgStart: '', bgEnd: '', shirleyIter: '5',
10822:              endpointAvg: '1', roiMin: '', roiMax: '',
10847:        shirleyIter: '5', roiMin: '', roiMax: '',
12223:    _pushUndoFor(tgt, { endpointAvg: tgt.ui && tgt.ui.endpointAvg });
14278:  const shirleyIter = document.getElementById('shirley-iter');
14279:  if (shirleyIter) {
14280:    shirleyIter.disabled = !needsIter;
14281:    shirleyIter.style.opacity = needsIter ? '1' : '0.4';
15390:      ((stored.regions || []).join(', ') || '?') + ', endpoint averaging ' + (stored.endpointAvg || '?') +
15855:    options.endpoint_avg = parseInt(document.getElementById('bg-endpoint-avg')?.value) || 1;
15924:    _fpSetLast({ body, method, regions, fitFullWindow: !!options.fit_full_window, endpointAvg: engineEndpointAvg }, owner);
16119:  pushUndo({ endpointAvg: document.getElementById('bg-endpoint-avg')?.value });
16149:  const usedEp = (_fpLast && _fpLast.endpointAvg) || LEGACY_ENDPOINT_AVG;
16153:  if (active) active.ui.endpointAvg = usedEp;   // unconditional: the record must match the fit even if the field was hand-edited

exec
/bin/zsh -lc "sed -n '6610,6635p' docs/autofit/codex/f1_stale_statistics_verdict_runA.md
sed -n '6370,6394p' docs/autofit/codex/f1_stale_statistics_verdict_runB.md
sed -n '7610,7750p' templates/index.html
sed -n '1000,1180p' templates/index.html
sed -n '4680,4775p' templates/index.html
rg -n 'id=\"(shirley-iter|bg-endpoint-avg|roi-min|bg-start)\"|function renderResults|function renderQuant|oninput.*rsf|function _computeRFactor|function _updateRFactorUI' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
Auto-Fit after background edit: {"requestedBG":"none","liveBG":"linear","stats":"current","fitChi":1,"restored":false}

codex
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
tokens used
105,525
1. **MAJOR — Auto-Fit stamps edits made during the request as current.** [templates/index.html:7345](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:7345)  
const run=new Function(constants+'\\''\\n'\\''+[\"_startsModelKey\",\"_startsLiveKey\",\"_statsState\",\"_statsLiveState\",\"getCorrectedBE\",\"getROIData\"].map(fn).join('\\''\\n'\\'')+\"\\nconst state={rawBE:[279,280,281,282],rawIntensity:[1,2,3,4],peaks:[],ccShift:0};\\nconst fields={'\\''roi-min'\\'':{value:'\\''280.0'\\''},'\\''roi-max'\\'':{value:'\\''282'\\''}};\\nconst document={getElementById:id=>fields[id]};\\nconst tabManager={_captureUI:()=>({roiMin:fields['\\''roi-min'\\''].value,roiMax:fields['\\''roi-max'\\''].value})};\\nstate.fitResult={startsModelKey:_startsLiveKey()};\\nconst before=getROIData(); fields['\\''roi-min'\\''].value='\\''280'\\'';\\nreturn {unchangedData:JSON.stringify(before)===JSON.stringify(getROIData()),state:_statsLiveState()};\\n\");console.log(JSON.stringify(run()));'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
{"unchangedData":true,"state":"stale"}

codex
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
tokens used
110,246

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
    min-width: 0;
  }
  #spectrum-tab-bar::-webkit-scrollbar { display: none; }
  .tab-scroll-btn {
    display: none;
    align-items: center;
    justify-content: center;
    width: 22px;
    flex-shrink: 0;
    background: var(--bg2);
    border: none;
    color: var(--text2);
    cursor: pointer;
    font-size: 18px;
    line-height: 1;
    padding: 0;
    transition: background 0.1s, color 0.1s;
    z-index: 1;
  }
  .tab-scroll-btn.visible { display: flex; }
  #tab-scroll-left { border-right: 1px solid var(--border); }
  #tab-scroll-right { border-left: 1px solid var(--border); }
  .tab-scroll-btn:hover { background: var(--bg3); color: var(--text); }
  .sp-tab {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 5px 10px 5px 9px;
    font-family: var(--mono);
    font-size: 11px;
    color: var(--text2);
    cursor: pointer;
    border-right: 1px solid var(--border);
    border-bottom: 2px solid transparent;
    white-space: nowrap;
    flex-shrink: 0;
    transition: background 0.1s;
    user-select: none;
  }
  .sp-tab:hover {
    background: var(--bg3);
    color: var(--text);
    box-shadow: inset 0 -2px 0 var(--border2);
  }
  .sp-tab.active:hover {
    box-shadow: none;
  }
  .sp-tab.active {
    background: var(--bg);
    color: var(--text);
    border-bottom-color: var(--accent);
  }
  .sp-tab-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .sp-tab-close {
    margin-left: 4px;
    opacity: 0;
    font-size: 13px;
    line-height: 1;
    color: var(--text3);
    cursor: pointer;
    padding: 1px 3px;
    border-radius: 3px;
  }
  .sp-tab:hover .sp-tab-close { opacity: 1; }
  .sp-tab-close:hover { background: var(--red-dim); color: var(--red); }
  .sp-tab.dragging { opacity: 0.35; }
  .sp-tab.drag-over-left { box-shadow: inset 3px 0 0 var(--accent); }
  .sp-tab.drag-over-right { box-shadow: inset -3px 0 0 var(--accent); }

  /* ── Stack tab visual identity ──────────────────────────── */
  .sp-tab.is-stack {
    background: var(--purple-dim);
    border-bottom-color: rgba(180,142,255,0.35);
  }
  .sp-tab.is-stack.active {
    background: var(--bg);
    border-bottom-color: var(--purple);
  }
  .sp-tab.is-stack .sp-tab-dot { display: none; }

  /* ── Stack legend rows ──────────────────────────────────── */
  .stack-legend-row {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 10px;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    background: var(--bg2);
    margin-bottom: 6px;
    font-size: 11px;
  }
  .stack-legend-row .swatch {
    width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
  }
  .stack-legend-row .name { flex: 1; color: var(--text); font-weight: 500; }
  .stack-legend-row .cc {
    font-family: var(--mono); font-size: 10px; color: var(--text2);
    margin-right: 4px;
  }
  .stack-legend-row .vis { cursor: pointer; accent-color: var(--accent); }
  .stack-legend-row .fit-toggle { cursor: pointer; accent-color: var(--accent); }
  .stack-legend-row .fit-toggle:disabled { opacity: 0.3; cursor: not-allowed; }
  .stack-legend-row .remove {
    cursor: pointer; padding: 0 4px;
    color: var(--text3); font-size: 14px; line-height: 1;
    border-radius: 3px;
  }
  .stack-legend-row .remove:hover { color: var(--red); background: var(--red-dim); }

  /* ── Common (always-visible) panel controls ─────────────── */
  /* Hosts the universal Line Width slider for both spectrum and stack
     tabs. Sits above .tabs and any .tab-panel so the slider DOM stays
     mounted across tab switches (single bind point in activateTab). */
  .common-controls {
    padding: 0 0 10px 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 10px;
  }

  /* ── Stack control sliders (offset) ─────────────────────── */
  .stack-controls {
    padding: 0 0 10px 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 10px;
  }
  .stack-control-row {
    display: flex; align-items: center; gap: 8px;
    margin-bottom: 8px;
    font-size: 11px;
  }
  .stack-control-row:last-child { margin-bottom: 0; }
  .stack-control-row label {
    width: 72px; flex-shrink: 0;
    color: var(--text2);
  }
  .stack-control-row input[type=range] {
    flex: 1;
    accent-color: var(--accent);
    cursor: pointer;
  }
  .stack-control-value {
    width: 56px; flex-shrink: 0; text-align: right;
    font-family: var(--mono); font-size: 10px; color: var(--text);
  }

  /* ── Add-spectrum dropdown menu ─────────────────────────── */
  .add-spectrum-menu {
    position: absolute; top: 100%; left: 0;
    min-width: 180px; max-height: 240px; overflow-y: auto;
    background: var(--bg3); border: 1px solid var(--border2);
    border-radius: var(--radius); padding: 4px; z-index: 30;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  }
  .add-spectrum-menu .item {
    padding: 5px 10px; cursor: pointer; border-radius: 4px;
    font-size: 11px; color: var(--text); white-space: nowrap;
  }
  .add-spectrum-menu .item:hover { background: var(--accent-dim); color: var(--accent2); }
  .add-spectrum-menu .empty { padding: 8px; font-size: 10px; color: var(--text3); }

  /* ── Hide peak/fit controls when a stack tab is active ──── */
  body.stack-tab-active .peak-fit-control { display: none !important; }

  /* ── Survey tab in right sidebar ───────────────────────── */
  #tab-survey { display: none; }
  #tab-survey.active { display: block; }
  .tab.survey-tab { display: none; }
  .tab.survey-tab.visible { display: block; }
  #survey-info { padding: 4px 0; }
  #survey-info .survey-heading {
    font-family: var(--mono); font-size: 10px; font-weight: 500;
    letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--text3); margin-bottom: 10px;
  }
  #survey-no-data { color: var(--text3); font-size: 11px; text-align: center; padding: 20px 0; }
  /* Survey selector list */
  #survey-selector { list-style: none; padding: 0; margin: 0 0 12px; }
  #survey-selector li {
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
2035:                <input type="number" id="bg-start" value="726" step="0.5" oninput="_invalidateBgCache(); updatePlot()">
2045:                <input type="number" id="shirley-iter" value="5" min="1" max="50" step="1" oninput="_clampShirleyIter(); _invalidateBgCache(); updatePlot()" title="Number of iterations for the Shirley background calculation. The algorithm converges quickly — most of the change happens between 1 and 5 iterations. Values above 10 rarely produce visible differences. Default: 5.">
2049:                <input type="number" id="bg-endpoint-avg" value="3" min="1" max="50" step="1" oninput="_invalidateBgCache(); updatePlot()" title="Number of points to average at each endpoint for smoother background anchoring">
2064:                <input type="number" id="roi-min" value="706" step="0.5" oninput="updatePlot();_recomputeAutoFitMenuState()">
8654:function renderResults() {
8820:function renderQuantify(areas, totalArea) {
11580:function _computeRFactor(fitResult) {
11620:function _updateRFactorUI(rf) {

exec
/bin/zsh -lc 'node --test tests/js/stale_statistics.test.js tests/js/fit_acceptance.test.js tests/js/local_lm_descent.test.js tests/js/scattered_starts.test.js tests/js/unsupported_components.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 exited 1 in 6149ms:
# Subtest: A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
ok 1 - A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
  ---
  duration_ms: 8.471378
  type: 'test'
  ...
# Subtest: a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
ok 2 - a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
  ---
  duration_ms: 6.464584
  type: 'test'
  ...
# Subtest: a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
ok 3 - a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
  ---
  duration_ms: 2.436765
  type: 'test'
  ...
# Subtest: a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
ok 4 - a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
  ---
  duration_ms: 8.463629
  type: 'test'
  ...
# Subtest: a converged backend result is applied (sanity)
ok 5 - a converged backend result is applied (sanity)
  ---
  duration_ms: 2.618886
  type: 'test'
  ...
# Subtest: the engine/objective labels of a fit result survive spectrum and project save/load
ok 6 - the engine/objective labels of a fit result survive spectrum and project save/load
  ---
  duration_ms: 0.660897
  type: 'test'
  ...
# Subtest: an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
ok 7 - an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
  ---
  duration_ms: 2.983957
  type: 'test'
  ...
# Subtest: an HTTP 502 on the upload is a server failure, not a transport failure
ok 8 - an HTTP 502 on the upload is a server failure, not a transport failure
  ---
  duration_ms: 2.317736
  type: 'test'
  ...
# Subtest: uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
ok 9 - uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
  ---
  duration_ms: 1.618777
  type: 'test'
  ...
# Subtest: every consumer that prints the goodness-of-fit statistic routes through the statistic identity
ok 10 - every consumer that prints the goodness-of-fit statistic routes through the statistic identity
  ---
  duration_ms: 0.833081
  type: 'test'
  ...
# Subtest: uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
ok 11 - uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
  ---
  duration_ms: 0.730464
  type: 'test'
  ...
# Subtest: a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
ok 12 - a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
  ---
  duration_ms: 1.383296
  type: 'test'
  ...
# Subtest: starting-point helpers: keyed on the persisted objective, weighted results untouched
ok 13 - starting-point helpers: keyed on the persisted objective, weighted results untouched
  ---
  duration_ms: 2.803374
  type: 'test'
  ...
# Subtest: Quantify shows the starting-point banner for a local result and not for a weighted one
ok 14 - Quantify shows the starting-point banner for a local result and not for a weighted one
  ---
  duration_ms: 4.509998
  type: 'test'
  ...
# Subtest: every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
ok 15 - every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
  ---
  duration_ms: 1.614747
  type: 'test'
  ...
# Subtest: project save derives the designation from the objective for an older local result lacking the new fields
ok 16 - project save derives the designation from the objective for an older local result lacking the new fields
  ---
  duration_ms: 6.74645
  type: 'test'
  ...
# Subtest: stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
ok 17 - stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
  ---
  duration_ms: 0.869177
  type: 'test'
  ...
# Subtest: _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
ok 18 - _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
  ---
  duration_ms: 3.302168
  type: 'test'
  ...
# Subtest: history preview glow is keyed on the dataset flag, not the label text
ok 19 - history preview glow is keyed on the dataset flag, not the label text
  ---
  duration_ms: 0.662554
  type: 'test'
  ...
# Subtest: spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
ok 20 - spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
  ---
  duration_ms: 0.447437
  type: 'test'
  ...
# Subtest: _applyStatDisplay clears header, tooltip, caption and value together on local → none
ok 21 - _applyStatDisplay clears header, tooltip, caption and value together on local → none
  ---
  duration_ms: 2.998792
  type: 'test'
  ...
# Subtest: _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
ok 22 - _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
  ---
  duration_ms: 1.538337
  type: 'test'
  ...
# Subtest: fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
ok 23 - fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
  ---
  duration_ms: 1.383608
  type: 'test'
  ...
# Subtest: undo/redo snapshots carry and restore model provenance
ok 24 - undo/redo snapshots carry and restore model provenance
  ---
  duration_ms: 4.193993
  type: 'test'
  ...
# Subtest: round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
ok 25 - round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
  ---
  duration_ms: 1.184591
  type: 'test'
  ...
# Subtest: _provenanceOf derives a designation from a live local result, and undo snapshots use it
ok 26 - _provenanceOf derives a designation from a live local result, and undo snapshots use it
  ---
  duration_ms: 2.685167
  type: 'test'
  ...
# Subtest: batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
ok 27 - batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
  ---
  duration_ms: 0.368163
  type: 'test'
  ...
# Subtest: the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
ok 28 - the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
  ---
  duration_ms: 2.481686
  type: 'test'
  ...
# Subtest: round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
ok 29 - round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
  ---
  duration_ms: 0.684592
  type: 'test'
  ...
# Subtest: the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
ok 30 - the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
  ---
  duration_ms: 2.762144
  type: 'test'
  ...
# Subtest: the sidebar banner is sticky at the top of the scrolling panel body
ok 31 - the sidebar banner is sticky at the top of the scrolling panel body
  ---
  duration_ms: 0.298057
  type: 'test'
  ...
# Subtest: the sidebar banner shows on a stack tab whose visible entries draw a local source fit
ok 32 - the sidebar banner shows on a stack tab whose visible entries draw a local source fit
  ---
  duration_ms: 2.58919
  type: 'test'
  ...
# Subtest: every stack chart repaint path refreshes the sidebar designation before any early return
ok 33 - every stack chart repaint path refreshes the sidebar designation before any early return
  ---
  duration_ms: 0.442218
  type: 'test'
  ...
# Subtest: closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
ok 34 - closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
  ---
  duration_ms: 0.196545
  type: 'test'
  ...
# Subtest: W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
ok 35 - W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
  ---
  duration_ms: 2.89059
  type: 'test'
  ...
# Subtest: TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
ok 36 - TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
  ---
  duration_ms: 4.267748
  type: 'test'
  ...
# Subtest: adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
ok 37 - adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
  ---
  duration_ms: 3.009037
  type: 'test'
  ...
# Subtest: adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
ok 38 - adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
  ---
  duration_ms: 2.919846
  type: 'test'
  ...
# Subtest: adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
ok 39 - adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
  ---
  duration_ms: 2.679187
  type: 'test'
  ...
# Subtest: adoption: success records the choice, the starts evidence and the key of the model it describes
ok 40 - adoption: success records the choice, the starts evidence and the key of the model it describes
  ---
  duration_ms: 2.812276
  type: 'test'
  ...
# Subtest: an ordinary Run Fit on one unlinked component does not ask for the starts check
ok 41 - an ordinary Run Fit on one unlinked component does not ask for the starts check
  ---
  duration_ms: 3.060789
  type: 'test'
  ...
# Subtest: a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
ok 42 - a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
  ---
  duration_ms: 3.160512
  type: 'test'
  ...
# Subtest: a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
ok 43 - a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
  ---
  duration_ms: 5.531738
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
  duration_ms: 1359.031058
  type: 'test'
  ...
# Subtest: A01 replay: the linked U 4f pair also descends
ok 45 - A01 replay: the linked U 4f pair also descends
  ---
  duration_ms: 249.808945
  type: 'test'
  ...
# Subtest: noiseless Gaussian: amplitude 10 started at 5 is recovered
ok 46 - noiseless Gaussian: amplitude 10 started at 5 is recovered
  ---
  duration_ms: 12.033159
  type: 'test'
  ...
# Subtest: acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
ok 47 - acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
  ---
  duration_ms: 9.035778
  type: 'test'
  ...
# Subtest: a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
ok 48 - a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
  ---
  duration_ms: 13.253271
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
ok 49 - bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
  ---
  duration_ms: 9.069605
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
ok 50 - bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
  ---
  duration_ms: 8.522478
  type: 'test'
  ...
# Subtest: a weak component the data DO hold is no longer forced up to an amplitude of 1
ok 51 - a weak component the data DO hold is no longer forced up to an amplitude of 1
  ---
  duration_ms: 8.790412
  type: 'test'
  ...
# Subtest: derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
ok 52 - derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
  ---
  duration_ms: 43.835415
  type: 'test'
  ...
# Subtest: derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
ok 53 - derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
  ---
  duration_ms: 25.868264
  type: 'test'
  ...
# Subtest: a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
ok 54 - a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
  ---
  duration_ms: 9.739617
  type: 'test'
  ...
# Subtest: linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
ok 55 - linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
  ---
  duration_ms: 13.668383
  type: 'test'
  ...
# Subtest: round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
ok 56 - round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
  ---
  duration_ms: 11.990099
  type: 'test'
  ...
# Subtest: round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
ok 57 - round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
  ---
  duration_ms: 10.120761
  type: 'test'
  ...
# Subtest: round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
ok 58 - round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
  ---
  duration_ms: 11.132596
  type: 'test'
  ...
# Subtest: A01 replay targets converge to constrained stationary points (C1s and U 4f)
ok 59 - A01 replay targets converge to constrained stationary points (C1s and U 4f)
  ---
  duration_ms: 1365.804454
  type: 'test'
  ...
# Subtest: round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
ok 60 - round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
  ---
  duration_ms: 58.94215
  type: 'test'
  ...
# Subtest: round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
ok 61 - round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
  ---
  duration_ms: 20.835553
  type: 'test'
  ...
# Subtest: round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
ok 62 - round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
  ---
  duration_ms: 12.427742
  type: 'test'
  ...
# Subtest: round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
ok 63 - round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
  ---
  duration_ms: 74.656555
  type: 'test'
  ...
# Subtest: round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
ok 64 - round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
  ---
  duration_ms: 1159.010798
  type: 'test'
  ...
# Subtest: round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
ok 65 - round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
  ---
  duration_ms: 21.252422
  type: 'test'
  ...
# Subtest: round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
ok 66 - round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
  ---
  duration_ms: 11.177743
  type: 'test'
  ...
# Subtest: weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
ok 67 - weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
  ---
  duration_ms: 8.550454
  type: 'test'
  ...
# Subtest: server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
not ok 68 - server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
  ---
  duration_ms: 1444.614044
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
  duration_ms: 21.749248
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
ok 70 - an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
  ---
  duration_ms: 24.588747
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
ok 71 - an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
  ---
  duration_ms: 19.98639
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
ok 72 - round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
  ---
  duration_ms: 8.71094
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
ok 73 - round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
  ---
  duration_ms: 8.809864
  type: 'test'
  ...
# Subtest: recovery from an amplitude of exactly zero (the new floor is not a trap)
ok 74 - recovery from an amplitude of exactly zero (the new floor is not a trap)
  ---
  duration_ms: 10.714836
  type: 'test'
  ...
# Subtest: summary wording: counts of STARTS and of SOLUTIONS, never certification
ok 75 - summary wording: counts of STARTS and of SOLUTIONS, never certification
  ---
  duration_ms: 17.394705
  type: 'test'
  ...
# Subtest: no alternative: one line, no table
ok 76 - no alternative: one line, no table
  ---
  duration_ms: 11.888571
  type: 'test'
  ...
# Subtest: alternatives: "Your fit" first, own areas per component, the moved component named and coloured
ok 77 - alternatives: "Your fit" first, own areas per component, the moved component named and coloured
  ---
  duration_ms: 8.419775
  type: 'test'
  ...
# Subtest: RED band: applying asks first and NAMES the component and the distance
ok 78 - RED band: applying asks first and NAMES the component and the distance
  ---
  duration_ms: 8.889142
  type: 'test'
  ...
# Subtest: adoption never writes the live model itself: the alternative is only the START of a fit, and the choice rides along
ok 79 - adoption never writes the live model itself: the alternative is only the START of a fit, and the choice rides along
  ---
  duration_ms: 8.28947
  type: 'test'
  ...
# Subtest: below the red band there is no dialog
ok 80 - below the red band there is no dialog
  ---
  duration_ms: 23.612354
  type: 'test'
  ...
# Subtest: a locked parameter is never moved by an alternative
ok 81 - a locked parameter is never moved by an alternative
  ---
  duration_ms: 8.190373
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a peak deleted: the panel says so and nothing can be applied
ok 82 - evidence is bound to the fitted model — a peak deleted: the panel says so and nothing can be applied
  ---
  duration_ms: 9.24402
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a shape changed (GL -> DS) and the centre moved: the panel says so and nothing can be applied
ok 83 - evidence is bound to the fitted model — a shape changed (GL -> DS) and the centre moved: the panel says so and nothing can be applied
  ---
  duration_ms: 9.659464
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a lock toggled: the panel says so and nothing can be applied
ok 84 - evidence is bound to the fitted model — a lock toggled: the panel says so and nothing can be applied
  ---
  duration_ms: 8.954939
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a link added: the panel says so and nothing can be applied
ok 85 - evidence is bound to the fitted model — a link added: the panel says so and nothing can be applied
  ---
  duration_ms: 9.17537
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — an undo that restored other values: the panel says so and nothing can be applied
ok 86 - evidence is bound to the fitted model — an undo that restored other values: the panel says so and nothing can be applied
  ---
  duration_ms: 8.17041
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — an auto-fit asymmetry bound changed: the panel says so and nothing can be applied
ok 87 - evidence is bound to the fitted model — an auto-fit asymmetry bound changed: the panel says so and nothing can be applied
  ---
  duration_ms: 8.568872
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — the background type changed: the panel says so and nothing can be applied
ok 88 - evidence is bound to the fitted model — the background type changed: the panel says so and nothing can be applied
  ---
  duration_ms: 8.50516
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — the background window moved: the panel says so and nothing can be applied
ok 89 - evidence is bound to the fitted model — the background window moved: the panel says so and nothing can be applied
  ---
  duration_ms: 7.984861
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — endpoint averaging changed: the panel says so and nothing can be applied
ok 90 - evidence is bound to the fitted model — endpoint averaging changed: the panel says so and nothing can be applied
  ---
  duration_ms: 8.252889
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — the ROI changed: the panel says so and nothing can be applied
ok 91 - evidence is bound to the fitted model — the ROI changed: the panel says so and nothing can be applied
  ---
  duration_ms: 7.935496
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a manual anchor was added: the panel says so and nothing can be applied
ok 92 - evidence is bound to the fitted model — a manual anchor was added: the panel says so and nothing can be applied
  ---
  duration_ms: 8.228418
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — the charge correction changed: the panel says so and nothing can be applied
ok 93 - evidence is bound to the fitted model — the charge correction changed: the panel says so and nothing can be applied
  ---
  duration_ms: 8.196277
  type: 'test'
  ...
# Subtest: a cosmetic edit (name, colour, visibility) does not invalidate the evidence
ok 94 - a cosmetic edit (name, colour, visibility) does not invalidate the evidence
  ---
  duration_ms: 7.93903
  type: 'test'
  ...
# Subtest: preview overlays a COPY and toggles off; the model is untouched
ok 95 - preview overlays a COPY and toggles off; the model is untouched
  ---
  duration_ms: 9.577426
  type: 'test'
  ...
# Subtest: a record is keyed like the live tab (project save of a non-active tab)
ok 96 - a record is keyed like the live tab (project save of a non-active tab)
  ---
  duration_ms: 9.510111
  type: 'test'
  ...
# Subtest: what is saved: the counts, never the alternatives' parameter sets
ok 97 - what is saved: the counts, never the alternatives' parameter sets
  ---
  duration_ms: 10.049263
  type: 'test'
  ...
# Subtest: a loaded summary (no parameter sets) still renders its line and offers nothing to apply
ok 98 - a loaded summary (no parameter sets) still renders its line and offers nothing to apply
  ---
  duration_ms: 9.453319
  type: 'test'
  ...
# Subtest: wiring: the trigger is decided with the other request inputs, BEFORE the first await
ok 99 - wiring: the trigger is decided with the other request inputs, BEFORE the first await
  ---
  duration_ms: 13.809073
  type: 'test'
  ...
# Subtest: persistence and export sites carry the summary
ok 100 - persistence and export sites carry the summary
  ---
  duration_ms: 2.674295
  type: 'test'
  ...
# Subtest: the tooltip reports what the starts found and claims nothing about the data
ok 101 - the tooltip reports what the starts found and claims nothing about the data
  ---
  duration_ms: 0.734005
  type: 'test'
  ...
# Subtest: the recorded adoption is worded once, for the exports
ok 102 - the recorded adoption is worded once, for the exports
  ---
  duration_ms: 9.160708
  type: 'test'
  ...
# Subtest: one accessor classifies a result against a key: none / unverified / current / stale
ok 103 - one accessor classifies a result against a key: none / unverified / current / stale
  ---
  duration_ms: 16.92897
  type: 'test'
  ...
# Subtest: the key is the step (b) key: F1 adds no second binding mechanism and no new key field
ok 104 - the key is the step (b) key: F1 adds no second binding mechanism and no new key field
  ---
  duration_ms: 3.725434
  type: 'test'
  ...
# Subtest: Results panel, current: statistic, RMSE, R and sigma are shown
ok 105 - Results panel, current: statistic, RMSE, R and sigma are shown
  ---
  duration_ms: 9.298047
  type: 'test'
  ...
# Subtest: Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
ok 106 - Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
  ---
  duration_ms: 7.172082
  type: 'test'
  ...
# Subtest: Results panel, unverified (older save, no key): values shown with a plain note
ok 107 - Results panel, unverified (older save, no key): values shown with a plain note
  ---
  duration_ms: 7.373967
  type: 'test'
  ...
# Subtest: status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
ok 108 - status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
  ---
  duration_ms: 6.995431
  type: 'test'
  ...
# Subtest: the stored fitted curve is never drawn, saved or stacked as the fit once stale
ok 109 - the stored fitted curve is never drawn, saved or stacked as the fit once stale
  ---
  duration_ms: 2.936575
  type: 'test'
  ...
# Subtest: saves keep the key and say plainly when the statistics are stale or unverified
ok 110 - saves keep the key and say plainly when the statistics are stale or unverified
  ---
  duration_ms: 2.271478
  type: 'test'
  ...
# Subtest: CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
ok 111 - CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
  ---
  duration_ms: 14.172532
  type: 'test'
  ...
# Subtest: XLSX: stale writes a WARNING row instead of the statistic, and no sigma
ok 112 - XLSX: stale writes a WARNING row instead of the statistic, and no sigma
  ---
  duration_ms: 4.88948
  type: 'test'
  ...
# Subtest: TSV: stale says the Model / Residual columns are the current, unfitted model
ok 113 - TSV: stale says the Model / Residual columns are the current, unfitted model
  ---
  duration_ms: 7.787408
  type: 'test'
  ...
# Subtest: the refresh re-renders Results only when its rendered state differs
ok 114 - the refresh re-renders Results only when its rendered state differs
  ---
  duration_ms: 3.245475
  type: 'test'
  ...
# Subtest: an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
ok 115 - an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
  ---
  duration_ms: 2.832763
  type: 'test'
  ...
# Subtest: Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
ok 116 - Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
  ---
  duration_ms: 3.465359
  type: 'test'
  ...
# Subtest: Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
ok 117 - Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
  ---
  duration_ms: 7.293336
  type: 'test'
  ...
# Subtest: reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
ok 118 - reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
  ---
  duration_ms: 1.537575
  type: 'test'
  ...
# Subtest: the twin reproduces the server verdict on real responses, and defers to the server field when present
ok 119 - the twin reproduces the server verdict on real responses, and defers to the server field when present
  ---
  duration_ms: 10.204021
  type: 'test'
  ...
# Subtest: _applySupport writes every peak, follows ancestry to the root, stamps the fit key, and leaves null where the response says nothing
ok 120 - _applySupport writes every peak, follows ancestry to the root, stamps the fit key, and leaves null where the response says nothing
  ---
  duration_ms: 6.17564
  type: 'test'
  ...
# Subtest: the verdict applies only to the model and context it was computed for
ok 121 - the verdict applies only to the model and context it was computed for
  ---
  duration_ms: 4.681174
  type: 'test'
  ...
# Subtest: the local engine computes the same statistic from its own residuals
ok 122 - the local engine computes the same statistic from its own residuals
  ---
  duration_ms: 5.927684
  type: 'test'
  ...
# Subtest: sidebar card: badge; centre and width shown as a dash; area % excluded and the others renormalised
ok 123 - sidebar card: badge; centre and width shown as a dash; area % excluded and the others renormalised
  ---
  duration_ms: 5.905899
  type: 'test'
  ...
# Subtest: results table: greyed row, no centre / width / sigma, area kept, percentage dash, and the note beneath
ok 124 - results table: greyed row, no centre / width / sigma, area kept, percentage dash, and the note beneath
  ---
  duration_ms: 11.906949
  type: 'test'
  ...
# Subtest: uncertainty panel: one rule-0 warning for the component, no per-parameter alarms and no "locked" note for it
ok 125 - uncertainty panel: one rule-0 warning for the component, no per-parameter alarms and no "locked" note for it
  ---
  duration_ms: 4.686916
  type: 'test'
  ...
# Subtest: Quantify: excluded from the body, listed beneath with the reason; total and percentages over the rest
ok 126 - Quantify: excluded from the body, listed beneath with the reason; total and percentages over the rest
  ---
  duration_ms: 5.605354
  type: 'test'
  ...
# Subtest: CSV / XLSX export: Status column, suppressed cells, At% empty, WARNING line
ok 127 - CSV / XLSX export: Status column, suppressed cells, At% empty, WARNING line
  ---
  duration_ms: 7.027525
  type: 'test'
  ...
# Subtest: publication figure: no label at the (zero) component, legend entry says so; chart and stack labels say so
ok 128 - publication figure: no label at the (zero) component, legend entry says so; chart and stack labels say so
  ---
  duration_ms: 2.683031
  type: 'test'
  ...
# Subtest: write-back: a server result sets support; the local engine and a propagated model reset it
ok 129 - write-back: a server result sets support; the local engine and a propagated model reset it
  ---
  duration_ms: 1.573447
  type: 'test'
  ...
# Subtest: persistence: support travels with the peak object through every save (the peak is spread whole)
ok 130 - persistence: support travels with the peak object through every save (the peak is spread whole)
  ---
  duration_ms: 1.036754
  type: 'test'
  ...
# Subtest: CSV / XLSX: an unsupported DS+G component exports no width of any kind (beta, m)
ok 131 - CSV / XLSX: an unsupported DS+G component exports no width of any kind (beta, m)
  ---
  duration_ms: 5.864187
  type: 'test'
  ...
# Subtest: the scattered-starts table: an unsupported component shows neither area % nor a move in "Your fit", and is not the largest move
ok 132 - the scattered-starts table: an unsupported component shows neither area % nor a move in "Your fit", and is not the largest move
  ---
  duration_ms: 6.863084
  type: 'test'
  ...
# Subtest: exports: a stale or keyless verdict is "not established", never "supported"
ok 133 - exports: a stale or keyless verdict is "not established", never "supported"
  ---
  duration_ms: 9.959764
  type: 'test'
  ...
# Subtest: Auto-Fit finalisation (locks, charge shift) keeps its own verdicts: _restampSupport, called after the locks
ok 134 - Auto-Fit finalisation (locks, charge shift) keeps its own verdicts: _restampSupport, called after the locks
  ---
  duration_ms: 4.400592
  type: 'test'
  ...
# Subtest: a .fit.json import onto this tab's data carries no verdict
ok 135 - a .fit.json import onto this tab's data carries no verdict
  ---
  duration_ms: 0.139027
  type: 'test'
  ...
# Subtest: _isUnsupported is never handed an array index as its key (Array.filter passes one)
ok 136 - _isUnsupported is never handed an array index as its key (Array.filter passes one)
  ---
  duration_ms: 4.355934
  type: 'test'
  ...
# Subtest: a key change re-renders every consumer of the verdict — each compared with ITS OWN rendering
ok 137 - a key change re-renders every consumer of the verdict — each compared with ITS OWN rendering
  ---
  duration_ms: 2.838774
  type: 'test'
  ...
# Subtest: stack tabs judge a source component against the SOURCE record's key
ok 138 - stack tabs judge a source component against the SOURCE record's key
  ---
  duration_ms: 4.612292
  type: 'test'
  ...
# Subtest: "Your fit" percentages are over supported components; an empty Quantify shows no 100 %
ok 139 - "Your fit" percentages are over supported components; an empty Quantify shows no 100 %
  ---
  duration_ms: 11.914248
  type: 'test'
  ...
# Subtest: the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
ok 140 - the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
  ---
  duration_ms: 5.235679
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
# duration_ms 6189.617573

codex
The Auto-Fit key is captured after its provisional shift and model setup, so those changes do not make it discard itself. I found a potential false-current case in numeric canonicalization: it uses `Number()`, while background controls use `parseInt()`. I’m checking that with real background calculations, along with reload and refresh behavior.
exec
/bin/zsh -lc "sed -n '3208,3355p' templates/index.html
sed -n '8645,8905p' templates/index.html
sed -n '10240,10490p' templates/index.html
sed -n '10620,10730p' templates/index.html
sed -n '11565,11660p' templates/index.html
rg -n 'function _clampShirleyIter|function _autoFitRestore|function updatePeak|function updateRSF|function updatePlot|fromJSON\\(' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
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
function _peakArea(p, be) {
  const step = be.length > 1 ? Math.abs(be[1] - be[0]) : 1;
  // evalPeakArray(), not a per-point evalPeak map: for LACX with caM > 0,
  // only the array evaluator applies the shape's Gaussian convolution —
  // evalPeak silently returns the unconvolved base regardless of caM.
  // Feeds the Results panel/sidebar Area+% and the CSV/XLSX export.
  return evalPeakArray(be, p).reduce((s, y) => s + y, 0) * step;
}

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
  // grid, exactly as renderPeakList already does for its area/percentage column.
  let be = state.fitResult.be;
  if ((!be || !be.length) && typeof getROIData === 'function' && state.rawBE.length) {
    be = getROIData().be;
  }
  if (!be) be = [];
  const areas = state.peaks.map(p => _peakArea(p, be));
  // percentages are over the components the fit DID determine
  const totalArea = areas.reduce((s, v, i) => s + (_isUnsupported(state.peaks[i]) ? 0 : v), 0);
  const unsupportedPeaks = state.peaks.filter(p => _isUnsupported(p));

  state.peaks.forEach((p, i) => {
    const pct = totalArea > 0 ? (areas[i] / totalArea * 100) : 0;
    const par = stderrMap[String(p.id)] || {};
    const centerSE = par.center ? par.center.stderr : null;
    const fwhmSE   = par.fwhm   ? par.fwhm.stderr   :
                     par.fwhm_l ? par.fwhm_l.stderr  : null;
    if (_isUnsupported(p)) {
      // the fit did not determine this component: no centre, width or sigma is reported
      html += `<tr class="unsupported-row" data-peak-id="${p.id}" style="color:var(--text3)">
      <td><span style="display:inline-block;width:8px;height:8px;border-radius:2px;background:${p.color};margin-right:5px;opacity:.4"></span>${_escHtml(p.name)} ${_unsupportedBadge(p.id)}</td>
      <td style="font-family:var(--mono)">&mdash;</td>
      <td style="font-family:var(--mono)">&mdash;</td>
      <td>${areas[i].toFixed(0)}</td>
      <td>&mdash;</td>
    </tr>`;
      return;
    }
    html += `<tr>
      <td><span style="display:inline-block;width:8px;height:8px;border-radius:2px;background:${p.color};margin-right:5px"></span>${_escHtml(p.name)}</td>
      <td style="font-family:var(--mono)">${fmtVal(p.center, centerSE, 3)} eV</td>
      <td style="font-family:var(--mono)">${fmtVal(p.fwhm, fwhmSE, 3)} eV</td>
      <td>${areas[i].toFixed(0)}</td>
      <td>${pct.toFixed(1)}%</td>
    </tr>`;
  });

  html += '</tbody></table>';
  if (unsupportedPeaks.length) {
    html += `<div class="unsupported-note" style="font-size:11px;line-height:1.5;color:var(--text2);margin-top:6px" title="${_escAttr(_UNSUPPORTED_TIP)}">
      ${unsupportedPeaks.length === 1 ? 'One component is' : unsupportedPeaks.length + ' components are'} <b>${_UNSUPPORTED_LABEL}</b> (${unsupportedPeaks.map(q => _escHtml(q.name)).join(', ')}): with the other components held as fitted, removing ${unsupportedPeaks.length === 1 ? 'it' : 'any one of them'} does not make the fit significantly worse, so this fit did not determine ${unsupportedPeaks.length === 1 ? 'its' : 'their'} position or width. ${unsupportedPeaks.length === 1 ? 'Its' : 'Their'} area is excluded from the percentages and from Quantify.</div>`;
  }
  html += _startsPanelHtml(state.fitResult);

  // Uncertainty warnings (backend fit only). Genuine alarms go in the amber
  // warn-box; intentionally locked params get a neutral info-box so they
  // stop reading as scary regressions after auto-fit locks centers.
  const { warnings: uncWarnings, info: uncInfo } = _validateUncertainties();
  if (uncWarnings.length) {
    html += `<div class="unc-warn-box">
      <div class="uw-title">&#9888; Uncertainty Warnings</div>
      <ul>${uncWarnings.join('')}</ul>
    </div>`;
  }
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
  if (_saveMode === 'fit') _doSaveFit();
  else if (_saveMode === 'spectrum') _doSaveSpectrum();
  else if (_saveMode === 'project') _doSaveProject();
  closeSaveDialog();
}

function saveFit() {
  document.getElementById('save-dropdown').classList.remove('open');
  if (!tabManager.activeId) { notify('No active tab.', 'amber'); return; }
  const tab = tabManager._getTab(tabManager.activeId);
  _openSaveDialog('fit', tab?.name || 'spectrum', '.fit.json', 'Save Fit');
}

function saveSpectrum() {
  document.getElementById('save-dropdown').classList.remove('open');
  if (!tabManager.activeId || !state.rawBE.length) { notify('No spectrum loaded.', 'amber'); return; }
  const tab = tabManager._getTab(tabManager.activeId);
  _openSaveDialog('spectrum', tab?.name || 'spectrum', '.spec.json', 'Save Spectrum');
}

function showProjectDialog() {
  document.getElementById('save-dropdown').classList.remove('open');
  if (!tabManager.tabs.length) { notify('No tabs to save.', 'amber'); return; }
  const ext = tabManager.tabs.length < 5 ? '.proj.json' : '.proj.zip';
  _openSaveDialog('project', 'project', ext, 'Save Project');
}

// ── 1. Save Fit (v1) ────────────────────────────────
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
    statistics: stats,
    notes: tab.notes || '',
    manualAnchors: tab.manualAnchors || [],
    modelProvenance: tab.modelProvenance || null,
  };

  const fname = document.getElementById('save-fname').value.trim() || 'spectrum';
  _downloadBlob(
    new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'}),
    fname + '.spec.json'
  );
  notify('Spectrum + fit saved.', 'green');
}

// ── 3. Save Project (v3) ─────────────────────────────
async function _doSaveProject() {
  tabManager._syncActiveToRecord();
  const sampleName = document.getElementById('proj-sample').value.trim();
  const instrument = document.getElementById('proj-instrument').value.trim();
  const fname = document.getElementById('save-fname').value.trim() || 'project';

  // Phase 5: stack tabs now persist. Spectrum tab shape unchanged;
  // stack tabs serialize with stack-specific fields only (entries +
  // visualization state). Source data lives on the spectrum tabs and
  // is reached via entry.sourceTabId at load time.
  const tabs = tabManager.tabs;
  // Size control for the frozen fit grid: BE to 4 decimals, intensities to
  // 6 significant figures — both far beyond instrument resolution. Keep
  // values as JSON numbers: toPrecision returns a STRING, so it must be
  // wrapped in Number() or downstream math silently breaks.
  const _roundBE = (a) => Array.isArray(a) ? a.map(v => Math.round(v * 1e4) / 1e4) : null;
  const _roundIntensity = (a) => Array.isArray(a) ? a.map(v => Number(v.toPrecision(6))) : null;
  const buildTabData = (t) => {
    if (t.isStack) {
      return {
        id: t.id, name: t.name, isStack: true,
        _nextColorIdx: t._nextColorIdx || 0,
        lineWidth: t.lineWidth ?? 1.5,
        verticalOffset: t.verticalOffset ?? 0,
        entries: (t.entries || []).map(e => ({
          id: e.id,
          sourceTabId: e.sourceTabId,
          color: e.color,
          visible: !!e.visible,
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
    // per-peak confidence) must ride peak-level fields (the spread channel,
    // like _backendParams/_confidence), never this namespace.
    if (t.analysis != null) rec.analysis = t.analysis;
    return rec;
      // Normalize be/inten → rawBE/rawIntensity for _loadSpectrumFile
      if (!data.rawBE && data.be) data.rawBE = data.be;
      if (!data.rawIntensity && data.inten) data.rawIntensity = data.inten;
      _loadSpectrumFile(data, file.name); return;
    }
    if (hasPeaks) {
      if (!_ownerActive(owner)) { notify('Fit file not applied — the tab changed while the file was being read.', 'amber'); return; }
      _applyFitJSON(data); return;
    }

    // No recognized structure — try as spectral data (CSV-like)
    _loadSpectralFile(file);
  } catch (err) {
    notify('Failed to load file: ' + err.message, 'red');
  }
}

async function handleSessionLoad(event) {
  const file = event.target.files[0];
  if (!file) return;
  event.target.value = '';
  await _loadSessionFile(file);
}

function _loadSpectrumFile(data, sessionFile) {
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
  // strings); peak ids/links/colors are checked by _peaksLoadError.
  for (const t of (data.tabs || [])) {
    if (!t || typeof t !== 'object') continue;
    if (t.id != null && !_SLUG_ID_RE.test(String(t.id))) {
      notify('Project not loaded: tab id ' + JSON.stringify(t.id).slice(0, 60)
  const d = new Array(n).fill(0);
  for (let i = 1; i < n - 1; i++) {
    const dx = be[i+1] - be[i-1];
    if (Math.abs(dx) > 1e-10) d[i] = (intensity[i+1] - intensity[i-1]) / dx;
  }
  d[0] = d[1]; d[n-1] = d[n-2];
  return d;
}

// ═══════════════════════════════════════════════════
// RUNS TEST — residual randomness diagnostic
// ═══════════════════════════════════════════════════
// R-FACTOR (reliability factor)
// R = Σ|residual| / Σ|data| × 100%
// ═══════════════════════════════════════════════════
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
}

function _updateROIDisplay(roiRange) {
  const el = document.getElementById('sb-roi');
  if (!el) return;
  if (!roiRange) { el.textContent = ''; return; }
  el.textContent = `ROI: ${roiRange.min}\u2013${roiRange.max} eV`;
}

const _LOCALFIT_TOOLTIP = "Statistic of the local (in-page) fit. Since unit W1 (2026-09) the local engine is Poisson-weighted like the server, so its \u03c7\u00b2\u1d63 is comparable with the server's, but it gives no parameter uncertainties and can differ from the server fit for LA components (m held at its start locally) or where the model has several minima. Local results saved earlier were unweighted and are labelled 'Residual variance'. Run Fit with the server available for a reportable result.";
const _CHISQ_TOOLTIP = "Reduced chi-squared (\u03c7\u00b2\u1d63) measures the goodness of fit weighted by data uncertainty. Computed within the ROI range.\n\n\u2022 \u03c7\u00b2 \u2248 1.0 = ideal fit (residuals match expected noise)\n\u2022 \u03c7\u00b2 >> 1 = poor fit or underestimated uncertainties\n\u2022 \u03c7\u00b2 << 1 = possible overfitting or overestimated uncertainties\n\nNote: a low \u03c7\u00b2 does not guarantee a correct model \u2014 always check the R-factor and visually inspect residuals.";

// Wire up custom tooltip for data-xps-tip elements (R-factor, chi-squared, etc.)
(function () {
  const DELAY = 300;
  let timer = null;
  document.addEventListener('mouseenter', function (e) {
    const el = e.target instanceof Element ? e.target.closest('[data-xps-tip]') : null;
    if (!el) return;
    clearTimeout(timer);
    timer = setTimeout(() => {
      const tip = document.getElementById('xps-tooltip');
3403:  fromJSON(data) {
4665:function _clampShirleyIter() {
5990:function updatePeakParam(id, key, value) {
6994:function _autoFitRestore(snap, owner) {
9533:function updatePlot() {
10575:  tabManager.fromJSON(data);

exec
/bin/zsh -lc "sed -n '9530,9628p' templates/index.html
sed -n '5975,6078p' templates/index.html
sed -n '3400,3510p' templates/index.html
sed -n '4658,4678p' templates/index.html
sed -n '6955,7065p' templates/index.html
rg -n 'function renderEmptyChart|function onRSFInputChange|fitResult\\.(be|bgSubtracted|bgIntensity)\\s*=' templates/index.html
cat package.json 2>/dev/null
sed -n '1,85p' tests/js/stale_statistics.test.js" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
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
  // result over a replaced model): the envelope is then the current peaks
  const fittedYBacked = haveFit && state.fitResult.fittedY &&
                        state.fitResult.fittedY.length === plotBE.length &&
                        _statsLiveState() !== 'stale'
                        ? state.fitResult.fittedY : null;
  const rawResiduals = fittedYBacked
    ? plotInten.map((v, i) => v - fittedYBacked[i])
    : bgSubtracted.map((v, i) => v - modelFull[i]);
  // Percentage residuals: ((data - fit) / data) × 100, clamped to ±100%
  const residuals = rawResiduals.map((r, i) => {
    const d = fittedYBacked ? plotInten[i] : bgSubtracted[i];
    if (Math.abs(d) < 1e-10) return 0;
    return Math.max(-100, Math.min(100, (r / d) * 100));
  });

  const datasets = [];

  // Bkgrd Sub view: redraws the chart with the background subtracted.
  // The flag is read once per updatePlot() call so all dataset branches
  // see a consistent value. _isBgSubViewActive() is defensive — it
  // returns false if bg-type is "none" even when the pill is checked.
  const bgSubView = _isBgSubViewActive();

  // Individual peaks drawn first (bottom layer) — frozen to fit range after fit
  const showFill = document.getElementById('show-fill').checked;
  if (showIndividual && plotBE.length) {
    if (showFill) {
      // First add invisible background-level datasets as fill targets
      for (let pi = 0; pi < state.peaks.length; pi++) {
        const p = state.peaks[pi];
        datasets.push({
          label: '_bg_' + p.id,
          data: plotBE.map((b, i) => ({ x: b, y: bgSubView ? 0 : plotBG[i] })),
          borderColor: 'transparent',
// A ratio of 0 is not physically meaningful for a linked multiplet anyway —
// if the satellite truly has no intensity, it should not be linked.
function _onLinkRatioInput(id, rawVal) {
  const child = getPeak(id);
  if (!child || !child.linked) return;
  const parent = getPeak(child.linked);
  if (!parent) return;
  let r = parseFloat(rawVal);
  if (!isFinite(r) || r < 0.01) r = 0.01;
  if (r > 2) r = 2;
  child.linkRatio = r;
  child.amplitude = parent.amplitude * r;
  updatePeakParam(id, 'amplitude', child.amplitude);
}

function updatePeakParam(id, key, value) {
  _pushUndoDebounced();
  const p = getPeak(id);
  if (!p) return;
  // asymmetry: clamp to the backend's own bound (fitting.py np.clip(asymmetry,
  // 0, 1)) — a plain assignment let out-of-range values (e.g. pasted/loaded)
  // sit on the peak until a backend fit result overwrote them.
  if (key === 'asymmetry') value = Math.max(0, Math.min(1, value));
  p[key] = value;

  const syncKeys = ['center','amplitude','fwhm','shape','glMix','asymmetry','dsAlpha','dsGamma','laAlpha','laBeta','laM','caAlpha','caBeta','caM'];
  if (syncKeys.includes(key)) {
    // Resolve canonical parent: if p is a child, find its parent first
    let parent = p.linked ? getPeak(p.linked) : p;
    if (!parent) parent = p;

    if (p.linked && parent) {
      // p is a child — back-propagate changed value to parent
      if (key === 'center') parent.center = p.center - p.linkOffset;
      else if (key === 'amplitude') {
        // Only divide back to the parent when the ratio is meaningfully >0.
        // Otherwise (child was zeroed or ratio is tiny) leave the parent alone.
        if (p.linkRatio && p.linkRatio > 1e-6) {
          parent.amplitude = p.amplitude / p.linkRatio;
        }
      }
      else parent[key] = p[key];
      renderPeakControls(parent);
    }

    // Forward-propagate from parent to all children (including p if it is one)
    for (const child of state.peaks.filter(q => q.linked === parent.id)) {
      if (key === 'center') child.center = parent.center + child.linkOffset;
      else if (key === 'amplitude') child.amplitude = parent.amplitude * child.linkRatio;
      else child[key] = parent[key];
      if (child.id !== id) renderPeakControls(child);
    }
  }
  _invalidateFittedY();
  updatePlot();
}

function toggleLock(id, key, btn) {
  const p = getPeak(id);
  if (!p) return;
  p[key] = !p[key];
  btn.className = 'lock-btn' + (p[key] ? ' locked' : '');
  btn.innerHTML = p[key] ? '&#x1f512;' : '&#x1f513;';
  btn.title = (p[key] ? 'Unlock' : 'Lock') + ' during fitting';
  _updateLockAllBtn();
  _refreshStartsEvidence(true);      // a lock is part of the fitted model
}

const LOCK_ALL_KEYS = ['fixCenter', 'fixFwhm', 'fixAmplitude', 'fixAsymmetry', 'fixGlMix', 'fixDsAlpha', 'fixDsGamma'];

function _lockAllStats() {
  let locked = 0, total = 0;
  for (const p of state.peaks) {
    if (p.linked) continue;
    for (const k of LOCK_ALL_KEYS) {
      total++;
      if (p[k]) locked++;
    }
  }
  return { locked, total };
}

function toggleAllLocks() {
  if (!state.peaks.length) return;
  const { locked, total } = _lockAllStats();
  // Majority unlocked → lock all; majority locked → unlock all
  const newVal = locked <= total / 2;
  for (const p of state.peaks) {
    if (p.linked) continue;
    for (const k of LOCK_ALL_KEYS) p[k] = newVal;
  }
  renderPeakList();
  _refreshStartsEvidence(true);
}

function _updateLockAllBtn() {
  const wrap = document.getElementById('peak-lock-all-wrap');
  const btn = document.getElementById('btn-lock-all');
  if (!wrap || !btn) return;
  const hasLockable = state.peaks.some(p => !p.linked);
  if (!hasLockable) { wrap.style.display = 'none'; return; }
  wrap.style.display = '';
  const { locked, total } = _lockAllStats();
  if (locked > total / 2) {
    };
  }

  fromJSON(data) {
    if (data.version === 1 || !data.tabs) {
      // v1 backward compat: apply settings to the ACTIVE tab only
      // Other tabs are preserved — this just restores peaks/background/CC
      if (!this.activeId || !state.rawBE.length) {
        notify('Load a spectrum file first, then load the v1 setup.', 'amber');
        return;
      }
      const active = this._getTab(this.activeId);
      if (!active) return;

      // Audit F1/F4/F5: reject unsafe peak ids/links/colors before rendering.
      const pe = _peaksLoadError(data.peaks);
      if (pe) { notify('Fit not loaded: ' + pe + '.', 'red', true); return; }

      // Import is an undoable transaction on this record: the previous model
      // (and its averaging) is one Ctrl-Z away, redo is cleared, and a Find
      // Peaks result produced for the previous model no longer applies.
      pushUndo({ endpointAvg: document.getElementById('bg-endpoint-avg')?.value });
      active.findPeaks = null;
      // Apply peaks. Parameters imported onto this tab's data carry no verdict:
      // "not supported by the data" was about the data they were fitted to.
      state.peaks = _normalizePeaksCRef((data.peaks || []).map(p => ({...p, support: null})));
      state.nextId = data.nextId || (Math.max(0, ...state.peaks.map(p => p.id)) + 1);
      state.fitResult = null;
      active.peaks = state.peaks;
      active.nextId = state.nextId;
      active.fitResult = null;
      // Provenance of the imported parameters (unit A0): a model saved from
      // a local (unweighted) fit stays a starting point, not a result.
      active.modelProvenance = _isLocalProvenance(data.fitStatistics)
        ? { ...data.fitStatistics, importedFrom: 'fit.json' } : null;

      // Apply charge correction
      if (data.chargeCorrection) {
        state.ccShift = data.chargeCorrection.shift || 0;
        active.ccShift = state.ccShift;
        active.ui.ccMethod = data.chargeCorrection.method || 'none';
        active.ui.ccObs = data.chargeCorrection.observedBE || '';
      }

      // Fit loaded from external file — CC not verified for this spectrum
      active.chargeVerified = false;
      this._updateCCVerifiedUI(false);

      // Endpoint averaging is resolved whether or not the file carries a
      // background block: v1 files written before 2026-09-08 never recorded
      // it (those fits were made at 1), and an accepted peaks-only file must
      // not inherit the fresh target tab's new-tab default either (Codex
      // round 1, both runs).
      active.ui.endpointAvg = (data.background && data.background.endpointAvg) || LEGACY_ENDPOINT_AVG;

      // Apply background
      if (data.background) {
        active.ui.bgType = data.background.type || 'shirley';
        active.ui.bgStart = data.background.start || '';
        active.ui.bgEnd = data.background.end || '';
        active.ui.shirleyIter = data.background.shirleyIter || '5';
        // bgSubtractedView is missing from pre-feature saves → falsy default
        active.ui.bgSubtractedView = !!data.background.bgSubtractedView;
      }

      // Apply ROI
      if (data.roi) {
        active.ui.roiMin = data.roi.min || '';
        active.ui.roiMax = data.roi.max || '';
      }

      // Apply notes
      if (data.notes) active.notes = data.notes;
      const notesEl = document.getElementById('spectrum-notes');
      if (notesEl) notesEl.value = active.notes || '';

      // Apply manual anchor points
      if (data.manualAnchors) active.manualAnchors = data.manualAnchors;

      // Restore DOM from updated ui and re-render
      this._restoreUI(active.ui);
      renderPeakList();
      updatePlot();
      renderResults();   // installs the imported model's designation (or the plain placeholder) and clears stale widgets
      return;
    }

    // v2+ multi-tab data — route through _loadProjectJSON (has confirmation)
    _loadProjectJSON(data);
  }

  // ── Tab bar rendering ───────────────────────────

  renderTabBar() {
    const bar = document.getElementById('spectrum-tab-bar');
    if (!bar) return;
    bar.innerHTML = '';
    for (const tab of this.tabs) {
      const el = document.createElement('div');
      el.className = 'sp-tab'
        + (tab.id === this.activeId ? ' active' : '')
        + (tab.isStack ? ' is-stack' : '');
      const tabId = tab.id;

      const inner = document.createElement('span');
      inner.innerHTML =
        '<span class="sp-tab-dot" style="background:' + tab.color + '"></span>' +
        '<span>' + this._esc(tab.name) + '</span>' +
        '<span class="sp-tab-close" title="Close tab">&times;</span>';
      el.appendChild(inner);

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

// Apply a successful auto-fit result. Mutates state and DOM so the tab
// ends in a self-consistent corrected frame with graphite at exactly 284.50.
// Pure decision: given (id, area) pairs and graphite's id, decide whether
// to emit the < 40% area-fraction warning toast. Returns null on no-warning,
// or { fractionPct, warning } on warning. Boundary: '< 0.40' so 0.40 itself
// does NOT warn.
//
// This logic is intentionally state-free so the Python port test in
// /tmp/test_autofit_decide_warning.py can validate it without simulating
4657:  if (state.fitResult) state.fitResult.bgIntensity = null;
8925:function onRSFInputChange(peakId, val) {
10031:function renderEmptyChart() {
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
    const getROIData = () => ({ be: [1, 2, 3] });
    const getPeak = id => state.peaks.find(p => p.id === id);
    const _UNSUPPORTED_LABEL = 'not supported by the data', _UNSUPPORTED_TIP = '';
    ${src}
    return { ${[...STATE_FNS, '_applyStatDisplay', '_updateRFactorUI', 'renderResults', '_validateUncertainties'].join(', ')} };
  `)(doc, state, env);
  return { api, doc, state, env };
}

function serverResult(key) {

exec
/bin/zsh -lc 'node --test --test-reporter=spec tests/js/stale_statistics.test.js tests/js/fit_acceptance.test.js tests/js/local_lm_descent.test.js tests/js/scattered_starts.test.js tests/js/unsupported_components.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 exited 1 in 5905ms:
✔ A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown (8.646508ms)
✔ a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser (6.328332ms)
✔ a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay (2.839551ms)
✔ a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay (8.375901ms)
✔ a converged backend result is applied (sanity) (2.380218ms)
✔ the engine/objective labels of a fit result survive spectrum and project save/load (0.646203ms)
✔ an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback (2.720556ms)
✔ an HTTP 502 on the upload is a server failure, not a transport failure (2.551321ms)
✔ uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id (1.674471ms)
✔ every consumer that prints the goodness-of-fit statistic routes through the statistic identity (0.790624ms)
✔ uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure (0.598818ms)
✔ a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown (1.303374ms)
✔ starting-point helpers: keyed on the persisted objective, weighted results untouched (3.00215ms)
✔ Quantify shows the starting-point banner for a local result and not for a weighted one (3.880706ms)
✔ every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels (1.50724ms)
✔ project save derives the designation from the objective for an older local result lacking the new fields (6.578964ms)
✔ stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately (0.769608ms)
✔ _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none (2.701234ms)
✔ history preview glow is keyed on the dataset flag, not the label text (0.563703ms)
✔ spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation (0.432358ms)
✔ _applyStatDisplay clears header, tooltip, caption and value together on local → none (3.57374ms)
✔ _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result (1.82932ms)
✔ fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it (2.478852ms)
✔ undo/redo snapshots carry and restore model provenance (4.260095ms)
✔ round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it (0.979667ms)
✔ _provenanceOf derives a designation from a live local result, and undo snapshots use it (2.313672ms)
✔ batch propagation copies the source model provenance onto each target (cleared again only by a successful fit) (0.298125ms)
✔ the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise (2.229016ms)
✔ round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance (0.555924ms)
✔ the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview (2.207895ms)
✔ the sidebar banner is sticky at the top of the scrolling panel body (0.234007ms)
✔ the sidebar banner shows on a stack tab whose visible entries draw a local source fit (2.332341ms)
✔ every stack chart repaint path refreshes the sidebar designation before any early return (0.332663ms)
✔ closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab (0.194611ms)
✔ W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched (2.356144ms)
✔ TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result (3.880871ms)
✔ adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success (2.766701ms)
✔ adoption: a transport failure does NOT fall back to the local engine (it would start from the live model) (2.391545ms)
✔ adoption: a tab switch during the re-fit discards it and leaves the originating model as it was (2.163703ms)
✔ adoption: success records the choice, the starts evidence and the key of the model it describes (2.306089ms)
✔ an ordinary Run Fit on one unlinked component does not ask for the starts check (2.600491ms)
✔ a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key) (2.676012ms)
✔ a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays) (5.42666ms)
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
✔ A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters (1195.452086ms)
✔ A01 replay: the linked U 4f pair also descends (232.731479ms)
✔ noiseless Gaussian: amplitude 10 started at 5 is recovered (12.836623ms)
✔ acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result (8.827912ms)
✔ a local fit result is Poisson-weighted: objective, weighting and the designated statistic text (13.604799ms)
✔ bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall (9.784022ms)
✔ bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit (9.136735ms)
✔ a weak component the data DO hold is no longer forced up to an amplitude of 1 (9.172417ms)
✔ derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width) (41.766325ms)
✔ derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum (24.785887ms)
✔ a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence (8.785492ms)
✔ linked child follows its parent even when the parent width is locked (behaviour documented in unit A0) (12.6887ms)
✔ round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point (11.151045ms)
✔ round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum (9.926632ms)
✔ round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data) (10.488719ms)
✔ A01 replay targets converge to constrained stationary points (C1s and U 4f) (1334.545452ms)
✔ round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen (59.404918ms)
✔ round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude (20.487998ms)
✔ round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point (12.005133ms)
✔ round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point (74.603855ms)
✔ round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data) (1171.718937ms)
✔ round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window) (20.732446ms)
✔ round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one (10.628292ms)
✔ weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one (8.374052ms)
✖ server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets) (1380.044273ms)
✔ the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom (23.170059ms)
✔ an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy (28.521976ms)
✔ an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free (23.543411ms)
✔ round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV (9.150479ms)
✔ round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001 (19.291977ms)
✔ recovery from an amplitude of exactly zero (the new floor is not a trap) (18.335471ms)
✔ summary wording: counts of STARTS and of SOLUTIONS, never certification (17.73109ms)
✔ no alternative: one line, no table (11.715763ms)
✔ alternatives: "Your fit" first, own areas per component, the moved component named and coloured (8.377576ms)
✔ RED band: applying asks first and NAMES the component and the distance (8.422314ms)
✔ adoption never writes the live model itself: the alternative is only the START of a fit, and the choice rides along (7.754016ms)
✔ below the red band there is no dialog (24.282557ms)
✔ a locked parameter is never moved by an alternative (7.325667ms)
✔ evidence is bound to the fitted model — a peak deleted: the panel says so and nothing can be applied (8.108369ms)
✔ evidence is bound to the fitted model — a shape changed (GL -> DS) and the centre moved: the panel says so and nothing can be applied (9.056624ms)
✔ evidence is bound to the fitted model — a lock toggled: the panel says so and nothing can be applied (8.853061ms)
✔ evidence is bound to the fitted model — a link added: the panel says so and nothing can be applied (9.690988ms)
✔ evidence is bound to the fitted model — an undo that restored other values: the panel says so and nothing can be applied (7.85302ms)
✔ evidence is bound to the fitted model — an auto-fit asymmetry bound changed: the panel says so and nothing can be applied (8.44085ms)
✔ evidence is bound to the fitted model — the background type changed: the panel says so and nothing can be applied (7.402601ms)
✔ evidence is bound to the fitted model — the background window moved: the panel says so and nothing can be applied (6.554746ms)
✔ evidence is bound to the fitted model — endpoint averaging changed: the panel says so and nothing can be applied (6.928923ms)
✔ evidence is bound to the fitted model — the ROI changed: the panel says so and nothing can be applied (6.534447ms)
✔ evidence is bound to the fitted model — a manual anchor was added: the panel says so and nothing can be applied (6.731951ms)
✔ evidence is bound to the fitted model — the charge correction changed: the panel says so and nothing can be applied (6.707714ms)
✔ a cosmetic edit (name, colour, visibility) does not invalidate the evidence (6.568378ms)
✔ preview overlays a COPY and toggles off; the model is untouched (7.160839ms)
✔ a record is keyed like the live tab (project save of a non-active tab) (6.59347ms)
✔ what is saved: the counts, never the alternatives' parameter sets (7.003585ms)
✔ a loaded summary (no parameter sets) still renders its line and offers nothing to apply (6.526176ms)
✔ wiring: the trigger is decided with the other request inputs, BEFORE the first await (9.875263ms)
✔ persistence and export sites carry the summary (1.87125ms)
✔ the tooltip reports what the starts found and claims nothing about the data (0.506513ms)
✔ the recorded adoption is worded once, for the exports (6.709434ms)
✔ one accessor classifies a result against a key: none / unverified / current / stale (16.381669ms)
✔ the key is the step (b) key: F1 adds no second binding mechanism and no new key field (3.802266ms)
✔ Results panel, current: statistic, RMSE, R and sigma are shown (8.936029ms)
✔ Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma (6.956851ms)
✔ Results panel, unverified (older save, no key): values shown with a plain note (7.048821ms)
✔ status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched (6.724487ms)
✔ the stored fitted curve is never drawn, saved or stacked as the fit once stale (2.697125ms)
✔ saves keep the key and say plainly when the statistics are stale or unverified (2.018866ms)
✔ CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma (15.603573ms)
✔ XLSX: stale writes a WARNING row instead of the statistic, and no sigma (4.293551ms)
✔ TSV: stale says the Model / Residual columns are the current, unfitted model (6.589895ms)
✔ the refresh re-renders Results only when its rendered state differs (2.601031ms)
✔ an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not (2.623696ms)
✔ Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone (3.242273ms)
✔ Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies (6.099263ms)
✔ reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model (1.457686ms)
✔ the twin reproduces the server verdict on real responses, and defers to the server field when present (10.932664ms)
✔ _applySupport writes every peak, follows ancestry to the root, stamps the fit key, and leaves null where the response says nothing (5.614388ms)
✔ the verdict applies only to the model and context it was computed for (4.753176ms)
✔ the local engine computes the same statistic from its own residuals (5.920282ms)
✔ sidebar card: badge; centre and width shown as a dash; area % excluded and the others renormalised (5.899555ms)
✔ results table: greyed row, no centre / width / sigma, area kept, percentage dash, and the note beneath (11.188862ms)
✔ uncertainty panel: one rule-0 warning for the component, no per-parameter alarms and no "locked" note for it (4.38759ms)
✔ Quantify: excluded from the body, listed beneath with the reason; total and percentages over the rest (5.454628ms)
✔ CSV / XLSX export: Status column, suppressed cells, At% empty, WARNING line (8.976407ms)
✔ publication figure: no label at the (zero) component, legend entry says so; chart and stack labels say so (2.239659ms)
✔ write-back: a server result sets support; the local engine and a propagated model reset it (1.387107ms)
✔ persistence: support travels with the peak object through every save (the peak is spread whole) (0.841068ms)
✔ CSV / XLSX: an unsupported DS+G component exports no width of any kind (beta, m) (4.894746ms)
✔ the scattered-starts table: an unsupported component shows neither area % nor a move in "Your fit", and is not the largest move (5.83035ms)
✔ exports: a stale or keyless verdict is "not established", never "supported" (8.339316ms)
✔ Auto-Fit finalisation (locks, charge shift) keeps its own verdicts: _restampSupport, called after the locks (4.119714ms)
✔ a .fit.json import onto this tab's data carries no verdict (0.120731ms)
✔ _isUnsupported is never handed an array index as its key (Array.filter passes one) (4.309678ms)
✔ a key change re-renders every consumer of the verdict — each compared with ITS OWN rendering (2.992011ms)
✔ stack tabs judge a source component against the SOURCE record's key (4.008639ms)
✔ "Your fit" percentages are over supported components; an empty Quantify shows no 100 % (13.270806ms)
✔ the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict (5.352182ms)
ℹ tests 140
ℹ suites 0
ℹ pass 139
ℹ fail 1
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 5958.711041

✖ failing tests:

test at tests/js/local_lm_descent.test.js:455:1
✖ server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets) (1380.044273ms)
  Error: Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/tests/js/local_lm_server_parity_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
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
  
      at genericNodeError (node:internal/errors:983:15)
      at wrappedFn (node:internal/errors:537:14)
      at checkExecSyncError (node:child_process:916:11)
      at execFileSync (node:child_process:952:15)
      at TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/tests/js/local_lm_descent.test.js:468:31)
      at Test.runInAsyncScope (node:async_hooks:214:14)
      at Test.run (node:internal/test_runner/test:1047:25)
      at Test.processPendingSubtests (node:internal/test_runner/test:744:18)
      at Test.postRun (node:internal/test_runner/test:1173:19)
      at Test.run (node:internal/test_runner/test:1101:12) {
    status: 1,
    signal: null,
    output: [ null, '', `Traceback (most recent call last):\n  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/tests/js/local_lm_server_parity_backend.py", line 12, in <module>\n    import fitting  # noqa: E402\n    ^^^^^^^^^^^^^^\n  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/fitting.py", line 33, in <module>\n    from lmfit import Model, Parameters\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>\n    from .confidence import conf_interval, conf_interval2d\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>\n    from .minimizer import MinimizerException\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>\n    from .parameter import Parameter, Parameters\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>\n    from .jsonutils import decode4js, encode4js\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>\n    import dill\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>\n    from .session import (\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>\n    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())\n                               ^^^^^^^^^^^^^^^^^^^^^\n  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir\n    return _os.fsdecode(_gettempdir())\n                        ^^^^^^^^^^^^^\n  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir\n    tempdir = _get_default_tempdir()\n              ^^^^^^^^^^^^^^^^^^^^^^\n  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir\n    raise FileNotFoundError(_errno.ENOENT,\nFileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics']\n` ],
    pid: 65089,
    stdout: '',
    stderr: `Traceback (most recent call last):\n  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/tests/js/local_lm_server_parity_backend.py", line 12, in <module>\n    import fitting  # noqa: E402\n    ^^^^^^^^^^^^^^\n  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/fitting.py", line 33, in <module>\n    from lmfit import Model, Parameters\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>\n    from .confidence import conf_interval, conf_interval2d\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>\n    from .minimizer import MinimizerException\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>\n    from .parameter import Parameter, Parameters\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>\n    from .jsonutils import decode4js, encode4js\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>\n    import dill\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>\n    from .session import (\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>\n    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())\n                               ^^^^^^^^^^^^^^^^^^^^^\n  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir\n    return _os.fsdecode(_gettempdir())\n                        ^^^^^^^^^^^^^\n  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir\n    tempdir = _get_default_tempdir()\n              ^^^^^^^^^^^^^^^^^^^^^^\n  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir\n    raise FileNotFoundError(_errno.ENOENT,\nFileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics']\n`
  }

exec
/bin/zsh -lc "git diff main..HEAD -- templates/index.html | head -300
sed -n '10025,10060p' templates/index.html
sed -n '8910,8950p' templates/index.html
rg -n 'chiReduced|rFactor|\\.rmse|\\.chi\\b|_buildStderrMap' templates/index.html | tail -90" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Y9ufJrWE' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-P0uDeDiK' (errno=Operation not permitted)
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
    mainCanvas._dragZoomAttached = true;
  }

  document.getElementById('mainChart').ondblclick = () => resetAllZoom();
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
3252:    if (state.fitResult && state.fitResult.rFactor == null && _statsLiveState() !== 'stale') {
3253:      state.fitResult.rFactor = _computeRFactor(state.fitResult);
3255:    _updateRFactorUI(state.fitResult ? state.fitResult.rFactor : null);
7337:  const chiReduced = stats.reduced_chi_square || 0;
7341:    chi: chiReduced * Math.max(1, be2.length - state.peaks.length * 3),
7342:    chiReduced, rmse,
7349:  state.fitResult.rFactor = _computeRFactor(state.fitResult);
7354:    fq.textContent = 'χ²ᵣ = ' + chiReduced.toFixed(2);
7360:  if (sbChi) sbChi.textContent = chiReduced.toFixed(3);
7363:  if (typeof _updateRFactorUI === 'function') _updateRFactorUI(state.fitResult.rFactor);
7554:    notify('Auto-fit complete. χ²ᵣ = ' + (state.fitResult?.chiReduced?.toFixed(3) || '?'), 'green');
7701:  if (typeof _updateRFactorUI === 'function') _updateRFactorUI(state.fitResult ? state.fitResult.rFactor : null);
7876:  _historyPreview = { snapId: key, altKey: state.fitResult.startsModelKey, peaks, fitResult: { chiReduced: alt.chi2r } };
8037:    const chiReduced = stats.reduced_chi_square || 0;
8040:    state.fitResult = { chi: chiReduced * Math.max(1, be.length - state.peaks.length * 3),
8041:                        chiReduced, rmse, be, bgSubtracted, bgIntensity, backendResult,
8049:    state.fitResult.rFactor = _computeRFactor(state.fitResult);
8052:    _updateRFactorUI(state.fitResult.rFactor);
8055:    notify('Fit complete. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3), 'green');
8186:           weighting: fr.weighting || null, chiReduced: fr.chiReduced ?? null,
8195:  return _fitStatLabel(fr) + ' = ' + fr.chiReduced.toFixed(2) + tag;
8211:  if (fr && Number.isFinite(fr.chiReduced) && st === 'stale') {
8215:  } else if (fr && Number.isFinite(fr.chiReduced)) {
8218:    if (sb) sb.textContent = fr.chiReduced.toFixed(3);
8563:  const chiReduced = chi / dof;                       // weighted reduced chi-square, as lmfit's redchi
8585:  state.fitResult = { chi, chiReduced, rmse, be, bgSubtracted, bgIntensity, roiRange,
8590:  state.fitResult.rFactor = _computeRFactor(state.fitResult);
8594:  _updateRFactorUI(state.fitResult.rFactor);
8603:         '. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3) + ' (Poisson-weighted; no uncertainties). Starting point only: run Fit before reporting.', 'amber');
8605:  return { success: true, engine: 'local', iterations, acceptedSteps, chiReduced, certifyRestarts };
8637:function _buildStderrMap(fitResult) {
8675:  const { chiReduced, rmse, backendResult } = state.fitResult;
8679:  const stderrMap = _stale ? {} : _buildStderrMap(state.fitResult);
8704:        <div style="font-family:var(--mono);font-size:16px;color:${_stale ? 'var(--text3)' : _statIsChi ? (chiReduced<2?'var(--green)':chiReduced<5?'var(--amber)':'var(--red)') : 'var(--text)'}">${_stale ? _dash : chiReduced.toFixed(3)}</div>
8715:    ${_stale ? '' : _renderRFactorPanel(state.fitResult.rFactor)}
10299:      chiReduced: state.fitResult.chiReduced ?? null,
10356:    chi: state.fitResult.chi,
10357:    chiReduced: state.fitResult.chiReduced,
10358:    rmse: state.fitResult.rmse,
10359:    rFactor: state.fitResult.rFactor || null,   // F1: the fit's own R (restored only while current)
10446:        chi: t.fitResult.chi, chiReduced: t.fitResult.chiReduced,
10447:        rmse: t.fitResult.rmse, fittedY: t.fitResult.fittedY || null,
10448:        rFactor: t.fitResult.rFactor || null,   // F1: the fit's own R, not one recomputed from edited peaks on reload
10684:    const fr = { chi: data.statistics.chi, chiReduced: data.statistics.chiReduced, rmse: data.statistics.rmse };
10690:    if (data.statistics.rFactor && data.statistics.statisticsState !== 'stale') fr.rFactor = data.statistics.rFactor;
11288:      ctx.fillText(statLabel + '\u2009=\u2009' + state.fitResult.chiReduced.toFixed(3) + (_figStats === 'unverified' ? ' (unverified)' : ''),
11450:  const stderrMap = _stats === 'stale' ? {} : _buildStderrMap(state.fitResult);
11465:  const chiStr = state.fitResult.chiReduced.toFixed(4);
11623:  if (rf && state.fitResult && rf === state.fitResult.rFactor && _statsLiveState() === 'stale') {
11700:  const stderrMap = _buildStderrMap(state.fitResult);
12273:                   chi: ok && Number.isFinite(outcome.chiReduced) ? outcome.chiReduced : null,
12289:    ? `<div class="prop-row">${_escHtml(r.name)}: converged &mdash; &#967;&#178;<sub>r</sub> = ${r.chi != null ? r.chi.toFixed(3) : 'n/a'} (local fit: a starting point, not a reportable result)${roiNote(r)}</div>`
14024:  const chi = state.fitResult.chiReduced;
14041:    rFactor: state.fitResult.rFactor ?? null,
14090:        <div class="hist-row-meta">${s.timestamp} &middot; ${(s.peaks || []).length} peak${(s.peaks || []).length !== 1 ? 's' : ''}${typeof s.chi === 'number' && isFinite(s.chi) ? ' &middot; <span class="hist-row-chi">' + _escHtml(_fitStatLabel(s.fitResult)) + ' = ' + s.chi.toFixed(3) + (_isLocalFit(s.fitResult) ? ' (starting point)' : '') + '</span>' : ''}${typeof s.rFactor === 'number' && isFinite(s.rFactor) ? ', R = ' + s.rFactor.toFixed(1) + '%' : ''}</div>

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\''); const h=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\''); const ls=h.split('\\''\\n'\\'');
function fn(n){let s=ls.findIndex(x=>new RegExp('\\''"'^(async )?function '"'\\''+n+'\\''\\\\('\\'').test(x)),d=0,seen=false;for(let i=s;i<ls.length;i++){for(const c of ls[i]){if(c==='\\''{'\\''){d++;seen=true;}if(c==='\\''}'\\'')d--;}if(seen&&"'!d)return ls.slice(s,i+1).join('"'\\''\\n'\\'');}throw n;}
const c=ls.slice(ls.findIndex(x=>x.startsWith('\\''const _STARTS_MODEL_FIELDS'\\'')),ls.findIndex(x=>x.startsWith('\\''const _STARTS_UI_FIELDS'\\''))+1).join('\\''\\n'\\'');
const names=['\\''_startsModelKey'\\'','\\''_fitKeyCanon'\\'','\\''_sameFitKey'\\'','\\''_statsState'\\'','\\''_startsIfCurrent'\\'','\\''_bgWindowIndices'\\'','\\''computeBackgroundCore'\\'','\\''_applyEndpointAveraging'\\'','\\''shirleyBackground'\\''];
const api=new Function(c+'\\''\\n'\\''+names.map(fn).join('\\''\\n'\\'')+'\\''\\nreturn {'\\''+names.join('\\'','\\'')+'\\''};'\\'')();
const be=Array.from({length:31},(_,i)=>300-i);const y=be.map((x,i)=>20+0.7*i+150*Math.exp(-Math.pow((x-285)/3,2)));const ui={bgType:'\\''shirley'\\'',bgStart:'\\''300'\\'',bgEnd:'\\''270'\\'',shirleyIter:'\\''5'\\'',endpointAvg:'\\''10'\\'',roiMin:'\\''270'\\'',roiMax:'\\''300'\\''};
const a=api._startsModelKey([],ui,0,[]), other={...ui,endpointAvg:'\\''1e1'\\''},b=api._startsModelKey([],other,0,[]);
const bgA=api.computeBackgroundCore(be,y,ui),bgB=api.computeBackgroundCore(be,y,other);
console.log(JSON.stringify({input:['\\''10'\\'','\\''1e1'\\''],requestEndpointAvg:[parseInt(ui.endpointAvg),parseInt(other.endpointAvg)],sameFitKey:api._sameFitKey(a,b),stats:api._statsState({startsModelKey:a},b),startsAccepted:"'!!api._startsIfCurrent({startsModelKey:a,starts:{ran:true}},b),backgroundMaxDifference:Math.max(...bgA.map((v,i)=>Math.abs(v-bgB[i])))}));
for(const fld of ['"'\\''roiMin'\\'','\\''shirleyIter'\\'','\\''endpointAvg'\\''])for(const pair of [['\\''280'\\'','\\''280.0'\\''],['\\''3.5'\\'','\\''3.50'\\''],['\\''10'\\'','\\''1e1'\\''],['\\''16'\\'','\\''0x10'\\''],['\\''280'\\'','\\'' 280'\\''],['\\''280'\\'','\\''280 '\\''],['\\'''\\'','\\''0'\\'']]){const x=api._startsModelKey([],{...ui,[fld]:pair[0]},0,[]),z=api._startsModelKey([],{...ui,[fld]:pair[1]},0,[]);if(api._sameFitKey(x,z)){const parse=fld==='\\''roiMin'\\''?parseFloat:parseInt; if(parse(pair[0])"'!==parse(pair[1]))console.log({fld,pair,parsed:pair.map(s=>parse(s)),incorrectlyEqual:true});}}
for(let i=0;i<2000;i++)api._fitKeyCanon(JSON.stringify({u:[String(i)]}));console.log('"'\\''memoSize'\\'',api._fitKeyCanon._memo.size);'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
{"input":["10","1e1"],"requestEndpointAvg":[10,1],"sameFitKey":true,"stats":"current","startsAccepted":true,"backgroundMaxDifference":2.8044884984296132}
{
  fld: 'roiMin',
  pair: [ '16', '0x10' ],
  parsed: [ 16, 0 ],
  incorrectlyEqual: true
}
{
  fld: 'shirleyIter',
  pair: [ '10', '1e1' ],
  parsed: [ 10, 1 ],
  incorrectlyEqual: true
}
{
  fld: 'endpointAvg',
  pair: [ '10', '1e1' ],
  parsed: [ 10, 1 ],
  incorrectlyEqual: true
}
memoSize 237

codex
Confirmed: changing endpoint averaging from `10` to `1e1` changes the fit input from 10 points to 1, but the new comparator calls the keys equal and leaves statistics current. The actual background arrays differ. The focused suite has 139 passes; its one failure is a Python parity subprocess blocked by the read-only sandbox’s lack of a writable temporary directory. I’m finishing the empty-tab check and testing whether each new behavioral test catches removal of its fix.
exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\''),path=require('\\''path'\\''),{createRequire}=require('\\''module'\\''); const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
async function run(file,pattern,mutate) {
 const cases=[];const req=createRequire(path.resolve(file));let source=fs.readFileSync(file,'\\''utf8'\\'');
 source=source.replace(/const html = fs\\.readFileSync\\(path\\.join\\(__dirname, '\\''\\.\\.\\/\\.\\.\\/templates\\/index\\.html'\\''\\), '\\''utf8'\\''\\);/, '\\''const html = reviewHtml;'\\'');
 const customRequire=n=>n==='\\''node:test'\\''?{test:(name,...args)=>cases.push({name,fn:args.at(-1)})}:req(n);
 new Function('\\''require'\\'','\\''__dirname'\\'','\\''reviewHtml'\\'',source)(customRequire,path.dirname(path.resolve(file)),mutate?mutate(html):html);
 const test=cases.find(c=>pattern.test(c.name));if("'!test)throw Error('"'\\''missing test'\\'');try{await test.fn();return '\\''PASS'\\'';}catch(e){return '\\''FAIL: '\\''+e.message.split('\\''\\n'\\'')[0];}
}
const items=[
 ['\\''fallback'\\'','\\''tests/js/fit_acceptance.test.js'\\'',/"'^a transport failure after the model/,h=>h.replace(/    if '"\\(e && e\\.transportFailure && ctxAtRequest "'!== null['"\\s\\S]*?\\n    }\\n/,'\\'''\\'')],
 ['\\''Auto-Fit'\\'','\\''tests/js/stale_statistics.test.js'\\'',/"'^Auto-Fit discards/,h=>h.replace(/    if '"\\("'!_sameFitKey'"\\(_startsLiveKey\\(\\), ctxAtRequest\\)\\) \\{[\\s\\S]*?_autoFitRestore\\(snap, fittingTab\\);\\n      return;\\n    }\\n/,'\\'''\\'')],
 ['\\''canonical'\\'','\\''tests/js/stale_statistics.test.js'\\'',/"'^an equivalent spelling/,h=>h.replace('"'\\''a === b || _fitKeyCanon(a) === _fitKeyCanon(b)'\\'','\\''a === b'\\'')],
 ['\\''Clear All'\\'','\\''tests/js/stale_statistics.test.js'\\'',/"'^Clear All/,h=>h.replace("(state.fitResult || el.getAttribute('"'\\''data-stats-state'\\''))\",\"state.fitResult\")]
];
(async()=>{for(const [name,file,pattern,mutate]of items){if(mutate(html)===html)throw Error('\\''mutation did not apply '\\''+name);console.log(name,JSON.stringify({baseline:await run(file,pattern),withoutFix:await run(file,pattern,mutate)}));}})();'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 12ms:
Clear All {"baseline":"PASS","withoutFix":"FAIL: the shown result was cleared: back to the empty state"}

exec
/bin/zsh -lc "sed -n '1,115p' tests/js/fit_acceptance.test.js
sed -n '597,653p' tests/js/fit_acceptance.test.js
sed -n '10050,10120p' templates/index.html
sed -n '4645,4668p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
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

test('a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay', async () => {
  const env = makeEnv({ fetchImpl: async () => { throw new TypeError('Failed to fetch'); } });
  // replace the stubbed local fitter with a failing one
  const failing = makeEnv({ fetchImpl: async () => { throw new TypeError('Failed to fetch'); } });
  failing.calls.local = 0;
  // rebuild with a failing runFitLocal
  const dom = failing.dom;
  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n');
  const noop = () => {};
  const owner = { id: 1 };
  const state = failing.state;
  const { runFit } = new Function('document', 'state', 'fetch', 'uploadToBackend', 'notify', 'pushUndo', '_showFitSpinner', '_hideFitSpinner',
    '_opOwner', '_ownerActive', 'getROIData', 'computeBackground', 'peakToBackendSpec', '_getManualAnchors', 'applyBackendResult',
    '_computeRFactor', '_CHISQ_TOOLTIP', '_updateRFactorUI', '_updateROIDisplay', 'renderPeakList', 'updatePlot', 'renderResults',
    '_autoSnapshot', 'runFitLocal', '_snapshotSuppressed', 'console', '_applyStatDisplay', '_activeTab', src + '\nreturn { runFit };')(
    { getElementById: id => (dom[id] ||= { value: '', textContent: '', style: {}, setAttribute() {}, classList: { add(c) { this._c = c; }, remove() { this._c = null; }, _c: null } }), querySelector: () => ({}), querySelectorAll: () => [] },
    state, async () => { throw new TypeError('Failed to fetch'); }, async () => 'sid', noop, noop, noop, noop, () => owner, o => o === owner,
    () => ({ be: state.rawBE.slice(), inten: state.rawIntensity.slice() }), b => b.map(() => 0), p => ({ id: p.id }), () => [], noop,
    () => 0.1, '', noop, noop, noop, noop, noop, noop, () => ({ success: false, message: 'did not converge' }), false, { warn: noop }, noop, () => owner);
  await runFit();
  assert.notEqual(dom['localfit-warn-overlay']?.classList._c, 'open', 'overlay must not claim a local fit was performed');
  void env;
});

test('a converged backend result is applied (sanity)', async () => {
test('adoption: success records the choice, the starts evidence and the key of the model it describes', async () => {
  const starts = { ran: true, n_run: 3, n_converged: 3, n_same_as_fit: 3, n_in_alternatives: 0, n_not_better_elsewhere: 0, alternatives: [] };
  const env = makeEnv({ specImpl: spec, fetchImpl: okResponse({ success: true, statistics: { reduced_chi_square: 1.16 }, residuals: [], fitted_y: [], individual_peaks: [], starts }) });
  await env.runFit({ startPeaks: ALT_START, chosenAlternative: CHOSEN });
  assert.strictEqual(env.calls.applied, 1);
  assert.deepStrictEqual(env.state.fitResult.chosenAlternative, CHOSEN);
  assert.deepStrictEqual(env.state.fitResult.starts, starts);
  assert.strictEqual(typeof env.state.fitResult.startsModelKey, 'string');
});

test('an ordinary Run Fit on one unlinked component does not ask for the starts check', async () => {
  let body = null;
  const env = makeEnv({ fetchImpl: async (url, init) => { body = JSON.parse(init.body); return { ok: true, status: 200, json: async () => ({ success: true, statistics: {}, residuals: [], fitted_y: [], individual_peaks: [] }) }; } });
  await env.runFit();
  assert.strictEqual(body.n_starts, 0);
  assert.strictEqual(env.state.fitResult.chosenAlternative, null);
});


test('a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server\'s statistics, with a fresh evidence key)', async () => {
  let env;
  env = makeEnv({ specImpl: spec, fetchImpl: async () => {
    env.state.peaks[0].center = 290; env.state.peaks[0].fixCenter = true;          // the student edits while waiting
    return { ok: true, status: 200, json: async () => ({ success: true, statistics: { reduced_chi_square: 1.2 }, residuals: [], fitted_y: [], individual_peaks: [] }) };
  } });
  await env.runFit();
  assert.strictEqual(env.calls.applied, 0, 'the result is not applied over the edited model');
  assert.strictEqual(env.state.fitResult.marker, 'previous');
  assert.strictEqual(env.state.peaks[0].center, 290, 'the edit itself is kept');
  assert.ok(env.calls.notify.some(n => n.kind === 'amber' && /edited while the fit was running/.test(n.msg)), JSON.stringify(env.calls.notify));
  assert.match(env.dom['sb-msg'].textContent, /discarded/);
});

// ── F1 Codex round 1: the local fallback never fits the press-time arrays over an edited model ──
test('a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)', async () => {
  let envRef = null;
  const env = makeEnv({
    uploadImpl: async () => { envRef.state.peaks[0].center = 286; return 'sid'; },   // the student edits while the upload runs
    fetchImpl: async () => { throw new TypeError('Failed to fetch'); },
  });
  envRef = env;
  await env.runFit();
  assert.equal(env.calls.local, 0, 'no local fit over the edited model');
  assert.equal(env.state.fitResult.marker, 'previous', 'previous result kept');
  assert.match(env.dom['sb-msg'].textContent, /discarded \(model edited\)/);
  assert.ok(env.calls.notify.some(n => n.kind === 'amber' && /edited while the fit was running/.test(n.msg)), JSON.stringify(env.calls.notify));
  // unchanged model: the fallback still runs (the earlier test) — and an equivalent ROI spelling is not an edit
  const same = makeEnv({ fetchImpl: async () => { throw new TypeError('Failed to fetch'); } });
  await same.runFit();
  assert.equal(same.calls.local, 1);
});
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
          label: 'Residuals',
          data: be.map((b, i) => ({ x: b, y: residuals[i] })),
          borderColor: '#8a9ab8',
          borderWidth: 1,
          pointRadius: 0,
          fill: false
        },
        {
          label: 'Zero',
          data: [{ x: beMin, y: 0 }, { x: beMax, y: 0 }],
          borderColor: 'rgba(74,158,255,0.3)',
          borderWidth: 1,
          pointRadius: 0,
          fill: false,
          borderDash: [3, 3]
        }
      ]
  }

  // 5. Combine: linear baseline + Shirley correction, clamped to data
  const result = new Array(n);
  for (let i = 0; i < n; i++) {
    result[i] = Math.min(linear[i] + bg[i], intensity[i]);
  }
  return result;
}

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

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\''),path=require('\\''path'\\''),{createRequire}=require('\\''module'\\''); const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');const file='\\''tests/js/fit_acceptance.test.js'\\'';
async function run(mutate) {const cases=[];const req=createRequire(path.resolve(file));let source=fs.readFileSync(file,'\\''utf8'\\'').replace(/"'^const html = .*$/m,'"'\\''const html = reviewHtml;'\\'');new Function('\\''require'\\'','\\''__dirname'\\'','\\''reviewHtml'\\'',source)(n=>n==='\\''node:test'\\''?{test:(name,...args)=>cases.push({name,fn:args.at(-1)})}:req(n),path.dirname(path.resolve(file)),mutate?mutate(html):html);const t=cases.find(c=>/"'^a transport failure after the model/.test(c.name));try{await t.fn();return '"'\\''PASS'\\'';}catch(e){return '\\''FAIL: '\\''+e.message.split('\\''\\n'\\'')[0];}}
(async()=>console.log({baseline:await run(),withoutFix:await run(h=>h.replace(/    if \\(e && e\\.transportFailure && ctxAtRequest "'!== null['"\\s\\S]*?\\n    }\\n/,'\\'''\\''))}))();'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
{
  baseline: 'PASS',
  withoutFix: 'FAIL: no local fit over the edited model'
}

exec
/bin/zsh -lc "rg -n '"'^const tabManager|''^let tabManager|''^class TabManager|''^function _applyRightPanelMode|''^function _fitStatusText'"' templates/index.html
sed -n '10800,10875p' templates/index.html
sed -n '8180,8230p' templates/index.html
sed -n '7290,7378p' templates/index.html
sed -n '14000,14050p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
2547:function _applyRightPanelMode(activeTab) {
3133:class TabManager {
3988:let tabManager;
8193:function _fitStatusText(fr) {
      // (sourceTabId references resolved after all tabs are pushed below).
      return {
        id,
        name: t.name || '▦ Stack',
        color: '#7a7a7a',
        isStack: true,
        _nextColorIdx: t._nextColorIdx || 0,
        lineWidth: typeof t.lineWidth === 'number' ? t.lineWidth : 1.5,
        verticalOffset: typeof t.verticalOffset === 'number' ? t.verticalOffset : 0,
        entries: Array.isArray(t.entries) ? t.entries.map(e => ({
          id: e.id || ('e_' + Math.random().toString(36).slice(2, 9)),
          sourceTabId: e.sourceTabId,
          color: e.color || '#7a7a7a',
          visible: e.visible !== false,
          showFit: !!e.showFit,
        })) : [],
        // Inert spectrum-tab fields kept to satisfy existing lifecycle code paths.
        isSurvey: false, chargeVerified: true,
        rawBE: [], rawIntensity: [], ccShift: 0,
        peaks: [], nextId: 1, fitResult: null,
        markedElements: [], notes: '', sourcePath: null,
        ui: { bgType: 'shirley', bgStart: '', bgEnd: '', shirleyIter: '5',
              endpointAvg: '1', roiMin: '', roiMax: '',
              ccMethod: 'none', ccObs: '', ccLit: '' },
      };
    }
    const color = TAB_COLORS[tabManager._colorIdx++ % TAB_COLORS.length];
    const isSurvey = t.isSurvey || false;
    return {
      id, name: t.name, color, isSurvey,
      sourcePath: t.sourcePath || (sessionFile ? sessionFile : '(restored)'),
      chargeVerified: t.chargeVerified ?? true,
      rawBE: t.rawBE || [], rawIntensity: t.rawIntensity || [],
      ccShift: t.ccShift || 0,
      peaks: _normalizePeaksCRef((t.peaks || []).map(p => ({...p}))),
      nextId: t.nextId || 1,
      fitResult: t.fitResult || null,
      modelProvenance: t.modelProvenance || null,
      // Autofit candidate-set annotations — restored verbatim when present
      // (see buildTabData; absent in pre-engine saves → null).
      analysis: t.analysis ?? null,
      markedElements: t.markedElements || [],
      notes: t.notes || '',
      manualAnchors: t.manualAnchors || [],
      lineWidth: typeof t.lineWidth === 'number' ? t.lineWidth : 1.5,
      ui: {
        bgType: 'shirley', bgStart: '', bgEnd: '',
        shirleyIter: '5', roiMin: '', roiMax: '',
        ccMethod: 'none', ccObs: '', ccLit: '',
        ...(t.ui || {})
      },
      // B2: restore per-tab element overlays. deserializeRefOverlays is total —
      // an absent/old-shaped t.refOverlays yields an empty selection (clean, no
      // overlays). Valid saved colorIdx restored verbatim; invalid repaired
      // by-position via the shared RefCore.nextColorIdx (paletteLen passed
      // explicitly). No identify marker is ever restored.
      _refSel: { ..._refDefaultSel(),
        ...RefCore.deserializeRefOverlays(t.refOverlays, ELEMENT_MARKER_COLORS.length) },
    };
  });
  // Preserve the saved tab order verbatim. (Fresh folder loads still use the
  // surveys-front convention via createTab; this path is only for saved
  // projects whose order the user already chose.)
  for (const tab of newTabs) {
    tabManager.tabs.push(tab);
  }

  // Rewrite stack-entry source references through idMap BEFORE pruning.
  // When the collision-detect path renamed a source spectrum tab, the
  // saved sourceTabId now belongs to a PRE-EXISTING tab — without the
  // remap the entry would silently render the wrong spectrum (or be
  // pruned if the colliding tab isn't a spectrum tab). Only newly loaded
  // stacks are remapped; pre-existing stacks reference live IDs.
  for (const tab of newTabs) {
    if (!tab.isStack) continue;
    for (const e of tab.entries) {
function _provenanceOf(tab) {
  if (!tab) return null;
  if (tab.modelProvenance) return JSON.parse(JSON.stringify(tab.modelProvenance));
  const fr = tab.fitResult;
  if (!_isLocalFit(fr)) return null;
  return { objective: fr.objective || null, engine: fr.engine || 'local', status: fr.status || null,
           weighting: fr.weighting || null, chiReduced: fr.chiReduced ?? null,
           reportable: false, caveat: _localFitCaveat(fr), derivedFrom: 'local_fit' };
}
function _localFitCaveat(fr) {
  if (!_isLocalFit(fr)) return '';
  return _isUnweightedLocal(fr) ? _LOCAL_FIT_CAVEAT_UNWEIGHTED : _LOCAL_FIT_CAVEAT;
}
function _fitStatusText(fr) {
  const tag = !_isLocalFit(fr) ? '' : (_isUnweightedLocal(fr) ? ' (starting point)' : ' (local, starting point)');
  return _fitStatLabel(fr) + ' = ' + fr.chiReduced.toFixed(2) + tag;
}
function _applyStatCaption(fr) {
  const cap = document.getElementById('sb-chi-caption');
  if (!cap) return;
  cap.innerHTML = !_isLocalFit(fr) ? '&#967;&#178;&#7523;:'
    : (_isUnweightedLocal(fr) ? 'Residual variance (starting point):' : '&#967;&#178;&#7523; (local, starting point):');
}
// The statistic is displayed as ONE unit — header text + tooltip, status-bar
// caption + value — from the same fit result, or all cleared. Refreshing
// any one of them alone can pair a local value with a chi-square caption
// (Codex round 9).
function _applyStatDisplay(fr) {
  const fq = document.getElementById('fit-quality');
  const sb = document.getElementById('sb-chi');
  const st = (fr && fr === state.fitResult) ? _statsLiveState() : 'current';
  if (fr && Number.isFinite(fr.chiReduced) && st === 'stale') {
    // F1: the statistic belongs to the previous model: say so, show no number
    if (fq) { fq.textContent = _fitStatLabel(fr) + ' \u2014 (model changed)'; fq.setAttribute('data-xps-tip', _STATS_STALE_NOTE); }
    if (sb) sb.textContent = '\u2014';
  } else if (fr && Number.isFinite(fr.chiReduced)) {
    const tip = (_isLocalFit(fr) ? _LOCALFIT_TOOLTIP : _CHISQ_TOOLTIP) + (st === 'unverified' ? '\n\n' + _STATS_UNVERIFIED_NOTE : '');
    if (fq) { fq.textContent = _fitStatusText(fr); fq.setAttribute('data-xps-tip', tip); }
    if (sb) sb.textContent = fr.chiReduced.toFixed(3);
  } else {
    if (fq) { fq.innerHTML = '&#967;&#178; &mdash;'; fq.removeAttribute('data-xps-tip'); }
    if (sb) sb.textContent = '\u2014';
  }
  _applyStatCaption(fr);
  _updateLocalModelBanner();
}

// Local Levenberg-Marquardt: the fallback engine, and the ONLY engine Batch
// Fit uses.
//
// ACCEPTANCE RULE (unit A0, 2026-09-15): this function never writes to
  }
  // 1b. The charge correction below is derived from this component's fitted
  // centre and then shifts EVERY binding energy in the spectrum, so the
  // component has to exist. A Graphite amplitude driven to its lower bound
  // (the server's floor is zero; lmfit returns ~1e-12 there) still comes back
  // with a centre inside the ±0.3 eV window — a position of nothing.
  // 1c. Supported (the fit cannot drop it without cost, other components held)
  // is necessary but not sufficient: with strong overlap the OTHER components
  // could absorb the anchor if refitted. The server refits without it when
  // asked (require_component) and reports whether that made the fit
  // significantly worse. A redundant anchor is refused the same way.
  const req = json && json.required;
  if (req && req.ran === true && req.required === false) {
    notify('Auto-fit: the Graphite component is not required by the data — refitting the other components without it fits the data as well' + (req.f != null ? ' (F = ' + Number(req.f).toFixed(1) + ', threshold 10)' : '') + '. No charge correction was derived from it and the fit was not applied. The model gives the other components enough freedom to absorb the graphite line; lock or narrow them and try again.', 'red', true);
    return false;
  }
  if (!_autoFitGraphiteIsSupported(gPeak, json)) {
    notify('Auto-fit: the data do not support the Graphite component (removing it does not worsen the fit), so no charge correction was derived from it and the fit was not applied.', 'red', true);
    return false;
  }
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
  }
  return html + '</div>';
}

// ══════════════════════════════════════════════════════════════
// FEATURE 3: VISUAL FIT HISTORY — SNAPSHOT COMPARISON
// ══════════════════════════════════════════════════════════════

const SNAPSHOT_MAX = 10;
let _snapshotSuppressed = false;

// Preview state: { peaks, fitResult } or null — drawn in orange overlay
let _historyPreview = null;

function _autoSnapshot() {
  if (_snapshotSuppressed) return;
  if (!tabManager.activeId || !state.peaks.length || !state.fitResult) return;

  const tab = tabManager._getTab(tabManager.activeId);
  if (!tab) return;
  if (!tab.snapshots) tab.snapshots = [];
  if (!tab._fitCount) tab._fitCount = 0;
  tab._fitCount++;

  const chi = state.fitResult.chiReduced;
  const n = state.peaks.length;
  const label = `Fit #${tab._fitCount} (${n} peak${n !== 1 ? 's' : ''})`;

  const snap = {
    id: Date.now(),
    label,
    timestamp: new Date().toLocaleTimeString(),
    peaks: JSON.parse(JSON.stringify(state.peaks)),
    fitResult: {
      ...state.fitResult,
      be: [...(state.fitResult.be || [])],
      bgSubtracted: [...(state.fitResult.bgSubtracted || [])],
      bgIntensity: state.fitResult.bgIntensity ? [...state.fitResult.bgIntensity] : null,
      fittedY: state.fitResult.fittedY ? [...state.fitResult.fittedY] : null,
    },
    chi,
    rFactor: state.fitResult.rFactor ?? null,
  };

  tab.snapshots.unshift(snap);
  if (tab.snapshots.length > SNAPSHOT_MAX) tab.snapshots.pop();
}

function showHistoryModal() {
  _renderHistoryList();
  const panel = document.getElementById('history-panel');

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\''); const h=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\''); const ls=h.split('\\''\\n'\\'');
function fn(n){let s=ls.findIndex(x=>new RegExp('\\''"'^(async )?function '"'\\''+n+'\\''\\\\('\\'').test(x)),d=0,seen=false;for(let i=s;i<ls.length;i++){for(const c of ls[i]){if(c==='\\''{'\\''){d++;seen=true;}if(c==='\\''}'\\'')d--;}if(seen&&"'!d)return ls.slice(s,i+1).join('"'\\''\\n'\\'');}throw n;}
const c=ls.slice(ls.findIndex(x=>x.startsWith('\\''const _STARTS_MODEL_FIELDS'\\'')),ls.findIndex(x=>x.startsWith('\\''const _STARTS_UI_FIELDS'\\''))+1).join('\\''\\n'\\'');

const method=ls.slice(ls.findIndex(l=>l==='\\''  closeTab(id) {'\\''),ls.findIndex(l=>l==='\\''  // ── Folder upload ───────────────────────────────'\\'')).join('\\''\\n'\\'').replace('\\''  closeTab(id) {'\\'','\\''function closeTab(id) {'\\'');
const elements={};const el=id=>elements[id]??=( {textContent:'\\'''\\'',innerHTML:'\\'''\\'',value:'\\'''\\'',style:{},classList:{add(){},remove(){}},setAttribute(){},removeAttribute(){},getContext:()=>({clearRect(){}}),querySelector:()=>null,appendChild(){}} );
const document={getElementById:el,createElement:()=>({})};let renders=0;
el('\\''results-area'\\'').innerHTML='\\''Previous fit: chi = 1.200, RMSE = 2.0'\\'';el('\\''fit-quality'\\'').textContent='\\''χ²ᵣ = 1.20'\\'';el('\\''sb-chi'\\'').textContent='\\''1.200'\\'';
const state={fitResult:{chiReduced:1.2},peaks:[{id:1}],rawBE:[1],rawIntensity:[2]};
const deps={state,document,_updateUndoButtons(){},renderPeakList(){},_updateRFactorUI(){},_updateROIDisplay(){},renderResults(){renders++;},_applyStatDisplay(){renders++;}};
const close=new Function(...Object.keys(deps),fn('\\''renderEmptyChart'\\'')+'\\''\\n'\\''+method+'\\''\\nreturn closeTab;'\\'')(...Object.values(deps));
const manager={tabs:[{id:1,name:'\\''only spectrum'\\''}],activeId:1,renderTabBar(){},_updateSurveyPanel(){},_updateCCVerifiedUI(){}};
close.call(manager,1);console.log(JSON.stringify({actualFitResult:state.fitResult,resultsHTML:el('\\''results-area'\\'').innerHTML,header:el('\\''fit-quality'\\'').textContent,statusChi:el('\\''sb-chi'\\'').textContent,statsRefreshCalls:renders}));
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
{"actualFitResult":null,"resultsHTML":"Previous fit: chi = 1.200, RMSE = 2.0","header":"χ²ᵣ = 1.20","statusChi":"1.200","statsRefreshCalls":0}

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\''),path=require('\\''path'\\''),{createRequire}=require('\\''module'\\'');const file='\\''tests/js/fit_acceptance.test.js'\\'',req=createRequire(path.resolve(file)); const makeEnv=new Function('\\''require'\\'','\\''__dirname'\\'',fs.readFileSync(file,'\\''utf8'\\'')+'\\''\\nreturn makeEnv;'\\'')(n=>n==='\\''node:test'\\''?{test(){}}:req(n),path.dirname(path.resolve(file)));
(async()=>{for(const failure of [false,true]){let env,request;env=makeEnv({uploadImpl:async()=>{env.dom['\\''bg-endpoint-avg'\\''].value='\\''1e1'\\'';return '\\''sid'\\'';},fetchImpl:async(url,init)=>{request=JSON.parse(init.body);if(failure)throw new TypeError('\\''Failed to fetch'\\'');return {ok:true,json:async()=>({success:true,statistics:{reduced_chi_square:1.2},residuals:[],fitted_y:[]})};}});
env.dom['\\''bg-endpoint-avg'\\'']={value:'\\''10'\\''};globalThis.tabManager={_captureUI:()=>({endpointAvg:env.dom['\\''bg-endpoint-avg'\\''].value})};
await env.runFit();console.log(JSON.stringify({transportFailure:failure,requestedEndpointAvg:request.background.endpoint_avg,liveEndpointAvg:parseInt(env.dom['\\''bg-endpoint-avg'\\''].value),serverApplied:env.calls.applied,localFitCalls:env.calls.local,discarded:env.calls.notify.some(n=>n.msg.includes('\\''discarded'\\''))}));}delete globalThis.tabManager;})();'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
{"transportFailure":false,"requestedEndpointAvg":10,"liveEndpointAvg":1,"serverApplied":1,"localFitCalls":0,"discarded":false}
{"transportFailure":true,"requestedEndpointAvg":10,"liveEndpointAvg":1,"serverApplied":0,"localFitCalls":1,"discarded":false}

exec
/bin/zsh -lc "git diff main..HEAD -- templates/index.html | tail -150
nl -ba templates/index.html | sed -n '3292,3328p;7637,7653p'
rg -n 'statisticsState|startsModelKey|altKey|fitKey|ctxAtRequest' static/js templates/index.html | tail -55
sed -n '2547,2588p' templates/index.html
sed -n '3800,3865p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-NT0NzKwU' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-hVwQeSRY' (errno=Operation not permitted)
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
  3292	            // it, or the closed source's curves (and, for a local source,
  3293	            // their only designation) outlive the entry (Codex A0 round 19).
  3294	            _renderStackChart(t);
  3295	          }
  3296	        }
  3297	      }
  3298	    }
  3299	
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
  7637	// already persisted in saved files keep matching.
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
  7653	// The key of the ACTIVE tab as it stands now (live model, live controls).
templates/index.html:7157:// `p.support.fitKey`, the key of the model and fit context at that time, and
templates/index.html:7198:function _applySupportVerdicts(peaks, verdictOf, fitKey) {
templates/index.html:7202:    p.support = v ? { f: v.f ?? null, delta_chi2: v.delta_chi2 ?? null, supported: !!v.supported, fitKey,
templates/index.html:7206:function _applySupport(peaks, json, fitKey) {
templates/index.html:7207:  _applySupportVerdicts(peaks, id => _componentSupportFromResponse(json, id), fitKey);
templates/index.html:7212:  if (!p.support.fitKey) return false;                              // a verdict from before keys existed: not applied
templates/index.html:7214:  return _sameFitKey(p.support.fitKey, key);
templates/index.html:7218:  if (!(p && p.support && p.support.fitKey)) return null;
templates/index.html:7219:  return _sameFitKey(p.support.fitKey, _startsLiveKey()) ? p.support : null;
templates/index.html:7226:  for (const p of state.peaks) if (p.support) p.support.fitKey = key;
templates/index.html:7227:  if (state.fitResult) state.fitResult.startsModelKey = key;   // F1: the statistics are the same result's
templates/index.html:7347:    startsModelKey: _startsLiveKey(),   // F1: binds the statistics to this model; re-stamped below with the locks
templates/index.html:7492:    const ctxAtRequest = _startsLiveKey();
templates/index.html:7537:    if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
templates/index.html:7626:function _startsModelKey(peaks, ui, ccShift, anchors) {
templates/index.html:7638:function _fitKeyCanon(k) {
templates/index.html:7640:  const memo = _fitKeyCanon._memo || (_fitKeyCanon._memo = new Map());
templates/index.html:7652:function _sameFitKey(a, b) { return !!a && !!b && (a === b || _fitKeyCanon(a) === _fitKeyCanon(b)); }
templates/index.html:7656:  return _startsModelKey(state.peaks, ui, state.ccShift, typeof _getManualAnchors === 'function' ? _getManualAnchors() : []);
templates/index.html:7659:function _startsRecordKey(t) { return _startsModelKey(t.peaks, t.ui, t.ccShift, t.manualAnchors); }
templates/index.html:7663:  if (!st || !fr.startsModelKey || !_sameFitKey(fr.startsModelKey, key)) return null;
templates/index.html:7679:  if (!fr.startsModelKey) return 'unverified';
templates/index.html:7680:  return _sameFitKey(fr.startsModelKey, key) ? 'current' : 'stale';
templates/index.html:7690:  return (st === 'stale' || st === 'unverified') ? { statisticsState: st, statisticsNote: _statsNote(st) } : {};
templates/index.html:7739:      !(state.fitResult && _historyPreview.altKey === state.fitResult.startsModelKey && _startsIfCurrent(state.fitResult, _startsLiveKey()))) {
templates/index.html:7876:  _historyPreview = { snapId: key, altKey: state.fitResult.startsModelKey, peaks, fitResult: { chiReduced: alt.chi2r } };
templates/index.html:7926:  let ctxAtRequest = null;   // set with the other request inputs; read again by the local fallback
templates/index.html:7946:    ctxAtRequest = _startsLiveKey();
templates/index.html:8022:    if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
templates/index.html:8044:                        startsModelKey: _startsLiveKey(),     // model + context, taken AFTER the result was applied
templates/index.html:8071:    if (e && e.transportFailure && ctxAtRequest !== null && !_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
templates/index.html:8589:                      startsModelKey: _startsLiveKey() };   // F1: the statistics describe the committed model
templates/index.html:10305:      startsModelKey: state.fitResult.startsModelKey || null,
templates/index.html:10367:    startsModelKey: state.fitResult.startsModelKey || null,
templates/index.html:10464:        startsModelKey: t.fitResult.startsModelKey || null,
templates/index.html:10685:    for (const k of ['engine', 'objective', 'weighting', 'status', 'caveat', 'starts', 'startsModelKey', 'chosenAlternative']) if (data.statistics[k]) fr[k] = data.statistics[k];
templates/index.html:10689:    if (data.fittedY && data.statistics.statisticsState !== 'stale') fr.fittedY = data.fittedY;
templates/index.html:10690:    if (data.statistics.rFactor && data.statistics.statisticsState !== 'stale') fr.rFactor = data.statistics.rFactor;
function _applyRightPanelMode(activeTab) {
  const tabsBar = document.querySelector('#right-panel .panel-body > .tabs');
  const subPanels = document.querySelectorAll('#right-panel .panel-body > .tab-panel');
  const stackPanel = document.getElementById('tab-stack-legend');
  const header = document.querySelector('#right-panel .panel-header');
  const wrap = document.getElementById('add-spectrum-wrap');
  const isStack = isStackTab(activeTab);
  if (tabsBar) tabsBar.style.display = isStack ? 'none' : '';
  subPanels.forEach(p => {
    if (p.id === 'tab-stack-legend') return;
    p.style.display = isStack ? 'none' : '';
  });
  if (stackPanel) stackPanel.classList.toggle('active', isStack);
  if (header) header.textContent = isStack ? 'Stack Legend' : 'Peaks & Results';
  if (wrap) wrap.style.display = isStack ? 'inline-block' : 'none';
  document.body.classList.toggle('stack-tab-active', isStack);
  // Universal: line-width slider always rebinds to the active tab.
  if (activeTab) _bindLineWidthControl(activeTab);
  if (isStack) {
    renderStackLegend(activeTab);
    _bindOffsetControl(activeTab);
  }
}

// "+ Add Spectrum" dropdown toggle (button onclick handler).
function _toggleAddSpectrumMenu() {
  const menu = document.getElementById('add-spectrum-menu');
  if (!menu) return;
  const open = menu.style.display === 'block';
  if (open) { menu.style.display = 'none'; return; }
  const active = tabManager._getTab(tabManager.activeId);
  if (!isStackTab(active)) return;
  const spectrumTabs = tabManager.tabs.filter(t => !t.isStack);
  menu.innerHTML = '';
  if (spectrumTabs.length === 0) {
    menu.innerHTML = '<div class="empty">No spectrum tabs open.</div>';
  } else {
    for (const t of spectrumTabs) {
      const item = document.createElement('div');
      item.className = 'item';
      item.textContent = t.name;
      item.addEventListener('click', () => {
    }
    this._preSurveyTabId = null;
  }

  // ── Private helpers ─────────────────────────────

  _getTab(id) { return this.tabs.find(t => t.id === id) || null; }

  _syncActiveToRecord() {
    if (!this.activeId) return;
    const t = this._getTab(this.activeId);
    if (!t) return;
    if (t.isStack) return;  // stack tabs have no UI/form state to sync back
    // Re-capture peaks reference in case removePeak/clearAllPeaks replaced the array
    t.peaks = state.peaks;
    t.ccShift = isNaN(state.ccShift) ? 0 : state.ccShift;
    t.nextId = state.nextId;
    t.fitResult = state.fitResult;
    t.lineWidth = state.lineWidth ?? 1.5;
    t.yZoom = state._mainYMax || null;
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

codex
The four new behavioral tests each fail when their corresponding fix is removed in memory. I also reproduced a remaining cleanup gap: closing the last spectrum clears `fitResult` but leaves the previous Results table and χ² displays visible. I’ll report that alongside the canonicalization regression.
exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '3295,3326p'
git status --short" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
  3295	          }
  3296	        }
  3297	      }
  3298	    }
  3299	
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
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-5D6TmVt8' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Oc4wL36j' (errno=Operation not permitted)
?? docs/autofit/codex/f1_stale_statistics_r2_verdict_runA.md
?? docs/autofit/codex/f1_stale_statistics_r2_verdict_runB.md

codex
1. **MAJOR — Canonicalization treats different fit inputs as equal.** [templates/index.html:7645](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:7645)  
   Fit with endpoint averaging `10`, then change it to `1e1`. `_fitKeyCanon` uses `Number()`, so the keys compare equal; background computation and requests use `parseInt()`, producing **10 versus 1**. Reproduced with actual background functions: different arrays, statistics still `current`, starts evidence still accepted. During a pending `runFit`, this also bypasses both discard checks: a successful server response applies, and a transport failure runs the local fallback. Canonicalization must follow each field’s actual reader semantics.

2. **MAJOR — Closing the last tab still leaves the previous statistics visible.** [templates/index.html:3305](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:3305)  
   Fit the only open spectrum, show Results, then close its tab. This branch clears `state.fitResult` and calls `renderEmptyChart`, but never reaches the new statistics refresh or `renderResults`. Reproduced using the actual close handler and empty-chart renderer: `fitResult === null`, while Results, header χ² and status-bar χ² retain the closed spectrum’s values. The Clear All fix does not cover this remaining transition to `none`.

Validation: **139/140 focused tests passed**; the Python parity subprocess failed because the read-only sandbox lacks a writable temporary directory. All four new behavioral tests fail when their respective fixes are removed in memory. Auto-Fit’s key capture follows its provisional setup, so that setup does not cause self-discard. Browser tests were not run. No files changed.

**VERDICT: NO-GO**
tokens used
97,906
1. **MAJOR — Canonicalization treats different fit inputs as equal.** [templates/index.html:7645](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:7645)  
   Fit with endpoint averaging `10`, then change it to `1e1`. `_fitKeyCanon` uses `Number()`, so the keys compare equal; background computation and requests use `parseInt()`, producing **10 versus 1**. Reproduced with actual background functions: different arrays, statistics still `current`, starts evidence still accepted. During a pending `runFit`, this also bypasses both discard checks: a successful server response applies, and a transport failure runs the local fallback. Canonicalization must follow each field’s actual reader semantics.

2. **MAJOR — Closing the last tab still leaves the previous statistics visible.** [templates/index.html:3305](/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics/templates/index.html:3305)  
   Fit the only open spectrum, show Results, then close its tab. This branch clears `state.fitResult` and calls `renderEmptyChart`, but never reaches the new statistics refresh or `renderResults`. Reproduced using the actual close handler and empty-chart renderer: `fitResult === null`, while Results, header χ² and status-bar χ² retain the closed spectrum’s values. The Clear All fix does not cover this remaining transition to `none`.

Validation: **139/140 focused tests passed**; the Python parity subprocess failed because the read-only sandbox lacks a writable temporary directory. All four new behavioral tests fail when their respective fixes are removed in memory. Auto-Fit’s key capture follows its provisional setup, so that setup does not cause self-discard. Browser tests were not run. No files changed.

**VERDICT: NO-GO**
