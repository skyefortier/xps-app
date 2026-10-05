# Background math implementation — Codex round 25, run B (commit c9aebdc)

Reviewed `c9aebdc`, read-only. **Two MAJOR findings:**

1. **MAJOR — Offset-incompatible branches still exhaust the search cap and drop a uniquely identifiable fit.** [templates/index.html:10189](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10189), [templates/index.html:10226](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10226)

   Reproducer: fit twenty samples at `280 + 0.1i`, Gaussian starting at `(center=280.95, FWHM=1, amplitude=1000)`, manual background `10000`, counts rounded to two decimals. Backend convergence succeeds, RMSE `0.00307893245`.

   Append a second region at `300 + 0.1i`: leave its first energy unchanged, subtract `0.00004` from its eighteen interior energies, and add `0.00009` to its last energy. Duplicate each interior sample with corresponding original counts plus `0.001` and `0.002`.

   The backward table admits these samples under the initial offset interval. Interior selections narrow that interval so the final sample becomes impossible, but the dead branches still multiply until the cap declares ambiguity. **Increasing only the cap restores the unique original reading**, stale “unconfirmed,” as required by the owner’s policy.

   The wider table interval is conservative as a lower bound; its interaction with the work cap causes the incorrect rejection.

2. **MAJOR — Spectrum loading discards saved count evidence and drops an unchanged current keyed fit.** [templates/index.html:11963](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:11963)

   Reproducer: eleven samples at `280 + 0.1i`, Gaussian `(280.5, 0.5, 1000)`, manual background `10000`, alternating `±0.01` count noise. The backend converges with RMSE `0.0099895544`. Add an excluded raw sample at `279.99999`, with count `2 × fittedY[0] − originalCount[0]`.

   The two possible first samples have opposite residuals and identical squared residuals. Stored counts distinguish them: the project record restores current. **Production Save Spectrum followed by production loading drops the fit**, because the loader populates the background but ignores counts recoverable from the saved residuals and envelope.

   An in-memory control recovering `bgSubtracted = residuals + fittedY − background` restores it as current.

Verification: census **0 current / 81 stale / 40 peaks-only** reproduced exactly; Python twin verdicts agree. Measurement summaries and student-note figures reproduce; all **202 upload inputs, seeds, and background arrays** match. The narrowed test checks actual draws; CI floor is **561**.

**115 targeted JS and 84 Python checks passed.** Two Python fixtures required forbidden filesystem writes; the remaining optimizer tests were stopped for budget. Full/browser suites were not rerun. No files changed.

**VERDICT: NO-GO**
