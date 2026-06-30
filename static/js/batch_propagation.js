/*
 * batch_propagation.js — pure, DOM-free logic for batch-fit settings
 * propagation. THE SHIPPED MODULE: index.html must not copy this function.
 * UMD: require()-able in Node (tests) and a browser global (BatchPropagation).
 * No build step, no dependencies. Keep pure — no document/window/state.
 */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.BatchPropagation = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // Build the UI settings a batch-fit target inherits from the source spectrum.
  // Batch fit propagates the background (type / start / end / iterations) AND the
  // region of interest, so every target is fit over the SAME ROI as the source.
  // Start/end/ROI use a defensive guard: a blank source value falls back to the
  // target's own value, so a blank source field never wipes the target's. All
  // other target UI fields are preserved unchanged.
  function propagateFitUi(srcUi, tgtUi) {
    const keep = (s, t) => (s !== '' ? s : t);
    return {
      ...tgtUi,
      bgType: srcUi.bgType,
      bgStart: keep(srcUi.bgStart, tgtUi.bgStart),
      bgEnd: keep(srcUi.bgEnd, tgtUi.bgEnd),
      shirleyIter: srcUi.shirleyIter,
      roiMin: keep(srcUi.roiMin, tgtUi.roiMin),
      roiMax: keep(srcUi.roiMax, tgtUi.roiMax),
    };
  }

  return { propagateFitUi };
});
