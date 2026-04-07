# Manual Spline Background + Shirley Iterations Disable

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an interactive "Manual (spline)" background type with draggable anchor points, and grey out the Shirley iterations field for non-Shirley background types.

**Architecture:** A new `"spline"` case is added to `computeBackground()` that reads anchor points from `state.splineAnchors` and interpolates a natural cubic spline. Anchor points are managed via click (add), right-click (remove), and drag (move) interactions on the chart canvas. The backend accepts a pre-computed background array when the method is `"spline"`. All existing background code is untouched.

**Tech Stack:** Chart.js 4.4 (canvas drawing, scale access), vanilla JS cubic spline interpolation, Python/Flask backend.

**CRITICAL CONSTRAINT:** Do NOT modify any existing `shirleyBackground`, `smartBackground`, `linearBackground`, `tougaardBackground` functions, or any existing loading/parsing logic. Only ADD new code.

---

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `templates/index.html` | Modify | All frontend: HTML option, CSS, spline math, interaction, rendering, state management |
| `fitting.py` | Modify | Add `"spline"` case to `run_fit()` that accepts a pre-computed background array |

---

### Task 1: Disable Shirley Iterations for Non-Shirley Types

**Files:**
- Modify: `templates/index.html` (lines ~1351, ~1371, ~4509)

This is a standalone change with no dependencies on the spline feature.

- [ ] **Step 1: Add `_updateShirleyIterState` function**

In `templates/index.html`, find the line `function updateChargeCorrection()` (search for it — currently around line 2712). Insert this new function BEFORE it:

```javascript
function _updateShirleyIterState() {
  const bgType = document.getElementById('bg-type').value;
  const shirleyIter = document.getElementById('shirley-iter');
  const isShirley = (bgType === 'shirley' || bgType === 'smart');
  shirleyIter.disabled = !isShirley;
  shirleyIter.style.opacity = isShirley ? '1' : '0.4';
  shirleyIter.style.pointerEvents = isShirley ? '' : 'none';
}
```

- [ ] **Step 2: Call it from bg-type onchange**

Find the `<select id="bg-type"` element (around line 1351). Change its `onchange` from:

```html
<select id="bg-type" onchange="updatePlot()">
```

to:

```html
<select id="bg-type" onchange="_updateShirleyIterState(); updatePlot()">
```

- [ ] **Step 3: Call it on tab activation**

Find `_restoreUI(ui)` method in the TabManager class (around line 2408). At the very end of the function (after the last DOM value is set), add:

```javascript
if (typeof _updateShirleyIterState === 'function') _updateShirleyIterState();
```

- [ ] **Step 4: Call it on page load**

Find the `document.addEventListener('DOMContentLoaded', ...)` handler (or the initialization block at the bottom of `<script>`). After `tabManager = new TabManager();`, add:

```javascript
_updateShirleyIterState();
```

- [ ] **Step 5: Verify and commit**

Run the JS syntax check:
```bash
python3 -c "
import re
with open('templates/index.html', 'r') as f:
    content = f.read()
scripts = re.findall(r'<script(?![^>]*src)[^>]*>(.*?)</script>', content, re.DOTALL)
main_js = max(scripts, key=len)
with open('/tmp/check_js.js', 'w') as f:
    f.write(main_js)
" && node --check /tmp/check_js.js
```

Test manually: Select "Linear" → Shirley iterations should be greyed out. Select "Shirley" → should be enabled. Switch tabs → state should follow the tab's bg-type.

```bash
git add templates/index.html
git commit -m "Disable Shirley iterations input for non-Shirley background types"
```

---

### Task 2: Natural Cubic Spline Interpolation Function

**Files:**
- Modify: `templates/index.html`

A pure math function with no DOM dependencies. Add it near the existing background functions (after `tougaardBackground`, around line 2749).

- [ ] **Step 1: Add the `cubicSplineInterpolate` function**

Find the line `function computeBackground(be, intensity)` (around line 2751). Insert the following function BEFORE it:

```javascript
// Natural cubic spline interpolation through sorted anchor points.
// anchors: [{be, intensity}, ...] sorted by BE descending (same as spectrum)
// evalBE: array of BE values to evaluate at
// Returns: array of interpolated intensity values at each evalBE point
function cubicSplineInterpolate(anchors, evalBE) {
  if (!anchors || anchors.length < 2) return evalBE.map(() => 0);

  // Sort anchors by BE ascending for spline math
  const pts = anchors.map(a => ({ x: a.be, y: a.intensity }))
    .sort((a, b) => a.x - b.x);
  const n = pts.length;

  // For exactly 2 points, use linear interpolation
  if (n === 2) {
    const [p0, p1] = pts;
    const slope = (p1.y - p0.y) / (p1.x - p0.x || 1e-12);
    return evalBE.map(x => {
      if (x <= p0.x) return p0.y;
      if (x >= p1.x) return p1.y;
      return p0.y + slope * (x - p0.x);
    });
  }

  // Compute h[i] = x[i+1] - x[i]
  const h = [];
  for (let i = 0; i < n - 1; i++) h.push(pts[i + 1].x - pts[i].x || 1e-12);

  // Solve tridiagonal system for natural cubic spline second derivatives (M)
  // M[0] = M[n-1] = 0 (natural boundary conditions)
  const alpha = new Array(n).fill(0);
  for (let i = 1; i < n - 1; i++) {
    alpha[i] = (3 / h[i]) * (pts[i + 1].y - pts[i].y) -
               (3 / h[i - 1]) * (pts[i].y - pts[i - 1].y);
  }

  const l = new Array(n).fill(1);
  const mu = new Array(n).fill(0);
  const z = new Array(n).fill(0);

  for (let i = 1; i < n - 1; i++) {
    l[i] = 2 * (pts[i + 1].x - pts[i - 1].x) - h[i - 1] * mu[i - 1];
    mu[i] = h[i] / l[i];
    z[i] = (alpha[i] - h[i - 1] * z[i - 1]) / l[i];
  }

  const c = new Array(n).fill(0);
  const b = new Array(n).fill(0);
  const d = new Array(n).fill(0);

  for (let j = n - 2; j >= 0; j--) {
    c[j] = z[j] - mu[j] * c[j + 1];
    b[j] = (pts[j + 1].y - pts[j].y) / h[j] - h[j] * (c[j + 1] + 2 * c[j]) / 3;
    d[j] = (c[j + 1] - c[j]) / (3 * h[j]);
  }

  // Evaluate spline at each BE point
  return evalBE.map(x => {
    // Clamp to endpoint values outside the anchor range
    if (x <= pts[0].x) return pts[0].y;
    if (x >= pts[n - 1].x) return pts[n - 1].y;

    // Binary search for the correct interval
    let lo = 0, hi = n - 2;
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      if (pts[mid + 1].x < x) lo = mid + 1;
      else hi = mid;
    }
    const dx = x - pts[lo].x;
    return pts[lo].y + b[lo] * dx + c[lo] * dx * dx + d[lo] * dx * dx * dx;
  });
}
```

- [ ] **Step 2: Verify syntax**

```bash
python3 -c "
import re
with open('templates/index.html', 'r') as f:
    content = f.read()
scripts = re.findall(r'<script(?![^>]*src)[^>]*>(.*?)</script>', content, re.DOTALL)
main_js = max(scripts, key=len)
with open('/tmp/check_js.js', 'w') as f:
    f.write(main_js)
" && node --check /tmp/check_js.js
```

- [ ] **Step 3: Commit**

```bash
git add templates/index.html
git commit -m "Add natural cubic spline interpolation function"
```

---

### Task 3: Anchor Point State Model + "Spline" Background Option

**Files:**
- Modify: `templates/index.html`

- [ ] **Step 1: Add `splineAnchors` to global state**

Find the global `state` object declaration (around line 1313, look for `const state = {` or `state = {`). Add `splineAnchors: [],` inside it.

- [ ] **Step 2: Add `splineAnchors` to tab creation**

Find `createTab(name, be, inten, sourcePath = null)` (around line 1546). In the tab object literal, after `chargeVerified: true,` add:

```javascript
      splineAnchors: [],
```

- [ ] **Step 3: Sync anchors in `_syncActiveToRecord`**

Find `_syncActiveToRecord()` (around line 2072). Inside it, after the line `t.fitResult = state.fitResult;`, add:

```javascript
    t.splineAnchors = state.splineAnchors || [];
```

- [ ] **Step 4: Restore anchors in `activateTab`**

Find `activateTab(id)` (around line 1597). After the line `state.fitResult = tab.fitResult;`, add:

```javascript
    state.splineAnchors = tab.splineAnchors || [];
```

- [ ] **Step 5: Clear anchors when last tab is closed**

Find the zero-tabs branch in `closeTab` (the block `if (this.tabs.length === 0) {`). After `state.ccShift = 0; state.nextId = 1;`, add:

```javascript
      state.splineAnchors = [];
```

- [ ] **Step 6: Add the "Manual (spline)" option to the bg-type select**

Find `<select id="bg-type"` (around line 1351). Add a new option BEFORE the `"none"` option:

```html
<option value="spline" data-tip="Manually place anchor points on the spectrum and interpolate a cubic spline through them. Click to add, right-click to remove, drag to move.">Manual (spline)</option>
```

- [ ] **Step 7: Add `"spline"` case to `computeBackground`**

Find `function computeBackground(be, intensity)` (around line 2751). Inside the function, find the line that checks for the `"none"` case (look for `if (bgType === 'none')`). BEFORE that line, add:

```javascript
  if (bgType === 'spline') {
    if (!state.splineAnchors || state.splineAnchors.length < 2) {
      return Array(be.length).fill(0);
    }
    return cubicSplineInterpolate(state.splineAnchors, be);
  }
```

**CRITICAL:** Do NOT modify any existing if/else branches. Insert this new block before the `"none"` check or as a new `else if` in the chain.

- [ ] **Step 8: Verify syntax and commit**

```bash
python3 -c "
import re
with open('templates/index.html', 'r') as f:
    content = f.read()
scripts = re.findall(r'<script(?![^>]*src)[^>]*>(.*?)</script>', content, re.DOTALL)
main_js = max(scripts, key=len)
with open('/tmp/check_js.js', 'w') as f:
    f.write(main_js)
" && node --check /tmp/check_js.js
```

```bash
git add templates/index.html
git commit -m "Add spline background option, anchor state model, and computeBackground case"
```

---

### Task 4: Anchor Point Chart Interaction (Click/Right-Click/Drag)

**Files:**
- Modify: `templates/index.html`

This is the core interaction system. We add three event listeners to the chart canvas that are active ONLY when bgType is `"spline"`. We reuse the existing coordinate-conversion pattern from `handleChartClick` (lines 3386–3470) and the drag pattern from `_attachDragZoom` (lines 3169–3237).

- [ ] **Step 1: Add the spline interaction IIFE**

Find the end of the `<script>` block (search for `</script>`). Insert the following IIFE BEFORE `</script>`:

```javascript
// ══════════════════════════════════════════════════════════════
// SPLINE BACKGROUND — ANCHOR POINT INTERACTION
// ══════════════════════════════════════════════════════════════
(function() {
  const ANCHOR_RADIUS = 7;  // px — hit detection and visual radius
  let draggingIdx = -1;     // index into state.splineAnchors being dragged

  function _isSplineMode() {
    const sel = document.getElementById('bg-type');
    return sel && sel.value === 'spline';
  }

  function _canvasCoords(e, canvas) {
    const rect = canvas.getBoundingClientRect();
    return { x: e.clientX - rect.left, y: e.clientY - rect.top };
  }

  function _findNearestAnchor(bePx, intPx, chart) {
    // Returns index of nearest anchor within ANCHOR_RADIUS px, or -1
    if (!state.splineAnchors || !chart) return -1;
    const xScale = chart.scales.x, yScale = chart.scales.y;
    let bestIdx = -1, bestDist = ANCHOR_RADIUS + 1;
    for (let i = 0; i < state.splineAnchors.length; i++) {
      const a = state.splineAnchors[i];
      const ax = xScale.getPixelForValue(a.be);
      const ay = yScale.getPixelForValue(a.intensity);
      const dist = Math.sqrt((bePx - ax) ** 2 + (intPx - ay) ** 2);
      if (dist < bestDist) { bestDist = dist; bestIdx = i; }
    }
    return bestIdx;
  }

  // ── Left-click: add anchor or start drag ──
  document.addEventListener('mousedown', function(e) {
    if (!_isSplineMode() || !state.chart || e.button !== 0) return;
    const canvas = document.getElementById('mainChart');
    if (e.target !== canvas) return;

    // Don't interfere with place mode
    if (typeof placeMode !== 'undefined' && placeMode) return;

    const { x, y } = _canvasCoords(e, canvas);
    const chart = state.chart;
    const xScale = chart.scales.x, yScale = chart.scales.y;

    // Only handle clicks inside the chart area
    if (x < xScale.left || x > xScale.right || y < yScale.top || y > yScale.bottom) return;

    // Check if clicking near an existing anchor (start drag)
    const nearIdx = _findNearestAnchor(x, y, chart);
    if (nearIdx >= 0) {
      draggingIdx = nearIdx;
      e.preventDefault();
      document.body.style.cursor = 'grabbing';
      return;
    }

    // Add new anchor point at click location
    const be = xScale.getValueForPixel(x);
    const intensity = yScale.getValueForPixel(y);
    state.splineAnchors.push({ be, intensity });
    updatePlot();
  });

  // ── Mousemove: drag anchor ──
  document.addEventListener('mousemove', function(e) {
    if (draggingIdx < 0 || !state.chart) return;
    const canvas = document.getElementById('mainChart');
    const { x, y } = _canvasCoords(e, canvas);
    const xScale = state.chart.scales.x, yScale = state.chart.scales.y;

    // Clamp to chart area
    const cx = Math.max(xScale.left, Math.min(xScale.right, x));
    const cy = Math.max(yScale.top, Math.min(yScale.bottom, y));

    state.splineAnchors[draggingIdx] = {
      be: xScale.getValueForPixel(cx),
      intensity: yScale.getValueForPixel(cy)
    };
    updatePlot();
  });

  // ── Mouseup: end drag ──
  document.addEventListener('mouseup', function(e) {
    if (draggingIdx >= 0) {
      draggingIdx = -1;
      document.body.style.cursor = '';
    }
  });

  // ── Right-click: remove nearest anchor ──
  document.addEventListener('contextmenu', function(e) {
    if (!_isSplineMode() || !state.chart) return;
    const canvas = document.getElementById('mainChart');
    if (e.target !== canvas) return;

    const { x, y } = _canvasCoords(e, canvas);
    const chart = state.chart;
    const xScale = chart.scales.x, yScale = chart.scales.y;

    if (x < xScale.left || x > xScale.right || y < yScale.top || y > yScale.bottom) return;

    const nearIdx = _findNearestAnchor(x, y, chart);
    if (nearIdx >= 0) {
      e.preventDefault();
      state.splineAnchors.splice(nearIdx, 1);
      updatePlot();
    }
  });

  // ── Cursor feedback: show 'grab' when hovering an anchor in spline mode ──
  document.addEventListener('mousemove', function(e) {
    if (!_isSplineMode() || !state.chart || draggingIdx >= 0) return;
    const canvas = document.getElementById('mainChart');
    if (e.target !== canvas) return;

    const { x, y } = _canvasCoords(e, canvas);
    const nearIdx = _findNearestAnchor(x, y, state.chart);
    canvas.style.cursor = nearIdx >= 0 ? 'grab' : 'crosshair';
  });
})();
```

- [ ] **Step 2: Set crosshair cursor when spline mode is active**

Find the `_updateShirleyIterState` function (added in Task 1). Add to its end, AFTER the existing lines:

```javascript
  // Set chart cursor for spline mode
  const canvas = document.getElementById('mainChart');
  if (canvas) canvas.style.cursor = (bgType === 'spline') ? 'crosshair' : '';
```

- [ ] **Step 3: Disable drag-zoom when in spline mode**

The existing `_attachDragZoom` function checks `_dragZoomEnabled` (line 3112). We need to disable drag-zoom when spline mode is active to prevent conflicts. Find the `_updateShirleyIterState` function again. Add:

```javascript
  if (typeof _dragZoomEnabled !== 'undefined') {
    // Don't disable if placeMode is active (placeMode already controls this)
    if (!placeMode) _dragZoomEnabled = (bgType !== 'spline');
  }
```

- [ ] **Step 4: Verify syntax and commit**

```bash
python3 -c "
import re
with open('templates/index.html', 'r') as f:
    content = f.read()
scripts = re.findall(r'<script(?![^>]*src)[^>]*>(.*?)</script>', content, re.DOTALL)
main_js = max(scripts, key=len)
with open('/tmp/check_js.js', 'w') as f:
    f.write(main_js)
" && node --check /tmp/check_js.js
```

```bash
git add templates/index.html
git commit -m "Add spline anchor point interaction: click/drag/right-click"
```

---

### Task 5: Anchor Point Visual Rendering

**Files:**
- Modify: `templates/index.html`

Draw anchor points as circles on the chart, and add CSS for a hint label.

- [ ] **Step 1: Add `_drawSplineAnchors` function**

Find the `_drawSourceLabel` function (around line 6046). Insert the following function BEFORE it:

```javascript
// Draw spline background anchor points as draggable circles
function _drawSplineAnchors(chart) {
  const bgType = document.getElementById('bg-type')?.value;
  if (bgType !== 'spline' || !state.splineAnchors || !state.splineAnchors.length) return;
  const { ctx, chartArea, scales } = chart;
  if (!chartArea || !scales.x || !scales.y) return;

  const isLight = document.body.classList.contains('light-theme');
  const fillColor = isLight ? 'rgba(37,99,235,0.85)' : 'rgba(96,165,250,0.9)';
  const strokeColor = isLight ? '#1e40af' : '#ffffff';

  ctx.save();
  for (const a of state.splineAnchors) {
    const x = scales.x.getPixelForValue(a.be);
    const y = scales.y.getPixelForValue(a.intensity);
    if (x < chartArea.left || x > chartArea.right) continue;

    ctx.beginPath();
    ctx.arc(x, y, 6, 0, Math.PI * 2);
    ctx.fillStyle = fillColor;
    ctx.fill();
    ctx.strokeStyle = strokeColor;
    ctx.lineWidth = 1.5;
    ctx.stroke();
  }

  // Draw instruction text if fewer than 2 anchors
  if (state.splineAnchors.length < 2) {
    const msg = state.splineAnchors.length === 0
      ? 'Click on the spectrum to place background anchor points'
      : 'Place at least one more anchor point';
    ctx.font = "13px 'IBM Plex Mono', monospace";
    ctx.fillStyle = isLight ? 'rgba(0,0,0,0.5)' : 'rgba(255,255,255,0.5)';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(msg, (chartArea.left + chartArea.right) / 2, (chartArea.top + chartArea.bottom) / 2);
  }
  ctx.restore();
}
```

- [ ] **Step 2: Register in the overlay plugin**

Find the `overlayPlugin` definition in `updatePlot()` (search for `id: 'xpsOverlays'`). Add the call inside `afterDraw`:

```javascript
    afterDraw(chart) {
      _drawNistMarkers(chart);
      _drawHistoryPreview(chart);
      _drawSourceLabel(chart);
      _drawSplineAnchors(chart);   // ← add this line
    }
```

- [ ] **Step 3: Verify syntax and commit**

```bash
python3 -c "
import re
with open('templates/index.html', 'r') as f:
    content = f.read()
scripts = re.findall(r'<script(?![^>]*src)[^>]*>(.*?)</script>', content, re.DOTALL)
main_js = max(scripts, key=len)
with open('/tmp/check_js.js', 'w') as f:
    f.write(main_js)
" && node --check /tmp/check_js.js
```

```bash
git add templates/index.html
git commit -m "Add visual rendering of spline anchor points on chart"
```

---

### Task 6: Backend — Accept Pre-Computed Spline Background

**Files:**
- Modify: `fitting.py`

When the frontend uses spline background, the backend cannot compute it (it doesn't have the anchor points or the spline math). Instead, the frontend will send the pre-computed background array. We add a `"spline"` case to the backend that uses this array directly.

- [ ] **Step 1: Add `"spline"` case to `run_fit()` in `fitting.py`**

Find the background method selection in `run_fit()` (around line 616–626, look for `if background_method == 'shirley':`). Add the `"spline"` case BEFORE the `else: raise ValueError(...)`:

```python
    elif background_method == 'spline':
        # Frontend sends pre-computed spline background array
        manual_bg = kwargs.get('manual_bg')
        if manual_bg is not None and len(manual_bg) == len(y):
            bg = np.array(manual_bg, dtype=float)
        else:
            # Fallback: zero background if array not provided or wrong length
            bg = np.zeros_like(y)
```

- [ ] **Step 2: Pass `manual_bg` from the Flask route**

Find the `/api/fit` route in `app.py` (around line 346–404). Look for where `run_fit()` is called. Add `manual_bg` to the keyword arguments. Find the line that looks like:

```python
result = run_fit(energy, intensity, peaks, ...)
```

Before this call, extract the manual bg from the request:

```python
    manual_bg = bg_cfg.get("manual_bg")
```

Then pass it through to `run_fit`:

Find the `run_fit(...)` call and add `manual_bg=manual_bg` to the keyword arguments.

- [ ] **Step 3: Accept `manual_bg` in `run_fit()` signature**

Find the `def run_fit(` signature in `fitting.py`. Add `manual_bg=None` to the keyword parameters. It should look like:

```python
def run_fit(energy, intensity, peak_specs, ..., manual_bg=None):
```

And pass it through the kwargs dict that reaches the background selection code. Find where `background_method` is read and where `kwargs` is used — the `manual_bg` value needs to be accessible where the `"spline"` case was added.

If `run_fit` doesn't use `**kwargs`, add `manual_bg` as a named parameter and reference it directly in the `elif background_method == 'spline':` block:

```python
    elif background_method == 'spline':
        if manual_bg is not None and len(manual_bg) == len(y):
            bg = np.array(manual_bg, dtype=float)
        else:
            bg = np.zeros_like(y)
```

- [ ] **Step 4: Send spline background from frontend**

Back in `templates/index.html`, find `runFit()` (around line 4001). Find where the `fitReq` object is constructed (the `const fitReq = {` block). After the `background:` property, add the pre-computed spline BG if applicable:

Find the existing background property in `fitReq`:
```javascript
      background: { method: bgType, start_idx: bgStartIdx, end_idx: bgEndIdx },
```

Replace it with:

```javascript
      background: {
        method: bgType, start_idx: bgStartIdx, end_idx: bgEndIdx,
        ...(bgType === 'spline' ? { manual_bg: Array.from(bgIntensity) } : {})
      },
```

Note: `bgIntensity` is already computed at line 4010 via `computeBackground(be, inten)` which will use the spline when `bgType === 'spline'`. This sends the frontend-computed spline background array to the backend so it doesn't need to recompute it.

- [ ] **Step 5: Verify Python syntax**

```bash
python3 -c "import ast; ast.parse(open('fitting.py').read()); print('OK')"
```

- [ ] **Step 6: Verify JS syntax and commit**

```bash
python3 -c "
import re
with open('templates/index.html', 'r') as f:
    content = f.read()
scripts = re.findall(r'<script(?![^>]*src)[^>]*>(.*?)</script>', content, re.DOTALL)
main_js = max(scripts, key=len)
with open('/tmp/check_js.js', 'w') as f:
    f.write(main_js)
" && node --check /tmp/check_js.js
```

```bash
git add templates/index.html fitting.py app.py
git commit -m "Backend: accept pre-computed spline background array for fitting"
```

---

### Task 7: Save/Load Persistence for Spline Anchors

**Files:**
- Modify: `templates/index.html`

Ensure spline anchors survive save/load and tab propagation.

- [ ] **Step 1: Include anchors in project save**

Find `const buildTabData = (t) => ({` in `_doSaveProject()` (around line 4755). Add after the `ui: {...t.ui},` line:

```javascript
    splineAnchors: t.splineAnchors || [],
```

- [ ] **Step 2: Include anchors in spectrum save**

Find `const data = {` in `_doSaveSpectrum()` (around line 4711). Add after `ui: {...tab.ui},`:

```javascript
    splineAnchors: tab.splineAnchors || [],
```

- [ ] **Step 3: Restore anchors from project load**

Find `_loadProjectJSON(data, sessionFile)` (around line 4875). In the tab object construction, after `chargeVerified:`, add:

```javascript
      splineAnchors: t.splineAnchors || [],
```

- [ ] **Step 4: Restore anchors from spectrum load**

Find `_loadSpectrumFile(data, sessionFile)` (around line 4843). After the line that sets `active.fitResult`, add:

```javascript
  active.splineAnchors = data.splineAnchors || [];
  state.splineAnchors = active.splineAnchors;
```

- [ ] **Step 5: Include anchors in batch propagation**

Find `runPropagation()` (around line 5764). After the line `tgt.ccShift = sourceTab.ccShift;`, add:

```javascript
    // Propagate spline anchors if source uses spline background
    if (srcUi.bgType === 'spline') {
      tgt.splineAnchors = JSON.parse(JSON.stringify(sourceTab.splineAnchors || []));
    }
```

- [ ] **Step 6: Include anchors in `toJSON` / `fromJSON` for fit files**

Find `toJSON()` in TabManager (around line 1689). In the object returned for tabs, ensure `splineAnchors` is included. Find the line that has `ccShift: t.ccShift,` in the tab serialization and add after it:

```javascript
        splineAnchors: t.splineAnchors || [],
```

Find `fromJSON(data)` in TabManager. After `active.peaks = state.peaks;`, add:

```javascript
      if (data.splineAnchors) {
        state.splineAnchors = data.splineAnchors;
        active.splineAnchors = state.splineAnchors;
      }
```

- [ ] **Step 7: Verify syntax and commit**

```bash
python3 -c "
import re
with open('templates/index.html', 'r') as f:
    content = f.read()
scripts = re.findall(r'<script(?![^>]*src)[^>]*>(.*?)</script>', content, re.DOTALL)
main_js = max(scripts, key=len)
with open('/tmp/check_js.js', 'w') as f:
    f.write(main_js)
" && node --check /tmp/check_js.js
```

```bash
git add templates/index.html
git commit -m "Persist spline anchor points in save/load, propagation, and tab state"
```

---

### Task 8: Integration Testing and Polish

**Files:**
- Modify: `templates/index.html` (minor adjustments if needed)

- [ ] **Step 1: Manual integration test — spline background**

1. Load a spectrum (drag a .vgd or .csv file)
2. Select "Manual (spline)" from background type dropdown
3. Verify: Shirley iterations field is greyed out
4. Verify: Chart cursor changes to crosshair
5. Click 3-4 points on the spectrum to define background anchors
6. Verify: Blue circles appear at each click location
7. Verify: Background curve (dashed grey) passes through the anchor points
8. Drag an anchor point — background should update in real-time
9. Right-click an anchor — it should be removed
10. Click "Run Fit" — fit should work using the spline background

- [ ] **Step 2: Manual integration test — Shirley iterations**

1. Select "Shirley (iterative)" — iterations field should be enabled (full opacity)
2. Select "Smart (constrained Shirley)" — iterations field should be enabled
3. Select "Linear" — iterations field should be greyed out and non-interactive
4. Select "Manual (spline)" — iterations field should be greyed out
5. Select "None" — iterations field should be greyed out
6. Switch between tabs — each tab's Shirley iteration state should be correct

- [ ] **Step 3: Manual integration test — persistence**

1. Set up a spline background with 4 anchor points
2. Switch to another tab, then switch back — anchors should reappear
3. Save as project (Save Project)
4. Reload page, load project — anchors should be restored
5. Select "Linear" to switch away from spline — anchors should be hidden but preserved
6. Select "Manual (spline)" again — anchors should reappear

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "Manual spline background and Shirley iterations disable — complete"
```

---

## Verification Checklist

- [ ] `shirleyBackground` function: NOT modified
- [ ] `smartBackground` function: NOT modified
- [ ] `linearBackground` function: NOT modified
- [ ] `tougaardBackground` function: NOT modified
- [ ] `_filterFiles` function: NOT modified
- [ ] `_loadOneFile` function: NOT modified
- [ ] `loadFile` function: NOT modified
- [ ] `parseCSV` / `parseXLSX` / `parseVGD`: NOT modified
- [ ] Existing `computeBackground` cases (shirley/smart/linear/tougaard/none): NOT modified — only a new `"spline"` case added
- [ ] All existing background types still work exactly as before
