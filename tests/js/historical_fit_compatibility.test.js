'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
const start = html.indexOf('function _preserveHistoricalNumericalFit(');
const end = html.indexOf('function _loadSpectrumFile(', start);
const c = vm.createContext({});
vm.runInContext(html.slice(start, end), c);
const plain = v => JSON.parse(JSON.stringify(v));
function record(shape, version) {
  return {id: 'A', peaks: [{id: 1, shape, center: 284.5, laAlpha: 0.1}],
    ccShift: 1.234, ui: {bgType: 'manual', endpointAvg: '5'}, manualAnchors: [{be: 284.5, intensity: 12.3}],
    fitResult: {be: [284.123456789,285.123456789], bgIntensity: [1,2],
      fittedY: [12.3456789123,23.4567891234], chiReduced: 0.23,
      provenance: version ? {software: {numerical_version: version}} : null},
    historicalFits: [{reason: 'previous archive'}]};
}
for (const shape of ['DSG_LA','LACX','Voigt']) test(shape + ' legacy fit is deeply preserved, with no active mixed-version result', () => {
  const input = record(shape), before = plain(input);
  const migrated = c._preserveHistoricalNumericalFit(input);
  assert.equal(migrated.fitResult, null);
  assert.deepEqual(plain(input), before, 'input record is not mutated');
  assert.equal(migrated.historicalFits.length, 2);
  const history = migrated.historicalFits[1];
  for (const key of ['fitResult','peaks','ui','ccShift','manualAnchors']) assert.deepEqual(plain(history[key]), before[key], key);
  input.fitResult.fittedY[0] = 999; input.peaks[0].center = 999;
  input.manualAnchors[0].intensity = 999;
  assert.equal(history.fitResult.fittedY[0], before.fitResult.fittedY[0]);
  assert.equal(history.peaks[0].center, 284.5);
  assert.equal(history.manualAnchors[0].intensity, 12.3);
  assert.equal(c._preserveHistoricalNumericalFit(migrated), migrated, 'repeat load does not duplicate history');
});
test('same-version fitted record remains active and unchanged', () => {
  const input = record('DSG_LA', '2026.09-audit.1');
  assert.equal(c._preserveHistoricalNumericalFit(input), input);
});
test('a newer unknown numerical version is archived rather than silently reinterpreted', () => {
  const input = record('LACX', '2099.future');
  const migrated = c._preserveHistoricalNumericalFit(input);
  assert.equal(migrated.fitResult, null);
  assert.equal(migrated.historicalFits[1].sourceNumericalVersion, '2099.future');
});
test('unaffected lineshapes do not require a numerical migration', () => {
  const input = record('Gaussian');
  assert.equal(c._preserveHistoricalNumericalFit(input), input);
});
