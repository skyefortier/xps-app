**One MAJOR finding remains under the requested exact-equivalence criterion: `_applyProjected` loses signed-zero updates.** The five round-one fixes are otherwise addressed.

1. **Requests and capture timing match; live application is not exactly unchanged.**

   I compared **3,840 request objects** against extracted `34ce8ba` code across all three producers, eight lineshapes, locks, links, backgrounds and fitting methods. All matched, including field presence. Request construction remains before each upload await: [index.html:9218](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9218), [index.html:8509](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8509), [index.html:8575](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8575). Auto-Fit’s earlier confirmation await remains unchanged.

   **MAJOR — signed-zero assignment is suppressed** at [index.html:7111](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7111). Reproduced using the actual old `_applyBackendParams`:

   ```js
   // Live DS peak: dsGamma = +0, unlocked
   // Reply: gamma_asym = { value: -0, expr: null }

   // Baseline live dsGamma: -0
   // Projection dsGamma:    -0
   // New live dsGamma:      +0
   ```

   `p[k] !== q[k]` considers these zeros equal and skips the assignment. The reverse transition fails too. Consequently, `_sameModel(live, projected)` returns **false**, whereas the baseline application matches the projection. This is an exact-value discrepancy; I am not claiming a measured fitting-error magnitude.

   Use `!Object.is(p[k], q[k])` for this comparison and add both signed-zero transitions to application tests.

   The omitted-component/parameter fix works: unnamed peaks retain their existing fields and `_backendParams`; presentation fields remain live. [index.html:7105](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7105)

2. **`project` is pure and detached for the page’s model/reply data; application equivalence has the exception above.**

   The snapshot and reply parameters are deep-cloned, and live `_backendParams` receives another clone. I found no remaining mutable alias between snapshot, projection, reply and live parameter evidence. [index.html:7070](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7070), [index.html:7113](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7113)

   “Use this solution” preserves the old application for the covered alternative-start cases, including omitted components/parameters. Auto-Fit supplies its separate anchor and final snapshots correctly. [index.html:8553](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8553), [index.html:8603](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8603)

3. **Charge correction and the successful Auto-Fit derivation match in the comparisons performed.**

   **1,536 old/new charge-correction cases matched**, including every preset, custom, none, unknown/inherited names, invalid text, reference-field writes and zero/nonzero Δ. Rendering callbacks were stubbed. The own-entry lookup fixes the inherited-name exception. [index.html:5482](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5482), [index.html:5500](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5500)

   **18 derivation comparisons matched** baseline application plus charge correction, with rendering/background gates stubbed. Graphite selection, raw centre, `toFixed(3)`, `'284.50' → '284.5'`, Δ, ROI/background `toFixed(1)`, centres, anchors and centre locks agree. I found no omitted live-context field changed by the successful transition. [index.html:8037](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8037), [index.html:8082](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8082)

4. **The structural rewrites retain their named protections; the pins are sound for their covered cases.**

   In-memory mutations each failed the corresponding test: removing inclusive `+1`, changing the scattered-start trigger, dropping the required anchor, and moving capture below upload. See [bg_window_indices.test.js:127](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/js/bg_window_indices.test.js:127), [scattered_starts.test.js:247](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/js/scattered_starts.test.js:247), [autofit_required.test.js:57](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/js/autofit_required.test.js:57), [per_tab_state.test.js:108](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/js/per_tab_state.test.js:108).

   The six original fixture entries remain unchanged from `be2e58a`. Auto-Fit now has an independent anchor-body assertion, closing the previous shared-builder gap; its final model/context/body are checked against derivation. [test_browser_seal_requests.py:124](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/test_browser_seal_requests.py:124), [test_browser_seal_requests.py:135](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/test_browser_seal_requests.py:135), [test_browser_seal_requests.py:179](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/test_browser_seal_requests.py:179)

   Application tests omit signed-zero transitions. Their lock coverage is four grouped configurations, not every combination. [seal_step2.test.js:50](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/js/seal_step2.test.js:50)

5. **No new numerical tolerance; one inconsistent equality reading remains.**

   Request parsing retains the old conversions. `_sameModel` now correctly handles key order, absent versus `undefined`, and `Object.is` numbers. However, its signed-zero distinction conflicts with `_applyProjected`’s assignment comparison—the MAJOR finding above. [index.html:7085](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7085)

Read-only review completed; checkout unchanged. **135 focused JS tests passed.** Browser tests and full pytest were not rerun here.

**VERDICT: NO-GO.**
