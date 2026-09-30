// The page's de-listed shirley_linear twin against the statement in
// fitting.shirley_linear_background's docstring (background math foundation,
// Codex round 2): B = min(L + d(1 - F(B)), I), L the line between the averaged
// edge levels affine in the point INDEX, d = |b_low - b_high|, F the cumulative
// fraction of max(I - B, 0) from the low-BE edge. The page solves it on an
// ASCENDING grid only; it does not reverse a descending one, so there it
// accumulates from the other edge (the pinned page / server gap).
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
const shirleyLinearBackground = new Function(extractFn('shirleyLinearBackground') + '\nreturn shirleyLinearBackground;')();

// the statement, written independently, on the grid as ordered ASCENDING in energy
function residual(E, I, B, nAvg) {
  const asc = E[0] > E[E.length - 1];
  const x = asc ? [...E].reverse() : E, y = asc ? [...I].reverse() : I, b = asc ? [...B].reverse() : B;
  const n = y.length, cap = Math.max(1, Math.min(nAvg, Math.floor(n / 4)));
  const mean = a => a.reduce((s, v) => s + v, 0) / a.length;
  const bl = mean(y.slice(0, cap)), bh = mean(y.slice(n - cap)), d = Math.abs(bl - bh);
  const s = y.map((v, i) => Math.max(v - b[i], 0));
  const Q = [0];
  for (let i = 1; i < n; i++) Q.push(Q[i - 1] + 0.5 * (s[i - 1] + s[i]) * (x[i] - x[i - 1]));
  const span = Math.max(...y) - Math.min(...y);
  let r = 0;
  for (let i = 0; i < n; i++) {
    const U = bl + (bh - bl) * i / (n - 1) + d * (1 - Q[i] / Q[n - 1]);
    r = Math.max(r, Math.abs(b[i] - Math.min(U, y[i])) / span);
  }
  return r;
}

function spectrum(E) {
  const g = (c, w, h) => E.map(e => h * Math.exp(-4 * Math.LN2 * ((e - c) / w) ** 2));
  const a = g(284.5, 0.9, 20000), b = g(286.5, 1.3, 4000);
  return E.map((e, i) => 1000 + 3 * (e - 280) + a[i] + b[i] + (e > 285 ? 600 : 0));
}

test('on an ascending grid the page solves the stated equation (uniform and non-uniform, averaging 1 and 5)', () => {
  for (const E of [Array.from({ length: 241 }, (_, i) => 280 + 0.05 * i),
                   Array.from({ length: 160 }, (_, i) => 280 + 12 * (i / 159) ** 1.4)]) {
    const I = spectrum(E);
    for (const nAvg of [1, 5]) {
      const B = shirleyLinearBackground(E, I, 200, nAvg);
      assert.ok(residual(E, I, B, nAvg) < 1e-9, `residual ${residual(E, I, B, nAvg)}`);
    }
  }
});

test('on a descending grid it does not (the known page / server gap)', () => {
  const E = [4, 3, 2, 1, 0], I = [12, 25, 30, 20, 10];          // Codex round 2's example
  const B = shirleyLinearBackground(E, I, 200, 1);
  assert.ok(residual(E, I, B, 1) > 0.05, `residual ${residual(E, I, B, 1)}`);
});
