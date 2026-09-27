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
  'linearBackground', 'tougaardBackground', '_npPairwiseSum', '_npMean', '_applyEndpointAveraging', '_bgWindowIndices',
  'computeBackgroundCore',
].map(extractFn).join('\n') + '\nconst manualAnchorBackground = () => { throw new Error("not in this test"); };' +
  '\nreturn { computeBackgroundCore, _npMean };')();
const CONVERGED_ITER = 200;
const jsBg = (be, inten, method, nAvg) => JS.computeBackgroundCore(be, inten,
  { bgType: method, shirleyIter: String(CONVERGED_ITER), endpointAvg: String(nAvg), bgStart: '', bgEnd: '' });

const CASES = py({ mode: 'cases' });
const span = y => Math.max(...y) - Math.min(...y);
// a flat spectrum (span 0) is compared absolutely; a NaN anywhere fails
function maxRelDiff(a, b, sp) { let m = 0; for (let i = 0; i < a.length; i++) { const d = Math.abs(a[i] - b[i]); m = Number.isNaN(d) ? Infinity : Math.max(m, d); } return m / (sp || 1); }
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

// Codex round 1: data that dip below the baseline. With the clamp but the old
// zero start and index-linear fallback, the JS reached another fixed point
// (33–58 % of the span); fitting.py starts from the straight line and keeps it
// when no net signal is left. Exact small cases, every iteration count.
const BELOW = [
  { be: [0, 1, 2, 3, 4], inten: [10, 5, 5, 17, 20] },
  { be: [3.5, 1.1, 1, 0], inten: [6, 7, 13, 19] },
  { be: [3, 2, 1, 0], inten: [100, 107, 120, 127] },
  { be: [0, 1, 3, 6, 10], inten: [10, 5, 5, 17, 20] },
  // round 2: decimal endpoints — a start line one rounding step off the
  // endpoint left a residue that became the whole integral (50 % of the span)
  { be: [0, 1, 2], inten: [1.1, 0.5, 0.2] },
  { be: [2, 1, 0], inten: [0.2, 0.5, 1.1] },
  { be: [2, 1, 0], inten: [10.2, 4, 1.1] },
  { be: [0, 1, 2], inten: [1.1, 4, 10.2] },
  { be: [0.3, 0.7, 1.9, 2.2, 3.1], inten: [7.3, 2.1, 0.9, 3.3, 9.7] },
  { be: [3.1, 2.2, 1.9, 0.7, 0.3], inten: [9.7, 3.3, 0.9, 2.1, 7.3] },
];
// 5, 50 and 200 iterations, the same cap on both sides (fitting.py also stops
// at its 1e-6 tolerance; the UI's count against the server's is Part 5).
test('below-baseline data, integer and decimal, both directions: shirley, smart and smart_exp equal fitting.py at 5, 50 and 200 iterations (Codex rounds 1-2)', () => {
  for (const method of ['shirley', 'smart', 'smart_exp']) {
    for (const it of [5, 50, 200]) {
      const server = py({ mode: 'bg', items: BELOW.map(c => ({ method, be: c.be, inten: c.inten, n_avg: 1, n_iter: it })) });
      BELOW.forEach((c, k) => {
        const js = JS.computeBackgroundCore(c.be, c.inten, { bgType: method, shirleyIter: String(it), endpointAvg: '1', bgStart: '', bgEnd: '' });
        const rel = maxRelDiff(js, server[k], span(c.inten));
        assert.ok(rel <= TOL, `${method} ${JSON.stringify(c.be)} at ${it} iterations: ${rel.toExponential(2)} of the span (js ${js.map(v => v.toFixed(3))}, server ${server[k].map(v => v.toFixed(3))})`);
      });
    }
  }
});

test('KNOWN GAP (Task 4 cause 4, not this unit): linear interpolates by index on the page, by energy on the server — equal on uniform grids only', () => {
  const nonUniform = { be: [0, 1, 3], inten: [10, 20, 40] };
  const server = py({ mode: 'bg', items: [{ method: 'linear', be: nonUniform.be, inten: nonUniform.inten, n_avg: 1 }] })[0];
  const js = jsBg(nonUniform.be, nonUniform.inten, 'linear', 1);
  assert.ok(maxRelDiff(js, server, span(nonUniform.inten)) > 0.05, 'still differs on a non-uniform grid — if this starts failing the gap was closed; update the pin and CLAUDE.md');
});

test('KNOWN GAP (de-listed, not fixed): shirley_linear agrees on ascending grids and diverges on descending ones (Task 4 cause 3)', () => {
  const rows = compare('shirley_linear', 1);
  for (const r of rows.filter(r => /ascending/.test(r.label))) assert.ok(r.rel <= 1e-3, `${r.label}: ${r.rel}`);
  const desc = rows.filter(r => /descending/.test(r.label));
  assert.ok(desc.some(r => r.rel > 0.05), 'still diverges on descending grids: ' + desc.map(r => r.rel.toFixed(3)).join(', ') +
    ' — if this starts failing, the gap was closed; update the pin and CLAUDE.md');
  assert.match(html, /<option value="shirley_linear" disabled hidden/, 'shirley_linear stays de-listed (disabled, hidden; shown only for saved files that use it)');
});

test('randomised: 200 decimal spectra, uniform and non-uniform, both directions — shirley and smart equal fitting.py at convergence', () => {
  const cases = randomCases(20260927, 200, false);
  for (const method of ['shirley', 'smart']) {
    const server = py({ mode: 'bg', items: cases.map(c => ({ method, be: c.be, inten: c.inten, n_avg: 1 })) });
    cases.forEach((c, k) => {
      const js = jsBg(c.be, c.inten, method, 1);
      const rel = maxRelDiff(js, server[k], span(c.inten));
      assert.ok(rel <= TOL, `${method} case ${k} (n ${c.be.length}): ${rel.toExponential(2)} of the span`);
    });
  }
});

// Codex round 3: with endpoint averaging the page summed the endpoint values
// sequentially and numpy pairwise; one rounding step in an endpoint mean (0.1
// averaged to 0.09999999999999999) left a residue the iteration turned into a
// different fixed point — 62.5 % of the span (run A), 62.7 % on a 44-point
// decimal spectrum that has not converged by 200 iterations (run B). The page
// now sums like numpy (_npMean); compared at EQUAL iteration caps.
const ROUND3 = (() => {
  const a = { be: [...Array(24).keys(), ...Array(8).fill(23)], inten: [...Array(8).fill(0.1), ...Array(16).fill(0), ...Array(8).fill(3.2)] };
  a.inten[10] = 1.1;
  const b = {
    be: Array.from({ length: 44 }, (_, i) => 43 - i),
    inten: [6.2, 5.7, 5.4, 7.3, 10.5, 12, 12.7, 12.5, 15.6, 15.3, 18.5, 15.2, 15.2, 12.8, 15, 21.9, 16.4, 21.7, 18, 22.7,
      24.8, 26.9, 22.1, 27.5, 27.8, 28.8, 26.1, 33.1, 28.6, 33.6, 31.8, 35.5, 37.4, 38.8, 36.1, 37.4, 36.7, 37.1, 36.3, 40.1,
      43.1, 46, 48.3, 44.6],
  };
  const rev = c => ({ be: c.be.slice().reverse(), inten: c.inten.slice().reverse() });
  return [['run A (repeated energies)', a], ['run A reversed', rev(a)], ['run B (44 decimals)', b], ['run B reversed', rev(b)]];
})();
test('Codex round 3 reproducers, both directions: every averaged method equals fitting.py at endpoint average 10 and 1, 5, 50, 200 iterations', () => {
  for (const method of ['shirley', 'smart', 'smart_exp', 'tougaard']) {
    for (const it of [1, 5, 50, 200]) {
      const server = py({ mode: 'bg', items: ROUND3.map(([, c]) => ({ method, be: c.be, inten: c.inten, n_avg: 10, n_iter: it })) });
      ROUND3.forEach(([label, c], k) => {
        const js = JS.computeBackgroundCore(c.be, c.inten, { bgType: method, shirleyIter: String(it), endpointAvg: '10', bgStart: '', bgEnd: '' });
        const rel = maxRelDiff(js, server[k], span(c.inten));
        assert.ok(rel <= TOL, `${method} ${label} at ${it} iterations: ${rel.toExponential(2)} of the span`);
      });
    }
  }
});

test("_npMean is numpy's mean bit for bit (1–300 values, 1025 and 4097; decimals, wide magnitudes, near-cancelling sums)", () => {
  let seed = 7;
  const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
  const arrays = [];
  for (const n of [...Array.from({ length: 300 }, (_, i) => i + 1), 1025, 4097]) {
    const kind = n % 3;
    arrays.push(Array.from({ length: n }, () => kind === 0 ? Math.round(rnd() * 1e4) / 100
      : kind === 1 ? (rnd() - 0.5) * 10 ** Math.floor(rnd() * 12 - 3) : 1e7 + (rnd() - 0.5) * 1e5));
  }
  const want = py({ mode: 'mean', arrays });
  arrays.forEach((a, k) => assert.strictEqual(JS._npMean(a), want[k], `n ${a.length}`));
});

// This test also found the page's smart_exp 1.4 % of the span away at every
// averaging (a 1e-4 stop where fitting.py uses 1e-6, and a descending grid
// integrated from the other end); it now mirrors fitting.py too.
test('randomised with endpoint averaging 1, 3 and 10: 200 decimal spectra incl. flat decimal endpoint runs and repeated energies — every averaged method equals fitting.py', () => {
  const cases = randomCases(20260928, 200, true);
  for (const method of ['shirley', 'smart', 'smart_exp', 'tougaard']) {
    for (const nAvg of [1, 3, 10]) {
      const server = py({ mode: 'bg', items: cases.map(c => ({ method, be: c.be, inten: c.inten, n_avg: nAvg })) });
      cases.forEach((c, k) => {
        const js = jsBg(c.be, c.inten, method, nAvg);
        const rel = maxRelDiff(js, server[k], span(c.inten));
        assert.ok(rel <= TOL, `${method} n_avg ${nAvg} case ${k} (n ${c.be.length}): ${rel.toExponential(2)} of the span`);
      });
    }
  }
});

function randomCases(seed0, count, plateaus) {
  let seed = seed0;
  const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
  const cases = [];
  for (let c = 0; c < count; c++) {
    const n = 3 + Math.floor(rnd() * 40);
    let x = 0;
    const be = [], inten = [];
    for (let i = 0; i < n; i++) {
      x += c % 2 ? 0.1 + rnd() : 0.5;                    // odd cases: non-uniform steps
      be.push(Math.round(x * 1000) / 1000);
      inten.push(Math.round((5 + 20 * rnd() + (i === Math.floor(n / 2) ? 40 * rnd() : 0)) * 100) / 100);
    }
    if (plateaus && c % 3 === 0) {                       // flat decimal endpoint runs (0.1, 3.2, …: sums that round)
      const lo = Math.round(rnd() * 50) / 10, hi = Math.round(rnd() * 50) / 10, run = 1 + Math.floor(rnd() * 12);
      for (let i = 0; i < Math.min(run, n); i++) { inten[i] = lo; inten[n - 1 - i] = hi; }
    }
    if (plateaus && c % 5 === 1) {                       // repeated energies at the end (a flat run, grid stays monotone)
      const r = Math.min(n - 2, 1 + Math.floor(rnd() * 6));
      for (let i = n - r; i < n; i++) be[i] = be[n - r - 1];
    }
    if (c % 4 >= 2) { be.reverse(); inten.reverse(); }   // half descending
    cases.push({ be, inten });
  }
  return cases;
}
