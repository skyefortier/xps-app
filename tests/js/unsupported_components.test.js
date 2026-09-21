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

const CORE = ['_componentSupportCore', '_componentSupportFromResponse', '_supportRootOf', '_applySupportVerdicts', '_applySupport', '_isUnsupported', '_currentSupport', '_restampSupport', '_unsupportedBadge'];
function core() {
  const src = [constLine('_SUPPORT_MIN_F'), constLine('_UNSUPPORTED_LABEL'), constLine('_UNSUPPORTED_TIP'), ...CORE.map(extractFn)].join('\n');
  return new Function('_escAttr', '_startsLiveKey', 'state', src + '\nreturn { ' + CORE.join(', ') + ' };')(esc, () => 'KEY', { peaks: [] });
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

test('_applySupport writes every peak, follows ancestry to the root, stamps the fit key, and leaves null where the response says nothing', () => {
  const c = core();
  const peaks = [{ id: 1, name: 'root' }, { id: 2, name: 'child', linked: 1 }, { id: 3, name: 'grandchild', linked: 2 }, { id: 9, name: 'not in the response' }];
  c._applySupport(peaks, { individual_peaks: [
    { id: '1', support: { f: 0.5, delta_chi2: -3, supported: false } },
    { id: '2', support: { f: 99, delta_chi2: 9, supported: true } },       // the server resolves this too; the page uses the ROOT regardless of order
    { id: '3', support: { f: 99, delta_chi2: 9, supported: true } } ] }, 'KEY');
  assert.deepStrictEqual(peaks[0].support, { f: 0.5, delta_chi2: -3, supported: false, fitKey: 'KEY' });
  assert.deepStrictEqual(peaks[1].support, { f: 0.5, delta_chi2: -3, supported: false, fitKey: 'KEY', follows: 1 });
  assert.deepStrictEqual(peaks[2].support, { f: 0.5, delta_chi2: -3, supported: false, fitKey: 'KEY', follows: 1 });
  assert.strictEqual(peaks[3].support, null);
  assert.ok(c._isUnsupported(peaks[0]) && c._isUnsupported(peaks[2]) && !c._isUnsupported(peaks[3]));
  // a link cycle does not hang
  const cyc = [{ id: 1, linked: 2 }, { id: 2, linked: 1 }];
  c._applySupport(cyc, { individual_peaks: [{ id: '1', support: { f: 0, supported: false } }, { id: '2', support: { f: 0, supported: false } }] }, 'KEY');
  assert.ok(cyc[0].support && cyc[1].support);
});

test('the verdict applies only to the model and context it was computed for', () => {
  const c = core();
  const p = { id: 1, support: { f: 1, supported: false, fitKey: 'KEY' } };
  assert.strictEqual(c._isUnsupported(p), true);
  p.support.fitKey = 'ANOTHER MODEL';                      // the student edited something since the fit
  assert.strictEqual(c._isUnsupported(p), false, 'nothing is suppressed or excluded on a model the verdict does not describe');
  assert.strictEqual(c._isUnsupported({ id: 1, support: { f: 1, supported: false } }), false, 'a verdict without a key (older save) is not applied');
});

test('the local engine computes the same statistic from its own residuals', () => {
  const c = core();
  const counts = [1000, 1000, 1010, 1000, 1000], fitted = [1000, 1000, 1005, 1000, 1000], comp = [0, 0, 5, 0, 0];
  const w = counts.map(v => 1 / Math.sqrt(v));
  const mine = c._componentSupportCore(counts, fitted, comp, w, 3, 3);
  const twin = c._componentSupportFromResponse({ counts, fitted_y: fitted, statistics: { n_free_params: 3 },
    individual_peaks: [{ id: '1', y: comp, params: { a: { vary: true }, b: { vary: true }, c: { vary: true } } }] }, 1);
  assert.deepStrictEqual(mine, twin);
  assert.match(extractFn('runFitLocal'), /_applySupportVerdicts\(state\.peaks, id => verdicts\[String\(id\)\] \|\| null, _startsLiveKey\(\)\);/);
});

// ── sites ───────────────────────────────────────────────────────────────────
const PEAKS = () => [
  { id: 1, name: 'Graphite', color: '#112233', visible: true, shape: 'asym-GL', center: 284.40, fwhm: 0.64, amplitude: 86000, glMix: 16, asymmetry: 0.1, support: { f: 1e4, supported: true, fitKey: 'KEY' } },
  { id: 2, name: 'Unknown 2', color: '#445566', visible: true, shape: 'GL', center: 282.25, fwhm: 0.42, amplitude: 215, glMix: 0, support: { f: 2.01, delta_chi2: 1.2, supported: false, fitKey: 'KEY' } },
  { id: 3, name: 'sat', color: '#778899', visible: true, shape: 'GL', center: 291.10, fwhm: 3.5, amplitude: 2600, glMix: 59, support: { f: 500, supported: true, fitKey: 'KEY' } },
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
    _startsLiveKey: () => 'KEY',
    _peakArea: p => p.amplitude * p.fwhm, getROIData: () => ({ be: [280, 285, 290] }), _buildStderrMap: fr => Object.fromEntries(fr.backendResult.individual_peaks.map(ip => [ip.id, ip.params])),
    _isLocalFit: () => false, _localFitCaveat: () => '', _localFitDetail: () => '', _startsPanelHtml: () => '', _validateUncertainties: () => ({ warnings: [], info: [] }),
    renderQuantify: () => {}, recalcQuantify: () => {}, _detectPeakRSF: () => ({ key: 'C 1s', rsf: 1 }), SCOFIELD_RSF: { 'C 1s': 1 }, notify: () => {},
    _clearDisallowedChargeRef: () => {}, _updateLocalModelBanner: () => {}, _updateLockAllBtn: () => {}, renderPeakForm: () => '', _highlightChartPeak: () => {},
    _isChargeRefAllowed: () => false, _fitStatLabel: () => 'χ²ᵣ', _isUnweightedLocal: () => false, _applyStatCaption: () => {}, _applyStatDisplay: () => {},
    _CHISQ_TOOLTIP: '', _LOCALFIT_TOOLTIP: '', _startsSummaryText: () => '', _startsChosenText: () => '', _startsIfCurrent: () => null,
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
  assert.match(mine[0], /not supported by the data — with the other components held as fitted, removing it does not make the fit significantly worse \(F = 2\.0, threshold 10\)/);
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
  assert.match(extractFn('_buildStackDatasets'), /_isUnsupported\(pc\.peak, _startsRecordKey\(src\)\) \? ' \(' \+ _UNSUPPORTED_LABEL \+ '\)' : ''/);
  assert.match(extractFn('exportResults'), /_isUnsupported\(p\) \? p\.name \+ ' \(not supported by the data\)' : p\.name/);
});

test('write-back: a server result sets support; the local engine and a propagated model reset it', () => {
  const abr = extractFn('applyBackendResult');
  assert.ok(abr.indexOf('_applyBackendParams(p, ipeak.params);') < abr.indexOf('_applySupport(state.peaks, result, _startsLiveKey());'), 'the key is taken AFTER the values are applied');
  assert.match(extractFn('runPropagation'), /amplitude: p\.linked \? p\.amplitude : p\.amplitude \* scale,\n\s*support: null/);
  assert.match(extractFn('runFitLocal'), /if \(param === 'amplitude'\)\s+return Math\.max\(0, v\);/, 'local amplitude floor is 0 (owner decision)');
});

test('persistence: support travels with the peak object through every save (the peak is spread whole)', () => {
  assert.match(extractFn('_doSaveFit'), /peaks: state\.peaks\.map\(p => \(\{\.\.\.p\}\)\)/);
  assert.match(extractFn('_doSaveSpectrum'), /peaks: tab\.peaks\.map\(p => \(\{\.\.\.p\}\)\)/);
  assert.match(html, /peaks: _normalizePeaksCRef\(\(t\.peaks \|\| \[\]\)\.map\(p => \(\{\.\.\.p\}\)\)\)/);
});


test('CSV / XLSX: an unsupported DS+G component exports no width of any kind (beta, m)', () => {
  const rows = [];
  const env = pageEnv(['exportFitTable', '_shapeExportCols'], {
    XLSX: { utils: { book_new: () => ({}), aoa_to_sheet: a => a, book_append_sheet: (wb, ws) => rows.push(ws) }, writeFile: () => {} },
    _downloadBlob: () => {}, _isUnweightedLocal: () => false,
  });
  Object.assign(env.state.peaks[1], { shape: 'DSG_LA', laAlpha: 0.1, laBeta: 0.3, laM: 0.4 });
  env.state.fitResult.chiReduced = 2.1;
  env.exportFitTable('xlsx');
  const table = rows[1], u = table.find(r => r[0] === 'Unknown 2');
  const hdr = table[0];
  assert.strictEqual(u[hdr.indexOf('Beta')], '');
  assert.strictEqual(u[hdr.indexOf('M_Gauss')], '');
  assert.strictEqual(u[hdr.indexOf('Alpha')], 0.1, 'alpha is an asymmetry, not a width: kept');
});

test('the scattered-starts table: an unsupported component shows neither area % nor a move in "Your fit", and is not the largest move', () => {
  const env = pageEnv(['_startsPanelHtml', '_startsSummaryText', '_startsShiftHtml', '_startsShiftColour', '_startsEv', '_startsPeakName', '_startsIfCurrent'], {
    _STARTS_SHIFT_AMBER_EV: 0.5, _STARTS_SHIFT_RED_EV: 1.0, _STARTS_TOOLTIP: '' });
  const comp = (id, pct, shift) => ({ id, area_percent: pct, center_shift_from_start: shift, params: { center: 285 } });
  const st = { ran: true, n_run: 3, n_converged: 3, n_same_as_fit: 2, n_in_alternatives: 1, n_not_better_elsewhere: 0, not_better_chi2r: [],
    fit: { chi2r: 5.3, largest_centre_shift_from_start: { id: 2, ev: 1.4 }, components: [comp(1, 60, 0.02), comp(2, 0.3, 1.4), comp(3, 39.7, 0)] },
    alternatives: [{ chi2r: 4.3, n_starts: 1, largest_centre_shift_from_start: { id: 2, ev: -0.9 }, largest_fraction_difference_pp: 10,
      components: [comp(1, 50, 0.1), comp(2, 12, -0.9), comp(3, 38, 0)] }] };
  env.state.fitResult.starts = st; env.state.fitResult.startsModelKey = 'KEY';
  const h = env._startsPanelHtml(env.state.fitResult);
  const yours = h.slice(h.indexOf('Your fit'), h.indexOf('Alternative 1'));
  assert.match(yours, /not supported by the data/);
  assert.doesNotMatch(yours, /0\.3<br>|\+1\.40 eV/, 'no area % and no move for the unsupported component');
  assert.match(yours, /sat \+0\.00 eV|Graphite \+0\.02 eV/, 'largest move among SUPPORTED components');
  const alt = h.slice(h.indexOf('Alternative 1'));
  assert.match(alt, /12\.0<br>/, 'an alternative is a different solution: its components are shown as they are');
});


// ── Codex round 2 ───────────────────────────────────────────────────────────
test('exports: a stale or keyless verdict is "not established", never "supported"', () => {
  const c = core();
  assert.strictEqual(c._currentSupport({ support: { supported: false, fitKey: 'OLD' } }), null);
  assert.strictEqual(c._currentSupport({ support: { supported: true } }), null);
  assert.deepStrictEqual(c._currentSupport({ support: { supported: true, fitKey: 'KEY' } }), { supported: true, fitKey: 'KEY' });
  const rows = [];
  const env = pageEnv(['exportFitTable', '_shapeExportCols'], {
    XLSX: { utils: { book_new: () => ({}), aoa_to_sheet: a => a, book_append_sheet: (wb, ws) => rows.push(ws) }, writeFile: () => {} },
    _downloadBlob: () => {}, _isUnweightedLocal: () => false,
  });
  env.state.peaks[1].support.fitKey = 'A MODEL THE STUDENT SINCE EDITED';
  env.state.fitResult.chiReduced = 2.1;
  env.exportFitTable('xlsx');
  const table = rows[1];
  assert.strictEqual(table.find(r => r[0] === 'Unknown 2')[1], '', 'stale: no status either way');
  assert.notStrictEqual(table.find(r => r[0] === 'Unknown 2')[2], '', 'and its centre is reported again');
  assert.strictEqual(table.find(r => r[0] === 'Graphite')[1], 'supported');
});

test('Auto-Fit finalisation (locks, charge shift) keeps its own verdicts: _restampSupport, called after the locks', () => {
  const src = extractFn('applyAutoFitResult');
  assert.ok(src.indexOf('for (const p of state.peaks) p.fixCenter = true;') < src.indexOf('_restampSupport()'), 're-stamped after the lock');
  assert.ok(src.indexOf('_restampSupport()') < src.indexOf('renderPeakList()'), 'and before anything renders');
  const c = core();
  const peaks = [{ id: 1, support: { supported: false, fitKey: 'BEFORE THE LOCKS' } }, { id: 2, support: null }];
  const api = new Function('_startsLiveKey', 'state', extractFn('_restampSupport') + '\nreturn _restampSupport;')(() => 'AFTER', { peaks });
  api();
  assert.strictEqual(peaks[0].support.fitKey, 'AFTER');
  assert.strictEqual(peaks[1].support, null);
});

test('a .fit.json import onto this tab\'s data carries no verdict', () => {
  assert.match(html, /state\.peaks = _normalizePeaksCRef\(\(data\.peaks \|\| \[\]\)\.map\(p => \(\{\.\.\.p, support: null\}\)\)\);/);
});

test('_isUnsupported is never handed an array index as its key (Array.filter passes one)', () => {
  assert.strictEqual((html.match(/filter\(_isUnsupported\)/g) || []).length, 0);
  const c = core();
  const p = { id: 1, support: { supported: false, fitKey: 'KEY' } };
  assert.deepStrictEqual([p].filter(q => c._isUnsupported(q)), [p]);
});

test('a key change re-renders every consumer of the verdict — each compared with ITS OWN rendering', () => {
  const src = extractFn('_refreshStartsEvidence');
  assert.match(src, /shownIn\('#peak-list \.unsupported-badge'\) !== flaggedNow[^\n]*renderPeakList\(\)/);
  assert.match(src, /shownIn\('\.results-table \.unsupported-row'\) !== flaggedNow[^\n]*renderResults\(\)/);
  assert.match(src, /chartFlagged !== flaggedNow\) \{ updatePlot\(\); return; \}/);
  assert.match(extractFn('updatePlot'), /_refreshStartsEvidence\(false, true\);/, 'no re-entrant repaint from inside updatePlot');
  // Codex round 3: a caller that redrew the sidebar first (addPeak, Lock All) must still get the tables refreshed
  const calls = [];
  const state = { peaks: [{ id: 2, support: { supported: false, fitKey: 'OLD' } }], fitResult: {}, chart: { data: { datasets: [{ _peakId: 2, _unsupported: true }] } } };
  const document = { querySelectorAll: sel => sel.includes('peak-list') ? [] : [{ getAttribute: () => '2' }], querySelector: () => null };
  const fn = new Function('state', 'document', '_startsLiveKey', '_isUnsupported', '_historyPreview', '_dropStaleAltPreview', 'renderPeakList', 'renderResults', 'updatePlot', '_startsPanelHtml',
    src + '\nreturn _refreshStartsEvidence;')(state, document, () => 'NEW', (p, k) => p.support.supported === false && p.support.fitKey === k, null, () => {},
    () => calls.push('sidebar'), () => calls.push('results'), () => calls.push('plot'), () => '');
  fn(false);
  assert.deepStrictEqual(calls, ['results', 'plot'], 'sidebar already clean; Results and the chart still stale');
  for (const fn of ['toggleLock', 'toggleAllLocks']) assert.match(extractFn(fn), /_refreshStartsEvidence\(true\);/, fn);
  assert.match(extractFn('updatePlot'), /_refreshStartsEvidence\(false, true\);/);
});

test('stack tabs judge a source component against the SOURCE record\'s key', () => {
  assert.match(extractFn('_buildStackDatasets'), /_isUnsupported\(pc\.peak, _startsRecordKey\(src\)\)/);
  const c = core();
  const p = { id: 1, support: { supported: false, fitKey: 'SRC' } };
  assert.strictEqual(c._isUnsupported(p, 'SRC'), true);
  assert.strictEqual(c._isUnsupported(p, 'the active stack tab'), false);
});

test('"Your fit" percentages are over supported components; an empty Quantify shows no 100 %', () => {
  const env = pageEnv(['_startsPanelHtml', '_startsSummaryText', '_startsShiftHtml', '_startsShiftColour', '_startsEv', '_startsPeakName', '_startsIfCurrent'], {
    _STARTS_SHIFT_AMBER_EV: 0.5, _STARTS_SHIFT_RED_EV: 1.0, _STARTS_TOOLTIP: '' });
  const comp = (id, pct, shift) => ({ id, area_percent: pct, center_shift_from_start: shift, params: { center: 285 } });
  env.state.fitResult.starts = { ran: true, n_run: 3, n_converged: 3, n_same_as_fit: 2, n_in_alternatives: 1, n_not_better_elsewhere: 0, not_better_chi2r: [],
    fit: { chi2r: 5.3, largest_centre_shift_from_start: { id: 2, ev: 1.4 }, components: [comp(1, 60, 0.02), comp(2, 0.3, 1.4), comp(3, 39.7, 0)] },
    alternatives: [{ chi2r: 4.3, n_starts: 1, largest_centre_shift_from_start: { id: 2, ev: -0.9 }, largest_fraction_difference_pp: 10, components: [comp(1, 50, 0.1), comp(2, 12, -0.9), comp(3, 38, 0)] }] };
  env.state.fitResult.startsModelKey = 'KEY';
  const yours = env._startsPanelHtml(env.state.fitResult); const y = yours.slice(yours.indexOf('Your fit'), yours.indexOf('Alternative 1'));
  assert.match(y, /60\.2<br>/); assert.match(y, /39\.8<br>/);
  const q = pageEnv(['renderQuantify', 'recalcQuantify']);
  for (const p of q.state.peaks) p.support = { supported: false, fitKey: 'KEY' };
  q.document.getElementById('quantify-area');
  q.renderQuantify([1, 1, 1], 0);
  assert.strictEqual(q.els['qtotal-pct'].textContent, '—');
});
