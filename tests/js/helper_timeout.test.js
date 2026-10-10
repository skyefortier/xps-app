// A helper process that stalls FAILS the test instead of hanging the run (owner 2026-10-09;
// tests/js/_helper_process.js). On 2026-10-07 lineshape_parity.test.js's Python helper sat
// blocked on its stdin for 10+ minutes and the JS suite never finished.
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { runHelper, HELPER_TIMEOUT_MS } = require('./_helper_process.js');

const NODE = process.execPath;

test('a helper that never reads its input and never exits is killed at its timeout, with a plain message', () => {
  const t0 = Date.now();
  assert.throws(() => runHelper(NODE, ['-e', 'setInterval(() => {}, 1000)'], { input: 'x'.repeat(16), encoding: 'utf8', timeout: 1500 }),
                e => /^helper process "node -e" did not finish within 1\.5 s and was killed \(a stalled helper fails the test instead of hanging the run\)$/.test(e.message));
  assert.ok(Date.now() - t0 < 15000, 'it fails promptly');
});

test('a helper blocked on an input larger than the pipe buffer (it never reads it) is killed too', () => {
  const t0 = Date.now();
  assert.throws(() => runHelper(NODE, ['-e', 'setInterval(() => {}, 1000)'], { input: 'x'.repeat(4 * 1024 * 1024), encoding: 'utf8', timeout: 1500 }),
                /did not finish within 1\.5 s and was killed/);
  assert.ok(Date.now() - t0 < 15000);
});

test('a helper that finishes returns its output; its own failure is reported as before, not as a timeout', () => {
  assert.strictEqual(runHelper(NODE, ['-e', 'process.stdin.pipe(process.stdout)'], { input: 'echo', encoding: 'utf8' }), 'echo');
  assert.throws(() => runHelper(NODE, ['-e', 'process.exit(3)'], { encoding: 'utf8', stdio: 'pipe' }),
                e => e.status === 3 && !/did not finish/.test(e.message));
});

test('every call has a budget: the default applies when a caller gives none', () => {
  assert.ok(Number.isFinite(HELPER_TIMEOUT_MS) && HELPER_TIMEOUT_MS > 0);
});

test('no JS test starts a process except through runHelper', () => {
  const dir = __dirname;
  const self = path.basename(__filename);                  // this file names the patterns it looks for
  const files = fs.readdirSync(dir).filter(n => n.endsWith('.js') && n !== '_helper_process.js' && n !== self);
  assert.ok(files.length >= 30 && files.includes('lineshape_parity.test.js'), files.length + ' files scanned');
  for (const f of files) {
    const src = fs.readFileSync(path.join(dir, f), 'utf8');
    assert.ok(!/child_process/.test(src.replace(/\/\/.*$/gm, '')), `${f} requires child_process directly`);
    assert.ok(!/\b(execFileSync|execSync|spawnSync|execFile|spawn|fork)\s*\(/.test(src.replace(/\/\/.*$/gm, '')), `${f} starts a process directly`);
  }
});
