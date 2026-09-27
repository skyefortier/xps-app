// F3 (2026-09-27, sweep M5): the Auto-Fit C1s gate judges the DATA the fit
// would use — for the active tab the live selection getROIData() returns, for
// any other record its saved window over its own corrected data — never the
// active tab's record ui (synced only on a tab switch or save) and never the
// typed midpoint of a window that reaches past the data.
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
const lines = html.split('\n');
function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name + '\\(');
  const start = lines.findIndex(l => re.test(l));
  assert.ok(start >= 0, name);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail('unbalanced ' + name);
}

// a wide scan 270-420 eV (C 1s and a U 4f doublet), 0.5 eV steps
const RAW = Array.from({ length: 301 }, (_, i) => 420 - 0.5 * i);
function gate({ activeId, liveSel }) {
  const tabManager = { activeId };
  const getROIData = () => ({ be: liveSel, inten: liveSel.map(() => 1) });
  return new Function('tabManager', 'getROIData', extractFn('isC1sTab') + '\nreturn isC1sTab;')(tabManager, getROIData);
}
const sel = (lo, hi) => RAW.filter(v => v >= lo && v <= hi);

test('the sweep reproduction: record window on C 1s, U 4f typed in the fields (no tab switch) — the gate CLOSES', () => {
  const tab = { id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '280', roiMax: '295' } };   // stale record ui
  assert.strictEqual(gate({ activeId: 't1', liveSel: sel(370, 415) })(tab), false, 'judged on the live U 4f selection');
  assert.strictEqual(gate({ activeId: 't1', liveSel: sel(280, 295) })(tab), true, 'a live C 1s selection passes');
});

test('the SELECTED data decide, not the typed midpoint of a window that reaches past the data', () => {
  // data 280-300 only; typed 250-400 -> typed midpoint 325 (not C 1s) but the selection is all C 1s
  const narrow = RAW.filter(v => v >= 280 && v <= 300);
  const tab = { id: 't1', rawBE: narrow, ccShift: 0, ui: { roiMin: '250', roiMax: '400' } };
  assert.strictEqual(gate({ activeId: 't1', liveSel: narrow })(tab), true);
  assert.strictEqual(gate({ activeId: 't1', liveSel: [] })(tab), false, 'an empty selection is not C 1s');
});

test('a non-active record is judged on its saved window over its own corrected data', () => {
  const g = gate({ activeId: 'other', liveSel: sel(370, 415) });
  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '280', roiMax: '295' } }), true);
  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '370', roiMax: '415' } }), false);
  // the window is in the CORRECTED frame, as the fit is: at a 100 eV shift, corrected 280-295 selects raw
  // 380-395, which exists — judged as C 1s; a window the shifted data do not reach selects nothing
  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 100, ui: { roiMin: '280', roiMax: '295' } }), true);
  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 200, ui: { roiMin: '280', roiMax: '295' } }), false,
    'corrected 70-220 has no point in 280-295: nothing selected');
  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: {} }), false, 'no window: the whole 270-420 scan, midpoint 345');
  assert.strictEqual(g({ id: 't1', rawBE: [], ui: {} }), false);
});

test('the record path makes the SAME selection getROIData() makes (Codex round 1)', () => {
  const g = gate({ activeId: 'other', liveSel: [] });
  // reversed bounds select nothing, exactly as the live selector does
  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '295', roiMax: '280' } }), false);
  // a blank bound is open on its own side only: 270-295 is C 1s
  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '', roiMax: '295' } }), true);
  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '370', roiMax: '' } }), false);
});

test('every caller of the gate passes the ACTIVE tab record (menu state, charge-reference permission, the Auto-Fit run)', () => {
  for (const fn of ['_recomputeAutoFitMenuState', '_isChargeRefAllowed', 'runAutoFitC1sGraphite']) {
    const src = extractFn(fn);
    const lookup = src.search(/const tab = [^;]*tabManager\._getTab\(tabManager\.activeId\)/);
    assert.ok(lookup >= 0, fn + ': the tab is looked up by tabManager.activeId');
    assert.ok(src.indexOf('isC1sTab(tab)') > lookup, fn + ': and that tab is the one judged');
    assert.ok(!/\btab\s*=(?!=)/.test(src.slice(lookup + 10, src.indexOf('isC1sTab(tab)'))), fn + ': not reassigned in between');
  }
  // and the ROI fields refresh the menu on every keystroke
  assert.match(html, /id="roi-min"[^>]*oninput="updatePlot\(\);_recomputeAutoFitMenuState\(\)"/);
  assert.match(html, /id="roi-max"[^>]*oninput="updatePlot\(\);_recomputeAutoFitMenuState\(\)"/);
});

for (const order of ['inactive first', 'active first']) for (const inactiveId of ['t1', 'inactive'])
test(`BEHAVIOURAL: each caller hands isC1sTab the ACTIVE record (${order}, inactive id "${inactiveId}") (Codex rounds 2-3)`, async () => {
  const inactive = { id: inactiveId, rawBE: RAW, ccShift: 0, ui: { roiMin: '280', roiMax: '295' } };   // C 1s
  const active   = { id: 't2', rawBE: RAW, ccShift: 0, ui: { roiMin: '370', roiMax: '415' } };           // U 4f
  const seen = [];
  const isC1sTab = t => { seen.push(t); return false; };
  const tabs = order === 'inactive first' ? [inactive, active] : [active, inactive];
  const tabManager = { activeId: 't2', tabs, _getTab: id => tabs.find(t => t.id === id) };
  const el = { disabled: false, value: 'c1s', setAttribute() {}, removeAttribute() {}, title: '' };
  const document = { getElementById: () => el };
  const notes = [];
  const deps = { tabManager, isC1sTab, document, notify: (m, k) => notes.push([m, k]), state: { rawBE: RAW, peaks: [] } };
  const src = ['_recomputeAutoFitMenuState', '_isChargeRefAllowed', 'runAutoFitC1sGraphite'].map(extractFn).join('\n');
  const fns = new Function(...Object.keys(deps), src + '\nreturn { _recomputeAutoFitMenuState, _isChargeRefAllowed, runAutoFitC1sGraphite };')(...Object.values(deps));
  fns._recomputeAutoFitMenuState();
  fns._isChargeRefAllowed();
  await fns.runAutoFitC1sGraphite();                 // returns at the gate (isC1sTab false)
  assert.strictEqual(seen.length, 3, 'each caller consulted the gate once');
  for (const t of seen) assert.strictEqual(t, active, 'the active record, never ' + (t && t.id));
  assert.ok(notes.some(([m]) => /only available for C1s spectra/.test(m)), 'the run stopped at the gate');
});
