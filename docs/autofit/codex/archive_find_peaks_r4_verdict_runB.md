# Archive Find Peaks round 4 — run B (commit d334b0e; codex exec, reasoning high)

- **MAJOR — Escaped test names can hide a real SKIP directive.** [scripts/ci_check_node_tap.py:41](/Users/skyefortier/xps-app/.claude/worktrees/archive-find-peaks/scripts/ci_check_node_tap.py:41) takes the first regex match, including escaped text inside the name. Reproduced with Node **22.22.2**, using `--test --test-reporter=tap`: wrap the actual archive test module in `describe.skip('archive # TODO later', ...)`, alongside 508 passing tests. Node emits `ok 509 - archive \# TODO later # SKIP`. The guard counts one TODO and misses the SKIP: **Node exit 0, guard accepts, no archive assertions execute**. Conversely, a passing test named `mentions # SKIP` falsely fails the guard. Parse the actual unescaped directive and add both regression cases.

- **MINOR — Truncated trailing runs still pass.** [scripts/ci_check_node_tap.py:32](/Users/skyefortier/xps-app/.claude/worktrees/archive-find-peaks/scripts/ci_check_node_tap.py:32) recognizes only complete header prefixes; summary validation does not reject trailing incomplete TAP. A real 508-pass log followed by `TAP versi` is accepted. A header plus that run’s summary, with every test result and plan removed, also passes. Validate stream completeness and terminal structure. The workflow’s `pipefail` still independently protects ordinary process failures.

Verification: **364 JS tests passed**, and their real TAP output passed the guard. The archive test rejects `main`. Ordinary skipped suites, failures, cancellations, complete concatenated runs, and interleaved console output behaved correctly.

Earlier implementation checks hold: runtime HTML differs only by the removed menu button; backend, shared fitting infrastructure, serialization, and existing tests are unchanged. No additional launch or cached-result/provenance display path found.

The full JS run encountered Python’s read-only temporary-directory restriction. Browser/Python suites and the **508-pass Ubuntu baseline were not independently verified**.

**VERDICT: NO-GO**
