const { extractFn, extractConst } = require('./lib.js');
const names = ['exportFitTable','_buildStderrMap','_peakArea','_isUnsupported','_currentSupport','_shapeExportCols','_isLocalFit','_isLocalProvenance','_isUnweightedLocal','_localFitCaveat','_startsSummaryText','_startsIfCurrent','_startsChosenText','updatePeakParam','_invalidateFittedY','_validateUncertainties','_escHtml'];
const consts = ['_SUPPORT_MIN_F','_UNSUPPORTED_LABEL','_LOCAL_FIT_CAVEAT','_LOCAL_FIT_CAVEAT_UNWEIGHTED'].map(extractConst).join('\n');
let downloaded = null;
const g = (x, c, w) => Math.exp(-((x - c) ** 2) / (2 * (w / 2.3548) ** 2));
const be = []; for (let v = 295; v >= 280; v -= 0.05) be.push(+v.toFixed(3));
const state = { ccShift: 0, peaks: [{ id: 1, name: 'C-C', shape: 'GL', center: 285.0, fwhm: 1.2, amplitude: 5000, glMix: 30, linked: null }] };
const keyOf = () => JSON.stringify(state.peaks.map(p => [p.center, p.fwhm, p.amplitude]));
state.fitResult = { be, chiReduced: 1.02, fittedY: be.map(x => 5000 * g(x, 285, 1.2)), _preFit: { 1: { center: 285.0, fwhm: 1.2, amplitude: 5000, glMix: 30 } },
  backendResult: { individual_peaks: [{ id: '1', params: { center: { value: 285.0, stderr: 0.002, vary: true, min: 283, max: 287 }, fwhm: { value: 1.2, stderr: 0.005, vary: true, min: 0.1, max: 15 }, amplitude: { value: 5000, stderr: 22, vary: true, min: 0, max: null } } }] } };
state.peaks[0].support = { f: 2e4, supported: true, fitKey: keyOf() };
const document = { getElementById: id => id === 'bg-type' ? { value: 'shirley' } : null };
const env = { state, document, getPeak: id => state.peaks.find(p => p.id === Number(id)), _startsLiveKey: keyOf,
  evalPeakArray: (xs, p) => xs.map(x => p.amplitude * g(x, p.center, p.fwhm)),
  _downloadBlob: (b) => { downloaded = b; }, notify: () => {}, Blob: class { constructor(parts) { this.text = parts.join(''); } },
  _pushUndoDebounced: () => {}, renderPeakControls: () => {}, updatePlot: () => {} };
const src = consts + '\n' + names.map(extractFn).join('\n') + '\nreturn { exportFitTable, updatePeakParam, _validateUncertainties };';
const f = new Function(...Object.keys(env), src)(...Object.values(env));
f.exportFitTable('csv');
console.log('--- CSV right after the fit:\n' + downloaded.text.split('\n').filter(l => /^#|C-C/.test(l)).join('\n'));
f.updatePeakParam(1, 'center', 287.4);   // student drags / types a new centre; nothing is refitted
f.updatePeakParam(1, 'fwhm', 2.5);
console.log('fitResult still present:', !!state.fitResult, ' fittedY:', state.fitResult.fittedY);
f.exportFitTable('csv');
console.log('--- CSV after editing centre 285.0 -> 287.4 and FWHM 1.2 -> 2.5 (no refit):\n' + downloaded.text.split('\n').filter(l => /^#|C-C/.test(l)).join('\n'));
console.log('uncertainty warnings after edit:', JSON.stringify(f._validateUncertainties()));
