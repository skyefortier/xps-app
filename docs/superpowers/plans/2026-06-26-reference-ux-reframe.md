# Reference/Identify UX Reframe — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. **This is a RESTRUCTURE + SERIALIZE of a working feature (shipped at `84e1bb8`), not a rebuild — maximize reuse of RefCore, the identify/compound logic, the tier-cap, and the DETAILS-card renderer.**

**Goal:** Replace the docked Reference/Identify drawer with a draggable, non-modal, collapsible floating palette; make element overlays persist on the chart (managed by an always-visible on-chart legend) independent of the palette; make Identify a per-peak click-anchored popover; and serialize picked overlays + compound markers into the project file with versioned, deterministic round-trip.

**Architecture:** Two clearly separated bodies of work. **Phase A (client-only restructure)** changes only runtime UI/draw behavior — no file format touched: tier-color single-source-of-truth, persistent overlays, on-chart legend + per-chip dropdown (reusing the existing DETAILS renderer), floating palette container, identify popover. **Phase B (serialization)** adds a *versioned* `refOverlays` field to the saved project via pure, node-testable serialize/deserialize helpers in `RefCore`, wired into `buildTabData`/`_loadProjectJSON`. Phase B gets Codex review **before** implementation because it is the only part that touches saved-file format and back-compat.

**Tech Stack:** Vanilla JS in `templates/index.html` (~12.1k LOC, no build step); `static/js/ref_identify_core.js` (the extracted, node-tested `RefCore` module — single source of truth for pure logic); Chart.js 4.4 (custom plugins draw overlays via canvas); `node --test` for `RefCore` unit tests; Playwright (prod venv) for in-app verification. Design tokens in committed `DESIGN.md` (instrument-grade dark theme).

---

## Recon Findings (ground truth — main @ `bfedc95`)

Line numbers are at `bfedc95`; re-grep before editing (the file evolves).

### Modules & data flow
- **`RefCore`** is an external module: `static/js/ref_identify_core.js`, loaded by `templates/index.html` with a loud absence guard (`templates/index.html:10414`). It is the single source for pure logic and is unit-tested in `tests/js/ref_core.test.js` (18 tests: `tolFromSlider`, `coerceTolToEv`, `blendedSearch`, `parseChemKey`, `compoundCandidatesFrom`, `capConfidenceByTier`, `mergeAndRankCandidates`, `elementOverlayVisible`). **New pure logic goes here so it is node-testable.**
- Reference payload from `GET /api/xps-reference` → `_refPayload`; element map via `_refElements()` (three-tier precedence curated > machine > legacy, per subshell), `templates/index.html:10231`.

### The three marker/draw paths (decision 3 touches all three)
1. **Element overlays** — `xpsRefLinesPlugin` (`templates/index.html:10897`), fed by `_refChartItems(chart)` (`:10859`). **PANEL-GATED**: returns null unless `_refPanelOpen` (`:10870`) and `RefCore.elementOverlayVisible({panelOpen,…})` (`:10866`). PE nominal lines are **SOLID** today (`c.setLineDash(m.isAuger ? [5,4] : [])`, `:10974`); Auger dashed; bands drawn in `beforeDatasetsDraw` (`:10900`); labels with greedy stagger in `afterDraw`.
2. **Compound markers** — global array `_refCompoundMarkers` (`:10019`), drawn by `_refDrawCompoundMarkers(chart)` (`:10067`) from the **global** `overlayPlugin` (called at `:7890`), **amber dashed**, **persistent** (survives drawer close). *This is the model to copy for persistent element overlays.*
3. **Identify marker** — **CORRECTION to the recon brief:** identify *does* draw an on-chart marker today. `_refIdentState(chart)` (`:11058`, panel-gated at `:11059`) drives, in `xpsRefLinesPlugin`: a tolerance tint band (`:10919`) + a **solid accent vertical line** `#4a9eff` + `"identify N.N"` label (`:10930-10954`). Decision 3 is therefore an *enhancement* (add caret, keep transient, drop panel-gating), not net-new.

### Identify (decision 5 — already per-peak)
- Armed from chart click when `mode === 'identify'` → `_refIdentifyAt(beClicked)` (`:11124`), called at `:4941`. Stores `tab._refIdentify = {be, tol, widened, ccUnverified, cands}` (`:11241`). `_refClearIdentify` (`:11246`). Candidate pool = full activatable set + compounds; tier-capped via `RefCore.capConfidenceByTier` (`:11237`). Results render into the **panel** via `_refRenderIdentifyResults(sel, range)` (`:11327`). **Change = drop the `_refPanelOpen` gate (`:11059`) + render a click-anchored popover instead of (or in addition to) the panel section.**

### DETAILS card (reuse target for decision 4)
- `_refRenderElementGroup(s, sel, range)` (`:10661`) renders a full card: tier badge (`headRight`), transition rows, tier note (curated/machine/legacy), element `short_caveat` + `more…` disclosure (real `<button aria-expanded>`), and the citation footer. **Reuse this verbatim inside the per-chip dropdown.**

### Container (decision 1)
- `#ref-panel` is a docked flex child: `width:520px; flex-shrink:0; border-left` (CSS `templates/index.html:176`), `.open{display:flex}` (`:185`), three zones (`.ref-zone-search/-table/-details`). HTML at `:2045`; toggled by `toggleRefPanel()` (`:10432`), button `#btn-ref-panel` (`:1897`). State `_refPanelOpen`. Because it is a flex sibling of the chart, **opening it compresses the chart today** — the floating palette fixes exactly this.

### Portal/popover + z-index precedent (decisions 4/5)
- A fixed/portal popover that escapes `overflow:hidden` **already exists**: `position:fixed; z-index:var(--z-popover,2200)` (`:202`), used by the blend-search portal. Reuse this pattern for legend dropdowns + identify popover.
- z-index is **partly** semantic (`--z-popover`) but mostly raw literals (999, 9999, 300, 200, 260, 250, 100, 50, 30; `:723,:1480,…`). Decision: **formalize a semantic scale** and route the new floating surfaces through it.

### Selection state & save/load (decision 7)
- `_refGetSel()` → `tab._refSel` (per-tab, lazy) or `_refGlobalSel` pre-tab (`:10196`). Shape `_refDefaultSel()` (`:10184`): `{ syms: [], showWeak:false, source:'AlKa', _nextColorIdx:0, tolEv:null, includeAuger:false }`. `syms` entries carry `{sym, colorIdx}`; overlay color = `ELEMENT_MARKER_COLORS[colorIdx % …]` (`:2507`, used `:10880`).
- `buildTabData(t)` (`:8376`) serializes a fixed field set. **CONFIRMED:** `_refSel`, `_refIdentify`, and the global `_refCompoundMarkers` are **NOT** serialized today. Project schema `version: 3` (`:8418`). Loaded by `_loadProjectJSON` (`:8604`).
- **Serialization wrinkle:** `_refCompoundMarkers` is a *global* array, not per-tab — its save home is **project-meta (global)**, confirmed (D2); element overlays stay per-tab.

### Canonical tier wording (use THIS, not the mockup draft)
Live wording shipped in `07bc470`/`bfedc95` (data/UI), to reuse verbatim in toasts/dropdowns:
- **machine:** "From NIST, automatically cross-checked but not yet reviewed by a person."
- **legacy/approximate:** "Approximate value — verify against literature."
- **curated/reviewed:** badge "reviewed"; note "Reference energies reviewed by a person. Please verify all energies against authoritative reference sources."

---

## File Structure (reused vs new)

| File | Role | Reuse / New |
|---|---|---|
| `static/js/ref_identify_core.js` | `RefCore` pure logic | **Reuse + extend**: add `TIER_COLORS` SSOT, `tierColor()`, `serializeRefOverlays()`, `deserializeRefOverlays()` (pure, versioned). |
| `templates/index.html` | All UI/DOM/Chart.js | **Modify**: palette container (drag/collapse/responsive), reverse overlay panel-gating, dashed element lines, on-chart legend + chip dropdown, identify popover, wire serialize/deserialize into `buildTabData`/`_loadProjectJSON`, semantic z-index scale. |
| `tests/js/ref_core.test.js` | node unit tests | **Extend**: tier-color SSOT, serialize/deserialize round-trip + version back-compat + deterministic color; do not weaken existing 18. |
| `docs/mockups/reference-ux-reframe-floating.html` | visual reference | **Being placed by Skye** — non-authoritative (plan + tests govern); for BUILD `live` iteration only. Ignore the older `reference-identify-mockup.html`. |

No backend/data/schema (`data/xps`, `parser.py`, `app.py`, `fitting.py`) changes. Project *file format* changes only in Phase B (additive, versioned).

---

## Phase ordering & review gates

1. **Phase A** (client-only restructure) — diffs reviewed by Skye + Codex per task; no file-format change; safe to build/verify/iterate (`live`) freely.
2. **Phase B** (serialization) — **Codex reviews the B1 design (pure serialize/deserialize + version policy) BEFORE B2 wiring.** Touches saved-file format + back-compat.

Each task is TDD where the logic is pure (node `RefCore` tests run red→green); DOM/Chart.js tasks specify the exact change + a Playwright verification step (the existing codebase's pattern — pure logic in `RefCore` unit-tested, DOM verified in-browser). Commit after each task.

---

## PHASE A — Client-only restructure

### Task A0: Tier-color single source of truth (SSOT)

**Files:**
- Modify: `static/js/ref_identify_core.js` (add `TIER_COLORS` + `tierColor`)
- Modify: `templates/index.html` (route legend dot, dropdown badge, identify popover, existing `.ref-cand-tier`/`.ref-badge-*` through the SSOT)
- Test: `tests/js/ref_core.test.js`

> **DECISION (confirmed, OPEN-1):** `curated = green #3ddc84` / `machine = violet #b48eff` / `legacy = amber #ffbb44` (DESIGN tokens `state-green` / `state-purple` / `state-amber`). This **intentionally recolors the shipped identify cards** (machine green→violet, curated gray→green). All tier visuals consume `RefCore.tierColor(tier)` so the hue lives in exactly one place. **Violet contrast must be verified** against the panel/control backgrounds (see Step 6).

- [ ] **Step 1: Write the failing test** (`tests/js/ref_core.test.js`)

```js
test('tierColor is a single source of truth for the three data tiers', () => {
  // Confirmed mapping (OPEN-1) — update these literals to the approved hex.
  assert.strictEqual(RefCore.tierColor('curated'), '#3ddc84');
  assert.strictEqual(RefCore.tierColor('machine'), '#b48eff');
  assert.strictEqual(RefCore.tierColor('legacy'),  '#ffbb44');
});
test('tierColor falls back safely for unknown tiers', () => {
  assert.strictEqual(RefCore.tierColor('nonsense'), RefCore.TIER_COLORS.fallback);
  assert.strictEqual(RefCore.tierColor(undefined), RefCore.TIER_COLORS.fallback);
});
```

- [ ] **Step 2: Run it, watch it fail** — `node --test tests/js/ref_core.test.js` → FAIL (`tierColor` undefined).
- [ ] **Step 3: Implement in `RefCore`**

```js
const TIER_COLORS = { curated: '#3ddc84', machine: '#b48eff', legacy: '#ffbb44', fallback: '#8a9ab8' };
function tierColor(tier) { return TIER_COLORS[tier] || TIER_COLORS.fallback; }
// export alongside existing RefCore members (same module.exports / window.RefCore pattern already in the file)
```

- [ ] **Step 4: Run it, watch it pass** — `node --test tests/js/ref_core.test.js` → PASS (existing 18 still green).
- [ ] **Step 5: Route existing tier visuals through the SSOT** — in `templates/index.html`, replace the hard-coded tier hues in `.ref-cand-tier.{curated,machine,legacy}` and the element-group header badges by driving their color from `RefCore.tierColor(tier)` (inline style or CSS custom property set in JS). Leave the *confidence* `.ref-tier.{strong,possible,weak}` classes alone — those are confidence labels, not data tiers.
- [ ] **Step 6: Verify (Playwright) — incl. violet contrast** — open identify on a known peak; confirm each candidate's data-tier badge uses the approved hue. **Measure violet (`#b48eff`) contrast** as badge text on the control background (`#1a2030`) and as a color-dot on the panel background (`#131720`); badge text must hit ≥4.5:1 (≥3:1 if rendered bold/large). If violet text is borderline, render the badge label in `ink-data` with violet only on the dot/border (color is never the sole signal anyway — the tier word/toast carries meaning). Screenshot with measured ratios.
- [ ] **Step 7: Commit** — `git commit -m "ref-ux: tier-color SSOT (RefCore.tierColor) routed through all tier visuals"`

---

### Task A1: Persistent element overlays (reverse panel-gating)

**Files:**
- Modify: `static/js/ref_identify_core.js` (`elementOverlayVisible` contract)
- Modify: `templates/index.html` (`_refChartItems` gate `:10859`)
- Test: `tests/js/ref_core.test.js`

- [ ] **Step 1: Update the failing test for the new contract** — `elementOverlayVisible` must no longer require `panelOpen`. Visibility = active non-stack chart + has selection; palette state is irrelevant.

```js
test('elementOverlayVisible no longer depends on the palette being open', () => {
  const base = { activeChart: true, isStackTab: false };
  assert.strictEqual(RefCore.elementOverlayVisible({ ...base, panelOpen: false }), true);
  assert.strictEqual(RefCore.elementOverlayVisible({ ...base, panelOpen: true }), true);
  assert.strictEqual(RefCore.elementOverlayVisible({ activeChart: true, isStackTab: true, panelOpen: true }), false);
  assert.strictEqual(RefCore.elementOverlayVisible({ activeChart: false, isStackTab: false, panelOpen: true }), false);
});
```

- [ ] **Step 2: Run it, watch it fail** (the current impl returns false when `panelOpen` is false).
- [ ] **Step 3: Implement** — drop `panelOpen` from the predicate (keep the param accepted for back-compat but ignored). Visibility gated only on `activeChart && !isStackTab`.
- [ ] **Step 4: Run it, watch it pass.**
- [ ] **Step 5: Update `_refChartItems`** (`templates/index.html:10870`) — remove the `if (!_refPanelOpen …) return null;` clause; keep the active-chart (`chart === state.chart && !chart._xpsStackTabId`) and stack-tab guards. Overlays now draw whenever `_refGetSel().syms` is non-empty.
- [ ] **Step 6: Verify (Playwright)** — select 2 elements, close the palette → overlays + bands remain on the chart; switch to a stack tab → overlays vanish; switch back → return. Screenshot.
- [ ] **Step 7: Commit** — `git commit -m "ref-ux: element overlays persist after palette closes (de-gate _refChartItems)"`

---

### Task A2: Element reference lines → dashed (three-language distinction)

**Files:** Modify `templates/index.html` (`xpsRefLinesPlugin.afterDraw` `:10974`)

- [ ] **Step 1: Change the line dash** — element PE nominal lines from solid to dashed, element-colored; keep Auger a distinct dash. Identify stays solid accent (A6); compound stays amber dashed (unchanged). Pick distinguishable dashes (e.g. element PE `[6,3]`, Auger `[2,3]`) so the three languages read apart by *style + color*.

```js
// was: c.setLineDash(m.isAuger ? [5, 4] : []);
c.setLineDash(m.isAuger ? [2, 3] : [6, 3]);   // element overlays always dashed; identify alone is solid
```

- [ ] **Step 2: Verify (Playwright + `live` eyeball)** — element overlay (dashed colored) vs compound (amber dashed) vs identify (solid accent) are visually distinct on one chart. **Non-blocker (confirmed):** eyeball the three dash languages + amber compound together in `live` mode — the two dashed languages must read apart by dash pattern + color, not blur into each other; tune dash arrays if needed. Screenshot all three together.
- [ ] **Step 3: Commit** — `git commit -m "ref-ux: element overlay lines dashed; solid reserved for identify marker"`

---

### Task A3: Always-visible on-chart legend (overlay manager)

**Files:** Modify `templates/index.html` (new legend DOM + render fn; hook into overlay add/remove)

The legend is an HTML overlay positioned over the chart corner (NOT a Chart.js plugin — it needs interactive chips). It lists the active `sel.syms`; each chip = element color swatch + **tier color-dot** (`RefCore.tierColor`, not the word) + chevron + remove (×). It is the overlay manager: removing a chip removes the element from `sel.syms`; it is visible whenever overlays exist, regardless of palette state.

- [ ] **Step 1: Add legend container + render fn** — `_refRenderLegend()` builds chips from `_refGetSel().syms`; mount in `#main-chart-wrap` (positioned, `pointer-events` only on chips). Each chip: `role="group"`, swatch `<span>`, tier dot `<span title>` (hover → tier toast, A4), chevron button (opens dropdown, A4), remove button (`aria-label="Remove <sym> overlay"`).
- [ ] **Step 2: Wire lifecycle + shared color assignment** — call `_refRenderLegend()` wherever `sel.syms` changes (`_refToggleElement` and the palette grid handlers) and on tab switch; hide when empty or on stack tabs. **Migrate the colorIdx assignment on element-add from the old `sel._nextColorIdx++` running counter to the shared `RefCore.nextColorIdx(sel.syms.map(s=>s.colorIdx), ELEMENT_MARKER_COLORS.length)`** (defined in B1; pure + order-independent — land it here at first use, reuse at load in B2 Step 3). This is the deliberate, flagged change to shared color assignment: it makes in-session picks residue-aware (no repeated rendered colors until the palette is exhausted) and is the SAME path post-load picks use, so restored and new overlays never share a rendered color while residues remain. Retire the vestigial `_nextColorIdx` field.
- [ ] **Step 3: a11y** — chips keyboard-reachable (`tabindex`), remove on Enter/Space, `aria-pressed` not needed (button), tier meaning carried by the toast text + chip label (never color-only).
- [ ] **Step 4: Verify (Playwright)** — add/remove elements via legend with palette closed; keyboard remove; tier dot hue matches SSOT; legend hidden on stack tab. Screenshot.
- [ ] **Step 5: Commit** — `git commit -m "ref-ux: always-visible on-chart legend manages element overlays"`

---

### Task A4: Legend chip dropdown (reuse DETAILS) + tier toast

**Files:** Modify `templates/index.html` (chip dropdown using the fixed/portal pattern `:202`; reuse `_refRenderElementGroup`)

- [ ] **Step 1: Tier toast** — hover/focus the chip tier dot → small fixed-position toast with the **canonical wording** for that tier (see Recon). Dismiss on blur/leave; respects `prefers-reduced-motion`.
- [ ] **Step 2: Chip dropdown** — click chip (or chevron) → a fixed/portal-positioned dropdown (z-index from the semantic scale, A5) containing the **full DETAILS** for that element by calling the existing `_refRenderElementGroup(s, sel, range)` — transition rows, tier note, `short_caveat` + `more…`, citation. Position with `getBoundingClientRect` + viewport clamp; close on outside-click/Esc. **Must escape `overflow:hidden`** (use the existing portal pattern, not `position:absolute` inside the chart wrap).
- [ ] **Step 3: a11y** — dropdown is a focus-trapped popover (`role="dialog"`/`aria-label`), Esc closes and returns focus to the chip; `more…` button keeps its `aria-expanded`.
- [ ] **Step 4: Verify (Playwright)** — open a chip dropdown with palette closed; confirm it shows the same content as the old DETAILS pane (provenance, caveat, more… expands); confirm it is not clipped by the chart container; Esc returns focus. Screenshot.
- [ ] **Step 5: Commit** — `git commit -m "ref-ux: legend chip dropdown reuses DETAILS renderer; tier toast (canonical wording)"`

---

### Task A5: Floating palette container (drag / collapse / responsive) + semantic z-index

**Files:** Modify `templates/index.html` (CSS for `#ref-panel` `:176`; drag/collapse JS; localStorage position; z-index scale)

- [ ] **Step 1: Semantic z-index scale** — define CSS custom properties (e.g. `--z-base:1; --z-legend:30; --z-palette:200; --z-dropdown:2200; --z-identify-popover:2300; --z-toast:2400; --z-tooltip:2600`) and use them for the new surfaces; fold the existing `--z-popover` into the scale. No new raw 999/9999. **Non-blocker (confirmed):** the **identify popover must sit ABOVE the palette** (`--z-identify-popover` > `--z-palette`) so identify results are never hidden behind the palette box; the chip dropdown (`--z-dropdown`) is likewise above the palette.
- [ ] **Step 2: Convert container to floating** — `#ref-panel` → `position:fixed`, removed from the chart flex flow (chart reclaims full width — **never compressed**). Sensible default position (e.g. top-right inset), `--z-palette`. Keep the three internal zones.
- [ ] **Step 3: Drag** — a header drag handle; pointer events update `left/top`; **viewport-clamped** so it can't leave the screen. Persist last position to `localStorage` (e.g. `xps.refPalette.pos`); restore on open (clamp on restore in case the viewport shrank).
- [ ] **Step 4: Collapse** — collapse/expand toggle (header) that hides the zones to a compact title bar; collapsed state persisted. Overlays/legend are unaffected by collapse (they live on the chart, A1/A3).
- [ ] **Step 5: Responsive fallback** — below ~640px the palette becomes a bottom sheet / full-width (dragging disabled; touch). Use a media query + a `matchMedia` guard around the drag handlers.
- [ ] **Step 6: Verify (Playwright + manual `live`)** — desktop: drag, clamp at edges, reload restores position, collapse persists, chart width unchanged when palette open; narrow viewport: bottom-sheet, no drag. **Drag/collapse feel is iterated in-browser with impeccable `live` (not one-shot).** Screenshots at wide + narrow.
- [ ] **Step 7: Commit** — `git commit -m "ref-ux: floating draggable/collapsible/responsive palette; semantic z-index scale; chart never compressed"`

---

### Task A6: Per-peak Identify popover (de-gate + click-anchored)

**Files:** Modify `templates/index.html` (`_refIdentState` `:11059`, identify marker `:10930`, click handler `:4941`, render `_refRenderIdentifyResults` `:11327`)

- [ ] **Step 1: De-gate identify** — remove the `_refPanelOpen` requirement from `_refIdentState` (`:11059`); identify works with the palette closed. Keep active-chart + non-stack guards.
- [ ] **Step 2: Arm from toolbar** — identify arm control reachable without the palette (toolbar toggle sets `mode='identify'`); clicking the chart calls `_refIdentifyAt` (already wired `:4941`).
- [ ] **Step 3: Identify marker = solid accent + caret, transient** — keep the solid accent line (`:10938`); add a caret/triangle glyph at top; ensure it is cleared by `_refClearIdentify`. Confirm it remains visually distinct from the now-dashed element overlays (A2).
- [ ] **Step 4: Click-anchored popover** — render the candidate list (reuse `_refRenderIdentifyResults` markup) in a fixed/portal popover anchored at the click pixel (viewport-clamped), separate from the legend, at **`--z-identify-popover`** (above the palette — A5 Step 1 — so results are never hidden behind the box). Candidates show tier via `RefCore.tierColor` (A0). Close on Esc/outside-click; `_refClearIdentify` removes marker + popover.
- [ ] **Step 5: Respect the Chart.js v4 leaf-mutation rule** — marker draw mutates only canvas context in the plugin; popover is DOM. No dataset array swaps mid-render.
- [ ] **Step 6: Verify (Playwright)** — with palette closed: arm identify, click a peak → popover at click with tier-capped candidates (elements + compounds); marker solid+caret; Esc clears both; click another peak → marker moves (transient). Confirm physics: PE candidates at `nominal_be_ev`, Auger move only on source switch, region=null never throws. Screenshot.
- [ ] **Step 7: Commit** — `git commit -m "ref-ux: per-peak identify popover, de-gated from palette; solid+caret transient marker"`

---

### Task A7: Reference-mode & lifecycle reconciliation

**Files:** Modify `templates/index.html` (`_refReferenceModeWanted` `:10998`, repaint hooks)

- [ ] **Step 1: Reconcile reference-mode trigger** — `_refReferenceModeWanted` currently keys on `_refPanelOpen` (`:11001`). With persistent overlays, the bare 0–1200 eV reference chart should appear when there is a selection and no spectrum, regardless of palette open/closed. Update the predicate accordingly.
- [ ] **Step 2: Repaint coverage** — ensure overlay/legend/identify all repaint on: tab switch, source switch (Auger移动), palette open/close, spectrum load/unload, charge-correction change.
- [ ] **Step 3: Verify (Playwright)** — no-spectrum tab with selection + palette closed → reference view with persistent dashed overlays + legend; load spectrum → overlays rebase; source switch moves only Auger. Screenshot.
- [ ] **Step 4: Commit** — `git commit -m "ref-ux: reconcile reference-mode + repaint lifecycle with persistent overlays"`

---

## PHASE B — Serialization (Codex reviews B1 before B2)

### Task B1: Pure, versioned serialize/deserialize in RefCore  *(Codex reviews this design BEFORE B2 wiring)*

**Files:**
- Modify: `static/js/ref_identify_core.js`
- Test: `tests/js/ref_core.test.js`

This is the **complete data-layer contract** Codex reviews before any save/load wiring (B2) is written. Nothing in B2/B3 may diverge from it.

**1. Exact JSON shape + DECOUPLED internal versions.** Two homes, by confirmed scope (D2): **element overlays are PER-TAB**, **compound markers are GLOBAL at project-meta**. **Each schema carries its OWN internal version constant** (P2 — decoupled so one can migrate without the other): `RefCore.REF_OVERLAYS_VERSION = 1` and `RefCore.REF_COMPOUND_MARKERS_VERSION = 1`. Both are independent of the top-level project `version` (which **stays at 3** — D3).

Per-tab `refOverlays` (omitted when a tab has no valid element selection):
```jsonc
"refOverlays": {
  "v": 1,
  "syms": [ { "sym": "Ti", "colorIdx": 0, "tier": "machine" },
            { "sym": "Cu", "colorIdx": 1, "tier": "curated" } ],
  "source": "AlKa",          // 'AlKa' | 'MgKa'
  "showWeak": false,
  "includeAuger": false
}
```
Project-meta `refCompoundMarkers` (omitted when empty), preserving today's GLOBAL compound-marker scope:
```jsonc
"refCompoundMarkers": {
  "v": 1,
  "markers": [ { "sym": "Cu", "state": "Cu2O", "be": 932.5, "ref": "NIST ..." } ]
}
```

**Functions — all four are TOTAL (never throw on any input):**
- `serializeRefOverlays(sel)` → the per-tab object, or **`null`** when `sel` is nullish / not an object / has no valid syms (so B2 can call it on a tab whose lazy `_refSel` was never created). `colorIdx` + `tier` saved per element. The pure serializer **never reads** `tab._refIdentify` / `sel.tolEv`, so identify is structurally un-serializable here (the *`buildTabData` never emits `_refIdentify`* claim is an e2e guarantee — see §3).
- `serializeRefCompoundMarkers(markers)` → the project-meta object, or **`null`** when the array is nullish / empty / not an array.
- `deserializeRefOverlays(obj, paletteLen)` → a partial sel `{ syms, source, showWeak, includeAuger }` to merge over `_refDefaultSel()`. **No stored color counter** — the next colorIdx is computed on demand by the shared helper below; the vestigial `_refDefaultSel._nextColorIdx` is retired.
- `deserializeRefCompoundMarkers(obj)` → an array of marker objects for the global `_refCompoundMarkers`.

**Shared color-assignment helper — the deliberate, FLAGGED change to color assignment:**
```js
// First index whose PALETTE RESIDUE (i % paletteLen) is NOT already used by the
// current overlays; deterministic reuse (max(used)+1) once every residue is taken.
RefCore.nextColorIdx(usedColorIndices, paletteLen) -> integer
```
- This ONE helper assigns `colorIdx` for **BOTH in-session element picks AND the post-load next-pick** — a single source of truth. **Deliberate behavior change (flagged):** it also fixes *in-session* same-rendered-color collisions — today's running `_nextColorIdx++` counter can wrap the palette and repeat a color; routing picks through the helper removes that, which is desirable and on-feature.
- Call sites: the in-session pick path (Phase A — the `_refToggleElement` / palette-grid + legend add path, currently `sel._nextColorIdx++`) and load (B2 Step 3), both as `RefCore.nextColorIdx(sel.syms.map(s => s.colorIdx), ELEMENT_MARKER_COLORS.length)`. The helper is pure + order-independent — implement it at first use (Phase A) and reuse verbatim at load.
- **Restored colors:** a **valid** saved `colorIdx` (`Number.isInteger(c) && c >= 0`) is preserved **verbatim** (even if two saved entries share one — we don't reshuffle the saved state). A **missing/invalid** `colorIdx` (negative, `NaN`, `Infinity`, fractional, `null`, string, array, object, absent) is assigned **deterministically by position** via the same helper against the colorIdx already resolved for earlier-kept entries — so even a malformed save yields stable, residue-aware colors. (Never `Math.trunc` a non-finite/negative value into a real index.)

**2. Load behavior — deserialize is TOTAL (never throws). Two DISTINCT failure granularities (resolving the prior table contradiction):**
| Input class | Result |
|---|---|
| **absent** (`undefined` / key missing) | empty (`syms:[]` / `markers:[]`) — clean, no overlays |
| **envelope-malformed** (not an object; `v` missing or non-numeric; `v` > the field's VERSION constant; `syms`/`markers` not an array) | **drop the WHOLE field → empty.** A blob with no/invalid `v` is NOT trusted as implicit-v1; a newer `v` is ignored (don't misread a future shape). (`v < current` has no case at v1; a future v2 adds an explicit `v===1` upgrade branch here.) |
| **entry-invalid** (envelope OK + version OK, individual entries bad) | **keep valid entries, skip invalid ones.** Overlay entry invalid **iff no resolvable `sym`**; its `colorIdx`/`tier` are *repaired*, not cause-to-drop. Marker entry invalid **iff `be` is not finite-numeric**. |
| **overlay entry repair** | missing/invalid `colorIdx` → by-position helper fallback; missing/unknown `tier` → **kept as-is**, rendered with `RefCore.tierColor` fallback (entry NOT dropped); `source` → `'AlKa'` unless exactly `'MgKa'`; `showWeak`/`includeAuger` coerced to bool; **duplicate `sym` → keep FIRST, drop later duplicates** (prevents duplicate legend chips + double draws). |
| **marker entry repair** | `sym` is **optional** (absent tolerated — live markers allow it); `state`/`ref` coerced to string (empty if absent); only a non-finite `be` drops the entry. |

**3. Guarantees — and which LAYER pins each (correcting the prior "all pinned in Step 1" overstatement):**
- **PURE (pinned by B1 Step-1 tests):**
  - Round-trip identity for a valid selection.
  - **Rendered-color determinism:** *the next-picked element renders a color distinct from every restored overlay while unused palette residues remain, and falls back to deterministic reuse (`max(used)+1`) once the palette is exhausted.* (Guarantee is at the **rendered-color** level — no "integer didn't collide" wording.)
  - Valid `colorIdx` preserved verbatim; missing/invalid → deterministic by-position via the helper.
  - Envelope-malformed / newer-version / absent → empty; entry-invalid skipped while valid entries kept; duplicate `sym` deduped first-wins; missing/unknown `tier` kept (fallback-colored).
  - The **pure serializer output never contains `tolEv`/identify keys**; serializers are total (`null` on empty/nullish/malformed).
  - Compound markers round-trip at the global-list shape; absent/envelope-malformed/newer-version → empty; non-finite `be` dropped, absent `sym` tolerated.
- **E2E (pinned by B2 Step 4 / B3 — NOT B1):** that `buildTabData` itself never emits `_refIdentify`; that compound markers actually land in **project-meta** (not per-tab); that an old project loads clean in the running app.

- [ ] **Step 1: Write failing tests** (paletteLen passed explicitly so tests don't depend on `ELEMENT_MARKER_COLORS`)

```js
const PAL = 8;   // stand-in palette length for the pure tests
// --- decoupled version constants ---
test('overlays and compound markers have independent version constants', () => {
  assert.strictEqual(typeof RefCore.REF_OVERLAYS_VERSION, 'number');
  assert.strictEqual(typeof RefCore.REF_COMPOUND_MARKERS_VERSION, 'number');
});
// --- nextColorIdx: residue-aware, deterministic reuse when exhausted ---
test('nextColorIdx returns the first index whose palette residue is unused', () => {
  assert.strictEqual(RefCore.nextColorIdx([0,5,2], PAL), 1);           // residues {0,5,2} → 1 free
  assert.strictEqual((1 % PAL), 1);                                     // and 1 is a distinct rendered residue
});
test('nextColorIdx falls back to max(used)+1 once every residue is taken', () => {
  assert.strictEqual(RefCore.nextColorIdx([0,1,2], 3), 3);             // palette of 3 fully used → reuse
  assert.strictEqual(RefCore.nextColorIdx([], PAL), 0);                // none used → 0
});
// --- serialize: total, deterministic, identify-free ---
test('serializeRefOverlays is total: null for empty/nullish/malformed sel', () => {
  for (const bad of [undefined, null, 42, 'x', {}, { syms:[] }, { syms:'no' }]) {
    assert.strictEqual(RefCore.serializeRefOverlays(bad), null);
  }
});
test('serializeRefOverlays captures selection and never emits identify keys', () => {
  const sel = { syms:[{sym:'Ti',colorIdx:0,tier:'machine'},{sym:'Cu',colorIdx:1,tier:'curated'}],
                source:'MgKa', showWeak:true, includeAuger:true, tolEv:0.9, _refIdentify:{be:1} };
  const out = RefCore.serializeRefOverlays(sel);
  assert.strictEqual(out.v, RefCore.REF_OVERLAYS_VERSION);
  assert.deepStrictEqual(out.syms, [{sym:'Ti',colorIdx:0,tier:'machine'},{sym:'Cu',colorIdx:1,tier:'curated'}]);
  assert.strictEqual(out.source,'MgKa');
  assert.ok(!('tolEv' in out) && !('cands' in out) && !('_refIdentify' in out));
});
// --- round-trip: valid colorIdx verbatim ---
test('round-trip preserves a valid colorIdx verbatim', () => {
  const sel = { syms:[{sym:'Fe',colorIdx:3,tier:'machine'}], source:'AlKa', showWeak:false, includeAuger:false };
  const back = RefCore.deserializeRefOverlays(RefCore.serializeRefOverlays(sel), PAL);
  assert.deepStrictEqual(back.syms, [{sym:'Fe',colorIdx:3,tier:'machine'}]);
  assert.strictEqual(back.source,'AlKa');
});
// --- deserialize totality: absent / envelope-malformed / newer-version ---
test('deserialize: absent or envelope-malformed → clean empty (no throw)', () => {
  for (const bad of [undefined, null, {}, 42, 'x', { syms:[{sym:'Cu',colorIdx:0}] }/*no v*/,
                     { v:'1', syms:[] }/*non-numeric v*/, { v:1, syms:'garbage' }]) {
    assert.deepStrictEqual(RefCore.deserializeRefOverlays(bad, PAL).syms, []);
  }
});
test('deserialize: newer internal version is ignored (no misread of a future shape)', () => {
  assert.deepStrictEqual(RefCore.deserializeRefOverlays({ v: 999, syms:[{sym:'Cu',colorIdx:0}] }, PAL).syms, []);
});
// --- deserialize entry repair: skip no-sym, repair colorIdx, keep unknown tier, dedup sym ---
test('deserialize entry repair: keep valid, skip no-sym, repair invalid colorIdx, keep unknown tier', () => {
  const back = RefCore.deserializeRefOverlays({ v:1, source:'bogus', showWeak:'yes',
    syms:[ {sym:'Cu',colorIdx:0,tier:'curated'},
           {colorIdx:1},                       // no sym → dropped
           {sym:'Ti',colorIdx:-3},             // invalid colorIdx → by-position helper fallback
           {sym:'Xe',colorIdx:2,tier:'weird'}, // unknown tier → kept (fallback-colored at render)
           {sym:'Cu',colorIdx:7} ] }, PAL);
  assert.deepStrictEqual(back.syms.map(s=>s.sym), ['Cu','Ti','Xe']);   // no-sym dropped; duplicate Cu → keep first
  assert.strictEqual(back.syms[0].colorIdx, 0);                        // Cu verbatim
  assert.ok(Number.isInteger(back.syms[1].colorIdx) && back.syms[1].colorIdx >= 0); // Ti repaired
  assert.notStrictEqual(back.syms[1].colorIdx % PAL, 0 % PAL);         // and distinct residue from Cu
  assert.strictEqual(back.syms[2].tier, 'weird');                      // unknown tier preserved (entry kept)
  assert.strictEqual(back.source, 'AlKa');                             // invalid source → default
  assert.strictEqual(back.showWeak, true);                             // 'yes' coerced to bool
});
// --- rendered-color determinism end to end ---
test('post-load next pick renders a color distinct from all restored while residues remain', () => {
  const back = RefCore.deserializeRefOverlays({ v:1,
    syms:[{sym:'Cu',colorIdx:0},{sym:'Ti',colorIdx:5},{sym:'Fe',colorIdx:2}] }, PAL);
  const usedResidues = new Set(back.syms.map(s => s.colorIdx % PAL));
  const next = RefCore.nextColorIdx(back.syms.map(s=>s.colorIdx), PAL);
  assert.ok(!usedResidues.has(next % PAL));                            // distinct RENDERED color
});
// --- compound markers: global scope, totality, partial-invalid, newer-version ---
test('serializeRefCompoundMarkers is total: null for empty/nullish/non-array', () => {
  for (const bad of [undefined, null, [], 'x', 42, {}]) {
    assert.strictEqual(RefCore.serializeRefCompoundMarkers(bad), null);
  }
});
test('compound markers round-trip at global scope; absent/malformed/newer → empty', () => {
  const markers = [{ sym:'Cu', state:'Cu2O', be:932.5, ref:'NIST' }];
  const out = RefCore.serializeRefCompoundMarkers(markers);
  assert.strictEqual(out.v, RefCore.REF_COMPOUND_MARKERS_VERSION);
  assert.deepStrictEqual(RefCore.deserializeRefCompoundMarkers(out), markers);
  assert.deepStrictEqual(RefCore.deserializeRefCompoundMarkers(undefined), []);          // absent
  assert.deepStrictEqual(RefCore.deserializeRefCompoundMarkers({ v:1, markers:'x' }), []); // envelope-malformed
  assert.deepStrictEqual(RefCore.deserializeRefCompoundMarkers({}), []);                  // no v
  assert.deepStrictEqual(RefCore.deserializeRefCompoundMarkers({ v:999, markers:[{be:1}] }), []); // newer version
});
test('compound markers: non-finite be dropped, absent sym tolerated (partial-invalid)', () => {
  const back = RefCore.deserializeRefCompoundMarkers({ v:1, markers:[
    { state:'surface', be:530.1 },          // no sym → tolerated
    { sym:'Cu', state:'Cu2O', be:'bad' },   // non-finite be → dropped
    { sym:'Fe', be:711 } ] });
  assert.deepStrictEqual(back.map(m=>m.be), [530.1, 711]);
});
```

- [ ] **Step 2: Run, watch fail.**
- [ ] **Step 3: Implement** in `RefCore`: the two version constants (`REF_OVERLAYS_VERSION`, `REF_COMPOUND_MARKERS_VERSION`), the shared `nextColorIdx(usedColorIndices, paletteLen)` helper, and the four total functions (`serializeRefOverlays`, `deserializeRefOverlays(obj, paletteLen)`, `serializeRefCompoundMarkers`, `deserializeRefCompoundMarkers`) to satisfy §1–§3.
- [ ] **Step 4: Run, watch pass** (existing tests still green).
- [ ] **Step 5: Commit** — `git commit -m "ref-ux(serialize): RefCore versioned overlay+marker serialize/deserialize + residue-aware nextColorIdx"`
- [ ] **GATE: Codex reviews the revised B1 (shape, decoupled versions, envelope-vs-entry rules, rendered-color guarantee + shared helper, identify/global-scope/total guarantees, pure-vs-e2e attribution) BEFORE B2 wiring.**

---

### Task B2: Wire serialization into save/load

**Files:** Modify `templates/index.html` (`buildTabData` `:8376`, project-meta assembly `:8417`, `_loadProjectJSON` `:8604`)

> **Compat boundary (confirmed, OPEN-3) — stated precisely, no hand-waving.**
> - **Top-level project `version` STAYS at 3.** `refOverlays` (per-tab) and `refCompoundMarkers` (project-meta) are **additive optional fields**, each with its own internal `v`.
> - **Backward-compatible (GUARANTEED + tested, B2/B3):** an old project (no overlay fields) loads clean in the new app — `deserialize*` returns empty, no overlays, no error.
> - **Forward-compatibility is NOT guaranteed.** A new project opened in an OLD app build may have `refOverlays`/`refCompoundMarkers` **ignored OR rejected depending on that old loader's unknown-field handling** — we do **not** guarantee forward-compatibility. *Verified fact for the concrete case:* the shipped loader at `bfedc95` reads a known-property whitelist (`t.id`, `t.peaks`, `t.isStack`, `t.name`, `t.lineWidth`, `t.ui`, … and validates only those + size caps at `templates/index.html:8618-8664`) — it has **no unknown-field rejection**, so it **silently ignores** the new fields and opens the project minus those overlays. That is the observed behavior of `bfedc95` specifically; an older or differently-built loader that strict-validates unknown fields could instead **reject** the file. We promise only backward-compat (old project → new app); forward-compat (new project → old app) is best-effort and explicitly untested. **Lossy-resave caveat:** an old app that ignores the fields and then **re-saves** the project will **drop** the `refOverlays`/`refCompoundMarkers` it didn't understand — round-tripping a new project through an old build silently loses overlays/markers.

- [ ] **Step 1: Save (per-tab overlays)** — in `buildTabData(t)` non-stack branch, add `refOverlays: RefCore.serializeRefOverlays(t._refSel)` **only when non-null** (omit the key entirely otherwise, so old-shaped saves stay byte-clean). Never add `_refIdentify`/`tolEv`.
- [ ] **Step 2: Save (global compound markers)** — in the project-meta assembly (`:8417`, where `version`/`activeId` are set), add `refCompoundMarkers: RefCore.serializeRefCompoundMarkers(_refCompoundMarkers)` when non-null. Leave `version: 3` unchanged. This keeps compound markers at the GLOBAL project scope they have today (no per-tab migration this round).
- [ ] **Step 3: Load** — in `_loadProjectJSON`: (a) per tab, after it is built, `tab._refSel = { ..._refDefaultSel(), ...RefCore.deserializeRefOverlays(saved.refOverlays, ELEMENT_MARKER_COLORS.length) }` (valid `colorIdx` restored verbatim; invalid repaired by the shared helper). The next in-session pick in that tab computes its colorIdx via `RefCore.nextColorIdx(sel.syms.map(s=>s.colorIdx), ELEMENT_MARKER_COLORS.length)` — the SAME helper used everywhere — so it renders distinct from restored overlays while residues remain. (b) once, restore the global list `_refCompoundMarkers.splice(0, _refCompoundMarkers.length, ...RefCore.deserializeRefCompoundMarkers(data.refCompoundMarkers))`; (c) trigger `_refRenderLegend()` + chart repaint so reopened projects re-show overlays + markers. Never restore an identify marker.
- [ ] **Step 3b: Verify rendered color (Playwright)** — load a project with overlays, then pick a NEW element in a restored tab; assert its **rendered color** differs from every restored overlay (while the palette has unused residues). (The pure invariant is covered in B1; this confirms the wired path uses the shared helper.)
- [ ] **Step 4: Verify (Playwright, in-app round-trip)** — pick overlays (2 elements, distinct tiers incl. machine→violet) + place a compound marker; arm identify on a peak (transient marker visible); save `.proj.json`; reload → identical overlays/colors/legend + compound marker re-shown, **identify marker absent**. Then load an **old** project (no overlay fields) → loads clean, no overlays, **no console error**. Screenshots of both.
- [ ] **Step 5: Commit** — `git commit -m "ref-ux(serialize): persist+restore per-tab overlays + global compound markers (additive, v3, deterministic colors)"`

---

### Task B3: Version back-compat + `.proj.zip` parity

**Files:** Modify `templates/index.html` (zip manifest path `:8432`); Test: in-app

- [ ] **Step 1:** Confirm the ≥5-tab `.proj.zip` path round-trips `refOverlays` identically to `.proj.json` (per-spectrum JSON inside the archive carries the per-tab field). **Compound markers live at project-meta**, so they go in the zip **manifest** (`:8433`) — same global scope as the `.proj.json` meta.
- [ ] **Step 2: Verify (Playwright)** — 5+ tabs with overlays + a global compound marker → `.proj.zip` → reload → overlays restored on the right tabs, compound marker restored once globally; an old `.proj.zip` without the fields loads clean.
- [ ] **Step 3: Commit** — `git commit -m "ref-ux(serialize): .proj.zip overlay round-trip + back-compat"`

---

## Tests (summary)

- **node `RefCore` (`tests/js/ref_core.test.js`)** — extend with: `tierColor` SSOT (A0), `elementOverlayVisible` de-gated contract (A1), the residue-aware `nextColorIdx` helper, and the full B1 serialize/deserialize contract — round-trip, **rendered-color determinism** (distinct while residues remain, deterministic reuse when exhausted), total serializers, decoupled version constants, envelope-malformed-vs-entry-invalid handling (absent / no-`v` / non-numeric-`v` / newer-version / partially-invalid), duplicate-`sym` first-wins, unknown-`tier` kept, and compound-marker partial-invalid/newer-version. **Do not weaken the existing 18.** Run: `node --test tests/js/ref_core.test.js`.
- **pytest** — no backend change expected; run full `pytest -v` to confirm zero regressions (incl. the durable snapshot guards, which must stay green).
- **Playwright (prod venv, build-phase verification)** — persistence after palette close (A1), three marker languages (A2/A6), legend + chip dropdown reuse (A3/A4), floating drag/clamp/collapse/responsive (A5), identify popover (A6), reference-mode (A7), save/load round-trip + old-project back-compat (B2/B3), a11y sweep.

## Do-NOT-regress checklist (carry from `84e1bb8`)

- **Physics:** PE markers at `nominal_be_ev` directly in corrected-BE frame, **never** shifted by `ccShift`; Auger at `hv − KE − φ`, moves **only** on source switch; line-list filtering uses acquisition range, draw clips to zoom; the `be`/region-null guard never throws (`:11149`).
- **Provenance:** citation ids, NIST codes, `curation_notes`, `short_caveat` + `more…` all preserved in the reused DETAILS dropdown; non-definitive language ("candidate", not "identified as").
- **a11y:** periodic-table cell `tabindex`/`role`/`aria-pressed`/Enter-Space preserved; new legend chips + dropdowns + popover fully keyboard-operable with Esc/focus-return; tier meaning never color-only (dot + toast text + label); WCAG AA contrast on dark theme; motion ≤200ms + `prefers-reduced-motion`; ≥24px targets.
- **Architecture:** `RefCore` stays the single source for pure logic; tier-cap (`capConfidenceByTier`) + `mergeAndRankCandidates` golden tests unchanged; Chart.js v4 leaf-mutation rule respected.

## Decisions (confirmed — locked into the tasks above)

- **D1 — Tier colors (was OPEN-1):** `curated = green #3ddc84` / `machine = violet #b48eff` / `legacy = amber #ffbb44`, one SSOT via `RefCore.tierColor`. **Recoloring the shipped identify cards is intended.** A0 Step 6 verifies violet contrast against panel/control backgrounds.
- **D2 — Compound-marker scope (was OPEN-2):** stay **GLOBAL at project-meta** (preserve current behavior); element overlays stay **per-tab** in `buildTabData`. No marker-scope migration this round.
- **D3 — Versioning (was OPEN-3):** additive optional `refOverlays` (per-tab) + `refCompoundMarkers` (project-meta), each with its own internal `v`; **top-level project `version` stays 3**. Compat boundary stated precisely in B2 (backward-compatible guaranteed/tested; forward-compat NOT guaranteed — the `bfedc95` loader ignores unknown fields, other/older builds may reject).
- **D4 — Mockup (was OPEN-4):** Skye places `docs/mockups/reference-ux-reframe-floating.html` for A5 `live`; **non-authoritative** (plan + tests govern); ignore the older `reference-identify-mockup.html`.
- **D5 — Tier wording (was OPEN-5):** canonical **live** wording shipped in `bfedc95` ONLY (see Recon); never the mockup draft.
- **D6 — Recon corrections (was OPEN-6), confirmed as sharpening intent, not changing it:** (a) identify already draws an on-chart marker → decision 3 is an enhancement (add caret, keep solid+transient, de-gate); (b) element PE lines are solid today → A2 makes them dashed so element-vs-identify no longer "look the same"; (c) `_refCompoundMarkers` is global → D2.

No residual open items. B1 remains the mandatory **Codex-before-B2** gate.
