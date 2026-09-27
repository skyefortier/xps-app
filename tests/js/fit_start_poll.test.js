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
    'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap();',
    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_claimFitOp'), extractFn('_fitOpCurrent'),
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
    'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap();',
    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_claimFitOp'), extractFn('_fitOpCurrent'),
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
  const claim = af.indexOf('afOp = _claimFitOp(fittingTab);');
  assert.ok(claim > 0 && claim < af.indexOf('await uploadToBackend('), 'Auto-Fit claims before its first server await');
  assert.match(af, /op: afOp,/);
  assert.match(af, /if \(json && json\._abandoned === 'superseded'\) return;/);
  assert.match(af, /if \(afOp && !_fitOpCurrent\(afOp\)\) return;/, 'Auto-Fit: no rollback when superseded');
});
