# Archive Find Peaks round 5 — run B (commits b94a847 + e6e617a; codex exec, reasoning high)

- **MAJOR — Synthetic file successes count as executed tests.** [scripts/ci_check_node_events.py:57](/Users/skyefortier/xps-app/.claude/worktrees/archive-find-peaks/scripts/ci_check_node_events.py:57) counts every non-TODO `test:pass` with `kind: "test"`. Node also emits that result for a file whose process exits successfully without reporting a completed test.

  Reproduced on **Node 22.22.2**, with process isolation and both reporters: one file contains **507 passing tests and two TODOs**; another contains `test('Find Peaks', () => { process.exit(0); throw Error('unreached'); })`. Node substitutes a successful file result, producing **510 tests, 508 passed, two TODOs**. **Node and the guard both exit 0 with `--min-passed 508 --max-todo 2`**, despite the unreached assertion. An empty file likewise contributes a synthetic pass. `pipefail` cannot catch this because Node succeeds.

  Preserve and validate per-file completion evidence—the reporter currently discards file summaries at [ci_node_events_reporter.mjs:18](/Users/skyefortier/xps-app/.claude/worktrees/archive-find-peaks/scripts/ci_node_events_reporter.mjs:18)—and prevent synthetic file results from satisfying the executed-test floor. Add a regression spanning multiple isolated files.

Verification: **364 unmodified JS tests passed**, and their structured stream passed the guard. Ordinary skips, load failures, hook failures, cancellation, late uncaught errors, concatenated streams and tested truncations were rejected. The archive test rejects `main`; runtime HTML remains equivalent apart from the removed button and comments. Backend, serialization and shared Run Fit code remain unchanged; no additional launch or cached-result display path emerged.

The full JS run encountered Python’s read-only temporary-directory restriction. Browser/Python suites and the fresh Ubuntu **508-pass baseline** remain independently unverified.

**VERDICT: NO-GO**
