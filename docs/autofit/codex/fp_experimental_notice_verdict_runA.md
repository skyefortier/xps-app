2026-07-20T22:26:08.031889Z ERROR codex_models_manager::cache: failed to load models cache: missing field `supports_reasoning_summaries` at line 88 column 5
OpenAI Codex v0.139.0
--------
workdir: /Users/skyefortier/xps-verify
model: gpt-5.5
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 019f81a2-f6b5-7922-9068-3c89ba7e3272
--------
user
You are an adversarial reviewer for a small UI commit in this repo (XPS
peak-fitting web app). Review commit 56b5d5a ("feat(ui): one-time Find
Peaks experimental notice") on branch feature-autofit-stage2 -- `git show
56b5d5a` gives the full diff. This lands on top of a merge of origin/main
into feature-autofit-stage2 (commit d13589d, already independently
verified clean) — confirm this commit itself is scoped correctly and
doesn't touch anything from that merge.

BACKGROUND: neither the Find Peaks modal's "BETA" badge nor its existing
blurb ("starting suggestions to review — not final answers") tells a
student the RUNTIME. A student clicking "Suggest peaks" with no idea a
full run can take up to 4 minutes may reasonably conclude the app is
frozen. This commit adds a one-time, dismissible notice banner
(#fp-experimental-notice) shown on first Find Peaks open, persisted via
localStorage so it never shows again after "Got it".

WHAT CHANGED (templates/index.html, tests/js/fp_experimental_notice.test.js):
- FP_STRINGS.experimentalNotice: new string, "Find Peaks is experimental.
  Suggestions are a starting point to review, not a final answer — and a
  full run can take 60–240 seconds depending on the region and method.
  This won't show again."
- New HTML: <div id="fp-experimental-notice"> banner with a "Got it"
  button, inserted between the modal's <h3> header and the existing
  #fp-blurb paragraph.
- New JS: _fpMaybeShowExperimentalNotice() (checks localStorage key
  xps-fp-experimental-notice-dismissed, shows/hides the banner and sets
  its text) and _fpDismissExperimentalNotice() (sets the localStorage key,
  hides the banner). openFindPeaksModal() now calls
  _fpMaybeShowExperimentalNotice() right after setting #fp-blurb.

ADVERSARIAL QUESTIONS -- ATTACK THESE SPECIFICALLY:

(a) THE LOCALSTORAGE LOGIC, TRACED PRECISELY. Confirm: (1) on a browser
    that has never dismissed the notice, opening the modal shows the
    banner with the correct FP_STRINGS.experimentalNotice text; (2)
    clicking "Got it" calls _fpDismissExperimentalNotice, which sets
    localStorage and hides the banner; (3) on every SUBSEQUANT open in
    the same browser (same localStorage), the banner stays hidden --
    _fpMaybeShowExperimentalNotice must correctly early-return without
    ever setting the banner's text/display when the key is present. Read
    the actual conditional logic character-by-character; don't just
    trust the summary above.

(b) IS "60-240 SECONDS" ACCURATE, OR INVENTED? Independently verify this
    specific claim against the codebase rather than trusting the commit
    message: grep app.py and autofit/engine.py for "60-240", "240", and
    TOTAL_ANALYSIS_TIMEOUT_SEC. Confirm this is a genuinely pre-existing,
    already-documented runtime range for the analysis backend (not a
    number invented for this notice), and confirm the notice's phrasing
    doesn't overstate precision (e.g. implying every run takes exactly
    this long, when it's a range "depending on region and method").

(c) DOES THE COPY OVERCLAIM OR UNDERCLAIM ANYTHING? Read
    FP_STRINGS.experimentalNotice literally, as a student with no other
    context would. Does it imply the results ARE accurate/correct (it
    shouldn't -- that's what "starting point to review, not a final
    answer" is for)? Does it correctly avoid implying the app is
    broken/frozen during a long run (the whole point of the notice)?

(d) INTERFERENCE CHECK. Confirm the new banner and its call site do not
    interfere with: the existing #fp-material-hint / #fp-method-hint
    mechanisms (_fpMaterialChanged / _fpMethodChanged, called elsewhere
    in openFindPeaksModal); the modal's drag behavior (_fpModalDragStart
    et al., which the header's onmousedown wires up — confirm the new
    banner element sits OUTSIDE the drag-handle element, i.e. doesn't
    accidentally start a drag when a user clicks "Got it" or reads the
    banner text); the #fp-blurb paragraph's own rendering (still set
    correctly right after, unaffected by the new call).

(e) SCOPE. Confirm 56b5d5a's diff touches only templates/index.html and
    tests/js/fp_experimental_notice.test.js. No diff in any Python file,
    any other test file, or unrelated parts of templates/index.html.

(f) TEST DISCRIMINATION. For each of the 5 tests in
    tests/js/fp_experimental_notice.test.js, would it actually fail if
    the corresponding behavior were missing or wrong (not just pass
    incidentally because of how the regex extraction works)?

Deliver: a numbered findings list (severity BLOCKER/MAJOR/MINOR, each with
file/line and a concrete failure scenario), then a final line exactly
"VERDICT: GO" or "VERDICT: NO-GO".

codex
I’ll review this as a commit audit, not a patch task. I’ll inspect the target diff, relevant runtime constants, and the new tests against the actual code paths before giving a verdict.
exec
/bin/zsh -lc 'rg -n "60-240|60–240|240|TOTAL_ANALYSIS_TIMEOUT_SEC" app.py autofit/engine.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
app.py:912:        For a long analysis (60-240s), POST /api/analyze/start + poll
app.py:944:        an entire worker for the whole 60-240s analysis, on top of the
autofit/engine.py:155:# overrun TOTAL_ANALYSIS_TIMEOUT_SEC — and hence the gunicorn --timeout
autofit/engine.py:189:TOTAL_ANALYSIS_TIMEOUT_SEC = 240.0
autofit/engine.py:254:# never finish inside TOTAL_ANALYSIS_TIMEOUT_SEC (240 s, deliberately below
autofit/engine.py:272:# The screen may spend at most this fraction of TOTAL_ANALYSIS_TIMEOUT_SEC —
autofit/engine.py:1616:    # Set when the sweep hit TOTAL_ANALYSIS_TIMEOUT_SEC and stopped before
autofit/engine.py:2188:    # BUDGET_SEC of sweep budget left would overrun TOTAL_ANALYSIS_TIMEOUT_SEC
autofit/engine.py:2734:        screen_deadline = sweep_start + SCREEN_BUDGET_FRACTION * TOTAL_ANALYSIS_TIMEOUT_SEC
autofit/engine.py:2775:        # 240 s budget on real data — past the gunicorn --timeout 300, i.e.
autofit/engine.py:2778:        # wall ≈ TOTAL_ANALYSIS_TIMEOUT_SEC.
autofit/engine.py:2780:        if elapsed > TOTAL_ANALYSIS_TIMEOUT_SEC - CANDIDATE_TIMEOUT_SEC:
autofit/engine.py:2786:                elapsed, TOTAL_ANALYSIS_TIMEOUT_SEC, n_evaluated, len(candidates),
autofit/engine.py:2851:                TOTAL_ANALYSIS_TIMEOUT_SEC - (pass_start - sweep_start))

exec
/bin/zsh -lc 'git show --stat --oneline --decorate --name-only 56b5d5a' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-9f5PR7Ra' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-CjHoyBxC' (errno=Operation not permitted)
56b5d5a feat(ui): one-time Find Peaks experimental notice
templates/index.html
tests/js/fp_experimental_notice.test.js

exec
/bin/zsh -lc 'git show --format=fuller --no-ext-diff --find-renames 56b5d5a -- templates/index.html tests/js/fp_experimental_notice.test.js' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ecRNDXa8' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Sjf6mBFa' (errno=Operation not permitted)
commit 56b5d5ab899ed4c6e203a5efa8fa484931b46107
Author:     Skye Fortier <skyefortier@gmail.com>
AuthorDate: Mon Jul 20 16:24:43 2026 -0600
Commit:     Skye Fortier <skyefortier@gmail.com>
CommitDate: Mon Jul 20 16:24:43 2026 -0600

    feat(ui): one-time Find Peaks experimental notice
    
    Neither the "BETA" badge nor the existing blurb ("starting suggestions
    to review — not final answers") tells a student the RUNTIME. A student
    clicking "Suggest peaks" with no idea a full run can take up to 4
    minutes may reasonably conclude the app is frozen, not slow. This is the
    one UX addition that protects users rather than adds convenience.
    
    FP_STRINGS.experimentalNotice states plainly: experimental, results are
    a starting point to review, and a full run can take 60–240 seconds
    depending on region/method. Shown as a dismissible banner
    (#fp-experimental-notice) at the top of the Find Peaks modal —
    persistent until acknowledged, not an auto-dismissing toast, since this
    is exactly the kind of thing a toast's few-second window would let a
    user miss. Dismissal persists via localStorage
    (xps-fp-experimental-notice-dismissed), so it shows once per browser,
    never again after "Got it".
    
    Tests: tests/js/fp_experimental_notice.test.js (5 tests) — the copy
    names it experimental and states the 60/240 runtime range, doesn't
    overclaim accuracy or imply the app is broken during a long run, and the
    DOM wiring (banner element, dismiss handler, localStorage gate,
    openFindPeaksModal calling the gate) all exist and are wired correctly.
    Browser-verified via Playwright: shows with the correct text on first
    open; dismissing hides it and sets the localStorage key; a second open
    in the same browser stays hidden (persisted); clearing localStorage
    (simulating a fresh browser) makes it reappear. Full JS suite (9 files)
    and a JS syntax check of the whole template both clean.
    
    Purely additive: one new HTML element, two new small DOM-wiring
    functions, one FP_STRINGS entry, one call site in openFindPeaksModal.
    No change to any existing Find Peaks behavior, hint mechanism, or modal
    drag/resize logic.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

diff --git a/templates/index.html b/templates/index.html
index 112f3fd..cab7ec3 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -12882,6 +12882,10 @@ document.addEventListener('mousedown', function(e) {
     <h3 class="fp-drag-handle" onmousedown="_fpModalDragStart(event)" title="Drag to move this box out of the way">Find Peaks <span style="font-size:10px;color:var(--text3)">BETA</span>
       <button class="btn btn-sm" onclick="closeFindPeaksModal()" style="float:right">&#x2715;</button>
     </h3>
+    <div id="fp-experimental-notice" style="display:none;background:var(--bg2);border:1px solid var(--amber);border-radius:var(--radius);padding:8px 10px;margin-bottom:10px;font-size:11px;color:var(--text2);line-height:1.5">
+      <span id="fp-experimental-notice-text"></span>
+      <button class="btn btn-sm" onclick="_fpDismissExperimentalNotice()" style="float:right;margin-left:8px">Got it</button>
+    </div>
     <p id="fp-blurb" style="font-size:11px;color:var(--text2);line-height:1.5;margin:0 0 10px"></p>
     <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
       <label style="font-size:11px" id="fp-material-label">Material class
@@ -13037,6 +13041,13 @@ const FP_STRINGS = {
          'unless you add them.',
   applyNote: 'Adding replaces this tab’s current peak list with the ' +
              'suggested peaks. You can undo this (Ctrl+Z).',
+  // One-time notice (2026-07-20): the BETA badge and the blurb above never
+  // told a student the RUNTIME — a full run can take up to 4 minutes, and
+  // without warning that reads as a frozen app, not a slow one.
+  experimentalNotice: 'Find Peaks is experimental. Suggestions are a ' +
+                       'starting point to review, not a final answer — ' +
+                       'and a full run can take 60–240 seconds depending ' +
+                       'on the region and method. This won’t show again.',
   // Label/hint override for one material-class dropdown option (2026-07-20).
   // Only "mixed" gets an entry — conductor/semiconductor/insulator render
   // exactly as before (bare backend value, no title attribute).
@@ -13441,6 +13452,7 @@ async function openFindPeaksModal() {
   // become an injection point)
   document.getElementById('fp-blurb').innerHTML = FP_STRINGS.blurb;
   document.getElementById('fp-apply-note').textContent = FP_STRINGS.applyNote;
+  _fpMaybeShowExperimentalNotice();
   document.getElementById('fp-material-label').title = FP_STRINGS.tips.material;
   document.getElementById('fp-method-label').title = FP_STRINGS.tips.method;
   document.getElementById('fp-regions-label').title = FP_STRINGS.tips.regions;
@@ -13759,6 +13771,24 @@ function _fpMaterialChanged() {
   document.getElementById('fp-material-hint').textContent = s.hint || '';
 }
 
+const FP_EXPERIMENTAL_NOTICE_LS_KEY = 'xps-fp-experimental-notice-dismissed';
+
+function _fpMaybeShowExperimentalNotice() {
+  const el = document.getElementById('fp-experimental-notice');
+  if (localStorage.getItem(FP_EXPERIMENTAL_NOTICE_LS_KEY)) {
+    el.style.display = 'none';
+    return;
+  }
+  document.getElementById('fp-experimental-notice-text').textContent =
+    FP_STRINGS.experimentalNotice;
+  el.style.display = 'block';
+}
+
+function _fpDismissExperimentalNotice() {
+  localStorage.setItem(FP_EXPERIMENTAL_NOTICE_LS_KEY, '1');
+  document.getElementById('fp-experimental-notice').style.display = 'none';
+}
+
 function _fpMethodChanged() {
   const id = document.getElementById('fp-method').value;
   const m = (_fpMeta.methods || []).find(x => x.id === id);
diff --git a/tests/js/fp_experimental_notice.test.js b/tests/js/fp_experimental_notice.test.js
new file mode 100644
index 0000000..f1e36c4
--- /dev/null
+++ b/tests/js/fp_experimental_notice.test.js
@@ -0,0 +1,67 @@
+// Find Peaks experimental notice (2026-07-20): the "BETA" badge and the
+// existing blurb ("starting suggestions to review — not final answers")
+// never told a student the RUNTIME. A student clicking "Suggest peaks" with
+// no idea it can take up to 4 minutes may reasonably conclude the app is
+// frozen. This is the one UX addition that protects users rather than adds
+// convenience: a one-time notice, shown on first open, dismissed permanently
+// via localStorage.
+
+const { test } = require('node:test');
+const assert = require('node:assert');
+const fs = require('node:fs');
+const path = require('node:path');
+
+const html = fs.readFileSync(
+  path.join(__dirname, '../../templates/index.html'), 'utf8');
+
+function extract(re, name) {
+  const m = html.match(re);
+  assert.ok(m, name + ' not found in templates/index.html');
+  return m[0];
+}
+
+const FP_STRINGS = eval(
+  '(' + extract(/const FP_STRINGS = \{[\s\S]*?\n\};/, 'FP_STRINGS')
+    .replace(/^const FP_STRINGS = /, '').replace(/;$/, '') + ')');
+
+test('FP_STRINGS.experimentalNotice names it experimental and states the '
+     + 'runtime range', () => {
+  const notice = FP_STRINGS.experimentalNotice;
+  assert.ok(notice, 'FP_STRINGS.experimentalNotice must exist');
+  assert.match(notice, /experimental/i);
+  assert.match(notice, /60/);
+  assert.match(notice, /240/);
+});
+
+test('FP_STRINGS.experimentalNotice says results are a starting point, '
+     + 'not a final answer', () => {
+  const notice = FP_STRINGS.experimentalNotice;
+  assert.match(notice, /starting point|not a final answer|review/i);
+});
+
+test('FP_STRINGS.experimentalNotice does not overclaim correctness or '
+     + 'imply the app is frozen/broken during a long run', () => {
+  const notice = FP_STRINGS.experimentalNotice;
+  assert.doesNotMatch(notice, /guarantee/i);
+  assert.doesNotMatch(notice, /accurate/i);
+});
+
+test('the notice DOM wiring exists: banner element, dismiss handler, and '
+     + 'a localStorage-backed one-time gate', () => {
+  assert.match(html, /id="fp-experimental-notice"/);
+  assert.match(html, /function _fpDismissExperimentalNotice/);
+  assert.match(html, /function _fpMaybeShowExperimentalNotice/);
+  // must actually persist the dismissal, not just hide it for the session
+  const fn = extract(/function _fpDismissExperimentalNotice\(\) \{[\s\S]*?\n\}/,
+    '_fpDismissExperimentalNotice');
+  assert.match(fn, /localStorage\.setItem/);
+  const gate = extract(/function _fpMaybeShowExperimentalNotice\(\) \{[\s\S]*?\n\}/,
+    '_fpMaybeShowExperimentalNotice');
+  assert.match(gate, /localStorage\.getItem/);
+});
+
+test('openFindPeaksModal calls the notice gate so it actually shows on open', () => {
+  const fn = extract(/async function openFindPeaksModal\(\) \{[\s\S]*?\n\}/,
+    'openFindPeaksModal');
+  assert.match(fn, /_fpMaybeShowExperimentalNotice\(\)/);
+});

codex
The initial diff is limited to the two expected files. I’m going deeper on the exact DOM placement, localStorage branch behavior, and whether the 60–240 second claim is backed by existing backend documentation.
exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '13032,13050p'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '12878,12892p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
 13032	
 13033	// ═══ ALL user-facing wording lives HERE (one place, easy to iterate). ═══
 13034	// Audience: bench chemists/spectroscopists. Engine jargon (grammar,
 13035	// candidate-model, decisive_override, +bfix, role slugs) must never reach
 13036	// the screen — the honest CONTENT stays, said plainly.
 13037	const FP_STRINGS = {
 13038	  blurb: 'Suggests a set of peaks for the region(s) you select and shows ' +
 13039	         'how confident it is. These are <b>starting suggestions to ' +
 13040	         'review — not final answers</b>. Nothing changes your manual fit ' +
 13041	         'unless you add them.',
 13042	  applyNote: 'Adding replaces this tab’s current peak list with the ' +
 13043	             'suggested peaks. You can undo this (Ctrl+Z).',
 13044	  // One-time notice (2026-07-20): the BETA badge and the blurb above never
 13045	  // told a student the RUNTIME — a full run can take up to 4 minutes, and
 13046	  // without warning that reads as a frozen app, not a slow one.
 13047	  experimentalNotice: 'Find Peaks is experimental. Suggestions are a ' +
 13048	                       'starting point to review, not a final answer — ' +
 13049	                       'and a full run can take 60–240 seconds depending ' +
 13050	                       'on the region and method. This won’t show again.',

 succeeded in 0ms:
 12878	     confidence + ambiguity flags; a NAMED human review is required
 12879	     before anything is applied to the tab. ═══════════════════════════ -->
 12880	<div id="find-peaks-overlay" class="xps-modal-overlay" onclick="if(event.target===this)this.classList.remove('open')">
 12881	  <div class="xps-modal" id="find-peaks-modal-box" style="max-width:680px;max-height:86vh;overflow-y:auto">
 12882	    <h3 class="fp-drag-handle" onmousedown="_fpModalDragStart(event)" title="Drag to move this box out of the way">Find Peaks <span style="font-size:10px;color:var(--text3)">BETA</span>
 12883	      <button class="btn btn-sm" onclick="closeFindPeaksModal()" style="float:right">&#x2715;</button>
 12884	    </h3>
 12885	    <div id="fp-experimental-notice" style="display:none;background:var(--bg2);border:1px solid var(--amber);border-radius:var(--radius);padding:8px 10px;margin-bottom:10px;font-size:11px;color:var(--text2);line-height:1.5">
 12886	      <span id="fp-experimental-notice-text"></span>
 12887	      <button class="btn btn-sm" onclick="_fpDismissExperimentalNotice()" style="float:right;margin-left:8px">Got it</button>
 12888	    </div>
 12889	    <p id="fp-blurb" style="font-size:11px;color:var(--text2);line-height:1.5;margin:0 0 10px"></p>
 12890	    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
 12891	      <label style="font-size:11px" id="fp-material-label">Material class
 12892	        <select id="fp-material" class="btn" style="width:100%" onchange="_fpMaterialChanged()"></select>

exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '13750,13792p'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '13436,13462p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
 13750	  const values = Array.from(_fpRegionsSelected);
 13751	  const coverage = (_fpMeta && _fpMeta.coverage) || [];
 13752	  const entries = values.map(v => coverage.find(e => e.region === v))
 13753	    .filter(Boolean);
 13754	  document.getElementById('fp-regions-tier-note').textContent =
 13755	    _fpTierNoteFor(entries);
 13756	  // ROI auto-fill: only for an UNAMBIGUOUS single-region pick with a real
 13757	  // hint — a co-fit selection (2 regions) has no single "right" window,
 13758	  // and a structure_only region honestly has no hint to offer (goal:
 13759	  // never invent a window; the note above says so, ROI is left alone).
 13760	  if (entries.length === 1 && entries[0].roi) {
 13761	    document.getElementById('roi-min').value = entries[0].roi.be_min;
 13762	    document.getElementById('roi-max').value = entries[0].roi.be_max;
 13763	  }
 13764	  _fpRenderPtGrid(document.getElementById('fp-regions-filter').value);
 13765	  _fpRenderExpandedPanel();
 13766	}
 13767	
 13768	function _fpMaterialChanged() {
 13769	  const v = document.getElementById('fp-material').value;
 13770	  const s = FP_STRINGS.materials[v] || {};
 13771	  document.getElementById('fp-material-hint').textContent = s.hint || '';
 13772	}
 13773	
 13774	const FP_EXPERIMENTAL_NOTICE_LS_KEY = 'xps-fp-experimental-notice-dismissed';
 13775	
 13776	function _fpMaybeShowExperimentalNotice() {
 13777	  const el = document.getElementById('fp-experimental-notice');
 13778	  if (localStorage.getItem(FP_EXPERIMENTAL_NOTICE_LS_KEY)) {
 13779	    el.style.display = 'none';
 13780	    return;
 13781	  }
 13782	  document.getElementById('fp-experimental-notice-text').textContent =
 13783	    FP_STRINGS.experimentalNotice;
 13784	  el.style.display = 'block';
 13785	}
 13786	
 13787	function _fpDismissExperimentalNotice() {
 13788	  localStorage.setItem(FP_EXPERIMENTAL_NOTICE_LS_KEY, '1');
 13789	  document.getElementById('fp-experimental-notice').style.display = 'none';
 13790	}
 13791	
 13792	function _fpMethodChanged() {

 succeeded in 0ms:
 13436	async function openFindPeaksModal() {
 13437	  if (!state.rawBE || !state.rawBE.length) {
 13438	    notify('Load a spectrum first — Find Peaks runs on the active tab.', 'amber');
 13439	    return;
 13440	  }
 13441	  try {
 13442	    if (!_fpMeta) {
 13443	      const r = await fetch('/api/analyze/meta');
 13444	      _fpMeta = await r.json();
 13445	    }
 13446	  } catch (e) {
 13447	    notify('Find Peaks backend unavailable: ' + e.message, 'amber');
 13448	    return;
 13449	  }
 13450	  // all wording from FP_STRINGS; server strings escaped even though
 13451	  // currently code-controlled (a future registered label must never
 13452	  // become an injection point)
 13453	  document.getElementById('fp-blurb').innerHTML = FP_STRINGS.blurb;
 13454	  document.getElementById('fp-apply-note').textContent = FP_STRINGS.applyNote;
 13455	  _fpMaybeShowExperimentalNotice();
 13456	  document.getElementById('fp-material-label').title = FP_STRINGS.tips.material;
 13457	  document.getElementById('fp-method-label').title = FP_STRINGS.tips.method;
 13458	  document.getElementById('fp-regions-label').title = FP_STRINGS.tips.regions;
 13459	  const mat = document.getElementById('fp-material');
 13460	  mat.innerHTML = _fpMeta.material_classes
 13461	    .map(m => {
 13462	      const s = FP_STRINGS.materials[m] || {};

exec
/bin/zsh -lc "nl -ba tests/js/fp_experimental_notice.test.js | sed -n '1,90p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
     1	// Find Peaks experimental notice (2026-07-20): the "BETA" badge and the
     2	// existing blurb ("starting suggestions to review — not final answers")
     3	// never told a student the RUNTIME. A student clicking "Suggest peaks" with
     4	// no idea it can take up to 4 minutes may reasonably conclude the app is
     5	// frozen. This is the one UX addition that protects users rather than adds
     6	// convenience: a one-time notice, shown on first open, dismissed permanently
     7	// via localStorage.
     8	
     9	const { test } = require('node:test');
    10	const assert = require('node:assert');
    11	const fs = require('node:fs');
    12	const path = require('node:path');
    13	
    14	const html = fs.readFileSync(
    15	  path.join(__dirname, '../../templates/index.html'), 'utf8');
    16	
    17	function extract(re, name) {
    18	  const m = html.match(re);
    19	  assert.ok(m, name + ' not found in templates/index.html');
    20	  return m[0];
    21	}
    22	
    23	const FP_STRINGS = eval(
    24	  '(' + extract(/const FP_STRINGS = \{[\s\S]*?\n\};/, 'FP_STRINGS')
    25	    .replace(/^const FP_STRINGS = /, '').replace(/;$/, '') + ')');
    26	
    27	test('FP_STRINGS.experimentalNotice names it experimental and states the '
    28	     + 'runtime range', () => {
    29	  const notice = FP_STRINGS.experimentalNotice;
    30	  assert.ok(notice, 'FP_STRINGS.experimentalNotice must exist');
    31	  assert.match(notice, /experimental/i);
    32	  assert.match(notice, /60/);
    33	  assert.match(notice, /240/);
    34	});
    35	
    36	test('FP_STRINGS.experimentalNotice says results are a starting point, '
    37	     + 'not a final answer', () => {
    38	  const notice = FP_STRINGS.experimentalNotice;
    39	  assert.match(notice, /starting point|not a final answer|review/i);
    40	});
    41	
    42	test('FP_STRINGS.experimentalNotice does not overclaim correctness or '
    43	     + 'imply the app is frozen/broken during a long run', () => {
    44	  const notice = FP_STRINGS.experimentalNotice;
    45	  assert.doesNotMatch(notice, /guarantee/i);
    46	  assert.doesNotMatch(notice, /accurate/i);
    47	});
    48	
    49	test('the notice DOM wiring exists: banner element, dismiss handler, and '
    50	     + 'a localStorage-backed one-time gate', () => {
    51	  assert.match(html, /id="fp-experimental-notice"/);
    52	  assert.match(html, /function _fpDismissExperimentalNotice/);
    53	  assert.match(html, /function _fpMaybeShowExperimentalNotice/);
    54	  // must actually persist the dismissal, not just hide it for the session
    55	  const fn = extract(/function _fpDismissExperimentalNotice\(\) \{[\s\S]*?\n\}/,
    56	    '_fpDismissExperimentalNotice');
    57	  assert.match(fn, /localStorage\.setItem/);
    58	  const gate = extract(/function _fpMaybeShowExperimentalNotice\(\) \{[\s\S]*?\n\}/,
    59	    '_fpMaybeShowExperimentalNotice');
    60	  assert.match(gate, /localStorage\.getItem/);
    61	});
    62	
    63	test('openFindPeaksModal calls the notice gate so it actually shows on open', () => {
    64	  const fn = extract(/async function openFindPeaksModal\(\) \{[\s\S]*?\n\}/,
    65	    'openFindPeaksModal');
    66	  assert.match(fn, /_fpMaybeShowExperimentalNotice\(\)/);
    67	});

codex
The banner is a sibling after the `h3`, so it is outside the drag handle; the dismiss button should not invoke the header’s `onmousedown`. I’m checking the rest of `openFindPeaksModal` now to ensure the existing hint updates still run in their original order.
exec
/bin/zsh -lc "nl -ba app.py | sed -n '895,955p'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '13452,13540p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   895	          "cc_shift":       0.0,          // frontend charge shift (corrected = raw − cc_shift)
   896	          "roi":            {"be_min": ..., "be_max": ...},   // corrected frame
   897	          "material_class": "conductor" | "insulator" | "semiconductor" | "mixed",
   898	          "regions":        ["Cl 2p", ...],   // registered region names
   899	          "phase":          {"id": "sample", "material": "graphite"},  // optional
   900	          "method":         "ic_model_comparison" | "least_squares"
   901	                            | "bayesian_exchange_mc" | "sparse_map",
   902	          "options":        {...},        // per-method; validated by the method
   903	          "peak_specs":     [...]         // least_squares only (manual baseline)
   904	        }
   905	
   906	        Returns the full MethodResult: candidate peaks with the per-peak
   907	        confidence vector, the analysis namespace (ambiguity flags, ranked
   908	        alternatives, constants provenance), diagnostics, and a review-gate
   909	        stub — results are candidates + honesty flags, not ground truth;
   910	        a NAMED human review is required before export (spec §8).
   911	
   912	        For a long analysis (60-240s), POST /api/analyze/start + poll
   913	        GET /api/analyze/progress/<job_id> instead — same validation, same
   914	        result shape, plus live sweep progress (Find Peaks UI, 2026-07-11).
   915	        This synchronous route is UNCHANGED: both now share
   916	        ``_validate_analyze_request``/``_run_analyze_method``/
   917	        ``_build_analyze_payload`` under the hood (a pure extract-method
   918	        refactor — tests/test_api_analyze.py pins the contract identical).
   919	        """
   920	        body = request.get_json(silent=True)
   921	        if not isinstance(body, dict):
   922	            return _err("request body must be a JSON object")
   923	        try:
   924	            ctx = _validate_analyze_request(body, app.config["UPLOAD_FOLDER"])
   925	            res = _run_analyze_method(ctx)
   926	        except _AnalyzeError as exc:
   927	            return _err(str(exc), exc.status)
   928	        payload = _build_analyze_payload(ctx, res)
   929	        return jsonify(_json_sanitize(payload))
   930	
   931	    @app.post("/api/analyze/start")
   932	    @_require_json
   933	    def analyze_start():
   934	        """
   935	        Async twin of POST /api/analyze for the Find Peaks progress
   936	        indicator (2026-07-11).  Same request body; same SYNCHRONOUS
   937	        validation (a malformed request is STILL an immediate 400, never
   938	        a spinner) — only the actual method execution (the genuinely
   939	        slow, honestly-long part) moves to a background thread.
   940	
   941	        Why a thread + a poll file, not SSE: production gunicorn runs the
   942	        default SYNC worker class (`--workers 4`, no gthread/gevent — see
   943	        the LaunchAgent plist), so a held-open SSE connection would tie up
   944	        an entire worker for the whole 60-240s analysis, on top of the
   945	        existing synchronous /api/analyze already doing exactly that for
   946	        ITS OWN request. A background thread returns the HTTP response
   947	        immediately (freeing the worker's request loop), and progress is
   948	        written to a small JSON file under the upload folder — file, not
   949	        an in-process dict, because gunicorn's workers are separate OS
   950	        processes and a poll can land on a different one (same reasoning
   951	        as the existing session .npz files: "no server-side memory state
   952	        ... compatible with multi-worker gunicorn").
   953	
   954	        Returns {"job_id": "..."} , 202.  Poll
   955	        GET /api/analyze/progress/<job_id> for {status, phase,

 succeeded in 0ms:
 13452	  // become an injection point)
 13453	  document.getElementById('fp-blurb').innerHTML = FP_STRINGS.blurb;
 13454	  document.getElementById('fp-apply-note').textContent = FP_STRINGS.applyNote;
 13455	  _fpMaybeShowExperimentalNotice();
 13456	  document.getElementById('fp-material-label').title = FP_STRINGS.tips.material;
 13457	  document.getElementById('fp-method-label').title = FP_STRINGS.tips.method;
 13458	  document.getElementById('fp-regions-label').title = FP_STRINGS.tips.regions;
 13459	  const mat = document.getElementById('fp-material');
 13460	  mat.innerHTML = _fpMeta.material_classes
 13461	    .map(m => {
 13462	      const s = FP_STRINGS.materials[m] || {};
 13463	      const title = s.hint ? ` title="${_fpEsc(s.hint)}"` : '';
 13464	      return `<option value="${_fpEsc(m)}"${title}>${_fpEsc(s.label || m)}</option>`;
 13465	    }).join('');
 13466	  _fpMaterialChanged();
 13467	  document.getElementById('fp-regions-filter').value = '';
 13468	  _fpRegionsSelected = new Set();
 13469	  _fpExpandedElement = null;
 13470	  _fpRenderLegend();
 13471	  _fpRenderPtGrid('');
 13472	  _fpRenderSearchDropdown('');
 13473	  _fpRenderExpandedPanel();
 13474	  document.getElementById('fp-regions-tier-note').textContent = '';
 13475	  const meth = document.getElementById('fp-method');
 13476	  meth.innerHTML = _fpMeta.methods
 13477	    .map(m => {
 13478	      const s = FP_STRINGS.methods[m.id] || {};
 13479	      // hovering an option (even before selecting it) shows the SAME
 13480	      // plain-English explanation as the hint box below the dropdown —
 13481	      // no jargon, and no need to select first just to learn what an
 13482	      // option does. Previously showed the raw backend label here
 13483	      // (e.g. "Auto — model comparison (IC)"), which read as vague/
 13484	      // jargon-y "the tooltip" per the 2026-07-14 bug report.
 13485	      return `<option value="${_fpEsc(m.id)}" title="${_fpEsc(s.hint || s.label || m.label || m.id)}">${_fpEsc(s.label || m.label || m.id)}</option>`;
 13486	    }).join('');
 13487	  meth.value = 'ic_model_comparison';
 13488	  _fpMethodChanged();
 13489	  document.getElementById('fp-results').style.display = 'none';
 13490	  document.getElementById('fp-status').textContent = '';
 13491	  _fpResetModalPosition();
 13492	  document.getElementById('find-peaks-overlay').classList.add('open');
 13493	}
 13494	
 13495	function closeFindPeaksModal() {
 13496	  document.getElementById('find-peaks-overlay').classList.remove('open');
 13497	}
 13498	
 13499	// ── Draggable modal (2026-07-11) ────────────────────────────────────────
 13500	// Same technique as the Reference palette's _refPaletteDragStart/Move/End
 13501	// (static/js/ref_identify_core.js RefCore.clampToViewport is the shared,
 13502	// tested clamp math) — but scoped to ONLY the Find Peaks modal: every
 13503	// other .xps-modal in the app stays centered/non-draggable.
 13504	
 13505	let _fpModalDrag = null;
 13506	
 13507	// True for the close button (or any future control placed in the header)
 13508	// — those must still work; only the bare header background starts a drag.
 13509	// (`instanceof Element` guard: a text-node event target lacks .closest —
 13510	// see CLAUDE.md Known Issues re: the same class of bug elsewhere.)
 13511	function _fpIsDragBlockingTarget(target) {
 13512	  return !!(target instanceof Element && target.closest('button, select, input, a, textarea'));
 13513	}
 13514	
 13515	function _fpClampModal(left, top) {
 13516	  const el = document.getElementById('find-peaks-modal-box');
 13517	  const w = el ? el.offsetWidth : 680, h = el ? el.offsetHeight : 400;
 13518	  return RefCore.clampToViewport(left, top, w, h, window.innerWidth, window.innerHeight, 8);
 13519	}
 13520	
 13521	function _fpModalDragStart(e) {
 13522	  if (_fpIsDragBlockingTarget(e.target)) return;
 13523	  const el = document.getElementById('find-peaks-modal-box');
 13524	  if (!el) return;
 13525	  const r = el.getBoundingClientRect();
 13526	  // First drag: switch from flex-centered to absolutely positioned,
 13527	  // pinned at its CURRENT visual spot so there is no jump.
 13528	  el.style.position = 'fixed';
 13529	  el.style.left = r.left + 'px'; el.style.top = r.top + 'px';
 13530	  el.style.margin = '0';
 13531	  _fpModalDrag = { dx: e.clientX - r.left, dy: e.clientY - r.top };
 13532	  el.classList.add('dragging');
 13533	  document.addEventListener('mousemove', _fpModalDragMove, true);
 13534	  document.addEventListener('mouseup', _fpModalDragEnd, true);
 13535	  e.preventDefault();
 13536	}
 13537	function _fpModalDragMove(e) {
 13538	  if (!_fpModalDrag) return;
 13539	  const el = document.getElementById('find-peaks-modal-box');
 13540	  if (!el) return;

exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '145,200p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   145	# the persistence gate below its threshold — measured on the real C 1s
   146	# motivating case (PROGRESS.md diagnosis follow-up): a ΔBIC* −86 proposal
   147	# with no boundary hits was rejected at persistence 2/3 = 0.67 < 0.70 purely
   148	# because the 4th refit never ran.  35 s fits n_refits=4 at the measured
   149	# ~7-8 s worst-case per refit on 191-point real data.  UNVERIFIED tunable.
   150	PROPOSAL_STABILITY_TIMEOUT_SEC = 35.0
   151	# Minimum budget (s) that must remain before an augmented-model FIT is
   152	# started inside the proposal pass.  A single fit_candidate at
   153	# FIT_CANDIDATE_MAX_NFEV runs ~10-12 s worst-case on 191-point data with no
   154	# internal wall clock, so starting one with less than this left would
   155	# overrun TOTAL_ANALYSIS_TIMEOUT_SEC — and hence the gunicorn --timeout
   156	# (Codex c1s-fix review, run B MAJOR).  A proposal attempt that cannot fit
   157	# this budget fast-rejects with 'insufficient_budget'.  UNVERIFIED tunable.
   158	PROPOSAL_MIN_FIT_BUDGET_SEC = 15.0
   159	
   160	# See fit_candidate() docstring: deterministic per-call ceiling on lmfit's
   161	# own effort, replacing its effectively-unbounded default.
   162	FIT_CANDIDATE_MAX_NFEV = 18000
   163	WARM_RESTART_MAX_NFEV = 2000     # single retry budget for a failed-but-
   164	                                 # finite fit (measured need: ~33 evals;
   165	                                 # generous headroom, still bounded)
   166	
   167	# Wall-clock ceiling on ONE candidate's entire primary-fit + stability-refit
   168	# pass (compare_models -> run_stability_analysis). Mirrors
   169	# PROPOSAL_CANDIDATE_TIMEOUT_SEC's existing per-candidate budget for the
   170	# later residual-proposal pass: a candidate that blows this budget stops
   171	# taking further stability refits rather than consuming the rest of the
   172	# request's time. FIT_CANDIDATE_MAX_NFEV already bounds any single call to
   173	# roughly 10-12s on this pipeline's DS+G cost profile, so this allows a
   174	# couple of such calls (primary + 1-2 refits) before cutting the rest.
   175	CANDIDATE_TIMEOUT_SEC = 25.0
   176	
   177	# Wall-clock ceiling on the ENTIRE compare_models sweep over all candidates
   178	# in the grammar. Per-candidate budgets (CANDIDATE_TIMEOUT_SEC,
   179	# PROPOSAL_CANDIDATE_TIMEOUT_SEC) bound any one candidate but not their sum
   180	# — a 29-candidate grammar at ~7s/candidate for ordinary (non-degenerate)
   181	# fits already runs ~3-4 minutes, and several candidates hitting the
   182	# DS+G-style degenerate corner push that further. Checked once per outer
   183	# loop iteration (compare_models): once exceeded, remaining candidates are
   184	# skipped and the sweep returns best-so-far, ranked normally, with
   185	# ComparisonResult.analysis_truncated=True — an honest partial result
   186	# instead of a request timeout. Deliberately below the gunicorn dev
   187	# --timeout so this truncation path always gets to run and respond before
   188	# the worker is aborted (see DEPLOY.md / dev gunicorn --timeout).
   189	TOTAL_ANALYSIS_TIMEOUT_SEC = 240.0
   190	PROPOSAL_ENDPOINT_WARNING_BE = 1.0
   191	PROPOSAL_COINCIDENCE_BE = 0.5
   192	
   193	# Component treated as asymmetric during shape-aware slot disambiguation.
   194	ALPHA_SYMMETRY_THRESHOLD = 0.01      # DS / DS+G α, asym-GL asymmetry
   195	LACX_EXPONENT_ASYMMETRY = 0.02       # |α − β| for true CasaXPS LA
   196	
   197	# ── Pre-fit out-of-grammar dominant seeding (unit F1, 2026-07-07) ──────────
   198	# Measured motivation (PROGRESS.md "Real multi-environment C 1s — MEASURED
   199	# DIAGNOSIS"): on real low-BE-dominant multi-environment C 1s spectra the
   200	# dominant data feature lies OUTSIDE every grammar window, so every

exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '245,285p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   245	GRAMMAR_AUGMENT_MAX_SEEDS = 3        # of those, at most this many augment
   246	                                     # each GRAMMAR family (measured: the
   247	                                     # full set made all 29 screens blow
   248	                                     # the nfev cap); the detection family
   249	                                     # carries the full structure instead
   250	
   251	# ── Two-phase sweep: screen → stabilize (unit F3, 2026-07-07) ──────────────
   252	# Measured motivation (PROGRESS.md diagnosis, cause a): a 29-candidate C 1s
   253	# grammar at 25 s/candidate stability budgets + a 30-60 s proposal pass can
   254	# never finish inside TOTAL_ANALYSIS_TIMEOUT_SEC (240 s, deliberately below
   255	# the gunicorn --timeout 300) — the real spectra truncated at 8/29 with the
   256	# expert-structure MG family (candidates #21-24) never evaluated.  When the
   257	# candidate set is larger than SCREEN_TOP_K, compare_models first fits EVERY
   258	# candidate once (primary fit only, SCREEN_MAX_NFEV effort cap), ranks the
   259	# converged screens by BIC, and runs the full pipeline (stability, proposal
   260	# pass, absent slots) ONLY for the top SCREEN_TOP_K — reusing each screen
   261	# fit as that candidate's primary, so no work repeats.  Candidates screened
   262	# out are reported honestly (analysis `screen` record: every candidate's
   263	# screen BIC / non-convergence, nothing silent) and can never become
   264	# survivors — the same contract as truncation, but deterministic and
   265	# best-candidates-first instead of grammar-order-first.  Sweeps of
   266	# ≤ SCREEN_TOP_K candidates (every existing gate/battery/stress case) take
   267	# the classic single-phase path unchanged.  Both UNVERIFIED tunables.
   268	SCREEN_MAX_NFEV = 6000     # measured: converging primaries on real 191-pt
   269	                           # C 1s data use 3-5k evals; hopeless landscapes
   270	                           # burn ≥ 18k without converging
   271	SCREEN_TOP_K = 6
   272	# The screen may spend at most this fraction of TOTAL_ANALYSIS_TIMEOUT_SEC —
   273	# the deep phase must always retain budget, else a very large (joint) grammar
   274	# could burn the whole sweep screening and deep-evaluate NOTHING.
   275	SCREEN_BUDGET_FRACTION = 0.6
   276	
   277	
   278	def _slot_prefix(role: str) -> str:
   279	    """Slot role → lmfit parameter-name prefix (must match grammar._slot_param_prefix)."""
   280	    return "s_" + re.sub(r"[^A-Za-z0-9_]", "_", role) + "_"
   281	
   282	
   283	# ─────────────────────────────────────────────────────────────────────────────
   284	# Background
   285	# ─────────────────────────────────────────────────────────────────────────────

exec
/bin/zsh -lc 'git show --pretty=raw --no-patch 56b5d5a && git diff-tree --no-commit-id --name-status -r 56b5d5a' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-GDfL4G31' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-pSuMblgu' (errno=Operation not permitted)
commit 56b5d5ab899ed4c6e203a5efa8fa484931b46107
tree 51f5e487a609275bd52fe8f124eaf322c6985ad7
parent d13589d72ea97f8318083a90d233a5cf43ce869c
author Skye Fortier <skyefortier@gmail.com> 1784586283 -0600
committer Skye Fortier <skyefortier@gmail.com> 1784586283 -0600

    feat(ui): one-time Find Peaks experimental notice
    
    Neither the "BETA" badge nor the existing blurb ("starting suggestions
    to review — not final answers") tells a student the RUNTIME. A student
    clicking "Suggest peaks" with no idea a full run can take up to 4
    minutes may reasonably conclude the app is frozen, not slow. This is the
    one UX addition that protects users rather than adds convenience.
    
    FP_STRINGS.experimentalNotice states plainly: experimental, results are
    a starting point to review, and a full run can take 60–240 seconds
    depending on region/method. Shown as a dismissible banner
    (#fp-experimental-notice) at the top of the Find Peaks modal —
    persistent until acknowledged, not an auto-dismissing toast, since this
    is exactly the kind of thing a toast's few-second window would let a
    user miss. Dismissal persists via localStorage
    (xps-fp-experimental-notice-dismissed), so it shows once per browser,
    never again after "Got it".
    
    Tests: tests/js/fp_experimental_notice.test.js (5 tests) — the copy
    names it experimental and states the 60/240 runtime range, doesn't
    overclaim accuracy or imply the app is broken during a long run, and the
    DOM wiring (banner element, dismiss handler, localStorage gate,
    openFindPeaksModal calling the gate) all exist and are wired correctly.
    Browser-verified via Playwright: shows with the correct text on first
    open; dismissing hides it and sets the localStorage key; a second open
    in the same browser stays hidden (persisted); clearing localStorage
    (simulating a fresh browser) makes it reappear. Full JS suite (9 files)
    and a JS syntax check of the whole template both clean.
    
    Purely additive: one new HTML element, two new small DOM-wiring
    functions, one FP_STRINGS entry, one call site in openFindPeaksModal.
    No change to any existing Find Peaks behavior, hint mechanism, or modal
    drag/resize logic.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-kP49VALn' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-swjDdG7p' (errno=Operation not permitted)
M	templates/index.html
A	tests/js/fp_experimental_notice.test.js

codex
The runtime claim is not invented: `app.py` already documents long analysis as `60-240s`, and `autofit/engine.py` has `TOTAL_ANALYSIS_TIMEOUT_SEC = 240.0` with comments tying 240 seconds to the sweep ceiling. I’m now testing whether the added unit tests are actually discriminating or only checking loose substrings.
exec
/bin/zsh -lc 'rg -n "_fpMaybeShowExperimentalNotice|_fpDismissExperimentalNotice|fp-experimental-notice|fp-material-hint|fp-method-hint|_fpMaterialChanged|_fpMethodChanged|fp-blurb|_fpModalDragStart" templates/index.html tests/js/fp_experimental_notice.test.js' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
tests/js/fp_experimental_notice.test.js:51:  assert.match(html, /id="fp-experimental-notice"/);
tests/js/fp_experimental_notice.test.js:52:  assert.match(html, /function _fpDismissExperimentalNotice/);
tests/js/fp_experimental_notice.test.js:53:  assert.match(html, /function _fpMaybeShowExperimentalNotice/);
tests/js/fp_experimental_notice.test.js:55:  const fn = extract(/function _fpDismissExperimentalNotice\(\) \{[\s\S]*?\n\}/,
tests/js/fp_experimental_notice.test.js:56:    '_fpDismissExperimentalNotice');
tests/js/fp_experimental_notice.test.js:58:  const gate = extract(/function _fpMaybeShowExperimentalNotice\(\) \{[\s\S]*?\n\}/,
tests/js/fp_experimental_notice.test.js:59:    '_fpMaybeShowExperimentalNotice');
tests/js/fp_experimental_notice.test.js:66:  assert.match(fn, /_fpMaybeShowExperimentalNotice\(\)/);
templates/index.html:12882:    <h3 class="fp-drag-handle" onmousedown="_fpModalDragStart(event)" title="Drag to move this box out of the way">Find Peaks <span style="font-size:10px;color:var(--text3)">BETA</span>
templates/index.html:12885:    <div id="fp-experimental-notice" style="display:none;background:var(--bg2);border:1px solid var(--amber);border-radius:var(--radius);padding:8px 10px;margin-bottom:10px;font-size:11px;color:var(--text2);line-height:1.5">
templates/index.html:12886:      <span id="fp-experimental-notice-text"></span>
templates/index.html:12887:      <button class="btn btn-sm" onclick="_fpDismissExperimentalNotice()" style="float:right;margin-left:8px">Got it</button>
templates/index.html:12889:    <p id="fp-blurb" style="font-size:11px;color:var(--text2);line-height:1.5;margin:0 0 10px"></p>
templates/index.html:12892:        <select id="fp-material" class="btn" style="width:100%" onchange="_fpMaterialChanged()"></select>
templates/index.html:12895:        <select id="fp-method" class="btn" style="width:100%" onchange="_fpMethodChanged()"></select>
templates/index.html:12909:        <div id="fp-material-hint" style="color:var(--text3);font-size:10px;line-height:1.45;margin-bottom:6px"></div>
templates/index.html:12910:        <div id="fp-method-hint" style="color:var(--text3);font-size:10px;line-height:1.45;margin-bottom:6px"></div>
templates/index.html:13453:  document.getElementById('fp-blurb').innerHTML = FP_STRINGS.blurb;
templates/index.html:13455:  _fpMaybeShowExperimentalNotice();
templates/index.html:13466:  _fpMaterialChanged();
templates/index.html:13488:  _fpMethodChanged();
templates/index.html:13521:function _fpModalDragStart(e) {
templates/index.html:13768:function _fpMaterialChanged() {
templates/index.html:13771:  document.getElementById('fp-material-hint').textContent = s.hint || '';
templates/index.html:13774:const FP_EXPERIMENTAL_NOTICE_LS_KEY = 'xps-fp-experimental-notice-dismissed';
templates/index.html:13776:function _fpMaybeShowExperimentalNotice() {
templates/index.html:13777:  const el = document.getElementById('fp-experimental-notice');
templates/index.html:13782:  document.getElementById('fp-experimental-notice-text').textContent =
templates/index.html:13787:function _fpDismissExperimentalNotice() {
templates/index.html:13789:  document.getElementById('fp-experimental-notice').style.display = 'none';
templates/index.html:13792:function _fpMethodChanged() {
templates/index.html:13796:  document.getElementById('fp-method-hint').textContent = strs.hint || '';

exec
/bin/zsh -lc 'git branch --show-current' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-58VIRtoL' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-GripRSlF' (errno=Operation not permitted)
feature-autofit-stage2

exec
/bin/zsh -lc 'node --test tests/js/fp_experimental_notice.test.js' in /Users/skyefortier/xps-verify
 succeeded in 127ms:
# Subtest: FP_STRINGS.experimentalNotice names it experimental and states the runtime range
ok 1 - FP_STRINGS.experimentalNotice names it experimental and states the runtime range
  ---
  duration_ms: 0.886988
  type: 'test'
  ...
# Subtest: FP_STRINGS.experimentalNotice says results are a starting point, not a final answer
ok 2 - FP_STRINGS.experimentalNotice says results are a starting point, not a final answer
  ---
  duration_ms: 0.176709
  type: 'test'
  ...
# Subtest: FP_STRINGS.experimentalNotice does not overclaim correctness or imply the app is frozen/broken during a long run
ok 3 - FP_STRINGS.experimentalNotice does not overclaim correctness or imply the app is frozen/broken during a long run
  ---
  duration_ms: 0.165185
  type: 'test'
  ...
# Subtest: the notice DOM wiring exists: banner element, dismiss handler, and a localStorage-backed one-time gate
ok 4 - the notice DOM wiring exists: banner element, dismiss handler, and a localStorage-backed one-time gate
  ---
  duration_ms: 1.180314
  type: 'test'
  ...
# Subtest: openFindPeaksModal calls the notice gate so it actually shows on open
ok 5 - openFindPeaksModal calls the notice gate so it actually shows on open
  ---
  duration_ms: 0.640811
  type: 'test'
  ...
1..5
# tests 5
# suites 0
# pass 5
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 89.871216

codex
The new Node test file passes. One review point remains: the tests are useful for presence and core copy, but some assertions are loose; I’m separating that test-quality observation from product-blocking behavior.
exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '13788,13805p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
 13788	  localStorage.setItem(FP_EXPERIMENTAL_NOTICE_LS_KEY, '1');
 13789	  document.getElementById('fp-experimental-notice').style.display = 'none';
 13790	}
 13791	
 13792	function _fpMethodChanged() {
 13793	  const id = document.getElementById('fp-method').value;
 13794	  const m = (_fpMeta.methods || []).find(x => x.id === id);
 13795	  const strs = FP_STRINGS.methods[id] || {};
 13796	  document.getElementById('fp-method-hint').textContent = strs.hint || '';
 13797	  // the Advanced JSON stays the single source of truth for the request —
 13798	  // the friendly controls below are a labeled VIEW that writes into it
 13799	  document.getElementById('fp-options').value =
 13800	    JSON.stringify((m && m.default_options) || {}, null, 1);
 13801	  _fpBuildSimpleControls(id);
 13802	}
 13803	
 13804	function _fpBuildSimpleControls(methodId) {
 13805	  const host = document.getElementById('fp-simple-options');

exec
/bin/zsh -lc 'git diff 56b5d5a''^ 56b5d5a -- templates/index.html | sed -n '"'1,220p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-tQls0Dm0' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-9KYHR1SL' (errno=Operation not permitted)
diff --git a/templates/index.html b/templates/index.html
index 112f3fd..cab7ec3 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -12882,6 +12882,10 @@ document.addEventListener('mousedown', function(e) {
     <h3 class="fp-drag-handle" onmousedown="_fpModalDragStart(event)" title="Drag to move this box out of the way">Find Peaks <span style="font-size:10px;color:var(--text3)">BETA</span>
       <button class="btn btn-sm" onclick="closeFindPeaksModal()" style="float:right">&#x2715;</button>
     </h3>
+    <div id="fp-experimental-notice" style="display:none;background:var(--bg2);border:1px solid var(--amber);border-radius:var(--radius);padding:8px 10px;margin-bottom:10px;font-size:11px;color:var(--text2);line-height:1.5">
+      <span id="fp-experimental-notice-text"></span>
+      <button class="btn btn-sm" onclick="_fpDismissExperimentalNotice()" style="float:right;margin-left:8px">Got it</button>
+    </div>
     <p id="fp-blurb" style="font-size:11px;color:var(--text2);line-height:1.5;margin:0 0 10px"></p>
     <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
       <label style="font-size:11px" id="fp-material-label">Material class
@@ -13037,6 +13041,13 @@ const FP_STRINGS = {
          'unless you add them.',
   applyNote: 'Adding replaces this tab’s current peak list with the ' +
              'suggested peaks. You can undo this (Ctrl+Z).',
+  // One-time notice (2026-07-20): the BETA badge and the blurb above never
+  // told a student the RUNTIME — a full run can take up to 4 minutes, and
+  // without warning that reads as a frozen app, not a slow one.
+  experimentalNotice: 'Find Peaks is experimental. Suggestions are a ' +
+                       'starting point to review, not a final answer — ' +
+                       'and a full run can take 60–240 seconds depending ' +
+                       'on the region and method. This won’t show again.',
   // Label/hint override for one material-class dropdown option (2026-07-20).
   // Only "mixed" gets an entry — conductor/semiconductor/insulator render
   // exactly as before (bare backend value, no title attribute).
@@ -13441,6 +13452,7 @@ async function openFindPeaksModal() {
   // become an injection point)
   document.getElementById('fp-blurb').innerHTML = FP_STRINGS.blurb;
   document.getElementById('fp-apply-note').textContent = FP_STRINGS.applyNote;
+  _fpMaybeShowExperimentalNotice();
   document.getElementById('fp-material-label').title = FP_STRINGS.tips.material;
   document.getElementById('fp-method-label').title = FP_STRINGS.tips.method;
   document.getElementById('fp-regions-label').title = FP_STRINGS.tips.regions;
@@ -13759,6 +13771,24 @@ function _fpMaterialChanged() {
   document.getElementById('fp-material-hint').textContent = s.hint || '';
 }
 
+const FP_EXPERIMENTAL_NOTICE_LS_KEY = 'xps-fp-experimental-notice-dismissed';
+
+function _fpMaybeShowExperimentalNotice() {
+  const el = document.getElementById('fp-experimental-notice');
+  if (localStorage.getItem(FP_EXPERIMENTAL_NOTICE_LS_KEY)) {
+    el.style.display = 'none';
+    return;
+  }
+  document.getElementById('fp-experimental-notice-text').textContent =
+    FP_STRINGS.experimentalNotice;
+  el.style.display = 'block';
+}
+
+function _fpDismissExperimentalNotice() {
+  localStorage.setItem(FP_EXPERIMENTAL_NOTICE_LS_KEY, '1');
+  document.getElementById('fp-experimental-notice').style.display = 'none';
+}
+
 function _fpMethodChanged() {
   const id = document.getElementById('fp-method').value;
   const m = (_fpMeta.methods || []).find(x => x.id === id);

exec
/bin/zsh -lc 'git diff 56b5d5a''^ 56b5d5a --stat && git diff 56b5d5a''^ 56b5d5a --name-only' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-IJb50DI1' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-VZ7Jkict' (errno=Operation not permitted)
 templates/index.html                    | 30 +++++++++++++++
 tests/js/fp_experimental_notice.test.js | 67 +++++++++++++++++++++++++++++++++
 2 files changed, 97 insertions(+)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-jsUvvxVN' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Nkru3vkZ' (errno=Operation not permitted)
templates/index.html
tests/js/fp_experimental_notice.test.js

2026-07-20T22:27:06.890603Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 88 column 5
codex
One possible resilience edge is storage access failure, but the app already assumes browser storage in multiple places. I’m checking whether this change introduces a new convention violation or matches existing frontend assumptions.
exec
/bin/zsh -lc "rg -n \"try \\{|localStorage|getItem|setItem\" templates/index.html | sed -n '1,80p'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "rg -n \"localStorage\\.\" templates/index.html static tests/js" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
templates/index.html:10132:  localStorage.setItem('xps-theme', isLight ? 'light' : 'dark');
templates/index.html:10139:  if (localStorage.getItem('xps-theme') === 'light') {
templates/index.html:10882:    const o = JSON.parse(localStorage.getItem(REF_PALETTE_LS) || 'null');
templates/index.html:10888:    localStorage.setItem(REF_PALETTE_LS, JSON.stringify({ ...(_refLoadPaletteState() || {}), ...patch }));
templates/index.html:13778:  if (localStorage.getItem(FP_EXPERIMENTAL_NOTICE_LS_KEY)) {
templates/index.html:13788:  localStorage.setItem(FP_EXPERIMENTAL_NOTICE_LS_KEY, '1');
tests/js/fp_experimental_notice.test.js:7:// via localStorage.

 succeeded in 0ms:
2966:  try {
3790:          try {
3799:          try {
4507:      try {
4516:      try {
4988:  try {
6671:  try {
6788:  try {
8874:  try {
8887:    try {
10132:  localStorage.setItem('xps-theme', isLight ? 'light' : 'dark');
10139:  if (localStorage.getItem('xps-theme') === 'light') {
10881:  try {
10882:    const o = JSON.parse(localStorage.getItem(REF_PALETTE_LS) || 'null');
10887:  try {
10888:    localStorage.setItem(REF_PALETTE_LS, JSON.stringify({ ...(_refLoadPaletteState() || {}), ...patch }));
13441:  try {
13778:  if (localStorage.getItem(FP_EXPERIMENTAL_NOTICE_LS_KEY)) {
13788:  localStorage.setItem(FP_EXPERIMENTAL_NOTICE_LS_KEY, '1');
13816:  try { opts = JSON.parse(document.getElementById('fp-options').value || '{}'); }
13859:  try { opts = JSON.parse(document.getElementById('fp-options').value || '{}'); }
13931:  try {
13939:  try {
13970:        try {

2026-07-20T22:27:30.149367Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 88 column 5
exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '10122,10144p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
 10122	    rawData: document.body.classList.contains('light-theme') ? '#1a1a2e' : '#e8edf5',
 10123	  };
 10124	}
 10125	
 10126	// ═══════════════════════════════════════════════════
 10127	// DARK / LIGHT MODE
 10128	// ═══════════════════════════════════════════════════
 10129	function toggleTheme() {
 10130	  const isLight = document.body.classList.toggle('light-theme');
 10131	  document.getElementById('theme-toggle').textContent = isLight ? '☀️' : '🌙';
 10132	  localStorage.setItem('xps-theme', isLight ? 'light' : 'dark');
 10133	  // Re-render chart so grid/text colors update
 10134	  if (state.chart) updatePlot();
 10135	}
 10136	
 10137	// Apply saved theme on load
 10138	(function() {
 10139	  if (localStorage.getItem('xps-theme') === 'light') {
 10140	    document.body.classList.add('light-theme');
 10141	    // Update button after DOM is ready
 10142	    window.addEventListener('DOMContentLoaded', () => {
 10143	      const btn = document.getElementById('theme-toggle');
 10144	      if (btn) btn.textContent = '☀️';

exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '10876,10892p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
 10876	
 10877	function _refPaletteIsMobile() {
 10878	  return typeof window.matchMedia === 'function' && window.matchMedia('(max-width: 640px)').matches;
 10879	}
 10880	function _refLoadPaletteState() {
 10881	  try {
 10882	    const o = JSON.parse(localStorage.getItem(REF_PALETTE_LS) || 'null');
 10883	    return (o && typeof o === 'object') ? o : null;
 10884	  } catch (e) { return null; }
 10885	}
 10886	function _refSavePaletteState(patch) {
 10887	  try {
 10888	    localStorage.setItem(REF_PALETTE_LS, JSON.stringify({ ...(_refLoadPaletteState() || {}), ...patch }));
 10889	  } catch (e) { /* private mode / quota — geometry is best-effort */ }
 10890	}
 10891	function _refClampPalette(left, top) {
 10892	  const el = document.getElementById('ref-panel');

2026-07-20T22:27:35.615934Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 88 column 5
codex
1. MINOR: [tests/js/fp_experimental_notice.test.js](/Users/skyefortier/xps-verify/tests/js/fp_experimental_notice.test.js:36) has loose discrimination for tests 2-4. Test 2 would pass on only “review”; test 3 does not actually reject “frozen”/“broken” or “correct”; test 4 only checks `getItem`/`setItem` presence, not exact key, button wiring, display transitions, or early-return semantics. Concrete failure: a future wrong-key implementation could pass while showing the notice on every open.

No BLOCKER/MAJOR product findings. Commit `56b5d5a` is a single-parent commit on `d13589d` and touches only `templates/index.html` plus the new JS test file. The localStorage logic is correct: undismissed opens set the notice text and `display='block'`; “Got it” writes `xps-fp-experimental-notice-dismissed` and hides it; subsequent opens set `display='none'` and return before setting text or showing.

The `60-240 seconds` claim is pre-existing: `app.py` documents long analysis as `60-240s`, and `autofit/engine.py` has `TOTAL_ANALYSIS_TIMEOUT_SEC = 240.0`. The notice is phrased as a range depending on region and method, and does not claim accuracy or final correctness. The banner is outside the `h3.fp-drag-handle`, and `openFindPeaksModal()` still sets `#fp-blurb`, then calls the notice gate, then runs the existing material/method hint flows.

Verified: `node --test tests/js/fp_experimental_notice.test.js` passes.

VERDICT: GO
tokens used
31,927
1. MINOR: [tests/js/fp_experimental_notice.test.js](/Users/skyefortier/xps-verify/tests/js/fp_experimental_notice.test.js:36) has loose discrimination for tests 2-4. Test 2 would pass on only “review”; test 3 does not actually reject “frozen”/“broken” or “correct”; test 4 only checks `getItem`/`setItem` presence, not exact key, button wiring, display transitions, or early-return semantics. Concrete failure: a future wrong-key implementation could pass while showing the notice on every open.

No BLOCKER/MAJOR product findings. Commit `56b5d5a` is a single-parent commit on `d13589d` and touches only `templates/index.html` plus the new JS test file. The localStorage logic is correct: undismissed opens set the notice text and `display='block'`; “Got it” writes `xps-fp-experimental-notice-dismissed` and hides it; subsequent opens set `display='none'` and return before setting text or showing.

The `60-240 seconds` claim is pre-existing: `app.py` documents long analysis as `60-240s`, and `autofit/engine.py` has `TOTAL_ANALYSIS_TIMEOUT_SEC = 240.0`. The notice is phrased as a range depending on region and method, and does not claim accuracy or final correctness. The banner is outside the `h3.fp-drag-handle`, and `openFindPeaksModal()` still sets `#fp-blurb`, then calls the notice gate, then runs the existing material/method hint flows.

Verified: `node --test tests/js/fp_experimental_notice.test.js` passes.

VERDICT: GO
