#!/usr/bin/env node
// Sealed-fit v6 Q5 (owner 2026-10-11: "measure first and show me the numbers before switching"):
// ONE area definition for every reader. Today three: the page's rectangle sum × the first step
// (`_peakArea`: Results, sidebar, sidebar support patching, Quantify, CSV/XLSX, Auto-Fit's 40 %
// graphite warning), the server's trapezoid as a magnitude (`abs(trapezoid(y, x))`, fitting.py:
// individual_peaks[].area, the alternatives' areas and fractions), and the spectrum save's
// sequential trapezoid with |dx| per interval. The recommendation: the server's for every reader.
// This measures, on every committed saved fit, what each reader would show under the server's
// definition: each component's area, its area %, and whether Auto-Fit's 40 % graphite warning flips.
// The curves are the page's own (evalPeakArray: equal to the server's to ≤ 1e-6 of amplitude by the
// lineshape parity harnesses), on the grid the page integrates on (fitResult.be, else the ROI grid).
// SUPERSEDED (Codex Q5 round 1) by scripts/q5_areas_on_load.py, which measures what the page shows
// after a real load: this reads the RAW saved records and integrates on the saved fit grid, which
// older saves hold in the UNCORRECTED frame (the B4C B 1s scans: 175.4-191.3 eV for peaks in the
// corrected 181.3-197.3 eV frame), so it reported a "B-O centred outside, 17-19 %" that the page never
// shows. Kept as the record of the pre-decision measurement; both baselines are explicit here.
// Usage: node scripts/q5_area_definitions.js. Writes docs/findings/q5-area/areas.json.
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const REPO = path.join(__dirname, '..');
const PY = [path.join(REPO, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3'].find(p => fs.existsSync(p)) || 'python3';
const lines = fs.readFileSync(path.join(REPO, 'templates/index.html'), 'utf8').split('\n');
const extract = name => {
  const re = new RegExp('^(async )?function ' + name.replace(/\$/g, '\\$') + '\\(');
  const start = lines.findIndex(l => re.test(l));
  if (start < 0) throw new Error('missing ' + name);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  throw new Error('unbalanced ' + name);
};
const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', '_laKernelHalf', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array',
  '_fftRadix2', '_circularConvolve', 'dsgConvolved_array', 'evalPeakArray', '_roiSelect', '_autoFitDecideAreaWarning'];
// the page's area BEFORE this unit, frozen here (the page's _peakArea is now the server's trapezoid)
const rectArea = (y, be) => y.reduce((s, v) => s + v, 0) * (be.length > 1 ? Math.abs(be[1] - be[0]) : 1);
const P = new Function(NAMES.map(extract).join('\n\n') + '\nreturn { ' + NAMES.join(', ') + ' };')();

const script = 'import glob, json, sys; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs\n' +
  'out = []\nfor f in sorted(glob.glob(sys.argv[1] + "/docs/autofit/test_data/**/*.proj.*", recursive=True)):\n' +
  '    for t in load_project_tabs(f):\n        if not t.get("isStack") and t.get("peaks") and t.get("rawBE"):\n' +
  '            fr = t.get("fitResult") or {}\n' +
  '            out.append({"file": f.split("/")[-1], "name": t.get("name"), "rawBE": t["rawBE"], "rawIntensity": t["rawIntensity"], "ccShift": t.get("ccShift") or 0, "ui": t.get("ui") or {}, "peaks": t["peaks"], "be": fr.get("be")})\n' +
  'print(json.dumps(out))';
const tabs = JSON.parse(execFileSync(PY, ['-c', script, REPO], { encoding: 'utf8', maxBuffer: 512 << 20 }));

const trapzServer = (y, x) => { let s = 0; for (let i = 0; i + 1 < x.length; i++) s += (x[i + 1] - x[i]) * (y[i + 1] + y[i]) / 2; return Math.abs(s); };
const trapzSave = (y, x) => { let s = 0; for (let i = 1; i < x.length; i++) s += 0.5 * (y[i - 1] + y[i]) * Math.abs(x[i] - x[i - 1]); return s; };
const pct = (areas, i) => { const t = areas.reduce((s, v) => s + v, 0); return t > 0 ? 100 * areas[i] / t : NaN; };

const rows = [];
for (const t of tabs) {
  let be = Array.isArray(t.be) && t.be.length > 1 ? t.be : null, grid = 'fitResult.be';
  if (!be) { be = P._roiSelect(t.rawBE, t.rawIntensity, t.ccShift, t.ui.roiMin, t.ui.roiMax).be; grid = 'ROI'; }
  if (!be || be.length < 2) continue;
  const steps = be.slice(1).map((v, i) => Math.abs(v - be[i]));
  const step0 = steps[0], irregular = Math.max(...steps.map(s => Math.abs(s - step0) / step0));
  const curves = t.peaks.map(p => P.evalPeakArray(be, p));
  const rect = curves.map(y => rectArea(y, be));
  const server = curves.map(y => trapzServer(y, be));
  const save = curves.map(y => trapzSave(y, be));
  const comps = t.peaks.map((p, i) => ({
    name: p.name, shape: p.shape, rect: rect[i], server: server[i], save: save[i],
    rel_server: rect[i] ? (server[i] - rect[i]) / rect[i] : null,
    rel_save: rect[i] ? (save[i] - rect[i]) / rect[i] : null,
    pct_rect: pct(rect, i), pct_server: pct(server, i), dpp: pct(server, i) - pct(rect, i),
    // what the component carries at the window's edges (the trapezoid weighs the end samples by half)
    edge_frac: rect[i] ? (curves[i][0] + curves[i][curves[i].length - 1]) * step0 / 2 / rect[i] : null,
  }));
  const g = t.peaks.findIndex(p => p.name === 'Graphite');
  const warn = g < 0 ? null : {
    rect: P._autoFitDecideAreaWarning(t.peaks.map((p, i) => ({ id: p.id, area: rect[i] })), t.peaks[g].id),
    server: P._autoFitDecideAreaWarning(t.peaks.map((p, i) => ({ id: p.id, area: server[i] })), t.peaks[g].id),
    frac_rect: comps[g].pct_rect, frac_server: comps[g].pct_server,
  };
  rows.push({ file: t.file, tab: t.name, grid, n: be.length, step0, irregular, comps, graphite: warn });
}

const all = rows.flatMap(r => r.comps.filter(c => c.rect > 0));
const absRel = all.map(c => Math.abs(c.rel_server)).sort((a, b) => a - b);
const q = f => absRel[Math.min(absRel.length - 1, Math.floor(f * absRel.length))];
const dpp = rows.map(r => Math.max(...r.comps.map(c => Math.abs(c.dpp) || 0))).sort((a, b) => a - b);
const gRows = rows.filter(r => r.graphite);
const flips = gRows.filter(r => !!r.graphite.rect !== !!r.graphite.server);
const nearest = gRows.map(r => ({ tab: r.file + ' / ' + r.tab, rect: r.graphite.frac_rect, server: r.graphite.frac_server }))
  .sort((a, b) => Math.abs(a.rect - 40) - Math.abs(b.rect - 40)).slice(0, 5);
const worst = all.map((c, k) => c).sort((a, b) => Math.abs(b.rel_server) - Math.abs(a.rel_server)).slice(0, 8);
const worstRows = rows.flatMap(r => r.comps.map(c => ({ tab: r.file + ' / ' + r.tab, grid: r.grid, irregular: r.irregular, ...c })))
  .filter(c => c.rect > 0).sort((a, b) => Math.abs(b.rel_server) - Math.abs(a.rel_server)).slice(0, 8);
const summary = {
  tabs: rows.length, components: all.length,
  grids: { fitResult_be: rows.filter(r => r.grid === 'fitResult.be').length, roi: rows.filter(r => r.grid === 'ROI').length,
           irregular_over_1e_6: rows.filter(r => r.irregular > 1e-6).length, max_irregular: Math.max(...rows.map(r => r.irregular)) },
  area_rel_change_server_vs_page: { median: q(0.5), p90: q(0.9), max: absRel[absRel.length - 1],
    over_0_1_pct: absRel.filter(v => v > 1e-3).length, over_1_pct: absRel.filter(v => v > 1e-2).length },
  area_pct_change_pp_per_tab_max: { median: dpp[Math.floor(dpp.length / 2)], p90: dpp[Math.floor(0.9 * dpp.length)], max: dpp[dpp.length - 1],
    tabs_over_0_1_pp: dpp.filter(v => v > 0.1).length, tabs_over_1_pp: dpp.filter(v => v > 1).length },
  save_vs_server_max_rel: Math.max(...all.map(c => Math.abs((c.save - c.server) / c.server))),
  graphite_40pct_warning: { tabs_with_graphite: gRows.length, warn_page: gRows.filter(r => r.graphite.rect).length,
    warn_server: gRows.filter(r => r.graphite.server).length, flips: flips.map(r => r.file + ' / ' + r.tab), nearest_to_40: nearest },
  worst_components: worstRows.map(c => ({ tab: c.tab, name: c.name, shape: c.shape, grid: c.grid, rel: c.rel_server, dpp: c.dpp, edge_frac: c.edge_frac, irregular: c.irregular })),
};
fs.writeFileSync(path.join(REPO, 'docs/findings/q5-area/areas.json'), JSON.stringify({ summary, rows }, null, 1) + '\n');
console.log(JSON.stringify(summary, null, 1));
