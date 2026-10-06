# Background math implementation — Codex round 31, run A (commit 94ea074)

Reviewed `bg-math-implement` at `94ea074`, read-only. **One MAJOR finding.**

1. **MAJOR — Underflow in the RMSE search window drops an accepted current fit.** [templates/index.html:10187](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10187), [10259](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10259).

   Concrete reproducer:
   - Energies: `[280, 280.5, 281, 281.5, 282]`.
   - Counts: `[2e-162, 0, 0, 0, 0]`; background None.
   - Gaussian: amplitude locked at `0`, FWHM locked at `1`, center initially `281` and free.

   The fit endpoint returns **HTTP 200, success and certified**. Its envelope is zero. The page computes RMSE `0`: the squared-residual sum is `5e-324`, but division by five underflows to zero.

   On reload, `ssWindow` also produces `ssMax = 0`. The backward-table prune therefore rejects the sole reading because `5e-324 > 0`, although `rmseVerdict` accepts it. Production Spectrum and Project serialization both reproduce the loss; disabling numerical pruning restores the reading.

   The relative `(2n + 4)u` widening cannot cover underflow. The window needs conservative handling of subnormal arithmetic.

   **Proportionality:** these intensities are unrealistic for XPS. Nevertheless, this is an accepted, current keyed fit that the record uniquely identifies, satisfying the stated MAJOR criterion. Neither search cap is involved.

Verification otherwise:

- Census and Python twin reproduce **0 current / 81 stale / 40 peaks-only**.
- All five measurement summaries and student-note figures reproduce.
- All **202** upload round trips, seeds, background arrays and net areas match.
- **30,000** ordinary-scale search comparisons found no discrepancy.
- **243 Spectrum + 243 Project** stale-fit cycles and **60 current Spectrum** cycles passed.
- **132 JS and 141 Python tests passed**; ten Python fixtures were blocked by filesystem permissions. The narrowed scattered-starts test checks actual draws and passes.
- CI floor remains **568**. No files changed.

**VERDICT: NO-GO**
