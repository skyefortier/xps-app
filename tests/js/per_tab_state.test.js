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
  state: 'B',                 // the ACTIVE tab's working copy, swapped wholesale by activateTab
  _undoDebounceTimer: 'A', _tabRuntimeTokens: 'B', _tabRuntimeSeq: 'B',
  _nextStackNum: 'B', _accSurveyCache: 'B', _accChemCache: 'B', _refUnavailableNotified: 'B',
  tabManager: 'B',
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
  _undoDebounce: 'A',         // { owner, snap } bound at burst start; flushed onto its owner only
  // Populated constant catalogues (read-only tables) and the chart plugin
  // object: class B. Listed, not skipped, so a per-tab store hidden in an
  // ALL_CAPS name or in a plugin property would need an explicit entry here.
  STACK_PALETTE: 'B', LEGACY_REFERENCE: 'B', LEGACY_REFERENCE_OK: 'B', ELEMENT_NAMES: 'B',
  ELEMENT_MARKER_COLORS: 'B', PEAK_COLORS: 'B', SCOFIELD_RSF: 'B', SPIN_ORBIT_PRESETS: 'B',
  TAB_COLORS: 'B', SHAPE_PARAM_SCHEMA: 'B', PLACE_MODE_BUTTONS: 'B', LOCK_ALL_KEYS: 'B',
  _BG_SUB_DEPENDENT_CONTROL_IDS: 'B', xpsRefLinesPlugin: 'B',
  FP_TIER_META: 'B', FP_STRINGS: 'B', FP_MODEL_LABELS: 'B', FP_ROLE_LABELS: 'B', FP_SHAPE_LABELS: 'B', FP_TIER_RANK: 'B',
};

const { scanModuleMutables } = require('./lib/module_state_scan');
function moduleLevelMutables() {
  // scan only the page's inline scripts (not the HTML)
  const scripts = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
  assert.ok(scripts.length >= 1, 'no inline scripts found');
  return [...new Set(scripts.flatMap(scanModuleMutables))];
}

test('every module-level mutable is allowlisted with a non-C class', () => {
  const names = moduleLevelMutables();
  assert.ok(names.length > 20, 'scan found too few declarations: ' + names.length);
  const unknown = names.filter(n => !(n in ALLOWLIST));
  assert.deepStrictEqual(unknown, [], 'module-level state not allowlisted (put per-tab content on the tab record): ' + unknown.join(', '));
  for (const [n, cls] of Object.entries(ALLOWLIST)) assert.notStrictEqual(cls, 'C', n);
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
  // fits: owner is the record OBJECT, not an id
  assert.doesNotMatch(grab('async function runFit()', 1200), /fittingTabId = tabManager\.activeId/);
  assert.match(grab('function _autoFitRestore(', 300), /_autoFitRestore\(snap, owner\)/);
  // batch propagation re-validates the target after its yield
  const rp = grab('async function runPropagation', 5000);
  assert.ok(rp.indexOf('_activeTab() !== tgt') > rp.indexOf('setTimeout(r, 20)'), 'propagation must re-check the target after yielding');
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
