OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0dc38-2bed-7771-ba56-05b45b8f1096
--------
user
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

Finish with VERDICT: GO or VERDICT: NO-GO.
codex
I’ll check the diff, trace the statistics consumers and fit-result writes, and run the relevant read-only tests. I’ll focus on concrete failures and finish with a ranked verdict.
exec
/bin/zsh -lc "pwd && rg --files -g AGENTS.md -g package.json -g '*stale_statistics*' -g '*fit_acceptance*' -g '*local_lm_descent*' -g '*unsupported_components*' && git status --short && git diff --stat main..HEAD" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
tests/js/fit_acceptance.test.js
tests/js/local_lm_descent.test.js
tests/js/unsupported_components.test.js
tests/js/stale_statistics.test.js
docs/autofit/codex/unsupported_components_r4_verdict_runB.md
docs/autofit/codex/unsupported_components_recheck5_prompt.txt
docs/autofit/codex/unsupported_components_r5_verdict_runB.md
docs/autofit/codex/f1_stale_statistics_verdict_runA.md
docs/autofit/codex/unsupported_components_recheck2_prompt.txt
docs/autofit/codex/unsupported_components_r2_verdict_runB.md
docs/autofit/codex/unsupported_components_r6_verdict_runA.md
docs/autofit/codex/unsupported_components_review_prompt.txt
docs/autofit/codex/unsupported_components_r3_verdict_runB.md
docs/autofit/codex/unsupported_components_verdict_runB.md
docs/autofit/codex/unsupported_components_r3_verdict_runA.md
docs/autofit/codex/unsupported_components_recheck3_prompt.txt
docs/autofit/codex/unsupported_components_r6_verdict_runB.md
docs/autofit/codex/unsupported_components_verdict_runA.md
docs/autofit/codex/unsupported_components_recheck_prompt.txt
docs/autofit/codex/unsupported_components_recheck4_prompt.txt
docs/autofit/codex/f1_stale_statistics_review_prompt.txt
docs/autofit/codex/unsupported_components_r2_verdict_runA.md
docs/autofit/codex/unsupported_components_r5_verdict_runA.md
docs/autofit/codex/f1_stale_statistics_verdict_runB.md
docs/autofit/codex/unsupported_components_r4_verdict_runA.md
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-o5AFmoLb' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-f617ZB4x' (errno=Operation not permitted)
?? docs/autofit/codex/f1_stale_statistics_verdict_runA.md
?? docs/autofit/codex/f1_stale_statistics_verdict_runB.md
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-j1WFeM7w' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-7jFqkX2l' (errno=Operation not permitted)
 CLAUDE.md                                          |  25 +-
 .../codex/f1_stale_statistics_review_prompt.txt    |  67 +++++
 .../plans/2026-09-25-f1-stale-statistics.md        | 111 ++++++++
 templates/index.html                               | 130 +++++++--
 tests/js/fit_acceptance.test.js                    |  14 +-
 tests/js/local_lm_descent.test.js                  |   4 +-
 tests/js/stale_statistics.test.js                  | 300 +++++++++++++++++++++
 tests/js/unsupported_components.test.js            |   1 +
 tests/test_browser_find_peaks_full_window.py       |  32 +++
 9 files changed, 654 insertions(+), 30 deletions(-)

exec
/bin/zsh -lc 'for p in /AGENTS.md /Users/AGENTS.md /Users/skyefortier/AGENTS.md /Users/skyefortier/xps-app/AGENTS.md /Users/skyefortier/xps-app/.claude/AGENTS.md /Users/skyefortier/xps-app/.claude/worktrees/AGENTS.md; do if [ -f "$p" ]; then cat "$p"; fi; done; rg -n '"'chiReduced|\\brmse\\b|rFactor|backendResult|fittedY|_buildStderrMap|startsModelKey|fitResult\\s*=' templates/index.html static/js" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
templates/index.html:3237:    state.fitResult = tab.fitResult;
templates/index.html:3250:    if (state.fitResult && state.fitResult.rFactor == null) {
templates/index.html:3251:      state.fitResult.rFactor = _computeRFactor(state.fitResult);
templates/index.html:3253:    _updateRFactorUI(state.fitResult ? state.fitResult.rFactor : null);
templates/index.html:3303:      state.peaks = []; state.fitResult = null;
templates/index.html:3425:      state.fitResult = null;
templates/index.html:3428:      active.fitResult = null;
templates/index.html:3815:    t.fitResult = state.fitResult;
templates/index.html:4660:  if (state.fitResult) state.fitResult.fittedY = null;
templates/index.html:5952:  state.fitResult = null;
templates/index.html:7015:    t.fitResult = snap.fitResult;
templates/index.html:7027:  state.fitResult = snap.fitResult;
templates/index.html:7225:  if (state.fitResult) state.fitResult.startsModelKey = key;   // F1: the statistics are the same result's
templates/index.html:7335:  const chiReduced = stats.reduced_chi_square || 0;
templates/index.html:7336:  const rmse = Math.sqrt((json.residuals || []).reduce((s, v) => s + v * v, 0) / Math.max(1, be2.length));
templates/index.html:7338:  state.fitResult = {
templates/index.html:7339:    chi: chiReduced * Math.max(1, be2.length - state.peaks.length * 3),
templates/index.html:7340:    chiReduced, rmse,
templates/index.html:7342:    backendResult: json,
templates/index.html:7343:    fittedY: json.fitted_y,
templates/index.html:7345:    startsModelKey: _startsLiveKey(),   // F1: binds the statistics to this model; re-stamped below with the locks
templates/index.html:7347:  state.fitResult.rFactor = _computeRFactor(state.fitResult);
templates/index.html:7352:    fq.textContent = 'χ²ᵣ = ' + chiReduced.toFixed(2);
templates/index.html:7358:  if (sbChi) sbChi.textContent = chiReduced.toFixed(3);
templates/index.html:7361:  if (typeof _updateRFactorUI === 'function') _updateRFactorUI(state.fitResult.rFactor);
templates/index.html:7447:  state.fitResult = null;
templates/index.html:7543:    notify('Auto-fit complete. χ²ᵣ = ' + (state.fitResult?.chiReduced?.toFixed(3) || '?'), 'green');
templates/index.html:7615:function _startsModelKey(peaks, ui, ccShift, anchors) {
templates/index.html:7626:  return _startsModelKey(state.peaks, ui, state.ccShift, typeof _getManualAnchors === 'function' ? _getManualAnchors() : []);
templates/index.html:7629:function _startsRecordKey(t) { return _startsModelKey(t.peaks, t.ui, t.ccShift, t.manualAnchors); }
templates/index.html:7633:  if (!st || !fr.startsModelKey || fr.startsModelKey !== key) return null;
templates/index.html:7649:  if (!fr.startsModelKey) return 'unverified';
templates/index.html:7650:  return fr.startsModelKey === key ? 'current' : 'stale';
templates/index.html:7670:  if (typeof _updateRFactorUI === 'function') _updateRFactorUI(state.fitResult ? state.fitResult.rFactor : null);
templates/index.html:7705:      !(state.fitResult && _historyPreview.altKey === state.fitResult.startsModelKey && _startsIfCurrent(state.fitResult, _startsLiveKey()))) {
templates/index.html:7842:  _historyPreview = { snapId: key, altKey: state.fitResult.startsModelKey, peaks, fitResult: { chiReduced: alt.chi2r } };
templates/index.html:7891:  let backendResult = null;
templates/index.html:7973:    backendResult = json;
templates/index.html:7999:    applyBackendResult(backendResult);
templates/index.html:8001:    const stats = backendResult.statistics || {};
templates/index.html:8002:    const chiReduced = stats.reduced_chi_square || 0;
templates/index.html:8003:    const rmse = Math.sqrt((backendResult.residuals || []).reduce((s, v) => s + v * v, 0) / Math.max(1, be.length));
templates/index.html:8005:    state.fitResult = { chi: chiReduced * Math.max(1, be.length - state.peaks.length * 3),
templates/index.html:8006:                        chiReduced, rmse, be, bgSubtracted, bgIntensity, backendResult,
templates/index.html:8007:                        fittedY: backendResult.fitted_y, roiRange, _preFit,
templates/index.html:8008:                        starts: backendResult.starts || null,
templates/index.html:8009:                        startsModelKey: _startsLiveKey(),     // model + context, taken AFTER the result was applied
templates/index.html:8014:    state.fitResult.rFactor = _computeRFactor(state.fitResult);
templates/index.html:8017:    _updateRFactorUI(state.fitResult.rFactor);
templates/index.html:8020:    notify('Fit complete. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3), 'green');
templates/index.html:8143:           weighting: fr.weighting || null, chiReduced: fr.chiReduced ?? null,
templates/index.html:8152:  return _fitStatLabel(fr) + ' = ' + fr.chiReduced.toFixed(2) + tag;
templates/index.html:8168:  if (fr && Number.isFinite(fr.chiReduced) && st === 'stale') {
templates/index.html:8172:  } else if (fr && Number.isFinite(fr.chiReduced)) {
templates/index.html:8175:    if (sb) sb.textContent = fr.chiReduced.toFixed(3);
templates/index.html:8520:  const chiReduced = chi / dof;                       // weighted reduced chi-square, as lmfit's redchi
templates/index.html:8522:  const rmse = Math.sqrt(_raw.reduce((a, v) => a + v * v, 0) / be.length);   // unweighted RMS, as the server path reports
templates/index.html:8542:  state.fitResult = { chi, chiReduced, rmse, be, bgSubtracted, bgIntensity, roiRange,
templates/index.html:8546:                      startsModelKey: _startsLiveKey() };   // F1: the statistics describe the committed model
templates/index.html:8547:  state.fitResult.rFactor = _computeRFactor(state.fitResult);
templates/index.html:8551:  _updateRFactorUI(state.fitResult.rFactor);
templates/index.html:8560:         '. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3) + ' (Poisson-weighted; no uncertainties). Starting point only: run Fit before reporting.', 'amber');
templates/index.html:8562:  return { success: true, engine: 'local', iterations, acceptedSteps, chiReduced, certifyRestarts };
templates/index.html:8594:function _buildStderrMap(fitResult) {
templates/index.html:8596:  const peaks = fitResult?.backendResult?.individual_peaks;
templates/index.html:8632:  const { chiReduced, rmse, backendResult } = state.fitResult;
templates/index.html:8636:  const stderrMap = _stale ? {} : _buildStderrMap(state.fitResult);
templates/index.html:8661:        <div style="font-family:var(--mono);font-size:16px;color:${_stale ? 'var(--text3)' : _statIsChi ? (chiReduced<2?'var(--green)':chiReduced<5?'var(--amber)':'var(--red)') : 'var(--text)'}">${_stale ? _dash : chiReduced.toFixed(3)}</div>
templates/index.html:8665:        <div style="font-family:var(--mono);font-size:16px;color:var(--accent2)">${_stale ? _dash : rmse.toFixed(1)}</div>
templates/index.html:8667:      ${backendResult ? `<div style="flex:1;background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);padding:8px 10px">
templates/index.html:8672:    ${_stale ? '' : _renderRFactorPanel(state.fitResult.rFactor)}
templates/index.html:8993://   { be, bg, fittedY, peaks: [{peak, y}] }
templates/index.html:8995:// `fittedY` is the raw-level envelope; each peak's `y` is the raw-level
templates/index.html:8999://   A:  fitResult.be + fitResult.fittedY both present, lengths match
templates/index.html:9000://       → use fittedY directly (already raw-level). Frozen to fit-time
templates/index.html:9002://   A2: fitResult.be + fitResult.bgIntensity present, no fittedY (local
templates/index.html:9003://       LM fit) → fittedY = evalAllPeaks(be, peaks) + bg.
templates/index.html:9034:    return { be: [], bg: [], rawY: [], fittedY: [], peaks: [] };
templates/index.html:9039:    return { be: [], bg: [], rawY: [], fittedY: [], peaks: [] };
templates/index.html:9073:  let fittedY;
templates/index.html:9074:  if (Array.isArray(fr.fittedY) && fr.fittedY.length === be.length && _statsRecordState(src) !== 'stale') {
templates/index.html:9075:    // Path A: backend fittedY directly (already raw-level). Never a stale
templates/index.html:9077:    fittedY = fr.fittedY.slice();
templates/index.html:9081:    fittedY = model.map((v, i) => v + bg[i]);
templates/index.html:9092:  return { be, bg, rawY, fittedY, peaks: peakCurves };
templates/index.html:9245:        ? rd.be.map((b, i) => ({ x: b, y: (rd.fittedY[i] - rd.bg[i]) + yShift }))
templates/index.html:9246:        : rd.be.map((b, i) => ({ x: b, y: rd.fittedY[i]              + yShift }));
templates/index.html:9419:            ? rd.be.map((b, i) => ({ x: b, y: (rd.fittedY[i] - rd.bg[i]) + yShift }))
templates/index.html:9420:            : rd.be.map((b, i) => ({ x: b, y: rd.fittedY[i]              + yShift })))
templates/index.html:9553:  const fittedYBacked = haveFit && state.fitResult.fittedY &&
templates/index.html:9554:                        state.fitResult.fittedY.length === plotBE.length &&
templates/index.html:9556:                        ? state.fitResult.fittedY : null;
templates/index.html:9557:  const rawResiduals = fittedYBacked
templates/index.html:9558:    ? plotInten.map((v, i) => v - fittedYBacked[i])
templates/index.html:9562:    const d = fittedYBacked ? plotInten[i] : bgSubtracted[i];
templates/index.html:9644:  if (showEnvelope && plotBE.length && (fittedYBacked || state.peaks.length)) {
templates/index.html:9647:      data: fittedYBacked
templates/index.html:9648:        ? plotBE.map((b, i) => ({ x: b, y: fittedYBacked[i] - (bgSubView ? plotBG[i] : 0) }))
templates/index.html:10257:      chiReduced: state.fitResult.chiReduced ?? null,
templates/index.html:10263:      startsModelKey: state.fitResult.startsModelKey || null,
templates/index.html:10292:  // fittedY then matches its residuals (the current model), as with no fit
templates/index.html:10294:  const fittedY = (_saveStats !== 'stale' && state.fitResult?.fittedY) || modelFull.map((v, i) => v + bgIntensity[i]);
templates/index.html:10315:    chiReduced: state.fitResult.chiReduced,
templates/index.html:10316:    rmse: state.fitResult.rmse,
templates/index.html:10324:    startsModelKey: state.fitResult.startsModelKey || null,
templates/index.html:10345:    fittedY: fittedY,
templates/index.html:10403:        chi: t.fitResult.chi, chiReduced: t.fitResult.chiReduced,
templates/index.html:10404:        rmse: t.fitResult.rmse, fittedY: t.fitResult.fittedY || null,
templates/index.html:10420:        startsModelKey: t.fitResult.startsModelKey || null,
templates/index.html:10640:    const fr = { chi: data.statistics.chi, chiReduced: data.statistics.chiReduced, rmse: data.statistics.rmse };
templates/index.html:10641:    for (const k of ['engine', 'objective', 'weighting', 'status', 'caveat', 'starts', 'startsModelKey', 'chosenAlternative']) if (data.statistics[k]) fr[k] = data.statistics[k];
templates/index.html:10643:    if (data.fittedY) fr.fittedY = data.fittedY;
templates/index.html:10644:    active.fitResult = fr;
templates/index.html:10645:    state.fitResult = fr;
templates/index.html:11027:  const fittedY = (_figStats !== 'stale' && state.fitResult?.fittedY?.length === be.length) ? state.fitResult.fittedY : null;
templates/index.html:11028:  const residArr = fittedY ? inten.map((v, i) => v - fittedY[i]) : null;
templates/index.html:11055:  for (const arr of [inten, bgArr, fittedY]) {
templates/index.html:11144:  if (fittedY) {
templates/index.html:11146:    polyline(be, fittedY, yM);
templates/index.html:11241:      ctx.fillText(statLabel + '\u2009=\u2009' + state.fitResult.chiReduced.toFixed(3) + (_figStats === 'unverified' ? ' (unverified)' : ''),
templates/index.html:11269:  if (fittedY) lgItems.push({ label: _isLocalModel() ? 'Fit (local, starting point)' : 'Fit', type: 'line', color: '#cc0000' });
templates/index.html:11403:  const stderrMap = _stats === 'stale' ? {} : _buildStderrMap(state.fitResult);
templates/index.html:11418:  const chiStr = state.fitResult.chiReduced.toFixed(4);
templates/index.html:11539:  if (fitResult.fittedY && fitResult.fittedY.length === be.length) {
templates/index.html:11542:      residuals = bgSub.map((v, i) => (v + bgI[i]) - fitResult.fittedY[i]);
templates/index.html:11544:      residuals = bgSub.map((v, i) => v - (fitResult.fittedY[i] - (bgI ? bgI[i] : 0)));
templates/index.html:11576:  if (rf && state.fitResult && rf === state.fitResult.rFactor && _statsLiveState() === 'stale') {
templates/index.html:11647:  if (!state.fitResult?.backendResult?.individual_peaks) return { warnings: [], info: [] };
templates/index.html:11653:  const stderrMap = _buildStderrMap(state.fitResult);
templates/index.html:12184:    tgt.fitResult = null;
templates/index.html:12194:      state.fitResult = null;   // live copy of tgt.fitResult = null above (unit A0)
templates/index.html:12226:                   chi: ok && Number.isFinite(outcome.chiReduced) ? outcome.chiReduced : null,
templates/index.html:13977:  const chi = state.fitResult.chiReduced;
templates/index.html:13991:      fittedY: state.fitResult.fittedY ? [...state.fitResult.fittedY] : null,
templates/index.html:13994:    rFactor: state.fitResult.rFactor ?? null,
templates/index.html:14043:        <div class="hist-row-meta">${s.timestamp} &middot; ${(s.peaks || []).length} peak${(s.peaks || []).length !== 1 ? 's' : ''}${typeof s.chi === 'number' && isFinite(s.chi) ? ' &middot; <span class="hist-row-chi">' + _escHtml(_fitStatLabel(s.fitResult)) + ' = ' + s.chi.toFixed(3) + (_isLocalFit(s.fitResult) ? ' (starting point)' : '') + '</span>' : ''}${typeof s.rFactor === 'number' && isFinite(s.rFactor) ? ', R = ' + s.rFactor.toFixed(1) + '%' : ''}</div>
templates/index.html:14135:  state.fitResult = snap.fitResult ? { ...snap.fitResult } : null;
templates/index.html:16119:  // Peaks' own response has no be/fittedY/bgIntensity arrays to rebuild a
templates/index.html:16128:    state.fitResult = null;
templates/index.html:16151:    // state.fitResult === null correctly (falls back to its own

exec
/bin/zsh -lc 'git diff main..HEAD -- templates/index.html' in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-qCX6ysn6' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-uWL7nwlR' (errno=Operation not permitted)
diff --git a/templates/index.html b/templates/index.html
index 0b9268d..9f032ae 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -7222,6 +7222,7 @@ function _currentSupport(p) {
 function _restampSupport() {
   const key = _startsLiveKey();
   for (const p of state.peaks) if (p.support) p.support.fitKey = key;
+  if (state.fitResult) state.fitResult.startsModelKey = key;   // F1: the statistics are the same result's
 }
 // Patch the sidebar cards in place for the current verdicts (a re-render would
 // replace an input the student is typing in): header centre, the three summary
@@ -7341,6 +7342,7 @@ function applyAutoFitResult(json, graphiteRaw, roi) {
     backendResult: json,
     fittedY: json.fitted_y,
     roiRange,
+    startsModelKey: _startsLiveKey(),   // F1: binds the statistics to this model; re-stamped below with the locks
   };
   state.fitResult.rFactor = _computeRFactor(state.fitResult);
 
@@ -7631,6 +7633,43 @@ function _startsIfCurrent(fr, key) {
   if (!st || !fr.startsModelKey || fr.startsModelKey !== key) return null;
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
+  return fr.startsModelKey === key ? 'current' : 'stale';
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
+  if (el && state.fitResult && el.getAttribute('data-stats-state') !== st && typeof renderResults === 'function') renderResults();   // applies the header / status bar too
+  else _applyStatDisplay(state.fitResult);
+  if (typeof _updateRFactorUI === 'function') _updateRFactorUI(state.fitResult ? state.fitResult.rFactor : null);
+}
+
 // After anything that may have changed the model or its context without going
 // through a Results re-render (a lock toggle, Lock All, a background or ROI
 // control): take a stale alternative overlay off the chart and bring the
@@ -8125,8 +8164,14 @@ function _applyStatCaption(fr) {
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
@@ -8497,7 +8542,8 @@ function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
   state.fitResult = { chi, chiReduced, rmse, be, bgSubtracted, bgIntensity, roiRange,
                       engine: 'local', status: 'converged',
                       objective: 'poisson_weighted_chi_square', weighting: '1/sqrt(max(counts,1))', iterations,
-                      reportable: false, caveat: _LOCAL_FIT_CAVEAT };
+                      reportable: false, caveat: _LOCAL_FIT_CAVEAT,
+                      startsModelKey: _startsLiveKey() };   // F1: the statistics describe the committed model
   state.fitResult.rFactor = _computeRFactor(state.fitResult);
 
   _applyStatDisplay(state.fitResult);
@@ -8564,6 +8610,8 @@ function _peakArea(p, be) {
 
 function renderResults() {
   const el = document.getElementById('results-area');
+  const _stats = _statsLiveState();   // F1: current / stale / unverified / none
+  if (el) el.setAttribute('data-stats-state', _stats);
   _applyStatDisplay(state.fitResult);   // header + status bar track every result change (clear, restore, auto-fit) as one unit
   _updateLocalModelBanner();
   if (!state.fitResult) {
@@ -8583,7 +8631,14 @@ function renderResults() {
 
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
@@ -8598,22 +8653,23 @@ function renderResults() {
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
@@ -9015,8 +9071,9 @@ function _buildEntryRenderData(entry) {
 
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
@@ -9491,8 +9548,11 @@ function updatePlot() {
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
@@ -9594,6 +9654,7 @@ function updatePlot() {
     });
   }
 
+  _refreshStatsState();                  // F1: chi-square / sigma / R follow the same key
   _refreshStartsEvidence(false, true);   // background / ROI controls only repaint the chart: keep the visible consumers honest (fromPlot: the chart itself is being rebuilt)
   _refreshRoiAndCentreWarnings();         // ROI past the data / centre outside the data: warn, never move
   // History snapshot preview overlay (cyan dashed, drawn on top)
@@ -10203,6 +10264,7 @@ function _doSaveFit() {
       chosenAlternative: _startsIfCurrent(state.fitResult, _startsLiveKey()) ? (state.fitResult.chosenAlternative || null) : null,
       reportable: _isLocalFit(state.fitResult) ? false : (state.fitResult.reportable ?? null),
       caveat: _localFitCaveat(state.fitResult) || state.fitResult.caveat || null,
+      ..._statsSaveFields(_statsLiveState()),   // F1: says plainly when the statistics belong to the previous model
     } : ((_activeTab() && _activeTab().modelProvenance) ? {
       ..._activeTab().modelProvenance, reportable: false, caveat: _localFitCaveat(_activeTab().modelProvenance),
     } : null),
@@ -10226,7 +10288,10 @@ function _doSaveSpectrum() {
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
@@ -10262,6 +10327,7 @@ function _doSaveSpectrum() {
     // these fields existed) is designated on re-save too.
     reportable: _isLocalFit(state.fitResult) ? false : (state.fitResult.reportable ?? null),
     caveat: _localFitCaveat(state.fitResult) || state.fitResult.caveat || null,
+    ..._statsSaveFields(_saveStats),
   } : null;
 
   const data = {
@@ -10356,6 +10422,7 @@ async function _doSaveProject() {
         iterations: t.fitResult.iterations ?? null,
         reportable: _isLocalFit(t.fitResult) ? false : (t.fitResult.reportable ?? null),
         caveat: _localFitCaveat(t.fitResult) || t.fitResult.caveat || null,
+        ..._statsSaveFields(_statsRecordState(t)),   // F1: judged against the RECORD's key
       } : null,
       modelProvenance: t.modelProvenance || null,
       notes: t.notes || '',
@@ -10917,7 +10984,11 @@ function exportResults() {
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
@@ -10951,7 +11022,9 @@ function _doPublicationExport() {
   if (!be.length) { notify('No data in ROI.', 'red'); return; }
 
   const bgArr   = computeBackground(be, inten);
-  const fittedY = (state.fitResult?.fittedY?.length === be.length) ? state.fitResult.fittedY : null;
+  // F1: a stale result's fitted curve is the previous model's: not drawn as "Fit"
+  const _figStats = _statsLiveState();
+  const fittedY = (_figStats !== 'stale' && state.fitResult?.fittedY?.length === be.length) ? state.fitResult.fittedY : null;
   const residArr = fittedY ? inten.map((v, i) => v - fittedY[i]) : null;
   const invert   = document.getElementById('invert-be').checked;
   const showIndiv = document.getElementById('show-individual').checked;
@@ -11160,10 +11233,12 @@ function _doPublicationExport() {
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
@@ -11322,7 +11397,10 @@ function _shapeExportCols(p) {
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
@@ -11371,7 +11449,9 @@ function exportFitTable(fmt) {
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
@@ -11384,7 +11464,9 @@ function exportFitTable(fmt) {
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
@@ -11491,6 +11573,13 @@ function _renderRFactorPanel(rf) {
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
@@ -11556,6 +11645,9 @@ const _CHISQ_TOOLTIP = "Reduced chi-squared (\u03c7\u00b2\u1d63) measures the go
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
/bin/zsh -lc 'git diff main..HEAD -- tests/js/fit_acceptance.test.js tests/js/local_lm_descent.test.js tests/js/unsupported_components.test.js tests/test_browser_find_peaks_full_window.py CLAUDE.md && cat tests/js/stale_statistics.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-egXNPQ7D' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-U5kjHtrf' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index ea02c0a..bfc19b8 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -610,9 +610,28 @@ result if that key changed: amber notice, "Fit discarded (model edited)",
 previous peaks and result kept. Before this, a centre changed and locked
 mid-fit kept its edited value (`applyBackendResult` honours locks) under the
 server's χ², σ and fitted curve for a different model.
-Not covered by this rule (separate units): model replacement that
-keeps an older result (Find Peaks apply in the default window, undo/redo)
-and loaded files without convergence provenance. From the initial commit
+STATISTICS AFTER AN EDIT (unit F1, 2026-09-25; plan
+`docs/superpowers/plans/2026-09-25-f1-stale-statistics.md`): χ², σ, RMSE,
+the R-factor and the stored fitted curve are bound to their fit by the SAME
+key (`fitResult.startsModelKey`, now stamped by every creator — `runFit`,
+`runFitLocal`, `applyAutoFitResult`, re-stamped by `_restampSupport`); no
+second mechanism. One accessor, `_statsState(fr, key)` (`_statsLiveState()`,
+`_statsRecordState(t)`): `current` / `stale` (the model or its context
+changed since — an edit, a Find Peaks apply in the default window, an undo
+or history restore to other values) / `unverified` (no key: saved before
+this unit — values shown with a note to re-run). Stale: Results banner
+("belong to the previous model"), statistic / RMSE "—", no R panel, no σ;
+header "χ²ᵣ — (model changed)", status "—", "R: —"; no per-parameter
+uncertainty rule; CSV/XLSX a WARNING instead of the statistic, σ cells
+empty; TSV a NOTE (its columns are the current, unfitted model); figure no
+χ² and no stored "Fit" curve; chart and stack envelopes composed from the
+current peaks; saves keep the key (a reload judges again) and add
+`statisticsState` / `statisticsNote`. Refreshed from `updatePlot`
+(`_refreshStatsState`, Results carries `data-stats-state`). The model
+replacement that keeps an older result is thereby covered for the
+statistics. Not covered (separate units): loaded files without convergence
+provenance; `p._backendParams` still rides in a stale save (not displayed;
+the sealed fit record owns it). From the initial commit
 until this unit the local LM step had the wrong sign and returned the
 starting model as "Fit complete"; see
 `docs/superpowers/plans/2026-09-15-a01-local-lm-proof.md` and
diff --git a/tests/js/fit_acceptance.test.js b/tests/js/fit_acceptance.test.js
index 63e2e50..995460c 100644
--- a/tests/js/fit_acceptance.test.js
+++ b/tests/js/fit_acceptance.test.js
@@ -260,8 +260,9 @@ test('project save derives the designation from the objective for an older local
   const src = html.slice(start, end) + ';';
   const constLine = html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n');
   const fieldsAt = lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS'));
-  const helpers = lines.slice(fieldsAt, lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\n' + ['_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_localFitCaveat', '_startsForSave', '_startsIfCurrent', '_startsModelKey', '_startsRecordKey'].map(extractFn).join('\n');
-  const build = new Function('RefCore', '_roundBE', '_roundIntensity', constLine + '\n' + helpers + '\n' + src + '\nreturn buildTabData;')(
+  const helpers = lines.slice(fieldsAt, lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\n' + ['_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_localFitCaveat', '_startsForSave', '_startsIfCurrent', '_startsModelKey', '_startsRecordKey', '_statsState', '_statsRecordState', '_statsNote', '_statsSaveFields'].map(extractFn).join('\n');
+  const statsConsts = html.match(/^const _STATS_\w+_NOTE = .*$/mg).join('\n');
+  const build = new Function('RefCore', '_roundBE', '_roundIntensity', constLine + '\n' + statsConsts + '\n' + helpers + '\n' + src + '\nreturn buildTabData;')(
     { serializeRefOverlays: () => null }, a => a, a => a);
   const older = { id: 1, name: 't', rawBE: [1, 2], rawIntensity: [1, 1], ccShift: 0, peaks: [], nextId: 1, ui: {},
     fitResult: { chi: 1, chiReduced: 1e4, rmse: 100, objective: 'unweighted_residual_variance', be: [1, 2], bgIntensity: [0, 0], bgSubtracted: [1, 1] } };
@@ -296,7 +297,7 @@ test('_applyStatDisplay keeps header, tooltip, caption and value consistent thro
   const src = ['_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay'].map(extractFn).join('\n');
   const constLine = html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n');
   const dom = {}; const el = id => (dom[id] ||= { textContent: '', innerHTML: '', tip: null, setAttribute(k, v) { this.tip = v; }, removeAttribute() { this.tip = null; } });
-  const apply = new Function('document', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_updateLocalModelBanner', constLine + '\n' + src + '\nreturn _applyStatDisplay;')({ getElementById: el }, 'CHI', 'LOCAL', () => {});
+  const apply = new Function('document', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_updateLocalModelBanner', 'state', constLine + '\n' + src + '\nreturn _applyStatDisplay;')({ getElementById: el }, 'CHI', 'LOCAL', () => {}, { fitResult: null });
   apply({ objective: 'unweighted_residual_variance', chiReduced: 12345 });
   assert.equal(dom['fit-quality'].textContent, 'Residual variance = 12345.00 (starting point)');
   assert.equal(dom['fit-quality'].tip, 'LOCAL'); assert.match(dom['sb-chi-caption'].innerHTML, /starting point/); assert.equal(dom['sb-chi'].textContent, '12345.000');
@@ -329,7 +330,7 @@ test('_applyStatDisplay clears header, tooltip, caption and value together on lo
   const src = ['_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay'].map(extractFn).join('\n');
   const constLine = html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n');
   const dom = {}; const el = id => (dom[id] ||= { textContent: '', innerHTML: '', tip: null, setAttribute(k, v) { this.tip = v; }, removeAttribute() { this.tip = null; } });
-  const apply = new Function('document', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_updateLocalModelBanner', constLine + '\n' + src + '\nreturn _applyStatDisplay;')({ getElementById: el }, 'CHI', 'LOCAL', () => {});
+  const apply = new Function('document', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_updateLocalModelBanner', 'state', constLine + '\n' + src + '\nreturn _applyStatDisplay;')({ getElementById: el }, 'CHI', 'LOCAL', () => {}, { fitResult: null });
   apply({ objective: 'unweighted_residual_variance', chiReduced: 999 });
   apply(null);
   assert.match(dom['fit-quality'].innerHTML, /&mdash;/); assert.equal(dom['fit-quality'].tip, null);
@@ -487,7 +488,7 @@ test('the sidebar banner shows on a stack tab whose visible entries draw a local
   assert.equal(run({ isStack: true, entries: [{ sourceTabId: 2, visible: true, showFit: false }] }).style.display, 'none', 'fit curves hidden → no designation needed');
   assert.equal(run({ isStack: true, entries: [{ sourceTabId: 3, visible: true, showFit: true }] }).style.display, 'none', 'weighted source only');
   const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
-  assert.match(grab('function _applyStatDisplay(', 900), /_updateLocalModelBanner\(\)/, 'activation/result changes refresh the banner');
+  assert.match(grab('function _applyStatDisplay(', 1800), /_updateLocalModelBanner\(\)/, 'activation/result changes refresh the banner');
   const legendAt = html.indexOf("row.querySelector('.name').textContent = name;");
   assert.match(html.slice(legendAt, legendAt + 2500), /_updateLocalModelBanner\(\)/, 'stack legend rebuild refreshes the banner');
 });
@@ -532,7 +533,8 @@ test('W1 helpers: weighted local results are chi-square but still designated; le
 
 // ── W1 Codex round 1: the TSV export's warning follows the GOVERNING objective (behavioural) ──
 test('TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result', () => {
-  const src = ['_isUnweightedLocal', '_isLocalProvenance', '_isLocalFit', '_isLocalModel', '_localFitCaveat', '_governingProvenance', 'exportResults', '_isUnsupported'].map(extractFn).join('\n');
+  const src = ['_isUnweightedLocal', '_isLocalProvenance', '_isLocalFit', '_isLocalModel', '_localFitCaveat', '_governingProvenance', 'exportResults', '_isUnsupported'].map(extractFn).join('\n')
+    + '\nconst _statsLiveState = () => "current";';   // F1's stale note is pinned in stale_statistics.test.js
   const consts = html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n');
   const run = (fitResult, modelProvenance) => {
     let text = null;
diff --git a/tests/js/local_lm_descent.test.js b/tests/js/local_lm_descent.test.js
index 3901fdc..342ad9f 100644
--- a/tests/js/local_lm_descent.test.js
+++ b/tests/js/local_lm_descent.test.js
@@ -40,8 +40,8 @@ const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'a
   'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
   'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
   '_computeRFactor', '_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel', '_governingProvenance', '_localFitCaveat', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay', '_updateLocalModelBanner',
-  '_componentSupportCore', '_supportRootOf', '_applySupportVerdicts'];
-const CAVEAT_CONST = (html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg) || []).join('\n');
+  '_componentSupportCore', '_supportRootOf', '_applySupportVerdicts', '_statsState', '_statsLiveState'];
+const CAVEAT_CONST = (html.match(/^const (_LOCAL_FIT_CAVEAT\w*|_STATS_\w+_NOTE) = .*$/mg) || []).join('\n');
 
 // One isolated environment per test: a fresh `state`, a stub DOM, and the
 // extracted functions bound to them.
diff --git a/tests/js/unsupported_components.test.js b/tests/js/unsupported_components.test.js
index 7e002bd..5de224f 100644
--- a/tests/js/unsupported_components.test.js
+++ b/tests/js/unsupported_components.test.js
@@ -114,6 +114,7 @@ function pageEnv(fns, extraArgs = {}) {
     renderQuantify: () => {}, recalcQuantify: () => {}, _detectPeakRSF: () => ({ key: 'C 1s', rsf: 1 }), SCOFIELD_RSF: { 'C 1s': 1 }, notify: () => {},
     _clearDisallowedChargeRef: () => {}, _updateLocalModelBanner: () => {}, _updateLockAllBtn: () => {}, renderPeakForm: () => '', _highlightChartPeak: () => {},
     _roiWindowStatus: () => ({ state: 'ok', n: 0 }), _patchPeakCardsForCentre: () => {},   // the ROI / centre warnings: tests/js/roi_clamp_centre_warning.test.js
+    _statsLiveState: () => 'current', _STATS_STALE_NOTE: '', _STATS_UNVERIFIED_NOTE: '',   // F1's stale statistics: tests/js/stale_statistics.test.js
     _isChargeRefAllowed: () => false, _fitStatLabel: () => 'χ²ᵣ', _isUnweightedLocal: () => false, _applyStatCaption: () => {}, _applyStatDisplay: () => {},
     _CHISQ_TOOLTIP: '', _LOCALFIT_TOOLTIP: '', _startsSummaryText: () => '', _startsChosenText: () => '', _startsIfCurrent: () => null,
     _isLocalModel: () => false, _updateRFactorUI: () => {}, _activeTab: () => ({}), _renderRFactorPanel: () => '', _statIsChi: true,
diff --git a/tests/test_browser_find_peaks_full_window.py b/tests/test_browser_find_peaks_full_window.py
index c20dab7..079860f 100644
--- a/tests/test_browser_find_peaks_full_window.py
+++ b/tests/test_browser_find_peaks_full_window.py
@@ -150,6 +150,10 @@ def _load_c1s_with_stale_narrow_fit(pg):
             be: narrowBE, bgIntensity: narrowBG, bgSubtracted: narrowSub,
             fittedY: narrowBE.map((b, i) => narrowSub[i] + 300),
             roiRange: { min: '278.0', max: '290.4' },
+            // a real fit stores its R-factor with the result; since F1
+            // (2026-09-25) the status bar is re-applied from the stored
+            // result on every repaint, so it must be where a fit puts it
+            rFactor: { rPct: 3.2, level: 'good' },
         };
         document.getElementById('roi-min').value = 278.0;
         document.getElementById('roi-max').value = 298.0;
@@ -247,6 +251,34 @@ def test_checkbox_off_preserves_todays_cropped_behavior(browser, server):
         pg.close()
 
 
+def test_checkbox_off_marks_a_keyed_result_stale_after_find_peaks_apply(browser, server):
+    """F1 (2026-09-25): the default Find Peaks apply keeps the old result over
+    a REPLACED model. A result that carries its fit key (every result since
+    the scattered-starts unit) is then judged against the new model: its
+    chi-square, sigma and R are marked as the previous model's, and the
+    chart's envelope is composed from the new peaks, not the old curve. A
+    keyless result (the test above) is shown as before, with the unverified
+    note."""
+    pg = _new_page(browser, server)
+    try:
+        _load_c1s_with_stale_narrow_fit(pg)
+        pg.evaluate("() => { state.fitResult.startsModelKey = _startsLiveKey(); renderResults(); }")
+        assert pg.evaluate("() => _statsLiveState()") == "current"
+        _run_and_apply_find_peaks(pg, full_window=False)
+        assert pg.evaluate("() => state.fitResult !== null"), "the old result is kept, as before"
+        st = pg.evaluate("""() => ({ state: _statsLiveState(),
+            header: document.getElementById('fit-quality').textContent,
+            sbChi: document.getElementById('sb-chi').textContent,
+            sbRuns: document.getElementById('sb-runs').textContent,
+            banner: !!document.querySelector('#results-area .stats-stale-note') })""")
+        assert st["state"] == "stale", st
+        assert "model changed" in st["header"], st
+        assert st["sbChi"] == "\u2014" and st["sbRuns"] == "R: \u2014", st
+        assert st["banner"], st
+    finally:
+        pg.close()
+
+
 def test_checkbox_on_extends_fit_and_background_to_the_full_window(browser, server):
     """The actual fix: checked must make the background/fit-curve span
     the FULL user-set ROI (278-298), not the stale frozen 278.0-290.4
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

const STATE_FNS = ['_statsState', '_statsLiveState', '_statsRecordState', '_statsNote', '_statsSaveFields'];
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
  // every creator of a fit result stamps fitResult.startsModelKey from _startsLiveKey()
  assert.match(extractFn('runFit'), /startsModelKey: _startsLiveKey\(\)/);
  assert.match(extractFn('runFitLocal'), /startsModelKey: _startsLiveKey\(\)/, 'the local engine stamps its result');
  assert.match(extractFn('applyAutoFitResult'), /startsModelKey: _startsLiveKey\(\)/, 'Auto-Fit stamps its result');
  // Auto-Fit locks every centre and refines the charge shift AFTER applying: the re-stamp covers the statistics
  const restamp = new Function('state', '_startsLiveKey', extractFn('_restampSupport') + '\nreturn _restampSupport;');
  const st = { peaks: [{ id: 1, support: { fitKey: 'OLD' } }], fitResult: { startsModelKey: 'OLD' } };
  restamp(st, () => 'NEW')();
  assert.strictEqual(st.fitResult.startsModelKey, 'NEW');
  assert.strictEqual(st.peaks[0].support.fitKey, 'NEW');
  // no other key-like field was introduced
  assert.ok(!/statsModelKey|statisticsKey/.test(html), 'no second key');
});

test('Results panel, current: statistic, RMSE, R and sigma are shown', () => {
  const { api, doc, state } = sandbox({ liveKey: 'K1' });
  state.peaks = [{ ...PEAK }];
  state.fitResult = serverResult('K1');
  api.renderResults();
  const h = doc.els['results-area'].innerHTML;
  assert.strictEqual(doc.els['results-area'].getAttribute('data-stats-state'), 'current');
  assert.match(h, /1\.235/);
  assert.match(h, /7\.5/);
  assert.match(h, /R-factor/);
  assert.match(h, /± 0\.012/, 'sigma on the centre');
  assert.ok(!/stats-stale-note/.test(h));
  assert.strictEqual(doc.els['sb-chi'].textContent, '1.235');
});

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
});

test('status-bar R: the previous model\'s R is not shown on a stale result; an unrelated rFactor argument is untouched', () => {
  const { api, doc, state, env } = sandbox({ liveKey: 'EDITED' });
  state.fitResult = serverResult('K1');
  api._updateRFactorUI(state.fitResult.rFactor);
  assert.strictEqual(doc.els['sb-runs'].textContent, 'R: —');
  env.key = 'K1';
  api._updateRFactorUI(state.fitResult.rFactor);
  assert.strictEqual(doc.els['sb-runs'].textContent, 'R: 3.2%');
  api._updateRFactorUI(null);
  assert.strictEqual(doc.els['sb-runs'].textContent, '');
});

test('the stored fitted curve is never drawn, saved or stacked as the fit once stale', () => {
  const up = extractFn('updatePlot');
  assert.match(up, /fittedYBacked = haveFit[\s\S]*?_statsLiveState\(\) !== 'stale'/, 'chart envelope / residuals');
  assert.match(up, /_refreshStatsState\(\)/, 'every repaint keeps the visible statistics honest');
  assert.match(extractFn('_buildEntryRenderData'), /_statsRecordState\(src\) !== 'stale'/, 'stack Path A judged against the SOURCE record');
  assert.match(extractFn('_doPublicationExport'), /_figStats !== 'stale' && state\.fitResult\?\.fittedY/, 'figure');
  assert.match(extractFn('_doSaveSpectrum'), /_saveStats !== 'stale' && state\.fitResult\?\.fittedY/, 'spectrum save');
});

test('saves keep the key and say plainly when the statistics are stale or unverified', () => {
  assert.match(extractFn('_doSaveFit'), /_statsSaveFields\(_statsLiveState\(\)\)/);
  assert.match(extractFn('_doSaveSpectrum'), /_statsSaveFields\(_saveStats\)/);
  assert.match(extractFn('_doSaveProject'), /_statsSaveFields\(_statsRecordState\(t\)\)/, 'project: the RECORD\'s key');
  for (const f of ['_doSaveFit', '_doSaveSpectrum', '_doSaveProject']) assert.match(extractFn(f), /startsModelKey:/, f + ' keeps the key');
});

// ── CSV / XLSX / TSV: run the real exporters on stubs ───────────────────────
function exportSandbox(liveKey, fr) {
  const out = {};
  const src = [...STATE_CONSTS.map(constLine), ...STATE_FNS.map(extractFn), extractFn('exportFitTable'), extractFn('exportResults')].join('\n');
  const state = { peaks: [{ ...PEAK }], fitResult: fr, ccShift: 0 };
  const api = new Function('state', 'out', `
    const _startsLiveKey = () => ${JSON.stringify(liveKey)};
    const _startsRecordKey = t => t.key;
    const document = { getElementById: () => null };
    const notify = () => {};
    const _buildStderrMap = fr => { const o = {}; for (const ip of fr.backendResult.individual_peaks) o[ip.id] = ip.params; return o; };
    const _peakArea = p => p.amplitude;
    const _isUnsupported = () => false, _currentSupport = () => null;
    const _isLocalFit = () => false, _isUnweightedLocal = () => false, _localFitCaveat = () => '';
    const _isLocalModel = () => false, _governingProvenance = () => null;
    const _startsSummaryText = () => '', _startsIfCurrent = () => null, _startsChosenText = () => '';
    const _shapeExportCols = () => ({ gl: '', alpha: '', beta: '', m: '' });
    const _UNSUPPORTED_LABEL = 'not supported by the data';
    const _downloadBlob = (b, name) => { out.blob = b; out.name = name; };
    const getROIData = () => ({ be: [1, 2, 3], inten: [1, 2, 1] });
    const computeBackground = be => be.map(() => 0);
    const evalAllPeaks = be => be.map(() => 0.5);
    const evalPeakArray = be => be.map(() => 0.5);
    const XLSX = { utils: { book_new: () => ({ sheets: [] }), aoa_to_sheet: a => a, book_append_sheet: (wb, ws, n) => wb.sheets.push([n, ws]) },
                   writeFile: wb => { out.wb = wb; } };
    const Blob = function (parts) { this.text = parts.join(''); };
    const URL = { createObjectURL: b => { out.blob = b; return 'u'; }, revokeObjectURL: () => {} };
    ${src.replace(/document\.createElement\('a'\)/g, '({ click() {} })')}
    return { exportFitTable, exportResults };
  `)(state, out);
  return { api, out };
}

test('CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma', () => {
  let { api, out } = exportSandbox('K1', serverResult('K1'));
  api.exportFitTable('csv');
  assert.match(out.blob.text, /# .*: 1\.2346/);
  assert.match(out.blob.text, /"0\.01230"/);
  ({ api, out } = exportSandbox('EDITED', serverResult('K1')));
  api.exportFitTable('csv');
  assert.match(out.blob.text, /# WARNING: .*previous model/);
  assert.ok(!/1\.2346/.test(out.blob.text), 'no statistic');
  assert.ok(!/0\.0123/.test(out.blob.text) && !/0\.0456/.test(out.blob.text), 'no sigma');
  const fr = serverResult('K1'); delete fr.startsModelKey;
  ({ api, out } = exportSandbox('K1', fr));
  api.exportFitTable('csv');
  assert.match(out.blob.text, /# NOTE: .*cannot be confirmed/);
  assert.match(out.blob.text, /1\.2346/, 'unverified: shown, with the note');
});

test('XLSX: stale writes a WARNING row instead of the statistic, and no sigma', () => {
  const { api, out } = exportSandbox('EDITED', serverResult('K1'));
  api.exportFitTable('xlsx');
  const info = out.wb.sheets.find(s => s[0] === 'Info')[1];
  assert.ok(info.some(r => r[0] === 'WARNING' && /previous model/.test(r[1])));
  assert.ok(!info.some(r => r[1] === '1.2346'));
  const rows = out.wb.sheets.find(s => s[0] === 'Fit Results')[1];
  assert.strictEqual(rows[1][3], '', 'centre sigma empty');
  assert.strictEqual(rows[1][5], '', 'width sigma empty');
});

test('TSV: stale says the Model / Residual columns are the current, unfitted model', () => {
  let { api, out } = exportSandbox('EDITED', serverResult('K1'));
  api.exportResults();
  assert.match(out.blob.text, /^# NOTE: the model has changed since the last fit/);
  ({ api, out } = exportSandbox('K1', serverResult('K1')));
  api.exportResults();
  assert.ok(!/# NOTE/.test(out.blob.text));
});

test('the refresh re-renders Results only when its rendered state differs', () => {
  const src = [...STATE_CONSTS.map(constLine), ...STATE_FNS.map(extractFn), extractFn('_refreshStatsState')].join('\n');
  const doc = makeDoc();
  const env = { key: 'K1', renders: 0, applied: 0 };
  const state = { fitResult: serverResult('K1') };
  const refresh = new Function('document', 'state', 'env', `
    const _startsLiveKey = () => env.key, _startsRecordKey = t => t.key;
    const renderResults = () => { env.renders++; document.getElementById('results-area').setAttribute('data-stats-state', _statsLiveState()); };
    const _applyStatDisplay = () => { env.applied++; };
    const _updateRFactorUI = () => { env.r = (env.r || 0) + 1; };
    ${src}
    return _refreshStatsState;`)(doc, state, env);
  doc.els['results-area'].setAttribute('data-stats-state', 'current');
  refresh();
  assert.strictEqual(env.renders, 0, 'unchanged: no re-render');
  env.key = 'EDITED';
  refresh();
  assert.strictEqual(env.renders, 1, 'the edit made it stale: re-rendered once');
  assert.strictEqual(env.r, 2, 'the status-bar R follows on the re-render path too (renderResults does not write it)');
  refresh();
  assert.strictEqual(env.renders, 1);
  env.key = 'K1';               // an undo brings the fitted model back
  refresh();
  assert.strictEqual(env.renders, 2, 'current again');
});

exec
/bin/zsh -lc "sed -n '7560,7640p' templates/index.html; sed -n '3110,3275p' templates/index.html; sed -n '7870,8035p' templates/index.html; sed -n '7280,7430p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
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
  if (!st || !fr.startsModelKey || fr.startsModelKey !== key) return null;
  return st;
}
// Unit F1 (2026-09-25): the fit STATISTICS (chi-square, sigma, R-factor, RMSE
// and the stored fitted curve) are bound to the fit that produced them by the
// SAME key — no second mechanism. One accessor classifies a result:
//   'current'    the key matches: they describe the model shown;
//   'stale'      the key differs: they belong to the previous model (an edit,
      if (activeEl && typeof activeEl.scrollIntoView === 'function') {
        activeEl.scrollIntoView({ block: 'nearest', inline: 'nearest' });
      }
    }
  } catch (_) { /* non-fatal */ }
}

// ═══════════════════════════════════════════════════
// TAB MANAGER
// ═══════════════════════════════════════════════════
// Endpoint averaging (n_avg) defaults. NEW tabs get 3 — the smallest
// averaging that captures most of the one-point-edge benefit with half the
// anchor bias of 5 (docs/superpowers/plans/2026-09-03-endpoint-averaging-
// default.md; owner decision 2026-09-03). LEGACY is what a SAVED ui that
// lacks endpointAvg must resolve to: such fits were made before the field
// existed, i.e. at 1, and their stored results are reconstructed against
// that background — "new fits only, nothing previously reported changes".
const NEW_TAB_ENDPOINT_AVG = '3';
const LEGACY_ENDPOINT_AVG = '1';
// Upper bound shared with the backend (autofit.methods.base.ENDPOINT_AVG_MAX)
// and the #bg-endpoint-avg input's max attribute.
const ENDPOINT_AVG_MAX = 50;

class TabManager {
  constructor() {
    this.tabs = [];
    this.activeId = null;
    this._colorIdx = 0;
    this._preSurveyTabId = null; // tab to restore when leaving survey sidebar tab
  }

  // ── Core tab lifecycle ──────────────────────────

  createTab(name, be, inten, sourcePath = null) {
    const id = 'tab_' + Math.random().toString(36).slice(2, 9);
    const color = TAB_COLORS[this._colorIdx++ % TAB_COLORS.length];

    // Sort by BE descending (same as setSpectrum)
    const pairs = be.map((b, i) => [b, inten[i]]).sort((a, b) => b[0] - a[0]);
    const sortedBE = pairs.map(p => p[0]);
    const sortedInten = pairs.map(p => p[1]);

    const beRange = sortedBE.length ? sortedBE[0] - sortedBE[sortedBE.length - 1] : 0;
    const isSurvey = /survey/i.test(name) || beRange > 200;

    // Strip file extension for display name
    const displayName = name.replace(/\.[^.]+$/, '');

    const minBE = sortedBE.length ? sortedBE[sortedBE.length - 1].toFixed(1) : '';
    const maxBE = sortedBE.length ? sortedBE[0].toFixed(1) : '';

    const tab = {
      id, name: displayName, color, isSurvey,
      sourcePath,
      chargeVerified: true,
      rawBE: sortedBE,
      rawIntensity: sortedInten,
      ccShift: 0,
      peaks: [],
      nextId: 1,
      fitResult: null,
      markedElements: [],
      notes: '',
      lineWidth: 1.5,
      ui: {
        bgType: 'shirley', bgStart: maxBE, bgEnd: minBE,
        shirleyIter: '5', endpointAvg: NEW_TAB_ENDPOINT_AVG,
        roiMin: minBE, roiMax: maxBE,
        ccMethod: 'none', ccObs: '', ccLit: '',
      }
    };

    if (isSurvey) {
      this.tabs.unshift(tab);
    } else {
      this.tabs.push(tab);
    }

    this.activateTab(id);
    this._updateSurveyPanel();
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
    if (state.fitResult && state.fitResult.rFactor == null) {
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
    const ctxAtRequest = _startsLiveKey();
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
    if (_startsLiveKey() !== ctxAtRequest) {
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
}

function applyAutoFitResult(json, graphiteRaw, roi) {
  // 1. Locate the graphite peak in state.peaks (named "Graphite").
  const gPeak = state.peaks.find(p => p.name === 'Graphite') || state.peaks[0];
  if (!gPeak || !Number.isFinite(gPeak.center)) {
    notify('Auto-fit failed: graphite center not found in fit result.', 'red', true);
    return false;
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

exec
/bin/zsh -lc 'cat tests/js/stale_statistics.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
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

const STATE_FNS = ['_statsState', '_statsLiveState', '_statsRecordState', '_statsNote', '_statsSaveFields'];
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
  // every creator of a fit result stamps fitResult.startsModelKey from _startsLiveKey()
  assert.match(extractFn('runFit'), /startsModelKey: _startsLiveKey\(\)/);
  assert.match(extractFn('runFitLocal'), /startsModelKey: _startsLiveKey\(\)/, 'the local engine stamps its result');
  assert.match(extractFn('applyAutoFitResult'), /startsModelKey: _startsLiveKey\(\)/, 'Auto-Fit stamps its result');
  // Auto-Fit locks every centre and refines the charge shift AFTER applying: the re-stamp covers the statistics
  const restamp = new Function('state', '_startsLiveKey', extractFn('_restampSupport') + '\nreturn _restampSupport;');
  const st = { peaks: [{ id: 1, support: { fitKey: 'OLD' } }], fitResult: { startsModelKey: 'OLD' } };
  restamp(st, () => 'NEW')();
  assert.strictEqual(st.fitResult.startsModelKey, 'NEW');
  assert.strictEqual(st.peaks[0].support.fitKey, 'NEW');
  // no other key-like field was introduced
  assert.ok(!/statsModelKey|statisticsKey/.test(html), 'no second key');
});

test('Results panel, current: statistic, RMSE, R and sigma are shown', () => {
  const { api, doc, state } = sandbox({ liveKey: 'K1' });
  state.peaks = [{ ...PEAK }];
  state.fitResult = serverResult('K1');
  api.renderResults();
  const h = doc.els['results-area'].innerHTML;
  assert.strictEqual(doc.els['results-area'].getAttribute('data-stats-state'), 'current');
  assert.match(h, /1\.235/);
  assert.match(h, /7\.5/);
  assert.match(h, /R-factor/);
  assert.match(h, /± 0\.012/, 'sigma on the centre');
  assert.ok(!/stats-stale-note/.test(h));
  assert.strictEqual(doc.els['sb-chi'].textContent, '1.235');
});

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
});

test('status-bar R: the previous model\'s R is not shown on a stale result; an unrelated rFactor argument is untouched', () => {
  const { api, doc, state, env } = sandbox({ liveKey: 'EDITED' });
  state.fitResult = serverResult('K1');
  api._updateRFactorUI(state.fitResult.rFactor);
  assert.strictEqual(doc.els['sb-runs'].textContent, 'R: —');
  env.key = 'K1';
  api._updateRFactorUI(state.fitResult.rFactor);
  assert.strictEqual(doc.els['sb-runs'].textContent, 'R: 3.2%');
  api._updateRFactorUI(null);
  assert.strictEqual(doc.els['sb-runs'].textContent, '');
});

test('the stored fitted curve is never drawn, saved or stacked as the fit once stale', () => {
  const up = extractFn('updatePlot');
  assert.match(up, /fittedYBacked = haveFit[\s\S]*?_statsLiveState\(\) !== 'stale'/, 'chart envelope / residuals');
  assert.match(up, /_refreshStatsState\(\)/, 'every repaint keeps the visible statistics honest');
  assert.match(extractFn('_buildEntryRenderData'), /_statsRecordState\(src\) !== 'stale'/, 'stack Path A judged against the SOURCE record');
  assert.match(extractFn('_doPublicationExport'), /_figStats !== 'stale' && state\.fitResult\?\.fittedY/, 'figure');
  assert.match(extractFn('_doSaveSpectrum'), /_saveStats !== 'stale' && state\.fitResult\?\.fittedY/, 'spectrum save');
});

test('saves keep the key and say plainly when the statistics are stale or unverified', () => {
  assert.match(extractFn('_doSaveFit'), /_statsSaveFields\(_statsLiveState\(\)\)/);
  assert.match(extractFn('_doSaveSpectrum'), /_statsSaveFields\(_saveStats\)/);
  assert.match(extractFn('_doSaveProject'), /_statsSaveFields\(_statsRecordState\(t\)\)/, 'project: the RECORD\'s key');
  for (const f of ['_doSaveFit', '_doSaveSpectrum', '_doSaveProject']) assert.match(extractFn(f), /startsModelKey:/, f + ' keeps the key');
});

// ── CSV / XLSX / TSV: run the real exporters on stubs ───────────────────────
function exportSandbox(liveKey, fr) {
  const out = {};
  const src = [...STATE_CONSTS.map(constLine), ...STATE_FNS.map(extractFn), extractFn('exportFitTable'), extractFn('exportResults')].join('\n');
  const state = { peaks: [{ ...PEAK }], fitResult: fr, ccShift: 0 };
  const api = new Function('state', 'out', `
    const _startsLiveKey = () => ${JSON.stringify(liveKey)};
    const _startsRecordKey = t => t.key;
    const document = { getElementById: () => null };
    const notify = () => {};
    const _buildStderrMap = fr => { const o = {}; for (const ip of fr.backendResult.individual_peaks) o[ip.id] = ip.params; return o; };
    const _peakArea = p => p.amplitude;
    const _isUnsupported = () => false, _currentSupport = () => null;
    const _isLocalFit = () => false, _isUnweightedLocal = () => false, _localFitCaveat = () => '';
    const _isLocalModel = () => false, _governingProvenance = () => null;
    const _startsSummaryText = () => '', _startsIfCurrent = () => null, _startsChosenText = () => '';
    const _shapeExportCols = () => ({ gl: '', alpha: '', beta: '', m: '' });
    const _UNSUPPORTED_LABEL = 'not supported by the data';
    const _downloadBlob = (b, name) => { out.blob = b; out.name = name; };
    const getROIData = () => ({ be: [1, 2, 3], inten: [1, 2, 1] });
    const computeBackground = be => be.map(() => 0);
    const evalAllPeaks = be => be.map(() => 0.5);
    const evalPeakArray = be => be.map(() => 0.5);
    const XLSX = { utils: { book_new: () => ({ sheets: [] }), aoa_to_sheet: a => a, book_append_sheet: (wb, ws, n) => wb.sheets.push([n, ws]) },
                   writeFile: wb => { out.wb = wb; } };
    const Blob = function (parts) { this.text = parts.join(''); };
    const URL = { createObjectURL: b => { out.blob = b; return 'u'; }, revokeObjectURL: () => {} };
    ${src.replace(/document\.createElement\('a'\)/g, '({ click() {} })')}
    return { exportFitTable, exportResults };
  `)(state, out);
  return { api, out };
}

test('CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma', () => {
  let { api, out } = exportSandbox('K1', serverResult('K1'));
  api.exportFitTable('csv');
  assert.match(out.blob.text, /# .*: 1\.2346/);
  assert.match(out.blob.text, /"0\.01230"/);
  ({ api, out } = exportSandbox('EDITED', serverResult('K1')));
  api.exportFitTable('csv');
  assert.match(out.blob.text, /# WARNING: .*previous model/);
  assert.ok(!/1\.2346/.test(out.blob.text), 'no statistic');
  assert.ok(!/0\.0123/.test(out.blob.text) && !/0\.0456/.test(out.blob.text), 'no sigma');
  const fr = serverResult('K1'); delete fr.startsModelKey;
  ({ api, out } = exportSandbox('K1', fr));
  api.exportFitTable('csv');
  assert.match(out.blob.text, /# NOTE: .*cannot be confirmed/);
  assert.match(out.blob.text, /1\.2346/, 'unverified: shown, with the note');
});

test('XLSX: stale writes a WARNING row instead of the statistic, and no sigma', () => {
  const { api, out } = exportSandbox('EDITED', serverResult('K1'));
  api.exportFitTable('xlsx');
  const info = out.wb.sheets.find(s => s[0] === 'Info')[1];
  assert.ok(info.some(r => r[0] === 'WARNING' && /previous model/.test(r[1])));
  assert.ok(!info.some(r => r[1] === '1.2346'));
  const rows = out.wb.sheets.find(s => s[0] === 'Fit Results')[1];
  assert.strictEqual(rows[1][3], '', 'centre sigma empty');
  assert.strictEqual(rows[1][5], '', 'width sigma empty');
});

test('TSV: stale says the Model / Residual columns are the current, unfitted model', () => {
  let { api, out } = exportSandbox('EDITED', serverResult('K1'));
  api.exportResults();
  assert.match(out.blob.text, /^# NOTE: the model has changed since the last fit/);
  ({ api, out } = exportSandbox('K1', serverResult('K1')));
  api.exportResults();
  assert.ok(!/# NOTE/.test(out.blob.text));
});

test('the refresh re-renders Results only when its rendered state differs', () => {
  const src = [...STATE_CONSTS.map(constLine), ...STATE_FNS.map(extractFn), extractFn('_refreshStatsState')].join('\n');
  const doc = makeDoc();
  const env = { key: 'K1', renders: 0, applied: 0 };
  const state = { fitResult: serverResult('K1') };
  const refresh = new Function('document', 'state', 'env', `
    const _startsLiveKey = () => env.key, _startsRecordKey = t => t.key;
    const renderResults = () => { env.renders++; document.getElementById('results-area').setAttribute('data-stats-state', _statsLiveState()); };
    const _applyStatDisplay = () => { env.applied++; };
    const _updateRFactorUI = () => { env.r = (env.r || 0) + 1; };
    ${src}
    return _refreshStatsState;`)(doc, state, env);
  doc.els['results-area'].setAttribute('data-stats-state', 'current');
  refresh();
  assert.strictEqual(env.renders, 0, 'unchanged: no re-render');
  env.key = 'EDITED';
  refresh();
  assert.strictEqual(env.renders, 1, 'the edit made it stale: re-rendered once');
  assert.strictEqual(env.r, 2, 'the status-bar R follows on the re-render path too (renderResults does not write it)');
  refresh();
  assert.strictEqual(env.renders, 1);
  env.key = 'K1';               // an undo brings the fitted model back
  refresh();
  assert.strictEqual(env.renders, 2, 'current again');
});

exec
/bin/zsh -lc "sed -n '3800,3915p' templates/index.html; sed -n '4640,4680p' templates/index.html; sed -n '9440,9555p' templates/index.html; sed -n '11520,11665p' templates/index.html; rg -n '_autoSnapshot\\(|_restampSupport\\(|_fitStatusText\\(|_provenanceFromFit|modelProvenance|function peakToBackendSpec|function getROIData|function updateChargeCorrection|function undo|function redo' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
exec
/bin/zsh -lc 'git diff main..HEAD -- tests/js/fit_acceptance.test.js tests/js/local_lm_descent.test.js tests/js/unsupported_components.test.js tests/test_browser_find_peaks_full_window.py CLAUDE.md && cat docs/superpowers/plans/2026-09-25-f1-stale-statistics.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
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
    }
    // Bkgrd Sub: restore checked state, sync visual class, refresh enable,
    // and re-gate the dependent overlay controls so they reflect the
    // restored sub-view state.
    const bgSubToggle = document.getElementById('bg-sub-toggle');
    const bgSubPill = document.getElementById('bg-sub-pill');
    if (bgSubToggle && bgSubPill) {
      const want = !!ui.bgSubtractedView;
      bgSubToggle.checked = want;
      bgSubPill.classList.toggle('active', want);
    }
    if (typeof _updateBgSubPillEnabled === 'function') _updateBgSubPillEnabled();
    if (typeof _syncSubViewDependentControls === 'function') _syncSubViewDependentControls();
  }

  _updateCCVerifiedUI(verified) {
    const dot = document.getElementById('cc-warn-dot');
    const asterisk = document.getElementById('cc-warn-asterisk');
    const obsInput = document.getElementById('cc-obs');
    const show = verified === false;
    if (dot) dot.style.display = show ? 'inline-block' : 'none';
    if (asterisk) asterisk.style.display = show ? 'inline' : 'none';
    if (obsInput) obsInput.classList.toggle('cc-unverified', show);
  }

  _updateInfoBadge(tab) {
    const n = tab.rawBE.length;
    document.getElementById('data-info').textContent =
      n ? (tab.name + ' \u00b7 ' + n + ' pts') : 'no data';
    const comboLabel = document.getElementById('spec-combo-label');
    if (comboLabel) comboLabel.textContent = n ? (tab.name + ' \u00b7 ' + n + ' pts') : 'no data';
    document.getElementById('sb-pts').textContent = n || '\u2014';
      newBg[i] = stepH * (sumRight / totalInt);
    }
    bg = newBg;
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
      if (!tip) return;
      tip.textContent = '';
      const lines = el.dataset.xpsTip.split('\n');
      lines.forEach((line, i) => {
        if (i > 0) tip.appendChild(document.createElement('br'));
        tip.appendChild(document.createTextNode(line));
      });
      tip.classList.remove('tip-above', 'visible');
      const rect = el.getBoundingClientRect();
      const tipH = 160;
      const spaceBelow = window.innerHeight - rect.bottom;
      if (spaceBelow < tipH && rect.top > tipH) {
        tip.classList.add('tip-above');
        tip.style.top = (rect.top - tipH - 6) + 'px';
      } else {
        tip.style.top = (rect.bottom + 6) + 'px';
      }
      tip.style.left = Math.max(8, Math.min(rect.left, window.innerWidth - 320)) + 'px';
      tip.classList.add('visible');
    }, DELAY);
  }, true);
  document.addEventListener('mouseleave', function (e) {
    if (!(e.target instanceof Element) || !e.target.closest('[data-xps-tip]')) return;
    clearTimeout(timer);
    const tip = document.getElementById('xps-tooltip');
    if (tip) tip.classList.remove('visible');
  }, true);
})();

// ═══════════════════════════════════════════════════
// UNCERTAINTY VALIDATION
// ═══════════════════════════════════════════════════
function _validateUncertainties() {
  if (!state.fitResult?.backendResult?.individual_peaks) return { warnings: [], info: [] };
  // F1: a stale result's sigma and bounds describe the previous model; the
  // Results banner says so once — no per-parameter rule is judged on them
  if (_statsLiveState() === 'stale') return { warnings: [], info: [] };
  const warnings = [];
  const info = [];
  const stderrMap = _buildStderrMap(state.fitResult);
  const preFit = state.fitResult._preFit || {};
  // Map backend param names to pre-fit property names
  const nameMap = { center: 'center', fwhm: 'fwhm', fwhm_l: 'fwhm', amplitude: 'amplitude', gl_ratio: 'glMix' };

  for (const [rawId, params] of Object.entries(stderrMap)) {
    const p = getPeak(Number(rawId));
    if (!p) continue;
    // Rule 0: the fit did not determine this component at all. Reported once,
    // here, instead of the per-parameter alarms (or, after Auto-Fit's centre
    // lock, the neutral "locked" note) that would otherwise misdescribe it.
    if (_isUnsupported(p)) {
      warnings.push(`<li><b>${_escHtml(p.name)}:</b> ${_UNSUPPORTED_LABEL} — with the other components held as fitted, removing it does not make the fit significantly worse${p.support.f != null ? ' (F = ' + p.support.f.toFixed(1) + ', threshold 10)' : ''}. Its centre, width and uncertainties are not reported. Try another starting position or width, lock the centre where chemistry says it belongs, or drop the component.</li>`);
2379:  snap._modelProvenance = t ? _provenanceOf({ modelProvenance: t.modelProvenance, fitResult: state.fitResult }) : null;
2384:  tab.modelProvenance = snap._modelProvenance ? JSON.parse(JSON.stringify(snap._modelProvenance)) : null;
2413:  snap._modelProvenance = _provenanceOf(tab);
2447:function undo() {
2465:function redo() {
3431:      active.modelProvenance = _isLocalProvenance(data.fitStatistics)
4962:function updateChargeCorrection() {
5082:function getROIData() {
5953:  { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }
6440:function peakToBackendSpec(p) {
6980:    modelProvenance: (() => { const o = _opOwner(); return o && o.modelProvenance ? JSON.parse(JSON.stringify(o.modelProvenance)) : null; })(),
7018:    t.modelProvenance = snap.modelProvenance || null;
7030:  { const _t = _activeTab(); if (_t) _t.modelProvenance = snap.modelProvenance || null; }
7222:function _restampSupport() {
7355:  { const _t = typeof _activeTab === 'function' ? _activeTab() : null; if (_t) _t.modelProvenance = null; }
7370:  if (typeof _restampSupport === 'function') _restampSupport();
7374:  if (typeof _autoSnapshot === 'function') _autoSnapshot();
8000:    { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }   // a new result supersedes imported provenance
8058:  _autoSnapshot();
8092:  return (t && t.modelProvenance) || null;
8101:// point too (tab.modelProvenance, set by fromJSON, cleared by any new fit).
8105:  return !!(t && _isLocalProvenance(t.modelProvenance));
8139:  if (tab.modelProvenance) return JSON.parse(JSON.stringify(tab.modelProvenance));
8150:function _fitStatusText(fr) {
8174:    if (fq) { fq.textContent = _fitStatusText(fr); fq.setAttribute('data-xps-tip', tip); }
8541:  { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }   // a new result supersedes imported provenance
8561:  _autoSnapshot();
10268:    } : ((_activeTab() && _activeTab().modelProvenance) ? {
10269:      ..._activeTab().modelProvenance, reportable: false, caveat: _localFitCaveat(_activeTab().modelProvenance),
10351:    modelProvenance: tab.modelProvenance || null,
10427:      modelProvenance: t.modelProvenance || null,
10638:  active.modelProvenance = _isLocalProvenance(data.modelProvenance) ? data.modelProvenance : null;
10790:      modelProvenance: t.modelProvenance || null,
12185:    tgt.modelProvenance = srcProvenance ? { ...srcProvenance, copiedFrom: sourceTab.name } : null;
13967:function _autoSnapshot() {
14136:  tab.modelProvenance = null;   // the restored result governs the designation (unit A0)
16089:  { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }   // the replaced model's provenance does not describe these peaks

 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-MmJvm06Q' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-bUSBe7Rl' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index ea02c0a..bfc19b8 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -610,9 +610,28 @@ result if that key changed: amber notice, "Fit discarded (model edited)",
 previous peaks and result kept. Before this, a centre changed and locked
 mid-fit kept its edited value (`applyBackendResult` honours locks) under the
 server's χ², σ and fitted curve for a different model.
-Not covered by this rule (separate units): model replacement that
-keeps an older result (Find Peaks apply in the default window, undo/redo)
-and loaded files without convergence provenance. From the initial commit
+STATISTICS AFTER AN EDIT (unit F1, 2026-09-25; plan
+`docs/superpowers/plans/2026-09-25-f1-stale-statistics.md`): χ², σ, RMSE,
+the R-factor and the stored fitted curve are bound to their fit by the SAME
+key (`fitResult.startsModelKey`, now stamped by every creator — `runFit`,
+`runFitLocal`, `applyAutoFitResult`, re-stamped by `_restampSupport`); no
+second mechanism. One accessor, `_statsState(fr, key)` (`_statsLiveState()`,
+`_statsRecordState(t)`): `current` / `stale` (the model or its context
+changed since — an edit, a Find Peaks apply in the default window, an undo
+or history restore to other values) / `unverified` (no key: saved before
+this unit — values shown with a note to re-run). Stale: Results banner
+("belong to the previous model"), statistic / RMSE "—", no R panel, no σ;
+header "χ²ᵣ — (model changed)", status "—", "R: —"; no per-parameter
+uncertainty rule; CSV/XLSX a WARNING instead of the statistic, σ cells
+empty; TSV a NOTE (its columns are the current, unfitted model); figure no
+χ² and no stored "Fit" curve; chart and stack envelopes composed from the
+current peaks; saves keep the key (a reload judges again) and add
+`statisticsState` / `statisticsNote`. Refreshed from `updatePlot`
+(`_refreshStatsState`, Results carries `data-stats-state`). The model
+replacement that keeps an older result is thereby covered for the
+statistics. Not covered (separate units): loaded files without convergence
+provenance; `p._backendParams` still rides in a stale save (not displayed;
+the sealed fit record owns it). From the initial commit
 until this unit the local LM step had the wrong sign and returned the
 starting model as "Fit complete"; see
 `docs/superpowers/plans/2026-09-15-a01-local-lm-proof.md` and
diff --git a/tests/js/fit_acceptance.test.js b/tests/js/fit_acceptance.test.js
index 63e2e50..995460c 100644
--- a/tests/js/fit_acceptance.test.js
+++ b/tests/js/fit_acceptance.test.js
@@ -260,8 +260,9 @@ test('project save derives the designation from the objective for an older local
   const src = html.slice(start, end) + ';';
   const constLine = html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n');
   const fieldsAt = lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS'));
-  const helpers = lines.slice(fieldsAt, lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\n' + ['_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_localFitCaveat', '_startsForSave', '_startsIfCurrent', '_startsModelKey', '_startsRecordKey'].map(extractFn).join('\n');
-  const build = new Function('RefCore', '_roundBE', '_roundIntensity', constLine + '\n' + helpers + '\n' + src + '\nreturn buildTabData;')(
+  const helpers = lines.slice(fieldsAt, lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\n' + ['_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_localFitCaveat', '_startsForSave', '_startsIfCurrent', '_startsModelKey', '_startsRecordKey', '_statsState', '_statsRecordState', '_statsNote', '_statsSaveFields'].map(extractFn).join('\n');
+  const statsConsts = html.match(/^const _STATS_\w+_NOTE = .*$/mg).join('\n');
+  const build = new Function('RefCore', '_roundBE', '_roundIntensity', constLine + '\n' + statsConsts + '\n' + helpers + '\n' + src + '\nreturn buildTabData;')(
     { serializeRefOverlays: () => null }, a => a, a => a);
   const older = { id: 1, name: 't', rawBE: [1, 2], rawIntensity: [1, 1], ccShift: 0, peaks: [], nextId: 1, ui: {},
     fitResult: { chi: 1, chiReduced: 1e4, rmse: 100, objective: 'unweighted_residual_variance', be: [1, 2], bgIntensity: [0, 0], bgSubtracted: [1, 1] } };
@@ -296,7 +297,7 @@ test('_applyStatDisplay keeps header, tooltip, caption and value consistent thro
   const src = ['_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay'].map(extractFn).join('\n');
   const constLine = html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n');
   const dom = {}; const el = id => (dom[id] ||= { textContent: '', innerHTML: '', tip: null, setAttribute(k, v) { this.tip = v; }, removeAttribute() { this.tip = null; } });
-  const apply = new Function('document', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_updateLocalModelBanner', constLine + '\n' + src + '\nreturn _applyStatDisplay;')({ getElementById: el }, 'CHI', 'LOCAL', () => {});
+  const apply = new Function('document', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_updateLocalModelBanner', 'state', constLine + '\n' + src + '\nreturn _applyStatDisplay;')({ getElementById: el }, 'CHI', 'LOCAL', () => {}, { fitResult: null });
   apply({ objective: 'unweighted_residual_variance', chiReduced: 12345 });
   assert.equal(dom['fit-quality'].textContent, 'Residual variance = 12345.00 (starting point)');
   assert.equal(dom['fit-quality'].tip, 'LOCAL'); assert.match(dom['sb-chi-caption'].innerHTML, /starting point/); assert.equal(dom['sb-chi'].textContent, '12345.000');
@@ -329,7 +330,7 @@ test('_applyStatDisplay clears header, tooltip, caption and value together on lo
   const src = ['_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay'].map(extractFn).join('\n');
   const constLine = html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n');
   const dom = {}; const el = id => (dom[id] ||= { textContent: '', innerHTML: '', tip: null, setAttribute(k, v) { this.tip = v; }, removeAttribute() { this.tip = null; } });
-  const apply = new Function('document', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_updateLocalModelBanner', constLine + '\n' + src + '\nreturn _applyStatDisplay;')({ getElementById: el }, 'CHI', 'LOCAL', () => {});
+  const apply = new Function('document', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_updateLocalModelBanner', 'state', constLine + '\n' + src + '\nreturn _applyStatDisplay;')({ getElementById: el }, 'CHI', 'LOCAL', () => {}, { fitResult: null });
   apply({ objective: 'unweighted_residual_variance', chiReduced: 999 });
   apply(null);
   assert.match(dom['fit-quality'].innerHTML, /&mdash;/); assert.equal(dom['fit-quality'].tip, null);
@@ -487,7 +488,7 @@ test('the sidebar banner shows on a stack tab whose visible entries draw a local
   assert.equal(run({ isStack: true, entries: [{ sourceTabId: 2, visible: true, showFit: false }] }).style.display, 'none', 'fit curves hidden → no designation needed');
   assert.equal(run({ isStack: true, entries: [{ sourceTabId: 3, visible: true, showFit: true }] }).style.display, 'none', 'weighted source only');
   const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
-  assert.match(grab('function _applyStatDisplay(', 900), /_updateLocalModelBanner\(\)/, 'activation/result changes refresh the banner');
+  assert.match(grab('function _applyStatDisplay(', 1800), /_updateLocalModelBanner\(\)/, 'activation/result changes refresh the banner');
   const legendAt = html.indexOf("row.querySelector('.name').textContent = name;");
   assert.match(html.slice(legendAt, legendAt + 2500), /_updateLocalModelBanner\(\)/, 'stack legend rebuild refreshes the banner');
 });
@@ -532,7 +533,8 @@ test('W1 helpers: weighted local results are chi-square but still designated; le
 
 // ── W1 Codex round 1: the TSV export's warning follows the GOVERNING objective (behavioural) ──
 test('TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result', () => {
-  const src = ['_isUnweightedLocal', '_isLocalProvenance', '_isLocalFit', '_isLocalModel', '_localFitCaveat', '_governingProvenance', 'exportResults', '_isUnsupported'].map(extractFn).join('\n');
+  const src = ['_isUnweightedLocal', '_isLocalProvenance', '_isLocalFit', '_isLocalModel', '_localFitCaveat', '_governingProvenance', 'exportResults', '_isUnsupported'].map(extractFn).join('\n')
+    + '\nconst _statsLiveState = () => "current";';   // F1's stale note is pinned in stale_statistics.test.js
   const consts = html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n');
   const run = (fitResult, modelProvenance) => {
     let text = null;
diff --git a/tests/js/local_lm_descent.test.js b/tests/js/local_lm_descent.test.js
index 3901fdc..342ad9f 100644
--- a/tests/js/local_lm_descent.test.js
+++ b/tests/js/local_lm_descent.test.js
@@ -40,8 +40,8 @@ const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'a
   'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
   'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
   '_computeRFactor', '_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel', '_governingProvenance', '_localFitCaveat', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay', '_updateLocalModelBanner',
-  '_componentSupportCore', '_supportRootOf', '_applySupportVerdicts'];
-const CAVEAT_CONST = (html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg) || []).join('\n');
+  '_componentSupportCore', '_supportRootOf', '_applySupportVerdicts', '_statsState', '_statsLiveState'];
+const CAVEAT_CONST = (html.match(/^const (_LOCAL_FIT_CAVEAT\w*|_STATS_\w+_NOTE) = .*$/mg) || []).join('\n');
 
 // One isolated environment per test: a fresh `state`, a stub DOM, and the
 // extracted functions bound to them.
diff --git a/tests/js/unsupported_components.test.js b/tests/js/unsupported_components.test.js
index 7e002bd..5de224f 100644
--- a/tests/js/unsupported_components.test.js
+++ b/tests/js/unsupported_components.test.js
@@ -114,6 +114,7 @@ function pageEnv(fns, extraArgs = {}) {
     renderQuantify: () => {}, recalcQuantify: () => {}, _detectPeakRSF: () => ({ key: 'C 1s', rsf: 1 }), SCOFIELD_RSF: { 'C 1s': 1 }, notify: () => {},
     _clearDisallowedChargeRef: () => {}, _updateLocalModelBanner: () => {}, _updateLockAllBtn: () => {}, renderPeakForm: () => '', _highlightChartPeak: () => {},
     _roiWindowStatus: () => ({ state: 'ok', n: 0 }), _patchPeakCardsForCentre: () => {},   // the ROI / centre warnings: tests/js/roi_clamp_centre_warning.test.js
+    _statsLiveState: () => 'current', _STATS_STALE_NOTE: '', _STATS_UNVERIFIED_NOTE: '',   // F1's stale statistics: tests/js/stale_statistics.test.js
     _isChargeRefAllowed: () => false, _fitStatLabel: () => 'χ²ᵣ', _isUnweightedLocal: () => false, _applyStatCaption: () => {}, _applyStatDisplay: () => {},
     _CHISQ_TOOLTIP: '', _LOCALFIT_TOOLTIP: '', _startsSummaryText: () => '', _startsChosenText: () => '', _startsIfCurrent: () => null,
     _isLocalModel: () => false, _updateRFactorUI: () => {}, _activeTab: () => ({}), _renderRFactorPanel: () => '', _statIsChi: true,
diff --git a/tests/test_browser_find_peaks_full_window.py b/tests/test_browser_find_peaks_full_window.py
index c20dab7..079860f 100644
--- a/tests/test_browser_find_peaks_full_window.py
+++ b/tests/test_browser_find_peaks_full_window.py
@@ -150,6 +150,10 @@ def _load_c1s_with_stale_narrow_fit(pg):
             be: narrowBE, bgIntensity: narrowBG, bgSubtracted: narrowSub,
             fittedY: narrowBE.map((b, i) => narrowSub[i] + 300),
             roiRange: { min: '278.0', max: '290.4' },
+            // a real fit stores its R-factor with the result; since F1
+            // (2026-09-25) the status bar is re-applied from the stored
+            // result on every repaint, so it must be where a fit puts it
+            rFactor: { rPct: 3.2, level: 'good' },
         };
         document.getElementById('roi-min').value = 278.0;
         document.getElementById('roi-max').value = 298.0;
@@ -247,6 +251,34 @@ def test_checkbox_off_preserves_todays_cropped_behavior(browser, server):
         pg.close()
 
 
+def test_checkbox_off_marks_a_keyed_result_stale_after_find_peaks_apply(browser, server):
+    """F1 (2026-09-25): the default Find Peaks apply keeps the old result over
+    a REPLACED model. A result that carries its fit key (every result since
+    the scattered-starts unit) is then judged against the new model: its
+    chi-square, sigma and R are marked as the previous model's, and the
+    chart's envelope is composed from the new peaks, not the old curve. A
+    keyless result (the test above) is shown as before, with the unverified
+    note."""
+    pg = _new_page(browser, server)
+    try:
+        _load_c1s_with_stale_narrow_fit(pg)
+        pg.evaluate("() => { state.fitResult.startsModelKey = _startsLiveKey(); renderResults(); }")
+        assert pg.evaluate("() => _statsLiveState()") == "current"
+        _run_and_apply_find_peaks(pg, full_window=False)
+        assert pg.evaluate("() => state.fitResult !== null"), "the old result is kept, as before"
+        st = pg.evaluate("""() => ({ state: _statsLiveState(),
+            header: document.getElementById('fit-quality').textContent,
+            sbChi: document.getElementById('sb-chi').textContent,
+            sbRuns: document.getElementById('sb-runs').textContent,
+            banner: !!document.querySelector('#results-area .stats-stale-note') })""")
+        assert st["state"] == "stale", st
+        assert "model changed" in st["header"], st
+        assert st["sbChi"] == "\u2014" and st["sbRuns"] == "R: \u2014", st
+        assert st["banner"], st
+    finally:
+        pg.close()
+
+
 def test_checkbox_on_extends_fit_and_background_to_the_full_window(browser, server):
     """The actual fix: checked must make the background/fit-curve span
     the FULL user-set ROI (278-298), not the stale frozen 278.0-290.4
# F1 — statistics after an edit belong to the previous model (2026-09-25)

Branch `fix-stale-statistics` off main `4475023` (caM unit deployed). Owner's
brief, first of the three sweep units: "Reuse step (b)'s fit key (model +
background/ROI/anchors/charge shift). When the current key does not match
the key the statistics came from, mark χ², σ and R stale in the Results
panel, CSV, XLSX, TSV, figure export and saves — say plainly they belong to
the previous model, or omit them. Do not build a second binding mechanism;
this is a down payment on the sealed fit record and must be absorbable by
it. Enumerate every consumer of the statistics first."

Source finding: `docs/findings/2026-09-25-fail-open-guards-sweep.md` H1
(`sweep-fail-open-guards`).

## 1. The one mechanism

The key already exists and already binds two things to their fit:
`_startsModelKey(peaks, ui, ccShift, anchors)` — every peak field a request
reads, background type and window, endpoint averaging, Shirley iterations,
ROI, manual anchors, charge shift. `fitResult.startsModelKey` (the starts
evidence) and `p.support.fitKey` (step (b)'s verdicts) both hold it, taken
after the result is applied, and are compared with `_startsLiveKey()` /
`_startsRecordKey(t)` at every read. F1 adds NO new key and no new field
name: every creator of a fit result stamps `fitResult.startsModelKey`, and
ONE accessor classifies a result against a key:

- `current` — the key matches: the statistics describe the model shown;
- `stale` — the key differs: they belong to the previous model;
- `unverified` — the result carries no key (saved before this unit, or an
  older local / Auto-Fit result): whether it described the saved model
  cannot be known. Shown, with a plain note to re-run. Treating these as
  stale would hide χ² and σ on nearly every existing lab project.

The sealed fit record absorbs this directly: its record will carry the key
and the statistics together; `_statsState` becomes a read of the seal.

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

## 4. Verification

- JS: `tests/js/stale_statistics.test.js` (12 tests: the accessor; every
  creator stamps the key and `_restampSupport` re-stamps the result; the
  Results panel current / stale / unverified, header, status bar, R,
  uncertainty panel on stubs; CSV / XLSX / TSV run for real on stubs;
  chart / stack / figure / spectrum-save curve gates; the saves' fields;
  the refresh re-renders once per state change and writes R on both
  paths). Existing sandboxes in `local_lm_descent`, `fit_acceptance`,
  `unsupported_components` given the accessor (or a `'current'` stub).
- Browser (`scratchpad/browser_check_f1.py`, :5151, committed UCl4-graphite
  project): on load every tab is `unverified` (committed before this unit)
  → note shown, values kept; Run Fit → `current`; centre edit → `stale`:
  header "χ²ᵣ — (model changed)", status "—", "R: —", banner, no σ, no R
  panel, chart envelope NOT the stored curve; CSV head carries the
  WARNING; spectrum save has `statisticsState: 'stale'` + key; undo →
  `current` again; project save → reload → `current` (the key survives the
  round trip); the stale spectrum save reloads `stale`; a stack entry over
  the edited source does not use the stored curve. Auto-Fit C1s Graphite on
  C1s Scan_3 → `current` with every centre locked (the re-stamp). No page
  errors.
- pytest: `test_browser_find_peaks_full_window.py`'s default-path guard
  hand-wrote an R display the injected result did not carry; the fixture
  now stores `rFactor` where a fit puts it. New test there: a KEYED result
  kept over a Find Peaks apply is `stale` (header, status, R, banner).

## 5. Codex rounds

(filled in as they run)

codex
The main display and export paths use the shared key as intended. I’m checking round trips and paths where the key may stay current incorrectly; the new unit tests mostly stub the key, so they don’t establish that coverage.
exec
/bin/zsh -lc "git diff main..HEAD -- tests/js/fit_acceptance.test.js tests/js/local_lm_descent.test.js tests/js/unsupported_components.test.js tests/test_browser_find_peaks_full_window.py; sed -n '2360,2485p' templates/index.html; sed -n '3830,3890p' templates/index.html; sed -n '4962,5125p' templates/index.html; sed -n '6440,6530p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-uJICbqZC' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-gehESzOm' (errno=Operation not permitted)
diff --git a/tests/js/fit_acceptance.test.js b/tests/js/fit_acceptance.test.js
index 63e2e50..995460c 100644
--- a/tests/js/fit_acceptance.test.js
+++ b/tests/js/fit_acceptance.test.js
@@ -260,8 +260,9 @@ test('project save derives the designation from the objective for an older local
   const src = html.slice(start, end) + ';';
   const constLine = html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n');
   const fieldsAt = lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS'));
-  const helpers = lines.slice(fieldsAt, lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\n' + ['_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_localFitCaveat', '_startsForSave', '_startsIfCurrent', '_startsModelKey', '_startsRecordKey'].map(extractFn).join('\n');
-  const build = new Function('RefCore', '_roundBE', '_roundIntensity', constLine + '\n' + helpers + '\n' + src + '\nreturn buildTabData;')(
+  const helpers = lines.slice(fieldsAt, lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\n' + ['_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_localFitCaveat', '_startsForSave', '_startsIfCurrent', '_startsModelKey', '_startsRecordKey', '_statsState', '_statsRecordState', '_statsNote', '_statsSaveFields'].map(extractFn).join('\n');
+  const statsConsts = html.match(/^const _STATS_\w+_NOTE = .*$/mg).join('\n');
+  const build = new Function('RefCore', '_roundBE', '_roundIntensity', constLine + '\n' + statsConsts + '\n' + helpers + '\n' + src + '\nreturn buildTabData;')(
     { serializeRefOverlays: () => null }, a => a, a => a);
   const older = { id: 1, name: 't', rawBE: [1, 2], rawIntensity: [1, 1], ccShift: 0, peaks: [], nextId: 1, ui: {},
     fitResult: { chi: 1, chiReduced: 1e4, rmse: 100, objective: 'unweighted_residual_variance', be: [1, 2], bgIntensity: [0, 0], bgSubtracted: [1, 1] } };
@@ -296,7 +297,7 @@ test('_applyStatDisplay keeps header, tooltip, caption and value consistent thro
   const src = ['_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay'].map(extractFn).join('\n');
   const constLine = html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n');
   const dom = {}; const el = id => (dom[id] ||= { textContent: '', innerHTML: '', tip: null, setAttribute(k, v) { this.tip = v; }, removeAttribute() { this.tip = null; } });
-  const apply = new Function('document', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_updateLocalModelBanner', constLine + '\n' + src + '\nreturn _applyStatDisplay;')({ getElementById: el }, 'CHI', 'LOCAL', () => {});
+  const apply = new Function('document', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_updateLocalModelBanner', 'state', constLine + '\n' + src + '\nreturn _applyStatDisplay;')({ getElementById: el }, 'CHI', 'LOCAL', () => {}, { fitResult: null });
   apply({ objective: 'unweighted_residual_variance', chiReduced: 12345 });
   assert.equal(dom['fit-quality'].textContent, 'Residual variance = 12345.00 (starting point)');
   assert.equal(dom['fit-quality'].tip, 'LOCAL'); assert.match(dom['sb-chi-caption'].innerHTML, /starting point/); assert.equal(dom['sb-chi'].textContent, '12345.000');
@@ -329,7 +330,7 @@ test('_applyStatDisplay clears header, tooltip, caption and value together on lo
   const src = ['_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay'].map(extractFn).join('\n');
   const constLine = html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n');
   const dom = {}; const el = id => (dom[id] ||= { textContent: '', innerHTML: '', tip: null, setAttribute(k, v) { this.tip = v; }, removeAttribute() { this.tip = null; } });
-  const apply = new Function('document', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_updateLocalModelBanner', constLine + '\n' + src + '\nreturn _applyStatDisplay;')({ getElementById: el }, 'CHI', 'LOCAL', () => {});
+  const apply = new Function('document', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_updateLocalModelBanner', 'state', constLine + '\n' + src + '\nreturn _applyStatDisplay;')({ getElementById: el }, 'CHI', 'LOCAL', () => {}, { fitResult: null });
   apply({ objective: 'unweighted_residual_variance', chiReduced: 999 });
   apply(null);
   assert.match(dom['fit-quality'].innerHTML, /&mdash;/); assert.equal(dom['fit-quality'].tip, null);
@@ -487,7 +488,7 @@ test('the sidebar banner shows on a stack tab whose visible entries draw a local
   assert.equal(run({ isStack: true, entries: [{ sourceTabId: 2, visible: true, showFit: false }] }).style.display, 'none', 'fit curves hidden → no designation needed');
   assert.equal(run({ isStack: true, entries: [{ sourceTabId: 3, visible: true, showFit: true }] }).style.display, 'none', 'weighted source only');
   const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
-  assert.match(grab('function _applyStatDisplay(', 900), /_updateLocalModelBanner\(\)/, 'activation/result changes refresh the banner');
+  assert.match(grab('function _applyStatDisplay(', 1800), /_updateLocalModelBanner\(\)/, 'activation/result changes refresh the banner');
   const legendAt = html.indexOf("row.querySelector('.name').textContent = name;");
   assert.match(html.slice(legendAt, legendAt + 2500), /_updateLocalModelBanner\(\)/, 'stack legend rebuild refreshes the banner');
 });
@@ -532,7 +533,8 @@ test('W1 helpers: weighted local results are chi-square but still designated; le
 
 // ── W1 Codex round 1: the TSV export's warning follows the GOVERNING objective (behavioural) ──
 test('TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result', () => {
-  const src = ['_isUnweightedLocal', '_isLocalProvenance', '_isLocalFit', '_isLocalModel', '_localFitCaveat', '_governingProvenance', 'exportResults', '_isUnsupported'].map(extractFn).join('\n');
+  const src = ['_isUnweightedLocal', '_isLocalProvenance', '_isLocalFit', '_isLocalModel', '_localFitCaveat', '_governingProvenance', 'exportResults', '_isUnsupported'].map(extractFn).join('\n')
+    + '\nconst _statsLiveState = () => "current";';   // F1's stale note is pinned in stale_statistics.test.js
   const consts = html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n');
   const run = (fitResult, modelProvenance) => {
     let text = null;
diff --git a/tests/js/local_lm_descent.test.js b/tests/js/local_lm_descent.test.js
index 3901fdc..342ad9f 100644
--- a/tests/js/local_lm_descent.test.js
+++ b/tests/js/local_lm_descent.test.js
@@ -40,8 +40,8 @@ const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'a
   'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
   'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
   '_computeRFactor', '_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel', '_governingProvenance', '_localFitCaveat', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay', '_updateLocalModelBanner',
-  '_componentSupportCore', '_supportRootOf', '_applySupportVerdicts'];
-const CAVEAT_CONST = (html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg) || []).join('\n');
+  '_componentSupportCore', '_supportRootOf', '_applySupportVerdicts', '_statsState', '_statsLiveState'];
+const CAVEAT_CONST = (html.match(/^const (_LOCAL_FIT_CAVEAT\w*|_STATS_\w+_NOTE) = .*$/mg) || []).join('\n');
 
 // One isolated environment per test: a fresh `state`, a stub DOM, and the
 // extracted functions bound to them.
diff --git a/tests/js/unsupported_components.test.js b/tests/js/unsupported_components.test.js
index 7e002bd..5de224f 100644
--- a/tests/js/unsupported_components.test.js
+++ b/tests/js/unsupported_components.test.js
@@ -114,6 +114,7 @@ function pageEnv(fns, extraArgs = {}) {
     renderQuantify: () => {}, recalcQuantify: () => {}, _detectPeakRSF: () => ({ key: 'C 1s', rsf: 1 }), SCOFIELD_RSF: { 'C 1s': 1 }, notify: () => {},
     _clearDisallowedChargeRef: () => {}, _updateLocalModelBanner: () => {}, _updateLockAllBtn: () => {}, renderPeakForm: () => '', _highlightChartPeak: () => {},
     _roiWindowStatus: () => ({ state: 'ok', n: 0 }), _patchPeakCardsForCentre: () => {},   // the ROI / centre warnings: tests/js/roi_clamp_centre_warning.test.js
+    _statsLiveState: () => 'current', _STATS_STALE_NOTE: '', _STATS_UNVERIFIED_NOTE: '',   // F1's stale statistics: tests/js/stale_statistics.test.js
     _isChargeRefAllowed: () => false, _fitStatLabel: () => 'χ²ᵣ', _isUnweightedLocal: () => false, _applyStatCaption: () => {}, _applyStatDisplay: () => {},
     _CHISQ_TOOLTIP: '', _LOCALFIT_TOOLTIP: '', _startsSummaryText: () => '', _startsChosenText: () => '', _startsIfCurrent: () => null,
     _isLocalModel: () => false, _updateRFactorUI: () => {}, _activeTab: () => ({}), _renderRFactorPanel: () => '', _statIsChi: true,
diff --git a/tests/test_browser_find_peaks_full_window.py b/tests/test_browser_find_peaks_full_window.py
index c20dab7..079860f 100644
--- a/tests/test_browser_find_peaks_full_window.py
+++ b/tests/test_browser_find_peaks_full_window.py
@@ -150,6 +150,10 @@ def _load_c1s_with_stale_narrow_fit(pg):
             be: narrowBE, bgIntensity: narrowBG, bgSubtracted: narrowSub,
             fittedY: narrowBE.map((b, i) => narrowSub[i] + 300),
             roiRange: { min: '278.0', max: '290.4' },
+            // a real fit stores its R-factor with the result; since F1
+            // (2026-09-25) the status bar is re-applied from the stored
+            // result on every repaint, so it must be where a fit puts it
+            rFactor: { rPct: 3.2, level: 'good' },
         };
         document.getElementById('roi-min').value = 278.0;
         document.getElementById('roi-max').value = 298.0;
@@ -247,6 +251,34 @@ def test_checkbox_off_preserves_todays_cropped_behavior(browser, server):
         pg.close()
 
 
+def test_checkbox_off_marks_a_keyed_result_stale_after_find_peaks_apply(browser, server):
+    """F1 (2026-09-25): the default Find Peaks apply keeps the old result over
+    a REPLACED model. A result that carries its fit key (every result since
+    the scattered-starts unit) is then judged against the new model: its
+    chi-square, sigma and R are marked as the previous model's, and the
+    chart's envelope is composed from the new peaks, not the old curve. A
+    keyless result (the test above) is shown as before, with the unverified
+    note."""
+    pg = _new_page(browser, server)
+    try:
+        _load_c1s_with_stale_narrow_fit(pg)
+        pg.evaluate("() => { state.fitResult.startsModelKey = _startsLiveKey(); renderResults(); }")
+        assert pg.evaluate("() => _statsLiveState()") == "current"
+        _run_and_apply_find_peaks(pg, full_window=False)
+        assert pg.evaluate("() => state.fitResult !== null"), "the old result is kept, as before"
+        st = pg.evaluate("""() => ({ state: _statsLiveState(),
+            header: document.getElementById('fit-quality').textContent,
+            sbChi: document.getElementById('sb-chi').textContent,
+            sbRuns: document.getElementById('sb-runs').textContent,
+            banner: !!document.querySelector('#results-area .stats-stale-note') })""")
+        assert st["state"] == "stale", st
+        assert "model changed" in st["header"], st
+        assert st["sbChi"] == "\u2014" and st["sbRuns"] == "R: \u2014", st
+        assert st["banner"], st
+    finally:
+        pg.close()
+
+
 def test_checkbox_on_extends_fit_and_background_to_the_full_window(browser, server):
     """The actual fix: checked must make the background/fit-curve span
     the FULL user-set ROI (278-298), not the stale frozen 278.0-290.4
  const t = _activeTab();
  if (!t || t.isStack) return null;
  if (!t.undoStack) t.undoStack = [];
  if (!t.redoStack) t.redoStack = [];
  return t;
}

// Undo snapshots are deep copies of state.peaks. An action that ALSO changes
// endpoint averaging (today: applying Find Peaks suggestions, which sets the
// panel to what the engine fitted at) passes { endpointAvg } so the snapshot
// carries the pre-action value as a non-index property; undo/redo restore it
// to the panel AND the tab record. Peak-only actions leave it absent.
function _peaksSnapshot(extra) {
  const snap = JSON.parse(JSON.stringify(state.peaks));
  if (extra && extra.endpointAvg !== undefined) snap._endpointAvg = String(extra.endpointAvg);
  // The model's provenance (imported local fit = starting point) travels
  // with the model through undo/redo (unit A0).
  const t = _historyTab();
  // The active tab's live result is state.fitResult (the record is synced on switch-away).
  snap._modelProvenance = t ? _provenanceOf({ modelProvenance: t.modelProvenance, fitResult: state.fitResult }) : null;
  return snap;
}
function _restoreSnapshotProvenance(tab, snap) {
  if (!tab || !snap) return;
  tab.modelProvenance = snap._modelProvenance ? JSON.parse(JSON.stringify(snap._modelProvenance)) : null;
}
function _restoreSnapshotEndpointAvg(tab, snap) {
  if (!snap || snap._endpointAvg === undefined) return;
  const el = document.getElementById('bg-endpoint-avg');
  if (el) el.value = snap._endpointAvg;
  if (tab && tab.ui) tab.ui.endpointAvg = snap._endpointAvg;
}
function _pushSnapshot(t, snap) {
  if (!t.undoStack) t.undoStack = [];
  if (!t.redoStack) t.redoStack = [];
  t.undoStack.push(snap);
  if (t.undoStack.length > MAX_UNDO) t.undoStack.shift();
  t.redoStack.length = 0;
  _updateUndoButtons();
}
function pushUndo(extra) {
  _flushUndoDebounce();     // a pending slider burst is OLDER than this action: it goes first
  const t = _historyTab();
  if (!t) return;
  _pushSnapshot(t, _peaksSnapshot(extra));
}
// History entry for a record that is NOT necessarily active (batch
// propagation writes into target records): snapshot that record's own peaks.
function _pushUndoFor(tab, extra) {
  _flushUndoDebounce();
  if (!tab || tab.isStack) return;
  const snap = JSON.parse(JSON.stringify(tab.peaks || []));
  if (extra && extra.endpointAvg !== undefined) snap._endpointAvg = String(extra.endpointAvg);
  snap._modelProvenance = _provenanceOf(tab);
  _pushSnapshot(tab, snap);
}

// Debounced undo for slider-style edits: ONE entry per burst. The owner and
// the snapshot are bound when the burst starts, so the timer can only ever
// push onto the record that was being edited — never onto whichever tab is
// active when it fires (Codex round 1: A's timer cleared B's redo stack).
let _undoDebounce = null;   // { owner, snap }
function _pushUndoDebounced() {
  const t = _historyTab();
  if (!t) return;
  if (!_undoDebounce || _undoDebounce.owner !== t) {
    if (_undoDebounce) _flushUndoDebounce();
    _undoDebounce = { owner: t, snap: _peaksSnapshot() };
  }
  clearTimeout(_undoDebounceTimer);
  _undoDebounceTimer = setTimeout(_flushUndoDebounce, 500);
}
function _flushUndoDebounce() {
  clearTimeout(_undoDebounceTimer);
  const d = _undoDebounce; _undoDebounce = null;
  if (!d || !_ownerLive(d.owner)) return;      // owner closed: drop the entry
  _pushSnapshot(d.owner, d.snap);
}

function _updateUndoButtons() {
  const t = _activeTab();
  const u = document.getElementById('btn-undo');
  const r = document.getElementById('btn-redo');
  if (u) u.disabled = !(t && !t.isStack && t.undoStack && t.undoStack.length);
  if (r) r.disabled = !(t && !t.isStack && t.redoStack && t.redoStack.length);
}

function undo() {
  _flushUndoDebounce();     // never undo past a pending burst
  const t = _historyTab();
  if (!t || !t.undoStack.length) return;
  const snap = t.undoStack.pop();
  // Mirror the averaging into the redo entry only when the undo entry
  // carried one, so a redo re-applies exactly what the action did.
  t.redoStack.push(_peaksSnapshot(snap._endpointAvg !== undefined
    ? { endpointAvg: document.getElementById('bg-endpoint-avg')?.value } : null));
  state.peaks = snap;
  _restoreSnapshotEndpointAvg(t, snap);
  _restoreSnapshotProvenance(t, snap);
  renderPeakList();
  updatePlot();
  renderResults();   // the restored model's designation (or its absence) must be visible immediately
  _updateUndoButtons();
}

function redo() {
  _flushUndoDebounce();
  const t = _historyTab();
  if (!t || !t.redoStack.length) return;
  const snap = t.redoStack.pop();
  t.undoStack.push(_peaksSnapshot(snap._endpointAvg !== undefined
    ? { endpointAvg: document.getElementById('bg-endpoint-avg')?.value } : null));
  state.peaks = snap;
  _restoreSnapshotEndpointAvg(t, snap);
  _restoreSnapshotProvenance(t, snap);
  renderPeakList();
  updatePlot();
  renderResults();   // the restored model's designation (or its absence) must be visible immediately
  _updateUndoButtons();
}

// ═══════════════════════════════════════════════════
// STACK FEATURE — data model
// ═══════════════════════════════════════════════════
// Wong colorblind-safe palette for stack-entry traces.
const STACK_PALETTE = ['#E69F00','#56B4E9','#009E73','#F0E442','#0072B2','#D55E00','#CC79A7'];
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
    }
    // Bkgrd Sub: restore checked state, sync visual class, refresh enable,
    // and re-gate the dependent overlay controls so they reflect the
    // restored sub-view state.
    const bgSubToggle = document.getElementById('bg-sub-toggle');
    const bgSubPill = document.getElementById('bg-sub-pill');
    if (bgSubToggle && bgSubPill) {
function updateChargeCorrection() {
  const prevShift = state.ccShift;
  const method = document.getElementById('cc-method').value;
  const refField = document.getElementById('cc-ref-field');
  const targetField = document.getElementById('cc-target-field');

  refField.style.display = 'none';
  targetField.style.display = 'none';

  if (method === 'c1s') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    state.ccShift = isNaN(obs) ? 0 : obs - 284.5;
    refField.style.display = 'block';
    document.getElementById('cc-lit').value = '284.5';
  } else if (method === 'c1s-adv') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    state.ccShift = isNaN(obs) ? 0 : obs - 284.8;
    refField.style.display = 'block';
    document.getElementById('cc-lit').value = '284.8';
  } else if (method === 'au4f') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    state.ccShift = isNaN(obs) ? 0 : obs - 83.98;
    refField.style.display = 'block';
    document.getElementById('cc-lit').value = '83.98';
  } else if (method === 'b1s-b2o3') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    state.ccShift = isNaN(obs) ? 0 : obs - 192.99;
    refField.style.display = 'block';
    document.getElementById('cc-lit').value = '192.99';
  } else if (method === 'n1s-bn') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    state.ccShift = isNaN(obs) ? 0 : obs - 398.31;
    refField.style.display = 'block';
    document.getElementById('cc-lit').value = '398.31';
  } else if (method === 'b1s-bn') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    state.ccShift = isNaN(obs) ? 0 : obs - 190.74;
    refField.style.display = 'block';
    document.getElementById('cc-lit').value = '190.74';
  } else if (method === 'custom') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    const lit = parseFloat(document.getElementById('cc-lit').value);
    state.ccShift = (isNaN(obs) || isNaN(lit)) ? 0 : obs - lit;
    refField.style.display = 'block';
    targetField.style.display = 'block';
  } else {
    state.ccShift = 0;
  }

  // Shift all energy-dependent values by the change in correction
  const delta = state.ccShift - prevShift;
  if (delta !== 0) {
    // ROI boundaries
    const roiMinEl = document.getElementById('roi-min');
    const roiMaxEl = document.getElementById('roi-max');
    const roiMinVal = parseFloat(roiMinEl.value);
    const roiMaxVal = parseFloat(roiMaxEl.value);
    if (!isNaN(roiMinVal)) roiMinEl.value = (roiMinVal - delta).toFixed(1);
    if (!isNaN(roiMaxVal)) roiMaxEl.value = (roiMaxVal - delta).toFixed(1);

    // Background endpoints
    const bgStartEl = document.getElementById('bg-start');
    const bgEndEl = document.getElementById('bg-end');
    const bgStartVal = parseFloat(bgStartEl.value);
    const bgEndVal = parseFloat(bgEndEl.value);
    if (!isNaN(bgStartVal)) bgStartEl.value = (bgStartVal - delta).toFixed(1);
    if (!isNaN(bgEndVal)) bgEndEl.value = (bgEndVal - delta).toFixed(1);

    // Peak centers
    for (const p of state.peaks) {
      p.center -= delta;
    }

    // Manual background anchors. Anchors are DATA-ATTACHED like peak
    // centers (x = a data point's corrected BE at placement time, y = that
    // point's intensity), so they follow the same -delta migration as the
    // ROI/bg fields and peak centers above — NOT the reference-marker
    // convention (literature markers stay at nominal corrected BE). y is
    // untouched: intensity is unaffected by charge correction. Saved files
    // need no migration — anchors persist alongside the tab's ccShift, so
    // every save is a self-consistent snapshot.
    const ccAnchors = _getManualAnchors();
    for (const a of ccAnchors) {
      a.x -= delta;
    }

    // Background cache is no longer valid after CC shift
    _invalidateBgCache();
  }

  const shift = -state.ccShift;
  document.getElementById('cc-shift-display').textContent = (shift >= 0 ? '+' : '') + shift.toFixed(3) + ' eV';
  updatePlot();
  // Re-render the per-peak panels so the C 1s graphite checkbox
  // appears/disappears reactively when the method changes (and any
  // stale isChargeReference flags are cleared by renderPeakList).
  renderPeakList();
  // Reference Lines panel shows the corrected range + a not-charge-corrected
  // hint — both go stale when the correction changes.
  if (typeof _refOnTabChange === 'function') _refOnTabChange();
  // fix #5: updatePlot() rebuilds the main chart at the corrected axis, but the
  // xpsRefLinesPlugin gates on `chart === state.chart` and is skipped on the
  // `new Chart()` first paint (the same render-timing gap _refRenderReferenceChart
  // already works around). renderPeakList/_refOnTabChange only refresh panel/legend
  // DOM — no chart repaint — so element reference overlays (lines, bands, labels)
  // would vanish until the next hover/toggle. Re-issue the guarded reference-overlay
  // repaint so they stay painted through a charge-correction change. Leaf-level
  // chart.update('none'); positioning math and ccShift are untouched (overlays stay
  // at nominal corrected BE), and it is a no-op when no chart/spectrum/overlays exist.
  if (typeof _refRepaint === 'function') _refRepaint();
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
  // on intensity)
  const d = [];
function peakToBackendSpec(p) {
  // All initial values go at top level — fitting.py reads spec.get("center") etc.
  const spec = {
    id: String(p.id),
    name: p.name,
    center: p.center,
    amplitude: p.amplitude,
    fwhm: p.fwhm,
    amplitude_min: 0,
    fix_center: !!p.fixCenter,
    fix_fwhm: !!p.fixFwhm,
    fix_amplitude: !!p.fixAmplitude,
    fix_gl_ratio: !!p.fixGlMix
  };
  const shape = p.shape;
  if (shape === 'Gaussian') {
    spec.shape = 'gaussian';
  } else if (shape === 'Lorentzian') {
    spec.shape = 'lorentzian';
  } else if (shape === 'Voigt') {
    // A03 (2026-09-22): Voigt IS the fixed 50/50 mix the page draws, exports
    // and fits locally (evalPeak: eta = 0.5; runFitLocal holds it). Until A03
    // the request sent eta FREE from 0.3, so the server fitted a mix the page
    // never showed — on the 90 committed Voigt targets 60 of 180 components
    // went to pure Gaussian and 16 to pure Lorentzian, and every area the page
    // reported for them was the 0.5 curve's, up to 20 % off the fitted one.
    // Fixed on both sides; use GL to fit the mix.
    spec.shape = 'pseudo_voigt_gl';
    spec.gl_ratio = 0.5;
    spec.fix_gl_ratio = true;
  } else if (shape === 'GL') {
    spec.shape = 'pseudo_voigt_gl';
    spec.gl_ratio = p.glMix / 100;   // frontend 0-100 → backend 0-1
  } else if (shape === 'asym-GL') {
    spec.shape = 'asymmetric_gl';
    // A03 Codex round 1: `p.glMix || 50` sent a mix of 0 as 50 (and a DS α of 0
    // as 0.1 below) — a value the page draws but never requested; locked, the
    // server held the substitute and the drawn curve differed from the fitted
    // one by 6.9 % (asym-GL) and 8.8 % (DS) of amplitude. Only a NON-NUMBER
    // falls back to the default.
    spec.gl_ratio = (Number.isFinite(p.glMix) ? p.glMix : 50) / 100;
    spec.asymmetry = Number.isFinite(p.asymmetry) ? p.asymmetry : 0;
    spec.fix_asymmetry = !!p.fixAsymmetry;
    // Forward auto-fit asymmetry bounds when present (set by buildAutoFitModel).
    // For non-auto-fit peaks these fields are absent and the backend falls back
    // to its [0.0, 1.0] default.
    if (Number.isFinite(p._afAsymMin)) spec.asymmetry_min = p._afAsymMin;
    if (Number.isFinite(p._afAsymMax)) spec.asymmetry_max = p._afAsymMax;
  } else if (shape === 'DS') {
    spec.shape = 'doniach_sunjic';
    spec.alpha      = Number.isFinite(p.dsAlpha) ? p.dsAlpha : 0.1;
    spec.gamma_asym = Number.isFinite(p.dsGamma) ? p.dsGamma : 0.0;
    spec.fix_alpha      = !!p.fixDsAlpha;
    spec.fix_gamma_asym = !!p.fixDsGamma;
  } else if (shape === 'DSG_LA') {
    spec.shape = 'ds_g';
    spec.alpha   = Number.isFinite(p.laAlpha) ? p.laAlpha : 0.10;
    spec.beta    = Number.isFinite(p.laBeta)  ? p.laBeta  : 0.3;
    spec.m_gauss = Number.isFinite(p.laM)     ? p.laM     : 0.4;
    spec.fix_alpha   = !!p.fixLaAlpha;
    spec.fix_beta    = !!p.fixLaBeta;
    spec.fix_m_gauss = !!p.fixLaM;
  } else if (shape === 'LACX') {
    spec.shape = 'la_casaxps';
    spec.alpha = Number.isFinite(p.caAlpha) ? p.caAlpha : 1.0;
    spec.beta  = Number.isFinite(p.caBeta)  ? p.caBeta  : 1.0;
    spec.m     = Number.isFinite(p.caM)     ? p.caM     : 50.0;
    spec.fix_alpha = !!p.fixCaAlpha;
    spec.fix_beta  = !!p.fixCaBeta;
    spec.fix_m     = !!p.fixCaM;
  } else {
    spec.shape = 'gaussian';
  }
  if (p.linked) {
    const parent = getPeak(p.linked);
    if (parent) {
      spec.constrain_to = String(p.linked);
      spec.splitting = p.linkOffset;
      spec.area_ratio = p.linkRatio;
      spec.fix_fwhm = true;
    }
  }
  return spec;
}

// Server parameter names -> the peak's fields, honouring the peak's locks.
// Shared by a fit result and by an alternative solution (previewed on a COPY
// of the peaks, or adopted as the start of a new fit).
function _applyBackendParams(p, par) {
  if (par.center    && !p.fixCenter)    p.center    = par.center.value;
  if (par.amplitude && !p.fixAmplitude) p.amplitude = par.amplitude.value;

exec
/bin/zsh -lc 'node --test tests/js/stale_statistics.test.js tests/js/fit_acceptance.test.js tests/js/local_lm_descent.test.js tests/js/unsupported_components.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 exited 1 in 5778ms:
# Subtest: A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
ok 1 - A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
  ---
  duration_ms: 7.683625
  type: 'test'
  ...
# Subtest: a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
ok 2 - a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
  ---
  duration_ms: 4.713333
  type: 'test'
  ...
# Subtest: a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
ok 3 - a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
  ---
  duration_ms: 3.331339
  type: 'test'
  ...
# Subtest: a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
ok 4 - a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
  ---
  duration_ms: 6.829958
  type: 'test'
  ...
# Subtest: a converged backend result is applied (sanity)
ok 5 - a converged backend result is applied (sanity)
  ---
  duration_ms: 2.347074
  type: 'test'
  ...
# Subtest: the engine/objective labels of a fit result survive spectrum and project save/load
ok 6 - the engine/objective labels of a fit result survive spectrum and project save/load
  ---
  duration_ms: 0.737233
  type: 'test'
  ...
# Subtest: an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
ok 7 - an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
  ---
  duration_ms: 2.219843
  type: 'test'
  ...
# Subtest: an HTTP 502 on the upload is a server failure, not a transport failure
ok 8 - an HTTP 502 on the upload is a server failure, not a transport failure
  ---
  duration_ms: 2.11297
  type: 'test'
  ...
# Subtest: uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
ok 9 - uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
  ---
  duration_ms: 1.849085
  type: 'test'
  ...
# Subtest: every consumer that prints the goodness-of-fit statistic routes through the statistic identity
ok 10 - every consumer that prints the goodness-of-fit statistic routes through the statistic identity
  ---
  duration_ms: 0.874533
  type: 'test'
  ...
# Subtest: uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
ok 11 - uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
  ---
  duration_ms: 0.70498
  type: 'test'
  ...
# Subtest: a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
ok 12 - a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
  ---
  duration_ms: 1.483407
  type: 'test'
  ...
# Subtest: starting-point helpers: keyed on the persisted objective, weighted results untouched
ok 13 - starting-point helpers: keyed on the persisted objective, weighted results untouched
  ---
  duration_ms: 3.154612
  type: 'test'
  ...
# Subtest: Quantify shows the starting-point banner for a local result and not for a weighted one
ok 14 - Quantify shows the starting-point banner for a local result and not for a weighted one
  ---
  duration_ms: 4.382276
  type: 'test'
  ...
# Subtest: every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
ok 15 - every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
  ---
  duration_ms: 1.580986
  type: 'test'
  ...
# Subtest: project save derives the designation from the objective for an older local result lacking the new fields
ok 16 - project save derives the designation from the objective for an older local result lacking the new fields
  ---
  duration_ms: 7.652269
  type: 'test'
  ...
# Subtest: stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
ok 17 - stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
  ---
  duration_ms: 0.966398
  type: 'test'
  ...
# Subtest: _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
ok 18 - _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
  ---
  duration_ms: 3.51535
  type: 'test'
  ...
# Subtest: history preview glow is keyed on the dataset flag, not the label text
ok 19 - history preview glow is keyed on the dataset flag, not the label text
  ---
  duration_ms: 0.715485
  type: 'test'
  ...
# Subtest: spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
ok 20 - spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
  ---
  duration_ms: 0.421685
  type: 'test'
  ...
# Subtest: _applyStatDisplay clears header, tooltip, caption and value together on local → none
ok 21 - _applyStatDisplay clears header, tooltip, caption and value together on local → none
  ---
  duration_ms: 2.783022
  type: 'test'
  ...
# Subtest: _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
ok 22 - _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
  ---
  duration_ms: 1.671172
  type: 'test'
  ...
# Subtest: fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
ok 23 - fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
  ---
  duration_ms: 1.397176
  type: 'test'
  ...
# Subtest: undo/redo snapshots carry and restore model provenance
ok 24 - undo/redo snapshots carry and restore model provenance
  ---
  duration_ms: 3.341704
  type: 'test'
  ...
# Subtest: round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
ok 25 - round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
  ---
  duration_ms: 1.016084
  type: 'test'
  ...
# Subtest: _provenanceOf derives a designation from a live local result, and undo snapshots use it
ok 26 - _provenanceOf derives a designation from a live local result, and undo snapshots use it
  ---
  duration_ms: 2.471995
  type: 'test'
  ...
# Subtest: batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
ok 27 - batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
  ---
  duration_ms: 0.365323
  type: 'test'
  ...
# Subtest: the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
ok 28 - the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
  ---
  duration_ms: 2.179011
  type: 'test'
  ...
# Subtest: round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
ok 29 - round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
  ---
  duration_ms: 0.814629
  type: 'test'
  ...
# Subtest: the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
ok 30 - the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
  ---
  duration_ms: 2.451904
  type: 'test'
  ...
# Subtest: the sidebar banner is sticky at the top of the scrolling panel body
ok 31 - the sidebar banner is sticky at the top of the scrolling panel body
  ---
  duration_ms: 0.251724
  type: 'test'
  ...
# Subtest: the sidebar banner shows on a stack tab whose visible entries draw a local source fit
ok 32 - the sidebar banner shows on a stack tab whose visible entries draw a local source fit
  ---
  duration_ms: 2.271468
  type: 'test'
  ...
# Subtest: every stack chart repaint path refreshes the sidebar designation before any early return
ok 33 - every stack chart repaint path refreshes the sidebar designation before any early return
  ---
  duration_ms: 0.401798
  type: 'test'
  ...
# Subtest: closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
ok 34 - closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
  ---
  duration_ms: 0.182043
  type: 'test'
  ...
# Subtest: W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
ok 35 - W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
  ---
  duration_ms: 3.014668
  type: 'test'
  ...
# Subtest: TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
ok 36 - TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
  ---
  duration_ms: 4.914437
  type: 'test'
  ...
# Subtest: adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
ok 37 - adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
  ---
  duration_ms: 2.833534
  type: 'test'
  ...
# Subtest: adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
ok 38 - adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
  ---
  duration_ms: 2.042489
  type: 'test'
  ...
# Subtest: adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
ok 39 - adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
  ---
  duration_ms: 2.132496
  type: 'test'
  ...
# Subtest: adoption: success records the choice, the starts evidence and the key of the model it describes
ok 40 - adoption: success records the choice, the starts evidence and the key of the model it describes
  ---
  duration_ms: 2.188259
  type: 'test'
  ...
# Subtest: an ordinary Run Fit on one unlinked component does not ask for the starts check
ok 41 - an ordinary Run Fit on one unlinked component does not ask for the starts check
  ---
  duration_ms: 2.023368
  type: 'test'
  ...
# Subtest: a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
ok 42 - a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
  ---
  duration_ms: 1.854154
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
ok 43 - A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
  ---
  duration_ms: 1222.666228
  type: 'test'
  ...
# Subtest: A01 replay: the linked U 4f pair also descends
ok 44 - A01 replay: the linked U 4f pair also descends
  ---
  duration_ms: 239.845022
  type: 'test'
  ...
# Subtest: noiseless Gaussian: amplitude 10 started at 5 is recovered
ok 45 - noiseless Gaussian: amplitude 10 started at 5 is recovered
  ---
  duration_ms: 12.191377
  type: 'test'
  ...
# Subtest: acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
ok 46 - acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
  ---
  duration_ms: 8.445738
  type: 'test'
  ...
# Subtest: a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
ok 47 - a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
  ---
  duration_ms: 11.938955
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
ok 48 - bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
  ---
  duration_ms: 8.472666
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
ok 49 - bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
  ---
  duration_ms: 8.343285
  type: 'test'
  ...
# Subtest: a weak component the data DO hold is no longer forced up to an amplitude of 1
ok 50 - a weak component the data DO hold is no longer forced up to an amplitude of 1
  ---
  duration_ms: 8.283487
  type: 'test'
  ...
# Subtest: derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
ok 51 - derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
  ---
  duration_ms: 40.100479
  type: 'test'
  ...
# Subtest: derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
ok 52 - derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
  ---
  duration_ms: 23.00169
  type: 'test'
  ...
# Subtest: a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
ok 53 - a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
  ---
  duration_ms: 7.39056
  type: 'test'
  ...
# Subtest: linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
ok 54 - linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
  ---
  duration_ms: 11.951201
  type: 'test'
  ...
# Subtest: round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
ok 55 - round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
  ---
  duration_ms: 10.498753
  type: 'test'
  ...
# Subtest: round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
ok 56 - round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
  ---
  duration_ms: 9.06462
  type: 'test'
  ...
# Subtest: round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
ok 57 - round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
  ---
  duration_ms: 9.682854
  type: 'test'
  ...
# Subtest: A01 replay targets converge to constrained stationary points (C1s and U 4f)
ok 58 - A01 replay targets converge to constrained stationary points (C1s and U 4f)
  ---
  duration_ms: 1298.899072
  type: 'test'
  ...
# Subtest: round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
ok 59 - round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
  ---
  duration_ms: 70.747547
  type: 'test'
  ...
# Subtest: round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
ok 60 - round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
  ---
  duration_ms: 20.351429
  type: 'test'
  ...
# Subtest: round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
ok 61 - round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
  ---
  duration_ms: 15.400077
  type: 'test'
  ...
# Subtest: round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
ok 62 - round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
  ---
  duration_ms: 78.506988
  type: 'test'
  ...
# Subtest: round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
ok 63 - round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
  ---
  duration_ms: 1138.640851
  type: 'test'
  ...
# Subtest: round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
ok 64 - round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
  ---
  duration_ms: 19.784026
  type: 'test'
  ...
# Subtest: round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
ok 65 - round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
  ---
  duration_ms: 9.676137
  type: 'test'
  ...
# Subtest: weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
ok 66 - weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
  ---
  duration_ms: 8.069073
  type: 'test'
  ...
# Subtest: server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
not ok 67 - server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
  ---
  duration_ms: 1321.78794
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
ok 68 - the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom
  ---
  duration_ms: 22.699935
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
ok 69 - an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
  ---
  duration_ms: 26.302126
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
ok 70 - an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
  ---
  duration_ms: 18.824264
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
ok 71 - round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
  ---
  duration_ms: 7.895846
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
ok 72 - round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
  ---
  duration_ms: 8.639301
  type: 'test'
  ...
# Subtest: recovery from an amplitude of exactly zero (the new floor is not a trap)
ok 73 - recovery from an amplitude of exactly zero (the new floor is not a trap)
  ---
  duration_ms: 9.31368
  type: 'test'
  ...
# Subtest: one accessor classifies a result against a key: none / unverified / current / stale
ok 74 - one accessor classifies a result against a key: none / unverified / current / stale
  ---
  duration_ms: 15.643066
  type: 'test'
  ...
# Subtest: the key is the step (b) key: F1 adds no second binding mechanism and no new key field
ok 75 - the key is the step (b) key: F1 adds no second binding mechanism and no new key field
  ---
  duration_ms: 3.760346
  type: 'test'
  ...
# Subtest: Results panel, current: statistic, RMSE, R and sigma are shown
ok 76 - Results panel, current: statistic, RMSE, R and sigma are shown
  ---
  duration_ms: 8.434206
  type: 'test'
  ...
# Subtest: Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
ok 77 - Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
  ---
  duration_ms: 6.943675
  type: 'test'
  ...
# Subtest: Results panel, unverified (older save, no key): values shown with a plain note
ok 78 - Results panel, unverified (older save, no key): values shown with a plain note
  ---
  duration_ms: 6.985294
  type: 'test'
  ...
# Subtest: status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
ok 79 - status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
  ---
  duration_ms: 7.545021
  type: 'test'
  ...
# Subtest: the stored fitted curve is never drawn, saved or stacked as the fit once stale
ok 80 - the stored fitted curve is never drawn, saved or stacked as the fit once stale
  ---
  duration_ms: 2.505606
  type: 'test'
  ...
# Subtest: saves keep the key and say plainly when the statistics are stale or unverified
ok 81 - saves keep the key and say plainly when the statistics are stale or unverified
  ---
  duration_ms: 2.426041
  type: 'test'
  ...
# Subtest: CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
ok 82 - CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
  ---
  duration_ms: 11.654724
  type: 'test'
  ...
# Subtest: XLSX: stale writes a WARNING row instead of the statistic, and no sigma
ok 83 - XLSX: stale writes a WARNING row instead of the statistic, and no sigma
  ---
  duration_ms: 3.870657
  type: 'test'
  ...
# Subtest: TSV: stale says the Model / Residual columns are the current, unfitted model
ok 84 - TSV: stale says the Model / Residual columns are the current, unfitted model
  ---
  duration_ms: 5.828008
  type: 'test'
  ...
# Subtest: the refresh re-renders Results only when its rendered state differs
ok 85 - the refresh re-renders Results only when its rendered state differs
  ---
  duration_ms: 2.611683
  type: 'test'
  ...
# Subtest: the twin reproduces the server verdict on real responses, and defers to the server field when present
ok 86 - the twin reproduces the server verdict on real responses, and defers to the server field when present
  ---
  duration_ms: 10.379474
  type: 'test'
  ...
# Subtest: _applySupport writes every peak, follows ancestry to the root, stamps the fit key, and leaves null where the response says nothing
ok 87 - _applySupport writes every peak, follows ancestry to the root, stamps the fit key, and leaves null where the response says nothing
  ---
  duration_ms: 4.855628
  type: 'test'
  ...
# Subtest: the verdict applies only to the model and context it was computed for
ok 88 - the verdict applies only to the model and context it was computed for
  ---
  duration_ms: 4.164941
  type: 'test'
  ...
# Subtest: the local engine computes the same statistic from its own residuals
ok 89 - the local engine computes the same statistic from its own residuals
  ---
  duration_ms: 5.652081
  type: 'test'
  ...
# Subtest: sidebar card: badge; centre and width shown as a dash; area % excluded and the others renormalised
ok 90 - sidebar card: badge; centre and width shown as a dash; area % excluded and the others renormalised
  ---
  duration_ms: 5.704489
  type: 'test'
  ...
# Subtest: results table: greyed row, no centre / width / sigma, area kept, percentage dash, and the note beneath
ok 91 - results table: greyed row, no centre / width / sigma, area kept, percentage dash, and the note beneath
  ---
  duration_ms: 12.37896
  type: 'test'
  ...
# Subtest: uncertainty panel: one rule-0 warning for the component, no per-parameter alarms and no "locked" note for it
ok 92 - uncertainty panel: one rule-0 warning for the component, no per-parameter alarms and no "locked" note for it
  ---
  duration_ms: 4.797355
  type: 'test'
  ...
# Subtest: Quantify: excluded from the body, listed beneath with the reason; total and percentages over the rest
ok 93 - Quantify: excluded from the body, listed beneath with the reason; total and percentages over the rest
  ---
  duration_ms: 4.332454
  type: 'test'
  ...
# Subtest: CSV / XLSX export: Status column, suppressed cells, At% empty, WARNING line
ok 94 - CSV / XLSX export: Status column, suppressed cells, At% empty, WARNING line
  ---
  duration_ms: 6.344826
  type: 'test'
  ...
# Subtest: publication figure: no label at the (zero) component, legend entry says so; chart and stack labels say so
ok 95 - publication figure: no label at the (zero) component, legend entry says so; chart and stack labels say so
  ---
  duration_ms: 2.337882
  type: 'test'
  ...
# Subtest: write-back: a server result sets support; the local engine and a propagated model reset it
ok 96 - write-back: a server result sets support; the local engine and a propagated model reset it
  ---
  duration_ms: 1.483481
  type: 'test'
  ...
# Subtest: persistence: support travels with the peak object through every save (the peak is spread whole)
ok 97 - persistence: support travels with the peak object through every save (the peak is spread whole)
  ---
  duration_ms: 0.883288
  type: 'test'
  ...
# Subtest: CSV / XLSX: an unsupported DS+G component exports no width of any kind (beta, m)
ok 98 - CSV / XLSX: an unsupported DS+G component exports no width of any kind (beta, m)
  ---
  duration_ms: 4.995197
  type: 'test'
  ...
# Subtest: the scattered-starts table: an unsupported component shows neither area % nor a move in "Your fit", and is not the largest move
ok 99 - the scattered-starts table: an unsupported component shows neither area % nor a move in "Your fit", and is not the largest move
  ---
  duration_ms: 6.084607
  type: 'test'
  ...
# Subtest: exports: a stale or keyless verdict is "not established", never "supported"
ok 100 - exports: a stale or keyless verdict is "not established", never "supported"
  ---
  duration_ms: 8.436092
  type: 'test'
  ...
# Subtest: Auto-Fit finalisation (locks, charge shift) keeps its own verdicts: _restampSupport, called after the locks
ok 101 - Auto-Fit finalisation (locks, charge shift) keeps its own verdicts: _restampSupport, called after the locks
  ---
  duration_ms: 4.109435
  type: 'test'
  ...
# Subtest: a .fit.json import onto this tab's data carries no verdict
ok 102 - a .fit.json import onto this tab's data carries no verdict
  ---
  duration_ms: 0.128948
  type: 'test'
  ...
# Subtest: _isUnsupported is never handed an array index as its key (Array.filter passes one)
ok 103 - _isUnsupported is never handed an array index as its key (Array.filter passes one)
  ---
  duration_ms: 4.124731
  type: 'test'
  ...
# Subtest: a key change re-renders every consumer of the verdict — each compared with ITS OWN rendering
ok 104 - a key change re-renders every consumer of the verdict — each compared with ITS OWN rendering
  ---
  duration_ms: 2.328133
  type: 'test'
  ...
# Subtest: stack tabs judge a source component against the SOURCE record's key
ok 105 - stack tabs judge a source component against the SOURCE record's key
  ---
  duration_ms: 3.070303
  type: 'test'
  ...
# Subtest: "Your fit" percentages are over supported components; an empty Quantify shows no 100 %
ok 106 - "Your fit" percentages are over supported components; an empty Quantify shows no 100 %
  ---
  duration_ms: 13.607398
  type: 'test'
  ...
# Subtest: the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
ok 107 - the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
  ---
  duration_ms: 5.678168
  type: 'test'
  ...
1..107
# tests 107
# suites 0
# pass 106
# fail 1
# cancelled 0
# skipped 0
# todo 0
# duration_ms 5833.072198

exec
/bin/zsh -lc "sed -n '10210,10470p' templates/index.html; sed -n '10570,10690p' templates/index.html; sed -n '10720,10860p' templates/index.html; sed -n '3370,3460p' templates/index.html; sed -n '13960,14015p' templates/index.html; sed -n '14100,14170p' templates/index.html; sed -n '8030,8065p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:

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
  };

  const meta = {
    version: 3,
    timestamp: new Date().toISOString(),
    sample_name: sampleName,
    instrument: instrument,
    activeId: tabManager.activeId,
  };
  // B2: compound markers are GLOBAL (project-meta scope, not per-tab). Additive +
  // optional — omit the key when there are no markers (serializer returns null).
  // Top-level version stays 3. (Flows to both the .proj.json `{...meta}` and the
  // .proj.zip manifest `{...meta}`, which reuse this same meta object.)
  const _refCM = RefCore.serializeRefCompoundMarkers(_refCompoundMarkers);
  if (_refCM) meta.refCompoundMarkers = _refCM;

  if (tabs.length < 5) {
    const data = { ...meta, tabs: tabs.map(buildTabData) };
    _downloadBlob(
      new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'}),
      fname + '.proj.json'
    );
  } else {
    const zip = new JSZip();

    const hasPeaks = Array.isArray(data.peaks);
    const hasRaw = (Array.isArray(data.rawBE) && data.rawBE.length) ||
                   (Array.isArray(data.be) && data.be.length);

    if (hasPeaks && hasRaw) {
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
    if (data.fittedY) fr.fittedY = data.fittedY;
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
             + ' is not a valid identifier.', 'red', true);
      return;
    }
    if (Array.isArray(t.entries)) {
      for (const e of t.entries) {
        if (!e || typeof e !== 'object') continue;
        if (e.id != null && !_SLUG_ID_RE.test(String(e.id))) {
    const nI  = Array.isArray(t.rawIntensity) ? t.rawIntensity.length : 0;
    if (nBE > MAX_SPECTRUM_POINTS || nI > MAX_SPECTRUM_POINTS) {
      notify('Project not loaded: a spectrum exceeds '
             + MAX_SPECTRUM_POINTS.toLocaleString() + ' points.', 'red', true);
      return;
    }
  }

  // Phase 5: preserve saved tab IDs (with collision-detect fallback to
  // random). Stack-entry sourceTabId references resolve correctly when
  // IDs round-trip. Backward compatible — old saves with no isStack
  // tabs flow through the spectrum-tab branch unchanged.
  const usedIds = new Set(tabManager.tabs.map(x => x.id));
  const newId = (saved) => {
    if (saved && !usedIds.has(saved)) { usedIds.add(saved); return saved; }
    let nid = 'tab_' + Math.random().toString(36).slice(2, 9);
    while (usedIds.has(nid)) nid = 'tab_' + Math.random().toString(36).slice(2, 9);
    usedIds.add(nid);
    return nid;
  };

  // Map saved IDs to final IDs for ALL project tabs, so references recorded
  // against saved IDs (stack-entry sourceTabId, saved activeId) can be
  // rewritten when the collision-detect path assigns a fresh ID. Identity
  // mappings (no collision) are harmless.
  const idMap = new Map();

  // Add project tabs to the existing tab bar (same as loading a folder)
  const newTabs = data.tabs.map(t => {
    const id = newId(t.id);
    if (t.id) idMap.set(t.id, id);
    if (t.isStack) {
      // Stack tab — shape matches createStackTab; entries restored verbatim
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
      e.sourceTabId = idMap.get(e.sourceTabId) ?? e.sourceTabId;
    }
  }

  // Phase 5: prune stack entries whose sourceTabId doesn't resolve to a
  // loaded spectrum tab. After the remap above this only happens when the
  // saved file was manually edited to reference a non-existent tab, or a
  // spectrum file was missing from a ZIP load. Notify per-stack so the
  // user knows what was dropped.
  const validSpectrumIds = new Set(
    tabManager.tabs.filter(x => !x.isStack).map(x => x.id)
  );
  for (const t of tabManager.tabs) {
    if (!t.isStack) continue;
    const before = t.entries.length;
    t.entries = t.entries.filter(e => validSpectrumIds.has(e.sourceTabId));
    const removed = before - t.entries.length;
    if (removed > 0) {
      notify('Pruned ' + removed + ' stale entr' + (removed === 1 ? 'y' : 'ies')
             + ' from stack "' + t.name + '" (source tabs not found).', 'amber');
    }
  }

  // Phase 5: advance _nextStackNum past the highest restored "▦ Stack N"
  // so future "+ Stack" creates non-colliding names.
  let maxN = 0;
  for (const t of tabManager.tabs) {
    if (!t.isStack) continue;
    const m = /^▦\s*Stack\s+(\d+)$/.exec(t.name || '');
    if (m) maxN = Math.max(maxN, parseInt(m[1], 10));
  }
  if (maxN >= _nextStackNum) _nextStackNum = maxN + 1;
        rawBE: t.rawBE,
        rawIntensity: t.rawIntensity,
        ccShift: t.ccShift,
        peaks: t.peaks.map(p => ({...p})),
        nextId: t.nextId,
        markedElements: t.markedElements || [],
        notes: t.notes || '',
        ui: {...t.ui},
      })),
      // v1 compat keys from active tab
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
        endpointAvg: document.getElementById('bg-endpoint-avg').value
      },
      roi: {
        min: document.getElementById('roi-min').value,
        max: document.getElementById('roi-max').value
      }
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
  if (!panel.classList.contains('open')) {
    // Position at top-right of viewport, offset from the right panel
    const rp = document.getElementById('right-panel');
    const rpLeft = rp ? rp.getBoundingClientRect().left : window.innerWidth - 360;
    panel.style.top = '60px';
    panel.style.left = Math.max(20, rpLeft - 360) + 'px';
    panel.style.right = '';
    panel.classList.add('open');
  }
}

function _closeHistoryPanel() {
  if (!snap) return;

  if (_historyPreview && _historyPreview.snapId === snapId) {
    _historyClearPreview();
    return;
  }

  if (!snap.peaks || !snap.peaks.length) {
    notify('Preview not available for this snapshot.', 'amber');
    return;
  }

  _historyPreview = { snapId, peaks: snap.peaks, fitResult: snap.fitResult };
  _updateLocalModelBanner();
  document.querySelectorAll('.hist-row').forEach(r => r.classList.remove('hist-preview-active'));
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
  if (!tab || !tab.snapshots) return;
  tab.snapshots = tab.snapshots.filter(s => s.id !== snapId);
  if (_historyPreview && _historyPreview.snapId === snapId) _historyClearPreview();
  _renderHistoryList();
}

// History panel drag logic
(function () {
  const panel = document.getElementById('history-panel');
  const bar = document.getElementById('history-panel-titlebar');
  if (!panel || !bar) return;
  let dragging = false, offX = 0, offY = 0;
  bar.addEventListener('mousedown', e => {
    if (e.target.closest('button')) return;
    dragging = true;
    const r = panel.getBoundingClientRect();
    offX = e.clientX - r.left;
    offY = e.clientY - r.top;
    document.body.style.cursor = 'grabbing';
    document.body.style.userSelect = 'none';
    e.preventDefault();
  });
      // Adopting an alternative needs the server: the local engine would start
      // from the live model, not from the alternative. Nothing was changed.
      document.getElementById('sb-msg').textContent = 'Fit failed';
      notify('The server could not be reached, so the alternative was not applied. Previous peaks and result kept.', 'red', true);
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

exec
/bin/zsh -lc "rg -n 'function renderPeakList|function renderPeakForm|function _normalizePeaksCRef|function evalAllPeaks|function updatePeak|function toggleLock|roi-min.*on|roi-max.*on|shirley-iter.*on|bg-start.*on|bg-end.*on|bg-endpoint-avg.*on|fit-method.*on' templates/index.html; sed -n '5310,5450p' templates/index.html; sed -n '5925,6120p' templates/index.html; sed -n '12165,12245p' templates/index.html; sed -n '8980,9095p' templates/index.html; cat docs/superpowers/plans/2026-09-25-f1-stale-statistics.md" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
124:  #fit-method:focus { border-color: var(--accent); outline: none; }
2035:                <input type="number" id="bg-start" value="726" step="0.5" oninput="_invalidateBgCache(); updatePlot()">
2039:                <input type="number" id="bg-end" value="706" step="0.5" oninput="_invalidateBgCache(); updatePlot()">
2045:                <input type="number" id="shirley-iter" value="5" min="1" max="50" step="1" oninput="_clampShirleyIter(); _invalidateBgCache(); updatePlot()" title="Number of iterations for the Shirley background calculation. The algorithm converges quickly — most of the change happens between 1 and 5 iterations. Values above 10 rarely produce visible differences. Default: 5.">
2049:                <input type="number" id="bg-endpoint-avg" value="3" min="1" max="50" step="1" oninput="_invalidateBgCache(); updatePlot()" title="Number of points to average at each endpoint for smoother background anchoring">
2064:                <input type="number" id="roi-min" value="706" step="0.5" oninput="updatePlot();_recomputeAutoFitMenuState()">
2068:                <input type="number" id="roi-max" value="726" step="0.5" oninput="updatePlot();_recomputeAutoFitMenuState()">
4390:function evalAllPeaks(beArray, peaks) {
5215:function _normalizePeaksCRef(peaks) {
5988:function updatePeakParam(id, key, value) {
6030:function toggleLock(id, key, btn) {
6110:function renderPeakList() {
6174:function renderPeakForm(p) {
6579:// `shirley-iter` is gated when bg-type doesn't need iteration.
// peakToBackendSpec / applyBackendResult / runFit per the checklist in
// CLAUDE.md.
//
// Note: glMix uses the frontend 0-100 slider scale (= backend gl_ratio × 100).
// Do NOT cross-map look-alike params across shapes (e.g. DSG_LA's laAlpha vs
// LACX's caAlpha) — they are mathematically different parameters that share
// a Greek letter.
const SHAPE_PARAM_SCHEMA = {
  'Gaussian':   {},
  'Lorentzian': {},
  'Voigt':      {},
  'GL':         { glMix: 30, fixGlMix: false },
  'asym-GL':    { glMix: 30, fixGlMix: false, asymmetry: 0.0, fixAsymmetry: false },
  'DS':         { dsAlpha: 0.10, fixDsAlpha: false, dsGamma: 0.0, fixDsGamma: false },
  'DSG_LA':     { laAlpha: 0.10, fixLaAlpha: false, laBeta: 0.3, fixLaBeta: false, laM: 0.4, fixLaM: false },
  'LACX':       { caAlpha: 1.0,  fixCaAlpha: false, caBeta: 1.0, fixCaBeta: false, caM: 50, fixCaM: true },
};

// Which peak field holds the effective eV WIDTH for a given shape. Every
// shape stores its width in the top-level `fwhm` EXCEPT DS+G (DSG_LA), whose
// width is the Gaussian FWHM `laM` (DS+G's `fwhm` field is display-only /
// readonly and excluded from fitting — see renderShapeControls / runFit).
// Used to CARRY the width across a shape switch instead of resetting it to a
// per-shape default. The two accessors return the value field and its
// lock (fix-flag) field respectively.
function _widthField(shape) { return shape === 'DSG_LA' ? 'laM' : 'fwhm'; }
function _widthFixField(shape) { return shape === 'DSG_LA' ? 'fixLaM' : 'fixFwhm'; }

// Switch ONE peak object's lineshape IN PLACE. Pure — no DOM, no state, no
// rendering (_switchPeakShape wraps it with the family / undo / render / plot
// orchestration; the JS round-trip tests exercise it directly).
//
// Preserves the parameters that carry over — center and amplitude (untouched
// top-level fields), and the effective WIDTH (mapped across the laM↔fwhm
// boundary, not reset) — and seeds a default ONLY for a parameter the new
// shape genuinely introduces that the peak does not already carry.
//
// Round-trip guarantee (A → B → A returns the peak's ACTIVE parameters — the
// ones evalPeak reads for shape A — to their originals, so the rendered curve
// is unchanged):
//   1. Non-width shape params are NEVER deleted, so a value the peak already
//      carries (e.g. DS+G's laBeta) survives the excursion through B and is
//      not re-defaulted coming back. This replaces the old
//      delete-then-default behaviour that silently reset fitted values
//      (observed: laBeta 0.05 → 0.30, laM 3.11 → 0.40 on DS+G → GL → DS+G).
//   2. The width is MAPPED, not reset: the eV width is copied across the
//      laM↔fwhm boundary. The map is the identity in eV, so it is invertible
//      and the round-trip restores the original width (and its lock).
function _applyShapeSwitch(peak, newShape) {
  const oldShape = peak.shape;
  if (oldShape === newShape || !(newShape in SHAPE_PARAM_SCHEMA)) return;
  // 1. carry the effective width (value + lock) across the laM↔fwhm boundary
  const oldWF = _widthField(oldShape), newWF = _widthField(newShape);
  if (newWF !== oldWF) {
    const w = peak[oldWF];
    if (Number.isFinite(w)) peak[newWF] = w;
    const lock = peak[_widthFixField(oldShape)];
    if (typeof lock === 'boolean') peak[_widthFixField(newShape)] = lock;
  }
  // 2. switch shape; seed a default ONLY for a param the new shape introduces
  //    that the peak does not already carry (carried-over values preserved)
  peak.shape = newShape;
  const schema = SHAPE_PARAM_SCHEMA[newShape];
  for (const [k, v] of Object.entries(schema)) {
    if (!(k in peak)) peak[k] = v;
  }
}

// Switch a peak's lineshape and re-render. Shape-agnostic fields (id, name,
// color, center, amplitude, linked/linkOffset/linkRatio, fixCenter/
// fixAmplitude, isChargeReference) survive untouched; the width and every
// carried-over shape param are preserved by _applyShapeSwitch. Linked
// children share their parent's shape and shape-specific params, so the
// switch is applied to the whole multiplet family.
function _switchPeakShape(id, newShape) {
  const p = getPeak(id);
  if (!p || p.shape === newShape) return;
  if (!(newShape in SHAPE_PARAM_SCHEMA)) return;
  const parent = p.linked ? (getPeak(p.linked) || p) : p;
  if (parent.shape === newShape) return;
  const family = [parent, ...state.peaks.filter(q => q.linked === parent.id)];
  _pushUndoDebounced();
  for (const peak of family) _applyShapeSwitch(peak, newShape);
  _invalidateFittedY();
  for (const peak of family) renderPeakControls(peak);
  updatePlot();
}

// ═══════════════════════════════════════════════════
// ZOOM HELPERS
// ═══════════════════════════════════════════════════
// Manual zoom state — no plugin, full control
let _origYMax = null;       // main chart original Y max
let _origXMin = null;       // main chart original X min
let _origXMax = null;       // main chart original X max
let _origResidYMin = null;  // residuals chart
let _origResidYMax = null;
let _dragZoomEnabled = true; // toggled off during placeMode

function resetAllZoom() {
  if (state.chart) {
    // Stack tabs: _origYMax / _origXMin are set by single-tab updatePlot
    // and carry stale spectrum-range values when the active tab is a
    // stack. Clear explicit Y and X bounds, let Chart.js auto-fit, and
    // seed state._mainYMax from current chart data so the next wheel
    // event has a real number to multiply against (same pattern as
    // _renderStackChart init).
    const _activeTab = typeof tabManager !== 'undefined' && tabManager._getTab(tabManager.activeId);
    if (isStackTab(_activeTab)) {
      delete state.chart.options.scales.y.min;
      delete state.chart.options.scales.y.max;
      delete state.chart.options.scales.x.min;
      delete state.chart.options.scales.x.max;
      let _maxY = 0;
      for (const ds of state.chart.data.datasets) {
        if (!Array.isArray(ds.data)) continue;
        for (const pt of ds.data) {
          const v = (pt && typeof pt === 'object') ? pt.y : pt;
          if (typeof v === 'number' && isFinite(v) && v > _maxY) _maxY = v;
        }
      }
      state._mainYMax = _maxY > 0 ? _maxY : null;
      state._mainXMin = null;
      state._mainXMax = null;
      state.chart.update('none');
      updateResetZoomButton();
      return;
    }
    // Reset Y — remove explicit min/max so Chart.js auto-fits to data
    if (_origYMax !== null) {
      state._mainYMax = _origYMax;
      delete state.chart.options.scales.y.min;
      state.chart.options.scales.y.max = _origYMax;
    }
    // Reset X
    if (_origXMin !== null) {
      state._mainXMin = null;
      state._mainXMax = null;
      state.chart.options.scales.x.min = _origXMin;
      state.chart.options.scales.x.max = _origXMax;
    }
    color: p1.color,
    linked: p1.id,
    linkOffset: 10.9,
    linkRatio: 0.75
  });
  state.peaks.push(p2);
  renderPeakList();
  updatePlot();
  // Auto-expand the linked peak so the offset/ratio fields are immediately visible
  const body = document.getElementById('peak-body-' + p2.id);
  if (body) body.classList.add('open');
  notify('Multiplet pair added \u2014 edit offset & ratio below \u201c' + p2.name + '\u201d', 'green');
}

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
    btn.innerHTML = '&#x1f513; Unlock All';
    btn.title = 'Unlock all fit parameters on all peaks';
  } else {
    btn.innerHTML = '&#x1f512; Lock All';
    btn.title = 'Lock all fit parameters on all peaks';
  }
}

// ═══════════════════════════════════════════════════
// PEAK LIST UI
// ═══════════════════════════════════════════════════
// The per-peak "Charge-correction reference (C 1s graphite)" checkbox is
// only meaningful when the user is on a C 1s spectrum AND the global
// charge-correction method is set to graphite. When either condition is
// false, the checkbox is hidden completely AND any peak that previously
// held the marker is silently unchecked, so re-entering the valid mode
// gives a clean unchecked state rather than a stale stored value.
function _isChargeRefAllowed() {
  const cm = document.getElementById('cc-method');
  if (!cm || cm.value !== 'c1s') return false;
  const tab = (typeof tabManager !== 'undefined' && tabManager.activeId)
    ? tabManager._getTab(tabManager.activeId)
    : null;
  return !!(tab && isC1sTab(tab));
}

function _clearDisallowedChargeRef() {
  if (_isChargeRefAllowed()) return;
  for (const p of state.peaks) {
    if (p.isChargeReference) p.isChargeReference = false;
  }
}

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
    }));

    // Copy peak nextId
    const nextId = Math.max(0, ...clonedPeaks.map(p => p.id)) + 1;

    // Propagate background + ROI settings from source (BatchPropagation is the
    // single source of truth for the merge — see static/js/batch_propagation.js).
    // ccShift is copied separately just below.
    const newUi = BatchPropagation.propagateFitUi(srcUi, tgt.ui);

    // Apply to target tab record (without switching UI) — undoable on that record
    _pushUndoFor(tgt, { endpointAvg: tgt.ui && tgt.ui.endpointAvg });
    tgt.peaks = clonedPeaks;
    tgt.nextId = nextId;
    tgt.ui = newUi;
    tgt.ccShift = srcShift;
    tgt.chargeVerified = false;
    // A propagated model has not been fitted yet: the target's previous
    // result belonged to its previous peaks (unit A0 acceptance rule).
    tgt.fitResult = null;
    tgt.modelProvenance = srcProvenance ? { ...srcProvenance, copiedFrom: sourceTab.name } : null;

    // Now activate this tab so state is populated. activateTab is a no-op
    // when the target is ALREADY active (the user switched to it during the
    // previous target's fit): then live state still holds the target's old
    // model and the post-fit sync would overwrite the propagated record —
    // load the record into live state explicitly (Codex round 3, run B).
    if (tabManager.activeId === tid) {
      state.peaks = tgt.peaks; state.nextId = tgt.nextId; state.ccShift = tgt.ccShift;
      state.fitResult = null;   // live copy of tgt.fitResult = null above (unit A0)
      tabManager._restoreUI(tgt.ui);
      renderPeakList();
      _refreshRoiAndCentreWarnings();   // this branch does not redraw: the hint must describe the target's window (Codex round 2)
    } else {
      tabManager.activateTab(tid);
    }

    // Small yield so progress message renders
    await new Promise(r => setTimeout(r, 20));
    if (_activeTab() !== tgt) {
      // The user switched tabs during the yield: fitting would read and
      // write whichever tab is active now. Stop here; targets already
      // fitted keep their results.
      notify('Batch fit stopped at ' + tgt.name + ' — the tab changed while it was running.', 'amber');
      break;
    }

    // Run local fit
    const roiSt = _roiWindowStatus();    // warn only: the fit below uses getROIData() exactly as before
    const { be, inten } = getROIData();
    const bgI = computeBackground(be, inten);
    const bgSub = inten.map((v, idx) => v - bgI[idx]);
    const outcome = runFitLocal(be, bgSub, bgI);

    // Sync result back to record
    tabManager._syncActiveToRecord();

    // Read the statistic from the fit's own return value, not from live
    // state: the active tab can change while the fit runs.
    const ok = !!(outcome && outcome.success);
    results.push({ name: tgt.name, ok, roiHint: _roiHintFor(roiSt),
                   chi: ok && Number.isFinite(outcome.chiReduced) ? outcome.chiReduced : null,
                   message: ok ? null : ((outcome && outcome.message) || 'local fit did not converge') });

    await new Promise(r => setTimeout(r, 10));
  }

  _snapshotSuppressed = false;

  // Return to source tab
  tabManager.activateTab(sourceId);

  const nOk = results.filter(r => r.ok).length;
  const nFail = results.length - nOk;
  prog.textContent = `Batch complete: ${nOk} converged as starting points, ${nFail} not fitted. Run Fit on each spectrum before reporting.`;
  const roiNote = r => r.roiHint ? ` <span class="roi-hint${r.roiHint.cls ? ' ' + r.roiHint.cls : ''}" style="display:inline">${_escHtml(r.roiHint.text)}</span>` : '';
  summary.innerHTML = results.map(r => r.ok
    ? `<div class="prop-row">${_escHtml(r.name)}: converged &mdash; &#967;&#178;<sub>r</sub> = ${r.chi != null ? r.chi.toFixed(3) : 'n/a'} (local fit: a starting point, not a reportable result)${roiNote(r)}</div>`
    : `<div class="prop-row" style="color:var(--red,#f87171)">${_escHtml(r.name)}: NOT fitted &mdash; ${_escHtml(r.message)} (model copied, no result stored)${roiNote(r)}</div>`
  ).join('') + `<div class="prop-row" style="color:var(--red,#f87171);margin-top:4px">&#9888; Charge corrections marked in red need verification</div>`;
  summary.style.display = 'block';
  }
  let settings = {
    bgType:      (srcUi && srcUi.bgType)      || 'shirley',
    shirleyIter: (srcUi && srcUi.shirleyIter) || '5',
    endpointAvg: (srcUi && srcUi.endpointAvg) || LEGACY_ENDPOINT_AVG,
    bgStart:     (srcUi && srcUi.bgStart)     || '',
    bgEnd:       (srcUi && srcUi.bgEnd)       || '',
  };
  if (settings.bgType === 'manual') settings = { ...settings, bgType: 'shirley' };
  return computeBackgroundCore(be, inten, settings);
}

// Build all render data for one entry's fit visualization:
//   { be, bg, fittedY, peaks: [{peak, y}] }
// `be` is corrected-BE space; `bg` is raw-level background curve;
// `fittedY` is the raw-level envelope; each peak's `y` is the raw-level
// peak shape (peak height + bg).
//
// Three internal paths, chosen by what the source tab has available:
//   A:  fitResult.be + fitResult.fittedY both present, lengths match
//       → use fittedY directly (already raw-level). Frozen to fit-time
//         ccShift, matching single-tab behavior.
//   A2: fitResult.be + fitResult.bgIntensity present, no fittedY (local
//       LM fit) → fittedY = evalAllPeaks(be, peaks) + bg.
//   B:  post-load, neither fr.be nor fr.bgIntensity present → derive be
//       by ROI-filtering corrBE using src.ui.roiMin/roiMax, recompute
//       bg via _computeBackgroundForSource(be, inten, src.ui).
//       Live ccShift (deliberate asymmetry vs A/A2).
//
// Returns empty arrays if source isn't available or has no fit.
// Align src.rawIntensity to a fit-time `be` array (Path A/A2). fr.be is
// a contiguous slice of corrBE at fit time; if ccShift hasn't drifted,
// we can find the matching window in current rawBE by locating the
// index where (rawBE - shift) is closest to be[0]. Returns rawIntensity
// slice of length matching `be` (or shorter if data runs out).
function _alignRawToFitBe(src, be) {
  if (!Array.isArray(src.rawBE) || !Array.isArray(src.rawIntensity)
      || src.rawBE.length === 0 || !be || be.length === 0) return [];
  const shift = src.ccShift || 0;
  const target = be[0];
  let i0 = 0;
  let minDiff = Math.abs((src.rawBE[0] - shift) - target);
  for (let i = 1; i < src.rawBE.length; i++) {
    const d = Math.abs((src.rawBE[i] - shift) - target);
    if (d < minDiff) { minDiff = d; i0 = i; }
    else if (i0 > 0) break;  // rawBE is monotonic; past the closest match.
  }
  const len = Math.min(be.length, src.rawBE.length - i0);
  return src.rawIntensity.slice(i0, i0 + len);
}

function _buildEntryRenderData(entry) {
  const src = tabManager._getTab(entry.sourceTabId);
  if (!src || !Array.isArray(src.rawBE) || src.rawBE.length < 2) {
    return { be: [], bg: [], rawY: [], fittedY: [], peaks: [] };
  }
  const peaks = Array.isArray(src.peaks) ? src.peaks : [];
  const fr = src.fitResult;
  if (!fr || peaks.length === 0) {
    return { be: [], bg: [], rawY: [], fittedY: [], peaks: [] };
  }
  const shift = src.ccShift || 0;

  // be + bg + rawY
  let be, bg, rawY;
  if (Array.isArray(fr.be) && fr.be.length >= 2
      && Array.isArray(fr.bgIntensity)
      && fr.bgIntensity.length === fr.be.length) {
    // Path A/A2: fit-time be + bg both present (frozen).
    be = fr.be.slice();
    bg = fr.bgIntensity.slice();
    rawY = _alignRawToFitBe(src, be);
  } else {
    // Path B: post-load — derive ROI-window be from rawBE + ui.roiMin/Max,
    // recompute bg from raw via source's persisted bg settings.
    const corrBE = src.rawBE.map(b => b - shift);
    const roiMinV = parseFloat(src.ui && src.ui.roiMin);
    const roiMaxV = parseFloat(src.ui && src.ui.roiMax);
    let i0 = 0, i1 = corrBE.length - 1;
    if (isFinite(roiMinV) && isFinite(roiMaxV)) {
      const lo = Math.min(roiMinV, roiMaxV);
      const hi = Math.max(roiMinV, roiMaxV);
      // corrBE is descending (highest BE first); locate ROI bounds.
      while (i0 < corrBE.length && corrBE[i0] > hi) i0++;
      while (i1 >= 0 && corrBE[i1] < lo) i1--;
      if (i1 < i0) { i0 = 0; i1 = corrBE.length - 1; }
    }
    be = corrBE.slice(i0, i1 + 1);
    rawY = src.rawIntensity.slice(i0, i1 + 1);
    bg = _computeBackgroundForSource(be, rawY, src.ui);
  }

  // Envelope (raw-level)
  let fittedY;
  if (Array.isArray(fr.fittedY) && fr.fittedY.length === be.length && _statsRecordState(src) !== 'stale') {
    // Path A: backend fittedY directly (already raw-level). Never a stale
    // result's curve (F1: judged against the SOURCE record's key).
    fittedY = fr.fittedY.slice();
  } else {
    // Path A2/B: compose envelope from peaks + bg.
    const model = evalAllPeaks(be, peaks);
    fittedY = model.map((v, i) => v + bg[i]);
  }

  // Per-peak curves. peakOnly = pure peak shape (bg-subtracted level);
  // y = peakOnly + bg (raw level). Both kept so Bkgrd Sub view can
  // pick the appropriate one without recomputing.
  const peakCurves = peaks.map(p => {
    const peakOnly = evalPeakArray(be, p);
    return { peak: p, peakOnly, y: peakOnly.map((v, i) => v + bg[i]) };
  });

  return { be, bg, rawY, fittedY, peaks: peakCurves };
}

// Cached wrapper around _buildEntryRenderData. Stored on the entry as
# F1 — statistics after an edit belong to the previous model (2026-09-25)

Branch `fix-stale-statistics` off main `4475023` (caM unit deployed). Owner's
brief, first of the three sweep units: "Reuse step (b)'s fit key (model +
background/ROI/anchors/charge shift). When the current key does not match
the key the statistics came from, mark χ², σ and R stale in the Results
panel, CSV, XLSX, TSV, figure export and saves — say plainly they belong to
the previous model, or omit them. Do not build a second binding mechanism;
this is a down payment on the sealed fit record and must be absorbable by
it. Enumerate every consumer of the statistics first."

Source finding: `docs/findings/2026-09-25-fail-open-guards-sweep.md` H1
(`sweep-fail-open-guards`).

## 1. The one mechanism

The key already exists and already binds two things to their fit:
`_startsModelKey(peaks, ui, ccShift, anchors)` — every peak field a request
reads, background type and window, endpoint averaging, Shirley iterations,
ROI, manual anchors, charge shift. `fitResult.startsModelKey` (the starts
evidence) and `p.support.fitKey` (step (b)'s verdicts) both hold it, taken
after the result is applied, and are compared with `_startsLiveKey()` /
`_startsRecordKey(t)` at every read. F1 adds NO new key and no new field
name: every creator of a fit result stamps `fitResult.startsModelKey`, and
ONE accessor classifies a result against a key:

- `current` — the key matches: the statistics describe the model shown;
- `stale` — the key differs: they belong to the previous model;
- `unverified` — the result carries no key (saved before this unit, or an
  older local / Auto-Fit result): whether it described the saved model
  cannot be known. Shown, with a plain note to re-run. Treating these as
  stale would hide χ² and σ on nearly every existing lab project.

The sealed fit record absorbs this directly: its record will carry the key
and the statistics together; `_statsState` becomes a read of the seal.

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

## 4. Verification

- JS: `tests/js/stale_statistics.test.js` (12 tests: the accessor; every
  creator stamps the key and `_restampSupport` re-stamps the result; the
  Results panel current / stale / unverified, header, status bar, R,
  uncertainty panel on stubs; CSV / XLSX / TSV run for real on stubs;
  chart / stack / figure / spectrum-save curve gates; the saves' fields;
  the refresh re-renders once per state change and writes R on both
  paths). Existing sandboxes in `local_lm_descent`, `fit_acceptance`,
  `unsupported_components` given the accessor (or a `'current'` stub).
- Browser (`scratchpad/browser_check_f1.py`, :5151, committed UCl4-graphite
  project): on load every tab is `unverified` (committed before this unit)
  → note shown, values kept; Run Fit → `current`; centre edit → `stale`:
  header "χ²ᵣ — (model changed)", status "—", "R: —", banner, no σ, no R
  panel, chart envelope NOT the stored curve; CSV head carries the
  WARNING; spectrum save has `statisticsState: 'stale'` + key; undo →
  `current` again; project save → reload → `current` (the key survives the
  round trip); the stale spectrum save reloads `stale`; a stack entry over
  the edited source does not use the stored curve. Auto-Fit C1s Graphite on
  C1s Scan_3 → `current` with every centre locked (the re-stamp). No page
  errors.
- pytest: `test_browser_find_peaks_full_window.py`'s default-path guard
  hand-wrote an R display the injected result did not carry; the fixture
  now stores `rFactor` where a fit puts it. New test there: a KEYED result
  kept over a Find Peaks apply is `stale` (header, status, R, banner).

## 5. Codex rounds

(filled in as they run)

exec
/bin/zsh -lc "sed -n '7672,7735p' templates/index.html; sed -n '6110,6174p' templates/index.html; sed -n '4380,4408p' templates/index.html; sed -n '5210,5242p' templates/index.html; sed -n '8610,8635p' templates/index.html; sed -n '9089,9142p' templates/index.html; rg -n 'fittedY|statistics\\b|chiReduced|backendResult' autofit/parity.py autofit -g '*.py' | head -90; sed -n '1,125p' tests/test_browser_find_peaks_full_window.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:

// After anything that may have changed the model or its context without going
// through a Results re-render (a lock toggle, Lock All, a background or ROI
// control): take a stale alternative overlay off the chart and bring the
// VISIBLE panel up to date (counts -> "the model has changed since this fit").
function _refreshStartsEvidence(repaint, fromPlot) {
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

  for (const p of state.peaks) {
    const item = document.createElement('div');
    item.className = 'peak-item';
    item.id = 'peak-item-' + p.id;
    item.style.borderLeftColor = p.color;
    const isLinked = !!p.linked;
    const pArea = _peakAreas[p.id] || 0;
    const unsupported = _isUnsupported(p);
    const areaPct = unsupported ? '\u2014' : (totalArea > 0 && pArea > 0 ? ((pArea / totalArea) * 100).toFixed(1) : '\u2014');
    const dash = '\u2014';

    item.innerHTML = `
      <div class="peak-header" onclick="togglePeakBody(${p.id})">
        <div class="peak-color" style="background:${p.color}"></div>
        <span class="peak-name">${_escHtml(p.name)}${isLinked ? ' <span class="linked-badge">linked</span>' : ''}${p.isChargeReference ? ' <span class="chargeref-badge" title="Charge-correction reference (C 1s graphite 284.5 eV)">C-ref</span>' : ''}${unsupported ? ' ' + _unsupportedBadge(p.id) : ''}</span>
        <span class="peak-info">${unsupported ? dash : p.center.toFixed(2) + ' eV'}</span>
        <button class="btn btn-icon btn-sm" style="margin-left:4px;color:var(--red)" onclick="event.stopPropagation();removePeak(${p.id})">&times;</button>
      </div>
      <div class="peak-summary" onclick="togglePeakBody(${p.id})">
        <span class="peak-summary-label">Center</span>
        <span class="peak-summary-label">FWHM</span>
        <span class="peak-summary-label">Area</span>
        <span class="peak-summary-val">${unsupported ? dash : p.center.toFixed(2)}</span>
        <span class="peak-summary-val">${unsupported ? dash : p.fwhm.toFixed(2)}</span>
        <span class="peak-summary-val">${areaPct === '\u2014' ? areaPct : areaPct + '%'}</span>
      </div>
      <div class="peak-body" id="peak-body-${p.id}">
        ${renderPeakForm(p)}
      </div>
    `;
    el.appendChild(item);
    if (expandedIds.has(p.id)) document.getElementById('peak-body-' + p.id).classList.add('open');
    item.addEventListener('mouseenter', () => _highlightChartPeak(p.id, true));
    item.addEventListener('mouseleave', () => _highlightChartPeak(p.id, false));
  }
  if (state.rawBE && state.rawBE.length) _patchPeakCardsForCentre(_roiWindowStatus());
}

function renderPeakForm(p) {
    // (p.laM || 0): negative laM matches the backend's clamp-to-0-then-delta
    // path; NaN/undefined coerce to 0 → delta, which peakToBackendSpec's
    // non-finite→default sanitisation makes unreachable in fit flows.
    const yArr = dsgConvolved_array(beArr, p.center, p.laAlpha, p.laBeta, p.laM || 0);
    const amp = p.amplitude;
    return yArr.map(v => amp * v);
  }
  return beArr.map(x => evalPeak(x, p));
}

function evalAllPeaks(beArray, peaks) {
  const N = beArray.length;
  const sums = new Array(N).fill(0);
  for (const p of peaks) {
    const yArr = evalPeakArray(beArray, p);
    for (let i = 0; i < N; i++) sums[i] += yArr[i];
  }
  return sums;
}

// ═══════════════════════════════════════════════════
// BACKGROUND SUBTRACTION
// ═══════════════════════════════════════════════════
function shirleyBackground(be, intensity, maxIter) {
  const n = be.length;
  if (n < 2) return new Array(n).fill(0);
  const I0 = intensity[0], I1 = intensity[n - 1];
  let bg = new Array(n).fill(0);

// PEAKS
// ═══════════════════════════════════════════════════
// Normalize charge-reference flags on a freshly-loaded peak list.
// Old saves do not have `isChargeReference` — default to false.
// If a save somehow has >1 true, keep the first and clear the rest.
function _normalizePeaksCRef(peaks) {
  if (!Array.isArray(peaks)) return peaks;
  let seen = false;
  return peaks.map(p => {
    const q = { ...p };
    if (typeof q.isChargeReference !== 'boolean') q.isChargeReference = false;
    if (q.isChargeReference) {
      if (seen) q.isChargeReference = false;
      else seen = true;
    }
    return q;
  });
}

// Toggle the charge-reference designation on peak `id`.
// Enforces single-reference invariant: marking one peak clears all others.
// Clicking the already-marked peak clears it (zero-reference state).
function toggleChargeReference(id) {
  const target = getPeak(id);
  if (!target) return;
  pushUndo();
  const turningOn = !target.isChargeReference;
  for (const p of state.peaks) p.isChargeReference = false;
  if (turningOn) target.isChargeReference = true;
  renderPeakList();
}

// Returns true iff the active tab has exactly one peak marked as the

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
    return { peak: p, peakOnly, y: peakOnly.map((v, i) => v + bg[i]) };
  });

  return { be, bg, rawY, fittedY, peaks: peakCurves };
}

// Cached wrapper around _buildEntryRenderData. Stored on the entry as
// entry._renderDataCache. Slider drags and other in-place updates hit
// the cache; _renderStackChart clears all entry caches before rebuild,
// which is the only path that runs when source-tab state changes
// (peak edits, ccShift edits, re-fits all happen while user is on the
// source tab — they return to the stack via activateTab → updatePlot →
// _renderStackChart, picking up fresh data).
//
// The big win: Path B (post-load) recomputes a Shirley background per
// call, which costs ~1-2 ms per entry. Without the cache, that compute
// fires on every offset/line-width slider tick (60 Hz) for every fit
// entry — visible stutter. With the cache, slider drag is O(1) lookup.
function _getEntryRenderData(entry) {
  if (entry._renderDataCache) return entry._renderDataCache;
  const rd = _buildEntryRenderData(entry);
  entry._renderDataCache = rd;
  return rd;
}

// Read the four toolbar pill states once per stack render. On stack
// tabs, _isBgSubViewActive() returns false unconditionally (state.rawBE
// is empty/inert), so the bg-sub gate is just the pill's checked state.
// Defaults match the pills' initial checked state in the HTML.
function _readStackPillState() {
  return {
    showEnvelope:   document.getElementById('show-envelope')?.checked   ?? true,
    showIndividual: document.getElementById('show-individual')?.checked ?? true,
    showFill:       document.getElementById('show-fill')?.checked       ?? true,
    bgSubView:      document.getElementById('bg-sub-toggle')?.checked   ?? false,
  };
}

// Count entries that have a valid source and are flagged visible.
// Drives the empty-state DOM message.
function _countVisibleStackEntries(stackTab) {
  let n = 0;
  for (const e of stackTab.entries) {
    if (!e.visible) continue;
    const src = tabManager._getTab(e.sourceTabId);
    if (src && Array.isArray(src.rawBE) && src.rawBE.length >= 2) n++;
  }
  return n;
}

// Pure builder. Per entry, emits up to 2 + 2×N_peaks datasets:
//   <id>:pbg:<peakId>   hidden background-level target for each peak fill
//   <id>:peak:<peakId>  filled peak component (raw-level peak + bg)
//   <id>:raw            solid raw spectrum
autofit/parity.py:10:   ``fitResult.fittedY``.  This proves the spec mirror
autofit/parity.py:142:    if not fr.get("fittedY") or not fr.get("be"):
autofit/parity.py:143:        return False, "legacy fitResult (no be/fittedY)"
autofit/parity.py:144:    if len(fr["fittedY"]) != len(fr["be"]):
autofit/parity.py:146:            f"internally inconsistent fitResult (fittedY {len(fr['fittedY'])} "
autofit/parity.py:147:            f"pts vs be {len(fr['be'])} pts — stale fittedY from an earlier ROI)"
autofit/parity.py:181:    fittedY (the saved result itself carries no mix). Such a pair fails eval
autofit/parity.py:193:    Max |python_eval − saved fittedY| / max|fittedY| on the reconstructed
autofit/parity.py:197:    server recorded for the fit that produced ``fittedY``
autofit/parity.py:202:    old request (eta free from 0.3) cannot reproduce their own fittedY that
autofit/parity.py:205:    fittedY = np.asarray(rf.fit_result["fittedY"], dtype=float)
autofit/parity.py:216:    scale = max(float(np.max(np.abs(fittedY))), 1.0)
autofit/parity.py:217:    return float(np.max(np.abs(model + bg - fittedY)) / scale)
autofit/parity.py:264:        "reduced_chi_square": res["statistics"]["reduced_chi_square"],
autofit/parity.py:265:        "r_factor": res["statistics"]["r_factor"],
autofit/candidates.py:32:pure counting-statistics anomaly measure.  Because the kernel is exactly
autofit/candidates.py:66:# counts (~2k) the envelope shifts one step coarser (counting statistics).
autofit/parity.py:10:   ``fitResult.fittedY``.  This proves the spec mirror
autofit/parity.py:142:    if not fr.get("fittedY") or not fr.get("be"):
autofit/parity.py:143:        return False, "legacy fitResult (no be/fittedY)"
autofit/parity.py:144:    if len(fr["fittedY"]) != len(fr["be"]):
autofit/parity.py:146:            f"internally inconsistent fitResult (fittedY {len(fr['fittedY'])} "
autofit/parity.py:147:            f"pts vs be {len(fr['be'])} pts — stale fittedY from an earlier ROI)"
autofit/parity.py:181:    fittedY (the saved result itself carries no mix). Such a pair fails eval
autofit/parity.py:193:    Max |python_eval − saved fittedY| / max|fittedY| on the reconstructed
autofit/parity.py:197:    server recorded for the fit that produced ``fittedY``
autofit/parity.py:202:    old request (eta free from 0.3) cannot reproduce their own fittedY that
autofit/parity.py:205:    fittedY = np.asarray(rf.fit_result["fittedY"], dtype=float)
autofit/parity.py:216:    scale = max(float(np.max(np.abs(fittedY))), 1.0)
autofit/parity.py:217:    return float(np.max(np.abs(model + bg - fittedY)) / scale)
autofit/parity.py:264:        "reduced_chi_square": res["statistics"]["reduced_chi_square"],
autofit/parity.py:265:        "r_factor": res["statistics"]["r_factor"],
autofit/methods/bayesian_exchange_mc.py:135:    energy (stepping-stone), acceptance statistics, and the noise estimate.
autofit/methods/least_squares.py:83:        stats = res["statistics"]
autofit/methods/least_squares.py:90:                "statistics": stats,
"""Real-browser test for the "fit the entire window" checkbox's actual
visible effect (2026-07-14 bug report — the checkbox was a no-op).

ROOT CAUSE (found by tracing, not guessed): the backend's position-bound
widening (autofit/engine.py's ``fit_full_window`` — added 2026-07-13)
works exactly as designed and reaches the winning candidate correctly,
but has near-zero observable effect on real spectra, because Find
Peaks' out-of-grammar detection/proposal machinery already finds real
peaks wherever they sit, independent of this flag. The user's actual
symptom ("ROI: 278.0-290.4" shown when 278-298 was set) traced to a
DIFFERENT, purely-frontend bug: ``updatePlot()`` freezes the chart's
background/fit-curve rendering to ``state.fitResult``'s own frozen
``be``/``bgIntensity`` arrays once ANY fit exists (a prior manual Run
Fit, or Auto-Fit C1s Graphite) — and ``applyFindPeaks()`` never touched
``state.fitResult`` at all, so applying new Find-Peaks-suggested peaks
left the chart showing background/fit cropped to whatever OLD, possibly
much narrower range a prior fit happened to freeze it to, regardless of
how wide a window Find Peaks itself just used.

The fix: when the analyze request that produced the applied peaks used
``fit_full_window: true``, ``applyFindPeaks()`` now clears
``state.fitResult`` before re-rendering — ``updatePlot()`` then falls
back to its existing unfit-preview path (``getROIData()`` + client-side
``computeBackground()``), which correctly spans whatever the CURRENT
``#roi-min``/``#roi-max`` fields say (the same fields Find Peaks itself
just read at submit time). Default (unchecked) leaves
``state.fitResult`` untouched — today's (possibly stale/cropped)
behavior is unchanged, as required.

This file proves the full, real bug scenario end to end: a tab with a
PRIOR, narrower frozen fit (matching the bug report's exact numbers),
then Find Peaks run + applied with the checkbox on vs. off, checking the
ACTUAL RENDERED CHART DATA (not just the backend response) for both.
Skips cleanly when Playwright/Chromium/gunicorn are absent, same as the
other browser tests.
"""
import glob
import os
import socket
import subprocess
import sys
import time
import urllib.request

import pytest

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import sync_playwright  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _find_chromium():
    base = os.path.expanduser("~/Library/Caches/ms-playwright")
    patterns = [
        base + "/chromium-*/chrome-mac*/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
        base + "/chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium",
        base + "/chromium-*/chrome-linux/chrome",
        base + "/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell",
    ]
    for pat in patterns:
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[-1]
    return None


def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture(scope="module")
def server():
    gunicorn = os.path.join(os.path.dirname(sys.executable), "gunicorn")
    if not os.path.exists(gunicorn):
        pytest.skip("gunicorn not found next to the test interpreter")
    port = _free_port()
    proc = subprocess.Popen(
        [gunicorn, "app:app", "-w", "1", "-b", f"127.0.0.1:{port}", "--timeout", "90"],
        cwd=REPO_ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    try:
        ok = False
        for _ in range(50):
            if proc.poll() is not None:
                pytest.skip("gunicorn exited during startup")
            try:
                with urllib.request.urlopen(base + "/api/health", timeout=1) as r:
                    if r.status == 200:
                        ok = True
                        break
            except Exception:
                time.sleep(0.2)
        if not ok:
            pytest.skip("gunicorn did not become healthy")
        yield base
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


@pytest.fixture(scope="module")
def browser():
    exe = _find_chromium()
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(headless=True)
        except Exception:
            if not exe:
                pytest.skip("no usable Chromium build found")
            b = p.chromium.launch(headless=True, executable_path=exe)
        yield b
        b.close()


def _new_page(browser, server):
    pg = browser.new_page(viewport={"width": 1000, "height": 1000})

codex
I found a refresh gap: individual locks and Lock All can change the key without reaching the new statistics refresh, leaving the old values visible. I’m reproducing that path and checking whether Clear All has the same problem.
exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\''),html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\''),lines=html.split('\\''\\n'\\'');
function fn(name) { let a=lines.findIndex(l=>new RegExp('\\''"'^(async )?function '"'\\''+name+'\\''\\\\('\\'').test(l)), d=0, seen=false; for(let i=a;i<lines.length;i++){for(const c of lines[i]){if(c==='\\''{'\\''){d++;seen=true;}else if(c==='\\''}'\\'')d--;}if(seen&&"'!d)return lines.slice(a,i+1).join('"'\\''\\n'\\'');}throw name; }
const constants=html.slice(html.indexOf('\\''const _STARTS_MODEL_FIELDS'\\''),html.indexOf('\\''function _startsModelKey'\\''));
const run=new Function(constants+'\\''\\n'\\''+[\"_startsModelKey\",\"_startsLiveKey\",\"_statsState\",\"_statsLiveState\",\"_refreshStatsState\",\"toggleLock\",\"toggleAllLocks\",\"_lockAllStats\",\"_refreshStartsEvidence\",\"_dropStaleAltPreview\",\"clearAllPeaks\"].map(fn).join('\\''\\n'\\'')+\"\\n const state={peaks:[{id:1,center:284.5,fixCenter:false}],ccShift:0,chart:{data:{datasets:[]}}};\\n const tabManager={_captureUI:()=>({roiMin:'\\''280'\\'',roiMax:'\\''290'\\''})};\\n let _historyPreview=null, renders=0, updates=0;\\n const LOCK_ALL_KEYS=['\\''fixCenter'\\'','\\''fixFwhm'\\'','\\''fixAmplitude'\\'','\\''fixAsymmetry'\\'','\\''fixGlMix'\\'','\\''fixDsAlpha'\\'','\\''fixDsGamma'\\''];\\n const results={rendered:'\\''current'\\'',getAttribute(){return this.rendered}};\\n const document={getElementById:id=>id==='\\''results-area'\\''?results:null,querySelectorAll:()=>[],querySelector:()=>null};\\n const _isUnsupported=()=>false,_updateLockAllBtn=()=>{},renderPeakList=()=>{},pushUndo=()=>{},confirm=()=>true,_activeTab=()=>null;\\n const _applyStatDisplay=()=>{},_updateRFactorUI=()=>{};\\n function renderResults(){renders++; results.rendered=_statsLiveState();}\\n function updatePlot(){updates++;_refreshStatsState();_refreshStartsEvidence(false,true);}\\n state.fitResult={chiReduced:1.234,startsModelKey:_startsLiveKey()};\\n toggleLock(1,'\\''fixCenter'\\'',{});\\n const lock={actual:_statsLiveState(),rendered:results.rendered,renders,updates};\\n state.peaks[0].fixCenter=false;\\n toggleAllLocks();\\n const all={actual:_statsLiveState(),rendered:results.rendered,renders,updates};\\n clearAllPeaks();\\n return {lock,all,clear:{actual:_statsLiveState(),rendered:results.rendered,renders,updates}};\\n\"); console.log(JSON.stringify(run(),null,2));'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 exited 1 in 0ms:
<anonymous_script>:35
  const p = getPeak(id);
            ^

ReferenceError: getPeak is not defined
    at toggleLock (eval at <anonymous> ([eval]:4:11), <anonymous>:35:13)
    at eval (eval at <anonymous> ([eval]:4:11), <anonymous>:118:2)
    at [eval]:4:1610
    at runScriptInThisContext (node:internal/vm:209:10)
    at node:internal/process/execution:446:12
    at [eval]-wrapper:6:24
    at runScriptInContext (node:internal/process/execution:444:60)
    at evalFunction (node:internal/process/execution:279:30)
    at evalTypeScript (node:internal/process/execution:291:3)
    at node:internal/main/eval_string:74:3

Node.js v22.22.2

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\''),html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\''),lines=html.split('\\''\\n'\\'');
function fn(name) { let a=lines.findIndex(l=>new RegExp('\\''"'^(async )?function '"'\\''+name+'\\''\\\\('\\'').test(l)), d=0, seen=false; for(let i=a;i<lines.length;i++){for(const c of lines[i]){if(c==='\\''{'\\''){d++;seen=true;}else if(c==='\\''}'\\'')d--;}if(seen&&"'!d)return lines.slice(a,i+1).join('"'\\''\\n'\\'');}throw name; }
const constants=html.slice(html.indexOf('\\''const _STARTS_MODEL_FIELDS'\\''),html.indexOf('\\''function _startsModelKey'\\''));
const run=new Function(constants+'\\''\\n'\\''+[\"getPeak\",\"_startsModelKey\",\"_startsLiveKey\",\"_statsState\",\"_statsLiveState\",\"_refreshStatsState\",\"toggleLock\",\"toggleAllLocks\",\"_lockAllStats\",\"_refreshStartsEvidence\",\"_dropStaleAltPreview\",\"clearAllPeaks\"].map(fn).join('\\''\\n'\\'')+\"\\n const state={peaks:[{id:1,center:284.5,fixCenter:false}],ccShift:0,chart:{data:{datasets:[]}}};\\n const tabManager={_captureUI:()=>({roiMin:'\\''280'\\'',roiMax:'\\''290'\\''})};\\n let _historyPreview=null, renders=0, updates=0;\\n const LOCK_ALL_KEYS=['\\''fixCenter'\\'','\\''fixFwhm'\\'','\\''fixAmplitude'\\'','\\''fixAsymmetry'\\'','\\''fixGlMix'\\'','\\''fixDsAlpha'\\'','\\''fixDsGamma'\\''];\\n const results={rendered:'\\''current'\\'',getAttribute(){return this.rendered}};\\n const document={getElementById:id=>id==='\\''results-area'\\''?results:null,querySelectorAll:()=>[],querySelector:()=>null};\\n const _isUnsupported=()=>false,_updateLockAllBtn=()=>{},renderPeakList=()=>{},pushUndo=()=>{},confirm=()=>true,_activeTab=()=>null;\\n const _applyStatDisplay=()=>{},_updateRFactorUI=()=>{};\\n function renderResults(){renders++; results.rendered=_statsLiveState();}\\n function updatePlot(){updates++;_refreshStatsState();_refreshStartsEvidence(false,true);}\\n state.fitResult={chiReduced:1.234,startsModelKey:_startsLiveKey()};\\n toggleLock(1,'\\''fixCenter'\\'',{});\\n const lock={actual:_statsLiveState(),rendered:results.rendered,renders,updates};\\n state.peaks[0].fixCenter=false;\\n toggleAllLocks();\\n const all={actual:_statsLiveState(),rendered:results.rendered,renders,updates};\\n clearAllPeaks();\\n return {lock,all,clear:{actual:_statsLiveState(),rendered:results.rendered,renders,updates}};\\n\"); console.log(JSON.stringify(run(),null,2));'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
{
  "lock": {
    "actual": "stale",
    "rendered": "current",
    "renders": 0,
    "updates": 0
  },
  "all": {
    "actual": "stale",
    "rendered": "current",
    "renders": 0,
    "updates": 0
  },
  "clear": {
    "actual": "none",
    "rendered": "current",
    "renders": 0,
    "updates": 1
  }
}

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\''),html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\''),lines=html.split('\\''\\n'\\'');
function fn(name) { let a=lines.findIndex(l=>new RegExp('\\''"'^(async )?function '"'\\''+name+'\\''\\\\('\\'').test(l)), d=0, seen=false; for(let i=a;i<lines.length;i++){for(const c of lines[i]){if(c==='\\''{'\\''){d++;seen=true;}else if(c==='\\''}'\\'')d--;}if(seen&&"'!d)return lines.slice(a,i+1).join('"'\\''\\n'\\'');}throw name; }
const constants=html.slice(html.indexOf('\\''const _STARTS_MODEL_FIELDS'\\''),html.indexOf('\\''function _startsModelKey'\\''));

const at=html.indexOf('\\''  const buildTabData = (t) => {'\\'',html.indexOf('\\''async function _doSaveProject'\\''));
const end=html.indexOf('\\''\\n  const meta = {'\\'',at);
const build=html.slice(at,end);
const extra=html.match(/"'^const _STATS_'"\\w+_NOTE = .*"'$/mg).join('"'\\''\\n'\\'');
const stubs=\"const _roundBE=a=>a,_roundIntensity=a=>a,RefCore={serializeRefOverlays:()=>null},_isLocalFit=()=>false,_localFitCaveat=()=>'\\'''\\'';\";
const run=new Function(constants+'\\''\\n'\\''+extra+'\\''\\n'\\''+[\"gaussian\",\"evalPeak\",\"evalPeakArray\",\"evalAllPeaks\",\"_computeRFactor\",\"_invalidateFittedY\",\"_startsModelKey\",\"_startsLiveKey\",\"_startsRecordKey\",\"_startsIfCurrent\",\"_statsState\",\"_statsLiveState\",\"_statsRecordState\",\"_statsNote\",\"_statsSaveFields\",\"_startsForSave\"].map(fn).join('\\''\\n'\\'')+'\\''\\n'\\''+stubs+'\\''\\n'\\''+build+\"\\nconst state={peaks:[{id:1,shape:'\\''Gaussian'\\'',center:1,fwhm:1,amplitude:100}],ccShift:0};\\nconst ui={bgType:'\\''linear'\\'',bgStart:'\\''2'\\'',bgEnd:'\\''0'\\'',roiMin:'\\''0'\\'',roiMax:'\\''2'\\'',endpointAvg:'\\''3'\\'',shirleyIter:'\\''5'\\''};\\nconst tabManager={_captureUI:()=>ui};\\nconst be=[2,1,0],bg=[0,0,0],data=evalAllPeaks(be,state.peaks);\\nstate.fitResult={be,bgIntensity:bg,bgSubtracted:data,fittedY:data.slice(),startsModelKey:_startsLiveKey()};\\nconst originalR=_computeRFactor(state.fitResult);\\nstate.peaks[0].amplitude=50; _invalidateFittedY();\\nconst t={id:'\\''t'\\'',name:'\\''t'\\'',rawBE:be,rawIntensity:data,peaks:state.peaks,ui,ccShift:0,fitResult:state.fitResult};\\nconst saved=JSON.parse(JSON.stringify(buildTabData(t)));\\nstate.peaks=saved.peaks; state.fitResult=saved.fitResult;\\nif(state.fitResult && state.fitResult.rFactor==null) state.fitResult.rFactor=_computeRFactor(state.fitResult);\\nconst reloaded={state:_statsLiveState(),r:state.fitResult.rFactor};\\nstate.peaks[0].amplitude=100; _invalidateFittedY();\\nreturn {originalR,reloaded,restored:{state:_statsLiveState(),displayedR:state.fitResult.rFactor,correctR:_computeRFactor(state.fitResult)}};\\n\");
console.log(JSON.stringify(run(),null,2));
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 0ms:
{
  "originalR": {
    "rPct": 0,
    "level": "good"
  },
  "reloaded": {
    "state": "stale",
    "r": {
      "rPct": 50,
      "level": "red"
    }
  },
  "restored": {
    "state": "current",
    "displayedR": {
      "rPct": 50,
      "level": "red"
    },
    "correctR": {
      "rPct": 0,
      "level": "good"
    }
  }
}

exec
/bin/zsh -lc "sed -n '1,170p' tests/js/fit_acceptance.test.js; sed -n '42,132p' tests/js/local_lm_descent.test.js; sed -n '8480,8555p' templates/index.html; rg -n 'oninput=.*[Rr][Ss][Ff]|function recalcQuantify|function renderQuantify|rsf-' templates/index.html; git branch --show-current; rg -n 'not ok|server parity' tests/js/local_lm_descent.test.js" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
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
  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_startsIfCurrent'].map(extractFn).join('\n');
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
  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_startsIfCurrent'].map(extractFn).join('\n');
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
  const env = makeEnv({ fetchImpl: okResponse({ success: true, statistics: { reduced_chi_square: 1.2 }, residuals: [], fitted_y: [], individual_peaks: [] }) });
  await env.runFit();
  assert.equal(env.calls.applied, 1);
  assert.equal(env.calls.local, 0);
  assert.notEqual(env.state.fitResult.marker, 'previous');
  assert.equal(env.dom['sb-msg'].textContent, 'Fit complete (lmfit)', 'the success path must run to completion, not die in an exception');
});

test('the engine/objective labels of a fit result survive spectrum and project save/load', () => {
  const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
  // spectrum save: statistics block carries objective/engine; loader restores them
  const save = grab('function _doSaveSpectrum()', 2500);
  assert.match(save, /objective: state\.fitResult\.objective/);
  assert.match(save, /engine: state\.fitResult\.engine/);
  const load = grab('function _loadSpectrumFile(', 6000);
  assert.match(load, /\['engine', 'objective', 'weighting', 'status', 'caveat', 'starts', 'startsModelKey', 'chosenAlternative'\]/);
  // project save: the whitelisted fitResult record carries them
  const proj = grab('const buildTabData = (t) =>', 3000);
  assert.match(proj, /objective: t\.fitResult\.objective/);
  assert.match(proj, /engine: t\.fitResult\.engine/);
});

// ── Codex round-1 findings (2026-09-15): HTTP failures with non-JSON bodies ──

function envWithFetch(fetchImpl, uploadImpl) { return makeEnv({ fetchImpl, uploadImpl }); }

test('an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback', async () => {
  const env = envWithFetch(async () => ({ ok: false, status: 502, json: async () => { throw new SyntaxError('Unexpected token <'); } }));
  await env.runFit();
  assert.equal(env.calls.local, 0, 'no fallback on a 502');
  assert.equal(env.calls.applied, 0);
  assert.ok(env.calls.notify.some(n => n.kind === 'red' && /502/.test(n.msg)), JSON.stringify(env.calls.notify));
});

test('an HTTP 502 on the upload is a server failure, not a transport failure', async () => {
  const env = envWithFetch(async () => { throw new Error('fit must not be reached'); }, async () => { const e = new Error('Upload failed (HTTP 502).'); e.serverError = true; throw e; });
  await env.runFit();
  assert.equal(env.calls.local, 0);
  assert.ok(env.calls.notify.some(n => n.kind === 'red' && /502/.test(n.msg)));
});

test('uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id', async () => {
  const src = extractFn('uploadToBackend');
  const make = fetchImpl => new Function('fetch', 'FormData', 'Blob', src + '\nreturn uploadToBackend;')(fetchImpl, class { append() {} }, class {});
  await assert.rejects(make(async () => ({ ok: false, status: 502, json: async () => { throw new SyntaxError('<html>'); } }))([1], [1]), e => e.serverError === true && /502/.test(e.message));
  await assert.rejects(make(async () => ({ ok: true, status: 200, json: async () => ({}) }))([1], [1]), e => e.serverError === true && /session/i.test(e.message));
  await assert.rejects(make(async () => { throw new TypeError('Failed to fetch'); })([1], [1]), e => !e.serverError);
});

test('every consumer that prints the goodness-of-fit statistic routes through the statistic identity', () => {
  const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
  // figure export annotation
  const fig = grab('function exportFigure()', 60000);
  assert.match(fig, /_isLocalFit\(state\.fitResult\)/, 'figure export must label the statistic by engine');
  assert.match(fig, /Residual variance \(local fit, not reportable\)/, 'figure annotation names the legacy unweighted statistic');
  '_computeRFactor', '_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel', '_governingProvenance', '_localFitCaveat', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay', '_updateLocalModelBanner',
  '_componentSupportCore', '_supportRootOf', '_applySupportVerdicts', '_statsState', '_statsLiveState'];
const CAVEAT_CONST = (html.match(/^const (_LOCAL_FIT_CAVEAT\w*|_STATS_\w+_NOTE) = .*$/mg) || []).join('\n');

// One isolated environment per test: a fresh `state`, a stub DOM, and the
// extracted functions bound to them.
function makeEnv() {
  const dom = {};
  const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, setAttribute() {}, removeAttribute() {},
    classList: { add() {}, remove() {}, contains: () => false } });
  const document = { getElementById: el, querySelectorAll: () => [] };
  const state = { peaks: [], fitResult: null, rawBE: [], rawIntensity: [], ccShift: 0 };
  const calls = { notify: [] };
  const notify = (msg, kind) => calls.notify.push({ msg, kind });
  const noop = () => {};
  const src = CAVEAT_CONST + '\nconst _SUPPORT_MIN_F = 10; const _startsLiveKey = () => "KEY";\n' + NAMES.map(extractFn).join('\n\n');
  const factory = new Function('document', 'state', 'notify', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_activeTab', '_escHtml', '_historyPreview', 'tabManager', '_updateRFactorUI', '_updateROIDisplay',
    'renderPeakList', 'updatePlot', 'renderResults', '_hideFitSpinner', '_autoSnapshot', 'manualAnchorBackground',
    src + '\nreturn { runFitLocal, computeBackgroundCore, evalAllPeaks, evalPeakArray, gaussian };');
  const fns = factory(document, state, notify, '', '', () => null, x => String(x), null, null, noop, noop, noop, noop, noop, noop, noop,
    be => new Array(be.length).fill(0));
  return { ...fns, state, dom, calls };
}

// ── Committed lab project, replayed exactly as runPropagation does ──────────
const PROJECT = path.join(REPO_ROOT, 'docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip');
const BatchPropagation = require(path.join(REPO_ROOT, 'static/js/batch_propagation.js'));

function loadProjectTabs() {
  const py = fs.existsSync(path.join(REPO_ROOT, 'venv/bin/python3')) ? path.join(REPO_ROOT, 'venv/bin/python3')
    : (fs.existsSync('/Users/skyefortier/xps-app/venv/bin/python3') ? '/Users/skyefortier/xps-app/venv/bin/python3' : 'python3');
  const script = 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; ' +
    'print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))';
  return JSON.parse(execFileSync(py, ['-c', script, REPO_ROOT, PROJECT], { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }));
}

function batchTarget(env, tabs, sourceName, targetName) {
  const src = tabs.find(t => t.name === sourceName), tgt = tabs.find(t => t.name === targetName);
  assert.ok(src && tgt, 'source/target tabs present in committed project');
  const scale = Math.max(...tgt.rawIntensity) / Math.max(...src.rawIntensity);
  const cloned = JSON.parse(JSON.stringify(src.peaks)).map(p => ({ ...p, amplitude: p.linked ? p.amplitude : p.amplitude * scale }));
  const ui = BatchPropagation.propagateFitUi({ ...src.ui }, { ...tgt.ui });
  const roiMin = parseFloat(ui.roiMin), roiMax = parseFloat(ui.roiMax);
  const be = [], inten = [];
  tgt.rawBE.forEach((b, i) => { const c = b - (src.ccShift || 0); if (c >= roiMin && c <= roiMax) { be.push(c); inten.push(tgt.rawIntensity[i]); } });
  const bg = env.computeBackgroundCore(be, inten, ui);
  const bgSub = inten.map((v, i) => v - bg[i]);
  env.state.peaks = cloned;
  env.state.fitResult = null;
  return { be, bgSub, bg, initial: JSON.parse(JSON.stringify(cloned)) };
}

// The objective the local engine minimises since unit W1: the Poisson-weighted
// sum of squares, w = 1/sqrt(max(raw counts, 1)), raw = bgSub + bg.
function residualSS(env, be, bgSub, bg) {
  const m = env.evalAllPeaks(be, env.state.peaks);
  return be.reduce((s, _, i) => { const raw = bgSub[i] + (bg ? bg[i] : 0); return s + (bgSub[i] - m[i]) ** 2 / Math.max(raw, 1); }, 0);
}

test('A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters', () => {
  const tabs = loadProjectTabs();
  for (const target of ['C1s Scan_0', 'C1s Scan_4', 'C1s Scan_8']) {
    const env = makeEnv();
    const { be, bgSub, bg, initial } = batchTarget(env, tabs, 'C1s Scan', target);
    const chi0 = residualSS(env, be, bgSub, bg);
    const out = env.runFitLocal(be, bgSub, bg);
    assert.ok(out && out.success === true, `${target}: runFitLocal must report success, got ${JSON.stringify(out)}`);
    const chi1 = residualSS(env, be, bgSub, bg);
    assert.ok(chi1 < 0.5 * chi0, `${target}: residual must drop substantially (before ${chi0.toExponential(3)}, after ${chi1.toExponential(3)})`);
    const moved = env.state.peaks.some((p, i) => Math.abs(p.center - initial[i].center) > 1e-3 || Math.abs(p.fwhm / initial[i].fwhm - 1) > 1e-3);
    assert.ok(moved, `${target}: at least one free centre/width must move — the shipped code returned the starting model on 18/18 targets`);
    assert.ok(env.state.fitResult && env.state.fitResult.status === 'converged', 'a converged local fit records status: converged');
  }
});

test('A01 replay: the linked U 4f pair also descends', () => {
  const tabs = loadProjectTabs();
  const env = makeEnv();
  const { be, bgSub, bg } = batchTarget(env, tabs, 'U4f Scan', 'U4f Scan_3');
  const chi0 = residualSS(env, be, bgSub, bg);
  const out = env.runFitLocal(be, bgSub, bg);
  assert.equal(out.success, true);
  assert.ok(residualSS(env, be, bgSub, bg) < 0.5 * chi0);
  const parent = env.state.peaks.find(p => !p.linked && p.shape === 'LACX');
  const child = env.state.peaks.find(p => p.linked);
  assert.ok(Math.abs(child.center - (parent.center + child.linkOffset)) < 1e-9, 'linked centre follows the parent');
  assert.ok(Math.abs(child.amplitude - parent.amplitude * child.linkRatio) < 1e-6, 'linked amplitude follows the parent');
});

test('noiseless Gaussian: amplitude 10 started at 5 is recovered', () => {
  const env = makeEnv();
      for (let a = 0; a < n; a++) {
        lin += Jtr[a] * step[a];
        for (let b = 0; b < n; b++) quad += step[a] * JtJ0[a][b] * step[b];
      }
      const prered = (-2 * lin - quad) / Math.max(chi, 1e-300);
      const relStep = Math.max(0, ...step.map((d, i) => Math.abs(d) / paramScale(i, params)));
      params = newParams;
      chi = newChi;
      acceptedSteps++;
      lambda *= 0.7;
      if (chi === 0 || (prered > 0 && actred <= FTOL && prered <= FTOL && actred / prered <= 2) || relStep <= XTOL) {
        if (certify()) { converged = true; break; }
      }
    } else {
      lambda *= 3;
      if (lambda > 1e8) {
        // Even a tiny steepest-descent step no longer reduces the residual,
        // yet the projected gradient is not small: stalled, not converged.
        return fail('the optimiser stalled (no step reduces the residual) after ' + iterations + ' iterations.', iterations);
      }
    }
  }
  if (!converged) return fail('iteration limit (' + maxIter + ') reached.', iterations);

  // ── Converged: commit the working copy to the live peaks ──────────────────
  applyParams(params);
  for (const p of work) {
    const live = getPeak(p.id);
    if (!live) continue;
    Object.assign(live, p);
    // A local fit has no backend covariance; any _backendParams on the peak
    // belong to an earlier server fit (or, in Batch Fit, to the SOURCE
    // spectrum's fit) and must not travel with this result.
    delete live._backendParams;
  }

  // Degrees of freedom count the parameters this engine varies (caM is held,
  // not one of them; parameters temporarily blocked at a wall still count).
  const nVaried = params.filter((_, j) => !isDiscrete(j)).length;
  const dof = Math.max(1, be.length - nVaried);
  const chiReduced = chi / dof;                       // weighted reduced chi-square, as lmfit's redchi
  const _raw = rawResiduals(params);
  const rmse = Math.sqrt(_raw.reduce((a, v) => a + v * v, 0) / be.length);   // unweighted RMS, as the server path reports
  // "Not supported by the data": the same removal statistic the server
  // computes, from this engine's own residuals and weights (a component driven
  // to the zero floor is an outcome here too, not something to hide).
  {
    const model = evalAllPeaks(be, work);
    const verdicts = {};
    for (const wp of work) {
      if (wp.linked) continue;
      const comp = evalPeakArray(be, wp);
      const nFreeComp = paramMap.filter(d => d.id === wp.id && !isDiscrete(paramMap.indexOf(d))).length;
      verdicts[String(wp.id)] = _componentSupportCore(bgSubtracted, model, comp, _w, nFreeComp, nVaried);
    }
    _applySupportVerdicts(state.peaks, id => verdicts[String(id)] || null, _startsLiveKey());
  }

  // KNOWN LIMITATION: this engine produces no parameter uncertainties; the
  // results panel shows blank sigma for every parameter after a local fit.
  const roiRange = { min: _arrMin(be).toFixed(1), max: _arrMax(be).toFixed(1) };
  { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }   // a new result supersedes imported provenance
  state.fitResult = { chi, chiReduced, rmse, be, bgSubtracted, bgIntensity, roiRange,
                      engine: 'local', status: 'converged',
                      objective: 'poisson_weighted_chi_square', weighting: '1/sqrt(max(counts,1))', iterations,
                      reportable: false, caveat: _LOCAL_FIT_CAVEAT,
                      startsModelKey: _startsLiveKey() };   // F1: the statistics describe the committed model
  state.fitResult.rFactor = _computeRFactor(state.fitResult);

  _applyStatDisplay(state.fitResult);
  document.getElementById('sb-msg').textContent = 'Fit complete (local)';
  _updateRFactorUI(state.fitResult.rFactor);
  _updateROIDisplay(roiRange);

  renderPeakList();
  updatePlot();
8777:function renderQuantify(areas, totalArea) {
8797:      <select id="rsf-source" style="font-size:11px;padding:2px 6px;background:var(--bg3);border:1px solid var(--border2);color:var(--text);border-radius:var(--radius)" onchange="onRSFSourceChange(this.value)">
8825:      <td><input type="number" value="${useRSF.toFixed(3)}" step="0.001" min="0.001" style="width:62px;font-size:11px;padding:2px 4px" onchange="onRSFInputChange(${p.id},this.value)" id="rsf-${p.id}"></td>
8827:        <select style="font-size:10px;padding:1px 3px;background:var(--bg3);border:1px solid var(--border);color:var(--text2);border-radius:var(--radius);max-width:80px" onchange="onRSFElemChange(${p.id},this.value)" id="rsf-elem-${p.id}">
8864:    document.getElementById('rsf-source').value = 'scofield';
8869:    const inp = document.getElementById('rsf-' + p.id);
8894:  const inp = document.getElementById('rsf-' + peakId);
8899:function recalcQuantify() {
8906:    const rsf = parseFloat(document.getElementById('rsf-' + p.id)?.value || 1);
11407:    const el = document.getElementById('rsf-' + p.id);
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-04YhRUq0' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-mfQtYqqB' (errno=Operation not permitted)
fix-stale-statistics
455:test('server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)', () => {

codex
The refresh reproductions confirm both gaps: locks leave Results marked current, and Clear All leaves the old Results table displayed. I also reproduced an R-factor error after a stale project reload: restoring the original model makes the key current, but the displayed R remains 50% instead of the correct 0%.

The requested JavaScript tests finished with 106 passes and one failure: the Python parity test could not initialize a temporary directory in this read-only sandbox.
exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\''),html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\''),lines=html.split('\\''\\n'\\'');
function fn(name) { let a=lines.findIndex(l=>new RegExp('\\''"'^(async )?function '"'\\''+name+'\\''\\\\('\\'').test(l)), d=0, seen=false; for(let i=a;i<lines.length;i++){for(const c of lines[i]){if(c==='\\''{'\\''){d++;seen=true;}else if(c==='\\''}'\\'')d--;}if(seen&&"'!d)return lines.slice(a,i+1).join('"'\\''\\n'\\'');}throw name; }
const constants=html.slice(html.indexOf('\\''const _STARTS_MODEL_FIELDS'\\''),html.indexOf('\\''function _startsModelKey'\\''));

const localTest=fs.readFileSync('\\''tests/js/local_lm_descent.test.js'\\'','\\''utf8'\\'');
const names=new Function(localTest.match(/const NAMES = [\\s\\S]*?;/)[0]+'\\''return NAMES;'\\'')();
const all=[...new Set([...names.filter(x=>x"'!=='"'\\''_startsLiveKey'\\''),'\\''_startsModelKey'\\'','\\''_startsLiveKey'\\'','\\''runFit'\\'','\\''getCorrectedBE'\\'','\\''getROIData'\\'','\\''peakToBackendSpec'\\'','\\''_startsUnlinkedCount'\\''])];
const extra=(html.match(/"'^const (_LOCAL_FIT_CAVEAT'"\\w*|_STATS_\\w+_NOTE) = .*"'$/mg)||[]).join('"'\\''\\n'\\'')+'\\''\\nconst _SUPPORT_MIN_F=10,_STARTS_N=3;'\\'';
const AsyncFunction=Object.getPrototypeOf(async function(){}).constructor;
const run=new AsyncFunction(constants+'\\''\\n'\\''+extra+'\\''\\n'\\''+all.map(fn).join('\\''\\n'\\'')+\"\\nconst state={peaks:[{id:1,shape:'\\''Gaussian'\\'',name:'\\''p'\\'',center:285,fwhm:1,amplitude:5,fixCenter:true,fixFwhm:true}],ccShift:0,rawBE:Array.from({length:101},(_,i)=>280+i/10),fitResult:null};\\nstate.rawIntensity=state.rawBE.map(b=>gaussian(b,285,1,10));\\nconst dom={}; const el=id=>dom[id] ||= {value:'\\'''\\'',textContent:'\\'''\\'',style:{},classList:{add(){},remove(){}},setAttribute(){},removeAttribute(){}};\\nconst document={getElementById:el,querySelectorAll:()=>[]};\\nel('\\''roi-min'\\'').value='\\''280'\\'';el('\\''roi-max'\\'').value='\\''290'\\'';el('\\''bg-type'\\'').value='\\''linear'\\'';el('\\''bg-start'\\'').value='\\''290'\\'';el('\\''bg-end'\\'').value='\\''280'\\'';\\nconst tabManager={_captureUI:()=>({roiMin:el('\\''roi-min'\\'').value,roiMax:el('\\''roi-max'\\'').value,bgType:el('\\''bg-type'\\'').value})};\\nconst _opOwner=()=>1,_ownerActive=()=>true,_activeTab=()=>null,_getManualAnchors=()=>[],pushUndo=()=>{},_showFitSpinner=()=>{},_hideFitSpinner=()=>{},notify=()=>{};\\nconst _updateRFactorUI=()=>{},_updateROIDisplay=()=>{},renderPeakList=()=>{},updatePlot=()=>{},renderResults=()=>{},_autoSnapshot=()=>{};\\nconst _snapshotSuppressed=false,_CHISQ_TOOLTIP='\\'''\\'',_LOCALFIT_TOOLTIP='\\'''\\'',_escHtml=x=>x;\\nlet _historyPreview=null;\\nconst computeBackground=be=>be.map(()=>0);\\nasync function uploadToBackend(){return '\\''sid'\\'';}\\nasync function fetch(){el('\\''roi-min'\\'').value='\\''284'\\'';el('\\''roi-max'\\'').value='\\''286'\\'';throw new TypeError('\\''network interrupted after ROI edit'\\'');}\\nawait runFit();\\nreturn {state:_statsLiveState(),liveROI:[el('\\''roi-min'\\'').value,el('\\''roi-max'\\'').value],fitROI:state.fitResult?.roiRange,keyMatches:state.fitResult?.startsModelKey===_startsLiveKey(),status:state.fitResult?.status};\\n\");
run().then(x=>console.log(JSON.stringify(x,null,2))).catch(console.error);
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 36ms:
Backend unreachable, falling back to local LM: network interrupted after ROI edit
{
  "state": "current",
  "liveROI": [
    "284",
    "286"
  ],
  "fitROI": {
    "min": "280.0",
    "max": "290.0"
  },
  "keyMatches": true,
  "status": "converged"
}

exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '7657,7673p'; nl -ba templates/index.html | sed -n '6030,6065p'; nl -ba templates/index.html | sed -n '8537,8550p'; nl -ba templates/index.html | sed -n '8030,8047p'; nl -ba templates/index.html | sed -n '3245,3256p'; nl -ba templates/index.html | sed -n '10399,10426p'; nl -ba templates/index.html | sed -n '7610,7624p'; rg --files static/js | wc -l; rg -n '\\bchi\\b|stderr|sigma|statistics|fitResult' static/js; git status --short" in /Users/skyefortier/xps-app/.claude/worktrees/fix-stale-statistics
 succeeded in 4ms:
?? docs/autofit/codex/f1_stale_statistics_verdict_runA.md
?? docs/autofit/codex/f1_stale_statistics_verdict_runB.md

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\''),html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\''),lines=html.split('\\''\\n'\\'');
function fn(name) { let a=lines.findIndex(l=>new RegExp('\\''"'^(async )?function '"'\\''+name+'\\''\\\\('\\'').test(l)), d=0, seen=false; for(let i=a;i<lines.length;i++){for(const c of lines[i]){if(c==='\\''{'\\''){d++;seen=true;}else if(c==='\\''}'\\'')d--;}if(seen&&"'!d)return lines.slice(a,i+1).join('"'\\''\\n'\\'');}throw name; }
const constants=html.slice(html.indexOf('\\''const _STARTS_MODEL_FIELDS'\\''),html.indexOf('\\''function _startsModelKey'\\''));
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
