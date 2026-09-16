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
  '_computeRFactor'];

// One isolated environment per test: a fresh `state`, a stub DOM, and the
// extracted functions bound to them.
function makeEnv() {
  const dom = {};
  const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', setAttribute() {}, removeAttribute() {},
    classList: { add() {}, remove() {}, contains: () => false } });
  const document = { getElementById: el, querySelectorAll: () => [] };
  const state = { peaks: [], fitResult: null, rawBE: [], rawIntensity: [], ccShift: 0 };
  const calls = { notify: [] };
  const notify = (msg, kind) => calls.notify.push({ msg, kind });
  const noop = () => {};
  const src = NAMES.map(extractFn).join('\n\n');
  const factory = new Function('document', 'state', 'notify', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_updateRFactorUI', '_updateROIDisplay',
    'renderPeakList', 'updatePlot', 'renderResults', '_hideFitSpinner', '_autoSnapshot', 'manualAnchorBackground',
    src + '\nreturn { runFitLocal, computeBackgroundCore, evalAllPeaks, evalPeakArray, gaussian };');
  const fns = factory(document, state, notify, '', '', noop, noop, noop, noop, noop, noop, noop,
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

function residualSS(env, be, bgSub) {
  const m = env.evalAllPeaks(be, env.state.peaks);
  return be.reduce((s, _, i) => s + (bgSub[i] - m[i]) ** 2, 0);
}

test('A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters', () => {
  const tabs = loadProjectTabs();
  for (const target of ['C1s Scan_0', 'C1s Scan_4', 'C1s Scan_8']) {
    const env = makeEnv();
    const { be, bgSub, bg, initial } = batchTarget(env, tabs, 'C1s Scan', target);
    const chi0 = residualSS(env, be, bgSub);
    const out = env.runFitLocal(be, bgSub, bg);
    assert.ok(out && out.success === true, `${target}: runFitLocal must report success, got ${JSON.stringify(out)}`);
    const chi1 = residualSS(env, be, bgSub);
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
  const chi0 = residualSS(env, be, bgSub);
  const out = env.runFitLocal(be, bgSub, bg);
  assert.equal(out.success, true);
  assert.ok(residualSS(env, be, bgSub) < 0.5 * chi0);
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

test('a local fit result is labelled as unweighted residual variance, never as χ²ᵣ', () => {
  const env = makeEnv();
  const be = Array.from({ length: 201 }, (_, i) => 280 + 0.05 * i);
  const data = be.map(x => 10 * env.gaussian(x, 285.0, 1.2));
  env.state.peaks = [{ id: 1, name: 'g', shape: 'Gaussian', center: 284.8, fwhm: 1.5, amplitude: 5, glMix: 50, asymmetry: 0 }];
  env.runFitLocal(be, data, new Array(be.length).fill(0));
  assert.equal(env.state.fitResult.objective, 'unweighted_residual_variance');
  assert.ok(!/χ/.test(env.dom['fit-quality'].textContent), `status text must not read as chi-square: ${env.dom['fit-quality'].textContent}`);
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
  const env = makeEnv();
  const be = grid(280, 290, 0.05);
  const { data, bg } = gaussCase(env, { be, dataAmp: 0.5, dataFwhm: 1.2, start: { center: 285.0, fwhm: 1.2, amplitude: 1, fixCenter: true, fixFwhm: true } });
  const out = env.runFitLocal(be, data, bg);
  assert.equal(out.success, true, JSON.stringify(out));
  assert.equal(env.state.peaks[0].amplitude, 1, 'stays on the wall');
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
