// Lineshape parity harness — the invariant that was missing until the
// 2026-08-30 asym-GL/LACX bug (see docs/autofit/codex/asym_gl_mismatch_*).
//
// Two DISTINCT invariants, both silently unchecked before this file:
//
//   (A) FRONTEND vs BACKEND: for every shape, the frontend's array evaluator
//       (evalPeakArray, called for chart data build paths) must numerically
//       match fitting.py's registered shape function (_SHAPE_FUNCS) over a
//       realistic BE grid and parameter sweep, including m>0 for the two
//       Gaussian-convolved shapes (DSG_LA, LACX). This is what asym-GL failed
//       — the frontend chart and the backend fit disagreed by ~10% of peak
//       height on real U 4f data.
//
//   (B) FRONTEND vs FRONTEND: the two JS evaluators for a single point,
//       evalPeak(x, p) and evalPeakArray(...)[i] at the same x, must agree
//       with each other. This is a SEPARATE bug class from (A) — even a
//       frontend that's perfectly correct vs. the backend can still disagree
//       with itself if it has two code paths computing "the same" curve.
//       This is exactly what the LACX per-point fallback did: evalPeak()
//       silently ignores Gaussian convolution (m) while evalPeakArray()
//       applies it correctly, so any evalPeak() caller — export/save/Results
//       panel — showed a materially different number than the chart.
//
// NOTE on (B)'s exact formulation: convolution is a GRID operation (it needs
// neighboring points to define a kernel), so it is not well-posed to ask for
// "the convolved value at an isolated point" via evalPeakArray([x], p)[0] —
// with only one point in the array, laTrueCasaXPS_array's own peak-finding +
// renormalization logic collapses to a degenerate constant (amplitude,
// trivially, for ANY x/alpha/beta) regardless of what evalPeak() does. That
// isn't a meaningful comparison for any shape, correct or not. Instead (B)
// asserts evalPeak(x, p) against evalPeakArray(realisticGrid, p)[indexOfX] —
// same real grid the chart/export code actually uses — which is the
// meaningful version of "do the two evaluators agree."

const { test } = require('node:test');
const assert = require('node:assert');
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');

const REPO_ROOT = path.join(__dirname, '../..');
const html = fs.readFileSync(path.join(REPO_ROOT, 'templates/index.html'), 'utf8');

function extract(re, name) {
  const m = html.match(re);
  assert.ok(m, name + ' not found in templates/index.html');
  return m[0];
}

// ── Extract the shipped lineshape block (gaussian … evalPeakArray) ─────────
const evalCtx = eval('(function(){\n'
  + extract(/function gaussian\(x, center, fwhm\) \{[\s\S]*?\nfunction evalPeakArray\(beArr, p\) \{[\s\S]*?\n\}/,
            'lineshape block') + '\n'
  + 'return { evalPeak, evalPeakArray };\n})()');
const { evalPeak, evalPeakArray } = evalCtx;

// ── Python bridge: call fitting.py's OWN _SHAPE_FUNCS, never a reimpl ──────
// A git-worktree checkout does NOT get its own venv/ (confirmed 2026-07-11,
// see memory xps-autofit-session-ops) — the venv only exists in the main
// repo checkout, so a worktree run must fall back to that absolute path.
function findPython() {
  const candidates = [
    process.env.XPS_PYTHON,
    path.join(REPO_ROOT, 'venv/bin/python3'),          // main checkout's own venv
    '/Users/skyefortier/xps-app/venv/bin/python3',      // worktree -> main repo venv
    'python3',
  ].filter(Boolean);
  for (const c of candidates) {
    try {
      if (c === 'python3' || fs.existsSync(c)) return c;
    } catch { /* keep looking */ }
  }
  return 'python3';
}
const PYTHON = findPython();
const BRIDGE = path.join(__dirname, 'lineshape_parity_backend.py');

function backendEval(shape, params, x) {
  const input = JSON.stringify({ shape, params, x });
  const out = execFileSync(PYTHON, [BRIDGE], { input, encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 });
  return JSON.parse(out);
}

// ── Realistic BE grid: 10 eV window, 0.05 eV step (200 pts) around center ──
function grid(center) {
  const x = [];
  for (let i = 0; i < 200; i++) x.push(center - 5.0 + 0.05 * i);
  return x;
}

function maxRelDiff(a, b, amplitude) {
  let m = 0;
  for (let i = 0; i < a.length; i++) m = Math.max(m, Math.abs(a[i] - b[i]));
  return m / amplitude;
}

// ── One representative peak per shape (distinctive, non-default values) ───
const AMPLITUDE = 17794.0;
const CENTER = 391.8;
const FWHM = 1.83;

function basePeak(shape) {
  return {
    id: 1, name: 'P', color: '#000', center: CENTER, amplitude: AMPLITUDE, fwhm: FWHM,
    shape,
    glMix: 55, asymmetry: 0.59,
    dsAlpha: 0.22, dsGamma: 0.05,
    laAlpha: 0.18, laBeta: 0.7, laM: 0.9,
    caAlpha: 1.4, caBeta: 0.8, caM: 50,
    linked: null, isChargeReference: false, visible: true,
  };
}

// backend shape id + kwargs builder per frontend shape
const BACKEND = {
  'Gaussian':   p => ({ shape: 'gaussian',       params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm } }),
  'Lorentzian': p => ({ shape: 'lorentzian',      params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm } }),
  'Voigt':      p => ({ shape: 'pseudo_voigt_gl', params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm, gl_ratio: 0.5 } }),
  'GL':         p => ({ shape: 'pseudo_voigt_gl', params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm, gl_ratio: p.glMix / 100 } }),
  'asym-GL':    p => ({ shape: 'asymmetric_gl',   params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm, asymmetry: p.asymmetry, gl_ratio: p.glMix / 100 } }),
  'DS':         p => ({ shape: 'doniach_sunjic',  params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm, alpha: p.dsAlpha, gamma_asym: p.dsGamma } }),
  'DSG_LA':     p => ({ shape: 'ds_g',            params: { amplitude: p.amplitude, center: p.center, alpha: p.laAlpha, beta: p.laBeta, m_gauss: p.laM } }),
  'LACX':       p => ({ shape: 'la_casaxps',      params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm, alpha: p.caAlpha, beta: p.caBeta, m: p.caM } }),
};

const TIGHT_TOL = 1e-6; // relative to amplitude; both sides are closed-form double-precision math

// ── (A) Frontend vs backend, shapes that must match tightly ───────────────
// Gaussian/Lorentzian/GL/Voigt/DS: no convolution, identical formulas on
// both sides — proven to agree by the earlier Codex sweep. asym-GL: fixed
// by unit-1 commit 1 (frontend rewritten to the backend's piecewise
// two-constant-width formula) — this assertion is what proves that fix.
for (const shape of ['Gaussian', 'Lorentzian', 'GL', 'Voigt', 'DS', 'asym-GL']) {
  test(`(A) frontend vs backend parity: ${shape}`, () => {
    const p = basePeak(shape);
    const x = grid(p.center);
    const jsY = evalPeakArray(x, p);
    const { shape: beShape, params } = BACKEND[shape](p);
    const beY = backendEval(beShape, params, x);
    const rel = maxRelDiff(jsY, beY, p.amplitude);
    assert.ok(rel < TIGHT_TOL,
      `${shape}: frontend vs backend max diff = ${(rel * 100).toFixed(4)}% of amplitude (tol ${TIGHT_TOL * 100}%)`);
  });
}

// ── (A) Frontend vs backend, shapes with a KNOWN, tracked residual ────────
// LACX and DSG_LA were BOTH suspected (2026-08-30 scoping) to share one root
// cause — a Gaussian-conv kernel-construction difference that should grow
// monotonically with m. An explicit m=0,1,2,5,10,50 sweep (see
// docs/autofit/codex git-archaeology notes / session record) DISPROVED that
// for DSG_LA: the two shapes have DIFFERENT, unrelated defects. Do not
// re-merge these into one explanation without re-running the sweep.
//
//   LACX: error GROWS with m as hypothesized (m=0: 0.0000%, m=1: 0.0000%,
//   m=2: 0.0001%, m=5: 0.0061%, m=10: 0.0312%, m=50: 0.1496% of amplitude) —
//   consistent with backend continuous-m + ceil(3.5*sigma) kernel vs
//   frontend rounded-m + 2m+1 kernel. Small, monotonic, unit-2 material.
//
//   DSG_LA: FIXED 2026-09-22 (unit fix-dsg-page-evaluator). The page's
//   evaluator used to be a numerical quadrature (laCasaXPS) whose step
//   resolved the Lorentzian core (β/3) but not the Gaussian kernel, so it
//   was wrong by up to 1e52 × amplitude at β = 2, m = 0.05 and by 4-14 % of
//   amplitude on the very box Find Peaks emits for a graphitic C 1s line
//   (β 0.05, α 0-0.3, m 0.4-1.8) — the A03 sweep, section (D) below. The
//   m < 0.001 delta branch (dsgDeltaKernel_array) had been mirrored in
//   2026-08; dsgConvolved_array now mirrors the server's padded-grid
//   convolution for every m (< 1e-6 of amplitude, measured ≤ 2e-14, across
//   the fitted box, every grid step, orientation and off-grid centre tested
//   below).
//
test('(A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization)', { todo: 'unit 2 fast-follow: LACX Gaussian-conv kernel mismatch vs backend, grows with m (~0.15% at m=50, measured 2026-08-30)' }, () => {
  const p = basePeak('LACX');
  const x = grid(p.center);
  const jsY = evalPeakArray(x, p);
  const { shape: beShape, params } = BACKEND.LACX(p);
  const beY = backendEval(beShape, params, x);
  const rel = maxRelDiff(jsY, beY, p.amplitude);
  assert.ok(rel < TIGHT_TOL,
    `LACX: frontend vs backend max diff = ${(rel * 100).toFixed(4)}% of amplitude (tol ${TIGHT_TOL * 100}%)`);
});

test('(A) frontend vs backend parity: LACX at m=0 (no convolution)', () => {
  const p = basePeak('LACX');
  p.caM = 0;
  const x = grid(p.center);
  const jsY = evalPeakArray(x, p);
  const { shape: beShape, params } = BACKEND.LACX(p);
  const beY = backendEval(beShape, params, x);
  const rel = maxRelDiff(jsY, beY, p.amplitude);
  assert.ok(rel < TIGHT_TOL,
    `LACX at m=0: frontend vs backend max diff = ${(rel * 100).toFixed(4)}% of amplitude (tol ${TIGHT_TOL * 100}%)`);
});

test('(A) frontend vs backend parity: DSG_LA at moderate m (FIXED 2026-09-22: grid-aware convolution, dsgConvolved_array)', () => {
  const p = basePeak('DSG_LA');
  const x = grid(p.center);
  const jsY = evalPeakArray(x, p);
  const { shape: beShape, params } = BACKEND.DSG_LA(p);
  const beY = backendEval(beShape, params, x);
  const rel = maxRelDiff(jsY, beY, p.amplitude);
  assert.ok(rel < TIGHT_TOL,
    `DSG_LA: frontend vs backend max diff = ${(rel * 100).toFixed(4)}% of amplitude (tol ${TIGHT_TOL * 100}%)`);
});

// FIXED (fix-dsgla-m0-collapse): for laM below the backend's 0.001 delta-
// kernel threshold (_ds_g_dscore_gauss, `m_gauss < 0.001` → normalised DS
// core, no convolution), evalPeakArray now takes a grid-aware branch that
// mirrors the backend EXACTLY, including its normalisation by
// np.interp(center, x, ds_core) ON THE DATA GRID — not the analytic core
// value at eps=0. The distinction matters when the fitted center falls
// BETWEEN grid points (~9.7e-4 of amplitude apart on a 0.05 eV grid,
// Codex run-A MAJOR on the first cut of this fix, which normalised
// analytically) — hence the centerOffset sweep below: 0 (on-grid) and
// 0.025 (half a grid step). Pre-fix baseline for context: the quadrature
// collapse made the curve vanish entirely (101.8% max diff at laM=0).
for (const laM of [0, 0.0009]) {
  for (const centerOffset of [0, 0.025]) {
    test(`(A) frontend vs backend parity: DSG_LA at m=${laM}, center ${centerOffset ? 'half-step off-grid' : 'on-grid'} (delta kernel)`, () => {
      const p = basePeak('DSG_LA');
      p.laM = laM;
      const x = grid(p.center);       // grid built around the ON-grid center
      p.center += centerOffset;       // then shift the peak off-grid
      const jsY = evalPeakArray(x, p);
      const { shape: beShape, params } = BACKEND.DSG_LA(p);
      const beY = backendEval(beShape, params, x);
      const rel = maxRelDiff(jsY, beY, p.amplitude);
      assert.ok(rel < TIGHT_TOL,
        `DSG_LA at m=${laM}, centerOffset=${centerOffset}: frontend vs backend max diff = ${(rel * 100).toFixed(4)}% of amplitude (tol ${TIGHT_TOL * 100}%)`);
    });
  }
}

// Same delta branch on a DESCENDING grid (real acquisitions descend): the
// backend delta branch reverses before np.interp; the JS mirror must too.
test('(A) frontend vs backend parity: DSG_LA at m=0, descending grid, off-grid center', () => {
  const p = basePeak('DSG_LA');
  p.laM = 0;
  const x = grid(p.center).reverse();
  p.center += 0.025;
  const jsY = evalPeakArray(x, p);
  const { shape: beShape, params } = BACKEND.DSG_LA(p);
  const beY = backendEval(beShape, params, x);
  const rel = maxRelDiff(jsY, beY, p.amplitude);
  assert.ok(rel < TIGHT_TOL,
    `DSG_LA m=0 descending off-grid: max diff = ${(rel * 100).toFixed(4)}% of amplitude`);
});

// ── (B) Frontend vs frontend: evalPeak(x,p) vs evalPeakArray(grid,p)[i] ────
// For every shape EXCEPT LACX, evalPeakArray falls through to
// `beArr.map(x => evalPeak(x, p))` — so this is trivially true by
// construction for those shapes; asserting it anyway locks in that
// structural fact (a future special-case added to evalPeakArray for another
// shape would have to keep it true, or this test catches the divergence
// immediately). LACX with m>0 is the one shape where evalPeakArray takes a
// genuinely different code path (laTrueCasaXPS_array, WITH convolution) than
// evalPeak (laTrueCasaXPS, WITHOUT convolution) — tracked as `todo` since
// unit 1/commit 2 reroutes evalPeak()'s CALLERS away from the bad path but
// does not change evalPeak()'s own (now-unreachable-from-shipped-code-paths)
// definition. See the (C) structural guard below for what actually closes
// this mechanism for real callers.
const ALL_SHAPES = ['Gaussian', 'Lorentzian', 'Voigt', 'GL', 'asym-GL', 'DS', 'DSG_LA', 'LACX'];
for (const shape of ALL_SHAPES) {
  const opts = shape === 'LACX' ? { todo: 'evalPeak() LACX branch ignores m; only its call sites are rerouted in unit-1 commit 2, not evalPeak() itself — see file header' }
    : shape === 'DSG_LA' ? { todo: 'evalPeak() DSG_LA branch is the normalised DS core with m IGNORED (the convolution is a grid operation, dsgConvolved_array via evalPeakArray); no shipped caller reaches it — guard (C)' } : undefined;
  test(`(B) evalPeak vs evalPeakArray agree pointwise: ${shape}`, opts, () => {
    const p = basePeak(shape);
    const x = grid(p.center);
    const arr = evalPeakArray(x, p);
    const idx = 130; // an arbitrary interior point, away from both edges and center
    const single = evalPeak(x[idx], p);
    const diff = Math.abs(single - arr[idx]) / p.amplitude;
    assert.ok(diff < TIGHT_TOL,
      `${shape} at x=${x[idx]}: evalPeak=${single}, evalPeakArray[i]=${arr[idx]}, rel diff=${(diff * 100).toFixed(4)}%`);
  });
}

// ── (C) Structural guard: evalPeak() must have no callers of its own ──────
// outside evalPeakArray()'s internal fallback. This is what actually closes
// the bug-(B) mechanism for shipped code: any FUTURE export/save/results
// function that calls evalPeak(...) directly instead of evalPeakArray(...)
// will silently reintroduce the LACX-ignores-convolution bug for that call
// site, exactly as happened in commits 8ff030e..5093487 (2026-04-25 through
// 2026-08-30, per docs/autofit/codex git-archaeology). This test makes that
// impossible to do silently.
test('(C) evalPeak() has no direct callers outside evalPeakArray()', () => {
  const evalPeakDef = extract(/function evalPeak\(x, p\) \{[\s\S]*?\n\}\n/, 'evalPeak definition');
  const evalPeakArrayDef = extract(/function evalPeakArray\(beArr, p\) \{[\s\S]*?\n\}\n/, 'evalPeakArray definition');
  assert.ok(/\bevalPeak\(x, p\)/.test(evalPeakArrayDef),
    'evalPeakArray() no longer contains its expected internal evalPeak() fallback call — update this test\'s assumption');
  const rest = html.split(evalPeakDef).join('\n').split(evalPeakArrayDef).join('\n');
  const strayCalls = [...rest.matchAll(/\bevalPeak\(/g)];
  assert.strictEqual(strayCalls.length, 0,
    `evalPeak() is called directly ${strayCalls.length} time(s) outside evalPeakArray() — route through evalPeakArray() ` +
    'instead (see file header: evalPeak() silently ignores Gaussian convolution for LACX with m>0, which evalPeakArray() ' +
    'handles correctly).');
});

// ── (D) A03 (2026-09-22): sweep each shape's FREE parameters across the ──
// ranges the FIT can reach. Every test above evaluates ONE base peak per
// shape; a divergence that only appears at the edge of a bound (η = 0 or 1,
// α at 0.5, a Gaussian kernel narrower than the quadrature step) was
// invisible to it. The ranges below are fitting.py `_make_peak_params`'s
// bounds for a free peak (gl_ratio 0–1, asymmetry 0–1, DS α 0–0.5 and
// γ 0–5, DS+G α 0–0.49 / β 0.05–2 / m 0.05–4, LA α,β 0.1–5 / m 0–499,
// fwhm 0.1–15) — what the OPTIMISER can reach. A lock can hold a value
// outside them (a held value is honoured as requested since A03 round 2;
// the round-trip harness covers those), a link follows its parent.
// One interpreter start per shape (the bridge accepts a list of specs).
//
// Measured on the first run of this sweep (worktree fix-voigt-eta-identity):
//   Gaussian, Lorentzian, Voigt, GL, asym-GL, DS: ≤ 6.1e-16 everywhere.
//   LACX, m = 0: exact. LACX, m > 0: up to 0.89 % of amplitude — the tracked
//     kernel-discretisation gap (continuous m + ceil(3.5σ) kernel on the
//     server vs rounded m + 2m+1 kernel on the page), largest where the
//     kernel is wide against the peak (m = 50 points on a 0.1 eV peak).
//   DSG_LA, m < 0.001: the delta branch, exact. DSG_LA, m ≥ 0.05: the page's
//     quadrature (laCasaXPS) sizes its step to resolve the Lorentzian core
//     (β/3) but NOT the Gaussian kernel (σ = m/2.355): at β = 2, m = 0.05
//     the step is 0.67 eV against σ = 0.021 eV, the kernel weights sample
//     nothing, and the curve is 1e52 × amplitude; at β = 0.7, m = 0.05 the
//     page's area is 23 % of the server's; at β = 2, m = 0.4 (the default
//     m) 64 %. Zero committed components use DS+G (0 of the 530 peak records
//     in the seven committed projects), so no saved
//     figure is affected today; it is the fit range nonetheless. Its own
//     unit (the file header already names it); recorded in
//     docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md.
function backendEvalMany(specs) {
  const input = JSON.stringify(specs);
  const out = execFileSync(PYTHON, [BRIDGE], { input, encoding: 'utf8', maxBuffer: 256 * 1024 * 1024 });
  return JSON.parse(out);
}
function combos(ranges) {
  let out = [{}];
  for (const k of Object.keys(ranges)) out = out.flatMap(o => ranges[k].map(v => ({ ...o, [k]: v })));
  return out;
}
const FWHM_RANGE = [0.1, 1.83, 15];
const SWEEP = {
  'Gaussian':   { fwhm: FWHM_RANGE },
  'Lorentzian': { fwhm: FWHM_RANGE },
  'Voigt':      { fwhm: FWHM_RANGE, glMix: [0, 100] },          // glMix must be IGNORED: Voigt is η = 0.5 (A03)
  'GL':         { glMix: [0, 25, 50, 75, 100], fwhm: FWHM_RANGE },
  'asym-GL':    { glMix: [0, 50, 100], asymmetry: [0, 0.5, 1], fwhm: FWHM_RANGE },
  'DS':         { dsAlpha: [0, 0.25, 0.5], dsGamma: [0, 1, 5], fwhm: FWHM_RANGE },
  'DSG_LA (delta kernel)': { laAlpha: [0, 0.25, 0.49], laBeta: [0.05, 0.7, 2], laM: [0, 0.0009] },
  'LACX (m = 0)': { caAlpha: [0.1, 1, 5], caBeta: [0.1, 1, 5], caM: [0], fwhm: FWHM_RANGE },
  // the full β/m box the optimiser can reach, incl. the corner that made the
  // old quadrature 1e52 × amplitude (β 2, m 0.05) and the delta threshold
  'DSG_LA (m > 0)': { laAlpha: [0, 0.25, 0.49], laBeta: [0.05, 0.7, 2], laM: [0.001, 0.05, 0.4, 2, 4] },
};
const SWEEP_KNOWN_GAP = {
  'LACX (m > 0)':   { caAlpha: [0.1, 1, 5], caBeta: [0.1, 1, 5], caM: [1, 5, 50, 499], fwhm: FWHM_RANGE },
};
function sweepShape(label) { return label.split(' ')[0]; }
// The backend parameters of the sweep come from the PAGE's request builder,
// not from a mapping of this file's own (Codex round 1: a mapping written
// here could not see `p.glMix || 50` sending an asym-GL mix of 0 as 50).
const _specState = { peaks: [] };
const { peakToBackendSpec } = new Function('state', 'getPeak',
  extract(/function peakToBackendSpec\(p\) \{[\s\S]*?\n\}\n/, 'peakToBackendSpec definition') + '\nreturn { peakToBackendSpec };')(_specState, id => _specState.peaks.find(q => q.id === id));
function backendParamsFromRequest(p) {
  const spec = peakToBackendSpec(p);
  const keep = spec.shape === 'ds_g' ? ['amplitude', 'center', 'alpha', 'beta', 'm_gauss']
    : ['amplitude', 'center', 'fwhm', 'gl_ratio', 'asymmetry', 'alpha', 'gamma_asym', 'beta', 'm'];
  const params = {};
  for (const k of keep) if (k in spec) params[k] = spec[k];
  return { shape: spec.shape, params };
}
function runSweep(label, ranges) {
  const shape = sweepShape(label);
  const cases = combos(ranges).map(c => ({ c, p: { ...basePeak(shape), ...c } }));
  const specs = cases.map(k => { const b = backendParamsFromRequest(k.p); return { ...b, x: grid(k.p.center) }; });
  const beYs = backendEvalMany(specs);
  return cases.map((k, i) => {
    const x = grid(k.p.center);
    const rel = maxRelDiff(evalPeakArray(x, k.p), beYs[i], k.p.amplitude);
    return { c: k.c, rel };
  }).sort((a, b) => b.rel - a.rel);
}
for (const [label, ranges] of Object.entries(SWEEP)) {
  test(`(D) sweep across the fitted range: ${label}`, () => {
    const worst = runSweep(label, ranges);
    assert.ok(worst[0].rel < TIGHT_TOL,
      `${label}: ${worst.filter(r => r.rel >= TIGHT_TOL).length} of ${worst.length} parameter combinations diverge; worst ` +
      `${(worst[0].rel * 100).toExponential(3)} % of amplitude at ${JSON.stringify(worst[0].c)}`);
  });
}
for (const [label, ranges] of Object.entries(SWEEP_KNOWN_GAP)) {
  test(`(D) sweep across the fitted range: ${label} — KNOWN GAP`, { todo: 'convolved shapes: LACX kernel discretisation (unit 2 / caM clamp); DSG_LA page quadrature step ignores the Gaussian kernel width (own unit)' }, () => {
    const worst = runSweep(label, ranges);
    assert.ok(worst[0].rel < TIGHT_TOL,
      `${label}: ${worst.filter(r => r.rel >= TIGHT_TOL).length} of ${worst.length} parameter combinations diverge; worst ` +
      `${(worst[0].rel * 100).toExponential(3)} % of amplitude at ${JSON.stringify(worst[0].c)}`);
  });
}

// ── (D′) DS+G convergence beyond the base grid (unit fix-dsg-page-evaluator) ──
// The convolution is a GRID operation: the server pads at the data step,
// builds its kernel on it and normalises at the interpolated centre. So the
// box is swept again on a coarser and a finer step, a DESCENDING grid (real
// acquisitions), a centre half a step off-grid, a short window, and a
// window narrower than the pad — every case at the 1e-6 tolerance.
function gridOf(center, step, n, { descending = false, offset = 0 } = {}) {
  const x = [];
  for (let i = 0; i < n; i++) x.push(center - (step * n) / 2 + step * i + offset);
  return descending ? x.reverse() : x;
}
const DSG_GRID_CASES = [
  { label: 'step 0.1 eV, 120 pts', step: 0.1, n: 120 },
  { label: 'step 0.02 eV, 500 pts', step: 0.02, n: 500 },
  { label: 'step 0.05 eV, descending', step: 0.05, n: 200, descending: true },
  { label: 'step 0.05 eV, centre half a step off-grid', step: 0.05, n: 200, offset: 0.025 },
  { label: 'step 0.1 eV, descending, centre 0.03 eV off-grid', step: 0.1, n: 120, descending: true, offset: 0.03 },
  { label: 'short window: 30 pts at 0.1 eV (narrower than the pad)', step: 0.1, n: 30 },
  { label: 'irregular-ish step 0.0503 eV (median step), 181 pts', step: 0.0503, n: 181 },
];
const DSG_BOX = { laAlpha: [0, 0.25, 0.49], laBeta: [0.05, 0.7, 2], laM: [0.001, 0.05, 0.4, 2, 4] };
for (const g of DSG_GRID_CASES) {
  test(`(D′) DS+G convolution converges on another grid: ${g.label}`, () => {
    const cases = combos(DSG_BOX).map(c => ({ c, p: { ...basePeak('DSG_LA'), ...c } }));
    const specs = cases.map(k => { const b = backendParamsFromRequest(k.p); return { ...b, x: gridOf(k.p.center, g.step, g.n, g) }; });
    const beYs = backendEvalMany(specs);
    const worst = cases.map((k, i) => ({ c: k.c, rel: maxRelDiff(evalPeakArray(specs[i].x, k.p), beYs[i], k.p.amplitude) })).sort((a, b) => b.rel - a.rel);
    assert.ok(worst[0].rel < TIGHT_TOL,
      `${g.label}: ${worst.filter(r => r.rel >= TIGHT_TOL).length} of ${worst.length} combinations diverge; worst ${(worst[0].rel * 100).toExponential(3)} % of amplitude at ${JSON.stringify(worst[0].c)}`);
  });
}

// ── (D″) DS+G: the cases Codex round 1 broke the first cut with, and the ──
// server's own degenerate zone. The first cut summed the convolution
// directly within 8 σ and clipped at the padded array's ends; the server's
// FFT is CIRCULAR, so a DS tail that reaches the far end wraps — visible
// with a centre outside the window (0.41 × amplitude off) and on a
// short irregular grid. _circularConvolve now does what the FFT does.
const DSG_REGRESSIONS = [
  { label: 'centre 10 eV outside a [−5, 5] window (a free DS+G centre has no window on the server)', x: Array.from({ length: 200 }, (_, i) => (i - 99.5) * 0.05), center: 10, laAlpha: 0.25, laBeta: 0.05, laM: 0.4 },
  { label: 'a 6-point irregular grid', x: [-3, -2.9, -2.8, 0, 2, 3], center: 0, laAlpha: 0.25, laBeta: 0.05, laM: 0.05 },
  { label: 'genuinely irregular steps (0.05 / 0.06 alternating; median ≠ mean)', x: (() => { const o = []; let v = 280; for (let i = 0; i < 200; i++) { o.push(v); v += i % 2 ? 0.06 : 0.05; } return o; })(), center: 285.3, laAlpha: 0.3, laBeta: 0.7, laM: 1.2 },
  { label: 'a 0.001 eV grid over 10 eV at the box corner β 2, m 4, α 0.49 (13 s per curve in the first cut)', x: Array.from({ length: 10001 }, (_, i) => 280 + 0.001 * i), center: 285, laAlpha: 0.49, laBeta: 2, laM: 4 },
  { label: 'a 2-point grid', x: [284.4, 284.6], center: 284.5, laAlpha: 0.2, laBeta: 0.3, laM: 0.4 },
  { label: 'a 1-point grid', x: [284.5], center: 284.5, laAlpha: 0.2, laBeta: 0.3, laM: 0.4 },
];
for (const c of DSG_REGRESSIONS) {
  test(`(D″) DS+G regression: ${c.label}`, () => {
    const p = { ...basePeak('DSG_LA'), amplitude: 1, center: c.center, laAlpha: c.laAlpha, laBeta: c.laBeta, laM: c.laM };
    const { shape, params } = backendParamsFromRequest(p);
    const beY = backendEval(shape, params, c.x);
    const t0 = Date.now();
    const jsY = evalPeakArray(c.x, p);
    const ms = Date.now() - t0;
    const rel = maxRelDiff(jsY, beY, 1);
    assert.ok(rel < TIGHT_TOL, `${c.label}: max diff ${rel.toExponential(3)} of amplitude (server max ${Math.max(...beY.map(Math.abs)).toExponential(2)})`);
    assert.ok(ms < 2000, `${c.label}: ${ms} ms for one curve — the cost must stay bounded (O(n log n))`);
  });
}

// KNOWN SERVER LIMIT (not this unit's to change; recorded for the owner):
// just above the 0.001 delta threshold the server's Gaussian kernel can
// UNDERFLOW on a coarse grid — σ = m/2.355 far below the step, so no
// padded-grid sample carries kernel weight (for an even padded length the
// nearest sample is half a step from the centre) — and the server returns
// an all-zero curve for the component. The page mirrors it exactly (a
// vanished curve drawn as vanished, never a curve the server did not fit).
// The zone closes quickly: at 0.1 eV, m = 0.02 is already ordinary.
for (const laM of [0.001, 0.002, 0.02, 0.05]) {
  test(`(D″) DS+G at m = ${laM} on a 0.1 eV grid: page equals server${laM <= 0.002 ? ' (both an all-zero curve — the server kernel underflows; known server limit)' : ''}`, () => {
    const x = Array.from({ length: 120 }, (_, i) => 290 - 0.1 * i);
    const p = { ...basePeak('DSG_LA'), amplitude: 1, center: 284.5, laAlpha: 0.25, laBeta: 0.7, laM };
    const { shape, params } = backendParamsFromRequest(p);
    const beY = backendEval(shape, params, x);
    const jsY = evalPeakArray(x, p);
    assert.ok(maxRelDiff(jsY, beY, 1) < TIGHT_TOL, `m = ${laM}: page vs server ${maxRelDiff(jsY, beY, 1).toExponential(3)}`);
    const serverMax = Math.max(...beY.map(Math.abs));
    if (laM <= 0.002) assert.equal(serverMax, 0, `m = ${laM}: the server curve is expected to vanish here (kernel underflow) — if it no longer does, the server changed; update this characterisation`);
    else assert.ok(serverMax > 0.9, `m = ${laM}: a real curve`);
  });
}
