// Manual-fit lineshape-switch round-trip stability — JS twin of the shipped
// _applyShapeSwitch in templates/index.html.
//
// Pins the 2026-07-08 data-integrity fix: cycling a peak's Line-shape
// dropdown (e.g. DS+G → GL → DS+G) must PRESERVE the parameters that carry
// over (center, amplitude, and the effective WIDTH — mapped across the
// laM↔fwhm boundary, not reset), and default ONLY parameters the new shape
// genuinely introduces. A round-trip must return the peak's ACTIVE
// parameters to their originals, so the rendered curve is unchanged.
// Before the fix, _switchPeakShape deleted the old shape's params and
// re-seeded defaults, silently corrupting fitted values (observed:
// DS+G laM 3.11 → 0.40, laBeta 0.05 → 0.30 on a round-trip).

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

// ── Pure shape-switch logic (schema + width accessors + _applyShapeSwitch) ──
const switchCtx = eval('(function(){\n'
  + extract(/const SHAPE_PARAM_SCHEMA = \{[\s\S]*?\n\};/, 'SHAPE_PARAM_SCHEMA') + '\n'
  + extract(/function _widthField\(shape\) \{[^\n]*\}/, '_widthField') + '\n'
  + extract(/function _widthFixField\(shape\) \{[^\n]*\}/, '_widthFixField') + '\n'
  + extract(/function _applyShapeSwitch\(peak, newShape\) \{[\s\S]*?\n\}/, '_applyShapeSwitch') + '\n'
  + 'return { SHAPE_PARAM_SCHEMA, _widthField, _applyShapeSwitch };\n})()');
const { SHAPE_PARAM_SCHEMA, _widthField, _applyShapeSwitch } = switchCtx;

// ── Lineshape evaluators (gaussian … evalPeakArray) for the curve check ──
const evalCtx = eval('(function(){\n'
  + extract(/function gaussian\(x, center, fwhm\) \{[\s\S]*?\nfunction evalPeakArray\(beArr, p\) \{[\s\S]*?\n\}/,
            'lineshape block') + '\n'
  + 'return { evalPeak, evalPeakArray };\n})()');
const { evalPeakArray } = evalCtx;

const ALL_SHAPES = ['Gaussian', 'Lorentzian', 'Voigt', 'GL', 'asym-GL', 'DS', 'DSG_LA', 'LACX'];

// Parameters evalPeak/evalPeakArray actually read for each shape (its ACTIVE
// params). Round-trip stability means EXACTLY these must be unchanged.
const ACTIVE = {
  'Gaussian':   ['center', 'amplitude', 'fwhm'],
  'Lorentzian': ['center', 'amplitude', 'fwhm'],
  'Voigt':      ['center', 'amplitude', 'fwhm'],
  'GL':         ['center', 'amplitude', 'fwhm', 'glMix'],
  'asym-GL':    ['center', 'amplitude', 'fwhm', 'glMix', 'asymmetry'],
  'DS':         ['center', 'amplitude', 'fwhm', 'dsAlpha', 'dsGamma'],
  'DSG_LA':     ['center', 'amplitude', 'laAlpha', 'laBeta', 'laM'],
  'LACX':       ['center', 'amplitude', 'fwhm', 'caAlpha', 'caBeta', 'caM'],
};

// A fully-populated peak (like defaultPeak) with DISTINCTIVE, non-default
// values in every shape param, so any silent reset is detectable.
function makePeak(shape) {
  return {
    id: 1, name: 'P', color: '#000', center: 284.6, amplitude: 12345, fwhm: 1.73,
    shape,
    glMix: 42, asymmetry: 0.17,
    dsAlpha: 0.13, dsGamma: 0.021,
    laAlpha: 0.12, laBeta: 0.05, laM: 3.11,
    caAlpha: 1.4, caBeta: 0.8, caM: 37,
    linked: null, linkOffset: 10.9, linkRatio: 0.5, visible: true,
    fixCenter: false, fixFwhm: false, fixAmplitude: false,
    fixGlMix: false, fixAsymmetry: false, fixDsAlpha: false, fixDsGamma: false,
    fixLaAlpha: false, fixLaBeta: false, fixLaM: false,
    fixCaAlpha: false, fixCaBeta: false, fixCaM: true,
    isChargeReference: false,
  };
}

function activeSnapshot(peak) {
  const out = {};
  for (const k of ACTIVE[peak.shape]) out[k] = peak[k];
  return out;
}

function curve(peak) {
  const grid = [];
  for (let i = 0; i <= 120; i++) grid.push(280.0 + 0.1 * i);
  return Array.from(evalPeakArray(grid, peak)).map(v => peak.amplitude * v);
}

// ── 1. round-trip param stability across the full shape set ──
test('round-trip A -> B -> A restores every ACTIVE parameter (all shapes)', () => {
  for (const A of ALL_SHAPES) {
    for (const B of ALL_SHAPES) {
      if (B === A) continue;
      const peak = makePeak(A);
      const before = activeSnapshot(peak);
      _applyShapeSwitch(peak, B);
      assert.strictEqual(peak.shape, B, `${A}->${B} did not set shape`);
      _applyShapeSwitch(peak, A);
      assert.strictEqual(peak.shape, A, `${A}->${B}->${A} did not restore shape`);
      const after = activeSnapshot(peak);
      assert.deepStrictEqual(after, before,
        `${A} -> ${B} -> ${A} changed an active parameter`);
    }
  }
});

// ── 2. the reported case, param + LOCK + rendered-curve identity ──
test('DS+G -> GL -> DS+G leaves laAlpha/laBeta/laM and the curve unchanged', () => {
  const peak = makePeak('DSG_LA');
  peak.fixLaM = true;                       // a user width-lock must survive too
  const c0 = curve(peak);
  const laAlpha0 = peak.laAlpha, laBeta0 = peak.laBeta, laM0 = peak.laM;

  _applyShapeSwitch(peak, 'GL');
  // width carried across the laM->fwhm boundary (NOT reset to a default)
  assert.strictEqual(peak.fwhm, laM0, 'width not carried DS+G -> GL');
  assert.strictEqual(peak.fixFwhm, true, 'width lock not carried DS+G -> GL');

  _applyShapeSwitch(peak, 'DSG_LA');
  assert.strictEqual(peak.laAlpha, laAlpha0);
  assert.strictEqual(peak.laBeta, laBeta0, 'laBeta silently reset (the bug)');
  assert.strictEqual(peak.laM, laM0, 'laM silently reset (the bug)');
  assert.strictEqual(peak.fixLaM, true, 'width lock not restored');
  const c1 = curve(peak);
  assert.deepStrictEqual(c1, c0, 'rendered curve changed on a no-op round-trip');
});

// ── 3. width mapped across shapes, not reset to a default ──
test('switching carries the effective eV width, both directions of laM<->fwhm', () => {
  const dsg = makePeak('DSG_LA');           // width lives in laM = 3.11
  _applyShapeSwitch(dsg, 'Gaussian');
  assert.strictEqual(dsg.fwhm, 3.11, 'DS+G width (laM) not mapped into fwhm');

  const gl = makePeak('GL');                // width lives in fwhm = 1.73
  _applyShapeSwitch(gl, 'DSG_LA');
  assert.strictEqual(gl.laM, 1.73, 'fwhm width not mapped into DS+G laM');
});

// ── 4. only genuinely-new params are defaulted; carried ones preserved ──
test('a genuinely-new param is defaulted; a carried-over one is preserved', () => {
  // Gaussian -> asym-GL: asymmetry is genuinely introduced. Start from a peak
  // that LACKS it, so it must be seeded from the schema default.
  const p = makePeak('Gaussian');
  delete p.asymmetry;
  _applyShapeSwitch(p, 'asym-GL');
  assert.strictEqual(p.asymmetry, SHAPE_PARAM_SCHEMA['asym-GL'].asymmetry,
    'genuinely-new param not seeded from the schema default');
  // glMix WAS already carried (42) — must NOT be reset to the schema default (30)
  assert.strictEqual(p.glMix, 42, 'carried-over glMix was reset to a default');
});

// ── 5b. fit-table export is shape-gated (Codex run A MAJOR) ──
// The never-delete switcher means a peak carries every shape's params; the
// export must read ONLY the ACTIVE shape's, not the first non-null via a
// fallback chain (which would export a stale inactive param).
const _shapeExportCols = eval('(function(){\n'
  + extract(/function _shapeExportCols\(p\) \{[\s\S]*?\n\}/, '_shapeExportCols') + '\n'
  + 'return _shapeExportCols;\n})()');

test('export columns read the ACTIVE shape, never a stale accumulated param', () => {
  // an LACX peak that still carries stale DS + DS+G fields (as after
  // DS -> DSG_LA -> LACX, or simply from defaultPeak)
  const p = { ...makePeak('LACX'), dsAlpha: 0.22, laBeta: 0.55, laM: 0.66,
              caAlpha: 1.70, caBeta: 0.80, caM: 37 };
  const c = _shapeExportCols(p);
  assert.strictEqual(c.alpha, 1.70, 'export Alpha picked a stale DS/DS+G value');
  assert.strictEqual(c.beta, 0.80, 'export Beta picked a stale DS+G value');
  assert.strictEqual(c.m, 37, 'export M_Gauss picked a stale DS+G value');
  assert.strictEqual(c.gl, '', 'LACX has no GL ratio');
  // DS+G reads la*, not the stale ca*
  const d = _shapeExportCols({ ...makePeak('DSG_LA'), caAlpha: 9, caBeta: 9, caM: 9 });
  assert.strictEqual(d.alpha, makePeak('DSG_LA').laAlpha);
  assert.strictEqual(d.m, makePeak('DSG_LA').laM);
  // a symmetric shape exports no shape params, even with stale fields present
  const g = _shapeExportCols({ ...makePeak('Gaussian'), glMix: 99, dsAlpha: 9 });
  assert.deepStrictEqual(g, { gl: '', alpha: '', beta: '', m: '' });
});

// ── 5. round-trip via three shapes still restores the origin ──
test('multi-hop round-trip DS+G -> LACX -> GL -> DS+G restores active params', () => {
  const peak = makePeak('DSG_LA');
  const before = activeSnapshot(peak);
  const c0 = curve(peak);
  _applyShapeSwitch(peak, 'LACX');
  _applyShapeSwitch(peak, 'GL');
  _applyShapeSwitch(peak, 'DSG_LA');
  assert.deepStrictEqual(activeSnapshot(peak), before);
  assert.deepStrictEqual(curve(peak), c0);
});
