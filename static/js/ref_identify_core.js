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

  // Data-tier color SSOT — the single source for tier hue across every surface
  // (element-group + identify-candidate badges now; legend dot / chip dropdown /
  // identify popover in later tasks). curated=green, machine=violet, legacy=amber;
  // fallback=label ink for any unknown tier. Hexes mirror the --green/--purple/
  // --amber design tokens in index.html.
  const TIER_COLORS = { curated: '#3ddc84', machine: '#b48eff', legacy: '#ffbb44', fallback: '#8a9ab8' };
  function tierColor(tier) { return TIER_COLORS[tier] || TIER_COLORS.fallback; }

  // Data-tier note SSOT — the single canonical wording for each tier, rendered by
  // every reviewed/machine/legacy surface (tier toast, reviewed-card line). Change
  // the wording here and it updates everywhere. Unknown tier → the curated note
  // (mirrors the reviewed-card default).
  const TIER_NOTES = {
    machine: 'From NIST, automatically cross-checked but not yet reviewed by a person.',
    legacy: 'Approximate value — verify against literature.',
    curated: 'Reference energies reviewed against source records. Please still verify all energies against authoritative reference sources.',
  };
  function tierNote(tier) {
    return tier === 'machine' ? TIER_NOTES.machine
         : tier === 'legacy' ? TIER_NOTES.legacy
         : TIER_NOTES.curated;
  }

  // Shared color-assignment helper (A3) — the single source for picking an
  // overlay colorIdx, used for BOTH in-session picks and (later) post-load
  // next-pick. Returns the first index whose PALETTE RESIDUE (i % paletteLen) is
  // not already used by the current overlays, so a new overlay renders a colour
  // distinct from existing ones while unused residues remain; once every residue
  // is taken it falls back deterministically to max(used)+1 (accepts reuse).
  // Invalid entries (non-integer / negative) are ignored when computing the set.
  function nextColorIdx(usedColorIndices, paletteLen) {
    const used = Array.isArray(usedColorIndices)
      ? usedColorIndices.filter(c => Number.isInteger(c) && c >= 0) : [];
    const len = (Number.isInteger(paletteLen) && paletteLen > 0) ? paletteLen : 1;
    const usedResidues = new Set(used.map(c => c % len));
    for (let i = 0; i < len; i++) if (!usedResidues.has(i)) return i;
    return used.length ? Math.max.apply(null, used) + 1 : 0;
  }

  // Pure viewport clamp (A5) for the floating palette: keep the box on-screen
  // (with `margin`), and always leave at least an 80px header band reachable
  // vertically so a stale/offscreen saved position can never strand the palette.
  // Non-finite left/top fall back to the margin (treated as "unset").
  function clampToViewport(left, top, w, h, vw, vh, margin) {
    const m = Number.isFinite(margin) ? margin : 8;
    const maxLeft = Math.max(m, vw - w - m);
    const maxTop = Math.max(m, vh - Math.min(h, 80) - m);
    const L = Number.isFinite(left) ? left : m;
    const T = Number.isFinite(top) ? top : m;
    return { left: Math.min(Math.max(m, L), maxLeft), top: Math.min(Math.max(m, T), maxTop) };
  }

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

  // Normalize a mixed-granularity chemical-state key (revision #4). Exact
  // spin-orbit keys map to themselves; subshell-only p/d/f keys attach to BOTH
  // spin-orbit partners; s subshells have no split.
  const SO_SPLIT = { p: ['3/2', '1/2'], d: ['5/2', '3/2'], f: ['7/2', '5/2'] };
  function parseChemKey(key) {
    const str = String(key == null ? '' : key).trim();
    const m = str.match(/^([A-Z][a-z]?)\s+(\d)([spdf])(?:(\d)\/(\d))?$/);
    if (!m) {
      const parts = str.split(/\s+/);
      return { sym: parts[0] || str, orbital: parts.slice(1).join(' '), targets: [] };
    }
    const sym = m[1], n = m[2], l = m[3];
    if (m[4] && m[5]) { const orb = n + l + m[4] + '/' + m[5]; return { sym, orbital: orb, targets: [orb] }; }
    if (l === 's') { const orb = n + 's'; return { sym, orbital: orb, targets: [orb] }; }
    const orb = n + l;
    return { sym, orbital: orb, targets: SO_SPLIT[l].map(j => orb + j) };
  }

  // Physics projections (revision #6). Pure; mirror vgd_parser's convention.
  function augerApparentBE(ke, photonEv, workFn) { return photonEv - ke - workFn; }
  function photoelectronBE(nominalBE) { return nominalBE; }   // source-invariant

  // Marker-lifetime predicates (revision #5).
  // Element overlays PERSIST independent of the palette: visibility depends only
  // on being the active, non-stack chart with a selection. `panelOpen` is still
  // accepted (callers pass it) but no longer gates — overlays stay drawn after
  // the palette closes. (Stack-tab + active-chart guards remain authoritative.)
  function elementOverlayVisible(s) { return !!(s && s.activeChart && !s.isStackTab); }
  function compoundMarkerVisible() { return true; }            // global/persistent

  // ALL chem states within tol become candidates — no evidence filter exists at
  // runtime (revision #2). Proximity is honest; tier capping is applied later.
  function compoundCandidatesFrom(chemGroups, clickedBE, tolEv) {
    const out = [];
    const tol = tolFromSlider(tolEv);
    for (const g of chemGroups || []) {
      const pk = parseChemKey(g.orbital_key);
      const sym = pk.sym || g.element;
      for (const s of g.states || []) {
        const dist = Math.abs(s.be_ev - clickedBE);
        if (dist > tol) continue;
        const score = 20 + 30 * Math.max(0, 1 - dist / Math.max(tol, 0.01));
        out.push({
          id: s.id || (g.orbital_key + ':' + s.state),
          sym: sym, orbital: pk.orbital, orbitalTargets: pk.targets,
          label: sym + ' ' + pk.orbital + ' — ' + s.state,
          isAuger: false, ke: null, be: s.be_ev, dist: dist,
          inRegion: false, hasRegion: false, vis: 'n/a',
          score: score, dataTier: 'legacy', isCompound: true,
          stateName: s.state, ref: s.ref || '',
          // Proximity-only: 'strong' energy match requires an expected-region
          // hit, which chemical-state records structurally lack, so a compound
          // tops out at 'moderate' (mirrors production's element rule).
          energyMatch: 'moderate',
          partnerTxt: 'n/a — chemical-state record',
          othersTxt: 'n/a — chemical-state record',
          conflictTxt: null,
          sourceId: s.source || 'legacy-embedded-dataset',
        });
      }
    }
    return out;
  }

  // Tier modulates ALL THREE confidence surfaces for legacy (revision #3):
  // overall noun -> "Legacy hint"; energy proximity stays honest but annotated.
  function capConfidenceByTier(score, energyMatch, dataTier) {
    if (dataTier === 'legacy') {
      return { label: 'Legacy hint', labelCls: 'legacy',
               energyText: energyMatch + ' (confidence capped by source tier)' };
    }
    const label = score >= 80 ? 'Strong candidate' : (score >= 50 ? 'Possible' : 'Weak candidate');
    const labelCls = score >= 80 ? 'strong' : (score >= 50 ? 'possible' : 'weak');
    return { label: label, labelCls: labelCls, energyText: energyMatch };
  }

  // PRESERVE production's comparator exactly (revision #1): |Δ| primary; ties
  // within 0.5 eV break by tier (curated<machine<legacy), then score, then PE>Auger.
  function mergeAndRankCandidates(elementCands, compoundCands, limit) {
    const TIER_RANK = { curated: 0, machine: 1, legacy: 2 };
    const all = (elementCands || []).concat(compoundCands || []);
    all.sort((a, b) => {
      const dd = a.dist - b.dist;
      if (Math.abs(dd) > 0.5) return dd;
      const tr = (TIER_RANK[a.dataTier] != null ? TIER_RANK[a.dataTier] : 9) -
                 (TIER_RANK[b.dataTier] != null ? TIER_RANK[b.dataTier] : 9);
      if (tr) return tr;
      return (b.score - a.score) || ((a.isAuger ? 1 : 0) - (b.isAuger ? 1 : 0));
    });
    return all.slice(0, limit || 8);
  }

  // ───────────────────────────────────────────────────────────────────────────
  // B1: pure, versioned (de)serialization for reference-overlay save/load.
  // PURE only — no DOM/state, no save/load wiring (B2 wires buildTabData /
  // _loadProjectJSON). Element overlays are PER-TAB; compound markers are GLOBAL
  // at project-meta. Each schema carries its OWN internal version (decoupled),
  // independent of the top-level project version (which stays 3). All four
  // functions are TOTAL: serializers return null on empty/nullish/malformed
  // input; deserializers never throw and fall back to empty.
  // ───────────────────────────────────────────────────────────────────────────
  const REF_OVERLAYS_VERSION = 1;
  const REF_COMPOUND_MARKERS_VERSION = 1;

  // Per-tab element-overlay selection → the persisted object, or null when there
  // is no valid selection (so B2 can call it on a tab whose lazy _refSel was
  // never created). colorIdx + tier saved per element. Never reads identify state
  // (tab._refIdentify / sel.tolEv) — identify is structurally un-serializable here.
  function serializeRefOverlays(sel) {
    if (!sel || typeof sel !== 'object' || !Array.isArray(sel.syms)) return null;
    const syms = [];
    for (const s of sel.syms) {
      if (!s || typeof s !== 'object' || typeof s.sym !== 'string' || !s.sym) continue;
      syms.push({ sym: s.sym, colorIdx: s.colorIdx, tier: s.tier });
    }
    if (!syms.length) return null;
    return {
      v: REF_OVERLAYS_VERSION,
      syms,
      source: sel.source === 'MgKa' ? 'MgKa' : 'AlKa',
      showWeak: !!sel.showWeak,
      includeAuger: !!sel.includeAuger,
    };
  }

  // Persisted overlay object → a partial sel { syms, source, showWeak,
  // includeAuger } to merge over _refDefaultSel(). Envelope-malformed (not an
  // object / v missing or non-numeric / v newer than ours / syms not an array)
  // → empty. Entry-invalid (no resolvable sym) is skipped; colorIdx/tier are
  // repaired, not cause-to-drop. A valid colorIdx (integer ≥ 0) is preserved
  // verbatim; a missing/invalid one is assigned by position via the shared
  // residue-aware nextColorIdx against the colorIdx already resolved for
  // earlier-kept entries. Duplicate sym → keep first. Unknown tier → kept.
  function deserializeRefOverlays(obj, paletteLen) {
    const empty = { syms: [], source: 'AlKa', showWeak: false, includeAuger: false };
    if (!obj || typeof obj !== 'object' || typeof obj.v !== 'number' ||
        obj.v > REF_OVERLAYS_VERSION || !Array.isArray(obj.syms)) {
      return empty;
    }
    const len = (Number.isInteger(paletteLen) && paletteLen > 0) ? paletteLen : 1;
    const syms = [];
    const seen = new Set();
    for (const e of obj.syms) {
      if (!e || typeof e !== 'object') continue;
      const sym = (typeof e.sym === 'string' && e.sym) ? e.sym : null;
      if (!sym || seen.has(sym)) continue;              // no sym → skip; duplicate → keep first
      seen.add(sym);
      const colorIdx = (Number.isInteger(e.colorIdx) && e.colorIdx >= 0)
        ? e.colorIdx                                     // valid → verbatim
        : nextColorIdx(syms.map(s => s.colorIdx), len); // invalid/missing → by-position repair
      syms.push({ sym, colorIdx, tier: e.tier });
    }
    return {
      syms,
      source: obj.source === 'MgKa' ? 'MgKa' : 'AlKa',
      showWeak: !!obj.showWeak,
      includeAuger: !!obj.includeAuger,
    };
  }

  // THE single compound-marker validity + normalization rule, shared by both
  // serialize and deserialize (don't write it twice). Validity: a finite `be`.
  // Repair: `state`/`ref` coerced to string; `sym` optional (absent tolerated).
  // Returns a clean marker, or null when the entry is a non-object or has a
  // non-finite `be`.
  function _normalizeCompoundMarker(m) {
    if (!m || typeof m !== 'object') return null;
    const be = Number(m.be);
    if (!Number.isFinite(be)) return null;
    const marker = {
      state: typeof m.state === 'string' ? m.state : '',
      be,
      ref: typeof m.ref === 'string' ? m.ref : '',
    };
    if (typeof m.sym === 'string' && m.sym) marker.sym = m.sym;   // sym optional
    return marker;
  }

  // Global compound markers → the persisted object, or null when the array is
  // nullish/non-array/empty OR no entry survives normalization. TOTAL: invalid
  // entries (non-object, non-finite be) are skipped, never thrown on.
  function serializeRefCompoundMarkers(markers) {
    if (!Array.isArray(markers)) return null;
    const out = [];
    for (const m of markers) {
      const marker = _normalizeCompoundMarker(m);
      if (marker) out.push(marker);
    }
    if (!out.length) return null;
    return { v: REF_COMPOUND_MARKERS_VERSION, markers: out };
  }

  // Persisted compound-marker object → the global marker list. Envelope-malformed
  // (not an object / v missing or non-numeric / v newer / markers not an array)
  // → empty. Per entry: the SAME _normalizeCompoundMarker rule — a non-finite be
  // drops it; sym is optional (absent tolerated); state/ref coerced to string.
  function deserializeRefCompoundMarkers(obj) {
    if (!obj || typeof obj !== 'object' || typeof obj.v !== 'number' ||
        obj.v > REF_COMPOUND_MARKERS_VERSION || !Array.isArray(obj.markers)) {
      return [];
    }
    const out = [];
    for (const m of obj.markers) {
      const marker = _normalizeCompoundMarker(m);
      if (marker) out.push(marker);
    }
    return out;
  }

  return { tolFromSlider, coerceTolToEv, blendedSearch, parseChemKey,
           augerApparentBE, photoelectronBE, elementOverlayVisible, compoundMarkerVisible,
           compoundCandidatesFrom, capConfidenceByTier, mergeAndRankCandidates,
           tierColor, TIER_COLORS, tierNote, TIER_NOTES, nextColorIdx, clampToViewport,
           REF_OVERLAYS_VERSION, REF_COMPOUND_MARKERS_VERSION,
           serializeRefOverlays, deserializeRefOverlays,
           serializeRefCompoundMarkers, deserializeRefCompoundMarkers };
});
