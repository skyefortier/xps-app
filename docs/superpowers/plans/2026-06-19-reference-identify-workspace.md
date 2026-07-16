# Reference / Identify Workspace — Implementation Plan (rev 2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Unify the docked Reference panel (`#ref-panel`) and the separate NIST Lookup modal (`#nist-modal-overlay`) into one chart-adjacent right drawer; relocate clicked-element details out from under the Identify control; make Identify return compounds as well as elements; and convert tolerance to a continuous slider — without regressing physics, provenance, accessibility, or existing ranking/marker behavior.

**Architecture:** The existing `#ref-panel` is *widened and restructured into a three-zone right drawer* (search → periodic table → details); it is never a centered overlay, so the chart stays clickable for Identify. All new correctness-critical logic is extracted into **one** dependency-free UMD module `static/js/ref_identify_core.js` (`RefCore`), which is the **shipped** module (no copied fallback in `index.html`) and is unit-tested with the built-in `node:test` runner. DOM/Chart.js work is browser-verified on dev gunicorn. The NIST modal and its `_nist*` functions are retired, but the **chemical-state marker lifetime is preserved**: element overlays stay panel-gated/per-tab/stack-excluded, while compound markers stay **global and persistent** ("mark it, close the panel, it stays"). No Python backend changes.

**Tech Stack:** Vanilla JS in `templates/index.html` (no build step), Chart.js v4 (CDN), Flask/Jinja render, Node ≥18 built-in `node:test` for the pure core, existing pytest suite as a backend no-regression gate.

**Rev-2 changes** (folding Codex's verified findings against `aa6ffac`): ranking is preserved Δ-primary with golden tests (#1); no insufficient-evidence filter — surface all 52 chem states as of this plan's authoring, now 51 after a 2026-07-16 provenance-audit removal (a self-citation entry; see tests/test_chem_state_tier.py) (#2); tier-cap applied across all three confidence surfaces with a "Legacy hint" noun (#3); `parseChemKey` normalizes mixed-granularity keys (#4); markers unify render/style but **keep both lifetimes** (#5); physics assertion tests added (#6); RefCore is the single shipped module, cache-busted, no inline fallback (#7); the search dropdown is a body-portal fixed popover, not a z-index escape (#8).

---

## As-Built Addendum (2026-06-22)

The feature was implemented task-by-task on `feature-reference-identify-workspace`.
This addendum records where the build deviated from or extended the written task
specs below; the task sections are otherwise accurate.

**Deltas from the written spec:**

1. **Task 5A added — uniform periodic-table grid (Decision 2).** A dedicated task
   (not "later polish"): `_refRenderGrid` applies one `.selectable` class to every
   activatable cell regardless of tier; the three tier-coloured cell rules
   (`.ref-pt-cell.curated/.machine/.legacy`) were removed. Tier now surfaces only in
   the cell tooltip and the result-card badge. Cell a11y (`tabindex`, `role="button"`,
   `aria-pressed`, Enter/Space `onkeydown`) preserved verbatim.
2. **Task 5 — Identify controls moved to the search zone (Decision 1).**
   `_refRenderIdentify` was split into `_refRenderIdentifyControls` (arm button +
   tolerance slider + Auger toggle → **search zone**) and `_refRenderIdentifyResults`
   (candidate cards → **details zone**). No Identify control sits above the element
   cards in Details.
3. **Tolerance slider drag refinement.** The slider uses `oninput="_refTolPreview()"`
   (readout-only, no rebuild) + `onchange="_refSetTol()"` (commit + re-run on release),
   instead of a single `oninput` that would rebuild the panel mid-drag and destroy the
   slider element.
4. **`energyMatch` for compounds → `'moderate'`.** A self-inconsistency in the written
   Task 3 (impl `dist <= tol/2 ? 'strong'` vs the test asserting `'moderate'`) was
   reconciled in favour of the test and the principle: a chemical-state record lacks
   the expected-region evidence `'strong'` requires, so it tops out at `'moderate'`.
   The plan snippet was updated to match.
5. **Task 9 — full modal retirement (Codex caveat).** Deleted the modal HTML, its CSS,
   and ALL seven `_nist*` functions (not just repointing the button), closing the
   dual-shape marker window. The only remaining `m.orbital` reads (draw + chips) keep
   the `(m.sym || m.orbital || '')` fallback. `_accChemicalStates()` is now orphaned
   (left in place — Stage-9 accessor layer with parity fixtures).
6. **Test invocation.** Use `node --test tests/js/*.test.js` (the bare-directory form
   is not globbed on Node ≥21).

**Plan → commit map** (branch `feature-reference-identify-workspace`):

| Step | Commit | Step | Commit |
|---|---|---|---|
| Mockup decision-lock | `449e793` | T5A uniform grid | `eebbb82` |
| T1 RefCore + tolerance | `6c517a1` | T6 portal search | `e491f19` |
| Test-cmd fix | `606de27` | T7 compounds in Identify | `86a111b` |
| T2 blended search | `aec6319` | T8 marker unification | `39cff4a` |
| T3 keys/compounds/tier/rank/physics | `9b7bfc3` | T9 retire modal | `5aa827b` |
| T4 three-zone drawer | `50b1dc6` | T10 polish | `847eb2a` |
| T5 tolerance slider + Decision 1 | `eb24909` | T11 final verify | (no code) |

**Verification status at T11:** JS core suite 18/18; backend pytest structurally
unaffected (branch changes no `.py` / `data/` files; no test references the removed
NIST identifiers; the two failing tests are pre-existing data-generation failures
present on `main`, re-confirmed by a branch-vs-main run); no RefCore function defined
inline in `index.html`; no `be + ccShift` in any reference path. Browser pass pending.

---

## Testing Strategy (READ FIRST — one non-obvious decision for sign-off)

This project has **no frontend test harness** by design (single-file vanilla JS, no build step; CLAUDE.md mandates browser verification on dev gunicorn :5151). The writing-plans skill mandates TDD. Because the hard constraint is "no regression of physics, provenance, or ranking," verification is split:

- **Pure, correctness-critical logic → automated `node:test`.** Tolerance mapping, blended search, key normalization, compound-candidate construction, tier-confidence cap, candidate merge/rank, and the physics projection helpers are extracted into `static/js/ref_identify_core.js` as a UMD module (sets `module.exports` for Node, `globalThis.RefCore` for the browser — standard shim, **no build step, zero npm dependencies**), with failing-test-first TDD via `node --test tests/js/*.test.js`. This includes **golden ordering tests** (#1) and **physics assertions** (#6). (Use the explicit `*.test.js` glob — a bare `node --test tests/js/` directory arg is not globbed on Node ≥21 and errors trying to load the directory as a module.)
- **DOM / Chart.js / layout / markers / popover positioning → browser verification** on :5151 (the established project pattern), each task carrying an explicit, concrete manual checklist. Lifetime/style behaviors that cannot be unit-tested (panel-closed persistence, stack-tab exclusion, popover-while-scrolled) are pinned by **pure predicates** in RefCore *and* a manual browser check.
- **Backend → untouched.** `pytest tests/ -v` runs at the end as a no-regression gate (catches a Jinja/template breakage that would stop the page rendering).

**RefCore is the shipped module — no inline duplicate (#7).** `index.html` must contain zero copies of the tested functions; it loads and calls the module, and disables the reference feature loudly if the module is absent (never a silent inline fallback). A grep step enforces this.

**If you'd rather not add `static/js/` + `tests/js/` at all**, say so at sign-off; Tasks 1–3 collapse into inline functions verified manually, but you lose automated protection on exactly the physics/provenance/ranking code you asked not to regress.

**Branch:** `feature-reference-identify-workspace` off `main`.

---

## File Structure

| File | Responsibility | Action |
|---|---|---|
| `static/js/ref_identify_core.js` | Pure, DOM-free logic (the shipped module). UMD (Node + browser global `RefCore`). | Create |
| `tests/js/ref_core.test.js` | `node:test` unit tests, incl. golden ordering + physics assertions. | Create |
| `templates/index.html` | Drawer restructure, tolerance slider, compound Identify, unified search (portal popover), marker rename/rewire, modal retirement, polish. | Modify |
| `docs/superpowers/plans/2026-06-19-reference-identify-workspace.md` | This plan. | Create (committed for review) |

**Confirmed code anchors** (verified against `aa6ffac`; re-grep before editing):

- Static serving: `app.py:63` (`static_folder="static"`). No `static/` tree exists yet — create `static/js/`.
- Tokens (`:root`): `templates/index.html:14-39` (`--bg #0d0f14`, `--bg2 #131720`, `--bg3 #1a2030`, `--border`, `--border2`, `--accent #4a9eff`, `--green #3ddc84`, `--amber #ffbb44`, `--text #e8edf5`, `--text2 #8a9ab8`, `--text3 #4a5a78`, `--mono`, `--sans`; `--accent2`, `--accent-dim`, `--green-dim`, `--amber-dim`, `--purple`, `--purple-dim` exist).
- Drawer shell: `:2017-2022`. Drawer CSS width 340px: `:172-181`. Reusable ref classes: `:194-319`.
- Sel state: `_refDefaultSel()` `:10221-10222`; `_refGetSel()` `:10232-10234` (stores `tab._refSel`, **runtime-only** — not in `buildTabData` `:8348`).
- Tolerance: `_refToleranceEv()` `:10935-10950`; `_refSetTolMode()` `:11108-11111`.
- Identify: `_refIdentifyAt()` `:10972-11093` — **sort is Δ-primary → tier(≤0.5 eV) → score → PE>Auger** at `:11068-11078`; element candidate shape `:11056-11064`; score→label at `:11085-11088`; `energyMatch` sub-label at `:11060-11061`. Render: `_refRenderIdentify()` `:11140-11200`; the rendered noun ("… candidate") at `:11183`.
- Chart click route: `handleChartClick` `:4890`, identify branch `:4903-4913`.
- Panel render: `_refRenderPanel()` `:10661-10727`.
- **Marker lifetimes (revision #5):**
  - Compound/NIST markers are **GLOBAL/persistent**: `_nistMarkers` const `:9989`; drawn by `overlayPlugin.afterDraw` → `_drawNistMarkers(chart)` `:7861-7862`; plugin registered in the chart `plugins:[...]` array `:7889`; draw impl `_drawNistMarkers` `:10108-10135`.
  - Element overlays are **panel-gated/per-tab/stack-excluded**: `xpsRefLinesPlugin.afterDraw` `:10792`, fed by `_refChartItems(chart)` `:10729-10749` which returns null unless `_refPanelOpen && _refPayload && chart===state.chart && !chart._xpsStackTabId && !isStackTab(tab)`.
- NIST modal: HTML `:11865-11877`; functions `showNistModal` `:9992`, `_nistFilter` `:10001`, `_nistRenderResults` `:10005`, `_nistAddMarker` `:10039`, `_nistRemoveMarker` `:10047`, `_nistRenderMarkerChips` `:10054`, `_nistClearAll` `:10066`. Lookup button `:1666`; disabled list referencing `btn-nist-lookup` `:2429`.
- Chemical-state data: `data/xps/legacy/chemical-states.json` — 11 groups / 52 states as of this plan's authoring, now 51 states after a 2026-07-16 provenance-audit removal (a self-citation entry unrelated to this plan's scope); **mixed-granularity keys**: spin-orbit-resolved (`Ti 2p3/2`, `Fe 2p3/2`, `Cu 2p3/2`, `U 4f7/2`, `Cl 2p3/2`, `Au 4f7/2`, `S 2p3/2`) and subshell-only (`Si 2p` — the only p/d/f subshell key; `C 1s`, `O 1s`, `N 1s`). Each group has `orbital_key`,`element`,`z`,`orbital`,`states[{id,state,be_ev,ref,source,tier}]`. Reduced by `_accChemicalStates()` `:10411` to `{state, be, ref}` — **uniformly `legacy-unverified`, no per-state evidence predicate exists** (revision #2).

---

## Behavior changes the user should expect (call-outs, not bugs)

1. **Ranking is unchanged for elements.** Compounds enter the *same* Δ-primary comparator; the existing tier tie-break (within ~0.5 eV) already demotes legacy at similar Δ. Golden tests pin the element-only order so adding compounds cannot perturb it (revision #1).
2. **All chem states surface** (52 as of this plan's authoring, 51 after a 2026-07-16 provenance-audit self-citation removal) as candidates within tolerance — tier-capped and badged legacy. No evidence filter (none exists at runtime); a per-state evidence schema is noted as future curation, out of scope (revision #2).
3. **Tier caps confidence on every surface for legacy items (elements *and* compounds)** (revision #3): the overall noun renders **"Legacy hint"** (not "Strong/Possible/Weak candidate"); the energy sub-label stays honest but is annotated "(confidence capped by source tier)". Today element-legacy lines can read "Strong candidate" — they no longer will.
4. **Tolerance, once moved by the user, sticks** (absolute eV, seeded from the resolution-aware auto-base). The "not charge corrected" hint still shows but no longer force-widens a user-chosen value.
5. **Compound markers remain global/persistent**; element overlays remain panel-gated. Marking a compound, then closing the drawer, keeps the marker (revision #5).

---

### Task 1: `RefCore` scaffold (shipped module) + tolerance core

**Files:** Create `static/js/ref_identify_core.js`, `tests/js/ref_core.test.js`; Modify `templates/index.html` (one cache-busted `<script src>` + absence guard).

- [ ] **Step 1: Confirm Node ≥18**

Run: `node --version` — expect `v18+`. If lower, STOP and tell the user.

- [ ] **Step 2: Write the failing test**

Create `tests/js/ref_core.test.js`:

```js
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
```

- [ ] **Step 3: Run to verify it fails**

Run: `node --test tests/js/*.test.js` — FAIL: `Cannot find module '.../ref_identify_core.js'`.

- [ ] **Step 4: Create the UMD module**

Create `static/js/ref_identify_core.js`:

```js
/*
 * ref_identify_core.js — pure, DOM-free logic for the Reference / Identify
 * workspace. THE SHIPPED MODULE: index.html must not copy these functions.
 * UMD: require()-able in Node (tests) and a browser global (RefCore). No build
 * step, no dependencies. Keep pure — no document/window/state references.
 */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.RefCore = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const TOL_MIN = 0.25, TOL_MAX = 5.0, TOL_STEP = 0.25, TOL_DEFAULT = 1.0;

  function tolFromSlider(value) {
    let v = Number(value);
    if (!isFinite(v)) v = TOL_DEFAULT;
    v = Math.min(TOL_MAX, Math.max(TOL_MIN, v));
    v = Math.round(v / TOL_STEP) * TOL_STEP;
    return Math.round(v * 100) / 100;
  }

  function coerceTolToEv(stored, base) {
    const b = tolFromSlider(base);
    if (typeof stored === 'number' && isFinite(stored)) return tolFromSlider(stored);
    const mult = { narrow: 0.5, normal: 1, broad: 2 }[stored];
    return mult != null ? tolFromSlider(b * mult) : b;
  }

  return { tolFromSlider, coerceTolToEv };
});
```

- [ ] **Step 5: Run to verify it passes**

Run: `node --test tests/js/*.test.js` — PASS (2 tests).

- [ ] **Step 6: Include the module (cache-busted) + absence guard (revision #7)**

Find the Chart.js CDN include: `grep -n "cdn.jsdelivr.*chart\|chart.umd\|Chart.js" templates/index.html | head`. Immediately AFTER it, add (cache-bust query so template edits force a reload):

```html
<script src="/static/js/ref_identify_core.js?v=20260619"></script>
```

Then add a loud absence guard near `_refEnsureData()` (the reference feature must NOT silently fall back to inline logic). At the top of `_refEnsureData()`:

```js
  if (typeof RefCore === 'undefined') {
    _refError = { error: 'RefCore module failed to load (static/js/ref_identify_core.js)' };
    _refRenderPanel();
    return;
  }
```

- [ ] **Step 7: Browser sanity (:5151)**

Start: `gunicorn -b 127.0.0.1:5151 --reload "app:create_app()" &`. In console: `RefCore.tolFromSlider(9)` → `5`.

- [ ] **Step 8: Commit**

```bash
git add static/js/ref_identify_core.js tests/js/ref_core.test.js templates/index.html
git commit -m "feat(reference): add shipped RefCore module + tolerance mapping (node:test)"
```

---

### Task 2: Blended-search core (`RefCore.blendedSearch`)

**Files:** Modify `static/js/ref_identify_core.js`, `tests/js/ref_core.test.js`.

- [ ] **Step 1: Write the failing test** — append to `tests/js/ref_core.test.js`:

```js
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
```

- [ ] **Step 2: Run to verify it fails** — `node --test tests/js/*.test.js` → `blendedSearch is not a function`.

- [ ] **Step 3: Implement** — in `ref_identify_core.js` before the `return`:

```js
  function blendedSearch(query, elements, chemGroups, opts) {
    const limit = (opts && opts.limit) || 8;
    const q = String(query == null ? '' : query).trim().toLowerCase();
    if (!q) return [];
    const isNum = /^\d/.test(q);
    const rows = [];
    for (const e of elements || []) {
      const name = String(e.name || '').toLowerCase();
      if (e.sym.toLowerCase().startsWith(q) || name.includes(q))
        rows.push({ kind: 'element', sym: e.sym, label: e.sym + ' — ' + (e.name || e.sym), ev: 'Z=' + e.z });
    }
    for (const g of chemGroups || []) {
      const parent = g.element || '';
      for (const s of g.states || []) {
        const hay = (s.state + ' ' + g.orbital_key + ' ' + (s.ref || '')).toLowerCase();
        if (hay.includes(q) || parent.toLowerCase() === q)
          rows.push({ kind: 'compound', sym: parent, key: g.orbital_key, id: s.id,
                      label: s.state + ' · ' + g.orbital_key, be: s.be_ev, ref: s.ref || '',
                      ev: s.be_ev.toFixed(1) + ' eV' });
      }
    }
    if (isNum) {
      for (const g of chemGroups || []) for (const s of g.states || []) {
        if (String(s.be_ev).startsWith(q))
          rows.push({ kind: 'energy', sym: g.element, key: g.orbital_key, id: s.id,
                      label: g.orbital_key + ' (' + s.state + ')', be: s.be_ev, ref: s.ref || '',
                      ev: s.be_ev.toFixed(1) + ' eV' });
      }
    }
    const order = { element: 0, compound: 1, energy: 2 };
    rows.sort((a, b) => order[a.kind] - order[b.kind]);
    return rows.slice(0, limit);
  }
```

Add `blendedSearch` to the returned object.

- [ ] **Step 4: Run to verify it passes** — `node --test tests/js/*.test.js` → PASS.

- [ ] **Step 5: Commit**

```bash
git add static/js/ref_identify_core.js tests/js/ref_core.test.js
git commit -m "feat(reference): blended element/compound/energy search core"
```

---

### Task 3: Key normalization, compound candidates, tier cap, merge/rank, physics + golden tests

This is the physics/provenance/ranking-critical task. Revisions #1, #2, #3, #4, #6 land here.

**Files:** Modify `static/js/ref_identify_core.js`, `tests/js/ref_core.test.js`.

- [ ] **Step 1: Write the failing tests** — append:

```js
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
```

- [ ] **Step 2: Run to verify it fails** — `node --test tests/js/*.test.js` → `parseChemKey is not a function`.

- [ ] **Step 3: Implement** — in `ref_identify_core.js` before the `return`:

```js
  // Normalize a mixed-granularity chemical-state key (revision #4). Exact
  // spin-orbit keys map to themselves; subshell-only p/d/f keys attach to BOTH
  // spin-orbit partners; s subshells have no split.
  const SO_SPLIT = { p: ['3/2', '1/2'], d: ['5/2', '3/2'], f: ['7/2', '5/2'] };
  function parseChemKey(key) {
    const str = String(key == null ? '' : key).trim();
    const m = str.match(/^([A-Z][a-z]?)\s+(\d)([spdf])(?:(\d)\/(\d))?$/);
    if (!m) {
      const parts = str.split(/\s+/);
      return { sym: parts[0] || str, orbital: parts.slice(1).join(' '), targets: [] };
    }
    const sym = m[1], n = m[2], l = m[3];
    if (m[4] && m[5]) { const orb = n + l + m[4] + '/' + m[5]; return { sym, orbital: orb, targets: [orb] }; }
    if (l === 's') { const orb = n + 's'; return { sym, orbital: orb, targets: [orb] }; }
    const orb = n + l;
    return { sym, orbital: orb, targets: SO_SPLIT[l].map(j => orb + j) };
  }

  // Physics projections (revision #6). Pure; mirror vgd_parser's convention.
  function augerApparentBE(ke, photonEv, workFn) { return photonEv - ke - workFn; }
  function photoelectronBE(nominalBE) { return nominalBE; }   // source-invariant

  // Marker-lifetime predicates (revision #5).
  function elementOverlayVisible(s) { return !!(s && s.panelOpen && s.activeChart && !s.isStackTab); }
  function compoundMarkerVisible() { return true; }            // global/persistent

  // ALL chem states within tol become candidates — no evidence filter exists at
  // runtime (revision #2). Proximity is honest; tier capping is applied later.
  function compoundCandidatesFrom(chemGroups, clickedBE, tolEv) {
    const out = [];
    const tol = tolFromSlider(tolEv);
    for (const g of chemGroups || []) {
      const pk = parseChemKey(g.orbital_key);
      const sym = pk.sym || g.element;
      for (const s of g.states || []) {
        const dist = Math.abs(s.be_ev - clickedBE);
        if (dist > tol) continue;
        const score = 20 + 30 * Math.max(0, 1 - dist / Math.max(tol, 0.01));
        out.push({
          id: s.id || (g.orbital_key + ':' + s.state),
          sym, orbital: pk.orbital, orbitalTargets: pk.targets,
          label: sym + ' ' + pk.orbital + ' — ' + s.state,
          isAuger: false, ke: null, be: s.be_ev, dist,
          inRegion: false, hasRegion: false, vis: 'n/a',
          score, dataTier: 'legacy', isCompound: true,
          stateName: s.state, ref: s.ref || '',
          // Proximity-only: 'strong' requires an expected-region hit, which
          // chemical-state records lack, so a compound tops out at 'moderate'.
          energyMatch: 'moderate',
          partnerTxt: 'n/a — chemical-state record',
          othersTxt: 'n/a — chemical-state record',
          conflictTxt: null,
          sourceId: s.source || 'legacy-embedded-dataset',
        });
      }
    }
    return out;
  }

  // Tier modulates ALL THREE confidence surfaces for legacy (revision #3):
  // overall noun -> "Legacy hint"; energy proximity stays honest but annotated.
  function capConfidenceByTier(score, energyMatch, dataTier) {
    if (dataTier === 'legacy') {
      return { label: 'Legacy hint', labelCls: 'legacy',
               energyText: energyMatch + ' (confidence capped by source tier)' };
    }
    const label = score >= 80 ? 'Strong candidate' : (score >= 50 ? 'Possible' : 'Weak candidate');
    const labelCls = score >= 80 ? 'strong' : (score >= 50 ? 'possible' : 'weak');
    return { label, labelCls, energyText: energyMatch };
  }

  // PRESERVE production's comparator exactly (revision #1): |Δ| primary; ties
  // within 0.5 eV break by tier (curated<machine<legacy), then score, then PE>Auger.
  function mergeAndRankCandidates(elementCands, compoundCands, limit) {
    const TIER_RANK = { curated: 0, machine: 1, legacy: 2 };
    const all = (elementCands || []).concat(compoundCands || []);
    all.sort((a, b) => {
      const dd = a.dist - b.dist;
      if (Math.abs(dd) > 0.5) return dd;
      const tr = (TIER_RANK[a.dataTier] != null ? TIER_RANK[a.dataTier] : 9) -
                 (TIER_RANK[b.dataTier] != null ? TIER_RANK[b.dataTier] : 9);
      if (tr) return tr;
      return (b.score - a.score) || ((a.isAuger ? 1 : 0) - (b.isAuger ? 1 : 0));
    });
    return all.slice(0, limit || 8);
  }
```

Extend the returned object to:
`return { tolFromSlider, coerceTolToEv, blendedSearch, parseChemKey, augerApparentBE, photoelectronBE, elementOverlayVisible, compoundMarkerVisible, compoundCandidatesFrom, capConfidenceByTier, mergeAndRankCandidates };`

- [ ] **Step 4: Run to verify it passes** — `node --test tests/js/*.test.js` → PASS (all).

- [ ] **Step 5: Commit**

```bash
git add static/js/ref_identify_core.js tests/js/ref_core.test.js
git commit -m "feat(reference): key normalization, compound candidates, tier cap, ranking + physics tests"
```

---

### Task 4: Drawer restructure — three zones + details relocation + widen

**Files:** Modify `templates/index.html` (CSS `:172-181`; `_refRenderPanel` `:10661-10727`).

- [ ] **Step 1: Widen + structure the drawer (CSS)** — replace `#ref-panel { width: 340px; ... }` (`:172-181`) with:

```css
  #ref-panel {
    width: 520px; flex-shrink: 0; background: var(--bg2);
    border-left: 1px solid var(--border); display: none;
    flex-direction: column; min-height: 0;
  }
  #ref-panel.open { display: flex; }
  .ref-zone-search { padding: 10px 12px; border-bottom: 1px solid var(--border); flex-shrink: 0; }
  .ref-zone-table  { padding: 10px 12px; border-bottom: 1px solid var(--border); flex-shrink: 0; }
  .ref-zone-details { padding: 10px 12px; overflow-y: auto; flex: 1; min-height: 0; }
  .ref-zone-head { font-family: var(--mono); font-size: 10px; letter-spacing: 0.08em;
    text-transform: uppercase; color: var(--text2); margin-bottom: 8px; }
```

- [ ] **Step 2: Restructure `_refRenderPanel` into zones** — keep all existing computation; assign the current inline fragments to locals (`srcRowHtml`, `contextHtml`, `elementSearchHtml`, `allLinesToggleHtml`) and assemble three zones, moving identify + element groups into details:

```js
  const searchZone = '<div class="ref-zone-search">' + blendedSearchHtml + srcRowHtml + contextHtml + elementSearchHtml + '</div>';
  const tableZone  = '<div class="ref-zone-table">' + _refRenderGrid(sel) + allLinesToggleHtml + '</div>';
  let detailsInner = _refRenderIdentify(sel, range);
  if (!sel.syms.length) {
    detailsInner += '<div class="ref-hint">Click an element to overlay its reference lines on the spectrum. ' +
      'Solid-outlined elements are curated (source-verified); dashed elements carry only legacy-unverified ' +
      'markers. Dimmed elements have no line data — no values are invented for them.</div>';
  }
  for (const s of sel.syms) detailsInner += _refRenderElementGroup(s, sel, range);
  const detailsZone = '<div class="ref-zone-details"><div class="ref-zone-head">Details</div>' + detailsInner + '</div>';
  body.innerHTML = searchZone + tableZone + detailsZone;
```

`blendedSearchHtml` is added in Task 6 (until then define `const blendedSearchHtml = '';`). Do not change fragment internals in this task.

- [ ] **Step 3: Restart gunicorn** (template change is not hot-reloaded): `kill %1 2>/dev/null; gunicorn -b 127.0.0.1:5151 --reload "app:create_app()" &`.

- [ ] **Step 4: Manual verification (:5151)** — load a spectrum, open the drawer:
- [ ] ~520px drawer, docked right; chart fully visible, never covered.
- [ ] Three zones: search · table · details.
- [ ] Clicking an element renders its line table **in the details zone**.
- [ ] Arming Identify + clicking a peak renders candidates **in the details zone** (not under the Identify control).
- [ ] Details zone scrolls; search + table stay fixed.

- [ ] **Step 5: Commit**

```bash
git add templates/index.html
git commit -m "refactor(reference): three-zone drawer; relocate details out from under Identify"
```

---

### Task 5: Continuous tolerance slider seeded from the auto-base

**Files:** Modify `templates/index.html` (`_refToleranceEv` `:10935`; `_refSetTolMode` `:11108`; `_refDefaultSel` `:10221`; `_refRenderIdentify` tol control `:11148-11155`).

- [ ] **Step 1: Auto-base helper + rewrite `_refToleranceEv`** — replace `_refToleranceEv()` (`:10935-10950`) with:

```js
function _refAutoTolBase() {
  let step = 0.1, highres = false;
  if (state.rawBE && state.rawBE.length > 1) {
    const be = getCorrectedBE();
    const span = Math.abs(be[be.length - 1] - be[0]);
    step = span / (be.length - 1);
    highres = span <= 100;
  }
  let tol = Math.max(3 * Math.abs(step), highres ? 0.4 : 1.0);
  tol += highres ? 0.3 : 0.5;
  let widened = false;
  if (!_refIsChargeCorrected()) { tol += 1.5; widened = true; }
  return { base: RefCore.tolFromSlider(tol), widened, highres };
}
function _refToleranceEv() {
  const sel = _refGetSel();
  const auto = _refAutoTolBase();
  if (sel.tolEv == null) {
    sel.tolEv = (sel.tolMode != null) ? RefCore.coerceTolToEv(sel.tolMode, auto.base) : auto.base;
  }
  return { tol: sel.tolEv, widened: auto.widened, highres: auto.highres };
}
```

- [ ] **Step 2: eV setter** — replace `_refSetTolMode(v)` (`:11108-11111`) with:

```js
function _refSetTol(v) { _refGetSel().tolEv = RefCore.tolFromSlider(v); _refRerunIdentify(); }
```

- [ ] **Step 3: Default sel** — in `_refDefaultSel()` (`:10221-10222`):

```js
  return { syms: [], showWeak: false, source: 'AlKa', _nextColorIdx: 0,
           tolEv: null, includeAuger: false };
```

- [ ] **Step 4: Slider control** — in `_refRenderIdentify` (`:11148-11155`), replace the `<select onchange="_refSetTolMode(...)">` … `<span class="ref-ident-tol">` block with:

```js
  html += '<div class="ref-ident-row">' +
    '<button class="btn btn-sm' + (armed ? ' place-active' : '') + '" id="ref-identify-btn" ' +
    'onclick="togglePlaceMode(\'identify\')" title="Arm Identify mode: chart clicks list candidate lines instead of placing peaks">&#8982; Identify mode</button>' +
    '<label class="ref-tol-wrap"><span class="ref-tol-cap">&plusmn; tol</span>' +
    '<input type="range" id="ref-tol-range" min="0.25" max="5" step="0.25" value="' + tol.toFixed(2) + '" ' +
    'oninput="_refSetTol(this.value)" aria-label="Identify tolerance in eV"></label>' +
    '<span class="ref-ident-tol" id="ref-tol-val">&plusmn; ' + tol.toFixed(2) + ' eV</span></div>';
```

Add CSS near `.ref-ident-*` (`:295-300`):

```css
  .ref-tol-wrap { display: inline-flex; align-items: center; gap: 6px; }
  .ref-tol-cap { font-size: 10px; color: var(--text2); }
  #ref-tol-range { width: 96px; accent-color: var(--accent); cursor: pointer; }
  #ref-tol-range:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
```

- [ ] **Step 5: Restart gunicorn + manual verification** — with a spectrum + Identify armed:
- [ ] Slider (0.25–5.0, step 0.25), not a dropdown.
- [ ] First-open value = resolution-aware default (wider for 0–1200 survey; ~0.4–0.7 for <100 eV window).
- [ ] Dragging updates the readout live and re-runs identify.

- [ ] **Step 6: Commit**

```bash
git add templates/index.html
git commit -m "feat(reference): continuous tolerance slider seeded from resolution-aware base"
```

---

### Task 6: Unified top search — body-portal fixed popover (revision #8)

The app layout uses `overflow:hidden`, so a `z-index`/absolute dropdown is clipped. Render results in a **body portal** as a `position:fixed` popover positioned from the input's `getBoundingClientRect()`, repositioned on scroll/resize, dismissed on outside-click/Esc.

**Files:** Modify `templates/index.html` (search-zone HTML; portal popover element + handlers; CSS).

- [ ] **Step 1: Add the search input (no inline results container) + a one-time body portal**

In `_refRenderPanel`, build `elementsForSearch` and `blendedSearchHtml` (input only; results live in the portal):

```js
  const elementsForSearch = REF_PT_LAYOUT.filter(e => _refActivation(e.sym)).map(e => {
    const ent = _refElements()[e.sym];
    const name = (typeof ELEMENT_NAMES !== 'undefined' && ELEMENT_NAMES[e.sym]) ||
                 (ent && (ent.pe || ent.auger) && (ent.pe || ent.auger).name) || e.sym;
    return { sym: e.sym, name, z: e.z, tier: _refActivation(e.sym) };
  });
  _refSearchElements = elementsForSearch;
  const blendedSearchHtml =
    '<div class="ref-blendsearch">' +
    '<input id="ref-blend-input" autocomplete="off" oninput="_refBlendedSearch(this.value)" ' +
    'onkeydown="if(event.key===\'Escape\'){_refCloseSearch()}" ' +
    'placeholder="Search element, orbital, compound, or BE (e.g. U, Cl 2p, UO2, 707)" ' +
    'aria-label="Search reference data" aria-expanded="false" aria-controls="ref-blend-portal"></div>';
```

Declare `let _refSearchElements = [];` once beside the other `_ref*` module state. Ensure a single portal node exists (created lazily):

```js
function _refSearchPortal() {
  let p = document.getElementById('ref-blend-portal');
  if (!p) {
    p = document.createElement('div');
    p.id = 'ref-blend-portal';
    p.className = 'ref-blend-portal';
    p.setAttribute('role', 'listbox');
    document.body.appendChild(p);
  }
  return p;
}
```

- [ ] **Step 2: Search handlers with rect-based fixed positioning**

```js
function _refBlendedSearch(q) {
  const input = document.getElementById('ref-blend-input');
  const portal = _refSearchPortal();
  const groups = (LEGACY_REFERENCE_OK && LEGACY_REFERENCE.chemical_states) || [];
  const rows = RefCore.blendedSearch(q, _refSearchElements, groups, { limit: 8 });
  if (!String(q).trim()) { _refCloseSearch(); return; }
  portal.innerHTML = rows.length
    ? rows.map((r, i) =>
        '<div class="ref-blend-row" role="option" tabindex="0" data-kind="' + _escAttr(r.kind) + '" ' +
        'data-sym="' + _escAttr(r.sym) + '" data-id="' + _escAttr(r.id || '') + '" data-be="' + (r.be != null ? r.be : '') + '" ' +
        'data-state="' + _escAttr(r.label) + '" data-ref="' + _escAttr(r.ref || '') + '" ' +
        'onclick="_refBlendedPick(this)" onkeydown="if(event.key===\'Enter\'){event.preventDefault();_refBlendedPick(this)}">' +
        '<span class="ref-blend-kind ' + r.kind + '">' + r.kind + '</span>' +
        '<span class="ref-blend-main">' + _escHtml(r.label) + '</span>' +
        '<span class="ref-blend-ev">' + _escHtml(r.ev) + '</span></div>').join('')
    : '<div class="ref-blend-empty">No matches — try an element symbol, a compound, or a binding energy.</div>';
  _refPositionSearchPortal();
  portal.classList.add('show');
  if (input) input.setAttribute('aria-expanded', 'true');
}
function _refPositionSearchPortal() {
  const input = document.getElementById('ref-blend-input');
  const portal = document.getElementById('ref-blend-portal');
  if (!input || !portal) return;
  const r = input.getBoundingClientRect();
  portal.style.position = 'fixed';
  portal.style.top = (r.bottom + 4) + 'px';
  portal.style.left = r.left + 'px';
  portal.style.width = r.width + 'px';
}
function _refCloseSearch() {
  const input = document.getElementById('ref-blend-input');
  const portal = document.getElementById('ref-blend-portal');
  if (portal) { portal.classList.remove('show'); portal.innerHTML = ''; }
  if (input) { input.setAttribute('aria-expanded', 'false'); }
}
function _refBlendedPick(el) {
  const kind = el.getAttribute('data-kind');
  const sym = el.getAttribute('data-sym');
  const be = parseFloat(el.getAttribute('data-be'));
  const input = document.getElementById('ref-blend-input');
  if (input) input.value = '';
  _refCloseSearch();
  if (kind === 'element') { if (sym) _refToggleElement(sym); return; }
  // compound / energy -> add a global, persistent compound marker (Task 8 API)
  if (isFinite(be) && sym) {
    _refAddCompoundMarker(sym, el.getAttribute('data-state') || (sym + ' ' + be.toFixed(1)), be, el.getAttribute('data-ref') || '');
  }
}
```

Register once (e.g. in the existing app init), keeping the popover anchored while scrolling and dismissing on outside click:

```js
window.addEventListener('scroll', () => { if (document.getElementById('ref-blend-portal')?.classList.contains('show')) _refPositionSearchPortal(); }, true);
window.addEventListener('resize', () => { if (document.getElementById('ref-blend-portal')?.classList.contains('show')) _refPositionSearchPortal(); });
document.addEventListener('click', (e) => {
  const p = document.getElementById('ref-blend-portal');
  if (!p || !p.classList.contains('show')) return;
  if (e.target.closest && (e.target.closest('#ref-blend-portal') || e.target.closest('#ref-blend-input'))) return;
  _refCloseSearch();
});
```

- [ ] **Step 3: CSS — fixed portal escapes any clip**

```css
  .ref-blendsearch { margin-bottom: 8px; }
  .ref-blendsearch input {
    width: 100%; padding: 7px 10px; border-radius: 6px; background: var(--bg);
    border: 1px solid var(--border); color: var(--text); font-family: var(--sans); font-size: 12px;
  }
  .ref-blendsearch input:focus { outline: none; border-color: var(--accent); }
  .ref-blend-portal {
    display: none; position: fixed; z-index: var(--z-popover, 2200);
    background: var(--bg); border: 1px solid var(--border2); border-radius: 8px;
    overflow: hidden; box-shadow: 0 10px 30px -12px rgba(0,0,0,0.7);
  }
  .ref-blend-portal.show { display: block; }
  .ref-blend-row { display: flex; align-items: center; gap: 8px; padding: 7px 10px; cursor: pointer; border-bottom: 1px solid var(--border); }
  .ref-blend-row:last-child { border-bottom: 0; }
  .ref-blend-row:hover, .ref-blend-row:focus-visible { background: var(--accent-dim); outline: none; }
  .ref-blend-kind { font-family: var(--mono); font-size: 9px; text-transform: uppercase; letter-spacing: 0.06em; padding: 1px 5px; border-radius: 3px; border: 1px solid var(--border2); color: var(--text2); }
  .ref-blend-kind.element { color: var(--accent2); border-color: var(--accent); }
  .ref-blend-kind.compound { color: var(--green); border-color: var(--green); }
  .ref-blend-kind.energy { color: var(--amber); border-color: var(--amber); }
  .ref-blend-main { flex: 1; min-width: 0; font-size: 12px; color: var(--text); }
  .ref-blend-ev { font-family: var(--mono); font-size: 11px; color: var(--text2); }
  .ref-blend-empty { padding: 8px 10px; font-size: 11px; color: var(--text2); }
```

If `--z-popover` is not in `:root`, add `--z-popover: 2200;` (above the drawer; semantic, not arbitrary).

- [ ] **Step 4: Restart gunicorn + manual verification (incl. the scrolled case, revision #8)**
- [ ] `U` → element row; `UO2` → compound row; `284` → energy rows; tagged correctly.
- [ ] **Scroll the drawer/page while the dropdown is open** — the popover stays anchored to the input and is NOT clipped by any `overflow:hidden` ancestor.
- [ ] Enter + click both select; rows are keyboard-focusable; Esc and outside-click dismiss.
- [ ] Selecting an element overlays its lines; selecting a compound/energy drops a persistent amber marker (Task 8).

- [ ] **Step 5: Commit**

```bash
git add templates/index.html
git commit -m "feat(reference): unified top search as body-portal fixed popover (escapes overflow clip)"
```

---

### Task 7: Identify returns compounds + tier cap on all confidence surfaces

**Files:** Modify `templates/index.html` (`_refIdentifyAt` `:11068-11088`; `_refRenderIdentify` cards `:11175-11198`; CSS).

- [ ] **Step 1: Append compounds; rank via core; cap via core (all surfaces)** — in `_refIdentifyAt`, replace the existing `TIER_RANK`/`cands.sort`/`slice(0,8)`/label block (`:11068-11088`) with:

```js
  const chemGroups = (LEGACY_REFERENCE_OK && LEGACY_REFERENCE.chemical_states) || [];
  const compoundCands = RefCore.compoundCandidatesFrom(chemGroups, beClicked, tol);
  if (ccUnverified) for (const c of compoundCands) c.score -= 10;

  const top = RefCore.mergeAndRankCandidates(cands, compoundCands, 8);

  for (const a of top) {                                  // overlap conflicts (different element)
    const clash = top.find(b => b !== a && b.sym !== a.sym && Math.abs(b.be - a.be) <= tol);
    if (clash) a.conflictTxt = 'overlapping ' + clash.label + ' at ' + clash.be.toFixed(1) + ' eV';
  }
  for (const c of top) {                                  // tier cap on label + energy text (revision #3)
    const cap = RefCore.capConfidenceByTier(c.score, c.energyMatch, c.dataTier);
    c.tier = cap.label; c.tierCls = cap.labelCls; c.energyText = cap.energyText;
  }
```

- [ ] **Step 2: Render compound + capped energy** — in `_refRenderIdentify` (`:11175-11198`), replace the candidate-card template so the noun comes from `c.tier`, the energy line uses `c.energyText`, and compounds get a kind tag + reference line:

```js
    const kindTag = c.isCompound
      ? '<span class="ref-blend-kind compound">compound</span>'
      : '<span class="ref-blend-kind element">element</span>';
    html += '<div class="ref-cand' + (c.isCompound ? ' compound' : '') + '">' +
      '<div class="ref-cand-head"><span class="ref-tier ' + c.tierCls + '">' + _escHtml(c.tier) + '</span>' +
      kindTag + '<span class="ref-cand-name">' + _escHtml(c.label) + '</span>' + tierBadge +
      (c.isAuger ? '<span class="ref-chip auger">Auger</span>' : '') +
      '<span class="ref-cand-ev">' + c.be.toFixed(2) + ' eV &middot; &Delta;' + c.dist.toFixed(2) + '</span></div>' +
      '<div class="ref-cand-line">Energy match: <b>' + _escHtml(c.energyText || c.energyMatch) + '</b>' +
      (c.hasRegion ? (c.inRegion ? ' (inside expected region)' : ' (outside expected region)')
                   : (c.isCompound ? ' (chemical-state record — proximity only)' : ' (proximity match — no expected-region band)')) + '</div>' +
      '<div class="ref-cand-line">Expected visibility: <b>' + _escHtml(c.vis) + '</b></div>' +
      '<div class="ref-cand-line">Doublet partner: ' + _escHtml(c.partnerTxt) + '</div>' +
      '<div class="ref-cand-line">Other ' + _escHtml(c.sym) + ' lines: ' + _escHtml(c.othersTxt) + '</div>' +
      (c.isCompound && c.ref ? '<div class="ref-cand-line">Reference: <b>' + _escHtml(c.ref) + '</b></div>' : '') +
      (c.conflictTxt ? '<div class="ref-cand-conflict">Possible conflict: ' + _escHtml(c.conflictTxt) + '</div>' : '') +
      (c.isAuger ? '<div class="ref-cand-line">KE ' + c.ke.toFixed(2) + ' eV &rarr; apparent BE on ' + srcLabel + '</div>' : '') +
      '<div class="ref-cand-actions"><button type="button" class="ref-cand-add" onclick="_refAddOverlayFromCand(\'' + _escAttr(c.sym) + '\')">+ overlay ' + _escHtml(c.sym) + '</button>' +
      (cite ? '<span class="ref-cite" title="' + _escAttr(cite.citation) + '">source: ' + _escHtml(c.sourceId) + '</span>' : '') +
      '</div></div>';
```

Keep the existing `tierBadge`/`cite` setup lines. Add CSS:

```css
  .ref-cand.compound { border-color: var(--green); }
  .ref-tier.legacy { color: var(--amber); border-color: var(--amber); background: var(--amber-dim); }
```

- [ ] **Step 3: Restart gunicorn + manual verification** — U 4f spectrum, charge-correct, arm Identify, click ~380 eV:
- [ ] Results include elemental U 4f lines AND compound rows (e.g. `U 4f7/2 — UO2`, tagged compound).
- [ ] Every legacy item (compounds AND any legacy element line) shows the noun **"Legacy hint"** (never "Strong candidate"); its energy line reads e.g. "strong (confidence capped by source tier)".
- [ ] Curated/machine items keep "Strong/Possible/Weak candidate" with un-annotated energy text.
- [ ] Ranking matches today for the element rows; a curated element beats a legacy compound within ~0.5 eV of the click.
- [ ] Non-definitive language only.

- [ ] **Step 4: Commit**

```bash
git add templates/index.html
git commit -m "feat(reference): Identify returns compounds; tier caps confidence on all surfaces"
```

---

### Task 8: Marker unification — same render/style, preserved distinct lifetimes (revision #5)

Rename the chem-state marker state/draw into the reference namespace and feed it from the unified search/identify, **keeping its global/persistent lifetime**. Element overlays stay panel-gated. Both styles kept (element-colored dashed vs amber dashed). Chart.js v4: mutate leaf fields only.

**Files:** Modify `templates/index.html` (`_nistMarkers` `:9989`; `_drawNistMarkers` `:10108`; `overlayPlugin.afterDraw` `:7861-7862`; new add/remove + chips).

- [ ] **Step 1: Rename the global state + draw, preserving lifetime**

- Rename `const _nistMarkers = [];` (`:9989`) → `const _refCompoundMarkers = [];` (still module-global → persistent).
- Rename `_drawNistMarkers` (`:10108`) → `_refDrawCompoundMarkers`, keep its amber-dashed style verbatim, and have it read `_refCompoundMarkers`. Keep it drawn from the GLOBAL `overlayPlugin.afterDraw` (`:7862`): change that call to `_refDrawCompoundMarkers(chart);`. Do NOT gate it on `_refPanelOpen` (persistence requirement).
- Element overlays remain in `xpsRefLinesPlugin` + `_refChartItems` — unchanged (still gated). Optionally assert the gate via the pure predicate at the top of `_refChartItems`:

```js
  if (!RefCore.elementOverlayVisible({ panelOpen: _refPanelOpen, activeChart: chart === state.chart, isStackTab: !!(tab && isStackTab(tab)) })) return null;
```

(retain the existing explicit checks too; the predicate documents the contract.)

- [ ] **Step 2: Add/remove API + active-marker chips**

```js
function _refAddCompoundMarker(sym, stateLabel, be, ref) {
  const id = (_refCompoundMarkerNextId = (typeof _refCompoundMarkerNextId === 'undefined' ? 0 : _refCompoundMarkerNextId) + 1);
  _refCompoundMarkers.push({ id, sym, state: stateLabel, be, ref: ref || '' });
  _refRenderPanel();
  if (state.chart) state.chart.update('none');     // leaf update; preserves zoom
  notify('Marked ' + sym + ' ' + be.toFixed(1) + ' eV', 'green');
}
function _refRemoveCompoundMarker(id) {
  const i = _refCompoundMarkers.findIndex(m => m.id === id);
  if (i >= 0) _refCompoundMarkers.splice(i, 1);
  _refRenderPanel();
  if (state.chart) state.chart.update('none');
}
function _refRenderCompoundChips() {
  if (!_refCompoundMarkers.length) return '';
  return '<div class="ref-cmarker-chips">' + _refCompoundMarkers.map(m =>
    '<span class="ref-cmarker-chip">' + _escHtml(m.sym + ' ' + m.be.toFixed(1) + ' eV') +
    '<button type="button" onclick="_refRemoveCompoundMarker(' + m.id + ')" title="Remove marker" aria-label="Remove marker">&#10005;</button></span>').join('') + '</div>';
}
```

Declare `let _refCompoundMarkerNextId = 0;` beside the array. Insert `_refRenderCompoundChips()` into the search zone (Task 4 assembly), after `blendedSearchHtml`. Add CSS:

```css
  .ref-cmarker-chips { display: flex; flex-wrap: wrap; gap: 4px; margin: 6px 0; }
  .ref-cmarker-chip { display: inline-flex; align-items: center; gap: 4px; font-family: var(--mono); font-size: 10px;
    color: var(--amber); border: 1px solid var(--amber); background: var(--amber-dim); border-radius: 3px; padding: 1px 6px; }
  .ref-cmarker-chip button { border: 0; background: none; color: var(--amber); cursor: pointer; font-size: 11px; line-height: 1; }
```

- [ ] **Step 3: Restart gunicorn + manual verification (both lifetimes + both styles)**
- [ ] Search/select a compound → **amber dashed** marker at its BE; select an element → **element-colored dashed** lines — both visible together.
- [ ] **Persistence:** add a compound marker, then close the drawer — the amber marker **stays** on the chart.
- [ ] **Panel-gated overlays:** element overlays disappear when the drawer is closed (and never draw on a stack tab).
- [ ] Zoom/pan preserved across updates (`update('none')`); no console errors; Chart config not reassigned.

- [ ] **Step 4: Commit**

```bash
git add templates/index.html
git commit -m "refactor(reference): rename NIST markers into ref namespace; keep global lifetime + amber style"
```

---

### Task 9: Retire the NIST modal

**Files:** Modify `templates/index.html` (modal HTML `:11865-11877`; `_nist*` functions `:9992-10070`; Lookup button `:1666`; disabled list `:2429`).

- [ ] **Step 1: Remove modal markup** — delete the `#nist-modal-overlay` block (`:11865-11877`).
- [ ] **Step 2: Remove the `_nist*` UI functions** — delete `showNistModal`, `_nistFilter`, `_nistRenderResults`, `_nistAddMarker`, `_nistRemoveMarker`, `_nistRenderMarkerChips`, `_nistClearAll`. (Draw + state were renamed in Task 8, not deleted.) Run `grep -n "_nist" templates/index.html` → expect zero hits.
- [ ] **Step 3: Repoint the Lookup button** (`:1666`) to open the drawer:

```html
<button class="btn" id="btn-nist-lookup" onclick="toggleRefPanel()" title="Open the Reference / Identify workspace (elements + chemical-state lookup)">Lookup</button>
```

- [ ] **Step 4: Verify the disabled list** (`:2429`) — `['btn-ref-panel','btn-nist-lookup','survey-tab-btn']` still matches DOM ids (keep `btn-nist-lookup` since it now opens the drawer and should disable when reference data fails).
- [ ] **Step 5: Restart gunicorn + manual verification**
- [ ] `grep -n "_nist\|nist-modal-overlay" templates/index.html` → nothing.
- [ ] "Lookup" opens the drawer; compound search works there.
- [ ] Simulate reference-data failure (rename a `data/xps` file, restart): entry buttons disable + banner; restore the file after.

- [ ] **Step 6: Commit**

```bash
git add templates/index.html
git commit -m "refactor(reference): retire NIST modal; Lookup opens unified drawer"
```

---

### Task 10: Design-system polish (impeccable) — drawer surface only

**Files:** Modify `templates/index.html` (drawer CSS + instruction string).

- [ ] **Step 1: Token + gradient audit** — `grep -n "#5bb0ff\|#4fd08a\|#e0a64a\|--machine\|--legacy\|--ink3\|background-clip\|-webkit-text-fill" templates/index.html` → no hits in the Reference/Identify additions. All colors are committed tokens.
- [ ] **Step 2: Contrast** — `grep -n "ref-hint\|ref-context\|ref-cite\|ref-blend-empty\|ref-cand-line\|ref-note\|ref-zone-head" templates/index.html | grep "text3"` → any prose using `var(--text3)` (#4a5a78, ~2.1:1 on `--bg2`) switches to `var(--text2)` (#8a9ab8, ~6:1). Mono numeric badges may stay dense; sentences must clear 4.5:1.
- [ ] **Step 3: Sentence-case** the periodic-table instruction string (no `text-transform: uppercase` on a full sentence; short `.ref-zone-head` labels may stay uppercased mono).
- [ ] **Step 4: Detector over a rendered snapshot** — with gunicorn running, copy `document.getElementById('ref-panel').outerHTML` + `document.getElementById('ref-blend-portal').outerHTML` into a scratch HTML wrapped with the `:root` tokens, then `npx impeccable detect <file>`. Expect no `gradient-text`, no prose `low-contrast`, no `all-caps-body` on the instruction. (Pre-existing whole-app findings are out of scope.)
- [ ] **Step 5: Commit**

```bash
git add templates/index.html
git commit -m "style(reference): align drawer to DESIGN.md tokens, fix prose contrast, sentence-case guidance"
```

---

### Task 11: Final verification + finish

**Files:** none.

- [ ] **Step 1: JS core tests** — `node --test tests/js/*.test.js` → PASS (incl. golden ordering + physics).
- [ ] **Step 2: Backend gate** — `pytest tests/ -v` → PASS.
- [ ] **Step 3: No-inline-fallback check (revision #7)** — `grep -n "function tolFromSlider\|function compoundCandidatesFrom\|function mergeAndRankCandidates\|function parseChemKey\|function capConfidenceByTier" templates/index.html` → **zero** hits (these live only in `static/js/ref_identify_core.js`).
- [ ] **Step 4: No `be + ccShift` regression (revision #6)** — `grep -n "ccShift" templates/index.html | grep -i "ref\|marker\|cand\|overlay"` → no reference marker/candidate path adds `ccShift` to a reference BE (overlays draw at corrected nominal BE; clicks already arrive corrected).
- [ ] **Step 5: Physics + provenance + lifetime checklist (:5151)** — U 4f spectrum, charge-corrected, drawer open:
- [ ] Switch Al Kα → Mg Kα: **Auger markers move**, **photoelectron markers and compound markers do NOT move** (PE/compound at source-invariant BE; Auger at hν − KE − φ).
- [ ] Reference markers draw at corrected BE; "not charge corrected" hint only when no CC method.
- [ ] Element groups + compound candidates show source citations.
- [ ] Legacy items read "Legacy hint" with capped energy text; curated/machine read "… candidate".
- [ ] Identify works by clicking the spectrum (drawer never occludes the chart).
- [ ] Compound marker persists after closing the drawer; element overlays vanish when closed and never draw on a stack tab.
- [ ] Search popover stays anchored while scrolling and is never clipped.
- [ ] **Step 6: Finish** — announce "I'm using the finishing-a-development-branch skill to complete this work." Use **superpowers:finishing-a-development-branch**. Do not merge to `main` until the user has browser-verified per CLAUDE.md.

---

## Self-Review (completed)

- **Spec coverage:** Container/drawer (Task 4); modal→drawer unification + retirement (Tasks 6, 9); readable table preserving existing cell a11y (Task 4 does not touch `_refRenderGrid` cells at `:10552-10554`); details relocation (Task 4); compounds in Identify, all 52 at authoring (51 after a 2026-07-16 provenance-audit removal), tier-capped, no evidence filter (Tasks 3, 7); continuous tolerance seeded from auto-base + non-persisted coercion (Tasks 1, 5); ranking preserved Δ-primary with golden tests (Tasks 3, 7); tier cap on all three surfaces + "Legacy hint" (Tasks 3, 7); `parseChemKey` for mixed keys (Task 3); marker render/style unified with both lifetimes preserved + predicates (Tasks 3, 8); physics assertions (Tasks 3, 11); RefCore single shipped module, cache-busted, no inline fallback (Tasks 1, 11); body-portal popover (Task 6); DESIGN.md tokens / contrast / sentence-case (Task 10).
- **Placeholder scan:** No TBD/TODO; every code step carries complete code; manual steps list concrete, checkable observations.
- **Type consistency:** `RefCore` API fixed in Tasks 1–3 (`tolFromSlider`, `coerceTolToEv`, `blendedSearch`, `parseChemKey`, `augerApparentBE`, `photoelectronBE`, `elementOverlayVisible`, `compoundMarkerVisible`, `compoundCandidatesFrom`, `capConfidenceByTier`, `mergeAndRankCandidates`) and used consistently. `capConfidenceByTier(score, energyMatch, dataTier) -> {label, labelCls, energyText}` is consumed in Task 7 Step 1 (`c.tier`/`c.tierCls`/`c.energyText`) and rendered in Step 2. Candidate fields from `compoundCandidatesFrom` match the renderer. `_refSetTolMode`→`_refSetTol` and `sel.tolMode`→`sel.tolEv` are renamed at definition and all call sites. Marker rename `_nistMarkers`→`_refCompoundMarkers`, `_drawNistMarkers`→`_refDrawCompoundMarkers` applied at declaration, draw, plugin call site, and new API.

---

## Open risks flagged for the implementer

1. **`MONO_FONT` / draw constants in Task 8** — the renamed `_refDrawCompoundMarkers` keeps the original `_drawNistMarkers` body; confirm its font/colour constants are unchanged after the rename (`grep -n "MONO_FONT" templates/index.html`).
2. **Plugin draw order (Task 8)** — `overlayPlugin` and `xpsRefLinesPlugin` are both in the `plugins:[...]` array (`:7889`); keep their relative order so compound markers and element overlays layer as today.
3. **`REF_PT_LAYOUT` / `ELEMENT_NAMES` scope (Task 6)** — both are used elsewhere in the panel (`:10531`, `:10541`); confirm in scope at the search-zone build site.
4. **Portal cleanup** — `#ref-blend-portal` is a body child; it persists across panel open/close by design. Ensure `_refCloseSearch()` runs when the drawer closes (call it in `toggleRefPanel` close path) so a stale popover never lingers.
