// Background-math implementation (2026-10-01): analysis of scripts/bg_math_impl_measure.py
// runs. node bg_math_impl_analyze.js <dir> [suffix] — reads main_<suffix>, main2_<suffix>,
// item1_only_<suffix>, both_<suffix> .jsonl (suffix tr: the committed settings; avg3: every
// target at endpoint averaging 3, the page's default) (+ legacy_reference.json, the page's RSF data) and prints, for each
// comparison, the background-level NET-AREA change (%, on each target's own window,
// method and averaging) and the fit-level AREA % and ATOMIC % changes (pp; the largest
// component per target; area % over the components the server calls supported, at %
// the Quantify tab's area/RSF with the page's own _detectPeakRSF): median, max, count
// over 1 (and over 0.1). main vs main2 is Trust-Region's own press-to-press noise.
const fs = require('fs'), path = require('path');
const dir = process.argv[2], suffix = process.argv[3] || 'tr';
// `node bg_math_impl_analyze.js <dir> pair A.jsonl B.jsonl` compares two runs of
// scripts/bg_math_impl_seeded.py (main's seeds forced on the branch: the background's
// effect on the fits alone)
const PAIR = suffix === 'pair' ? [process.argv[4], process.argv[5]] : null;
const html = fs.readFileSync(path.join(__dirname, '..', 'templates', 'index.html'), 'utf8');
const lines = html.split('\n');
function block(re) {
  const s = lines.findIndex(l => re.test(l)); if (s < 0) throw new Error('missing ' + re);
  let d = 0, seen = false;
  for (let i = s; i < lines.length; i++) { for (const c of lines[i]) { if (c === '{') { d++; seen = true; } else if (c === '}') d--; }
    if (seen && d === 0) return lines.slice(s, i + 1).join('\n'); }
}
const LEGACY_REFERENCE = JSON.parse(fs.readFileSync(path.join(dir, 'legacy_reference.json'), 'utf8'));
const { _detectPeakRSF } = new Function('LEGACY_REFERENCE', ['let _accSurveyCache = null; const LEGACY_REFERENCE_OK = true; function _accReferenceUnavailable() {}',
  block(/^const SCOFIELD_RSF = \{/) + ';', block(/^function _accSurveyElements\(/), block(/^function _detectPeakRSF\(/)].join('\n') +
  '\nreturn { _detectPeakRSF };')(LEGACY_REFERENCE);
const read = f => Object.fromEntries(fs.readFileSync(path.join(dir, f), 'utf8').trim().split('\n').map(l => JSON.parse(l)).map(r => [r.id, r]));
const RUNS = PAIR ? { a: read(PAIR[0]), b: read(PAIR[1]) }
  : Object.fromEntries(['main', 'main2', 'item1_only', 'both'].map(v => [v, read(`${v}_${suffix}.jsonl`)]));
function pct(r, rsf) {
  const sup = r.components.filter(c => c.supported !== false);
  const w = sup.map(c => c.area / (rsf ? _detectPeakRSF({ name: c.name || '', center: c.center }).rsf : 1));
  const tot = w.reduce((a, b) => a + b, 0);
  return Object.fromEntries(sup.map((c, i) => [c.id, tot > 0 ? 100 * w[i] / tot : 0]));
}
const q = (a, p) => { if (!a.length) return null; const s = [...a].sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(p * (s.length - 1) + 0.5))]; };
const r3 = v => v == null ? null : Math.round(v * 1000) / 1000;
const S = a => ({ n: a.length, median: r3(q(a, 0.5)), p90: r3(q(a, 0.9)), max: r3(a.length ? Math.max(...a) : null),
                  over_1: a.filter(v => v > 1).length, over_0_1: a.filter(v => v > 0.1).length });
function compare(an, bn) {
  const A = RUNS[an], B = RUNS[bn];
  const net = [], area = [], at = [], worst = [], fail = [];
  for (const id of Object.keys(A)) {
    const a = A[id], b = B[id]; if (!b) continue;
    if (a.background && b.background && a.background.net_area > 0 && b.background.net_area != null)
      net.push(100 * Math.abs(b.background.net_area - a.background.net_area) / a.background.net_area);
    if (!!a.success !== !!b.success) fail.push([a.tab, a.project, an + ':' + (a.success ? 'ok' : (a.error || a.message)), bn + ':' + (b.success ? 'ok' : (b.error || b.message))]);
    if (!(a.success && b.success)) continue;
    const pa = pct(a, false), pb = pct(b, false), ta = pct(a, true), tb = pct(b, true);
    let mA = 0, mT = 0, who = null;
    for (const c of a.components) {
      const cb = b.components.find(x => x.id === c.id); if (!cb) continue;
      const da = Math.abs((pa[c.id] ?? 0) - (pb[c.id] ?? 0)), dt = Math.abs((ta[c.id] ?? 0) - (tb[c.id] ?? 0));
      if (da > mA) { mA = da; who = c.name; } mT = Math.max(mT, dt);
    }
    area.push(mA); at.push(mT);
    worst.push([r3(mA), r3(mT), a.project, a.tab, who, a.method, a.endpoint_avg, r3(a.chi2r), r3(b.chi2r)]);
  }
  return { compare: an + ' -> ' + bn, net_area_pct: S(net), area_pp: S(area), atomic_pp: S(at), success_changes: fail,
           worst: worst.sort((x, y) => y[0] - x[0]).slice(0, 8) };
}
if (PAIR) { console.log(JSON.stringify(compare('a', 'b'), null, 1)); process.exit(0); }
const out = [compare('main', 'main2'), compare('main', 'item1_only'), compare('item1_only', 'both'), compare('main', 'both')];
// net area split by the targets' averaging (item 1 moves only averaged windows)
const byAvg = {};
for (const id of Object.keys(RUNS.main)) {
  const a = RUNS.main[id], b = RUNS.both[id]; if (!b || !a.background || !b.background || !(a.background.net_area > 0)) continue;
  const k = a.endpoint_avg > 1 ? 'endpoint_avg>1' : 'endpoint_avg=1';
  (byAvg[k] ||= []).push(100 * Math.abs(b.background.net_area - a.background.net_area) / a.background.net_area);
}
console.log(JSON.stringify({ comparisons: out, net_area_main_to_both_by_averaging: Object.fromEntries(Object.entries(byAvg).map(([k, v]) => [k, S(v)])) }, null, 1));
