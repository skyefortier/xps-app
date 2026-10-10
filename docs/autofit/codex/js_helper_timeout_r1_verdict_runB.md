# JS helper timeout — Codex round 1, run B (commit 3bfda21)

Three MAJOR findings under your criteria:

1. **The wrapper permits disabling the timeout.** [_helper_process.js:16](/Users/skyefortier/xps-app/.claude/worktrees/helper-timeout/tests/js/_helper_process.js:16) accepts `opts.timeout: 0`, which disables Node’s deadline. With the default overridden to 100 ms, a helper given `timeout: 0` completed after 463 ms. An endless helper would hang. The source guard accepts this call, and the budget test checks only the default constant. Validate the effective timeout as a positive finite integer. No current migrated caller supplies zero.

2. **The source guard can miss unbounded process launches.** [helper_timeout.test.js:39](/Users/skyefortier/xps-app/.claude/worktrees/helper-timeout/tests/js/helper_timeout.test.js:39) excludes itself, nested modules, `.mjs`/`.cjs` dependencies, and the CI reporter. Its comment stripping also treats `//` inside strings as a comment: a line starting with `const url = "https://example.test";` can then import and invoke an aliased `execFileSync` without detection. I reproduced acceptance by both regex checks. Thus the claimed enforcement is incomplete. Separate inspection found no existing unwrapped launch in those dependencies or the reporter.

3. **A non-timeout error changes behavior.** [_helper_process.js:21](/Users/skyefortier/xps-app/.claude/worktrees/helper-timeout/tests/js/_helper_process.js:21) forces SIGKILL for buffer overflow too. With `maxBuffer: 2048` and 4096 bytes of output, original `execFileSync` returned `ENOBUFS` with `signal: SIGTERM`; `runHelper` returned `ENOBUFS` with `signal: SIGKILL`. This contradicts the stated preservation of non-timeout failures.

Other checks:

- All ten replacements preserve their arguments and options. Buffer/string output, input, cwd, env, and ordinary nonzero exits behaved correctly.
- All five new tests pass. A real blocked-stdin read also timed out promptly. Current callers execute Python directly, so SIGKILL reaches the helper.
- A grandchild inheriting pipes survived its parent’s timeout, but did **not** keep `runHelper` open.
- Registration counting confirms **589 tests: 587 non-TODO and 2 TODO**. The CI floor is accurate.
- 300 s provides approximately 122× the recorded 2.46 s maximum—ample measured headroom, though not a guarantee under arbitrary load. I could not independently reproduce the measurements: the full suite encountered Python temporary-directory failures imposed by the read-only sandbox.
- PROGRESS.md overstates what the source guard proves.

No files changed.

VERDICT: NO-GO.
