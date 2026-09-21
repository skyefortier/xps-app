// Auto-Fit C1s derives the spectrum's charge correction from the fitted
// centre of the "Graphite" component and then rigidly shifts every binding
// energy. Until 2026-09-21 it checked only that the centre lay within
// ±0.3 eV of 284.50 — which a component whose amplitude was driven to zero
// still satisfies (its centre is bounded to that window). The correction
// would then come from a component that does not exist.
//
// applyAutoFitResult is extracted verbatim from templates/index.html.

const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
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

const PAST_THE_GATE = new Error('reached the result-building step');
function makeEnv(peaks) {
  const dom = {};
  const el = id => (dom[id] ||= { value: '', textContent: '', setAttribute() {} });
  const calls = { notify: [], chargeCorrection: 0 };
  const state = { peaks, ccShift: 0.4, fitResult: { marker: 'previous' } };
  const src = ['applyAutoFitResult', '_autoFitGraphiteIsSupported'].map(extractFn).join('\n');
  const konst = lines.find(l => l.startsWith('const _AUTOFIT_ANCHOR_MIN_SPAN_FRACTION'));
  assert.ok(konst, 'threshold constant not found');
  const factory = new Function('document', 'state', 'notify', 'updateChargeCorrection', 'getROIData',
    konst + '\n' + src + '\nreturn { applyAutoFitResult, _autoFitGraphiteIsSupported };');
  const api = factory({ getElementById: el }, state, (msg, kind) => calls.notify.push({ msg, kind }),
    () => { calls.chargeCorrection++; }, () => { throw PAST_THE_GATE; });
  return { ...api, state, dom, calls };
}
// A C 1s-like region: background 1000, main line 86 000 high.
const be = Array.from({ length: 301 }, (_, i) => 280 + 0.05 * i);
const g = (c, a, w) => be.map(x => a * Math.exp(-4 * Math.LN2 * ((x - c) / w) ** 2));
const spectrum = (...parts) => be.map((_, i) => 1000 + parts.reduce((s, p) => s + p[i], 0));
const REAL = spectrum(g(284.6, 86000, 0.7), g(285.1, 14000, 1.9), g(286.4, 2300, 1.4));
const model = gAmp => [
  { id: 1, name: 'Graphite', center: 284.62, amplitude: gAmp, fwhm: 0.7 },
  { id: 2, name: 'Adventitious 1', center: 285.1, amplitude: 14000, fwhm: 1.9 },
  { id: 3, name: 'Adventitious 2', center: 286.4, amplitude: 2300, fwhm: 1.4 },
];
const json = (amps, ses) => ({ statistics: {}, individual_peaks: amps.map((a, i) => ({ id: String(i + 1),
  params: { amplitude: { value: a, stderr: ses ? ses[i] : null } } })) });
function rejected(env, ok) {
  assert.strictEqual(ok, false, 'caller rolls the model back on false');
  assert.strictEqual(env.calls.chargeCorrection, 0, 'updateChargeCorrection must not run');
  assert.deepStrictEqual(env.dom, {}, 'cc-method / cc-obs / cc-lit must not be touched');
  assert.deepStrictEqual(env.state.fitResult, { marker: 'previous' });
  assert.strictEqual(env.calls.notify.length, 1);
  assert.strictEqual(env.calls.notify[0].kind, 'red');
  assert.match(env.calls.notify[0].msg, /Graphite component fitted to no significant intensity/);
  assert.match(env.calls.notify[0].msg, /no charge correction/);
}

for (const gAmp of [0, 3.2e-12, -5, NaN, 0.013]) {
  test(`a Graphite amplitude of ${gAmp} sets no charge correction and rejects the auto-fit`, () => {
    const env = makeEnv(model(gAmp));
    rejected(env, env.applyAutoFitResult(json([gAmp, 14000, 2300]), 284.9, { inten: REAL }));
  });
}

test('a real Graphite component still drives the charge correction from its fitted centre', () => {
  const env = makeEnv(model(86000));
  assert.throws(() => env.applyAutoFitResult(json([86000, 14000, 2300], [120, 90, 60]), 284.9, { inten: REAL }), e => e === PAST_THE_GATE);
  assert.strictEqual(env.calls.chargeCorrection, 1);
  assert.strictEqual(env.dom['cc-method'].value, 'c1s');
  assert.strictEqual(env.dom['cc-obs'].value, (284.62 + 0.4).toFixed(3));
  assert.strictEqual(env.dom['cc-lit'].value, '284.50');
  assert.deepStrictEqual(env.calls.notify, []);
});

test('a weak but real Graphite component passes (the < 40 % area warning covers it)', () => {
  // 12 % of the region's span, 40 standard errors from zero: exists; whether it is a GOOD anchor is the amber warning's job
  const weak = spectrum(g(284.6, 9000, 0.7), g(285.1, 60000, 1.9));
  const env = makeEnv(model(9000));
  assert.throws(() => env.applyAutoFitResult(json([9000, 60000, 0], [220, 300, null]), 284.9, { inten: weak }), e => e === PAST_THE_GATE);
  assert.strictEqual(env.calls.chargeCorrection, 1);
});

test('no standard errors from the server (covariance failed) does not reject a real anchor', () => {
  const env = makeEnv(model(86000));
  assert.throws(() => env.applyAutoFitResult(json([86000, 14000, 2300], null), 284.9, { inten: REAL }), e => e === PAST_THE_GATE);
});

// ── Codex round 1 (both runs): the reference must be in the DATA. A threshold
//    relative to the strongest COMPONENT passes when the whole model collapses.
test('a collapsed model (every amplitude numerical residue) anchors nothing', () => {
  // weak scan, background over-estimated: server returned success with these amplitudes
  const amps = [3.25e-8, 2.59e-10, 1e-10, 1e-10, 1e-10];
  const peaks = amps.map((a, i) => ({ id: i + 1, name: i ? 'c' + i : 'Graphite', center: i ? 285 + i : 284.200000028, amplitude: a, fwhm: 1 }));
  const weakScan = be.map(x => 1000 + 30 * Math.exp(-4 * Math.LN2 * ((x - 284.5) / 0.3) ** 2));
  const env = makeEnv(peaks);
  rejected(env, env.applyAutoFitResult(json(amps), 284.9, { inten: weakScan }));
});

test('a signal below the upload rounding (server fitted a constant) anchors nothing', () => {
  // baseline 10 with a 0.004 bump: the server sees constant 10.00; least_squares returned 6.18e-5
  const amps = [6.18e-5, 2.0e-5, 1e-6];
  const peaks = amps.map((a, i) => ({ id: i + 1, name: i ? 'c' + i : 'Graphite', center: 284.23 + i, amplitude: a, fwhm: 1 }));
  const tiny = be.map(x => 10 + 0.004 * Math.exp(-4 * Math.LN2 * ((x - 284.5) / 0.4) ** 2));
  const env = makeEnv(peaks);
  rejected(env, env.applyAutoFitResult(json(amps), 284.9, { inten: tiny }));
});

test('a flat region supports no anchor at all', () => {
  const env = makeEnv(model(500));
  rejected(env, env.applyAutoFitResult(json([500, 14000, 2300]), 284.9, { inten: be.map(() => 1000) }));
});

test('an amplitude within three of its own standard errors of zero anchors nothing', () => {
  const env = makeEnv(model(9000));
  rejected(env, env.applyAutoFitResult(json([9000, 14000, 2300], [4000, 90, 60]), 284.9, { inten: REAL }));
});

test('the support check precedes every write of the charge-correction inputs', () => {
  const src = extractFn('applyAutoFitResult');
  const gate = src.indexOf('_autoFitGraphiteIsSupported(');
  assert.ok(gate > 0);
  for (const marker of ["getElementById('cc-method')", "getElementById('cc-obs')", 'updateChargeCorrection()'])
    assert.ok(src.indexOf(marker) > gate, marker + ' must come after the gate');
});

test('the fallback "first peak" anchor is held to the same rule', () => {
  const peaks = [{ id: 9, name: 'sp2', center: 284.5, amplitude: 0, fwhm: 0.7 }, { id: 10, name: 'x', center: 286, amplitude: 900, fwhm: 1 }];
  const env = makeEnv(peaks);
  assert.strictEqual(env.applyAutoFitResult(json([0, 900]), 284.9, { inten: REAL }), false);
  assert.strictEqual(env.calls.chargeCorrection, 0);
});

// ── Rollback: the rejection restores Custom charge correction WITH its input ──
test('rolling back to a Custom reference shows its target field again', () => {
  const dom = {};
  const el = id => (dom[id] ||= { value: '', textContent: '', style: { display: '' } });
  const owner = { id: 1 };
  const state = { peaks: [], ccShift: 0.3 };
  const factory = new Function('document', 'state', '_ownerLive', '_activeTab', '_setManualAnchors', 'renderPeakList', 'updatePlot',
    extractFn('_autoFitRestore') + '\nreturn _autoFitRestore;');
  const restore = factory({ getElementById: el }, state, () => true, () => owner, () => {}, () => {}, () => {});
  el('cc-target-field').style.display = 'none';            // what the provisional 'c1s' correction left behind
  el('cc-ref-field').style.display = 'block';
  restore({ owner, peaks: [], fitResult: null, ccShift: 0, manualAnchors: [], nextId: 1, ccMethodDom: 'custom',
            ccObsDom: '285.1', ccLitDom: '284.8', roiMinDom: '', roiMaxDom: '', bgStartDom: '', bgEndDom: '' }, owner);
  assert.strictEqual(dom['cc-method'].value, 'custom');
  assert.strictEqual(dom['cc-target-field'].style.display, 'block');
  assert.strictEqual(dom['cc-ref-field'].style.display, 'block');
  restore({ owner, peaks: [], fitResult: null, ccShift: 0, manualAnchors: [], nextId: 1, ccMethodDom: 'none',
            ccObsDom: '', ccLitDom: '', roiMinDom: '', roiMaxDom: '', bgStartDom: '', bgEndDom: '' }, owner);
  assert.strictEqual(dom['cc-target-field'].style.display, 'none');
  assert.strictEqual(dom['cc-ref-field'].style.display, 'none');
});
