No remaining **BLOCKER or MAJOR** found. The round-1 runtime defects are resolved; two **MINOR test-coverage limitations** remain.

1. **Round-1 findings**

   | Finding | Status |
   |---|---|
   | Failed successor strands an installed seal PENDING | **Resolved.** Discarded producer replies schedule background recovery after clearing their attempt. [index.html:9485](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:9485) |
   | Active rollback encounters an obsolete producer attempt | **Resolved.** That attempt now hands over when it settles. Probes confirmed recovery with rollback both before and after its reply. [index.html:9491](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:9491) |
   | Inactive rollback omits verification | **Resolved.** It verifies the reinstated seal before returning. [index.html:8046](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8046) |
   | Confirmation ignores Cancel and has no timeout | **Resolved.** Both checks receive the operation signal; confirmation has its own timer, and abort leads to rollback. [index.html:8853](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8853), [index.html:8914](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8914) |
   | Rejected commit retains its cached verdict | **Resolved.** Rejection deletes both verdict and unreachable entries. [index.html:8942](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8942) |
   | Unpublished transaction remains registered | **Resolved.** `finally` abandons it; late replies cannot append answers afterward. [index.html:8977](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8977), [index.html:9453](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:9453) |
   | Success-toast assertion accepts any statistic | **Resolved.** It requires `2.000` again. An in-memory `999.000` mutation failed this assertion. [autofit_refit.test.js:91](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/tests/js/autofit_refit.test.js:91) |
   | Missing lifecycle regression coverage | **Substantially resolved, with the limits below.** |

2. **Can an installed seal still be stranded PENDING without an attempt, answer, or future trigger?**

   **No such path found among the requested operation orderings.** Recovery now covers discarded producer replies and both rollback branches. Contextual undo, activation, history restore, and both loaders supply verification triggers; local/Batch seals require no server attempt. [index.html:2431](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:2431), [index.html:3327](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:3327), [index.html:17680](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:17680), [index.html:13999](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:13999), [index.html:14277](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:14277).

   A verification request that never settles can still remain PENDING **with an outstanding attempt**; background verification has no timeout. That is outside the stranded state specified in this question. [index.html:9480](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:9480)

3. **Auto-Fit failure restoration and cleanup**

   **Yes for the listed failures, subject to the intentional ownership exceptions.** Publication requires both counting, consistent answers and a CURRENT final state. Cancel/timeout, unreachable responses, either mismatch, and tab-switch rejection reach restoration and transaction cleanup. [index.html:8917](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8917), [index.html:8927](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8927), [index.html:8953](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8953).

   Supersession deliberately preserves the successor’s workspace instead of restoring over it; closed owners are not resurrected. Both are appropriate stated limits. [index.html:8955](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8955), [index.html:8022](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/templates/index.html:8022)

   Extracted-function probes passed Cancel and simulated timeout during both uploads, both fits, and confirmation; independent anchor/final failures; rejected-commit cache cleanup; and inactive rollback.

4. **Tests and assertion strength**

   The four new tests discriminate the named defects: automatic recovery, cancellation without releasing held replies, final-check-only mismatch with transaction deletion, and inactive restoration without activation. Corresponding in-memory mutation probes reproduced the failures when fixes were removed. The browser tests themselves were **not rerun**. [test_browser_seal_step7.py:310](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/tests/test_browser_seal_step7.py:310)

   Two **MINOR** coverage issues remain:

   - The new confirmation tests still compare only peaks, fit, and three charge controls. They do not directly pin confirmation timeout or cached-verdict deletion after final-state rejection. Extend them with the fuller workspace/history comparison and those two cases. [test_browser_seal_step7.py:144](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/tests/test_browser_seal_step7.py:144)
   - Across the full step-7 diff, the legacy save/load port drops its previous `Object.isFrozen(...) === false` assertion. This is a small coverage loss, not an observed runtime regression. Round-2 changes themselves strengthen assertions. [test_browser_seal_step6.py:354](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s7/tests/test_browser_seal_step6.py:354)

Validation: **270 targeted tests passed**; three Python-backed checks failed because the read-only sandbox provides no writable temporary directory. Lifecycle and mutation probes ran entirely in memory. No files changed.

**VERDICT: GO**
