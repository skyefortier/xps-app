// Local Levenberg–Marquardt: it must DESCEND and it must never present a
// non-converged attempt as a result (unit A0, 2026-09-15).
//
// Background: from the initial commit (f20d71b) until this unit, runFitLocal
// solved JᵀJ·dp = +Jᵀr with r = data − model, so every step was an ascent
// step, no step was ever accepted, and after 24 rejections λ passed 1e8 and
// the loop exited with the STARTING parameters, announced as "Fit complete
// (local LM)". Every Batch Fit called that path. The empirical proof is in
// docs/superpowers/plans/2026-09-15-a01-local-lm-proof.md; this file is
// that proof turned into a regression test on the SHIPPED functions.
//
// Everything under test is extracted verbatim from templates/index.html by
// function name (brace-matched) — the same functions the browser runs.

const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

const REPO_ROOT = path.join(__dirname, '../..');
const html = fs.readFileSync(path.join(REPO_ROOT, 'templates/index.html'), 'utf8');
const lines = html.split('\n');

function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name.replace(/\$/g, '\\$') + '\\(');
  const start = lines.findIndex(l => re.test(l));
  assert.ok(start >= 0, `function ${name} not found in templates/index.html`);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail(`unbalanced braces extracting ${name}`);
}

const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', 'dsgDeltaKernel_array',
  'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
  'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
  'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
  '_computeRFactor', '_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel', '_governingProvenance', '_localFitCaveat', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay', '_updateLocalModelBanner'];
const CAVEAT_CONST = (html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg) || []).join('\n');

// One isolated environment per test: a fresh `state`, a stub DOM, and the
// extracted functions bound to them.
function makeEnv() {
  const dom = {};
  const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, setAttribute() {}, removeAttribute() {},
    classList: { add() {}, remove() {}, contains: () => false } });
  const document = { getElementById: el, querySelectorAll: () => [] };
  const state = { peaks: [], fitResult: null, rawBE: [], rawIntensity: [], ccShift: 0 };
  const calls = { notify: [] };
  const notify = (msg, kind) => calls.notify.push({ msg, kind });
  const noop = () => {};
  const src = CAVEAT_CONST + '\n' + NAMES.map(extractFn).join('\n\n');
  const factory = new Function('document', 'state', 'notify', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_activeTab', '_escHtml', '_historyPreview', 'tabManager', '_updateRFactorUI', '_updateROIDisplay',
    'renderPeakList', 'updatePlot', 'renderResults', '_hideFitSpinner', '_autoSnapshot', 'manualAnchorBackground',
    src + '\nreturn { runFitLocal, computeBackgroundCore, evalAllPeaks, evalPeakArray, gaussian };');
  const fns = factory(document, state, notify, '', '', () => null, x => String(x), null, null, noop, noop, noop, noop, noop, noop, noop,
    be => new Array(be.length).fill(0));
  return { ...fns, state, dom, calls };
}

// ── Committed lab project, replayed exactly as runPropagation does ──────────
const PROJECT = path.join(REPO_ROOT, 'docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip');
const BatchPropagation = require(path.join(REPO_ROOT, 'static/js/batch_propagation.js'));

function loadProjectTabs() {
  const py = fs.existsSync(path.join(REPO_ROOT, 'venv/bin/python3')) ? path.join(REPO_ROOT, 'venv/bin/python3')
    : (fs.existsSync('/Users/skyefortier/xps-app/venv/bin/python3') ? '/Users/skyefortier/xps-app/venv/bin/python3' : 'python3');
  const script = 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; ' +
    'print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))';
  return JSON.parse(execFileSync(py, ['-c', script, REPO_ROOT, PROJECT], { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }));
}

function batchTarget(env, tabs, sourceName, targetName) {
  const src = tabs.find(t => t.name === sourceName), tgt = tabs.find(t => t.name === targetName);
  assert.ok(src && tgt, 'source/target tabs present in committed project');
  const scale = Math.max(...tgt.rawIntensity) / Math.max(...src.rawIntensity);
  const cloned = JSON.parse(JSON.stringify(src.peaks)).map(p => ({ ...p, amplitude: p.linked ? p.amplitude : p.amplitude * scale }));
  const ui = BatchPropagation.propagateFitUi({ ...src.ui }, { ...tgt.ui });
  const roiMin = parseFloat(ui.roiMin), roiMax = parseFloat(ui.roiMax);
  const be = [], inten = [];
  tgt.rawBE.forEach((b, i) => { const c = b - (src.ccShift || 0); if (c >= roiMin && c <= roiMax) { be.push(c); inten.push(tgt.rawIntensity[i]); } });
  const bg = env.computeBackgroundCore(be, inten, ui);
  const bgSub = inten.map((v, i) => v - bg[i]);
  env.state.peaks = cloned;
  env.state.fitResult = null;
  return { be, bgSub, bg, initial: JSON.parse(JSON.stringify(cloned)) };
}

// The objective the local engine minimises since unit W1: the Poisson-weighted
// sum of squares, w = 1/sqrt(max(raw counts, 1)), raw = bgSub + bg.
function residualSS(env, be, bgSub, bg) {
  const m = env.evalAllPeaks(be, env.state.peaks);
  return be.reduce((s, _, i) => { const raw = bgSub[i] + (bg ? bg[i] : 0); return s + (bgSub[i] - m[i]) ** 2 / Math.max(raw, 1); }, 0);
}

test('A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters', () => {
  const tabs = loadProjectTabs();
  for (const target of ['C1s Scan_0', 'C1s Scan_4', 'C1s Scan_8']) {
    const env = makeEnv();
    const { be, bgSub, bg, initial } = batchTarget(env, tabs, 'C1s Scan', target);
    const chi0 = residualSS(env, be, bgSub, bg);
    const out = env.runFitLocal(be, bgSub, bg);
    assert.ok(out && out.success === true, `${target}: runFitLocal must report success, got ${JSON.stringify(out)}`);
    const chi1 = residualSS(env, be, bgSub, bg);
    assert.ok(chi1 < 0.5 * chi0, `${target}: residual must drop substantially (before ${chi0.toExponential(3)}, after ${chi1.toExponential(3)})`);
    const moved = env.state.peaks.some((p, i) => Math.abs(p.center - initial[i].center) > 1e-3 || Math.abs(p.fwhm / initial[i].fwhm - 1) > 1e-3);
    assert.ok(moved, `${target}: at least one free centre/width must move — the shipped code returned the starting model on 18/18 targets`);
    assert.ok(env.state.fitResult && env.state.fitResult.status === 'converged', 'a converged local fit records status: converged');
  }
});

test('A01 replay: the linked U 4f pair also descends', () => {
  const tabs = loadProjectTabs();
  const env = makeEnv();
  const { be, bgSub, bg } = batchTarget(env, tabs, 'U4f Scan', 'U4f Scan_3');
  const chi0 = residualSS(env, be, bgSub, bg);
  const out = env.runFitLocal(be, bgSub, bg);
  assert.equal(out.success, true);
  assert.ok(residualSS(env, be, bgSub, bg) < 0.5 * chi0);
  const parent = env.state.peaks.find(p => !p.linked && p.shape === 'LACX');
  const child = env.state.peaks.find(p => p.linked);
  assert.ok(Math.abs(child.center - (parent.center + child.linkOffset)) < 1e-9, 'linked centre follows the parent');
  assert.ok(Math.abs(child.amplitude - parent.amplitude * child.linkRatio) < 1e-6, 'linked amplitude follows the parent');
});

test('noiseless Gaussian: amplitude 10 started at 5 is recovered', () => {
  const env = makeEnv();
  const be = Array.from({ length: 201 }, (_, i) => 280 + 0.05 * i);
  const truth = { id: 1, name: 'g', shape: 'Gaussian', center: 285.0, fwhm: 1.2, amplitude: 10, glMix: 50, asymmetry: 0 };
  const data = be.map(x => 10 * env.gaussian(x, 285.0, 1.2));
  env.state.peaks = [{ ...truth, center: 284.8, fwhm: 1.5, amplitude: 5 }];
  const out = env.runFitLocal(be, data, new Array(be.length).fill(0));
  assert.equal(out.success, true);
  const p = env.state.peaks[0];
  assert.ok(Math.abs(p.amplitude - 10) < 1e-3, `amplitude ${p.amplitude}`);
  assert.ok(Math.abs(p.center - 285.0) < 1e-4, `center ${p.center}`);
  assert.ok(Math.abs(p.fwhm - 1.2) < 1e-3, `fwhm ${p.fwhm}`);
  assert.ok(out.iterations > 1, 'a real descent takes more than one accepted step');
});

test('acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result', () => {
  const env = makeEnv();
  const be = Array.from({ length: 201 }, (_, i) => 280 + 0.05 * i);
  const data = be.map(x => 10 * env.gaussian(x, 285.0, 1.2));
  env.state.peaks = [{ id: 1, name: 'g', shape: 'Gaussian', center: 284.8, fwhm: 1.5, amplitude: 5, glMix: 50, asymmetry: 0 }];
  const previousFit = { chi: 123, chiReduced: 1.5, marker: 'previous' };
  env.state.fitResult = previousFit;
  const before = JSON.stringify(env.state.peaks);
  const out = env.runFitLocal(be, data, new Array(be.length).fill(0), { maxIterations: 1 });
  assert.equal(out.success, false, 'one iteration cannot converge from this start');
  assert.equal(JSON.stringify(env.state.peaks), before, 'peaks untouched on non-convergence');
  assert.strictEqual(env.state.fitResult, previousFit, 'previous fit result retained on non-convergence');
  assert.ok(env.calls.notify.some(n => n.kind === 'red' || n.kind === 'amber'), 'user is told the local fit did not converge');
});

test('a local fit result is Poisson-weighted: objective, weighting and the designated statistic text', () => {
  const env = makeEnv();
  const be = Array.from({ length: 201 }, (_, i) => 280 + 0.05 * i);
  const data = be.map(x => 10 * env.gaussian(x, 285.0, 1.2));
  env.state.peaks = [{ id: 1, name: 'g', shape: 'Gaussian', center: 284.8, fwhm: 1.5, amplitude: 5, glMix: 50, asymmetry: 0 }];
  const out = env.runFitLocal(be, data, new Array(be.length).fill(0));
  assert.equal(env.state.fitResult.objective, 'poisson_weighted_chi_square');
  assert.equal(env.state.fitResult.weighting, '1/sqrt(max(counts,1))');
  assert.equal(env.state.fitResult.engine, 'local');
  assert.equal(env.state.fitResult.reportable, false);
  assert.ok(Number.isFinite(out.chiReduced), 'the fitter returns its own chi-square');
  assert.match(env.dom['fit-quality'].textContent, /^\u03c7\u00b2\u1d63 = .* \(local, starting point\)$/, env.dom['fit-quality'].textContent);
});

// ── Codex round-1 findings (2026-09-15): bound stationarity and derivative accuracy ──

function gaussCase(env, { be, dataAmp, dataFwhm, dataCenter = 285.0, start }) {
  const data = be.map(x => dataAmp * env.gaussian(x, dataCenter, dataFwhm));
  env.state.peaks = [{ id: 1, name: 'g', shape: 'Gaussian', glMix: 50, asymmetry: 0, ...start }];
  return { data, bg: new Array(be.length).fill(0) };
}
const grid = (lo, hi, step) => Array.from({ length: Math.round((hi - lo) / step) + 1 }, (_, i) => lo + step * i);

test('bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall', () => {
  const env = makeEnv();
  const be = grid(280, 290, 0.05);
  const { data, bg } = gaussCase(env, { be, dataAmp: 10, dataFwhm: 1.2, start: { center: 285.0, fwhm: 1.2, amplitude: 1, fixCenter: true, fixFwhm: true } });
  const out = env.runFitLocal(be, data, bg);
  assert.equal(out.success, true);
  assert.ok(out.acceptedSteps > 0, 'must actually step off the wall');
  assert.ok(Math.abs(env.state.peaks[0].amplitude - 10) < 1e-3, `amplitude ${env.state.peaks[0].amplitude}`);
});

test('bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit', () => {
  // The floor is 0 since unit step (b) (owner decision: zero allowed in both
  // engines). Data pulling the amplitude NEGATIVE leave it on the wall at 0.
  const env = makeEnv();
  const be = grid(280, 290, 0.05);
  const { data, bg } = gaussCase(env, { be, dataAmp: -0.5, dataFwhm: 1.2, start: { center: 285.0, fwhm: 1.2, amplitude: 1, fixCenter: true, fixFwhm: true } });
  const out = env.runFitLocal(be, data, bg);
  assert.equal(out.success, true, JSON.stringify(out));
  assert.equal(env.state.peaks[0].amplitude, 0, 'stays on the wall');
});

test('a weak component the data DO hold is no longer forced up to an amplitude of 1', () => {
  const env = makeEnv();
  const be = grid(280, 290, 0.05);
  const { data, bg } = gaussCase(env, { be, dataAmp: 0.5, dataFwhm: 1.2, start: { center: 285.0, fwhm: 1.2, amplitude: 1, fixCenter: true, fixFwhm: true } });
  const out = env.runFitLocal(be, data, bg);
  assert.equal(out.success, true, JSON.stringify(out));
  assert.ok(Math.abs(env.state.peaks[0].amplitude - 0.5) < 1e-3, `amplitude ${env.state.peaks[0].amplitude}`);
});

test('derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)', () => {
  // Codex replay: model FWHM locked at 0.1, data FWHM 0.2, amplitude locked — the
  // forward difference h*max(1,|p|) = 0.0285 eV was coarser than the peak itself.
  for (const startCenter of [284.9, 285.02]) {
    const env = makeEnv();
    const be = grid(283, 287, 0.005);
    const { data, bg } = gaussCase(env, { be, dataAmp: 10, dataFwhm: 0.2, start: { center: startCenter, fwhm: 0.1, amplitude: 10, fixFwhm: true, fixAmplitude: true } });
    const out = env.runFitLocal(be, data, bg);
    assert.equal(out.success, true, JSON.stringify(out));
    assert.ok(Math.abs(env.state.peaks[0].center - 285.0) < 2e-4, `from ${startCenter}: centre ${env.state.peaks[0].center}`);
  }
});

test('derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum', () => {
  // Codex replay: data amplitude 5, FWHM 0.3 at 1000; model amplitude locked at 10.
  for (const startCenter of [999.8, 1000.2]) {
    const env = makeEnv();
    const be = grid(998, 1002, 0.005);
    const data = be.map(x => 5 * env.gaussian(x, 1000.0, 0.3));
    env.state.peaks = [{ id: 1, name: 'g', shape: 'Gaussian', glMix: 50, asymmetry: 0, center: startCenter, fwhm: 0.3, amplitude: 10, fixFwhm: true, fixAmplitude: true }];
    const out = env.runFitLocal(be, data, new Array(be.length).fill(0));
    assert.equal(out.success, true, JSON.stringify(out));
    assert.ok(Math.abs(env.state.peaks[0].center - 1000.0) < 2e-4, `from ${startCenter}: centre ${env.state.peaks[0].center}`);
  }
});

test('a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence', () => {
  const env = makeEnv();
  const be = grid(280, 290, 0.05);
  const data = be.map(x => 10 * env.gaussian(x, 285.0, 1.0));
  env.state.peaks = [{ id: 1, name: 'g', shape: 'Gaussian', glMix: 50, asymmetry: 0, center: 250.0, fwhm: 1.0, amplitude: 10, fixFwhm: true, fixAmplitude: true }];
  const out = env.runFitLocal(be, data, new Array(be.length).fill(0));
  assert.equal(out.success, false, 'the model has no measurable sensitivity here; declaring convergence would be the old defect in a new form');
  assert.equal(env.state.peaks[0].center, 250.0);
});

test('linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)', () => {
  const env = makeEnv();
  const be = grid(280, 300, 0.05);
  const data = be.map(x => 10 * env.gaussian(x, 285.0, 1.0) + 6 * env.gaussian(x, 291.0, 1.0));
  env.state.peaks = [
    { id: 1, name: 'p', shape: 'Gaussian', glMix: 50, asymmetry: 0, center: 284.7, fwhm: 1.0, amplitude: 5, fixFwhm: true },
    { id: 2, name: 'c', shape: 'Gaussian', glMix: 50, asymmetry: 0, center: 290.7, fwhm: 1.0, amplitude: 3, linked: 1, linkOffset: 6.0, linkRatio: 0.6 },
  ];
  const out = env.runFitLocal(be, data, new Array(be.length).fill(0));
  assert.equal(out.success, true, JSON.stringify(out));
  const [p, c] = env.state.peaks;
  assert.ok(Math.abs(p.center - 285.0) < 1e-3 && Math.abs(p.amplitude - 10) < 1e-2, `parent ${p.center} ${p.amplitude}`);
  assert.ok(Math.abs(c.center - (p.center + 6.0)) < 1e-9, 'child centre = parent + offset');
  assert.ok(Math.abs(c.amplitude - p.amplitude * 0.6) < 1e-9, 'child amplitude = parent x ratio');
  assert.equal(c.fwhm, p.fwhm, 'child width = parent width, locked parent included');
});

// ── Codex round-2 finding (2026-09-15): constrained stationarity oracle ──────
// A converged result must be a stationary point of the BOX-CONSTRAINED
// problem: no small feasible move of any free parameter reduces the residual.
const BOX = { fwhm: [0.1, 15], amplitude: [1, Infinity], glMix: [0, 100], asymmetry: [0, 1], dsAlpha: [0, 0.49],
  dsGamma: [0, 5], laAlpha: [0, 0.49], laBeta: [0.05, 2], laM: [0.05, 4], caAlpha: [0.1, 5], caBeta: [0.1, 5] };
function freeParamsOf(p) {
  const out = [];
  if (p.linked) return out;
  if (!p.fixCenter) out.push('center');
  if (!p.fixFwhm && p.shape !== 'DSG_LA') out.push('fwhm');
  if (!p.fixAmplitude) out.push('amplitude');
  if ((p.shape === 'GL' || p.shape === 'asym-GL') && !p.fixGlMix) out.push('glMix');
  if (p.shape === 'asym-GL' && !p.fixAsymmetry) out.push('asymmetry');
  if (p.shape === 'DS') { if (!p.fixDsAlpha) out.push('dsAlpha'); if (!p.fixDsGamma) out.push('dsGamma'); }
  if (p.shape === 'DSG_LA') { if (!p.fixLaAlpha) out.push('laAlpha'); if (!p.fixLaBeta) out.push('laBeta'); if (!p.fixLaM) out.push('laM'); }
  if (p.shape === 'LACX') { if (!p.fixCaAlpha) out.push('caAlpha'); if (!p.fixCaBeta) out.push('caBeta'); }
  return out;
}
const SYNC_KEYS = ['glMix','asymmetry','dsAlpha','dsGamma','laAlpha','laBeta','laM','caAlpha','caBeta','caM'];
function assertConstrainedStationary(env, be, bgSub, relTol, label, bg) {
  const ss = () => residualSS(env, be, bgSub, bg);
  const base = ss();
  for (const p of env.state.peaks) {
    for (const k of freeParamsOf(p)) {
      const scale = k === 'center' ? Math.max(0.05, p.fwhm) : Math.max(1, Math.abs(p[k]));
      const [lo, hi] = BOX[k] || [-Infinity, Infinity];
      for (const sgn of [-1, 1]) {
        const v0 = p[k];
        const v = Math.max(lo, Math.min(hi, v0 + sgn * 1e-3 * scale));
        if (v === v0) continue;
        p[k] = v;
        // linked children follow the parent, as in the optimiser
        for (const q of env.state.peaks) if (q.linked === p.id) { q.center = p.center + q.linkOffset; q.amplitude = p.amplitude * q.linkRatio; q.fwhm = p.fwhm; for (const kk of SYNC_KEYS) if (p[kk] !== undefined) q[kk] = p[kk]; }
        const trial = ss();
        p[k] = v0;
        for (const q of env.state.peaks) if (q.linked === p.id) { q.center = p.center + q.linkOffset; q.amplitude = p.amplitude * q.linkRatio; q.fwhm = p.fwhm; for (const kk of SYNC_KEYS) if (p[kk] !== undefined) q[kk] = p[kk]; }
        assert.ok(trial >= base * (1 - relTol), `${label}: moving ${p.name}.${k} by ${sgn}×1e-3 reduces SS ${base.toExponential(6)} → ${trial.toExponential(6)} (${((1 - trial / base) * 100).toFixed(4)} %) — not a constrained stationary point`);
      }
    }
  }
}

test('round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point', () => {
  const env = makeEnv();
  const be = grid(283, 287, 0.01);
  const data = be.map(x => 1 * env.gaussian(x, 285.0, 0.3));
  env.state.peaks = [{ id: 1, name: 'g', shape: 'Gaussian', glMix: 50, asymmetry: 0, center: 284.0, fwhm: 0.3, amplitude: 1 }];
  const out = env.runFitLocal(be, data, new Array(be.length).fill(0));
  if (out.success) assertConstrainedStationary(env, be, data, 1e-8, 'replay A');
  else assert.ok(/stall|sensitivity|iteration/i.test(out.message), out.message);
});

test('round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum', () => {
  const env = makeEnv();
  const be = grid(283, 287, 0.01);
  // Floor 0 since unit step (b): a NEGATIVE feature pins the amplitude on the
  // wall at 0; the width must still reach its constrained optimum there.
  const data = be.map(x => -0.5 * env.gaussian(x, 285.0, 1.0) + 0.02 * env.gaussian(x, 285.0, 0.3));
  env.state.peaks = [{ id: 1, name: 'g', shape: 'Gaussian', glMix: 50, asymmetry: 0, center: 285.0, fwhm: 1.5, amplitude: 5, fixCenter: true }];
  const out = env.runFitLocal(be, data, new Array(be.length).fill(0));
  assert.equal(out.success, true, JSON.stringify(out));
  assert.equal(env.state.peaks[0].amplitude, 0, 'amplitude on its wall');
  assertConstrainedStationary(env, be, data, 1e-8, 'replay B');
});

test('round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)', () => {
  const env = makeEnv();
  const be = grid(283, 287, 0.01);
  const data = be.map(x => 1 * env.gaussian(x, 285.0, 0.3));
  env.state.peaks = [{ id: 1, name: 'g', shape: 'Gaussian', glMix: 50, asymmetry: 0, center: 284.0, fwhm: 0.5, amplitude: 1 }];
  const out = env.runFitLocal(be, data, new Array(be.length).fill(0));
  if (out.success) assertConstrainedStationary(env, be, data, 1e-8, 'replay A/0.5');
});

test('A01 replay targets converge to constrained stationary points (C1s and U 4f)', () => {
  const tabs = loadProjectTabs();
  for (const [srcName, target] of [['C1s Scan', 'C1s Scan_0'], ['C1s Scan', 'C1s Scan_4'], ['C1s Scan', 'C1s Scan_8'], ['U4f Scan', 'U4f Scan_3'], ['U4f Scan', 'U4f Scan_6']]) {
    const env = makeEnv();
    const { be, bgSub, bg } = batchTarget(env, tabs, srcName, target);
    const out = env.runFitLocal(be, bgSub, bg);
    assert.equal(out.success, true, `${target}: ${JSON.stringify(out)}`);
    assertConstrainedStationary(env, be, bgSub, 1e-6, target, bg);
  }
});


// ── Codex round-3 reproductions (2026-09-15) ────────────────────────────────

test('round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen', () => {
  const env = makeEnv();
  const be = grid(280, 300, 0.05);
  const data = be.map(x => 100000 * env.gaussian(x, 285.0, 1.0) + 1000 * env.gaussian(x, 295.0, 1.0));
  env.state.peaks = [
    { id: 1, name: 'main', shape: 'Gaussian', glMix: 50, asymmetry: 0, center: 285.0, fwhm: 1.0, amplitude: 100000 },
    { id: 2, name: 'satellite', shape: 'Gaussian', glMix: 50, asymmetry: 0, center: 295.0, fwhm: 1.0, amplitude: 1 },
  ];
  const out = env.runFitLocal(be, data, new Array(be.length).fill(0));
  assert.equal(out.success, true, JSON.stringify(out));
  assert.ok(Math.abs(env.state.peaks[1].amplitude - 1000) < 1, `satellite amplitude ${env.state.peaks[1].amplitude}`);
  assertConstrainedStationary(env, be, data, 1e-8, 'A1');
});

test('round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude', () => {
  const env = makeEnv();
  const be = grid(280, 295, 0.01);
  const data = be.map(x => 100000 * env.gaussian(x, 285.0, 1.0) + 10 * env.gaussian(x, 290.0, 1.0));
  env.state.peaks = [
    { id: 1, name: 'main', shape: 'Gaussian', glMix: 50, asymmetry: 0, center: 285.0, fwhm: 1.0, amplitude: 100000, fixCenter: true, fixFwhm: true },
    { id: 2, name: 'satellite', shape: 'Gaussian', glMix: 50, asymmetry: 0, center: 290.0, fwhm: 1.0, amplitude: 5, fixCenter: true, fixFwhm: true },
  ];
  const out = env.runFitLocal(be, data, new Array(be.length).fill(0));
  assert.equal(out.success, true, JSON.stringify(out));
  assert.ok(Math.abs(env.state.peaks[1].amplitude - 10) < 1e-2, `satellite amplitude ${env.state.peaks[1].amplitude}`);
  assertConstrainedStationary(env, be, data, 1e-8, 'B1');
});

test('round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point', () => {
  const env = makeEnv();
  const be = grid(283, 287, 0.01);
  const data = be.map(x => 0.1 * env.gaussian(x, 285.0, 1.5));
  env.state.peaks = [{ id: 1, name: 'g', shape: 'Gaussian', glMix: 50, asymmetry: 0, center: 285.3, fwhm: 1.0, amplitude: 8 }];
  const out = env.runFitLocal(be, data, new Array(be.length).fill(0));
  if (out.success) assertConstrainedStationary(env, be, data, 1e-6, 'A2');
});

test('round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point', () => {
  const env = makeEnv();
  const be = grid(283, 287, 0.01);
  const data = be.map(x => 5 * env.gaussian(x, 285.0, 1.5));
  env.state.peaks = [{ id: 1, name: 'g', shape: 'Gaussian', glMix: 50, asymmetry: 0, center: 286.0, fwhm: 0.3, amplitude: 20, fixFwhm: true }];
  const out = env.runFitLocal(be, data, new Array(be.length).fill(0));
  assert.equal(out.success, true, JSON.stringify(out));
  assertConstrainedStationary(env, be, data, 1e-6, 'B2');
});

// ── Codex round-4 reproductions (2026-09-15): the tiny-residual exits must also be certified ──

test('round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)', () => {
  for (const startCenter of [280.0, 280.5]) {
    const env = makeEnv();
    const be = grid(283, 287, 0.01);
    const data = new Array(be.length).fill(0);
    env.state.peaks = [{ id: 1, name: 'g', shape: 'Gaussian', glMix: 50, asymmetry: 0, center: startCenter, fwhm: 1.0, amplitude: 1, fixFwhm: true, fixAmplitude: true }];
    const out = env.runFitLocal(be, data, new Array(be.length).fill(0));
    if (out.success) assertConstrainedStationary(env, be, data, 1e-6, `zero-data from ${startCenter}`);
  }
});

test('round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)', () => {
  for (const [center, dataAmp] of [[287, 2], [286, 3]]) {
    const env = makeEnv();
    const be = grid(280, 281, 0.05);
    const data = be.map(x => dataAmp * env.gaussian(x, center, 2.0));
    env.state.peaks = [{ id: 1, name: 'g', shape: 'Gaussian', glMix: 50, asymmetry: 0, center, fwhm: 2.0, amplitude: 1, fixCenter: true, fixFwhm: true }];
    const out = env.runFitLocal(be, data, new Array(be.length).fill(0));
    if (out.success) assertConstrainedStationary(env, be, data, 1e-6, `tiny residual centre ${center}`);
  }
});

// ── Codex round-5 reproduction (2026-09-15): the certificate scale must not read a stale working width ──
test('round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one', () => {
  const env = makeEnv();
  const be = grid(-50, 50, 0.1);
  const data = be.map(x => 1.28063417 * env.gaussian(x, -11.999999, 15.0) + 1.28063417 * env.gaussian(x, 12.000001, 15.0));
  env.state.peaks = [{ id: 1, name: 'g', shape: 'Gaussian', glMix: 50, asymmetry: 0, center: 0.0, fwhm: 15.0, amplitude: 1, fixAmplitude: true }];
  const out = env.runFitLocal(be, data, new Array(be.length).fill(0));
  if (out.success) assertConstrainedStationary(env, be, data, 1e-6, 'round-5');
});


// ── Unit W1 (2026-09-18): the local engine is Poisson-weighted like the server ──
test('weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one', () => {
  const env = makeEnv();
  const be = grid(280, 290, 0.05);
  const g = be.map(x => env.gaussian(x, 285.0, 1.5));
  // data = 1000 * g plus a deliberate misfit on the high-count core, so that weighting changes the answer
  const data = be.map((x, i) => 1000 * g[i] * (Math.abs(x - 285) < 0.4 ? 1.30 : 1.0) + 5);
  const bg = new Array(be.length).fill(0);
  env.state.peaks = [{ id: 1, name: 'g', shape: 'Gaussian', glMix: 50, asymmetry: 0, center: 285.0, fwhm: 1.5, amplitude: 800, fixCenter: true, fixFwhm: true }];
  const out = env.runFitLocal(be, data, bg);
  assert.equal(out.success, true, JSON.stringify(out));
  const w2 = data.map(v => 1 / Math.max(v, 1));
  const aW = data.reduce((s, d, i) => s + w2[i] * d * g[i], 0) / g.reduce((s, gi, i) => s + w2[i] * gi * gi, 0);
  const aU = data.reduce((s, d, i) => s + d * g[i], 0) / g.reduce((s, gi) => s + gi * gi, 0);
  assert.ok(Math.abs(aW / aU - 1) > 0.01, `the construction must separate the two solutions (weighted ${aW}, unweighted ${aU})`);
  assert.ok(Math.abs(env.state.peaks[0].amplitude / aW - 1) < 1e-5, `amplitude ${env.state.peaks[0].amplitude} vs weighted closed form ${aW} (unweighted would be ${aU})`);
});

test('server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)', () => {
  const tabs = loadProjectTabs();
  const bridge = path.join(__dirname, 'local_lm_server_parity_backend.py');
  const py = fs.existsSync(path.join(REPO_ROOT, 'venv/bin/python3')) ? path.join(REPO_ROOT, 'venv/bin/python3')
    : (fs.existsSync('/Users/skyefortier/xps-app/venv/bin/python3') ? '/Users/skyefortier/xps-app/venv/bin/python3' : 'python3');
  for (const target of ['C1s Scan_0', 'C1s Scan_5']) {
    const env = makeEnv();
    const { be, bgSub, bg, initial } = batchTarget(env, tabs, 'C1s Scan', target);
    const src = tabs.find(t => t.name === 'C1s Scan'), tgt = tabs.find(t => t.name === target);
    const ui = BatchPropagation.propagateFitUi({ ...src.ui }, { ...tgt.ui });
    const out = env.runFitLocal(be, bgSub, bg);
    assert.equal(out.success, true, JSON.stringify(out));
    const inten = bgSub.map((v, i) => v + bg[i]);
    const server = JSON.parse(execFileSync(py, [bridge, REPO_ROOT], { input: JSON.stringify({ be, inten, peaks: initial, ui }), encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 }));
    assert.equal(server.success, true);
    assert.ok(Math.abs(out.chiReduced / server.chi2r - 1) < 0.01, `${target}: chi2r local ${out.chiReduced} vs server ${server.chi2r}`);
    env.state.peaks.forEach((p, i) => {
      const q = server.peaks[i];
      assert.ok(Math.abs(p.center - q.center) < 0.010, `${target} ${p.name}: centre ${p.center} vs server ${q.center}`);
      assert.ok(Math.abs(p.fwhm / q.fwhm - 1) < 0.01, `${target} ${p.name}: fwhm ${p.fwhm} vs server ${q.fwhm}`);
      assert.ok(Math.abs(p.amplitude / q.amplitude - 1) < 0.01, `${target} ${p.name}: amplitude ${p.amplitude} vs server ${q.amplitude}`);
    });
  }
});

// ── W1 Codex round 1: a never-optimised parameter (integer-clamped caM) is not a degree of freedom ──
test('reduced chi-square does not count the held caM as a varied parameter', () => {
  const run = (fixCaM) => {
    const env = makeEnv();
    const be = grid(280, 282, 0.1);
    const truth = { id: 1, name: 'la', shape: 'LACX', center: 281.0, fwhm: 1.0, amplitude: 50, caAlpha: 1.2, caBeta: 1.5, caM: 6, glMix: 50, asymmetry: 0 };
    env.state.peaks = [{ ...truth }];
    const data = env.evalAllPeaks(be, env.state.peaks).map((v, i) => v * (1 + 0.05 * Math.sin(3 * i)) + 20);
    env.state.peaks = [{ ...truth, amplitude: 40, fixCenter: true, fixFwhm: true, fixCaAlpha: true, fixCaBeta: true, fixCaM }];
    const out = env.runFitLocal(be, data.map(v => v - 20), new Array(be.length).fill(20));
    assert.equal(out.success, true, JSON.stringify(out));
    return { chi: env.state.fitResult.chi, chiReduced: out.chiReduced, amp: env.state.peaks[0].amplitude };
  };
  const a = run(true), b = run(false);
  assert.ok(Math.abs(a.amp - b.amp) < 1e-9 && Math.abs(a.chi - b.chi) < 1e-9, 'identical fit either way');
  assert.ok(Math.abs(a.chiReduced - b.chiReduced) < 1e-12, `same fit, same reduced chi-square: ${a.chiReduced} vs ${b.chiReduced}`);
});
