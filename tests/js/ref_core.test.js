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

// --- marker-lifetime predicates (A1: overlays persist independent of palette) ---
test('elementOverlayVisible no longer depends on the palette being open', () => {
  // A1: overlays persist after the palette closes — visible with panelOpen either way…
  assert.strictEqual(RefCore.elementOverlayVisible({ panelOpen: true,  activeChart: true,  isStackTab: false }), true);
  assert.strictEqual(RefCore.elementOverlayVisible({ panelOpen: false, activeChart: true,  isStackTab: false }), true);
  // …still NOT on stack tabs…
  assert.strictEqual(RefCore.elementOverlayVisible({ panelOpen: true,  activeChart: true,  isStackTab: true  }), false);
  assert.strictEqual(RefCore.elementOverlayVisible({ panelOpen: false, activeChart: true,  isStackTab: true  }), false);
  // …still only on the active chart…
  assert.strictEqual(RefCore.elementOverlayVisible({ panelOpen: true,  activeChart: false, isStackTab: false }), false);
  assert.strictEqual(RefCore.elementOverlayVisible({ panelOpen: false, activeChart: false, isStackTab: false }), false);
  // …and compound-marker behavior is unchanged (always visible / persistent).
  assert.strictEqual(RefCore.compoundMarkerVisible(), true);
});

// --- A0: data-tier color SSOT ---
test('tierColor is a single source of truth for the three data tiers', () => {
  assert.strictEqual(RefCore.tierColor('curated'), '#3ddc84');   // green
  assert.strictEqual(RefCore.tierColor('machine'), '#b48eff');   // violet
  assert.strictEqual(RefCore.tierColor('legacy'),  '#ffbb44');   // amber
});
test('tierColor falls back safely for unknown/missing tiers', () => {
  assert.strictEqual(RefCore.tierColor('nonsense'), RefCore.TIER_COLORS.fallback);
  assert.strictEqual(RefCore.tierColor(undefined),  RefCore.TIER_COLORS.fallback);
});

// --- A3: shared residue-aware color assignment (nextColorIdx) ---
test('nextColorIdx returns the first index whose palette residue is unused', () => {
  assert.strictEqual(RefCore.nextColorIdx([0, 5, 2], 8), 1);   // residues {0,5,2} → 1 free
});
test('nextColorIdx falls back to max(used)+1 once every residue is taken', () => {
  assert.strictEqual(RefCore.nextColorIdx([0, 1, 2], 3), 3);   // palette of 3 fully used → reuse
  assert.strictEqual(RefCore.nextColorIdx([], 8), 0);          // none used → 0
});
test('nextColorIdx: a new pick shares no rendered residue with existing overlays (while residues remain)', () => {
  const used = [0, 5, 2];
  const usedResidues = new Set(used.map(c => c % 8));
  assert.ok(!usedResidues.has(RefCore.nextColorIdx(used, 8) % 8));
});
test('nextColorIdx ignores invalid entries (non-integer/negative) when computing the used set', () => {
  assert.strictEqual(RefCore.nextColorIdx([0, -1, NaN, 1.5, '2', null, 1], 8), 2);  // valid {0,1} → first free 2
});

// --- A5: floating-palette viewport clamp (stale/offscreen positions clamp safe) ---
test('clampToViewport: an in-bounds position passes through unchanged', () => {
  assert.deepStrictEqual(RefCore.clampToViewport(100, 80, 520, 400, 1200, 800, 8), { left: 100, top: 80 });
});
test('clampToViewport: negative / above-left position clamps to the margin', () => {
  assert.deepStrictEqual(RefCore.clampToViewport(-300, -50, 520, 400, 1200, 800, 8), { left: 8, top: 8 });
});
test('clampToViewport: far off-screen (stale) position clamps inside the viewport', () => {
  const c = RefCore.clampToViewport(5000, 5000, 520, 400, 1200, 800, 8);
  assert.strictEqual(c.left, 1200 - 520 - 8);          // 672 — fully visible horizontally
  assert.strictEqual(c.top, 800 - 80 - 8);             // 712 — header band stays reachable
});
test('clampToViewport: non-finite (corrupt saved) coords fall back to the margin', () => {
  assert.deepStrictEqual(RefCore.clampToViewport(NaN, undefined, 520, 400, 1200, 800, 8), { left: 8, top: 8 });
});

// --- B1: pure, versioned serialize/deserialize (overlays + compound markers) ---
const PAL = 8;   // stand-in palette length so these tests don't depend on ELEMENT_MARKER_COLORS

test('overlays and compound markers have independent (decoupled) version constants', () => {
  assert.strictEqual(typeof RefCore.REF_OVERLAYS_VERSION, 'number');
  assert.strictEqual(typeof RefCore.REF_COMPOUND_MARKERS_VERSION, 'number');
});

// serialize: total, deterministic, identify-free
test('serializeRefOverlays is total: null for empty/nullish/malformed sel', () => {
  for (const bad of [undefined, null, 42, 'x', {}, { syms: [] }, { syms: 'no' }]) {
    assert.strictEqual(RefCore.serializeRefOverlays(bad), null);
  }
});
test('serializeRefOverlays captures selection and never emits identify keys', () => {
  const sel = { syms: [{ sym: 'Ti', colorIdx: 0, tier: 'machine' }, { sym: 'Cu', colorIdx: 1, tier: 'curated' }],
                source: 'MgKa', showWeak: true, includeAuger: true, tolEv: 0.9, _refIdentify: { be: 1 } };
  const out = RefCore.serializeRefOverlays(sel);
  assert.strictEqual(out.v, RefCore.REF_OVERLAYS_VERSION);
  assert.deepStrictEqual(out.syms, [{ sym: 'Ti', colorIdx: 0, tier: 'machine' }, { sym: 'Cu', colorIdx: 1, tier: 'curated' }]);
  assert.strictEqual(out.source, 'MgKa');
  assert.ok(!('tolEv' in out) && !('cands' in out) && !('_refIdentify' in out));
});

// round-trip: valid colorIdx verbatim
test('round-trip preserves a valid colorIdx verbatim', () => {
  const sel = { syms: [{ sym: 'Fe', colorIdx: 3, tier: 'machine' }], source: 'AlKa', showWeak: false, includeAuger: false };
  const back = RefCore.deserializeRefOverlays(RefCore.serializeRefOverlays(sel), PAL);
  assert.deepStrictEqual(back.syms, [{ sym: 'Fe', colorIdx: 3, tier: 'machine' }]);
  assert.strictEqual(back.source, 'AlKa');
});

// deserialize totality: absent / envelope-malformed / newer-version
test('deserialize: absent or envelope-malformed → clean empty (no throw)', () => {
  for (const bad of [undefined, null, {}, 42, 'x', { syms: [{ sym: 'Cu', colorIdx: 0 }] }/*no v*/,
                     { v: '1', syms: [] }/*non-numeric v*/, { v: 1, syms: 'garbage' }]) {
    assert.deepStrictEqual(RefCore.deserializeRefOverlays(bad, PAL).syms, []);
  }
});
test('deserialize: newer internal version is ignored (no misread of a future shape)', () => {
  assert.deepStrictEqual(RefCore.deserializeRefOverlays({ v: 999, syms: [{ sym: 'Cu', colorIdx: 0 }] }, PAL).syms, []);
});

// deserialize entry repair: skip no-sym, repair colorIdx, keep unknown tier, dedup sym
test('deserialize entry repair: keep valid, skip no-sym, repair invalid colorIdx, keep unknown tier', () => {
  const back = RefCore.deserializeRefOverlays({ v: 1, source: 'bogus', showWeak: 'yes',
    syms: [{ sym: 'Cu', colorIdx: 0, tier: 'curated' },
           { colorIdx: 1 },                        // no sym → dropped
           { sym: 'Ti', colorIdx: -3 },            // invalid colorIdx → by-position helper fallback
           { sym: 'Xe', colorIdx: 2, tier: 'weird' }, // unknown tier → kept (fallback-colored at render)
           { sym: 'Cu', colorIdx: 7 }] }, PAL);
  assert.deepStrictEqual(back.syms.map(s => s.sym), ['Cu', 'Ti', 'Xe']);   // no-sym dropped; duplicate Cu → keep first
  assert.strictEqual(back.syms[0].colorIdx, 0);                            // Cu verbatim
  assert.ok(Number.isInteger(back.syms[1].colorIdx) && back.syms[1].colorIdx >= 0); // Ti repaired
  assert.notStrictEqual(back.syms[1].colorIdx % PAL, 0 % PAL);            // distinct residue from Cu
  assert.strictEqual(back.syms[2].tier, 'weird');                         // unknown tier preserved (entry kept)
  assert.strictEqual(back.source, 'AlKa');                                // invalid source → default
  assert.strictEqual(back.showWeak, true);                               // 'yes' coerced to bool
});

// rendered-color determinism end to end
test('post-load next pick renders a color distinct from all restored while residues remain', () => {
  const back = RefCore.deserializeRefOverlays({ v: 1,
    syms: [{ sym: 'Cu', colorIdx: 0 }, { sym: 'Ti', colorIdx: 5 }, { sym: 'Fe', colorIdx: 2 }] }, PAL);
  const usedResidues = new Set(back.syms.map(s => s.colorIdx % PAL));
  const next = RefCore.nextColorIdx(back.syms.map(s => s.colorIdx), PAL);
  assert.ok(!usedResidues.has(next % PAL));                              // distinct RENDERED color
});

// compound markers: global scope, totality, partial-invalid, newer-version
test('serializeRefCompoundMarkers is total: null for empty/nullish/non-array', () => {
  for (const bad of [undefined, null, [], 'x', 42, {}]) {
    assert.strictEqual(RefCore.serializeRefCompoundMarkers(bad), null);
  }
});
test('serializeRefCompoundMarkers is total for malformed ARRAY ENTRIES (no throw; all-invalid → null)', () => {
  // non-object entries and non-finite be must not throw and must not emit an
  // invalid marker — an all-invalid array yields null (no valid marker remains).
  assert.strictEqual(RefCore.serializeRefCompoundMarkers([null]), null);
  assert.strictEqual(RefCore.serializeRefCompoundMarkers([undefined]), null);
  assert.strictEqual(RefCore.serializeRefCompoundMarkers([42]), null);
  assert.strictEqual(RefCore.serializeRefCompoundMarkers([{ be: 'bad' }]), null);
});
test('serializeRefCompoundMarkers: mixed valid+invalid → invalid be dropped, valid kept', () => {
  const out = RefCore.serializeRefCompoundMarkers([
    null,                                                   // non-object → skipped
    { sym: 'Cu', state: 'Cu2O', be: 932.5, ref: 'NIST' },  // valid
    { be: 'bad' },                                          // non-finite be → dropped
    { state: 'surface', be: 530.1 },                       // no sym → tolerated
  ]);
  assert.strictEqual(out.v, RefCore.REF_COMPOUND_MARKERS_VERSION);
  assert.deepStrictEqual(out.markers.map(m => m.be), [932.5, 530.1]);   // invalid dropped, valid kept
  assert.strictEqual(out.markers[0].sym, 'Cu');
  assert.ok(!('sym' in out.markers[1]));                                // absent sym tolerated
});
test('compound markers round-trip at global scope; absent/malformed/newer → empty', () => {
  const markers = [{ sym: 'Cu', state: 'Cu2O', be: 932.5, ref: 'NIST' }];
  const out = RefCore.serializeRefCompoundMarkers(markers);
  assert.strictEqual(out.v, RefCore.REF_COMPOUND_MARKERS_VERSION);
  assert.deepStrictEqual(RefCore.deserializeRefCompoundMarkers(out), markers);
  assert.deepStrictEqual(RefCore.deserializeRefCompoundMarkers(undefined), []);          // absent
  assert.deepStrictEqual(RefCore.deserializeRefCompoundMarkers({ v: 1, markers: 'x' }), []); // envelope-malformed
  assert.deepStrictEqual(RefCore.deserializeRefCompoundMarkers({}), []);                  // no v
  assert.deepStrictEqual(RefCore.deserializeRefCompoundMarkers({ v: 999, markers: [{ be: 1 }] }), []); // newer version
});
test('compound markers: non-finite be dropped, absent sym tolerated (partial-invalid)', () => {
  const back = RefCore.deserializeRefCompoundMarkers({ v: 1, markers: [
    { state: 'surface', be: 530.1 },          // no sym → tolerated
    { sym: 'Cu', state: 'Cu2O', be: 'bad' },  // non-finite be → dropped
    { sym: 'Fe', be: 711 }] });
  assert.deepStrictEqual(back.map(m => m.be), [530.1, 711]);
});
