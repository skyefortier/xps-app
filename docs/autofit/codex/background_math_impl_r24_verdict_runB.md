# Background math implementation — Codex round 24, run B (commit 52e9ca5)

Reviewed `52e9ca5`, read-only. **Three MAJOR findings:**

1. **MAJOR — A sub-rounding charge change hides a genuine background change.** [templates/index.html:10029](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10029)

   Reproducer: keyless legacy Gaussian, center `285`, FWHM `1`, amplitude `100000`, eleven energies `284.55 + 0.005i`, originally fitted against constant manual background `100`. Apply charge correction `0.00004` and change the background to `94.3`.

   The backend successfully fits the rounded upload. Restoration then installs **94.3 with no background-stale flag**, accepting a **5.7% genuine change**. The offset interval includes zero, so `grid.moved` is false; component-reconstruction error cancels the background change. This demonstrates a reachable consequence of the stated four-decimal limitation.

2. **MAJOR — The search-step cutoff still drops uniquely identifiable fits.** [templates/index.html:10192](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10192)

   Reproducer: legacy keyless Gaussian on twenty energies `280 + 0.1i`, center `281`, FWHM `0.5`, amplitude `1000`, background `100`, stored six-significant-figure counts, legacy-upload RMSE `0.003600975331`.

   Append a second region twenty eV higher, with each energy repeated twice. Its counts are the corresponding original count plus `0.0001` and `0.0002`, except both final samples are increased by `1`.

   The final stored count excludes every second-region reading. Nevertheless, earlier unequal samples multiply the paths until the cutoff drops the fit as indistinguishable. **Removing only that cutoff restores the original fit without staleness.**

3. **MAJOR — Full-precision fits receive an obsolete RMSE allowance and reload peaks-only.** [templates/index.html:10140](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10140)

   Reproducer: keyed, `uploadFull: true` Gaussian on `280 + 0.1i`, `i=0…10`, center `280.5`, FWHM `0.5`, amplitude `1000`, manual background `10000`, ROI `[280,281]`. Add one raw point outside the ROI at `279.99999`, with the first fitted sample’s count plus `0.004`.

   A successful backend fit has RMSE approximately `5e-13`. The wrong assignment has RMSE approximately `0.001206`, but the unconditional old-upload allowance `0.005` admits it. Restoration refuses the unchanged fit as indistinguishable. **Removing that allowance for full-precision records restores it correctly.**

Verification: census **8 current / 73 stale / 40 peaks-only** reproduced exactly; Python twin verdicts agree. Committed measurement analysis and student-note measurements reproduce. All **202 upload inputs, seeds, and background arrays** match. The narrowed test checks actual scattered-start draws; CI floor is **559**.

**120 JS and 46 Python checks passed.** Two Python fixtures required forbidden temporary-file writes. Full optimizer/browser suites were not rerun. No files changed.

**VERDICT: NO-GO**
