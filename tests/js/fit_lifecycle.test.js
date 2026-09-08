/* Behavioral regressions for the shipped fit lifecycle, independent of lmfit. */
'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
function extract(start, end) {
  const i = html.indexOf(start), j = html.indexOf(end, i + start.length);
  assert.ok(i >= 0 && j > i, 'source boundaries exist');
  return html.slice(i, j);
}
const code = extract('async function runFit()', '// ═══════════════════════════════════════════════════\n// RESULTS');
const gaussian = (x, p) => p.amplitude * Math.exp(-4 * Math.log(2) * ((x - p.center) / p.fwhm) ** 2);
const model = (x, peaks) => x.map(v => peaks.reduce((sum, p) => sum + gaussian(v, p), 0));
const grid = Array.from({ length: 201 }, (_, i) => -2 + i * 0.04);
const initial = () => ({ id: 1, shape: 'Gaussian', center: 1.65, fwhm: 1.5, amplitude: 25 });
function ctx() {
  const elements = {}, notifications = [], noop = () => {};
  const c = {
    state: { rawBE: grid.slice(), rawIntensity: grid.map(() => 0), ccShift: 0, peaks: [initial()], fitResult: null },
    tabManager: { activeId: 'A' }, notifications, snapshots: 0,
    document: { getElementById(id) { return elements[id] ||= { value: '', style: {}, setAttribute: noop, classList: { add: noop } }; } },
    notify: (...args) => notifications.push(args), _showFitSpinner: noop, _hideFitSpinner: noop,
    pushUndo: noop, _getManualAnchors: () => [], _snapshotSuppressed: false,
    getROIData: () => ({ be: grid.slice(), inten: grid.map(() => 1) }),
    computeBackground: be => be.map(() => 0),
    peakToBackendSpec: p => ({ ...p }), uploadToBackend: async () => 'session-A',
    applyBackendResult: result => { for (const ip of result.individual_peaks) c.state.peaks.find(p => p.id === Number(ip.id)).center = ip.params.center.value; },
    evalAllPeaks: model, _arrMin: a => Math.min(...a), _arrMax: a => Math.max(...a),
    _computeRFactor: () => 0, _updateRFactorUI: noop, _updateROIDisplay: noop,
    _CHISQ_TOOLTIP: '', renderPeakList: noop, updatePlot: noop, renderResults: noop,
    _autoSnapshot: () => c.snapshots++,
  };
  vm.createContext(c); vm.runInContext(code, c); return c;
}
function goodResponse() {
  return { ok: true, json: async () => ({ success: true,
    statistics: { chi_square: 1, reduced_chi_square: 0.1 },
    residuals: grid.map(() => 0), fitted_y: grid.map(() => 1),
    background_y: grid.map(() => 0.2), counts: grid.map(() => 1),
    individual_peaks: [{ id: '1', params: { center: { value: 2 } } }],
  }) };
}
const tick = () => new Promise(resolve => setImmediate(resolve));

test('nonlinear local fit needs multiple accepted steps and recovers center, width, and height', () => {
  const c = ctx(), truth = { center: 2, fwhm: 0.8, amplitude: 40 };
  const result = c.runFitLocal(grid, model(grid, [truth]), grid.map(() => 0));
  assert.equal(result.success, true);
  assert.ok(result.acceptedSteps > 2, JSON.stringify(result));
  for (const k of ['center','fwhm','amplitude']) assert.ok(Math.abs(c.state.peaks[0][k] - truth[k]) < 1e-4, k);
  assert.equal(c.state.fitResult.objective, 'unweighted_least_squares');
  assert.equal(c.state.fitResult.uncertaintyAvailable, false);
});

test('linked siblings and descendants inherit every fixed root shape parameter', () => {
  const c = ctx();
  c.state.peaks = [
    { id: 1, shape: 'Gaussian', center: 0, fwhm: 0.8, amplitude: 5, fixCenter: true, fixFwhm: true },
    { id: 2, shape: 'Lorentzian', linked: 1, linkOffset: 1, linkRatio: 0.5, center: 999, fwhm: 3, amplitude: 2 },
    { id: 3, shape: 'Lorentzian', linked: 1, linkOffset: 2, linkRatio: 0.3, center: 999, fwhm: 3, amplitude: 2 },
    { id: 4, shape: 'Lorentzian', linked: 2, linkOffset: 0.5, linkRatio: 0.2, center: 999, fwhm: 3, amplitude: 2 },
  ];
  const truth = [10,5,3,1].map((amplitude, i) => ({ amplitude, center: [0,1,2,1.5][i], fwhm: 0.8 }));
  assert.equal(c.runFitLocal(grid, model(grid, truth), grid.map(() => 0)).success, true);
  for (let i = 0; i < 4; i++) {
    assert.ok(Math.abs(c.state.peaks[i].amplitude - truth[i].amplitude) < 1e-5);
    assert.equal(c.state.peaks[i].center, truth[i].center);
    assert.equal(c.state.peaks[i].fwhm, 0.8);
    assert.equal(c.state.peaks[i].shape, 'Gaussian');
  }
});

test('local optimization is invariant to a rigid binding-energy offset', () => {
  const y = model(grid, [{center: 2,fwhm: 0.8,amplitude: 40}]).map((v,i) => v + 0.5*Math.sin(i*0.73));
  const a = ctx(), b = ctx();
  b.state.peaks[0].center += 284;
  assert.equal(a.runFitLocal(grid, y, grid.map(() => 0)).success, true);
  assert.equal(b.runFitLocal(grid.map(x => x+284), y, grid.map(() => 0)).success, true);
  assert.ok(Math.abs(a.state.peaks[0].center - (b.state.peaks[0].center-284)) < 1e-6);
  for (const k of ['fwhm','amplitude']) assert.ok(Math.abs(a.state.peaks[0][k]-b.state.peaks[0][k]) < 1e-5, k);
});

test('amplitude can converge at its physical zero bound', () => {
  const c = ctx(); c.state.peaks[0].fixCenter = c.state.peaks[0].fixFwhm = true;
  assert.equal(c.runFitLocal(grid, grid.map(() => -1), grid.map(() => 0)).success, true);
  assert.equal(c.state.peaks[0].amplitude, 0);
});

test('center bound is anchored to the initial value, not moved with each trial', () => {
  const c = ctx();
  c.state.peaks = [{ id: 1, shape: 'Gaussian', center: 1.5, fwhm: 1, amplitude: 10,
    fixFwhm: true, fixAmplitude: true }];
  assert.equal(c.runFitLocal(grid, model(grid, [{center: 4,fwhm: 1,amplitude: 10}]), grid.map(() => 0)).success, true);
  assert.equal(c.state.peaks[0].center, 3.5);
});

test('iteration exhaustion preserves previous peaks and committed fit', () => {
  const c = ctx(), prior = { chi: 123 }; c.state.fitResult = prior;
  const peaks = JSON.stringify(c.state.peaks);
  const result = c.runFitLocal(grid, model(grid, [{ center: 2, fwhm: 0.8, amplitude: 40 }]), grid.map(() => 0), { maxIterations: 1 });
  assert.equal(result.success, false); assert.equal(JSON.stringify(c.state.peaks), peaks);
  assert.equal(c.state.fitResult, prior); assert.equal(c.snapshots, 0);
});

test('invalid data and circular links fail without mutating live state', () => {
  const c = ctx();
  assert.equal(c.runFitLocal(grid, [NaN], []).success, false);
  c.state.peaks[0].linked = 1;
  const old = JSON.stringify(c.state.peaks);
  assert.equal(c.runFitLocal(grid, grid.map(() => 1), grid.map(() => 0)).success, false);
  assert.equal(JSON.stringify(c.state.peaks), old);
});

test('A -> B -> A during upload sends the original model and accepts its valid result', async () => {
  const c = ctx(); let uploadDone, request;
  const a = c.state.peaks;
  c.uploadToBackend = () => new Promise(resolve => { uploadDone = resolve; });
  c.fetch = async (_url, opts) => { request = JSON.parse(opts.body); return goodResponse(); };
  const pending = c.runFit();
  c.tabManager.activeId = 'B'; c.state.peaks = [{ ...initial(), center: 532 }];
  uploadDone('session-A'); await tick();
  // The immediate result was discarded while B remained active.
  assert.equal((await pending).stale, true);
  assert.equal(request.peaks[0].center, a[0].center);
  c.tabManager.activeId = 'A'; c.state.peaks = a;
  let responseDone;
  c.uploadToBackend = async () => 'session-A';
  c.fetch = () => new Promise(resolve => { responseDone = resolve; });
  const second = c.runFit(); await tick();
  c.tabManager.activeId = 'B'; c.state.peaks = [{ ...initial(), center: 532 }];
  c.tabManager.activeId = 'A'; c.state.peaks = a;
  responseDone(goodResponse());
  assert.equal((await second).success, true);
  assert.equal(c.state.fitResult.bgIntensity[0], 0.2);
  assert.equal(c.state.fitResult.bgSubtracted[0], 0.8);
});

test('same-tab parameter edits invalidate pending fit without erasing the edit', async () => {
  const c = ctx(); let done;
  c.fetch = () => new Promise(resolve => { done = resolve; });
  const pending = c.runFit(); await tick();
  c.state.peaks[0].center = 3;
  done(goodResponse());
  assert.equal((await pending).stale, true);
  assert.equal(c.state.peaks[0].center, 3); assert.equal(c.snapshots, 0);
});

for (const [name, response] of [
  ['nonconvergence', { ok: true, json: async () => ({ success: false, message: 'iteration limit' }) }],
  ['server rejection', { ok: false, status: 422, json: async () => ({ error: 'invalid model' }) }],
  ['malformed successful response', { ok: true, json: async () => ({ success: true }) }],
]) test(name + ' never silently invokes a different optimizer', async () => {
  const c = ctx(), prior = { chi: 123 }; let fallback = 0;
  c.state.fitResult = prior; c.fetch = async () => response;
  c.runFitLocal = () => { fallback++; return { success: true }; };
  assert.equal((await c.runFit()).success, false);
  assert.equal(fallback, 0); assert.equal(c.state.fitResult, prior); assert.equal(c.snapshots, 0);
});

test('a genuine network failure permits explicit local fallback', async () => {
  const c = ctx(); let fallback = 0;
  c.fetch = async () => { throw new Error('network disconnected'); };
  c.runFitLocal = () => { fallback++; return { success: true, engine: 'local' }; };
  assert.equal((await c.runFit()).engine, 'local'); assert.equal(fallback, 1);
});

test('auto graphite correction rigidly shifts the frozen server grid and preserves exact fitted arrays', () => {
  const c = ctx();
  vm.runInContext(extract('function applyAutoFitResult(', '// Top-level entry point.'), c);
  c.state.peaks = [{ id: 1, name: 'Graphite', center: 284.623, amplitude: 10, fwhm: 1 }];
  c.state.ccShift = 1.2;
  c._autoFitCheckGraphiteFraction = () => null;
  c.getROIData = c.computeBackground = () => { throw new Error('must not recompute fitted samples'); };
  c.updateChargeCorrection = () => {
    const next = Number(c.document.getElementById('cc-obs').value) - 284.5;
    const delta = next - c.state.ccShift;
    c.state.peaks.forEach(p => { p.center -= delta; }); c.state.ccShift = next;
  };
  const json = { energy: [284,284.1,284.2,284.3], counts: [11,22,33,44],
    background_y: [1,2,3,4], fitted_y: [10.9,22.2,32.7,44.4], residuals: [0.1,-0.2,0.3,-0.4],
    statistics: { chi_square: 7, reduced_chi_square: 0.25 },
    individual_peaks: [{ id: '1', params: { center: { value: 284.623, stderr: 0.01 } } }],
  };
  const fitInputs = { fitMethod: 'least_squares', ccShift: 1.2, be: json.energy.slice() };
  assert.equal(c.applyAutoFitResult(json, 285.7, { ccShift: 1.2, fitInputs }), true);
  const fit = c.state.fitResult;
  assert.equal(fit.chi, 7); assert.equal(fit.chiReduced, 0.25);
  assert.deepEqual(Array.from(fit.bgIntensity), json.background_y);
  assert.deepEqual(Array.from(fit.bgSubtracted), [10,20,30,40]);
  assert.deepEqual(Array.from(fit.fittedY), json.fitted_y);
  assert.ok(Math.abs(fit.be[0] - (284 - 0.123)) < 1e-10);
  assert.ok(Math.abs(fit.backendResult.individual_peaks[0].params.center.value - 284.5) < 1e-10);
  assert.equal(json.individual_peaks[0].params.center.value, 284.623, 'input response is unmodified');
  assert.equal(fit.fitInputs, fitInputs);
  assert.equal(fit.provenance.workflow, 'auto_c1s_graphite');
  assert.equal(c.state.peaks[0].fixCenter, true);
});
