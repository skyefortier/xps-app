# Background math implementation — Codex round 23, run A (commit f186951)

Reviewed `f186951`, read-only. **Three MAJOR findings:**

1. **MAJOR — Shifted-keyless reconstruction can still hide a genuine background change.** [templates/index.html:10013](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10013)

   Reproducer: legacy keyless Gaussian, locked center `285`, FWHM `1`, amplitude `100000`; eleven energies `284.55 + 0.005i`; original constant manual background `100`. The backend successfully fits the old rounded upload. Apply charge correction `+0.01004`, shifting the peak accordingly, and change the manual background to `94.3`.

   Restoration **accepts this 5.7% background change**, installs `94.3`, and sets no `backgroundStale`. Keeping the original background instead produces **5.713% staleness**. The reconstructed component’s rounding error cancels the actual background change. Withdrawing the allowance does not make uncertainty one-sided.

2. **MAJOR — Save Spectrum still writes inconsistent curves and residuals for restored-current legacy fits.** [templates/index.html:11509](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:11509)

   The `_modelBe` fix applies only when `_restoredStale` is true.

   Reproducer: keyed legacy Gaussian `(center=280.5, FWHM=0.2, amplitude=1000)`, raw energies `280.00004 + 0.1i`, background `10`. Restore unchanged: correctly current. The production saver then writes, at `280.40004`, background `10`, component `500.2772802763`, and envelope approximately `510`. It also writes residual **−0.2772802765**, although raw counts minus the saved envelope is **zero**.

3. **MAJOR — The search-step limit drops a fit uniquely identified by stored counts.** [templates/index.html:10189](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10189)

   Reproducer: keyless Gaussian fit on `[280,280.5,281,281.5,282]`, counts `[62.5,500,1000,500,62.5]`, background zero, RMSE zero. Append another run at `290…292`, with each sample repeated five times and its center count changed to `999.999`.

   The second run meets the RMSE allowance, but six-significant-figure counts exclude it. Nevertheless, its duplicate assignment paths exhaust `64 × (n+1)` steps and drop the entire fit as indistinguishable. **Lifting only that limit selects the original five samples correctly.** Deduplicating completed readings does not make this separate cutoff sound.

Verification: census **10/71/40**, Python twin, measurement analysis, and student-note numbers reproduce. All **202 upload inputs, background arrays, and request seeds** match. The narrowed test checks actual scattered-start draws; CI floor is **557**.

**122 JS and 84 Python checks passed.** Two Python fixtures required forbidden writes; the longer run was stopped for budget. Full optimizer and browser suites were not rerun. No files changed.

**VERDICT: NO-GO.**
