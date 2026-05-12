# Spectrum Stacking — Design Memo

**Branch:** `spectrum-stacking`
**Date opened:** 2026-05-11
**Status:** Session 1 in planning — implementation pending Skye's approval.

This memo captures the conceptual design and decisions for the multi-session "spectrum stack" feature. The session-by-session implementation plans are separate artifacts; the very first one (session 1) will be reviewed and approved alongside this memo.

---

## Goal

Add a new kind of tab — a **stack tab** — that holds a collection of references to existing spectrum tabs and displays them as multiple traces on shared axes. Stack tabs are **viewer-only**: no peak operations, no fitting. They are the entry point for comparison-style workflows that XPS analysts currently can't do without external tooling.

A stack tab is a *view* over spectra that live in regular spectrum tabs. It does not own spectrum data; it holds references plus per-entry display metadata.

---

## Multi-session roadmap

| Session | Scope |
|---|---|
| **1 (today)** | Remove existing Overlay feature. Add stack-tab type, ▦ tab styling, "+ Stack" button, "Add Spectrum to Stack" dropdown, overlay-mode rendering, legend right-panel, peak-controls hiding, lifecycle (source-close auto-removal, Organize Tabs block). Session-only (no persistence). |
| 2 | Stacked-offset render mode (vertical separation). Mode toggle between overlay and offset in legend or chart-toolbar. |
| 3 | Persistence — either embed stacks in `.proj.json` or introduce `.stack.json`. Decision deferred until session 1's data model is in use and we know the shape we want to serialize. |
| 4 | Peak rendering from `.fit.json` / saved fits over stacked spectra. |
| (later) | Per-spectrum opacity / color customization UI, drag-and-drop to add to stack, file-picker to load spectra directly into a stack. |

Sessions 2–4 are not blocking and can be reordered based on feedback after session 1 ships locally.

---

## Session 1 scope summary

**In:**
- Remove the existing Overlay feature (button, state, toggle function, tab-strip checkboxes, plot integration, CSS) — it's superseded.
- Stack tab type with `▦` glyph label and distinguishing background tint.
- `+ Stack` toolbar button (replaces the slot vacated by Overlay).
- `Add Spectrum to Stack` toolbar button visible only when a stack tab is active; opens a dropdown of open spectrum tabs.
- Overlay rendering: each visible stack entry as a solid line in its assigned Wong-palette color, shared X/Y auto-fit.
- Legend right-side panel replaces Peaks/Results/Quantify/Survey when a stack tab is active.
- Empty-state DOM message in the chart area when stack tab has no entries.
- Auto-remove stack entries when a referenced source tab is closed (with toast).
- Organize Tabs moves stack tabs as a block to the end of the strip.
- Hide (not disable) peak/fit toolbar controls when a stack tab is active.
- Session-only state — no persistence; stacks evaporate on reload.

**Out (session 1 — explicitly deferred):**
- Stacked-offset mode (session 2).
- Save/load — `.proj.json` or `.stack.json` (session 3).
- Peak rendering from `.fit.json` in stack view (session 4).
- Drag-and-drop to add spectra to stack.
- Per-spectrum opacity/color customization UI.
- File picker to load spectra directly into a stack.
- New rename code for stack tabs — if the existing tab rename UI (if any) works generically, fine; otherwise skip.

---

## Design decisions

These eight decisions are the user's calls; recorded here for permanence.

### 1. Source reference, not copy
A stack entry holds `{ sourceTabId, color, visible }` only. Spectrum data (`rawBE`, `rawIntensity`, `ccShift`) is read live from the source tab at render time.

**Why:** Avoids data duplication and staleness. Editing charge correction on a source tab is reflected immediately in any stack that references it. Cost: a stack entry pointing at a closed tab is invalid — handled by decision 3.

### 2. Charge correction is live
Each entry's binding-energy axis is computed at render time as `source.rawBE - source.ccShift`. No frozen copy of CC.

**Why:** Consistent with decision 1. The "charge correction value" shown in the legend entry is the *current* `ccShift` of the source tab, not a captured snapshot.

### 3. Source-tab close auto-removes the stack entry
When `tabManager.closeTab(id)` removes a spectrum tab, every stack tab is scanned. Any entry whose `sourceTabId === id` is removed. A toast notification announces each removal:

> Removed "{spectrum name}" from "{stack name}" (source tab closed).

**Why:** Avoids dangling references and broken render paths. Toast keeps the user informed rather than silently mutating their stacks.

### 4. Organize Tabs treats stack tabs as a block at the end
`organizeTabs()` (the function added today for spectrum-tab grouping) is extended: all stack tabs collect to the right end of the tab strip, preserving their relative order among themselves. Spectrum tabs still sort by Survey → element-alpha → Other within their region of the strip.

**Why:** Stack tabs are conceptually a "second class" of tab; segregating them visually matches their behaviour difference. Preserving relative order respects user intent in arranging multiple stacks.

### 5. Empty stack = DOM message, no chart
When a stack tab is active and has no entries, the Chart.js canvas is hidden and a centered `<div>` message is shown in the chart area:

> Empty stack. Click "Add Spectrum to Stack" to add a spectrum from your open tabs.

**Why:** Avoids a misleading empty chart with axis ticks and an empty plot area. The DOM message is unambiguous and points the user at the next action.

### 6. Legend entry contents
Each legend row (one per stack entry) shows:
- Small color swatch (8 px circle) in the entry's assigned color
- Spectrum name (read from source tab — reflects renames if any)
- Current charge correction: `ΔCC: ±N.NN eV` (or `ΔCC: 0 eV` if zero)
- Visibility toggle (checkbox)
- Remove (×) button

**Why:** Surfaces all per-entry state without a separate properties panel. Charge correction is shown because it determines where the trace sits on the BE axis and the user needs to see it to interpret the stack.

### 7. Peak/fit controls hidden when a stack tab is active
The following are display:none (not disabled) while a stack tab is active:
`+ Add Peak`, `+ Multiplet Pair`, `Run Fit`, `Batch Fit`, fit-method dropdown (with its label).

Visible: file loading inputs, zoom controls, `History`, `Lookup`, `Actions`, `Undo`/`Redo`, `⇅ Organize Tabs`, `+ Stack`, and the new `Add Spectrum to Stack` button.

**Why:** Disable-styled buttons in a "wrong context" mode are noisy and confusing. Hiding signals "this surface doesn't apply here" cleanly. Switching back to a spectrum tab restores them.

### 8. Stack tab label: `▦ Stack N`
The tab's `name` field is literally `"▦ Stack 1"`, `"▦ Stack 2"`, …. The ▦ glyph (U+25A6 SQUARE WITH HORIZONTAL FILL) prefixes the name, separated by one space.

**Why:** Same pattern as the `⇅` glyph on the Organize Tabs button — gives a quick visual classifier for "this is a stack" without changing the tab structure. Reading the tab strip, the eye picks out stacks instantly.

---

## Architecture

### Data model

Stack tabs are stored in `tabManager.tabs` alongside spectrum tabs (single source of truth — no separate array). The two types are distinguished by an `isStack: true` flag on the tab object.

```js
// Spectrum tab (existing, unchanged):
{ id, name, color, isSurvey, rawBE, rawIntensity, ccShift, peaks, ... }

// Stack tab (new):
{
  id,                // 'tab_' + random9 (same convention)
  name,              // '▦ Stack 1'
  isStack: true,
  entries: [         // ordered list
    { sourceTabId, color, visible }
  ],
  _nextColorIdx,     // for cycling Wong palette on add
  // Inert fields kept for compatibility with existing tab lifecycle:
  rawBE: [], rawIntensity: [], peaks: [], nextId: 1,
  fitResult: null, ccShift: 0, markedElements: [], notes: '',
  ui: { /* same shape as spectrum tab, unused */ }
}
```

The inert fields exist because functions like `activateTab`, `_syncActiveToRecord`, `_doSaveProject.buildTabData` iterate or read tab properties. Setting them to empty/default values makes a stack tab traverse the same code paths without crashing. Where behaviour must differ (rendering, right panel, save serialization), an `if (tab.isStack)` branch handles it.

### Render path

`updatePlot()` is the single entry point. At its top, after resolving the active tab:

- If active tab is a spectrum tab: existing code path (unchanged).
- If active tab is a stack tab:
  - Compute datasets from `tab.entries.filter(e => e.visible).map(e => lookup source tab + build dataset)`.
  - Skip all peak/envelope/residual logic.
  - If `entries.length === 0` (or all hidden), hide the canvas and show the empty-state `<div>`; skip Chart.js entirely.
  - Otherwise render a Chart.js line chart with one dataset per visible entry, solid lines in the entry's assigned Wong color, no peak overlays.

### Right-panel switching

The right panel today has four sub-tabs (Peaks/Results/Quantify/Survey) and their panel divs. Add a fifth panel (`#tab-stack-legend`) that is hidden by default. When activating a stack tab:
- Hide the four existing sub-tab buttons (`.panel-body > .tabs > .tab`).
- Hide the four existing panels (`.panel-body > .tab-panel`).
- Show `#tab-stack-legend` and render its contents from `tab.entries`.
- Update the panel-header text from "Peaks & Results" to "Stack Legend".

When activating any other tab type, reverse this.

### Peak-control hiding

Add a class `.peak-fit-control` to each peak/fit element:
- `#btn-add-peak`, `#btn-add-multiplet`
- `Run Fit` button, `Batch Fit` button (give them IDs in the process)
- Fit-method dropdown wrapper (the `<div class="hselect-wrap">` containing the `<select>` and its label)

CSS rule:
```css
body.stack-tab-active .peak-fit-control { display: none !important; }
```

Toggle `body.stack-tab-active` class based on the active tab type. Single point of control.

### Lifecycle hooks

- `tabManager.closeTab(id)` — extend to scan all stack tabs and remove invalidated entries (post-removal, after the spectrum tab is gone from `this.tabs`).
- `organizeTabs()` — extend to segregate stack tabs to the end as a block.
- `_doSaveProject.buildTabData` — skip stack tabs entirely (filter them out of the tabs array before serialization). This is a defensive guard so existing save/load works; stack persistence is session 3 scope.

---

## Risks & open questions

| Risk | Mitigation |
|---|---|
| `activateTab` swaps `state.rawBE` etc. — for a stack tab, this resets state to empty. Could break code that reads `state.peaks` post-activation. | Stack tab's inert fields are empty arrays / null. `renderPeakList` on empty peaks just shows the empty-state message — harmless. `updatePlot` branches on `isStack` early and ignores state for stack tabs. |
| `_syncActiveToRecord` (called when switching off any tab) reads form fields and writes them to `tab.ui`. On a stack tab, form fields hold whatever defaults — could write nonsense back. | Add an early-return guard: `if (currentTab.isStack) return;` Stack tabs have no UI to sync. |
| `_doSaveProject` would call `buildTabData` on a stack tab and serialize garbage (or crash). | Filter `tabs.filter(t => !t.isStack)` before mapping in `buildTabData`. Session 3 will revisit. |
| `_updateSurveyPanel` iterates tabs looking for surveys. Stack tabs lack `isSurvey`. | Harmless — falsy `isSurvey` filters them out naturally. |
| `_loadProjectJSON` reconstructs tabs from saved data, none of which have `isStack: true`. | Loaded tabs become regular spectrum tabs — no change. Stack persistence (when added in session 3) will need a new field on the saved record. |
| Closing the LAST tab while it's a stack tab → `closeTab` empty-state handler resets `state`. | Already handled by existing empty-state path in `closeTab` lines 2292–2311. |
| Stack tab renamed via existing rename code (if any) — would still display ▦ prefix if user kept it; would lose ▦ semantics if user wipes it. | Acceptable — user choice. Out of scope to enforce. |

### Adjacent issues observed but not fixed in session 1
- `_doSaveProject` writes `meta.activeId` but `_loadProjectJSON` ignores it and always activates the first tab (flagged in earlier Organize Tabs work). Still unfixed.
- CLAUDE.md states the frontend is `xps-fitting-tool.html`. The actual frontend is `templates/index.html`. Should be corrected in a separate doc-hygiene commit.

---

## End-of-session-1 demo (the success criterion)

After session 1, this end-to-end flow should work in a browser:

1. Load three spectrum tabs (e.g. demo C1s, U4f, Fe2p).
2. Click **+ Stack** → a new tab `▦ Stack 1` appears, becomes active, chart area shows "Empty stack" message, right panel shows "Stack Legend" (empty).
3. Click **Add Spectrum to Stack** → dropdown shows "C 1s, U4f, Fe2p" → pick C1s. Chart renders one solid trace in the first Wong color (#E69F00). Legend gets a row with swatch, name, "ΔCC: 0 eV", visible-check, X.
4. Add the other two. Three traces in three distinct Wong colors. Legend has three rows.
5. Switch to the C1s spectrum tab, change its charge correction (e.g. shift by +0.5 eV). Switch back to ▦ Stack 1 → that trace has moved on the BE axis; legend row shows updated `ΔCC`.
6. In the legend, uncheck the U4f row → that trace disappears, others remain.
7. Click the × on the Fe2p row → entry gone, trace gone, legend has two rows.
8. Click **⇅ Organize Tabs** → spectrum tabs cluster by element, ▦ Stack 1 moves to the end. Create a ▦ Stack 2 (right next to Stack 1). Organize again → both stacks stay together at the end.
9. Switch to the C1s spectrum tab → right panel reverts to Peaks/Results/Quantify; chart shows the single C1s spectrum with any peaks; `+ Add Peak`, `Run Fit`, etc. are visible. Switch back to a stack → those controls disappear.
10. Close the U4f spectrum tab while it's referenced in ▦ Stack 1 → toast: `Removed "U4f Scan" from "▦ Stack 1" (source tab closed).` Legend row gone.
11. Reload the page → no stacks (session-only).
12. Save & reload a `.proj.json` (with spectrum tabs only) → loads cleanly, no errors from the buildTabData guard.

If all 12 steps pass, session 1 is done.

---

*Implementation plan for session 1 is reviewed alongside this memo. Sessions 2–4 will get their own design notes appended here as they're scoped.*
