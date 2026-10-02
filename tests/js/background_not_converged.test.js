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
  const tip = v => html.match(new RegExp('<option value="' + v + '" data-tip="([^"]*)"'))[1];
  assert.match(tip('smart'), /raises net area by about 1 % on noisy data/);
  assert.match(tip('smart_exp'), /raises net area by about 1 % on noisy data/);
  assert.match(tip('smart_exp'), /plain Shirley carries its own bias at large steps/);
  assert.match(tip('shirley'), /its own net-area bias at large background steps/);
  assert.match(html, /<option value="shirley_linear" disabled hidden/, 'shirley_linear stays off the menu');
  assert.match(html, /id="bg-legacy-note"/, 'its notice stays');
});

// ── Codex impl round 3: the producers throw; the record path reads the record ──
function recordEnv() {
  const fn = name => enclosingFunction(lines.findIndex(l => new RegExp('^(async )?function ' + name + '\\(').test(l))).body;
  const src = require('./_page_background_source.js')({ manual: 'real' }) + '\n' +
    lines.find(l => l.startsWith('const LEGACY_ENDPOINT_AVG =')) + '\n' +
    ['manualAnchorBackground', '_roiSelect', '_computeBackgroundForSource', '_recordBackground',
     '_restoredFitBgFailure', '_dropRestoredFit'].map(fn).join('\n') +
    '\nconst _getManualAnchors = () => { throw new Error("the active tab is not read"); };' +
    '\nreturn { computeBackgroundCore, _certifiedBg, _bgOrFailure, _isBgNotConverged, _roiSelect, _computeBackgroundForSource, _recordBackground, _restoredFitBgFailure, _fmt3 };';
  return new Function(src)();
}
const R = recordEnv();
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

test('restore: kept only when the stored curve IS the certified one — no method exempt, non-numbers fail closed', () => {
  const fitWith = rec => { const { be, bg } = R._recordBackground(rec); return { ...rec, fitResult: { be: be.slice(), bgIntensity: Array.from(bg) } }; };
  for (const bgType of ['shirley', 'smart', 'tougaard', 'linear', 'none', 'manual']) {
    const base = peakRec({ ui: { ...peakRec().ui, bgType }, manualAnchors: [{ x: 282, y: 100 }, { x: 290, y: 140 }] });
    const rec = fitWith(base);
    assert.strictEqual(R._restoredFitBgFailure(rec), null, bgType + ': its own curve is restored');
    // a stale fit: the stored curve is the fit's, the settings changed after it
    const stale = fitWith(base); stale.ui = { ...stale.ui, bgType: bgType === 'none' ? 'linear' : 'none' };
    assert.match(R._restoredFitBgFailure(stale) || '', /is not the background its settings give now/, bgType + ': a changed method is refused, not exempt');
    if (bgType === 'manual') {
      const moved = fitWith(base); moved.manualAnchors = [{ x: 282, y: 100 }, { x: 290, y: 150 }];
      assert.match(R._restoredFitBgFailure(moved) || '', /is not the background/, 'moved anchors are refused');
    }
    for (const bad of [v => String(v), () => null, () => 'abc', () => undefined]) {
      const r = fitWith(base); r.fitResult.bgIntensity[3] = bad(r.fitResult.bgIntensity[3]);
      assert.match(R._restoredFitBgFailure(r) || '', /is not the background/, bgType + ': a non-number fails closed');
    }
  }
  const rounded = fitWith(peakRec()); rounded.fitResult.bgIntensity = rounded.fitResult.bgIntensity.map(v => Number(v.toPrecision(6)));
  assert.strictEqual(R._restoredFitBgFailure(rounded), null, 'as the save rounds it');
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
  const withFit = over => ({ ...peakRec(), fitResult: { be: be.slice(), bgIntensity: Array.from(bg) }, ...over });
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
            fitting.manual_anchor_background(x, c['anchors']) if len(c['anchors']) >= 2 else fitting.linear_background(x, y)
        elif c['m'] == 'linear':
            fitting.linear_background(x, y)
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
  const E = Array.from({ length: 11 }, (_, i) => 280 + i), I = E.map(() => 50);
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
