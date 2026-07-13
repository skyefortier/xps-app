// Find Peaks periodic-table region picker — JS twin of the pure
// selection-logic helpers in templates/index.html (2026-07-13, unit 2 of
// the "Find Peaks UI improvements round 2" session). The picker replaces
// the flat <select multiple> region list; DOM-touching render functions
// (_fpRenderPtGrid, _fpRenderExpandedPanel, ...) are exercised by the
// Playwright browser tests instead — this file covers only the DOM-free
// selection-set math and tier-ranking logic.

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
  + extract(/const FP_TIER_RANK = \{[^;]*\};/, 'FP_TIER_RANK') + '\n'
  + extract(/function _fpBestTier\(entries\) \{[\s\S]*?\n\}/, '_fpBestTier') + '\n'
  + extract(/function _fpNextSelection\(current, region, additive\) \{[\s\S]*?\n\}/, '_fpNextSelection') + '\n'
  + 'return { FP_TIER_RANK, _fpBestTier, _fpNextSelection };\n})()');
const { FP_TIER_RANK, _fpBestTier, _fpNextSelection } = ctx;

// ── _fpBestTier ─────────────────────────────────────────────────────────

test('_fpBestTier: curated wins over machine and structure_only', () => {
  const t = _fpBestTier([{ tier: 'structure_only' }, { tier: 'curated' }, { tier: 'machine' }]);
  assert.strictEqual(t, 'curated');
});

test('_fpBestTier: machine wins over structure_only when no curated present', () => {
  const t = _fpBestTier([{ tier: 'structure_only' }, { tier: 'machine' }]);
  assert.strictEqual(t, 'machine');
});

test('_fpBestTier: empty entries -> null (an element with zero practical coverage)', () => {
  assert.strictEqual(_fpBestTier([]), null);
});

test('FP_TIER_RANK: strictly orders curated > machine > structure_only', () => {
  assert.ok(FP_TIER_RANK.curated > FP_TIER_RANK.machine);
  assert.ok(FP_TIER_RANK.machine > FP_TIER_RANK.structure_only);
});

// ── _fpNextSelection ────────────────────────────────────────────────────

test('_fpNextSelection: plain click on a fresh region replaces an existing single selection', () => {
  const next = _fpNextSelection(new Set(['C 1s']), 'Fe 2p', false);
  assert.deepStrictEqual(Array.from(next), ['Fe 2p']);
});

test('_fpNextSelection: plain click replaces a multi-region selection with just the clicked one', () => {
  const next = _fpNextSelection(new Set(['C 1s', 'Fe 2p']), 'N 1s', false);
  assert.deepStrictEqual(Array.from(next), ['N 1s']);
});

test('_fpNextSelection: plain click on the ONLY already-selected region is a no-op (stays selected)', () => {
  const current = new Set(['Fe 2p']);
  const next = _fpNextSelection(current, 'Fe 2p', false);
  assert.deepStrictEqual(Array.from(next), ['Fe 2p']);
});

test('_fpNextSelection: additive click ADDS a second region (ctrl-click co-fit)', () => {
  const next = _fpNextSelection(new Set(['C 1s']), 'Fe 2p', true);
  assert.deepStrictEqual(new Set(next), new Set(['C 1s', 'Fe 2p']));
});

test('_fpNextSelection: additive click on an already-selected region REMOVES it', () => {
  const next = _fpNextSelection(new Set(['C 1s', 'Fe 2p']), 'Fe 2p', true);
  assert.deepStrictEqual(Array.from(next), ['C 1s']);
});

test('_fpNextSelection: additive click on the last remaining region empties the selection', () => {
  const next = _fpNextSelection(new Set(['Fe 2p']), 'Fe 2p', true);
  assert.deepStrictEqual(Array.from(next), []);
});

test('_fpNextSelection: never mutates the `current` Set passed in', () => {
  const current = new Set(['C 1s']);
  _fpNextSelection(current, 'Fe 2p', true);
  assert.deepStrictEqual(Array.from(current), ['C 1s']);
});
