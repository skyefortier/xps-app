// ROI past the data / peak centre outside the data (2026-09-25).
// WARN, NEVER REINTERPRET: the helpers report the window getROIData()
// already uses and write nothing back. Plan:
// docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md.
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
const NAMES = ['getCorrectedBE', 'getROIData', '_roiWindowStatus', '_roiHintFor', '_refreshRoiHint', '_centreOutsideData', '_outsideDataBadge', '_escAttr'];
const FP_UPLOAD_ROUND = v => +v.toFixed(4);   // uploadToBackend: energies to 4 dp
function makeEnv({ rawBE, ccShift = 0, roiMin, roiMax }) {
  const dom = { 'roi-min': { value: String(roiMin) }, 'roi-max': { value: String(roiMax) },
    'roi-hint': { textContent: '', className: 'roi-hint', style: { display: 'none' } } };
  const document = { getElementById: id => dom[id] || null };
  const state = { rawBE, rawIntensity: rawBE.map(() => 100), ccShift, peaks: [] };
  const fns = new Function('document', 'state', NAMES.map(extractFn).join('\n\n') + '\nreturn { ' + NAMES.join(', ') + ' };')(document, state);
  return { ...fns, dom, state };
}
const grid = (lo, hi, step) => Array.from({ length: Math.round((hi - lo) / step) + 1 }, (_, i) => +(lo + step * i).toFixed(6));
const DATA = grid(280, 295, 0.05);

test('an ROI inside the data: no hint', () => {
  const e = makeEnv({ rawBE: DATA, roiMin: 282, roiMax: 293 });
  const st = e._roiWindowStatus();
  assert.equal(st.state, 'ok');
  assert.equal(e._roiHintFor(st), null);
  e._refreshRoiHint(st);
  assert.equal(e.dom['roi-hint'].style.display, 'none');
});

test('an ROI past the data by more than one step: the quiet hint names the window actually used', () => {
  const e = makeEnv({ rawBE: DATA, roiMin: 270, roiMax: 320 });
  const st = e._roiWindowStatus();
  assert.equal(st.state, 'past');
  const h = e._roiHintFor(st);
  assert.equal(h.cls, '', 'quiet, not amber');
  assert.equal(h.text, 'ROI extends past your data — clipped to 280.00–295.00 eV.');
  e._refreshRoiHint(st);
  assert.equal(e.dom['roi-hint'].style.display, '');
  assert.equal(e.dom['roi-hint'].textContent, h.text);
});

test('one side past the data is enough; the window named is the selected data', () => {
  const e = makeEnv({ rawBE: DATA, roiMin: 283.2, roiMax: 300 });
  const st = e._roiWindowStatus();
  assert.equal(st.state, 'past');
  assert.equal(e._roiHintFor(st).text, 'ROI extends past your data — clipped to 283.20–295.00 eV.');
});

test('a sub-step overshoot (a toFixed(1) rounding of the data edge) is not "past the data"', () => {
  const e = makeEnv({ rawBE: grid(279.97, 295.03, 0.1), roiMin: 279.9, roiMax: 295.1 });   // 0.07 eV past each edge, step 0.1
  assert.equal(e._roiWindowStatus().state, 'ok');
});

test('min above max: amber, no data selected (getROIData selects nothing)', () => {
  const e = makeEnv({ rawBE: DATA, roiMin: 293, roiMax: 282 });
  const st = e._roiWindowStatus();
  assert.equal(st.state, 'inverted');
  assert.equal(e.getROIData().be.length, 0);
  assert.deepEqual(e._roiHintFor(st), { cls: 'amber', text: 'BE min is above BE max — no data is selected.' });
});

test('an ROI that misses the data entirely: amber, names the data range', () => {
  const e = makeEnv({ rawBE: DATA, roiMin: 700, roiMax: 740 });
  const st = e._roiWindowStatus();
  assert.equal(st.state, 'no-overlap');
  assert.deepEqual(e._roiHintFor(st), { cls: 'amber', text: 'ROI does not overlap your data (280.00–295.00 eV) — no data is selected.' });
});

test('empty fields mean the full range (as getROIData): no hint', () => {
  const e = makeEnv({ rawBE: DATA, roiMin: '', roiMax: '' });
  assert.equal(e._roiWindowStatus().state, 'ok');
});

test('the window is in the CORRECTED frame (raw − ccShift), as the fit and Find Peaks use it', () => {
  const e = makeEnv({ rawBE: DATA, ccShift: 1.5, roiMin: 278.5, roiMax: 293.5 });   // corrected data 278.5–293.5
  assert.equal(e._roiWindowStatus().state, 'ok');
  const e2 = makeEnv({ rawBE: DATA, ccShift: 1.5, roiMin: 280, roiMax: 295 });     // past the corrected top by 1.5 eV
  const st = e2._roiWindowStatus();
  assert.equal(st.state, 'past');
  assert.equal(e2._roiHintFor(st).text, 'ROI extends past your data — clipped to 280.00–293.50 eV.');
});

test('a descending acquisition behaves the same', () => {
  const e = makeEnv({ rawBE: DATA.slice().reverse(), roiMin: 270, roiMax: 320 });
  const st = e._roiWindowStatus();
  assert.equal(st.state, 'past');
  assert.equal(e._roiHintFor(st).text, 'ROI extends past your data — clipped to 280.00–295.00 eV.');
});

test('centre outside the SELECTED data is flagged; inside, at the edges, or with no data selected is not', () => {
  const e = makeEnv({ rawBE: DATA, roiMin: 282, roiMax: 293 });
  const st = e._roiWindowStatus();
  for (const [c, out] of [[287, false], [282, false], [293, false], [281.9, true], [293.05, true], [310, true]]) {
    assert.equal(e._centreOutsideData({ id: 1, center: c }, st), out, `centre ${c}`);
  }
  const eNone = makeEnv({ rawBE: DATA, roiMin: 700, roiMax: 740 });
  assert.equal(eNone._centreOutsideData({ id: 1, center: 310 }, eNone._roiWindowStatus()), false, 'no selected data: nothing to compare against (the ROI hint speaks instead)');
  const badge = e._outsideDataBadge({ id: 7, center: 310 }, st);
  assert.match(badge, /class="outside-data-badge" data-peak-id="7"/);
  assert.match(badge, /Centre 310\.00 eV lies outside the fitted data \(282\.00–293\.00 eV\)/);
  assert.match(badge, /Nothing has been moved/);
});

// WARN, NEVER REINTERPRET — structural guards on the new helpers
test('the helpers write nothing: no assignment to a field value, a peak or the fit state', () => {
  for (const name of ['_roiWindowStatus', '_roiHintFor', '_refreshRoiHint', '_centreOutsideData', '_outsideDataBadge', '_patchPeakCardsForCentre', '_refreshRoiAndCentreWarnings']) {
    const src = extractFn(name);
    assert.doesNotMatch(src, /\.value\s*=(?!=)/, `${name} assigns an input value`);
    assert.doesNotMatch(src, /\bp\.(center|fwhm|amplitude)\s*=(?!=)/, `${name} moves a peak`);
    assert.doesNotMatch(src, /state\.(peaks|fitResult|ccShift)\s*=(?!=)/, `${name} writes the fit state`);
    assert.doesNotMatch(src, /\b(pushUndo|updatePeakParam|renderPeakList|updatePlot)\(/, `${name} triggers an edit or a re-render`);
  }
});

test('the fit and Find Peaks still read the ROI exactly as before (getROIData / the two field values)', () => {
  const g = extractFn('getROIData');
  assert.match(g, /corrBE\[i\] >= roiMin && corrBE\[i\] <= roiMax/, 'inclusive filter unchanged');
  assert.match(html, /roi: \{ be_min: parseFloat\(document\.getElementById\('roi-min'\)\.value\),\s*\n\s*be_max: parseFloat\(document\.getElementById\('roi-max'\)\.value\) \}/, 'Find Peaks payload unchanged');
  const rp = extractFn('runPropagation');
  assert.match(rp, /const roiSt = _roiWindowStatus\(\);[^\n]*\n\s*const \{ be, inten \} = getROIData\(\);/, 'Batch Fit reads the status beside, not instead of, getROIData');
});

test('an unsupported component: the badge warns without reporting its suppressed centre', () => {
  const e = makeEnv({ rawBE: DATA, roiMin: 282, roiMax: 293 });
  const st = e._roiWindowStatus();
  const b = e._outsideDataBadge({ id: 3, center: 310 }, st, true);
  assert.doesNotMatch(b, /310/, 'the suppressed centre must not appear');
  assert.match(b, /Its centre lies outside the fitted data \(282\.00–293\.00 eV\)/);
});

// "One fix covers both" (plan §3): manual fit filters the corrected
// energies, then uploads them rounded to 4 dp; Find Peaks uploads the
// corrected energies rounded to 4 dp and the SERVER applies the same
// inclusive mask. The two selections are identical except for an energy
// within 5e-5 eV of an ROI edge, where rounding can move it across. Pinned
// both ways so the qualification stays true.
function serverMask(corr, lo, hi) { return corr.map(FP_UPLOAD_ROUND).filter(v => v >= lo && v <= hi); }
test('manual fit and Find Peaks select the same points whenever no energy lies within 5e-5 eV of an ROI edge', () => {
  for (const [lo, hi] of [[270, 320], [283.2, 300], [282, 293], [281.37, 291.83]]) {
    const e = makeEnv({ rawBE: DATA, roiMin: lo, roiMax: hi });
    const page = e.getROIData().be.map(FP_UPLOAD_ROUND);
    assert.deepStrictEqual(serverMask(DATA, lo, hi), page, `ROI ${lo}–${hi}`);
  }
});
test('…and can differ by one edge point, IN EITHER DIRECTION, when an energy lies within 5e-5 eV of an edge (pre-existing, logged, not changed)', () => {
  // rounding DROPS a point (Codex round 1)
  const raw = Array.from({ length: 21 }, (_, i) => 280.00004 + 0.1 * i);
  const e = makeEnv({ rawBE: raw, roiMin: 280.00002, roiMax: 282.1 });
  assert.equal(e.getROIData().be.length, 21);
  assert.equal(serverMask(raw, 280.00002, 282.1).length, 20, 'rounding 280.00004 to 280.0 moves it below the edge');
  // rounding ADDS a point, with an ordinary ROI (Codex round 2)
  const raw2 = Array.from({ length: 21 }, (_, i) => 279.99996 + 0.1 * i);
  const e2 = makeEnv({ rawBE: raw2, roiMin: 280, roiMax: 282.1 });
  assert.equal(e2.getROIData().be.length, 20);
  assert.equal(serverMask(raw2, 280, 282.1).length, 21, 'rounding 279.99996 to 280.0 moves it onto the edge');
  // …and a charge shift's float subtraction can produce such an energy from a clean grid (Codex round 2, run A)
  const raw3 = Array.from({ length: 21 }, (_, i) => +(280.1 + 0.1 * i).toFixed(1));
  const e3 = makeEnv({ rawBE: raw3, ccShift: 0.2, roiMin: 279.9, roiMax: 281.9 });
  const corr3 = raw3.map(b => b - 0.2);
  assert.equal(e3.getROIData().be.length, serverMask(corr3, 279.9, 281.9).length - 1, 'the corrected 281.90000000000003 is outside the page ROI and inside the server one');
});
