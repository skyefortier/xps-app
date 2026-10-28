# Unit B — estimating a spectrum's noise from the data (design + measurement, 2026-10-26; revised after the round-1 design review; owner decisions and the counting-time step added 2026-10-27)

**Scope (owner, 2026-10-26):** design and measurement only. Nothing a user sees changes, no fitted number changes,
nothing is deployed. Whether and how the displayed χ²ᵣ changes is a separate decision after this review.

**Owner decisions, 2026-10-27:**
- **No change to the fitting weights.** §1a derives what a constant noise scale does and does not change, and measures it.
- **Next step, read-only:** decode the counting time from the files. That is [counting-time.md](counting-time.md).
  Within the tested ranges (any common T up to each acquisition's own length, and every c × scans × dwell with
  c ≤ 1024), under the stated error model, no common counting time makes the stored values whole counts. So σ = √N
  is not recoverable from these files. (Round 2: the bounds are essential. Every stored float is a dyadic rational,
  so some enormous T always makes a file's values whole numbers.)
- **Proposed wording for the displayed χ²ᵣ** is in §8, for approval. It is not implemented.

**Correction, 2026-10-27:** §2 and §5 read 230 of the 275 committed VGDs. The other 45, in
`9 UCl4-graphite 4%, no kapton …/`, were outside the glob `test_data/*.DATA/*.VGD`. The counting-time step reads all
275; its per-region k agree with §5's medians ([counting-time.md](counting-time.md) §5). Seven of the 45 sidecars
title the intensity axis `Counts`, not `Counts / s`, although their values are non-integer at every point
([counting-time.md](counting-time.md) §1), so §2's "Counts / s" row holds for the 230 files it read.

**The question:** the displayed χ²ᵣ should be about 1 for a fit that explains the data down to the noise. It can be
only if the variance it divides by is the data's real noise. Can that variance be estimated from each spectrum
itself, independent of any fit model?

Every claim about the current code or the data is labelled **VERIFIED** (file:line or a committed output, read on
main at a192f78) or **HYPOTHESIS**. Every number comes from a committed generator (end of this file) and its output
in this folder; where the round-1 design review corrected the first version, the correction is marked "round 1".

---

## 1. What the fit assumes today, and what a noise scale would and would not change

- **VERIFIED** — the server weights each point by w_i = 1/√max(y_i, 1), y in the file's own units, before
  background subtraction (`fitting.py:3006-3007`; the comment `fitting.py:3002-3005` calls it Poisson); the
  verifier recomputes the same (`fitting.py:3821`). The reported χ²ᵣ = Σ((y_sub − fitted_sub)·w)² / max(1, n − n_free)
  (`fitting.py:3384-3387`); recomputed from the residuals of the 121 committed fits in §5 it agrees to 1.8e-15.
- **VERIFIED** — the local engine and the page's support twin use the same weights (`templates/index.html:8214`,
  `:10759`; the record names the objective `poisson_weighted_chi_square`, `:7388`, `:7399`).
- **VERIFIED** — lmfit multiplies the parameters' COVARIANCE by χ²ᵣ, so each σ by √χ²ᵣ (round 1: "σ by χ²ᵣ" was
  wrong): `Model.fit` defaults to `scale_covar=True` (`venv/.../lmfit/model.py:1034`; the scaling at
  `lmfit/minimizer.py:812-813`), and `fitting.py` never passes it (each `model.fit(...)`, e.g. `fitting.py:2198`,
  `:2209`, `:2246`, `:2283`). The support statistic is a ratio of χ² differences (`fitting.py:2697-2712`).

Two uses of a noise estimate must be kept apart (round 1):

1. **A diagnostic on frozen residuals** — the fit unchanged, its χ²ᵣ recomputed under another variance model.
   Changes no fitted number whatever the model's shape; §5 does exactly this. For a scaled-Poisson model
   (v = k·max(y, 1)) it is the displayed χ²ᵣ / k.
2. **New fitting weights.** If the new variance is the current one times ONE positive constant k, the objective is
   divided by k: its minimiser is mathematically unchanged, lmfit's covariance scaling cancels k (so the σ are
   unchanged at that solution), the support F is unchanged; the raw χ² and Δχ² scale by 1/k and the current AIC /
   BIC shift by −n·log k (while χ² stays above its numerical floor, `fitting.py:3388`); a numerical optimiser's path is not guaranteed bit-identical. A variance of any other
   relative shape (a constant term, per-point factors) changes the objective and can change fitted parameters;
   correlated noise needs a covariance matrix, not different diagonal weights.

### 1a. One constant on every σ — derivation and measurement (owner 2026-10-27: no change to the fitting weights)

Write the fit's objective as χ²(θ) = Σᵢ rᵢ(θ)² / σᵢ², where rᵢ = y_sub,i − fᵢ(θ) and σᵢ = √max(yᵢ, 1)
(`fitting.py:3006-3007`). Replace every σᵢ by s·σᵢ, i.e. multiply every variance by k = s². Then:

1. **The objective.** χ²_s(θ) = χ²(θ) / k for every θ. This is an identity, not an approximation.
2. **The fitted parameters.** Dividing by a positive constant preserves order. So the minimiser, every local minimum
   and its basin, and every comparison of χ² values on the same data are unchanged. The comparisons in `run_fit` are
   all of this kind:
   - the perturbed restarts' ranking (`fitting.py:3157-3167`);
   - the "lower χ² wins" competitions for differential evolution and basinhopping (`fitting.py:2254`, `:2304`);
   - the scattered starts' "lower by more than 0.1 %" (`fitting.py:2545`, `:2658`, relative);
   - the certificate's relative improvement against ftol (`fitting.py:2370-2371`).
3. **χ² and χ²ᵣ.** Both are divided by k. The displayed χ²ᵣ is the only number a student sees change.
4. **Parameter uncertainties.**
   - The Gauss–Newton covariance at the minimum is C = (Jᵀ W J)⁻¹ with W = diag(1/σᵢ²). With W_s = W/k,
     C_s = k·C. lmfit then multiplies by χ²ᵣ (`scale_covar=True`, its default; `fitting.py` never sets it —
     `lmfit/model.py:1034`, `lmfit/minimizer.py:812-813`). So C_s · χ²ᵣ,s = k·C · χ²ᵣ / k = C · χ²ᵣ. **The reported
     σ are independent of the noise scale**, because they are scaled to the fit's own residual scatter.
   - What they mean: with variance k·σᵢ² as the true noise, the uncertainty from the noise alone is
     σ_reported / √(χ²ᵣ / k). Where the fit leaves more than the noise (χ²ᵣ / k > 1), the reported σ are larger than
     noise-only σ: misfit is counted as if it were noise. Where it leaves less, they are smaller. Without
     `scale_covar` they would scale with s.
   - The page's uncertainty rules read these σ, so they are unchanged too.
5. **The support and required-component F tests.** F = (Δχ²/p) / (χ²/dof) divides two χ² quantities, so it is
   invariant (`fitting.py:2697-2712`, `:2760-2777`). So is the page's twin, the Auto-Fit anchor check. This is why
   the design rule prefers it: it estimates the common scale from the residuals rather than assuming it.
6. **AIC / BIC as reported.**
   - The response's `aic` / `bic` use lmfit's form, n·ln(χ²/n) + 2p (or p·ln n) (`fitting.py:3389-3398`). The page
     does not display them (VERIFIED: no "aic" / "bic" in `templates/index.html`).
   - Under σ → s·σ every model fitted to the same n points shifts by the same −n·ln k. So **ΔAIC and ΔBIC between
     models are invariant**: this form profiles out an unknown common scale, as the F test does.
   - Find Peaks' (archived) BIC* uses the same form (`autofit/engine.py:1579-1584`, `autofit/criteria.py:50-57`), so
     its ranking is invariant.
   - The known-noise forms, AIC = χ² + 2p and BIC = χ² + p·ln n, are NOT invariant: Δχ² scales by 1/k while the
     penalty does not. So the preferred model would depend on the assumed noise scale. The same holds for a χ²
     difference judged against a χ²_p distribution. Neither form is used by the app.
7. **The numerical path.** The identity holds in exact arithmetic. An optimiser's stopping rules are another matter:
   a rule stated in χ² units does not scale.
   - **Scale-free:** Levenberg–Marquardt (MINPACK: relative ftol and xtol; gtol a cosine), Trust-Region's ftol and
     xtol (`scipy/optimize/_lsq/common.py:705-707`), and differential evolution's convergence test (relative,
     atol = 0: `scipy/optimize/_differentialevolution.py:1181-1183`).
   - **Absolute in χ² units:**
     - Trust-Region's gtol, on the scaled gradient (`_lsq/trf.py:265-266`).
     - Nelder–Mead's fatol = 1e-4 (`scipy/optimize/_optimize.py:868-869`).
     - basinhopping's Metropolis temperature T = 1.0 (`lmfit/minimizer.py:1758`).
   - `fitting.py` passes none of these (VERIFIED: no `gtol` / `fatol` / `T=` in it), so the defaults apply. A
     power-of-two s makes every scaled operation exact, so only an absolute rule can make the path differ. Any other
     s also rounds differently.

**Measured** (`scripts/noise_sigma_scale_check.py`, `sigma_scale.txt`). `run_fit` is run unchanged except for its one
σ line, multiplied by s, on the 202 committed fit targets, with the page's 3 perturbed restarts. Each fit at s is
compared with the fit at s = 1 by the app's own same-fit rule (`same_fit.fit_differences`), after its χ²-valued
fields are put back on the s = 1 scale. A second s = 1 run measures each method's run-to-run floor.

SIGMA_SCALE_TABLE

**So:** a constant noise scale is a statement about the displayed χ²ᵣ alone. Dividing the displayed χ²ᵣ by an
estimated k is the same number a refit with σ × √k would report, and no fitted parameter, uncertainty, support or
required verdict would move beyond the measured run-to-run floor.

## 2. What the data are (part a)

| source | what the intensities are | label | evidence |
|---|---|---|---|
| Thermo Avantage `.vgd` (all 230 committed raw files) | **counts per second** | VERIFIED | each file's chart sidecar `.xml` titles the intensity axis `Counts / s` (e.g. `docs/autofit/test_data/1 UCl4-graphite …DATA/C1s Scan.xml`); at least 99.8 % of every file's stored values are non-integer (`real_spectra.txt`). The instrument is a Nexsa G2, Avantage v6.7.0 (strings in the files' main property stream) |
| the same — raw counts divided by a per-point counting time t? | **not established either way** (round 4) | VERIFIED (the bound), HYPOTHESIS (whether the acquisition allows it) | were the values counts / t, all would be multiples of 1/t, so every gap would be at least 1/t: **t ≥ 1/(smallest gap)**, no search needed; for stored (rounded) values the gap is taken plus its endpoints' rounding (round 4). That gives t ≥ 2.3–60 000 s per point (median 99 s; smallest gaps 1.7e-5–0.44 CPS; `real_spectra.txt`). Whether such counting times are possible depends on the acquisition model, which is not established here: counted point by point, every whole spectrum would need at least 435 s, against about a minute (the files' start/end timestamps, in undocumented property ids); but the Nexsa G2's detector is multichannel (HYPOTHESIS: 128 channels collecting several energies at once, per Thermo's Nexsa G2 datasheet and application note 31009 as cited by the round-4 review; not checked here), and under assumed full 128-fold parallelism the calculated LOWER BOUNDS fall below 120 s for 99 of the 230 files (below 60 s for 68) — for those the bound does not exclude counts / t, and whether their actual acquisitions are compatible is not established (round 5). Supporting only: the heuristic search `noise_estimators.common_quantum` (divisors m ≤ 1000 of the smallest gap, least-squares refinement, values checked against 2 ulps + 4 ulps of u per multiple) finds the quantum in every tested counts / t case and refuses an incommensurate offset lattice, and accepts no candidate in any of the 230 files or 166 project spectra; it is not complete (round 3 found grids it misses) and its tolerance admits near-grids |
| what Avantage did between counting and the stored CPS | unknown | HYPOTHESIS | a continuous correction (detector efficiency, dead time, transmission) would explain the absence of any grid; not established. 2026-10-27: the dwell, scans, pass energy and start / end are now decoded ([counting-time.md](counting-time.md) §1). An EXACT test excludes every common counting time up to each acquisition's own length, and every c × scans × dwell with c ≤ 1024, in all 275 files (§2 there). Every file records that a detector-signature correction and a TXFN correction were set (`SignatureCorrected`, `Acq_TXFN_Correction`, and coefficient counts; two unnamed blocks are HYPOTHESIS their coefficients); how they are computed, and whether they are what removes a lattice, is not in the files |
| the app's VGD reader | returns the stored values unchanged; a multi-scan ("overlay") file becomes the **per-point mean of its scans** | VERIFIED | `vgd_parser.py:95-98` (the mean at `:98`; round 2: the line was off by one); the page always parses VGDs on the server (`templates/index.html:4032`, `:5404` → `app.py:1022`); its heuristic `parseVGD` (`templates/index.html:5322`) has no caller. All 230 committed VGDs hold one series, so the mean never applies to them |
| committed projects (`*.proj.zip`, 166 spectra) | 70 are, value for value, a committed VGD's intensities; all 166 are non-integer, and the search above accepts no grid in any | VERIFIED (the 70; non-integer; the search's outcome) / HYPOTHESIS (that the other 96 are the same Avantage CPS — their tab names are VGD scan names) | `real_spectra.json` → `projects` (round 1: "all 166 are the same CPS" was not established) |
| `.csv` / `.tsv` / `.txt` / `.xy` / `.xlsx` | **unknown to the app**: whatever the exporting program wrote (counts, CPS, normalised, smoothed) | VERIFIED (that it is not known) | `parser.py:47` ("intensity (counts or CPS)"); no unit is read or stored |
| the page's smoothing | display only — it never reaches a fit | VERIFIED | `savitzkyGolay` has one caller, the "Smoothed" chart overlay (`templates/index.html:12958-12969`) |

**Where Poisson holds.** For RAW COUNTS — integers from counting, including sums of independent counting
acquisitions (still Poisson) — the variance equals the EXPECTED count; σ = √y is its plug-in from the observed count,
biased at low counts (round 1: "exact" was too strong). Counts divided by a counting time t have variance s/t
(k = 1/t); the mean of m sweeps s/m; after a smooth per-point correction factor T, s/T (k varies across the
window); after smoothing or interpolation neighbouring points are correlated and no per-point σ describes the
noise fully (a χ² with the true marginal variances still has expectation n but is not χ²-distributed, and a fitted
residual's calibration by n − p is not guaranteed). **None of the committed data are raw counts**, so σ = √y in
their units has no derivation; how close it happens to be is what §5 measures.

## 3. Candidate estimators (part b) — `scripts/noise_estimators.py`

All read only the intensities, in point order, and return a variance model v(y) = a + k·y. Common to all: MAD → σ
uses the Gaussian consistency factor 1.4826 (Gaussian-consistent, not variance-consistent for every distribution);
the points on a peak's flanks (where the SIGNAL's difference is large) are meant to fall outside the MAD, which works
only while signal-free differences are the majority; normalising by the OBSERVED y (a random quantity) makes
numerator and denominator dependent at low counts; a short spectrum or discrete values can give a zero MAD — a zero
variance, counted as a failure in §4.

| estimator | model | assumes | fails when (measured in §4) |
|---|---|---|---|
| `poisson_file_units` (today) | v = y (k = 1) | the file holds raw counts | any other unit, by exactly the unit's factor |
| `scaled_d1`, `scaled_d2`, `scaled_d4` | v = k·y, k = (robust σ of the 1st / 2nd / 4th binomial difference normalised by √(Σ c_j² max(y_{i+j}, 1)))²; squared filter norms 2, 6, 70 | scaled Poisson; neighbouring points independent; the signal's difference small at most points (an order-N difference annihilates polynomials of degree below N) | **correlated neighbours** (smoothing, interpolation): differences cancel correlated noise — k underestimated, more for higher orders; **high counts with peaks**: the signal's difference inflates k, more for lower orders |
| `scaled_d2_lag3` | the same with points 3 apart | correlation shorter than 3 points | the signal's curvature over 6 points inflates k strongly at high counts |
| `constant_d2`, `constant_d4` | v = a (one constant), from 2nd / 4th differences | noise independent of intensity | shot noise: the level right somewhere, the SHAPE wrong across the window |
| `der_snr` (Stoehr et al. 2008) | v = a from median\|2y_i − y_{i−2} − y_{i+2}\| (lag 2, the median of the absolute value, as published) | constant noise; points two apart independent | shot noise (shape); the signal's curvature at lag 2 at high counts |
| `varmean` | v = a + k·y: binned robust variances of 2nd differences against a local mean, weighted LSQ with a, k ≥ 0 | independent points; a spread of intensities | high counts with peaks (the peak bins' variance is inflated by the signal); a narrow intensity range confounds a and k. **Round 1:** the first version binned by a mean made of the difference's own points, which selects on the noise (covariance −v with the difference: the variance falls from 6v towards 4v, i.e. to ~⅔); it now bins by the points just outside, y_{i−2} and y_{i+2} (`test_the_regression_does_not_select_on_the_noise`). Its weights are a heuristic |
| `flat_ends` | v = k·y from the variance about a straight line on each end's 10 % | ends with no peak and no curvature; independent points | an end on a peak, step or curvature (a survey window: k ≈ 31, §5); **correlated noise** (round 1): removing a fitted line also removes part of it — for a 24-point end with 5-point moving-average noise the expected variance is ≈ 0.70 of the true |

**Correlation diagnostics** (not estimators), `correlation_diagnostics`: the lag-1 correlation of the normalised 1st
and 4th differences (for independent noise of constant variance −0.5 and −0.8, `WHITE_RHO1`; approximate after the
normalisation and the outlier clipping), and the lag profile k(lag L)/k(lag 1) of 2nd differences (flat for
independent noise until the signal's curvature lifts it). On the synthetic set (`synthetic.txt`): the 1st-difference
reading is moved by the signal from −0.5 to −0.29…+0.51 even for independent noise; the 4th-difference reading stays
at −0.76…−0.79 for every independent case, moves to −0.34…−0.69 for 5–7-point smoothing, the half-bin shift and
upsampling, and does NOT move for a 3-point moving average (−0.82) — smoothing need not move it up (round 1; the lag
profile does move for it, 3.20 at lag 2 — round 4). The
lag profile at lag 2 is 1.09–1.51 for the independent cases and 2.87–4.20 for the smoothed and shifted ones (the
upsampled case gives none: its second differences have a zero MAD). Evidence only, not a test with a threshold, and
the synthetic correlation families are few.

## 4. Ground truth: synthetic spectra with known noise (part c) — `synthetic.json`, `synthetic.txt`, `synthetic_tables.md`

`scripts/noise_synthetic_benchmark.py --seeds 30`: a C 1s-like window of 241 points (three GL peaks; widths of 3,
10 or 30 points; flat, sloped or Shirley-step background; tallest peak 300 to 3·10⁵ counts) under 13 noise models
whose per-point variance is known exactly: Poisson counts; CPS at counting times 0.05, 1 and 20 s; the mean of 10
sweeps; Gaussian constant; Poisson + constant; a ±30 % transmission factor; 3- and 5-point moving averages and a
7-point Savitzky-Golay (the filter applied to truth and to the variance as h∗s and h²∗v; the truncated edges
dropped, so boundary handling is not benchmarked); a half-bin shift (adjacent means on the same grid — round 1: this
was mislabelled "interpolation"); and linear upsampling ×2 (the measured points kept, midpoints added: variances
alternate v_i and (v_i + v_{i+1})/4 — round 1). 13 × 9 shapes × 4 levels × 30 seeds = 14 040 spectra, each judged by
every estimator. No fit and no expert reference is used.

**Metrics (round 1).** The estimated model v̂ is evaluated at the TRUE signal, which isolates the estimation error:
the **level** error median(v̂(s)/σ²) and the **shape** error, the 90th / 10th-percentile spread of v̂(s)/σ² across the
window (1 is right for both). The χ²ᵣ of the true signal with the plug-in weights v̂(y) — what a fit weighted by the
observed intensity, as today, would show — is reported separately. The first version used only that, which
conflated the estimation error with the plug-in: at the lowest CPS level (15 counts at the peak) it read 7.5–8.8 for
the scaled estimators, where their level error is 0.97–1.11 and their χ²ᵣ with v̂(s) 0.87–1.01 (`synthetic.json`).

The level error by peak level (300 / 3·10³ / 3·10⁴ / 3·10⁵ counts), medians over 9 shapes × 30 seeds, from
`synthetic_tables.md` (all 10 estimators, with the shape spreads and plug-in χ²ᵣ, are there; 5–95 % ranges per
spectrum in `synthetic.json`):

| noise (truth) | today, v = y | `scaled_d4` | `scaled_d2` | `flat_ends` | `scaled_d2_lag3` | `der_snr` |
|---|---|---|---|---|---|---|
| Poisson counts | 1 / 1 / 1 / 1 | 1 / 1 / 1.1 / 1.1 | 1 / 1.1 / 1.3 / 1.5 | 0.97 / 1 / 1 / 1.1 | 1.2 / 1.5 / 1.9 / 3.1 | 1.2 / 1.3 / 1.5 / 2 |
| CPS, t = 1 s | 1 (all) | 1 / 1 / 1.1 / 1.1 | 1 / 1.1 / 1.2 / 1.5 | 0.99 / 0.99 / 0.98 / 1.1 | 1.2 / 1.5 / 2 / 3.1 | 1.2 / 1.2 / 1.5 / 2 |
| CPS, t = 0.05 s | 0.05 (all) | 1.1 / 1 / 1 / 1.1 | 1.1 / 1 / 1.1 / 1.2 | 0.97 / 1 / 0.98 / 1 | 1.1 / 1.1 / 1.4 / 1.7 | 1.1 / 1.1 / 1.2 / 1.5 |
| CPS, t = 20 s | 20 (all) | 1.1 / 1 / 1.1 / 1.2 | 1.1 / 1.3 / 1.6 / 2.1 | 0.98 / 1 / 1.1 / 1.2 | 1.6 / 2.1 / 4.2 / 17 | 1.4 / 1.7 / 2.3 / 5.6 |
| mean of 10 sweeps | 10 (all) | 1 / 1.1 / 1.1 / 1.1 | 1.1 / 1.2 / 1.5 / 1.9 | 0.99 / 0.99 / 1.1 / 1.1 | 1.5 / 1.9 / 3.1 / 11 | 1.3 / 1.5 / 2 / 4 |
| transmission ±30 % | 1 (all) | 1 / 1 / 1.1 / 1.1 | 1 / 1.1 / 1.2 / 1.5 | 1.1 / 1.1 / 1.1 / 1.2 | 1.2 / 1.5 / 2 / 3.1 | 1.2 / 1.3 / 1.6 / 2.1 |
| Poisson + constant | 0.92 / 0.52 / 0.098 / 0.011 | 1 / 0.97 / 0.87 / 0.89 | 1 / 1 / 0.99 / 0.98 | 1 / 1.2 / 1.3 / 1.3 | 1.3 / 1.5 / 1.7 / 1.7 | 1.2 / 1.3 / 1.3 / 1.4 |
| Gaussian constant | 68 / 6.8 / 0.68 / 0.068 | 0.88–0.91 | 1.2 | 1.3 | 1.9–2 | 1.6 |
| smoothed MA3 | 3 (all) | 0.21 / 0.22 / 0.23 / 0.23 | 0.24 / 0.28 / 0.35 / 0.46 | 0.81 / 0.79 / 0.87 / 1 | 1.4 / 1.7 / 2.3 / 5.2 | 0.72 / 0.82 / 1.1 / 1.7 |
| smoothed MA5 | 5 (all) | 0.12 / 0.12 / 0.13 / 0.14 | 0.15 / 0.18 / 0.25 / 0.34 | 0.65 / 0.61 / 0.73 / 0.82 | 0.74 / 0.95 / 1.6 / 5.5 | 0.36 / 0.45 / 0.61 / 1.5 |
| smoothed SG7 | 3 (all) | 0.11 / 0.11 / 0.12 / 0.13 | 0.16 / 0.19 / 0.23 / 0.3 | 0.78 / 0.82 / 0.85 / 0.96 | 1.3 / 1.6 / 2.2 / 5.5 | 0.61 / 0.7 / 0.92 / 1.6 |
| half-bin shift | 2 (all) | 0.21 / 0.21 / 0.22 / 0.23 | 0.36 / 0.39 / 0.49 / 0.6 | 0.91 / 0.88 / 0.95 / 1.1 | 1.3 / 1.6 / 2.1 / 4.3 | 1.2 / 1.3 / 1.7 / 2.3 |
| upsampled ×2 | 1 (all) | 0.033 / 0.036 / 0.045 / 0.054 | 0 (zero MAD) | 0.7 / 0.7 / 0.7 / 0.76 | 0.81 / 0.89 / 1.1 / 1.4 | 0.55 / 0.61 / 0.69 / 0.86 |

(For "today" under Gaussian noise the level error is the ratio of the counts to the constant variance, so it moves
with the level.)

What the measurement shows (per-level medians; individual spectra scatter around them):
- **Today's v = y** has a level error of exactly the unit's factor whenever the noise is scaled Poisson (×0.05 for
  CPS at 50 ms, ×20 at 20 s, ×10 for 10 averaged sweeps), and the wrong shape for constant noise.
- **Independent noise with ONE scale** (counts, CPS, sweeps: v = k·s): `scaled_d4` 1.0–1.2 and `flat_ends`
  0.97–1.15 at every level, both with the right shape (spread 1); `flat_ends`' median is the closer to 1 in 16 of
  these 20 case-levels (5 cases × 4 levels), `scaled_d4` needs no flat ends (round 3: the first ranking had no stated basis). **A per-point factor**
  (the ±30 % transmission case, v = s/T(x)) has no single k: every scaled estimator, these two included, keeps a
  shape error (spread 1.63) whatever its level (1.0–1.2). `scaled_d2`, `scaled_d2_lag3`, `der_snr` and `varmean` overestimate as the counts rise
  (the signal's differences; at the highest level 1.2–2.1, 1.7–17, 1.5–5.6 and 1.3–130).
- **Independent constant noise:** `constant_d4` gets its level (1.05–1.07) and shape (spread 1); `constant_d2`
  (1.25–1.28) and `der_snr` (1.60–1.63) get its shape but overestimate its level; every scaled estimator gets the
  wrong shape (spread 3.9), `scaled_d4` at a level of 0.88–0.91 (round 2: independence alone does not select the
  variance model). Under shot noise the reverse (the constant estimators' spread 3.5–3.9).
- **Correlated noise** (smoothing, the half-bin shift, upsampling): the 2nd- and 4th-difference estimators at lag 1,
  scaled and constant, underestimate the variance — `scaled_d4` by 4–30×, `scaled_d2` by 1.7× to failure (zero MAD on
  the upsampled grid), `constant_d4` by 4–20×; `scaled_d1` runs from below 1 at low counts to above 1 at high counts
  (0.29–6.6: the signal's first differences outgrow the noise's cancellation — round 2); `flat_ends`
  is biased low too (0.61–1.1, MA5 the worst) — less affected, not immune (round 1); `scaled_d2_lag3` and `der_snr`
  (lag > 1) range over 0.36–5.5, rising with the counts — near 1 only at some levels of some cases.
- **Low counts:** the plug-in χ²ᵣ (weights from the observed y) departs from the estimation error at 15 counts per
  point (above) — a property of plug-in weighting, not of the estimators.
- No estimator is right in every regime. Which one is right depends on the variance law (one scale, a per-point
  factor, a constant), the correlation, and the signal's structure at the ends and at high counts (round 3); the
  diagnostics of §3 bear only on the correlation, and incompletely (the 4th-difference correlation misses a 3-point
  moving average; the lag profile does not, but no rule on either is validated).

## 5. The committed real data (part d) — report only

### Whole spectra — `real_spectra.json`, `real_spectra.txt` (`scripts/noise_real_spectra.py`, all 230 VGDs)

Estimator outputs per region, median over the region's files [10–90 %]. k is the estimated factor in v = k·y (CPS
units); for the constant estimators a / median(y) is shown, to read on the same scale; `varmean`'s intercept
a / median(y) has median 0.000 in every region (90th percentile 0.04–0.40):

| region | files | step | rho1 d4 | lag profile | `scaled_d4` k | `scaled_d2` k | `flat_ends` k | `varmean` k | `der_snr` a/ỹ | `constant_d4` a/ỹ |
|---|---|---|---|---|---|---|---|---|---|---|
| B 1s | 50 | 0.1 eV | −0.78 | 1.00 1.38 1.71 2.22 | 0.73 [0.55, 0.88] | 0.85 [0.69, 1.14] | 1.12 [0.77, 4.61] | 0.96 [0.65, 1.40] | 0.98 | 0.71 |
| C 1s | 60 | 0.1 eV | −0.75 | 1.00 1.51 1.76 2.16 | 0.71 [0.54, 0.96] | 0.89 [0.67, 1.22] | 0.99 [0.65, 19.3] | 1.30 [0.54, 2.67] | 1.15 | 0.75 |
| N 1s | 40 | 0.1 eV | −0.78 | 1.00 1.46 1.72 2.30 | 0.62 [0.48, 0.82] | 0.88 [0.69, 1.13] | 0.94 [0.63, 1.45] | 1.33 [0.31, 3.14] | 1.19 | 0.71 |
| U 4f | 20 | 0.1 eV | −0.78 | 1.00 1.55 2.21 2.97 | 0.66 [0.54, 0.81] | 0.82 [0.63, 0.88] | 2.47 [0.95, 4.45] | 1.00 [0.46, 1.27] | 1.09 | 0.64 |
| Survey | 60 | 1.0 eV | −0.75 | 1.00 1.19 1.32 1.50 | 1.01 [0.91, 1.12] | 1.07 [0.96, 1.16] | 31.6 [21.0, 73.4] | 1.08 [0.97, 1.22] | 0.86 | 0.67 |

Set beside §4 — comparisons, with interpretations labelled (round 1: the first version stated them as facts):
- The core levels' 4th-difference correlation (−0.75…−0.78) equals the synthetic independent cases' (−0.76…−0.79);
  their lag profiles at lag 2 (1.38–1.55) are at or just above the top of the synthetic independent range
  (1.09–1.51) and below the smoothed and shifted ones (2.87–4.20). The 4th-difference reading cannot rule out a 3-point moving average (§3); the lag profiles sit well below
  the one it gives (3.20 at lag 2).
- On B 1s, C 1s and N 1s (whose `flat_ends` medians are stable; their 90th percentiles reach 1.4–19) `flat_ends`
  reads 1.4–1.5× `scaled_d4`; on the synthetic set that ratio is ≈ 0.9–1.1 for independent one-scale (scaled-Poisson) noise (≈ 1.4–1.5 for constant noise), 3.8–7.4 for the
  smoothed and shifted cases and 14–21 upsampled.
- HYPOTHESIS: the noise of these files is nearly independent between neighbouring points, with an estimated k of
  0.6–1.0 by `scaled_d4` (one of the two that work for independent one-scale noise in §4) and 0.9–1.1 by `flat_ends` where its ends
  behave; a mild correlation or imperfectly flat ends would explain the gap between them, and these measurements do
  not separate the two.
- HYPOTHESIS: an estimated k of order 1 in CPS units means today's weighting happens to be near this data's noise —
  an accident of the acquisition (§2: the stored values are CPS, not counts), not a derivation.
- The earlier flat-end measurement on the C 1s scans (dispersion 0.4–1.2 × the mean;
  `docs/findings/find-peaks-scale/README.md` §2, on branch `fix-occupancy-f-test`) is of the same order.

### Existing fits — `real_fits.json`, `real_fits.txt` (`scripts/noise_real_fits.py`)

Each committed tab's own saved model refitted by the current server through the page (Run Fit: 121 of 121
converged), and the χ²ᵣ of the SAME residuals under each estimate (a diagnostic, use 1 of §1), estimated from the
fit window and from the whole spectrum:

| variance used | window: median [10–90 %] | whole spectrum: median [10–90 %] |
|---|---|---|
| today, v = y (displayed) | 2.44 [1.74, 17.5] | — |
| `scaled_d4` | 3.75 [2.40, 22.1] | 3.75 [2.41, 23.9] |
| `scaled_d2` | 3.18 [1.71, 15.9] | 3.19 [1.74, 18.8] |
| `flat_ends` | 2.81 [1.58, 8.43] | 2.74 [1.56, 6.20] |
| `varmean` | 2.60 [0.76, 11.3] | 2.60 [0.81, 13.4] |
| `scaled_d2_lag3` | 1.65 [0.84, 7.36] | 1.64 [0.95, 8.60] |
| `der_snr` | 2.79 [1.70, 23.6] | 2.72 [1.80, 25.0] |
| `constant_d2` | 4.26 [2.54, 33.1] | 4.25 [2.59, 37.7] |
| `constant_d4` | 4.56 [2.88, 43.3] | 4.55 [2.92, 46.0] |

Window and whole spectrum, PER FIT (round 1: the first version said they "agree"): the ratio of the two χ²ᵣ has a
median of 0.99–1.00 for every estimator, but 10–90 % ranges up to 0.72–1.06 (`varmean`), 0.74–1.01
(`scaled_d2_lag3`) and 0.90–1.63 (`flat_ends`), and extremes of 2–10× (e.g. `flat_ends` 46.5 against 4.4 on 4-GTA
UCl4-BN / B1s Scan_6).

By region (window; displayed | `scaled_d4` | `flat_ends`): B 1s (20) 9.95 | 9.83 | 9.61; C 1s (44) 2.34 | 3.88 | 3.16;
Cl 2p (3) 3.28 | 5.25 | 2.93; U 4f (54) 2.38 | 3.64 | 2.43. Under every estimate most committed fits sit above 1.
**Reported, not concluded:** above 1 can mean the model leaves structure in the residuals, or that the estimate is
low; this measurement does not separate the two, and the expert fits are a reference for neither.

## 6. What a design could be (for the owner's decision — not decided here)

1. **The diagnostic needs no fit change.** χ²ᵣ under any variance model can be computed on the fit's own residuals
   (§1, use 1); showing a "noise-calibrated χ²ᵣ" this way changes no fitted number. Adopting new weights is a fitting
   change (§1, use 2) and its own unit.
2. **Which estimate.** On the synthetic set, by the level error and shape spread of §4: for independent noise with
   one scale `flat_ends` (0.97–1.15, needing flat ends) and `scaled_d4` (1.0–1.2) both work, for independent constant
   noise `constant_d4` (independence alone does not select the variance model), no single-k estimator removes a
   per-point factor's shape error, and the lag-1 difference estimators are badly wrong for correlated noise; `flat_ends` is less affected by correlation but needs flat ends and is itself biased by
   correlation; the lag > 1 estimators trade one bias for another. A design needs a rule for the regime, and the only
   model-free evidence of the regime (the diagnostics) is incomplete. Any rule on them is a threshold on a scale-free
   quantity (CLAUDE.md, "Thresholds on data-scaled quantities fail": scale-free, but still a choice that needs its
   own measurement).
3. **Where to estimate it.** The fit window and the whole spectrum agree in the median, not per fit (§5); the choice
   is part of the design.
4. **What to say.** A calibrated χ²ᵣ is only as good as its noise model: whether to show the estimate and its basis
   ("noise estimated from the data: 0.7 × the CPS value"), and what to show when the data are few counts, smoothed,
   or give an unstable estimate.
5. **The instrument's own evidence.** Attempted 2026-10-27 ([counting-time.md](counting-time.md)). Dwell and scans
   are decoded, but the stored values are not whole counts over any common time in the tested ranges, and every file
   records that detector-signature and TXFN corrections were set. The estimated k does not follow 1/(dwell × scans)
   across the two acquisition settings either: surveys have a tenth of the counting time and about 1.5 times the k.
   That is consistent with counting noise only if a/f (the correction over the detector factor) differs between the
   settings, or if the estimators are biased differently. The files do not hold either factor in a usable form, so k
   cannot be taken from the acquisition with what they hold.

## 7. Limits of this measurement

- The synthetic spectra are one family (C 1s-like, 241 points, three GL peaks) and a few correlation families; the
  real surveys (1-point-wide peaks, 1361 points) and other correlation structures are not represented synthetically;
  boundary handling is not benchmarked.
- The real-data readings have no independent truth: no repeated sweeps are stored separately in these files, and
  "Scan_0 … Scan_9" are (HYPOTHESIS) different analysis spots — the folders are named "…10spot" — not repeats, so
  they cannot serve as replicates. 2026-10-27: each file records a point name ("1-1", "1-2", …, property 232) and
  stage coordinates (properties 203–205: 67 distinct X, Y, Z positions over 275 files, 66 in X, Y), which supports
  this.
- The fits are the CURRENT server's refits of the saved models, not the saved fits (those load as "saved before
  sealed records").

## 8. Proposed wording for the displayed χ²ᵣ (2026-10-27, for the owner's approval — not implemented)

**Why change the words.** The page's χ²ᵣ divides by σ = √intensity. For these files that is not the noise (§2), the
real noise scale is not recorded, and it cannot be recovered from the counting time
([counting-time.md](counting-time.md)). §1a shows this scale changes nothing fitted: the uncertainties, support and
required verdicts, and every comparison of fits of the same spectrum stay as they are. It changes only what the
absolute value means.

Today's tooltip says the opposite: "χ² ≈ 1.0 = ideal fit (residuals match expected noise)"
(`templates/index.html:15210`). The Results tile also colours the value green below 2, amber below 5 and red above
(`:11277`). Both read the absolute value as if the noise were known.

**Proposed (site, today → proposed):**

| site | today | proposed |
|---|---|---|
| label: Results tile, header, status bar (`_fitStatLabel` `:10492-10494`, `_applyStatCaption` `:10589`) | `χ²ᵣ` | `χ²ᵣ (relative)` |
| Results tile colour (`:11277`) | green < 2, amber < 5, red ≥ 5 | the ordinary text colour (no verdict from the size) |
| tooltip (`_CHISQ_TOOLTIP`, `:15210`) | "…χ² ≈ 1.0 = ideal fit (residuals match expected noise); χ² >> 1 = poor fit or underestimated uncertainties; χ² << 1 = possible overfitting…" | the text below |
| local-fit tooltip (`_LOCALFIT_TOOLTIP`, `:15209`) | — | append: "Like the server's, it is relative: the noise scale of the data is unknown." |
| notices (`:10414`, `:8953`, `:11083`) | "Fit complete. χ²ᵣ = 2.441 (confirming…)" | "Fit complete. χ²ᵣ (relative) = 2.441 (confirming…)" |
| figure label (`:14772`) | `χ²_r = 2.441` | `χ²_r (relative) = 2.441` |
| CSV / XLSX statistic name (`:14991-14992`) | `Chi-squared reduced` | `Chi-squared reduced (relative; noise scale unknown)` |
| scattered starts, "Other solutions found" (`:9943-9945`, `:10159`, `:10188-10191`) | "…a lower χ²ᵣ…" | unchanged: they compare fits of the same spectrum, which a constant scale leaves intact (§1a) |
| Find Peaks (archived) table, "fit quality (χ²ᵣ)" (`:19700`) | — | unchanged while archived; on revival, the same label |

**Proposed tooltip text:**

> **Reduced chi-squared (χ²ᵣ), relative: the noise scale is unknown.** This is the fit's squared residual per degree
> of freedom, each point weighted by 1/√intensity. That weight is the counting noise only for raw counts. Avantage
> files store counts per second, and their real noise level is not recorded.
>
> - Compare χ²ᵣ between fits of the **same spectrum**: lower means the model leaves less unexplained.
> - Its size does not tell you whether the fit reaches the noise. χ²ᵣ ≈ 1 is not "ideal" here, and values from
>   different spectra, regions or instruments cannot be compared.
> - The ± uncertainties are scaled to the fit's own residuals, so they do not depend on this.
>
> A lower χ²ᵣ is not a better chemical model: check the residuals and the R-factor.

**Open choices:**

- **Label length.** `χ²ᵣ (rel.)` is a shorter label if the tile is tight.
- **CSV / XLSX imports.** The tooltip could say "files" instead of "Avantage files", or name the case where
  intensities are raw counts, where √N is the right noise. The app cannot tell which case a CSV is: `parser.py:47`
  records no unit.
- **The held student note** (`docs/comms/2026-10-16-sealed-fit-record-note.md`) would need one sentence if this
  ships.
- **A calibrated χ²ᵣ** (§6.1) would change these words again. It is a separate decision.

## Generators and files

| file | command |
|---|---|
| `synthetic.json`, `synthetic.txt`, `synthetic_tables.md` | `venv/bin/python scripts/noise_synthetic_benchmark.py --seeds 30 --json docs/findings/noise-estimator/synthetic.json --markdown docs/findings/noise-estimator/synthetic_tables.md > …/synthetic.txt` |
| `real_spectra.json`, `real_spectra.txt` | `venv/bin/python scripts/noise_real_spectra.py --json docs/findings/noise-estimator/real_spectra.json > …/real_spectra.txt` |
| `real_fits_collected.json` | `venv/bin/python scripts/noise_real_fits.py collect --url http://127.0.0.1:PORT --out …` against a 4-worker gunicorn of this branch (a192f78 + these scripts) |
| `real_fits.json`, `real_fits.txt` | `venv/bin/python scripts/noise_real_fits.py analyse docs/findings/noise-estimator/real_fits_collected.json --json …/real_fits.json` |
| the estimators | `scripts/noise_estimators.py`; their arithmetic pinned by `tests/test_noise_estimators.py` (27 tests) |
| `sigma_scale.txt`, `sigma_scale.json` (§1a) | `venv/bin/python scripts/noise_sigma_scale_check.py run OUT.jsonl --procs 4` (the 202 targets of `scripts/optimizer_disagreement_targets.js`; the JSONL holds every response and is not committed), then `… analyse OUT.jsonl --json docs/findings/noise-estimator/sigma_scale.json > …/sigma_scale.txt` |
| `counting_time.txt`, `counting_time.json` ([counting-time.md](counting-time.md)) | `venv/bin/python scripts/noise_counting_time.py --json docs/findings/noise-estimator/counting_time.json > …/counting_time.txt`; the property reader `scripts/vgd_properties.py`; the exact test pinned by `tests/test_noise_counting_time.py` (12 tests) |
