// Find Peaks expanded element/region selector — JS twin of the shipped
// pure helpers in templates/index.html (2026-07-11, unit 3).
//
// FP's coverage-tier vocabulary (curated/machine/structure_only) is
// DELIBERATELY DIFFERENT from RefCore's reference-DATA tier system
// (curated/machine/legacy) — this one grades whether Find Peaks has cited
// FITTING GRAMMAR for a region, not whether an energy value is
// well-sourced. See autofit/coverage_index.py's module docstring.

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
  + extract(/const FP_TIER_META = \{[\s\S]*?\n\};/, 'FP_TIER_META') + '\n'
  + extract(/function _fpRegionMatchesFilter\(entry, query\) \{[\s\S]*?\n\}/, '_fpRegionMatchesFilter') + '\n'
  + extract(/function _fpRegionOptionLabel\(entry\) \{[\s\S]*?\n\}/, '_fpRegionOptionLabel') + '\n'
  + extract(/function _fpBuildRegionOptions\(coverage, query\) \{[\s\S]*?\n\}/, '_fpBuildRegionOptions') + '\n'
  + extract(/function _fpTierNoteFor\(entries\) \{[\s\S]*?\n\}/, '_fpTierNoteFor') + '\n'
  + 'return { FP_TIER_META, _fpRegionMatchesFilter, _fpRegionOptionLabel, '
  + '_fpBuildRegionOptions, _fpTierNoteFor };\n})()');
const { FP_TIER_META, _fpRegionMatchesFilter, _fpRegionOptionLabel,
        _fpBuildRegionOptions, _fpTierNoteFor } = ctx;

const SAMPLE = [
  { region: 'C 1s', symbol: 'C', z: 6, name: 'Carbon', level: '1s',
    tier: 'curated', note: 'Cited fitting grammar.', roi: { be_min: 278, be_max: 298, basis: 'grammar' } },
  { region: 'Fe 2p', symbol: 'Fe', z: 26, name: 'Iron', level: '2p',
    tier: 'machine', note: 'Sourced, not cited grammar.', roi: { be_min: 700, be_max: 720, basis: 'sourced' } },
  { region: 'Fe 3d', symbol: 'Fe', z: 26, name: 'Iron', level: '3d',
    tier: 'structure_only', note: 'No position at all.', roi: null },
  { region: 'H 1s', symbol: 'H', z: 1, name: 'Hydrogen', level: '1s',
    tier: 'structure_only', note: 'No position at all.', roi: null },
];

test('FP_TIER_META defines all three tiers with a color and short label', () => {
  for (const t of ['curated', 'machine', 'structure_only']) {
    assert.ok(FP_TIER_META[t], t);
    assert.ok(typeof FP_TIER_META[t].color === 'string' && FP_TIER_META[t].color);
    assert.ok(typeof FP_TIER_META[t].tag === 'string' && FP_TIER_META[t].tag);
  }
});

test('_fpRegionMatchesFilter: empty query matches everything', () => {
  for (const e of SAMPLE) assert.strictEqual(_fpRegionMatchesFilter(e, ''), true);
});

test('_fpRegionMatchesFilter: matches by symbol (case-insensitive, prefix)', () => {
  assert.strictEqual(_fpRegionMatchesFilter(SAMPLE[1], 'fe'), true);
  assert.strictEqual(_fpRegionMatchesFilter(SAMPLE[1], 'FE'), true);
  assert.strictEqual(_fpRegionMatchesFilter(SAMPLE[3], 'fe'), false);
});

test('_fpRegionMatchesFilter: matches by element name substring', () => {
  assert.strictEqual(_fpRegionMatchesFilter(SAMPLE[1], 'iron'), true);
  assert.strictEqual(_fpRegionMatchesFilter(SAMPLE[1], 'ir'), true);
  assert.strictEqual(_fpRegionMatchesFilter(SAMPLE[0], 'iron'), false);
});

test('_fpRegionMatchesFilter: matches by level/subshell', () => {
  assert.strictEqual(_fpRegionMatchesFilter(SAMPLE[1], '2p'), true);
  assert.strictEqual(_fpRegionMatchesFilter(SAMPLE[2], '3d'), true);
  assert.strictEqual(_fpRegionMatchesFilter(SAMPLE[1], '3d'), false);
});

test('_fpRegionMatchesFilter: matches the full region label', () => {
  assert.strictEqual(_fpRegionMatchesFilter(SAMPLE[0], 'c 1s'), true);
});

test('_fpRegionOptionLabel: includes the tier tag, region, and element name', () => {
  const label = _fpRegionOptionLabel(SAMPLE[0]);
  assert.match(label, /C 1s/);
  assert.match(label, /Carbon/);
  assert.match(label, new RegExp(FP_TIER_META.curated.tag.replace(/[[\]]/g, '\\$&')));
});

test('_fpRegionOptionLabel: structure_only region is tagged distinctly from curated', () => {
  const curatedLabel = _fpRegionOptionLabel(SAMPLE[0]);
  const structOnlyLabel = _fpRegionOptionLabel(SAMPLE[2]);
  assert.notStrictEqual(
    curatedLabel.match(/^\[[^\]]+\]/)[0],
    structOnlyLabel.match(/^\[[^\]]+\]/)[0]);
});

test('_fpBuildRegionOptions: no query returns everything, sorted stably by input order', () => {
  const opts = _fpBuildRegionOptions(SAMPLE, '');
  assert.strictEqual(opts.length, SAMPLE.length);
  assert.deepStrictEqual(opts.map(o => o.value), SAMPLE.map(e => e.region));
});

test('_fpBuildRegionOptions: filters by query, each option carries its tier', () => {
  const opts = _fpBuildRegionOptions(SAMPLE, 'fe');
  assert.deepStrictEqual(opts.map(o => o.value), ['Fe 2p', 'Fe 3d']);
  assert.strictEqual(opts[0].tier, 'machine');
  assert.strictEqual(opts[1].tier, 'structure_only');
});

test('_fpBuildRegionOptions: an unmatched query yields an empty list (never throws)', () => {
  assert.deepStrictEqual(_fpBuildRegionOptions(SAMPLE, 'xyz-nonexistent'), []);
});

test('_fpBuildRegionOptions: tolerates a missing/empty coverage array', () => {
  assert.deepStrictEqual(_fpBuildRegionOptions(undefined, 'fe'), []);
  assert.deepStrictEqual(_fpBuildRegionOptions([], 'fe'), []);
});

test('_fpTierNoteFor: single curated selection shows its own note', () => {
  const text = _fpTierNoteFor([SAMPLE[0]]);
  assert.match(text, /Cited fitting grammar/);
});

test('_fpTierNoteFor: single fallback (machine) selection is honestly labeled', () => {
  const text = _fpTierNoteFor([SAMPLE[1]]);
  assert.match(text, /Sourced, not cited grammar/);
  assert.doesNotMatch(text.toLowerCase(), /cited fitting grammar\.$/);
});

test('_fpTierNoteFor: structure_only selection says no reference position', () => {
  const text = _fpTierNoteFor([SAMPLE[2]]);
  assert.match(text, /No position at all/);
});

test('_fpTierNoteFor: no selection is an empty string (never throws)', () => {
  assert.strictEqual(_fpTierNoteFor([]), '');
  assert.strictEqual(_fpTierNoteFor(undefined), '');
});

test('_fpTierNoteFor: multi-region selection lists each region+tier', () => {
  const text = _fpTierNoteFor([SAMPLE[0], SAMPLE[1]]);
  assert.match(text, /C 1s/);
  assert.match(text, /Fe 2p/);
});
