#!/usr/bin/env node
// Q5 unit (owner 2026-10-12): a component centred outside the fit window gets a plain note in
// Results ("centred outside the window — its area is poorly determined by the data"). This counts,
// with the page's own _centredOutsideWindow on the grid Results integrates on (fitResult.be, else
// the ROI grid), how many committed saved components get the note, and how far outside they sit.
// Usage: node scripts/outside_window_census.js. Writes docs/findings/q5-area/outside_window.json.
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const REPO = path.join(__dirname, '..');
const PY = [path.join(REPO, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3'].find(p => fs.existsSync(p)) || 'python3';
const lines = fs.readFileSync(path.join(REPO, 'templates/index.html'), 'utf8').split('\n');
const extract = name => {
  const start = lines.findIndex(l => new RegExp('^function ' + name + '\\(').test(l));
  if (start < 0) throw new Error('missing ' + name);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
};
const P = new Function(['_arrMin', '_arrMax', '_roiSelect', '_centredOutsideWindow'].map(extract).join('\n') + '\nreturn { _arrMin, _arrMax, _roiSelect, _centredOutsideWindow };')();
const script = 'import glob, json, sys; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs\n' +
  'out = []\nfor f in sorted(glob.glob(sys.argv[1] + "/docs/autofit/test_data/**/*.proj.*", recursive=True)):\n' +
  '    for t in load_project_tabs(f):\n        if not t.get("isStack") and t.get("peaks") and t.get("rawBE"):\n' +
  '            out.append({"file": f.split("/")[-1], "name": t.get("name"), "rawBE": t["rawBE"], "rawIntensity": t["rawIntensity"], "ccShift": t.get("ccShift") or 0, "ui": t.get("ui") or {}, "peaks": t["peaks"], "be": (t.get("fitResult") or {}).get("be")})\n' +
  'print(json.dumps(out))';
const tabs = JSON.parse(execFileSync(PY, ['-c', script, REPO], { encoding: 'utf8', maxBuffer: 512 << 20 }));
const noted = []; let comps = 0;
for (const t of tabs) {
  const be = Array.isArray(t.be) && t.be.length > 1 ? t.be : P._roiSelect(t.rawBE, t.rawIntensity, t.ccShift, t.ui.roiMin, t.ui.roiMax).be;
  for (const p of t.peaks) {
    comps++;
    if (P._centredOutsideWindow(p, be)) {
      const lo = P._arrMin(be), hi = P._arrMax(be);
      noted.push({ tab: t.file + ' / ' + t.name, component: p.name, shape: p.shape, center: p.center, window: [lo, hi],
                   outside_by_ev: p.center < lo ? lo - p.center : p.center - hi, fwhm: p.fwhm });
    }
  }
}
const out = { tabs: tabs.length, components: comps, noted: noted.length, tabs_with_a_note: new Set(noted.map(n => n.tab)).size, components_noted: noted };
fs.writeFileSync(path.join(REPO, 'docs/findings/q5-area/outside_window.json'), JSON.stringify(out, null, 1) + '\n');
console.log(`committed tabs ${out.tabs}, components ${comps}: ${noted.length} centred outside the window in ${out.tabs_with_a_note} tabs`);
for (const n of noted) console.log(' ', n.tab, '|', n.component, n.shape, 'centre', n.center.toFixed(2), 'window', n.window.map(v => v.toFixed(2)).join('-'), 'outside by', n.outside_by_ev.toFixed(2), 'eV');
