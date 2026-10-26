No BLOCKER found. **Three MAJOR findings remain.**

Read-only verification: **27 tests passed**. The full 14,040-spectrum benchmark and both real-data analyses reproduced all seven committed JSON/text/Markdown outputs exactly, using in-memory output capture. I analysed the committed fit collection; I did not collect new browser refits.

1. **Is every round-2 finding resolved? No.**

   Resolved: the per-file gap/time bounds, VGD averaging citation, AIC/BIC floor qualification, ten-estimator synthetic tables, CPS-at-one-second row, separate `scaled_d1` correlation results, and individual Gaussian constant-estimator levels. See [README.md:37](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:37), [real_spectra.txt:67](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/real_spectra.txt:67), [README.md:48](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:48), [synthetic_tables.md:3](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/synthetic_tables.md:3), and [README.md:140](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:140).

   Both round-2 quantum counterexamples now pass, as do the specified offset tests. However, the general quantum guarantee remains false, and the revised estimator recommendation still exceeds the evidence.

2. **Is `common_quantum` correct as stated? No — MAJOR.**

   This new counterexample returns `None`:

   ```python
   counts = np.array([
       1000, 123456, 200000, 500000, 100000001, 100000002
   ])
   common_quantum(counts / 1000.0)
   ```

   These are counts divided by **1,000 seconds**, with quantum **0.001**, smallest count difference **m = 1**, and intensities **1–100,000.002 CPS**. The calculated smallest gap is `0.0009999999892897904`. Initial rounding assigns the two largest values count indices **one too high**. Least-squares refinement preserves those incorrect assignments and settles at approximately `0.000999999990000153`. Enumerating divisors and iterating assignments therefore does not guarantee finding the valid grid. The true quantum passes the routine’s own residual allowance. [noise_estimators.py:207](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_estimators.py:207)

   The acceptance criterion also differs from the stated error model: it uses **2 ulps of the largest value plus 4 ulps of `u` times the multiple**, rather than the described half-ulp value rounding. For example:

   ```python
   common_quantum(np.array([1.0, 2.0, 3.0 + 4e-15]))
   # 1.0000000000000009
   ```

   Residuals are approximately `[8.88e-16, 1.78e-15, 1.33e-15]`, exceeding half-ulp value rounding plus half-ulp quantum rounding. These stored values have no exact common quantum within the stated divisor bound. [noise_estimators.py:198](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_estimators.py:198), [noise_estimators.py:221](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_estimators.py:221)

   Checking values fixes the original gaps-only mistake, but neither universal detection nor universal rejection is established. Describe the result as compatibility under a specified numerical error model; either establish completeness within that model or narrow negative results to “no candidate accepted.”

3. **Are the VERIFIED claims justified, and do tables and sentences match outputs? Not entirely.**

   The **0/230 and 0/166 routine results reproduce**, but the stronger VERIFIED statements that those spectra are “on no common grid” are not established by this incomplete search. This affects both the VGD and project rows. It does not demonstrate that any committed spectrum actually is gridded. [README.md:46](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:46), [README.md:49](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:49)

   The other principal implementation/provenance claims checked out, including 230 CPS sidecars, single-series VGDs, instrument/version strings, and 70 exact project matches. Acquisition-time, correction-mechanism, and unmatched-project provenance assumptions remain appropriately labelled HYPOTHESIS.

   **The README’s numerical table cells match the generated outputs within rounding.** Some explanatory sentences do not, as detailed below.

   **MINOR:** the README still says “24 tests”; the current suite contains and passes **27**. [README.md:255](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:255)

4. **Does any sentence conclude more than the measurement supports? Yes.**

   **MAJOR — transmission noise is incorrectly included in the “right shape” claim.** The README includes transmission among scaled-Poisson cases and says `scaled_d4` and `flat_ends` both recover the right shape. But the implemented truth is `v_i = s_i / T_i`, with varying `T_i`; a single `k·s_i` cannot reproduce it. Both estimators’ measured shape spreads are **1.63**, not 1. Separate this case from constant-scale Poisson noise and report its remaining shape error. [README.md:137](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:137), [noise_synthetic_benchmark.py:76](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_synthetic_benchmark.py:76), [synthetic.txt:138](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/synthetic.txt:138)

   **MAJOR — “`scaled_d4` is the closest” remains unsupported by the specified metrics.** Splitting by variance family fixes the Gaussian counterexample, but does not establish this ranking. For independent Poisson counts, overall median level ratios are **1.0149 for `flat_ends` versus 1.0629 for `scaled_d4`**, with shape spread **1 for both**. For CPS at 0.05 seconds and the highest level, the ratios are **1.00013 versus 1.06571**, again with equal shape spread. A preference based on tails, robustness to endpoint curvature, or another aggregate criterion needs that criterion stated and measured. [README.md:221](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:221), [synthetic.txt:90](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/synthetic.txt:90), [synthetic.txt:95](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/synthetic.txt:95), [synthetic_tables.md:5](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/synthetic_tables.md:5)

   Relatedly, the round-2 objection to “the data’s correlation decides between the difference family and `flat_ends`” remains unresolved: that sentence is unchanged. Variance law and endpoint signal structure also matter. [README.md:152](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:152)

   Part (d)’s frozen-residual reporting and explicit limits remain appropriately qualified. [README.md:206](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:206)

VERDICT: NO-GO.
