No remaining **BLOCKER or MAJOR** found. The implementation fixes the round-1 defects. One **MINOR test-coverage gap** remains.

1. **Round-1 findings**

| Finding | Status |
|---|---|
| **MAJOR:** discarded producer verification strands an installed seal | **Resolved.** The discarded attempt schedules background recovery when its seal remains installed. This also recovers an obsolete producer attempt encountered by active rollback. [index.html:9485](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:9485) |
| **MAJOR:** inactive Auto-Fit rollback skips verification | **Resolved.** Both inactive and active restoration trigger verification. [index.html:8047](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8047), [index.html:8080](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8080) |
| **MAJOR:** confirmation ignores Cancel and has no timeout | **Resolved.** Both checks receive the operation’s signal; confirmation has its own timer and checks cancellation before publication. [index.html:8853](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8853), [index.html:8915](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8915) |
| **MINOR:** rejected commit retains its cached verdict | **Resolved.** Rejection deletes both verdict and unreachable entries. [index.html:8943](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8943) |
| **MINOR:** unpublished transaction remains registered | **Resolved.** The outer `finally` abandons the transaction; late checks cannot append answers afterward. [index.html:8978](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8978), [index.html:9453](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:9453) |
| **MINOR:** weakened success-toast assertion | **Resolved.** The stub reads the seal’s statistic and the assertion requires `2.000`. [\_seal_stubs.js:13](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/tests/js/_seal_stubs.js:13), [autofit_refit.test.js:91](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/tests/js/autofit_refit.test.js:91) |
| **MINOR:** insufficient lifecycle tests | **Substantially improved; residual coverage limit.** The new tests cover the named races, but do not directly test confirmation timeout or post-commit cache deletion. Their restoration comparison still omits shift, anchors, windows, provenance and undo/redo. [test_browser_seal_step7.py:144](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/tests/test_browser_seal_step7.py:144) |

2. **Stranded PENDING seals**

I found no remaining supported operation ordering that leaves an installed seal PENDING with neither an attempt nor an answer nor a future trigger.

Run Fit and “Use this solution” start producer checks; local/Batch seals verify locally. Reinstalls trigger background verification through undo context, history, activation, rollback and loaders. Superseded attempts cannot delete newer attempts, and discarded producer replies now hand off automatically. [index.html:10326](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:10326), [index.html:9604](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:9604), [index.html:2431](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:2431), [index.html:3327](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:3327), [index.html:17680](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:17680), [index.html:14277](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:14277).

An outstanding network request can still remain pending; that is distinct from the orphaned state asked about.

3. **Auto-Fit failure handling**

The reviewed paths restore the captured workspace while Auto-Fit still owns it, and terminate the unpublished transaction. Cancellation/timeout reach uploads, fitting and staged verification. Either check’s mismatch/unreachable outcome rejects publication; commit additionally requires counting answers and CURRENT state. [index.html:8810](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8810), [index.html:8927](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8927), [index.html:8940](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8940).

**Supersession deliberately does not restore:** the successor owns the workspace. Closed owners likewise receive no restoration. These are the ownership rules, not cleanup failures. Tab switches restore into the original tab’s record. [index.html:8953](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8953), [index.html:8022](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8022).

4. **Test discrimination and assertion strength**

The new tests target the named defects correctly: recovery without another trigger, cancellation before held replies are released, final-check-only mismatch with transaction termination, and inactive rollback without activation. [test_browser_seal_step7.py:310](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/tests/test_browser_seal_step7.py:310), [332](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/tests/test_browser_seal_step7.py:332), [356](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/tests/test_browser_seal_step7.py:356), [381](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/tests/test_browser_seal_step7.py:381). The step-4 test now requires automatic recovery. [test_browser_seal_step4.py:187](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/tests/test_browser_seal_step4.py:187). No additional assertion weakening found.

Validation: **253 targeted Node tests passed**; three Python-backed checks failed because the sandbox has no writable temporary directory. Extracted-function probes passed recovery and Auto-Fit cleanup scenarios, including timeout and rejected-commit cache removal. In-memory mutations removing recovery/cleanup reproduced failures; changing the toast to `999.000` failed the existing assertion. Playwright mutation checks were not independently rerun. No files changed.

**VERDICT: GO**
