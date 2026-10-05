# Background math implementation — Codex round 18, run B (commit 131cc39)

Reviewed `131cc39`, read-only. Six MAJOR findings:

1. **MAJOR — Grid-step charge shifts select the wrong samples.** [templates/index.html:10003](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10003)  
   Exact energy matching returns before checking stored counts/RMSE. Reproducer: raw energies `0…9`, fitted points `[2,3,4,5]`, GL peak `(center=3.5, FWHM=1, amplitude=100, mix=30%)`, constant manual background `10`; increase charge correction by `1`. Restore selects raw samples `[3,4,5,6]` and reports **82.414% stale**, although the background is unchanged. Reproduces in both orders; a `0.25` shift restores correctly.

2. **MAJOR — Project-save rounding makes current full-precision fits stale.** [templates/index.html:9996](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9996)  
   Project saves round `fr.be`, but retain the full-precision envelope. Restore evaluates peaks at those rounded energies (`modelBe: stored`). With energies `[2.000012,3.000023,4.000034,5.000045]` and the GL peak above, an unchanged `none` fit reloads **100% stale**; an unchanged constant manual background `0.1` reloads **4.197% stale**.

3. **MAJOR — Ordinary floating-point peak differences make zero-background fits stale.** [templates/index.html:9961](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9961)  
   This also fails without energy rounding. For a server Gaussian on `linspace(280,290,101)`, amplitude `100`, center `284.123`, FWHM `1.14`, page reconstruction differs by just **1.421e-14 counts**. With `none`, that subtraction error becomes the entire background scale, producing **100% stale** for a current fit.

4. **MAJOR — Historical Voigt fits are restored using one shape and displayed using another.** [templates/index.html:10050](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10050), [templates/index.html:10105](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10105)  
   Recorded η is applied only to temporary copies during comparison. Display still evaluates `Voigt` at η=`0.5`; background-stale rendering recomposes the envelope with those incorrect peaks. In committed `Cl2p_projfit_test.proj.zip / Cl2p Scan_1`, recorded η is `0.1571334411`; the displayed envelope differs from the saved fit by up to **338.076 counts**. This violates “its own background and peaks as saved.”

5. **MAJOR — Saving a background-stale spectrum destroys its fitted envelope.** [templates/index.html:11335](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:11335), [templates/index.html:11719](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:11719)  
   Load a fit made against background `10` whose current manual anchors give `20`: it correctly restores 50% stale. Save Spectrum replaces its envelope with `peaks + 20`; reloading then unconditionally drops the fit because `statisticsState === 'stale'`. The checkable historical fit cannot survive this save/reload cycle.

6. **MAJOR — Scattered-starts consumers bypass background staleness.** [templates/index.html:8397](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:8397), [templates/index.html:8555](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:8555)  
   `_startsIfCurrent` checks only the model key. A background-stale reload with saved starts and `chosenAlternative` still displays its comparison and χ² values and includes them in CSV/XLSX through `_startsChosenText`. Reproduced with `_statsState === 'stale'` while the panel/export retained `χ²ᵣ 12.34 → 6.78`.

Two smaller findings:

- **MINOR — Linear averaging becomes disabled after loading or switching tabs.** [templates/index.html:3899](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:3899): `_restoreUI` retains the old `needsEpAvg` condition, unlike `_onBgTypeChange`.
- **MINOR — Measurement prose undercounts worse fits.** [plan:864](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/docs/superpowers/plans/2026-10-01-background-math-implement.md:864): “Three of the six” contradicts the four rows labelled worse in its table and their committed χ² values.

Verification: **58 Python and 67 JavaScript tests passed**, plus **200 exact averaged Linear/manual parity probes**. Census reproduced **15/66/40**; `final_analysis.json` reproduced exactly; the Python twin and student-note measurements agreed. Parser compatibility and finite-double round-trip probes passed. CI floor is **539**. Full browser/HTTP suites were not rerun; no files changed.

**VERDICT: NO-GO.**
