# Background math implementation — Codex round 21, run B (commit dcca5a4)

Reviewed `dcca5a4`, read-only. **Three MAJOR findings:**

1. **MAJOR — A charge-shifted fit is lost on its second save/reload.** [templates/index.html:10012](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10012)  
   Fit samples `1…4` from raw energies `0…5`, with a Gaussian `(center=2.5, FWHM=2, amplitude=100)` and background None. Keep its model key, apply charge correction `+0.5`, then save/load. Restoration succeeds but changes `fr.be` to `[0.5,1.5,2.5,3.5]` while retaining the key’s shift `0`. Save/load again: the matcher applies the old offset to these already-transformed energies and drops the checkable fit as “not points of its raw data.”

2. **MAJOR — Six-significant-figure bounds admit readings the record actually separates.** [templates/index.html:10086](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10086)  
   A keyless project contains a Gaussian fit on `280…284`: stored counts `[62.5,500,1000,500,62.5]`, zero background and RMSE zero. Another run at `290…294` has identical counts except its center is `999.996`. Its RMSE discrepancy is `0.001789`, within the allowance. `half6(1000)` then admits its count discrepancy of `0.004`, so restoration refuses both readings as indistinguishable.

   But `999.996` remains `999.996` at six significant figures. The lower rounding boundary for stored `1000` is approximately `999.9995`, not `999.995`. The stored counts distinguish the correct run; the symmetric bound incorrectly drops it.

3. **MAJOR — Legacy Voigt spectrum saves still mix different models’ curves.** [templates/index.html:11466](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:11466)  
   Restore an unedited pre-A03 Voigt `(center=282, FWHM=2, amplitude=100, recorded η=0.3)` on `280…284`, with background None. `_restoredModelIsFit` passes and Save Spectrum preserves its historical envelope, but evaluates `peakCurves` at η=0.5. The production saver writes **envelope 10.375, background 0, component 13.125** at energy `280`; the saved component area also disagrees with the preserved fit.

Verification: census **10 current / 71 stale / 40 peaks-only**, Python twin verdicts, committed measurement analysis and student-note numbers reproduce. No committed fit is refused as indistinguishable. All **202 upload inputs, seeds and background curves** match the measurement records. The narrowed test still compares actual scattered-start draws; CI floor is **548**.

**94 Python and 19 targeted JS checks passed.** Broader verification encountered read-only temporary-file restrictions and time limits; browser suites were not rerun. No files changed.

**VERDICT: NO-GO.**
