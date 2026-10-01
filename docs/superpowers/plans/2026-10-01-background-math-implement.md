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
is no solution (F11). The near-uniform fast branch's approximation is NOT certified:
re-evaluating the stated sum would fail ordinary instrument grids whose spacing differs
by rounding, and the owner's item lists undetermined / unsolvable only.
`fitting.compute_background` = the method + its certificate; on failure it raises
`BackgroundNotConverged` (a ValueError) with "<Method> background not converged:
<reason>." — HTTP 422 from `/api/fit` (and `/api/fit/start`'s record) and
`/api/background`. `run_fit`, `compute_background_only`, Find Peaks' engine
(`autofit/engine.py`) and `autofit/parity.py` all call it. No fallback solver.

**The page.** The twins run fitting.py's arithmetic operation for operation (shared
helpers `_bgEdgeLevels`, `_bgAscending`, `_npLinspace`, `_bgCumFromHigh`,
`_bgShirleyMap`; `BG_REL_TOL`, `BG_MAX_ITER` = 200): bit-identical for the Shirley
family. `shirleyLinearBackground` now mirrors the server's ascending copy (it skipped
it: 7.8 % of the span on a descending 5-point example) — otherwise the page's
certificate would fail every old Shirley + linear file on ordinary descending data
while the server certified it. `_bgCertificate` is the server's certificate (same
tests, reasons, tolerance). `computeBackgroundCore` returns the array marked
`converged` / `failure`; `_bgFailure(bg)` reads it.

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

A CLASS guard pins it: `tests/js/background_not_converged.test.js` finds every such
assignment and fails unless its function checks `_bgFailure(<that variable>)` (or
refuses up front on `_bgFailure(computeBackground(...))`); verified by mutation
(removing the figure's check fails it, naming the function and line).

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
- `tests/js/background_not_converged.test.js` (7): the class guard; the marker; the
  note; Run Fit's refusal order; Auto-Fit's preflight; the retired setting; the
  tooltips (F2) and Shirley + linear's menu state and notice.
- `tests/test_browser_background_not_converged.py`: real page, real server — the note,
  nothing drawn, Run Fit refused with no undo entry; an explicit background fits.
- `tests/js/_page_background_source.js`: the page's background section as one source
  for every JS test that runs it.
- JS CI floor 508 -> 523 (the owner's 512 for the two landed branches + this unit's tests).

## 4. Measurements

(below, filled from `scripts/bg_math_impl_measure.py` / `bg_math_impl_analyze.js`)

## 5. Release note (at deploy)

(below)
