# Background math implementation — Codex round 25, run A (commit c9aebdc)

Reviewed `c9aebdc`, read-only. **One MAJOR finding.**

1. **MAJOR — Backward reachability still lets impossible branches exhaust the cap and drop an identifiable fit.** [templates/index.html:10189](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10189), [cap:10226](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10226)

   Concrete reproducer: a keyless legacy fit on twenty energies `280 + 0.1i`, Gaussian `(center=280.95, FWHM=1, amplitude=1000)`, manual background `10000`, and project-rounded stored counts. The actual backend fit succeeds with RMSE `0.0030789330132251825`.

   Append another region with corresponding original counts: first energy `300`; for `i=1…18`, two energies `300 + 0.1i + 0.00008` and `+0.00009`; final energy `301.9 − 0.00008`.

   The backward table admits these samples independently within the search’s original offset interval. But the middle samples require offsets below `−20.00003`, while the final sample requires one above `−19.99997`. No alternative can complete at one offset. Nevertheless, the middle choices multiply until the cutoff declares ambiguity and drops the fit.

   **Increasing only the cap in memory restores the original twenty samples uniquely**, correctly marked stale-unconfirmed with `matches: true`. The wider table is conservative as a pruning bound, but fails to prevent this false refusal. This violates §7’s retention of checkable historical fits.

Verification: **140 targeted JS tests, 82 Python tests, and 243 keyed project-load probes passed.** Census **0 current / 81 stale / 40 peaks-only** reproduces exactly; Python twin verdicts agree. All five measurement summaries and student-note measurements reproduce. All **202** current upload inputs, seeds, and background arrays match the committed measurement records. The narrowed test checks actual draws; CI floor is **561**.

Full optimizer/browser suites were not rerun. No files changed.

**VERDICT: NO-GO**
