# Fail-open guards sweep — REPORT ONLY (2026-09-25)

Owner's brief: "Find every check that passes when its own machinery errors,
when a precondition is absent, or when an input it relies on is never sent.
For each finding: where it is, what it silently passes, whether anything
downstream relies on it, and severity. REPORT ONLY, no fixes."

Method: three independent read-only passes (server code; page code; the
page ↔ server contract, with every request built by the page's own
`peakToBackendSpec` / `_bgWindowIndices` and posted through the Flask test
client), then verification of the load-bearing claims by me. Main at
3ea3b8b. Reproduction scripts as run: `docs/findings/fail-open/repro/`
(paths inside them point at the session scratchpad; they are records, not
tests). Nothing in the code was changed.

Evidence levels: **R** reproduced (a run whose output is quoted), **R-me**
reproduced or verified by me as well, **C** verified from code only.

Severity: **HIGH** a wrong scientific result or charge correction is
presented as valid; **MEDIUM** a warning or verdict a user relies on
silently disappears or is replaced; **LOW** hygiene, fails closed, or
unreachable from the UI.

## 1. The three known instances

| instance | status |
|---|---|
| Differential evolution failing the required-component check open | **FIXED** (R): the refit goes through `fit_model` → `_global_or_local_candidate`; a real anchor gives `required: true, F 1226`, a redundant one `required: false, F 5.6`. |
| `_validateUncertainties`' at-bound rule never firing | **Refined** (R, R-me): it CAN fire for a free centre (start ± 2 eV, every shape but DS+G), FWHM [0.1, 15] and GL mix [0, 1]. It can NEVER fire for amplitude (`max` is always null: the page sends no `amplitude_max`, the server has no default) or a DS+G centre (no window at all). And every other shape parameter with finite bounds — asymmetry, DS α/γ, DS+G α/β/m, LA α/β/m — is filtered out by a five-name allowlist before any rule runs: DS α fitted at exactly its 0.5 ceiling, DS+G β on its 0.05 floor, LA β on its 5.0 ceiling, asym-GL asymmetry at 1.0 all return no warning. `fwhm_l` in the allowlist is not a server parameter (dead). See M4. |
| Find Peaks rejecting an empty ROI field the page treats as full range | **Confirmed, fails CLOSED** (R): an empty field becomes JSON `null`; the server's default applies only when the key is ABSENT, so `{"be_min": null}` → 400 "must be numbers" (`{}` → accepted). LOW. |

## 2. HIGH

**H1. After an edit, the previous fit's statistics are reported as the fit
of the current model** (page; R, R-me).
- Where: `updatePeakParam`, `addPeak`, `removePeak` call only
  `_invalidateFittedY` (nulls `fittedY`); `state.fitResult` keeps its χ²ᵣ,
  R-factor, `backendResult` and σ. `exportFitTable`'s only gate is
  `if (!state.fitResult)`.
- What passes: CSV right after a fit — `"C-C","supported","285.0000",
  "0.00200","1.2000",…` under `# Chi-squared reduced: 1.0200`; after
  typing centre 287.4 and FWHM 2.5, no refit — `"C-C","","287.4000",
  "0.00200","2.5000",…` under the same χ²ᵣ, with no WARNING line.
- Downstream: CSV/XLSX, TSV, the publication figure's χ²ᵣ, spectrum/fit
  saves, and the Results table (the edited centre ± the old σ). Find Peaks
  apply in its default mode replaces the peaks without even nulling
  `fittedY` (already listed in CLAUDE.md as not covered, with undo/redo;
  the ordinary edit case is not).
- Closing it: bind χ², σ, R and every export/save to `_startsLiveKey()`,
  as the support verdicts and starts evidence already are.

**H2. basinhopping always reports `success: true`** (server; R, R-me).
- Where: lmfit 1.3.4 sets `result.success = True` in `prepare_fit` and
  `basinhopping` never reads scipy's result (only an evaluation-budget
  abort clears it); `run_fit` passes it through.
- What passes: the A0 acceptance rule for that method. A 3-component C 1s
  fit returned `success: true` while scipy's own lowest minimisation said
  "Desired error not necessarily achieved due to precision loss" (the
  answer there was good, χ²ᵣ 0.88); with the local minimiser crippled to
  one iteration (settings the page cannot send), `success: true` at
  χ²ᵣ 59 930.
- Downstream: Run Fit's `success !== true` gate, Auto-Fit's gate (a charge
  correction can follow), the perturb loop and the required check.
- Rated HIGH because it is an acceptance gate that cannot close for a
  method the Method dropdown offers; NOT reproduced with a bad answer from
  page-sendable settings.
- Closing it: take success from scipy's `lowest_optimization_result`.

## 3. MEDIUM

**M1. A non-finite number in a successful `/api/fit` reply makes the page
switch to the local engine** (contract; R, R-me for the serialisation).
- Where: `app.py` returns `jsonify(result)` without `_json_sanitize`
  (which `/api/analyze` uses); Flask writes `NaN`. `fitting.py` passes a
  NaN stderr through. The page's `resp.json()` throws, `_asTransport`
  classifies it as a transport failure, `runFitLocal` runs.
- What passes: the A0 rule "fall back to local only on a transport
  failure". Reproduced: 40-point ROI, three components collapsed to 0 —
  HTTP 200, `success: true`, three `NaN` tokens; the server's converged
  result, its "not supported" verdicts and its starts evidence are
  replaced by a local starting-point fit. 4 of 27 narrow-ROI
  configurations; none on a full 190-point ROI. Auto-Fit fails closed on
  the same body.
- Closing it: sanitise `/api/fit`, or never treat a 2xx parse failure as
  transport.

**M2. n_data ≤ n_free is reported as a near-perfect, fully supported fit**
(server; R).
- lmfit's `redchi = χ²/max(1, nfree)`; `_component_support` and
  `_component_required` clamp dof to 1; Trust-Region accepts m < n.
  6 points, 2 GL components (8 free): `success`, χ²ᵣ 2.8e-6, both
  "supported" (F 7.5e7, 2.2e7), `required: true`.
- Through `/api/fit` it is masked by M1 (NaN σ); through Find Peaks'
  "Refit my current peaks" (NaN sanitised to null, ≥ 20 ROI points
  required) a model with > 20 free parameters reaches it.

**M3. The required-anchor verdict ignores whether its refit converged**
(server + page; R).
- `_component_required` computes `required` whether or not the refit
  converged (a non-finite refit χ² reads "required"); the page never reads
  `refit_converged`. Reproduced with a refit stopped early: `required:
  true, F 992, refit_converged: false` for an anchor that is redundant
  (`F 1.17` when the refit completes). Not reproduced organically.
- Related, by design and documented: `required: null` or `{ran: false}`
  (an exception, "nothing left") never blocks, silently.
- Downstream: Auto-Fit's charge correction.

**M4. `_validateUncertainties` is fail-open beyond the known rule**
(page; R).
- Rule 1: see §1 (allowlist; amplitude and DS+G centre never).
- Rule 2 ("covariance singular"): needs `_preFit`, which only `runFit`
  sets — never fires after Auto-Fit (reachable: a U 4f Auto-Fit returned
  "Could not estimate error-bars"); compares `gl_ratio` (0–1) with `glMix`
  (0–100); silent for a parameter that moved and has a null σ; blind to a
  singular covariance lmfit still inverts (two identical components:
  amplitude σ 5.9e11 on 3060, both "supported", no rule fires). After
  "Use this solution", `_preFit` is the live model, not the request's
  start.
- The whole panel is gated on `backendResult`, which saves do not persist
  (each peak's `_backendParams` is saved): after save and reload every
  uncertainty warning and every σ in Results and CSV/XLSX disappears.

**M5. Auto-Fit's C 1s gate judges a stale, typed window** (page; R-me in a
browser; consequence R server-side only).
- `isC1sTab` reads `tab.ui.roiMin/roiMax` (synced only on tab switch or
  save) and tests the TYPED midpoint, not the data selected;
  `findGraphiteRawBE` takes the highest strong maximum in the live window;
  nothing bounds the provisional shift.
- Browser (mine): wide scan 270–420 eV (small C 1s + U 4f doublet), record
  ROI 280–295, ROI typed 370–415 with no tab switch → the Auto-Fit menu is
  ENABLED and the gate passes. In 3 of 3 constructions the step (c) refit
  then refused the fake anchor (F 0.1–2.5; nothing applied). The server
  construction of the page-code pass (U 4f₅/₂ taken as "Graphite",
  provisional shift 107.3 eV) passed support (F 2096) AND required
  (F 384) — every gate in `applyAutoFitResult` passes, so a ~107 eV charge
  correction would follow; the page-side apply of THAT construction was
  not run.
- Rated MEDIUM on the evidence (the gate is open; the downstream checks
  held on the page in every run I made); its consequence class is HIGH.
- Closing it: gate on the live `getROIData()` selection; require a
  plausible provisional shift.

**M6. Auto-Fit has no "model edited mid-fit" discard** (page; C). `runFit`
compares the model-plus-context key before and after its await; Auto-Fit
checks only the owner, then rebuilds its background from the live (possibly
edited) ROI, and `_restampSupport` stamps verdicts current for a model that
was never fitted.

**M7. Charge-correction verification** (page; R). `_onCCObsInput` sets
`chargeVerified = true` on ANY input, including clearing the field;
`updateChargeCorrection` maps an empty value to a shift of 0. A batch-
propagated tab (unverified, shift 1.6) cleared → `verified: true`, red mark
hidden, `ccShift: 0`, method still `c1s`. `chargeVerified` and the method
are never exported (CSV/XLSX write only "Charge correction: 0.000 eV").

**M8. Run Fit after Auto-Fit drops Auto-Fit's centre and width bounds**
(contract; R at the spec level). `peakToBackendSpec` forwards only
`_afAsymMin/Max`, not `_afCenter*` / `_afFwhm*`: the Graphite FWHM
0.4–1.2 becomes 0.1–15, Adventitious 1's centre floor of 284.80 becomes
start − 2 eV, on the refit users routinely run.

**M9. Find Peaks** (server + page).
- The absolute `noise_floor = 1.0` (never sent by the page) decides
  whether a slot is "occupied" and so drives persistence, the absent-slot
  test and the stability gate: `main_graphitic` occupied at amplitude 1.5
  counts, not at 0.5, whatever the data's scale (R). The Design Rules case
  exactly ("thresholds on data-scaled quantities fail").
- Persistence = occupied / refits ATTEMPTED; the 25 s per-candidate
  deadline can stop refits early and `n_attempted` / `timed_out` are not
  reported; `n_refits` can be set to 1 → persistence 1.0, the 0.7 gate
  passes, "stable across re-fits" (C).
- `_fpPlainMessage` says "passed every check cleanly — stable across
  re-fits…" unless one of five flags is set; it ignores
  `weighted_ic_disagreement` (rendered nowhere), `model_selection_warning`
  (a banner shows while the text says "passed"), ambiguous pairs,
  residual/autocorrelation flags, `bic_ambiguous` / `criteria_conflict`,
  `candidate_pool.error`; `sparse_map` returns `success: true` when its λ
  did not converge (C).
- `applyFindPeaks` ignores `body.success` ("Refit my current peaks" can
  return a non-converged fit's peaks and σ) (C).

**M10. A crashed scattered-starts check looks like "not applicable"**
(server + page; C). `{ran: false, reason: "error"}` renders as no panel;
exports drop the line. Not triggered organically (per-start exceptions are
swallowed and counted).

## 4. LOW

- **Page NaN → JSON null** (R): clearing a free amplitude / FWHM / GL-mix
  field sends null; lmfit starts it from −∞ clipped to the lower bound
  (0 / 0.1 / 0) and returns `success: true` — a fit from a start the page
  never had (the seed and scattered starts built from it). A cleared
  centre, a locked field or a link offset gives HTTP 500 "Internal
  fitting error" (fails closed, poorly).
- **±2 eV centre window re-centres on each press** (R): the drift guard
  limits each press, not the total; the at-bound warning reflects only the
  last request.
- `/api/parse-vgd` never receives `photon_energy` / `work_function` (every
  VGD at 1486.6 / 4.5 eV); a VGD error in multi-file load is dropped
  silently; folder load reports every attempted file as "Loaded" (C).
- `runFitLocal`'s "normal equations singular" failure cannot fire
  (`solveLinear` substitutes 0 for a zero pivot) (R).
- Batch Fit's summary omits targets closed mid-batch and the target it
  stopped at on a tab change (C).
- `_findPeaksReview` / `verified: false` written, never read (the server's
  "named human review required before export" is not enforced); the
  C-ref badge is compared with nothing; `_autoFitDecideAreaWarning` returns
  no toast for a non-finite area; `_fpSyncOptionsFromControls` discards
  invalid Advanced JSON silently (C).
- Server hygiene (C unless noted): peak-id prefix collisions ("1" and
  "1_a") break the required check → `ran: false` (R, API-only);
  bayesian-exchange MC warning cannot fire with `n_replicas = 1` (the page
  minimum is 4); NaN residual diagnostics make `autocorr_flag` false;
  inf − inf makes two perfect fits never "ambiguous"; AICc `None` makes
  `criteria_conflict` unreachable; `/api/fit` coerces a bad
  `endpoint_avg` / index to a default instead of 400; the required test's
  p counts only the root's free parameters; `stats.reduced_chi_square
  || 0` would show a missing χ²ᵣ as a green 0.000 (unreachable).

## 5. Examined and judged not fail-open

runFit's acceptance and owner checks; `uploadToBackend` errors;
`runFitLocal`'s guards, commit-on-success and certificate;
`_autoFitGraphiteIsSupported`; `_componentSupportCore` /
`_componentSupportFromResponse` / `_component_support` (masked non-finite,
all-masked → unsupported, linked follow root); `_isUnsupported` /
`_currentSupport` (stale = "not established", fail-open by design and
pinned — the reason H1 matters); `_startsIfCurrent` and "Use this
solution"; `_same_solution` / `_scattered_starts`; the perturb loop
(unverified trials cannot displace the best); `_search_then_refine` /
`_global_or_local_candidate` / `_finite_search_box`;
`_validate_constraint_graph`; `_FIT_METHODS` and `n_starts` / seed
validation; leastsq / least_squares / nelder / DE success from scipy or
MINPACK; `_validate_analyze_request`; upload keeps finite values; the
background anchor-window fallback matches `_bgWindowIndices`; the engine's
non-converged candidates never become reports; `criteria.f_test` returns
no verdict on dof ≤ 0; the local-fit labelling; `_roiWindowStatus` /
`_roiHintFor` / `_centreOutsideData`; `runPropagation`'s resets;
`_computeRFactor` (NaN → red); every other catch block (cosmetic, rethrow,
or red/amber notice).

## 6. Suggested grouping for later units (not decided)

1. **Bind every reported statistic to the model it describes** (H1, M4's
   save/reload loss, M6): the by-key principle the sealed-fit-record memo
   already names for 1a–1d.
2. **Fit-outcome truthfulness on the server** (H2, M1, M2, M3, M10):
   success from scipy for basinhopping, sanitised JSON, n ≤ k refused,
   required only from a converged refit, a crashed check said aloud.
3. **Uncertainty panel coverage** (M4, §1): every varying parameter against
   whichever bounds are finite.
4. **Auto-Fit gate and bounds** (M5, M8, M7).
5. **Find Peaks' verdicts** (M9): the absolute noise floor is a Design
   Rules violation and the likely first target.
