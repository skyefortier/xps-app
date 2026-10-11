// Endpoint averaging: every reader reads the field one way, and a value outside the field's own
// 1-50 is refused, never clamped (owner 2026-10-11; Codex averaging round 1): the page's reader,
// its Python twin for saved projects (autofit.reference.page_endpoint_avg), the fit key's
// comparison, and the background itself (computeBackgroundCore), which every consumer reaches.
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { runHelper } = require('./_helper_process.js');

const REPO_ROOT = path.join(__dirname, '../..');
const html = fs.readFileSync(path.join(REPO_ROOT, 'templates/index.html'), 'utf8');
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
const PYTHON = [path.join(REPO_ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3'].find(p => fs.existsSync(p)) || 'python3';
const fail = new Function(extractFn('_endpointAvgFailure') + '\nreturn _endpointAvgFailure;')();

const TEXTS = ['1', '3', '50', ' 7 ', '3.0', '+3', '007', '1.', '0x10', '0X1f', '3e0', '30e-1',
  '', ' ', '0', '-1', '-0', '51', '1000', '1e1', '1e2', '1e21', '2e21', '2.5', '.5', 'abc', '1_0', '3 4',
  '0b11', '0o7', '+0x10', 'Infinity', 'NaN', '1,0', '0'.repeat(400) + '3',
  // Codex averaging round 2: JavaScript's whitespace, ASCII-only digits, no big-integer limits
  '\ufeff3', '\u00853', '\u00a07\u00a0', '\u20283', '3e\u0660', '\u0663', '0'.repeat(5000) + '3', '0x' + 'f'.repeat(6000),
  '0x1g', '0b2', '-0x3'];

test('the Python twin reads every saved text exactly as the page does', () => {
  const page = TEXTS.map(t => { const f = fail(t); return f ? null : Number(String(t).trim()); });
  const script = 'import json, sys; sys.path.insert(0, sys.argv[1]); from autofit.reference import page_endpoint_avg as f\n' +
    'out = []\nfor t in json.load(sys.stdin):\n    try: out.append(f(t))\n    except ValueError: out.append(None)\nprint(json.dumps(out))';
  const py = JSON.parse(runHelper(PYTHON, ['-c', script, REPO_ROOT], { input: JSON.stringify(TEXTS), encoding: 'utf8' }));
  assert.deepStrictEqual(py, page, TEXTS.map((t, i) => `${JSON.stringify(t.length > 20 ? t.slice(-5) : t)}: page ${page[i]} py ${py[i]}`).filter((_, i) => py[i] !== page[i]).join('; '));
  assert.ok(page.filter(v => v !== null).length >= 10 && page.filter(v => v === null).length >= 15, 'both outcomes exercised');
});

test('a non-scalar saved value is refused by both readers', () => {
  for (const v of [[3], ['3'], {}, [[3]]]) assert.match(String(fail(v)), /it is not a number/, JSON.stringify(v));
  const script = 'import json, sys; sys.path.insert(0, sys.argv[1]); from autofit.reference import page_endpoint_avg as f\n' +
    'out = []\nfor t in json.load(sys.stdin):\n    try: f(t); out.append("accepted")\n    except ValueError: out.append("refused")\nprint(json.dumps(out))';
  const py = JSON.parse(runHelper(PYTHON, ['-c', script, REPO_ROOT], { input: JSON.stringify([[3], ['3'], {}, [[3]]]), encoding: 'utf8' }));
  assert.deepStrictEqual(py, ['refused', 'refused', 'refused', 'refused']);
});

test('the fit key compares the averaging as the refusal reads it', () => {
  const src = lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') +
    '\n' + ['_endpointAvgFailure', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n') + '\nreturn { _sameFitKey, _STARTS_UI_FIELDS };';
  const K = new Function(src)();
  const key = avg => JSON.stringify({ p: [], u: K._STARTS_UI_FIELDS.map(f => (f === 'endpointAvg' ? avg : '')), s: 0, a: [] });
  assert.ok(!K._sameFitKey(key('1'), key('1e2')), '"1e2" is refused, not the 1 parseInt makes of it');
  assert.ok(!K._sameFitKey(key('3'), key('3e2')));
  assert.ok(!K._sameFitKey(key('1'), key('0')));
  assert.ok(K._sameFitKey(key('3'), key('3.0')) && K._sameFitKey(key('3'), key(' 3 ')), 'one value, two spellings');
  assert.ok(K._sameFitKey(key('1e2'), key('1e2')), 'the same text is the same');
});

test('the background itself refuses: every consumer of computeBackgroundCore inherits it', () => {
  const B = new Function(require('./_page_background_source.js')() + '\nreturn { computeBackgroundCore };')();
  const be = Array.from({ length: 60 }, (_, i) => 290 - i * 0.1), y = be.map((x, i) => 100 + 1000 * Math.exp(-((x - 285) ** 2)) + (i > 30 ? 50 : 0));
  const ok = B.computeBackgroundCore(be, y, { bgType: 'shirley', endpointAvg: '3', bgStart: '', bgEnd: '' });
  assert.strictEqual(ok.converged, true);
  assert.deepStrictEqual(Array.from(B.computeBackgroundCore(be, y, { bgType: 'shirley', endpointAvg: 3, bgStart: '', bgEnd: '' })), Array.from(ok), 'numeric 3 = "3"');
  const legacy = B.computeBackgroundCore(be, y, { bgType: 'shirley', bgStart: '', bgEnd: '' });
  assert.deepStrictEqual(Array.from(legacy), Array.from(B.computeBackgroundCore(be, y, { bgType: 'shirley', endpointAvg: '1', bgStart: '', bgEnd: '' })), 'absent is the legacy 1');
  for (const t of ['51', '0', '1e21', '', '2.5', '1e1']) {
    const bg = B.computeBackgroundCore(be, y, { bgType: 'shirley', endpointAvg: t, bgStart: '', bgEnd: '' });
    assert.strictEqual(bg.converged, false, t);
    assert.strictEqual(bg.failure, `Background not computed: endpoint averaging must be a whole number from 1 to 50 (it is "${t.trim()}").`);
  }
  // every method, not only the integral ones
  for (const m of ['linear', 'manual', 'none', 'tougaard', 'smart'])
    assert.strictEqual(B.computeBackgroundCore(be, y, { bgType: m, endpointAvg: '51', bgStart: '', bgEnd: '', anchors: [] }).converged, false, m);
});

test('archived Find Peaks refuses the field as typed before any conversion (structural)', () => {
  const src = extractFn('runFindPeaks');
  assert.match(src, /const epText = document\.getElementById\('bg-endpoint-avg'\)\?\.value;\n\s+const epFail = _endpointAvgFailure\(epText\);\n\s+if \(epFail\) \{ status\.textContent = 'Not run: ' \+ epFail; return; \}\n\s+options\.endpoint_avg = Number\(String\(epText\)\.trim\(\)\);/);
  assert.ok(!/parseInt\(document\.getElementById\('bg-endpoint-avg'\)/.test(src), 'no parseInt(field) || 1');
});
