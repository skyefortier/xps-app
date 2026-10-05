# Background math implementation — Codex round 23, run B (commit f186951)

Reviewed `f186951`, read-only. **Three MAJOR findings:**

1. **MAJOR — The remaining search-step cutoff drops uniquely identifiable fits.** [templates/index.html:10189](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10189)

   Reproducer: a keyless legacy Gaussian fit on ten energies `280 + 0.1i`, center `280.5`, FWHM `0.5`, amplitude `1000`, background None. Add another region at `300 + 0.1i`, with counts `original[i] + 0.004`, duplicating each sample twice. Preserve the fit’s six-significant-figure counts and legacy-upload RMSE `0.003468170584`.

   The stored counts uniquely identify the original region. Nevertheless, duplicate assignments exceed `64 × (n + 1)` search steps, and restoration drops the fit as indistinguishable. Without the duplicates, it restores successfully. Collecting completed readings by value does not fix this earlier cutoff.

2. **MAJOR — Removing the energy allowance still permits genuine background changes to escape staleness.** [templates/index.html:10013](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10013)

   Reproducer: legacy keyless Gaussian on `280.00004 + 0.1i`, `i=0…10`, center `280.5`, FWHM `0.2`, amplitude `1000`, originally fitted against background `100`. Apply charge correction `0.033337`.

   Let `Mold` be its original four-decimal component curve and `Mestimated` the reconstruction in today’s rounded frame. Set manual anchors at the corrected samples to `100 + Mold − Mestimated`. This changes the background by up to **0.256483 counts**, exceeding the required approximately **0.100256-count** tolerance.

   Production restoration accepts it with **no `backgroundStale` flag**. The reconstruction error cancels the genuine change. Withdrawing an allowance does not make uncertain reconstruction conservative; §7.9’s “never wrongly current” claim remains false.

3. **MAJOR — Save Spectrum still mixes component grids for legacy fits that restore as current.** [templates/index.html:11509](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:11509)

   `_modelBe` is used only when `_restoredStale` is true.

   Reproducer: unchanged keyed legacy Gaussian on `280.00004 + 0.1i`, center `280.5`, FWHM `0.2`, amplitude `1000`, constant manual background `10`. It correctly restores without staleness. The production saver then writes, at `280.40004`:

   - Background: `10`
   - Component: `500.2772802763`
   - Preserved envelope: approximately `510`
   - Residual: approximately `−0.2772802765`, although counts minus the preserved envelope is zero

   The saved curves and residuals describe different evaluations. Round 22 fixed the restored-stale branch but leaves this current-fit path incorrect.

Verification: census **10/71/40** and serialized Python twin reproduce exactly; `final_analysis.json` and student-note numbers reproduce. All **202 upload inputs, seeds, and background arrays** match the measurement records. The narrowed scattered-starts test passes and compares actual draws. CI floor is **557**.

**133 JS and 82 Python checks passed.** Three JS checks and two Python fixtures encountered read-only temporary-file restrictions. Full/browser suites were not verified. No files changed.

**VERDICT: NO-GO.**
