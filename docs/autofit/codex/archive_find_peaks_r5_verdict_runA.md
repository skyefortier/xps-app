# Archive Find Peaks round 5 — run A (commits b94a847 + e6e617a; codex exec, reasoning high)

- **MAJOR — Synthetic file successes count as executed tests.** [scripts/ci_check_node_events.py:57](/Users/skyefortier/xps-app/.claude/worktrees/archive-find-peaks/scripts/ci_check_node_events.py:57) accepts every passing `kind: "test"` result. Node also uses that kind for a file that exits successfully without running its tests. Reproduced under **Node 22.22.2**, with process isolation and both reporters: one file supplies **507 real passes and two TODOs**; another calls `process.exit(0)` before registering its assertion. Node substitutes a passing file result, producing **508 passed, two TODOs**. **Node exit 0; guard CLI exit 0 with the workflow’s exact floor.** Empty files and an immediate exit inside a lone test also bypass it. Distinguish file-level successes from completed tests and validate per-file completion; the global stream’s `end` does not establish that every child finished its tests.

- **MINOR — Missing result records can evade summary reconciliation.** [scripts/ci_check_node_events.py:67](/Users/skyefortier/xps-app/.claude/worktrees/archive-find-peaks/scripts/ci_check_node_events.py:67) checks `passed`, but ignores summary `todo`, `tests`, `suites` and `topLevel`. Two independently reproduced cases:
  - Generate 508 passes and three TODOs, then remove one TODO result line. The untouched summary still says `todo: 3`, but **guard exit 0**.
  - Generate 508 passes and a skipped Find Peaks suite, then remove its suite-result line. The summary still records the additional suite, but **guard exit 0**.
  
  Reconcile all applicable counters and require results before the terminal summary. These are log-integrity gaps; ordinary process failures remain protected by `pipefail`.

Verification: **364 actual JS tests passed**, and their structured stream passed the guard. Load errors, hook failures, timeouts, cancellations, late uncaught errors and nested skips were rejected. Registration inspection found **510 tests: 508 ordinary, two TODOs**; no machine-dependent registration condition emerged. Workflow destination pairing, stale-file removal, `pipefail` and `always()` appear correct.

The archive implementation remains equivalent to main after removing comments and the menu button. Backend, serialization and shared Run Fit infrastructure are unchanged; no additional launch or cached-result/provenance display path emerged.

The full JS attempt timed out; backend imports independently hit the read-only temporary-directory restriction. Full Python/browser suites and the green Ubuntu baseline were not verified. No files changed.

**VERDICT: NO-GO**
