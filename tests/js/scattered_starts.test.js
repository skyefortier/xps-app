// Scattered-starts check, page side (step (a), 2026-09-21). Owner decisions
// pinned here: the student's result remains the fit; only lower-chi-square
// solutions are listed, with their own areas and each component's move from
// the student's start; solutions that are not better are counted, not listed;
// "N starts reached this solution" — no certification language; adopting an
// alternative is explicit, undoable and recorded, and when its largest centre
// move is in the RED band (> 1 eV) it needs a confirmation that NAMES the
// component and the distance (the measured trap: a lower chi-square bought by
// sliding C-O 1.4 eV under the main line).
//
// All functions are extracted verbatim from templates/index.html.

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

const FNS = ['_isUnsupported', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_startsRecordKey', '_startsIfCurrent', '_dropStaleAltPreview',
  '_startsChosenText', '_startsForSave', '_startsSummaryText', '_startsPeakName',
  '_startsShiftColour', '_startsEv', '_startsShiftHtml', '_startsPanelHtml', '_altPeaks', '_currentAlternative',
  'previewAlternative', 'useAlternative', '_applyBackendParams'];
function makeEnv({ peaks, starts, confirmAnswer = true, staleKey = false }) {
  const calls = { confirm: [], pushUndo: 0, runFit: [], notify: [], updatePlot: 0, renderPeakList: 0 };
  const state = { peaks, ccShift: -4.74, fitResult: { chiReduced: starts && starts.fit ? starts.fit.chi2r : 1, starts } };
  const ui = { bgType: 'shirley', bgStart: '281.0', bgEnd: '294.0', shirleyIter: '5', endpointAvg: '3', roiMin: '280', roiMax: '295' };
  const anchors = [];
  const fieldsStart = lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS'));
  const fields = lines.slice(fieldsStart, lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n');
  const src = [constLine('_STARTS_N'), constLine('_STARTS_SHIFT_AMBER_EV'), constLine('_STARTS_TOOLTIP'), constLine('_STARTS_STALE_MSG'), constLine('_UNSUPPORTED_LABEL'), constLine('_UNSUPPORTED_TIP'), fields,
    'let _historyPreview = null; const document = { querySelectorAll: () => [] };', ...FNS.map(extractFn)].join('\n');
  const factory = new Function('state', 'getPeak', '_escHtml', 'confirm', 'pushUndo', 'runFit', 'notify', 'updatePlot',
    'renderPeakList', '_updateLocalModelBanner', '_historyClearPreview', 'tabManager', '_getManualAnchors',
    src + '\nreturn { ' + FNS.join(', ') + ', preview: () => _historyPreview, clear: () => { _historyPreview = null; } };');
  const api = factory(state, id => state.peaks.find(p => p.id === id || String(p.id) === String(id)),
    s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;'),
    msg => { calls.confirm.push(msg); return confirmAnswer; }, () => { calls.pushUndo++; },
    async o => { calls.runFit.push(o); }, (m, k) => calls.notify.push([k, m]), () => { calls.updatePlot++; },
    () => { calls.renderPeakList++; }, () => {}, () => { api.clear(); }, { _captureUI: () => ({ ...ui }) }, () => anchors);
  state.fitResult.startsModelKey = staleKey ? 'a different model' : api._startsLiveKey();
  return { ...api, state, calls, ui, anchors };
}

const PEAKS = () => [
  { id: 1, name: 'Graphite', shape: 'asym-GL', center: 284.40, fwhm: 0.64, amplitude: 86000, glMix: 16, asymmetry: 0.1, fixCenter: true },
  { id: 2, name: 'C-O', shape: 'GL', center: 286.41, fwhm: 1.42, amplitude: 2300, glMix: 0 },
  { id: 3, name: 'sat', shape: 'GL', center: 291.10, fwhm: 3.5, amplitude: 2600, glMix: 59 },
];
const comp = (id, pct, center, shift, extra = {}) => ({ id, shape: 'x', area: pct * 10, area_percent: pct, center_shift_from_start: shift,
  params: { center, amplitude: 1000 * id, fwhm: 1.1, gl_ratio: 0.25, ...extra } });
const STARTS = (alts, over = {}) => ({ ran: true, n_run: 3, n_converged: 3, n_same_as_fit: 3 - alts.length, n_not_better_elsewhere: 0,
  not_better_chi2r: [], fit: { chi2r: 17.55, largest_centre_shift_from_start: { id: 2, ev: 0.02 },
    components: [comp(1, 58, 284.40, 0), comp(2, 3, 286.43, 0.02), comp(3, 39, 291.1, 0)] }, alternatives: alts, ...over });
const ALT = (shiftEv, chi = 12.3) => ({ chi2r: chi, n_starts: 1, largest_fraction_difference_pp: 21.1,
  largest_centre_shift_from_start: { id: 2, ev: shiftEv },
  components: [comp(1, 49, 284.45, 0.05), comp(2, 24, 286.41 + shiftEv, shiftEv), comp(3, 27, 291.1, 0)] });

test('summary wording: counts of STARTS and of SOLUTIONS, never certification', () => {
  const { _startsSummaryText } = makeEnv({ peaks: PEAKS(), starts: STARTS([]) });
  assert.strictEqual(_startsSummaryText(STARTS([])), '3 of 3 scattered starts reached this solution.');
  assert.strictEqual(_startsSummaryText(STARTS([], { n_same_as_fit: 2, n_not_better_elsewhere: 1, not_better_chi2r: [7.912] })),
    '2 of 3 scattered starts reached this solution; 1 ended in a solution that is not better (χ²ᵣ 7.91).');
  assert.strictEqual(_startsSummaryText(STARTS([], { n_converged: 2, n_same_as_fit: 2 })),
    '2 of 3 scattered starts reached this solution; 1 did not converge.');
  assert.strictEqual(_startsSummaryText(STARTS([ALT(-1.4)])),
    '2 of 3 scattered starts reached this solution; 1 found a DIFFERENT solution with a lower χ²ᵣ. Your fit is unchanged.');
  // Codex round 1: all three starts reaching ONE different solution is three starts, not "one start"
  const allThree = STARTS([{ ...ALT(-1.4), n_starts: 3 }], { n_same_as_fit: 0 });
  assert.strictEqual(_startsSummaryText(allThree),
    '0 of 3 scattered starts reached this solution; 3 found a DIFFERENT solution with a lower χ²ᵣ. Your fit is unchanged.');
  assert.strictEqual(_startsSummaryText(STARTS([{ ...ALT(-1.4), n_starts: 2 }, ALT(0.7, 15)], { n_same_as_fit: 0 })),
    '0 of 3 scattered starts reached this solution; 3 found 2 DIFFERENT solutions with a lower χ²ᵣ. Your fit is unchanged.');
  for (const t of [_startsSummaryText(allThree), _startsSummaryText(STARTS([]))])
    assert.doesNotMatch(t, /best|verified|confirmed|correct|unique|global|reliable|trust/i);
  assert.strictEqual(_startsSummaryText(null), '');
  assert.strictEqual(_startsSummaryText({ ran: false, reason: 'single_component' }), '');
});

test('no alternative: one line, no table', () => {
  const env = makeEnv({ peaks: PEAKS(), starts: STARTS([]) });
  const h = env._startsPanelHtml(env.state.fitResult);
  assert.match(h, /3 of 3 scattered starts reached this solution/);
  assert.doesNotMatch(h, /<table|Other solutions found/);
  assert.strictEqual(env._startsPanelHtml({ starts: null }), '');
  assert.strictEqual(env._startsPanelHtml({ starts: { ran: false, reason: 'method' } }), '');
});

test('alternatives: "Your fit" first, own areas per component, the moved component named and coloured', () => {
  const env = makeEnv({ peaks: PEAKS(), starts: STARTS([ALT(-1.4), ALT(0.7, 15.0), ALT(0.2, 16.9)]) });
  const h = env._startsPanelHtml(env.state.fitResult);
  assert.match(h, /Other solutions found/);
  assert.ok(h.indexOf('Your fit') < h.indexOf('Alternative 1') && h.indexOf('Alternative 1') < h.indexOf('Alternative 2'));
  for (const name of ['>Graphite<br>', '>C-O<br>', '>sat<br>']) assert.ok(h.includes(name), name);
  assert.ok(h.includes('area % &middot; move'));
  assert.ok(h.includes('>24.0<br>') && h.includes('>49.0<br>'), 'the alternative shows its OWN area fractions');
  // Codex round 1: EVERY component's move from the student's start, not only the largest
  assert.match(h, /49\.0<br><span style="color:var\(--text2\)">\+0\.05 eV/, 'Graphite moved +0.05 eV in the alternative');
  assert.match(h, /24\.0<br><span style="color:var\(--red,#ef4444\)">−1\.40 eV/);
  assert.match(h, /27\.0<br><span style="color:var\(--text2\)">\+0\.00 eV/);
  assert.match(h, /color:var\(--red,#ef4444\)[^>]*>C-O −1\.40 eV/, '> 1 eV is red');
  assert.match(h, /color:var\(--amber,#f59e0b\)[^>]*>C-O \+0\.70 eV/, '0.5-1 eV is amber');
  assert.match(h, /color:var\(--text2\)[^>]*>C-O \+0\.20 eV/);
  assert.strictEqual((h.match(/useAlternative\(/g) || []).length, 3);
  assert.strictEqual((h.match(/previewAlternative\(/g) || []).length, 3);
  assert.doesNotMatch(h.replace(/data-xps-tip="[^"]*"/, ''), /best|verified|recommended/i);
});

test('RED band: applying asks first and NAMES the component and the distance', async () => {
  const env = makeEnv({ peaks: PEAKS(), starts: STARTS([ALT(-1.47)]), confirmAnswer: false });
  const before = JSON.stringify(env.state.peaks);
  await env.useAlternative(0);
  assert.deepStrictEqual(env.calls.confirm, ['This solution moves C-O by −1.47 eV from where you placed it. Apply?']);
  assert.strictEqual(JSON.stringify(env.state.peaks), before, 'declined: nothing changes');
  assert.deepStrictEqual(env.calls.runFit, []);
});

test('adoption never writes the live model itself: the alternative is only the START of a fit, and the choice rides along', async () => {
  const env = makeEnv({ peaks: PEAKS(), starts: STARTS([ALT(-1.47)]), confirmAnswer: true });
  const before = JSON.stringify(env.state.peaks);
  await env.useAlternative(0);
  assert.strictEqual(env.calls.confirm.length, 1);
  assert.strictEqual(env.calls.pushUndo, 0, 'runFit pushes the single undo entry, with the pre-apply model');
  assert.strictEqual(JSON.stringify(env.state.peaks), before, 'only a SUCCESSFUL fit may change the model');
  assert.strictEqual(env.calls.runFit.length, 1);
  const o = env.calls.runFit[0];
  assert.deepStrictEqual(o.chosenAlternative, { fromChi: 17.55, toChi: 12.3, shiftName: 'C-O', shiftEv: -1.47 });
  const co = o.startPeaks.find(p => p.id === 2);
  assert.ok(Math.abs(co.center - (286.41 - 1.47)) < 1e-9 && co.fwhm === 1.1 && co.glMix === 25);
  assert.notStrictEqual(o.startPeaks, env.state.peaks);
});

test('below the red band there is no dialog', async () => {
  for (const ev of [0.2, 0.7, -1.0]) {
    const env = makeEnv({ peaks: PEAKS(), starts: STARTS([ALT(ev)]) });
    await env.useAlternative(0);
    assert.deepStrictEqual(env.calls.confirm, [], String(ev));
    assert.strictEqual(env.calls.runFit.length, 1);
  }
});

test('a locked parameter is never moved by an alternative', async () => {
  const env = makeEnv({ peaks: PEAKS(), starts: STARTS([ALT(0.3)]) });
  await env.useAlternative(0);
  assert.strictEqual(env.calls.runFit[0].startPeaks.find(p => p.id === 1).center, 284.40, 'Graphite centre is locked (fixCenter)');
});

for (const [label, edit] of [
  ['a peak deleted', ps => ps.slice(0, 2)],
  ['a shape changed (GL -> DS) and the centre moved', ps => { ps[1].shape = 'DS'; ps[1].center = 290; return ps; }],
  ['a lock toggled', ps => { ps[1].fixCenter = true; return ps; }],
  ['a link added', ps => { ps[2].linked = 1; ps[2].linkOffset = 6.7; return ps; }],
  ['an undo that restored other values', ps => { ps[0].amplitude = 50000; return ps; }],
  ['an auto-fit asymmetry bound changed', ps => { ps[0]._afAsymMax = 0.8; return ps; }],
  ['the background type changed', (ps, env) => { env.ui.bgType = 'linear'; return ps; }],
  ['the background window moved', (ps, env) => { env.ui.bgEnd = '292.5'; return ps; }],
  ['endpoint averaging changed', (ps, env) => { env.ui.endpointAvg = '5'; return ps; }],
  ['the ROI changed', (ps, env) => { env.ui.roiMax = '293'; return ps; }],
  ['a manual anchor was added', (ps, env) => { env.anchors.push({ x: 288, y: 1200 }); return ps; }],
  ['the charge correction changed', (ps, env) => { env.state.ccShift = -4.6; return ps; }],
]) {
  test(`evidence is bound to the fitted model — ${label}: the panel says so and nothing can be applied`, async () => {
    const env = makeEnv({ peaks: PEAKS(), starts: STARTS([ALT(0.3)]) });
    env.state.peaks = edit(env.state.peaks, env);
    const h = env._startsPanelHtml(env.state.fitResult);
    assert.match(h, /model has changed since this fit/);
    assert.doesNotMatch(h, /<table|useAlternative|scattered starts reached/);
    await env.useAlternative(0);
    env.previewAlternative(0);
    assert.strictEqual(env.calls.runFit.length, 0);
    assert.strictEqual(env.preview(), null);
    assert.strictEqual(env.calls.notify.length, 2);
    assert.match(env.calls.notify[0][1], /model has changed since this fit/);
    assert.strictEqual(env._startsIfCurrent(env.state.fitResult, env._startsLiveKey()), null, 'saves and exports get nothing');
    assert.strictEqual(env._startsChosenText({ ...env.state.fitResult, chosenAlternative: { fromChi: 2, toChi: 1, shiftName: 'x', shiftEv: 0.1 } }), '');
  });
}

test('a cosmetic edit (name, colour, visibility) does not invalidate the evidence', () => {
  const env = makeEnv({ peaks: PEAKS(), starts: STARTS([ALT(0.3)]) });
  Object.assign(env.state.peaks[1], { name: 'C–O / C–N', color: '#123456', visible: false });
  assert.match(env._startsPanelHtml(env.state.fitResult), /Other solutions found/);
});

test('preview overlays a COPY and toggles off; the model is untouched', () => {
  const env = makeEnv({ peaks: PEAKS(), starts: STARTS([ALT(-1.4)]) });
  const before = JSON.stringify(env.state.peaks);
  env.previewAlternative(0);
  assert.strictEqual(env.preview().snapId, 'alt:0');
  assert.ok(Math.abs(env.preview().peaks.find(p => p.id === 2).center - 285.01) < 1e-9);
  assert.strictEqual(JSON.stringify(env.state.peaks), before);
  assert.strictEqual(env.calls.updatePlot, 1);
  env.previewAlternative(0);
  assert.strictEqual(env.preview(), null);
  // Codex round 2: an open preview must not survive its evidence
  env.previewAlternative(0);
  assert.strictEqual(env.preview().altKey, env.state.fitResult.startsModelKey);
  env._dropStaleAltPreview();
  assert.ok(env.preview(), 'still valid: kept');
  env.state.peaks[1].fwhm = 2.0;
  env._dropStaleAltPreview();
  assert.strictEqual(env.preview(), null, 'the model was edited: the overlay goes');
});

test('a record is keyed like the live tab (project save of a non-active tab)', () => {
  const env = makeEnv({ peaks: PEAKS(), starts: STARTS([]) });
  const rec = { peaks: env.state.peaks, ui: { ...env.ui, ccObs: '279.7', bgSubtractedView: true }, ccShift: -4.74, manualAnchors: [] };
  assert.strictEqual(env._startsRecordKey(rec), env._startsLiveKey(), 'charge-correction inputs and the view toggle are not fit context');
  assert.notStrictEqual(env._startsRecordKey({ ...rec, ui: { ...rec.ui, endpointAvg: 1 } }), env._startsLiveKey());
  assert.strictEqual(env._startsRecordKey({ ...rec, ui: { ...rec.ui, endpointAvg: 3 } }), env._startsLiveKey(), 'a number and its string are the same setting');
});

test('what is saved: the counts, never the alternatives\' parameter sets', () => {
  const { _startsForSave } = makeEnv({ peaks: PEAKS(), starts: STARTS([]) });
  const saved = _startsForSave(STARTS([ALT(-1.4), ALT(0.7, 15)], { n_not_better_elsewhere: 0 }));
  assert.deepStrictEqual(saved, { ran: true, n_run: 3, n_converged: 3, n_same_as_fit: 1, n_not_better_elsewhere: 0,
    n_in_alternatives: 2, n_alternatives: 2, best_alternative_chi2r: 12.3 });
  assert.ok(!JSON.stringify(saved).includes('components'));
  assert.deepStrictEqual(_startsForSave(saved), saved, 're-saving a loaded summary keeps it');
  assert.deepStrictEqual(_startsForSave({ ran: false, reason: 'method' }), { ran: false, reason: 'method' });
  assert.strictEqual(_startsForSave(null), null);
});

test('a loaded summary (no parameter sets) still renders its line and offers nothing to apply', async () => {
  const env = makeEnv({ peaks: PEAKS(), starts: { ran: true, n_run: 3, n_converged: 3, n_same_as_fit: 2, n_not_better_elsewhere: 0,
    n_in_alternatives: 1, n_alternatives: 1, best_alternative_chi2r: 12.3 } });
  const h = env._startsPanelHtml(env.state.fitResult);
  assert.match(h, /2 of 3 scattered starts reached this solution; 1 found a DIFFERENT solution/);
  assert.doesNotMatch(h, /<table/);
  await env.useAlternative(0);
  assert.strictEqual(env.calls.runFit.length, 0);
});

test('wiring: the trigger is decided with the other request inputs, BEFORE the first await', () => {
  const { _startsUnlinkedCount } = makeEnv({ peaks: PEAKS(), starts: STARTS([]) });
  assert.strictEqual(_startsUnlinkedCount(PEAKS()), 3);
  assert.strictEqual(_startsUnlinkedCount([{ id: 1 }, { id: 2, linked: 1 }]), 1);
  const runFit = extractFn('runFit');
  const decided = runFit.indexOf('const nStarts = _startsUnlinkedCount(startModel) >= 2 ? _STARTS_N : 0;');
  assert.ok(decided > 0);
  assert.ok(decided < runFit.indexOf('await uploadToBackend('), 'a tab switch during the upload must not turn the check off');
  assert.match(runFit, /n_starts: nStarts/);
  assert.doesNotMatch(runFit.slice(runFit.indexOf('await uploadToBackend(')), /_startsUnlinkedCount\(state\.peaks\)/);
  assert.match(runFit, /const startModel = opts\.startPeaks \|\| state\.peaks;\n\s*const peakSpecs = startModel\.map\(peakToBackendSpec\);/);
  assert.match(runFit, /startsModelKey: _startsLiveKey\(\),/);
  assert.ok(runFit.indexOf('applyBackendResult(backendResult);') < runFit.indexOf('startsModelKey: _startsLiveKey()'), 'the key describes the model AFTER the result was applied');
  const captured = runFit.indexOf('const ctxAtRequest = _startsLiveKey();');
  assert.ok(captured > 0 && captured < runFit.indexOf('await uploadToBackend('), 'context captured before the first await');
  assert.ok(runFit.indexOf('if (_startsLiveKey() !== ctxAtRequest)') < runFit.indexOf('applyBackendResult(backendResult);'), 'and checked before anything is applied');
  assert.match(runFit, /chosenAlternative: opts\.chosenAlternative \|\| null/);
  assert.match(extractFn('renderResults'), /_startsPanelHtml\(state\.fitResult\)/);
  assert.doesNotMatch(extractFn('_invalidateFittedY'), /starts/, 'validity is by key comparison: a rename (which calls this) must not delete evidence');
  assert.match(extractFn('updatePlot'), /_refreshStartsEvidence\(false\);/);
  assert.match(extractFn('toggleLock'), /_refreshStartsEvidence\(true\);/);
  assert.match(extractFn('toggleAllLocks'), /_refreshStartsEvidence\(true\);/);
  assert.match(runFit, /snapId\.startsWith\('alt:'\)\) _historyPreview = null;/, 'a successful fit clears an alternative overlay unconditionally');
  // Batch Fit and the local fallback never request it (local engine; starting point, not a result)
  assert.doesNotMatch(extractFn('runPropagation'), /n_starts/);
  assert.doesNotMatch(extractFn('runFitLocal'), /n_starts|_STARTS_N/);
});

test('persistence and export sites carry the summary', () => {
  // only evidence that still describes the saved model is written, with the key that binds it
  for (const fn of ['_doSaveFit', '_doSaveSpectrum']) {
    assert.match(extractFn(fn), /starts: _startsForSave\(_startsIfCurrent\(state\.fitResult, _startsLiveKey\(\)\)\),\n\s*startsModelKey: state\.fitResult\.startsModelKey \|\| null,/, fn);
  }
  assert.strictEqual((html.match(/starts: _startsForSave\(_startsIfCurrent\(t\.fitResult, _startsRecordKey\(t\)\)\)/g) || []).length, 1, 'project save (buildTabData)');
  assert.strictEqual((html.match(/starts: _startsForSave\(/g) || []).length, 3, 'exactly three save sites');
  assert.match(extractFn('_loadSpectrumFile'), /'caveat', 'starts', 'startsModelKey', 'chosenAlternative'\]/);
  const ex = extractFn('exportFitTable');
  assert.match(ex, /\['Scattered starts', _startsSummaryText\(_startsIfCurrent\(state\.fitResult, _startsLiveKey\(\)\)\)\]/);
  assert.match(ex, /# Scattered starts: \$\{_startsSummaryText\(_startsIfCurrent\(state\.fitResult, _startsLiveKey\(\)\)\)\}/);
  assert.match(ex, /\['Chosen alternative', _startsChosenText\(state\.fitResult\)\]/);
  assert.match(ex, /# Chosen alternative: \$\{_startsChosenText\(state\.fitResult\)\}/);
});


test('the tooltip reports what the starts found and claims nothing about the data', () => {
  const tip = constLine('_STARTS_TOOLTIP');
  assert.doesNotMatch(tip, /pin it down|proves?|guarantee|determined by the data|reliable|trust/i);
  assert.match(tip, /that is what those starts found, no more/);
  assert.match(tip, /A lower .* is not a better chemical model/);
});

test('the recorded adoption is worded once, for the exports', () => {
  const env = makeEnv({ peaks: PEAKS(), starts: STARTS([]) });
  env.state.fitResult.chosenAlternative = { fromChi: 35.772, toChi: 15.47, shiftName: 'Adventitious 2', shiftEv: -1.417 };
  assert.strictEqual(env._startsChosenText(env.state.fitResult),
    'this fit started from a solution chosen from the scattered starts (χ²ᵣ 35.77 → 15.47; largest move from the original start: Adventitious 2 −1.42 eV)');
  assert.strictEqual(env._startsChosenText({ starts: null }), '');
});
