# Archive Find Peaks round 3 — run B (commit 312396a; codex exec, reasoning high)

- **MAJOR — Skipped suites bypass the zero-skip guard.** [scripts/ci_check_node_tap.py:31](/Users/skyefortier/xps-app/.claude/worktrees/archive-find-peaks/scripts/ci_check_node_tap.py:31) checks only the summary’s `skipped` count. Node 22 excludes skipped **suites** from that count. Reproduced with 504 passing tests and a nested `describe.skip` containing the actual archive test module: **504 passed, 0 skipped, Node exit 0, guard exit 0**. None of the archive assertions executes. Wrapping this commit’s four archive tests in a skipped suite would leave 504 passes, above the floor. Check TAP skip directives at every nesting level and add a real Node regression test.

- **MINOR — Multiple summaries can conceal failures or truncation.** [scripts/ci_check_node_tap.py:21](/Users/skyefortier/xps-app/.claude/worktrees/archive-find-peaks/scripts/ci_check_node_tap.py:21) retains the last value **per field**, without validating summary boundaries. Concatenating a real failing Node run and a passing run returns **guard exit 0**. A complete green summary followed by a second run ending at `# tests 510` also passes by borrowing earlier fields. Reject duplicate/ambiguous summaries and incomplete trailing runs. The current single-invocation workflow’s `pipefail` still protects ordinary process failures.

Validation: **364 JS tests passed** without Python bridges; the archive test correctly fails against `main`. Real failing assertions, skipped child tests, and crashes before any summary were rejected. Bash `pipefail` preserved Node’s failure. Workflow configuration, Python dependencies and committed fixtures look suitable for Ubuntu; Ubuntu, Python and browser suites were not rerun.

Earlier implementation checks still hold: runtime HTML differs only by the removed menu button; backend, shared fitting code and serialization are unchanged. Unit B’s corrected range matches its cited record.

**VERDICT: NO-GO**
