const { extractFn, extractConst } = require('./lib.js');
const fits = require('./fits.json');
const src = [extractConst('_SUPPORT_MIN_F'), extractConst('_UNSUPPORTED_LABEL'),
  ...['_validateUncertainties','_buildStderrMap','_isUnsupported','_escHtml'].map(extractFn)].join('\n');
const shapeOf = { A_center_at_bound: 'GL', B_amp_to_zero: 'GL', C_ds: 'DS', D_dsg: 'DSG_LA', E_glratio: 'GL', F_lacx: 'LACX' };
for (const [k, r] of Object.entries(fits)) {
  const state = { peaks: r.individual_peaks.map(ip => ({ id: Number(ip.id), name: 'P' + ip.id, shape: shapeOf[k], support: null })) };
  state.fitResult = { backendResult: r, _preFit: {} };
  const f = new Function('state', 'getPeak', '_startsLiveKey', src + '\nreturn _validateUncertainties;')(state, id => state.peaks.find(p => p.id === id), () => 'K');
  const out = f();
  console.log(k, JSON.stringify(out.warnings.map(w => w.replace(/<[^>]+>/g, ''))));
}
