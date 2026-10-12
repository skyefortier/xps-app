No BLOCKER or MAJOR findings. Round-one blocking findings are fixed.

**MINOR — the alternative fixture remains inconsistent with its parent’s lock.** In [scattered_starts.test.js:310](/Users/skyefortier/xps-app/.claude/worktrees/linked-child/tests/js/scattered_starts.test.js:310), the alternative gives the parent centre `284.45`, although it is locked at `284.40`. The preview consequently contains child centre `291.10`, while its displayed parent plus offset gives `291.05`. Align the alternative with the parent’s lock. The test genuinely detects the write-back regression, but its “solution the server could return” comment is still incorrect. **Requires inconsistent synthetic inputs: yes.**

Verification:

- The fitted parameters consumed by this write-back receive server expressions through link constraints. Genuine unlinked locks remain protected; shape guards, including Voigt mix preservation, remain intact.
- Run Fit, Auto-Fit and successful alternative adoption use the corrected application function. Batch Fit’s local engine already synchronizes linked fields regardless of locks. History/restore copy stored peaks; previously stale records remain unrepaired.
- Measurement reproduced: **67 linked children, 12 carrying locks, zero active-parameter differences, nine inactive Voigt mix differences**. All 12 locks are inactive `fixCaM` flags. The committed-data conclusion holds.
- **70/70 relevant tests passed** using an in-memory bootstrap for read-only dependency initialization. All six new tests fail with the old page rule. Reverting only LA’s `m` handling fails its strengthened test; reverting the Python twin fails the expanded parity test. Reverting only the alternative expression marking also fails.
- No unrelated runtime changes found. No files modified. This was targeted verification, not a full-suite run.

VERDICT: GO
