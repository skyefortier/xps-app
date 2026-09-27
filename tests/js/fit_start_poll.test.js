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
    'const _runningFitJobs = new Set(); const _fitJobByOwner = new WeakMap();',
    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
  return new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob, _runningFitJobs };')(
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

test('a new start for the same tab SUPERSEDES the previous job: cancelled on the server, its loop returns quietly (Codex round 1)', async () => {
  let n = 0;
  let releaseFirst;
  const gate = new Promise(r => { releaseFirst = r; });
  const s = server(u => u === START ? ok({ job_id: 'J' + (++n) }, 202)
    : isProgress(u) ? ok({ status: 'running', heartbeat_age_sec: 0 }) : ok({}));
  // a poll loop that yields between polls, so two jobs can interleave
  const src = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
    'const _runningFitJobs = new Set(); const _fitJobByOwner = new WeakMap();',
    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
  const { _serverFitJob } = new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob };')(
    s.fetch, f => { setImmediate(f); return 0; }, class extends Error {});   // yield to the event loop between polls
  const owner = { id: 'tab-1' };
  let polls2 = 0;
  const first = _serverFitJob({}, { owner });
  await new Promise(r => setImmediate(r)); await new Promise(r => setImmediate(r));
  const second = _serverFitJob({}, { owner, abandoned: () => (++polls2 > 3 ? 'tab' : null) });
  assert.deepStrictEqual(await first, { _abandoned: 'superseded' });
  assert.ok(s.calls.some(c => c.url === '/api/fit/cancel/J1' && c.method === 'POST'), 'the first job is cancelled on the server');
  assert.deepStrictEqual(await second, { _abandoned: 'tab' }, 'the second runs on, owning the tab');
  // another tab's job is not touched
  const other = _serverFitJob({}, { owner: { id: 'tab-2' }, abandoned: () => 'model' });
  assert.deepStrictEqual(await other, { _abandoned: 'model' });
});

test('both callers pass their tab as the owner and do nothing at all when superseded', () => {
  for (const fn of ['runFit', 'runAutoFitC1sGraphite']) {
    const src = extractFn(fn);
    assert.match(src, /owner: fittingTab,/, fn);
    assert.match(src, /if \(json && json\._abandoned === 'superseded'\) return;/, fn);
  }
});
