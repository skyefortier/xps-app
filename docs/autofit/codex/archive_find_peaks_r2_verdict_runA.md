# Archive Find Peaks round 2 — run A (commit 9593e13; codex exec, reasoning high)

- **MAJOR — The guard counts skipped tests as executed.** [scripts/ci_check_node_tap.py:16](/Users/skyefortier/xps-app/.claude/worktrees/archive-find-peaks/scripts/ci_check_node_tap.py:16) checks Node’s total `tests`, which includes skips, and never limits `skipped` or `todo`. Reproduced with Node 22: **510 tests, 0 passes, 510 skipped** gives Node exit **0** and guard exit **0** (`JS suite guard ok`). Thus skipped Find Peaks tests can leave CI green without executing their assertions, violating the retention requirement. Count executed tests and explicitly constrain skips/TODOs, allowing only the documented exceptions.

Other checks:

- A real failing assertion produced Node exit **1** and guard exit **1**; the workflow’s `pipefail` preserves that failure. The glob, Python dependencies and referenced fixtures appear suitable for a fresh checkout.
- Unit B’s corrected **0.83–2.5×** range matches `08a51d9`. Constant variance scaling cancels from the support F ratio and lmfit’s scaled parameter covariance.
- Runtime HTML remains equivalent to main apart from the removed menu button. Backend, serialization and shared fitting code remain unchanged; no additional launch or cached-result display path found.

Validation: **128 focused JS tests passed**. Full-suite verification was obstructed by Python’s temporary-directory requirement in this read-only sandbox; Ubuntu CI and browser suites were not rerun.

**VERDICT: NO-GO**
