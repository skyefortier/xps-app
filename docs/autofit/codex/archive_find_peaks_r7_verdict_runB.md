# Archive Find Peaks round 7 — run B (commit 900c0c7; codex exec, reasoning high)

No BLOCKER, MAJOR or MINOR findings at `900c0c7`.

- Round-6 fixes hold: empty-reason directives are preserved; splice tests use independent rosters and passing baselines.
- On Node **22.22.2**, adversarial isolated-file runs rejected skips at multiple nesting levels, empty files, premature exits, load/hook failures, timeouts, cancellations and late errors—even alongside 508 genuine passes.
- Concatenation, truncation and deleted/duplicated results or file summaries were rejected. A generated **508-pass/two-TODO** run passed the guard CLI; stopping one test’s registration failed it.
- **364 unmodified JS tests passed**, and their structured stream passed the guard. Registration inspection found **510 tests: 508 ordinary, two TODOs**, with no machine-dependent registration condition found.
- CI reporter destinations, stale-file removal, `pipefail` and `always()` are correct on inspection.
- Runtime HTML remains equivalent to `main` apart from comments and the removed menu button. Backend, serialization and shared Run Fit infrastructure are unchanged. No additional launch or cached-result/provenance display path found. The archive test rejects `main`.

Full Python/browser suites and a fresh Ubuntu green run remain independently unverified: backend imports fail because this read-only sandbox has no writable temporary directory. No files changed.

**VERDICT: GO**
