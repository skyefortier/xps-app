// Every helper process the JS tests start goes through runHelper (owner 2026-10-09: a stall
// FAILS instead of hanging CI). On 2026-10-07 lineshape_parity.test.js's Python helper sat
// blocked reading its stdin at 0 % CPU for 10+ minutes; execFileSync has no timeout of its
// own, so the run hung. runHelper is execFileSync with a timeout and SIGKILL; a helper that
// does not finish in time is killed and the test fails with a message naming it. SIGKILL,
// not Node's default SIGTERM, so a helper that ignores SIGTERM is stopped too. Its one side
// effect on a failure that is not a timeout: when Node kills a helper whose output exceeds
// maxBuffer, the error is still ENOBUFS but its `signal` reads SIGKILL (no caller reads it).
// Pinned by tests/js/helper_timeout.test.js (the timeout fires; no test file starts a
// process any other way).
const { execFileSync } = require('node:child_process');
const path = require('node:path');

// The budget per call: the slowest helper call measured in a full JS run, with ample margin
// (docs/superpowers/plans/2026-10-09-js-helper-timeout.md). XPS_HELPER_TIMEOUT_MS overrides it.
const HELPER_TIMEOUT_MS = Number(process.env.XPS_HELPER_TIMEOUT_MS) || 300000;

function runHelper(file, args = [], opts = {}) {
  const timeout = opts.timeout ?? HELPER_TIMEOUT_MS;
  // a budget that is not a positive whole number of ms would disable the deadline (Node treats
  // 0 as "no timeout"): refused (Codex round 1)
  if (!(Number.isInteger(timeout) && timeout > 0))
    throw new TypeError(`runHelper: the timeout must be a positive whole number of milliseconds, not ${timeout}`);
  // the executable and its first argument (a script's file name, or -c / -e): "python3 lineshape_parity_backend.py"
  const name = [path.basename(String(file)), ...args.slice(0, 1).map(a => (String(a).includes('/') ? path.basename(String(a)) : String(a)))].join(' ');
  const t0 = Date.now();
  try {
    return execFileSync(file, args, { ...opts, timeout, killSignal: 'SIGKILL' });
  } catch (e) {
    if (e && e.code === 'ETIMEDOUT')
      throw new Error(`helper process "${name}" did not finish within ${timeout / 1000} s and was killed ` +
                      '(a stalled helper fails the test instead of hanging the run)');
    throw e;
  } finally {
    if (process.env.XPS_HELPER_LOG)
      require('node:fs').appendFileSync(process.env.XPS_HELPER_LOG, JSON.stringify({ name, ms: Date.now() - t0 }) + '\n');
  }
}

module.exports = { runHelper, HELPER_TIMEOUT_MS };
