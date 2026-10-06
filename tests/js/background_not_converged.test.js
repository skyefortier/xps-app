// A background that does not satisfy its defining statement is "not converged"
// and nothing on the page uses it as a background (owner, 2026-10-01; background
// math F10, F11, F12). computeBackgroundCore marks every result with its
// certificate (converged / failure), and the producers consumers call throw
// BgNotConverged rather than hand out a failed curve (Codex impl round 3).
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
const lines = html.split('\n');
const B = new Function(require('./_page_background_source.js')() +
  '\nreturn { computeBackgroundCore, _bgFailure, _certifiedBg, _bgOrFailure, _isBgNotConverged };')();

function enclosingFunction(lineIdx) {
  let start = lineIdx;
  while (start >= 0 && !/^(async )?function [A-Za-z_$][\w$]*\(/.test(lines[start])) start--;
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return { name: lines[start].match(/function ([\w$]+)/)[1], body: lines.slice(start, i + 1).join('\n') };
  }
  throw new Error('unbalanced function around line ' + (lineIdx + 1));
}

// Codex impl round 3: a guard that checks each consumer's own refusal is always one
// call form behind (rounds 1-3 each found a way past it). The CLASS is closed by
// construction instead: the producers a consumer can call THROW BgNotConverged rather
// than return a background that failed its statement, so a consumer that forgets to
// refuse aborts — it cannot draw, subtract, fit, save or export the curve. What is
// pinned here: (1) the only callers of computeBackgroundCore and of the method twins
// are the producers (nothing reaches an unchecked curve by another road); (2) the
// producers throw (behavioural, below); (3) every consumer call is HANDLED — wrapped
// in _bgOrFailure(() => ...) or inside a try whose catch tests _isBgNotConverged — so
// the student is told why instead of the page aborting.
const PRODUCERS = ['computeBackground', '_computeBackgroundForSource', '_recordBackground'];
const stripComment = l => l.replace(/\/\/.*$/, '');
const code = lines.map(stripComment);

function callersOf(name) {
  const re = new RegExp('\\b' + name.replace(/\$/g, '\\$') + '\\b');
  const out = [];
  code.forEach((l, i) => {
    if (!re.test(l) || new RegExp('^\\s*(async )?function ' + name + '\\(').test(l)) return;
    out.push({ line: i + 1, text: l.trim(), fn: enclosingFunction(i).name });
  });
  return out;
}

test('only the producers reach computeBackgroundCore and the method twins', () => {
  const allowed = {
    computeBackgroundCore: ['computeBackground', '_computeBackgroundForSource'],
    _computeBackgroundUnchecked: ['computeBackgroundCore'],   // its finiteness check wraps every method (round 5)
    shirleyBackground: ['_computeBackgroundUnchecked', 'smartBackground'],
    smartBackground: ['_computeBackgroundUnchecked'], smartExperimentalBackground: ['_computeBackgroundUnchecked'],
    shirleyLinearBackground: ['_computeBackgroundUnchecked'], tougaardBackground: ['_computeBackgroundUnchecked'],
    manualAnchorBackground: ['_computeBackgroundUnchecked'], linearBackground: ['_computeBackgroundUnchecked', 'manualAnchorBackground'],
  };
  for (const [name, fns] of Object.entries(allowed)) {
    const sites = callersOf(name);
    assert.ok(sites.length > 0, name + ' is called');
    for (const s of sites) assert.ok(fns.includes(s.fn), `${name} referenced from ${s.fn} (line ${s.line}): ${s.text}`);
  }
  for (const p of ['computeBackground', '_computeBackgroundForSource']) {
    const body = enclosingFunction(lines.findIndex(l => l.startsWith('function ' + p + '('))).body;
    const calls = body.match(/computeBackgroundCore\(/g) || [];
    const certified = body.match(/_certifiedBg\(computeBackgroundCore\(/g) || [];
    assert.ok(calls.length >= 1 && calls.length === certified.length, p + ' hands out computeBackgroundCore only through _certifiedBg');
  }
});

test('every consumer call of a producer is handled (the student is told why, the page does not abort)', () => {
  const sites = [];
  for (const p of PRODUCERS) for (const s of callersOf(p)) if (!PRODUCERS.includes(s.fn)) sites.push({ ...s, p });
  assert.ok(sites.length >= 11, 'found the consumers: ' + sites.map(s => s.fn).join(', '));
  for (const s of sites) {
    if (new RegExp('_bgOrFailure\\(\\(\\) => ' + s.p + '\\(').test(s.text)) continue;
    // otherwise: inside `try { ... }` whose catch tests _isBgNotConverged
    const fn = enclosingFunction(s.line - 1);
    const at = fn.body.indexOf(s.text) + s.text.indexOf(s.p + '(');
    const before = fn.body.slice(0, at), after = fn.body.slice(at);
    const tryAt = before.lastIndexOf('try {');
    assert.ok(tryAt >= 0 && !/\}\s*catch/.test(before.slice(tryAt)), `${s.fn} (line ${s.line}): ${s.p} called outside _bgOrFailure and outside a try: ${s.text}`);
    assert.ok(/^[^]*?catch \(e\) \{[^}]*_isBgNotConverged\(e\)/.test(after) && after.indexOf('catch (e)') < after.indexOf('\n}'),
      `${s.fn} (line ${s.line}): its catch does not handle BgNotConverged`);
  }
});

test('computeBackgroundCore marks a non-converged background and its plain reason', () => {
  const cyc = B.computeBackgroundCore([0, 1, 2, 3], [2, 3, 10, 13], { bgType: 'shirley', endpointAvg: '1', bgStart: '', bgEnd: '' });
  assert.strictEqual(cyc.converged, false);
  assert.match(B._bgFailure(cyc), /^Shirley background not converged: the result misses the Shirley relation by /);
  const flat = B.computeBackgroundCore([0, 1, 2, 3, 4], [10, 5, 5, 17, 20], { bgType: 'smart', endpointAvg: '1', bgStart: '', bgEnd: '' });
  assert.match(B._bgFailure(flat), /no net signal/);
  const ok = B.computeBackgroundCore([0, 1, 2, 3, 4, 5], [10, 12, 40, 30, 22, 20], { bgType: 'shirley', endpointAvg: '1', bgStart: '', bgEnd: '' });
  assert.strictEqual(ok.converged, true);
  assert.strictEqual(B._bgFailure(ok), null);
  for (const t of ['linear', 'none']) assert.strictEqual(B.computeBackgroundCore([0, 1, 2], [1, 2, 3], { bgType: t, endpointAvg: '1', bgStart: '', bgEnd: '' }).converged, true);
});

test('the note under the method menu shows the failure and hides when it clears', () => {
  const src = lines.slice(lines.findIndex(l => l.startsWith('function _refreshBgConvergenceNote(')));
  const fnSrc = enclosingFunction(lines.findIndex(l => l.startsWith('function _refreshBgConvergenceNote('))).body;
  const el = { style: {}, textContent: '', dataset: {} };
  const refresh = new Function('document', fnSrc + '\nreturn _refreshBgConvergenceNote;')({ getElementById: id => id === 'bg-not-converged' ? el : null });
  refresh('Shirley background not converged: x.');
  assert.strictEqual(el.style.display, 'block');
  assert.match(el.textContent, /^Shirley background not converged: x\. Nothing is subtracted or fitted against it/);
  refresh(null);
  assert.strictEqual(el.style.display, 'none');
  assert.strictEqual(src.length > 0, true);
  assert.match(html, /<div id="bg-not-converged" role="alert"/);
});

test('Run Fit refuses a non-converged background before anything changes (no undo entry, no spinner, no request)', () => {
  const body = enclosingFunction(lines.findIndex(l => l.startsWith('async function runFit('))).body;
  const check = body.indexOf('if (bgPre.failure)');
  assert.ok(check > 0);
  for (const later of ['pushUndo()', '_showFitSpinner()', 'uploadToBackend(', 'runFitLocal(']) {
    const at = body.indexOf(later);
    assert.ok(at > check, `${later} comes after the convergence refusal`);
  }
});

test('Auto-Fit refuses in its preflight, before it claims the tab (a running Run Fit is left alone)', () => {
  const body = enclosingFunction(lines.findIndex(l => l.startsWith('async function runAutoFitC1sGraphite('))).body;
  const at = body.indexOf('_bgOrFailure(() => computeBackground(corrBE, inten))');
  assert.ok(at > 0 && body.indexOf('if (bgR.failure)') > at && body.indexOf('if (bgR.failure)') < body.indexOf('_installFitOp(afOp)'));
});

test('the Shirley iterations setting is retired (hidden; kept for saved files and fit keys)', () => {
  assert.match(html, /<div class="field" style="display:none" aria-hidden="true">\s*<label>Shirley iterations<\/label>/);
  const core = enclosingFunction(lines.findIndex(l => l.startsWith('function computeBackgroundCore('))).body;
  assert.ok(!/shirleyIter/.test(core.replace(/\/\/.*$/mg, '')), 'computeBackgroundCore does not read it');
});

test('the background tooltips say the noise bias plainly (findings F2)', () => {
  const tip = v => html.match(new RegExp('<option value="' + v + '"(?: disabled hidden)? data-tip="([^"]*)"'))[1];
  assert.match(tip('smart'), /raises net area by about 1 % on noisy data/);
  assert.match(tip('smart_exp'), /raises net area by about 1 % on noisy data/);
  assert.match(tip('smart_exp'), /plain Shirley carries its own bias at large steps/);
  assert.match(tip('shirley'), /its own net-area bias at large background steps/);
  assert.match(html, /<option value="shirley_linear" disabled hidden/, 'shirley_linear stays off the menu');
  // F3 (owner 2026-10-03): one Smart entry; Smart (experimental) kept for saved files only
  assert.match(html, /<option value="smart_exp" disabled hidden/, 'smart_exp is off the menu');
  assert.match(html, /<option value="smart" data-tip="[^"]*">Smart<\/option>/, 'the one entry is "Smart"');
  assert.match(html, /id="bg-legacy-note"/, 'its notice stays');
});

// ── Codex impl round 3: the producers throw; the record path reads the record ──
// a top-level `const NAME = ...;` that may span lines
function constBlock(name) {
  const s = lines.findIndex(l => l.startsWith('const ' + name + ' ='));
  let e = s; while (!/;\s*$/.test(lines[e])) e++;
  return lines.slice(s, e + 1).join('\n');
}
function recordEnv() {
  const fn = name => enclosingFunction(lines.findIndex(l => new RegExp('^(async )?function ' + name + '\\(').test(l))).body;
  const src = require('./_page_background_source.js')({ manual: 'real' }) + '\n' +
    lines.find(l => l.startsWith('const LEGACY_ENDPOINT_AVG =')) + '\n' +
    lines.find(l => l.startsWith('const BG_RESTORE_REL =')) + '\n' +
    constBlock('_STARTS_MODEL_FIELDS') + '\n' + constBlock('_STARTS_UI_FIELDS') + '\n' +
    ['manualAnchorBackground', '_roiSelect', '_computeBackgroundForSource', '_recordBackground',
     '_restoredFitBgFailure', '_dropRestoredFit', '_restoredFitGrid', '_restoredFitModel', 'evalAllPeaks', '_arrMin', '_arrMax',
     '_restoredFitPeaks', '_asFitted', '_restoredModelIsFit', '_legacyVoigts', '_restoredStale', '_startsModelKey', '_startsRecordKey',
     'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic', 'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS',
     '_laKernelHalf', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve',
     'dsgConvolved_array', 'evalPeakArray', 'getPeak'].map(fn).join('\n') +
    '\nconst _getManualAnchors = () => { throw new Error("the active tab is not read"); };' +
    '\nreturn { computeBackgroundCore, _certifiedBg, _bgOrFailure, _isBgNotConverged, _roiSelect, _computeBackgroundForSource, _recordBackground, _restoredFitBgFailure, _fmt3, BG_RESTORE_REL, evalAllPeaks, _startsRecordKey, _restoredStale, _restoredModelIsFit, _restoredFitGrid };';
  return new Function(src)();
}
const R = recordEnv();
// "today's background, as far as the record lets it be said": a keyed fit current (no
// difference); a keyless one never confirmed current (owner 2026-10-05) — stale
// "unconfirmed" with a reconstructed difference within the restore's tolerance
const agreesToday = fr => !fr.backgroundStale ||
  (fr.backgroundStale.unconfirmed === true && fr.backgroundStale.matches === true && !fr.startsModelKey);
const peakRec = (over = {}) => {
  const rawBE = [], rawIntensity = [];
  for (let i = 0; i <= 120; i++) { const x = 280 + 0.1 * i; rawBE.push(x); rawIntensity.push(100 + 40 / (1 + Math.exp(-(x - 286) * 3)) + 500 * Math.exp(-((x - 285.5) ** 2) / 0.5)); }
  return { rawBE, rawIntensity, ccShift: 0, ui: { bgType: 'shirley', endpointAvg: '3', roiMin: '281', roiMax: '291', bgStart: '', bgEnd: '' },
           manualAnchors: [], peaks: [{ id: 1, support: { f: 1 } }], ...over };
};

test('the producers THROW a background that fails its statement (never return it)', () => {
  const cyc = { bgType: 'shirley', endpointAvg: '1' };
  assert.throws(() => R._computeBackgroundForSource([0, 1, 2, 3], [2, 3, 10, 13], cyc), e => R._isBgNotConverged(e) && /not converged/.test(e.message));
  assert.throws(() => R._recordBackground({ rawBE: [0, 1, 2, 3], rawIntensity: [2, 3, 10, 13], ccShift: 0, ui: cyc }), e => R._isBgNotConverged(e));
  assert.throws(() => R._certifiedBg([1, 2, 3]), e => R._isBgNotConverged(e), 'an unmarked array is not a background');
  const r = R._bgOrFailure(() => R._computeBackgroundForSource([0, 1, 2, 3], [2, 3, 10, 13], cyc));
  assert.strictEqual(r.bg, null); assert.match(r.failure, /not converged/);
  assert.throws(() => R._bgOrFailure(() => { throw new TypeError('x'); }), TypeError, 'any other error propagates');
  assert.strictEqual(R._computeBackgroundForSource([0, 1, 2, 3, 4, 5], [10, 12, 40, 30, 22, 20], { bgType: 'shirley', endpointAvg: '1' }).converged, true);
});

test('getROIData and the record path select the same points: one rule (_roiSelect)', () => {
  assert.ok(/function getROIData\(\) \{\s*return _roiSelect\(state\.rawBE, state\.rawIntensity, state\.ccShift,/.test(html));
  const be = [295, 293, 291, 289, 287, 285], y = [1, 2, 3, 4, 5, 6];
  const asc = be.slice().reverse(), yAsc = y.slice().reverse();
  for (const [mn, mx, shift] of [['', '', 0], ['288', '', 0], ['', '290', 0], ['286', '292', 1], ['abc', '291', 0], ['289', '289', 0]]) {
    const d = R._roiSelect(be, y, shift, mn, mx), a = R._roiSelect(asc, yAsc, shift, mn, mx);
    const lo = isNaN(parseFloat(mn)) ? -Infinity : parseFloat(mn), hi = isNaN(parseFloat(mx)) ? Infinity : parseFloat(mx);
    const want = be.map((e, i) => [e - shift, y[i]]).filter(([c]) => c >= lo && c <= hi);
    assert.deepStrictEqual(d.be, want.map(w => w[0]), `descending, ${mn}..${mx} shift ${shift}`);
    assert.deepStrictEqual(a.be, want.map(w => w[0]).reverse(), `ascending, ${mn}..${mx}`);
    const rec = R._recordBackground({ rawBE: be, rawIntensity: y, ccShift: shift, ui: { bgType: 'none', roiMin: mn, roiMax: mx } });
    assert.deepStrictEqual(rec.be, d.be, 'the record path is the same selection');
  }
});

test('a manual background on a record is built from THAT record\'s anchors (no Shirley substitute, no active-tab read)', () => {
  const anchors = [{ x: 282, y: 100 }, { x: 290, y: 140 }];
  const rec = peakRec({ ui: { ...peakRec().ui, bgType: 'manual' }, manualAnchors: anchors });
  const { be, bg } = R._recordBackground(rec);
  be.forEach((x, i) => {
    const want = x < 282 ? 100 : x >= 290 ? 140 : ((140 - 100) / (290 - 282)) * (x - 282) + 100;
    assert.strictEqual(bg[i], want);
  });
});

test('restore: the background the fit USED (envelope less peaks) against today\'s — current, stale (sized) or peaks-only', () => {
  // owner 2026-10-03: the stored background curve was the page's preview; the fit's own
  // background is its envelope less its peaks
  const G = [{ id: 1, name: 'g', shape: 'Gaussian', center: 285.5, fwhm: 1.0, amplitude: 300 }];
  const fitWith = (rec, peaks = G) => {
    const { be, bg } = R._recordBackground(rec);
    const model = R.evalAllPeaks(be, peaks), { rawY } = R._recordBackground(rec);
    const fittedY = Array.from(bg).map((v, i) => v + model[i]);
    const rmse = Math.sqrt(rawY.reduce((a, v, i) => a + (v - fittedY[i]) ** 2, 0) / rawY.length);   // every save has it
    return { ...rec, peaks, fitResult: { uploadFull: true, be: be.slice(), fittedY, rmse, bgIntensity: be.map(() => 0) } };
  };
  for (const bgType of ['shirley', 'smart', 'tougaard', 'linear', 'none', 'manual']) {
    const base = peakRec({ ui: { ...peakRec().ui, bgType }, manualAnchors: [{ x: 282, y: 100 }, { x: 290, y: 140 }] });
    const rec = fitWith(base);
    assert.strictEqual(R._restoredFitBgFailure(rec), null, bgType + ': its own background reloads');
    assert.ok(agreesToday(rec.fitResult), bgType + ': as current');
    if (bgType !== 'none') assert.ok(Array.from(rec.fitResult.bgIntensity).some(v => v !== 0), bgType + ': the certified curve is installed');
    // the settings changed after the fit: reloaded STALE with the fit's own background, sized
    const stale = fitWith(base); stale.ui = { ...stale.ui, bgType: bgType === 'none' ? 'linear' : 'none' };
    const want = stale.fitResult.fittedY.map((v, i) => v - R.evalAllPeaks(stale.fitResult.be, G)[i]);
    assert.strictEqual(R._restoredFitBgFailure(stale), null, bgType + ': a changed method reloads, stale');
    assert.ok(stale.fitResult.backgroundStale && stale.fitResult.backgroundStale.pct > 0.1, bgType + ': marked stale with its size');
    assert.deepStrictEqual(Array.from(stale.fitResult.bgIntensity), want, bgType + ': the fit\'s own background is shown');
    if (bgType === 'manual') {
      const moved = fitWith(base); moved.manualAnchors = [{ x: 282, y: 100 }, { x: 290, y: 150 }];
      assert.strictEqual(R._restoredFitBgFailure(moved), null); assert.ok(moved.fitResult.backgroundStale, 'moved anchors: stale');
    }
    for (const bad of [v => String(v), () => null, () => 'abc', () => undefined, () => NaN]) {
      const r = fitWith(base); r.fitResult.fittedY[3] = bad(r.fitResult.fittedY[3]);
      assert.match(R._restoredFitBgFailure(r) || '', /stored envelope is not a number at every point/, bgType + ': a non-number fails closed');
    }
  }
  // within fit_equality's rounding on the background's own scale: current; beyond: stale, sized
  const base2 = fitWith(peakRec()), used = base2.fitResult.fittedY.map((v, i) => v - R.evalAllPeaks(base2.fitResult.be, G)[i]);
  const scale = Math.max(...used.map(Math.abs));
  // (the record stays consistent: its RMSE is its own envelope's — Codex impl round 24)
  const reRmse = r => { const y = R._recordBackground(r).rawY; r.fitResult.rmse = Math.sqrt(y.reduce((a, v, i) => a + (v - r.fitResult.fittedY[i]) ** 2, 0) / y.length); };
  const near = fitWith(peakRec()); near.fitResult.fittedY[5] += 0.5 * R.BG_RESTORE_REL * scale; reRmse(near);
  assert.strictEqual(R._restoredFitBgFailure(near), null); assert.ok(agreesToday(near.fitResult), 'within the tolerance: current');
  const far = fitWith(peakRec()); far.fitResult.fittedY[5] += 2 * R.BG_RESTORE_REL * scale; reRmse(far);
  assert.strictEqual(R._restoredFitBgFailure(far), null);
  assert.ok(Math.abs(far.fitResult.backgroundStale.pct - 0.2) < 1e-9, 'beyond: stale, sized ' + far.fitResult.backgroundStale.pct);
  // the stored background CURVE is not evidence: a garbage curve with a good envelope reloads current
  const garbage = fitWith(peakRec()); garbage.fitResult.bgIntensity = garbage.fitResult.be.map(() => 12345);
  assert.strictEqual(R._restoredFitBgFailure(garbage), null); assert.ok(agreesToday(garbage.fitResult));
  // no envelope / no stored points: peaks-only, plain message
  const noEnv = fitWith(peakRec()); delete noEnv.fitResult.fittedY;
  assert.match(R._restoredFitBgFailure(noEnv) || '', /saved without its fitted envelope/);
  const noBe = fitWith(peakRec()); delete noBe.fitResult.be;
  assert.match(R._restoredFitBgFailure(noBe) || '', /saved without the energies it was fitted on/);
  const short = fitWith(peakRec()); short.fitResult.fittedY.pop();
  assert.match(R._restoredFitBgFailure(short) || '', /envelope and the energies it was fitted on have different lengths/);
  const off = fitWith(peakRec()); off.fitResult.be = off.fitResult.be.map((v, k) => v + 0.013 * k);
  assert.match(R._restoredFitBgFailure(off) || '', /not points of its raw data/);
  // the charge correction changed after the fit: the same samples at a constant offset — compared in today's frame
  const shifted = fitWith(peakRec()); shifted.fitResult.be = shifted.fitResult.be.map(v => v + 0.05);
  { const inten = R._recordBackground(peakRec()).rawY;   // what the fit saw: its subtracted counts + its background
    shifted.fitResult.bgSubtracted = inten.map(v => v - 7); shifted.fitResult.bgIntensity = inten.map(() => 7); }
  shifted.peaks = G.map(p => ({ ...p }));            // the peaks moved with the correction (they are today's)
  const fy = shifted.fitResult.fittedY.slice();
  assert.strictEqual(R._restoredFitBgFailure(shifted), null, 'a charge shift after the fit: compared on the same samples');
  assert.ok(agreesToday(shifted.fitResult)); assert.deepStrictEqual(shifted.fitResult.fittedY, fy);
  // on a uniform grid every run of samples is a constant offset: without the counts it saw, not resolved
  const blind = fitWith(peakRec()); blind.fitResult.be = blind.fitResult.be.map(v => v + 0.05); delete blind.fitResult.rmse;
  assert.match(R._restoredFitBgFailure(blind) || '', /cannot be told apart/);
});

// ── Codex impl round 18 ──
// a record with a fit of `peaks` made against its own background (as test 12's fitWith)
function fitWith(rec, peaks = [{ id: 1, name: 'g', shape: 'Gaussian', center: 285.5, fwhm: 1.0, amplitude: 300 }]) {
  const { be, bg, rawY } = R._recordBackground(rec);
  const model = R.evalAllPeaks(be, peaks), fittedY = Array.from(bg).map((v, i) => v + model[i]);
  const rmse = Math.sqrt(rawY.reduce((a, v, i) => a + (v - fittedY[i]) ** 2, 0) / rawY.length);
  return { ...rec, peaks, fitResult: { uploadFull: true, be: be.slice(), fittedY, rmse, bgIntensity: be.map(() => 0) } };
}
test('restore: a charge shift of whole grid steps is pinned by the fit\'s record, not by the exact match it makes', () => {
  // the fit saw samples i..; the correction then moved by one step (0.1 eV), so the
  // stored energies now coincide EXACTLY with the next samples — the wrong ones
  const G = [{ id: 1, name: 'g', shape: 'GL', glMix: 30, center: 285.5, fwhm: 1.0, amplitude: 300 }];
  for (const steps of [1, 2, -1]) {
    const rec = peakRec({ peaks: G.map(p => ({ ...p })) });
    const { be, bg, rawY } = R._recordBackground(rec);
    const model = R.evalAllPeaks(be, rec.peaks), fittedY = Array.from(bg).map((v, i) => v + model[i]);
    const rmse = Math.sqrt(rawY.reduce((a, v, i) => a + (v - fittedY[i]) ** 2, 0) / rawY.length);
    rec.fitResult = { uploadFull: true, be: be.slice(), fittedY, rmse, bgIntensity: be.map(() => 0) };
    const d = 0.1 * steps;                                  // updateChargeCorrection: ccShift += d, peaks and fields −= d
    rec.ccShift = d; rec.peaks.forEach(p => { p.center -= d; });
    rec.ui = { ...rec.ui, roiMin: String(+rec.ui.roiMin - d), roiMax: String(+rec.ui.roiMax - d) };
    assert.strictEqual(R._restoredFitBgFailure(rec), null, steps + ' step(s)');
    assert.ok(agreesToday(rec.fitResult), steps + ' step(s): the same background, on the same samples');
    assert.deepStrictEqual(rec.fitResult.bgSubtracted.map((v, i) => v + rec.fitResult.bgIntensity[i]), rawY, 'the samples the fit saw');
  }
});

// ── Codex impl round 19 ──
test('restore: the RMSE pins the samples before the 6-significant-figure counts a project save keeps', () => {
  // counts exactly a broad Gaussian of 1e6: rounded to 6 significant figures they are all 1000000
  const rawBE = [], rawIntensity = [];
  const G = [{ id: 1, name: 'g', shape: 'Gaussian', center: 280.004, fwhm: 10, amplitude: 1e6 }];
  for (let i = 0; i < 10; i++) rawBE.push(280 + 0.001 * i);
  const model = R.evalAllPeaks(rawBE, G); rawIntensity.push(...model);
  const rec = peakRec({ rawBE, rawIntensity, peaks: G, ui: { ...peakRec().ui, bgType: 'none', roiMin: '280', roiMax: '280.003' } });
  const { be, rawY } = R._recordBackground(rec);
  assert.strictEqual(be.length, 4);
  rec.fitResult = { uploadFull: true, be: be.map(v => Math.round(v * 1e4) / 1e4), fittedY: rawY.slice(), rmse: 0,
                    bgIntensity: be.map(() => 0), bgSubtracted: rawY.map(v => Number(v.toPrecision(6))) };
  assert.strictEqual(R._restoredFitBgFailure(rec), null);
  assert.ok(agreesToday(rec.fitResult), 'the samples the fit saw: ' + rec.fitResult.be);
  assert.deepStrictEqual(rec.fitResult.be, be);
});

test('restore: after a charge shift the samples are matched at one offset in order, however the record interleaves them', () => {
  for (const order of ['as is', 'reversed']) {
    let rawBE = [0, 9, 1, 9, 2, 9, 3, 9, 4, 9, 5].map(v => 280 + v);
    let rawIntensity = rawBE.map((x, i) => 100 + 1000 * Math.exp(-((x - 282.5) ** 2)) + (i % 2 ? 7 : 0));
    if (order === 'reversed') { rawBE = rawBE.slice().reverse(); rawIntensity = rawIntensity.slice().reverse(); }
    const G = [{ id: 1, name: 'g', shape: 'Gaussian', center: 282.5, fwhm: 1.5, amplitude: 1000 }];
    const rec = peakRec({ rawBE, rawIntensity, peaks: G.map(p => ({ ...p })), ui: { ...peakRec().ui, bgType: 'none', roiMin: '281', roiMax: '284' } });
    const { be, rawY } = R._recordBackground(rec);
    const model = R.evalAllPeaks(be, rec.peaks);
    rec.fitResult = { uploadFull: true, be: be.slice(), fittedY: model, bgIntensity: be.map(() => 0),
                      rmse: Math.sqrt(rawY.reduce((a, v, i) => a + (v - model[i]) ** 2, 0) / rawY.length) };
    const d = 0.5;
    rec.ccShift = d; rec.peaks.forEach(p => { p.center -= d; });
    rec.ui = { ...rec.ui, roiMin: String(281 - d), roiMax: String(284 - d) };
    assert.strictEqual(R._restoredFitBgFailure(rec), null, order);
    assert.ok(agreesToday(rec.fitResult), order + ': the same samples');
    assert.deepStrictEqual(rec.fitResult.bgSubtracted, rawY.map(v => v - 0), order);
  }
});

// ── Codex impl round 20 ──
// a record fitted on its ROI with `peaks` over background none, RMSE and (optionally) 6-sig-fig counts as a project keeps them
function fittedNone(rawBE, rawIntensity, peaks, roiMin, roiMax, { counts = false, key = false } = {}) {
  const rec = peakRec({ rawBE, rawIntensity, peaks: peaks.map(p => ({ ...p })), ui: { ...peakRec().ui, bgType: 'none', roiMin: String(roiMin), roiMax: String(roiMax) } });
  const { be, rawY } = R._recordBackground(rec);
  const fy = R.evalAllPeaks(be, rec.peaks);
  rec.fitResult = { uploadFull: true, be: be.slice(), fittedY: fy, bgIntensity: be.map(() => 0),
                    rmse: Math.sqrt(rawY.reduce((a, v, i) => a + (v - fy[i]) ** 2, 0) / rawY.length) };
  if (counts) { rec.fitResult.bgSubtracted = rawY.map(v => Number(v.toPrecision(6))); rec.fitResult.bgIntensity = be.map(() => 0); }
  if (key) rec.fitResult.startsModelKey = R._startsRecordKey(rec);
  return { rec, be, rawY };
}
const shiftAfter = (rec, d) => {                            // updateChargeCorrection: ccShift += d; peaks and fields −= d
  rec.ccShift = (rec.ccShift || 0) + d; rec.peaks.forEach(p => { p.center -= d; });
  rec.ui = { ...rec.ui, roiMin: String(+rec.ui.roiMin - d), roiMax: String(+rec.ui.roiMax - d) };
};
const r4be = rec => { rec.fitResult.be = rec.fitResult.be.map(v => Math.round(v * 1e4) / 1e4); };   // a project save

test('restore: samples the record cannot tell apart are refused, not guessed — and a model key removes the offset guess', () => {
  // two runs of samples whose counts differ by rounding: the RMSE cannot choose between them
  const rawBE = [0, 1, 2, 3, 10, 11, 12, 13].map(v => 280 + v);
  const G = [{ id: 1, name: 'g', shape: 'Gaussian', center: 281.5, fwhm: 2, amplitude: 100, fixCenter: true }];
  const base = [1, -2, 3, -4].map((r, k) => 10000 + R.evalAllPeaks([280 + k], G)[0] + r);
  const rawIntensity = base.concat(base.map((v, k) => v + [0, 1, -1, -1][k] * 2 ** -39));
  const a = fittedNone(rawBE, rawIntensity, G, 280, 283.5);
  shiftAfter(a.rec, 0);                                     // keyless, no change: still two readings at different offsets
  assert.match(R._restoredFitBgFailure(a.rec) || '', /cannot be told apart/);
  const b = fittedNone(rawBE, rawIntensity, G, 280, 283.5, { key: true });
  assert.strictEqual(R._restoredFitBgFailure(b.rec), null, 'the key gives the offset: one reading');
  assert.deepStrictEqual(b.rec.fitResult.bgSubtracted.slice(), b.rawY, 'its own samples');
});

test('restore: two samples one rounded energy fits are both tried; the counts a project keeps choose', () => {
  const rawBE = [0, 1.00001, 1.00002, 2.00002, 3.00002, 4.00002];
  const G = [{ id: 1, name: 'g', shape: 'Gaussian', center: 2, fwhm: 2, amplitude: 100 }];
  const rawIntensity = R.evalAllPeaks(rawBE, G);
  const f = fittedNone(rawBE, rawIntensity, G, 1.000015, 3.1, { counts: true });
  assert.strictEqual(f.be.length, 3);
  shiftAfter(f.rec, 0.5); r4be(f.rec);
  assert.strictEqual(R._restoredFitBgFailure(f.rec), null);
  assert.ok(agreesToday(f.rec.fitResult), 'the samples it was fitted on');
  assert.deepStrictEqual(f.rec.fitResult.bgSubtracted.slice(), f.rawY);
});

test('restore: a project\'s rounded energies admit the offset the samples share, not one pinned to the first', () => {
  for (const rev of [false, true]) {
    let rawBE = [0.00004, 1.00006, 2.00004, 3.00006, 4.00004, 5.00006];
    const G = [{ id: 1, name: 'g', shape: 'Gaussian', center: 2.5, fwhm: 2, amplitude: 100 }];
    let rawIntensity = R.evalAllPeaks(rawBE, G).map(v => v + 5);
    if (rev) { rawBE = rawBE.slice().reverse(); rawIntensity = rawIntensity.slice().reverse(); }
    const f = fittedNone(rawBE, rawIntensity, G, 1, 4.1);
    shiftAfter(f.rec, 0.5); r4be(f.rec);
    assert.strictEqual(R._restoredFitBgFailure(f.rec), null, 'reversed ' + rev);
    assert.deepStrictEqual(f.rec.fitResult.bgSubtracted.slice(), f.rawY, 'reversed ' + rev);
  }
});

// ── Codex impl round 21 ──
test('restore: a restored charge-shifted fit survives the next save and load (its energies carry their frame)', () => {
  const rawBE = [0, 1, 2, 3, 4, 5].map(v => 280 + v);
  const G = [{ id: 1, name: 'g', shape: 'Gaussian', center: 282.5, fwhm: 2, amplitude: 100 }];
  const f = fittedNone(rawBE, R.evalAllPeaks(rawBE, G).map(v => v + 3), G, 281, 284, { key: true });
  shiftAfter(f.rec, 0.5); r4be(f.rec);
  assert.strictEqual(R._restoredFitBgFailure(f.rec), null, 'first load');
  assert.ok(agreesToday(f.rec.fitResult));
  assert.strictEqual(f.rec.fitResult.beShift, 0.5, 'its energies are now in today\'s frame');
  const again = JSON.parse(JSON.stringify(f.rec)); r4be(again);           // saved as a project, loaded again
  assert.strictEqual(R._restoredFitBgFailure(again), null, 'second load');
  assert.ok(agreesToday(again.fitResult));
  assert.deepStrictEqual(again.fitResult.bgSubtracted.slice(), f.rawY);
});

test('restore: a fit made before the full-precision upload is reconstructed where the server evaluated it (4 dp)', () => {
  const rawBE = Array.from({ length: 11 }, (_, i) => 280.00004 + 0.1 * i);
  const G = [{ id: 1, name: 'g', shape: 'Gaussian', center: 280.5, fwhm: 0.2, amplitude: 1000, fixCenter: true }];
  const rawIntensity = rawBE.map(x => 100 + R.evalAllPeaks([Number(x.toFixed(4))], G)[0] + 2);
  for (const keyed of [true, false]) {
    for (const bgType of ['none', 'manual']) {
      const rec = peakRec({ rawBE, rawIntensity, peaks: G.map(p => ({ ...p })), manualAnchors: [{ x: 280, y: 100 }, { x: 281.5, y: 100 }],
                            ui: { ...peakRec().ui, bgType, roiMin: '', roiMax: '' } });
      const { be, bg, rawY } = R._recordBackground(rec);
      const server = R.evalAllPeaks(be.map(v => Number(v.toFixed(4))), rec.peaks);   // the old upload's energies
      const fy = Array.from(bg).map((v, i) => v + server[i]);
      rec.fitResult = { be: be.map(v => Math.round(v * 1e4) / 1e4), fittedY: fy, bgIntensity: be.map(() => 0),
                        rmse: Math.sqrt(rawY.reduce((a, v, i) => a + (v - fy[i]) ** 2, 0) / rawY.length) };
      if (keyed) rec.fitResult.startsModelKey = R._startsRecordKey(rec);
      assert.strictEqual(R._restoredFitBgFailure(rec), null, `${bgType} keyed ${keyed}`);
      assert.ok(agreesToday(rec.fitResult), `${bgType} keyed ${keyed}: an unchanged background`);
    }
  }
  // no key, and the charge correction moved after the fit by a fraction of a 4-dp step: the
  // fit's frame is not known to better than the upload's rounding (≤ 1e-4 eV). Codex impl
  // round 22: an allowance for that hid genuine changes; without one the reconstruction's
  // own uncertainty can only read as a DIFFERENCE — stale, never wrongly current
  const rec = peakRec({ rawBE, rawIntensity, peaks: G.map(p => ({ ...p })), ui: { ...peakRec().ui, bgType: 'none', roiMin: '', roiMax: '' } });
  const { be, rawY } = R._recordBackground(rec);
  const fy = R.evalAllPeaks(be.map(v => Number(v.toFixed(4))), rec.peaks);
  rec.fitResult = { be: be.map(v => Math.round(v * 1e4) / 1e4), fittedY: fy, bgIntensity: be.map(() => 0),
                    rmse: Math.sqrt(rawY.reduce((a, v, i) => a + (v - fy[i]) ** 2, 0) / rawY.length) };
  rec.ccShift = 0.033337; rec.peaks.forEach(p => { p.center -= 0.033337; });
  assert.strictEqual(R._restoredFitBgFailure(rec), null, 'keyless, shifted: reloaded');
  assert.ok(rec.fitResult.backgroundStale, 'keyless, shifted: not confirmed current');
  // unmoved: the old upload's energies are reproduced exactly, so an unchanged background is
  // current and a change of 0.2 % of the background's scale at a steep flank is a difference
  const still = peakRec({ rawBE, rawIntensity, peaks: G.map(p => ({ ...p })), ui: { ...peakRec().ui, bgType: 'manual', roiMin: '', roiMax: '' },
                          manualAnchors: [{ x: 280, y: 100 }, { x: 281.5, y: 100 }] });
  const sb = R._recordBackground(still), sm = R.evalAllPeaks(sb.be.map(v => Number(v.toFixed(4))), still.peaks);
  const sfy = Array.from(sb.bg).map((v, i) => v + sm[i] + (i === 4 ? 0.2 : 0));     // 0.2 counts off at a steep flank (half maximum)
  still.fitResult = { be: sb.be.map(v => Math.round(v * 1e4) / 1e4), fittedY: sfy, bgIntensity: sb.be.map(() => 0),
                      rmse: Math.sqrt(sb.rawY.reduce((a, v, i) => a + (v - sfy[i]) ** 2, 0) / sb.rawY.length) };
  assert.strictEqual(R._restoredFitBgFailure(still), null);
  assert.ok(still.fitResult.backgroundStale, 'unmoved: the difference is seen');
});

test('restore: the RMSE bound covers the sums of squares (a large window of large counts)', () => {
  const n = 16384, I = 171337899239733.8, B = 94231556951999.66, P = 65942324525676.664;
  const rawBE = Array.from({ length: n }, (_, i) => i), rawIntensity = rawBE.map(() => I);
  const G = [{ id: 1, name: 'g', shape: 'Gaussian', center: 8192, fwhm: 1e16, amplitude: P, fixCenter: true, fixFwhm: true }];
  const rec = peakRec({ rawBE, rawIntensity, peaks: G, manualAnchors: [{ x: 0, y: B }, { x: n - 1, y: B }],
                        ui: { ...peakRec().ui, bgType: 'manual', roiMin: '', roiMax: '' } });
  const { be, bg } = R._recordBackground(rec);
  const m = R.evalAllPeaks(be, G), fy = Array.from(bg).map((v, i) => v + m[i]);
  const server = rawIntensity.map((v, i) => (v - bg[i]) - m[i]);                 // the server's residuals
  rec.fitResult = { uploadFull: true, be: be.slice(), fittedY: fy, bgIntensity: be.map(() => 0),
                    rmse: Math.sqrt(server.reduce((a, v) => a + v * v, 0) / n) };
  assert.strictEqual(R._restoredFitBgFailure(rec), null);
});

test('restore: a power of ten rounded to 6 significant figures came from a one-sided interval', () => {
  // two runs with the same counts but one 999.996 where the fit's has 1000: the 6-figure record separates them
  const rawBE = [0, 1, 2, 3, 4, 10, 11, 12, 13, 14].map(v => 280 + v);
  const c = [62.5, 500, 1000, 500, 62.5], d = [62.5, 500, 999.996, 500, 62.5];
  const rec = peakRec({ rawBE, rawIntensity: c.concat(d), peaks: [], ui: { ...peakRec().ui, bgType: 'none', roiMin: '280', roiMax: '284' } });
  rec.fitResult = { uploadFull: true, be: [280, 281, 282, 283, 284], fittedY: c.slice(), rmse: 0,
                    bgSubtracted: c.map(v => Number(v.toPrecision(6))), bgIntensity: [0, 0, 0, 0, 0] };
  assert.strictEqual(R._restoredFitBgFailure(rec), null);
  assert.deepStrictEqual(rec.fitResult.be.slice(), [280, 281, 282, 283, 284], 'the run it was fitted on');
  assert.deepStrictEqual(rec.fitResult.bgSubtracted.map((v, i) => v + rec.fitResult.bgIntensity[i]), c, 'and its counts');
});

// ── Codex impl round 22 ──
test('restore: the stored counts choose before any cap on the readings the RMSE leaves', () => {
  const c = [62.5, 500, 1000, 500, 62.5], other = [62.5, 500, 999.999, 500, 62.5];
  const rawBE = [], rawIntensity = [];
  for (let r = 0; r < 65; r++) for (let k = 0; k < 5; k++) { rawBE.push(280 + 10 * r + k); rawIntensity.push((r ? other : c)[k]); }
  const rec = peakRec({ rawBE, rawIntensity, peaks: [], ui: { ...peakRec().ui, bgType: 'none', roiMin: '280', roiMax: '284' } });
  rec.fitResult = { uploadFull: true, be: [280, 281, 282, 283, 284], fittedY: c.slice(), rmse: 0,
                    bgSubtracted: c.slice(), bgIntensity: [0, 0, 0, 0, 0] };
  assert.strictEqual(R._restoredFitBgFailure(rec), null, '64 other runs meet the RMSE; the counts single out the fit\'s');
  assert.deepStrictEqual(rec.fitResult.be.slice(), [280, 281, 282, 283, 284]);
});

test('restore: a genuine background change is not hidden by the reconstruction (no allowance)', () => {
  const rawBE = Array.from({ length: 101 }, (_, i) => 280 + 0.1 * i);
  const G = [{ id: 1, name: 'g', shape: 'Gaussian', center: 285, fwhm: 1, amplitude: 1e5 }];
  const rawIntensity = rawBE.map(x => 1000 + R.evalAllPeaks([Number(x.toFixed(4))], G)[0]);
  const rec = peakRec({ rawBE, rawIntensity, peaks: G.map(p => ({ ...p })), ui: { ...peakRec().ui, bgType: 'manual', roiMin: '', roiMax: '' },
                        manualAnchors: [{ x: 280, y: 1000 }, { x: 290, y: 1000 }] });
  const { be, bg, rawY } = R._recordBackground(rec);
  const fy = Array.from(bg).map((v, i) => v + R.evalAllPeaks([Number(be[i].toFixed(4))], rec.peaks)[0]);
  rec.fitResult = { be: be.map(v => Math.round(v * 1e4) / 1e4), fittedY: fy, bgIntensity: be.map(() => 0),
                    rmse: Math.sqrt(rawY.reduce((a, v, i) => a + (v - fy[i]) ** 2, 0) / rawY.length) };
  shiftAfter(rec, 0.1);
  rec.manualAnchors = [{ x: 279.9, y: 1000 }, { x: 285.0, y: 1000 }, { x: 285.2, y: 1008 }, { x: 285.4, y: 1000 }, { x: 289.9, y: 1000 }];
  assert.strictEqual(R._restoredFitBgFailure(rec), null);
  assert.ok(rec.fitResult.backgroundStale && rec.fitResult.backgroundStale.pct > 0.5, 'the 8-count bump is a difference: ' + JSON.stringify(rec.fitResult.backgroundStale));
});

test('restore: an older LOCAL-engine fit used the page\'s own energies (no 4-dp upload)', () => {
  const rawBE = Array.from({ length: 11 }, (_, i) => 280.00004 + 0.1 * i);
  const G = [{ id: 1, name: 'g', shape: 'Gaussian', center: 280.5, fwhm: 0.2, amplitude: 1000 }];
  const rawIntensity = R.evalAllPeaks(rawBE, G).map(v => v + 103);
  const rec = peakRec({ rawBE, rawIntensity, peaks: G.map(p => ({ ...p })), ui: { ...peakRec().ui, bgType: 'manual', roiMin: '', roiMax: '' },
                        manualAnchors: [{ x: 280, y: 100 }, { x: 281.5, y: 100 }] });
  const { be, bg, rawY } = R._recordBackground(rec);
  const fy = Array.from(bg).map((v, i) => v + R.evalAllPeaks(be, rec.peaks)[i]);
  rec.fitResult = { engine: 'local', be: be.slice(), fittedY: fy, bgIntensity: be.map(() => 0),
                    rmse: Math.sqrt(rawY.reduce((a, v, i) => a + (v - fy[i]) ** 2, 0) / rawY.length) };
  assert.strictEqual(R._restoredFitBgFailure(rec), null);
  assert.ok(agreesToday(rec.fitResult));
});

test('restore: the RMSE bound covers a background and components that cancel', () => {
  const rawBE = Array.from({ length: 8 }, (_, i) => 280 + i), rawIntensity = rawBE.map(() => 0.1);
  const G = [{ id: 1, name: 'g', shape: 'Gaussian', center: 283.5, fwhm: 1e16, amplitude: 1e15, fixCenter: true, fixFwhm: true }];
  const rec = peakRec({ rawBE, rawIntensity, peaks: G, ui: { ...peakRec().ui, bgType: 'manual', roiMin: '', roiMax: '' },
                        manualAnchors: [{ x: 280, y: -1e15 }, { x: 287, y: -1e15 }] });
  const { be, bg } = R._recordBackground(rec);
  const m = R.evalAllPeaks(be, G), fy = Array.from(bg).map((v, i) => v + m[i]);
  const server = rawIntensity.map((v, i) => (v - bg[i]) - m[i]);
  rec.fitResult = { uploadFull: true, be: be.slice(), fittedY: fy, bgIntensity: be.map(() => 0),
                    rmse: Math.sqrt(server.reduce((a, v) => a + v * v, 0) / server.length) };
  assert.strictEqual(R._restoredFitBgFailure(rec), null);
});

test('restore: "the record\'s peaks are the fit\'s" compares centres in one charge frame', () => {
  const rawBE = [0, 1, 2, 3, 4, 5].map(v => 280 + v);
  const G = [{ id: 1, name: 'g', shape: 'Gaussian', center: 282.5, fwhm: 1, amplitude: 100 }];
  const f = fittedNone(rawBE, R.evalAllPeaks(rawBE, G).map(v => v + 10), G, 281, 284, { key: true });
  assert.ok(R._restoredModelIsFit(f.rec));
  shiftAfter(f.rec, 0.5); shiftAfter(f.rec, -0.2);          // two charge changes after the fit
  assert.ok(R._restoredModelIsFit(f.rec), 'the same peaks, in today\'s frame');
  f.rec.peaks[0].amplitude = 200;
  assert.ok(!R._restoredModelIsFit(f.rec), 'an edit is not the fit');
});

// ── Codex impl round 23 ──
test('restore: a keyless older fit whose charge correction moved is never confirmed current', () => {
  // its reconstruction is uncertain by up to 1e-4 eV, which can cancel a genuine change (a
  // background built as 100 + (M_fitted − M_reconstructed) read "current")
  const rawBE = Array.from({ length: 11 }, (_, i) => 280.00004 + 0.1 * i);
  const G = [{ id: 1, name: 'g', shape: 'Gaussian', center: 280.5, fwhm: 0.2, amplitude: 1000 }];
  const rawIntensity = rawBE.map(x => 100 + R.evalAllPeaks([Number(x.toFixed(4))], G)[0]);
  const rec = peakRec({ rawBE, rawIntensity, peaks: G.map(p => ({ ...p })), ui: { ...peakRec().ui, bgType: 'manual', roiMin: '', roiMax: '' },
                        manualAnchors: [{ x: 280, y: 100 }, { x: 281.5, y: 100 }] });
  const { be, bg, rawY } = R._recordBackground(rec);
  const mOld = R.evalAllPeaks(be.map(v => Number(v.toFixed(4))), rec.peaks);
  const fy = Array.from(bg).map((v, i) => v + mOld[i]);
  rec.fitResult = { be: be.map(v => Math.round(v * 1e4) / 1e4), fittedY: fy, bgIntensity: be.map(() => 0),
                    rmse: Math.sqrt(rawY.reduce((a, v, i) => a + (v - fy[i]) ** 2, 0) / rawY.length) };
  rec.ccShift = 0.033337; rec.peaks.forEach(p => { p.center -= 0.033337; });
  // the cancelling background: what the reconstruction gets wrong, added to the anchors
  const corr = be.map(v => v - 0.033337);
  const mEst = R.evalAllPeaks(corr.map(v => Number(v.toFixed(4))), rec.peaks);
  rec.manualAnchors = corr.map((x, i) => ({ x, y: 100 + mOld[i] - mEst[i] }));
  assert.strictEqual(R._restoredFitBgFailure(rec), null);
  assert.ok(rec.fitResult.backgroundStale && rec.fitResult.backgroundStale.unconfirmed, 'stale, unconfirmed — never current');
  const again = JSON.parse(JSON.stringify(rec)); again.fitResult.be = again.fitResult.be.map(v => Math.round(v * 1e4) / 1e4);
  assert.strictEqual(R._restoredFitBgFailure(again), null);
  assert.ok(again.fitResult.backgroundStale && again.fitResult.backgroundStale.unconfirmed, 'and on the next load');
  // owner 2026-10-05: ANY keyless fit — even one whose stored energies show no move (a change
  // below the save's rounding leaves no trace) — is never confirmed current
  const unmoved = peakRec({ rawBE, rawIntensity, peaks: G.map(p => ({ ...p })), ui: { ...peakRec().ui, bgType: 'manual', roiMin: '', roiMax: '' },
                            manualAnchors: [{ x: 280, y: 100 }, { x: 281.5, y: 100 }] });
  unmoved.fitResult = { be: be.map(v => Math.round(v * 1e4) / 1e4), fittedY: fy.slice(), bgIntensity: be.map(() => 0),
                        rmse: Math.sqrt(rawY.reduce((a, v, i) => a + (v - fy[i]) ** 2, 0) / rawY.length) };
  assert.strictEqual(R._restoredFitBgFailure(unmoved), null);
  assert.ok(unmoved.fitResult.backgroundStale && unmoved.fitResult.backgroundStale.unconfirmed && unmoved.fitResult.backgroundStale.matches,
            'unmoved and matching as far as can be told: still not confirmed current');
  const keyed = JSON.parse(JSON.stringify(unmoved)); delete keyed.fitResult.backgroundStale;
  keyed.fitResult.be = be.map(v => Math.round(v * 1e4) / 1e4); keyed.fitResult.startsModelKey = R._startsRecordKey(keyed);
  assert.strictEqual(R._restoredFitBgFailure(keyed), null);
  assert.strictEqual(keyed.fitResult.backgroundStale, undefined, 'its fit key gives the frame: current');
});

test('restore: repeated samples are one branch, and the stored counts prune as the search goes', () => {
  const c = [62.5, 500, 1000, 500, 62.5];
  const rawBE = [280, 280.5, 281, 281.5, 282], rawIntensity = c.slice();
  for (let k = 0; k < 5; k++) for (let r = 0; r < 5; r++) { rawBE.push(290 + 0.5 * k); rawIntensity.push(k === 2 ? 999.999 : c[k]); }
  const rec = peakRec({ rawBE, rawIntensity, peaks: [], ui: { ...peakRec().ui, bgType: 'none', roiMin: '280', roiMax: '282' } });
  rec.fitResult = { uploadFull: true, be: [280, 280.5, 281, 281.5, 282], fittedY: c.slice(), rmse: 0,
                    bgSubtracted: c.slice(), bgIntensity: [0, 0, 0, 0, 0] };
  assert.strictEqual(R._restoredFitBgFailure(rec), null, 'not "too many": duplicates do not multiply the search');
  assert.deepStrictEqual(rec.fitResult.be.slice(), [280, 280.5, 281, 281.5, 282]);
  // and without stored counts: a record whose every sample is repeated four times
  const be4 = [], i4 = [];
  for (let k = 0; k < 12; k++) for (let r = 0; r < 4; r++) { be4.push(280 + k); i4.push(100 + 10 * k); }
  const rep = peakRec({ rawBE: be4, rawIntensity: i4, peaks: [], ui: { ...peakRec().ui, bgType: 'none', roiMin: '', roiMax: '' } });
  rep.fitResult = { uploadFull: true, be: be4.slice(), fittedY: i4.slice(), rmse: 0, bgIntensity: be4.map(() => 0) };
  assert.strictEqual(R._restoredFitBgFailure(rep), null, 'equal samples are one reading, found once');
  // another run whose samples are each repeated six times, its centre count a hair off, and no
  // stored counts: two readings the RMSE cannot separate — said as such, not "too many"
  const c7 = [10, 62.5, 500, 1000, 500, 62.5, 10], e7 = [280, 280.5, 281, 281.5, 282, 282.5, 283];
  const c6BE = e7.slice(), c6I = c7.slice();
  for (let k = 0; k < 7; k++) for (let r = 0; r < 6; r++) { c6BE.push(290 + 0.5 * k); c6I.push(k === 3 ? 999.999 : c7[k]); }
  const six = peakRec({ rawBE: c6BE, rawIntensity: c6I, peaks: [], ui: { ...peakRec().ui, bgType: 'none', roiMin: '280', roiMax: '283' } });
  six.fitResult = { be: e7.slice(), fittedY: c7.slice(), rmse: 0, bgIntensity: e7.map(() => 0) };   // an older upload: its RMSE is known to 0.005
  assert.match(R._restoredFitBgFailure(six) || '', /equally well/, 'equal samples did not multiply the search into "too many"');
});

// ── Codex impl round 24 ──
test('restore: branches that cannot be completed are never expanded (unequal near-duplicates, an excluding last count)', () => {
  const G = [{ id: 1, name: 'g', shape: 'Gaussian', center: 280.85, fwhm: 1, amplitude: 1000 }];
  const own = Array.from({ length: 18 }, (_, i) => 280 + 0.1 * i);
  const c = own.map(x => 10000 + R.evalAllPeaks([x], G)[0]);
  const rawBE = own.slice(), rawIntensity = c.slice();
  for (let i = 0; i < 18; i++) {
    const tail = i === 17;
    rawBE.push(300 + 0.1 * i, 300 + 0.1 * i); rawIntensity.push(c[i] + (tail ? 1 : 0.001), c[i] + (tail ? 1 : 0.002));
  }
  const rec = peakRec({ rawBE, rawIntensity, peaks: [], ui: { ...peakRec().ui, bgType: 'none', roiMin: '280', roiMax: '281.75' } });
  rec.fitResult = { be: own.map(v => Math.round(v * 1e4) / 1e4), fittedY: c.slice(), rmse: 0,
                    bgSubtracted: c.map(v => Number(v.toPrecision(6))), bgIntensity: c.map(() => 0) };
  assert.strictEqual(R._restoredFitBgFailure(rec), null, 'not "too many": 2^17 dead branches are never grown');
  assert.deepStrictEqual(rec.fitResult.be.slice(), own);
});

test('restore: a full-precision fit\'s RMSE carries no allowance for the old 2-dp upload', () => {
  const G = [{ id: 1, name: 'g', shape: 'Gaussian', center: 280.5, fwhm: 0.5, amplitude: 1000 }];
  const own = Array.from({ length: 11 }, (_, i) => 280 + 0.1 * i), c = R.evalAllPeaks(own, G).map(v => v + 10000);
  const rawBE = [279.99999].concat(own), rawIntensity = [c[0] + 0.004].concat(c);   // a sample the save's 4 dp cannot tell from 280
  const rec = peakRec({ rawBE, rawIntensity, peaks: G.map(p => ({ ...p })), ui: { ...peakRec().ui, bgType: 'none', roiMin: '280', roiMax: '281' } });
  rec.fitResult = { uploadFull: true, be: own.map(v => Math.round(v * 1e4) / 1e4), fittedY: c.slice(), rmse: 5e-13, bgIntensity: own.map(() => 0) };
  rec.fitResult.startsModelKey = R._startsRecordKey(rec);
  assert.strictEqual(R._restoredFitBgFailure(rec), null);
  assert.deepStrictEqual(rec.fitResult.be.slice(), own, 'the RMSE (to its arithmetic) singles out the fit\'s samples');
});

// ── Codex impl round 25 ──
test('restore: choices that can never share one offset are explored once (a dead-state memo), not until the cap', () => {
  const G = [{ id: 1, name: 'g', shape: 'Gaussian', center: 280.95, fwhm: 1, amplitude: 1000 }];
  const own = Array.from({ length: 20 }, (_, i) => Math.round((280 + 0.1 * i) * 10) / 10);
  const c = own.map(x => 10000 + R.evalAllPeaks([x], G)[0]);
  const rawBE = own.slice(), rawIntensity = c.slice();
  rawBE.push(300); rawIntensity.push(c[0]);
  for (let i = 1; i <= 18; i++) { const x = 300 + 0.1 * i; rawBE.push(x + 0.00008, x + 0.00009); rawIntensity.push(c[i], c[i]); }
  rawBE.push(301.9 - 0.00008); rawIntensity.push(c[19]);
  const rec = peakRec({ rawBE, rawIntensity, peaks: [], ui: { ...peakRec().ui, bgType: 'none', roiMin: '280', roiMax: '281.95' } });
  rec.fitResult = { be: own.slice(), fittedY: c.slice(), rmse: 0,
                    bgSubtracted: c.map(v => Number(v.toPrecision(6))), bgIntensity: c.map(() => 0) };
  assert.strictEqual(R._restoredFitBgFailure(rec), null, 'not "too many": the middle choices narrow the offset past the last point');
  assert.deepStrictEqual(rec.fitResult.be.slice(), own);
});

// ── Codex impl round 26 ──
test('restore: a reading whose RMSE is too SMALL does not mark the shared rest of the search dead', () => {
  const G = [{ id: 1, name: 'g', shape: 'Gaussian', center: 280.5, fwhm: 0.5, amplitude: 1e6 }];
  const own = Array.from({ length: 11 }, (_, i) => Math.round((280 + 0.1 * i) * 10) / 10);
  const fy = R.evalAllPeaks(own, G);
  const c = fy.map((v, i) => v + (i % 2 ? 0.01 : -0.01));
  const rawBE = [279.99999].concat(own), rawIntensity = [fy[0]].concat(c);   // the other first sample: residual exactly 0
  const rec = peakRec({ rawBE, rawIntensity, peaks: G.map(p => ({ ...p })), ui: { ...peakRec().ui, bgType: 'none', roiMin: '280', roiMax: '281' } });
  rec.fitResult = { uploadFull: true, be: own.slice(), fittedY: fy.slice(), bgIntensity: own.map(() => 0),
                    rmse: Math.sqrt(c.reduce((a, v, i) => a + (v - fy[i]) ** 2, 0) / c.length),
                    bgSubtracted: c.map(v => Number(v.toPrecision(6))) };
  rec.fitResult.bgIntensity = own.map(() => 0);
  rec.fitResult.startsModelKey = R._startsRecordKey(rec);
  assert.strictEqual(R._restoredFitBgFailure(rec), null, 'the fit\'s own samples are found');
  assert.deepStrictEqual(rec.fitResult.be.slice(), own);
  assert.strictEqual(rec.fitResult.backgroundStale, undefined, 'current');
});

// ── Codex impl round 27 ──
test('restore: branches whose every completion has too SMALL an RMSE are cut, not grown to the cap', () => {
  const G = [{ id: 1, name: 'g', shape: 'Gaussian', center: 280.85, fwhm: 1, amplitude: 1000 }];
  const own = Array.from({ length: 18 }, (_, i) => Math.round((280 + 0.1 * i) * 10) / 10);
  const fy = own.map(x => 12345.6 + R.evalAllPeaks([x], G)[0]);
  const c = fy.map((v, i) => v + (i % 2 ? 0.02 : -0.02));
  const rawBE = own.slice(), rawIntensity = c.slice();
  for (let i = 0; i < 18; i++) { rawBE.push(300 + 0.1 * i, 300 + 0.1 * i); rawIntensity.push(fy[i], fy[i] + 0.001); }
  const rec = peakRec({ rawBE, rawIntensity, peaks: [], ui: { ...peakRec().ui, bgType: 'none', roiMin: '280', roiMax: '281.75' } });
  rec.fitResult = { be: own.slice(), fittedY: fy.slice(), rmse: Math.sqrt(c.reduce((a, v, i) => a + (v - fy[i]) ** 2, 0) / c.length),
                    bgSubtracted: c.map(v => Number(v.toPrecision(6))), bgIntensity: c.map(() => 0) };
  assert.strictEqual(R._restoredFitBgFailure(rec), null, 'not "too many": 2^18 readings, all too small, are cut at the root');
  assert.deepStrictEqual(rec.fitResult.be.slice(), own);
  // and with no stored counts at all: the RMSE alone has to cut them
  const bare = JSON.parse(JSON.stringify(rec));
  bare.fitResult = { be: own.slice(), fittedY: fy.slice(), rmse: rec.fitResult.rmse, bgIntensity: own.map(() => 0) };
  assert.strictEqual(R._restoredFitBgFailure(bare), null, 'RMSE only');
  assert.deepStrictEqual(bare.fitResult.be.slice(), own);
});

test('restore: an unrelated large sample does not widen the RMSE tolerance', () => {
  const G = [{ id: 1, name: 'g', shape: 'Gaussian', center: 280.5, fwhm: 0.5, amplitude: 1000 }];
  const own = Array.from({ length: 11 }, (_, i) => Math.round((280 + 0.1 * i) * 10) / 10);
  const fy = R.evalAllPeaks(own, G);
  const rawBE = [279.99999].concat(own, [300]), rawIntensity = [fy[0] + 1e-7].concat(fy, [1e8]);
  const rec = peakRec({ rawBE, rawIntensity, peaks: G.map(p => ({ ...p })), ui: { ...peakRec().ui, bgType: 'none', roiMin: '280', roiMax: '281' } });
  rec.fitResult = { uploadFull: true, be: own.slice(), fittedY: fy.slice(), rmse: 0, bgIntensity: own.map(() => 0),
                    bgSubtracted: fy.map(v => Number(v.toPrecision(6))) };
  rec.fitResult.startsModelKey = R._startsRecordKey(rec);
  assert.strictEqual(R._restoredFitBgFailure(rec), null);
  assert.deepStrictEqual(rec.fitResult.be.slice(), own);
  assert.strictEqual(rec.fitResult.backgroundStale, undefined, 'current');
});

// ── Codex impl round 28 ──
test('restore: the verdict\'s tolerance is the reading\'s own — an unusable large neighbour does not loosen it', () => {
  const G = [{ id: 1, name: 'g', shape: 'Gaussian', center: 280.5, fwhm: 0.5, amplitude: 1000 }];
  const own = Array.from({ length: 11 }, (_, i) => Math.round((280 + 0.1 * i) * 10) / 10);
  const fy = R.evalAllPeaks(own, G);
  // a million-count neighbour its residual rules out, and a near-copy of the first point
  const rawBE = [279.99998, 279.99999].concat(own), rawIntensity = [1e6, fy[0] + 1e-9].concat(fy);
  const rec = peakRec({ rawBE, rawIntensity, peaks: G.map(p => ({ ...p })), ui: { ...peakRec().ui, bgType: 'none', roiMin: '280', roiMax: '281' } });
  rec.fitResult = { uploadFull: true, be: own.slice(), fittedY: fy.slice(), rmse: 0, bgIntensity: own.map(() => 0) };   // a spectrum file before fitCounts
  rec.fitResult.startsModelKey = R._startsRecordKey(rec);
  assert.strictEqual(R._restoredFitBgFailure(rec), null);
  assert.deepStrictEqual(rec.fitResult.be.slice(), own);
  assert.strictEqual(rec.fitResult.backgroundStale, undefined, 'current');
});

// ── Codex impl round 29 ──
test('restore: a spectrum file\'s points and counts are exact — a simple value is not read as rounded', () => {
  const G = [{ id: 1, name: 'g', shape: 'Gaussian', center: 281, fwhm: 1, amplitude: 1000 }];
  const own = [280, 280.5, 281, 281.5, 282], c = [62.5, 500, 1000, 500, 62.5001];
  const fy = R.evalAllPeaks(own, G);
  for (const [nbE, nb, label] of [[279.99999, 62.5, 'a neighbour 1e-5 eV away'], [279.99999, 62.5000058823438, 'a neighbour whose count rounds like the fit\'s'],
                                  [279.99999999999994, 62.5, 'a neighbour one ulp away (round 30: compared exactly in the same frame)']]) {
    const rawBE = [nbE].concat(own), rawIntensity = [nb].concat(c);
    const rec = peakRec({ rawBE, rawIntensity, peaks: G.map(p => ({ ...p })), ui: { ...peakRec().ui, bgType: 'none', roiMin: '280', roiMax: '282' } });
    rec.fitResult = { uploadFull: true, beExact: true, be: own.slice(), fittedY: fy.slice(), bgIntensity: own.map(() => 0),
                      bgSubtracted: c.slice(),                       // fitCounts − background, exact
                      rmse: Math.sqrt(c.reduce((a, v, i) => a + (v - fy[i]) ** 2, 0) / c.length) };
    rec.fitResult.startsModelKey = R._startsRecordKey(rec);
    assert.strictEqual(R._restoredFitBgFailure(rec), null, label);
    assert.deepStrictEqual(rec.fitResult.be.slice(), own, label);
    assert.strictEqual(rec.fitResult.backgroundStale, undefined, label + ': current');
  }
});

test('restore: the search\'s RMSE window is widened by the summation\'s own rounding (a reading at the boundary)', () => {
  const be = [280, 280.1, 280.2, 280.3, 280.4, 280.5];
  const rec = { rawBE: be, rawIntensity: [-87809067.2660619, 33063639.28131759, -94206236.07002199, 95697211.52074635, -9742030.92046082, 60016250.517219305],
                fitResult: { fittedY: [19819426.350295544, 70811345.56792676, -98611670.26683688, -54457667.19058156, -80704812.00702488, -6804285.477846861],
                             rmse: 86675042.30314377 } };
  const g = R._restoredFitGrid(rec, be, 0, 89769475.55784136, 0);
  assert.ok(!g.fail, 'the sole reading, accepted by the verdict, is not pruned: ' + g.fail);
});

test('restore: what the subtraction cannot resolve is not a difference — a zero background, the save\'s 4-dp energies', () => {
  // the server's own evaluation of a component differs from the page's in the last bits
  const none = fitWith(peakRec({ ui: { ...peakRec().ui, bgType: 'none' } }));
  none.fitResult.fittedY = none.fitResult.fittedY.map((v, i) => v + (i % 3 - 1) * 4e-14);
  assert.strictEqual(R._restoredFitBgFailure(none), null);
  assert.ok(agreesToday(none.fitResult), 'a zero background recovered as rounding noise is zero');
  // a project save rounds the energies to 4 dp and keeps the envelope at full precision
  const rawBE = [], rawIntensity = [];
  for (let i = 0; i <= 120; i++) { const x = 280.00004 + i / 8; rawBE.push(x); rawIntensity.push(100 + 1e4 * Math.exp(-4 * Math.LN2 * (x - 285) ** 2)); }
  const sharp = [{ id: 1, name: 's', shape: 'Gaussian', center: 285, fwhm: 1, amplitude: 1e4 }];
  const r = peakRec({ rawBE, rawIntensity, ui: { ...peakRec().ui, bgType: 'linear', endpointAvg: '1', roiMin: '', roiMax: '' } });
  const f = (() => { const { be, bg, rawY } = R._recordBackground(r); const m = R.evalAllPeaks(be, sharp);
    const fy = Array.from(bg).map((v, i) => v + m[i]);
    return { ...r, peaks: sharp, fitResult: { uploadFull: true, be: be.map(v => Math.round(v * 1e4) / 1e4), fittedY: fy, bgIntensity: be.map(() => 0),
             rmse: Math.sqrt(rawY.reduce((a, v, i) => a + (v - fy[i]) ** 2, 0) / rawY.length) } }; })();
  assert.strictEqual(R._restoredFitBgFailure(f), null);
  assert.ok(agreesToday(f.fitResult), 'the components are evaluated at the samples, not at the rounded energies');
});

test('restore: the components are the fit\'s own (its key) — an edit after the fit does not leak into its background', () => {
  const G = [{ id: 1, name: 'g', shape: 'Gaussian', center: 285.5, fwhm: 1.0, amplitude: 300 }];
  const keyed = fitWith(peakRec());
  keyed.peaks = G.map(p => ({ ...p })); keyed.fitResult.startsModelKey = R._startsRecordKey({ ...keyed, peaks: G });
  keyed.peaks[0].amplitude = 900;                          // edited after the fit, then saved
  assert.strictEqual(R._restoredFitBgFailure(keyed), null);
  assert.ok(agreesToday(keyed.fitResult), 'its background reconstructed from the fit\'s own components');
  const unkeyed = fitWith(peakRec()); unkeyed.peaks = G.map(p => ({ ...p, amplitude: 900 }));
  assert.strictEqual(R._restoredFitBgFailure(unkeyed), null);
  assert.ok(unkeyed.fitResult.backgroundStale, 'without a key the saved peaks are all there is: stale');
  assert.ok(unkeyed.fitResult.restoredKey, 'and the restore stamps what it judged, for the next save');
});

test('restore: a Voigt fitted before A03 cannot be shown as fitted — stale whatever its background, and its evidence goes', () => {
  const V = [{ id: 1, name: 'v', shape: 'Voigt', center: 285.5, fwhm: 1.0, amplitude: 300, support: { supported: true, fitKey: 'k' },
               _backendParams: { gl_ratio: { value: 0.3 } } }];
  const rec = peakRec({ peaks: V });
  const { be, bg } = R._recordBackground(rec);
  const m = R.evalAllPeaks(be, [{ ...V[0], shape: 'GL', glMix: 30 }]);           // what the server fitted
  const fy = Array.from(bg).map((v, i) => v + m[i]), rawY = R._recordBackground(rec).rawY;
  rec.fitResult = { uploadFull: true, be: be.slice(), fittedY: fy, bgIntensity: be.map(() => 0), starts: { ran: true }, certificateMove: { id: 1, ev: 2 },
                    chosenAlternative: { fromChi: 2, toChi: 1 }, rmse: Math.sqrt(rawY.reduce((a, v, i) => a + (v - fy[i]) ** 2, 0) / rawY.length) };
  assert.strictEqual(R._restoredFitBgFailure(rec), null);
  assert.ok(agreesToday(rec.fitResult), 'its background is today\'s');
  assert.deepStrictEqual(rec.fitResult.voigtStale, [{ name: 'v', eta: 0.3 }]);
  assert.ok(R._restoredStale(rec.fitResult));
  assert.ok(rec.fitResult.starts === null && rec.fitResult.certificateMove === null && rec.fitResult.chosenAlternative === null && rec.peaks[0].support === null);
  const post = peakRec({ peaks: [{ ...V[0], _backendParams: { gl_ratio: { value: 0.5 } } }] });   // A03 and after: fitted at 0.5
  const { be: b2, bg: g2 } = R._recordBackground(post), m2 = R.evalAllPeaks(b2, post.peaks);
  const fy2 = Array.from(g2).map((v, i) => v + m2[i]), raw2 = R._recordBackground(post).rawY;
  post.fitResult = { uploadFull: true, be: b2.slice(), fittedY: fy2, bgIntensity: b2.map(() => 0),
                     rmse: Math.sqrt(raw2.reduce((a, v, i) => a + (v - fy2[i]) ** 2, 0) / raw2.length) };
  post.fitResult.startsModelKey = R._startsRecordKey(post);   // a recent fit carries its key
  assert.strictEqual(R._restoredFitBgFailure(post), null);
  assert.ok(!R._restoredStale(post.fitResult), 'a Voigt fitted at 0.5 is drawn as fitted');
});

test('BG_RESTORE_REL is fit_equality.py\'s SAME_MINIMUM_REL', () => {
  const { execFileSync } = require('node:child_process');
  const PY = ['/Users/skyefortier/xps-app/venv/bin/python3', path.join(__dirname, '../../venv/bin/python3')].find(p => fs.existsSync(p)) || 'python3';
  const v = Number(execFileSync(PY, ['-c', 'import sys; sys.path[:0] = [".", "tests"]; import fit_equality; print(repr(fit_equality.SAME_MINIMUM_REL))'], { encoding: 'utf8', cwd: path.join(__dirname, '../..') }));
  assert.ok(Math.abs(v - R.BG_RESTORE_REL) <= 1e-15 * v, v + ' vs ' + R.BG_RESTORE_REL);
});

// ── Codex impl round 4 ──
test('linear: ends at one energy with different intensities have no line through them — not converged, the server\'s words', () => {
  const E = [3, 2, 1, 1, 0], I = [20, 25, 10, 30, 5];
  const want = 'Linear background not converged: its two end points are at the same energy with different intensities, so no line passes through both.';
  const lin = B.computeBackgroundCore(E, I, { bgType: 'linear', endpointAvg: '1', bgStart: '1', bgEnd: '1' });
  assert.strictEqual(lin.converged, false);
  assert.strictEqual(lin.failure, want, 'fitting._line_through raises the same text (tests/test_background_certificate.py)');
  assert.throws(() => R._computeBackgroundForSource(E, I, { bgType: 'linear', endpointAvg: '1', bgStart: '1', bgEnd: '1' }), e => R._isBgNotConverged(e));
  // manual with fewer than two anchors is the line through the ROI's ends: the same rule
  assert.throws(() => R._computeBackgroundForSource([1, 1], [10, 30], { bgType: 'manual' }, []), e => e.message === want);
  assert.strictEqual(R._computeBackgroundForSource([1, 1], [10, 10], { bgType: 'manual' }, []).converged, true);
  assert.strictEqual(B.computeBackgroundCore([1, 1], [10, 10], { bgType: 'linear', endpointAvg: '1', bgStart: '', bgEnd: '' }).converged, true);
});

test('restore: a fit whose raw data are missing or incomplete is not restored (the check needs them)', () => {
  const ok = peakRec(); const { be, bg } = R._recordBackground(ok);
  const withFit = over => ({ ...peakRec(), peaks: [], fitResult: { uploadFull: true, be: be.slice(), fittedY: Array.from(bg), bgIntensity: Array.from(bg),
    bgSubtracted: R._recordBackground(ok).rawY.map((v, i) => v - bg[i]) }, ...over });
  assert.strictEqual(R._restoredFitBgFailure(withFit({})), null);
  for (const over of [{ rawBE: [281], rawIntensity: [100] }, { rawBE: [] }, { rawBE: undefined }, { rawIntensity: undefined },
                      { rawIntensity: [1, 2, 3] }]) {
    assert.match(R._restoredFitBgFailure(withFit(over)) || '', /raw data are missing or incomplete/, JSON.stringify(Object.keys(over)));
  }
});

// ── Codex impl round 5: an explicit background must exist (the server's words, tests/test_background_certificate.py) ──
test('explicit backgrounds: conflicting anchors and non-finite results are not converged, page = server words', () => {
  const ANCHOR = 'Manual background not converged: two anchors are at the same energy with different intensities, so no curve passes through both.';
  const FINITE = 'Linear background not converged: it is not a finite number at every point (the arithmetic overflowed or an input is not finite).';
  const E = [0, 1, 2, 3, 4, 5], I = [10, 12, 40, 30, 22, 20];
  const conflict = [{ x: 0, y: 0 }, { x: 2, y: 1 }, { x: 2, y: 20 }, { x: 5, y: 0 }];
  assert.throws(() => R._computeBackgroundForSource(E, I, { bgType: 'manual' }, conflict), e => R._isBgNotConverged(e) && e.message === ANCHOR);
  const agree = [{ x: 0, y: 0 }, { x: 2, y: 1 }, { x: 2, y: 1 }, { x: 5, y: 0 }];
  assert.strictEqual(R._computeBackgroundForSource(E, I, { bgType: 'manual' }, agree).converged, true);
  // since round 11 the line is evaluated exactly: these used to overflow and now give
  // their true values; only an EXTRAPOLATION past the largest double is not finite
  for (const [x, y, want] of [[[0, 1e-309], [0, 1], [0, 1]], [[0, 1, 2], [1e308, 1, -1e308], [1e308, 0, -1e308]]]) {
    const bg = B.computeBackgroundCore(x, y, { bgType: 'linear', endpointAvg: '1', bgStart: '', bgEnd: '' });
    assert.strictEqual(bg.converged, true); assert.deepStrictEqual(Array.from(bg), want);
  }
  const ex = B.computeBackgroundCore([0, 1, 2], [-1.7e308, 1.7e308, 0], { bgType: 'linear', endpointAvg: '1', bgStart: '0', bgEnd: '1' });
  assert.strictEqual(ex.converged, false); assert.strictEqual(ex.failure, FINITE);
  // anchors near the largest double: the exact interpolation is a convex combination of
  // finite values, so it is finite and correct (it overflowed before round 10)
  const huge = R._computeBackgroundForSource([0, 5e-301, 5], [1, 2, 3], { bgType: 'manual' }, [{ x: 0, y: -1.7e308 }, { x: 1e-300, y: 1.7e308 }, { x: 5, y: 1 }]);
  assert.strictEqual(huge.converged, true); assert.deepStrictEqual(Array.from(huge), [-1.7e308, 0, 1]);
});

test('manual: an anchor that is not a pair of finite numbers is not converged (the server\'s words)', () => {
  const W = 'Manual background not converged: an anchor is not a pair of finite numbers.';
  const E = [0, 1, 2, 3, 4, 5], I = [10, 12, 40, 30, 22, 20];
  for (const bad of [{ x: NaN, y: 1 }, { x: 2, y: Infinity }, { x: '2', y: 1 }, { x: 2, y: null }, { x: true, y: 1 }, null]) {
    assert.throws(() => R._computeBackgroundForSource(E, I, { bgType: 'manual' }, [{ x: 0, y: 0 }, bad, { x: 5, y: 0 }]),
      e => R._isBgNotConverged(e) && e.message === W, JSON.stringify(bad));
  }
});

// ── Codex impl round 6 ──
function serverWords(cases) {
  const { execFileSync } = require('node:child_process');
  const PY = ['/Users/skyefortier/xps-app/venv/bin/python3', path.join(__dirname, '../../venv/bin/python3')].find(p => fs.existsSync(p)) || 'python3';
  const out = execFileSync(PY, ['-c', `import json, sys, math
sys.path.insert(0, ${JSON.stringify(path.join(__dirname, '../..'))})
import numpy as np, fitting
res = []
for c in json.load(sys.stdin):
    x, y = np.array(c['x'], float), np.array(c['y'], float)
    try:
        if c['m'] == 'manual':
            fitting.manual_anchor_background(x, c['anchors'], fitting._span(y)) if len(c['anchors']) >= 2 else fitting.linear_background(x, y, n_avg=c.get('n', 1))
        elif c['m'] == 'linear':
            fitting.linear_background(x, y, n_avg=c.get('n', 1))
        else:
            fitting._region_in_order(x, c['m'])          # run_fit's order: the region, then the window
            fitting.compute_background(x, y, c['m'], n_avg=c.get('n', 1))
        res.append(None)
    except fitting.BackgroundNotConverged as e:
        res.append(str(e))
print(json.dumps(res))`], { input: JSON.stringify(cases), encoding: 'utf8', cwd: path.join(__dirname, '../..') });
  return JSON.parse(out);
}

test('every refusal: page = server, verdict and words (incl. order, overflow, anchors, the residual %)', () => {
  const cases = [
    { m: 'shirley', x: [0, 2, 1, 3], y: [10, 40, 12, 20] }, { m: 'tougaard', x: [3, 1, 2, 0], y: [20, 12, 40, 10] },
    { m: 'smart', x: [0, 2, 1, 3], y: [10, 40, 12, 20] }, { m: 'shirley_linear', x: [0, 1, 2, 3, 4], y: [1e308, -1e308, 1e308, -1e308, 1e308] },
    { m: 'shirley', x: [0, 1, 2, 3], y: [2, 3, 10, 13] }, { m: 'smart', x: [0, 1, 2, 3, 4], y: [10, 5, 5, 17, 20] },
    { m: 'shirley', x: [0, 1, 1, 2, 3, 4, 5], y: [10, 12, 14, 40, 30, 22, 20] }, { m: 'shirley', x: [0, 1, 2], y: [1, NaN, 3] },
    { m: 'linear', x: [1, 1], y: [10, 30] }, { m: 'linear', x: [0, 1e-309], y: [0, 1] },
    { m: 'manual', x: [0, 1e-309], y: [0, 1], anchors: [] },
    { m: 'linear', x: [1e20, 290, 289, 280], y: [1e20, 70, 80, 50] }, { m: 'manual', x: [-1e20, 280, 290, 300], y: [1e20, 50, 60, 1], anchors: [] },
    // round 12: Tougaard whose kernel arithmetic overflows (refused), and large data (certified)
    { m: 'tougaard', x: [0, 1, 9.999999999999999e79, 1e80], y: [0, 1e200, 1e145, 1e200] }, { m: 'tougaard', x: [280, 285, 290], y: [1e20, 2e20, 50] },
    // round 13: near-cancelling Tougaard (the rounding bound refuses), Shirley family on 1e12 +- 8 (the exact check refuses)
    { m: 'tougaard', x: [280, 281, 282, 283], y: [200, 300, 0.73, 300] }, { m: 'shirley', x: [0, 1, 2, 3], y: [1e12, 1e12 + 4, 1e12 + 8, 1e12 + 2] },
    { m: 'smart', x: [3, 2, 1, 0], y: [1e12 + 2, 1e12 + 8, 1e12 + 4, 1e12] }, { m: 'shirley_linear', x: [0, 1, 2, 3], y: [1e12, 1e12 + 4, 1e12 + 8, 1e12 + 2] },
    { m: 'tougaard', x: [280, 281, 282, 283], y: [2, 3, 0.0072794, 3] }, { m: 'shirley', x: [280, 281, 282, 283], y: [1e-200, 5e-200, 4e-200, 2e-200] },
    { m: 'smart_exp', x: [283, 282, 281, 280], y: [2e-200, 4e-200, 5e-200, 1e-200] },
    // round 14: the bound at tiny scale (normalised frame), the zero-loss branch with exact means
    { m: 'tougaard', x: [280, 281, 282, 283], y: [2e-110, 3e-110, 1.3e-112, 3e-110] }, { m: 'tougaard', x: [283, 282, 281, 280], y: [3e-118, 1.15e-120, 3e-118, 2e-118] },
    { m: 'tougaard', n: 2, x: [281, 280, 280, 280, 280, 280, 280, 280], y: [1e12 + 2 ** -13, 1e12, 1e12 + 4, 1e12 + 8, 1e12 + 4, 1e12 + 8, 1e12, 1e12] },
    { m: 'tougaard', n: 2, x: [280, 281, 282, 283, 284, 285, 286, 287], y: [1, 1, 1, 1, 1, 1, 1, 1.0000000000000002] },
    { m: 'tougaard', x: [0, 1, 2, 3], y: [7, 7, 7, 7] }, { m: 'tougaard', x: [280, 281, 282, 283], y: [3e-307, 4.5e-307, 2.7e-307, 4.5e-307] },
    // round 15: computed D = 0 with a cancelling high-edge sum; a rescale that rounds to zero
    { m: 'tougaard', n: 3, x: [333, 280 + 2 ** -44, 280, 245.21875, 245.21875, 245.21875, 245.21875, 245.21875, 245.21875, 245.21875, 245.21875, 245.21875], y: [146.21875000000003, 162.78125, 75, 128, 128, 128, 128, 128, 128, 128, 128, 128] },
    { m: 'tougaard', n: 2, x: [55.4022790912908, 55.4022790912908, 32, 32, 31.999999999999996, 31.999999999999996, 24, 24], y: [12, 12.000000000000002, 15.999999999999998, 12, 12, 0.2988604543545996, 12, 12] },
    { m: 'tougaard', n: 3, x: [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0], y: [1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0].map(v => v * 2 ** -1074) },
    { m: 'tougaard', n: 2, x: [1e6, 1e6 - 1e-3, 1e6 - 2e-3, 30, 25, 20, 15, 1, 0], y: [1, 1, 1, 400, 1000, 400, 1, 1, 1 + 2 ** -52] },
    // round 16: an exact curve's rounding outside the predicate (1e12 counts, span 1-2)
    { m: 'linear', x: [280, 281, 283], y: [1e12, 1e12 + 2, 1e12 + 1] }, { m: 'linear', x: [3, 1, 0], y: [1e12 + 1, 1e12, 1e12] },
    { m: 'manual', x: [0, 1, 3], y: [1e12, 1e12, 1e12 + 1], anchors: [[0, 1e12], [3, 1e12 + 1]] }, { m: 'manual', x: [0, 1, 3], y: [1e12, 1e12, 1e12 + 1], anchors: [] },
    { m: 'manual', x: [0, 1, 2, 3, 4, 5], y: [10, 12, 40, 30, 22, 20], anchors: [[0, 0], [2, 1], [2, 20], [5, 0]] },
  ];
  const S = serverWords(cases);
  cases.forEach((c, k) => {
    const settings = { bgType: c.m, endpointAvg: String(c.n || 1), bgStart: '', bgEnd: '' };
    if (c.m === 'manual') settings.anchors = c.anchors.map(([x, y]) => ({ x, y }));
    const bg = R.computeBackgroundCore(c.x, c.y, settings);
    assert.strictEqual(bg.converged ? null : bg.failure, S[k], `case ${k} (${c.m})`);
  });
  assert.ok(S.filter(v => v).length >= 9, 'the cases are mostly refusals');
  assert.ok(S.filter(v => v === null).length >= 4, 'and the exact lines converge on both sides');
  assert.strictEqual(S[cases.findIndex(c => c.m === 'tougaard' && c.y[0] === 3e-307)], null, 'the normalised bound certifies the 1.5e-307 case');
  // the residual text: Python's %.3g, value for value
  const { execFileSync } = require('node:child_process');
  // incl. exact binary ties (12.25, 1.125, 0.125·10^k): fitting._fmt3 rounds them half up, as toExponential does
  const vals = [1.234e-5, 0.0001234, 1e-4, 0.001, 0.1, 1, 12.5, 99.95, 100, 123.4, 999.6, 1234, 2.5e-7, 5.555e-3, 0.00995, 4.2e12,
                12.25, 1.125, 0.125, 12.75, 0.0625, 1.375, 99.96, 0.000099996, 9.995, 2.675, 1e-10, 3.14159e-8, 6.02e23];
  const PY = ['/Users/skyefortier/xps-app/venv/bin/python3', path.join(__dirname, '../../venv/bin/python3')].find(p => fs.existsSync(p)) || 'python3';
  const py = JSON.parse(execFileSync(PY, ['-c', 'import json,sys; sys.path.insert(0, "."); import fitting; print(json.dumps([fitting._fmt3(v) for v in json.load(sys.stdin)]))'],
    { input: JSON.stringify(vals), encoding: 'utf8', cwd: path.join(__dirname, '../..') }));
  assert.deepStrictEqual(vals.map(R._fmt3), py);
  // the certificate's residual is written with it (a residual below 1e-4 % reads '1.23e-05' on both sides)
  assert.match(enclosingFunction(lines.findIndex(l => l.startsWith('function _bgExactShirleyCertificate('))).body, /_fmt3\(_bgRatToDouble\(100n \* maxNum, den \* SP\)\)/);
  // a lone anchor is checked too (it would otherwise fall back to the line silently)
  for (const lone of [[{ x: NaN, y: 1 }], [{ x: 2, y: null }], [{ x: true, y: 1 }], [null]])
    assert.throws(() => R._computeBackgroundForSource([0, 1, 2], [1, 2, 3], { bgType: 'manual' }, lone),
      e => e.message === 'Manual background not converged: an anchor is not a pair of finite numbers.', JSON.stringify(lone));
});

test('a stack aligns raw counts to the fit grid point for point, also on an unsorted record', () => {
  const fn = name => enclosingFunction(lines.findIndex(l => l.startsWith('function ' + name + '('))).body;
  const align = new Function(fn('_roiSelect') + '\n' + fn('_alignRawToFitBe') + '\nreturn _alignRawToFitBe;')();
  // incl. Codex round 7's rounding collisions: an excluded point 5e-5 / 1e-5 eV from a selected one
  for (const [rawBE, mn, mx] of [[[5, 1, 4, 0, 3, 2], '1', '4'], [[10, 6, 8, 5, 4, 3, 2, 1, 0], '', '4'], [[0, 1, 2, 3, 4, 5], '1', '3'],
                                 [[5, 4, 3, 2, 1, 0], '', ''], [[0.99996, 1, 2, 3, 4, 5, 6], '1', '6'], [[3.00001, 3, 2, 1, 0], '', '3'],
                                 [[5.123456, 1.123456, 4.123456, 0.123456, 3.123456, 2.123456], '1', '4.5']]) {   // saved grid != exact
    const rawIntensity = rawBE.map(e => 10 * e + 1);
    const sel = R._roiSelect(rawBE, rawIntensity, 0, mn, mx);
    const rec = { rawBE, rawIntensity, ccShift: 0, ui: { roiMin: mn, roiMax: mx } };
    assert.deepStrictEqual(align(rec, sel.be), sel.inten, JSON.stringify(rawBE));
    assert.deepStrictEqual(align(rec, sel.be.map(e => Math.round(e * 1e4) / 1e4)), sel.inten, 'as saved (4 dp)');
    // the ROI changed since the fit: an exact point-for-point match, never a rounded one
    assert.deepStrictEqual(align({ ...rec, ui: { roiMin: '', roiMax: '' } }, sel.be), sel.inten, 'exact match ' + JSON.stringify(rawBE));
  }
});

test('an integral background on an unsorted fitted region is not converged; a one-point manual fallback is its point (round 7)', () => {
  const E = [5, 0, 1, 2, 3, -1], I = [20, 10, 10, 40, 20, 10];
  for (const t of ['shirley', 'smart', 'smart_exp', 'tougaard', 'shirley_linear']) {
    const bg = R.computeBackgroundCore(E, I, { bgType: t, endpointAvg: '1', bgStart: '1', bgEnd: '3' });
    assert.strictEqual(bg.converged, false, t);
    assert.match(bg.failure, /the energies in the fitted region are not in order/, t);
  }
  assert.strictEqual(R.computeBackgroundCore(E, I, { bgType: 'linear', endpointAvg: '1', bgStart: '1', bgEnd: '3' }).converged, true, 'a line is affine in energy whatever the order');
  const one = R._computeBackgroundForSource([1], [20], { bgType: 'manual' }, []);
  assert.deepStrictEqual(Array.from(one), [20]);
});

test('manual: far and huge anchors give the exact piecewise-affine value, page = server (rounds 9-10)', () => {
  // np.interp's floating-point formula overflowed (±1e308) or cancelled to a finite, wrong 0
  // (-1e20); exact evaluation, rounded once, gives the line the anchors define
  // (data with a span: since round 16 each value's rounding is judged against the data's span)
  const E = Array.from({ length: 11 }, (_, i) => 280 + i), I = [50, 50, 60, 100, 500, 100, 60, 50, 50, 50, 50];
  const want = { a: E.map((_, i) => 80 + i), b: E.map((_, i) => 21 - i), c: E.map(() => 50) };
  const got = {
    a: R._computeBackgroundForSource(E, I, { bgType: 'manual' }, [{ x: -1e20, y: -1e20 }, { x: 300, y: 100 }]),
    b: R._computeBackgroundForSource(E, I, { bgType: 'manual' }, [{ x: -1e20, y: 1e20 }, { x: 300, y: 1 }]),
    c: R._computeBackgroundForSource(E, I, { bgType: 'manual' }, [{ x: -1e308, y: 0 }, { x: 1e308, y: 100 }]),
  };
  for (const k of ['a', 'b', 'c']) { assert.strictEqual(got[k].converged, true, k); assert.deepStrictEqual(Array.from(got[k]), want[k], k); }
  const S = serverWords([{ m: 'manual', x: E, y: I, anchors: [[-1e20, -1e20], [300, 100]] }]);
  assert.deepStrictEqual(S, [null], 'the server accepts it too (the values: manual_background_statement.test.js)');
});

test('linear (and manual without anchors) is the exact line, page = server, also beside a 1e20 end point (round 11)', () => {
  const E1 = [1e20, 290, 289, 288, 287, 286, 285, 284, 283, 282, 281, 280], I1 = [1e20, 70, 70, 80, 120, 500, 120, 80, 70, 70, 60, 50];
  const lin = R.computeBackgroundCore(E1, I1, { bgType: 'linear', endpointAvg: '1', bgStart: '', bgEnd: '' });
  assert.deepStrictEqual(Array.from(lin), [1e20, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50]);
  const E2 = [-1e20, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 300], I2 = [1e20, 50, 50, 60, 100, 500, 100, 60, 50, 50, 50, 50, 1];
  const man = R._computeBackgroundForSource(E2, I2, { bgType: 'manual' }, []);
  assert.deepStrictEqual(Array.from(man), [1e20, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 1]);
});
