Reviewed HEAD `94d7819`, read-only. **Two MAJOR findings remain.**

1. **MAJOR — Upload-rounded flat data still produces an accepted anchor.** [templates/index.html:6847](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:6847)

   Reproduced with extracted frontend model construction and the actual backend: ROI 280–295 eV, spacing 0.02 eV, baseline 10, Gaussian bump height **0.0001**, FWHM 0.4, centre 284.5. Detection succeeds, but upload rounds every intensity to **10.00**. Linear subtraction therefore leaves zero signal.

   With `least_squares`, `n_perturb: 3`, the backend returns success: Graphite amplitude **3.096e-5**, stderr **7.461e-6**, centre **284.204003**. This passes both thresholds: amplitude exceeds **5e-6** and **3 × stderr**. The extracted `applyAutoFitResult` writes `cc-obs = 284.204` and calls charge correction—approximately **0.296 eV from numerical residue**. Repeated runs also passed. Checking the data actually fitted must reject this flat-input case.

2. **MAJOR — Raw-span threshold rejects a resolved Graphite peak on a steep background.** [templates/index.html:6847](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:6847)

   Reproduced over 280–295 eV at 0.05 eV spacing: background `1000 + 2000 × (E − 280)`, plus an asymmetric GL Graphite peak of amplitude **1,000**, centre **284.5**, FWHM **0.7**, GL ratio **0.3**, asymmetry **0.25**.

   With linear background and the same Auto-Fit backend settings, detection selects **284.5** and fitting recovers amplitude **981.925**, centre **284.500674**. Yet the raw span is **29,998.965**, requiring amplitude **1,499.948**. The shipped application function rejects and rolls back this real anchor. Detection prerequisites do not prevent this: detection uses background-subtracted intensity, while the new gate includes the background slope.

The other requested checks pass:

- **ROI ownership:** `be2/inten2` are captured before upload and reused at application; the backend fits the entire uploaded ROI. `_ownerActive` precedes application. They represent the same region, although upload rounding changes the intensities, as finding 1 demonstrates.
- **Inactive rollback visibility:** restoring `t.ui.ccMethod` is sufficient. `activateTab` calls `_restoreUI`, which restores both fields’ visibility.
- **No additional BLOCKER or MINOR findings.** The acknowledged undo/redo issue remains unchanged.

All **15 committed Node tests pass**; neither reproduction is covered. Workspace unchanged; no browser run.

**VERDICT: NO-GO.**
