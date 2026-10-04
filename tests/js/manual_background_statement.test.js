// The page's manual background against its defining statement (background math
// foundation, 2026-09-30): the piecewise-affine curve through the anchors (sorted
// by energy), constant beyond the outermost ones — what the server computes with
// np.interp. With fewer than 2 anchors it falls back to linearBackground.
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
const lines = html.split('\n');
function extractFn(name) {
  const start = lines.findIndex(l => l.startsWith('function ' + name + '('));
  assert.ok(start >= 0, name);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
}
function make(anchors) {
  return new Function('_getManualAnchors', extractFn('linearBackground') + '\n' + extractFn('manualAnchorBackground') + '\n' + ['_bgExact', '_bgBitLen', '_bgRatToDouble', '_bgExactLevels', '_bgExactLine', '_bgRoundingWithin', '_bgPrecisionWords'].map(extractFn).join('\n') +
    '\nreturn { manualAnchorBackground, linearBackground };')(() => anchors);
}
function definition(be, anchors) {
  const a = [...anchors].sort((p, q) => p.x - q.x);
  return be.map(e => {
    if (e <= a[0].x) return a[0].y;
    if (e >= a[a.length - 1].x) return a[a.length - 1].y;
    let k = 0; while (!(e >= a[k].x && e <= a[k + 1].x)) k++;
    return a[k].y + (e - a[k].x) / (a[k + 1].x - a[k].x) * (a[k + 1].y - a[k].y);
  });
}

test('the manual background is the piecewise-affine curve through the anchors, constant outside', () => {
  const anchors = [{ x: 282.0, y: 1000 }, { x: 289.5, y: 1400 }, { x: 284.0, y: 1050 }, { x: 294.0, y: 1500 }];
  for (const be of [Array.from({ length: 321 }, (_, i) => 296 - 0.05 * i),                  // descending, uniform
                    Array.from({ length: 200 }, (_, i) => 296 - 16 * (i / 199) ** 1.7)]) {    // descending, non-uniform
    const { manualAnchorBackground } = make(anchors);
    const got = manualAnchorBackground(be, be.map(() => 5000));
    const want = definition(be, anchors);
    for (let i = 0; i < be.length; i++) assert.ok(Math.abs(got[i] - want[i]) < 1e-9, `at ${be[i]}: ${got[i]} vs ${want[i]}`);
  }
});

test('with fewer than two anchors the fallback is the page line (by index)', () => {
  const be = [296, 290, 286, 285, 280];
  const y = [1500, 1300, 2000, 1800, 1000];
  const { manualAnchorBackground, linearBackground } = make([{ x: 285, y: 1200 }]);
  assert.deepStrictEqual(manualAnchorBackground(be, y), linearBackground(be, y));
});

test("the manual background is the exact piecewise-affine value, correctly rounded — bit-identical to the server (Codex impl rounds 2, 9-10)", () => {
  const { execFileSync } = require('node:child_process');
  const PY = ['venv/bin/python3', '/Users/skyefortier/xps-app/venv/bin/python3'].map(p => path.join(__dirname, '../..', p)).concat(['/Users/skyefortier/xps-app/venv/bin/python3', 'python3'])
    .find(p => p === 'python3' || fs.existsSync(p));
  let seed = 11;
  const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
  const cases = [{ be: [0, 1, 3], anchors: [{ x: 0, y: 0 }, { x: 3, y: 1 }] }, { be: [0, 1, 2], anchors: [{ x: 0, y: 0.1 }, { x: 3, y: 3.2 }] }];
  for (let c = 0; c < 60; c++) {
    const n = 3 + Math.floor(rnd() * 30), be = Array.from({ length: n }, (_, i) => Math.round((296 - i * (0.05 + rnd() * 0.3)) * 1e4) / 1e4);
    const k = 2 + Math.floor(rnd() * 4), anchors = Array.from({ length: k }, () => ({ x: Math.round((be[n - 1] - 1 + rnd() * (be[0] - be[n - 1] + 2)) * 100) / 100, y: Math.round(rnd() * 5000) / 10 }));
    if (new Set(anchors.map(a => a.x)).size === k) cases.push({ be, anchors });
  }
  // numpy's edge branches (Codex impl round 5 probe): an exact anchor energy, an
  // overflowing slope (numpy recomputes a NaN from the right-hand anchor), agreeing duplicates
  // far and huge anchors (rounds 9-10: np.interp overflowed or cancelled to a finite 0;
  // exact evaluation gives the true value), extreme magnitudes, subnormals, ties
  cases.push({ be: [0, 5e-301, 1e-300, 2], anchors: [{ x: 0, y: -8e307 }, { x: 1e-300, y: 8e307 }, { x: 5, y: 1 }] });
  cases.push({ be: [0, 5e-301, 1e-300, 2], anchors: [{ x: 0, y: -1.7e308 }, { x: 1e-300, y: 1.7e308 }, { x: 5, y: 1 }] });
  const E11 = Array.from({ length: 11 }, (_, i) => 280 + i);
  cases.push({ be: E11, anchors: [{ x: -1e20, y: -1e20 }, { x: 300, y: 100 }] });
  cases.push({ be: E11, anchors: [{ x: -1e20, y: 1e20 }, { x: 300, y: 1 }] });
  cases.push({ be: E11, anchors: [{ x: -1e308, y: 0 }, { x: 1e308, y: 100 }] });
  cases.push({ be: [1e-320, 3e-320, 1e-310], anchors: [{ x: 0, y: 4e-323 }, { x: 1e-300, y: -4e-323 }] });
  cases.push({ be: [0.5, 1.5, 2.5], anchors: [{ x: 0, y: 0 }, { x: 4, y: 1 }] });
  // exact ties between two doubles: 1 + 2^-53 -> 1 (even), 1 + 1.5·2^-52 -> 1 + 2^-51 (even)
  cases.push({ be: [0.5], anchors: [{ x: 0, y: 1 }, { x: 1, y: 1 + 2 ** -52 }] });
  cases.push({ be: [0.5], anchors: [{ x: 0, y: 1 + 2 ** -52 }, { x: 1, y: 1 + 2 ** -51 }] });
  for (let c = 0; c < 40; c++) {
    const big = () => (rnd() < 0.5 ? -1 : 1) * Math.pow(10, -300 + rnd() * 608);
    const xs = Array.from({ length: 2 + Math.floor(rnd() * 4) }, big).sort((p, q) => p - q);
    if (new Set(xs).size !== xs.length) continue;
    const be = Array.from({ length: 6 }, () => xs[0] + rnd() * (xs[xs.length - 1] - xs[0]));
    if (!be.every(Number.isFinite)) continue;
    cases.push({ be, anchors: xs.map(x => ({ x, y: big() })) });
  }
  cases.push({ be: [0, 1, 2, 3], anchors: [{ x: 1, y: 4 }, { x: 2, y: 9 }] });
  cases.push({ be: [0, 1, 2, 3], anchors: [{ x: 0, y: 1 }, { x: 2, y: 5 }, { x: 2, y: 5 }, { x: 3, y: 2 }] });
  cases.push({ be: [0, 1e-320, 1], anchors: [{ x: 0, y: 1e308 }, { x: 1e-320, y: 1e308 }, { x: 1, y: 0 }] });
  const server = execFileSync(PY, ['-c', `import json,sys,numpy as np; sys.path.insert(0, ".")
out=[]
for c in json.load(sys.stdin):
    import fitting
    out.append([repr(float(v)) for v in fitting.manual_anchor_background(np.array(c['be'], float), [[p['x'], p['y']] for p in c['anchors']])])
print(json.dumps(out))`], { input: JSON.stringify(cases), encoding: 'utf8', cwd: path.join(__dirname, '../..') });
  const num = r => ({ inf: Infinity, '-inf': -Infinity, nan: NaN })[r] ?? Number(r);
  const S = JSON.parse(server).map(row => row.map(num));
  cases.forEach((c, k) => {
    const got = make(c.anchors).manualAnchorBackground(c.be, c.be.map(() => 1000));
    assert.deepStrictEqual(got, S[k], `case ${k}`);
  });
});
