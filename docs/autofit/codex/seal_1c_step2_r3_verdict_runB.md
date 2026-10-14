**One MAJOR finding remains: “Use this solution” can overwrite a locked value that the baseline preserves.** The previous findings are fixed in their tested cases.

1. **Request bodies and capture timing match; live application is not exactly unchanged.**

   **3,840 differential request comparisons** against `34ce8ba` passed across eight shapes, eight backgrounds, five methods, locks, links and all three producers. Capture remains before each upload await: [index.html:9222](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9222), [index.html:8509](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8509), [index.html:8574](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8574). Auto-Fit’s earlier confirmation await is unchanged.

   **MAJOR — installation copies held snapshot values into live peaks.** `_applyProjected` checks parameter presence, but does not distinguish fields actually written by `_applyBackendParams` from fields retained under a lock: [index.html:7112](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7112).

   Reproduced using the actual `_altPeaks` and baseline/current application functions, with two unlinked components:

   ```text
   Live DS peak: dsGamma = -0, fixDsGamma = true
   Adopted start: dsGamma = +0
   Reply: gamma_asym = { value: 0, expr: null }

   Baseline application: dsGamma remains -0
   HEAD application:     dsGamma becomes +0
   ```

   The adopted start differs because `_altPeaks` uses a JSON clone: [index.html:9121](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9121). The old application honours the lock: [index.html:7221](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7221). This is an exact-value defect, not a demonstrated visible spectral change. Preserve the old lock/shape write rules during installation.

2. **`project` is pure and detached; installation has the exception above.**

   Snapshot and reply parameters are deeply cloned, and live `_backendParams` receives another copy: [index.html:7070](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7070), [index.html:7114](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7114). No shared mutable parameter object remains. Presentation fields and omitted components/parameters retain the round-1 protections. Auto-Fit uses separate snapshots for its two applications.

3. **Charge correction and successful Auto-Fit derivation matched.**

   **384 baseline comparisons** passed for presets, custom, none, unknown/inherited names, reference text, display branches and movement arithmetic. Own-entry lookup, `delta !== 0`, `parseFloat` and `toFixed(1)` behave as intended: [index.html:5482](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5482), [index.html:5520](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5520).

   **48 successful-transition comparisons** passed for graphite/fallback selection, raw centre, `toFixed(3)`, `'284.50' → '284.5'`, zero/nonzero Δ, ROI/background/centre/anchor movement and centre locks: [index.html:8083](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8083). No omitted changed context field was found. Rendering and background gates were stubbed in these comparisons.

4. **Structural protections remain; the pins miss the new counterexample.**

   In-memory mutations were rejected for inclusive endpoints, scattered-start triggering, required-anchor forwarding and capture after upload. Reverting `Object.is` also fails the new regression.

   The six original fixtures are unchanged. Run Fit and Auto-Fit anchor requests have independent baseline pins; the final Auto-Fit pin checks model, context, energies and body: [browser tests:124](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/test_browser_seal_requests.py:124), [browser tests:158](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/test_browser_seal_requests.py:158), [browser tests:179](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/test_browser_seal_requests.py:179).

   However, the adopted-start test uses `structuredClone`, bypassing `_altPeaks`’ actual JSON conversion, and the signed-zero regression exercises an unlocked field: [seal_step2.test.js:86](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/js/seal_step2.test.js:86), [seal_step2.test.js:200](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/js/seal_step2.test.js:200).

5. **No tolerance or conflicting numeric parser was introduced.**

   `_sameModel` correctly distinguishes signed zero, absent versus undefined, and NaN versus null while ignoring key order: [index.html:7085](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7085). The remaining inconsistency is installation’s broader write rule versus `_applyBackendParams`’ lock/shape rules.

Read-only; checkout unchanged. **136 focused JS tests passed.** Browser tests and full pytest were not rerun.

**VERDICT: NO-GO.**
