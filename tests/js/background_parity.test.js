// Unit 4 (2026-09-27): the page's background twins against fitting.py — the
// curve the page draws, saves and fits locally against must be the one the
// server fits against. Task 4 (docs/superpowers/plans/2026-09-02-task4-
// background-twin-parity.md) measured the gaps and proved their causes;
// this unit fixes the two JS bugs it found and PINS the parity:
//   S4 shirley: the JS integrated the raw net signal, fitting.py max(y−B, 0)
//      (0.015–0.24 % of the span at convergence);
//   S5 smart at endpoint averaging > 1: the JS clamped against the averaged
//      copy, fitting.py against the raw data (up to 1 % of the span).
// shirley_linear is DE-LISTED (not offered): its order-sensitivity on
// descending grids (27–33 % of the span, Task 4 cause 3) is pinned as a KNOWN
// GAP, not fixed. Convergence semantics (the UI's Shirley iteration count vs
// the server's tolerance) are Part 5 of the sealed-fit-record memo, not this
// unit: the JS runs at a converged iteration count here.
//
// The JS runs computeBackgroundCore (the page's own dispatcher) extracted
// verbatim; the Python side calls fitting.py's own functions through
// tests/js/background_parity_backend.py.
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

const REPO_ROOT = path.join(__dirname, '../..');
const html = fs.readFileSync(path.join(REPO_ROOT, 'templates/index.html'), 'utf8');
const lines = html.split('\n');
function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name + '\\(');
  const start = lines.findIndex(l => re.test(l));
  assert.ok(start >= 0, `function ${name} not found`);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail('unbalanced ' + name);
}
const PYTHON = (() => {
  for (const c of [path.join(REPO_ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3']) {
    if (fs.existsSync(c)) return c;
  }
  return 'python3';
})();
const BRIDGE = path.join(__dirname, 'background_parity_backend.py');
const py = req => JSON.parse(execFileSync(PYTHON, [BRIDGE], { input: JSON.stringify(req), encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }));

const JS = new Function([
  'shirleyBackground', 'smartBackground', 'smartExperimentalBackground', 'shirleyLinearBackground',
  'linearBackground', 'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
].map(extractFn).join('\n') + '\nconst manualAnchorBackground = () => { throw new Error("not in this test"); };' +
  '\nreturn { computeBackgroundCore };')();
const CONVERGED_ITER = 200;
const jsBg = (be, inten, method, nAvg) => JS.computeBackgroundCore(be, inten,
  { bgType: method, shirleyIter: String(CONVERGED_ITER), endpointAvg: String(nAvg), bgStart: '', bgEnd: '' });

const CASES = py({ mode: 'cases' });
const span = y => Math.max(...y) - Math.min(...y);
function maxRelDiff(a, b, sp) { let m = 0; for (let i = 0; i < a.length; i++) m = Math.max(m, Math.abs(a[i] - b[i])); return m / sp; }
function compare(method, nAvg) {
  const py_out = py({ mode: 'bg', items: CASES.map(c => ({ method, be: c.be, inten: c.inten, n_avg: nAvg })) });
  return CASES.map((c, k) => ({ label: c.label, rel: maxRelDiff(jsBg(c.be, c.inten, method, nAvg), py_out[k], span(c.inten)) }));
}

test('the cases include the committed real U 4f scan, ascending and descending', () => {
  assert.ok(CASES.length >= 6, CASES.map(c => c.label).join('; '));
  assert.ok(CASES.some(c => /real U 4f/.test(c.label) && /descending/.test(c.label)));
});

// Parity tolerance: 1e-6 of the intensity span — far below Task 4's smallest
// measured gap (1.5e-4 of the span, the unclamped Shirley) and far above the
// difference between 200 JS iterations and the server's 1e-6-count stopping
// tolerance.
const TOL = 1e-6;
for (const method of ['shirley', 'smart', 'smart_exp', 'tougaard', 'linear']) {
  for (const nAvg of [1, 10]) {
    test(`${method}, endpoint average ${nAvg}: the page's background equals the server's within ${TOL} of the span on every case`, () => {
      for (const r of compare(method, nAvg)) assert.ok(r.rel <= TOL, `${r.label}: ${r.rel.toExponential(2)} of the span`);
    });
  }
}

test('KNOWN GAP (de-listed, not fixed): shirley_linear agrees on ascending grids and diverges on descending ones (Task 4 cause 3)', () => {
  const rows = compare('shirley_linear', 1);
  for (const r of rows.filter(r => /ascending/.test(r.label))) assert.ok(r.rel <= 1e-3, `${r.label}: ${r.rel}`);
  const desc = rows.filter(r => /descending/.test(r.label));
  assert.ok(desc.some(r => r.rel > 0.05), 'still diverges on descending grids: ' + desc.map(r => r.rel.toFixed(3)).join(', ') +
    ' — if this starts failing, the gap was closed; update the pin and CLAUDE.md');
  assert.match(html, /<option value="shirley_linear" disabled hidden/, 'shirley_linear stays de-listed (disabled, hidden; shown only for saved files that use it)');
});
