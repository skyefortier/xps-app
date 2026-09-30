// A2 analysis: node a2_analyze.js <dir> <method> <variant>  — compares <variant>_<method>.jsonl with main_<method>.jsonl.
// Area % = the Results table's percentages (over components the server calls supported); at % = the Quantify
// tab's (area/RSF over supported components; RSF detected by the page's own _detectPeakRSF).
const fs = require('fs'), path = require('path');
const [dir, method, variant] = process.argv.slice(2);
const html = fs.readFileSync(path.join(__dirname, '..', 'templates', 'index.html'), 'utf8');
const lines = html.split('\n');
function block(startRe) {
  const s = lines.findIndex(l => startRe.test(l)); if (s < 0) throw new Error('missing ' + startRe);
  let d = 0, seen = false;
  for (let i = s; i < lines.length; i++) { for (const c of lines[i]) { if (c === '{') { d++; seen = true; } else if (c === '}') d--; }
    if (seen && d === 0) return lines.slice(s, i + 1).join('\n'); }
}
const LEGACY_REFERENCE = JSON.parse(fs.readFileSync(path.join(dir, 'legacy_reference.json'), 'utf8'));
const src = ['let _accSurveyCache = null; const LEGACY_REFERENCE_OK = true; function _accReferenceUnavailable() {}',
  block(/^const SCOFIELD_RSF = \{/) + ';', block(/^function _accSurveyElements\(/), block(/^function _detectPeakRSF\(/)].join('\n');
const { _detectPeakRSF } = new Function('LEGACY_REFERENCE', src + '\nreturn { _detectPeakRSF };')(LEGACY_REFERENCE);
const read = f => Object.fromEntries(fs.readFileSync(path.join(dir, f), 'utf8').trim().split('\n').map(l => JSON.parse(l)).map(r => [r.id, r]));
const A = read(`main_${method}.jsonl`), B = read(`${variant}_${method}.jsonl`);
function pct(r, rsf) {
  const sup = r.components.filter(c => c.supported !== false);
  const w = sup.map(c => c.area / (rsf ? _detectPeakRSF({ name: c.name || '', center: c.center }).rsf : 1));
  const tot = w.reduce((a, b) => a + b, 0);
  return Object.fromEntries(sup.map((c, i) => [c.id, tot > 0 ? 100 * w[i] / tot : 0]));
}
const q = (a, p) => { if (!a.length) return null; const s = [...a].sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(p * (s.length - 1) + 0.5))]; };
const med = a => q(a, 0.5), r2 = v => v == null ? null : Math.round(v * 1000) / 1000;
const out = { method, variant, n_both: 0, success: { main_true: 0, after_true: 0, lost: [], gained: [] }, dArea: [], dAt: [], dChi: [], dSec: [], secMain: [], secAfter: [],
  supportFlips: [], startsLine: { changed: 0, examples: [], alt_main: 0, alt_after: 0, failed_main: 0, failed_after: 0 }, cert: { moved: 0, uncertified: 0, restarts: [] }, worst: [] };
const line = s => !s || !s.ran ? `(not run: ${s && s.reason})` : `${s.n_same_as_fit}/${s.n_run} same; ${s.n_in_alternatives} in ${s.n_alternatives} lower; ${s.n_not_better_elsewhere} not better; ${s.n_run - s.n_converged} not converged`;
for (const id of Object.keys(A)) {
  const a = A[id], b = B[id]; if (!b) continue;
  out.n_both++; if (a.success) out.success.main_true++; if (b.success) out.success.after_true++;
  if (a.success && !b.success) out.success.lost.push([id, a.tab, b.message]);
  if (!a.success && b.success) out.success.gained.push([id, a.tab]);
  out.secMain.push(a.sec); out.secAfter.push(b.sec); out.dSec.push(b.sec - a.sec);
  if (b.certificate) { if (b.certificate.moved) out.cert.moved++; if (!b.certificate.certified) out.cert.uncertified++; out.cert.restarts.push(b.certificate.restarts); }
  if (!(a.success && b.success)) continue;
  const pa = pct(a, false), pb = pct(b, false), ta = pct(a, true), tb = pct(b, true);
  let mA = 0, mT = 0, who = null;
  for (const c of a.components) {
    const cb = b.components.find(x => x.id === c.id);
    if ((c.supported !== false) !== (cb.supported !== false)) out.supportFlips.push([id, a.tab, c.name, c.supported, cb.supported]);
    const da = Math.abs((pa[c.id] ?? 0) - (pb[c.id] ?? 0)), dt = Math.abs((ta[c.id] ?? 0) - (tb[c.id] ?? 0));
    if (da > mA) { mA = da; who = c.name; } mT = Math.max(mT, dt);
  }
  out.dArea.push(mA); out.dAt.push(mT); out.dChi.push((b.chi2r - a.chi2r) / a.chi2r);
  out.worst.push([mA, id, a.project, a.tab, who, r2(a.chi2r), r2(b.chi2r)]);
  const la = line(a.starts), lb = line(b.starts);
  if (a.starts && a.starts.n_alternatives) out.startsLine.alt_main++; if (b.starts && b.starts.n_alternatives) out.startsLine.alt_after++;
  if (a.starts && a.starts.ran && a.starts.n_run > a.starts.n_converged) out.startsLine.failed_main++;
  if (b.starts && b.starts.ran && b.starts.n_run > b.starts.n_converged) out.startsLine.failed_after++;
  if (la !== lb) { out.startsLine.changed++; if (out.startsLine.examples.length < 12) out.startsLine.examples.push([a.tab, la, '→', lb]); }
}
const S = a => ({ median: r2(med(a)), p90: r2(q(a, 0.9)), max: r2(Math.max(...a)), over_1pp: a.filter(v => v > 1).length, over_0_1pp: a.filter(v => v > 0.1).length, n: a.length });
const res = { method, variant, n_both: out.n_both, success: out.success,
  area_pp: S(out.dArea), atomic_pp: S(out.dAt),
  chi2r_rel: { median: med(out.dChi), min: Math.min(...out.dChi), max: Math.max(...out.dChi), lower_by_1pct: out.dChi.filter(v => v < -0.01).length, higher: out.dChi.filter(v => v > 1e-6).length },
  sec: { main_median: r2(med(out.secMain)), after_median: r2(med(out.secAfter)), added_median: r2(med(out.dSec)), added_p90: r2(q(out.dSec, 0.9)), added_max: r2(Math.max(...out.dSec)),
         main_p90: r2(q(out.secMain, 0.9)), after_p90: r2(q(out.secAfter, 0.9)), main_max: r2(Math.max(...out.secMain)), after_max: r2(Math.max(...out.secAfter)),
         after_over_60s: out.secAfter.filter(v => v > 60).length, main_over_60s: out.secMain.filter(v => v > 60).length },
  certificate: { moved: out.cert.moved, uncertified: out.cert.uncertified, restarts_median: med(out.cert.restarts), restarts_max: Math.max(...out.cert.restarts) },
  support_flips: out.supportFlips, starts_line: out.startsLine,
  worst_area: out.worst.sort((x, y) => y[0] - x[0]).slice(0, 8).map(w => [r2(w[0]), ...w.slice(1)]) };
console.log(JSON.stringify(res, null, 1));
