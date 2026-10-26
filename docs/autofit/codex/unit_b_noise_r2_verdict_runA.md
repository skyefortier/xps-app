The measurements reproduce, but the quantisation test and several conclusions still need correction. **No BLOCKER findings; MAJOR findings remain.**

Read-only verification: **24 tests passed**. The full **14,040-spectrum benchmark**, real-spectrum analysis, and saved-fit analysis reproduced their committed JSON/text/Markdown outputs exactly. I analysed the committed fit collection; I did not collect fresh browser refits.

**1. Is every round-1 finding resolved? No.**

Resolved: covariance versus σ scaling; project provenance; `varmean`’s original conditioning bias; `flat_ends`’ correlation qualification; both additional estimators; actual upsampling; separate variance-error and plug-in metrics; paired window/spectrum reporting; and the distinction between frozen-residual diagnostics and changed fitting weights. See [README:24](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:24), [noise_estimators.py:96](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_estimators.py:96), [benchmark:87](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_synthetic_benchmark.py:87), and [README:201](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:201).

**MAJOR — quantisation remains unresolved numerically.** Enumerating the smallest gap’s divisors is exhaustive within the stated bound **in exact arithmetic**. The implementation fixes each candidate to a rounded subtraction, then amplifies that subtraction’s error when dividing larger gaps. This reproducible counterexample returns `None`:

```python
common_quantum(
    np.array([1000, 203000, 345000, 5500000, 5500001]) / 50.0
)
```

These are integer counts divided by **50 s**, with true quantum **0.02** and smallest count difference **m = 1**. The computed smallest gap is `0.020000000004074536`; the largest gap’s integer residual becomes approximately **0.00105021**, exceeding `tol=0.001`. Intensities remain within the committed data’s overall range.

Thus the five passing counting-time examples do not establish the claimed exclusion. Account for propagated rounding uncertainty when rejecting candidates, or narrow the claim to “no candidate accepted by this routine.” This does **not** establish that any committed spectrum is gridded. [noise_estimators.py:192](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_estimators.py:192), [tests:72](/Users/skyefortier/xps-app/.claude/worktrees/noise/tests/test_noise_estimators.py:72), [README:46](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:46).

The routine also checks gaps only: a positive result establishes an **offset lattice**, not necessarily the claimed zero-origin lattice `u·ℤ`.

**2. Are all VERIFIED claims and hypothesis labels correct? No.**

The principal application claims check out. All 230 sidecars identify CPS; all 230 files contain one series and the stated instrument/software strings. The 70 exact project matches reproduce, and the remaining provenance and acquisition-time assumptions are appropriately labelled HYPOTHESIS.

Beyond the quantisation issue:

- **MINOR — regional medians are presented as file-level bounds.** The quoted smallest gaps, **0.0006–0.05 CPS**, are rounded regional medians. Actual file extrema are approximately **0.00001659–0.43904 CPS**, giving reciprocal bounds **2.28–60,273 s**, not **20–1,700 s**. The finer-than-tested-grid argument still implies long counting times, but its supporting numbers need correction. [README:46](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:46), [real_spectra.json:158](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/real_spectra.json:158), [real_spectra.json:4712](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/real_spectra.json:4712).
- **MINOR — the averaging citation remains wrong.** The mean occurs at **line 98**, not line 97. This round-1 citation finding was not fixed. [README:48](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:48), [vgd_parser.py:98](/Users/skyefortier/xps-app/.claude/worktrees/noise/vgd_parser.py:98).
- **MINOR — AIC/BIC scaling needs the numerical-floor qualification.** The stated `−n log k` shift applies away from the implemented χ² floor. [README:37](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:37), [fitting.py:3388](/Users/skyefortier/xps-app/.claude/worktrees/noise/fitting.py:3388).

**3. Are the mathematics, true variances, and tables right? Mostly; the quantum exception is material.**

The difference-filter norms, Gaussian MAD factor, white-noise correlations, constant fourth-difference estimator, and revised regression arithmetic check out. Moving the regression’s binning samples outside each difference removes the identified same-noise conditioning mechanism for independent samples; it remains a heuristic estimator. I independently obtained **0.6966377** for the stated MA5 endpoint detrending bias. [noise_estimators.py:33](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_estimators.py:33), [noise_estimators.py:106](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_estimators.py:106), [noise_estimators.py:137](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_estimators.py:137).

The DER_SNR noise formula matches the [published algorithm](https://archive.stsci.edu/vodocs/der_snr.pdf). [noise_estimators.py:87](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_estimators.py:87).

All 13 implemented noise models’ true marginal variances are correct, including squared smoothing coefficients, retained-edge handling, and alternating upsampling variances. The revised level/spread metrics correctly separate variance-model error from observed-intensity weighting. [benchmark:59](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_synthetic_benchmark.py:59), [benchmark:129](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_synthetic_benchmark.py:129).

The displayed table cells match generated outputs within rounding. **MINOR:** “all 8 estimators” is inaccurate: ten are benchmarked, while the Markdown tables omit `scaled_d1` and `constant_d2`. [README:112](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:112), [benchmark:190](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_synthetic_benchmark.py:190).

**4. Does any sentence conclude more than the measurement supports? Yes.**

**MAJOR — the revised estimator conclusions still overgeneralise.**

- “Every lag-1 difference estimator underestimates” is false for `scaled_d1`. Its highest-level median variance ratios are **4.53 for MA3, 6.61 for MA5, 4.46 for SG7, 4.36 for the half-bin shift, and 1.22 for upsampling**. Restrict the sentence to the measured second/fourth-difference estimators. [README:141](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:141), [synthetic.txt:104](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/synthetic.txt:104), [synthetic.txt:116](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/synthetic.txt:116).
- “`scaled_d4` is the best for independent noise” is too broad. Gaussian constant noise is independent: `scaled_d4` has shape spread **3.93**, versus **1** for `constant_d4`, whose level error is approximately **1.05–1.07**. Independence alone cannot select the variance model. Narrow the recommendation to the appropriate intensity-dependent noise family and define “best.” [README:216](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:216), [synthetic.txt:38](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/synthetic.txt:38).
- “The constant estimators get its level” also overstates the Gaussian results: `constant_d2` gives **1.25–1.28**, and DER_SNR **1.60–1.63**. The favourable level claim belongs specifically to `constant_d4`. [README:139](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:139), [synthetic.txt:39](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/synthetic.txt:39).

Part (d)’s revised physical interpretations and paired-fit reporting are substantially improved and appropriately qualified. The remaining major problems concern the quantisation exclusion and the synthetic-to-design conclusions.

VERDICT: NO-GO.
