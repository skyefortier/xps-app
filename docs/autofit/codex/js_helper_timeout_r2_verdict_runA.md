# JS helper timeout — Codex round 2, run A (commit bb08775)

**MAJOR — the source scan still exempts nested helpers by filename.** [helper_timeout.test.js:57](/Users/skyefortier/xps-app/.claude/worktrees/helper-timeout/tests/js/helper_timeout.test.js:57) excludes every file whose basename is `_helper_process.js`, rather than only the approved wrapper.

An in-memory mutation adding `tests/js/review_probe/_helper_process.js` containing an unbounded `require('node:child_process').execFileSync(...)` passed the guard without that file being read. Identical contents in `ordinary.js` and `ordinary.mjs` failed. A test can import the exempt nested module and hang; this needs no dynamically constructed name. Exempt the wrapper’s exact path and regression-test a nested namesake. PROGRESS.md’s coverage claim remains overstated.

Other checks:

- All **six timeout tests passed**. Additional probes confirmed blocked-stdin and SIGTERM-ignoring helpers terminate promptly.
- Timeout validation, null/undefined defaults, option forwarding, returned-object identity, and non-timeout error identity passed.
- All ten migrated calls preserve their arguments and options.
- **The ENOBUFS change is acceptable:** code, message, and status were preserved; only `signal` changed. No current caller reads it. Minor caveat: the new test does not actually assert the claimed signal pin.
- Registration counting confirmed **590 tests: 588 non-TODO, 2 TODO**, matching the CI floor.
- The full-suite attempt, using an in-memory shim for the sandbox-blocked Python temporary-directory probe, exceeded my **240-second review limit**. I cannot claim a full-suite pass.
- The documented 300-second budget provides roughly 122× the historical measured maximum; no new evidence warrants changing it.

No files changed.

VERDICT: NO-GO
