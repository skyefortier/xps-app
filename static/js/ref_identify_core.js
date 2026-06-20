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

  // Blended element + compound + energy search. Inputs are plain data so this
  // stays pure: elements = [{sym,name,z,tier}], chemGroups = the legacy
  // chemical_states groups [{orbital_key,element,z,orbital,states:[{state,be_ev,ref}]}].
  // Returns up to `limit` rows: { kind:'element'|'compound'|'energy', sym, label, ev, ... }.
  function blendedSearch(query, elements, chemGroups, opts) {
    const limit = (opts && opts.limit) || 8;
    const q = String(query == null ? '' : query).trim().toLowerCase();
    if (!q) return [];
    const isNum = /^\d/.test(q);
    const rows = [];
    for (const e of elements || []) {
      const name = String(e.name || '').toLowerCase();
      if (e.sym.toLowerCase().startsWith(q) || name.includes(q))
        rows.push({ kind: 'element', sym: e.sym, label: e.sym + ' — ' + (e.name || e.sym), ev: 'Z=' + e.z });
    }
    for (const g of chemGroups || []) {
      const parent = g.element || '';
      for (const s of g.states || []) {
        const hay = (s.state + ' ' + g.orbital_key + ' ' + (s.ref || '')).toLowerCase();
        if (hay.includes(q) || parent.toLowerCase() === q)
          rows.push({ kind: 'compound', sym: parent, key: g.orbital_key, id: s.id,
                      label: s.state + ' · ' + g.orbital_key, be: s.be_ev, ref: s.ref || '',
                      ev: s.be_ev.toFixed(1) + ' eV' });
      }
    }
    if (isNum) {
      for (const g of chemGroups || []) for (const s of g.states || []) {
        if (String(s.be_ev).startsWith(q))
          rows.push({ kind: 'energy', sym: g.element, key: g.orbital_key, id: s.id,
                      label: g.orbital_key + ' (' + s.state + ')', be: s.be_ev, ref: s.ref || '',
                      ev: s.be_ev.toFixed(1) + ' eV' });
      }
    }
    const order = { element: 0, compound: 1, energy: 2 };
    rows.sort((a, b) => order[a.kind] - order[b.kind]);
    return rows.slice(0, limit);
  }

  return { tolFromSlider, coerceTolToEv, blendedSearch };
});
