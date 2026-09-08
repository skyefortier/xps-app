'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
function extract(a, b) {
  const i = html.indexOf(a), j = html.indexOf(b, i + a.length);
  assert.ok(i >= 0 && j > i); return html.slice(i, j);
}
function context(extra = {}) {
  const els = {}, noop = () => {};
  return vm.createContext({Blob, document: {getElementById(id) {
    return els[id] ||= {value: '', style: {}, removeAttribute: noop};
  }}, notify: noop, _escHtml: s => s, ...extra});
}
test('project preserves exact fit arrays, local statistic identity, and reproducibility settings', async () => {
  let blob;
  const fr = {chi: 3, chiReduced: 1.5, rmse: .3, be: [1.123456789, 2.123456789],
    bgIntensity: [.123456789, .234567891], bgSubtracted: [2.123456789, 4.234567891],
    fittedY: [2, 4], objective: 'unweighted_least_squares', statisticLabel: 'Residual variance',
    uncertaintyAvailable: false, fitInputs: {background: {type: 'manual', endpointAvg: 5}},
    provenance: {software: {source_sha256: 'abc'}}, status: 'converged'};
  const tab = {id: 'A', peaks: [], ui: {}, fitResult: fr};
  const c = context({tabManager: {_syncActiveToRecord() {}, tabs: [tab], activeId: 'A'},
    RefCore: {serializeRefOverlays() {}, serializeRefCompoundMarkers() {}},
    _refCompoundMarkers: [], _downloadBlob: b => {blob = b;}});
  vm.runInContext(extract('async function _doSaveProject(', '// ── Unified Load'), c);
  await c._doSaveProject();
  const saved = JSON.parse(await blob.text()).tabs[0].fitResult;
  for (const key of ['be','bgIntensity','bgSubtracted','objective','statisticLabel','uncertaintyAvailable','fitInputs','provenance']) {
    assert.deepEqual(saved[key], fr[key], key);
  }
});
test('table export refuses stale or incomplete fitted records before evaluating curves', () => {
  let evaluated = false, notice;
  const c = context({state: {fitResult: {stale: true}}, notify: s => {notice = s;},
    _peakArea() {evaluated = true;}});
  vm.runInContext(extract('function exportFitTable(', '\n// ══'), c);
  c.exportFitTable('csv');
  assert.match(notice, /current fit/); assert.equal(evaluated, false);
  c.state.fitResult = {chiReduced: 1}; c.exportFitTable('csv');
  assert.equal(evaluated, false);
});
test('spectrum save keeps the accepted grid, background and residuals together despite viewer ROI changes', async () => {
  let blob;
  const fr = {chi: 2, chiReduced: 1, rmse: 1, be: [1, 2], bgIntensity: [3, 4],
    bgSubtracted: [7, 16], fittedY: [9, 19]};
  const tab = {name: 'test', rawBE: [1, 2, 3], rawIntensity: [10, 20, 30], peaks: [], ui: {}};
  const c = context({state: {fitResult: fr, peaks: []},
    tabManager: {_syncActiveToRecord() {}, _getTab: () => tab},
    getROIData: () => ({be: [2, 3], inten: [20, 30]}),
    computeBackground() {throw new Error('Must preserve accepted background');},
    evalAllPeaks: be => be.map(() => 999), _downloadBlob: b => {blob = b;}});
  vm.runInContext(extract('function _doSaveSpectrum(', '// ── 3. Save Project'), c);
  c._doSaveSpectrum();
  const saved = JSON.parse(await blob.text());
  assert.deepEqual(saved.roiBE, [1, 2]); assert.deepEqual(saved.background, [3, 4]);
  assert.deepEqual(saved.fittedY, [9, 19]); assert.deepEqual(saved.residuals, [1, 1]);
  assert.equal(saved.fitResult.chi, 2);
});
test('batch copies endpoint averaging and scaled manual anchors and reports unsuccessful optimization', async () => {
  const BatchPropagation = require('../../static/js/batch_propagation.js');
  const src = {id: 'A', name: 'source', rawIntensity: [10], peaks: [{id: 1, amplitude: 8, _backendParams: {old: true}}],
    ui: {endpointAvg: '5'}, manualAnchors: [{x: 1, y: 2}], ccShift: .2};
  const tgt = {id: 'B', name: 'target', rawIntensity: [20], peaks: [], ui: {}, fitResult: {chiReduced: .01}};
  const state = {peaks: src.peaks, rawBE: [1, 2], fitResult: null};
  const tm = {activeId: 'A', _getTab: id => id === 'A' ? src : tgt, _syncActiveToRecord() {},
    activateTab(id) {this.activeId = id; const t = this._getTab(id); state.peaks = t.peaks; state.fitResult = t.fitResult;}};
  const c = context({state, tabManager: tm, BatchPropagation, _snapshotSuppressed: false,
    _arrMax: a => Math.max(...a), setTimeout: fn => {fn();},
    getROIData: () => ({be: [1, 2], inten: [10, 20]}), computeBackground: () => [0, 0],
    runFitLocal: () => ({success: false, message: 'Iteration limit reached'})});
  c.document.querySelectorAll = () => [{dataset: {id: 'B'}}];
  vm.runInContext(extract('async function runPropagation(', '// ══════════════════════════════════════════════════════════════\n// FEATURE 2'), c);
  await c.runPropagation();
  assert.equal(tgt.ui.endpointAvg, '5'); assert.equal(tgt.manualAnchors[0].y, 4);
  assert.equal(src.manualAnchors[0].y, 2); assert.equal(tgt.peaks[0].amplitude, 16);
  assert.equal(tgt.peaks[0]._backendParams, undefined); assert.equal(tgt.fitResult, null);
  assert.equal(tm.activeId, 'A'); assert.equal(c._snapshotSuppressed, false);
  assert.match(c.document.getElementById('propagate-summary').innerHTML, /Iteration limit/);
  assert.match(c.document.getElementById('propagate-progress').textContent, /0 fitted; 1 failed/);
});
test('batch stops if the user switches to its next target between jobs', async () => {
  const src = {id: 'A', name: 'source', rawIntensity: [10], peaks: [{id: 1, amplitude: 8}], ui: {}};
  const tabs = {A: src, B: {id: 'B', name: 'first', rawIntensity: [20], peaks: [], ui: {}},
    C: {id: 'C', name: 'next', rawIntensity: [20], peaks: [{id: 1, amplitude: 99}], ui: {}}};
  const state = {peaks: src.peaks, rawBE: [1, 2]}; let fits = 0;
  const tm = {activeId: 'A', _getTab: id => tabs[id], _syncActiveToRecord() {},
    activateTab(id) {if (id === this.activeId) return; this.activeId = id; state.peaks = tabs[id].peaks;}};
  const c = context({state, tabManager: tm, _snapshotSuppressed: false,
    BatchPropagation: require('../../static/js/batch_propagation.js'), _arrMax: a => Math.max(...a),
    setTimeout(fn, ms) {if (ms === 10) tm.activateTab('C'); fn();},
    getROIData: () => ({be: [1, 2], inten: [10, 20]}), computeBackground: () => [0, 0],
    runFitLocal() {fits++; state.fitResult = {chiReduced: 1}; return {success: true};}});
  c.document.querySelectorAll = () => ['B', 'C'].map(id => ({dataset: {id}}));
  vm.runInContext(extract('async function runPropagation(', '// ══════════════════════════════════════════════════════════════\n// FEATURE 2'), c);
  await c.runPropagation();
  assert.equal(fits, 1); assert.equal(tabs.C.peaks[0].amplitude, 99);
  assert.equal(tm.activeId, 'A'); assert.equal(c._snapshotSuppressed, false);
  assert.match(c.document.getElementById('propagate-summary').innerHTML, /active spectrum changed/);
});
