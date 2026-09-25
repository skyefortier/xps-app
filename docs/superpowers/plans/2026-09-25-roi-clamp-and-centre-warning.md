# ROI past the data + peak centre outside the data — warn, don't reinterpret (2026-09-25)

Branch `fix-roi-clamp` off main `c4015ae` (DS+G evaluator deployed). Owner's
brief: "ROI CLAMP + CENTRE-OUTSIDE-DATA WARNING (one unit, UI only, no
fitting math). (1) ROI beyond the data range silently clips to the data edge,
which users read as truncation. Clamp the ROI to the data range and show a
quiet hint ('ROI extends past your data — clipped to X–Y eV'). roi-min/roi-max
are shared by manual fit and Find Peaks, so one fix covers both — verify
that. Check the saved-ROI restore path (ui.roiMin / roiMax) so loading an
old file doesn't silently change behaviour. (2) Peak centre outside the data
window: warn on the peak card. It is the only way to reach the §3c DS+G
limit. Do not auto-move the user's ROI or peaks. Warn; don't reinterpret.
Enumerate the consumer sites first."

Also in this branch: the flaky required-anchor test (commit 2e7cc33; §6).

## 1. What "clipped" means today, precisely

`getROIData()` keeps the corrected energies (raw − `ccShift`) that lie in
[roi-min, roi-max], inclusive; an empty field is ±∞. An ROI past the data
therefore selects the data up to its edge: the fit, the background, the
chart's fitted region and every area already use the CLAMPED window. The
defect is that nothing says so — the fields still read, say, 270–320 eV
over data that stop at 280–295 eV. So "clamp" is already the behaviour; the
unit makes it VISIBLE, and leaves the typed values alone (the owner: do not
auto-move the ROI).

## 2. Consumer sites — every reader of the ROI and of a peak centre

ROI readers (`roi-min`, `roi-max`, `ui.roiMin`, `ui.roiMax`, `getROIData`):

| # | site | what it reads | window semantics | this unit |
|---|---|---|---|---|
| 1 | `getROIData` | DOM fields | inclusive filter of corrected BE; empty = ±∞; min > max → EMPTY | unchanged; the hint's source of truth |
| 2 | `runFit` (Run Fit, `/api/fit`) | `getROIData` | as 1 (the request carries the filtered arrays) | unchanged |
| 3 | `runFitLocal` via Batch Fit `runPropagation` | `getROIData` on each target, target keeps its own ROI (`propagateFitUi` keep) | as 1 | unchanged; summary row notes a clipped target |
| 4 | Find Peaks `/api/analyze` payload (`fpMethodMeta` block) | DOM fields as numbers + `getCorrectedBE()` | server `app._validate_analyze_request`: `(corrected >= be_min) & (corrected <= be_max)` — the SAME inclusive mask on the SAME corrected frame | unchanged — verified identical to 1 (§3); an EMPTY field differs (page: full range; server: 400 "must be numbers") — logged, not changed |
| 5 | Find Peaks ROI auto-fill (`coverage` block) | writes `entries[0].roi.be_min/max` (curated nominal window, can exceed the data) | — | unchanged; the hint now fires when the suggested window overshoots |
| 6 | `updatePlot` (chart fitted region, preview) | `getROIData` | as 1 | hosts the hint + centre-warning refresh |
| 7 | `renderPeakList` / `_patchPeakCardsForSupport` (area %) | `getROIData` | as 1 | cards get the centre warning |
| 8 | `renderResults` fallback grid, `exportResults`, figure export, `_doSaveSpectrum`, `applyAutoFitResult`, `runAutoFitC1sGraphite`, `handleChartClick` | `getROIData` | as 1 | unchanged |
| 9 | `zoomToROI` | DOM fields, swapped if min > max | axis only | unchanged |
| 10 | `isC1sTab` (Auto-Fit enable gate) | `ui.roiMin/roiMax` MIDPOINT of the typed values | typed window, not the data it selects | unchanged — logged: with an ROI past the data the gate judges a window the fit never sees |
| 11 | `_buildEntryRenderData` Path B (stack tabs) | `ui.roiMin/roiMax`, SWAPPED if min > max | differs from 1 for an inverted ROI (1 selects nothing) | unchanged — logged; the source tab's hint says "no data selected" |
| 12 | `_captureUI` / `_restoreUI` / `toJSON` / `fromJSON` / `_doSaveFit` / `_autoFitSnapshot` / `_autoFitRestore` | read/write the field values verbatim | — | unchanged: loading a file restores the same numbers and the fit selects the same data as before; the hint is computed from the live fields and data, so an old file only GAINS a message |
| 13 | `updateChargeCorrection` | shifts both fields by the correction delta | ROI follows the data | unchanged; the hint re-evaluates after the redraw |
| 14 | `autoSetROI` / `maxROI` | write fields from the data range (`toFixed(1)`) | may land a rounding step inside or outside the data edge | unchanged; the hint's criterion (§4) ignores sub-step overshoot |
| 15 | `_STARTS_UI_FIELDS` (fit-evidence key) | `roiMin`, `roiMax` | — | unchanged (the hint writes nothing into the model or key) |
| 16 | Python twin `autofit/reference.py` `ReferenceFit._roi_bounds` / `roi_mask` | saved `ui` | inclusive, empty = ±∞ | unchanged |
| 17 | `_getSuggestedPresets` | `bg-start` / `bg-end` (not the ROI) | — | not an ROI reader (named `roiMin` locally) |

Peak-centre readers relevant to "outside the data": the card header and
summary (`renderPeakList`, patched in place by `_patchPeakCardsForSupport`).
The data window a component is fitted against is the ROI selection of
row 1, so the warning compares `p.center` with min/max of `getROIData().be`
— the grid the request carries.

## 3. "One fix covers both" — verified, with one exact qualification

Manual fit (row 2) and Find Peaks (row 4) apply the same inclusive
[min, max] filter to the same corrected energies, with one difference in
ORDER (Codex round 1): manual fit filters first and then uploads the
selection rounded to 4 dp (`uploadToBackend`), while Find Peaks uploads
the corrected energies rounded to 4 dp and the server filters those. The
selections are therefore identical except for an energy lying within
5e-5 eV of an ROI edge, which the rounding can move across it IN EITHER
DIRECTION — dropping a point (Codex round 1: 21 energies 280.00004 + 0.1 i,
ROI 280.00002–282.1, manual 21 points, Find Peaks 20) or adding one (round
2: 279.99996 + 0.1 i, ROI 280–282.1, manual 20, Find Peaks 21). It is
reachable with an ordinary ROI on a clean grid: a charge shift's float
subtraction turns 282.1 − 0.2 into 281.90000000000003, outside a typed
281.9 on the page and inside it after the upload rounds it (round 2,
run A). So the window the hint names can differ from Find Peaks' by one
point at an edge; it never differs by more, and the hint's X–Y (2 dp)
cannot show a difference that small. All three cases are pinned in
`tests/js/roi_clamp_centre_warning.test.js`. The edge divergence is
pre-existing and is not changed here (it would change Find Peaks'
request); logged with the empty-field divergence (row 4) for the
fail-open sweep.

## 4. The hint

Under the ROI inputs, one line, computed on every redraw of a spectrum tab
(hidden on stack tabs):

- ROI reaches more than ONE SAMPLING STEP past the data on either side
  (a step = median |Δ corrected BE|; within a step there is no sample the
  window could have included, so a `toFixed(1)` rounding of the edge is not
  "past the data" — a grid-relative criterion, not an intensity threshold):
  quiet — "ROI extends past your data — clipped to X–Y eV." (X, Y = the
  first and last selected energies);
- min > max: amber — "BE min is above BE max — no data is selected.";
- no overlap: amber — "ROI does not overlap your data (X–Y eV) — no data is
  selected.";
- otherwise nothing.

Measured on the committed projects (166 spectrum tabs): 30 show the quiet
hint (overshoot median 0.39 eV, max 4.85 eV; 8 over 1 eV), none is
inverted or disjoint.

## 5. The centre warning

A peak whose centre lies outside [min, max] of the selected energies gets a
badge on its card, "outside data", with a tooltip naming the centre and the
window and saying that a component centred outside the measured data is
almost always a placement error — the fit sees only its tail. Nothing is
moved. Patched in place from every redraw (never a re-render under a typing
student) and on card creation. Measured: 0 of 530 committed peaks.

## 6. The flaky test (same branch, commit 2e7cc33)

`test_component_required.py::test_a_redundant_anchor_is_supported_but_not_required`
passed 2 of 3 on main. Cause: NOT an unseeded path — every process drew the
identical seed; the variation is Trust-Region's documented last-digit
jitter. It reached the assertion because the construction did not
reproduce its own premise: starting the other components at the exact
truth lets the fit drive the anchor to residue (~0.01), so the held-others
F landed at 11–24 against the threshold of 10. Codex's original
reproduction had a large anchor (1,081–1,894, F ≈ 1e6) because that fit
stopped in a minimum where the anchor carries weight. Fixed by holding the
anchor at 1,500 (inside that range) so the fit must carry it,
parametrised over Trust-Region and Levenberg-Marquardt: F ≈ 4e7, refit
without it ~1e4× better, 5 of 5 runs of the file pass, and 20 of 20
separate-process runs of the test itself pass (after Codex round 1).
Holding the anchor POSES the premise (a fit carrying a large redundant
anchor) rather than reproducing the free local minimum Codex found; the
property under test — a refit without the component fits as well, so it
is not required, even though the held-others statistic supports it — is
the same.

## 7. Verification

- `tests/js/roi_clamp_centre_warning.test.js` (12): every hint state, the
  sub-step criterion, the corrected frame, a descending grid, the centre
  check incl. its edges and the no-data case, and structural guards that
  the new helpers assign no field value, move no peak, write no fit state
  and trigger no edit or re-render; `getROIData`'s filter and the Find
  Peaks payload pinned unchanged; Batch Fit reads the status BESIDE
  `getROIData`.
- JS suite (after round 1): 411 tests, 406 pass, 0 fail, 5 todo (the
  documented LACX gap and the scalar DS+G evaluator).
- Browser check (`browser_check_roi.py`, dev gunicorn :5151): the committed
  UCl4-graphite C1s Scan loads with its saved ROI 279.0–298.5 over data
  279.16–298.16 — fields unchanged, the fit selects the same 191 points,
  the quiet hint appears; inside → no hint; inverted and disjoint → amber;
  270–320 → hint, fields left at 270 / 320; a centre moved to 296.5 eV →
  "outside data" badge patched into the SAME card element, centre
  unmoved, cleared when it returns, present after a full re-render; a tab
  switch and back restores the fields verbatim and recomputes the hint;
  Run Fit's grid equals `getROIData()`'s; a stack tab hides the hint;
  Batch Fit onto C1s Scan_8 converges and its summary row names the
  clipped window; no page errors.
- Python suite: 993 passed, 7 skipped on the round-0 tree and again on the
  round-1 commit (5733406) and on the final commit (aafc1cc).

## 8. Codex rounds

**Round 1 (`docs/autofit/codex/roi_clamp_verdict_run{A,B}.md`): NO-GO ×2.**
Both confirmed the warn-only reading of "clamp" and found no write to the
fields, the fit inputs, saves or the evidence key. Fixed:
1. MAJOR — Find Peaks' ROI auto-fill (`_fpSyncSelectionUI`, table row 5)
   writes the fields programmatically, which fires no `input` event, so
   the hint and badges stayed stale. It now refreshes them. Every other
   programmatic writer was checked: `maxROI`, `autoSetROI`,
   `_autoFitRestore` and `updateChargeCorrection` redraw in the same
   function; three of the four callers of `_restoreUI` redraw right after,
   and the fourth — Batch Fit's already-active-target branch, missed in
   this audit and found in round 2 — now refreshes the warnings itself.
   Browser-checked on the real selection path (C 1s suggests 278–298; the
   hint names 279.16–297.96).
2. MAJOR — §3's "identical" was wrong at the rounding edge; stated exactly
   above and pinned both ways.
3. MAJOR/MINOR — the badge's tooltip revealed the centre of a component
   step (b) suppresses; it now warns without the number for an
   unsupported component. Pinned and browser-checked.
4. MINOR — closing the last tab left the hint showing (`closeTab` goes
   straight to `renderEmptyChart`, as does `updatePlot`'s no-data
   branch); `renderEmptyChart` now clears it.
Also: both reviewers noted that five runs do not prove the flake gone and
that holding the anchor poses the premise rather than reproducing the
free local minimum. The second is stated in the test's docstring; for the
first, 20 more separate-process runs are recorded in §6.

**Round 2 (`roi_clamp_r2_verdict_run{A,B}.md`): GO ×2.** Two MINORs, fixed
after the GO: Batch Fit's already-active-target branch (a fourth
`_restoreUI` caller) did not refresh the hint; and §3 still claimed
identical windows "for every ROI a user sets" — rounding can add a point
as well as drop one, and a charge shift can produce such an energy from a
clean grid. Both corrected; the reverse and charge-shift cases pinned.
Adding the Batch Fit line pushed `per_tab_state.test.js`'s re-check past
its fixed 5,000-character window (it read −1 and failed); that assertion
now reads the whole function. JS suite after the fixes: 411 tests, 406
pass, 5 todo.
