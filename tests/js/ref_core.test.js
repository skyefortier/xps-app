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

// --- parseChemKey (revision #4) ---
test('parseChemKey: exact spin-orbit key', () => {
  assert.deepStrictEqual(RefCore.parseChemKey('Ti 2p3/2'), { sym: 'Ti', orbital: '2p3/2', targets: ['2p3/2'] });
  assert.deepStrictEqual(RefCore.parseChemKey('U 4f7/2'),  { sym: 'U',  orbital: '4f7/2', targets: ['4f7/2'] });
});
test('parseChemKey: subshell-only p attaches to BOTH spin-orbit lines (Si 2p)', () => {
  assert.deepStrictEqual(RefCore.parseChemKey('Si 2p'), { sym: 'Si', orbital: '2p', targets: ['2p3/2', '2p1/2'] });
});
test('parseChemKey: 1s has no split', () => {
  assert.deepStrictEqual(RefCore.parseChemKey('C 1s'), { sym: 'C', orbital: '1s', targets: ['1s'] });
});

// --- compoundCandidatesFrom: surface ALL within tol, no evidence filter (revision #2) ---
test('compoundCandidatesFrom returns legacy candidates within tol, honest proximity', () => {
  const cands = RefCore.compoundCandidatesFrom(GROUPS, 380.4, 1.0);
  assert.strictEqual(cands.length, 1);            // UO2 (380.0) within ±1.0; UCl4 (382.1) out
  const c = cands[0];
  assert.strictEqual(c.sym, 'U');
  assert.strictEqual(c.dataTier, 'legacy');
  assert.strictEqual(c.isCompound, true);
  assert.strictEqual(c.hasRegion, false);
  assert.strictEqual(c.energyMatch, 'moderate');  // |Δ|=0.4, tol/2=0.5 -> not strong, honest proximity
  assert.deepStrictEqual(c.orbitalTargets, ['4f7/2']);
});

// --- tier cap across ALL THREE surfaces (revision #3) ---
test('capConfidenceByTier: curated/machine keep candidate label + raw energyMatch', () => {
  assert.deepStrictEqual(RefCore.capConfidenceByTier(90, 'strong', 'curated'),
    { label: 'Strong candidate', labelCls: 'strong', energyText: 'strong' });
  assert.deepStrictEqual(RefCore.capConfidenceByTier(90, 'strong', 'machine'),
    { label: 'Strong candidate', labelCls: 'strong', energyText: 'strong' });
});
test('capConfidenceByTier: legacy noun is "Legacy hint", energy annotated, never Strong', () => {
  assert.deepStrictEqual(RefCore.capConfidenceByTier(90, 'strong', 'legacy'),
    { label: 'Legacy hint', labelCls: 'legacy', energyText: 'strong (confidence capped by source tier)' });
  assert.deepStrictEqual(RefCore.capConfidenceByTier(10, 'weak', 'legacy'),
    { label: 'Legacy hint', labelCls: 'legacy', energyText: 'weak (confidence capped by source tier)' });
});

// --- ranking preserved Δ-primary; GOLDEN element-only order (revision #1) ---
const GOLD_ELEMENTS = [
  { id: 'U-4f7', sym: 'U', be: 380.9, dist: 0.4, score: 88, dataTier: 'curated', isAuger: false },
  { id: 'U-4f5', sym: 'U', be: 391.8, dist: 0.9, score: 70, dataTier: 'curated', isAuger: false },
  { id: 'O-1s',  sym: 'O', be: 530.0, dist: 1.2, score: 60, dataTier: 'curated', isAuger: false },
];
test('mergeAndRankCandidates: element-only golden order is Δ-primary', () => {
  const r = RefCore.mergeAndRankCandidates(GOLD_ELEMENTS, []);
  assert.deepStrictEqual(r.map(c => c.id), ['U-4f7', 'U-4f5', 'O-1s']);
});
test('adding compounds does not perturb the element subsequence', () => {
  const compounds = [
    { id: 'UO2', sym: 'U', be: 380.0, dist: 0.5, score: 45, dataTier: 'legacy', isAuger: false, isCompound: true },
  ];
  const r = RefCore.mergeAndRankCandidates(GOLD_ELEMENTS, compounds);
  const elemOrder = r.filter(c => !c.isCompound).map(c => c.id);
  assert.deepStrictEqual(elemOrder, ['U-4f7', 'U-4f5', 'O-1s']);   // unchanged
  // UO2 (Δ0.5) vs U-4f7 (Δ0.4) differ by 0.1 (<=0.5): tier tie-break -> curated before legacy.
  assert.strictEqual(r[0].id, 'U-4f7');
});
test('mergeAndRankCandidates: a clear Δ winner ranks first regardless of tier', () => {
  const near = { id: 'leg', sym: 'X', be: 100.1, dist: 0.1, score: 30, dataTier: 'legacy', isAuger: false };
  const far  = { id: 'cur', sym: 'Y', be: 101.6, dist: 1.6, score: 95, dataTier: 'curated', isAuger: false };
  assert.strictEqual(RefCore.mergeAndRankCandidates([far], [near])[0].id, 'leg');
});

// --- physics assertions (revision #6) ---
test('augerApparentBE shifts with source; photoelectronBE is source-invariant', () => {
  const al = RefCore.augerApparentBE(910, 1486.6, 4.5);
  const mg = RefCore.augerApparentBE(910, 1253.6, 4.5);
  assert.notStrictEqual(al, mg);
  assert.ok(Math.abs((1486.6 - 910 - 4.5) - al) < 1e-9);
  assert.strictEqual(RefCore.photoelectronBE(284.5), 284.5);
});
test('compound BE equals input be_ev (no ccShift, source-invariant)', () => {
  const c = RefCore.compoundCandidatesFrom(GROUPS, 284.5, 1.0).find(x => x.sym === 'C');
  assert.strictEqual(c.be, 284.5);
});

// --- marker-lifetime predicates (revision #5) ---
test('elementOverlayVisible is gated; compoundMarkerVisible is always true', () => {
  assert.strictEqual(RefCore.elementOverlayVisible({ panelOpen: true,  activeChart: true,  isStackTab: false }), true);
  assert.strictEqual(RefCore.elementOverlayVisible({ panelOpen: false, activeChart: true,  isStackTab: false }), false);
  assert.strictEqual(RefCore.elementOverlayVisible({ panelOpen: true,  activeChart: true,  isStackTab: true  }), false);
  assert.strictEqual(RefCore.elementOverlayVisible({ panelOpen: true,  activeChart: false, isStackTab: false }), false);
  assert.strictEqual(RefCore.compoundMarkerVisible(), true);
});
