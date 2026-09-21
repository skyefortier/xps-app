Reviewed HEAD `f49ad4a`, read-only. **Two MAJOR findings and one MINOR. No BLOCKER.**

1. **MAJOR — High-count spectra can accept materially worse refinements.** [fitting.py:1060](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1060)

   Reproducer: `x = linspace(999,1001,1000)`, Poisson counts from a Gaussian with amplitude `1e6`, centre `1000`, FWHM `15`; `default_rng(0)`. Fix centre and width, leave amplitude open above, and use no background.

   Here, `P = 995,903,002`, giving an absolute allowance of **9.95903**. The same 1% chi-square fault injection used by the new regression test is **accepted**: **991.07935 → 1000.99014**.

   I also injected a consistent degraded result by shifting amplitude **99.76 counts**, approximately **3.16 standard errors**, and recomputing predictions, residuals and statistics. It likewise returns `success=true`. Seed 2 accepts a **0.9%** degradation with initial chi-square/point **1.02257**, squarely within the requested range.

   These are acceptance-gate fault injections, not claims that the unmodified solver naturally produced those degradations.

2. **MAJOR — Removing the absolute floor introduces false failures on zero/near-zero signals.** [fitting.py:1060](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1060)

   Reproducer: 101 points over `999–1001`, constant counts **1000**, manual background **1000**. Fit a Gaussian with fixed centre **1000**, fixed FWHM **0.5**, and amplitude starting at its requested minimum **0**, open above.

   DE returns amplitude **0**, chi-square **1.01e-248**. Successful refinement nudges amplitude to **1e-10**, producing chi-square **1.88173e-22**. Because **P=0**, HEAD rejects this negligible displacement and reports failure caused by generated limits.

   Reproduced with **zero and three perturbations**. Restoring the round-6 allowance in memory makes both succeed. Tiny positive and negative background-subtracted signals also reproduce false rejection.

3. **MINOR — Power includes observations omitted from the residual objective.** [fitting.py:1059](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:1059)

   Ordinary NaNs in `y_sub` are excluded consistently. However, a finite intensity whose **energy is NaN** contributes to `P`, while its Gaussian residual is omitted.

   Concrete normalized-data probe: 101 points, Gaussian amplitude `1e-4`, noise standard deviation `1e-6`, then set `x[50]=NaN`, `y[50]=1`. Weights remain 1. The fit uses 100 residuals, but the omitted observation inflates `P` from approximately **1.787e-7 to 1.00000018**. A fault-injected **100-fold** chi-square increase, **9.16038e-11 → 9.16020e-9**, is accepted through `run_fit`. Also, `nansum` retains infinity, whereas residual omission removes it; an infinite power makes the comparison ineffective.

Validation: **41 tests passed; one upload test excluded to preserve read-only execution.** No files changed. The full suite was not independently rerun.

**VERDICT: NO-GO.**
