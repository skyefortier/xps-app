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
  return new Function('_getManualAnchors', extractFn('linearBackground') + '\n' + extractFn('manualAnchorBackground') +
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
