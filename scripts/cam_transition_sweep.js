const path = require('path'); process.chdir(path.join(__dirname, '..'));   // caM unit: local LA fits around kernel-width transitions (m = 6k/7), m unlocked vs locked (held either way since the withdrawal; plan §7)
const fs = require('fs'); const html = fs.readFileSync('templates/index.html', 'utf8'); const lines = html.split('\n');
function extractFn(name) { const re = new RegExp('^(async )?function ' + name + '\\('); const start = lines.findIndex(l => re.test(l)); let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) { for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; } if (seen && depth === 0) return lines.slice(start, i + 1).join('\n'); } }
const NAMES = ['_arrMin','_arrMax','gaussian','lorentzian','pseudoVoigt','asymmGL','doniachSunjic','laCasaXPSCore','laCasaXPS','laTrueCasaXPS','_laKernelHalf','laTrueCasaXPS_array','evalPeak','_dsgAlpha','dsgDeltaKernel_array','_fftRadix2','_circularConvolve','dsgConvolved_array','evalPeakArray','evalAllPeaks','getPeak','runFitLocal','solveLinear','_computeRFactor','_fitStatLabel','_isUnweightedLocal','_isLocalProvenance','_localFitDetail','_isLocalFit','_isLocalModel','_governingProvenance','_localFitCaveat','_fitStatusText','_applyStatCaption','_applyStatDisplay','_updateLocalModelBanner','_componentSupportCore','_supportRootOf','_applySupportVerdicts'];
const CAV = (html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg) || []).join('\n');
function env() { const dom = {}; const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, setAttribute() {}, removeAttribute() {}, classList: { add() {}, remove() {}, contains: () => false } });
  const state = { peaks: [], fitResult: null, rawBE: [], rawIntensity: [], ccShift: 0 }; const noop = () => {};
  const f = new Function('document','state','notify','_CHISQ_TOOLTIP','_LOCALFIT_TOOLTIP','_activeTab','_escHtml','_historyPreview','tabManager','_updateRFactorUI','_updateROIDisplay','renderPeakList','updatePlot','renderResults','_hideFitSpinner','_autoSnapshot','manualAnchorBackground',
    CAV + '\nconst _SUPPORT_MIN_F = 10; const _startsLiveKey = () => "K";\n' + NAMES.map(extractFn).join('\n\n') + '\nreturn { runFitLocal, evalAllPeaks };');
  return { ...f({ getElementById: el, querySelectorAll: () => [] }, state, noop, '', '', () => null, x => String(x), null, null, noop, noop, noop, noop, noop, noop, noop, be => be.map(() => 0)), state }; }
const grid = (lo, hi, st) => Array.from({ length: Math.round((hi - lo) / st) + 1 }, (_, i) => lo + st * i);
let unlockedFail = 0, lockedFail = 0, differ = 0, n = 0; const fails = [];
for (const st of [0.03, 0.05, 0.1]) for (const k of [2, 3, 5, 9, 17, 33, 56]) for (const off of [-0.003, -0.0005, 0, 0.0005, 0.003]) for (const startDelta of [-0.4, 0.3]) {
  const mT = 6 * k / 7 + off; const be = grid(280, 280 + 150 * st, st);
  const truth = { id: 1, name: 'la', shape: 'LACX', center: 280 + 75 * st + 0.013, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: mT, glMix: 50, asymmetry: 0 };
  const run = fixCaM => { const e = env(); e.state.peaks = [{ ...truth }]; const d = e.evalAllPeaks(be, e.state.peaks).map((v, i) => v + 5 * Math.sin(1.77 * i));
    e.state.peaks = [{ ...truth, amplitude: 4600, caM: Math.max(0.01, mT + startDelta), fixCenter: true, fixFwhm: true, fixCaM }]; const o = e.runFitLocal(be, d, be.map(() => 0)); return { o, chi: e.state.fitResult && e.state.fitResult.chi }; };
  const fr = run(false), hd = run(true); n++;
  if (!fr.o.success) { unlockedFail++; fails.push({ st, k, off, startDelta, msg: fr.o.message }); }
  if (!hd.o.success) lockedFail++;
  if (fr.o.success && hd.o.success && Math.abs(fr.chi - hd.chi) > 1e-12 * Math.max(1, hd.chi)) differ++;
}
console.log(JSON.stringify({ note: 'since the caM withdrawal the local engine HOLDS m, so unlocked and locked are the same fit; the free-m evidence of Codex round 1 (0 of 210 failing with m free) is historical, plan §7', cases: n, unlocked_failed: unlockedFail, locked_failed: lockedFail, unlocked_differs_from_locked: differ, first_fails: fails.slice(0, 5) }));
