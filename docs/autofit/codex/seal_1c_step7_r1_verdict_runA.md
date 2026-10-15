Found **two MAJOR issues and two MINOR issues**. No BLOCKER findings.

1. **Producers and reinstalls: seal-only publication is implemented, but verification recovery is incomplete — MAJOR.**

   Run Fit/Use this solution, Auto-Fit, and local/Batch finish with frozen `{seal}` results. The local engine still temporarily creates a legacy result before replacing it; both page callers supply `options.seal`. See [index.html:10299](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:10299), [index.html:10914](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:10914), and [index.html:10945](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:10945).

   However, this sequence strands an installed fit **PENDING indefinitely**: Run Fit A succeeds and starts verification; Run Fit B supersedes its operation but fails; A’s verification then arrives and is discarded. B’s failure path never requests background verification. I reproduced preservation of A’s result with **no cached verdict and no outstanding attempt**. See [index.html:9477](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:9477) and [index.html:10350](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:10350).

   Inactive Auto-Fit rollback also returns before `_ensureVerified`; an extracted-function probe confirmed zero verification triggers after reinstalling the captured seal. See [index.html:8032](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8032). Recovery needs to cover failed/discarded operations and both rollback branches.

2. **Auto-Fit: publication gates are correct, but cancellation and timeout coverage is incomplete — MAJOR.**

   The commit path requires both outcomes to count under current numerics/epoch, a consistent aggregate, a successful staged commit, and `sealedState === 'current'` before publication. See [index.html:8922](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8922).

   During confirmation, however, the fit timer has already been cleared, verification fetches receive no abort signal, and cancellation is checked only **after both promises resolve**. A stalled verification therefore leaves the busy overlay and provisional workspace in place despite Cancel. I reproduced two outstanding verification requests, zero active timeouts, and no rollback after cancellation; rollback happened only after releasing the replies. See [index.html:8880](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8880), [index.html:8913](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8913), and [index.html:9359](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:9359).

   **MINOR — transaction cleanup:** `_commitStaged` caches the verdict before the final state gate. If that gate rejects the seal, rollback does not remove its cache entry. Earlier failure exits also leave the transaction in `_stagedTxns`, allowing late checks to retain answers for an abandoned transaction. This falls short of the requested “nothing cached unless published” contract. See [index.html:8935](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8935), [index.html:9445](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:9445), and [index.html:9462](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:9462).

3. **Old authorities and legacy behavior: no additional regression found.**

   The reviewed sealed readers dispatch before legacy keys/support, and saved seals bypass legacy reconstruction. See [index.html:8234](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8234), [index.html:9725](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:9725), and [index.html:14139](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:14139).

   The committed census contains 121 cases: 81 LEGACY, 40 dropped, zero seals, identical restore decisions and re-saves except the permitted fields, and no page errors. The comparison code supports that claim for this corpus. See [seal_legacy_census.py:103](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/scripts/seal_legacy_census.py:103) and [legacy_census.json:1](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/docs/findings/seal-1c/legacy_census.json:1).

4. **Spectrum and export fixes: correct in the reviewed paths.**

   STALE spectrum convenience fields now use the live model/window, with matching residuals and Results’ area definition. Both TSV paths and CSV append state/provenance after existing content; XLSX appends them after existing Info rows. These changes follow Q5/F1 and the owner’s append-only rule. See [index.html:13553](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:13553), [index.html:14348](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:14348), [index.html:14371](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:14371), and [index.html:14892](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:14892).

5. **Tests: mostly sound ports, with one demonstrated weakening — MINOR.**

   The Auto-Fit success-toast assertion now accepts any three-decimal statistic instead of checking the expected value. An in-memory mutation announcing `999.000` passed all five tests in that file. See [autofit_refit.test.js:90](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/tests/js/autofit_refit.test.js:90).

   The new failure test covers immediate abort/mismatch responses, but “changes nothing” compares only peaks, fit JSON, and three charge controls. It does not exercise stalled confirmation cancellation/timeouts or transaction/cache cleanup. The older recovery test manually calls `_ensureVerified`, masking the missing producer recovery trigger. See [test_browser_seal_step7.py:144](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/tests/test_browser_seal_step7.py:144) and [test_browser_seal_step4.py:187](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/tests/test_browser_seal_step4.py:187).

Validation: **112 targeted JavaScript tests passed**; read-only runtime probes reproduced the lifecycle defects. Browser suites and the two-server census were not rerun. No files changed.

**VERDICT: NO-GO.**
