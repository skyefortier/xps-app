The revision resolves most round-1 findings, but **three MAJOR findings remain**. No BLOCKER found.

Read-only verification: **24 tests passed**. All synthetic JSON/text/Markdown outputs and both real-data JSON/text reports reproduced exactly. I checked the committed fit collection; I did not collect new browser refits.

1. **Is every round-1 finding resolved? No.**

The covariance/σ correction, project-provenance qualification, `varmean` conditioning fix, `flat_ends` correlation limitation, added estimators, interpolation geometry, direct variance metrics, and paired window/spectrum reporting are substantially resolved. The code now bins `varmean` using independent outside samples, and its large-sample regression test passes. The analytic MA5 endpoint bias is **0.69664**, matching the revised description. [README:24](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:24), [noise_estimators.py:106](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_estimators.py:106), [README:79](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:79), [README:201](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:201).

Quantisation and performance-summary claims remain unresolved, as detailed below. The VGD averaging citation also remains incorrect.

2. **Are every VERIFIED claim and hypothesis label justified? No.**

**MAJOR — `common_quantum` can still reject exact counts/time data.** The divisor argument is valid in exact arithmetic, but the implementation treats the rounded smallest gap as exact. Its error is amplified by the ratio of a larger gap to that smallest gap. This reproducible counterexample returns `None`:

```python
counts = np.array([1000, 123456, 200000, 500000, 5800000, 5800001])
common_quantum(counts / 50.0)
```

The true quantum is **0.02**, the smallest count difference is **1**, and intensities span **20–116,000.02 CPS**, within the committed data’s intensity range. The largest gap-ratio error is approximately **0.001080**, exceeding `tol=0.001`. Thus enumerating all divisors does not establish the claimed exclusion under floating-point arithmetic. The reproduced **0/230 and 0/166** results establish what this implementation returned; they do not yet certify the stronger arithmetic claim. Account for uncertainty in the candidate spacing and add this counterexample, or narrow the claim. [noise_estimators.py:192](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_estimators.py:192), [README:46](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:46).

The positive result also checks a grid’s **gaps**, without checking its origin: `[0.2, 1.2, 2.2]` returns quantum `1`, although those values are not on `1·ℤ`. [noise_estimators.py:200](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_estimators.py:200).

**MINOR — the quoted gap and counting-time bounds use regional medians as file-wide bounds.** Actual per-file minimum gaps range from **0.0000165913 to 0.439042 CPS**, giving `1/g` from **2.28 to 60,273 seconds**, rather than the stated 20–1,700 seconds. The bound on acquisition time is appropriately labelled HYPOTHESIS, but these measured inputs need correction. [README:46](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:46), [real_spectra.json:158](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/real_spectra.json:158), [real_spectra.json:4712](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/real_spectra.json:4712).

**MINOR — the averaging citation is still off by one.** Averaging occurs at **line 98**, not line 97. The underlying claim is correct. [README:48](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:48), [vgd_parser.py:98](/Users/skyefortier/xps-app/.claude/worktrees/noise/vgd_parser.py:98).

The other principal VERIFIED implementation/provenance claims check out, including the 230 CPS sidecars, single-series VGDs, instrument/version strings, and 70 exact project matches.

3. **Are the mathematics, true variances, tables, and sentences correct? Mostly; the quantum exception and summary contradictions prevent acceptance.**

The difference norms **2, 6, 70**, white-noise correlations, Gaussian MAD normalization, revised `varmean` indexing, and constant fourth-difference estimator are correct under their stated assumptions. The lag-two noise formula matches the [published DER_SNR formula](https://archive.stsci.edu/vodocs/der_snr.pdf). [noise_estimators.py:31](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_estimators.py:31), [noise_estimators.py:87](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_estimators.py:87).

All benchmark true variances are correct, including retained smoothing samples and alternating original/midpoint variances. Independent matrix propagation reproduced those means and variances to floating-point precision. Evaluating variance error at the true signal addresses the earlier metric confounding. [noise_synthetic_benchmark.py:59](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_synthetic_benchmark.py:59), [noise_synthetic_benchmark.py:130](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_synthetic_benchmark.py:130).

**MAJOR — “every lag-1 difference estimator underestimates” remains false.** At the highest level, `scaled_d1` has median variance ratios **4.53 for MA3**, **6.61 for MA5**, and **4.46 for SG7**—substantial overestimation. Restrict the statement to the estimators actually supported by the measurements. [README:141](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:141), [synthetic.txt:104](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/synthetic.txt:104), [synthetic.txt:116](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/synthetic.txt:116), [synthetic.txt:128](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/synthetic.txt:128).

**MINOR — table coverage is overstated.** Displayed numerical cells match the generated outputs, but “all 8 estimators” means eight selected estimators out of **ten**; `scaled_d1` and `constant_d2` are omitted. The README table also omits CPS at one second, although the generated table includes it. [README:112](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:112), [noise_estimators.py:153](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_estimators.py:153), [synthetic_tables.md:6](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/synthetic_tables.md:6).

4. **Does any sentence conclude more than the measurement supports? Yes.**

**MAJOR — “`scaled_d4` is the best for independent noise” ignores the variance law.** Independent Gaussian noise is already a counterexample in this benchmark: `scaled_d4` has median level ratio **0.89** and shape spread **3.93**, whereas `constant_d4` gives **1.06** and **1.00**. Independence alone cannot select a scaled-Poisson model, and correlation alone cannot decide between the difference family and `flat_ends`. Qualify the conclusion by variance family and an explicit comparison metric. [README:147](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:147), [README:216](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:216), [synthetic.txt:40](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/synthetic.txt:40), [synthetic.txt:47](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/synthetic.txt:47).

Part (d)’s paired comparisons and explicit physical HYPOTHESIS labels now address the principal round-1 overclaims. Frozen-residual diagnostics are also correctly distinguished from changing fitting weights.

**MINOR — the AIC/BIC scaling statement still needs the numerical-floor qualification.** The shift is `−n log k` only while neither evaluation reaches the implemented χ² floor. [README:34](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:34), [fitting.py:3388](/Users/skyefortier/xps-app/.claude/worktrees/noise/fitting.py:3388).

**VERDICT: NO-GO.**
