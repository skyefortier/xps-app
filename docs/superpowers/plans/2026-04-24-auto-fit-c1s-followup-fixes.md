# Auto-Fit C1s Graphite — Follow-up Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix two real-data failure modes in the shipped Auto-Fit C1s Graphite feature: (FIX 1) Adventitious 1 sliding below graphite, and (FIX 2) graphite area-fraction < 40% going un-flagged.

**Architecture:** Frontend-only changes inside `templates/index.html`. FIX 1 is a one-line bound change in `buildAutoFitModel`. FIX 2 adds one helper `_autoFitCheckGraphiteFraction` and a single `notify()` call inside `applyAutoFitResult`. Backend (`fitting.py`, `app.py`) is **not** modified.

**Tech Stack:** Vanilla JS in `templates/index.html`; Python 3 (lmfit) backend via `/api/fit`, unchanged.

---

## Spec source

This plan implements the two fixes specified by the user on 2026-04-24, building on the shipped Auto-Fit C1s Graphite feature documented in:

- `docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite.md` (spec)
- `docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite-implementation.md` (Phase-1 implementation plan)

Both fixes are additive. No previously-shipped behavior should regress.

## FIX 1 backend feasibility — already decided

The user gave two attempts in priority order:
1. **lmfit parameter expression** linking adv1's center lower bound to graphite's center.
2. **Static computed lower bound** in the frontend.

I verified the backend's `_set` helper (`fitting.py:583-589`) does accept an `expr` string, but lmfit's expression mechanism *fixes* a parameter to the expression's value (no degrees of freedom) — it cannot be used as a lower-bound. Properly enforcing "adv1.center ≥ graphite.center + 0.3" via lmfit requires injecting a derived parameter (`p_sep = p_adv1.center − p_graphite.center` with `min=0.3`); the current backend has no per-spec mechanism to do this and adding one is **substantially more than 10 lines** of architectural change.

**Decision: Attempt 2 (static frontend bound).** No backend changes.

The trade-off: adv1's lower bound is fixed at `284.80` in the corrected BE frame, regardless of where graphite actually lands inside its `±0.3` window. Worst case (graphite drifts to 284.80 — its upper bound) puts adv1's floor exactly at graphite's ceiling — overlap is technically possible but only when both peaks are pinned to bounds, which itself indicates a poor fit. In practice graphite-matrix samples land graphite very near 284.50, so the floor sits ≥ 0.3 eV above graphite and the chemical constraint is honored.

## Scope / Non-Goals

- **No** changes to `fitting.py` or `app.py`.
- **No** changes to graphite bounds (still `284.50 ± 0.30`).
- **No** changes to adventitious 2/3/4 bounds.
- **No** changes to low-BE peak detection logic.
- **No** new menu entries, buttons, modals, settings, or persistence.
- The 40% threshold is hardcoded; not user-configurable in this phase.

---

## File structure

| File | Responsibility |
|---|---|
| `templates/index.html` | Both code fixes (one bound change + one helper + one toast call). |
| `docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite.md` | Append a "Follow-up fixes" section. |
| `docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite-implementation.md` | Append a pointer to this plan. |

No new files, no test files (no JS test harness exists in the project).

---

## Testing strategy

Same layered approach as the Phase-1 plan:

1. **Structural grep** after the FIX 1 line change.
2. **Python-port unit test** for the FIX 2 fraction-compute helper — pure logic, four assertions covering the stated boundary cases.
3. **Browser manual checklist** (Task 5) — four items focused on the two fixes plus a Phase-1 regression check.

Each task ends with a single `git commit`.

---

## Task 1: FIX 1 — clamp Adventitious 1 lower bound to 284.80

**Files:**
- Modify: `templates/index.html:4793`

The current line in `buildAutoFitModel` (verified at `templates/index.html:4793`):

```js
  peaks[1]._afCenterMin = 284.80 - 0.50; peaks[1]._afCenterMax = 284.80 + 0.50;
```

`peaks[1]` is the Adventitious 1 peak; the value `284.80 - 0.50 = 284.30` is the bug — it allows adv1 to slide *below* graphite's lower bound (284.20). We change the lower bound to `284.80` (= graphite_init `284.50` + the chemical 0.3 eV separation) while leaving the upper bound `284.80 + 0.50 = 285.30` unchanged.

- [ ] **Step 1: Apply the edit**

Find the exact line:

```js
  peaks[1]._afCenterMin = 284.80 - 0.50; peaks[1]._afCenterMax = 284.80 + 0.50;
```

Replace with:

```js
  // Adventitious carbon (sp3) is always at higher BE than graphitic sp2 carbon.
  // The lower bound is fixed at 284.80 eV (= graphite_init 284.50 + 0.30 eV
  // chemical separation). Trade-off: this is a STATIC corrected-frame floor,
  // not relative to graphite's fitted center — if graphite drifts to its
  // ±0.30 upper bound (284.80), adv1's floor sits exactly at graphite's
  // ceiling, which still enforces non-overlap. A relative constraint would
  // need an lmfit derived-parameter mechanism not present in the backend.
  peaks[1]._afCenterMin = 284.80;        peaks[1]._afCenterMax = 284.80 + 0.50;
```

- [ ] **Step 2: Verify the new bound is present and the old buggy one is gone**

```bash
grep -c '_afCenterMin = 284.80;' templates/index.html
```

Expected: `1` (the new line).

```bash
grep -c '_afCenterMin = 284.80 - 0.50' templates/index.html
```

Expected: `0` (the old buggy line is gone).

- [ ] **Step 3: Brace-balance sanity (no template syntax was disturbed)**

```bash
venv/bin/python -c "
import re
src = open('templates/index.html').read()
js = '\n'.join(m.group(1) for m in re.finditer(r'<script(?![^>]*src=)[^>]*>(.*?)</script>', src, re.S))
assert js.count('{') == js.count('}'), 'brace mismatch'
assert js.count('(') == js.count(')'), 'paren mismatch'
assert js.count('[') == js.count(']'), 'bracket mismatch'
print('structure: ok')
"
```

Expected: `structure: ok`

- [ ] **Step 4: Commit**

```bash
git add templates/index.html
git commit -m "fix(autofit): clamp Adventitious 1 center floor at 284.80 eV

Prevents adv1 from sliding below graphite. Chemical constraint:
adventitious sp3 carbon is always at higher BE than graphitic sp2.
Static frontend bound (graphite_init + 0.3); a true relative constraint
would need an lmfit derived-parameter mechanism not present in the
backend.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: FIX 2 — graphite-area-fraction warning helper

**Files:**
- Modify: `templates/index.html` — add a new helper `_autoFitCheckGraphiteFraction` immediately above `function applyAutoFitResult` (currently at line 4853).
- Modify: `templates/index.html` — call the helper inside `applyAutoFitResult` just before `return true;` at the success-path end (currently around line 4921, after the `tabManager._syncActiveToRecord` block).

The helper is a pure function — no DOM access, no side effects — so it's portable and unit-testable in Python. The caller in `applyAutoFitResult` issues the toast via the existing `notify()` API.

- [ ] **Step 1: Add the helper above `applyAutoFitResult`**

Find the line in `templates/index.html`:

```js
function applyAutoFitResult(json, graphiteRaw, roi) {
```

Insert directly above it:

```js
// Compute graphite's area fraction from a /api/fit response and decide
// whether to surface a non-blocking "graphite < 40%" warning. Pure function;
// returns null when no warning is needed (or when input is malformed),
// otherwise returns { fractionPct, warning } where `warning` is the exact
// user-facing toast text and `fractionPct` is the rounded-to-1dp percentage.
//
// Boundary: the spec says "< 0.40" so 0.40 itself does NOT warn.
function _autoFitCheckGraphiteFraction(json, graphiteId) {
  if (!json || !Array.isArray(json.individual_peaks)) return null;
  let total = 0;
  let graphiteArea = null;
  for (const ip of json.individual_peaks) {
    const a = ip && ip.params && ip.params.area && ip.params.area.value;
    if (!Number.isFinite(a)) continue;
    total += a;
    if (String(ip.id) === String(graphiteId)) graphiteArea = a;
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

```

- [ ] **Step 2: Wire the call in `applyAutoFitResult`**

Find the success-path tail (currently around lines 4917-4921):

```js
  // 7. Sync to tab record so tab switching preserves the result.
  if (typeof tabManager !== 'undefined' && tabManager._syncActiveToRecord) {
    tabManager._syncActiveToRecord();
  }
  return true;
```

Replace with:

```js
  // 7. Sync to tab record so tab switching preserves the result.
  if (typeof tabManager !== 'undefined' && tabManager._syncActiveToRecord) {
    tabManager._syncActiveToRecord();
  }

  // 8. Sanity check: warn if graphite area fraction is below 40%. The fit
  // is kept regardless — this is a triage signal, not a fit-quality gate.
  const gPeak2 = state.peaks.find(p => p.name === 'Graphite') || state.peaks[0];
  if (gPeak2) {
    const check = _autoFitCheckGraphiteFraction(json, gPeak2.id);
    if (check) notify(check.warning, 'amber', true);
  }

  return true;
```

- [ ] **Step 3: Verify the helper exists exactly once and is called exactly once**

```bash
grep -c 'function _autoFitCheckGraphiteFraction' templates/index.html
```

Expected: `1`

```bash
grep -c '_autoFitCheckGraphiteFraction(json' templates/index.html
```

Expected: `1`

- [ ] **Step 4: Python-port unit test for the fraction-compute helper**

```bash
venv/bin/python -c "
def check(json_resp, graphite_id):
    if not json_resp or not isinstance(json_resp.get('individual_peaks'), list):
        return None
    total = 0.0
    graphite_area = None
    for ip in json_resp['individual_peaks']:
        a = (ip or {}).get('params', {}).get('area', {}).get('value')
        try: a = float(a)
        except (TypeError, ValueError): continue
        if a != a or a in (float('inf'), float('-inf')): continue  # finite check
        total += a
        if str(ip.get('id')) == str(graphite_id):
            graphite_area = a
    if graphite_area is None or not (total > 0):
        return None
    fraction = graphite_area / total
    if fraction >= 0.40:
        return None
    fraction_pct = round(fraction * 1000) / 10
    warning = (
        f'Graphite area is only {fraction_pct:.1f}% of the total C1s signal. '
        f'This is below the typical 40% expected for a graphite-dominated sample. '
        f'Review the fit and consider manual adjustment.'
    )
    return {'fractionPct': fraction_pct, 'warning': warning}

def mk_resp(areas_by_id):
    return {'individual_peaks': [
        {'id': pid, 'params': {'area': {'value': a}}}
        for pid, a in areas_by_id.items()
    ]}

# Case 1: graphite at 0.45 of total → null (no warning)
r1 = check(mk_resp({1: 450, 2: 300, 3: 150, 4: 100}), 1)
assert r1 is None, r1

# Case 2: graphite at 0.25 of total → warning with '25.0%'
r2 = check(mk_resp({1: 250, 2: 400, 3: 200, 4: 150}), 1)
assert r2 is not None, r2
assert r2['fractionPct'] == 25.0, r2
assert '25.0%' in r2['warning'], r2['warning']
assert 'Graphite area is only 25.0% of the total C1s signal.' in r2['warning']
assert 'consider manual adjustment.' in r2['warning']

# Case 3: exactly 0.40 boundary → null (spec says < 0.40)
r3 = check(mk_resp({1: 400, 2: 300, 3: 200, 4: 100}), 1)
assert r3 is None, r3

# Case 4: missing area data on graphite → null (safe fallback)
r4 = check({'individual_peaks': [
    {'id': 1, 'params': {}},  # no area on graphite
    {'id': 2, 'params': {'area': {'value': 100}}},
]}, 1)
assert r4 is None, r4

# Case 5: empty / malformed input → null
assert check(None, 1) is None
assert check({}, 1) is None
assert check({'individual_peaks': 'not a list'}, 1) is None

print('autoFitCheckGraphiteFraction: ok')
"
```

Expected: `autoFitCheckGraphiteFraction: ok`

- [ ] **Step 5: Brace-balance sanity**

```bash
venv/bin/python -c "
import re
src = open('templates/index.html').read()
js = '\n'.join(m.group(1) for m in re.finditer(r'<script(?![^>]*src=)[^>]*>(.*?)</script>', src, re.S))
assert js.count('{') == js.count('}'), 'brace mismatch'
assert js.count('(') == js.count(')'), 'paren mismatch'
assert js.count('[') == js.count(']'), 'bracket mismatch'
print('structure: ok')
"
```

Expected: `structure: ok`

- [ ] **Step 6: Commit**

```bash
git add templates/index.html
git commit -m "feat(autofit): warn when graphite area fraction < 40%

Adds a pure helper _autoFitCheckGraphiteFraction(json, graphiteId)
that returns the warning text + percentage when graphite occupies
less than 40% of total fitted C1s area, or null otherwise. Wired into
applyAutoFitResult's success path as an amber notify() — non-blocking,
keeps the fit, just surfaces the triage signal.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: Update the spec doc

**Files:**
- Modify: `docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite.md` (append a section, do not rewrite earlier content)

- [ ] **Step 1: Append the section**

Append the following to the **end** of the spec file (after the existing "Related history" section):

```markdown

---

## Follow-up fixes (2026-04-24)

After Phase-1 shipped and was tested on real Fortier Lab data, two issues
surfaced that needed constraints added to the fit. Both were specified
2026-04-24 and implemented as additive frontend-only changes (no
`fitting.py` or `app.py` edits).

### FIX 1 — Adventitious 1 stays above graphite

**Problem.** Adv 1's previous bounds `[284.30, 285.30]` allowed it to slide
below graphite (which is bounded `[284.20, 284.80]`). Adventitious sp3
carbon is always at higher BE than graphitic sp2 — the bound was wrong.

**Resolution.** Use a static frontend lower bound (Attempt 2 in the user's
prescribed order). Adv 1's `_afCenterMin` is now `284.80` (= graphite_init
`284.50` + the chemical 0.3 eV separation). Upper bound unchanged at `285.30`.

**Trade-off.** The floor is fixed in the corrected BE frame, not relative to
graphite's *fitted* center. If graphite drifts to its `±0.3` upper bound
(284.80), adv 1's floor sits exactly at graphite's ceiling. A truly relative
constraint would need an lmfit derived-parameter mechanism that the backend
spec format does not currently support; adding it is well over 10 lines of
backend change. The static bound is sufficient for graphite-matrix samples
in practice.

### FIX 2 — Post-fit warning when graphite area < 40%

**Problem.** Real spectra were converging with graphite at 23–26% of total
fitted area. Mathematically valid; physically dubious for a graphite-
dominated sample.

**Resolution.** After a successful fit, compute
`graphite_area / sum(all_peak_areas)` from the `/api/fit`
`individual_peaks[*].params.area.value` data. If `< 0.40`, emit an amber
non-blocking `notify()` toast in addition to the green success toast.
Threshold is hardcoded; the fit is kept regardless.

**Implementation pointer.** See `docs/superpowers/plans/2026-04-24-auto-fit-c1s-followup-fixes.md`.
```

- [ ] **Step 2: Verify the section is present**

```bash
grep -c '^## Follow-up fixes (2026-04-24)' docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite.md
```

Expected: `1`

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite.md
git commit -m "docs(autofit): record FIX 1 / FIX 2 follow-up resolutions in spec

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Update the prior implementation plan doc

**Files:**
- Modify: `docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite-implementation.md` (append, do not rewrite)

- [ ] **Step 1: Append a forward pointer**

Append at the very end of the file:

```markdown

---

## Follow-up tasks (2026-04-24)

After Phase-1 shipped, two real-data fixes were specified and implemented
as a separate plan: see
[2026-04-24-auto-fit-c1s-followup-fixes.md](2026-04-24-auto-fit-c1s-followup-fixes.md).

- FIX 1: clamp Adventitious 1 center floor at 284.80 eV (1-line bound change in `buildAutoFitModel`).
- FIX 2: amber warning toast when graphite area fraction < 40% (helper + 1 call in `applyAutoFitResult`).

Both are additive, frontend-only, with no regression to Phase-1 behavior.
```

- [ ] **Step 2: Verify**

```bash
grep -c '^## Follow-up tasks (2026-04-24)' docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite-implementation.md
```

Expected: `1`

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite-implementation.md
git commit -m "docs(autofit): point Phase-1 plan at follow-up-fixes plan

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Browser verification checklist (handoff)

**Files:** none — manual walk-through.

Before publishing, walk these four items at `http://127.0.0.1:5000/`. Hard-refresh first (Cmd-Shift-R / Ctrl-Shift-R) and leave DevTools console visible.

- [ ] **A. FIX 1 — Adventitious 1 lands above graphite on a previously-failing spectrum.**
  Load `8 A/C1s Scan.VGD` (the known previous-failure case where adv1 slid to ~284.3). Run Auto-Fit C1s Graphite. Expand the peak list; confirm:
  - Adventitious 1 center is **≥ 284.80 eV** (corrected BE).
  - Graphite center is at 284.50 ± 0.05.
  - Visually the fit no longer puts adv1 to the left of graphite.

- [ ] **B. FIX 2 — Warning toast appears when graphite area < 40%.**
  On the same spectrum (or any other spectrum that produces `graphite_area / total < 0.40`), confirm that *after* the green "Auto-fit complete" toast, a separate **amber** toast appears with this exact text format:

  > Graphite area is only **X.X%** of the total C1s signal. This is below the typical 40% expected for a graphite-dominated sample. Review the fit and consider manual adjustment.

  The percentage is rounded to one decimal. The toast is persistent (does not auto-dismiss). The fit is **not** rolled back — peaks remain in the peak list.

- [ ] **C. FIX 2 negative case — No warning when graphite ≥ 40%.**
  Load `Project10D.proj.json` (known pass case, graphite at 42.8%). Run Auto-Fit. Confirm:
  - Green "Auto-fit complete" toast appears.
  - **No** amber warning toast appears.
  - The peak list shows graphite as the largest-area peak.

- [ ] **D. Phase-1 regression — low-BE peak count detection still works.**
  On the three Phase-1 test scenarios:
  - C1s with prominent low-BE peak → 2 Unknown peaks.
  - C1s with one small low-BE bump → 1 Unknown peak.
  - C1s with negligible low-BE intensity → 0 Unknown peaks.

  These should behave identically to Phase-1 — the fixes don't touch low-BE detection.

When all four items pass, the user will request push to origin/main.

---

## Phase-3 / Phase-4 hooks (deferred, not part of this plan)

- **Relative constraint for adv1 lower bound.** Replace the static `284.80` floor with a true `graphite_center + 0.3` derived-parameter constraint, requiring a backend extension to inject extra lmfit Parameters from the spec dict. Worth doing only if static bounds prove insufficient on a wider sample set.
- **User-configurable area-fraction threshold.** Surface the 40% as a setting if lab usage patterns vary across sample types.
- **Triage UI for warned fits.** Aggregate warning state into a per-tab badge so a batch of fits can be sorted by "needs review" status. Builds naturally on Phase-2 batch when that revives.

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
