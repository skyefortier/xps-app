// Endpoint-averaging default = 3 for NEW tabs; legacy files keep 1.
// Decision + measurements: docs/superpowers/plans/2026-09-03-endpoint-averaging-default.md
// (owner: smallest averaging that captures most of the one-point-edge
// benefit; anchor bias grows linearly with cap and is harder to detect
// than noise). "New fits only": every path that restores a SAVED ui that
// lacks endpointAvg must resolve to '1', because those fits were made at 1
// and stack Path B / re-render reconstruct the background from that value.
//
// Structural pins (the browser test covers the live behaviour):
//   * one named constant NEW_TAB_ENDPOINT_AVG = '3', used by createTab, and
//     the #bg-endpoint-avg input's initial value equals it;
//   * one named constant LEGACY_ENDPOINT_AVG = '1', used by every saved-ui
//     fallback (_restoreUI, stack Path B, _loadSpectrumFile, fromJSON);
//   * no bare "|| '1'" fallback for endpointAvg remains outside the constant.
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');

function constant(name) {
  const m = html.match(new RegExp('const ' + name + " = '([0-9]+)';"));
  assert.ok(m, name + ' must be defined exactly once as a quoted integer string');
  assert.strictEqual((html.match(new RegExp('const ' + name + ' =', 'g')) || []).length, 1);
  return m[1];
}

test('new tabs default to endpoint averaging 3, via one constant', () => {
  assert.strictEqual(constant('NEW_TAB_ENDPOINT_AVG'), '3');
  const input = html.match(/<input type="number" id="bg-endpoint-avg" value="(\d+)"/);
  assert.ok(input, '#bg-endpoint-avg input not found');
  assert.strictEqual(input[1], '3', 'the fresh-page input must match the new-tab default');
  assert.match(html, /endpointAvg: NEW_TAB_ENDPOINT_AVG,/, 'createTab must use the constant');
});

test('legacy fallbacks resolve a saved ui without endpointAvg to 1', () => {
  assert.strictEqual(constant('LEGACY_ENDPOINT_AVG'), '1');
  assert.match(html, /set\('bg-endpoint-avg', ui\.endpointAvg \|\| LEGACY_ENDPOINT_AVG\)/, '_restoreUI');
  assert.match(html, /endpointAvg: \(srcUi && srcUi\.endpointAvg\) \|\| LEGACY_ENDPOINT_AVG,/, 'stack Path B');
  const uses = (html.match(/LEGACY_ENDPOINT_AVG/g) || []).length;
  // definition + _restoreUI + Path B + _loadSpectrumFile + fromJSON (v1) at minimum
  assert.ok(uses >= 5, 'expected the legacy constant at every saved-ui boundary, saw ' + uses);
});

test("no bare endpointAvg || '1' fallback survives outside the constant", () => {
  const bare = html.match(/endpointAvg[^\n]*\|\| *'1'/g) || [];
  assert.deepStrictEqual(bare, [], 'bare fallbacks: ' + bare.join(' | '));
});

test('Find Peaks records the averaging its engine used and applies it on apply', () => {
  // runFindPeaks stores what the engine will use (advanced-option endpoint_avg
  // or 1) on _fpLast; applyFindPeaks writes it to the panel + tab record.
  assert.match(html, /_fpLast = \{[^}]*endpointAvg: engineEndpointAvg/, 'runFindPeaks must record engineEndpointAvg on _fpLast');
  const applyStart = html.indexOf('async function applyFindPeaks()');
  const applyBody = html.slice(applyStart, applyStart + 8000);
  assert.match(applyBody, /_fpLast\.endpointAvg/, 'applyFindPeaks must read _fpLast.endpointAvg');
  assert.match(applyBody, /getElementById\('bg-endpoint-avg'\)/, 'applyFindPeaks must set the panel');
});

test('undo/redo carry the averaging recorded by the Find Peaks apply action', () => {
  const undoStart = html.indexOf('function undo()');
  const redoStart = html.indexOf('function redo()');
  assert.ok(undoStart > 0 && redoStart > 0);
  const undoBody = html.slice(undoStart, undoStart + 900);
  const redoBody = html.slice(redoStart, redoStart + 900);
  assert.match(undoBody, /_endpointAvg/, 'undo must restore a snapshot-carried endpointAvg');
  assert.match(redoBody, /_endpointAvg/, 'redo must restore a snapshot-carried endpointAvg');
  const applyStart = html.indexOf('async function applyFindPeaks()');
  const applyBody = html.slice(applyStart, applyStart + 8000);
  assert.match(applyBody, /pushUndo\(\{ ?endpointAvg:/, 'the apply action must record the pre-apply averaging on its undo entry');
});

test('averaging snapshots are scoped to the LIVE originating tab object, not its persisted id', () => {
  const start = html.indexOf('function _peaksSnapshot(');
  const body = html.slice(start, start + 1500);
  assert.match(body, /_runtimeTokenOf\(/, 'snapshot must record a runtime token of the originating tab object');
  assert.doesNotMatch(body, /_tabId/, 'persisted tab ids are reused after project reload — must not be the key');
  const rs = html.indexOf('function _restoreSnapshotEndpointAvg(');
  assert.match(html.slice(rs, rs + 900), /_runtimeTokenOf\(/, 'restore must compare the runtime token of the active tab object');
});
