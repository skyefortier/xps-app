Reviewed `b804968..947f4b4`, read-only. **The successful final-fit path is substantially correct, but the required transaction is not implemented.**

1. **MAJOR — The anchor fit is visible and saveable before the final fit succeeds.**  
   [index.html:8372](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/templates/index.html:8372) applies the anchor response to live peaks, then `applyAutoFitResult()` calls `updateChargeCorrection()`, which changes the live correction, bounds and manual anchors and redraws the page. The second upload then yields control. The spinner covers only the chart; save and keyboard actions remain available.

   I reproduced this using the actual extracted charge-shift and save functions: between fits, the page redraws at **+0.2 eV correction**, and Save Fit exports that correction, the anchor-derived peaks and moved manual anchors. Final-fit acceptance has not occurred. A later rollback cannot retract that file. A superseding fit also starts from these already-mutated values, although the older operation correctly avoids further writes after detecting supersession.

   Stage the transaction separately and commit only after final acceptance. **Non-physical inputs required: no.**

2. **MAJOR — Rollback leaves undo/redo changes; the undo entry does not cover the transaction.**  
   `pushUndo()` runs before fitting at [index.html:8286](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/templates/index.html:8286). It pushes only the peak snapshot and clears redo. [_autoFitRestore()](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/templates/index.html:7530) restores the listed model/context fields but neither history stack.

   The reproduction restored the previous peaks, correction, anchors and result after failure, yet retained **one extra undo entry and an emptied redo stack**. On success, Undo restores old peak centres without restoring the correction, ROI/background bounds or anchors, putting those peaks in another energy frame. This is inherited machinery, but it does not satisfy this unit’s explicit transaction contract. Create one complete undo entry at commit. **Non-physical inputs required: no.**

3. **MAJOR — The final upload can outlive the advertised two-minute timeout indefinitely.**  
   [index.html:8393](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/templates/index.html:8393) arms the timer, then awaits `uploadToBackend()`. That helper’s fetch receives **no abort signal**. If the upload or response body stalls, aborting `ctrl` does not release this await, so rollback and spinner cleanup do not run. No final job exists yet for the cancel beacon to cancel.

   Pass cancellation through the upload and response read. The original upload has the same latent defect; the new second upload repeats it while the anchor-derived correction is live. **Non-physical inputs required: no; an ordinary stalled connection suffices.**

4. **MAJOR — The simulated-job tests do not prove their rollback/publication claims.**  
   [autofit_refit.test.js:41](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/tests/js/autofit_refit.test.js:41) replaces snapshot/restore with `{}` and a boolean flag. It also replaces charge correction, backend application, gates, publication, undo, backgrounds and anchors; its timer never expires. Thus “restores everything” means only “called the restore stub,” and “only the final fit is published” cannot detect the real anchor redraw/save above.

   The [browser test](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/tests/test_browser_autofit_refit.py:16) is a useful, genuine check of exact energy-array equality for one successful case. It does not establish background/model equality or transaction isolation. Add actual-state assertions during a delayed second fit and after rejection, cancellation and supersession. **Non-physical inputs required: no.**

5. **MINOR — The “18 of 51 at approximately 15–17% → 2%” claim miscounts the measurements.**  
   Recounting the committed data gives **16** tabs at approximately **14.8–17.3% → 1.6–2.2%**. Two additional B4C tabs change **11.25% → 5.58%** and **12.48% → 6.07%**. Eighteen is the count above 10% initially, not the count fitting the stated range. Correct the [README](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/docs/findings/q8-autofit-refit/README.md:18), plan, code comment and CLAUDE claim. **Non-physical inputs required: no; committed measurements.**

6. **MINOR — The held student note presents paired-measurement bounds as rerun guarantees.**  
   The [note](/Users/skyefortier/xps-app/.claude/worktrees/af-refit/docs/superpowers/plans/2026-10-12-autofit-refit-student-note.md:11) says “at most about four” percentage points and “Centres do not change,” then recommends rerunning Auto-Fit. Those statements describe adding the final fit to the **same anchor result**. They do not describe independent Auto-Fit reruns: the confirmation includes an **11.516 pp** component difference, and B4C Scan_1’s Adventitious 1 centre differs by approximately **0.149 eV** between runs.

   Qualify the numbers as paired measurements and distinguish the final fit’s locked centres from rerun variability. “χ²ᵣ can move a little” also understates the measured approximately **−35% to +35%** range. **Non-physical inputs required: no; committed spectra.**

Other checks were favorable:

- By code comparison, the anchor request retains main’s numerical inputs and settings, preserving seed derivation by effect.
- The final request rereads the shifted/re-rounded window, background and manual anchors, retains bounds overlays and amplitude floor, and sends the method, three perturbations and captured anchor id.
- Both Δ branches reach the final fit; the final response repeats the supported/required/refit-converged/centre-window gates. Only the anchor response derives the shift.
- Auto-Fit builds asym-GL and GL components; it does not build LA or DS+G.
- The B4C table agrees with its JSON files at the displayed precision. The confirmation’s reported maxima and three acceptance mismatches reproduce from the committed data. Tiny changes on another refit support numerical stability, not proof of a global minimum.
- No Q5 implementation or unrelated production behavior change appeared in this diff.

**Validation:** all 84 selected JavaScript tests passed; additional in-memory probes demonstrated the premature save and rollback residue. I did not rerun the real-browser/server test under the read-only sandbox. No files changed.

**VERDICT: NO-GO.**
