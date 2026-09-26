const { extractFn } = require('./lib.js');
const f = new Function(extractFn('isC1sTab') + extractFn('findGraphiteRawBE') + '\nreturn {isC1sTab, findGraphiteRawBE};')();
// wide scan 270-420 eV: C 1s (284.8, small) + U 4f7/2 380.9, 4f5/2 391.8 (large)
const be = []; for (let v = 420; v >= 270; v -= 0.1) be.push(+v.toFixed(2));
const g = (x, c, w, a) => a * Math.exp(-((x - c) ** 2) / (2 * (w / 2.3548) ** 2));
const I = be.map(x => g(x, 284.8, 1.2, 800) + g(x, 380.9, 1.8, 9000) + g(x, 391.8, 1.8, 7000));
// record ui as of activation: C 1s window
const tab = { rawBE: be, ui: { roiMin: '280', roiMax: '295' } };
console.log('record ui 280-295 -> isC1sTab =', f.isC1sTab(tab));
// user now types 370-415 in the live fields; tab.ui is NOT updated by oninput -> gate unchanged
console.log('live ROI 370-415 but record ui unchanged -> isC1sTab =', f.isC1sTab(tab));
// what Auto-Fit then sees (getROIData on the LIVE fields)
const sel = be.map((b, i) => [b, I[i]]).filter(([b]) => b >= 370 && b <= 415);
const graphiteRaw = f.findGraphiteRawBE(sel.map(s => s[0]), sel.map(s => s[1]));
console.log('findGraphiteRawBE on live window =', graphiteRaw, '-> provisional shift', (graphiteRaw - 284.5).toFixed(2), 'eV');
// typed-window vs selected-window (plan row 10), with live ui synced: data 300-420, ROI typed 200-420
const be2 = be.filter(b => b >= 300);
console.log('data 300-420, ROI typed 200-420 -> isC1sTab =', f.isC1sTab({ rawBE: be2, ui: { roiMin: '200', roiMax: '420' } }));
