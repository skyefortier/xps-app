**No BLOCKER or MAJOR findings. Three MINOR wording/precision issues remain.** All 27 tests passed. The full 14,040-spectrum benchmark and both real-data analyses reproduced all seven committed outputs exactly, using in-memory capture. No files changed; no fresh refits were collected.

1. **Are the round-3 findings resolved? Substantively, yes.**

   The search now states its actual tolerance, incompleteness, and meaning of `None`; transmission is separated from one-scale noise; the unsupported ranking is replaced by an explicit comparison; estimator selection includes variance law and signal structure; and the test count is corrected. See [noise_estimators.py:192](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_estimators.py:192), [README.md:137](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:137), [README.md:155](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:155), and [README.md:259](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:259). Some older wording was not updated, as noted below.

2. **Is the gap argument correct, and are the rows labelled correctly? Yes for exact values, with a MINOR numerical qualification.**

   If \(y_i=N_i/t\) exactly, every nonzero gap is \(|N_i-N_j|/t\ge1/t\), hence \(t\ge1/g_{\min}\). No search is needed. The project row correctly limits VERIFIED to matching values, non-integer intensities, and the search outcome; the acquisition-time exclusion remains HYPOTHESIS. [README.md:46](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:46), [README.md:49](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:49).

   **MINOR — distinguish exact quotients from rounded stored values.** For `[100000000, 100000001] / 10000`, float arithmetic gives `1/min_gap = 10000.000070722308`, slightly exceeding the actual `t = 10000`. For rounded quotients, use the gap plus the endpoints’ rounding uncertainties. Applying that correction to all committed VGDs leaves the reported precision unchanged: minimum whole-spectrum counting bound **435.038451815 seconds**, with maximum relative correction below **2.8×10⁻⁸**. This does not undermine the measurement, but qualifies “no tolerance” when applied to stored floats. [README.md:46](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:46), [noise_real_spectra.py:61](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_real_spectra.py:61).

3. **Do the tables and sentences match generated outputs? The numerical tables do, within displayed rounding.**

   Independently confirmed: `flat_ends` is closer to 1 in **16/20** case-levels; its range is **0.96724–1.15027**, versus **0.99567–1.19632** for `scaled_d4`; transmission shape spread is **1.63158**. These support the revised comparison and design summary. [README.md:137](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:137), [README.md:224](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:224).

   **MINOR — the MA3 sentence overgeneralises the diagnostic failure.** “They miss a 3-point moving average” should identify **`rho1_d4` specifically**. The measured lag-2 profile is **3.20**, so the diagnostics collectively are not unchanged. This still establishes no validated classification threshold. [README.md:157](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:157), [synthetic.txt:98](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/synthetic.txt:98).

4. **Does any sentence conclude more than supported? Minor carryovers remain.**

   **MINOR — propagate the heuristic wording throughout the unit.** Generated output still says “on a common grid: 0,” and a test docstring still claims the search finds the quantum “for any t.” Replace these with “no candidate accepted” and a statement limited to the tested cases. [noise_real_spectra.py:87](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_real_spectra.py:87), [real_spectra.txt:69](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/real_spectra.txt:69), [test_noise_estimators.py:74](/Users/skyefortier/xps-app/.claude/worktrees/noise/tests/test_noise_estimators.py:74).

   The principal design conclusions and frozen-residual reporting are appropriately qualified for this design-and-measurement scope. [README.md:216](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:216).

VERDICT: GO
