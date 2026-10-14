**One remaining MAJOR finding under the requested exact-behaviour contract: `_applyProjected` loses signed-zero changes.** The five round-1 findings are otherwise addressed.

1. **Requests and capture timing match; live application is not universally identical.**

   I compared **2,880 request bodies** against code extracted from `34ce8ba`, covering all eight shapes, six backgrounds, five methods, links, locks and all three producers. Values and field presence matched. Capture remains before each upload await: [index.html:9221](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9221), [index.html:8509](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8509), [index.html:8573](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8573). Auto-Fit’s earlier confirmation await is unchanged.

   **MAJOR — the `p[k] !== q[k]` guard skips `-0 → +0` and `+0 → -0`:** [index.html:7111](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7111).

   Reproduced using the actual baseline application:

   ```js
   // Live/snapshot: Gaussian, center: -0, fixCenter: false
   // Reply: center: { value: 0, expr: null }

   Object.is(baseline[0].center, 0)     // true
   Object.is(newLive[0].center, -0)    // true
   _sameModel(projected, newLive)     // false
   ```

   This is a finite-number edge, not a demonstrated visible spectral change. Nevertheless, it violates both exact application and the explicit `Object.is` model contract. Use `!Object.is(p[k], q[k])` for this guard and add a regression test.

2. **Projection purity and isolation are fixed.**

   `project` clones the snapshot and reply parameters; installation clones `_backendParams` again. No shared mutable parameter object remains between snapshot, reply, projection and live peaks. [index.html:7070](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7070), [index.html:7113](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7113)

   The omitted-component/parameter fix works, and presentation fields remain untouched. **131,072 additional ordinary-value comparisons** matched the old application across shapes, all 13-lock combinations and adopted starts. Auto-Fit applies each reply against its respective snapshot. Exact equivalence still has the signed-zero exception above.

3. **Charge correction and successful Auto-Fit derivation match.**

   **648 comparisons against the baseline function** matched preset/custom/none/unknown methods, inherited-property names, reference text, display branches and movement arithmetic. Own-entry lookup fixes round 1; `delta !== 0`, `parseFloat` and `toFixed(1)` retain their meanings. [index.html:5482](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5482), [index.html:5520](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5520)

   **36 successful-transition comparisons** matched graphite/fallback selection, raw centre, `toFixed(3)`, `'284.50' → '284.5'`, zero/nonzero Δ, ROI/background/centre/anchor movement and centre locks. I found no omitted context field changed by that transition. Rendering and background acceptance were stubbed in these comparisons. [index.html:8037](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8037), [index.html:8082](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8082)

4. **The structural migrations retain their protections; the pins are sound within their coverage.**

   In-memory mutations were rejected for removing inclusive `+1`, changing the scattered-start trigger, removing the required-anchor field and moving capture after upload. See [background test:127](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/js/bg_window_indices.test.js:127), [starts test:247](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/js/scattered_starts.test.js:247), [anchor test:57](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/js/autofit_required.test.js:57), [ownership test:114](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/js/per_tab_state.test.js:114).

   Run Fit’s independent fixtures remain, and Auto-Fit now independently pins its anchor request, closing the shared-builder oracle gap. The final-transition test compares model, context, energies and body. These pins detect changes exercised by their scenarios; they do not cover signed zero. [browser tests:124](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/test_browser_seal_requests.py:124), [browser tests:158](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/test_browser_seal_requests.py:158), [browser tests:179](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/test_browser_seal_requests.py:179)

5. **No numerical tolerance or conflicting input parser was introduced.**

   `_sameModel` now correctly handles key order, absent versus undefined, NaN and signed zero. The remaining inconsistency is its `Object.is` equality versus installation’s `!==` equality. [index.html:7085](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7085)

Read-only; checkout unchanged. **135 focused JS tests passed.** Browser tests and full pytest were not rerun.

**VERDICT: NO-GO.**
