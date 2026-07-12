// Find Peaks progress-indicator pure helpers — JS twin of the shipped
// _fpFormatElapsed / _fpProgressText in templates/index.html (2026-07-11).
//
// These format the REAL engine sweep signal (candidate N of M,
// screening/stabilizing, elapsed seconds) polled from
// GET /api/analyze/progress/<job_id> — never a fake animation. Pinned here
// so the wording/timing math can't silently drift; the actual polling
// loop + DOM wiring is covered by the Playwright browser test (real
// fetch/timers/DOM), which this file deliberately does not duplicate.

const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(
  path.join(__dirname, '../../templates/index.html'), 'utf8');

function extract(re, name) {
  const m = html.match(re);
  assert.ok(m, name + ' not found in templates/index.html');
  return m[0];
}

const ctx = eval('(function(){\n'
  + extract(/function _fpFormatElapsed\(sec\) \{[\s\S]*?\n\}/, '_fpFormatElapsed') + '\n'
  + extract(/function _fpProgressText\(poll\) \{[\s\S]*?\n\}/, '_fpProgressText') + '\n'
  + 'return { _fpFormatElapsed, _fpProgressText };\n})()');
const { _fpFormatElapsed, _fpProgressText } = ctx;

test('_fpFormatElapsed: sub-minute seconds', () => {
  assert.strictEqual(_fpFormatElapsed(0), '0s');
  assert.strictEqual(_fpFormatElapsed(7), '7s');
  assert.strictEqual(_fpFormatElapsed(59), '59s');
});

test('_fpFormatElapsed: minutes + seconds', () => {
  assert.strictEqual(_fpFormatElapsed(60), '1m 0s');
  assert.strictEqual(_fpFormatElapsed(125), '2m 5s');
  assert.strictEqual(_fpFormatElapsed(239.6), '4m 0s');   // rounds first
});

test('_fpFormatElapsed: never negative, tolerates junk input', () => {
  assert.strictEqual(_fpFormatElapsed(-5), '0s');
  assert.strictEqual(_fpFormatElapsed(null), '0s');
  assert.strictEqual(_fpFormatElapsed(undefined), '0s');
  assert.strictEqual(_fpFormatElapsed(NaN), '0s');
});

test('_fpProgressText: real candidate-sweep message', () => {
  const text = _fpProgressText({
    elapsed_sec: 47, message: 'candidate 7 of 29 — stabilizing (A2_linked)',
  });
  assert.strictEqual(text,
    'Analyzing… 47s — candidate 7 of 29 — stabilizing (A2_linked)');
});

test('_fpProgressText: starting phase before any candidate has run', () => {
  const text = _fpProgressText({ elapsed_sec: 0, message: 'starting analysis…' });
  assert.strictEqual(text, 'Analyzing… 0s — starting analysis…');
});

test('_fpProgressText: missing/malformed poll degrades to a generic message, never throws', () => {
  assert.strictEqual(_fpProgressText({}), 'Analyzing… 0s — working…');
  assert.strictEqual(_fpProgressText(null), 'Analyzing… 0s — working…');
  assert.strictEqual(_fpProgressText(undefined), 'Analyzing… 0s — working…');
});
