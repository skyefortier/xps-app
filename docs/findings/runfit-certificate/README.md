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

## V3 — main's search path, only the winner certified (added after the above)

V2 certified the fit BEFORE the perturbed restarts, which moved the point they
start from — the cause of V2's basin flips. V3 is the brief read literally and
without that side effect: the fit and its perturbed restarts run exactly as on
main (judged by the flag, perturbed from main's point), then the WINNER is
certified; the scattered starts (and the required refit) are certified.

| V3 | Trust-Region | Levenberg-Marquardt |
|---|---|---|
| converged | 202 → 202 | 197 → 202 |
| area %: max / > 1 pp / > 0.1 pp | 21.9 pp / 5 / 9 | 13.4 pp / 2 / 16 |
| atomic %: max / > 1 pp | 22.6 pp / 6 | 13.8 pp / 2 |
| chi2r lower by > 1 % / higher | 6 / 2 | 6 / 1 (+0.68 %) |
| returned fit moved | 12 | 98 |
| added time: median / p90 / max | +0.07 / +0.54 / +32 s | +0.04 / +0.91 / +37 s |
| Run Fits over 60 s | 0 → 1 | 1 → 0 |
| "N of 3" line changed; alternatives listed | 37; 8 → 5 | 45; 7 → 6 |
| targets with a start "did not converge" | 3 → 1 | 30 → 4 |
| two presses: byte-identical / max / > 1 pp | 109 / 21.9 pp / 2 | 138 / **0.074 pp** / 0 |

LM V3's largest change is 8-JT C1s Scan_7, 13.4 pp to a BETTER minimum
(chi2r 21.0 → 15.5); its repeat presses agree better than main's (0.074 vs
0.23 pp).

TR V3's largest change and repeat difference are the SAME target, 8-JT C1s
Scan_5 (33.9 vs 51.9), and in the press that returned 51.9 the certificate did
not move the fit (1 restart): main's own search landed there. **Main alone,
pressed 12 times in fresh processes, returns 51.9 every time; in both full
runs (the target is the 92nd in the process) it returned 33.9.** The basin
main's Trust-Region reaches on this target depends on the process's history
(memory alignment → BLAS rounding → basin). So "two presses" understates
main's own instability, and TR flips of this kind are pre-existing; the
certificate changes how often they occur, it does not create the class.


## Final code (V3 only, the displacement report added; 2026-09-30)

The shipped code (`fitting.py` sha256 13433ac0…, switches removed), all 202
targets, both methods (`data/final_*.jsonl`, `data/analysis_final_*.json`):
reproduces V3 — TR: converged 202 → 202, area > 1 pp on 4 (max 15.2 pp, 1-GTA
C1s Scan_4 to a better minimum; 8-JT Scan_5's history-dependent basin did not
flip in this run), chi2r higher on 0; LM: converged 197 → 202, area > 1 pp on 2
(max 13.4 pp, 8-JT C1s Scan_7, chi2r 21.0 → 15.5), higher on 0, scattered
starts "did not converge" 30 → 3 targets. (Added time in this run is inflated
by the full test suite running alongside; V3's clean timings stand.)

**The > 1 eV displacement notice** (owner, 2026-09-29): **0 of 202 targets
with either method.** The certificate moved the returned fit on 10 (TR) and 100
(LM) targets, and the largest centre move was 0.043 eV (TR, 1-GTA C1s Scan_4)
and 0.011 eV (LM); none > 0.1 eV. The area changes above come from amplitudes
and widths (many of these models lock their centres). The notice exists for the
fit that stopped far from a minimum — the two-basin test model, where
Levenberg-Marquardt reports success at chi2r ~286 and the continuation moves
components > 1 eV (`tests/test_runfit_certificate.py`).

**Scan_5 check (owner: does the scattered-starts line flag the 33.9 / 51.9
minima?)** — partly. Twenty presses of main at shifted memory alignments
(`scripts/runfit_certificate_scan5_presses.py`): 10 at 33.9, 10 at 51.9. From
33.9 the line reads "0 of 3 scattered starts reached this solution; 1 found a
DIFFERENT solution with a lower χ²ᵣ; 2 ended in a solution that is not better
(χ²ᵣ 51.91)" — 51.9 is named. From 51.9: "2 of 3 scattered starts reached this
solution; 1 found a DIFFERENT solution with a lower χ²ᵣ" — the alternative is
χ²ᵣ 17.26 (a component moved −1.43 eV, 21.8 pp), and 33.9 is not found. Either
way the student is told the fit is not unique; only one direction names the
other minimum.

## The C 1s parity battery (found by the full suite, 2026-09-30)

`tests/autofit/test_c1s_parity_battery.py` refits each of the 29 eligible saved
expert C 1s fits with Levenberg-Marquardt and NO perturbed restarts, and
asserted the refit stays within 5 meV / 0.5 % of the saved fit. With the
certificate, 25 are unchanged; four are not minima:

| target | saved fit chi2r | certified refit | largest move |
|---|---|---|---|
| 8-JT C1s Scan_2 | 5.49378 | 5.47705 | 0.0013 eV, 0.58 % |
| 8-JT C1s Scan_3 | 5.99467 | 5.97492 | 0.0105 eV, 4.3 % |
| 8-JT C1s Scan_5 | 6.94134 | 6.91861 | 0.0084 eV, 1.8 % |
| 8-JT C1s Scan_6 | 8.95275 | NOT certified in 50 restarts (8.918 at the cap) | — |

Scan_6 is a flat valley: each Trust-Region restart stops on its own tolerance
after 34–51 evaluations while still improving by > 1e-8; 106 restarts certify
it at chi2 −3.1 %, with a zero-amplitude component resurrected as a 0.2 eV
needle (amplitude 0 → 649, FWHM 4.18 → 0.20 eV). The cap (50, a count) is not
raised: on the page's own requests (3 perturbed restarts) the most any
returned fit needed was 32 (Trust-Region) / 5 (Levenberg-Marquardt), and
Scan_6's own model certifies there in 32 / 1. The one page path that sends no
perturbed restarts — Find Peaks' "Refit my current peaks" (`/api/analyze`,
`n_perturb` 0) — reports this model as not converged. The battery now lists
the four (`BEYOND_THE_EXPERT_FIT`: the certified refit must be LOWER than the
saved fit; `NOT_CERTIFIED`: the verdict is pinned), keeps the old rule for the
other 25, and its regenerated fixture is compared within rounding
(`fit_equality.SAME_MINIMUM_REL`).

## Codex rounds

**Round 1 — NO-GO ×2** (`docs/autofit/codex/a2_runfit_certificate_verdict_run{A,B}.md`,
commit 79dfa58; both: the certificate's exits, cancellation during a restart
(`FitCancelled`), V3's unchanged search order and the 0 / 202 notice count
verified; the Scan_5 answer confirmed):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B): `assert_same_fit` accepted distinct minima of a SMALL component — curves on the whole signal's scale, centres on the energy span (A: a 10-count line beside a held 1e6 one, certified at ±0.25 eV; B: two minor lines swapped) | each quantity on its OWN scale: a component's curve against that component's height, its centre against its own half-maximum width; chi2 at the objective's scale (10 × ftol), parameters at 10 × √ftol; a component the fit calls unsupported in both responses is compared by its verdict only (its parameters are undetermined — no magnitude floor). Tests: both counterexamples (the small line relocated 1 eV in a dominant line's tail, invisible on the signal's scale), a 1 %-of-width centre move |
| 2 | MAJOR (A, B): a NaN or None in a curve compared equal (NaN > tol is false) | non-finite values must sit in the same places, then finite parts are compared; tests for NaN / None / inf in fitted_y, residuals and a component |
| 3 | MAJOR (B): the battery fixture admitted +0.09 % chi2r and +0.010 eV (chi2 at the parameter tolerance, a centre against the span) | fixture chi2 at 10 × ftol (1e-7; same-minimum presses measured ≤ 8.9e-9), centres at 1e-3 of the component's own FWHM; both injections now fail; stable over 3 separate processes |
| 4 | MINOR (A): the different-minimum proofs could pass on the seed alone | proofs pin one seed; a rejection must name a fitted quantity and never `random_seed` |
| 5 | MINOR (B): the note called every changed TR fit "better", incl. Scan_5's basin flip | the note separates the certificate's changes (all to a lower chi2r; final run: 4 TR, 2 LM) from the pre-existing two-solution variability |
| 6 | MINOR (B): the branch diff "deleted" A1's deploy-log entry (the branch was cut before that commit) | main merged into the branch (no rebase, no force-push) |

**Round 2 — NO-GO ×2** (`a2_runfit_certificate_r2_verdict_run{A,B}.md`, commit
b66d6fe; round-1 fixes verified: the small-component proof, seed-pinned
rejections, the battery injections, stability over three processes):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B): skipping components both fits call unsupported hid distinct certified minima (an unsupported narrow line certified at −0.25 and +0.25 eV, the objective rising between) | no skip and no per-quantity scales: ONE metric, the fit's own — the fitted curve as sum(w² Δy²) with the fit's weights, against 10 × ftol × chi2 (what certification means); every fitted parameter in units of its own sigma on the same scale (sqrt(10 × ftol × dof) × sigma: if the fitted curve is within tolerance every parameter is within that bound, Cauchy-Schwarz in the H norm); a component the fit determines (a free parameter with a sigma) is judged by its parameters, one it does not (no sigma) by its curve in the objective norm — zero-amplitude jitter counts ~0, a relocated line jumps by many sigma. (A first version judged every component's CURVE in the objective norm; the full suite then failed on two overlapping components trading intensity along a flat direction of one minimum — the sum within tolerance, each curve 3× past it — so determined components are judged by their parameters; test added.) Support statistic relatively, floored by the objective tolerance. Test: the reviewers' unsupported pair, rejected |
| 2 | MAJOR (B) / MINOR (A): matching infinities made a component's scale infinite, so a 1e6-count finite change passed | the weighted norm runs over the finite samples after the non-finite masks are checked; test |
| 3 | MINOR (B) / MAJOR (A): the scattered starts' chi2r (fit, alternatives, not-better list) got the parameter tolerance (+0.09 % passed) | chi2r and not_better_chi2r at the objective scale; three tests |
| 4 | MINOR (A, B): the note mixed runs (4 / 202 is the final run's, where 198 — not 197 — stay below 1 pp and starts' non-convergence is 30 → 3) and called two U 4f satellites C 1s | the note takes the changes, convergence and the notice from the final run, labels the time as V3's clean measurement, and names the regions |

**Round 3 — NO-GO ×2** (`a2_runfit_certificate_r3_verdict_run{A,B}.md`, commit
03916fa; the certificate, cancellation, V3 order, the battery and the note's
numbers verified again):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B): distinct certified minima still compared equal — two 10-count lines at ±0.25 eV beside a 1e6-count one: the saddle 6e-10 relative in chi2 (below ftol), the centre's sigma 17 eV, so both the objective-norm curve test and the sigma-unit parameter test accepted a five-width relocation | the statistical criteria are gone: judging sameness through the fit's own statistics lets statistically indistinguishable but DISTINCT minima through, and the owner's condition is about minima. Every quantity on its OWN scale with no exemption: each component's curve against its own height, its centre against its own half-maximum width, bounded parameters against their span, everything else relatively, all at 10 × √ftol; objectives at 10 × ftol. The pair is rejected (test). Resolution, stated in the helper: minima closer than 1e-3 of every quantity's own scale are not told apart; a component driven exactly to zero amplitude fails closed (none in the tests' models) |
| 2 | MAJOR (B): the sigma-value comparison rejects recorded same-minimum presses (B4C-UCl4 U4f Scan_1: chi2 8.9e-9 apart, a GL-mix sigma 0.544 vs 0.129) | uncertainties are not compared (documented with that evidence); test |
| 3 | MAJOR (A, B): determined components' curves and every area went unchecked (+1e6 counts in a curve, area × 2 or NaN passed) | every component curve against its own height; areas relatively, non-finite correspondence; tests |
| 4 | MINOR (A): NaN vs inf sigma compared equal | uncertainties are not compared (#2) |

**Round 4 — NO-GO ×2** (`a2_runfit_certificate_r4_verdict_run{A,B}.md`, commit
711da78). **Proportionality ruling, both runs: the stated finite resolution
satisfies the owner's "equal within rounding" requirement; sub-resolution
distinct minima alone are not a finding.** No false rejection on the tests'
models (incl. the overlapping-component case); certificate, cancellation, V3
order and 0 / 202 notices verified again.

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A): a scattered-start alternative's centres were scaled by the RETURNED fit's component width — a 0.04 eV alternative line took a 0.29 eV allowance, and two alternatives 0.24 eV apart passed | an alternative's centres and shifts are scaled by that alternative's own components' FWHM; test |
| 2 | MAJOR (A, B): a LINKED parameter (expr, no bounds of its own) was compared relatively while its master used its bound span: recorded same-minimum Trust-Region repeats of LA doublets (4-GTA UCl4-BN U4f Scan_4 and three more: m 0.477 → 0.001 inside 0–499) would be rejected | a linked parameter is judged on the span of the master its expression references; test |

**Round 5 — NO-GO ×2** (`a2_runfit_certificate_r5_verdict_run{A,B}.md`, commit
68fbf47; the resolution ruling stands; all 398 eligible recorded same-minimum
parameter / curve replays pass, incl. round 4's four):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B): a DS+G alternative (α, β, m — no fwhm parameter) still took the returned fit's width (0.62 eV allowance for lines 0.1 eV wide, 0.5 eV apart) | the CLASS fix: one width definition everywhere — the half-maximum width of the component's own curve. An alternative's curve is evaluated from its parameters through the server's own lineshape (the one whose arguments are exactly those parameters); no match fails closed at one grid step. No shape-specific width parameter anywhere; test |
| 2 | MAJOR (A, B): bound inheritance stopped after one link (p4_m → p3_m → p2_m: the grandchild fell back to a relative allowance) | resolved transitively to the bounded master (cycle-guarded); test |

**Round 6 — NO-GO ×2** (`a2_runfit_certificate_r6_verdict_run{A,B}.md`, commit
2157625; the resolution ruling stands; round 5's fixes verified — all seven
lineshapes, unmatched / raising shapes, negative and zero curves, real
three-component link chains with factors and offsets; 398 recorded replays
pass):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B): a scattered-start alternative's parameters are bare values, so a bounded one (LA m, 0–499) was compared relatively and equivalent alternatives — identical curves and chi2r — were rejected | an alternative is the same model: its bare values take the model's bounds (or linked master) from the returned fit's matching parameter; test |
| 2 | MINOR (B): link references were parsed with a restricted pattern (ids with underscores, e.g. proot_1_m, not resolved) | any lmfit identifier in the expression is looked up; test |

**Round 7 — NO-GO ×2** (`a2_runfit_certificate_r7_verdict_run{A,B}.md`, commit
577e6aa; the resolution ruling stands; round 6's fixes, the certificate and
398 recorded replays verified):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A): the bounded rule was 1e-3 × max(span, |value|): a narrow bound far from zero ([1.1, 1.101]) allowed 0.0011 where its span allows 1e-6 — two certified minima with swapped widths accepted | the span ALONE; test (the reviewer's pair, real fits) |
| 2 | MAJOR (B): alternatives' curves were reconstructed only for the centre scale, never compared — once round 6 gave their parameters the model's span, an LA α / β swap changing the curve by 0.147 % of its height passed | an alternative's reconstructed component curves are compared against their own height, like a returned component's (both its curve and its parameters must agree); the round-6 test now uses an m change below one data point (identical curves, the reviewers' case); test |

**Round 8 — NO-GO ×2** (`a2_runfit_certificate_r8_verdict_run{A,B}.md`, commit
01cbb80; the resolution ruling stands; narrow bounds down to 1e-11 span
verified; 398 recorded replays pass):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B): gaussian and lorentzian share parameter names, so an alternative's curve was reconstructed with BOTH and both compared — a Lorentzian inside the resolution (0.096 %) was rejected by its fictitious Gaussian twin (0.106 %) | the lineshape's identity is taken from the response: the one lineshape that reproduces the returned component of the same id from its own parameters; the alternative is evaluated with it; test (the reviewers' case) |
| 2 | MINOR (A, B): a reconstruction that raised silently removed the curve check | fails closed: "its curve cannot be reconstructed"; test with an injected failure |
| 3 | MINOR (B): a 1e-11 bound span rejected a one-ULP difference | a machine-precision floor (4 ULP of the value) beside the span, not a wider span; test (the reviewer's real fits) |

**Round 9 — NO-GO ×2** (`a2_runfit_certificate_r9_verdict_run{A,B}.md`, commit
fe2120f; the resolution ruling stands; round 8's fixes verified — unmatched
shapes, non-finite returned curves, mismatched parameter sets, reconstruction
exceptions):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B): lineshape identity cannot be inferred from a curve — a very broad Gaussian and Lorentzian agree to 1e-13 on the grid, identification was ambiguous and a byte-identical copy failed closed | the identity is carried explicitly: `run_fit` reports each `individual_peaks[]` entry's `shape` (additive; no numerical effect — the fit is unchanged, `fitting.py`'s measured numerics stand); the comparison reads it (inference only for a response without it, failing closed when ambiguous); test |
| 2 | MINOR (B): a reconstruction returning NaN at the alternative's parameters matched NaN masks and passed | a non-finite reconstruction is a failed one (fails closed); test |
