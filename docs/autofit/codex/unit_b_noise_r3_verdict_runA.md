**No BLOCKER findings; MAJOR findings remain.** Read-only verification: **27 tests passed**. The complete 14,040-spectrum benchmark and both real-data analyses reproduced their committed JSON/text/Markdown outputs exactly, using in-memory output capture. I analysed the committed fit records; I did not collect fresh refits.

**1. Is every round-2 finding resolved? No.**

Resolved:

- Per-file gap/counting-time bounds, with acquisition-time interpretation still labelled HYPOTHESIS: [README:46](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:46), [generator:95](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_real_spectra.py:95).
- VGD averaging citation and AIC/BIC numerical-floor qualification: [README:48](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:48), [README:37](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:37).
- All ten estimators in the generated synthetic tables and CPS at one second in the README: [synthetic_tables.md:3](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/synthetic_tables.md:3), [README:118](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:118).
- The `scaled_d1` exception and separate Gaussian levels for the constant estimators: [README:140](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:140).

Both specific round-2 quantum counterexamples now pass, and checking values fixes the original origin-check omission. However, the general quantum claim remains false. The estimator-selection conclusion is only partially corrected, as detailed below.

**2. Is `common_quantum` correct as stated? No.**

**MAJOR — valid counts/time data can still return `None`, within the divisor bound.**

Reproduced:

```python
counts = np.array([1000, 203000, 345000, 100000000, 100000001])
common_quantum(counts / 10000.0)
# None
```

The true quantum is **0.0001**, and the smallest count difference is **m = 1**. The computed smallest gap is `9.999999929277692e-05`. Initial rounding assigns the two largest values counts one higher than their true counts; refinement does not recover the correct assignments.

Least squares fixes an inaccurate quantum **conditional on correct integer assignments**. The current assignment/refinement loop does not exhaust the possible assignments, so `None` cannot certify “no quantum ≥ g/max_divisor.” [noise_estimators.py:201](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_estimators.py:201), [noise_estimators.py:209](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_estimators.py:209).

**MAJOR — acceptance also exceeds the stated rounding tolerance.**

The implementation uses:

```python
allowed = 2 * ulp + abs(n) * 4 * np.spacing(u)
```

That is not the stated half-ulp input bound plus rounding of `u`. [noise_estimators.py:198](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_estimators.py:198), [noise_estimators.py:221](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_estimators.py:221).

For example:

```python
common_quantum(np.array([1.0, 2.0, 3.0 + 4e-15]))
# 1.0000000000000009
```

At the second value, the residual is **1.7764e-15**, versus **4.4409e-16** for half an ulp of the largest value plus half an ulp of `u` times its multiple. Exact rational interval checks found **no compatible grid for m ≤ 1000** under the stated half-ulp input uncertainty.

Thus the routine neither finds every admissible grid nor rejects every non-grid input at its stated precision. These counterexamples do **not** establish that any committed spectrum is gridded.

**3. Are VERIFIED claims justified, and do tables and sentences match outputs? Not entirely.**

The numerical tables reproduce and match the README within its displayed rounding. I also verified all 230 CPS sidecars, single-series VGDs, instrument/version strings, and the 70 exact project matches.

However, **“0 of 230 files and 0 of 166 project spectra lie on such a grid” remains stronger than established**. The verified result is that this implementation accepts none; the counterexample above prevents interpreting rejection as a certified exclusion. The corresponding VERIFIED labels need narrowing or a sound exclusion procedure. [README:46](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:46), [README:49](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:49).

**MINOR — stale test count:** the README says 24 tests; there are now 27 passing tests. [README:255](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:255).

**4. Does any sentence conclude more than the measurement supports? Yes.**

**MAJOR — the estimator-selection summary still contradicts measured results.**

- **“`scaled_d4` is the closest for independent scaled-Poisson noise” is not established by the stated metrics.** For CPS at 0.05 seconds, the aggregate median level ratio is **0.9898 for `flat_ends` versus 1.0454 for `scaled_d4`**, with shape spread **1 for both**. `flat_ends` also has the closer aggregate median level in the other four constant-scale independent Poisson/CPS/sweep cases. Naming level error and shape spread does not supply a ranking that selects `scaled_d4`. [README:221](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:221), [synthetic.txt:6](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/synthetic.txt:6), [synthetic.txt:11](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/synthetic.txt:11).

- **“Both with the right shape” incorrectly includes transmission.** That case has variance `s/T(x)`, so one constant `k` cannot represent its shape. Both estimators have measured shape spread **1.63158**, not 1. Separate this case from constant-scale Poisson noise. [README:137](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:137), [benchmark:76](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_synthetic_benchmark.py:76), [synthetic.txt:138](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/synthetic.txt:138).

- **“The data’s correlation decides between the difference family and `flat_ends`” remains unchanged**, despite round 2 identifying it. Selection also depends on the variance law and signal/end curvature; the diagnostics do not establish a selection rule. [README:152](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:152).

Part (d)’s frozen-residual reporting and explicitly hypothetical physical interpretations remain appropriately qualified. The required corrections concern quantisation certification and conclusions drawn from the synthetic measurements.

VERDICT: NO-GO.
