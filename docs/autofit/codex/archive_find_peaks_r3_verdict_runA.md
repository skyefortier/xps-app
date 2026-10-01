# Archive Find Peaks round 3 — run A (commit 312396a; codex exec, reasoning high)

- **MAJOR — Skipped suites bypass the zero-skip guard.** [scripts/ci_check_node_tap.py:31](/Users/skyefortier/xps-app/.claude/worktrees/archive-find-peaks/scripts/ci_check_node_tap.py:31) trusts `# skipped`, but Node 22 excludes skipped `describe` suites from that counter. Reproduced with `node --test`, wrapping the actual archive test file in `describe.skip(...)` in memory alongside 504 passing tests and two TODOs: TAP contains `archived tests # SKIP`, yet reports **504 passed, 0 skipped, 2 TODO**. **Node and guard both exit 0.** Wrapping the archive file’s four tests this way would leave the commit’s reported 508-pass baseline above the 500 floor while disabling every archive assertion. Check suite-level skip directives as well; add a real Node-generated regression case.

- **MINOR — Separate summaries can fabricate a complete successful result.** [scripts/ci_check_node_tap.py:21](/Users/skyefortier/xps-app/.claude/worktrees/archive-find-peaks/scripts/ci_check_node_tap.py:21) retains the last value independently for each counter. A complete green summary followed by `TAP version 13\n# tests 510\n` exits **0**, borrowing the missing counters from the earlier run. A failed summary followed by a green summary also exits **0**, erasing the failure. Reject duplicate/multiple summaries and require one complete terminal summary. The current workflow’s `pipefail` still independently protects against ordinary Node failures and crashes.

Verification: **150 focused JS tests passed**; the archive test fails against `main`; all eight committed guard scenarios returned their expected statuses. Node version, glob, `always()`, Python dependencies and tracked fixtures appear suitable for CI. Runtime HTML remains equivalent to main apart from comments and the removed button; backend, serialization and shared fitting code remain unchanged. The corrected Unit B rationale matches its cited record.

The full JS attempt encountered Python’s read-only temporary-directory restriction. Python/browser suites and Ubuntu execution were not verified.

**VERDICT: NO-GO**
