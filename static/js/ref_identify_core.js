/*
 * ref_identify_core.js — pure, DOM-free logic for the Reference / Identify
 * workspace. THE SHIPPED MODULE: index.html must not copy these functions.
 * UMD: require()-able in Node (tests) and a browser global (RefCore). No build
 * step, no dependencies. Keep pure — no document/window/state references.
 */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.RefCore = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const TOL_MIN = 0.25, TOL_MAX = 5.0, TOL_STEP = 0.25, TOL_DEFAULT = 1.0;

  function tolFromSlider(value) {
    let v = Number(value);
    if (!isFinite(v)) v = TOL_DEFAULT;
    v = Math.min(TOL_MAX, Math.max(TOL_MIN, v));
    v = Math.round(v / TOL_STEP) * TOL_STEP;
    return Math.round(v * 100) / 100;
  }

  function coerceTolToEv(stored, base) {
    const b = tolFromSlider(base);
    if (typeof stored === 'number' && isFinite(stored)) return tolFromSlider(stored);
    const mult = { narrow: 0.5, normal: 1, broad: 2 }[stored];
    return mult != null ? tolFromSlider(b * mult) : b;
  }

  return { tolFromSlider, coerceTolToEv };
});
