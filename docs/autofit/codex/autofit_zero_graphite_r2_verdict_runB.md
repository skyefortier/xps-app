Rechecked `94d7819` read-only. All **15 Node tests pass**, but two MAJOR failures reproduce using extracted frontend functions and the actual backend (`least_squares`, `n_perturb: 3`). No BLOCKER found.

1. **MAJOR — Constant uploaded data can still produce an accepted anchor.** [templates/index.html:6847](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:6847)

   Reproduction: 280–295 eV, 0.01 eV spacing; baseline 10 plus a Gaussian of height **0.00004**, FWHM 0.4, centred at 284.5. Detection succeeds, but upload rounding makes every intensity **10.00**.

   The backend returns success with Graphite amplitude **3.09614e-5**, stderr **5.24039e-6**, centre **284.204003**. This passes both thresholds: amplitude exceeds **2e-6** (5% of the original span) and **1.57212e-5** (3σ). It permits approximately **+0.296 eV of axis correction from numerical residue**.

   Reproduced with ordinary unseeded perturbations; fixed perturbation seeds 1–4 also reproduce it. Missing stderr is therefore unnecessary for this escape.

2. **MAJOR — Raw background slope rejects a well-resolved, real anchor.** [templates/index.html:6847](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:6847)

   Synthetic spectrum: 278–296 eV at 0.05 eV spacing; background `100000 + 15000 × (BE − 278)` plus a 10,000-count asymmetric-GL Graphite peak at 284.5, FWHM 0.7, GL ratio 0.3, asymmetry 0.25.

   With automatic linear background subtraction and Poisson noise averaged over 100 scans, detection selects **284.5**. The backend returns amplitude **9,686 ± 517**, centre **284.5016 ± 0.0031 eV**. Nevertheless, the raw span is **269,919**, requiring amplitude ≥ **13,496**, so the operation rolls back. This fails solely on the span rule; the anchor comfortably passes 3σ.

   Background-subtracted peak detection does not impose the raw-span relationship assumed by the new guard.

3. **MINOR — Known undo/redo loss remains.** [templates/index.html:7003](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:7003)

   Undo an edit, then run an Auto-Fit that rejects: `pushUndo()` clears Redo, and rollback does not restore it. Accepted as the documented, pre-existing limitation.

The other requested checks pass:

- **ROI ownership:** the captured `be2`/`inten2` supply both upload and support validation; the backend fits the whole uploaded ROI. `_ownerActive` precedes result application. The region matches, although upload rounding changes its numerical values.
- **Inactive-owner visibility:** no additional fix is needed. Record rollback restores `ui.ccMethod`; `activateTab` calls `_restoreUI`, which restores both fields’ visibility. The active-owner fix also passes.

**VERDICT: NO-GO.**
