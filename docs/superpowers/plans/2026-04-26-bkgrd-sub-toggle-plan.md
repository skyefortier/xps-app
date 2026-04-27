# Background-Subtracted View Toggle — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a "Bkgrd Sub" pill toggle to the chart toolbar that, when active, redraws the spectrum, peaks, and envelope with the background subtracted (peaks rise from y=0), with the toggle persisted in saved fits/projects and disabled when no background is available or while a fit is running.

**Architecture:** Single new pill in [templates/index.html](templates/index.html) wired into the existing `updatePlot()` re-render pipeline. Subtracted view is computed at draw time from existing `plotBE`/`plotBG`/`plotInten` arrays — no new state arrays, no new computations. Pill state lives in `tab.ui.bgSubtractedView` and round-trips through the existing `_captureUI`/`_restoreUI`/`_doSaveFit`/`fromJSON` paths. A small helper (`_isBgSubViewActive()`) gates the rendering branch and falls back to raw view if the bg becomes unavailable while the pill is on.

**Tech Stack:** Vanilla JS (no framework), Chart.js 4.4 (CDN), single-file `templates/index.html`. No backend changes (`fitting.py` and `app.py` are NOT touched).

**Reference:** Spec at [docs/superpowers/plans/2026-04-26-bkgrd-sub-toggle.md](docs/superpowers/plans/2026-04-26-bkgrd-sub-toggle.md). Read it first.

**Constraint:** All edits are in `templates/index.html`. If at any point you find yourself wanting to edit `fitting.py` or `app.py`, STOP and report — that means the plan is wrong, not that the backend needs changing.

**Deferred (future enhancement):** Subtracted-mode smoothing and derivatives. This implementation only re-computes the spectrum line itself; smoothing, derivative, and overlay-tab overlays are hidden in subtracted view (with their controls visibly disabled so users understand why). A later enhancement could re-derive those overlays from the bg-subtracted ROI data so they remain usable.

---

## File Structure

Single file modified: **`templates/index.html`** (~377K, ~9K lines).

Touchpoints in that file (line numbers below are approximate — `grep` exact strings before editing):

| Section | Approx line | What changes |
|---|---|---|
| Pill-toggle CSS block | ~1129 | Add `.pill-toggle.disabled` rule |
| Chart toolbar HTML | ~1623 | Insert new `<label>` between `show-residuals` and `invert-be` |
| `tabManager._captureUI` | ~2666 | Add `bgSubtractedView` capture |
| `tabManager._restoreUI` | ~2681 | Add `bgSubtractedView` restore + visual sync |
| `_doSaveFit` (v1) | ~6675 | Add `bgSubtractedView` to `background` block |
| `tabManager.fromJSON` (v1 path) | ~2284 | Apply `data.background.bgSubtractedView` to `active.ui` |
| `_showFitSpinner` / `_hideFitSpinner` | ~4818 / ~4829 | Call pill-state recompute |
| Bg-type `<select>` `onchange` (`_onBgTypeChange` or inline) | grep `bg-type` | Call pill-state recompute |
| New helpers | new functions, near other UI helpers around ~4818 | `_onBgSubToggle()`, `_isBgSubViewActive()`, `_updateBgSubPillEnabled()` |
| `updatePlot()` dataset construction | ~5987–6210 | Branch on `_isBgSubViewActive()` for data/peaks/envelope/bg/fill-targets |
| `updatePlot()` chart plugins | ~6225 | Add `bgSubZeroLinePlugin` for the y=0 reference line |

No new files. No backend changes.

---

## Pre-flight

Before any task, create the rollback tag the spec calls for, and back up the file. **Do these once at the very start, not per task.**

- [ ] **Step 0.1: Create rollback tag**

  ```bash
  cd ~/xps-app
  git tag pre-bkgrd-sub-toggle
  git push origin pre-bkgrd-sub-toggle
  ```

  Expected: tag created locally and pushed to origin.

- [ ] **Step 0.2: Back up `templates/index.html`**

  ```bash
  cp ~/xps-app/templates/index.html ~/xps-app/backups/templates_index.html.pre-bkgrd-sub-$(date +%Y%m%d-%H%M%S)
  ```

  Expected: silent success; `ls ~/xps-app/backups/ | grep pre-bkgrd-sub` shows the new file.

---

## Task 1: Add the pill button HTML and disabled CSS

**Files:**
- Modify: `templates/index.html` (CSS block at ~line 1155, chart-toolbar HTML at ~line 1623)

This task adds a visually correct pill that renders all three states (active/inactive/disabled) but does nothing functional yet. We verify it appears in the right place and the CSS works before wiring any behavior.

- [ ] **Step 1.1: Add `.pill-toggle.disabled` CSS**

  Locate the existing `.pill-toggle` block (search for `.pill-toggle.active {`). Insert AFTER the `.pill-toggle.active { ... }` rule and BEFORE the `.pill-toggle input[type="checkbox"] { display: none; }` rule:

  ```css
    .pill-toggle.disabled {
      opacity: 0.4;
      cursor: not-allowed;
      pointer-events: none;
      color: var(--text3);
      border-color: var(--border);
      background: transparent;
    }
  ```

  `pointer-events: none` blocks click activation regardless of the underlying `<input>` state, which is the simplest robust disable.

- [ ] **Step 1.2: Add the pill HTML in chart-toolbar**

  Locate the existing toolbar block (search for `show-residuals">`). Insert a new `<label>` IMMEDIATELY AFTER the `Residuals` `</label>` and BEFORE the `Invert BE` `<label>`:

  ```html
          <label class="pill-toggle disabled" id="bg-sub-pill" title="Background subtraction is unavailable when no background method is set.">
            <input type="checkbox" id="bg-sub-toggle" disabled onchange="_onBgSubToggle()">
            Bkgrd Sub
          </label>
  ```

  Notes:
  - Initial state is `disabled` (no spectrum/bg loaded yet on a fresh page); `_updateBgSubPillEnabled()` will re-enable it once a bg becomes available (Task 2).
  - Initial state is NOT `active` — spec says default is OFF.
  - `_onBgSubToggle()` is defined in Task 2; the call here is a no-op until then because the pill is disabled.

- [ ] **Step 1.3: Open the app in a browser, verify visual**

  ```bash
  cd ~/xps-app
  source venv/bin/activate
  python3 -c "from app import app; app.run(host='127.0.0.1', port=5000, debug=False)" &
  ```

  Open `http://127.0.0.1:5000` in browser. Expected: a faded "Bkgrd Sub" pill appears in the toolbar between "Residuals" and "Invert BE". Hover shows the tooltip. Clicking does nothing (it's disabled). The other pills work as before.

  Stop the server (`fg` then Ctrl+C, or `pkill -f "app.run"`).

- [ ] **Step 1.4: Commit**

  ```bash
  git add templates/index.html
  git commit -m "feat(ui): add Bkgrd Sub pill button (HTML + disabled CSS, no behavior yet)"
  ```

---

## Task 2: Pill state machine — enable/disable + toggle handler

**Files:**
- Modify: `templates/index.html` (new helper functions + hooks into bg-type change and fit spinner)

This task wires the pill so it correctly enables/disables based on bg availability and fit-in-progress, and so clicking it toggles the visual state and triggers a chart re-render. It does NOT yet change what the chart draws — `updatePlot()` is still raw-only. The visual cycle (toggle on → pill turns blue, toggle off → pill turns gray) should work end-to-end.

- [ ] **Step 2.1: Add the three new helper functions**

  Locate `_showFitSpinner` (search for `function _showFitSpinner()`). Insert these three functions IMMEDIATELY BEFORE `_showFitSpinner`:

  ```javascript
  // ═══════════════════════════════════════════════════
  // BKGRD SUB VIEW TOGGLE
  // ═══════════════════════════════════════════════════
  // The pill at id="bg-sub-pill" / id="bg-sub-toggle" can be in three
  // visual states (active, inactive, disabled). The disabled state
  // applies whenever subtraction is meaningless: no spectrum loaded,
  // bg-type is "none", or a fit is running. The pill's checked state
  // is preserved across disable cycles so users get their preference
  // back when bg becomes available again.

  let _bgSubFitInFlight = false;

  // IDs of overlay controls that don't compose with subtracted view
  // (they're full-spectrum / non-bg-aware). When subtracted view is
  // effectively active we disable them with the existing app
  // convention (opacity 0.4 + disabled attr + title tooltip), so users
  // see why their checkbox appears inert. Identical pattern to how
  // `shirley-iter` is gated when bg-type doesn't need iteration.
  const _BG_SUB_DEPENDENT_CONTROL_IDS = ['smooth-enable', 'deriv1-enable', 'deriv2-enable'];

  function _isBgSubViewActive() {
    const toggle = document.getElementById('bg-sub-toggle');
    if (!toggle || !toggle.checked) return false;
    // Even if the pill is checked, fall back to raw view when bg is
    // unavailable (defensive: covers the moment between bg-type=none
    // and the pill recompute, and any transient bg gap).
    const bgType = document.getElementById('bg-type')?.value || 'shirley';
    if (bgType === 'none') return false;
    if (!state.rawBE || state.rawBE.length < 2) return false;
    return true;
  }

  function _updateBgSubPillEnabled() {
    const pill = document.getElementById('bg-sub-pill');
    const toggle = document.getElementById('bg-sub-toggle');
    if (!pill || !toggle) return;
    const bgType = document.getElementById('bg-type')?.value || 'shirley';
    const noBg = bgType === 'none';
    const noSpectrum = !state.rawBE || state.rawBE.length < 2;
    const fitting = _bgSubFitInFlight;
    const disabled = noBg || noSpectrum || fitting;
    toggle.disabled = disabled;
    pill.classList.toggle('disabled', disabled);
    if (fitting) {
      pill.title = 'Background subtraction toggle is locked while a fit is running.';
    } else if (noSpectrum) {
      pill.title = 'Load a spectrum to enable background subtraction.';
    } else if (noBg) {
      pill.title = 'Background subtraction is unavailable when no background method is set.';
    } else {
      pill.title = 'Toggle background-subtracted chart view.';
    }
  }

  function _onBgSubToggle() {
    const toggle = document.getElementById('bg-sub-toggle');
    const pill = document.getElementById('bg-sub-pill');
    if (!toggle || !pill) return;
    pill.classList.toggle('active', toggle.checked);
    // Persist into the active tab's UI snapshot so save/restore round-trip.
    if (typeof tabManager !== 'undefined' && tabManager.activeId) {
      const t = tabManager._getTab(tabManager.activeId);
      if (t && t.ui) t.ui.bgSubtractedView = toggle.checked;
    }
    _syncSubViewDependentControls();
    updatePlot();
  }

  // Disable controls that don't compose with subtracted view, so their
  // checkboxes don't read as "broken" when toggling them does nothing
  // visible. Re-enable when subtracted view is off. Tooltip mirrors the
  // future-enhancement note in the plan.
  function _syncSubViewDependentControls() {
    const subActive = _isBgSubViewActive();
    for (const id of _BG_SUB_DEPENDENT_CONTROL_IDS) {
      const el = document.getElementById(id);
      if (!el) continue;
      el.disabled = subActive;
      // Apply opacity to the wrapping label so the visual disable is
      // obvious — matches the shirley-iter / bg-endpoint-avg pattern.
      const wrap = el.closest('label') || el.parentElement;
      if (wrap) wrap.style.opacity = subActive ? '0.4' : '1';
      if (subActive) {
        el.title = 'Unavailable in subtracted view. Toggle Bkgrd Sub off to enable.';
        if (wrap && wrap !== el) wrap.title = el.title;
      } else {
        el.title = '';
        if (wrap && wrap !== el) wrap.title = '';
      }
    }
  }
  ```

  Note `_bgSubFitInFlight` is a module-level boolean — the spec calls for global gating, so a single flag is correct.

- [ ] **Step 2.2: Hook into the fit spinner**

  Locate `_showFitSpinner` (the function we inserted before in Step 2.1). Modify its body — after `if (overlay) overlay.style.display = 'flex';` — to set the in-flight flag and recompute the pill:

  Find:
  ```javascript
  function _showFitSpinner() {
    const overlay = document.getElementById('fit-spinner-overlay');
    const label = document.getElementById('fit-spinner-label');
    if (overlay) overlay.style.display = 'flex';
    if (label) label.innerHTML = 'Fitting<span class="ellipsis"></span>';
    document.querySelector('.btn-green').disabled = true;
  ```

  Replace with:
  ```javascript
  function _showFitSpinner() {
    const overlay = document.getElementById('fit-spinner-overlay');
    const label = document.getElementById('fit-spinner-label');
    if (overlay) overlay.style.display = 'flex';
    if (label) label.innerHTML = 'Fitting<span class="ellipsis"></span>';
    document.querySelector('.btn-green').disabled = true;
    _bgSubFitInFlight = true;
    _updateBgSubPillEnabled();
  ```

  Find:
  ```javascript
  function _hideFitSpinner() {
    const overlay = document.getElementById('fit-spinner-overlay');
    if (overlay) overlay.style.display = 'none';
    document.querySelector('.btn-green').disabled = false;
    clearTimeout(_showFitSpinner._timer);
  }
  ```

  Replace with:
  ```javascript
  function _hideFitSpinner() {
    const overlay = document.getElementById('fit-spinner-overlay');
    if (overlay) overlay.style.display = 'none';
    document.querySelector('.btn-green').disabled = false;
    clearTimeout(_showFitSpinner._timer);
    _bgSubFitInFlight = false;
    _updateBgSubPillEnabled();
  }
  ```

- [ ] **Step 2.3: Hook into the bg-type change**

  Find the `<select id="bg-type" ...>` element (search `id="bg-type"`). Identify its `onchange` handler. There is an existing `_onBgTypeChange` function called from this handler (search `function _onBgTypeChange`). Add these two calls as the LAST statements inside `_onBgTypeChange`'s body (right before its closing `}`):

  ```javascript
      _updateBgSubPillEnabled();
      _syncSubViewDependentControls();
  ```

  Both calls are needed because changing bg-type can switch `_isBgSubViewActive()` from true to false (or vice-versa via re-enable + remembered checked state), and the dependent controls' enabled state must follow.

  If `_onBgTypeChange` does not exist as a named function and the bg-type onchange is inline, instead modify the inline handler to append `; _updateBgSubPillEnabled(); _syncSubViewDependentControls()` to the existing handler chain. Use `grep -n 'id="bg-type"' templates/index.html` to find the exact element and confirm.

- [ ] **Step 2.4: Hook into spectrum load and tab activation**

  After `state.rawBE` becomes populated (any spectrum load) or after `tabManager.activateTab` finishes restoring UI, the pill state must be recomputed. Locate `tabManager.activateTab` and find the line that calls `this._restoreUI(tab.ui);`. Append, on the next line:

  ```javascript
      if (typeof _updateBgSubPillEnabled === 'function') _updateBgSubPillEnabled();
  ```

  Also locate the spectrum-loaded code path that triggers `updatePlot()` after parsing a file. Search for the body of the function that sets `state.rawBE = ...` and calls `updatePlot()` (likely a `_loadSpectrumFile` or `parseAndLoadSpectrum`-style helper — `grep` for `state.rawBE\s*=`). Immediately before its `updatePlot()` call, add:

  ```javascript
      if (typeof _updateBgSubPillEnabled === 'function') _updateBgSubPillEnabled();
  ```

  (Defensive `typeof` check guards against function ordering — `_updateBgSubPillEnabled` is defined later in the file than some load handlers.)

- [ ] **Step 2.5: Browser smoke test**

  Restart the dev server. Load a real spectrum (e.g., the demo C 1s).
  - Pill becomes enabled (clickable, blue when active).
  - Click it → pill turns blue. Chart redraws but currently looks the same as raw (because Task 3 hasn't landed yet).
  - Click again → pill turns gray. Chart redraws same way.
  - Change Background Method to "None" → pill becomes disabled and faded; tooltip explains.
  - Change back to "Shirley" → pill re-enables, and remembers its previous checked state.
  - Trigger Run Fit → pill becomes disabled while fit runs, re-enables when fit finishes.

  No errors in the JS console.

- [ ] **Step 2.6: Commit**

  ```bash
  git add templates/index.html
  git commit -m "feat(ui): wire Bkgrd Sub pill state machine (enable/disable + toggle)"
  ```

---

## Task 3: Render subtracted view in `updatePlot()`

**Files:**
- Modify: `templates/index.html` (`updatePlot()` body around lines 5987–6210)

This is the biggest task. We branch the dataset construction inside `updatePlot()` so that when `_isBgSubViewActive()` returns true, the spectrum/peaks/envelope are drawn from y=0, the background line is hidden, the data series is restricted to the ROI (since bg only exists for ROI), and full-spectrum overlays (smoothed, derivatives, other-tab overlays) are suppressed because they don't compose with subtracted ROI rendering.

- [ ] **Step 3.1: Read the affected block to memorize structure**

  ```bash
  sed -n '5987,6210p' templates/index.html | less
  ```

  Confirm the variables `plotBE`, `plotBG`, `plotInten`, `bgSubtracted`, `modelFull`, `fittedYBacked` are defined and named as the plan assumes. If anything is renamed, adjust each subsequent step accordingly.

- [ ] **Step 3.2: Compute subtracted-view flag once, near the top of `updatePlot()`**

  Locate the line `const showFill = document.getElementById('show-fill').checked;` (~line 6045). It's after the data and ROI extraction but before peak datasets are pushed. Insert IMMEDIATELY BEFORE that line:

  ```javascript
    // Bkgrd Sub view: redraws the chart with the background subtracted.
    // The flag is read once per updatePlot() call so all dataset branches
    // see a consistent value. _isBgSubViewActive() is defensive — it
    // returns false if bg-type is "none" even when the pill is checked.
    const bgSubView = _isBgSubViewActive();
  ```

- [ ] **Step 3.3: Branch the individual-peak datasets**

  Find the existing block that constructs the `_bg_<peakid>` invisible fill targets and the per-peak datasets (currently `data: plotBE.map((b, i) => ({ x: b, y: plotBG[i] }))` for the targets and `y: peakY[i] + plotBG[i]` for the peaks).

  Replace the `_bg_*` target push:

  ```javascript
          datasets.push({
            label: '_bg_' + p.id,
            data: plotBE.map((b, i) => ({ x: b, y: plotBG[i] })),
            ...
          });
  ```

  With:

  ```javascript
          datasets.push({
            label: '_bg_' + p.id,
            data: plotBE.map((b, i) => ({ x: b, y: bgSubView ? 0 : plotBG[i] })),
            borderColor: 'transparent',
            borderWidth: 0,
            pointRadius: 0,
            fill: false,
            hidden: false,
          });
  ```

  Replace the per-peak push's `y` calculation:

  ```javascript
            data: plotBE.map((b, i) => ({ x: b, y: peakY[i] + plotBG[i] })),
  ```

  With:

  ```javascript
            data: plotBE.map((b, i) => ({ x: b, y: peakY[i] + (bgSubView ? 0 : plotBG[i]) })),
  ```

- [ ] **Step 3.4: Branch the background line**

  Find the block:

  ```javascript
    // Background — frozen to fit range after fit
    if (plotBE.length) {
      datasets.push({
        label: 'Background',
        ...
      });
    }
  ```

  Replace its first line with:

  ```javascript
    // Background — frozen to fit range after fit. Hidden in subtracted view.
    if (plotBE.length && !bgSubView) {
      datasets.push({
  ```

  (No other change to the body.)

- [ ] **Step 3.5: Branch the raw "Data" series**

  Find:

  ```javascript
    // Raw data — FULL spectrum range (zoom-independent)
    const _cc = _chartColors();
    datasets.push({
      label: 'Data',
      data: corrBE.map((b, i) => ({ x: b, y: fullInten[i] })),
      borderColor: _cc.rawData,
      ...
    });
  ```

  Replace with:

  ```javascript
    // Raw data — FULL spectrum range in raw view; ROI-only subtracted in
    // subtracted view (background only exists for the ROI window).
    const _cc = _chartColors();
    datasets.push({
      label: 'Data',
      data: bgSubView
        ? plotBE.map((b, i) => ({ x: b, y: plotInten[i] - plotBG[i] }))
        : corrBE.map((b, i) => ({ x: b, y: fullInten[i] })),
      borderColor: _cc.rawData,
      backgroundColor: document.body.classList.contains('light-theme')
        ? 'rgba(26,26,46,0.08)' : 'rgba(232,237,245,0.08)',
      pointRadius: 0,
      borderWidth: 1.5,
      tension: 0,
      fill: false
    });
  ```

- [ ] **Step 3.6: Branch the envelope ("Fit") series**

  Find:

  ```javascript
    if (showEnvelope && plotBE.length && (fittedYBacked || state.peaks.length)) {
      datasets.push({
        label: 'Fit',
        data: fittedYBacked
          ? plotBE.map((b, i) => ({ x: b, y: fittedYBacked[i] }))
          : plotBE.map((b, i) => ({ x: b, y: modelFull[i] + plotBG[i] })),
        ...
      });
    }
  ```

  Replace the `data:` block:

  ```javascript
        data: fittedYBacked
          ? plotBE.map((b, i) => ({ x: b, y: fittedYBacked[i] - (bgSubView ? plotBG[i] : 0) }))
          : plotBE.map((b, i) => ({ x: b, y: modelFull[i] + (bgSubView ? 0 : plotBG[i]) })),
  ```

- [ ] **Step 3.7: Branch the preview overlay**

  Find:

  ```javascript
    if (_historyPreview && _historyPreview.peaks && _historyPreview.peaks.length && plotBE.length) {
      const prevPeakY = evalAllPeaks(plotBE, _historyPreview.peaks);
      ...
      datasets.push({
        label: 'Preview',
        data: plotBE.map((b, i) => ({ x: b, y: prevPeakY[i] + plotBG[i] })),
        ...
      });
    }
  ```

  Replace the `data:` line:

  ```javascript
        data: plotBE.map((b, i) => ({ x: b, y: prevPeakY[i] + (bgSubView ? 0 : plotBG[i]) })),
  ```

- [ ] **Step 3.8: Hide full-spectrum overlays in subtracted view**

  Smoothed, derivatives, and other-tab overlays are full-spectrum and don't have ROI-aligned bg, so they don't compose with subtracted view. Wrap each in a `bgSubView` guard. (The smooth/derivative *checkboxes* are also visibly disabled so users see why — that gating lives in `_syncSubViewDependentControls` from Task 2 and runs whenever sub-view state changes; the chart-side guards here are the matching draw-time enforcement.)

  Find the `if (smoothEnabled && fullInten.length > 5) {` block. Change to:

  ```javascript
    if (!bgSubView && smoothEnabled && fullInten.length > 5) {
  ```

  Find the `if ((d1Enabled || d2Enabled) && fullInten.length > 3) {` block. Change to:

  ```javascript
    if (!bgSubView && (d1Enabled || d2Enabled) && fullInten.length > 3) {
  ```

  Find the overlay-tab block (`if (overlayMode && typeof tabManager !== 'undefined') {`). Change to:

  ```javascript
    if (!bgSubView && overlayMode && typeof tabManager !== 'undefined') {
  ```

  (Note: Overlay button itself stays interactive — gating it requires more invasive changes to overlayMode lifecycle and is out of scope. Per the future-enhancement note at the top of this plan, overlay-tab subtracted rendering is deferred. If a user enables Overlay while bg-sub is on they'll see no overlays render; toggling bg-sub off restores them.)

- [ ] **Step 3.9: Browser test — toggle behavior**

  Restart server. Load a spectrum, set bg-type to Shirley, place ROI around a peak, run a fit.

  - Pill OFF: chart looks identical to before (regression check). Smooth/derivative checkboxes in the Tools panel are interactive at full opacity.
  - Pill ON: spectrum (ROI window only), peaks, envelope all draw from y=0; background line gone; full-spectrum data outside ROI also gone; smoothed/derivatives/overlay tabs hidden in chart. Smooth and derivative checkboxes in the Tools panel are visibly faded (opacity 0.4) and unclickable; hovering one shows "Unavailable in subtracted view…".
  - Toggle on/off rapidly: chart redraws each time, controls' enable state flips with it, no console errors.

  Don't worry yet about the y=0 reference line (Task 4) — small negative tail values may render below the x-axis without a baseline; that's expected at this stage.

- [ ] **Step 3.10: Commit**

  ```bash
  git add templates/index.html
  git commit -m "feat(ui): render Bkgrd Sub view in updatePlot (peaks/envelope from y=0)"
  ```

---

## Task 4: Y=0 reference line plugin

**Files:**
- Modify: `templates/index.html` (chart plugin block around line 6225)

A thin gray horizontal line at y=0 helps users orient when negative values appear in subtracted view.

- [ ] **Step 4.1: Add the inline plugin**

  Locate the existing inline plugins block in `updatePlot()` — they are declared right before `state.chart = new Chart(...)`. Find `pinYRangePlugin` (search `const pinYRangePlugin =`). Insert AFTER `pinYRangePlugin`'s closing `};`:

  ```javascript
    // Plugin: in subtracted view, draw a thin gray horizontal line at y=0
    // behind all data series. Helps users orient since negative values
    // can appear from background-subtraction noise at endpoints.
    const bgSubZeroLinePlugin = {
      id: 'bgSubZeroLine',
      beforeDatasetsDraw(chart) {
        if (!_isBgSubViewActive()) return;
        const { ctx, chartArea, scales } = chart;
        if (!chartArea || !scales.y) return;
        const yZero = scales.y.getPixelForValue(0);
        if (!isFinite(yZero) || yZero < chartArea.top || yZero > chartArea.bottom) return;
        ctx.save();
        ctx.strokeStyle = 'rgba(120,140,170,0.5)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(chartArea.left, yZero);
        ctx.lineTo(chartArea.right, yZero);
        ctx.stroke();
        ctx.restore();
      }
    };
  ```

- [ ] **Step 4.2: Register the plugin in the Chart constructor**

  Locate the `new Chart(ctx, { ... plugins: [...] ... })` call. The current `plugins:` array reads:

  ```javascript
      plugins: [surveyLabelPlugin, pinYRangePlugin, overlayPlugin, previewGlowPlugin],
  ```

  Replace with:

  ```javascript
      plugins: [surveyLabelPlugin, pinYRangePlugin, bgSubZeroLinePlugin, overlayPlugin, previewGlowPlugin],
  ```

- [ ] **Step 4.3: Browser test — y=0 line appears**

  Restart server. Toggle Bkgrd Sub on. Confirm a thin gray horizontal line appears at y=0 across the plot area. Toggle off — line vanishes.

- [ ] **Step 4.4: Commit**

  ```bash
  git add templates/index.html
  git commit -m "feat(ui): add y=0 reference line in subtracted-view chart"
  ```

---

## Task 5: Save/load round-trip

**Files:**
- Modify: `templates/index.html` (`_captureUI`, `_restoreUI`, `_doSaveFit`, `tabManager.fromJSON` v1 path)

Persist the toggle state in v1 fit files (`.fit.json`) and v2 projects (`.proj.json`). v2 round-trip is automatic once `_captureUI`/`_restoreUI` carry the field, because `tab.ui` is serialized whole; v1 needs explicit field handling.

- [ ] **Step 5.1: Extend `_captureUI`**

  Locate `_captureUI` (search `_captureUI()`). Inside the returned object, add a new key. Find the existing object (it ends with `ccLit:`):

  ```javascript
        ccLit:       document.getElementById('cc-lit')?.value || '',
      };
  ```

  Replace with:

  ```javascript
        ccLit:       document.getElementById('cc-lit')?.value || '',
        bgSubtractedView: !!document.getElementById('bg-sub-toggle')?.checked,
      };
  ```

- [ ] **Step 5.2: Extend `_restoreUI`**

  Locate `_restoreUI(ui)` (immediately follows `_captureUI`). At the END of the function body, BEFORE the closing `}`, add:

  ```javascript
      // Bkgrd Sub: restore checked state, sync visual class, refresh enable,
      // and re-gate the dependent overlay controls so they reflect the
      // restored sub-view state.
      const bgSubToggle = document.getElementById('bg-sub-toggle');
      const bgSubPill = document.getElementById('bg-sub-pill');
      if (bgSubToggle && bgSubPill) {
        const want = !!ui.bgSubtractedView;
        bgSubToggle.checked = want;
        bgSubPill.classList.toggle('active', want);
      }
      if (typeof _updateBgSubPillEnabled === 'function') _updateBgSubPillEnabled();
      if (typeof _syncSubViewDependentControls === 'function') _syncSubViewDependentControls();
  ```

  Note: the `_updateBgSubPillEnabled()` call here supersedes the one we added in Task 2 Step 2.4. You can either keep both (idempotent) or remove the Task 2 call from `activateTab` once you confirm `_restoreUI` runs on every tab activation. Check by searching `_restoreUI(` — it's called from `activateTab` and from `fromJSON` v1 path. So removing the Task 2 `activateTab` hook is safe.

- [ ] **Step 5.3: Extend v1 save (`_doSaveFit`)**

  Locate `_doSaveFit` (search `function _doSaveFit()`). Find the `background:` object in its returned `data`:

  ```javascript
      background: {
        type: document.getElementById('bg-type').value,
        start: document.getElementById('bg-start').value,
        end: document.getElementById('bg-end').value,
        shirleyIter: document.getElementById('shirley-iter').value
      },
  ```

  Replace with:

  ```javascript
      background: {
        type: document.getElementById('bg-type').value,
        start: document.getElementById('bg-start').value,
        end: document.getElementById('bg-end').value,
        shirleyIter: document.getElementById('shirley-iter').value,
        bgSubtractedView: !!document.getElementById('bg-sub-toggle')?.checked,
      },
  ```

- [ ] **Step 5.4: Extend v1 load (`tabManager.fromJSON`)**

  Locate the v1-load branch in `fromJSON` (search `// Apply background`). Find:

  ```javascript
        if (data.background) {
          active.ui.bgType = data.background.type || 'shirley';
          active.ui.bgStart = data.background.start || '';
          active.ui.bgEnd = data.background.end || '';
          active.ui.shirleyIter = data.background.shirleyIter || '5';
        }
  ```

  Replace with:

  ```javascript
        if (data.background) {
          active.ui.bgType = data.background.type || 'shirley';
          active.ui.bgStart = data.background.start || '';
          active.ui.bgEnd = data.background.end || '';
          active.ui.shirleyIter = data.background.shirleyIter || '5';
          // bgSubtractedView is missing from pre-feature saves → falsy default
          active.ui.bgSubtractedView = !!data.background.bgSubtractedView;
        }
  ```

  v2 projects need no extra fromJSON code — `tab.ui` is restored whole through `_restoreUI` in `activateTab`.

- [ ] **Step 5.5: Browser test — round-trip**

  - Save a fit with toggle ON: saved JSON's `background` block must include `"bgSubtractedView": true`. Inspect it via the browser's Save-as dialog and a text editor.
  - Reload the page (Ctrl+R). The toggle starts OFF (no spectrum loaded).
  - Drag-load the saved `.fit.json`. Toggle should snap to ON; chart should be in subtracted view.
  - Save the project (multi-tab `.proj.json`) with toggle ON. Reload. Drag-load. Toggle ON.
  - Save a project with toggle OFF; reload; drag-load. Toggle OFF.
  - Backwards compat: drag-load a `.fit.json` from before this feature (any older saved fit). Toggle OFF, no errors in console.

- [ ] **Step 5.6: Commit**

  ```bash
  git add templates/index.html
  git commit -m "feat(ui): persist Bkgrd Sub toggle in fit and project save/load"
  ```

---

## Task 6: Final wiring & cleanup pass

**Files:**
- Modify: `templates/index.html` (remove Task 2 `activateTab` hook if redundant; remove load-time hook duplication if redundant; verify spec coverage)

This is the housekeeping task. We confirm there's exactly one place that drives `_updateBgSubPillEnabled` per state change, no duplicate calls, and no orphan hooks.

- [ ] **Step 6.1: Remove redundant hooks**

  If you added a `_updateBgSubPillEnabled()` call right after `_restoreUI(tab.ui)` in `activateTab` during Task 2 Step 2.4, AND `_restoreUI` itself now calls `_updateBgSubPillEnabled()` (Task 5 Step 5.2), the `activateTab`-side call is redundant. Remove it.

  Likewise, the spectrum-load hook from Task 2 Step 2.4 is redundant if the spectrum-load path ends with an `activateTab(...)` call. Verify by tracing: search for `_loadOneFile` and `parseAndLoad`-style functions — confirm they trigger `activateTab` (which now triggers `_updateBgSubPillEnabled` via `_restoreUI`). If they DO go through `activateTab`, remove the spectrum-load-side `_updateBgSubPillEnabled` call. If they DON'T (e.g., raw drop-in), keep that call.

- [ ] **Step 6.2: Sanity-grep for stragglers**

  ```bash
  grep -n "_updateBgSubPillEnabled\|_syncSubViewDependentControls\|_isBgSubViewActive\|_onBgSubToggle\|bg-sub-toggle\|bg-sub-pill\|bgSubtractedView\|bgSubView\|_bgSubFitInFlight\|_BG_SUB_DEPENDENT_CONTROL_IDS" templates/index.html
  ```

  Confirm the call sites match the design:
  - `_updateBgSubPillEnabled` called from: `_showFitSpinner`, `_hideFitSpinner`, `_onBgTypeChange` (or bg-type onchange), `_restoreUI`, possibly load-path.
  - `_syncSubViewDependentControls` called from: `_onBgSubToggle`, `_onBgTypeChange` (or bg-type onchange), `_restoreUI`.
  - `_isBgSubViewActive` called from: `updatePlot` (data branches), `bgSubZeroLinePlugin`, `_syncSubViewDependentControls`.
  - `_onBgSubToggle` called from: the `<input id="bg-sub-toggle">` onchange only.
  - `bg-sub-toggle`/`bg-sub-pill` referenced inside the helpers and `_restoreUI`.
  - `bgSubtractedView` referenced in `_captureUI`, `_restoreUI`, `_doSaveFit`, `fromJSON`.
  - `bgSubView` is a local `const` inside `updatePlot` only.
  - `_bgSubFitInFlight` referenced only in `_updateBgSubPillEnabled` and the spinner helpers.
  - `_BG_SUB_DEPENDENT_CONTROL_IDS` referenced only in `_syncSubViewDependentControls`.

  Anything not on that list is a stray; investigate.

- [ ] **Step 6.3: JS syntax check**

  ```bash
  python3 -c "
  import re
  html = open('/home/skye/xps-app/templates/index.html').read()
  scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
  open('/tmp/_index_combined.js', 'w').write('\n;\n'.join(scripts))
  "
  node --check /tmp/_index_combined.js && echo "OK syntax"
  ```

  Expected: `OK syntax`.

- [ ] **Step 6.4: Final spec coverage walk**

  Re-read [docs/superpowers/plans/2026-04-26-bkgrd-sub-toggle.md](docs/superpowers/plans/2026-04-26-bkgrd-sub-toggle.md) §Specification end-to-end. For each requirement, point at the task that implements it. Any gap → file a follow-up task before commit.

- [ ] **Step 6.5: Commit**

  ```bash
  git add templates/index.html
  git commit -m "chore(ui): de-duplicate Bkgrd Sub state hooks after _restoreUI integration"
  ```

  (Skip this step if Step 6.1 found nothing to remove.)

---

## Push

- [ ] **Step P.1: Push all commits**

  ```bash
  git push origin main
  ```

  Expected: 5–6 commits land on origin/main (one per task). Tag `pre-bkgrd-sub-toggle` is already pushed (Step 0.1).

---

## Browser verification checklist

Run these AFTER all commits land. Each numbered item maps to spec §Browser verification:

1. **Pill placement.** Open the app fresh. The pill labeled "Bkgrd Sub" appears between "Residuals" and "Invert BE". Visually consistent with adjacent pills.

2. **Disabled — no spectrum.** On page load before any spectrum is dropped, the pill is faded with "Load a spectrum to enable…" tooltip, and not clickable.

3. **Disabled — bg=none.** Load a spectrum, set Background Method dropdown to "None". Pill becomes faded with "Background subtraction is unavailable…" tooltip. Not clickable.

4. **Active state.** Set bg method to "Shirley", click pill. Pill turns blue. Spectrum, peaks (if any), envelope (if a fit exists) all visibly draw from y=0. Background dashed line gone. Y=0 gray reference line visible across the plot area. Y-axis range auto-fits and includes negative values.

5. **Inactive state.** Click pill again. Pill turns gray. Chart returns to today's behavior — full-spectrum data, peaks ride on background, dashed background line visible. (Compare against `git stash`-ed pre-feature build if uncertain.)

6. **Live re-render.** Toggle on/off rapidly. Chart redraws each click; no console errors.

7. **Save/load v1.** Save a fit (`.fit.json`) with toggle ON. Reload page. Drag the file in. Toggle is ON, chart in subtracted view.

8. **Save/load v2 project.** With multiple tabs, save a project (`.proj.json`) with toggle ON on tab A and OFF on tab B (toggle pill, switch tabs, toggle again, save). Reload. Drag in. Confirm switching between tabs flips the pill state correctly.

9. **Old file compat.** Drag in a `.fit.json` from before this feature exists (any older save). No errors. Toggle is OFF.

10. **Disabled during fit.** With toggle ON, click Run Fit. Pill becomes disabled with "fit running" tooltip while the fit runs. Chart stays in subtracted view. After fit completes, pill re-enables, still ON, chart re-renders subtracted with the new fit.

11. **Composition with Invert BE.** Toggle Bkgrd Sub ON, then Invert BE. Both work — x-axis flips while subtracted rendering stays correct.

12. **Composition with Envelope/Individual peaks/Fill peaks.** Toggle each off and on individually while Bkgrd Sub is ON. Each pill's element hides/shows independently.

13. **Negative regions.** Pick a spectrum with noisy ROI endpoints (or one where Shirley undershoots the data). Toggle ON. Negative tail values render below y=0 without clipping. Y=0 line still visible.

14. **No bg → bg → toggle remembered.** With toggle ON, switch bg-type to "None" (pill disables, chart returns to raw). Switch back to "Shirley" — pill re-enables and snaps back to ON; chart snaps back to subtracted.

15. **Empty spectrum.** Drop in a malformed/empty file. Pill stays disabled. No console crash.

16. **Disabled overlays explained.** Open the Tools panel. Toggle Bkgrd Sub ON. The "Savitzky-Golay smooth", "1st derivative", "2nd derivative" checkboxes visibly fade (opacity ~0.4) and become unclickable. Hover one — tooltip reads "Unavailable in subtracted view. Toggle Bkgrd Sub off to enable." Toggle Bkgrd Sub OFF — checkboxes return to full opacity and are interactive again.

If any item fails, revert the implicated commit and investigate before re-pushing.

---

## Self-review

**Spec coverage check** (re-walked the spec §Specification):

- §UI placement: ✓ Task 1.2 (HTML insertion between Residuals and Invert BE).
- §Toggle states (active/inactive/disabled): ✓ Task 1.1 (CSS), Task 2.1 (state machine).
- §Disable activation conditions (bg=none, no spectrum, fit running): ✓ Task 2.1 (`_updateBgSubPillEnabled`), Task 2.2 (fit hook), Task 2.3 (bg-type hook).
- §Disable remembers previous active state: ✓ Task 2.1 — we toggle `pill-toggle.disabled` and `input.disabled` but never mutate `input.checked`, so user's preference survives.
- §Spectrum line subtracted: ✓ Task 3.5.
- §Peak fills from y=0: ✓ Task 3.3.
- §Envelope from y=0: ✓ Task 3.6.
- §Background line hidden: ✓ Task 3.4.
- §Y-axis bounds auto-fit including negatives: ✓ default Chart.js behavior; we don't override.
- §Y=0 reference line: ✓ Task 4.
- §Y-axis label unchanged: ✓ no edit (default already says "Intensity (counts/s)").
- §Hover tooltip plain number: ✓ no edit (existing tooltip uses `item.raw.y.toFixed(1)`, which is the subtracted value when bgSubView is on).
- §Toggle disabled during fit: ✓ Task 2.2.
- §Persistence (.fit.json + .proj.json): ✓ Task 5.
- §Default new tabs OFF / old saves OFF: ✓ Task 1.2 (initial unchecked) + Task 5.4 (`!!data.background.bgSubtractedView`).
- §Independence from other pills: ✓ Task 3 keeps each existing pill's read of its own `<input>.checked`; our branch only changes the y baseline.
- Smoothing / derivative checkboxes visibly disabled in subtracted view (so they don't read as broken): ✓ Task 2.1 (`_syncSubViewDependentControls` helper + `_BG_SUB_DEPENDENT_CONTROL_IDS`), wired from `_onBgSubToggle`, `_onBgTypeChange`, `_restoreUI`. Pattern matches the existing `shirley-iter` / `bg-endpoint-avg` opacity+disabled+title convention.
- §Edge case (no bg computed): ✓ Task 2.1 (covered by `bgType === 'none'` branch and `state.rawBE.length` guard).
- §Edge case (bg method change mid-session): ✓ Task 2.3 (recompute on bg-type change).
- §Edge case (bg recompute in progress): not explicitly handled — matches existing pattern (no other pill handles this either).
- §Edge case (empty/single-point spectrum): ✓ Task 2.1 (`state.rawBE.length < 2` guard).
- §Edge case (bg/spectrum length mismatch): not explicitly handled — would surface as NaNs in the subtracted dataset; existing chart tolerates NaN holes. Defensive behavior matches spec's "disable + log" intent only loosely. If you want the strict log-and-disable, add it in Task 6 — but spec marks this case "should never happen", so I'm not adding code for it by default.

**Placeholder scan**: no "TBD", "implement later", or stub steps. Every code block is the literal source to paste/replace. Every command is exact.

**Type/name consistency**: `bg-sub-toggle` / `bg-sub-pill` / `bgSubtractedView` / `_isBgSubViewActive` / `_onBgSubToggle` / `_updateBgSubPillEnabled` / `_syncSubViewDependentControls` / `_BG_SUB_DEPENDENT_CONTROL_IDS` / `_bgSubFitInFlight` / `bgSubView` (local) / `bgSubZeroLinePlugin` — used consistently across all tasks.

**Scope check**: Single subsystem (chart visualization toggle). Plan does not touch `fitting.py`, `app.py`, the residuals plot, or the figure export, all per spec exclusions. No background calculation changes.

---

## Rollback (from spec)

If the feature breaks something post-merge:

```bash
cd ~/xps-app
git revert pre-bkgrd-sub-toggle..HEAD
git push origin main
ssh root@137.184.183.202 "cd /opt/xps-app && git pull && systemctl restart xps-app"
```
