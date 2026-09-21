Reviewed HEAD `9e41388`, read-only. **Two in-scope MAJOR findings.**

Reproductions used shipped detection, `buildAutoFitModel`, `uploadToBackend` serialization/parser, `/api/fit` with `least_squares`, `n_perturb: 3`, and extracted result-application functions. Session storage was supplied in memory; no browser run or files changed.

1. **MAJOR — Holding other components fixed accepts a redundant overlap component.** [templates/index.html:6865](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:6865)

   Input: **295→280 eV**, spacing **0.02**, constant/manual background **1000**, plus two symmetric GL lines, mixing **0.3**:
   
   - amplitude **10,000**, center **284.8**, FWHM **1.4**;
   - amplitude **15,000**, center **283.3**, FWHM **1.8**.

   Detection selects **284.46**. Across three perturbation seeds, the successful full fit returns Graphite amplitudes **1081–1894**, with **F ≈ 1.1–3.8 million**. The shipped handler accepts and calls charge correction, writing `cc-obs` **284.577–284.634**.

   Yet deleting Graphite and refitting the remaining components—with their existing bounds—produces successful fits with **χ² ≈ 3.8×10⁻⁶**, versus **0.24–0.56** for the full model. Maximum residual without Graphite is approximately **0.0056 counts**.

   The data are explained by the remaining components to upload-rounding precision. Fixed-component deletion measures the cost of disturbing the fitted decomposition; it does **not** establish that the data require the anchor. This is component redundancy, independent of chemical identification.

2. **MAJOR — Global residual scaling rejects a resolved anchor beneath an outlier.** [templates/index.html:6875](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:6875)

   Same grid and background. Generate Graphite asymmetric GL with amplitude **10,000**, center **284.5**, FWHM **0.7**, mixing **0.3**, asymmetry **0.25**. Add symmetric GL components of amplitude **2000**, mixing **0.3**, at center/FWHM **285.3/0.8, 286.2/0.8, 287.8/0.8, 291/1.0**. Add **3,000,000 counts** to the channel at **284.5**.

   Detection selects **284.5**. Across three seeds, fits succeed and recover Graphite amplitude approximately **8582–8584**, center **284.47528**, but **F ≈ 8.97** rejects the result. Removing Graphite increases χ² by approximately **183,500–183,700**.

   With a **300,000-count** spike, the recovered anchor is nearly unchanged and **F ≈ 93.7** passes. Increasing the outlier inflates the global denominator until the resolved underlying line fails. This concerns rejection of a resolved line beneath a spike; spike-only anchoring remains outside scope.

No BLOCKER or separate MINOR finding. All **61 targeted Node tests pass**. Tested rounded-away residues reject; nonpositive-count weights and ascending/descending grids behave consistently. Backend curves share the counts grid. Million-sample support-check controls pass; full optimization at that size was not tested.

**OUT-OF-SCOPE**

- Feature authenticity of a spike-only anchor.
- Nonzero plateau anchors under background None.
- Previously documented undo/redo loss on rejection.

**VERDICT: NO-GO.**
