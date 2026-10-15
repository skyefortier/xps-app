// Per-tab state ownership (docs/superpowers/plans/2026-09-08-per-tab-state-ownership.md).
//
// The construction rule: content that belongs to ONE spectrum tab lives on
// that tab's record, never at module scope, so "restore into whichever tab
// is active" has no path. This structural test is the class-killer: every
// module-level mutable declaration in templates/index.html must be
// allowlisted with its class (A UI-transient, B tab-independent cache /
// catalogue, B' chart-instance state reset on activation). Class C — per-tab
// content — is NOT allowed at module scope; the three instances found
// (auto-fit snapshot, undo/redo stacks, the Find Peaks result) are gone or
// on the record. A new global that is not listed fails this test.
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');

// name -> class. Keep this list honest: adding a name here is a design
// decision, and "C" is not a valid value.
const ALLOWLIST = {
  state: 'B',                 // OWNERSHIP INFRASTRUCTURE, not a cache: the ACTIVE tab's working copy, swapped wholesale by activateTab / _syncActiveToRecord
  _undoDebounceTimer: 'A', _tabRuntimeTokens: 'B', _tabRuntimeSeq: 'B',
  _nextStackNum: 'B', _accSurveyCache: 'B', _accChemCache: 'B', _refUnavailableNotified: 'B',
  tabManager: 'B',            // OWNERSHIP INFRASTRUCTURE: the record store itself
  _origYMax: "B'", _origXMin: "B'", _origXMax: "B'", _origResidYMin: "B'", _origResidYMax: "B'",
  _dragZoomEnabled: 'A', placeMode: 'A', _pendingMultipletPreset: 'A', _bgSubFitInFlight: 'A',
  _autoFitConfirmResolver: 'A', _saveMode: 'A',
  _refCompoundMarkers: 'B', _refCompoundMarkerNextId: 'B',
  _refPanelOpen: 'A', _refPayload: 'B', _refError: 'B', _refFetchPromise: 'B', _refHoverId: 'A',
  _refGlobalSel: 'B', _refNotesOpen: 'A', _refSearchElements: 'B',
  _refPaletteDrag: 'A', _refChipOpenSym: 'A', _refChipOpenBtn: 'A',
  _snapshotSuppressed: 'A', _historyPreview: "B'",
  _ssFocusIdx: 'A', _ssFiltered: 'A',
  _fpMeta: 'B', _fpModalDrag: 'A', _fpRegionsSelected: 'A', _fpExpandedElement: 'A',
  _findPeaksApplyConfirmResolver: 'A',
  _autoFitBusy: 'A',   // Q8: the Auto-Fit transaction in progress (its operation and its Cancel) — no spectrum content
  _runningFitJobs: 'A', _fitOpByOwner: 'A', _fitOpSeq: 'A', _fitSpinnerOp: 'A',   // unit 2: in-flight job ids (pagehide beacon; the current job of each tab record, WeakMap keyed by the record) — no spectrum content       // unit 2: ids of in-flight server fit jobs, for the pagehide cancel beacon — no spectrum content
  _undoDebounce: 'A',         // burst buffer: DOES hold a peaks snapshot, but bound to its owner record at burst start and flushed onto that record only — the async-ownership exception to class A's 'no spectrum content'
  // Populated constant catalogues (read-only tables) and the chart plugin
  // object: class B. Listed, not skipped, so a per-tab store hidden in an
  // ALL_CAPS name or in a plugin property would need an explicit entry here.
  STACK_PALETTE: 'B', LEGACY_REFERENCE: 'B', LEGACY_REFERENCE_OK: 'B', ELEMENT_NAMES: 'B',
  ELEMENT_MARKER_COLORS: 'B', PEAK_COLORS: 'B', SCOFIELD_RSF: 'B', SPIN_ORBIT_PRESETS: 'B',
  TAB_COLORS: 'B', SHAPE_PARAM_SCHEMA: 'B', PLACE_MODE_BUTTONS: 'B', LOCK_ALL_KEYS: 'B',
  _BG_SUB_DEPENDENT_CONTROL_IDS: 'B', xpsRefLinesPlugin: 'B',
  _STARTS_MODEL_FIELDS: 'B', _STARTS_UI_FIELDS: 'B',   // constant tables: what the scattered-starts evidence is bound to
  _MODEL_EVIDENCE_FIELDS: 'B', _CC_REFERENCE: 'B',   // seal 1c step 2: constant tables (projection, model equality, charge references)
  _sealViews: 'B',   // seal 1c step 3: a WeakMap memo seal -> its view (derived, keyed by the immutable seal; no tab content)
  _SEAL_MODEL_FIELDS: 'B', _SEAL_CTX_FIELDS: 'B', _LOCAL_LINK_SYNC_KEYS: 'B',   // seal 1c step 4: constant tables (the live key; the local engine's link sync)
  _sealBindingMemo: 'B', _sealVerdicts: 'B', _sealUnreachable: 'B',   // seal 1c step 4: WeakMaps keyed by the immutable seal (derived answers; no tab content)
  _sealAttempts: 'A', _sealAttemptSeq: 'A',   // seal 1c step 4: verification attempts in flight, WeakMap keyed by the tab record (like _fitOpByOwner)
  _stagedTxns: 'A', _stagedTxnSeq: 'A',   // seal 1c step 4: Auto-Fit's staged verification transactions, WeakMap keyed by the tab record (like _sealAttempts)
  _serverNumerics: 'B', _NUMERICS_IDENTITY_KEYS: 'B', _numericsEpoch: 'B', _numericsAllowance: 'B', _numericsSplit: 'B', _checksInFlight: 'B',   // owner 2026-10-15: the server's declared numerics, epoch, allowance and split (page-wide, not per tab)
  _sealDetached: 'B',   // seal 1c step 5: WeakSet of snapshot records with a detached check in flight (keyed by the immutable seal)
  _sealSchemaMemo: 'B',
  _SEAL_MOVE_T: 'B', _SEAL_NOT_RUN_T: 'B', _SEAL_STARTS_T: 'B', _SEAL_REQUIRED_T: 'B', _SEAL_CERTIFICATE_T: 'B', _SEAL_SUPPORT_T: 'B', _SEAL_STATISTICS_T: 'B', _SEAL_SOFTWARE_T: 'B', _SEAL_BG_VERDICT_T: 'B', _SEAL_PAGE_T: 'B', _SEAL_LOCAL_CERT_T: 'B', _SEAL_BG_EFFECT_T: 'B', _SEAL_PEAK_NUM_FIELDS: 'B', _SEAL_EFFECT_FIELDS: 'B',   // seal 1c step 6: the typed-form specs (constant tables, fitting.py's)   // seal 1c step 6: WeakMap memo seal -> its schema verdict (derived, keyed by the immutable seal)
  _sealIds: 'B', _sealIdSeq: 'B',   // seal 1c step 5: a display identity per immutable seal (repaint signature; no tab content)
  BG_LABELS: 'B',            // constant table: background methods' display names (background math, 2026-10-01)
  FP_TIER_META: 'B', FP_STRINGS: 'B', FP_MODEL_LABELS: 'B', FP_ROLE_LABELS: 'B', FP_SHAPE_LABELS: 'B', FP_TIER_RANK: 'B',
  REF_PT_LAYOUT: 'B',        // periodic-table layout table (built by a call at load; read-only)
  _HEX_COLOR_RE: 'B', _SLUG_ID_RE: 'B',   // RegExp literals are objects (lastIndex is writable); these are validation constants
};

const { scanModuleMutables, inlineScripts } = require('./lib/module_state_scan');
function moduleLevelMutables() {
  // scan only the page's inline scripts (Jinja interpolations substituted)
  const scripts = inlineScripts(html);
  assert.ok(scripts.length >= 1, 'no inline scripts found');
  return [...new Set(scripts.flatMap(scanModuleMutables))];
}

const VALID_CLASSES = new Set(['A', 'B', "B'"]);
// Own-property lookup: an inherited name such as `constructor` or `toString`
// must NOT count as allowlisted (Codex round 4, both runs).
// '[anonymous class].…' names are rejected outright: an unbound class with
// static state has no binding to classify — give it one, or remove the state.
const isAllowlisted = (n) => !n.startsWith('[anonymous class]') && Object.hasOwn(ALLOWLIST, n) && VALID_CLASSES.has(ALLOWLIST[n]);

test('every module-level mutable is allowlisted with a valid non-C class', () => {
  const names = moduleLevelMutables();
  assert.ok(names.length > 20, 'scan found too few declarations: ' + names.length);
  const unknown = names.filter(n => !isAllowlisted(n));
  assert.deepStrictEqual(unknown, [], 'module-level state not allowlisted (put per-tab content on the tab record): ' + unknown.join(', '));
  for (const [n, cls] of Object.entries(ALLOWLIST)) assert.ok(VALID_CLASSES.has(cls), n + ' has an invalid class ' + cls);
});

test('inherited property names and anonymous-class names cannot slip through the allowlist', () => {
  for (const n of ['constructor', 'toString', '__proto__', 'hasOwnProperty', '[anonymous class].s', '[anonymous class].[static block]']) assert.ok(!isAllowlisted(n), n);
  // the prefix rule must hold even against an explicit own entry (Codex round 7)
  ALLOWLIST['[anonymous class].s'] = 'B';
  try { assert.ok(!isAllowlisted('[anonymous class].s'), 'an explicit allowlist entry must not rescue an anonymous class'); }
  finally { delete ALLOWLIST['[anonymous class].s']; }
  for (const sc of inlineScripts(html)) {
    const found = scanModuleMutables(sc + '\nlet constructor = [];');
    assert.ok(found.includes('constructor') && !isAllowlisted('constructor'));
  }
});

test('the known class-C holders are gone from module scope', () => {
  for (const bad of ['undoStack', 'redoStack', '_fpLast']) {
    assert.ok(!new RegExp('^(?:let|var|const) ' + bad + '\\b', 'm').test(html), bad + ' must live on the tab record');
  }
});

test('async operations capture their owning record before the first await', () => {
  const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
  // runFindPeaks: owner + inputs captured before uploadToBackend; result stored on the owner
  const rf = grab('async function runFindPeaks()', 6000);
  const ownerAt = rf.indexOf('_opOwner()'), uploadAt = rf.indexOf('await uploadToBackend');
  assert.ok(ownerAt > 0 && uploadAt > ownerAt, 'runFindPeaks must capture its owner before the upload await');
  assert.ok(rf.indexOf('peakToBackendSpec') < uploadAt || rf.indexOf('peakToBackendSpec') < 0, 'peak specs must be captured before the await');
  assert.match(rf, /_fpSetLast\([^)]*,\s*owner\)/, 'result must be stored on the captured owner');
  // applyFindPeaks: owner captured, re-validated after the confirmation await
  const ap = grab('async function applyFindPeaks()', 2500);
  assert.match(ap, /const owner = _opOwner\(\)/);
  assert.ok(ap.indexOf('_ownerActive(owner)') > ap.indexOf('await _showFindPeaksApplyConfirmModal'), 'owner must be re-validated after the confirmation await');
  // fits: owner is the record OBJECT, not an id, and EVERY request input is read before the upload await
  for (const fn of ['async function runFit(', 'async function runAutoFitC1sGraphite()']) {
    const body = grab(fn, 12000);
    assert.doesNotMatch(body, /fittingTabId = tabManager\.activeId/);
    const up = body.indexOf('await uploadToBackend');
    assert.ok(up > 0, fn + ' upload await');
    // seal 1c step 2: every request input is read by _liveFitContext (the controls, the shift, the anchors) and
    // turned into the request by _buildFitRequest (the peak specs) — both called before the upload await
    // (seal 1c step 4: _liveFitContext is _contextOf(the active page), whose controls are _uiFromDom's)
    const ctxSrc = grab('function _liveFitContext(', 1200), buildSrc = grab('function _buildFitRequest(', 3000);
    const ofSrc = grab('function _contextOf(', 2000), domSrc = grab('function _uiFromDom(', 2000);
    assert.ok(ctxSrc.indexOf('_contextOf(') > 0, '_liveFitContext reads through _contextOf');
    assert.ok(ofSrc.indexOf('_uiFromDom()') > 0, '_contextOf reads the active controls through _uiFromDom');
    for (const input of ["'fit-method'", "'bg-endpoint-avg'", "'bg-type'", "'bg-start'", "'roi-min'"])
      assert.ok(domSrc.indexOf(input) > 0, '_uiFromDom reads ' + input);
    for (const input of ['_getManualAnchors()', 'state.ccShift'])
      assert.ok(ofSrc.indexOf(input) > 0, '_contextOf reads ' + input);
    assert.ok(buildSrc.indexOf('peakToBackendSpec') > 0, '_buildFitRequest builds the peak specs');
    if (fn.includes('AutoFit')) {
      // Auto-Fit reads its inputs in _autoFitRequest (Q8: the anchor fit and the final fit alike),
      // each call before that fit's upload await
      const req = grab('function _autoFitRequest(', 3000);
      for (const input of ['_liveFitContext()', '_buildFitRequest('])
        assert.ok(req.indexOf(input) > 0, '_autoFitRequest: ' + input);
      const r1 = body.indexOf('const req1 = _autoFitRequest(anchorId);'), r2 = body.indexOf('const req2 = _autoFitRequest(anchorId);');
      assert.ok(r1 > 0 && r1 < up, 'the anchor fit\'s inputs before its upload');
      assert.ok(r2 > 0 && r2 < body.indexOf('await uploadToBackend(req2.be, req2.inten'), 'the final fit\'s inputs before its upload');
      continue;
    }
    for (const input of ['_liveFitContext()', '_buildFitRequest(']) {
      const at = body.indexOf(input);
      assert.ok(at > 0 && at < up, fn + ': ' + input + ' must be read before the upload await');
    }
  }
  // auto-fit: the owner is captured BEFORE its confirmation await and re-validated after it
  const af = grab('async function runAutoFitC1sGraphite()', 3000);
  const afOwnerAt = af.indexOf('_opOwner()'), afConfirmAt = af.indexOf('await _showAutoFitConfirmModal');
  assert.ok(afOwnerAt > 0 && afConfirmAt > afOwnerAt, 'auto-fit owner must be captured before the confirmation await');
  assert.ok(af.indexOf('_ownerActive(fittingTab)') > afConfirmAt, 'auto-fit must re-validate its owner after the confirmation');
  // generic-JSON route carries the same guard as the explicit .fit.json route
  const ls = grab('async function _loadSessionFile(', 3500);
  assert.strictEqual((ls.match(/_ownerActive\(owner\)/g) || []).length, 2, 'both fit-file routes must check the owner');
  // batch: targets resolved to objects before the first await
  const rp2 = grab('async function runPropagation', 6000);
  assert.ok(rp2.indexOf('const targets = ') > 0 && rp2.indexOf('const targets = ') < rp2.indexOf('await '), 'targets must be resolved before the first await');
  // modal open renders the active tab's stored result
  assert.match(grab('async function openFindPeaksModal()', 4000), /_fpGetLast\(\)/);
  // immediate history actions flush a pending burst first
  for (const fn of ['function pushUndo(', 'function undo()', 'function redo()']) assert.match(grab(fn, 400), /_flushUndoDebounce\(\)/, fn);
  assert.match(grab('function _autoFitRestore(', 300), /_autoFitRestore\(snap, owner\)/);
  // batch propagation re-validates the target after its yield
  // the WHOLE function (a fixed 5000-character window silently stopped
  // reaching the re-check when the function grew — fix-roi-clamp round 2)
  const rpAt = html.indexOf('async function runPropagation');
  const rp = html.slice(rpAt, html.indexOf('\n}\n', rpAt));
  const yieldAt = rp.indexOf('setTimeout(r, 20)'), recheckAt = rp.indexOf('_activeTab() !== tgt');
  assert.ok(yieldAt > 0 && recheckAt > yieldAt, 'propagation must re-check the target after yielding');
  // debounce binds owner + snapshot at schedule time
  assert.match(grab('function _pushUndoDebounced()', 900), /_historyTab\(\)/);
});

test('undo/redo and Find Peaks apply read the ACTIVE tab record only', () => {
  const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
  // _historyTab() is the spectrum-tab-with-containers view of _activeTab()
  assert.match(grab('function undo()', 900), /_historyTab\(\)/);
  assert.match(grab('function redo()', 900), /_historyTab\(\)/);
  assert.match(grab('function pushUndo(', 700), /_historyTab\(\)/);
  assert.match(grab('function _historyTab()', 400), /_activeTab\(\)/);
  assert.match(grab('async function applyFindPeaks()', 600), /_fpGetLast\(\)/);
  assert.doesNotMatch(grab('function _peaksSnapshot(', 800), /_runtimeTokenOf/, 'the runtime-token guard is redundant once stacks are per-tab');
});
