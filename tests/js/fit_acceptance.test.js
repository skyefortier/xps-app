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

function makeEnv({ fetchImpl, uploadImpl }) {
  const dom = {};
  const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, disabled: false,
    setAttribute() {}, removeAttribute() {}, classList: { add(c) { this._c = c; }, remove() { this._c = null; }, contains() { return false; }, _c: null } });
  const document = { getElementById: el, querySelector: () => el('.btn-green'), querySelectorAll: () => [] };
  const be = Array.from({ length: 50 }, (_, i) => 280 + 0.2 * i);
  const state = { rawBE: be.slice(), rawIntensity: be.map(() => 100), ccShift: 0, fitResult: { marker: 'previous' },
    peaks: [{ id: 1, name: 'p', shape: 'Gaussian', center: 285, fwhm: 1.2, amplitude: 50, glMix: 50, asymmetry: 0 }] };
  const owner = { id: 7 };
  const calls = { notify: [], local: 0, applied: 0 };
  const src = ['runFit', '_bgWindowIndices', '_arrMin', '_arrMax'].map(extractFn).join('\n');
  const factory = new Function('document', 'state', 'fetch', 'uploadToBackend', 'notify', 'pushUndo', '_showFitSpinner', '_hideFitSpinner',
    '_opOwner', '_ownerActive', 'getROIData', 'computeBackground', 'peakToBackendSpec', '_getManualAnchors', 'applyBackendResult',
    '_computeRFactor', '_CHISQ_TOOLTIP', '_updateRFactorUI', '_updateROIDisplay', 'renderPeakList', 'updatePlot', 'renderResults',
    '_autoSnapshot', 'runFitLocal', '_snapshotSuppressed', 'console', '_applyStatDisplay', '_activeTab',
    src + '\nreturn { runFit };');
  const noop = () => {};
  const { runFit } = factory(document, state, fetchImpl, uploadImpl || (async () => 'sid'), (msg, kind) => calls.notify.push({ msg, kind }),
    noop, noop, noop, () => owner, o => o === owner, () => ({ be: state.rawBE.slice(), inten: state.rawIntensity.slice() }),
    b => b.map(() => 0), p => ({ id: p.id, shape: 'gaussian' }), () => [], () => { calls.applied++; },
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
  const src = ['runFit', '_bgWindowIndices', '_arrMin', '_arrMax'].map(extractFn).join('\n');
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
  assert.match(load, /\['engine', 'objective', 'weighting', 'status', 'caveat'\]/);
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
  assert.match(fig, /\\u03c7\\u00b2_r \(local fit, not reportable\)/, 'figure annotation designates a weighted local chi-square');
  // fit-history rows
  const hist = grab('function _renderHistoryList(', 3000);
  assert.match(hist, /_fitStatLabel\(/, 'history rows must label the statistic by engine');
  // tab activation tooltip
  const act = grab("// Update chi-squared display for this tab's fit result", 300);
  assert.match(act, /_applyStatDisplay\(state\.fitResult\)/, 'tab activation refreshes the whole statistic display');
});

test('uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure', async () => {
  const src = extractFn('uploadToBackend');
  const make = fetchImpl => new Function('fetch', 'FormData', 'Blob', src + '\nreturn uploadToBackend;')(fetchImpl, class { append() {} }, class {});
  await assert.rejects(make(async () => ({ ok: true, status: 200, json: async () => null }))([1], [1]), e => e.serverError === true);
  await assert.rejects(make(async () => ({ ok: true, status: 200, json: async () => 'nope' }))([1], [1]), e => e.serverError === true);
});

test('a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown', () => {
  const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
  // Results panel banner, keyed on the statistic identity
  const rr = grab('function renderResults()', 6000);
  assert.match(rr, /starting point/i, 'results panel must say the local result is a starting point');
  assert.match(rr, /Run Fit/, 'results panel must tell the user to press Run Fit');
  // batch summary rows
  const rp = grab('async function runPropagation', 9000);
  assert.match(rp, /starting point/i, 'batch summary must say converged rows are starting points');
  // table exports carry the warning
  const ex = grab('function exportFitTable(fmt)', 6000);
  assert.match(ex, /_localFitCaveat\(state\.fitResult\)/, 'CSV/XLSX export must carry the designation text for a local result');
  // figure annotation
  const fig = grab('function exportFigure()', 60000);
  assert.match(fig, /local fit, not reportable/i, 'figure annotation must say not reportable');
  // local-fit overlay
  assert.match(html, /id="localfit-warn-overlay"[\s\S]{0,1500}starting point/i, 'overlay must say starting point');
});

// ── Codex round-7: the starting-point designation at every site, behaviourally ──
test('starting-point helpers: keyed on the persisted objective, weighted results untouched', () => {
  const src = ['_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_localFitCaveat', '_fitStatusText'].map(extractFn).join('\n');
  const constLine = [html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n')]; assert.ok(constLine[0], '_LOCAL_FIT_CAVEAT constants');
  const h = new Function(constLine[0] + '\n' + src + '\nreturn { _fitStatLabel, _isLocalFit, _localFitCaveat, _fitStatusText };')();
  const local = { objective: 'unweighted_residual_variance', chiReduced: 34523.31 };
  const reloaded = { objective: 'unweighted_residual_variance', chiReduced: 1.5 };   // engine field absent, as older saves may be
  const weighted = { chiReduced: 4.97 };
  assert.equal(h._isLocalFit(local), true); assert.equal(h._isLocalFit(reloaded), true); assert.equal(h._isLocalFit(weighted), false);
  assert.match(h._localFitCaveat(local), /starting point, not a reportable result/i);
  assert.equal(h._localFitCaveat(weighted), '');
  assert.match(h._fitStatusText(local), /^Residual variance = 34523\.31 \(starting point\)$/);
  assert.match(h._fitStatusText(weighted), /^χ²ᵣ = 4\.97$/);
});

test('Quantify shows the starting-point banner for a local result and not for a weighted one', () => {
  const src = ['renderQuantify', '_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_localFitCaveat'].map(extractFn).join('\n');
  const constLine = html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n');
  const rsf = html.match(/^const SCOFIELD_RSF = \{[\s\S]*?^\};/m); assert.ok(rsf, 'SCOFIELD_RSF table');
  const run = (fitResult) => {
    const el = { innerHTML: '', _rsfSource: 'scofield' };
    const document = { getElementById: () => el, querySelectorAll: () => [] };
    const state = { fitResult, peaks: [{ id: 1, name: 'C 1s', shape: 'Gaussian', center: 284.8, fwhm: 1, amplitude: 10, rsfKey: 'C 1s' }] };
    new Function('document', 'state', '_escHtml', '_detectPeakRSF', 'recalcQuantify', constLine + '\n' + rsf[0] + '\n' + src + '\nrenderQuantify([100], 100);')(
      document, state, s => String(s), () => ({ key: 'C 1s', rsf: 1 }), () => {});
    return el.innerHTML;
  };
  assert.match(run({ objective: 'unweighted_residual_variance', chiReduced: 3e4 }), /starting point, not a reportable result/i);
  assert.doesNotMatch(run({ chiReduced: 2.0 }), /starting point/i);
});

test('every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels', () => {
  const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
  assert.match(grab('function exportResults()', 2500), /_LOCAL_FIT_CAVEAT|_localFitCaveat\(/, 'TSV export');
  assert.match(grab('function _doSaveSpectrum()', 2500), /caveat: _localFitCaveat\(state\.fitResult\) \|\| state\.fitResult\.caveat/, 'spectrum save persists caveat');
  assert.match(grab('function _doSaveSpectrum()', 2500), /reportable: _isLocalFit\(state\.fitResult\) \? false : \(state\.fitResult\.reportable/, 'spectrum save persists reportable');
  assert.match(grab('const buildTabData = (t) =>', 3500), /caveat: _localFitCaveat\(t\.fitResult\) \|\| t\.fitResult\.caveat/, 'project save persists caveat');
  assert.match(grab('function _loadSpectrumFile(', 6000), /'caveat'/, 'spectrum load restores caveat');
  assert.match(grab("// Update chi-squared display for this tab's fit result", 300), /_applyStatDisplay\(/, 'tab activation');
  assert.match(html, /id="sb-chi-caption"/, 'status-bar caption element');
  assert.match(grab('function _renderHistoryList(', 3000), /starting point/, 'history rows');
  assert.match(grab("label: _isLocalModel() ? 'Fit (local, starting point)' : 'Fit'", 100), /Fit \(local/, 'chart envelope label');
  const fig = grab('function exportFigure()', 60000);
  assert.match(fig, /label: _isLocalModel\(\) \? 'Fit \(local, starting point\)' : 'Fit'/, 'figure legend label');
  // the local fit result itself declares it
  const rfl = grab('function runFitLocal(', 20000);
  assert.match(rfl, /reportable: false, caveat: _LOCAL_FIT_CAVEAT/, 'runFitLocal marks its result');
});

// ── Codex round-8: stack/preview labels, save-time normalisation, auto-fit caption ──
test('project save derives the designation from the objective for an older local result lacking the new fields', () => {
  const start = html.indexOf('const buildTabData = (t) =>'); assert.ok(start > 0);
  let depth = 0, seen = false, end = -1;
  for (let i = start; i < html.length; i++) { const ch = html[i]; if (ch === '{') { depth++; seen = true; } else if (ch === '}') { depth--; if (seen && depth === 0) { end = i + 1; break; } } }
  const src = html.slice(start, end) + ';';
  const constLine = html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n');
  const helpers = ['_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_localFitCaveat'].map(extractFn).join('\n');
  const build = new Function('RefCore', '_roundBE', '_roundIntensity', constLine + '\n' + helpers + '\n' + src + '\nreturn buildTabData;')(
    { serializeRefOverlays: () => null }, a => a, a => a);
  const older = { id: 1, name: 't', rawBE: [1, 2], rawIntensity: [1, 1], ccShift: 0, peaks: [], nextId: 1, ui: {},
    fitResult: { chi: 1, chiReduced: 1e4, rmse: 100, objective: 'unweighted_residual_variance', be: [1, 2], bgIntensity: [0, 0], bgSubtracted: [1, 1] } };
  const rec = build(older);
  assert.strictEqual(rec.fitResult.reportable, false);
  assert.match(rec.fitResult.caveat, /starting point, not a reportable result/i);
  const weighted = { ...older, fitResult: { chi: 1, chiReduced: 2, rmse: 100, be: [1, 2], bgIntensity: [0, 0], bgSubtracted: [1, 1] } };
  assert.strictEqual(build(weighted).fitResult.reportable, null);
  assert.strictEqual(build(weighted).fitResult.caveat, null);
});

test('stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately', () => {
  const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
  assert.match(html, /_isLocalFit\(src\.fitResult\) \? ' \(fit: local, starting point\)' : ' \(fit\)'/, 'stack envelope dataset label');
  assert.match(html, /local fit: starting point/, 'stack legend row name');
  assert.match(html, /label: _isLocalFit\(_historyPreview\.fitResult\) \? 'Preview \(local, starting point\)' : 'Preview'/, 'history preview label');
  assert.match(grab('function applyAutoFitResult(', 12000), /_applyStatDisplay\(state\.fitResult\)/, 'auto-fit refreshes the statistic display');
  assert.match(grab('function renderResults()', 800), /_applyStatDisplay\(state\.fitResult\)/, 'renderResults refreshes the statistic display on every result change');
  const spec = grab('function _doSaveSpectrum()', 3000);
  assert.match(spec, /reportable: _isLocalFit\(state\.fitResult\) \? false/, 'spectrum save derives reportable');
  assert.match(spec, /caveat: _localFitCaveat\(state\.fitResult\)/, 'spectrum save derives caveat');
  const ex = grab('function exportFitTable(fmt)', 6000);
  const xlsxPart = ex.slice(ex.indexOf("if (fmt === 'xlsx')"), ex.indexOf('} else {'));
  const csvPart = ex.slice(ex.indexOf('} else {'));
  assert.match(xlsxPart, /WARNING/, 'XLSX warning row');
  assert.match(csvPart, /# WARNING/, 'CSV warning line');
});


// ── Codex round-9: header, tooltip, caption and value move as one unit ──
test('_applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none', () => {
  const src = ['_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay'].map(extractFn).join('\n');
  const constLine = html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n');
  const dom = {}; const el = id => (dom[id] ||= { textContent: '', innerHTML: '', tip: null, setAttribute(k, v) { this.tip = v; }, removeAttribute() { this.tip = null; } });
  const apply = new Function('document', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_updateLocalModelBanner', constLine + '\n' + src + '\nreturn _applyStatDisplay;')({ getElementById: el }, 'CHI', 'LOCAL', () => {});
  apply({ objective: 'unweighted_residual_variance', chiReduced: 12345 });
  assert.equal(dom['fit-quality'].textContent, 'Residual variance = 12345.00 (starting point)');
  assert.equal(dom['fit-quality'].tip, 'LOCAL'); assert.match(dom['sb-chi-caption'].innerHTML, /starting point/); assert.equal(dom['sb-chi'].textContent, '12345.000');
  apply({ chiReduced: 1.25 });
  assert.equal(dom['fit-quality'].textContent, '\u03c7\u00b2\u1d63 = 1.25'); assert.equal(dom['fit-quality'].tip, 'CHI');
  assert.doesNotMatch(dom['sb-chi-caption'].innerHTML, /starting point/); assert.equal(dom['sb-chi'].textContent, '1.250');
  apply(null);
  assert.equal(dom['sb-chi'].textContent, '\u2014'); assert.equal(dom['fit-quality'].tip, null);
});

test('history preview glow is keyed on the dataset flag, not the label text', () => {
  assert.match(html, /_historyPreview: true/, 'preview dataset carries the flag');
  assert.doesNotMatch(html, /\?\.label !== 'Preview'/, 'plugin no longer compares the label text');
  assert.equal((html.match(/\?\._historyPreview\) return;/g) || []).length, 2, 'both glow hooks key on the flag');
});

// ── Codex round-10: spectrum reload re-renders Results; Save Fit carries the designation; clear-state asserts all four ──
test('spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation', () => {
  const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
  const load = grab('function _loadSpectrumFile(', 7000);
  const tail = load.slice(load.indexOf("notify('Spectrum loaded as new tab") - 200, load.indexOf("notify('Spectrum loaded as new tab"));
  assert.match(tail, /renderResults\(\)/, 'Results (and the statistic display) must be rendered after the restored result is installed');
  const save = grab('function _doSaveFit()', 3000);
  assert.match(save, /fitStatistics: state\.fitResult \? \{/, 'Save Fit writes a fitStatistics block');
  assert.match(save, /caveat: _localFitCaveat\(state\.fitResult\)/, 'Save Fit derives the caveat');
  assert.match(save, /reportable: _isLocalFit\(state\.fitResult\) \? false/, 'Save Fit derives reportable');
});

test('_applyStatDisplay clears header, tooltip, caption and value together on local → none', () => {
  const src = ['_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay'].map(extractFn).join('\n');
  const constLine = html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n');
  const dom = {}; const el = id => (dom[id] ||= { textContent: '', innerHTML: '', tip: null, setAttribute(k, v) { this.tip = v; }, removeAttribute() { this.tip = null; } });
  const apply = new Function('document', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_updateLocalModelBanner', constLine + '\n' + src + '\nreturn _applyStatDisplay;')({ getElementById: el }, 'CHI', 'LOCAL', () => {});
  apply({ objective: 'unweighted_residual_variance', chiReduced: 999 });
  apply(null);
  assert.match(dom['fit-quality'].innerHTML, /&mdash;/); assert.equal(dom['fit-quality'].tip, null);
  assert.doesNotMatch(dom['sb-chi-caption'].innerHTML, /starting point/); assert.equal(dom['sb-chi'].textContent, '—');
});

// ── Codex round-11: the designation follows the MODEL through a .fit.json round trip ──
test('_isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result', () => {
  const src = ['_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel'].map(extractFn).join('\n');
  const mk = (fitResult, tab) => new Function('state', '_activeTab', src + '\nreturn _isLocalModel;')({ fitResult }, () => tab);
  assert.equal(mk(null, { modelProvenance: { objective: 'unweighted_residual_variance' } })(), true);
  assert.equal(mk(null, { modelProvenance: null })(), false);
  assert.equal(mk({ chiReduced: 2 }, { modelProvenance: { objective: 'unweighted_residual_variance' } })(), false, 'a weighted fit result supersedes imported provenance');
  assert.equal(mk({ objective: 'unweighted_residual_variance', chiReduced: 2 }, null)(), true);
});

test('fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it', () => {
  const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
  assert.match(grab('  fromJSON(data) {', 6000), /active\.modelProvenance = /, 'fromJSON records imported provenance');
  const save = grab('function _doSaveFit()', 3500);
  assert.match(save, /modelProvenance/, 'Save Fit falls back to imported provenance');
  assert.match(grab('function exportResults()', 2500), /_isLocalModel\(\)/, 'TSV export keys on the model provenance');
  assert.match(grab('const buildTabData = (t) =>', 4000), /modelProvenance: t\.modelProvenance \|\| null/, 'project save carries provenance');
  assert.match(grab('function _loadProjectJSON(', 8000), /modelProvenance: t\.modelProvenance \|\| null/, 'project load carries provenance');
  assert.match(grab('function renderResults()', 1200), /_isLocalModel\(\)/, 'no-result placeholder designates an imported local model');
  for (const fn of ['function runFitLocal(', 'async function runFit()', 'function applyAutoFitResult(', 'function clearAllPeaks()']) {
    assert.match(grab(fn, 25000), /modelProvenance = null/, fn + ' clears imported provenance');
  }
});

// ── Codex round-12: provenance survives undo/redo and spectrum save/load; import refreshes Results; figure/chart key on the model; Find Peaks clears it ──
test('undo/redo snapshots carry and restore model provenance', () => {
  const src = ['_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_localFitCaveat', '_provenanceOf', '_peaksSnapshot', '_restoreSnapshotEndpointAvg', '_restoreSnapshotProvenance'].map(extractFn).join('\n');
  const constLine = html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n');
  const tab = { modelProvenance: { objective: 'unweighted_residual_variance', caveat: 'x' }, ui: {} };
  const fns = new Function('state', '_historyTab', 'document', constLine + '\n' + src + '\nreturn { _peaksSnapshot, _restoreSnapshotProvenance };')(
    { peaks: [{ id: 1, center: 285 }], fitResult: null }, () => tab, { getElementById: () => null });
  const snap = fns._peaksSnapshot(null);
  assert.deepEqual(snap._modelProvenance, tab.modelProvenance, 'snapshot captures the active tab provenance');
  tab.modelProvenance = null;
  fns._restoreSnapshotProvenance(tab, snap);
  assert.deepEqual(tab.modelProvenance, { objective: 'unweighted_residual_variance', caveat: 'x' }, 'restore reinstates it');
  tab.modelProvenance = null;
  const snap2 = fns._peaksSnapshot(null);   // provenance now null
  assert.strictEqual(snap2._modelProvenance, null);
  fns._restoreSnapshotProvenance(tab, snap2);
  assert.strictEqual(tab.modelProvenance, null, 'restore also clears it when the snapshot had none');
});

test('round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it', () => {
  const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
  assert.match(grab('function undo()', 900), /_restoreSnapshotProvenance\(t, snap\)/, 'undo');
  assert.match(grab('function redo()', 900), /_restoreSnapshotProvenance\(t, snap\)/, 'redo');
  assert.match(grab('function _pushUndoFor(', 600), /_modelProvenance/, 'batch history entry carries provenance');
  assert.match(grab('function _doSaveSpectrum()', 4000), /modelProvenance: tab\.modelProvenance \|\| null/, 'spectrum save');
  assert.match(grab('function _loadSpectrumFile(', 7000), /active\.modelProvenance = /, 'spectrum load');
  const fj = grab('  fromJSON(data) {', 7000);
  assert.match(fj.slice(fj.indexOf('this._restoreUI(active.ui);')), /renderResults\(\)/, 'import renders Results');
  assert.match(grab('function exportFigure()', 60000), /if \(state\.fitResult \|\| _isLocalModel\(\)\)/, 'figure annotation keys on the model');
  assert.match(html, /label: _isLocalModel\(\) \? 'Fit \(local, starting point\)' : 'Fit'/, 'chart/figure envelope labels key on the model');
  assert.match(grab('async function applyFindPeaks()', 6000), /modelProvenance = null/, 'Find Peaks apply clears superseded provenance');
});

// ── Codex round-13: provenance derived from a LIVE local result for undo snapshots; batch clones carry the source's ──
test('_provenanceOf derives a designation from a live local result, and undo snapshots use it', () => {
  const src = ['_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_localFitCaveat', '_provenanceOf', '_peaksSnapshot'].map(extractFn).join('\n');
  const constLine = html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n');
  const tab = { modelProvenance: null, fitResult: null };
  const state = { peaks: [{ id: 1 }], fitResult: { objective: 'unweighted_residual_variance', engine: 'local', chiReduced: 3e4, status: 'converged' } };
  const fns = new Function('state', '_historyTab', constLine + '\n' + src + '\nreturn { _provenanceOf, _peaksSnapshot };')(state, () => tab);
  const p = fns._provenanceOf({ modelProvenance: null, fitResult: state.fitResult });
  assert.equal(p.objective, 'unweighted_residual_variance'); assert.equal(p.reportable, false); assert.match(p.caveat, /starting point/i);
  assert.equal(fns._provenanceOf({ modelProvenance: null, fitResult: { chiReduced: 2 } }), null, 'weighted result → no designation');
  assert.equal(fns._provenanceOf({ modelProvenance: { objective: 'unweighted_residual_variance' }, fitResult: null }).objective, 'unweighted_residual_variance');
  const snap = fns._peaksSnapshot(null);   // active tab has no stored provenance but a live local result
  assert.equal(snap._modelProvenance && snap._modelProvenance.objective, 'unweighted_residual_variance', 'snapshot derives provenance from the live local result');
});

test('batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)', () => {
  const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
  const rp = grab('async function runPropagation', 9000);
  assert.match(rp, /const srcProvenance = _provenanceOf\(sourceTab\)/, 'source provenance captured with the source snapshot');
  assert.match(rp, /tgt\.modelProvenance = srcProvenance/, 'target carries it with the copied model');
  assert.match(grab('function _pushUndoFor(', 700), /_provenanceOf\(tab\)/, 'batch history entry derives provenance too');
});

// ── Codex round-14: persistent designation in the Peaks sidebar; undo/redo re-render; auto-fit rollback carries provenance ──
test('the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise', () => {
  const src = ['_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel', '_governingProvenance', '_updateLocalModelBanner'].map(extractFn).join('\n');
  const run = (fitResult, tab) => {
    const el = { style: { display: 'block' } };
    new Function('state', '_activeTab', 'document', '_historyPreview', src + '\n_updateLocalModelBanner();')({ fitResult }, () => tab, { getElementById: id => id === 'local-model-banner' ? el : null }, null);
    return el.style.display;
  };
  assert.equal(run({ objective: 'unweighted_residual_variance', chiReduced: 1 }, { modelProvenance: null }), 'block');
  assert.equal(run(null, { modelProvenance: { objective: 'unweighted_residual_variance' } }), 'block');
  assert.equal(run({ chiReduced: 2 }, { modelProvenance: { objective: 'unweighted_residual_variance' } }), 'none', 'a weighted result supersedes');
  assert.equal(run(null, { modelProvenance: null }), 'none');
});

test('round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance', () => {
  const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
  assert.match(html, /id="local-model-banner"/, 'banner element in the Peaks sidebar');
  assert.match(grab('function renderPeakList()', 1200), /_updateLocalModelBanner\(\)/, 'peak list refresh updates the banner');
  assert.match(grab('function renderResults()', 1500), /_updateLocalModelBanner\(\)/, 'results refresh updates the banner');
  assert.match(grab('function undo()', 1000), /renderResults\(\)/, 'undo re-renders Results');
  assert.match(grab('function redo()', 1000), /renderResults\(\)/, 'redo re-renders Results');
  assert.match(grab('function _autoFitSnapshot()', 1500), /modelProvenance:/, 'auto-fit snapshot carries provenance');
  assert.match(grab('function _autoFitRestore(', 3000), /modelProvenance = snap\.modelProvenance/, 'auto-fit restore reinstates it');
});


// ── Codex round-15: banner outside the switchable panels; local history preview designated; history restore reconciles provenance ──
test('the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview', () => {
  const bannerAt = html.indexOf('id="local-model-banner"'), tabsAt = html.indexOf('<div class="tabs">'), peaksPanelAt = html.indexOf('id="tab-peaks"');
  assert.ok(bannerAt > 0 && bannerAt < tabsAt && bannerAt < peaksPanelAt, 'banner precedes the tab bar and every panel');
  const src = ['_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel', '_governingProvenance', '_updateLocalModelBanner'].map(extractFn).join('\n');
  const run = (fitResult, preview) => {
    const el = { style: { display: 'block' }, innerHTML: '' };
    new Function('state', '_activeTab', 'document', '_historyPreview', src + '\n_updateLocalModelBanner();')({ fitResult }, () => ({ modelProvenance: null }), { getElementById: id => id === 'local-model-banner' ? el : null }, preview);
    return el;
  };
  const shown = run({ chiReduced: 2 }, { fitResult: { objective: 'unweighted_residual_variance' } });
  assert.equal(shown.style.display, 'block', 'a local preview overlay is designated even over a weighted current fit');
  assert.match(shown.innerHTML, /preview/i);
  assert.equal(run({ chiReduced: 2 }, { fitResult: { chiReduced: 1 } }).style.display, 'none');
  const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
  assert.match(grab('function _historyPreviewSnap(', 1400), /_updateLocalModelBanner\(\)/, 'preview start refreshes the banner');
  assert.match(grab('function _historyClearPreview(', 400), /_updateLocalModelBanner\(\)/, 'preview clear refreshes the banner');
  assert.match(grab('function _historyRestoreSnap(', 900), /modelProvenance = null/, 'history restore lets the restored result govern');
});

// ── Codex round-16: the sidebar designation stays in view when the panel body scrolls ──
test('the sidebar banner is sticky at the top of the scrolling panel body', () => {
  const m = html.match(/<div id="local-model-banner" style="([^"]*)"/);
  assert.ok(m, 'banner element');
  assert.match(m[1], /position:\s*sticky/, 'sticky positioning');
  assert.match(m[1], /top:\s*0/, 'pinned to the top of its scroll container');
  assert.match(m[1], /z-index:\s*[1-9]/, 'stacked above the peak cards');
});

// ── Codex round-17: a stack view showing a local source's fit curves is designated too ──
test('the sidebar banner shows on a stack tab whose visible entries draw a local source fit', () => {
  const src = ['_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel', '_governingProvenance', '_updateLocalModelBanner'].map(extractFn).join('\n');
  const local = { id: 2, fitResult: { objective: 'unweighted_residual_variance', chiReduced: 1 }, name: 'C1s local' };
  const weighted = { id: 3, fitResult: { chiReduced: 2 }, name: 'C1s server' };
  const tabManager = { _getTab: id => ({ 2: local, 3: weighted })[id] };
  const run = (tab) => {
    const el = { style: { display: 'block' }, innerHTML: '' };
    new Function('state', '_activeTab', 'document', '_historyPreview', 'tabManager', '_escHtml', src + '\n_updateLocalModelBanner();')({ fitResult: null }, () => tab, { getElementById: id => id === 'local-model-banner' ? el : null }, null, tabManager, x => String(x));
    return el;
  };
  const shown = run({ isStack: true, entries: [{ sourceTabId: 2, visible: true, showFit: true }, { sourceTabId: 3, visible: true, showFit: true }] });
  assert.equal(shown.style.display, 'block'); assert.match(shown.innerHTML, /C1s local/); assert.match(shown.innerHTML, /starting point/i);
  assert.equal(run({ isStack: true, entries: [{ sourceTabId: 2, visible: true, showFit: false }] }).style.display, 'none', 'fit curves hidden → no designation needed');
  assert.equal(run({ isStack: true, entries: [{ sourceTabId: 3, visible: true, showFit: true }] }).style.display, 'none', 'weighted source only');
  const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
  assert.match(grab('function _applyStatDisplay(', 900), /_updateLocalModelBanner\(\)/, 'activation/result changes refresh the banner');
  const legendAt = html.indexOf("row.querySelector('.name').textContent = name;");
  assert.match(html.slice(legendAt, legendAt + 2500), /_updateLocalModelBanner\(\)/, 'stack legend rebuild refreshes the banner');
});

// ── Codex round-18: stack visibility / fit toggles refresh the designation ──
test('every stack chart repaint path refreshes the sidebar designation before any early return', () => {
  const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
  for (const fn of ['function _updateStackChart(', 'function _renderStackChart(']) {
    const body = grab(fn, 400);
    const firstReturn = body.indexOf('return');
    const bannerAt = body.indexOf('_updateLocalModelBanner()');
    assert.ok(bannerAt > 0 && (firstReturn < 0 || bannerAt < firstReturn), fn + ' must refresh the banner before its first return');
  }
});

// ── Codex round-19: closing a source tab prunes its curves from an ACTIVE stack's chart, not only its legend ──
test('closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab', () => {
  const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
  const ct = grab('  closeTab(', 3000);
  const prune = ct.slice(ct.indexOf('t.entries = t.entries.filter(e => e.sourceTabId !== id)'), ct.indexOf('t.entries = t.entries.filter(e => e.sourceTabId !== id)') + 600);
  assert.match(prune, /_renderStackChart\(t\)/, 'the active stack chart is rebuilt after pruning');
});


// ── Unit W1: designation helpers are objective-aware (weighted local vs legacy unweighted vs server) ──
test('W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched', () => {
  const src = ['_isUnweightedLocal', '_fitStatLabel', '_isLocalProvenance', '_isLocalFit', '_localFitDetail', '_localFitCaveat', '_fitStatusText'].map(extractFn).join('\n');
  const consts = html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n');
  const h = new Function(consts + '\n' + src + '\nreturn { _fitStatLabel, _isLocalFit, _localFitCaveat, _fitStatusText, _localFitDetail };')();
  const weighted = { engine: 'local', objective: 'poisson_weighted_chi_square', chiReduced: 4.353 };
  const legacy = { engine: 'local', objective: 'unweighted_residual_variance', chiReduced: 34523.31 };
  const server = { chiReduced: 4.357 };
  assert.equal(h._fitStatLabel(weighted), '\u03c7\u00b2\u1d63'); assert.equal(h._fitStatLabel(legacy), 'Residual variance');
  assert.equal(h._isLocalFit(weighted), true); assert.equal(h._isLocalFit(legacy), true); assert.equal(h._isLocalFit(server), false);
  assert.match(h._localFitCaveat(weighted), /Poisson-weighted like the server, no uncertainties.*starting point, not a reportable result/);
  assert.match(h._localFitCaveat(legacy), /unweighted fit: a starting point/);
  assert.equal(h._localFitCaveat(server), '');
  assert.equal(h._fitStatusText(weighted), '\u03c7\u00b2\u1d63 = 4.35 (local, starting point)');
  assert.equal(h._fitStatusText(server), '\u03c7\u00b2\u1d63 = 4.36');
  assert.match(h._localFitDetail(weighted), /Voigt or LA components/); assert.match(h._localFitDetail(legacy), /more than 100/);
});

// ── W1 Codex round 1: the TSV export's warning follows the GOVERNING objective (behavioural) ──
test('TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result', () => {
  const src = ['_isUnweightedLocal', '_isLocalProvenance', '_isLocalFit', '_isLocalModel', '_localFitCaveat', '_governingProvenance', 'exportResults'].map(extractFn).join('\n');
  const consts = html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n');
  const run = (fitResult, modelProvenance) => {
    let text = null;
    class Blob { constructor(parts) { text = parts.join(''); } }
    const state = { fitResult, peaks: [{ id: 1, name: 'p' }] };
    new Function('state', '_activeTab', 'getROIData', 'computeBackground', 'evalAllPeaks', 'evalPeakArray', 'Blob', 'URL', 'document', 'notify',
      consts + '\n' + src + '\nexportResults();')(state, () => ({ modelProvenance }), () => ({ be: [1, 2], inten: [5, 6] }), () => [0, 0],
      () => [1, 1], () => [1, 1], Blob, { createObjectURL: () => 'u', revokeObjectURL() {} }, { createElement: () => ({ click() {} }) }, () => {});
    return text.split('\n')[0];
  };
  assert.match(run({ engine: 'local', objective: 'unweighted_residual_variance', chiReduced: 3e4 }, null), /^# WARNING: Local unweighted fit/);
  assert.match(run(null, { engine: 'local', objective: 'unweighted_residual_variance' }), /^# WARNING: Local unweighted fit/, 'imported legacy model');
  assert.match(run({ engine: 'local', objective: 'poisson_weighted_chi_square', chiReduced: 4 }, null), /^# WARNING: Local fit \(Poisson-weighted/);
  assert.doesNotMatch(run({ chiReduced: 4 }, null), /WARNING/);
});
