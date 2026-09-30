// The certificate's displacement notice (unit A2, 2026-09-29). The server
// certifies the returned fit by continuing it from where the optimiser stopped
// (fitting._certify_fit). Owner: when that continuation moves any component
// centre more than 1 eV (the existing red-band distance), show it with the
// existing displacement indicator — "fit continued past where the optimiser
// stopped; <component> moved <X> eV". A NOTICE, not a confirmation: it is the
// student's own fit continued, unlike a scattered-starts alternative. Bound to
// the fit by the same model key as the starts evidence.
//
// Functions are extracted verbatim from templates/index.html.
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
function constStmt(name) {                     // a const statement, possibly over several lines
  const start = lines.findIndex(l => l.startsWith('const ' + name));
  assert.ok(start >= 0, name);
  let end = start; while (!lines[end].trimEnd().endsWith(';')) end++;
  return lines.slice(start, end + 1).join('\n');
}

const FNS = ['_fitKeyCanon', '_sameFitKey', '_startsModelKey', '_startsLiveKey', '_startsPeakName', '_startsShiftColour', '_startsEv',
  '_certificateMoveFrom', '_certificateMoveIfCurrent', '_certificateMoveText', '_certificateMoveTip', '_certificateNoticeHtml'];
function makeEnv({ cert, stale = false }) {
  const peaks = [{ id: 1, name: 'Graphite', shape: 'GL', center: 284.4, fwhm: 0.7, amplitude: 9000, glMix: 20 },
                 { id: 2, name: 'C-O', shape: 'GL', center: 286.4, fwhm: 1.4, amplitude: 2000, glMix: 0 }];
  const state = { peaks, ccShift: 0, fitResult: {} };
  const ui = { bgType: 'shirley', bgStart: '281.0', bgEnd: '294.0', shirleyIter: '5', endpointAvg: '3', roiMin: '280', roiMax: '295' };
  const fieldsStart = lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS'));
  const fields = lines.slice(fieldsStart, lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n');
  const src = [constStmt('_STARTS_SHIFT_AMBER_EV'), fields, ...FNS.map(extractFn)].join('\n');
  const api = new Function('state', 'getPeak', '_escHtml', '_escAttr', 'tabManager', '_getManualAnchors',
    src + '\nreturn { ' + FNS.join(', ') + ', TIP: _certificateMoveTip() };')(
    state, id => peaks.find(p => String(p.id) === String(id)),
    s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;'), s => String(s).replace(/"/g, '&quot;'),
    { _captureUI: () => ({ ...ui }) }, () => []);
  state.fitResult.certificateMove = api._certificateMoveFrom(cert);
  state.fitResult.startsModelKey = stale ? 'a different model' : api._startsLiveKey();
  return { ...api, state };
}
const CERT = (ev, over = {}) => ({ certified: true, restarts: 6, moved: true, optimiser_flag: true,
  centre_moves: [{ id: 1, ev: 0.01 }, { id: 2, ev }], largest_centre_move: { id: 2, ev }, ...over });

test('only a move beyond the red-band distance (> 1 eV) is a notice', () => {
  const { _certificateMoveFrom } = makeEnv({ cert: null });
  assert.strictEqual(_certificateMoveFrom(null), null);                               // DE / basinhopping
  assert.strictEqual(_certificateMoveFrom(CERT(-1.47, { moved: false })), null);     // the fit was already at its minimum
  assert.strictEqual(_certificateMoveFrom(CERT(0.9)), null);
  assert.strictEqual(_certificateMoveFrom(CERT(1.0)), null);                          // the band is "more than 1 eV"
  assert.deepStrictEqual(_certificateMoveFrom(CERT(-1.47)), { id: 2, ev: -1.47 });
  assert.deepStrictEqual(_certificateMoveFrom(CERT(1.2)), { id: 2, ev: 1.2 });
});

test('the notice names the component and the distance with the displacement indicator, and asks nothing', () => {
  const env = makeEnv({ cert: CERT(-1.47) });
  const h = env._certificateNoticeHtml(env.state.fitResult);
  assert.match(h, /class="certificate-move-note"/);
  assert.match(h, /Fit continued past where the optimiser stopped; <span style="color:var\(--red,#ef4444\);font-weight:600">C-O moved −1\.47 eV<\/span>\./);
  assert.ok(!/<button|confirm/i.test(h), 'a notice, not a confirmation');
  assert.match(env.TIP, /still your model and your start/);
  assert.strictEqual(env._certificateMoveText(env.state.fitResult),
    'fit continued past where the optimiser stopped; C-O moved −1.47 eV');
});

test('bound to the fit: after the model changes the notice is gone (placeholder kept for the in-place refresh)', () => {
  const env = makeEnv({ cert: CERT(-1.47), stale: true });
  assert.strictEqual(env._certificateNoticeHtml(env.state.fitResult), '<div class="certificate-move-note"></div>');
  assert.strictEqual(env._certificateMoveText(env.state.fitResult), '');
  assert.strictEqual(env._certificateMoveIfCurrent(env.state.fitResult, env._startsLiveKey()), null);
  const quiet = makeEnv({ cert: CERT(0.4) });
  assert.strictEqual(quiet._certificateNoticeHtml(quiet.state.fitResult), '<div class="certificate-move-note"></div>');
});

test('wiring: stored from the response, shown before the starts panel, refreshed in place, saved while current, restored, exported', () => {
  assert.match(html, /certificateMove: _certificateMoveFrom\(backendResult\.certificate\),/);
  assert.match(html, /html \+= _certificateNoticeHtml\(state\.fitResult\);\n  html \+= _startsPanelHtml\(state\.fitResult\);/);
  assert.match(html, /const cn = document\.querySelector\('\.certificate-move-note'\);\n  if \(cn && state\.fitResult\) cn\.outerHTML = _certificateNoticeHtml\(state\.fitResult\);/);
  assert.strictEqual((html.match(/certificateMove: _certificateMoveIfCurrent\(state\.fitResult, _startsLiveKey\(\)\),/g) || []).length, 2);
  assert.strictEqual((html.match(/certificateMove: _certificateMoveIfCurrent\(t\.fitResult, _startsRecordKey\(t\)\),/g) || []).length, 1);
  assert.match(html, /'chosenAlternative', 'certificateMove'\]\) if \(data\.statistics\[k\]\)/);
  assert.match(html, /\['Fit continued', _certificateMoveText\(state\.fitResult\)\]/);
  assert.match(html, /csv \+= `# Fit continued: \$\{_certificateMoveText\(state\.fitResult\)\}\\n`;/);
});
