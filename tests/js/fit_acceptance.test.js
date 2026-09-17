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
    '_autoSnapshot', 'runFitLocal', '_snapshotSuppressed', 'console',
    src + '\nreturn { runFit };');
  const noop = () => {};
  const { runFit } = factory(document, state, fetchImpl, uploadImpl || (async () => 'sid'), (msg, kind) => calls.notify.push({ msg, kind }),
    noop, noop, noop, () => owner, o => o === owner, () => ({ be: state.rawBE.slice(), inten: state.rawIntensity.slice() }),
    b => b.map(() => 0), p => ({ id: p.id, shape: 'gaussian' }), () => [], () => { calls.applied++; },
    () => 0.1, '', noop, noop, noop, noop, noop, noop,
    () => { calls.local++; return { success: true, engine: 'local' }; }, false, { warn: noop, error: noop, log: noop });
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
    '_autoSnapshot', 'runFitLocal', '_snapshotSuppressed', 'console', src + '\nreturn { runFit };')(
    { getElementById: id => (dom[id] ||= { value: '', textContent: '', style: {}, setAttribute() {}, classList: { add(c) { this._c = c; }, remove() { this._c = null; }, _c: null } }), querySelector: () => ({}), querySelectorAll: () => [] },
    state, async () => { throw new TypeError('Failed to fetch'); }, async () => 'sid', noop, noop, noop, noop, () => owner, o => o === owner,
    () => ({ be: state.rawBE.slice(), inten: state.rawIntensity.slice() }), b => b.map(() => 0), p => ({ id: p.id }), () => [], noop,
    () => 0.1, '', noop, noop, noop, noop, noop, noop, () => ({ success: false, message: 'did not converge' }), false, { warn: noop });
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
});

test('the engine/objective labels of a fit result survive spectrum and project save/load', () => {
  const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
  // spectrum save: statistics block carries objective/engine; loader restores them
  const save = grab('function _doSaveSpectrum()', 2500);
  assert.match(save, /objective: state\.fitResult\.objective/);
  assert.match(save, /engine: state\.fitResult\.engine/);
  const load = grab('function _loadSpectrumFile(', 6000);
  assert.match(load, /\['engine', 'objective', 'status', 'caveat'\]/);
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
  assert.match(fig, /_fitStatLabel\(/, 'figure export must label the statistic by engine');
  assert.match(fig, /Residual variance \(local fit, not reportable\)/, 'figure annotation names the local statistic');
  // fit-history rows
  const hist = grab('function _renderHistoryList(', 3000);
  assert.match(hist, /_fitStatLabel\(/, 'history rows must label the statistic by engine');
  // tab activation tooltip
  const act = grab('fqEl.textContent = _fitStatusText(state.fitResult)', 400);
  assert.match(act, /_LOCALFIT_TOOLTIP/, 'tab activation must attach the local tooltip for local results');
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
  assert.match(ex, /not a reportable result/i, 'CSV/XLSX export must carry the warning for a local result');
  // figure annotation
  const fig = grab('function exportFigure()', 60000);
  assert.match(fig, /local fit, not reportable/i, 'figure annotation must say not reportable');
  // local-fit overlay
  assert.match(html, /id="localfit-warn-overlay"[\s\S]{0,1500}starting point/i, 'overlay must say starting point');
});

// ── Codex round-7: the starting-point designation at every site, behaviourally ──
test('starting-point helpers: keyed on the persisted objective, weighted results untouched', () => {
  const src = ['_fitStatLabel', '_isLocalFit', '_localFitCaveat', '_fitStatusText'].map(extractFn).join('\n');
  const constLine = html.match(/^const _LOCAL_FIT_CAVEAT = .*$/m); assert.ok(constLine, '_LOCAL_FIT_CAVEAT constant');
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
  const src = ['renderQuantify', '_fitStatLabel', '_isLocalFit', '_localFitCaveat'].map(extractFn).join('\n');
  const constLine = html.match(/^const _LOCAL_FIT_CAVEAT = .*$/m)[0];
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
  assert.match(grab('function _doSaveSpectrum()', 2500), /caveat: state\.fitResult\.caveat/, 'spectrum save persists caveat');
  assert.match(grab('function _doSaveSpectrum()', 2500), /reportable: state\.fitResult\.reportable/, 'spectrum save persists reportable');
  assert.match(grab('const buildTabData = (t) =>', 3500), /caveat: t\.fitResult\.caveat/, 'project save persists caveat');
  assert.match(grab('function _loadSpectrumFile(', 6000), /'caveat'/, 'spectrum load restores caveat');
  assert.match(grab('fqEl.textContent = _fitStatusText(state.fitResult)', 200), /_applyStatCaption\(/, 'tab activation');
  assert.match(html, /id="sb-chi-caption"/, 'status-bar caption element');
  assert.match(grab('function _renderHistoryList(', 3000), /starting point/, 'history rows');
  assert.match(grab("label: _isLocalFit(state.fitResult) ? 'Fit (local, starting point)' : 'Fit'", 100), /Fit \(local/, 'chart envelope label');
  const fig = grab('function exportFigure()', 60000);
  assert.match(fig, /label: _isLocalFit\(state\.fitResult\) \? 'Fit \(local, starting point\)' : 'Fit'/, 'figure legend label');
  // the local fit result itself declares it
  const rfl = grab('function runFitLocal(', 20000);
  assert.match(rfl, /reportable: false, caveat: _LOCAL_FIT_CAVEAT/, 'runFitLocal marks its result');
});
