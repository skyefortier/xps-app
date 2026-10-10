# JS helper timeout — Codex round 2, run B (commit bb08775)

**MAJOR — the recursive scan still exempts nested files named `_helper_process.js`.** [helper_timeout.test.js:57](/Users/skyefortier/xps-app/.claude/worktrees/helper-timeout/tests/js/helper_timeout.test.js:57) excludes by basename rather than the approved wrapper’s exact path.

An in-memory mutation containing a literal `require('node:child_process')` and an unbounded, aliased launch was rejected as `lib/unbounded.mjs` but **passed as `lib/_helper_process.js`**. A test could import and invoke that module without detection. This is independent of the documented runtime-name limitation. Exclude only the actual wrapper path and add a regression check for a nested namesake. No existing unwrapped launch was found.

Other checks:

- All six focused tests passed. Invalid timeout rejection works; `null` and `undefined` use the default.
- Additional probes terminated a blocked stdin read and a helper ignoring SIGTERM in approximately 500 ms.
- The ten migrated calls preserve their arguments and options. **The ENOBUFS signal change is acceptable for current callers:** none reads `signal`; direct comparison preserved its code, message, and status.
- Registration counting confirms **588 non-TODO tests and 2 TODOs**, matching the CI floor.
- The 300-second budget has ample headroom against the documented 2.46-second measurement.
- Full-suite verification, using an in-memory Python temporary-directory workaround, exceeded my 180-second review limit; I cannot confirm a complete suite pass.

No files changed.

VERDICT: NO-GO
