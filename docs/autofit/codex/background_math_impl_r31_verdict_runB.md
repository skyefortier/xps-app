# Background math implementation — Codex round 31, run B (commit 94ea074)

One **MAJOR** finding.

1. **MAJOR — The RMSE tolerance underestimates grid-normalized components and drops a current fit.** [templates/index.html:9999](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9999), [templates/index.html:10161](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10161).

   `ampBound` assumes component magnitudes are bounded by their amplitudes. LACX normalizes its convolved curve at the sample nearest its center; on an unsorted grid, other samples can be much larger.

   Concrete reproducer:

   - Energies: concatenate `[280]`, `[5000+i, i=0…699]`, and `[280.01+0.00001i, i=0…1399]`. Counts: `0.1` throughout.
   - Fixed LACX: center `280`, FWHM `1`, amplitude `1000`, α=β=`1`, m=`499`.
   - Manual anchors at every sample, with intensity equal to the negative LACX value.
   - Gaussian: fixed center `5000`, fixed FWHM `1`, freely fitted amplitude.

   The backend succeeds. The LACX reaches **416324.82**, despite amplitude **1000**. Stored RMSE and the envelope-based reconstruction differ by **1.3603×10⁻¹¹**, exceeding `tolOwn`’s **3.6000×10⁻¹²**.

   Executing production Save Spectrum/load functions in memory saves the fit **current**, then drops it as **“its stored points are not points of its raw data.”** A control using evaluated component magnitudes restores it **current**.

   This is synthetic and atypical of XPS data, but reachable. There is exactly one reading; neither search cap is involved. The magnitude bounds used by both the verdict and pruning need to cover grid-normalized components.

Verification: census reproduces **0 current / 81 stale / 40 peaks-only**, with the Python twin agreeing. All five measurement summaries reproduce; all **202** upload round trips, seeds, background arrays and net areas match. **12,000** comparisons against disabled numerical pruning/memoization found no discrepancy.

**122 focused JS tests and 82 Python tests passed.** Two Python fixtures were blocked by filesystem permissions; full browser and optimizer suites were not certified. No files changed.

**VERDICT: NO-GO**
