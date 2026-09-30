# A2 — the minimum certificate on Run Fit: measurements (2026-09-29)

Owner: "Run Fit's returned fit and its scattered starts: apply the
certificate. Before review, measure on the 202 targets with the default
method: peak AREA and ATOMIC-% changes, not only chi2 (median, max, count over
1 pp) … added wall time per Run Fit (median, 90th percentile); how the 'N of 3
scattered starts' line changes. Same measurements for Levenberg-Marquardt."

## What was built (uncommitted on `fix-runfit-certificate`, pending the decisions below)

`fitting._certify_fit` / `_certified`, applied in `run_fit`'s one fitter
`fit_model` for the local methods (leastsq, least_squares, nelder): restart
Trust-Region from the end point, again from each point it improves, until a
restart improves chi2 by less than Trust-Region's own ftol (scipy's default,
read from its signature); at most 50 restarts; out of restarts / non-finite /
raising / evaluation-capped-without-improvement = not converged, `success:
false` with the reason. The point returned is the one the final restart
certified — the fit itself when it was already at its minimum (a
Levenberg-Marquardt fit at its minimum comes back exactly as MINPACK returned
it). Response field `certificate: {certified, restarts, moved, optimiser_flag}`.
A caller's `max_nfev` limits each restart. DE / basinhopping keep their own
refinement verdict (`certificate: null`).

Two scopes were measured, because the brief names "the returned fit and its
scattered starts" while the perturbed restarts are what PRODUCE the returned
fit:

* **V1** — every local candidate certified: the fit, each of the 3 perturbed
  restarts, each of the 3 scattered starts (and Auto-Fit's required refit).
* **V2** — the brief literally: the fit and the scattered starts certified; the
  perturbed restarts compete by their flag as before and the winner is
  certified.

## Method

`scripts/runfit_certificate_measure.py`: all 202 committed targets through
`/api/fit` exactly as the page sends them (n_perturb 3, n_starts 3), main
(detached worktree at d6f4423) vs the branch, Trust-Region and
Levenberg-Marquardt, six single-threaded processes on the 8-core i9
(`VECLIB_MAXIMUM_THREADS=1`), so per-target times are comparable across
configurations. `scripts/runfit_certificate_analyze.js`: area % = the Results
table's (over components the server calls supported), atomic % = the Quantify
tab's (area / RSF over supported components, RSF from the page's own
`_detectPeakRSF`); per target the largest component change. Repeat presses:
`scripts/runfit_certificate_repeat.py` (a second full run of the identical
requests in a separate process).

## Results (main → after, 202 targets; LM: 196–197 converged on main)

| | TR V1 | TR V2 | LM V1 | LM V2 |
|---|---|---|---|---|
| converged | 202 → 202 | 202 → 202 | 197 → 202 | 197 → 202 |
| area %: median / max change | 0 / 37.3 pp | 0 / 15.2 pp | 0.001 / 29.6 pp | 0 / 32.5 pp |
| area % change > 1 pp / > 0.1 pp | 6 / 10 | 3 / 7 | 8 / 22 | 5 / 19 |
| atomic %: max / > 1 pp | 38.4 pp / 8 | 15.6 pp / 4 | 30.4 pp / 8 | 33.5 pp / 5 |
| chi2r lower by > 1 % / higher | 9 / 0 | 5 / 2 (≤ +0.95 %) | 11 / 2 (≤ +70 %) | 8 / 2 (≤ +205 %) |
| returned fit moved by the certificate | 76 | 15 | 185 | 101 |
| added time per Run Fit: median / p90 / max | +0.9 / +19.3 / +306 s | +0.14 / +1.0 / +43 s | +1.0 / +13.8 / +69 s | +0.13 / +2.9 / +39 s |
| Run Fits over 60 s | 0 → 15 | 0 → 1 | 1 → 1 | 1 → 0 |
| "N of 3" line changed | 39 | 33 | 49 | 45 |
| targets with an alternative listed | 8 → 3 | 8 → 5 | 7 → 6 | 7 → 7 |
| targets with a start "did not converge" | 3 → 1 | 3 → 0 | 30 → 4 | 30 → 4 |
| support verdict flipped | 1 | 1 | 0 | 0 |

Every target whose areas moved by > 1 pp (all C 1s except one U 4f):

| | lower chi2 | higher chi2 | a centre moved > 1 eV |
|---|---|---|---|
| TR V1 (6) | 6 | 0 | 2 (1-GTA Scan_4 2.36 eV, 8-JT Scan_8 1.87 eV) |
| TR V2 (3) | 3 | 0 | 0 |
| LM V1 (8) | 6 | 2 (8-JT Scan_7 21.0 → 35.8; Cl2p-project C1s Scan_4 4.31 → 5.29) | 5 |
| LM V2 (5) | 3 | 2 (8-JT Scan_7 21.0 → 64.2; Cl2p-project C1s Scan_4 4.31 → 5.29) | 3 |

A HIGHER returned chi2 is possible although the certificate only ever lowers
chi2 from a given point: the perturbed restarts start from the (certified)
fit, not from where main's uncertified fit stopped, so they explore different
basins; on main the better answer came from a lucky perturbed restart. It is
the known several-minima problem (8-JT C1s Scan_1/5/6/7 are the scattered-
starts unit's trap targets), not a certificate error. Under V1 Trust-Region it
did not occur; under Levenberg-Marquardt it did in both scopes.

The certificate also moves components a long way: a "success" of main's
Levenberg-Marquardt at chi2r 286 on the scattered-starts test's two-basin
problem is not a minimum; the certificate carries it in 6 restarts to the real
decomposition (1.37), relocating two components by > 1 eV — what the
scattered-starts panel used to offer as an alternative, behind the red-band
confirmation. It is a descent from the student's start, not a jump to a
better-scoring basin, but the student is not asked.

## Reproducibility (two presses of the identical request, separate processes)

| two presses | byte-identical | largest area-% difference | targets > 1 pp |
|---|---|---|---|
| main TR | 145 / 202 | 1.51 pp (U 4f Scan_7) | 1 |
| TR V1 | 99 / 202 | **37.3 pp** (1-GTA C1s Scan_4: chi2r 3.40 vs 3.98 — the second press returned main's answer), 21.9 pp (8-JT C1s Scan_5: 33.9 vs 51.9), 16.1 pp (8-JT C1s Scan_7: 15.5 vs 35.8) | **3** |
| TR V2 | 138 / 202 | 1.19 pp (U 4f Scan_7) | 1 |
| main LM | 140 / 196 | 0.23 pp (U 4f Scan_4) | 0 |
| LM V1 | 112 / 202 | 0.033 pp | 0 |
| LM V2 | 156 / 202 | **21.9 pp** (8-JT C1s Scan_5: 51.9 vs 33.9), 21.6 pp (8-JT C1s Scan_6: 38.3 vs 70.6) | **2** |

So the large before/after changes above are partly a LOTTERY, not a
deterministic effect of the certificate: on the several-minima C 1s targets
(8-JT Scan_5/6/7, 1-GTA Scan_4) each certificate restart adds Trust-Region's
arithmetic jitter, the perturbed restarts start from the jittered point, and
the basin they reach flips between identical presses — by 16–37 pp. The owner's
2026-09-21 requirement ("reloading a saved project and pressing Run Fit
regenerates the figure within meaningful precision"; met on main: 1 target
> 1 pp, 1.5 pp) is violated by TR V1 on 3 targets and LM V2 on 2.

**Pre-existing, found here:** on MAIN, Levenberg-Marquardt is not
byte-reproducible across processes on the U 4f models containing LA(α,β,m):
56 of 64 such targets differ (≤ 0.23 pp), every other shape family 0. LA's
evaluation runs `np.convolve`, whose float64 inner product goes through the
BLAS dot (Accelerate's alignment effect, the Trust-Region cause) — so the
"Levenberg-Marquardt byte-identical on 202" of the seeding unit (2026-09-21)
predates the continuous-m LA (2026-09-25). Not addressed here.

**Consequence of the certificate:** wherever it moves a Levenberg-Marquardt or
Nelder-Mead fit, the returned numbers are Trust-Region's and carry its
jitter. 19 existing tests pin LM / Nelder byte-identity or observe the
optimiser's calls; they fail as the code stands (list in the plan).
