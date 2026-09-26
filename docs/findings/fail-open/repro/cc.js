const { extractFn } = require('./lib.js');
const el = v => ({ value: v, style: {}, textContent: '' });
const dom = { 'cc-method': el('c1s'), 'cc-obs': el('286.10'), 'cc-lit': el('284.5'), 'cc-ref-field': el(), 'cc-target-field': el(),
  'roi-min': el('280'), 'roi-max': el('295'), 'bg-start': el('294'), 'bg-end': el('281'), 'cc-shift-display': el() };
const document = { getElementById: id => dom[id] };
const tab = { chargeVerified: false };   // just batch-propagated: shift copied from the source, marked unverified
const tabManager = { activeId: 1, _getTab: () => tab, _updateCCVerifiedUI: v => { tabManager.shown = v; } };
const state = { ccShift: 1.6, peaks: [{ center: 283.4 }] };
const noop = () => {};
const f = new Function('document', 'tabManager', 'state', '_getManualAnchors', '_invalidateBgCache', 'updatePlot', 'renderPeakList', '_refOnTabChange', '_refRepaint',
  extractFn('updateChargeCorrection') + extractFn('_onCCObsInput') + '\nreturn _onCCObsInput;')(document, tabManager, state, () => [], noop, noop, noop, undefined, undefined);
dom['cc-obs'].value = '';   // student clears the field to retype (an <input type=number> holding "286,1" also reads '')
f();
console.log('chargeVerified =', tab.chargeVerified, '| red mark hidden =', tabManager.shown === true, '| ccShift =', state.ccShift, '| method still', dom['cc-method'].value, '| peak centre now', state.peaks[0].center.toFixed(2));
