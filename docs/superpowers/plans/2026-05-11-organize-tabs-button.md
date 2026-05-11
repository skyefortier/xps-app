# Organize Tabs Button Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a single "Organize Tabs" toolbar button that reorders the flat spectrum-tab strip so same-element tabs are adjacent, with Surveys first and Other last, preserving the active tab.

**Architecture:** Pure-frontend addition inside `templates/index.html`. A new classifier function maps each tab to one of `{survey, element:<symbol>, other}` using the filename (regex against the existing `XPS_ELEMENTS` table) with a BE-range fallback. A new action `organizeTabs()` performs a stable sort of `tabManager.tabs` in place — tab IDs and the `activeId` are unchanged, so persistence and active-tab tracking are unaffected. One small fix in the project-load path is required so a saved organized order round-trips faithfully.

**Tech Stack:** Vanilla JS embedded in a single Jinja-rendered HTML file (`templates/index.html`). No new dependencies. No backend changes.

---

## Scope Boundaries

**In scope (frontend only, `templates/index.html`):**
- New helper `classifyTabForOrganize(name, rawBE)`
- New action `organizeTabs()`
- New toolbar button + onclick wiring
- One-line fix in `_loadProjectJSON` so it honors saved order instead of re-sorting surveys to front

**Out of scope (do NOT touch):**
- `app.py`, `fitting.py`, `parser.py`, `vgd_parser.py`
- `.proj.json` schema (no new fields)
- Drag-and-drop tab reordering (already works; leave intact)
- Collapsible groups / hide-show / per-peak element detection
- Folder-load behavior in `createTab` (still wants surveys-to-front for fresh loads)

If during implementation any of these out-of-scope boundaries appear necessary, STOP and ask.

---

## File Touch Surface Estimate

Single file: `templates/index.html`

| Change | Approx. location | LOC added |
|---|---|---|
| `classifyTabForOrganize` + console test harness | After `TAB_COLORS` (line 2045), before `class TabManager` (line 2050) | ~75 |
| `organizeTabs()` action | After `_doSaveProject` block, top-level scope alongside other action funcs (e.g. near line 6920 or as a sibling of `tabManager` methods — see Task 2) | ~25 |
| Toolbar button markup | Inside `#chart-toolbar`, after line 1613 (`Overlay` button), before flex spacer line 1614 | 1 |
| Load fix | `_loadProjectJSON` lines 7151–7155 | -3, +1 |

**Total: ~100 lines added, ~3 lines removed, 1 file.**

---

## Design Decisions That Need Your Confirmation

Both have a default chosen below; redirect during plan review if you want different.

**D1. Button style:** The spec names two visually different button families:
- The "near + Add Peak" cluster uses `.btn .btn-sm` (rounded rectangles, 11px font, 6px/14px padding, no persistent active state).
- The Envelope/.../Invert BE cluster uses `.pill-toggle` (rounded pills, 10px font, 3px/10px padding, persistent active state via checkbox).

Since "Organize Tabs" is a one-shot action with no on/off state, the semantic match is `.btn .btn-sm`. **Default: `.btn .btn-sm`** (matches its immediate left-side neighbors + Add Peak, + Multiplet Pair, Overlay).

**D2. Button position:** **Default: between Overlay (line 1613) and the flex spacer (line 1614)** so the cluster reads `Undo Redo + Add Peak + Multiplet Pair Overlay │ Organize Tabs │ <spacer> <pill toggles>`. Alternative: at the very start of the action cluster after Redo. Going with "rightmost of the action cluster" because Organize Tabs is whole-strip rather than per-spectrum, and placing it nearest the right-hand toggles signals "view/strip controls".

**D3. Button label / glyph:** **Default: plain text "Organize Tabs"** (matches "Overlay", "+ Add Peak" precedent of plain words). Alternative: prepend a Unicode reorder glyph (e.g. `⇅ Organize Tabs`). Keeping plain text unless asked.

---

## Existing Code Anchors (verified)

| Concern | Location | Notes |
|---|---|---|
| Toolbar container | `templates/index.html:1608-1641` (`<div id="chart-toolbar">`) | Buttons + flex spacer + pill toggles |
| `+ Add Peak` button | line 1611 | `<button class="btn btn-sm" id="btn-add-peak" onclick="togglePlaceMode('peak')">+ Add Peak</button>` |
| `.btn` CSS | lines 172–185 | base + `:hover` |
| `.btn-sm` CSS | line 222 | small variant: `padding: 3px 8px; font-size: 10px;` |
| `XPS_ELEMENTS` table | lines 1849–1903 | element symbols → orbital BEs |
| `TAB_COLORS` | line 2045 | (anchor for placing helper just below) |
| `class TabManager` | line 2050 | `this.tabs` line 2052, `this.activeId` line 2053 |
| `createTab` | lines 2060–2107 | sets `tab.name` (extension-stripped), `tab.isSurvey`, pushes/unshifts |
| `activateTab(id)` | lines 2109–2157 | by-ID activation; early-return when already active |
| `renderTabBar()` | lines 2332–2423 | clears `#spectrum-tab-bar` and re-renders from `this.tabs` |
| `_doSaveProject` | lines 6922–6971 | saves `data.tabs = tabs.map(buildTabData)` — preserves array order ✓ |
| `_loadProjectJSON` | lines 7117–7162 | **re-sorts surveys to front on load (lines 7152–7155)** — breaks roundtrip; needs fix in Task 4 |
| `_loadZipProject` | lines 7164–7181 | calls `_loadProjectJSON`; inherits the fix automatically |

---

## Risks

1. **Load-side resort destroys organized order.** Confirmed above; Task 4 fixes by switching to plain `push` for all tabs on project load. This changes behavior for projects saved before this change too (their tabs will load in *literal saved order*, which for un-organized old projects is still the order the user saved them in — surveys may not float to the top anymore on reload). Acceptable: saved order is what the user chose.
2. **`isSurvey` flag vs filename regex.** A tab's `isSurvey` field is set at load using `/survey/i.test(name) || beRange > 200` (line 2070). The plan's classifier re-runs detection from name + BE rather than trusting `isSurvey`, so behavior is consistent regardless of how the tab was created. Trade-off: a tiny bit of recomputation, but no surprise discrepancies. (Alternative: use `tab.isSurvey` as a fast-path; rejected for clarity.)
3. **Element-symbol disambiguation.** "Cl2p" must classify as Cl, not C. Handled by sorting candidate symbols longest-first when scanning the filename.
4. **Active-tab visibility after reorder.** The tab strip has `tab-scroll-btn`s — the active tab might scroll out of view after reordering. Mitigation in Task 3: after `renderTabBar()`, scroll the active tab's DOM element into view if a helper exists; otherwise skip (low-impact polish).
5. **Stale `_preSurveyTabId`.** The TabManager stores `_preSurveyTabId` (line 2055) for restoring a tab when leaving the survey sidebar. IDs are stable through reorder, so this is unaffected — confirmed by inspection.
6. **`_updateSurveyPanel()` after reorder.** The survey panel is keyed by tab id, not index — reorder shouldn't disturb it, but Task 3 includes a defensive call to be safe.
7. **Pre-existing adjacent issue (flag only, do NOT fix here):** `_doSaveProject` records `activeId` (line 6949) but `_loadProjectJSON` ignores it and unconditionally activates the first new tab (line 7157). Out of scope for this commit; mention in PR description.

---

## File Structure Decision

All changes live inside the existing `templates/index.html`. The single-file frontend pattern is the established codebase style — do NOT introduce new files or split modules. Helper functions sit alongside their conceptual neighbors:

- `classifyTabForOrganize` is placed near `XPS_ELEMENTS` and `TAB_COLORS` (data) but kept free of `TabManager` internals (pure function — takes `name` and `rawBE`, returns a classification object). This keeps it independently console-testable.
- `organizeTabs()` is a top-level action like `togglePlaceMode`, `toggleOverlayMode`, etc., so the onclick wiring matches the rest of the toolbar.

---

## Tasks

### Task 1: Add `classifyTabForOrganize` helper and console test harness

**Files:**
- Modify: `templates/index.html` (insert after line 2045, before `// ═══ TAB MANAGER ═══` block at line 2047)

**Step 1: Insert the classifier and test harness**

- [ ] Open `templates/index.html`. After the line `const TAB_COLORS = [...];` (line 2045) and before the `// ═══════════════════════════════════════════════════` separator that introduces TAB MANAGER (line 2047), insert the following block:

```js

// ═══════════════════════════════════════════════════
// TAB ORGANIZER — classification helper
// ═══════════════════════════════════════════════════
// classifyTabForOrganize: pure function. Given a tab's display name and its
// rawBE array, return a classification:
//   { kind: 'survey' }
//   { kind: 'element', symbol: 'C' }
//   { kind: 'other' }
// Priority: filename regex first; BE-range fallback if filename doesn't match.
function classifyTabForOrganize(name, rawBE) {
  const raw = String(name || '').trim();

  // Survey by filename — case-insensitive, allows "XPS Survey", "Survey_0", etc.
  if (/survey/i.test(raw)) return { kind: 'survey' };

  // Element + orbital from filename. Use XPS_ELEMENTS keys as the valid set.
  // Sort longest-first so 'Cl' is tried before 'C' (and 'Ca' before 'C').
  const symbols = Object.keys(XPS_ELEMENTS).sort((a, b) => b.length - a.length);
  const orbital = '(?:1s|2[sp]|3[spd]|4[spdf]|5[spdf]|6[spdf])';

  for (const sym of symbols) {
    // Element symbol must sit at a word boundary on the left so 'Cu' doesn't
    // match inside 'Curium'; orbital immediately or after optional [ _-] sep.
    const re = new RegExp(
      '(?:^|[^A-Za-z])' + sym + '\\s*[_\\-]?\\s*' + orbital + '\\b',
      'i'
    );
    if (re.test(raw)) return { kind: 'element', symbol: sym };
  }

  // BE-range fallback
  const be = Array.isArray(rawBE) ? rawBE : [];
  if (be.length >= 2) {
    const beMax = be[0];
    const beMin = be[be.length - 1];
    const range = beMax - beMin;
    if (range > 1000) return { kind: 'survey' };

    // Find element peaks whose BE falls inside this window; pick the one
    // closest to window center.
    const center = (beMax + beMin) / 2;
    let best = null;
    let bestDist = Infinity;
    for (const sym of symbols) {
      const lines = XPS_ELEMENTS[sym].lines || {};
      for (const orb in lines) {
        const lineBE = lines[orb];
        if (lineBE >= beMin && lineBE <= beMax) {
          const d = Math.abs(lineBE - center);
          if (d < bestDist) { bestDist = d; best = sym; }
        }
      }
    }
    if (best) return { kind: 'element', symbol: best };
  }

  return { kind: 'other' };
}

// Console test harness — call `__testClassifyTab()` in browser devtools to run.
function __testClassifyTab() {
  const cases = [
    // [name, rawBE_min, rawBE_max, expectedKind, expectedSymbol]
    ['C1s Scan',       280, 295, 'element', 'C'],
    ['C 1s',           280, 295, 'element', 'C'],
    ['c1s_scan',       280, 295, 'element', 'C'],
    ['C1s Scan_0',     280, 295, 'element', 'C'],
    ['Au4f7/2',         80,  95, 'element', 'Au'],
    ['Cl2p',           195, 205, 'element', 'Cl'],
    ['Ca2p',           340, 360, 'element', 'Ca'],
    ['XPS Survey',       0,1200, 'survey',  null],
    ['Survey',           0,1200, 'survey',  null],
    ['Survey_0',         0,1200, 'survey',  null],
    ['random_name',      0,1300, 'survey',  null],   // BE-range fallback
    ['untitled.csv',   280, 295, 'element', 'C'],     // filename no match → BE
    ['weird_thing',      5,  10, 'other',   null],
    ['',               280, 295, 'element', 'C'],
  ];
  let pass = 0, fail = 0;
  for (const [name, lo, hi, ek, es] of cases) {
    // Build a descending-BE array (matches createTab convention)
    const be = [hi, (hi + lo) / 2, lo];
    const got = classifyTabForOrganize(name, be);
    const ok = got.kind === ek && (got.symbol || null) === es;
    if (ok) { pass++; }
    else { fail++; console.error('FAIL', { name, lo, hi, expected: { kind: ek, symbol: es }, got }); }
  }
  console.log(`classifyTabForOrganize: ${pass} pass, ${fail} fail`);
  return { pass, fail };
}
```

- [ ] **Step 2: Run the dev server and verify the harness passes**

Run the Flask app and open the page in a browser. In devtools console, run:

```js
__testClassifyTab()
```

Expected output:
```
classifyTabForOrganize: 14 pass, 0 fail
{ pass: 14, fail: 0 }
```

If any case fails, fix the regex / fallback logic before moving on. Common causes:
- Symbol-precedence (Cl matching as C) — verify longest-first sort
- BE-fallback picking wrong element — verify "closest to center" tie-break
- Empty `name` falling through wrong path — verify regex tolerates empty string

- [ ] **Step 3: Commit**

```bash
git add templates/index.html
git commit -m "feat(ui): add classifyTabForOrganize helper + console test harness"
```

---

### Task 2: Add `organizeTabs()` action

**Files:**
- Modify: `templates/index.html` — add `organizeTabs()` as a top-level function. Insert location: immediately after the `__testClassifyTab` block from Task 1 (keeps the organizer code colocated).

**Step 1: Insert `organizeTabs`**

- [ ] After `__testClassifyTab() { ... }` from Task 1, insert:

```js

// organizeTabs: reorder tabManager.tabs in place so groups cluster together.
// Group ordering: surveys first, then elements alphabetical by symbol, then
// 'other' last. Within each group, preserve original relative order (stable).
// Active tab remains active (its id is stable; only the array index changes).
function organizeTabs() {
  const tm = tabManager;
  if (!tm || !Array.isArray(tm.tabs) || tm.tabs.length < 2) return;

  const annotated = tm.tabs.map((tab, origIdx) => ({
    tab, origIdx,
    cls: classifyTabForOrganize(tab.name, tab.rawBE),
  }));

  const groupRank = (cls) => {
    if (cls.kind === 'survey')  return 0;
    if (cls.kind === 'element') return 1;
    return 2;
  };

  annotated.sort((a, b) => {
    const ra = groupRank(a.cls), rb = groupRank(b.cls);
    if (ra !== rb) return ra - rb;
    if (a.cls.kind === 'element' && b.cls.kind === 'element') {
      const sa = a.cls.symbol, sb = b.cls.symbol;
      if (sa !== sb) return sa < sb ? -1 : 1;
    }
    return a.origIdx - b.origIdx;
  });

  tm.tabs = annotated.map(a => a.tab);
  tm.renderTabBar();
  if (typeof tm._updateSurveyPanel === 'function') tm._updateSurveyPanel();

  // Best-effort: scroll the active tab into view after reorder.
  try {
    const bar = document.getElementById('spectrum-tab-bar');
    if (bar && tm.activeId) {
      const activeEl = bar.querySelector('[data-tab-id="' + tm.activeId + '"]');
      if (activeEl && typeof activeEl.scrollIntoView === 'function') {
        activeEl.scrollIntoView({ block: 'nearest', inline: 'nearest' });
      }
    }
  } catch (_) { /* non-fatal */ }
}
```

**Note on the `data-tab-id` selector:** the scroll-into-view code assumes `renderTabBar` writes a `data-tab-id` attribute on each tab element. Verify this against the actual rendering code at `templates/index.html:2332-2423` before relying on the selector. If the attribute is named differently (e.g. `data-id`, or no attribute at all), update the selector accordingly — or if no per-tab id exists in the DOM, drop the scroll-into-view block entirely. This is a polish item, not a feature requirement.

- [ ] **Step 2: Manual smoke test in browser console**

Reload the page, load a folder of spectra (or `loadDemo('U4f')` then `loadDemo('Fe2p')` then `loadDemo('C1s')`) so multiple tabs exist. In console:

```js
tabManager.tabs.map(t => t.name)   // record order before
organizeTabs()
tabManager.tabs.map(t => t.name)   // verify new order
tabManager.activeId                 // should be unchanged
```

Expected: Surveys (if any) cluster first, then elements alphabetical by symbol, Other last. Active tab id unchanged.

- [ ] **Step 3: Commit**

```bash
git add templates/index.html
git commit -m "feat(ui): add organizeTabs() to cluster same-element tabs"
```

---

### Task 3: Add the toolbar button

**Files:**
- Modify: `templates/index.html:1613` — insert one new line after the `Overlay` button, before the flex spacer at line 1614.

**Step 1: Add the button markup**

- [ ] Open `templates/index.html`. Find the toolbar block (line 1608 `<div id="chart-toolbar">`). After this line:

```html
        <button class="btn btn-sm" id="btn-overlay" onclick="toggleOverlayMode()" title="Overlay multiple spectra">Overlay</button>
```

insert directly below it:

```html
        <button class="btn btn-sm" id="btn-organize-tabs" onclick="organizeTabs()" title="Reorder tabs so same-element spectra are adjacent (Surveys → elements alphabetical → Other)">Organize Tabs</button>
```

Resulting toolbar fragment (lines 1611–1615 after edit):

```html
        <button class="btn btn-sm" id="btn-add-peak" onclick="togglePlaceMode('peak')">+ Add Peak</button>
        <button class="btn btn-sm" id="btn-add-multiplet" onclick="_onMultipletBtnClick()">+ Multiplet Pair</button>
        <button class="btn btn-sm" id="btn-overlay" onclick="toggleOverlayMode()" title="Overlay multiple spectra">Overlay</button>
        <button class="btn btn-sm" id="btn-organize-tabs" onclick="organizeTabs()" title="Reorder tabs so same-element spectra are adjacent (Surveys → elements alphabetical → Other)">Organize Tabs</button>
        <div style="flex:1"></div>
```

**Styling:** No new CSS. Reuses `.btn .btn-sm` (already defined at `templates/index.html:172-185` and `:222`), so the new button automatically inherits `font-family: var(--sans)`, `font-size: 10px`, `padding: 3px 8px`, `border-radius: var(--radius)` (6px), border + background using the same design tokens, and the hover state (`background: var(--bg4); border-color: var(--accent); color: var(--accent2);`). Height, padding, font, color, and hover all match its left-side neighbors (`+ Add Peak`, `+ Multiplet Pair`, `Overlay`) exactly because they share the class.

**Press feedback:** the existing `.btn { transition: all 0.15s; }` provides a subtle color-shift on click via the `:hover`/`:active` flow; no extra CSS needed. If the user later wants a stronger "pressed" flash, it can be added as a single rule (out of scope here).

- [ ] **Step 2: Run the dev server and click the button**

Start the Flask app, load a folder with mixed tabs (Survey, C1s, O1s, U4f, etc., scattered). Click "Organize Tabs". Expected:
- Tabs visibly reorder: Surveys leftmost, then C, O, U (alphabetical), Other rightmost.
- The active tab remains highlighted (chrome unchanged); its position may have shifted.
- No console errors.
- Visual: button sits between Overlay and the flex spacer; height/padding/font match `+ Add Peak`; hover background lightens identically.

- [ ] **Step 3: Commit**

```bash
git add templates/index.html
git commit -m "feat(ui): add 'Organize Tabs' toolbar button"
```

---

### Task 4: Fix `_loadProjectJSON` so saved order roundtrips

**Files:**
- Modify: `templates/index.html:7151-7155`

The save code preserves order (`data.tabs = tabs.map(buildTabData)` — line 6953), but the load code re-sorts on insertion:

```js
  // Insert surveys at front, others at back (same as createTab)
  for (const tab of newTabs) {
    if (tab.isSurvey) tabManager.tabs.unshift(tab);
    else tabManager.tabs.push(tab);
  }
```

After our Organize Tabs feature, this would scramble a deliberately-organized order on every save/load cycle. The fix is to trust the saved array order.

**Step 1: Replace the survey-front insertion with a plain append**

- [ ] At `templates/index.html:7151-7155`, replace:

```js
  // Insert surveys at front, others at back (same as createTab)
  for (const tab of newTabs) {
    if (tab.isSurvey) tabManager.tabs.unshift(tab);
    else tabManager.tabs.push(tab);
  }
```

with:

```js
  // Preserve the saved tab order verbatim. (Fresh folder loads still use the
  // surveys-front convention via createTab; this path is only for saved
  // projects whose order the user has already chosen.)
  for (const tab of newTabs) {
    tabManager.tabs.push(tab);
  }
```

- [ ] **Step 2: Roundtrip verification in browser**

1. Load demo data via `loadDemo('C1s'); loadDemo('U4f'); loadDemo('Fe2p')` in the console (or load a real folder).
2. Click "Organize Tabs". Note the new order, e.g. `[C 1s, Fe 2p, U 4f]`.
3. Use the Save Project UI to save a `.proj.json` (or `.proj.zip` if ≥5 tabs).
4. Reload the page (fresh state).
5. Load the saved file via the Load UI.
6. Expected: tabs appear in the same organized order `[C 1s, Fe 2p, U 4f]`, NOT re-sorted with surveys first.

- [ ] **Step 3: Backward-compatibility sanity check**

Load any pre-existing `.proj.json` (one saved before this change). Verify tabs load in the order they were saved (which for old projects is whatever order existed at save time). Surveys may no longer "float to the top" automatically on load — this is the intended behavior change.

- [ ] **Step 4: Commit**

```bash
git add templates/index.html
git commit -m "fix(ui): preserve saved tab order on project load (was re-sorting surveys to front)"
```

---

### Task 5: Final browser verification + adjacent-issue note

This is verification only, no code changes.

**Step 1: Full browser verification checklist**

- [ ] Start the dev server. Open the app in a fresh browser tab.
- [ ] **Empty state:** With zero tabs loaded, click "Organize Tabs". Expected: no error, no visible change (the function returns early when `tabs.length < 2`).
- [ ] **Single tab:** Load one spectrum (e.g. `loadDemo('C1s')`). Click "Organize Tabs". Expected: no error, no visible change.
- [ ] **Two tabs same element:** Load `C1s` twice (e.g. demo + a real `C 1s` CSV). Click "Organize Tabs". Expected: tabs stay adjacent (already are), order stable.
- [ ] **Mixed demo set:** Run `loadDemo('U4f'); loadDemo('C1s'); loadDemo('Fe2p')`. Click "Organize Tabs". Expected: order becomes `[C 1s, Fe 2p, U 4f]` (alphabetical: C → Fe → U).
- [ ] **Survey + mixed:** Load a real folder containing an `XPS Survey.csv`, `C1s Scan.csv`, `Cl2p Scan.csv`, `U4f Scan.csv` in scrambled filesystem order. Click "Organize Tabs". Expected order: `[XPS Survey, C1s Scan, Cl2p Scan, U4f Scan]` (survey first, then C before Cl before U alphabetically).
- [ ] **Cl vs C disambiguation:** Verify `Cl2p` is grouped under Cl, not C. Examine `tabManager.tabs.map(t => classifyTabForOrganize(t.name, t.rawBE))` in console.
- [ ] **Active tab preservation:** Activate a non-first tab (e.g. click a U4f tab). Run `tabManager.activeId`. Click Organize Tabs. Confirm `tabManager.activeId` is unchanged and the same tab is still visually highlighted as active.
- [ ] **Charge correction / peaks intact:** On the active tab post-organize, verify `state.peaks` still points to the same data (the active tab's peak list should be unchanged in the Peaks panel).
- [ ] **Hover/active states match neighbors:** Hover Organize Tabs and `+ Add Peak`. Confirm identical background-color and border-color transitions. Click each; confirm momentary press feel matches.
- [ ] **Existing drag-and-drop still works:** Drag one tab past another. Verify the existing DnD reordering (lines 2376–2417) is unaffected.
- [ ] **Save/load roundtrip (small project, .proj.json):** Organize, save, reload page, load. Order is preserved.
- [ ] **Save/load roundtrip (large project, .proj.zip):** With ≥5 tabs: organize, save, reload, load. Order is preserved (ZIP path goes through `_loadProjectJSON` so inherits the Task 4 fix).
- [ ] **No console errors** at any step.

**Step 2: Adjacent-issue note for PR description**

When opening the PR, mention this pre-existing bug (out of scope here, do NOT fix in this commit):

> Noticed during implementation: `_doSaveProject` records `meta.activeId` (line 6949) but `_loadProjectJSON` ignores it and unconditionally activates the first new tab (line 7157). After loading a saved project, the active tab is reset rather than restored. Worth a follow-up.

**Step 3: No commit for this task** (verification + note only).

---

## Self-Review

- **Spec coverage:** Organize button (Task 3 ✓), in-place reorder (Task 2 ✓), active tab stays active (Task 2: uses stable id ✓), no confirmation dialog (Task 2: instant ✓), filename regex (Task 1 ✓), BE-range fallback >1000 = Survey (Task 1 ✓), BE-range fallback element by lookup (Task 1 ✓), Other fallback (Task 1 ✓), survey first / element alpha / other last (Task 2 ✓), stable within-group (Task 2 ✓), persistence via existing tab order (Task 4 fix ensures save/load roundtrip ✓), no schema change (no new fields in `.proj.json` ✓).
- **Placeholder scan:** no TBDs, no "implement later", no "similar to Task N", no abstract "handle edge cases" — all code is concrete.
- **Type consistency:** classifier returns `{kind: 'survey'|'element'|'other', symbol?}` consistently across Task 1 helper, Task 1 test harness, and Task 2 consumer.
- **Scope guard:** all edits inside `templates/index.html`; no backend file is touched; no new dependency.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-11-organize-tabs-button.md`.

**STOPPING HERE per your instructions — do not execute yet. Awaiting your review.**

When ready to proceed, two execution options:

**1. Subagent-Driven (recommended)** — fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — execute tasks in this session with checkpoints for review.
