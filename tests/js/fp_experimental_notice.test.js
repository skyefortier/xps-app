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

test('FP_STRINGS.experimentalNotice says BOTH "starting point" and '
     + '"not a final answer" -- either alone is not the safety claim', () => {
  // Codex-caught (both runs, round 1): an any-of match would still pass
  // if the copy dropped the "not a final answer" half of the claim.
  const notice = FP_STRINGS.experimentalNotice;
  assert.match(notice, /starting point/i);
  assert.match(notice, /not a final answer/i);
});

test('FP_STRINGS.experimentalNotice does not overclaim correctness and '
     + 'does not describe the app as broken/frozen', () => {
  // Codex-caught (both runs, round 1): the point of the notice is to
  // PREVENT a user from concluding the app is frozen -- if the copy itself
  // used that word, the safety framing would be self-defeating. Reject it
  // outright rather than just rejecting unrelated words like "guarantee".
  const notice = FP_STRINGS.experimentalNotice;
  assert.doesNotMatch(notice, /guarantee/i);
  assert.doesNotMatch(notice, /accurate/i);
  assert.doesNotMatch(notice, /frozen/i);
  assert.doesNotMatch(notice, /broken/i);
});

test('the notice banner element and its dismiss button are wired to the '
     + 'actual dismiss function, not just present somewhere in the page', () => {
  const banner = extract(/<div id="fp-experimental-notice"[\s\S]*?<\/div>/,
    '#fp-experimental-notice banner');
  assert.match(banner, /onclick="_fpDismissExperimentalNotice\(\)"/,
    'the banner\'s own button must call the dismiss function directly');
});

test('both notice functions read/write the SAME localStorage key -- a '
     + 'mismatched key would show the notice every time despite dismissal', () => {
  const keyDecl = extract(
    /const FP_EXPERIMENTAL_NOTICE_LS_KEY = '[^']+';/,
    'FP_EXPERIMENTAL_NOTICE_LS_KEY declaration');
  const keyName = 'FP_EXPERIMENTAL_NOTICE_LS_KEY';
  const gate = extract(/function _fpMaybeShowExperimentalNotice\(\) \{[\s\S]*?\n\}/,
    '_fpMaybeShowExperimentalNotice');
  const dismiss = extract(/function _fpDismissExperimentalNotice\(\) \{[\s\S]*?\n\}/,
    '_fpDismissExperimentalNotice');
  assert.match(gate, new RegExp(`localStorage\\.getItem\\(${keyName}\\)`),
    'the gate must read the SAME named constant, not a duplicated literal '
    + 'that could drift from the one the dismiss handler writes');
  assert.match(dismiss, new RegExp(`localStorage\\.setItem\\(${keyName},`),
    'the dismiss handler must write the SAME named constant the gate reads');
  assert.ok(keyDecl, 'sanity: the constant itself must be declared');
});

test('the gate function early-returns (hides, does not show) when '
     + 'already dismissed, and only sets text+shows in the un-dismissed path', () => {
  // Structural check on control flow, not just "these tokens appear
  // somewhere": split the function on its guard `if` block and confirm
  // hide+return lives INSIDE it while text-set+show lives strictly AFTER.
  const gate = extract(/function _fpMaybeShowExperimentalNotice\(\) \{[\s\S]*?\n\}/,
    '_fpMaybeShowExperimentalNotice');
  const guardMatch = gate.match(/if \(localStorage\.getItem\([^)]*\)\) \{([\s\S]*?)\}/);
  assert.ok(guardMatch, 'expected an `if (localStorage.getItem(...)) { ... }` guard');
  const guardBody = guardMatch[1];
  const afterGuard = gate.slice(gate.indexOf(guardMatch[0]) + guardMatch[0].length);
  assert.match(guardBody, /style\.display = 'none'/,
    'the dismissed-already branch must hide the banner');
  assert.match(guardBody, /return/,
    'the dismissed-already branch must return before falling through');
  assert.doesNotMatch(guardBody, /textContent/,
    'the dismissed-already branch must not set the notice text');
  assert.match(afterGuard, /textContent = *\n? *FP_STRINGS\.experimentalNotice/,
    'the un-dismissed path must set the real notice text');
  assert.match(afterGuard, /style\.display = 'block'/,
    'the un-dismissed path must show the banner');
});

test('openFindPeaksModal calls the notice gate so it actually shows on open', () => {
  const fn = extract(/async function openFindPeaksModal\(\) \{[\s\S]*?\n\}/,
    'openFindPeaksModal');
  assert.match(fn, /_fpMaybeShowExperimentalNotice\(\)/);
});
