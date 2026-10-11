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
const H = new Function('document', ['_fitRecordFrom', '_pageSoftware', '_localFitRecord', '_isFitRecord', '_fitRecordRows', '_fitRecordTextLines', '_b64Utf8', '_recordParts', '_fitRecordXlsxRows'].map(extractFn).join('\n') +
  '\nreturn { _fitRecordFrom, _localFitRecord, _isFitRecord, _fitRecordRows, _fitRecordTextLines, _fitRecordXlsxRows, _recordParts };')(
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

const BAD = 'a, "b"\tc\r\nd ≥ é 😀';   // every character a reader splits or quotes on, and non-ASCII
const reassemble = (lines, label) => lines.filter(l => l.startsWith(label)).map(l => l.slice(l.indexOf('): ') + 3)).join('');

test('the CSV / TSV tail: every line one cell to any reader, a comment, and the JSON lossless', () => {
  // the adversarial text in fields the SUMMARY lines print (component id, software strings,
  // the background method) — and in the base64-only reason (Codex recording round 5)
  const rec = H._fitRecordFrom({ ...SERVER,
    background_verdict: { ...SERVER.background_verdict, method: BAD, converged: false, reason: BAD },
    certificate: { ...SERVER.certificate, largest_centre_move: { id: BAD, ev: 0.5 } },
    software: { ...SERVER.software, git_commit: BAD, python: BAD, numerics: BAD } });
  const summary = Object.fromEntries(H._fitRecordRows(rec).slice(0, -1));
  for (const k of ['Background check', 'Minimum certificate', 'Software']) assert.ok(/[,"\t\r\n]/.test(summary[k]), k + ' carries the text');
  const lines = H._fitRecordTextLines(rec);
  assert.strictEqual(lines.length, 6);
  for (const l of lines) {
    assert.ok(l.startsWith('# '), l);
    assert.ok(!/[,"\t\r\n]/.test(l), 'no delimiter, quote or line break: ' + l);
  }
  assert.ok(lines.every(l => !l.includes('Fit record') || l.startsWith('# Fit record (JSON base64 part 1 of 1): ')));
  const b64 = reassemble(lines, '# Fit record (JSON base64 part ');
  assert.deepStrictEqual(JSON.parse(Buffer.from(b64, 'base64').toString('utf8')), rec, 'lossless, UTF-8');
  assert.strictEqual(lines[0], '# Fit method: leastsq');
  assert.deepStrictEqual(H._fitRecordTextLines(null), []);
});

test('a record of any size: every line and cell within every reader\'s limit, the parts reassemble losslessly', () => {
  // Codex round 5: 4 000 manual anchors made one 207 352-character line (Python csv refuses
  // fields over 131 072) and a 155 491-character cell (Excel holds 32 767)
  const anchors = Array.from({ length: 4000 }, (_, i) => [280 + i * 0.0025, 1000 + i / 7]);
  const rec = H._fitRecordFrom({ ...SERVER, background_verdict: { ...SERVER.background_verdict, method: 'manual',
    effect: { method: 'manual', anchors } } });
  rec.backgroundVerdict.reason = BAD.repeat(500);    // surrogate pairs across part boundaries
  const lines = H._fitRecordTextLines(rec);
  const parts = lines.filter(l => l.startsWith('# Fit record (JSON base64 part '));
  assert.ok(parts.length > 1, 'split: ' + parts.length);
  parts.forEach((l, i) => assert.ok(l.startsWith(`# Fit record (JSON base64 part ${i + 1} of ${parts.length}): `), l.slice(0, 60)));
  for (const l of lines) assert.ok(l.length <= 32767 && !/[,"\t\r\n]/.test(l), l.length);
  assert.deepStrictEqual(JSON.parse(Buffer.from(reassemble(parts, '# Fit record'), 'base64').toString('utf8')), rec);
  const cells = H._fitRecordXlsxRows(rec).filter(([k]) => k.startsWith('Fit record (JSON part '));
  assert.ok(cells.length > 1);
  cells.forEach(([k, v], i) => { assert.strictEqual(k, `Fit record (JSON part ${i + 1} of ${cells.length})`); assert.ok(v.length <= 32767, v.length); });
  assert.deepStrictEqual(JSON.parse(cells.map(([, v]) => v).join('')), rec, 'the XLSX parts are the JSON');
  // a part boundary never splits a surrogate pair
  for (const [, v] of cells) assert.ok(!/^[\udc00-\udfff]|[\ud800-\udbff]$/.test(v));
  assert.deepStrictEqual(H._recordParts(''), ['']);
});

test('a summary value of any length is cut within every reader\'s limit; the JSON keeps it whole (Codex round 6)', () => {
  const longId = 'z'.repeat(140000), longPy = 'p'.repeat(40000);
  const rec = H._fitRecordFrom({ ...SERVER, certificate: { ...SERVER.certificate, largest_centre_move: { id: longId, ev: 0.5 } },
                                 software: { ...SERVER.software, python: longPy } });
  for (const l of H._fitRecordTextLines(rec)) assert.ok(l.length <= 32767 && !/[,"\t\r\n]/.test(l), l.length);
  for (const [k, v] of H._fitRecordXlsxRows(rec)) assert.ok(String(v).length <= 32767, k + ' ' + String(v).length);
  const summary = Object.fromEntries(H._fitRecordRows(rec));
  assert.match(summary['Minimum certificate'], / … \(cut here; the fit record JSON holds it whole\)$/);
  assert.match(summary['Software'], / … \(cut here; the fit record JSON holds it whole\)$/);
  const json = H._fitRecordXlsxRows(rec).filter(([k]) => k.startsWith('Fit record (JSON part ')).map(([, v]) => v).join('');
  assert.strictEqual(JSON.parse(json).certificate.largest_centre_move.id, longId, 'whole in the record');
  assert.strictEqual(JSON.parse(json).software.python, longPy);
  // an ordinary summary is not cut
  assert.ok(!Object.values(Object.fromEntries(H._fitRecordRows(H._fitRecordFrom(SERVER)))).some(v => v.includes('cut here')));
});

test('a part boundary falling on a surrogate pair keeps the pair whole (Codex round 6)', () => {
  const E = '😀';
  assert.deepStrictEqual(H._recordParts('x'.repeat(15999) + E + 'y'), ['x'.repeat(15999) + E, 'y']);
  assert.deepStrictEqual(H._recordParts('x'.repeat(16000) + E), ['x'.repeat(16000), E]);
  // the summary's cut, likewise
  const rec = H._fitRecordFrom({ ...SERVER, certificate: { ...SERVER.certificate, largest_centre_move: { id: 'x'.repeat(5000), ev: 0.5 } } });
  const pre = 'certified, 1 restart, not moved, largest centre move 0.5 eV (component ';
  rec.certificate.largest_centre_move.id = 'x'.repeat(2000 - pre.length - 1) + E + 'tail';
  const cut = Object.fromEntries(H._fitRecordRows(rec))['Minimum certificate'];
  assert.ok(cut.startsWith(pre) && cut.includes(E + ' … (cut here'), cut.slice(1990, 2010));
});
