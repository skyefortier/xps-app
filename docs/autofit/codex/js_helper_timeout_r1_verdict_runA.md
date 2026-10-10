# JS helper timeout — Codex round 1, run A (commit 3bfda21)

**MAJOR — a caller can disable the timeout.** In [_helper_process.js:16](/Users/skyefortier/xps-app/.claude/worktrees/helper-timeout/tests/js/_helper_process.js:16), `opts.timeout ?? HELPER_TIMEOUT_MS` accepts `0`, which disables Node’s timeout. Reproduced with a 50 ms default: a helper given `{ timeout: 0 }` ran for 1,062 ms and returned normally. An indefinite helper would hang. Existing callers do not pass zero, but the wrapper permits it and the source guard accepts it. Enforce a positive timeout and test this case.

**MINOR — the scan’s coverage is overstated.** [helper_timeout.test.js:39](/Users/skyefortier/xps-app/.claude/worktrees/helper-timeout/tests/js/helper_timeout.test.js:39) scans only top-level `.js` files, excluding itself and the wrapper. It misses imported `tests/js/lib/` modules, `.mjs`/`.cjs` dependencies, and the CI reporter. Direct inspection found no existing unwrapped process call in those dependencies. CI explicitly runs `tests/js/*.test.js`; additional extensions are not automatically selected.

Other checks:

- All 10 existing call sites were converted mechanically. Arguments and options are unchanged. Probes confirmed option forwarding, returned-object identity, and preservation of non-timeout errors.
- The five new tests passed unmodified. Additional probes confirmed prompt termination of a helper blocked reading stdin and one ignoring SIGTERM. The large-input test passed.
- SIGKILL targets the executable directly for current callers. Descendants are not killed; however, a grandchild inheriting the helper’s default pipes did not keep `runHelper` open after timeout.
- The instrumented full suite produced **587 passed, 2 todo, zero failures**, and passed the CI guard. It made **239 helper calls: 235 Python and 4 Node**, matching the documentation. The slowest measured here was **2.371 s**.
- The 300-second budget provides substantial headroom—about 122× the reported 2.46-second maximum. No evidence found that it is too short.

The full-suite verification needed an in-memory Python startup shim because the read-only sandbox prevents `dill`’s temporary-directory probe. No repository files were changed. Historical pytest/browser timings in PROGRESS.md were not independently rerun.

VERDICT: NO-GO.
