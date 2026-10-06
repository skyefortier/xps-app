# Background math implementation — Codex round 26, run B (commit 14560d7)

Reviewed `14560d7`, read-only. **One MAJOR finding.**

1. **MAJOR — The dead-state dominance rule drops a uniquely identifiable current fit.** [templates/index.html:10246](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10246), [dead-state insertion:10253](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10253)

   RMSE agreement is **two-sided**. A subtree can fail because its residual sum is too small; reaching that same state with a larger sum can succeed. Marking every later arrival with `ss >= failedSS` dead is therefore unsound.

   Concrete reproducer: successfully fit eleven samples at `280 + 0.1i`, with Gaussian `(center=280.5, FWHM=0.5, amplitude=1e6)`, alternating `±0.01` count noise, and background None. Preserve its key and full-precision marker; save counts at project precision. Include an excluded raw sample at `279.99999` whose count equals `fittedY[0]`.

   Both first-point choices satisfy the rounded count evidence. The excluded sample produces RMSE **0.010099691367**, below the stored **0.010363524814**. Its failed path poisons the shared memo state, pruning the correct path.

   **Production restore drops the fit as “not points of its raw data.” Disabling only the memo check restores the correct eleven samples as current.** This violates §7’s restore requirement.

Verification: census **0 current / 81 stale / 40 peaks-only** reproduces exactly; Python twin verdicts agree. All five measurement summaries and student-note figures reproduce. All **202** parsed upload inputs, request seeds, and background arrays match the committed measurement records. The narrowed scattered-starts test still compares actual draws; CI floor is **562**.

**84 Python checks passed** before stopping the longer run; an HTTP fixture required forbidden filesystem writes. JS checks also encountered temporary-directory restrictions. Full/browser suites were not completed. No files changed.

**VERDICT: NO-GO**
