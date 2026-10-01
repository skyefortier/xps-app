// A background that does not satisfy its defining statement is "not converged"
// and nothing on the page uses it as a background (owner, 2026-10-01; background
// math F10, F11, F12). computeBackgroundCore marks every result with its
// certificate (converged / failure); every consumer must read it. The guard below
// is a CLASS guard: every assignment of a computed background must be followed,
// in its own function, by a _bgFailure check of that variable (or the function
// must refuse up front on _bgFailure(computeBackground(...))) — a new consumer
// that forgets fails here.
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
const lines = html.split('\n');
const B = new Function(require('./_page_background_source.js')() +
  '\nreturn { computeBackgroundCore, _bgFailure };')();

function enclosingFunction(lineIdx) {
  let start = lineIdx;
  while (start >= 0 && !/^(async )?function [A-Za-z_$][\w$]*\(/.test(lines[start])) start--;
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return { name: lines[start].match(/function ([\w$]+)/)[1], body: lines.slice(start, i + 1).join('\n') };
  }
  throw new Error('unbalanced function around line ' + (lineIdx + 1));
}

// Codex impl round 1: the guard must not be evadable by another call form, an alias,
// a chained use or a check placed after consumption. Every textual reference to a
// PRODUCER outside the DISPATCHERS must be one of exactly two forms:
//   (A) `[const|let|var] NAME = [be.length ? ]PRODUCER(` or a destructuring
//       `{ ..., bg, ... } = _recordBackground(` — and the FIRST later reference to
//       NAME in its function must be `_bgFailure(NAME)`;
//   (B) `_bgFailure(PRODUCER(` — an inline refusal; an (A) site later in the same
//       function is then covered by it (runFit refuses up front).
// Anything else — `(computeBackground)(`, `computeBackground (`, an alias, a
// `return ...computeBackground(...).map(...)` — fails.
const PRODUCERS = ['computeBackground', 'computeBackgroundCore', '_computeBackgroundForSource', '_recordBackground'];
const DISPATCHERS = ['computeBackground', 'computeBackgroundCore', '_computeBackgroundForSource', '_recordBackground'];
const stripComment = l => l.replace(/\/\/.*$/, '');

test('every computed background is checked for convergence by its consumer (class guard)', () => {
  const sites = [];
  const ref = new RegExp('\\b(' + PRODUCERS.join('|') + ')\\b');
  lines.forEach((raw, i) => {
    const l = stripComment(raw);
    if (!ref.test(l) || /^\s*(async )?function /.test(l)) return;
    const fn = enclosingFunction(i);
    if (DISPATCHERS.includes(fn.name)) return;
    sites.push({ line: i + 1, text: l.trim(), fn, idx: i });
  });
  assert.ok(sites.length >= 11, 'found the consumers: ' + sites.map(s => s.fn.name).join(', '));
  const P = '(?:' + PRODUCERS.join('|') + ')';
  const formA = new RegExp('^(?:(?:const|let|var)\\s+)?([A-Za-z_$][\\w$]*)\\s*=\\s*(?:be\\.length \\? )?' + P + '\\(');
  const formAd = new RegExp('^\\(?(?:(?:const|let|var)\\s+)?\\{[^}]*\\bbg\\b[^}]*\\}\\s*=\\s*_recordBackground\\(');
  const formB = new RegExp('_bgFailure\\(' + P + '\\(');
  for (const s of sites) {
    if (formB.test(s.text)) continue;
    let name = null;
    const a = s.text.match(formA);
    if (a) name = a[1];
    else if (formAd.test(s.text)) name = 'bg';
    assert.ok(name, `${s.fn.name} (line ${s.line}): a producer referenced outside the two allowed forms: ${s.text}`);
    // covered by an earlier inline refusal in the same function?
    const before = s.fn.body.slice(0, s.fn.body.indexOf(s.text));
    if (formB.test(before)) continue;
    // the FIRST later reference to NAME in the function must be the check
    const after = s.fn.body.slice(s.fn.body.indexOf(s.text) + s.text.length).split('\n').map(stripComment).join('\n');
    const esc = name.replace(/\$/g, '\\$');
    const m = after.match(new RegExp('\\b' + esc + '\\b'));
    const isCheck = m && after.slice(Math.max(0, m.index - 11), m.index) === '_bgFailure(' && after[m.index + name.length] === ')';
    assert.ok(isCheck,
      `${s.fn.name} (line ${s.line}): the first use of ${name} after it is computed is not _bgFailure(${name})`);
  }
});

test('computeBackgroundCore marks a non-converged background and its plain reason', () => {
  const cyc = B.computeBackgroundCore([0, 1, 2, 3], [2, 3, 10, 13], { bgType: 'shirley', endpointAvg: '1', bgStart: '', bgEnd: '' });
  assert.strictEqual(cyc.converged, false);
  assert.match(B._bgFailure(cyc), /^Shirley background not converged: its iteration did not settle on a solution/);
  const flat = B.computeBackgroundCore([0, 1, 2, 3, 4], [10, 5, 5, 17, 20], { bgType: 'smart', endpointAvg: '1', bgStart: '', bgEnd: '' });
  assert.match(B._bgFailure(flat), /no net signal/);
  const ok = B.computeBackgroundCore([0, 1, 2, 3, 4, 5], [10, 12, 40, 30, 22, 20], { bgType: 'shirley', endpointAvg: '1', bgStart: '', bgEnd: '' });
  assert.strictEqual(ok.converged, true);
  assert.strictEqual(B._bgFailure(ok), null);
  for (const t of ['linear', 'none']) assert.strictEqual(B.computeBackgroundCore([0, 1, 2], [1, 2, 3], { bgType: t, endpointAvg: '1', bgStart: '', bgEnd: '' }).converged, true);
});

test('the note under the method menu shows the failure and hides when it clears', () => {
  const src = lines.slice(lines.findIndex(l => l.startsWith('function _refreshBgConvergenceNote(')));
  const fnSrc = enclosingFunction(lines.findIndex(l => l.startsWith('function _refreshBgConvergenceNote('))).body;
  const el = { style: {}, textContent: '', dataset: {} };
  const refresh = new Function('document', fnSrc + '\nreturn _refreshBgConvergenceNote;')({ getElementById: id => id === 'bg-not-converged' ? el : null });
  refresh('Shirley background not converged: x.');
  assert.strictEqual(el.style.display, 'block');
  assert.match(el.textContent, /^Shirley background not converged: x\. Nothing is subtracted or fitted against it/);
  refresh(null);
  assert.strictEqual(el.style.display, 'none');
  assert.strictEqual(src.length > 0, true);
  assert.match(html, /<div id="bg-not-converged" role="alert"/);
});

test('Run Fit refuses a non-converged background before anything changes (no undo entry, no spinner, no request)', () => {
  const body = enclosingFunction(lines.findIndex(l => l.startsWith('async function runFit('))).body;
  const check = body.indexOf('_bgFailure(computeBackground(');
  assert.ok(check > 0);
  for (const later of ['pushUndo()', '_showFitSpinner()', 'uploadToBackend(', 'runFitLocal(']) {
    const at = body.indexOf(later);
    assert.ok(at > check, `${later} comes after the convergence refusal`);
  }
});

test('Auto-Fit refuses in its preflight, before it claims the tab (a running Run Fit is left alone)', () => {
  const body = enclosingFunction(lines.findIndex(l => l.startsWith('async function runAutoFitC1sGraphite('))).body;
  assert.ok(body.indexOf('_bgFailure(bgI)') > 0 && body.indexOf('_bgFailure(bgI)') < body.indexOf('_installFitOp(afOp)'));
});

test('the Shirley iterations setting is retired (hidden; kept for saved files and fit keys)', () => {
  assert.match(html, /<div class="field" style="display:none" aria-hidden="true">\s*<label>Shirley iterations<\/label>/);
  const core = enclosingFunction(lines.findIndex(l => l.startsWith('function computeBackgroundCore('))).body;
  assert.ok(!/shirleyIter/.test(core.replace(/\/\/.*$/mg, '')), 'computeBackgroundCore does not read it');
});

test('the background tooltips say the noise bias plainly (findings F2)', () => {
  const tip = v => html.match(new RegExp('<option value="' + v + '" data-tip="([^"]*)"'))[1];
  assert.match(tip('smart'), /raises net area by about 1 % on noisy data/);
  assert.match(tip('smart_exp'), /raises net area by about 1 % on noisy data/);
  assert.match(tip('smart_exp'), /plain Shirley carries its own bias at large steps/);
  assert.match(tip('shirley'), /its own net-area bias at large background steps/);
  assert.match(html, /<option value="shirley_linear" disabled hidden/, 'shirley_linear stays off the menu');
  assert.match(html, /id="bg-legacy-note"/, 'its notice stays');
});
