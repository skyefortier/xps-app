# Unit B — estimating a spectrum's noise from the data (design + measurement, 2026-10-26)

**Scope (owner, 2026-10-26):** design and measurement only. Nothing a user sees changes, no fitted number changes,
nothing is deployed. Whether and how the displayed χ²ᵣ changes is a separate decision after this review.

**The question:** the displayed χ²ᵣ should be about 1 for a fit that explains the data down to the noise. It can be
only if the variance it divides by is the data's real noise. Can that variance be estimated from each spectrum
itself, independent of any fit model?

Every claim about the current code is labelled **VERIFIED** (file:line, read on main at a192f78) or **HYPOTHESIS**.
Numbers come from the committed generators (end of this file) and their outputs in this folder.

---

## 1. What the fit assumes today

- **VERIFIED** — the server weights every point by σ_i = √max(y_i, 1), y in the file's own units, before
  background subtraction (`fitting.py:3006-3007`, comment `fitting.py:3002-3005`); the verifier recomputes the same
  (`fitting.py:3821`). The reported χ²ᵣ = Σ((y_sub − fitted_sub)·w)² / max(1, n − n_free) (`fitting.py:3384-3387`).
  Recomputed from the residuals of the 121 committed fits below it agrees to 1.8e-15.
- **VERIFIED** — the local engine and the page's own support test use the same weighting, 1/√max(counts, 1)
  (`templates/index.html:8214`, `:10759`; its record names it `poisson_weighted_chi_square`, `:7388`, `:7399`).
- **VERIFIED** — the σ of every parameter is scaled by χ²ᵣ: lmfit's `Model.fit` defaults to `scale_covar=True`
  (`venv/.../lmfit/model.py:1034`) and `fitting.py` never passes it (every `model.fit(...)` call,
  e.g. `fitting.py:2198`, `:2209`, `:2246`, `:2283`). The support statistic is a ratio of χ² differences
  (`fitting.py:2697-2712`).
- Consequence (arithmetic, from the above): if the true variance is k·y for ONE constant k per spectrum, the fit
  itself, every parameter, every σ and every support F are unchanged by k; only the displayed χ²ᵣ is k times the
  calibrated one. If the true variance has any other shape (a constant term, a correlation, a per-point factor),
  the weights themselves are wrong in relative terms, and correcting them would change fitted numbers.

## 2. What the data are (part a)

| source | what the intensities are | label | evidence |
|---|---|---|---|
| Thermo Avantage `.vgd` (all 230 committed raw files; the instrument is a Nexsa G2, Avantage v6.7.0, per the files' property stream) | **counts per second**, not counts | VERIFIED | each file's chart sidecar `.xml` titles the intensity axis `Counts / s` (e.g. `docs/autofit/test_data/1 UCl4-graphite …DATA/C1s Scan.xml`); at least 99.8 % of every file's stored values are non-integer (`real_spectra.txt`) |
| the same — raw counts divided by a counting time? | **no**: the values are not on any grid 1/t | VERIFIED (data); cause HYPOTHESIS | for counting times t from 5 ms to 2 s, at most 0.55 % of any file's values lie on the grid 1/t — chance level (`real_spectra.txt`, `best_quantum`). HYPOTHESIS: Avantage applies a continuous correction (detector efficiency / dead time / transmission) before storing — not established; its acquisition parameters (dwell, scans) sit in undocumented numeric property ids of the files' main property stream and are not decoded here |
| the app's VGD reader | returns the stored values unchanged; a multi-scan ("overlay") file is returned as the **per-point mean of its scans** | VERIFIED | `vgd_parser.py:94-97`; the page always parses VGDs on the server (`templates/index.html:4032`, `:5404` → `app.py:1022`); its heuristic `parseVGD` (`templates/index.html:5322`) has no caller. All 230 committed VGDs hold one series, so the mean never applies to them |
| committed projects (`*.proj.zip`, 166 spectra) | the same Avantage CPS (non-integer in every spectrum; tab names are the VGD scan names) | VERIFIED | `scripts/noise_real_fits.py` reads them; maxima 7 000–117 000 CPS |
| `.csv` / `.tsv` / `.txt` / `.xy` / `.xlsx` | **unknown to the app**: whatever the exporting program wrote (counts, CPS, normalised, smoothed) | VERIFIED (that it is not known) | `parser.py:47` ("intensity (counts or CPS)"); no unit is read or stored |
| the page's smoothing | display only — it never reaches a fit | VERIFIED | `savitzkyGolay` has one caller, the "Smoothed" chart overlay (`templates/index.html:12958-12969`) |

**Where Poisson σ = √N holds.** Only for RAW COUNTS: integers from one acquisition, not divided, averaged,
corrected, interpolated or smoothed. For counts divided by a counting time t the variance is y/t (k = 1/t); for the
mean of m sweeps it is y/m; after a smooth per-point correction factor T it is y/T (k varies across the window);
after smoothing or interpolation neighbouring points are correlated and no per-point σ describes them fully.
**None of the committed data are raw counts**, so σ = √y in their units has no derivation; whether it happens to be
close is what §5 measures.

## 3. Candidate estimators (part b) — `scripts/noise_estimators.py`

All read only the intensities, in point order, and return a variance model var(y_i) = a + k·y_i. MAD → σ uses the
Gaussian factor 1.4826 so that points on a peak's flanks (where the SIGNAL's difference is large) count as
outliers.

| estimator | model | assumes | fails when |
|---|---|---|---|
| `poisson_file_units` (today) | var = y (k = 1) | the file holds raw counts | any other unit: CPS (k = 1/t), averaged sweeps, any correction |
| `scaled_d1`, `scaled_d2`, `scaled_d4` | var = k·y, k = (robust σ of the normalised 1st / 2nd / 4th binomial difference)² | scaled Poisson; neighbouring points independent; the signal's difference small at most points (a difference of order N annihilates polynomials below N) | **neighbours correlated** (smoothing, interpolation): differences cancel correlated noise, so k is underestimated — by 4–9× for 4th differences (§4); **high counts with sharp peaks**: the signal's difference is not small on enough points and inflates k (worst for low orders); **low counts** (≲ 20 counts per point): the normalisation by the observed y breaks |
| `scaled_d2_lag3` | the same with points 3 apart | correlation shorter than 3 points | the signal's curvature over 6 points inflates k strongly at high counts |
| `constant_d2` (DER_SNR-type) | var = a (constant), from second differences | noise independent of intensity | shot noise (the variance follows the intensity); correlation |
| `varmean` | var = a + k·y, weighted fit of binned second-difference variances against the local mean | a spread of intensities; independent points | high counts with peaks: the peak bins' variance is inflated by the signal, so k collapses (§4); a narrow intensity range confounds a and k |
| `flat_ends` | var = k·y from the variance about a straight line on each end's 10 % | both ends flat (no peak, no curvature) | an end on a peak, a step or curvature — e.g. a survey window (k ≈ 31, §5) |

**Correlation diagnostics** (not estimators), `correlation_diagnostics`: the lag-1 correlation of the normalised
1st and 4th differences (independent points: −0.5 and −0.8, `WHITE_RHO1`), and the lag profile k(lag L)/k(lag 1) of
second differences (independent points: flat, until the signal's curvature lifts it). On the synthetic set the
1st-difference reading is useless at ordinary counts (the signal moves it from −0.5 to +0.0…+0.5 even for pure
Poisson data); the 4th-difference reading stays at −0.75…−0.79 for independent noise and moves to −0.46…−0.69 for
5–7-point smoothing and interpolation, but NOT for a 3-point moving average (−0.83); the lag profile catches all of
them (lag 2: 2.9–4.2 against 1.2–1.5 for independent noise). Evidence, not a test with a threshold.

## 4. Ground truth: synthetic spectra with known noise (part c) — `synthetic.json`, `synthetic.txt`

`scripts/noise_synthetic_benchmark.py --seeds 30`: a C 1s-like window of 241 points (three GL peaks; widths of 3,
10 or 30 points; flat, sloped or Shirley-step background; tallest peak 300 to 3·10⁵ counts) under 12 noise models
whose per-point variance is known exactly: Poisson counts; CPS at counting times 0.05, 1 and 20 s; the mean of 10
sweeps; Gaussian constant; Poisson + constant; a ±30 % transmission factor; a 3- and 5-point moving average, a
7-point Savitzky-Golay, and linear interpolation onto a half-step grid. 12 × 9 shapes × 4 levels × 30 seeds =
12 960 spectra, each judged by every estimator. No fit and no expert reference is used.

The figure of merit is **χ²ᵣ of the TRUE signal** under each estimator's variance, Σ(y − s)²/σ̂² / n: what a fit that
explains the data exactly would show. 1 is right; above 1 the variance is underestimated, below 1 overestimated.
Medians over shapes and seeds, by peak level (counts at the tallest peak):

| noise (truth) | today: var = y | `scaled_d4` | `scaled_d2` | `flat_ends` | `varmean` |
|---|---|---|---|---|---|
| Poisson counts | 1.00–1.05 | 0.87–1.03 | 0.64–1.02 | 0.91–1.07 | 0.15–1.06 |
| CPS, t = 0.05 s (k = 20) | 20–175 | 0.95–1.12 (7.8 at the lowest level) | 0.86–1.10 (7.5) | 0.99–1.15 (8.8) | 0.78–1.19 (9.2) |
| CPS, t = 20 s (k = 0.05) | 0.05 | 0.84–0.95 | 0.48–0.89 | 0.87–1.02 | 0.01–0.84 |
| mean of 10 sweeps | 0.10 | 0.87–0.99 | 0.51–0.93 | 0.88–1.02 | 0.02–0.89 |
| transmission ±30 % | 1.03–1.09 | 0.93–1.10 | 0.66–1.08 | 0.86–1.02 | 0.16–1.13 |
| Poisson + constant | 1.2–96 | 1.05–1.14 | 0.98–1.04 | 0.76–1.04 | 0.86–1.09 |
| Gaussian constant | 0.02–15 | 1.09–1.10 | 0.78–0.81 | 0.75–0.77 | 0.66–0.68 |
| smoothed MA3 | 0.33 | **4.2–4.8** | 2.1–4.1 | 1.02–1.26 | 0.06–3.9 |
| smoothed SG7 | 0.33–0.35 | **7.7–9.5** | 3.3–6.4 | 1.11–1.29 | 0.05–5.9 |
| interpolated (half step) | 0.50 | **4.2–4.9** | 1.6–2.9 | 0.95–1.12 | 0.09–2.8 |

What the measurement shows:
- **Today's σ = √y is exact for raw counts and wrong by exactly k otherwise** (×20 too low a variance for CPS at
  50 ms, ×20 too high at 20 s, ×10 for 10 averaged sweeps).
- **Independent noise of any scale** (counts, CPS, sweeps, a transmission factor): `scaled_d4` recovers it to within
  about −16 % … +12 % in χ²ᵣ at every level above the low-count regime, best of the difference estimators; lower
  orders and `varmean` are pulled down at high counts by the signal (peaks' differences).
- **Correlated noise**: every difference estimator underestimates the variance, the higher the order the worse
  (`scaled_d4` 4–9.5×). `flat_ends` holds (0.95–1.29) because it measures the variance itself, not differences —
  when its ends really are flat.
- **Below ~20 counts per point** (CPS at 50 ms with a 300-count peak) every normalised estimator breaks (7–9).
- No estimator is right everywhere: the data's correlation decides between the difference family and `flat_ends`,
  and the correlation diagnostics of §3 are the only model-free evidence of it.

## 5. The committed real data (part d) — report only

### Whole spectra — `real_spectra.json`, `real_spectra.txt` (`scripts/noise_real_spectra.py`, all 230 VGDs)

Median k (var = k·y in CPS units) over each region's files, with 10–90 %:

| region | files | step | rho1 d4 (white −0.80) | lag profile | `scaled_d4` | `scaled_d2` | `flat_ends` | `varmean` |
|---|---|---|---|---|---|---|---|---|
| B 1s | 50 | 0.1 eV | −0.78 | 1.00 1.38 1.71 2.22 | 0.73 [0.55, 0.88] | 0.85 [0.69, 1.14] | 1.12 [0.77, 4.61] | 0.89 [0.58, 1.39] |
| C 1s | 60 | 0.1 eV | −0.75 | 1.00 1.51 1.76 2.16 | 0.71 [0.54, 0.96] | 0.89 [0.67, 1.22] | 0.99 [0.65, 19.3] | 1.30 [0.61, 2.74] |
| N 1s | 40 | 0.1 eV | −0.78 | 1.00 1.46 1.72 2.30 | 0.62 [0.48, 0.82] | 0.88 [0.69, 1.13] | 0.94 [0.63, 1.45] | 1.25 [0.40, 3.33] |
| U 4f | 20 | 0.1 eV | −0.78 | 1.00 1.55 2.21 2.97 | 0.66 [0.54, 0.81] | 0.82 [0.63, 0.88] | 2.47 [0.95, 4.45] | 1.06 [0.52, 1.49] |
| Survey | 60 | 1.0 eV | −0.75 | 1.00 1.19 1.32 1.50 | 1.01 [0.91, 1.12] | 1.07 [0.96, 1.16] | 31.6 (ends not flat) | 1.07 [0.98, 1.16] |

Read against §4, not concluded from. The core levels' 4th-difference correlation is at the independent value
(−0.75…−0.78 against −0.75…−0.79 synthetic independent, −0.46…−0.69 smoothed). Their lag profiles (1.4–1.6 at lag 2)
sit just above the synthetic independent cases (1.2–1.5) and well below the smoothed ones (2.9–4.2). And on the core
levels `flat_ends` reads 1.4–1.5× `scaled_d4` where the ends are flat (B 1s 1.53, C 1s 1.39, N 1s 1.52), against
≈ 0.94–1.0 for synthetic independent noise and 3.8–7.2 for synthetic smoothed or interpolated noise. Each reading is consistent with nearly
independent noise; the intermediate ones admit a mild correlation or ends that are not quite flat, and this
measurement does not separate the two. On these data k is **of order 1** in CPS units (`scaled_d4` 0.62–1.01 by
region; `flat_ends` 0.94–1.12 where the ends are flat) — near the value today's weighting assumes, which in CPS
units is a coincidence of the acquisition, not a derivation (§2). The earlier flat-end measurement on the C 1s scans
(dispersion 0.4–1.2 × the mean; `docs/findings/find-peaks-scale/README.md` §2, on branch `fix-occupancy-f-test`) is
consistent with this.

### Existing fits — `real_fits.json`, `real_fits.txt` (`scripts/noise_real_fits.py`)

Each committed tab's own saved model refitted by the current server through the page (Run Fit; 121 of 121
converged), and the χ²ᵣ of the SAME residuals under each estimate (estimated once from the fit window, once from the
whole spectrum — they agree):

| variance used | χ²ᵣ median | 10–90 % |
|---|---|---|
| today, var = y (displayed) | 2.44 | [1.74, 17.5] |
| `scaled_d4` | 3.75 | [2.40, 22.1] |
| `scaled_d2` | 3.18 | [1.71, 15.9] |
| `flat_ends` | 2.81 | [1.58, 8.43] |
| `varmean` | 2.58 | [0.74, 12.4] |
| `scaled_d2_lag3` | 1.65 | [0.84, 7.36] |
| `constant_d2` | 4.26 | [2.54, 33.1] |

By region (median; displayed | `scaled_d4` | `flat_ends`): B 1s (20) 9.95 | 9.83 | 9.61; C 1s (44) 2.34 | 3.88 | 3.16;
Cl 2p (3) 3.28 | 5.25 | 2.93; U 4f (54) 2.38 | 3.64 | 2.43. Under every estimate most committed fits sit above 1.
**Reported, not concluded:** above 1 can mean the model leaves structure in the residuals, or that the estimate is
low; this measurement does not separate the two, and the expert fits are not a reference for either.

## 6. What a design could be (for the owner's decision — not decided here)

1. **Only a constant scale keeps every fitted number.** A per-spectrum k̂ (var = k̂·y) changes the displayed χ²ᵣ to
   χ²ᵣ/k̂ and nothing else (§1). Anything with another shape (a + k·y, per-point factors, correlation) changes the
   weights and so the fits — that would be a fitting change, its own unit.
2. **Which k̂.** On the synthetic set `scaled_d4` is the best estimator when neighbouring points are independent and
   `flat_ends` the one that survives correlation; neither is right in both regimes. A design would need a rule for
   the regime — the correlation diagnostics are the evidence, and turning them into a rule means a threshold on a
   scale-free quantity (CLAUDE.md, "Thresholds on data-scaled quantities fail": these are scale-free, but the
   rule is still a choice that needs its own measurement).
3. **Where to estimate it.** The fit window or the whole spectrum agree on the committed data (§5); the whole
   spectrum has more points but may include regions with other corrections.
4. **What to say.** A calibrated χ²ᵣ is only as good as the noise model; showing k̂ and its basis (e.g. "noise
   estimated from the data: 0.7 × the counts-per-second value") is part of the decision, as is what to show when
   the data are too few counts, smoothed, or the estimate is unstable.
5. **The best evidence would be the instrument's own.** If Avantage's acquisition parameters (dwell time, scans,
   detector correction) could be decoded from the VGD properties, k would follow from the acquisition, not the
   data. Not attempted here (undocumented ids, §2).

## 7. Limits of this measurement

- The synthetic spectra are one family (C 1s-like, 241 points, three GL peaks); surveys with 1-point-wide peaks and
  very large windows are represented only by the real data.
- The real-data readings rest on assumptions §4 tests only synthetically; there is no independent truth for them:
  no repeated sweeps are stored separately in these files, and "Scan_0 … Scan_9" are HYPOTHESIS different
  analysis spots (the folders are named "…10spot"), not repeats, so they cannot serve as replicates.
- The fits are the CURRENT server's refits of the saved models, not the saved fits (those load as "saved before
  sealed records").

## Generators and files

| file | command |
|---|---|
| `synthetic.json`, `synthetic.txt` | `venv/bin/python scripts/noise_synthetic_benchmark.py --seeds 30 --json docs/findings/noise-estimator/synthetic.json > …/synthetic.txt` |
| `real_spectra.json`, `real_spectra.txt` | `venv/bin/python scripts/noise_real_spectra.py --json docs/findings/noise-estimator/real_spectra.json > …/real_spectra.txt` |
| `real_fits_collected.json` | `venv/bin/python scripts/noise_real_fits.py collect --url http://127.0.0.1:PORT --out …` against a 4-worker gunicorn of this branch (a192f78 + these scripts) |
| `real_fits.json`, `real_fits.txt` | `venv/bin/python scripts/noise_real_fits.py analyse docs/findings/noise-estimator/real_fits_collected.json --json …/real_fits.json` |
| the estimators | `scripts/noise_estimators.py`; their arithmetic pinned by `tests/test_noise_estimators.py` |
