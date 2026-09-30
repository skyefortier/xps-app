# Archive Find Peaks round 6 — run A (commit c6358d9; codex exec, reasoning high)

- **MINOR — Log-corruption regression tests use the wrong expected-file roster.** [tests/test_ci_check_node_events.py:98](/Users/skyefortier/xps-app/.claude/worktrees/archive-find-peaks/tests/test_ci_check_node_events.py:98): generating `failing` overwrites `FILES[tmp_path]`, so subsequent checks of `green` expect the failing run’s filename. Even the **unaltered green log is rejected** for missing/unexpected files. Consequently, removing truncation detection could leave those regression assertions passing. Preserve each run’s roster, pass it explicitly, and assert the unmodified baseline succeeds.

No BLOCKER or MAJOR found. Independent checks using the correct rosters confirmed:

- Early exits, empty files, load/hook failures, timeouts, cancellations, late uncaught errors and nested skips are rejected—even alongside 508 genuine passes.
- Missing/duplicated results and file summaries, concatenation, truncation and misplaced run summaries are rejected. A real Node-generated 508-pass/two-TODO stream succeeds.
- **364 unmodified JS tests passed**, and their structured stream passed the guard. Registration inspection supports **510 tests: 508 ordinary, two TODOs**; no machine-dependent registration condition emerged.
- Reporter destinations, stale-log removal, `pipefail` and `always()` are correct on inspection.
- Runtime HTML remains equivalent to `main` apart from comments and the removed menu button. Backend, serialization and shared Run Fit infrastructure are unchanged; no additional launch or cached-result/provenance display path emerged.

Full backend/browser suites and a fresh Ubuntu green run remain unverified: backend imports hit the sandbox’s unavailable writable temporary directory. No files changed.

**VERDICT: GO**
