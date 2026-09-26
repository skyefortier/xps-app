#!/usr/bin/env node
// caM unit (2026-09-25): the page's LA (LACX) curve vs the server's, for every
// LA component in the committed projects, at its SAVED parameters on its tab's
// ROI grid (the page's getROIData semantics: corrected BE inside the ROI).
// Reports the max |page − server| as a fraction of amplitude and the area
// difference, per component. Run before and after the unit: before = the
// defect; after = what a student sees change when a saved project is opened.
// Usage: node scripts/lacx_page_vs_server.js [out.json]
const fs = require('fs'); const path = require('path'); const { execFileSync } = require('child_process');
const ROOT = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'templates/index.html'), 'utf8');
const m = html.match(/function gaussian\(x, center, fwhm\) \{[\s\S]*?\nfunction evalPeakArray\(beArr, p\) \{[\s\S]*?\n\}/);
const { evalPeakArray } = eval('(function(){\n' + m[0] + '\nreturn { evalPeak, evalPeakArray };})()');
const PY = [path.join(ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3'].find(p => fs.existsSync(p));
const DATA = path.join(ROOT, 'docs/autofit/test_data');
const rows = [];
const specs = [];
for (const zp of fs.readdirSync(DATA).filter(f => f.endsWith('.proj.zip')).sort()) {
  const tabs = JSON.parse(execFileSync(PY, ['-c', 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))', ROOT, path.join(DATA, zp)], { encoding: 'utf8', maxBuffer: 1 << 26 }));
  for (const t of tabs) {
    const ui = t.ui || {}; const lo = parseFloat(ui.roiMin), hi = parseFloat(ui.roiMax);
    const be = t.rawBE.map(b => b - (t.ccShift || 0)).filter(c => (!(lo <= Infinity) || c >= lo) && (!(hi <= Infinity) || c <= hi));
    for (const p of t.peaks || []) {
      if (p.shape !== 'LACX') continue;
      rows.push({ project: zp, tab: t.name, peak: p.name, caM: p.caM, fixCaM: !!p.fixCaM, be, p });
      specs.push({ shape: 'la_casaxps', params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm, alpha: p.caAlpha, beta: p.caBeta, m: p.caM }, x: be });
    }
  }
}
const srv = JSON.parse(execFileSync(PY, [path.join(ROOT, 'tests/js/lineshape_parity_backend.py')], { input: JSON.stringify(specs), encoding: 'utf8', maxBuffer: 1 << 28 }));
const out = rows.map((r, i) => {
  const pg = evalPeakArray(r.be, r.p); let mx = 0, aP = 0, aS = 0;
  for (let j = 0; j < r.be.length; j++) { mx = Math.max(mx, Math.abs(pg[j] - srv[i][j])); aP += pg[j]; aS += srv[i][j]; }
  return { project: r.project, tab: r.tab, peak: r.peak, caM: r.caM, fixCaM: r.fixCaM, maxDiffRel: mx / Math.abs(r.p.amplitude || 1), dAreaPct: aS ? 100 * (aP / aS - 1) : null };
});
const q = v => { v = [...v].sort((a, b) => a - b); const n = v.length; return { n, median: n % 2 ? v[(n - 1) / 2] : 0.5 * (v[n / 2 - 1] + v[n / 2]), max: v[n - 1] }; };
const summary = { components: out.length, integer_caM: out.filter(r => Number.isInteger(r.caM)).length, locked: out.filter(r => r.fixCaM).length,
  maxDiffRel: q(out.map(r => r.maxDiffRel)), absDAreaPct: q(out.map(r => Math.abs(r.dAreaPct))) };
console.log(JSON.stringify(summary));
if (process.argv[2]) fs.writeFileSync(process.argv[2], JSON.stringify({ summary, rows: out }, null, 1));
