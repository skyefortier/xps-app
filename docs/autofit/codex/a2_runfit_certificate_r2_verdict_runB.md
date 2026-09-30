# A2 round 2 — run B (commit b66d6fe; codex exec, reasoning high)

1. **MAJOR — Unsupported components can still hide distinct certified minima.** [tests/fit_equality.py:120](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:120)

   Reproduced with complete `run_fit` responses, identical bounds and seed 123: a fixed Gaussian of height 1e6 and FWHM 300, plus one free Gaussian fitting either of two 500-height, 0.1-eV-wide lines at ±0.25 eV. Both fits certify at χ² **249842.892876**, with the small component unsupported (`F = 0.01005`). Profiling amplitude and width at the intervening centre gives χ² **249843.269643**: these are separate minima, five linewidths apart. **`assert_same_fit` accepts them.**

   Construction: `x = linspace(-500,500,20001)`; data are the dominant Gaussian `D`, both narrow lines, and symmetric residual `5*sqrt(D)*cos(3*x)*(abs(x)>2)`. Minor-component bounds: centre [−1,1], FWHM [0.05,0.15], amplitude ≥0; LM, no background or perturbations.

   “Unsupported” does not establish that two optimisation minima are identical. Skipping the entire component defeats the owner’s explicit requirement.

2. **MAJOR — Matching infinities disable comparison of finite component samples.** [tests/fit_equality.py:123](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:123)

   Starting from the tests’ real two-peak response, put `+inf` at the same component-curve index in both copies, then add **1,000,000 counts** to another sample in only one copy. The helper accepts them. Non-finite masks match, but `own` becomes infinity, so every finite difference passes. Compute the comparison scale from finite samples after validating the masks.

3. **MINOR — Scattered-starts objectives still receive the parameter tolerance.** [tests/fit_equality.py:41](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:41)

   `_OBJECTIVE` omits `chi2r`, used by the scattered-starts report. On a real response, changing only `starts.fit.chi2r` from **1.3608791486992644 to 1.3621039399330936** (+0.09%) passes, while `statistics.reduced_chi_square` remains unchanged. Alternative objectives have the same hole. Include these fields in the objective-scale comparison.

4. **MINOR — The note mixes measurement runs without identifying them.** [docs/comms/2026-09-30-run-fit-certificate-note.md:35](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/docs/comms/2026-09-30-run-fit-certificate-note.md:35)

   The corrected **4/202** default-method changes comes from the final run, where **198/202**, not 197, stayed below one percentage point; LM scattered-start failures were **30→3**, not 30→4. The latter figures belong to the earlier V3 run. Use one run consistently or label the sources.

Validation: **59 battery tests passed in each of three fresh processes; 122 JavaScript tests passed.** Both round-1 battery injections now fail. The broader Python sweep reached 36 passes before I stopped it for the review budget. Cancellation during certification raises `FitCancelled`; committed data confirm zero >1-eV notices and maxima 0.04299/0.01059 eV. Production certificate/UI code is unchanged since round 1. No files changed.

**VERDICT: NO-GO**
