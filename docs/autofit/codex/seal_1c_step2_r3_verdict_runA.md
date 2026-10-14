**One MAJOR finding remains: “Use this solution” can overwrite a locked live value.** The specific round-1 fixes and round-2 free-field signed-zero fix are verified.

1. **Behaviour is not exactly unchanged. — MAJOR**

   `_applyProjected` transfers every field associated with a reported parameter, even when `_applyBackendParams` preserved that field because it was locked. [templates/index.html:7112](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7112)

   Reproduced using the actual `_altPeaks` and baseline application extracted from `34ce8ba`:

   ```text
   Live DS peak:       dsGamma = -0, fixDsGamma = true
   Adopted start:      dsGamma = +0
   Reply gamma_asym:   { value: 0, expr: null }
   Baseline live:      dsGamma = -0
   HEAD live:          dsGamma = +0
   ```

   The adopted start differs because `_altPeaks` uses JSON cloning, which converts `-0` to `+0`. The baseline honours the live lock; HEAD copies the snapshot’s zero back into the live peak. [templates/index.html:9121](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9121)

   Preserve the baseline’s locked-field write behaviour and add a regression through the real `_altPeaks` path. This is an exact-value discrepancy, not a demonstrated spectral-error magnitude.

   **Requests:** 2,880 comparisons against extracted baseline code matched across all three producers, eight shapes, six backgrounds, five methods, links and locks, including field presence. Capture remains before upload: [Run Fit:9222](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9222), [Auto-Fit anchor:8510](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8510), [final:8574](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8574). Auto-Fit’s earlier confirmation await remains unchanged.

2. **Projection is pure and detached; application equivalence has the exception above.**

   `project` clones the snapshot and reply parameters; installation clones `_backendParams` again. No mutable alias remains between those objects for the page’s model/reply data. Presentation fields stay live, and the round-1 omitted-component/parameter cases pass. [project:7070](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7070), [installation:7105](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7105)

   Auto-Fit applies each reply against its own snapshot. [anchor:8554](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8554), [final:8604](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8604)

3. **Charge correction and successful Auto-Fit derivation match in the comparisons performed.**

   **648 baseline comparisons** matched all preset/custom/none/unknown branches, inherited-property names, reference writes, display branches, zero/nonzero Δ and movement arithmetic. Own-entry lookup fixes round 1; `parseFloat` and `toFixed(1)` retain their meanings. [templates/index.html:5482](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5482)

   **36 successful-transition comparisons** matched graphite/fallback selection, raw centre, `toFixed(3)`, `'284.50' → '284.5'`, shifts, ROI/background fields, centres, anchors and centre locks. I found no omitted live-context field changed by that transition. Rendering and acceptance gates were stubbed in these comparisons. [templates/index.html:8083](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8083)

4. **The structural migrations retain their original protections; the pins miss the MAJOR case.**

   In-memory mutations failed the respective tests when removing inclusive `+1`, changing the scattered-start trigger, dropping the required-anchor value, or moving capture after upload. Reverting `Object.is` also fails the new signed-zero test.

   The six original request fixtures remain unchanged from `be2e58a`. Auto-Fit’s independent anchor pin closes the previous shared-builder gap; its final-transition pin checks model, context, energies and body. [browser pins:124](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/test_browser_seal_requests.py:124), [158](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/test_browser_seal_requests.py:158), [179](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/test_browser_seal_requests.py:179)

   However, the “Use this solution” test constructs its start with `structuredClone`, bypassing the real JSON clone; the signed-zero regression tests an unlocked field. Neither catches the finding. [seal_step2.test.js:86](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/js/seal_step2.test.js:86), [200](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/js/seal_step2.test.js:200)

5. **No new numerical tolerance or conflicting numeric parser was introduced.**

   `_sameModel` correctly distinguishes signed zero, NaN/null and absent/undefined while ignoring key order. The remaining problem is transferring a locked snapshot value after the existing JSON clone normalised it. [templates/index.html:7085](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7085)

Read-only review; checkout unchanged. **136 focused JS tests passed.** Browser tests and full pytest were not rerun.

**VERDICT: NO-GO**
