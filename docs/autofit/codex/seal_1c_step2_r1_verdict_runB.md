**Two MAJOR projection findings prevent GO.** No request-body difference was found in the producer comparisons.

1. **Behaviour is not exactly unchanged: omitted reply components are now applied from the start snapshot. — MAJOR**

   `_applyProjected` copies fields from **every** projected peak, including peaks absent from `individual_peaks`. The old application loop visited only components named by the reply. Reproduction: live peak 2 has `center=286`, the adopted alternative has `center=287`, and the reply names only peak 1. Old application leaves peak 2 at **286**; new application writes **287**. Missing parameters on a named component have the analogous problem. Preserve the old write set when applying the projection. [index.html:7092](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7092)

   Otherwise, the builder matched baseline bodies across **1,280 model/context combinations per producer**, covering all shapes, linked/unlinked models, locks, backgrounds and five methods. Inputs remain captured before each upload await; Auto-Fit’s existing confirmation await still precedes capture. Presentation fields remain live. [index.html:9201](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9201), [index.html:8370](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8370)

2. **The projection is not isolated from mutable inputs or live peaks. — MAJOR**

   `project` deep-clones `pageModel`, then installs `ip.params` **by reference**. `_applyProjected` transfers that same object into the live peak. Consequently:

   ```js
   projected[0]._backendParams === O.individual_peaks[0].params
   live[0]._backendParams === projected[0]._backendParams
   ```

   Both are true. Mutating live `_backendParams.center.value` changes the projection and reply. The call itself does not mutate its inputs, but it violates the plan’s explicit “no mutable object shared with the seal” requirement. Clone the parameter evidence and isolate the live installation. [index.html:7077](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7077), [index.html:7096](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7096), [plan:96](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:96)

   The purity test checks only changes to scalar fields against the model snapshot; it never checks reply aliases or live/projection aliases. [seal_step2.test.js:99](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/js/seal_step2.test.js:99)

3. **Charge correction matches for selectable methods; unknown-method handling has an exception.**

   The actual old/new functions matched **432 combinations** with mocked DOM/repaint dependencies, including preset/custom/none, invalid text, reference-field writes and zero/nonzero Δ. The `parseFloat` and `toFixed(1)` arithmetic is preserved. [index.html:5509](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5509)

   **MAJOR under the requested unknown-method contract:** `_ccShiftOf('constructor', …)`, `'toString'` and `'__proto__'` throw when destructuring an inherited table property; the old unknown-method branch returned shift zero. These names are not selectable in today’s dropdown, so this is a helper-contract regression, not an ordinary UI path. Use an own-property lookup. [index.html:5484](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5484)

   For accepted Auto-Fit paths, I found **no omitted context field**. Graphite/fallback selection, raw centre, `toFixed(3)`, `'284.50' → '284.5'`, Δ, field/centre/anchor movement and centre locks match. Thirty-six extracted-function comparisons matched, including zero Δ and anchors. The derivation inherits the parameter alias from finding 2. [index.html:8026](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8026), [index.html:8065](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8065)

4. **The structural-test rewrites retain their original protections; the new pins have coverage limits.**

   In-memory mutations confirmed failures for removing inclusive `+1`, changing the scattered-start trigger, removing `require_component`, and moving request capture below upload.

   The six Run Fit fixtures are independently pinned: commit `be2e58a` changed only tests/fixtures, before page changes.

   **MINOR — Auto-Fit’s pin proves consistency, not independent request identity.** Both actual and expected bodies use `_buildFitRequest`; changing Auto-Fit-only `n_perturb: 3` to `4` changes both sides together. That mutation also passes `autofit_refit.test.js`. Add a baseline oracle for Auto-Fit-specific request fields. [test_browser_seal_requests.py:158](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/test_browser_seal_requests.py:158)

   The projection cases always return every component, and use four grouped lock configurations—not every lock combination—so they miss finding 1. [seal_step2.test.js:50](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/js/seal_step2.test.js:50)

5. **No new numerical tolerance or conflicting numeric parser was introduced.**

   **MINOR — `_sameModel` is JSON serialization equality, not field equality.** Identical fields inserted in different orders compare unequal; absent versus `undefined` compares equal. This is currently a helper/test limitation, but should be resolved before it governs seal bindings. [index.html:7085](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7085)

Read-only review completed; **131 targeted JS tests passed**. I did not rerun the browser/full pytest suite.

**VERDICT: NO-GO.**
