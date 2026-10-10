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
const H = new Function(['_fitRecordFrom', '_localFitRecord', '_isFitRecord', '_fitRecordRows'].map(extractFn).join('\n') +
  '\nreturn { _fitRecordFrom, _localFitRecord, _isFitRecord, _fitRecordRows };')();

const SERVER = { fit_method: 'leastsq', random_seed: 0, seed_source: 'caller',
  background_verdict: { method: 'shirley', effect: { method: 'shirley', window: [0, 120], k: 3 }, check: 'defining_statement', converged: true, residual: 1.5e-13, reason: '' },
  certificate: { certified: true, restarts: 1, moved: false, optimiser_flag: true, centre_moves: [], largest_centre_move: { id: 1, ev: 0.0012 } },
  software: { git_commit: 'a'.repeat(40), git_dirty: false, python: '3.12.13', numpy: '2.4.4', scipy: '1.17.1', lmfit: '1.3.4', seed_derivation: 'xps-fit-seed-v2' } };

test('every producer writes the record: Run Fit, Auto-Fit, the local engine', () => {
  assert.match(extractFn('runFit'), /record: _fitRecordFrom\(backendResult\)/);
  assert.match(extractFn('applyAutoFitResult'), /record: _fitRecordFrom\(json\)/);
  assert.match(extractFn('runFitLocal'), /record: _localFitRecord\(certifyRestarts, /);
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
  assert.deepStrictEqual(Object.keys(rows), ['Fit method', 'Random seed', 'Background check', 'Minimum certificate', 'Software']);
  assert.strictEqual(rows['Fit method'], 'leastsq');
  assert.strictEqual(rows['Random seed'], '0 (caller)');
  assert.strictEqual(rows['Background check'], 'shirley: converged (defining statement, residual 1.50e-13), window 0-120, averaging 3');
  assert.strictEqual(rows['Minimum certificate'], 'certified, 1 restart, not moved, largest centre move 0.0012 eV, optimiser flag success');
  assert.match(rows['Software'], /^commit a{40}; python 3\.12\.13, numpy 2\.4\.4, scipy 1\.17\.1, lmfit 1\.3\.4; seed xps-fit-seed-v2$/);
  const local = Object.fromEntries(H._fitRecordRows(H._localFitRecord(2, 'shirley')));
  assert.strictEqual(local['Fit method'], 'local engine (local_lm)');
  assert.ok(!('Random seed' in local) && !('Software' in local));
  assert.strictEqual(local['Minimum certificate'], 'certified, 2 restarts (coordinate)');
  assert.deepStrictEqual(H._fitRecordRows(null), []);
  assert.deepStrictEqual(H._fitRecordRows({ engine: 'other' }), []);
});
