'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
function extract(start, end) {
  const a = html.indexOf(start), b = html.indexOf(end, a + start.length);
  assert.ok(a >= 0 && b > a); return html.slice(a, b);
}
function fixture() {
  const nodes = {}, noop = () => {};
  const accepted = {stale: false, chi: 1, chiReduced: .1, rmse: .2,
    be: [2,1], fittedY: [10,10], bgIntensity: [0,0], bgSubtracted: [10,10],
    rFactor: {rPct: .1, level: 'good'}, backendResult: {individual_peaks: [
      {id: '1', params: {amplitude: {value: 10, stderr: .1}}}]}};
  const state = {peaks: [{id: 1, name: 'peak', amplitude: 10}], fitResult: accepted,
    rawBE: [2,1], rawIntensity: [10,10]};
  const tab = {name: 'test', peaks: state.peaks, rawBE: state.rawBE,
    rawIntensity: state.rawIntensity, ui: {}, manualAnchors: [{x:2,y:0},{x:1,y:0}]};
  const tm = {activeId: 'A', _getTab: () => tab,
    _syncActiveToRecord() {tab.peaks = state.peaks; tab.fitResult = state.fitResult;}};
  const c = vm.createContext({Blob, state, tabManager: tm, undoStack: [], redoStack: [],
    document: {getElementById(id) {return nodes[id] ||= {value:'', textContent:'', innerHTML:'',
      style:{}, removeAttribute:noop};}}, notify:noop, confirm:()=>true,
    renderPeakList:noop, updatePlot:noop, _updateUndoButtons:noop, pushUndo:noop,
    _updateLockAllBtn:noop, _updateManualAnchorCount:noop, _RFACTOR_TOOLTIP:'',
    getROIData:()=>({be:[2,1],inten:[10,10]}), computeBackground:()=>[0,0],
    evalAllPeaks:be=>be.map(()=>state.peaks.reduce((s,p)=>s+p.amplitude,0)),
    evalPeakArray:(be,p)=>be.map(()=>p.amplitude), _downloadBlob:blob=>{c.savedBlob=blob;}});
  for (const [start,end] of [
    ['function undo()', '// ═'],
    ['function _invalidateBgCache()', 'function _clampShirleyIter()'],
    ['function _buildStderrMap(', '// Trapezoidal area'],
    ['function renderResults()', '// Auto-detect element/orbital'],
    ['function _updateRFactorUI(', 'function _updateROIDisplay('],
    ['function clearAllPeaks()', '// Handler for the linked-peak'],
    ['function toggleLock(', 'function _updateLockAllBtn()'],
    ['function _getManualAnchors()', 'function _onBgTypeChange()'],
    ['function _manualUndoAnchor()', '// Linear interpolation'],
    ['function _doSaveSpectrum()', '// ── 3. Save Project'],
  ]) vm.runInContext(extract(start,end),c);
  c.document.getElementById('sb-runs').textContent = 'R: 0.1%';
  c.document.getElementById('results-area').innerHTML = 'old fit';
  c.document.getElementById('quantify-area').innerHTML = 'old quantification';
  return {c, state, nodes, tab, accepted};
}
function assertStale(f) {
  assert.equal(f.state.fitResult.stale,true);
  assert.equal(f.state.fitResult.fittedY,null);
  assert.equal(Object.keys(f.c._buildStderrMap(f.state.fitResult)).length,0);
  assert.equal(f.nodes['sb-runs'].textContent,'');
  assert.equal(f.nodes['sb-chi'].textContent,'—');
  assert.match(f.nodes['results-area'].innerHTML,/Run the fit again/);
  assert.match(f.nodes['quantify-area'].innerHTML,/Run fit to quantify/);
}

test('undo after accepted fit invalidates envelope and uncertainty; saved spectrum is an honest preview',async()=>{
  const f=fixture(); f.c.undoStack.push([{id:1,name:'peak',amplitude:5}]);
  f.c.undo(); assert.equal(f.state.peaks[0].amplitude,5); assertStale(f);
  f.c._doSaveSpectrum(); const saved=JSON.parse(await f.c.savedBlob.text());
  assert.equal(saved.fitResult,null); assert.equal(saved.statistics,null);
  assert.deepEqual(saved.peakCurves[0].y,[5,5]); assert.deepEqual(saved.fittedY,[5,5]);
  assert.deepEqual(saved.residuals,[5,5]);
});

test('redo after a subsequent accepted fit cannot retain that fit diagnostics',()=>{
  const f=fixture(); f.c.redoStack.push([{id:1,amplitude:20}]);
  f.c.redo(); assert.equal(f.state.peaks[0].amplitude,20); assertStale(f);
});

test('empty undo/redo leave a current accepted fit alone',()=>{
  const f=fixture(); f.c.undo();f.c.redo();assert.equal(f.state.fitResult.stale,false);
});

test('unlinking changes constraint count and invalidates prior covariance',()=>{
  const f=fixture(); f.state.peaks.push({id:2,amplitude:5,linked:1});
  f.c.unlinkPeak(2);assert.equal(f.state.peaks[1].linked,null);assertStale(f);
});

test('single lock change invalidates the uncertainty from the previous free parameter set',()=>{
  const f=fixture();f.c.toggleLock(1,'fixAmplitude',{});
  assert.equal(f.state.peaks[0].fixAmplitude,true);assertStale(f);
});

test('lock all changes invalidate the previous fit',()=>{
  const f=fixture(); f.c.toggleAllLocks();
  assert.equal(f.state.peaks[0].fixCenter,true);assertStale(f);
});

test('clear peaks removes result/quantification panels and old quality values',()=>{
  const f=fixture();f.c.clearAllPeaks();
  assert.equal(f.state.fitResult,null);assert.equal(f.state.peaks.length,0);
  assert.match(f.nodes['results-area'].innerHTML,/Run the fit to see results/);
  assert.match(f.nodes['quantify-area'].innerHTML,/Run fit to quantify/);
  assert.equal(f.nodes['sb-runs'].textContent,'');assert.equal(f.nodes['sb-chi'].textContent,'—');
});

test('editing/clearing manual background anchors invalidates frozen background and diagnostics',()=>{
  for(const action of ['_manualUndoAnchor','_manualClearAnchors']){
    const f=fixture();f.c[action]();assertStale(f);
    assert.equal(f.state.fitResult.bgIntensity,null);
  }
});

test('restoring anchors can explicitly preserve the matching accepted snapshot',()=>{
  const f=fixture();f.c._setManualAnchors([{x:2,y:0},{x:1,y:0}],false);
  assert.equal(f.state.fitResult,f.accepted);assert.equal(f.state.fitResult.stale,false);
});
