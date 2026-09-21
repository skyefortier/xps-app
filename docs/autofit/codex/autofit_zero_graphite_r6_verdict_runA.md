Reviewed HEAD `9e41388`, read-only. **Three in-scope MAJOR findings.**

Reproductions used shipped detection, `buildAutoFitModel`, `uploadToBackend` serialization/parser, `/api/fit` with `least_squares`, `n_perturb: 3`, and extracted result handlers. Session storage was supplied in memory; no browser run or files changed.

1. **MAJOR — Holding other components fixed accepts an unnecessary overlapping anchor.** [templates/index.html:6865](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:6865)

   Scan **295→280 eV, spacing 0.02**; manual background **1000**. Add two symmetric GL components, mixing **0.3**, with amplitude/center/FWHM:
   **1000/284.8/3.0** and **400/283.5/1.5**.

   Detection selects **284.2** and builds seven components. With seed 1, the successful fit returns Graphite amplitude **33.9365**, center **284.230752**, and **F ≈ 5.61 million**. The handler accepts and writes **`cc-obs = 283.931`**.

   Yet removing Graphite and **refitting the remaining components from their returned values**, through `/api/fit`, succeeds and reduces χ² from **0.000642084 to 0.0000116848**—about **55× better**.

   This directly answers the overlap question: fixed-component deletion measures contribution to the current decomposition, not whether the data require that component. Seeds 0, 1, and 2 all accept, producing raw reference positions spanning approximately **0.366 eV**.

2. **MAJOR — One zero-count channel away from a resolved anchor causes rejection.** [templates/index.html:6875](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:6875)

   Same grid; manual background **1000**. Add asymmetric GL with amplitude **1000**, center **284.5**, FWHM **0.7**, mixing **0.3**, asymmetry **0.25**. Set only the sample at **281 eV** to zero.

   Seed 0 returns amplitude **906.387**, center **284.506000**, width **0.705879**. Removing Graphite worsens χ² by **13,067.43**, but the distant dropout dominates the denominator: **F = 1.9078**, so the handler rejects before charge correction.

   Seeds 1 and 2 also reject. The identical spectrum without the dropout passes. The global residual normalization therefore turns a separate bad channel into “Graphite unsupported,” despite the resolved line remaining.

3. **MAJOR — Upload/background rounding residue can still derive charge correction.** [templates/index.html:6890](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:6890)

   Scan **286→283 eV, spacing 0.005**. Background and manual endpoint anchors **10.006**; add asymmetric GL with amplitude **0.0001**, center **284.5**, FWHM **0.4**, mixing **0.3**, asymmetry **0.25**.

   Detection selects **284.5**, but upload makes **all 601 counts exactly 10.01**. The entire line disappears; the unrounded manual background leaves a constant **0.004 rounding residue**.

   Seeds 0–2 nevertheless return Graphite amplitude approximately **0.001775**, center **284.200**, and **F ≈ 278**. The handler calls charge correction with **`cc-obs = 284.200`**, deriving a **0.300 eV correction from upload residue**. This is the previously in-scope upload/background precision mismatch.

No BLOCKER or additional MINOR finding.

All **20 targeted tests and 57 related tests pass**. Descending grids and negative-count controls worked; the parser removes NaN rows, response curves share the server grid, and a synthetic **300,000-point** gate check completed successfully.

**OUT-OF-SCOPE**

- Single-channel spikes used as anchors and plateaus under background None: feature authenticity.
- Previously documented undo/redo changes on rejection.

**VERDICT: NO-GO.**
