No BLOCKER or MAJOR found. **Two MINOR findings remain: R-status presentation still depends on an adjacent legacy field, and two regression assertions do not discriminate their named defects.**

1. **Round-7 findings**

| Finding | Status |
|---|---|
| `_sealDesignation` reads an unreadable record | **Resolved.** `_sealReadableView` checks version, R, O, context and page model, and catches view-construction failure. [index.html:10144](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10144) |
| Unreadable seal falls back to local/unweighted designation and caveat | **Resolved.** Both designation readers suppress legacy fallback when `_readsSeal` holds. [index.html:10141](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10141), [10178](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10178) |
| Results engine card falls back to `backendResult` | **Resolved in implementation; regression coverage incomplete**, below. [index.html:10934](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10934) |
| Provenance falls back beside unreadable seals; readable local provenance copies `fr.status` | **Resolved in implementation.** Unreadable designation returns no fit-derived provenance; readable local status is `'converged'`. Status regression coverage remains incomplete. [index.html:10229](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10229) |
| Unreadable fixture never reaches null designation | **Resolved.** Unknown-version and missing-O cases now assert null designation and null saved metadata. [test_browser_seal_step5.py:771](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:771) |
| PNG coordinates/statistic-source discrimination; stale chart excludes Data and residual chart | **Retained coverage limits.** PNG still captures text with agreeing χ² sources; stale chart comparison still excludes those datasets. [test_browser_seal_step5.py:675](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:675), [720](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:720) |

2. **Switch OFF**

I found no additional observable regression beyond the stated total-renderer/missing-statistic exceptions. The authority gates preserve legacy paths, including chart/stack stored curves and `.fit.json` metadata. [index.html:9423](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9423), [11871](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11871), [12386](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12386), [13150](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13150).

3. **Switch ON, ANY sealed state**

**MINOR — R-status presentation still reads beside the seal.** `_updateRFactorUI` conditions its stale presentation on legacy `rf` truthiness and identity with `state.fitResult.rFactor`. For the same unreadable seal, extracted execution produced:

- Without legacy `rFactor`: blank text, no tooltip.
- With legacy `rFactor`: `R: —`, with the failed-record tooltip.

No poisoned numeric R appears, but the universal isolation guarantee remains false. Derive this presentation from sealed state independently of the adjacent field. [index.html:14690](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14690), [14702](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14702).

4. **Do the new tests detect their named defects?**

**Partly. MINOR — two mutations survive the new fixtures:**

- **Engine-card fallback:** the replacement result omits `backendResult`, so restoring the old fallback still produces no card for unreadable seals. Add a truthy poisoned `backendResult`.
- **Local provenance status:** every variant starts with a server seal; `_provenanceOf` returns null before reaching the changed status expression. Add a readable local seal with poisoned `status` and require `'converged'`.

These gaps are at [test_browser_seal_step5.py:778](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:778) and [791](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:791). In-memory mutations of the actual functions confirmed both survive; strengthened inputs expose both defects. The designation fallback mutation is detected by both unreadable cases; direct-view restoration is detected by the unknown-version case.

Validation: **186/187 selected JavaScript tests passed**; backend parity and browser startup were blocked by temporary-directory permissions. Browser assertions were not executed. No files changed.

**VERDICT: NO-GO**
