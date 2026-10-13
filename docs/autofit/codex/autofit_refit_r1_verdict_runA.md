Reviewed `b804968..947f4b4` read-only. The final-fit request construction looks sound, but the required transaction is not implemented.

1. **MAJOR — The anchor fit publishes live state before the final fit.**  
   [applyAutoFitResult](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/templates/index.html:7877) calls `updateChargeCorrection()`, which changes the charge correction, peaks, ROI/background bounds and manual anchors, and renders them. The second upload then yields. Save, tab synchronization and Ctrl/Cmd+F can consume this intermediate state.

   A probe using the real shift and save functions saved a **0.15 eV correction**, shifted ROI and moved anchors before any final fit existed. A superseding Run Fit inherits that state; the old Auto-Fit’s subsequent “write nothing” return cannot undo the earlier publication. A newer Auto-Fit likewise snapshots the intermediate state. Stage both fits privately and commit only after final acceptance. **Non-physical inputs: no.**

2. **MAJOR — Undo and rollback are not transactional.**  
   [The early `pushUndo()`](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/templates/index.html:8291) records peaks only and clears redo. `_autoFitRestore()` restores neither stack. Using the real functions, a failed operation left **one undo entry and zero redo entries**. After success, undo restored the old peaks while retaining the new charge correction, ROI and final result.

   This is inherited behavior, but retaining it does not satisfy step 0d’s transaction contract. Commit one complete undo record on success; failure must preserve history. **Non-physical inputs: no.**

3. **MAJOR — The final upload is outside the effective two-minute timeout.**  
   [The second upload](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/templates/index.html:8393) receives no abort signal; [uploadToBackend](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/templates/index.html:6957) performs an unsignalled fetch. If it stalls, the timer aborts the controller but execution remains awaiting upload. Rollback and ownership checks do not run until that promise settles, leaving the intermediate state exposed. The upload must participate in timeout/cancellation. **Non-physical inputs: no; an ordinary network stall suffices.**

4. **MAJOR — The simulated-job tests do not prove their rollback/publication claims.**  
   [The harness](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/tests/js/autofit_refit.test.js:41) replaces snapshot/restore, undo, charge shifting, gates and publication with stubs. “Restores everything” checks only a boolean; “only final published” cannot detect rendering or saving through `updateChargeCorrection()`. Timers never expire, ownership is always active, and ROI selection never changes point count.

   The [browser test](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/tests/test_browser_autofit_refit.py:29) makes a genuine exact-array assertion for one successful spectrum, but checks neither rendered chart data nor background/model identity, rollback or interleavings. Add tests using the real transaction functions and observable saved/rendered state. **Non-physical inputs: no.**

5. **MINOR — The “18 / 51” R-factor headline is incorrect.**  
   [README line 18](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/docs/findings/q8-autofit-refit/README.md:18) claims 18 tabs at 14.8–17.3% → 1.6–2.2%. The committed JSON contains **16**. There are **18 above 10%**, including the two B4C cases at 11.25% and 12.48%, falling to 5.58% and 6.07%. Correct the repeated headline in the plan, comments and CLAUDE.md. **Non-physical inputs: no.**

Other checks:

- The anchor request preserves main’s inputs and seed by effect. The final request freshly reads shifted points, bounds and manual anchors, retains overlays/amplitude floor/method/three restarts, and uses the captured anchor ID.
- Both responses use the same gates; only the anchor response derives the shift. Both Δ branches reach the final fit. Auto-Fit builds GL/asym-GL models, not LA/DS+G.
- The B4C table agrees with its JSON. Confirmation supports 49 close comparisons, one 11.516 pp outlier and three acceptance mismatches—not unconditional equivalence.
- The student note’s typical/max area changes and median extra second match the measurements. “χ²ᵣ can move a little” understates the measured −35% to +35% range.
- Q5 remains measurement-only; I found no unrelated production change.

All **84 targeted JavaScript tests passed**. I ran additional in-memory probes and recalculated measurement totals; I did not run the real-browser test in this restricted read-only environment. No files changed.

**VERDICT: NO-GO.**
