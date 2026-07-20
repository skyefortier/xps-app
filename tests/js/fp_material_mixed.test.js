// MIXED material class (2026-07-20 unit) -- Find Peaks modal must offer a
// clear label ("mixed (analyte in matrix)" reads better than bare "mixed")
// and an advisory note: MIXED does not correct for differential charging,
// it only stops ASSUMING there isn't any. Per the DECIDED scope
// (Skye, 2026-07-17), the note must describe the charge reference as not
// necessarily transferring to the analyte -- it must never imply the app
// has corrected for anything.

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

test('FP_STRINGS.materials.mixed has a clear, non-bare label', () => {
  assert.ok(FP_STRINGS.materials && FP_STRINGS.materials.mixed,
    'FP_STRINGS.materials.mixed must exist');
  const label = FP_STRINGS.materials.mixed.label;
  assert.match(label, /mixed/i);
  assert.match(label, /analyte/i);
  assert.notStrictEqual(label, 'mixed');
});

test('FP_STRINGS.materials.mixed hint is advisory, never claims correction', () => {
  const hint = FP_STRINGS.materials.mixed.hint;
  assert.match(hint, /charge reference/i);
  assert.match(hint, /uncertain|not.*apply|may not/i);
  // must not imply the app corrected for differential charging
  assert.doesNotMatch(hint, /has been corrected/i);
  assert.doesNotMatch(hint, /automatically adjust/i);
  assert.doesNotMatch(hint, /we (have )?correct/i);
});

test('FP_STRINGS has no override entries for the other 3 material classes '
     + '(dropdown rendering must stay byte-identical for them)', () => {
  const materials = FP_STRINGS.materials || {};
  for (const v of ['conductor', 'semiconductor', 'insulator']) {
    assert.strictEqual(materials[v], undefined,
      `${v} must not get an FP_STRINGS override -- non-MIXED rendering `
      + 'must be unchanged');
  }
});

test('FP_STRINGS.materials.mixed hint names C 1s specifically and does not '
     + 'overstate scope to other regions (Codex run B MAJOR, 77bf3a8 recheck)', () => {
  // "Peak width limits are relaxed accordingly" (no region named) reads as
  // global -- a chemist picking MIXED for U 4f/Cl 2p/B 1s/N 1s would wrongly
  // believe peak widths changed there too. Only C 1s contamination/
  // adventitious widths actually relax.
  const hint = FP_STRINGS.materials.mixed.hint;
  assert.match(hint, /C ?1s/);
  assert.match(hint, /other regions are unaffected|only C ?1s|no effect on other regions/i);
});
