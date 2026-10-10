// Every fit's RECORD (owner 2026-10-10; recording only): the producers write it, the saves carry
// it, the spectrum loader restores it explicitly, and the export rows say what it holds.
// The behaviour is pinned in a real browser by tests/test_browser_fit_recording.py.
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
const H = new Function('document', ['_fitRecordFrom', '_pageSoftware', '_localFitRecord', '_isFitRecord', '_fitRecordRows'].map(extractFn).join('\n') +
  '\nreturn { _fitRecordFrom, _localFitRecord, _isFitRecord, _fitRecordRows };')(
  { querySelector: () => ({ getAttribute: () => JSON.stringify({ git_commit: 'b'.repeat(40), numerics: '2026-10-09' }) }) });

const SERVER = { fit_method: 'leastsq', random_seed: 0, seed_source: 'caller',
  background_verdict: { method: 'shirley', effect: { method: 'shirley', window: [0, 120], k: 3 }, check: 'defining_statement', converged: true, residual: 1.5e-13, reason: '' },
  certificate: { certified: true, restarts: 1, moved: false, optimiser_flag: true, centre_moves: [], largest_centre_move: { id: 1, ev: 0.0012 } },
  software: { git_commit: 'a'.repeat(40), git_dirty: false, python: '3.12.13', numpy: '2.4.4', scipy: '1.17.1', lmfit: '1.3.4', numerics: '2026-10-09', seed_derivation: 'xps-fit-seed-v2' } };

test('every producer writes the record: Run Fit, Auto-Fit, the local engine', () => {
  assert.match(extractFn('runFit'), /record: _fitRecordFrom\(backendResult\)/);
  assert.match(extractFn('applyAutoFitResult'), /record: _fitRecordFrom\(json\)/);
  assert.match(extractFn('runFitLocal'), /record: _localFitRecord\(certifyRestarts, /);
  assert.match(extractFn('_doSaveFit'), /record: _isFitRecord\(state\.fitResult\.record\) \? state\.fitResult\.record : null/);
  assert.match(extractFn('_doPublicationExport'), /_pngWithText\(blob, 'XPS-Fit-Record', JSON\.stringify\(rec\)\)/);
});

test('both saves carry it and the spectrum loader restores it explicitly (a seed of 0 is a seed)', () => {
  assert.match(extractFn('_doSaveSpectrum'), /record: _isFitRecord\(state\.fitResult\.record\) \? state\.fitResult\.record : null/);
  assert.match(extractFn('_doSaveProject'), /record: _isFitRecord\(t\.fitResult\.record\) \? t\.fitResult\.record : null/);
  assert.match(extractFn('_loadSpectrumFile'), /if \(_isFitRecord\(data\.statistics\.record\)\) fr\.record = data\.statistics\.record;/);
});

test('the record is copied from the server, field for field; a seed of 0 is kept', () => {
  const r = H._fitRecordFrom(SERVER);
  assert.deepStrictEqual(r, { engine: 'server', fitMethod: 'leastsq', seed: 0, seedSource: 'caller',
    backgroundVerdict: SERVER.background_verdict, certificate: SERVER.certificate, software: SERVER.software });
  assert.strictEqual(H._fitRecordFrom(null), null);
  assert.strictEqual(H._fitRecordFrom({ ...SERVER, random_seed: 1.5 }).seed, null, 'a non-integer seed is not recorded');
});

test('the export rows state what the record holds', () => {
  const rows = Object.fromEntries(H._fitRecordRows(H._fitRecordFrom(SERVER)));
  assert.deepStrictEqual(Object.keys(rows), ['Fit method', 'Random seed', 'Background check', 'Minimum certificate', 'Software', 'Fit record (JSON)']);
  assert.deepStrictEqual(JSON.parse(rows['Fit record (JSON)']), H._fitRecordFrom(SERVER), 'lossless');
  assert.strictEqual(rows['Fit method'], 'leastsq');
  assert.strictEqual(rows['Random seed'], '0 (caller)');
  assert.strictEqual(rows['Background check'], 'shirley: converged (defining statement, residual 1.50e-13), window 0-120, averaging 3');
  assert.strictEqual(rows['Minimum certificate'], 'certified, 1 restart, not moved, largest centre move 0.0012 eV (component 1), optimiser flag success');
  assert.match(rows['Software'], /^commit a{40}; numerics 2026-10-09; python 3\.12\.13, numpy 2\.4\.4, scipy 1\.17\.1, lmfit 1\.3\.4; seed xps-fit-seed-v2$/);
  const bg = Object.assign([1, 2], { converged: true, failure: null, bgType: 'shirley', effect: { method: 'shirley', window: [0, 2], k: 1 },
                                     certificate: { converged: true, residual: 2e-13, reason: '' } });
  const lrec = H._localFitRecord(2, true, [{ id: 1, ev: 0.000012345 }, { id: 2, ev: -0.5 }], bg);
  assert.deepStrictEqual(lrec.certificate, { certified: true, restarts: 2, moved: true, centre_moves: [{ id: 1, ev: 0.000012345 }, { id: 2, ev: -0.5 }],
                                             largest_centre_move: { id: 2, ev: -0.5 }, check: 'coordinate' });
  assert.deepStrictEqual(lrec.backgroundVerdict, { method: 'shirley', effect: { method: 'shirley', window: [0, 2], k: 1 },
                                                   check: 'page_certificate', converged: true, residual: 2e-13, reason: '' });
  // "moved" is what the engine says (the whole point), never inferred from the centres
  assert.strictEqual(H._localFitRecord(1, true, [{ id: 1, ev: 0 }], bg).certificate.moved, true);
  assert.strictEqual(H._localFitRecord(0, false, [{ id: 1, ev: 0 }], bg).certificate.moved, false);
  // an unmarked array is no verdict: unknown, not converged
  assert.strictEqual(H._localFitRecord(0, false, [], [1, 2]).backgroundVerdict.converged, null);
  assert.strictEqual(lrec.software.role, 'served_the_page');
  const local = Object.fromEntries(H._fitRecordRows(lrec));
  assert.strictEqual(local['Fit method'], 'local engine (local_lm)');
  assert.ok(!('Random seed' in local));
  assert.strictEqual(local['Minimum certificate'], 'certified, 2 restarts, moved, largest centre move -0.5 eV (component 2) (coordinate)');
  assert.deepStrictEqual(JSON.parse(local['Fit record (JSON)']), lrec, 'lossless: an unrounded move survives');
  assert.deepStrictEqual(H._fitRecordRows(null), []);
  assert.deepStrictEqual(H._fitRecordRows({ engine: 'other' }), []);
});
