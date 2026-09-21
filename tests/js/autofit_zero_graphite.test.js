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
  const konst = lines.find(l => l.startsWith('const _AUTOFIT_ANCHOR_MIN_F'));
  assert.ok(konst, 'threshold constant not found');
  const factory = new Function('document', 'state', 'notify', 'updateChargeCorrection', 'getROIData',
    konst + '\n' + src + '\nreturn { applyAutoFitResult, _autoFitGraphiteIsSupported };');
  const api = factory({ getElementById: el }, state, (msg, kind) => calls.notify.push({ msg, kind }),
    () => { calls.chargeCorrection++; }, () => { throw PAST_THE_GATE; });
  return { ...api, state, dom, calls };
}
function rejected(env, ok) {
  assert.strictEqual(ok, false, 'caller rolls the model back on false');
  assert.strictEqual(env.calls.chargeCorrection, 0, 'updateChargeCorrection must not run');
  assert.deepStrictEqual(env.dom, {}, 'cc-method / cc-obs / cc-lit must not be touched');
  assert.deepStrictEqual(env.state.fitResult, { marker: 'previous' });
  assert.strictEqual(env.calls.notify.length, 1);
  assert.strictEqual(env.calls.notify[0].kind, 'red');
  assert.match(env.calls.notify[0].msg, /data do not support the Graphite component/);
  assert.match(env.calls.notify[0].msg, /no charge correction/);
}

// Real fitting.run_fit responses (scripts/gen_autofit_anchor_fixtures.py): every case the Codex
// reviews produced while five intensity-floor rules failed, plus an ordinary C 1s.
const FIXTURES = JSON.parse(fs.readFileSync(path.join(__dirname, 'fixtures/autofit_anchor.json'), 'utf8'));
const peaksOf = fx => [{ id: Number(fx.graphite.id), name: 'Graphite', center: fx.graphite.center, amplitude: fx.graphite.amplitude, fwhm: 0.7 }];

test('the fixture set covers both outcomes', () => {
  assert.ok(FIXTURES.filter(f => f.supported).length >= 5 && FIXTURES.filter(f => !f.supported).length >= 4);
  assert.ok(FIXTURES.every(f => f.json.success === true), 'every case is a fit the server called successful');
});

for (const fx of FIXTURES) {
  test(`${fx.supported ? 'anchors the correction' : 'anchors NOTHING'} — ${fx.name}`, () => {
    const env = makeEnv(peaksOf(fx));
    if (!fx.supported) return rejected(env, env.applyAutoFitResult(fx.json, 284.9, {}));
    assert.throws(() => env.applyAutoFitResult(fx.json, 284.9, {}), e => e === PAST_THE_GATE);
    assert.strictEqual(env.calls.chargeCorrection, 1);
    assert.strictEqual(env.dom['cc-method'].value, 'c1s');
    assert.strictEqual(env.dom['cc-obs'].value, (fx.graphite.center + 0.4).toFixed(3));
    assert.strictEqual(env.dom['cc-lit'].value, '284.50');
    assert.deepStrictEqual(env.calls.notify, []);
  });
}

const real = FIXTURES.find(f => /ordinary C 1s/.test(f.name));
for (const gAmp of [0, -5, NaN, Infinity]) {
  test(`an anchor amplitude of ${gAmp} is refused before anything is computed`, () => {
    const env = makeEnv([{ ...peaksOf(real)[0], amplitude: gAmp }]);
    rejected(env, env.applyAutoFitResult(real.json, 284.9, {}));
  });
}

test('a response that lacks the fitted data or the component curve cannot vouch for an anchor', () => {
  for (const drop of ['counts', 'fitted_y']) {
    const env = makeEnv(peaksOf(real));
    const j = { ...real.json }; delete j[drop];
    rejected(env, env.applyAutoFitResult(j, 284.9, {}));
  }
  const env = makeEnv(peaksOf(real));
  rejected(env, env.applyAutoFitResult({ ...real.json, individual_peaks: [] }, 284.9, {}));
});

test('an exact fit that needs the component is supported (chi-square with it is zero)', () => {
  const comp = Array.from({ length: 50 }, (_, i) => 100 * Math.exp(-(((i - 25) / 4) ** 2)));
  const counts = comp.map(v => 1000 + v);
  const json = { counts, fitted_y: counts.slice(), statistics: { n_free_params: 3 },
    individual_peaks: [{ id: '1', y: comp, params: { amplitude: { value: 100, vary: true, expr: null } } }] };
  const env = makeEnv([{ id: 1, name: 'Graphite', center: 284.5, amplitude: 100, fwhm: 0.7 }]);
  assert.throws(() => env.applyAutoFitResult(json, 284.9, {}), e => e === PAST_THE_GATE);
});

test('removing a component that costs nothing is the definition of unsupported', () => {
  // identical counts and fit WITHOUT the component; the component only adds misfit
  const comp = Array.from({ length: 50 }, (_, i) => 0.03 * Math.exp(-(((i - 25) / 4) ** 2)));
  const counts = Array.from({ length: 50 }, () => 1e7);
  const json = { counts, fitted_y: counts.map((c, i) => c + comp[i]), statistics: { n_free_params: 3 },
    individual_peaks: [{ id: '1', y: comp, params: { amplitude: { value: 0.03, stderr: 0.009, vary: true, expr: null } } }] };
  const env = makeEnv([{ id: 1, name: 'Graphite', center: 284.256, amplitude: 0.03, fwhm: 0.7 }]);
  rejected(env, env.applyAutoFitResult(json, 284.9, {}));
});

test('the support check precedes every write of the charge-correction inputs', () => {
  const src = extractFn('applyAutoFitResult');
  const gate = src.indexOf('_autoFitGraphiteIsSupported(');
  assert.ok(gate > 0);
  for (const marker of ["getElementById('cc-method')", "getElementById('cc-obs')", 'updateChargeCorrection()'])
    assert.ok(src.indexOf(marker) > gate, marker + ' must come after the gate');
});

test('the fallback "first peak" anchor is held to the same rule', () => {
  const fx = FIXTURES.find(f => !f.supported);
  const env = makeEnv([{ ...peaksOf(fx)[0], name: 'sp2' }]);
  assert.strictEqual(env.applyAutoFitResult(fx.json, 284.9, {}), false);
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
