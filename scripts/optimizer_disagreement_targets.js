#!/usr/bin/env node
// Build the fit targets for the optimiser-disagreement frequency measurement
// (investigation 2026-09-18). NO app code is changed: the requests are built
// by the SHIPPED frontend functions extracted from templates/index.html
// (peakToBackendSpec, _bgWindowIndices) and static/js/batch_propagation.js,
// so every target is exactly what Run Fit would send.
//
// Two kinds of start per committed project:
//   batch : the region's first fitted tab is propagated onto every other tab
//           of the same region, as runPropagation does (scaled clone, source
//           background/ROI/charge shift) — a start that is NOT yet a solution;
//   own   : each fitted tab's own saved model and settings — what pressing
//           Run Fit again on a saved project sends.
// Usage: node scripts/optimizer_disagreement_targets.js <tabs.json> > targets.json
const fs = require('fs'); const path = require('path'); const crypto = require('crypto');
const ROOT = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'templates/index.html'), 'utf8'); const lines = html.split('\n');
function extractFn(name) { const re = new RegExp('^(async )?function ' + name + '\\('); const s = lines.findIndex(l => re.test(l)); if (s < 0) throw new Error(name); let d = 0, seen = false;
  for (let i = s; i < lines.length; i++) { for (const ch of lines[i]) { if (ch === '{') { d++; seen = true; } else if (ch === '}') d--; } if (seen && d === 0) return lines.slice(s, i + 1).join('\n'); } }
const BatchPropagation = require(path.join(ROOT, 'static/js/batch_propagation.js'));
const state = { peaks: [] };
const fns = new Function('state', 'getPeak', extractFn('peakToBackendSpec') + '\n' + extractFn('_bgWindowIndices') + '\nreturn { peakToBackendSpec, _bgWindowIndices };')(state, id => state.peaks.find(p => p.id === id));
const tabs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const region = name => name.replace(/_\d+$/, '').trim();
function request(kind, project, tab, peaks, ui, ccShift, rawBE, rawIntensity, sourceName) {
  const roiMin = parseFloat(ui.roiMin), roiMax = parseFloat(ui.roiMax);
  const lo = isNaN(roiMin) ? -Infinity : roiMin, hi = isNaN(roiMax) ? Infinity : roiMax;
  const be = [], inten = [];
  rawBE.forEach((b, i) => { const c = b - (isNaN(ccShift) ? 0 : ccShift); if (c >= lo && c <= hi) { be.push(c); inten.push(rawIntensity[i]); } });
  if (be.length < 10 || !peaks.length) return null;
  const win = fns._bgWindowIndices(be, parseFloat(ui.bgStart), parseFloat(ui.bgEnd));
  state.peaks = peaks;
  const specs = peaks.map(fns.peakToBackendSpec);
  const bgType = ui.bgType || 'shirley';
  if (bgType === 'manual') return null;        // anchors are per-tab hand work; out of scope for a method comparison
  const t = { kind, project, region: region(tab), tab, source: sourceName || null, be, inten,
    background: { method: bgType, start_idx: win.i0, end_idx: win.i1 + 1, endpoint_avg: parseInt(ui.endpointAvg) || 1 },
    specs, n_peaks: peaks.length, shapes: peaks.map(p => p.shape) };
  t.id = crypto.createHash('sha1').update(JSON.stringify([t.kind, be, inten, specs, t.background])).digest('hex').slice(0, 12);
  return t;
}
const out = []; const seen = new Set();
const byProject = {};
for (const t of tabs) { if (!t.peaks || !t.peaks.length) continue; (byProject[t.project] ||= []).push(t); }
for (const [project, list] of Object.entries(byProject)) {
  const groups = {};
  for (const t of list) (groups[region(t.name)] ||= []).push(t);
  for (const g of Object.values(groups)) {
    for (const t of g) { const r = request('own', project, t.name, JSON.parse(JSON.stringify(t.peaks)), t.ui, t.ccShift, t.rawBE, t.rawIntensity); if (r && !seen.has(r.id)) { seen.add(r.id); out.push(r); } }
    const src = g[0]; const srcMax = Math.max(...src.rawIntensity);
    for (const tgt of g.slice(1)) {
      const scale = srcMax > 0 ? Math.max(...tgt.rawIntensity) / srcMax : 1;
      const cloned = JSON.parse(JSON.stringify(src.peaks)).map(p => ({ ...p, amplitude: p.linked ? p.amplitude : p.amplitude * scale }));
      const ui = BatchPropagation.propagateFitUi({ ...src.ui }, { ...tgt.ui });
      const r = request('batch', project, tgt.name, cloned, ui, src.ccShift, tgt.rawBE, tgt.rawIntensity, src.name);
      if (r && !seen.has(r.id)) { seen.add(r.id); out.push(r); }
    }
  }
}
process.stdout.write(JSON.stringify(out));
process.stderr.write(`targets: ${out.length} (own ${out.filter(t => t.kind === 'own').length}, batch ${out.filter(t => t.kind === 'batch').length})\n`);
