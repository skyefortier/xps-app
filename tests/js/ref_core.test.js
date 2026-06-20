const { test } = require('node:test');
const assert = require('node:assert');
const RefCore = require('../../static/js/ref_identify_core.js');

test('tolFromSlider clamps to [0.25, 5.0] and snaps to 0.25', () => {
  assert.strictEqual(RefCore.tolFromSlider(1), 1);
  assert.strictEqual(RefCore.tolFromSlider(0.1), 0.25);
  assert.strictEqual(RefCore.tolFromSlider(9), 5);
  assert.strictEqual(RefCore.tolFromSlider(1.1), 1);
  assert.strictEqual(RefCore.tolFromSlider(1.13), 1.25);
  assert.strictEqual(RefCore.tolFromSlider('2.5'), 2.5);
  assert.strictEqual(RefCore.tolFromSlider(NaN), 1);
});

test('coerceTolToEv maps legacy modes onto the base, passes numbers through', () => {
  assert.strictEqual(RefCore.coerceTolToEv('narrow', 1.0), 0.5);
  assert.strictEqual(RefCore.coerceTolToEv('normal', 1.0), 1.0);
  assert.strictEqual(RefCore.coerceTolToEv('broad', 1.0), 2.0);
  assert.strictEqual(RefCore.coerceTolToEv(0.75, 1.0), 0.75);
  assert.strictEqual(RefCore.coerceTolToEv('garbage', 1.3), RefCore.tolFromSlider(1.3));
  assert.strictEqual(RefCore.coerceTolToEv(undefined, 1.3), RefCore.tolFromSlider(1.3));
});

// Shared fixtures (defined once; Task 3 reuses them). GROUPS is the superset
// including Si 2p so the subshell-only key path has coverage downstream.
const ELS = [
  { sym: 'U', name: 'Uranium', z: 92, tier: 'curated' },
  { sym: 'O', name: 'Oxygen',  z: 8,  tier: 'curated' },
  { sym: 'Cu', name: 'Copper', z: 29, tier: 'machine' },
];
const GROUPS = [
  { orbital_key: 'U 4f7/2', element: 'U', z: 92, orbital: '4f7/2',
    states: [ { id:'u1', state: 'UO2', be_ev: 380.0, ref: 'NIST', source:'legacy-embedded-dataset' },
              { id:'u2', state: 'UCl4', be_ev: 382.1, ref: 'lit', source:'legacy-embedded-dataset' } ] },
  { orbital_key: 'Si 2p', element: 'Si', z: 14, orbital: '2p',
    states: [ { id:'si1', state: 'SiO2', be_ev: 103.5, ref: 'NIST', source:'legacy-embedded-dataset' } ] },
  { orbital_key: 'C 1s', element: 'C', z: 6, orbital: '1s',
    states: [ { id:'c1', state: 'Graphite', be_ev: 284.5, ref: 'Moulder', source:'legacy-embedded-dataset' } ] },
];

test('blendedSearch matches elements by symbol/name', () => {
  assert.ok(RefCore.blendedSearch('ura', ELS, GROUPS).some(r => r.kind === 'element' && r.sym === 'U'));
});
test('blendedSearch matches compounds, tagged compound', () => {
  const hit = RefCore.blendedSearch('uo2', ELS, GROUPS).find(r => r.kind === 'compound');
  assert.ok(hit && hit.sym === 'U' && /UO2/.test(hit.label));
});
test('blendedSearch numeric query yields energy rows', () => {
  assert.ok(RefCore.blendedSearch('284', ELS, GROUPS).some(r => r.kind === 'energy' && /284\.5/.test(r.ev)));
});
test('blendedSearch caps results and empty query returns []', () => {
  assert.deepStrictEqual(RefCore.blendedSearch('', ELS, GROUPS), []);
  assert.ok(RefCore.blendedSearch('u', ELS, GROUPS, { limit: 2 }).length <= 2);
});
