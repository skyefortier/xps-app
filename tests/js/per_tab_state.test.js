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
};

function moduleLevelMutables() {
  const re = /^(?:let|var) ([A-Za-z_$][A-Za-z0-9_$]*)\s*(?:=|;)|^const ([A-Za-z_$][A-Za-z0-9_$]*) = (?:\[\]|\{\}|new (?:Set|Map|WeakMap)\(|null)/gm;
  const names = [];
  let m;
  while ((m = re.exec(html)) !== null) {
    const name = m[1] || m[2];
    if (/^[A-Z][A-Z0-9_]+$/.test(name)) continue;          // ALL_CAPS constants are config, not state
    names.push(name);
  }
  return names;
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
