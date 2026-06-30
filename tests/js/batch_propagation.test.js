const { test } = require('node:test');
const assert = require('node:assert');
const BatchPropagation = require('../../static/js/batch_propagation.js');

// The UI shape carried on each tab (only the fields propagation touches plus a
// couple of unrelated ones to prove they pass through untouched).
function ui(over) {
  return Object.assign({
    bgType: 'shirley', bgStart: '700', bgEnd: '740', shirleyIter: '5',
    roiMin: '700', roiMax: '740',
    ccMethod: 'none', endpointAvg: '1',   // unrelated fields — must be preserved
  }, over);
}

// --- the bug fix: ROI now propagates from source to target ---
test('source ROI overwrites a different target ROI during propagation', () => {
  const src = ui({ roiMin: '525', roiMax: '545' });
  const tgt = ui({ roiMin: '100', roiMax: '160' });
  const out = BatchPropagation.propagateFitUi(src, tgt);
  assert.strictEqual(out.roiMin, '525');   // source ROI wins
  assert.strictEqual(out.roiMax, '545');
});

test('blank source ROI leaves the target ROI unchanged (never wipes it)', () => {
  const src = ui({ roiMin: '', roiMax: '' });
  const tgt = ui({ roiMin: '100', roiMax: '160' });
  const out = BatchPropagation.propagateFitUi(src, tgt);
  assert.strictEqual(out.roiMin, '100');   // target's own ROI kept
  assert.strictEqual(out.roiMax, '160');
});

test('a blank source ROI bound (one side) falls back per-field', () => {
  const src = ui({ roiMin: '530', roiMax: '' });
  const tgt = ui({ roiMin: '100', roiMax: '160' });
  const out = BatchPropagation.propagateFitUi(src, tgt);
  assert.strictEqual(out.roiMin, '530');   // present source min propagates
  assert.strictEqual(out.roiMax, '160');   // blank source max falls back to target
});

// --- no regression: background propagation behaves exactly as before ---
test('background fields still propagate from source (no regression)', () => {
  const src = ui({ bgType: 'tougaard', bgStart: '690', bgEnd: '750', shirleyIter: '9' });
  const tgt = ui({ bgType: 'shirley', bgStart: '700', bgEnd: '740', shirleyIter: '5' });
  const out = BatchPropagation.propagateFitUi(src, tgt);
  assert.strictEqual(out.bgType, 'tougaard');
  assert.strictEqual(out.bgStart, '690');
  assert.strictEqual(out.bgEnd, '750');
  assert.strictEqual(out.shirleyIter, '9');
});

test('blank source bgStart/bgEnd fall back to target (unchanged guard semantics)', () => {
  const src = ui({ bgStart: '', bgEnd: '' });
  const tgt = ui({ bgStart: '700', bgEnd: '740' });
  const out = BatchPropagation.propagateFitUi(src, tgt);
  assert.strictEqual(out.bgStart, '700');
  assert.strictEqual(out.bgEnd, '740');
});

// --- unrelated target UI is preserved; only the propagated set changes ---
test('unrelated target UI fields are preserved untouched', () => {
  const src = ui({ ccMethod: 'graphite-2845', endpointAvg: '3', roiMin: '525', roiMax: '545' });
  const tgt = ui({ ccMethod: 'advcarbon-2848', endpointAvg: '2' });
  const out = BatchPropagation.propagateFitUi(src, tgt);
  // these are NOT in the propagated set — they keep the TARGET's values
  assert.strictEqual(out.ccMethod, 'advcarbon-2848');
  assert.strictEqual(out.endpointAvg, '2');
  // exactly the propagated set differs from the target
  const propagated = ['bgType', 'bgStart', 'bgEnd', 'shirleyIter', 'roiMin', 'roiMax'];
  const changed = Object.keys(out).filter(k => out[k] !== tgt[k]);
  assert.deepStrictEqual(changed.sort(), ['roiMax', 'roiMin'].sort());   // only ROI differs here
  assert.ok(propagated.every(k => k in out));
});
