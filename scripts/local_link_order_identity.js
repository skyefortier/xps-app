#!/usr/bin/env node
// Q10 0b (owner 2026-10-11): the local engine resolves links in dependency order and finalises
// on one frozen model. Claim: on every committed model the result is BIT-IDENTICAL to main's
// (none has a link chain two levels deep, where peak order mattered). This runs the local engine
// extracted from main's page and from this checkout's on each committed tab — its own spectrum,
// its saved peaks as the start, its saved background settings — and compares the committed peaks,
// χ², χ²ᵣ, RMSE and iterations exactly. Usage: node scripts/local_link_order_identity.js [main-ref]
// Writes docs/findings/local-link-order/identity.json.
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const REPO = path.join(__dirname, '..');
const REF = process.argv[2] || 'main';
const PY = [path.join(REPO, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3'].find(p => fs.existsSync(p)) || 'python3';

const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', '_laKernelHalf', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
  'evalPeakArray', 'evalAllPeaks', 'getPeak', 'runFitLocal', '_pageSoftware', '_localFitRecord', 'solveLinear',
  '_computeRFactor', '_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel', '_governingProvenance', '_localFitCaveat', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay', '_updateLocalModelBanner',
  '_componentSupportCore', '_supportRootOf', '_applySupportVerdicts', '_fitKeyCanon', '_endpointAvgFailure', '_sameFitKey', '_statsState', '_statsLiveState'];

function engine(html) {
  const lines = html.split('\n');
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
  const consts = (html.match(/^const (_LOCAL_FIT_CAVEAT\w*|_STATS_\w+_NOTE) = .*$/mg) || []).join('\n');
  const src = consts + '\nconst _SUPPORT_MIN_F = 10; const _startsLiveKey = () => "KEY";\n' + NAMES.map(extract).join('\n\n') +
    '\n' + require(path.join(REPO, 'tests/js/_page_background_source.js'))({ manual: 'none' });
  return () => {
    const dom = {};
    const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, setAttribute() {}, removeAttribute() {},
      classList: { add() {}, remove() {}, contains: () => false } });
    const state = { peaks: [], fitResult: null, rawBE: [], rawIntensity: [], ccShift: 0 };
    const noop = () => {};
    const f = new Function('document', 'state', 'notify', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_activeTab', '_escHtml', '_historyPreview', 'tabManager', '_updateRFactorUI', '_updateROIDisplay',
      'renderPeakList', 'updatePlot', 'renderResults', '_hideFitSpinner', '_autoSnapshot', 'manualAnchorBackground',
      src + '\nreturn { runFitLocal, computeBackgroundCore };')({ getElementById: el, querySelectorAll: () => [] }, state, noop, '', '', () => null,
      x => String(x), null, null, noop, noop, noop, noop, noop, noop, noop, be => new Array(be.length).fill(0));
    return { ...f, state };
  };
}

const mainHtml = execFileSync('git', ['-C', REPO, 'show', REF + ':templates/index.html'], { encoding: 'utf8', maxBuffer: 64 << 20 });
const hereHtml = fs.readFileSync(path.join(REPO, 'templates/index.html'), 'utf8');
const MAIN = engine(mainHtml), HERE = engine(hereHtml);

const script = 'import glob, json, sys; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs\n' +
  'out = []\nfor f in sorted(glob.glob(sys.argv[1] + "/docs/autofit/test_data/**/*.proj.*", recursive=True)):\n' +
  '    for t in load_project_tabs(f):\n        if not t.get("isStack") and t.get("peaks") and t.get("rawBE"):\n' +
  '            out.append({"file": f.split("/")[-1], "name": t.get("name"), "rawBE": t["rawBE"], "rawIntensity": t["rawIntensity"], "ccShift": t.get("ccShift") or 0, "ui": t.get("ui") or {}, "peaks": t["peaks"]})\n' +
  'print(json.dumps(out))';
const tabs = JSON.parse(execFileSync(PY, ['-c', script, REPO], { encoding: 'utf8', maxBuffer: 1 << 30 }));

function fit(make, t) {
  const env = make();
  const roiMin = parseFloat(t.ui.roiMin), roiMax = parseFloat(t.ui.roiMax);
  const be = [], y = [];
  t.rawBE.forEach((b, i) => { const c = b - t.ccShift; if (!(c < roiMin) && !(c > roiMax)) { be.push(c); y.push(t.rawIntensity[i]); } });
  const bg = env.computeBackgroundCore(be, y, { ...t.ui, anchors: [] });
  if (bg.converged !== true) return { skipped: 'background: ' + bg.failure };
  env.state.peaks = JSON.parse(JSON.stringify(t.peaks));
  const out = env.runFitLocal(be, y.map((v, i) => v - bg[i]), bg, { maxIterations: 3000 });
  const fr = env.state.fitResult;
  return { out, peaks: env.state.peaks, chi: fr && fr.chi, chiReduced: fr && fr.chiReduced, rmse: fr && fr.rmse };
}
// exact equality: every number by Object.is (−0 ≠ 0, NaN = NaN), every key and array element
function deepSame(a, b) {
  if (typeof a === 'number' || typeof b === 'number') return Object.is(a, b);
  if (a === null || b === null || typeof a !== 'object' || typeof b !== 'object') return a === b;
  if (Array.isArray(a) !== Array.isArray(b)) return false;
  const ka = Object.keys(a), kb = Object.keys(b);
  return ka.length === kb.length && ka.every(k => Object.prototype.hasOwnProperty.call(b, k) && deepSame(a[k], b[k]));
}
const rows = [];
let identical = 0, differ = 0, skipped = 0;
for (const t of tabs) {
  const a = fit(MAIN, t), b = fit(HERE, t);
  const same = deepSame(a, b);
  if (a.skipped) skipped++; else if (same) identical++; else differ++;
  rows.push({ file: t.file, tab: t.name, skipped: a.skipped || null, identical: same, success: a.out && a.out.success });
}
const result = { ref: REF, tabs: tabs.length, identical, differ, skipped, rows };
fs.mkdirSync(path.join(REPO, 'docs/findings/local-link-order'), { recursive: true });
fs.writeFileSync(path.join(REPO, 'docs/findings/local-link-order/identity.json'), JSON.stringify(result, null, 1));
console.log(`committed tabs ${tabs.length}: bit-identical ${identical}, different ${differ}, skipped ${skipped}`);
if (differ) for (const r of rows.filter(r => !r.identical && !r.skipped)) console.log('  DIFFERS', r.file, r.tab);
