// Unit 2 (2026-09-27): Run Fit and Auto-Fit start the fit and poll for it
// (_serverFitJob). Pinned: the result is the /api/fit body; a bad request's
// message and status are the synchronous route's; ownership (a switched tab,
// an edited model) cancels the server's job and discards; transport keeps its
// meaning (a START that cannot reach the server may fall back to the local
// engine; one lost poll does not; five in a row do); a lost heartbeat, a
// cancelled or errored record are failed fits; F2's NaN rule applies to the
// final record; the 2-minute Auto-Fit abort cancels the job.
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
const lines = html.split('\n');
function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name + '\\(');
  const start = lines.findIndex(l => re.test(l));
  assert.ok(start >= 0, `function ${name} not found`);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail('unbalanced ' + name);
}
const constLine = n => { const l = lines.find(x => x.startsWith('const ' + n)); assert.ok(l, n); return l; };

// fetch scripted by URL; every call recorded
function server(script) {
  const calls = [];
  const fetch = async (url, init) => {
    calls.push({ url, method: (init && init.method) || 'GET' });
    const h = script(url, init, calls);
    if (h instanceof Error) throw h;
    return h;
  };
  return { fetch, calls };
}
const ok = (obj, status = 200) => ({ ok: true, status, text: async () => (typeof obj === 'string' ? obj : JSON.stringify(obj)) });
const bad = (status, obj) => ({ ok: false, status, json: async () => { if (obj === undefined) throw new SyntaxError('x'); return obj; } });

function make(fetch) {
  const src = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
    'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap(); let _fitSpinnerOp = null;',
    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_newFitOp'), extractFn('_installFitOp'), extractFn('_claimFitOp'), extractFn('_fitOpCurrent'),
    extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
  return new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob, _runningFitJobs, _claimFitOp };')(
    fetch, f => f(), class extends Error { constructor(m, n) { super(m); this.name = n; } });
}
const START = '/api/fit/start';
const isProgress = u => u.startsWith('/api/fit/progress/');
const isCancel = u => u.startsWith('/api/fit/cancel/');

test('start -> running polls -> done: the result is the /api/fit body; no job is left registered', async () => {
  let n = 0;
  const s = server(u => u === START ? ok({ job_id: 'J' }, 202)
    : isProgress(u) ? (++n < 3 ? ok({ status: 'running', heartbeat_age_sec: 0.4 }) : ok({ status: 'done', result: { success: true, x: 1 } }))
    : ok({}));
  const { _serverFitJob, _runningFitJobs } = make(s.fetch);
  assert.deepStrictEqual(await _serverFitJob({ a: 1 }, {}), { success: true, x: 1 });
  assert.strictEqual(s.calls.filter(c => isProgress(c.url)).length, 3);
  assert.strictEqual(_runningFitJobs.size, 0);
  assert.ok(!s.calls.some(c => isCancel(c.url)), 'a finished job is not cancelled');
});

test('a bad request: the synchronous route\'s message and status, immediately; no poll', async () => {
  const s = server(u => u === START ? bad(400, { error: 'n_perturb must be between 0 and 10' }) : assert.fail(u));
  const { _serverFitJob } = make(s.fetch);
  await assert.rejects(_serverFitJob({}, {}), e => e.serverError && e.httpStatus === 400 && /n_perturb must be between/.test(e.message));
});

test('a START that cannot reach the server is a transport failure (the caller may fall back to the local engine)', async () => {
  const s = server(u => new TypeError('Failed to fetch'));
  const { _serverFitJob } = make(s.fetch);
  await assert.rejects(_serverFitJob({}, {}), e => e.transportFailure === true && !e.serverError);
});

test('an error record is a failed fit with the synchronous message and status', async () => {
  const s = server(u => u === START ? ok({ job_id: 'J' }, 202)
    : ok({ status: 'error', http_status: 400, error: 'The model is not determined by these data: 8 free parameters for 6 data points' }));
  const { _serverFitJob } = make(s.fetch);
  await assert.rejects(_serverFitJob({}, {}), e => e.serverError && e.httpStatus === 400 && /not determined by these data/.test(e.message));
});

test('a done record carrying NaN is F2\'s failed fit (unreadable reply), not a transport failure', async () => {
  const s = server(u => u === START ? ok({ job_id: 'J' }, 202)
    : isProgress(u) ? ok('{"status": "done", "result": {"success": true, "s": NaN}}') : ok({}));
  const { _serverFitJob } = make(s.fetch);
  await assert.rejects(_serverFitJob({}, {}), e => e.unreadableReply === true && e.serverError && !e.transportFailure && /non-finite/.test(e.message));
});

test('one lost poll is retried; five in a row are a transport failure and cancel the job', async () => {
  let n = 0;
  const flaky = server(u => u === START ? ok({ job_id: 'J' }, 202)
    : isProgress(u) ? (++n <= 4 ? new TypeError('network') : ok({ status: 'done', result: { success: true } })) : ok({}));
  assert.deepStrictEqual(await make(flaky.fetch)._serverFitJob({}, {}), { success: true });
  const dead = server(u => u === START ? ok({ job_id: 'J' }, 202) : isProgress(u) ? new TypeError('network') : ok({}));
  await assert.rejects(make(dead.fetch)._serverFitJob({}, {}), e => e.transportFailure === true && /Lost contact/.test(e.message));
  assert.ok(dead.calls.some(c => isCancel(c.url) && c.method === 'POST'), 'the server is told to stop');
});

test('a stopped heartbeat (restarted worker) is a failed fit, never an endless spinner', async () => {
  const s = server(u => u === START ? ok({ job_id: 'J' }, 202) : isProgress(u) ? ok({ status: 'running', heartbeat_age_sec: 45 }) : ok({}));
  await assert.rejects(make(s.fetch)._serverFitJob({}, {}), e => e.serverError && /stopped working on the fit/.test(e.message));
});

test('a job cancelled on the server (abandoned) is reported, not waited for', async () => {
  const s = server(u => u === START ? ok({ job_id: 'J' }, 202) : ok({ status: 'cancelled' }));
  await assert.rejects(make(s.fetch)._serverFitJob({}, {}), e => e.serverError && /stopped on the server/.test(e.message));
});

test('ownership inside the loop: a switched tab or an edited model cancels the job and returns the reason', async () => {
  for (const reason of ['tab', 'model']) {
    let polls = 0;
    const s = server(u => u === START ? ok({ job_id: 'J' }, 202) : isProgress(u) ? (polls++, ok({ status: 'running', heartbeat_age_sec: 0 })) : ok({}));
    let t = 0;
    const out = await make(s.fetch)._serverFitJob({}, { abandoned: () => (++t > 2 ? reason : null) });
    assert.deepStrictEqual(out, { _abandoned: reason });
    assert.ok(s.calls.some(c => isCancel(c.url) && c.method === 'POST'), reason + ': the server is told to stop');
    assert.strictEqual(polls, 2, 'no poll after the model or tab changed');
  }
});

test('the Auto-Fit abort (2 minutes) cancels the job and surfaces as an AbortError', async () => {
  const ctrl = { aborted: false, reason: null };
  let polls = 0;
  const s = server(u => u === START ? ok({ job_id: 'J' }, 202) : isProgress(u) ? (++polls === 2 && (ctrl.aborted = true, ctrl.reason = Object.assign(new Error('timeout'), { name: 'AbortError' })), ok({ status: 'running', heartbeat_age_sec: 0 })) : ok({}));
  await assert.rejects(make(s.fetch)._serverFitJob({}, { signal: ctrl }), e => e.name === 'AbortError');
  assert.ok(s.calls.some(c => isCancel(c.url)));
});

test('Run Fit and Auto-Fit both go through _serverFitJob; nothing on the page posts to the synchronous /api/fit any more', () => {
  assert.match(extractFn('runFit'), /await _serverFitJob\(fitReq, \{/);
  assert.match(extractFn('runAutoFitC1sGraphite'), /await _serverFitJob\(\{/);
  assert.ok(!/fetch\('\/api\/fit'/.test(html), 'no synchronous /api/fit fetch left');
  // the ownership reasons are the ones the discard messages handle
  for (const fn of ['runFit', 'runAutoFitC1sGraphite']) {
    const src = extractFn(fn);
    assert.match(src, /_abandoned === 'tab'/, fn);
    assert.match(src, /_abandoned === 'model'/, fn);
  }
  assert.match(html, /addEventListener\('pagehide'/, 'a closed page cancels its running fits');
});

// Round 2: ownership is an OPERATION claimed before the caller's first await
// (_claimFitOp); the newest claim for a tab is current whatever order the
// server's responses arrive in, and a superseded operation returns
// { _abandoned: 'superseded' } at every step after an await and before every
// exit (a result, an error, a timeout).
function makeAsync(fetch) {
  const src = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
    'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap(); let _fitSpinnerOp = null;',
    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_newFitOp'), extractFn('_installFitOp'), extractFn('_claimFitOp'), extractFn('_fitOpCurrent'),
    extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
  return new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob, _claimFitOp };')(
    fetch, f => { setImmediate(f); return 0; }, class extends Error {});   // yield to the event loop between polls
}
const deferred = () => { let res; const p = new Promise(r => { res = r; }); return { p, res }; };

test('the NEWEST claim is current whatever order the start responses arrive in (Codex round 2)', async () => {
  const calls = [];
  const aStart = deferred();
  let n = 0;
  const fetch = async (url, init) => {
    calls.push({ url, method: (init && init.method) || 'GET' });
    if (url === '/api/fit/start') {
      const id = 'J' + (++n);
      if (id === 'J1') await aStart.p;                 // A's start response is delayed
      return ok({ job_id: id }, 202);
    }
    if (url.startsWith('/api/fit/progress/')) return ok({ status: 'done', result: { which: url.split('/').pop() } });
    return ok({});
  };
  const { _serverFitJob, _claimFitOp } = makeAsync(fetch);
  const owner = { id: 'tab-1' };
  const opA = _claimFitOp(owner);                      // A pressed first
  const a = _serverFitJob({}, { op: opA });
  await new Promise(r => setImmediate(r));
  const opB = _claimFitOp(owner);                      // B pressed second
  const b = _serverFitJob({}, { op: opB });
  assert.deepStrictEqual(await b, { which: 'J2' }, 'B, the newer, gets its result');
  aStart.res();
  assert.deepStrictEqual(await a, { _abandoned: 'superseded' }, 'A, older, is superseded though its response came last');
  assert.ok(calls.some(c => c.url === '/api/fit/cancel/J1' && c.method === 'POST'), "A's late job is cancelled by A itself");
  assert.ok(!calls.some(c => c.url === '/api/fit/cancel/J2'), "B's job is never cancelled");
});

test('a poll in flight when a newer claim arrives: its reply is never applied, never an error (Codex round 2)', async () => {
  for (const late of [{ status: 'done', result: { stale: true } }, { status: 'cancelled' }, { status: 'error', http_status: 500, error: 'x' }]) {
    const calls = [];
    const polled = deferred();
    const release = deferred();
    const fetch = async (url, init) => {
      calls.push({ url, method: (init && init.method) || 'GET' });
      if (url === '/api/fit/start') return ok({ job_id: 'J1' }, 202);
      if (url.startsWith('/api/fit/progress/')) { polled.res(); await release.p; return ok(late); }
      return ok({});
    };
    const { _serverFitJob, _claimFitOp } = makeAsync(fetch);
    const owner = { id: 'tab-1' };
    const a = _serverFitJob({}, { op: _claimFitOp(owner) });
    await polled.p;                                    // A's poll is in flight
    _claimFitOp(owner);                                // B claims the tab
    release.res();                                     // A's late reply arrives
    assert.deepStrictEqual(await a, { _abandoned: 'superseded' }, late.status);
    assert.ok(calls.some(c => c.url === '/api/fit/cancel/J1'), late.status + ': the newer claim cancelled A');
  }
});

test('an Auto-Fit timeout after a newer claim is superseded, not a timeout (Codex round 2)', async () => {
  const signal = { aborted: false, reason: null };
  const polled = deferred();
  const release = deferred();
  const fetch = async (url) => {
    if (url === '/api/fit/start') return ok({ job_id: 'J1' }, 202);
    if (url.startsWith('/api/fit/progress/')) { polled.res(); await release.p; signal.aborted = true;
      signal.reason = Object.assign(new Error('timeout'), { name: 'AbortError' }); throw signal.reason; }
    return ok({});
  };
  const { _serverFitJob, _claimFitOp } = makeAsync(fetch);
  const owner = {};
  const a = _serverFitJob({}, { op: _claimFitOp(owner), signal });
  await polled.p;
  _claimFitOp(owner);
  release.res();
  assert.deepStrictEqual(await a, { _abandoned: 'superseded' });
});

test('both callers claim their operation before the first await and do nothing at all when superseded', () => {
  const run = extractFn('runFit');
  assert.ok(run.indexOf('fitOp = _claimFitOp(fittingTab);') > 0 && run.indexOf('fitOp = _claimFitOp(fittingTab);') < run.indexOf('await uploadToBackend('), 'runFit claims before its first await');
  assert.ok(!/\bawait\s+[\w(]/.test(run.slice(0, run.indexOf('fitOp = _claimFitOp(fittingTab);')).replace(/\/\/[^\n]*/g, '')), 'no code await before the claim');
  assert.match(run, /op: fitOp,/);
  assert.match(run, /if \(json && json\._abandoned === 'superseded'\) return;/);
  assert.match(run, /\} catch \(e\) \{\n(\s*\/\/[^\n]*\n)*\s*if \(fitOp && !_fitOpCurrent\(fitOp\)\) return;/, 'runFit: a superseded operation never reaches the local fallback');
  const af = extractFn('runAutoFitC1sGraphite');
  const num = af.indexOf('const afOp = _newFitOp(fittingTab);');
  assert.ok(num > 0 && num < af.indexOf('await _showAutoFitConfirmModal('), 'Auto-Fit numbers its operation before its FIRST await (the modal)');
  const outdated = af.indexOf('if (_fitOpOutdated(afOp)) return;');
  assert.ok(outdated > af.indexOf('await _showAutoFitConfirmModal(') && outdated < af.indexOf('_autoFitSnapshot()'),
    'after the modal it steps aside for a newer operation before anything is done');
  const inst = af.indexOf('if (!_installFitOp(afOp)) return;');
  // round 5: installed only AFTER the preflight refusals (installing cancels a running fit on the tab)
  assert.ok(inst > af.indexOf("notify('ROI is empty.") && inst > af.indexOf("notify('No strong peak found"), 'installed after every preflight refusal');
  assert.ok(inst < af.indexOf('pushUndo();') && inst < af.indexOf('_showFitSpinner();') && inst < af.indexOf('await uploadToBackend('),
    'and before anything is changed, shown or sent');
  assert.ok(!/\bawait\s+[\w(]/.test(af.slice(outdated, inst).replace(/\/\/[^\n]*/g, '')), 'no await between the check and the install');
  assert.match(af, /op: afOp,/);
  assert.match(af, /if \(json && json\._abandoned === 'superseded'\) return;/);
  assert.match(af, /if \(afOp && !_fitOpCurrent\(afOp\)\) return;/, 'Auto-Fit: no rollback when superseded');
});

const AF_FNS = ['_cancelFitJob', '_fitHttpError', '_newFitOp', '_installFitOp', '_claimFitOp', '_fitOpOutdated', '_fitOpCurrent', '_hideFitSpinnerFor',
  '_readFitReply', '_serverFitJob', 'runAutoFitC1sGraphite', '_bgFailure', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'];
test('the Auto-Fit modal race: a Run Fit pressed while the confirmation is open WINS; the confirmed Auto-Fit changes nothing (Codex round 3)', async () => {
  const constants = lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n');
  const modal = deferred();
  const tab = { id: 't1' };
  const out = { starts: 0, restored: 0, snapshots: 0, applied: 0, cancels: [] };
  const state = { peaks: [{ id: 1 }], ccShift: 0, rawBE: [285, 284.5, 284], rawIntensity: [10, 20, 10] };
  const deps = {
    state, tabManager: { activeId: 't1', _getTab: () => tab, _captureUI: () => ({}) },
    document: { getElementById: () => ({ value: '', style: {}, setAttribute() {}, classList: { add() {}, remove() {} } }) },
    notify() {}, _opOwner: () => tab, _ownerActive: () => true, isC1sTab: () => true,
    _showAutoFitConfirmModal: () => modal.p, _autoFitSnapshot: () => { out.snapshots++; return {}; }, _autoFitRestore: () => { out.restored++; },
    fetch: async (u, i) => { if (u === '/api/fit/start') out.starts++; if (u.startsWith('/api/fit/cancel/')) out.cancels.push(u); return ok({ job_id: 'X' }, 202); },
    applyBackendResult: () => { out.applied++; }, _showFitSpinner() {}, _hideFitSpinner() {}, setTimeout, clearTimeout, AbortController, DOMException: Error,
    getROIData: () => ({ be: state.rawBE, inten: state.rawIntensity }), computeBackground: be => be.map(() => 0), findGraphiteRawBE: () => 284.5,
    uploadToBackend: async () => 'sid', pushUndo() {}, buildAutoFitModel: () => [], renderPeakList() {}, peakToBackendSpec: p => p, _getManualAnchors: () => [],
  };
  const src = constants + '\n' + [
    'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap(); let _fitSpinnerOp = null;',
    ...AF_FNS.map(extractFn)].join('\n');
  const api = new Function(...Object.keys(deps), src + '\nreturn { runAutoFitC1sGraphite, _claimFitOp, _fitOpCurrent };')(...Object.values(deps));
  const af = api.runAutoFitC1sGraphite();             // Auto-Fit pressed: the modal is open
  await new Promise(r => setImmediate(r));
  const runFitOp = api._claimFitOp(tab);              // Run Fit pressed (Ctrl/Cmd+F) while the modal is open
  modal.res(true);                                    // the student confirms Auto-Fit
  await af;
  assert.strictEqual(out.snapshots, 0, 'the superseded Auto-Fit took no snapshot (changed nothing)');
  assert.strictEqual(out.starts, 0, 'and sent nothing');
  assert.strictEqual(out.applied + out.restored, 0);
  assert.ok(api._fitOpCurrent(runFitOp), 'the Run Fit still owns the tab');
  assert.deepStrictEqual(out.cancels, [], "the Run Fit's job was not cancelled");
});

test("the spinner belongs to the operation that showed it: an ended fit never hides another fit's spinner (Codex round 3)", () => {
  const hides = [];
  const api = new Function('_hideFitSpinner', 'let _fitSpinnerOp = null;\n' + extractFn('_hideFitSpinnerFor') +
    '\nreturn { hideFor: _hideFitSpinnerFor, set: op => { _fitSpinnerOp = op; }, get: () => _fitSpinnerOp };')(() => hides.push('hide'));
  const a = { seq: 1 }, b = { seq: 2 };
  api.set(b);                                         // tab B's fit showed the spinner last
  api.hideFor(a);                                     // tab A's fit ends (discarded)
  assert.deepStrictEqual(hides, [], "A leaves B's spinner alone");
  api.hideFor(b);
  assert.deepStrictEqual(hides, ['hide']);
  assert.strictEqual(api.get(), null);
  // and every hide after each caller's claim is an owned hide
  for (const [fn, op, mark] of [['runFit', 'fitOp', '_fitSpinnerOp = fitOp;'], ['runAutoFitC1sGraphite', 'afOp', '_fitSpinnerOp = afOp;']]) {
    const src = extractFn(fn);
    const after = src.slice(src.indexOf(mark));
    assert.ok(src.indexOf(mark) > 0, fn + ' takes the spinner');
    assert.ok(!/_hideFitSpinner\(\);/.test(after), fn + ': no unowned hide after the claim');
    assert.ok(new RegExp('_hideFitSpinnerFor\\(' + op + '\\)').test(after), fn);
  }
});

// Round 5 (Codex round 4, MAJOR): Auto-Fit installed its operation — which
// cancels a running fit on the tab — BEFORE its preflight; a refusal there
// ("No strong peak found", an empty ROI) then returned with the Run Fit's job
// cancelled, its spinner up, Run Fit disabled and nothing running. Now a
// refusal leaves the running Run Fit exactly as it was: its job is not
// cancelled, its spinner stays, and it completes with its own result.
test('an Auto-Fit REFUSED by its preflight leaves a running Run Fit alone: not cancelled, spinner kept, its result arrives (Codex round 4)', async () => {
  const constants = lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n');
  for (const refusal of ['no strong peak', 'empty ROI', 'no strong peak, no modal (no peaks yet)']) {
    const tab = { id: 't1' };
    const out = { cancels: [], hides: 0, notes: [], snapshots: 0, undo: 0 };
    const poll = deferred();
    const state = { peaks: /no peaks/.test(refusal) ? [] : [{ id: 1 }], ccShift: 0, rawBE: [285, 284.5, 284], rawIntensity: [10, 20, 10] };
    const deps = {
      state, tabManager: { activeId: 't1', _getTab: () => tab, _captureUI: () => ({}) },
      document: { getElementById: () => ({ value: '', style: {}, setAttribute() {}, classList: { add() {}, remove() {} } }), querySelector: () => ({}) },
      notify: (m) => out.notes.push(m), _opOwner: () => tab, _ownerActive: () => true, isC1sTab: () => true,
      _showAutoFitConfirmModal: async () => true, _autoFitSnapshot: () => { out.snapshots++; return {}; }, _autoFitRestore() {},
      fetch: async (u) => {
        if (u.startsWith('/api/fit/cancel/')) { out.cancels.push(u); return ok({}); }
        if (u === '/api/fit/start') return ok({ job_id: 'RUN1' }, 202);
        if (u.startsWith('/api/fit/progress/')) { await poll.p; return ok({ status: 'done', result: { success: true, mine: 'RUN1' } }); }
        return ok({});
      },
      applyBackendResult() {}, _showFitSpinner() {}, _hideFitSpinner: () => { out.hides++; }, setTimeout: f => { setImmediate(f); return 0; }, clearTimeout() {},
      AbortController, DOMException: Error,
      getROIData: () => (refusal === 'empty ROI' ? { be: [], inten: [] } : { be: state.rawBE, inten: state.rawIntensity }),
      computeBackground: be => be.map(() => 0), findGraphiteRawBE: () => null,
      uploadToBackend: async () => 'sid', pushUndo: () => { out.undo++; }, buildAutoFitModel: () => [], renderPeakList() {}, peakToBackendSpec: p => p, _getManualAnchors: () => [],
    };
    const src = constants + '\n' + [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
      'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap(); let _fitSpinnerOp = null;',
      ...AF_FNS.map(extractFn)].join('\n');
    const api = new Function(...Object.keys(deps), src +
      '\nreturn { runAutoFitC1sGraphite, _claimFitOp, _fitOpCurrent, _serverFitJob, _hideFitSpinnerFor, takeSpinner: op => { _fitSpinnerOp = op; }, spinner: () => _fitSpinnerOp };')(...Object.values(deps));
    // a Run Fit is running on the tab: it claimed its operation, owns the spinner, its job is being polled
    const runOp = api._claimFitOp(tab);
    api.takeSpinner(runOp);
    const run = api._serverFitJob({}, { op: runOp });
    await new Promise(r => setImmediate(r));
    assert.strictEqual(runOp.jobId, 'RUN1', refusal + ': the Run Fit job is running');
    // the student confirms Auto-Fit on the same tab; its preflight refuses
    await api.runAutoFitC1sGraphite();
    assert.ok(out.notes.some(m => /No strong peak found|ROI is empty/.test(m)), refusal + ': Auto-Fit refused: ' + out.notes.join(' | '));
    assert.deepStrictEqual(out.cancels, [], refusal + ": the Run Fit's job was NOT cancelled");
    assert.ok(api._fitOpCurrent(runOp), refusal + ': the Run Fit still owns the tab');
    assert.strictEqual(api.spinner(), runOp, refusal + ': the spinner is still the Run Fit\'s');
    assert.strictEqual(out.hides, 0, refusal + ': nobody hid it');
    assert.strictEqual(out.undo, 0, refusal + ': Auto-Fit changed nothing');
    poll.res();
    assert.deepStrictEqual(await run, { success: true, mine: 'RUN1' }, refusal + ': the Run Fit gets its own result (not superseded)');
    api._hideFitSpinnerFor(runOp);
    assert.strictEqual(out.hides, 1, refusal + ': and hides its own spinner at the end');
  }
});

// Round 5 (Codex round 4, MINOR): Batch Fit's local fits hid the page-wide
// spinner unconditionally — a quick batch while a server fit was pending left
// that fit running with no spinner. runFitLocal now hides only the spinner of
// the operation it is given (Run Fit's fallback); Batch Fit gives none.
test("runFitLocal hides only its caller's spinner: Batch Fit (no operation) never hides a running fit's (Codex round 4)", () => {
  const src = extractFn('runFitLocal');
  assert.ok(!/_hideFitSpinner\(\)/.test(src), 'no unowned hide inside runFitLocal');
  assert.match(src, /const hideSpinner = \(\) => \{ if \(options\.spinnerOp\) _hideFitSpinnerFor\(options\.spinnerOp\); \};/);
  assert.match(extractFn('runFit'), /runFitLocal\(be, bgSubtracted, bgIntensity, \{ spinnerOp: fitOp \}\)/, "Run Fit's fallback passes its operation");
  // (since 2026-10-01 behind the background's convergence check: `bgFail ? {...} : runFitLocal(...)`)
  const batchCall = html.match(/const outcome = (?:bgFail \? \{[^}]*\} : )?runFitLocal\(([^)]*)\);/);
  assert.ok(batchCall && batchCall[1] === 'be, bgSub, bgI', 'Batch Fit passes no operation: ' + (batchCall && batchCall[1]));
  // behaviour on the failure path (invalid data returns before any fitting)
  for (const [label, opts, owned, want] of [['Batch Fit (no op)', {}, 'RUN', 0], ['another op', { spinnerOp: 'B' }, 'RUN', 0], ['its own op', { spinnerOp: 'RUN' }, 'RUN', 1]]) {
    let hides = 0, spinnerOp = owned;
    const deps = {
      _hideFitSpinnerFor: op => { if (spinnerOp !== op) return; spinnerOp = null; hides++; },
      document: { getElementById: () => ({ textContent: '' }) }, notify() {},
    };
    const f = new Function(...Object.keys(deps), src + '\nreturn runFitLocal;')(...Object.values(deps));
    const r = f([1], [1], [0], opts);
    assert.strictEqual(r.success, false, label);
    assert.strictEqual(hides, want, label + ': hides');
  }
});
