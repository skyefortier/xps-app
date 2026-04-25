# Auto-Fit C1s Graphite Follow-Up Round 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix two real-data bugs and add one quality-of-life feature on top of the shipped Auto-Fit C1s Graphite v1: (1) make the graphite-area-fraction warning toast actually fire when graphite is below 40%, (2) switch graphite from LA → Asymmetric GL with enforceable α bounds so it stops collapsing to a symmetric line, (3) lock peak centers after a successful auto-fit so manual follow-up fits don't drift the converged positions.

**Architecture:** Frontend-only changes for ISSUE 1, ISSUE 3, and ISSUE 4. ISSUE 2 needs a 2-line surgical edit in `fitting.py` to plumb asymmetry bounds through to the lmfit `Parameter` (no new backend feature, just exposing existing capability — same pattern already used for `center_min`/`center_max`/`fwhm_min`/`fwhm_max`). All four items reuse existing primitives (`_peakArea`, `notify`, `fixCenter` lock, `peakToBackendSpec`); no new UI controls, no new menu entries, no settings, no persistence.

**Tech Stack:** Single-file frontend at `templates/index.html` (CSS + HTML + JS), Flask backend at `app.py`, lmfit-based fitter at `fitting.py`. Tests run via inline `venv/bin/python -c "..."` or written to `/tmp/` (no `tests/` directory in this repo).

**Iteration-cycle constraint (user-set, 2026-04-24):** The 2-line `fitting.py` edit in Task 2 is the LAST backend change permitted in this iteration cycle of Auto-Fit C1s Graphite. Any future round that identifies a backend change must trigger a **stop-and-redesign at the spec level** — i.e. a fresh `/superpowers:brainstorm` or `/superpowers:write-plan` cycle, not an inline approval. Do not propose mid-execution backend touches in subsequent rounds.

---

## Background: why each fix

### ISSUE 1 — area-fraction warning silently swallowed

After a successful auto-fit on `8 A/C1s Scan.VGD`, the peak list AREA column reports graphite at **33.3%** of total fitted area. By spec, anything below 40% should emit an amber warning toast. No toast appears.

**Root cause** (high confidence, given the code paths):

- The peak-list AREA column calls `_peakArea(p, be)` ([templates/index.html:5412](../../../templates/index.html#L5412)), which integrates the **frontend** lineshape via `evalPeak` over `state.fitResult.be`.
- The follow-up-1 helper `_autoFitCheckGraphiteFraction(json, graphiteId)` ([templates/index.html:4867](../../../templates/index.html#L4867)) instead reads `json.individual_peaks[i].params.area.value` — which is the **backend** trapezoid integration of the **backend** lineshape (`fitting.py:896` → `area = float(trapezoid(peak_y, x))`).
- For the LA shape, the JS implementation and the Python implementation are not byte-identical. They diverge enough on a strongly-asymmetric LA tail that the backend area for graphite can sit on the other side of the 40% threshold from the frontend area, even when both are computed correctly.

**Fix:** make the helper use `_peakArea` against `state.peaks` and `state.fitResult.be` — the *exact same source* as the user-visible AREA column. The two will then agree by construction. As a side-effect, the helper no longer depends on the backend response shape, eliminating an entire class of potential breakage.

### ISSUE 2 — LA(α,β,m) overparameterised, α collapses to 0

On real C1s data the optimizer drove graphite's α to ~0.000 with LA. When α=0, the LA shape is symmetric, and the high-BE shoulder that should belong to graphite ends up absorbed by Adventitious 1 — which fattens to FWHM 2.17 eV in the same fit, an unphysical width for sp³ adventitious carbon.

**Why LA collapses:** LA has three free shape parameters (α, β, m) plus center, FWHM, amplitude. Six freedom for one peak with limited prior — the optimizer happily zeroes α since β alone produces a passable Lorentzian-ish shape. Worse: even though the frontend declares α bounds [0.05, 0.20], **those bounds never reach the backend**. `peakToBackendSpec` ([templates/index.html:4499–4506](../../../templates/index.html#L4499-L4506)) emits `spec.alpha`, `spec.beta`, `spec.m_gauss` but no min/max keys, and the backend `_make_peak_params` for `la_casaxps` ([fitting.py:663–669](../../../fitting.py#L663-L669)) hardcodes `min_=0.0, max_=0.49`. The frontend declarations were silently ignored.

**Fix:** switch graphite to Asymmetric GL — the same shape the user uses successfully in manual fits. Asymmetric GL has only **one** asymmetry parameter (the `asymmetry` factor that broadens the high-BE side; CasaXPS-equivalent α). Combined with the existing FWHM and η, it has only one extra degree of freedom relative to plain GL — much harder for the optimizer to misuse. **And** plumb the asymmetry bounds [0.10, 0.50] from frontend `_afAsymMin`/`_afAsymMax` through to the backend `_set("asymmetry", ...)` call so the bounds are *actually enforced*.

The backend touch is the same pattern that already exists for center, FWHM, and amplitude bounds — so it's not new mechanism, just exposing a missing key.

### ISSUE 3 — manual follow-up fits drift centers off the auto-fit positions

After auto-fit converges, users frequently click "Run Fit" again to refine FWHMs/amplitudes. With centers free, the secondary fit can shift the converged auto-fit positions even when the user just wanted width refinement. Locking centers after auto-fit makes the secondary refinement do what the user expects, with a clearly-visible padlock the user can manually toggle off if they want a free re-fit.

### ISSUE 4 — sanity check

Re-verify FIX 1 from the previous round (`peaks[1]._afCenterMin = 284.80`) survives the lineshape change. No code edit; one grep.

---

## File map

| File | Action | Why |
|------|--------|-----|
| `templates/index.html` | Modify | All frontend changes: helper refactor (ISSUE 1), spec for graphite peak (ISSUE 2 frontend half), peakToBackendSpec to forward asymmetry bounds (ISSUE 2 frontend half), center-lock-after-auto-fit (ISSUE 3) |
| `fitting.py` | Modify | 2-line change: `_set("asymmetry", ...)` reads `spec.get("asymmetry_min", 0.0)` and `spec.get("asymmetry_max", 1.0)` (ISSUE 2 backend half) |
| `docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite.md` | Append | Document the round-2 follow-ups inline in the spec |
| `docs/superpowers/plans/2026-04-24-auto-fit-c1s-followup-fixes.md` | Append | Cross-link to this round-2 plan |
| `docs/superpowers/plans/2026-04-24-auto-fit-c1s-followup-2.md` | Create (this file) | The plan |

No `tests/` directory will be created. Pure-logic tests run inline via `venv/bin/python -c "..."` or scratch files in `/tmp/`, matching the round-1 pattern.

---

## Tasks

### Task 1: Refactor area-fraction helper to use frontend `_peakArea` (ISSUE 1)

**Files:**
- Modify: `templates/index.html:4860–4887` (helper rewrite)
- Modify: `templates/index.html:4958–4964` (caller signature change)
- Test: `/tmp/test_autofit_decide_warning.py` (Python port of pure decision logic)

- [ ] **Step 1: Write the Python port test for the pure decision function**

Create `/tmp/test_autofit_decide_warning.py` with the following exact content. This tests the *pure* decision logic that we'll extract from the helper. The function signature mirrors the JS:

```python
"""
Python port of _autoFitDecideAreaWarning(peakAreas, graphiteId).

Pure logic: given an array of {id, area} pairs and a graphite id, decide
whether to emit the warning toast. Returns None on no-warning,
{'fractionPct': float, 'warning': str} on warning.
"""

def decide(peak_areas, graphite_id):
    total = 0.0
    graphite_area = None
    for entry in peak_areas:
        a = entry.get("area")
        if not isinstance(a, (int, float)):
            continue
        # JS Number.isFinite excludes NaN/Inf; in Python guard with isfinite-ish
        if a != a:  # NaN
            continue
        if a == float("inf") or a == float("-inf"):
            continue
        if a < 0:
            continue
        total += a
        if str(entry.get("id")) == str(graphite_id):
            graphite_area = a
    if graphite_area is None or not (total > 0):
        return None
    fraction = graphite_area / total
    if fraction >= 0.40:
        return None
    fraction_pct = round(fraction * 1000) / 10.0  # 1 dp
    warning = (
        "Graphite area is only " + f"{fraction_pct:.1f}" +
        "% of the total C1s signal. This is below the typical 40% expected "
        "for a graphite-dominated sample. Review the fit and consider manual "
        "adjustment."
    )
    return {"fractionPct": fraction_pct, "warning": warning}


# ── Test cases ──────────────────────────────────────────────────────────
# Case 1: graphite at 45% of total → no warning
r = decide([{"id": 1, "area": 4500}, {"id": 2, "area": 5500}], 1)
assert r is None, f"case 1 expected None, got {r!r}"

# Case 2: graphite at 25% of total → warning with '25.0%'
r = decide([{"id": 1, "area": 2500}, {"id": 2, "area": 7500}], 1)
assert r is not None, "case 2 expected warning"
assert r["fractionPct"] == 25.0, f"case 2 pct = {r['fractionPct']}"
assert "25.0%" in r["warning"], f"case 2 warning = {r['warning']!r}"

# Case 3: exactly 40% → no warning (boundary)
r = decide([{"id": 1, "area": 4000}, {"id": 2, "area": 6000}], 1)
assert r is None, f"case 3 expected None at boundary, got {r!r}"

# Case 4: missing area data → no warning
r = decide([{"id": 1}, {"id": 2, "area": 1000}], 1)
assert r is None, f"case 4 expected None, got {r!r}"

# Case 5: 33.3% — the actual 8 A/C1s Scan.VGD failure case
r = decide([
    {"id": 1, "area": 3333.3},   # graphite
    {"id": 2, "area": 2000.0},   # adv1
    {"id": 3, "area": 2000.0},   # adv2
    {"id": 4, "area": 1500.0},   # adv3
    {"id": 5, "area": 1166.7},   # adv4
], 1)
assert r is not None, "case 5 expected warning"
assert r["fractionPct"] == 33.3, f"case 5 pct = {r['fractionPct']}"
assert "33.3%" in r["warning"], f"case 5 warning = {r['warning']!r}"

# Case 6: malformed input (non-list) → no warning
r = decide([], 1)
assert r is None

# Case 7: id type mismatch (int vs string) tolerated via str() coercion
r = decide([{"id": "1", "area": 2500}, {"id": "2", "area": 7500}], 1)
assert r is not None, "case 7 expected warning despite int/string id mismatch"

print("OK — all 7 cases pass")
```

- [ ] **Step 2: Run the test to confirm it passes against the Python port (sanity)**

Run: `venv/bin/python /tmp/test_autofit_decide_warning.py`
Expected output: `OK — all 7 cases pass`

(The Python port is the spec; the JS implementation in step 3 must mirror it exactly.)

- [ ] **Step 3: Replace the JS helper with a split (pure decision + state-aware wrapper)**

Edit `templates/index.html`. Locate the existing helper at line 4860-onward (function `_autoFitCheckGraphiteFraction(json, graphiteId)`). Replace the entire function block (the 28 lines from the `// Compute graphite's area fraction…` comment block at line 4860 through the closing `}` at line 4887) with the following:

```js
// Pure decision: given (id, area) pairs and graphite's id, decide whether
// to emit the < 40% area-fraction warning toast. Returns null on no-warning,
// or { fractionPct, warning } on warning. Boundary: '< 0.40' so 0.40 itself
// does NOT warn.
//
// This logic is intentionally state-free so the Python port test in
// /tmp/test_autofit_decide_warning.py can validate it without simulating
// state.peaks or the backend.
function _autoFitDecideAreaWarning(peakAreas, graphiteId) {
  if (!Array.isArray(peakAreas)) return null;
  let total = 0;
  let graphiteArea = null;
  for (const entry of peakAreas) {
    if (!entry) continue;
    const a = entry.area;
    if (!Number.isFinite(a) || a < 0) continue;
    total += a;
    if (String(entry.id) === String(graphiteId)) graphiteArea = a;
  }
  if (graphiteArea == null || !(total > 0)) return null;
  const fraction = graphiteArea / total;
  if (fraction >= 0.40) return null;
  const fractionPct = Math.round(fraction * 1000) / 10;  // 1 decimal
  const warning =
    'Graphite area is only ' + fractionPct.toFixed(1) +
    '% of the total C1s signal. This is below the typical 40% expected ' +
    'for a graphite-dominated sample. Review the fit and consider manual ' +
    'adjustment.';
  return { fractionPct, warning };
}

// State-aware wrapper: build (id, area) pairs from the current state using
// _peakArea — the SAME integration the user-visible AREA column uses. This
// guarantees the warning fires iff the AREA column shows the same number
// crossing the threshold (no more frontend/backend disagreement on areas).
function _autoFitCheckGraphiteFraction(graphiteId) {
  const be = state.fitResult && state.fitResult.be;
  if (!Array.isArray(be) || be.length < 2) return null;
  const peakAreas = state.peaks.map(p => ({ id: p.id, area: _peakArea(p, be) }));
  return _autoFitDecideAreaWarning(peakAreas, graphiteId);
}
```

- [ ] **Step 4: Update the caller signature in `applyAutoFitResult`**

Find the call site (currently at line 4960-4964 in `applyAutoFitResult`). The existing two-arg call needs to drop the `json` argument:

Replace:
```js
  // 8. Sanity check: warn if graphite area fraction is below 40%. The fit
  // is kept regardless — this is a triage signal, not a fit-quality gate.
  const gPeak2 = state.peaks.find(p => p.name === 'Graphite') || state.peaks[0];
  if (gPeak2) {
    const check = _autoFitCheckGraphiteFraction(json, gPeak2.id);
    if (check) notify(check.warning, 'amber', true);
  }
```

with:
```js
  // 8. Sanity check: warn if graphite area fraction is below 40%. The fit
  // is kept regardless — this is a triage signal, not a fit-quality gate.
  // Uses _peakArea so the warning matches the user-visible AREA column
  // exactly (and so it doesn't depend on backend response shape).
  const gPeak2 = state.peaks.find(p => p.name === 'Graphite') || state.peaks[0];
  if (gPeak2) {
    const check = _autoFitCheckGraphiteFraction(gPeak2.id);
    if (check) notify(check.warning, 'amber', true);
  }
```

(The `json` parameter is still in `applyAutoFitResult`'s signature — it's used elsewhere in the function. Don't touch the function signature.)

- [ ] **Step 5: Verify structural integrity (braces / parens balance + helper exists in served HTML)**

Run: `venv/bin/python -c "import re; html = open('templates/index.html').read(); assert html.count('function _autoFitDecideAreaWarning') == 1; assert html.count('function _autoFitCheckGraphiteFraction') == 1; assert '_autoFitCheckGraphiteFraction(gPeak2.id)' in html; assert '_autoFitCheckGraphiteFraction(json' not in html; assert html.count('{') == html.count('}'), 'brace mismatch'; print('OK')"`
Expected output: `OK`

- [ ] **Step 6: Reload gunicorn and confirm served HTML has both functions**

Run: `pkill -HUP -F gunicorn.ctl 2>/dev/null; sleep 1; curl -s http://localhost:5000/ | grep -c '_autoFitDecideAreaWarning\|_autoFitCheckGraphiteFraction'`
Expected output: `4` (two declarations + one wrapper-internal call to `_autoFitDecideAreaWarning` + one caller of `_autoFitCheckGraphiteFraction`)

If gunicorn isn't running, skip the reload and run only the curl with `--connect-timeout 2 || echo "gunicorn not running, skip"`.

- [ ] **Step 7: Commit**

```bash
git add templates/index.html
git commit -m "$(cat <<'EOF'
fix(autofit): use _peakArea for graphite-area warning helper

The previous helper read ip.params.area.value from the /api/fit response.
The peak-list AREA column uses _peakArea(p, be) (frontend integration
via evalPeak). For LA shapes the JS and Python lineshape implementations
diverge enough that the backend area can sit on the opposite side of
the 40% threshold from the visible AREA column — silently swallowing
the warning toast (observed on 8 A/C1s Scan.VGD: AREA column 33.3%,
no warning fired).

Also splits the helper into a pure decision function (testable from a
Python port) and a state-aware wrapper. The pure function is exercised
by /tmp/test_autofit_decide_warning.py with 7 cases including the
33.3% real-data failure mode.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Plumb asymmetry bounds through to lmfit Parameter (ISSUE 2 backend half)

**Files:**
- Modify: `fitting.py:617–620` (master-peak path, asymmetric_gl branch)
- Modify: `fitting.py:655–657` (free-peak path, asymmetric_gl branch)
- Modify: `templates/index.html:4488–4492` (peakToBackendSpec for asym-GL)
- Modify: `templates/index.html:5052–5061` (peakSpecs builder in runAutoFitC1sGraphite)
- Test: `/tmp/test_asymmetry_bounds.py` (lmfit-level test)

**This task touches `fitting.py`. Per the user's spec, this requires explicit approval before execution. The change is a 2-line edit: replace `min_=0.0, max_=1.0` with `min_=spec.get("asymmetry_min", 0.0)` and `max_=spec.get("asymmetry_max", 1.0)` in two places — exactly mirroring the existing `center_min`/`center_max`/`fwhm_min`/`fwhm_max` pattern used elsewhere in the same function.**

- [ ] **Step 1: Write the failing lmfit-level test**

Create `/tmp/test_asymmetry_bounds.py`:

```python
"""
Verify that spec.asymmetry_min / spec.asymmetry_max in the peak spec actually
reach the lmfit Parameter's .min / .max attributes. Without this, frontend-
declared bounds are silently dropped and the optimizer can drive asymmetry
to whatever the hardcoded backend allows (currently 0.0).
"""
import sys
sys.path.insert(0, "/home/skye/xps-app")

from lmfit import Model
from fitting import _make_peak_params, _asymmetric_gl

# Build a one-peak asymmetric_gl spec WITH bounds set
spec = {
    "id": "1",
    "shape": "asymmetric_gl",
    "center": 284.5,
    "amplitude": 1000.0,
    "fwhm": 0.7,
    "gl_ratio": 0.30,
    "asymmetry": 0.25,
    "asymmetry_min": 0.10,
    "asymmetry_max": 0.50,
}

model = Model(_asymmetric_gl, prefix="p1_")
params = _make_peak_params(model, spec, "p1_", [spec])

asym_par = params["p1_asymmetry"]
assert asym_par.min == 0.10, f"asymmetry min = {asym_par.min}, expected 0.10"
assert asym_par.max == 0.50, f"asymmetry max = {asym_par.max}, expected 0.50"
assert asym_par.value == 0.25, f"asymmetry value = {asym_par.value}, expected 0.25"
assert asym_par.vary is True, f"asymmetry vary = {asym_par.vary}, expected True"

# Default-fallback: spec without bounds → defaults [0.0, 1.0]
spec_default = {
    "id": "2",
    "shape": "asymmetric_gl",
    "center": 286.0,
    "amplitude": 500.0,
    "fwhm": 1.0,
    "gl_ratio": 0.30,
    "asymmetry": 0.0,
}
params2 = _make_peak_params(model, spec_default, "p2_", [spec_default])
asym_par2 = params2["p2_asymmetry"]
assert asym_par2.min == 0.0, f"default asymmetry min = {asym_par2.min}, expected 0.0"
assert asym_par2.max == 1.0, f"default asymmetry max = {asym_par2.max}, expected 1.0"

print("OK — asymmetry bounds plumbing verified")
```

- [ ] **Step 2: Run the test to verify it fails on current backend**

Run: `venv/bin/python /tmp/test_asymmetry_bounds.py`
Expected: `AssertionError: asymmetry min = 0.0, expected 0.10`
(Confirms the bounds are NOT currently honored — this is the bug.)

- [ ] **Step 3: Patch `fitting.py` — free-peak path**

Edit `fitting.py`. Locate the `if shape == "asymmetric_gl":` block in the free-peak path (lines 655-657 in the current file):

Replace:
```python
    if shape == "asymmetric_gl":
        _set("asymmetry", asymmetry, min_=0.0, max_=1.0,
             vary=not spec.get("fix_asymmetry", False))
```

with:
```python
    if shape == "asymmetric_gl":
        _set("asymmetry", asymmetry,
             min_=spec.get("asymmetry_min", 0.0),
             max_=spec.get("asymmetry_max", 1.0),
             vary=not spec.get("fix_asymmetry", False))
```

- [ ] **Step 4: Patch `fitting.py` — master-peak (constrained) path**

Locate the `if shape == "asymmetric_gl":` block inside the `if master_id is not None:` branch (lines 617-620). Same idea, but the `_set` call here also has an `expr=` arg for spin-orbit constraints; we only override the bounds:

Replace:
```python
        if shape == "asymmetric_gl":
            _set("asymmetry", asymmetry,
                 expr=f"{m_prefix}asymmetry" if spec.get("fix_fwhm", True) else None,
                 min_=0.0, max_=1.0)
```

with:
```python
        if shape == "asymmetric_gl":
            _set("asymmetry", asymmetry,
                 expr=f"{m_prefix}asymmetry" if spec.get("fix_fwhm", True) else None,
                 min_=spec.get("asymmetry_min", 0.0),
                 max_=spec.get("asymmetry_max", 1.0))
```

(Note: when `expr` is set, `_set` ignores min/max and pins the parameter via the expression — but spec.asymmetry_min/max being present still allows future code to use them when expr is None. Setting them here keeps the two paths symmetric.)

- [ ] **Step 5: Run the test to verify it passes**

Run: `venv/bin/python /tmp/test_asymmetry_bounds.py`
Expected: `OK — asymmetry bounds plumbing verified`

- [ ] **Step 6: Forward bounds from frontend `peakToBackendSpec` (asym-GL branch)**

Edit `templates/index.html`. Locate the asym-GL branch in `peakToBackendSpec` (lines 4488-4492):

Replace:
```js
  } else if (shape === 'asym-GL') {
    spec.shape = 'asymmetric_gl';
    spec.gl_ratio = (p.glMix || 50) / 100;
    spec.asymmetry = p.asymmetry || 0;
    spec.fix_asymmetry = !!p.fixAsymmetry;
  } else if (shape === 'DS' || shape === 'DSG') {
```

with:
```js
  } else if (shape === 'asym-GL') {
    spec.shape = 'asymmetric_gl';
    spec.gl_ratio = (p.glMix || 50) / 100;
    spec.asymmetry = p.asymmetry || 0;
    spec.fix_asymmetry = !!p.fixAsymmetry;
    // Forward auto-fit asymmetry bounds when present (set by buildAutoFitModel).
    // For non-auto-fit peaks these fields are absent and the backend falls back
    // to its [0.0, 1.0] default.
    if (Number.isFinite(p._afAsymMin)) spec.asymmetry_min = p._afAsymMin;
    if (Number.isFinite(p._afAsymMax)) spec.asymmetry_max = p._afAsymMax;
  } else if (shape === 'DS' || shape === 'DSG') {
```

- [ ] **Step 7: Verify structural integrity**

Run: `venv/bin/python -c "html = open('templates/index.html').read(); assert 'asymmetry_min' in html; assert 'asymmetry_max' in html; assert html.count('{') == html.count('}'); print('OK')"`
Expected output: `OK`

Run: `venv/bin/python -c "src = open('fitting.py').read(); assert 'asymmetry_min' in src; assert 'asymmetry_max' in src; print('OK')"`
Expected output: `OK`

- [ ] **Step 8: Reload gunicorn and verify**

Run: `pkill -HUP -F gunicorn.ctl 2>/dev/null; sleep 1; venv/bin/python /tmp/test_asymmetry_bounds.py`
Expected: `OK — asymmetry bounds plumbing verified`

- [ ] **Step 9: Commit**

```bash
git add fitting.py templates/index.html
git commit -m "$(cat <<'EOF'
feat(fitting): plumb asymmetric_gl asymmetry bounds via spec keys

The asymmetric_gl 'asymmetry' lmfit Parameter previously had hardcoded
bounds [0.0, 1.0]. Frontend-declared bounds (set on peak metadata for
auto-fit) were silently dropped, letting the optimizer drive asymmetry
to 0.0 — collapsing the shape to symmetric and propagating the high-BE
shoulder into adjacent peaks.

Now spec.asymmetry_min / spec.asymmetry_max in the peak spec are read
by _make_peak_params and applied to the lmfit Parameter, mirroring the
existing center_min/center_max/fwhm_min/fwhm_max pattern. Defaults
unchanged (0.0, 1.0) so non-auto-fit peaks behave identically.

peakToBackendSpec forwards _afAsymMin / _afAsymMax onto these spec keys
when present.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Switch graphite from LA to Asymmetric GL in `buildAutoFitModel` (ISSUE 2 frontend half)

**Files:**
- Modify: `templates/index.html:4717–4732` (graphite peak spec)
- Modify: `templates/index.html:4791–4792` (per-peak bound metadata for graphite)

- [ ] **Step 1: Replace the graphite peak spec**

Edit `templates/index.html`. Locate the graphite peak push in `buildAutoFitModel` (lines 4716-4732):

Replace:
```js
  // Graphite — LA shape, beta fixed at 0.05, alpha bounded [0.05, 0.20].
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
```

with:
```js
  // Graphite — Asymmetric GL (η + α). Replaces LA(α,β,m) which had three
  // free shape params and was being driven to α=0 (symmetric collapse) by
  // the optimizer on real data, propagating the high-BE shoulder into adv1.
  // Asymmetric GL has a single asymmetry knob with enforceable bounds and
  // matches what users employ successfully in manual fits.
  peaks.push(defaultPeak({
    name: 'Graphite',
    shape: 'asym-GL',
    center: 284.50,
    fwhm: 0.7,
    amplitude: Math.max(1, assessment.graphiteHeight || 1000),
    glMix: 30,            // η = 30% Lorentzian, free
    asymmetry: 0.25,      // start mid-bound; bounds enforced via _afAsymMin/Max
    fixGlMix: false,
    fixAsymmetry: false,
    fixCenter: false,
    fixFwhm: false,
    fixAmplitude: false,
  }));
```

- [ ] **Step 2: Add asymmetry bound metadata for graphite in the bounds block**

Locate the per-peak bound metadata block (lines 4790-4792 currently):

Replace:
```js
  // Per-peak bound metadata, consumed in runAutoFitC1sGraphite.
  peaks[0]._afCenterMin = 284.50 - 0.30; peaks[0]._afCenterMax = 284.50 + 0.30;
  peaks[0]._afFwhmMin   = 0.40;          peaks[0]._afFwhmMax   = 1.20;
```

with:
```js
  // Per-peak bound metadata, consumed in runAutoFitC1sGraphite.
  peaks[0]._afCenterMin = 284.50 - 0.30; peaks[0]._afCenterMax = 284.50 + 0.30;
  peaks[0]._afFwhmMin   = 0.40;          peaks[0]._afFwhmMax   = 1.20;
  peaks[0]._afAsymMin   = 0.10;          peaks[0]._afAsymMax   = 0.50;
```

- [ ] **Step 3: Verify structural integrity**

Run: `venv/bin/python -c "html = open('templates/index.html').read(); assert \"shape: 'asym-GL',\" in html.replace('  ', ' '); assert '_afAsymMin   = 0.10' in html or '_afAsymMin = 0.10' in html; assert html.count('{') == html.count('}'); print('OK')"`
Expected output: `OK`

- [ ] **Step 4: Reload gunicorn and verify served HTML reflects the change**

Run: `pkill -HUP -F gunicorn.ctl 2>/dev/null; sleep 1; curl -s http://localhost:5000/ | grep -c \"shape: 'asym-GL'\"`
Expected: at least `1` (the graphite peak push) — possibly more if asym-GL appears in demo data.

Run: `curl -s http://localhost:5000/ | grep -c '_afAsymMin'`
Expected: `1`

- [ ] **Step 5: Commit**

```bash
git add templates/index.html
git commit -m "$(cat <<'EOF'
feat(autofit): switch graphite from LA to Asymmetric GL

LA(α,β,m) has three free shape parameters and was over-fit on real C1s
data — the optimizer drove α to 0.000 (symmetric collapse) on the
8 A/C1s Scan.VGD spectrum, causing the high-BE graphite shoulder to be
absorbed by Adventitious 1 (which fattened to FWHM 2.17 eV).

Asymmetric GL replaces LA: one asymmetry parameter (α=0.25 start, bounds
[0.10, 0.50] now actually enforced via the asymmetry_min/asymmetry_max
backend plumbing from the previous commit), one mixing parameter
(η=30% start, free), plus center/FWHM/amplitude. Same shape the user
uses successfully in manual fits.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Lock peak centers after a successful auto-fit (ISSUE 3)

**Files:**
- Modify: `templates/index.html:4948` (just before `renderPeakList()` in `applyAutoFitResult`)

- [ ] **Step 1: Find the exact spot to insert the lock**

The mutation must happen AFTER `applyBackendResult(json)` runs (which sets `p.center` from the fit result) and BEFORE `renderPeakList()` so the UI immediately reflects the locked state. The cleanest location is in `applyAutoFitResult` step 6, just before the existing `renderPeakList()` call.

Edit `templates/index.html`. Locate the block at lines 4946-4951 (in `applyAutoFitResult` step 6):

Replace:
```js
  if (typeof _updateRFactorUI === 'function') _updateRFactorUI(state.fitResult.rFactor);
  if (typeof _updateROIDisplay === 'function') _updateROIDisplay(roiRange);
  if (typeof renderPeakList === 'function') renderPeakList();
  if (typeof updatePlot === 'function') updatePlot();
  if (typeof renderResults === 'function') renderResults();
  if (typeof _autoSnapshot === 'function') _autoSnapshot();
```

with:
```js
  if (typeof _updateRFactorUI === 'function') _updateRFactorUI(state.fitResult.rFactor);
  if (typeof _updateROIDisplay === 'function') _updateROIDisplay(roiRange);
  // Lock all peak centers after a successful auto-fit. Users frequently
  // run "Run Fit" again to refine FWHMs/amplitudes; without this lock the
  // converged auto-fit positions can drift. The user can manually unlock
  // any center via the existing padlock icon in the peak editor.
  for (const p of state.peaks) p.fixCenter = true;
  if (typeof renderPeakList === 'function') renderPeakList();
  if (typeof updatePlot === 'function') updatePlot();
  if (typeof renderResults === 'function') renderResults();
  if (typeof _autoSnapshot === 'function') _autoSnapshot();
```

- [ ] **Step 2: Verify structural integrity**

Run: `venv/bin/python -c "html = open('templates/index.html').read(); assert 'for (const p of state.peaks) p.fixCenter = true;' in html; assert html.count('{') == html.count('}'); print('OK')"`
Expected output: `OK`

- [ ] **Step 3: Reload gunicorn and confirm the change is in served HTML**

Run: `pkill -HUP -F gunicorn.ctl 2>/dev/null; sleep 1; curl -s http://localhost:5000/ | grep -c 'p.fixCenter = true;'`
Expected: at least `1`.

- [ ] **Step 4: Commit**

```bash
git add templates/index.html
git commit -m "$(cat <<'EOF'
feat(autofit): lock peak centers after successful auto-fit

Users frequently click 'Run Fit' after auto-fit to refine FWHMs and
amplitudes. With centers free, this secondary fit drifts the converged
auto-fit positions even when the user only intended width refinement.

After applyAutoFitResult succeeds, set fixCenter=true on every peak.
Other parameters (FWHM, amplitude, η, α) remain free. The user can
manually unlock any center via the existing padlock icon in the peak
editor — no new UI.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: Sanity-verify FIX 1 from previous round still applies to adv1 (ISSUE 4)

**Files:** none (read-only verification)

- [ ] **Step 1: Confirm `peaks[1]._afCenterMin = 284.80` is still present and unchanged**

Run: `grep -n "peaks\[1\]._afCenterMin" /home/skye/xps-app/templates/index.html`
Expected: exactly one match, of the form `4800:  peaks[1]._afCenterMin = 284.80;        peaks[1]._afCenterMax = 284.80 + 0.50;`
(Line number may shift after Task 3's edit; the content must match.)

- [ ] **Step 2: Confirm peaks[1] is still Adventitious 1**

Run: `venv/bin/python -c "
html = open('templates/index.html').read()
# Find the adv definitions block — adv1 should be at array index 0 (peaks[1] after graphite)
import re
m = re.search(r\"const adv = \\[\\s*\\{ name: 'Adventitious 1'\", html)
assert m, 'Adventitious 1 not first in adv array'
print('OK — peaks[1] is Adventitious 1, floor 284.80 still applies')
"`
Expected output: `OK — peaks[1] is Adventitious 1, floor 284.80 still applies`

(No commit — verification only.)

---

### Task 6: Update spec doc with round-2 follow-up notes

**Files:**
- Modify: `docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite.md` (append a section)

- [ ] **Step 1: Append a "Follow-up fixes round 2" section to the spec**

Append exactly the following to the bottom of `docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite.md`:

```markdown

---

## Follow-up fixes — Round 2 (2026-04-24)

After real-data testing of the round-1 fixes, three additional issues surfaced.
This section is additive; nothing earlier in the spec is rescinded.

### ISSUE 1 (BUG): graphite-area-fraction warning toast was silently swallowed

**Symptom:** On `8 A/C1s Scan.VGD`, the peak-list AREA column reported
graphite at 33.3% — well below the 40% warning threshold added in round 1
— but no amber warning toast appeared.

**Root cause:** the round-1 helper read `json.individual_peaks[i].params.area.value`
(backend trapezoid integration of the *backend* lineshape). The user-visible
AREA column uses `_peakArea(p, be)` (frontend integration of the *frontend*
lineshape via `evalPeak`). For LA shapes the JS and Python implementations
diverge enough that the backend-side area can sit on the opposite side of
the 40% threshold from the visible AREA column.

**Fix:** rewrite the helper to use `_peakArea` against `state.peaks` and
`state.fitResult.be` — the same source the visible AREA column uses. The
warning now fires iff the AREA column shows the same number crossing the
threshold (no more disagreement). The pure decision logic is split into
`_autoFitDecideAreaWarning(peakAreas, graphiteId)` so it can be unit-tested
in isolation from state.

### ISSUE 2 (ALGORITHM CHANGE): graphite shape switched from LA(α,β,m) to Asymmetric GL

**Symptom:** With LA, the optimizer drove α to ~0.000 on the same real-data
spectrum, collapsing graphite to a symmetric line. The high-BE graphite
shoulder was then absorbed by Adventitious 1, which fattened to FWHM 2.17 eV
(unphysical for sp³ adventitious carbon).

**Root cause:** LA has three free shape parameters (α, β, m) — over-parameterised
relative to the data's information content. Worse, the round-1 frontend
declared α bounds [0.05, 0.20] but the backend hardcoded `min_=0.0, max_=0.49`
for `la_casaxps` α — the frontend bounds were silently dropped. (Same was true
for `asymmetric_gl`'s asymmetry parameter: hardcoded `[0.0, 1.0]` with no
spec-key override.)

**Fix:** Two parts.

1. *Backend plumbing* (2-line edit in `fitting.py`): the `asymmetric_gl`
   branch of `_make_peak_params` now reads `spec.get("asymmetry_min", 0.0)`
   and `spec.get("asymmetry_max", 1.0)` — same pattern already used for
   center, FWHM, amplitude. Defaults unchanged (so non-auto-fit peaks
   behave identically).

2. *Lineshape switch* (frontend): graphite uses `shape: 'asym-GL'` with
   `glMix: 30` (η, free), `asymmetry: 0.25` (α, free, bounds [0.10, 0.50]
   now actually enforced via `_afAsymMin`/`_afAsymMax` overlaid by
   `peakToBackendSpec` onto `spec.asymmetry_min`/`spec.asymmetry_max`).
   Center bounds, FWHM bounds, and amplitude bounds unchanged.

LA was kept available as a manual-mode peak shape for users who prefer it;
auto-fit no longer uses it.

### ISSUE 3 (FEATURE): peak centers are locked after a successful auto-fit

**Rationale:** Users frequently run a manual "Run Fit" after auto-fit to
refine FWHMs and amplitudes. With centers free this secondary fit drifts
the converged auto-fit positions; locking centers makes the secondary
refinement do what the user expects.

**Implementation:** After `applyAutoFitResult` succeeds, every peak's
`fixCenter` is set to `true` before the peak list re-renders. Users can
manually unlock any center via the existing padlock icon — no new UI.
Other parameters (FWHM, amplitude, η, α) remain unlocked.

### ISSUE 4 (sanity check)

The round-1 adv1 lower-bound floor (`peaks[1]._afCenterMin = 284.80`) still
applies after the lineshape change.
```

- [ ] **Step 2: Verify the file ends with the new section**

Run: `tail -20 /home/skye/xps-app/docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite.md`
Expected: visible `### ISSUE 4 (sanity check)` heading and the closing paragraph.

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite.md
git commit -m "$(cat <<'EOF'
docs(autofit): record round-2 follow-up fixes in spec

Append a 'Follow-up fixes — Round 2' section documenting ISSUE 1
(area-fraction helper now uses _peakArea), ISSUE 2 (graphite LA→asym-GL
with backend-plumbed asymmetry bounds), and ISSUE 3 (auto-lock peak
centers after auto-fit). ISSUE 4 verified as still-correct.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 7: Cross-link the round-1 follow-up plan to round 2

**Files:**
- Modify: `docs/superpowers/plans/2026-04-24-auto-fit-c1s-followup-fixes.md` (append a pointer)

- [ ] **Step 1: Append a "Round 2" pointer**

Append exactly the following to the bottom of `docs/superpowers/plans/2026-04-24-auto-fit-c1s-followup-fixes.md`:

```markdown

---

## Round 2 (2026-04-24)

A second round of follow-ups was triaged after real-data testing of these
fixes. The round-2 plan lives at:
`docs/superpowers/plans/2026-04-24-auto-fit-c1s-followup-2.md`.

It addresses three issues:

1. **The < 40% warning toast was silently swallowed** because the round-1
   helper read backend-computed areas while the user-visible AREA column
   uses frontend-computed areas; the round-2 helper aligns with the AREA
   column's source.
2. **Graphite's lineshape changes from LA(α,β,m) to Asymmetric GL** because
   LA was over-parameterised and converging to α=0 on real data; the bound
   plumbing also gets fixed in the backend so frontend-declared α bounds
   are now enforced.
3. **Peak centers are locked after a successful auto-fit** so manual
   follow-up "Run Fit" passes can refine widths/amplitudes without
   drifting the converged positions.
```

- [ ] **Step 2: Verify**

Run: `tail -25 /home/skye/xps-app/docs/superpowers/plans/2026-04-24-auto-fit-c1s-followup-fixes.md`
Expected: visible `## Round 2 (2026-04-24)` heading.

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/plans/2026-04-24-auto-fit-c1s-followup-fixes.md
git commit -m "$(cat <<'EOF'
docs(autofit): point round-1 follow-up plan at round-2 plan

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 8: Browser verification checklist (handoff)

**Files:** none (manual verification by the user)

This task does not run automatically. After Tasks 1-7 are committed, present the user with the following checklist exactly. The user has previously walked similar checklists by hand on real data (round 1 and Phase 1).

**Verification scenarios to walk through:**

**A. ISSUE 1 — warning toast actually fires.** Load `8 A/C1s Scan.VGD` (the known-failing case). Run Auto-Fit → confirm:
   - Graphite area in the AREA column is below 40%
   - Amber warning toast appears with the correct percentage in the text (e.g., `"Graphite area is only 33.3% of the total C1s signal. …"`)
   - The toast persists (does not auto-dismiss; matches `notify(msg, 'amber', true)` semantics)

**B. ISSUE 2 — Asymmetric GL replaces LA on graphite.** Same 8 A spectrum. Run Auto-Fit → confirm:
   - Graphite peak's lineshape dropdown shows `Asymmetric GL (α asymmetry)` (NOT `LA (α,β,m)`)
   - Graphite α (asymmetry) parameter is between 0.10 and 0.50 (NOT 0.000) — the bound is enforced
   - Graphite area fraction is **higher** than the previous LA-based fit (was 33.3%; expected substantially higher with proper asymmetry)
   - Adventitious 1 FWHM is **narrower** than the previous fit (was 2.17 eV)
   - The amber warning toast may or may not appear depending on whether graphite still ends below 40% — both are acceptable; the warning logic is correct, the question is whether the new shape brings graphite above 40%.

**C. ISSUE 2 — known-good case regression.** Load `Project10D.proj.json`. Run Auto-Fit → confirm:
   - Graphite area is still well above 40% (was 48.8% with LA)
   - No amber warning toast
   - Visual fit quality comparable or better

**D. ISSUE 3 — center locks appear after auto-fit.** On any spectrum, after Auto-Fit completes, expand each peak in the peak editor. For each peak:
   - The "Center (eV)" field shows the **closed** padlock icon (🔒) and is read-only/dimmed
   - The "FWHM (eV)" and "Amplitude" fields show the **open** padlock icon (🔓) and are editable
   - Clicking the center padlock unlocks it (toggles to 🔓) — confirms manual override still works

**E. ISSUE 4 — adv1 floor sanity.** Same auto-fit. Confirm:
   - Adventitious 1's center value is ≥ 284.80 eV (the round-1 floor)

**F. Regression — no Phase-1 functionality lost.** Three test scenarios from the Phase-1 checklist:
   - Spectrum with 0 unknown low-BE peaks → auto-fit creates Graphite + 4 adventitious only
   - Spectrum with 1 unknown → adds Unknown 1
   - Spectrum with 2 unknowns → adds Unknown 1 and Unknown 2
   - Tab switch / ROI edit / non-C1s tab disable behaviour unchanged
   - Confirmation modal still appears when peaks already exist

**Reporting back:**
- If everything passes → push the round-2 commits to origin/main.
- If anything fails → paste the symptom + browser console output. The plan author will patch the specific failure.

(No commit for this task — manual verification only.)

---

## Self-review

Spec coverage check:

| Spec section | Task |
|--------------|------|
| ISSUE 1 (warning helper not firing) | Task 1 |
| ISSUE 1 unit test | Task 1, Step 1-2 |
| ISSUE 2 (LA → Asymmetric GL) | Task 3 |
| ISSUE 2 (bounds actually enforced) | Task 2 |
| ISSUE 2 backend bound-plumbing test | Task 2, Step 1-5 |
| ISSUE 3 (lock centers after auto-fit) | Task 4 |
| ISSUE 3 — uses existing fixCenter mechanism | Task 4 (per-peak `p.fixCenter = true`) |
| ISSUE 4 (adv1 floor sanity) | Task 5 |
| Browser verification checklist | Task 8 |
| Spec doc update | Task 6 |
| Round-1 plan cross-link | Task 7 |

No gaps.

Type/identifier consistency check:

- `_autoFitDecideAreaWarning(peakAreas, graphiteId)` defined in Task 1 Step 3, called in same step. Pure function, no state.
- `_autoFitCheckGraphiteFraction(graphiteId)` (one arg) defined in Task 1 Step 3, called in Task 1 Step 4. Wrapper.
- Spec keys `asymmetry_min` / `asymmetry_max` defined in Task 2 Step 1 test, used in Task 2 Step 3-4 backend, emitted by Task 2 Step 6 frontend, consumed by Task 3 Step 2 metadata (`_afAsymMin` / `_afAsymMax`).
- `p.fixCenter` (boolean) defined in existing peak schema, mutated in Task 4 Step 1, consumed by existing `peakToBackendSpec` (line 4472: `fix_center: !!p.fixCenter`) — already wired through to backend.

No placeholder scan: searched the document for "TBD", "TODO", "fill in", "implement later", "appropriate error handling", "similar to" — none present.
