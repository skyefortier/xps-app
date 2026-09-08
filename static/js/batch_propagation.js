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

  // A saved ui that lacks endpointAvg was fitted before the field existed,
  // i.e. at 1 — the same LEGACY_ENDPOINT_AVG rule index.html applies at every
  // saved-ui boundary (kept literal here: this module is DOM-free and must not
  // depend on index.html globals).
  const LEGACY_ENDPOINT_AVG = '1';

  // Build the UI settings a batch-fit target inherits from the source spectrum.
  // Batch fit propagates the background (type / start / end / iterations /
  // endpoint averaging) AND the region of interest, so every target is fit
  // over the SAME ROI with the SAME background definition as the source.
  // Endpoint averaging is background-affecting (sealed-fit-record memo R3-B5);
  // since new tabs default to 3 and legacy files to 1, leaving the target's
  // own value in place made "propagate background" silently fit targets at a
  // different averaging than the source (Codex 2026-09-08, both runs).
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
      endpointAvg: (srcUi.endpointAvg !== undefined && srcUi.endpointAvg !== '')
        ? srcUi.endpointAvg : LEGACY_ENDPOINT_AVG,
      roiMin: keep(srcUi.roiMin, tgtUi.roiMin),
      roiMax: keep(srcUi.roiMax, tgtUi.roiMax),
    };
  }

  return { propagateFitUi };
});
