**No BLOCKER or MAJOR findings. Two MINOR wording issues remain.**

Read-only verification: **27 tests passed**. The full 14,040-spectrum benchmark and both real-data analyses reproduced all seven committed outputs exactly in memory. No files changed; no fresh refits were collected.

1. **Is every round-4 finding resolved? Substantively yes, with one remaining acquisition-time qualification.**

   The rounding correction is implemented, the grid-search output describes accepted candidates, and the test docstring limits success to tested cases. The MA3 discussion now distinguishes fourth-difference correlation from the changing lag profile. See [noise_real_spectra.py:96](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_real_spectra.py:96), [test_noise_estimators.py:74](/Users/skyefortier/xps-app/.claude/worktrees/noise/tests/test_noise_estimators.py:74), and [README.md:158](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:158).

2. **Are VERIFIED claims true and unestablished claims labelled HYPOTHESIS? The explicit VERIFIED claims checked out; the acquisition prose still overstates its calculation.**

   **MINOR — a lower bound is described as a sufficient acquisition time.** “99 … files would need under 2 minutes” should say their **calculated lower bounds are below 120 seconds**. The generator substitutes the lower bound for \(t\); it does not demonstrate a compatible counting time or acquisition schedule. Moreover, only **68** bounds are below 60 seconds, so “for them the bound excludes nothing” needs qualification against the preceding “about a minute.” [README.md:46](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:46), [noise_real_spectra.py:98](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_real_spectra.py:98).

   The [Thermo datasheet](https://assets.thermofisher.com/TFS-Assets/MSD/Datasheets/ds0364-nexsa-g2-xps.pdf) confirms 128-channel hardware; that does not establish these files’ acquisition model. The overall conclusion **“not established either way”** remains appropriate.

3. **Do the README’s tables and sentences match generated outputs? The tables do, within displayed rounding; one additional sentence needs narrowing.**

   **MINOR — “independent noise” is too broad for the estimator-ratio comparison.** The claimed `flat_ends / scaled_d4` ratio of approximately **0.9–1.1** does not cover independent constant noise: its aggregate level medians are approximately **1.31 / 0.89 = 1.47**. The mixed-noise case also falls outside that range. Restrict the comparison to the applicable scaled-Poisson cases. [README.md:182](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:182), [synthetic.txt:42](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/synthetic.txt:42), [synthetic.txt:47](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/synthetic.txt:47).

4. **Does any sentence conclude more than the measurement supports? Yes—the two statements above.**

   Neither changes the principal design conclusions: estimator suitability depends on the variance law and correlation, and elevated real-fit χ²ᵣ does not distinguish model inadequacy from underestimated noise. Those limitations remain explicit in [README.md:219](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:219) and [README.md:227](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:227). The remaining issues are minor within this design-and-measurement scope.

VERDICT: GO
