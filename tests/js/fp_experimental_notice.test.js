// Find Peaks experimental notice (2026-07-20): the "BETA" badge and the
// existing blurb ("starting suggestions to review — not final answers")
// never told a student the RUNTIME. A student clicking "Suggest peaks" with
// no idea it can take up to 4 minutes may reasonably conclude the app is
// frozen. This is the one UX addition that protects users rather than adds
// convenience: a one-time notice, shown on first open, dismissed permanently
// via localStorage.

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

const FP_STRINGS = eval(
  '(' + extract(/const FP_STRINGS = \{[\s\S]*?\n\};/, 'FP_STRINGS')
    .replace(/^const FP_STRINGS = /, '').replace(/;$/, '') + ')');

test('FP_STRINGS.experimentalNotice names it experimental and states the '
     + 'runtime range', () => {
  const notice = FP_STRINGS.experimentalNotice;
  assert.ok(notice, 'FP_STRINGS.experimentalNotice must exist');
  assert.match(notice, /experimental/i);
  assert.match(notice, /60/);
  assert.match(notice, /240/);
});

test('FP_STRINGS.experimentalNotice says results are a starting point, '
     + 'not a final answer', () => {
  const notice = FP_STRINGS.experimentalNotice;
  assert.match(notice, /starting point|not a final answer|review/i);
});

test('FP_STRINGS.experimentalNotice does not overclaim correctness or '
     + 'imply the app is frozen/broken during a long run', () => {
  const notice = FP_STRINGS.experimentalNotice;
  assert.doesNotMatch(notice, /guarantee/i);
  assert.doesNotMatch(notice, /accurate/i);
});

test('the notice DOM wiring exists: banner element, dismiss handler, and '
     + 'a localStorage-backed one-time gate', () => {
  assert.match(html, /id="fp-experimental-notice"/);
  assert.match(html, /function _fpDismissExperimentalNotice/);
  assert.match(html, /function _fpMaybeShowExperimentalNotice/);
  // must actually persist the dismissal, not just hide it for the session
  const fn = extract(/function _fpDismissExperimentalNotice\(\) \{[\s\S]*?\n\}/,
    '_fpDismissExperimentalNotice');
  assert.match(fn, /localStorage\.setItem/);
  const gate = extract(/function _fpMaybeShowExperimentalNotice\(\) \{[\s\S]*?\n\}/,
    '_fpMaybeShowExperimentalNotice');
  assert.match(gate, /localStorage\.getItem/);
});

test('openFindPeaksModal calls the notice gate so it actually shows on open', () => {
  const fn = extract(/async function openFindPeaksModal\(\) \{[\s\S]*?\n\}/,
    'openFindPeaksModal');
  assert.match(fn, /_fpMaybeShowExperimentalNotice\(\)/);
});
