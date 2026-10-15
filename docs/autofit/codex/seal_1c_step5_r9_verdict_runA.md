No new BLOCKER, MAJOR, or MINOR correctness finding. The round-8 defects are resolved; the stated coverage limits remain.

1. **Round-8 findings**

| Finding | Status |
|---|---|
| Stale/unreadable R status depends on adjacent `rFactor` | **Resolved.** Both missing and poisoned copies now produce `R: —` with the sealed-state reason. [index.html:14691](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14691) |
| Engine-card test cannot detect legacy fallback | **Resolved.** The fixture now supplies truthy `backendResult`; unreadable cases require no lmfit card. [test_browser_seal_step5.py:784](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:784), [808](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:808) |
| Provenance test cannot detect copied local status | **Resolved.** A readable LOCAL seal receives poisoned metadata; assertions require `converged`, the recorded designation and recorded χ²ᵣ. [test_browser_seal_step5.py:818](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:818) |
| PNG drawing coordinates and statistic-source discrimination | **Retained coverage limit.** The annotation test captures text, with agreeing recorded/legacy χ². [test_browser_seal_step5.py:675](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:675) |
| Stale chart comparison excludes Data and residual chart | **Retained stated limit.** The stack comparison remains broader. [test_browser_seal_step5.py:719](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:719) |

The earlier readability, designation and provenance fixes remain intact: unreadable seals designate nothing, and readable local provenance comes from the record. [index.html:10144](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10144), [10229](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10229).

2. **Switch OFF**

No additional observable difference found beyond the previously stated renderer/frozen-seal guards and missing-statistic formatting exceptions. `_readsSeal` requires the switch; chart, stack and `.fit.json` retain their legacy paths when OFF. [index.html:9423](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9423), [11871](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11871), [12386](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12386), [13150](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13150).

3. **Switch ON, any sealed state**

No remaining **authoritative fallback** to adjacent fields found in the step-5 consumers. This is not literally zero property access: Results still destructures `backendResult`, and R updates pass/compare `fr.rFactor`; those accesses no longer determine the displayed sealed values or missing-value presentation. [index.html:10889](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10889), [10934](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10934), [14691](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14691).

Project/spectrum persistence still reads legacy fields; its migration remains explicitly step 6, outside this verdict. [index.html:13233](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13233), [plan:357](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/docs/superpowers/plans/2026-10-14-seal-1c-page.md:357).

4. **Do the new tests detect their named defects?**

**Yes, by assertion inspection and focused in-memory mutation checks.** Restoring the old R code breaks bare/poisoned equality; restoring the engine fallback shows lmfit for unreadable seals; restoring `status: fr.status` returns `POISON`. The relevant assertions are at [test:796](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:796), [808](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:808), and [829](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:829).

Validation: **186/187 selected JavaScript tests passed**; backend parity failed because temporary-directory creation was prohibited. Chromium startup was blocked by the same restriction, so browser assertions were not executed. No files changed.

VERDICT: GO
