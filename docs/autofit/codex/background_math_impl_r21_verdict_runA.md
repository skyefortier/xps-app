# Background math implementation — Codex round 21, run A (commit dcca5a4)

Reviewed `dcca5a4`, read-only. **Three MAJOR findings:**

1. **MAJOR — A restored charge-shifted fit cannot survive another project save/load.** [templates/index.html:10007](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10007)  
   Restoration replaces `fr.be` with today’s corrected energies but retains the original key’s charge frame. The next load applies that charge difference again.

   Reproducer: raw energies `0…5`, fit points `1…4`, Gaussian `(center=2.5, FWHM=1, amplitude=100)`, manual background `10`. Change charge correction to `0.5` and background anchors to `20`, then save/load. It correctly restores 50% stale with energies `[0.5,1.5,2.5,3.5]`. Save that restored project without editing and reload: **the fit is dropped as “not points of its raw data.”** Reproduced through the production project saver.

2. **MAJOR — Legacy upload rounding is mistaken for a changed background.** [templates/index.html:9986](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9986)  
   Historical uploads rounded energies to four decimals. Restoration now always evaluates components at unrounded raw energies, so it subtracts a different component curve from the historical envelope.

   Reproducer: raw energies `280.00004 + 0.1i`, `i=0…10`; locked Gaussian `(center=280.5, FWHM=0.2, amplitude=1000)`. Fit using the old upload formatting and backend from `0c7ea15`, then restore unchanged. The successful fit becomes **100% background-stale with None**, or **0.276514% stale with constant manual background 100**. Both backgrounds are unchanged. The implementation needs to distinguish upload rounding from project serialization rounding.

3. **MAJOR — The claimed rigorous RMSE bound excludes a correct, successful fit.** [templates/index.html:10091](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10091)  
   The bound omits accumulation error from the sequential sum of squared residuals.

   Concrete extreme but accepted finite input: 16,384 energies `0…16383`, constant counts `I=171337899239733.8`, manual background `B=94231556951999.66`, locked Gaussian centered at `8192`, FWHM `1e16`, amplitude `P=65942324525676.664`. Its evaluated component is constant. The successful backend’s residual is `(I−B)−P=11164017762057.492`; restoration computes `I−(B+P)=11164017762057.5`. After sequential square accumulation, saved RMSE is `11164017762055.322`, versus recomputed `11164017762057.277`: **difference 1.955078125 exceeds the allowed 0.3019205194**. Restoration rejects the sole correct reading and drops the fit.

Verification: census **10 current / 71 stale / 40 peaks-only**, Python twin, measurement analysis, and student-note numbers reproduce. All **202** upload inputs, seeds, and background arrays match the measurement records. Indistinguishability refusal is reachable for keyless flat/repeated-count windows; none of the committed 121 hits it. The narrowed test still checks actual draws; CI floor is **548**.

**101 targeted JS and 127 Python tests passed**; four Python fixtures required forbidden writes. Full suites were not verified clean in this sandbox. No files changed.

**VERDICT: NO-GO.**
