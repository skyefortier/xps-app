**No BLOCKER findings. One MAJOR and three MINOR findings remain.**

Read-only verification: **27 tests passed**. The full 14,040-spectrum benchmark and both real-data analyses reproduced all seven committed outputs exactly, using in-memory capture. I analysed the saved fit collection; I did not collect fresh refits.

1. **Is every round-3 finding resolved? Almost, but not throughout the unit.**

   The estimator conclusions are corrected: transmission is separated, its shape spread is **1.63158**, and `flat_ends` is closer to 1 in **16/20** case-levels. The variance law, correlation, and signal structure now all enter the selection discussion. The test count is correct. See [README:137](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:137), [README:155](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:155), [README:224](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:224), and [README:259](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:259).

   `common_quantum` now accurately describes its incompleteness and implemented tolerance. However, stronger claims survive in the generated report and tests; see item 3. [noise_estimators.py:193](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_estimators.py:193)

2. **Is the gap bound correct, and are the rows labelled correctly? The exact per-point argument is correct; the acquisition-time interpretation needs another assumption.**

   For exact values \(y_i=N_i/t\), every positive gap is \(m/t\), with integer \(m\ge1\). Therefore \(t\ge1/g_{\min}\), without searching. The reported numerical ranges reproduce. The project row correctly limits VERIFIED to the matches, non-integer values, and search outcome. [README:46](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:46), [README:49](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:49)

   **MAJOR — summed point exposure is not an established lower bound on elapsed acquisition time.** Multiplying by the number of points establishes \(N_{\text{points}}t\), but comparing that quantity with start/end timestamps assumes sequential acquisition without simultaneous channel collection. The generator merely multiplies; it does not establish that assumption. [noise_real_spectra.py:95](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_real_spectra.py:95)

   This matters here: the Nexsa G2 has a 128-channel detector, and Thermo documents multichannel collection at different energies, including simultaneous acquisition. [Nexsa G2 datasheet](https://assets.thermofisher.com/TFS-Assets/MSD/Datasheets/ds0364-nexsa-g2-xps.pdf), [Thermo application note 31009](https://documents.thermofisher.com/TFS-Assets/CAD/Application-Notes/D16066~.pdf). **My inference:** the acquisition model must be established before treating **435 s** as an elapsed-time bound. Keep the per-point bound VERIFIED; explicitly qualify the conversion to elapsed time alongside the timestamp hypothesis.

   **MINOR — “no tolerance” needs an exact-value qualification.** Stored floating-point counts/time values need not satisfy the exact inequality literally. Reproducing round 3’s counts divided by `10000.0` gives \(1/g=10000.000070722308\), slightly above the true \(t\). A rounding-error bound resolves this and does not materially change the reported ranges. [README:46](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:46), [noise_real_spectra.py:61](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_real_spectra.py:61)

3. **Do the tables and sentences match generated outputs? The numerical tables do, within displayed rounding; some wording does not.**

   **MINOR — grid-certification wording remains in the supporting artifacts.** The report still says “files on a common grid …: 0” and “on a common grid: 0.” These are counts of accepted candidates, not certified grid exclusions. Update the generator and regenerate the report. [noise_real_spectra.py:87](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_real_spectra.py:87), [real_spectra.txt:69](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/real_spectra.txt:69). The test docstring also still claims the search finds the quantum “for any t.” [test_noise_estimators.py:75](/Users/skyefortier/xps-app/.claude/worktrees/noise/tests/test_noise_estimators.py:75)

   **MINOR — “the diagnostics … miss a 3-point moving average” is too broad.** The fourth-difference correlation misses it, but the measured lag profile changes to **1, 3.20, 6.84, 8.67**. Qualify this as the correlation reading alone; no validated classification rule is established either way. [README:157](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:157), [synthetic.txt:98](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/synthetic.txt:98)

4. **Does any sentence conclude more than the measurement supports? Yes—the acquisition-time conversion and residual wording above.**

   The revised estimator comparison is supported. Part (d) also remains appropriately limited: elevated χ²ᵣ does not distinguish model inadequacy from underestimated noise, and expert fits are not treated as truth. [README:216](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:216)

**VERDICT: NO-GO.**
