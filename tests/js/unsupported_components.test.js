// "Not supported by the data" (unit step (b), 2026-09-22). Owner decisions
// pinned here: a component the fit drove to its floor is an explicit outcome;
// its centre, width and sigma are not reported anywhere a result is shown,
// stored or exported; it is excluded from the Quantify body and listed beneath
// (0.0 % would be a measurement claim); a linked component follows its parent;
// a local-engine result or a propagated model establishes nothing.
//
// Functions are extracted verbatim from templates/index.html; the fixture is a
// REAL run_fit response (tests/js/fixtures/autofit_anchor.json) plus hand-built
// responses for the twin.

const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
const lines = html.split('\n');
function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name + '\\(');
  const start = lines.findIndex(l => re.test(l));
  assert.ok(start >= 0, `function ${name} not found`);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail('unbalanced ' + name);
}
const constLine = name => { const l = lines.find(x => x.startsWith('const ' + name)); assert.ok(l, name); return l; };
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');

const CORE = ['_componentSupportFromResponse', '_applySupport', '_isUnsupported', '_unsupportedBadge'];
function core() {
  const src = [constLine('_SUPPORT_MIN_F'), constLine('_UNSUPPORTED_LABEL'), constLine('_UNSUPPORTED_TIP'), ...CORE.map(extractFn)].join('\n');
  return new Function('_escAttr', src + '\nreturn { ' + CORE.join(', ') + ' };')(esc);
}

const FIX = JSON.parse(fs.readFileSync(path.join(__dirname, 'fixtures/autofit_anchor.json'), 'utf8'));
const collapsed = FIX.find(f => /collapsed model/.test(f.name));
const resolved = FIX.find(f => /ordinary C 1s/.test(f.name));

test('the twin reproduces the server verdict on real responses, and defers to the server field when present', () => {
  const c = core();
  assert.strictEqual(c._componentSupportFromResponse(collapsed.json, '1').supported, false);
  assert.strictEqual(c._componentSupportFromResponse(resolved.json, '1').supported, true);
  assert.ok(c._componentSupportFromResponse(resolved.json, '1').f > 1000);
  const withField = { individual_peaks: [{ id: '1', support: { f: 2.0, delta_chi2: 1, supported: false } }] };
  assert.deepStrictEqual(c._componentSupportFromResponse(withField, 1), { f: 2.0, delta_chi2: 1, supported: false });
  assert.strictEqual(c._componentSupportFromResponse({ individual_peaks: [] }, 1), null, 'nothing to judge: not established');
  assert.strictEqual(c._componentSupportFromResponse({ counts: [1, 2], fitted_y: [1], individual_peaks: [{ id: '1', y: [1, 2] }] }, 1), null);
});

test('_applySupport writes every peak, follows links, and leaves null where the response says nothing', () => {
  const c = core();
  const peaks = [{ id: 1, name: 'a' }, { id: 2, name: 'b', linked: 1, linkRatio: 0.5 }, { id: 9, name: 'not in the response' }];
  c._applySupport(peaks, { individual_peaks: [{ id: '1', support: { f: 0.5, delta_chi2: -3, supported: false } }] });
  assert.deepStrictEqual(peaks[0].support, { f: 0.5, delta_chi2: -3, supported: false });
  assert.deepStrictEqual(peaks[1].support, { f: 0.5, delta_chi2: -3, supported: false, follows: 1 });
  assert.strictEqual(peaks[2].support, null);
  assert.ok(c._isUnsupported(peaks[0]) && c._isUnsupported(peaks[1]) && !c._isUnsupported(peaks[2]));
  assert.ok(!c._isUnsupported({ support: null }) && !c._isUnsupported({}) && !c._isUnsupported(null));
});

// ── sites ───────────────────────────────────────────────────────────────────
const PEAKS = () => [
  { id: 1, name: 'Graphite', color: '#112233', visible: true, shape: 'asym-GL', center: 284.40, fwhm: 0.64, amplitude: 86000, glMix: 16, asymmetry: 0.1, support: { f: 1e4, supported: true } },
  { id: 2, name: 'Unknown 2', color: '#445566', visible: true, shape: 'GL', center: 282.25, fwhm: 0.42, amplitude: 215, glMix: 0, support: { f: 2.01, delta_chi2: 1.2, supported: false } },
  { id: 3, name: 'sat', color: '#778899', visible: true, shape: 'GL', center: 291.10, fwhm: 3.5, amplitude: 2600, glMix: 59, support: { f: 500, supported: true } },
];
function pageEnv(fns, extraArgs = {}) {
  const dom = {}; const els = {};
  const el = id => (els[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, classList: { add() {}, remove() {}, contains() { return false; } },
    setAttribute() {}, querySelectorAll: () => [], querySelector: () => null, appendChild(n) { (this.children ||= []).push(n); }, _rsfSource: 'scofield' });
  const document = { getElementById: el, querySelectorAll: () => [], querySelector: () => null,
    createElement: () => ({ style: {}, classList: { add() {} }, addEventListener() {}, set innerHTML(v) { this._html = v; }, get innerHTML() { return this._html; } }) };
  const state = { peaks: PEAKS(), rawBE: [1, 2, 3], ccShift: 0, lineWidth: 1.5,
    fitResult: { be: [280, 285, 290], chiReduced: 2.1, rmse: 12.5, rFactor: null, backendResult: { individual_peaks: PEAKS().map(p => ({ id: String(p.id), params: {
      center: { value: p.center, stderr: 0.01, vary: true, min: null, max: null }, fwhm: { value: p.fwhm, stderr: 0.02, vary: true, min: 0.1, max: 15 },
      amplitude: { value: p.amplitude, stderr: 3, vary: true, min: 0, max: null } } })) } } };
  const names = [...CORE, ...fns];
  const src = [constLine('_SUPPORT_MIN_F'), constLine('_UNSUPPORTED_LABEL'), constLine('_UNSUPPORTED_TIP'), ...names.map(extractFn)].join('\n');
  const args = { _escAttr: esc, _escHtml: esc, document, state, getPeak: id => state.peaks.find(p => p.id === Number(id)),
    _peakArea: p => p.amplitude * p.fwhm, getROIData: () => ({ be: [280, 285, 290] }), _buildStderrMap: fr => Object.fromEntries(fr.backendResult.individual_peaks.map(ip => [ip.id, ip.params])),
    _isLocalFit: () => false, _localFitCaveat: () => '', _localFitDetail: () => '', _startsPanelHtml: () => '', _validateUncertainties: () => ({ warnings: [], info: [] }),
    renderQuantify: () => {}, recalcQuantify: () => {}, _detectPeakRSF: () => ({ key: 'C 1s', rsf: 1 }), SCOFIELD_RSF: { 'C 1s': 1 }, notify: () => {},
    _clearDisallowedChargeRef: () => {}, _updateLocalModelBanner: () => {}, _updateLockAllBtn: () => {}, renderPeakForm: () => '', _highlightChartPeak: () => {},
    _isChargeRefAllowed: () => false, _fitStatLabel: () => 'χ²ᵣ', _isUnweightedLocal: () => false, _applyStatCaption: () => {}, _applyStatDisplay: () => {},
    _CHISQ_TOOLTIP: '', _LOCALFIT_TOOLTIP: '', _startsSummaryText: () => '', _startsChosenText: () => '', _startsIfCurrent: () => null, _startsLiveKey: () => '',
    _isLocalModel: () => false, _updateRFactorUI: () => {}, _activeTab: () => ({}), _renderRFactorPanel: () => '', _statIsChi: true,
    ...extraArgs };
  const api = new Function(...Object.keys(args), src + '\nreturn { ' + names.join(', ') + ' };')(...Object.values(args));
  return { ...api, state, els, document };
}

test('sidebar card: badge; centre and width shown as a dash; area % excluded and the others renormalised', () => {
  const env = pageEnv(['renderPeakList']);
  env.renderPeakList();
  const cards = env.els['peak-list'].children.map(c => c.innerHTML);
  assert.strictEqual(cards.length, 3);
  assert.match(cards[1], /unsupported-badge/);
  assert.match(cards[1], /<span class="peak-info">—<\/span>/);
  assert.doesNotMatch(cards[1], /282\.25|0\.42/);
  assert.match(cards[1], /peak-summary-val">—<\/span>\s*<span class="peak-summary-val">—<\/span>\s*<span class="peak-summary-val">—<\/span>/);
  assert.doesNotMatch(cards[0], /unsupported-badge/);
  const total = 86000 * 0.64 + 2600 * 3.5;                      // Unknown 2 excluded from the total
  assert.match(cards[0], new RegExp((86000 * 0.64 / total * 100).toFixed(1) + '%'));
});

test('results table: greyed row, no centre / width / sigma, area kept, percentage dash, and the note beneath', () => {
  const env = pageEnv(['renderResults', 'fmtVal'].filter(n => lines.some(l => new RegExp('^function ' + n + '\\(').test(l))));
  env.renderResults();
  const h = env.els['results-area'].innerHTML || Object.values(env.els).map(e => e.innerHTML).find(x => /unsupported-row/.test(x));
  assert.ok(h, 'results html');
  const row = h.slice(h.indexOf('unsupported-row'), h.indexOf('</tr>', h.indexOf('unsupported-row')));
  assert.match(row, /Unknown 2/);
  assert.doesNotMatch(row, /282\.25|0\.42|±/);
  assert.match(row, /<td>90<\/td>/);                          // its area (215 * 0.42) is shown, not hidden
  assert.match(row, /<td>&mdash;<\/td>\s*$/);
  assert.match(h, /One component is <b>not supported by the data<\/b> \(Unknown 2\)/);
  assert.match(h, /excluded from the percentages and from Quantify/);
  const gRow = h.slice(h.indexOf('Graphite'), h.indexOf('</tr>', h.indexOf('Graphite')));
  assert.match(gRow, new RegExp((86000 * 0.64 / (86000 * 0.64 + 2600 * 3.5) * 100).toFixed(1) + '%'), 'percentages over supported area only');
});

test('uncertainty panel: one rule-0 warning for the component, no per-parameter alarms and no "locked" note for it', () => {
  const env = pageEnv(['_validateUncertainties']);
  env.state.fitResult._preFit = {};
  env.state.fitResult.backendResult.individual_peaks[1].params.center.vary = false;   // as after Auto-Fit's centre lock
  const { warnings, info } = env._validateUncertainties();
  const mine = warnings.filter(w => /Unknown 2/.test(w));
  assert.strictEqual(mine.length, 1);
  assert.match(mine[0], /not supported by the data — removing it does not make the fit worse \(F = 2\.0, threshold 10\)/);
  assert.match(mine[0], /centre, width and uncertainties are not reported/);
  assert.ok(!info.some(i => /Unknown 2/.test(i)), 'not described as merely "locked"');
});

test('Quantify: excluded from the body, listed beneath with the reason; total and percentages over the rest', () => {
  const env = pageEnv(['renderQuantify', 'recalcQuantify']);
  env.document.getElementById('quantify-area');
  env.renderQuantify([86000 * 0.64, 215 * 0.42, 2600 * 3.5], 0);
  const h = env.els['quantify-area'].innerHTML;
  assert.doesNotMatch(h, /id="rsf-2"|qpct-2/);
  assert.match(h, /Not quantified — <b>not supported by the data<\/b>: Unknown 2/);
  assert.match(h, /0\.0 % would be a measurement claim/);
  assert.match(h, /id="rsf-1"/);
  // recalc: the excluded component contributes nothing to the total
  env.els['rsf-1'].value = '1'; env.els['rsf-3'].value = '1';
  env.recalcQuantify();
  assert.strictEqual(env.els['qtotal-norm'].textContent, String(Math.round(86000 * 0.64 + 2600 * 3.5)));
});

test('CSV / XLSX export: Status column, suppressed cells, At% empty, WARNING line', () => {
  const rows = [];
  const env = pageEnv(['exportFitTable', '_shapeExportCols'], {
    XLSX: { utils: { book_new: () => ({}), aoa_to_sheet: a => a, book_append_sheet: (wb, ws) => rows.push(ws) }, writeFile: () => {} },
    _downloadBlob: () => {}, _isUnweightedLocal: () => false,
  });
  env.state.fitResult.chiReduced = 2.1;
  env.exportFitTable('xlsx');
  const meta = rows[0], table = rows[1];
  assert.ok(meta.some(r => r[0] === 'WARNING' && /Not supported by the data .*Unknown 2/.test(r[1])));
  assert.strictEqual(table[0][1], 'Status');
  const u = table.find(r => r[0] === 'Unknown 2');
  assert.strictEqual(u[1], 'not supported by the data');
  assert.deepStrictEqual(u.slice(2, 6), ['', '', '', '']);                    // centre, σ, width, σ
  assert.strictEqual(u[u.length - 1], '', 'no At%');
  assert.strictEqual(table.find(r => r[0] === 'Graphite')[1], 'supported');
  const gAt = Number(table.find(r => r[0] === 'Graphite')[table[0].length - 1]);
  assert.ok(Math.abs(gAt - 86000 * 0.64 / (86000 * 0.64 + 2600 * 3.5) * 100) < 0.01, 'At% over the supported components');
});

test('publication figure: no label at the (zero) component, legend entry says so; chart and stack labels say so', () => {
  const fig = extractFn('_doPublicationExport');
  assert.match(fig, /if \(!p\.visible \|\| _isUnsupported\(p\)\) continue;\s*\/\/ no label/);
  assert.match(fig, /label: _isUnsupported\(p\) \? p\.name \+ ' \(not supported by the data\)' : p\.name, type: 'fill'/);
  assert.match(extractFn('updatePlot'), /label: _isUnsupported\(p\) \? p\.name \+ ' \(' \+ _UNSUPPORTED_LABEL \+ '\)' : p\.name,/);
  assert.match(extractFn('_buildStackDatasets'), /_isUnsupported\(pc\.peak\) \? ' \(' \+ _UNSUPPORTED_LABEL \+ '\)' : ''/);
  assert.match(extractFn('exportResults'), /_isUnsupported\(p\) \? p\.name \+ ' \(not supported by the data\)' : p\.name/);
});

test('write-back: a server result sets support; the local engine and a propagated model reset it', () => {
  assert.match(extractFn('applyBackendResult'), /^function applyBackendResult\(result\) \{\n  _applySupport\(state\.peaks, result\);/);
  assert.match(extractFn('runFitLocal'), /Object\.assign\(live, p\);\n\s*live\.support = null;/);
  assert.match(extractFn('runPropagation'), /amplitude: p\.linked \? p\.amplitude : p\.amplitude \* scale,\n\s*support: null/);
  assert.match(extractFn('runFitLocal'), /if \(param === 'amplitude'\)\s+return Math\.max\(0, v\);/, 'local amplitude floor is 0 (owner decision)');
});

test('persistence: support travels with the peak object through every save (the peak is spread whole)', () => {
  assert.match(extractFn('_doSaveFit'), /peaks: state\.peaks\.map\(p => \(\{\.\.\.p\}\)\)/);
  assert.match(extractFn('_doSaveSpectrum'), /peaks: tab\.peaks\.map\(p => \(\{\.\.\.p\}\)\)/);
  assert.match(html, /peaks: _normalizePeaksCRef\(\(t\.peaks \|\| \[\]\)\.map\(p => \(\{\.\.\.p\}\)\)\)/);
});
