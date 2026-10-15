#!/usr/bin/env node
// Seal 1c step 8 (plan §10, "each measured on the committed fits"): what a student SEES change when the page reads a
// fit's RECORD instead of re-deriving it. ONE server reply per committed target — seal 1b's records (run v2, one
// clean commit, a46cd3f) — read two ways:
//   main   : the page as deployed (templates/index.html at `main`, its functions extracted verbatim): the fitted
//            values applied to the tab's own model by main's _applyBackendParams; chi-square formed as
//            chi2r x max(1, n - 3 x peaks); RMSE over the reply's residuals; R by main's _computeRFactor on the page's
//            background (seal 1b: bit-identical to the server's on 328 / 328); each component and its area by main's
//            evalPeakArray / _peakArea on the fit's grid;
//   record : what the sealed page shows — the reply's own statistics, curves and areas (the view, plan §7).
// No refit: optimiser jitter cannot enter (the same reply on both sides).
//
// Usage: node scripts/seal_1c_release_measure.js <records.jsonl> <tabs.json> <targets.json> <main index.html> [--json OUT]
'use strict';
const fs = require('fs');

const [recPath, tabsPath, targetsPath, mainPath] = process.argv.slice(2);
const jsonOut = process.argv.includes('--json') ? process.argv[process.argv.indexOf('--json') + 1] : null;
const lines = fs.readFileSync(mainPath, 'utf8').split('\n');
const fn = name => {
  const re = new RegExp('^(async )?function ' + name + '\\(');
  const s = lines.findIndex(l => re.test(l));
  if (s < 0) throw new Error('main has no function ' + name);
  let d = 0, seen = false;
  for (let i = s; i < lines.length; i++) {
    for (const c of lines[i]) { if (c === '{') { d++; seen = true; } else if (c === '}') d--; }
    if (seen && d === 0) return lines.slice(s, i + 1).join('\n');
  }
  throw new Error(name);
};
const NAMES = ['gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic', 'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS',
  '_laKernelHalf', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve',
  'dsgConvolved_array', 'evalPeakArray', '_migrateLineshapeAliases', '_arrMin', '_arrMax', '_applyBackendParams',
  '_npPairwiseSum', '_trapezoidArea', '_peakArea', '_computeRFactor'];
const main = new Function('state', 'getPeak', NAMES.map(fn).join('\n') +
  '\nreturn { evalPeakArray, _migrateLineshapeAliases, _applyBackendParams, _peakArea, _computeRFactor };')(
  { peaks: [] }, () => null);

const tabs = JSON.parse(fs.readFileSync(tabsPath, 'utf8'));
const targets = new Map(JSON.parse(fs.readFileSync(targetsPath, 'utf8')).map(t => [t.id, t]));
const tabOf = (project, name) => tabs.find(t => t.project === project && t.name === name);

const rows = [];
for (const line of fs.readFileSync(recPath, 'utf8').split('\n')) {
  if (!line.trim()) continue;
  const rec = JSON.parse(line);
  const t = targets.get(rec.id);
  if (!t) continue;                                   // a synthetic record: no page model to read it with
  const { R, O } = rec;
  const src = tabOf(t.project, t.source || t.tab);
  const peaks = JSON.parse(JSON.stringify(src.peaks));
  main._migrateLineshapeAliases(peaks);
  for (const ip of O.individual_peaks) {
    const p = peaks.find(q => String(q.id) === String(ip.id));
    if (p) main._applyBackendParams(p, ip.params);
  }
  const be = R.energies, n = be.length, st = O.statistics;
  // chi-square: main's formula against the server's
  const mainChi = st.reduced_chi_square * Math.max(1, n - peaks.length * 3);
  const rmseMain = Math.sqrt(O.residuals.reduce((s, v) => s + v * v, 0) / Math.max(1, n));
  const bg = O.background_y, net = R.counts.map((c, i) => c - bg[i]);
  const rMain = main._computeRFactor({ be, bgSubtracted: net, bgIntensity: bg, fittedY: O.fitted_y });
  const comps = O.individual_peaks.map(ip => {
    const p = peaks.find(q => String(q.id) === String(ip.id));
    const y = main.evalPeakArray(be, p);
    const amp = Math.max(...ip.y.map(Math.abs));
    const dev = Math.max(...y.map((v, i) => Math.abs(v - ip.y[i])));
    const areaMain = main._peakArea(p, be), areaRec = ip.params.area.value;
    return { id: String(ip.id), shape: p.shape, curveRel: amp > 0 ? dev / amp : (dev === 0 ? 0 : Infinity),
             areaMain, areaRec, areaRel: areaRec !== 0 ? Math.abs(areaMain - areaRec) / Math.abs(areaRec) : (areaMain === 0 ? 0 : Infinity) };
  });
  const pct = key => { const tot = comps.reduce((s, c) => s + c[key], 0); return comps.map(c => tot > 0 ? 100 * c[key] / tot : 0); };
  const pm = pct('areaMain'), pr = pct('areaRec');
  rows.push({ id: rec.id, project: t.project, tab: t.tab, kind: t.kind, n, peaks: peaks.length, nFree: st.n_free_params,
              chiMain: mainChi, chiRec: st.chi_square, chiRel: Math.abs(mainChi - st.chi_square) / st.chi_square,
              rmseMain, rmseRec: st.rmse, rmseRel: Math.abs(rmseMain - st.rmse) / st.rmse,
              rMainPct: rMain ? rMain.rPct : null, rRecPct: st.r_factor == null ? null : st.r_factor * 100,
              comps, areaPctMaxPp: Math.max(...pm.map((v, i) => Math.abs(v - pr[i]))) });
}

const med = a => { const s = [...a].sort((x, y) => x - y), k = s.length; return k ? (k % 2 ? s[(k - 1) / 2] : (s[k / 2 - 1] + s[k / 2]) / 2) : NaN; };
const max = a => a.reduce((m, v) => Math.max(m, v), 0);
const g = x => Number(x).toPrecision(3);
const out = [];
const say = s => { out.push(s); console.log(s); };
say(`${rows.length} committed targets (seal 1b run v2 records): one server reply each, read as main reads it and as the record says`);
const formulaDiffers = rows.filter(r => r.nFree !== r.peaks * 3);
say(`chi-square: main formed chi2r x max(1, n - 3 x peaks); the record is the server's chi-square`);
say(`  free parameters != 3 x peaks (links, locks, held or extra shape parameters): ${formulaDiffers.length} / ${rows.length}`);
say(`  relative difference: median ${g(med(rows.map(r => r.chiRel)))}, max ${g(max(rows.map(r => r.chiRel)))}; ` +
    `> 1 %: ${rows.filter(r => r.chiRel > 0.01).length}, > 10 %: ${rows.filter(r => r.chiRel > 0.1).length}`);
say(`RMSE: main's over the reply's residuals vs the server's: max relative difference ${g(max(rows.map(r => r.rmseRel)))}`);
const rd = rows.filter(r => r.rMainPct != null && r.rRecPct != null).map(r => Math.abs(r.rMainPct - r.rRecPct));
say(`R-factor: main's _computeRFactor vs the server's: max |difference| ${g(max(rd))} percentage points over ${rd.length}`);
const comps = rows.flatMap(r => r.comps);
const byShape = {};
for (const c of comps) (byShape[c.shape] ||= []).push(c);
say(`components (${comps.length}): main's page curve vs the recorded curve (max |difference| / the component's height) and area`);
for (const [sh, cs] of Object.entries(byShape).sort()) {
  say(`  ${sh.padEnd(10)} n=${String(cs.length).padStart(3)}  curve median ${g(med(cs.map(c => c.curveRel)))} max ${g(max(cs.map(c => c.curveRel)))}` +
      `   area relative median ${g(med(cs.map(c => c.areaRel)))} max ${g(max(cs.map(c => c.areaRel)))}`);
}
say(`area % (each target's largest component difference): median ${g(med(rows.map(r => r.areaPctMaxPp)))} pp, max ${g(max(rows.map(r => r.areaPctMaxPp)))} pp; ` +
    `> 0.01 pp: ${rows.filter(r => r.areaPctMaxPp > 0.01).length}, > 0.1 pp: ${rows.filter(r => r.areaPctMaxPp > 0.1).length}`);
if (jsonOut) fs.writeFileSync(jsonOut, JSON.stringify({ summary: out, rows }, null, 1));
