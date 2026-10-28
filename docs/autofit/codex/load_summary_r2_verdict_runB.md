Review scoped to **390acab**; later working-tree edits are excluded. Line numbers refer to that commit.

1. **MAJOR — Rejected fit files immediately lose their error message.** [templates/index.html:13970](/Users/skyefortier/xps-app/.claude/worktrees/load-notices/templates/index.html:13970)  
   `fromJSON()` displays “Fit not loaded” and returns on validation failure. `_applyFitJSON()` then unconditionally dismisses that error and announces success.

   Reproduction: with a spectrum active, load a `.fit.json` containing `{"version":1,"peaks":[{"id":1,"color":"invalid"}]}`. Executing the committed functions produced a **hidden error box** and **“Fit applied to active tab: 1 peak.”** The model was not applied. Return an explicit success result and clear/report success only when application succeeds. The replacement test covers only successful imports.

2. **MINOR — Load titles remain unbounded, including in timed toasts.** [templates/index.html:15510](/Users/skyefortier/xps-app/.claude/worktrees/load-notices/templates/index.html:15510), [templates/index.html:834](/Users/skyefortier/xps-app/.claude/worktrees/load-notices/templates/index.html:834)  
   Project `sample_name` and spectrum `spectrumName` flow into the title without a length limit. When there are no warnings, that title reaches the non-wrapping, four-second `notify`. Reproduced a **1,416-character green notification** through the committed functions.

   With warnings, an extremely long title also defeats body readability: the non-shrinking header can exceed the panel’s maximum height and squeeze the scrolling body to zero height. For example, extend the phone test’s title to several thousand characters. This layout consequence is from CSS inspection; browser execution was unavailable. Bound displayed titles and ensure the body retains usable space.

3. **MINOR — One arithmetic refusal still incorrectly claims record damage.** [templates/index.html:15447](/Users/skyefortier/xps-app/.claude/worktrees/load-notices/templates/index.html:15447)  
   The reason beginning **“its data less its background are not finite numbers in floating point…”** falls through to `damaged`, producing **“the saved fit is incomplete or inconsistent.”** This establishes an arithmetic overflow, not an inconsistent saved record.

   Reproduced the classification using the committed functions. An existing numerical reproduction is in [tests/js/background_not_converged.test.js:1004](/Users/skyefortier/xps-app/.claude/worktrees/load-notices/tests/js/background_not_converged.test.js:1004). The new reason-mapping test omits this reason. Route it to `uncheckable`.

The remaining dispositions check out:

| Disposition | Verification |
|---|---|
| Phone dismissal | Height cap, scrolling body, wrapping and fixed header implemented; extreme-title exception above. |
| Persistent load errors | Listed error paths converted and values/details bounded; rejected-fit regression above. |
| Stack pruning detail | Names/counts retained; per-stack legend uses the runtime WeakMap, correctly allowlisted and not serialized. |
| Revised wording | Corrections present; remaining overflow misclassification above. |
| Voigt overlap | Separate counts attach to the appropriate background line. |
| Later successful loads | Raw, fit/setup, project, spectrum and folder paths clear or replace the summary. |
| Refit proposal | Remains documentation only; undo, concurrent edits, transport fallback and alternative confirmation corrected. |
| Test gaps | Real server-fit save/reload, nonempty groups, FileReader error, replacement and phone tests added. Exceptions above remain uncovered. |

I found no additional concatenated per-tab load/restore toast. Restore decisions are unchanged: the legacy checker, grid matching, peak reconstruction, drop function, seal installer and stale-reason function are byte-identical to base. Per-tab Results explanations remain intact.

Validation against committed sources: **118 of 121 JS checks passed** across the acceptance, per-tab-state and background suites. Three failed during Python setup because temporary-directory creation is forbidden. Browser launch was blocked by the same read-only restriction. **Full pytest status remains unverified.**

VERDICT: NO-GO
