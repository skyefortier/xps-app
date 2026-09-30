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
    const _startsPanelHtml = () => '', _certificateNoticeHtml = () => '';
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
  assert.match(up, /_refreshStartsEvidence\(false, true\)/, 'every repaint reaches the refresh');
  assert.match(extractFn('_refreshStartsEvidence'), /^function _refreshStartsEvidence[^\n]*\n(\s*\/\/[^\n]*\n)*\s*_refreshStatsState\(\);/, 'first thing, for EVERY caller (lock toggles, Lock All, updatePlot)');
  for (const fn of ['toggleLock', 'toggleAllLocks']) assert.match(extractFn(fn), /_refreshStartsEvidence\(true\);/, fn + ' reaches the statistics refresh');
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
    const _startsSummaryText = () => '', _startsIfCurrent = () => null, _startsChosenText = () => '', _certificateMoveText = () => '';
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

// Unit 2: Auto-Fit starts the fit and polls for it (_serverFitJob). Each
// sandbox scripts the single /api/fit reply it always did; pollify serves it
// as a finished job, and runs the poll loop's short waits at once (the
// 2-minute Auto-Fit timer is left pending, as before).
const POLL_SRC = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
  'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap(); let _fitSpinnerOp = null;', ...['_cancelFitJob', '_fitHttpError', '_newFitOp', '_installFitOp', '_claimFitOp', '_fitOpOutdated', '_fitOpCurrent', '_hideFitSpinnerFor', '_serverFitJob'].map(extractFn)].join('\n');
function pollify(deps) {
  const inner = deps.fetch;
  let reply = null;
  deps.fetch = async (url, init) => {
    if (url === '/api/fit/start') {
      const r = await inner('/api/fit', init);
      if (r && r.ok === false) return r;
      reply = r;
      return { ok: true, status: 202, text: async () => JSON.stringify({ job_id: 'job-1' }) };
    }
    if (url.startsWith('/api/fit/progress/')) return { ok: true, status: 200, text: async () => '{"status": "done", "result": ' + (await reply.text()) + '}' };
    if (url.startsWith('/api/fit/cancel/')) return { ok: true, status: 200, json: async () => ({}) };
    return inner(url, init);
  };
  deps.setTimeout = (f, ms) => { if (!(ms >= 60000)) f(); return 1; };
  deps.DOMException = class extends Error { constructor(m, n) { super(m); this.name = n; } };
  return deps;
}

// ── Codex round 1 ───────────────────────────────────────────────────────────
function keyFns() {
  const src = lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n')
    + '\n' + ['_startsModelKey', '_fitKeyCanon', '_sameFitKey', '_statsState'].map(extractFn).join('\n');
  return new Function(src + '\nreturn { _startsModelKey, _sameFitKey, _statsState };')();
}

test('an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not', () => {
  const k = keyFns();
  const peaks = [{ id: 1, shape: 'GL', center: 284.5, fwhm: 1, amplitude: 10 }];
  const ui = { bgType: 'shirley', bgStart: '295', bgEnd: '280', shirleyIter: '10', endpointAvg: '3', roiMin: '280', roiMax: '295' };
  const a = k._startsModelKey(peaks, ui, 0, []);
  assert.ok(k._sameFitKey(a, k._startsModelKey(peaks, { ...ui, roiMin: '280.0', roiMax: '295.00' }, 0, [])), 'same data, same request');
  assert.ok(!k._sameFitKey(a, k._startsModelKey(peaks, { ...ui, roiMin: '280.5' }, 0, [])), 'a real ROI change');
  assert.ok(!k._sameFitKey(a, k._startsModelKey(peaks, { ...ui, bgType: 'linear' }, 0, [])), 'a background change');
  assert.ok(!k._sameFitKey(a, k._startsModelKey(peaks, { ...ui, roiMin: '' }, 0, [])), 'an emptied field is not "0"');
  assert.strictEqual(k._statsState({ startsModelKey: a }, k._startsModelKey(peaks, { ...ui, roiMin: '280.0' }, 0, [])), 'current');
  // Codex round 2: each field is read as ITS READERS read it — the counts through parseInt
  for (const [field, fitted, typed, same] of [
    ['endpointAvg', '30', '3e1', false],     // Number('3e1') = 30, parseInt('3e1') = 3: a different background
    ['endpointAvg', '10', '1e1', false],
    ['shirleyIter', '5', '5.0', true],       // parseInt: 5 either way
    ['shirleyIter', '5', '5.9', true],       // parseInt reads 5 — the same fit
    ['endpointAvg', '3', '03', true],
    ['roiMin', '280', '2.8e2', true],        // parseFloat reads 280 either way
    ['roiMin', '280', '280abc', true],       // parseFloat reads 280 (what getROIData selects)
    ['bgStart', '295', '295.5', false],
  ]) {
    const fk = k._startsModelKey(peaks, { ...ui, [field]: fitted }, 0, []);
    const lk = k._startsModelKey(peaks, { ...ui, [field]: typed }, 0, []);
    const pf = /Iter|Avg/.test(field) ? parseInt : parseFloat;
    assert.strictEqual(pf(fitted) === pf(typed), same, 'fixture: the reader agrees with the expectation');
    assert.strictEqual(k._sameFitKey(fk, lk), same, `${field} ${fitted} vs ${typed}`);
  }
  assert.ok(!k._sameFitKey(null, null) && !k._sameFitKey(a, null), 'no key never matches');
  assert.ok(!k._sameFitKey('not json', 'not json ') && k._sameFitKey('not json', 'not json'));
});

test('Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone', () => {
  const src = [...STATE_CONSTS.map(constLine), ...['_fitKeyCanon', '_sameFitKey', ...STATE_FNS].map(extractFn), extractFn('_refreshStatsState')].join('\n');
  const doc = makeDoc();
  const env = { renders: 0 };
  const state = { fitResult: null };
  const refresh = new Function('document', 'state', 'env', `
    const _startsLiveKey = () => 'K', _startsRecordKey = t => t.key;
    const renderResults = () => { env.renders++; document.getElementById('results-area').setAttribute('data-stats-state', _statsLiveState()); };
    const _applyStatDisplay = () => {}, _updateRFactorUI = () => {};
    ${src}
    return _refreshStatsState;`)(doc, state, env);
  refresh();
  assert.strictEqual(env.renders, 0, 'fresh page: nothing rendered yet, nothing to clear');
  doc.els['results-area'].setAttribute('data-stats-state', 'current');   // a fit was shown
  refresh();
  assert.strictEqual(env.renders, 1, 'the shown result was cleared: back to the empty state');
  refresh();
  assert.strictEqual(env.renders, 1);
});

test('Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies', async () => {
  const constants = lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n');
  const run = async (editDuringUpload) => {
    const state = { peaks: [], ccShift: 0, rawBE: [285, 284.5, 284], rawIntensity: [10, 20, 10] };
    const dom = {};
    const document = { getElementById: id => (dom[id] ??= { value: ({ 'bg-type': 'none', 'bg-start': '285', 'bg-end': '284', 'bg-endpoint-avg': '3', 'fit-method': 'leastsq' })[id] || '', style: {}, textContent: '', setAttribute() {}, classList: { add() {}, remove() {} } }), querySelector: () => ({}) };
    const tab = { id: 1 };
    const out = { restored: false, applied: 0, notes: [] };
    const tabManager = { activeId: 1, _getTab: () => tab, _captureUI: () => ({ bgType: document.getElementById('bg-type').value, roiMin: '284', roiMax: '285' }), _syncActiveToRecord() {} };
    const deps = { state, document, tabManager, notify: (m, k) => out.notes.push([m, k]), _opOwner: () => tab, _ownerActive: () => true, isC1sTab: () => true,
      _autoFitSnapshot: () => ({}), _autoFitRestore: () => { out.restored = true; }, _showAutoFitConfirmModal: async () => true,
      getROIData: () => ({ be: state.rawBE, inten: state.rawIntensity }), computeBackground: be => be.map(() => 0),
      findGraphiteRawBE: () => 284.5, assessLowBERegion: () => ({}), pushUndo() {}, updateChargeCorrection() {},
      buildAutoFitModel: () => [{ id: 1, name: 'Graphite', shape: 'Gaussian', center: 284.5, fwhm: 1, amplitude: 20 }],
      renderPeakList() {}, _showFitSpinner() {}, _hideFitSpinner() {}, AbortController, setTimeout: () => 1, clearTimeout() {},
      peakToBackendSpec: p => ({ ...p }), _getManualAnchors: () => [],
      uploadToBackend: async () => { if (editDuringUpload) document.getElementById('bg-type').value = 'linear'; return 'sid'; },
      fetch: async () => ({ text: async () => JSON.stringify({ success: true, statistics: { reduced_chi_square: 1 }, fitted_y: [10, 20, 10], residuals: [0, 0, 0] }) }),
      applyBackendResult: () => { out.applied++; }, applyAutoFitResult: () => true };
    const src = constants + '\n' + ['runAutoFitC1sGraphite', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
    await new Function(...Object.keys(pollify(deps)), src + '\n' + POLL_SRC + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
    return out;
  };
  const edited = await run(true);
  assert.strictEqual(edited.applied, 0, 'nothing applied over the edited model');
  assert.strictEqual(edited.restored, true, 'rolled back');
  assert.ok(edited.notes.some(([m, k]) => k === 'amber' && /edited while it was running/.test(m)), JSON.stringify(edited.notes));
  const clean = await run(false);
  assert.strictEqual(clean.applied, 1, 'an unedited run is applied as before');
  assert.strictEqual(clean.restored, false);
});

test('closing the last tab clears the Results panel, header and status statistics too', () => {
  const close = html.slice(html.indexOf('  closeTab(id) {'));
  const last = close.slice(close.indexOf('if (this.tabs.length === 0) {'));
  assert.ok(/renderResults\(\)/.test(last.slice(0, last.indexOf('return;'))), 'the no-result render runs before the early return');
});

test('reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model', () => {
  const load = extractFn('_loadSpectrumFile');
  assert.match(load, /if \(data\.fittedY && data\.statistics\.statisticsState !== 'stale'\) fr\.fittedY = data\.fittedY;/);
  assert.match(load, /if \(data\.statistics\.rFactor && data\.statistics\.statisticsState !== 'stale'\) fr\.rFactor = data\.statistics\.rFactor;/);
  assert.match(html, /state\.fitResult\.rFactor == null && _statsLiveState\(\) !== 'stale'\) \{\s*state\.fitResult\.rFactor = _computeRFactor/, 'tab activation');
  assert.match(extractFn('_doSaveProject'), /rFactor: t\.fitResult\.rFactor \|\| null/, 'project saves keep the fit\'s own R');
  assert.match(extractFn('_doSaveSpectrum'), /rFactor: state\.fitResult\.rFactor \|\| null/, 'spectrum saves keep it too');
});

test('F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back', async () => {
  const constants = lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n');
  const state = { peaks: [], ccShift: 0, rawBE: [285, 284.5, 284], rawIntensity: [10, 20, 10] };
  const dom = {};
  const document = { getElementById: id => (dom[id] ??= { value: ({ 'bg-type': 'none', 'bg-start': '285', 'bg-end': '284', 'bg-endpoint-avg': '3', 'fit-method': 'leastsq' })[id] || '', style: {}, textContent: '', setAttribute() {}, classList: { add() {}, remove() {} } }), querySelector: () => ({}) };
  const tab = { id: 1 };
  const out = { restored: false, applied: 0, notes: [] };
  const deps = { state, document, tabManager: { activeId: 1, _getTab: () => tab, _captureUI: () => ({ bgType: 'none' }), _syncActiveToRecord() {} },
    notify: (m, k) => out.notes.push([m, k]), _opOwner: () => tab, _ownerActive: () => true, isC1sTab: () => true,
    _autoFitSnapshot: () => ({}), _autoFitRestore: () => { out.restored = true; }, _showAutoFitConfirmModal: async () => true,
    getROIData: () => ({ be: state.rawBE, inten: state.rawIntensity }), computeBackground: be => be.map(() => 0),
    findGraphiteRawBE: () => 284.5, assessLowBERegion: () => ({}), pushUndo() {}, updateChargeCorrection() {},
    buildAutoFitModel: () => [{ id: 1, name: 'Graphite', shape: 'Gaussian', center: 284.5, fwhm: 1, amplitude: 20 }],
    renderPeakList() {}, _showFitSpinner() {}, _hideFitSpinner() {}, AbortController, setTimeout: () => 1, clearTimeout() {},
    peakToBackendSpec: p => ({ ...p }), _getManualAnchors: () => [], uploadToBackend: async () => 'sid',
    fetch: async () => ({ text: async () => '{"success": true, "statistics": {"reduced_chi_square": NaN}}' }),
    applyBackendResult: () => { out.applied++; }, applyAutoFitResult: () => true, console: { warn() {} } };
  const src = constants + '\n' + ['runAutoFitC1sGraphite', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
  await new Function(...Object.keys(pollify(deps)), src + '\n' + POLL_SRC + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
  assert.strictEqual(out.applied, 0);
  assert.strictEqual(out.restored, true);
  assert.ok(out.notes.some(([m, k]) => k === 'red' && /^Auto-fit failed: .*non-finite number/.test(m)), JSON.stringify(out.notes));
});

for (const [label, reply, expect] of [
  ['a Cloudflare 524 (plain-text body)', { ok: false, status: 524, json: async () => { throw new SyntaxError('error code: 524'); }, text: async () => 'error code: 524' }, /^Auto-fit failed: Fit request failed \(HTTP 524\)\.$/],
  ['a 500 with a JSON error', { ok: false, status: 500, json: async () => ({ error: 'Internal fitting error' }) }, /^Auto-fit failed: Internal fitting error$/],
]) test(`F2: Auto-Fit on ${label} is a failed request with its status, never "could not be read"`, async () => {
  const constants = lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n');
  const state = { peaks: [], ccShift: 0, rawBE: [285, 284.5, 284], rawIntensity: [10, 20, 10] };
  const dom = {};
  const document = { getElementById: id => (dom[id] ??= { value: ({ 'bg-type': 'none', 'bg-start': '285', 'bg-end': '284', 'bg-endpoint-avg': '3', 'fit-method': 'leastsq' })[id] || '', style: {}, textContent: '', setAttribute() {}, classList: { add() {}, remove() {} } }), querySelector: () => ({}) };
  const tab = { id: 1 };
  const out = { restored: false, applied: 0, notes: [] };
  const deps = { state, document, tabManager: { activeId: 1, _getTab: () => tab, _captureUI: () => ({ bgType: 'none' }), _syncActiveToRecord() {} },
    notify: (m, k) => out.notes.push([m, k]), _opOwner: () => tab, _ownerActive: () => true, isC1sTab: () => true,
    _autoFitSnapshot: () => ({}), _autoFitRestore: () => { out.restored = true; }, _showAutoFitConfirmModal: async () => true,
    getROIData: () => ({ be: state.rawBE, inten: state.rawIntensity }), computeBackground: be => be.map(() => 0),
    findGraphiteRawBE: () => 284.5, assessLowBERegion: () => ({}), pushUndo() {}, updateChargeCorrection() {},
    buildAutoFitModel: () => [{ id: 1, name: 'Graphite', shape: 'Gaussian', center: 284.5, fwhm: 1, amplitude: 20 }],
    renderPeakList() {}, _showFitSpinner() {}, _hideFitSpinner() {}, AbortController, setTimeout: () => 1, clearTimeout() {},
    peakToBackendSpec: p => ({ ...p }), _getManualAnchors: () => [], uploadToBackend: async () => 'sid',
    fetch: async () => reply,
    applyBackendResult: () => { out.applied++; }, applyAutoFitResult: () => true, console: { warn() {} } };
  const src = constants + '\n' + ['runAutoFitC1sGraphite', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
  await new Function(...Object.keys(pollify(deps)), src + '\n' + POLL_SRC + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
  assert.strictEqual(out.applied, 0);
  assert.strictEqual(out.restored, true);
  assert.ok(out.notes.some(([m, k]) => k === 'red' && expect.test(m)), JSON.stringify(out.notes));
  assert.ok(!out.notes.some(([m]) => /could not be read/.test(m)));
});
