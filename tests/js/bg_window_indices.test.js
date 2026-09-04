// Background-window point-set contract (unit 1c of the sealed-fit-record
// design, docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md,
// round-5 amendment).
//
// The user types two binding energies; the preview background, the fit
// request, and the auto-fit request must all use the SAME set of grid points:
// every point with lo <= BE <= hi, inclusive at both ends (the rule
// getROIData already uses for the ROI). Before 1c the two request builders
// picked the nearest grid index per bound and the backend sliced
// end-exclusive, so the fit anchored one point inside the drawn window.
//
// Three invariants, each pinned here:
//   (1) _bgWindowIndices is the single definition of the window (unit tests);
//   (2) computeBackgroundCore's window IS the helper's window (behavioural);
//   (3) both request builders derive start_idx/end_idx from the helper and
//       send end_idx = i1 + 1 (structural — no nearest-index idiom remains).

const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(
  path.join(__dirname, '../../templates/index.html'), 'utf8');

function extract(name) {
  const m = html.match(new RegExp('function ' + name + '\\([\\s\\S]*?\\n\\}'));
  assert.ok(m, name + ' not found in templates/index.html');
  return m[0];
}

const _bgWindowIndices = eval('(' + extract('_bgWindowIndices') + ')');

function descending(hi, n, step) {
  const be = [];
  for (let i = 0; i < n; i++) be.push(Math.round((hi - i * step) * 1000) / 1000);
  return be;
}

// ── (1) helper unit tests ────────────────────────────────────────────────────

test('window at the ROI bounds covers every point, including the last one', () => {
  // 1-GTA U4f Scan_0: 350-pt descending grid 405.06 … 370.16, bounds 405.1 / 370.1
  const be = descending(405.06, 350, 0.1);
  assert.deepStrictEqual(_bgWindowIndices(be, '405.1', '370.1'), { i0: 0, i1: 349 });
});

test('off-grid bound inside the ROI never pulls in a point outside it', () => {
  // 1-GTA C1s Scan: grid 298.16 … 279.16 (191 pts); typed 279.2 lies between
  // 279.26 (in) and 279.16 (out). Nearest would have chosen 279.16.
  const be = descending(298.16, 191, 0.1);
  const w = _bgWindowIndices(be, '298.2', '279.2');
  assert.strictEqual(be[w.i1], 279.26);
  assert.strictEqual(w.i0, 0);
  assert.strictEqual(w.i1, 189);
});

test('bound order does not matter', () => {
  const be = descending(298.16, 191, 0.1);
  assert.deepStrictEqual(_bgWindowIndices(be, '279.2', '298.2'),
                         _bgWindowIndices(be, '298.2', '279.2'));
});

test('ascending grid gives the same point set as descending', () => {
  const be = descending(298.16, 191, 0.1).slice().reverse();
  const w = _bgWindowIndices(be, '298.2', '279.2');
  assert.strictEqual(be[w.i0], 279.26);
  assert.strictEqual(w.i1, 190);
});

test('blank or NaN bound falls back to the full range', () => {
  const be = descending(405.06, 350, 0.1);
  assert.deepStrictEqual(_bgWindowIndices(be, '', '370.1'), { i0: 0, i1: 349 });
  assert.deepStrictEqual(_bgWindowIndices(be, '405.1', 'abc'), { i0: 0, i1: 349 });
  assert.deepStrictEqual(_bgWindowIndices(be, NaN, NaN), { i0: 0, i1: 349 });
});

test('fewer than two points in range falls back to the full range', () => {
  const be = descending(405.06, 350, 0.1);
  assert.deepStrictEqual(_bgWindowIndices(be, '380.01', '380.09'), { i0: 0, i1: 349 }); // 0 points
  assert.deepStrictEqual(_bgWindowIndices(be, '380.05', '380.07'), { i0: 0, i1: 349 }); // 1 point (380.06)
});

test('exactly two points in range is a usable window', () => {
  const be = descending(405.06, 350, 0.1);
  const w = _bgWindowIndices(be, '380.05', '380.17');   // 380.16 and 380.06
  assert.strictEqual(w.i1 - w.i0, 1);
  assert.strictEqual(be[w.i0], 380.16);
  assert.strictEqual(be[w.i1], 380.06);
});

// ── (2) preview window == helper window (behavioural) ───────────────────────

test('computeBackgroundCore uses exactly the helper window', () => {
  // Evaluate the shipped computeBackgroundCore with a marker linearBackground:
  // inside the window the result equals the BE value, outside it is a flat
  // hold — so the positions where result[i] === be[i] ARE the window.
  const src = extract('computeBackgroundCore');
  const factory = new Function('_bgWindowIndices', 'linearBackground', 'manualAnchorBackground',
    'shirleyBackground', 'smartBackground', 'smartExperimentalBackground',
    'shirleyLinearBackground', 'tougaardBackground', '_applyEndpointAveraging',
    src + '\nreturn computeBackgroundCore;');
  const marker = (beSub) => beSub.slice();
  const unused = () => { throw new Error('unexpected background type call'); };
  const core = factory(_bgWindowIndices, marker, unused, unused, unused, unused, unused, unused, (y) => y);

  const be = descending(298.16, 191, 0.1);
  const inten = be.map(() => 1000);
  for (const [s, e] of [['298.2', '279.2'], ['290.0', '285.05'], ['', ''], ['380.01', '380.09']]) {
    const out = core(be, inten, { bgType: 'linear', shirleyIter: '5', endpointAvg: '1', bgStart: s, bgEnd: e });
    const w = _bgWindowIndices(be, s, e);
    const inWindow = [];
    for (let i = 0; i < be.length; i++) if (out[i] === be[i]) inWindow.push(i);
    assert.strictEqual(inWindow[0], w.i0, `i0 for bounds ${s}/${e}`);
    assert.strictEqual(inWindow[inWindow.length - 1], w.i1, `i1 for bounds ${s}/${e}`);
    assert.strictEqual(inWindow.length, w.i1 - w.i0 + 1, `contiguous window for ${s}/${e}`);
  }
});

// ── (3) request builders (structural) ───────────────────────────────────────

test('no request builder uses the old nearest-index idiom for the bg window', () => {
  const nearest = html.match(/Math\.abs\(v - bg(Start|End)\)/g) || [];
  assert.deepStrictEqual(nearest, [], 'nearest-index bg bound selection still present: ' + nearest.join(', '));
});

test('both /api/fit request builders send the inclusive window as end_idx = i1 + 1', () => {
  // Every bg payload in the page: { method: bgType, start_idx: <i0>, end_idx: <i1> + 1, ... }
  const payloads = html.match(/start_idx:\s*[^,]+,\s*end_idx:\s*[^,}]+/g) || [];
  assert.strictEqual(payloads.length, 2, 'expected exactly two bg payload sites (runFit + auto-fit), got: ' + JSON.stringify(payloads));
  for (const p of payloads) {
    assert.match(p, /end_idx:\s*\w+\.i1 \+ 1/, p);
    assert.match(p, /start_idx:\s*\w+\.i0/, p);
  }
  const calls = (html.match(/_bgWindowIndices\(/g) || []).length;
  // definition + computeBackgroundCore + runFit + auto-fit
  assert.ok(calls >= 4, '_bgWindowIndices should be defined and called from 3 sites, saw ' + calls);
});
