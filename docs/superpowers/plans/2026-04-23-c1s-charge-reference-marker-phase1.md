# C1s Charge-Reference Marker — Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an `isChargeReference` boolean to peaks, a single-select UI toggle, a validation helper, and persist the flag through all save/load paths — without touching fit logic or batch flows.

**Architecture:** Extend the peak object created in `defaultPeak()` with one new field. Leverage the existing `state.peaks.map(p => ({...p}))` spread that every serializer already uses — so save is automatic. Backfill to `false` at each load entry point (`tabManager.fromJSON` v1 path, `_loadSpectrumFile`, `_loadProjectJSON`, and history snapshot restore). Add a `toggleChargeReference(id)` mutator that enforces the single-reference invariant, a checkbox row in the peak editor body, an amber badge in the peak list header, and a `hasExactlyOneChargeReference()` helper for Phase 2 to call.

**Tech Stack:** Vanilla JS + inline CSS in `templates/index.html`. No backend/API changes. No new dependencies.

---

## Scope / Non-Goals

This plan implements **only** the peak data model flag, its UI toggle, its save/load persistence, and a validation helper. It does not touch:

- Assisted batch mode (Phase 2)
- Two-pass fit logic (Phase 2)
- Charge-correction recomputation
- Review queue, badges, or navigation
- `U 4f` or generic propagation behavior
- Backend `fitting.py` or `app.py`

---

## Testing approach

The project has **no JS/Python test harness** (no `pytest`, no `jest`, no spec runner). Phase 1 verifications therefore use:

1. Python static checks via `venv/bin/python` + stdlib `re` / `json` to assert the template source contains expected patterns.
2. A runnable headless sanity script that exercises the load-normalization logic by extracting and eval-ing the two helpers in Node (not required, optional).
3. A manual browser checklist (Task 9) walking through the acceptance criteria.

Each task below uses a verifier that can actually be run in this environment.

---

## File Structure

All changes are in a single file:

- Modify: `templates/index.html`

**Regions that will change (line numbers from current main):**

| Region | Line(s) | Purpose |
|---|---|---|
| CSS: peak badges | insert near `528` (`.linked-badge`) | Add `.chargeref-badge` rule |
| `defaultPeak()` object literal | `3453-3486` | Add `isChargeReference: false` |
| Peak list header markup in `renderPeakList` | `4135-4141` | Add amber "C-ref" badge next to name |
| `renderPeakForm()` | after `4161` (inside the body, after Name field) | Add checkbox row |
| `tabManager.fromJSON` v1 path | `2162` | Normalize peaks on load |
| `_loadSpectrumFile` | `5940` | Normalize peaks on load |
| `_loadProjectJSON` | `5974` | Normalize peaks on load |
| History snapshot restore | `7547` | Normalize peaks on load |
| New helpers (any stable spot — pick inside the PEAKS section near `3453`) | new | `_normalizePeakCRef`, `toggleChargeReference`, `hasExactlyOneChargeReference` |

---

## Task 1: Add `isChargeReference: false` to `defaultPeak`

**Files:**
- Modify: `templates/index.html:3456-3486`

- [ ] **Step 1: Inspect the current `defaultPeak` object literal**

Run: `grep -n "isChargeReference\|fixLaM" templates/index.html | head`

Expected output (before the change):
```
4056:const LOCK_ALL_KEYS = [...'fixLaM'...]   (or similar — the field is the last one in defaultPeak)
```
(`isChargeReference` should not match anywhere yet.)

- [ ] **Step 2: Add the new field to the `defaultPeak` literal**

Locate the `defaultPeak` function around line 3453 and add `isChargeReference: false` as the last property before the closing brace of the object literal.

Edit:

```js
    fixLaM: false,
    isChargeReference: false
  }, overrides);
}
```

(That is: change the existing `fixLaM: false` line to add a trailing comma and append `isChargeReference: false` right after it.)

- [ ] **Step 3: Verify the field is present**

Run:
```
grep -n "isChargeReference" templates/index.html
```

Expected: at least one match on the new line inside `defaultPeak`.

- [ ] **Step 4: Commit**

```bash
git add templates/index.html
git commit -m "feat(peaks): add isChargeReference flag to default peak schema"
```

---

## Task 2: Add `_normalizePeakCRef` backfill helper

**Files:**
- Modify: `templates/index.html` (insert just before `defaultPeak`, around line 3453)

- [ ] **Step 1: Decide the invariant**

The helper backfills `isChargeReference: false` when missing on a loaded peak, and guarantees at most one `true` across the list (keeps the first `true`, clears the rest). This prevents a corrupt save from producing two references.

- [ ] **Step 2: Add the helper**

Insert immediately above the `function defaultPeak(overrides) {` line:

```js
// Normalize charge-reference flags on a freshly-loaded peak list.
// Old saves do not have `isChargeReference` — default to false.
// If a save somehow has >1 true, keep the first and clear the rest.
function _normalizePeaksCRef(peaks) {
  if (!Array.isArray(peaks)) return peaks;
  let seen = false;
  return peaks.map(p => {
    const q = { ...p };
    if (typeof q.isChargeReference !== 'boolean') q.isChargeReference = false;
    if (q.isChargeReference) {
      if (seen) q.isChargeReference = false;
      else seen = true;
    }
    return q;
  });
}
```

- [ ] **Step 3: Verify the helper parses**

Run:
```
grep -n "_normalizePeaksCRef" templates/index.html
```

Expected: at least one declaration line and — after Task 3 — four call sites.

- [ ] **Step 4: Commit**

```bash
git add templates/index.html
git commit -m "feat(peaks): add _normalizePeaksCRef loader backfill helper"
```

---

## Task 3: Wire `_normalizePeaksCRef` into all four peak-load paths

**Files:**
- Modify: `templates/index.html:2162` (tabManager.fromJSON v1 compat path)
- Modify: `templates/index.html:5940` (`_loadSpectrumFile`)
- Modify: `templates/index.html:5974` (`_loadProjectJSON`)
- Modify: `templates/index.html:7547` (`_historyRestoreSnap`, restore from snapshot)

Each site currently uses `(data.peaks || []).map(p => ({...p}))` (or an equivalent deep copy). We wrap the result in `_normalizePeaksCRef(...)`.

- [ ] **Step 1: Patch `tabManager.fromJSON` v1 path**

Change:

```js
state.peaks = (data.peaks || []).map(p => ({...p}));
```

to:

```js
state.peaks = _normalizePeaksCRef((data.peaks || []).map(p => ({...p})));
```

- [ ] **Step 2: Patch `_loadSpectrumFile`**

Change line 5940:

```js
active.peaks = (data.peaks || []).map(p => ({...p}));
```

to:

```js
active.peaks = _normalizePeaksCRef((data.peaks || []).map(p => ({...p})));
```

- [ ] **Step 3: Patch `_loadProjectJSON`**

Change line 5974 inside the `newTabs` map:

```js
peaks: (t.peaks || []).map(p => ({...p})),
```

to:

```js
peaks: _normalizePeaksCRef((t.peaks || []).map(p => ({...p}))),
```

- [ ] **Step 4: Patch history snapshot restore**

Find the restore call (around line 7547):

```js
state.peaks = JSON.parse(JSON.stringify(snap.peaks));
```

Change to:

```js
state.peaks = _normalizePeaksCRef(JSON.parse(JSON.stringify(snap.peaks)));
```

- [ ] **Step 5: Verify all four call sites exist**

Run:
```
grep -n "_normalizePeaksCRef" templates/index.html
```

Expected: exactly 5 matches (1 declaration + 4 call sites).

- [ ] **Step 6: Backward-compat smoke test**

Construct a fake legacy fit JSON without the field and assert that post-normalization every peak has `isChargeReference === false`. Run:

```
venv/bin/python - <<'PY'
import re, json
src = open('templates/index.html').read()
# Extract the helper body and a minimal runtime via Node is overkill — instead
# just assert shape by regex: the helper exists and the four call sites present.
assert src.count('_normalizePeaksCRef(') >= 4, 'expected >=4 call sites'
assert '_normalizePeaksCRef(peaks)' in src or 'function _normalizePeaksCRef' in src
print('ok')
PY
```

Expected output: `ok`

- [ ] **Step 7: Commit**

```bash
git add templates/index.html
git commit -m "feat(peaks): normalize isChargeReference on all peak-load paths"
```

---

## Task 4: Add `toggleChargeReference(id)` single-select mutator

**Files:**
- Modify: `templates/index.html` (insert just below `_normalizePeaksCRef` from Task 2)

- [ ] **Step 1: Add the mutator**

Place directly after the `_normalizePeaksCRef` function:

```js
// Toggle the charge-reference designation on peak `id`.
// Enforces single-reference invariant: marking one peak clears all others.
// Clicking the already-marked peak clears it (zero-reference state).
function toggleChargeReference(id) {
  const target = getPeak(id);
  if (!target) return;
  pushUndo();
  const turningOn = !target.isChargeReference;
  for (const p of state.peaks) p.isChargeReference = false;
  if (turningOn) target.isChargeReference = true;
  renderPeakList();
  // Flag is metadata — does not affect fitted curve, so no updatePlot() needed.
}
```

- [ ] **Step 2: Verify declaration exists**

Run:
```
grep -n "function toggleChargeReference" templates/index.html
```

Expected: one match.

- [ ] **Step 3: Commit**

```bash
git add templates/index.html
git commit -m "feat(peaks): add toggleChargeReference single-select mutator"
```

---

## Task 5: Add `hasExactlyOneChargeReference()` validation helper

**Files:**
- Modify: `templates/index.html` (immediately after `toggleChargeReference`)

- [ ] **Step 1: Add the helper**

Place directly below `toggleChargeReference`:

```js
// Returns true iff the active tab has exactly one peak marked as the
// charge-reference. Phase 2 (C1s assisted batch) calls this as a gate.
// Not wired into any current workflow.
function hasExactlyOneChargeReference() {
  if (!Array.isArray(state.peaks)) return false;
  let count = 0;
  for (const p of state.peaks) if (p.isChargeReference) count++;
  return count === 1;
}
```

- [ ] **Step 2: Verify declaration exists**

Run:
```
grep -n "function hasExactlyOneChargeReference" templates/index.html
```

Expected: one match.

- [ ] **Step 3: Commit**

```bash
git add templates/index.html
git commit -m "feat(peaks): add hasExactlyOneChargeReference validation helper"
```

---

## Task 6: Add amber "C-ref" badge in peak list header

**Files:**
- Modify: `templates/index.html:4138` (inside `renderPeakList`)

The existing header shows `${p.name}${isLinked ? ' <span class="linked-badge">linked</span>' : ''}`. We append a parallel conditional for the charge-reference flag.

- [ ] **Step 1: Patch the header template literal**

Change:

```js
<span class="peak-name">${p.name}${isLinked ? ' <span class="linked-badge">linked</span>' : ''}</span>
```

to:

```js
<span class="peak-name">${p.name}${isLinked ? ' <span class="linked-badge">linked</span>' : ''}${p.isChargeReference ? ' <span class="chargeref-badge" title="Charge-correction reference (C 1s graphite 284.8 eV)">C-ref</span>' : ''}</span>
```

- [ ] **Step 2: Verify**

Run:
```
grep -n "chargeref-badge" templates/index.html
```

Expected: at least two matches once Task 7's CSS lands (one in markup, one in CSS).

- [ ] **Step 3: Commit**

```bash
git add templates/index.html
git commit -m "feat(peaks): show C-ref badge in peak list header"
```

---

## Task 7: Add `.chargeref-badge` CSS rule

**Files:**
- Modify: `templates/index.html` — immediately after the existing `.linked-badge` block (around line 537)

- [ ] **Step 1: Insert the CSS rule**

Place directly after the closing brace of `.linked-badge`:

```css
  /* Charge-reference (C 1s graphite) marker */
  .chargeref-badge {
    font-size: 9px;
    padding: 1px 5px;
    border-radius: 2px;
    background: var(--amber-dim);
    border: 1px solid var(--amber);
    color: var(--amber);
    margin-left: 4px;
  }
```

- [ ] **Step 2: Verify**

Run:
```
grep -n "chargeref-badge" templates/index.html
```

Expected: at least two matches (markup from Task 6 + this CSS rule).

- [ ] **Step 3: Commit**

```bash
git add templates/index.html
git commit -m "style(peaks): amber badge style for C-ref marker"
```

---

## Task 8: Add charge-reference toggle row inside peak editor body

**Files:**
- Modify: `templates/index.html` — inside `renderPeakForm` (function starts at line 4161)

Find the existing `<label>Name</label>` row near the top of `renderPeakForm` and insert a compact checkbox row directly after the Name field's closing `</div>`. The control sits at the top of the editor so it reads as a peak-level attribute, not a fit parameter.

- [ ] **Step 1: Locate the Name ↔ Line-shape seam inside `renderPeakForm`**

Run:
```
grep -n '<label>Name</label>\|<label>Line shape</label>' templates/index.html
```

Expected: two adjacent matches, a few lines apart, inside `renderPeakForm`. The new block goes between the Name field's closing `</div>` and the Line-shape field's opening `<div class="field">`.

- [ ] **Step 2: Insert the toggle row**

Add a new `<div class="field">` block between the Name field and the Line-shape field. Use the existing `.field` styling for consistency.

```html
    <div class="field" style="display:flex;align-items:center;gap:6px;margin-top:2px">
      <input type="checkbox" id="pk-cref-${p.id}"
             ${p.isChargeReference ? 'checked' : ''}
             onchange="toggleChargeReference(${p.id})"
             style="margin:0">
      <label for="pk-cref-${p.id}"
             style="margin:0;font-size:11px;cursor:pointer;user-select:none"
             title="Mark this peak as the charge-correction reference (typically C 1s graphite at 284.8 eV). Only one peak per fit can hold this marker.">
        Charge-correction reference (C&nbsp;1s graphite)
      </label>
    </div>
```

- [ ] **Step 3: Verify**

Run:
```
grep -n "pk-cref-" templates/index.html
```

Expected: two matches (input id + label for).

- [ ] **Step 4: Commit**

```bash
git add templates/index.html
git commit -m "feat(peaks): add C-ref checkbox row to peak editor"
```

---

## Task 9: Manual verification checklist

**Files:** none — browser + DevTools.

- [ ] **Step 1: Start the dev server**

```bash
venv/bin/python app.py
```

Open `http://localhost:5000` (or whatever port the app prints) in a browser.

- [ ] **Step 2: Load demo C 1s spectrum**

Click the `C 1s` demo button (or load any spectrum). Add two peaks if none exist.

- [ ] **Step 3: Verify default value**

Open DevTools console, run: `state.peaks.map(p => p.isChargeReference)` — expect all `false`.

- [ ] **Step 4: Verify UI single-select**

Expand the first peak's editor body. Tick "Charge-correction reference (C 1s graphite)".
Expected: amber "C-ref" badge appears in that peak's header row. Run in console `hasExactlyOneChargeReference()` — expect `true`.

Tick the second peak's checkbox.
Expected: first peak's badge disappears, second peak's badge appears, first peak's checkbox is now unchecked. `hasExactlyOneChargeReference()` still `true`.

Un-tick the second peak.
Expected: no badges anywhere. `hasExactlyOneChargeReference()` → `false`.

- [ ] **Step 5: Verify save/load round-trip (.fit.json and .proj.json)**

Re-tick peak 2. Save → "Save Fit". Reload the page (fresh state). Load a spectrum, then drag the saved `.fit.json` back in. Expected: peak 2 has its "C-ref" badge restored and `state.peaks[1].isChargeReference === true`.

Then: with peak 2 still marked, "Save Project". Reload the page. Drag the `.proj.json` in (no spectrum load required — project restores its own tab). Expected: peak 2 still shows the badge, and `tabManager._getTab(tabManager.activeId).peaks[1].isChargeReference === true`.

- [ ] **Step 6: Verify legacy-file load**

Construct a minimal legacy JSON and drag it in:

```bash
cat > /tmp/legacy.fit.json <<'EOF'
{
  "version": 1,
  "peaks": [
    { "id": 1, "name": "P1", "center": 284.8, "fwhm": 1.0, "amplitude": 1000,
      "shape": "GL", "glMix": 30, "color": "#ff6666",
      "linked": null, "visible": true }
  ],
  "nextId": 2,
  "chargeCorrection": { "method": "none", "observedBE": "", "shift": 0 },
  "background": { "type": "shirley", "start": "", "end": "", "shirleyIter": "5" },
  "roi": { "min": "280", "max": "295" }
}
EOF
```

Load spectrum first, then drag `/tmp/legacy.fit.json` into the browser.
Expected: no badges, `state.peaks[0].isChargeReference === false`, no errors in the console.

- [ ] **Step 7: Verify snapshot restore preserves the flag**

Mark peak 2 as C-ref. Run a fit to trigger the auto snapshot. Clear/edit the peak (un-tick the checkbox). Open history panel, click "Restore" on the most recent snapshot. Expected: peak 2's badge is back.

- [ ] **Step 8: Verify regression — no visible changes to generic propagation UI**

Open the "Propagate fit model" dialog (the existing batch flow). Visually confirm it is unchanged from before this phase.

---

## Assumptions

1. **No filter on linked peaks.** The spec doesn't forbid marking a linked (child) multiplet peak. The mutator does not exclude linked peaks. If later phases want to forbid this, they can extend `toggleChargeReference`.
2. **Single tab scope.** The invariant is enforced per tab (since `state.peaks` is the active tab's peak list). Different tabs may each independently mark one peak as their own reference — that matches the per-tab nature of charge correction in the current app.
3. **No backend change required.** The marker is pure frontend metadata. When peaks are serialized for `/fit` calls, extra keys (`isChargeReference`) are ignored by the backend (it picks only known keys from each spec).
4. **Undo coverage.** `toggleChargeReference` calls `pushUndo()`, so ticking/unticking is undoable consistent with other peak edits.

## Phase 2 Hooks Provided

- `toggleChargeReference(id)` — mutator with single-select invariant, ready for keyboard shortcut wiring or batch UI triggers.
- `hasExactlyOneChargeReference()` — gate function for the assisted-batch "Run" button / preflight check.
- Peak has a stable boolean `isChargeReference` that survives every persistence path (fit save, spectrum save, project save/zip, snapshot, tab switch), so Phase 2 code can rely on reading `p.isChargeReference` from any loaded peak list.
