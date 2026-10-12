// A link the server cannot fit as drawn is refused, never dropped (Q10 0c′, owner 2026-10-11):
// _linkGraphFailure (page) and fitting._validate_constraint_graph (server) — a link to a peak
// that is gone, a self-link, a cycle, a link across lineshapes, two peaks sharing an id. Real-browser checks of Run Fit
// and Batch Fit: tests/test_browser_link_graph_refusal.py.
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
const fail = new Function(extractFn('_linkGraphFailure') + '\nreturn _linkGraphFailure;')();
const P = (id, shape, linked, name) => ({ id, shape, linked: linked ?? null, name: name || ('P' + id) });

test('a valid graph passes: unlinked peaks, a doublet, a chain in any order', () => {
  assert.strictEqual(fail([P(1, 'GL'), P(2, 'GL')]), null);
  assert.strictEqual(fail([P(1, 'Voigt'), P(2, 'Voigt', 1)]), null);
  assert.strictEqual(fail([P(3, 'DS', 2), P(2, 'DS', 1), P(1, 'DS')]), null);
  assert.strictEqual(fail([P(1, 'GL', undefined)]), null);
  assert.strictEqual(fail([P(1, 'GL', '')]), null, 'an empty link is no link');
});

test('a link to a peak that is gone, a self-link, a cycle, a link across lineshapes are refused, by name', () => {
  assert.match(fail([P(3, 'GL', 2, 'orphan'), P(1, 'GL')]), /^"orphan" is linked to a peak that is no longer in the model/);
  assert.match(fail([P(1, 'GL', 1, 'self')]), /^"self" is linked to itself/);
  assert.match(fail([P(1, 'GL', 2, 'a'), P(2, 'GL', 1, 'b')]), /is in a circle of links/);
  assert.match(fail([P(1, 'GL', undefined, 'parent'), P(2, 'Voigt', 1, 'child')]),
    /^"child" is linked to "parent" but has a different lineshape \(Voigt, GL\); a linked peak takes its parent's lineshape/);
  // two peaks with one id: the server's route refuses them ("Duplicate peak ids"); so does the page
  assert.match(fail([P(1, 'GL', undefined, 'first'), P(1, 'GL', undefined, 'second')]), /^"first" and "second" share one internal id, so the model is ambiguous/);
  assert.match(fail([P(1, 'GL', undefined, 'root'), P(2, 'GL', 1, 'c1'), P(2, 'GL', 1, 'c2')]), /^"c1" and "c2" share one internal id/);
  // ids match exactly, as getPeak and the local engine match them
  assert.match(fail([P(1, 'GL'), P(2, 'GL', '1')]), /no longer in the model/, '"1" is not peak 1');
});

test('the request names each peak\'s page lineshape, and every fit path refuses an invalid graph first', () => {
  assert.match(extractFn('peakToBackendSpec'), /frontend_shape: p\.shape,/);
  assert.match(extractFn('runFit'), /const linkFail = _linkGraphFailure\(opts\.startPeaks \|\| state\.peaks\);[^\n]*\n\s+if \(linkFail\) \{ notify\('Fit not run: ' \+ linkFail, 'red', true\); return; \}\n\s+const \{ be, inten \} = getROIData\(\);/,
    'Run Fit and Use this solution: before the background, the undo entry and any request');
  assert.match(extractFn('runFitLocal'), /\{ const linkFail = _linkGraphFailure\(work\); if \(linkFail\) return fail\(linkFail\); \}/, 'the local engine');
  assert.match(extractFn('runPropagation'), /const batchLinkFail = _linkGraphFailure\(state\.peaks\);[^\n]*\n\s+if \(batchLinkFail\) \{ notify\('Batch fit not run: ' \+ batchLinkFail, 'red', true\); return; \}/,
    'Batch Fit: before any target is changed');
  const rp = extractFn('runPropagation');
  assert.ok(rp.indexOf('batchLinkFail') < rp.indexOf('btn.disabled = true'), 'before the batch starts');
});
