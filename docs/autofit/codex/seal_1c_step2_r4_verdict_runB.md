**No BLOCKER, MAJOR or MINOR findings remain.** The prior-round fixes are verified.

1. **Producer behaviour matches the baseline.**  
   All **30,720 differential request comparisons** matched extracted `34ce8ba` code, including values and field presence, across three producers, eight lineshapes, links, locks, eight backgrounds and five methods. Run Fit captures before upload at [index.html:9214](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9214). Auto-Fit captures each request synchronously through [index.html:8380](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8380); its earlier confirmation await is unchanged.

   Live application now uses the baseline loop and unchanged `_applyBackendParams`, with the intended independent `_backendParams` copy. Presentation fields, omitted parameters and unnamed components retain their previous treatment. Support is still stamped separately, including on unnamed peaks, as before. [index.html:7217](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7217), [index.html:7903](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7903)

2. **`project` is pure and detached; `_applyProjected` is gone.**  
   **131,072 comparisons** matched baseline parameter application across all combinations of the 13 locks, all shapes, and expression/non-expression parameters. Snapshot and reply evidence are deeply copied. Nested mutation checks found no sharing between snapshot, projection, reply and live parameter evidence. [index.html:7070](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7070)

   The actual `_altPeaks` round-3 reproduction now preserves live locked `-0`, while projecting the adopted snapshot’s `+0`. That distinction is intentional under amended §4: application honours the live lock; projection honours the snapshot lock. Both match baseline application to their respective inputs. [index.html:9111](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9111), [plan:96](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:96)

3. **Charge correction and successful Auto-Fit derivation match.**  
   **1,536 baseline comparisons** passed for presets, custom, none, unknown/inherited names, reference writes, display branches, zero/nonzero Δ and `toFixed(1)` movement. The own-property lookup resolves round 1. [index.html:5482](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5482), [index.html:5500](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5500)

   **192 derivation comparisons** matched graphite/fallback selection, raw centre, `toFixed(3)`, `'284.50' → '284.5'`, Δ, ROI/background fields, centres, anchors and centre locks. No omitted live-context field changed by the successful transition was found. Rendering and background gates were stubbed in these arithmetic comparisons. [index.html:8030](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8030), [index.html:8075](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8075)

4. **Structural protections remain; pins are sound within their coverage.**  
   In-memory mutations failed the corresponding tests for inclusive endpoints, scattered-start triggering, required-anchor forwarding and capture after upload. [background:127](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/js/bg_window_indices.test.js:127), [starts:247](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/js/scattered_starts.test.js:247), [anchor:57](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/js/autofit_required.test.js:57), [ownership:108](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/js/per_tab_state.test.js:108)

   The six original fixtures are unchanged from `be2e58a`. Independent Auto-Fit anchor fixtures close the shared-builder oracle gap; the final-transition pin compares model, context, energies and body. Changes exercised by these scenarios fail the pins. [browser tests:124](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/test_browser_seal_requests.py:124), [browser tests:158](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/test_browser_seal_requests.py:158), [browser tests:179](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/test_browser_seal_requests.py:179)

5. **No conflicting reading or new numerical tolerance found.**  
   Request parsing retains the existing conversions; projection and live application share `_applyBackendParams`. `_sameModel` preserves `Object.is` numeric distinctions, ignores key order, and distinguishes absent from undefined. [index.html:7036](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7036), [index.html:7085](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7085)

Read-only review completed; checkout unchanged. **137 focused JS tests passed.** Browser tests and full pytest were not rerun here.

**VERDICT: GO**
