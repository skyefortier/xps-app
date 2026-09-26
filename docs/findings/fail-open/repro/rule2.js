const { extractFn, extractConst } = require('./lib.js');
const src = [extractConst('_SUPPORT_MIN_F'), extractConst('_UNSUPPORTED_LABEL'), ...['_validateUncertainties','_buildStderrMap','_isUnsupported','_escHtml'].map(extractFn)].join('\n');
function run(label, params, preFit, shape = 'GL', extra = {}) {
  const state = { peaks: [{ id: 1, name: 'P1', shape, support: null }] };
  state.fitResult = { backendResult: { individual_peaks: [{ id: '1', params }] }, _preFit: preFit, ...extra };
  const f = new Function('state', 'getPeak', '_startsLiveKey', src + '\nreturn _validateUncertainties;')(state, id => state.peaks.find(p => p.id === id), () => 'K');
  console.log(label, JSON.stringify(f().warnings.map(w => w.replace(/<[^>]+>/g, ''))));
}
// covariance failed (all stderr null); centre and gl_ratio did not move
const P = { center: { value: 285.0, stderr: null, vary: true, min: 283, max: 287 }, fwhm: { value: 1.5, stderr: null, vary: true, min: 0.1, max: 15 },
            amplitude: { value: 4000, stderr: null, vary: true, min: 0, max: null }, gl_ratio: { value: 0.3, stderr: null, vary: true, min: 0, max: 1 } };
run('runFit result, stderr all null, nothing moved:', P, { 1: { center: 285.0, fwhm: 1.5, amplitude: 4000, glMix: 30 } });
// same, but params moved (singular covariance after a real move)
const P2 = JSON.parse(JSON.stringify(P)); P2.center.value = 285.3; P2.fwhm.value = 1.3; P2.amplitude.value = 4500; P2.gl_ratio.value = 0.45;
run('runFit result, stderr all null, params moved:', P2, { 1: { center: 285.0, fwhm: 1.5, amplitude: 4000, glMix: 30 } });
// Auto-Fit result: no _preFit at all
run('Auto-Fit result (no _preFit), stderr all null, nothing moved:', P, undefined);
// amplitude driven to 0 with no current verdict
run('amplitude 0 on its floor, no current verdict:', { amplitude: { value: 0, stderr: 5, vary: true, min: 0, max: null } }, {});
// asym-GL asymmetry at its upper bound
run('asym-GL asymmetry at 1.0 (bound [0,1]):', { asymmetry: { value: 1.0, stderr: 0.01, vary: true, min: 0, max: 1 } }, {}, 'asym-GL');
