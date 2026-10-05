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
SUPERSEDED 2026-10-03 by the owner's restore rule (§7): the evidence is the background
the fit USED (envelope less peaks), within 1e-3 of its scale — 10 current, 71 reloaded
stale, 40 peaks only (after Codex round 18, §7.5).

**The "Shirley iterations" setting is retired.** A 5-iteration preview is not a
solution (F7: up to 8.6e-5 of the span from it), so under item 2 every page background
must run to convergence, as the server's always has. The field is hidden (kept: saved
files restore it and fit keys still compare it — removing it from the key would make
every saved fit stale on load) and never read.

**Explicit backgrounds must exist; short records; file order (Codex rounds 4-5).**
Linear, manual and none are "explicit — nothing to converge", but each is a curve
that must EXIST, and that is now checked like every other statement, server and page,
in the same words: linear (and manual with fewer than two anchors, the line through
the ROI's ends) has no line when the window's end points share an energy and not an
intensity (`fitting._line_through` / `_bgLineFailure`); manual has no curve when two
anchors share an energy and not an intensity (`fitting.manual_anchor_background` /
`_bgAnchorFailure`); and every value must be a finite number — finite inputs can
overflow (a slope over a 1e-309 eV window, intensities near 1e308)
(`fitting._explicit_background`; on the page `computeBackgroundCore` checks the
result of every method, `_computeBackgroundUnchecked` computes it). The flat first
intensity, an interpolation between conflicting anchors and NaN / ±Infinity used to
be drawn and fitted against; ordinary windows are bit-for-bit unchanged. The parity
reference `autofit/parity.background_like_run_fit` uses `_line_through` too. A
restored fit whose raw data are missing or incomplete is dropped (the certificate
needs them). The spectrum-file loader keeps the FILE's point order, as the project
loader does (round 4 re-sorted the fit's arrays to `createTab`'s BE-descending order;
round 5 showed re-ordering is not neutral — repeated energies integrate in another
order, 0.7-12 % of the span, and a line's arithmetic rounds differently — so a
current fit was still dropped).

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
  bit-identical to the server's — since round 10 both the exact piecewise-affine value
  rounded once (half to even) — on ~100 cases incl. far / huge anchors, subnormals,
  exact ties and random magnitudes from 1e-300 to 1e308.
- Codex round 1's cases pinned: the stop / certificate boundary (two), Tougaard near
  cancellation on a near-uniform grid (both now the stated sum, page = server), an
  overflowing evaluation (not converged, page and server).
- `tests/js/_page_background_source.js`: the page's background section as one source
  for every JS test that runs it.
- JS CI floor 508 -> 543, exact (the owner's 512 for the two landed branches + this unit's tests; 538 before the owner round of 2026-10-03, 539 at its first commit, 543 after Codex round 18).

## 4. Measurements

(STILL CURRENT at the final commit, checked after round 17: on the 202 targets, each at
its own method and at its committed averaging and at 3 — 404 cases — every background is
bit-identical to the measured commit cf64e80 and none is refused; the request seed hashes
the computed background, so the fits below are the final commit's fits. Re-run after
Codex implementation round 1: every request now serialised exactly as
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

**The page's and the server's readings of the data (Codex round 9, A2 — measured, held
for the owner).** The page computes its background on the raw counts; the server on
the counts as `uploadToBackend` sends them (BE toFixed(4), intensity toFixed(2)); Run
Fit freezes the page's curve beside the server's envelope. On the 202 committed
targets × shirley / smart / smart_exp / tougaard × averaging 1 / 3 / 10 (2 424 cases,
`scripts/bg_math_upload_rounding_gap.py`, `data/impl/upload_rounding_gap.json`): the
two backgrounds differ by at most 8.6e-7 of the span (median 8.0e-8, 99th percentile
7.7e-7) and their verdicts agree on every case. A large gap needs an ill-conditioned
input (Tougaard near cancellation, a constructed four-point case in the review: 1001.5
vs 369.6). The class fix is to upload at full precision (one reading, page = server bit
for bit, the frozen pair consistent by construction); it changes every fit's input by
up to 0.005 counts and with it every request seed (the perturbed-restart lottery of §4
again), so it is an OWNER DECISION, not made here.

**Auto-Fit's result after its charge shift (Codex round 9, A1 — pre-existing, logged).**
Auto-Fit refines the charge shift after the fit; the shift rounds the ROI and
background bounds to 0.1 eV (`updateChargeCorrection`), so the window can then select
other samples, and the result is assembled from the NEW selection with the server's
`fitted_y` for the OLD one (an R of 18.6 % instead of 0.02 % on the review's case). The
background on the new selection is certified; the pairing of samples and envelope is
main's (unchanged since before this unit) and is a statistics problem of Auto-Fit, not a
background that misses its statement. Logged for its own unit (options: move the bounds
by exactly the shift, freeze the fitted samples, or refit after the shift) with the
other Auto-Fit items in CLAUDE.md's "LOGGED FOR ONE LATER UNIT".

## 5. Release note (at deploy)

(Rewritten for the owner round of 2026-10-03, §7.)

Backgrounds: endpoint averaging now sets only the two edge levels the background is
anchored to; the background itself is computed from the measured data, the same way
for every method (Shirley, Smart and Tougaard used to replace the end points of the
data by their average), and the Linear background now uses the same averaged edge
levels. Every background is checked against its own defining equation; when it has no
solution — most often a window with no peak in it — the page says "… background not
converged" under the method menu, suggests the Linear background for a window with no
peak, and nothing is fitted, subtracted or exported against it. Every background runs
to convergence; the "Shirley iterations" setting is gone. "Smart" and "Smart
(experimental)" were the same calculation and are now one menu entry ("Smart"); files
that use either still load. The page now draws exactly the background the server fits,
and sends the server your data at full precision (it used to round intensities to two
decimals).

Saved fits: a saved fit reloads as it was when the background it was fitted against —
its stored fitted curve less its peaks — equals the background its settings give today
within rounding. When it differs, the fit still loads with its own background and
peaks, but its statistics (χ², R-factor, RMSE, uncertainties) are marked out of date and
are not shown or exported, with the size of the difference; Run Fit brings it up to
date. On the lab's 121 committed saved fits: 10 reload as they were; 71 reload marked
out of date — 66 because their background differs (most by under 1 % of its own scale,
at most 5 %, nearly all because older versions chose the background window's end points
differently), and 41 because they hold a Voigt component fitted before 2026-09-22 with a
G/L mix the page does not draw (the page draws a Voigt at 50/50; 5 of these for that
reason alone); and 40 — saved by older versions without the fitted curve or the energies
it was fitted on — load their peaks only.

Fits: the random restarts are now drawn from a seed computed from your data, window,
settings and model rather than from the computed background, so they no longer change
when a background's arithmetic changes in the last digit; this unit changes them once.
On the committed fits the backgrounds moved by at most 0.001 % of net area; six fits
that sit between two solutions landed in another (1–29 pp of area or atomic %: one to a
better fit, four worse, one level). The "scattered starts" line under the Results table
flags four of them; on the other two every scattered start reaches the returned
solution (one of them 21 % worse in χ²ᵣ than the previous version's). The Smart tooltips say that constraining against noisy counts
raises net area by about 1 %.

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

**Round 4 — NO-GO ×2** (`background_math_impl_r4_verdict_run{A,B}.md`, commit b03344c;
both: the census reproduces exactly — 3 restored, 62 differing, 56 without curves —
and the owner consequence is accurately stated; the four measurement summaries and
the 376 smart / smart_exp pairs reproduce; B: 512 project round trips kept):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A): linear certified an impossible line — window ends at one energy, different intensities — and the server fitted against the flat first intensity | `fitting._line_through` raises, the page's `_bgLineFailure` refuses, same words (also manual with < 2 anchors); ordinary windows bit-for-bit unchanged; pinned both sides |
| 2 | MAJOR (A, B): a record with missing / short raw data skipped the restore check and drew its stored curve | dropped: "its raw data are missing or incomplete"; pinned (one point, empty, absent, unequal lengths) |
| 3 | MAJOR (A, B): an ascending spectrum file's current fit was dropped (createTab sorts the raw data; the fit's arrays were left in file order) | grid, background and fitted curve put in createTab's order (stable descending); browser test on the reversed file, point for point |

**Round 5 — NO-GO ×2** (`background_math_impl_r5_verdict_run{A,B}.md`, commit dd1259a;
both: the census (3 / 62 / 56), the four measurement summaries and the smart /
smart_exp identity reproduce; A: 128 further project round trips kept):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B): conflicting manual anchors (two at one energy, different intensities) certified an impossible curve; `run_fit` fitted against it | refused, server and page, same words; agreeing duplicates still fit |
| 2 | MAJOR (A, B): ascending spectrum files with repeated energies (and a linear rounding case) still lost current fits — re-ordering is not neutral | the loader keeps the file's order (round 4's re-ordering removed); browser test with repeated energies |
| 3 | MINOR (A, B): explicit backgrounds could overflow to NaN / ±Infinity and be certified | every result must be finite (`_explicit_background`; the page's `computeBackgroundCore` wraps every method); pinned on both overflow cases |
| 4 | MINOR (A, B): the parity reference kept the impossible-line fallback | it uses `_line_through`; pinned |
| 5 | MINOR (A, B): the "same words" differed in number formatting (1e-05 vs 0.00001) | the messages carry no formatted number; pinned equal strings both sides |

Found in my own pre-review after the round-5 fixes, fixed with them: an anchor that is
not a pair of finite numbers (NaN, Infinity, a string, null, a bool, a missing
coordinate) is refused on both sides in the same words — a NaN anchor could
interpolate to finite values and pass the finiteness check, and a string anchor
("2") was read as a number by the server and refused by the page; and the page's
interpolation now follows numpy's `arr_interp` on its edge branches (an anchor energy
returns its intensity; a NaN from an overflowing slope is recomputed from the
right-hand anchor), so the finiteness verdicts agree too — pinned bit-identical,
NaN / Infinity included, on five such cases.

Mutation-verified (11 of 11 killed): the page's finiteness check, its anchor checks
(conflict, validity), the loader's order, the server's finiteness and anchor checks,
the parity fallback, the page's two numpy edge branches, the round-4 linear refusals.

**Round 6 — NO-GO ×2** (`background_math_impl_r6_verdict_run{A,B}.md`, commit 65da2c7;
both: the census, the four measurement summaries and the smart / smart_exp identity
reproduce):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B): an UNSORTED window (the spectrum loader keeps a file's order since round 5; a project always did) — the integral backgrounds integrated the array order and their certificate agreed: Shirley above both edge levels, Tougaard summing a higher-energy point as a lower one; `run_fit` fitted, stacks drew | the integral relations are integrals along the energy axis: the certificate requires finite data and a window in order (ascending or descending, repeats allowed), server and page, same words; committed data unchanged (census 3 / 62 / 56 again) |
| 2 | MAJOR (A, B): a stack aligned raw counts to the fit grid by a contiguous slice from the nearest start — wrong samples on an unsorted record (a background-subtracted trace of 20-50 where it is 0) | `_alignRawToFitBe` matches the fit grid point for point as `_roiSelect` selected it (exactly or as saved, 4 dp); the old slice only when the charge shift changed since |
| 3 | MAJOR (B): a manual fit with no `manual_bg` sent (or `/api/background` manual) silently used zeros | the fewer-than-two-anchors case: the line through the window's ends, as the page (the page always sends the array — its requests unchanged) |
| 4 | MAJOR (B): an overflowing span / difference certified a non-solution (inf <= tol · inf) | a non-finite span or difference does not certify, server and page, same words |
| 5 | MINOR (B): a lone invalid anchor took the fallback silently; `[null, …]` raised TypeError on the server | every anchor given is checked, even a lone one; a non-list entry is refused in the same words |
| 6 | MINOR (A, B): manual-fallback overflow said "Manual" on the page, "Linear" on the server | the page's fallback is the server's line with its words |

Also: the certificate's residual is written with a JS twin of Python's `%.3g`
(`_pyG3`; round 7 replaced both with `_fmt3`, below), so "misses the relation by 1.23e-05 %" reads the same on both sides; a
new test compares verdict AND words page = server across every refusal kind (order,
overflow, cycling, no net signal, NaN data, linear, manual) by running the server.
Mutation-verified (12 of 12 killed).

**Round 7 — NO-GO ×2** (`background_math_impl_r7_verdict_run{A,B}.md`, commit 11733d8;
both: the census, the four measurement summaries and the smart / smart_exp identity
reproduce; A: 216 grid-pathology parity cases agree):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (B): a sorted background window inside an UNSORTED fitted region — the integral background is held flat beyond its window by array position, so the high-BE side took the low-edge level; `run_fit` fitted | an integral background needs the whole fitted region in order (`fitting._region_in_order`, in `run_fit` and the parity reference; the page's `computeBackgroundCore`), same words; a line is affine in energy and still fits |
| 2 | MAJOR (A, B): the stack's rounded (4 dp) point match let an excluded neighbour 1e-5 / 5e-5 eV away stand in for a selected point (net 890 where it is 0) | the alignment takes the ROI selection itself when it reproduces the fit grid (sample identity kept), otherwise an EXACT point-for-point match, never a rounded one |
| 3 | MAJOR (A): a one-point ROI under manual with no anchors gave 0 on the page, the point on the server | the page's line through one point is that point (as `linear_background`) |
| 4 | MINOR (A, B): the residual text differed on exact binary ties (12.25: '12.3' page, '12.2' server — %.3g rounds ties to even) | one definition both compute exactly: three significant digits rounded half up on the exact value (`fitting._fmt3` via Decimal; the page's `_fmt3` via toExponential / toFixed); pinned on 29 values incl. ties |

Mutation-verified (7 of 7 killed).

**Round 8 — NO-GO ×2** (`background_math_impl_r8_verdict_run{A,B}.md`, commit b4c5e25;
both: the census, the four measurement summaries and the smart / smart_exp identity
reproduce; `_fmt3` page = server on 104 207 (A) and 29 988 (B) random finite doubles;
A: 256 loader round trips):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B): after the charge shift changed (or a history restore), a stack re-derived the frozen fit grid's raw counts from the CURRENT shift and subtracted the background from other samples | Path A takes the fit's own frozen counts (`bgSubtracted` + the frozen background, as `updatePlot` draws them); the alignment only for a result without them; browser test with an interior ROI (at the data's edge the old slice lands right by coincidence) |
| 2 | MINOR (A, B): an empty linear / manual window on `/api/background` raised IndexError (HTTP 500) | an empty window is an empty curve, as the page |

Mutation-verified (2 of 2 killed).

**Round 9 — NO-GO ×2** (`background_math_impl_r9_verdict_run{A,B}.md`, commit 530513f;
both: the round-8 fixes hold; the census, the four measurement summaries and the
smart / smart_exp identity reproduce; A: 128 loader round trips; B: 192 record round
trips / frozen-stack cases):

| # | finding | disposition |
|---|---|---|
| 1 | MAJOR (B): manual anchors whose gap overflows (±1e308): np.interp's slope is 0 and the curve a finite, wrong 0 — certified, fitted, saved | refused, server and page, same words: anchor and intensity gaps and every x − anchor must be finite; pinned, page = server [SUPERSEDED in round 10: evaluated exactly instead, which gives these anchors their true line] |
| 2 | MAJOR (A): Auto-Fit assembles its result from the post-shift selection with the pre-shift envelope | PRE-EXISTING (main assembles it so), a statistics problem, not a background that misses its statement — logged for its own unit (§4); not fixed here |
| 3 | MAJOR (A): Run Fit freezes the page's background (raw counts) beside the server's envelope (2-dp counts); on an ill-conditioned constructed Tougaard case they differ by most of the span | PRE-EXISTING reading gap (documented since W1); MEASURED on the committed data: ≤ 8.6e-7 of the span, verdicts agree on all 2 424 cases (§4); the class fix (full-precision upload) changes every fit's input and seed — OWNER DECISION |
| 4 | MINOR (A): the parity reference kept manual's zero fallback | the line through the ROI's ends, as run_fit; pinned |

Mutation-verified (3 of 3 killed).

**Round 10 — NO-GO ×2** (`background_math_impl_r10_verdict_run{A,B}.md`, commit ad80814;
both: the round-9 refusal works; the census, the four measurement summaries, the
smart / smart_exp identity and the upload-rounding measurement (8.59e-7, 2 424 matching
verdicts) reproduce; the two dispositioned pre-existing items not re-raised; A: 900
numerical parity probes, 96 loader round trips; B: 64 loader round trips):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B): manual anchors at -1e20 eV against data at 280 eV — np.interp's formula loses the offsets and cancels to a finite, wrong 0 (the line is 80..90 / 21..11); every intermediate finite, so round 9's overflow checks pass; certified, saved, fitted | the CLASS, not another edge: the manual curve is the exact piecewise-affine value through the anchors, rounded once to the nearest double, half to even — `Fraction` on the server (`float()` rounds correctly), `BigInt` on the page (`_bgExact`, `_bgRatToDouble`); no tolerance, no overflow possible (a convex combination of finite values), page = server bit for bit (pinned on ~100 cases: far and huge anchors, subnormals, exact ties, random magnitudes 1e-300..1e308). Round 9's gap / overflow refusal is withdrawn: those anchors now give their true line. Ordinary anchors move by at most an ulp from np.interp; no committed target uses a manual background, so no measured number changes |

Cost (i9, 4 000 points × 12 anchors — larger than any committed window): 0.055 s on
the server, 0.035 s per evaluation on the page (a few ms on a typical few-hundred-point
window; the page re-evaluates on each redraw in manual mode).

Mutation-verified (3 of 3 killed): ties rounded up, the floating-point formula on the
page, np.interp on the server.

**Round 11 — NO-GO ×2** (`background_math_impl_r11_verdict_run{A,B}.md`, commit 60025c7;
both: the round-10 manual evaluator holds — A: 10 006 exact-double, 12 890
rational-rounding and 44 871 page = server values; B: 15 000 values, 5 006
decompositions, 13 392 rounding probes incl. ties around every finite power of two; 4 000
points × 12 anchors 29-36 ms page / 67 ms server; the census, the four measurement
summaries, the smart / smart_exp identity and the upload-rounding measurement
reproduce):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B): the LINEAR background (and manual with fewer than two anchors) beside a 1e20 end point: y0 + slope (x − x0) cancelled to a finite, wrong 0 (the line is 60..50 / 21..11); certified, saved, restored, fitted | the same class fix as round 10: the line through the window's ends evaluated exactly — (y0 (x1 − x) + y1 (x − x0)) / (x1 − x0) in Fraction / BigInt — rounded once (`fitting._line_through`, the page's `_bgExactLine`, used by the linear branch and the manual fallback); the round-5 "overflow" cases now give their true line; only an extrapolation past the largest double is not finite (refused). `_bgRatToDouble` takes either sign of denominator (a descending grid; the parity test found it). Ordinary windows within an ulp of the old formula; no committed target uses linear |

The full suite then found the synthetic two-basin fixture of
`tests/test_scattered_starts.py` (shared by `test_fit_equality.py` and
`test_runfit_certificate.py`) CHAOTIC IN THE LAST BIT of its input: the exact line
differs from the old formula by one ulp at 3 of its 300 points, and that moves
Levenberg-Marquardt's stall (chi2r ~286, not a minimum), the basin the certificate and the
scattered starts reach, and puts Trust-Region's alignment-dependent continuation on a
basin boundary (identical requests differed run to run: 6 tests, 2 of them flaky). Those
modules test the starts / certificate / equality machinery on a FIXED input, so they pin
the background arithmetic the model was found with (`tests/_legacy_line.py`, an autouse
fixture: the old floating-point line); the exact line is pinned by its own tests. 75 of
75 pass, three runs in a row. The sensitivity itself is the accepted, disclosed property
(CLAUDE.md, Reproducibility: near a basin boundary a rounding step decides the basin).
OWNER (2026-10-01): the pin is accepted as a stopgap — the background is incidental
there and the exact line keeps its own tests; the round-12 review is asked whether the
pin hides a real change; the follow-up (a fixture clearly inside one basin, the pin
removed, boundary behaviour given its own deliberate test if wanted) is logged in
`docs/autofit/PROGRESS.md` "LOGGED — follow-up units".

Mutation-verified (3 of 3 killed): the floating-point line on either side, the
denominator sign.

**Round 12 — A: GO; B: NO-GO** (`background_math_impl_r12_verdict_run{A,B}.md`, commit
b3fce06; both: the exact line holds — A: 2 175, B: 1 802 page = server cases incl.
descending grids, extrapolation, signed zeros, subnormals; 4 000 points ~22 ms page /
27-29 ms server; the census, the measurements, the smart / smart_exp identity and the
upload-rounding measurement reproduce):

| # | finding | disposition |
|---|---|---|
| 1 | MAJOR (B): Tougaard at energies near 1e80 — `u·u` overflows, real kernel terms become silent zeros, the curve misses the stated sum by 99.99999 % of the span; certified, saved, restored | an overflowing intermediate (u·u, B·T, a term) makes that loss sum NaN, server and page, and the background is refused as not finite (same words); ordinary sums untouched, bit for bit (the parity suite) |
| 2 | (B, same finding): Tougaard on intensities near 1e20 — the anchoring rounds, the high edge is 16384 where the exact relation gives 50 | NOT CHANGED, measured: 8e-17 of the window's span, inside the certificate's predicate (BG_REL_TOL = 1e-12 of the span) by which every certified background is judged; pinned against an EXACT Fraction evaluation of the stated relation, both directions. The closed-form explicit curves (line, manual) are evaluated exactly because that is cheap; Tougaard's loss sum is O(n²) — in rationals too slow for the page's redraw — and is certified, like the iterative methods, by the span-relative predicate |
| 3 | MINOR (A) / note (B): the `_legacy_line` pin masks changed basin outcomes — unpinned, 3 tests fail (A: pure-function / curve-height / >1 eV continuation; B: centres-scaled / reconstruction / >1 eV continuation), 11 more are susceptible (A's list) | both: the pin is HONEST as the owner-accepted stopgap, the failures are the disclosed basin sensitivity, not a background defect; the lists are added to the PROGRESS.md follow-up (which tests the new fixture must re-establish) |

Mutation-verified (2 of 2 killed).

**Round 13 — NO-GO (A); B: no verdict (model capacity), B2: NO-GO**
(`background_math_impl_r13_verdict_run{A,B,B2}.md`, commit 81234c4; A and B2 reproduce the
census, the four measurement summaries, the smart / smart_exp identity and the
upload-rounding measurement; the round-12 overflow refusal holds):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B2): Tougaard on ordinary-looking data whose high-edge loss sum nearly cancels (A: `[200, 300, 0.73, 300]`, 278 000 × the predicate; B2: `[2, 3, 0.0072794, 3]`, 0.6 % of the span) — the anchoring amplifies rounding; the certificate accepted any nonzero high-edge sum | the curve is closed-form, so its only error is rounding: it is certified only if a first-order RIGOROUS rounding bound (`fitting._tougaard_rounding_bound`, the page's `_tougaardRoundingBound`, operation for operation; per-term and summation-tree roundings, the edge means' rounding through the net, the anchoring) meets the predicate; otherwise "the loss sum at the high-BE edge nearly cancels…". Measured on the committed targets × averaging 1 / 3 (404 cases): the bound is at most 0.035 of the predicate (median 0.002; 0.043 after round 14's revision) — no committed verdict changes; A's case: 4.2e6 × |
| 2 | MAJOR (A, B2): the Shirley-family certificate re-did the iteration's arithmetic, so it confirmed its rounding — 1e12 ± 8 counts (A: residual 6.6e-7, predicate 8e-12, rounded to 0) and 1e-200 counts (B2: underflow, 25 % of the span), Shirley + linear too | the residual of the RETURNED curve is computed EXACTLY — exact edge means, exact trapezoids, exact map, `Fraction` on the server (`_exact_shirley_certificate`), BigInt integers over one common denominator on the page (`_bgExactShirleyCertificate`), the predicate decided by an integer comparison; page = server verdicts AND words on the full parity sweep. Measured on the committed targets (`scripts/bg_math_exact_certificate_margin.py`, 202 × 3 methods × averaging 1 / 3 = 1 212 cases): the same verdict on every case, the exact residual at most 0.993 of the predicate (median 0.31); every committed window sits ≥ 3 000 × inside double precision's resolution of the predicate (eps · max|I| / (tol · span) ≤ 3.2e-4). The reason no longer says the iteration "did not settle" (it may have, at double precision): "the result misses the … relation by X % of the intensity span (its iteration alternates or ran out of steps, or the data exceed what double precision resolves at this span)" |

A consequence, by decision: the iteration still STOPS on its float criterion and the
certificate now JUDGES exactly, so a background constructed at the float boundary (Codex
round 1's two cases) is refused by a hair (the exact residual 1e-10 % of the span, over
the 1e-10 % predicate) — the verdict is the statement's. Cost on the page, 400 points:
2-3 ms per Shirley / Smart background with its certificate, 9 ms for Tougaard.

Mutation-verified (4 of 4 killed): the bound bypassed and the exact check replaced, on
each side.

**Round 14 — NO-GO ×2** (`background_math_impl_r14_verdict_run{A,B}.md`, commit d4aca1a;
both: the 1 212-case exact margin, the measurements, the census and the upload-rounding
comparison reproduce; all 404 committed Tougaard windows below the bound; no committed
refusal):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B): the Tougaard bound's OWN arithmetic underflowed on 1e-110 / 1e-120-count data — `D·|L|·(dL0 + dc·W0)` became 0 and the bound dropped the error it bounds (2.6-9.7 × the predicate, certified) | Tougaard is computed — and the certificate judges it — on the intensities scaled by an exact power of two to max|I| in [0.5, 1) and scaled back (`_pow2_exp`, `np.ldexp`; the page's `_bgPow2Exp`, `_bgLdexp`): the relation is homogeneous in the intensity, so on ordinary data every intermediate is the same bits times 2^-e — measured on the committed targets × averaging 1 / 3 / 10 (606 cases): 0 backgrounds differ from the previous commit, bit for bit. The bound is evaluated ratio-first (no product of three small numbers), carries an absolute term for subnormal rounding (eta = 2^-1074 per rounding) and is enlarged by (1 + 64 u) for its own roundings; a value scaled back into the subnormal range is refused (it lost bits). Committed bound margin: at most 0.043 of the predicate |
| 2 | MAJOR (A, B): the zero-loss branch certified the flat C0 when the FLOAT edge means compared equal — exact means 1 and 1 + 2^-53 (B), 1e12 + 0 and 1e12 + 2^-14 with repeated energies (A): no amplitude meets the anchor | the flat member is certified only if the EXACT loss vector is zero (every term has an exactly zero factor: T = 0, a zero weight, or a zero net against the exact low-edge mean — a float zero not proven so is refused as cancelling), the EXACT edge means agree, and the returned flat curve is the exact mean within the predicate (`fitting._tougaard_zero_loss_verdict`, the page's `_tougaardZeroLossVerdict`, Fraction / BigInt) |

A separating case pins that the bound is the bound of the computation performed: at
1.5e-307 counts the normalised bound certifies (0.012 of the predicate) and the result is
within the predicate of the exact relation, where a bound at the data's own scale would
have refused (1.1 ×). Mutation-verified (4 of 4 killed): the certificate unnormalised and
the zero-loss branch on float means, each side.

**Round 15 — NO-GO ×2** (`background_math_impl_r15_verdict_run{A,B}.md`, commit 41b60d8;
both: all 606 committed Tougaard backgrounds bit-identical to the previous computation,
no refusal, bound at most 0.0432 of the predicate; the margin, measurements, census and
upload comparison reproduce):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B): the bound was FIRST-ORDER — with the computed edge difference D = 0 (exact 2^-45 / 3, 2^-50) and the high-edge sum's uncertainty above its magnitude (q0 ≈ 26) the truncated terms dominated: 7e11 / 2e13 × the predicate, certified | the bound is now RIGOROUS (no truncation): the exact ratio L_i / L_0 lies within rho_i = (dL_i + r_i dL_0) / (|L_0| − dL_0) of the computed one — refused (inf) when dL_0 ≥ |L_0|, the high-edge sum's sign then not established; the exact D within dD = da + dc + u|D| multiplies (r + rho), so a computed D of 0 cannot hide it; the gammas are g(m) = m u / (1 − m u); the C0 uncertainty enters every row through W. Committed: 606 / 606 bit-identical, none refused, bound ≤ 0.0433 of the predicate. A separating case pins dD: a well-determined high-edge sum, computed D 0, exact 2^-53, a far peak (ratio ~1e13) — refused; without dD the bound would be 3e-4 of the predicate while the returned curve misses the exact relation by 8.7 × |
| 2 | MAJOR (B): scaling back rounded the whole curve to ZERO, which the subnormal guard exempted | the rescale must round-trip (`ldexp(ldexp(v, e), −e) == v`, both sides): a value that lost bits — to the subnormal range or to zero — is refused |

Mutation-verified (4 of 4 killed): dD dropped, the zero exemption, each side.

**Round 16 — NO-GO ×2** (`background_math_impl_r16_verdict_run{A,B}.md`, commit 848ff1e;
both: no Tougaard violation in 2 500 (A) / 8 000 (B) further extreme-scale probes; the 606
committed Tougaard backgrounds bit-identical, none refused, bound ≤ 0.0433; the margin,
measurements, census and upload comparison reproduce; B: 128 loader cases):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B): the exact line / manual curve is correctly rounded, but that one rounding is itself an error — 4e-5 at 1e12 counts over a span of 1-2, 2-4e7 × the predicate — and the explicit backgrounds checked only finiteness | each exact value's rounding must meet the predicate, decided EXACTLY: \|round(q) − q\| ≤ BG_REL_TOL × span, span the exact span of the data the curve is judged against — the background window for linear (as its line is defined), the ROI for manual and its fallback — server (`_line_through`, `manual_anchor_background`, `_span` exact) and page (`_bgExactLine`, `manualAnchorBackground`, `_bgRoundingWithin`, `_bgExactSpan`), same words: "… its exact values cannot be represented within the certificate's precision at this span (the data exceed what double precision resolves)". It refuses only where max\|I\| / span exceeds ~4 500 (tol / u): with Poisson noise the span is a few √I, so ~7e8 noise-free counts; no committed target uses linear or manual, every committed window ≥ 3 000 × inside |

Two tests used perfectly FLAT data (span 0, so a predicate of 0 that any rounding
misses): they now carry structure (their point is the curve through the anchors).
Mutation-verified (4 of 4 killed): the check off for the line and for manual, each side.

**Round 17 — GO ×2, no findings** (`background_math_impl_r17_verdict_run{A,B}.md`,
commit e882d9d). A: 3 500 adversarial Tougaard probes with no false certificate against
exact rational evaluation, 700 page / server comparisons bit for bit; the 606 committed
Tougaard cases certified unchanged (bound ≤ 0.0433); the 1 212 Shirley-family cases within
the predicate (≤ 0.9928); 128 valid / 128 altered records in both loaders; the census and
measurements reproduce; 484 smart / smart_exp comparisons bit-identical. B: 2 000
Tougaard and 2 000 linear / manual probes with no accepted violation or parity mismatch;
128 loader cases; the same reproductions — with the caveat that it "does not establish a
universal numerical proof" (normalisation can lose tiny components on extreme mixed-scale
inputs; no violation found). REVIEW COMPLETE — stopped for the owner, not deployed.

## 7. Owner round, 2026-10-03 — restore, seed, upload, linear, F3, F13

Owner, 2026-10-03 (not yet approved for deploy):

> 1. RESTORE: a saved fit reloads if its stored background equals the recomputed one
>    within fit_equality.py's rounding tolerance (on the background's own scale). Only a
>    genuine difference loads peaks-only with a notice stating the size of the change.
> 2. SEED: derive the request seed from INPUTS (raw data, window, settings, model), not
>    from the computed background.
> 3. FULL-PRECISION UPLOAD, bundled with (2) so there is one redraw.
> 4. LINEAR uses averaged edge levels, consistent with (1) of this unit.
> 5. F3: collapse smart and smart_exp into one "Smart" menu entry; both codes still load.
> 6. F13: keep refusing; the message suggests Linear for windows with no peak.
> Measure after (2)+(3)+(4) on the 202 targets [...]. Student note drafted, held.

Two follow-up decisions the same day (questions asked when the census showed what
"stored background" means in old files):

> Implied only (stored fittedY − stored peaks = the background the fit actually used).
> For the 29 with an envelope on other points: recompute today's background on the
> STORED points and compare there; refuse only if that is impossible. The 11 with no
> envelope load peaks-only — the stored curve was a preview, not the fit's background.

> Reload marked stale, for every fit whose envelope is checkable: show the fit's own
> implied background and peaks as saved, statistics marked stale with the size of the
> difference from today's background. Stale fits must not export or report as current
> results (existing F1 behaviour). The 10 that match reload as current. The 40
> uncheckable load peaks-only with a plain message.

### 7.1 What changed

- **Seed v2** (`fitting._request_seed`, tag `xps-fit-seed-v2`): the background term is
  `_background_effect` — the method, the window [i0, i1) where the method reads one, the
  averaging AS IT ACTS (k = min(n_avg, n // 4), `_avg_k`), a manual background's anchors
  in energy order (fewer than two: "manual-line" with its k; none / flat: "none") —
  never the computed curve. Everything else hashed as in v1 (energies, counts, the
  model's effective roles, method, solver options, n_perturb). So a future change in a
  derived quantity's arithmetic (an ulp in a background) no longer redraws the restarts.
- **Full-precision upload** (`uploadToBackend`): every value as `String(v)` (the
  shortest round-trip decimal) instead of BE `toFixed(4)` / intensity `toFixed(2)`.
  FOUND while pinning it: pandas' python engine does NOT round decimal text correctly —
  17-significant-digit values came back up to 2 ulp off (3 629 of 80 000 sampled values;
  2- and 4-decimal text, what the page used to send, is exact). `parser.parse_csv` now
  re-reads the two chosen columns as text and converts each value with Python's
  `float()` (correctly rounded; `_exact_columns`), so the server holds exactly the
  doubles the page holds — pinned by `tests/test_full_precision_upload.py` (node formats
  400 values incl. exponent forms and a subnormal, `/api/upload` stores them bit for
  bit, in the page's order). Page and server now compute on the same numbers (the 2-dp
  gap of §4, ≤ 8.6e-7 of the span on the committed targets, is gone by construction).
  The measurement of §7.3 was re-run after this fix (a first run through the inexact
  parse is not reported).
- **Linear through averaged edge levels**: the line through (E[i0], mean of the first k
  window points) and (E[i1−1], mean of the last k), k as for every method, evaluated
  exactly (`_exact_edge_levels` → Fractions, `_line_through`; page `_bgExactLevels` →
  BigInt, `_bgExactLine`) and rounded once, the rounding checked against the predicate
  as before. `needsEpAvg` now shows the averaging field for linear; its tooltip says so.
  The manual fallback (fewer than two anchors) reads the same levels on both sides.
- **F3**: one "Smart" entry; `smart_exp` is a disabled, hidden option shown only when a
  loaded file selects it (`_syncLegacyBgOption`, as `shirley_linear`), so old files load
  with their own code (bit-identical results, measured in §4).
- **F13**: the "no net signal" and "misses the relation" refusals end with " — for a
  window with no peak, use the Linear background" (`_NO_PEAK` / `_BG_NO_PEAK`, same words).
- **Restore** (`_restoredFitBgFailure`, `_restoredFitGrid`, `_restoredFitModel`):
  - the evidence is the background the fit USED: stored `fittedY` (the server's envelope)
    less the saved peaks evaluated at the fit's points (a Voigt saved before A03 drawn
    at the η the server recorded, `p._backendParams.gl_ratio`, as GL — the
    `autofit.parity.recorded_voigt_eta` rule). The stored background CURVE is not
    evidence: before this unit the page saved its own preview beside the server's fit;
  - the fit's points: the record's ROI selection when it reproduces the stored energies
    (exactly or as saved to 4 dp), else each stored energy matched in order, else a
    CONSTANT OFFSET (the charge correction changed after the fit, and the peaks moved
    with it, `updateChargeCorrection`). On a uniform grid every run of samples is such an
    offset, so the run is pinned by the fit's own record: the counts it saw (stored
    background + subtracted counts) or, when it stored no background, its RMSE (counts
    less envelope on its points) — nearest wins, a tie or no record refuses. On the 16
    committed offset fits the chosen run reproduces the stored RMSE to 4 significant
    figures and the next candidate is off by 139–2 150 counts; the true offsets are
    0.001–0.13 eV (a charge shift re-entered after the fit);
  - today's certified background is computed on those points from the saved settings
    (manual: the record's own anchors) and compared with the implied one: worst
    |used − today| ≤ `BG_RESTORE_REL` (1e-3, `fit_equality.SAME_MINIMUM_REL`, pinned
    equal by a test) × max(|used|, |today|) — CURRENT, today's certified curve installed;
    beyond — STALE: the fit's own background and peaks as saved,
    `fr.backgroundStale = {pct}`, `_statsState` 'stale' (F1: no χ², R, RMSE or σ shown,
    exported or saved as current; CSV / XLSX WARNING, TSV NOTE, the Results banner, the
    header tooltip all say "background changed" with the size — `_bgStaleNote`); judged
    afresh on every load; amber notice naming each stale fit with its size;
  - uncheckable (no envelope; no stored energies; envelope and energies of different
    lengths; stored points not points of the raw data; settings without a converged
    background now): peaks only, each with its plain reason.

### 7.2 The census (121 committed saved fits, `scripts/bg_math_restore_census.py`, the page's own functions)

After Codex round 18 (§7.5); the round-18 commit 131cc39 reported 15 / 66 / 40 — the five
it called current hold a Voigt fitted before A03 at another mix.

| outcome | n |
|---|---|
| CURRENT (implied background = today's within 1e-3 of its scale; median 2.2e-6, max 9.4e-5) | 10 |
| STALE (reloaded with its own background and peaks; statistics not reported) | 71 |
| — against another background | 66 |
| —— of which only through today's inclusive window (the old request's nearest-index, end-exclusive window reproduces them) | 60 (median 0.83 %, max 5.07 %) |
| —— of which under EITHER window | 6 |
| — holding a Voigt fitted before A03 at a mix other than 0.5 (the page draws 0.5, so it cannot show the fit as fitted) | 41 |
| —— stale for that alone (background equal to today's) | 5 |
| PEAKS-ONLY: saved without the energies it was fitted on | 28 |
| PEAKS-ONLY: saved without its fitted envelope | 11 |
| PEAKS-ONLY: envelope and energies of different lengths | 1 |

The pre-A03 Voigts are the U 4f satellite (and two Cl 2p) components of 47 committed
fits (41 of them checkable): before 2026-09-22 the server fitted a Voigt's mix freely
(recorded η from ~0 to 1.0, `p._backendParams.gl_ratio`) while the page drew 0.5 (A03). The
restore reconstructs the implied background with the recorded η, but the page's drawn
components are at 0.5, so such a fit's statistics are never shown as current
(`fr.voigtStale`, the notices name the component and its η).

`scripts/bg_math_restore_alternative.py` recomputes the same in Python (`fitting`,
`autofit.parity`) under both window rules: verdicts identical on all 121.

The six that differ under either window (same size under both rules, so not the window;
main's own server background on the same samples, old window, misses them too — by
0.85–2.95 % (U4f Scan_0 1.21 %, U4f Scan_3 0.95 %, the others as below), with or without
the old 2-dp counts — so these fits were made against a background no
version in this repository's main gives, or their peaks were edited after the fit in a
save older than F1, which kept no model key; the record cannot tell which):

| project / tab | method | difference (today) | old window |
|---|---|---|---|
| 4-GTA UCl4-BN / B1s Scan_1 | smart | 2.95 % | 2.95 % |
| 4-GTA UCl4-BN / U4f Scan_0 | smart | 1.65 % | 1.65 % |
| 4-GTA UCl4-BN / U4f Scan | smart | 1.65 % | 1.65 % |
| 4-GTA UCl4-BN / B1s Scan_4 | smart | 1.55 % | 1.55 % |
| 4-GTA UCl4-BN / U4f Scan_3 | smart | 1.17 % | 1.17 % |
| UCl4_on_graphite / U4f Scan_2 | smart | 0.878 % | 0.905 % |

CORRECTION to what was reported before the owner's decision: "9 genuine differences,
4-GTA B 1s up to 127 %, 4-GTA U 4f ~97 %, UCl4 U 4f 14.9 %" was an artefact of my offset
matching, which took the FIRST run of samples that fitted the offset — on a uniform grid
any run — and so compared 16 fits on samples 2.4–6 eV away from their own. With the run
pinned by the fit's own record, the backgrounds of 4-GTA B1s Scan_2 / Scan_3, U4f
Scan_1 / Scan_8 and UCl4 U4f Scan_1 equal today's (the three U 4f ones are stale for
their pre-A03 Voigts alone), and nothing differs by more than 5.07 %.

### 7.3 Measurements after (2)+(3)+(4) — 202 targets, Trust-Region, n_perturb 3, as the page sends them

`final_tr` / `final2_tr` (two identical presses of the branch, run AFTER the parser fix of
§7.1) against `main_tr` / `main2_tr` (main as shipped); `node scripts/bg_math_impl_analyze.js
docs/findings/background-math/data/impl final` → `final_analysis.json`. (A first pair of
runs through pandas' inexact parse is not reported: every seed differed from this run's,
as the inputs differed by ulps.)

| | median | max | count > 1 pp | count > 0.1 pp |
|---|---|---|---|---|
| net area of the background, main → branch | 0 % | 0.001 % | 0 | 0 |
| area %, main → branch | 0 | 28.4 pp | 4 | 8 |
| atomic %, main → branch | 0 | 29.4 pp | 6 | 8 |
| area %, two presses of main | 0 | 0.019 pp | 0 | 0 |
| area %, two presses of the branch | 0 | 0.003 pp | 0 | 0 |
| atomic %, two presses of the branch | 0 | 0.003 pp | 0 | 0 |

No convergence verdict changes; the seed is identical across the branch's two presses on
all 202. The backgrounds barely move, so every move > 1 pp is the one redraw of the
restarts (seed v2, and inputs at full precision) landing in another minimum. The
scattered-starts line on the branch flags FOUR of the six — not all:

| target | component (largest move) | area / atomic pp | χ²ᵣ main → branch | scattered-starts line (branch) |
|---|---|---|---|---|
| 8-JT Graphite / C1s Scan_8 | Graphite | 28.4 / 29.4 | 35.5 → 32.3 (better) | 0 of 3 reached this solution; 1 alternative — flagged |
| 8-JT Graphite / C1s Scan_5 | Graphite | 17.5 / 18.1 | 17.3 → 33.9 (worse) | 0 of 3; 1 alternative — flagged |
| 1-GTA / C1s Scan_0 | Adventitious 3 | 10.8 / 11.3 | 3.82 → 4.62 (worse, +21 %) | 3 of 3 reached this solution — NOT flagged |
| 8-JT Graphite / C1s Scan_6 | Adventitious 2 | 2.67 / 2.79 | 8.54 → 8.55 (level) | 3 of 3 — NOT flagged |
| B4C-UCl4 / U4f Scan_7 | Satellite 1 | 0.62 / 2.17 | 2.77 → 2.93 (worse) | 2 of 3; 1 alternative — flagged |
| Cl2p_projfit_test / U4f Scan_1 | U 4f7/2 | 0.34 / 1.02 | 1.56 → 1.58 (worse) | 2 of 3 — flagged |

The two unflagged moves are the check's documented limit: its starts are scattered
around the STUDENT'S start, and on these two every one of them reaches the solution the
fit returned — main's better minimum for 1-GTA C1s Scan_0 (χ²ᵣ 3.82) was found only by
main's perturbed restarts. Four of the six are worse fits than main returned (8-JT C1s
Scan_5 is CLAUDE.md's known 33.9 / 51.9 / 17.26 case). This is the same seed lottery as
the round-17 measurement (§4: eight 8-JT moves of 2–28 pp, then with v1's seed) —
redrawn once more by this round, and not again for arithmetic reasons.

### 7.4 Tests

Restore: `tests/js/background_not_converged.test.js` (the implied rule for every
method, within / beyond the tolerance, the stored curve not evidence, non-numbers fail
closed, each uncheckable reason, the charge-offset case pinned by the counts and refused
without them), `tests/test_browser_background_not_converged.py` (a fit saved now, with a
garbage stored preview, and against the old 5-iteration Shirley reloads current — the
5-iteration curve is 1.7e-6 of its scale from today's here; against a one-step Shirley,
4 %, stale with its notice; manual anchors moved / method changed: stale or, without an
envelope, peaks only), `tests/js/stale_statistics.test.js` (the background-stale note
threads through the save fields). Seed: the pinned seed values and draws are
re-derived for v2 — an intentional derivation change, not a numpy upgrade
(`PINNED_SEED` 3015826926 → 2117573689); the ignored-setting test is rewritten (Linear
now reads averaging): averaging under "none", and an averaging beyond the window's
quarter under Linear and Shirley, leave the background and the seed bit-identical; the
whole-fit comparison is kept for none and linear — under Shirley the certificate's
Trust-Region continuation sent the two identical requests on this several-minima model
into different basins once in the full suite (the accepted property), so there the
inputs are the claim. `tests/test_fit_equality.py`'s not-better case pins v1's seed for
the two-basin fixture (PROGRESS.md follow-up). Upload: `tests/test_full_precision_upload.py`.
Suites at the commit: JS 539 passed + 2 TODO (floor 539, exact); pytest in the commit
message.

### 7.5 Codex round 18 — NO-GO ×2 (`background_math_impl_r18_verdict_run{A,B}.md`, commit 131cc39)

Both runs reproduced the census (15 / 66 / 40 at that commit), `final_analysis.json`, the
Python twin and the student note's numbers.

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B): a zero background (none) reloaded 100 % stale — the server's and the page's evaluation of a component differ by ~1e-14, which IS the implied background's whole scale | the comparison allows the precision the subtraction recovers a background to: worst ≤ BG_RESTORE_REL × the background's own scale + BG_REL_TOL (the unit's certificate precision, 1e-12) × the envelope's scale — no new constant |
| 2 | MAJOR (A, B): a charge shift by whole grid steps made an EXACT match on the wrong samples, returned before the fit's record was consulted (75.9 % / 82.4 % stale for unchanged fits) | `_restoredFitGrid` collects EVERY reading that reproduces the stored energies (the ROI selection, the in-order matches, every constant-offset run) and the fit's record (stored counts, else its RMSE) chooses among them; a tie or no record refuses |
| 3 | MAJOR (A, B): a project save rounds the energies to 4 dp and keeps the envelope at full precision; the components were evaluated at the rounded energies (0.56 % / 4.2 % / 100 % stale for unchanged fits) | the components are evaluated at the matched raw samples' own energies in the fit's charge frame (raw − the key's shift), full precision |
| 4 | MAJOR (A, B): a Voigt fitted before A03 was checked at its recorded η and drawn at 0.5 (Cl2p Scan_1: 338 counts) | such a fit cannot be shown as fitted: `fr.voigtStale` makes its statistics stale whatever its background, the notes name each component and its η (41 committed fits) |
| 5 | MAJOR (A, B): Save Spectrum of a background-stale fit wrote today's background and a recomposed envelope; the reload then dropped it | a restored-stale fit not edited since it was loaded (`fr.loadKey`, runtime only) is saved with its own points, envelope and background and `restoredStale: true`; the loader judges it afresh |
| 6 | MAJOR (B): the scattered-starts panel, the recorded choice and its export ignored background staleness | `_startsIfCurrent` / `_certificateMoveIfCurrent` refuse a restored-stale result, and the restore clears its starts, choice, certificate notice and support verdicts |
| 7 | MAJOR (A): the full-precision upload wrote integer text; [-1, 1e19, 1] was not one integer type to pandas, which read the column as text and skipped a row | `uploadToBackend` writes a whole number with '.0', so every column is a float column; pinned by `tests/test_full_precision_upload.py` with the page's own formatter |
| 8 | MAJOR (A) / MINOR (B): §7.3 said three of the six moves were worse fits; the table shows four | corrected |
| 9 | MINOR (B): `_restoreUI` did not enable the averaging field for Linear | it does |

Also found while fixing (2)–(3): the components of a fit with a model key are now the
key's own peak values (`_restoredFitPeaks`) — an edit made after the fit and saved
(the F1 stale case) no longer leaks into the reconstructed background — and an older
save without a key gets one stamped at restore (`restoredKey`, saved with it) for the
same reason. Mutation-verified (5 of 5 killed): components at the rounded energies, no
subtraction-precision term, the exact match first, no key components, no Voigt stale.
Census after the fixes: 10 current, 71 stale (66 against another background, 41 with a
pre-A03 Voigt, 5 for that alone), 40 peaks only.

Owner, 2026-10-04 (asked when the full suite went red on a test this round did not
touch): `test_scattered_starts.py::test_the_starts_are_a_pure_function_of_the_request`
failed in two consecutive full suites and passed alone — after `test_fit_reproducibility.py`
or the browser module, two identical requests on the two-basin fixture sent one
scattered start into the other basin (the certificate's Trust-Region arithmetic). "Narrow
the test now: assert identical requests give identical inputs (seed, scattered starting
points). Move the whole-fit comparison to the two-basin follow-up, and promote that unit
from LOGGED to NEXT in PROGRESS.md — it runs right after this unit, before anything
else." Done: the test records every `_scattered_start` draw and requires the same seed
and the same four starting points bit for bit; PROGRESS.md "NEXT".

