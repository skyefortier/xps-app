# A01 — the local Levenberg–Marquardt fitter never descends: empirical proof (2026-09-15)

Status: PROOF ONLY, reported before any fix. Nothing changed in code.
Origin: Codex audit finding A01 (`docs/audit-2026-09-08.md` on the audit
branch). This document replays the shipped code, not a reimplementation.

## Verdict

Confirmed. `runFitLocal` in `templates/index.html` (main `072534c`) cannot
improve a fit. On every Batch Fit target it returns the starting model
unchanged and reports "Fit complete (local LM). χ²ᵣ = …". Two defects,
both present since the initial commit `f20d71b` (2026-03-26):

1. **Step sign.** Residuals are `data − model` (`:7231`), the Jacobian is
   `∂r/∂p`, and the normal equations are solved as `JᵀJ·dp = Jᵀr`
   (`:7267`). The correct Gauss–Newton/LM step is `dp = −(JᵀJ)⁻¹Jᵀr`. Every
   proposed step is therefore an ASCENT step, χ² rises, the step is
   rejected, λ is multiplied by 3, and after 24 rejections λ exceeds 1e8
   and the loop exits with the initial parameters (0.001 × 3²⁴ > 1e8).
2. **Convergence test.** `:7280` tests `|newChi − chi| / chi < 1e-8` AFTER
   `chi = newChi` on an accepted step, so the first accepted step would
   always terminate the loop. Today this never triggers (no step is ever
   accepted); once the sign is fixed it becomes the active bug, which is
   why a sign-only fix produced 1–5 iteration "fits" in the replay below.

## Scope: which paths use it

| path | uses local LM? | evidence |
|---|---|---|
| **Batch Fit** (`runPropagation`, `:10670–10790`) | **Always.** No backend branch exists in the function; every target runs `runFitLocal(be, bgSub, bgI)` at `:10774`. Since Batch Fit shipped (`5f3fc9b`, 2026-03-30). | code |
| Manual **Run Fit** (`runFit`) | Only as fallback, `:7151`, reached on ANY thrown error in the backend path: network failure, timeout, **and any `json.error` from the server** (a 400 validation error also lands here). The user then sees the "Local Fit Performed" overlay ("Results may be less accurate") with the starting model as the result. | code |
| **Auto-Fit C1s Graphite** | No (backend only, restores snapshot on failure). | code |
| Find Peaks | No. | code |

"Every Batch Fit uses it" is exactly true.

## Replay on committed project data

Harness (scratchpad, not committed): extracts `runFitLocal`, `solveLinear`,
`computeBackgroundCore` + all background functions, and the whole lineshape
block from main's `templates/index.html` verbatim by function name, loads
the shipped `static/js/batch_propagation.js`, and repeats `runPropagation`
step by step (source snapshot, amplitude scale = target max / source max,
linked amplitudes not scaled, `propagateFitUi`, source ccShift, ROI slice,
JS background, `runFitLocal`). Data: `docs/autofit/test_data/1-GTA UCl4-
graphite one set of U doublets.proj.zip`, source `C1s Scan` (6 peaks: GL +
asym-GL, Shirley) → 9 C1s targets; source `U4f Scan` (2 × LACX linked pair
+ 2 × Voigt, Smart) → 9 U 4f targets.

### Shipped code: final parameters vs starting model

| targets | iterations | parameters changed |
|---|---|---|
| C1s Scan_0 … _8 (9) | 24 each | **none** — every centre, FWHM, amplitude, GL mix and asymmetry identical to the scaled clone |
| U4f Scan_0 … _8 (9) | 24 each | only two, neither from fitting: `caM` 8.19935 → 8 (the `Math.round` clamp in `applyParams`), and the linked U 4f₅/₂ amplitude re-derived as parent × 0.65 (the clone step does not scale linked amplitudes; `applyParams` re-syncs them). Centres, widths, α, β, satellites: identical |

The reported "χ²ᵣ" in the batch summary is the unweighted residual
variance of the STARTING model: 1.0e5 to 2.1e6 on the C1s targets,
1.1e5 to 1.1e6 on the U 4f targets. It was displayed as
`χ²ᵣ = 187379.91` etc. in the propagation summary and the status bar.

### The same code with only the sign flipped

1–5 iterations, then the convergence test (defect 2) stops it after the
first accepted step. Parameters move (centres 44–420 meV) but χ² is still
far from the optimum. Not a usable reference.

### Sign + convergence test fixed (reference for what local LM could do)

17–473 iterations (two C1s targets hit the 500 cap region), residual
variance 2.4e4–3.7e5 on C1s, 1.9e4–7.2e4 on U 4f. This shows the fitter
works once both defects are fixed, but the unit that ships the fix must
also address the iteration budget and the 1e-8 relative tolerance; this
replay is evidence, not the fix design.

### Size of the error: backend (production lmfit, Poisson weights) from the same starting model

This is what the student would have obtained from Run Fit on each target
instead of the returned starting model. Δ = correct fit − what Batch Fit
reported.

| target | χ²ᵣ (weighted) | max Δ centre | max Δ FWHM | max Δ area | max Δ atomic fraction |
|---|---:|---:|---:|---:|---:|
| C1s Scan_0 | 4.36 | 326 meV | 22.5 % | 23.9 % | 6.7 pp |
| C1s Scan_1 | 13.07 | 133 meV | 34.6 % | 38.0 % | 3.9 pp |
| C1s Scan_2 | 4.09 | 213 meV | 18.9 % | 28.8 % | 2.7 pp |
| C1s Scan_3 | 4.43 | 261 meV | 24.6 % | 36.2 % | 8.7 pp |
| C1s Scan_4 | 19.06 | 537 meV | 41.8 % | 73.8 % | 6.4 pp |
| C1s Scan_5 | 4.33 | 338 meV | 29.9 % | 39.7 % | 8.7 pp |
| C1s Scan_6 | 5.23 | 56 meV | 10.6 % | 13.0 % | 3.1 pp |
| C1s Scan_7 | 8.02 | 289 meV | 38.5 % | 49.2 % | 12.0 pp |
| C1s Scan_8 | 2.74 | 362 meV | 32.8 % | 24.6 % | 7.8 pp |
| U4f Scan_0 | 1.93 | 71 meV | 15.7 % | 21.9 % | 7.6 pp |
| U4f Scan_1 | 2.08 | 169 meV | 3.6 % | 11.9 % | 2.4 pp |
| U4f Scan_2 | 1.92 | 114 meV | 20.7 % | 35.5 % | 3.8 pp |
| U4f Scan_3 | 1.68 | 147 meV | 27.3 % | 49.6 % | 7.5 pp |
| U4f Scan_4 | 1.60 | 143 meV | 78.6 % | 33.0 % | 9.6 pp |
| U4f Scan_5 | 1.89 | 101 meV | 11.1 % | 12.2 % | 2.1 pp |
| U4f Scan_6 | 2.64 | 69 meV | 3.3 % | 12.2 % | 1.5 pp |
| U4f Scan_7 | 1.71 | 352 meV | 24.0 % | 24.4 % | 2.6 pp |
| U4f Scan_8 | 3.62 | 159 meV | 17.2 % | 25.3 % | 4.1 pp |

Areas: trapezoid of the component on the target grid for both. "Atomic
fraction" = area share within the region at equal RSF. These are the
committed lab project's own scans; a batch on scans that differ more from
the source would be worse, on near-identical repeat scans better.

## Which outputs carried the un-fitted numbers

After a Batch Fit, the target tab holds `state.peaks` = the scaled starting
model and `state.fitResult` = `{chi, chiReduced, rmse, be, bgSubtracted,
bgIntensity, roiRange}` from `runFitLocal`. Every consumer reads those:

- Results panel and Quantify table (`renderResults` → `_peakArea(state.peaks…)`, `:7417`; `renderQuantify`, `:7487`) — areas and atomic % of the starting model.
- CSV/XLSX table export (`exportFitTable`, `:10013`, areas at `:10017`) — same.
- Spectrum export and figure export (`exportResults` `:9590`, `exportFigure` `:9630`).
- `.spec.json` Save Spectrum (`_doSaveSpectrum`, `:8949`) and project save (`_doSaveProject`, `:9013`) — the starting model is persisted as the tab's peaks with a `fitResult` attached, so reopening the project shows it as a fitted tab.
- The batch summary itself lists "χ²ᵣ = <residual variance>" per target.
- Fit history: `_autoSnapshot` is suppressed during batch (`_snapshotSuppressed`), so no history entry marks these as batch results.
- Charge correction: `tgt.chargeVerified = false` is set, so the red "needs verification" marker is the only visible warning, and it concerns the shift, not the fit.

Nothing distinguishes a batch-propagated tab from a fitted one in the saved
file except the absence of backend stderr (blank σ columns) and the
implausible χ²ᵣ magnitude.

## A08 is the same family

`runFit` checks `json.error` but not `json.success` (`:7000` region; the
auto-fit path does check it at `:6997`), so an lmfit result that did not
converge is applied and announced as "Fit complete (lmfit)". A01 and A08
do not share a code line, but they share one root cause: no path in the
app gates "present as a result" on "converged". The A0 unit should fix
both through one acceptance rule (a result is displayed only with an
explicit convergence flag from its engine; local LM must produce one) and
one test per path, rather than two patches.

## Ship plan (A0 — alone, own branch, own deploy)

1. Fix the step sign and the convergence test; bound iterations; return
   `{success, iterations}`; refuse to overwrite `state.peaks`/`fitResult`
   on non-convergence (keep the previous state); label the statistic as
   unweighted residual variance, not χ²ᵣ.
2. `runFit`: require `json.success === true`; a `success:false` response is
   a failed fit, not a fallback trigger; only transport failures fall back
   to local LM, and the overlay must say the result is a local fit.
3. Batch summary: per-target success/failure, no χ²ᵣ label for an
   unweighted statistic.
4. Tests: Node replay of this document (a noiseless Gaussian, amplitude 10
   from 5, must reach 10; the committed U 4f and C1s batch pairs must move
   by at least the backend's direction), plus the A08 response test.
5. Codex ×2, full suite, browser check on :5151, deploy, then send the
   student note (draft in `docs/comms/2026-09-15-batch-fit-student-note.md`).

Reproduction: scratch harness `batch_proof.js` (variants `shipped`,
`signfix`, `fullfix`) and `batch_backend_ref` in the session scratchpad;
the A0 unit converts the harness into `tests/js/local_lm_descent.test.js`.
