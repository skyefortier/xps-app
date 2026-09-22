// Step (c): Auto-Fit asks the server whether its charge-reference anchor is
// REQUIRED (a refit without it), and refuses a redundant anchor the same way
// it refuses an unsupported one — before any charge-correction input is
// touched. Extracted from templates/index.html.
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
const lines = html.split('\n');
function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name + '\\(');
  const start = lines.findIndex(l => re.test(l));
  assert.ok(start >= 0, name);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail('unbalanced ' + name);
}
const constLine = n => lines.find(l => l.startsWith('const ' + n));
const PAST = new Error('past the gates');
function env(peaks) {
  const dom = {}; const el = id => (dom[id] ||= { value: '', textContent: '', setAttribute() {} });
  const calls = { notify: [], cc: 0 };
  const state = { peaks, ccShift: 0.4, fitResult: { marker: 'previous' } };
  const src = [constLine('_AUTOFIT_ANCHOR_MIN_F'), extractFn('_autoFitGraphiteIsSupported'), extractFn('applyAutoFitResult')].join('\n');
  const f = new Function('document', 'state', 'notify', 'updateChargeCorrection', 'getROIData', '_escAttr', src + '\nreturn applyAutoFitResult;')(
    { getElementById: el }, state, (m, k) => calls.notify.push([k, m]), () => { calls.cc++; }, () => { throw PAST; }, s => s);
  return { f, calls, dom };
}
const FIX = JSON.parse(fs.readFileSync(path.join(__dirname, 'fixtures/autofit_anchor.json'), 'utf8'));
const real = FIX.find(x => /ordinary C 1s/.test(x.name));
const peaks = () => [{ id: 1, name: 'Graphite', center: real.graphite.center, amplitude: real.graphite.amplitude, fwhm: 0.7 }];

test('a supported but NOT required anchor is refused before any charge-correction input is touched', () => {
  const e = env(peaks());
  const ok = e.f({ ...real.json, required: { ran: true, required: false, f: 0.0, chi2_with: 1.2, chi2_without_refit: 1.2, refit_converged: true } }, 284.9, {});
  assert.strictEqual(ok, false);
  assert.strictEqual(e.calls.cc, 0);
  assert.deepStrictEqual(e.dom, {});
  assert.strictEqual(e.calls.notify.length, 1);
  assert.strictEqual(e.calls.notify[0][0], 'red');
  assert.match(e.calls.notify[0][1], /not required by the data — refitting the other components without it fits the data as well \(F = 0\.0, threshold 10\)/);
  assert.match(e.calls.notify[0][1], /No charge correction was derived/);
});

test('a required anchor proceeds; a check that did not run (older server, error, non-converged) does not block', () => {
  for (const required of [{ ran: true, required: true, f: 6120 }, null, undefined, { ran: false, reason: 'error', error: 'x' }]) {
    const e = env(peaks());
    assert.throws(() => e.f({ ...real.json, required }, 284.9, {}), x => x === PAST, JSON.stringify(required));
    assert.strictEqual(e.calls.cc, 1);
  }
});

test('the request asks for the Graphite anchor by id, and the gate precedes the support gate and every cc write', () => {
  const run = extractFn('runAutoFitC1sGraphite');
  assert.match(run, /require_component: String\(\(state\.peaks\.find\(p => p\.name === 'Graphite'\) \|\| state\.peaks\[0\]\)\.id\)/);
  const apply = extractFn('applyAutoFitResult');
  const gate = apply.indexOf('req.required === false');
  assert.ok(gate > 0 && gate < apply.indexOf('_autoFitGraphiteIsSupported(gPeak, json)'));
  for (const m of ["getElementById('cc-method')", "getElementById('cc-obs')", 'updateChargeCorrection()']) assert.ok(apply.indexOf(m) > gate, m);
});
