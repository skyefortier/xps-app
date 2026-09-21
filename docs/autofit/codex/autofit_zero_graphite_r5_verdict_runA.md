Reviewed HEAD `2f8420b`, read-only. **Two in-scope MAJOR findings remain.**

Both reproductions use 295→280 eV at 0.02 eV spacing, shipped detection and `buildAutoFitModel`, actual `uploadToBackend` formatting/parser, and `/api/fit` with `least_squares`, `n_perturb: 3`. Both reproduce with perturbation seeds 0, 1, and 2.

1. **MAJOR — Numerical residue on an exactly zero fitted signal is accepted.** [templates/index.html:6848](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:6848)

   Input: constant background **10,000,000**, plus a Gaussian of amplitude **0.0001**, center **284.5**, FWHM **0.4**. Manual background anchors both equal **10,000,000**.

   Detection selects 284.5, but upload removes the entire bump. Every server count equals its background; the zero-component model has **exactly zero residual**.

   Nevertheless, the successful fit returns Graphite amplitude **0.02958561 ± 0.00916660**, center **284.256015**. This passes both thresholds. The extracted result handler writes `cc-obs = 284.256` and calls charge correction, deriving approximately **+0.244 eV from numerical residue**.

   This is case **(a)**, not a feature-authenticity objection: the server’s background-subtracted signal is identically zero.

2. **MAJOR — The 0.01 floor rejects a resolved line that survives upload rounding.** [templates/index.html:6848](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:6848)

   Input: zero manual background; one asymmetric GL line with amplitude **0.0058**, center **284.5**, FWHM **0.7**, asymmetry **0.25**, mixing **0.3**.

   Upload preserves **17 consecutive samples at 0.01**; the remaining samples are zero. For seed 0, the server returns amplitude **0.00933007 ± 0.00023253**—approximately **40σ**—and center **284.511906 ± 0.011746 eV**.

   The handler rejects solely because amplitude is below 0.01. All three seeds reject, despite amplitudes exceeding **35σ**.

   This answers **(b)** and **(c)**: small-unit data can retain a resolved, nonzero line after two-decimal upload while the gate rejects it. Sample quantization does **not** establish a minimum resolvable fitted amplitude.

No BLOCKER or additional in-scope MINOR found.

All **21 targeted Node tests** and **41 related acceptance/state tests** pass. Endpoint controls confirm the round-4 50-count/million-background line passes, an amplitude-0.8 spectrum passes, and the earlier rounded-away residue rejects. Sessions were supplied in memory; no browser run or files changed.

**OUT-OF-SCOPE observations**

- Previously documented nonzero anchors on featureless data with background None and single-channel spikes remain feature-authenticity issues.
- Documented undo/redo loss on rejection remains outside this unit.

**VERDICT: NO-GO.**
