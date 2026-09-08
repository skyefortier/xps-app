#!/usr/bin/env node
/*
 * Independent application audit probes for baseline aba24c69.
 * Run: node scripts/audit_application_repro.js
 * No browser, server, network, or experimental files are used. Production
 * functions are extracted verbatim into isolated VM contexts; only their
 * DOM/network dependencies are stubbed. JSON reports expected vs observed
 * behavior. Exit 1 means at least one behavioral defect was reproduced.
 */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../templates/index.html'), 'utf8');
function extract(start, end) {
  const i = source.indexOf(start);
  const j = source.indexOf(end, i + start.length);
  if (i < 0 || j < 0) throw new Error('Source boundary changed: ' + start);
  return source.slice(i, j);
}
function context(extra = {}) {
  const elements = {};
  const noop = () => {};
  const c = {
    state: { peaks: [], rawBE: [], rawIntensity: [] },
    document: { getElementById(id) {
      return elements[id] ||= { value: '', style: {}, setAttribute: noop,
        removeAttribute: noop, classList: { add: noop, remove: noop } };
    } },
    _CHISQ_TOOLTIP: '', _computeRFactor: () => 0,
    _updateRFactorUI: noop, _updateROIDisplay: noop, renderPeakList: noop,
    updatePlot: noop, renderResults: noop, _hideFitSpinner: noop,
    notify: noop, _autoSnapshot: noop, _arrMin: a => Math.min(...a),
    _arrMax: a => Math.max(...a), Blob, ...extra,
  };
  c.getPeak = id => c.state.peaks.find(p => p.id === id);
  return vm.createContext(c);
}
const results = [];
async function probe(id, expected, run) {
  try {
    const { observed, pass } = await run();
    results.push({ id, pass, expected, observed });
  } catch (e) {
    results.push({ id, pass: false, expected, harnessError: e.stack });
  }
}
(async () => {
  await probe('local_lm_amplitude_recovery', 'Recover amplitude 10 from initial 5 for a noiseless fixed-width Gaussian', () => {
    const c = context({ evalAllPeaks: (be, ps) => be.map(x => ps[0].amplitude * Math.exp(-4 * Math.log(2) * x * x)) });
    c.state.peaks = [{ id: 1, shape: 'Gaussian', center: 0, fwhm: 1,
      amplitude: 5, fixCenter: true, fixFwhm: true }];
    vm.runInContext(extract('function runFitLocal(', '// ═══════════════════════════════════════════════════\n// RESULTS'), c);
    const be = Array.from({ length: 101 }, (_, i) => (i - 50) / 20);
    const y = be.map(x => 10 * Math.exp(-4 * Math.log(2) * x * x));
    c.runFitLocal(be, y, be.map(() => 0));
    return { observed: { amplitude: c.state.peaks[0].amplitude, sse: c.state.fitResult.chi },
      pass: Math.abs(c.state.peaks[0].amplitude - 10) < 1e-4 };
  });
  for (const [id, peak, key, expectedValue, expectedFixed] of [
    ['voigt_preview_backend_contract', { shape: 'Voigt' }, 'gl_ratio', 0.5, 'fix_gl_ratio'],
    ['locked_zero_ds_alpha', { shape: 'DS', dsAlpha: 0, fixDsAlpha: true }, 'alpha', 0, 'fix_alpha'],
    ['locked_zero_asymmetric_gl_mix', { shape: 'asym-GL', glMix: 0, fixGlMix: true }, 'gl_ratio', 0, 'fix_gl_ratio'],
  ]) {
    await probe(id, { [key]: expectedValue, [expectedFixed]: true }, () => {
      const c = context();
      vm.runInContext(extract('function peakToBackendSpec(', 'function applyBackendResult('), c);
      const spec = c.peakToBackendSpec({ id: 1, center: 0, fwhm: 1, amplitude: 10, ...peak });
      return { observed: { [key]: spec[key], [expectedFixed]: spec[expectedFixed] },
        pass: spec[key] === expectedValue && spec[expectedFixed] === true };
    });
  }
  await probe('area_integration_nonuniform_grid', 'Integral of unit intensity over [0,3] equals 3', () => {
    const c = context({ evalPeakArray: be => be.map(() => 1) });
    vm.runInContext(extract('function _peakArea(', 'function renderResults('), c);
    const area = c._peakArea({}, [0, 0.1, 1, 3]);
    return { observed: area, pass: Math.abs(area - 3) < 1e-12 };
  });
  await probe('find_peaks_replacement_invalidates_prior_fit', 'Replacing a model clears the previous fitted envelope and diagnostics even when fitFullWindow is false', async () => {
    const c = context({
      _fpLast: { body: { peaks: [{ id: 1, center: 2 }] }, method: 'test', regions: ['test'], fitFullWindow: false },
      confirm: () => true, _showFindPeaksApplyConfirmModal: async () => true,
      pushUndo() {}, _fpPeakFromBackend: p => ({ ...p }),
      tabManager: { activeId: 'A', tabs: [{ id: 'A' }] },
      closeFindPeaksModal() {}, _fpFmt: s => s, FP_STRINGS: { toastApplied: 'applied' },
    });
    c.state.peaks = [{ id: 1, center: 0 }];
    c.state.fitResult = { fittedY: [10, 20], chiReduced: 0.1 };
    vm.runInContext(extract('async function applyFindPeaks(', '</script>'), c);
    await c.applyFindPeaks();
    return { observed: { center: c.state.peaks[0].center, fitResult: c.state.fitResult }, pass: c.state.fitResult === null };
  });
  await probe('project_roundtrip_parameter_uncertainty', 'Saved projects retain parameter standard errors accessible to the results/export reader', async () => {
    let saved;
    const params = { center: { value: 284.8, stderr: 0.02 } };
    const t = { id: 'A', name: 'test', rawBE: [284,285], rawIntensity: [10,20], ccShift: 0,
      peaks: [{ id: 1, name: 'C 1s', _backendParams: params }], nextId: 2, ui: {},
      fitResult: { chi: 1, chiReduced: 1, rmse: 1, be: [284,285], bgIntensity: [0,0],
        bgSubtracted: [10,20], fittedY: [10,20], backendResult: { individual_peaks: [{ id: '1', params }] } } };
    const c = context({ tabManager: { _syncActiveToRecord() {}, activeId: 'A', tabs: [t] },
      RefCore: { serializeRefOverlays: () => null, serializeRefCompoundMarkers: () => null },
      _refCompoundMarkers: [], _downloadBlob: blob => { saved = blob; } });
    vm.runInContext(extract('async function _doSaveProject(', '// ── Unified Load'), c);
    vm.runInContext(extract('function _buildStderrMap(', 'function _peakArea('), c);
    await c._doSaveProject();
    const restored = JSON.parse(await saved.text()).tabs[0];
    const map = c._buildStderrMap(restored.fitResult);
    return { observed: { persistedOnPeak: restored.peaks[0]._backendParams.center.stderr,
      resultsPanelStdErr: map['1']?.center?.stderr ?? null }, pass: map['1']?.center?.stderr === 0.02 };
  });
  await probe('manual_fit_captures_originating_tab_model', 'A fit started on tab A sends tab A peaks even if the user changes tabs during upload', async () => {
    let uploadDone, responseDone, request;
    const upload = new Promise(resolve => { uploadDone = resolve; });
    const response = new Promise(resolve => { responseDone = resolve; });
    const peakA = { id: 1, center: 284.8 }, peakB = { id: 1, center: 532 };
    const c = context({
      tabManager: { activeId: 'A' }, pushUndo() {}, _showFitSpinner() {},
      getROIData: () => ({ be: [284, 285], inten: [10, 20] }),
      computeBackground: () => [0, 0], uploadToBackend: () => upload,
      peakToBackendSpec: p => ({ ...p }),
      fetch: (_url, opts) => { request = JSON.parse(opts.body); return response; },
      applyBackendResult() {},
    });
    c.state.rawBE = [284, 285];
    c.state.peaks = [peakA];
    vm.runInContext(extract('async function runFit()', 'function runFitLocal('), c);
    const pending = c.runFit();
    c.tabManager.activeId = 'B'; c.state.peaks = [peakB];
    uploadDone('session-A');
    await new Promise(resolve => setImmediate(resolve));
    // Return to A before the response: the current-id-only guard now passes.
    c.tabManager.activeId = 'A'; c.state.peaks = [peakA];
    responseDone({ ok: true, json: async () => ({ success: true,
      statistics: { chi_square: 2, reduced_chi_square: 1 }, residuals: [0,0],
      fitted_y: [10,20], background_y: [0,0], counts: [10,20], individual_peaks: [] }) });
    await pending;
    return { observed: { uploadedSession: request.session_id,
      submittedCenter: request.peaks[0].center, acceptedOnTabA: !!c.state.fitResult },
      pass: request.peaks[0].center === peakA.center && !!c.state.fitResult };
  });
  const failed = results.filter(r => !r.pass).length;
  console.log(JSON.stringify({ suite: 'application-audit', probes: results.length, failed, results }, null, 2));
  process.exitCode = failed ? 1 : 0;
})();
