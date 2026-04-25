# Auto-Fit C1s Graphite — Feature Specification

**Date:** 2026-04-24
**Status:** Planning. Claude Code will produce an implementation plan next via `/superpowers:write-plan`; that plan must be reviewed before execution.
**Rollback tag:** `clean-slate-pre-autofit`
**Author:** Skye Fortier, with design assistance from Claude

---

## Goal

Produce a single-action feature in XPS Fitting Studio that fits a C1s graphite spectrum and applies the resulting charge correction automatically. The user loads a C1s scan, selects "Auto-Fit C1s Graphite" from the Actions menu, and within approximately one minute (hard cap two minutes) receives a complete, chemically defensible fit with the graphite peak centered at 284.50 eV and the tab's charge correction applied from the fitted graphite position.

The feature's core purpose is to eliminate the ~10 minute manual fitting workflow currently required for each C1s spectrum in a UCl₄/graphite sample series (typically 10 spots per pellet) while producing fits comparable in quality to those produced manually by Fortier Lab personnel.

---

## Design rationale

### Why this feature, and not the previous attempts

This is the third attempt at a C1s automation feature. The prior two attempts failed for instructive reasons:

- **Phase 1/2 assisted batch fit** (shipped as Phase 1 marker only, then rolled back): aimed at propagating a template fit across multiple target spectra. The two-pass approach was sound in principle but premature — it assumed an atomic single-spectrum fit already existed, which it didn't.
- **Codex "Auto-Fit Graphite C1s"** (wild goose chase, rolled back): tried to combine automatic charge correction, 3-peak vs 4-peak variant comparison, a chooser modal, and shared-FWHM backend constraints in a single feature. Scope creep made the implementation fragile and untrustworthy.

This attempt narrows the scope deliberately. No variant chooser, no backend changes, no batch, no review queue. One button, one fit.

### Key design decisions and why

**Actions menu, not toolbar.** The feature is a workflow action, not a moment-to-moment control. It also needs to be disabled when the active tab isn't a C1s spectrum, which is easier to convey in a menu than a toolbar button.

**C1s detection by ROI energy range, not by tab name.** Tab names are user-editable and inconsistent. The ROI's energy-range midpoint (270–315 eV) is a physical property of the data and always reliable.

**Highest-BE strong peak as the graphite-finding heuristic.** "Most intense peak = graphite" fails when the low-BE "unknown" feature is very prominent (as in screenshots 4 and the more heavily-loaded UCl₄ samples). In every spectrum examined from Fortier Lab's UCl₄/graphite samples, graphite is the highest-BE strong maximum even when it isn't the tallest absolute peak. This heuristic is robust for the specific sample system the feature targets.

**4 adventitious peaks by default, not 3.** Both 3-peak and 4-peak models are literature-supported (Biesinger 2022 and related work). The 4-peak model accommodates a wider range of sample surfaces without modification, and matches the default practice of one of the lab's primary users (postdoc). Users who prefer 3 peaks can delete Adventitious 4 after the fit completes. No automated chooser is provided because the 3-vs-4 choice is stylistic/aesthetic rather than a fit-quality question.

**pseudo-Voigt for adventitious peaks, LA for graphite.** LA captures the intrinsic asymmetry of graphite (metallic density of states). Adventitious carbon species are insulator-like and symmetric, so pseudo-Voigt with free GL mixing is appropriate and matches existing lab practice.

**Center bounds calibrated against empirical Fortier Lab fits.** The 4th adventitious peak's bounds were widened to ±1.0 eV (not the ±0.5 used for peaks 1–3) because lab fits have landed that peak anywhere from 291.0 to 291.7 eV. Tighter bounds would artificially constrain the fit away from defensible positions.

**Data-driven low-BE peak count (0, 1, or 2).** The low-BE "unknown" region varies dramatically between spots on the same pellet. Static inclusion of low-BE peaks would over-fit when they're absent; static exclusion would fail when they're prominent. An intensity-ratio threshold, computed after provisional charge correction, adapts the model to the actual data.

**Identity of low-BE peaks is explicitly not determined.** The lab confirms the peaks are real but has not identified their chemistry. For the purposes of extracting a trustworthy graphite position, the peaks only need to be absorbed by the fit, not assigned. They are labeled "Unknown 1" and "Unknown 2".

**Single fit, no multi-pass.** Multi-pass fitting (e.g., graphite-only then full refit) was considered and rejected. Good initial positions + reasonable bounds + the existing lmfit trust-region solver converges reliably in one call.

**No FWHM linking between adventitious peaks.** Some XPS practitioners link adventitious FWHMs under the rationale that all adventitious carbon species should share a width. This is a choice, not a rule. Lab practice (postdoc, graduate student, and PI all examined) does not link, and the lab's existing fits vary FWHMs from ~1.3 to ~6.3 eV across adventitious species. Independent FWHMs match existing practice.

**Frontend timeout only, no backend cancellation.** The 2-minute hard cap is enforced via `AbortController` on the HTTP request. The server-side lmfit computation will continue to completion after abort and its result is discarded. This is a known limitation acceptable for single-user usage; proper backend cancellation would require modifying `fitting.py` and is out of scope.

**Single plain spinner, no cancel button, no progress text.** Lmfit doesn't expose real iteration progress over HTTP, so a progress bar would be dishonest. Elapsed-time display encourages users to abort too early. A plain spinner says "something is happening" without overcommitting to what.

---

## Full specification (the prompt for Claude Code)

The following is the exact prompt to paste into Claude Code. It supersedes any prior agreement or suggestion from earlier conversations.

```
Use the superpowers plugin with the feature-dev and frontend-design skills.
Before implementation, use /superpowers:write-plan to produce a detailed
implementation plan. I will review the plan before you run
/superpowers:execute-plan.

DO NOT modify fitting.py or app.py. This is a frontend-only feature built on
the existing /api/fit endpoint (which already uses lmfit). If you believe a
backend change is required, stop and tell me why before proceeding.

FEATURE: Auto-Fit C1s Graphite

A single-action feature that produces a complete, chemically reasonable fit
of a C1s spectrum, with charge correction automatically applied from the
fitted graphite peak. Target runtime under 1 minute typical; hard cap 2
minutes via frontend timeout.

MENU PLACEMENT

Add "Auto-Fit C1s Graphite" as an entry in the existing Actions dropdown menu.

- Enabled only when the active tab is identified as a C1s spectrum (see
  detection below).
- Grayed out (disabled) otherwise, with a tooltip explaining why
  (e.g., "Auto-Fit C1s Graphite is only available for C1s spectra").
- Not added to the main toolbar.

C1S TAB DETECTION

Identify a tab as a C1s spectrum by energy range, not by tab name:

- Compute the midpoint of the tab's ROI: (BE_min + BE_max) / 2 of current ROI.
- If 270.0 <= midpoint <= 315.0 eV, the tab qualifies.
- Recompute whenever the active tab changes or the ROI is edited, so the
  menu item enables/disables live.

PRE-FIT CONFIRMATION

When activated on a tab that already has peaks (peak count >= 1), show a
confirmation modal BEFORE running:

  Title: "Auto-Fit will replace existing peaks"
  Body:  "This tab has N peak(s) and a fit result. Auto-Fit will clear them
          and run a fresh fit. Continue?"
  Buttons: [Cancel] [Proceed]

Only run on Proceed. If the tab has zero peaks, skip the modal.

FITTING BACKEND

Use the existing /api/fit endpoint (which wraps lmfit). Do NOT implement any
client-side fitting in JavaScript.

ALGORITHM (runs after any confirmation):

1. FIND GRAPHITE IN RAW BE FRAME
   - Use the tab's current background-subtracted spectrum (current background
     method, current ROI).
   - Find all local maxima.
   - Filter to strong maxima: intensity >= 30% of global max intensity within
     the ROI.
   - Pick the highest-BE strong maximum. Its BE is graphite_raw_BE.
   - If no strong maxima found: abort with a clear error, leave tab state
     unchanged.

2. PROVISIONAL CHARGE CORRECTION
   - provisional_shift = 284.50 - graphite_raw_BE
   - Apply internally for step 3 only; do NOT write to tab state yet.

3. ASSESS LOW-BE REGION (in provisionally-shifted frame)
   - Integrate background-subtracted intensity over 278.0 <= BE <= 283.5 eV.
   - Compare to graphite peak height (intensity at 284.50 in shifted frame).
   - ratio = integrated_low_BE / graphite_height
   - Count distinct local maxima in 278.0-283.5 above 10% of graphite_height.
   - Decide number of low-BE peaks:
     * ratio < 0.03                              -> 0 low-BE peaks
     * 0.03 <= ratio < 0.15 OR exactly one max   -> 1 low-BE peak
     * ratio >= 0.15 OR two or more distinct maxima -> 2 low-BE peaks

4. BUILD FIT MODEL (peaks expressed in corrected BE frame after provisional_shift)

   Graphite peak:
   - Lineshape: LA (Lorentzian-asymmetric)
   - Center start: 284.50, bounds +/- 0.3
   - FWHM start: 0.7, bounds 0.4 to 1.2
   - alpha: start 0.10, bounds 0.05 to 0.20
   - beta: fixed at 0.05
   - m: free
   - Amplitude: free, lower bound 0

   Adventitious peak 1 (always):
   - Lineshape: pseudo-Voigt
   - Center start: 284.80, bounds +/- 0.5
   - FWHM start: 1.4, bounds 0.8 to 3.0
   - eta (GL mix): start 0.30, bounds 0.0 to 1.0, free
   - Amplitude: free, lower bound 0

   Adventitious peak 2 (always):
   - Pseudo-Voigt
   - Center start: 286.20, bounds +/- 0.5
   - FWHM start: 1.6, bounds 0.8 to 3.0
   - eta: start 0.30, bounds 0.0 to 1.0, free
   - Amplitude: free, lower bound 0

   Adventitious peak 3 (always):
   - Pseudo-Voigt
   - Center start: 287.80, bounds +/- 0.5
   - FWHM start: 1.8, bounds 0.8 to 3.5
   - eta: start 0.30, bounds 0.0 to 1.0, free
   - Amplitude: free, lower bound 0

   Adventitious peak 4 (always):
   - Pseudo-Voigt
   - Center start: 291.00, bounds +/- 1.0
   - FWHM start: 2.5, bounds 1.0 to 4.0
   - eta: start 0.30, bounds 0.0 to 1.0, free
   - Amplitude: free, lower bound 0

   Low-BE peak 1 (if step 3 assigned >= 1):
   - Pseudo-Voigt
   - Center start: observed local max in 278.0-283.5, or 283.0 default.
     Bounds +/- 0.8.
   - FWHM start: 1.0, bounds 0.5 to 3.0
   - eta: start 0.30, bounds 0.0 to 1.0, free
   - Amplitude: free, lower bound 0

   Low-BE peak 2 (if step 3 assigned 2):
   - Pseudo-Voigt
   - Center start: second observed local max, or 282.0 default.
     Bounds +/- 0.8.
   - FWHM start: 1.0, bounds 0.5 to 3.0
   - eta: start 0.30, bounds 0.0 to 1.0, free
   - Amplitude: free, lower bound 0

   Do NOT link FWHMs across peaks. Each peak has independent FWHM.

5. CLEAR EXISTING PEAKS AND RUN FIT
   - Clear existing peaks (user has confirmed above if there were any).
   - Insert the peak list from step 4.
   - Invoke /api/fit. Match the shape of runFit().
   - Use the tab's currently-selected fitting method (default Trust-Region).
   - Single fit call. No iteration, no retry, no multi-pass.
   - During the fit, display a simple spinner overlay on the plot area.
     No text, no elapsed time, no cancel button. Just a spinner indicating
     the fit is in progress.
   - Enforce a frontend timeout using AbortController: if the /api/fit
     request does not complete within 120 seconds (2 minutes), abort the
     request and treat it as a failure.
   - Known limitation: aborting the frontend request does not stop the
     server-side fit. The server will continue computing and discard the
     result. This is acceptable given single-user usage patterns.

6. FINALIZE
   - On fit failure, on timeout, or if the fitted graphite center is outside
     its 284.50 +/- 0.3 bounds:
     * Restore the tab to its pre-autofit state (the peak list from BEFORE
       the autofit, and prior fit result/charge correction).
     * Remove the spinner.
     * Show an error:
         - "No strong peak found..." for pre-fit detection failure
         - "Auto-fit exceeded the 2-minute timeout." for timeout
         - "Fit failed to converge or produced an unphysical graphite
            position." for fit-level failure
   - On success:
     * Remove the spinner.
     * Read fitted graphite center in the corrected frame.
     * final_shift = 284.50 - (graphite_fitted_center - provisional_shift)
       (equivalently: final_shift = 284.50 - graphite_fitted_raw_center)
     * Apply to tab state:
         state.ccShift   = final_shift
         state.ccMethod  = 'c1s'
         state.ccObs     = graphite_raw_BE
         state.ccLit     = 284.50
     * Persist the fit result to the tab normally, as if the user had
       clicked Run Fit manually.
     * Peak names:
         "Graphite"
         "Adventitious 1", "Adventitious 2", "Adventitious 3", "Adventitious 4"
         "Unknown 1", "Unknown 2"  (only the unknown labels actually added)

UI BEHAVIOR SUMMARY

- Actions menu entry is the only new UI surface.
- Confirmation modal appears only if pre-existing peaks.
- Spinner overlay on plot area during fit. No text, no cancel, no elapsed time.
- Hard timeout at 120 seconds.
- On success: fit and charge correction appear as if user ran Run Fit manually.
- On failure: toast or inline error. Tab state restored.
- The entire auto-fit action (clearing peaks + fit + charge correction)
  goes through pushUndo as a single undoable action.

SCOPE EXCLUSIONS (do not implement)

- No 3-peak vs 4-peak variant comparison or chooser
- No backend changes (fitting.py, app.py untouched)
- No file format changes
- No quality flags or review badges
- No fallback when no strong peak is found
- No batch support (single spectrum only)
- No handling of non-graphite-matrix samples
- No changes to Run Fit, Batch Fit, or Propagate Fit workflows
- No new endpoints, no backend parameters
- No new lineshape types (LA and pseudo-Voigt already exist)
- No cancel button during the fit
- No client-side fitting (all fitting goes through /api/fit)
- No elapsed-time display, no progress bar, no stage labels

ARCHITECTURAL CONSTRAINTS

- All logic lives in templates/index.html.
- Keep orchestration in one clearly named function (e.g.,
  runAutoFitC1sGraphite) with small named helpers for algorithm steps:
  isC1sTab, findGraphiteRawBE, assessLowBERegion, buildAutoFitModel,
  applyAutoFitResult.
- Reuse existing helpers where they exist: local-maxima detection,
  /api/fit invocation (match runFit()), charge-correction state updates,
  peak-list rendering, pushUndo.
- Actions menu integration must match existing menu pattern.
- Use AbortController for the 120-second HTTP timeout.

BROWSER VERIFICATION (for your plan to specify)

I can provide these test spectra:
- C1s with prominent low-BE peak (should trigger 2 low-BE peaks)
- C1s with small low-BE bump (should trigger 1 low-BE peak)
- C1s with negligible low-BE intensity (should trigger 0 low-BE peaks)
- A non-C1s tab (U4f, Cl2p) to verify menu item is grayed out
- A C1s tab with existing peaks to verify the confirmation modal appears
- A C1s tab with no peaks to verify no modal appears and fit runs directly

Success criteria for verification:
- Fitted graphite center within 0.1 eV of manually-fit graphite center on the
  same spectrum
- Applied charge correction within 0.1 eV of what I would apply manually
- Menu entry enables/disables correctly as user switches tabs
- Confirmation modal appears/doesn't appear correctly
- Spinner appears during fit and is removed on success, failure, or timeout
- Undo after a successful auto-fit restores the tab's pre-autofit state

DELIVERABLES

1. Implementation plan via /superpowers:write-plan for my review.
2. After my approval: implementation via /superpowers:execute-plan.
3. A browser-verification checklist in plain language (not dev-speak).

Stop after producing the plan. Do not begin implementation until I say go.
```

---

## Known limitations (accepted tradeoffs)

- **Server ghost computation after frontend timeout.** When the 2-minute timeout fires, the HTTP request is aborted but the server-side lmfit call continues to completion. The result is discarded. This is harmless for correctness but wasteful; unlikely to matter in practice given single-user usage.
- **No support for non-graphite-matrix samples.** Applying Auto-Fit to a C1s spectrum of a sample without a graphite matrix will produce nonsense. The feature does not detect this case. Users are expected to apply it only to appropriate samples.
- **No 3-peak adventitious option.** Defaults to 4 peaks. Users who prefer 3 must manually delete Adventitious 4 after the fit.
- **No batch support.** Single spectrum only. Batch across multiple tabs is a later phase.
- **Low-BE peak identity is undefined.** Peaks below 283.5 eV are labeled "Unknown 1" and "Unknown 2" with no attempt at chemical assignment.
- **No learning from prior fits.** The feature uses static starting positions and bounds. It does not adapt based on the user's prior fits on similar samples.
- **Background method and ROI are inputs, not outputs.** The feature respects whatever background method and ROI are currently set on the tab. It does not auto-select or modify them.

---

## Open questions (deferred)

- **Auto-fit for other core levels (O1s, Si2p, Fe2p, etc.)?** Natural extension once C1s is validated. Each new element requires its own peak model; the structure of the C1s implementation should be reusable but the specific bounds and starting positions will differ.
- **Batch auto-fit across multiple spots?** The batch propagation workflow from earlier phases was deferred specifically because it depended on a working single-spectrum atomic fit. Once this feature is in use, revisit batch.
- **Server-side cancellation?** Would eliminate the ghost computation issue but requires a backend change to `fitting.py`. Worth doing if multi-user concurrency becomes relevant; not worth doing now.
- **Learning from prior fits?** Could adapt starting positions based on the user's saved fits on similar samples. Potentially valuable but substantially more complex; not in scope for this phase.
- **Chemical assignment of low-BE peaks?** The lab has not identified these features chemically. If identification becomes possible later, the "Unknown" labels can be replaced with specific species.

---

## Rollback procedure

If this feature introduces regressions or fails to work as expected:

```bash
cd ~/xps-app
git revert clean-slate-pre-autofit..HEAD
git push origin main

ssh root@137.184.183.202 "cd /opt/xps-app && git pull && systemctl restart xps-app"
```

This reverts all commits made since the tag was placed, pushes the revert to `main`, and syncs the droplet.

---

## Related history

- **2026-04-23** — Phase 1 C1s charge-reference marker. Shipped, then rolled back as part of the broader Codex cleanup.
- **2026-04-23** — Codex-designed "Auto-Fit Graphite C1s" built via Claude Code. Rolled back completely; see `clean-slate-pre-autofit` tag.
- **2026-04-24** — This specification. First attempt at the feature after a full rollback and deliberate rescoping.

---

## Follow-up fixes (2026-04-24)

After Phase-1 shipped and was tested on real Fortier Lab data, two issues
surfaced that needed constraints added to the fit. Both were specified
2026-04-24 and implemented as additive frontend-only changes (no
`fitting.py` or `app.py` edits).

### FIX 1 — Adventitious 1 stays above graphite

**Problem.** Adv 1's previous bounds `[284.30, 285.30]` allowed it to slide
below graphite (which is bounded `[284.20, 284.80]`). Adventitious sp3
carbon is always at higher BE than graphitic sp2 — the bound was wrong.

**Resolution.** Use a static frontend lower bound (Attempt 2 in the user's
prescribed order). Adv 1's `_afCenterMin` is now `284.80` (= graphite_init
`284.50` + the chemical 0.3 eV separation). Upper bound unchanged at `285.30`.

**Trade-off.** The floor is fixed in the corrected BE frame, not relative to
graphite's *fitted* center. If graphite drifts to its `±0.3` upper bound
(284.80), adv 1's floor sits exactly at graphite's ceiling. A truly relative
constraint would need an lmfit derived-parameter mechanism that the backend
spec format does not currently support; adding it is well over 10 lines of
backend change. The static bound is sufficient for graphite-matrix samples
in practice.

### FIX 2 — Post-fit warning when graphite area < 40%

**Problem.** Real spectra were converging with graphite at 23–26% of total
fitted area. Mathematically valid; physically dubious for a graphite-
dominated sample.

**Resolution.** After a successful fit, compute
`graphite_area / sum(all_peak_areas)` from the `/api/fit`
`individual_peaks[*].params.area.value` data. If `< 0.40`, emit an amber
non-blocking `notify()` toast in addition to the green success toast.
Threshold is hardcoded; the fit is kept regardless.

**Implementation pointer.** See `docs/superpowers/plans/2026-04-24-auto-fit-c1s-followup-fixes.md`.

---

## Follow-up fixes — Round 2 (2026-04-24)

After real-data testing of the round-1 fixes, three additional issues surfaced.
This section is additive; nothing earlier in the spec is rescinded.

### ISSUE 1 (BUG): graphite-area-fraction warning toast was silently swallowed

**Symptom:** On `8 A/C1s Scan.VGD`, the peak-list AREA column reported
graphite at 33.3% — well below the 40% warning threshold added in round 1
— but no amber warning toast appeared.

**Root cause:** the round-1 helper read `json.individual_peaks[i].params.area.value`
(backend trapezoid integration of the *backend* lineshape). The user-visible
AREA column uses `_peakArea(p, be)` (frontend integration of the *frontend*
lineshape via `evalPeak`). For LA shapes the JS and Python implementations
diverge enough that the backend-side area can sit on the opposite side of
the 40% threshold from the visible AREA column.

**Fix:** rewrite the helper to use `_peakArea` against `state.peaks` and
`state.fitResult.be` — the same source the visible AREA column uses. The
warning now fires iff the AREA column shows the same number crossing the
threshold (no more disagreement). The pure decision logic is split into
`_autoFitDecideAreaWarning(peakAreas, graphiteId)` so it can be unit-tested
in isolation from state.

### ISSUE 2 (ALGORITHM CHANGE): graphite shape switched from LA(α,β,m) to Asymmetric GL

**Symptom:** With LA, the optimizer drove α to ~0.000 on the same real-data
spectrum, collapsing graphite to a symmetric line. The high-BE graphite
shoulder was then absorbed by Adventitious 1, which fattened to FWHM 2.17 eV
(unphysical for sp³ adventitious carbon).

**Root cause:** LA has three free shape parameters (α, β, m) — over-parameterised
relative to the data's information content. Worse, the round-1 frontend
declared α bounds [0.05, 0.20] but the backend hardcoded `min_=0.0, max_=0.49`
for `la_casaxps` α — the frontend bounds were silently dropped. (Same was true
for `asymmetric_gl`'s asymmetry parameter: hardcoded `[0.0, 1.0]` with no
spec-key override.)

**Fix:** Two parts.

1. *Backend plumbing* (2-line edit in `fitting.py`): the `asymmetric_gl`
   branch of `_make_peak_params` now reads `spec.get("asymmetry_min", 0.0)`
   and `spec.get("asymmetry_max", 1.0)` — same pattern already used for
   center, FWHM, amplitude. Defaults unchanged (so non-auto-fit peaks
   behave identically).

2. *Lineshape switch* (frontend): graphite uses `shape: 'asym-GL'` with
   `glMix: 30` (η, free), `asymmetry: 0.25` (α, free, bounds [0.10, 0.50]
   now actually enforced via `_afAsymMin`/`_afAsymMax` overlaid by
   `peakToBackendSpec` onto `spec.asymmetry_min`/`spec.asymmetry_max`).
   Center bounds, FWHM bounds, and amplitude bounds unchanged.

LA was kept available as a manual-mode peak shape for users who prefer it;
auto-fit no longer uses it.

### ISSUE 3 (FEATURE): peak centers are locked after a successful auto-fit

**Rationale:** Users frequently run a manual "Run Fit" after auto-fit to
refine FWHMs and amplitudes. With centers free this secondary fit drifts
the converged auto-fit positions; locking centers makes the secondary
refinement do what the user expects.

**Implementation:** After `applyAutoFitResult` succeeds, every peak's
`fixCenter` is set to `true` before the peak list re-renders. Users can
manually unlock any center via the existing padlock icon — no new UI.
Other parameters (FWHM, amplitude, η, α) remain unlocked.

### ISSUE 4 (sanity check)

The round-1 adv1 lower-bound floor (`peaks[1]._afCenterMin = 284.80`) still
applies after the lineshape change.
