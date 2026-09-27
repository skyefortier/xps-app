OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0e201-e254-7ab2-9502-7c5e57d4530c
--------
user
Review unit F3 (the Auto-Fit C1s gate on live data): branch fix-noise-floor-scale-free, stacked on fix-fit-start-poll. Review git diff 07e0839..HEAD (07e0839 is the unit-2 commit F3 was cut from; later unit-2 commits are NOT part of F3): templates/index.html (isC1sTab only), tests/js/autofit_c1s_gate.test.js, CLAUDE.md, docs/superpowers/plans/2026-09-27-f3-noise-floor-and-c1s-gate.md, and the PARKED half's write-up docs/findings/noise-floor-occupancy/ (README + two patches that are NOT applied — review the write-up's claims and the patches as proposals, and say which variant you would choose and why). Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO (for the shipped gate change; the parked half is advice). Budget your time: a verdict is required within the run.

OWNER'S BRIEF (verbatim): "Find Peaks' absolute 1.0-count noise floor -> scale-free, per the design rule. Include the Auto-Fit C1s gate judging a stale typed window." Source: docs/findings/2026-09-25-fail-open-guards-sweep.md (branch sweep-fail-open-guards) M5 and M9.

TRY TO BREAK
a. isC1sTab: every caller and the moment it runs (menu state on ROI input, charge-reference permission, the Auto-Fit run at click time), the active tab vs a record (tab switch in progress, a stack tab active, a survey tab, a tab with no ROI typed, a reversed min/max, an ROI outside the data, an empty selection, a charge shift), getROIData()'s own semantics (corrected frame, inclusive, clipped), a very long scan (performance of the record path).
b. Anything the old behaviour allowed that users rely on (e.g. enabling Auto-Fit before the ROI is set).
c. The tests: real and non-vacuous (would fail on the old isC1sTab).
d. The parked half: are the measurements and the causal explanation in the README right (engine.py _extract_fitted_components / match_components_to_slots / rank_and_filter / the decisive override); is the recommendation sound; is anything in either patch wrong regardless of the choice (the variance floor left alone, orphans, the detectability payload, the grammar.contains change).

Finish with VERDICT: GO or VERDICT: NO-GO.

codex
I’ll trace the gate’s callers and data semantics, check whether the tests catch the old behavior, and review the parked patches as proposals. I’ll give a ranked review and a verdict on the shipped gate within this run.

exec
/bin/zsh -lc "pwd; git status --short; git diff --stat 07e0839..HEAD; rg --files -g 'AGENTS.md' -g 'CLAUDE.md' -g '*autofit_c1s*' -g '*noise-floor*'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-faPTpSp2' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-F2myBL1P' (errno=Operation not permitted)
?? docs/autofit/codex/f3_c1s_gate_verdict_runA.md
?? docs/autofit/codex/f3_c1s_gate_verdict_runB.md
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-UEQQAZVq' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-oxTBkGVz' (errno=Operation not permitted)
 CLAUDE.md                                          |   6 +-
 docs/autofit/codex/f3_c1s_gate_review_prompt.txt   |  11 ++
 docs/findings/noise-floor-occupancy/README.md      |  78 ++++++++
 .../variant_F_support_test.patch                   | 197 ++++++++++++++++++++
 .../variant_LR_likelihood_ratio.patch              | 201 +++++++++++++++++++++
 .../2026-09-27-f3-noise-floor-and-c1s-gate.md      |  43 +++++
 templates/index.html                               |  35 +++-
 tests/js/autofit_c1s_gate.test.js                  |  67 +++++++
 8 files changed, 626 insertions(+), 12 deletions(-)
CLAUDE.md
docs/superpowers/plans/2026-09-27-f3-noise-floor-and-c1s-gate.md
tests/js/autofit_c1s_gate.test.js

exec
/bin/zsh -lc 'git diff 07e0839..HEAD -- templates/index.html tests/js/autofit_c1s_gate.test.js CLAUDE.md docs/superpowers/plans/2026-09-27-f3-noise-floor-and-c1s-gate.md; cat docs/findings/noise-floor-occupancy/README.md; cat CLAUDE.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-kDjq4mCE' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-dFqgmHGQ' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index 4b92c72..7f03bea 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -936,8 +936,10 @@ invariants worth knowing before touching the code:
 - **`+ Stack` / `+ Add Spectrum ▾`** (chart toolbar): create a new
   empty stack and add open spectrum tabs to the active stack.
 - **Auto-Fit C1s Graphite** (Actions menu): one-click C1s peak model
-  + charge correction. Enabled only when the active ROI midpoint is in
-  270–315 eV.
+  + charge correction. Enabled only when the midpoint of the DATA the fit
+  would use is in 270–315 eV — for the active tab the live selection
+  `getROIData()` returns, never the tab record's stale window or a typed
+  window reaching past the data (`isC1sTab`, unit F3 2026-09-27, sweep M5).
 - **ROI past the data / centre outside the data** (2026-09-25, warn only):
   `getROIData()` has always clamped an ROI to the data it selects; the page
   now SAYS so under the ROI fields ("ROI extends past your data — clipped
diff --git a/docs/superpowers/plans/2026-09-27-f3-noise-floor-and-c1s-gate.md b/docs/superpowers/plans/2026-09-27-f3-noise-floor-and-c1s-gate.md
new file mode 100644
index 0000000..23edbe8
--- /dev/null
+++ b/docs/superpowers/plans/2026-09-27-f3-noise-floor-and-c1s-gate.md
@@ -0,0 +1,43 @@
+# F3 — the Auto-Fit C1s gate on live data; Find Peaks' noise floor (PARKED) (2026-09-27)
+
+Branch `fix-noise-floor-scale-free`, stacked on `fix-fit-start-poll` (unit 2,
+itself on F2): deploy F2 → unit 2 → F3, three fast-forwards. F3 touches
+neither Run Fit nor the job path (only `isC1sTab`), so it can be rebased onto
+main alone if unit 2 is held.
+
+Owner's brief (2026-09-27): "Find Peaks' absolute 1.0-count noise floor ->
+scale-free, per the design rule. Include the Auto-Fit C1s gate judging a
+stale typed window." Sources: sweep M9 (first bullet) and M5
+(`docs/findings/2026-09-25-fail-open-guards-sweep.md`).
+
+## 1. Shipped: the Auto-Fit C1s gate judges the data the fit would use (M5)
+
+| site | before | after |
+|---|---|---|
+| `isC1sTab(tab)` | the midpoint of `tab.ui.roiMin/roiMax` — for the ACTIVE tab a record synced only on a tab switch or save, and the TYPED values even where they reach past the data | for the active tab the live selection `getROIData()` returns (the fields clipped to the data, corrected frame); for any other record its saved window over its own corrected data; an empty selection is not C 1s; the midpoint of the SELECTED points is tested (270–315 eV, unchanged) |
+| callers (`_recomputeAutoFitMenuState`, `_isChargeRefAllowed`, `runAutoFitC1sGraphite`) | — | unchanged; all three are for the active tab; the ROI fields already refresh the menu on every keystroke |
+
+The sweep's reproduction (a wide 270–420 eV scan, the record's window on
+C 1s, a U 4f window typed in the fields without a tab switch): the menu was
+enabled and the gate passed, and the fit then took the U 4f₅/₂ line as
+"Graphite" (the step (c) refit refused it in the page runs, but a server
+construction passed every gate with a 107 eV provisional shift). Now the gate
+closes. Not in scope (sweep suggestion, a threshold of its own): bounding the
+provisional shift.
+
+Tests: `tests/js/autofit_c1s_gate.test.js` (the reproduction closes; a live
+C 1s selection passes; the selected data decide, not a typed window reaching
+past them; an empty selection; a non-active record judged on its own
+corrected data incl. a charge shift; every caller is the active tab; the ROI
+fields refresh the menu).
+
+## 2. PARKED for an owner decision: the occupancy floor (M9)
+
+`docs/findings/noise-floor-occupancy/README.md`: both scale-free variants
+implemented as patches and measured (the server's support F test breaks the
+background-mismatch honesty case; a Poisson likelihood ratio passes every
+gated and always-on suite). Recommendation: the likelihood ratio.
+
+## 3. Codex rounds
+
+(filled in as they run)
diff --git a/templates/index.html b/templates/index.html
index 72a215e..5d38496 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -7748,20 +7748,35 @@ async function runAutoFitC1sGraphite() {
   }
 }
 
+// Is this a C 1s spectrum, as Auto-Fit C1s Graphite would fit it? Unit F3
+// (2026-09-27, sweep M5): judged on the DATA the fit would use — for the active
+// tab the live selection getROIData() returns (the typed fields, clipped to the
+// data, in the corrected frame); for any other record its saved window over
+// its own corrected data. It used to read tab.ui, which for the ACTIVE tab is
+// synced only on a tab switch or save, and the TYPED midpoint: a wide scan with
+// the record's C 1s window but a U 4f window typed in the fields passed the
+// gate, and the fit then took the U 4f line as "Graphite".
 function isC1sTab(tab) {
   if (!tab || !tab.rawBE || !tab.rawBE.length) return false;
-  const ui = tab.ui || {};
-  let lo = parseFloat(ui.roiMin);
-  let hi = parseFloat(ui.roiMax);
-  if (!Number.isFinite(lo) || !Number.isFinite(hi)) {
-    // Fall back to full raw range (no UI ROI set yet)
-    let rmin = Infinity, rmax = -Infinity;
-    for (const v of tab.rawBE) {
-      if (v < rmin) rmin = v;
-      if (v > rmax) rmax = v;
+  let be;
+  const isActive = typeof tabManager !== 'undefined' && tabManager && tab.id === tabManager.activeId;
+  if (isActive && typeof getROIData === 'function') {
+    be = getROIData().be;
+  } else {
+    const shift = Number.isFinite(tab.ccShift) ? tab.ccShift : 0;
+    const corr = tab.rawBE.map(v => v - shift);
+    const ui = tab.ui || {};
+    const a = parseFloat(ui.roiMin), b = parseFloat(ui.roiMax);
+    if (Number.isFinite(a) && Number.isFinite(b)) {
+      const lo = Math.min(a, b), hi = Math.max(a, b);
+      be = corr.filter(v => v >= lo && v <= hi);
+    } else {
+      be = corr;                               // no window set yet: the whole scan
     }
-    lo = rmin; hi = rmax;
   }
+  if (!be || !be.length) return false;
+  let lo = Infinity, hi = -Infinity;
+  for (const v of be) { if (v < lo) lo = v; if (v > hi) hi = v; }
   if (!Number.isFinite(lo) || !Number.isFinite(hi)) return false;
   const mid = (lo + hi) / 2;
   return mid >= 270.0 && mid <= 315.0;
diff --git a/tests/js/autofit_c1s_gate.test.js b/tests/js/autofit_c1s_gate.test.js
new file mode 100644
index 0000000..7b07fd6
--- /dev/null
+++ b/tests/js/autofit_c1s_gate.test.js
@@ -0,0 +1,67 @@
+// F3 (2026-09-27, sweep M5): the Auto-Fit C1s gate judges the DATA the fit
+// would use — for the active tab the live selection getROIData() returns, for
+// any other record its saved window over its own corrected data — never the
+// active tab's record ui (synced only on a tab switch or save) and never the
+// typed midpoint of a window that reaches past the data.
+const { test } = require('node:test');
+const assert = require('node:assert');
+const fs = require('node:fs');
+const path = require('node:path');
+const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
+const lines = html.split('\n');
+function extractFn(name) {
+  const re = new RegExp('^(async )?function ' + name + '\\(');
+  const start = lines.findIndex(l => re.test(l));
+  assert.ok(start >= 0, name);
+  let depth = 0, seen = false;
+  for (let i = start; i < lines.length; i++) {
+    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
+    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
+  }
+  assert.fail('unbalanced ' + name);
+}
+
+// a wide scan 270-420 eV (C 1s and a U 4f doublet), 0.5 eV steps
+const RAW = Array.from({ length: 301 }, (_, i) => 420 - 0.5 * i);
+function gate({ activeId, liveSel }) {
+  const tabManager = { activeId };
+  const getROIData = () => ({ be: liveSel, inten: liveSel.map(() => 1) });
+  return new Function('tabManager', 'getROIData', extractFn('isC1sTab') + '\nreturn isC1sTab;')(tabManager, getROIData);
+}
+const sel = (lo, hi) => RAW.filter(v => v >= lo && v <= hi);
+
+test('the sweep reproduction: record window on C 1s, U 4f typed in the fields (no tab switch) — the gate CLOSES', () => {
+  const tab = { id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '280', roiMax: '295' } };   // stale record ui
+  assert.strictEqual(gate({ activeId: 't1', liveSel: sel(370, 415) })(tab), false, 'judged on the live U 4f selection');
+  assert.strictEqual(gate({ activeId: 't1', liveSel: sel(280, 295) })(tab), true, 'a live C 1s selection passes');
+});
+
+test('the SELECTED data decide, not the typed midpoint of a window that reaches past the data', () => {
+  // data 280-300 only; typed 250-400 -> typed midpoint 325 (not C 1s) but the selection is all C 1s
+  const narrow = RAW.filter(v => v >= 280 && v <= 300);
+  const tab = { id: 't1', rawBE: narrow, ccShift: 0, ui: { roiMin: '250', roiMax: '400' } };
+  assert.strictEqual(gate({ activeId: 't1', liveSel: narrow })(tab), true);
+  assert.strictEqual(gate({ activeId: 't1', liveSel: [] })(tab), false, 'an empty selection is not C 1s');
+});
+
+test('a non-active record is judged on its saved window over its own corrected data', () => {
+  const g = gate({ activeId: 'other', liveSel: sel(370, 415) });
+  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '280', roiMax: '295' } }), true);
+  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '370', roiMax: '415' } }), false);
+  // the window is in the CORRECTED frame, as the fit is: at a 100 eV shift, corrected 280-295 selects raw
+  // 380-395, which exists — judged as C 1s; a window the shifted data do not reach selects nothing
+  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 100, ui: { roiMin: '280', roiMax: '295' } }), true);
+  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 200, ui: { roiMin: '280', roiMax: '295' } }), false,
+    'corrected 70-220 has no point in 280-295: nothing selected');
+  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: {} }), false, 'no window: the whole 270-420 scan, midpoint 345');
+  assert.strictEqual(g({ id: 't1', rawBE: [], ui: {} }), false);
+});
+
+test('every caller of the gate is for the active tab (menu state, charge-reference permission, the Auto-Fit run)', () => {
+  for (const fn of ['_recomputeAutoFitMenuState', '_isChargeRefAllowed', 'runAutoFitC1sGraphite']) {
+    assert.match(extractFn(fn), /isC1sTab\(tab\)/, fn);
+  }
+  // and the ROI fields refresh the menu on every keystroke
+  assert.match(html, /id="roi-min"[^>]*oninput="updatePlot\(\);_recomputeAutoFitMenuState\(\)"/);
+  assert.match(html, /id="roi-max"[^>]*oninput="updatePlot\(\);_recomputeAutoFitMenuState\(\)"/);
+});
# Find Peaks' 1-count occupancy floor → scale-free: PARKED for an owner decision (2026-09-27)

Part of unit F3 (sweep M9, first bullet). The other half of F3 — the Auto-Fit
C1s gate judging a stale typed window (sweep M5) — ships on its own in
`fix-noise-floor-scale-free` and does not depend on this.

## What was found

`noise_floor` (default 1.0, never sent by the page) does two jobs in
`autofit/`:

1. a Poisson variance floor, `sigma = sqrt(max(y, noise_floor))` — the
   counting convention the server's weights use; not a decision threshold,
   left as is by both variants;
2. an OCCUPANCY threshold, `amplitude > noise_floor` — whether a fitted
   component occupies its slot (`match_components_to_slots`), whether a
   proposed slot survives (`_evaluate_proposal`), the detectability status
   (`build_confidence_vector`). A slot is "occupied" at amplitude 1.5 and not
   at 0.5 whatever the data's scale; persistence, the absent-slot test and the
   stability gate follow from it. This is the design rule's case.

Both variants replace (2) with a statistic on the component's own fit
(computed once when the component is extracted from its lmfit result and
carried on `FittedComponent.support`), leave (1) alone, and fall back to
`amplitude > 0` (a sign test) for a component with no fit behind it. They
differ in ONE line — what "occupied" means:

| variant | occupied when | patch |
|---|---|---|
| **F** — the server's support test | `fitting._component_support` "supported": Δχ² > 0 and F = (Δχ²/p) / (χ²_with/dof) ≥ 10 — the step (b) "not supported by the data" statistic and threshold | `variant_F_support_test.patch` |
| **LR** — Poisson likelihood ratio | Δχ²/p ≥ 10 on the Poisson-weighted χ², NOT divided by the fit's own misfit χ²_with/dof | `variant_LR_likelihood_ratio.patch` |

Both are scale-free (the weights make χ² dimensionless) and carry no tolerance.

## The evidence

| suite | baseline (today) | F | LR |
|---|---|---|---|
| gated real-data parity gates + stress honesty (`RUN_AUTOFIT_GATE=1`: C 1s parity, Bayesian real, candidate-pool real, U 4f unresolved, stress honesty) | 17 passed, 4 skipped | **16 passed, 1 FAILED** | 17 passed, 4 skipped |
| always-on `tests/autofit` (incl. the C 1s / region parity batteries) | green | **1 failed** (the same stress case), 556 passed | 557 passed, 7 skipped |

The failing case, `test_stress_honesty.py::test_bg_mismatch_surfaces_loudly`:
a Shirley-shaped truth fitted with a straight-line background, χ²ᵣ ≈ 280–470
for every candidate. The test requires the mismatch to be machine-visible
("conditional" tier), never a clean confident result. Today the 3-component
candidate P3 is stable but violates plausibility, enters the conditional
pool, and its bound-fixed refit wins via the decisive override →
`conditional: true`. Under F, P3's third component has F < 10 BECAUSE the fit
is so bad: F divides the gain by χ²_with/dof ≈ 284, so a component that
removes a large χ² still reads "unsupported"; it becomes an orphan, P3's
persistence drops to 0, P3 leaves the conditional pool, and P2 (χ²ᵣ 309) is
returned as a CLEAN survivor. Under LR the same component is occupied (its
gain per parameter is far above 10 Poisson units) and the result is
conditional, as today.

## The decision (owner)

- **F** keeps ONE definition of "supported" across the app (Find Peaks would
  judge components exactly as Run Fit's "not supported by the data" does), but
  in a grossly mis-modelled fit it declares real components absent and can
  turn an honest "conditional" answer into a clean one.
- **LR** keeps today's behaviour on every gate and the honesty case; its
  statistic differs from the server's support verdict, so after "Apply" a
  component Find Peaks counted as occupied could still read "not supported"
  in Run Fit's results on a very badly fitted model (the two agree whenever
  χ²ᵣ ≈ 1).

**Recommendation: LR.** Occupancy asks "did the fit put something real
here", which is a question about the signal against counting noise, not
against the model's own misfit; normalising by the misfit makes the answer
depend on how wrong the rest of the model is, which is exactly what the
honesty tier exists to report. Measured: LR changes nothing on any gate; F
breaks the honesty contract.

To apply the chosen variant: `git apply docs/findings/noise-floor-occupancy/variant_<X>.patch`
on this branch, then the full suite, the gated suite (`RUN_AUTOFIT_GATE=1`)
and Codex ×2. The `test_methods_seam` detectability assertion and the schema
round-trip fixture already accept both variants' status strings.
# XPS Fitting Studio

Web application for XPS (X-ray Photoelectron Spectroscopy) peak fitting,
multi-spectrum visualization, and project management. Python/Flask backend
with an lmfit-driven peak-fitting pipeline; single-page frontend in
`templates/index.html`. Deployed at xps.fortierlab.org via a gunicorn
LaunchAgent + Cloudflare Tunnel.

## Stack

- **Backend:** Python/Flask, served by gunicorn. App factory in [app.py](app.py).
- **Fitting engine:** lmfit ≥ 1.3 (5 methods: leastsq, least_squares, nelder, differential_evolution, basinhopping).
- **Numerics:** numpy, scipy.
- **File parsing:** pandas, openpyxl (xlsx), olefile (vgd).
- **Frontend:** Single-page HTML/JS in `templates/index.html` (~8500 LOC). Vanilla JS, no build step.
- **Charting:** Chart.js 4.4 (CDN).
- **Deployment:** macOS LaunchAgent runs gunicorn on **127.0.0.1:5050** (NOT :5000 — macOS AirTunes intercepts :5000 and returns 403, so health-check :5050); Cloudflare Tunnel publishes to xps.fortierlab.org. Dev gunicorn typically runs on :5151 with `--reload` for pre-merge verification. See [DEPLOY.md](DEPLOY.md) for the full deploy sequence.

## Project Layout

```
app.py                    # Flask app factory + REST routes
fitting.py                # lmfit pipeline, lineshape impls, background algorithms
parser.py                 # File parsers (csv / tsv / txt / xy / xlsx / xls / vgd)
vgd_parser.py             # Thermo Avantage VGD binary parser (uses olefile)
templates/index.html      # Frontend — CSS + HTML + JS in one file
tests/                    # pytest suite (focused on LA + DS+G correctness)
docs/superpowers/plans/   # Agent-authored design memos and implementation plans
uploads/                  # Per-session .npz storage (gitignored)
requirements.txt
venv/                     # virtualenv (do not commit)
```

The Flask backend serves the frontend via `render_template('index.html')`
and exposes a REST API consumed by the page through fetch.

## Backend API

Per-upload sessions store parsed `(energy, counts)` arrays as compressed
`.npz` in `uploads/<session_id>.npz`. No server-side memory state —
compatible with multi-worker gunicorn.

| Method | Path | Purpose |
|---|---|---|
| `GET`    | `/`                       | Serve the frontend (`templates/index.html`). |
| `GET`    | `/api/health`             | Liveness probe. Returns `{status: "ok"}`. |
| `GET`    | `/api/peak-shapes`        | List backend-registered lineshapes (gaussian / lorentzian / pseudo_voigt_gl / asymmetric_gl / doniach_sunjic / ds_g / la_casaxps). |
| `GET`    | `/api/elements`           | Spin-orbit element presets (splitting + area ratio). |
| `POST`   | `/api/upload`             | Upload a spectrum file; returns `session_id` + downsampled preview. |
| `POST`   | `/api/parse-vgd`          | Parse Thermo Avantage VGD binary directly (no session storage). |
| `GET`    | `/api/session/<id>`       | Retrieve a stored session's preview data. |
| `DELETE` | `/api/session/<id>`       | Delete session files. |
| `POST`   | `/api/background`         | Compute background curve for a session. |
| `POST`   | `/api/fit`                | Run lmfit on a session with peak specs; returns chi², bgIntensity, bgSubtracted, fittedY, per-peak refined params + σ. |
| `POST`   | `/api/fit/start`          | The same request and validation as `/api/fit` (an immediate identical 400 / 404); runs the SAME `run_fit` in a background thread; returns `{job_id}` 202 (unit 2, 2026-09-27). |
| `GET`    | `/api/fit/progress/<id>`  | The job record: `status` running / done / error / cancelled, `elapsed_sec`, `heartbeat_age_sec`; `result` = exactly the `/api/fit` body; `error` + `http_status` = exactly what `/api/fit` would answer. |
| `POST`   | `/api/fit/cancel/<id>`    | Stop the job (every minimisation aborts via lmfit's `iter_cb`); also automatic after 180 s without a poll. |

## Frontend Architecture

### State

Module-global `state` holds the currently-active tab's working values
(swapped on tab switch by `TabManager.activateTab`):

```js
state = {
  rawBE, rawIntensity,   // full spectrum as loaded
  ccShift,               // charge-correction rigid shift (eV)
  peaks[],               // array of peak objects
  nextId,                // auto-increment peak ID
  chart,                 // Chart.js instance
  residChart,            // Residuals sub-chart instance
  fitResult,             // last fit diagnostics (be, bgIntensity, bgSubtracted, fittedY, chi, etc.)
  lineWidth,             // per-tab line width (sync of tab.lineWidth)
}
```

### Tab model

`TabManager` (a class in `templates/index.html`) holds `tabs[]` and an
`activeId`. Two tab types share the array:

- **Spectrum tab:** has `rawBE`, `rawIntensity`, `peaks`, `fitResult`, `ccShift`, `manualAnchors`, `lineWidth`, `ui` (form field snapshot incl. bg settings, ROI, charge correction method).
- **Stack tab** (`isStack: true`): viewer-only container for references to other spectrum tabs. Has `entries[{id, sourceTabId, color, visible, showFit}]`, `lineWidth`, `verticalOffset`, `_nextColorIdx`. No raw data of its own — entries resolve their source tab at render time.

Lifecycle: `createTab`, `createStackTab`, `activateTab`, `closeTab`,
`_syncActiveToRecord` (writes state-back-to-tab on switch-away). Drag-and-drop
tab reordering exists.

### Peak Object Schema — core fields

(Non-exhaustive. Additional optional fields appear for multiplet linkage, fix-flags per parameter, auto-fit asymmetry bounds, etc. Search the source for `defaultPeak` to see the full shape.)

```js
{
  id, name, color, visible,
  center, fwhm, amplitude,
  shape,       // 'Gaussian'|'Lorentzian'|'Voigt'|'GL'|'asym-GL'|'DS'|'DSG_LA'|'LACX'
  glMix,       // 0–100 (Gauss → Lorentz)
  asymmetry,   // asym-GL asymmetry index
  dsAlpha, dsGamma,                       // DS params
  laAlpha, laBeta, laM,                   // DS+G params (laAlpha=α, laBeta=Lorentzian half-width, laM=Gauss FWHM)
  caAlpha, caBeta, caM,                   // CasaXPS LA params (caM is in DATA POINTS, not eV)
  linked, linkOffset, linkRatio,          // multiplet linkage to parent peak
  isChargeReference,                      // marks this peak as the cc anchor
}
```

### Lineshapes

| ID | Description |
|----|-------------|
| `Gaussian` | Pure Gaussian |
| `Lorentzian` | Pure Lorentzian |
| `Voigt` | Pseudo-Voigt, fixed η = 0.5 on BOTH sides (A03, 2026-09-22: the request sends `gl_ratio: 0.5, fix_gl_ratio: true`; until then the server fitted η FREE from 0.3 while the page drew, integrated and exported 0.5). Use `GL` to fit the mix. |
| `GL` | Pseudo-Voigt with adjustable GL mixing (0–100) |
| `asym-GL` | GL with asymmetric FWHM broadening on high-BE side |
| `DS` | Doniach-Šunjić, `dsAlpha` (0–0.5) + `dsGamma` |
| `DSG_LA` | DS+G — DS asymmetric core convolved with Gaussian. Frontend params `laAlpha`/`laBeta`/`laM`; backend id `ds_g`. |
| `LACX` | True CasaXPS LA(α,β,m) — asymmetric Lorentzian + Gauss conv with a CONTINUOUS m (data points; σ = m/3, half-width ⌈3.5σ⌉) on both sides since the caM unit (2026-09-25). Frontend params `caAlpha`/`caBeta`/`caM`; backend id `la_casaxps`. |

**What the page draws must be what the server fitted.** Two harnesses pin
it: `tests/js/lineshape_roundtrip.test.js` builds the request with the
page's own `peakToBackendSpec`, fits it with `fitting.run_fit`, applies the
result with `_applyBackendParams` and requires `evalPeakArray` on the fitted
grid to equal `individual_peaks[].y` for every shape (it also pins the
Python twin `autofit.reference.peak_to_backend_spec` to the page's builder,
shape by shape); section (D) of `tests/js/lineshape_parity.test.js` sweeps
each shape's FREE parameters across the fit's bounds. Both were added in A03
(2026-09-22) after a "Voigt" was found to be fitted with η free while drawn
at 0.5; the same harnesses then found `p.glMix || 50` / `p.dsAlpha || 0.1`
sending a mix or α of exactly 0 as the default, lmfit clipping a HELD value
to the optimiser's bounds (a DS+G m locked at 0 fitted at 0.05 —
`_make_peak_params._set` now widens a limit to a held value), and the
server clipping DS+G α to 0.495 where the page did not (`_dsgAlpha`). A
held parameter is held at its value; what the page draws is what the
server fitted. No shape carries a tracked gap any more. LACX with m > 0 was
the last (the page drew m rounded to an integer 2m+1 kernel while the
server fits it continuously: up to 0.97 % of amplitude and 1.2 % of area on
the lab's U 4f components) until the `caM` unit, 2026-09-25:
`laTrueCasaXPS_array` now mirrors `_la_casaxps_true` (continuous σ = m/3,
half-width max(1, ⌈3.5σ⌉), `np.convolve` 'same' with the server's trim,
normalisation at the grid point nearest the centre) — ≤ 7e-16 of amplitude
on all 108 committed LA components, pinned across the α/β/m box on seven
grids incl. grids shorter than the kernel
(`docs/superpowers/plans/2026-09-25-cam-continuous.md`). DS+G was the other gap until 2026-09-22 (the page's quadrature
`laCasaXPS` sized its step to the Lorentzian core, not the Gaussian kernel,
and was wrong by up to 1e52 × amplitude at β = 2, m = 0.05 and 5–21 % low
in area on the very box Find Peaks emits for a graphitic C 1s line);
`dsgConvolved_array` now mirrors the server's padded-grid convolution for
every m — the same FFT circular convolution — pinned at 1e-6 across the
full β/m box on eight grids, irregular grids and centres outside the
window (`docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md`). Two
server limits found there: a DS+G m just above the 0.001 delta threshold
on a coarse grid (m ≤ 0.003 at 0.1 eV, even padded length) underflows the
kernel and returns an all-zero curve — left as is, it reads as a
zero-amplitude component and step (b) flags it; and a centre OUTSIDE the
padded grid was normalised by rounding noise — fixed 2026-09-25 by a NEW
GUARDED BRANCH (normalise by the maximum), proven byte-identical for every
in-range centre against main's function (`scripts/dsg_outside_centre_identity.py`). Details of
A03 in `docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`.

---

## Design Rules

### Thresholds on data-scaled quantities fail

XPS spans many orders of magnitude within one spectrum, so any absolute
floor, delta or exactness cutoff will misjudge at some dynamic range. Two
units learned this independently — five intensity floors on the Auto-Fit
anchor (answer: a scale-free F test), then two tolerances on that F test
(answer: none). Prefer a scale-free comparison with no tolerance. If a
check seems to need a magnitude threshold, that is evidence the check is
formulated wrong.

(Owner, 2026-09-22. The record: the anchor unit's six Codex rounds in
`docs/autofit/codex/autofit_zero_graphite_*`, the DE unit's tolerance rounds
5–8 in `de_finite_bounds_*`, and the required-refit unit's rounds 2–3 in
`autofit_required_*`. The DE unit is the same rule seen from the other
side: every χ² comparison tolerance produced reachable false failures and
no reachable protection, and the fix was to delete the comparison.)

### Two readings of one field

When two places read the same input — the page and the server, a preview
and a fit, a comparison and the thing it compares — they must read it the
same way, or equivalent inputs get treated as different and different inputs
as equivalent. The instances so far: a "Voigt" meant η = 0.5 to the page and
a free η to the server (A03); the ROI, the preview background and the fitted
background meant three different point sets until one inclusive-bound
definition (`_bgWindowIndices`, sealed-fit-record memo Part 3); and in F1 the
fit key compared form numbers with `Number()` while the background code reads
the iteration and averaging counts with `parseInt()`, so typing "3e1" (read
as 3) matched a fit made at 30 (Codex round 2,
`docs/autofit/codex/f1_stale_statistics_r2_verdict_run{A,B}.md`). A comparison
must read each field exactly the way its consumer reads it — integers as
integers, energies through `parseFloat` — never a generic conversion
(`_fitKeyCanon`). (Owner, 2026-09-26.)

### Long fits start and poll (unit 2, 2026-09-27)

Run Fit (incl. "Use this solution") and Auto-Fit never hold a request open
for a fit: `_serverFitJob` starts it (`/api/fit/start`), polls every 0.5 s
and reads the finished record's `result` (the `/api/fit` body) with F2's
`_readFitReply` rules. So no request meets the public ~100 s ceiling (the five
largest C 1s basinhopping models completed in 213–414 s through the poll
path with no request longer than 0.28 s). Server: Find Peaks' job records
(atomic JSON under the upload folder, readable by any worker), a fit thread
and a 2 s heartbeat thread per job; `run_fit(cancel=)` gives every
`model.fit` an `iter_cb` that aborts once the job is cancelled — without it
the calls are made exactly as before (Levenberg-Marquardt byte-identical
either way). Page: the ownership rules run INSIDE the poll loop (a switched
tab or an edited model cancels the job and discards with the usual message);
a START that cannot reach the server is still a transport failure (local
fallback); a poll that cannot is retried, five in a row are; a stopped
heartbeat (> 30 s) is a failed fit; a closed page sends a cancel beacon, and
the server cancels a job nobody has polled for 180 s (above the ~1-minute
timer throttling of hidden browser tabs). The synchronous `/api/fit` stays
for scripts, tests and the Python twins. Plan:
`docs/superpowers/plans/2026-09-27-long-fits-start-poll.md`.

### Timing claims are measured through the public URL

A request from a student reaches the server through Cloudflare, whose edge
ends a proxied request at ~100 s (HTTP 524; probes through
xps.fortierlab.org on 2026-09-26: 88 s passed, 125 s gave 524) — well short
of gunicorn's `--timeout 300`. "300 s covers it" was written for the DS+G
Run Fit in 2026-09-22 and was true on the i9 and false through the public
URL. A claim that a request fits inside a limit is measured through
xps.fortierlab.org, not on 127.0.0.1. (Owner, 2026-09-27;
`docs/findings/2026-09-26-public-request-ceiling.md`.)

---

## Lineshape Physics — Critical Rules

### DS (Doniach-Šunjić) Asymmetric Lineshape

The DS tail MUST always point toward **higher binding energy** (the left
side on a standard inverted BE axis). Asymmetric broadening in metals
arises from low-energy electron-hole pair excitations at the Fermi level,
which produce intensity only on the high-BE side of the core-level peak.

**Never invert the DS tail toward lower binding energy.**

Implementation convention: `dx = center − x`. The power-law term
extends the tail toward higher BE (`x > center` ⇒ `dx < 0`). The
optional exponential cutoff `gamma_asym` decays **only** on that
side — `Math.exp(gamma_asym * Math.min(dx, 0))` in the JS
`doniachSunjic`, equivalent to `exp(−gamma_asym · max(x − center, 0))`
in `fitting.py`'s `_doniach_sunjic`. When adding DS-derived shapes,
preserve this convention: the high-BE side is where `dx < 0` and where
the exponential envelope must decay.

### DS+G (formerly mislabeled "LA(α, β, m) [CasaXPS]")

The shape registered as `ds_g` in the backend (frontend enum `'DSG_LA'`,
dropdown text "DS+G") is a Doniach-Šunjić asymmetric core convolved with
a Gaussian. Despite its old label, this is NOT the CasaXPS LA
formulation. Frontend field names `laAlpha` / `laBeta` / `laM` are kept
for save-state compatibility:

| Parameter | Meaning |
|-----------|---------|
| α (`laAlpha`) | DS asymmetry index, dimensionless, 0 ≤ α < 0.5 |
| β (`laBeta`) | Lorentzian HALF-width (eV) of the DS core |
| m (`laM`) | Gaussian FWHM (eV) used in the convolution |

Tail points toward **higher** binding energy (DS physics: low-energy
electron-hole pair excitations on the high-BE side only).

Saved fits using the old `'LA'` shape value are auto-migrated on load to
`'DSG_LA'` — math is unchanged, only the label. Saved fits using the
short-lived `'DSG'` shape are auto-migrated to `'DS'` (the shape they
were actually being fit against, due to a pre-existing preview/backend
mismatch).

### LA(α, β, m) [CasaXPS] — true CasaXPS formulation

The shape registered as `la_casaxps` (frontend enum `'LACX'`, dropdown
"LA(α,β,m) [CasaXPS]") implements the genuine CasaXPS LA. Distinct field
names `caAlpha` / `caBeta` / `caM` so users do not confuse them with DS+G's
`laAlpha` / `laBeta` / `laM` (which have totally different units):

| Parameter | Meaning |
|-----------|---------|
| α (`caAlpha`) | High-BE-side exponent on the unit-amplitude Lorentzian; dimensionless, default 1.0, bounds 0.1–5.0 |
| β (`caBeta`) | Low-BE-side exponent; dimensionless, default 1.0, bounds 0.1–5.0 |
| m (`caM`) | Gaussian convolution kernel width in DATA POINTS (not eV); continuous (the server fits it continuously so its derivative exists; the page draws the same continuous value since 2026-09-25 — it drew an integer kernel; the local engine HOLDS it exactly, since LA's curve jumps at m = 6k/7 and a smooth optimiser cannot fit it), default 50, bounds 0–499 |

α=β=1, m=0 reduces exactly to a pure Lorentzian. Increasing α
**suppresses** the high-BE tail; decreasing α extends it (BE-axis
convention; sign-flipped from CasaXPS's KE-axis description). m controls
Gaussian broadening; effective eV width ≈ (m/3) × dx where dx is the
data step size.

When implementing new LA-related lineshape parameters, **always** add
them to (use grep to find current line numbers — the file evolves):

- `defaultPeak` defaults block in `templates/index.html`
- `syncKeys` array
- `renderShapeControls` LACX param row
- `peakToBackendSpec` LACX branch
- `applyBackendResult` LACX backend-param mapping
- `runFit` JS LM free-params block + per-param clamps + linked-peak sync
- `evalPeak` switch + grid-aware `laTrueCasaXPS_array` evaluator (called via `evalPeakArray`; DS+G's grid-aware twin is `dsgConvolved_array` — a convolved shape's scalar `evalPeak` branch ignores m and must have no caller, parity guard (C))
- `_migrateLineshapeAliases` if backwards-compat alias needed

### UCl4 U 4f Asymmetric Broadening

The asymmetric broadening in the UCl4 U 4f spectrum is due to **5f²
multiplet coupling**, not metallic screening. Do not attribute it to
Kondo screening or Doniach-Šunjić metallic behaviour. Use
multiplet-split component models, not a single DS peak.

When modeling U 4f, use `asym-GL` for the U 4f₇/₂ and 4f₅/₂ main lines,
with separate symmetric GL peaks for the multiplet satellites.

### Satellite Peaks

Satellite peaks (shake-up, shake-off, plasmon loss) use **symmetric**
lineshapes — Voigt or GL. Do not apply DS or LA lineshapes to satellites.

### Linked (Multiplet) Peaks

A linked peak derives its center, amplitude, and **all lineshape
parameters** from its parent. The sync block must cover every shape
parameter — failing to add a new param breaks spin-orbit constraints
during fitting. Search for the `syncKeys` array and the `applyParams`
closure in `runFit` when adding parameters; both need the new key.

| Parent param changes | Linked peak receives |
|----------------------|----------------------|
| `center` | `parent.center + linkOffset` |
| `amplitude` | `parent.amplitude × linkRatio` |
| `fwhm` / `shape` / `glMix` / `asymmetry` / `dsAlpha` / `dsGamma` | same value |
| `laAlpha` / `laBeta` / `laM` (DS+G params) | same value |
| `caAlpha` / `caBeta` / `caM` (CasaXPS LA params) | same value |

---

## Fitting Algorithm

### Backend (default)

`POST /api/fit` runs lmfit on the server. Selectable methods: `leastsq`
(Levenberg-Marquardt), `least_squares` (Trust-Region), `nelder`,
`differential_evolution`, `basinhopping`. The UI Method dropdown
defaults to **Trust-Region** (`least_squares`); the backend falls back
to **`leastsq`** when a request omits `fit_method`. The endpoint
returns the full result including refined params, σ bounds, χ²,
`bgIntensity`, `bgSubtracted`, and `fittedY`. Linked peaks are
constrained via lmfit parameter expressions.

`differential_evolution` samples from the parameter bounds and refuses an
open one, and the page sends `amplitude_min: 0` with no `amplitude_max`
(a free DS+G centre has no default window either), so until 2026-09-19
every ordinary request for that method returned HTTP 422. For THAT METHOD
ONLY, every candidate (the first search and each perturbed refit) is now
`_search_then_refine`: differential evolution inside a generated box
(`_finite_search_box`: open sides of freely varying parameters only —
amplitude ± max(10 × the largest |background-subtracted intensity|,
2 × |start|, 1), just the ceiling for the page, which sets the floor
itself; centre = the fitted energy range, always a real interval), then —
whenever a side was generated — an UNCONDITIONAL `least_squares`
refinement from that solution under the request's own open bounds. A box
can shape an answer that lies nowhere near its sides, so nothing is
inferred from nearness. A refinement that CONVERGED is the result — a
`least_squares` fit of the requested model under the requested bounds,
which is what the default method returns; its χ² is deliberately not
compared with the boxed search's (a descent cannot end materially above
its start, but it ends a hair above an exact start sitting on a requested
bound, and every tolerance tried for that comparison produced reachable
false failures and no reachable protection — Codex rounds 5–8). If the
refinement did not converge or raised, the search result
stays marked unverified, never displaces a verified candidate in the
perturb loop, and, if it is what `run_fit` returns, is `success: false`
naming the generated limits.
Because differential evolution ignores the start and can "converge" with
a needle-narrow component outside the fitted range, each candidate also
competes with a `least_squares` fit from its own start under the request's
bounds (`_global_or_local_candidate`: verified beats unverified, then the
lower χ² wins), so this method never returns worse than the default method
would from the same start.
Generated sides are never echoed back as `min`/`max` (the page saves
returned bounds and warns within 1 % of them). A returned DE result
therefore normally carries `least_squares` uncertainties and message.
Every other method's parameters are unchanged; `/api/analyze` reaches the
same code through `options.fit_method`. Measured on committed targets with
the page's `n_perturb: 3`: 2–75 s per fit (6–7-component C 1s models
exhaust DE's evaluation budget in every search and are rescued by the
refinement). It is not a gold standard: on one 3-component B 1s target it
returned χ²ᵣ 1.92 where Trust-Region found 1.81.

`basinhopping` follows THE SAME PATTERN since unit F2 (2026-09-26; owner
decision; plan `docs/superpowers/plans/2026-09-26-f2-acceptance-holes.md`):
`_basinhopping_candidate` — the search, then an unconditional
`least_squares` refinement from its point under the request's bounds (the
refinement's convergence is the verdict, no χ² comparison), then a
competition with a `least_squares` fit from the same start (verified beats
unverified, then the lower χ²), for the main fit, every perturbed restart and
the required refit. Until then basinhopping always reported `success: true`
(lmfit sets it before minimising and never reads scipy's result), and
scipy's own flag is no verdict either: it marked 23 of 24 sampled committed
targets failed (BFGS "precision loss") at points equal to Trust-Region's
minimum (median relative χ²ᵣ difference 1e-9). An unverifiable search is
`success: false`. Basinhopping runs NO perturbed restarts (a global search:
with the page's `n_perturb` 3 they took 14 of 16 multi-component targets past
the 300 s server timeout, median 386 s, for χ²ᵣ identical to 1e-8; without
them median 96 s, max 256 s). NOTE: the public URL's ceiling is lower —
Cloudflare returns 524 between 88 s and 125 s — so the largest basinhopping
models still fail there
(`docs/findings/2026-09-26-public-request-ceiling.md`, not yet addressed).

**Determinacy (unit F2).** `run_fit` refuses a model with at least as many
free parameters as data points (`ValueError`, HTTP 400, "not determined by
these data: N free parameters for M data points"), and so does the local
engine: lmfit divides by max(1, nfree) and the F tests clamp dof to 1, so such
a model read as a near-perfect, fully supported fit (6 points, 2 GL
components: χ²ᵣ 2.8e-6, both "supported"). A count, not a threshold; one
degree of freedom is fitted as before.

**Reproducibility (2026-09-21).** Every random draw in `run_fit` — the
`n_perturb` restarts (the page sends 3; ±15 % on every varying parameter)
and the populations of `differential_evolution` and `basinhopping`, which
lmfit otherwise takes from numpy's GLOBAL generator — comes from one seed
that is a pure function of THE NUMBERS THE OPTIMISER IS HANDED
(`_request_seed`: SHA-256 of the energies, counts and the COMPUTED
background curve as little-endian float64, plus the canonical JSON of each
component's lineshape, each lmfit parameter's effective role — a
constrained one is its expression, a fixed one its value, a free one its
value and bounds — the method, solver options and `n_perturb`; tag
`xps-fit-seed-v1`). Settings are hashed by their EFFECT, never as sent, so
nothing the fit ignores can change the draws: a peak's name or colour, the
`fix_gl_ratio` the page still sends for a Gaussian, stale shape parameters
kept after a shape switch, the `endpoint_avg` a linear background does not
use, bounds of a fixed parameter, start values a link overrides, anchor
order, and the peaks' internal ids (parameter names and constraint
references are hashed by component POSITION: the page never reuses an id,
so a model rebuilt after deleting a peak would otherwise fit differently)
(in review each such no-op edit moved an area fraction by 15–45 pp
while the request was hashed as sent). It is a seed,
not an identity (32 bits collide; never a cache key). The response reports
it as `random_seed`; a caller's `fit_kws.fit_kws.seed` (integer in
[0, 2³²)) replaces it and is consumed, never forwarded to a solver.
`run_fit` itself accepts only the five supported methods, case-folded
(`_FIT_METHODS`): `/api/analyze` forwards `options.fit_method` without the
route's allowlist, and lmfit's `ampgo`, `dual_annealing`, … would draw
from the global generator. The seed value and the draws `run_fit` actually
makes (observed through Levenberg-Marquardt) are pinned by tests; numpy does not promise the same `default_rng` stream across
versions, so a failing pin after an upgrade is a release note ("saved
projects regenerate differently"), not something to re-pin silently.

What seeding buys and what it does not. "Identical request" means the same
data, model START values and settings — after a fit the page holds the
fitted values, so a second press is a different request; re-loading a
saved project and pressing Run Fit is the repeatable case. Measured on the
202 committed targets × 5 presses of the identical request, before → after:
Levenberg-Marquardt byte-identical on 145 → 202 targets;
Trust-Region on 51 → 145, area fractions moving by more than 1 pp between
presses on 8 → 0 targets, by more than 0.01 pp on 14 → 2 (worst 0.30 pp,
one U 4f scan where two presses in five land in a neighbouring minimum). Levenberg-Marquardt (MINPACK) and Nelder-Mead are
byte-identical. Trust-Region, the default, is NOT and cannot be made so by
seeding: the BLAS dot product (Apple Accelerate on the i9) rounds one unit
in the last place differently depending on where its argument sits in
memory (`w.dot(w)` gives two values over 16 alignments, `np.sum(w*w)`
one), `norm` inside scipy's `_lsq/trf.py` is the first call to return
different output for identical input, and the iteration amplifies that to
~1e-4 relative in an area at its stopping tolerance of 1e-8. Worse, the
perturbed restarts start from that jittering solution, and near a basin
boundary 1e-5 in a start is enough to send a restart into another minimum:
on the lab's targets that happened once (0.30 pp), but on a synthetic
five-component model two presses of the seeded request differed by 29 pp
(`tests/test_fit_reproducibility.py` docstring). Do not patch scipy
internals for this, and do not tighten the tolerance: ftol = xtol = gtol =
1e-12 on the same 202 × 5 gave FEWER byte-identical targets (123 vs 146)
and made two targets that converge today abort on the evaluation budget.
OWNER DECISION 2026-09-21: ACCEPT AND DISCLOSE; no unit for bit-identity.
Byte-identity is a software property, not a scientific one. The scientific
requirement — reloading a saved project and pressing Run Fit regenerates
the figure within meaningful precision — is met (2 of 202 targets move
more than 0.01 pp, worst 0.30 pp). The 29 pp synthetic case is the SAME
phenomenon as the local-minimum problem (near a basin boundary 1e-4 of
jitter flips the answer), so the scattered-starts cross-check unit is
already the mitigation: it exposes exactly those fits. Do not build a
second thing (a reviewer tried a deterministic perturbation base: identical
starts, results still differed; a reproducible-arithmetic BLAS is a large
project with uncertain payoff). Disclosure wording, for docs and the
student note: identical requests now give identical results on real data
in practice; the underlying arithmetic is not bit-reproducible, so a fit
sitting near a boundary between two solutions can still resolve
differently, and that is precisely the situation the multiple-starts check
is designed to surface.

**Scattered-starts check (step (a) of the 2026-09-21 unit; plan in
`docs/superpowers/plans/2026-09-21-scattered-starts-and-unsupported-components.md`).**
Every Run Fit with ≥ 2 unlinked components sends `n_starts: 3`; after the
normal fit (unchanged: THE FIT is what the student's method returned,
byte-identical with and without the check, and `n_starts` is not part of
the seed) `run_fit` runs three more fits of the SAME method from scattered
starts — drawn from a third stream of the request seed, anchored to the
REQUEST's start (amplitude ×/÷ 3, width ×/÷ 1.5, free centres ± 0.5 eV,
other bounded parameters redrawn inside the middle 90 % of their range),
clamped into the request's bounds (amplitude sign kept). "Same solution" =
every area fraction within 1 pp and every centre within 0.1 eV, COMPONENT
BY COMPONENT by id — no permutations: "C-O" and "C=O" trading places is a
different chemical reading even when both are GL lines. The response's
`starts` reports how many reached
the fit, how many ended in a solution that is NOT better (counted, never
listed — ~25 % of fits have one and listing them would train people to
ignore the panel), and `alternatives`: solutions whose χ²ᵣ is lower by more
than 0.1 %, each with its own areas and every component's centre shift
from the STUDENT'S START. Not run for `differential_evolution` /
`basinhopping`, single-component models, a fit that did not converge,
Batch Fit or the local fallback; a failure inside the check never fails
the fit. Page: one line under the Results table ("2 of 3 scattered starts
reached this solution; …" — counts, never certification language) and,
when alternatives exist, an "Other solutions found" table (your fit first;
the largest move named, amber > 0.5 eV, red > 1 eV) with Preview (the
history-preview overlay, on a copy) and "Use this solution": explicit, one
undo entry, recorded as `fitResult.chosenAlternative`, and ATOMIC by
construction — the alternative is only the START of an ordinary server fit
(`runFit({startPeaks})`); the live model is written by that fit's success
path and by nothing else, so a fit that fails, does not converge, is
discarded on a tab switch or cannot reach the server (no local fallback
here) leaves peaks and result exactly as they were, and σ, exports and
saves come through the one existing path. Every row shows EACH component's
own area % and its own move from the student's start. The evidence is
BOUND TO THE FIT THAT PRODUCED IT by COMPARISON, never by hand
invalidation (so no edit path can be forgotten): `fitResult.startsModelKey`
covers every peak field the request reads (incl. the auto-fit asymmetry
bounds) AND the fit context — background type and window, endpoint
averaging, Shirley iterations, ROI, manual anchors, charge shift — taken
after the result is applied and persisted with the counts.
`_startsIfCurrent(fr, key)` is the single accessor (`_startsLiveKey()` for
the active tab, `_startsRecordKey(t)` for a record): after any such change,
an undo or a history restore that brings back other values, the panel says
the comparison no longer applies, nothing can be previewed or applied, an
open alternative preview is dropped (`_dropStaleAltPreview`), and
saves/exports carry neither counts nor the recorded choice. A name, colour
or visibility is not part of a fit and does not invalidate it. `runFit`
captures the same key before its first await and DISCARDS a result whose
model or context was edited while it ran (the peak controls stay editable
during a fit; a newly locked centre would otherwise keep its edited value
under the server's statistics). The trigger (`n_starts`) is decided with
the other request inputs before the first await. In the RED band — and only there — it first asks,
naming the component and the distance ("This solution moves C-O by
−1.47 eV from where you placed it. Apply?"): a lower χ²ᵣ bought by
relocating a component is the measured trap (8-JT C1s Scan_1/5/6/7), and
the app must never substitute a chemical interpretation because it scored
better. Saves persist the counts (`_startsForSave`), not the alternatives'
parameter sets (regenerable from the seeded request). Measured with the
shipped code on the 202 committed targets: an alternative is shown on 0 of
94 re-fits of a saved solution and 6 of 84 not-yet-fitted starts (7.1 %;
three of them in the red band), median +0.54 s per Run Fit (90th
percentile +1.8 s). It shows that a decomposition is not unique; it cannot
say which one is correct, and four known targets defeat even ten starts.

### Client-side fallback

`runFitLocal` in `templates/index.html` is a JS Levenberg-Marquardt
implementation used as a fallback when the backend is unreachable, and
the ONLY engine Batch Fit uses. Central-difference Jacobian (centre
step scaled by the peak width), active-set step (parameters pushed into a
box wall are held fixed), max 3000 iterations. Terminates on a gradient
cosine < 1e-6, on actual and predicted relative χ² reductions both < 1e-6
in agreement, or on a relative step < 1e-8, and only after a
feasible-descent CERTIFICATE passes: no single free parameter moved by
1e-3 (scaled, inside its box) reduces the residual by more than 1e-6 of
its value, otherwise that point is taken and iteration continues. The
certificate is a coordinate (single-parameter) check, not a proof of a
local minimum along coupled directions; no exit is exempt from it.
Damping exhaustion is a FAILURE. Poisson-weighted since unit W1
(2026-09-18): it minimises Σ(w·r)² with w = 1/√max(raw counts, 1), the
server's weighting, so its statistic is a real χ²ᵣ (objective
`poisson_weighted_chi_square`); results saved by unit A0 were unweighted
and stay labelled "Residual variance". It produces no uncertainties, and it
HOLDS LA's `caM` at its exact value (it used to round it in its clamp; a
free m was tried in the `caM` unit and withdrawn: LA's curve is
discontinuous in m, `docs/superpowers/plans/2026-09-25-cam-continuous.md`).

**A local result is a STARTING POINT, not a reportable result** (keyed on
`engine: 'local'`, helpers `_isLocalFit` / `_isLocalModel` /
`_localFitCaveat`). Measured in unit W1 and RE-MEASURED after A03
(2026-09-22, `docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`,
generator `scripts/local_server_gap.js`): weighted, it matches the server on
GL-type models (≤ 4 meV, ≤ 1.4 % area on the lab's C1s scans) and on Voigt
components (fixed η = 0.5 on both sides since A03: on the 5 of 9 committed
U 4f targets where both engines reach the same minimum every component
agrees within 4.3 meV, 2.6 % FWHM, 2.0 % area, 0.12 pp — W1 had measured up
to 20.8 % area on the Voigt satellites); it still differs on the other U 4f
targets for two reasons, separated by a control arm (the server with LA's
m held at the same value): the `caM` hold (the server fits m, the local
engine holds it — on Scan_6 the whole gap), and the local descent stopping
in a worse minimum (5–13 % χ²ᵣ above the held-m server on Scan_4/5/8) —
the "several minima" case (`docs/findings/cam/local_server_gap_after_cam.json`;
both engines' amplitude floor is 0 since unit step (b)). Both engines weight by
√intensity whether the data are counts or CPS (a convention, not a
calibrated uncertainty for rates); the formula is the same but the inputs
are not bit-identical, because `uploadToBackend` rounds intensities to
2 dp before the server weights them. A03 and the `caM` unit are done and
the designation STAYS on both grounds: fitting m locally needs a
derivative-free search (its own unit), and the worse-minimum outcome
(three of nine U 4f targets) remains; the label is reconsidered only on a
re-measurement after that work. (The amplitude-bound change
DECIDED 2026-09-18 — `docs/findings/2026-09-fit-determinacy.md` §3 — is
implemented: unit step (b), 2026-09-22, below.) The same file records that a
converged server fit is not ground truth: on a committed C 1s scan the
server's default method stopped in a local minimum the local engine
avoided.
See `docs/superpowers/plans/2026-09-18-local-engine-poisson-weighting.md`.

**"Not supported by the data" (unit step (b), 2026-09-22; owner decision
2026-09-18).** A component whose amplitude the fit drove to its floor,
pinned on a bound or fitted to numerical residue is an explicit OUTCOME —
the fit did not determine it — and its centre, width and σ are not reported
as if they were. The statement needs no intensity floor (six were tried for
the Auto-Fit anchor and each rejected real components or accepted residue):
with the other components held at their fitted values, removing this one
must make the fit significantly worse — `fitting._component_support`, the
Auto-Fit anchor's F statistic (F ≥ 10; `SUPPORT_MIN_F`). The SERVER computes
it once per component (`individual_peaks[].support = {f, delta_chi2,
supported}`; a linked component `follows` its parent); the page's twin
`_componentSupportFromResponse` recomputes it from any response carrying
`counts`, `fitted_y` and the component's curve; the LOCAL engine computes
the same statistic from its own residuals and weights
(`_componentSupportCore`), so a component driven to the zero floor by Batch
Fit is an outcome there too. Linked components follow their ROOT ancestor
whatever the request order. The verdict is a property of the fit that
produced it, CONDITIONAL on the other components as fitted, so it is bound
to that fit: `p.support.fitKey` is the model-plus-context key
(`_startsLiveKey()`) taken after the values are applied, and
`_isUnsupported(p)` compares it with the live key at every read — after
the student edits any peak, lock, link, the background, ROI, anchors or
charge correction, or an undo brings back other values, nothing is
suppressed or excluded until a new fit writes a new verdict (a verdict
without a key, from an older save, is never applied; exports write a
Status only from a CURRENT verdict — stale means "not established", never
"supported"). When the key changes, `_refreshStartsEvidence` compares the
set of flagged components with what EACH consumer has rendered — sidebar
badges, Results rows and chart datasets carry the peak id / flag — and
re-renders the ones that differ — the sidebar is PATCHED IN PLACE (header, summary values, area % over the currently supported components, badge), never re-rendered, because the student may be typing in a card (a caller that already redrew the sidebar,
such as Lock All or Add Peak, therefore still gets Results, Quantify and the
chart refreshed); it runs from the lock toggles, Lock All and every
`updatePlot` (which passes `fromPlot` so the chart is not rebuilt from
inside its own rebuild). Auto-Fit locks
every centre and refines the charge shift AFTER the result is applied, so
it re-stamps its verdicts (`_restampSupport`) — those changes are part of
its result. `p.support` is persisted with the peak (saves spread the peak
whole); Batch Fit's copy and a `.fit.json` import set it to `null`
(parameters on other data: nothing established); stack tabs judge a source
component against the SOURCE record's key. Sites
(`_isUnsupported`): sidebar card (badge; centre/width "—"; excluded from the
area total), Results table (greyed row, no centre/width/σ, area kept,
percentage "—", note beneath; percentages over supported components),
uncertainty panel (one rule-0 warning, before the per-parameter alarms and
instead of the neutral "locked" note Auto-Fit's centre lock would produce),
Quantify (no row; listed beneath: "an atomic percentage of 0.0 % would be a
measurement claim"), chart / stack / figure legend labels, no figure label at
the component's (zero) maximum, CSV/XLSX (Status column, empty cells, no
At%, WARNING line — and no width of any kind: DS+G β / m and LA m are widths
too), TSV (column kept, header says so), the scattered-starts table ("Your
fit" row shows neither area % nor a move for it, and it is never the
largest move; an alternative's components are unjudged and shown as they
are). Both engines' amplitude
floor is 0 (`runFitLocal`'s clamp was 1). Measured on the 202 committed
targets: 3 of 752 components (three C 1s re-fits, F 0.95–3.9), 0 of 95 fresh
starts — but committed projects are survivorship-biased (a collapsed
component may have been deleted before saving), so the working-fit rate is
plausibly higher. Known limits, the anchor check's: a gross single-channel
artefact can mark a real component unsupported; REDUNDANCY UNDER OVERLAP is
not detected (a refit without the component is the test; step (c) does it
for the Auto-Fit anchor).

**Acceptance rule for fit outcomes (unit A0, 2026-09-15):** a fit OUTCOME
from Run Fit, Batch Fit or the local engine is shown, stored or exported
only if it converged. `runFitLocal` works on a copy and commits only on
success, returning `{success, iterations, chiReduced}`; `runFit`
treats `success !== true` from `/api/fit` as a failed fit and falls back to
the local engine only on a transport failure, never on a server-side
error. A 2xx body that was READ but is not JSON is the server's reply, not a
transport failure (unit F2): `_readFitReply` reads the text (a failure there
is transport) and parses it; a NaN / Infinity token (Flask serialises a σ it
could not compute that way) or any unparseable body is a failed fit with its
message, for Run Fit and Auto-Fit alike — until F2 it sent Run Fit to the
local engine, replacing the server's converged result, verdicts and starts
evidence with a starting point. A RESULT IS DISCARDED IF THE MODEL WAS EDITED WHILE THE FIT WAS RUNNING
(2026-09-22; a correctness fix for EVERY Run Fit, shipped with the
scattered-starts check but independent of it). The peak controls stay
editable during a fit. `runFit` captures the model-plus-context key
(`_startsLiveKey()`: every peak field the request reads, background type and
window, endpoint averaging, ROI, anchors, charge shift) beside `peakSpecs`,
before its first await, and after the tab-owner check refuses to apply a
result if that key changed: amber notice, "Fit discarded (model edited)",
previous peaks and result kept. Before this, a centre changed and locked
mid-fit kept its edited value (`applyBackendResult` honours locks) under the
server's χ², σ and fitted curve for a different model.
STATISTICS AFTER AN EDIT (unit F1, 2026-09-25; plan
`docs/superpowers/plans/2026-09-25-f1-stale-statistics.md`): χ², σ, RMSE,
the R-factor and the stored fitted curve are bound to their fit by the SAME
key (`fitResult.startsModelKey`, now stamped by every creator — `runFit`,
`runFitLocal`, `applyAutoFitResult`, re-stamped by `_restampSupport`); no
second mechanism. One accessor, `_statsState(fr, key)` (`_statsLiveState()`,
`_statsRecordState(t)`): `current` / `stale` (the model or its context
changed since — an edit, a Find Peaks apply in the default window, an undo
or history restore to other values) / `unverified` (no key: saved before
this unit — values shown with a note to re-run). Stale: Results banner
("belong to the previous model"), statistic / RMSE "—", no R panel, no σ;
header "χ²ᵣ — (model changed)", status "—", "R: —"; no per-parameter
uncertainty rule; CSV/XLSX a WARNING instead of the statistic, σ cells
empty; TSV a NOTE (its columns are the current, unfitted model); figure no
χ² and no stored "Fit" curve; chart and stack envelopes composed from the
current peaks; saves keep the key (a reload judges again) and add
`statisticsState` / `statisticsNote`. Refreshed from `updatePlot`
via `_refreshStartsEvidence` (`_refreshStatsState`, Results carries
`data-stats-state`; lock toggles and Lock All reach it too). Keys are
compared by `_sameFitKey` (each form field canonicalised through its
readers' parser: energies parseFloat, "280" = "280.0"; counts parseInt,
"3e1" ≠ "30").
Auto-Fit now discards a response whose model or context was edited while
it ran, and a transport failure after such an edit runs no local fit. A
stale save's curve and R are never re-installed on load. The model
replacement that keeps an older result is thereby covered for the
statistics. Not covered (separate units): loaded files without convergence
provenance; `p._backendParams` still rides in a stale save (not displayed;
the sealed fit record owns it). From the initial commit
until this unit the local LM step had the wrong sign and returned the
starting model as "Fit complete"; see
`docs/superpowers/plans/2026-09-15-a01-local-lm-proof.md` and
`scripts/scan_batch_fit_signature.py`, which lists suspected saved files.

## Background Methods

| Backend id | Notes |
|---|---|
| `shirley` | Iterative Shirley (Proctor & Sherwood, *Anal. Chem.* **1982**, 54, 13, 2438–2439). Default. |
| `smart` | Shirley variant with smarter endpoint handling. |
| `smart_exp` | Experimental Shirley variant. |
| `shirley_linear` | Shirley with a linear-fallback bridge. |
| `linear` | Straight line between ROI endpoints. |
| `tougaard` | Single-pass universal cross-section K(T) = B·T/(C+T²)², B = 2866 eV², C = 1643 eV² (Tougaard, *Surf. Interface Anal.* **1988**, 11, 453; kernel max at √(C/3) ≈ 23.4 eV). Order-robust (either BE direction); amplitude anchored to the data at the high-BE edge. JS twin `tougaardBackground` must stay in numerical agreement (pinned by `tests/js/tougaard_twin.test.js`). |
| `manual` (frontend only) | User-placed anchor points; `manualAnchorBackground` in JS. |

Use Shirley for standard core-level regions. Linear only when the
spectral window is very narrow and featureless.

## Quantification

Peak areas are integrated numerically (trapezoidal over BE grid). RSF
(relative sensitivity factor) corrections are applied in the Quantify
tab. Atomic percent = (area/RSF) / Σ(area/RSF) × 100.

---

## Charge Correction

Reference: **C 1s adventitious carbon at 284.8 eV** is the default. The
UI dropdown also offers **C 1s graphitic carbon (sp²) at 284.5 eV** as
an alternative; the Auto-Fit C1s Graphite feature uses 284.5 eV as the
fixed reference for the graphitic component it identifies.

A rigid shift (`state.ccShift`) is applied to all binding energies
before fitting. The corrected axis is produced by `getCorrectedBE()`.

Auto-Fit C1s Graphite derives that shift from the FITTED centre of its
"Graphite" component, so the data must SUPPORT that component
(`_autoFitGraphiteIsSupported`), in the one sense that needs no intensity
threshold: removing it from the fitted model must make the fit to the
server's own data significantly worse. From the `/api/fit` response alone —
`counts`, `fitted_y`, the component's curve `individual_peaks[].y`, the
server's weights 1/max(counts, 1) — F = ((χ²_without − χ²_with)/p) /
(χ²_with/dof), p = the component's free parameters; supported means
χ²_without > χ²_with and F ≥ 10 (or χ²_with = 0). A component driven to
zero, pinned on its bound or fitted to numerical residue has
χ²_without ≤ χ²_with — removing it costs nothing (true of every such
reproduction in `docs/autofit/codex/autofit_zero_graphite_*`); resolved
anchors measured F from 1.7e2 (behind a 300 000-count one-channel spike) to
1e9, and the 70 committed Graphite models F ≥ 1.1e3. Otherwise the auto-fit
is rejected and rolled back with a red notice before any charge-correction
input is touched. Until 2026-09-21 only the centre was checked (±0.3 eV of
284.50), which a zero-amplitude component always satisfies because its
centre is bounded to that window. Do NOT replace this with an intensity
floor: five were tried (relative to the strongest component, the raw span,
the background-subtracted maximum, the raw magnitude, the upload's 0.01
resolution) and each rejected real anchors or accepted residue. The same
statistic is the natural definition for the planned "component not
supported by the data" outcome. Fixtures are real `run_fit` responses:
`scripts/gen_autofit_anchor_fixtures.py` →
`tests/js/fixtures/autofit_anchor.json`. SCOPE: it answers "do the data
support this component?", not "is it graphite?".

KNOWN LIMITS of that check (owner decision 2026-09-21: shipped with them
after six Codex rounds, all NO-GO; do NOT write a seventh rule — six
intensity floors failing is the data saying no threshold on intensity can
mean "zero" independently of the data):
- It REJECTS A REAL ANCHOR when the fitted region carries a gross
  single-channel artefact (a spike of millions of counts, or a dead
  zero-count channel): that channel dominates χ²_with and drags F under 10.
  The user gets a red notice and a rolled-back model; removing the artefact
  or narrowing the ROI recovers. A recoverable refusal beats main's old
  failure mode — a non-existent component silently setting the energy
  reference for a whole spectrum.
- REDUNDANCY UNDER OVERLAP was out of scope for the support check
  (χ²_without holds the other components fixed) and is CLOSED by step (c),
  2026-09-22: Auto-Fit's request carries `require_component: <Graphite id>`
  and the server refits the model WITHOUT that component from the others'
  fitted values under the request's bounds (`fitting._component_required`,
  through the run's own fitter `fit_model` — so differential evolution's
  box/refinement machinery and the request seed apply to the refit too;
  everything linked to the removed component goes with it, transitively;
  every retained parameter is created before any expression is assigned,
  so a chain of links in any request order resolves; NO tolerance of any
  kind on the comparison — a delta floor relative to the data's power and
  then an "exactness" cutoff on the reduced fit each masked a resolved
  anchor at high dynamic range, Codex rounds 2–3, the DE unit's lesson
  again. Known limit, accepted: on NOISE-FREE data whose full fit is exact
  to machine precision F is meaningless and a truly redundant component can
  read "required"; real data never fit to machine precision) and returns
  `required: {required, f, chi2_with, chi2_without_refit, refit_converged}`
  with the same F ≥ 10 rule (a refit that did not converge gives NO verdict
  since unit F2 — `required: null, refit_converged: false` — and Auto-Fit
  refuses that anchor too: a refit stopped early had read "required", F 992,
  for a redundant anchor). `applyAutoFitResult` refuses a supported-but-
  not-required anchor exactly like an unsupported one, before any
  charge-correction input is touched ("refitting the other components
  without it fits the data as well"); the anchor id is captured with the
  other request inputs before the first await. One extra fit, Auto-Fit only; the fit
  itself is unchanged by the check, and a check that did not run never
  blocks. On the 70 committed Graphite models the anchor is required on
  all 70 (F ≥ 54, median 6.1e3 — a measurement with `require_component` over
  the un-committed target file, not a test); the round-6 reproduction (two symmetric GL
  lines, no graphite: support F ~ 1e6 with the others held, refit without it
  equal to rounding) is now refused.
- One rounding-residue construction still passes (unrounded manual
  background a rounding step under data the upload flattened; F ≈ 280).

LOGGED FOR ONE LATER UNIT (untouched): Auto-Fit anchors on a one-channel
spike, and on a featureless plateau under background None, and still
derives a charge correction from it; a rejected Auto-Fit (any reason)
leaves its `pushUndo()` entry and a cleared redo stack behind. The spike
case shares a root with the false rejection above — gross single-channel
artefacts are unhandled generally — so if this becomes a despike /
outlier-flag unit, those three are one piece of work.

Adventitious carbon referencing (284.8 eV) is the default for
convenience but has known criticisms in the XPS literature — the C 1s
position of adventitious carbon depends on surface chemistry and is not
a true universal standard. Graphitic carbon (284.5 eV) or a known
internal reference is preferable when available.

Additional fixed references in the dropdown: Au 4f₇/₂ (83.98 eV), B 1s
for B₂O₃ (192.99 eV), N 1s for BN (398.31 eV), B 1s for BN (190.74 eV),
plus a free-entry "Custom reference" option.

## File Formats Supported

| Extension | Notes |
|-----------|-------|
| `.csv`, `.tsv`, `.txt`, `.xy` | Whitespace/comma/tab/semicolon delimited. Backend `parseCSV` + frontend equivalent. |
| `.xlsx`, `.xls` | Backend `parseXLSX` (openpyxl); frontend XLSX.js for client-side parse. |
| `.vgd` | Thermo Avantage binary. Backend uses `vgd_parser.py` (olefile); frontend `parseVGD` does a heuristic Float32 extraction. |

Spectrum columns: first = BE (eV), second = intensity (counts/s). Rows
with non-numeric or missing values are skipped.

---

## Multi-Tab + Project Save/Load

The app supports multiple spectrum tabs simultaneously. Project state
saves to `.proj.json` (< 5 tabs) or `.proj.zip` (≥ 5 tabs; manifest +
per-spectrum JSON inside the archive). Schema version 3.

- **Tab IDs** are preserved across save/load. Field is top-level
  `data.activeId`; the saved active tab is re-activated on load.
- **Stack tabs persist.** Saved with `isStack: true` + their entries
  + line-width + offset; spectrum tab data lives elsewhere and is
  reached by `entry.sourceTabId` at render time.
- **Stale stack entry pruning:** if a saved stack references a source
  tab that didn't load, the entry is dropped and an amber toast tells
  the user.

## Spectrum Stacking

A stack tab visualizes multiple spectra on shared axes with per-entry
fit visualization (envelope + shaded peak components, raw-level).
The whole stack chart's behavior is governed by a small set of
invariants worth knowing before touching the code:

- **Dataset keying.** Each entry contributes 2 + 2×N_peaks datasets to
  the chart, each tagged with a stable `_stackKey` of the form
  `<entryId>:raw`, `<entryId>:env`, `<entryId>:peak:<peakId>`,
  `<entryId>:pbg:<peakId>` (the `:pbg` is a transparent fill anchor for
  the matching peak's shaded fill — Chart.js requires a real dataset
  for fill targets). Keys let in-place updates target specific datasets
  without relying on array indices, which shift when datasets reorder.

- **In-place updates preserve zoom.** `_updateStackChart` mutates
  `data` / `hidden` / `borderWidth` / `fill` on existing datasets and
  calls `chart.update('none')`. `_renderStackChart` is the destroy +
  rebuild path, used only on entry add/remove or when the active chart
  is the wrong chart (see next bullet).

- **Chart-type discriminator.** `state.chart._xpsStackTabId` is set on
  every stack chart at creation. `_updateStackChart` rebuilds whenever
  the active chart isn't tagged for the current stack tab — guards
  against in-place updates running against a stale spectrum chart or
  a different stack's chart.

- **3 render-data paths** in `_buildEntryRenderData` cover fresh
  backend fits (Path A: use fitResult.fittedY directly), fresh local-LM
  fits (Path A2: compose envelope from peaks + bgIntensity), and
  post-load reconstruction (Path B: recompute bg from raw via the
  source tab's persisted bg settings using `_computeBackgroundForSource`).
  Render data is cached on the entry as `_renderDataCache` and
  invalidated only at `_renderStackChart` rebuild.

- **Layered visibility model.** Per-entry `entry.showFit` gates whether
  the entry participates in fit visualization at all; the toolbar pills
  (Envelope, Individual Peaks, Fill, Bkgrd Sub) act as global layer
  switches on top. The `peak-fit-control` CSS class hides peak/fit
  toolbar items entirely on stack tabs (Run Fit, Batch Fit, etc.).

## Toolbar Highlights (frontend)

- **Line Width slider** (right panel, always visible): per-tab,
  persisted. Drives raw + per-peak `borderWidth`; envelope uses
  `min(width + 1, 6)` so it stays visually distinct.
- **Vertical Offset slider** (right panel, stack tabs only): vertical
  separation between visible entries.
- **`⇅ Organize Tabs`** (chart toolbar): sorts spectrum tabs as
  Survey → element-alphabetical → Other; stack tabs cluster at the
  end as a block, preserving their relative order.
- **`+ Stack` / `+ Add Spectrum ▾`** (chart toolbar): create a new
  empty stack and add open spectrum tabs to the active stack.
- **Auto-Fit C1s Graphite** (Actions menu): one-click C1s peak model
  + charge correction. Enabled only when the midpoint of the DATA the fit
  would use is in 270–315 eV — for the active tab the live selection
  `getROIData()` returns, never the tab record's stale window or a typed
  window reaching past the data (`isC1sTab`, unit F3 2026-09-27, sweep M5).
- **ROI past the data / centre outside the data** (2026-09-25, warn only):
  `getROIData()` has always clamped an ROI to the data it selects; the page
  now SAYS so under the ROI fields ("ROI extends past your data — clipped
  to X–Y eV" when a field reaches more than one sampling step past the
  data; amber when min > max or the window misses the data) and badges a
  peak card whose centre lies outside the selected data ("outside data").
  Neither the fields nor the peaks are ever moved; the fit, Find Peaks
  (same inclusive mask on the same corrected energies) and saves read the
  ROI exactly as before. `_roiWindowStatus` / `_refreshRoiAndCentreWarnings`,
  refreshed in place from `updatePlot`; plan
  `docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md`.
- **Manual anchor background**: place anchors on the chart for
  per-spectrum hand-tuned background curves; persisted as
  `tab.manualAnchors`.

## Tests

```
tests/test_la_continuous_m.py   # LA(α,β,m) continuity across integer-m kernel widths
tests/test_la_short_input.py    # LA edge cases on very-short input arrays
tests/test_mixed_ds_lacx_e2e.py # End-to-end: a fit with both DS+G and CasaXPS LA peaks
```

Run via `pytest tests/`.

## Reference Energies for Common Regions

There is **no demo-spectrum loader** in the app (a `loadDemo(...)`
function does not exist — earlier versions of this file were stale).
Typical regions for hand-testing:

| Region | Window | Notes |
|--------|--------|-------|
| Fe 2p | 700–740 eV | Fe(0) at 706.6, Fe(III) at 710.5, satellite at 713.5 |
| U 4f | 370–415 eV | UCl4-like U(IV); 4f₇/₂ at 380.9, 4f₅/₂ at 391.8 (offset 10.9 eV) |
| C 1s | 280–295 eV | sp², sp³, C-O, C=O, COOH components; charge ref at 284.8 eV |

## Known Issues

- Legacy document-level tooltip handlers call `e.target.closest(...)`
  without checking that the event target is an Element
  (`templates/index.html` around the `data-xps-tip` listeners); events
  targeting non-Elements throw `e.target.closest is not a function`.
  Needs an `instanceof Element` guard in a future pass.
- Gunicorn `--reload` watches Python files only — **edits to
  `templates/index.html` are NOT picked up** outside Flask debug mode
  because Jinja caches compiled templates per worker. Restart the dev
  gunicorn after template changes before browser-verifying.

## Development Workflow

- Develop on feature branches off `main`.
- Production gunicorn serves whatever is on disk at
  `templates/index.html`. Browser-verify changes on a separate dev
  gunicorn on **port 5151** (run with `--reload`) before merging.
- Merge to main only after browser verification.
- Design memos and implementation plans live under
  `docs/superpowers/plans/` and are committed alongside the changes
  they describe.

exec
/bin/zsh -lc "rg -n 'isC1sTab|getROIData\\(|chargeRef|charge.reference|updateAutoFit|autoFitBtn|autofitBtn' templates/index.html; rg --files docs/findings/noise-floor-occupancy; rg --files | rg '("'^|/)(engine|grammar|ranking).*'"\\.py"'$|package.json|conftest'"'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
5087:function getROIData() {
5105:// WARN, NEVER REINTERPRET. getROIData() already selects the corrected
5120:  const { be } = getROIData();
5217:// Normalize charge-reference flags on a freshly-loaded peak list.
5234:// Toggle the charge-reference designation on peak `id`.
5248:// charge-reference. Phase 2 (C1s assisted batch) calls this as a gate.
5795:  const { be, inten } = getROIData();
6105:  return !!(tab && isC1sTab(tab));
6134:  const { be: _roiBE } = (typeof getROIData === 'function' && state.rawBE.length) ? getROIData() : { be: [] };
6718:  const enabled = !!tab && isC1sTab(tab);
7239:  const { be: roiBE } = (typeof getROIData === 'function' && state.rawBE && state.rawBE.length) ? getROIData() : { be: [] };
7344:  const { be: be2, inten: inten2 } = getROIData();
7563:  if (!isC1sTab(tab)) {
7585:  const { be: corrBE, inten } = getROIData();
7637:    const { be: be2, inten: inten2 } = getROIData();
7679:        // step (c): is the charge-reference anchor REQUIRED? The server refits
7753:// tab the live selection getROIData() returns (the typed fields, clipped to the
7759:function isC1sTab(tab) {
7764:    be = getROIData().be;
8126:  const { be, inten } = getROIData();
8946:    be = getROIData().be;
9775:  const { be, inten } = getROIData();
10545:  const { be, inten } = getROIData();
11224:  const { be, inten } = getROIData();
11285:  const { be, inten } = getROIData();
12477:    const roiSt = _roiWindowStatus();    // warn only: the fit below uses getROIData() exactly as before
12478:    const { be, inten } = getROIData();
15170:            'other regions are unaffected. The charge reference ' +
16386:  // unfit-preview path (getROIData() + client-side computeBackground()),
docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch
docs/findings/noise-floor-occupancy/variant_F_support_test.patch
docs/findings/noise-floor-occupancy/README.md
autofit/engine.py
autofit/grammar.py
tests/conftest.py

exec
/bin/zsh -lc "sed -n '5025,5110p' templates/index.html; sed -n '6085,6110p' templates/index.html; sed -n '6685,6735p' templates/index.html; sed -n '7540,7655p' templates/index.html; rg -n 'activateTab|switchTab|activeId =|_recomputeAutoFitMenuState\\(' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
    if (!isNaN(roiMaxVal)) roiMaxEl.value = (roiMaxVal - delta).toFixed(1);

    // Background endpoints
    const bgStartEl = document.getElementById('bg-start');
    const bgEndEl = document.getElementById('bg-end');
    const bgStartVal = parseFloat(bgStartEl.value);
    const bgEndVal = parseFloat(bgEndEl.value);
    if (!isNaN(bgStartVal)) bgStartEl.value = (bgStartVal - delta).toFixed(1);
    if (!isNaN(bgEndVal)) bgEndEl.value = (bgEndVal - delta).toFixed(1);

    // Peak centers
    for (const p of state.peaks) {
      p.center -= delta;
    }

    // Manual background anchors. Anchors are DATA-ATTACHED like peak
    // centers (x = a data point's corrected BE at placement time, y = that
    // point's intensity), so they follow the same -delta migration as the
    // ROI/bg fields and peak centers above — NOT the reference-marker
    // convention (literature markers stay at nominal corrected BE). y is
    // untouched: intensity is unaffected by charge correction. Saved files
    // need no migration — anchors persist alongside the tab's ccShift, so
    // every save is a self-consistent snapshot.
    const ccAnchors = _getManualAnchors();
    for (const a of ccAnchors) {
      a.x -= delta;
    }

    // Background cache is no longer valid after CC shift
    _invalidateBgCache();
  }

  const shift = -state.ccShift;
  document.getElementById('cc-shift-display').textContent = (shift >= 0 ? '+' : '') + shift.toFixed(3) + ' eV';
  updatePlot();
  // Re-render the per-peak panels so the C 1s graphite checkbox
  // appears/disappears reactively when the method changes (and any
  // stale isChargeReference flags are cleared by renderPeakList).
  renderPeakList();
  // Reference Lines panel shows the corrected range + a not-charge-corrected
  // hint — both go stale when the correction changes.
  if (typeof _refOnTabChange === 'function') _refOnTabChange();
  // fix #5: updatePlot() rebuilds the main chart at the corrected axis, but the
  // xpsRefLinesPlugin gates on `chart === state.chart` and is skipped on the
  // `new Chart()` first paint (the same render-timing gap _refRenderReferenceChart
  // already works around). renderPeakList/_refOnTabChange only refresh panel/legend
  // DOM — no chart repaint — so element reference overlays (lines, bands, labels)
  // would vanish until the next hover/toggle. Re-issue the guarded reference-overlay
  // repaint so they stay painted through a charge-correction change. Leaf-level
  // chart.update('none'); positioning math and ccShift are untouched (overlays stay
  // at nominal corrected BE), and it is a no-op when no chart/spectrum/overlays exist.
  if (typeof _refRepaint === 'function') _refRepaint();
}

function getCorrectedBE() {
  const shift = isNaN(state.ccShift) ? 0 : state.ccShift;
  return state.rawBE.map(b => b - shift);
}

// ═══════════════════════════════════════════════════
// ROI FILTERING
// ═══════════════════════════════════════════════════
function getROIData() {
  const roiMinRaw = parseFloat(document.getElementById('roi-min').value);
  const roiMaxRaw = parseFloat(document.getElementById('roi-max').value);
  // NaN bounds mean the field is empty — use full range rather than filtering everything out
  const roiMin = isNaN(roiMinRaw) ? -Infinity : roiMinRaw;
  const roiMax = isNaN(roiMaxRaw) ?  Infinity : roiMaxRaw;
  const corrBE = getCorrectedBE();
  const be = [], inten = [];
  for (let i = 0; i < corrBE.length; i++) {
    if (corrBE[i] >= roiMin && corrBE[i] <= roiMax) {
      be.push(corrBE[i]);
      inten.push(state.rawIntensity[i]);
    }
  }
  return { be, inten };
}

// ── ROI past the data / centre outside the data (2026-09-25) ─────────────
// WARN, NEVER REINTERPRET. getROIData() already selects the corrected
// energies inside [roi-min, roi-max], so an ROI past the data is clamped to
// the data in every fit, background, area and export — the defect was that
// nothing said so. This reports the window actually used; it writes nothing
// back into the fields, the peaks or the fit-evidence key. Find Peaks sends
// the same two numbers against the same corrected energies to a server mask
    btn.innerHTML = '&#x1f512; Lock All';
    btn.title = 'Lock all fit parameters on all peaks';
  }
}

// ═══════════════════════════════════════════════════
// PEAK LIST UI
// ═══════════════════════════════════════════════════
// The per-peak "Charge-correction reference (C 1s graphite)" checkbox is
// only meaningful when the user is on a C 1s spectrum AND the global
// charge-correction method is set to graphite. When either condition is
// false, the checkbox is hidden completely AND any peak that previously
// held the marker is silently unchecked, so re-entering the valid mode
// gives a clean unchecked state rather than a stale stored value.
function _isChargeRefAllowed() {
  const cm = document.getElementById('cc-method');
  if (!cm || cm.value !== 'c1s') return false;
  const tab = (typeof tabManager !== 'undefined' && tabManager.activeId)
    ? tabManager._getTab(tabManager.activeId)
    : null;
  return !!(tab && isC1sTab(tab));
}

function _clearDisallowedChargeRef() {
  if (_isChargeRefAllowed()) return;
  for (const p of state.peaks) {
  }
}

function _showFitSpinner() {
  const overlay = document.getElementById('fit-spinner-overlay');
  const label = document.getElementById('fit-spinner-label');
  if (overlay) overlay.style.display = 'flex';
  if (label) label.innerHTML = 'Fitting<span class="ellipsis"></span>';
  document.querySelector('.btn-green').disabled = true;
  _bgSubFitInFlight = true;
  _updateBgSubPillEnabled();
  // After 2s, update label to hint at perturbations
  _showFitSpinner._timer = setTimeout(() => {
    if (label) label.innerHTML = 'Running perturbations<span class="ellipsis"></span>';
  }, 2000);
}
function _hideFitSpinner() {
  const overlay = document.getElementById('fit-spinner-overlay');
  if (overlay) overlay.style.display = 'none';
  document.querySelector('.btn-green').disabled = false;
  clearTimeout(_showFitSpinner._timer);
  _bgSubFitInFlight = false;
  _updateBgSubPillEnabled();
}

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

// Late-init for Auto-Fit menu state (in case startup runs before the
// menu item is in the DOM).
window.addEventListener('DOMContentLoaded', () => {
  if (typeof _recomputeAutoFitMenuState === 'function') _recomputeAutoFitMenuState();
});

// Returns a Promise<boolean> — true if user clicks Proceed, false on Cancel/X.
        continue;
      }
      misses = 0;
      if (rec.status === 'done') return rec.result;
      if (rec.status === 'error') throw _fitHttpError(rec.http_status || 500, rec.error);
      if (rec.status === 'cancelled') throw _fitHttpError(409, 'The fit was stopped on the server before it finished. Run it again.');
      if (Number.isFinite(rec.heartbeat_age_sec) && rec.heartbeat_age_sec > FIT_HEARTBEAT_LOST_SEC) {
        _cancelFitJob(jobId);
        throw _fitHttpError(503, 'The server stopped working on the fit (no sign of it for ' + Math.round(rec.heartbeat_age_sec) +
                                 ' s — it was probably restarted). Run the fit again.');
      }
      if (typeof guard.onProgress === 'function') guard.onProgress(rec);
    }
  } finally {
    _runningFitJobs.delete(jobId);
  }
}

async function runAutoFitC1sGraphite() {
  // Pre-conditions
  if (!state.rawBE || !state.rawBE.length) { notify('Load a spectrum first.', 'amber'); return; }
  const tab = tabManager._getTab(tabManager.activeId);
  if (!tab) { notify('No active tab.', 'amber'); return; }
  if (!isC1sTab(tab)) {
    notify('Auto-Fit C1s Graphite is only available for C1s spectra (ROI midpoint 270–315 eV).', 'amber');
    return;
  }
  // OWNER FIRST: the confirmation below is an await; the tab that is active
  // when it resolves may not be the one the user asked to auto-fit.
  const fittingTab = _opOwner();
  if (!fittingTab) { notify('No active spectrum tab.', 'amber'); return; }
  // Confirmation if existing peaks
  if (state.peaks.length >= 1) {
    const proceed = await _showAutoFitConfirmModal(state.peaks.length);
    if (!proceed) return;
    if (!_ownerActive(fittingTab)) {
      notify('Auto-fit cancelled — the tab changed while the confirmation was open.', 'amber');
      return;
    }
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
  const provisionalShift = graphiteRaw - 284.50;

  // Step 3: assess low-BE region using provisional shift (no state mutation yet).
  const assessment = assessLowBERegion(rawBE, bgSub, provisionalShift);

  // Step 4: build the peak model (in corrected frame after provisional shift).
  pushUndo();
  state.peaks = [];
  state.fitResult = null;
  // Apply provisional shift via updateChargeCorrection so ROI/bg DOM fields
  // shift along with state.ccShift.
  const cm = document.getElementById('cc-method');
  const co = document.getElementById('cc-obs');
  const cl = document.getElementById('cc-lit');
  cm.value = 'c1s';
  co.value = graphiteRaw.toFixed(3);
  cl.value = '284.50';
  updateChargeCorrection();
  // Now build the peak list (graphite center 284.50 in this frame).
  const newPeaks = buildAutoFitModel(assessment);
  state.peaks = newPeaks;
  state.nextId = Math.max(0, ...state.peaks.map(p => p.id)) + 1;
  renderPeakList();

  // Step 5: run /api/fit with AbortController + spinner.
  _showFitSpinner();
  const spinLabel = document.getElementById('fit-spinner-label');
  if (spinLabel) spinLabel.textContent = 'Auto-fitting…';
  const runBtn = document.querySelector('.btn-green');
  if (runBtn) runBtn.disabled = true;

  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(new DOMException('timeout', 'AbortError')), 120000);

  try {
    const { be: be2, inten: inten2 } = getROIData();
    const bgType = document.getElementById('bg-type').value;
    const bgStart = parseFloat(document.getElementById('bg-start').value);
    const bgEnd = parseFloat(document.getElementById('bg-end').value);
    // Inclusive bg window — the same point set computeBackgroundCore draws;
    // the backend slices end-exclusive, so the request sends i1 + 1.
    const bgWin = _bgWindowIndices(be2, bgStart, bgEnd);
    const epAvg = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
    const fitMethod = document.getElementById('fit-method').value;

    // The anchor whose necessity the server must test — captured with the
    // other request inputs, before the first await (a tab switch during the
    // upload must not send another tab's id).
    const anchorId = String((state.peaks.find(p => p.name === 'Graphite') || state.peaks[0]).id);
    // the model and its fit context as sent (F1, Codex round 1): a result must
    // not be applied, and stamped current, over a model edited while it ran
    const ctxAtRequest = _startsLiveKey();
    // Build peak specs and overlay the per-peak bounds we attached in buildAutoFitModel.
    const peakSpecs = state.peaks.map(p => {
1115:     mounted across tab switches (single bind point in activateTab). */
2064:                <input type="number" id="roi-min" value="706" step="0.5" oninput="updatePlot();_recomputeAutoFitMenuState()">
2068:                <input type="number" id="roi-max" value="726" step="0.5" oninput="updatePlot();_recomputeAutoFitMenuState()">
2201:          <div class="tab active" onclick="switchTab(this,'peaks')">Peaks</div>
2202:          <div class="tab" onclick="switchTab(this,'results')">Results</div>
2203:          <div class="tab" onclick="switchTab(this,'quantify')">Quantify</div>
2204:          <div class="tab survey-tab" id="survey-tab-btn" onclick="switchTab(this,'survey')">Survey</div>
3136:    this.activeId = null;
3188:    this.activateTab(id);
3214:    this.activateTab(id);
3218:  activateTab(id) {
3219:    if (this.activeId === id) return;
3229:    this.activeId = id;
3247:    if (typeof _recomputeAutoFitMenuState === 'function') _recomputeAutoFitMenuState();
3301:      this.activeId = null;
3327:    if (this.activeId === id) {
3329:      this.activeId = null; // force re-activate
3330:      this.activateTab(this.tabs[nextIdx].id);
3519:          this.activateTab(tabId);
3584:        if (peaksBtn) switchTab(peaksBtn, 'peaks');
3653:    this.activateTab(surveyId);
3802:      this.activateTab(this._preSurveyTabId);
6711:// Called from activateTab and from ROI-input event handlers.
6712:function _recomputeAutoFitMenuState() {
6732:  if (typeof _recomputeAutoFitMenuState === 'function') _recomputeAutoFitMenuState();
7013:  // newly-migrating anchors). activateTab already synced the provisional
9360:// source tab — they return to the stack via activateTab → updatePlot →
9407:// in stack mode), and any such change triggers a fresh activateTab →
9587:  // against. Without this, _mainYMax stays null after activateTab and the
9992:  // which are swapped by activateTab, so reading from the live chart would
10194:  // Restore X zoom from tab-scoped state vars (already swapped by activateTab).
11152:  if (restoreId) tabManager.activateTab(restoreId);
12007:function switchTab(el, name) {
12451:    // Now activate this tab so state is populated. activateTab is a no-op
12456:    if (tabManager.activeId === tid) {
12463:      tabManager.activateTab(tid);
12499:  tabManager.activateTab(sourceId);
14787:    tabManager.activateTab(t.id);
16400:    // "no committed fit yet" state TabManager.activateTab already uses

exec
/bin/zsh -lc "cat docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch; diff -u docs/findings/noise-floor-occupancy/variant_F_support_test.patch docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch; rg -n '_extract_fitted_components|match_components_to_slots|rank_and_filter|decisive|noise_floor|_evaluate_proposal' autofit/engine.py; rg -n 'def _component_support|noise_floor' fitting.py; rg -n 'design rule|scale.free|tolerance' CLAUDE.md" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
diff --git a/autofit/confidence.py b/autofit/confidence.py
index bb74778..ab2897f 100644
--- a/autofit/confidence.py
+++ b/autofit/confidence.py
@@ -83,6 +83,9 @@ def _max_correlation(report: ModelReport, role: str) -> Optional[float]:
     return float(np.max(sub)) if sub.size else None
 
 
+from fitting import SUPPORT_MIN_F as _SUPPORT_MIN_F  # F3: one threshold, the server's
+
+
 def build_confidence_vector(
     report: ModelReport,
     role: str,
@@ -96,12 +99,19 @@ def build_confidence_vector(
                 if h.startswith(f"{role}:")]
 
     amplitude = float(comp.amplitude) if comp is not None else None
-    floor = detection_floor_multiple * noise_floor
+    # F3 (2026-09-27): detectability is the support F test on the fit
+    # (fitting._component_support, the server's statistic), not multiples of an
+    # absolute 1-count floor. above_floor = supported (F >= SUPPORT_MIN_F);
+    # present_but_poorly_constrained = the fit gains from it but not
+    # significantly; not_confidently_detected = removing it costs nothing.
+    support = getattr(comp, "support", None) if comp is not None else None
     if amplitude is None:
         detect_status = "not_fitted"
-    elif amplitude >= floor:
+    elif support is None:
+        detect_status = "above_floor" if amplitude > 0 else "not_confidently_detected"
+    elif support.get("supported"):
         detect_status = "above_floor"
-    elif amplitude > noise_floor:
+    elif (support.get("delta_chi2") or 0.0) > 0:
         detect_status = "present_but_poorly_constrained"
     else:
         detect_status = "not_confidently_detected"
@@ -122,9 +132,9 @@ def build_confidence_vector(
         },
         "detectability": {
             "amplitude": amplitude,
-            "noise_floor": noise_floor,
-            "floor_multiple": detection_floor_multiple,
-            "floor_multiple_is_tunable": True,
+            "basis": "support_f_test",       # F3: fitting._component_support, F >= SUPPORT_MIN_F
+            "support_f": (support or {}).get("f"),
+            "support_min_f": _SUPPORT_MIN_F,
             "status": detect_status,
         },
         "identifiability": {
diff --git a/autofit/engine.py b/autofit/engine.py
index dbf4fd7..e1a729e 100644
--- a/autofit/engine.py
+++ b/autofit/engine.py
@@ -36,6 +36,7 @@ from typing import Callable, Optional
 
 import numpy as np
 from lmfit import Model, Parameters
+import fitting as _fitting  # F3: the server's support statistic, one definition
 from lmfit.model import ModelResult
 from scipy.integrate import trapezoid
 
@@ -637,6 +638,17 @@ class FittedComponent:
     amplitude: float
     shape_params: dict
     line_shape: Optional[LineShape] = None
+    # Unit F3 (2026-09-27): does the fit that produced this component need it?
+    # fitting._component_support on that fit — with the other components held
+    # as fitted, removing this one must make the fit significantly worse (F >=
+    # SUPPORT_MIN_F). The occupancy decisions (slot matching, the proposal
+    # gate, detectability) read this instead of an absolute amplitude floor
+    # of 1 count, which judged a slot "occupied" at amplitude 1.5 and not at
+    # 0.5 whatever the data's scale (sweep M9; design rule "thresholds on
+    # data-scaled quantities fail"). None only where no fit is behind the
+    # component (hand-built in tests): then occupancy falls back to amplitude
+    # > 0, a sign test.
+    support: Optional[dict] = None
 
 
 @dataclass
@@ -652,10 +664,50 @@ class FitOutcome:
     boundary_hits: list[str] = field(default_factory=list)
 
 
+def _component_supports(result: ModelResult) -> dict[str, dict]:
+    """``fitting._component_support`` for every peak component of an lmfit
+    result, keyed by prefix — the one definition the server uses (step (b)).
+    Empty when the result carries no data (never raises: occupancy then falls
+    back to the sign test)."""
+    try:
+        comps = result.eval_components()
+        data = np.asarray(result.data, float)
+        fitted = np.asarray(result.best_fit, float)
+        w = result.weights if result.weights is not None else np.ones_like(data)
+        w = np.broadcast_to(np.asarray(w, float), data.shape)
+        n_free_total = int(result.nvarys)
+    except Exception:
+        return {}
+    out = {}
+    for prefix, comp_y in comps.items():
+        n_free_comp = sum(1 for n, par in result.params.items()
+                          if n.startswith(prefix) and par.vary and par.expr is None)
+        try:
+            out[prefix] = _fitting._component_support(data, fitted, np.asarray(comp_y, float), w,
+                                                      n_free_comp, n_free_total)
+            out[prefix]["_p"] = max(1, n_free_comp)
+        except Exception:
+            continue
+    return out
+
+
+def _occupies(comp: "FittedComponent") -> bool:
+    """A slot is occupied by a component the data support (F3). No threshold
+    on any data-scaled quantity: the support F test where a fit is behind the
+    component, else the sign of its amplitude."""
+    if comp.support is not None:
+        # PROBE (likelihood-ratio variant, not for shipping): the Poisson-weighted
+        # chi-square gain per free parameter, NOT normalised by the fit's misfit
+        d = comp.support.get("delta_chi2") or 0.0
+        return bool(d > 0 and d / max(1, comp.support.get("_p", 1)) >= _fitting.SUPPORT_MIN_F)
+    return comp.amplitude > 0
+
+
 def _extract_fitted_components(
     result: ModelResult, model: CandidateModel
 ) -> list[FittedComponent]:
     out: list[FittedComponent] = []
+    supports = _component_supports(result)
     for slot in model.slots:
         prefix = _slot_prefix(slot.role)
         pars = result.params
@@ -676,6 +728,7 @@ def _extract_fitted_components(
             slot_role=slot.role, position=center, fwhm=fwhm,
             amplitude=amplitude, shape_params=shape_params,
             line_shape=slot.line_shape,
+            support=supports.get(prefix),
         ))
     return out
 
@@ -1055,7 +1108,7 @@ def match_components_to_slots(
                                       (bound_overrides or {}).get(slot.role))
         return (lo <= comp.position <= hi
                 and slot.fwhm_range[0] <= comp.fwhm <= slot.fwhm_range[1]
-                and comp.amplitude > noise_floor)
+                and _occupies(comp))       # F3: supported by the data, not amplitude > 1 count
 
     def _window_center(slot: ComponentSlot) -> float:
         # NEVER the widened bound (Codex-caught, round 2): this is a
@@ -1077,7 +1130,7 @@ def match_components_to_slots(
             orphans.append(FittedComponent(
                 slot_role="unmatched", position=comp.position, fwhm=comp.fwhm,
                 amplitude=comp.amplitude, shape_params=comp.shape_params,
-                line_shape=comp.line_shape,
+                line_shape=comp.line_shape, support=comp.support,
             ))
             continue
 
@@ -1095,7 +1148,7 @@ def match_components_to_slots(
         claimed = FittedComponent(
             slot_role=best_slot.role, position=comp.position, fwhm=comp.fwhm,
             amplitude=comp.amplitude, shape_params=comp.shape_params,
-            line_shape=comp.line_shape,
+            line_shape=comp.line_shape, support=comp.support,
         )
         if incumbent is None:
             slot_map[best_slot.role] = claimed
@@ -2229,8 +2282,10 @@ def _attempt_proposal(
     # to a wall (Codex fwhm-cap review, run B BLOCKER).
     width_cap_hit = f"{spec.role}:fwhm@max"
     pr.boundary_hits = _proposed_slot_pegs(primary, spec.role)
-    if comp.amplitude <= noise_floor:
-        return _fast(f"amplitude {comp.amplitude:.1f} ≤ noise_floor {noise_floor:.1f}")
+    if not _occupies(comp):
+        f = (comp.support or {}).get("f")
+        return _fast("not supported by the data (removing it does not make the fit significantly worse"
+                     + (f", F = {f:.2f} < {_fitting.SUPPORT_MIN_F:.0f}" if f is not None else "") + ")")
     spurious_hits = [h for h in pr.boundary_hits if h != width_cap_hit]
     if spurious_hits:
         return _fast(f"proposed slot boundary pegs: {spurious_hits}")
diff --git a/autofit/grammar.py b/autofit/grammar.py
index c9a85cd..bed2606 100644
--- a/autofit/grammar.py
+++ b/autofit/grammar.py
@@ -181,11 +181,15 @@ class ComponentSlot:
     broad_justification: Optional[str] = None
 
     def contains(self, be: float, fwhm: float, amplitude: float,
-                 noise_floor: float) -> bool:
+                 noise_floor: float = 0.0) -> bool:
+        # F3 (2026-09-27): occupancy is decided by the support F test on the
+        # fit (engine._occupies); this geometric check keeps only the sign of
+        # the amplitude. ``noise_floor`` is accepted and ignored (no caller in
+        # the engine passes it any more).
         return (
             self.be_window[0] <= be <= self.be_window[1]
             and self.fwhm_range[0] <= fwhm <= self.fwhm_range[1]
-            and amplitude > noise_floor
+            and amplitude > 0
         )
 
 
--- docs/findings/noise-floor-occupancy/variant_F_support_test.patch	2026-09-27 02:09:01
+++ docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch	2026-09-27 02:09:01
@@ -49,7 +49,7 @@
          },
          "identifiability": {
 diff --git a/autofit/engine.py b/autofit/engine.py
-index dbf4fd7..9bad455 100644
+index dbf4fd7..e1a729e 100644
 --- a/autofit/engine.py
 +++ b/autofit/engine.py
 @@ -36,6 +36,7 @@ from typing import Callable, Optional
@@ -78,7 +78,7 @@
  
  
  @dataclass
-@@ -652,10 +664,46 @@ class FitOutcome:
+@@ -652,10 +664,50 @@ class FitOutcome:
      boundary_hits: list[str] = field(default_factory=list)
  
  
@@ -103,6 +103,7 @@
 +        try:
 +            out[prefix] = _fitting._component_support(data, fitted, np.asarray(comp_y, float), w,
 +                                                      n_free_comp, n_free_total)
++            out[prefix]["_p"] = max(1, n_free_comp)
 +        except Exception:
 +            continue
 +    return out
@@ -113,7 +114,10 @@
 +    on any data-scaled quantity: the support F test where a fit is behind the
 +    component, else the sign of its amplitude."""
 +    if comp.support is not None:
-+        return bool(comp.support.get("supported"))
++        # PROBE (likelihood-ratio variant, not for shipping): the Poisson-weighted
++        # chi-square gain per free parameter, NOT normalised by the fit's misfit
++        d = comp.support.get("delta_chi2") or 0.0
++        return bool(d > 0 and d / max(1, comp.support.get("_p", 1)) >= _fitting.SUPPORT_MIN_F)
 +    return comp.amplitude > 0
 +
 +
@@ -125,7 +129,7 @@
      for slot in model.slots:
          prefix = _slot_prefix(slot.role)
          pars = result.params
-@@ -676,6 +724,7 @@ def _extract_fitted_components(
+@@ -676,6 +728,7 @@ def _extract_fitted_components(
              slot_role=slot.role, position=center, fwhm=fwhm,
              amplitude=amplitude, shape_params=shape_params,
              line_shape=slot.line_shape,
@@ -133,7 +137,7 @@
          ))
      return out
  
-@@ -1055,7 +1104,7 @@ def match_components_to_slots(
+@@ -1055,7 +1108,7 @@ def match_components_to_slots(
                                        (bound_overrides or {}).get(slot.role))
          return (lo <= comp.position <= hi
                  and slot.fwhm_range[0] <= comp.fwhm <= slot.fwhm_range[1]
@@ -142,7 +146,7 @@
  
      def _window_center(slot: ComponentSlot) -> float:
          # NEVER the widened bound (Codex-caught, round 2): this is a
-@@ -1077,7 +1126,7 @@ def match_components_to_slots(
+@@ -1077,7 +1130,7 @@ def match_components_to_slots(
              orphans.append(FittedComponent(
                  slot_role="unmatched", position=comp.position, fwhm=comp.fwhm,
                  amplitude=comp.amplitude, shape_params=comp.shape_params,
@@ -151,7 +155,7 @@
              ))
              continue
  
-@@ -1095,7 +1144,7 @@ def match_components_to_slots(
+@@ -1095,7 +1148,7 @@ def match_components_to_slots(
          claimed = FittedComponent(
              slot_role=best_slot.role, position=comp.position, fwhm=comp.fwhm,
              amplitude=comp.amplitude, shape_params=comp.shape_params,
@@ -160,7 +164,7 @@
          )
          if incumbent is None:
              slot_map[best_slot.role] = claimed
-@@ -2229,8 +2278,10 @@ def _attempt_proposal(
+@@ -2229,8 +2282,10 @@ def _attempt_proposal(
      # to a wall (Codex fwhm-cap review, run B BLOCKER).
      width_cap_hit = f"{spec.role}:fwhm@max"
      pr.boundary_hits = _proposed_slot_pegs(primary, spec.role)
83:# candidate; the result carries conditional_reason='decisive_override'.
84:# Without any override, a clean-but-terrible fit masks a decisively better
655:def _extract_fitted_components(
769:    tier via rank_and_filter) rather than silently accepted.
923:        components=_extract_fitted_components(result, model),
1039:def match_components_to_slots(
1042:    noise_floor: float,
1058:                and comp.amplitude > noise_floor)
1168:    noise_floor: float,
1234:        slot_map = match_components_to_slots(outcome.components, model, noise_floor,
1406:    noise_floor: float,
1411:    sigma = np.sqrt(np.maximum(y, noise_floor))
1500:    # Full lmfit param names fixed at their bounds by the decisive-override
1597:    #   'decisive_override'  — clean survivors exist but a bound-fixed refit
1610:    # decisive threshold — {name, bic_star, delta_bic_vs_winner,
1645:def rank_and_filter(
1716:    # NOTE: the decisive-override path (clean survivors exist but a
1718:    # compare_models — it needs the spectrum to refit; rank_and_filter is
1808:    noise_floor: float = 1.0,
1856:        local_sigma = float(np.median(np.sqrt(np.maximum(y_asc[mask], noise_floor)))) \
1857:            if mask.sum() > 1 else float(np.sqrt(max(noise_floor, 1.0)))
2007:    noise_floor: float,
2014:    sigma = np.sqrt(np.maximum(y, noise_floor))
2163:    noise_floor: float,
2232:    if comp.amplitude <= noise_floor:
2233:        return _fast(f"amplitude {comp.amplitude:.1f} ≤ noise_floor {noise_floor:.1f}")
2240:    local_sigma = float(np.median(np.sqrt(np.maximum(y[mask], noise_floor)))) \
2241:        if mask.sum() > 1 else float(np.sqrt(max(noise_floor, 1.0)))
2273:        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
2312:    residuals = compute_residual_diagnostics(x, y, y_fit_aug, noise_floor, diagnostic_windows)
2391:    noise_floor: float,
2446:        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
2460:            x, y, y_fit, noise_floor, diagnostic_windows),
2472:        # promoted via decisive-override keeps its width_capped/proposed_peaks
2479:def _apply_decisive_override(
2486:    noise_floor: float,
2507:                                   diagnostic_windows, noise_floor,
2524:        result.conditional_reason = "decisive_override"
2554:    noise_floor: float = 1.0,
2575:    proposals, bound-fixed refits, decisive override, detection). Default 1
2586:    refits, the proposal pass, and the bound-fixed decisive-override
2627:            noise_floor=noise_floor,
2646:                noise_floor=noise_floor,
2826:            noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
2840:        residuals = compute_residual_diagnostics(x, y, y_fit, noise_floor, diagnostic_windows)
2882:                    x, y, current_y_fit, noise_floor, current.model,
2904:                        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
2944:    result = rank_and_filter(
2950:    result = _apply_decisive_override(
2954:        noise_floor=noise_floor,
3000:    # at ΔBIC* +74…+944): a FILTERED candidate whose BIC* decisively beats
3006:        # promotion LINEAGE, not just names: a decisive-override winner is
1444:def _component_support(y_sub, fitted_sub, comp_y, weights, n_free_comp, n_free_total) -> dict[str, Any]:
173:anchor (answer: a scale-free F test), then two tolerances on that F test
174:(answer: none). Prefer a scale-free comparison with no tolerance. If a
179:`docs/autofit/codex/autofit_zero_graphite_*`, the DE unit's tolerance rounds
182:side: every χ² comparison tolerance produced reachable false failures and
375:bound, and every tolerance tried for that comparison produced reachable
471:~1e-4 relative in an area at its stopping tolerance of 1e-8. Worse, the
477:internals for this, and do not tighten the tolerance: ftol = xtol = gtol =
814:  so a chain of links in any request order resolves; NO tolerance of any

exec
/bin/zsh -lc 'rg --files -g AGENTS.md /Users/skyefortier/xps-app /Users/skyefortier/.codex 2>/dev/null | head -30; node --test tests/js/autofit_c1s_gate.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 80ms:
# Subtest: the sweep reproduction: record window on C 1s, U 4f typed in the fields (no tab switch) — the gate CLOSES
ok 1 - the sweep reproduction: record window on C 1s, U 4f typed in the fields (no tab switch) — the gate CLOSES
  ---
  duration_ms: 5.29483
  type: 'test'
  ...
# Subtest: the SELECTED data decide, not the typed midpoint of a window that reaches past the data
ok 2 - the SELECTED data decide, not the typed midpoint of a window that reaches past the data
  ---
  duration_ms: 1.188802
  type: 'test'
  ...
# Subtest: a non-active record is judged on its saved window over its own corrected data
ok 3 - a non-active record is judged on its saved window over its own corrected data
  ---
  duration_ms: 0.722509
  type: 'test'
  ...
# Subtest: every caller of the gate is for the active tab (menu state, charge-reference permission, the Auto-Fit run)
ok 4 - every caller of the gate is for the active tab (menu state, charge-reference permission, the Auto-Fit run)
  ---
  duration_ms: 1.866878
  type: 'test'
  ...
1..4
# tests 4
# suites 0
# pass 4
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 113.063892

codex
The new tests pass, and the stale-window regression is covered by assertions that would fail against the old gate. I found a mismatch between the record path and `getROIData()`: reversed bounds and partly blank bounds select differently. I’m checking whether current callers can reach that path and whether tab activation reads the live state before it has finished loading.

exec
/bin/zsh -lc "sed -n '3130,3275p' templates/index.html; sed -n '3525,3610p' templates/index.html; rg -n '_loadTab|_syncState|_applyUI|_restoreUI|renderPeakList\\(|_clearDisallowedChargeRef\\(' templates/index.html | head -70; sed -n '6105,6145p' templates/index.html; sed -n '1440,1510p' fitting.py; sed -n '630,700p' autofit/engine.py; sed -n '1035,1155p' autofit/engine.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
// and the #bg-endpoint-avg input's max attribute.
const ENDPOINT_AVG_MAX = 50;

class TabManager {
  constructor() {
    this.tabs = [];
    this.activeId = null;
    this._colorIdx = 0;
    this._preSurveyTabId = null; // tab to restore when leaving survey sidebar tab
  }

  // ── Core tab lifecycle ──────────────────────────

  createTab(name, be, inten, sourcePath = null) {
    const id = 'tab_' + Math.random().toString(36).slice(2, 9);
    const color = TAB_COLORS[this._colorIdx++ % TAB_COLORS.length];

    // Sort by BE descending (same as setSpectrum)
    const pairs = be.map((b, i) => [b, inten[i]]).sort((a, b) => b[0] - a[0]);
    const sortedBE = pairs.map(p => p[0]);
    const sortedInten = pairs.map(p => p[1]);

    const beRange = sortedBE.length ? sortedBE[0] - sortedBE[sortedBE.length - 1] : 0;
    const isSurvey = /survey/i.test(name) || beRange > 200;

    // Strip file extension for display name
    const displayName = name.replace(/\.[^.]+$/, '');

    const minBE = sortedBE.length ? sortedBE[sortedBE.length - 1].toFixed(1) : '';
    const maxBE = sortedBE.length ? sortedBE[0].toFixed(1) : '';

    const tab = {
      id, name: displayName, color, isSurvey,
      sourcePath,
      chargeVerified: true,
      rawBE: sortedBE,
      rawIntensity: sortedInten,
      ccShift: 0,
      peaks: [],
      nextId: 1,
      fitResult: null,
      markedElements: [],
      notes: '',
      lineWidth: 1.5,
      ui: {
        bgType: 'shirley', bgStart: maxBE, bgEnd: minBE,
        shirleyIter: '5', endpointAvg: NEW_TAB_ENDPOINT_AVG,
        roiMin: minBE, roiMax: maxBE,
        ccMethod: 'none', ccObs: '', ccLit: '',
      }
    };

    if (isSurvey) {
      this.tabs.unshift(tab);
    } else {
      this.tabs.push(tab);
    }

    this.activateTab(id);
    this._updateSurveyPanel();
    return tab;
  }

  createStackTab() {
    const id = 'tab_' + Math.random().toString(36).slice(2, 9);
    const tab = {
      id,
      name: '▦ Stack ' + (_nextStackNum++),
      color: '#7a7a7a',           // inert — stack tabs render no dot
      isStack: true,
      entries: [],
      _nextColorIdx: 0,
      lineWidth: 1.5,
      verticalOffset: 0,
      // Inert spectrum-tab fields kept to satisfy existing lifecycle code paths.
      isSurvey: false, chargeVerified: true,
      rawBE: [], rawIntensity: [], ccShift: 0,
      peaks: [], nextId: 1, fitResult: null,
      markedElements: [], notes: '', sourcePath: null,
      ui: { bgType: 'shirley', bgStart: '', bgEnd: '', shirleyIter: '5',
            endpointAvg: '1', roiMin: '', roiMax: '',
            ccMethod: 'none', ccObs: '', ccLit: '' },
    };
    this.tabs.push(tab);
    this.activateTab(id);
    return tab;
  }

  activateTab(id) {
    if (this.activeId === id) return;
    const tab = this._getTab(id);
    if (!tab) return;
    // Cancel any armed placement mode so a click on the new tab's chart
    // isn't consumed by a placement aimed at the previous spectrum.
    if (placeMode) togglePlaceMode(placeMode);
    // Clear stale history preview from previous tab
    if (typeof _historyPreview !== 'undefined') _historyPreview = null;
    // Save current tab's live state
    this._syncActiveToRecord();
    this.activeId = id;

    // Swap global state fields — peaks uses reference sharing
    state.rawBE = tab.rawBE;
    state.rawIntensity = tab.rawIntensity;
    state.ccShift = tab.ccShift;
    state.peaks = tab.peaks;
    state.nextId = tab.nextId;
    state.fitResult = tab.fitResult;
    state.lineWidth = tab.lineWidth ?? 1.5;

    // Restore DOM form fields
    this._restoreUI(tab.ui);
    _updateUndoButtons();   // history is per tab: buttons reflect the incoming record
    const notesEl = document.getElementById('spectrum-notes');
    if (notesEl) notesEl.value = tab.notes || '';
    this._updateCCVerifiedUI(tab.chargeVerified ?? true);
    this._updateInfoBadge(tab);
    if (typeof _recomputeAutoFitMenuState === 'function') _recomputeAutoFitMenuState();
    // Update chi-squared display for this tab's fit result
    _applyStatDisplay(state.fitResult);
    // F1: never computed over an edited model and cached under the fit's key
    // (without a stored curve _computeRFactor evaluates the CURRENT peaks)
    if (state.fitResult && state.fitResult.rFactor == null && _statsLiveState() !== 'stale') {
      state.fitResult.rFactor = _computeRFactor(state.fitResult);
    }
    _updateRFactorUI(state.fitResult ? state.fitResult.rFactor : null);
    _updateROIDisplay(state.fitResult ? state.fitResult.roiRange : null);
    // Reset Y zoom so chart auto-scales to this tab's data range
    // (prevents survey zoom from squishing narrow-region spectra)
    state._mainYMax = tab.yZoom || null;
    state._mainXMin = tab.xZoomMin ?? null;
    state._mainXMax = tab.xZoomMax ?? null;

    this.renderTabBar();
    renderPeakList();
    renderResults();
    _applyRightPanelMode(tab);
    if (typeof _refOnTabChange === 'function') _refOnTabChange();
    updatePlot();
  }

  closeTab(id) {
    const idx = this.tabs.findIndex(t => t.id === id);
    if (idx === -1) return;
    const closing = this.tabs[idx];
    const closingName = closing.name;
      el.dataset.tabId = tabId;
      el.addEventListener('dragstart', e => {
        this._dragTabId = tabId;
        el.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', tabId);
      });
      el.addEventListener('dragend', () => {
        el.classList.remove('dragging');
        this._dragTabId = null;
        bar.querySelectorAll('.sp-tab').forEach(t => t.classList.remove('drag-over-left', 'drag-over-right'));
      });
      el.addEventListener('dragover', e => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        if (this._dragTabId == null || this._dragTabId === tabId) return;
        bar.querySelectorAll('.sp-tab').forEach(t => t.classList.remove('drag-over-left', 'drag-over-right'));
        const rect = el.getBoundingClientRect();
        const mid = rect.left + rect.width / 2;
        el.classList.add(e.clientX < mid ? 'drag-over-left' : 'drag-over-right');
      });
      el.addEventListener('dragleave', () => {
        el.classList.remove('drag-over-left', 'drag-over-right');
      });
      el.addEventListener('drop', e => {
        e.preventDefault();
        bar.querySelectorAll('.sp-tab').forEach(t => t.classList.remove('drag-over-left', 'drag-over-right'));
        if (this._dragTabId == null || this._dragTabId === tabId) return;
        const fromIdx = this.tabs.findIndex(t => t.id === this._dragTabId);
        let toIdx = this.tabs.findIndex(t => t.id === tabId);
        if (fromIdx === -1 || toIdx === -1) return;
        const rect = el.getBoundingClientRect();
        const mid = rect.left + rect.width / 2;
        const [moved] = this.tabs.splice(fromIdx, 1);
        toIdx = this.tabs.findIndex(t => t.id === tabId);
        if (e.clientX < mid) this.tabs.splice(toIdx, 0, moved);
        else this.tabs.splice(toIdx + 1, 0, moved);
        this._dragTabId = null;
        this.renderTabBar();
      });

      bar.appendChild(el);
    }
    // Update scroll arrows after DOM settles
    setTimeout(_updateTabScrollArrows, 0);
  }

  // ── Survey panel ────────────────────────────────

  _updateSurveyPanel() {
    const surveys = this.tabs.filter(t => t.isSurvey && t.rawBE.length);
    const btn = document.getElementById('survey-tab-btn');
    if (!btn) return;

    if (!surveys.length) {
      btn.classList.remove('visible');
      if (btn.classList.contains('active')) {
        this._restoreFromSurvey();
        const peaksBtn = document.querySelector('.tab[onclick*="peaks"]');
        if (peaksBtn) switchTab(peaksBtn, 'peaks');
      }
      return;
    }
    btn.classList.add('visible');
  }

  /** Called when the Survey sidebar tab is activated */
  _showSurveyInMain() {
    const surveys = this.tabs.filter(t => t.isSurvey && t.rawBE.length);
    const noData = document.getElementById('survey-no-data');
    const selWrap = document.getElementById('survey-selector-wrap');
    const markersWrap = document.getElementById('survey-markers-wrap');
    if (!noData || !selWrap || !markersWrap) return;

    if (!surveys.length) {
      noData.style.display = '';
      selWrap.style.display = 'none';
      markersWrap.style.display = 'none';
      return;
    }

    noData.style.display = 'none';

    if (surveys.length === 1) {
      selWrap.style.display = 'none';
      this._activateSurvey(surveys[0].id);
2459:  renderPeakList();
2475:  renderPeakList();
3241:    this._restoreUI(tab.ui);
3264:    renderPeakList();
3312:      renderPeakList();
3483:      this._restoreUI(active.ui);
3484:      renderPeakList();
3845:  _restoreUI(ui) {
5063:  renderPeakList();
5244:  renderPeakList();
5853:    renderPeakList();
5919:  renderPeakList();
5936:  renderPeakList();
5948:  renderPeakList();
5959:  renderPeakList();
5971:  renderPeakList();
6069:  renderPeakList();
6108:function _clearDisallowedChargeRef() {
6115:function renderPeakList() {
6116:  _clearDisallowedChargeRef();
7056:  if (typeof renderPeakList === 'function') renderPeakList();
7384:  if (typeof renderPeakList === 'function') renderPeakList();
7624:  renderPeakList();
8308:  renderPeakList();
8814:  renderPeakList();
10885:  // restore below: _restoreUI refreshes the manual-anchor count label from
10897:  tabManager._restoreUI(active.ui);
10913:  renderPeakList();
12459:      tabManager._restoreUI(tgt.ui);
12460:      renderPeakList();
14404:  renderPeakList();
16419:  renderPeakList();
  return !!(tab && isC1sTab(tab));
}

function _clearDisallowedChargeRef() {
  if (_isChargeRefAllowed()) return;
  for (const p of state.peaks) {
    if (p.isChargeReference) p.isChargeReference = false;
  }
}

function renderPeakList() {
  _clearDisallowedChargeRef();
  _updateLocalModelBanner();
  const el = document.getElementById('peak-list');
  const empty = document.getElementById('peak-empty');
  // Preserve which peak cards are expanded before clearing
  const expandedIds = new Set();
  el.querySelectorAll('.peak-body.open').forEach(b => {
    const m = b.id.match(/peak-body-(\d+)/);
    if (m) expandedIds.add(Number(m[1]));
  });
  el.innerHTML = '';
  empty.style.display = state.peaks.length ? 'none' : 'block';
  const clearWrap = document.getElementById('peak-clear-wrap');
  if (clearWrap) clearWrap.style.display = state.peaks.length ? 'block' : 'none';
  document.getElementById('sb-peaks').textContent = state.peaks.length;
  _updateLockAllBtn();

  // Compute total area for percentage (using ROI data if available)
  const { be: _roiBE } = (typeof getROIData === 'function' && state.rawBE.length) ? getROIData() : { be: [] };
  const _peakAreas = {};
  let totalArea = 0;
  if (_roiBE.length) {
    for (const p of state.peaks) { const a = _peakArea(p, _roiBE); _peakAreas[p.id] = a; if (!_isUnsupported(p)) totalArea += a; }
  }

  for (const p of state.peaks) {
    const item = document.createElement('div');
    item.className = 'peak-item';
    item.id = 'peak-item-' + p.id;
    item.style.borderLeftColor = p.color;
# F >= 1.1e3 and 3 of 752 components are unsupported (F 0.95-3.9).
SUPPORT_MIN_F = 10.0


def _component_support(y_sub, fitted_sub, comp_y, weights, n_free_comp, n_free_total) -> dict[str, Any]:
    w2 = np.asarray(weights, float) ** 2
    r = np.asarray(y_sub, float) - np.asarray(fitted_sub, float)
    ok = np.isfinite(r) & np.isfinite(comp_y) & np.isfinite(w2)
    chi_with = float(np.sum(w2[ok] * r[ok] ** 2))
    chi_without = float(np.sum(w2[ok] * (r[ok] + np.asarray(comp_y, float)[ok]) ** 2))
    delta = chi_without - chi_with
    p = max(1, int(n_free_comp))
    dof = max(1, int(ok.sum()) - int(n_free_total))
    if delta <= 0:
        f = 0.0
    elif chi_with == 0:
        f = float("inf")
    else:
        f = (delta / p) / (chi_with / dof)
    return {"f": None if not np.isfinite(f) else f, "delta_chi2": delta,
            "supported": bool(delta > 0 and (chi_with == 0 or f >= SUPPORT_MIN_F))}


# ── "Is this component REQUIRED?" — the refit test ───────────────────────────
# `support` (above) holds the OTHER components at their fitted values, so it
# cannot see redundancy under overlap: a component the others could absorb if
# they were refitted still passes. The test for that is the refit itself:
# remove the component, refit the rest from their fitted values under the
# request's own bounds, and compare the fit to the data with and without it:
#     F = ((chi2_without_refit - chi2_with) / p) / (chi2_with / dof)
# p = the component's free parameters, dof = n - nvarys of the full model.
# One extra fit, so it is done only when asked for (Auto-Fit asks for its
# charge-reference anchor: an anchor that is not required must not set the
# energy reference of a whole spectrum). Same threshold as `support`.
def _component_required(fit_reduced, params_full, removed_prefixes, y_sub, weights,
                        chi2_with, n_free_comp, n_free_total) -> dict[str, Any]:
    """``fit_reduced(params)`` is the run's own fitter for the reduced model
    (the same candidate machinery and seeding the fit used, so differential
    evolution's box/refinement and the request seed apply to the refit too).
    ``removed_prefixes`` is the removed component AND everything linked to it,
    transitively. The reduced start is built in dependency order: plain
    parameters first, expressions after, so a child ordered before its parent
    in the request still resolves."""
    kept = [(name, par) for name, par in params_full.items() if not any(name.startswith(r) for r in removed_prefixes)]
    # ALL retained parameters exist before any expression is assigned, so a
    # chain of links in any request order resolves (lmfit evaluates an
    # expression when it is set).
    start = Parameters()
    for name, par in kept:
        start.add(name, value=par.value, min=par.min, max=par.max, vary=par.vary)
    for name, par in kept:
        if par.expr:
            start[name].set(expr=par.expr)
    refit = fit_reduced(start)
    chi2_without = float(refit.chisqr) if refit.chisqr is not None else float("inf")
    if not refit.success or getattr(refit, "box_unverified", False):
        # F2 (2026-09-26): a refit that did not converge establishes nothing
        # (nor does a differential-evolution candidate whose search box no
        # refinement verified — the main fit's acceptance rule rejects it too;
        # Codex round 1)
        # either way — its chi-square is wherever the optimiser stopped (a
        # redundant anchor read "required", F 992, from a refit stopped early;
        # F 1.17 once it completed). No verdict; the caller decides.
        return {"required": None, "f": None, "chi2_with": float(chi2_with), "chi2_without_refit": chi2_without,
                "refit_converged": False, "reason": "refit_not_converged",
                "message": str(getattr(refit, "message", "") or "")[:200]}
    delta = chi2_without - chi2_with
    p = max(1, int(n_free_comp))
    dof = max(1, len(y_sub) - int(n_free_total))
    # No tolerance of any kind (Codex rounds 2-3: a floor on the chi-square
    # change relative to the data's power, and then an "exactness" cutoff on
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class FittedComponent:
    slot_role: str
    position: float
    fwhm: float          # width-parameter value (m_gauss for DS+G — fitalg convention)
    amplitude: float
    shape_params: dict
    line_shape: Optional[LineShape] = None


@dataclass
class FitOutcome:
    converged: bool
    components: list[FittedComponent]
    residual_sum_sq: float
    weighted_chi_sq: float
    n_params: int
    n_data: int
    lmfit_result: Optional[ModelResult] = None
    background: Optional[np.ndarray] = None
    boundary_hits: list[str] = field(default_factory=list)


def _extract_fitted_components(
    result: ModelResult, model: CandidateModel
) -> list[FittedComponent]:
    out: list[FittedComponent] = []
    for slot in model.slots:
        prefix = _slot_prefix(slot.role)
        pars = result.params
        try:
            center = float(pars[f"{prefix}center"].value)
            amplitude = float(pars[f"{prefix}amplitude"].value)
            fwhm = float(pars[f"{prefix}{_width_param(slot.line_shape)}"].value)
        except KeyError:
            continue
        shape_params = {}
        for name, _, _, _ in _SHAPE_PARAM_DEFAULTS[slot.line_shape]:
            par = pars.get(f"{prefix}{name}")
            if par is not None:
                shape_params[name] = float(par.value)
        if slot.line_shape is LineShape.DS_G:
            shape_params["m_gauss"] = fwhm
        out.append(FittedComponent(
            slot_role=slot.role, position=center, fwhm=fwhm,
            amplitude=amplitude, shape_params=shape_params,
            line_shape=slot.line_shape,
        ))
    return out


# Shape-parameter names allowed to saturate at bounds per lineshape (shape
# preference, not pathology).  Width-like params are NOT excluded.
_BOUNDARY_EXCLUDED: dict[LineShape, frozenset[str]] = {
    LineShape.GAUSSIAN: frozenset(),
    LineShape.LORENTZIAN: frozenset(),
    LineShape.PSEUDO_VOIGT: frozenset({"gl_ratio"}),
    LineShape.ASYM_GL: frozenset({"gl_ratio", "asymmetry"}),
    LineShape.DS: frozenset({"alpha", "gamma_asym"}),
    LineShape.DS_G: frozenset({"alpha"}),          # beta is a WIDTH here — counted
    LineShape.LACX: frozenset({"alpha", "beta"}),  # both are exponents here
}


def _role_for_param(pname: str, role_by_prefix: dict[str, str]) -> Optional[str]:
    for prefix in sorted(role_by_prefix, key=len, reverse=True):
        if pname.startswith(prefix):
            return role_by_prefix[prefix]
    return None
    lo, hi = slot.linked_offset_range
    return (parent.position + lo, parent.position + hi)


def match_components_to_slots(
    components: list[FittedComponent],
    model: CandidateModel,
    noise_floor: float,
    bound_overrides: Optional[dict[str, tuple[float, float]]] = None,
) -> dict[str, Optional[FittedComponent]]:
    """Assign fitted peaks to grammar slots (role + effective window + width).

    ``bound_overrides`` (fit_full_window) — see ``_effective_be_window``.
    """
    slot_map: dict[str, Optional[FittedComponent]] = {s.role: None for s in model.slots}
    orphans: list[FittedComponent] = []
    asym_shapes = {LineShape.ASYM_GL, LineShape.DS, LineShape.DS_G, LineShape.LACX}

    def _accepts(slot: ComponentSlot, comp: FittedComponent) -> bool:
        lo, hi = _effective_be_window(slot, components,
                                      (bound_overrides or {}).get(slot.role))
        return (lo <= comp.position <= hi
                and slot.fwhm_range[0] <= comp.fwhm <= slot.fwhm_range[1]
                and comp.amplitude > noise_floor)

    def _window_center(slot: ComponentSlot) -> float:
        # NEVER the widened bound (Codex-caught, round 2): this is a
        # TIE-BREAK reference point ("how close is this component to
        # where this slot expects its peak"), not an acceptance test —
        # widening it would drag the reference point far from the
        # slot's true expected position (e.g. a curated slot's own
        # narrow window widened to a whole ROI), making a neighboring
        # slot's UNWIDENED, much-closer center win the tie-break even
        # when the component sits well inside THIS slot's own original
        # window. Acceptance (_accepts, above) is the only place the
        # widened bound belongs.
        lo, hi = _effective_be_window(slot, components)
        return 0.5 * (lo + hi)

    for comp in components:
        candidate_slots = [s for s in model.slots if _accepts(s, comp)]
        if not candidate_slots:
            orphans.append(FittedComponent(
                slot_role="unmatched", position=comp.position, fwhm=comp.fwhm,
                amplitude=comp.amplitude, shape_params=comp.shape_params,
                line_shape=comp.line_shape,
            ))
            continue

        shapes = {s.line_shape for s in candidate_slots}
        if len(shapes) > 1:
            if _is_asymmetric_component(comp):
                preferred = [s for s in candidate_slots if s.line_shape in asym_shapes]
            else:
                preferred = [s for s in candidate_slots if s.line_shape not in asym_shapes]
            if preferred:
                candidate_slots = preferred

        best_slot = min(candidate_slots, key=lambda s: abs(comp.position - _window_center(s)))
        incumbent = slot_map[best_slot.role]
        claimed = FittedComponent(
            slot_role=best_slot.role, position=comp.position, fwhm=comp.fwhm,
            amplitude=comp.amplitude, shape_params=comp.shape_params,
            line_shape=comp.line_shape,
        )
        if incumbent is None:
            slot_map[best_slot.role] = claimed
        else:
            wc = _window_center(best_slot)
            if abs(comp.position - wc) < abs(incumbent.position - wc):
                orphans.append(incumbent)
                slot_map[best_slot.role] = claimed
            else:
                orphans.append(comp)

    slot_map["__orphans__"] = orphans  # type: ignore[assignment]
    return slot_map


# ─────────────────────────────────────────────────────────────────────────────
# Stability
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SlotStability:
    role: str
    persistence: float
    position_median: Optional[float]
    position_mad: Optional[float]
    fwhm_median: Optional[float]
    fwhm_mad: Optional[float]
    amplitude_median: Optional[float]
    amplitude_mad: Optional[float] = None


@dataclass
class ModelStability:
    per_slot: dict[str, SlotStability]
    orphan_rate: float
    convergence_rate: float
    # Best converged refit found during the multi-start pass (by weighted χ²).
    # Port improvement over fitalg, which always reported the primary fit even
    # when a perturbed refit found a deeper minimum: the driver promotes this
    # outcome when it beats the primary, so the report describes the best
    # minimum FOUND and the stability numbers describe its robustness.
    best_outcome: Optional[FitOutcome] = None
    # How many multi-start fits (refits + primary) landed within
    # BASIN_SUPPORT_RTOL of the best weighted χ² — an honesty diagnostic for
    # the best-minimum promotion (Codex Stage-2 re-review finding #4: a
    # one-off deeper minimum is a different product than a reproducible one).
    # Reporting-only; never used in ranking.
    best_basin_support: int = 0
    # How many of the requested n_refits were actually attempted before the
    # candidate's wall-clock budget (CANDIDATE_TIMEOUT_SEC) ran out. Equal to
    # n_refits unless timed_out is True — used as the honest denominator for
    # persistence/orphan_rate/convergence_rate instead of silently
    # understating them against the full nominal n_refits.
    n_attempted: int = 0
    timed_out: bool = False

    @property

exec
/bin/zsh -lc "sed -n '1640,1745p' autofit/engine.py; sed -n '2479,2538p' autofit/engine.py; cat tests/autofit/test_stress_honesty.py; sed -n '1,170p' autofit/confidence.py; rg -n '\\.contains\\(|unmatched|orphans' autofit tests/autofit | head -90; ls -d venv .venv 2>/dev/null; sed -n '145,185p' CLAUDE.md" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
    # with per-feature gate outcomes and seeding decisions.  None when the
    # layer did not run (enable_preseed=False or no candidates).
    candidate_pool: Optional[dict] = None


def rank_and_filter(
    reports: list[ModelReport],
    persistence_threshold: float = DEFAULT_PERSISTENCE_THRESHOLD,
    bic_ambiguity_threshold: float = DEFAULT_BIC_AMBIGUITY,
    allow_conditional: bool = True,
    allow_last_resort: bool = False,
) -> ComparisonResult:
    """
    Filter (plausibility, active persistence) then rank (χ²ᵣ, BIC*).

    Two-tier semantics (departure from fitalg, which returned zero survivors
    whenever every candidate had any boundary hit — routine on real composite
    samples): when NO candidate passes plausibility cleanly but some are
    otherwise stable, those are ranked as a CONDITIONAL tier with
    ``result.conditional = True`` and every violation preserved.  Stability
    failures are never promoted — an unstable fit is pathology, not a
    constraint conflict.
    """
    filtered_out: list[tuple[ModelReport, str]] = []
    survivors: list[ModelReport] = []
    conditional_pool: list[ModelReport] = []

    for r in reports:
        active_min = r.active_min_persistence
        stable = active_min >= persistence_threshold
        if r.plausibility.boundary_hits or r.plausibility.unphysical_widths \
                or r.plausibility.orphan_peaks:
            # orphan_peaks included (Codex Stage-2 re-review finding #3):
            # refits repeatedly producing unmatched components is a
            # plausibility violation, not clean-survivor material.
            filtered_out.append((r, f"plausibility: {r.plausibility}"))
            if stable:
                conditional_pool.append(r)
            continue
        if not stable:
            absent_roles = [a.role for a in r.absent_slots]
            extra = f"  (absent slots excluded: {absent_roles})" if absent_roles else ""
            filtered_out.append((r, f"stability: active min persistence "
                                    f"{active_min:.2f} < {persistence_threshold}{extra}"))
            continue
        survivors.append(r)

    conditional = False
    conditional_reason = None
    if allow_conditional and conditional_pool and not survivors:
        survivors = conditional_pool
        conditional = True
        conditional_reason = "no_clean_survivor"
    elif allow_conditional and allow_last_resort and not survivors and reports:
        # LAST-RESORT tier (Stage-2, 2026-07-10; measured on real low-res
        # Fe 2p): fires ONLY when the caller says detection found real
        # structure (allow_last_resort = detection seeds exist) — its job
        # is rescuing DETECTED structure from selection instability, never
        # forcing an answer on featureless data (a flat-noise grammar fit
        # can converge; the honest result there stays no-survivor).
        # Every candidate failed BOTH tiers — typically cross-refit
        # label instability (orphan_peaks) on heavily-overlapped low-res
        # structure.  For a suggest-a-profile tool an EMPTY answer is the
        # worst answer: emit the single best CONVERGED model, loudly
        # flagged unstable.  This tier exists only when clean and
        # conditional are BOTH empty — stability failures are still never
        # preferred over anything (the original design rule stands).
        viable = [r for r in reports
                  if r.primary_fit.converged
                  and np.isfinite(r.bic_adjusted)]
        if viable:
            best = min(viable,
                       key=lambda r: (r.bic_adjusted, r.reduced_chi_sq))
            survivors = [best]
            conditional = True
            conditional_reason = "unstable_last_resort"
    # NOTE: the decisive-override path (clean survivors exist but a
    # bound-fixed refit of a conditional candidate dominates) lives in
    # compare_models — it needs the spectrum to refit; rank_and_filter is
    # pure ranking.

    # BIC* is the ranking default (spec §6); χ²ᵣ breaks ties only.  fitalg
    # ranked (χ²ᵣ, BIC*) — spec-noncompliant, changed per Codex finding #3.
    survivors.sort(key=lambda r: (r.bic_adjusted, r.reduced_chi_sq))

    ambiguous: list[tuple[str, str, str]] = []
    for i in range(len(survivors)):
        for j in range(i + 1, len(survivors)):
            a, b = survivors[i], survivors[j]
            if abs(a.bic_adjusted - b.bic_adjusted) <= bic_ambiguity_threshold \
               and a.model.n_components != b.model.n_components:
                diff = {s.role for s in a.model.slots} ^ {s.role for s in b.model.slots}
                ambiguous.append((
                    a.model.name, b.model.name,
                    f"Indistinguishable on fit quality and BIC* "
                    f"(ΔBIC*={abs(a.bic_adjusted - b.bic_adjusted):.2f}); "
                    f"structural difference: {diff}",
                ))
    return ComparisonResult(
        reports=reports, survivors=survivors,
        filtered_out=filtered_out, ambiguous_pairs=ambiguous,
        conditional=conditional, conditional_reason=conditional_reason,
        bic_ambiguity_threshold=bic_ambiguity_threshold,
    )


def _apply_decisive_override(
    x: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray,
    result: ComparisonResult,
    persistence_threshold: float,
    diagnostic_windows: dict[str, tuple[float, float]],
    noise_floor: float,
    n_refits: int,
    rng_seed: int,
    fit_full_window: bool = False,
    endpoint_avg: int = 1,
) -> ComparisonResult:
    """Dominance rule — see CONDITIONAL_OVERRIDE_DELTA_BIC block comment."""
    if result.conditional or not result.survivors:
        return result
    clean_best = result.survivors[0]
    # (4) the clean best must itself show residual-structure evidence
    if not (clean_best.residuals.autocorr_flag
            or clean_best.residuals.flagged_windows):
        return result
    pool = [r for r, why in result.filtered_out
            if why.startswith("plausibility")
            and r.active_min_persistence >= persistence_threshold]
    pool.sort(key=lambda r: r.bic_adjusted)

    for candidate in pool[:OVERRIDE_MAX_ATTEMPTS]:
        refit = _bound_fixed_refit(x, y, weights, candidate,
                                   diagnostic_windows, noise_floor,
                                   n_refits=n_refits, rng_seed=rng_seed,
                                   fit_full_window=fit_full_window,
                                   endpoint_avg=endpoint_avg)
        if refit is None:
            continue
        # the bound-fixed model must be STABLE in its own right
        if refit.active_min_persistence < persistence_threshold:
            continue
        # (2) very-strong BIC* margin AND (3) strictly better χ²ᵣ
        if not (refit.bic_adjusted + CONDITIONAL_OVERRIDE_DELTA_BIC
                < clean_best.bic_adjusted
                and refit.reduced_chi_sq < clean_best.reduced_chi_sq):
            continue
        result.reports.append(refit)
        result.survivors = [refit] + result.survivors  # clean kept as alternatives
        result.conditional = True
        result.conditional_reason = "decisive_override"
        return result
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Top-level driver — region-agnostic
# ─────────────────────────────────────────────────────────────────────────────

def _report_progress(
    progress_cb: Optional[Callable[[dict], None]],
    phase: str, idx: int, total: int, name: str,
) -> None:
    """Fire ``progress_cb`` for one candidate transition; never let a
    broken sink (e.g. a full disk on the progress-file writer) break the
"""
Always-on stress-honesty net — the KEY-CRITERION invariants from the
synthetic hard-case suite (run-brief item 2), pinned on the fast subset
(IC n_refits=4 + LS + sparse; the full battery incl. Bayesian and noise
replicates is scripts/run_stress_battery.py → stress_battery_runs.jsonl,
summarized in docs/autofit/stress-test-report.md).

Where there IS a right answer the engine must recover it; where the truth
is outside the model space the mismatch must be machine-visible; an
over-specified menu must be pruned, not populated.  Values pinned from the
2026-07-04 measurement run.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from stress_cases import (  # noqa: E402
    asym_truth_case,
    bg_matched_control_case,
    bg_mismatch_case,
    isolated_missing_peak_case,
    overlap_case,
    overspecified_case,
    overspecified_decoy_case,
)
from autofit.methods import get_method  # noqa: E402

IC_OPTS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
           "enable_proposal_pass": True}


def _ic(case):
    return get_method("ic_model_comparison").run(
        case.x, case.y, grammar=case.grammar, options=dict(IC_OPTS))


@pytest.fixture(scope="module")
def sep1():
    case = overlap_case(1.0, 9000.0, seed=11, expectation="recover")
    return case, _ic(case)


def test_resolved_doublet_recovered_clean(sep1):
    """Separation 1×FWHM at 9000 counts: distinguishable → must recover."""
    case, res = sep1
    assert res.success
    assert res.diagnostics["winner"] == "P2"
    assert res.diagnostics["conditional"] is False
    by_role = {p["role"]: p for p in res.peaks}
    for t, role in zip(case.truth, ("main_a", "main_b")):
        assert by_role[role]["center"] == pytest.approx(t["center"], abs=0.05)


def test_resolved_doublet_ls_baseline(sep1):
    case, _ = sep1
    res = get_method("least_squares").run(
        case.x, case.y, peak_specs=case.ls_specs,
        options={"background_method": "linear"})
    assert res.success
    for t, p in zip(case.truth, res.peaks):
        assert p["center"] == pytest.approx(t["center"], abs=0.05)
        assert p["fwhm"] == pytest.approx(t["fwhm"], abs=0.1)


def test_resolved_doublet_sparse_count_only():
    """Sparse COUNT-ONLY pin — explicitly NOT a recovery claim: on this
    PV-truth case the selected atoms sit 0.45-0.75 eV off (Gaussian-atom /
    30%-Lorentzian mismatch, its documented weakness; classified
    count_ok_param_biased in the battery, never PASS).  The invariant
    worth pinning is only that the component COUNT does not hallucinate on
    a clean, well-separated doublet."""
    case = overlap_case(1.0, 9000.0, seed=11, expectation="recover")
    res = get_method("sparse_map").run(case.x, case.y, grammar=case.grammar)
    assert res.success
    assert len(res.peaks) == 2


def test_overspecified_menu_prunes_not_invents():
    """Truth 2 peaks, menu offers up to 5: the winner must carry exactly
    the true structure — no invented components."""
    case = overspecified_case(seed=31)
    res = _ic(case)
    assert res.diagnostics["winner"] == "P2"
    assert len(res.peaks) == 2
    by_role = {p["role"]: p for p in res.peaks}
    matched = 0
    for t in case.truth:
        if any(abs(p["center"] - t["center"]) < 0.3 for p in by_role.values()):
            matched += 1
    assert matched == 2


def test_inroi_decoy_pruned_not_populated():
    """The harder over-specification test (Codex stress review): a decoy
    'shoulder' window BETWEEN the true peaks, where real tail intensity
    lives — the winner must carry the true 2-component structure with the
    decoy hypothesis rejected, not a populated 3-component invention.
    Measured 2026-07-04: P2 clean, χ²ᵣ 1.10, exact recovery ON THIS BASE
    DRAW.  The battery shows the prune is noise-draw-DEPENDENT (offset
    2000 promotes the bound-fixed decoy via decisive_override, k=3,
    conditional-flagged) — stress report finding 8; this pin covers the
    base draw only."""
    case = overspecified_decoy_case(seed=32)
    res = _ic(case)
    assert res.diagnostics["winner"] == "P2"
    assert len(res.peaks) == 2
    by_role = {p["role"]: p for p in res.peaks}
    for t, role in zip(case.truth, ("main_a", "main_b")):
        assert by_role[role]["center"] == pytest.approx(t["center"], abs=0.1)


def test_bg_matched_control_recovers():
    case = bg_matched_control_case(seed=62)
    res = _ic(case)
    assert res.diagnostics["winner"] == "P2"
    assert res.diagnostics["conditional"] is False
    wc = next(c for c in res.analysis["candidates"] if c["name"] == "P2")
    assert wc["reduced_chi_sq"] < 2.0


def test_bg_mismatch_surfaces_loudly():
    """Shirley-shaped truth fit with a straight line: the mismatch must be
    machine-visible (conditional tier + grossly elevated χ²ᵣ), never a
    clean confident result."""
    case = bg_mismatch_case(seed=61)
    res = _ic(case)
    assert res.diagnostics["conditional"] is True
    wc = next(c for c in res.analysis["candidates"]
              if c["name"] == res.diagnostics["winner"])
    assert wc["reduced_chi_sq"] > 10.0


def test_preseed_catches_isolated_missing_peak():
    """Unit F1 (2026-07-07): the isolated unmodeled peak (28% of the main —
    above the preseed dominance gate) is now caught by the PRE-FIT seeding
    channel: same honesty contract as the proposal pass (region-unassigned
    component, human adjudication), reached before the fit so the landscape
    is sane.  The peak must be seeded, fitted at the true position, and
    surfaced in analysis.preseeded_features."""
    case = isolated_missing_peak_case(seed=71)
    res = _ic(case)
    assert res.diagnostics["winner"].endswith("+preseed")
    feats = res.analysis["preseeded_features"]
    assert len(feats) == 1
    assert feats[0]["center_be"] == pytest.approx(201.5, abs=0.3)
    seeded = [p for p in res.peaks if p["role"].startswith("preseed_dominant")]
    assert len(seeded) == 1
    assert seeded[0]["center"] == pytest.approx(201.5, abs=0.3)
    assert seeded[0]["region"] == "unassigned"
    assert "human review" in res.message


def test_proposal_pass_fires_on_isolated_missing_peak():
    """The residual-guided proposal pass's designed regime (3d): with the
    preseed channel disabled, a discrete isolated real peak the menu
    doesn't model must still be proposed, accepted, and fitted at the true
    position (measured on every noise draw; 0 false positives across the
    battery's 66 covered rows)."""
    case = isolated_missing_peak_case(seed=71)
    res = get_method("ic_model_comparison").run(
        case.x, case.y, grammar=case.grammar,
        options={**IC_OPTS, "enable_preseed": False})
    assert res.diagnostics["winner"].endswith("+prop")
    accepted = [p for c in res.analysis["candidates"]
                for p in c.get("proposed_peaks", []) if p["accepted"]]
    assert len(accepted) == 1
    assert accepted[0]["fitted_center"] == pytest.approx(201.5, abs=0.3)


def test_asym_truth_recovered_when_expressible():
    case = asym_truth_case(seed=52, with_asym_candidate=True)
    res = _ic(case)
    assert res.diagnostics["winner"] == "asym_main"


def test_asym_truth_symmetric_only_flags_mismatch():
    """DS truth, symmetric-only menu: the model-space gap must be machine-
    visible — residual autocorrelation flag + elevated χ²ᵣ on the winner."""
    case = asym_truth_case(seed=51, with_asym_candidate=False)
    res = _ic(case)
    wc = next(c for c in res.analysis["candidates"]
              if c["name"] == res.diagnostics["winner"])
    assert wc["autocorr_flag"] is True
    assert wc["reduced_chi_sq"] > 3.0


def test_subfwhm_dominant_alternative_never_silently_lost():
    """INVARIANT (not a pin of the current deficient winner — Codex stress
    review): on the high-count sub-FWHM doublet the EVIDENCE decisively
    favors P2 (ΔBIC* 74-97 on every noise draw; stress report finding 0).
    Whatever the pipeline emits, the dominant evidence must never be
    silently lost:
    - if the engine picks P2 (a future fix), its centers must be sane; or
    - if it picks anything else, the dominant P2 record must remain fully
      machine-readable (fit quality, BIC* dominance, explicit non-survival
      reason) OR the result must carry an ambiguity/conditional signal."""
    case = overlap_case(0.4, 9000.0, seed=13, expectation="recover")
    res = _ic(case)
    winner = res.diagnostics["winner"]
    cands = {c["name"]: c for c in res.analysis["candidates"]}
    if winner.startswith("P2"):
        by_role = {p["role"]: p for p in res.peaks}
        assert len(by_role) == 2
    else:
        p2, w = cands["P2"], cands[winner]
        dominated = p2["bic_star"] < w["bic_star"] - 10
        # the engine now carries the RESULT-LEVEL burial flag (change
        # driven by stress finding 0) — when the dominant alternative is
        # filtered, the flag must name it
        result_flagged = (res.diagnostics.get("conditional")
                          or res.analysis.get("ambiguous_pairs")
                          or res.diagnostics.get(
                              "filtered_dominant_alternative"))
        assert (not dominated) or result_flagged, (
            "dominant alternative buried without any RESULT-level signal")
        if dominated and res.diagnostics.get("filtered_dominant_alternative"):
            assert (res.diagnostics["filtered_dominant_alternative"]["name"]
                    == "P2")
"""
Per-peak, per-parameter confidence vectors (spec v2.1 §5).

Rules encoded:

- **Typed statistical σ** — ``uncertainty_kind ∈ {covariance, stability_mad,
  unavailable}``; kinds are NEVER mixed in one numeric field.  ``covariance``
  = lmfit stderr; ``stability_mad`` = raw median-absolute-deviations from
  the perturbation refits (reported as MADs, not silently rescaled to σ);
  ``unavailable`` otherwise.
- **Stability/persistence** — refit survival fraction + parameter MADs.
- **Detectability** — amplitude vs the noise floor; the ``5×`` floor is a
  TUNABLE validation parameter (UNVERIFIED), not a constant.
- **Identifiability** — boundary hits + max parameter correlation.
- ``reference_sensitivity_range`` is a SEPARATE field (never combined with
  σ_stat, no quadrature).  A single-spectrum fit cannot populate it — it
  needs the corrected-BE spread across admissible references for the phase —
  so it is ``None`` here with an explanatory kind, filled by the (later)
  charge-reference machinery.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from .engine import ModelReport, _slot_prefix, _width_param

# UNVERIFIED tunable (spec §9): detection floor as a multiple of the noise
# estimate. Calibrate on the labeled set; do not treat as physics.
DETECTION_FLOOR_MULTIPLE = 5.0


def _sigma_stat_for_slot(report: ModelReport, role: str) -> dict:
    """σ_stat for center/width/amplitude with an explicit kind."""
    result = report.primary_fit.lmfit_result
    slot = report.model.slot_by_role(role)
    wname = _width_param(slot.line_shape) if slot is not None else "fwhm"
    prefix = _slot_prefix(role)

    if result is not None:
        stderr = {}
        for short, pname in (("center", f"{prefix}center"),
                             ("fwhm", f"{prefix}{wname}"),
                             ("amplitude", f"{prefix}amplitude")):
            par = result.params.get(pname)
            stderr[short] = (float(par.stderr)
                             if par is not None and par.stderr is not None else None)
        if any(v is not None for v in stderr.values()):
            return {"uncertainty_kind": "covariance", "values": stderr}

    sstab = report.stability.per_slot.get(role)
    if sstab is not None and sstab.position_mad is not None:
        return {
            "uncertainty_kind": "stability_mad",
            # raw MADs from the perturbation refits — NOT rescaled to a
            # Gaussian σ; consumers must not compare across kinds.
            "values": {"center": sstab.position_mad,
                       "fwhm": sstab.fwhm_mad,
                       "amplitude": sstab.amplitude_mad},
        }
    return {"uncertainty_kind": "unavailable", "values": None}


def _max_correlation(report: ModelReport, role: str) -> Optional[float]:
    """Max |correlation| between this slot's varying params and any other."""
    result = report.primary_fit.lmfit_result
    if result is None or result.covar is None:
        return None
    var_names = list(result.var_names)
    covar = np.asarray(result.covar, dtype=float)
    d = np.sqrt(np.diag(covar))
    with np.errstate(invalid="ignore", divide="ignore"):
        corr = covar / np.outer(d, d)
    prefix = _slot_prefix(role)
    idx = [i for i, n in enumerate(var_names) if n.startswith(prefix)]
    others = [i for i in range(len(var_names)) if i not in idx]
    if not idx or not others:
        return None
    sub = np.abs(corr[np.ix_(idx, others)])
    sub = sub[np.isfinite(sub)]
    return float(np.max(sub)) if sub.size else None


def build_confidence_vector(
    report: ModelReport,
    role: str,
    noise_floor: float,
    detection_floor_multiple: float = DETECTION_FLOOR_MULTIPLE,
) -> dict:
    """The per-peak `_confidence` payload for one grammar slot."""
    sstab = report.stability.per_slot.get(role)
    comp = next((c for c in report.primary_fit.components if c.slot_role == role), None)
    boundary = [h for h in report.primary_fit.boundary_hits
                if h.startswith(f"{role}:")]

    amplitude = float(comp.amplitude) if comp is not None else None
    floor = detection_floor_multiple * noise_floor
    if amplitude is None:
        detect_status = "not_fitted"
    elif amplitude >= floor:
        detect_status = "above_floor"
    elif amplitude > noise_floor:
        detect_status = "present_but_poorly_constrained"
    else:
        detect_status = "not_confidently_detected"

    return {
        "sigma_stat": _sigma_stat_for_slot(report, role),
        # Systematic reference envelope — SEPARATE from σ_stat by design
        # (spec §4 M2: no quadrature). Not derivable from a single fit.
        "reference_sensitivity_range": {
            "kind": "unavailable_single_fit",
            "range_ev": None,
        },
        "stability": None if sstab is None else {
            "persistence": sstab.persistence,
            "position_mad": sstab.position_mad,
            "fwhm_mad": sstab.fwhm_mad,
            "amplitude_mad": sstab.amplitude_mad,
        },
        "detectability": {
            "amplitude": amplitude,
            "noise_floor": noise_floor,
            "floor_multiple": detection_floor_multiple,
            "floor_multiple_is_tunable": True,
            "status": detect_status,
        },
        "identifiability": {
            "boundary_hits": boundary,
            "max_cross_correlation": _max_correlation(report, role),
        },
    }
autofit/engine.py:1050:    orphans: list[FittedComponent] = []
autofit/engine.py:1077:            orphans.append(FittedComponent(
autofit/engine.py:1078:                slot_role="unmatched", position=comp.position, fwhm=comp.fwhm,
autofit/engine.py:1105:                orphans.append(incumbent)
autofit/engine.py:1108:                orphans.append(comp)
autofit/engine.py:1110:    slot_map["__orphans__"] = orphans  # type: ignore[assignment]
autofit/engine.py:1189:    n_with_orphans = 0
autofit/engine.py:1236:        if slot_map.pop("__orphans__", []):
autofit/engine.py:1237:            n_with_orphans += 1
autofit/engine.py:1270:        orphan_rate=n_with_orphans / max(n_attempted, 1),
autofit/engine.py:1673:            # refits repeatedly producing unmatched components is a
on all 108 committed LA components, pinned across the α/β/m box on seven
grids incl. grids shorter than the kernel
(`docs/superpowers/plans/2026-09-25-cam-continuous.md`). DS+G was the other gap until 2026-09-22 (the page's quadrature
`laCasaXPS` sized its step to the Lorentzian core, not the Gaussian kernel,
and was wrong by up to 1e52 × amplitude at β = 2, m = 0.05 and 5–21 % low
in area on the very box Find Peaks emits for a graphitic C 1s line);
`dsgConvolved_array` now mirrors the server's padded-grid convolution for
every m — the same FFT circular convolution — pinned at 1e-6 across the
full β/m box on eight grids, irregular grids and centres outside the
window (`docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md`). Two
server limits found there: a DS+G m just above the 0.001 delta threshold
on a coarse grid (m ≤ 0.003 at 0.1 eV, even padded length) underflows the
kernel and returns an all-zero curve — left as is, it reads as a
zero-amplitude component and step (b) flags it; and a centre OUTSIDE the
padded grid was normalised by rounding noise — fixed 2026-09-25 by a NEW
GUARDED BRANCH (normalise by the maximum), proven byte-identical for every
in-range centre against main's function (`scripts/dsg_outside_centre_identity.py`). Details of
A03 in `docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`.

---

## Design Rules

### Thresholds on data-scaled quantities fail

XPS spans many orders of magnitude within one spectrum, so any absolute
floor, delta or exactness cutoff will misjudge at some dynamic range. Two
units learned this independently — five intensity floors on the Auto-Fit
anchor (answer: a scale-free F test), then two tolerances on that F test
(answer: none). Prefer a scale-free comparison with no tolerance. If a
check seems to need a magnitude threshold, that is evidence the check is
formulated wrong.

(Owner, 2026-09-22. The record: the anchor unit's six Codex rounds in
`docs/autofit/codex/autofit_zero_graphite_*`, the DE unit's tolerance rounds
5–8 in `de_finite_bounds_*`, and the required-refit unit's rounds 2–3 in
`autofit_required_*`. The DE unit is the same rule seen from the other
side: every χ² comparison tolerance produced reachable false failures and
no reachable protection, and the fix was to delete the comparison.)

### Two readings of one field

exec
/bin/zsh -lc "command -v python python3 pytest; ls -d /Users/skyefortier/xps-app/venv /Users/skyefortier/xps-app/.venv 2>/dev/null; sed -n '1645,1728p' autofit/engine.py; sed -n '2479,2528p' autofit/engine.py; sed -n '3840,3895p' templates/index.html; sed -n '6735,6805p' templates/index.html; rg -n 'renderPeakList|_recomputeAutoFitMenuState' templates/index.html | tail -25; rg -n 'weights=|sigma =' autofit/engine.py | head -30; rg -n 'def bg_mismatch_case' tests/autofit/stress_cases.py; rg -n 'detectability|floor_multiple|support_f' templates/index.html autofit tests/autofit/test_methods_seam.py tests/autofit/test_schema_roundtrip.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 exited 2 in 0ms:
/usr/bin/python3
/Users/skyefortier/xps-app/venv
def rank_and_filter(
    reports: list[ModelReport],
    persistence_threshold: float = DEFAULT_PERSISTENCE_THRESHOLD,
    bic_ambiguity_threshold: float = DEFAULT_BIC_AMBIGUITY,
    allow_conditional: bool = True,
    allow_last_resort: bool = False,
) -> ComparisonResult:
    """
    Filter (plausibility, active persistence) then rank (χ²ᵣ, BIC*).

    Two-tier semantics (departure from fitalg, which returned zero survivors
    whenever every candidate had any boundary hit — routine on real composite
    samples): when NO candidate passes plausibility cleanly but some are
    otherwise stable, those are ranked as a CONDITIONAL tier with
    ``result.conditional = True`` and every violation preserved.  Stability
    failures are never promoted — an unstable fit is pathology, not a
    constraint conflict.
    """
    filtered_out: list[tuple[ModelReport, str]] = []
    survivors: list[ModelReport] = []
    conditional_pool: list[ModelReport] = []

    for r in reports:
        active_min = r.active_min_persistence
        stable = active_min >= persistence_threshold
        if r.plausibility.boundary_hits or r.plausibility.unphysical_widths \
                or r.plausibility.orphan_peaks:
            # orphan_peaks included (Codex Stage-2 re-review finding #3):
            # refits repeatedly producing unmatched components is a
            # plausibility violation, not clean-survivor material.
            filtered_out.append((r, f"plausibility: {r.plausibility}"))
            if stable:
                conditional_pool.append(r)
            continue
        if not stable:
            absent_roles = [a.role for a in r.absent_slots]
            extra = f"  (absent slots excluded: {absent_roles})" if absent_roles else ""
            filtered_out.append((r, f"stability: active min persistence "
                                    f"{active_min:.2f} < {persistence_threshold}{extra}"))
            continue
        survivors.append(r)

    conditional = False
    conditional_reason = None
    if allow_conditional and conditional_pool and not survivors:
        survivors = conditional_pool
        conditional = True
        conditional_reason = "no_clean_survivor"
    elif allow_conditional and allow_last_resort and not survivors and reports:
        # LAST-RESORT tier (Stage-2, 2026-07-10; measured on real low-res
        # Fe 2p): fires ONLY when the caller says detection found real
        # structure (allow_last_resort = detection seeds exist) — its job
        # is rescuing DETECTED structure from selection instability, never
        # forcing an answer on featureless data (a flat-noise grammar fit
        # can converge; the honest result there stays no-survivor).
        # Every candidate failed BOTH tiers — typically cross-refit
        # label instability (orphan_peaks) on heavily-overlapped low-res
        # structure.  For a suggest-a-profile tool an EMPTY answer is the
        # worst answer: emit the single best CONVERGED model, loudly
        # flagged unstable.  This tier exists only when clean and
        # conditional are BOTH empty — stability failures are still never
        # preferred over anything (the original design rule stands).
        viable = [r for r in reports
                  if r.primary_fit.converged
                  and np.isfinite(r.bic_adjusted)]
        if viable:
            best = min(viable,
                       key=lambda r: (r.bic_adjusted, r.reduced_chi_sq))
            survivors = [best]
            conditional = True
            conditional_reason = "unstable_last_resort"
    # NOTE: the decisive-override path (clean survivors exist but a
    # bound-fixed refit of a conditional candidate dominates) lives in
    # compare_models — it needs the spectrum to refit; rank_and_filter is
    # pure ranking.

    # BIC* is the ranking default (spec §6); χ²ᵣ breaks ties only.  fitalg
    # ranked (χ²ᵣ, BIC*) — spec-noncompliant, changed per Codex finding #3.
    survivors.sort(key=lambda r: (r.bic_adjusted, r.reduced_chi_sq))

    ambiguous: list[tuple[str, str, str]] = []
    for i in range(len(survivors)):
        for j in range(i + 1, len(survivors)):
            a, b = survivors[i], survivors[j]
def _apply_decisive_override(
    x: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray,
    result: ComparisonResult,
    persistence_threshold: float,
    diagnostic_windows: dict[str, tuple[float, float]],
    noise_floor: float,
    n_refits: int,
    rng_seed: int,
    fit_full_window: bool = False,
    endpoint_avg: int = 1,
) -> ComparisonResult:
    """Dominance rule — see CONDITIONAL_OVERRIDE_DELTA_BIC block comment."""
    if result.conditional or not result.survivors:
        return result
    clean_best = result.survivors[0]
    # (4) the clean best must itself show residual-structure evidence
    if not (clean_best.residuals.autocorr_flag
            or clean_best.residuals.flagged_windows):
        return result
    pool = [r for r, why in result.filtered_out
            if why.startswith("plausibility")
            and r.active_min_persistence >= persistence_threshold]
    pool.sort(key=lambda r: r.bic_adjusted)

    for candidate in pool[:OVERRIDE_MAX_ATTEMPTS]:
        refit = _bound_fixed_refit(x, y, weights, candidate,
                                   diagnostic_windows, noise_floor,
                                   n_refits=n_refits, rng_seed=rng_seed,
                                   fit_full_window=fit_full_window,
                                   endpoint_avg=endpoint_avg)
        if refit is None:
            continue
        # the bound-fixed model must be STABLE in its own right
        if refit.active_min_persistence < persistence_threshold:
            continue
        # (2) very-strong BIC* margin AND (3) strictly better χ²ᵣ
        if not (refit.bic_adjusted + CONDITIONAL_OVERRIDE_DELTA_BIC
                < clean_best.bic_adjusted
                and refit.reduced_chi_sq < clean_best.reduced_chi_sq):
            continue
        result.reports.append(refit)
        result.survivors = [refit] + result.survivors  # clean kept as alternatives
        result.conditional = True
        result.conditional_reason = "decisive_override"
        return result
    return result


      ccLit:       document.getElementById('cc-lit')?.value || '',
      bgSubtractedView: !!document.getElementById('bg-sub-toggle')?.checked,
    };
  }

  _restoreUI(ui) {
    const set = (id, val) => {
      const el = document.getElementById(id);
      if (el && val !== undefined) el.value = val;
    };
    set('bg-type', ui.bgType);
    _syncLegacyBgOption();
    set('bg-start', ui.bgStart);
    set('bg-end', ui.bgEnd);
    set('shirley-iter', ui.shirleyIter);
    set('bg-endpoint-avg', ui.endpointAvg || LEGACY_ENDPOINT_AVG);
    set('roi-min', ui.roiMin);
    set('roi-max', ui.roiMax);
    set('cc-method', ui.ccMethod);
    set('cc-obs', ui.ccObs);
    set('cc-lit', ui.ccLit);
    // Update cc field visibility without dispatching change event
    // (which would overwrite state.ccShift and trigger a double updatePlot)
    const refField = document.getElementById('cc-ref-field');
    const targetField = document.getElementById('cc-target-field');
    if (refField) refField.style.display = (ui.ccMethod === 'none') ? 'none' : 'block';
    if (targetField) targetField.style.display = (ui.ccMethod === 'custom') ? 'block' : 'none';
    // Update shift display from the already-restored state.ccShift
    const shift = -state.ccShift;
    document.getElementById('cc-shift-display').textContent = (shift >= 0 ? '+' : '') + shift.toFixed(3) + ' eV';
    // Update manual bg controls and Shirley iteration state for restored bg type
    if (typeof _onBgTypeChange === 'function') {
      const mc = document.getElementById('manual-bg-controls');
      if (mc) mc.style.display = ui.bgType === 'manual' ? 'block' : 'none';
      const needsIter = (ui.bgType === 'shirley' || ui.bgType === 'smart' || ui.bgType === 'smart_exp' || ui.bgType === 'shirley_linear');
      const si = document.getElementById('shirley-iter');
      if (si) {
        si.disabled = !needsIter;
        si.style.opacity = needsIter ? '1' : '0.4';
      }
      // Endpoint averaging also applies to Tougaard (it sets the high-BE
      // amplitude anchor), not just the Shirley iteration family.
      const needsEpAvg = needsIter || ui.bgType === 'tougaard';
      const epAvg = document.getElementById('bg-endpoint-avg');
      if (epAvg) {
        epAvg.disabled = !needsEpAvg;
        epAvg.style.opacity = needsEpAvg ? '1' : '0.4';
      }
      if (typeof _updateManualAnchorCount === 'function') _updateManualAnchorCount();
    }
    // Bkgrd Sub: restore checked state, sync visual class, refresh enable,
    // and re-gate the dependent overlay controls so they reflect the
    // restored sub-view state.
    const bgSubToggle = document.getElementById('bg-sub-toggle');
    const bgSubPill = document.getElementById('bg-sub-pill');
    if (bgSubToggle && bgSubPill) {
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

// Returns true if the tab is a C1s spectrum, defined by ROI midpoint
// in [270.0, 315.0] eV. Uses the tab's persisted UI ROI fields (which
// are corrected-BE values), falling back to the current rawBE range.
// Reads from a tab record, not state, so it works for inactive tabs.
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

// Decide how many low-BE peaks (0, 1, or 2) the auto-fit model should include.
//   rawBE             : array of raw BE values
//   bgSubInten        : background-subtracted intensity (same length)
//   provisionalShift  : state.ccShift to apply mentally — does NOT mutate state.
//                       App convention: corrected = raw − shift.
// Returns:
//   { count: 0|1|2, locations: number[] of corrected-BE local-max centers,
//     ratio: number, graphiteHeight: number }
function assessLowBERegion(rawBE, bgSubInten, provisionalShift) {
  const n = rawBE.length;
  // 1. Graphite height: closest-corrected-to-284.5 sample
  let gIdx = 0;
  let gDist = Infinity;
  for (let i = 0; i < n; i++) {
    const corr = rawBE[i] - provisionalShift;
5062:  // stale isChargeReference flags are cleared by renderPeakList).
5063:  renderPeakList();
5070:  // already works around). renderPeakList/_refOnTabChange only refresh panel/legend
5244:  renderPeakList();
5853:    renderPeakList();
5919:  renderPeakList();
5936:  renderPeakList();
5948:  renderPeakList();
5959:  renderPeakList();
5971:  renderPeakList();
6069:  renderPeakList();
6115:function renderPeakList() {
6712:function _recomputeAutoFitMenuState() {
6732:  if (typeof _recomputeAutoFitMenuState === 'function') _recomputeAutoFitMenuState();
7056:  if (typeof renderPeakList === 'function') renderPeakList();
7238:  // area % over the components the CURRENT verdicts support (as renderPeakList computes it)
7384:  if (typeof renderPeakList === 'function') renderPeakList();
7624:  renderPeakList();
8308:  renderPeakList();
8814:  renderPeakList();
8943:  // grid, exactly as renderPeakList already does for its area/percentage column.
10913:  renderPeakList();
12460:      renderPeakList();
14404:  renderPeakList();
16419:  renderPeakList();
889:        result = composite.fit(y_sub, params, x=x, weights=weights,
906:                                  weights=weights, method="leastsq",
1411:    sigma = np.sqrt(np.maximum(y, noise_floor))
1856:        local_sigma = float(np.median(np.sqrt(np.maximum(y_asc[mask], noise_floor)))) \
2014:    sigma = np.sqrt(np.maximum(y, noise_floor))
2240:    local_sigma = float(np.median(np.sqrt(np.maximum(y[mask], noise_floor)))) \
2903:                        x=x, y=y, weights=weights, base_report=current, spec=spec,
404:def bg_mismatch_case(seed: int) -> StressCase:
rg: tests/autofit/test_schema_roundtrip.py: No such file or directory (os error 2)
tests/autofit/test_methods_seam.py:104:    assert conf["detectability"]["status"] == "above_floor"
autofit/confidence.py:90:    detection_floor_multiple: float = DETECTION_FLOOR_MULTIPLE,
autofit/confidence.py:99:    floor = detection_floor_multiple * noise_floor
autofit/confidence.py:123:        "detectability": {
autofit/confidence.py:126:            "floor_multiple": detection_floor_multiple,
autofit/confidence.py:127:            "floor_multiple_is_tunable": True,

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import numpy, lmfit, pytest; print(\"Scientific test environment available\")'; sed -n '404,454p' tests/autofit/stress_cases.py; sed -n '1520,1590p' autofit/engine.py; sed -n '1200,1275p' autofit/engine.py; rg -n 'def .*absent|absent_slots|primary.*amplitude|amplitude.*floor' autofit/engine.py | head -35; rg --files tests/js | head -40" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 1155ms:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
    from .confidence import conf_interval, conf_interval2d
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
    from .minimizer import MinimizerException
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
    from .parameter import Parameter, Parameters
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
    from .jsonutils import decode4js, encode4js
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
    import dill
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
    from .session import (
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                               ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
    return _os.fsdecode(_gettempdir())
                        ^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
    tempdir = _get_default_tempdir()
              ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free']
def bg_mismatch_case(seed: int) -> StressCase:
    x = _grid()
    truth = [{"center": 197.2, "fwhm": 1.2, "height": 9000.0},
             {"center": 198.9, "fwhm": 1.2, "height": 6300.0}]
    sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
    y = _noisy(sig + _shirley_like_bg(x, sig), seed)
    return StressCase(
        name="bg_shirley_truth_linear_fit",
        regime="bg_mismatch", expectation="honesty",
        x=x, y=y, truth=truth, truth_n=2,
        grammar=_grammar(_n_peak_ladder(197.2, 198.9, n_max=3)),  # LINEAR bg
        ls_specs=_ls_specs(truth),
        true_candidates=("P2",),
        bg="shirley_like",
        notes="integral background fit with a straight line — the mismatch "
              "must surface, not silently vanish",
    )


def bg_matched_control_case(seed: int) -> StressCase:
    """Control for the mismatch case: same truth, Shirley-candidate fits.
    The engine's iterative Shirley should absorb the integral background."""
    x = _grid()
    truth = [{"center": 197.2, "fwhm": 1.2, "height": 9000.0},
             {"center": 198.9, "fwhm": 1.2, "height": 6300.0}]
    sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
    y = _noisy(sig + _shirley_like_bg(x, sig), seed)
    cands = _n_peak_ladder(197.2, 198.9, n_max=3, bg=BackgroundType.SHIRLEY)
    return StressCase(
        name="bg_shirley_truth_shirley_fit",
        regime="bg_mismatch", expectation="recover",
        x=x, y=y, truth=truth, truth_n=2,
        grammar=_grammar(cands),
        ls_specs=_ls_specs(truth),
        true_candidates=("P2",),
        bg="shirley_like",
        notes="control: matched background family",
    )


# ─────────────────────────────────────────────────────────────────────────────
# The roster
# ─────────────────────────────────────────────────────────────────────────────

def build_all_cases(seed_offset: int = 0) -> list[StressCase]:
    """The full battery roster (seeds fixed; deterministic).  A nonzero
    ``seed_offset`` regenerates the SAME truths under fresh noise draws —
    conclusion-stability replicates for the battery."""
    o = seed_offset
    return [
        # heavy overlap — resolvable at wide separation/high counts,
        counterparts REPORTED beside it: see bic_raw / bic_weighted)."""
        n = self.primary_fit.n_data
        rss = self.primary_fit.residual_sum_sq
        if n <= 0 or rss <= 0:
            return float("inf")
        return n * np.log(rss / n) + self.adjusted_n_params * np.log(n)

    @property
    def bic_raw(self) -> float:
        """Full-k, no absent-slot adjustment — reported beside the labeled
        heuristic so the adjustment can never silently decide alone
        (BIC/IC math review: 'large-model RSS with small-model penalty')."""
        return compute_bic(self.primary_fit)

    @property
    def bic_weighted(self) -> float:
        """Known-σ (weighted-χ²) FULL-k BIC: χ²_w + k·ln n with k = the
        actual free-parameter count (NO absent-slot adjustment — the
        adjustment is the labeled heuristic on BIC*; letting it into the
        companion criterion would let the heuristic shape the
        weighted-vs-RSS disagreement it exists to expose).  This is the
        criterion CONSISTENT with the Poisson-weighted fits; the ranking
        still uses BIC*, and weighted_ic_disagreement fires when the two
        criteria pick different survivors."""
        n = self.primary_fit.n_data
        chi = self.primary_fit.weighted_chi_sq
        if n <= 0 or not np.isfinite(chi):
            return float("inf")
        return chi + self.primary_fit.n_params * np.log(n)

    @property
    def n_eff_lag1(self) -> Optional[float]:
        """Effective sample size from the lag-1 autocorrelation of the
        weighted residuals: n·(1−ρ)/(1+ρ).  Oversampled/correlated spectra
        make the raw n in k·ln(n) (and the ΔBIC thresholds) overconfident
        — reported so consumers can see how far the independence
        assumption is stretched (BIC/IC math review)."""
        lm = self.primary_fit.lmfit_result
        if lm is None or getattr(lm, "residual", None) is None:
            return None
        r = np.asarray(lm.residual, dtype=float)
        if len(r) < 8 or float(np.std(r)) == 0.0:
            return None
        r = r - r.mean()
        rho = float(np.sum(r[:-1] * r[1:]) / np.sum(r * r))
        rho = min(max(rho, -0.99), 0.99)
        return float(len(r) * (1.0 - rho) / (1.0 + rho))

    @property
    def active_min_persistence(self) -> float:
        absent_roles = {a.role for a in self.absent_slots}
        active = [s for s in self.stability.per_slot.values() if s.role not in absent_roles]
        if not active:
            return 0.0
        return min(s.persistence for s in active)


def compute_bic(fit: FitOutcome) -> float:
    """fitalg likelihood convention: BIC = n·ln(RSS/n) + k·ln(n)."""
    n, rss = fit.n_data, fit.residual_sum_sq
    if n <= 0 or rss <= 0:
        return float("inf")
    return n * np.log(rss / n) + fit.n_params * np.log(n)


@dataclass
class ComparisonResult:
    reports: list[ModelReport]
    survivors: list[ModelReport]
    filtered_out: list[tuple[ModelReport, str]]
    ambiguous_pairs: list[tuple[str, str, str]]
    bg = primary_fit.background
    y_net = y - bg if bg is not None else None

    best_outcome: Optional[FitOutcome] = None
    refit_chis: list[float] = [float(primary_fit.weighted_chi_sq)]
    n_attempted = 0
    timed_out = False
    for _ in range(n_refits):
        if deadline is not None and time.perf_counter() >= deadline:
            timed_out = True
            log.warning(
                "run_stability_analysis: candidate %s hit its %.0fs budget "
                "after %d/%d refits — remaining refits skipped",
                model.name, CANDIDATE_TIMEOUT_SEC, n_attempted, n_refits,
            )
            break
        n_attempted += 1
        seed = int(rng.integers(0, 2**31 - 1))
        init = perturb_initial_params(model, seed=seed, x=x, y_net=y_net,
                                      fit_full_window=fit_full_window)
        if fixed_param_values:
            # bound-fixed refit stability: the constrained parameters stay
            # fixed at their bounds in every multi-start refit
            for pname, val in fixed_param_values.items():
                if pname in init:
                    init[pname].set(value=float(val), vary=False)
        outcome = fit_candidate(x, y, weights, model, initial_params=init,
                                endpoint_avg=endpoint_avg)
        if not outcome.converged:
            continue
        n_converged += 1
        refit_chis.append(float(outcome.weighted_chi_sq))
        if best_outcome is None or outcome.weighted_chi_sq < best_outcome.weighted_chi_sq:
            best_outcome = outcome
        slot_map = match_components_to_slots(outcome.components, model, noise_floor,
                                            bound_overrides=bound_overrides)
        if slot_map.pop("__orphans__", []):
            n_with_orphans += 1
        for role, comp in slot_map.items():
            if comp is None:
                continue
            occupied[role] += 1
            pos[role].append(comp.position)
            fw[role].append(comp.fwhm)
            am[role].append(comp.amplitude)

    def _med(v):  # median or None
        return float(np.median(v)) if v else None

    def _mad(v):
        if not v:
            return None
        arr = np.asarray(v)
        return float(np.median(np.abs(arr - np.median(arr))))

    per_slot = {
        role: SlotStability(
            role=role,
            persistence=occupied[role] / max(n_attempted, 1),
            position_median=_med(pos[role]), position_mad=_mad(pos[role]),
            fwhm_median=_med(fw[role]), fwhm_mad=_mad(fw[role]),
            amplitude_median=_med(am[role]), amplitude_mad=_mad(am[role]),
        )
        for role in occupied
    }
    best_chi = min(refit_chis)
    basin_support = sum(1 for c in refit_chis
                        if c <= best_chi * (1.0 + BASIN_SUPPORT_RTOL))
    return ModelStability(
        per_slot=per_slot,
        orphan_rate=n_with_orphans / max(n_attempted, 1),
        convergence_rate=n_converged / max(n_attempted, 1),
        best_outcome=best_outcome,
        best_basin_support=basin_support,
        n_attempted=n_attempted,
        timed_out=timed_out,
1058:                and comp.amplitude > noise_floor)
1330:def _identify_absent_slots(
1497:    absent_slots: list[AbsentSlotReport] = field(default_factory=list)
1513:        removed = sum(a.removed_n_params for a in self.absent_slots)
1570:        absent_roles = {a.role for a in self.absent_slots}
1680:            absent_roles = [a.role for a in r.absent_slots]
2232:    if comp.amplitude <= noise_floor:
2233:        return _fast(f"amplitude {comp.amplitude:.1f} ≤ noise_floor {noise_floor:.1f}")
2314:    absent = _identify_absent_slots(
2327:        absent_slots=absent, augmented_from=base_model.name,
2469:        absent_slots=[],                      # conservative full-k BIC*
2842:        absent = _identify_absent_slots(
2855:            absent_slots=absent,
tests/js/batch_propagation.test.js
tests/js/fit_acceptance.test.js
tests/js/local_lm_descent.test.js
tests/js/fp_material_mixed.test.js
tests/js/bg_window_indices.test.js
tests/js/local_lm_server_parity_backend.py
tests/js/find_peaks_periodic_table.test.js
tests/js/shape_switch_roundtrip.test.js
tests/js/unsupported_components.test.js
tests/js/find_peaks_progress.test.js
tests/js/fixtures/autofit_anchor.json
tests/js/find_peaks_coverage.test.js
tests/js/lib/acorn.LICENSE
tests/js/lib/acorn.js
tests/js/lib/module_state_scan.js
tests/js/ref_core.test.js
tests/js/endpoint_avg_default.test.js
tests/js/tougaard_twin.test.js
tests/js/stale_statistics.test.js
tests/js/module_state_scan.test.js
tests/js/lineshape_roundtrip_backend.py
tests/js/per_tab_state.test.js
tests/js/lineshape_parity_backend.py
tests/js/fit_start_poll.test.js
tests/js/find_peaks_plain_message.test.js
tests/js/scattered_starts.test.js
tests/js/find_peaks_endpoint_avg.test.js
tests/js/lineshape_roundtrip.test.js
tests/js/fp_experimental_notice.test.js
tests/js/autofit_c1s_gate.test.js
tests/js/lineshape_parity.test.js
tests/js/autofit_required.test.js
tests/js/roi_clamp_centre_warning.test.js
tests/js/autofit_zero_graphite.test.js

codex
Tab activation restores the incoming data and ROI fields before calling the gate; stack tabs also fail closed. The record-path mismatch therefore appears limited to inactive-record use. In the parked LR proposal, occupancy uses the new statistic, but detectability still reports the F-test verdict, which can disagree on the README’s own stress case. I’m checking that case numerically without applying either patch.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import numpy, lmfit
print('\\''Imports OK'\\'')'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 1652ms:
/Users/skyefortier/.matplotlib is not a writable directory
Imports OK

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\''),cp=require('\\''child_process'\\''),vm=require('\\''vm'\\'');
const old=cp.execFileSync('\\''git'\\'',['\\''show'\\'','\\''07e0839:templates/index.html'\\''],{encoding:'\\''utf8'\\'',stdio:['\\''ignore'\\'','\\''pipe'\\'','\\''ignore'\\'']});
const test=fs.readFileSync('\\''tests/js/autofit_c1s_gate.test.js'\\'','\\''utf8'\\'');
vm.runInNewContext(test,{require:n=>n==='\\''fs'\\''?{readFileSync:()=>old}:require(n),__dirname:process.cwd()+'\\''/tests/js'\\'',console});'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
TAP version 13
# Subtest: the sweep reproduction: record window on C 1s, U 4f typed in the fields (no tab switch) — the gate CLOSES
ok 1 - the sweep reproduction: record window on C 1s, U 4f typed in the fields (no tab switch) — the gate CLOSES
  ---
  duration_ms: 2.557056
  type: 'test'
  ...
# Subtest: the SELECTED data decide, not the typed midpoint of a window that reaches past the data
ok 2 - the SELECTED data decide, not the typed midpoint of a window that reaches past the data
  ---
  duration_ms: 1.4576
  type: 'test'
  ...
# Subtest: a non-active record is judged on its saved window over its own corrected data
ok 3 - a non-active record is judged on its saved window over its own corrected data
  ---
  duration_ms: 0.729971
  type: 'test'
  ...
# Subtest: every caller of the gate is for the active tab (menu state, charge-reference permission, the Auto-Fit run)
ok 4 - every caller of the gate is for the active tab (menu state, charge-reference permission, the Auto-Fit run)
  ---
  duration_ms: 2.222556
  type: 'test'
  ...
1..4
# tests 4
# suites 0
# pass 4
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 17.341851

exec
/bin/zsh -lc "git show 07e0839:templates/index.html | sed -n '7748,7780p'; git rev-parse HEAD; git diff --numstat 07e0839..HEAD -- templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-RR4HDDFG' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-l0J16xws' (errno=Operation not permitted)
  }
}

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

// ── Scattered-starts check (2026-09-21) ───────────────────────────────────────
// Every Run Fit with two or more unlinked components asks the server for three
// more fits of the SAME method from scattered starts. The student's result
// stays THE FIT; a solution with a lower reduced chi-square is listed beside it
// with its own areas and how far each component moved from the student's start
// (a relocated component must be visible at a glance: on a committed C 1s scan
// the better-scoring solution slid C-O 1.4 eV under the main line). Solutions
// that are not better are only counted. Measured on the lab's 202 fit targets:
// an alternative appears on 0 % of re-fits of a saved solution and 7 % of
// not-yet-fitted starts, for a median +0.5 s. No certification language: the
// check can show a decomposition is not unique, never that one is correct.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-jqYw2K0n' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-GP7MLHrP' (errno=Operation not permitted)
895f323eeacb80cf89491e4b007d5b6160a29541
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-zBYDXztV' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-OmKgDw1Q' (errno=Operation not permitted)
25	10	templates/index.html

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\''),cp=require('\\''child_process'\\'');
const old=cp.execFileSync('\\''git'\\'',['\\''show'\\'','\\''07e0839:templates/index.html'\\''],{encoding:'\\''utf8'\\'',stdio:['\\''ignore'\\'','\\''pipe'\\'','\\''ignore'\\'']});
const test=fs.readFileSync('\\''tests/js/autofit_c1s_gate.test.js'\\'','\\''utf8'\\'');
let failed=0;
const req=n=>n==='\\''fs'\\''?{readFileSync:()=>old}:n==='\\''node:test'\\''?{test:(name,fn)=>{try{fn();console.log('\\''PASS'\\'',name)}catch(e){failed++;console.log('\\''FAIL'\\'',name,e.message)}}}:require(n);
new Function('\\''require'\\'','\\''__dirname'\\'',test)(req,process.cwd()+'\\''/tests/js'\\'');
console.log('\\''old gate failures'\\'',failed);'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
PASS the sweep reproduction: record window on C 1s, U 4f typed in the fields (no tab switch) — the gate CLOSES
PASS the SELECTED data decide, not the typed midpoint of a window that reaches past the data
PASS a non-active record is judged on its saved window over its own corrected data
PASS every caller of the gate is for the active tab (menu state, charge-reference permission, the Auto-Fit run)
old gate failures 0

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile
tempfile.tempdir = '\\''/tmp'\\''
import sys, pathlib, re, importlib.abc, importlib.util, json
variant = sys.argv[1]
sources = {}
if variant "'!= '"'\\''baseline'\\'':
    patch = pathlib.Path('\\''docs/findings/noise-floor-occupancy/variant_'\\''+variant+'\\''.patch'\\'').read_text()
    for chunk in patch.split('\\''diff --git '\\'')[1:]:
        lines = chunk.splitlines(keepends=True)
        filename = lines[0].split()[1][2:]
        orig = pathlib.Path(filename).read_text().splitlines(keepends=True)
        out=[]; cursor=0; i=1
        while i < len(lines):
            m=re.match(r'\\''@@ -(\\d+)(?:,\\d+)? \\+\\d+(?:,\\d+)? @@'\\'',lines[i])
            if not m: i+=1; continue
            start=int(m.group(1))-1
            out.extend(orig[cursor:start]); cursor=start; i+=1
            while i<len(lines) and not lines[i].startswith('\\''@@'\\''):
                line=lines[i]
                if line.startswith('\\'' '\\''):
                    assert orig[cursor] == line[1:],(filename,cursor)
                    out.append(line[1:]); cursor+=1
                elif line.startswith('\\''-'\\''):
                    assert orig[cursor] == line[1:],(filename,cursor)
                    cursor+=1
                elif line.startswith('\\''+'\\''): out.append(line[1:])
                i+=1
        out.extend(orig[cursor:]); sources[filename[:-3].replace('\\''/'\\'','\\''.'\\'')]='\\'''\\''.join(out)
class Loader(importlib.abc.MetaPathFinder,importlib.abc.Loader):
    def find_spec(self,fullname,path=None,target=None):
        if fullname in sources:return importlib.util.spec_from_loader(fullname,self)
    def create_module(self,spec): return None
    def exec_module(self,module):exec(compile(sources[module.__name__],module.__name__,'\\''exec'\\''),module.__dict__)
sys.meta_path.insert(0,Loader())
sys.path.insert(0,str(pathlib.Path('\\''tests/autofit'\\'').resolve()))
import autofit.engine as e
from stress_cases import bg_mismatch_case
from autofit.methods import get_method
original=e.rank_and_filter
def rank(*args,**kwargs):
    for r in args[0]:
        print(variant,'\\''report'\\'',r.model.name,'\\''chi'\\'',r.reduced_chi_sq,'\\''persist'\\'',r.active_min_persistence,'\\''orphan'\\'',r.stability.orphan_rate,
              '\\''comps'\\'',[(c.slot_role,getattr(c,'\\''support'\\'',None)) for c in r.primary_fit.components],flush=True)
    return original(*args,**kwargs)
e.rank_and_filter=rank
case=bg_mismatch_case(seed=61)
res=get_method('\\''ic_model_comparison'\\'').run(case.x,case.y,grammar=case.grammar,options={'\\''n_refits'\\'':4,'\\''rng_seed'\\'':0,'\\''noise_floor'\\'':1.0,'\\''enable_proposal_pass'\\'':True})
print(variant,'\\''RESULT'\\'',json.dumps(res.diagnostics,default=str),flush=True)
' baseline" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
exec
/bin/zsh -lc "node -e 'const cp=require('\\''child_process'\\'');const old=cp.execFileSync('\\''git'\\'',['\\''show'\\'','\\''07e0839:templates/index.html'\\''],{encoding:'\\''utf8'\\'',stdio:['\\''ignore'\\'','\\''pipe'\\'','\\''ignore'\\'']});const code=old.slice(old.indexOf('\\''function isC1sTab('\\''),old.indexOf('\\''// ── Scattered-starts'\\'',old.indexOf('\\''function isC1sTab('\\'')));console.log(code);const f=new Function('\\''tabManager'\\'','\\''getROIData'\\'',code+'\\'';return isC1sTab'\\'')({activeId:'\\''t1'\\''},()=>({be:[370,415]}));console.log('\\''old direct stale C1s='\\'',f({id:'\\''t1'\\'',rawBE:[270,420],ui:{roiMin:'\\''280'\\'',roiMax:'\\''295'\\''}}));'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
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


old direct stale C1s= true

 succeeded in 13247ms:
/Users/skyefortier/.matplotlib is not a writable directory
baseline report P1 chi 468.6838552678528 persist 1.0 orphan 0.0 comps [('main_a', None)]
baseline report P2 chi 308.7466180222082 persist 1.0 orphan 0.0 comps [('main_a', None), ('main_b', None)]
baseline report P3 chi 284.1218885924425 persist 1.0 orphan 0.0 comps [('main_a', None), ('main_b', None), ('main_c', None)]
baseline RESULT {"winner": "P3+bfix", "conditional": true, "conditional_reason": "decisive_override", "winner_boundary_hits": [], "winner_unphysical_widths": ["main_c:fwhm=2.50eV\u22652.0eV ordinary cap (no known-broad justification)"], "winner_boundary_fixed_params": ["s_main_c_fwhm"], "filtered_dominant_alternative": null, "weighted_ic_disagreement": null, "preseeded_features": [], "n_survivors": 2, "n_filtered": 2, "n_non_converged": 0, "analysis_truncated": false, "n_candidates_evaluated": 3, "n_candidates_total": 3}

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile
tempfile.tempdir = '\\''/tmp'\\''
import sys, pathlib, re, importlib.abc, importlib.util, json
variant = sys.argv[1]
sources = {}
if variant "'!= '"'\\''baseline'\\'':
    patch = pathlib.Path('\\''docs/findings/noise-floor-occupancy/variant_'\\''+variant+'\\''.patch'\\'').read_text()
    for chunk in patch.split('\\''diff --git '\\'')[1:]:
        lines = chunk.splitlines(keepends=True)
        filename = lines[0].split()[1][2:]
        orig = pathlib.Path(filename).read_text().splitlines(keepends=True)
        out=[]; cursor=0; i=1
        while i < len(lines):
            m=re.match(r'\\''@@ -(\\d+)(?:,\\d+)? \\+\\d+(?:,\\d+)? @@'\\'',lines[i])
            if not m: i+=1; continue
            start=int(m.group(1))-1
            out.extend(orig[cursor:start]); cursor=start; i+=1
            while i<len(lines) and not lines[i].startswith('\\''@@'\\''):
                line=lines[i]
                if line.startswith('\\'' '\\''):
                    assert orig[cursor] == line[1:],(filename,cursor)
                    out.append(line[1:]); cursor+=1
                elif line.startswith('\\''-'\\''):
                    assert orig[cursor] == line[1:],(filename,cursor)
                    cursor+=1
                elif line.startswith('\\''+'\\''): out.append(line[1:])
                i+=1
        out.extend(orig[cursor:]); sources[filename[:-3].replace('\\''/'\\'','\\''.'\\'')]='\\'''\\''.join(out)
class Loader(importlib.abc.MetaPathFinder,importlib.abc.Loader):
    def find_spec(self,fullname,path=None,target=None):
        if fullname in sources:return importlib.util.spec_from_loader(fullname,self)
    def create_module(self,spec): return None
    def exec_module(self,module):exec(compile(sources[module.__name__],module.__name__,'\\''exec'\\''),module.__dict__)
sys.meta_path.insert(0,Loader())
sys.path.insert(0,str(pathlib.Path('\\''tests/autofit'\\'').resolve()))
import autofit.engine as e
from stress_cases import bg_mismatch_case
from autofit.methods import get_method
original=e.rank_and_filter
def rank(*args,**kwargs):
    for r in args[0]:
        print(variant,'\\''report'\\'',r.model.name,'\\''chi'\\'',r.reduced_chi_sq,'\\''persist'\\'',r.active_min_persistence,'\\''orphan'\\'',r.stability.orphan_rate,
              '\\''comps'\\'',[(c.slot_role,getattr(c,'\\''support'\\'',None)) for c in r.primary_fit.components],flush=True)
    return original(*args,**kwargs)
e.rank_and_filter=rank
case=bg_mismatch_case(seed=61)
res=get_method('\\''ic_model_comparison'\\'').run(case.x,case.y,grammar=case.grammar,options={'\\''n_refits'\\'':4,'\\''rng_seed'\\'':0,'\\''noise_floor'\\'':1.0,'\\''enable_proposal_pass'\\'':True})
print(variant,'\\''RESULT'\\'',json.dumps(res.diagnostics,default=str),flush=True)
' F_support_test" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile
tempfile.tempdir = '\\''/tmp'\\''
import sys, pathlib, re, importlib.abc, importlib.util, json
variant = sys.argv[1]
sources = {}
if variant "'!= '"'\\''baseline'\\'':
    patch = pathlib.Path('\\''docs/findings/noise-floor-occupancy/variant_'\\''+variant+'\\''.patch'\\'').read_text()
    for chunk in patch.split('\\''diff --git '\\'')[1:]:
        lines = chunk.splitlines(keepends=True)
        filename = lines[0].split()[1][2:]
        orig = pathlib.Path(filename).read_text().splitlines(keepends=True)
        out=[]; cursor=0; i=1
        while i < len(lines):
            m=re.match(r'\\''@@ -(\\d+)(?:,\\d+)? \\+\\d+(?:,\\d+)? @@'\\'',lines[i])
            if not m: i+=1; continue
            start=int(m.group(1))-1
            out.extend(orig[cursor:start]); cursor=start; i+=1
            while i<len(lines) and not lines[i].startswith('\\''@@'\\''):
                line=lines[i]
                if line.startswith('\\'' '\\''):
                    assert orig[cursor] == line[1:],(filename,cursor)
                    out.append(line[1:]); cursor+=1
                elif line.startswith('\\''-'\\''):
                    assert orig[cursor] == line[1:],(filename,cursor)
                    cursor+=1
                elif line.startswith('\\''+'\\''): out.append(line[1:])
                i+=1
        out.extend(orig[cursor:]); sources[filename[:-3].replace('\\''/'\\'','\\''.'\\'')]='\\'''\\''.join(out)
class Loader(importlib.abc.MetaPathFinder,importlib.abc.Loader):
    def find_spec(self,fullname,path=None,target=None):
        if fullname in sources:return importlib.util.spec_from_loader(fullname,self)
    def create_module(self,spec): return None
    def exec_module(self,module):exec(compile(sources[module.__name__],module.__name__,'\\''exec'\\''),module.__dict__)
sys.meta_path.insert(0,Loader())
sys.path.insert(0,str(pathlib.Path('\\''tests/autofit'\\'').resolve()))
import autofit.engine as e
from stress_cases import bg_mismatch_case
from autofit.methods import get_method
original=e.rank_and_filter
def rank(*args,**kwargs):
    for r in args[0]:
        print(variant,'\\''report'\\'',r.model.name,'\\''chi'\\'',r.reduced_chi_sq,'\\''persist'\\'',r.active_min_persistence,'\\''orphan'\\'',r.stability.orphan_rate,
              '\\''comps'\\'',[(c.slot_role,getattr(c,'\\''support'\\'',None)) for c in r.primary_fit.components],flush=True)
    return original(*args,**kwargs)
e.rank_and_filter=rank
case=bg_mismatch_case(seed=61)
res=get_method('\\''ic_model_comparison'\\'').run(case.x,case.y,grammar=case.grammar,options={'\\''n_refits'\\'':4,'\\''rng_seed'\\'':0,'\\''noise_floor'\\'':1.0,'\\''enable_proposal_pass'\\'':True})
print(variant,'\\''RESULT'\\'',json.dumps(res.diagnostics,default=str),flush=True)
' LR_likelihood_ratio" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 9182ms:
/Users/skyefortier/.matplotlib is not a writable directory
F_support_test report P1 chi 468.6838552678528 persist 1.0 orphan 0.0 comps [('main_a', {'f': 132.10063473899734, 'delta_chi2': 247653.73909121484, 'supported': True})]
F_support_test report P2 chi 308.7466180222082 persist 1.0 orphan 0.0 comps [('main_a', {'f': 85.29090448970058, 'delta_chi2': 105333.11323700091, 'supported': True}), ('main_b', {'f': 122.78792727078564, 'delta_chi2': 151641.42911524777, 'supported': True})]
F_support_test report P3 chi 284.1218885924425 persist 0.0 orphan 1.0 comps [('main_a', {'f': 114.09141507309049, 'delta_chi2': 129663.47329100291, 'supported': True}), ('main_b', {'f': 113.66600159164356, 'delta_chi2': 129179.99616387737, 'supported': True}), ('main_c', {'f': 9.417061879395952, 'delta_chi2': 10702.373624663494, 'supported': False})]
F_support_test RESULT {"winner": "P2", "conditional": false, "conditional_reason": null, "winner_boundary_hits": [], "winner_unphysical_widths": [], "winner_boundary_fixed_params": [], "filtered_dominant_alternative": {"name": "P3", "bic_star": 3648.466236534472, "delta_bic_vs_winner": 152.94516771360122, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:fwhm@max'], unphysical_widths=['main_c:fwhm=2.50eV\u22652.0eV ordinary cap (no known-broad justification)'], orphan_peaks=True)"}, "weighted_ic_disagreement": null, "preseeded_features": [], "n_survivors": 1, "n_filtered": 2, "n_non_converged": 0, "analysis_truncated": false, "n_candidates_evaluated": 3, "n_candidates_total": 3}

exec
/bin/zsh -lc "sed -n '1,85p' tests/js/autofit_c1s_gate.test.js; nl -ba templates/index.html | sed -n '7750,7795p'; nl -ba docs/findings/noise-floor-occupancy/README.md | head -90; rg -n '\\.contains\\(' --glob '*.py' . | head -35; sed -n '1060,1114p' autofit/engine.py; sed -n '1325,1395p' autofit/engine.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
// F3 (2026-09-27, sweep M5): the Auto-Fit C1s gate judges the DATA the fit
// would use — for the active tab the live selection getROIData() returns, for
// any other record its saved window over its own corrected data — never the
// active tab's record ui (synced only on a tab switch or save) and never the
// typed midpoint of a window that reaches past the data.
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
const lines = html.split('\n');
function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name + '\\(');
  const start = lines.findIndex(l => re.test(l));
  assert.ok(start >= 0, name);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail('unbalanced ' + name);
}

// a wide scan 270-420 eV (C 1s and a U 4f doublet), 0.5 eV steps
const RAW = Array.from({ length: 301 }, (_, i) => 420 - 0.5 * i);
function gate({ activeId, liveSel }) {
  const tabManager = { activeId };
  const getROIData = () => ({ be: liveSel, inten: liveSel.map(() => 1) });
  return new Function('tabManager', 'getROIData', extractFn('isC1sTab') + '\nreturn isC1sTab;')(tabManager, getROIData);
}
const sel = (lo, hi) => RAW.filter(v => v >= lo && v <= hi);

test('the sweep reproduction: record window on C 1s, U 4f typed in the fields (no tab switch) — the gate CLOSES', () => {
  const tab = { id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '280', roiMax: '295' } };   // stale record ui
  assert.strictEqual(gate({ activeId: 't1', liveSel: sel(370, 415) })(tab), false, 'judged on the live U 4f selection');
  assert.strictEqual(gate({ activeId: 't1', liveSel: sel(280, 295) })(tab), true, 'a live C 1s selection passes');
});

test('the SELECTED data decide, not the typed midpoint of a window that reaches past the data', () => {
  // data 280-300 only; typed 250-400 -> typed midpoint 325 (not C 1s) but the selection is all C 1s
  const narrow = RAW.filter(v => v >= 280 && v <= 300);
  const tab = { id: 't1', rawBE: narrow, ccShift: 0, ui: { roiMin: '250', roiMax: '400' } };
  assert.strictEqual(gate({ activeId: 't1', liveSel: narrow })(tab), true);
  assert.strictEqual(gate({ activeId: 't1', liveSel: [] })(tab), false, 'an empty selection is not C 1s');
});

test('a non-active record is judged on its saved window over its own corrected data', () => {
  const g = gate({ activeId: 'other', liveSel: sel(370, 415) });
  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '280', roiMax: '295' } }), true);
  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '370', roiMax: '415' } }), false);
  // the window is in the CORRECTED frame, as the fit is: at a 100 eV shift, corrected 280-295 selects raw
  // 380-395, which exists — judged as C 1s; a window the shifted data do not reach selects nothing
  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 100, ui: { roiMin: '280', roiMax: '295' } }), true);
  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 200, ui: { roiMin: '280', roiMax: '295' } }), false,
    'corrected 70-220 has no point in 280-295: nothing selected');
  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: {} }), false, 'no window: the whole 270-420 scan, midpoint 345');
  assert.strictEqual(g({ id: 't1', rawBE: [], ui: {} }), false);
});

test('every caller of the gate is for the active tab (menu state, charge-reference permission, the Auto-Fit run)', () => {
  for (const fn of ['_recomputeAutoFitMenuState', '_isChargeRefAllowed', 'runAutoFitC1sGraphite']) {
    assert.match(extractFn(fn), /isC1sTab\(tab\)/, fn);
  }
  // and the ROI fields refresh the menu on every keystroke
  assert.match(html, /id="roi-min"[^>]*oninput="updatePlot\(\);_recomputeAutoFitMenuState\(\)"/);
  assert.match(html, /id="roi-max"[^>]*oninput="updatePlot\(\);_recomputeAutoFitMenuState\(\)"/);
});
  7750	
  7751	// Is this a C 1s spectrum, as Auto-Fit C1s Graphite would fit it? Unit F3
  7752	// (2026-09-27, sweep M5): judged on the DATA the fit would use — for the active
  7753	// tab the live selection getROIData() returns (the typed fields, clipped to the
  7754	// data, in the corrected frame); for any other record its saved window over
  7755	// its own corrected data. It used to read tab.ui, which for the ACTIVE tab is
  7756	// synced only on a tab switch or save, and the TYPED midpoint: a wide scan with
  7757	// the record's C 1s window but a U 4f window typed in the fields passed the
  7758	// gate, and the fit then took the U 4f line as "Graphite".
  7759	function isC1sTab(tab) {
  7760	  if (!tab || !tab.rawBE || !tab.rawBE.length) return false;
  7761	  let be;
  7762	  const isActive = typeof tabManager !== 'undefined' && tabManager && tab.id === tabManager.activeId;
  7763	  if (isActive && typeof getROIData === 'function') {
  7764	    be = getROIData().be;
  7765	  } else {
  7766	    const shift = Number.isFinite(tab.ccShift) ? tab.ccShift : 0;
  7767	    const corr = tab.rawBE.map(v => v - shift);
  7768	    const ui = tab.ui || {};
  7769	    const a = parseFloat(ui.roiMin), b = parseFloat(ui.roiMax);
  7770	    if (Number.isFinite(a) && Number.isFinite(b)) {
  7771	      const lo = Math.min(a, b), hi = Math.max(a, b);
  7772	      be = corr.filter(v => v >= lo && v <= hi);
  7773	    } else {
  7774	      be = corr;                               // no window set yet: the whole scan
  7775	    }
  7776	  }
  7777	  if (!be || !be.length) return false;
  7778	  let lo = Infinity, hi = -Infinity;
  7779	  for (const v of be) { if (v < lo) lo = v; if (v > hi) hi = v; }
  7780	  if (!Number.isFinite(lo) || !Number.isFinite(hi)) return false;
  7781	  const mid = (lo + hi) / 2;
  7782	  return mid >= 270.0 && mid <= 315.0;
  7783	}
  7784	
  7785	// ── Scattered-starts check (2026-09-21) ───────────────────────────────────────
  7786	// Every Run Fit with two or more unlinked components asks the server for three
  7787	// more fits of the SAME method from scattered starts. The student's result
  7788	// stays THE FIT; a solution with a lower reduced chi-square is listed beside it
  7789	// with its own areas and how far each component moved from the student's start
  7790	// (a relocated component must be visible at a glance: on a committed C 1s scan
  7791	// the better-scoring solution slid C-O 1.4 eV under the main line). Solutions
  7792	// that are not better are only counted. Measured on the lab's 202 fit targets:
  7793	// an alternative appears on 0 % of re-fits of a saved solution and 7 % of
  7794	// not-yet-fitted starts, for a median +0.5 s. No certification language: the
  7795	// check can show a decomposition is not unique, never that one is correct.
     1	# Find Peaks' 1-count occupancy floor → scale-free: PARKED for an owner decision (2026-09-27)
     2	
     3	Part of unit F3 (sweep M9, first bullet). The other half of F3 — the Auto-Fit
     4	C1s gate judging a stale typed window (sweep M5) — ships on its own in
     5	`fix-noise-floor-scale-free` and does not depend on this.
     6	
     7	## What was found
     8	
     9	`noise_floor` (default 1.0, never sent by the page) does two jobs in
    10	`autofit/`:
    11	
    12	1. a Poisson variance floor, `sigma = sqrt(max(y, noise_floor))` — the
    13	   counting convention the server's weights use; not a decision threshold,
    14	   left as is by both variants;
    15	2. an OCCUPANCY threshold, `amplitude > noise_floor` — whether a fitted
    16	   component occupies its slot (`match_components_to_slots`), whether a
    17	   proposed slot survives (`_evaluate_proposal`), the detectability status
    18	   (`build_confidence_vector`). A slot is "occupied" at amplitude 1.5 and not
    19	   at 0.5 whatever the data's scale; persistence, the absent-slot test and the
    20	   stability gate follow from it. This is the design rule's case.
    21	
    22	Both variants replace (2) with a statistic on the component's own fit
    23	(computed once when the component is extracted from its lmfit result and
    24	carried on `FittedComponent.support`), leave (1) alone, and fall back to
    25	`amplitude > 0` (a sign test) for a component with no fit behind it. They
    26	differ in ONE line — what "occupied" means:
    27	
    28	| variant | occupied when | patch |
    29	|---|---|---|
    30	| **F** — the server's support test | `fitting._component_support` "supported": Δχ² > 0 and F = (Δχ²/p) / (χ²_with/dof) ≥ 10 — the step (b) "not supported by the data" statistic and threshold | `variant_F_support_test.patch` |
    31	| **LR** — Poisson likelihood ratio | Δχ²/p ≥ 10 on the Poisson-weighted χ², NOT divided by the fit's own misfit χ²_with/dof | `variant_LR_likelihood_ratio.patch` |
    32	
    33	Both are scale-free (the weights make χ² dimensionless) and carry no tolerance.
    34	
    35	## The evidence
    36	
    37	| suite | baseline (today) | F | LR |
    38	|---|---|---|---|
    39	| gated real-data parity gates + stress honesty (`RUN_AUTOFIT_GATE=1`: C 1s parity, Bayesian real, candidate-pool real, U 4f unresolved, stress honesty) | 17 passed, 4 skipped | **16 passed, 1 FAILED** | 17 passed, 4 skipped |
    40	| always-on `tests/autofit` (incl. the C 1s / region parity batteries) | green | **1 failed** (the same stress case), 556 passed | 557 passed, 7 skipped |
    41	
    42	The failing case, `test_stress_honesty.py::test_bg_mismatch_surfaces_loudly`:
    43	a Shirley-shaped truth fitted with a straight-line background, χ²ᵣ ≈ 280–470
    44	for every candidate. The test requires the mismatch to be machine-visible
    45	("conditional" tier), never a clean confident result. Today the 3-component
    46	candidate P3 is stable but violates plausibility, enters the conditional
    47	pool, and its bound-fixed refit wins via the decisive override →
    48	`conditional: true`. Under F, P3's third component has F < 10 BECAUSE the fit
    49	is so bad: F divides the gain by χ²_with/dof ≈ 284, so a component that
    50	removes a large χ² still reads "unsupported"; it becomes an orphan, P3's
    51	persistence drops to 0, P3 leaves the conditional pool, and P2 (χ²ᵣ 309) is
    52	returned as a CLEAN survivor. Under LR the same component is occupied (its
    53	gain per parameter is far above 10 Poisson units) and the result is
    54	conditional, as today.
    55	
    56	## The decision (owner)
    57	
    58	- **F** keeps ONE definition of "supported" across the app (Find Peaks would
    59	  judge components exactly as Run Fit's "not supported by the data" does), but
    60	  in a grossly mis-modelled fit it declares real components absent and can
    61	  turn an honest "conditional" answer into a clean one.
    62	- **LR** keeps today's behaviour on every gate and the honesty case; its
    63	  statistic differs from the server's support verdict, so after "Apply" a
    64	  component Find Peaks counted as occupied could still read "not supported"
    65	  in Run Fit's results on a very badly fitted model (the two agree whenever
    66	  χ²ᵣ ≈ 1).
    67	
    68	**Recommendation: LR.** Occupancy asks "did the fit put something real
    69	here", which is a question about the signal against counting noise, not
    70	against the model's own misfit; normalising by the misfit makes the answer
    71	depend on how wrong the rest of the model is, which is exactly what the
    72	honesty tier exists to report. Measured: LR changes nothing on any gate; F
    73	breaks the honesty contract.
    74	
    75	To apply the chosen variant: `git apply docs/findings/noise-floor-occupancy/variant_<X>.patch`
    76	on this branch, then the full suite, the gated suite (`RUN_AUTOFIT_GATE=1`)
    77	and Codex ×2. The `test_methods_seam` detectability assertion and the schema
    78	round-trip fixture already accept both variants' status strings.
./tests/test_browser_find_peaks_drag.py:187:            "() => document.getElementById('find-peaks-overlay').classList.contains('open')")
./tests/test_browser_find_peaks_drag.py:190:            "() => document.getElementById('find-peaks-modal-box').classList.contains('dragging')")
./tests/test_browser_palette.py:174:        assert pg.evaluate("() => document.getElementById('ref-panel').classList.contains('collapsed')") is True
./tests/test_browser_palette.py:182:            return { collapsed: p.classList.contains('collapsed'),
./tests/test_browser_palette.py:204:            const dragging = p.classList.contains('dragging');
./tests/test_browser_palette.py:222:            return { passthrough: p.classList.contains('identify-passthrough'),
./tests/test_browser_palette.py:241:            return { mode: placeMode, passthrough: p.classList.contains('identify-passthrough'),
./tests/test_browser_identify_frame.py:219:        light: document.body.classList.contains('light-theme'),
./tests/test_browser_identify_frame.py:229:            light: document.body.classList.contains('light-theme'),
./tests/test_browser_identify_frame.py:241:        page.evaluate("""() => { if (document.body.classList.contains('light-theme')) toggleTheme();
./tests/test_browser_identify_frame.py:511:        return { mode: placeMode, cls: p.classList.contains('identify-passthrough'),
./tests/test_browser_batch_roi.py:237:                toastShown: document.getElementById('prominent-toast').classList.contains('show'),
    def _window_center(slot: ComponentSlot) -> float:
        # NEVER the widened bound (Codex-caught, round 2): this is a
        # TIE-BREAK reference point ("how close is this component to
        # where this slot expects its peak"), not an acceptance test —
        # widening it would drag the reference point far from the
        # slot's true expected position (e.g. a curated slot's own
        # narrow window widened to a whole ROI), making a neighboring
        # slot's UNWIDENED, much-closer center win the tie-break even
        # when the component sits well inside THIS slot's own original
        # window. Acceptance (_accepts, above) is the only place the
        # widened bound belongs.
        lo, hi = _effective_be_window(slot, components)
        return 0.5 * (lo + hi)

    for comp in components:
        candidate_slots = [s for s in model.slots if _accepts(s, comp)]
        if not candidate_slots:
            orphans.append(FittedComponent(
                slot_role="unmatched", position=comp.position, fwhm=comp.fwhm,
                amplitude=comp.amplitude, shape_params=comp.shape_params,
                line_shape=comp.line_shape,
            ))
            continue

        shapes = {s.line_shape for s in candidate_slots}
        if len(shapes) > 1:
            if _is_asymmetric_component(comp):
                preferred = [s for s in candidate_slots if s.line_shape in asym_shapes]
            else:
                preferred = [s for s in candidate_slots if s.line_shape not in asym_shapes]
            if preferred:
                candidate_slots = preferred

        best_slot = min(candidate_slots, key=lambda s: abs(comp.position - _window_center(s)))
        incumbent = slot_map[best_slot.role]
        claimed = FittedComponent(
            slot_role=best_slot.role, position=comp.position, fwhm=comp.fwhm,
            amplitude=comp.amplitude, shape_params=comp.shape_params,
            line_shape=comp.line_shape,
        )
        if incumbent is None:
            slot_map[best_slot.role] = claimed
        else:
            wc = _window_center(best_slot)
            if abs(comp.position - wc) < abs(incumbent.position - wc):
                orphans.append(incumbent)
                slot_map[best_slot.role] = claimed
            else:
                orphans.append(comp)

    slot_map["__orphans__"] = orphans  # type: ignore[assignment]
    return slot_map


# ─────────────────────────────────────────────────────────────────────────────
    for s in non_main:
        groups.setdefault(root(s.role), []).append(s)
    return list(groups.values())


def _identify_absent_slots(
    model: CandidateModel,
    stability: ModelStability,
    slot_areas: dict[str, float],
    primary: FitOutcome,
    persistence_threshold: float = ABSENT_SLOT_PERSISTENCE_THRESHOLD,
    area_fraction_threshold: float = ABSENT_SLOT_AREA_FRACTION,
) -> list[AbsentSlotReport]:
    """
    Absent classification is ATOMIC per linked group: a slot whose amplitude
    or shape is expression-tied to a partner cannot be absent while the
    partner is present (a spin-orbit satellite pair is one physical feature).
    Every member must individually meet the persistence + area criteria for
    the group to be classified absent.

    The area fraction is normalized against the mains of the SLOT'S OWN
    (region, phase) when any exist — in a joint co-fit, normalizing against
    the global main area would let a huge foreign main (e.g. the BN N 1s
    line in a U 4f + N 1s window) dilute a real satellite of the smaller
    element below the threshold (Codex Stage-3 finding #2).  Falls back to
    the global main area for slots without same-scope mains (e.g. proposals,
    which are region-unassigned).
    """
    global_main_area = sum(a for role, a in slot_areas.items() if _is_main_role(role))
    if global_main_area <= 0:
        return []

    scoped_main_area: dict[tuple[str, str], float] = {}
    for s in model.slots:
        if _is_main_role(s.role):
            key = (s.region, s.phase_id)
            scoped_main_area[key] = scoped_main_area.get(key, 0.0) \
                + float(slot_areas.get(s.role, 0.0))

    def _member_report(slot: ComponentSlot) -> Optional[AbsentSlotReport]:
        sstab = stability.per_slot.get(slot.role)
        if sstab is None or sstab.persistence >= persistence_threshold:
            return None
        main_area = scoped_main_area.get((slot.region, slot.phase_id), 0.0)
        if main_area <= 0:
            main_area = global_main_area
        area = float(slot_areas.get(slot.role, 0.0))
        frac = area / main_area
        if frac >= area_fraction_threshold:
            return None
        return AbsentSlotReport(
            role=slot.role, persistence=sstab.persistence, fitted_area=area,
            main_area=main_area, area_fraction=frac,
            threshold=area_fraction_threshold,
            removed_n_params=_count_slot_free_params(slot, primary),
        )

    absent: list[AbsentSlotReport] = []
    for group in _linked_groups(model):
        reports = [_member_report(s) for s in group]
        if all(r is not None for r in reports):
            absent.extend(reports)  # type: ignore[arg-type]
    return absent


# ─────────────────────────────────────────────────────────────────────────────
# Residual diagnostics
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ResidualDiagnostics:

 succeeded in 12697ms:
/Users/skyefortier/.matplotlib is not a writable directory
LR_likelihood_ratio report P1 chi 468.6838552678528 persist 1.0 orphan 0.0 comps [('main_a', {'f': 132.10063473899734, 'delta_chi2': 247653.73909121484, 'supported': True, '_p': 4})]
LR_likelihood_ratio report P2 chi 308.7466180222082 persist 1.0 orphan 0.0 comps [('main_a', {'f': 85.29090448970058, 'delta_chi2': 105333.11323700091, 'supported': True, '_p': 4}), ('main_b', {'f': 122.78792727078564, 'delta_chi2': 151641.42911524777, 'supported': True, '_p': 4})]
LR_likelihood_ratio report P3 chi 284.1218885924425 persist 1.0 orphan 0.0 comps [('main_a', {'f': 114.09141507309049, 'delta_chi2': 129663.47329100291, 'supported': True, '_p': 4}), ('main_b', {'f': 113.66600159164356, 'delta_chi2': 129179.99616387737, 'supported': True, '_p': 4}), ('main_c', {'f': 9.417061879395952, 'delta_chi2': 10702.373624663494, 'supported': False, '_p': 4})]
LR_likelihood_ratio RESULT {"winner": "P3+bfix", "conditional": true, "conditional_reason": "decisive_override", "winner_boundary_hits": [], "winner_unphysical_widths": ["main_c:fwhm=2.50eV\u22652.0eV ordinary cap (no known-broad justification)"], "winner_boundary_fixed_params": ["s_main_c_fwhm"], "filtered_dominant_alternative": null, "weighted_ic_disagreement": null, "preseeded_features": [], "n_survivors": 2, "n_filtered": 2, "n_non_converged": 0, "analysis_truncated": false, "n_candidates_evaluated": 3, "n_candidates_total": 3}

codex
The stress-case measurements reproduce: baseline and LR return conditional `P3+bfix`; F drops P3’s persistence to zero and returns P2 with `conditional: false`. F still emits a `filtered_dominant_alternative` warning, so the README overstates the loss of warning signals. Its “scale-free” claim also needs correction: with the supplied Poisson weights, rescaling intensity changes LR’s verdict even when every value stays above the variance floor.

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\''),cp=require('\\''child_process'\\'');
const old=cp.execFileSync('\\''git'\\'',['\\''show'\\'','\\''07e0839:templates/index.html'\\''],{encoding:'\\''utf8'\\'',stdio:['\\''ignore'\\'','\\''pipe'\\'','\\''ignore'\\'']});
const test=fs.readFileSync('\\''tests/js/autofit_c1s_gate.test.js'\\'','\\''utf8'\\'');
let failed=0;
const req=n=>(n==='\\''fs'\\''||n==='\\''node:fs'\\'')?{readFileSync:()=>old}:n==='\\''node:test'\\''?{test:(name,fn)=>{try{fn();console.log('\\''PASS'\\'',name)}catch(e){failed++;console.log('\\''FAIL'\\'',name,e.message)}}}:require(n);
new Function('\\''require'\\'','\\''__dirname'\\'',test)(req,process.cwd()+'\\''/tests/js'\\'');
console.log('\\''old gate failures'\\'',failed);
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
function fn(name){const lines=html.split('\\''\\n'\\'');const s=lines.findIndex(x=>x.startsWith('\\''function '\\''+name+'\\''('\\''));let d=0;for(let i=s;i<lines.length;i++){for(const ch of lines[i]){if(ch==='\\''{'\\'')d++;if(ch==='\\''}'\\'')d--;}if(d===0)return lines.slice(s,i+1).join('\\''\\n'\\'');}}
let state={rawBE:Array.from({length:301},(_,i)=>270+i/2),rawIntensity:Array(301).fill(1),ccShift:0},fields={'\\''roi-min'\\'':{value:'\\''280'\\''},'\\''roi-max'\\'':{value:'\\''295'\\''}},tm={activeId:'\\''t1'\\''},doc={getElementById:k=>fields[k]};
const api=new Function('\\''state'\\'','\\''document'\\'','\\''tabManager'\\'',[fn('\\''getCorrectedBE'\\''),fn('\\''getROIData'\\''),fn('\\''isC1sTab'\\''),'\\''return {isC1sTab,getROIData}'\\''].join('\\''\\n'\\''))(state,doc,tm);
function check(label,lo,hi,shift=0){fields['\\''roi-min'\\''].value=lo;fields['\\''roi-max'\\''].value=hi;state.ccShift=shift;let tab={id:'\\''t1'\\'',rawBE:state.rawBE,ccShift:shift,ui:{roiMin:lo,roiMax:hi}};let active=api.isC1sTab(tab);tm.activeId='\\''other'\\'';let record=api.isC1sTab(tab);tm.activeId='\\''t1'\\'';console.log(label,{active,record,n:api.getROIData().be.length});}
check('\\''C1s'\\'','\\''280'\\'','\\''295'\\'');check('\\''U4f'\\'','\\''370'\\'','\\''415'\\'');check('\\''reversed'\\'','\\''295'\\'','\\''280'\\'');check('\\''blank low'\\'','\\'''\\'','\\''295'\\'');check('\\''both blank'\\'','\\'''\\'','\\'''\\'');check('\\''outside'\\'','\\''500'\\'','\\''600'\\'');check('\\''shifted'\\'','\\''280'\\'','\\''295'\\'',100);
state.rawBE=Array.from({length:1000000},(_,i)=>280+20*i/999999);tm.activeId='\\''other'\\'';const t0=performance.now();console.log('\\''million point record'\\'',api.isC1sTab({id:'\\''long'\\'',rawBE:state.rawBE,ui:{}}),'\\''ms'\\'',performance.now()-t0);'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 160ms:
million point record true ms 101.99014200000002

exec
/bin/zsh -lc 'node --test tests/js/autofit_c1s_gate.test.js tests/js/roi_clamp_centre_warning.test.js tests/js/autofit_required.test.js tests/js/autofit_zero_graphite.test.js tests/js/per_tab_state.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 336ms:
# Subtest: the sweep reproduction: record window on C 1s, U 4f typed in the fields (no tab switch) — the gate CLOSES
ok 1 - the sweep reproduction: record window on C 1s, U 4f typed in the fields (no tab switch) — the gate CLOSES
  ---
  duration_ms: 5.489262
  type: 'test'
  ...
# Subtest: the SELECTED data decide, not the typed midpoint of a window that reaches past the data
ok 2 - the SELECTED data decide, not the typed midpoint of a window that reaches past the data
  ---
  duration_ms: 1.466658
  type: 'test'
  ...
# Subtest: a non-active record is judged on its saved window over its own corrected data
ok 3 - a non-active record is judged on its saved window over its own corrected data
  ---
  duration_ms: 0.923739
  type: 'test'
  ...
# Subtest: every caller of the gate is for the active tab (menu state, charge-reference permission, the Auto-Fit run)
ok 4 - every caller of the gate is for the active tab (menu state, charge-reference permission, the Auto-Fit run)
  ---
  duration_ms: 2.133255
  type: 'test'
  ...
# Subtest: a supported but NOT required anchor is refused before any charge-correction input is touched
ok 5 - a supported but NOT required anchor is refused before any charge-correction input is touched
  ---
  duration_ms: 5.553362
  type: 'test'
  ...
# Subtest: a required anchor proceeds; a check that did not RUN (older server, error, main fit not converged) does not block
ok 6 - a required anchor proceeds; a check that did not RUN (older server, error, main fit not converged) does not block
  ---
  duration_ms: 10.486697
  type: 'test'
  ...
# Subtest: the request asks for the Graphite anchor by id, and the gate precedes the support gate and every cc write
ok 7 - the request asks for the Graphite anchor by id, and the gate precedes the support gate and every cc write
  ---
  duration_ms: 1.032094
  type: 'test'
  ...
# Subtest: a refit that did not converge: no verdict, and Auto-Fit refuses before any charge-correction input is touched
ok 8 - a refit that did not converge: no verdict, and Auto-Fit refuses before any charge-correction input is touched
  ---
  duration_ms: 2.157719
  type: 'test'
  ...
# Subtest: the fixture set covers both outcomes
ok 9 - the fixture set covers both outcomes
  ---
  duration_ms: 1.31872
  type: 'test'
  ...
# Subtest: anchors NOTHING — residue: 1e7 flat, 1e-4 bump rounded away, manual background (round 5)
ok 10 - anchors NOTHING — residue: 1e7 flat, 1e-4 bump rounded away, manual background (round 5)
  ---
  duration_ms: 4.49135
  type: 'test'
  ...
# Subtest: anchors NOTHING — residue: 10.009999 flat uploaded as 10.01, unrounded manual background (round 3)
ok 11 - anchors NOTHING — residue: 10.009999 flat uploaded as 10.01, unrounded manual background (round 3)
  ---
  duration_ms: 2.452145
  type: 'test'
  ...
# Subtest: anchors NOTHING — residue: 10 + 1e-4 bump, linear background (round 2)
ok 12 - anchors NOTHING — residue: 10 + 1e-4 bump, linear background (round 2)
  ---
  duration_ms: 2.670744
  type: 'test'
  ...
# Subtest: anchors NOTHING — collapsed model: 30-count bump, manual background over-estimated at 1020 (round 1)
ok 13 - anchors NOTHING — collapsed model: 30-count bump, manual background over-estimated at 1020 (round 1)
  ---
  duration_ms: 1.914925
  type: 'test'
  ...
# Subtest: anchors the correction — resolved 0.0058 line on a zero background, 17 samples survive the upload (round 5)
ok 14 - anchors the correction — resolved 0.0058 line on a zero background, 17 samples survive the upload (round 5)
  ---
  duration_ms: 2.019864
  type: 'test'
  ...
# Subtest: anchors the correction — resolved 50-count line on a noise-free 1e6 background (round 4)
ok 15 - anchors the correction — resolved 50-count line on a noise-free 1e6 background (round 4)
  ---
  duration_ms: 1.502487
  type: 'test'
  ...
# Subtest: anchors the correction — resolved 10 000-count line on a steep noisy ramp, 100 scans averaged (round 2)
ok 16 - anchors the correction — resolved 10 000-count line on a steep noisy ramp, 100 scans averaged (round 2)
  ---
  duration_ms: 2.017559
  type: 'test'
  ...
# Subtest: anchors the correction — resolved 10 000-count anchor behind a 300 000-count one-channel spike (round 3)
ok 17 - anchors the correction — resolved 10 000-count anchor behind a 300 000-count one-channel spike (round 3)
  ---
  duration_ms: 1.781305
  type: 'test'
  ...
# Subtest: anchors the correction — ordinary C 1s: 86 000-count graphite line with Poisson noise
ok 18 - anchors the correction — ordinary C 1s: 86 000-count graphite line with Poisson noise
  ---
  duration_ms: 1.501186
  type: 'test'
  ...
# Subtest: an anchor amplitude of 0 is refused before anything is computed
ok 19 - an anchor amplitude of 0 is refused before anything is computed
  ---
  duration_ms: 0.959908
  type: 'test'
  ...
# Subtest: an anchor amplitude of -5 is refused before anything is computed
ok 20 - an anchor amplitude of -5 is refused before anything is computed
  ---
  duration_ms: 1.340172
  type: 'test'
  ...
# Subtest: an anchor amplitude of NaN is refused before anything is computed
ok 21 - an anchor amplitude of NaN is refused before anything is computed
  ---
  duration_ms: 0.874942
  type: 'test'
  ...
# Subtest: an anchor amplitude of Infinity is refused before anything is computed
ok 22 - an anchor amplitude of Infinity is refused before anything is computed
  ---
  duration_ms: 0.942779
  type: 'test'
  ...
# Subtest: a response that lacks the fitted data or the component curve cannot vouch for an anchor
ok 23 - a response that lacks the fitted data or the component curve cannot vouch for an anchor
  ---
  duration_ms: 2.256807
  type: 'test'
  ...
# Subtest: an exact fit that needs the component is supported (chi-square with it is zero)
ok 24 - an exact fit that needs the component is supported (chi-square with it is zero)
  ---
  duration_ms: 1.676821
  type: 'test'
  ...
# Subtest: removing a component that costs nothing is the definition of unsupported
ok 25 - removing a component that costs nothing is the definition of unsupported
  ---
  duration_ms: 1.515467
  type: 'test'
  ...
# Subtest: the support check precedes every write of the charge-correction inputs
ok 26 - the support check precedes every write of the charge-correction inputs
  ---
  duration_ms: 0.509463
  type: 'test'
  ...
# Subtest: the fallback "first peak" anchor is held to the same rule
ok 27 - the fallback "first peak" anchor is held to the same rule
  ---
  duration_ms: 1.156103
  type: 'test'
  ...
# Subtest: rolling back to a Custom reference shows its target field again
ok 28 - rolling back to a Custom reference shows its target field again
  ---
  duration_ms: 0.868403
  type: 'test'
  ...
# Subtest: every module-level mutable is allowlisted with a valid non-C class
ok 29 - every module-level mutable is allowlisted with a valid non-C class
  ---
  duration_ms: 172.827122
  type: 'test'
  ...
# Subtest: inherited property names and anonymous-class names cannot slip through the allowlist
ok 30 - inherited property names and anonymous-class names cannot slip through the allowlist
  ---
  duration_ms: 78.055656
  type: 'test'
  ...
# Subtest: the known class-C holders are gone from module scope
ok 31 - the known class-C holders are gone from module scope
  ---
  duration_ms: 7.249307
  type: 'test'
  ...
# Subtest: async operations capture their owning record before the first await
ok 32 - async operations capture their owning record before the first await
  ---
  duration_ms: 2.085257
  type: 'test'
  ...
# Subtest: undo/redo and Find Peaks apply read the ACTIVE tab record only
ok 33 - undo/redo and Find Peaks apply read the ACTIVE tab record only
  ---
  duration_ms: 0.559231
  type: 'test'
  ...
# Subtest: an ROI inside the data: no hint
ok 34 - an ROI inside the data: no hint
  ---
  duration_ms: 7.263618
  type: 'test'
  ...
# Subtest: an ROI past the data by more than one step: the quiet hint names the window actually used
ok 35 - an ROI past the data by more than one step: the quiet hint names the window actually used
  ---
  duration_ms: 4.052992
  type: 'test'
  ...
# Subtest: one side past the data is enough; the window named is the selected data
ok 36 - one side past the data is enough; the window named is the selected data
  ---
  duration_ms: 2.871691
  type: 'test'
  ...
# Subtest: a sub-step overshoot (a toFixed(1) rounding of the data edge) is not "past the data"
ok 37 - a sub-step overshoot (a toFixed(1) rounding of the data edge) is not "past the data"
  ---
  duration_ms: 4.203906
  type: 'test'
  ...
# Subtest: min above max: amber, no data selected (getROIData selects nothing)
ok 38 - min above max: amber, no data selected (getROIData selects nothing)
  ---
  duration_ms: 4.370126
  type: 'test'
  ...
# Subtest: an ROI that misses the data entirely: amber, names the data range
ok 39 - an ROI that misses the data entirely: amber, names the data range
  ---
  duration_ms: 2.059342
  type: 'test'
  ...
# Subtest: empty fields mean the full range (as getROIData): no hint
ok 40 - empty fields mean the full range (as getROIData): no hint
  ---
  duration_ms: 1.898464
  type: 'test'
  ...
# Subtest: the window is in the CORRECTED frame (raw − ccShift), as the fit and Find Peaks use it
ok 41 - the window is in the CORRECTED frame (raw − ccShift), as the fit and Find Peaks use it
  ---
  duration_ms: 4.582925
  type: 'test'
  ...
# Subtest: a descending acquisition behaves the same
ok 42 - a descending acquisition behaves the same
  ---
  duration_ms: 2.67966
  type: 'test'
  ...
# Subtest: centre outside the SELECTED data is flagged; inside, at the edges, or with no data selected is not
ok 43 - centre outside the SELECTED data is flagged; inside, at the edges, or with no data selected is not
  ---
  duration_ms: 4.642251
  type: 'test'
  ...
# Subtest: the helpers write nothing: no assignment to a field value, a peak or the fit state
ok 44 - the helpers write nothing: no assignment to a field value, a peak or the fit state
  ---
  duration_ms: 1.826799
  type: 'test'
  ...
# Subtest: the fit and Find Peaks still read the ROI exactly as before (getROIData / the two field values)
ok 45 - the fit and Find Peaks still read the ROI exactly as before (getROIData / the two field values)
  ---
  duration_ms: 1.784972
  type: 'test'
  ...
# Subtest: an unsupported component: the badge warns without reporting its suppressed centre
ok 46 - an unsupported component: the badge warns without reporting its suppressed centre
  ---
  duration_ms: 2.65355
  type: 'test'
  ...
# Subtest: manual fit and Find Peaks select the same points whenever no energy lies within 5e-5 eV of an ROI edge
ok 47 - manual fit and Find Peaks select the same points whenever no energy lies within 5e-5 eV of an ROI edge
  ---
  duration_ms: 8.46813
  type: 'test'
  ...
# Subtest: …and can differ by one edge point, IN EITHER DIRECTION, when an energy lies within 5e-5 eV of an edge (pre-existing, logged, not changed)
ok 48 - …and can differ by one edge point, IN EITHER DIRECTION, when an energy lies within 5e-5 eV of an edge (pre-existing, logged, not changed)
  ---
  duration_ms: 5.498012
  type: 'test'
  ...
1..48
# tests 48
# suites 0
# pass 48
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 390.365058

exec
/bin/zsh -lc "nl -ba docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch | sed -n '1,60p'; nl -ba docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch | sed -n '110,205p'; rg -n 'filtered_dominant_alternative' templates/index.html autofit/methods/*.py; rg -n 'orphan_peaks=' autofit/engine.py; git status --short" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
     1	diff --git a/autofit/confidence.py b/autofit/confidence.py
     2	index bb74778..ab2897f 100644
     3	--- a/autofit/confidence.py
     4	+++ b/autofit/confidence.py
     5	@@ -83,6 +83,9 @@ def _max_correlation(report: ModelReport, role: str) -> Optional[float]:
     6	     return float(np.max(sub)) if sub.size else None
     7	 
     8	 
     9	+from fitting import SUPPORT_MIN_F as _SUPPORT_MIN_F  # F3: one threshold, the server's
    10	+
    11	+
    12	 def build_confidence_vector(
    13	     report: ModelReport,
    14	     role: str,
    15	@@ -96,12 +99,19 @@ def build_confidence_vector(
    16	                 if h.startswith(f"{role}:")]
    17	 
    18	     amplitude = float(comp.amplitude) if comp is not None else None
    19	-    floor = detection_floor_multiple * noise_floor
    20	+    # F3 (2026-09-27): detectability is the support F test on the fit
    21	+    # (fitting._component_support, the server's statistic), not multiples of an
    22	+    # absolute 1-count floor. above_floor = supported (F >= SUPPORT_MIN_F);
    23	+    # present_but_poorly_constrained = the fit gains from it but not
    24	+    # significantly; not_confidently_detected = removing it costs nothing.
    25	+    support = getattr(comp, "support", None) if comp is not None else None
    26	     if amplitude is None:
    27	         detect_status = "not_fitted"
    28	-    elif amplitude >= floor:
    29	+    elif support is None:
    30	+        detect_status = "above_floor" if amplitude > 0 else "not_confidently_detected"
    31	+    elif support.get("supported"):
    32	         detect_status = "above_floor"
    33	-    elif amplitude > noise_floor:
    34	+    elif (support.get("delta_chi2") or 0.0) > 0:
    35	         detect_status = "present_but_poorly_constrained"
    36	     else:
    37	         detect_status = "not_confidently_detected"
    38	@@ -122,9 +132,9 @@ def build_confidence_vector(
    39	         },
    40	         "detectability": {
    41	             "amplitude": amplitude,
    42	-            "noise_floor": noise_floor,
    43	-            "floor_multiple": detection_floor_multiple,
    44	-            "floor_multiple_is_tunable": True,
    45	+            "basis": "support_f_test",       # F3: fitting._component_support, F >= SUPPORT_MIN_F
    46	+            "support_f": (support or {}).get("f"),
    47	+            "support_min_f": _SUPPORT_MIN_F,
    48	             "status": detect_status,
    49	         },
    50	         "identifiability": {
    51	diff --git a/autofit/engine.py b/autofit/engine.py
    52	index dbf4fd7..e1a729e 100644
    53	--- a/autofit/engine.py
    54	+++ b/autofit/engine.py
    55	@@ -36,6 +36,7 @@ from typing import Callable, Optional
    56	 
    57	 import numpy as np
    58	 from lmfit import Model, Parameters
    59	+import fitting as _fitting  # F3: the server's support statistic, one definition
    60	 from lmfit.model import ModelResult
   110	+
   111	+
   112	+def _occupies(comp: "FittedComponent") -> bool:
   113	+    """A slot is occupied by a component the data support (F3). No threshold
   114	+    on any data-scaled quantity: the support F test where a fit is behind the
   115	+    component, else the sign of its amplitude."""
   116	+    if comp.support is not None:
   117	+        # PROBE (likelihood-ratio variant, not for shipping): the Poisson-weighted
   118	+        # chi-square gain per free parameter, NOT normalised by the fit's misfit
   119	+        d = comp.support.get("delta_chi2") or 0.0
   120	+        return bool(d > 0 and d / max(1, comp.support.get("_p", 1)) >= _fitting.SUPPORT_MIN_F)
   121	+    return comp.amplitude > 0
   122	+
   123	+
   124	 def _extract_fitted_components(
   125	     result: ModelResult, model: CandidateModel
   126	 ) -> list[FittedComponent]:
   127	     out: list[FittedComponent] = []
   128	+    supports = _component_supports(result)
   129	     for slot in model.slots:
   130	         prefix = _slot_prefix(slot.role)
   131	         pars = result.params
   132	@@ -676,6 +728,7 @@ def _extract_fitted_components(
   133	             slot_role=slot.role, position=center, fwhm=fwhm,
   134	             amplitude=amplitude, shape_params=shape_params,
   135	             line_shape=slot.line_shape,
   136	+            support=supports.get(prefix),
   137	         ))
   138	     return out
   139	 
   140	@@ -1055,7 +1108,7 @@ def match_components_to_slots(
   141	                                       (bound_overrides or {}).get(slot.role))
   142	         return (lo <= comp.position <= hi
   143	                 and slot.fwhm_range[0] <= comp.fwhm <= slot.fwhm_range[1]
   144	-                and comp.amplitude > noise_floor)
   145	+                and _occupies(comp))       # F3: supported by the data, not amplitude > 1 count
   146	 
   147	     def _window_center(slot: ComponentSlot) -> float:
   148	         # NEVER the widened bound (Codex-caught, round 2): this is a
   149	@@ -1077,7 +1130,7 @@ def match_components_to_slots(
   150	             orphans.append(FittedComponent(
   151	                 slot_role="unmatched", position=comp.position, fwhm=comp.fwhm,
   152	                 amplitude=comp.amplitude, shape_params=comp.shape_params,
   153	-                line_shape=comp.line_shape,
   154	+                line_shape=comp.line_shape, support=comp.support,
   155	             ))
   156	             continue
   157	 
   158	@@ -1095,7 +1148,7 @@ def match_components_to_slots(
   159	         claimed = FittedComponent(
   160	             slot_role=best_slot.role, position=comp.position, fwhm=comp.fwhm,
   161	             amplitude=comp.amplitude, shape_params=comp.shape_params,
   162	-            line_shape=comp.line_shape,
   163	+            line_shape=comp.line_shape, support=comp.support,
   164	         )
   165	         if incumbent is None:
   166	             slot_map[best_slot.role] = claimed
   167	@@ -2229,8 +2282,10 @@ def _attempt_proposal(
   168	     # to a wall (Codex fwhm-cap review, run B BLOCKER).
   169	     width_cap_hit = f"{spec.role}:fwhm@max"
   170	     pr.boundary_hits = _proposed_slot_pegs(primary, spec.role)
   171	-    if comp.amplitude <= noise_floor:
   172	-        return _fast(f"amplitude {comp.amplitude:.1f} ≤ noise_floor {noise_floor:.1f}")
   173	+    if not _occupies(comp):
   174	+        f = (comp.support or {}).get("f")
   175	+        return _fast("not supported by the data (removing it does not make the fit significantly worse"
   176	+                     + (f", F = {f:.2f} < {_fitting.SUPPORT_MIN_F:.0f}" if f is not None else "") + ")")
   177	     spurious_hits = [h for h in pr.boundary_hits if h != width_cap_hit]
   178	     if spurious_hits:
   179	         return _fast(f"proposed slot boundary pegs: {spurious_hits}")
   180	diff --git a/autofit/grammar.py b/autofit/grammar.py
   181	index c9a85cd..bed2606 100644
   182	--- a/autofit/grammar.py
   183	+++ b/autofit/grammar.py
   184	@@ -181,11 +181,15 @@ class ComponentSlot:
   185	     broad_justification: Optional[str] = None
   186	 
   187	     def contains(self, be: float, fwhm: float, amplitude: float,
   188	-                 noise_floor: float) -> bool:
   189	+                 noise_floor: float = 0.0) -> bool:
   190	+        # F3 (2026-09-27): occupancy is decided by the support F test on the
   191	+        # fit (engine._occupies); this geometric check keeps only the sign of
   192	+        # the amplitude. ``noise_floor`` is accepted and ignored (no caller in
   193	+        # the engine passes it any more).
   194	         return (
   195	             self.be_window[0] <= be <= self.be_window[1]
   196	             and self.fwhm_range[0] <= fwhm <= self.fwhm_range[1]
   197	-            and amplitude > noise_floor
   198	+            and amplitude > 0
   199	         )
   200	 
   201	 
autofit/methods/ic_model_comparison.py:184:                "filtered_dominant_alternative":
autofit/methods/ic_model_comparison.py:185:                    result.filtered_dominant_alternative,
autofit/methods/ic_model_comparison.py:197:                f"{result.filtered_dominant_alternative['name']} beats this "
autofit/methods/ic_model_comparison.py:199:                f"{result.filtered_dominant_alternative['delta_bic_vs_winner']:.1f} "
autofit/methods/ic_model_comparison.py:201:                f"({result.filtered_dominant_alternative['filter_reason']})"
autofit/methods/ic_model_comparison.py:202:                if result.filtered_dominant_alternative else "")
autofit/methods/ic_model_comparison.py:341:        "filtered_dominant_alternative": result.filtered_dominant_alternative,
templates/index.html:15523:  if (d.filtered_dominant_alternative) {
templates/index.html:15524:    const fda = d.filtered_dominant_alternative;
templates/index.html:16196:  if (d.filtered_dominant_alternative) {
templates/index.html:16197:    const f = d.filtered_dominant_alternative;
2325:            orphan_peaks=stability.orphan_rate > 0.1,
2467:            orphan_peaks=stability.orphan_rate > 0.1,
2853:                orphan_peaks=stability.orphan_rate > 0.1,
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-jSFEY0n6' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-JrUTKQDj' (errno=Operation not permitted)
?? docs/autofit/codex/f3_c1s_gate_verdict_runA.md
?? docs/autofit/codex/f3_c1s_gate_verdict_runB.md

exec
/bin/zsh -lc "rg -n 'auto-fit-c1s-confirm|keydown|focus\\(|inert|trapFocus|aria-modal' templates/index.html | head -55; sed -n '15515,15540p' templates/index.html; sed -n '16188,16208p' templates/index.html; sed -n '1590,1615p' templates/index.html; sed -n '2570,2605p' autofit/engine.py; rg -n 'weights =|weights:' autofit/methods/ic_model_comparison.py autofit/engine.py | tail -15; nl -ba tests/js/autofit_c1s_gate.test.js | tail -16" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
3198:      color: '#7a7a7a',           // inert — stack tabs render no dot
3744:    fresh.addEventListener('keydown', (e) => {
5688:  setTimeout(() => input.focus(), 50);
5863:document.addEventListener('keydown', function(e) {
6583:// see why their checkbox appears inert. Identical pattern to how
6607:  // is empty/inert for stack tabs so the spectrum-mode gating would
6654:  // Skip stack tabs — their ui block is inert and bg-sub is a view-mode
6740:    const span = document.getElementById('auto-fit-c1s-confirm-count');
6742:    const proceed = document.getElementById('auto-fit-c1s-confirm-proceed');
6744:      document.getElementById('auto-fit-c1s-confirm-overlay').classList.remove('open');
6748:    document.getElementById('auto-fit-c1s-confirm-overlay').classList.add('open');
6752:  document.getElementById('auto-fit-c1s-confirm-overlay').classList.remove('open');
9376:// is empty/inert), so the bg-sub gate is just the pill's checked state.
10447:  fnameInput.focus();
13105:        ' onkeydown="if(event.key===\'Enter\'||event.key===\' \'){event.preventDefault();_refToggleElement(\'' + a + '\')}">×</button>' +
13152:  if (_refChipOpenSym === sym) { _refCloseChipDropdown(); if (btn) btn.focus(); return; }
13158:  document.addEventListener('keydown', _refChipEsc, true);
13165:  document.removeEventListener('keydown', _refChipEsc, true);
13176:  if (e.key === 'Escape') { const b = _refChipOpenBtn; _refCloseChipDropdown(); if (b) b.focus(); }
13226:        'onclick="_refBlendedPick(this)" onkeydown="if(event.key===\'Enter\'){event.preventDefault();_refBlendedPick(this)}">' +
13399:        ' onkeydown="if(event.key===\'Enter\'||event.key===\' \'){event.preventDefault();_refToggleElement(\'' + e.sym + '\')}"' : '') +
13558:    'onkeydown="if(event.key===\'Escape\'){_refCloseSearch()}" ' +
14704:  setTimeout(() => input.focus(), 30);
14798:document.getElementById('spec-combo-search').addEventListener('keydown', function(e) {
14870:      <input type="text" id="save-fname" placeholder="filename" onkeydown="if(event.key==='Enter')confirmSave()">
14924:<div id="auto-fit-c1s-confirm-overlay" class="xps-modal-overlay" onclick="if(event.target===this)this.classList.remove('open')">
14930:      This tab has <span id="auto-fit-c1s-confirm-count">0</span> peak(s) and a fit result.
14935:      <button class="btn btn-accent" id="auto-fit-c1s-confirm-proceed">Proceed</button>
15764:          ` onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();_fpToggleElementExpand('${el.sym}')}"`
15802:      ` onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();_fpToggleRegion('${_fpEsc(e.region)}', event.ctrlKey||event.metaKey)}"` +
15826:      ` onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();_fpPickFromSearch('${_fpEsc(o.value)}', event.ctrlKey||event.metaKey)}">` +
        `options (${_fpModelLabel(d.winner)}). It hit some parameter ` +
        `limits (${hits || 'see below'}) — worth double-checking those components.`);
    }
  }
  if ((d.winner_unphysical_widths || []).length) {
    const widths = d.winner_unphysical_widths.map(_fpWidthFlagLabel).join('; ');
    parts.push(`LOW CONFIDENCE: ${widths}.`);
  }
  if (d.filtered_dominant_alternative) {
    const fda = d.filtered_dominant_alternative;
    parts.push(`Note: a different model (${_fpModelLabel(fda.name)}) scored ` +
      `better by ${(+fda.delta_bic_vs_winner).toFixed(1)} points but was set ` +
      `aside (${_fpFilterReasonLabel(fda.filter_reason).toLowerCase()}) — ` +
      'worth a look in the comparison table.');
  }
  if (d.analysis_truncated) {
    parts.push(`Only ${d.n_candidates_evaluated} of ${d.n_candidates_total} ` +
      'candidate models were checked before time ran out.');
  }
  if (!parts.length) {
    parts.push('This model passed every check cleanly — stable across ' +
      're-fits, no parameter limits hit, no unexplained extra peaks.');
  }
  return parts.join(' ');
}

    } else {
      const hits = (d.winner_boundary_hits || [])
        .map(h => _fpParamLabel('s_' + String(h).replace(':', '_')
                                .replace(/@(min|max)$/, ''))).join(', ');
      flags.push(_fpBanner(_fpEsc(_fpFmt(B.constraintBind,
        { details: hits || 'see Technical details' })), '#e0a030'));
    }
  }
  if (d.filtered_dominant_alternative) {
    const f = d.filtered_dominant_alternative;
    flags.push(_fpBanner('&#9888; ' + _fpEsc(_fpFmt(B.hiddenBetter, {
      name: _fpModelLabel(f.name),
      reason: _fpFilterReasonLabel(f.filter_reason).toLowerCase(),
    })), '#e05555'));
  }
  if (a.ambiguous_pairs && a.ambiguous_pairs.length)
    flags.push(_fpBanner(_fpEsc(_fpFmt(B.tooCloseToCall, {
      pairs: a.ambiguous_pairs
        .map(p => _fpModelLabel(p[0]) + ' vs ' + _fpModelLabel(p[1]))
        .join('; '),
    })), '#e0a030'));
  }
  .xps-modal h3 {
    margin: 0 0 14px 0; font-family: var(--mono); font-size: 13px;
    color: var(--text); font-weight: 500;
    display: flex; justify-content: space-between; align-items: center;
  }
  .xps-modal label { font-size: 11px; color: var(--text2); margin-bottom: 4px; display: block; }
  .xps-modal input[type=text], .xps-modal input[type=number], .xps-modal select {
    width: 100%; font-family: var(--mono); font-size: 12px;
    padding: 6px 10px; margin-bottom: 10px;
    background: var(--bg3); border: 1px solid var(--border2); border-radius: var(--radius);
    color: var(--text); box-sizing: border-box;
  }
  .xps-modal input:focus, .xps-modal select:focus { border-color: var(--accent); outline: none; }
  .xps-modal .dialog-btns { display: flex; gap: 8px; justify-content: flex-end; margin-top: 10px; }
  .xps-modal .row2 { display: flex; gap: 10px; }
  .xps-modal .row2 > div { flex: 1; }
  .xps-modal .chk-row { display: flex; align-items: center; gap: 6px; margin-bottom: 8px; font-size: 11px; color: var(--text2); cursor: pointer; }
  .xps-modal .chk-row input { width: auto; margin: 0; }
  .xps-modal .section-label {
    font-size: 9px; text-transform: uppercase; letter-spacing: 0.08em;
    color: var(--text3); margin: 10px 0 6px; font-family: var(--mono);
  }

  /* ── Shortcuts modal ────────────────────────────────────── */
  .shortcut-row { display: flex; gap: 8px; margin-bottom: 7px; align-items: center; }

    ``endpoint_avg`` (Find Peaks honours the Background panel, 2026-09-08 —
    F3 round two): number of channels averaged at each window edge before
    the background anchors are read; threaded to every fit_candidate /
    _compute_background call below (screen, primary, stability refits,
    proposals, bound-fixed refits, decisive override, detection). Default 1
    keeps every committed fixture byte-stable.

    ``fit_full_window`` (Find Peaks UI, 2026-07-13): OPTIONAL, default
    False — zero behavior change for every existing caller. When True,
    relaxes each candidate's primary-slot center bound per
    ``_full_window_bound_overrides`` (outer envelope only for curated
    multi-component models; full ROI for detection/structural-fallback
    slots) instead of the region module's fixed literature window.
    Threaded through every place a candidate's initial/refit parameters
    get built from scratch (screen fit, deep-phase primary fit, stability
    refits, the proposal pass, and the bound-fixed decisive-override
    refit) so the relaxed bound is consistent across a candidate's whole
    lifecycle.

    ``candidate_filter`` limits the run to the named candidates (useful for
    fast tests / method options); None = all.  ``enable_preseed`` gates the
    pre-fit out-of-grammar dominant seeding (unit F1) — detection-driven, so
    it is a no-op on spectra whose prominent features the grammar covers.

    ``progress_cb`` (Find Peaks UI, 2026-07-11): OPTIONAL, default None —
    zero behavior/perf change for every existing caller.  When given, it is
    invoked with ``{"phase": "screening"|"stabilizing", "candidate_index",
    "candidate_total", "candidate_name"}`` right before each candidate's
    fit — the REAL screen->stabilize sweep progress (unit F3), not a fake
    animation.  A raising callback is swallowed (never lets a progress sink
    break the analysis — the honesty/result contract outranks the nicety).
    """
    candidates = grammar.candidates
    if candidate_filter is not None:
        wanted = set(candidate_filter)
autofit/methods/ic_model_comparison.py:40:        weights: Optional[np.ndarray] = None,
autofit/engine.py:855:    weights: np.ndarray,
autofit/engine.py:879:    weights = np.asarray(weights, dtype=float)
autofit/engine.py:1165:    weights: np.ndarray,
autofit/engine.py:2160:    weights: np.ndarray,
autofit/engine.py:2388:    weights: np.ndarray,
autofit/engine.py:2482:    weights: np.ndarray,
autofit/engine.py:2552:    weights: np.ndarray,
    52	  // 380-395, which exists — judged as C 1s; a window the shifted data do not reach selects nothing
    53	  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 100, ui: { roiMin: '280', roiMax: '295' } }), true);
    54	  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 200, ui: { roiMin: '280', roiMax: '295' } }), false,
    55	    'corrected 70-220 has no point in 280-295: nothing selected');
    56	  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: {} }), false, 'no window: the whole 270-420 scan, midpoint 345');
    57	  assert.strictEqual(g({ id: 't1', rawBE: [], ui: {} }), false);
    58	});
    59	
    60	test('every caller of the gate is for the active tab (menu state, charge-reference permission, the Auto-Fit run)', () => {
    61	  for (const fn of ['_recomputeAutoFitMenuState', '_isChargeRefAllowed', 'runAutoFitC1sGraphite']) {
    62	    assert.match(extractFn(fn), /isC1sTab\(tab\)/, fn);
    63	  }
    64	  // and the ROI fields refresh the menu on every keystroke
    65	  assert.match(html, /id="roi-min"[^>]*oninput="updatePlot\(\);_recomputeAutoFitMenuState\(\)"/);
    66	  assert.match(html, /id="roi-max"[^>]*oninput="updatePlot\(\);_recomputeAutoFitMenuState\(\)"/);
    67	});

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile
tempfile.tempdir='\\''/tmp'\\''
import numpy as np
from fitting import _component_support
for scale in (1,.1):
 y=np.array([100.,100.])*scale; fit=np.array([90.,110.])*scale; comp=np.array([40.,40.])*scale
 s=_component_support(y,fit,comp,1/np.sqrt(np.maximum(y,1)),1,1)
 print('\\''scale'\\'',scale,'\\''support'\\'',s,'\\''LR occupied'\\'',s['\\''delta_chi2'\\'']>=10)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 1628ms:
/Users/skyefortier/.matplotlib is not a writable directory
scale 1 support {'f': 16.0, 'delta_chi2': 32.00000000000001, 'supported': True} LR occupied True
scale 0.1 support {'f': 15.999999999999998, 'delta_chi2': 3.1999999999999997, 'supported': True} LR occupied False

codex
No BLOCKER found in the shipped gate. The parked proposals need further work.

- **MAJOR — parked LR is not invariant to intensity rescaling.** [README.md:33](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:33), [LR patch:120](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch:120). Dimensionless does not imply scale-free. Reproduced with `y=[100,100]`, fit `[90,110]`, component `[40,40]`, and one free parameter: Δχ²/p = 32, F = 16. Multiply every intensity by 0.1: Δχ²/p = 3.2, F remains 16. LR changes from occupied to absent; every count remains above the variance floor. This matters for unit normalization, independently of legitimately collecting fewer counts. Also, the implemented statistic is a weighted component-removal gain with other components held fixed, not a refitted Poisson likelihood-ratio test.

- **MAJOR — parked LR reports a different decision rule from the one it uses.** [LR patch:31](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch:31), [LR patch:173](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch:173). Detectability still consumes `support.supported` and advertises `support_f_test`. In the scaled example above, occupancy rejects the component while detectability says `above_floor`; proposal rejection can literally report **“F = 16.00 < 10.”** Carry the chosen statistic, threshold, verdict, and basis consistently through occupancy, confidence, and rejection messages. Both variants also mislabel the positive-amplitude fallback as an F-test result when no support statistic exists.

- **MAJOR — both parked patches retain the conflation of absence with an unexplained extra peak.** [F patch:141](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/variant_F_support_test.patch:141), [LR patch:145](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch:145). A component rejected by `_occupies` has no accepting slot and becomes an orphan. An unsupported optional component recurring across refits therefore produces `orphan_rate=1`, triggering a plausibility violation even when absent-slot handling excludes it from active persistence. This behavior predates the proposals, but replacing occupancy expands its consequences. Unsupported components and supported components that cannot be assigned need distinct treatment.

- **MINOR — inactive-record selection disagrees with the actual fit.** [index.html:7770](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/templates/index.html:7770). On a 270–420 eV scan, saved bounds `295,280` return **true** through the record path, while the active path selects nothing and returns **false**. Bounds `'',295` produce the opposite disagreement: the active selection is 270–295 and passes; the record path uses the entire scan and fails. Preserve bound order and default missing bounds independently, matching `getROIData()`. This is nonblocking because all three production callers currently supply the active tab.

- **MINOR — the parked write-up overstates what the stress failure demonstrates.** [README.md:48](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:48). F does return `conditional:false`, but also returns `filtered_dominant_alternative` naming P3 with ΔBIC ≈ 152.95; the page displays that warning. It does not silently produce an entirely unqualified answer. Moreover, this fixture contains **two true peaks**: P3’s third component compensates for background mismatch. Calling it a rejected “real component” is unsupported.

I reproduced the central measurements by loading each patch’s source **in memory**, without applying either patch:

| Variant | Winner | Conditional | P3 minimum persistence |
|---|---|---:|---:|
| Baseline | P3+bfix | true | 1 |
| F | P2 | false | 0 |
| LR | P3+bfix | true | 1 |

P3’s third component has F ≈ **9.417**, Δχ² ≈ **10,702**, and four free parameters. The extraction → matching → persistence → decisive-override explanation is correct. The claimed complete suite totals were not independently rerun.

**I would choose F as the starting variant for the stated scale-free requirement**, then repair the absence/orphan distinction and the honesty behavior before shipping it. Neither patch is ready unchanged. LR’s passing existing gates does not establish scale invariance. Leaving the variance floor alone preserves the existing weighting convention, but neither proposal should promise arbitrary-unit invariance across that floor. The `grammar.contains` change has no internal callers and is consistent with a sign-only geometric check; it should not be presented as a support verdict.

For the shipped gate, all three callers resolve the active record. Tab activation restores data and fields before evaluating it. Stack tabs fail closed; survey tabs retain the midpoint rule. The active path correctly inherits corrected energies, inclusive clipping, independently blank bounds, and empty/reversed-window behavior. Blank ROI fields still permit Auto-Fit on a narrow C1s scan. A million-point inactive record completed without argument-spread failure, taking approximately 102 ms here, though its intermediate arrays are avoidable.

Validation: **48 relevant JS tests passed**. Running the four new tests against the old implementation produced **three failures**, confirming substantive regression coverage. The fourth test only checks source patterns; it does not prove active-tab identity or caller timing. No files were changed.

VERDICT: GO
tokens used
81,417
No BLOCKER found in the shipped gate. The parked proposals need further work.

- **MAJOR — parked LR is not invariant to intensity rescaling.** [README.md:33](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:33), [LR patch:120](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch:120). Dimensionless does not imply scale-free. Reproduced with `y=[100,100]`, fit `[90,110]`, component `[40,40]`, and one free parameter: Δχ²/p = 32, F = 16. Multiply every intensity by 0.1: Δχ²/p = 3.2, F remains 16. LR changes from occupied to absent; every count remains above the variance floor. This matters for unit normalization, independently of legitimately collecting fewer counts. Also, the implemented statistic is a weighted component-removal gain with other components held fixed, not a refitted Poisson likelihood-ratio test.

- **MAJOR — parked LR reports a different decision rule from the one it uses.** [LR patch:31](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch:31), [LR patch:173](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch:173). Detectability still consumes `support.supported` and advertises `support_f_test`. In the scaled example above, occupancy rejects the component while detectability says `above_floor`; proposal rejection can literally report **“F = 16.00 < 10.”** Carry the chosen statistic, threshold, verdict, and basis consistently through occupancy, confidence, and rejection messages. Both variants also mislabel the positive-amplitude fallback as an F-test result when no support statistic exists.

- **MAJOR — both parked patches retain the conflation of absence with an unexplained extra peak.** [F patch:141](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/variant_F_support_test.patch:141), [LR patch:145](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch:145). A component rejected by `_occupies` has no accepting slot and becomes an orphan. An unsupported optional component recurring across refits therefore produces `orphan_rate=1`, triggering a plausibility violation even when absent-slot handling excludes it from active persistence. This behavior predates the proposals, but replacing occupancy expands its consequences. Unsupported components and supported components that cannot be assigned need distinct treatment.

- **MINOR — inactive-record selection disagrees with the actual fit.** [index.html:7770](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/templates/index.html:7770). On a 270–420 eV scan, saved bounds `295,280` return **true** through the record path, while the active path selects nothing and returns **false**. Bounds `'',295` produce the opposite disagreement: the active selection is 270–295 and passes; the record path uses the entire scan and fails. Preserve bound order and default missing bounds independently, matching `getROIData()`. This is nonblocking because all three production callers currently supply the active tab.

- **MINOR — the parked write-up overstates what the stress failure demonstrates.** [README.md:48](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:48). F does return `conditional:false`, but also returns `filtered_dominant_alternative` naming P3 with ΔBIC ≈ 152.95; the page displays that warning. It does not silently produce an entirely unqualified answer. Moreover, this fixture contains **two true peaks**: P3’s third component compensates for background mismatch. Calling it a rejected “real component” is unsupported.

I reproduced the central measurements by loading each patch’s source **in memory**, without applying either patch:

| Variant | Winner | Conditional | P3 minimum persistence |
|---|---|---:|---:|
| Baseline | P3+bfix | true | 1 |
| F | P2 | false | 0 |
| LR | P3+bfix | true | 1 |

P3’s third component has F ≈ **9.417**, Δχ² ≈ **10,702**, and four free parameters. The extraction → matching → persistence → decisive-override explanation is correct. The claimed complete suite totals were not independently rerun.

**I would choose F as the starting variant for the stated scale-free requirement**, then repair the absence/orphan distinction and the honesty behavior before shipping it. Neither patch is ready unchanged. LR’s passing existing gates does not establish scale invariance. Leaving the variance floor alone preserves the existing weighting convention, but neither proposal should promise arbitrary-unit invariance across that floor. The `grammar.contains` change has no internal callers and is consistent with a sign-only geometric check; it should not be presented as a support verdict.

For the shipped gate, all three callers resolve the active record. Tab activation restores data and fields before evaluating it. Stack tabs fail closed; survey tabs retain the midpoint rule. The active path correctly inherits corrected energies, inclusive clipping, independently blank bounds, and empty/reversed-window behavior. Blank ROI fields still permit Auto-Fit on a narrow C1s scan. A million-point inactive record completed without argument-spread failure, taking approximately 102 ms here, though its intermediate arrays are avoidable.

Validation: **48 relevant JS tests passed**. Running the four new tests against the old implementation produced **three failures**, confirming substantive regression coverage. The fourth test only checks source patterns; it does not prove active-tab identity or caller timing. No files were changed.

VERDICT: GO
