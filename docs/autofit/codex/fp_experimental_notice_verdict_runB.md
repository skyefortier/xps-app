2026-07-20T22:26:08.027951Z ERROR codex_models_manager::cache: failed to load models cache: missing field `supports_reasoning_summaries` at line 88 column 5
OpenAI Codex v0.139.0
--------
workdir: /Users/skyefortier/xps-verify
model: gpt-5.5
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 019f81a2-f6cf-7702-a168-98f361fdd927
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
I’ll review this as a diff-level code review and verify the runtime claim against the current tree. I’ll read the target commit plus the relevant backend constants and tests, then report only concrete findings or say none.
exec
/bin/zsh -lc 'rg -n "60.?240|240|TOTAL_ANALYSIS_TIMEOUT_SEC" app.py autofit/engine.py templates/index.html tests/js/fp_experimental_notice.test.js' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
app.py:912:        For a long analysis (60-240s), POST /api/analyze/start + poll
app.py:944:        an entire worker for the whole 60-240s analysis, on top of the
tests/js/fp_experimental_notice.test.js:33:  assert.match(notice, /240/);
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
templates/index.html:51:    --z-toast: 2400;           /* tier toast */
templates/index.html:437:    display: none; position: fixed; z-index: var(--z-toast, 2400);
templates/index.html:1136:    min-width: 180px; max-height: 240px; overflow-y: auto;
templates/index.html:1259:     while a long analysis (60-240s) runs. */
templates/index.html:1813:  #propagate-tab-list { max-height: 240px; overflow-y: auto; border: 1px solid var(--border); border-radius: var(--radius); padding: 6px 8px; margin-bottom: 10px; }
templates/index.html:2750://   V 2p:  3.240
templates/index.html:2807:  'Ca 3s': 0.304, 'Ti 2p': 2.752, 'V 2p': 3.240, 'Cr 2p': 3.758, 'Mn 2p': 4.326,
templates/index.html:13049:                       'and a full run can take 60–240 seconds depending ' +
templates/index.html:13893:// (TOTAL_ANALYSIS_TIMEOUT_SEC, well under this), so this only fires if a

exec
/bin/zsh -lc 'git show --find-renames --find-copies --stat --patch --unified=80 56b5d5a -- templates/index.html tests/js/fp_experimental_notice.test.js' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-qNM2sBpj' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-3VJlzXb2' (errno=Operation not permitted)
commit 56b5d5ab899ed4c6e203a5efa8fa484931b46107
Author: Skye Fortier <skyefortier@gmail.com>
Date:   Mon Jul 20 16:24:43 2026 -0600

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
---
 templates/index.html                    | 30 +++++++++++++++
 tests/js/fp_experimental_notice.test.js | 67 +++++++++++++++++++++++++++++++++
 2 files changed, 97 insertions(+)

diff --git a/templates/index.html b/templates/index.html
index 112f3fd..cab7ec3 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -12805,315 +12805,326 @@ document.addEventListener('mousedown', function(e) {
       <button class="btn" onclick="document.getElementById('propagate-modal-overlay').classList.remove('open')">Cancel</button>
       <button class="btn btn-accent" id="propagate-run-btn" onclick="runPropagation()">Propagate &amp; Fit</button>
     </div>
   </div>
 </div>
 
 <!-- Local Fit Warning Modal -->
 <div id="localfit-warn-overlay" class="xps-modal-overlay" onclick="if(event.target===this)this.classList.remove('open')">
   <div class="xps-modal" style="max-width:460px;border-color:var(--amber,#f59e0b)">
     <h3 style="color:var(--amber,#f59e0b)">&#9888; Warning: Local Fit Performed <button class="btn btn-sm" onclick="document.getElementById('localfit-warn-overlay').classList.remove('open')">&#x2715;</button></h3>
     <p style="font-size:12px;color:var(--text);line-height:1.6;margin:0 0 10px">The server fitting engine (lmfit) did not respond. A simplified local fit was used instead. Results may be less accurate.</p>
     <p style="font-size:11px;color:var(--text2);line-height:1.6;margin:0 0 12px"><strong style="color:var(--text)">Possible causes:</strong><br>
     &bull; The server may be offline or restarting<br>
     &bull; The fit request may have timed out<br>
     &bull; Network connection issue</p>
     <p style="font-size:11px;color:var(--text2);line-height:1.6;margin:0 0 12px">Try clicking <strong>Run Fit</strong> again. If the problem persists, check that the server is running.</p>
     <div class="dialog-btns">
       <button class="btn btn-accent" onclick="document.getElementById('localfit-warn-overlay').classList.remove('open')">Dismiss</button>
     </div>
   </div>
 </div>
 
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
 
 <!-- Fit History Floating Panel -->
 <div id="history-panel">
   <div id="history-panel-titlebar">
     <span>Fit History</span>
     <button class="btn btn-sm" onclick="_closeHistoryPanel()" style="padding:1px 6px">&#x2715;</button>
   </div>
   <div id="history-panel-body">
     <p style="font-size:10px;color:var(--text3);margin:0 0 8px;line-height:1.5">Auto-saved after each fit (max 10). Preview overlays in orange.</p>
     <div id="history-compare-info"></div>
     <div id="history-list"></div>
     <div style="margin-top:8px;display:flex;gap:6px;justify-content:flex-end">
       <button class="btn btn-sm" onclick="_historyClearPreview()">Clear Preview</button>
       <button class="btn btn-sm" onclick="_closeHistoryPanel()">Close</button>
     </div>
   </div>
 </div>
 
 <!-- Multiplet preset selection modal -->
 <div id="multiplet-modal-overlay" onclick="if(event.target===this)_closeMultipletModal()">
   <div id="multiplet-modal">
     <div id="multiplet-modal-header">
       <h3>SELECT SPIN-ORBIT PAIR</h3>
       <button class="btn btn-sm" onclick="_closeMultipletModal()">✕</button>
     </div>
     <div id="multiplet-modal-search">
       <input type="text" id="multiplet-modal-input" placeholder="Search element or orbital…" oninput="_filterMultipletModal(this.value)" autocomplete="off">
     </div>
     <div id="multiplet-modal-list"></div>
   </div>
 </div>
 <!-- ═══════════════════════════════════════════════════════════════════
      Find Peaks (beta) — opt-in grammar-driven analysis (spec §5A/§8).
      STRICTLY ADDITIVE: the manual fit path (/api/fit, Run Fit, peak
      editing) is untouched.  Results are candidate models + per-peak
      confidence + ambiguity flags; a NAMED human review is required
      before anything is applied to the tab. ═══════════════════════════ -->
 <div id="find-peaks-overlay" class="xps-modal-overlay" onclick="if(event.target===this)this.classList.remove('open')">
   <div class="xps-modal" id="find-peaks-modal-box" style="max-width:680px;max-height:86vh;overflow-y:auto">
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
         <select id="fp-material" class="btn" style="width:100%" onchange="_fpMaterialChanged()"></select>
       </label>
       <label style="font-size:11px" id="fp-method-label">Method
         <select id="fp-method" class="btn" style="width:100%" onchange="_fpMethodChanged()"></select>
       </label>
       <label style="font-size:11px;grid-column:1 / -1" id="fp-regions-label">Region(s) <small style="color:var(--text3)">(click an element for its levels; ctrl/&#8984;-click a level to fit two together)</small>
         <input type="text" id="fp-regions-filter" placeholder="Search element, name, or level (e.g. Fe, iron, 2p)…"
                autocomplete="off" style="width:100%;font-family:var(--mono);font-size:11px;padding:4px 8px;margin:2px 0 4px;
                background:var(--bg2);border:1px solid var(--border2);border-radius:var(--radius);color:var(--text1);box-sizing:border-box"
                oninput="_fpFilterRegions(this.value)">
         <div id="fp-search-dropdown"></div>
         <div class="fp-legend" id="fp-legend"></div>
         <div id="fp-pt-grid" role="group" aria-label="Periodic table region picker"></div>
         <div id="fp-expanded-panel" class="fp-expanded-panel"></div>
         <div id="fp-regions-tier-note" style="font-size:9.5px;color:var(--text3);margin-top:3px;line-height:1.4"></div>
       </label>
       <div style="font-size:11px;grid-column:1 / -1">
         <div id="fp-material-hint" style="color:var(--text3);font-size:10px;line-height:1.45;margin-bottom:6px"></div>
         <div id="fp-method-hint" style="color:var(--text3);font-size:10px;line-height:1.45;margin-bottom:6px"></div>
         <div id="fp-simple-options"></div>
         <details id="fp-advanced" style="margin-top:6px">
           <summary style="font-size:10px;color:var(--text3);cursor:pointer">Advanced (edit as JSON)</summary>
           <textarea id="fp-options" spellcheck="false" style="width:100%;height:72px;font-family:monospace;font-size:10px;background:var(--bg2);color:var(--text1);border:1px solid var(--border);margin-top:4px"></textarea>
         </details>
       </div>
     </div>
     <div style="display:flex;gap:8px;align-items:center;margin-bottom:10px">
       <button class="btn btn-accent" id="fp-run" onclick="runFindPeaks()">Suggest peaks</button>
       <span id="fp-spinner" class="fp-spinner" style="display:none"></span>
       <span id="fp-status" style="font-size:11px;color:var(--text2)"></span>
     </div>
     <div id="fp-results" style="display:none">
       <div id="fp-flags"></div>
       <h4 style="font-size:11px;margin:10px 0 4px">Suggested peaks</h4>
       <div style="overflow-x:auto"><table id="fp-peaks" style="width:100%;font-size:10px;border-collapse:collapse"></table></div>
       <h4 style="font-size:11px;margin:10px 0 4px" title="Every peak model that was tried for this region, ranked by how well the data supports it.">Other models compared</h4>
       <div style="overflow-x:auto"><table id="fp-cands" style="width:100%;font-size:10px;border-collapse:collapse"></table></div>
       <details style="margin-top:8px">
         <summary style="font-size:10px;color:var(--text3);cursor:pointer">Technical details</summary>
         <div id="fp-message-plain" style="font-size:10.5px;color:var(--text2);margin:4px 0;line-height:1.5"></div>
         <details style="margin-top:4px">
           <summary style="font-size:9.5px;color:var(--text3);cursor:pointer">Advanced (raw engine output)</summary>
           <div id="fp-message" style="font-size:10px;color:var(--text3);margin:4px 0;font-family:monospace;white-space:pre-wrap"></div>
         </details>
       </details>
       <div style="margin-top:12px;padding-top:10px;border-top:1px solid var(--border);display:flex;gap:8px;align-items:center">
         <button class="btn" id="fp-apply" onclick="applyFindPeaks()"
                 title="Replaces this tab's current peaks with the suggested ones. You can undo this.">Add peaks to my fit</button>
       </div>
       <p id="fp-apply-note" style="font-size:10px;color:var(--text3);margin:6px 0 0"></p>
     </div>
   </div>
 </div>
 
 <!-- Find Peaks — apply confirmation (statistically generated, unverified) -->
 <div id="find-peaks-apply-confirm-overlay" class="xps-modal-overlay" onclick="if(event.target===this)_findPeaksApplyConfirmCancel()">
   <div class="xps-modal" style="max-width:440px">
     <h3>Add suggested peaks?
       <button class="btn btn-sm" onclick="_findPeaksApplyConfirmCancel()">&#x2715;</button>
     </h3>
     <p style="font-size:11px;color:var(--text2);line-height:1.5;margin:0 0 14px">
       These are statistically generated peaks offered as a starting point,
       not verified results — it's your responsibility to check them
       against your chemistry before use.
     </p>
     <div class="dialog-btns">
       <button class="btn" onclick="_findPeaksApplyConfirmCancel()">Cancel</button>
       <button class="btn btn-accent" id="find-peaks-apply-confirm-proceed">Add anyway</button>
     </div>
   </div>
 </div>
 
 <script>
 // ── Find Peaks (beta) — all logic self-contained in this block ──────────
 let _fpMeta = null;        // /api/analyze/meta cache
 let _fpLast = null;        // last analysis result (for apply)
 
 // ── Find Peaks region-selector coverage tier (2026-07-11, unit 3) ─────────
 // FP's own vocabulary — grades whether Find Peaks has CITED FITTING
 // GRAMMAR for a region.  Deliberately DISTINCT from RefCore's
 // tierColor/tierNote (curated/machine/legacy), which grades a REFERENCE
 // ENERGY VALUE's provenance for the separate Reference/Identify palette —
 // see autofit/coverage_index.py's module docstring for why the same word
 // ("curated") means something different in each system, and why that's
 // intentional rather than an inconsistency to fix.
 const FP_TIER_META = {
   curated:        { color: '#3ddc84', tag: '[cited]',
                     label: 'Cited fit recipe' },
   machine:        { color: '#b48eff', tag: '[sourced]',
                     label: 'Sourced reference position' },
   structure_only: { color: '#8a9ab8', tag: '[structure only]',
                     label: 'No reference position' },
 };
 
 // One coverage entry + a search query -> does it match? Case-insensitive
 // substring match against the region label, element symbol, element name,
 // and level/subshell — matches how a chemist would actually search
 // ("Fe", "iron", "2p", "Fe 2p" all find the same entry).
 function _fpRegionMatchesFilter(entry, query) {
   const q = String(query == null ? '' : query).trim().toLowerCase();
   if (!q) return true;
   const hay = [entry.region, entry.symbol, entry.name, entry.level]
     .map(v => String(v || '').toLowerCase());
   return hay.some(h => h.includes(q));
 }
 
 // One coverage entry -> its <option> display text: tier tag + region +
 // element name, so the tier is legible even where <option> styling is
 // ignored (some browsers/screen readers) — color is a second, not the
 // only, channel.
 function _fpRegionOptionLabel(entry) {
   const meta = FP_TIER_META[entry.tier] || FP_TIER_META.structure_only;
   return meta.tag + ' ' + entry.region + ' — ' + entry.name;
 }
 
 // The full coverage array + a search query -> the option list to render
 // (value/label/tier per entry). Pure — used by both the initial modal
 // population and the live filter-input handler. Total: a missing/empty
 // coverage array or an unmatched query both degrade to [], never throw.
 function _fpBuildRegionOptions(coverage, query) {
   return (coverage || [])
     .filter(e => _fpRegionMatchesFilter(e, query))
     .map(e => ({ value: e.region, label: _fpRegionOptionLabel(e), tier: e.tier }));
 }
 
 // The currently-selected coverage entries -> the honesty note shown below
 // the selector (goal: "never shown as if it had cited grammar"). Total:
 // no selection -> ''.
 function _fpTierNoteFor(entries) {
   const list = entries || [];
   if (!list.length) return '';
   if (list.length === 1) {
     const meta = FP_TIER_META[list[0].tier] || FP_TIER_META.structure_only;
     return meta.label + ': ' + list[0].note;
   }
   return list.map(e => {
     const meta = FP_TIER_META[e.tier] || FP_TIER_META.structure_only;
     return e.region + ' (' + meta.label + ')';
   }).join(' · ');
 }
 
 // ═══ ALL user-facing wording lives HERE (one place, easy to iterate). ═══
 // Audience: bench chemists/spectroscopists. Engine jargon (grammar,
 // candidate-model, decisive_override, +bfix, role slugs) must never reach
 // the screen — the honest CONTENT stays, said plainly.
 const FP_STRINGS = {
   blurb: 'Suggests a set of peaks for the region(s) you select and shows ' +
          'how confident it is. These are <b>starting suggestions to ' +
          'review — not final answers</b>. Nothing changes your manual fit ' +
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
   materials: {
     mixed: {
       label: 'mixed (analyte in matrix)',
       hint: 'Your sample is an analyte embedded in a different matrix, ' +
             'which can charge differently under x-rays than the matrix ' +
             'does (differential charging). For C 1s, contamination/' +
             'adventitious peak width limits are relaxed accordingly — ' +
             'other regions are unaffected. The charge reference ' +
             'calibrates the MATRIX’s potential — it may not apply to the ' +
             'analyte, so reported positions carry additional, ' +
             'unquantified uncertainty. This does not correct for that ' +
             'uncertainty; it only stops assuming there isn’t any.',
     },
   },
   tips: {
     material: 'Conducting samples charge-correct differently from ' +
               'insulating ones, and the suggested peak shapes differ too. ' +
               'Pick what best describes YOUR sample.',
     method: 'How the suggestions are generated. Hover (or select) an ' +
             'option below to see what it does and when to use it — ' +
             '“Compare peak models” fits most regions; the others trade ' +
             'speed for confidence ranges, a quick estimate, or refitting ' +
             'peaks you already placed.',
     regions: 'Which core-level region(s) to model. Pick the region this ' +
              'scan covers; ctrl-click two if one scan genuinely contains ' +
              'both (e.g. N 1s inside a U 4f window).',
     chi2r: 'Goodness of fit: about 1 means the model matches the data ' +
            'within noise; higher means the model is missing structure.',
     bic: 'Ranking score used to compare models — lower is better. Extra ' +
          'peaks are only rewarded when the data genuinely supports them.',
     sigmaCenter: 'Statistical uncertainty in the fitted peak position (eV).',
     position: 'Fitted peak position, binding energy (eV).',
     width: 'Fitted peak width, FWHM (eV).',
     height: 'Fitted peak height (counts).',
     shape: 'Line shape used for this peak.',
     status: 'How this model fared: the best-supported one wins; others ' +
             'are kept for comparison or rejected with the reason shown.',
   },
   methods: {
     ic_model_comparison: {
       label: 'Compare peak models (recommended)',
       hint: 'Tries several physically sensible peak models for the ' +
             'region, checks each for stability and plausibility, and ' +
             'reports the best-supported one. Use this first for most ' +
             'regions. Usually seconds to a minute.',
     },
     bayesian_exchange_mc: {
       label: 'Compare peak models + confidence ranges (slower)',
       hint: 'Does the same comparison, but samples many fits to attach ' +
             'confidence ranges to the result. Use this when you need an ' +
             'uncertainty estimate, not just a single best answer. Can ' +
             'take several minutes.',
     },
     sparse_map: {
       label: 'Quick peak count (approximate)',
       hint: 'A fast first look that estimates how many peaks are ' +
             'present. Positions are approximate — use this to get ' +
             'oriented, then follow up with “Compare peak models”.',
     },
     least_squares: {
       label: 'Refit my current peaks',
       hint: 'Refits the peaks already on this tab, using their current ' +
             'shapes and positions as the starting point. Use this to ' +
             'polish a fit you’ve already built manually — add peaks first.',
     },
   },
   // friendly controls per method — each writes into the Advanced JSON so
   // the request itself is unchanged (values only, no new behavior)
   controls: {
     ic_model_comparison: [
       { key: 'n_refits', type: 'number', min: 1, max: 32, step: 1,
         label: 'Stability re-fits',
         tip: 'How many times each model is re-fitted from different ' +
              'starting points to check the answer is stable. More is ' +
              'slower but more reliable.' },
       { key: 'enable_proposal_pass', type: 'checkbox',
         label: 'Look for unexpected extra peaks',
@@ -13364,160 +13375,161 @@ function _fpPlainMessage(body) {
       'each option was set aside.');
     return parts.join(' ');
   }
   const unassignedPeaks = (body.peaks || []).filter(p => p.region === 'unassigned');
   if (unassignedPeaks.length) {
     const centers = unassignedPeaks.map(p => (+p.center).toFixed(2)).join(', ');
     parts.push(`Found ${unassignedPeaks.length} extra peak(s) at ${centers} eV ` +
       'that aren’t part of a known chemical assignment for this region — ' +
       'their positions come directly from your data, not a reference table, ' +
       'so please review and assign them yourself.');
   }
   if (d.conditional) {
     if (d.conditional_reason === 'decisive_override') {
       const fixed = (d.winner_boundary_fixed_params || []).map(_fpParamLabel).join(', ');
       parts.unshift(`CONDITIONAL — the best-supported model ` +
         `(${_fpModelLabel(d.winner)}) only fits well with ` +
         `${fixed || 'some parameters'} pinned at their limits. Equally ` +
         'clean alternatives are shown in the comparison table below and ' +
         'are worth a look.');
     } else if (d.conditional_reason === 'unstable_last_resort') {
       parts.unshift('LOW CONFIDENCE — no model held together consistently ' +
         'when re-fit from different starting points, so component ' +
         `identities aren’t reliable here. Showing the best-converged ` +
         `attempt (${_fpModelLabel(d.winner)}) so you can see what the data ` +
         'roughly supports — treat every peak as a rough suggestion; the ' +
         'data may not clearly separate one broad feature from several ' +
         'overlapping ones.');
     } else {
       const hits = (d.winner_boundary_hits || []).map(_fpBoundaryHitLabel).join(', ');
       parts.unshift('CONDITIONAL — no model passed every plausibility ' +
         'check cleanly, so this is the best of the stable-but-limited ' +
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
 
 function _fpFmt(tpl, vars) {
   return tpl.replace(/\{(\w+)\}/g, (_, k) => vars[k] != null ? vars[k] : '');
 }
 
 async function openFindPeaksModal() {
   if (!state.rawBE || !state.rawBE.length) {
     notify('Load a spectrum first — Find Peaks runs on the active tab.', 'amber');
     return;
   }
   try {
     if (!_fpMeta) {
       const r = await fetch('/api/analyze/meta');
       _fpMeta = await r.json();
     }
   } catch (e) {
     notify('Find Peaks backend unavailable: ' + e.message, 'amber');
     return;
   }
   // all wording from FP_STRINGS; server strings escaped even though
   // currently code-controlled (a future registered label must never
   // become an injection point)
   document.getElementById('fp-blurb').innerHTML = FP_STRINGS.blurb;
   document.getElementById('fp-apply-note').textContent = FP_STRINGS.applyNote;
+  _fpMaybeShowExperimentalNotice();
   document.getElementById('fp-material-label').title = FP_STRINGS.tips.material;
   document.getElementById('fp-method-label').title = FP_STRINGS.tips.method;
   document.getElementById('fp-regions-label').title = FP_STRINGS.tips.regions;
   const mat = document.getElementById('fp-material');
   mat.innerHTML = _fpMeta.material_classes
     .map(m => {
       const s = FP_STRINGS.materials[m] || {};
       const title = s.hint ? ` title="${_fpEsc(s.hint)}"` : '';
       return `<option value="${_fpEsc(m)}"${title}>${_fpEsc(s.label || m)}</option>`;
     }).join('');
   _fpMaterialChanged();
   document.getElementById('fp-regions-filter').value = '';
   _fpRegionsSelected = new Set();
   _fpExpandedElement = null;
   _fpRenderLegend();
   _fpRenderPtGrid('');
   _fpRenderSearchDropdown('');
   _fpRenderExpandedPanel();
   document.getElementById('fp-regions-tier-note').textContent = '';
   const meth = document.getElementById('fp-method');
   meth.innerHTML = _fpMeta.methods
     .map(m => {
       const s = FP_STRINGS.methods[m.id] || {};
       // hovering an option (even before selecting it) shows the SAME
       // plain-English explanation as the hint box below the dropdown —
       // no jargon, and no need to select first just to learn what an
       // option does. Previously showed the raw backend label here
       // (e.g. "Auto — model comparison (IC)"), which read as vague/
       // jargon-y "the tooltip" per the 2026-07-14 bug report.
       return `<option value="${_fpEsc(m.id)}" title="${_fpEsc(s.hint || s.label || m.label || m.id)}">${_fpEsc(s.label || m.label || m.id)}</option>`;
     }).join('');
   meth.value = 'ic_model_comparison';
   _fpMethodChanged();
   document.getElementById('fp-results').style.display = 'none';
   document.getElementById('fp-status').textContent = '';
   _fpResetModalPosition();
   document.getElementById('find-peaks-overlay').classList.add('open');
 }
 
 function closeFindPeaksModal() {
   document.getElementById('find-peaks-overlay').classList.remove('open');
 }
 
 // ── Draggable modal (2026-07-11) ────────────────────────────────────────
 // Same technique as the Reference palette's _refPaletteDragStart/Move/End
 // (static/js/ref_identify_core.js RefCore.clampToViewport is the shared,
 // tested clamp math) — but scoped to ONLY the Find Peaks modal: every
 // other .xps-modal in the app stays centered/non-draggable.
 
 let _fpModalDrag = null;
 
 // True for the close button (or any future control placed in the header)
 // — those must still work; only the bare header background starts a drag.
 // (`instanceof Element` guard: a text-node event target lacks .closest —
 // see CLAUDE.md Known Issues re: the same class of bug elsewhere.)
 function _fpIsDragBlockingTarget(target) {
   return !!(target instanceof Element && target.closest('button, select, input, a, textarea'));
 }
 
 function _fpClampModal(left, top) {
   const el = document.getElementById('find-peaks-modal-box');
   const w = el ? el.offsetWidth : 680, h = el ? el.offsetHeight : 400;
   return RefCore.clampToViewport(left, top, w, h, window.innerWidth, window.innerHeight, 8);
 }
 
 function _fpModalDragStart(e) {
   if (_fpIsDragBlockingTarget(e.target)) return;
   const el = document.getElementById('find-peaks-modal-box');
   if (!el) return;
   const r = el.getBoundingClientRect();
   // First drag: switch from flex-centered to absolutely positioned,
   // pinned at its CURRENT visual spot so there is no jump.
   el.style.position = 'fixed';
   el.style.left = r.left + 'px'; el.style.top = r.top + 'px';
   el.style.margin = '0';
   _fpModalDrag = { dx: e.clientX - r.left, dy: e.clientY - r.top };
   el.classList.add('dragging');
   document.addEventListener('mousemove', _fpModalDragMove, true);
   document.addEventListener('mouseup', _fpModalDragEnd, true);
   e.preventDefault();
@@ -13682,160 +13694,178 @@ function _fpRenderSearchDropdown(query) {
   const box = document.getElementById('fp-search-dropdown');
   if (!box) return;
   const q = String(query == null ? '' : query).trim();
   if (!q) { box.innerHTML = ''; return; }
   const coverage = ((_fpMeta && _fpMeta.coverage) || []).filter(e => e.practical);
   const opts = _fpBuildRegionOptions(coverage, q).slice(0, 8);
   if (!opts.length) { box.innerHTML = ''; return; }
   const rows = opts.map(o => {
     const meta = FP_TIER_META[o.tier] || FP_TIER_META.structure_only;
     const entry = coverage.find(e => e.region === o.value);
     return `<div class="fp-search-dropdown-item" style="--tier-c:${meta.color}"` +
       ` tabindex="0" role="button"` +
       ` onclick="_fpPickFromSearch('${_fpEsc(o.value)}', event.ctrlKey||event.metaKey)"` +
       ` onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();_fpPickFromSearch('${_fpEsc(o.value)}', event.ctrlKey||event.metaKey)}">` +
       `<span>${meta.tag} ${_fpEsc(o.value)}</span>` +
       `<span class="fp-sdi-name">${_fpEsc(entry ? entry.name : '')}</span></div>`;
   }).join('');
   box.innerHTML = `<div class="fp-search-dropdown">${rows}</div>`;
 }
 
 function _fpPickFromSearch(region, additive) {
   const coverage = (_fpMeta && _fpMeta.coverage) || [];
   const entry = coverage.find(e => e.region === region);
   if (entry) _fpExpandedElement = entry.symbol;
   _fpToggleRegion(region, additive);
   const box = document.getElementById('fp-search-dropdown');
   if (box) box.innerHTML = '';
 }
 
 function _fpFilterRegions(query) {
   _fpRenderPtGrid(query);
   _fpRenderSearchDropdown(query);
 }
 
 // Pure selection-set logic (DOM-free, unit-testable): a plain click
 // REPLACES the selection with just that region (matches how a single
 // click reads); ctrl/cmd-click toggles membership without disturbing the
 // rest (goal: "preserve the existing multi-region selection (ctrl-click
 // to fit two together)"). Returns a NEW Set — never mutates `current`.
 function _fpNextSelection(current, region, additive) {
   if (additive) {
     const next = new Set(current);
     if (next.has(region)) next.delete(region);
     else next.add(region);
     return next;
   }
   if (current.size === 1 && current.has(region)) return current;
   return new Set([region]);
 }
 
 function _fpToggleRegion(region, additive) {
   _fpRegionsSelected = _fpNextSelection(_fpRegionsSelected, region, additive);
   _fpSyncSelectionUI();
 }
 
 function _fpSyncSelectionUI() {
   const values = Array.from(_fpRegionsSelected);
   const coverage = (_fpMeta && _fpMeta.coverage) || [];
   const entries = values.map(v => coverage.find(e => e.region === v))
     .filter(Boolean);
   document.getElementById('fp-regions-tier-note').textContent =
     _fpTierNoteFor(entries);
   // ROI auto-fill: only for an UNAMBIGUOUS single-region pick with a real
   // hint — a co-fit selection (2 regions) has no single "right" window,
   // and a structure_only region honestly has no hint to offer (goal:
   // never invent a window; the note above says so, ROI is left alone).
   if (entries.length === 1 && entries[0].roi) {
     document.getElementById('roi-min').value = entries[0].roi.be_min;
     document.getElementById('roi-max').value = entries[0].roi.be_max;
   }
   _fpRenderPtGrid(document.getElementById('fp-regions-filter').value);
   _fpRenderExpandedPanel();
 }
 
 function _fpMaterialChanged() {
   const v = document.getElementById('fp-material').value;
   const s = FP_STRINGS.materials[v] || {};
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
   const strs = FP_STRINGS.methods[id] || {};
   document.getElementById('fp-method-hint').textContent = strs.hint || '';
   // the Advanced JSON stays the single source of truth for the request —
   // the friendly controls below are a labeled VIEW that writes into it
   document.getElementById('fp-options').value =
     JSON.stringify((m && m.default_options) || {}, null, 1);
   _fpBuildSimpleControls(id);
 }
 
 function _fpBuildSimpleControls(methodId) {
   const host = document.getElementById('fp-simple-options');
   const defs = FP_STRINGS.controls[methodId] || [];
   host.innerHTML = '';
   if (!defs.length) {
     const p = document.createElement('div');
     p.style.cssText = 'font-size:10px;color:var(--text3)';
     p.textContent = FP_STRINGS.controls._none;
     host.appendChild(p);
     return;
   }
   let opts = {};
   try { opts = JSON.parse(document.getElementById('fp-options').value || '{}'); }
   catch (e) { opts = {}; }
   for (const def of defs) {
     const row = document.createElement('label');
     row.style.cssText = 'display:flex;align-items:center;gap:6px;' +
       'font-size:11px;margin:3px 0';
     row.title = def.tip;
     let input;
     if (def.type === 'checkbox') {
       input = document.createElement('input');
       input.type = 'checkbox';
       input.checked = !!opts[def.key];
     } else if (def.type === 'select') {
       input = document.createElement('select');
       input.className = 'btn';
       for (const [v, text] of def.choices) {
         const o = document.createElement('option');
         o.value = v; o.textContent = text;
         input.appendChild(o);
       }
       if (opts[def.key] != null) input.value = String(opts[def.key]);
     } else {
       input = document.createElement('input');
       input.type = 'number';
       input.min = def.min; input.max = def.max; input.step = def.step;
       input.style.cssText = 'width:72px;font-size:11px;background:var(--bg2);' +
         'color:var(--text1);border:1px solid var(--border);padding:2px 4px';
       if (opts[def.key] != null) input.value = opts[def.key];
     }
     input.id = 'fp-opt-' + def.key;
     input.addEventListener('change', () => _fpSyncOptionsFromControls(methodId));
     const span = document.createElement('span');
     span.textContent = def.label;
     if (def.type === 'checkbox') { row.appendChild(input); row.appendChild(span); }
     else { row.appendChild(span); row.appendChild(input); }
     host.appendChild(row);
   }
 }
 
 function _fpSyncOptionsFromControls(methodId) {
   // controls write INTO the JSON (unknown/advanced keys preserved) — the
   // request path is unchanged; this is purely a friendlier way to edit it
   let opts = {};
   try { opts = JSON.parse(document.getElementById('fp-options').value || '{}'); }
   catch (e) { opts = {}; }
   for (const def of (FP_STRINGS.controls[methodId] || [])) {
     const el = document.getElementById('fp-opt-' + def.key);
     if (!el) continue;
     if (def.type === 'checkbox') opts[def.key] = el.checked;
     else if (def.type === 'select') opts[def.key] = el.value;
     else if (el.value !== '') opts[def.key] = Number(el.value);
   }
   document.getElementById('fp-options').value = JSON.stringify(opts, null, 1);
 }
 
 // ── Progress indicator (2026-07-11): pure formatting helpers ───────────────
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

exec
/bin/zsh -lc 'git show --stat --oneline --decorate 56b5d5a && git show --name-only --format=fuller 56b5d5a' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-OxFg1NVp' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-LInQs8wH' (errno=Operation not permitted)
56b5d5a feat(ui): one-time Find Peaks experimental notice
 templates/index.html                    | 30 +++++++++++++++
 tests/js/fp_experimental_notice.test.js | 67 +++++++++++++++++++++++++++++++++
 2 files changed, 97 insertions(+)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Zmp69q9g' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-W7MZXEm7' (errno=Operation not permitted)
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

templates/index.html
tests/js/fp_experimental_notice.test.js

codex
The commit is very small at the Git level: `56b5d5a` reports only `templates/index.html` and `tests/js/fp_experimental_notice.test.js`. I’m now checking the exact localStorage branch behavior and the backend timeout comments/constants instead of relying on the commit message.
exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '13035,13055p;13390,13435p;13690,13720p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
 13051	  // Label/hint override for one material-class dropdown option (2026-07-20).
 13052	  // Only "mixed" gets an entry — conductor/semiconductor/insulator render
 13053	  // exactly as before (bare backend value, no title attribute).
 13054	  materials: {
 13055	    mixed: {
 13390	        `(${_fpModelLabel(d.winner)}) only fits well with ` +
 13391	        `${fixed || 'some parameters'} pinned at their limits. Equally ` +
 13392	        'clean alternatives are shown in the comparison table below and ' +
 13393	        'are worth a look.');
 13394	    } else if (d.conditional_reason === 'unstable_last_resort') {
 13395	      parts.unshift('LOW CONFIDENCE — no model held together consistently ' +
 13396	        'when re-fit from different starting points, so component ' +
 13397	        `identities aren’t reliable here. Showing the best-converged ` +
 13398	        `attempt (${_fpModelLabel(d.winner)}) so you can see what the data ` +
 13399	        'roughly supports — treat every peak as a rough suggestion; the ' +
 13400	        'data may not clearly separate one broad feature from several ' +
 13401	        'overlapping ones.');
 13402	    } else {
 13403	      const hits = (d.winner_boundary_hits || []).map(_fpBoundaryHitLabel).join(', ');
 13404	      parts.unshift('CONDITIONAL — no model passed every plausibility ' +
 13405	        'check cleanly, so this is the best of the stable-but-limited ' +
 13406	        `options (${_fpModelLabel(d.winner)}). It hit some parameter ` +
 13407	        `limits (${hits || 'see below'}) — worth double-checking those components.`);
 13408	    }
 13409	  }
 13410	  if ((d.winner_unphysical_widths || []).length) {
 13411	    const widths = d.winner_unphysical_widths.map(_fpWidthFlagLabel).join('; ');
 13412	    parts.push(`LOW CONFIDENCE: ${widths}.`);
 13413	  }
 13414	  if (d.filtered_dominant_alternative) {
 13415	    const fda = d.filtered_dominant_alternative;
 13416	    parts.push(`Note: a different model (${_fpModelLabel(fda.name)}) scored ` +
 13417	      `better by ${(+fda.delta_bic_vs_winner).toFixed(1)} points but was set ` +
 13418	      `aside (${_fpFilterReasonLabel(fda.filter_reason).toLowerCase()}) — ` +
 13419	      'worth a look in the comparison table.');
 13420	  }
 13421	  if (d.analysis_truncated) {
 13422	    parts.push(`Only ${d.n_candidates_evaluated} of ${d.n_candidates_total} ` +
 13423	      'candidate models were checked before time ran out.');
 13424	  }
 13425	  if (!parts.length) {
 13426	    parts.push('This model passed every check cleanly — stable across ' +
 13427	      're-fits, no parameter limits hit, no unexplained extra peaks.');
 13428	  }
 13429	  return parts.join(' ');
 13430	}
 13431	
 13432	function _fpFmt(tpl, vars) {
 13433	  return tpl.replace(/\{(\w+)\}/g, (_, k) => vars[k] != null ? vars[k] : '');
 13434	}
 13435	
 13690	
 13691	// Up to 8 direct region matches while typing — a fast alternative to
 13692	// clicking through the grid (goal: type-ahead search alongside the grid).
 13693	function _fpRenderSearchDropdown(query) {
 13694	  const box = document.getElementById('fp-search-dropdown');
 13695	  if (!box) return;
 13696	  const q = String(query == null ? '' : query).trim();
 13697	  if (!q) { box.innerHTML = ''; return; }
 13698	  const coverage = ((_fpMeta && _fpMeta.coverage) || []).filter(e => e.practical);
 13699	  const opts = _fpBuildRegionOptions(coverage, q).slice(0, 8);
 13700	  if (!opts.length) { box.innerHTML = ''; return; }
 13701	  const rows = opts.map(o => {
 13702	    const meta = FP_TIER_META[o.tier] || FP_TIER_META.structure_only;
 13703	    const entry = coverage.find(e => e.region === o.value);
 13704	    return `<div class="fp-search-dropdown-item" style="--tier-c:${meta.color}"` +
 13705	      ` tabindex="0" role="button"` +
 13706	      ` onclick="_fpPickFromSearch('${_fpEsc(o.value)}', event.ctrlKey||event.metaKey)"` +
 13707	      ` onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();_fpPickFromSearch('${_fpEsc(o.value)}', event.ctrlKey||event.metaKey)}">` +
 13708	      `<span>${meta.tag} ${_fpEsc(o.value)}</span>` +
 13709	      `<span class="fp-sdi-name">${_fpEsc(entry ? entry.name : '')}</span></div>`;
 13710	  }).join('');
 13711	  box.innerHTML = `<div class="fp-search-dropdown">${rows}</div>`;
 13712	}
 13713	
 13714	function _fpPickFromSearch(region, additive) {
 13715	  const coverage = (_fpMeta && _fpMeta.coverage) || [];
 13716	  const entry = coverage.find(e => e.region === region);
 13717	  if (entry) _fpExpandedElement = entry.symbol;
 13718	  _fpToggleRegion(region, additive);
 13719	  const box = document.getElementById('fp-search-dropdown');
 13720	  if (box) box.innerHTML = '';

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

exec
/bin/zsh -lc "nl -ba app.py | sed -n '900,950p'; nl -ba autofit/engine.py | sed -n '150,195p;245,280p;2768,2788p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
  2768	            "evaluation: %s", len(candidates), n_cand,
  2769	            [m.name for m in candidates])
  2770	
  2771	    for idx, model in enumerate(candidates, 1):
  2772	        # Pre-check with the candidate's own worst-case budget: a candidate
  2773	        # STARTED just under the wire used to overshoot the sweep budget by
  2774	        # its full stability + proposal cost (measured 310 s wall vs the
  2775	        # 240 s budget on real data — past the gunicorn --timeout 300, i.e.
  2776	        # the exact worker-kill this budget exists to prevent).  Truncating
  2777	        # BEFORE starting a candidate that cannot finish keeps the worst-case
  2778	        # wall ≈ TOTAL_ANALYSIS_TIMEOUT_SEC.
  2779	        elapsed = time.perf_counter() - sweep_start
  2780	        if elapsed > TOTAL_ANALYSIS_TIMEOUT_SEC - CANDIDATE_TIMEOUT_SEC:
  2781	            analysis_truncated = True
  2782	            log.warning(
  2783	                "compare_models: sweep budget cannot fit another candidate "
  2784	                "(%.0fs elapsed of %.0fs) after %d/%d — remaining candidates "
  2785	                "skipped, returning best-so-far",
  2786	                elapsed, TOTAL_ANALYSIS_TIMEOUT_SEC, n_evaluated, len(candidates),
  2787	            )
  2788	            break

exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '12855,12905p;13720,13755p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
 12855	      <button class="btn btn-sm" onclick="_historyClearPreview()">Clear Preview</button>
 12856	      <button class="btn btn-sm" onclick="_closeHistoryPanel()">Close</button>
 12857	    </div>
 12858	  </div>
 12859	</div>
 12860	
 12861	<!-- Multiplet preset selection modal -->
 12862	<div id="multiplet-modal-overlay" onclick="if(event.target===this)_closeMultipletModal()">
 12863	  <div id="multiplet-modal">
 12864	    <div id="multiplet-modal-header">
 12865	      <h3>SELECT SPIN-ORBIT PAIR</h3>
 12866	      <button class="btn btn-sm" onclick="_closeMultipletModal()">✕</button>
 12867	    </div>
 12868	    <div id="multiplet-modal-search">
 12869	      <input type="text" id="multiplet-modal-input" placeholder="Search element or orbital…" oninput="_filterMultipletModal(this.value)" autocomplete="off">
 12870	    </div>
 12871	    <div id="multiplet-modal-list"></div>
 12872	  </div>
 12873	</div>
 12874	<!-- ═══════════════════════════════════════════════════════════════════
 12875	     Find Peaks (beta) — opt-in grammar-driven analysis (spec §5A/§8).
 12876	     STRICTLY ADDITIVE: the manual fit path (/api/fit, Run Fit, peak
 12877	     editing) is untouched.  Results are candidate models + per-peak
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
 12893	      </label>
 12894	      <label style="font-size:11px" id="fp-method-label">Method
 12895	        <select id="fp-method" class="btn" style="width:100%" onchange="_fpMethodChanged()"></select>
 12896	      </label>
 12897	      <label style="font-size:11px;grid-column:1 / -1" id="fp-regions-label">Region(s) <small style="color:var(--text3)">(click an element for its levels; ctrl/&#8984;-click a level to fit two together)</small>
 12898	        <input type="text" id="fp-regions-filter" placeholder="Search element, name, or level (e.g. Fe, iron, 2p)…"
 12899	               autocomplete="off" style="width:100%;font-family:var(--mono);font-size:11px;padding:4px 8px;margin:2px 0 4px;
 12900	               background:var(--bg2);border:1px solid var(--border2);border-radius:var(--radius);color:var(--text1);box-sizing:border-box"
 12901	               oninput="_fpFilterRegions(this.value)">
 12902	        <div id="fp-search-dropdown"></div>
 12903	        <div class="fp-legend" id="fp-legend"></div>
 12904	        <div id="fp-pt-grid" role="group" aria-label="Periodic table region picker"></div>
 12905	        <div id="fp-expanded-panel" class="fp-expanded-panel"></div>
 13720	  if (box) box.innerHTML = '';
 13721	}
 13722	
 13723	function _fpFilterRegions(query) {
 13724	  _fpRenderPtGrid(query);
 13725	  _fpRenderSearchDropdown(query);
 13726	}
 13727	
 13728	// Pure selection-set logic (DOM-free, unit-testable): a plain click
 13729	// REPLACES the selection with just that region (matches how a single
 13730	// click reads); ctrl/cmd-click toggles membership without disturbing the
 13731	// rest (goal: "preserve the existing multi-region selection (ctrl-click
 13732	// to fit two together)"). Returns a NEW Set — never mutates `current`.
 13733	function _fpNextSelection(current, region, additive) {
 13734	  if (additive) {
 13735	    const next = new Set(current);
 13736	    if (next.has(region)) next.delete(region);
 13737	    else next.add(region);
 13738	    return next;
 13739	  }
 13740	  if (current.size === 1 && current.has(region)) return current;
 13741	  return new Set([region]);
 13742	}
 13743	
 13744	function _fpToggleRegion(region, additive) {
 13745	  _fpRegionsSelected = _fpNextSelection(_fpRegionsSelected, region, additive);
 13746	  _fpSyncSelectionUI();
 13747	}
 13748	
 13749	function _fpSyncSelectionUI() {
 13750	  const values = Array.from(_fpRegionsSelected);
 13751	  const coverage = (_fpMeta && _fpMeta.coverage) || [];
 13752	  const entries = values.map(v => coverage.find(e => e.region === v))
 13753	    .filter(Boolean);
 13754	  document.getElementById('fp-regions-tier-note').textContent =
 13755	    _fpTierNoteFor(entries);

exec
/bin/zsh -lc "git show --format='%H%n%P%n%s' --no-patch 56b5d5a" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-hEQBvelU' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-yWFHoUZv' (errno=Operation not permitted)
56b5d5ab899ed4c6e203a5efa8fa484931b46107
d13589d72ea97f8318083a90d233a5cf43ce869c
feat(ui): one-time Find Peaks experimental notice

codex
The runtime range is not invented: `app.py` already documents long analysis as `60-240s`, and `autofit/engine.py` has `TOTAL_ANALYSIS_TIMEOUT_SEC = 240.0` with comments tying the full sweep budget to that cap. The notice says “can take” and “depending on the region and method,” so it reads as a range, not a precise promise.
exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '13755,13795p;13435,13475p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
 13435	
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
 13793	  const id = document.getElementById('fp-method').value;
 13794	  const m = (_fpMeta.methods || []).find(x => x.id === id);
 13795	  const strs = FP_STRINGS.methods[id] || {};

exec
/bin/zsh -lc 'git diff --name-status 56b5d5a''^ 56b5d5a && git diff --stat 56b5d5a''^ 56b5d5a && git diff --numstat 56b5d5a''^ 56b5d5a' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-9ARmIX1r' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ebEIhdex' (errno=Operation not permitted)
M	templates/index.html
A	tests/js/fp_experimental_notice.test.js
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-1ji088kg' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-IgeaqCgC' (errno=Operation not permitted)
 templates/index.html                    | 30 +++++++++++++++
 tests/js/fp_experimental_notice.test.js | 67 +++++++++++++++++++++++++++++++++
 2 files changed, 97 insertions(+)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-RvosPk9U' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-w1TZyaLb' (errno=Operation not permitted)
30	0	templates/index.html
67	0	tests/js/fp_experimental_notice.test.js

exec
/bin/zsh -lc 'node --test tests/js/fp_experimental_notice.test.js' in /Users/skyefortier/xps-verify
 succeeded in 144ms:
# Subtest: FP_STRINGS.experimentalNotice names it experimental and states the runtime range
ok 1 - FP_STRINGS.experimentalNotice names it experimental and states the runtime range
  ---
  duration_ms: 1.050474
  type: 'test'
  ...
# Subtest: FP_STRINGS.experimentalNotice says results are a starting point, not a final answer
ok 2 - FP_STRINGS.experimentalNotice says results are a starting point, not a final answer
  ---
  duration_ms: 0.206895
  type: 'test'
  ...
# Subtest: FP_STRINGS.experimentalNotice does not overclaim correctness or imply the app is frozen/broken during a long run
ok 3 - FP_STRINGS.experimentalNotice does not overclaim correctness or imply the app is frozen/broken during a long run
  ---
  duration_ms: 0.18977
  type: 'test'
  ...
# Subtest: the notice DOM wiring exists: banner element, dismiss handler, and a localStorage-backed one-time gate
ok 4 - the notice DOM wiring exists: banner element, dismiss handler, and a localStorage-backed one-time gate
  ---
  duration_ms: 1.395617
  type: 'test'
  ...
# Subtest: openFindPeaksModal calls the notice gate so it actually shows on open
ok 5 - openFindPeaksModal calls the notice gate so it actually shows on open
  ---
  duration_ms: 0.761959
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
# duration_ms 97.85621

codex
The exact gate is sound: on a present key it sets the banner to `display: none` and returns before text assignment or `display: block`; on an absent key it writes the notice text and shows the banner. Dismissal writes the same shared constant key and hides the banner.
exec
/bin/zsh -lc 'rg -n "localStorage" templates/index.html static tests app.py autofit || true' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
templates/index.html:10132:  localStorage.setItem('xps-theme', isLight ? 'light' : 'dark');
templates/index.html:10139:  if (localStorage.getItem('xps-theme') === 'light') {
templates/index.html:10882:    const o = JSON.parse(localStorage.getItem(REF_PALETTE_LS) || 'null');
templates/index.html:10888:    localStorage.setItem(REF_PALETTE_LS, JSON.stringify({ ...(_refLoadPaletteState() || {}), ...patch }));
templates/index.html:13778:  if (localStorage.getItem(FP_EXPERIMENTAL_NOTICE_LS_KEY)) {
templates/index.html:13788:  localStorage.setItem(FP_EXPERIMENTAL_NOTICE_LS_KEY, '1');
tests/test_browser_palette.py:152:        pg.evaluate("() => localStorage.setItem('xps.refPalette.v1', JSON.stringify({left:9000, top:9000}))")
tests/test_browser_palette.py:169:        pg.evaluate("() => localStorage.removeItem('xps.refPalette.v1')")
tests/js/fp_experimental_notice.test.js:7:// via localStorage.
tests/js/fp_experimental_notice.test.js:50:     + 'a localStorage-backed one-time gate', () => {
tests/js/fp_experimental_notice.test.js:57:  assert.match(fn, /localStorage\.setItem/);
tests/js/fp_experimental_notice.test.js:60:  assert.match(gate, /localStorage\.getItem/);

exec
/bin/zsh -lc 'git diff --unified=20 56b5d5a''^ 56b5d5a -- templates/index.html' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-sfWn42uG' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-QEbSzIXH' (errno=Operation not permitted)
diff --git a/templates/index.html b/templates/index.html
index 112f3fd..cab7ec3 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -12865,40 +12865,44 @@ document.addEventListener('mousedown', function(e) {
       <h3>SELECT SPIN-ORBIT PAIR</h3>
       <button class="btn btn-sm" onclick="_closeMultipletModal()">✕</button>
     </div>
     <div id="multiplet-modal-search">
       <input type="text" id="multiplet-modal-input" placeholder="Search element or orbital…" oninput="_filterMultipletModal(this.value)" autocomplete="off">
     </div>
     <div id="multiplet-modal-list"></div>
   </div>
 </div>
 <!-- ═══════════════════════════════════════════════════════════════════
      Find Peaks (beta) — opt-in grammar-driven analysis (spec §5A/§8).
      STRICTLY ADDITIVE: the manual fit path (/api/fit, Run Fit, peak
      editing) is untouched.  Results are candidate models + per-peak
      confidence + ambiguity flags; a NAMED human review is required
      before anything is applied to the tab. ═══════════════════════════ -->
 <div id="find-peaks-overlay" class="xps-modal-overlay" onclick="if(event.target===this)this.classList.remove('open')">
   <div class="xps-modal" id="find-peaks-modal-box" style="max-width:680px;max-height:86vh;overflow-y:auto">
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
         <select id="fp-material" class="btn" style="width:100%" onchange="_fpMaterialChanged()"></select>
       </label>
       <label style="font-size:11px" id="fp-method-label">Method
         <select id="fp-method" class="btn" style="width:100%" onchange="_fpMethodChanged()"></select>
       </label>
       <label style="font-size:11px;grid-column:1 / -1" id="fp-regions-label">Region(s) <small style="color:var(--text3)">(click an element for its levels; ctrl/&#8984;-click a level to fit two together)</small>
         <input type="text" id="fp-regions-filter" placeholder="Search element, name, or level (e.g. Fe, iron, 2p)…"
                autocomplete="off" style="width:100%;font-family:var(--mono);font-size:11px;padding:4px 8px;margin:2px 0 4px;
                background:var(--bg2);border:1px solid var(--border2);border-radius:var(--radius);color:var(--text1);box-sizing:border-box"
                oninput="_fpFilterRegions(this.value)">
         <div id="fp-search-dropdown"></div>
         <div class="fp-legend" id="fp-legend"></div>
         <div id="fp-pt-grid" role="group" aria-label="Periodic table region picker"></div>
         <div id="fp-expanded-panel" class="fp-expanded-panel"></div>
         <div id="fp-regions-tier-note" style="font-size:9.5px;color:var(--text3);margin-top:3px;line-height:1.4"></div>
       </label>
       <div style="font-size:11px;grid-column:1 / -1">
@@ -13020,40 +13024,47 @@ function _fpTierNoteFor(entries) {
     const meta = FP_TIER_META[list[0].tier] || FP_TIER_META.structure_only;
     return meta.label + ': ' + list[0].note;
   }
   return list.map(e => {
     const meta = FP_TIER_META[e.tier] || FP_TIER_META.structure_only;
     return e.region + ' (' + meta.label + ')';
   }).join(' · ');
 }
 
 // ═══ ALL user-facing wording lives HERE (one place, easy to iterate). ═══
 // Audience: bench chemists/spectroscopists. Engine jargon (grammar,
 // candidate-model, decisive_override, +bfix, role slugs) must never reach
 // the screen — the honest CONTENT stays, said plainly.
 const FP_STRINGS = {
   blurb: 'Suggests a set of peaks for the region(s) you select and shows ' +
          'how confident it is. These are <b>starting suggestions to ' +
          'review — not final answers</b>. Nothing changes your manual fit ' +
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
   materials: {
     mixed: {
       label: 'mixed (analyte in matrix)',
       hint: 'Your sample is an analyte embedded in a different matrix, ' +
             'which can charge differently under x-rays than the matrix ' +
             'does (differential charging). For C 1s, contamination/' +
             'adventitious peak width limits are relaxed accordingly — ' +
             'other regions are unaffected. The charge reference ' +
             'calibrates the MATRIX’s potential — it may not apply to the ' +
             'analyte, so reported positions carry additional, ' +
             'unquantified uncertainty. This does not correct for that ' +
             'uncertainty; it only stops assuming there isn’t any.',
     },
   },
   tips: {
     material: 'Conducting samples charge-correct differently from ' +
               'insulating ones, and the suggested peak shapes differ too. ' +
@@ -13424,40 +13435,41 @@ function _fpFmt(tpl, vars) {
 
 async function openFindPeaksModal() {
   if (!state.rawBE || !state.rawBE.length) {
     notify('Load a spectrum first — Find Peaks runs on the active tab.', 'amber');
     return;
   }
   try {
     if (!_fpMeta) {
       const r = await fetch('/api/analyze/meta');
       _fpMeta = await r.json();
     }
   } catch (e) {
     notify('Find Peaks backend unavailable: ' + e.message, 'amber');
     return;
   }
   // all wording from FP_STRINGS; server strings escaped even though
   // currently code-controlled (a future registered label must never
   // become an injection point)
   document.getElementById('fp-blurb').innerHTML = FP_STRINGS.blurb;
   document.getElementById('fp-apply-note').textContent = FP_STRINGS.applyNote;
+  _fpMaybeShowExperimentalNotice();
   document.getElementById('fp-material-label').title = FP_STRINGS.tips.material;
   document.getElementById('fp-method-label').title = FP_STRINGS.tips.method;
   document.getElementById('fp-regions-label').title = FP_STRINGS.tips.regions;
   const mat = document.getElementById('fp-material');
   mat.innerHTML = _fpMeta.material_classes
     .map(m => {
       const s = FP_STRINGS.materials[m] || {};
       const title = s.hint ? ` title="${_fpEsc(s.hint)}"` : '';
       return `<option value="${_fpEsc(m)}"${title}>${_fpEsc(s.label || m)}</option>`;
     }).join('');
   _fpMaterialChanged();
   document.getElementById('fp-regions-filter').value = '';
   _fpRegionsSelected = new Set();
   _fpExpandedElement = null;
   _fpRenderLegend();
   _fpRenderPtGrid('');
   _fpRenderSearchDropdown('');
   _fpRenderExpandedPanel();
   document.getElementById('fp-regions-tier-note').textContent = '';
   const meth = document.getElementById('fp-method');
@@ -13742,40 +13754,58 @@ function _fpSyncSelectionUI() {
   document.getElementById('fp-regions-tier-note').textContent =
     _fpTierNoteFor(entries);
   // ROI auto-fill: only for an UNAMBIGUOUS single-region pick with a real
   // hint — a co-fit selection (2 regions) has no single "right" window,
   // and a structure_only region honestly has no hint to offer (goal:
   // never invent a window; the note above says so, ROI is left alone).
   if (entries.length === 1 && entries[0].roi) {
     document.getElementById('roi-min').value = entries[0].roi.be_min;
     document.getElementById('roi-max').value = entries[0].roi.be_max;
   }
   _fpRenderPtGrid(document.getElementById('fp-regions-filter').value);
   _fpRenderExpandedPanel();
 }
 
 function _fpMaterialChanged() {
   const v = document.getElementById('fp-material').value;
   const s = FP_STRINGS.materials[v] || {};
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
   const strs = FP_STRINGS.methods[id] || {};
   document.getElementById('fp-method-hint').textContent = strs.hint || '';
   // the Advanced JSON stays the single source of truth for the request —
   // the friendly controls below are a labeled VIEW that writes into it
   document.getElementById('fp-options').value =
     JSON.stringify((m && m.default_options) || {}, null, 1);
   _fpBuildSimpleControls(id);
 }
 
 function _fpBuildSimpleControls(methodId) {
   const host = document.getElementById('fp-simple-options');
   const defs = FP_STRINGS.controls[methodId] || [];
   host.innerHTML = '';
   if (!defs.length) {
     const p = document.createElement('div');
     p.style.cssText = 'font-size:10px;color:var(--text3)';
     p.textContent = FP_STRINGS.controls._none;

2026-07-20T22:27:12.499697Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 88 column 5
codex
I also checked interference points: the banner is a sibling after the draggable `<h3>`, not inside it, and `_fpMaybeShowExperimentalNotice()` is placed after `#fp-blurb` assignment but before the material/method hint setup. It does not touch `#fp-material-hint`, `#fp-method-hint`, or the blurb element.
exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '10120,10145p;10874,10892p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
 10120	    tooltipBody: _cssVar('--text2'),
 10121	    // Raw spectrum data color adapts to theme
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
 10145	    });
 10874	const REF_PALETTE_LS = 'xps.refPalette.v1';   // namespaced + VERSIONED geometry key
 10875	let _refPaletteDrag = null;
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

exec
/bin/zsh -lc 'git diff --check 56b5d5a''^ 56b5d5a' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-4EjpTuNf' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-HlCzXOF4' (errno=Operation not permitted)

2026-07-20T22:27:22.418363Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 88 column 5
codex
1. MINOR [tests/js/fp_experimental_notice.test.js](/Users/skyefortier/xps-verify/tests/js/fp_experimental_notice.test.js:39): the “starting point / not final answer” test is too loose. It would still pass if the notice only said “review” and dropped “not a final answer,” so it does not fully discriminate that safety copy.

2. MINOR [tests/js/fp_experimental_notice.test.js](/Users/skyefortier/xps-verify/tests/js/fp_experimental_notice.test.js:44): the “does not imply frozen/broken” test only rejects `guarantee` and `accurate`. A bad notice saying “the app may look broken/frozen” would still pass.

3. MINOR [tests/js/fp_experimental_notice.test.js](/Users/skyefortier/xps-verify/tests/js/fp_experimental_notice.test.js:49): the DOM/localStorage test checks for function names plus `getItem`/`setItem`, but not same-key use, button wiring, hide/show behavior, or the early return. A broken implementation that reads one key, writes another, and never hides the banner could still pass.

No product-code blocker/major findings. The actual implementation traces correctly: first open sets notice text and `display: block`; dismiss writes `xps-fp-experimental-notice-dismissed` and hides; subsequent opens hit the `getItem` branch, hide, and return before text assignment/show. Runtime copy is pre-existing and supported by `app.py`’s `60-240s` docs plus `TOTAL_ANALYSIS_TIMEOUT_SEC = 240.0` in `autofit/engine.py`. Scope is correct: parent is `d13589d`, and the diff touches only `templates/index.html` plus the new JS test file.

VERDICT: GO
tokens used
40,560
1. MINOR [tests/js/fp_experimental_notice.test.js](/Users/skyefortier/xps-verify/tests/js/fp_experimental_notice.test.js:39): the “starting point / not final answer” test is too loose. It would still pass if the notice only said “review” and dropped “not a final answer,” so it does not fully discriminate that safety copy.

2. MINOR [tests/js/fp_experimental_notice.test.js](/Users/skyefortier/xps-verify/tests/js/fp_experimental_notice.test.js:44): the “does not imply frozen/broken” test only rejects `guarantee` and `accurate`. A bad notice saying “the app may look broken/frozen” would still pass.

3. MINOR [tests/js/fp_experimental_notice.test.js](/Users/skyefortier/xps-verify/tests/js/fp_experimental_notice.test.js:49): the DOM/localStorage test checks for function names plus `getItem`/`setItem`, but not same-key use, button wiring, hide/show behavior, or the early return. A broken implementation that reads one key, writes another, and never hides the banner could still pass.

No product-code blocker/major findings. The actual implementation traces correctly: first open sets notice text and `display: block`; dismiss writes `xps-fp-experimental-notice-dismissed` and hides; subsequent opens hit the `getItem` branch, hide, and return before text assignment/show. Runtime copy is pre-existing and supported by `app.py`’s `60-240s` docs plus `TOTAL_ANALYSIS_TIMEOUT_SEC = 240.0` in `autofit/engine.py`. Scope is correct: parent is `d13589d`, and the diff touches only `templates/index.html` plus the new JS test file.

VERDICT: GO
