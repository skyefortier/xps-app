# Background math implementation — Codex round 22, run A (commit 423f2d1)

Reviewed `423f2d1`, read-only. **Four MAJOR findings and one MINOR:**

1. **MAJOR — The 64-reading cutoff drops a fit whose stored counts uniquely identify it.** [templates/index.html:10160](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10160)

   The cutoff runs before `countsAgree` and before collapsing equivalent readings.

   Reproducer: 65 consecutive five-point runs, with a keyless Gaussian fit on the first: counts `[62.5,500,1000,500,62.5]`, zero background and RMSE zero. Every other run differs only at its center, `999.999`. Their RMSE discrepancy is `0.000447`, within `0.005`, but the stored six-significant-figure center `1000` excludes them: its lower boundary is `999.9995`.

   **64 runs restore successfully; 65 runs drop the same fit as indistinguishable.** Resource limits are not proof that the record cannot separate the readings.

2. **MAJOR — The energy allowance hides genuine background changes at realistic scales.** [templates/index.html:10012](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10012)

   Reproducer: legacy keyless Gaussian, center `282`, FWHM `1`, amplitude `10000`, sampled over `280–284` every `0.05 eV`, fitted against background `100`. Apply charge correction `0.01`. In the corrected frame, change the manual background to a triangular bump: `100` at `281.19`, `101` at `281.59`, and `100` at `281.99`, flat outside.

   Restoration accepts this **0.9901% genuine background difference**, installs the changed background and sets no background-stale flag. The allowance reaches `1.4234` counts—**1.4234% of the original background**, versus the required `0.1%` tolerance.

   The independent absolute allowances do not require one consistent energy displacement. Approximately, a Gaussian’s maximum allowance scales as `1.428 × 10⁻⁴ × amplitude/FWHM`; it has no bound relative to background height.

3. **MAJOR — Charge-shifted restored-stale fits still disappear after Save Spectrum.** [templates/index.html:9960](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9960)

   `_restoredModelIsFit` compares centers in different charge frames.

   Reproducer: raw energies `0…5`, fitted samples `1…4`, Gaussian `(center=2.5, FWHM=1, amplitude=100)`, background `10`. Preserve its key, shift by `0.5`, and change background anchors to `20`. Restoration correctly retains the fit as 50% stale.

   Without further editing, the production spectrum saver writes envelope `[20.1953125,70,70,20.1953125]` instead of `[10.1953125,60,60,10.1953125]`, with `restoredStale: null`. The loader consequently drops the fit.

4. **MAJOR — Legacy spectrum saves still combine curves evaluated on different energy grids.** [templates/index.html:11520](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:11520)

   Restoration reconstructs legacy components at four-decimal upload energies, but the saver evaluates component curves at unrounded `be`.

   Reproducer: unchanged legacy Gaussian `(center=280.5, FWHM=0.2, amplitude=1000)`, raw energies `280.00004 + 0.1i`, background `10`. It correctly restores without background staleness. At saved energy `280.40004`, however, the production saver writes background `10`, component `500.2772802763`, and envelope `510`. **The saved curves disagree by 0.2772802765 counts.** This also affects restored-stale saves.

5. **MINOR — The student-note generator no longer runs.** [scripts/bg_math_preview_vs_fitted.py:16](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/scripts/bg_math_preview_vs_fitted.py:16)

   `fit_grid` now returns four values; this caller unpacks three and raises `ValueError`. Adapting that unpack in memory reproduces the note’s reported numbers.

Verification: census **10 current / 71 stale / 40 peaks-only**, Python twin outcomes and `final_analysis.json` reproduce. All **202 upload inputs, seeds and background arrays** match. The committed allowance maximum reproduces as **0.5887% across 16 fits**. The narrowed test still records actual scattered-start draws; CI floor is **552**.

**55 JS checks and 57 Python checks passed.** Two Python fixtures required forbidden writes; the longer run was stopped for the review budget. Full/browser suites were not completed. No files changed.

**VERDICT: NO-GO.**
