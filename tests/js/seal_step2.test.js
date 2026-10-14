// Seal 1c step 2 (plan docs/superpowers/plans/2026-10-14-seal-1c-page.md §2-§4, §6.3): the pure functions the
// seal will judge with — `project` (the live application of a server fit), `_ccShiftOf` / `_ccMoveField`
// (updateChargeCorrection's arithmetic) and `_sameModel` — are the live behaviour, not a second reading of it.
// The live request identity and Auto-Fit's derivation are pinned in the browser:
// tests/test_browser_seal_requests.py.
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
const lines = html.split('\n');
function extractFn(name) {
  const start = lines.findIndex(l => new RegExp('^(async )?function ' + name + '\\(').test(l));
  assert.ok(start >= 0, name);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail('unbalanced ' + name);
}
function extractConst(name) {
  const start = lines.findIndex(l => l.startsWith('const ' + name + ' ='));
  assert.ok(start >= 0, name);
  let i = start; while (!/;\s*$/.test(lines[i])) i++;
  return lines.slice(start, i + 1).join('\n');
}
const S = new Function(
  ['_PROJECTED_FIELDS', '_MODEL_EVIDENCE_FIELDS', '_CC_REFERENCE'].map(extractConst).join('\n') + '\n' +
  ['_applyBackendParams', 'project', '_applyProjected', '_sameModel', '_ccShiftOf', '_ccMoveField'].map(extractFn).join('\n') +
  '\nreturn { _applyBackendParams, project, _applyProjected, _sameModel, _ccShiftOf, _ccMoveField };')();

// The live application as it was before step 2 (applyBackendResult's loop): on the live peaks, by id.
function applyLikeBefore(live, O) {
  for (const ip of O.individual_peaks) {
    const p = live.find(x => x.id === Number(ip.id)) || live.find(x => x.id === ip.id);
    if (!p) continue;
    S._applyBackendParams(p, ip.params);
    p._backendParams = ip.params;
  }
}
const par = (value, expr = null) => ({ value, stderr: 0.01, vary: !expr, expr, min: null, max: null });
// one peak of every lineshape, with every lock pattern, plus a linked child
function models() {
  const shapes = [
    { shape: 'Gaussian' }, { shape: 'Lorentzian' }, { shape: 'Voigt', glMix: 42 }, { shape: 'GL', glMix: 30 },
    { shape: 'asym-GL', glMix: 20, asymmetry: 0.2 }, { shape: 'DS', dsAlpha: 0.1, dsGamma: 0.0 },
    { shape: 'DSG_LA', laAlpha: 0.1, laBeta: 0.3, laM: 0.4 }, { shape: 'LACX', caAlpha: 1.2, caBeta: 1.0, caM: 6 },
  ];
  const locks = [{}, { fixCenter: true }, { fixFwhm: true, fixAmplitude: true }, { fixGlMix: true, fixAsymmetry: true,
    fixDsAlpha: true, fixDsGamma: true, fixLaAlpha: true, fixLaBeta: true, fixLaM: true, fixCaAlpha: true, fixCaBeta: true, fixCaM: true }];
  const out = [];
  for (const sh of shapes) for (const lk of locks) {
    const parent = { id: 1, name: 'P', color: '#f00', center: 284.8, fwhm: 1.1, amplitude: 5000, ...sh, ...lk };
    const child = { id: 2, name: 'C', color: '#0f0', center: 286.4, fwhm: 1.1, amplitude: 1250, ...sh, ...lk,
                    linked: 1, linkOffset: 1.6, linkRatio: 0.25 };
    out.push([parent, child]);
  }
  return out;
}
function reply(model) {
  // the server's reply: every parameter of the shape, fitted values moved; a linked child's by expression
  const ip = model.map(p => {
    const e = p.linked ? 'p1_' : null;
    const params = { center: par(p.center + 0.013, e && e + 'center + 1.6'), amplitude: par(p.amplitude * 1.07, e && e + 'amplitude * 0.25'),
                     fwhm: par(p.fwhm * 0.97, e && e + 'fwhm'), area: { value: 1, stderr: null } };
    if (['Voigt', 'GL', 'asym-GL'].includes(p.shape)) params.gl_ratio = par(0.33, e && e + 'gl_ratio');
    if (p.shape === 'asym-GL') params.asymmetry = par(0.27, e && e + 'asymmetry');
    if (p.shape === 'DS') { params.alpha = par(0.13, e && e + 'alpha'); params.gamma_asym = par(0.02, e && e + 'gamma_asym'); }
    if (p.shape === 'DSG_LA') { params.alpha = par(0.12, e && e + 'alpha'); params.beta = par(0.31, e && e + 'beta'); params.m_gauss = par(0.45, e && e + 'm_gauss'); }
    if (p.shape === 'LACX') { params.alpha = par(1.3, e && e + 'alpha'); params.beta = par(1.1, e && e + 'beta'); params.m = par(6.5, e && e + 'm'); }
    return { id: String(p.id), params };
  });
  return { individual_peaks: ip };
}

test('project applied in place is EXACTLY the live application it replaced, for every lineshape and lock (Run Fit)', () => {
  for (const model of models()) {
    const O = reply(model);
    const before = structuredClone(model); applyLikeBefore(before, O);
    const live = structuredClone(model); S._applyProjected(live, S.project(model, O));
    assert.deepStrictEqual(live, before, model[0].shape + ' ' + JSON.stringify(Object.keys(model[0]).filter(k => k.startsWith('fix'))));
  }
});

test('"Use this solution": the projection of the adopted start onto the live model is the old live application', () => {
  for (const model of models()) {
    // the start differs from the live model in FREE fields only (_altPeaks applies the alternative's values
    // through the same lock rules); presentation fields are the live model's
    const start = structuredClone(model);
    S._applyBackendParams(start[0], reply(model).individual_peaks[0].params);
    const O = reply(start);
    const before = structuredClone(model); applyLikeBefore(before, O);
    const live = structuredClone(model); S._applyProjected(live, S.project(start, O));
    assert.deepStrictEqual(live, before, model[0].shape);
  }
});

test('project is PURE: the snapshot is not touched, and the result shares no mutable object with it', () => {
  const model = models()[4];
  const frozen = JSON.stringify(model);
  const out = S.project(model, reply(model));
  assert.strictEqual(JSON.stringify(model), frozen);
  out[0].center = -1; out[0].name = 'x';
  assert.strictEqual(JSON.stringify(model), frozen);
});

test('_applyProjected never writes presentation fields (name, colour, visibility) — a live rename survives', () => {
  const model = models()[0];
  const live = structuredClone(model); live[0].name = 'renamed while the fit ran'; live[0].color = '#123456'; live[0].visible = false;
  S._applyProjected(live, S.project(model, reply(model)));
  assert.strictEqual(live[0].name, 'renamed while the fit ran');
  assert.strictEqual(live[0].color, '#123456');
  assert.strictEqual(live[0].visible, false);
});

// updateChargeCorrection before step 2, its arithmetic written out (the branch per method)
function shiftLikeBefore(method, obsText, litText) {
  const obs = parseFloat(obsText);
  const refs = { c1s: 284.5, 'c1s-adv': 284.8, au4f: 83.98, 'b1s-b2o3': 192.99, 'n1s-bn': 398.31, 'b1s-bn': 190.74 };
  if (method in refs) return isNaN(obs) ? 0 : obs - refs[method];
  if (method === 'custom') { const lit = parseFloat(litText); return (isNaN(obs) || isNaN(lit)) ? 0 : obs - lit; }
  return 0;
}

test('_ccShiftOf is updateChargeCorrection\'s arithmetic for every method, number and blank', () => {
  const methods = ['none', 'c1s', 'c1s-adv', 'au4f', 'b1s-b2o3', 'n1s-bn', 'b1s-bn', 'custom', 'unknown'];
  const texts = ['', '284.937', '285', 'abc', '-0', '1e2', '284.5000001', ' 286.1 '];
  for (const m of methods) for (const o of texts) for (const l of texts) {
    const got = S._ccShiftOf(m, o, l).shift, want = shiftLikeBefore(m, o, l);
    assert.ok(Object.is(got, want), `${m} ${JSON.stringify(o)} ${JSON.stringify(l)}: ${got} vs ${want}`);
  }
  assert.strictEqual(S._ccShiftOf('c1s', '285', '284.50').lit, '284.5');   // the reference field reads 284.5
  assert.strictEqual(S._ccShiftOf('custom', '285', '284.50').lit, '284.50');
});

test('_ccMoveField moves a number by -delta to one decimal and keeps a blank or non-number', () => {
  assert.strictEqual(S._ccMoveField('298.16', 0.437), (298.16 - 0.437).toFixed(1));
  assert.strictEqual(S._ccMoveField('', 0.437), '');
  assert.strictEqual(S._ccMoveField('abc', 0.437), 'abc');
  assert.strictEqual(S._ccMoveField('280', -1.25), (280 + 1.25).toFixed(1));
});

test('_sameModel: equal models, the fit evidence (support) aside; any other field differs', () => {
  const a = models()[3], b = structuredClone(a);
  b[0].support = { f: 12, supported: true, fitKey: 'k' };
  assert.ok(S._sameModel(a, b));
  b[1].fixCenter = !b[1].fixCenter;
  assert.ok(!S._sameModel(a, b));
  assert.ok(!S._sameModel(a, a.slice(0, 1)));
  const c = structuredClone(a); c[0].shape = 'Lorentzian';
  assert.ok(!S._sameModel(a, c));
});
