No BLOCKER or MAJOR findings. The round 1 major findings are fixed.

- **MINOR — the alternative fixture remains inconsistent with a real server response.** In [scattered_starts.test.js:310](/Users/skyefortier/xps-app/.claude/worktrees/linked-child/tests/js/scattered_starts.test.js:310), the alternative parent centre is `284.45`, although that parent is locked at `284.40`. Consequently, the previewed child and retained parent do not satisfy the configured offset. The test genuinely proves locked-child copying and fails under the old rule; its “solution the server could return” comment remains inaccurate. Align the alternative parent centre and child offset. **Requires non-physical inputs: yes—an inconsistent synthetic response.**

Verified:

- Applied server expressions originate in link constraints. Genuine unlinked locks remain protected; shape guards, including Voigt mix preservation, are intact.
- Run Fit, Auto-Fit and alternative adoption use the corrected application function. The Python twin now handles both expression-bearing responses and plain-value linked records. Local fitting and Batch Fit already synchronize linked values regardless of locks.
- History and restore copy stored peaks. New snapshots retain corrected values; previously stale snapshots are not repaired.
- Measurement reproduced: **67 linked children, 12 carrying locks, zero active-parameter discrepancies, nine inactive Voigt mix differences**. All 12 locks are inactive `fixCaM` flags. The committed-data conclusion holds.
- **70/70 tests passed** across the two relevant files using an in-memory bootstrap for read-only Python initialization. All six added tests fail with the old page rule. Restoring only the old LA `m` rule fails the explicit `caM` assertion; restoring the old Python twin fails parity.
- No unrelated runtime changes found. No files modified. Full repository suite not run.

VERDICT: GO
