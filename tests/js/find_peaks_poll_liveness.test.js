// Unit A1 (2026-09-29): Find Peaks' poll judges a job lost by LIVENESS (a
// heartbeat older than FIT_HEARTBEAT_LOST_SEC), never by total time. The
// engine no longer stops on a wall-clock budget, so a counted run under heavy
// load can legitimately take longer than the old 600 s cap, which turned it
// into "Try again" (Codex A1 round 1).
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

function make(records) {
  let i = 0, clock = 0;
  const fetch = async () => {
    const rec = records(i++);
    return { ok: true, status: 200, json: async () => rec };
  };
  const document = { getElementById: () => ({ textContent: '' }) };
  const FakeDate = { now: () => (clock += 1000) };          // one second passes per read
  const src = [constLine('FP_POLL_INTERVAL_MS'), constLine('FIT_HEARTBEAT_LOST_SEC'),
    extractFn('_fpFormatElapsed'), extractFn('_fpProgressText'), extractFn('_fpPollJob')].join('\n');
  const api = new Function('fetch', 'document', 'setTimeout', 'Date', src + '\nreturn { _fpPollJob };')(
    fetch, document, f => setImmediate(f), FakeDate);
  return { api, polls: () => i };
}

test('a live job is waited on however long it runs (no total-time cap)', async () => {
  const { api, polls } = make(k => k < 2000
    ? { status: 'running', elapsed_sec: k, heartbeat_age_sec: 1.2, message: 'stabilizing' }
    : { status: 'done', result: { success: true, winner: 'MG2' } });
  const done = await api._fpPollJob('j');
  assert.strictEqual(done.status, 'done');
  assert.strictEqual(polls(), 2001, 'polled through 2000 s of a live job');
});

test('a stale heartbeat is a lost job, reported — never an endless spinner', async () => {
  const { api } = make(k => ({ status: 'running', elapsed_sec: k, heartbeat_age_sec: k < 5 ? 1 : 31, message: 'x' }));
  await assert.rejects(api._fpPollJob('j'), /stopped responding/);
});

test('the first poll without a heartbeat age yet is waited on', async () => {
  const { api } = make(k => k === 0 ? { status: 'running', heartbeat_age_sec: null }
    : { status: 'done', result: {} });
  assert.strictEqual((await api._fpPollJob('j')).status, 'done');
});

test('a job that never shows valid heartbeat evidence is lost after the liveness limit', async () => {
  // A progress record that persistently cannot be read comes back "running"
  // with no heartbeat age (Codex A1 round 2): the first such poll is waited
  // on, but time WITHOUT evidence is bounded by FIT_HEARTBEAT_LOST_SEC.
  const { api, polls } = make(() => ({ status: 'running', heartbeat_age_sec: null }));
  await assert.rejects(api._fpPollJob('j'), /stopped responding/);
  assert.ok(polls() < 40, `gave up after ${polls()} polls`);
});

test('missing ages between valid ones do not end a live job', async () => {
  const { api } = make(k => k < 500
    ? { status: 'running', heartbeat_age_sec: k % 4 === 0 ? 1 : null }
    : { status: 'done', result: {} });
  assert.strictEqual((await api._fpPollJob('j')).status, 'done');
});

test('no total-duration watchdog remains in the poll loop', () => {
  const src = extractFn('_fpPollJob');
  // the clock is read only to age the latest heartbeat evidence
  assert.ok(!/WATCHDOG/.test(src) && !/startedAt|t0\b|pollStart/.test(src), src);
  assert.ok(/lastAlive/.test(src));
  assert.ok(!/FP_POLL_WATCHDOG_SEC/.test(html));
});
