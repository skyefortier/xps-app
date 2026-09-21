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

const FNS = ['_startsUnlinkedCount', '_startsForSave', '_startsSummaryText', '_startsPeakName', '_startsShiftHtml',
  '_startsPanelHtml', '_altPeaks', '_currentAlternative', 'previewAlternative', 'useAlternative', '_applyBackendParams'];
function makeEnv({ peaks, starts, confirmAnswer = true }) {
  const calls = { confirm: [], pushUndo: 0, runFit: [], notify: [], updatePlot: 0, renderPeakList: 0 };
  const state = { peaks, fitResult: { chiReduced: starts && starts.fit ? starts.fit.chi2r : 1, starts } };
  const src = [constLine('_STARTS_N'), constLine('_STARTS_SHIFT_AMBER_EV'), constLine('_STARTS_TOOLTIP'),
    'let _historyPreview = null;', ...FNS.map(extractFn)].join('\n');
  const factory = new Function('state', 'getPeak', '_escHtml', 'confirm', 'pushUndo', 'runFit', 'notify', 'updatePlot',
    'renderPeakList', '_updateLocalModelBanner', '_historyClearPreview',
    src + '\nreturn { ' + FNS.join(', ') + ', preview: () => _historyPreview, clear: () => { _historyPreview = null; } };');
  const api = factory(state, id => state.peaks.find(p => p.id === id || String(p.id) === String(id)),
    s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;'),
    msg => { calls.confirm.push(msg); return confirmAnswer; }, () => { calls.pushUndo++; },
    async o => { calls.runFit.push(o); }, (m, k) => calls.notify.push([k, m]), () => { calls.updatePlot++; },
    () => { calls.renderPeakList++; }, () => {}, () => { api.clear(); });
  return { ...api, state, calls };
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
  components: [comp(1, 49, 284.95, 0.55), comp(2, 24, 286.41 + shiftEv, shiftEv), comp(3, 27, 291.1, 0)] });

test('summary wording: counts, never certification', () => {
  const { _startsSummaryText } = makeEnv({ peaks: PEAKS(), starts: STARTS([]) });
  assert.strictEqual(_startsSummaryText(STARTS([])), '3 of 3 scattered starts reached this solution.');
  assert.strictEqual(_startsSummaryText(STARTS([], { n_same_as_fit: 2, n_not_better_elsewhere: 1, not_better_chi2r: [7.912] })),
    '2 of 3 scattered starts reached this solution; 1 ended in a solution that is not better (χ²ᵣ 7.91).');
  assert.strictEqual(_startsSummaryText(STARTS([], { n_converged: 2, n_same_as_fit: 2 })),
    '2 of 3 scattered starts reached this solution; 1 did not converge.');
  const withAlt = _startsSummaryText(STARTS([ALT(-1.4)]));
  assert.match(withAlt, /^2 of 3 scattered starts reached this solution; one start found a DIFFERENT solution with a lower χ²ᵣ\. Your fit is unchanged\.$/);
  for (const t of [withAlt, _startsSummaryText(STARTS([]))])
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
  for (const name of ['Graphite %', 'C-O %', 'sat %']) assert.ok(h.includes(name), name);
  assert.ok(h.includes('>24.0<') && h.includes('>49.0<'), 'the alternative shows its OWN area fractions');
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
  assert.strictEqual(env.calls.pushUndo, 0);
  assert.deepStrictEqual(env.calls.runFit, []);
});

test('RED band accepted: one undo entry, the solution becomes the START of an ordinary fit, and the choice is recorded', async () => {
  const env = makeEnv({ peaks: PEAKS(), starts: STARTS([ALT(-1.47)]), confirmAnswer: true });
  await env.useAlternative(0);
  assert.strictEqual(env.calls.confirm.length, 1);
  assert.strictEqual(env.calls.pushUndo, 1);
  assert.strictEqual(env.calls.runFit.length, 1);
  assert.strictEqual(env.calls.runFit[0].skipUndo, true, 'runFit must not push a second undo entry');
  assert.deepStrictEqual(env.calls.runFit[0].chosenAlternative, { fromChi: 17.55, toChi: 12.3, shiftName: 'C-O', shiftEv: -1.47 });
  const co = env.state.peaks.find(p => p.id === 2);
  assert.ok(Math.abs(co.center - (286.41 - 1.47)) < 1e-9 && co.fwhm === 1.1 && co.glMix === 25);
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
  assert.strictEqual(env.state.peaks.find(p => p.id === 1).center, 284.40, 'Graphite centre is locked (fixCenter)');
});

test('a model edited since the fit cannot be overwritten by stale alternatives', async () => {
  const peaks = PEAKS().slice(0, 2);                       // the student deleted a peak after fitting
  const env = makeEnv({ peaks, starts: STARTS([ALT(0.3)]) });
  await env.useAlternative(0);
  env.previewAlternative(0);
  assert.strictEqual(env.calls.runFit.length, 0);
  assert.strictEqual(env.calls.pushUndo, 0);
  assert.strictEqual(env.preview(), null);
  assert.strictEqual(env.calls.notify.length, 2);
  assert.match(env.calls.notify[0][1], /model has changed since this fit/);
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
});

test('what is saved: the counts, never the alternatives\' parameter sets', () => {
  const { _startsForSave } = makeEnv({ peaks: PEAKS(), starts: STARTS([]) });
  const saved = _startsForSave(STARTS([ALT(-1.4), ALT(0.7, 15)], { n_not_better_elsewhere: 0 }));
  assert.deepStrictEqual(saved, { ran: true, n_run: 3, n_converged: 3, n_same_as_fit: 1, n_not_better_elsewhere: 0,
    n_alternatives: 2, best_alternative_chi2r: 12.3 });
  assert.ok(!JSON.stringify(saved).includes('components'));
  assert.deepStrictEqual(_startsForSave(saved), saved, 're-saving a loaded summary keeps it');
  assert.deepStrictEqual(_startsForSave({ ran: false, reason: 'method' }), { ran: false, reason: 'method' });
  assert.strictEqual(_startsForSave(null), null);
});

test('a loaded summary (no parameter sets) still renders its line and offers nothing to apply', async () => {
  const env = makeEnv({ peaks: PEAKS(), starts: { ran: true, n_run: 3, n_converged: 3, n_same_as_fit: 2, n_not_better_elsewhere: 0,
    n_alternatives: 1, best_alternative_chi2r: 12.3 } });
  const h = env._startsPanelHtml(env.state.fitResult);
  assert.match(h, /2 of 3 scattered starts reached this solution; one start found a DIFFERENT solution/);
  assert.doesNotMatch(h, /<table/);
  await env.useAlternative(0);
  assert.strictEqual(env.calls.runFit.length, 0);
});

test('wiring: runFit asks for the check only with two or more unlinked components', () => {
  const { _startsUnlinkedCount } = makeEnv({ peaks: PEAKS(), starts: STARTS([]) });
  assert.strictEqual(_startsUnlinkedCount(PEAKS()), 3);
  assert.strictEqual(_startsUnlinkedCount([{ id: 1 }, { id: 2, linked: 1 }]), 1);
  const runFit = extractFn('runFit');
  assert.match(runFit, /n_starts: _startsUnlinkedCount\(state\.peaks\) >= 2 \? _STARTS_N : 0/);
  assert.match(runFit, /if \(!opts\.skipUndo\) pushUndo\(\);/);
  assert.match(runFit, /starts: backendResult\.starts \|\| null,/);
  assert.match(runFit, /chosenAlternative: opts\.chosenAlternative \|\| null/);
  assert.match(extractFn('renderResults'), /_startsPanelHtml\(state\.fitResult\)/);
  // Batch Fit and the local fallback never request it (local engine; starting point, not a result)
  assert.doesNotMatch(extractFn('runPropagation'), /n_starts/);
  assert.doesNotMatch(extractFn('runFitLocal'), /n_starts|_STARTS_N/);
});

test('persistence and export sites carry the summary', () => {
  for (const fn of ['_doSaveFit', '_doSaveSpectrum'])
    assert.match(extractFn(fn), /starts: _startsForSave\(state\.fitResult\.starts\)/, fn);
  assert.strictEqual((html.match(/starts: _startsForSave\(t\.fitResult\.starts\)/g) || []).length, 1, 'project save (buildTabData)');
  assert.strictEqual((html.match(/starts: _startsForSave\(/g) || []).length, 3, 'exactly three save sites');
  assert.match(extractFn('_loadSpectrumFile'), /'caveat', 'starts', 'chosenAlternative'\]/);
  const ex = extractFn('exportFitTable');
  assert.match(ex, /\['Scattered starts', _startsSummaryText\(state\.fitResult\.starts\)\]/);
  assert.match(ex, /# Scattered starts: \$\{_startsSummaryText\(state\.fitResult\.starts\)\}/);
});
