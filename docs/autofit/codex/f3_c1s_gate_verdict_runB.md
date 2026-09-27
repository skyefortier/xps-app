OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0e201-e230-7b70-9839-5309b1fba185
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
I’ll trace the gate’s callers and ROI semantics, check whether the tests catch regressions, and review both parked proposals. I’ll keep the verdict focused on the shipped gate change.

exec
/bin/zsh -lc "pwd && rg --files -g 'AGENTS.md' -g 'CLAUDE.md' -g '*autofit_c1s*' -g '*noise-floor*' -g '*2026-09-27-f3*'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
CLAUDE.md
docs/superpowers/plans/2026-09-27-f3-noise-floor-and-c1s-gate.md
tests/js/autofit_c1s_gate.test.js

exec
/bin/zsh -lc 'git status --short && git diff --stat 07e0839..HEAD && git diff 07e0839..HEAD -- templates/index.html tests/js/autofit_c1s_gate.test.js CLAUDE.md docs/superpowers/plans/2026-09-27-f3-noise-floor-and-c1s-gate.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-HINWmcLO' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-2ZN5QDfT' (errno=Operation not permitted)
?? docs/autofit/codex/f3_c1s_gate_verdict_runA.md
?? docs/autofit/codex/f3_c1s_gate_verdict_runB.md
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-P42AE2Dz' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-JGl5pBj2' (errno=Operation not permitted)
 CLAUDE.md                                          |   6 +-
 docs/autofit/codex/f3_c1s_gate_review_prompt.txt   |  11 ++
 docs/findings/noise-floor-occupancy/README.md      |  78 ++++++++
 .../variant_F_support_test.patch                   | 197 ++++++++++++++++++++
 .../variant_LR_likelihood_ratio.patch              | 201 +++++++++++++++++++++
 .../2026-09-27-f3-noise-floor-and-c1s-gate.md      |  43 +++++
 templates/index.html                               |  35 +++-
 tests/js/autofit_c1s_gate.test.js                  |  67 +++++++
 8 files changed, 626 insertions(+), 12 deletions(-)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-cTC7sP1N' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-edjD4xuK' (errno=Operation not permitted)
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

exec
/bin/zsh -lc "rg -n 'isC1sTab|function getROIData|function _isChargeRefAllowed|function _recomputeAutoFitMenuState|async function runAutoFitC1sGraphite|activeId =|switchTab\\(|loadTab|restoreTab' templates/index.html && cat docs/findings/noise-floor-occupancy/README.md && cat docs/findings/noise-floor-occupancy/variant_F_support_test.patch && cat docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
2201:          <div class="tab active" onclick="switchTab(this,'peaks')">Peaks</div>
2202:          <div class="tab" onclick="switchTab(this,'results')">Results</div>
2203:          <div class="tab" onclick="switchTab(this,'quantify')">Quantify</div>
2204:          <div class="tab survey-tab" id="survey-tab-btn" onclick="switchTab(this,'survey')">Survey</div>
3136:    this.activeId = null;
3219:    if (this.activeId === id) return;
3229:    this.activeId = id;
3301:      this.activeId = null;
3327:    if (this.activeId === id) {
3329:      this.activeId = null; // force re-activate
3584:        if (peaksBtn) switchTab(peaksBtn, 'peaks');
5087:function getROIData() {
6099:function _isChargeRefAllowed() {
6105:  return !!(tab && isC1sTab(tab));
6712:function _recomputeAutoFitMenuState() {
6718:  const enabled = !!tab && isC1sTab(tab);
7558:async function runAutoFitC1sGraphite() {
7563:  if (!isC1sTab(tab)) {
7759:function isC1sTab(tab) {
12007:function switchTab(el, name) {
12456:    if (tabManager.activeId === tid) {
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
index dbf4fd7..9bad455 100644
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
@@ -652,10 +664,46 @@ class FitOutcome:
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
+        return bool(comp.support.get("supported"))
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
@@ -676,6 +724,7 @@ def _extract_fitted_components(
             slot_role=slot.role, position=center, fwhm=fwhm,
             amplitude=amplitude, shape_params=shape_params,
             line_shape=slot.line_shape,
+            support=supports.get(prefix),
         ))
     return out
 
@@ -1055,7 +1104,7 @@ def match_components_to_slots(
                                       (bound_overrides or {}).get(slot.role))
         return (lo <= comp.position <= hi
                 and slot.fwhm_range[0] <= comp.fwhm <= slot.fwhm_range[1]
-                and comp.amplitude > noise_floor)
+                and _occupies(comp))       # F3: supported by the data, not amplitude > 1 count
 
     def _window_center(slot: ComponentSlot) -> float:
         # NEVER the widened bound (Codex-caught, round 2): this is a
@@ -1077,7 +1126,7 @@ def match_components_to_slots(
             orphans.append(FittedComponent(
                 slot_role="unmatched", position=comp.position, fwhm=comp.fwhm,
                 amplitude=comp.amplitude, shape_params=comp.shape_params,
-                line_shape=comp.line_shape,
+                line_shape=comp.line_shape, support=comp.support,
             ))
             continue
 
@@ -1095,7 +1144,7 @@ def match_components_to_slots(
         claimed = FittedComponent(
             slot_role=best_slot.role, position=comp.position, fwhm=comp.fwhm,
             amplitude=comp.amplitude, shape_params=comp.shape_params,
-            line_shape=comp.line_shape,
+            line_shape=comp.line_shape, support=comp.support,
         )
         if incumbent is None:
             slot_map[best_slot.role] = claimed
@@ -2229,8 +2278,10 @@ def _attempt_proposal(
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
 
 

exec
/bin/zsh -lc "rg --files -g AGENTS.md /Users/skyefortier/xps-app /Users/skyefortier/.codex 2>/dev/null; rg -n 'extract_fitted_components|match_components_to_slots|rank_and_filter|decisive|detectability|noise_floor|grammar.contains' core tests | head -180; cat CLAUDE.md | head -100" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
rg: core: No such file or directory (os error 2)
tests/test_browser_find_peaks_tooltip_markup.py:30:``decisive_override``-style bound-fixed refit) while giving it a
tests/test_browser_find_peaks_tooltip_markup.py:31:``filter_reason`` — but ``autofit/engine.py``'s ``_apply_decisive_
tests/test_browser_find_peaks_tooltip_markup.py:39:The REAL trigger is ``rank_and_filter()``'s ``no_clean_survivor``
tests/test_browser_find_peaks_tooltip_markup.py:151:# bug: rank_and_filter()'s "no_clean_survivor" conditional tier promotes
tests/test_browser_find_peaks_tooltip_markup.py:156:# name) -- per autofit/engine.py's rank_and_filter and
tests/test_browser_find_peaks_tooltip_markup.py:218:    """The common case (no decisive_override, winner has no
tests/autofit/stress_cases.py:459:        # 2026-07-04 battery measured the EVIDENCE decisively favoring P2
tests/autofit/test_methods_seam.py:72:        "n_refits": 4, "noise_floor": 25.0,
tests/autofit/test_methods_seam.py:104:    assert conf["detectability"]["status"] == "above_floor"
tests/autofit/test_methods_seam.py:121:        "n_refits": 2, "noise_floor": 25.0,
tests/autofit/test_bayesian_method.py:73:    # under-specified K1 decisively rejected; over-specified K3 penalized
tests/autofit/test_bayesian_method.py:119:    |ΔF| ~ 3 — silently, before this machinery).  K1-vs-K2 is decisive
tests/autofit/test_stage2_rereview_findings.py:9:   (was: recorded but ignored by rank_and_filter and dropped from payload);
tests/autofit/test_stage2_rereview_findings.py:23:    rank_and_filter,
tests/autofit/test_stage2_rereview_findings.py:39:                                       noise_floor=1.0, n_refits=3, rng_seed=0)
tests/autofit/test_stage2_rereview_findings.py:56:    res = rank_and_filter([clean, orphaned])
tests/autofit/test_stage2_rereview_findings.py:67:    res = rank_and_filter([orphaned])
tests/autofit/test_stage2_rereview_findings.py:82:                                noise_floor=1.0, n_refits=4, rng_seed=0)
tests/autofit/test_stage2_rereview_findings.py:133:        "n_refits": 4, "noise_floor": 25.0,
tests/autofit/test_preseed_dominants.py:35:IC_OPTS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
tests/autofit/test_preseed_dominants.py:346:        noise_floor=1.0, n_refits=2, rng_seed=0,
tests/autofit/test_preseed_dominants.py:488:        noise_floor=1.0, n_refits=4, rng_seed=0,
tests/autofit/test_b1s_cl2p_parity_gates.py:6:- Cl 2p (both corrected anchors): with the decisive-override rule the
tests/autofit/test_b1s_cl2p_parity_gates.py:33:OPTIONS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
tests/autofit/test_b1s_cl2p_parity_gates.py:88:    # decisive-override path must fire — winner is the bound-fixed refit of
tests/autofit/test_b1s_cl2p_parity_gates.py:93:    assert res.diagnostics["conditional_reason"] == "decisive_override"
tests/autofit/test_b1s_cl2p_parity_gates.py:121:    # fixed-vs-relaxed evidence: the relaxed family is decisively better,
tests/autofit/test_browser_schema_roundtrip.py:136:    "detectability": "above_floor",
tests/autofit/test_candidate_pool_real_gate.py:108:        noise_floor=1.0,
tests/js/find_peaks_plain_message.test.js:181:test('_fpPlainMessage: decisive_override reads CONDITIONAL and names the fixed parameter', () => {
tests/js/find_peaks_plain_message.test.js:185:      conditional_reason: 'decisive_override',
tests/js/find_peaks_plain_message.test.js:191:  assert.doesNotMatch(text, /decisive_override/);
tests/autofit/test_u4f_parity_gate.py:48:OPTIONS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
tests/autofit/test_stress_honesty.py:32:IC_OPTS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
tests/autofit/test_stress_honesty.py:104:    2000 promotes the bound-fixed decoy via decisive_override, k=3,
tests/autofit/test_stress_honesty.py:193:    review): on the high-count sub-FWHM doublet the EVIDENCE decisively
tests/autofit/test_cl2p_freewidth.py:43:OPTIONS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
tests/autofit/test_bayesian_real_gate.py:11:on the boundary-piled ratio chain.  The IC method's decisive-override winner
tests/autofit/test_bayesian_real_gate.py:69:        options={"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
tests/autofit/test_endpoint_avg_wiring.py:57:                        "_attempt_proposal", "_bound_fixed_refit", "_apply_decisive_override",
tests/autofit/test_endpoint_avg_wiring.py:193:    eng.run_stability_analysis(x, y, w, model, primary, noise_floor=1.0, n_refits=2, rng_seed=0, endpoint_avg=7)
tests/autofit/test_candidate_pool.py:36:    noise_floor=1.0,
tests/autofit/test_fit_physics_wiring.py:129:        options={"n_refits": 2, "rng_seed": 0, "noise_floor": 1.0,
tests/autofit/test_c1s_parity_gate.py:121:        options={"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
tests/autofit/test_c1s_parity_gate.py:135:        if res.diagnostics["conditional_reason"] == "decisive_override":
tests/autofit/test_filtered_dominant_flag.py:21:OPTS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
tests/autofit/test_filtered_dominant_flag.py:45:    """Codex analyze review blocker: a decisive-override winner is renamed
tests/autofit/test_engine_doublet.py:96:                                  noise_floor=15.0, n_refits=6, rng_seed=0)
tests/autofit/test_bic_companions.py:26:        options={"n_refits": 2, "rng_seed": 0, "noise_floor": 1.0,
tests/autofit/test_c1s_mixed_material_class.py:296:                                compare_models, rank_and_filter,
tests/autofit/test_c1s_mixed_material_class.py:326:    result = rank_and_filter([conditional_report], allow_conditional=True)
tests/autofit/test_c1s_mixed_material_class.py:327:    # rank_and_filter's `survivors` holds the final ranked winner regardless
tests/autofit/test_fit_full_window_option.py:36:                            match_components_to_slots, run_stability_analysis)
tests/autofit/test_fit_full_window_option.py:254:    matching during stability re-fits (``match_components_to_slots`` /
tests/autofit/test_fit_full_window_option.py:268:        x, y, w, model, primary, noise_floor=1.0, n_refits=6, rng_seed=0,
tests/autofit/test_fit_full_window_option.py:302:    slot_map = match_components_to_slots([comp], model, noise_floor=1.0,
tests/autofit/test_stage2_completeness.py:43:IC_OPTS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
tests/autofit/test_stage2_completeness.py:266:    res = eng.rank_and_filter([unstable], allow_last_resort=True)
tests/autofit/test_stage2_completeness.py:275:    res = eng.rank_and_filter([clean, unstable], allow_last_resort=True)
tests/autofit/test_stage2_completeness.py:339:    res = eng.rank_and_filter([unstable])          # default: no evidence
tests/autofit/test_stage2_completeness.py:355:    res = eng.rank_and_filter([cond, unstable], allow_last_resort=True)
tests/autofit/test_candidate_pool_wiring.py:37:IC_OPTS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
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

exec
/bin/zsh -lc "sed -n '3190,3310p' templates/index.html; sed -n '3430,3610p' templates/index.html; sed -n '5060,5125p' templates/index.html; sed -n '6080,6120p' templates/index.html; sed -n '6690,6740p' templates/index.html; sed -n '7540,7660p' templates/index.html; rg -n '_recomputeAutoFitMenuState|_isChargeRefAllowed|function getCorrectedBE' templates/index.html; rg -n '"'^def (_component_support|rank_and_filter|_apply_decisive_override|run_stability_analysis)|SUPPORT_MIN_F|noise_floor|orphans|conditional_pool'"' fitting.py autofit/engine.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
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
    const wasStack = !!closing.isStack;
    this.tabs.splice(idx, 1);

    // Prune stack entries that referenced the closed tab (skip if it was
    // itself a stack — stacks don't reference each other).
    if (!wasStack) {
      for (const t of this.tabs) {
        if (!t.isStack) continue;
        const before = t.entries.length;
        t.entries = t.entries.filter(e => e.sourceTabId !== id);
        const removed = before - t.entries.length;
        if (removed > 0) {
          notify('Removed "' + closingName + '" from "' + t.name + '" (source tab closed).', 'amber');
          if (t.id === this.activeId) {
            renderStackLegend(t);
            // The chart holds datasets keyed to the removed entry: rebuild
            // it, or the closed source's curves (and, for a local source,
            // their only designation) outlive the entry (Codex A0 round 19).
            _renderStackChart(t);
          }
        }
      }
    }

    if (this.tabs.length === 0) {
      this.activeId = null;
      _updateUndoButtons();
      if (typeof _historyPreview !== 'undefined') _historyPreview = null;
      state.rawBE = []; state.rawIntensity = [];
      state.peaks = []; state.fitResult = null;
      state.ccShift = 0; state.nextId = 1;
      document.getElementById('data-info').textContent = 'no data';
      const _cl = document.getElementById('spec-combo-label');
      if (_cl) _cl.textContent = 'no data';
      document.getElementById('sb-pts').textContent = '\u2014';
      state.fitResult = null;
      active.peaks = state.peaks;
      active.nextId = state.nextId;
      active.fitResult = null;
      // Provenance of the imported parameters (unit A0): a model saved from
      // a local (unweighted) fit stays a starting point, not a result.
      active.modelProvenance = _isLocalProvenance(data.fitStatistics)
        ? { ...data.fitStatistics, importedFrom: 'fit.json' } : null;

      // Apply charge correction
      if (data.chargeCorrection) {
        state.ccShift = data.chargeCorrection.shift || 0;
        active.ccShift = state.ccShift;
        active.ui.ccMethod = data.chargeCorrection.method || 'none';
        active.ui.ccObs = data.chargeCorrection.observedBE || '';
      }

      // Fit loaded from external file — CC not verified for this spectrum
      active.chargeVerified = false;
      this._updateCCVerifiedUI(false);

      // Endpoint averaging is resolved whether or not the file carries a
      // background block: v1 files written before 2026-09-08 never recorded
      // it (those fits were made at 1), and an accepted peaks-only file must
      // not inherit the fresh target tab's new-tab default either (Codex
      // round 1, both runs).
      active.ui.endpointAvg = (data.background && data.background.endpointAvg) || LEGACY_ENDPOINT_AVG;

      // Apply background
      if (data.background) {
        active.ui.bgType = data.background.type || 'shirley';
        active.ui.bgStart = data.background.start || '';
        active.ui.bgEnd = data.background.end || '';
        active.ui.shirleyIter = data.background.shirleyIter || '5';
        // bgSubtractedView is missing from pre-feature saves → falsy default
        active.ui.bgSubtractedView = !!data.background.bgSubtractedView;
      }

      // Apply ROI
      if (data.roi) {
        active.ui.roiMin = data.roi.min || '';
        active.ui.roiMax = data.roi.max || '';
      }

      // Apply notes
      if (data.notes) active.notes = data.notes;
      const notesEl = document.getElementById('spectrum-notes');
      if (notesEl) notesEl.value = active.notes || '';

      // Apply manual anchor points
      if (data.manualAnchors) active.manualAnchors = data.manualAnchors;

      // Restore DOM from updated ui and re-render
      this._restoreUI(active.ui);
      renderPeakList();
      updatePlot();
      renderResults();   // installs the imported model's designation (or the plain placeholder) and clears stale widgets
      return;
    }

    // v2+ multi-tab data — route through _loadProjectJSON (has confirmation)
    _loadProjectJSON(data);
  }

  // ── Tab bar rendering ───────────────────────────

  renderTabBar() {
    const bar = document.getElementById('spectrum-tab-bar');
    if (!bar) return;
    bar.innerHTML = '';
    for (const tab of this.tabs) {
      const el = document.createElement('div');
      el.className = 'sp-tab'
        + (tab.id === this.activeId ? ' active' : '')
        + (tab.isStack ? ' is-stack' : '');
      const tabId = tab.id;

      const inner = document.createElement('span');
      inner.innerHTML =
        '<span class="sp-tab-dot" style="background:' + tab.color + '"></span>' +
        '<span>' + this._esc(tab.name) + '</span>' +
        '<span class="sp-tab-close" title="Close tab">&times;</span>';
      el.appendChild(inner);

      el.addEventListener('click', e => {
        if (e.target.classList.contains('sp-tab-close')) {
          e.stopPropagation();
          this.closeTab(tabId);
        } else {
          this.activateTab(tabId);
        }
      });

      // ── Drag-and-drop reordering ──
      el.draggable = true;
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
// of the same inclusive form, so this one window is the one both use.
// Plan: docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md.
function _roiWindowStatus() {
  const corrBE = (typeof getCorrectedBE === 'function' && state.rawBE && state.rawBE.length) ? getCorrectedBE() : [];
  if (!corrBE.length) return { state: 'no-data' };
  let dMin = Infinity, dMax = -Infinity;
  for (const v of corrBE) { if (v < dMin) dMin = v; if (v > dMax) dMax = v; }
  const lo = parseFloat(document.getElementById('roi-min').value);
  const hi = parseFloat(document.getElementById('roi-max').value);
  const { be } = getROIData();
  let sMin = Infinity, sMax = -Infinity;
  for (const v of be) { if (v < sMin) sMin = v; if (v > sMax) sMax = v; }
  const base = { dMin, dMax, lo, hi, sMin, sMax, n: be.length };
  if (Number.isFinite(lo) && Number.isFinite(hi) && lo > hi) return { ...base, state: 'inverted' };
  if (!be.length) return { ...base, state: 'no-overlap' };
  const { locked, total } = _lockAllStats();
  if (locked > total / 2) {
    btn.innerHTML = '&#x1f513; Unlock All';
    btn.title = 'Unlock all fit parameters on all peaks';
  } else {
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
    if (p.isChargeReference) p.isChargeReference = false;
  }
}

function renderPeakList() {
  _clearDisallowedChargeRef();
  _updateLocalModelBanner();
  const el = document.getElementById('peak-list');
  const empty = document.getElementById('peak-empty');
  // Preserve which peak cards are expanded before clearing
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
let _autoFitConfirmResolver = null;
function _showAutoFitConfirmModal(peakCount) {
  return new Promise(resolve => {
    _autoFitConfirmResolver = resolve;
    const span = document.getElementById('auto-fit-c1s-confirm-count');
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
      const spec = peakToBackendSpec(p);
      if (Number.isFinite(p._afCenterMin)) spec.center_min = p._afCenterMin;
      if (Number.isFinite(p._afCenterMax)) spec.center_max = p._afCenterMax;
      if (Number.isFinite(p._afFwhmMin))   spec.fwhm_min   = p._afFwhmMin;
      if (Number.isFinite(p._afFwhmMax))   spec.fwhm_max   = p._afFwhmMax;
2064:                <input type="number" id="roi-min" value="706" step="0.5" oninput="updatePlot();_recomputeAutoFitMenuState()">
2068:                <input type="number" id="roi-max" value="726" step="0.5" oninput="updatePlot();_recomputeAutoFitMenuState()">
3247:    if (typeof _recomputeAutoFitMenuState === 'function') _recomputeAutoFitMenuState();
5079:function getCorrectedBE() {
6099:function _isChargeRefAllowed() {
6109:  if (_isChargeRefAllowed()) return;
6181:  const showChargeRef = _isChargeRefAllowed();
6712:function _recomputeAutoFitMenuState() {
6732:  if (typeof _recomputeAutoFitMenuState === 'function') _recomputeAutoFitMenuState();
fitting.py:1441:SUPPORT_MIN_F = 10.0
fitting.py:1444:def _component_support(y_sub, fitted_sub, comp_y, weights, n_free_comp, n_free_total) -> dict[str, Any]:
fitting.py:1460:            "supported": bool(delta > 0 and (chi_with == 0 or f >= SUPPORT_MIN_F))}
fitting.py:1524:        required = f >= SUPPORT_MIN_F
autofit/engine.py:1042:    noise_floor: float,
autofit/engine.py:1050:    orphans: list[FittedComponent] = []
autofit/engine.py:1058:                and comp.amplitude > noise_floor)
autofit/engine.py:1077:            orphans.append(FittedComponent(
autofit/engine.py:1105:                orphans.append(incumbent)
autofit/engine.py:1108:                orphans.append(comp)
autofit/engine.py:1110:    slot_map["__orphans__"] = orphans  # type: ignore[assignment]
autofit/engine.py:1162:def run_stability_analysis(
autofit/engine.py:1168:    noise_floor: float,
autofit/engine.py:1189:    n_with_orphans = 0
autofit/engine.py:1234:        slot_map = match_components_to_slots(outcome.components, model, noise_floor,
autofit/engine.py:1236:        if slot_map.pop("__orphans__", []):
autofit/engine.py:1237:            n_with_orphans += 1
autofit/engine.py:1270:        orphan_rate=n_with_orphans / max(n_attempted, 1),
autofit/engine.py:1406:    noise_floor: float,
autofit/engine.py:1411:    sigma = np.sqrt(np.maximum(y, noise_floor))
autofit/engine.py:1645:def rank_and_filter(
autofit/engine.py:1665:    conditional_pool: list[ModelReport] = []
autofit/engine.py:1677:                conditional_pool.append(r)
autofit/engine.py:1689:    if allow_conditional and conditional_pool and not survivors:
autofit/engine.py:1690:        survivors = conditional_pool
autofit/engine.py:1808:    noise_floor: float = 1.0,
autofit/engine.py:1856:        local_sigma = float(np.median(np.sqrt(np.maximum(y_asc[mask], noise_floor)))) \
autofit/engine.py:1857:            if mask.sum() > 1 else float(np.sqrt(max(noise_floor, 1.0)))
autofit/engine.py:2007:    noise_floor: float,
autofit/engine.py:2014:    sigma = np.sqrt(np.maximum(y, noise_floor))
autofit/engine.py:2163:    noise_floor: float,
autofit/engine.py:2232:    if comp.amplitude <= noise_floor:
autofit/engine.py:2233:        return _fast(f"amplitude {comp.amplitude:.1f} ≤ noise_floor {noise_floor:.1f}")
autofit/engine.py:2240:    local_sigma = float(np.median(np.sqrt(np.maximum(y[mask], noise_floor)))) \
autofit/engine.py:2241:        if mask.sum() > 1 else float(np.sqrt(max(noise_floor, 1.0)))
autofit/engine.py:2273:        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
autofit/engine.py:2312:    residuals = compute_residual_diagnostics(x, y, y_fit_aug, noise_floor, diagnostic_windows)
autofit/engine.py:2391:    noise_floor: float,
autofit/engine.py:2446:        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
autofit/engine.py:2460:            x, y, y_fit, noise_floor, diagnostic_windows),
autofit/engine.py:2479:def _apply_decisive_override(
autofit/engine.py:2486:    noise_floor: float,
autofit/engine.py:2507:                                   diagnostic_windows, noise_floor,
autofit/engine.py:2554:    noise_floor: float = 1.0,
autofit/engine.py:2627:            noise_floor=noise_floor,
autofit/engine.py:2646:                noise_floor=noise_floor,
autofit/engine.py:2826:            noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
autofit/engine.py:2840:        residuals = compute_residual_diagnostics(x, y, y_fit, noise_floor, diagnostic_windows)
autofit/engine.py:2882:                    x, y, current_y_fit, noise_floor, current.model,
autofit/engine.py:2904:                        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
autofit/engine.py:2954:        noise_floor=noise_floor,

exec
/bin/zsh -lc "ls -d venv /Users/skyefortier/xps-app/venv 2>/dev/null; node --test tests/js/autofit_c1s_gate.test.js; sed -n '1,110p' tests/autofit/test_stress_honesty.py; sed -n '85,150p' autofit/confidence.py; rg -n 'detectability|floor_multiple|support_f|\\.contains\\(' autofit templates tests/autofit | head -100" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 75ms:
# Subtest: the sweep reproduction: record window on C 1s, U 4f typed in the fields (no tab switch) — the gate CLOSES
ok 1 - the sweep reproduction: record window on C 1s, U 4f typed in the fields (no tab switch) — the gate CLOSES
  ---
  duration_ms: 4.278999
  type: 'test'
  ...
# Subtest: the SELECTED data decide, not the typed midpoint of a window that reaches past the data
ok 2 - the SELECTED data decide, not the typed midpoint of a window that reaches past the data
  ---
  duration_ms: 1.070215
  type: 'test'
  ...
# Subtest: a non-active record is judged on its saved window over its own corrected data
ok 3 - a non-active record is judged on its saved window over its own corrected data
  ---
  duration_ms: 0.628303
  type: 'test'
  ...
# Subtest: every caller of the gate is for the active tab (menu state, charge-reference permission, the Auto-Fit run)
ok 4 - every caller of the gate is for the active tab (menu state, charge-reference permission, the Auto-Fit run)
  ---
  duration_ms: 1.624479
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
# duration_ms 106.702035
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
templates/index.html.pre-audit:1289:        if (e.target.classList.contains('sp-tab-close')) {
templates/index.html.pre-audit:1309:      if (btn.classList.contains('active')) {
templates/index.html.pre-audit:3534:  if (dd.classList.contains('open')) {
templates/index.html.pre-audit:3535:    const close = (e) => { if (!dd.contains(e.target)) { dd.classList.remove('open'); document.removeEventListener('click', close); } };
templates/index.html.pre-audit:3910:  const wasSurvey = document.getElementById('tab-survey').classList.contains('active');
tests/autofit/test_browser_schema_roundtrip.py:136:    "detectability": "above_floor",
templates/index.html:2706:  if (wrap && !wrap.contains(e.target)) {
templates/index.html:2718:    const isLight = document.body.classList.contains('light-theme');
templates/index.html:3515:        if (e.target.classList.contains('sp-tab-close')) {
templates/index.html:3581:      if (btn.classList.contains('active')) {
templates/index.html:5872:    if (document.getElementById('spec-combo-drop').classList.contains('open')) {
templates/index.html:5878:    if (multipletOverlay && multipletOverlay.classList.contains('open')) {
templates/index.html:9894:    backgroundColor: document.body.classList.contains('light-theme')
templates/index.html:9922:    const isLight = document.body.classList.contains('light-theme');
templates/index.html:9942:    const smoothColor = document.body.classList.contains('light-theme') ? '#cc5500' : '#00FFDD';
templates/index.html:10120:      const isL = document.body.classList.contains('light-theme');
templates/index.html:10429:  if (dd.classList.contains('open')) {
templates/index.html:10430:    const close = (e) => { if (!dd.contains(e.target)) { dd.classList.remove('open'); document.removeEventListener('click', close); } };
templates/index.html:12009:  const wasSurvey = document.getElementById('tab-survey').classList.contains('active');
templates/index.html:12144:    gridColor: document.body.classList.contains('light-theme')
templates/index.html:12147:    tooltipBorder: document.body.classList.contains('light-theme')
templates/index.html:12152:    rawData: document.body.classList.contains('light-theme') ? '#1a1a2e' : '#e8edf5',
templates/index.html:12324:    if (tip.classList.contains('visible')) showTip(sel, text);
templates/index.html:12550:  const isLight = document.body.classList.contains('light-theme');
templates/index.html:12583:  const isLight = document.body.classList.contains('light-theme');
templates/index.html:12986:  const collapsed = !el.classList.contains('collapsed');
templates/index.html:13173:  if (p && !p.contains(t) && !(t instanceof Element && t.closest('.ref-legend-more'))) _refCloseChipDropdown();
templates/index.html:13270:  if (p && p.classList.contains('show')) _refPositionSearchPortal();
templates/index.html:13274:  if (p && p.classList.contains('show')) _refPositionSearchPortal();
templates/index.html:13278:  if (!p || !p.classList.contains('show')) return;
templates/index.html:14268:  if (!panel.classList.contains('open')) {
templates/index.html:14645:  const isLight = document.body.classList.contains('light-theme');
templates/index.html:14698:  if (drop.classList.contains('open')) return;
templates/index.html:14714:  if (document.getElementById('spec-combo-drop').classList.contains('open')) _ssClose();
templates/index.html:14819:  if (combo && !combo.contains(e.target)) _ssClose();
templates/index.html:15676:  if (!overlay || !overlay.classList.contains('open') || !el) return;
autofit/confidence.py:90:    detection_floor_multiple: float = DETECTION_FLOOR_MULTIPLE,
autofit/confidence.py:99:    floor = detection_floor_multiple * noise_floor
autofit/confidence.py:123:        "detectability": {
autofit/confidence.py:126:            "floor_multiple": detection_floor_multiple,
autofit/confidence.py:127:            "floor_multiple_is_tunable": True,
tests/autofit/test_methods_seam.py:104:    assert conf["detectability"]["status"] == "above_floor"

codex
The four gate tests pass. The active-tab path now uses the same ROI selection as the fit, and tab activation restores state and fields before checking the menu. I found two areas to probe: saved-record ROI handling differs from the live selector, and the parked LR patch still uses F-test logic in its confidence payload.

exec
/bin/zsh -lc "sed -n '1440,1465p' fitting.py; sed -n '1035,1115p' autofit/engine.py; sed -n '1160,1275p' autofit/engine.py; sed -n '1635,1720p' autofit/engine.py; sed -n '2470,2545p' autofit/engine.py; sed -n '2930,2965p' autofit/engine.py; sed -n '3620,3690p' templates/index.html; sed -n '4970,5068p' templates/index.html; sed -n '7555,7585p' templates/index.html; rg -n 'bg_mismatch|threshold|scale.free|tolerance|variance' tests/autofit/test_stress_honesty.py CLAUDE.md" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
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


def run_stability_analysis(
    x: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray,
    model: CandidateModel,
    primary_fit: FitOutcome,
    noise_floor: float,
    n_refits: int = 20,
    rng_seed: int = 0,
    fixed_param_values: Optional[dict[str, float]] = None,
    deadline: Optional[float] = None,
    fit_full_window: bool = False,
    endpoint_avg: int = 1,
) -> ModelStability:
    """
    ``deadline`` is an absolute ``time.perf_counter()`` timestamp (set by
    the caller from CANDIDATE_TIMEOUT_SEC) shared across this candidate's
    primary fit + all its refits. Once passed, remaining refits are
    skipped — not run and not counted as failures — so one candidate stuck
    in a slow-but-nfev-capped region can't consume the rest of the request.
    """
    rng = np.random.default_rng(rng_seed)
    pos: dict[str, list[float]] = {s.role: [] for s in model.slots}
    fw: dict[str, list[float]] = {s.role: [] for s in model.slots}
    am: dict[str, list[float]] = {s.role: [] for s in model.slots}
    occupied: dict[str, int] = {s.role: 0 for s in model.slots}
    n_converged = 0
    n_with_orphans = 0
    # Same widened bounds every refit was actually built with (constant
    # across this candidate's whole stability pass) — identity-matching
    # must agree with the bound the fit was allowed to search, or a
    # component correctly placed outside its ORIGINAL window becomes an
    # orphan here, tanking persistence for the very slot this option
    # exists to rescue (Codex-caught, see _effective_be_window).
    bound_overrides = _full_window_bound_overrides(model, x) if fit_full_window else None

    # Data-informed perturbation seeds (see perturb_initial_params): reuse
    # the primary fit's background rather than recomputing per refit.
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
    # candidates are visible here and can never be survivors.
    screen: Optional[list[dict]] = None
    # Candidate-generation layer (autofit.candidates): the OVERCOMPLETE,
    # provenance-tagged detection pool payload — every feature any source
    # (local_max / curvature_shoulder / residual_gap / grammar) proposed,
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

        boundary_fixed_params=sorted(fixed),
        # carry the proposal lineage forward so a width-capped proposal
        # promoted via decisive-override keeps its width_capped/proposed_peaks
        # record on the winner row (Codex fwhm-cap review, run A MINOR)
        proposed_peaks=list(report.proposed_peaks),
        augmented_from=report.augmented_from,
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
    analysis itself."""
    if progress_cb is None:
        return
    try:
        progress_cb({"phase": phase, "candidate_index": idx,
                     "candidate_total": total, "candidate_name": name})
    except Exception:
            final_report = current
            if rejected:
                # rejected attempts stay visible on whichever report we emit
                final_report.proposed_peaks = final_report.proposed_peaks + rejected
            timings.append(ProposalPassTiming(
                candidate_name=model.name, n_flagged=counts["n_flagged"],
                n_over_cap=counts["n_over_cap"],
                n_attempted=counts["n_attempted"], n_fast_rejected=counts["n_fast"],
                n_stability_rejected=counts["n_stab"], n_accepted=counts["n_acc"],
                wall_time_sec=time.perf_counter() - pass_start, timed_out=timed_out,
            ))

        reports.append(final_report)

    result = rank_and_filter(
        reports,
        persistence_threshold=persistence_threshold,
        bic_ambiguity_threshold=bic_ambiguity_threshold,
        allow_last_resort=bool(preseed_specs),
    )
    result = _apply_decisive_override(
        x, y, weights, result,
        persistence_threshold=persistence_threshold,
        diagnostic_windows=diagnostic_windows,
        noise_floor=noise_floor,
        n_refits=n_refits,
        rng_seed=rng_seed,
        fit_full_window=fit_full_window,
        endpoint_avg=endpoint_avg,
    )
    result.non_converged = non_converged
    result.cross_candidate_coincidences = _cross_candidate_coincidences(proposal_attempts)
    result.proposal_pass_timings = timings
    result.analysis_truncated = analysis_truncated
    result.n_candidates_evaluated = n_evaluated
    result.n_candidates_total = n_cand
    } else {
      markersWrap.style.display = 'none';
    }
  }

  _renderSurveySelector(surveys) {
    const sel = document.getElementById('survey-selector');
    if (!sel) return;
    sel.innerHTML = surveys.map(s => {
      const n = s.rawBE.length;
      const beMin = _arrMin(s.rawBE).toFixed(0);
      const beMax = _arrMax(s.rawBE).toFixed(0);
      return `<li data-survey-id="${s.id}" onclick="tabManager._onSurveySelect('${s.id}')">` +
        `<span class="survey-sel-name">${_escHtml(s.name)}</span>` +
        `<span class="survey-sel-meta">${n} pts \u00b7 ${beMin}\u2013${beMax} eV</span></li>`;
    }).join('');
  }

  _onSurveySelect(surveyId) {
    this._activateSurvey(surveyId);
  }

  /** Switch main chart to a survey and show element markers panel */
  _activateSurvey(surveyId) {
    const surveyTab = this._getTab(surveyId);
    if (!surveyTab) return;

    // Remember previous non-survey tab for restore
    const currentActive = this._getTab(this.activeId);
    if (currentActive && !currentActive.isSurvey) {
      this._preSurveyTabId = this.activeId;
    }

    this.activateTab(surveyId);

    // Initialize element selections if needed
    if (!surveyTab.markedElements) surveyTab.markedElements = [];

    // Highlight active survey in selector list
    document.querySelectorAll('#survey-selector li').forEach(li => {
      li.classList.toggle('active-survey', li.dataset.surveyId === surveyId);
    });

    // Show markers panel and render
    const markersWrap = document.getElementById('survey-markers-wrap');
    if (markersWrap) markersWrap.style.display = '';
    this._renderElementMarkers(surveyId);
    this._initElementSearch(surveyId);
    updatePlot();
  }

  /** Render the list of user-added elements with their lines */
  _renderElementMarkers(surveyId) {
    const surveyTab = this._getTab(surveyId);
    const list = document.getElementById('survey-element-list');
    if (!surveyTab || !list) return;

    const elements = surveyTab.markedElements || [];
    if (!elements.length) {
      list.innerHTML = '<li style="color:var(--text3);font-size:11px;padding:6px 0;">No elements added. Use the search box above.</li>';
      return;
    }

    list.innerHTML = elements.map((sym, idx) => {
      const color = ELEMENT_MARKER_COLORS[idx % ELEMENT_MARKER_COLORS.length];
      const el = _accSurveyElements()[sym];
      if (!el) return '';
      const name = ELEMENT_NAMES[sym] || sym;
      const linesHtml = Object.entries(el.lines).map(([line, be]) => {
        const isAuger = /^[A-Z]/.test(line);
        const label = sym + ' ' + line;
  const refField = document.getElementById('cc-ref-field');
  const targetField = document.getElementById('cc-target-field');

  refField.style.display = 'none';
  targetField.style.display = 'none';

  if (method === 'c1s') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    state.ccShift = isNaN(obs) ? 0 : obs - 284.5;
    refField.style.display = 'block';
    document.getElementById('cc-lit').value = '284.5';
  } else if (method === 'c1s-adv') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    state.ccShift = isNaN(obs) ? 0 : obs - 284.8;
    refField.style.display = 'block';
    document.getElementById('cc-lit').value = '284.8';
  } else if (method === 'au4f') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    state.ccShift = isNaN(obs) ? 0 : obs - 83.98;
    refField.style.display = 'block';
    document.getElementById('cc-lit').value = '83.98';
  } else if (method === 'b1s-b2o3') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    state.ccShift = isNaN(obs) ? 0 : obs - 192.99;
    refField.style.display = 'block';
    document.getElementById('cc-lit').value = '192.99';
  } else if (method === 'n1s-bn') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    state.ccShift = isNaN(obs) ? 0 : obs - 398.31;
    refField.style.display = 'block';
    document.getElementById('cc-lit').value = '398.31';
  } else if (method === 'b1s-bn') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    state.ccShift = isNaN(obs) ? 0 : obs - 190.74;
    refField.style.display = 'block';
    document.getElementById('cc-lit').value = '190.74';
  } else if (method === 'custom') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    const lit = parseFloat(document.getElementById('cc-lit').value);
    state.ccShift = (isNaN(obs) || isNaN(lit)) ? 0 : obs - lit;
    refField.style.display = 'block';
    targetField.style.display = 'block';
  } else {
    state.ccShift = 0;
  }

  // Shift all energy-dependent values by the change in correction
  const delta = state.ccShift - prevShift;
  if (delta !== 0) {
    // ROI boundaries
    const roiMinEl = document.getElementById('roi-min');
    const roiMaxEl = document.getElementById('roi-max');
    const roiMinVal = parseFloat(roiMinEl.value);
    const roiMaxVal = parseFloat(roiMaxEl.value);
    if (!isNaN(roiMinVal)) roiMinEl.value = (roiMinVal - delta).toFixed(1);
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
tests/autofit/test_stress_honesty.py:24:    bg_mismatch_case,
tests/autofit/test_stress_honesty.py:125:def test_bg_mismatch_surfaces_loudly():
tests/autofit/test_stress_honesty.py:129:    case = bg_mismatch_case(seed=61)
CLAUDE.md:155:server limits found there: a DS+G m just above the 0.001 delta threshold
CLAUDE.md:173:anchor (answer: a scale-free F test), then two tolerances on that F test
CLAUDE.md:174:(answer: none). Prefer a scale-free comparison with no tolerance. If a
CLAUDE.md:175:check seems to need a magnitude threshold, that is evidence the check is
CLAUDE.md:179:`docs/autofit/codex/autofit_zero_graphite_*`, the DE unit's tolerance rounds
CLAUDE.md:182:side: every χ² comparison tolerance produced reachable false failures and
CLAUDE.md:375:bound, and every tolerance tried for that comparison produced reachable
CLAUDE.md:422:components: χ²ᵣ 2.8e-6, both "supported"). A count, not a threshold; one
CLAUDE.md:471:~1e-4 relative in an area at its stopping tolerance of 1e-8. Worse, the
CLAUDE.md:477:internals for this, and do not tighten the tolerance: ftol = xtol = gtol =
CLAUDE.md:579:and stay labelled "Residual variance". It produces no uncertainties, and it
CLAUDE.md:770:threshold: removing it from the fitted model must make the fit to the
CLAUDE.md:796:intensity floors failing is the data saying no threshold on intensity can
CLAUDE.md:814:  so a chain of links in any request order resolves; NO tolerance of any

exec
/bin/zsh -lc "sed -n '1,130p' autofit/methods/ic.py; rg -n 'ic_model|run_candidate|sigma =|weights =' autofit/methods/*; ls tests/js; ls /Users/skyefortier/AGENTS.md /Users/AGENTS.md /AGENTS.md /Users/skyefortier/xps-app/AGENTS.md /Users/skyefortier/xps-app/.claude/AGENTS.md /Users/skyefortier/xps-app/.claude/worktrees/AGENTS.md 2>/dev/null" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 exited 1 in 0ms:
sed: autofit/methods/ic.py: No such file or directory
autofit/methods/max_entropy.py:105:            sigma = float(opts.pop("noise_sigma"))
autofit/methods/max_entropy.py:109:            sigma = float(1.4826 * np.median(np.abs(d2 - np.median(d2))) / np.sqrt(6.0))
autofit/methods/max_entropy.py:110:            sigma = max(sigma, 1e-12)
autofit/methods/ic_model_comparison.py:32:    id = "ic_model_comparison"
autofit/methods/ic_model_comparison.py:47:            raise ValueError("ic_model_comparison requires a resolved grammar")
autofit/methods/ic_model_comparison.py:51:            raise ValueError(f"unknown ic_model_comparison options: {sorted(unknown)}")
autofit/methods/ic_model_comparison.py:308:        "method": "ic_model_comparison",
autofit/methods/base.py:65:        ``ic_model_comparison`` threads it through to a real signal
autofit/methods/__init__.py:7:  2. ic_model_comparison     — fitalg engine port (peak-count by IC panel)
autofit/methods/__init__.py:22:from .ic_model_comparison import ICModelComparisonMethod
autofit_c1s_gate.test.js
autofit_required.test.js
autofit_zero_graphite.test.js
batch_propagation.test.js
bg_window_indices.test.js
endpoint_avg_default.test.js
find_peaks_coverage.test.js
find_peaks_endpoint_avg.test.js
find_peaks_periodic_table.test.js
find_peaks_plain_message.test.js
find_peaks_progress.test.js
fit_acceptance.test.js
fit_start_poll.test.js
fixtures
fp_experimental_notice.test.js
fp_material_mixed.test.js
lib
lineshape_parity.test.js
lineshape_parity_backend.py
lineshape_roundtrip.test.js
lineshape_roundtrip_backend.py
local_lm_descent.test.js
local_lm_server_parity_backend.py
module_state_scan.test.js
per_tab_state.test.js
ref_core.test.js
roi_clamp_centre_warning.test.js
scattered_starts.test.js
shape_switch_roundtrip.test.js
stale_statistics.test.js
tougaard_twin.test.js
unsupported_components.test.js

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import sys, re, importlib, importlib.abc, importlib.machinery
from pathlib import Path
sys.path.insert(0, str(Path('\\''tests/autofit'\\'').resolve()))
class Loader(importlib.abc.Loader):
    def __init__(self, source, filename): self.source,self.filename=source,filename
    def create_module(self, spec): return None
    def exec_module(self, module): exec(compile(self.source,self.filename,'\\''exec'\\''),module.__dict__)
class Finder(importlib.abc.MetaPathFinder):
    sources={}
    def find_spec(self, fullname, path, target=None):
        if fullname not in self.sources: return None
        spec=importlib.machinery.PathFinder.find_spec(fullname,path)
        spec.loader=Loader(self.sources[fullname],spec.origin)
        return spec
finder=Finder(); sys.meta_path.insert(0,finder)
def patched_sources(patch):
    out={}
    for block in patch.split('\\''diff --git '\\'')[1:]:
        filename=block.splitlines()[0].split()[1][2:]
        old=Path(filename).read_text().splitlines(True); new=[]; cursor=0
        for h in re.split(r'\\''(?m)"'^@@ '"'\\'',block)[1:]:
            header,body=h.split('\\''\\n'\\'',1); start=int(re.match(r'\\''-(\\d+)'\\'',header).group(1))-1
            new.extend(old[cursor:start]); cursor=start
            for line in body.splitlines(True):
                if line.startswith('\\'' '\\''):
                    assert old[cursor]==line[1:], (filename,cursor,line)
                    new.append(line[1:]); cursor+=1
                elif line.startswith('\\''-'\\''):
                    assert old[cursor]==line[1:], (filename,cursor,line)
                    cursor+=1
                elif line.startswith('\\''+'\\''): new.append(line[1:])
        new.extend(old[cursor:]); out[filename[:-3].replace('\\''/'\\'','\\''.'\\'')]='\\'''\\''.join(new)
    return out
for variant in ['\\''baseline'\\'','\\''F_support_test'\\'','\\''LR_likelihood_ratio'\\'']:
    finder.sources={} if variant=='\\''baseline'\\'' else patched_sources(Path('\\''docs/findings/noise-floor-occupancy/variant_'\\''+variant+'\\''.patch'\\'').read_text())
    for name in list(sys.modules):
        if name=='\\''autofit'\\'' or name.startswith('\\''autofit.'\\'') or name=='\\''stress_cases'\\'': del sys.modules[name]
    from stress_cases import bg_mismatch_case
    from autofit.methods import get_method
    import autofit.engine as e
    original=e.rank_and_filter
    def ranked(reports, **kw):
        for r in reports:
            print(variant, r.model.name, '\\''redchi'\\'',round(r.reduced_chi_sq,3),'\\''persistence'\\'',r.active_min_persistence,'\\''orphan'\\'',r.stability.orphan_rate,flush=True)
            for c in r.primary_fit.components:
                s=getattr(c,'\\''support'\\'',None)
                if s: print('\\'' '\\'',c.slot_role,{k:round(v,3) if type(v)==float else v for k,v in s.items()},flush=True)
        return original(reports,**kw)
    e.rank_and_filter=ranked
    case=bg_mismatch_case(seed=61)
    res=get_method('\\''ic_model_comparison'\\'').run(case.x,case.y,grammar=case.grammar,options={'\\''n_refits'\\'':4,'\\''rng_seed'\\'':0,'\\''noise_floor'\\'':1.0,'\\''enable_proposal_pass'\\'':True})
    print('\\''RESULT'\\'',variant,res.success,res.diagnostics['\\''winner'\\''],res.diagnostics['\\''conditional'\\''],res.diagnostics.get('\\''conditional_reason'\\''),flush=True)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 exited 1 in 973ms:
Traceback (most recent call last):
  File "<string>", line 38, in <module>
  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/tests/autofit/stress_cases.py", line 58, in <module>
    from fitting import _SHAPE_FUNCS
  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/fitting.py", line 35, in <module>
    from lmfit import Model, Parameters
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

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import sys, re, importlib, importlib.abc, importlib.machinery
from pathlib import Path
sys.path.insert(0, str(Path('\\''tests/autofit'\\'').resolve()))
class Loader(importlib.abc.Loader):
    def __init__(self, source, filename): self.source,self.filename=source,filename
    def create_module(self, spec): return None
    def exec_module(self, module): exec(compile(self.source,self.filename,'\\''exec'\\''),module.__dict__)
class Finder(importlib.abc.MetaPathFinder):
    sources={}
    def find_spec(self, fullname, path, target=None):
        if fullname not in self.sources: return None
        spec=importlib.machinery.PathFinder.find_spec(fullname,path)
        spec.loader=Loader(self.sources[fullname],spec.origin)
        return spec
finder=Finder(); sys.meta_path.insert(0,finder)
def patched_sources(patch):
    out={}
    for block in patch.split('\\''diff --git '\\'')[1:]:
        filename=block.splitlines()[0].split()[1][2:]
        old=Path(filename).read_text().splitlines(True); new=[]; cursor=0
        for h in re.split(r'\\''(?m)"'^@@ '"'\\'',block)[1:]:
            header,body=h.split('\\''\\n'\\'',1); start=int(re.match(r'\\''-(\\d+)'\\'',header).group(1))-1
            new.extend(old[cursor:start]); cursor=start
            for line in body.splitlines(True):
                if line.startswith('\\'' '\\''):
                    assert old[cursor]==line[1:], (filename,cursor,line)
                    new.append(line[1:]); cursor+=1
                elif line.startswith('\\''-'\\''):
                    assert old[cursor]==line[1:], (filename,cursor,line)
                    cursor+=1
                elif line.startswith('\\''+'\\''): new.append(line[1:])
        new.extend(old[cursor:]); out[filename[:-3].replace('\\''/'\\'','\\''.'\\'')]='\\'''\\''.join(new)
    return out
for variant in ['\\''baseline'\\'','\\''F_support_test'\\'','\\''LR_likelihood_ratio'\\'']:
    finder.sources={} if variant=='\\''baseline'\\'' else patched_sources(Path('\\''docs/findings/noise-floor-occupancy/variant_'\\''+variant+'\\''.patch'\\'').read_text())
    for name in list(sys.modules):
        if name=='\\''autofit'\\'' or name.startswith('\\''autofit.'\\'') or name=='\\''stress_cases'\\'': del sys.modules[name]
    from stress_cases import bg_mismatch_case
    from autofit.methods import get_method
    import autofit.engine as e
    original=e.rank_and_filter
    def ranked(reports, **kw):
        for r in reports:
            print(variant, r.model.name, '\\''redchi'\\'',round(r.reduced_chi_sq,3),'\\''persistence'\\'',r.active_min_persistence,'\\''orphan'\\'',r.stability.orphan_rate,flush=True)
            for c in r.primary_fit.components:
                s=getattr(c,'\\''support'\\'',None)
                if s: print('\\'' '\\'',c.slot_role,{k:round(v,3) if type(v)==float else v for k,v in s.items()},flush=True)
        return original(reports,**kw)
    e.rank_and_filter=ranked
    case=bg_mismatch_case(seed=61)
    res=get_method('\\''ic_model_comparison'\\'').run(case.x,case.y,grammar=case.grammar,options={'\\''n_refits'\\'':4,'\\''rng_seed'\\'':0,'\\''noise_floor'\\'':1.0,'\\''enable_proposal_pass'\\'':True})
    print('\\''RESULT'\\'',variant,res.success,res.diagnostics['\\''winner'\\''],res.diagnostics['\\''conditional'\\''],res.diagnostics.get('\\''conditional_reason'\\''),flush=True)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
exec
/bin/zsh -lc "sed -n '148,180p' CLAUDE.md; sed -n '7725,7800p' templates/index.html; sed -n '1,120p' tests/js/roi_clamp_centre_warning.test.js; sed -n '1,110p' tests/js/lib/extract.js; rg -n '_restoreUI|_showAutoFitConfirmModal|toggleActions|actions.*open' templates/index.html; nl -ba docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch | head -210" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
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
    }

    _hideFitSpinner();
    notify('Auto-fit complete. χ²ᵣ = ' + (state.fitResult?.chiReduced?.toFixed(3) || '?'), 'green');
  } catch (e) {
    clearTimeout(timer);
    _hideFitSpinner();
    // The catch path can also fire after a mid-flight tab switch (fetch
    // error/timeout after the user moved on) — same wrong-tab hazard as
    // the explicit discard branch, so it gets the same tab-aware restore.
    _autoFitRestore(snap, fittingTab);
    let msg;
    if (e && (e.name === 'AbortError' || (e.message && e.message.toLowerCase().includes('aborted')))) {
      msg = 'Auto-fit exceeded the 2-minute timeout.';
    } else if (e && (e.unreadableReply || e.httpStatus)) {
      msg = 'Auto-fit failed: ' + e.message;
    } else if (e && e.message) {
      msg = 'Fit failed to converge or produced an unphysical graphite position.';
      console.warn('Auto-fit error:', e);
    } else {
      msg = 'Auto-fit failed.';
    }
    notify(msg, 'red', true);
  }
}

// Is this a C 1s spectrum, as Auto-Fit C1s Graphite would fit it? Unit F3
// (2026-09-27, sweep M5): judged on the DATA the fit would use — for the active
// tab the live selection getROIData() returns (the typed fields, clipped to the
// data, in the corrected frame); for any other record its saved window over
// its own corrected data. It used to read tab.ui, which for the ACTIVE tab is
// synced only on a tab switch or save, and the TYPED midpoint: a wide scan with
// the record's C 1s window but a U 4f window typed in the fields passed the
// gate, and the fit then took the U 4f line as "Graphite".
function isC1sTab(tab) {
  if (!tab || !tab.rawBE || !tab.rawBE.length) return false;
  let be;
  const isActive = typeof tabManager !== 'undefined' && tabManager && tab.id === tabManager.activeId;
  if (isActive && typeof getROIData === 'function') {
    be = getROIData().be;
  } else {
    const shift = Number.isFinite(tab.ccShift) ? tab.ccShift : 0;
    const corr = tab.rawBE.map(v => v - shift);
    const ui = tab.ui || {};
    const a = parseFloat(ui.roiMin), b = parseFloat(ui.roiMax);
    if (Number.isFinite(a) && Number.isFinite(b)) {
      const lo = Math.min(a, b), hi = Math.max(a, b);
      be = corr.filter(v => v >= lo && v <= hi);
    } else {
      be = corr;                               // no window set yet: the whole scan
    }
  }
  if (!be || !be.length) return false;
  let lo = Infinity, hi = -Infinity;
  for (const v of be) { if (v < lo) lo = v; if (v > hi) hi = v; }
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
const _STARTS_N = 3;
const _STARTS_SHIFT_AMBER_EV = 0.5, _STARTS_SHIFT_RED_EV = 1.0;
const _STARTS_TOOLTIP = "After your fit, the same method is run again from a few scattered starting points. If they all come back to your solution, that is what those starts found, no more: other starts or another method might not. If one finds a different solution with a lower χ²ᵣ it is listed here with how far each component moved from where you put it. Your fit is never replaced. A lower χ²ᵣ is not a better chemical model. Identical requests give identical results on real data in practice, but the underlying arithmetic is not bit-reproducible, so a fit sitting near a boundary between two solutions can still resolve differently; that is the situation this check is designed to surface.";

function _startsUnlinkedCount(peaks) { return (peaks || []).filter(p => !p.linked).length; }
// ROI past the data / peak centre outside the data (2026-09-25).
// WARN, NEVER REINTERPRET: the helpers report the window getROIData()
// already uses and write nothing back. Plan:
// docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md.
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
const lines = html.split('\n');
function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name + '\\(');
  const start = lines.findIndex(l => re.test(l));
  assert.ok(start >= 0, `function ${name} not found`);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail('unbalanced ' + name);
}
const NAMES = ['getCorrectedBE', 'getROIData', '_roiWindowStatus', '_roiHintFor', '_refreshRoiHint', '_centreOutsideData', '_outsideDataBadge', '_escAttr'];
const FP_UPLOAD_ROUND = v => +v.toFixed(4);   // uploadToBackend: energies to 4 dp
function makeEnv({ rawBE, ccShift = 0, roiMin, roiMax }) {
  const dom = { 'roi-min': { value: String(roiMin) }, 'roi-max': { value: String(roiMax) },
    'roi-hint': { textContent: '', className: 'roi-hint', style: { display: 'none' } } };
  const document = { getElementById: id => dom[id] || null };
  const state = { rawBE, rawIntensity: rawBE.map(() => 100), ccShift, peaks: [] };
  const fns = new Function('document', 'state', NAMES.map(extractFn).join('\n\n') + '\nreturn { ' + NAMES.join(', ') + ' };')(document, state);
  return { ...fns, dom, state };
}
const grid = (lo, hi, step) => Array.from({ length: Math.round((hi - lo) / step) + 1 }, (_, i) => +(lo + step * i).toFixed(6));
const DATA = grid(280, 295, 0.05);

test('an ROI inside the data: no hint', () => {
  const e = makeEnv({ rawBE: DATA, roiMin: 282, roiMax: 293 });
  const st = e._roiWindowStatus();
  assert.equal(st.state, 'ok');
  assert.equal(e._roiHintFor(st), null);
  e._refreshRoiHint(st);
  assert.equal(e.dom['roi-hint'].style.display, 'none');
});

test('an ROI past the data by more than one step: the quiet hint names the window actually used', () => {
  const e = makeEnv({ rawBE: DATA, roiMin: 270, roiMax: 320 });
  const st = e._roiWindowStatus();
  assert.equal(st.state, 'past');
  const h = e._roiHintFor(st);
  assert.equal(h.cls, '', 'quiet, not amber');
  assert.equal(h.text, 'ROI extends past your data — clipped to 280.00–295.00 eV.');
  e._refreshRoiHint(st);
  assert.equal(e.dom['roi-hint'].style.display, '');
  assert.equal(e.dom['roi-hint'].textContent, h.text);
});

test('one side past the data is enough; the window named is the selected data', () => {
  const e = makeEnv({ rawBE: DATA, roiMin: 283.2, roiMax: 300 });
  const st = e._roiWindowStatus();
  assert.equal(st.state, 'past');
  assert.equal(e._roiHintFor(st).text, 'ROI extends past your data — clipped to 283.20–295.00 eV.');
});

test('a sub-step overshoot (a toFixed(1) rounding of the data edge) is not "past the data"', () => {
  const e = makeEnv({ rawBE: grid(279.97, 295.03, 0.1), roiMin: 279.9, roiMax: 295.1 });   // 0.07 eV past each edge, step 0.1
  assert.equal(e._roiWindowStatus().state, 'ok');
});

test('min above max: amber, no data selected (getROIData selects nothing)', () => {
  const e = makeEnv({ rawBE: DATA, roiMin: 293, roiMax: 282 });
  const st = e._roiWindowStatus();
  assert.equal(st.state, 'inverted');
  assert.equal(e.getROIData().be.length, 0);
  assert.deepEqual(e._roiHintFor(st), { cls: 'amber', text: 'BE min is above BE max — no data is selected.' });
});

test('an ROI that misses the data entirely: amber, names the data range', () => {
  const e = makeEnv({ rawBE: DATA, roiMin: 700, roiMax: 740 });
  const st = e._roiWindowStatus();
  assert.equal(st.state, 'no-overlap');
  assert.deepEqual(e._roiHintFor(st), { cls: 'amber', text: 'ROI does not overlap your data (280.00–295.00 eV) — no data is selected.' });
});

test('empty fields mean the full range (as getROIData): no hint', () => {
  const e = makeEnv({ rawBE: DATA, roiMin: '', roiMax: '' });
  assert.equal(e._roiWindowStatus().state, 'ok');
});

test('the window is in the CORRECTED frame (raw − ccShift), as the fit and Find Peaks use it', () => {
  const e = makeEnv({ rawBE: DATA, ccShift: 1.5, roiMin: 278.5, roiMax: 293.5 });   // corrected data 278.5–293.5
  assert.equal(e._roiWindowStatus().state, 'ok');
  const e2 = makeEnv({ rawBE: DATA, ccShift: 1.5, roiMin: 280, roiMax: 295 });     // past the corrected top by 1.5 eV
  const st = e2._roiWindowStatus();
  assert.equal(st.state, 'past');
  assert.equal(e2._roiHintFor(st).text, 'ROI extends past your data — clipped to 280.00–293.50 eV.');
});

test('a descending acquisition behaves the same', () => {
  const e = makeEnv({ rawBE: DATA.slice().reverse(), roiMin: 270, roiMax: 320 });
  const st = e._roiWindowStatus();
  assert.equal(st.state, 'past');
  assert.equal(e._roiHintFor(st).text, 'ROI extends past your data — clipped to 280.00–295.00 eV.');
});

test('centre outside the SELECTED data is flagged; inside, at the edges, or with no data selected is not', () => {
  const e = makeEnv({ rawBE: DATA, roiMin: 282, roiMax: 293 });
  const st = e._roiWindowStatus();
  for (const [c, out] of [[287, false], [282, false], [293, false], [281.9, true], [293.05, true], [310, true]]) {
    assert.equal(e._centreOutsideData({ id: 1, center: c }, st), out, `centre ${c}`);
  }
  const eNone = makeEnv({ rawBE: DATA, roiMin: 700, roiMax: 740 });
  assert.equal(eNone._centreOutsideData({ id: 1, center: 310 }, eNone._roiWindowStatus()), false, 'no selected data: nothing to compare against (the ROI hint speaks instead)');
  const badge = e._outsideDataBadge({ id: 7, center: 310 }, st);
  assert.match(badge, /class="outside-data-badge" data-peak-id="7"/);
  assert.match(badge, /Centre 310\.00 eV lies outside the fitted data \(282\.00–293\.00 eV\)/);
  assert.match(badge, /Nothing has been moved/);
});

// WARN, NEVER REINTERPRET — structural guards on the new helpers
test('the helpers write nothing: no assignment to a field value, a peak or the fit state', () => {
sed: tests/js/lib/extract.js: No such file or directory
3241:    this._restoreUI(tab.ui);
3483:      this._restoreUI(active.ui);
3845:  _restoreUI(ui) {
6737:function _showAutoFitConfirmModal(peakCount) {
7573:    const proceed = await _showAutoFitConfirmModal(state.peaks.length);
10885:  // restore below: _restoreUI refreshes the manual-anchor count label from
10897:  tabManager._restoreUI(active.ui);
12459:      tabManager._restoreUI(tgt.ui);
16294:// _showAutoFitConfirmModal/_autoFitConfirmCancel.
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
    61	 from scipy.integrate import trapezoid
    62	 
    63	@@ -637,6 +638,17 @@ class FittedComponent:
    64	     amplitude: float
    65	     shape_params: dict
    66	     line_shape: Optional[LineShape] = None
    67	+    # Unit F3 (2026-09-27): does the fit that produced this component need it?
    68	+    # fitting._component_support on that fit — with the other components held
    69	+    # as fitted, removing this one must make the fit significantly worse (F >=
    70	+    # SUPPORT_MIN_F). The occupancy decisions (slot matching, the proposal
    71	+    # gate, detectability) read this instead of an absolute amplitude floor
    72	+    # of 1 count, which judged a slot "occupied" at amplitude 1.5 and not at
    73	+    # 0.5 whatever the data's scale (sweep M9; design rule "thresholds on
    74	+    # data-scaled quantities fail"). None only where no fit is behind the
    75	+    # component (hand-built in tests): then occupancy falls back to amplitude
    76	+    # > 0, a sign test.
    77	+    support: Optional[dict] = None
    78	 
    79	 
    80	 @dataclass
    81	@@ -652,10 +664,50 @@ class FitOutcome:
    82	     boundary_hits: list[str] = field(default_factory=list)
    83	 
    84	 
    85	+def _component_supports(result: ModelResult) -> dict[str, dict]:
    86	+    """``fitting._component_support`` for every peak component of an lmfit
    87	+    result, keyed by prefix — the one definition the server uses (step (b)).
    88	+    Empty when the result carries no data (never raises: occupancy then falls
    89	+    back to the sign test)."""
    90	+    try:
    91	+        comps = result.eval_components()
    92	+        data = np.asarray(result.data, float)
    93	+        fitted = np.asarray(result.best_fit, float)
    94	+        w = result.weights if result.weights is not None else np.ones_like(data)
    95	+        w = np.broadcast_to(np.asarray(w, float), data.shape)
    96	+        n_free_total = int(result.nvarys)
    97	+    except Exception:
    98	+        return {}
    99	+    out = {}
   100	+    for prefix, comp_y in comps.items():
   101	+        n_free_comp = sum(1 for n, par in result.params.items()
   102	+                          if n.startswith(prefix) and par.vary and par.expr is None)
   103	+        try:
   104	+            out[prefix] = _fitting._component_support(data, fitted, np.asarray(comp_y, float), w,
   105	+                                                      n_free_comp, n_free_total)
   106	+            out[prefix]["_p"] = max(1, n_free_comp)
   107	+        except Exception:
   108	+            continue
   109	+    return out
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

exec
/bin/zsh -lc "sed -n '3838,3888p' templates/index.html; sed -n '6734,6795p' templates/index.html; rg -n 'function updatePlot|renderPeakList\\(' templates/index.html | tail -35; sed -n '1280,1350p' autofit/engine.py; rg -n 'orphan_peaks|active_min_persistence|absent_slots' autofit/engine.py | head -40; git show sweep-fail-open-guards:docs/findings/2026-09-25-fail-open-guards-sweep.md | rg -n -A 20 -B 2 'M5|M9'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
      ccMethod:    document.getElementById('cc-method')?.value || 'none',
      ccObs:       document.getElementById('cc-obs')?.value || '',
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
2459:  renderPeakList();
2475:  renderPeakList();
3264:    renderPeakList();
3312:      renderPeakList();
3484:      renderPeakList();
5063:  renderPeakList();
5244:  renderPeakList();
5853:    renderPeakList();
5919:  renderPeakList();
5936:  renderPeakList();
5948:  renderPeakList();
5959:  renderPeakList();
5971:  renderPeakList();
6069:  renderPeakList();
6115:function renderPeakList() {
7056:  if (typeof renderPeakList === 'function') renderPeakList();
7384:  if (typeof renderPeakList === 'function') renderPeakList();
7624:  renderPeakList();
8308:  renderPeakList();
8814:  renderPeakList();
9750:function updatePlot() {
10913:  renderPeakList();
12460:      renderPeakList();
14404:  renderPeakList();
16419:  renderPeakList();
# Absent slots
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AbsentSlotReport:
    role: str
    persistence: float
    fitted_area: float
    main_area: float
    area_fraction: float
    threshold: float
    removed_n_params: int


def _count_slot_free_params(slot: ComponentSlot, primary: FitOutcome) -> int:
    if primary.lmfit_result is None:
        return 0
    prefix = _slot_prefix(slot.role)
    return sum(1 for pname, par in primary.lmfit_result.params.items()
               if pname.startswith(prefix) and par.vary)


def _is_main_role(role: str) -> bool:
    """Main-slot convention: bare role or region-prefixed role starts 'main'."""
    return role.split("__")[-1].startswith("main")


def _linked_groups(model: CandidateModel) -> list[list[ComponentSlot]]:
    """
    Connected components of non-main slots over ``linked_to`` edges (edges
    touching a main slot do not bind — mains are never absent-eligible, so a
    satellite linked to a main is its own group; a satellite DOUBLET
    (sat5/2 → sat7/2) is one group).
    """
    non_main = [s for s in model.slots if not _is_main_role(s.role)]
    roles = {s.role for s in non_main}
    parent_of = {s.role: s.linked_to for s in non_main
                 if s.linked_to is not None and s.linked_to in roles}

    def root(role: str) -> str:
        while role in parent_of:
            role = parent_of[role]
        return role

    groups: dict[str, list[ComponentSlot]] = {}
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
1330:def _identify_absent_slots(
1441:    orphan_peaks: bool = False
1497:    absent_slots: list[AbsentSlotReport] = field(default_factory=list)
1513:        removed = sum(a.removed_n_params for a in self.absent_slots)
1569:    def active_min_persistence(self) -> float:
1570:        absent_roles = {a.role for a in self.absent_slots}
1668:        active_min = r.active_min_persistence
1671:                or r.plausibility.orphan_peaks:
1672:            # orphan_peaks included (Codex Stage-2 re-review finding #3):
1680:            absent_roles = [a.role for a in r.absent_slots]
1701:        # label instability (orphan_peaks) on heavily-overlapped low-res
2314:    absent = _identify_absent_slots(
2325:            orphan_peaks=stability.orphan_rate > 0.1,
2327:        absent_slots=absent, augmented_from=base_model.name,
2467:            orphan_peaks=stability.orphan_rate > 0.1,
2469:        absent_slots=[],                      # conservative full-k BIC*
2502:            and r.active_min_persistence >= persistence_threshold]
2514:        if refit.active_min_persistence < persistence_threshold:
2842:        absent = _identify_absent_slots(
2853:                orphan_peaks=stability.orphan_rate > 0.1,
2855:            absent_slots=absent,
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-CO2C1aS6' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-tiXrAVX5' (errno=Operation not permitted)
121-  uncertainty warning and every σ in Results and CSV/XLSX disappears.
122-
123:**M5. Auto-Fit's C 1s gate judges a stale, typed window** (page; R-me in a
124-browser; consequence R server-side only).
125-- `isC1sTab` reads `tab.ui.roiMin/roiMax` (synced only on tab switch or
126-  save) and tests the TYPED midpoint, not the data selected;
127-  `findGraphiteRawBE` takes the highest strong maximum in the live window;
128-  nothing bounds the provisional shift.
129-- Browser (mine): wide scan 270–420 eV (small C 1s + U 4f doublet), record
130-  ROI 280–295, ROI typed 370–415 with no tab switch → the Auto-Fit menu is
131-  ENABLED and the gate passes. In 3 of 3 constructions the step (c) refit
132-  then refused the fake anchor (F 0.1–2.5; nothing applied). The server
133-  construction of the page-code pass (U 4f₅/₂ taken as "Graphite",
134-  provisional shift 107.3 eV) passed support (F 2096) AND required
135-  (F 384) — every gate in `applyAutoFitResult` passes, so a ~107 eV charge
136-  correction would follow; the page-side apply of THAT construction was
137-  not run.
138-- Rated MEDIUM on the evidence (the gate is open; the downstream checks
139-  held on the page in every run I made); its consequence class is HIGH.
140-- Closing it: gate on the live `getROIData()` selection; require a
141-  plausible provisional shift.
142-
143-**M6. Auto-Fit has no "model edited mid-fit" discard** (page; C). `runFit`
--
160-start − 2 eV, on the refit users routinely run.
161-
162:**M9. Find Peaks** (server + page).
163-- The absolute `noise_floor = 1.0` (never sent by the page) decides
164-  whether a slot is "occupied" and so drives persistence, the absent-slot
165-  test and the stability gate: `main_graphitic` occupied at amplitude 1.5
166-  counts, not at 0.5, whatever the data's scale (R). The Design Rules case
167-  exactly ("thresholds on data-scaled quantities fail").
168-- Persistence = occupied / refits ATTEMPTED; the 25 s per-candidate
169-  deadline can stop refits early and `n_attempted` / `timed_out` are not
170-  reported; `n_refits` can be set to 1 → persistence 1.0, the 0.7 gate
171-  passes, "stable across re-fits" (C).
172-- `_fpPlainMessage` says "passed every check cleanly — stable across
173-  re-fits…" unless one of five flags is set; it ignores
174-  `weighted_ic_disagreement` (rendered nowhere), `model_selection_warning`
175-  (a banner shows while the text says "passed"), ambiguous pairs,
176-  residual/autocorrelation flags, `bic_ambiguous` / `criteria_conflict`,
177-  `candidate_pool.error`; `sparse_map` returns `success: true` when its λ
178-  did not converge (C).
179-- `applyFindPeaks` ignores `body.success` ("Refit my current peaks" can
180-  return a non-converged fit's peaks and σ) (C).
181-
182-**M10. A crashed scattered-starts check looks like "not applicable"**
--
250-3. **Uncertainty panel coverage** (M4, §1): every varying parameter against
251-   whichever bounds are finite.
252:4. **Auto-Fit gate and bounds** (M5, M8, M7).
253:5. **Find Peaks' verdicts** (M9): the absolute noise floor is a Design
254-   Rules violation and the likely first target.

codex
I reproduced the README’s key failure using both patches in memory: F gives P3’s third component F = 9.417, drops its persistence to zero, and returns P2 with `conditional: false`. Baseline returns `P3+bfix` with `conditional: true`. I’m finishing the LR comparison and targeted gate edge cases; no files have been changed.

 succeeded in 30951ms:
/Users/skyefortier/.matplotlib is not a writable directory
baseline P1 redchi 468.684 persistence 1.0 orphan 0.0
baseline P2 redchi 308.747 persistence 1.0 orphan 0.0
baseline P3 redchi 284.122 persistence 1.0 orphan 0.0
RESULT baseline True P3+bfix True decisive_override
F_support_test P1 redchi 468.684 persistence 1.0 orphan 0.0
  main_a {'f': 132.101, 'delta_chi2': 247653.739, 'supported': True}
F_support_test P2 redchi 308.747 persistence 1.0 orphan 0.0
  main_a {'f': 85.291, 'delta_chi2': 105333.113, 'supported': True}
  main_b {'f': 122.788, 'delta_chi2': 151641.429, 'supported': True}
F_support_test P3 redchi 284.122 persistence 0.0 orphan 1.0
  main_a {'f': 114.091, 'delta_chi2': 129663.473, 'supported': True}
  main_b {'f': 113.666, 'delta_chi2': 129179.996, 'supported': True}
  main_c {'f': 9.417, 'delta_chi2': 10702.374, 'supported': False}
RESULT F_support_test True P2 False None
LR_likelihood_ratio P1 redchi 468.684 persistence 1.0 orphan 0.0
  main_a {'f': 132.101, 'delta_chi2': 247653.739, 'supported': True, '_p': 4}
LR_likelihood_ratio P2 redchi 308.747 persistence 1.0 orphan 0.0
  main_a {'f': 85.291, 'delta_chi2': 105333.113, 'supported': True, '_p': 4}
  main_b {'f': 122.788, 'delta_chi2': 151641.429, 'supported': True, '_p': 4}
LR_likelihood_ratio P3 redchi 284.122 persistence 1.0 orphan 0.0
  main_a {'f': 114.091, 'delta_chi2': 129663.473, 'supported': True, '_p': 4}
  main_b {'f': 113.666, 'delta_chi2': 129179.996, 'supported': True, '_p': 4}
  main_c {'f': 9.417, 'delta_chi2': 10702.374, 'supported': False, '_p': 4}
RESULT LR_likelihood_ratio True P3+bfix True decisive_override

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\''),cp=require('\\''child_process'\\''),vm=require('\\''vm'\\''),path=require('\\''path'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
function extract(name){const lines=html.split('\\''\\n'\\''),s=lines.findIndex(x=>x.startsWith('\\''function '\\''+name+'\\''('\\''));let d=0;for(let i=s;i<lines.length;i++){for(const c of lines[i]){if(c==='\\''{'\\'')d++;if(c==='\\''}'\\'')d--;}if(d===0)return lines.slice(s,i+1).join('\\''\\n'\\'');}}
const dom={'\\''roi-min'\\'':{value:'\\'''\\''},'\\''roi-max'\\'':{value:'\\'''\\''}};
const state={rawBE:[],rawIntensity:[],ccShift:0},tabManager={activeId:'\\''t'\\''};
const api=new Function('\\''state'\\'','\\''document'\\'','\\''tabManager'\\'',['\\''getCorrectedBE'\\'','\\''getROIData'\\'','\\''isC1sTab'\\''].map(extract).join('\\''\\n'\\'')+'\\'';return {getROIData,isC1sTab};'\\'')(state,{getElementById:id=>dom[id]},tabManager);
function run(label,raw,lo,hi,shift=0){state.rawBE=raw;state.rawIntensity=raw.map(()=>1);state.ccShift=shift;dom['\\''roi-min'\\''].value=lo;dom['\\''roi-max'\\''].value=hi;const tab={id:'\\''t'\\'',rawBE:raw,ccShift:shift,ui:{roiMin:lo,roiMax:hi}};const n=api.getROIData().be.length;tabManager.activeId='\\''t'\\'';const active=api.isC1sTab(tab);tabManager.activeId='\\''other'\\'';const record=api.isC1sTab(tab);console.log(label,{n,active,record});}
const raw=Array.from({length:301},(_,i)=>270+i*.5);
run('\\''reversed'\\'',raw,'\\''295'\\'','\\''280'\\'');
run('\\''upper only'\\'',raw,'\\'''\\'','\\''295'\\'');
run('\\''lower only outside narrow scan'\\'',[280,290,300],'\\''350'\\'','\\'''\\'');
run('\\''both blank narrow'\\'',[280,290,300],'\\'''\\'','\\'''\\'');
run('\\''both blank wide'\\'',raw,'\\'''\\'','\\'''\\'');
run('\\''outside'\\'',raw,'\\''500'\\'','\\''600'\\'');
run('\\''charge shift'\\'',[380,390,395],'\\''280'\\'','\\''295'\\'',100);
run('\\''inclusive endpoint'\\'',[280,290,300],'\\''300'\\'','\\''300'\\'');
run('\\''stack'\\'',[],'\\'''\\'','\\'''\\'');
run('\\''survey whole'\\'',Array.from({length:1201},(_,i)=>i),'\\'''\\'','\\'''\\'');
run('\\''survey C1s'\\'',Array.from({length:1201},(_,i)=>i),'\\''280'\\'','\\''295'\\'');
const large={id:'\\''other'\\'',rawBE:Array.from({length:1000000},(_,i)=>270+30*i/999999),ccShift:0,ui:{roiMin:'\\''280'\\'',roiMax:'\\''295'\\''}};
tabManager.activeId='\\''t'\\'';let t=performance.now();console.log('\\''million point record'\\'',api.isC1sTab(large),'\\''ms'\\'',performance.now()-t);
const old=cp.execFileSync('\\''git'\\'',['\\''show'\\'','\\''07e0839:templates/index.html'\\''],{encoding:'\\''utf8'\\'',stdio:['\\''ignore'\\'','\\''pipe'\\'','\\''ignore'\\'']});
const testFile=path.resolve('\\''tests/js/autofit_c1s_gate.test.js'\\''),testText=fs.readFileSync(testFile,'\\''utf8'\\'');let passed=0,failed=0;
const req=name=>name==='\\''node:fs'\\''?{...fs,readFileSync:()=>old}:name==='\\''node:test'\\''?{test:(title,fn)=>{try{fn();passed++}catch(e){failed++;console.log('\\''OLD FAIL'\\'',title)}}}:require(name);
vm.runInNewContext(testText,{require:req,__dirname:path.dirname(testFile),console});
console.log('\\''old implementation'\\'', {passed,failed});
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 177ms:
million point record true ms 111.16839599999999
OLD FAIL the sweep reproduction: record window on C 1s, U 4f typed in the fields (no tab switch) — the gate CLOSES
OLD FAIL the SELECTED data decide, not the typed midpoint of a window that reaches past the data
OLD FAIL a non-active record is judged on its saved window over its own corrected data
old implementation { passed: 1, failed: 3 }

exec
/bin/zsh -lc 'node --test tests/js/autofit_c1s_gate.test.js tests/js/roi_clamp_centre_warning.test.js tests/js/autofit_required.test.js tests/js/autofit_zero_graphite.test.js tests/js/unsupported_components.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 203ms:
# Subtest: the sweep reproduction: record window on C 1s, U 4f typed in the fields (no tab switch) — the gate CLOSES
ok 1 - the sweep reproduction: record window on C 1s, U 4f typed in the fields (no tab switch) — the gate CLOSES
  ---
  duration_ms: 7.423498
  type: 'test'
  ...
# Subtest: the SELECTED data decide, not the typed midpoint of a window that reaches past the data
ok 2 - the SELECTED data decide, not the typed midpoint of a window that reaches past the data
  ---
  duration_ms: 1.49472
  type: 'test'
  ...
# Subtest: a non-active record is judged on its saved window over its own corrected data
ok 3 - a non-active record is judged on its saved window over its own corrected data
  ---
  duration_ms: 1.016944
  type: 'test'
  ...
# Subtest: every caller of the gate is for the active tab (menu state, charge-reference permission, the Auto-Fit run)
ok 4 - every caller of the gate is for the active tab (menu state, charge-reference permission, the Auto-Fit run)
  ---
  duration_ms: 2.527166
  type: 'test'
  ...
# Subtest: a supported but NOT required anchor is refused before any charge-correction input is touched
ok 5 - a supported but NOT required anchor is refused before any charge-correction input is touched
  ---
  duration_ms: 6.805552
  type: 'test'
  ...
# Subtest: a required anchor proceeds; a check that did not RUN (older server, error, main fit not converged) does not block
ok 6 - a required anchor proceeds; a check that did not RUN (older server, error, main fit not converged) does not block
  ---
  duration_ms: 11.368015
  type: 'test'
  ...
# Subtest: the request asks for the Graphite anchor by id, and the gate precedes the support gate and every cc write
ok 7 - the request asks for the Graphite anchor by id, and the gate precedes the support gate and every cc write
  ---
  duration_ms: 0.996059
  type: 'test'
  ...
# Subtest: a refit that did not converge: no verdict, and Auto-Fit refuses before any charge-correction input is touched
ok 8 - a refit that did not converge: no verdict, and Auto-Fit refuses before any charge-correction input is touched
  ---
  duration_ms: 2.197814
  type: 'test'
  ...
# Subtest: the fixture set covers both outcomes
ok 9 - the fixture set covers both outcomes
  ---
  duration_ms: 1.961099
  type: 'test'
  ...
# Subtest: anchors NOTHING — residue: 1e7 flat, 1e-4 bump rounded away, manual background (round 5)
ok 10 - anchors NOTHING — residue: 1e7 flat, 1e-4 bump rounded away, manual background (round 5)
  ---
  duration_ms: 6.840014
  type: 'test'
  ...
# Subtest: anchors NOTHING — residue: 10.009999 flat uploaded as 10.01, unrounded manual background (round 3)
ok 11 - anchors NOTHING — residue: 10.009999 flat uploaded as 10.01, unrounded manual background (round 3)
  ---
  duration_ms: 3.102369
  type: 'test'
  ...
# Subtest: anchors NOTHING — residue: 10 + 1e-4 bump, linear background (round 2)
ok 12 - anchors NOTHING — residue: 10 + 1e-4 bump, linear background (round 2)
  ---
  duration_ms: 3.146081
  type: 'test'
  ...
# Subtest: anchors NOTHING — collapsed model: 30-count bump, manual background over-estimated at 1020 (round 1)
ok 13 - anchors NOTHING — collapsed model: 30-count bump, manual background over-estimated at 1020 (round 1)
  ---
  duration_ms: 1.557605
  type: 'test'
  ...
# Subtest: anchors the correction — resolved 0.0058 line on a zero background, 17 samples survive the upload (round 5)
ok 14 - anchors the correction — resolved 0.0058 line on a zero background, 17 samples survive the upload (round 5)
  ---
  duration_ms: 2.020605
  type: 'test'
  ...
# Subtest: anchors the correction — resolved 50-count line on a noise-free 1e6 background (round 4)
ok 15 - anchors the correction — resolved 50-count line on a noise-free 1e6 background (round 4)
  ---
  duration_ms: 1.528962
  type: 'test'
  ...
# Subtest: anchors the correction — resolved 10 000-count line on a steep noisy ramp, 100 scans averaged (round 2)
ok 16 - anchors the correction — resolved 10 000-count line on a steep noisy ramp, 100 scans averaged (round 2)
  ---
  duration_ms: 1.792693
  type: 'test'
  ...
# Subtest: anchors the correction — resolved 10 000-count anchor behind a 300 000-count one-channel spike (round 3)
ok 17 - anchors the correction — resolved 10 000-count anchor behind a 300 000-count one-channel spike (round 3)
  ---
  duration_ms: 2.102104
  type: 'test'
  ...
# Subtest: anchors the correction — ordinary C 1s: 86 000-count graphite line with Poisson noise
ok 18 - anchors the correction — ordinary C 1s: 86 000-count graphite line with Poisson noise
  ---
  duration_ms: 1.412486
  type: 'test'
  ...
# Subtest: an anchor amplitude of 0 is refused before anything is computed
ok 19 - an anchor amplitude of 0 is refused before anything is computed
  ---
  duration_ms: 1.012553
  type: 'test'
  ...
# Subtest: an anchor amplitude of -5 is refused before anything is computed
ok 20 - an anchor amplitude of -5 is refused before anything is computed
  ---
  duration_ms: 0.809705
  type: 'test'
  ...
# Subtest: an anchor amplitude of NaN is refused before anything is computed
ok 21 - an anchor amplitude of NaN is refused before anything is computed
  ---
  duration_ms: 0.893988
  type: 'test'
  ...
# Subtest: an anchor amplitude of Infinity is refused before anything is computed
ok 22 - an anchor amplitude of Infinity is refused before anything is computed
  ---
  duration_ms: 0.795152
  type: 'test'
  ...
# Subtest: a response that lacks the fitted data or the component curve cannot vouch for an anchor
ok 23 - a response that lacks the fitted data or the component curve cannot vouch for an anchor
  ---
  duration_ms: 2.301562
  type: 'test'
  ...
# Subtest: an exact fit that needs the component is supported (chi-square with it is zero)
ok 24 - an exact fit that needs the component is supported (chi-square with it is zero)
  ---
  duration_ms: 1.00369
  type: 'test'
  ...
# Subtest: removing a component that costs nothing is the definition of unsupported
ok 25 - removing a component that costs nothing is the definition of unsupported
  ---
  duration_ms: 0.935702
  type: 'test'
  ...
# Subtest: the support check precedes every write of the charge-correction inputs
ok 26 - the support check precedes every write of the charge-correction inputs
  ---
  duration_ms: 0.455703
  type: 'test'
  ...
# Subtest: the fallback "first peak" anchor is held to the same rule
ok 27 - the fallback "first peak" anchor is held to the same rule
  ---
  duration_ms: 1.389984
  type: 'test'
  ...
# Subtest: rolling back to a Custom reference shows its target field again
ok 28 - rolling back to a Custom reference shows its target field again
  ---
  duration_ms: 0.820593
  type: 'test'
  ...
# Subtest: an ROI inside the data: no hint
ok 29 - an ROI inside the data: no hint
  ---
  duration_ms: 7.990213
  type: 'test'
  ...
# Subtest: an ROI past the data by more than one step: the quiet hint names the window actually used
ok 30 - an ROI past the data by more than one step: the quiet hint names the window actually used
  ---
  duration_ms: 3.395367
  type: 'test'
  ...
# Subtest: one side past the data is enough; the window named is the selected data
ok 31 - one side past the data is enough; the window named is the selected data
  ---
  duration_ms: 3.067308
  type: 'test'
  ...
# Subtest: a sub-step overshoot (a toFixed(1) rounding of the data edge) is not "past the data"
ok 32 - a sub-step overshoot (a toFixed(1) rounding of the data edge) is not "past the data"
  ---
  duration_ms: 6.164486
  type: 'test'
  ...
# Subtest: min above max: amber, no data selected (getROIData selects nothing)
ok 33 - min above max: amber, no data selected (getROIData selects nothing)
  ---
  duration_ms: 3.149383
  type: 'test'
  ...
# Subtest: an ROI that misses the data entirely: amber, names the data range
ok 34 - an ROI that misses the data entirely: amber, names the data range
  ---
  duration_ms: 1.87377
  type: 'test'
  ...
# Subtest: empty fields mean the full range (as getROIData): no hint
ok 35 - empty fields mean the full range (as getROIData): no hint
  ---
  duration_ms: 1.895214
  type: 'test'
  ...
# Subtest: the window is in the CORRECTED frame (raw − ccShift), as the fit and Find Peaks use it
ok 36 - the window is in the CORRECTED frame (raw − ccShift), as the fit and Find Peaks use it
  ---
  duration_ms: 3.78119
  type: 'test'
  ...
# Subtest: a descending acquisition behaves the same
ok 37 - a descending acquisition behaves the same
  ---
  duration_ms: 2.257815
  type: 'test'
  ...
# Subtest: centre outside the SELECTED data is flagged; inside, at the edges, or with no data selected is not
ok 38 - centre outside the SELECTED data is flagged; inside, at the edges, or with no data selected is not
  ---
  duration_ms: 4.655796
  type: 'test'
  ...
# Subtest: the helpers write nothing: no assignment to a field value, a peak or the fit state
ok 39 - the helpers write nothing: no assignment to a field value, a peak or the fit state
  ---
  duration_ms: 1.661563
  type: 'test'
  ...
# Subtest: the fit and Find Peaks still read the ROI exactly as before (getROIData / the two field values)
ok 40 - the fit and Find Peaks still read the ROI exactly as before (getROIData / the two field values)
  ---
  duration_ms: 1.574503
  type: 'test'
  ...
# Subtest: an unsupported component: the badge warns without reporting its suppressed centre
ok 41 - an unsupported component: the badge warns without reporting its suppressed centre
  ---
  duration_ms: 1.885364
  type: 'test'
  ...
# Subtest: manual fit and Find Peaks select the same points whenever no energy lies within 5e-5 eV of an ROI edge
ok 42 - manual fit and Find Peaks select the same points whenever no energy lies within 5e-5 eV of an ROI edge
  ---
  duration_ms: 8.04504
  type: 'test'
  ...
# Subtest: …and can differ by one edge point, IN EITHER DIRECTION, when an energy lies within 5e-5 eV of an edge (pre-existing, logged, not changed)
ok 43 - …and can differ by one edge point, IN EITHER DIRECTION, when an energy lies within 5e-5 eV of an edge (pre-existing, logged, not changed)
  ---
  duration_ms: 6.286992
  type: 'test'
  ...
# Subtest: the twin reproduces the server verdict on real responses, and defers to the server field when present
ok 44 - the twin reproduces the server verdict on real responses, and defers to the server field when present
  ---
  duration_ms: 13.42075
  type: 'test'
  ...
# Subtest: _applySupport writes every peak, follows ancestry to the root, stamps the fit key, and leaves null where the response says nothing
ok 45 - _applySupport writes every peak, follows ancestry to the root, stamps the fit key, and leaves null where the response says nothing
  ---
  duration_ms: 7.849352
  type: 'test'
  ...
# Subtest: the verdict applies only to the model and context it was computed for
ok 46 - the verdict applies only to the model and context it was computed for
  ---
  duration_ms: 4.75344
  type: 'test'
  ...
# Subtest: the local engine computes the same statistic from its own residuals
ok 47 - the local engine computes the same statistic from its own residuals
  ---
  duration_ms: 6.952514
  type: 'test'
  ...
# Subtest: sidebar card: badge; centre and width shown as a dash; area % excluded and the others renormalised
ok 48 - sidebar card: badge; centre and width shown as a dash; area % excluded and the others renormalised
  ---
  duration_ms: 5.821322
  type: 'test'
  ...
# Subtest: results table: greyed row, no centre / width / sigma, area kept, percentage dash, and the note beneath
ok 49 - results table: greyed row, no centre / width / sigma, area kept, percentage dash, and the note beneath
  ---
  duration_ms: 14.275371
  type: 'test'
  ...
# Subtest: uncertainty panel: one rule-0 warning for the component, no per-parameter alarms and no "locked" note for it
ok 50 - uncertainty panel: one rule-0 warning for the component, no per-parameter alarms and no "locked" note for it
  ---
  duration_ms: 6.720124
  type: 'test'
  ...
# Subtest: Quantify: excluded from the body, listed beneath with the reason; total and percentages over the rest
ok 51 - Quantify: excluded from the body, listed beneath with the reason; total and percentages over the rest
  ---
  duration_ms: 7.087858
  type: 'test'
  ...
# Subtest: CSV / XLSX export: Status column, suppressed cells, At% empty, WARNING line
ok 52 - CSV / XLSX export: Status column, suppressed cells, At% empty, WARNING line
  ---
  duration_ms: 7.667693
  type: 'test'
  ...
# Subtest: publication figure: no label at the (zero) component, legend entry says so; chart and stack labels say so
ok 53 - publication figure: no label at the (zero) component, legend entry says so; chart and stack labels say so
  ---
  duration_ms: 2.754709
  type: 'test'
  ...
# Subtest: write-back: a server result sets support; the local engine and a propagated model reset it
ok 54 - write-back: a server result sets support; the local engine and a propagated model reset it
  ---
  duration_ms: 1.567659
  type: 'test'
  ...
# Subtest: persistence: support travels with the peak object through every save (the peak is spread whole)
ok 55 - persistence: support travels with the peak object through every save (the peak is spread whole)
  ---
  duration_ms: 1.071613
  type: 'test'
  ...
# Subtest: CSV / XLSX: an unsupported DS+G component exports no width of any kind (beta, m)
ok 56 - CSV / XLSX: an unsupported DS+G component exports no width of any kind (beta, m)
  ---
  duration_ms: 5.587106
  type: 'test'
  ...
# Subtest: the scattered-starts table: an unsupported component shows neither area % nor a move in "Your fit", and is not the largest move
ok 57 - the scattered-starts table: an unsupported component shows neither area % nor a move in "Your fit", and is not the largest move
  ---
  duration_ms: 6.803379
  type: 'test'
  ...
# Subtest: exports: a stale or keyless verdict is "not established", never "supported"
ok 58 - exports: a stale or keyless verdict is "not established", never "supported"
  ---
  duration_ms: 8.890157
  type: 'test'
  ...
# Subtest: Auto-Fit finalisation (locks, charge shift) keeps its own verdicts: _restampSupport, called after the locks
ok 59 - Auto-Fit finalisation (locks, charge shift) keeps its own verdicts: _restampSupport, called after the locks
  ---
  duration_ms: 4.881115
  type: 'test'
  ...
# Subtest: a .fit.json import onto this tab's data carries no verdict
ok 60 - a .fit.json import onto this tab's data carries no verdict
  ---
  duration_ms: 0.24126
  type: 'test'
  ...
# Subtest: _isUnsupported is never handed an array index as its key (Array.filter passes one)
ok 61 - _isUnsupported is never handed an array index as its key (Array.filter passes one)
  ---
  duration_ms: 3.893977
  type: 'test'
  ...
# Subtest: a key change re-renders every consumer of the verdict — each compared with ITS OWN rendering
ok 62 - a key change re-renders every consumer of the verdict — each compared with ITS OWN rendering
  ---
  duration_ms: 2.496414
  type: 'test'
  ...
# Subtest: stack tabs judge a source component against the SOURCE record's key
ok 63 - stack tabs judge a source component against the SOURCE record's key
  ---
  duration_ms: 3.920252
  type: 'test'
  ...
# Subtest: "Your fit" percentages are over supported components; an empty Quantify shows no 100 %
ok 64 - "Your fit" percentages are over supported components; an empty Quantify shows no 100 %
  ---
  duration_ms: 9.740601
  type: 'test'
  ...
# Subtest: the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
ok 65 - the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
  ---
  duration_ms: 4.548417
  type: 'test'
  ...
1..65
# tests 65
# suites 0
# pass 65
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 263.28612

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import sys, re, importlib, importlib.abc, importlib.machinery
from pathlib import Path
sys.path.insert(0, str(Path('\\''tests/autofit'\\'').resolve()))
class Loader(importlib.abc.Loader):
    def __init__(self, source, filename): self.source,self.filename=source,filename
    def create_module(self, spec): return None
    def exec_module(self, module): exec(compile(self.source,self.filename,'\\''exec'\\''),module.__dict__)
class Finder(importlib.abc.MetaPathFinder):
    sources={}
    def find_spec(self, fullname, path, target=None):
        if fullname not in self.sources: return None
        spec=importlib.machinery.PathFinder.find_spec(fullname,path)
        spec.loader=Loader(self.sources[fullname],spec.origin)
        return spec
finder=Finder(); sys.meta_path.insert(0,finder)
def patched_sources(patch):
    out={}
    for block in patch.split('\\''diff --git '\\'')[1:]:
        filename=block.splitlines()[0].split()[1][2:]
        old=Path(filename).read_text().splitlines(True); new=[]; cursor=0
        for h in re.split(r'\\''(?m)"'^@@ '"'\\'',block)[1:]:
            header,body=h.split('\\''\\n'\\'',1); start=int(re.match(r'\\''-(\\d+)'\\'',header).group(1))-1
            new.extend(old[cursor:start]); cursor=start
            for line in body.splitlines(True):
                if line.startswith('\\'' '\\''):
                    assert old[cursor]==line[1:], (filename,cursor,line)
                    new.append(line[1:]); cursor+=1
                elif line.startswith('\\''-'\\''):
                    assert old[cursor]==line[1:], (filename,cursor,line)
                    cursor+=1
                elif line.startswith('\\''+'\\''): new.append(line[1:])
        new.extend(old[cursor:]); out[filename[:-3].replace('\\''/'\\'','\\''.'\\'')]='\\'''\\''.join(new)
    return out

finder.sources=patched_sources(Path('\\''docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch'\\'').read_text())
from fitting import _component_support
from autofit.engine import FittedComponent, _occupies
from autofit.confidence import build_confidence_vector
from types import SimpleNamespace
import numpy as np
for scale in (1.0, .1):
    y=np.full(20,100.0)*scale
    s=_component_support(y,np.full(20,90.0)*scale,np.full(20,20.0)*scale,1/np.sqrt(y),4,4)
    s['\\''_p'\\'']=4
    comp=FittedComponent('\\''main'\\'',285,1,20*scale,{},support=s)
    report=SimpleNamespace(stability=SimpleNamespace(per_slot={}),primary_fit=SimpleNamespace(components=[comp],boundary_hits=[],lmfit_result=None))
    print('\\''scale'\\'',scale,'\\''gain/p'\\'',s['\\''delta_chi2'\\'']/4,'\\''F'\\'',s['\\''f'\\''],'\\''occupies'\\'',_occupies(comp),'\\''confidence'\\'',build_confidence_vector(report,'\\''main'\\'',1)['\\''detectability'\\''])
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
exec
/bin/zsh -lc "nl -ba docs/findings/noise-floor-occupancy/README.md | head -90; rg -n '\\.contains\\(' --glob '*.py' . | head -30; sed -n '1,88p' autofit/confidence.py; sed -n '9750,9778p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
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
./tests/test_browser_identify_frame.py:219:        light: document.body.classList.contains('light-theme'),
./tests/test_browser_identify_frame.py:229:            light: document.body.classList.contains('light-theme'),
./tests/test_browser_identify_frame.py:241:        page.evaluate("""() => { if (document.body.classList.contains('light-theme')) toggleTheme();
./tests/test_browser_identify_frame.py:511:        return { mode: placeMode, cls: p.classList.contains('identify-passthrough'),
./tests/test_browser_palette.py:174:        assert pg.evaluate("() => document.getElementById('ref-panel').classList.contains('collapsed')") is True
./tests/test_browser_palette.py:182:            return { collapsed: p.classList.contains('collapsed'),
./tests/test_browser_palette.py:204:            const dragging = p.classList.contains('dragging');
./tests/test_browser_palette.py:222:            return { passthrough: p.classList.contains('identify-passthrough'),
./tests/test_browser_palette.py:241:            return { mode: placeMode, passthrough: p.classList.contains('identify-passthrough'),
./tests/test_browser_batch_roi.py:237:                toastShown: document.getElementById('prominent-toast').classList.contains('show'),
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
function updatePlot() {
  // Stack-tab early branch: render multi-spectrum overlay, no peaks/fits.
  // Route through _updateStackChart so toolbar-pill toggles (Envelope,
  // Individual Peaks, Fill, Bkgrd Sub) and other state changes preserve
  // zoom by in-place updating. _updateStackChart delegates to
  // _renderStackChart automatically when no chart exists.
  {
    const _activeTab = (typeof tabManager !== 'undefined') ? tabManager._getTab(tabManager.activeId) : null;
    const _emptyEl = document.getElementById('stack-empty-state');
    const _canvas = document.getElementById('mainChart');
    if (isStackTab(_activeTab)) {
      _refreshRoiHint(null);   // a stack tab has no ROI of its own
      _updateStackChart(_activeTab);
      return;
    } else {
      if (_canvas) _canvas.style.display = '';
      if (_emptyEl) _emptyEl.style.display = 'none';
    }
  }

  // Full corrected spectrum (for raw data display and axis range)
  const corrBE = getCorrectedBE();
  const fullInten = state.rawIntensity;

  // ROI-filtered data (for fitting, background, peaks)
  const { be, inten } = getROIData();
  const invert = document.getElementById('invert-be').checked;
  const showIndividual = document.getElementById('show-individual').checked;
  const showResiduals = document.getElementById('show-residuals').checked;

 exited 1 in 1966ms:
/Users/skyefortier/.matplotlib is not a writable directory
Traceback (most recent call last):
  File "<string>", line 48, in <module>
  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/autofit/confidence.py", line 120, in build_confidence_vector
    "fwhm_mad": sstab.fwhm_mad,
              ^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/autofit/confidence.py", line 38, in _sigma_stat_for_slot
    slot = report.model.slot_by_role(role)
           ^^^^^^^^^^^^
AttributeError: 'types.SimpleNamespace' object has no attribute 'model'

exec
/bin/zsh -lc "rg -n -A 65 '"'^def bg_mismatch_case'"' tests/autofit/stress_cases.py; sed -n '120,139p' tests/autofit/test_stress_honesty.py; sed -n '33,66p' autofit/methods/ic_model_comparison.py; rg -n 'weights =|maximum\\(y' autofit/engine.py | tail -15; git status --short" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
404:def bg_mismatch_case(seed: int) -> StressCase:
405-    x = _grid()
406-    truth = [{"center": 197.2, "fwhm": 1.2, "height": 9000.0},
407-             {"center": 198.9, "fwhm": 1.2, "height": 6300.0}]
408-    sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
409-    y = _noisy(sig + _shirley_like_bg(x, sig), seed)
410-    return StressCase(
411-        name="bg_shirley_truth_linear_fit",
412-        regime="bg_mismatch", expectation="honesty",
413-        x=x, y=y, truth=truth, truth_n=2,
414-        grammar=_grammar(_n_peak_ladder(197.2, 198.9, n_max=3)),  # LINEAR bg
415-        ls_specs=_ls_specs(truth),
416-        true_candidates=("P2",),
417-        bg="shirley_like",
418-        notes="integral background fit with a straight line — the mismatch "
419-              "must surface, not silently vanish",
420-    )
421-
422-
423-def bg_matched_control_case(seed: int) -> StressCase:
424-    """Control for the mismatch case: same truth, Shirley-candidate fits.
425-    The engine's iterative Shirley should absorb the integral background."""
426-    x = _grid()
427-    truth = [{"center": 197.2, "fwhm": 1.2, "height": 9000.0},
428-             {"center": 198.9, "fwhm": 1.2, "height": 6300.0}]
429-    sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
430-    y = _noisy(sig + _shirley_like_bg(x, sig), seed)
431-    cands = _n_peak_ladder(197.2, 198.9, n_max=3, bg=BackgroundType.SHIRLEY)
432-    return StressCase(
433-        name="bg_shirley_truth_shirley_fit",
434-        regime="bg_mismatch", expectation="recover",
435-        x=x, y=y, truth=truth, truth_n=2,
436-        grammar=_grammar(cands),
437-        ls_specs=_ls_specs(truth),
438-        true_candidates=("P2",),
439-        bg="shirley_like",
440-        notes="control: matched background family",
441-    )
442-
443-
444-# ─────────────────────────────────────────────────────────────────────────────
445-# The roster
446-# ─────────────────────────────────────────────────────────────────────────────
447-
448-def build_all_cases(seed_offset: int = 0) -> list[StressCase]:
449-    """The full battery roster (seeds fixed; deterministic).  A nonzero
450-    ``seed_offset`` regenerates the SAME truths under fresh noise draws —
451-    conclusion-stability replicates for the battery."""
452-    o = seed_offset
453-    return [
454-        # heavy overlap — resolvable at wide separation/high counts,
455-        # honestly ambiguous at 0.4×FWHM with low counts
456-        overlap_case(1.0, 9000.0, seed=11 + o, expectation="recover"),
457-        overlap_case(0.7, 9000.0, seed=12 + o, expectation="recover"),
458-        # 0.4×FWHM at high counts: a-priori labeled ambiguous, but the
459-        # 2026-07-04 battery measured the EVIDENCE decisively favoring P2
460-        # on every noise draw (ΔBIC* 74-97, P2 stable at persistence
461-        # 0.92-1.0) — the data distinguishes; the current filter pipeline
462-        # buries the dominant candidate (orphan matching) → relabeled
463-        # recover; its FAILs are a measured engine deficiency (see
464-        # stress-test-report.md finding on evidence burial), not noise.
465-        overlap_case(0.4, 9000.0, seed=13 + o, expectation="recover"),
466-        # at low counts the parsimony choice genuinely wins the evidence
467-        # (P1 ΔBIC* 5-12 below P2 on every draw) — truly ambiguous
468-        overlap_case(0.4, 900.0, seed=14 + o, expectation="ambiguous"),
469-        # weak minor — detectable at high counts; the low-count case was
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
    label = "Auto — model comparison (IC)"
    requires_grammar = True

    def run(
        self,
        x: np.ndarray,
        y: np.ndarray,
        weights: Optional[np.ndarray] = None,
        grammar: Optional[CandidateGrammar] = None,
        peak_specs: Optional[list[dict]] = None,
        options: Optional[dict[str, Any]] = None,
        progress_cb: Optional[Callable[[dict], None]] = None,
    ) -> MethodResult:
        if grammar is None:
            raise ValueError("ic_model_comparison requires a resolved grammar")
        opts = dict(options or {})
        unknown = set(opts) - _ALLOWED_OPTIONS
        if unknown:
            raise ValueError(f"unknown ic_model_comparison options: {sorted(unknown)}")

        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        w = np.asarray(weights, dtype=float) if weights is not None \
            else poisson_like_weights(y)
        noise_floor = float(opts.pop("noise_floor", 1.0))

        result = compare_models(
            x, y, w, grammar,
            noise_floor=noise_floor,
            n_refits=int(opts.pop("n_refits", 20)),
            rng_seed=int(opts.pop("rng_seed", 0)),
            candidate_filter=opts.pop("candidate_filter", None),
            enable_proposal_pass=bool(opts.pop("enable_proposal_pass", True)),
            enable_preseed=bool(opts.pop("enable_preseed", True)),
879:    weights = np.asarray(weights, dtype=float)
1411:    sigma = np.sqrt(np.maximum(y, noise_floor))
1856:        local_sigma = float(np.median(np.sqrt(np.maximum(y_asc[mask], noise_floor)))) \
2014:    sigma = np.sqrt(np.maximum(y, noise_floor))
2240:    local_sigma = float(np.median(np.sqrt(np.maximum(y[mask], noise_floor)))) \
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-M9AvuTt2' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-WPtcWqYT' (errno=Operation not permitted)
?? docs/autofit/codex/f3_c1s_gate_verdict_runA.md
?? docs/autofit/codex/f3_c1s_gate_verdict_runB.md

codex
The live gate passed the targeted edge cases, including blank fields, reversed bounds, empty selections, charge shifts, stacks, and surveys. Three of the four new tests fail against the old implementation, so they do catch the regression.

The parked recommendation needs qualification: the honesty fixture contains two true peaks. P3’s third component absorbs background mismatch; this case does not show F rejecting a real third peak. LR preserves the conditional warning, but that alone does not establish better occupancy detection.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import sys, re, importlib, importlib.abc, importlib.machinery
from pathlib import Path
sys.path.insert(0, str(Path('\\''tests/autofit'\\'').resolve()))
class Loader(importlib.abc.Loader):
    def __init__(self, source, filename): self.source,self.filename=source,filename
    def create_module(self, spec): return None
    def exec_module(self, module): exec(compile(self.source,self.filename,'\\''exec'\\''),module.__dict__)
class Finder(importlib.abc.MetaPathFinder):
    sources={}
    def find_spec(self, fullname, path, target=None):
        if fullname not in self.sources: return None
        spec=importlib.machinery.PathFinder.find_spec(fullname,path)
        spec.loader=Loader(self.sources[fullname],spec.origin)
        return spec
finder=Finder(); sys.meta_path.insert(0,finder)
def patched_sources(patch):
    out={}
    for block in patch.split('\\''diff --git '\\'')[1:]:
        filename=block.splitlines()[0].split()[1][2:]
        old=Path(filename).read_text().splitlines(True); new=[]; cursor=0
        for h in re.split(r'\\''(?m)"'^@@ '"'\\'',block)[1:]:
            header,body=h.split('\\''\\n'\\'',1); start=int(re.match(r'\\''-(\\d+)'\\'',header).group(1))-1
            new.extend(old[cursor:start]); cursor=start
            for line in body.splitlines(True):
                if line.startswith('\\'' '\\''):
                    assert old[cursor]==line[1:], (filename,cursor,line)
                    new.append(line[1:]); cursor+=1
                elif line.startswith('\\''-'\\''):
                    assert old[cursor]==line[1:], (filename,cursor,line)
                    cursor+=1
                elif line.startswith('\\''+'\\''): new.append(line[1:])
        new.extend(old[cursor:]); out[filename[:-3].replace('\\''/'\\'','\\''.'\\'')]='\\'''\\''.join(new)
    return out

finder.sources=patched_sources(Path('\\''docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch'\\'').read_text())
from fitting import _component_support
from autofit.engine import FittedComponent, _occupies
from autofit.confidence import build_confidence_vector
from types import SimpleNamespace
import numpy as np
for scale in (1.0, .1):
    y=np.full(20,100.0)*scale
    s=_component_support(y,np.full(20,90.0)*scale,np.full(20,20.0)*scale,1/np.sqrt(y),4,4)
    s['\\''_p'\\'']=4
    comp=FittedComponent('\\''main'\\'',285,1,20*scale,{},support=s)
    report=SimpleNamespace(model=SimpleNamespace(slot_by_role=lambda role:None),stability=SimpleNamespace(per_slot={}),primary_fit=SimpleNamespace(components=[comp],boundary_hits=[],lmfit_result=None))
    print('\\''scale'\\'',scale,'\\''gain/p'\\'',s['\\''delta_chi2'\\'']/4,'\\''F'\\'',s['\\''f'\\''],'\\''occupies'\\'',_occupies(comp),'\\''confidence'\\'',build_confidence_vector(report,'\\''main'\\'',1)['\\''detectability'\\''])
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
exec
/bin/zsh -lc "rg -n -A 14 '"'^def poisson_like_weights'"' autofit/*; nl -ba tests/js/autofit_c1s_gate.test.js | tail -15; nl -ba docs/findings/noise-floor-occupancy/variant_F_support_test.patch | sed -n '85,125p'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
autofit/methods/base.py:84:def poisson_like_weights(y: np.ndarray) -> np.ndarray:
autofit/methods/base.py-85-    """
autofit/methods/base.py-86-    1/√max(y,1) weights — matching the existing manual-fit path.  Valid for
autofit/methods/base.py-87-    RAW COUNTS only; for processed spectra prefer an empirical repeat-sweep
autofit/methods/base.py-88-    noise estimate (fitalg LIMITATIONS §8; spec §9) when replicates exist.
autofit/methods/base.py-89-    """
autofit/methods/base.py-90-    return 1.0 / np.sqrt(np.maximum(np.asarray(y, dtype=float), 1.0))
autofit/methods/base.py-91-
autofit/methods/base.py-92-
autofit/methods/base.py-93-# Shared upper bound for endpoint averaging: the Background panel's
autofit/methods/base.py-94-# #bg-endpoint-avg input carries max="50" and the frontend defines the same
autofit/methods/base.py-95-# ENDPOINT_AVG_MAX, so every value the engine accepts is representable by the
autofit/methods/base.py-96-# panel (Codex 2026-09-08 round 2: 1e21 passed both validators while the
autofit/methods/base.py-97-# preview's parseInt read it as 1).
autofit/methods/base.py-98-ENDPOINT_AVG_MAX = 50
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
    85	+def _component_supports(result: ModelResult) -> dict[str, dict]:
    86	+    """``fitting._component_support`` for every peak component of an lmfit
    87	+    result, keyed by prefix — the one definition the server uses (step (b)).
    88	+    Empty when the result carries no data (never raises: occupancy then falls
    89	+    back to the sign test)."""
    90	+    try:
    91	+        comps = result.eval_components()
    92	+        data = np.asarray(result.data, float)
    93	+        fitted = np.asarray(result.best_fit, float)
    94	+        w = result.weights if result.weights is not None else np.ones_like(data)
    95	+        w = np.broadcast_to(np.asarray(w, float), data.shape)
    96	+        n_free_total = int(result.nvarys)
    97	+    except Exception:
    98	+        return {}
    99	+    out = {}
   100	+    for prefix, comp_y in comps.items():
   101	+        n_free_comp = sum(1 for n, par in result.params.items()
   102	+                          if n.startswith(prefix) and par.vary and par.expr is None)
   103	+        try:
   104	+            out[prefix] = _fitting._component_support(data, fitted, np.asarray(comp_y, float), w,
   105	+                                                      n_free_comp, n_free_total)
   106	+        except Exception:
   107	+            continue
   108	+    return out
   109	+
   110	+
   111	+def _occupies(comp: "FittedComponent") -> bool:
   112	+    """A slot is occupied by a component the data support (F3). No threshold
   113	+    on any data-scaled quantity: the support F test where a fit is behind the
   114	+    component, else the sign of its amplitude."""
   115	+    if comp.support is not None:
   116	+        return bool(comp.support.get("supported"))
   117	+    return comp.amplitude > 0
   118	+
   119	+
   120	 def _extract_fitted_components(
   121	     result: ModelResult, model: CandidateModel
   122	 ) -> list[FittedComponent]:
   123	     out: list[FittedComponent] = []
   124	+    supports = _component_supports(result)
   125	     for slot in model.slots:

 succeeded in 1730ms:
/Users/skyefortier/.matplotlib is not a writable directory
scale 1.0 gain/p 40.00000000000001 F 32.0 occupies True confidence {'amplitude': 20.0, 'basis': 'support_f_test', 'support_f': 32.0, 'support_min_f': 10.0, 'status': 'above_floor'}
scale 0.1 gain/p 3.999999999999999 F 31.999999999999986 occupies False confidence {'amplitude': 2.0, 'basis': 'support_f_test', 'support_f': 31.999999999999986, 'support_min_f': 10.0, 'status': 'above_floor'}

codex
No BLOCKER or MAJOR found in the shipped gate change. The parked proposals need further work.

1. **MAJOR — parked: “scale-free Poisson likelihood ratio” overstates the implementation.** [README.md:31](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:31). The LR patch computes a weighted squared-error gain with other components held fixed; it neither evaluates a Poisson likelihood nor refits the reduced model. Dimensionless does not imply invariant under intensity rescaling. In a concrete probe, scaling data, fit, and component by 0.1 changed Δχ²/p from **40 to 4**, flipping LR occupancy; F stayed **32**. All observations remained above the variance floor. This matters for the same spectrum expressed in different intensity units.

2. **MAJOR — parked: LR occupancy and detectability contradict each other.** [variant_LR_likelihood_ratio.patch:31](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch:31), also line 176. Confidence still uses `support.supported`, reports `basis: support_f_test`, and exposes only the F statistic. The probe above produces **unoccupied** alongside **`above_floor`, F = 32**. Proposal rejection can consequently print **“F = 32.00 < 10”**. Use the chosen occupancy statistic consistently, or explicitly expose two distinct assessments.

3. **MAJOR — parked: F reproduces the honesty regression, but the recommendation misinterprets its cause.** [README.md:48](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:48). I reproduced:
   
   | Variant | Winner | Conditional |
   |---|---|---|
   | Baseline | P3+bfix | true |
   | F | P2 | false |
   | LR | P3+bfix | true |
   
   P3’s third component has Δχ² **10,702.374**, F **9.417**; F drops its persistence to zero and orphan rate becomes one. That excludes it from the decisive-override pool, as described. However, the fixture has **two true peaks** ([stress_cases.py:406](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/tests/autofit/stress_cases.py:406)). This demonstrates an honesty flag depending on retaining a background-compensating third component; it does **not** demonstrate F rejecting a real third peak.

4. **MINOR — shipped: inactive records use different ROI semantics.** [templates/index.html:7771](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/templates/index.html:7771). Saved `295–280` is reordered and passes, while the live selector returns nothing. On a 270–420 scan, saved `min=""`, `max=295` uses the whole scan and fails; the live selector selects 270–295 and passes. Mirror independent open bounds and preserve reversed bounds. This is nonblocking because all three current callers pass the active tab.

5. **MINOR — tests: the caller assertion does not establish active-tab ownership.** [autofit_c1s_gate.test.js:60](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/tests/js/autofit_c1s_gate.test.js:60). Replacing a caller’s lookup with an inactive record would still satisfy `/isC1sTab\(tab\)/`. The other three tests are substantive: all three fail against `07e0839`.

The active path behaved correctly with the actual `getROIData()`: inclusive clipping, reversed and empty selections, independently blank bounds, corrected energies, stacks, and surveys. Blank ROI fields still permit Auto-Fit on a narrow C1s scan. Tab activation installs incoming state and fields before menu evaluation; click-time validation reads live data. A million-point inactive record completed without argument-limit failure, taking approximately **111 ms** locally, though it allocates intermediate arrays.

For the parked work, **I would choose F as the basis**, with model-mismatch honesty handled independently before applying it. It shares the existing support definition and avoids LR’s demonstrated rescaling sensitivity. Neither patch is ready unchanged. Leaving the variance floor alone is reasonable for this scoped change, but preserves its raw-count assumptions. Both correctly retain support through component copies; both also classify unsupported in-window components as orphans, which should be distinguished from geometrically unmatched peaks. `grammar.contains` has no current Python callers; its ignored `noise_floor` argument is therefore an API cleanup concern, not a demonstrated runtime regression.

Validation: **65 focused JavaScript tests passed**; both patches were evaluated in memory without application. The central README measurements and ranking explanation were reproduced. The complete claimed Python suite totals were not independently rerun. No files changed.

VERDICT: GO
tokens used
77,668
No BLOCKER or MAJOR found in the shipped gate change. The parked proposals need further work.

1. **MAJOR — parked: “scale-free Poisson likelihood ratio” overstates the implementation.** [README.md:31](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:31). The LR patch computes a weighted squared-error gain with other components held fixed; it neither evaluates a Poisson likelihood nor refits the reduced model. Dimensionless does not imply invariant under intensity rescaling. In a concrete probe, scaling data, fit, and component by 0.1 changed Δχ²/p from **40 to 4**, flipping LR occupancy; F stayed **32**. All observations remained above the variance floor. This matters for the same spectrum expressed in different intensity units.

2. **MAJOR — parked: LR occupancy and detectability contradict each other.** [variant_LR_likelihood_ratio.patch:31](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch:31), also line 176. Confidence still uses `support.supported`, reports `basis: support_f_test`, and exposes only the F statistic. The probe above produces **unoccupied** alongside **`above_floor`, F = 32**. Proposal rejection can consequently print **“F = 32.00 < 10”**. Use the chosen occupancy statistic consistently, or explicitly expose two distinct assessments.

3. **MAJOR — parked: F reproduces the honesty regression, but the recommendation misinterprets its cause.** [README.md:48](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:48). I reproduced:
   
   | Variant | Winner | Conditional |
   |---|---|---|
   | Baseline | P3+bfix | true |
   | F | P2 | false |
   | LR | P3+bfix | true |
   
   P3’s third component has Δχ² **10,702.374**, F **9.417**; F drops its persistence to zero and orphan rate becomes one. That excludes it from the decisive-override pool, as described. However, the fixture has **two true peaks** ([stress_cases.py:406](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/tests/autofit/stress_cases.py:406)). This demonstrates an honesty flag depending on retaining a background-compensating third component; it does **not** demonstrate F rejecting a real third peak.

4. **MINOR — shipped: inactive records use different ROI semantics.** [templates/index.html:7771](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/templates/index.html:7771). Saved `295–280` is reordered and passes, while the live selector returns nothing. On a 270–420 scan, saved `min=""`, `max=295` uses the whole scan and fails; the live selector selects 270–295 and passes. Mirror independent open bounds and preserve reversed bounds. This is nonblocking because all three current callers pass the active tab.

5. **MINOR — tests: the caller assertion does not establish active-tab ownership.** [autofit_c1s_gate.test.js:60](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/tests/js/autofit_c1s_gate.test.js:60). Replacing a caller’s lookup with an inactive record would still satisfy `/isC1sTab\(tab\)/`. The other three tests are substantive: all three fail against `07e0839`.

The active path behaved correctly with the actual `getROIData()`: inclusive clipping, reversed and empty selections, independently blank bounds, corrected energies, stacks, and surveys. Blank ROI fields still permit Auto-Fit on a narrow C1s scan. Tab activation installs incoming state and fields before menu evaluation; click-time validation reads live data. A million-point inactive record completed without argument-limit failure, taking approximately **111 ms** locally, though it allocates intermediate arrays.

For the parked work, **I would choose F as the basis**, with model-mismatch honesty handled independently before applying it. It shares the existing support definition and avoids LR’s demonstrated rescaling sensitivity. Neither patch is ready unchanged. Leaving the variance floor alone is reasonable for this scoped change, but preserves its raw-count assumptions. Both correctly retain support through component copies; both also classify unsupported in-window components as orphans, which should be distinguished from geometrically unmatched peaks. `grammar.contains` has no current Python callers; its ignored `noise_floor` argument is therefore an API cleanup concern, not a demonstrated runtime regression.

Validation: **65 focused JavaScript tests passed**; both patches were evaluated in memory without application. The central README measurements and ranking explanation were reproduced. The complete claimed Python suite totals were not independently rerun. No files changed.

VERDICT: GO
