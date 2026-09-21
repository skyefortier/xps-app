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
  const factory = new Function('document', 'state', 'notify', 'updateChargeCorrection', 'getROIData',
    src + '\nreturn { applyAutoFitResult, _autoFitGraphiteIsSupported };');
  const api = factory({ getElementById: el }, state, (msg, kind) => calls.notify.push({ msg, kind }),
    () => { calls.chargeCorrection++; }, () => { throw PAST_THE_GATE; });
  return { ...api, state, dom, calls };
}
const model = gAmp => [
  { id: 1, name: 'Graphite', center: 284.62, amplitude: gAmp, fwhm: 0.7 },
  { id: 2, name: 'Adventitious 1', center: 285.1, amplitude: 14000, fwhm: 1.9 },
  { id: 3, name: 'Adventitious 2', center: 286.4, amplitude: 2300, fwhm: 1.4 },
];

for (const gAmp of [0, 3.2e-12, -5, NaN, 0.013]) {
  test(`a Graphite amplitude of ${gAmp} sets no charge correction and rejects the auto-fit`, () => {
    const env = makeEnv(model(gAmp));
    const ok = env.applyAutoFitResult({ statistics: {} }, 284.9, {});
    assert.strictEqual(ok, false, 'caller rolls the model back on false');
    assert.strictEqual(env.calls.chargeCorrection, 0, 'updateChargeCorrection must not run');
    assert.deepStrictEqual(env.dom, {}, 'cc-method / cc-obs / cc-lit must not be touched');
    assert.deepStrictEqual(env.state.fitResult, { marker: 'previous' });
    assert.strictEqual(env.calls.notify.length, 1);
    assert.strictEqual(env.calls.notify[0].kind, 'red');
    assert.match(env.calls.notify[0].msg, /Graphite component fitted to zero intensity/);
    assert.match(env.calls.notify[0].msg, /no charge correction/);
  });
}

test('a real Graphite component still drives the charge correction from its fitted centre', () => {
  const env = makeEnv(model(86000));
  assert.throws(() => env.applyAutoFitResult({ statistics: {} }, 284.9, {}), e => e === PAST_THE_GATE);
  assert.strictEqual(env.calls.chargeCorrection, 1);
  assert.strictEqual(env.dom['cc-method'].value, 'c1s');
  assert.strictEqual(env.dom['cc-obs'].value, (284.62 + 0.4).toFixed(3));
  assert.strictEqual(env.dom['cc-lit'].value, '284.50');
  assert.deepStrictEqual(env.calls.notify, []);
});

test('a weak but real Graphite component passes (the < 40 % area warning covers it)', () => {
  const env = makeEnv(model(150));              // ~1 % of the strongest component
  assert.throws(() => env.applyAutoFitResult({ statistics: {} }, 284.9, {}), e => e === PAST_THE_GATE);
  assert.strictEqual(env.calls.chargeCorrection, 1);
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
  assert.strictEqual(env.applyAutoFitResult({ statistics: {} }, 284.9, {}), false);
  assert.strictEqual(env.calls.chargeCorrection, 0);
});
