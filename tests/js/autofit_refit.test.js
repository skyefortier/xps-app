// Auto-Fit refits after its charge shift (sealed-fit v6 Q8, owner 2026-10-12). The anchor fit decides
// the shift by its gates and is never published; the FINAL fit — the same model with every centre
// locked, in the corrected frame, on the window the shift selected — is what Auto-Fit shows. A final
// fit that fails, is discarded, or whose anchor no longer passes restores everything. The deployed
// page's runAutoFitC1sGraphite runs here with the server's job routes simulated; the real-browser
// measurement is docs/findings/q8-autofit-refit (scripts/q8_autofit_refit.py).
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
const lines = html.split('\n');
function extractFn(name) {
  const start = lines.findIndex(l => new RegExp('^(async )?function ' + name + '\\(').test(l));
  assert.ok(start >= 0, name);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail('unbalanced ' + name);
}
const constLine = n => { const l = lines.find(x => x.startsWith('const ' + n)); assert.ok(l, n); return l; };
const POLL_SRC = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
  'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap(); let _fitSpinnerOp = null;',
  ...['_cancelFitJob', '_fitHttpError', '_newFitOp', '_installFitOp', '_claimFitOp', '_fitOpOutdated', '_fitOpCurrent', '_hideFitSpinnerFor', '_serverFitJob'].map(extractFn),
  'const _noteServerSoftware = () => {};   // owner 2026-10-15: the verdict cache\'s numerics (not exercised here)'].join('\n');
const KEY_SRC = lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\n' + lines.find(l => l.startsWith('const _SEAL_CTX_FIELDS')) + '\n' + lines.find(l => l.startsWith('const LEGACY_ENDPOINT_AVG'));

// replies: one per fit, in order; hooks: per-upload side effects (1-based)
async function runAutoFit({ replies, refuseFinal = false, refuseAnchor = false, onUpload = {} }) {
  const state = { peaks: [], ccShift: 0, rawBE: [285, 284.5, 284], rawIntensity: [10, 20, 10] };
  const dom = {};
  const document = { getElementById: id => (dom[id] ??= { value: ({ 'bg-type': 'none', 'bg-start': '285', 'bg-end': '284', 'bg-endpoint-avg': '3', 'fit-method': 'leastsq' })[id] || '', style: {}, textContent: '', setAttribute() {}, classList: { add() {}, remove() {} } }), querySelector: () => ({}) };
  const tab = { id: 1 };
  const out = { restored: false, applied: [], published: [], uploads: [], notes: [], refusalOf: [], labels: [] };
  let n = 0, fetched = 0;
  const label = { set textContent(v) { out.labels.push(v); } };
  const deps = { state, document: { ...document, getElementById: id => (id === 'fit-spinner-label' ? label : document.getElementById(id)) },
    tabManager: { activeId: 1, _getTab: () => tab, _captureUI: () => ({ bgType: document.getElementById('bg-type').value, roiMin: '284', roiMax: '285' }), _syncActiveToRecord() {} },
    notify: (m, k) => out.notes.push([m, k]), _opOwner: () => tab, _ownerActive: () => true, isC1sTab: () => true,
    _autoFitSnapshot: () => ({}), _autoFitRestore: () => { out.restored = true; }, _flushUndoDebounce() {}, _showAutoFitConfirmModal: async () => true,
    getROIData: () => ({ be: state.rawBE.map(b => b - state.ccShift), inten: state.rawIntensity }),
    computeBackground: be => Object.assign(be.map(() => 0), { converged: true }),
    findGraphiteRawBE: () => 284.5, assessLowBERegion: () => ({}), pushUndo() {}, updateChargeCorrection() {},
    buildAutoFitModel: () => [{ id: 1, name: 'Graphite', shape: 'Gaussian', center: 284.5, fwhm: 1, amplitude: 20 }],
    renderPeakList() {}, _showFitSpinner() {}, _hideFitSpinner() {}, AbortController, setTimeout: () => 1, clearTimeout() {},
    peakToBackendSpec: p => ({ ...p }), _getManualAnchors: () => [],
    uploadToBackend: async (be) => { n++; out.uploads.push({ be, ccShift: state.ccShift, locked: state.peaks.every(p => p.fixCenter) }); if (onUpload[n]) onUpload[n](document); return 'sid' + n; },
    fetch: async () => { const r = replies[fetched++]; return { text: async () => JSON.stringify(r) }; },
    applyBackendResult: j => { out.applied.push(j.tag); },
    // the anchor fit's gates and shift: the frame moves by 0.2 eV and every centre is locked
    applyAutoFitResult: j => { if (refuseAnchor) return false; out.shiftedBy = j.tag; state.ccShift = 0.2; for (const p of state.peaks) p.fixCenter = true; return true; },
    _autoFitAnchorRefusal: j => { out.refusalOf.push(j.tag); return refuseFinal ? 'Auto-fit: the data do not support the Graphite component.' : null; },
    _autoFitPublish: j => { out.published.push(j.tag); state.fitResult = { chiReduced: j.statistics.reduced_chi_square }; return true; },
    _autoFitBusyBegin: () => { out.busy = (out.busy || 0) + 1; }, _autoFitBusyLabel: t => out.labels.push(t), _autoFitBusyEnd: () => { out.busyEnded = (out.busyEnded || 0) + 1; },
    console: { warn() {} } };
  // the poll routes answer from the reply of the last start
  const inner = deps.fetch; let reply = null;
  deps.fetch = async (url, init) => {
    if (url === '/api/fit/start') { reply = await inner(url, init); return { ok: true, status: 202, text: async () => JSON.stringify({ job_id: 'job' }) }; }
    if (url.startsWith('/api/fit/progress/')) return { ok: true, status: 200, text: async () => '{"status": "done", "result": ' + (await reply.text()) + '}' };
    if (url.startsWith('/api/fit/cancel/')) return { ok: true, status: 200, json: async () => ({}) };
    return inner(url, init);
  };
  deps.setTimeout = (f, ms) => { if (!(ms >= 60000)) f(); return 1; };
  deps.DOMException = class extends Error { constructor(m, k) { super(m); this.name = k; } };
  const src = KEY_SRC + '\n' + ['runAutoFitC1sGraphite', '_autoFitRequest', '_buildFitRequest', '_liveFitContext', '_contextOf', '_uiFromDom', '_sealR', '_makeSeal', '_deepFreeze', '_pageIdentity', 'BgNotConverged', '_isBgNotConverged', '_bgOrFailure', '_endpointAvgFailure', '_readFitReply',
    '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
  await new Function(...Object.keys(deps), src + '\n' + POLL_SRC + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
  // the page waits for exactly this one transaction: the overlay goes up once and comes down once, on every exit
  assert.strictEqual(out.busy, 1, 'the overlay is shown once');
  assert.strictEqual(out.busyEnded, 1, 'and taken down once');
  return out;
}
const OK = (tag, chi) => ({ tag, success: true, statistics: { reduced_chi_square: chi }, fitted_y: [10, 20, 10], residuals: [0, 0, 0] });

test('the anchor fit decides the shift; the FINAL fit, in the corrected frame with the centres locked, is the one published', async () => {
  const out = await runAutoFit({ replies: [OK('A', 3.0), OK('B', 2.0)] });
  assert.deepStrictEqual(out.applied, ['A', 'B']);
  assert.strictEqual(out.shiftedBy, 'A', 'the shift is derived from the anchor fit');
  assert.deepStrictEqual(out.refusalOf, ['B'], 'the final fit\'s anchor is held to the same gates');
  assert.deepStrictEqual(out.published, ['B'], 'only the final fit is published');
  assert.strictEqual(out.uploads.length, 2);
  assert.deepStrictEqual([out.uploads[0].ccShift, out.uploads[1].ccShift], [0, 0.2], 'the final fit is made on the shifted window');
  assert.deepStrictEqual(out.uploads[1].be, [285, 284.5, 284].map(b => b - 0.2));
  assert.strictEqual(out.uploads[1].locked, true, 'with every centre locked');
  assert.ok(out.labels.includes('Auto-Fit: anchor fitted, refitting in the corrected frame…'), JSON.stringify(out.labels));
  assert.strictEqual(out.restored, false);
  assert.ok(out.notes.some(([m, k]) => k === 'green' && /^Auto-fit complete\. χ²ᵣ = 2\.000$/.test(m)), JSON.stringify(out.notes));
});

test('a final fit that does not converge restores everything; nothing is published', async () => {
  const out = await runAutoFit({ replies: [OK('A', 3.0), { tag: 'B', success: false, message: 'evaluation budget exhausted' }] });
  assert.deepStrictEqual(out.published, []);
  assert.strictEqual(out.restored, true);
  assert.ok(out.notes.some(([m, k]) => k === 'red' && /^Auto-fit not applied: the final fit in the corrected frame did not converge \(evaluation budget exhausted\)\. Previous peaks and result restored\.$/.test(m)), JSON.stringify(out.notes));
});

test('a final fit whose anchor no longer passes restores everything, with the reason', async () => {
  const out = await runAutoFit({ replies: [OK('A', 3.0), OK('B', 2.0)], refuseFinal: true });
  assert.deepStrictEqual(out.published, []);
  assert.strictEqual(out.restored, true);
  assert.ok(out.notes.some(([m, k]) => k === 'red' && /^After the refit in the corrected frame — Auto-fit: the data do not support the Graphite component\.$/.test(m)), JSON.stringify(out.notes));
});

test('a model edited while the final fit runs: discarded and restored, like the anchor fit', async () => {
  const out = await runAutoFit({ replies: [OK('A', 3.0), OK('B', 2.0)], onUpload: { 2: doc => { doc.getElementById('bg-type').value = 'linear'; } } });
  assert.deepStrictEqual(out.applied, ['A']);
  assert.deepStrictEqual(out.published, []);
  assert.strictEqual(out.restored, true);
  assert.ok(out.notes.some(([m, k]) => k === 'amber' && /edited while it was running/.test(m)), JSON.stringify(out.notes));
});

test('an anchor fit the gates refuse makes no second fit', async () => {
  const out = await runAutoFit({ replies: [OK('A', 3.0), OK('B', 2.0)], refuseAnchor: true });
  assert.strictEqual(out.uploads.length, 1, 'no final fit');
  assert.deepStrictEqual(out.published, []);
  assert.strictEqual(out.restored, true);
});
