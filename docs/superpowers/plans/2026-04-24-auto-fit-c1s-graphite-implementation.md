# Auto-Fit C1s Graphite — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a single-action "Auto-Fit C1s Graphite" Actions-menu entry that produces a complete C1s fit and applies charge correction from the fitted graphite peak, calling the existing `/api/fit` endpoint exactly once.

**Architecture:** One orchestrator (`runAutoFitC1sGraphite`) + five small named helpers (`isC1sTab`, `findGraphiteRawBE`, `assessLowBERegion`, `buildAutoFitModel`, `applyAutoFitResult`) + one menu entry + one confirmation modal. Reuses every existing piece of fit infrastructure (`uploadToBackend`, `peakToBackendSpec`, `applyBackendResult`, `pushUndo`, `_showFitSpinner`, `_autoSnapshot`, `updateChargeCorrection`, `notify`). No backend changes.

**Tech Stack:** Vanilla JS + inline HTML/CSS in `templates/index.html`; Python 3 (lmfit) backend via the existing `/api/fit` endpoint, unchanged.

---

## Spec source

This plan implements the spec at `docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite.md`. The plan does not relitigate scope decisions; refer to the spec for the rationale behind every choice (Actions menu vs toolbar, 4 vs 3 adventitious peaks, no FWHM linking, etc.).

## Sign-convention callout (READ BEFORE CODING)

The XPS app stores `state.ccShift` such that `getCorrectedBE()` returns `raw_BE − state.ccShift` (see `templates/index.html:3413`). That is **opposite** to the spec's narrative convention `corrected = raw + shift`. Every formula in the plan uses the **app convention**:

| Quantity | Spec (narrative) | App (USE THIS) |
|---|---|---|
| Provisional shift after step 1 | `284.50 − graphite_raw_BE` | `state.ccShift = graphite_raw_BE − 284.50` |
| Convert corrected → raw | `raw = corrected − shift` | `raw = corrected + state.ccShift` |
| Final shift after fit | `284.50 − graphite_fitted_raw_center` | `state.ccShift = graphite_fitted_raw_center − 284.50` |
| `cc-shift-display` text | `+(284.50 − graphite_raw)` | `−state.ccShift`, formatted with sign |

The existing `updateChargeCorrection()` at `templates/index.html:3346-3411` already does the right thing under the app convention when fed `cc-method='c1s'`, `cc-obs=graphite_raw_BE`, `cc-lit=284.50`: it sets `state.ccShift = obs − 284.50`, shifts ROI/bg DOM fields and peak centers by the delta, and updates the shift display. The plan drives the auto-fit's charge correction through that function so the entire frame stays self-consistent.

## Spec ambiguity to flag (resolution baked into plan)

The spec specifies (success path):
```
state.ccShift = final_shift             ← derived from graphite_fitted_raw
state.ccObs   = graphite_raw_BE         ← the initial detection, NOT the fitted value
```

These two are **internally inconsistent** under c1s charge correction. If the user later inspects or edits the cc panel, the relation `state.ccShift = state.ccObs − state.ccLit` will not hold — they differ by the post-fit refinement (typically ~0.05 eV).

**Plan resolution:** set `state.ccObs = graphite_fitted_raw_center` so the cc panel is self-consistent. The fitted raw position is the more accurate observation anyway. If the user prefers the literal spec wording, they can ask for a change before execution.

## Scope / Non-Goals

- **No** changes to `fitting.py` or `app.py`.
- **No** new endpoints, no new backend parameters.
- **No** changes to `runFit`, `runFitLocal`, `showPropagateModal`, `runPropagation`, save/load, history.
- **No** variant chooser, no 3-vs-4 comparison, no quality flags.
- **No** batch support, no review queue, no learning from prior fits.
- **No** client-side fitting; every fit goes through `/api/fit`.
- **No** new lineshape types — uses existing `LA` and `GL` (pseudo-Voigt) shapes.

---

## File structure

| File | Responsibility |
|---|---|
| `templates/index.html` | All UI, all logic, all helpers — single-file project convention. |

New JS symbols all prefixed `_af` except the public entry points: `runAutoFitC1sGraphite`, `isC1sTab`, `findGraphiteRawBE`, `assessLowBERegion`, `buildAutoFitModel`, `applyAutoFitResult`. New DOM ids prefixed `auto-fit-c1s-…` or `af-…`.

---

## Testing strategy

The project has **no JS test harness** (no Jest, no Mocha). Verification is layered:

1. **Structural grep checks** after every task — assert function/identifier/DOM-id presence, brace balance.
2. **Python-port unit tests** for the three pure-logic helpers (`isC1sTab`, `findGraphiteRawBE`, `assessLowBERegion`). Each helper's algorithm is short and deterministic; the plan re-implements it in Python on a synthetic input and compares to expected output. This catches off-by-one and threshold bugs without spinning up a browser.
3. **End-to-end Python harness** (Task 12) that POSTs a representative C1s spectrum + the auto-fit peak model to `/api/fit` and checks: success=true, graphite center within ±0.3 of 284.50, all peak amplitudes finite. Runs against the live `127.0.0.1:5000` server.
4. **Browser manual checklist** (Task 13) covering all six test scenarios listed in the spec, plus undo, spinner appearance, and the 120-second abort path. Written in plain language for the user to walk through.

Every task ends with `git commit` so the history is bisectable if a regression appears.

---

## Task 1: `isC1sTab(tab)` helper + Python port test

**Files:**
- Modify: `templates/index.html` — insert near the other tab-classification helpers. A clean insertion point is **immediately after** the closing `}` of `tabManager.activateTab` (currently around line 2050), inside the same `<script>` block but **outside the tabManager class** so it can be called from anywhere. Concretely: insert just before the line `closeTab(id) {` in the tabManager class — no wait, it should be a free function. The clean insertion point is after the tabManager class definition closes (look for `} // end TabManager` or the `}` that ends the class). For the executor: place it directly before `function runFit()` (around line 4554), with the other top-level utility functions.

- [ ] **Step 1: Write the function**

Insert before `async function runFit() {`:

```js
// Returns true if the tab is a C1s spectrum, defined by ROI midpoint
// in [270.0, 315.0] eV. Uses the tab's persisted UI ROI fields (which
// are corrected-BE values), falling back to the current rawBE range.
// Reads from a tab record, not state, so it works for inactive tabs.
function isC1sTab(tab) {
  if (!tab || !tab.rawBE || !tab.rawBE.length) return false;
  const ui = tab.ui || {};
  let lo = parseFloat(ui.roiMin);
  let hi = parseFloat(ui.roiMax);
  if (!Number.isFinite(lo) || !Number.isFinite(hi)) {
    // Fall back to full raw range (no UI ROI set yet)
    let rmin = Infinity, rmax = -Infinity;
    for (const v of tab.rawBE) {
      if (v < rmin) rmin = v;
      if (v > rmax) rmax = v;
    }
    lo = rmin; hi = rmax;
  }
  if (!Number.isFinite(lo) || !Number.isFinite(hi)) return false;
  const mid = (lo + hi) / 2;
  return mid >= 270.0 && mid <= 315.0;
}
```

- [ ] **Step 2: Python-port unit test**

```bash
venv/bin/python - <<'PY'
def is_c1s(tab):
    if not tab or not tab.get('rawBE'): return False
    ui = tab.get('ui', {}) or {}
    try: lo = float(ui.get('roiMin'))
    except (TypeError, ValueError): lo = None
    try: hi = float(ui.get('roiMax'))
    except (TypeError, ValueError): hi = None
    if lo is None or hi is None:
        be = tab['rawBE']
        lo, hi = min(be), max(be)
    mid = (lo + hi) / 2
    return 270.0 <= mid <= 315.0

# Inside C1s window
assert is_c1s({'rawBE':[270, 300], 'ui':{'roiMin':'278','roiMax':'295'}}) is True
# Edge of window — both endpoints inclusive
assert is_c1s({'rawBE':[260, 320], 'ui':{'roiMin':'270','roiMax':'270'}}) is True
assert is_c1s({'rawBE':[260, 320], 'ui':{'roiMin':'315','roiMax':'315'}}) is True
# Outside (U 4f range mid ≈ 392)
assert is_c1s({'rawBE':[370, 415], 'ui':{'roiMin':'375','roiMax':'410'}}) is False
# Outside (Cl 2p range mid ≈ 200)
assert is_c1s({'rawBE':[195, 210], 'ui':{'roiMin':'196','roiMax':'205'}}) is False
# Empty tab
assert is_c1s({'rawBE':[]}) is False
assert is_c1s(None) is False
# Falls back to rawBE range when ui ROI absent
assert is_c1s({'rawBE':[280, 295]}) is True
assert is_c1s({'rawBE':[100, 110]}) is False
print('isC1sTab: ok')
PY
```

Expected: `isC1sTab: ok`

- [ ] **Step 3: Structural check**

```
grep -n 'function isC1sTab' templates/index.html
```

Expected: exactly one match.

- [ ] **Step 4: Commit**

```bash
git add templates/index.html
git commit -m "feat(autofit): isC1sTab helper (ROI midpoint in 270–315 eV)"
```

---

## Task 2: Actions-menu entry + disabled-item CSS

**Files:**
- Modify: `templates/index.html:1404-1408` (between Export Table (XLSX) and the divider before Load Fit)
- Modify: `templates/index.html` — append a CSS rule near the existing `.save-dropdown-item` rules (around line 600).

The entry sits in its own visual section. The plan inserts it between the Export-Table block and the second divider so it's visually grouped with the actionable workflow tools, distinct from save/load.

- [ ] **Step 1: Add the menu item HTML**

Find:

```html
          <button class="save-dropdown-item" onclick="exportFitTable('xlsx')"><span class="dd-icon">&#128202;</span><div>Export Table (XLSX)<small>All fit parameters</small></div></button>
          <div style="height:1px;background:var(--border);margin:4px 0"></div>
```

Replace with:

```html
          <button class="save-dropdown-item" onclick="exportFitTable('xlsx')"><span class="dd-icon">&#128202;</span><div>Export Table (XLSX)<small>All fit parameters</small></div></button>
          <div style="height:1px;background:var(--border);margin:4px 0"></div>
          <button class="save-dropdown-item" id="auto-fit-c1s-menu-item" onclick="runAutoFitC1sGraphite()" title="Available only on C1s spectra (ROI midpoint 270–315 eV)"><span class="dd-icon">&#128293;</span><div>Auto-Fit C1s Graphite<small>One-click fit + charge correction</small></div></button>
          <div style="height:1px;background:var(--border);margin:4px 0"></div>
```

- [ ] **Step 2: Add the disabled-state CSS**

Find the existing `.save-dropdown-item:hover` rule (line ~617) and insert directly after it:

```css
  .save-dropdown-item:disabled,
  .save-dropdown-item[aria-disabled="true"] {
    opacity: 0.4;
    cursor: not-allowed;
    pointer-events: none;
  }
```

- [ ] **Step 3: Verify**

```
grep -c 'id="auto-fit-c1s-menu-item"' templates/index.html
```

Expected: `1`

```
grep -c '\.save-dropdown-item:disabled' templates/index.html
```

Expected: `1`

- [ ] **Step 4: Commit**

```bash
git add templates/index.html
git commit -m "feat(autofit): Actions-menu entry + disabled-item CSS"
```

---

## Task 3: Live menu enable/disable wiring

**Files:**
- Modify: `templates/index.html` — add `_recomputeAutoFitMenuState()` near the `isC1sTab` definition.
- Modify: `templates/index.html:1532, 1536` — extend the `oninput` of `#roi-min` and `#roi-max` to call the recompute.
- Modify: `templates/index.html:2007-2050` — add a call inside `tabManager.activateTab` after state is swapped.
- Modify: `templates/index.html` — call once at startup so the menu state is correct on load.

- [ ] **Step 1: Add the recompute function**

Insert directly after `function isC1sTab(tab) { ... }`:

```js
// Sync the Auto-Fit menu item's disabled state with the active tab.
// Called from activateTab and from ROI-input event handlers.
function _recomputeAutoFitMenuState() {
  const item = document.getElementById('auto-fit-c1s-menu-item');
  if (!item) return;
  const tab = (typeof tabManager !== 'undefined' && tabManager.activeId)
    ? tabManager._getTab(tabManager.activeId)
    : null;
  const enabled = !!tab && isC1sTab(tab);
  item.disabled = !enabled;
  if (enabled) {
    item.removeAttribute('aria-disabled');
    item.title = 'Auto-Fit C1s Graphite — one-click fit + charge correction';
  } else {
    item.setAttribute('aria-disabled', 'true');
    item.title = 'Auto-Fit C1s Graphite is only available for C1s spectra (ROI midpoint 270–315 eV).';
  }
}
```

- [ ] **Step 2: Wire `tabManager.activateTab`**

Find inside `activateTab` (around line 2042, after `this._updateInfoBadge(tab);`):

```js
    this._updateInfoBadge(tab);
```

Insert directly after:

```js
    this._updateInfoBadge(tab);
    if (typeof _recomputeAutoFitMenuState === 'function') _recomputeAutoFitMenuState();
```

- [ ] **Step 3: Wire ROI inputs**

Find at line 1532:

```html
                <input type="number" id="roi-min" value="706" step="0.5" oninput="updatePlot()">
```

Replace with:

```html
                <input type="number" id="roi-min" value="706" step="0.5" oninput="updatePlot();_recomputeAutoFitMenuState()">
```

Find at line 1536:

```html
                <input type="number" id="roi-max" value="726" step="0.5" oninput="updatePlot()">
```

Replace with:

```html
                <input type="number" id="roi-max" value="726" step="0.5" oninput="updatePlot();_recomputeAutoFitMenuState()">
```

- [ ] **Step 4: One-shot startup call**

Find the startup sequence (search for `// Initialize` or look for `tabManager.renderTabBar` near the bottom of the script). Add `_recomputeAutoFitMenuState()` at the end of startup. A safe, late-binding location is at the very end of the inline script's last IIFE; if uncertain, place a call inside a `DOMContentLoaded` listener:

```js
// Late-init for Auto-Fit menu state (in case startup runs before the
// menu item is in the DOM).
window.addEventListener('DOMContentLoaded', () => {
  if (typeof _recomputeAutoFitMenuState === 'function') _recomputeAutoFitMenuState();
});
```

Insert this block immediately after the `function _recomputeAutoFitMenuState()` definition.

- [ ] **Step 5: Verify**

```
grep -c '_recomputeAutoFitMenuState()' templates/index.html
```

Expected: `4` (one declaration call inside `activateTab`, two `oninput` chains, one DOMContentLoaded).

```
grep -c 'function _recomputeAutoFitMenuState' templates/index.html
```

Expected: `1`

- [ ] **Step 6: Commit**

```bash
git add templates/index.html
git commit -m "feat(autofit): live enable/disable on tab change and ROI edit"
```

---

## Task 4: Confirmation modal HTML

**Files:**
- Modify: `templates/index.html` — append a new modal directly after the `#localfit-warn-overlay` block (find by `id="localfit-warn-overlay"`).
- Modify: `templates/index.html` — add `_showAutoFitConfirmModal(peakCount)` near the other modal helpers.

- [ ] **Step 1: Add the modal HTML**

Find the closing `</div>` of `#localfit-warn-overlay` (line ~8120 region). Insert after that block:

```html

<!-- Auto-Fit C1s Graphite — replace-existing-peaks confirmation -->
<div id="auto-fit-c1s-confirm-overlay" class="xps-modal-overlay" onclick="if(event.target===this)this.classList.remove('open')">
  <div class="xps-modal" style="max-width:440px">
    <h3>Auto-Fit will replace existing peaks
      <button class="btn btn-sm" onclick="_autoFitConfirmCancel()">&#x2715;</button>
    </h3>
    <p style="font-size:11px;color:var(--text2);line-height:1.5;margin:0 0 14px">
      This tab has <span id="auto-fit-c1s-confirm-count">0</span> peak(s) and a fit result.
      Auto-Fit will clear them and run a fresh fit. Continue?
    </p>
    <div class="dialog-btns">
      <button class="btn" onclick="_autoFitConfirmCancel()">Cancel</button>
      <button class="btn btn-accent" id="auto-fit-c1s-confirm-proceed">Proceed</button>
    </div>
  </div>
</div>
```

- [ ] **Step 2: Add the promise-based modal helpers**

Insert near the auto-fit logic (e.g., directly after `_recomputeAutoFitMenuState`):

```js
// Returns a Promise<boolean> — true if user clicks Proceed, false on Cancel/X.
let _autoFitConfirmResolver = null;
function _showAutoFitConfirmModal(peakCount) {
  return new Promise(resolve => {
    _autoFitConfirmResolver = resolve;
    const span = document.getElementById('auto-fit-c1s-confirm-count');
    if (span) span.textContent = String(peakCount);
    const proceed = document.getElementById('auto-fit-c1s-confirm-proceed');
    proceed.onclick = () => {
      document.getElementById('auto-fit-c1s-confirm-overlay').classList.remove('open');
      const r = _autoFitConfirmResolver; _autoFitConfirmResolver = null;
      if (r) r(true);
    };
    document.getElementById('auto-fit-c1s-confirm-overlay').classList.add('open');
  });
}
function _autoFitConfirmCancel() {
  document.getElementById('auto-fit-c1s-confirm-overlay').classList.remove('open');
  const r = _autoFitConfirmResolver; _autoFitConfirmResolver = null;
  if (r) r(false);
}
```

- [ ] **Step 3: Verify**

```
grep -c 'id="auto-fit-c1s-confirm-overlay"\|id="auto-fit-c1s-confirm-count"\|id="auto-fit-c1s-confirm-proceed"' templates/index.html
```

Expected: `3`

```
grep -c 'function _showAutoFitConfirmModal\|function _autoFitConfirmCancel' templates/index.html
```

Expected: `2`

- [ ] **Step 4: Commit**

```bash
git add templates/index.html
git commit -m "feat(autofit): replace-existing-peaks confirmation modal"
```

---

## Task 5: `findGraphiteRawBE` helper + Python port test

**Files:**
- Modify: `templates/index.html` — append after `isC1sTab`.

- [ ] **Step 1: Write the helper**

```js
// Find graphite in the raw-BE frame from a background-subtracted spectrum.
//   rawBE      : array of raw BE values (state.rawBE, NOT corrected)
//   bgSubInten : background-subtracted intensity at the same indices
// Returns the BE of the highest-BE strong local maximum, or null.
//
// Algorithm (matches spec §1):
//   1. Find all strict local maxima of bgSubInten (3-point test).
//   2. Filter to "strong" maxima: bgSubInten[i] >= 0.30 * max(bgSubInten).
//   3. Pick the one with the highest rawBE value.
function findGraphiteRawBE(rawBE, bgSubInten) {
  const n = rawBE && rawBE.length;
  if (!n || n !== bgSubInten.length || n < 3) return null;
  let gMax = -Infinity;
  for (const v of bgSubInten) if (v > gMax) gMax = v;
  if (!(gMax > 0)) return null;
  const threshold = 0.30 * gMax;
  const strong = []; // array of {be, intensity}
  for (let i = 1; i < n - 1; i++) {
    if (bgSubInten[i] < threshold) continue;
    if (bgSubInten[i] >= bgSubInten[i - 1] && bgSubInten[i] >= bgSubInten[i + 1]) {
      strong.push({ be: rawBE[i], intensity: bgSubInten[i] });
    }
  }
  if (!strong.length) return null;
  // Highest-BE strong maximum
  let best = strong[0];
  for (const c of strong) if (c.be > best.be) best = c;
  return best.be;
}
```

- [ ] **Step 2: Python-port unit test**

```bash
venv/bin/python - <<'PY'
def find_graphite(be, y):
    n = len(be)
    if n != len(y) or n < 3: return None
    gmax = max(y)
    if gmax <= 0: return None
    thr = 0.30 * gmax
    strong = []
    for i in range(1, n-1):
        if y[i] < thr: continue
        if y[i] >= y[i-1] and y[i] >= y[i+1]:
            strong.append((be[i], y[i]))
    if not strong: return None
    return max(strong, key=lambda x: x[0])[0]

# Two strong peaks: low-BE Unknown at 281, graphite at 285. Pick 285.
be = [278 + 0.1*i for i in range(80)]   # 278..285.9
y  = [0.0]*80
for i,b in enumerate(be):
    y[i] += 1.0 / (1 + ((b-281.0)/0.6)**2)   # Unknown peak amplitude 1.0
    y[i] += 1.5 / (1 + ((b-285.0)/0.5)**2)   # Graphite peak amplitude 1.5
r = find_graphite(be, y)
assert abs(r - 285.0) < 0.15, f'expected ~285, got {r}'

# One strong peak only — should return it.
y2 = [1.5 / (1 + ((b-285.0)/0.5)**2) for b in be]
r2 = find_graphite(be, y2)
assert abs(r2 - 285.0) < 0.15, r2

# Two strong peaks at 282 and 285 — pick highest BE (285)
y3 = [(1.5 / (1 + ((b-285.0)/0.5)**2)) + (1.4 / (1 + ((b-282.0)/0.5)**2)) for b in be]
r3 = find_graphite(be, y3)
assert abs(r3 - 285.0) < 0.15, r3

# Weak peak at 285 (below 30% threshold of stronger peak at 281) → 281 is the only
# "strong" max; should return 281.
y4 = [(0.20 / (1 + ((b-285.0)/0.5)**2)) + (1.0 / (1 + ((b-281.0)/0.5)**2)) for b in be]
r4 = find_graphite(be, y4)
assert abs(r4 - 281.0) < 0.15, r4

# Flat / no maxima → None
assert find_graphite([280, 281, 282], [0, 0, 0]) is None
print('findGraphiteRawBE: ok')
PY
```

Expected: `findGraphiteRawBE: ok`

- [ ] **Step 3: Verify**

```
grep -c 'function findGraphiteRawBE' templates/index.html
```

Expected: `1`

- [ ] **Step 4: Commit**

```bash
git add templates/index.html
git commit -m "feat(autofit): findGraphiteRawBE helper (highest-BE strong max)"
```

---

## Task 6: `assessLowBERegion` helper + Python port test

**Files:**
- Modify: `templates/index.html` — append after `findGraphiteRawBE`.

- [ ] **Step 1: Write the helper**

```js
// Decide how many low-BE peaks (0, 1, or 2) the auto-fit model should include.
//   rawBE             : array of raw BE values
//   bgSubInten        : background-subtracted intensity (same length)
//   provisionalShift  : state.ccShift to apply mentally — does NOT mutate state.
//                       App convention: corrected = raw − shift.
// Returns:
//   { count: 0|1|2, locations: number[] of corrected-BE local-max centers,
//     ratio: number, graphiteHeight: number }
//
// Algorithm (matches spec §3):
//   - Convert each rawBE to corrected: corr = raw − provisionalShift.
//   - Integrate bgSubInten over 278.0 ≤ corr ≤ 283.5.
//   - graphite_height = max bgSubInten where corr is closest to 284.50.
//   - ratio = integrated_low_BE / graphite_height.
//   - Local maxima in 278.0 ≤ corr ≤ 283.5 with bgSubInten ≥ 0.10 * graphite_height.
//   - Decide:
//       ratio < 0.03                              → 0
//       0.03 ≤ ratio < 0.15  OR exactly one max   → 1
//       ratio ≥ 0.15         OR ≥2 distinct maxima → 2
function assessLowBERegion(rawBE, bgSubInten, provisionalShift) {
  const n = rawBE.length;
  // 1. Graphite height: closest-corrected-to-284.5 sample
  let gIdx = 0;
  let gDist = Infinity;
  for (let i = 0; i < n; i++) {
    const corr = rawBE[i] - provisionalShift;
    const d = Math.abs(corr - 284.50);
    if (d < gDist) { gDist = d; gIdx = i; }
  }
  const graphiteHeight = bgSubInten[gIdx];
  if (!(graphiteHeight > 0)) {
    return { count: 0, locations: [], ratio: 0, graphiteHeight: 0 };
  }

  // 2. Integrate over 278.0 ≤ corrected ≤ 283.5 (trapezoid in corrected BE)
  let integral = 0;
  const corr = rawBE.map(b => b - provisionalShift);
  for (let i = 1; i < n; i++) {
    const c0 = corr[i - 1], c1 = corr[i];
    if (c1 < 278.0 || c0 > 283.5) continue;
    // Clip the segment to [278.0, 283.5]
    const lo = Math.max(Math.min(c0, c1), 278.0);
    const hi = Math.min(Math.max(c0, c1), 283.5);
    if (hi <= lo) continue;
    const width = hi - lo;
    const yMid = 0.5 * (bgSubInten[i - 1] + bgSubInten[i]);
    integral += width * Math.max(0, yMid);
  }
  const ratio = integral / graphiteHeight;

  // 3. Local maxima in [278.0, 283.5] with bgSub ≥ 0.10 * graphite_height
  const minPeak = 0.10 * graphiteHeight;
  const locations = [];
  for (let i = 1; i < n - 1; i++) {
    const c = corr[i];
    if (c < 278.0 || c > 283.5) continue;
    if (bgSubInten[i] < minPeak) continue;
    if (bgSubInten[i] >= bgSubInten[i - 1] && bgSubInten[i] >= bgSubInten[i + 1]) {
      locations.push(c);
    }
  }
  // De-duplicate locations within 0.4 eV of each other (keep highest)
  locations.sort((a, b) => a - b);
  const dedup = [];
  for (const c of locations) {
    if (dedup.length && Math.abs(dedup[dedup.length - 1] - c) < 0.4) continue;
    dedup.push(c);
  }

  // 4. Decide count
  let count;
  if (ratio < 0.03) count = 0;
  else if (ratio >= 0.15 || dedup.length >= 2) count = 2;
  else count = 1;
  return { count, locations: dedup, ratio, graphiteHeight };
}
```

- [ ] **Step 2: Python-port unit test**

```bash
venv/bin/python - <<'PY'
def assess(be, y, shift):
    n = len(be)
    corr = [b - shift for b in be]
    # graphite height
    gIdx = min(range(n), key=lambda i: abs(corr[i] - 284.50))
    gh = y[gIdx]
    if gh <= 0: return {'count': 0, 'locations': [], 'ratio': 0, 'graphiteHeight': 0}
    # integral
    integral = 0
    for i in range(1, n):
        c0, c1 = corr[i-1], corr[i]
        if c1 < 278.0 or c0 > 283.5: continue
        lo = max(min(c0, c1), 278.0)
        hi = min(max(c0, c1), 283.5)
        if hi <= lo: continue
        ymid = 0.5*(y[i-1] + y[i])
        integral += (hi - lo) * max(0, ymid)
    ratio = integral / gh
    minPk = 0.10 * gh
    locs = []
    for i in range(1, n-1):
        c = corr[i]
        if c < 278.0 or c > 283.5: continue
        if y[i] < minPk: continue
        if y[i] >= y[i-1] and y[i] >= y[i+1]:
            locs.append(c)
    locs.sort()
    dedup = []
    for c in locs:
        if dedup and abs(dedup[-1] - c) < 0.4: continue
        dedup.append(c)
    if ratio < 0.03: count = 0
    elif ratio >= 0.15 or len(dedup) >= 2: count = 2
    else: count = 1
    return {'count': count, 'locations': dedup, 'ratio': ratio, 'graphiteHeight': gh}

# Synthetic raw BE in [276, 295], graphite at raw 285, provisional_shift = +0.5
# So corrected: graphite at 284.5. Add features in low-BE region (corrected 278-283.5).
def lor(b, c, w=0.4, a=1.0):
    return a / (1 + ((b-c)/w)**2)

be = [276 + 0.05*i for i in range(380)]   # raw 276..294.95

# Case 1: clean graphite, no low-BE feature → count=0
y1 = [lor(b, 285.0, 0.5, 1.0) + lor(b, 285.5, 1.4, 0.3) for b in be]
r1 = assess(be, y1, 0.5)
assert r1['count'] == 0, r1
print('case 1 (clean):', r1['count'], 'ratio', f"{r1['ratio']:.3f}")

# Case 2: small bump at corrected ~282.5 → count=1
y2 = [lor(b, 285.0, 0.5, 1.0) + lor(b, 285.5, 1.4, 0.3) + lor(b, 283.0, 0.6, 0.10) for b in be]
r2 = assess(be, y2, 0.5)
assert r2['count'] == 1, r2
print('case 2 (small low-BE bump):', r2['count'], 'ratio', f"{r2['ratio']:.3f}")

# Case 3: prominent low-BE peak (single broad feature → ratio high, single max) → count=2 via ratio
y3 = [lor(b, 285.0, 0.5, 1.0) + lor(b, 285.5, 1.4, 0.3) + lor(b, 282.5, 1.0, 0.45) for b in be]
r3 = assess(be, y3, 0.5)
assert r3['count'] == 2, r3
print('case 3 (prominent low-BE):', r3['count'], 'ratio', f"{r3['ratio']:.3f}")

# Case 4: two distinct low-BE peaks, neither very tall → count=2 via locations
y4 = [lor(b, 285.0, 0.5, 1.0) + lor(b, 285.5, 1.4, 0.3) + lor(b, 282.5, 0.4, 0.15) + lor(b, 280.5, 0.4, 0.15) for b in be]
r4 = assess(be, y4, 0.5)
assert r4['count'] == 2, r4
print('case 4 (two distinct low-BE):', r4['count'], 'locs', r4['locations'])

print('assessLowBERegion: ok')
PY
```

Expected: `assessLowBERegion: ok` (with case prints showing count = 0/1/2 as labeled).

- [ ] **Step 3: Verify**

```
grep -c 'function assessLowBERegion' templates/index.html
```

Expected: `1`

- [ ] **Step 4: Commit**

```bash
git add templates/index.html
git commit -m "feat(autofit): assessLowBERegion (0/1/2 low-BE peaks)"
```

---

## Task 7: `buildAutoFitModel` peak-list factory

**Files:**
- Modify: `templates/index.html` — append after `assessLowBERegion`.

- [ ] **Step 1: Write the factory**

```js
// Build the auto-fit peak list in the corrected-BE frame.
//   assessment : the object returned by assessLowBERegion
// Returns: array of peak objects (defaultPeak overrides), in the order
//   [Graphite, Adventitious 1, Adventitious 2, Adventitious 3, Adventitious 4,
//    Unknown 1?, Unknown 2?]
// Each peak gets a fresh state.nextId via defaultPeak.
function buildAutoFitModel(assessment) {
  const peaks = [];

  // Graphite — LA shape, beta fixed at 0.05, alpha bounded [0.05, 0.20].
  // The backend hard-codes alpha bounds [0, 0.49] and m_gauss [0, 4.0]; we
  // initialize alpha=0.10 inside the spec's [0.05, 0.20] target range and
  // m=0.55 inside [0.4, 1.2]. peakToBackendSpec emits alpha/beta/m_gauss with
  // their fix flags — fix_alpha=false (we want it to vary), fix_beta=true.
  peaks.push(defaultPeak({
    name: 'Graphite',
    shape: 'LA',
    center: 284.50,
    fwhm: 0.7,
    amplitude: Math.max(1, assessment.graphiteHeight || 1000),
    laAlpha: 0.10,
    laBeta: 0.05,
    laM: 0.55,
    fixLaAlpha: false,
    fixLaBeta: true,
    fixLaM: false,
    fixCenter: false,
    fixFwhm: false,
    fixAmplitude: false,
  }));

  // Adventitious 1–4 — pseudo-Voigt (shape='GL'), eta free.
  // peakToBackendSpec emits gl_ratio = glMix/100, fix_gl_ratio = !!fixGlMix.
  // We want eta free so fixGlMix=false. Initial glMix=30 → gl_ratio=0.30.
  const adv = [
    { name: 'Adventitious 1', center: 284.80, fwhm: 1.4 },
    { name: 'Adventitious 2', center: 286.20, fwhm: 1.6 },
    { name: 'Adventitious 3', center: 287.80, fwhm: 1.8 },
    { name: 'Adventitious 4', center: 291.00, fwhm: 2.5 },
  ];
  for (const a of adv) {
    peaks.push(defaultPeak({
      name: a.name,
      shape: 'GL',
      center: a.center,
      fwhm: a.fwhm,
      amplitude: Math.max(1, (assessment.graphiteHeight || 1000) * 0.20),
      glMix: 30,
      fixGlMix: false,
      fixCenter: false,
      fixFwhm: false,
      fixAmplitude: false,
    }));
  }

  // Unknown 1 / Unknown 2 — assessment.locations[0/1] when present
  if (assessment.count >= 1) {
    const c1 = (assessment.locations && assessment.locations[0] != null)
      ? assessment.locations[0] : 283.0;
    peaks.push(defaultPeak({
      name: 'Unknown 1',
      shape: 'GL',
      center: c1,
      fwhm: 1.0,
      amplitude: Math.max(1, (assessment.graphiteHeight || 1000) * 0.15),
      glMix: 30,
      fixGlMix: false,
      fixCenter: false,
      fixFwhm: false,
      fixAmplitude: false,
    }));
  }
  if (assessment.count >= 2) {
    const c2 = (assessment.locations && assessment.locations[1] != null)
      ? assessment.locations[1] : 282.0;
    peaks.push(defaultPeak({
      name: 'Unknown 2',
      shape: 'GL',
      center: c2,
      fwhm: 1.0,
      amplitude: Math.max(1, (assessment.graphiteHeight || 1000) * 0.10),
      glMix: 30,
      fixGlMix: false,
      fixCenter: false,
      fixFwhm: false,
      fixAmplitude: false,
    }));
  }

  // Tag each peak with the spec's per-peak bounds so we can lay them on the
  // backend spec before /api/fit. peakToBackendSpec doesn't read these; we
  // attach them out-of-band and consume them in the fit-call site.
  // (The fit-call site is in Task 9 — runAutoFitC1sGraphite's _autoFitFitCall.)
  peaks[0]._afCenterMin = 284.50 - 0.30; peaks[0]._afCenterMax = 284.50 + 0.30;
  peaks[0]._afFwhmMin   = 0.40;          peaks[0]._afFwhmMax   = 1.20;
  // Adventitious 1–4 center ranges — peak #4 widened ±1.0 per spec.
  peaks[1]._afCenterMin = 284.80 - 0.50; peaks[1]._afCenterMax = 284.80 + 0.50;
  peaks[1]._afFwhmMin   = 0.80;          peaks[1]._afFwhmMax   = 3.00;
  peaks[2]._afCenterMin = 286.20 - 0.50; peaks[2]._afCenterMax = 286.20 + 0.50;
  peaks[2]._afFwhmMin   = 0.80;          peaks[2]._afFwhmMax   = 3.00;
  peaks[3]._afCenterMin = 287.80 - 0.50; peaks[3]._afCenterMax = 287.80 + 0.50;
  peaks[3]._afFwhmMin   = 0.80;          peaks[3]._afFwhmMax   = 3.50;
  peaks[4]._afCenterMin = 291.00 - 1.00; peaks[4]._afCenterMax = 291.00 + 1.00;
  peaks[4]._afFwhmMin   = 1.00;          peaks[4]._afFwhmMax   = 4.00;
  for (let i = 5; i < peaks.length; i++) {
    peaks[i]._afCenterMin = peaks[i].center - 0.80;
    peaks[i]._afCenterMax = peaks[i].center + 0.80;
    peaks[i]._afFwhmMin   = 0.50;
    peaks[i]._afFwhmMax   = 3.00;
  }
  return peaks;
}
```

- [ ] **Step 2: Verify**

```
grep -c 'function buildAutoFitModel' templates/index.html
```

Expected: `1`

- [ ] **Step 3: Smoke-test the function shape via console**

(Can be skipped during automated execution; the next end-to-end test exercises this implicitly. For sanity, the executor may run a quick browser console check if a tab is already loaded. Not gating.)

- [ ] **Step 4: Commit**

```bash
git add templates/index.html
git commit -m "feat(autofit): buildAutoFitModel peak-list factory (graphite + adv + unknowns)"
```

---

## Task 8: `_autoFitSnapshot` / `_autoFitRestore` (failure rollback)

**Files:**
- Modify: `templates/index.html` — append after `buildAutoFitModel`.

`pushUndo()` only deep-copies `state.peaks`; it does not capture `state.fitResult`, `state.ccShift`, or the cc-method/cc-obs/cc-lit DOM fields. The auto-fit restore-on-failure path needs all of these.

- [ ] **Step 1: Write the snapshot/restore pair**

```js
// Capture exactly the bits of state Auto-Fit will mutate, so a failure can
// cleanly restore the tab. Returns an opaque snapshot object.
function _autoFitSnapshot() {
  return {
    peaks:        JSON.parse(JSON.stringify(state.peaks || [])),
    fitResult:    state.fitResult ? { ...state.fitResult } : null,
    ccShift:      state.ccShift,
    nextId:       state.nextId,
    ccMethodDom:  document.getElementById('cc-method')?.value || 'none',
    ccObsDom:     document.getElementById('cc-obs')?.value || '',
    ccLitDom:     document.getElementById('cc-lit')?.value || '',
    roiMinDom:    document.getElementById('roi-min')?.value || '',
    roiMaxDom:    document.getElementById('roi-max')?.value || '',
    bgStartDom:   document.getElementById('bg-start')?.value || '',
    bgEndDom:     document.getElementById('bg-end')?.value || '',
  };
}

function _autoFitRestore(snap) {
  if (!snap) return;
  state.peaks     = snap.peaks;
  state.fitResult = snap.fitResult;
  state.ccShift   = snap.ccShift;
  state.nextId    = snap.nextId;
  const set = (id, v) => { const el = document.getElementById(id); if (el) el.value = v; };
  set('cc-method', snap.ccMethodDom);
  set('cc-obs',    snap.ccObsDom);
  set('cc-lit',    snap.ccLitDom);
  set('roi-min',   snap.roiMinDom);
  set('roi-max',   snap.roiMaxDom);
  set('bg-start',  snap.bgStartDom);
  set('bg-end',    snap.bgEndDom);
  // Recompute display + cc panel visibility without re-driving updateChargeCorrection
  // (which would shift things again). Just refresh the shift display:
  const disp = document.getElementById('cc-shift-display');
  if (disp) {
    const sh = -state.ccShift;
    disp.textContent = (sh >= 0 ? '+' : '') + sh.toFixed(3) + ' eV';
  }
  if (typeof renderPeakList === 'function') renderPeakList();
  if (typeof updatePlot === 'function') updatePlot();
}
```

- [ ] **Step 2: Verify**

```
grep -c 'function _autoFitSnapshot\|function _autoFitRestore' templates/index.html
```

Expected: `2`

- [ ] **Step 3: Commit**

```bash
git add templates/index.html
git commit -m "feat(autofit): pre-autofit snapshot + restore for failure rollback"
```

---

## Task 9: `applyAutoFitResult` (post-fit charge-correction refinement)

**Files:**
- Modify: `templates/index.html` — append after `_autoFitRestore`.

This helper runs **after** `applyBackendResult(json)` has updated peak parameter values. It refines `state.ccShift` from the fitted graphite center, drives `updateChargeCorrection()` to ripple the change through ROI/bg/peak-center DOM, and assembles `state.fitResult` exactly the way `runFit()` does.

Important: by the time this runs, the fit was already executed in the **provisional** corrected frame. `state.peaks[graphite].center` is the fitted value in that frame. `state.ccShift` is still the provisional value.

- [ ] **Step 1: Write the helper**

```js
// Apply a successful auto-fit result. Mutates state and DOM so the tab
// ends in a self-consistent corrected frame with graphite at exactly 284.50.
//   json         : raw /api/fit response (already passed through applyBackendResult)
//   graphiteRaw  : the raw-BE graphite center detected in step 1 (for cc-obs)
//   roi          : { be, inten, bgIntensity, bgSubtracted } from getROIData() at fit time
// Returns true on success; false (with notify) if the fitted graphite center
// is outside ±0.3 of 284.50 — caller treats false as a failure rollback.
function applyAutoFitResult(json, graphiteRaw, roi) {
  // 1. Locate the graphite peak in state.peaks (named "Graphite", first peak).
  const gPeak = state.peaks.find(p => p.name === 'Graphite') || state.peaks[0];
  if (!gPeak || !Number.isFinite(gPeak.center)) {
    notify('Auto-fit failed: graphite center not found in fit result.', 'red', true);
    return false;
  }
  // 2. Validate within ±0.3 of 284.50 (the LA center bound).
  if (Math.abs(gPeak.center - 284.50) > 0.30 + 1e-6) {
    notify('Fit failed to converge or produced an unphysical graphite position.', 'red', true);
    return false;
  }
  // 3. Compute fitted raw center using APP CONVENTION:
  //    raw = corrected + state.ccShift (state.ccShift is the provisional value here).
  const graphiteFittedRaw = gPeak.center + (Number.isFinite(state.ccShift) ? state.ccShift : 0);

  // 4. Drive updateChargeCorrection() to refine the shift.
  //    Self-consistency choice: cc-obs = graphite_fitted_raw (NOT graphite_raw_BE).
  //    Reasoning: the spec's narrative says ccObs = graphite_raw_BE, but that
  //    creates a UI inconsistency (state.ccShift would not equal obs − lit
  //    under c1s). The fitted raw center is the more accurate observation.
  const cm = document.getElementById('cc-method');
  const co = document.getElementById('cc-obs');
  const cl = document.getElementById('cc-lit');
  if (cm && co && cl) {
    cm.value = 'c1s';
    co.value = graphiteFittedRaw.toFixed(3);
    cl.value = '284.50';
    if (typeof updateChargeCorrection === 'function') updateChargeCorrection();
  }

  // 5. Build state.fitResult exactly the way runFit() does — see runFit at
  //    templates/index.html:4621-4624. The BE array we use is the ROI BE in
  //    the now-refined corrected frame. Since updateChargeCorrection shifted
  //    state.peaks centers by the refinement delta but not the roi.be array,
  //    we re-fetch.
  const { be: be2, inten: inten2 } = getROIData();
  const bgI2 = computeBackground(be2, inten2);
  const bgSub2 = inten2.map((v, i) => v - bgI2[i]);
  const stats = json.statistics || {};
  const chiReduced = stats.reduced_chi_square || 0;
  const rmse = Math.sqrt((json.residuals || []).reduce((s, v) => s + v * v, 0) / Math.max(1, be2.length));
  const roiRange = { min: _arrMin(be2).toFixed(1), max: _arrMax(be2).toFixed(1) };
  state.fitResult = {
    chi: chiReduced * Math.max(1, be2.length - state.peaks.length * 3),
    chiReduced, rmse,
    be: be2, bgSubtracted: bgSub2, bgIntensity: bgI2,
    backendResult: json,
    fittedY: json.fitted_y,
    roiRange,
  };
  state.fitResult.rFactor = _computeRFactor(state.fitResult);

  // 6. Update the same DOM elements runFit() updates.
  const fq = document.getElementById('fit-quality');
  if (fq) {
    fq.textContent = 'χ²ᵣ = ' + chiReduced.toFixed(2);
    if (typeof _CHISQ_TOOLTIP !== 'undefined') fq.setAttribute('data-xps-tip', _CHISQ_TOOLTIP);
  }
  const sbChi = document.getElementById('sb-chi');
  if (sbChi) sbChi.textContent = chiReduced.toFixed(3);
  const sbMsg = document.getElementById('sb-msg');
  if (sbMsg) sbMsg.textContent = 'Auto-fit complete';
  if (typeof _updateRFactorUI === 'function') _updateRFactorUI(state.fitResult.rFactor);
  if (typeof _updateROIDisplay === 'function') _updateROIDisplay(roiRange);
  if (typeof renderPeakList === 'function') renderPeakList();
  if (typeof updatePlot === 'function') updatePlot();
  if (typeof renderResults === 'function') renderResults();
  if (typeof _autoSnapshot === 'function') _autoSnapshot();

  // 7. Sync to tab record so tab switching preserves the result.
  if (typeof tabManager !== 'undefined' && tabManager._syncActiveToRecord) {
    tabManager._syncActiveToRecord();
  }
  return true;
}
```

- [ ] **Step 2: Verify**

```
grep -c 'function applyAutoFitResult' templates/index.html
```

Expected: `1`

- [ ] **Step 3: Commit**

```bash
git add templates/index.html
git commit -m "feat(autofit): applyAutoFitResult (refine ccShift + persist fit like runFit)"
```

---

## Task 10: `runAutoFitC1sGraphite` orchestrator

**Files:**
- Modify: `templates/index.html` — append after `applyAutoFitResult`.

This is the big one. It glues all helpers together, manages the spinner, AbortController, snapshot/restore, and confirmation flow.

- [ ] **Step 1: Write the orchestrator**

```js
// Top-level entry point. Wired to the Actions menu item.
async function runAutoFitC1sGraphite() {
  // Pre-conditions
  if (!state.rawBE || !state.rawBE.length) { notify('Load a spectrum first.', 'amber'); return; }
  const tab = tabManager._getTab(tabManager.activeId);
  if (!tab) { notify('No active tab.', 'amber'); return; }
  if (!isC1sTab(tab)) {
    notify('Auto-Fit C1s Graphite is only available for C1s spectra (ROI midpoint 270–315 eV).', 'amber');
    return;
  }
  // Confirmation if existing peaks
  if (state.peaks.length >= 1) {
    const proceed = await _showAutoFitConfirmModal(state.peaks.length);
    if (!proceed) return;
  }

  // Snapshot for failure rollback (separate from pushUndo, which only covers peaks).
  const snap = _autoFitSnapshot();

  // Step 1: find graphite in raw BE
  const { be: corrBE, inten } = getROIData();
  if (!corrBE.length) {
    notify('ROI is empty. Set roi-min and roi-max before auto-fit.', 'red', true);
    return;
  }
  const bgI = computeBackground(corrBE, inten);
  const bgSub = inten.map((v, i) => v - bgI[i]);
  // App convention: raw = corrected + state.ccShift
  const curShift = Number.isFinite(state.ccShift) ? state.ccShift : 0;
  const rawBE = corrBE.map(b => b + curShift);
  const graphiteRaw = findGraphiteRawBE(rawBE, bgSub);
  if (graphiteRaw == null) {
    notify('No strong peak found in the C1s ROI; Auto-Fit cannot proceed.', 'red', true);
    return;
  }

  // Step 2: provisional shift (APP CONVENTION).
  // state.ccShift = graphite_raw_BE − 284.50. Any user-set shift is overwritten.
  const provisionalShift = graphiteRaw - 284.50;

  // Step 3: assess low-BE region using provisional shift (no state mutation yet).
  const assessment = assessLowBERegion(rawBE, bgSub, provisionalShift);

  // Step 4: build the peak model (in corrected frame after provisional shift).
  pushUndo();
  state.peaks = [];
  state.fitResult = null;
  // Apply provisional shift via updateChargeCorrection so ROI/bg DOM fields
  // shift along with state.ccShift. We need cc-method=c1s and cc-obs=graphiteRaw
  // for updateChargeCorrection to compute the right shift.
  const cm = document.getElementById('cc-method');
  const co = document.getElementById('cc-obs');
  const cl = document.getElementById('cc-lit');
  cm.value = 'c1s';
  co.value = graphiteRaw.toFixed(3);
  cl.value = '284.50';
  updateChargeCorrection();
  // After updateChargeCorrection, state.ccShift = provisionalShift.
  // Now build the peak list (which uses 284.50 as graphite center).
  const newPeaks = buildAutoFitModel(assessment);
  state.peaks = newPeaks;
  state.nextId = Math.max(0, ...state.peaks.map(p => p.id)) + 1;
  renderPeakList();

  // Step 5: run /api/fit with AbortController + spinner.
  _showFitSpinner();
  const spinLabel = document.getElementById('fit-spinner-label');
  if (spinLabel) spinLabel.textContent = 'Auto-fitting…';
  // Disable Run Fit button while auto-fit runs (mirrors _showFitSpinner's behavior; safe to call again).
  const runBtn = document.querySelector('.btn-green');
  if (runBtn) runBtn.disabled = true;

  const fittingTabId = tabManager.activeId;
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(new DOMException('timeout', 'AbortError')), 120000);

  try {
    // Build /api/fit request matching runFit's shape (templates/index.html:4582-4592).
    const { be: be2, inten: inten2 } = getROIData();
    const bgType = document.getElementById('bg-type').value;
    const bgStart = parseFloat(document.getElementById('bg-start').value);
    const bgEnd = parseFloat(document.getElementById('bg-end').value);
    const bgStartIdx = be2.reduce((best, v, i) => Math.abs(v - bgStart) < Math.abs(be2[best] - bgStart) ? i : best, 0);
    const bgEndIdx   = be2.reduce((best, v, i) => Math.abs(v - bgEnd)   < Math.abs(be2[best] - bgEnd)   ? i : best, 0);
    const epAvg = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
    const sessionId = await uploadToBackend(be2, inten2);
    const fitMethod = document.getElementById('fit-method').value;

    // Build peak specs and overlay the per-peak bounds we attached in buildAutoFitModel.
    const peakSpecs = state.peaks.map(p => {
      const spec = peakToBackendSpec(p);
      if (Number.isFinite(p._afCenterMin)) spec.center_min = p._afCenterMin;
      if (Number.isFinite(p._afCenterMax)) spec.center_max = p._afCenterMax;
      if (Number.isFinite(p._afFwhmMin))   spec.fwhm_min   = p._afFwhmMin;
      if (Number.isFinite(p._afFwhmMax))   spec.fwhm_max   = p._afFwhmMax;
      spec.amplitude_min = 0;
      return spec;
    });

    const resp = await fetch('/api/fit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        background: { method: bgType, start_idx: bgStartIdx, end_idx: bgEndIdx, endpoint_avg: epAvg },
        peaks: peakSpecs,
        fit_method: fitMethod,
        n_perturb: 3,
      }),
      signal: ctrl.signal,
    });
    clearTimeout(timer);
    const json = await resp.json();
    if (json.error) throw new Error(json.error);
    if (!json.success) throw new Error('fit did not converge');
    if (tabManager.activeId !== fittingTabId) {
      _hideFitSpinner();
      notify('Auto-fit discarded — tab switched during fit.', 'amber');
      _autoFitRestore(snap);
      return;
    }

    // Apply fitted values to state.peaks.
    applyBackendResult(json);

    // Step 6: refine charge correction + persist fit result. Returns false on
    // out-of-bounds graphite center; we treat that as a failure.
    const ok = applyAutoFitResult(json, graphiteRaw, { be: be2, inten: inten2, bgIntensity: bgI, bgSubtracted: bgSub });
    if (!ok) {
      _hideFitSpinner();
      _autoFitRestore(snap);
      return;
    }

    _hideFitSpinner();
    notify('Auto-fit complete. χ²ᵣ = ' + (state.fitResult?.chiReduced?.toFixed(3) || '?'), 'green');
  } catch (e) {
    clearTimeout(timer);
    _hideFitSpinner();
    _autoFitRestore(snap);
    let msg;
    if (e && (e.name === 'AbortError' || (e.message && e.message.toLowerCase().includes('aborted')))) {
      msg = 'Auto-fit exceeded the 2-minute timeout.';
    } else if (e && e.message) {
      msg = 'Fit failed to converge or produced an unphysical graphite position.';
      console.warn('Auto-fit error:', e);
    } else {
      msg = 'Auto-fit failed.';
    }
    notify(msg, 'red', true);
  }
}
```

- [ ] **Step 2: Structural verify**

```bash
venv/bin/python - <<'PY'
import re
src = open('templates/index.html').read()
js = '\n'.join(m.group(1) for m in re.finditer(r'<script(?![^>]*src=)[^>]*>(.*?)</script>', src, re.S))
assert js.count('{') == js.count('}'), ('brace mismatch', js.count('{'), js.count('}'))
assert js.count('(') == js.count(')'), 'paren mismatch'
assert js.count('[') == js.count(']'), 'bracket mismatch'
for sym in ['runAutoFitC1sGraphite','isC1sTab','findGraphiteRawBE',
            'assessLowBERegion','buildAutoFitModel','applyAutoFitResult',
            '_autoFitSnapshot','_autoFitRestore','_showAutoFitConfirmModal',
            '_recomputeAutoFitMenuState','_autoFitConfirmCancel']:
    assert (f'function {sym}' in src) or (f'async function {sym}' in src), sym
print('structure: ok')
PY
```

Expected: `structure: ok`

- [ ] **Step 3: Commit**

```bash
git add templates/index.html
git commit -m "feat(autofit): runAutoFitC1sGraphite orchestrator"
```

---

## Task 11: Web-server reload + served-page sanity

**Files:** none — checks the running gunicorn instance is serving the new code.

- [ ] **Step 1: Reload gunicorn**

```bash
ps aux | grep -E 'gunicorn' | grep -v grep | head -3
```

Identify the master pid. Reload via:

```bash
kill -HUP <master_pid>
sleep 2
curl -sS -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:5000/
```

Expected: `HTTP 200`

- [ ] **Step 2: Confirm new symbols in the served HTML**

```bash
for m in 'runAutoFitC1sGraphite' 'isC1sTab' 'findGraphiteRawBE' 'assessLowBERegion' 'buildAutoFitModel' 'applyAutoFitResult' 'auto-fit-c1s-menu-item' 'auto-fit-c1s-confirm-overlay'; do
  c=$(curl -sS http://127.0.0.1:5000/ | grep -c "$m")
  echo "  $m: $c"
done
```

Expected: every count `>= 1`.

- [ ] **Step 3: No commit needed — this is a verification step.**

---

## Task 12: End-to-end Python harness (against running /api/fit)

**Files:** none — pure runtime check against the live server.

This validates that the auto-fit peak model, when posted to the running `/api/fit`, converges and lands graphite within bounds. It exercises the entire backend round-trip independent of the browser, catching backend-spec mistakes early.

- [ ] **Step 1: Run the harness**

```bash
venv/bin/python - <<'PY'
import json, urllib.request, math, random
random.seed(42)

# Synthesize a realistic C1s spectrum: graphite at raw 280.5 (charging
# of +4.0 eV from 284.50), adventitious cluster, mild low-BE bump.
def lor(b, c, w, a): return a / (1 + ((b-c)/(w/2))**2)
def gau(b, c, w, a):
    sig = w / 2.355
    return a * math.exp(-((b-c)/sig)**2 / 2)
def pv(b, c, w, a, eta=0.30):
    return (1-eta)*gau(b,c,w,a) + eta*lor(b,c,w,a)

be = [277 + 0.05*i for i in range(420)]   # raw 277 .. 297.95
y = []
for b in be:
    base = 200 + 20*(297-b)/20      # mild Shirley-like slope
    s  = pv(b, 280.50, 0.7, 2200)   # graphite
    s += pv(b, 280.80, 1.4,  600)   # adv 1
    s += pv(b, 282.20, 1.6,  300)   # adv 2 (corresponds to corrected 286.20)
    s += pv(b, 283.80, 1.8,  150)   # adv 3
    s += pv(b, 287.00, 2.5,  120)   # adv 4 (broad)
    s += pv(b, 279.00, 1.0,  150)   # one low-BE bump (corrected 283.00)
    y.append(base + s + random.gauss(0, 12))

# Upload spectrum
csv = '\n'.join(f'{b:.4f},{v:.2f}' for b,v in zip(be,y))
bd = '----wb'
body = (f'--{bd}\r\nContent-Disposition: form-data; name="file"; filename="c1s.csv"\r\n'
        'Content-Type: text/plain\r\n\r\n' + csv + f'\r\n--{bd}--\r\n').encode()
req = urllib.request.Request('http://127.0.0.1:5000/api/upload', data=body,
    headers={'Content-Type': f'multipart/form-data; boundary={bd}'})
sid = json.loads(urllib.request.urlopen(req).read())['session_id']

# Build the auto-fit peak list in CORRECTED frame (provisional shift = 280.50 − 284.50 = −4.00).
# After applying that shift, the corrected ROI is approximately 281–301.95.
# Graphite at corrected 284.50, etc.
peaks = [
    # Graphite (LA)
    dict(id='1', name='Graphite', shape='la_casaxps', center=284.50, amplitude=2200, fwhm=0.7,
         alpha=0.10, beta=0.05, m_gauss=0.55,
         fix_alpha=False, fix_beta=True, fix_m_gauss=False, fix_center=False, fix_amplitude=False, fix_fwhm=False,
         center_min=284.20, center_max=284.80, fwhm_min=0.40, fwhm_max=1.20, amplitude_min=0),
    # Adv 1
    dict(id='2', name='Adventitious 1', shape='pseudo_voigt_gl', center=284.80, amplitude=600, fwhm=1.4,
         gl_ratio=0.30, fix_gl_ratio=False, fix_center=False, fix_fwhm=False, fix_amplitude=False,
         center_min=284.30, center_max=285.30, fwhm_min=0.80, fwhm_max=3.00, amplitude_min=0),
    # Adv 2
    dict(id='3', name='Adventitious 2', shape='pseudo_voigt_gl', center=286.20, amplitude=300, fwhm=1.6,
         gl_ratio=0.30, fix_gl_ratio=False, fix_center=False, fix_fwhm=False, fix_amplitude=False,
         center_min=285.70, center_max=286.70, fwhm_min=0.80, fwhm_max=3.00, amplitude_min=0),
    # Adv 3
    dict(id='4', name='Adventitious 3', shape='pseudo_voigt_gl', center=287.80, amplitude=150, fwhm=1.8,
         gl_ratio=0.30, fix_gl_ratio=False, fix_center=False, fix_fwhm=False, fix_amplitude=False,
         center_min=287.30, center_max=288.30, fwhm_min=0.80, fwhm_max=3.50, amplitude_min=0),
    # Adv 4 (wider center bound)
    dict(id='5', name='Adventitious 4', shape='pseudo_voigt_gl', center=291.00, amplitude=120, fwhm=2.5,
         gl_ratio=0.30, fix_gl_ratio=False, fix_center=False, fix_fwhm=False, fix_amplitude=False,
         center_min=290.00, center_max=292.00, fwhm_min=1.00, fwhm_max=4.00, amplitude_min=0),
    # Unknown 1
    dict(id='6', name='Unknown 1', shape='pseudo_voigt_gl', center=283.00, amplitude=150, fwhm=1.0,
         gl_ratio=0.30, fix_gl_ratio=False, fix_center=False, fix_fwhm=False, fix_amplitude=False,
         center_min=282.20, center_max=283.80, fwhm_min=0.50, fwhm_max=3.00, amplitude_min=0),
]

# Post the fit. Note: the upload was raw BE; the backend doesn't apply the
# provisional shift itself (Auto-Fit's frontend does that via state.ccShift).
# For this harness we shift the BE before upload so the backend's frame
# matches the peak centers we send. Re-do the upload with shifted BE:
shift = 280.50 - 284.50   # state.ccShift in app convention = graphite_raw - 284.50 = -4.00
corr_be = [b - shift for b in be]   # corrected = raw − shift (app convention)
csv2 = '\n'.join(f'{b:.4f},{v:.2f}' for b,v in zip(corr_be,y))
body2 = (f'--{bd}\r\nContent-Disposition: form-data; name="file"; filename="c1s.csv"\r\n'
         'Content-Type: text/plain\r\n\r\n' + csv2 + f'\r\n--{bd}--\r\n').encode()
sid2 = json.loads(urllib.request.urlopen(urllib.request.Request(
    'http://127.0.0.1:5000/api/upload', data=body2,
    headers={'Content-Type': f'multipart/form-data; boundary={bd}'})).read())['session_id']

req = urllib.request.Request('http://127.0.0.1:5000/api/fit',
    data=json.dumps({'session_id': sid2,
        'background': {'method': 'shirley', 'start_idx': 0, 'end_idx': len(corr_be), 'endpoint_avg': 1},
        'peaks': peaks, 'fit_method': 'leastsq', 'n_perturb': 3}).encode(),
    headers={'Content-Type': 'application/json'})
data = json.loads(urllib.request.urlopen(req).read())
print('success:', data['success'], 'chi²ᵣ:', data['statistics']['reduced_chi_square'])
g = next(ip for ip in data['individual_peaks'] if ip.get('name') == 'Graphite')
gc = g['params']['center']['value']
print(f'graphite fitted center: {gc:.3f} (target 284.50, bound ±0.30)')
assert data['success']
assert abs(gc - 284.50) <= 0.30 + 1e-6, f'graphite at {gc} outside bound'
print('end-to-end fit: ok')
PY
```

Expected:
- `success: True`
- `chi²ᵣ:` is a finite small number
- `graphite fitted center` within `[284.20, 284.80]`
- `end-to-end fit: ok`

- [ ] **Step 2: No commit needed.** This is a runtime sanity check; the previous commits already cover the implementation.

---

## Task 13: Browser manual verification checklist (plain language)

**Files:** none — this is for the human reviewer.

Before pushing, walk through every scenario in a real browser at `http://127.0.0.1:5000/`. Hard-refresh first (Cmd-Shift-R / Ctrl-Shift-R) so the new JS is loaded. Open the browser DevTools console — leave it visible the whole time.

### Menu enable/disable

- [ ] **Open a non-C1s tab first.** If you have a U 4f or Cl 2p tab handy, switch to it.
- [ ] **Open the Actions menu.** "Auto-Fit C1s Graphite" should appear *grayed out* (lower opacity, not clickable). Hover the entry — the tooltip should say it is only available for C1s spectra.
- [ ] **Switch to a C1s tab.** Re-open the Actions menu. "Auto-Fit C1s Graphite" should now be *clickable* (full opacity, no "not allowed" cursor when hovering).
- [ ] **Edit the ROI on the C1s tab** — for example, change the upper ROI to 320 eV. The midpoint moves out of the C1s window. Re-open the menu — the entry should be *grayed out* again. Restore the ROI; the entry re-enables.

### Confirmation modal

- [ ] **On a C1s tab with no peaks** (verify the peak list is empty), click "Auto-Fit C1s Graphite". The fit should start *immediately* — no confirmation modal appears. The plot area shows a spinner.
- [ ] **On a C1s tab with peaks present**, click "Auto-Fit C1s Graphite". A modal appears with the title "Auto-Fit will replace existing peaks", showing the actual peak count. Click *Cancel* — the modal closes, peaks are unchanged, no fit runs. Re-click the menu and this time click *Proceed* — the fit starts.

### Fit happy path (the main case)

- [ ] **On a C1s spectrum with a clear graphite peak**, run Auto-Fit. The spinner should appear within ~0.2 seconds. The fit should complete in under one minute on typical hardware. When it finishes:
  - The spinner disappears.
  - A green toast says "Auto-fit complete" with a chi-squared value.
  - The peak list shows: Graphite, Adventitious 1, Adventitious 2, Adventitious 3, Adventitious 4, and possibly Unknown 1 / Unknown 2.
  - The graphite peak's center is **284.50 ± 0.05 eV** in the corrected-BE display.
  - The charge-correction panel shows: Method = "C 1s graphite (284.5 eV)", Observed = the fitted raw graphite BE, Reference = 284.50, Shift = the corresponding eV value.
  - The chart shows the fitted envelope sitting on top of the data — visually a good fit.

### Low-BE peak count selection

- [ ] **C1s with prominent low-BE peak** (test spectrum #1). Auto-Fit should produce a peak list that includes both Unknown 1 *and* Unknown 2. Verify by counting the peaks.
- [ ] **C1s with one small low-BE bump** (test spectrum #2). Auto-Fit should produce a peak list that includes Unknown 1 *only* (no Unknown 2). Verify.
- [ ] **C1s with negligible low-BE intensity** (test spectrum #3). Auto-Fit should produce a peak list with *no* Unknown peaks — only Graphite + Adventitious 1–4.

### Failure paths

- [ ] **No strong peak.** Pick a noise-dominated region or a flat baseline ROI on a C1s tab. Run Auto-Fit. Expect a red toast: "No strong peak found in the C1s ROI; Auto-Fit cannot proceed." Peaks unchanged.
- [ ] **Graphite out of bounds.** This is hard to provoke deterministically; it happens when the auto-fit converges to a graphite center outside [284.20, 284.80]. If this never trips, that's fine — the failure path is also exercised below by the timeout.
- [ ] **Timeout.** Without a way to force a slow fit, this is the hardest case to verify. Optional: temporarily lower the timeout in the JS to 1000 ms, run on a slow target, observe the toast "Auto-fit exceeded the 2-minute timeout." and confirm peaks are restored. Revert the change before committing.

### Undo

- [ ] **Run Auto-Fit successfully on a tab that previously had a manual fit.** Click Undo (Ctrl-Z / Cmd-Z). The previous peaks should be restored. (Note: undo restores `state.peaks` only, not the charge-correction shift; charge correction is a separate user action.)

### Spinner lifecycle

- [ ] **During the fit**, the plot area shows a spinner overlay. No text, no elapsed-time counter, no cancel button — just a spinner.
- [ ] **On success**, the spinner disappears as soon as the toast appears.
- [ ] **On failure** (e.g. the "no strong peak" case above), the spinner does *not* appear at all, because failure is detected pre-fit. For backend-rejection cases that DO start the fit, the spinner disappears together with the red toast.

### Console hygiene

- [ ] **Throughout all of the above**, the DevTools console should show no red error stack traces. A `console.warn('Auto-fit error: …')` line is acceptable on the failure paths — that's expected logging.

---

## Phase-3 hooks (deferred, not part of this plan)

- **Auto-fit for other core levels (O 1s, Si 2p, Fe 2p).** The structure of `runAutoFitC1sGraphite` is reusable; the per-element initial centers, bounds, and the dominant-peak heuristic become parameters.
- **Batch auto-fit across tabs.** Build on this single-spectrum fit once the lab confirms it produces defensible fits in routine use.
- **Server-side cancellation.** Eliminates the ghost-computation issue when the 120-second timeout fires; requires a backend change.
- **Learning from prior fits.** Adapt starting positions / bounds based on the user's saved fits.

---

## Follow-up tasks (2026-04-24)

After Phase-1 shipped, two real-data fixes were specified and implemented
as a separate plan: see
[2026-04-24-auto-fit-c1s-followup-fixes.md](2026-04-24-auto-fit-c1s-followup-fixes.md).

- FIX 1: clamp Adventitious 1 center floor at 284.80 eV (1-line bound change in `buildAutoFitModel`).
- FIX 2: amber warning toast when graphite area fraction < 40% (helper + 1 call in `applyAutoFitResult`).

Both are additive, frontend-only, with no regression to Phase-1 behavior.
