**NO-GO: two MAJOR projection findings prevent the claimed exact equivalence and isolation.** No request-body difference was found.

1. **Requests and timing match; result application is not universally unchanged.**

   I compared 3,840 bodies against extracted baseline code across all eight lineshapes, links, locks, backgrounds and fitting methods, for all three producers. They matched, including field presence. Run Fit builds before upload at [index.html:9204](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9204); Auto-Fit captures each request before its respective upload at [index.html:8492](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8492) and [index.html:8556](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8556). Auto-Fit’s earlier confirmation await is unchanged.

   **MAJOR — `_applyProjected` writes peaks the reply never names.** It iterates the entire projected model, rather than the reply’s components: [index.html:7093](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7093).

   Reproduced against the actual baseline application:
   - Live peak 2: centre **286**.
   - Adopted alternative’s peak 2: centre **287**.
   - Reply names only peak 1.
   - Baseline preserves peak 2 at **286**; HEAD writes **287**.

   The current server normally returns every component; this is the explicitly requested omitted-component case. Missing individual parameters produce the analogous problem. Even an omitted peak’s existing `_backendParams` gets replaced by its cloned snapshot object, whereas the old loop leaves it alone.

   Presentation fields remain live: the transfer list excludes name, colour and visibility. Normal complete replies retain the existing lock, expression and shape conversions through `_applyBackendParams`.

2. **Projection does not mutate its inputs during execution, but it is not detached.**

   **MAJOR — mutable evidence is shared between reply, projection and live peaks.** [index.html:7077](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7077) assigns `ip.params` directly, and [index.html:7096](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7096) transfers that reference directly.

   Reproduced:
   ```js
   projected[0]._backendParams === reply.individual_peaks[0].params // true
   live[0]._backendParams === projected[0]._backendParams          // true
   ```
   Changing the projection’s nested parameter value changes both the reply and live evidence. Ordinary request snapshots are separately cloned, but the required isolation between projection and live peaks fails. The old live/reply alias already existed; the newly introduced projection inherits it.

   Auto-Fit correctly uses separate snapshots for its two applications, but both pass through this same aliasing path.

3. **Charge correction and successful Auto-Fit derivation otherwise match.**

   The six presets, custom, none and ordinary unknown strings retain the old arithmetic and reference-field writes. `delta !== 0` still controls movement, and `parseFloat` plus `toFixed(1)` is unchanged: [index.html:5482](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5482), [index.html:5520](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5520).

   `deriveAutoFit` matches graphite selection, raw-centre reconstruction, `toFixed(3)`, `'284.50' → '284.5'`, shift subtraction, ROI/background/centre/anchor movement, and centre locks: [index.html:8065](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8065). I found no omitted context field changed by the successful anchor-to-final transition. An additional 81 differential cases matched baseline application and arithmetic, with rendering and background gates stubbed.

   **MAJOR under the requested “every unknown method” contract:** `_ccShiftOf('toString', '285', '284.5')` throws `TypeError`; the old explicit branches fall through to shift zero. The table lookup accepts inherited properties at [index.html:5484](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5484). The normal select cannot supply that value, so this is a helper-domain defect, not an ordinary UI path.

4. **The structural migrations preserve their named checks; the new pins have gaps.**

   I found no weakened check for capture-before-upload, inclusive background endpoints, scattered-start selection or required-anchor forwarding. The 131 focused JavaScript tests passed.

   The six Run Fit fixtures independently pin baseline bodies, including absent fields: [test_browser_seal_requests.py:124](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/test_browser_seal_requests.py:124).

   **MINOR — Auto-Fit’s pin proves derivation consistency, not baseline request identity.** Both sides use today’s builder at [test_browser_seal_requests.py:160](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/test_browser_seal_requests.py:160). Changing Auto-Fit’s `n_perturb` from 3 to 4 would change both compared bodies without inherently failing this assertion.

   The projection tests miss the MAJOR cases: replies always name every model peak, and the purity test mutates only scalar fields—not nested `_backendParams`: [seal_step2.test.js:63](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/js/seal_step2.test.js:63), [seal_step2.test.js:99](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/tests/js/seal_step2.test.js:99).

5. **No new numerical tolerance; one equality-reader concern.**

   Request parsing preserves the old conversions. The repeated DOM reads in charge correction are synchronous and use the same parser; I found no differing interpretation there.

   **MINOR — `_sameModel` is JSON-text equality, not field equality:** [index.html:7087](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7087). Reordered properties compare unequal; `NaN` and `null` compare equal. This needs an explicit domain/equality contract before it becomes a seal authority.

Read-only review completed; checkout unchanged. Browser tests and full pytest were not rerun here.

**VERDICT: NO-GO.**
