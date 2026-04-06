# XPS Fitting Studio UI Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Modernize the XPS Fitting Studio UI with consistent typography, glassmorphism effects, pill toggles, collapsible peak cards, onboarding empty state, and polished interactions — without touching any data pipeline, parsing, fitting, or backend communication code.

**Architecture:** All changes are CSS-only or display-related JS in the single-file `templates/index.html`. The file is ~6487 lines. CSS lives in lines 11-1047, HTML structure in lines 1048-1337, JS from line 1340 onward. No new files are created. Changes must work in both dark (`body`) and light (`body.light-theme`) modes.

**Tech Stack:** HTML/CSS/JS (vanilla), Chart.js 4.4, CSS `backdrop-filter` for glassmorphism, CSS custom properties for theming.

**CRITICAL CONSTRAINT:** Do NOT modify any of these functions or their internal logic: `loadFile`, `_loadOneFile`, `_filterFiles`, `parseCSV`, `parseXLSX`, `handleDrop`, `handleDragOver`, `runFit`, `peakToBackendSpec`, `uploadToBackend`, `computeBackground`, `getROIData`, `getCorrectedBE`, `updateChargeCorrection`, `updatePeakParam`, `applyParams` (inside runFit), VGD parsing, or any `fetch()` calls. Only modify CSS, HTML templates, and display-rendering JS (e.g., `renderPeakList`, `renderPeakForm`, `renderEmptyChart`, `clearAllPeaks` prompt, `toggleSaveMenu` dropdown items, status bar display, chart toolbar checkboxes).

---

## File Structure

**Only one file is modified:**
- Modify: `templates/index.html` (all 20 items are CSS, HTML, or display-JS changes within this file)

**No new files are created.** All changes live in the single-file HTML app.

---

## Task 1: Typography — System Font Stack and Consistent Sizing

**Files:**
- Modify: `templates/index.html:11-50` (CSS variables and body)
- Modify: `templates/index.html:68-74` (header h1)
- Modify: `templates/index.html:144-157` (panel-header)
- Modify: `templates/index.html:207-222` (form elements)
- Modify: `templates/index.html:245-256` (section-head)

This task covers items 1-6 from the spec: consistent sans-serif font family, uppercase section headers, consistent label sizing, monospace only for numerical values, and button font cleanup.

- [ ] **Step 1: Replace the Google Fonts import and CSS font variables**

Remove the Google Fonts `@import` on line 12 and update the two font variables in `:root` (lines 39-40):

```css
/* REMOVE this line entirely: */
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500&display=swap');

/* UPDATE these two variables in :root: */
--mono: 'SF Mono', 'Fira Code', 'Cascadia Code', 'Consolas', monospace;
--sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
```

- [ ] **Step 2: Update section headers for consistent uppercase scientific look**

Update `.section-head` (line 245) to use the sans-serif font with uppercase letter-spacing:

```css
.section-head {
  padding: 6px 10px;
  background: var(--bg3);
  font-family: var(--sans);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text2);
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  user-select: none;
  transition: background 0.12s, color 0.12s;
}
```

Update `.panel-header` (line 144) to match. It already has uppercase + letter-spacing, just switch from `--mono` to `--sans`:

```css
.panel-header {
  font-family: var(--sans);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text3);
  padding: 10px 14px 8px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}
```

- [ ] **Step 3: Make form labels consistent**

Update the global `label` rule (line 208) to use sans-serif explicitly:

```css
label { font-family: var(--sans); font-size: 11px; font-weight: 500; color: var(--text2); display: block; margin-bottom: 4px; }
```

- [ ] **Step 4: Keep monospace only for numerical inputs**

The input/select rule (line 209) already uses `--mono`. This is correct because inputs contain numerical values. No change needed.

Update `.btn` (line 166) to use `--sans` instead of `--mono`:

```css
.btn {
  font-family: var(--sans);
  font-size: 11px;
  font-weight: 500;
  /* rest unchanged */
}
```

Update `#header h1` (line 68) from `--mono` to `--sans` with slightly bolder weight:

```css
#header h1 {
  font-family: var(--sans);
  font-size: 14px;
  font-weight: 600;
  color: var(--accent2);
  letter-spacing: 0.05em;
}
```

- [ ] **Step 5: Verify both themes render correctly**

Visually check that the font changes work in both dark and light modes. The variables flow through CSS custom properties, so both themes should inherit automatically.

- [ ] **Step 6: Commit**

```bash
git add templates/index.html
git commit -m "feat(ui): consistent system font stack, uppercase section headers, sans-serif buttons"
```

---

## Task 2: Pill Toggle Buttons for Display Options

**Files:**
- Modify: `templates/index.html:~935-950` (add new CSS for pill toggles)
- Modify: `templates/index.html:1237-1252` (chart toolbar HTML)
- Modify: `templates/index.html` JS: `updatePlot` reads checkbox state — we must preserve the same IDs and `.checked` behavior

This covers item 7: replace display toggle checkboxes with compact pill-shaped toggle buttons.

- [ ] **Step 1: Add pill toggle CSS**

Add after the `.tools-chk-row` rules (around line 947), before the uncertainty warnings:

```css
/* ── Pill toggle buttons ─────────────────────────── */
.pill-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0;
  padding: 3px 10px;
  border-radius: 999px;
  font-family: var(--sans);
  font-size: 10px;
  font-weight: 500;
  color: var(--text3);
  background: transparent;
  border: 1px solid var(--border);
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
  white-space: nowrap;
}
.pill-toggle:hover {
  border-color: var(--text2);
  color: var(--text2);
}
.pill-toggle.active {
  background: var(--accent-dim);
  border-color: var(--accent);
  color: var(--accent2);
}
.pill-toggle input[type="checkbox"] {
  display: none;
}
```

- [ ] **Step 2: Replace checkbox HTML in chart toolbar with pill toggles**

Replace lines 1237-1252 (the four `<label>` checkbox elements) with:

```html
<label class="pill-toggle active">
  <input type="checkbox" id="show-individual" checked onchange="this.parentElement.classList.toggle('active',this.checked);updatePlot()">
  Individual peaks
</label>
<label class="pill-toggle active">
  <input type="checkbox" id="show-fill" checked onchange="this.parentElement.classList.toggle('active',this.checked);updatePlot()">
  Fill peaks
</label>
<label class="pill-toggle active">
  <input type="checkbox" id="show-residuals" checked onchange="this.parentElement.classList.toggle('active',this.checked);updatePlot()">
  Residuals
</label>
<label class="pill-toggle active">
  <input type="checkbox" id="invert-be" checked onchange="this.parentElement.classList.toggle('active',this.checked);updatePlot()">
  Invert BE
</label>
```

The `<input>` IDs and `checked` property are preserved so `updatePlot()` reads them identically. The `onchange` also toggles the parent `.active` class for visual state.

- [ ] **Step 3: Verify updatePlot still reads the checkbox states**

No changes to `updatePlot` itself. It reads `document.getElementById('show-individual').checked` etc., which still works because the checkbox inputs are still in the DOM with the same IDs.

- [ ] **Step 4: Commit**

```bash
git add templates/index.html
git commit -m "feat(ui): pill-shaped toggle buttons for display options in chart toolbar"
```

---

## Task 3: Collapsible Peak Cards with Summary Grid

**Files:**
- Modify: `templates/index.html:339-372` (peak-item CSS)
- Modify: `templates/index.html:3324-3350` (renderPeakList function)

This covers items 8 and 18: redesign peak list as cards with color dot, name, 3-column summary (Center, FWHM, Area%), collapsible full editing, and color-coded left border.

- [ ] **Step 1: Update peak card CSS**

Replace the existing `.peak-item` through `.peak-body.open` block (lines 339-372) with:

```css
/* Peak list cards */
.peak-item {
  border: 1px solid var(--border);
  border-left: 3px solid var(--border);
  border-radius: var(--radius);
  margin-bottom: 8px;
  overflow: hidden;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.peak-item.selected { border-color: var(--accent); }
.peak-item:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
.peak-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 10px;
  background: var(--bg3);
  cursor: pointer;
}
.peak-color {
  width: 10px; height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.peak-name {
  font-family: var(--sans);
  font-size: 11px;
  font-weight: 600;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.peak-summary {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 2px 8px;
  padding: 4px 10px 6px;
  background: var(--bg3);
  border-top: 1px solid var(--border);
}
.peak-summary-label {
  font-family: var(--sans);
  font-size: 9px;
  font-weight: 500;
  color: var(--text3);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.peak-summary-val {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--text);
}
.peak-info {
  font-family: var(--mono);
  font-size: 10px;
  color: var(--text2);
}
.peak-body { padding: 10px; display: none; border-top: 1px solid var(--border); }
.peak-body.open { display: block; }
```

- [ ] **Step 2: Update renderPeakList to include summary grid and color-coded border**

Replace the `renderPeakList` function (lines 3324-3350) with:

```javascript
function renderPeakList() {
  const el = document.getElementById('peak-list');
  const empty = document.getElementById('peak-empty');
  el.innerHTML = '';
  empty.style.display = state.peaks.length ? 'none' : 'block';
  document.getElementById('sb-peaks').textContent = state.peaks.length;

  // Compute total area for percentage
  const totalArea = state.peaks.reduce((s, p) => s + (p._area || 0), 0);

  for (const p of state.peaks) {
    const item = document.createElement('div');
    item.className = 'peak-item';
    item.id = 'peak-item-' + p.id;
    item.style.borderLeftColor = p.color;
    const isLinked = !!p.linked;
    const areaPct = totalArea > 0 && p._area ? ((p._area / totalArea) * 100).toFixed(1) : '\u2014';

    item.innerHTML = `
      <div class="peak-header" onclick="togglePeakBody(${p.id})">
        <div class="peak-color" style="background:${p.color}"></div>
        <span class="peak-name">${p.name}${isLinked ? ' <span class="linked-badge">linked</span>' : ''}</span>
        <span class="peak-info">${p.center.toFixed(2)} eV</span>
        <button class="btn btn-icon btn-sm" style="margin-left:4px;color:var(--red)" onclick="event.stopPropagation();removePeak(${p.id})">&times;</button>
      </div>
      <div class="peak-summary" onclick="togglePeakBody(${p.id})" style="cursor:pointer">
        <span class="peak-summary-label">Center</span>
        <span class="peak-summary-label">FWHM</span>
        <span class="peak-summary-label">Area</span>
        <span class="peak-summary-val">${p.center.toFixed(2)}</span>
        <span class="peak-summary-val">${p.fwhm.toFixed(2)}</span>
        <span class="peak-summary-val">${areaPct}%</span>
      </div>
      <div class="peak-body" id="peak-body-${p.id}">
        ${renderPeakForm(p)}
      </div>
    `;
    el.appendChild(item);
  }
}
```

Note: `p._area` is set by the fitting result handler. If no fit has been run, it falls back to `\u2014` (em dash).

- [ ] **Step 3: Commit**

```bash
git add templates/index.html
git commit -m "feat(ui): collapsible peak cards with summary grid and color-coded left border"
```

---

## Task 4: Peak Card Hover Highlights Chart Peak

**Files:**
- Modify: `templates/index.html:3324-3350` (renderPeakList — add mouseenter/mouseleave)
- Modify: `templates/index.html` JS: small helper function for chart dataset highlighting

This covers item 19: hovering a peak card highlights the corresponding peak in the chart.

- [ ] **Step 1: Add hover event listeners to peak cards in renderPeakList**

After `el.appendChild(item)` in the loop, add:

```javascript
item.addEventListener('mouseenter', () => _highlightChartPeak(p.id, true));
item.addEventListener('mouseleave', () => _highlightChartPeak(p.id, false));
```

- [ ] **Step 2: Add _highlightChartPeak helper function**

Add this small helper near `renderPeakList` (after `togglePeakBody`):

```javascript
function _highlightChartPeak(peakId, highlight) {
  if (!state.chart) return;
  const datasets = state.chart.data.datasets;
  for (const ds of datasets) {
    if (ds._peakId === peakId) {
      ds.borderWidth = highlight ? 3 : 1.5;
      if (highlight) {
        ds._origBorderColor = ds._origBorderColor || ds.borderColor;
        // keep color, just widen
      }
    }
  }
  state.chart.update('none');
}
```

Note: This relies on `updatePlot` tagging each peak dataset with `_peakId`. We need to check whether `updatePlot` sets this. If not, we'll add `_peakId: p.id` when building peak datasets in `updatePlot`. This is display-only metadata on the Chart.js dataset object and does not touch data processing.

- [ ] **Step 3: Tag peak datasets in updatePlot with _peakId**

In `updatePlot`, where individual peak datasets are pushed (find the loop that builds peak datasets), add `_peakId: p.id` to each dataset config object. This is a display-only annotation — Chart.js ignores unknown properties.

Search for the line in `updatePlot` that creates peak datasets (around line 4200-4300 where it loops through `state.peaks`). Add `_peakId: p.id` to each dataset object.

- [ ] **Step 4: Commit**

```bash
git add templates/index.html
git commit -m "feat(ui): highlight chart peak on hover over peak card"
```

---

## Task 5: Move "Clear All" and Add Confirmation

**Files:**
- Modify: `templates/index.html:1282-1284` (right panel header — remove Clear all button)
- Modify: `templates/index.html:1294-1298` (peak-list area — add Clear all at bottom)
- Modify: `templates/index.html:3261-3267` (clearAllPeaks function — add confirm prompt)

This covers item 9: move "Clear all" to less accident-prone location with confirmation.

- [ ] **Step 1: Remove Clear all from panel header**

Change line 1283-1284 from:

```html
<div class="panel-header">
  Peaks &amp; Results
  <button class="btn btn-sm btn-red" onclick="clearAllPeaks()">Clear all</button>
</div>
```

to:

```html
<div class="panel-header">
  Peaks &amp; Results
</div>
```

- [ ] **Step 2: Add Clear all at the bottom of the peak list area**

After the `#peak-empty` div (line 1298), add:

```html
<div id="peak-clear-wrap" style="display:none;padding-top:8px;border-top:1px solid var(--border);margin-top:8px">
  <button class="btn btn-sm btn-red" style="width:100%;font-size:10px" onclick="clearAllPeaks()">Clear all peaks</button>
</div>
```

- [ ] **Step 3: Show/hide the Clear all button based on peak count**

In `renderPeakList`, after setting the empty state display, add:

```javascript
const clearWrap = document.getElementById('peak-clear-wrap');
if (clearWrap) clearWrap.style.display = state.peaks.length ? 'block' : 'none';
```

- [ ] **Step 4: Add confirmation prompt to clearAllPeaks**

Replace the `clearAllPeaks` function (lines 3261-3267) with:

```javascript
function clearAllPeaks() {
  if (!state.peaks.length) return;
  if (!confirm('Are you sure you want to clear all peaks?')) return;
  pushUndo();
  state.peaks = [];
  state.fitResult = null;
  renderPeakList();
  updatePlot();
}
```

- [ ] **Step 5: Commit**

```bash
git add templates/index.html
git commit -m "feat(ui): move Clear All to bottom of peak list, add confirmation prompt"
```

---

## Task 6: Status Bar Monospace Cleanup

**Files:**
- Modify: `templates/index.html:325-337` (statusbar CSS)

This covers item 10.

- [ ] **Step 1: Update status bar CSS**

The status bar (lines 325-337) already uses `font-family: var(--mono)` for all content. This is correct for numerical readability. Add explicit styling for labels vs values:

```css
#statusbar {
  padding: 4px 14px;
  background: var(--bg2);
  border-top: 1px solid var(--border);
  font-family: var(--sans);
  font-size: 10px;
  color: var(--text3);
  display: flex;
  gap: 20px;
  flex-shrink: 0;
}
#statusbar span { color: var(--text2); }
#statusbar span span { font-family: var(--mono); font-weight: 500; }
```

The outer `<span>` has the label (sans-serif), the inner `<span>` has the number (monospace).

- [ ] **Step 2: Commit**

```bash
git add templates/index.html
git commit -m "feat(ui): status bar labels sans-serif, values monospace"
```

---

## Task 7: Redesign Drop Zone with SVG Upload Icon

**Files:**
- Modify: `templates/index.html:404-421` (dropzone CSS)
- Modify: `templates/index.html:1099-1106` (dropzone HTML)

This covers item 11.

- [ ] **Step 1: Replace the folder emoji icon with an inline SVG**

Replace the dropzone HTML content (lines 1099-1106) — only the inner content, keep the event handlers:

```html
<div id="dropzone" onclick="document.getElementById('fileInput').click()"
     ondragover="handleDragOver(event)"
     ondragleave="this.classList.remove('drag-over')"
     ondrop="handleDrop(event)">
  <svg class="dz-svg-icon" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
    <line x1="12" y1="18" x2="12" y2="12"/>
    <polyline points="9 15 12 12 15 15"/>
  </svg>
  <p><strong>Click</strong> or drag &middot; file or folder</p>
  <p>.csv &middot; .txt &middot; .xlsx &middot; .vgd</p>
</div>
```

- [ ] **Step 2: Update dropzone CSS for the SVG icon**

Replace `.dz-icon` rule (line 418) with:

```css
#dropzone .dz-svg-icon { color: var(--text3); margin-bottom: 8px; opacity: 0.6; transition: opacity 0.2s; }
#dropzone:hover .dz-svg-icon { opacity: 1; color: var(--accent); }
```

- [ ] **Step 3: Commit**

```bash
git add templates/index.html
git commit -m "feat(ui): SVG document-upload icon for drop zone"
```

---

## Task 8: Empty State Onboarding with 1-2-3 Steps

**Files:**
- Modify: `templates/index.html:4508-4519` (renderEmptyChart function)
- Modify: `templates/index.html` CSS (add styles for onboarding)

This covers item 12: 1-2-3 step onboarding in the empty chart state.

- [ ] **Step 1: Add onboarding CSS**

Add new CSS block (before the light theme overrides, around line 790):

```css
/* ── Empty state onboarding ──────────────────────── */
.onboard-wrap {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  pointer-events: none;
}
.onboard-icon {
  width: 48px; height: 48px;
  margin: 0 auto 12px;
  color: var(--text3);
  opacity: 0.4;
}
.onboard-title {
  font-family: var(--sans);
  font-size: 14px;
  color: var(--text3);
  margin-bottom: 20px;
}
.onboard-steps {
  display: flex;
  gap: 32px;
  justify-content: center;
  align-items: flex-start;
}
.onboard-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.onboard-num {
  width: 32px; height: 32px;
  border-radius: 50%;
  border: 1px solid var(--border2);
  background: rgba(74,158,255,0.06);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--mono);
  font-size: 13px;
  font-weight: 500;
  color: var(--text2);
}
.onboard-label {
  font-family: var(--sans);
  font-size: 11px;
  color: var(--text3);
}
```

- [ ] **Step 2: Replace renderEmptyChart to show onboarding HTML**

Replace the `renderEmptyChart` function (lines 4508-4519) with:

```javascript
function renderEmptyChart() {
  if (state.chart) { state.chart.destroy(); state.chart = null; }
  if (state.residChart) { state.residChart.destroy(); state.residChart = null; }
  document.getElementById('resid-wrap').classList.add('hidden');
  document.getElementById('resid-handle').classList.add('hidden');

  const wrap = document.getElementById('main-chart-wrap');
  // Clear the canvas and add onboarding overlay
  const canvas = document.getElementById('mainChart');
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Remove any existing onboarding overlay
  const existing = wrap.querySelector('.onboard-wrap');
  if (existing) existing.remove();

  const ob = document.createElement('div');
  ob.className = 'onboard-wrap';
  ob.innerHTML = `
    <svg class="onboard-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
      <path d="M9 13h6"/><path d="M9 17h3"/>
    </svg>
    <div class="onboard-title">Load a spectrum to begin</div>
    <div class="onboard-steps">
      <div class="onboard-step">
        <div class="onboard-num">1</div>
        <div class="onboard-label">Drop a file</div>
      </div>
      <div class="onboard-step">
        <div class="onboard-num">2</div>
        <div class="onboard-label">Add peaks</div>
      </div>
      <div class="onboard-step">
        <div class="onboard-num">3</div>
        <div class="onboard-label">Run fit</div>
      </div>
    </div>
  `;
  wrap.appendChild(ob);
}
```

Also need to ensure the onboarding overlay is removed when a spectrum loads. In `updatePlot`, before the chart is built, add cleanup:

```javascript
const _ob = document.getElementById('main-chart-wrap').querySelector('.onboard-wrap');
if (_ob) _ob.remove();
```

Add this right at the top of `updatePlot`, after the `getROIData()` call and before the `renderEmptyChart` early return.

- [ ] **Step 3: Commit**

```bash
git add templates/index.html
git commit -m "feat(ui): empty state onboarding with 1-2-3 step guide"
```

---

## Task 9: Glassmorphism Effects on Sidebar Sections and Peak Cards

**Files:**
- Modify: `templates/index.html:236-256` (section CSS)
- Modify: `templates/index.html:339-372` (peak-item CSS)

This covers item 13: frosted glass effect with backdrop-filter blur and semi-transparent backgrounds.

- [ ] **Step 1: Add glassmorphism to sidebar sections**

Update the `.section` rule (line 236):

```css
.section {
  border: 1px solid rgba(100,140,220,0.12);
  border-radius: var(--radius);
  margin-bottom: 10px;
  overflow: hidden;
  background: rgba(26,32,48,0.5);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
```

Add a light-theme override inside `body.light-theme`:

```css
body.light-theme .section {
  background: rgba(255,255,255,0.6);
}
```

- [ ] **Step 2: Add glassmorphism to peak cards**

Update the `.peak-item` rule to include:

```css
.peak-item {
  /* existing properties... */
  background: rgba(26,32,48,0.4);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}
```

Light theme override:

```css
body.light-theme .peak-item {
  background: rgba(255,255,255,0.5);
}
```

- [ ] **Step 3: Commit**

```bash
git add templates/index.html
git commit -m "feat(ui): glassmorphism backdrop-filter on sections and peak cards"
```

---

## Task 10: Run Fit Button Shimmer/Glow Effect

**Files:**
- Modify: `templates/index.html` CSS (add keyframe animation)

This covers item 14.

- [ ] **Step 1: Add shimmer hover effect CSS**

Add after the `.btn-green:hover` rule (around line 193):

```css
.btn-green {
  background: var(--green-dim);
  border-color: var(--green);
  color: var(--green);
  position: relative;
  overflow: hidden;
}
.btn-green:hover {
  background: rgba(61,220,132,0.25);
  box-shadow: 0 0 12px rgba(61,220,132,0.3);
}
.btn-green:hover::after {
  content: '';
  position: absolute;
  top: 0; left: -100%; width: 50%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
  animation: btn-shimmer 0.8s ease-in-out;
}
@keyframes btn-shimmer {
  0% { left: -100%; }
  100% { left: 200%; }
}
```

- [ ] **Step 2: Commit**

```bash
git add templates/index.html
git commit -m "feat(ui): shimmer glow effect on Run Fit button hover"
```

---

## Task 11: Smooth Focus Ring Animations on Inputs

**Files:**
- Modify: `templates/index.html:209-221` (input focus CSS)

This covers item 15.

- [ ] **Step 1: Update input focus styles**

Replace the input focus rule (line 221) with:

```css
input:focus, select:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 2px rgba(74,158,255,0.15);
  transition: border-color 0.2s ease, box-shadow 0.3s ease;
}
```

Also update the base input rule (line 209) to ensure transition is smooth:

```css
input[type=text], input[type=number], select {
  /* ...existing properties... */
  transition: border-color 0.2s ease, box-shadow 0.3s ease;
}
```

For light theme, the accent color is already overridden in `:root`, so the rgba focus ring will use the correct blue.

- [ ] **Step 2: Commit**

```bash
git add templates/index.html
git commit -m "feat(ui): smooth animated focus rings on input fields"
```

---

## Task 12: Tab Bar Hover Effect

**Files:**
- Modify: `templates/index.html:624-662` (sp-tab CSS)

This covers item 16.

- [ ] **Step 1: Enhance spectrum tab hover**

The `.sp-tab:hover` rule (line 640) already has `background: var(--bg3); color: var(--text);`. Enhance it:

```css
.sp-tab:hover {
  background: var(--bg3);
  color: var(--text);
  box-shadow: inset 0 -2px 0 var(--border2);
}
.sp-tab.active:hover {
  box-shadow: none;
}
```

This adds a subtle bottom highlight on hover for inactive tabs, while keeping the active tab's solid accent border unaffected.

- [ ] **Step 2: Commit**

```bash
git add templates/index.html
git commit -m "feat(ui): subtle hover effect on spectrum tab bar"
```

---

## Task 13: Actions Dropdown with Icons and Hover Effects

**Files:**
- Modify: `templates/index.html:1073-1084` (Actions dropdown HTML items)
- Modify: `templates/index.html:513-531` (save-dropdown-item CSS)

This covers item 17: hover highlighting and small icons next to each Actions menu item.

- [ ] **Step 1: Update dropdown item CSS for better hover**

Update `.save-dropdown-item:hover` (line 529):

```css
.save-dropdown-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  width: 100%;
  padding: 7px 14px;
  font-family: var(--sans);
  font-size: 11px;
  color: var(--text);
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
  border-bottom: 1px solid var(--border);
  transition: background 0.15s, color 0.15s;
}
.save-dropdown-item:last-child { border-bottom: none; }
.save-dropdown-item:hover { background: var(--accent-dim); color: var(--accent2); }
.save-dropdown-item small { display: block; font-size: 9px; color: var(--text3); margin-top: 2px; }
.save-dropdown-item .dd-icon { flex-shrink: 0; font-size: 13px; margin-top: 1px; opacity: 0.6; }
```

- [ ] **Step 2: Add icons to dropdown items in HTML**

Update each `save-dropdown-item` button to include a `<span class="dd-icon">` prefix. Replace the dropdown menu content (lines 1074-1083):

```html
<div class="save-dropdown-menu">
  <button class="save-dropdown-item" onclick="saveFit()"><span class="dd-icon">&#128190;</span><div>Save Fit<small>Peak params only (~2 KB)</small></div></button>
  <button class="save-dropdown-item" onclick="saveSpectrum()"><span class="dd-icon">&#128196;</span><div>Save Spectrum<small>Data + fit curves (~50-200 KB)</small></div></button>
  <button class="save-dropdown-item" onclick="showProjectDialog()"><span class="dd-icon">&#128193;</span><div>Save Project<small>All tabs + metadata</small></div></button>
  <div style="height:1px;background:var(--border);margin:4px 0"></div>
  <button class="save-dropdown-item" onclick="exportFitTable('csv')"><span class="dd-icon">&#128202;</span><div>Export Table (CSV)<small>All fit parameters</small></div></button>
  <button class="save-dropdown-item" onclick="exportFitTable('xlsx')"><span class="dd-icon">&#128202;</span><div>Export Table (XLSX)<small>All fit parameters</small></div></button>
  <div style="height:1px;background:var(--border);margin:4px 0"></div>
  <button class="save-dropdown-item" onclick="loadSession()"><span class="dd-icon">&#128194;</span><div>Load Fit<small>Restore saved fit params</small></div></button>
  <button class="save-dropdown-item" onclick="exportResults()"><span class="dd-icon">&#128203;</span><div>Export Results<small>Peaks + areas as JSON</small></div></button>
  <button class="save-dropdown-item" onclick="exportFigure()"><span class="dd-icon">&#128247;</span><div>Export Figure<small>Save chart as PNG</small></div></button>
</div>
```

Unicode icons used: disk (&#128190;), page (&#128196;), folder (&#128193;), chart (&#128202;), open folder (&#128194;), clipboard (&#128203;), camera (&#128247;).

- [ ] **Step 3: Commit**

```bash
git add templates/index.html
git commit -m "feat(ui): icons and hover effects on Actions dropdown items"
```

---

## Task 14: Build Date in Footer

**Files:**
- Modify: `templates/index.html:1340-1345` (JS state/constants — add BUILD_DATE)
- Modify: `templates/index.html:1268-1274` (status bar HTML)

This covers item 20.

- [ ] **Step 1: Add BUILD_DATE constant at the top of the script section**

Add immediately after `<script>` (line 1340), before the state object:

```javascript
const BUILD_DATE = '2026-04-06';
```

- [ ] **Step 2: Add build date display to the status bar**

Add a final span in the status bar HTML (line 1273, after `#sb-msg`):

```html
<span style="margin-left:auto;color:var(--text3);font-family:var(--mono);font-size:9px" id="sb-build"></span>
```

- [ ] **Step 3: Set the build date on page load**

In the initialization code at the bottom of the script (near line 5674 where `renderEmptyChart()` is called), add:

```javascript
document.getElementById('sb-build').textContent = 'Build ' + BUILD_DATE;
```

- [ ] **Step 4: Commit**

```bash
git add templates/index.html
git commit -m "feat(ui): build date display in status bar footer"
```

---

## Task 15: Final Light Theme Adjustments

**Files:**
- Modify: `templates/index.html:791-811` (light theme CSS overrides)

This covers the cross-cutting requirement that all changes work in both dark and light modes.

- [ ] **Step 1: Add light theme overrides for new elements**

Add to the `body.light-theme` block (after line 811):

```css
body.light-theme .pill-toggle.active {
  background: rgba(37,99,235,0.1);
  border-color: var(--accent);
  color: var(--accent2);
}
body.light-theme .section {
  background: rgba(255,255,255,0.6);
  border-color: rgba(0,0,0,0.08);
}
body.light-theme .peak-item {
  background: rgba(255,255,255,0.5);
  border-color: rgba(0,0,0,0.08);
}
body.light-theme .onboard-num {
  background: rgba(37,99,235,0.06);
  border-color: rgba(0,0,0,0.12);
}
body.light-theme .btn-green:hover {
  box-shadow: 0 0 12px rgba(22,163,74,0.3);
}
body.light-theme .save-dropdown-item:hover {
  background: rgba(37,99,235,0.08);
}
```

- [ ] **Step 2: Test both themes by toggling the theme button**

Verify: pill toggles, peak cards, sections, onboarding, status bar, dropzone, and dropdown all render correctly in light mode.

- [ ] **Step 3: Commit**

```bash
git add templates/index.html
git commit -m "feat(ui): light theme overrides for all new UI elements"
```

---

## Task 16: Verify No Data Pipeline Code Was Modified

- [ ] **Step 1: Run a diff to confirm untouched functions**

```bash
git diff HEAD -- templates/index.html | grep -E '^\+.*function (loadFile|_loadOneFile|_filterFiles|parseCSV|parseXLSX|runFit|peakToBackendSpec|uploadToBackend|computeBackground|getROIData|getCorrectedBE|updateChargeCorrection|updatePeakParam)' | head -20
```

Expected: Empty output (no changes to any of these function signatures).

- [ ] **Step 2: Run JS syntax check**

```bash
node --check templates/index.html 2>&1 || echo "Syntax check not applicable to HTML"
```

Extract the `<script>` content and check:

```bash
sed -n '/<script>/,/<\/script>/p' templates/index.html | sed '1d;$d' > /tmp/xps_check.js && node --check /tmp/xps_check.js
```

Expected: No syntax errors.

- [ ] **Step 3: Final commit with all changes**

If any fixups were needed during verification, commit them:

```bash
git add templates/index.html
git commit -m "chore: verify data pipeline untouched, fix any syntax issues"
```

---

## Self-Review Checklist

| Spec Item | Task |
|-----------|------|
| 1. System font stack | Task 1, Step 1 |
| 2. Consistent section headers | Task 1, Step 2 |
| 3. Consistent input labels | Task 1, Step 3 |
| 4. Monospace only for numbers | Task 1, Step 4 |
| 5. Clean up font inconsistencies | Task 1, Steps 2-4 |
| 6. "Auto from data" font fix | Task 1, Step 4 (btn class uses sans now) |
| 7. Pill-shaped toggle buttons | Task 2 |
| 8. Collapsible peak cards with summary | Task 3 |
| 9. Move Clear all + confirmation | Task 5 |
| 10. Status bar monospace cleanup | Task 6 |
| 11. SVG upload icon drop zone | Task 7 |
| 12. 1-2-3 onboarding empty state | Task 8 |
| 13. Glassmorphism effects | Task 9 |
| 14. Run Fit shimmer/glow | Task 10 |
| 15. Smooth focus ring animations | Task 11 |
| 16. Tab bar hover effect | Task 12 |
| 17. Actions dropdown icons + hover | Task 13 |
| 18. Color-coded left border on peak cards | Task 3, Step 1 (border-left) |
| 19. Hover peak card highlights chart peak | Task 4 |
| 20. Build date in footer | Task 14 |
| Dark/light mode compatibility | Task 15 |
| Data pipeline untouched verification | Task 16 |
