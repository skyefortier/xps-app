# Archive Find Peaks round 2 — run B (commit 9593e13; codex exec, reasoning high)

- **MAJOR — The CI guard can pass when no tests execute.** [scripts/ci_check_node_tap.py:16](/Users/skyefortier/xps-app/.claude/worktrees/archive-find-peaks/scripts/ci_check_node_tap.py:16) checks TAP’s total `tests`, which includes skipped tests, while ignoring `pass`, `skipped`, and `todo`. Reproduced with Node 22: **510 skipped, 0 passed, 0 failed → Node exit 0, guard exit 0**. Thus mass-skipping the suite leaves CI green despite the owner’s requirement. It also accepts an incomplete log containing only `# tests 510`. Require a complete summary, enforce an executed/passed-test floor, and bound skips/TODOs explicitly.

Ordinary assertion failures correctly fail Node and the guard; the workflow’s `pipefail` preserves that failure. Inspection found the glob, Python dependencies, and referenced fixture files suitable for a fresh checkout. `setup-node` lacks `always()`, but skipping it after an earlier failure cannot make the job green.

The corrected Unit B range matches `08a51d9`. The constant-factor invariance claim agrees with the support-F implementation and lmfit’s covariance scaling. Round-1 implementation checks still hold: runtime HTML differs only by the removed menu button; backend and shared fitting code remain unchanged.

Validation: **77 focused Find Peaks JS tests passed**; the archive test rejects `main`. The full JS attempt encountered the read-only environment’s temporary-directory restriction during lmfit/dill imports. Python/browser suites and Ubuntu execution were not verified.

**VERDICT: NO-GO**
