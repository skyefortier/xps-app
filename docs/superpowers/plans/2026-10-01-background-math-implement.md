# Background math — implementation (2026-10-01)

Owner, 2026-10-01 (findings accepted, `docs/findings/background-math/README.md`):

> Implement as ONE unit on its own branch, measure, and REPORT the number changes
> before review. Do not deploy.
> 1. Endpoint averaging sets the two edge levels ONLY (fixes F1 and smart's failure
>    above an averaging of 1 — which is the default since it became 3). The integral
>    and the B <= I constraint both use the raw data. All methods read averaging the
>    same way.
> 2. F12/F10/F11 — every background must satisfy its defining statement or report
>    failure. Check each result against the statement; on failure (cycling, can't
>    start, Tougaard undetermined/unsolvable) the background is "not converged" with
>    a plain message, and nothing downstream treats it as valid. No fallback solver now.
> 3. F5 — Shirley's stopping tolerance becomes relative, per the design rule.
> 4. F2 — state plainly in docstrings and the background-type tooltips: the smart
>    methods constrain against noisy counts, which raises net area by about 1% on
>    noisy data; plain Shirley carries its own bias at large steps. Document, don't change.
> 5. F3 — after (1), re-measure smart vs smart_exp on all committed spectra. If they
>    agree within fit_equality.py's rounding, propose collapsing them into one menu
>    entry, with both codes still loading old files. Report, don't implement the collapse.
> 6. F4 — shirley_linear stays off the menu permanently; existing notice stays.
> Measure on the committed data: net-area and atomic-% changes from (1) and (3)
> (median, max, count over 1 pp). Codex x2. Stop for my review with the numbers.

Branch `bg-math-implement` = `bg-math-foundation` (the accepted findings) + main
(the Find Peaks archive) + this unit.

## 1. Design

**One reading (item 1).** `fitting._edge_levels(ys, n_avg)`: the means of the first /
last k = min(n_avg, n // 4) points, k >= 1 (1 below four points) — the rule
`_apply_endpoint_averaging` and `smart_exp` already used. Shirley, Smart (its
Shirley), Smart (experimental), Shirley + linear and Tougaard all take their levels
from it; every integral and clamp reads the raw data. `linear` is unchanged: it never
read the averaging (raw end points; the request seed already excludes `endpoint_avg`
for it) — extending averaging to it would be a new behaviour, not a reading of an
existing one (an owner decision if wanted). `_apply_endpoint_averaging` stays for the
tests and scripts that reproduce the old reading.

**One stop (item 3).** `BG_REL_TOL = 1e-12` of the window's intensity span (max - min
of the raw window): every iteration (Shirley, Smart (experimental), Shirley +
linear; Smart through its Shirley) stops when one more step changes it by at most
that, and returns the point the step was taken FROM — the point whose residual was
just measured. Chosen from the measurement on the 121 committed spectra (new reading):
1e-6 / 1e-8 / 1e-10 / 1e-12 / 1e-13 of the span are reached in at most 9 / 12 / 16 /
19 / 21 steps (cap 200); the residual floor the iteration reaches is <= 1.3e-16 of the
span. 1e-12 sits four orders above that floor and far below any reported quantity.

**One certificate (item 2).** `fitting.background_certificate(x, y, bg, method, n_avg)`
checks a result against its DEFINING STATEMENT, independently of how it was computed:
Shirley B = T(B); Smart / Smart (experimental) B = min(T(B), I); Shirley + linear
B = min(L + d(1 - F(B)), I); residual <= BG_REL_TOL of the span — the same number the
iterations stop on, and the same arithmetic (`_shirley_map`, `_cum_from_high`), so a
stopped iteration certifies exactly; the clamp identity is exact in floating point
(I - min(B, I) is 0 where it clamps), so a certified Shirley gives a certified Smart.
Undefined (no net signal above the edge line, F10) and non-finite results fail.
Tougaard is explicit (no iteration): its certificate is whether the anchor determines
the amplitude — a zero high-edge loss sum with equal levels is undetermined unless the
whole loss vector is zero (then the flat C0 IS the answer), with unequal levels there
is no solution (F11). Since Codex round 1 the sum is evaluated AS STATED on every
grid (the convolution that stood in for it on grids uniform to 1e-6 of the step is
gone: near cancellation its error became 16 % of the span, and the page — which
always summed exactly — then disagreed with the server); measured equal to the
checker's independent sum (0 difference) on all 121 committed spectra, 20 ms on a
1500-point window. The certificate's predicate is the iterations' own (diff <= tol x
span, not the quotient: they differ by a rounding step at the boundary), and a target
that does not evaluate to finite numbers fails.
`fitting.compute_background` = the method + its certificate; on failure it raises
`BackgroundNotConverged` (a ValueError) with "<Method> background not converged:
<reason>." — HTTP 422 from `/api/fit` (and `/api/fit/start`'s record) and
`/api/background`. `run_fit`, `compute_background_only`, Find Peaks' engine
(`autofit/engine.py`) and `autofit/parity.py` all call it. No fallback solver.

**The page.** The twins run fitting.py's arithmetic operation for operation (shared
helpers `_bgEdgeLevels`, `_bgAscending`, `_npLinspace`, `_bgCumFromHigh`,
`_bgShirleyMap`; `BG_REL_TOL`, `BG_MAX_ITER` = 200): bit-identical for the Shirley
family, and since Codex round 1 for every method: Tougaard's loss sum term for term
with numpy's pairwise summation, the linear background affine in energy and
extrapolated across the ROI through the window's end points as `run_fit` does (it was
drawn by index and flat-held: F8 closed). `shirleyLinearBackground` now mirrors the server's ascending copy (it skipped
it: 7.8 % of the span on a descending 5-point example) — otherwise the page's
certificate would fail every old Shirley + linear file on ordinary descending data
while the server certified it. `_bgCertificate` is the server's certificate (same
tests, reasons, tolerance). `computeBackgroundCore` returns the array marked
`converged` / `failure`; `_bgFailure(bg)` reads it and FAILS CLOSED: an unmarked
array (a stored or serialized curve) is not a certified background.
`_bgMaxAbsDiff` treats a NaN as infinite (it used to skip it and read a non-finite
step as "no change").

**Restored fits (Codex rounds 1-3, BLOCKER in each).** A fit loaded from a
project or a spectrum file carried its stored background, which no certificate had
ever seen. `_restoredFitBgFailure` recomputes the record's background from its raw
data (saved at full precision) under its saved settings and, for manual, its own
anchors (`_recordBackground`: the ROI selection `_roiSelect` that `getROIData` uses,
then `_computeBackgroundForSource`, the stack's Path B computation), certifies it, and
keeps the fit ONLY IF the stored curve
IS that certified background — equal exactly, or exactly as the save rounds it (6
significant figures, `_roundIntensity`); no tolerance. A kept fit then carries the
certified curve itself (grid and net signal with it). Otherwise — the settings give
no converged background, the curve was computed by an earlier version, the fit is
STALE (its method, window, averaging, ROI, anchors or charge shift changed after it
was fitted: the stored curve is the fit's, the settings are not), a stored value is
not a number (fails closed), or the fit stored no curve — the fit is dropped
(`fitResult` null, its support verdicts cleared), the model (the fitted peaks) kept,
and an amber notice names the tab and the reason. No method is exempt (round 3: an
exemption for manual / none read the CURRENT method, so a stale fit switched to
"none" before saving drew its old curve): manual is recomputed from the record's
anchors and none is zero, and each must equal what was stored. The spectrum-file
loader hands the check the grid and curve the file stores (round 3: it passed
neither, dropping every `.spec.json` fit); a STALE spectrum file is dropped outright,
because its stored curve is the edited state's (`_doSaveSpectrum` writes the live
one), not the fit's. A change of background settings after a fit already clears the
fit's frozen curve (`_invalidateBgCache`, unchanged), so such a save carries none.
CONSEQUENCE — an owner decision: a fit saved before this unit is restored only if
the curve it stored happens to equal today's certified background as the save rounds
it. Measured with the page's own function on the committed projects
(`scripts/bg_math_restore_census.py`, `data/impl/restore_census.json`): 121 spectrum
tabs carry a saved fit; **3 are restored** (`Cl2p_projfit_test`: Cl2p Scan, Scan_0,
Scan_1 — smart_exp at averaging 1, where the old 5-iteration curve already agrees
with today's to 6 significant figures); 62 stored a curve that differs (residuals
6.6e-8 to 6.0e-3 of the span, median 8.0e-5) and 56 stored none (saved before the
grid was persisted); those 118 load their model and need Run Fit. (Round 2's
"0 of 65, no older fit is restored" counted the strict certificate, not the restore
rule, which allows the save's rounding — Codex round 3.) The alternatives, not
implemented: keep an older fit with its statistics marked stale and the certified
curve drawn; or keep it as it was (round 1's policy, which both reviewers rejected).

**The "Shirley iterations" setting is retired.** A 5-iteration preview is not a
solution (F7: up to 8.6e-5 of the span from it), so under item 2 every page background
must run to convergence, as the server's always has. The field is hidden (kept: saved
files restore it and fit keys still compare it — removing it from the key would make
every saved fit stale on load) and never read.

**Item 6.** The amber notice for files that use Shirley + linear stays; its stated
reason ("its on-screen curve can differ from the background the backend fit actually
subtracts") is no longer true (the twin now mirrors the server), so it now says why the
method is off the menu: a reversed step no physical model gives.

## 2. Every consumer of a background (enumerated before review)

Server: `run_fit` (fit; the scattered starts and required refit reuse its background),
`compute_background_only` (`/api/background`), `autofit/engine._compute_background`
(Find Peaks, archived), `autofit/parity._background` — all through `compute_background`.

Page — every assignment of a computed background (`computeBackground`,
`computeBackgroundCore`, `_computeBackgroundForSource`) outside the dispatchers:

| site | on a non-converged background |
|---|---|
| `updatePlot` (preview) | red note under the method menu (`#bg-not-converged`, `_refreshBgConvergenceNote`); before a fit nothing is drawn or subtracted (peak previews on zero), the Bkgrd Sub view is off; after a fit the fit's frozen background stays drawn |
| `runFit` (+ "Use this solution") | refused before the undo entry, the spinner and any request: "Fit not run: <reason>"; no local fallback |
| `runAutoFitC1sGraphite` | refused in the preflight, before it claims the tab (a running Run Fit is left alone) |
| `applyAutoFitResult` | after the charge shift the window can hold other points: refused, the caller restores everything incl. the charge correction |
| `runPropagation` (Batch Fit) | that target is NOT fitted, with the reason |
| `handleChartClick` | the clicked height is the starting amplitude (nothing subtracted) |
| `_buildEntryRenderData` (stack, Path B) | the entry shows no fit |
| `_doSaveSpectrum` | `background: null`, no residuals or composed envelope, `backgroundFailure` |
| `exportResults` (TSV) | Background / BG-subtracted / Residual cells empty, WARNING line |
| `_doPublicationExport` | refused: "Figure not exported: <reason>" |
| `_loadProjectJSON`, `.spec.json` load | a restored fit whose stored curve is not the certified background now is dropped (model kept, notice) |
| `_restoredFitBgFailure`, `_buildEntryRenderData` | through `_recordBackground` |

THE CLASS IS CLOSED BY CONSTRUCTION (Codex round 3; rounds 1-3 each found a call form
past a guard that recognised each consumer's own refusal — an ignored assigned
failure, a check in a multi-line `if (false)`, an unrelated inline check). The three
producers a consumer can call — `computeBackground`, `_computeBackgroundForSource`,
`_recordBackground` — THROW `BgNotConverged` (`_certifiedBg`) instead of returning a
background that failed its statement, so a consumer that forgets to refuse ABORTS: it
cannot draw, subtract, fit, save or export the curve. Consumers refuse through
`_bgOrFailure(() => producer(...))` (`{bg, failure}`; any other error propagates) or a
`try` whose catch tests `_isBgNotConverged`; save, TSV and Batch Fit carry NaN, never
numbers, in place of a refused curve, behind their existing gates. What
`tests/js/background_not_converged.test.js` pins: (1) only the producers call
`computeBackgroundCore` (each through `_certifiedBg`) and only `computeBackgroundCore`
calls the method twins — no road to an unchecked curve; (2) the producers throw
(behavioural); (3) every consumer call is handled, so the student is told why rather
than the page aborting (this one is structural; it found runFit computing the
background a second time after its refusal, now reused). Mutation-verified: the
producer returning anyway, a direct `computeBackgroundCore` call in a consumer, an
unhandled producer call, the manual / none exemption restored, the `typeof` check
removed, manual substituted by Shirley or read from the active tab, and the record
path's own ROI loop each fail it.

## 3. Tests

- `tests/test_background_certificate.py` (10): all 121 committed spectra certify under
  every method; the cycles (F12), no net signal (F10), Tougaard undetermined /
  unsolvable / the all-zero flat (F11), Shirley + linear's equal edges fail; the
  certificate judges the statement, not the iteration; `run_fit` refuses; `/api/fit`
  422, `/api/fit/start` record 422, `/api/background` 422.
- `tests/test_background_defining_statements.py`: the findings tests turned into
  contracts — Shirley and Tougaard under the levels reading, the stop relative (the
  same relative answer at scale 1, 1e-6, 1e6), Smart solves its statement at every
  averaging, the stopped-short case now reaches its exact solution.
- `tests/js/background_parity.test.js`: bit-identity (Shirley family) / 1e-12
  (Tougaard), the certificate's verdict and reason page = server; twins at each
  iteration cap; Shirley + linear equal on both directions.
- `tests/js/background_not_converged.test.js` (12): only the producers reach
  `computeBackgroundCore` and the twins; every consumer call is handled; the producers
  throw; one ROI rule (`_roiSelect`) for the page and the record path; a record's
  manual background from its own anchors; the restore check (every method, a stale
  method or moved anchors, non-numbers, the save's rounding); the marker; the note;
  Run Fit's refusal order; Auto-Fit's preflight; the retired setting; the tooltips
  (F2) and Shirley + linear's menu state and notice.
- `tests/test_browser_background_not_converged.py`: real page, real server — the note,
  nothing drawn, Run Fit refused with no undo entry; an explicit background fits; a
  project saved with a fit on such a window reloads with the fit dropped, the model
  kept, the notice shown, and a stack entry built on it shows no fit; a fit saved by
  this version is restored; the same project with an older version's stored curve (a
  5-iteration Shirley) is not; a manual-background fit is restored, and one whose
  anchors moved or whose method changed after the fit is not; a spectrum file's
  current fit is restored, a stale one is not.
- `tests/js/manual_background_statement.test.js`: the page's manual background is
  np.interp's arithmetic, bit-identical to the server on 62 cases.
- Codex round 1's cases pinned: the stop / certificate boundary (two), Tougaard near
  cancellation on a near-uniform grid (both now the stated sum, page = server), an
  overflowing evaluation (not converged, page and server).
- `tests/js/_page_background_source.js`: the page's background section as one source
  for every JS test that runs it.
- JS CI floor 508 -> 529, exact (the owner's 512 for the two landed branches + this unit's 17 tests).

## 4. Measurements

(Re-run after Codex implementation round 1: every request now serialised exactly as
the page's `uploadToBackend` sends it — BE toFixed(4), intensity toFixed(2); "item 1
alone" is main's own algorithms with only the levels reading,
`scripts/bg_math_impl_item1_only.py`.)

Data and generators: `docs/findings/background-math/data/impl/` (JSONL per run, the
analyses, `background_level_by_averaging.txt`); `scripts/bg_math_impl_measure.py`
(the 202 committed targets through `/api/fit` as the page sends them — Trust-Region,
`n_perturb` 3 — and each target's net area on its own background window),
`scripts/bg_math_impl_seeded.py` (the same fits through `run_fit` with main's request
seed forced on the branch), `scripts/bg_math_impl_analyze.js`. Runs: `main` twice
(`main2`: Trust-Region's own press-to-press noise), `item1_only`, `both` (the branch as
shipped); each at the committed settings and with every target at endpoint averaging 3
(the page's default — 171 of the 202 committed fits were saved at 1, where item 1
changes nothing). Area % = the Results table's (the largest component change per
target, pp); at % = the Quantify tab's area/RSF with the page's own `_detectPeakRSF`.

**Background level — net area on each target's own window (%):**

| | median | max | > 1 % |
|---|---|---|---|
| item 1 alone, committed settings | 0 | 0.001 | 0 |
| item 3 (+ the certificate), committed settings | 0 | 0 | 0 |
| both, committed settings | 0 | 0.001 | 0 |
| both, every target at averaging 3 | 0.002 | 0.039 | 0 |

On the 121 reference spectra (main -> branch): at averaging 3 Shirley max 0.042 %,
Smart max 0.038 %, Smart (experimental) 0 (it already read the levels), Tougaard max
0.0005 %; at averaging 10 Shirley max 0.18 % (8 over 0.1 %), Smart max 0.11 %. So
small on the committed data because the averaged committed fits are Smart
(experimental) B 1s (unchanged) and Smart U 4f at averaging 6 on 322-point windows
with flat ends. No committed background is refused, at any averaging.

**Fits — the BACKGROUND's effect (main's request seed forced on the branch), 202 targets:**

| | area median | area max | > 1 pp | at % max | > 1 pp |
|---|---|---|---|---|---|
| committed settings | 0 | 0.022 | 0 | 0.046 | 0 |
| every target at averaging 3 | 0.002 | 0.36 | 0 | 0.36 | 0 |
| (Trust-Region's own noise, main vs main, committed / averaging 3) | 0 / 0 | 0.019 / 0.008 | 0 / 0 | 0.046 / 0.013 | 0 / 0 |

The largest, 0.36 pp at averaging 3, is 1-GTA C1s Scan_4 (Graphite; chi2r 19.708 ->
19.695). At the committed settings the background's effect is at the noise floor.

**Fits — AS SHIPPED (through /api/fit, the branch's own request seed):**

| | area median | area max | > 1 pp | at % max | > 1 pp |
|---|---|---|---|---|---|
| item 1 alone, committed | 0 | 0.003 | 0 | 0.003 | 0 |
| both, committed | 0 | 28.4 | 5 | 29.4 | 6 |
| item 1 alone, averaging 3 | 0.002 | 21.1 | 1 | 21.7 | 1 |
| both, averaging 3 | 0.002 | 23.0 | 3 | 23.8 | 3 |

Every move over 1 pp is the REQUEST SEED, not the background's shape: the seed hashes
the computed background, so a change as small as the stop's (~1e-7 of the span)
redraws the three perturbed restarts, and on a several-minima target they land in
another basin; with main's seed forced each reproduces main to <= 0.022 pp (table
above). All are 8-JT Graphite C 1s scans (the known several-minima project; A2 found
Scan_5 landing at 33.9 or 51.9 by memory alignment) except one atomic-% move:

| target | settings | main chi2r -> branch | area pp |
|---|---|---|---|
| 8-JT C1s Scan_8 | committed | 35.55 -> 32.35 (better) | 28.4 |
| 8-JT C1s Scan_6 (Adventitious 2) | committed | 38.31 -> 70.61 (worse) | 21.6 |
| 8-JT C1s Scan_7 | committed | 35.77 -> 64.17 (worse) | 21.1 |
| 8-JT C1s Scan_5 | committed | 17.26 -> 33.90 (worse) | 17.5 |
| 8-JT C1s Scan_6 (other copy) | committed | 8.539 -> 8.545 (level) | 2.7 |
| B4C-UCl4 U4f Scan_7 | committed | 2.773 -> 2.933 | 0.6 (at % 2.2) |
| 8-JT C1s Scan_6 (Adventitious 1) | averaging 3 | 70.94 -> 18.53 (better) | 23.0 |
| 8-JT C1s Scan_5 | averaging 3 | 33.86 -> 51.70 (worse) | 22.0 |
| 8-JT C1s Scan_6 (other copy) | averaging 3 | 8.552 -> 8.539 (level) | 2.5 |

The direction is a lottery: of the eight 8-JT moves over 1 pp (five at the committed
settings, three at averaging 3), two end better, four worse, two level. It is the pre-existing basin sensitivity of these targets (CLAUDE.md
"Reproducibility": any change of the computed background redraws the restarts), made
visible here because the background changed; the scattered-starts check is the
mitigation that already ships. No fit lost or gained convergence.

**Item 5 (F3) — smart vs smart_exp after item 1:** bit-identical on all 376 committed
spectrum x averaging cases (each spectrum at its own averaging and at 1, 3, 10); on
40 000 random small spectra the same converged / not-converged verdict every time,
37 902 of 39 408 converged pairs bit-identical, the rest within 3.5e-12 of the span —
the stop tolerance, as the argument predicts (with the clamp identity exact, the
projected iterates ARE the clamped Shirley iterates, P_k = min(B_k, I) for k >= 1; the
projected iteration's steps are never larger, so it can stop a step earlier). Far
within fit_equality.py's rounding (1e-3 of each quantity's own scale). PROPOSAL (not
implemented): one menu entry "Smart (constrained Shirley)"; `smart_exp` kept as a
backend id and in the saved-file loader, mapped to the same computation, so old files
load and fit as before (whether a file saved as `smart_exp` re-saves as `smart` or
keeps its id: an owner choice).

**F13 (new): featureless windows.** On 300-point synthetic Poisson windows with no
peak the Shirley family is not converged on 200 / 200 linear drifts, 185–186 / 200
peakless steps, 6 / 200 pure-noise windows (mostly alternation; the checker's
independent reference solver does not converge either); 0 / 200 with a peak or a
spike; Tougaard never. Until now those windows got a non-solution silently; now a
student who selects a window without a peak gets the message and no fit. Two Find
Peaks tests on such inputs accept the refusal (nothing seeded, nothing emitted).

**Other number changes:** the C 1s parity battery's frozen fixture regenerated — only
8-JT C1s Scan_6 moved materially (chi2r 1.5e-4 relative; parameters up to 25 %
relative on its near-zero component: the flat valley the battery already lists as
NOT_CERTIFIED); the other 28 records within 2.6e-10 (chi2r) and 5.4e-5 (parameters).
The page now draws every background at convergence (it stopped at the 5-iteration
setting: up to 8.6e-5 of the span, F7), draws de-listed Shirley + linear files as the
server computes them (up to 7.8 % of the span on descending grids before), draws the
linear background affine in energy and extrapolated across the ROI (by index and
flat-held before), and Tougaard on near-uniform grids as the stated sum (both sides).

## 5. Release note (at deploy)

Backgrounds: endpoint averaging now sets only the two edge levels the background is
anchored to; the background itself is computed from the measured data, the same way
for every method (Shirley, Smart and Tougaard used to replace the end points of the
data by their average). Every background is checked against its own defining
equation; when it has no solution — most often a window with no peak in it — the page
says "… background not converged" under the method menu and nothing is fitted,
subtracted or exported against it. A saved fit is restored only when the background
it was fitted against is today's (as the file stores it) — so most fits saved before
this version are not restored (on the lab's committed projects 3 of 121 are): their
models load, and Run Fit regenerates them. Every background now runs to convergence; the "Shirley
iterations" setting is gone. The page now draws exactly the background the server fits
(the linear background affine in energy, as the server always had it). On the
committed fits the backgrounds moved by at most 0.04 % of net area (at averaging 3) and
the fitted areas by at most 0.4 pp for the background's sake — but a changed background
also re-draws the fit's perturbed restarts, so a fit that sits between two solutions
can land in the other: on the 8-JT C 1s scans eight such moves of 2–28 pp, two to a
better fit, four worse, two level. The Smart tooltips now say that constraining against noisy
counts raises net area by about 1 %.

## 6. Codex rounds

**Round 1 — NO-GO ×2** (`docs/autofit/codex/background_math_impl_r1_verdict_run{A,B}.md`,
commit 0571228; both: all four analysis summaries reproduce; the 376 committed
smart / smart_exp pairs bit-identical):

| # | finding | fix |
|---|---|---|
| 1 | BLOCKER (A, B): a restored fit's stored background bypassed the certificate (preview, stack Path A/A2, saves); `_bgFailure` treated an unmarked array as converged | restored fits are dropped when their settings give no converged background now (model kept, notice); `_bgFailure` fails closed; browser lifecycle test |
| 2 | MAJOR (A, B): Tougaard certified its near-uniform APPROXIMATION of the sum (16 % of the span from the page's exact sum; opposite verdicts on another case) | the stated sum on every grid, server and page bit-identical (pairwise summation); both cases pinned |
| 3 | MAJOR (A): the page's linear background (by index) was certified though it is not the statement's curve | affine in energy, extrapolated across the ROI as `run_fit` does; bit-identical to the server, F8 closed |
| 4 | MAJOR (A, B): "item 1 alone" kept the branch's return-before-update rule (a 1e-7 background change at averaging 1 that redraws the seed) | `scripts/bg_math_impl_item1_only.py`: main's own algorithms with only the levels reading; equal to main at averaging 1 except np.convolve's own non-reproducible last bit (2.3e-13, one spectrum) |
| 5 | MAJOR (B): the harnesses sent intensities at 4 dp, the page sends 2 (different request seeds) | both harnesses serialise exactly as `uploadToBackend` (toFixed(4), toFixed(2)); every measurement re-run |
| 6 | MINOR (A, B): stop and certificate disagreed at the tolerance boundary | one predicate, diff <= tol x span, server and page; pinned |
| 7 | MINOR (A, B): the class guard could be evaded and did not check order | every producer reference must be one of two forms; first use after assignment must be the check; mutation-verified |
| 8 | MINOR (B): a NaN in the page's maximum difference was skipped (an overflowing case certified) | NaN is infinite; non-finite targets fail; pinned |

**Round 2 — NO-GO ×2** (`background_math_impl_r2_verdict_run{A,B}.md`, commit cf64e80;
both: all four analysis summaries reproduce, incl. the seeded maxima and the two
better / four worse / two level classification; serialisation matches the page on all
202 targets; 2 160 further comparisons (A) bit-identical with identical verdicts):

| # | finding | fix |
|---|---|---|
| 1 | BLOCKER (A, B): a restored fit was kept when a NEW background converged, and its OLD stored curve was drawn uncertified (2.4e-6 and 0.26 % of the span on two examples) | the stored curve must BE the certified background (exactly, or exactly as the save rounds it); otherwise the fit is dropped. 0 of 65 committed saved fits pass: no older fit is restored — an owner decision (§1) [CORRECTED in round 3: 3 of 121 are restored] |
| 2 | MAJOR (A, B): the restore check reused the stack helper that substitutes Shirley for manual, dropping valid manual fits | manual is accepted as the user's curve; browser test |
| 3 | MINOR (A, B): the guard accepted a check inside `if (false)` and consumption on the assignment line | the assignment must end at the call; the check must be a refusal statement; mutation-verified |
| 4 | MINOR (A, B): "every method bit-identical" was false for manual (one rounding step) | the page's manual background is np.interp's arithmetic; pinned bit-identical |

**Round 3 — NO-GO ×2** (`background_math_impl_r3_verdict_run{A,B}.md`, commit 056a3ce;
both: all four measurement summaries reproduce, the 376 smart / smart_exp pairs
bit-identical; B: 36 current-project round trips kept):

| # | finding | fix |
|---|---|---|
| 1 | BLOCKER (A): the manual / none exemption read the CURRENT method — a stale fit switched to "none" before saving drew its old, uncertified curve | no exemption: manual from the record's own anchors, none = zero, each must equal the stored curve; browser test (anchors moved, method changed) |
| 2 | MAJOR (A, B): the spectrum-file loader passed neither the stored grid nor the curve, so every `.spec.json` fit was dropped; a manual source's stack reconstructed Shirley | the loader passes `roiBE` / `background`; a stale spectrum file is dropped outright (its curve is the edited state's); `_computeBackgroundForSource` takes the record's anchors; browser round trip |
| 3 | MAJOR (A, B): the record path selected other ROI points than `getROIData` (both bounds required; descending grids assumed) | one rule, `_roiSelect`, used by both; pinned on descending and ascending grids, one blank bound, a bad field, a charge shift |
| 4 | MAJOR (A): a non-number stored value made the comparison NaN and the check failed open | fails closed: anything that is not this number (or as saved) is a mismatch; pinned for string, null, undefined |
| 5 | MINOR (A, B): the guard still accepted an ignored failure, a check in a multi-line `if (false)`, an unrelated inline check | the class closed by construction: producers throw (§2); mutation-verified |
| 6 | MINOR (A, B): "no older saved fit is restored" was false (3 committed Cl 2p fits pass the rounding rule; a constructed case too) | measured with the page's function: 3 of 121 restored, 62 differ, 56 stored no curve (§1); release note and CLAUDE.md corrected |
