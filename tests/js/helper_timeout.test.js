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

test('every call has a budget: the default applies when a caller gives none, and no caller can disable it', () => {
  assert.ok(Number.isInteger(HELPER_TIMEOUT_MS) && HELPER_TIMEOUT_MS > 0);
  for (const bad of [0, -1, 1.5, NaN, Infinity, '1000'])          // (null / undefined: none given, the default applies)
    assert.throws(() => runHelper(NODE, ['-e', ''], { timeout: bad }), /the timeout must be a positive whole number of milliseconds/, String(bad));
});

test('an output beyond maxBuffer is still ENOBUFS (only the signal Node used reads SIGKILL)', () => {
  assert.throws(() => runHelper(NODE, ['-e', 'process.stdout.write("x".repeat(4096))'], { encoding: 'utf8', maxBuffer: 2048 }),
                e => e.code === 'ENOBUFS' && e.signal === 'SIGKILL' && !/did not finish/.test(e.message));
});

// Every file node can load from tests/js (any depth, .js / .mjs / .cjs) and the CI reporter; this
// file included — its patterns are built from pieces so that they do not match themselves. The
// wrapper is exempt by its EXACT path, never by its name (Codex round 2: a nested namesake
// `lib/_helper_process.js` passed unread).
const WRAPPER = path.join(__dirname, '_helper_process.js');
const MODULE = new RegExp(['child', 'process'].join('_'));
// a call of one of the module's functions — not a method of the same name (RegExp.prototype.exec)
const LAUNCH = new RegExp('(^|[^.\\w$])(' + ['execFileSync', 'execSync', 'spawnSync', 'execFile', 'spawn', 'fork', 'exec'].join('|') + ')\\s*\\(', 'm');
function* sources(dir) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) { if (e.name !== 'node_modules') yield* sources(p); }
    else if (/\.(c|m)?js$/.test(e.name)) yield p;
  }
}
// the files under `root` (and `extra`) that name the process module or launch a process directly
function directLaunches(root, extra = [], wrapper = WRAPPER) {
  const files = [...sources(root), ...extra].filter(p => path.resolve(p) !== path.resolve(wrapper));
  const bad = [];
  for (const p of files) {
    const src = fs.readFileSync(p, 'utf8');                 // comments included: a mention is a finding too
    if (MODULE.test(src) || LAUNCH.test(src)) bad.push(path.relative(root, p));
  }
  return { files, bad };
}

test('no JS test starts a process except through runHelper', () => {
  const { files, bad } = directLaunches(__dirname, [path.join(__dirname, '../../scripts/ci_node_events_reporter.mjs')]);
  assert.ok(files.length >= 30 && files.some(p => p.endsWith('lineshape_parity.test.js')) && files.some(p => p.endsWith('helper_timeout.test.js')), files.length + ' files');
  assert.ok(!files.some(p => path.resolve(p) === path.resolve(WRAPPER)), 'the wrapper itself is the one exemption');
  assert.deepStrictEqual(bad, []);
});

test('the scan exempts only the wrapper\'s exact path: a nested namesake, an .mjs, a .cjs are read', () => {
  const os = require('node:os');
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'helper-scan-'));
  try {
    const launch = "const { " + 'execFile' + "Sync: go } = require('node:" + ['child', 'process'].join('_') + "'); go('x');\n";
    fs.mkdirSync(path.join(root, 'lib'));
    fs.writeFileSync(path.join(root, '_helper_process.js'), launch);            // the wrapper (exempt)
    fs.writeFileSync(path.join(root, 'lib', '_helper_process.js'), launch);     // a namesake (read)
    fs.writeFileSync(path.join(root, 'lib', 'm.mjs'), 'export const f = () => ' + 'spa' + "wn('x');\n");
    fs.writeFileSync(path.join(root, 'c.cjs'), "const u = 'https://x.test'; " + launch);
    fs.writeFileSync(path.join(root, 'ok.js'), "const r = /a/.exec('a');\n");
    const { bad } = directLaunches(root, [], path.join(root, '_helper_process.js'));
    assert.deepStrictEqual(bad.sort(), ['c.cjs', path.join('lib', '_helper_process.js'), path.join('lib', 'm.mjs')].sort());
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});
