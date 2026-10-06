# Background math implementation — Codex round 26, run A (commit 14560d7)

Reviewed `14560d7`, read-only. **One MAJOR finding.**

1. **MAJOR — The dead-state dominance rule drops an unchanged current fit.** [templates/index.html:10246](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10246)

   RMSE agreement is two-sided. A completion can fail because its residual is **too small**; reaching the same state with a larger partial sum can then agree. The memo incorrectly prunes that arrival.

   Concrete backend-verified reproducer: eleven samples at `280 + 0.1i`, Gaussian `(center=280.5, FWHM=0.5, amplitude=1000)`, manual background `10000`, alternating `±0.001` count noise. Include an excluded raw sample at `279.99999` whose count equals `fittedY[0]`. Save the keyed, full-precision fit using normal project rounding.

   The fit succeeds with RMSE `0.0009989554457`. The alternative first sample gives RMSE `0.0009558111306`: too small to agree. That path marks the shared suffix dead, suppressing the correct reading. Production restore reports “its stored points are not points of its raw data” and drops the fit. **Disabling only the memo restores the unique original reading as current.**

   Failure below the RMSE interval cannot justify this dominance rule. Any replacement memo must also account for the prefix-dependent arithmetic bound used by `rmseAgrees`.

Verification: **116 targeted JS checks and 83 Python tests passed**, with an in-memory workaround for sandbox import restrictions. Census reproduced exactly: **0 current / 81 stale / 40 peaks-only**; Python twin verdicts agree. Measurement summaries and student-note figures reproduce. Formatter/parser probes round-trip bit-exactly. The narrowed scattered-starts test checks actual draws; CI floor is **562**.

Full-suite verification was limited by the read-only environment; browser tests were not rerun. No files changed.

**VERDICT: NO-GO**
