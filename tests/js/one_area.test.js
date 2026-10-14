// ONE area definition (sealed-fit v6 Q5, owner 2026-10-12): every page reader of an area — Results,
// the sidebar and its support patching, Quantify, the CSV/XLSX export, Auto-Fit's 40 % graphite
// warning, the spectrum save — shows the SERVER's, |trapezoid(y, x)| on the fit grid
// (fitting.py individual_peaks[].params.area). The page's formula is pinned bit for bit to scipy's
// here; tests/js/lineshape_roundtrip.test.js pins the page's area to the server's for every lineshape.
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { runHelper } = require('./_helper_process.js');
const REPO_ROOT = path.join(__dirname, '../..');
const html = fs.readFileSync(path.join(REPO_ROOT, 'templates/index.html'), 'utf8');
const lines = html.split('\n');
function extractFn(name) {
  const start = lines.findIndex(l => new RegExp('^(async )?function ' + name + '\\(').test(l));
  assert.ok(start >= 0, name);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail('unbalanced ' + name);
}
const P = new Function(['_npPairwiseSum', '_trapezoidArea'].map(extractFn).join('\n') + '\nreturn { _trapezoidArea };')();
const PY = [path.join(REPO_ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3'].find(p => fs.existsSync(p)) || 'python3';

test('the page\'s trapezoid is scipy\'s, bit for bit, on every grid shape', () => {
  let s = 12345 >>> 0; const rnd = () => { s = (1664525 * s + 1013904223) >>> 0; return s / 4294967296; };
  const cases = [];
  for (const n of [2, 3, 7, 8, 9, 100, 128, 129, 241, 1001]) {
    const asc = Array.from({ length: n }, (_, i) => 280 + 0.05 * i);
    const irregular = []; let x = 280; for (let i = 0; i < n; i++) { irregular.push(x); x += 0.02 + 0.08 * rnd(); }
    const y = Array.from({ length: n }, () => 1e4 * rnd());
    cases.push({ x: asc, y }, { x: asc.slice().reverse(), y }, { x: irregular, y });
  }
  cases.push({ x: [0, 2, 1], y: [1, 1, 1] });          // the design memo's example: server 1 (rectangle 6, |dx| trapezoid 3)
  const script = 'import json, sys; from scipy.integrate import trapezoid; import numpy as np\n' +
    'print(json.dumps([float(abs(trapezoid(np.array(c["y"], dtype=float), np.array(c["x"], dtype=float)))) for c in json.load(sys.stdin)]))';
  const want = JSON.parse(runHelper(PY, ['-c', script], { input: JSON.stringify(cases), encoding: 'utf8', maxBuffer: 64 << 20 }));
  cases.forEach((c, k) => assert.strictEqual(P._trapezoidArea(c.y, c.x), want[k], `case ${k} (n = ${c.x.length})`));
  assert.strictEqual(P._trapezoidArea([1, 1, 1], [0, 2, 1]), 1);
  assert.strictEqual(P._trapezoidArea([5], [280]), 0, 'one point has no area');
});

test('the one grid: the fit\'s own energies while it is current (a restored fit\'s _modelBe first), else the live ROI grid', () => {
  const run = (fitResult, stats) => {
    const state = { fitResult, rawBE: [1, 2, 3] };
    return new Function('state', '_statsLiveState', 'getROIData', extractFn('_areaGrid') + '\n' + require('./_seal_readers.js')(extractFn) + '\nreturn _areaGrid;')(
      state, () => stats, () => ({ be: ['ROI'] , inten: [] }))();
  };
  assert.deepStrictEqual(run({ be: [1, 2, 3] }, 'current'), [1, 2, 3], 'a fresh fit: the energies it was fitted on');
  assert.deepStrictEqual(run({ be: [1, 2, 3], _modelBe: [1.0001, 2.0001, 3.0001] }, 'current'), [1.0001, 2.0001, 3.0001],
    'a restored fit: the energies the server evaluated and integrated its components on');
  for (const st of ['stale', 'unverified']) assert.deepStrictEqual(run({ be: [1, 2, 3], _modelBe: [1, 2] }, st), ['ROI'], st + ': the live grid');
  assert.deepStrictEqual(run(null, 'none'), ['ROI'], 'no fit: the live grid');
  assert.deepStrictEqual(run({ be: [1] }, 'current'), ['ROI'], 'a fit grid of one point is no grid');
});

test('every area reader integrates on the one grid (behaviour: tests/test_browser_one_area.py)', () => {
  assert.match(extractFn('_peakArea'), /return _trapezoidArea\(evalPeakArray\(be, p\), be\);/);
  assert.doesNotMatch(extractFn('_peakArea'), /\* step|reduce\(/, 'no rectangle sum left');
  // Results (and Quantify, which takes its areas), the sidebar, its support patching, the 40 % warning, the export
  for (const fn of ['renderResults', 'renderPeakList', '_patchPeakCardsForSupport', '_autoFitCheckGraphiteFraction', 'exportFitTable'])
    assert.match(extractFn(fn), /_areaGrid\(\)/, fn);
  assert.match(extractFn('renderResults'), /renderQuantify\(areas, totalArea\)/, 'Quantify takes Results\' areas');
  // the spectrum save: what Results shows; a restored fit saved unedited keeps its own record's area
  // (its components on the energies the server integrated them on) and adds the display value, labelled
  assert.match(html, /area: own \? _ownFitArea\(own, p, yArr\) : _peakArea\(p, _areaGrid\(\)\),\n\s+\.\.\.\(own \? \{ displayArea: _peakArea\(p, _areaGrid\(\)\),/);
  assert.doesNotMatch(html, /0\.5 \* \(yArr\[i - 1\] \+ y\) \* dx/, 'the save\'s own trapezoid is gone');
});

test('a restored fit\'s own area: the file\'s value verbatim, else the server\'s reported number, else computed (owner 2026-10-13)', () => {
  const f = new Function(['_npPairwiseSum', '_trapezoidArea', '_ownFitArea'].map(extractFn).join('\n') + '\nreturn _ownFitArea;')();
  const y = [1, 1, 1], g = [0, 1, 2];
  assert.strictEqual(f({ _savedPeakAreas: { 7: 1234.5678 }, _modelBe: g }, { id: 7, _backendParams: { area: { value: -99 } } }, y), 1234.5678, 'the file\'s own value, untouched');
  assert.strictEqual(f({ _savedPeakAreas: { 8: 1 }, _modelBe: g }, { id: 7, _backendParams: { area: { value: -99 } } }, y), 99, 'the server\'s number for that fit');
  assert.strictEqual(f({ _modelBe: g }, { id: 7 }, y), 2, 'neither: the server\'s formula on its energies');
  assert.strictEqual(f({ _savedPeakAreas: { 7: NaN }, _modelBe: g }, { id: 7 }, y), 2, 'a non-number is not a value');
});
