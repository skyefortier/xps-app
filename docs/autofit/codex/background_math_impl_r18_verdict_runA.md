# Background math implementation — Codex round 18, run A (commit 131cc39)

Reviewed `131cc39`, read-only. **Seven MAJOR findings:**

1. **MAJOR — “None” falsely reloads stale from floating-point noise.** [templates/index.html:9966](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9966)  
   A server Gaussian at center `285.123`, FWHM `1.123`, amplitude `500`, on `280…290` in `0.125` steps reconstructs a background of only `5.68e-14` counts. Because today’s background is zero, `worst === scale`: the unchanged fit reloads **100% stale**, suppressing its statistics.

2. **MAJOR — Grid-step charge shifts bypass the sample-identification evidence.** [templates/index.html:10003](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10003)  
   On a `0.125 eV` grid, fit ROI `282–290`, then change charge correction by `0.5 eV`. Exact energy matching selects a different raw-sample run before consulting stored counts. An unchanged Gaussian-plus-Linear example reloads **75.9% background-stale**, in both energy orders.

3. **MAJOR — This version’s project saves falsely stale full-precision fits.** [templates/index.html:9996](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9996)  
   Project saving rounds `be` to four decimals but preserves the full-precision envelope. Restoration evaluates peaks at those rounded energies. For `BE = 280.00004 + i/8`, a Gaussian of amplitude `10000`, FWHM `1`, center `285`, over a 100-count Linear background reloads **0.56% stale** without any edit.

4. **MAJOR — Legacy Voigts are checked at their recorded eta but displayed at 0.5.** [templates/index.html:10050](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10050), [chart:10585](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10585)  
   The GL conversion affects temporary copies only. On committed `Cl2p_projfit_test / Cl2p Scan_1`, recorded eta is `0.157133441…`; the restored stale envelope drawn with eta `0.5` differs by up to **338.08 counts**. It does not show the fit’s saved components.

5. **MAJOR — Saving a background-stale spectrum destroys its recoverable fit.** [templates/index.html:11335](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:11335), [reload:11719](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:11719)  
   Restore a fit using a 100-count manual background against today’s 110-count anchors. “Save Spectrum” writes today’s 110-count background and recomposed envelope instead of the preserved fit. Reload then unconditionally drops it to peaks-only. Reproduced through the production saver and loader.

6. **MAJOR — Full-precision upload can silently discard numeric rows.** [parser.py:133](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/parser.py:133)  
   For energies `[3,2,1]`, counts `[-1,1e19,1]`, `String(v)` produces mixed signed/large unsigned integer text. Pandas classifies the column as nonnumeric; header skipping discards the first sample. `_exact_columns` runs too late. The former decimal-form upload preserves all three samples.

7. **MAJOR — §7.3 understates the worse-fit count.** [plan:864](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/docs/superpowers/plans/2026-10-01-background-math-implement.md:864)  
   “Three of the six” conflicts with the committed measurements and its own table: **four** are worse—8-JT Scan_5, 1-GTA Scan_0, B4C-UCl4 Scan_7, and Cl2p_projfit_test U4f Scan_1.

Verification: **67 JS checks passed; 96 Python checks passed** before stopping the longer run. Two HTTP fixtures were blocked by read-only filesystem permissions. Census **15/66/40**, generated analysis JSON, and student-note preview numbers reproduced. Full browser suites were not rerun. No files changed.

**VERDICT: NO-GO.**
