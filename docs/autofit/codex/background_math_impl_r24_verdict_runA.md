# Background math implementation — Codex round 24, run A (commit 52e9ca5)

Reviewed `52e9ca5`, read-only. **Three MAJOR findings:**

1. **MAJOR — A sub-4-decimal charge change hides a genuine background change.** [templates/index.html:10029](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10029)

   Reproducer: legacy keyless Gaussian, center `285`, FWHM `1`, amplitude `100000`, eleven energies `284.55 + 0.005i`, constant background `100`. The backend successfully fits the rounded upload, RMSE `0.003371537`.

   Apply charge correction `0.00004` and change the manual background to `94.3`. Reconstruction estimates the original background as `94.2869–94.3068`. Restoration installs `94.3` with **neither `backgroundStale` nor `frameMoved`**, so statistics escape the required stale suppression despite a **5.7% genuine change**. This demonstrates a reachable consequence of the stated rounding limit.

2. **MAJOR — The increased search cutoff still drops a uniquely identifiable fit.** [templates/index.html:10192](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10192)

   Reproducer: legacy 18-point fit at `280 + 0.1i`, Gaussian `(center=280.85, FWHM=1, amplitude=1000)`, background `10000`, stored counts rounded to six significant figures.

   Append another region at `300 + 0.1i`: duplicate its first 17 energies with counts `original + 0.001` and `original + 0.002`; its final count is `original + 1`. Partial branches pass the count checks, but the final count excludes every completed alternative.

   Production restoration nevertheless exhausts `4096 × (n+1)` steps and drops the fit as ambiguous. **Raising only that cutoff selects indices 0–17 uniquely.** Equal-energy samples with different counts still cause exponential branching.

3. **MAJOR — Save Spectrum loses a restored fit stale only through its model key.** [templates/index.html:11573](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:11573)

   Reproducer: keyed Gaussian `(center=282.5, FWHM=1, amplitude=100)`, background None, fitted samples `281…284` within raw energies `280…285`. Apply charge correction `+0.5`, then restore and save without further edits.

   The saver correctly preserves the fit’s own curves, but writes `statisticsState: "stale"` and `restoredStale: null`: `_restoredStale` excludes model-key staleness. The [loader](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:11926) consequently **drops the checkable fit**. Reproduced through the production saver and loader.

Verification: census **8/73/40**, serialized Python twin, measurement analysis and student-note numbers reproduce. All **202 upload inputs, seeds and background arrays** match. The narrowed test checks actual draws; CI floor is **559**.

**95 targeted JS and 82 Python checks passed.** Two Python fixtures required forbidden writes; the longer JS parity run was stopped for budget. Full/browser suites were not completed. No files changed.

**VERDICT: NO-GO.**
