OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0dbeb-91a7-7773-8167-1e1e53764621
--------
user
RECHECK, round 3, of the caM unit: branch fix-cam-continuous, git diff main..HEAD. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

History (plan docs/superpowers/plans/2026-09-25-cam-continuous.md §1 and §7; verdicts docs/autofit/codex/cam_continuous_*verdict_run{A,B}.md). Round 0 made the page draw LA with the server's continuous-m kernel (a literal mirror of fitting._la_casaxps_true) AND freed m in the local engine. Round 1 (NO-GO x2): central differences straddling LA's jumps in m (the kernel half-width max(1, ceil(3.5 m/3)) changes at m = 6k/7) stalled local fits. Round 2 (NO-GO x2): after confining the derivative to one piece, the LM step still crossed jumps (a fit started on a transition exhausted damping) and the piece rule created a zero derivative next to the 1e-3 no-convolution threshold (a regression vs main).

THE FINAL CONTRACT (commit "fix(caM): Codex round 2 ... WITHDRAWN"): the page still mirrors the server's continuous-m kernel exactly (unchanged since round 0 and clean in rounds 1-2); the local engine NEVER makes caM free - it is held at its EXACT value (before this unit a free caM was made free and then Math.round-ed by the clamp, so a fractional 8.2 was silently fitted as 8); the piece-confined derivative is removed; `_laKernelHalf` remains only as the evaluator's half-width helper. The local-fit caveat ("can differ ... for LA components (m held at its start locally) or where the model has several minima") is restored. All four Codex reproducers of rounds 1-2 are regression tests that converge; the local test pins the exact hold (5.37 stays 5.37 free or locked; not a dof). scripts/local_server_gap.js's control arm now holds the server's m at the same exact value; the re-measurement (plan §4) shows A03's picture. JS 422 tests, 420 pass, 2 todo; browser: LA drawn vs fitted 1.1e-13, areas exact, Batch Fit keeps m at exactly its given value.

Verify: (1) every local-engine path that could still move, round or count caM (the free-parameter block, clamp, applyParams, the linked-child sync - does a linked LA child's caM follow the parent's exact value?, the certificate, dof, per-component support p, Batch Fit's copy, the scaled start in runPropagation); (2) that holding m changes NOTHING else for LA fits relative to main except the rounding (main rounded a fractional m at the clamp: a saved 8.2 fitted as 8 - now 8.2 exactly; any fit where that matters?); (3) the page mirror once more (unchanged) and that nothing in the diff still depends on the withdrawn code (dead helpers, stale comments, tests that assert the withdrawn behaviour); (4) docs vs code vs docs/findings/cam/*.json (plan §1/§3/§4/§6/§7, CLAUDE.md). Whether withdrawing the free-m half is the right call is the owner's; judge only whether what ships is correct and honestly described.

Finish with VERDICT: GO or VERDICT: NO-GO.

codex
I’ll trace the local caM paths against `main`, check the page kernel and evidence for stale claims, and give a ranked review with a verdict within this run.

exec
/bin/zsh -lc 'pwd; git status --short; git diff --stat main..HEAD; rg --files -g AGENTS.md -g CLAUDE.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Ala12NtJ' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-G0u4FFsf' (errno=Operation not permitted)
?? docs/autofit/codex/cam_continuous_r3_verdict_runA.md
?? docs/autofit/codex/cam_continuous_r3_verdict_runB.md
?? docs/autofit/codex/cam_continuous_recheck2_prompt.txt
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-77Vum8QY' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ZZMqqdQZ' (errno=Operation not permitted)
 CLAUDE.md                                          |    48 +-
 .../codex/cam_continuous_r2_verdict_runA.md        |  9728 +++++++++++++++
 .../codex/cam_continuous_r2_verdict_runB.md        |  9542 +++++++++++++++
 .../codex/cam_continuous_recheck_prompt.txt        |     9 +
 .../autofit/codex/cam_continuous_review_prompt.txt |    33 +
 docs/autofit/codex/cam_continuous_verdict_runA.md  | 11123 ++++++++++++++++++
 docs/autofit/codex/cam_continuous_verdict_runB.md  | 11767 +++++++++++++++++++
 docs/findings/cam/lacx_page_vs_server_after.json   |   991 ++
 docs/findings/cam/lacx_page_vs_server_before.json  |   991 ++
 docs/findings/cam/local_server_gap_after_cam.json  |  3375 ++++++
 docs/findings/cam/local_server_gap_after_cam.log   |    18 +
 docs/findings/cam/transition_sweep.json            |     1 +
 .../superpowers/plans/2026-09-25-cam-continuous.md |   153 +
 scripts/cam_transition_sweep.js                    |    24 +
 scripts/lacx_page_vs_server.js                     |    40 +
 scripts/local_server_gap.js                        |     9 +-
 scripts/voigt_saved_vs_refit.js                    |     2 +-
 templates/index.html                               |   127 +-
 tests/js/lineshape_parity.test.js                  |    32 +-
 tests/js/lineshape_roundtrip.test.js               |    17 +-
 tests/js/local_lm_descent.test.js                  |    79 +-
 21 files changed, 48006 insertions(+), 103 deletions(-)
CLAUDE.md

exec
/bin/zsh -lc 'git diff main..HEAD -- templates/index.html tests/js/lineshape_parity.test.js tests/js/lineshape_roundtrip.test.js tests/js/local_lm_descent.test.js scripts/local_server_gap.js scripts/voigt_saved_vs_refit.js scripts/cam_transition_sweep.js scripts/lacx_page_vs_server.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-E92Jakhz' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-E3jJrIov' (errno=Operation not permitted)
diff --git a/scripts/cam_transition_sweep.js b/scripts/cam_transition_sweep.js
new file mode 100644
index 0000000..f18f24f
--- /dev/null
+++ b/scripts/cam_transition_sweep.js
@@ -0,0 +1,24 @@
+const path = require('path'); process.chdir(path.join(__dirname, '..'));   // caM unit, Codex round 1: local LA fits with m free around kernel-width transitions (m = 6k/7) vs m held
+const fs = require('fs'); const html = fs.readFileSync('templates/index.html', 'utf8'); const lines = html.split('\n');
+function extractFn(name) { const re = new RegExp('^(async )?function ' + name + '\\('); const start = lines.findIndex(l => re.test(l)); let depth = 0, seen = false;
+  for (let i = start; i < lines.length; i++) { for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; } if (seen && depth === 0) return lines.slice(start, i + 1).join('\n'); } }
+const NAMES = ['_arrMin','_arrMax','gaussian','lorentzian','pseudoVoigt','asymmGL','doniachSunjic','laCasaXPSCore','laCasaXPS','laTrueCasaXPS','_laKernelHalf','laTrueCasaXPS_array','evalPeak','_dsgAlpha','dsgDeltaKernel_array','_fftRadix2','_circularConvolve','dsgConvolved_array','evalPeakArray','evalAllPeaks','getPeak','runFitLocal','solveLinear','_computeRFactor','_fitStatLabel','_isUnweightedLocal','_isLocalProvenance','_localFitDetail','_isLocalFit','_isLocalModel','_governingProvenance','_localFitCaveat','_fitStatusText','_applyStatCaption','_applyStatDisplay','_updateLocalModelBanner','_componentSupportCore','_supportRootOf','_applySupportVerdicts'];
+const CAV = (html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg) || []).join('\n');
+function env() { const dom = {}; const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, setAttribute() {}, removeAttribute() {}, classList: { add() {}, remove() {}, contains: () => false } });
+  const state = { peaks: [], fitResult: null, rawBE: [], rawIntensity: [], ccShift: 0 }; const noop = () => {};
+  const f = new Function('document','state','notify','_CHISQ_TOOLTIP','_LOCALFIT_TOOLTIP','_activeTab','_escHtml','_historyPreview','tabManager','_updateRFactorUI','_updateROIDisplay','renderPeakList','updatePlot','renderResults','_hideFitSpinner','_autoSnapshot','manualAnchorBackground',
+    CAV + '\nconst _SUPPORT_MIN_F = 10; const _startsLiveKey = () => "K";\n' + NAMES.map(extractFn).join('\n\n') + '\nreturn { runFitLocal, evalAllPeaks };');
+  return { ...f({ getElementById: el, querySelectorAll: () => [] }, state, noop, '', '', () => null, x => String(x), null, null, noop, noop, noop, noop, noop, noop, noop, be => be.map(() => 0)), state }; }
+const grid = (lo, hi, st) => Array.from({ length: Math.round((hi - lo) / st) + 1 }, (_, i) => lo + st * i);
+let freeFail = 0, heldFail = 0, worse = 0, n = 0; const fails = [];
+for (const st of [0.03, 0.05, 0.1]) for (const k of [2, 3, 5, 9, 17, 33, 56]) for (const off of [-0.003, -0.0005, 0, 0.0005, 0.003]) for (const startDelta of [-0.4, 0.3]) {
+  const mT = 6 * k / 7 + off; const be = grid(280, 280 + 150 * st, st);
+  const truth = { id: 1, name: 'la', shape: 'LACX', center: 280 + 75 * st + 0.013, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: mT, glMix: 50, asymmetry: 0 };
+  const run = fixCaM => { const e = env(); e.state.peaks = [{ ...truth }]; const d = e.evalAllPeaks(be, e.state.peaks).map((v, i) => v + 5 * Math.sin(1.77 * i));
+    e.state.peaks = [{ ...truth, amplitude: 4600, caM: Math.max(0.01, mT + startDelta), fixCenter: true, fixFwhm: true, fixCaM }]; const o = e.runFitLocal(be, d, be.map(() => 0)); return { o, chi: e.state.fitResult && e.state.fitResult.chi }; };
+  const fr = run(false), hd = run(true); n++;
+  if (!fr.o.success) { freeFail++; fails.push({ st, k, off, startDelta, msg: fr.o.message }); }
+  if (!hd.o.success) heldFail++;
+  if (fr.o.success && hd.o.success && fr.chi > hd.chi * (1 + 1e-9)) worse++;
+}
+console.log(JSON.stringify({ cases: n, free_failed: freeFail, held_failed: heldFail, free_ended_worse_than_held: worse, first_fails: fails.slice(0, 5) }));
diff --git a/scripts/lacx_page_vs_server.js b/scripts/lacx_page_vs_server.js
new file mode 100644
index 0000000..603b030
--- /dev/null
+++ b/scripts/lacx_page_vs_server.js
@@ -0,0 +1,40 @@
+#!/usr/bin/env node
+// caM unit (2026-09-25): the page's LA (LACX) curve vs the server's, for every
+// LA component in the committed projects, at its SAVED parameters on its tab's
+// ROI grid (the page's getROIData semantics: corrected BE inside the ROI).
+// Reports the max |page − server| as a fraction of amplitude and the area
+// difference, per component. Run before and after the unit: before = the
+// defect; after = what a student sees change when a saved project is opened.
+// Usage: node scripts/lacx_page_vs_server.js [out.json]
+const fs = require('fs'); const path = require('path'); const { execFileSync } = require('child_process');
+const ROOT = path.join(__dirname, '..');
+const html = fs.readFileSync(path.join(ROOT, 'templates/index.html'), 'utf8');
+const m = html.match(/function gaussian\(x, center, fwhm\) \{[\s\S]*?\nfunction evalPeakArray\(beArr, p\) \{[\s\S]*?\n\}/);
+const { evalPeakArray } = eval('(function(){\n' + m[0] + '\nreturn { evalPeak, evalPeakArray };})()');
+const PY = [path.join(ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3'].find(p => fs.existsSync(p));
+const DATA = path.join(ROOT, 'docs/autofit/test_data');
+const rows = [];
+const specs = [];
+for (const zp of fs.readdirSync(DATA).filter(f => f.endsWith('.proj.zip')).sort()) {
+  const tabs = JSON.parse(execFileSync(PY, ['-c', 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))', ROOT, path.join(DATA, zp)], { encoding: 'utf8', maxBuffer: 1 << 26 }));
+  for (const t of tabs) {
+    const ui = t.ui || {}; const lo = parseFloat(ui.roiMin), hi = parseFloat(ui.roiMax);
+    const be = t.rawBE.map(b => b - (t.ccShift || 0)).filter(c => (!(lo <= Infinity) || c >= lo) && (!(hi <= Infinity) || c <= hi));
+    for (const p of t.peaks || []) {
+      if (p.shape !== 'LACX') continue;
+      rows.push({ project: zp, tab: t.name, peak: p.name, caM: p.caM, fixCaM: !!p.fixCaM, be, p });
+      specs.push({ shape: 'la_casaxps', params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm, alpha: p.caAlpha, beta: p.caBeta, m: p.caM }, x: be });
+    }
+  }
+}
+const srv = JSON.parse(execFileSync(PY, [path.join(ROOT, 'tests/js/lineshape_parity_backend.py')], { input: JSON.stringify(specs), encoding: 'utf8', maxBuffer: 1 << 28 }));
+const out = rows.map((r, i) => {
+  const pg = evalPeakArray(r.be, r.p); let mx = 0, aP = 0, aS = 0;
+  for (let j = 0; j < r.be.length; j++) { mx = Math.max(mx, Math.abs(pg[j] - srv[i][j])); aP += pg[j]; aS += srv[i][j]; }
+  return { project: r.project, tab: r.tab, peak: r.peak, caM: r.caM, fixCaM: r.fixCaM, maxDiffRel: mx / Math.abs(r.p.amplitude || 1), dAreaPct: aS ? 100 * (aP / aS - 1) : null };
+});
+const q = v => { v = [...v].sort((a, b) => a - b); const n = v.length; return { n, median: n % 2 ? v[(n - 1) / 2] : 0.5 * (v[n / 2 - 1] + v[n / 2]), max: v[n - 1] }; };
+const summary = { components: out.length, integer_caM: out.filter(r => Number.isInteger(r.caM)).length, locked: out.filter(r => r.fixCaM).length,
+  maxDiffRel: q(out.map(r => r.maxDiffRel)), absDAreaPct: q(out.map(r => Math.abs(r.dAreaPct))) };
+console.log(JSON.stringify(summary));
+if (process.argv[2]) fs.writeFileSync(process.argv[2], JSON.stringify({ summary, rows: out }, null, 1));
diff --git a/scripts/local_server_gap.js b/scripts/local_server_gap.js
index 0344a54..61d2f67 100644
--- a/scripts/local_server_gap.js
+++ b/scripts/local_server_gap.js
@@ -13,8 +13,8 @@
 // ROI grid × step) — so the comparison is about parameters, not about which
 // side integrated. A third arm (Codex round 1: "movement in m alone does not
 // establish that the residual is the local clamp") fits the server with every
-// LA m HELD at the value the local engine effectively uses — its start
-// ROUNDED to an integer, as laTrueCasaXPS_array rounds it (Codex round 2) —
+// LA m HELD at the value the local engine effectively uses — its exact
+// start since the caM unit (2026-09-25; before it, the start rounded) —
 // the one thing the local engine cannot move: if that arm agrees with the local engine where the
 // free-m arm did not, the attribution is established by a controlled
 // comparison, not inferred. Usage: node scripts/local_server_gap.js [out.json]
@@ -29,7 +29,7 @@ function extractFn(name) {
   throw new Error('unbalanced ' + name);
 }
 const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
-  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
+  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', '_laKernelHalf', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
   'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
   'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
   'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
@@ -77,7 +77,8 @@ for (const [region, sourceName] of [['C1s', 'C1s Scan'], ['U4f', 'U4f Scan']]) {
       return { r, peaks };
     };
     const { r: srv, peaks: serverPeaks } = serverFit(T.start);
-    const heldStart = T.start.map(p => p.shape === 'LACX' ? { ...p, caM: Math.round(p.caM || 0), fixCaM: true } : p);
+    // held at the value the local engine holds: its exact start since the caM unit (it rounded it before)
+    const heldStart = T.start.map(p => p.shape === 'LACX' ? { ...p, fixCaM: true } : p);
     const { r: srvHeld, peaks: serverHeldPeaks } = serverFit(heldStart);
     // linked peaks: the local engine syncs them; the server returns resolved values for them too (applied above)
     const aL = localPeaks.map(p => area(env, T.be, p)), aS = serverPeaks.map(p => area(env, T.be, p)), aH = serverHeldPeaks.map(p => area(env, T.be, p));
diff --git a/scripts/voigt_saved_vs_refit.js b/scripts/voigt_saved_vs_refit.js
index 72cb798..56d1124 100644
--- a/scripts/voigt_saved_vs_refit.js
+++ b/scripts/voigt_saved_vs_refit.js
@@ -29,7 +29,7 @@ function extractFn(name) {
   throw new Error('unbalanced ' + name);
 }
 const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic', 'laCasaXPSCore', 'laCasaXPS',
-  'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array', 'evalPeakArray', 'getPeak', '_applyBackendParams', '_bgWindowIndices'];
+  'laTrueCasaXPS', '_laKernelHalf', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array', 'evalPeakArray', 'getPeak', '_applyBackendParams', '_bgWindowIndices'];
 const state = { peaks: [] };
 const fns = new Function('state', NAMES.map(extractFn).join('\n\n') + '\nreturn { evalPeakArray, _applyBackendParams, _bgWindowIndices };')(state);
 const PY = [path.join(ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3', 'python3'].find(p => p === 'python3' || fs.existsSync(p));
diff --git a/templates/index.html b/templates/index.html
index be8edd2..e81b11e 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -4061,10 +4061,11 @@ function laCasaXPS(x, center, alpha, beta, mGauss) {
   return laCasaXPSCore(x - center, alpha, beta) / peakVal;
 }
 
-// True LA(α, β, m) [CasaXPS] — piecewise-asymmetric Lorentzian + integer-kernel Gauss conv.
-// Mirrors fitting.py:_la_casaxps_true. BE axis: high-BE side (eps ≥ 0)
-// gets exponent α; low-BE side (eps < 0) gets β. m is integer 0–499 in
-// data-points; σ_pts = m/3.
+// True LA(α, β, m) [CasaXPS] — piecewise-asymmetric Lorentzian + Gauss conv.
+// BE axis: high-BE side (eps ≥ 0) gets exponent α; low-BE side (eps < 0)
+// gets β. Per-point: the base curve only, m IGNORED — the convolution is a
+// grid operation (laTrueCasaXPS_array, via evalPeakArray; parity guard (C)
+// proves no shipped caller reaches the scalar path).
 function laTrueCasaXPS(x, center, fwhm, alpha, beta, m) {
   const F = Math.max(fwhm, 1e-9);
   const A = Math.max(alpha, 1e-3);
@@ -4076,49 +4077,67 @@ function laTrueCasaXPS(x, center, fwhm, alpha, beta, m) {
   return eps >= 0 ? Math.pow(L, A) : Math.pow(L, B);
 }
 
+// LA(α, β, m) on a grid — a literal mirror of fitting._la_casaxps_true
+// (caM unit, 2026-09-25). m is CONTINUOUS in data points (the server fits it
+// continuously so its derivative exists; the page used to round it and
+// build an integer 2m+1 kernel, drawing a curve up to 0.97 % of amplitude
+// and an area up to 1.2 % away from the fitted one on the lab's U 4f
+// components): σ = m/3 points, half-width max(1, ⌈3.5σ⌉), kernel
+// normalised to unit sum, np.convolve(base, kernel, 'same') with the
+// server's trim when the kernel is longer than the grid, normalisation at
+// the grid point nearest the centre (np.argmin |ε|; fallback max), m < 1e-3
+// = the bare base curve (no normalisation), m clamped to [0, 499].
+// Returns the curve for unit amplitude; the caller applies the amplitude.
+// The LA kernel's half-width in points for a given m — the server's
+// `max(1, ceil(3.5·σ))`, σ = m/3, and 0 below the 1e-3 no-convolution
+// threshold. The curve is smooth in m BETWEEN changes of this integer and
+// jumps where it changes (m = 6k/7); the local engine's derivative for m
+// uses it to stay inside one piece (Codex round 1 of the caM unit).
+function _laKernelHalf(m) {
+  const mc = Math.max(0, Math.min(499, Number.isFinite(m) ? m : 0));
+  if (mc < 1e-3) return 0;
+  return Math.max(1, Math.ceil(3.5 * (mc / 3.0)));
+}
+
 function laTrueCasaXPS_array(xArr, center, fwhm, alpha, beta, m) {
   const N = xArr.length;
   const F = Math.max(fwhm, 1e-9);
   const A = Math.max(alpha, 1e-3);
   const B = Math.max(beta,  1e-3);
-  const mInt = Math.max(0, Math.min(499, Math.round(m || 0)));
+  const mc = Math.max(0, Math.min(499, Number.isFinite(m) ? m : 0));
   const base = new Float64Array(N);
   for (let i = 0; i < N; i++) {
     const eps = xArr[i] - center;
     const L = 1.0 / (1.0 + 4.0 * (eps / F) * (eps / F));
     base[i] = eps >= 0 ? Math.pow(L, A) : Math.pow(L, B);
   }
-  if (mInt === 0) return base;
-  const sigma = mInt / 3.0;
-  const klen = 2 * mInt + 1;
-  const kern = new Float64Array(klen);
+  if (mc < 1e-3) return Array.from(base);
+  const sigma = mc / 3.0;
+  const half = _laKernelHalf(mc);
+  const K = 2 * half + 1;
+  const kern = new Float64Array(K);
   let ksum = 0;
-  for (let k = 0; k < klen; k++) {
-    const dk = k - mInt;
-    kern[k] = Math.exp(-(dk * dk) / (2.0 * sigma * sigma));
-    ksum += kern[k];
-  }
-  for (let k = 0; k < klen; k++) kern[k] /= ksum;
-  const out = new Float64Array(N);
+  for (let t = 0; t < K; t++) { const k = t - half; kern[t] = Math.exp(-(k * k) / (2.0 * sigma * sigma)); ksum += kern[t]; }
+  for (let t = 0; t < K; t++) kern[t] /= ksum;
+  // np.convolve(base, kern, 'same'), then the server's trim to len(base):
+  // out[i] = full[off + i], full[j] = Σ_t base[j − t]·kern[t],
+  // off = (K−1)/2 when K ≤ N, else ⌊(N−1)/2⌋ + ⌊(K−N)/2⌋ (pinned against
+  // numpy on 3,000 random (N, K) — plan §2)
+  const off = K <= N ? (K - 1) / 2 : Math.floor((N - 1) / 2) + Math.floor((K - N) / 2);
+  const out = new Array(N);
   for (let i = 0; i < N; i++) {
-    let s = 0;
-    for (let k = 0; k < klen; k++) {
-      const j = i + (k - mInt);
-      if (j >= 0 && j < N) s += base[j] * kern[k];
-    }
-    out[i] = s;
-  }
-  let pkIdx = 0;
-  for (let i = 1; i < N; i++) {
-    if (Math.abs(xArr[i] - center) < Math.abs(xArr[pkIdx] - center)) pkIdx = i;
-  }
-  let pkVal = out[pkIdx];
-  if (pkVal <= 0) {
-    let mx = 0; for (let i = 0; i < N; i++) if (out[i] > mx) mx = out[i];
-    pkVal = mx;
-  }
-  if (pkVal <= 0) return out;
-  for (let i = 0; i < N; i++) out[i] = out[i] / pkVal;
+    const j = off + i;
+    let acc = 0;
+    const t0 = Math.max(0, j - (N - 1)), t1 = Math.min(K - 1, j);
+    for (let t = t0; t <= t1; t++) acc += base[j - t] * kern[t];
+    out[i] = acc;
+  }
+  let pk = 0;
+  for (let i = 1; i < N; i++) if (Math.abs(xArr[i] - center) < Math.abs(xArr[pk] - center)) pk = i;   // np.argmin: first minimum
+  let pv = N ? out[pk] : 0;
+  if (!(pv > 0)) { let mx = -Infinity; for (let i = 0; i < N; i++) if (out[i] > mx) mx = out[i]; pv = mx; }
+  if (!(pv > 0)) return new Array(N).fill(0);
+  for (let i = 0; i < N; i++) out[i] = out[i] / pv;
   return out;
 }
 
@@ -4348,7 +4367,9 @@ function dsgConvolved_array(beArr, center, alpha, beta, mGauss) {
 // DSG_LA (every m: the delta branch below 0.001, the convolution above) so
 // the padding, kernel and normalisation see the whole grid.
 function evalPeakArray(beArr, p) {
-  if (p.shape === 'LACX' && Math.round(p.caM || 0) > 0) {
+  if (p.shape === 'LACX') {
+    // every m, continuous, as the server (caM unit 2026-09-25; it was
+    // Math.round(p.caM) > 0 → integer kernel)
     const yArr = laTrueCasaXPS_array(beArr, p.center, p.fwhm, p.caAlpha, p.caBeta, p.caM);
     const out = new Array(beArr.length);
     const amp = p.amplitude;
@@ -6334,10 +6355,10 @@ function renderShapeControls(p) {
         </div>
       </div>
       <div class="field">
-        <label data-xps-tip="Gaussian convolution kernel width in DATA POINTS (not eV). Integer 0–499. m=0 = no convolution. Effective eV width ≈ (m/3) × dx where dx is the data step size.">m (Gauss kernel pts)
+        <label data-xps-tip="Gaussian convolution kernel width in DATA POINTS (not eV), 0–499. Continuous: the fit returns a fractional value and the curve is drawn with it. m=0 = no convolution. Effective eV width ≈ (m/3) × dx where dx is the data step size.">m (Gauss kernel pts)
           ${!isLinked ? `<button class="lock-btn${p.fixCaM ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixCaM',this)" title="${p.fixCaM ? 'Unlock' : 'Lock'} during fitting">${p.fixCaM ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
         </label>
-        <input type="number" value="${Math.round(p.caM ?? 50)}" step="1" min="0" max="499"
+        <input type="number" value="${Number.isFinite(p.caM) ? +p.caM.toFixed(2) : 50}" step="0.1" min="0" max="499"
           oninput="updatePeakParam(${p.id},'caM',parseFloat(this.value))">
       </div>
     `;
@@ -8013,12 +8034,9 @@ function _fitStatLabel(fr) {
 // (2026-09-22: Voigt = fixed eta 0.5 on BOTH sides), on Voigt components
 // wherever the two engines reach the same minimum (5 of 9 committed U 4f
 // targets: every component within 4.3 meV, 2.6 % FWHM, 2 % area, 0.12 pp);
-// it still differs on the other 4 U 4f targets (satellite areas up to
-// 8.9 %, 0.77 pp): on one because the LA m is held at its start locally
-// (the gap closes when the server holds m too), on three because the local
-// descent stops at a higher chi2r than the server from the same start
-// (+5 to +13 %, with m held as well) - several minima - and it gives no
-// uncertainties. Unweighted A0-era results differed by more than 100 %.
+// it still differs where an LA component's m moves on the server (held,
+// exactly, at its start locally - LA is discontinuous in m, caM unit) and
+// where the model has several minima; and it gives no uncertainties. Unweighted A0-era results differed by more than 100 %.
 // Every site that shows, exports or saves a fit result carries the
 // designation, keyed on persisted identity so reloaded results are labelled.
 const _LOCAL_FIT_CAVEAT = 'Local fit (Poisson-weighted like the server, no uncertainties): a starting point, not a reportable result. Run Fit before reporting.';
@@ -8185,7 +8203,13 @@ function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
       if (p.shape === 'LACX') {
         if (!p.fixCaAlpha) { freeParams.push(Number.isFinite(p.caAlpha) ? p.caAlpha : 1.0); paramMap.push({id: p.id, param: 'caAlpha'}); }
         if (!p.fixCaBeta)  { freeParams.push(Number.isFinite(p.caBeta)  ? p.caBeta  : 1.0); paramMap.push({id: p.id, param: 'caBeta'}); }
-        if (!p.fixCaM)     { freeParams.push(Number.isFinite(p.caM)     ? p.caM     : 50);  paramMap.push({id: p.id, param: 'caM'}); }
+        // caM is HELD at its value — exactly, not rounded, not a degree of
+        // freedom. LA's curve jumps where its kernel half-width changes
+        // (m = 6k/7), and a smooth local optimiser cannot fit a discontinuous
+        // parameter: freeing it (caM unit, 2026-09-25) stalled fits at the
+        // jumps and a derivative confined to one piece failed next to the
+        // no-convolution threshold (Codex rounds 1–2). The server fits m;
+        // Batch Fit carries the value it is given.
       }
     }
   }
@@ -8208,7 +8232,6 @@ function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
     if (param === 'laM')          return Math.max(0.05, Math.min(4.0, v));
     if (param === 'caAlpha')      return Math.max(0.1, Math.min(5.0, v));
     if (param === 'caBeta')       return Math.max(0.1, Math.min(5.0, v));
-    if (param === 'caM')          return Math.max(0,   Math.min(499, Math.round(v)));
     return v;
   }
   const LINK_SYNC_KEYS = ['glMix', 'asymmetry', 'dsAlpha', 'dsGamma',
@@ -8296,10 +8319,11 @@ function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
     }
     return Math.max(1, Math.abs(vec[j]));
   };
-  // caM is rounded to an integer by its clamp, so a finite difference cannot
-  // see it: it is carried at its starting value (inherited behaviour; see the
-  // A0 follow-up list) and excluded from the stationarity test.
-  const isDiscrete = j => paramMap[j].param === 'caM';
+  // No free parameter is discrete: caM is never made free here (it is held
+  // at its exact value, see the free-parameter block). Until the caM unit it
+  // was made free and then ROUNDED by its clamp — a fractional server-fitted
+  // m of 8.2 was silently fitted as 8.
+  const isDiscrete = () => false;
   // MINPACK-style termination: (ftol) actual AND predicted relative
   // reductions both below FTOL, with the linearised model agreeing with
   // the actual reduction; (xtol) relative step below XTOL; (gtol) the
@@ -8444,9 +8468,8 @@ function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
     delete live._backendParams;
   }
 
-  // Degrees of freedom count the parameters this engine actually varies: the
-  // integer-clamped caM is carried at its start value and is not one of them
-  // (continuous parameters temporarily blocked at a wall still count).
+  // Degrees of freedom count the parameters this engine varies (caM is held,
+  // not one of them; parameters temporarily blocked at a wall still count).
   const nVaried = params.filter((_, j) => !isDiscrete(j)).length;
   const dof = Math.max(1, be.length - nVaried);
   const chiReduced = chi / dof;                       // weighted reduced chi-square, as lmfit's redchi
diff --git a/tests/js/lineshape_parity.test.js b/tests/js/lineshape_parity.test.js
index 9e7b849..98e23b5 100644
--- a/tests/js/lineshape_parity.test.js
+++ b/tests/js/lineshape_parity.test.js
@@ -168,7 +168,7 @@ for (const shape of ['Gaussian', 'Lorentzian', 'GL', 'Voigt', 'DS', 'asym-GL'])
 //   the fitted box, every grid step, orientation and off-grid centre tested
 //   below).
 //
-test('(A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization)', { todo: 'unit 2 fast-follow: LACX Gaussian-conv kernel mismatch vs backend, grows with m (~0.15% at m=50, measured 2026-08-30)' }, () => {
+test('(A) frontend vs backend parity: LACX (m>0) (FIXED 2026-09-25, caM unit: continuous-m kernel mirrored)', () => {
   const p = basePeak('LACX');
   const x = grid(p.center);
   const jsY = evalPeakArray(x, p);
@@ -347,10 +347,10 @@ const SWEEP = {
   // the full β/m box the optimiser can reach, incl. the corner that made the
   // old quadrature 1e52 × amplitude (β 2, m 0.05) and the delta threshold
   'DSG_LA (m > 0)': { laAlpha: [0, 0.25, 0.49], laBeta: [0.05, 0.7, 2], laM: [0.001, 0.05, 0.4, 2, 4] },
+  // continuous m (caM unit, 2026-09-25): fractional values, the 1e-3 threshold, and the 499 ceiling
+  'LACX (m > 0)':   { caAlpha: [0.1, 1, 5], caBeta: [0.1, 1, 5], caM: [0.001, 0.5, 1, 5, 8.66, 50, 123.4, 499], fwhm: FWHM_RANGE },
 };
-const SWEEP_KNOWN_GAP = {
-  'LACX (m > 0)':   { caAlpha: [0.1, 1, 5], caBeta: [0.1, 1, 5], caM: [1, 5, 50, 499], fwhm: FWHM_RANGE },
-};
+const SWEEP_KNOWN_GAP = {};
 function sweepShape(label) { return label.split(' ')[0]; }
 // The backend parameters of the sweep come from the PAGE's request builder,
 // not from a mapping of this file's own (Codex round 1: a mapping written
@@ -480,3 +480,27 @@ for (const laM of [0.001, 0.002, 0.02, 0.05]) {
     else assert.ok(serverMax > 0.9, `m = ${laM}: a real curve`);
   });
 }
+
+// ── (D‴) LA convergence beyond the base grid (caM unit, 2026-09-25) ──────────
+// The kernel is built in DATA POINTS, so the grid decides it: steps, a
+// descending grid, an off-grid centre, and grids SHORTER than the kernel
+// (np.convolve 'same' then the server's trim — the branch the old integer
+// kernel never exercised).
+const LA_BOX = { caAlpha: [0.1, 1.4, 5], caBeta: [0.1, 0.8, 5], caM: [0.001, 2.5, 8.66, 50, 499] };
+const LA_GRIDS = [
+  { label: 'step 0.1 eV, 120 pts', step: 0.1, n: 120 },
+  { label: 'step 0.02 eV, 500 pts', step: 0.02, n: 500 },
+  { label: 'step 0.05 eV, descending', step: 0.05, n: 200, descending: true },
+  { label: 'step 0.05 eV, centre 0.013 eV off-grid', step: 0.05, n: 200, offset: 0.013 },
+  { label: '9 points (kernel longer than the grid for m ≥ 3)', step: 0.1, n: 9 },
+  { label: '2 points', step: 0.1, n: 2 },
+];
+for (const g of LA_GRIDS) {
+  test(`(D‴) LA continuous-m convolution matches the server on another grid: ${g.label}`, () => {
+    const cases = combos(LA_BOX).map(c => ({ c, p: { ...basePeak('LACX'), ...c } }));
+    const specs = cases.map(k => { const b = backendParamsFromRequest(k.p); return { ...b, x: gridOf(k.p.center, g.step, g.n, g) }; });
+    const beYs = backendEvalMany(specs);
+    const worst = cases.map((k, i) => ({ c: k.c, rel: maxRelDiff(evalPeakArray(specs[i].x, k.p), beYs[i], k.p.amplitude) })).sort((a, b) => b.rel - a.rel);
+    assert.ok(worst[0].rel < TIGHT_TOL, `${g.label}: ${worst.filter(r => r.rel >= TIGHT_TOL).length} of ${worst.length} diverge; worst ${(worst[0].rel * 100).toExponential(3)} % of amplitude at ${JSON.stringify(worst[0].c)}`);
+  });
+}
diff --git a/tests/js/lineshape_roundtrip.test.js b/tests/js/lineshape_roundtrip.test.js
index 4103c52..4204428 100644
--- a/tests/js/lineshape_roundtrip.test.js
+++ b/tests/js/lineshape_roundtrip.test.js
@@ -15,10 +15,10 @@
 // page then DRAWS (evalPeakArray on the fitted grid) to be the curve the
 // server FITTED (individual_peaks[].y).
 //
-// One shape carries a known drawn-vs-fitted gap and is marked todo with the
-// unit that owns it: LACX (the page sends m free and draws it ROUNDED — the
-// caM clamp unit). DSG_LA was the other until 2026-09-22 (the page's
-// quadrature; now dsgConvolved_array mirrors the server).
+// No shape carries a known drawn-vs-fitted gap any more. DSG_LA did until
+// 2026-09-22 (the page's quadrature; now dsgConvolved_array mirrors the
+// server) and LACX until 2026-09-25 (the page drew m rounded to an integer
+// kernel; now laTrueCasaXPS_array mirrors the server's continuous-m one).
 const { test } = require('node:test');
 const assert = require('node:assert');
 const { execFileSync } = require('node:child_process');
@@ -41,7 +41,7 @@ function extractFn(name) {
   assert.fail(`unbalanced braces extracting ${name}`);
 }
 const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
-  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
+  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', '_laKernelHalf', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
   'evalPeakArray', 'getPeak', 'peakToBackendSpec', '_applyBackendParams'];
 const state = { peaks: [] };
 const env = new Function('state', NAMES.map(extractFn).join('\n\n') + '\nreturn { evalPeakArray, peakToBackendSpec, _applyBackendParams };')(state);
@@ -91,9 +91,7 @@ const CASES = {
   'LACX':       { truth: { shape: 'LACX', caAlpha: 1.6, caBeta: 0.7, caM: 20 }, start: { caAlpha: 1.0, caBeta: 1.0, caM: 30 } },
 };
 const TIGHT_TOL = 1e-6;      // of amplitude; both curves are the same closed form on the same grid
-const KNOWN_GAP = {
-  'LACX':   'LACX: the page sends m FREE and draws it rounded to an integer kernel (laTrueCasaXPS_array) — the caM clamp unit',
-};
+const KNOWN_GAP = {};   // LACX was the last (the page drew m rounded to an integer kernel) — closed by the caM unit, 2026-09-25
 
 function roundTrip(shape, { truth, start, extraPeaks = [] }) {
   const truthPeaks = [fullPeak(truth), ...extraPeaks.map(e => fullPeak(e.truth))];
@@ -193,7 +191,8 @@ const LOCKED_AT_BOUNDS = [
   // comparison sits under the caM evaluator gap marked todo above (curve: false)
   { label: 'DS+G m 0.05 locked', truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 0.5, laM: 0.05, fixLaM: true }, held: { m_gauss: 0.05 } },
   { label: 'DS+G m 4 locked',    truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 0.5, laM: 4, fixLaM: true }, held: { m_gauss: 4 } },
-  { label: 'LA m 499 locked (request and hold only)',    truth: { shape: 'LACX', caAlpha: 1, caBeta: 1, caM: 499, fixCaM: true }, held: { m: 499 }, curve: false },
+  { label: 'LA m 499 locked',    truth: { shape: 'LACX', caAlpha: 1, caBeta: 1, caM: 499, fixCaM: true }, held: { m: 499 } },
+  { label: 'LA m 8.66 locked (a fractional m, as a fit returns it)', truth: { shape: 'LACX', caAlpha: 1.3, caBeta: 0.9, caM: 8.66, fixCaM: true }, held: { m: 8.66 } },
 ];
 for (const c of LOCKED_AT_BOUNDS) {
   test(`locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — ${c.label}`, () => {
diff --git a/tests/js/local_lm_descent.test.js b/tests/js/local_lm_descent.test.js
index 024ca96..3901fdc 100644
--- a/tests/js/local_lm_descent.test.js
+++ b/tests/js/local_lm_descent.test.js
@@ -35,7 +35,7 @@ function extractFn(name) {
 }
 
 const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
-  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
+  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', '_laKernelHalf', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
   'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
   'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
   'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
@@ -477,25 +477,78 @@ test('server parity on GL-type models: weighted local Batch Fit matches lmfit fr
   }
 });
 
-// ── W1 Codex round 1: a never-optimised parameter (integer-clamped caM) is not a degree of freedom ──
-test('reduced chi-square does not count the held caM as a varied parameter', () => {
-  const run = (fixCaM) => {
+// ── caM unit (2026-09-25): the local engine HOLDS LA's m, exactly ──
+// It used to make a free caM free and then ROUND it in its clamp, so a
+// fractional server-fitted 8.2 was silently fitted as 8 and not counted
+// as a degree of freedom. Freeing it properly failed on the curve's jumps
+// in m (Codex rounds 1–2), so it is held at its exact value.
+test('the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom', () => {
+  const be = grid(280, 283, 0.05);
+  const truth = { id: 1, name: 'la', shape: 'LACX', center: 281.5, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: 8.66, glMix: 50, asymmetry: 0 };
+  const fitFrom = (fixCaM) => {
     const env = makeEnv();
-    const be = grid(280, 282, 0.1);
-    const truth = { id: 1, name: 'la', shape: 'LACX', center: 281.0, fwhm: 1.0, amplitude: 50, caAlpha: 1.2, caBeta: 1.5, caM: 6, glMix: 50, asymmetry: 0 };
     env.state.peaks = [{ ...truth }];
-    const data = env.evalAllPeaks(be, env.state.peaks).map((v, i) => v * (1 + 0.05 * Math.sin(3 * i)) + 20);
-    env.state.peaks = [{ ...truth, amplitude: 40, fixCenter: true, fixFwhm: true, fixCaAlpha: true, fixCaBeta: true, fixCaM }];
-    const out = env.runFitLocal(be, data.map(v => v - 20), new Array(be.length).fill(20));
+    const data = env.evalAllPeaks(be, env.state.peaks);
+    env.state.peaks = [{ ...truth, caM: 5.37, amplitude: 4000, fixCenter: true, fixFwhm: true, fixCaAlpha: true, fixCaBeta: true, fixCaM }];
+    const out = env.runFitLocal(be, data, new Array(be.length).fill(0));
     assert.equal(out.success, true, JSON.stringify(out));
-    return { chi: env.state.fitResult.chi, chiReduced: out.chiReduced, amp: env.state.peaks[0].amplitude };
+    return { out, p: env.state.peaks[0], fr: env.state.fitResult };
   };
-  const a = run(true), b = run(false);
-  assert.ok(Math.abs(a.amp - b.amp) < 1e-9 && Math.abs(a.chi - b.chi) < 1e-9, 'identical fit either way');
-  assert.ok(Math.abs(a.chiReduced - b.chiReduced) < 1e-12, `same fit, same reduced chi-square: ${a.chiReduced} vs ${b.chiReduced}`);
+  const free = fitFrom(false), held = fitFrom(true);
+  assert.equal(free.p.caM, 5.37, 'held exactly — not rounded to 5, not moved');
+  assert.equal(held.p.caM, 5.37);
+  assert.ok(Math.abs(free.p.amplitude - held.p.amplitude) < 1e-9, 'the same fit either way');
+  assert.ok(Math.abs(free.out.chiReduced - held.out.chiReduced) < 1e-12, 'm is not a degree of freedom either way');
 });
 
 
+// caM unit, Codex rounds 1–2: LA's curve JUMPS where the kernel half-width
+// max(1, ceil(3.5 m/3)) changes (m = 6k/7). With m made free, these fits
+// stalled (round 1) or failed next to the no-convolution threshold (round
+// 2). m is held, so each must converge whether or not it is locked.
+for (const c of [
+  { label: 'run A: 201 pts at 0.03 eV, m 48 (a transition), noisy', be: grid(280, 286, 0.03),
+    truth: { center: 283.013, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: 48 }, noise: i => 5 * Math.sin(1.77 * i),
+    start: { amplitude: 4900 }, lock: { fixCenter: true, fixFwhm: true, fixCaAlpha: true, fixCaBeta: true } },
+  { label: 'run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free', be: grid(280, 283, 0.05),
+    truth: { center: 281.538, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: 18 / 7 - 0.001 }, noise: i => 0.1 * Math.sin(3 * i),
+    start: { amplitude: 4000, caM: 2.6 }, lock: {} },
+]) {
+  test(`an LA fit with m free converges across a kernel-width transition — ${c.label}`, () => {
+    const run = (fixCaM) => {
+      const env = makeEnv();
+      const truth = { id: 1, name: 'la', shape: 'LACX', glMix: 50, asymmetry: 0, ...c.truth };
+      env.state.peaks = [{ ...truth }];
+      const data = env.evalAllPeaks(c.be, env.state.peaks).map((v, i) => v + c.noise(i));
+      env.state.peaks = [{ ...truth, ...c.start, ...c.lock, fixCaM }];
+      const out = env.runFitLocal(c.be, data, new Array(c.be.length).fill(0));
+      return { out, chi: env.state.fitResult && env.state.fitResult.chi };
+    };
+    const free = run(false), held = run(true);
+    assert.equal(held.out.success, true, 'held: ' + JSON.stringify(held.out));
+    assert.equal(free.out.success, true, 'free: ' + JSON.stringify(free.out));
+    assert.ok(Math.abs(free.chi - held.chi) <= 1e-12 * Math.max(1, held.chi), `an unlocked m is held: the same fit either way (${free.chi} vs ${held.chi})`);
+  });
+}
+
+// Codex round 2's two reproducers: an exact-transition start (m = 18/7)
+// with amplitude and m free, and noiseless m = 0 data started at m = 0.001.
+for (const c of [
+  { label: 'exact transition m = 18/7, 61 pts at 0.03 eV', be: grid(280, 281.8, 0.03), truth: { center: 280.913, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: 18 / 7 }, noise: i => 0.1 * Math.sin(3 * i), start: {}, lock: { fixCenter: true, fixFwhm: true, fixCaAlpha: true, fixCaBeta: true } },
+  { label: 'm = 0 data, start m = 0.001', be: grid(280, 283, 0.05), truth: { center: 281.513, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: 0 }, noise: () => 0, start: { caM: 0.001, amplitude: 4500 }, lock: { fixCenter: true, fixFwhm: true, fixCaAlpha: true, fixCaBeta: true } },
+]) {
+  test(`round-2 reproducer converges with m unlocked (m is held) — ${c.label}`, () => {
+    const env = makeEnv();
+    const truth = { id: 1, name: 'la', shape: 'LACX', glMix: 50, asymmetry: 0, ...c.truth };
+    env.state.peaks = [{ ...truth }];
+    const data = env.evalAllPeaks(c.be, env.state.peaks).map((v, i) => v + c.noise(i));
+    env.state.peaks = [{ ...truth, ...c.start, ...c.lock, fixCaM: false }];
+    const out = env.runFitLocal(c.be, data, new Array(c.be.length).fill(0));
+    assert.equal(out.success, true, JSON.stringify(out));
+    assert.equal(env.state.peaks[0].caM, c.start.caM ?? c.truth.caM, 'm held exactly');
+  });
+}
+
 test('recovery from an amplitude of exactly zero (the new floor is not a trap)', () => {
   const env = makeEnv();
   const be = grid(280, 290, 0.05);

exec
/bin/zsh -lc "cat docs/superpowers/plans/2026-09-25-cam-continuous.md; git diff main..HEAD -- CLAUDE.md; cat package.json; rg -n 'caM|_laKernelHalf|applyParams|runPropagation' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 0ms:
# The `caM` unit — LA's m continuous on the page and in the local engine (2026-09-25)

Branch `fix-cam-continuous` off main `3ea3b8b`. Queued by the owner after
A03 and the fail-open sweep ("Then the caM clamp"). The record defined the
unit as two halves (A03 plan §5/§6; CLAUDE.md): the page draws LA with m
ROUNDED to an integer 2m+1 kernel while the server fits m continuously, and
the local engine rounds m in its clamp and carries it at its start.

## 1. Contract (final, after Codex round 2)

The server's continuous m is deliberate (`_la_casaxps_true`: "m flows
through continuously so lmfit's finite-difference Jacobian in m is
non-singular" — rounding made the function locally constant in m and
poisoned the covariance of every other parameter). So:

- **The page DRAWS what the server fits:** it mirrors the continuous-m
  kernel exactly, as it does DS+G's (2026-09-22). Nothing on the server
  changes.
- **The local engine HOLDS m, exactly.** It used to make a free `caM` free
  and then round it in its clamp, silently fitting a fractional 8.2 as 8.
  Freeing it properly was tried and withdrawn (§7): LA's curve is
  DISCONTINUOUS in m — the kernel half-width max(1, ⌈3.5 m/3⌉) jumps at
  every m = 6k/7 — and a smooth optimiser cannot fit a discontinuous
  parameter; two Codex rounds each found new reachable failures of the
  patches. Fitting m in Batch Fit, if wanted, is a derivative-free
  one-dimensional search — its own unit.

## 2. Measured before (`scripts/lacx_page_vs_server.js`)

All 108 LA components in the seven committed projects, at their saved
parameters on their tab's ROI grid (106 carry a fractional, server-fitted
m; 107 are unlocked):

| | before | after |
|---|---:|---:|
| max page − server, of amplitude | median 0.29 %, max 0.97 % | max 7.4e-16 |
| area, page vs server | median 0.33 %, max 1.18 % | max 5.6e-14 % |

`docs/findings/cam/lacx_page_vs_server_{before,after}.json`. The "before"
column is also what a student sees change on opening a saved U 4f project:
the page's LA areas move by 0.33 % at the median, 1.2 % at most, to the
curve the server actually fitted.

## 3. Sites

| # | site | before | after |
|---|---|---|---|
| 1 | `laTrueCasaXPS_array` (+ `_laKernelHalf`, the kernel half-width it uses) | integer m = round(caM), kernel 2m+1, σ = m/3, own convolution and peak search | literal mirror of `_la_casaxps_true`: m clamped to [0, 499], continuous σ = m/3, half-width max(1, ⌈3.5σ⌉), unit-sum kernel, `np.convolve(base, k, 'same')` + the server's trim when the kernel is longer than the grid (index formula pinned against numpy on 3,000 random (N, K)), normalisation at `argmin |ε|` (first minimum), fallback max, m < 1e-3 = bare base curve |
| 2 | `evalPeakArray` LA gate | array path only when `Math.round(caM) > 0` | every LA through the array path (it handles m < 1e-3 itself) |
| 3 | `laTrueCasaXPS` (scalar) | base curve, m ignored | unchanged; comment corrected; parity guard (C) proves no shipped caller |
| 4 | m input (`renderPeakForm`) | `Math.round(caM)`, step 1, "Integer 0–499" | the value to 2 dp, step 0.1, "continuous" |
| 5 | `runFitLocal` free-parameter block + clamp | a free `caM` made free, then `Math.round`ed by the clamp | `caM` never made free: held at its exact value |
| 6 | `runFitLocal` `isDiscrete` (Jacobian skip, sensitivity, certificate, dof, per-component support p) | `caM` discrete → never moved, not a dof | nothing discrete (no free parameter is); m is not a dof because it is not free |
| 7 | local-fit caveat (`_localFitDetail`, `_LOCALFIT_TOOLTIP`, fallback banner) | "differ … for LA components (m held at its start locally)" | unchanged — true again, and now exactly (§4) |
| 8 | `peakToBackendSpec` (`m`, `fix_m`), `_applyBackendParams` (writes `par.m`), exports (`p.caM`), Find Peaks mapping (`o.caM = p.m`), `syncKeys` / `LINK_SYNC_KEYS`, `_STARTS_MODEL_FIELDS`, Python twins | carry the value as is | unchanged (they already carried the fractional server value) |
| 9 | defaults (`caM: 50`, `fixCaM: true`; server `fix_m` default true) | — | unchanged |

## 4. The re-measurement (`scripts/local_server_gap.js` → `docs/findings/cam/local_server_gap_after_cam.json`)

W1's 18 targets, local engine (m held exactly) vs server from the same
scaled start; the control arm is the server with LA's m held at the SAME
exact value.

| U 4f target | local vs server, m free (χ²ᵣ; max Δarea) | local vs server, m held |
|---|---|---|
| Scan_0, 2, 3, 7 | −0.2 to +0.6 %; ≤ 2.07 % | +0.1 to +0.8 %; ≤ 0.60 %, ≤ 0.04 pp |
| Scan_1 | +1.4 %; 2.22 % | +1.7 %; 2.12 %, 0.12 pp |
| Scan_4 | +10.1 %; 8.64 % | +5.4 %; 5.34 %, 0.19 pp |
| Scan_5 | +10.4 %; 6.81 % | +9.7 %; 5.49 %, 0.24 pp |
| Scan_6 | −4.8 %; 8.62 % | +1.1 %; 1.60 %, 0.07 pp |
| Scan_8 | +12.8 %; 8.47 % | +13.2 %; 8.23 %, 0.32 pp |

C 1s unchanged (8 of 9 within 3.8 meV / 0.5 % / 1.4 % / 0.32 pp; Scan_4 is
findings §2). The picture is A03's: where the server holds m too, the
engines agree except on the three worse-minimum targets (Scan_4/5/8, the
local engine 5–13 % above); on Scan_6 the whole gap is m moving on the
server. The "starting point" label stays, on both grounds, and the caveat
("differ … for LA components (m held at its start locally) or where the
model has several minima") is true — now exactly, since m is held at its
value rather than rounded.

A note on the withdrawn attempt: with m free and the piece-confined
derivative, the local engine reached the same minimum as the server on
Scan_6's neighbourhood and even a lower one (−5.7 %) — the gain was real,
but the method was not sound on a discontinuous parameter (§7).

## 5. Verification

- `tests/js/lineshape_parity.test.js`: (A) LACX m > 0 and (D) LACX m > 0
  (fractional m, the 1e-3 threshold, 499) are hard assertions; new (D‴)
  sweeps the LA box on six more grids incl. 9- and 2-point grids (kernel
  longer than the grid). `tests/js/lineshape_roundtrip.test.js`: no shape
  has a known gap; LA m locked at 499 and at a fractional 8.66 round-trip
  with the curve compared. `tests/js/local_lm_descent.test.js`: the local
  engine holds m exactly (a fractional 5.37 stays 5.37, free or locked, not
  a dof); the four Codex reproducers of rounds 1–2 converge. JS suite
  (final): 422 tests, 420 pass, 2 todo (the scalar evaluators of the two
  convolved shapes, by design).
- Browser check (`browser_check_cam.py`, dev :5151): committed
  UCl4-graphite U4f Scan loads with m 8.2 shown as "8.2"; Run Fit → LA
  drawn vs fitted 1.1e-13 of amplitude (was 5.6e-3), Results area equal to
  the server curve's (was −0.66 %); Batch Fit onto U4f Scan_1 converges;
  no page errors. Re-run on the final commit: Batch Fit onto U4f Scan_1
  converges and keeps m at exactly 6.4945… (the value it was given); LA
  drawn vs fitted 1.1e-13; areas exact.
- Python suite: 993 passed, 7 skipped (on the round-0 commit df388ce; the
  round-1 change is page-only).

## 6. Release-note line

LA(α, β, m) components are now drawn, integrated and exported with the same
continuous m the server fits (the page rounded it to a whole number of
points): opening a saved U 4f project moves an LA component's area by
0.33 % at the median and 1.2 % at most, to the curve that was actually
fitted. m is shown to 0.01. Batch Fit keeps m exactly at the value it is
given (it used to round it to a whole number).

## 7. Codex rounds

**Round 1 (`docs/autofit/codex/cam_continuous_verdict_run{A,B}.md`):
NO-GO ×2, one finding, the same in both.** MAJOR — LA's curve JUMPS where
the kernel half-width max(1, ⌈3.5 m/3⌉) changes (m = 6k/7), so a
central-difference step for m that straddles a jump is not a derivative;
with m now free, local fits that converge with m held stalled and failed
(run A: 201 points at 0.03 eV, m 48; run B: 61 points at 0.05 eV,
m 18/7 − 0.001). lmfit escapes it only because its step is ~1e-8. Fixed
in the local engine's Jacobian, not in the mirror: one shared
`_laKernelHalf(m)` (used by the evaluator and the Jacobian, so they cannot
disagree) and a difference that stays inside the current piece —
one-sided when one side crosses, the step halved when both would. Both
reproducers are regression tests (they fail on df388ce, pass now; freeing
m never ends worse than holding it). `scripts/cam_transition_sweep.js`
(→ `docs/findings/cam/transition_sweep.json`): 210 local LA fits started
around 7 transitions × 5 offsets × 3 grid steps × 2 starts — 0 fail with m
free, 0 with m held, 0 end worse free than held. The §4 re-measurement,
re-run on the fixed engine, is unchanged to the digits quoted.

**Round 2 (`cam_continuous_r2_verdict_run{A,B}.md`): NO-GO ×2.** Round 1's
reproducers pass, but: (1) MAJOR — the LM STEP still crosses the jumps: a
fit started exactly on a transition (m = 18/7) with amplitude and m free
exhausts damping (every positive step, down to Δm ≈ 3e-12, lands across
the jump and raises χ²); 17 failures in 540 near-truth starts. (2) MAJOR —
a regression introduced by round 1's fix: next to the no-convolution
threshold (noiseless m = 0 data, start m = 0.001) the piece-confined
derivative is zero, SENS_MIN fails the fit before the certificate can
reach m = 0 (main converges). Both are consequences of fitting a
discontinuous parameter with a smooth method; each patch had uncovered the
next reachable failure — the pattern of the DE and anchor units. So the
free-m half was WITHDRAWN rather than patched a third time: the local
engine holds m exactly (§1), the piece-confined derivative is removed,
all four reproducers are regression tests that converge, and the control
arm of `local_server_gap.js` now holds the server's m at the same exact
value. The page half (the user-facing defect) was clean in both rounds.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-VvbE1uEn' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-DWZjldUc' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index 7e8b8bd..ea02c0a 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -115,7 +115,7 @@ tab reordering exists.
 | `asym-GL` | GL with asymmetric FWHM broadening on high-BE side |
 | `DS` | Doniach-Šunjić, `dsAlpha` (0–0.5) + `dsGamma` |
 | `DSG_LA` | DS+G — DS asymmetric core convolved with Gaussian. Frontend params `laAlpha`/`laBeta`/`laM`; backend id `ds_g`. |
-| `LACX` | True CasaXPS LA(α,β,m) — asymmetric Lorentzian + integer-kernel Gauss conv. Frontend params `caAlpha`/`caBeta`/`caM`; backend id `la_casaxps`. |
+| `LACX` | True CasaXPS LA(α,β,m) — asymmetric Lorentzian + Gauss conv with a CONTINUOUS m (data points; σ = m/3, half-width ⌈3.5σ⌉) on both sides since the caM unit (2026-09-25). Frontend params `caAlpha`/`caBeta`/`caM`; backend id `la_casaxps`. |
 
 **What the page draws must be what the server fitted.** Two harnesses pin
 it: `tests/js/lineshape_roundtrip.test.js` builds the request with the
@@ -132,9 +132,16 @@ to the optimiser's bounds (a DS+G m locked at 0 fitted at 0.05 —
 `_make_peak_params._set` now widens a limit to a held value), and the
 server clipping DS+G α to 0.495 where the page did not (`_dsgAlpha`). A
 held parameter is held at its value; what the page draws is what the
-server fitted. Tracked gap, `todo` in both files: LACX with m > 0 (the page draws
-a rounded integer kernel; the server fits m continuously — the `caM` clamp
-unit). DS+G was the other gap until 2026-09-22 (the page's quadrature
+server fitted. No shape carries a tracked gap any more. LACX with m > 0 was
+the last (the page drew m rounded to an integer 2m+1 kernel while the
+server fits it continuously: up to 0.97 % of amplitude and 1.2 % of area on
+the lab's U 4f components) until the `caM` unit, 2026-09-25:
+`laTrueCasaXPS_array` now mirrors `_la_casaxps_true` (continuous σ = m/3,
+half-width max(1, ⌈3.5σ⌉), `np.convolve` 'same' with the server's trim,
+normalisation at the grid point nearest the centre) — ≤ 7e-16 of amplitude
+on all 108 committed LA components, pinned across the α/β/m box on seven
+grids incl. grids shorter than the kernel
+(`docs/superpowers/plans/2026-09-25-cam-continuous.md`). DS+G was the other gap until 2026-09-22 (the page's quadrature
 `laCasaXPS` sized its step to the Lorentzian core, not the Gaussian kernel,
 and was wrong by up to 1e52 × amplitude at β = 2, m = 0.05 and 5–21 % low
 in area on the very box Find Peaks emits for a graphitic C 1s line);
@@ -228,7 +235,7 @@ names `caAlpha` / `caBeta` / `caM` so users do not confuse them with DS+G's
 |-----------|---------|
 | α (`caAlpha`) | High-BE-side exponent on the unit-amplitude Lorentzian; dimensionless, default 1.0, bounds 0.1–5.0 |
 | β (`caBeta`) | Low-BE-side exponent; dimensionless, default 1.0, bounds 0.1–5.0 |
-| m (`caM`) | Gaussian convolution kernel width in DATA POINTS (not eV); integer, default 50, bounds 0–499 |
+| m (`caM`) | Gaussian convolution kernel width in DATA POINTS (not eV); continuous (the server fits it continuously so its derivative exists; the page draws the same continuous value since 2026-09-25 — it drew an integer kernel; the local engine HOLDS it exactly, since LA's curve jumps at m = 6k/7 and a smooth optimiser cannot fit it), default 50, bounds 0–499 |
 
 α=β=1, m=0 reduces exactly to a pure Lorentzian. Increasing α
 **suppresses** the high-BE tail; decreasing α extends it (BE-axis
@@ -488,8 +495,10 @@ Damping exhaustion is a FAILURE. Poisson-weighted since unit W1
 (2026-09-18): it minimises Σ(w·r)² with w = 1/√max(raw counts, 1), the
 server's weighting, so its statistic is a real χ²ᵣ (objective
 `poisson_weighted_chi_square`); results saved by unit A0 were unweighted
-and stay labelled "Residual variance". It produces no uncertainties, and
-the integer-clamped `caM` is not optimised (carried at its start value).
+and stay labelled "Residual variance". It produces no uncertainties, and it
+HOLDS LA's `caM` at its exact value (it used to round it in its clamp; a
+free m was tried in the `caM` unit and withdrawn: LA's curve is
+discontinuous in m, `docs/superpowers/plans/2026-09-25-cam-continuous.md`).
 
 **A local result is a STARTING POINT, not a reportable result** (keyed on
 `engine: 'local'`, helpers `_isLocalFit` / `_isLocalModel` /
@@ -500,22 +509,21 @@ GL-type models (≤ 4 meV, ≤ 1.4 % area on the lab's C1s scans) and on Voigt
 components (fixed η = 0.5 on both sides since A03: on the 5 of 9 committed
 U 4f targets where both engines reach the same minimum every component
 agrees within 4.3 meV, 2.6 % FWHM, 2.0 % area, 0.12 pp — W1 had measured up
-to 20.8 % area on the Voigt satellites); it still differs on the other 4
-U 4f targets (satellite areas up to 8.9 %, 0.77 pp) for two reasons,
-separated by a control arm (the server with every LA m held at its start):
-on one target the `caM` clamp (`caM` held at its start locally while the
-server fits m continuously; holding m on the server closes the gap), on
-three the local descent stopping at a χ²ᵣ 5–13 % above the server's from
-the same start with the same free parameters — a worse minimum, the
-"several minima" case (both engines' amplitude floor is 0 since unit
-step (b)). Both engines weight by
+to 20.8 % area on the Voigt satellites); it still differs on the other U 4f
+targets for two reasons, separated by a control arm (the server with LA's
+m held at the same value): the `caM` hold (the server fits m, the local
+engine holds it — on Scan_6 the whole gap), and the local descent stopping
+in a worse minimum (5–13 % χ²ᵣ above the held-m server on Scan_4/5/8) —
+the "several minima" case (`docs/findings/cam/local_server_gap_after_cam.json`;
+both engines' amplitude floor is 0 since unit step (b)). Both engines weight by
 √intensity whether the data are counts or CPS (a convention, not a
 calibrated uncertainty for rates); the formula is the same but the inputs
 are not bit-identical, because `uploadToBackend` rounds intensities to
-2 dp before the server weights them. A03 is done and the designation
-STAYS on both grounds; the `caM` clamp is the next unit, the worse-minimum
-outcome is recorded for the local-engine work after it, and the label is
-reconsidered only on a re-measurement after both. (The amplitude-bound change
+2 dp before the server weights them. A03 and the `caM` unit are done and
+the designation STAYS on both grounds: fitting m locally needs a
+derivative-free search (its own unit), and the worse-minimum outcome
+(three of nine U 4f targets) remains; the label is reconsidered only on a
+re-measurement after that work. (The amplitude-bound change
 DECIDED 2026-09-18 — `docs/findings/2026-09-fit-determinacy.md` §3 — is
 implemented: unit step (b), 2026-09-22, below.) The same file records that a
 converged server fit is not ground truth: on a committed C 1s scan the
cat: package.json: No such file or directory
4081:// (caM unit, 2026-09-25). m is CONTINUOUS in data points (the server fits it
4095:// uses it to stay inside one piece (Codex round 1 of the caM unit).
4096:function _laKernelHalf(m) {
4116:  const half = _laKernelHalf(mc);
4168:    y = laTrueCasaXPS(x, center, p.fwhm, p.caAlpha, p.caBeta, p.caM);
4371:    // every m, continuous, as the server (caM unit 2026-09-25; it was
4372:    // Math.round(p.caM) > 0 → integer kernel)
4373:    const yArr = laTrueCasaXPS_array(beArr, p.center, p.fwhm, p.caAlpha, p.caBeta, p.caM);
5271:    caM: 50,
5325:  'LACX':       { caAlpha: 1.0,  fixCaAlpha: false, caBeta: 1.0, fixCaBeta: false, caM: 50, fixCaM: true },
5998:  const syncKeys = ['center','amplitude','fwhm','shape','glMix','asymmetry','dsAlpha','dsGamma','laAlpha','laBeta','laM','caAlpha','caBeta','caM'];
6361:        <input type="number" value="${Number.isFinite(p.caM) ? +p.caM.toFixed(2) : 50}" step="0.1" min="0" max="499"
6362:          oninput="updatePeakParam(${p.id},'caM',parseFloat(this.value))">
6506:    spec.m     = Number.isFinite(p.caM)     ? p.caM     : 50.0;
6544:  if (par.m       && p.shape === 'LACX' && !p.fixCaM)     p.caM     = par.m.value;
7609:  'laAlpha', 'laBeta', 'laM', 'caAlpha', 'caBeta', 'caM', 'linked', 'linkOffset', 'linkRatio', '_afAsymMin', '_afAsymMax',
8038:// exactly, at its start locally - LA is discontinuous in m, caM unit) and
8206:        // caM is HELD at its value — exactly, not rounded, not a degree of
8209:        // parameter: freeing it (caM unit, 2026-09-25) stalled fits at the
8238:    'laAlpha', 'laBeta', 'laM', 'caAlpha', 'caBeta', 'caM'];
8240:  function applyParams(params) {
8261:    applyParams(params);
8283:    applyParams(params);                     // working copy = current point
8295:    applyParams(params);
8322:  // No free parameter is discrete: caM is never made free here (it is held
8323:  // at its exact value, see the free-parameter block). Until the caM unit it
8460:  applyParams(params);
8471:  // Degrees of freedom count the parameters this engine varies (caM is held,
8558:  // evalPeakArray(), not a per-point evalPeak map: for LACX with caM > 0,
8560:  // evalPeak silently returns the unconvolved base regardless of caM.
10232:  // for LACX with caM > 0, only the array evaluator applies the shape's
10233:  // Gaussian convolution — evalPeak silently ignores caM. These curves
10899:  // LACX with caM > 0, only the array evaluator applies the shape's
10900:  // Gaussian convolution — evalPeak silently ignores caM, which would
11049:      // convolution for LACX with caM > 0, which evalPeak ignores.
11081:      // convolution for LACX with caM > 0, which evalPeak ignores.
11317:    case 'LACX':    return { gl: '',            alpha: p.caAlpha ?? '', beta: p.caBeta ?? '', m: p.caM ?? '' };
12010:async function runPropagation() {
14546:      <button class="btn btn-accent" id="propagate-run-btn" onclick="runPropagation()">Propagate &amp; Fit</button>
15930:      o.caAlpha = p.alpha ?? 1; o.caBeta = p.beta ?? 1; o.caM = p.m ?? 50; break;

exec
/bin/zsh -lc "git diff main..HEAD -- templates/index.html | tail -105; sed -n '8110,8525p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
exec
/bin/zsh -lc "git diff main..HEAD -- tests/js/lineshape_parity.test.js tests/js/lineshape_roundtrip.test.js tests/js/local_lm_descent.test.js; sed -n '11960,12320p' templates/index.html; rg -n 'def _la_casaxps_true|node --test|PYTHON|python3' fitting.py tests/js/lineshape_parity.test.js tests/js/lineshape_roundtrip.test.js tests/js/local_lm_descent.test.js; rg --files -g '*AGENTS*' -g '*package*' -g '*test*' | head -35" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 29ms:
+    let acc = 0;
+    const t0 = Math.max(0, j - (N - 1)), t1 = Math.min(K - 1, j);
+    for (let t = t0; t <= t1; t++) acc += base[j - t] * kern[t];
+    out[i] = acc;
+  }
+  let pk = 0;
+  for (let i = 1; i < N; i++) if (Math.abs(xArr[i] - center) < Math.abs(xArr[pk] - center)) pk = i;   // np.argmin: first minimum
+  let pv = N ? out[pk] : 0;
+  if (!(pv > 0)) { let mx = -Infinity; for (let i = 0; i < N; i++) if (out[i] > mx) mx = out[i]; pv = mx; }
+  if (!(pv > 0)) return new Array(N).fill(0);
+  for (let i = 0; i < N; i++) out[i] = out[i] / pv;
   return out;
 }
 
@@ -4348,7 +4367,9 @@ function dsgConvolved_array(beArr, center, alpha, beta, mGauss) {
 // DSG_LA (every m: the delta branch below 0.001, the convolution above) so
 // the padding, kernel and normalisation see the whole grid.
 function evalPeakArray(beArr, p) {
-  if (p.shape === 'LACX' && Math.round(p.caM || 0) > 0) {
+  if (p.shape === 'LACX') {
+    // every m, continuous, as the server (caM unit 2026-09-25; it was
+    // Math.round(p.caM) > 0 → integer kernel)
     const yArr = laTrueCasaXPS_array(beArr, p.center, p.fwhm, p.caAlpha, p.caBeta, p.caM);
     const out = new Array(beArr.length);
     const amp = p.amplitude;
@@ -6334,10 +6355,10 @@ function renderShapeControls(p) {
         </div>
       </div>
       <div class="field">
-        <label data-xps-tip="Gaussian convolution kernel width in DATA POINTS (not eV). Integer 0–499. m=0 = no convolution. Effective eV width ≈ (m/3) × dx where dx is the data step size.">m (Gauss kernel pts)
+        <label data-xps-tip="Gaussian convolution kernel width in DATA POINTS (not eV), 0–499. Continuous: the fit returns a fractional value and the curve is drawn with it. m=0 = no convolution. Effective eV width ≈ (m/3) × dx where dx is the data step size.">m (Gauss kernel pts)
           ${!isLinked ? `<button class="lock-btn${p.fixCaM ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixCaM',this)" title="${p.fixCaM ? 'Unlock' : 'Lock'} during fitting">${p.fixCaM ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
         </label>
-        <input type="number" value="${Math.round(p.caM ?? 50)}" step="1" min="0" max="499"
+        <input type="number" value="${Number.isFinite(p.caM) ? +p.caM.toFixed(2) : 50}" step="0.1" min="0" max="499"
           oninput="updatePeakParam(${p.id},'caM',parseFloat(this.value))">
       </div>
     `;
@@ -8013,12 +8034,9 @@ function _fitStatLabel(fr) {
 // (2026-09-22: Voigt = fixed eta 0.5 on BOTH sides), on Voigt components
 // wherever the two engines reach the same minimum (5 of 9 committed U 4f
 // targets: every component within 4.3 meV, 2.6 % FWHM, 2 % area, 0.12 pp);
-// it still differs on the other 4 U 4f targets (satellite areas up to
-// 8.9 %, 0.77 pp): on one because the LA m is held at its start locally
-// (the gap closes when the server holds m too), on three because the local
-// descent stops at a higher chi2r than the server from the same start
-// (+5 to +13 %, with m held as well) - several minima - and it gives no
-// uncertainties. Unweighted A0-era results differed by more than 100 %.
+// it still differs where an LA component's m moves on the server (held,
+// exactly, at its start locally - LA is discontinuous in m, caM unit) and
+// where the model has several minima; and it gives no uncertainties. Unweighted A0-era results differed by more than 100 %.
 // Every site that shows, exports or saves a fit result carries the
 // designation, keyed on persisted identity so reloaded results are labelled.
 const _LOCAL_FIT_CAVEAT = 'Local fit (Poisson-weighted like the server, no uncertainties): a starting point, not a reportable result. Run Fit before reporting.';
@@ -8185,7 +8203,13 @@ function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
       if (p.shape === 'LACX') {
         if (!p.fixCaAlpha) { freeParams.push(Number.isFinite(p.caAlpha) ? p.caAlpha : 1.0); paramMap.push({id: p.id, param: 'caAlpha'}); }
         if (!p.fixCaBeta)  { freeParams.push(Number.isFinite(p.caBeta)  ? p.caBeta  : 1.0); paramMap.push({id: p.id, param: 'caBeta'}); }
-        if (!p.fixCaM)     { freeParams.push(Number.isFinite(p.caM)     ? p.caM     : 50);  paramMap.push({id: p.id, param: 'caM'}); }
+        // caM is HELD at its value — exactly, not rounded, not a degree of
+        // freedom. LA's curve jumps where its kernel half-width changes
+        // (m = 6k/7), and a smooth local optimiser cannot fit a discontinuous
+        // parameter: freeing it (caM unit, 2026-09-25) stalled fits at the
+        // jumps and a derivative confined to one piece failed next to the
+        // no-convolution threshold (Codex rounds 1–2). The server fits m;
+        // Batch Fit carries the value it is given.
       }
     }
   }
@@ -8208,7 +8232,6 @@ function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
     if (param === 'laM')          return Math.max(0.05, Math.min(4.0, v));
     if (param === 'caAlpha')      return Math.max(0.1, Math.min(5.0, v));
     if (param === 'caBeta')       return Math.max(0.1, Math.min(5.0, v));
-    if (param === 'caM')          return Math.max(0,   Math.min(499, Math.round(v)));
     return v;
   }
   const LINK_SYNC_KEYS = ['glMix', 'asymmetry', 'dsAlpha', 'dsGamma',
@@ -8296,10 +8319,11 @@ function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
     }
     return Math.max(1, Math.abs(vec[j]));
   };
-  // caM is rounded to an integer by its clamp, so a finite difference cannot
-  // see it: it is carried at its starting value (inherited behaviour; see the
-  // A0 follow-up list) and excluded from the stationarity test.
-  const isDiscrete = j => paramMap[j].param === 'caM';
+  // No free parameter is discrete: caM is never made free here (it is held
+  // at its exact value, see the free-parameter block). Until the caM unit it
+  // was made free and then ROUNDED by its clamp — a fractional server-fitted
+  // m of 8.2 was silently fitted as 8.
+  const isDiscrete = () => false;
   // MINPACK-style termination: (ftol) actual AND predicted relative
   // reductions both below FTOL, with the linearised model agreeing with
   // the actual reduction; (xtol) relative step below XTOL; (gtol) the
@@ -8444,9 +8468,8 @@ function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
     delete live._backendParams;
   }
 
-  // Degrees of freedom count the parameters this engine actually varies: the
-  // integer-clamped caM is carried at its start value and is not one of them
-  // (continuous parameters temporarily blocked at a wall still count).
+  // Degrees of freedom count the parameters this engine varies (caM is held,
+  // not one of them; parameters temporarily blocked at a wall still count).
   const nVaried = params.filter((_, j) => !isDiscrete(j)).length;
   const dof = Math.max(1, be.length - nVaried);
   const chiReduced = chi / dof;                       // weighted reduced chi-square, as lmfit's redchi
}
function _fitStatusText(fr) {
  const tag = !_isLocalFit(fr) ? '' : (_isUnweightedLocal(fr) ? ' (starting point)' : ' (local, starting point)');
  return _fitStatLabel(fr) + ' = ' + fr.chiReduced.toFixed(2) + tag;
}
function _applyStatCaption(fr) {
  const cap = document.getElementById('sb-chi-caption');
  if (!cap) return;
  cap.innerHTML = !_isLocalFit(fr) ? '&#967;&#178;&#7523;:'
    : (_isUnweightedLocal(fr) ? 'Residual variance (starting point):' : '&#967;&#178;&#7523; (local, starting point):');
}
// The statistic is displayed as ONE unit — header text + tooltip, status-bar
// caption + value — from the same fit result, or all cleared. Refreshing
// any one of them alone can pair a local value with a chi-square caption
// (Codex round 9).
function _applyStatDisplay(fr) {
  const fq = document.getElementById('fit-quality');
  const sb = document.getElementById('sb-chi');
  if (fr && Number.isFinite(fr.chiReduced)) {
    if (fq) { fq.textContent = _fitStatusText(fr); fq.setAttribute('data-xps-tip', _isLocalFit(fr) ? _LOCALFIT_TOOLTIP : _CHISQ_TOOLTIP); }
    if (sb) sb.textContent = fr.chiReduced.toFixed(3);
  } else {
    if (fq) { fq.innerHTML = '&#967;&#178; &mdash;'; fq.removeAttribute('data-xps-tip'); }
    if (sb) sb.textContent = '\u2014';
  }
  _applyStatCaption(fr);
  _updateLocalModelBanner();
}

// Local Levenberg-Marquardt: the fallback engine, and the ONLY engine Batch
// Fit uses.
//
// ACCEPTANCE RULE (unit A0, 2026-09-15): this function never writes to
// state.peaks or state.fitResult unless the optimiser converged. It works on
// a copy of the peak list and commits the copy on success; on
// non-convergence the previous peaks and the previous fit result are left
// exactly as they were and the caller receives { success: false }.
//
// History: from the initial commit (f20d71b) until this unit the update
// step solved JtJ.dp = +Jt.r with r = data - model, i.e. an ASCENT step, so
// every step was rejected, lambda inflated past 1e8 and the loop returned
// the STARTING model announced as "Fit complete (local LM)". The
// convergence test also compared chi-square with itself after acceptance.
// Both are pinned by tests/js/local_lm_descent.test.js, which replays the
// committed lab project; the proof is in
// docs/superpowers/plans/2026-09-15-a01-local-lm-proof.md.
function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
  const maxIter = Number.isFinite(options.maxIterations) ? options.maxIterations : 3000;
  const fail = (message, iterations) => {
    _hideFitSpinner();
    document.getElementById('sb-msg').textContent = 'Local fit failed';
    notify('Local fit did not converge: ' + message + ' Previous peaks and result kept.', 'red', true);
    return { success: false, engine: 'local', message, iterations: iterations || 0 };
  };
  if (!Array.isArray(be) || be.length < 2 ||
      !Array.isArray(bgSubtracted) || bgSubtracted.length !== be.length ||
      !Array.isArray(bgIntensity) || bgIntensity.length !== be.length ||
      !be.every(Number.isFinite) || !bgSubtracted.every(Number.isFinite) || !bgIntensity.every(Number.isFinite)) {
    return fail('invalid or non-finite data in the fitting region.');
  }
  // POISSON WEIGHTS (unit W1): the same weighting fitting.run_fit applies on
  // the server — sigma = sqrt(raw counts), floored at 1, where the raw
  // counts are the background-subtracted signal plus the background.
  const _w = be.map((_, i) => 1 / Math.sqrt(Math.max(bgSubtracted[i] + bgIntensity[i], 1)));
  // Work on copies: live peaks are touched only on success.
  const work = state.peaks.map(p => ({ ...p }));
  if (!work.length) return fail('no peaks to fit.');
  const workPeak = id => work.find(q => q.id === id);

  const freeParams = [];
  const paramMap = [];
  for (const p of work) {
    if (!p.linked) {
      if (!p.fixCenter)    { freeParams.push(p.center);    paramMap.push({id: p.id, param: 'center'}); }
      if (!p.fixFwhm && p.shape !== 'DSG_LA') { freeParams.push(p.fwhm); paramMap.push({id: p.id, param: 'fwhm'}); }
      if (!p.fixAmplitude) { freeParams.push(p.amplitude); paramMap.push({id: p.id, param: 'amplitude'}); }
      if ((p.shape === 'GL' || p.shape === 'asym-GL') && !p.fixGlMix) {
        freeParams.push(p.glMix); paramMap.push({id: p.id, param: 'glMix'});
      }
      if (p.shape === 'asym-GL' && !p.fixAsymmetry) {
        freeParams.push(p.asymmetry); paramMap.push({id: p.id, param: 'asymmetry'});
      }
      if (p.shape === 'DS' && !p.fixDsAlpha) {
        freeParams.push(p.dsAlpha); paramMap.push({id: p.id, param: 'dsAlpha'});
      }
      if (p.shape === 'DS' && !p.fixDsGamma) {
        freeParams.push(p.dsGamma); paramMap.push({id: p.id, param: 'dsGamma'});
      }
      if (p.shape === 'DSG_LA') {
        if (!p.fixLaAlpha) { freeParams.push(Number.isFinite(p.laAlpha) ? p.laAlpha : 0.10); paramMap.push({id: p.id, param: 'laAlpha'}); }
        if (!p.fixLaBeta)  { freeParams.push(Number.isFinite(p.laBeta)  ? p.laBeta  : 0.3);  paramMap.push({id: p.id, param: 'laBeta'}); }
        if (!p.fixLaM)     { freeParams.push(Number.isFinite(p.laM)     ? p.laM     : 0.4);  paramMap.push({id: p.id, param: 'laM'}); }
      }
      if (p.shape === 'LACX') {
        if (!p.fixCaAlpha) { freeParams.push(Number.isFinite(p.caAlpha) ? p.caAlpha : 1.0); paramMap.push({id: p.id, param: 'caAlpha'}); }
        if (!p.fixCaBeta)  { freeParams.push(Number.isFinite(p.caBeta)  ? p.caBeta  : 1.0); paramMap.push({id: p.id, param: 'caBeta'}); }
        // caM is HELD at its value — exactly, not rounded, not a degree of
        // freedom. LA's curve jumps where its kernel half-width changes
        // (m = 6k/7), and a smooth local optimiser cannot fit a discontinuous
        // parameter: freeing it (caM unit, 2026-09-25) stalled fits at the
        // jumps and a derivative confined to one piece failed next to the
        // no-convolution threshold (Codex rounds 1–2). The server fits m;
        // Batch Fit carries the value it is given.
      }
    }
  }
  if (!freeParams.every(Number.isFinite)) return fail('a free parameter is not a finite number.');

  // Parameter box. The amplitude floor is 0, the server's, since unit step (b)
  // (owner decision 2026-09-18: zero allowed in both engines; a component at
  // its floor is an explicit outcome). The active-set step holds a parameter
  // pushed into the wall, and paramScale is floored at 1, so a zero amplitude
  // is a valid, stationary point rather than a division by zero.
  function clamp(param, v) {
    if (param === 'fwhm')         return Math.max(0.1, Math.min(15, v));
    if (param === 'amplitude')    return Math.max(0, v);
    if (param === 'glMix')        return Math.max(0, Math.min(100, v));
    if (param === 'asymmetry')    return Math.max(0, Math.min(1, v));
    if (param === 'dsAlpha')      return Math.max(0, Math.min(0.49, v));
    if (param === 'dsGamma')      return Math.max(0, Math.min(5.0, v));
    if (param === 'laAlpha')      return Math.max(0, Math.min(0.49, v));
    if (param === 'laBeta')       return Math.max(0.05, Math.min(2.0, v));
    if (param === 'laM')          return Math.max(0.05, Math.min(4.0, v));
    if (param === 'caAlpha')      return Math.max(0.1, Math.min(5.0, v));
    if (param === 'caBeta')       return Math.max(0.1, Math.min(5.0, v));
    return v;
  }
  const LINK_SYNC_KEYS = ['glMix', 'asymmetry', 'dsAlpha', 'dsGamma',
    'laAlpha', 'laBeta', 'laM', 'caAlpha', 'caBeta', 'caM'];

  function applyParams(params) {
    for (let i = 0; i < params.length; i++) {
      const { id, param } = paramMap[i];
      const p = workPeak(id);
      if (p) p[param] = clamp(param, params[i]);
    }
    // Linked peaks follow their parent: centre + offset, amplitude x ratio,
    // and every lineshape parameter (the same constraint set the backend
    // enforces through lmfit expressions).
    for (const q of work) {
      if (!q.linked) continue;
      const parent = workPeak(q.linked);
      if (!parent) continue;
      if (Number.isFinite(q.linkOffset)) q.center = parent.center + q.linkOffset;
      if (Number.isFinite(q.linkRatio))  q.amplitude = parent.amplitude * q.linkRatio;
      q.fwhm = parent.fwhm;
      for (const k of LINK_SYNC_KEYS) if (parent[k] !== undefined) q[k] = parent[k];
    }
  }

  function rawResiduals(params) {
    applyParams(params);
    const model = evalAllPeaks(be, work);
    return be.map((_, i) => bgSubtracted[i] - model[i]);
  }
  // weighted residual: what the optimiser minimises (chi = sum of squares)
  function residuals(params) {
    return rawResiduals(params).map((v, i) => v * _w[i]);
  }

  function chiSq(params) {
    const r = residuals(params);
    return r.reduce((s, v) => s + v * v, 0);
  }

  let params = freeParams.map((v, i) => clamp(paramMap[i].param, v));
  let chi = chiSq(params);
  if (!Number.isFinite(chi)) return fail('the model is not finite at the starting parameters.');
  let lambda = 0.001;
  // Feasible-descent certificate (see PROBE_REL below). Returns true when
  // no single-parameter feasible move improves the residual by more than
  // FTOL; otherwise moves to the best such point and returns false.
  function certify() {
    applyParams(params);                     // working copy = current point
    let bestChi = chi, bestParams = null;
    for (let j = 0; j < params.length; j++) {
      if (isDiscrete(j)) continue;
      for (const sgn of [-1, 1]) {
        const trial = [...params];
        trial[j] = clamp(paramMap[j].param, params[j] + sgn * PROBE_REL * paramScale(j, params));
        if (trial[j] === params[j]) continue;
        const c = chiSq(trial);
        if (Number.isFinite(c) && c < bestChi) { bestChi = c; bestParams = trial; }
      }
    }
    applyParams(params);
    if (bestParams && bestChi < chi * (1 - FTOL)) {
      params = bestParams; chi = bestChi; certifyRestarts++;
      lambda = Math.max(lambda, 1e-3);
      return false;
    }
    return true;
  }
  // Finite-difference step per parameter. A centre's natural scale is the
  // peak WIDTH, not its binding energy: h*|285 eV| = 0.03 eV is wider than
  // a narrow peak and gave misleading derivatives (Codex round 1).
  const H_REL = 1e-4;
  // Scale of parameter j at the parameter VECTOR `vec` — a pure function of
  // the vector, never of the mutable working copy (which the Jacobian loop
  // leaves at its last perturbation — Codex round 5). A centre's scale is
  // its peak's width: from the vector when the width is free, from the
  // (never perturbed) fixed value otherwise.
  const fwhmIndex = {};
  paramMap.forEach((d, k) => { if (d.param === 'fwhm') fwhmIndex[d.id] = k; });
  const paramScale = (j, vec) => {
    const { id, param } = paramMap[j];
    if (param === 'center') {
      const w = fwhmIndex[id] !== undefined ? vec[fwhmIndex[id]] : (workPeak(id) || {}).fwhm;
      return Math.max(0.05, Number.isFinite(w) ? w : 1);
    }
    return Math.max(1, Math.abs(vec[j]));
  };
  // No free parameter is discrete: caM is never made free here (it is held
  // at its exact value, see the free-parameter block). Until the caM unit it
  // was made free and then ROUNDED by its clamp — a fractional server-fitted
  // m of 8.2 was silently fitted as 8.
  const isDiscrete = () => false;
  // MINPACK-style termination: (ftol) actual AND predicted relative
  // reductions both below FTOL, with the linearised model agreeing with
  // the actual reduction; (xtol) relative step below XTOL; (gtol) the
  // largest cosine between the residual and any Jacobian column below
  // GTOL. Tiny steps alone never count. FTOL = 1e-6 (relative chi-square):
  // on real 6-component C1s data with a vanished component the optimiser
  // otherwise crawls a flat valley for thousands of iterations changing
  // chi-square in its 7th digit and no parameter in its 5th.
  const FTOL = 1e-6, XTOL = 1e-8, GTOL = 1e-6, SENS_MIN = 1e-12;
  // CERTIFICATE: a tentative convergence (gtol / ftol / xtol) is accepted
  // only if no feasible move of PROBE_REL (scaled) in any single free
  // parameter reduces the residual by more than FTOL of its value. If one
  // does, that point is taken and iteration continues (Codex round 3: the
  // linearised model is not a stationarity certificate; a column-norm
  // cutoff froze determined parameters).
  const PROBE_REL = 1e-3, MAX_CERTIFY = 200;
  // No exit is exempt from the certificate: a tiny absolute residual is
  // still probed relatively (Codex round 4). The certificate is a
  // single-parameter (coordinate) feasible-descent check, not a proof of a
  // local minimum along coupled directions; the LM step handles coupling
  // during optimisation.
  let converged = params.length === 0 || (chi === 0 && certify());
  let iterations = 0;
  let acceptedSteps = 0;
  let certifyRestarts = 0;

  for (let iter = 0; iter < maxIter && !converged; iter++) {
    iterations++;
    if (certifyRestarts > MAX_CERTIFY) return fail('could not certify a stationary point after ' + iterations + ' iterations.', iterations);
    const r = residuals(params);
    const n = params.length;
    // Central-difference Jacobian d r / d p, stepping inside the parameter
    // box (one-sided at a wall).
    const J = [];
    for (let j = 0; j < n; j++) {
      const { param } = paramMap[j];
      const step = H_REL * paramScale(j, params);
      const pPlus = [...params], pMinus = [...params];
      pPlus[j] = clamp(param, params[j] + step);
      pMinus[j] = clamp(param, params[j] - step);
      const span = pPlus[j] - pMinus[j];
      if (span === 0) { J.push(r.map(() => 0)); continue; }
      const rPlus = pPlus[j] === params[j] ? r : residuals(pPlus);
      const rMinus = pMinus[j] === params[j] ? r : residuals(pMinus);
      J.push(rPlus.map((v, i) => (v - rMinus[i]) / span));
    }
    const JtJ = Array.from({length: n}, () => new Array(n).fill(0));
    const Jtr = new Array(n).fill(0);
    for (let a = 0; a < n; a++) {
      for (let b = 0; b < n; b++) {
        for (let i = 0; i < r.length; i++) JtJ[a][b] += J[a][i] * J[b][i];
      }
      for (let i = 0; i < r.length; i++) Jtr[a] += J[a][i] * r[i];
    }
    if (!Jtr.every(Number.isFinite) || !JtJ.every(row => row.every(Number.isFinite))) {
      return fail('the model derivative is not finite.', iterations);
    }
    // Sensitivity: a model that does not respond to any free parameter here
    // (e.g. a peak far outside the window) cannot be optimised — that is a
    // failure, not a stationary point.
    let sens = 0;
    for (let j = 0; j < n; j++) if (!isDiscrete(j)) sens = Math.max(sens, JtJ[j][j] * paramScale(j, params) ** 2);
    if (n > 0 && sens / Math.max(chi, 1e-300) < SENS_MIN) {
      return fail('the model has no measurable sensitivity to its free parameters in this region.', iterations);
    }
    // ACTIVE SET: a parameter whose descent direction points into a wall of
    // the parameter box (or that has no sensitivity, or is discrete) is held
    // FIXED for this step. Solving the joint system with such a parameter
    // and then clipping it would leave the other components of the step
    // meaningless and let a tiny "agreed" step pass the ftol test at a
    // non-stationary point (Codex round 2). With r = data - model,
    // d(chi)/dp_j = +2 * (J_j . r), so the descent direction is -sign(J_j . r).
    const active = [];
    let gradCos = 0;
    const rNorm = Math.sqrt(chi);
    for (let j = 0; j < n; j++) {
      if (isDiscrete(j) || !(JtJ[j][j] > 0)) continue;
      if (Jtr[j] !== 0) {
        const probe = clamp(paramMap[j].param, params[j] - Math.sign(Jtr[j]) * 1e-6 * paramScale(j, params));
        if (probe === params[j]) continue;          // blocked by the box
      }
      active.push(j);
      if (rNorm > 0) gradCos = Math.max(gradCos, Math.abs(Jtr[j]) / (Math.sqrt(JtJ[j][j]) * rNorm));
    }
    // Projected gradient test (gtol) over the active set only. A failed
    // certificate has moved the point: restart the iteration so the
    // derivatives and active set are rebuilt there.
    if (gradCos < GTOL) { if (certify()) { converged = true; break; } continue; }
    // Linear model of the residual, for the predicted reduction (ftol test).
    const JtJ0 = JtJ.map(row => row.slice());

    // Marquardt damping, then the DESCENT step on the active set:
    // JtJ_aa . dp_a = -Jt.r_a, dp = 0 for held parameters.
    const m = active.length;
    const A = active.map(a => active.map(b => (a === b ? JtJ[a][a] * (1 + lambda) + 1e-300 : JtJ[a][b])));
    const rhs = active.map(a => -Jtr[a]);
    const dpA = solveLinear(A, rhs, m);
    if (!dpA.every(Number.isFinite)) return fail('the normal equations are singular.', iterations);
    const dp = new Array(n).fill(0);
    active.forEach((a, k) => { dp[a] = dpA[k]; });
    const newParams = params.map((v, i) => clamp(paramMap[i].param, v + dp[i]));
    const step = newParams.map((v, i) => v - params[i]);
    const newChi = chiSq(newParams);

    if (Number.isFinite(newChi) && newChi < chi) {
      const actred = (chi - newChi) / Math.max(chi, 1e-300);
      // predicted reduction of the linearised problem: (2 Jt.r . (-dp) - dp.JtJ.dp) / chi
      let lin = 0, quad = 0;
      for (let a = 0; a < n; a++) {
        lin += Jtr[a] * step[a];
        for (let b = 0; b < n; b++) quad += step[a] * JtJ0[a][b] * step[b];
      }
      const prered = (-2 * lin - quad) / Math.max(chi, 1e-300);
      const relStep = Math.max(0, ...step.map((d, i) => Math.abs(d) / paramScale(i, params)));
      params = newParams;
      chi = newChi;
      acceptedSteps++;
      lambda *= 0.7;
      if (chi === 0 || (prered > 0 && actred <= FTOL && prered <= FTOL && actred / prered <= 2) || relStep <= XTOL) {
        if (certify()) { converged = true; break; }
      }
    } else {
      lambda *= 3;
      if (lambda > 1e8) {
        // Even a tiny steepest-descent step no longer reduces the residual,
        // yet the projected gradient is not small: stalled, not converged.
        return fail('the optimiser stalled (no step reduces the residual) after ' + iterations + ' iterations.', iterations);
      }
    }
  }
  if (!converged) return fail('iteration limit (' + maxIter + ') reached.', iterations);

  // ── Converged: commit the working copy to the live peaks ──────────────────
  applyParams(params);
  for (const p of work) {
    const live = getPeak(p.id);
    if (!live) continue;
    Object.assign(live, p);
    // A local fit has no backend covariance; any _backendParams on the peak
    // belong to an earlier server fit (or, in Batch Fit, to the SOURCE
    // spectrum's fit) and must not travel with this result.
    delete live._backendParams;
  }

  // Degrees of freedom count the parameters this engine varies (caM is held,
  // not one of them; parameters temporarily blocked at a wall still count).
  const nVaried = params.filter((_, j) => !isDiscrete(j)).length;
  const dof = Math.max(1, be.length - nVaried);
  const chiReduced = chi / dof;                       // weighted reduced chi-square, as lmfit's redchi
  const _raw = rawResiduals(params);
  const rmse = Math.sqrt(_raw.reduce((a, v) => a + v * v, 0) / be.length);   // unweighted RMS, as the server path reports
  // "Not supported by the data": the same removal statistic the server
  // computes, from this engine's own residuals and weights (a component driven
  // to the zero floor is an outcome here too, not something to hide).
  {
    const model = evalAllPeaks(be, work);
    const verdicts = {};
    for (const wp of work) {
      if (wp.linked) continue;
      const comp = evalPeakArray(be, wp);
      const nFreeComp = paramMap.filter(d => d.id === wp.id && !isDiscrete(paramMap.indexOf(d))).length;
      verdicts[String(wp.id)] = _componentSupportCore(bgSubtracted, model, comp, _w, nFreeComp, nVaried);
    }
    _applySupportVerdicts(state.peaks, id => verdicts[String(id)] || null, _startsLiveKey());
  }

  // KNOWN LIMITATION: this engine produces no parameter uncertainties; the
  // results panel shows blank sigma for every parameter after a local fit.
  const roiRange = { min: _arrMin(be).toFixed(1), max: _arrMax(be).toFixed(1) };
  { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }   // a new result supersedes imported provenance
  state.fitResult = { chi, chiReduced, rmse, be, bgSubtracted, bgIntensity, roiRange,
                      engine: 'local', status: 'converged',
                      objective: 'poisson_weighted_chi_square', weighting: '1/sqrt(max(counts,1))', iterations,
                      reportable: false, caveat: _LOCAL_FIT_CAVEAT };
  state.fitResult.rFactor = _computeRFactor(state.fitResult);

  _applyStatDisplay(state.fitResult);
  document.getElementById('sb-msg').textContent = 'Fit complete (local)';
  _updateRFactorUI(state.fitResult.rFactor);
  _updateROIDisplay(roiRange);

  renderPeakList();
  updatePlot();
  renderResults();

  _hideFitSpinner();
  notify('Local fit converged in ' + iterations + ' iteration' + (iterations === 1 ? '' : 's') +
         '. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3) + ' (Poisson-weighted; no uncertainties). Starting point only: run Fit before reporting.', 'amber');
  _autoSnapshot();
  return { success: true, engine: 'local', iterations, acceptedSteps, chiReduced, certifyRestarts };
}

function solveLinear(A, b, n) {
  const M = A.map((row, i) => [...row, b[i]]);
  for (let col = 0; col < n; col++) {
    let maxRow = col;
    for (let row = col + 1; row < n; row++) {
      if (Math.abs(M[row][col]) > Math.abs(M[maxRow][col])) maxRow = row;
    }

 succeeded in 40ms:
    hideTip();
  }, true);

  // Update tooltip text when user changes the selection
  document.addEventListener('change', function (e) {
    const sel = e.target instanceof Element ? e.target.closest('.xps-tip-select') : null;
    if (!sel) return;
    const text = getTipText(sel);
    if (tip.classList.contains('visible')) showTip(sel, text);
  });
})();

// ══════════════════════════════════════════════════════════════
// FEATURE 1: BATCH PROCESSING — PROPAGATE FIT MODEL
// ══════════════════════════════════════════════════════════════

function showPropagateModal() {
  if (!tabManager.activeId) { notify('No active tab.', 'amber'); return; }
  const sourceTab = tabManager._getTab(tabManager.activeId);
  if (!sourceTab || !sourceTab.peaks || !sourceTab.peaks.length) {
    notify('No peaks defined on this tab.', 'amber'); return;
  }

  const list = document.getElementById('propagate-tab-list');
  const prog = document.getElementById('propagate-progress');
  const summary = document.getElementById('propagate-summary');
  prog.textContent = '';
  summary.style.display = 'none';
  summary.innerHTML = '';

  const otherTabs = tabManager.tabs.filter(t => t.id !== tabManager.activeId && !t.isSurvey);
  if (!otherTabs.length) {
    list.innerHTML = '<div style="font-size:11px;color:var(--text3);padding:8px;font-family:var(--mono)">No other spectra tabs open.</div>';
  } else {
    list.innerHTML = otherTabs.map(t => `
      <label class="propagate-tab-row">
        <input type="checkbox" class="prop-chk" data-id="${t.id}" checked>
        <span class="propagate-tab-swatch" style="background:${t.color}"></span>
        <span>${_escHtml(t.name)}</span>
      </label>`).join('');
  }

  document.getElementById('propagate-run-btn').disabled = false;
  document.getElementById('propagate-modal-overlay').classList.add('open');
}

function _propagateSelectAll(checked) {
  document.querySelectorAll('.prop-chk').forEach(c => c.checked = checked);
}

async function runPropagation() {
  // Loud missing-load guard (mirrors the RefCore guard): batch fit depends on the
  // shipped BatchPropagation module for the source→target settings merge. If its
  // script failed to load, fail clearly and BEFORE mutating any state (button,
  // snapshot suppression, tab records) rather than throwing mid-propagation.
  if (typeof BatchPropagation === 'undefined' || !BatchPropagation.propagateFitUi) {
    notify('Batch-fit module failed to load (static/js/batch_propagation.js). Reload the page and try again.', 'red', true);
    return;
  }
  const sourceId = tabManager.activeId;
  const sourceTab = tabManager._getTab(sourceId);
  if (!sourceTab) return;

  // Sync source state to record before we leave it
  tabManager._syncActiveToRecord();

  const checkedIds = Array.from(document.querySelectorAll('.prop-chk:checked')).map(c => c.dataset.id);
  if (!checkedIds.length) { notify('No tabs selected.', 'amber'); return; }
  // Targets are record OBJECTS resolved now, before the first await: a target
  // closed and reopened from a project during the batch has the same id on a
  // NEW object and must not be written (Codex round 2, both runs).
  const targets = checkedIds.map(id => tabManager._getTab(id)).filter(t => t && !t.isStack);

  const btn = document.getElementById('propagate-run-btn');
  btn.disabled = true;
  const prog = document.getElementById('propagate-progress');
  const summary = document.getElementById('propagate-summary');
  summary.style.display = 'none';
  summary.innerHTML = '';

  // Suppress auto-snapshots during batch propagation
  _snapshotSuppressed = true;

  // Compute source amplitude scale reference (max raw intensity in ROI)
  const srcMaxInten = _arrMax(sourceTab.rawIntensity);
  // SOURCE SNAPSHOT before the first yield: the source record can change
  // between targets (an async rollback, an edit on it), and every target
  // must receive the model the user pressed the button with (Codex round 3).
  const srcPeaks = JSON.parse(JSON.stringify(sourceTab.peaks || []));
  const srcUi = { ...(sourceTab.ui || {}) };
  const srcShift = sourceTab.ccShift;
  // A model copied from a local-derived source stays a starting point on
  // every target until a successful fit supersedes it (unit A0).
  const srcProvenance = _provenanceOf(sourceTab);

  const results = [];

  for (let i = 0; i < targets.length; i++) {
    const tgt = targets[i];
    const tid = tgt.id;
    if (!_ownerLive(tgt)) continue;                 // closed (or replaced by a reload) since the batch started

    prog.textContent = `Fitting spectrum ${i + 1}/${targets.length}: ${tgt.name}…`;

    // Scale factor based on max intensity ratio
    const tgtMaxInten = _arrMax(tgt.rawIntensity);
    const scale = srcMaxInten > 0 ? tgtMaxInten / srcMaxInten : 1;

    // Deep-clone source peaks, scaled
    const clonedPeaks = srcPeaks.map(p => ({
      ...p,
      amplitude: p.linked ? p.amplitude : p.amplitude * scale,
      support: null           // a propagated model has not been fitted: nothing is established (a copied verdict could never match this tab's key anyway)
    }));

    // Copy peak nextId
    const nextId = Math.max(0, ...clonedPeaks.map(p => p.id)) + 1;

    // Propagate background + ROI settings from source (BatchPropagation is the
    // single source of truth for the merge — see static/js/batch_propagation.js).
    // ccShift is copied separately just below.
    const newUi = BatchPropagation.propagateFitUi(srcUi, tgt.ui);

    // Apply to target tab record (without switching UI) — undoable on that record
    _pushUndoFor(tgt, { endpointAvg: tgt.ui && tgt.ui.endpointAvg });
    tgt.peaks = clonedPeaks;
    tgt.nextId = nextId;
    tgt.ui = newUi;
    tgt.ccShift = srcShift;
    tgt.chargeVerified = false;
    // A propagated model has not been fitted yet: the target's previous
    // result belonged to its previous peaks (unit A0 acceptance rule).
    tgt.fitResult = null;
    tgt.modelProvenance = srcProvenance ? { ...srcProvenance, copiedFrom: sourceTab.name } : null;

    // Now activate this tab so state is populated. activateTab is a no-op
    // when the target is ALREADY active (the user switched to it during the
    // previous target's fit): then live state still holds the target's old
    // model and the post-fit sync would overwrite the propagated record —
    // load the record into live state explicitly (Codex round 3, run B).
    if (tabManager.activeId === tid) {
      state.peaks = tgt.peaks; state.nextId = tgt.nextId; state.ccShift = tgt.ccShift;
      state.fitResult = null;   // live copy of tgt.fitResult = null above (unit A0)
      tabManager._restoreUI(tgt.ui);
      renderPeakList();
      _refreshRoiAndCentreWarnings();   // this branch does not redraw: the hint must describe the target's window (Codex round 2)
    } else {
      tabManager.activateTab(tid);
    }

    // Small yield so progress message renders
    await new Promise(r => setTimeout(r, 20));
    if (_activeTab() !== tgt) {
      // The user switched tabs during the yield: fitting would read and
      // write whichever tab is active now. Stop here; targets already
      // fitted keep their results.
      notify('Batch fit stopped at ' + tgt.name + ' — the tab changed while it was running.', 'amber');
      break;
    }

    // Run local fit
    const roiSt = _roiWindowStatus();    // warn only: the fit below uses getROIData() exactly as before
    const { be, inten } = getROIData();
    const bgI = computeBackground(be, inten);
    const bgSub = inten.map((v, idx) => v - bgI[idx]);
    const outcome = runFitLocal(be, bgSub, bgI);

    // Sync result back to record
    tabManager._syncActiveToRecord();

    // Read the statistic from the fit's own return value, not from live
    // state: the active tab can change while the fit runs.
    const ok = !!(outcome && outcome.success);
    results.push({ name: tgt.name, ok, roiHint: _roiHintFor(roiSt),
                   chi: ok && Number.isFinite(outcome.chiReduced) ? outcome.chiReduced : null,
                   message: ok ? null : ((outcome && outcome.message) || 'local fit did not converge') });

    await new Promise(r => setTimeout(r, 10));
  }

  _snapshotSuppressed = false;

  // Return to source tab
  tabManager.activateTab(sourceId);

  const nOk = results.filter(r => r.ok).length;
  const nFail = results.length - nOk;
  prog.textContent = `Batch complete: ${nOk} converged as starting points, ${nFail} not fitted. Run Fit on each spectrum before reporting.`;
  const roiNote = r => r.roiHint ? ` <span class="roi-hint${r.roiHint.cls ? ' ' + r.roiHint.cls : ''}" style="display:inline">${_escHtml(r.roiHint.text)}</span>` : '';
  summary.innerHTML = results.map(r => r.ok
    ? `<div class="prop-row">${_escHtml(r.name)}: converged &mdash; &#967;&#178;<sub>r</sub> = ${r.chi != null ? r.chi.toFixed(3) : 'n/a'} (local fit: a starting point, not a reportable result)${roiNote(r)}</div>`
    : `<div class="prop-row" style="color:var(--red,#f87171)">${_escHtml(r.name)}: NOT fitted &mdash; ${_escHtml(r.message)} (model copied, no result stored)${roiNote(r)}</div>`
  ).join('') + `<div class="prop-row" style="color:var(--red,#f87171);margin-top:4px">&#9888; Charge corrections marked in red need verification</div>`;
  summary.style.display = 'block';
  btn.disabled = false;
}

// ══════════════════════════════════════════════════════════════
// FEATURE 2: NIST XPS DATABASE — CHEMICAL STATE LOOKUP
// ══════════════════════════════════════════════════════════════

// Legacy chemical-state constant removed at Stage 9 cutover — NIST-modal
// reference data is now served verbatim via the unified accessor over
// data/xps/legacy/chemical-states.json (see _accChemicalStates).

// Active compound (chemical-state) markers — GLOBAL and PERSISTENT by design:
// "mark it, close the palette, it stays". Element overlays also persist after the
// palette closes (A1); these differ only in SCOPE — compound markers are global,
// element overlays are per-tab/stack-excluded. Shape: { id, sym, state, be, ref }.
const _refCompoundMarkers = [];
let _refCompoundMarkerNextId = 1;

// The NIST Lookup modal was retired here: its chemical-state search folded into
// the drawer's unified top search (RefCore.blendedSearch) and its markers into
// the global _refCompoundMarkers store + _refRenderCompoundChips. The Lookup
// button now opens the Reference/Identify drawer.

// Draw source file path in top-left of plot area
function _drawSourceLabel(chart) {
  const tip = document.getElementById('source-path-tip');
  if (typeof tabManager === 'undefined') { if (tip) tip.style.display = 'none'; return; }
  const tab = tabManager._getTab(tabManager.activeId);
  if (!tab || !tab.sourcePath) { if (tip) tip.style.display = 'none'; return; }
  const { ctx, chartArea } = chart;
  if (!chartArea) { if (tip) tip.style.display = 'none'; return; }

  // Truncate folder segments only — never truncate the filename
  const truncFolder = s => s.length > 10 ? s.slice(0, 9) + '\u2026' : s;
  const parts = tab.sourcePath.split('/');
  const displayPath = [
    ...parts.slice(0, -1).map(truncFolder),
    parts[parts.length - 1]   // filename: never truncated
  ].join('/');

  const isLight = document.body.classList.contains('light-theme');
  ctx.save();
  ctx.font = "14px " + MONO_FONT;
  ctx.fillStyle = isLight ? '#1a1a2e' : '#ffffff';
  ctx.textAlign = 'left';
  ctx.textBaseline = 'top';
  ctx.fillText('Source: ' + displayPath, chartArea.left + 10, chartArea.top + 10);
  ctx.restore();

  // Keep the transparent hover overlay aligned over the label for the full-path tooltip
  if (tip) {
    tip.style.display = 'block';
    tip.style.left = (chartArea.left + 10) + 'px';
    tip.style.top  = (chartArea.top  + 10) + 'px';
    tip.title = tab.sourcePath;
  }
}

// Called from updatePlot() to draw NIST markers on the chart
// Amber-dashed chemical-state/compound markers. Drawn from the GLOBAL
// overlayPlugin (not gated on the panel) so they persist after the palette
// closes. Element reference overlays persist too (A1) but via their own draw
// path (xpsRefLinesPlugin) and element-coloured, dashed style — distinct styles,
// same persistent lifetime.
function _refDrawCompoundMarkers(chart) {
  if (!_refCompoundMarkers.length || !chart) return;
  const xScale = chart.scales.x;
  const yScale = chart.scales.y;
  if (!xScale || !yScale) return;

  const ctx = chart.ctx;
  const top = yScale.top;
  const bottom = yScale.bottom;
  const isLight = document.body.classList.contains('light-theme');
  const lineColor = isLight ? 'rgba(180,100,0,0.8)' : 'rgba(255,187,68,0.9)';
  const textColor = isLight ? '#7c3a00' : '#ffe08a';
  const shadowColor = isLight ? 'rgba(255,255,255,0.95)' : 'rgba(0,0,0,0.9)';

  // Collect visible markers with pixel positions
  const visible = _refCompoundMarkers
    .map(m => ({ ...m, px: xScale.getPixelForValue(m.be) }))
    .filter(m => m.px >= xScale.left && m.px <= xScale.right)
    .sort((a, b) => a.px - b.px);
  if (!visible.length) return;

  // Greedy stagger: assign vertical level so labels don't overlap (~90px wide)
  const LABEL_W = 90;
  const levels = [];
  for (const m of visible) {
    let lv = 0;
    while (levels[lv] !== undefined && m.px < levels[lv] + LABEL_W) lv++;
    levels[lv] = m.px;
    m.level = lv;
  }

  ctx.save();

  // Draw vertical dashed lines
  ctx.setLineDash([5, 4]);
  ctx.lineWidth = 1.5;
  ctx.strokeStyle = lineColor;
  for (const m of visible) {
    ctx.beginPath();
    ctx.moveTo(m.px, top);
    ctx.lineTo(m.px, bottom);
    ctx.stroke();
  }

  // Draw horizontal labels at top with text shadow for readability
  ctx.setLineDash([]);
  ctx.font = "bold 12px " + MONO_FONT;
  ctx.textAlign = 'left';
  ctx.textBaseline = 'top';
  ctx.shadowColor = shadowColor;
  ctx.shadowBlur = 4;
  ctx.fillStyle = textColor;
  for (const m of visible) {
    // Chemical state is the point of the marker — lead with it; fall back to
    // the sym/orbital label only when no state is recorded.
    const label = m.state
      ? m.state + ' ' + m.be.toFixed(1)
      : (m.sym || m.orbital || '') + ' ' + m.be.toFixed(1);
    ctx.fillText(label, m.px + 4, top + 5 + m.level * 17);
  }

  ctx.restore();
}

// ══════════════════════════════════════════════════════════════
// PERIODIC TABLE REFERENCE LINES  (data/xps via /api/xps-reference)
// ══════════════════════════════════════════════════════════════
// The Stage-9 cutover removed the legacy survey-marker and NIST-modal
// constants; all reference data now flows through the unified accessor over
// data/xps. Physics conventions (do not violate):
//   • Photoelectron markers draw at nominal_be_ev DIRECTLY in the
//     displayed corrected-BE frame — never shifted by ccShift.
//   • Auger lines store source-invariant KINETIC energy; apparent
//     BE = hν − KE − φ (vgd_parser convention). Switching the
//     reference source moves Auger markers ONLY.
//   • Line-list filtering uses the spectrum's acquisition range
//     (corrected data extent), never the current zoom; drawing
//     clips to the zoomed viewport.

// 18-column periodic-table layout. Rows 1–7 are the main grid;
// rows 9–10 are the detached f-blocks (La–Lu, Ac–Lr).
const REF_PT_LAYOUT = (() => {
  const SYM = ['H','He','Li','Be','B','C','N','O','F','Ne','Na','Mg','Al','Si',
    'P','S','Cl','Ar','K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn',
    'Ga','Ge','As','Se','Br','Kr','Rb','Sr','Y','Zr','Nb','Mo','Tc','Ru','Rh',
    'Pd','Ag','Cd','In','Sn','Sb','Te','I','Xe','Cs','Ba','La','Ce','Pr','Nd',
    'Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','Hf','Ta','W','Re',
    'Os','Ir','Pt','Au','Hg','Tl','Pb','Bi','Po','At','Rn','Fr','Ra','Ac','Th',
    'Pa','U','Np','Pu','Am','Cm','Bk','Cf','Es','Fm','Md','No','Lr','Rf','Db',
    'Sg','Bh','Hs','Mt','Ds','Rg','Cn','Nh','Fl','Mc','Lv','Ts','Og'];
  const out = [];
  let z = 1;
  const place = (col, row) => { out.push({ sym: SYM[z - 1], z, col, row }); z++; };
  place(1, 1); place(18, 1);                              // H, He
  for (const row of [2, 3]) {                             // Li–Ne, Na–Ar
    place(1, row); place(2, row);
    for (let c = 13; c <= 18; c++) place(c, row);
  }
  for (const row of [4, 5])                               // K–Kr, Rb–Xe
    for (let c = 1; c <= 18; c++) place(c, row);
  for (const [row, fRow] of [[6, 9], [7, 10]]) {          // Cs–Rn + La–Lu, Fr–Og + Ac–Lr
    place(1, row); place(2, row);
    for (let c = 3; c <= 17; c++) place(c, fRow);
tests/js/lineshape_roundtrip.test.js:50:  for (const c of [process.env.XPS_PYTHON, path.join(REPO_ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3']) {
tests/js/lineshape_roundtrip.test.js:53:  return 'python3';
tests/js/lineshape_roundtrip.test.js:55:const PYTHON = findPython();
tests/js/lineshape_roundtrip.test.js:58:  return JSON.parse(execFileSync(PYTHON, [BRIDGE, REPO_ROOT], { input: JSON.stringify(payload), encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }));
tests/js/local_lm_descent.test.js:71:  const py = fs.existsSync(path.join(REPO_ROOT, 'venv/bin/python3')) ? path.join(REPO_ROOT, 'venv/bin/python3')
tests/js/local_lm_descent.test.js:72:    : (fs.existsSync('/Users/skyefortier/xps-app/venv/bin/python3') ? '/Users/skyefortier/xps-app/venv/bin/python3' : 'python3');
tests/js/local_lm_descent.test.js:458:  const py = fs.existsSync(path.join(REPO_ROOT, 'venv/bin/python3')) ? path.join(REPO_ROOT, 'venv/bin/python3')
tests/js/local_lm_descent.test.js:459:    : (fs.existsSync('/Users/skyefortier/xps-app/venv/bin/python3') ? '/Users/skyefortier/xps-app/venv/bin/python3' : 'python3');
fitting.py:670:def _la_casaxps_true(
tests/js/lineshape_parity.test.js:63:    process.env.XPS_PYTHON,
tests/js/lineshape_parity.test.js:64:    path.join(REPO_ROOT, 'venv/bin/python3'),          // main checkout's own venv
tests/js/lineshape_parity.test.js:65:    '/Users/skyefortier/xps-app/venv/bin/python3',      // worktree -> main repo venv
tests/js/lineshape_parity.test.js:66:    'python3',
tests/js/lineshape_parity.test.js:70:      if (c === 'python3' || fs.existsSync(c)) return c;
tests/js/lineshape_parity.test.js:73:  return 'python3';
tests/js/lineshape_parity.test.js:75:const PYTHON = findPython();
tests/js/lineshape_parity.test.js:80:  const out = execFileSync(PYTHON, [BRIDGE], { input, encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 });
tests/js/lineshape_parity.test.js:329:  const out = execFileSync(PYTHON, [BRIDGE], { input, encoding: 'utf8', maxBuffer: 256 * 1024 * 1024 });
tests/test_component_required.py
tests/test_tougaard_background.py
tests/test_browser_overlay_zip_roundtrip.py
tests/test_browser_find_peaks_drag.py
tests/test_scan_batch_fit_signature.py
tests/test_coverage_exhaustion.py
tests/test_api_analyze_progress.py
tests/test_browser_endpoint_avg_default.py
tests/test_browser_palette.py
tests/test_scattered_starts.py
tests/test_xps_reference.py
tests/test_legacy_parity.py
tests/test_api_analyze.py
docs/autofit/stress-test-report.md
tests/test_browser_find_peaks_method_tooltips.py
tests/test_cutover.py
tests/test_api_analyze_coverage.py
tests/test_la_continuous_m.py
tests/test_expand_coverage.py
tests/test_browser_legacy_auger.py
tests/test_browser_reference_mode.py
tests/conftest.py
tests/test_browser_find_peaks_coverage.py
tests/test_browser_batch_roi.py
tests/test_chem_state_tier.py
tests/test_browser_identify_frame.py
tests/test_api_fit_full_window_option.py
tests/test_browser_shirley_linear_delist.py
tests/test_browser_find_peaks_tooltip_markup.py
tests/test_short_caveat.py
tests/test_browser_find_peaks_full_window.py
tests/test_shirley_linear_kept.py
tests/test_mixed_ds_lacx_e2e.py
tests/test_dsg_outside_centre.py
tests/test_browser_find_peaks_endpoint_avg.py

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 node --test tests/js/*.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
exec
/bin/zsh -lc "sed -n '670,745p' fitting.py; sed -n '8335,8525p' templates/index.html; git diff main..HEAD -- tests/js/local_lm_descent.test.js" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 0ms:
def _la_casaxps_true(
    x: np.ndarray,
    amplitude: float,
    center: float,
    fwhm: float,
    alpha: float,
    beta: float,
    m: float,
) -> np.ndarray:
    """
    True CasaXPS LA(α, β, m) lineshape.

    Built in two steps per the CasaXPS LA manual:

    1.  Asymmetric base Lorentzian. Start with a unit-amplitude Lorentzian
        of FWHM `fwhm` centered at `center`:
            L(x) = 1 / (1 + 4·((x − center)/fwhm)²)
        Apply piecewise exponents to introduce asymmetry. CasaXPS defines
        these on a kinetic-energy axis. We use a binding-energy axis, so
        the sides flip:
            LA_base(x) = L(x)^α   for x ≥ center  (high-BE side)
            LA_base(x) = L(x)^β   for x <  center  (low-BE side)
        Increasing α relative to β SUPPRESSES the high-BE tail; decreasing
        α extends it.

    2.  Gaussian convolution with a continuous-m kernel: σ_pts = m/3,
        kernel half-width max(1, ceil(3.5·σ_pts)) (±3.5σ; see the inline
        comment for why 3.5, not 3), truncation-renormalized, convolved
        with mode='same' on the uniform x grid. m < 1e-3 means no
        convolution. NOTE this deliberately deviates from the original
        integer 2m+1 design (still implemented by the frontend's
        laTrueCasaXPS_array — a tracked ~0.15%-at-m=50 parity gap, todo
        in tests/js/lineshape_parity.test.js): m flows through
        continuously so lmfit's finite-difference Jacobian in m is
        non-singular.

    With α=β=1 and m=0, this reduces exactly to amplitude × L(x) (a pure
    Lorentzian of peak height = amplitude, FWHM = `fwhm`).

    Parameters
    ----------
    fwhm  : Lorentzian FWHM in eV (must be > 0)
    alpha : high-BE-side exponent, dimensionless, default 1.0, bounds (0.1, 5.0)
    beta  : low-BE-side exponent, dimensionless, default 1.0, bounds (0.1, 5.0)
    m     : Gaussian convolution kernel width in DATA POINTS (not eV);
            0–499, used CONTINUOUSLY (no rounding — see kernel note above).
    """
    fwhm = max(float(fwhm), 1e-9)
    alpha = max(float(alpha), 1e-3)
    beta = max(float(beta), 1e-3)
    # Continuous-σ kernel: m flows through to the kernel weights as a real
    # number, so the Jacobian column for m is well-defined under lmfit's
    # finite-difference perturbation. Previously m was rounded with
    # int(round(m)), making the function locally constant in m and
    # producing a singular Hessian whenever m varied — that poisoned
    # covariance estimation for every other free param too.
    # Defensive guard preserves the prior [0, 499] cap in case a saved
    # spec or caller bypasses the lmfit bound.
    m_cont = max(0.0, min(499.0, float(m)))

    eps = x - center
    # Base unit-amplitude Lorentzian
    L = 1.0 / (1.0 + 4.0 * (eps / fwhm) ** 2)
    # Piecewise exponentiation. BE-axis: high-BE side is eps ≥ 0.
    high = eps >= 0
    base = np.where(high, np.power(L, alpha), np.power(L, beta))

    # Below ε, treat as un-convolved Lorentzian so an optimizer that lands
    # exactly at m=0 returns the bare base curve rather than degenerating.
    if m_cont < 1e-3:
        return amplitude * base

    sigma_pts = m_cont / 3.0
    # Kernel half-width: ±3.5σ captures > 99.95% of the Gaussian. Use 3.5
    # rather than 3 specifically so the kernel-length quantization step
    # `ceil(3.5σ)` doesn't coincide with integer m — that would put a
  const FTOL = 1e-6, XTOL = 1e-8, GTOL = 1e-6, SENS_MIN = 1e-12;
  // CERTIFICATE: a tentative convergence (gtol / ftol / xtol) is accepted
  // only if no feasible move of PROBE_REL (scaled) in any single free
  // parameter reduces the residual by more than FTOL of its value. If one
  // does, that point is taken and iteration continues (Codex round 3: the
  // linearised model is not a stationarity certificate; a column-norm
  // cutoff froze determined parameters).
  const PROBE_REL = 1e-3, MAX_CERTIFY = 200;
  // No exit is exempt from the certificate: a tiny absolute residual is
  // still probed relatively (Codex round 4). The certificate is a
  // single-parameter (coordinate) feasible-descent check, not a proof of a
  // local minimum along coupled directions; the LM step handles coupling
  // during optimisation.
  let converged = params.length === 0 || (chi === 0 && certify());
  let iterations = 0;
  let acceptedSteps = 0;
  let certifyRestarts = 0;

  for (let iter = 0; iter < maxIter && !converged; iter++) {
    iterations++;
    if (certifyRestarts > MAX_CERTIFY) return fail('could not certify a stationary point after ' + iterations + ' iterations.', iterations);
    const r = residuals(params);
    const n = params.length;
    // Central-difference Jacobian d r / d p, stepping inside the parameter
    // box (one-sided at a wall).
    const J = [];
    for (let j = 0; j < n; j++) {
      const { param } = paramMap[j];
      const step = H_REL * paramScale(j, params);
      const pPlus = [...params], pMinus = [...params];
      pPlus[j] = clamp(param, params[j] + step);
      pMinus[j] = clamp(param, params[j] - step);
      const span = pPlus[j] - pMinus[j];
      if (span === 0) { J.push(r.map(() => 0)); continue; }
      const rPlus = pPlus[j] === params[j] ? r : residuals(pPlus);
      const rMinus = pMinus[j] === params[j] ? r : residuals(pMinus);
      J.push(rPlus.map((v, i) => (v - rMinus[i]) / span));
    }
    const JtJ = Array.from({length: n}, () => new Array(n).fill(0));
    const Jtr = new Array(n).fill(0);
    for (let a = 0; a < n; a++) {
      for (let b = 0; b < n; b++) {
        for (let i = 0; i < r.length; i++) JtJ[a][b] += J[a][i] * J[b][i];
      }
      for (let i = 0; i < r.length; i++) Jtr[a] += J[a][i] * r[i];
    }
    if (!Jtr.every(Number.isFinite) || !JtJ.every(row => row.every(Number.isFinite))) {
      return fail('the model derivative is not finite.', iterations);
    }
    // Sensitivity: a model that does not respond to any free parameter here
    // (e.g. a peak far outside the window) cannot be optimised — that is a
    // failure, not a stationary point.
    let sens = 0;
    for (let j = 0; j < n; j++) if (!isDiscrete(j)) sens = Math.max(sens, JtJ[j][j] * paramScale(j, params) ** 2);
    if (n > 0 && sens / Math.max(chi, 1e-300) < SENS_MIN) {
      return fail('the model has no measurable sensitivity to its free parameters in this region.', iterations);
    }
    // ACTIVE SET: a parameter whose descent direction points into a wall of
    // the parameter box (or that has no sensitivity, or is discrete) is held
    // FIXED for this step. Solving the joint system with such a parameter
    // and then clipping it would leave the other components of the step
    // meaningless and let a tiny "agreed" step pass the ftol test at a
    // non-stationary point (Codex round 2). With r = data - model,
    // d(chi)/dp_j = +2 * (J_j . r), so the descent direction is -sign(J_j . r).
    const active = [];
    let gradCos = 0;
    const rNorm = Math.sqrt(chi);
    for (let j = 0; j < n; j++) {
      if (isDiscrete(j) || !(JtJ[j][j] > 0)) continue;
      if (Jtr[j] !== 0) {
        const probe = clamp(paramMap[j].param, params[j] - Math.sign(Jtr[j]) * 1e-6 * paramScale(j, params));
        if (probe === params[j]) continue;          // blocked by the box
      }
      active.push(j);
      if (rNorm > 0) gradCos = Math.max(gradCos, Math.abs(Jtr[j]) / (Math.sqrt(JtJ[j][j]) * rNorm));
    }
    // Projected gradient test (gtol) over the active set only. A failed
    // certificate has moved the point: restart the iteration so the
    // derivatives and active set are rebuilt there.
    if (gradCos < GTOL) { if (certify()) { converged = true; break; } continue; }
    // Linear model of the residual, for the predicted reduction (ftol test).
    const JtJ0 = JtJ.map(row => row.slice());

    // Marquardt damping, then the DESCENT step on the active set:
    // JtJ_aa . dp_a = -Jt.r_a, dp = 0 for held parameters.
    const m = active.length;
    const A = active.map(a => active.map(b => (a === b ? JtJ[a][a] * (1 + lambda) + 1e-300 : JtJ[a][b])));
    const rhs = active.map(a => -Jtr[a]);
    const dpA = solveLinear(A, rhs, m);
    if (!dpA.every(Number.isFinite)) return fail('the normal equations are singular.', iterations);
    const dp = new Array(n).fill(0);
    active.forEach((a, k) => { dp[a] = dpA[k]; });
    const newParams = params.map((v, i) => clamp(paramMap[i].param, v + dp[i]));
    const step = newParams.map((v, i) => v - params[i]);
    const newChi = chiSq(newParams);

    if (Number.isFinite(newChi) && newChi < chi) {
      const actred = (chi - newChi) / Math.max(chi, 1e-300);
      // predicted reduction of the linearised problem: (2 Jt.r . (-dp) - dp.JtJ.dp) / chi
      let lin = 0, quad = 0;
      for (let a = 0; a < n; a++) {
        lin += Jtr[a] * step[a];
        for (let b = 0; b < n; b++) quad += step[a] * JtJ0[a][b] * step[b];
      }
      const prered = (-2 * lin - quad) / Math.max(chi, 1e-300);
      const relStep = Math.max(0, ...step.map((d, i) => Math.abs(d) / paramScale(i, params)));
      params = newParams;
      chi = newChi;
      acceptedSteps++;
      lambda *= 0.7;
      if (chi === 0 || (prered > 0 && actred <= FTOL && prered <= FTOL && actred / prered <= 2) || relStep <= XTOL) {
        if (certify()) { converged = true; break; }
      }
    } else {
      lambda *= 3;
      if (lambda > 1e8) {
        // Even a tiny steepest-descent step no longer reduces the residual,
        // yet the projected gradient is not small: stalled, not converged.
        return fail('the optimiser stalled (no step reduces the residual) after ' + iterations + ' iterations.', iterations);
      }
    }
  }
  if (!converged) return fail('iteration limit (' + maxIter + ') reached.', iterations);

  // ── Converged: commit the working copy to the live peaks ──────────────────
  applyParams(params);
  for (const p of work) {
    const live = getPeak(p.id);
    if (!live) continue;
    Object.assign(live, p);
    // A local fit has no backend covariance; any _backendParams on the peak
    // belong to an earlier server fit (or, in Batch Fit, to the SOURCE
    // spectrum's fit) and must not travel with this result.
    delete live._backendParams;
  }

  // Degrees of freedom count the parameters this engine varies (caM is held,
  // not one of them; parameters temporarily blocked at a wall still count).
  const nVaried = params.filter((_, j) => !isDiscrete(j)).length;
  const dof = Math.max(1, be.length - nVaried);
  const chiReduced = chi / dof;                       // weighted reduced chi-square, as lmfit's redchi
  const _raw = rawResiduals(params);
  const rmse = Math.sqrt(_raw.reduce((a, v) => a + v * v, 0) / be.length);   // unweighted RMS, as the server path reports
  // "Not supported by the data": the same removal statistic the server
  // computes, from this engine's own residuals and weights (a component driven
  // to the zero floor is an outcome here too, not something to hide).
  {
    const model = evalAllPeaks(be, work);
    const verdicts = {};
    for (const wp of work) {
      if (wp.linked) continue;
      const comp = evalPeakArray(be, wp);
      const nFreeComp = paramMap.filter(d => d.id === wp.id && !isDiscrete(paramMap.indexOf(d))).length;
      verdicts[String(wp.id)] = _componentSupportCore(bgSubtracted, model, comp, _w, nFreeComp, nVaried);
    }
    _applySupportVerdicts(state.peaks, id => verdicts[String(id)] || null, _startsLiveKey());
  }

  // KNOWN LIMITATION: this engine produces no parameter uncertainties; the
  // results panel shows blank sigma for every parameter after a local fit.
  const roiRange = { min: _arrMin(be).toFixed(1), max: _arrMax(be).toFixed(1) };
  { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }   // a new result supersedes imported provenance
  state.fitResult = { chi, chiReduced, rmse, be, bgSubtracted, bgIntensity, roiRange,
                      engine: 'local', status: 'converged',
                      objective: 'poisson_weighted_chi_square', weighting: '1/sqrt(max(counts,1))', iterations,
                      reportable: false, caveat: _LOCAL_FIT_CAVEAT };
  state.fitResult.rFactor = _computeRFactor(state.fitResult);

  _applyStatDisplay(state.fitResult);
  document.getElementById('sb-msg').textContent = 'Fit complete (local)';
  _updateRFactorUI(state.fitResult.rFactor);
  _updateROIDisplay(roiRange);

  renderPeakList();
  updatePlot();
  renderResults();

  _hideFitSpinner();
  notify('Local fit converged in ' + iterations + ' iteration' + (iterations === 1 ? '' : 's') +
         '. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3) + ' (Poisson-weighted; no uncertainties). Starting point only: run Fit before reporting.', 'amber');
  _autoSnapshot();
  return { success: true, engine: 'local', iterations, acceptedSteps, chiReduced, certifyRestarts };
}

function solveLinear(A, b, n) {
  const M = A.map((row, i) => [...row, b[i]]);
  for (let col = 0; col < n; col++) {
    let maxRow = col;
    for (let row = col + 1; row < n; row++) {
      if (Math.abs(M[row][col]) > Math.abs(M[maxRow][col])) maxRow = row;
    }
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-g3dgJJjd' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-bYCyKc90' (errno=Operation not permitted)
diff --git a/tests/js/local_lm_descent.test.js b/tests/js/local_lm_descent.test.js
index 024ca96..3901fdc 100644
--- a/tests/js/local_lm_descent.test.js
+++ b/tests/js/local_lm_descent.test.js
@@ -35,7 +35,7 @@ function extractFn(name) {
 }
 
 const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
-  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
+  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', '_laKernelHalf', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
   'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
   'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
   'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
@@ -477,25 +477,78 @@ test('server parity on GL-type models: weighted local Batch Fit matches lmfit fr
   }
 });
 
-// ── W1 Codex round 1: a never-optimised parameter (integer-clamped caM) is not a degree of freedom ──
-test('reduced chi-square does not count the held caM as a varied parameter', () => {
-  const run = (fixCaM) => {
+// ── caM unit (2026-09-25): the local engine HOLDS LA's m, exactly ──
+// It used to make a free caM free and then ROUND it in its clamp, so a
+// fractional server-fitted 8.2 was silently fitted as 8 and not counted
+// as a degree of freedom. Freeing it properly failed on the curve's jumps
+// in m (Codex rounds 1–2), so it is held at its exact value.
+test('the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom', () => {
+  const be = grid(280, 283, 0.05);
+  const truth = { id: 1, name: 'la', shape: 'LACX', center: 281.5, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: 8.66, glMix: 50, asymmetry: 0 };
+  const fitFrom = (fixCaM) => {
     const env = makeEnv();
-    const be = grid(280, 282, 0.1);
-    const truth = { id: 1, name: 'la', shape: 'LACX', center: 281.0, fwhm: 1.0, amplitude: 50, caAlpha: 1.2, caBeta: 1.5, caM: 6, glMix: 50, asymmetry: 0 };
     env.state.peaks = [{ ...truth }];
-    const data = env.evalAllPeaks(be, env.state.peaks).map((v, i) => v * (1 + 0.05 * Math.sin(3 * i)) + 20);
-    env.state.peaks = [{ ...truth, amplitude: 40, fixCenter: true, fixFwhm: true, fixCaAlpha: true, fixCaBeta: true, fixCaM }];
-    const out = env.runFitLocal(be, data.map(v => v - 20), new Array(be.length).fill(20));
+    const data = env.evalAllPeaks(be, env.state.peaks);
+    env.state.peaks = [{ ...truth, caM: 5.37, amplitude: 4000, fixCenter: true, fixFwhm: true, fixCaAlpha: true, fixCaBeta: true, fixCaM }];
+    const out = env.runFitLocal(be, data, new Array(be.length).fill(0));
     assert.equal(out.success, true, JSON.stringify(out));
-    return { chi: env.state.fitResult.chi, chiReduced: out.chiReduced, amp: env.state.peaks[0].amplitude };
+    return { out, p: env.state.peaks[0], fr: env.state.fitResult };
   };
-  const a = run(true), b = run(false);
-  assert.ok(Math.abs(a.amp - b.amp) < 1e-9 && Math.abs(a.chi - b.chi) < 1e-9, 'identical fit either way');
-  assert.ok(Math.abs(a.chiReduced - b.chiReduced) < 1e-12, `same fit, same reduced chi-square: ${a.chiReduced} vs ${b.chiReduced}`);
+  const free = fitFrom(false), held = fitFrom(true);
+  assert.equal(free.p.caM, 5.37, 'held exactly — not rounded to 5, not moved');
+  assert.equal(held.p.caM, 5.37);
+  assert.ok(Math.abs(free.p.amplitude - held.p.amplitude) < 1e-9, 'the same fit either way');
+  assert.ok(Math.abs(free.out.chiReduced - held.out.chiReduced) < 1e-12, 'm is not a degree of freedom either way');
 });
 
 
+// caM unit, Codex rounds 1–2: LA's curve JUMPS where the kernel half-width
+// max(1, ceil(3.5 m/3)) changes (m = 6k/7). With m made free, these fits
+// stalled (round 1) or failed next to the no-convolution threshold (round
+// 2). m is held, so each must converge whether or not it is locked.
+for (const c of [
+  { label: 'run A: 201 pts at 0.03 eV, m 48 (a transition), noisy', be: grid(280, 286, 0.03),
+    truth: { center: 283.013, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: 48 }, noise: i => 5 * Math.sin(1.77 * i),
+    start: { amplitude: 4900 }, lock: { fixCenter: true, fixFwhm: true, fixCaAlpha: true, fixCaBeta: true } },
+  { label: 'run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free', be: grid(280, 283, 0.05),
+    truth: { center: 281.538, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: 18 / 7 - 0.001 }, noise: i => 0.1 * Math.sin(3 * i),
+    start: { amplitude: 4000, caM: 2.6 }, lock: {} },
+]) {
+  test(`an LA fit with m free converges across a kernel-width transition — ${c.label}`, () => {
+    const run = (fixCaM) => {
+      const env = makeEnv();
+      const truth = { id: 1, name: 'la', shape: 'LACX', glMix: 50, asymmetry: 0, ...c.truth };
+      env.state.peaks = [{ ...truth }];
+      const data = env.evalAllPeaks(c.be, env.state.peaks).map((v, i) => v + c.noise(i));
+      env.state.peaks = [{ ...truth, ...c.start, ...c.lock, fixCaM }];
+      const out = env.runFitLocal(c.be, data, new Array(c.be.length).fill(0));
+      return { out, chi: env.state.fitResult && env.state.fitResult.chi };
+    };
+    const free = run(false), held = run(true);
+    assert.equal(held.out.success, true, 'held: ' + JSON.stringify(held.out));
+    assert.equal(free.out.success, true, 'free: ' + JSON.stringify(free.out));
+    assert.ok(Math.abs(free.chi - held.chi) <= 1e-12 * Math.max(1, held.chi), `an unlocked m is held: the same fit either way (${free.chi} vs ${held.chi})`);
+  });
+}
+
+// Codex round 2's two reproducers: an exact-transition start (m = 18/7)
+// with amplitude and m free, and noiseless m = 0 data started at m = 0.001.
+for (const c of [
+  { label: 'exact transition m = 18/7, 61 pts at 0.03 eV', be: grid(280, 281.8, 0.03), truth: { center: 280.913, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: 18 / 7 }, noise: i => 0.1 * Math.sin(3 * i), start: {}, lock: { fixCenter: true, fixFwhm: true, fixCaAlpha: true, fixCaBeta: true } },
+  { label: 'm = 0 data, start m = 0.001', be: grid(280, 283, 0.05), truth: { center: 281.513, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: 0 }, noise: () => 0, start: { caM: 0.001, amplitude: 4500 }, lock: { fixCenter: true, fixFwhm: true, fixCaAlpha: true, fixCaBeta: true } },
+]) {
+  test(`round-2 reproducer converges with m unlocked (m is held) — ${c.label}`, () => {
+    const env = makeEnv();
+    const truth = { id: 1, name: 'la', shape: 'LACX', glMix: 50, asymmetry: 0, ...c.truth };
+    env.state.peaks = [{ ...truth }];
+    const data = env.evalAllPeaks(c.be, env.state.peaks).map((v, i) => v + c.noise(i));
+    env.state.peaks = [{ ...truth, ...c.start, ...c.lock, fixCaM: false }];
+    const out = env.runFitLocal(c.be, data, new Array(c.be.length).fill(0));
+    assert.equal(out.success, true, JSON.stringify(out));
+    assert.equal(env.state.peaks[0].caM, c.start.caM ?? c.truth.caM, 'm held exactly');
+  });
+}
+
 test('recovery from an amplitude of exactly zero (the new floor is not a trap)', () => {
   const env = makeEnv();
   const be = grid(280, 290, 0.05);

codex
The local parameter map excludes caM, and linked children copy the parent’s exact value. Batch Fit also preserves it while scaling amplitudes. I found a stale comment that still claims the withdrawn derivative uses `_laKernelHalf`; I’m checking for executable remnants and mismatches in the recorded evidence.

exec
/bin/zsh -lc "sed -n '1,120p' tests/js/local_lm_descent.test.js; sed -n '1,145p' scripts/local_server_gap.js; git diff main..HEAD -- tests/js/lineshape_parity.test.js tests/js/lineshape_roundtrip.test.js; sed -n '745,782p' fitting.py; cat docs/findings/cam/local_server_gap_after_cam.log; cat docs/findings/cam/transition_sweep.json" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 0ms:
// Local Levenberg–Marquardt: it must DESCEND and it must never present a
// non-converged attempt as a result (unit A0, 2026-09-15).
//
// Background: from the initial commit (f20d71b) until this unit, runFitLocal
// solved JᵀJ·dp = +Jᵀr with r = data − model, so every step was an ascent
// step, no step was ever accepted, and after 24 rejections λ passed 1e8 and
// the loop exited with the STARTING parameters, announced as "Fit complete
// (local LM)". Every Batch Fit called that path. The empirical proof is in
// docs/superpowers/plans/2026-09-15-a01-local-lm-proof.md; this file is
// that proof turned into a regression test on the SHIPPED functions.
//
// Everything under test is extracted verbatim from templates/index.html by
// function name (brace-matched) — the same functions the browser runs.

const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

const REPO_ROOT = path.join(__dirname, '../..');
const html = fs.readFileSync(path.join(REPO_ROOT, 'templates/index.html'), 'utf8');
const lines = html.split('\n');

function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name.replace(/\$/g, '\\$') + '\\(');
  const start = lines.findIndex(l => re.test(l));
  assert.ok(start >= 0, `function ${name} not found in templates/index.html`);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail(`unbalanced braces extracting ${name}`);
}

const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', '_laKernelHalf', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
  'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
  'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
  'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
  '_computeRFactor', '_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel', '_governingProvenance', '_localFitCaveat', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay', '_updateLocalModelBanner',
  '_componentSupportCore', '_supportRootOf', '_applySupportVerdicts'];
const CAVEAT_CONST = (html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg) || []).join('\n');

// One isolated environment per test: a fresh `state`, a stub DOM, and the
// extracted functions bound to them.
function makeEnv() {
  const dom = {};
  const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, setAttribute() {}, removeAttribute() {},
    classList: { add() {}, remove() {}, contains: () => false } });
  const document = { getElementById: el, querySelectorAll: () => [] };
  const state = { peaks: [], fitResult: null, rawBE: [], rawIntensity: [], ccShift: 0 };
  const calls = { notify: [] };
  const notify = (msg, kind) => calls.notify.push({ msg, kind });
  const noop = () => {};
  const src = CAVEAT_CONST + '\nconst _SUPPORT_MIN_F = 10; const _startsLiveKey = () => "KEY";\n' + NAMES.map(extractFn).join('\n\n');
  const factory = new Function('document', 'state', 'notify', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_activeTab', '_escHtml', '_historyPreview', 'tabManager', '_updateRFactorUI', '_updateROIDisplay',
    'renderPeakList', 'updatePlot', 'renderResults', '_hideFitSpinner', '_autoSnapshot', 'manualAnchorBackground',
    src + '\nreturn { runFitLocal, computeBackgroundCore, evalAllPeaks, evalPeakArray, gaussian };');
  const fns = factory(document, state, notify, '', '', () => null, x => String(x), null, null, noop, noop, noop, noop, noop, noop, noop,
    be => new Array(be.length).fill(0));
  return { ...fns, state, dom, calls };
}

// ── Committed lab project, replayed exactly as runPropagation does ──────────
const PROJECT = path.join(REPO_ROOT, 'docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip');
const BatchPropagation = require(path.join(REPO_ROOT, 'static/js/batch_propagation.js'));

function loadProjectTabs() {
  const py = fs.existsSync(path.join(REPO_ROOT, 'venv/bin/python3')) ? path.join(REPO_ROOT, 'venv/bin/python3')
    : (fs.existsSync('/Users/skyefortier/xps-app/venv/bin/python3') ? '/Users/skyefortier/xps-app/venv/bin/python3' : 'python3');
  const script = 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; ' +
    'print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))';
  return JSON.parse(execFileSync(py, ['-c', script, REPO_ROOT, PROJECT], { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }));
}

function batchTarget(env, tabs, sourceName, targetName) {
  const src = tabs.find(t => t.name === sourceName), tgt = tabs.find(t => t.name === targetName);
  assert.ok(src && tgt, 'source/target tabs present in committed project');
  const scale = Math.max(...tgt.rawIntensity) / Math.max(...src.rawIntensity);
  const cloned = JSON.parse(JSON.stringify(src.peaks)).map(p => ({ ...p, amplitude: p.linked ? p.amplitude : p.amplitude * scale }));
  const ui = BatchPropagation.propagateFitUi({ ...src.ui }, { ...tgt.ui });
  const roiMin = parseFloat(ui.roiMin), roiMax = parseFloat(ui.roiMax);
  const be = [], inten = [];
  tgt.rawBE.forEach((b, i) => { const c = b - (src.ccShift || 0); if (c >= roiMin && c <= roiMax) { be.push(c); inten.push(tgt.rawIntensity[i]); } });
  const bg = env.computeBackgroundCore(be, inten, ui);
  const bgSub = inten.map((v, i) => v - bg[i]);
  env.state.peaks = cloned;
  env.state.fitResult = null;
  return { be, bgSub, bg, initial: JSON.parse(JSON.stringify(cloned)) };
}

// The objective the local engine minimises since unit W1: the Poisson-weighted
// sum of squares, w = 1/sqrt(max(raw counts, 1)), raw = bgSub + bg.
function residualSS(env, be, bgSub, bg) {
  const m = env.evalAllPeaks(be, env.state.peaks);
  return be.reduce((s, _, i) => { const raw = bgSub[i] + (bg ? bg[i] : 0); return s + (bgSub[i] - m[i]) ** 2 / Math.max(raw, 1); }, 0);
}

test('A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters', () => {
  const tabs = loadProjectTabs();
  for (const target of ['C1s Scan_0', 'C1s Scan_4', 'C1s Scan_8']) {
    const env = makeEnv();
    const { be, bgSub, bg, initial } = batchTarget(env, tabs, 'C1s Scan', target);
    const chi0 = residualSS(env, be, bgSub, bg);
    const out = env.runFitLocal(be, bgSub, bg);
    assert.ok(out && out.success === true, `${target}: runFitLocal must report success, got ${JSON.stringify(out)}`);
    const chi1 = residualSS(env, be, bgSub, bg);
    assert.ok(chi1 < 0.5 * chi0, `${target}: residual must drop substantially (before ${chi0.toExponential(3)}, after ${chi1.toExponential(3)})`);
    const moved = env.state.peaks.some((p, i) => Math.abs(p.center - initial[i].center) > 1e-3 || Math.abs(p.fwhm / initial[i].fwhm - 1) > 1e-3);
    assert.ok(moved, `${target}: at least one free centre/width must move — the shipped code returned the starting model on 18/18 targets`);
    assert.ok(env.state.fitResult && env.state.fitResult.status === 'converged', 'a converged local fit records status: converged');
  }
});

test('A01 replay: the linked U 4f pair also descends', () => {
  const tabs = loadProjectTabs();
  const env = makeEnv();
  const { be, bgSub, bg } = batchTarget(env, tabs, 'U4f Scan', 'U4f Scan_3');
#!/usr/bin/env node
// Local engine vs server from the SAME scaled start on the committed
// UCl4-graphite project's Batch Fit targets (unit W1's methodology,
// 2026-09-18; re-run for A03, 2026-09-22 — the test of whether Batch Fit's
// "starting point" label can retire). Every C1s Scan_N and U4f Scan_N tab is
// a target; the source is the scan the student fitted ('C1s Scan' / 'U4f
// Scan'); the start is the source's model with amplitudes scaled to the
// target's maximum (what runPropagation does); both engines fit that start
// on the same background (the page's computeBackgroundCore; the server
// recomputes its own from the same settings). Differences are evaluated with
// the PAGE's semantics — the server's parameters written onto a copy of the
// start with _applyBackendParams, areas as _peakArea (evalPeakArray over the
// ROI grid × step) — so the comparison is about parameters, not about which
// side integrated. A third arm (Codex round 1: "movement in m alone does not
// establish that the residual is the local clamp") fits the server with every
// LA m HELD at the value the local engine effectively uses — its exact
// start since the caM unit (2026-09-25; before it, the start rounded) —
// the one thing the local engine cannot move: if that arm agrees with the local engine where the
// free-m arm did not, the attribution is established by a controlled
// comparison, not inferred. Usage: node scripts/local_server_gap.js [out.json]
const fs = require('fs'); const path = require('path'); const { execFileSync } = require('child_process');
const ROOT = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'templates/index.html'), 'utf8'); const lines = html.split('\n');
function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name + '\\('); const start = lines.findIndex(l => re.test(l));
  if (start < 0) throw new Error('missing ' + name);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) { for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; } if (seen && depth === 0) return lines.slice(start, i + 1).join('\n'); }
  throw new Error('unbalanced ' + name);
}
const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', '_laKernelHalf', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
  'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
  'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
  'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
  '_computeRFactor', '_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel', '_governingProvenance', '_localFitCaveat', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay', '_updateLocalModelBanner',
  '_componentSupportCore', '_supportRootOf', '_applySupportVerdicts', '_applyBackendParams'];
const CAVEAT_CONST = (html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg) || []).join('\n');
function makeEnv() {
  const dom = {}; const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, setAttribute() {}, removeAttribute() {}, classList: { add() {}, remove() {}, contains: () => false } });
  const document = { getElementById: el, querySelectorAll: () => [] };
  const state = { peaks: [], fitResult: null, rawBE: [], rawIntensity: [], ccShift: 0 }; const noop = () => {};
  const src = CAVEAT_CONST + '\nconst _SUPPORT_MIN_F = 10; const _startsLiveKey = () => "KEY";\n' + NAMES.map(extractFn).join('\n\n');
  const f = new Function('document', 'state', 'notify', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_activeTab', '_escHtml', '_historyPreview', 'tabManager', '_updateRFactorUI', '_updateROIDisplay', 'renderPeakList', 'updatePlot', 'renderResults', '_hideFitSpinner', '_autoSnapshot', 'manualAnchorBackground',
    src + '\nreturn { runFitLocal, computeBackgroundCore, evalAllPeaks, evalPeakArray, _applyBackendParams };');
  return { ...f(document, state, noop, '', '', () => null, x => String(x), null, null, noop, noop, noop, noop, noop, noop, noop, be => new Array(be.length).fill(0)), state };
}
const PY = [path.join(ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3', 'python3'].find(p => p === 'python3' || fs.existsSync(p));
const PROJECT = path.join(ROOT, 'docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip');
const BatchPropagation = require(path.join(ROOT, 'static/js/batch_propagation.js'));
const tabs = JSON.parse(execFileSync(PY, ['-c', 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))', ROOT, PROJECT], { encoding: 'utf8', maxBuffer: 1 << 26 }));
function target(env, sourceName, targetName) {
  const src = tabs.find(t => t.name === sourceName), tgt = tabs.find(t => t.name === targetName);
  const scale = Math.max(...tgt.rawIntensity) / Math.max(...src.rawIntensity);
  const cloned = JSON.parse(JSON.stringify(src.peaks)).map(p => ({ ...p, amplitude: p.linked ? p.amplitude : p.amplitude * scale }));
  const ui = BatchPropagation.propagateFitUi({ ...src.ui }, { ...tgt.ui });
  const roiMin = parseFloat(ui.roiMin), roiMax = parseFloat(ui.roiMax);
  const be = [], inten = [];
  tgt.rawBE.forEach((b, i) => { const c = b - (src.ccShift || 0); if (c >= roiMin && c <= roiMax) { be.push(c); inten.push(tgt.rawIntensity[i]); } });
  const bg = env.computeBackgroundCore(be, inten, ui);
  return { be, inten, bg, bgSub: inten.map((v, i) => v - bg[i]), ui, start: cloned };
}
const area = (env, be, p) => { const step = be.length > 1 ? Math.abs(be[1] - be[0]) : 1; return env.evalPeakArray(be, p).reduce((s, y) => s + y, 0) * step; };
const out = { generated: new Date().toISOString(), regions: {} };
for (const [region, sourceName] of [['C1s', 'C1s Scan'], ['U4f', 'U4f Scan']]) {
  const names = tabs.filter(t => new RegExp('^' + sourceName.replace(' ', ' ') + '_\\d+$').test(t.name)).map(t => t.name);
  out.regions[region] = [];
  for (const name of names) {
    const env = makeEnv(); const T = target(env, sourceName, name);
    env.state.peaks = JSON.parse(JSON.stringify(T.start)); env.state.fitResult = null;
    const loc = env.runFitLocal(T.be, T.bgSub, T.bg);
    const localPeaks = JSON.parse(JSON.stringify(env.state.peaks));
    const serverFit = startPeaks => {
      const r = JSON.parse(execFileSync(PY, [path.join(ROOT, 'tests/js/local_lm_server_parity_backend.py'), ROOT], { input: JSON.stringify({ be: T.be, inten: T.inten, peaks: startPeaks, ui: T.ui }), encoding: 'utf8', maxBuffer: 1 << 26 }));
      const peaks = JSON.parse(JSON.stringify(startPeaks));
      r.peaks.forEach((pp, i) => { const par = {}; for (const [k, v] of Object.entries(pp)) par[k] = { value: v }; env._applyBackendParams(peaks[i], par); });
      return { r, peaks };
    };
    const { r: srv, peaks: serverPeaks } = serverFit(T.start);
    // held at the value the local engine holds: its exact start since the caM unit (it rounded it before)
    const heldStart = T.start.map(p => p.shape === 'LACX' ? { ...p, fixCaM: true } : p);
    const { r: srvHeld, peaks: serverHeldPeaks } = serverFit(heldStart);
    // linked peaks: the local engine syncs them; the server returns resolved values for them too (applied above)
    const aL = localPeaks.map(p => area(env, T.be, p)), aS = serverPeaks.map(p => area(env, T.be, p)), aH = serverHeldPeaks.map(p => area(env, T.be, p));
    const tL = aL.reduce((s, v) => s + v, 0), tS = aS.reduce((s, v) => s + v, 0), tH = aH.reduce((s, v) => s + v, 0);
    const comps = localPeaks.map((p, i) => ({ name: p.name, shape: p.shape, linked: !!p.linked,
      dCenter_meV: 1000 * (p.center - serverPeaks[i].center), dFwhm_pct: 100 * (p.fwhm / serverPeaks[i].fwhm - 1),
      dArea_pct: aS[i] ? 100 * (aL[i] / aS[i] - 1) : null, dFrac_pp: 100 * (aL[i] / tL - aS[i] / tS),
      // the held-m arm: local vs server with every LA m held at its start
      held_dCenter_meV: 1000 * (p.center - serverHeldPeaks[i].center), held_dFwhm_pct: 100 * (p.fwhm / serverHeldPeaks[i].fwhm - 1),
      held_dArea_pct: aH[i] ? 100 * (aL[i] / aH[i] - 1) : null, held_dFrac_pp: 100 * (aL[i] / tL - aH[i] / tH),
      local: { center: p.center, fwhm: p.fwhm, amplitude: p.amplitude, area: aL[i] }, server: { center: serverPeaks[i].center, fwhm: serverPeaks[i].fwhm, amplitude: serverPeaks[i].amplitude, area: aS[i], glMix: serverPeaks[i].glMix, caM: serverPeaks[i].caM },
      server_held_m: { center: serverHeldPeaks[i].center, fwhm: serverHeldPeaks[i].fwhm, amplitude: serverHeldPeaks[i].amplitude, area: aH[i], caM: serverHeldPeaks[i].caM } }));
    const mx = f => Math.max(...comps.map(c => Math.abs(c[f]) || 0));
    out.regions[region].push({ target: name, local_success: loc.success, local_chi2r: env.state.fitResult && env.state.fitResult.chiReduced, server_success: srv.success, server_chi2r: srv.chi2r,
      server_held_m_success: srvHeld.success, server_held_m_chi2r: srvHeld.chi2r,
      max_dCenter_meV: mx('dCenter_meV'), max_dFwhm_pct: mx('dFwhm_pct'), max_dArea_pct: mx('dArea_pct'), max_dFrac_pp: mx('dFrac_pp'),
      held_max_dCenter_meV: mx('held_dCenter_meV'), held_max_dFwhm_pct: mx('held_dFwhm_pct'), held_max_dArea_pct: mx('held_dArea_pct'), held_max_dFrac_pp: mx('held_dFrac_pp'), comps });
    console.error(region, name, 'local', loc.success, (env.state.fitResult || {}).chiReduced && env.state.fitResult.chiReduced.toFixed(3), 'server', srv.success, srv.chi2r.toFixed(3), 'max Δcentre', mx('dCenter_meV').toFixed(1), 'meV, ΔFWHM', mx('dFwhm_pct').toFixed(2), '%, Δarea', mx('dArea_pct').toFixed(2), '%, Δfrac', mx('dFrac_pp').toFixed(2), 'pp',
      '| m held: server', srvHeld.chi2r.toFixed(3), 'Δcentre', mx('held_dCenter_meV').toFixed(1), 'meV, ΔFWHM', mx('held_dFwhm_pct').toFixed(2), '%, Δarea', mx('held_dArea_pct').toFixed(2), '%, Δfrac', mx('held_dFrac_pp').toFixed(2), 'pp');
  }
}
fs.writeFileSync(process.argv[2] || path.join(ROOT, 'docs/findings/a03/local_server_gap.json'), JSON.stringify(out, null, 1));
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-UYC4RTMl' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-tJ0zv4yj' (errno=Operation not permitted)
diff --git a/tests/js/lineshape_parity.test.js b/tests/js/lineshape_parity.test.js
index 9e7b849..98e23b5 100644
--- a/tests/js/lineshape_parity.test.js
+++ b/tests/js/lineshape_parity.test.js
@@ -168,7 +168,7 @@ for (const shape of ['Gaussian', 'Lorentzian', 'GL', 'Voigt', 'DS', 'asym-GL'])
 //   the fitted box, every grid step, orientation and off-grid centre tested
 //   below).
 //
-test('(A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization)', { todo: 'unit 2 fast-follow: LACX Gaussian-conv kernel mismatch vs backend, grows with m (~0.15% at m=50, measured 2026-08-30)' }, () => {
+test('(A) frontend vs backend parity: LACX (m>0) (FIXED 2026-09-25, caM unit: continuous-m kernel mirrored)', () => {
   const p = basePeak('LACX');
   const x = grid(p.center);
   const jsY = evalPeakArray(x, p);
@@ -347,10 +347,10 @@ const SWEEP = {
   // the full β/m box the optimiser can reach, incl. the corner that made the
   // old quadrature 1e52 × amplitude (β 2, m 0.05) and the delta threshold
   'DSG_LA (m > 0)': { laAlpha: [0, 0.25, 0.49], laBeta: [0.05, 0.7, 2], laM: [0.001, 0.05, 0.4, 2, 4] },
+  // continuous m (caM unit, 2026-09-25): fractional values, the 1e-3 threshold, and the 499 ceiling
+  'LACX (m > 0)':   { caAlpha: [0.1, 1, 5], caBeta: [0.1, 1, 5], caM: [0.001, 0.5, 1, 5, 8.66, 50, 123.4, 499], fwhm: FWHM_RANGE },
 };
-const SWEEP_KNOWN_GAP = {
-  'LACX (m > 0)':   { caAlpha: [0.1, 1, 5], caBeta: [0.1, 1, 5], caM: [1, 5, 50, 499], fwhm: FWHM_RANGE },
-};
+const SWEEP_KNOWN_GAP = {};
 function sweepShape(label) { return label.split(' ')[0]; }
 // The backend parameters of the sweep come from the PAGE's request builder,
 // not from a mapping of this file's own (Codex round 1: a mapping written
@@ -480,3 +480,27 @@ for (const laM of [0.001, 0.002, 0.02, 0.05]) {
     else assert.ok(serverMax > 0.9, `m = ${laM}: a real curve`);
   });
 }
+
+// ── (D‴) LA convergence beyond the base grid (caM unit, 2026-09-25) ──────────
+// The kernel is built in DATA POINTS, so the grid decides it: steps, a
+// descending grid, an off-grid centre, and grids SHORTER than the kernel
+// (np.convolve 'same' then the server's trim — the branch the old integer
+// kernel never exercised).
+const LA_BOX = { caAlpha: [0.1, 1.4, 5], caBeta: [0.1, 0.8, 5], caM: [0.001, 2.5, 8.66, 50, 499] };
+const LA_GRIDS = [
+  { label: 'step 0.1 eV, 120 pts', step: 0.1, n: 120 },
+  { label: 'step 0.02 eV, 500 pts', step: 0.02, n: 500 },
+  { label: 'step 0.05 eV, descending', step: 0.05, n: 200, descending: true },
+  { label: 'step 0.05 eV, centre 0.013 eV off-grid', step: 0.05, n: 200, offset: 0.013 },
+  { label: '9 points (kernel longer than the grid for m ≥ 3)', step: 0.1, n: 9 },
+  { label: '2 points', step: 0.1, n: 2 },
+];
+for (const g of LA_GRIDS) {
+  test(`(D‴) LA continuous-m convolution matches the server on another grid: ${g.label}`, () => {
+    const cases = combos(LA_BOX).map(c => ({ c, p: { ...basePeak('LACX'), ...c } }));
+    const specs = cases.map(k => { const b = backendParamsFromRequest(k.p); return { ...b, x: gridOf(k.p.center, g.step, g.n, g) }; });
+    const beYs = backendEvalMany(specs);
+    const worst = cases.map((k, i) => ({ c: k.c, rel: maxRelDiff(evalPeakArray(specs[i].x, k.p), beYs[i], k.p.amplitude) })).sort((a, b) => b.rel - a.rel);
+    assert.ok(worst[0].rel < TIGHT_TOL, `${g.label}: ${worst.filter(r => r.rel >= TIGHT_TOL).length} of ${worst.length} diverge; worst ${(worst[0].rel * 100).toExponential(3)} % of amplitude at ${JSON.stringify(worst[0].c)}`);
+  });
+}
diff --git a/tests/js/lineshape_roundtrip.test.js b/tests/js/lineshape_roundtrip.test.js
index 4103c52..4204428 100644
--- a/tests/js/lineshape_roundtrip.test.js
+++ b/tests/js/lineshape_roundtrip.test.js
@@ -15,10 +15,10 @@
 // page then DRAWS (evalPeakArray on the fitted grid) to be the curve the
 // server FITTED (individual_peaks[].y).
 //
-// One shape carries a known drawn-vs-fitted gap and is marked todo with the
-// unit that owns it: LACX (the page sends m free and draws it ROUNDED — the
-// caM clamp unit). DSG_LA was the other until 2026-09-22 (the page's
-// quadrature; now dsgConvolved_array mirrors the server).
+// No shape carries a known drawn-vs-fitted gap any more. DSG_LA did until
+// 2026-09-22 (the page's quadrature; now dsgConvolved_array mirrors the
+// server) and LACX until 2026-09-25 (the page drew m rounded to an integer
+// kernel; now laTrueCasaXPS_array mirrors the server's continuous-m one).
 const { test } = require('node:test');
 const assert = require('node:assert');
 const { execFileSync } = require('node:child_process');
@@ -41,7 +41,7 @@ function extractFn(name) {
   assert.fail(`unbalanced braces extracting ${name}`);
 }
 const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
-  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
+  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', '_laKernelHalf', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
   'evalPeakArray', 'getPeak', 'peakToBackendSpec', '_applyBackendParams'];
 const state = { peaks: [] };
 const env = new Function('state', NAMES.map(extractFn).join('\n\n') + '\nreturn { evalPeakArray, peakToBackendSpec, _applyBackendParams };')(state);
@@ -91,9 +91,7 @@ const CASES = {
   'LACX':       { truth: { shape: 'LACX', caAlpha: 1.6, caBeta: 0.7, caM: 20 }, start: { caAlpha: 1.0, caBeta: 1.0, caM: 30 } },
 };
 const TIGHT_TOL = 1e-6;      // of amplitude; both curves are the same closed form on the same grid
-const KNOWN_GAP = {
-  'LACX':   'LACX: the page sends m FREE and draws it rounded to an integer kernel (laTrueCasaXPS_array) — the caM clamp unit',
-};
+const KNOWN_GAP = {};   // LACX was the last (the page drew m rounded to an integer kernel) — closed by the caM unit, 2026-09-25
 
 function roundTrip(shape, { truth, start, extraPeaks = [] }) {
   const truthPeaks = [fullPeak(truth), ...extraPeaks.map(e => fullPeak(e.truth))];
@@ -193,7 +191,8 @@ const LOCKED_AT_BOUNDS = [
   // comparison sits under the caM evaluator gap marked todo above (curve: false)
   { label: 'DS+G m 0.05 locked', truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 0.5, laM: 0.05, fixLaM: true }, held: { m_gauss: 0.05 } },
   { label: 'DS+G m 4 locked',    truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 0.5, laM: 4, fixLaM: true }, held: { m_gauss: 4 } },
-  { label: 'LA m 499 locked (request and hold only)',    truth: { shape: 'LACX', caAlpha: 1, caBeta: 1, caM: 499, fixCaM: true }, held: { m: 499 }, curve: false },
+  { label: 'LA m 499 locked',    truth: { shape: 'LACX', caAlpha: 1, caBeta: 1, caM: 499, fixCaM: true }, held: { m: 499 } },
+  { label: 'LA m 8.66 locked (a fractional m, as a fit returns it)', truth: { shape: 'LACX', caAlpha: 1.3, caBeta: 0.9, caM: 8.66, fixCaM: true }, held: { m: 8.66 } },
 ];
 for (const c of LOCKED_AT_BOUNDS) {
   test(`locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — ${c.label}`, () => {
    # `ceil(3.5σ)` doesn't coincide with integer m — that would put a
    # discrete jump in the output exactly at integer m and re-break
    # backwards compat with previously-saved (integer-m) fits. With 3.5
    # the next jump from m=N is at m = 6(N+1)/7 ≠ integer.
    half = max(1, int(np.ceil(3.5 * sigma_pts)))
    k = np.arange(-half, half + 1, dtype=float)
    kern = np.exp(-(k ** 2) / (2.0 * sigma_pts ** 2))
    kern = kern / kern.sum()

    convolved = np.convolve(base, kern, mode='same')
    # np.convolve mode='same' returns max(len(base), len(kern)) — not
    # len(base). When the input grid is shorter than the kernel, trim
    # back to len(base) so the function's len(output) == len(x) contract
    # holds. lmfit's composite-fit residual path will broadcast the
    # per-peak arrays against the data grid, so a kernel-length return
    # surfaces as a cryptic shape mismatch downstream.
    if len(convolved) > len(base):
        excess = len(convolved) - len(base)
        start = excess // 2
        convolved = convolved[start:start + len(base)]

    peak_idx = int(np.argmin(np.abs(eps)))
    peak_val = convolved[peak_idx]
    if peak_val <= 0:
        peak_val = float(np.max(convolved))
    if peak_val <= 0:
        return np.zeros_like(x)
    return amplitude * convolved / peak_val


# ─────────────────────────────────────────────────────────────────────────────
# lmfit Model factory
# ─────────────────────────────────────────────────────────────────────────────

_SHAPE_FUNCS = {
    "gaussian": _gaussian,
    "lorentzian": _lorentzian,
    "pseudo_voigt_gl": _pseudo_voigt_gl,
C1s C1s Scan_0 local true 4.353 server true 4.357 max Δcentre 3.8 meV, ΔFWHM 0.29 %, Δarea 0.42 %, Δfrac 0.04 pp | m held: server 4.357 Δcentre 3.8 meV, ΔFWHM 0.29 %, Δarea 0.42 %, Δfrac 0.04 pp
C1s C1s Scan_1 local true 13.074 server true 13.066 max Δcentre 2.6 meV, ΔFWHM 0.50 %, Δarea 1.40 %, Δfrac 0.32 pp | m held: server 13.066 Δcentre 2.6 meV, ΔFWHM 0.50 %, Δarea 1.40 %, Δfrac 0.32 pp
C1s C1s Scan_2 local true 4.084 server true 4.087 max Δcentre 3.5 meV, ΔFWHM 0.07 %, Δarea 0.37 %, Δfrac 0.05 pp | m held: server 4.087 Δcentre 3.5 meV, ΔFWHM 0.07 %, Δarea 0.37 %, Δfrac 0.05 pp
C1s C1s Scan_3 local true 4.425 server true 4.432 max Δcentre 1.6 meV, ΔFWHM 0.06 %, Δarea 0.13 %, Δfrac 0.02 pp | m held: server 4.432 Δcentre 1.6 meV, ΔFWHM 0.06 %, Δarea 0.13 %, Δfrac 0.02 pp
C1s C1s Scan_4 local true 18.218 server true 19.056 max Δcentre 41.9 meV, ΔFWHM 8.97 %, Δarea 99.85 %, Δfrac 15.07 pp | m held: server 19.056 Δcentre 41.9 meV, ΔFWHM 8.97 %, Δarea 99.85 %, Δfrac 15.07 pp
C1s C1s Scan_5 local true 4.331 server true 4.332 max Δcentre 0.6 meV, ΔFWHM 0.03 %, Δarea 0.06 %, Δfrac 0.00 pp | m held: server 4.332 Δcentre 0.6 meV, ΔFWHM 0.03 %, Δarea 0.06 %, Δfrac 0.00 pp
C1s C1s Scan_6 local true 5.211 server true 5.230 max Δcentre 2.1 meV, ΔFWHM 0.17 %, Δarea 0.24 %, Δfrac 0.02 pp | m held: server 5.230 Δcentre 2.1 meV, ΔFWHM 0.17 %, Δarea 0.24 %, Δfrac 0.02 pp
C1s C1s Scan_7 local true 7.994 server true 8.016 max Δcentre 1.4 meV, ΔFWHM 0.24 %, Δarea 0.36 %, Δfrac 0.04 pp | m held: server 8.016 Δcentre 1.4 meV, ΔFWHM 0.24 %, Δarea 0.36 %, Δfrac 0.04 pp
C1s C1s Scan_8 local true 2.742 server true 2.741 max Δcentre 0.8 meV, ΔFWHM 0.12 %, Δarea 0.18 %, Δfrac 0.02 pp | m held: server 2.741 Δcentre 0.8 meV, ΔFWHM 0.12 %, Δarea 0.18 %, Δfrac 0.02 pp
U4f U4f Scan_0 local true 2.067 server true 2.055 max Δcentre 1.4 meV, ΔFWHM 0.39 %, Δarea 0.53 %, Δfrac 0.02 pp | m held: server 2.049 Δcentre 1.5 meV, ΔFWHM 0.23 %, Δarea 0.32 %, Δfrac 0.01 pp
U4f U4f Scan_1 local true 2.298 server true 2.267 max Δcentre 3.7 meV, ΔFWHM 1.53 %, Δarea 2.22 %, Δfrac 0.13 pp | m held: server 2.260 Δcentre 3.9 meV, ΔFWHM 1.46 %, Δarea 2.12 %, Δfrac 0.12 pp
U4f U4f Scan_2 local true 1.936 server true 1.940 max Δcentre 1.4 meV, ΔFWHM 0.60 %, Δarea 0.24 %, Δfrac 0.01 pp | m held: server 1.934 Δcentre 1.5 meV, ΔFWHM 0.32 %, Δarea 0.44 %, Δfrac 0.02 pp
U4f U4f Scan_3 local true 1.734 server true 1.732 max Δcentre 3.9 meV, ΔFWHM 3.35 %, Δarea 2.07 %, Δfrac 0.14 pp | m held: server 1.732 Δcentre 1.5 meV, ΔFWHM 0.31 %, Δarea 0.43 %, Δfrac 0.02 pp
U4f U4f Scan_4 local true 1.980 server true 1.798 max Δcentre 28.4 meV, ΔFWHM 5.80 %, Δarea 8.64 %, Δfrac 0.35 pp | m held: server 1.878 Δcentre 13.3 meV, ΔFWHM 3.21 %, Δarea 5.34 %, Δfrac 0.19 pp
U4f U4f Scan_5 local true 2.399 server true 2.174 max Δcentre 4.5 meV, ΔFWHM 4.40 %, Δarea 6.81 %, Δfrac 0.33 pp | m held: server 2.187 Δcentre 6.3 meV, ΔFWHM 3.50 %, Δarea 5.49 %, Δfrac 0.24 pp
U4f U4f Scan_6 local true 2.664 server true 2.798 max Δcentre 28.7 meV, ΔFWHM 14.94 %, Δarea 8.62 %, Δfrac 0.75 pp | m held: server 2.634 Δcentre 3.6 meV, ΔFWHM 1.08 %, Δarea 1.60 %, Δfrac 0.07 pp
U4f U4f Scan_7 local true 1.765 server true 1.757 max Δcentre 2.2 meV, ΔFWHM 0.68 %, Δarea 0.85 %, Δfrac 0.05 pp | m held: server 1.752 Δcentre 2.5 meV, ΔFWHM 0.44 %, Δarea 0.60 %, Δfrac 0.04 pp
U4f U4f Scan_8 local true 4.660 server true 4.129 max Δcentre 5.2 meV, ΔFWHM 5.12 %, Δarea 8.47 %, Δfrac 0.33 pp | m held: server 4.118 Δcentre 5.8 meV, ΔFWHM 4.97 %, Δarea 8.23 %, Δfrac 0.32 pp
{"cases":210,"free_failed":0,"held_failed":0,"free_ended_worse_than_held":0,"first_fails":[]}

exec
/bin/zsh -lc "node - <<'JS'
const fs=require('fs');
for(const n of ['lacx_page_vs_server_before','lacx_page_vs_server_after']) console.log(n,JSON.parse(fs.readFileSync('docs/findings/cam/'+n+'.json')).summary);
const d=JSON.parse(fs.readFileSync('docs/findings/cam/local_server_gap_after_cam.json'));
console.log('generated',d.generated);
for(const r of d.regions.U4f) console.log(r.target, 'success',r.local_success,r.server_success,r.server_held_m_success,'chi %',100*(r.local_chi2r/r.server_chi2r-1),'held chi %',100*(r.local_chi2r/r.server_held_m_chi2r-1),'area',r.max_dArea_pct,'held area',r.held_max_dArea_pct,'held frac',r.held_max_dFrac_pp,'held m',r.comps.filter(c=>c.shape==='LACX').map(c=>c.server_held_m.caM));
JS
rg -n 'caM|fixCaM|_laKernelHalf|isDiscrete|piece-confined' static/js tests/js scripts --glob '*.js' --glob '"'!reference*'"'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 0ms:
zsh:1: can't create temp file for here document: operation not permitted
tests/js/local_lm_descent.test.js:38:  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', '_laKernelHalf', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
tests/js/local_lm_descent.test.js:285:const SYNC_KEYS = ['glMix','asymmetry','dsAlpha','dsGamma','laAlpha','laBeta','laM','caAlpha','caBeta','caM'];
tests/js/local_lm_descent.test.js:480:// ── caM unit (2026-09-25): the local engine HOLDS LA's m, exactly ──
tests/js/local_lm_descent.test.js:481:// It used to make a free caM free and then ROUND it in its clamp, so a
tests/js/local_lm_descent.test.js:487:  const truth = { id: 1, name: 'la', shape: 'LACX', center: 281.5, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: 8.66, glMix: 50, asymmetry: 0 };
tests/js/local_lm_descent.test.js:488:  const fitFrom = (fixCaM) => {
tests/js/local_lm_descent.test.js:492:    env.state.peaks = [{ ...truth, caM: 5.37, amplitude: 4000, fixCenter: true, fixFwhm: true, fixCaAlpha: true, fixCaBeta: true, fixCaM }];
tests/js/local_lm_descent.test.js:498:  assert.equal(free.p.caM, 5.37, 'held exactly — not rounded to 5, not moved');
tests/js/local_lm_descent.test.js:499:  assert.equal(held.p.caM, 5.37);
tests/js/local_lm_descent.test.js:505:// caM unit, Codex rounds 1–2: LA's curve JUMPS where the kernel half-width
tests/js/local_lm_descent.test.js:511:    truth: { center: 283.013, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: 48 }, noise: i => 5 * Math.sin(1.77 * i),
tests/js/local_lm_descent.test.js:514:    truth: { center: 281.538, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: 18 / 7 - 0.001 }, noise: i => 0.1 * Math.sin(3 * i),
tests/js/local_lm_descent.test.js:515:    start: { amplitude: 4000, caM: 2.6 }, lock: {} },
tests/js/local_lm_descent.test.js:518:    const run = (fixCaM) => {
tests/js/local_lm_descent.test.js:523:      env.state.peaks = [{ ...truth, ...c.start, ...c.lock, fixCaM }];
tests/js/local_lm_descent.test.js:537:  { label: 'exact transition m = 18/7, 61 pts at 0.03 eV', be: grid(280, 281.8, 0.03), truth: { center: 280.913, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: 18 / 7 }, noise: i => 0.1 * Math.sin(3 * i), start: {}, lock: { fixCenter: true, fixFwhm: true, fixCaAlpha: true, fixCaBeta: true } },
tests/js/local_lm_descent.test.js:538:  { label: 'm = 0 data, start m = 0.001', be: grid(280, 283, 0.05), truth: { center: 281.513, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: 0 }, noise: () => 0, start: { caM: 0.001, amplitude: 4500 }, lock: { fixCenter: true, fixFwhm: true, fixCaAlpha: true, fixCaBeta: true } },
tests/js/local_lm_descent.test.js:545:    env.state.peaks = [{ ...truth, ...c.start, ...c.lock, fixCaM: false }];
tests/js/local_lm_descent.test.js:548:    assert.equal(env.state.peaks[0].caM, c.start.caM ?? c.truth.caM, 'm held exactly');
scripts/lacx_page_vs_server.js:2:// caM unit (2026-09-25): the page's LA (LACX) curve vs the server's, for every
scripts/lacx_page_vs_server.js:25:      rows.push({ project: zp, tab: t.name, peak: p.name, caM: p.caM, fixCaM: !!p.fixCaM, be, p });
scripts/lacx_page_vs_server.js:26:      specs.push({ shape: 'la_casaxps', params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm, alpha: p.caAlpha, beta: p.caBeta, m: p.caM }, x: be });
scripts/lacx_page_vs_server.js:34:  return { project: r.project, tab: r.tab, peak: r.peak, caM: r.caM, fixCaM: r.fixCaM, maxDiffRel: mx / Math.abs(r.p.amplitude || 1), dAreaPct: aS ? 100 * (aP / aS - 1) : null };
scripts/lacx_page_vs_server.js:37:const summary = { components: out.length, integer_caM: out.filter(r => Number.isInteger(r.caM)).length, locked: out.filter(r => r.fixCaM).length,
scripts/local_server_gap.js:17:// start since the caM unit (2026-09-25; before it, the start rounded) —
scripts/local_server_gap.js:32:  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', '_laKernelHalf', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
scripts/local_server_gap.js:80:    // held at the value the local engine holds: its exact start since the caM unit (it rounded it before)
scripts/local_server_gap.js:81:    const heldStart = T.start.map(p => p.shape === 'LACX' ? { ...p, fixCaM: true } : p);
scripts/local_server_gap.js:92:      local: { center: p.center, fwhm: p.fwhm, amplitude: p.amplitude, area: aL[i] }, server: { center: serverPeaks[i].center, fwhm: serverPeaks[i].fwhm, amplitude: serverPeaks[i].amplitude, area: aS[i], glMix: serverPeaks[i].glMix, caM: serverPeaks[i].caM },
scripts/local_server_gap.js:93:      server_held_m: { center: serverHeldPeaks[i].center, fwhm: serverHeldPeaks[i].fwhm, amplitude: serverHeldPeaks[i].amplitude, area: aH[i], caM: serverHeldPeaks[i].caM } }));
scripts/cam_transition_sweep.js:1:const path = require('path'); process.chdir(path.join(__dirname, '..'));   // caM unit, Codex round 1: local LA fits with m free around kernel-width transitions (m = 6k/7) vs m held
scripts/cam_transition_sweep.js:5:const NAMES = ['_arrMin','_arrMax','gaussian','lorentzian','pseudoVoigt','asymmGL','doniachSunjic','laCasaXPSCore','laCasaXPS','laTrueCasaXPS','_laKernelHalf','laTrueCasaXPS_array','evalPeak','_dsgAlpha','dsgDeltaKernel_array','_fftRadix2','_circularConvolve','dsgConvolved_array','evalPeakArray','evalAllPeaks','getPeak','runFitLocal','solveLinear','_computeRFactor','_fitStatLabel','_isUnweightedLocal','_isLocalProvenance','_localFitDetail','_isLocalFit','_isLocalModel','_governingProvenance','_localFitCaveat','_fitStatusText','_applyStatCaption','_applyStatDisplay','_updateLocalModelBanner','_componentSupportCore','_supportRootOf','_applySupportVerdicts'];
scripts/cam_transition_sweep.js:16:  const truth = { id: 1, name: 'la', shape: 'LACX', center: 280 + 75 * st + 0.013, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: mT, glMix: 50, asymmetry: 0 };
scripts/cam_transition_sweep.js:17:  const run = fixCaM => { const e = env(); e.state.peaks = [{ ...truth }]; const d = e.evalAllPeaks(be, e.state.peaks).map((v, i) => v + 5 * Math.sin(1.77 * i));
scripts/cam_transition_sweep.js:18:    e.state.peaks = [{ ...truth, amplitude: 4600, caM: Math.max(0.01, mT + startDelta), fixCenter: true, fixFwhm: true, fixCaM }]; const o = e.runFitLocal(be, d, be.map(() => 0)); return { o, chi: e.state.fitResult && e.state.fitResult.chi }; };
tests/js/lineshape_roundtrip.test.js:44:  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', '_laKernelHalf', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
tests/js/lineshape_roundtrip.test.js:74:    laAlpha: 0.10, laBeta: 0.3, laM: 0.4, caAlpha: 1.0, caBeta: 1.0, caM: 50,
tests/js/lineshape_roundtrip.test.js:78:    fixCaAlpha: false, fixCaBeta: false, fixCaM: false,
tests/js/lineshape_roundtrip.test.js:91:  'LACX':       { truth: { shape: 'LACX', caAlpha: 1.6, caBeta: 0.7, caM: 20 }, start: { caAlpha: 1.0, caBeta: 1.0, caM: 30 } },
tests/js/lineshape_roundtrip.test.js:94:const KNOWN_GAP = {};   // LACX was the last (the page drew m rounded to an integer kernel) — closed by the caM unit, 2026-09-25
tests/js/lineshape_roundtrip.test.js:184:  { label: 'LA alpha 0.1 locked (m = 0)', truth: { shape: 'LACX', caAlpha: 0.1, caBeta: 1, caM: 0, fixCaAlpha: true, fixCaM: true }, held: { alpha: 0.1, m: 0 } },
tests/js/lineshape_roundtrip.test.js:185:  { label: 'LA alpha 5 locked (m = 0)',   truth: { shape: 'LACX', caAlpha: 5, caBeta: 1, caM: 0, fixCaAlpha: true, fixCaM: true }, held: { alpha: 5, m: 0 } },
tests/js/lineshape_roundtrip.test.js:186:  { label: 'LA beta 0.1 locked (m = 0)',  truth: { shape: 'LACX', caAlpha: 1, caBeta: 0.1, caM: 0, fixCaBeta: true, fixCaM: true }, held: { beta: 0.1, m: 0 } },
tests/js/lineshape_roundtrip.test.js:187:  { label: 'LA beta 5 locked (m = 0)',    truth: { shape: 'LACX', caAlpha: 1, caBeta: 5, caM: 0, fixCaBeta: true, fixCaM: true }, held: { beta: 5, m: 0 } },
tests/js/lineshape_roundtrip.test.js:191:  // comparison sits under the caM evaluator gap marked todo above (curve: false)
tests/js/lineshape_roundtrip.test.js:194:  { label: 'LA m 499 locked',    truth: { shape: 'LACX', caAlpha: 1, caBeta: 1, caM: 499, fixCaM: true }, held: { m: 499 } },
tests/js/lineshape_roundtrip.test.js:195:  { label: 'LA m 8.66 locked (a fractional m, as a fit returns it)', truth: { shape: 'LACX', caAlpha: 1.3, caBeta: 0.9, caM: 8.66, fixCaM: true }, held: { m: 8.66 } },
tests/js/lineshape_roundtrip.test.js:248:      fixDsAlpha: true, fixDsGamma: true, fixLaAlpha: true, fixLaBeta: true, fixLaM: true, fixCaAlpha: true, fixCaBeta: true, fixCaM: true }), params });
scripts/voigt_saved_vs_refit.js:32:  'laTrueCasaXPS', '_laKernelHalf', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array', 'evalPeakArray', 'getPeak', '_applyBackendParams', '_bgWindowIndices'];
tests/js/shape_switch_roundtrip.test.js:56:  'LACX':       ['center', 'amplitude', 'fwhm', 'caAlpha', 'caBeta', 'caM'],
tests/js/shape_switch_roundtrip.test.js:68:    caAlpha: 1.4, caBeta: 0.8, caM: 37,
tests/js/shape_switch_roundtrip.test.js:73:    fixCaAlpha: false, fixCaBeta: false, fixCaM: true,
tests/js/shape_switch_roundtrip.test.js:165:              caAlpha: 1.70, caBeta: 0.80, caM: 37 };
tests/js/shape_switch_roundtrip.test.js:172:  const d = _shapeExportCols({ ...makePeak('DSG_LA'), caAlpha: 9, caBeta: 9, caM: 9 });
tests/js/lineshape_parity.test.js:109:    caAlpha: 1.4, caBeta: 0.8, caM: 50,
tests/js/lineshape_parity.test.js:123:  'LACX':       p => ({ shape: 'la_casaxps',      params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm, alpha: p.caAlpha, beta: p.caBeta, m: p.caM } }),
tests/js/lineshape_parity.test.js:171:test('(A) frontend vs backend parity: LACX (m>0) (FIXED 2026-09-25, caM unit: continuous-m kernel mirrored)', () => {
tests/js/lineshape_parity.test.js:184:  p.caM = 0;
tests/js/lineshape_parity.test.js:346:  'LACX (m = 0)': { caAlpha: [0.1, 1, 5], caBeta: [0.1, 1, 5], caM: [0], fwhm: FWHM_RANGE },
tests/js/lineshape_parity.test.js:350:  // continuous m (caM unit, 2026-09-25): fractional values, the 1e-3 threshold, and the 499 ceiling
tests/js/lineshape_parity.test.js:351:  'LACX (m > 0)':   { caAlpha: [0.1, 1, 5], caBeta: [0.1, 1, 5], caM: [0.001, 0.5, 1, 5, 8.66, 50, 123.4, 499], fwhm: FWHM_RANGE },
tests/js/lineshape_parity.test.js:389:  test(`(D) sweep across the fitted range: ${label} — KNOWN GAP`, { todo: 'convolved shapes: LACX kernel discretisation (unit 2 / caM clamp); DSG_LA page quadrature step ignores the Gaussian kernel width (own unit)' }, () => {
tests/js/lineshape_parity.test.js:484:// ── (D‴) LA convergence beyond the base grid (caM unit, 2026-09-25) ──────────
tests/js/lineshape_parity.test.js:489:const LA_BOX = { caAlpha: [0.1, 1.4, 5], caBeta: [0.1, 0.8, 5], caM: [0.001, 2.5, 8.66, 50, 499] };

 exited 1 in 65366ms:
# Subtest: a supported but NOT required anchor is refused before any charge-correction input is touched
ok 1 - a supported but NOT required anchor is refused before any charge-correction input is touched
  ---
  duration_ms: 8.078522
  type: 'test'
  ...
# Subtest: a required anchor proceeds; a check that did not run (older server, error, non-converged) does not block
ok 2 - a required anchor proceeds; a check that did not run (older server, error, non-converged) does not block
  ---
  duration_ms: 16.333267
  type: 'test'
  ...
# Subtest: the request asks for the Graphite anchor by id, and the gate precedes the support gate and every cc write
ok 3 - the request asks for the Graphite anchor by id, and the gate precedes the support gate and every cc write
  ---
  duration_ms: 1.622744
  type: 'test'
  ...
# Subtest: the fixture set covers both outcomes
ok 4 - the fixture set covers both outcomes
  ---
  duration_ms: 2.21473
  type: 'test'
  ...
# Subtest: anchors NOTHING — residue: 1e7 flat, 1e-4 bump rounded away, manual background (round 5)
ok 5 - anchors NOTHING — residue: 1e7 flat, 1e-4 bump rounded away, manual background (round 5)
  ---
  duration_ms: 6.68507
  type: 'test'
  ...
# Subtest: anchors NOTHING — residue: 10.009999 flat uploaded as 10.01, unrounded manual background (round 3)
ok 6 - anchors NOTHING — residue: 10.009999 flat uploaded as 10.01, unrounded manual background (round 3)
  ---
  duration_ms: 4.71195
  type: 'test'
  ...
# Subtest: anchors NOTHING — residue: 10 + 1e-4 bump, linear background (round 2)
ok 7 - anchors NOTHING — residue: 10 + 1e-4 bump, linear background (round 2)
  ---
  duration_ms: 7.167393
  type: 'test'
  ...
# Subtest: anchors NOTHING — collapsed model: 30-count bump, manual background over-estimated at 1020 (round 1)
ok 8 - anchors NOTHING — collapsed model: 30-count bump, manual background over-estimated at 1020 (round 1)
  ---
  duration_ms: 2.489732
  type: 'test'
  ...
# Subtest: anchors the correction — resolved 0.0058 line on a zero background, 17 samples survive the upload (round 5)
ok 9 - anchors the correction — resolved 0.0058 line on a zero background, 17 samples survive the upload (round 5)
  ---
  duration_ms: 2.963612
  type: 'test'
  ...
# Subtest: anchors the correction — resolved 50-count line on a noise-free 1e6 background (round 4)
ok 10 - anchors the correction — resolved 50-count line on a noise-free 1e6 background (round 4)
  ---
  duration_ms: 1.877727
  type: 'test'
  ...
# Subtest: anchors the correction — resolved 10 000-count line on a steep noisy ramp, 100 scans averaged (round 2)
ok 11 - anchors the correction — resolved 10 000-count line on a steep noisy ramp, 100 scans averaged (round 2)
  ---
  duration_ms: 1.761604
  type: 'test'
  ...
# Subtest: anchors the correction — resolved 10 000-count anchor behind a 300 000-count one-channel spike (round 3)
ok 12 - anchors the correction — resolved 10 000-count anchor behind a 300 000-count one-channel spike (round 3)
  ---
  duration_ms: 2.126404
  type: 'test'
  ...
# Subtest: anchors the correction — ordinary C 1s: 86 000-count graphite line with Poisson noise
ok 13 - anchors the correction — ordinary C 1s: 86 000-count graphite line with Poisson noise
  ---
  duration_ms: 1.974027
  type: 'test'
  ...
# Subtest: an anchor amplitude of 0 is refused before anything is computed
ok 14 - an anchor amplitude of 0 is refused before anything is computed
  ---
  duration_ms: 1.830915
  type: 'test'
  ...
# Subtest: an anchor amplitude of -5 is refused before anything is computed
ok 15 - an anchor amplitude of -5 is refused before anything is computed
  ---
  duration_ms: 1.623195
  type: 'test'
  ...
# Subtest: an anchor amplitude of NaN is refused before anything is computed
ok 16 - an anchor amplitude of NaN is refused before anything is computed
  ---
  duration_ms: 1.674058
  type: 'test'
  ...
# Subtest: an anchor amplitude of Infinity is refused before anything is computed
ok 17 - an anchor amplitude of Infinity is refused before anything is computed
  ---
  duration_ms: 1.104627
  type: 'test'
  ...
# Subtest: a response that lacks the fitted data or the component curve cannot vouch for an anchor
ok 18 - a response that lacks the fitted data or the component curve cannot vouch for an anchor
  ---
  duration_ms: 3.214473
  type: 'test'
  ...
# Subtest: an exact fit that needs the component is supported (chi-square with it is zero)
ok 19 - an exact fit that needs the component is supported (chi-square with it is zero)
  ---
  duration_ms: 1.314111
  type: 'test'
  ...
# Subtest: removing a component that costs nothing is the definition of unsupported
ok 20 - removing a component that costs nothing is the definition of unsupported
  ---
  duration_ms: 1.40058
  type: 'test'
  ...
# Subtest: the support check precedes every write of the charge-correction inputs
ok 21 - the support check precedes every write of the charge-correction inputs
  ---
  duration_ms: 0.819351
  type: 'test'
  ...
# Subtest: the fallback "first peak" anchor is held to the same rule
ok 22 - the fallback "first peak" anchor is held to the same rule
  ---
  duration_ms: 1.689109
  type: 'test'
  ...
# Subtest: rolling back to a Custom reference shows its target field again
ok 23 - rolling back to a Custom reference shows its target field again
  ---
  duration_ms: 1.379278
  type: 'test'
  ...
# Subtest: source ROI overwrites a different target ROI during propagation
ok 24 - source ROI overwrites a different target ROI during propagation
  ---
  duration_ms: 1.761144
  type: 'test'
  ...
# Subtest: blank source ROI leaves the target ROI unchanged (never wipes it)
ok 25 - blank source ROI leaves the target ROI unchanged (never wipes it)
  ---
  duration_ms: 0.373365
  type: 'test'
  ...
# Subtest: a blank source ROI bound (one side) falls back per-field
ok 26 - a blank source ROI bound (one side) falls back per-field
  ---
  duration_ms: 0.244456
  type: 'test'
  ...
# Subtest: background fields still propagate from source (no regression)
ok 27 - background fields still propagate from source (no regression)
  ---
  duration_ms: 0.239887
  type: 'test'
  ...
# Subtest: blank source bgStart/bgEnd fall back to target (unchanged guard semantics)
ok 28 - blank source bgStart/bgEnd fall back to target (unchanged guard semantics)
  ---
  duration_ms: 0.349202
  type: 'test'
  ...
# Subtest: unrelated target UI fields are preserved untouched
ok 29 - unrelated target UI fields are preserved untouched
  ---
  duration_ms: 1.302957
  type: 'test'
  ...
# Subtest: legacy source without endpointAvg propagates 1, not the target default
ok 30 - legacy source without endpointAvg propagates 1, not the target default
  ---
  duration_ms: 1.564663
  type: 'test'
  ...
# Subtest: window at the ROI bounds covers every point, including the last one
ok 31 - window at the ROI bounds covers every point, including the last one
  ---
  duration_ms: 3.232078
  type: 'test'
  ...
# Subtest: off-grid bound inside the ROI never pulls in a point outside it
ok 32 - off-grid bound inside the ROI never pulls in a point outside it
  ---
  duration_ms: 0.378672
  type: 'test'
  ...
# Subtest: bound order does not matter
ok 33 - bound order does not matter
  ---
  duration_ms: 1.376843
  type: 'test'
  ...
# Subtest: ascending grid gives the same point set as descending
ok 34 - ascending grid gives the same point set as descending
  ---
  duration_ms: 0.274379
  type: 'test'
  ...
# Subtest: blank or NaN bound falls back to the full range
ok 35 - blank or NaN bound falls back to the full range
  ---
  duration_ms: 0.299327
  type: 'test'
  ...
# Subtest: fewer than two points in range falls back to the full range
ok 36 - fewer than two points in range falls back to the full range
  ---
  duration_ms: 0.325372
  type: 'test'
  ...
# Subtest: exactly two points in range is a usable window
ok 37 - exactly two points in range is a usable window
  ---
  duration_ms: 0.339637
  type: 'test'
  ...
# Subtest: computeBackgroundCore uses exactly the helper window
ok 38 - computeBackgroundCore uses exactly the helper window
  ---
  duration_ms: 1.385175
  type: 'test'
  ...
# Subtest: no request builder uses the old nearest-index idiom for the bg window
ok 39 - no request builder uses the old nearest-index idiom for the bg window
  ---
  duration_ms: 1.171023
  type: 'test'
  ...
# Subtest: both /api/fit request builders send the inclusive window as end_idx = i1 + 1
ok 40 - both /api/fit request builders send the inclusive window as end_idx = i1 + 1
  ---
  duration_ms: 2.321927
  type: 'test'
  ...
# Subtest: new tabs default to endpoint averaging 3, via one constant
ok 41 - new tabs default to endpoint averaging 3, via one constant
  ---
  duration_ms: 2.651883
  type: 'test'
  ...
# Subtest: legacy fallbacks resolve a saved ui without endpointAvg to 1
ok 42 - legacy fallbacks resolve a saved ui without endpointAvg to 1
  ---
  duration_ms: 1.118918
  type: 'test'
  ...
# Subtest: no bare endpointAvg || '1' fallback survives outside the constant
ok 43 - no bare endpointAvg || '1' fallback survives outside the constant
  ---
  duration_ms: 1.750085
  type: 'test'
  ...
# Subtest: Find Peaks records the averaging its engine used and applies it on apply
ok 44 - Find Peaks records the averaging its engine used and applies it on apply
  ---
  duration_ms: 2.041181
  type: 'test'
  ...
# Subtest: undo/redo carry the averaging recorded by the Find Peaks apply action
ok 45 - undo/redo carry the averaging recorded by the Find Peaks apply action
  ---
  duration_ms: 0.761723
  type: 'test'
  ...
# Subtest: averaging snapshots live on the tab record: undo/redo read the ACTIVE tab only
ok 46 - averaging snapshots live on the tab record: undo/redo read the ACTIVE tab only
  ---
  duration_ms: 0.651598
  type: 'test'
  ...
# Subtest: FP_TIER_META defines all three tiers with a color and short label
ok 47 - FP_TIER_META defines all three tiers with a color and short label
  ---
  duration_ms: 1.990593
  type: 'test'
  ...
# Subtest: _fpRegionMatchesFilter: empty query matches everything
ok 48 - _fpRegionMatchesFilter: empty query matches everything
  ---
  duration_ms: 0.45352
  type: 'test'
  ...
# Subtest: _fpRegionMatchesFilter: matches by symbol (case-insensitive, prefix)
ok 49 - _fpRegionMatchesFilter: matches by symbol (case-insensitive, prefix)
  ---
  duration_ms: 0.284391
  type: 'test'
  ...
# Subtest: _fpRegionMatchesFilter: matches by element name substring
ok 50 - _fpRegionMatchesFilter: matches by element name substring
  ---
  duration_ms: 2.930734
  type: 'test'
  ...
# Subtest: _fpRegionMatchesFilter: matches by level/subshell
ok 51 - _fpRegionMatchesFilter: matches by level/subshell
  ---
  duration_ms: 0.311936
  type: 'test'
  ...
# Subtest: _fpRegionMatchesFilter: matches the full region label
ok 52 - _fpRegionMatchesFilter: matches the full region label
  ---
  duration_ms: 0.237727
  type: 'test'
  ...
# Subtest: _fpRegionOptionLabel: includes the tier tag, region, and element name
ok 53 - _fpRegionOptionLabel: includes the tier tag, region, and element name
  ---
  duration_ms: 0.547073
  type: 'test'
  ...
# Subtest: _fpRegionOptionLabel: structure_only region is tagged distinctly from curated
ok 54 - _fpRegionOptionLabel: structure_only region is tagged distinctly from curated
  ---
  duration_ms: 0.347428
  type: 'test'
  ...
# Subtest: _fpBuildRegionOptions: no query returns everything, sorted stably by input order
ok 55 - _fpBuildRegionOptions: no query returns everything, sorted stably by input order
  ---
  duration_ms: 2.099066
  type: 'test'
  ...
# Subtest: _fpBuildRegionOptions: filters by query, each option carries its tier
ok 56 - _fpBuildRegionOptions: filters by query, each option carries its tier
  ---
  duration_ms: 1.125042
  type: 'test'
  ...
# Subtest: _fpBuildRegionOptions: an unmatched query yields an empty list (never throws)
ok 57 - _fpBuildRegionOptions: an unmatched query yields an empty list (never throws)
  ---
  duration_ms: 0.443279
  type: 'test'
  ...
# Subtest: _fpBuildRegionOptions: tolerates a missing/empty coverage array
ok 58 - _fpBuildRegionOptions: tolerates a missing/empty coverage array
  ---
  duration_ms: 0.221032
  type: 'test'
  ...
# Subtest: _fpTierNoteFor: single curated selection shows its own note
ok 59 - _fpTierNoteFor: single curated selection shows its own note
  ---
  duration_ms: 0.262121
  type: 'test'
  ...
# Subtest: _fpTierNoteFor: single fallback (machine) selection is honestly labeled
ok 60 - _fpTierNoteFor: single fallback (machine) selection is honestly labeled
  ---
  duration_ms: 0.233074
  type: 'test'
  ...
# Subtest: _fpTierNoteFor: structure_only selection says no reference position
ok 61 - _fpTierNoteFor: structure_only selection says no reference position
  ---
  duration_ms: 0.166198
  type: 'test'
  ...
# Subtest: _fpTierNoteFor: no selection is an empty string (never throws)
ok 62 - _fpTierNoteFor: no selection is an empty string (never throws)
  ---
  duration_ms: 0.149102
  type: 'test'
  ...
# Subtest: _fpTierNoteFor: multi-region selection lists each region+tier
ok 63 - _fpTierNoteFor: multi-region selection lists each region+tier
  ---
  duration_ms: 0.242276
  type: 'test'
  ...
# Subtest: runFindPeaks injects the panel value only for methods advertising endpoint_avg, JSON wins
ok 64 - runFindPeaks injects the panel value only for methods advertising endpoint_avg, JSON wins
  ---
  duration_ms: 1.995687
  type: 'test'
  ...
# Subtest: _fpMethodChanged does not write endpoint_avg into the Advanced JSON view
ok 65 - _fpMethodChanged does not write endpoint_avg into the Advanced JSON view
  ---
  duration_ms: 0.672784
  type: 'test'
  ...
# Subtest: _fpBestTier: curated wins over machine and structure_only
ok 66 - _fpBestTier: curated wins over machine and structure_only
  ---
  duration_ms: 1.873752
  type: 'test'
  ...
# Subtest: _fpBestTier: machine wins over structure_only when no curated present
ok 67 - _fpBestTier: machine wins over structure_only when no curated present
  ---
  duration_ms: 0.310805
  type: 'test'
  ...
# Subtest: _fpBestTier: empty entries -> null (an element with zero practical coverage)
ok 68 - _fpBestTier: empty entries -> null (an element with zero practical coverage)
  ---
  duration_ms: 0.194709
  type: 'test'
  ...
# Subtest: FP_TIER_RANK: strictly orders curated > machine > structure_only
ok 69 - FP_TIER_RANK: strictly orders curated > machine > structure_only
  ---
  duration_ms: 0.205295
  type: 'test'
  ...
# Subtest: _fpNextSelection: plain click on a fresh region replaces an existing single selection
ok 70 - _fpNextSelection: plain click on a fresh region replaces an existing single selection
  ---
  duration_ms: 1.729771
  type: 'test'
  ...
# Subtest: _fpNextSelection: plain click replaces a multi-region selection with just the clicked one
ok 71 - _fpNextSelection: plain click replaces a multi-region selection with just the clicked one
  ---
  duration_ms: 1.486676
  type: 'test'
  ...
# Subtest: _fpNextSelection: plain click on the ONLY already-selected region is a no-op (stays selected)
ok 72 - _fpNextSelection: plain click on the ONLY already-selected region is a no-op (stays selected)
  ---
  duration_ms: 0.373008
  type: 'test'
  ...
# Subtest: _fpNextSelection: additive click ADDS a second region (ctrl-click co-fit)
ok 73 - _fpNextSelection: additive click ADDS a second region (ctrl-click co-fit)
  ---
  duration_ms: 0.3195
  type: 'test'
  ...
# Subtest: _fpNextSelection: additive click on an already-selected region REMOVES it
ok 74 - _fpNextSelection: additive click on an already-selected region REMOVES it
  ---
  duration_ms: 0.544977
  type: 'test'
  ...
# Subtest: _fpNextSelection: additive click on the last remaining region empties the selection
ok 75 - _fpNextSelection: additive click on the last remaining region empties the selection
  ---
  duration_ms: 0.670357
  type: 'test'
  ...
# Subtest: _fpNextSelection: never mutates the `current` Set passed in
ok 76 - _fpNextSelection: never mutates the `current` Set passed in
  ---
  duration_ms: 0.387966
  type: 'test'
  ...
# Subtest: _fpBoundaryHitLabel: translates role:param@max with no raw identifiers
ok 77 - _fpBoundaryHitLabel: translates role:param@max with no raw identifiers
  ---
  duration_ms: 4.945257
  type: 'test'
  ...
# Subtest: _fpBoundaryHitLabel: @min reads as lower limit
ok 78 - _fpBoundaryHitLabel: @min reads as lower limit
  ---
  duration_ms: 0.481592
  type: 'test'
  ...
# Subtest: _fpBoundaryHitLabel: unparseable input degrades honestly, never throws
ok 79 - _fpBoundaryHitLabel: unparseable input degrades honestly, never throws
  ---
  duration_ms: 0.344748
  type: 'test'
  ...
# Subtest: _fpWidthFlagLabel: detection-family "absorbing a neighbor" variant
ok 80 - _fpWidthFlagLabel: detection-family "absorbing a neighbor" variant
  ---
  duration_ms: 0.624796
  type: 'test'
  ...
# Subtest: _fpWidthFlagLabel: ordinary-cap "no known-broad justification" variant reads distinctly
ok 81 - _fpWidthFlagLabel: ordinary-cap "no known-broad justification" variant reads distinctly
  ---
  duration_ms: 0.308468
  type: 'test'
  ...
# Subtest: _fpWidthFlagLabel: DS+G and asym-GL variants still extract role + width cleanly
ok 82 - _fpWidthFlagLabel: DS+G and asym-GL variants still extract role + width cleanly
  ---
  duration_ms: 0.218775
  type: 'test'
  ...
# Subtest: _fpPlainMessage: structural_only stub (no cited or sourced data)
ok 83 - _fpPlainMessage: structural_only stub (no cited or sourced data)
  ---
  duration_ms: 0.745132
  type: 'test'
  ...
# Subtest: _fpPlainMessage: an EMPTY structural_only array must NOT trigger the stub (Codex-caught)
ok 84 - _fpPlainMessage: an EMPTY structural_only array must NOT trigger the stub (Codex-caught)
  ---
  duration_ms: 0.289585
  type: 'test'
  ...
# Subtest: _fpPlainMessage: a MIXED request that succeeded must NOT trigger the stub either (Codex-caught, round 2)
ok 85 - _fpPlainMessage: a MIXED request that succeeded must NOT trigger the stub either (Codex-caught, round 2)
  ---
  duration_ms: 0.651203
  type: 'test'
  ...
# Subtest: _fpPlainMessage: a MIXED request that failed for an unrelated reason must NOT trigger the stub
ok 86 - _fpPlainMessage: a MIXED request that failed for an unrelated reason must NOT trigger the stub
  ---
  duration_ms: 0.658802
  type: 'test'
  ...
# Subtest: _fpPlainMessage: no survivors
ok 87 - _fpPlainMessage: no survivors
  ---
  duration_ms: 0.302471
  type: 'test'
  ...
# Subtest: _fpPlainMessage: no survivors + truncated mentions the honest count
ok 88 - _fpPlainMessage: no survivors + truncated mentions the honest count
  ---
  duration_ms: 0.205002
  type: 'test'
  ...
# Subtest: _fpPlainMessage: clean winner with nothing flagged reads as clean
ok 89 - _fpPlainMessage: clean winner with nothing flagged reads as clean
  ---
  duration_ms: 0.162237
  type: 'test'
  ...
# Subtest: _fpPlainMessage: data-driven (region-unassigned) components need review
ok 90 - _fpPlainMessage: data-driven (region-unassigned) components need review
  ---
  duration_ms: 0.191046
  type: 'test'
  ...
# Subtest: _fpPlainMessage: decisive_override reads CONDITIONAL and names the fixed parameter
ok 91 - _fpPlainMessage: decisive_override reads CONDITIONAL and names the fixed parameter
  ---
  duration_ms: 0.49191
  type: 'test'
  ...
# Subtest: _fpPlainMessage: unstable_last_resort reads LOW CONFIDENCE, never hides the caveat
ok 92 - _fpPlainMessage: unstable_last_resort reads LOW CONFIDENCE, never hides the caveat
  ---
  duration_ms: 0.264491
  type: 'test'
  ...
# Subtest: _fpPlainMessage: no_clean_survivor names the boundary hit in plain words
ok 93 - _fpPlainMessage: no_clean_survivor names the boundary hit in plain words
  ---
  duration_ms: 0.270643
  type: 'test'
  ...
# Subtest: _fpPlainMessage: unphysical widths surface as LOW CONFIDENCE with no raw ceiling jargon
ok 94 - _fpPlainMessage: unphysical widths surface as LOW CONFIDENCE with no raw ceiling jargon
  ---
  duration_ms: 0.310983
  type: 'test'
  ...
# Subtest: _fpPlainMessage: filtered dominant alternative is mentioned honestly
ok 95 - _fpPlainMessage: filtered dominant alternative is mentioned honestly
  ---
  duration_ms: 0.30677
  type: 'test'
  ...
# Subtest: _fpPlainMessage: a CONDITIONAL result never reads as a clean pass
ok 96 - _fpPlainMessage: a CONDITIONAL result never reads as a clean pass
  ---
  duration_ms: 2.436659
  type: 'test'
  ...
# Subtest: _fpFormatElapsed: sub-minute seconds
ok 97 - _fpFormatElapsed: sub-minute seconds
  ---
  duration_ms: 1.572691
  type: 'test'
  ...
# Subtest: _fpFormatElapsed: minutes + seconds
ok 98 - _fpFormatElapsed: minutes + seconds
  ---
  duration_ms: 0.325055
  type: 'test'
  ...
# Subtest: _fpFormatElapsed: never negative, tolerates junk input
ok 99 - _fpFormatElapsed: never negative, tolerates junk input
  ---
  duration_ms: 0.23377
  type: 'test'
  ...
# Subtest: _fpProgressText: real candidate-sweep message
ok 100 - _fpProgressText: real candidate-sweep message
  ---
  duration_ms: 0.23876
  type: 'test'
  ...
# Subtest: _fpProgressText: starting phase before any candidate has run
ok 101 - _fpProgressText: starting phase before any candidate has run
  ---
  duration_ms: 0.308402
  type: 'test'
  ...
# Subtest: _fpProgressText: missing/malformed poll degrades to a generic message, never throws
ok 102 - _fpProgressText: missing/malformed poll degrades to a generic message, never throws
  ---
  duration_ms: 0.196604
  type: 'test'
  ...
# Subtest: A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
ok 103 - A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
  ---
  duration_ms: 14.955881
  type: 'test'
  ...
# Subtest: a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
ok 104 - a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
  ---
  duration_ms: 7.515511
  type: 'test'
  ...
# Subtest: a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
ok 105 - a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
  ---
  duration_ms: 4.60619
  type: 'test'
  ...
# Subtest: a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
ok 106 - a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
  ---
  duration_ms: 11.58024
  type: 'test'
  ...
# Subtest: a converged backend result is applied (sanity)
ok 107 - a converged backend result is applied (sanity)
  ---
  duration_ms: 4.06355
  type: 'test'
  ...
# Subtest: the engine/objective labels of a fit result survive spectrum and project save/load
ok 108 - the engine/objective labels of a fit result survive spectrum and project save/load
  ---
  duration_ms: 0.898471
  type: 'test'
  ...
# Subtest: an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
ok 109 - an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
  ---
  duration_ms: 5.2135
  type: 'test'
  ...
# Subtest: an HTTP 502 on the upload is a server failure, not a transport failure
ok 110 - an HTTP 502 on the upload is a server failure, not a transport failure
  ---
  duration_ms: 4.357843
  type: 'test'
  ...
# Subtest: uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
ok 111 - uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
  ---
  duration_ms: 4.272286
  type: 'test'
  ...
# Subtest: every consumer that prints the goodness-of-fit statistic routes through the statistic identity
ok 112 - every consumer that prints the goodness-of-fit statistic routes through the statistic identity
  ---
  duration_ms: 1.166701
  type: 'test'
  ...
# Subtest: uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
ok 113 - uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
  ---
  duration_ms: 1.11233
  type: 'test'
  ...
# Subtest: a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
ok 114 - a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
  ---
  duration_ms: 2.042576
  type: 'test'
  ...
# Subtest: starting-point helpers: keyed on the persisted objective, weighted results untouched
ok 115 - starting-point helpers: keyed on the persisted objective, weighted results untouched
  ---
  duration_ms: 5.607871
  type: 'test'
  ...
# Subtest: Quantify shows the starting-point banner for a local result and not for a weighted one
ok 116 - Quantify shows the starting-point banner for a local result and not for a weighted one
  ---
  duration_ms: 7.506081
  type: 'test'
  ...
# Subtest: every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
ok 117 - every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
  ---
  duration_ms: 2.044343
  type: 'test'
  ...
# Subtest: project save derives the designation from the objective for an older local result lacking the new fields
ok 118 - project save derives the designation from the objective for an older local result lacking the new fields
  ---
  duration_ms: 12.067614
  type: 'test'
  ...
# Subtest: stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
ok 119 - stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
  ---
  duration_ms: 1.245349
  type: 'test'
  ...
# Subtest: _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
ok 120 - _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
  ---
  duration_ms: 4.958281
  type: 'test'
  ...
# Subtest: history preview glow is keyed on the dataset flag, not the label text
ok 121 - history preview glow is keyed on the dataset flag, not the label text
  ---
  duration_ms: 0.786322
  type: 'test'
  ...
# Subtest: spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
ok 122 - spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
  ---
  duration_ms: 0.567254
  type: 'test'
  ...
# Subtest: _applyStatDisplay clears header, tooltip, caption and value together on local → none
ok 123 - _applyStatDisplay clears header, tooltip, caption and value together on local → none
  ---
  duration_ms: 4.665792
  type: 'test'
  ...
# Subtest: _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
ok 124 - _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
  ---
  duration_ms: 2.970646
  type: 'test'
  ...
# Subtest: fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
ok 125 - fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
  ---
  duration_ms: 1.624849
  type: 'test'
  ...
# Subtest: undo/redo snapshots carry and restore model provenance
ok 126 - undo/redo snapshots carry and restore model provenance
  ---
  duration_ms: 6.043677
  type: 'test'
  ...
# Subtest: round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
ok 127 - round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
  ---
  duration_ms: 1.344297
  type: 'test'
  ...
# Subtest: _provenanceOf derives a designation from a live local result, and undo snapshots use it
ok 128 - _provenanceOf derives a designation from a live local result, and undo snapshots use it
  ---
  duration_ms: 4.053331
  type: 'test'
  ...
# Subtest: batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
ok 129 - batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
  ---
  duration_ms: 0.491962
  type: 'test'
  ...
# Subtest: the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
ok 130 - the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
  ---
  duration_ms: 4.305884
  type: 'test'
  ...
# Subtest: round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
ok 131 - round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
  ---
  duration_ms: 0.908984
  type: 'test'
  ...
# Subtest: the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
ok 132 - the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
  ---
  duration_ms: 5.14904
  type: 'test'
  ...
# Subtest: the sidebar banner is sticky at the top of the scrolling panel body
ok 133 - the sidebar banner is sticky at the top of the scrolling panel body
  ---
  duration_ms: 0.314121
  type: 'test'
  ...
# Subtest: the sidebar banner shows on a stack tab whose visible entries draw a local source fit
ok 134 - the sidebar banner shows on a stack tab whose visible entries draw a local source fit
  ---
  duration_ms: 2.877794
  type: 'test'
  ...
# Subtest: every stack chart repaint path refreshes the sidebar designation before any early return
ok 135 - every stack chart repaint path refreshes the sidebar designation before any early return
  ---
  duration_ms: 0.559841
  type: 'test'
  ...
# Subtest: closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
ok 136 - closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
  ---
  duration_ms: 0.281081
  type: 'test'
  ...
# Subtest: W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
ok 137 - W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
  ---
  duration_ms: 4.692842
  type: 'test'
  ...
# Subtest: TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
ok 138 - TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
  ---
  duration_ms: 6.772613
  type: 'test'
  ...
# Subtest: adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
ok 139 - adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
  ---
  duration_ms: 4.022347
  type: 'test'
  ...
# Subtest: adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
ok 140 - adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
  ---
  duration_ms: 3.745688
  type: 'test'
  ...
# Subtest: adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
ok 141 - adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
  ---
  duration_ms: 3.296655
  type: 'test'
  ...
# Subtest: adoption: success records the choice, the starts evidence and the key of the model it describes
ok 142 - adoption: success records the choice, the starts evidence and the key of the model it describes
  ---
  duration_ms: 4.829462
  type: 'test'
  ...
# Subtest: an ordinary Run Fit on one unlinked component does not ask for the starts check
ok 143 - an ordinary Run Fit on one unlinked component does not ask for the starts check
  ---
  duration_ms: 4.087159
  type: 'test'
  ...
# Subtest: a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
ok 144 - a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
  ---
  duration_ms: 4.477603
  type: 'test'
  ...
# Subtest: FP_STRINGS.experimentalNotice names it experimental and states the runtime range
ok 145 - FP_STRINGS.experimentalNotice names it experimental and states the runtime range
  ---
  duration_ms: 1.703217
  type: 'test'
  ...
# Subtest: FP_STRINGS.experimentalNotice says BOTH "starting point" and "not a final answer" -- either alone is not the safety claim
ok 146 - FP_STRINGS.experimentalNotice says BOTH "starting point" and "not a final answer" -- either alone is not the safety claim
  ---
  duration_ms: 0.435599
  type: 'test'
  ...
# Subtest: FP_STRINGS.experimentalNotice does not overclaim correctness and does not describe the app as broken/frozen
ok 147 - FP_STRINGS.experimentalNotice does not overclaim correctness and does not describe the app as broken/frozen
  ---
  duration_ms: 0.37977
  type: 'test'
  ...
# Subtest: the notice banner element and its dismiss button are wired to the actual dismiss function, not just present somewhere in the page
ok 148 - the notice banner element and its dismiss button are wired to the actual dismiss function, not just present somewhere in the page
  ---
  duration_ms: 0.905844
  type: 'test'
  ...
# Subtest: both notice functions read/write the SAME localStorage key -- a mismatched key would show the notice every time despite dismissal
ok 149 - both notice functions read/write the SAME localStorage key -- a mismatched key would show the notice every time despite dismissal
  ---
  duration_ms: 2.412122
  type: 'test'
  ...
# Subtest: the gate function early-returns (hides, does not show) when already dismissed, and only sets text+shows in the un-dismissed path
ok 150 - the gate function early-returns (hides, does not show) when already dismissed, and only sets text+shows in the un-dismissed path
  ---
  duration_ms: 3.659832
  type: 'test'
  ...
# Subtest: openFindPeaksModal calls the notice gate so it actually shows on open
ok 151 - openFindPeaksModal calls the notice gate so it actually shows on open
  ---
  duration_ms: 1.277094
  type: 'test'
  ...
# Subtest: FP_STRINGS.materials.mixed has a clear, non-bare label
ok 152 - FP_STRINGS.materials.mixed has a clear, non-bare label
  ---
  duration_ms: 1.593114
  type: 'test'
  ...
# Subtest: FP_STRINGS.materials.mixed hint is advisory, never claims correction
ok 153 - FP_STRINGS.materials.mixed hint is advisory, never claims correction
  ---
  duration_ms: 1.781309
  type: 'test'
  ...
# Subtest: FP_STRINGS has no override entries for the other 3 material classes (dropdown rendering must stay byte-identical for them)
ok 154 - FP_STRINGS has no override entries for the other 3 material classes (dropdown rendering must stay byte-identical for them)
  ---
  duration_ms: 0.304527
  type: 'test'
  ...
# Subtest: FP_STRINGS.materials.mixed hint names C 1s specifically and does not overstate scope to other regions (Codex run B MAJOR, 77bf3a8 recheck)
ok 155 - FP_STRINGS.materials.mixed hint names C 1s specifically and does not overstate scope to other regions (Codex run B MAJOR, 77bf3a8 recheck)
  ---
  duration_ms: 0.369114
  type: 'test'
  ...
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Subtest: (A) frontend vs backend parity: Gaussian
not ok 156 - (A) frontend vs backend parity: Gaussian
  ---
  duration_ms: 1688.941
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.start (node:internal/test_runner/test:944:17)
    startSubtestAfterBootstrap (node:internal/test_runner/harness:296:17)
  ...
# Subtest: (A) frontend vs backend parity: Lorentzian
not ok 157 - (A) frontend vs backend parity: Lorentzian
  ---
  duration_ms: 1226.807363
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: GL
not ok 158 - (A) frontend vs backend parity: GL
  ---
  duration_ms: 1210.641735
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: Voigt
not ok 159 - (A) frontend vs backend parity: Voigt
  ---
  duration_ms: 1183.082531
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DS
not ok 160 - (A) frontend vs backend parity: DS
  ---
  duration_ms: 1268.232982
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: asym-GL
not ok 161 - (A) frontend vs backend parity: asym-GL
  ---
  duration_ms: 1623.458555
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: LACX (m>0) (FIXED 2026-09-25, caM unit: continuous-m kernel mirrored)
not ok 162 - (A) frontend vs backend parity: LACX (m>0) (FIXED 2026-09-25, caM unit: continuous-m kernel mirrored)
  ---
  duration_ms: 1299.966509
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:171:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:176:15)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: LACX at m=0 (no convolution)
not ok 163 - (A) frontend vs backend parity: LACX at m=0 (no convolution)
  ---
  duration_ms: 1332.477836
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:182:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:188:15)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at moderate m (FIXED 2026-09-22: grid-aware convolution, dsgConvolved_array)
not ok 164 - (A) frontend vs backend parity: DSG_LA at moderate m (FIXED 2026-09-22: grid-aware convolution, dsgConvolved_array)
  ---
  duration_ms: 1450.230946
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:194:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:199:15)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, center on-grid (delta kernel)
not ok 165 - (A) frontend vs backend parity: DSG_LA at m=0, center on-grid (delta kernel)
  ---
  duration_ms: 1392.889137
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:218:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:225:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, center half-step off-grid (delta kernel)
not ok 166 - (A) frontend vs backend parity: DSG_LA at m=0, center half-step off-grid (delta kernel)
  ---
  duration_ms: 1337.336314
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:218:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:225:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0.0009, center on-grid (delta kernel)
not ok 167 - (A) frontend vs backend parity: DSG_LA at m=0.0009, center on-grid (delta kernel)
  ---
  duration_ms: 1296.000997
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:218:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:225:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0.0009, center half-step off-grid (delta kernel)
not ok 168 - (A) frontend vs backend parity: DSG_LA at m=0.0009, center half-step off-grid (delta kernel)
  ---
  duration_ms: 1314.642192
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:218:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:225:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, descending grid, off-grid center
not ok 169 - (A) frontend vs backend parity: DSG_LA at m=0, descending grid, off-grid center
  ---
  duration_ms: 1296.163479
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:235:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:242:15)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Gaussian
ok 170 - (B) evalPeak vs evalPeakArray agree pointwise: Gaussian
  ---
  duration_ms: 0.399169
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Lorentzian
ok 171 - (B) evalPeak vs evalPeakArray agree pointwise: Lorentzian
  ---
  duration_ms: 0.20337
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Voigt
ok 172 - (B) evalPeak vs evalPeakArray agree pointwise: Voigt
  ---
  duration_ms: 0.256965
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: GL
ok 173 - (B) evalPeak vs evalPeakArray agree pointwise: GL
  ---
  duration_ms: 0.216741
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: asym-GL
ok 174 - (B) evalPeak vs evalPeakArray agree pointwise: asym-GL
  ---
  duration_ms: 0.220329
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: DS
ok 175 - (B) evalPeak vs evalPeakArray agree pointwise: DS
  ---
  duration_ms: 0.600927
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA
not ok 176 - (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA # TODO evalPeak() DSG_LA branch is the normalised DS core with m IGNORED (the convolution is a grid operation, dsgConvolved_array via evalPeakArray); no shipped caller reaches it — guard (C)
  ---
  duration_ms: 3.546617
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:265:3'
  failureType: 'testCodeFailure'
  error: 'DSG_LA at x=393.3: evalPeak=7298.4050340345175, evalPeakArray[i]=8703.575517573383, rel diff=7.8969%'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:272:12)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: LACX
not ok 177 - (B) evalPeak vs evalPeakArray agree pointwise: LACX # TODO evalPeak() LACX branch ignores m; only its call sites are rerouted in unit-1 commit 2, not evalPeak() itself — see file header
  ---
  duration_ms: 1.146606
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:265:3'
  failureType: 'testCodeFailure'
  error: 'LACX at x=393.3: evalPeak=2863.2353955224326, evalPeakArray[i]=7181.067813111589, rel diff=24.2657%'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:272:12)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: (C) evalPeak() has no direct callers outside evalPeakArray()
ok 178 - (C) evalPeak() has no direct callers outside evalPeakArray()
  ---
  duration_ms: 3.137693
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: Gaussian
not ok 179 - (D) sweep across the fitted range: Gaussian
  ---
  duration_ms: 1243.120554
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: Lorentzian
not ok 180 - (D) sweep across the fitted range: Lorentzian
  ---
  duration_ms: 1264.347131
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: Voigt
not ok 181 - (D) sweep across the fitted range: Voigt
  ---
  duration_ms: 1389.489166
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: GL
not ok 182 - (D) sweep across the fitted range: GL
  ---
  duration_ms: 1312.972603
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: asym-GL
not ok 183 - (D) sweep across the fitted range: asym-GL
  ---
  duration_ms: 1296.734964
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: DS
not ok 184 - (D) sweep across the fitted range: DS
  ---
  duration_ms: 1301.565269
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: DSG_LA (delta kernel)
not ok 185 - (D) sweep across the fitted range: DSG_LA (delta kernel)
  ---
  duration_ms: 1305.124276
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: LACX (m = 0)
not ok 186 - (D) sweep across the fitted range: LACX (m = 0)
  ---
  duration_ms: 1255.004549
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: DSG_LA (m > 0)
not ok 187 - (D) sweep across the fitted range: DSG_LA (m > 0)
  ---
  duration_ms: 1271.668978
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D) sweep across the fitted range: LACX (m > 0)
not ok 188 - (D) sweep across the fitted range: LACX (m > 0)
  ---
  duration_ms: 1324.850588
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: step 0.1 eV, 120 pts
not ok 189 - (D′) DS+G convolution converges on another grid: step 0.1 eV, 120 pts
  ---
  duration_ms: 1277.349563
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: step 0.02 eV, 500 pts
not ok 190 - (D′) DS+G convolution converges on another grid: step 0.02 eV, 500 pts
  ---
  duration_ms: 1257.4934
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: step 0.05 eV, descending
not ok 191 - (D′) DS+G convolution converges on another grid: step 0.05 eV, descending
  ---
  duration_ms: 1254.795841
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: step 0.05 eV, centre half a step off-grid
not ok 192 - (D′) DS+G convolution converges on another grid: step 0.05 eV, centre half a step off-grid
  ---
  duration_ms: 1289.011554
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: step 0.1 eV, descending, centre 0.03 eV off-grid
not ok 193 - (D′) DS+G convolution converges on another grid: step 0.1 eV, descending, centre 0.03 eV off-grid
  ---
  duration_ms: 1296.241933
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: short window: 30 pts at 0.1 eV (narrower than the pad)
not ok 194 - (D′) DS+G convolution converges on another grid: short window: 30 pts at 0.1 eV (narrower than the pad)
  ---
  duration_ms: 1276.0625
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: irregular-ish step 0.0503 eV (median step), 181 pts
not ok 195 - (D′) DS+G convolution converges on another grid: irregular-ish step 0.0503 eV (median step), 181 pts
  ---
  duration_ms: 1257.366029
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D″) DS+G regression: centre 10 eV outside a [−5, 5] window (a free DS+G centre has no window on the server)
not ok 196 - (D″) DS+G regression: centre 10 eV outside a [−5, 5] window (a free DS+G centre has no window on the server)
  ---
  duration_ms: 1297.009176
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: a 6-point irregular grid
not ok 197 - (D″) DS+G regression: a 6-point irregular grid
  ---
  duration_ms: 1290.632837
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: genuinely irregular steps (0.05 / 0.06 alternating; median ≠ mean)
not ok 198 - (D″) DS+G regression: genuinely irregular steps (0.05 / 0.06 alternating; median ≠ mean)
  ---
  duration_ms: 1255.274733
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: a 0.001 eV grid over 10 eV at the box corner β 2, m 4, α 0.49 (13 s per curve in the first cut)
not ok 199 - (D″) DS+G regression: a 0.001 eV grid over 10 eV at the box corner β 2, m 4, α 0.49 (13 s per curve in the first cut)
  ---
  duration_ms: 1360.124403
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D″) DS+G regression: centre 10 eV outside [−5, 5] on a 0.5 eV grid, β 0.05, m 0.05 (Codex round 2 reproducer: was 5e16 × amplitude)
not ok 200 - (D″) DS+G regression: centre 10 eV outside [−5, 5] on a 0.5 eV grid, β 0.05, m 0.05 (Codex round 2 reproducer: was 5e16 × amplitude)
  ---
  duration_ms: 1297.476845
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: centre −10 eV on the low-BE side, 201 points at 0.05 eV, m 0.001
not ok 201 - (D″) DS+G regression: centre −10 eV on the low-BE side, 201 points at 0.05 eV, m 0.001
  ---
  duration_ms: 1267.299179
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: centre just outside the padded grid (6.5 eV, pad 1 eV)
not ok 202 - (D″) DS+G regression: centre just outside the padded grid (6.5 eV, pad 1 eV)
  ---
  duration_ms: 1204.199834
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: centre just inside the padded grid (5.999 eV, pad 1 eV)
not ok 203 - (D″) DS+G regression: centre just inside the padded grid (5.999 eV, pad 1 eV)
  ---
  duration_ms: 1219.059105
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: a 2-point grid
not ok 204 - (D″) DS+G regression: a 2-point grid
  ---
  duration_ms: 1246.707459
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: a 1-point grid
not ok 205 - (D″) DS+G regression: a 1-point grid
  ---
  duration_ms: 1180.232321
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G at m = 0.001 on a 0.1 eV grid: page equals server (both an all-zero curve — the server kernel underflows; known server limit)
not ok 206 - (D″) DS+G at m = 0.001 on a 0.1 eV grid: page equals server (both an all-zero curve — the server kernel underflows; known server limit)
  ---
  duration_ms: 1173.527088
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:471:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:475:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G at m = 0.002 on a 0.1 eV grid: page equals server (both an all-zero curve — the server kernel underflows; known server limit)
not ok 207 - (D″) DS+G at m = 0.002 on a 0.1 eV grid: page equals server (both an all-zero curve — the server kernel underflows; known server limit)
  ---
  duration_ms: 1160.756224
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:471:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:475:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G at m = 0.02 on a 0.1 eV grid: page equals server
not ok 208 - (D″) DS+G at m = 0.02 on a 0.1 eV grid: page equals server
  ---
  duration_ms: 1194.606778
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:471:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:475:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G at m = 0.05 on a 0.1 eV grid: page equals server
not ok 209 - (D″) DS+G at m = 0.05 on a 0.1 eV grid: page equals server
  ---
  duration_ms: 1152.893533
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:471:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:475:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D‴) LA continuous-m convolution matches the server on another grid: step 0.1 eV, 120 pts
not ok 210 - (D‴) LA continuous-m convolution matches the server on another grid: step 0.1 eV, 120 pts
  ---
  duration_ms: 1139.056704
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:499:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:502:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D‴) LA continuous-m convolution matches the server on another grid: step 0.02 eV, 500 pts
not ok 211 - (D‴) LA continuous-m convolution matches the server on another grid: step 0.02 eV, 500 pts
  ---
  duration_ms: 1144.821108
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:499:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:502:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D‴) LA continuous-m convolution matches the server on another grid: step 0.05 eV, descending
not ok 212 - (D‴) LA continuous-m convolution matches the server on another grid: step 0.05 eV, descending
  ---
  duration_ms: 1146.123456
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:499:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:502:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D‴) LA continuous-m convolution matches the server on another grid: step 0.05 eV, centre 0.013 eV off-grid
not ok 213 - (D‴) LA continuous-m convolution matches the server on another grid: step 0.05 eV, centre 0.013 eV off-grid
  ---
  duration_ms: 1233.636618
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:499:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:502:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D‴) LA continuous-m convolution matches the server on another grid: 9 points (kernel longer than the grid for m ≥ 3)
not ok 214 - (D‴) LA continuous-m convolution matches the server on another grid: 9 points (kernel longer than the grid for m ≥ 3)
  ---
  duration_ms: 1190.698379
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:499:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:502:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D‴) LA continuous-m convolution matches the server on another grid: 2 points
not ok 215 - (D‴) LA continuous-m convolution matches the server on another grid: 2 points
  ---
  duration_ms: 1218.742652
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:499:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:502:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Gaussian
not ok 216 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Gaussian
  ---
  duration_ms: 1676.610781
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:120:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:121:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.start (node:internal/test_runner/test:944:17)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
not ok 217 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
  ---
  duration_ms: 1224.233584
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:120:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:121:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
not ok 218 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
  ---
  duration_ms: 1210.416197
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:120:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:121:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
not ok 219 - page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
  ---
  duration_ms: 1190.574919
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:120:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:121:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
not ok 220 - page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
  ---
  duration_ms: 1263.172737
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:120:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:121:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
not ok 221 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
  ---
  duration_ms: 1633.202078
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:120:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:121:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA
not ok 222 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA
  ---
  duration_ms: 1303.764795
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:120:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:121:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — LACX
not ok 223 - page → server → page: what the page draws after applying the result IS the curve the server fitted — LACX
  ---
  duration_ms: 1321.545736
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:120:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:121:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: Voigt is the fixed 50/50 mix on both sides (A03): request, server parameter, page write-back, drawn curve
not ok 224 - Voigt is the fixed 50/50 mix on both sides (A03): request, server parameter, page write-back, drawn curve
  ---
  duration_ms: 1427.514387
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:129:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:136:26)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
not ok 225 - a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
  ---
  duration_ms: 1394.734188
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:144:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:146:26)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 0 locked
not ok 226 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 0 locked
  ---
  duration_ms: 1359.245979
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 100 locked
not ok 227 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 100 locked
  ---
  duration_ms: 1291.522815
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 0 locked
not ok 228 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 0 locked
  ---
  duration_ms: 1316.266058
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 100 locked
not ok 229 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 100 locked
  ---
  duration_ms: 1295.210976
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 0 locked
not ok 230 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 0 locked
  ---
  duration_ms: 1243.87568
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 1 locked
not ok 231 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 1 locked
  ---
  duration_ms: 1270.525069
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0 locked
not ok 232 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0 locked
  ---
  duration_ms: 1398.340364
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0.5 locked
not ok 233 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0.5 locked
  ---
  duration_ms: 1307.895238
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 0 locked
not ok 234 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 0 locked
  ---
  duration_ms: 1296.931253
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 5 locked
not ok 235 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 5 locked
  ---
  duration_ms: 1302.628669
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0 locked (delta kernel)
not ok 236 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0 locked (delta kernel)
  ---
  duration_ms: 1308.078607
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.49 locked (delta kernel)
not ok 237 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.49 locked (delta kernel)
  ---
  duration_ms: 1238.976255
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 0.05 locked (delta kernel)
not ok 238 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 0.05 locked (delta kernel)
  ---
  duration_ms: 1287.983874
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 2 locked (delta kernel)
not ok 239 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 2 locked (delta kernel)
  ---
  duration_ms: 1325.611949
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 0.1 locked (m = 0)
not ok 240 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 0.1 locked (m = 0)
  ---
  duration_ms: 1272.207135
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 5 locked (m = 0)
not ok 241 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 5 locked (m = 0)
  ---
  duration_ms: 1255.957655
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 0.1 locked (m = 0)
not ok 242 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 0.1 locked (m = 0)
  ---
  duration_ms: 1256.913629
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 5 locked (m = 0)
not ok 243 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 5 locked (m = 0)
  ---
  duration_ms: 1279.502016
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.5 locked (delta kernel; both evaluators clip to 0.495)
not ok 244 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.5 locked (delta kernel; both evaluators clip to 0.495)
  ---
  duration_ms: 1303.978939
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 0.05 locked
not ok 245 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 0.05 locked
  ---
  duration_ms: 1272.123059
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 4 locked
not ok 246 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 4 locked
  ---
  duration_ms: 1259.33851
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA m 499 locked
not ok 247 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA m 499 locked
  ---
  duration_ms: 1306.835545
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA m 8.66 locked (a fractional m, as a fit returns it)
not ok 248 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA m 8.66 locked (a fractional m, as a fit returns it)
  ---
  duration_ms: 1281.743721
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: a locked GL mix is sent locked, held by the server and drawn at the locked value
not ok 249 - a locked GL mix is sent locked, held by the server and drawn at the locked value
  ---
  duration_ms: 1257.521803
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:212:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:213:33)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
not ok 250 - autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
  ---
  duration_ms: 1355.305759
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:223:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:231:14)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
not ok 251 - autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
  ---
  duration_ms: 1306.751572
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:241:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:250:14)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/local_lm_server_parity_backend.py", line 12, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Subtest: A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
ok 252 - A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
  ---
  duration_ms: 1482.782148
  type: 'test'
  ...
# Subtest: A01 replay: the linked U 4f pair also descends
ok 253 - A01 replay: the linked U 4f pair also descends
  ---
  duration_ms: 316.630847
  type: 'test'
  ...
# Subtest: noiseless Gaussian: amplitude 10 started at 5 is recovered
ok 254 - noiseless Gaussian: amplitude 10 started at 5 is recovered
  ---
  duration_ms: 13.907534
  type: 'test'
  ...
# Subtest: acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
ok 255 - acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
  ---
  duration_ms: 10.148051
  type: 'test'
  ...
# Subtest: a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
ok 256 - a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
  ---
  duration_ms: 12.264069
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
ok 257 - bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
  ---
  duration_ms: 9.347647
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
ok 258 - bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
  ---
  duration_ms: 8.65273
  type: 'test'
  ...
# Subtest: a weak component the data DO hold is no longer forced up to an amplitude of 1
ok 259 - a weak component the data DO hold is no longer forced up to an amplitude of 1
  ---
  duration_ms: 10.267564
  type: 'test'
  ...
# Subtest: derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
ok 260 - derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
  ---
  duration_ms: 47.56946
  type: 'test'
  ...
# Subtest: derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
ok 261 - derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
  ---
  duration_ms: 25.279216
  type: 'test'
  ...
# Subtest: a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
ok 262 - a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
  ---
  duration_ms: 8.504908
  type: 'test'
  ...
# Subtest: linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
ok 263 - linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
  ---
  duration_ms: 13.957994
  type: 'test'
  ...
# Subtest: round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
ok 264 - round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
  ---
  duration_ms: 14.422211
  type: 'test'
  ...
# Subtest: round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
ok 265 - round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
  ---
  duration_ms: 9.808202
  type: 'test'
  ...
# Subtest: round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
ok 266 - round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
  ---
  duration_ms: 11.12338
  type: 'test'
  ...
# Subtest: A01 replay targets converge to constrained stationary points (C1s and U 4f)
ok 267 - A01 replay targets converge to constrained stationary points (C1s and U 4f)
  ---
  duration_ms: 1555.488691
  type: 'test'
  ...
# Subtest: round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
ok 268 - round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
  ---
  duration_ms: 74.521272
  type: 'test'
  ...
# Subtest: round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
ok 269 - round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
  ---
  duration_ms: 21.526295
  type: 'test'
  ...
# Subtest: round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
ok 270 - round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
  ---
  duration_ms: 14.962993
  type: 'test'
  ...
# Subtest: round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
ok 271 - round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
  ---
  duration_ms: 82.391731
  type: 'test'
  ...
# Subtest: round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
ok 272 - round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
  ---
  duration_ms: 1258.252389
  type: 'test'
  ...
# Subtest: round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
ok 273 - round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
  ---
  duration_ms: 21.351069
  type: 'test'
  ...
# Subtest: round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
ok 274 - round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
  ---
  duration_ms: 10.661228
  type: 'test'
  ...
# Subtest: weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
ok 275 - weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
  ---
  duration_ms: 8.784483
  type: 'test'
  ...
# Subtest: server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
not ok 276 - server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
  ---
  duration_ms: 1616.430972
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/local_lm_descent.test.js:455:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/local_lm_server_parity_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/local_lm_server_parity_backend.py", line 12, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/local_lm_descent.test.js:468:31)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom
ok 277 - the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom
  ---
  duration_ms: 20.604966
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
ok 278 - an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
  ---
  duration_ms: 27.878327
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
ok 279 - an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
  ---
  duration_ms: 20.140952
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
ok 280 - round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
  ---
  duration_ms: 9.115248
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
ok 281 - round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
  ---
  duration_ms: 9.048289
  type: 'test'
  ...
# Subtest: recovery from an amplitude of exactly zero (the new floor is not a trap)
ok 282 - recovery from an amplitude of exactly zero (the new floor is not a trap)
  ---
  duration_ms: 11.590344
  type: 'test'
  ...
# Subtest: plain, indented, multi-declarator, same-line, multiline, ASI declarations
ok 283 - plain, indented, multi-declarator, same-line, multiline, ASI declarations
  ---
  duration_ms: 9.889217
  type: 'test'
  ...
# Subtest: populated containers, ALL_CAPS containers, parenthesised and conditional initialisers
ok 284 - populated containers, ALL_CAPS containers, parenthesised and conditional initialisers
  ---
  duration_ms: 4.035415
  type: 'test'
  ...
# Subtest: destructuring, labelled, unbraced-if, top-level block and static class fields
ok 285 - destructuring, labelled, unbraced-if, top-level block and static class fields
  ---
  duration_ms: 5.564031
  type: 'test'
  ...
# Subtest: function-local declarations and primitive consts are not module state
ok 286 - function-local declarations and primitive consts are not module state
  ---
  duration_ms: 3.501346
  type: 'test'
  ...
# Subtest: comments, strings, regex and nested template literals cannot hide or fake a declaration
ok 287 - comments, strings, regex and nested template literals cannot hide or fake a declaration
  ---
  duration_ms: 2.57929
  type: 'test'
  ...
# Subtest: appending a forbidden declaration to each real inline script is found
ok 288 - appending a forbidden declaration to each real inline script is found
  ---
  duration_ms: 427.654512
  type: 'test'
  ...
# Subtest: destructuring defaults and rest create containers even when the right-hand side is primitive
ok 289 - destructuring defaults and rest create containers even when the right-hand side is primitive
  ---
  duration_ms: 0.306305
  type: 'test'
  ...
# Subtest: static fields with string or computed keys, class expressions and static blocks are reported
ok 290 - static fields with string or computed keys, class expressions and static blocks are reported
  ---
  duration_ms: 0.657809
  type: 'test'
  ...
# Subtest: a const whose initialiser is a class expression WITH static fields is not skipped
ok 291 - a const whose initialiser is a class expression WITH static fields is not skipped
  ---
  duration_ms: 0.43743
  type: 'test'
  ...
# Subtest: static fields on an anonymous superclass expression are attributed to the subclass
ok 292 - static fields on an anonymous superclass expression are attributed to the subclass
  ---
  duration_ms: 0.473073
  type: 'test'
  ...
# Subtest: a static block is reported as a whole, whatever it does
ok 293 - a static block is reported as a whole, whatever it does
  ---
  duration_ms: 0.306611
  type: 'test'
  ...
# Subtest: an unbound class expression with static state is reported under an un-allowlistable name
ok 294 - an unbound class expression with static state is reported under an un-allowlistable name
  ---
  duration_ms: 0.209118
  type: 'test'
  ...
# Subtest: computed class keys are evaluated in the enclosing scope: a class declared inside one is reported
ok 295 - computed class keys are evaluated in the enclosing scope: a class declared inside one is reported
  ---
  duration_ms: 0.71398
  type: 'test'
  ...
# Subtest: catch-clause bindings at module scope are enumerated
ok 296 - catch-clause bindings at module scope are enumerated
  ---
  duration_ms: 0.233789
  type: 'test'
  ...
# Subtest: a RegExp literal is a mutable object, not an immutable constant
ok 297 - a RegExp literal is a mutable object, not an immutable constant
  ---
  duration_ms: 0.122545
  type: 'test'
  ...
# Subtest: a class without static state reports nothing at all
ok 298 - a class without static state reports nothing at all
  ---
  duration_ms: 0.154355
  type: 'test'
  ...
# Subtest: every module-level mutable is allowlisted with a valid non-C class
ok 299 - every module-level mutable is allowlisted with a valid non-C class
  ---
  duration_ms: 251.358192
  type: 'test'
  ...
# Subtest: inherited property names and anonymous-class names cannot slip through the allowlist
ok 300 - inherited property names and anonymous-class names cannot slip through the allowlist
  ---
  duration_ms: 91.684589
  type: 'test'
  ...
# Subtest: the known class-C holders are gone from module scope
ok 301 - the known class-C holders are gone from module scope
  ---
  duration_ms: 6.04561
  type: 'test'
  ...
# Subtest: async operations capture their owning record before the first await
ok 302 - async operations capture their owning record before the first await
  ---
  duration_ms: 2.679957
  type: 'test'
  ...
# Subtest: undo/redo and Find Peaks apply read the ACTIVE tab record only
ok 303 - undo/redo and Find Peaks apply read the ACTIVE tab record only
  ---
  duration_ms: 0.690967
  type: 'test'
  ...
# Subtest: tolFromSlider clamps to [0.25, 5.0] and snaps to 0.25
ok 304 - tolFromSlider clamps to [0.25, 5.0] and snaps to 0.25
  ---
  duration_ms: 1.682387
  type: 'test'
  ...
# Subtest: coerceTolToEv maps legacy modes onto the base, passes numbers through
ok 305 - coerceTolToEv maps legacy modes onto the base, passes numbers through
  ---
  duration_ms: 0.387276
  type: 'test'
  ...
# Subtest: blendedSearch matches elements by symbol/name
ok 306 - blendedSearch matches elements by symbol/name
  ---
  duration_ms: 0.433483
  type: 'test'
  ...
# Subtest: blendedSearch matches compounds, tagged compound
ok 307 - blendedSearch matches compounds, tagged compound
  ---
  duration_ms: 0.288672
  type: 'test'
  ...
# Subtest: blendedSearch numeric query yields energy rows
ok 308 - blendedSearch numeric query yields energy rows
  ---
  duration_ms: 0.312176
  type: 'test'
  ...
# Subtest: blendedSearch caps results and empty query returns []
ok 309 - blendedSearch caps results and empty query returns []
  ---
  duration_ms: 1.083432
  type: 'test'
  ...
# Subtest: parseChemKey: exact spin-orbit key
ok 310 - parseChemKey: exact spin-orbit key
  ---
  duration_ms: 0.673277
  type: 'test'
  ...
# Subtest: parseChemKey: subshell-only p attaches to BOTH spin-orbit lines (Si 2p)
ok 311 - parseChemKey: subshell-only p attaches to BOTH spin-orbit lines (Si 2p)
  ---
  duration_ms: 0.306461
  type: 'test'
  ...
# Subtest: parseChemKey: 1s has no split
ok 312 - parseChemKey: 1s has no split
  ---
  duration_ms: 0.625974
  type: 'test'
  ...
# Subtest: compoundCandidatesFrom returns legacy candidates within tol, honest proximity
ok 313 - compoundCandidatesFrom returns legacy candidates within tol, honest proximity
  ---
  duration_ms: 1.925226
  type: 'test'
  ...
# Subtest: capConfidenceByTier: curated/machine keep candidate label + raw energyMatch
ok 314 - capConfidenceByTier: curated/machine keep candidate label + raw energyMatch
  ---
  duration_ms: 0.233506
  type: 'test'
  ...
# Subtest: capConfidenceByTier: legacy noun is "Legacy hint", energy annotated, never Strong
ok 315 - capConfidenceByTier: legacy noun is "Legacy hint", energy annotated, never Strong
  ---
  duration_ms: 0.112331
  type: 'test'
  ...
# Subtest: mergeAndRankCandidates: element-only golden order is Δ-primary
ok 316 - mergeAndRankCandidates: element-only golden order is Δ-primary
  ---
  duration_ms: 0.322842
  type: 'test'
  ...
# Subtest: adding compounds does not perturb the element subsequence
ok 317 - adding compounds does not perturb the element subsequence
  ---
  duration_ms: 0.216094
  type: 'test'
  ...
# Subtest: mergeAndRankCandidates: a clear Δ winner ranks first regardless of tier
ok 318 - mergeAndRankCandidates: a clear Δ winner ranks first regardless of tier
  ---
  duration_ms: 0.157768
  type: 'test'
  ...
# Subtest: augerApparentBE shifts with source; photoelectronBE is source-invariant
ok 319 - augerApparentBE shifts with source; photoelectronBE is source-invariant
  ---
  duration_ms: 0.22812
  type: 'test'
  ...
# Subtest: compound BE equals input be_ev (no ccShift, source-invariant)
ok 320 - compound BE equals input be_ev (no ccShift, source-invariant)
  ---
  duration_ms: 0.310594
  type: 'test'
  ...
# Subtest: elementOverlayVisible no longer depends on the palette being open
ok 321 - elementOverlayVisible no longer depends on the palette being open
  ---
  duration_ms: 0.242668
  type: 'test'
  ...
# Subtest: tierColor is a single source of truth for the three data tiers
ok 322 - tierColor is a single source of truth for the three data tiers
  ---
  duration_ms: 0.184836
  type: 'test'
  ...
# Subtest: tierColor falls back safely for unknown/missing tiers
ok 323 - tierColor falls back safely for unknown/missing tiers
  ---
  duration_ms: 0.126074
  type: 'test'
  ...
# Subtest: tierNote is the single source for tier wording; reviewed text is canonical
ok 324 - tierNote is the single source for tier wording; reviewed text is canonical
  ---
  duration_ms: 0.158422
  type: 'test'
  ...
# Subtest: nextColorIdx returns the first index whose palette residue is unused
ok 325 - nextColorIdx returns the first index whose palette residue is unused
  ---
  duration_ms: 0.203481
  type: 'test'
  ...
# Subtest: nextColorIdx falls back to max(used)+1 once every residue is taken
ok 326 - nextColorIdx falls back to max(used)+1 once every residue is taken
  ---
  duration_ms: 0.13674
  type: 'test'
  ...
# Subtest: nextColorIdx: a new pick shares no rendered residue with existing overlays (while residues remain)
ok 327 - nextColorIdx: a new pick shares no rendered residue with existing overlays (while residues remain)
  ---
  duration_ms: 0.158985
  type: 'test'
  ...
# Subtest: nextColorIdx ignores invalid entries (non-integer/negative) when computing the used set
ok 328 - nextColorIdx ignores invalid entries (non-integer/negative) when computing the used set
  ---
  duration_ms: 0.137457
  type: 'test'
  ...
# Subtest: clampToViewport: an in-bounds position passes through unchanged
ok 329 - clampToViewport: an in-bounds position passes through unchanged
  ---
  duration_ms: 0.220523
  type: 'test'
  ...
# Subtest: clampToViewport: negative / above-left position clamps to the margin
ok 330 - clampToViewport: negative / above-left position clamps to the margin
  ---
  duration_ms: 0.139183
  type: 'test'
  ...
# Subtest: clampToViewport: far off-screen (stale) position clamps inside the viewport
ok 331 - clampToViewport: far off-screen (stale) position clamps inside the viewport
  ---
  duration_ms: 0.130095
  type: 'test'
  ...
# Subtest: clampToViewport: non-finite (corrupt saved) coords fall back to the margin
ok 332 - clampToViewport: non-finite (corrupt saved) coords fall back to the margin
  ---
  duration_ms: 0.138289
  type: 'test'
  ...
# Subtest: overlays and compound markers have independent (decoupled) version constants
ok 333 - overlays and compound markers have independent (decoupled) version constants
  ---
  duration_ms: 0.122999
  type: 'test'
  ...
# Subtest: serializeRefOverlays is total: null for empty/nullish/malformed sel
ok 334 - serializeRefOverlays is total: null for empty/nullish/malformed sel
  ---
  duration_ms: 0.220244
  type: 'test'
  ...
# Subtest: serializeRefOverlays captures selection and never emits identify keys
ok 335 - serializeRefOverlays captures selection and never emits identify keys
  ---
  duration_ms: 0.212873
  type: 'test'
  ...
# Subtest: round-trip preserves a valid colorIdx verbatim
ok 336 - round-trip preserves a valid colorIdx verbatim
  ---
  duration_ms: 0.295297
  type: 'test'
  ...
# Subtest: deserialize: absent or envelope-malformed → clean empty (no throw)
ok 337 - deserialize: absent or envelope-malformed → clean empty (no throw)
  ---
  duration_ms: 0.234258
  type: 'test'
  ...
# Subtest: deserialize: newer internal version is ignored (no misread of a future shape)
ok 338 - deserialize: newer internal version is ignored (no misread of a future shape)
  ---
  duration_ms: 0.265551
  type: 'test'
  ...
# Subtest: deserialize entry repair: keep valid, skip no-sym, repair invalid colorIdx, keep unknown tier
ok 339 - deserialize entry repair: keep valid, skip no-sym, repair invalid colorIdx, keep unknown tier
  ---
  duration_ms: 0.245914
  type: 'test'
  ...
# Subtest: post-load next pick renders a color distinct from all restored while residues remain
ok 340 - post-load next pick renders a color distinct from all restored while residues remain
  ---
  duration_ms: 0.145055
  type: 'test'
  ...
# Subtest: serializeRefCompoundMarkers is total: null for empty/nullish/non-array
ok 341 - serializeRefCompoundMarkers is total: null for empty/nullish/non-array
  ---
  duration_ms: 0.141582
  type: 'test'
  ...
# Subtest: serializeRefCompoundMarkers is total for malformed ARRAY ENTRIES (no throw; all-invalid → null)
ok 342 - serializeRefCompoundMarkers is total for malformed ARRAY ENTRIES (no throw; all-invalid → null)
  ---
  duration_ms: 0.133753
  type: 'test'
  ...
# Subtest: serializeRefCompoundMarkers: mixed valid+invalid → invalid be dropped, valid kept
ok 343 - serializeRefCompoundMarkers: mixed valid+invalid → invalid be dropped, valid kept
  ---
  duration_ms: 0.223887
  type: 'test'
  ...
# Subtest: compound markers round-trip at global scope; absent/malformed/newer → empty
ok 344 - compound markers round-trip at global scope; absent/malformed/newer → empty
  ---
  duration_ms: 0.28025
  type: 'test'
  ...
# Subtest: compound markers: non-finite be dropped, absent sym tolerated (partial-invalid)
ok 345 - compound markers: non-finite be dropped, absent sym tolerated (partial-invalid)
  ---
  duration_ms: 0.195205
  type: 'test'
  ...
# Subtest: an ROI inside the data: no hint
ok 346 - an ROI inside the data: no hint
  ---
  duration_ms: 8.865558
  type: 'test'
  ...
# Subtest: an ROI past the data by more than one step: the quiet hint names the window actually used
ok 347 - an ROI past the data by more than one step: the quiet hint names the window actually used
  ---
  duration_ms: 5.309491
  type: 'test'
  ...
# Subtest: one side past the data is enough; the window named is the selected data
ok 348 - one side past the data is enough; the window named is the selected data
  ---
  duration_ms: 4.609894
  type: 'test'
  ...
# Subtest: a sub-step overshoot (a toFixed(1) rounding of the data edge) is not "past the data"
ok 349 - a sub-step overshoot (a toFixed(1) rounding of the data edge) is not "past the data"
  ---
  duration_ms: 5.720868
  type: 'test'
  ...
# Subtest: min above max: amber, no data selected (getROIData selects nothing)
ok 350 - min above max: amber, no data selected (getROIData selects nothing)
  ---
  duration_ms: 7.704556
  type: 'test'
  ...
# Subtest: an ROI that misses the data entirely: amber, names the data range
ok 351 - an ROI that misses the data entirely: amber, names the data range
  ---
  duration_ms: 3.155767
  type: 'test'
  ...
# Subtest: empty fields mean the full range (as getROIData): no hint
ok 352 - empty fields mean the full range (as getROIData): no hint
  ---
  duration_ms: 3.165769
  type: 'test'
  ...
# Subtest: the window is in the CORRECTED frame (raw − ccShift), as the fit and Find Peaks use it
ok 353 - the window is in the CORRECTED frame (raw − ccShift), as the fit and Find Peaks use it
  ---
  duration_ms: 7.170896
  type: 'test'
  ...
# Subtest: a descending acquisition behaves the same
ok 354 - a descending acquisition behaves the same
  ---
  duration_ms: 4.057893
  type: 'test'
  ...
# Subtest: centre outside the SELECTED data is flagged; inside, at the edges, or with no data selected is not
ok 355 - centre outside the SELECTED data is flagged; inside, at the edges, or with no data selected is not
  ---
  duration_ms: 7.760522
  type: 'test'
  ...
# Subtest: the helpers write nothing: no assignment to a field value, a peak or the fit state
ok 356 - the helpers write nothing: no assignment to a field value, a peak or the fit state
  ---
  duration_ms: 3.384572
  type: 'test'
  ...
# Subtest: the fit and Find Peaks still read the ROI exactly as before (getROIData / the two field values)
ok 357 - the fit and Find Peaks still read the ROI exactly as before (getROIData / the two field values)
  ---
  duration_ms: 2.827018
  type: 'test'
  ...
# Subtest: an unsupported component: the badge warns without reporting its suppressed centre
ok 358 - an unsupported component: the badge warns without reporting its suppressed centre
  ---
  duration_ms: 4.487929
  type: 'test'
  ...
# Subtest: manual fit and Find Peaks select the same points whenever no energy lies within 5e-5 eV of an ROI edge
ok 359 - manual fit and Find Peaks select the same points whenever no energy lies within 5e-5 eV of an ROI edge
  ---
  duration_ms: 14.761484
  type: 'test'
  ...
# Subtest: …and can differ by one edge point, IN EITHER DIRECTION, when an energy lies within 5e-5 eV of an edge (pre-existing, logged, not changed)
ok 360 - …and can differ by one edge point, IN EITHER DIRECTION, when an energy lies within 5e-5 eV of an edge (pre-existing, logged, not changed)
  ---
  duration_ms: 7.43142
  type: 'test'
  ...
# Subtest: summary wording: counts of STARTS and of SOLUTIONS, never certification
ok 361 - summary wording: counts of STARTS and of SOLUTIONS, never certification
  ---
  duration_ms: 33.24831
  type: 'test'
  ...
# Subtest: no alternative: one line, no table
ok 362 - no alternative: one line, no table
  ---
  duration_ms: 29.362649
  type: 'test'
  ...
# Subtest: alternatives: "Your fit" first, own areas per component, the moved component named and coloured
ok 363 - alternatives: "Your fit" first, own areas per component, the moved component named and coloured
  ---
  duration_ms: 14.511079
  type: 'test'
  ...
# Subtest: RED band: applying asks first and NAMES the component and the distance
ok 364 - RED band: applying asks first and NAMES the component and the distance
  ---
  duration_ms: 11.558043
  type: 'test'
  ...
# Subtest: adoption never writes the live model itself: the alternative is only the START of a fit, and the choice rides along
ok 365 - adoption never writes the live model itself: the alternative is only the START of a fit, and the choice rides along
  ---
  duration_ms: 12.758398
  type: 'test'
  ...
# Subtest: below the red band there is no dialog
ok 366 - below the red band there is no dialog
  ---
  duration_ms: 32.760153
  type: 'test'
  ...
# Subtest: a locked parameter is never moved by an alternative
ok 367 - a locked parameter is never moved by an alternative
  ---
  duration_ms: 10.494474
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a peak deleted: the panel says so and nothing can be applied
ok 368 - evidence is bound to the fitted model — a peak deleted: the panel says so and nothing can be applied
  ---
  duration_ms: 11.841461
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a shape changed (GL -> DS) and the centre moved: the panel says so and nothing can be applied
ok 369 - evidence is bound to the fitted model — a shape changed (GL -> DS) and the centre moved: the panel says so and nothing can be applied
  ---
  duration_ms: 10.300958
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a lock toggled: the panel says so and nothing can be applied
ok 370 - evidence is bound to the fitted model — a lock toggled: the panel says so and nothing can be applied
  ---
  duration_ms: 11.179086
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a link added: the panel says so and nothing can be applied
ok 371 - evidence is bound to the fitted model — a link added: the panel says so and nothing can be applied
  ---
  duration_ms: 10.264213
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — an undo that restored other values: the panel says so and nothing can be applied
ok 372 - evidence is bound to the fitted model — an undo that restored other values: the panel says so and nothing can be applied
  ---
  duration_ms: 9.729002
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — an auto-fit asymmetry bound changed: the panel says so and nothing can be applied
ok 373 - evidence is bound to the fitted model — an auto-fit asymmetry bound changed: the panel says so and nothing can be applied
  ---
  duration_ms: 7.705485
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — the background type changed: the panel says so and nothing can be applied
ok 374 - evidence is bound to the fitted model — the background type changed: the panel says so and nothing can be applied
  ---
  duration_ms: 8.113596
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — the background window moved: the panel says so and nothing can be applied
ok 375 - evidence is bound to the fitted model — the background window moved: the panel says so and nothing can be applied
  ---
  duration_ms: 11.389749
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — endpoint averaging changed: the panel says so and nothing can be applied
ok 376 - evidence is bound to the fitted model — endpoint averaging changed: the panel says so and nothing can be applied
  ---
  duration_ms: 9.207061
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — the ROI changed: the panel says so and nothing can be applied
ok 377 - evidence is bound to the fitted model — the ROI changed: the panel says so and nothing can be applied
  ---
  duration_ms: 7.951704
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a manual anchor was added: the panel says so and nothing can be applied
ok 378 - evidence is bound to the fitted model — a manual anchor was added: the panel says so and nothing can be applied
  ---
  duration_ms: 7.51376
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — the charge correction changed: the panel says so and nothing can be applied
ok 379 - evidence is bound to the fitted model — the charge correction changed: the panel says so and nothing can be applied
  ---
  duration_ms: 8.271497
  type: 'test'
  ...
# Subtest: a cosmetic edit (name, colour, visibility) does not invalidate the evidence
ok 380 - a cosmetic edit (name, colour, visibility) does not invalidate the evidence
  ---
  duration_ms: 7.547626
  type: 'test'
  ...
# Subtest: preview overlays a COPY and toggles off; the model is untouched
ok 381 - preview overlays a COPY and toggles off; the model is untouched
  ---
  duration_ms: 7.494515
  type: 'test'
  ...
# Subtest: a record is keyed like the live tab (project save of a non-active tab)
ok 382 - a record is keyed like the live tab (project save of a non-active tab)
  ---
  duration_ms: 7.742123
  type: 'test'
  ...
# Subtest: what is saved: the counts, never the alternatives' parameter sets
ok 383 - what is saved: the counts, never the alternatives' parameter sets
  ---
  duration_ms: 7.525694
  type: 'test'
  ...
# Subtest: a loaded summary (no parameter sets) still renders its line and offers nothing to apply
ok 384 - a loaded summary (no parameter sets) still renders its line and offers nothing to apply
  ---
  duration_ms: 8.011139
  type: 'test'
  ...
# Subtest: wiring: the trigger is decided with the other request inputs, BEFORE the first await
ok 385 - wiring: the trigger is decided with the other request inputs, BEFORE the first await
  ---
  duration_ms: 11.797697
  type: 'test'
  ...
# Subtest: persistence and export sites carry the summary
ok 386 - persistence and export sites carry the summary
  ---
  duration_ms: 2.253648
  type: 'test'
  ...
# Subtest: the tooltip reports what the starts found and claims nothing about the data
ok 387 - the tooltip reports what the starts found and claims nothing about the data
  ---
  duration_ms: 0.609874
  type: 'test'
  ...
# Subtest: the recorded adoption is worded once, for the exports
ok 388 - the recorded adoption is worded once, for the exports
  ---
  duration_ms: 7.794961
  type: 'test'
  ...
# Subtest: round-trip A -> B -> A restores every ACTIVE parameter (all shapes)
ok 389 - round-trip A -> B -> A restores every ACTIVE parameter (all shapes)
  ---
  duration_ms: 4.340792
  type: 'test'
  ...
# Subtest: DS+G -> GL -> DS+G leaves laAlpha/laBeta/laM and the curve unchanged
ok 390 - DS+G -> GL -> DS+G leaves laAlpha/laBeta/laM and the curve unchanged
  ---
  duration_ms: 23.564897
  type: 'test'
  ...
# Subtest: switching carries the effective eV width, both directions of laM<->fwhm
ok 391 - switching carries the effective eV width, both directions of laM<->fwhm
  ---
  duration_ms: 0.306579
  type: 'test'
  ...
# Subtest: a genuinely-new param is defaulted; a carried-over one is preserved
ok 392 - a genuinely-new param is defaulted; a carried-over one is preserved
  ---
  duration_ms: 0.211013
  type: 'test'
  ...
# Subtest: export columns read the ACTIVE shape, never a stale accumulated param
ok 393 - export columns read the ACTIVE shape, never a stale accumulated param
  ---
  duration_ms: 0.368929
  type: 'test'
  ...
# Subtest: multi-hop round-trip DS+G -> LACX -> GL -> DS+G restores active params
ok 394 - multi-hop round-trip DS+G -> LACX -> GL -> DS+G restores active params
  ---
  duration_ms: 8.343841
  type: 'test'
  ...
# Subtest: loss-kernel response peaks ~23.4 eV above a delta-like peak
ok 395 - loss-kernel response peaks ~23.4 eV above a delta-like peak
  ---
  duration_ms: 28.838192
  type: 'test'
  ...
# Subtest: ascending and descending BE input give the identical background
ok 396 - ascending and descending BE input give the identical background
  ---
  duration_ms: 1.206372
  type: 'test'
  ...
# Subtest: background meets the data at BOTH edges (high-BE anchor, low-BE C0)
ok 397 - background meets the data at BOTH edges (high-BE anchor, low-BE C0)
  ---
  duration_ms: 0.756909
  type: 'test'
  ...
# Subtest: flat window yields no phantom signal (F1 regression pin)
ok 398 - flat window yields no phantom signal (F1 regression pin)
  ---
  duration_ms: 6.712324
  type: 'test'
  ...
# Subtest: agrees with the backend implementation (fitting.py) on the same spectrum
ok 399 - agrees with the backend implementation (fitting.py) on the same spectrum
  ---
  duration_ms: 7.090359
  type: 'test'
  ...
# Subtest: computeBackgroundCore applies endpoint averaging for tougaard (both branches)
ok 400 - computeBackgroundCore applies endpoint averaging for tougaard (both branches)
  ---
  duration_ms: 1.634569
  type: 'test'
  ...
# Subtest: the twin reproduces the server verdict on real responses, and defers to the server field when present
ok 401 - the twin reproduces the server verdict on real responses, and defers to the server field when present
  ---
  duration_ms: 17.488362
  type: 'test'
  ...
# Subtest: _applySupport writes every peak, follows ancestry to the root, stamps the fit key, and leaves null where the response says nothing
ok 402 - _applySupport writes every peak, follows ancestry to the root, stamps the fit key, and leaves null where the response says nothing
  ---
  duration_ms: 9.525795
  type: 'test'
  ...
# Subtest: the verdict applies only to the model and context it was computed for
ok 403 - the verdict applies only to the model and context it was computed for
  ---
  duration_ms: 9.301542
  type: 'test'
  ...
# Subtest: the local engine computes the same statistic from its own residuals
ok 404 - the local engine computes the same statistic from its own residuals
  ---
  duration_ms: 10.890365
  type: 'test'
  ...
# Subtest: sidebar card: badge; centre and width shown as a dash; area % excluded and the others renormalised
ok 405 - sidebar card: badge; centre and width shown as a dash; area % excluded and the others renormalised
  ---
  duration_ms: 18.877529
  type: 'test'
  ...
# Subtest: results table: greyed row, no centre / width / sigma, area kept, percentage dash, and the note beneath
ok 406 - results table: greyed row, no centre / width / sigma, area kept, percentage dash, and the note beneath
  ---
  duration_ms: 20.684063
  type: 'test'
  ...
# Subtest: uncertainty panel: one rule-0 warning for the component, no per-parameter alarms and no "locked" note for it
ok 407 - uncertainty panel: one rule-0 warning for the component, no per-parameter alarms and no "locked" note for it
  ---
  duration_ms: 7.181513
  type: 'test'
  ...
# Subtest: Quantify: excluded from the body, listed beneath with the reason; total and percentages over the rest
ok 408 - Quantify: excluded from the body, listed beneath with the reason; total and percentages over the rest
  ---
  duration_ms: 8.841388
  type: 'test'
  ...
# Subtest: CSV / XLSX export: Status column, suppressed cells, At% empty, WARNING line
ok 409 - CSV / XLSX export: Status column, suppressed cells, At% empty, WARNING line
  ---
  duration_ms: 8.897359
  type: 'test'
  ...
# Subtest: publication figure: no label at the (zero) component, legend entry says so; chart and stack labels say so
ok 410 - publication figure: no label at the (zero) component, legend entry says so; chart and stack labels say so
  ---
  duration_ms: 2.669329
  type: 'test'
  ...
# Subtest: write-back: a server result sets support; the local engine and a propagated model reset it
ok 411 - write-back: a server result sets support; the local engine and a propagated model reset it
  ---
  duration_ms: 1.60619
  type: 'test'
  ...
# Subtest: persistence: support travels with the peak object through every save (the peak is spread whole)
ok 412 - persistence: support travels with the peak object through every save (the peak is spread whole)
  ---
  duration_ms: 1.147874
  type: 'test'
  ...
# Subtest: CSV / XLSX: an unsupported DS+G component exports no width of any kind (beta, m)
ok 413 - CSV / XLSX: an unsupported DS+G component exports no width of any kind (beta, m)
  ---
  duration_ms: 6.590495
  type: 'test'
  ...
# Subtest: the scattered-starts table: an unsupported component shows neither area % nor a move in "Your fit", and is not the largest move
ok 414 - the scattered-starts table: an unsupported component shows neither area % nor a move in "Your fit", and is not the largest move
  ---
  duration_ms: 6.328204
  type: 'test'
  ...
# Subtest: exports: a stale or keyless verdict is "not established", never "supported"
ok 415 - exports: a stale or keyless verdict is "not established", never "supported"
  ---
  duration_ms: 8.183928
  type: 'test'
  ...
# Subtest: Auto-Fit finalisation (locks, charge shift) keeps its own verdicts: _restampSupport, called after the locks
ok 416 - Auto-Fit finalisation (locks, charge shift) keeps its own verdicts: _restampSupport, called after the locks
  ---
  duration_ms: 4.553619
  type: 'test'
  ...
# Subtest: a .fit.json import onto this tab's data carries no verdict
ok 417 - a .fit.json import onto this tab's data carries no verdict
  ---
  duration_ms: 0.184096
  type: 'test'
  ...
# Subtest: _isUnsupported is never handed an array index as its key (Array.filter passes one)
ok 418 - _isUnsupported is never handed an array index as its key (Array.filter passes one)
  ---
  duration_ms: 4.871894
  type: 'test'
  ...
# Subtest: a key change re-renders every consumer of the verdict — each compared with ITS OWN rendering
ok 419 - a key change re-renders every consumer of the verdict — each compared with ITS OWN rendering
  ---
  duration_ms: 3.104443
  type: 'test'
  ...
# Subtest: stack tabs judge a source component against the SOURCE record's key
ok 420 - stack tabs judge a source component against the SOURCE record's key
  ---
  duration_ms: 4.058532
  type: 'test'
  ...
# Subtest: "Your fit" percentages are over supported components; an empty Quantify shows no 100 %
ok 421 - "Your fit" percentages are over supported components; an empty Quantify shows no 100 %
  ---
  duration_ms: 11.728228
  type: 'test'
  ...
# Subtest: the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
ok 422 - the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
  ---
  duration_ms: 4.599518
  type: 'test'
  ...
1..422
# tests 422
# suites 0
# pass 332
# fail 88
# cancelled 0
# skipped 0
# todo 2
# duration_ms 65394.547709

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const cp=require(\"node:child_process\"),orig=cp.execFileSync;
cp.execFileSync=function(exe,args,opts) {
if (/python/.test(exe)) {
if(args[0]===\"-c\") args=[\"-c\",'\\''import tempfile; tempfile.tempdir=\"/tmp\";\\n'\\''+args[1],...args.slice(2)];
else args=[\"-c\",'\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name=\"__main__\")'\\'',...args];
} return orig.call(this,exe,args,opts);
};
require(\"./tests/js/lineshape_parity.test.js\");
require(\"./tests/js/lineshape_roundtrip.test.js\");
require(\"./tests/js/local_lm_descent.test.js\");' 2>&1 | tail -30" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
exec
/bin/zsh -lc "node -e 'const fs=require(\"fs\");for(const n of [\"lacx_page_vs_server_before\",\"lacx_page_vs_server_after\"]) console.log(n,JSON.parse(fs.readFileSync(\"docs/findings/cam/\"+n+\".json\")).summary);const d=JSON.parse(fs.readFileSync(\"docs/findings/cam/local_server_gap_after_cam.json\"));console.log(\"generated\",d.generated);for(const r of d.regions.U4f) console.log(r.target, r.local_success,r.server_success,r.server_held_m_success,\"chi %\",100*(r.local_chi2r/r.server_chi2r-1),\"held chi %\",100*(r.local_chi2r/r.server_held_m_chi2r-1),\"area\",r.max_dArea_pct,\"held area\",r.held_max_dArea_pct,\"held frac\",r.held_max_dFrac_pp,\"held m\",r.comps.filter(c=>c.shape===\"LACX\").map(c=>c.server_held_m.caM));'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 0ms:
lacx_page_vs_server_before {
  components: 108,
  integer_caM: 2,
  locked: 1,
  maxDiffRel: { n: 108, median: 0.0029393802197173954, max: 0.009675094022976498 },
  absDAreaPct: { n: 108, median: 0.326438717198263, max: 1.1833775199967866 }
}
lacx_page_vs_server_after {
  components: 108,
  integer_caM: 2,
  locked: 1,
  maxDiffRel: { n: 108, median: 3.2301494382596917e-16, max: 7.3638750138241e-16 },
  absDAreaPct: {
    n: 108,
    median: 1.1102230246251565e-14,
    max: 5.551115123125783e-14
  }
}
generated 2026-09-26T04:11:27.077Z
U4f Scan_0 true true true chi % 0.5511483068738388 held chi % 0.8435110633362886 area 0.5307123787363976 held area 0.3155218091766554 held frac 0.014075207596096762 held m [ 8.19934520780095, 8.19934520780095 ]
U4f Scan_1 true true true chi % 1.3763435567495597 held chi % 1.6736643190603306 area 2.2219095760906082 held area 2.123477281292907 held frac 0.11930388964426358 held m [ 8.19934520780095, 8.19934520780095 ]
U4f Scan_2 true true true chi % -0.1914270323305156 held chi % 0.09870929659896444 area 0.23788202473383757 held area 0.43868494069344566 held frac 0.020981595895175342 held m [ 8.19934520780095, 8.19934520780095 ]
U4f Scan_3 true true true chi % 0.13136951267045394 held chi % 0.10781924468465931 area 2.0728283603072994 held area 0.43362654400885825 held frac 0.018738751400120685 held m [ 8.19934520780095, 8.19934520780095 ]
U4f Scan_4 true true true chi % 10.124063057231169 held chi % 5.437529148852116 area 8.642295774210496 held area 5.340966018511029 held frac 0.19073521442046076 held m [ 8.19934520780095, 8.19934520780095 ]
U4f Scan_5 true true true chi % 10.36531413339512 held chi % 9.724966194862406 area 6.812618017679539 held area 5.48800706426158 held frac 0.2422065329392209 held m [ 8.19934520780095, 8.19934520780095 ]
U4f Scan_6 true true true chi % -4.7601911721179 held chi % 1.1482443559552413 area 8.616501378063157 held area 1.6008787373444022 held frac 0.0670006343067478 held m [ 8.19934520780095, 8.19934520780095 ]
U4f Scan_7 true true true chi % 0.4829194150065108 held chi % 0.7702415387472072 area 0.8534414290346737 held area 0.5994526745550233 held frac 0.03661977782453557 held m [ 8.19934520780095, 8.19934520780095 ]
U4f Scan_8 true true true chi % 12.841348472560178 held chi % 13.157026983530763 area 8.467174209190699 held area 8.233192126175371 held frac 0.3203886203584465 held m [ 8.19934520780095, 8.19934520780095 ]

exec
/bin/zsh -lc "node -e 'const fs=require(\"fs\"),cp=require(\"child_process\"),path=require(\"path\"),assert=require(\"assert/strict\");
const head=fs.readFileSync(\"templates/index.html\",\"utf8\");
const base=cp.execFileSync(\"git\",[\"show\",\"main:templates/index.html\"],{encoding:\"utf8\",maxBuffer:5e6});
const testSrc=fs.readFileSync(\"tests/js/local_lm_descent.test.js\",\"utf8\").split(\"// ── Committed lab project\")[0].replace(/const html = fs.readFileSync["'^'"\\n]+/,\"\");
function env(html){return new Function(\"require\",\"__dirname\",\"html\",testSrc+\"\\nreturn makeEnv();\")(require,path.resolve(\"tests/js\"),html);}
function local(s){return s.slice(s.indexOf(\"function runFitLocal(\"),s.indexOf(\"\\nfunction solveLinear(\"));}
const baseline=head.replace(local(head),local(base));
const be=Array.from({length:101},(_,i)=>280+0.05*i),bg=be.map(()=>20);
let compared=0;
for(const m of [0,0.001,1,6,8.2,48,499]) for(const fixCaM of [true,false]){
 if("'!fixCaM&&!Number.isInteger(m))continue;
 const a=env(head),b=env(baseline);
 const p={id:1,name:"parent",shape:"LACX",center:282.513,fwhm:0.8,amplitude:5000,caAlpha:1.2,caBeta:1.5,caM:m,fixCaM,fixCaAlpha:true,fixCaBeta:true,fixFwhm:true,fixCenter:true};
 const truth=[p,{...p,id:2,name:"child",linked:1,linkOffset:1,linkRatio:0.5,center:p.center+1,amplitude:2500}];
 const data=a.evalAllPeaks(be,truth).map((v,i)=>v+0.1*Math.sin(3*i));
 for(const e of [a,b])e.state.peaks=[{...p,amplitude:4600},{...truth[1],caM:123.456}];
 const ar=a.runFitLocal(be,data,bg),br=b.runFitLocal(be,data,bg);
 assert.equal(ar.success,true);assert.equal(br.success,true);
 assert.equal(a.state.peaks[1].caM,m);
 assert.equal(a.state.fitResult.chi,b.state.fitResult.chi);
 assert.equal(a.state.peaks[0].amplitude,b.state.peaks[0].amplitude);
 assert.equal(a.state.fitResult.chi/a.state.fitResult.chiReduced,be.length-1);
 assert.equal(a.state.peaks[0].support.p,1);
 compared++;
}
console.log("identical main-vs-HEAD optimiser results with shared evaluator:",compared,"cases; exact linked-child m, dof and component support p verified");
for(const fixCaM of [true,false]){
 const e=env(head),p={id:1,shape:"LACX",center:282.5,fwhm:0.8,amplitude:4000,caAlpha:1.2,caBeta:1.5,caM:5.37,fixCaM,fixCaAlpha:true,fixCaBeta:true,fixFwhm:true,fixCenter:true,fixAmplitude:true};
 e.state.peaks=[p];const d=e.evalAllPeaks(be,[{...p,amplitude:5000}]);const out=e.runFitLocal(be,d,bg);assert.equal(out.success,true);assert.equal(e.state.peaks[0].caM,5.37);assert.equal(e.state.fitResult.chi/e.state.fitResult.chiReduced,be.length);
}
console.log("zero-free-parameter LA cases preserve 5.37 and zero dof for m");'"'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 exited 1 in 40ms:
node:assert:150
  throw new AssertionError(obj);
  ^

AssertionError [ERR_ASSERTION]: Expected values to be strictly equal:

undefined !== 1

    at [eval]:23:9
    at runScriptInThisContext (node:internal/vm:209:10)
    at node:internal/process/execution:446:12
    at [eval]-wrapper:6:24
    at runScriptInContext (node:internal/process/execution:444:60)
    at evalFunction (node:internal/process/execution:279:30)
    at evalTypeScript (node:internal/process/execution:291:3)
    at node:internal/main/eval_string:74:3 {
  generatedMessage: true,
  code: 'ERR_ASSERTION',
  actual: undefined,
  expected: 1,
  operator: 'strictEqual',
  diff: 'simple'
}

Node.js v22.22.2

codex
The committed JSON matches the plan’s re-measurement table, including the held-server value `8.19934520780095`. The first suite run hit a read-only sandbox limitation: Python’s import-time temporary-directory probe failed. I’m rerunning the relevant tests with an in-memory adjustment that avoids that probe; repository files remain untouched.

exec
/bin/zsh -lc "sed -n '7160,7220p' templates/index.html; rg -n 'laTrueCasaXPS_array|_laKernelHalf|caM' tests/js/*.js | wc -l; git log -4 --oneline" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 0ms:
// or excluded; a new fit writes a new verdict. null = not established (no
// converged fit of this model yet, or a fit older than this unit).
const _SUPPORT_MIN_F = 10;
const _UNSUPPORTED_LABEL = 'not supported by the data';
const _UNSUPPORTED_TIP = 'With the other components held at their fitted values, removing this component does not make the fit to the data significantly worse (F < 10), so this fit did not determine it: its centre, width and uncertainties are not reported. This is an outcome of the fit, not a bug, and it is conditional on the other components. The data may still contain the species: try a different starting position or width, or lock the centre where chemistry says it belongs, and refit. Known limit: a gross single-channel artefact in the region can produce this verdict for a real component.';
// The statistic, from residuals of the fit (counts − fitted) and the component's curve.
function _componentSupportCore(counts, fitted, comp, weights, nFreeComp, nFreeTotal) {
  let withC = 0, withoutC = 0, used = 0;
  for (let i = 0; i < counts.length; i++) {
    if (!Number.isFinite(counts[i]) || !Number.isFinite(fitted[i]) || !Number.isFinite(comp[i])) continue;
    const w2 = weights[i] * weights[i], r = counts[i] - fitted[i];
    withC += w2 * r * r; withoutC += w2 * (r + comp[i]) * (r + comp[i]); used++;
  }
  const delta = withoutC - withC, p = Math.max(1, nFreeComp), dof = Math.max(1, used - nFreeTotal);
  const f = delta <= 0 ? 0 : (withC === 0 ? Infinity : (delta / p) / (withC / dof));
  return { f: Number.isFinite(f) ? f : null, delta_chi2: delta, supported: delta > 0 && (withC === 0 || f >= _SUPPORT_MIN_F) };
}
function _componentSupportFromResponse(json, peakId) {
  const counts = (json && json.counts) || [], fit = (json && json.fitted_y) || [];
  const ip = ((json && json.individual_peaks) || []).find(q => String(q.id) === String(peakId));
  if (ip && ip.support && typeof ip.support.supported === 'boolean') return ip.support;
  const comp = (ip && ip.y) || [], n = counts.length;
  if (!n || fit.length !== n || comp.length !== n) return null;
  let p = 0;
  for (const k in ((ip && ip.params) || {})) { const q = ip.params[k]; if (q && q.vary === true && (q.expr == null || q.expr === '')) p++; }
  const nFree = (json.statistics && Number.isFinite(json.statistics.n_free_params)) ? json.statistics.n_free_params : 0;
  return _componentSupportCore(counts, fit, comp, counts.map(c => 1 / Math.sqrt(Math.max(c, 1))), p, nFree);
}
// Resolve links by ANCESTRY (a grandchild follows the root), independent of order.
function _supportRootOf(peaks, p, seen = new Set()) {
  if (!p.linked || seen.has(p.id)) return p;
  seen.add(p.id);
  const par = peaks.find(q => String(q.id) === String(p.linked));
  return par ? _supportRootOf(peaks, par, seen) : p;
}
// Write p.support for every peak from per-peak verdicts {id -> verdict|null}, stamped with the fit key.
function _applySupportVerdicts(peaks, verdictOf, fitKey) {
  for (const p of peaks) {
    const root = _supportRootOf(peaks, p);
    const v = verdictOf(root.id);
    p.support = v ? { f: v.f ?? null, delta_chi2: v.delta_chi2 ?? null, supported: !!v.supported, fitKey,
                      ...(root !== p ? { follows: root.id } : {}) } : null;
  }
}
function _applySupport(peaks, json, fitKey) {
  _applySupportVerdicts(peaks, id => _componentSupportFromResponse(json, id), fitKey);
}
// TRUE only for a verdict that describes the CURRENT model and fit context.
function _isUnsupported(p, key) {
  if (!(p && p.support && p.support.supported === false)) return false;
  if (!p.support.fitKey) return false;                              // a verdict from before keys existed: not applied
  if (key === undefined) key = typeof _startsLiveKey === 'function' ? _startsLiveKey() : null;
  return p.support.fitKey === key;
}
// A CURRENT verdict, either way (for exports: a stale or keyless verdict is "not established", never "supported").
function _currentSupport(p) {
  if (!(p && p.support && p.support.fitKey)) return null;
  return p.support.fitKey === _startsLiveKey() ? p.support : null;
}
// Re-stamp every verdict with the live key: for a caller that changes the
// model or context AS PART OF producing the result (Auto-Fit locks every
      43
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-82a01DYN' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-j05hTTb0' (errno=Operation not permitted)
b20f0e8 fix(caM): Codex round 2 (NO-GO x2) - the free-m half WITHDRAWN: the local engine holds LA's m exactly; the page mirror stays
c875490 fix(caM): Codex round 1 (NO-GO x2) - the local engine's derivative for m stays inside one kernel-width piece
df388ce fix(caM): LA's m is continuous on the page and in the local engine, as the server fits it
3ea3b8b docs(roi): owner decisions at deploy - the edge difference filed under audit item 8 / R6-1; review the quiet hint's 18 % later; deploy-log entry

exec
/bin/zsh -lc "node -e 'const fs=require(\"fs\"),cp=require(\"child_process\"),path=require(\"path\"),assert=require(\"assert/strict\");
const head=fs.readFileSync(\"templates/index.html\",\"utf8\");
const base=cp.execFileSync(\"git\",[\"show\",\"main:templates/index.html\"],{encoding:\"utf8\",maxBuffer:5e6});
const testSrc=fs.readFileSync(\"tests/js/local_lm_descent.test.js\",\"utf8\").split(\"// ── Committed lab project\")[0].replace(/const html = fs.readFileSync["'^'"\\n]+/,\"\");
function env(html){return new Function(\"require\",\"__dirname\",\"html\",testSrc+\"\\nreturn makeEnv();\")(require,path.resolve(\"tests/js\"),html);}
function local(s){return s.slice(s.indexOf(\"function runFitLocal(\"),s.indexOf(\"\\nfunction solveLinear(\"));}
const baseline=head.replace(local(head),local(base));
const be=Array.from({length:101},(_,i)=>280+0.05*i),bg=be.map(()=>20);
let compared=0;
for(const m of [0,0.001,1,6,8.2,48,499]) for(const fixCaM of [true,false]){
 if("'!fixCaM&&!Number.isInteger(m))continue;
 const a=env(head),b=env(baseline);
 const p={id:1,name:"parent",shape:"LACX",center:282.513,fwhm:0.8,amplitude:5000,caAlpha:1.2,caBeta:1.5,caM:m,fixCaM,fixCaAlpha:true,fixCaBeta:true,fixFwhm:true,fixCenter:true};
 const truth=[p,{...p,id:2,name:"child",linked:1,linkOffset:1,linkRatio:0.5,center:p.center+1,amplitude:2500}];
 const data=a.evalAllPeaks(be,truth).map((v,i)=>v+0.1*Math.sin(3*i));
 for(const e of [a,b])e.state.peaks=[{...p,amplitude:4600},{...truth[1],caM:123.456}];
 const ar=a.runFitLocal(be,data,bg),br=b.runFitLocal(be,data,bg);
 assert.equal(ar.success,true,JSON.stringify(ar));assert.equal(br.success,true,JSON.stringify(br));
 assert.equal(a.state.peaks[1].caM,m);
 assert.equal(a.state.fitResult.chi,b.state.fitResult.chi);
 assert.equal(a.state.peaks[0].amplitude,b.state.peaks[0].amplitude);
 assert.equal(a.state.fitResult.chi/a.state.fitResult.chiReduced,be.length-1);
 const support=a.state.peaks[0].support;
 assert.ok(Math.abs(support.f/(support.delta_chi2/a.state.fitResult.chiReduced)-1)<1e-12);
 compared++;
}
console.log("identical main-vs-HEAD optimiser results with shared evaluator:",compared,"cases; exact linked-child m, dof and component support p verified");
for(const fixCaM of [true,false]){
 const e=env(head),p={id:1,shape:"LACX",center:282.5,fwhm:0.8,amplitude:4000,caAlpha:1.2,caBeta:1.5,caM:5.37,fixCaM,fixCaAlpha:true,fixCaBeta:true,fixFwhm:true,fixCenter:true,fixAmplitude:true};
 e.state.peaks=[p];const d=e.evalAllPeaks(be,[{...p,amplitude:5000}]);const out=e.runFitLocal(be,d,bg);assert.equal(out.success,true);assert.equal(e.state.peaks[0].caM,5.37);assert.ok(Math.abs(e.state.fitResult.chi/e.state.fitResult.chiReduced-be.length)<1e-12);
}
console.log("zero-free-parameter LA cases preserve 5.37 and do not count m");
'"'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 349ms:
identical main-vs-HEAD optimiser results with shared evaluator: 12 cases; exact linked-child m, dof and component support p verified
zero-free-parameter LA cases preserve 5.37 and do not count m

exec
/bin/zsh -lc "node -e 'const fs=require(\"fs\"); const d=JSON.parse(fs.readFileSync(\"docs/findings/cam/local_server_gap_after_cam.json\"));for(const r of d.regions.U4f){if([\"U4f Scan_0\",\"U4f Scan_1\",\"U4f Scan_2\",\"U4f Scan_3\",\"U4f Scan_7\"].includes(r.target)) console.log(r.target,r.comps.filter(c=>c.shape===\"Voigt\").map(c=>({name:c.name,width:c.dFwhm_pct,area:c.dArea_pct,frac:c.dFrac_pp})));}'; nl -ba CLAUDE.md | sed -n '503,530p'; git status --short" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 0ms:
U4f Scan_0 [
  {
    name: 'Satellite 2',
    width: -0.3851204131755437,
    area: -0.5307123787363976,
    frac: -0.023376589365860234
  },
  {
    name: 'Satellite 1',
    width: 0.03457999823504032,
    area: 0.03562946380100129,
    frac: 0.0011667462572452492
  }
]
U4f Scan_1 [
  {
    name: 'Satellite 2',
    width: -1.5289502051010095,
    area: -2.2219095760906082,
    frac: -0.1258171596685384
  },
  {
    name: 'Satellite 1',
    width: -0.4031101322401698,
    area: -0.585474120760443,
    frac: -0.025638134286538883
  }
]
U4f Scan_2 [
  {
    name: 'Satellite 2',
    width: -0.18519258287060802,
    area: -0.23788202473383757,
    frac: -0.007821471757799014
  },
  {
    name: 'Satellite 1',
    width: 0.02325045268598558,
    area: 0.030314046002621886,
    frac: 0.011155982600420666
  }
]
U4f Scan_3 [
  {
    name: 'Satellite 2',
    width: -1.4003595445902461,
    area: -2.0728283603072994,
    frac: -0.12051194106724242
  },
  {
    name: 'Satellite 1',
    width: -0.716327209987444,
    area: -1.2895335013202613,
    frac: -0.0903118688172791
  }
]
U4f Scan_7 [
  {
    name: 'Satellite 2',
    width: -0.6152679076421919,
    area: -0.8534414290346737,
    frac: -0.050833848186738334
  },
  {
    name: 'Satellite 1',
    width: -0.10938610970896434,
    area: -0.09711328307826506,
    frac: -0.011194564508849869
  }
]
   503	**A local result is a STARTING POINT, not a reportable result** (keyed on
   504	`engine: 'local'`, helpers `_isLocalFit` / `_isLocalModel` /
   505	`_localFitCaveat`). Measured in unit W1 and RE-MEASURED after A03
   506	(2026-09-22, `docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`,
   507	generator `scripts/local_server_gap.js`): weighted, it matches the server on
   508	GL-type models (≤ 4 meV, ≤ 1.4 % area on the lab's C1s scans) and on Voigt
   509	components (fixed η = 0.5 on both sides since A03: on the 5 of 9 committed
   510	U 4f targets where both engines reach the same minimum every component
   511	agrees within 4.3 meV, 2.6 % FWHM, 2.0 % area, 0.12 pp — W1 had measured up
   512	to 20.8 % area on the Voigt satellites); it still differs on the other U 4f
   513	targets for two reasons, separated by a control arm (the server with LA's
   514	m held at the same value): the `caM` hold (the server fits m, the local
   515	engine holds it — on Scan_6 the whole gap), and the local descent stopping
   516	in a worse minimum (5–13 % χ²ᵣ above the held-m server on Scan_4/5/8) —
   517	the "several minima" case (`docs/findings/cam/local_server_gap_after_cam.json`;
   518	both engines' amplitude floor is 0 since unit step (b)). Both engines weight by
   519	√intensity whether the data are counts or CPS (a convention, not a
   520	calibrated uncertainty for rates); the formula is the same but the inputs
   521	are not bit-identical, because `uploadToBackend` rounds intensities to
   522	2 dp before the server weights them. A03 and the `caM` unit are done and
   523	the designation STAYS on both grounds: fitting m locally needs a
   524	derivative-free search (its own unit), and the worse-minimum outcome
   525	(three of nine U 4f targets) remains; the label is reconsidered only on a
   526	re-measurement after that work. (The amplitude-bound change
   527	DECIDED 2026-09-18 — `docs/findings/2026-09-fit-determinacy.md` §3 — is
   528	implemented: unit step (b), 2026-09-22, below.) The same file records that a
   529	converged server fit is not ground truth: on a committed C 1s scan the
   530	server's default method stopped in a local minimum the local engine
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-OEIy07jL' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ZmSB9OYR' (errno=Operation not permitted)
?? docs/autofit/codex/cam_continuous_r3_verdict_runA.md
?? docs/autofit/codex/cam_continuous_r3_verdict_runB.md
?? docs/autofit/codex/cam_continuous_recheck2_prompt.txt

 succeeded in 158869ms:
  duration_ms: 18.598539
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
ok 125 - round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
  ---
  duration_ms: 8.107894
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
ok 126 - round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
  ---
  duration_ms: 8.622936
  type: 'test'
  ...
# Subtest: recovery from an amplitude of exactly zero (the new floor is not a trap)
ok 127 - recovery from an amplitude of exactly zero (the new floor is not a trap)
  ---
  duration_ms: 8.647186
  type: 'test'
  ...
1..127
# tests 127
# suites 0
# pass 125
# fail 0
# cancelled 0
# skipped 0
# todo 2
# duration_ms 158919.509504

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const fs=require(\"fs\"),cp=require(\"child_process\"),path=require(\"path\"),assert=require(\"assert/strict\"),orig=cp.execFileSync;
cp.execFileSync=function(exe,args,opts){if(/python/.test(exe)){if(args[0]===\"-c\")args=[\"-c\",'\\''import tempfile; tempfile.tempdir=\"/tmp\";\\n'\\''+args[1],...args.slice(2)];else args=[\"-c\",'\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name=\"__main__\")'\\'',...args];}return orig.call(this,exe,args,opts);};
const source=fs.readFileSync(\"scripts/local_server_gap.js\",\"utf8\").split(\"const out = { generated:\")[0];
const harness=new Function(\"require\",\"__dirname\",source+'\\''\\nreturn {makeEnv,target,tabs};'\\'')(require,path.resolve(\"scripts\"));
const saved=JSON.parse(fs.readFileSync(\"docs/findings/cam/local_server_gap_after_cam.json\"));
for(const [region,sourceName] of [[\"C1s\",\"C1s Scan\"],[\"U4f\",\"U4f Scan\"]])for(const row of saved.regions[region]){
const e=harness.makeEnv(),T=harness.target(e,sourceName,row.target);e.state.peaks=JSON.parse(JSON.stringify(T.start));const r=e.runFitLocal(T.be,T.bgSub,T.bg);
assert.equal(r.success,true);
assert.ok(Math.abs(r.chiReduced/row.local_chi2r-1)<1e-12);
for(const p of e.state.peaks.filter(p=>p.shape===\"LACX\")){const s=T.start.find(q=>q.id===(p.linked||p.id));assert.equal(p.caM,s.caM);}
console.log(row.target,\"matches committed local chi2r; exact caM preserved\");
}
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 exited 1 in 0ms:
<anonymous_script>:3
#!/usr/bin/env node
^

SyntaxError: Invalid or unexpected token
    at new Function (<anonymous>)
    at [eval]:4:15
    at runScriptInThisContext (node:internal/vm:209:10)
    at node:internal/process/execution:446:12
    at [eval]-wrapper:6:24
    at runScriptInContext (node:internal/process/execution:444:60)
    at evalFunction (node:internal/process/execution:279:30)
    at evalTypeScript (node:internal/process/execution:291:3)
    at node:internal/main/eval_string:74:3

Node.js v22.22.2

codex
The three relevant test files pass: 125 passed, 2 expected todos. In 12 additional probes using the same evaluator, `main` and HEAD produced identical optimizer results where rounding was not a factor; linked-child m, dof, and component-support counts also checked out. So far, the remaining issues are stale comments and evidence labels, with no runtime blocker found.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const fs=require(\"fs\"),cp=require(\"child_process\"),path=require(\"path\"),assert=require(\"assert/strict\"),orig=cp.execFileSync;
cp.execFileSync=function(exe,args,opts){if(/python/.test(exe)){if(args[0]===\"-c\")args=[\"-c\",'\\''import tempfile; tempfile.tempdir=\"/tmp\";\\n'\\''+args[1],...args.slice(2)];else args=[\"-c\",'\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name=\"__main__\")'\\'',...args];}return orig.call(this,exe,args,opts);};
const source=fs.readFileSync(\"scripts/local_server_gap.js\",\"utf8\").replace(/"'^#![''^'"\\n]+/,\"\").split(\"const out = { generated:\")[0];
const harness=new Function(\"require\",\"__dirname\",source+'\\''\\nreturn {makeEnv,target,tabs};'\\'')(require,path.resolve(\"scripts\"));
const saved=JSON.parse(fs.readFileSync(\"docs/findings/cam/local_server_gap_after_cam.json\"));
for(const [region,sourceName] of [[\"C1s\",\"C1s Scan\"],[\"U4f\",\"U4f Scan\"]])for(const row of saved.regions[region]){
const e=harness.makeEnv(),T=harness.target(e,sourceName,row.target);e.state.peaks=JSON.parse(JSON.stringify(T.start));const r=e.runFitLocal(T.be,T.bgSub,T.bg);
assert.equal(r.success,true);assert.ok(Math.abs(r.chiReduced/row.local_chi2r-1)<1e-12);
for(const p of e.state.peaks.filter(p=>p.shape===\"LACX\")){const s=T.start.find(q=>q.id===(p.linked||p.id));assert.equal(p.caM,s.caM);}
console.log(row.target,\"matches committed local chi2r; exact caM preserved\");
}'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 2539ms:
C1s Scan_0 matches committed local chi2r; exact caM preserved
C1s Scan_1 matches committed local chi2r; exact caM preserved
C1s Scan_2 matches committed local chi2r; exact caM preserved
C1s Scan_3 matches committed local chi2r; exact caM preserved
C1s Scan_4 matches committed local chi2r; exact caM preserved
C1s Scan_5 matches committed local chi2r; exact caM preserved
C1s Scan_6 matches committed local chi2r; exact caM preserved
C1s Scan_7 matches committed local chi2r; exact caM preserved
C1s Scan_8 matches committed local chi2r; exact caM preserved
U4f Scan_0 matches committed local chi2r; exact caM preserved
U4f Scan_1 matches committed local chi2r; exact caM preserved
U4f Scan_2 matches committed local chi2r; exact caM preserved
U4f Scan_3 matches committed local chi2r; exact caM preserved
U4f Scan_4 matches committed local chi2r; exact caM preserved
U4f Scan_5 matches committed local chi2r; exact caM preserved
U4f Scan_6 matches committed local chi2r; exact caM preserved
U4f Scan_7 matches committed local chi2r; exact caM preserved
U4f Scan_8 matches committed local chi2r; exact caM preserved

exec
/bin/zsh -lc "nl -ba scripts/cam_transition_sweep.js | tail -10; nl -ba tests/js/local_lm_descent.test.js | sed -n '513,519p'; rg -n 'can differ.*LA|LA components \\(m held' templates/index.html; git diff --numstat df388ce..HEAD -- templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 0ms:
    15	  const mT = 6 * k / 7 + off; const be = grid(280, 280 + 150 * st, st);
    16	  const truth = { id: 1, name: 'la', shape: 'LACX', center: 280 + 75 * st + 0.013, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: mT, glMix: 50, asymmetry: 0 };
    17	  const run = fixCaM => { const e = env(); e.state.peaks = [{ ...truth }]; const d = e.evalAllPeaks(be, e.state.peaks).map((v, i) => v + 5 * Math.sin(1.77 * i));
    18	    e.state.peaks = [{ ...truth, amplitude: 4600, caM: Math.max(0.01, mT + startDelta), fixCenter: true, fixFwhm: true, fixCaM }]; const o = e.runFitLocal(be, d, be.map(() => 0)); return { o, chi: e.state.fitResult && e.state.fitResult.chi }; };
    19	  const fr = run(false), hd = run(true); n++;
    20	  if (!fr.o.success) { freeFail++; fails.push({ st, k, off, startDelta, msg: fr.o.message }); }
    21	  if (!hd.o.success) heldFail++;
    22	  if (fr.o.success && hd.o.success && fr.chi > hd.chi * (1 + 1e-9)) worse++;
    23	}
    24	console.log(JSON.stringify({ cases: n, free_failed: freeFail, held_failed: heldFail, free_ended_worse_than_held: worse, first_fails: fails.slice(0, 5) }));
   513	  { label: 'run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free', be: grid(280, 283, 0.05),
   514	    truth: { center: 281.538, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: 18 / 7 - 0.001 }, noise: i => 0.1 * Math.sin(3 * i),
   515	    start: { amplitude: 4000, caM: 2.6 }, lock: {} },
   516	]) {
   517	  test(`an LA fit with m free converges across a kernel-width transition — ${c.label}`, () => {
   518	    const run = (fixCaM) => {
   519	      const env = makeEnv();
8058:    : 'It can differ from the server fit for LA components (the page holds the smoothing parameter m at its start; the server fits it) or where the model has several minima.';
11512:const _LOCALFIT_TOOLTIP = "Statistic of the local (in-page) fit. Since unit W1 (2026-09) the local engine is Poisson-weighted like the server, so its \u03c7\u00b2\u1d63 is comparable with the server's, but it gives no parameter uncertainties and can differ from the server fit for LA components (m held at its start locally) or where the model has several minima. Local results saved earlier were unweighted and are labelled 'Residual variance'. Run Fit with the server available for a reportable result.";
14555:    <p style="font-size:12px;color:var(--text);line-height:1.6;margin:0 0 10px">The server fitting engine (lmfit) could not be reached, so the page's built-in optimiser fitted this spectrum instead. It converged and is Poisson-weighted like the server, but it gives <strong>no parameter uncertainties</strong> and can differ from the server fit for LA components (m held at its start locally) or where the model has several minima. Treat it as a <strong>starting point, not a reportable result</strong>. Run Fit again when the server is available before quantifying, exporting or reporting.</p>
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-1yvW4LUQ' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-MUtwp4r6' (errno=Operation not permitted)
31	17	templates/index.html

codex
No BLOCKER or MAJOR findings.

- **MINOR — withdrawn derivative still described as active.** [templates/index.html:4094](/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/templates/index.html:4094) says the local m derivative uses `_laKernelHalf` to stay within one piece. That derivative no longer exists. Following this comment during a transition-failure investigation leads to nonexistent behavior; describe the helper as evaluator-only.

- **MINOR — sweep labels still imply free-m optimization.** [scripts/cam_transition_sweep.js:24](/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/scripts/cam_transition_sweep.js:24) emits `free_failed` and `free_ended_worse_than_held`. Running it on HEAD compares two held-m fits, differing only in the lock flag. Its output cannot establish free-m convergence. Rename these arms unlocked/locked and distinguish the historical round-1 evidence.

The shipping contract checks out: caM never enters the local parameter vector, clamp, derivative or certificate; it contributes neither dof nor component-support parameters. Linked children inherit the parent’s exact value. Batch copying and amplitude scaling preserve it. No executable dependency on the withdrawn derivative remains.

Validation: **125 relevant tests passed, 2 expected todos**, including page/server parity and all four reproducers. Twelve additional controlled comparisons matched main’s optimizer results using the same evaluator where rounding was irrelevant. All 18 local target replays matched the committed JSON, preserving exact caM. The final plan’s measurement table and restored caveat agree with that evidence.

The initial full-suite run encountered Python temporary-directory failures under the read-only sandbox; relevant tests passed with an in-memory adjustment avoiding that probe. No files changed; browser checks were not rerun.

VERDICT: GO
tokens used
87,977
No BLOCKER or MAJOR findings.

- **MINOR — withdrawn derivative still described as active.** [templates/index.html:4094](/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/templates/index.html:4094) says the local m derivative uses `_laKernelHalf` to stay within one piece. That derivative no longer exists. Following this comment during a transition-failure investigation leads to nonexistent behavior; describe the helper as evaluator-only.

- **MINOR — sweep labels still imply free-m optimization.** [scripts/cam_transition_sweep.js:24](/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/scripts/cam_transition_sweep.js:24) emits `free_failed` and `free_ended_worse_than_held`. Running it on HEAD compares two held-m fits, differing only in the lock flag. Its output cannot establish free-m convergence. Rename these arms unlocked/locked and distinguish the historical round-1 evidence.

The shipping contract checks out: caM never enters the local parameter vector, clamp, derivative or certificate; it contributes neither dof nor component-support parameters. Linked children inherit the parent’s exact value. Batch copying and amplitude scaling preserve it. No executable dependency on the withdrawn derivative remains.

Validation: **125 relevant tests passed, 2 expected todos**, including page/server parity and all four reproducers. Twelve additional controlled comparisons matched main’s optimizer results using the same evaluator where rounding was irrelevant. All 18 local target replays matched the committed JSON, preserving exact caM. The final plan’s measurement table and restored caveat agree with that evidence.

The initial full-suite run encountered Python temporary-directory failures under the read-only sandbox; relevant tests passed with an in-memory adjustment avoiding that probe. No files changed; browser checks were not rerun.

VERDICT: GO
