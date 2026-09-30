# Archive Find Peaks round 6 — run B (commit c6358d9; codex exec, reasoning high)

- **MAJOR — Empty skip reasons bypass the zero-skip requirement.** [scripts/ci_node_events_reporter.mjs:15](/Users/skyefortier/xps-app/.claude/worktrees/archive-find-peaks/scripts/ci_node_events_reporter.mjs:15) converts `d.skip === ""` to `false`. Reproduced on Node **22.22.2**, with process isolation and both reporters: **508 passing tests, two TODOs**, plus `describe('Find Peaks', { skip: '' }, () => {})`. TAP reports the empty suite as `# SKIP`; the structured reporter records `skip:false`. Node excludes skipped suites from its skipped counter, so every reconciliation succeeds: **Node exit 0; guard CLI exit 0**, including `--expect-files`. This reproduction hides an empty skipped suite, not skipped child assertions. Preserve directive presence independently of reason truthiness, apply the same correction to `todo`, and add regression cases.

Validation: **364 unmodified JS tests passed**, and their stream passed the guard. Adversarial early exits, empty files, load failures, hook failures, timeouts, cancellations, late errors, nested skips, deleted/duplicated results, concatenation and truncation were rejected. Registration inspection found **510 tests: 508 ordinary and two TODOs**, with no machine-dependent registration condition found.

Workflow reporter pairing, stale-file removal, `pipefail`, and `always()` appear correct. Runtime HTML remains equivalent to `main` except for comments and the removed menu button; backend, serialization and shared Run Fit code are unchanged. No additional launch or cached-result/provenance display path emerged. The archive test rejects `main`.

Full Python/browser suites and the fresh Ubuntu green run remain unverified: backend imports hit the read-only temporary-directory restriction. No files changed.

**VERDICT: NO-GO**
