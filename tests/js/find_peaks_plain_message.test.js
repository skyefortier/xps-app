// Plain-English "Technical details" translation (2026-07-13, Find Peaks
// UI improvements round 3, unit 2 — the plain-English pass). Twin tests
// for the pure translation helpers in templates/index.html:
// _fpBoundaryHitLabel, _fpWidthFlagLabel, and _fpPlainMessage — which
// build a chemist-facing paragraph ENTIRELY from the same structured
// diagnostics.* / peaks[].region / structural_only fields the existing
// banners/tables already use. body.message itself (the raw engine
// string many backend tests assert on verbatim) is UNCHANGED and stays
// available one level deeper, under "Advanced (raw engine output)" —
// these tests never touch it.

const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(
  path.join(__dirname, '../../templates/index.html'), 'utf8');

function extract(re, name) {
  const m = html.match(re);
  assert.ok(m, name + ' not found in templates/index.html');
  return m[0];
}

const ctx = eval('(function(){\n'
  + extract(/const FP_STRINGS = \{[\s\S]*?\n\};/, 'FP_STRINGS') + '\n'
  + extract(/const FP_MODEL_LABELS = \{[\s\S]*?\n\};/, 'FP_MODEL_LABELS') + '\n'
  + extract(/const FP_ROLE_LABELS = \{[\s\S]*?\n\};/, 'FP_ROLE_LABELS') + '\n'
  + extract(/function _fpModelLabel\(raw\) \{[\s\S]*?\n\}/, '_fpModelLabel') + '\n'
  + extract(/function _fpRoleLabel\(role\) \{[\s\S]*?\n\}/, '_fpRoleLabel') + '\n'
  + extract(/function _fpParamLabel\(slug\) \{[\s\S]*?\n\}/, '_fpParamLabel') + '\n'
  + extract(/function _fpFilterReasonLabel\(reason\) \{[\s\S]*?\n\}/, '_fpFilterReasonLabel') + '\n'
  + extract(/function _fpBoundaryHitLabel\(hit\) \{[\s\S]*?\n\}/, '_fpBoundaryHitLabel') + '\n'
  + extract(/function _fpWidthFlagLabel\(flag\) \{[\s\S]*?\n\}/, '_fpWidthFlagLabel') + '\n'
  + extract(/function _fpPlainMessage\(body\) \{[\s\S]*?\n\}/, '_fpPlainMessage') + '\n'
  + 'return { _fpBoundaryHitLabel, _fpWidthFlagLabel, _fpPlainMessage };\n})()');
const { _fpBoundaryHitLabel, _fpWidthFlagLabel, _fpPlainMessage } = ctx;

// ── _fpBoundaryHitLabel ─────────────────────────────────────────────────

test('_fpBoundaryHitLabel: translates role:param@max with no raw identifiers', () => {
  const text = _fpBoundaryHitLabel('main_graphitic:fwhm@max');
  assert.match(text, /width/);
  assert.match(text, /upper limit/);
  assert.doesNotMatch(text, /@max/);
  assert.doesNotMatch(text, /s_main_graphitic/);
});

test('_fpBoundaryHitLabel: @min reads as lower limit', () => {
  const text = _fpBoundaryHitLabel('main_p32:center@min');
  assert.match(text, /lower limit/);
});

test('_fpBoundaryHitLabel: unparseable input degrades honestly, never throws', () => {
  const text = _fpBoundaryHitLabel('garbage');
  assert.match(text, /garbage/);
});

// ── _fpWidthFlagLabel ───────────────────────────────────────────────────

test('_fpWidthFlagLabel: detection-family "absorbing a neighbor" variant', () => {
  const text = _fpWidthFlagLabel(
    'detected_peak_2:fwhm=3.20eV≥0.70×ceiling (4.50eV) — ~1.75× its detected width; likely absorbing a neighbor');
  assert.match(text, /3\.20 eV/);
  assert.match(text, /absorbing/);
  assert.doesNotMatch(text, /×ceiling/);
  assert.doesNotMatch(text, /0\.70/);
});

test('_fpWidthFlagLabel: ordinary-cap "no known-broad justification" variant reads distinctly', () => {
  const text = _fpWidthFlagLabel(
    'main_graphitic:fwhm=2.00eV≥2.00eV ordinary cap (no known-broad justification)');
  assert.match(text, /2\.00 eV/);
  assert.match(text, /physical width limit/);
  assert.doesNotMatch(text, /absorbing/);   // distinct failure class, must not conflate
});

test('_fpWidthFlagLabel: DS+G and asym-GL variants still extract role + width cleanly', () => {
  const dsg = _fpWidthFlagLabel(
    'main_graphitic:effective fwhm=2.10eV≥2.00eV ordinary cap (DS+G β=0.30 + m=1.80; no known-broad justification)');
  assert.match(dsg, /2\.10 eV/);
  assert.doesNotMatch(dsg, /β=/);
});

// ── _fpPlainMessage ─────────────────────────────────────────────────────

function baseBody(overrides) {
  return Object.assign({
    success: true, peaks: [], diagnostics: { winner: 'A0_graphite_only', conditional: false },
  }, overrides);
}

test('_fpPlainMessage: structural_only stub (no cited or sourced data)', () => {
  const text = _fpPlainMessage({ structural_only: ['Fe 1s', 'Xe 4d'] });
  assert.match(text, /Fe 1s, Xe 4d/);
  assert.match(text, /no cited reference/i);
});

test('_fpPlainMessage: an EMPTY structural_only array must NOT trigger the stub (Codex-caught)', () => {
  // Regression: app.py's normal payload shape ALWAYS carries
  // structural_only as a (possibly empty) array — `[]` is truthy in
  // JS, so a bare `if (body.structural_only)` would show the "no
  // fittable peaks" stub for EVERY ordinary successful result. This is
  // the realistic shape of a normal, healthy payload.
  const text = _fpPlainMessage(baseBody({ structural_only: [] }));
  assert.doesNotMatch(text, /No fittable peaks were found/);
  assert.match(text, /passed every check cleanly/);
});

test('_fpPlainMessage: no survivors', () => {
  const text = _fpPlainMessage(baseBody({
    success: false, diagnostics: { n_candidates_evaluated: 4, n_candidates_total: 4 },
  }));
  assert.match(text, /None of the peak models/);
});

test('_fpPlainMessage: no survivors + truncated mentions the honest count', () => {
  const text = _fpPlainMessage(baseBody({
    success: false,
    diagnostics: { analysis_truncated: true, n_candidates_evaluated: 3, n_candidates_total: 9 },
  }));
  assert.match(text, /3 of 9/);
});

test('_fpPlainMessage: clean winner with nothing flagged reads as clean', () => {
  const text = _fpPlainMessage(baseBody({}));
  assert.match(text, /passed every check cleanly/);
  assert.doesNotMatch(text, /CONDITIONAL/);
});

test('_fpPlainMessage: data-driven (region-unassigned) components need review', () => {
  const text = _fpPlainMessage(baseBody({
    peaks: [{ region: 'unassigned', center: 279.14 }],
  }));
  assert.match(text, /279\.14/);
  assert.match(text, /review and assign/);
});

test('_fpPlainMessage: decisive_override reads CONDITIONAL and names the fixed parameter', () => {
  const text = _fpPlainMessage(baseBody({
    diagnostics: {
      winner: 'A0_graphite_only+bfix', conditional: true,
      conditional_reason: 'decisive_override',
      winner_boundary_fixed_params: ['s_main_graphitic_fwhm'],
    },
  }));
  assert.match(text, /^CONDITIONAL/);
  assert.match(text, /width/);
  assert.doesNotMatch(text, /decisive_override/);
  assert.doesNotMatch(text, /s_main_graphitic_fwhm/);
});

test('_fpPlainMessage: unstable_last_resort reads LOW CONFIDENCE, never hides the caveat', () => {
  const text = _fpPlainMessage(baseBody({
    diagnostics: {
      winner: 'A0_graphite_only', conditional: true,
      conditional_reason: 'unstable_last_resort',
    },
  }));
  assert.match(text, /^LOW CONFIDENCE/);
  assert.match(text, /rough suggestion/);
});

test('_fpPlainMessage: no_clean_survivor names the boundary hit in plain words', () => {
  const text = _fpPlainMessage(baseBody({
    diagnostics: {
      winner: 'A0_graphite_only', conditional: true,
      conditional_reason: 'no_clean_survivor',
      winner_boundary_hits: ['main_graphitic:fwhm@max'],
    },
  }));
  assert.match(text, /^CONDITIONAL/);
  assert.match(text, /upper limit/);
  assert.doesNotMatch(text, /no_clean_survivor/);
  assert.doesNotMatch(text, /@max/);
});

test('_fpPlainMessage: unphysical widths surface as LOW CONFIDENCE with no raw ceiling jargon', () => {
  const text = _fpPlainMessage(baseBody({
    diagnostics: {
      winner: 'A0_graphite_only', conditional: false,
      winner_unphysical_widths: [
        'detected_peak_2:fwhm=3.20eV≥0.70×ceiling (4.50eV) — ~1.75× its detected width; likely absorbing a neighbor'],
    },
  }));
  assert.match(text, /^LOW CONFIDENCE/);
  assert.doesNotMatch(text, /×ceiling/);
});

test('_fpPlainMessage: filtered dominant alternative is mentioned honestly', () => {
  const text = _fpPlainMessage(baseBody({
    diagnostics: {
      winner: 'A0_graphite_only', conditional: false,
      filtered_dominant_alternative: {
        name: 'M2_graphite_aliphatic', delta_bic_vs_winner: 12.3,
        filter_reason: 'plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)',
      },
    },
  }));
  assert.match(text, /scored better by 12\.3/);
  assert.doesNotMatch(text, /PlausibilityFlags/);
});

test('_fpPlainMessage: a CONDITIONAL result never reads as a clean pass', () => {
  const text = _fpPlainMessage(baseBody({
    diagnostics: {
      winner: 'A0_graphite_only', conditional: true,
      conditional_reason: 'no_clean_survivor',
      winner_boundary_hits: ['main_graphitic:fwhm@max'],
    },
  }));
  assert.doesNotMatch(text, /passed every check cleanly/);
});
