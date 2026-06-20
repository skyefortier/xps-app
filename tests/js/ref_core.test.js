const { test } = require('node:test');
const assert = require('node:assert');
const RefCore = require('../../static/js/ref_identify_core.js');

test('tolFromSlider clamps to [0.25, 5.0] and snaps to 0.25', () => {
  assert.strictEqual(RefCore.tolFromSlider(1), 1);
  assert.strictEqual(RefCore.tolFromSlider(0.1), 0.25);
  assert.strictEqual(RefCore.tolFromSlider(9), 5);
  assert.strictEqual(RefCore.tolFromSlider(1.1), 1);
  assert.strictEqual(RefCore.tolFromSlider(1.13), 1.25);
  assert.strictEqual(RefCore.tolFromSlider('2.5'), 2.5);
  assert.strictEqual(RefCore.tolFromSlider(NaN), 1);
});

test('coerceTolToEv maps legacy modes onto the base, passes numbers through', () => {
  assert.strictEqual(RefCore.coerceTolToEv('narrow', 1.0), 0.5);
  assert.strictEqual(RefCore.coerceTolToEv('normal', 1.0), 1.0);
  assert.strictEqual(RefCore.coerceTolToEv('broad', 1.0), 2.0);
  assert.strictEqual(RefCore.coerceTolToEv(0.75, 1.0), 0.75);
  assert.strictEqual(RefCore.coerceTolToEv('garbage', 1.3), RefCore.tolFromSlider(1.3));
  assert.strictEqual(RefCore.coerceTolToEv(undefined, 1.3), RefCore.tolFromSlider(1.3));
});
