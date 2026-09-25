OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0d97a-a65e-7e50-ae31-3089c9cb7c02
--------
user
Review unit fix-roi-clamp: git diff main..HEAD (templates/index.html, tests/js/roi_clamp_centre_warning.test.js, tests/js/unsupported_components.test.js, tests/test_component_required.py, CLAUDE.md, docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md). Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

OWNER'S BRIEF (verbatim): "ROI CLAMP + CENTRE-OUTSIDE-DATA WARNING (one unit, UI only, no fitting math): 1. ROI beyond the data range: today it silently clips to the data edge, which users read as truncation. Clamp the ROI to the data range and show a quiet hint ('ROI extends past your data — clipped to X–Y eV'). roi-min/roi-max are shared by manual fit and Find Peaks, so one fix covers both — verify that. Check the saved-ROI restore path (ui.roiMin / roiMax) so loading an old file doesn't silently change behaviour. 2. Peak centre outside the data window: warn on the peak card. It is almost always a user error, and it is the only way to reach the §3c DS+G limit, so the warning closes that exposure without touching fitting math. Do not auto-move the user's ROI or peaks. Warn; don't reinterpret. Enumerate the consumer sites first (ROI and peak-centre readers), put the table in the plan and in the first Codex prompt." Also in the branch: "the pseudo-Voigt F >= 10 test passing 2 of 3 on main ... find out why this one still varies — unseeded path, or Trust-Region jitter reaching it. Fix it or make it deterministic; don't leave a flaky gate."

READ THE PLAN FIRST. Its interpretation of "clamp": getROIData() already selects only corrected energies inside [roi-min, roi-max] (inclusive; empty field = ±inf), so the fit, background, areas and exports already use the clamped window; the unit makes it VISIBLE and never rewrites the fields (the owner's "do not auto-move the user's ROI"). Challenge that interpretation if you think the brief meant something else.

THE SITE TABLE (plan §2, verbatim):

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


THE CHANGE. _roiWindowStatus() (corrected data range, parsed fields, the getROIData selection, a one-sampling-step criterion for "past", states ok/past/inverted/no-overlap/no-data); _roiHintFor / _refreshRoiHint (the #roi-hint line: quiet for 'past', amber for inverted / no-overlap); _centreOutsideData / _outsideDataBadge / _patchPeakCardsForCentre (an "outside data" badge on a card whose centre lies outside the SELECTED data, patched in place); _refreshRoiAndCentreWarnings() called at the end of updatePlot next to _refreshStartsEvidence; the stack branch of updatePlot hides the hint; renderPeakList patches badges on creation; runPropagation records _roiHintFor(_roiWindowStatus()) beside getROIData() and shows it on the target's summary row. Measured on the committed projects: 30 of 166 spectrum tabs show the quiet hint (overshoot median 0.39 eV, max 4.85 eV), 0 inverted or disjoint, 0 of 530 peaks outside their data. Browser-checked (plan §7). The flaky test: plan §6 and commit 2e7cc33 (same seed in every process; Trust-Region jitter; the construction did not reproduce its own premise; now the anchor is held at 1,500).

TRY TO BREAK
a. Site completeness: any reader of the ROI or of a peak centre the table misses (grep roi-min, roi-max, roiMin, roiMax, getROIData, be_min, be_max, and the peak-centre renderers: results table, stack legend, figure export, Find Peaks candidate preview/apply). Any path that sets the ROI fields WITHOUT a following updatePlot, so the hint goes stale (Find Peaks ROI auto-fill, Auto-Fit restore, history restore, undo, charge-correction change, project load, tab close, the "Auto from data"/"Max" buttons, programmatic .value writes)?
b. "One fix covers both": is the Find Peaks window REALLY identical to getROIData's for every numeric ROI (the server's corrected frame with cc_shift 0; float round-trip through JSON; min > max; a partially overlapping window)? The empty-field divergence is logged - is anything else different?
c. The criterion: one sampling step (median |Δ corrected BE|) past the data. Irregular grids, a 1-point spectrum, duplicate energies (step 0), a spectrum with a gap; does "past" ever fire when nothing is clipped, or stay silent when a meaningful part of the window has no data?
d. The badge: in place, never re-rendering under a typing student; stale after an edit path that does not reach updatePlot (updatePeakParam on a LINKED child? Lock All? shape switch? an alternative preview? a history-preview overlay?); unsupported components (their centre is suppressed - does the badge leak it?); linked children; the title text and escaping.
e. No reinterpretation: confirm nothing in the diff changes the fit request, Find Peaks' payload, saves, the fit-evidence key (_STARTS_UI_FIELDS), or the fields. The structural test's regexes - could a write slip past them?
f. The flaky-test fix: is the diagnosis right (seed identical; jitter) and is holding the anchor at 1,500 a faithful stand-in for the reproduction, or does it test something weaker than step (c)'s claim? Any OTHER test with the same knife-edge pattern (a threshold assertion on a Trust-Region fit of noise-free data)?
g. Docs vs code and vs measured numbers.

Finish with VERDICT: GO or VERDICT: NO-GO.

codex
I’ll read the plan first, then trace the changed code and its callers for failing cases. I’ll keep the review read-only and finish with ranked findings and a verdict.

exec
/bin/zsh -lc 'cat docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
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

## 3. "One fix covers both" — verified

Manual fit (row 2) and Find Peaks (row 4) apply the same inclusive
[min, max] filter to the same corrected energies (the page sends
`getCorrectedBE()` with `cc_shift: 0`; the server masks those numbers with
the two field values). For any numeric ROI the selected points are
identical, so the one clamped window the hint names is the window both
use. The only divergence is an EMPTY field (row 4): not an ROI past the
data, logged for the fail-open sweep.

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
without it ~1e4× better, 5 of 5 runs of the file pass.

## 7. Verification

- `tests/js/roi_clamp_centre_warning.test.js` (12): every hint state, the
  sub-step criterion, the corrected frame, a descending grid, the centre
  check incl. its edges and the no-data case, and structural guards that
  the new helpers assign no field value, move no peak, write no fit state
  and trigger no edit or re-render; `getROIData`'s filter and the Find
  Peaks payload pinned unchanged; Batch Fit reads the status BESIDE
  `getROIData`.
- JS suite: 408 tests, 403 pass, 0 fail, 5 todo (the documented LACX gap
  and the scalar DS+G evaluator).
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
- Python suite: see below after the run.

## 8. Codex rounds

(filled in as they run)

exec
/bin/zsh -lc 'git diff --stat main..HEAD' in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-2eG4diLv' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ah2omwuW' (errno=Operation not permitted)
 CLAUDE.md                                          |  11 ++
 .../2026-09-25-roi-clamp-and-centre-warning.md     | 138 +++++++++++++++++++++
 templates/index.html                               | 101 ++++++++++++++-
 tests/js/roi_clamp_centre_warning.test.js          | 135 ++++++++++++++++++++
 tests/js/unsupported_components.test.js            |   1 +
 tests/test_component_required.py                   |  31 +++--
 6 files changed, 406 insertions(+), 11 deletions(-)

exec
/bin/zsh -lc 'rg --files -g AGENTS.md -g CLAUDE.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
CLAUDE.md

exec
/bin/zsh -lc 'cat CLAUDE.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
# XPS Fitting Studio

Web application for XPS (X-ray Photoelectron Spectroscopy) peak fitting,
multi-spectrum visualization, and project management. Python/Flask backend
with an lmfit-driven peak-fitting pipeline; single-page frontend in
`templates/index.html`. Deployed at xps.fortierlab.org via a gunicorn
LaunchAgent + Cloudflare Tunnel.

## Stack

- **Backend:** Python/Flask, served by gunicorn. App factory in [app.py](app.py).
- **Fitting engine:** lmfit ≥ 1.3 (5 methods: leastsq, least_squares, nelder, differential_evolution, basinhopping).
- **Numerics:** numpy, scipy.
- **File parsing:** pandas, openpyxl (xlsx), olefile (vgd).
- **Frontend:** Single-page HTML/JS in `templates/index.html` (~8500 LOC). Vanilla JS, no build step.
- **Charting:** Chart.js 4.4 (CDN).
- **Deployment:** macOS LaunchAgent runs gunicorn on **127.0.0.1:5050** (NOT :5000 — macOS AirTunes intercepts :5000 and returns 403, so health-check :5050); Cloudflare Tunnel publishes to xps.fortierlab.org. Dev gunicorn typically runs on :5151 with `--reload` for pre-merge verification. See [DEPLOY.md](DEPLOY.md) for the full deploy sequence.

## Project Layout

```
app.py                    # Flask app factory + REST routes
fitting.py                # lmfit pipeline, lineshape impls, background algorithms
parser.py                 # File parsers (csv / tsv / txt / xy / xlsx / xls / vgd)
vgd_parser.py             # Thermo Avantage VGD binary parser (uses olefile)
templates/index.html      # Frontend — CSS + HTML + JS in one file
tests/                    # pytest suite (focused on LA + DS+G correctness)
docs/superpowers/plans/   # Agent-authored design memos and implementation plans
uploads/                  # Per-session .npz storage (gitignored)
requirements.txt
venv/                     # virtualenv (do not commit)
```

The Flask backend serves the frontend via `render_template('index.html')`
and exposes a REST API consumed by the page through fetch.

## Backend API

Per-upload sessions store parsed `(energy, counts)` arrays as compressed
`.npz` in `uploads/<session_id>.npz`. No server-side memory state —
compatible with multi-worker gunicorn.

| Method | Path | Purpose |
|---|---|---|
| `GET`    | `/`                       | Serve the frontend (`templates/index.html`). |
| `GET`    | `/api/health`             | Liveness probe. Returns `{status: "ok"}`. |
| `GET`    | `/api/peak-shapes`        | List backend-registered lineshapes (gaussian / lorentzian / pseudo_voigt_gl / asymmetric_gl / doniach_sunjic / ds_g / la_casaxps). |
| `GET`    | `/api/elements`           | Spin-orbit element presets (splitting + area ratio). |
| `POST`   | `/api/upload`             | Upload a spectrum file; returns `session_id` + downsampled preview. |
| `POST`   | `/api/parse-vgd`          | Parse Thermo Avantage VGD binary directly (no session storage). |
| `GET`    | `/api/session/<id>`       | Retrieve a stored session's preview data. |
| `DELETE` | `/api/session/<id>`       | Delete session files. |
| `POST`   | `/api/background`         | Compute background curve for a session. |
| `POST`   | `/api/fit`                | Run lmfit on a session with peak specs; returns chi², bgIntensity, bgSubtracted, fittedY, per-peak refined params + σ. |

## Frontend Architecture

### State

Module-global `state` holds the currently-active tab's working values
(swapped on tab switch by `TabManager.activateTab`):

```js
state = {
  rawBE, rawIntensity,   // full spectrum as loaded
  ccShift,               // charge-correction rigid shift (eV)
  peaks[],               // array of peak objects
  nextId,                // auto-increment peak ID
  chart,                 // Chart.js instance
  residChart,            // Residuals sub-chart instance
  fitResult,             // last fit diagnostics (be, bgIntensity, bgSubtracted, fittedY, chi, etc.)
  lineWidth,             // per-tab line width (sync of tab.lineWidth)
}
```

### Tab model

`TabManager` (a class in `templates/index.html`) holds `tabs[]` and an
`activeId`. Two tab types share the array:

- **Spectrum tab:** has `rawBE`, `rawIntensity`, `peaks`, `fitResult`, `ccShift`, `manualAnchors`, `lineWidth`, `ui` (form field snapshot incl. bg settings, ROI, charge correction method).
- **Stack tab** (`isStack: true`): viewer-only container for references to other spectrum tabs. Has `entries[{id, sourceTabId, color, visible, showFit}]`, `lineWidth`, `verticalOffset`, `_nextColorIdx`. No raw data of its own — entries resolve their source tab at render time.

Lifecycle: `createTab`, `createStackTab`, `activateTab`, `closeTab`,
`_syncActiveToRecord` (writes state-back-to-tab on switch-away). Drag-and-drop
tab reordering exists.

### Peak Object Schema — core fields

(Non-exhaustive. Additional optional fields appear for multiplet linkage, fix-flags per parameter, auto-fit asymmetry bounds, etc. Search the source for `defaultPeak` to see the full shape.)

```js
{
  id, name, color, visible,
  center, fwhm, amplitude,
  shape,       // 'Gaussian'|'Lorentzian'|'Voigt'|'GL'|'asym-GL'|'DS'|'DSG_LA'|'LACX'
  glMix,       // 0–100 (Gauss → Lorentz)
  asymmetry,   // asym-GL asymmetry index
  dsAlpha, dsGamma,                       // DS params
  laAlpha, laBeta, laM,                   // DS+G params (laAlpha=α, laBeta=Lorentzian half-width, laM=Gauss FWHM)
  caAlpha, caBeta, caM,                   // CasaXPS LA params (caM is in DATA POINTS, not eV)
  linked, linkOffset, linkRatio,          // multiplet linkage to parent peak
  isChargeReference,                      // marks this peak as the cc anchor
}
```

### Lineshapes

| ID | Description |
|----|-------------|
| `Gaussian` | Pure Gaussian |
| `Lorentzian` | Pure Lorentzian |
| `Voigt` | Pseudo-Voigt, fixed η = 0.5 on BOTH sides (A03, 2026-09-22: the request sends `gl_ratio: 0.5, fix_gl_ratio: true`; until then the server fitted η FREE from 0.3 while the page drew, integrated and exported 0.5). Use `GL` to fit the mix. |
| `GL` | Pseudo-Voigt with adjustable GL mixing (0–100) |
| `asym-GL` | GL with asymmetric FWHM broadening on high-BE side |
| `DS` | Doniach-Šunjić, `dsAlpha` (0–0.5) + `dsGamma` |
| `DSG_LA` | DS+G — DS asymmetric core convolved with Gaussian. Frontend params `laAlpha`/`laBeta`/`laM`; backend id `ds_g`. |
| `LACX` | True CasaXPS LA(α,β,m) — asymmetric Lorentzian + integer-kernel Gauss conv. Frontend params `caAlpha`/`caBeta`/`caM`; backend id `la_casaxps`. |

**What the page draws must be what the server fitted.** Two harnesses pin
it: `tests/js/lineshape_roundtrip.test.js` builds the request with the
page's own `peakToBackendSpec`, fits it with `fitting.run_fit`, applies the
result with `_applyBackendParams` and requires `evalPeakArray` on the fitted
grid to equal `individual_peaks[].y` for every shape (it also pins the
Python twin `autofit.reference.peak_to_backend_spec` to the page's builder,
shape by shape); section (D) of `tests/js/lineshape_parity.test.js` sweeps
each shape's FREE parameters across the fit's bounds. Both were added in A03
(2026-09-22) after a "Voigt" was found to be fitted with η free while drawn
at 0.5; the same harnesses then found `p.glMix || 50` / `p.dsAlpha || 0.1`
sending a mix or α of exactly 0 as the default, lmfit clipping a HELD value
to the optimiser's bounds (a DS+G m locked at 0 fitted at 0.05 —
`_make_peak_params._set` now widens a limit to a held value), and the
server clipping DS+G α to 0.495 where the page did not (`_dsgAlpha`). A
held parameter is held at its value; what the page draws is what the
server fitted. Tracked gap, `todo` in both files: LACX with m > 0 (the page draws
a rounded integer kernel; the server fits m continuously — the `caM` clamp
unit). DS+G was the other gap until 2026-09-22 (the page's quadrature
`laCasaXPS` sized its step to the Lorentzian core, not the Gaussian kernel,
and was wrong by up to 1e52 × amplitude at β = 2, m = 0.05 and 5–21 % low
in area on the very box Find Peaks emits for a graphitic C 1s line);
`dsgConvolved_array` now mirrors the server's padded-grid convolution for
every m — the same FFT circular convolution — pinned at 1e-6 across the
full β/m box on eight grids, irregular grids and centres outside the
window (`docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md`). Two
server limits found there: a DS+G m just above the 0.001 delta threshold
on a coarse grid (m ≤ 0.003 at 0.1 eV, even padded length) underflows the
kernel and returns an all-zero curve — left as is, it reads as a
zero-amplitude component and step (b) flags it; and a centre OUTSIDE the
padded grid was normalised by rounding noise — fixed 2026-09-25 by a NEW
GUARDED BRANCH (normalise by the maximum), proven byte-identical for every
in-range centre against main's function (`scripts/dsg_outside_centre_identity.py`). Details of
A03 in `docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`.

---

## Design Rules

### Thresholds on data-scaled quantities fail

XPS spans many orders of magnitude within one spectrum, so any absolute
floor, delta or exactness cutoff will misjudge at some dynamic range. Two
units learned this independently — five intensity floors on the Auto-Fit
anchor (answer: a scale-free F test), then two tolerances on that F test
(answer: none). Prefer a scale-free comparison with no tolerance. If a
check seems to need a magnitude threshold, that is evidence the check is
formulated wrong.

(Owner, 2026-09-22. The record: the anchor unit's six Codex rounds in
`docs/autofit/codex/autofit_zero_graphite_*`, the DE unit's tolerance rounds
5–8 in `de_finite_bounds_*`, and the required-refit unit's rounds 2–3 in
`autofit_required_*`. The DE unit is the same rule seen from the other
side: every χ² comparison tolerance produced reachable false failures and
no reachable protection, and the fix was to delete the comparison.)

---

## Lineshape Physics — Critical Rules

### DS (Doniach-Šunjić) Asymmetric Lineshape

The DS tail MUST always point toward **higher binding energy** (the left
side on a standard inverted BE axis). Asymmetric broadening in metals
arises from low-energy electron-hole pair excitations at the Fermi level,
which produce intensity only on the high-BE side of the core-level peak.

**Never invert the DS tail toward lower binding energy.**

Implementation convention: `dx = center − x`. The power-law term
extends the tail toward higher BE (`x > center` ⇒ `dx < 0`). The
optional exponential cutoff `gamma_asym` decays **only** on that
side — `Math.exp(gamma_asym * Math.min(dx, 0))` in the JS
`doniachSunjic`, equivalent to `exp(−gamma_asym · max(x − center, 0))`
in `fitting.py`'s `_doniach_sunjic`. When adding DS-derived shapes,
preserve this convention: the high-BE side is where `dx < 0` and where
the exponential envelope must decay.

### DS+G (formerly mislabeled "LA(α, β, m) [CasaXPS]")

The shape registered as `ds_g` in the backend (frontend enum `'DSG_LA'`,
dropdown text "DS+G") is a Doniach-Šunjić asymmetric core convolved with
a Gaussian. Despite its old label, this is NOT the CasaXPS LA
formulation. Frontend field names `laAlpha` / `laBeta` / `laM` are kept
for save-state compatibility:

| Parameter | Meaning |
|-----------|---------|
| α (`laAlpha`) | DS asymmetry index, dimensionless, 0 ≤ α < 0.5 |
| β (`laBeta`) | Lorentzian HALF-width (eV) of the DS core |
| m (`laM`) | Gaussian FWHM (eV) used in the convolution |

Tail points toward **higher** binding energy (DS physics: low-energy
electron-hole pair excitations on the high-BE side only).

Saved fits using the old `'LA'` shape value are auto-migrated on load to
`'DSG_LA'` — math is unchanged, only the label. Saved fits using the
short-lived `'DSG'` shape are auto-migrated to `'DS'` (the shape they
were actually being fit against, due to a pre-existing preview/backend
mismatch).

### LA(α, β, m) [CasaXPS] — true CasaXPS formulation

The shape registered as `la_casaxps` (frontend enum `'LACX'`, dropdown
"LA(α,β,m) [CasaXPS]") implements the genuine CasaXPS LA. Distinct field
names `caAlpha` / `caBeta` / `caM` so users do not confuse them with DS+G's
`laAlpha` / `laBeta` / `laM` (which have totally different units):

| Parameter | Meaning |
|-----------|---------|
| α (`caAlpha`) | High-BE-side exponent on the unit-amplitude Lorentzian; dimensionless, default 1.0, bounds 0.1–5.0 |
| β (`caBeta`) | Low-BE-side exponent; dimensionless, default 1.0, bounds 0.1–5.0 |
| m (`caM`) | Gaussian convolution kernel width in DATA POINTS (not eV); integer, default 50, bounds 0–499 |

α=β=1, m=0 reduces exactly to a pure Lorentzian. Increasing α
**suppresses** the high-BE tail; decreasing α extends it (BE-axis
convention; sign-flipped from CasaXPS's KE-axis description). m controls
Gaussian broadening; effective eV width ≈ (m/3) × dx where dx is the
data step size.

When implementing new LA-related lineshape parameters, **always** add
them to (use grep to find current line numbers — the file evolves):

- `defaultPeak` defaults block in `templates/index.html`
- `syncKeys` array
- `renderShapeControls` LACX param row
- `peakToBackendSpec` LACX branch
- `applyBackendResult` LACX backend-param mapping
- `runFit` JS LM free-params block + per-param clamps + linked-peak sync
- `evalPeak` switch + grid-aware `laTrueCasaXPS_array` evaluator (called via `evalPeakArray`; DS+G's grid-aware twin is `dsgConvolved_array` — a convolved shape's scalar `evalPeak` branch ignores m and must have no caller, parity guard (C))
- `_migrateLineshapeAliases` if backwards-compat alias needed

### UCl4 U 4f Asymmetric Broadening

The asymmetric broadening in the UCl4 U 4f spectrum is due to **5f²
multiplet coupling**, not metallic screening. Do not attribute it to
Kondo screening or Doniach-Šunjić metallic behaviour. Use
multiplet-split component models, not a single DS peak.

When modeling U 4f, use `asym-GL` for the U 4f₇/₂ and 4f₅/₂ main lines,
with separate symmetric GL peaks for the multiplet satellites.

### Satellite Peaks

Satellite peaks (shake-up, shake-off, plasmon loss) use **symmetric**
lineshapes — Voigt or GL. Do not apply DS or LA lineshapes to satellites.

### Linked (Multiplet) Peaks

A linked peak derives its center, amplitude, and **all lineshape
parameters** from its parent. The sync block must cover every shape
parameter — failing to add a new param breaks spin-orbit constraints
during fitting. Search for the `syncKeys` array and the `applyParams`
closure in `runFit` when adding parameters; both need the new key.

| Parent param changes | Linked peak receives |
|----------------------|----------------------|
| `center` | `parent.center + linkOffset` |
| `amplitude` | `parent.amplitude × linkRatio` |
| `fwhm` / `shape` / `glMix` / `asymmetry` / `dsAlpha` / `dsGamma` | same value |
| `laAlpha` / `laBeta` / `laM` (DS+G params) | same value |
| `caAlpha` / `caBeta` / `caM` (CasaXPS LA params) | same value |

---

## Fitting Algorithm

### Backend (default)

`POST /api/fit` runs lmfit on the server. Selectable methods: `leastsq`
(Levenberg-Marquardt), `least_squares` (Trust-Region), `nelder`,
`differential_evolution`, `basinhopping`. The UI Method dropdown
defaults to **Trust-Region** (`least_squares`); the backend falls back
to **`leastsq`** when a request omits `fit_method`. The endpoint
returns the full result including refined params, σ bounds, χ²,
`bgIntensity`, `bgSubtracted`, and `fittedY`. Linked peaks are
constrained via lmfit parameter expressions.

`differential_evolution` samples from the parameter bounds and refuses an
open one, and the page sends `amplitude_min: 0` with no `amplitude_max`
(a free DS+G centre has no default window either), so until 2026-09-19
every ordinary request for that method returned HTTP 422. For THAT METHOD
ONLY, every candidate (the first search and each perturbed refit) is now
`_search_then_refine`: differential evolution inside a generated box
(`_finite_search_box`: open sides of freely varying parameters only —
amplitude ± max(10 × the largest |background-subtracted intensity|,
2 × |start|, 1), just the ceiling for the page, which sets the floor
itself; centre = the fitted energy range, always a real interval), then —
whenever a side was generated — an UNCONDITIONAL `least_squares`
refinement from that solution under the request's own open bounds. A box
can shape an answer that lies nowhere near its sides, so nothing is
inferred from nearness. A refinement that CONVERGED is the result — a
`least_squares` fit of the requested model under the requested bounds,
which is what the default method returns; its χ² is deliberately not
compared with the boxed search's (a descent cannot end materially above
its start, but it ends a hair above an exact start sitting on a requested
bound, and every tolerance tried for that comparison produced reachable
false failures and no reachable protection — Codex rounds 5–8). If the
refinement did not converge or raised, the search result
stays marked unverified, never displaces a verified candidate in the
perturb loop, and, if it is what `run_fit` returns, is `success: false`
naming the generated limits.
Because differential evolution ignores the start and can "converge" with
a needle-narrow component outside the fitted range, each candidate also
competes with a `least_squares` fit from its own start under the request's
bounds (`_global_or_local_candidate`: verified beats unverified, then the
lower χ² wins), so this method never returns worse than the default method
would from the same start.
Generated sides are never echoed back as `min`/`max` (the page saves
returned bounds and warns within 1 % of them). A returned DE result
therefore normally carries `least_squares` uncertainties and message.
Every other method's parameters are unchanged; `/api/analyze` reaches the
same code through `options.fit_method`. Measured on committed targets with
the page's `n_perturb: 3`: 2–75 s per fit (6–7-component C 1s models
exhaust DE's evaluation budget in every search and are rescued by the
refinement). It is not a gold standard: on one 3-component B 1s target it
returned χ²ᵣ 1.92 where Trust-Region found 1.81.

**Reproducibility (2026-09-21).** Every random draw in `run_fit` — the
`n_perturb` restarts (the page sends 3; ±15 % on every varying parameter)
and the populations of `differential_evolution` and `basinhopping`, which
lmfit otherwise takes from numpy's GLOBAL generator — comes from one seed
that is a pure function of THE NUMBERS THE OPTIMISER IS HANDED
(`_request_seed`: SHA-256 of the energies, counts and the COMPUTED
background curve as little-endian float64, plus the canonical JSON of each
component's lineshape, each lmfit parameter's effective role — a
constrained one is its expression, a fixed one its value, a free one its
value and bounds — the method, solver options and `n_perturb`; tag
`xps-fit-seed-v1`). Settings are hashed by their EFFECT, never as sent, so
nothing the fit ignores can change the draws: a peak's name or colour, the
`fix_gl_ratio` the page still sends for a Gaussian, stale shape parameters
kept after a shape switch, the `endpoint_avg` a linear background does not
use, bounds of a fixed parameter, start values a link overrides, anchor
order, and the peaks' internal ids (parameter names and constraint
references are hashed by component POSITION: the page never reuses an id,
so a model rebuilt after deleting a peak would otherwise fit differently)
(in review each such no-op edit moved an area fraction by 15–45 pp
while the request was hashed as sent). It is a seed,
not an identity (32 bits collide; never a cache key). The response reports
it as `random_seed`; a caller's `fit_kws.fit_kws.seed` (integer in
[0, 2³²)) replaces it and is consumed, never forwarded to a solver.
`run_fit` itself accepts only the five supported methods, case-folded
(`_FIT_METHODS`): `/api/analyze` forwards `options.fit_method` without the
route's allowlist, and lmfit's `ampgo`, `dual_annealing`, … would draw
from the global generator. The seed value and the draws `run_fit` actually
makes (observed through Levenberg-Marquardt) are pinned by tests; numpy does not promise the same `default_rng` stream across
versions, so a failing pin after an upgrade is a release note ("saved
projects regenerate differently"), not something to re-pin silently.

What seeding buys and what it does not. "Identical request" means the same
data, model START values and settings — after a fit the page holds the
fitted values, so a second press is a different request; re-loading a
saved project and pressing Run Fit is the repeatable case. Measured on the
202 committed targets × 5 presses of the identical request, before → after:
Levenberg-Marquardt byte-identical on 145 → 202 targets;
Trust-Region on 51 → 145, area fractions moving by more than 1 pp between
presses on 8 → 0 targets, by more than 0.01 pp on 14 → 2 (worst 0.30 pp,
one U 4f scan where two presses in five land in a neighbouring minimum). Levenberg-Marquardt (MINPACK) and Nelder-Mead are
byte-identical. Trust-Region, the default, is NOT and cannot be made so by
seeding: the BLAS dot product (Apple Accelerate on the i9) rounds one unit
in the last place differently depending on where its argument sits in
memory (`w.dot(w)` gives two values over 16 alignments, `np.sum(w*w)`
one), `norm` inside scipy's `_lsq/trf.py` is the first call to return
different output for identical input, and the iteration amplifies that to
~1e-4 relative in an area at its stopping tolerance of 1e-8. Worse, the
perturbed restarts start from that jittering solution, and near a basin
boundary 1e-5 in a start is enough to send a restart into another minimum:
on the lab's targets that happened once (0.30 pp), but on a synthetic
five-component model two presses of the seeded request differed by 29 pp
(`tests/test_fit_reproducibility.py` docstring). Do not patch scipy
internals for this, and do not tighten the tolerance: ftol = xtol = gtol =
1e-12 on the same 202 × 5 gave FEWER byte-identical targets (123 vs 146)
and made two targets that converge today abort on the evaluation budget.
OWNER DECISION 2026-09-21: ACCEPT AND DISCLOSE; no unit for bit-identity.
Byte-identity is a software property, not a scientific one. The scientific
requirement — reloading a saved project and pressing Run Fit regenerates
the figure within meaningful precision — is met (2 of 202 targets move
more than 0.01 pp, worst 0.30 pp). The 29 pp synthetic case is the SAME
phenomenon as the local-minimum problem (near a basin boundary 1e-4 of
jitter flips the answer), so the scattered-starts cross-check unit is
already the mitigation: it exposes exactly those fits. Do not build a
second thing (a reviewer tried a deterministic perturbation base: identical
starts, results still differed; a reproducible-arithmetic BLAS is a large
project with uncertain payoff). Disclosure wording, for docs and the
student note: identical requests now give identical results on real data
in practice; the underlying arithmetic is not bit-reproducible, so a fit
sitting near a boundary between two solutions can still resolve
differently, and that is precisely the situation the multiple-starts check
is designed to surface.

**Scattered-starts check (step (a) of the 2026-09-21 unit; plan in
`docs/superpowers/plans/2026-09-21-scattered-starts-and-unsupported-components.md`).**
Every Run Fit with ≥ 2 unlinked components sends `n_starts: 3`; after the
normal fit (unchanged: THE FIT is what the student's method returned,
byte-identical with and without the check, and `n_starts` is not part of
the seed) `run_fit` runs three more fits of the SAME method from scattered
starts — drawn from a third stream of the request seed, anchored to the
REQUEST's start (amplitude ×/÷ 3, width ×/÷ 1.5, free centres ± 0.5 eV,
other bounded parameters redrawn inside the middle 90 % of their range),
clamped into the request's bounds (amplitude sign kept). "Same solution" =
every area fraction within 1 pp and every centre within 0.1 eV, COMPONENT
BY COMPONENT by id — no permutations: "C-O" and "C=O" trading places is a
different chemical reading even when both are GL lines. The response's
`starts` reports how many reached
the fit, how many ended in a solution that is NOT better (counted, never
listed — ~25 % of fits have one and listing them would train people to
ignore the panel), and `alternatives`: solutions whose χ²ᵣ is lower by more
than 0.1 %, each with its own areas and every component's centre shift
from the STUDENT'S START. Not run for `differential_evolution` /
`basinhopping`, single-component models, a fit that did not converge,
Batch Fit or the local fallback; a failure inside the check never fails
the fit. Page: one line under the Results table ("2 of 3 scattered starts
reached this solution; …" — counts, never certification language) and,
when alternatives exist, an "Other solutions found" table (your fit first;
the largest move named, amber > 0.5 eV, red > 1 eV) with Preview (the
history-preview overlay, on a copy) and "Use this solution": explicit, one
undo entry, recorded as `fitResult.chosenAlternative`, and ATOMIC by
construction — the alternative is only the START of an ordinary server fit
(`runFit({startPeaks})`); the live model is written by that fit's success
path and by nothing else, so a fit that fails, does not converge, is
discarded on a tab switch or cannot reach the server (no local fallback
here) leaves peaks and result exactly as they were, and σ, exports and
saves come through the one existing path. Every row shows EACH component's
own area % and its own move from the student's start. The evidence is
BOUND TO THE FIT THAT PRODUCED IT by COMPARISON, never by hand
invalidation (so no edit path can be forgotten): `fitResult.startsModelKey`
covers every peak field the request reads (incl. the auto-fit asymmetry
bounds) AND the fit context — background type and window, endpoint
averaging, Shirley iterations, ROI, manual anchors, charge shift — taken
after the result is applied and persisted with the counts.
`_startsIfCurrent(fr, key)` is the single accessor (`_startsLiveKey()` for
the active tab, `_startsRecordKey(t)` for a record): after any such change,
an undo or a history restore that brings back other values, the panel says
the comparison no longer applies, nothing can be previewed or applied, an
open alternative preview is dropped (`_dropStaleAltPreview`), and
saves/exports carry neither counts nor the recorded choice. A name, colour
or visibility is not part of a fit and does not invalidate it. `runFit`
captures the same key before its first await and DISCARDS a result whose
model or context was edited while it ran (the peak controls stay editable
during a fit; a newly locked centre would otherwise keep its edited value
under the server's statistics). The trigger (`n_starts`) is decided with
the other request inputs before the first await. In the RED band — and only there — it first asks,
naming the component and the distance ("This solution moves C-O by
−1.47 eV from where you placed it. Apply?"): a lower χ²ᵣ bought by
relocating a component is the measured trap (8-JT C1s Scan_1/5/6/7), and
the app must never substitute a chemical interpretation because it scored
better. Saves persist the counts (`_startsForSave`), not the alternatives'
parameter sets (regenerable from the seeded request). Measured with the
shipped code on the 202 committed targets: an alternative is shown on 0 of
94 re-fits of a saved solution and 6 of 84 not-yet-fitted starts (7.1 %;
three of them in the red band), median +0.54 s per Run Fit (90th
percentile +1.8 s). It shows that a decomposition is not unique; it cannot
say which one is correct, and four known targets defeat even ten starts.

### Client-side fallback

`runFitLocal` in `templates/index.html` is a JS Levenberg-Marquardt
implementation used as a fallback when the backend is unreachable, and
the ONLY engine Batch Fit uses. Central-difference Jacobian (centre
step scaled by the peak width), active-set step (parameters pushed into a
box wall are held fixed), max 3000 iterations. Terminates on a gradient
cosine < 1e-6, on actual and predicted relative χ² reductions both < 1e-6
in agreement, or on a relative step < 1e-8, and only after a
feasible-descent CERTIFICATE passes: no single free parameter moved by
1e-3 (scaled, inside its box) reduces the residual by more than 1e-6 of
its value, otherwise that point is taken and iteration continues. The
certificate is a coordinate (single-parameter) check, not a proof of a
local minimum along coupled directions; no exit is exempt from it.
Damping exhaustion is a FAILURE. Poisson-weighted since unit W1
(2026-09-18): it minimises Σ(w·r)² with w = 1/√max(raw counts, 1), the
server's weighting, so its statistic is a real χ²ᵣ (objective
`poisson_weighted_chi_square`); results saved by unit A0 were unweighted
and stay labelled "Residual variance". It produces no uncertainties, and
the integer-clamped `caM` is not optimised (carried at its start value).

**A local result is a STARTING POINT, not a reportable result** (keyed on
`engine: 'local'`, helpers `_isLocalFit` / `_isLocalModel` /
`_localFitCaveat`). Measured in unit W1 and RE-MEASURED after A03
(2026-09-22, `docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`,
generator `scripts/local_server_gap.js`): weighted, it matches the server on
GL-type models (≤ 4 meV, ≤ 1.4 % area on the lab's C1s scans) and on Voigt
components (fixed η = 0.5 on both sides since A03: on the 5 of 9 committed
U 4f targets where both engines reach the same minimum every component
agrees within 4.3 meV, 2.6 % FWHM, 2.0 % area, 0.12 pp — W1 had measured up
to 20.8 % area on the Voigt satellites); it still differs on the other 4
U 4f targets (satellite areas up to 8.9 %, 0.77 pp) for two reasons,
separated by a control arm (the server with every LA m held at its start):
on one target the `caM` clamp (`caM` held at its start locally while the
server fits m continuously; holding m on the server closes the gap), on
three the local descent stopping at a χ²ᵣ 5–13 % above the server's from
the same start with the same free parameters — a worse minimum, the
"several minima" case (both engines' amplitude floor is 0 since unit
step (b)). Both engines weight by
√intensity whether the data are counts or CPS (a convention, not a
calibrated uncertainty for rates); the formula is the same but the inputs
are not bit-identical, because `uploadToBackend` rounds intensities to
2 dp before the server weights them. A03 is done and the designation
STAYS on both grounds; the `caM` clamp is the next unit, the worse-minimum
outcome is recorded for the local-engine work after it, and the label is
reconsidered only on a re-measurement after both. (The amplitude-bound change
DECIDED 2026-09-18 — `docs/findings/2026-09-fit-determinacy.md` §3 — is
implemented: unit step (b), 2026-09-22, below.) The same file records that a
converged server fit is not ground truth: on a committed C 1s scan the
server's default method stopped in a local minimum the local engine
avoided.
See `docs/superpowers/plans/2026-09-18-local-engine-poisson-weighting.md`.

**"Not supported by the data" (unit step (b), 2026-09-22; owner decision
2026-09-18).** A component whose amplitude the fit drove to its floor,
pinned on a bound or fitted to numerical residue is an explicit OUTCOME —
the fit did not determine it — and its centre, width and σ are not reported
as if they were. The statement needs no intensity floor (six were tried for
the Auto-Fit anchor and each rejected real components or accepted residue):
with the other components held at their fitted values, removing this one
must make the fit significantly worse — `fitting._component_support`, the
Auto-Fit anchor's F statistic (F ≥ 10; `SUPPORT_MIN_F`). The SERVER computes
it once per component (`individual_peaks[].support = {f, delta_chi2,
supported}`; a linked component `follows` its parent); the page's twin
`_componentSupportFromResponse` recomputes it from any response carrying
`counts`, `fitted_y` and the component's curve; the LOCAL engine computes
the same statistic from its own residuals and weights
(`_componentSupportCore`), so a component driven to the zero floor by Batch
Fit is an outcome there too. Linked components follow their ROOT ancestor
whatever the request order. The verdict is a property of the fit that
produced it, CONDITIONAL on the other components as fitted, so it is bound
to that fit: `p.support.fitKey` is the model-plus-context key
(`_startsLiveKey()`) taken after the values are applied, and
`_isUnsupported(p)` compares it with the live key at every read — after
the student edits any peak, lock, link, the background, ROI, anchors or
charge correction, or an undo brings back other values, nothing is
suppressed or excluded until a new fit writes a new verdict (a verdict
without a key, from an older save, is never applied; exports write a
Status only from a CURRENT verdict — stale means "not established", never
"supported"). When the key changes, `_refreshStartsEvidence` compares the
set of flagged components with what EACH consumer has rendered — sidebar
badges, Results rows and chart datasets carry the peak id / flag — and
re-renders the ones that differ — the sidebar is PATCHED IN PLACE (header, summary values, area % over the currently supported components, badge), never re-rendered, because the student may be typing in a card (a caller that already redrew the sidebar,
such as Lock All or Add Peak, therefore still gets Results, Quantify and the
chart refreshed); it runs from the lock toggles, Lock All and every
`updatePlot` (which passes `fromPlot` so the chart is not rebuilt from
inside its own rebuild). Auto-Fit locks
every centre and refines the charge shift AFTER the result is applied, so
it re-stamps its verdicts (`_restampSupport`) — those changes are part of
its result. `p.support` is persisted with the peak (saves spread the peak
whole); Batch Fit's copy and a `.fit.json` import set it to `null`
(parameters on other data: nothing established); stack tabs judge a source
component against the SOURCE record's key. Sites
(`_isUnsupported`): sidebar card (badge; centre/width "—"; excluded from the
area total), Results table (greyed row, no centre/width/σ, area kept,
percentage "—", note beneath; percentages over supported components),
uncertainty panel (one rule-0 warning, before the per-parameter alarms and
instead of the neutral "locked" note Auto-Fit's centre lock would produce),
Quantify (no row; listed beneath: "an atomic percentage of 0.0 % would be a
measurement claim"), chart / stack / figure legend labels, no figure label at
the component's (zero) maximum, CSV/XLSX (Status column, empty cells, no
At%, WARNING line — and no width of any kind: DS+G β / m and LA m are widths
too), TSV (column kept, header says so), the scattered-starts table ("Your
fit" row shows neither area % nor a move for it, and it is never the
largest move; an alternative's components are unjudged and shown as they
are). Both engines' amplitude
floor is 0 (`runFitLocal`'s clamp was 1). Measured on the 202 committed
targets: 3 of 752 components (three C 1s re-fits, F 0.95–3.9), 0 of 95 fresh
starts — but committed projects are survivorship-biased (a collapsed
component may have been deleted before saving), so the working-fit rate is
plausibly higher. Known limits, the anchor check's: a gross single-channel
artefact can mark a real component unsupported; REDUNDANCY UNDER OVERLAP is
not detected (a refit without the component is the test; step (c) does it
for the Auto-Fit anchor).

**Acceptance rule for fit outcomes (unit A0, 2026-09-15):** a fit OUTCOME
from Run Fit, Batch Fit or the local engine is shown, stored or exported
only if it converged. `runFitLocal` works on a copy and commits only on
success, returning `{success, iterations, chiReduced}`; `runFit`
treats `success !== true` from `/api/fit` as a failed fit and falls back to
the local engine only on a transport failure, never on a server-side
error. A RESULT IS DISCARDED IF THE MODEL WAS EDITED WHILE THE FIT WAS RUNNING
(2026-09-22; a correctness fix for EVERY Run Fit, shipped with the
scattered-starts check but independent of it). The peak controls stay
editable during a fit. `runFit` captures the model-plus-context key
(`_startsLiveKey()`: every peak field the request reads, background type and
window, endpoint averaging, ROI, anchors, charge shift) beside `peakSpecs`,
before its first await, and after the tab-owner check refuses to apply a
result if that key changed: amber notice, "Fit discarded (model edited)",
previous peaks and result kept. Before this, a centre changed and locked
mid-fit kept its edited value (`applyBackendResult` honours locks) under the
server's χ², σ and fitted curve for a different model.
Not covered by this rule (separate units): model replacement that
keeps an older result (Find Peaks apply in the default window, undo/redo)
and loaded files without convergence provenance. From the initial commit
until this unit the local LM step had the wrong sign and returned the
starting model as "Fit complete"; see
`docs/superpowers/plans/2026-09-15-a01-local-lm-proof.md` and
`scripts/scan_batch_fit_signature.py`, which lists suspected saved files.

## Background Methods

| Backend id | Notes |
|---|---|
| `shirley` | Iterative Shirley (Proctor & Sherwood, *Anal. Chem.* **1982**, 54, 13, 2438–2439). Default. |
| `smart` | Shirley variant with smarter endpoint handling. |
| `smart_exp` | Experimental Shirley variant. |
| `shirley_linear` | Shirley with a linear-fallback bridge. |
| `linear` | Straight line between ROI endpoints. |
| `tougaard` | Single-pass universal cross-section K(T) = B·T/(C+T²)², B = 2866 eV², C = 1643 eV² (Tougaard, *Surf. Interface Anal.* **1988**, 11, 453; kernel max at √(C/3) ≈ 23.4 eV). Order-robust (either BE direction); amplitude anchored to the data at the high-BE edge. JS twin `tougaardBackground` must stay in numerical agreement (pinned by `tests/js/tougaard_twin.test.js`). |
| `manual` (frontend only) | User-placed anchor points; `manualAnchorBackground` in JS. |

Use Shirley for standard core-level regions. Linear only when the
spectral window is very narrow and featureless.

## Quantification

Peak areas are integrated numerically (trapezoidal over BE grid). RSF
(relative sensitivity factor) corrections are applied in the Quantify
tab. Atomic percent = (area/RSF) / Σ(area/RSF) × 100.

---

## Charge Correction

Reference: **C 1s adventitious carbon at 284.8 eV** is the default. The
UI dropdown also offers **C 1s graphitic carbon (sp²) at 284.5 eV** as
an alternative; the Auto-Fit C1s Graphite feature uses 284.5 eV as the
fixed reference for the graphitic component it identifies.

A rigid shift (`state.ccShift`) is applied to all binding energies
before fitting. The corrected axis is produced by `getCorrectedBE()`.

Auto-Fit C1s Graphite derives that shift from the FITTED centre of its
"Graphite" component, so the data must SUPPORT that component
(`_autoFitGraphiteIsSupported`), in the one sense that needs no intensity
threshold: removing it from the fitted model must make the fit to the
server's own data significantly worse. From the `/api/fit` response alone —
`counts`, `fitted_y`, the component's curve `individual_peaks[].y`, the
server's weights 1/max(counts, 1) — F = ((χ²_without − χ²_with)/p) /
(χ²_with/dof), p = the component's free parameters; supported means
χ²_without > χ²_with and F ≥ 10 (or χ²_with = 0). A component driven to
zero, pinned on its bound or fitted to numerical residue has
χ²_without ≤ χ²_with — removing it costs nothing (true of every such
reproduction in `docs/autofit/codex/autofit_zero_graphite_*`); resolved
anchors measured F from 1.7e2 (behind a 300 000-count one-channel spike) to
1e9, and the 70 committed Graphite models F ≥ 1.1e3. Otherwise the auto-fit
is rejected and rolled back with a red notice before any charge-correction
input is touched. Until 2026-09-21 only the centre was checked (±0.3 eV of
284.50), which a zero-amplitude component always satisfies because its
centre is bounded to that window. Do NOT replace this with an intensity
floor: five were tried (relative to the strongest component, the raw span,
the background-subtracted maximum, the raw magnitude, the upload's 0.01
resolution) and each rejected real anchors or accepted residue. The same
statistic is the natural definition for the planned "component not
supported by the data" outcome. Fixtures are real `run_fit` responses:
`scripts/gen_autofit_anchor_fixtures.py` →
`tests/js/fixtures/autofit_anchor.json`. SCOPE: it answers "do the data
support this component?", not "is it graphite?".

KNOWN LIMITS of that check (owner decision 2026-09-21: shipped with them
after six Codex rounds, all NO-GO; do NOT write a seventh rule — six
intensity floors failing is the data saying no threshold on intensity can
mean "zero" independently of the data):
- It REJECTS A REAL ANCHOR when the fitted region carries a gross
  single-channel artefact (a spike of millions of counts, or a dead
  zero-count channel): that channel dominates χ²_with and drags F under 10.
  The user gets a red notice and a rolled-back model; removing the artefact
  or narrowing the ROI recovers. A recoverable refusal beats main's old
  failure mode — a non-existent component silently setting the energy
  reference for a whole spectrum.
- REDUNDANCY UNDER OVERLAP was out of scope for the support check
  (χ²_without holds the other components fixed) and is CLOSED by step (c),
  2026-09-22: Auto-Fit's request carries `require_component: <Graphite id>`
  and the server refits the model WITHOUT that component from the others'
  fitted values under the request's bounds (`fitting._component_required`,
  through the run's own fitter `fit_model` — so differential evolution's
  box/refinement machinery and the request seed apply to the refit too;
  everything linked to the removed component goes with it, transitively;
  every retained parameter is created before any expression is assigned,
  so a chain of links in any request order resolves; NO tolerance of any
  kind on the comparison — a delta floor relative to the data's power and
  then an "exactness" cutoff on the reduced fit each masked a resolved
  anchor at high dynamic range, Codex rounds 2–3, the DE unit's lesson
  again. Known limit, accepted: on NOISE-FREE data whose full fit is exact
  to machine precision F is meaningless and a truly redundant component can
  read "required"; real data never fit to machine precision) and returns
  `required: {required, f, chi2_with, chi2_without_refit, refit_converged}`
  with the same F ≥ 10 rule. `applyAutoFitResult` refuses a supported-but-
  not-required anchor exactly like an unsupported one, before any
  charge-correction input is touched ("refitting the other components
  without it fits the data as well"); the anchor id is captured with the
  other request inputs before the first await. One extra fit, Auto-Fit only; the fit
  itself is unchanged by the check, and a check that did not run never
  blocks. On the 70 committed Graphite models the anchor is required on
  all 70 (F ≥ 54, median 6.1e3 — a measurement with `require_component` over
  the un-committed target file, not a test); the round-6 reproduction (two symmetric GL
  lines, no graphite: support F ~ 1e6 with the others held, refit without it
  equal to rounding) is now refused.
- One rounding-residue construction still passes (unrounded manual
  background a rounding step under data the upload flattened; F ≈ 280).

LOGGED FOR ONE LATER UNIT (untouched): Auto-Fit anchors on a one-channel
spike, and on a featureless plateau under background None, and still
derives a charge correction from it; a rejected Auto-Fit (any reason)
leaves its `pushUndo()` entry and a cleared redo stack behind. The spike
case shares a root with the false rejection above — gross single-channel
artefacts are unhandled generally — so if this becomes a despike /
outlier-flag unit, those three are one piece of work.

Adventitious carbon referencing (284.8 eV) is the default for
convenience but has known criticisms in the XPS literature — the C 1s
position of adventitious carbon depends on surface chemistry and is not
a true universal standard. Graphitic carbon (284.5 eV) or a known
internal reference is preferable when available.

Additional fixed references in the dropdown: Au 4f₇/₂ (83.98 eV), B 1s
for B₂O₃ (192.99 eV), N 1s for BN (398.31 eV), B 1s for BN (190.74 eV),
plus a free-entry "Custom reference" option.

## File Formats Supported

| Extension | Notes |
|-----------|-------|
| `.csv`, `.tsv`, `.txt`, `.xy` | Whitespace/comma/tab/semicolon delimited. Backend `parseCSV` + frontend equivalent. |
| `.xlsx`, `.xls` | Backend `parseXLSX` (openpyxl); frontend XLSX.js for client-side parse. |
| `.vgd` | Thermo Avantage binary. Backend uses `vgd_parser.py` (olefile); frontend `parseVGD` does a heuristic Float32 extraction. |

Spectrum columns: first = BE (eV), second = intensity (counts/s). Rows
with non-numeric or missing values are skipped.

---

## Multi-Tab + Project Save/Load

The app supports multiple spectrum tabs simultaneously. Project state
saves to `.proj.json` (< 5 tabs) or `.proj.zip` (≥ 5 tabs; manifest +
per-spectrum JSON inside the archive). Schema version 3.

- **Tab IDs** are preserved across save/load. Field is top-level
  `data.activeId`; the saved active tab is re-activated on load.
- **Stack tabs persist.** Saved with `isStack: true` + their entries
  + line-width + offset; spectrum tab data lives elsewhere and is
  reached by `entry.sourceTabId` at render time.
- **Stale stack entry pruning:** if a saved stack references a source
  tab that didn't load, the entry is dropped and an amber toast tells
  the user.

## Spectrum Stacking

A stack tab visualizes multiple spectra on shared axes with per-entry
fit visualization (envelope + shaded peak components, raw-level).
The whole stack chart's behavior is governed by a small set of
invariants worth knowing before touching the code:

- **Dataset keying.** Each entry contributes 2 + 2×N_peaks datasets to
  the chart, each tagged with a stable `_stackKey` of the form
  `<entryId>:raw`, `<entryId>:env`, `<entryId>:peak:<peakId>`,
  `<entryId>:pbg:<peakId>` (the `:pbg` is a transparent fill anchor for
  the matching peak's shaded fill — Chart.js requires a real dataset
  for fill targets). Keys let in-place updates target specific datasets
  without relying on array indices, which shift when datasets reorder.

- **In-place updates preserve zoom.** `_updateStackChart` mutates
  `data` / `hidden` / `borderWidth` / `fill` on existing datasets and
  calls `chart.update('none')`. `_renderStackChart` is the destroy +
  rebuild path, used only on entry add/remove or when the active chart
  is the wrong chart (see next bullet).

- **Chart-type discriminator.** `state.chart._xpsStackTabId` is set on
  every stack chart at creation. `_updateStackChart` rebuilds whenever
  the active chart isn't tagged for the current stack tab — guards
  against in-place updates running against a stale spectrum chart or
  a different stack's chart.

- **3 render-data paths** in `_buildEntryRenderData` cover fresh
  backend fits (Path A: use fitResult.fittedY directly), fresh local-LM
  fits (Path A2: compose envelope from peaks + bgIntensity), and
  post-load reconstruction (Path B: recompute bg from raw via the
  source tab's persisted bg settings using `_computeBackgroundForSource`).
  Render data is cached on the entry as `_renderDataCache` and
  invalidated only at `_renderStackChart` rebuild.

- **Layered visibility model.** Per-entry `entry.showFit` gates whether
  the entry participates in fit visualization at all; the toolbar pills
  (Envelope, Individual Peaks, Fill, Bkgrd Sub) act as global layer
  switches on top. The `peak-fit-control` CSS class hides peak/fit
  toolbar items entirely on stack tabs (Run Fit, Batch Fit, etc.).

## Toolbar Highlights (frontend)

- **Line Width slider** (right panel, always visible): per-tab,
  persisted. Drives raw + per-peak `borderWidth`; envelope uses
  `min(width + 1, 6)` so it stays visually distinct.
- **Vertical Offset slider** (right panel, stack tabs only): vertical
  separation between visible entries.
- **`⇅ Organize Tabs`** (chart toolbar): sorts spectrum tabs as
  Survey → element-alphabetical → Other; stack tabs cluster at the
  end as a block, preserving their relative order.
- **`+ Stack` / `+ Add Spectrum ▾`** (chart toolbar): create a new
  empty stack and add open spectrum tabs to the active stack.
- **Auto-Fit C1s Graphite** (Actions menu): one-click C1s peak model
  + charge correction. Enabled only when the active ROI midpoint is in
  270–315 eV.
- **ROI past the data / centre outside the data** (2026-09-25, warn only):
  `getROIData()` has always clamped an ROI to the data it selects; the page
  now SAYS so under the ROI fields ("ROI extends past your data — clipped
  to X–Y eV" when a field reaches more than one sampling step past the
  data; amber when min > max or the window misses the data) and badges a
  peak card whose centre lies outside the selected data ("outside data").
  Neither the fields nor the peaks are ever moved; the fit, Find Peaks
  (same inclusive mask on the same corrected energies) and saves read the
  ROI exactly as before. `_roiWindowStatus` / `_refreshRoiAndCentreWarnings`,
  refreshed in place from `updatePlot`; plan
  `docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md`.
- **Manual anchor background**: place anchors on the chart for
  per-spectrum hand-tuned background curves; persisted as
  `tab.manualAnchors`.

## Tests

```
tests/test_la_continuous_m.py   # LA(α,β,m) continuity across integer-m kernel widths
tests/test_la_short_input.py    # LA edge cases on very-short input arrays
tests/test_mixed_ds_lacx_e2e.py # End-to-end: a fit with both DS+G and CasaXPS LA peaks
```

Run via `pytest tests/`.

## Reference Energies for Common Regions

There is **no demo-spectrum loader** in the app (a `loadDemo(...)`
function does not exist — earlier versions of this file were stale).
Typical regions for hand-testing:

| Region | Window | Notes |
|--------|--------|-------|
| Fe 2p | 700–740 eV | Fe(0) at 706.6, Fe(III) at 710.5, satellite at 713.5 |
| U 4f | 370–415 eV | UCl4-like U(IV); 4f₇/₂ at 380.9, 4f₅/₂ at 391.8 (offset 10.9 eV) |
| C 1s | 280–295 eV | sp², sp³, C-O, C=O, COOH components; charge ref at 284.8 eV |

## Known Issues

- Legacy document-level tooltip handlers call `e.target.closest(...)`
  without checking that the event target is an Element
  (`templates/index.html` around the `data-xps-tip` listeners); events
  targeting non-Elements throw `e.target.closest is not a function`.
  Needs an `instanceof Element` guard in a future pass.
- Gunicorn `--reload` watches Python files only — **edits to
  `templates/index.html` are NOT picked up** outside Flask debug mode
  because Jinja caches compiled templates per worker. Restart the dev
  gunicorn after template changes before browser-verifying.

## Development Workflow

- Develop on feature branches off `main`.
- Production gunicorn serves whatever is on disk at
  `templates/index.html`. Browser-verify changes on a separate dev
  gunicorn on **port 5151** (run with `--reload`) before merging.
- Merge to main only after browser verification.
- Design memos and implementation plans live under
  `docs/superpowers/plans/` and are committed alongside the changes
  they describe.

exec
/bin/zsh -lc "rg -n 'roi-min|roi-max|roiMin|roiMax|getROIData|be_min|be_max|function updatePeakParam|function _patchPeakCardsForSupport|function renderPeakList|function updatePlot' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
2064:                <input type="number" id="roi-min" value="706" step="0.5" oninput="updatePlot();_recomputeAutoFitMenuState()">
2068:                <input type="number" id="roi-max" value="726" step="0.5" oninput="updatePlot();_recomputeAutoFitMenuState()">
3177:        roiMin: minBE, roiMax: maxBE,
3210:            endpointAvg: '1', roiMin: '', roiMax: '',
3395:        min: document.getElementById('roi-min').value,
3396:        max: document.getElementById('roi-max').value
3465:        active.ui.roiMin = data.roi.min || '';
3466:        active.ui.roiMax = data.roi.max || '';
3831:      roiMin:      document.getElementById('roi-min')?.value || '',
3832:      roiMax:      document.getElementById('roi-max')?.value || '',
3851:    set('roi-min', ui.roiMin);
3852:    set('roi-max', ui.roiMax);
4652:// rule getROIData uses for the ROI. This is the single definition shared by
4994:    const roiMinEl = document.getElementById('roi-min');
4995:    const roiMaxEl = document.getElementById('roi-max');
4996:    const roiMinVal = parseFloat(roiMinEl.value);
4997:    const roiMaxVal = parseFloat(roiMaxEl.value);
4998:    if (!isNaN(roiMinVal)) roiMinEl.value = (roiMinVal - delta).toFixed(1);
4999:    if (!isNaN(roiMaxVal)) roiMaxEl.value = (roiMaxVal - delta).toFixed(1);
5061:function getROIData() {
5062:  const roiMinRaw = parseFloat(document.getElementById('roi-min').value);
5063:  const roiMaxRaw = parseFloat(document.getElementById('roi-max').value);
5065:  const roiMin = isNaN(roiMinRaw) ? -Infinity : roiMinRaw;
5066:  const roiMax = isNaN(roiMaxRaw) ?  Infinity : roiMaxRaw;
5070:    if (corrBE[i] >= roiMin && corrBE[i] <= roiMax) {
5079:// WARN, NEVER REINTERPRET. getROIData() already selects the corrected
5080:// energies inside [roi-min, roi-max], so an ROI past the data is clamped to
5092:  const lo = parseFloat(document.getElementById('roi-min').value);
5093:  const hi = parseFloat(document.getElementById('roi-max').value);
5094:  const { be } = getROIData();
5167:  document.getElementById('roi-min').value = lo.toFixed(1);
5168:  document.getElementById('roi-max').value = hi.toFixed(1);
5178:  document.getElementById('roi-min').value = _roiLo.toFixed(1);
5179:  document.getElementById('roi-max').value = _roiHi.toFixed(1);
5442:  const roiMin = parseFloat(document.getElementById('roi-min').value);
5443:  const roiMax = parseFloat(document.getElementById('roi-max').value);
5444:  if (isNaN(roiMin) || isNaN(roiMax)) return;
5445:  const xMin = Math.min(roiMin, roiMax);
5446:  const xMax = Math.max(roiMin, roiMax);
5568:  const roiMin = parseFloat(document.getElementById('bg-end')?.value || 0);
5569:  const roiMax = parseFloat(document.getElementById('bg-start')?.value || 9999);
5570:  const beMin = Math.min(roiMin, roiMax);
5571:  const beMax = Math.max(roiMin, roiMax);
5766:  const { be, inten } = getROIData();
5964:function updatePeakParam(id, key, value) {
6086:function renderPeakList() {
6105:  const { be: _roiBE } = (typeof getROIData === 'function' && state.rawBE.length) ? getROIData() : { be: [] };
6961:    roiMinDom:    document.getElementById('roi-min')?.value || '',
6962:    roiMaxDom:    document.getElementById('roi-max')?.value || '',
6998:      roiMin: snap.roiMinDom, roiMax: snap.roiMaxDom,
7018:  set('roi-min',   snap.roiMinDom);
7019:  set('roi-max',   snap.roiMaxDom);
7206:function _patchPeakCardsForSupport() {
7209:  const { be: roiBE } = (typeof getROIData === 'function' && state.rawBE && state.rawBE.length) ? getROIData() : { be: [] };
7306:  const { be: be2, inten: inten2 } = getROIData();
7396:  const { be: corrBE, inten } = getROIData();
7398:    notify('ROI is empty. Set roi-min and roi-max before auto-fit.', 'red', true);
7448:    const { be: be2, inten: inten2 } = getROIData();
7541:  let lo = parseFloat(ui.roiMin);
7542:  let hi = parseFloat(ui.roiMax);
7588:const _STARTS_UI_FIELDS = ['bgType', 'bgStart', 'bgEnd', 'shirleyIter', 'endpointAvg', 'roiMin', 'roiMax'];
7823:  const { be, inten } = getROIData();
8603:  if ((!be || !be.length) && typeof getROIData === 'function' && state.rawBE.length) {
8604:    be = getROIData().be;
8923://       by ROI-filtering corrBE using src.ui.roiMin/roiMax, recompute
8971:    // Path B: post-load — derive ROI-window be from rawBE + ui.roiMin/Max,
8974:    const roiMinV = parseFloat(src.ui && src.ui.roiMin);
8975:    const roiMaxV = parseFloat(src.ui && src.ui.roiMax);
8977:    if (isFinite(roiMinV) && isFinite(roiMaxV)) {
8978:      const lo = Math.min(roiMinV, roiMaxV);
8979:      const hi = Math.max(roiMinV, roiMaxV);
9407:function updatePlot() {
9432:  const { be, inten } = getROIData();
10161:      min: document.getElementById('roi-min').value,
10162:      max: document.getElementById('roi-max').value
10197:  const { be, inten } = getROIData();
10681:              endpointAvg: '1', roiMin: '', roiMax: '',
10706:        shirleyIter: '5', roiMin: '', roiMax: '',
10866:  const { be, inten } = getROIData();
10923:  const { be, inten } = getROIData();
12093:    const roiSt = _roiWindowStatus();    // warn only: the fit below uses getROIData() exactly as before
12094:    const { be, inten } = getROIData();
15496:    document.getElementById('roi-min').value = entries[0].roi.be_min;
15497:    document.getElementById('roi-max').value = entries[0].roi.be_max;
15714:      roi: { be_min: parseFloat(document.getElementById('roi-min').value),
15715:             be_max: parseFloat(document.getElementById('roi-max').value) },
15999:  // unfit-preview path (getROIData() + client-side computeBackground()),
16001:  // CURRENT #roi-min/#roi-max, i.e., the full window Find Peaks just used.

exec
/bin/zsh -lc "rg -n 'def _validate_analyze_request|cc_shift|be_min|be_max' app.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
220:def _validate_analyze_request(body: dict, upload_folder: str) -> _AnalyzeContext:
253:        cc_shift = float(body.get("cc_shift", 0.0))
255:        raise _AnalyzeError("cc_shift must be a number")
256:    corrected = energy - cc_shift   # frontend getCorrectedBE convention
265:        be_min = float(roi.get("be_min", float(corrected.min())))
266:        be_max = float(roi.get("be_max", float(corrected.max())))
268:        raise _AnalyzeError("roi.be_min/be_max must be numbers")
269:    mask = (corrected >= be_min) & (corrected <= be_max)
910:          "cc_shift":       0.0,          // frontend charge shift (corrected = raw − cc_shift)
911:          "roi":            {"be_min": ..., "be_max": ...},   // corrected frame

exec
/bin/zsh -lc 'git diff main..HEAD -- templates/index.html tests/js/roi_clamp_centre_warning.test.js tests/js/unsupported_components.test.js tests/test_component_required.py CLAUDE.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-xCJSmpJY' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-yGiC5N91' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index d4550d8..7e8b8bd 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -814,6 +814,17 @@ invariants worth knowing before touching the code:
 - **Auto-Fit C1s Graphite** (Actions menu): one-click C1s peak model
   + charge correction. Enabled only when the active ROI midpoint is in
   270–315 eV.
+- **ROI past the data / centre outside the data** (2026-09-25, warn only):
+  `getROIData()` has always clamped an ROI to the data it selects; the page
+  now SAYS so under the ROI fields ("ROI extends past your data — clipped
+  to X–Y eV" when a field reaches more than one sampling step past the
+  data; amber when min > max or the window misses the data) and badges a
+  peak card whose centre lies outside the selected data ("outside data").
+  Neither the fields nor the peaks are ever moved; the fit, Find Peaks
+  (same inclusive mask on the same corrected energies) and saves read the
+  ROI exactly as before. `_roiWindowStatus` / `_refreshRoiAndCentreWarnings`,
+  refreshed in place from `updatePlot`; plan
+  `docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md`.
 - **Manual anchor background**: place anchors on the chart for
   per-spectrum hand-tuned background curves; persisted as
   `tab.manualAnchors`.
diff --git a/templates/index.html b/templates/index.html
index 07977d7..80ea07a 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -816,6 +816,11 @@
   }
 
   /* Multiplet link indicator */
+  /* ROI past the data / centre outside the data (2026-09-25): warn, never move */
+  .roi-hint { font-size: 10px; line-height: 1.4; color: var(--text3); margin: 2px 0 6px; }
+  .roi-hint.amber { color: var(--amber); }
+  .outside-data-badge { font-size: 9px; padding: 1px 4px; border-radius: 3px; margin-left: 4px;
+    color: var(--amber); border: 1px solid var(--amber); white-space: nowrap; cursor: help; }
   .unsupported-badge {
     font-size: 9px;
     padding: 1px 5px;
@@ -2063,6 +2068,7 @@
                 <input type="number" id="roi-max" value="726" step="0.5" oninput="updatePlot();_recomputeAutoFitMenuState()">
               </div>
             </div>
+            <div id="roi-hint" class="roi-hint" style="display:none" aria-live="polite"></div>
             <div style="display:flex;gap:6px">
               <button class="btn btn-sm" onclick="autoSetROI()">Auto from data</button>
               <button class="btn btn-sm" onclick="maxROI()" title="Set ROI to the full raw spectrum range">Max</button>
@@ -5069,6 +5075,90 @@ function getROIData() {
   return { be, inten };
 }
 
+// ── ROI past the data / centre outside the data (2026-09-25) ─────────────
+// WARN, NEVER REINTERPRET. getROIData() already selects the corrected
+// energies inside [roi-min, roi-max], so an ROI past the data is clamped to
+// the data in every fit, background, area and export — the defect was that
+// nothing said so. This reports the window actually used; it writes nothing
+// back into the fields, the peaks or the fit-evidence key. Find Peaks sends
+// the same two numbers against the same corrected energies to a server mask
+// of the same inclusive form, so this one window is the one both use.
+// Plan: docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md.
+function _roiWindowStatus() {
+  const corrBE = (typeof getCorrectedBE === 'function' && state.rawBE && state.rawBE.length) ? getCorrectedBE() : [];
+  if (!corrBE.length) return { state: 'no-data' };
+  let dMin = Infinity, dMax = -Infinity;
+  for (const v of corrBE) { if (v < dMin) dMin = v; if (v > dMax) dMax = v; }
+  const lo = parseFloat(document.getElementById('roi-min').value);
+  const hi = parseFloat(document.getElementById('roi-max').value);
+  const { be } = getROIData();
+  let sMin = Infinity, sMax = -Infinity;
+  for (const v of be) { if (v < sMin) sMin = v; if (v > sMax) sMax = v; }
+  const base = { dMin, dMax, lo, hi, sMin, sMax, n: be.length };
+  if (Number.isFinite(lo) && Number.isFinite(hi) && lo > hi) return { ...base, state: 'inverted' };
+  if (!be.length) return { ...base, state: 'no-overlap' };
+  // one sampling step = median |Δ corrected BE|: within a step there is no
+  // sample the window could have included, so a toFixed(1) rounding of an
+  // edge is not "past the data" (a grid-relative criterion, not a threshold
+  // on intensity)
+  const d = [];
+  for (let i = 1; i < corrBE.length; i++) d.push(Math.abs(corrBE[i] - corrBE[i - 1]));
+  d.sort((a, b) => a - b);
+  const step = d.length ? (d.length % 2 ? d[(d.length - 1) / 2] : 0.5 * (d[d.length / 2 - 1] + d[d.length / 2])) : 0;
+  const past = (Number.isFinite(lo) && lo < dMin - step) || (Number.isFinite(hi) && hi > dMax + step);
+  return { ...base, step, state: past ? 'past' : 'ok' };
+}
+function _roiHintFor(st) {
+  const f = v => v.toFixed(2);
+  if (st.state === 'past') return { cls: '', text: `ROI extends past your data — clipped to ${f(st.sMin)}–${f(st.sMax)} eV.` };
+  if (st.state === 'inverted') return { cls: 'amber', text: 'BE min is above BE max — no data is selected.' };
+  if (st.state === 'no-overlap') return { cls: 'amber', text: `ROI does not overlap your data (${f(st.dMin)}–${f(st.dMax)} eV) — no data is selected.` };
+  return null;
+}
+function _refreshRoiHint(st) {
+  const el = document.getElementById('roi-hint');
+  if (!el) return;
+  const h = st ? _roiHintFor(st) : null;
+  if (!h) { if (el.style.display !== 'none') { el.style.display = 'none'; el.textContent = ''; } return; }
+  if (el.textContent !== h.text) el.textContent = h.text;
+  el.className = 'roi-hint' + (h.cls ? ' ' + h.cls : '');
+  el.style.display = '';
+}
+// A component centred outside the selected data: the fit sees only its tail.
+// Almost always a placement error — and the one way to reach the DS+G
+// normalisation limit (plan 2026-09-22-dsg-page-evaluator §3c).
+function _centreOutsideData(p, st) {
+  return !!(st && st.n > 0 && Number.isFinite(p.center) && (p.center < st.sMin || p.center > st.sMax));
+}
+function _outsideDataBadge(p, st) {
+  const tip = `Centre ${p.center.toFixed(2)} eV lies outside the fitted data (${st.sMin.toFixed(2)}–${st.sMax.toFixed(2)} eV). `
+    + 'A component centred outside the measured data is almost always a placement error: the fit sees only its tail. Nothing has been moved.';
+  return `<span class="outside-data-badge" data-peak-id="${p.id}" title="${_escAttr(tip)}">outside data</span>`;
+}
+// Patched IN PLACE (the student may be typing in a card): add, update or
+// remove each card's badge; never re-render the list.
+function _patchPeakCardsForCentre(st) {
+  for (const p of state.peaks) {
+    const item = document.getElementById('peak-item-' + p.id);
+    if (!item) continue;
+    const name = item.querySelector('.peak-name');
+    if (!name) continue;
+    const badge = name.querySelector('.outside-data-badge');
+    const out = _centreOutsideData(p, st);
+    if (out) {
+      const html = _outsideDataBadge(p, st);
+      if (!badge) name.insertAdjacentHTML('beforeend', html);
+      else { const tmp = document.createElement('span'); tmp.innerHTML = html; const t = tmp.firstChild.getAttribute('title'); if (badge.getAttribute('title') !== t) badge.setAttribute('title', t); }
+    } else if (badge) badge.remove();
+  }
+}
+function _refreshRoiAndCentreWarnings() {
+  const st = _roiWindowStatus();
+  _refreshRoiHint(st);
+  _patchPeakCardsForCentre(st);
+  return st;
+}
+
 function maxROI() {
   if (!state.rawBE.length) return;
   const be = getCorrectedBE();
@@ -6054,6 +6144,7 @@ function renderPeakList() {
     item.addEventListener('mouseenter', () => _highlightChartPeak(p.id, true));
     item.addEventListener('mouseleave', () => _highlightChartPeak(p.id, false));
   }
+  if (state.rawBE && state.rawBE.length) _patchPeakCardsForCentre(_roiWindowStatus());
 }
 
 function renderPeakForm(p) {
@@ -9324,6 +9415,7 @@ function updatePlot() {
     const _emptyEl = document.getElementById('stack-empty-state');
     const _canvas = document.getElementById('mainChart');
     if (isStackTab(_activeTab)) {
+      _refreshRoiHint(null);   // a stack tab has no ROI of its own
       _updateStackChart(_activeTab);
       return;
     } else {
@@ -9477,6 +9569,7 @@ function updatePlot() {
   }
 
   _refreshStartsEvidence(false, true);   // background / ROI controls only repaint the chart: keep the visible consumers honest (fromPlot: the chart itself is being rebuilt)
+  _refreshRoiAndCentreWarnings();         // ROI past the data / centre outside the data: warn, never move
   // History snapshot preview overlay (cyan dashed, drawn on top)
   if (_historyPreview && _historyPreview.peaks && _historyPreview.peaks.length && plotBE.length) {
     const prevPeakY = evalAllPeaks(plotBE, _historyPreview.peaks);
@@ -11997,6 +12090,7 @@ async function runPropagation() {
     }
 
     // Run local fit
+    const roiSt = _roiWindowStatus();    // warn only: the fit below uses getROIData() exactly as before
     const { be, inten } = getROIData();
     const bgI = computeBackground(be, inten);
     const bgSub = inten.map((v, idx) => v - bgI[idx]);
@@ -12008,7 +12102,7 @@ async function runPropagation() {
     // Read the statistic from the fit's own return value, not from live
     // state: the active tab can change while the fit runs.
     const ok = !!(outcome && outcome.success);
-    results.push({ name: tgt.name, ok,
+    results.push({ name: tgt.name, ok, roiHint: _roiHintFor(roiSt),
                    chi: ok && Number.isFinite(outcome.chiReduced) ? outcome.chiReduced : null,
                    message: ok ? null : ((outcome && outcome.message) || 'local fit did not converge') });
 
@@ -12023,9 +12117,10 @@ async function runPropagation() {
   const nOk = results.filter(r => r.ok).length;
   const nFail = results.length - nOk;
   prog.textContent = `Batch complete: ${nOk} converged as starting points, ${nFail} not fitted. Run Fit on each spectrum before reporting.`;
+  const roiNote = r => r.roiHint ? ` <span class="roi-hint${r.roiHint.cls ? ' ' + r.roiHint.cls : ''}" style="display:inline">${_escHtml(r.roiHint.text)}</span>` : '';
   summary.innerHTML = results.map(r => r.ok
-    ? `<div class="prop-row">${_escHtml(r.name)}: converged &mdash; &#967;&#178;<sub>r</sub> = ${r.chi != null ? r.chi.toFixed(3) : 'n/a'} (local fit: a starting point, not a reportable result)</div>`
-    : `<div class="prop-row" style="color:var(--red,#f87171)">${_escHtml(r.name)}: NOT fitted &mdash; ${_escHtml(r.message)} (model copied, no result stored)</div>`
+    ? `<div class="prop-row">${_escHtml(r.name)}: converged &mdash; &#967;&#178;<sub>r</sub> = ${r.chi != null ? r.chi.toFixed(3) : 'n/a'} (local fit: a starting point, not a reportable result)${roiNote(r)}</div>`
+    : `<div class="prop-row" style="color:var(--red,#f87171)">${_escHtml(r.name)}: NOT fitted &mdash; ${_escHtml(r.message)} (model copied, no result stored)${roiNote(r)}</div>`
   ).join('') + `<div class="prop-row" style="color:var(--red,#f87171);margin-top:4px">&#9888; Charge corrections marked in red need verification</div>`;
   summary.style.display = 'block';
   btn.disabled = false;
diff --git a/tests/js/roi_clamp_centre_warning.test.js b/tests/js/roi_clamp_centre_warning.test.js
new file mode 100644
index 0000000..0bf778c
--- /dev/null
+++ b/tests/js/roi_clamp_centre_warning.test.js
@@ -0,0 +1,135 @@
+// ROI past the data / peak centre outside the data (2026-09-25).
+// WARN, NEVER REINTERPRET: the helpers report the window getROIData()
+// already uses and write nothing back. Plan:
+// docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md.
+const { test } = require('node:test');
+const assert = require('node:assert');
+const fs = require('node:fs');
+const path = require('node:path');
+
+const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
+const lines = html.split('\n');
+function extractFn(name) {
+  const re = new RegExp('^(async )?function ' + name + '\\(');
+  const start = lines.findIndex(l => re.test(l));
+  assert.ok(start >= 0, `function ${name} not found`);
+  let depth = 0, seen = false;
+  for (let i = start; i < lines.length; i++) {
+    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
+    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
+  }
+  assert.fail('unbalanced ' + name);
+}
+const NAMES = ['getCorrectedBE', 'getROIData', '_roiWindowStatus', '_roiHintFor', '_refreshRoiHint', '_centreOutsideData', '_outsideDataBadge', '_escAttr'];
+function makeEnv({ rawBE, ccShift = 0, roiMin, roiMax }) {
+  const dom = { 'roi-min': { value: String(roiMin) }, 'roi-max': { value: String(roiMax) },
+    'roi-hint': { textContent: '', className: 'roi-hint', style: { display: 'none' } } };
+  const document = { getElementById: id => dom[id] || null };
+  const state = { rawBE, rawIntensity: rawBE.map(() => 100), ccShift, peaks: [] };
+  const fns = new Function('document', 'state', NAMES.map(extractFn).join('\n\n') + '\nreturn { ' + NAMES.join(', ') + ' };')(document, state);
+  return { ...fns, dom, state };
+}
+const grid = (lo, hi, step) => Array.from({ length: Math.round((hi - lo) / step) + 1 }, (_, i) => +(lo + step * i).toFixed(6));
+const DATA = grid(280, 295, 0.05);
+
+test('an ROI inside the data: no hint', () => {
+  const e = makeEnv({ rawBE: DATA, roiMin: 282, roiMax: 293 });
+  const st = e._roiWindowStatus();
+  assert.equal(st.state, 'ok');
+  assert.equal(e._roiHintFor(st), null);
+  e._refreshRoiHint(st);
+  assert.equal(e.dom['roi-hint'].style.display, 'none');
+});
+
+test('an ROI past the data by more than one step: the quiet hint names the window actually used', () => {
+  const e = makeEnv({ rawBE: DATA, roiMin: 270, roiMax: 320 });
+  const st = e._roiWindowStatus();
+  assert.equal(st.state, 'past');
+  const h = e._roiHintFor(st);
+  assert.equal(h.cls, '', 'quiet, not amber');
+  assert.equal(h.text, 'ROI extends past your data — clipped to 280.00–295.00 eV.');
+  e._refreshRoiHint(st);
+  assert.equal(e.dom['roi-hint'].style.display, '');
+  assert.equal(e.dom['roi-hint'].textContent, h.text);
+});
+
+test('one side past the data is enough; the window named is the selected data', () => {
+  const e = makeEnv({ rawBE: DATA, roiMin: 283.2, roiMax: 300 });
+  const st = e._roiWindowStatus();
+  assert.equal(st.state, 'past');
+  assert.equal(e._roiHintFor(st).text, 'ROI extends past your data — clipped to 283.20–295.00 eV.');
+});
+
+test('a sub-step overshoot (a toFixed(1) rounding of the data edge) is not "past the data"', () => {
+  const e = makeEnv({ rawBE: grid(279.97, 295.03, 0.1), roiMin: 279.9, roiMax: 295.1 });   // 0.07 eV past each edge, step 0.1
+  assert.equal(e._roiWindowStatus().state, 'ok');
+});
+
+test('min above max: amber, no data selected (getROIData selects nothing)', () => {
+  const e = makeEnv({ rawBE: DATA, roiMin: 293, roiMax: 282 });
+  const st = e._roiWindowStatus();
+  assert.equal(st.state, 'inverted');
+  assert.equal(e.getROIData().be.length, 0);
+  assert.deepEqual(e._roiHintFor(st), { cls: 'amber', text: 'BE min is above BE max — no data is selected.' });
+});
+
+test('an ROI that misses the data entirely: amber, names the data range', () => {
+  const e = makeEnv({ rawBE: DATA, roiMin: 700, roiMax: 740 });
+  const st = e._roiWindowStatus();
+  assert.equal(st.state, 'no-overlap');
+  assert.deepEqual(e._roiHintFor(st), { cls: 'amber', text: 'ROI does not overlap your data (280.00–295.00 eV) — no data is selected.' });
+});
+
+test('empty fields mean the full range (as getROIData): no hint', () => {
+  const e = makeEnv({ rawBE: DATA, roiMin: '', roiMax: '' });
+  assert.equal(e._roiWindowStatus().state, 'ok');
+});
+
+test('the window is in the CORRECTED frame (raw − ccShift), as the fit and Find Peaks use it', () => {
+  const e = makeEnv({ rawBE: DATA, ccShift: 1.5, roiMin: 278.5, roiMax: 293.5 });   // corrected data 278.5–293.5
+  assert.equal(e._roiWindowStatus().state, 'ok');
+  const e2 = makeEnv({ rawBE: DATA, ccShift: 1.5, roiMin: 280, roiMax: 295 });     // past the corrected top by 1.5 eV
+  const st = e2._roiWindowStatus();
+  assert.equal(st.state, 'past');
+  assert.equal(e2._roiHintFor(st).text, 'ROI extends past your data — clipped to 280.00–293.50 eV.');
+});
+
+test('a descending acquisition behaves the same', () => {
+  const e = makeEnv({ rawBE: DATA.slice().reverse(), roiMin: 270, roiMax: 320 });
+  const st = e._roiWindowStatus();
+  assert.equal(st.state, 'past');
+  assert.equal(e._roiHintFor(st).text, 'ROI extends past your data — clipped to 280.00–295.00 eV.');
+});
+
+test('centre outside the SELECTED data is flagged; inside, at the edges, or with no data selected is not', () => {
+  const e = makeEnv({ rawBE: DATA, roiMin: 282, roiMax: 293 });
+  const st = e._roiWindowStatus();
+  for (const [c, out] of [[287, false], [282, false], [293, false], [281.9, true], [293.05, true], [310, true]]) {
+    assert.equal(e._centreOutsideData({ id: 1, center: c }, st), out, `centre ${c}`);
+  }
+  const eNone = makeEnv({ rawBE: DATA, roiMin: 700, roiMax: 740 });
+  assert.equal(eNone._centreOutsideData({ id: 1, center: 310 }, eNone._roiWindowStatus()), false, 'no selected data: nothing to compare against (the ROI hint speaks instead)');
+  const badge = e._outsideDataBadge({ id: 7, center: 310 }, st);
+  assert.match(badge, /class="outside-data-badge" data-peak-id="7"/);
+  assert.match(badge, /Centre 310\.00 eV lies outside the fitted data \(282\.00–293\.00 eV\)/);
+  assert.match(badge, /Nothing has been moved/);
+});
+
+// WARN, NEVER REINTERPRET — structural guards on the new helpers
+test('the helpers write nothing: no assignment to a field value, a peak or the fit state', () => {
+  for (const name of ['_roiWindowStatus', '_roiHintFor', '_refreshRoiHint', '_centreOutsideData', '_outsideDataBadge', '_patchPeakCardsForCentre', '_refreshRoiAndCentreWarnings']) {
+    const src = extractFn(name);
+    assert.doesNotMatch(src, /\.value\s*=(?!=)/, `${name} assigns an input value`);
+    assert.doesNotMatch(src, /\bp\.(center|fwhm|amplitude)\s*=(?!=)/, `${name} moves a peak`);
+    assert.doesNotMatch(src, /state\.(peaks|fitResult|ccShift)\s*=(?!=)/, `${name} writes the fit state`);
+    assert.doesNotMatch(src, /\b(pushUndo|updatePeakParam|renderPeakList|updatePlot)\(/, `${name} triggers an edit or a re-render`);
+  }
+});
+
+test('the fit and Find Peaks still read the ROI exactly as before (getROIData / the two field values)', () => {
+  const g = extractFn('getROIData');
+  assert.match(g, /corrBE\[i\] >= roiMin && corrBE\[i\] <= roiMax/, 'inclusive filter unchanged');
+  assert.match(html, /roi: \{ be_min: parseFloat\(document\.getElementById\('roi-min'\)\.value\),\s*\n\s*be_max: parseFloat\(document\.getElementById\('roi-max'\)\.value\) \}/, 'Find Peaks payload unchanged');
+  const rp = extractFn('runPropagation');
+  assert.match(rp, /const roiSt = _roiWindowStatus\(\);[^\n]*\n\s*const \{ be, inten \} = getROIData\(\);/, 'Batch Fit reads the status beside, not instead of, getROIData');
+});
diff --git a/tests/js/unsupported_components.test.js b/tests/js/unsupported_components.test.js
index 81bf8a8..7e002bd 100644
--- a/tests/js/unsupported_components.test.js
+++ b/tests/js/unsupported_components.test.js
@@ -113,6 +113,7 @@ function pageEnv(fns, extraArgs = {}) {
     _isLocalFit: () => false, _localFitCaveat: () => '', _localFitDetail: () => '', _startsPanelHtml: () => '', _validateUncertainties: () => ({ warnings: [], info: [] }),
     renderQuantify: () => {}, recalcQuantify: () => {}, _detectPeakRSF: () => ({ key: 'C 1s', rsf: 1 }), SCOFIELD_RSF: { 'C 1s': 1 }, notify: () => {},
     _clearDisallowedChargeRef: () => {}, _updateLocalModelBanner: () => {}, _updateLockAllBtn: () => {}, renderPeakForm: () => '', _highlightChartPeak: () => {},
+    _roiWindowStatus: () => ({ state: 'ok', n: 0 }), _patchPeakCardsForCentre: () => {},   // the ROI / centre warnings: tests/js/roi_clamp_centre_warning.test.js
     _isChargeRefAllowed: () => false, _fitStatLabel: () => 'χ²ᵣ', _isUnweightedLocal: () => false, _applyStatCaption: () => {}, _applyStatDisplay: () => {},
     _CHISQ_TOOLTIP: '', _LOCALFIT_TOOLTIP: '', _startsSummaryText: () => '', _startsChosenText: () => '', _startsIfCurrent: () => null,
     _isLocalModel: () => false, _updateRFactorUI: () => {}, _activeTab: () => ({}), _renderRFactorPanel: () => '', _statIsChi: true,
diff --git a/tests/test_component_required.py b/tests/test_component_required.py
index 78b4ef7..e48cac4 100644
--- a/tests/test_component_required.py
+++ b/tests/test_component_required.py
@@ -49,21 +49,36 @@ KW = dict(background_method="manual", manual_bg=[[280.0, 1000.0], [295.0, 1000.0
           fit_kws={"method": "least_squares"})
 
 
-def test_a_redundant_anchor_is_supported_but_not_required():
+@pytest.mark.parametrize("method", ["least_squares", "leastsq"])
+def test_a_redundant_anchor_is_supported_but_not_required(method):
     # Codex, Auto-Fit anchor unit round 6 (run B): two symmetric GL lines at
-    # 284.8/1.4 eV and 283.3/1.8 eV, no graphite. Auto-Fit's model puts an
-    # asymmetric-GL Graphite at 284.5 with the ±0.3 eV window; the fit gives it
-    # a large amplitude (F ~ 1e6 with the others HELD) — yet the other two
-    # components fit the data to rounding precision without it.
+    # 284.8/1.4 eV and 283.3/1.8 eV, no graphite. In that reproduction the
+    # full fit kept a LARGE Graphite (amplitude 1,081-1,894, held-others F ~
+    # 1e6) because it stopped in a minimum where the anchor carries weight;
+    # yet the other two components fit the data to rounding precision
+    # without it.
+    #
+    # The premise is posed deterministically by HOLDING the anchor at 1,500
+    # (inside that observed range). Until 2026-09-25 this test instead
+    # started the other components at the exact truth, which lets the fit
+    # drive the anchor to residue (~0.01) - the premise never formed, the
+    # held-others F landed at 11-24 against the threshold of 10, and
+    # Trust-Region's documented last-digit jitter (identical seed in every
+    # process) moved it across: the test passed 2 of 3 runs on main. Now
+    # F ~ 4e7 and the refit without the anchor is ~1e4 x better, under both
+    # methods, in every process.
     y = np.round(1000 + _gl(X, 10000, 284.8, 1.4) + _gl(X, 15000, 283.3, 1.8), 2)
-    specs = _autofit_model(1000, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
-    res = fitting.run_fit(X, y, specs, require_component="1", **KW)
+    specs = _autofit_model(1500, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
+    specs[0]["fix_amplitude"] = True
+    kw = dict(KW, fit_kws={"method": method})
+    res = fitting.run_fit(X, y, specs, require_component="1", **kw)
     assert res["success"] is True
     g = next(ip for ip in res["individual_peaks"] if ip["id"] == "1")
     assert g["support"]["supported"] is True, "held-others statistic passes: that is the gap"
+    assert g["support"]["f"] > 1e6, g["support"]["f"]           # far from the threshold, not on it
     req = res["required"]
     assert req["ran"] is True and req["refit_converged"] is True
-    assert req["chi2_without_refit"] <= req["chi2_with"] * 1.001
+    assert req["chi2_without_refit"] < 1e-2 * req["chi2_with"]
     assert req["required"] is False
 
 

exec
/bin/zsh -lc "sed -n '5920,6152p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
  updatePlot();
}

function clearAllPeaks() {
  if (!state.peaks.length) return;
  if (!confirm('Are you sure you want to clear all peaks?')) return;
  pushUndo();
  state.peaks = [];
  state.fitResult = null;
  { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }
  renderPeakList();
  updatePlot();
}

function getPeak(id) { return state.peaks.find(p => p.id === id); }

function unlinkPeak(id) {
  if (!confirm('Unlink this peak? It will become fully independent.')) return;
  pushUndo();
  const p = getPeak(id);
  if (!p) return;
  p.linked = null;
  renderPeakList();
  updatePlot();
}

// Handler for the linked-peak "Ratio (I₂/I₁)" input.
// Clamps to [0.01, 2] so the user can't accidentally zero out both peaks by
// typing 0 (which historically back-propagated a zero amplitude to the parent).
// A ratio of 0 is not physically meaningful for a linked multiplet anyway —
// if the satellite truly has no intensity, it should not be linked.
function _onLinkRatioInput(id, rawVal) {
  const child = getPeak(id);
  if (!child || !child.linked) return;
  const parent = getPeak(child.linked);
  if (!parent) return;
  let r = parseFloat(rawVal);
  if (!isFinite(r) || r < 0.01) r = 0.01;
  if (r > 2) r = 2;
  child.linkRatio = r;
  child.amplitude = parent.amplitude * r;
  updatePeakParam(id, 'amplitude', child.amplitude);
}

function updatePeakParam(id, key, value) {
  _pushUndoDebounced();
  const p = getPeak(id);
  if (!p) return;
  // asymmetry: clamp to the backend's own bound (fitting.py np.clip(asymmetry,
  // 0, 1)) — a plain assignment let out-of-range values (e.g. pasted/loaded)
  // sit on the peak until a backend fit result overwrote them.
  if (key === 'asymmetry') value = Math.max(0, Math.min(1, value));
  p[key] = value;

  const syncKeys = ['center','amplitude','fwhm','shape','glMix','asymmetry','dsAlpha','dsGamma','laAlpha','laBeta','laM','caAlpha','caBeta','caM'];
  if (syncKeys.includes(key)) {
    // Resolve canonical parent: if p is a child, find its parent first
    let parent = p.linked ? getPeak(p.linked) : p;
    if (!parent) parent = p;

    if (p.linked && parent) {
      // p is a child — back-propagate changed value to parent
      if (key === 'center') parent.center = p.center - p.linkOffset;
      else if (key === 'amplitude') {
        // Only divide back to the parent when the ratio is meaningfully >0.
        // Otherwise (child was zeroed or ratio is tiny) leave the parent alone.
        if (p.linkRatio && p.linkRatio > 1e-6) {
          parent.amplitude = p.amplitude / p.linkRatio;
        }
      }
      else parent[key] = p[key];
      renderPeakControls(parent);
    }

    // Forward-propagate from parent to all children (including p if it is one)
    for (const child of state.peaks.filter(q => q.linked === parent.id)) {
      if (key === 'center') child.center = parent.center + child.linkOffset;
      else if (key === 'amplitude') child.amplitude = parent.amplitude * child.linkRatio;
      else child[key] = parent[key];
      if (child.id !== id) renderPeakControls(child);
    }
  }
  _invalidateFittedY();
  updatePlot();
}

function toggleLock(id, key, btn) {
  const p = getPeak(id);
  if (!p) return;
  p[key] = !p[key];
  btn.className = 'lock-btn' + (p[key] ? ' locked' : '');
  btn.innerHTML = p[key] ? '&#x1f512;' : '&#x1f513;';
  btn.title = (p[key] ? 'Unlock' : 'Lock') + ' during fitting';
  _updateLockAllBtn();
  _refreshStartsEvidence(true);      // a lock is part of the fitted model
}

const LOCK_ALL_KEYS = ['fixCenter', 'fixFwhm', 'fixAmplitude', 'fixAsymmetry', 'fixGlMix', 'fixDsAlpha', 'fixDsGamma'];

function _lockAllStats() {
  let locked = 0, total = 0;
  for (const p of state.peaks) {
    if (p.linked) continue;
    for (const k of LOCK_ALL_KEYS) {
      total++;
      if (p[k]) locked++;
    }
  }
  return { locked, total };
}

function toggleAllLocks() {
  if (!state.peaks.length) return;
  const { locked, total } = _lockAllStats();
  // Majority unlocked → lock all; majority locked → unlock all
  const newVal = locked <= total / 2;
  for (const p of state.peaks) {
    if (p.linked) continue;
    for (const k of LOCK_ALL_KEYS) p[k] = newVal;
  }
  renderPeakList();
  _refreshStartsEvidence(true);
}

function _updateLockAllBtn() {
  const wrap = document.getElementById('peak-lock-all-wrap');
  const btn = document.getElementById('btn-lock-all');
  if (!wrap || !btn) return;
  const hasLockable = state.peaks.some(p => !p.linked);
  if (!hasLockable) { wrap.style.display = 'none'; return; }
  wrap.style.display = '';
  const { locked, total } = _lockAllStats();
  if (locked > total / 2) {
    btn.innerHTML = '&#x1f513; Unlock All';
    btn.title = 'Unlock all fit parameters on all peaks';
  } else {
    btn.innerHTML = '&#x1f512; Lock All';
    btn.title = 'Lock all fit parameters on all peaks';
  }
}

// ═══════════════════════════════════════════════════
// PEAK LIST UI
// ═══════════════════════════════════════════════════
// The per-peak "Charge-correction reference (C 1s graphite)" checkbox is
// only meaningful when the user is on a C 1s spectrum AND the global
// charge-correction method is set to graphite. When either condition is
// false, the checkbox is hidden completely AND any peak that previously
// held the marker is silently unchecked, so re-entering the valid mode
// gives a clean unchecked state rather than a stale stored value.
function _isChargeRefAllowed() {
  const cm = document.getElementById('cc-method');
  if (!cm || cm.value !== 'c1s') return false;
  const tab = (typeof tabManager !== 'undefined' && tabManager.activeId)
    ? tabManager._getTab(tabManager.activeId)
    : null;
  return !!(tab && isC1sTab(tab));
}

function _clearDisallowedChargeRef() {
  if (_isChargeRefAllowed()) return;
  for (const p of state.peaks) {
    if (p.isChargeReference) p.isChargeReference = false;
  }
}

function renderPeakList() {
  _clearDisallowedChargeRef();
  _updateLocalModelBanner();
  const el = document.getElementById('peak-list');
  const empty = document.getElementById('peak-empty');
  // Preserve which peak cards are expanded before clearing
  const expandedIds = new Set();
  el.querySelectorAll('.peak-body.open').forEach(b => {
    const m = b.id.match(/peak-body-(\d+)/);
    if (m) expandedIds.add(Number(m[1]));
  });
  el.innerHTML = '';
  empty.style.display = state.peaks.length ? 'none' : 'block';
  const clearWrap = document.getElementById('peak-clear-wrap');
  if (clearWrap) clearWrap.style.display = state.peaks.length ? 'block' : 'none';
  document.getElementById('sb-peaks').textContent = state.peaks.length;
  _updateLockAllBtn();

  // Compute total area for percentage (using ROI data if available)
  const { be: _roiBE } = (typeof getROIData === 'function' && state.rawBE.length) ? getROIData() : { be: [] };
  const _peakAreas = {};
  let totalArea = 0;
  if (_roiBE.length) {
    for (const p of state.peaks) { const a = _peakArea(p, _roiBE); _peakAreas[p.id] = a; if (!_isUnsupported(p)) totalArea += a; }
  }

  for (const p of state.peaks) {
    const item = document.createElement('div');
    item.className = 'peak-item';
    item.id = 'peak-item-' + p.id;
    item.style.borderLeftColor = p.color;
    const isLinked = !!p.linked;
    const pArea = _peakAreas[p.id] || 0;
    const unsupported = _isUnsupported(p);
    const areaPct = unsupported ? '\u2014' : (totalArea > 0 && pArea > 0 ? ((pArea / totalArea) * 100).toFixed(1) : '\u2014');
    const dash = '\u2014';

    item.innerHTML = `
      <div class="peak-header" onclick="togglePeakBody(${p.id})">
        <div class="peak-color" style="background:${p.color}"></div>
        <span class="peak-name">${_escHtml(p.name)}${isLinked ? ' <span class="linked-badge">linked</span>' : ''}${p.isChargeReference ? ' <span class="chargeref-badge" title="Charge-correction reference (C 1s graphite 284.5 eV)">C-ref</span>' : ''}${unsupported ? ' ' + _unsupportedBadge(p.id) : ''}</span>
        <span class="peak-info">${unsupported ? dash : p.center.toFixed(2) + ' eV'}</span>
        <button class="btn btn-icon btn-sm" style="margin-left:4px;color:var(--red)" onclick="event.stopPropagation();removePeak(${p.id})">&times;</button>
      </div>
      <div class="peak-summary" onclick="togglePeakBody(${p.id})">
        <span class="peak-summary-label">Center</span>
        <span class="peak-summary-label">FWHM</span>
        <span class="peak-summary-label">Area</span>
        <span class="peak-summary-val">${unsupported ? dash : p.center.toFixed(2)}</span>
        <span class="peak-summary-val">${unsupported ? dash : p.fwhm.toFixed(2)}</span>
        <span class="peak-summary-val">${areaPct === '\u2014' ? areaPct : areaPct + '%'}</span>
      </div>
      <div class="peak-body" id="peak-body-${p.id}">
        ${renderPeakForm(p)}
      </div>
    `;
    el.appendChild(item);
    if (expandedIds.has(p.id)) document.getElementById('peak-body-' + p.id).classList.add('open');
    item.addEventListener('mouseenter', () => _highlightChartPeak(p.id, true));
    item.addEventListener('mouseleave', () => _highlightChartPeak(p.id, false));
  }
  if (state.rawBE && state.rawBE.length) _patchPeakCardsForCentre(_roiWindowStatus());
}

function renderPeakForm(p) {
  const isLinked = !!p.linked;
  const showChargeRef = _isChargeRefAllowed();

exec
/bin/zsh -lc "sed -n '7160,7255p' templates/index.html; sed -n '9395,9445p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
  for (const k in ((ip && ip.params) || {})) { const q = ip.params[k]; if (q && q.vary === true && (q.expr == null || q.expr === '')) p++; }
  const nFree = (json.statistics && Number.isFinite(json.statistics.n_free_params)) ? json.statistics.n_free_params : 0;
  return _componentSupportCore(counts, fit, comp, counts.map(c => 1 / Math.sqrt(Math.max(c, 1))), p, nFree);
}
// Resolve links by ANCESTRY (a grandchild follows the root), independent of order.
function _supportRootOf(peaks, p, seen = new Set()) {
  if (!p.linked || seen.has(p.id)) return p;
  seen.add(p.id);
  const par = peaks.find(q => String(q.id) === String(p.linked));
  return par ? _supportRootOf(peaks, par, seen) : p;
}
// Write p.support for every peak from per-peak verdicts {id -> verdict|null}, stamped with the fit key.
function _applySupportVerdicts(peaks, verdictOf, fitKey) {
  for (const p of peaks) {
    const root = _supportRootOf(peaks, p);
    const v = verdictOf(root.id);
    p.support = v ? { f: v.f ?? null, delta_chi2: v.delta_chi2 ?? null, supported: !!v.supported, fitKey,
                      ...(root !== p ? { follows: root.id } : {}) } : null;
  }
}
function _applySupport(peaks, json, fitKey) {
  _applySupportVerdicts(peaks, id => _componentSupportFromResponse(json, id), fitKey);
}
// TRUE only for a verdict that describes the CURRENT model and fit context.
function _isUnsupported(p, key) {
  if (!(p && p.support && p.support.supported === false)) return false;
  if (!p.support.fitKey) return false;                              // a verdict from before keys existed: not applied
  if (key === undefined) key = typeof _startsLiveKey === 'function' ? _startsLiveKey() : null;
  return p.support.fitKey === key;
}
// A CURRENT verdict, either way (for exports: a stale or keyless verdict is "not established", never "supported").
function _currentSupport(p) {
  if (!(p && p.support && p.support.fitKey)) return null;
  return p.support.fitKey === _startsLiveKey() ? p.support : null;
}
// Re-stamp every verdict with the live key: for a caller that changes the
// model or context AS PART OF producing the result (Auto-Fit locks every
// centre and refines the charge correction after the fit is applied).
function _restampSupport() {
  const key = _startsLiveKey();
  for (const p of state.peaks) if (p.support) p.support.fitKey = key;
}
// Patch the sidebar cards in place for the current verdicts (a re-render would
// replace an input the student is typing in): header centre, the three summary
// values, the area % column (over the components the current verdicts
// support) and the badge.
function _patchPeakCardsForSupport() {
  const key = _startsLiveKey();
  // area % over the components the CURRENT verdicts support (as renderPeakList computes it)
  const { be: roiBE } = (typeof getROIData === 'function' && state.rawBE && state.rawBE.length) ? getROIData() : { be: [] };
  const areas = {};
  let total = 0;
  if (roiBE.length) for (const p of state.peaks) { areas[p.id] = _peakArea(p, roiBE); if (!_isUnsupported(p, key)) total += areas[p.id]; }
  for (const p of state.peaks) {
    const item = document.getElementById('peak-item-' + p.id);
    if (!item) continue;
    const un = _isUnsupported(p, key), dash = '\u2014';
    const info = item.querySelector('.peak-info');
    if (info) info.textContent = un ? dash : p.center.toFixed(2) + ' eV';
    const vals = item.querySelectorAll('.peak-summary-val');
    if (vals[0]) vals[0].textContent = un ? dash : p.center.toFixed(2);
    if (vals[1]) vals[1].textContent = un ? dash : p.fwhm.toFixed(2);
    if (vals[2]) vals[2].textContent = (un || !(total > 0 && areas[p.id] > 0)) ? dash : ((areas[p.id] / total) * 100).toFixed(1) + '%';
    const name = item.querySelector('.peak-name'), badge = name && name.querySelector('.unsupported-badge');
    if (un && name && !badge) name.insertAdjacentHTML('beforeend', ' ' + _unsupportedBadge(p.id));
    if (!un && badge) { badge.previousSibling && badge.previousSibling.nodeType === 3 && badge.previousSibling.textContent === ' ' ? badge.previousSibling.remove() : null; badge.remove(); }
  }
}
function _unsupportedBadge(id) { return `<span class="unsupported-badge" data-peak-id="${id}" title="${_escAttr(_UNSUPPORTED_TIP)}">${_UNSUPPORTED_LABEL}</span>`; }

const _AUTOFIT_ANCHOR_MIN_F = 10;
function _autoFitGraphiteIsSupported(gPeak, json) {
  const amp = gPeak && gPeak.amplitude;
  if (!Number.isFinite(amp) || amp <= 0) return false;
  const counts = (json && json.counts) || [], fit = (json && json.fitted_y) || [];
  const ip = ((json && json.individual_peaks) || []).find(q => String(q.id) === String(gPeak.id));
  const comp = (ip && ip.y) || [];
  const n = counts.length;
  if (!n || fit.length !== n || comp.length !== n) return false;          // nothing to judge against
  let withC = 0, withoutC = 0;
  for (let i = 0; i < n; i++) {
    if (!Number.isFinite(counts[i]) || !Number.isFinite(fit[i]) || !Number.isFinite(comp[i])) continue;
    const w = 1 / Math.max(counts[i], 1), r = counts[i] - fit[i];
    withC += w * r * r;
    withoutC += w * (r + comp[i]) * (r + comp[i]);
  }
  const delta = withoutC - withC;
  if (!(delta > 0)) return false;
  let p = 0;
  for (const k in (ip.params || {})) { const q = ip.params[k]; if (q && q.vary === true && (q.expr == null || q.expr === '')) p++; }
  p = Math.max(1, p);
  const nFree = (json.statistics && Number.isFinite(json.statistics.n_free_params)) ? json.statistics.n_free_params : 0;
  const dof = Math.max(1, n - nFree);
  if (withC === 0) return true;                                           // exact fit that the component is needed for
  return (delta / p) / (withC / dof) >= _AUTOFIT_ANCHOR_MIN_F;
}
    }
    if (sc.y) {
      if (sc.y.ticks) sc.y.ticks.display = !offsetActive;
      if (sc.y.title) {
        sc.y.title.display = true;
        sc.y.title.text = offsetActive ? 'Intensity (offset stacked)' : 'Intensity (counts/s)';
      }
    }
  }
  state.chart.update('none');
}

function updatePlot() {
  // Stack-tab early branch: render multi-spectrum overlay, no peaks/fits.
  // Route through _updateStackChart so toolbar-pill toggles (Envelope,
  // Individual Peaks, Fill, Bkgrd Sub) and other state changes preserve
  // zoom by in-place updating. _updateStackChart delegates to
  // _renderStackChart automatically when no chart exists.
  {
    const _activeTab = (typeof tabManager !== 'undefined') ? tabManager._getTab(tabManager.activeId) : null;
    const _emptyEl = document.getElementById('stack-empty-state');
    const _canvas = document.getElementById('mainChart');
    if (isStackTab(_activeTab)) {
      _refreshRoiHint(null);   // a stack tab has no ROI of its own
      _updateStackChart(_activeTab);
      return;
    } else {
      if (_canvas) _canvas.style.display = '';
      if (_emptyEl) _emptyEl.style.display = 'none';
    }
  }

  // Full corrected spectrum (for raw data display and axis range)
  const corrBE = getCorrectedBE();
  const fullInten = state.rawIntensity;

  // ROI-filtered data (for fitting, background, peaks)
  const { be, inten } = getROIData();
  const invert = document.getElementById('invert-be').checked;
  const showIndividual = document.getElementById('show-individual').checked;
  const showResiduals = document.getElementById('show-residuals').checked;

  const _ob = document.getElementById('main-chart-wrap').querySelector('.onboard-wrap');
  if (_ob) _ob.remove();

  if (!corrBE.length) {
    renderEmptyChart();
    return;
  }

  // After a fit, freeze all curve data to the stored fit state so that

exec
/bin/zsh -lc "sed -n '15450,15535p' templates/index.html; sed -n '15690,15730p' templates/index.html; sed -n '220,290p' app.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
  const coverage = (_fpMeta && _fpMeta.coverage) || [];
  const entry = coverage.find(e => e.region === region);
  if (entry) _fpExpandedElement = entry.symbol;
  _fpToggleRegion(region, additive);
  const box = document.getElementById('fp-search-dropdown');
  if (box) box.innerHTML = '';
}

function _fpFilterRegions(query) {
  _fpRenderPtGrid(query);
  _fpRenderSearchDropdown(query);
}

// Pure selection-set logic (DOM-free, unit-testable): a plain click
// REPLACES the selection with just that region (matches how a single
// click reads); ctrl/cmd-click toggles membership without disturbing the
// rest (goal: "preserve the existing multi-region selection (ctrl-click
// to fit two together)"). Returns a NEW Set — never mutates `current`.
function _fpNextSelection(current, region, additive) {
  if (additive) {
    const next = new Set(current);
    if (next.has(region)) next.delete(region);
    else next.add(region);
    return next;
  }
  if (current.size === 1 && current.has(region)) return current;
  return new Set([region]);
}

function _fpToggleRegion(region, additive) {
  _fpRegionsSelected = _fpNextSelection(_fpRegionsSelected, region, additive);
  _fpSyncSelectionUI();
}

function _fpSyncSelectionUI() {
  const values = Array.from(_fpRegionsSelected);
  const coverage = (_fpMeta && _fpMeta.coverage) || [];
  const entries = values.map(v => coverage.find(e => e.region === v))
    .filter(Boolean);
  document.getElementById('fp-regions-tier-note').textContent =
    _fpTierNoteFor(entries);
  // ROI auto-fill: only for an UNAMBIGUOUS single-region pick with a real
  // hint — a co-fit selection (2 regions) has no single "right" window,
  // and a structure_only region honestly has no hint to offer (goal:
  // never invent a window; the note above says so, ROI is left alone).
  if (entries.length === 1 && entries[0].roi) {
    document.getElementById('roi-min').value = entries[0].roi.be_min;
    document.getElementById('roi-max').value = entries[0].roi.be_max;
  }
  _fpRenderPtGrid(document.getElementById('fp-regions-filter').value);
  _fpRenderExpandedPanel();
}

function _fpMaterialChanged() {
  const v = document.getElementById('fp-material').value;
  const s = FP_STRINGS.materials[v] || {};
  document.getElementById('fp-material-hint').textContent = s.hint || '';
}

const FP_EXPERIMENTAL_NOTICE_LS_KEY = 'xps-fp-experimental-notice-dismissed';

function _fpMaybeShowExperimentalNotice() {
  const el = document.getElementById('fp-experimental-notice');
  if (localStorage.getItem(FP_EXPERIMENTAL_NOTICE_LS_KEY)) {
    el.style.display = 'none';
    return;
  }
  document.getElementById('fp-experimental-notice-text').textContent =
    FP_STRINGS.experimentalNotice;
  el.style.display = 'block';
}

function _fpDismissExperimentalNotice() {
  localStorage.setItem(FP_EXPERIMENTAL_NOTICE_LS_KEY, '1');
  document.getElementById('fp-experimental-notice').style.display = 'none';
}

function _fpMethodChanged() {
  const id = document.getElementById('fp-method').value;
  const m = (_fpMeta.methods || []).find(x => x.id === id);
  const strs = FP_STRINGS.methods[id] || {};
  document.getElementById('fp-method-hint').textContent = strs.hint || '';
  // the Advanced JSON stays the single source of truth for the request —
  // the friendly controls below are a labeled VIEW that writes into it.
  // endpoint_avg is the exception: its source is the Background panel
  // (runFindPeaks injects the panel value unless the JSON names one), so
  // so what the record holds is always exactly what the engine used.
  if (methodTakesEp && !(typeof options.endpoint_avg === 'number'
                         && Number.isInteger(options.endpoint_avg)
                         && options.endpoint_avg >= 1 && options.endpoint_avg <= ENDPOINT_AVG_MAX)) {
    status.textContent = 'Advanced options: endpoint_avg must be a whole number between 1 and ' +
                         ENDPOINT_AVG_MAX + ' (got ' + JSON.stringify(options.endpoint_avg) + ').';
    return;
  }
  const engineEndpointAvg = methodTakesEp ? String(options.endpoint_avg) : LEGACY_ENDPOINT_AVG;

  btn.disabled = true;
  spinner.style.display = 'inline-block';
  status.textContent = 'Analyzing… starting…';
  try {
    // OWNER + INPUTS FIRST: everything this analysis needs is read from the
    // tab that is active NOW, before the first await; the result goes back
    // to this same record object whatever tab is active at completion.
    const owner = _opOwner();
    if (!owner) { status.textContent = 'Open a spectrum tab first.'; return; }
    // corrected-frame data, same convention as the manual fit path
    const be = getCorrectedBE();
    const inten = state.rawIntensity;
    const payload = {
      session_id: null, cc_shift: 0,
      roi: { be_min: parseFloat(document.getElementById('roi-min').value),
             be_max: parseFloat(document.getElementById('roi-max').value) },
      material_class: document.getElementById('fp-material').value,
      regions, method, options,
    };
    if (method === 'least_squares') {
      payload.peak_specs = state.peaks.map(peakToBackendSpec);
      if (!payload.peak_specs.length) {
        status.textContent = '“Refit my current peaks” needs peaks on ' +
          'this tab first — add some, or pick “Compare peak models”.';
        return;
      }
    }
    payload.session_id = await uploadToBackend(be, inten);
    const resp = await fetch('/api/analyze/start', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
def _validate_analyze_request(body: dict, upload_folder: str) -> _AnalyzeContext:
    """ALL the synchronous, cheap validation /api/analyze has always done
    (session lookup through grammar resolution) — pure extract-method
    refactor, byte-identical checks/messages/order, raising
    ``_AnalyzeError`` in place of the old inline ``return _err(...)``."""
    from autofit.grammar import (MaterialClass, Phase,
                                 PhaseAmbiguityError, UnknownRegionError,
                                 resolve)

    session_id = body.get("session_id", "")
    _validate_session_id(session_id)
    try:
        energy, counts = _load_session(session_id, upload_folder)
    except KeyError:
        raise _AnalyzeError(f"Session '{session_id}' not found", 404)

    method_id = body.get("method", "ic_model_comparison")
    if method_id not in _ANALYZE_METHODS:
        raise _AnalyzeError(f"Unknown analyze method '{method_id}' "
                            f"(available: {sorted(_ANALYZE_METHODS)})")

    regions = body.get("regions") or []
    if (not isinstance(regions, list) or not regions
            or not all(isinstance(r, str) for r in regions)):
        raise _AnalyzeError("'regions' must be a non-empty list of region names")

    mc_raw = body.get("material_class", "")
    try:
        mclass = MaterialClass(mc_raw)
    except ValueError:
        raise _AnalyzeError(f"Unknown material_class '{mc_raw}'")

    try:
        cc_shift = float(body.get("cc_shift", 0.0))
    except (TypeError, ValueError):
        raise _AnalyzeError("cc_shift must be a number")
    corrected = energy - cc_shift   # frontend getCorrectedBE convention

    # present-but-falsy non-objects ([], "", false) must be clean 400s,
    # not silently treated as omitted (Codex re-check)
    roi = body.get("roi")
    roi = {} if roi is None else roi
    if not isinstance(roi, dict):
        raise _AnalyzeError("'roi' must be an object")
    try:
        be_min = float(roi.get("be_min", float(corrected.min())))
        be_max = float(roi.get("be_max", float(corrected.max())))
    except (TypeError, ValueError):
        raise _AnalyzeError("roi.be_min/be_max must be numbers")
    mask = (corrected >= be_min) & (corrected <= be_max)
    if int(mask.sum()) < 20:
        raise _AnalyzeError("ROI selects fewer than 20 points")
    x, y = corrected[mask], counts[mask]

    options = body.get("options")
    options = {} if options is None else options
    if not isinstance(options, dict):
        raise _AnalyzeError("'options' must be an object")
    opts = {**_ANALYZE_METHODS[method_id], **options}

    peak_specs = body.get("peak_specs") or None
    if method_id == "least_squares" and not peak_specs:
        raise _AnalyzeError("least_squares is the manual-model baseline — "
                            "provide 'peak_specs'")

    phase_kwargs = body.get("phase")
    phase_kwargs = {} if phase_kwargs is None else phase_kwargs
    if not isinstance(phase_kwargs, dict):
        raise _AnalyzeError("'phase' must be an object")
    grammar = None
    if method_id != "least_squares":

exec
/bin/zsh -lc "sed -n '1,110p' CLAUDE.md" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
# XPS Fitting Studio

Web application for XPS (X-ray Photoelectron Spectroscopy) peak fitting,
multi-spectrum visualization, and project management. Python/Flask backend
with an lmfit-driven peak-fitting pipeline; single-page frontend in
`templates/index.html`. Deployed at xps.fortierlab.org via a gunicorn
LaunchAgent + Cloudflare Tunnel.

## Stack

- **Backend:** Python/Flask, served by gunicorn. App factory in [app.py](app.py).
- **Fitting engine:** lmfit ≥ 1.3 (5 methods: leastsq, least_squares, nelder, differential_evolution, basinhopping).
- **Numerics:** numpy, scipy.
- **File parsing:** pandas, openpyxl (xlsx), olefile (vgd).
- **Frontend:** Single-page HTML/JS in `templates/index.html` (~8500 LOC). Vanilla JS, no build step.
- **Charting:** Chart.js 4.4 (CDN).
- **Deployment:** macOS LaunchAgent runs gunicorn on **127.0.0.1:5050** (NOT :5000 — macOS AirTunes intercepts :5000 and returns 403, so health-check :5050); Cloudflare Tunnel publishes to xps.fortierlab.org. Dev gunicorn typically runs on :5151 with `--reload` for pre-merge verification. See [DEPLOY.md](DEPLOY.md) for the full deploy sequence.

## Project Layout

```
app.py                    # Flask app factory + REST routes
fitting.py                # lmfit pipeline, lineshape impls, background algorithms
parser.py                 # File parsers (csv / tsv / txt / xy / xlsx / xls / vgd)
vgd_parser.py             # Thermo Avantage VGD binary parser (uses olefile)
templates/index.html      # Frontend — CSS + HTML + JS in one file
tests/                    # pytest suite (focused on LA + DS+G correctness)
docs/superpowers/plans/   # Agent-authored design memos and implementation plans
uploads/                  # Per-session .npz storage (gitignored)
requirements.txt
venv/                     # virtualenv (do not commit)
```

The Flask backend serves the frontend via `render_template('index.html')`
and exposes a REST API consumed by the page through fetch.

## Backend API

Per-upload sessions store parsed `(energy, counts)` arrays as compressed
`.npz` in `uploads/<session_id>.npz`. No server-side memory state —
compatible with multi-worker gunicorn.

| Method | Path | Purpose |
|---|---|---|
| `GET`    | `/`                       | Serve the frontend (`templates/index.html`). |
| `GET`    | `/api/health`             | Liveness probe. Returns `{status: "ok"}`. |
| `GET`    | `/api/peak-shapes`        | List backend-registered lineshapes (gaussian / lorentzian / pseudo_voigt_gl / asymmetric_gl / doniach_sunjic / ds_g / la_casaxps). |
| `GET`    | `/api/elements`           | Spin-orbit element presets (splitting + area ratio). |
| `POST`   | `/api/upload`             | Upload a spectrum file; returns `session_id` + downsampled preview. |
| `POST`   | `/api/parse-vgd`          | Parse Thermo Avantage VGD binary directly (no session storage). |
| `GET`    | `/api/session/<id>`       | Retrieve a stored session's preview data. |
| `DELETE` | `/api/session/<id>`       | Delete session files. |
| `POST`   | `/api/background`         | Compute background curve for a session. |
| `POST`   | `/api/fit`                | Run lmfit on a session with peak specs; returns chi², bgIntensity, bgSubtracted, fittedY, per-peak refined params + σ. |

## Frontend Architecture

### State

Module-global `state` holds the currently-active tab's working values
(swapped on tab switch by `TabManager.activateTab`):

```js
state = {
  rawBE, rawIntensity,   // full spectrum as loaded
  ccShift,               // charge-correction rigid shift (eV)
  peaks[],               // array of peak objects
  nextId,                // auto-increment peak ID
  chart,                 // Chart.js instance
  residChart,            // Residuals sub-chart instance
  fitResult,             // last fit diagnostics (be, bgIntensity, bgSubtracted, fittedY, chi, etc.)
  lineWidth,             // per-tab line width (sync of tab.lineWidth)
}
```

### Tab model

`TabManager` (a class in `templates/index.html`) holds `tabs[]` and an
`activeId`. Two tab types share the array:

- **Spectrum tab:** has `rawBE`, `rawIntensity`, `peaks`, `fitResult`, `ccShift`, `manualAnchors`, `lineWidth`, `ui` (form field snapshot incl. bg settings, ROI, charge correction method).
- **Stack tab** (`isStack: true`): viewer-only container for references to other spectrum tabs. Has `entries[{id, sourceTabId, color, visible, showFit}]`, `lineWidth`, `verticalOffset`, `_nextColorIdx`. No raw data of its own — entries resolve their source tab at render time.

Lifecycle: `createTab`, `createStackTab`, `activateTab`, `closeTab`,
`_syncActiveToRecord` (writes state-back-to-tab on switch-away). Drag-and-drop
tab reordering exists.

### Peak Object Schema — core fields

(Non-exhaustive. Additional optional fields appear for multiplet linkage, fix-flags per parameter, auto-fit asymmetry bounds, etc. Search the source for `defaultPeak` to see the full shape.)

```js
{
  id, name, color, visible,
  center, fwhm, amplitude,
  shape,       // 'Gaussian'|'Lorentzian'|'Voigt'|'GL'|'asym-GL'|'DS'|'DSG_LA'|'LACX'
  glMix,       // 0–100 (Gauss → Lorentz)
  asymmetry,   // asym-GL asymmetry index
  dsAlpha, dsGamma,                       // DS params
  laAlpha, laBeta, laM,                   // DS+G params (laAlpha=α, laBeta=Lorentzian half-width, laM=Gauss FWHM)
  caAlpha, caBeta, caM,                   // CasaXPS LA params (caM is in DATA POINTS, not eV)
  linked, linkOffset, linkRatio,          // multiplet linkage to parent peak
  isChargeReference,                      // marks this peak as the cc anchor
}
```

### Lineshapes

| ID | Description |
|----|-------------|

exec
/bin/zsh -lc 'git diff main..HEAD -- tests/test_component_required.py; cat tests/test_component_required.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-RAFpCtwS' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-FxNR9hUy' (errno=Operation not permitted)
diff --git a/tests/test_component_required.py b/tests/test_component_required.py
index 78b4ef7..e48cac4 100644
--- a/tests/test_component_required.py
+++ b/tests/test_component_required.py
@@ -49,21 +49,36 @@ KW = dict(background_method="manual", manual_bg=[[280.0, 1000.0], [295.0, 1000.0
           fit_kws={"method": "least_squares"})
 
 
-def test_a_redundant_anchor_is_supported_but_not_required():
+@pytest.mark.parametrize("method", ["least_squares", "leastsq"])
+def test_a_redundant_anchor_is_supported_but_not_required(method):
     # Codex, Auto-Fit anchor unit round 6 (run B): two symmetric GL lines at
-    # 284.8/1.4 eV and 283.3/1.8 eV, no graphite. Auto-Fit's model puts an
-    # asymmetric-GL Graphite at 284.5 with the ±0.3 eV window; the fit gives it
-    # a large amplitude (F ~ 1e6 with the others HELD) — yet the other two
-    # components fit the data to rounding precision without it.
+    # 284.8/1.4 eV and 283.3/1.8 eV, no graphite. In that reproduction the
+    # full fit kept a LARGE Graphite (amplitude 1,081-1,894, held-others F ~
+    # 1e6) because it stopped in a minimum where the anchor carries weight;
+    # yet the other two components fit the data to rounding precision
+    # without it.
+    #
+    # The premise is posed deterministically by HOLDING the anchor at 1,500
+    # (inside that observed range). Until 2026-09-25 this test instead
+    # started the other components at the exact truth, which lets the fit
+    # drive the anchor to residue (~0.01) - the premise never formed, the
+    # held-others F landed at 11-24 against the threshold of 10, and
+    # Trust-Region's documented last-digit jitter (identical seed in every
+    # process) moved it across: the test passed 2 of 3 runs on main. Now
+    # F ~ 4e7 and the refit without the anchor is ~1e4 x better, under both
+    # methods, in every process.
     y = np.round(1000 + _gl(X, 10000, 284.8, 1.4) + _gl(X, 15000, 283.3, 1.8), 2)
-    specs = _autofit_model(1000, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
-    res = fitting.run_fit(X, y, specs, require_component="1", **KW)
+    specs = _autofit_model(1500, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
+    specs[0]["fix_amplitude"] = True
+    kw = dict(KW, fit_kws={"method": method})
+    res = fitting.run_fit(X, y, specs, require_component="1", **kw)
     assert res["success"] is True
     g = next(ip for ip in res["individual_peaks"] if ip["id"] == "1")
     assert g["support"]["supported"] is True, "held-others statistic passes: that is the gap"
+    assert g["support"]["f"] > 1e6, g["support"]["f"]           # far from the threshold, not on it
     req = res["required"]
     assert req["ran"] is True and req["refit_converged"] is True
-    assert req["chi2_without_refit"] <= req["chi2_with"] * 1.001
+    assert req["chi2_without_refit"] < 1e-2 * req["chi2_with"]
     assert req["required"] is False
 
 
"""'Is this component REQUIRED?' — the refit test (unit step (c), 2026-09-22).

`support` holds the other components at their fitted values, so redundancy
under overlap escapes it (Auto-Fit anchor unit, Codex round 6: a large
Graphite component the other components could absorb if refitted). The refit
without the component is the test for that. It costs one fit, so it runs
only when asked (`require_component`); Auto-Fit asks for its anchor.
"""

import io

import numpy as np
import pytest

import fitting
from app import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app(upload_folder=str(tmp_path))
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _gl(x, a, c, w, mix=0.3):
    return fitting._SHAPE_FUNCS["pseudo_voigt_gl"](x, amplitude=a, center=c, fwhm=w, gl_ratio=mix)


def _agl(x, a, c, w):
    return fitting._SHAPE_FUNCS["asymmetric_gl"](x, amplitude=a, center=c, fwhm=w, gl_ratio=0.3, asymmetry=0.25)


X = np.round(np.arange(280.0, 295.0001, 0.02), 4)


def _autofit_model(graphite_amp, others):
    specs = [{"id": "1", "name": "Graphite", "shape": "asymmetric_gl", "center": 284.5, "center_min": 284.2, "center_max": 284.8,
              "amplitude": graphite_amp, "fwhm": 0.7, "gl_ratio": 0.3, "asymmetry": 0.25, "asymmetry_min": 0.1, "asymmetry_max": 0.5,
              "amplitude_min": 0, "fwhm_min": 0.4, "fwhm_max": 3.0}]
    for k, (a, c, w) in enumerate(others, start=2):
        specs.append({"id": str(k), "shape": "pseudo_voigt_gl", "center": c, "amplitude": a, "fwhm": w, "gl_ratio": 0.3,
                      "amplitude_min": 0, "fwhm_min": 0.4, "fwhm_max": 3.0})
    return specs


KW = dict(background_method="manual", manual_bg=[[280.0, 1000.0], [295.0, 1000.0]], n_perturb=3,
          fit_kws={"method": "least_squares"})


@pytest.mark.parametrize("method", ["least_squares", "leastsq"])
def test_a_redundant_anchor_is_supported_but_not_required(method):
    # Codex, Auto-Fit anchor unit round 6 (run B): two symmetric GL lines at
    # 284.8/1.4 eV and 283.3/1.8 eV, no graphite. In that reproduction the
    # full fit kept a LARGE Graphite (amplitude 1,081-1,894, held-others F ~
    # 1e6) because it stopped in a minimum where the anchor carries weight;
    # yet the other two components fit the data to rounding precision
    # without it.
    #
    # The premise is posed deterministically by HOLDING the anchor at 1,500
    # (inside that observed range). Until 2026-09-25 this test instead
    # started the other components at the exact truth, which lets the fit
    # drive the anchor to residue (~0.01) - the premise never formed, the
    # held-others F landed at 11-24 against the threshold of 10, and
    # Trust-Region's documented last-digit jitter (identical seed in every
    # process) moved it across: the test passed 2 of 3 runs on main. Now
    # F ~ 4e7 and the refit without the anchor is ~1e4 x better, under both
    # methods, in every process.
    y = np.round(1000 + _gl(X, 10000, 284.8, 1.4) + _gl(X, 15000, 283.3, 1.8), 2)
    specs = _autofit_model(1500, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
    specs[0]["fix_amplitude"] = True
    kw = dict(KW, fit_kws={"method": method})
    res = fitting.run_fit(X, y, specs, require_component="1", **kw)
    assert res["success"] is True
    g = next(ip for ip in res["individual_peaks"] if ip["id"] == "1")
    assert g["support"]["supported"] is True, "held-others statistic passes: that is the gap"
    assert g["support"]["f"] > 1e6, g["support"]["f"]           # far from the threshold, not on it
    req = res["required"]
    assert req["ran"] is True and req["refit_converged"] is True
    assert req["chi2_without_refit"] < 1e-2 * req["chi2_with"]
    assert req["required"] is False


def test_a_real_graphite_anchor_is_required():
    rng = np.random.default_rng(0)
    y = rng.poisson(1000 + _agl(X, 86000, 284.5, 0.7) + _gl(X, 14000, 285.1, 1.9) + _gl(X, 2300, 286.4, 1.4)).astype(float)
    specs = _autofit_model(80000, [(14000, 285.1, 1.9), (2300, 286.4, 1.4)])
    res = fitting.run_fit(X, y, specs, require_component="1", **KW)
    req = res["required"]
    assert req["ran"] and req["required"] is True and req["f"] > 1000
    assert req["chi2_without_refit"] > req["chi2_with"]


def test_the_fit_itself_is_unchanged_by_the_check():
    import json
    y = np.round(1000 + _gl(X, 10000, 284.8, 1.4) + _gl(X, 15000, 283.3, 1.8), 2)
    specs = _autofit_model(1000, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
    kw = {**KW, "fit_kws": {"method": "leastsq"}}
    a = fitting.run_fit(X, y, specs, **kw)
    b = fitting.run_fit(X, y, specs, require_component="1", **kw)
    strip = lambda r: json.dumps({k: v for k, v in r.items() if k != "required"}, sort_keys=True)  # noqa: E731
    assert strip(a) == strip(b) and a["required"] is None and b["required"]["ran"] is True


def _linked(pid, master, offset):
    return {"id": pid, "shape": "pseudo_voigt_gl", "center": 284.5 + offset, "amplitude": 100.0, "fwhm": 0.7, "gl_ratio": 0.3,
            "amplitude_min": 0, "constrain_to": master, "splitting": offset, "area_ratio": 0.01}


def test_everything_linked_to_the_removed_component_goes_with_it_transitively():
    # Codex round 1: 1 -> 9 -> 10 raised NameError in the reduced model; and a
    # child ordered BEFORE its parent broke expression construction.
    y = np.round(1000 + _gl(X, 10000, 284.8, 1.4) + _gl(X, 15000, 283.3, 1.8), 2)
    specs = _autofit_model(1000, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
    specs += [_linked("9", "1", 1.0), _linked("10", "9", 1.0)]
    res = fitting.run_fit(X, y, specs, require_component="1", **KW)
    assert res["required"]["ran"] is True, res["required"]
    assert res["required"]["required"] is False
    # remove an UNRELATED component while a kept child precedes its kept parent in the request
    specs2 = _autofit_model(1000, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
    specs2 = [specs2[0], _linked("4", "3", 0.8), specs2[1], specs2[2]]           # 4 -> 3, listed before 3
    res2 = fitting.run_fit(X, y, specs2, require_component="2", **KW)
    assert res2["required"]["ran"] is True, res2["required"]
    # Codex round 2: a retained CHAIN in reverse order (10 -> 9 -> 3, listed 10 before 9), removing 1
    specs3 = _autofit_model(1000, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)]) + [_linked("10", "9", 0.8), _linked("9", "3", 0.8)]
    res3 = fitting.run_fit(X, y, specs3, require_component="1", **KW)
    assert res3["required"]["ran"] is True, res3["required"]
    specs4 = _autofit_model(1000, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
    specs4 = [specs4[0], specs4[1], _linked("4", "3", 0.8), specs4[2]]
    specs4[2]["constrain_to"] = "3"; specs4.append(_linked("5", "4", 0.8)); specs4 = [specs4[0], specs4[1], specs4[4], specs4[2], specs4[3]]
    res4 = fitting.run_fit(X, y, specs4, require_component="1", **KW)
    assert res4["required"]["ran"] is True, res4["required"]


def test_differential_evolution_goes_through_its_own_candidate_machinery():
    # Codex round 1: a direct model.fit under DE failed on the open amplitude bound -> ran:false
    y = np.round(1000 + _gl(X, 10000, 284.8, 1.4) + _gl(X, 15000, 283.3, 1.8), 2)
    specs = _autofit_model(1000, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
    res = fitting.run_fit(X, y, specs, require_component="1", **{**KW, "n_perturb": 0, "fit_kws": {"method": "differential_evolution"}})
    assert res["success"] is True and res["required"]["ran"] is True, res["required"]
    assert res["required"]["required"] is False


def test_the_refit_of_a_stochastic_method_is_seeded(monkeypatch):
    seeds = []
    real_fit = fitting.Model.fit

    def spy(self, data, params, **kw):
        seeds.append((kw.get("method"), (kw.get("fit_kws") or {}).get("seed")))
        return real_fit(self, data, params, **kw)

    monkeypatch.setattr(fitting.Model, "fit", spy)
    y = np.round(1000 + _gl(X, 10000, 284.8, 1.4), 2)
    specs = _autofit_model(1000, [(10000, 284.8, 1.4)])
    fitting.run_fit(X, y, specs, require_component="1", **{**KW, "n_perturb": 0, "fit_kws": {"method": "basinhopping"}})
    bh = [s for m, s in seeds if m == "basinhopping"]
    assert len(bh) == 2 and all(isinstance(s, int) for s in bh) and bh[0] != bh[1]


def test_known_limit_noise_free_exact_fit_reports_a_redundant_component_as_required():
    # Two identical half-amplitude components on noise-free data: removing one
    # is lossless, but the full fit is exact to machine precision (chi2 ~1e-28)
    # so F is meaningless and reads as huge. Every tolerance tried to handle
    # this masked a real anchor at high dynamic range (Codex rounds 2-3), so
    # none is applied: this is a documented limit, not a rule. Real data never
    # fit to machine precision.
    y = 1000 + _gl(X, 10000, 284.8, 1.4)                                     # unrounded: numerically exact
    specs = [{"id": "1", "name": "Graphite", "shape": "pseudo_voigt_gl", "center": 284.8, "amplitude": 5000.0, "fwhm": 1.4, "gl_ratio": 0.3, "amplitude_min": 0},
             {"id": "2", "shape": "pseudo_voigt_gl", "center": 284.8, "amplitude": 5000.0, "fwhm": 1.4, "gl_ratio": 0.3, "amplitude_min": 0}]
    res = fitting.run_fit(X, y, specs, require_component="1", **{**KW, "fit_kws": {"method": "leastsq"}})
    assert res["required"]["ran"] is True
    assert res["required"]["chi2_with"] < 1e-12                                # the premise: an exact fit
    # documented: F is meaningless here and the verdict may read "required"; no rule papers over it
    # with Poisson noise the same construction is judged on its merits: lossless -> not required
    rng = np.random.default_rng(3)
    yn = rng.poisson(1000 + _gl(X, 10000, 284.8, 1.4)).astype(float)
    res_n = fitting.run_fit(X, yn, specs, require_component="1", **{**KW, "fit_kws": {"method": "leastsq"}})
    assert res_n["required"]["required"] is False, res_n["required"]


def test_a_resolved_anchor_at_extreme_dynamic_range_is_required():
    # Codex round 3: amplitude 1 beside 1e10 (F ~ 4e3) and 1 beside 3e9 (F ~ 9e2)
    for big in (1e10, 3e9):
        y = np.round(1000 + _agl(X, 1, 284.5, 0.7) + _gl(X, big, 285.1, 1.9) + _gl(X, 2300, 286.4, 1.4), 2)
        specs = _autofit_model(1, [(big, 285.1, 1.9), (2300, 286.4, 1.4)])
        res = fitting.run_fit(X, y, specs, require_component="1", **KW)
        assert res["required"]["ran"] and res["required"]["required"] is True, (big, res["required"])

codex
The diff preserves the ROI fields and fitting payloads, which supports the plan’s interpretation of “clamp.” I found a likely conflict with unsupported-component handling: the new badge’s tooltip can expose a centre that the card deliberately suppresses. I’m checking that case and the restore paths.

exec
/bin/zsh -lc "sed -n '15490,15515p' templates/index.html; sed -n '15700,15723p' templates/index.html; sed -n '220,290p' app.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
    _fpTierNoteFor(entries);
  // ROI auto-fill: only for an UNAMBIGUOUS single-region pick with a real
  // hint — a co-fit selection (2 regions) has no single "right" window,
  // and a structure_only region honestly has no hint to offer (goal:
  // never invent a window; the note above says so, ROI is left alone).
  if (entries.length === 1 && entries[0].roi) {
    document.getElementById('roi-min').value = entries[0].roi.be_min;
    document.getElementById('roi-max').value = entries[0].roi.be_max;
  }
  _fpRenderPtGrid(document.getElementById('fp-regions-filter').value);
  _fpRenderExpandedPanel();
}

function _fpMaterialChanged() {
  const v = document.getElementById('fp-material').value;
  const s = FP_STRINGS.materials[v] || {};
  document.getElementById('fp-material-hint').textContent = s.hint || '';
}

const FP_EXPERIMENTAL_NOTICE_LS_KEY = 'xps-fp-experimental-notice-dismissed';

function _fpMaybeShowExperimentalNotice() {
  const el = document.getElementById('fp-experimental-notice');
  if (localStorage.getItem(FP_EXPERIMENTAL_NOTICE_LS_KEY)) {
    el.style.display = 'none';
    return;
  btn.disabled = true;
  spinner.style.display = 'inline-block';
  status.textContent = 'Analyzing… starting…';
  try {
    // OWNER + INPUTS FIRST: everything this analysis needs is read from the
    // tab that is active NOW, before the first await; the result goes back
    // to this same record object whatever tab is active at completion.
    const owner = _opOwner();
    if (!owner) { status.textContent = 'Open a spectrum tab first.'; return; }
    // corrected-frame data, same convention as the manual fit path
    const be = getCorrectedBE();
    const inten = state.rawIntensity;
    const payload = {
      session_id: null, cc_shift: 0,
      roi: { be_min: parseFloat(document.getElementById('roi-min').value),
             be_max: parseFloat(document.getElementById('roi-max').value) },
      material_class: document.getElementById('fp-material').value,
      regions, method, options,
    };
    if (method === 'least_squares') {
      payload.peak_specs = state.peaks.map(peakToBackendSpec);
      if (!payload.peak_specs.length) {
        status.textContent = '“Refit my current peaks” needs peaks on ' +
          'this tab first — add some, or pick “Compare peak models”.';
def _validate_analyze_request(body: dict, upload_folder: str) -> _AnalyzeContext:
    """ALL the synchronous, cheap validation /api/analyze has always done
    (session lookup through grammar resolution) — pure extract-method
    refactor, byte-identical checks/messages/order, raising
    ``_AnalyzeError`` in place of the old inline ``return _err(...)``."""
    from autofit.grammar import (MaterialClass, Phase,
                                 PhaseAmbiguityError, UnknownRegionError,
                                 resolve)

    session_id = body.get("session_id", "")
    _validate_session_id(session_id)
    try:
        energy, counts = _load_session(session_id, upload_folder)
    except KeyError:
        raise _AnalyzeError(f"Session '{session_id}' not found", 404)

    method_id = body.get("method", "ic_model_comparison")
    if method_id not in _ANALYZE_METHODS:
        raise _AnalyzeError(f"Unknown analyze method '{method_id}' "
                            f"(available: {sorted(_ANALYZE_METHODS)})")

    regions = body.get("regions") or []
    if (not isinstance(regions, list) or not regions
            or not all(isinstance(r, str) for r in regions)):
        raise _AnalyzeError("'regions' must be a non-empty list of region names")

    mc_raw = body.get("material_class", "")
    try:
        mclass = MaterialClass(mc_raw)
    except ValueError:
        raise _AnalyzeError(f"Unknown material_class '{mc_raw}'")

    try:
        cc_shift = float(body.get("cc_shift", 0.0))
    except (TypeError, ValueError):
        raise _AnalyzeError("cc_shift must be a number")
    corrected = energy - cc_shift   # frontend getCorrectedBE convention

    # present-but-falsy non-objects ([], "", false) must be clean 400s,
    # not silently treated as omitted (Codex re-check)
    roi = body.get("roi")
    roi = {} if roi is None else roi
    if not isinstance(roi, dict):
        raise _AnalyzeError("'roi' must be an object")
    try:
        be_min = float(roi.get("be_min", float(corrected.min())))
        be_max = float(roi.get("be_max", float(corrected.max())))
    except (TypeError, ValueError):
        raise _AnalyzeError("roi.be_min/be_max must be numbers")
    mask = (corrected >= be_min) & (corrected <= be_max)
    if int(mask.sum()) < 20:
        raise _AnalyzeError("ROI selects fewer than 20 points")
    x, y = corrected[mask], counts[mask]

    options = body.get("options")
    options = {} if options is None else options
    if not isinstance(options, dict):
        raise _AnalyzeError("'options' must be an object")
    opts = {**_ANALYZE_METHODS[method_id], **options}

    peak_specs = body.get("peak_specs") or None
    if method_id == "least_squares" and not peak_specs:
        raise _AnalyzeError("least_squares is the manual-model baseline — "
                            "provide 'peak_specs'")

    phase_kwargs = body.get("phase")
    phase_kwargs = {} if phase_kwargs is None else phase_kwargs
    if not isinstance(phase_kwargs, dict):
        raise _AnalyzeError("'phase' must be an object")
    grammar = None
    if method_id != "least_squares":

exec
/bin/zsh -lc "sed -n '3220,3380p' templates/index.html; sed -n '3760,3900p' templates/index.html; sed -n '6965,7045p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
    const tab = this._getTab(id);
    if (!tab) return;
    // Cancel any armed placement mode so a click on the new tab's chart
    // isn't consumed by a placement aimed at the previous spectrum.
    if (placeMode) togglePlaceMode(placeMode);
    // Clear stale history preview from previous tab
    if (typeof _historyPreview !== 'undefined') _historyPreview = null;
    // Save current tab's live state
    this._syncActiveToRecord();
    this.activeId = id;

    // Swap global state fields — peaks uses reference sharing
    state.rawBE = tab.rawBE;
    state.rawIntensity = tab.rawIntensity;
    state.ccShift = tab.ccShift;
    state.peaks = tab.peaks;
    state.nextId = tab.nextId;
    state.fitResult = tab.fitResult;
    state.lineWidth = tab.lineWidth ?? 1.5;

    // Restore DOM form fields
    this._restoreUI(tab.ui);
    _updateUndoButtons();   // history is per tab: buttons reflect the incoming record
    const notesEl = document.getElementById('spectrum-notes');
    if (notesEl) notesEl.value = tab.notes || '';
    this._updateCCVerifiedUI(tab.chargeVerified ?? true);
    this._updateInfoBadge(tab);
    if (typeof _recomputeAutoFitMenuState === 'function') _recomputeAutoFitMenuState();
    // Update chi-squared display for this tab's fit result
    _applyStatDisplay(state.fitResult);
    if (state.fitResult && state.fitResult.rFactor == null) {
      state.fitResult.rFactor = _computeRFactor(state.fitResult);
    }
    _updateRFactorUI(state.fitResult ? state.fitResult.rFactor : null);
    _updateROIDisplay(state.fitResult ? state.fitResult.roiRange : null);
    // Reset Y zoom so chart auto-scales to this tab's data range
    // (prevents survey zoom from squishing narrow-region spectra)
    state._mainYMax = tab.yZoom || null;
    state._mainXMin = tab.xZoomMin ?? null;
    state._mainXMax = tab.xZoomMax ?? null;

    this.renderTabBar();
    renderPeakList();
    renderResults();
    _applyRightPanelMode(tab);
    if (typeof _refOnTabChange === 'function') _refOnTabChange();
    updatePlot();
  }

  closeTab(id) {
    const idx = this.tabs.findIndex(t => t.id === id);
    if (idx === -1) return;
    const closing = this.tabs[idx];
    const closingName = closing.name;
    const wasStack = !!closing.isStack;
    this.tabs.splice(idx, 1);

    // Prune stack entries that referenced the closed tab (skip if it was
    // itself a stack — stacks don't reference each other).
    if (!wasStack) {
      for (const t of this.tabs) {
        if (!t.isStack) continue;
        const before = t.entries.length;
        t.entries = t.entries.filter(e => e.sourceTabId !== id);
        const removed = before - t.entries.length;
        if (removed > 0) {
          notify('Removed "' + closingName + '" from "' + t.name + '" (source tab closed).', 'amber');
          if (t.id === this.activeId) {
            renderStackLegend(t);
            // The chart holds datasets keyed to the removed entry: rebuild
            // it, or the closed source's curves (and, for a local source,
            // their only designation) outlive the entry (Codex A0 round 19).
            _renderStackChart(t);
          }
        }
      }
    }

    if (this.tabs.length === 0) {
      this.activeId = null;
      _updateUndoButtons();
      if (typeof _historyPreview !== 'undefined') _historyPreview = null;
      state.rawBE = []; state.rawIntensity = [];
      state.peaks = []; state.fitResult = null;
      state.ccShift = 0; state.nextId = 1;
      document.getElementById('data-info').textContent = 'no data';
      const _cl = document.getElementById('spec-combo-label');
      if (_cl) _cl.textContent = 'no data';
      document.getElementById('sb-pts').textContent = '\u2014';
      document.getElementById('sb-range').textContent = '\u2014';
      renderPeakList();
      renderEmptyChart();
      this.renderTabBar();
      this._updateSurveyPanel();
      this._updateCCVerifiedUI(true);
      _updateRFactorUI(null);
      _updateROIDisplay(null);
      const notesEl = document.getElementById('spectrum-notes');
      if (notesEl) notesEl.value = '';
      return;
    }

    if (this.activeId === id) {
      const nextIdx = Math.min(idx, this.tabs.length - 1);
      this.activeId = null; // force re-activate
      this.activateTab(this.tabs[nextIdx].id);
    } else {
      this.renderTabBar();
    }
    this._updateSurveyPanel();
  }

  // ── Folder upload ───────────────────────────────

  async loadFolder(fileList) {
    const files = Array.from(fileList);
    if (!files.length) return;

    const eligible = this._filterFiles(files);
    if (!eligible.length) {
      notify('No XPS data files found in folder.', 'amber');
      return;
    }

    const prog = document.getElementById('folder-progress');
    prog.classList.add('active');
    let done = 0;
    const update = () => { prog.textContent = 'Loading ' + done + '/' + eligible.length + '\u2026'; };
    update();

    for (const file of eligible) {
      await this._loadOneFile(file);
      done++;
      update();
    }

    prog.classList.remove('active');
    notify('Loaded ' + done + ' spectra', 'green');
  }

  // ── Serialization ───────────────────────────────

  toJSON() {
    this._syncActiveToRecord();
    return {
      version: 2,
      timestamp: new Date().toISOString(),
      activeId: this.activeId,
      tabs: this.tabs.map(t => ({
        id: t.id, name: t.name, color: t.color, isSurvey: t.isSurvey,
        rawBE: t.rawBE,
        rawIntensity: t.rawIntensity,
        ccShift: t.ccShift,
        peaks: t.peaks.map(p => ({...p})),
        nextId: t.nextId,
        markedElements: t.markedElements || [],
        notes: t.notes || '',
        ui: {...t.ui},
      })),
      // v1 compat keys from active tab
      peaks: state.peaks.map(p => ({...p})),
        ac.classList.remove('open');
      } else if (e.key === 'Escape') {
        ac.classList.remove('open');
      }
    });

    // Close autocomplete when clicking outside
    fresh.addEventListener('blur', () => {
      setTimeout(() => ac.classList.remove('open'), 150);
    });
  }

  /** Add an element to the current survey's marker list */
  _addElement(surveyId, sym) {
    const surveyTab = this._getTab(surveyId);
    if (!surveyTab || !_accSurveyElements()[sym]) return;
    if (!surveyTab.markedElements) surveyTab.markedElements = [];
    if (surveyTab.markedElements.includes(sym)) return; // already added
    surveyTab.markedElements.push(sym);
    this._renderElementMarkers(surveyId);
    updatePlot();
  }

  /** Remove an element from the current survey's marker list */
  _removeElement(surveyId, sym) {
    const surveyTab = this._getTab(surveyId);
    if (!surveyTab || !surveyTab.markedElements) return;
    surveyTab.markedElements = surveyTab.markedElements.filter(s => s !== sym);
    this._renderElementMarkers(surveyId);
    updatePlot();
  }

  /** Switch the main chart back to whatever was active before survey */
  _restoreFromSurvey() {
    if (!this._preSurveyTabId) return;
    const prev = this._getTab(this._preSurveyTabId);
    if (prev) {
      this.activateTab(this._preSurveyTabId);
    }
    this._preSurveyTabId = null;
  }

  // ── Private helpers ─────────────────────────────

  _getTab(id) { return this.tabs.find(t => t.id === id) || null; }

  _syncActiveToRecord() {
    if (!this.activeId) return;
    const t = this._getTab(this.activeId);
    if (!t) return;
    if (t.isStack) return;  // stack tabs have no UI/form state to sync back
    // Re-capture peaks reference in case removePeak/clearAllPeaks replaced the array
    t.peaks = state.peaks;
    t.ccShift = isNaN(state.ccShift) ? 0 : state.ccShift;
    t.nextId = state.nextId;
    t.fitResult = state.fitResult;
    t.lineWidth = state.lineWidth ?? 1.5;
    t.yZoom = state._mainYMax || null;
    t.xZoomMin = state._mainXMin ?? null;
    t.xZoomMax = state._mainXMax ?? null;
    t.notes = document.getElementById('spectrum-notes')?.value || '';
    t.ui = this._captureUI();
  }

  _captureUI() {
    return {
      bgType:      document.getElementById('bg-type')?.value || 'shirley',
      bgStart:     document.getElementById('bg-start')?.value || '',
      bgEnd:       document.getElementById('bg-end')?.value || '',
      shirleyIter: document.getElementById('shirley-iter')?.value || '5',
      endpointAvg: document.getElementById('bg-endpoint-avg')?.value || LEGACY_ENDPOINT_AVG,
      roiMin:      document.getElementById('roi-min')?.value || '',
      roiMax:      document.getElementById('roi-max')?.value || '',
      ccMethod:    document.getElementById('cc-method')?.value || 'none',
      ccObs:       document.getElementById('cc-obs')?.value || '',
      ccLit:       document.getElementById('cc-lit')?.value || '',
      bgSubtractedView: !!document.getElementById('bg-sub-toggle')?.checked,
    };
  }

  _restoreUI(ui) {
    const set = (id, val) => {
      const el = document.getElementById(id);
      if (el && val !== undefined) el.value = val;
    };
    set('bg-type', ui.bgType);
    _syncLegacyBgOption();
    set('bg-start', ui.bgStart);
    set('bg-end', ui.bgEnd);
    set('shirley-iter', ui.shirleyIter);
    set('bg-endpoint-avg', ui.endpointAvg || LEGACY_ENDPOINT_AVG);
    set('roi-min', ui.roiMin);
    set('roi-max', ui.roiMax);
    set('cc-method', ui.ccMethod);
    set('cc-obs', ui.ccObs);
    set('cc-lit', ui.ccLit);
    // Update cc field visibility without dispatching change event
    // (which would overwrite state.ccShift and trigger a double updatePlot)
    const refField = document.getElementById('cc-ref-field');
    const targetField = document.getElementById('cc-target-field');
    if (refField) refField.style.display = (ui.ccMethod === 'none') ? 'none' : 'block';
    if (targetField) targetField.style.display = (ui.ccMethod === 'custom') ? 'block' : 'none';
    // Update shift display from the already-restored state.ccShift
    const shift = -state.ccShift;
    document.getElementById('cc-shift-display').textContent = (shift >= 0 ? '+' : '') + shift.toFixed(3) + ' eV';
    // Update manual bg controls and Shirley iteration state for restored bg type
    if (typeof _onBgTypeChange === 'function') {
      const mc = document.getElementById('manual-bg-controls');
      if (mc) mc.style.display = ui.bgType === 'manual' ? 'block' : 'none';
      const needsIter = (ui.bgType === 'shirley' || ui.bgType === 'smart' || ui.bgType === 'smart_exp' || ui.bgType === 'shirley_linear');
      const si = document.getElementById('shirley-iter');
      if (si) {
        si.disabled = !needsIter;
        si.style.opacity = needsIter ? '1' : '0.4';
      }
      // Endpoint averaging also applies to Tougaard (it sets the high-BE
      // amplitude anchor), not just the Shirley iteration family.
      const needsEpAvg = needsIter || ui.bgType === 'tougaard';
      const epAvg = document.getElementById('bg-endpoint-avg');
      if (epAvg) {
        epAvg.disabled = !needsEpAvg;
        epAvg.style.opacity = needsEpAvg ? '1' : '0.4';
      }
      if (typeof _updateManualAnchorCount === 'function') _updateManualAnchorCount();
    }
    // Bkgrd Sub: restore checked state, sync visual class, refresh enable,
    // and re-gate the dependent overlay controls so they reflect the
    // restored sub-view state.
    const bgSubToggle = document.getElementById('bg-sub-toggle');
    const bgSubPill = document.getElementById('bg-sub-pill');
    if (bgSubToggle && bgSubPill) {
      const want = !!ui.bgSubtractedView;
      bgSubToggle.checked = want;
      bgSubPill.classList.toggle('active', want);
    }
    if (typeof _updateBgSubPillEnabled === 'function') _updateBgSubPillEnabled();
    if (typeof _syncSubViewDependentControls === 'function') _syncSubViewDependentControls();
  }

  _updateCCVerifiedUI(verified) {
    const dot = document.getElementById('cc-warn-dot');
  };
}

function _autoFitRestore(snap, owner) {
  // owner is the record OBJECT the auto-fit started on — normally the one
  // the snapshot itself carries (taken before the first await). Anything
  // that is not a record object (an id from an older caller, undefined) is
  // ignored in favour of the snapshot's owner. A closed tab's id comes back
  // on a NEW object after a project reload, so an id lookup would restore a
  // stale snapshot into the reopened tab (Codex 2026-09-09).
  if (!snap) return;
  if (!owner || typeof owner !== 'object') owner = snap.owner;
  if (!_ownerLive(owner)) return;
  // If the fitting tab is no longer active (the user switched tabs while
  // the auto-fit request was in flight), restore into that tab's RECORD.
  // Writing the snapshot into live state/DOM here would clobber the newly
  // active tab with the fitting tab's pre-auto-fit state while leaving
  // the fitting tab's record in the provisional cc frame (Codex round-2
  // MAJOR — a pre-existing defect for peaks/ccShift/DOM, not just the
  // newly-migrating anchors). activateTab already synced the provisional
  // live state into the record at switch-away, so overwriting the record
  // fields with the snapshot undoes exactly that.
  if (_activeTab() !== owner) {
    const t = owner;
    if (t.isStack) return;
    t.peaks = snap.peaks;
    t.fitResult = snap.fitResult;
    t.ccShift = snap.ccShift;
    t.manualAnchors = snap.manualAnchors || [];
    t.modelProvenance = snap.modelProvenance || null;
    t.nextId = snap.nextId;
    t.ui = { ...t.ui,
      ccMethod: snap.ccMethodDom, ccObs: snap.ccObsDom, ccLit: snap.ccLitDom,
      roiMin: snap.roiMinDom, roiMax: snap.roiMaxDom,
      bgStart: snap.bgStartDom, bgEnd: snap.bgEndDom };
    return;
  }
  state.peaks     = snap.peaks;
  state.fitResult = snap.fitResult;
  state.ccShift   = snap.ccShift;
  _setManualAnchors(snap.manualAnchors || []);
  { const _t = _activeTab(); if (_t) _t.modelProvenance = snap.modelProvenance || null; }
  state.nextId    = snap.nextId;
  const set = (id, v) => { const el = document.getElementById(id); if (el) el.value = v; };
  set('cc-method', snap.ccMethodDom);
  set('cc-obs',    snap.ccObsDom);
  set('cc-lit',    snap.ccLitDom);
  // The provisional 'c1s' correction hid the custom-target field; putting the
  // method back without its field left Custom with no visible input (same
  // rule as the tab-restore path, no change event).
  { const rf = document.getElementById('cc-ref-field'), tf = document.getElementById('cc-target-field');
    if (rf) rf.style.display = (snap.ccMethodDom === 'none') ? 'none' : 'block';
    if (tf) tf.style.display = (snap.ccMethodDom === 'custom') ? 'block' : 'none'; }
  set('roi-min',   snap.roiMinDom);
  set('roi-max',   snap.roiMaxDom);
  set('bg-start',  snap.bgStartDom);
  set('bg-end',    snap.bgEndDom);
  const disp = document.getElementById('cc-shift-display');
  if (disp) {
    const sh = -state.ccShift;
    disp.textContent = (sh >= 0 ? '+' : '') + sh.toFixed(3) + ' eV';
  }
  if (typeof renderPeakList === 'function') renderPeakList();
  if (typeof updatePlot === 'function') updatePlot();
}

// Apply a successful auto-fit result. Mutates state and DOM so the tab
// ends in a self-consistent corrected frame with graphite at exactly 284.50.
// Pure decision: given (id, area) pairs and graphite's id, decide whether
// to emit the < 40% area-fraction warning toast. Returns null on no-warning,
// or { fractionPct, warning } on warning. Boundary: '< 0.40' so 0.40 itself
// does NOT warn.
//
// This logic is intentionally state-free so the Python port test in
// /tmp/test_autofit_decide_warning.py can validate it without simulating
// state.peaks or the backend.
function _autoFitDecideAreaWarning(peakAreas, graphiteId) {
  if (!Array.isArray(peakAreas)) return null;
  let total = 0;
  let graphiteArea = null;
  for (const entry of peakAreas) {

exec
/bin/zsh -lc "rg -n 'unsupported|not supported|suppress|centre|center' CLAUDE.md | head -55; rg -n 'seed|jitter|nondetermin|last.digit|least_squares' fitting.py | head -70; rg --files -g '*browser*' -g '*package*' -g '*pytest*' -g '*proj*' -g '*roi*'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
95:  center, fwhm, amplitude,
143:full β/m box on eight grids, irregular grids and centres outside the
148:zero-amplitude component and step (b) flags it; and a centre OUTSIDE the
151:in-range centre against main's function (`scripts/dsg_outside_centre_identity.py`). Details of
188:Implementation convention: `dx = center − x`. The power-law term
189:extends the tail toward higher BE (`x > center` ⇒ `dx < 0`). The
192:`doniachSunjic`, equivalent to `exp(−gamma_asym · max(x − center, 0))`
234:**suppresses** the high-BE tail; decreasing α extends it (BE-axis
268:A linked peak derives its center, amplitude, and **all lineshape
276:| `center` | `parent.center + linkOffset` |
299:(a free DS+G centre has no default window either), so until 2026-09-19
306:itself; centre = the fitted energy range, always a real interval), then —
410:`docs/superpowers/plans/2026-09-21-scattered-starts-and-unsupported-components.md`).**
416:REQUEST's start (amplitude ×/÷ 3, width ×/÷ 1.5, free centres ± 0.5 eV,
419:every area fraction within 1 pp and every centre within 0.1 eV, COMPONENT
426:than 0.1 %, each with its own areas and every component's centre shift
458:during a fit; a newly locked centre would otherwise keep its edited value
477:the ONLY engine Batch Fit uses. Central-difference Jacobian (centre
529:the fit did not determine it — and its centre, width and σ are not reported
549:suppressed or excluded until a new fit writes a new verdict (a verdict
560:every centre and refines the charge shift AFTER the result is applied, so
566:(`_isUnsupported`): sidebar card (badge; centre/width "—"; excluded from the
567:area total), Results table (greyed row, no centre/width/σ, area kept,
570:instead of the neutral "locked" note Auto-Fit's centre lock would produce),
584:artefact can mark a real component unsupported; REDUNDANCY UNDER OVERLAP is
602:previous peaks and result kept. Before this, a centre changed and locked
646:Auto-Fit C1s Graphite derives that shift from the FITTED centre of its
661:input is touched. Until 2026-09-21 only the centre was checked (±0.3 eV of
663:centre is bounded to that window. Do NOT replace this with an intensity
702:  not-required anchor exactly like an unsupported one, before any
817:- **ROI past the data / centre outside the data** (2026-09-25, warn only):
822:  peak card whose centre lies outside the selected data ("outside data").
827:  `docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md`.
1045:    then refine FROM that solution with ``least_squares`` under the request's
1072:    # Only what a local solver understands: DE options (seed, popsize, ...)
1073:    # passed through fit_kws would make least_squares raise.
1074:    refine_kws = {"method": "least_squares", "nan_policy": kws.get("nan_policy", "omit")}
1080:    # A converged refinement IS the result: it is a least_squares fit of the
1083:    # compared with the boxed search's chi-square. least_squares descends
1102:    outside the fitted range (chi-square 1e7 where ``least_squares`` from the
1104:    to from there. So a ``least_squares`` fit from the candidate's own start,
1114:                          method="least_squares", nan_policy=kws.get("nan_policy", "omit"))
1130:# numpy's global generator, unseeded.
1131:_FIT_METHODS = ("leastsq", "least_squares", "nelder", "differential_evolution", "basinhopping")
1148:def _request_seed(x, counts, background, shapes, prefixes, params, *, fit_kws, n_perturb) -> int:
1149:    """The seed for every random draw of one fit: a pure function of the
1168:    request was hashed as sent.) It is a seed, not an identity: 32 bits
1173:    solver = {k: v for k, v in dict(kws.pop("fit_kws", None) or {}).items() if k != "seed"}
1193:    h = hashlib.sha256(b"xps-fit-seed-v1\0")
1198:    return int.from_bytes(h.digest()[:4], "little")            # 32 bits: what scipy's seed accepts
1212:_STARTS_METHODS = ("leastsq", "least_squares", "nelder")     # the global methods already search
1220:    built from the request, never a fitted solution, which jitters): free
1392:    (the same candidate machinery and seeding the fit used, so differential
1393:    evolution's box/refinement and the request seed apply to the refit too).
1473:    # at 1e-8 and a different fit), and the seed hashes float64.
1491:    # A caller's seed is consumed HERE: it replaces the request-derived one
1492:    # and is never forwarded as a solver option (least_squares, leastsq and
1493:    # nelder reject a 'seed' keyword).
1495:    caller_seed = solver_kws.pop("seed", None)
1498:    if caller_seed is not None and (
1499:            isinstance(caller_seed, (bool, np.bool_)) or not isinstance(caller_seed, (int, np.integer))
1500:            or not 0 <= int(caller_seed) < 2 ** 32):
1501:        raise ValueError("fit_kws.fit_kws.seed must be an integer in [0, 2**32)")
1634:    # generator) comes from this one seed, so an identical request gives
1637:    if caller_seed is not None:
1638:        random_seed = int(caller_seed)
1640:        random_seed = _request_seed(
1647:                                           for child in np.random.SeedSequence(random_seed).spawn(3))
1660:    def seeded(call_kws):
1661:        """``call_kws`` with a fresh solver seed for the stochastic methods
1667:        solver_kws["seed"] = int(solver_rng.integers(0, 2 ** 32 - 1))
1671:    # when the method is differential evolution, else a plain seeded fit. The
1678:            return _global_or_local_candidate(model, params, bounds, y_sub, x, weights, seeded(kws))
1679:        return model.fit(y_sub, params, x=x, weights=weights, **seeded(kws))
1930:        "random_seed": random_seed,
tests/test_browser_find_peaks_tooltip_markup.py
tests/test_browser_find_peaks_coverage.py
tests/test_browser_batch_roi.py
tests/test_browser_identify_frame.py
tests/test_browser_overlay_zip_roundtrip.py
tests/test_browser_find_peaks_drag.py
tests/test_browser_endpoint_avg_default.py
tests/test_browser_palette.py
tests/test_browser_shirley_linear_delist.py
tests/test_browser_find_peaks_full_window.py
tests/test_browser_find_peaks_endpoint_avg.py
tests/test_browser_cc_overlay_repaint.py
tests/test_browser_find_peaks_method_tooltips.py
tests/test_browser_legacy_auger.py
tests/test_browser_reference_mode.py
tests/test_browser_manual_anchor_cc_migration.py
tests/test_browser_per_tab_state.py
docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md
tests/test_browser_bg_window_request.py
tests/test_browser_find_peaks_progress.py
tests/js/roi_clamp_centre_warning.test.js
tests/autofit/test_browser_schema_roundtrip.py
docs/autofit/test_data/Project9_CasaXPS_newfit.proj.zip
docs/autofit/test_data/8-JT Graphite.proj.zip
docs/autofit/test_data/UCl4_on_graphite.proj.zip
docs/autofit/test_data/4-GTA UCl4-BN.proj.zip
docs/autofit/test_data/Cl2p_projfit_test.proj.zip
docs/autofit/test_data/B4C-UCl4.proj.zip
docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip
docs/autofit/codex/roi_clamp_verdict_runA.md
docs/autofit/codex/fe2p_roi_widen_review_prompt.txt
docs/autofit/codex/fe2p_roi_widen_verdict_runB.md
docs/autofit/codex/fe2p_roi_widen_verdict_runA.md
docs/autofit/codex/roi_clamp_review_prompt.txt
docs/autofit/codex/roi_clamp_verdict_runB.md

exec
/bin/zsh -lc 'node --test tests/js/roi_clamp_centre_warning.test.js tests/js/unsupported_components.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 157ms:
# Subtest: an ROI inside the data: no hint
ok 1 - an ROI inside the data: no hint
  ---
  duration_ms: 4.644178
  type: 'test'
  ...
# Subtest: an ROI past the data by more than one step: the quiet hint names the window actually used
ok 2 - an ROI past the data by more than one step: the quiet hint names the window actually used
  ---
  duration_ms: 2.567724
  type: 'test'
  ...
# Subtest: one side past the data is enough; the window named is the selected data
ok 3 - one side past the data is enough; the window named is the selected data
  ---
  duration_ms: 2.870534
  type: 'test'
  ...
# Subtest: a sub-step overshoot (a toFixed(1) rounding of the data edge) is not "past the data"
ok 4 - a sub-step overshoot (a toFixed(1) rounding of the data edge) is not "past the data"
  ---
  duration_ms: 2.186879
  type: 'test'
  ...
# Subtest: min above max: amber, no data selected (getROIData selects nothing)
ok 5 - min above max: amber, no data selected (getROIData selects nothing)
  ---
  duration_ms: 3.179217
  type: 'test'
  ...
# Subtest: an ROI that misses the data entirely: amber, names the data range
ok 6 - an ROI that misses the data entirely: amber, names the data range
  ---
  duration_ms: 1.852307
  type: 'test'
  ...
# Subtest: empty fields mean the full range (as getROIData): no hint
ok 7 - empty fields mean the full range (as getROIData): no hint
  ---
  duration_ms: 1.483086
  type: 'test'
  ...
# Subtest: the window is in the CORRECTED frame (raw − ccShift), as the fit and Find Peaks use it
ok 8 - the window is in the CORRECTED frame (raw − ccShift), as the fit and Find Peaks use it
  ---
  duration_ms: 3.053429
  type: 'test'
  ...
# Subtest: a descending acquisition behaves the same
ok 9 - a descending acquisition behaves the same
  ---
  duration_ms: 2.740293
  type: 'test'
  ...
# Subtest: centre outside the SELECTED data is flagged; inside, at the edges, or with no data selected is not
ok 10 - centre outside the SELECTED data is flagged; inside, at the edges, or with no data selected is not
  ---
  duration_ms: 3.792881
  type: 'test'
  ...
# Subtest: the helpers write nothing: no assignment to a field value, a peak or the fit state
ok 11 - the helpers write nothing: no assignment to a field value, a peak or the fit state
  ---
  duration_ms: 1.40341
  type: 'test'
  ...
# Subtest: the fit and Find Peaks still read the ROI exactly as before (getROIData / the two field values)
ok 12 - the fit and Find Peaks still read the ROI exactly as before (getROIData / the two field values)
  ---
  duration_ms: 1.240633
  type: 'test'
  ...
# Subtest: the twin reproduces the server verdict on real responses, and defers to the server field when present
ok 13 - the twin reproduces the server verdict on real responses, and defers to the server field when present
  ---
  duration_ms: 8.27279
  type: 'test'
  ...
# Subtest: _applySupport writes every peak, follows ancestry to the root, stamps the fit key, and leaves null where the response says nothing
ok 14 - _applySupport writes every peak, follows ancestry to the root, stamps the fit key, and leaves null where the response says nothing
  ---
  duration_ms: 4.320641
  type: 'test'
  ...
# Subtest: the verdict applies only to the model and context it was computed for
ok 15 - the verdict applies only to the model and context it was computed for
  ---
  duration_ms: 3.626263
  type: 'test'
  ...
# Subtest: the local engine computes the same statistic from its own residuals
ok 16 - the local engine computes the same statistic from its own residuals
  ---
  duration_ms: 4.771154
  type: 'test'
  ...
# Subtest: sidebar card: badge; centre and width shown as a dash; area % excluded and the others renormalised
ok 17 - sidebar card: badge; centre and width shown as a dash; area % excluded and the others renormalised
  ---
  duration_ms: 6.151613
  type: 'test'
  ...
# Subtest: results table: greyed row, no centre / width / sigma, area kept, percentage dash, and the note beneath
ok 18 - results table: greyed row, no centre / width / sigma, area kept, percentage dash, and the note beneath
  ---
  duration_ms: 11.915628
  type: 'test'
  ...
# Subtest: uncertainty panel: one rule-0 warning for the component, no per-parameter alarms and no "locked" note for it
ok 19 - uncertainty panel: one rule-0 warning for the component, no per-parameter alarms and no "locked" note for it
  ---
  duration_ms: 4.782231
  type: 'test'
  ...
# Subtest: Quantify: excluded from the body, listed beneath with the reason; total and percentages over the rest
ok 20 - Quantify: excluded from the body, listed beneath with the reason; total and percentages over the rest
  ---
  duration_ms: 4.547766
  type: 'test'
  ...
# Subtest: CSV / XLSX export: Status column, suppressed cells, At% empty, WARNING line
ok 21 - CSV / XLSX export: Status column, suppressed cells, At% empty, WARNING line
  ---
  duration_ms: 5.718837
  type: 'test'
  ...
# Subtest: publication figure: no label at the (zero) component, legend entry says so; chart and stack labels say so
ok 22 - publication figure: no label at the (zero) component, legend entry says so; chart and stack labels say so
  ---
  duration_ms: 2.103484
  type: 'test'
  ...
# Subtest: write-back: a server result sets support; the local engine and a propagated model reset it
ok 23 - write-back: a server result sets support; the local engine and a propagated model reset it
  ---
  duration_ms: 1.291008
  type: 'test'
  ...
# Subtest: persistence: support travels with the peak object through every save (the peak is spread whole)
ok 24 - persistence: support travels with the peak object through every save (the peak is spread whole)
  ---
  duration_ms: 0.813235
  type: 'test'
  ...
# Subtest: CSV / XLSX: an unsupported DS+G component exports no width of any kind (beta, m)
ok 25 - CSV / XLSX: an unsupported DS+G component exports no width of any kind (beta, m)
  ---
  duration_ms: 4.457808
  type: 'test'
  ...
# Subtest: the scattered-starts table: an unsupported component shows neither area % nor a move in "Your fit", and is not the largest move
ok 26 - the scattered-starts table: an unsupported component shows neither area % nor a move in "Your fit", and is not the largest move
  ---
  duration_ms: 5.173282
  type: 'test'
  ...
# Subtest: exports: a stale or keyless verdict is "not established", never "supported"
ok 27 - exports: a stale or keyless verdict is "not established", never "supported"
  ---
  duration_ms: 6.978645
  type: 'test'
  ...
# Subtest: Auto-Fit finalisation (locks, charge shift) keeps its own verdicts: _restampSupport, called after the locks
ok 28 - Auto-Fit finalisation (locks, charge shift) keeps its own verdicts: _restampSupport, called after the locks
  ---
  duration_ms: 3.620835
  type: 'test'
  ...
# Subtest: a .fit.json import onto this tab's data carries no verdict
ok 29 - a .fit.json import onto this tab's data carries no verdict
  ---
  duration_ms: 0.101547
  type: 'test'
  ...
# Subtest: _isUnsupported is never handed an array index as its key (Array.filter passes one)
ok 30 - _isUnsupported is never handed an array index as its key (Array.filter passes one)
  ---
  duration_ms: 2.906655
  type: 'test'
  ...
# Subtest: a key change re-renders every consumer of the verdict — each compared with ITS OWN rendering
ok 31 - a key change re-renders every consumer of the verdict — each compared with ITS OWN rendering
  ---
  duration_ms: 2.203147
  type: 'test'
  ...
# Subtest: stack tabs judge a source component against the SOURCE record's key
ok 32 - stack tabs judge a source component against the SOURCE record's key
  ---
  duration_ms: 3.28863
  type: 'test'
  ...
# Subtest: "Your fit" percentages are over supported components; an empty Quantify shows no 100 %
ok 33 - "Your fit" percentages are over supported components; an empty Quantify shows no 100 %
  ---
  duration_ms: 8.93272
  type: 'test'
  ...
# Subtest: the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
ok 34 - the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
  ---
  duration_ms: 3.541957
  type: 'test'
  ...
1..34
# tests 34
# suites 0
# pass 34
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 207.899161

exec
/bin/zsh -lc "sed -n '15720,15845p' templates/index.html; sed -n '15890,16040p' templates/index.html; rg -n '_fpSyncSelectionUI|_fpToggleRegion|function closeFindPeaks|function openFindPeaks|fp-modal|fp-panel' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
      payload.peak_specs = state.peaks.map(peakToBackendSpec);
      if (!payload.peak_specs.length) {
        status.textContent = '“Refit my current peaks” needs peaks on ' +
          'this tab first — add some, or pick “Compare peak models”.';
        return;
      }
    }
    payload.session_id = await uploadToBackend(be, inten);
    const resp = await fetch('/api/analyze/start', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    // Don't assume the body is JSON before checking resp.ok — a worker
    // timeout/crash can return a bare non-JSON 500 (plain text or an HTML
    // error page), and calling .json() on that throws an opaque SyntaxError
    // instead of a message the user can act on.
    const ct = resp.headers.get('content-type') || '';
    if (!resp.ok) {
      let msg = 'HTTP ' + resp.status;
      if (ct.includes('application/json')) {
        try {
          const errBody = await resp.json();
          if (errBody && errBody.error) msg = errBody.error;
        } catch (_) { /* not actually JSON despite the header; use HTTP status */ }
      } else {
        const text = (await resp.text()).replace(/<[^>]*>/g, ' ').trim();
        if (text) msg += ': ' + text.slice(0, 300);
      }
      throw new Error(msg);
    }
    const { job_id } = await resp.json();
    const poll = await _fpPollJob(job_id);
    const body = poll.result;
    if (!_ownerLive(owner)) { status.textContent = 'Discarded — the tab was closed during the analysis.'; return; }
    _fpSetLast({ body, method, regions, fitFullWindow: !!options.fit_full_window, endpointAvg: engineEndpointAvg }, owner);
    if (!_ownerActive(owner)) {
      // The result belongs to the tab it was started on; do not show it
      // over another tab's modal.
      status.textContent = 'Results stored on tab “' + owner.name + '” — switch back to it and reopen Find Peaks to apply.';
      notify('Find Peaks finished on tab “' + owner.name + '”; its results are waiting there.', 'amber');
      return;
    }
    _fpRenderResults(body);
    status.textContent = '';
  } catch (e) {
    status.textContent = 'Failed: ' + e.message;
  } finally {
    // ALWAYS clears — success, error, and watchdog-timeout paths all land
    // here (goal: the indicator must never spin forever).
    btn.disabled = false;
    spinner.style.display = 'none';
  }
}

function _fpEsc(s) {
  return String(s == null ? '' : s).replace(/[&<>"]/g,
    c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}

function _fpBanner(text, color) {
  return `<div style="font-size:10px;padding:5px 8px;margin:3px 0;border-left:3px solid ${color};background:var(--bg2)">${text}</div>`;
}

function _fpRenderResults(body) {
  const flags = [];
  const d = body.diagnostics || {}, a = body.analysis || {};
  const B = FP_STRINGS.banners;
  if (!body.success) flags.push(_fpBanner(_fpEsc(B.noResult), '#e05555'));
  if (d.analysis_truncated) {
    flags.push(_fpBanner(_fpEsc(_fpFmt(B.truncated, {
      evaluated: d.n_candidates_evaluated, total: d.n_candidates_total,
    })), '#e0a030'));
  }
  if (d.conditional) {
    // the engine's decisive_override / no_clean_survivor stories, said
    // plainly: a literature-based limit had to hold the fit together
    const pinned = (d.winner_boundary_fixed_params || [])
      .map(_fpParamLabel).join(', ');
    if (pinned) {
      flags.push(_fpBanner(_fpEsc(_fpFmt(B.pinnedLimit, { param: pinned })),
                           '#e0a030'));
    } else {
      const hits = (d.winner_boundary_hits || [])
        .map(h => _fpParamLabel('s_' + String(h).replace(':', '_')
                                .replace(/@(min|max)$/, ''))).join(', ');
      flags.push(_fpBanner(_fpEsc(_fpFmt(B.constraintBind,
        { details: hits || 'see Technical details' })), '#e0a030'));
    }
  }
  if (d.filtered_dominant_alternative) {
    const f = d.filtered_dominant_alternative;
    flags.push(_fpBanner('&#9888; ' + _fpEsc(_fpFmt(B.hiddenBetter, {
      name: _fpModelLabel(f.name),
      reason: _fpFilterReasonLabel(f.filter_reason).toLowerCase(),
    })), '#e05555'));
  }
  if (a.ambiguous_pairs && a.ambiguous_pairs.length)
    flags.push(_fpBanner(_fpEsc(_fpFmt(B.tooCloseToCall, {
      pairs: a.ambiguous_pairs
        .map(p => _fpModelLabel(p[0]) + ' vs ' + _fpModelLabel(p[1]))
        .join('; '),
    })), '#e0a030'));
  if (a.model_selection_warning || a.selection_warning)
    flags.push(_fpBanner(_fpEsc(a.model_selection_warning || a.selection_warning), '#e0a030'));
  const nonv = (a.uses_conditional_or_unverified_constants || []).length;
  if (nonv) flags.push(_fpBanner(_fpEsc(B.provisional), '#888'));
  const anyProposed = (body.peaks || []).some(
    p => /^proposed_peak_/.test(p.role || ''));
  if (anyProposed) flags.push(_fpBanner(_fpEsc(B.extraPeakFound), '#e0a030'));
  document.getElementById('fp-flags').innerHTML = flags.join('');
  // plain-English default; the untranslated engine story stays available
  // one level deeper, under Advanced (raw engine output)
  document.getElementById('fp-message-plain').textContent = _fpPlainMessage(body);
  document.getElementById('fp-message').textContent = body.message || '';

  const td = 'padding:2px 6px;border-bottom:1px solid var(--border);text-align:left';
  const T = FP_STRINGS.tips;
  const th = (text, tip) =>
    `<th style="${td}" title="${_fpEsc(tip)}">${_fpEsc(text)}</th>`;
  const peaks = body.peaks || [];
  document.getElementById('fp-peaks').innerHTML =
    '<tr>' + th('peak', 'Which component this is in the suggested model.') +
    th('shape', T.shape) + th('position (eV)', T.position) +
    th('width (eV)', T.width) + th('height', T.height) +
    th('± position (eV)', T.sigmaCenter) + '</tr>' +
    peaks.map(p => {
    case 'gaussian':        o.shape = 'Gaussian'; break;
    case 'lorentzian':      o.shape = 'Lorentzian'; break;
    case 'asymmetric_gl':   o.shape = 'asym-GL';
      o.glMix = 100 * (p.gl_ratio ?? 0.3); o.asymmetry = p.asymmetry ?? 0.1; break;
    case 'doniach_sunjic':  o.shape = 'DS';
      o.dsAlpha = p.alpha ?? 0.1; o.dsGamma = p.gamma_asym ?? 0; break;
    case 'ds_g':            o.shape = 'DSG_LA';
      o.laAlpha = p.alpha ?? 0.1; o.laBeta = p.beta ?? 0.3; o.laM = p.m_gauss ?? p.fwhm ?? 1; break;
    case 'la_casaxps':      o.shape = 'LACX';
      o.caAlpha = p.alpha ?? 1; o.caBeta = p.beta ?? 1; o.caM = p.m ?? 50; break;
    default:                o.shape = 'GL'; o.glMix = 100 * (p.gl_ratio ?? 0.3);
  }
  return defaultPeak(o);
}

// One-time "these are unverified" confirmation, replacing the old
// required-reviewer-name gate. Same Promise/resolver pattern as
// _showAutoFitConfirmModal/_autoFitConfirmCancel.
let _findPeaksApplyConfirmResolver = null;
function _showFindPeaksApplyConfirmModal() {
  return new Promise(resolve => {
    _findPeaksApplyConfirmResolver = resolve;
    const proceed = document.getElementById('find-peaks-apply-confirm-proceed');
    proceed.onclick = () => {
      document.getElementById('find-peaks-apply-confirm-overlay').classList.remove('open');
      const r = _findPeaksApplyConfirmResolver; _findPeaksApplyConfirmResolver = null;
      if (r) r(true);
    };
    document.getElementById('find-peaks-apply-confirm-overlay').classList.add('open');
  });
}
function _findPeaksApplyConfirmCancel() {
  document.getElementById('find-peaks-apply-confirm-overlay').classList.remove('open');
  const r = _findPeaksApplyConfirmResolver; _findPeaksApplyConfirmResolver = null;
  if (r) r(false);
}

async function applyFindPeaks() {
  const owner = _opOwner();              // the record this apply belongs to
  const _fpLast = _fpGetLast();          // the ACTIVE tab's own result, or nothing
  if (!owner || !_fpLast) return;
  const peaks = (_fpLast.body.peaks || []);
  if (!peaks.length) { notify('Nothing to apply — the analysis emitted no peaks.', 'amber'); return; }
  if (state.peaks.length &&
      !confirm('Replace the ' + state.peaks.length + ' peak(s) on this tab ' +
               'with the ' + peaks.length + ' suggested peak(s)? ' +
               'You can undo this.')) return;
  if (!(await _showFindPeaksApplyConfirmModal())) return;
  if (!_ownerActive(owner)) {
    // The tab changed (or closed) while the confirmation was open: the
    // suggestions belong to the tab they were produced on, so nothing is
    // written anywhere.
    notify('Apply cancelled — the tab changed while the confirmation was open.', 'amber');
    return;
  }
  // the manual path's real undo: the replaced peak list must be Ctrl-Z
  // recoverable (Codex analyze review blocker). This action also changes
  // endpoint averaging (below), so the undo entry carries the pre-apply
  // value and undo/redo restore it with the peaks.
  pushUndo({ endpointAvg: document.getElementById('bg-endpoint-avg')?.value });
  // DURABLE provenance record: stamped on every applied peak (peak objects
  // round-trip through project save/load with extra fields intact, like
  // _rsfKey does) — no reviewer name anymore, but autoSuggested/verified
  // keep the "these came from Find Peaks and haven't been checked" fact
  // alive through save/load.
  const review = {
    autoSuggested: true, verified: false,
    method: _fpLast.method, regions: _fpLast.regions,
    winner: (_fpLast.body.diagnostics || {}).winner || null,
    at: new Date().toISOString(),
  };
  state.peaks = peaks.map((p, i) => {
    const fp = _fpPeakFromBackend(p, i);
    fp._findPeaks = review;
    return fp;
  });
  { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }   // the replaced model's provenance does not describe these peaks
  const active = tabManager.tabs.find(t => t.id === tabManager.activeId);
  if (active) active._findPeaksReview = review;
  // Find Peaks now sends the Background panel's endpoint averaging (see
  // runFindPeaks), so normally this is a no-op. It still guards preview ==
  // fit when the panel was changed between the run and the apply, or when
  // the Advanced JSON named a different value: the panel and the tab
  // record are set to what the engine actually used, with a notice.
  // (No _invalidateBgCache() here: with "fit the entire window" OFF the
  // frozen fit display must stay exactly as today — invalidating the cache
  // un-froze it, caught by test_checkbox_off_preserves_todays_cropped_behavior;
  // with it ON, state.fitResult is cleared below and the preview recomputes
  // from the panel value anyway.)
  const usedEp = (_fpLast && _fpLast.endpointAvg) || LEGACY_ENDPOINT_AVG;
  const epEl = document.getElementById('bg-endpoint-avg');
  const epChanged = !!epEl && epEl.value !== usedEp;
  if (epEl) epEl.value = usedEp;
  if (active) active.ui.endpointAvg = usedEp;   // unconditional: the record must match the fit even if the field was hand-edited
  if (epChanged) {
    notify('Find Peaks fitted with endpoint averaging ' + usedEp + '; the Background panel was set to ' +
           usedEp + ' so the preview matches the fit.', 'amber');
  }
  // The chart FREEZES its background/fit-curve display to state.fitResult's
  // OWN be/bgIntensity arrays once a fit exists (updatePlot's "haveFit"
  // branch) — a prior manual Run Fit or Auto-Fit C1s Graphite leaves this
  // set, frozen to THAT fit's own (possibly narrower) range. Applying new
  // Find Peaks peaks on top never touched it, so the chart kept showing
  // background/fit cropped to the OLD frozen range regardless of how wide
  // a window Find Peaks actually used — root cause of "fit + background
  // don't span the full selected window" (2026-07-14 bug report). Find
  // Peaks' own response has no be/fittedY/bgIntensity arrays to rebuild a
  // proper fitResult from, so when this run used "fit the entire window,"
  // clear it instead: updatePlot() then falls back to its existing
  // unfit-preview path (getROIData() + client-side computeBackground()),
  // exactly like peaks placed manually before any Run Fit — spanning the
  // CURRENT #roi-min/#roi-max, i.e., the full window Find Peaks just used.
  // Default (unchecked) leaves state.fitResult untouched — today's
  // behavior, unchanged.
  if (_fpLast && _fpLast.fitFullWindow) {
    state.fitResult = null;
    // Clearing state.fitResult fixes the CHART (updatePlot's "haveFit"
    // branch), but the status-bar widgets (χ²ᵣ, R-factor, "ROI: ...")
    // are a SEPARATE piece of DOM state that only refreshes when
    // explicitly told to (Codex review finding, 2026-07-14: this was
    // the other half of the bug report's exact symptom — the header
    // could still read the OLD fit's stale "ROI: 278.0-290.4 eV" even
    // after the chart itself had been fixed). Reset them to the SAME
    // "no committed fit yet" state TabManager.activateTab already uses
    // when a tab has no state.fitResult, rather than inventing a new
    // convention.
    const fqEl = document.getElementById('fit-quality');
    if (fqEl) { fqEl.innerHTML = '&#967;&#178; &mdash;'; fqEl.removeAttribute('data-xps-tip'); }
    const chiEl = document.getElementById('sb-chi');
    if (chiEl) chiEl.textContent = '—';
    _updateRFactorUI(null);
    _updateROIDisplay(null);
    // The right-side Results panel (#results-area) is a THIRD piece of
    // DOM state keyed off state.fitResult, separate from both the chart
    // and the status bar (Codex recheck finding, 2026-07-14): without
    // this call it kept showing the OLD fit's chi/RMSE/table after
    // state.fitResult was cleared, until some unrelated later action
    // happened to re-render it. renderResults() already handles
    // state.fitResult === null correctly (falls back to its own
    // "Run the fit to see results." placeholder).
    renderResults();
  }
  renderPeakList();
  updatePlot();
  closeFindPeaksModal();
  notify(_fpFmt(FP_STRINGS.toastApplied, { n: peaks.length }), 'amber', true);
}
</script>
</body>
</html>
15161:async function openFindPeaksModal() {
15230:function closeFindPeaksModal() {
15417:      ` onclick="_fpToggleRegion('${_fpEsc(e.region)}', event.ctrlKey||event.metaKey)"` +
15418:      ` onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();_fpToggleRegion('${_fpEsc(e.region)}', event.ctrlKey||event.metaKey)}"` +
15453:  _fpToggleRegion(region, additive);
15479:function _fpToggleRegion(region, additive) {
15481:  _fpSyncSelectionUI();
15484:function _fpSyncSelectionUI() {
15667:  // submitted (see _fpToggleRegion / _fpSyncSelectionUI).

exec
/bin/zsh -lc "rg -n 'restore|undo|preview' templates/index.html | tail -65; sed -n '4930,5020p' templates/index.html; sed -n '5158,5195p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
8074:      : '&#9888; <strong>The history preview overlay is a local fit &mdash; a starting point, not a reportable result.</strong>';
8541:  _applyStatDisplay(state.fitResult);   // header + status bar track every result change (clear, restore, auto-fit) as one unit
9454:  // Before fitting, they come from the current ROI so live peak previews still work.
9573:  // History snapshot preview overlay (cyan dashed, drawn on top)
9720:      c.restore();
9753:      ctx.restore();
9768:  const previewGlowPlugin = {
9769:    id: 'previewGlow',
9780:      chart.ctx.restore();
9788:    plugins: [surveyLabelPlugin, pinYRangePlugin, bgSubZeroLinePlugin, overlayPlugin, previewGlowPlugin, xpsRefLinesPlugin],
10404://   'DSG' → 'DS'     — DSG had a JS-only Gaussian-broadening preview
10407://                       restores the curve that was actually being fit.
10430:    console.info('[migration] Migrated ' + counts['DSG->DS'] + " peaks from 'DSG' → 'DS' (DSG's Gaussian-broadening preview was cosmetic only and did not affect fits; loading as DS shows the curve that was actually being fit).");
10511:  const srcPath = data.sourcePath || (sessionFile ? sessionFile : '(restored)');
10528:  // v1 fit-file loader and the project tab deserializer both restore).
10530:  // restore below: _restoreUI refreshes the manual-anchor count label from
10542:  tabManager._restoreUI(active.ui);
10557:  renderResults();   // installs the restored result's designation in Results/Quantify and the statistic display (unit A0)
10658:      // Stack tab — shape matches createStackTab; entries restored verbatim
10689:      sourcePath: t.sourcePath || (sessionFile ? sessionFile : '(restored)'),
10697:      // Autofit candidate-set annotations — restored verbatim when present
10710:      // B2: restore per-tab element overlays. deserializeRefOverlays is total —
10712:      // overlays). Valid saved colorIdx restored verbatim; invalid repaired
10714:      // explicitly). No identify marker is ever restored.
10758:  // Phase 5: advance _nextStackNum past the highest restored "▦ Stack N"
10781:  const restoreId = (resolvedActiveId && tabManager.tabs.some(t => t.id === resolvedActiveId))
10784:  // B2: restore the GLOBAL compound markers ONCE (project-meta scope), before
10794:  if (restoreId) tabManager.activateTab(restoreId);
10797:  // any tab restored overlays, ensure that data is fetched even with the palette
10804:  // restored compound markers immediately).
11063:  ctx.restore();
11130:  ctx.restore();
11162:    ctx.restore();
11230:    ctx.restore();
11262:    ctx.restore();
11625:  // When leaving survey sidebar tab, restore the previous main chart
11628:    tabManager._restoreFromSurvey();
12056:    // Apply to target tab record (without switching UI) — undoable on that record
12076:      tabManager._restoreUI(tgt.ui);
12173:  ctx.restore();
12251:  ctx.restore();
12944:  // colour until the palette is exhausted, and restored + new overlays stay
13299:    c.restore();
13338:          c.restore();
13383:    c.restore();
13994:  document.querySelectorAll('.hist-row').forEach(r => r.classList.remove('hist-preview-active'));
13996:  if (row) row.classList.add('hist-preview-active');
14003:  document.querySelectorAll('.hist-row').forEach(r => r.classList.remove('hist-preview-active'));
14016:  tab.modelProvenance = null;   // the restored result governs the designation (unit A0)
14024:  notify('Snapshot restored.', 'green');
14086:// stays in the DOM disabled + hidden so a saved file can still restore it.
14087:// While it IS the selected type (reachable via a restored tab.ui, or via
14277:  ctx.restore();
14651:                title="Replaces this tab's current peaks with the suggested ones. You can undo this.">Add peaks to my fit</button>
14768:             'suggested peaks. You can undo this (Ctrl+Z).',
14918:                'You can undo this.',
15680:  // sent is recorded on the tab's findPeaks.last so applyFindPeaks keeps preview == fit.
15936:               'You can undo this.')) return;
15945:  // the manual path's real undo: the replaced peak list must be Ctrl-Z
15947:  // endpoint averaging (below), so the undo entry carries the pre-apply
15948:  // value and undo/redo restore it with the peaks.
15970:  // runFindPeaks), so normally this is a no-op. It still guards preview ==
15977:  // with it ON, state.fitResult is cleared below and the preview recomputes
15986:           usedEp + ' so the preview matches the fit.', 'amber');
15999:  // unfit-preview path (getROIData() + client-side computeBackground()),
// ═══════════════════════════════════════════════════
function _onCCObsInput() {
  // Mark as verified when user manually edits the observed BE
  const tab = tabManager && tabManager._getTab(tabManager.activeId);
  if (tab && tab.chargeVerified === false) {
    tab.chargeVerified = true;
    tabManager._updateCCVerifiedUI(true);
  }
  updateChargeCorrection();
}

function updateChargeCorrection() {
  const prevShift = state.ccShift;
  const method = document.getElementById('cc-method').value;
  const refField = document.getElementById('cc-ref-field');
  const targetField = document.getElementById('cc-target-field');

  refField.style.display = 'none';
  targetField.style.display = 'none';

  if (method === 'c1s') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    state.ccShift = isNaN(obs) ? 0 : obs - 284.5;
    refField.style.display = 'block';
    document.getElementById('cc-lit').value = '284.5';
  } else if (method === 'c1s-adv') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    state.ccShift = isNaN(obs) ? 0 : obs - 284.8;
    refField.style.display = 'block';
    document.getElementById('cc-lit').value = '284.8';
  } else if (method === 'au4f') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    state.ccShift = isNaN(obs) ? 0 : obs - 83.98;
    refField.style.display = 'block';
    document.getElementById('cc-lit').value = '83.98';
  } else if (method === 'b1s-b2o3') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    state.ccShift = isNaN(obs) ? 0 : obs - 192.99;
    refField.style.display = 'block';
    document.getElementById('cc-lit').value = '192.99';
  } else if (method === 'n1s-bn') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    state.ccShift = isNaN(obs) ? 0 : obs - 398.31;
    refField.style.display = 'block';
    document.getElementById('cc-lit').value = '398.31';
  } else if (method === 'b1s-bn') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    state.ccShift = isNaN(obs) ? 0 : obs - 190.74;
    refField.style.display = 'block';
    document.getElementById('cc-lit').value = '190.74';
  } else if (method === 'custom') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    const lit = parseFloat(document.getElementById('cc-lit').value);
    state.ccShift = (isNaN(obs) || isNaN(lit)) ? 0 : obs - lit;
    refField.style.display = 'block';
    targetField.style.display = 'block';
  } else {
    state.ccShift = 0;
  }

  // Shift all energy-dependent values by the change in correction
  const delta = state.ccShift - prevShift;
  if (delta !== 0) {
    // ROI boundaries
    const roiMinEl = document.getElementById('roi-min');
    const roiMaxEl = document.getElementById('roi-max');
    const roiMinVal = parseFloat(roiMinEl.value);
    const roiMaxVal = parseFloat(roiMaxEl.value);
    if (!isNaN(roiMinVal)) roiMinEl.value = (roiMinVal - delta).toFixed(1);
    if (!isNaN(roiMaxVal)) roiMaxEl.value = (roiMaxVal - delta).toFixed(1);

    // Background endpoints
    const bgStartEl = document.getElementById('bg-start');
    const bgEndEl = document.getElementById('bg-end');
    const bgStartVal = parseFloat(bgStartEl.value);
    const bgEndVal = parseFloat(bgEndEl.value);
    if (!isNaN(bgStartVal)) bgStartEl.value = (bgStartVal - delta).toFixed(1);
    if (!isNaN(bgEndVal)) bgEndEl.value = (bgEndVal - delta).toFixed(1);

    // Peak centers
    for (const p of state.peaks) {
      p.center -= delta;
    }

    // Manual background anchors. Anchors are DATA-ATTACHED like peak
    // centers (x = a data point's corrected BE at placement time, y = that
    // point's intensity), so they follow the same -delta migration as the
    // ROI/bg fields and peak centers above — NOT the reference-marker
    // convention (literature markers stay at nominal corrected BE). y is
    // untouched: intensity is unaffected by charge correction. Saved files
    // need no migration — anchors persist alongside the tab's ccShift, so
  _patchPeakCardsForCentre(st);
  return st;
}

function maxROI() {
  if (!state.rawBE.length) return;
  const be = getCorrectedBE();
  const lo = _arrMin(be);
  const hi = _arrMax(be);
  document.getElementById('roi-min').value = lo.toFixed(1);
  document.getElementById('roi-max').value = hi.toFixed(1);
  document.getElementById('bg-start').value = hi.toFixed(1);
  document.getElementById('bg-end').value = lo.toFixed(1);
  updatePlot();
}

function autoSetROI() {
  if (!state.rawBE.length) return;
  const be = getCorrectedBE();
  const _roiLo = _arrMin(be), _roiHi = _arrMax(be);
  document.getElementById('roi-min').value = _roiLo.toFixed(1);
  document.getElementById('roi-max').value = _roiHi.toFixed(1);
  document.getElementById('bg-start').value = _roiHi.toFixed(1);
  document.getElementById('bg-end').value = _roiLo.toFixed(1);
  updatePlot();
}

// ═══════════════════════════════════════════════════
// PEAKS
// ═══════════════════════════════════════════════════
// Normalize charge-reference flags on a freshly-loaded peak list.
// Old saves do not have `isChargeReference` — default to false.
// If a save somehow has >1 true, keep the first and clear the rest.
function _normalizePeaksCRef(peaks) {
  if (!Array.isArray(peaks)) return peaks;
  let seen = false;
  return peaks.map(p => {
    const q = { ...p };

exec
/bin/zsh -lc "sed -n '520,580p' CLAUDE.md; sed -n '1,155p' tests/js/unsupported_components.test.js; rg -n 'json|upload|precision|float' parser.py | head -55" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
implemented: unit step (b), 2026-09-22, below.) The same file records that a
converged server fit is not ground truth: on a committed C 1s scan the
server's default method stopped in a local minimum the local engine
avoided.
See `docs/superpowers/plans/2026-09-18-local-engine-poisson-weighting.md`.

**"Not supported by the data" (unit step (b), 2026-09-22; owner decision
2026-09-18).** A component whose amplitude the fit drove to its floor,
pinned on a bound or fitted to numerical residue is an explicit OUTCOME —
the fit did not determine it — and its centre, width and σ are not reported
as if they were. The statement needs no intensity floor (six were tried for
the Auto-Fit anchor and each rejected real components or accepted residue):
with the other components held at their fitted values, removing this one
must make the fit significantly worse — `fitting._component_support`, the
Auto-Fit anchor's F statistic (F ≥ 10; `SUPPORT_MIN_F`). The SERVER computes
it once per component (`individual_peaks[].support = {f, delta_chi2,
supported}`; a linked component `follows` its parent); the page's twin
`_componentSupportFromResponse` recomputes it from any response carrying
`counts`, `fitted_y` and the component's curve; the LOCAL engine computes
the same statistic from its own residuals and weights
(`_componentSupportCore`), so a component driven to the zero floor by Batch
Fit is an outcome there too. Linked components follow their ROOT ancestor
whatever the request order. The verdict is a property of the fit that
produced it, CONDITIONAL on the other components as fitted, so it is bound
to that fit: `p.support.fitKey` is the model-plus-context key
(`_startsLiveKey()`) taken after the values are applied, and
`_isUnsupported(p)` compares it with the live key at every read — after
the student edits any peak, lock, link, the background, ROI, anchors or
charge correction, or an undo brings back other values, nothing is
suppressed or excluded until a new fit writes a new verdict (a verdict
without a key, from an older save, is never applied; exports write a
Status only from a CURRENT verdict — stale means "not established", never
"supported"). When the key changes, `_refreshStartsEvidence` compares the
set of flagged components with what EACH consumer has rendered — sidebar
badges, Results rows and chart datasets carry the peak id / flag — and
re-renders the ones that differ — the sidebar is PATCHED IN PLACE (header, summary values, area % over the currently supported components, badge), never re-rendered, because the student may be typing in a card (a caller that already redrew the sidebar,
such as Lock All or Add Peak, therefore still gets Results, Quantify and the
chart refreshed); it runs from the lock toggles, Lock All and every
`updatePlot` (which passes `fromPlot` so the chart is not rebuilt from
inside its own rebuild). Auto-Fit locks
every centre and refines the charge shift AFTER the result is applied, so
it re-stamps its verdicts (`_restampSupport`) — those changes are part of
its result. `p.support` is persisted with the peak (saves spread the peak
whole); Batch Fit's copy and a `.fit.json` import set it to `null`
(parameters on other data: nothing established); stack tabs judge a source
component against the SOURCE record's key. Sites
(`_isUnsupported`): sidebar card (badge; centre/width "—"; excluded from the
area total), Results table (greyed row, no centre/width/σ, area kept,
percentage "—", note beneath; percentages over supported components),
uncertainty panel (one rule-0 warning, before the per-parameter alarms and
instead of the neutral "locked" note Auto-Fit's centre lock would produce),
Quantify (no row; listed beneath: "an atomic percentage of 0.0 % would be a
measurement claim"), chart / stack / figure legend labels, no figure label at
the component's (zero) maximum, CSV/XLSX (Status column, empty cells, no
At%, WARNING line — and no width of any kind: DS+G β / m and LA m are widths
too), TSV (column kept, header says so), the scattered-starts table ("Your
fit" row shows neither area % nor a move for it, and it is never the
largest move; an alternative's components are unjudged and shown as they
are). Both engines' amplitude
floor is 0 (`runFitLocal`'s clamp was 1). Measured on the 202 committed
targets: 3 of 752 components (three C 1s re-fits, F 0.95–3.9), 0 of 95 fresh
// "Not supported by the data" (unit step (b), 2026-09-22). Owner decisions
// pinned here: a component the fit drove to its floor is an explicit outcome;
// its centre, width and sigma are not reported anywhere a result is shown,
// stored or exported; it is excluded from the Quantify body and listed beneath
// (0.0 % would be a measurement claim); a linked component follows its parent;
// a local-engine result or a propagated model establishes nothing.
//
// Functions are extracted verbatim from templates/index.html; the fixture is a
// REAL run_fit response (tests/js/fixtures/autofit_anchor.json) plus hand-built
// responses for the twin.

const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
const lines = html.split('\n');
function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name + '\\(');
  const start = lines.findIndex(l => re.test(l));
  assert.ok(start >= 0, `function ${name} not found`);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail('unbalanced ' + name);
}
const constLine = name => { const l = lines.find(x => x.startsWith('const ' + name)); assert.ok(l, name); return l; };
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');

const CORE = ['_componentSupportCore', '_componentSupportFromResponse', '_supportRootOf', '_applySupportVerdicts', '_applySupport', '_isUnsupported', '_currentSupport', '_restampSupport', '_unsupportedBadge'];
function core() {
  const src = [constLine('_SUPPORT_MIN_F'), constLine('_UNSUPPORTED_LABEL'), constLine('_UNSUPPORTED_TIP'), ...CORE.map(extractFn)].join('\n');
  return new Function('_escAttr', '_startsLiveKey', 'state', src + '\nreturn { ' + CORE.join(', ') + ' };')(esc, () => 'KEY', { peaks: [] });
}

const FIX = JSON.parse(fs.readFileSync(path.join(__dirname, 'fixtures/autofit_anchor.json'), 'utf8'));
const collapsed = FIX.find(f => /collapsed model/.test(f.name));
const resolved = FIX.find(f => /ordinary C 1s/.test(f.name));

test('the twin reproduces the server verdict on real responses, and defers to the server field when present', () => {
  const c = core();
  assert.strictEqual(c._componentSupportFromResponse(collapsed.json, '1').supported, false);
  assert.strictEqual(c._componentSupportFromResponse(resolved.json, '1').supported, true);
  assert.ok(c._componentSupportFromResponse(resolved.json, '1').f > 1000);
  const withField = { individual_peaks: [{ id: '1', support: { f: 2.0, delta_chi2: 1, supported: false } }] };
  assert.deepStrictEqual(c._componentSupportFromResponse(withField, 1), { f: 2.0, delta_chi2: 1, supported: false });
  assert.strictEqual(c._componentSupportFromResponse({ individual_peaks: [] }, 1), null, 'nothing to judge: not established');
  assert.strictEqual(c._componentSupportFromResponse({ counts: [1, 2], fitted_y: [1], individual_peaks: [{ id: '1', y: [1, 2] }] }, 1), null);
});

test('_applySupport writes every peak, follows ancestry to the root, stamps the fit key, and leaves null where the response says nothing', () => {
  const c = core();
  const peaks = [{ id: 1, name: 'root' }, { id: 2, name: 'child', linked: 1 }, { id: 3, name: 'grandchild', linked: 2 }, { id: 9, name: 'not in the response' }];
  c._applySupport(peaks, { individual_peaks: [
    { id: '1', support: { f: 0.5, delta_chi2: -3, supported: false } },
    { id: '2', support: { f: 99, delta_chi2: 9, supported: true } },       // the server resolves this too; the page uses the ROOT regardless of order
    { id: '3', support: { f: 99, delta_chi2: 9, supported: true } } ] }, 'KEY');
  assert.deepStrictEqual(peaks[0].support, { f: 0.5, delta_chi2: -3, supported: false, fitKey: 'KEY' });
  assert.deepStrictEqual(peaks[1].support, { f: 0.5, delta_chi2: -3, supported: false, fitKey: 'KEY', follows: 1 });
  assert.deepStrictEqual(peaks[2].support, { f: 0.5, delta_chi2: -3, supported: false, fitKey: 'KEY', follows: 1 });
  assert.strictEqual(peaks[3].support, null);
  assert.ok(c._isUnsupported(peaks[0]) && c._isUnsupported(peaks[2]) && !c._isUnsupported(peaks[3]));
  // a link cycle does not hang
  const cyc = [{ id: 1, linked: 2 }, { id: 2, linked: 1 }];
  c._applySupport(cyc, { individual_peaks: [{ id: '1', support: { f: 0, supported: false } }, { id: '2', support: { f: 0, supported: false } }] }, 'KEY');
  assert.ok(cyc[0].support && cyc[1].support);
});

test('the verdict applies only to the model and context it was computed for', () => {
  const c = core();
  const p = { id: 1, support: { f: 1, supported: false, fitKey: 'KEY' } };
  assert.strictEqual(c._isUnsupported(p), true);
  p.support.fitKey = 'ANOTHER MODEL';                      // the student edited something since the fit
  assert.strictEqual(c._isUnsupported(p), false, 'nothing is suppressed or excluded on a model the verdict does not describe');
  assert.strictEqual(c._isUnsupported({ id: 1, support: { f: 1, supported: false } }), false, 'a verdict without a key (older save) is not applied');
});

test('the local engine computes the same statistic from its own residuals', () => {
  const c = core();
  const counts = [1000, 1000, 1010, 1000, 1000], fitted = [1000, 1000, 1005, 1000, 1000], comp = [0, 0, 5, 0, 0];
  const w = counts.map(v => 1 / Math.sqrt(v));
  const mine = c._componentSupportCore(counts, fitted, comp, w, 3, 3);
  const twin = c._componentSupportFromResponse({ counts, fitted_y: fitted, statistics: { n_free_params: 3 },
    individual_peaks: [{ id: '1', y: comp, params: { a: { vary: true }, b: { vary: true }, c: { vary: true } } }] }, 1);
  assert.deepStrictEqual(mine, twin);
  assert.match(extractFn('runFitLocal'), /_applySupportVerdicts\(state\.peaks, id => verdicts\[String\(id\)\] \|\| null, _startsLiveKey\(\)\);/);
});

// ── sites ───────────────────────────────────────────────────────────────────
const PEAKS = () => [
  { id: 1, name: 'Graphite', color: '#112233', visible: true, shape: 'asym-GL', center: 284.40, fwhm: 0.64, amplitude: 86000, glMix: 16, asymmetry: 0.1, support: { f: 1e4, supported: true, fitKey: 'KEY' } },
  { id: 2, name: 'Unknown 2', color: '#445566', visible: true, shape: 'GL', center: 282.25, fwhm: 0.42, amplitude: 215, glMix: 0, support: { f: 2.01, delta_chi2: 1.2, supported: false, fitKey: 'KEY' } },
  { id: 3, name: 'sat', color: '#778899', visible: true, shape: 'GL', center: 291.10, fwhm: 3.5, amplitude: 2600, glMix: 59, support: { f: 500, supported: true, fitKey: 'KEY' } },
];
function pageEnv(fns, extraArgs = {}) {
  const dom = {}; const els = {};
  const el = id => (els[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, classList: { add() {}, remove() {}, contains() { return false; } },
    setAttribute() {}, querySelectorAll: () => [], querySelector: () => null, appendChild(n) { (this.children ||= []).push(n); }, _rsfSource: 'scofield' });
  const document = { getElementById: el, querySelectorAll: () => [], querySelector: () => null,
    createElement: () => ({ style: {}, classList: { add() {} }, addEventListener() {}, set innerHTML(v) { this._html = v; }, get innerHTML() { return this._html; } }) };
  const state = { peaks: PEAKS(), rawBE: [1, 2, 3], ccShift: 0, lineWidth: 1.5,
    fitResult: { be: [280, 285, 290], chiReduced: 2.1, rmse: 12.5, rFactor: null, backendResult: { individual_peaks: PEAKS().map(p => ({ id: String(p.id), params: {
      center: { value: p.center, stderr: 0.01, vary: true, min: null, max: null }, fwhm: { value: p.fwhm, stderr: 0.02, vary: true, min: 0.1, max: 15 },
      amplitude: { value: p.amplitude, stderr: 3, vary: true, min: 0, max: null } } })) } } };
  const names = [...CORE, ...fns];
  const src = [constLine('_SUPPORT_MIN_F'), constLine('_UNSUPPORTED_LABEL'), constLine('_UNSUPPORTED_TIP'), ...names.map(extractFn)].join('\n');
  const args = { _escAttr: esc, _escHtml: esc, document, state, getPeak: id => state.peaks.find(p => p.id === Number(id)),
    _startsLiveKey: () => 'KEY',
    _peakArea: p => p.amplitude * p.fwhm, getROIData: () => ({ be: [280, 285, 290] }), _buildStderrMap: fr => Object.fromEntries(fr.backendResult.individual_peaks.map(ip => [ip.id, ip.params])),
    _isLocalFit: () => false, _localFitCaveat: () => '', _localFitDetail: () => '', _startsPanelHtml: () => '', _validateUncertainties: () => ({ warnings: [], info: [] }),
    renderQuantify: () => {}, recalcQuantify: () => {}, _detectPeakRSF: () => ({ key: 'C 1s', rsf: 1 }), SCOFIELD_RSF: { 'C 1s': 1 }, notify: () => {},
    _clearDisallowedChargeRef: () => {}, _updateLocalModelBanner: () => {}, _updateLockAllBtn: () => {}, renderPeakForm: () => '', _highlightChartPeak: () => {},
    _roiWindowStatus: () => ({ state: 'ok', n: 0 }), _patchPeakCardsForCentre: () => {},   // the ROI / centre warnings: tests/js/roi_clamp_centre_warning.test.js
    _isChargeRefAllowed: () => false, _fitStatLabel: () => 'χ²ᵣ', _isUnweightedLocal: () => false, _applyStatCaption: () => {}, _applyStatDisplay: () => {},
    _CHISQ_TOOLTIP: '', _LOCALFIT_TOOLTIP: '', _startsSummaryText: () => '', _startsChosenText: () => '', _startsIfCurrent: () => null,
    _isLocalModel: () => false, _updateRFactorUI: () => {}, _activeTab: () => ({}), _renderRFactorPanel: () => '', _statIsChi: true,
    ...extraArgs };
  const api = new Function(...Object.keys(args), src + '\nreturn { ' + names.join(', ') + ' };')(...Object.values(args));
  return { ...api, state, els, document };
}

test('sidebar card: badge; centre and width shown as a dash; area % excluded and the others renormalised', () => {
  const env = pageEnv(['renderPeakList']);
  env.renderPeakList();
  const cards = env.els['peak-list'].children.map(c => c.innerHTML);
  assert.strictEqual(cards.length, 3);
  assert.match(cards[1], /unsupported-badge/);
  assert.match(cards[1], /<span class="peak-info">—<\/span>/);
  assert.doesNotMatch(cards[1], /282\.25|0\.42/);
  assert.match(cards[1], /peak-summary-val">—<\/span>\s*<span class="peak-summary-val">—<\/span>\s*<span class="peak-summary-val">—<\/span>/);
  assert.doesNotMatch(cards[0], /unsupported-badge/);
  const total = 86000 * 0.64 + 2600 * 3.5;                      // Unknown 2 excluded from the total
  assert.match(cards[0], new RegExp((86000 * 0.64 / total * 100).toFixed(1) + '%'));
});

test('results table: greyed row, no centre / width / sigma, area kept, percentage dash, and the note beneath', () => {
  const env = pageEnv(['renderResults', 'fmtVal'].filter(n => lines.some(l => new RegExp('^function ' + n + '\\(').test(l))));
  env.renderResults();
  const h = env.els['results-area'].innerHTML || Object.values(env.els).map(e => e.innerHTML).find(x => /unsupported-row/.test(x));
  assert.ok(h, 'results html');
  const row = h.slice(h.indexOf('unsupported-row'), h.indexOf('</tr>', h.indexOf('unsupported-row')));
  assert.match(row, /Unknown 2/);
  assert.doesNotMatch(row, /282\.25|0\.42|±/);
  assert.match(row, /<td>90<\/td>/);                          // its area (215 * 0.42) is shown, not hidden
  assert.match(row, /<td>&mdash;<\/td>\s*$/);
  assert.match(h, /One component is <b>not supported by the data<\/b> \(Unknown 2\)/);
  assert.match(h, /excluded from the percentages and from Quantify/);
  const gRow = h.slice(h.indexOf('Graphite'), h.indexOf('</tr>', h.indexOf('Graphite')));
  assert.match(gRow, new RegExp((86000 * 0.64 / (86000 * 0.64 + 2600 * 3.5) * 100).toFixed(1) + '%'), 'percentages over supported area only');
});

test('uncertainty panel: one rule-0 warning for the component, no per-parameter alarms and no "locked" note for it', () => {
67:        return np.asarray(be, dtype=float), np.asarray(inten, dtype=float)
157:    energy = df[numeric_cols[0]].to_numpy(dtype=float)
158:    counts = df[numeric_cols[1]].to_numpy(dtype=float)
209:            energy = df[numeric_cols[0]].to_numpy(dtype=float)
210:            counts = df[numeric_cols[1]].to_numpy(dtype=float)
249:    1. Mixed ASCII+binary: look for text header, parse calibration, read float32 payload.
252:       plausible float32 values (all positive, < 1e9).
275:    # ── Strategy 3: brute‑force float32 block ────────────────────────────────
287:    """Try to decode a text header + binary float32 payload."""
315:    start_e = float(m_start.group(1)) if m_start else None
316:    end_e = float(m_end.group(1)) if m_end else None
317:    step_e = float(m_step.group(1)) if m_step else None
331:    floats = _read_float32_block(data, bin_start, n_pts)
332:    if floats is None:
340:    return energy, floats
350:      offset 16  : float64 start_ke  (KE in eV)
351:      offset 24  : float64 step_ke   (step in eV)
352:      offset 512 : float32[n_points] intensity
356:      offset 8   : float64 start_ke
357:      offset 16  : float64 step_ke
358:      offset 256 : float32[n_points]
377:            floats = _read_float32_block(data, header_size, n_pts)
378:            if floats is None:
383:            return energy, floats
392:    Last‑resort: treat the entire file as float32 and find the longest run of
400:        n_floats = len(data) // 4
401:        if n_floats < 10:
403:        all_floats = np.frombuffer(data, dtype="<f4", count=n_floats).astype(float)
408:    plausible = np.isfinite(all_floats) & (all_floats >= 0) & (all_floats < 1e9)
427:    counts = all_floats[best_start: best_start + best_len]
428:    energy = np.arange(best_len, dtype=float)  # placeholder index axis
469:def _read_float32_block(
475:    """Read n little‑endian float32 values starting at offset; return None on failure."""
480:        arr = np.frombuffer(data, dtype=f"{endian}f4", count=n, offset=offset).astype(float)
486:            arr = np.frombuffer(data, dtype=">f4", count=n, offset=offset).astype(float)

exec
/bin/zsh -lc "ls -d venv .venv /Users/skyefortier/xps-app/venv /Users/skyefortier/xps-app/.venv 2>/dev/null; rg -n 'jitter|last.digit' tests docs/superpowers/plans/2026-09-2* | head -55" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
/Users/skyefortier/xps-app/venv
docs/superpowers/plans/2026-09-21-scattered-starts-and-unsupported-components.md:91:  one in §2, anchored to the REQUEST's start (not the jittering fitted
docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md:101:identical seed; the variation is Trust-Region's documented last-digit
docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md:102:jitter. It reached the assertion because the construction did not
tests/test_component_required.py:66:    # Trust-Region's documented last-digit jitter (identical seed in every
tests/test_tougaard_background.py:221:    x_jitter = x.copy()
tests/test_tougaard_background.py:222:    x_jitter[1:-1] += 1e-4 * np.sin(np.arange(len(x) - 2))
tests/test_tougaard_background.py:223:    bg_nonuniform = tougaard_background(x_jitter, y)
tests/test_fit_reproducibility.py:16:perturbed restarts start from that jittering solution, and on a model with
tests/test_fit_reproducibility.py:102:    # The first Trust-Region solution jitters at ~1e-5 from press to press

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -m pytest -p no:cacheprovider --capture=sys -q tests/test_component_required.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
exec
/bin/zsh -lc "sed -n '15160,15250p' templates/index.html; rg -n 'function uploadToBackend' templates/index.html; sed -n '7640,7710p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:

async function openFindPeaksModal() {
  if (!state.rawBE || !state.rawBE.length) {
    notify('Load a spectrum first — Find Peaks runs on the active tab.', 'amber');
    return;
  }
  try {
    if (!_fpMeta) {
      const r = await fetch('/api/analyze/meta');
      _fpMeta = await r.json();
    }
  } catch (e) {
    notify('Find Peaks backend unavailable: ' + e.message, 'amber');
    return;
  }
  // all wording from FP_STRINGS; server strings escaped even though
  // currently code-controlled (a future registered label must never
  // become an injection point)
  document.getElementById('fp-blurb').innerHTML = FP_STRINGS.blurb;
  document.getElementById('fp-apply-note').textContent = FP_STRINGS.applyNote;
  _fpMaybeShowExperimentalNotice();
  document.getElementById('fp-material-label').title = FP_STRINGS.tips.material;
  document.getElementById('fp-method-label').title = FP_STRINGS.tips.method;
  document.getElementById('fp-regions-label').title = FP_STRINGS.tips.regions;
  const mat = document.getElementById('fp-material');
  mat.innerHTML = _fpMeta.material_classes
    .map(m => {
      const s = FP_STRINGS.materials[m] || {};
      const title = s.hint ? ` title="${_fpEsc(s.hint)}"` : '';
      return `<option value="${_fpEsc(m)}"${title}>${_fpEsc(s.label || m)}</option>`;
    }).join('');
  _fpMaterialChanged();
  document.getElementById('fp-regions-filter').value = '';
  _fpRegionsSelected = new Set();
  _fpExpandedElement = null;
  _fpRenderLegend();
  _fpRenderPtGrid('');
  _fpRenderSearchDropdown('');
  _fpRenderExpandedPanel();
  document.getElementById('fp-regions-tier-note').textContent = '';
  const meth = document.getElementById('fp-method');
  meth.innerHTML = _fpMeta.methods
    .map(m => {
      const s = FP_STRINGS.methods[m.id] || {};
      // hovering an option (even before selecting it) shows the SAME
      // plain-English explanation as the hint box below the dropdown —
      // no jargon, and no need to select first just to learn what an
      // option does. Previously showed the raw backend label here
      // (e.g. "Auto — model comparison (IC)"), which read as vague/
      // jargon-y "the tooltip" per the 2026-07-14 bug report.
      return `<option value="${_fpEsc(m.id)}" title="${_fpEsc(s.hint || s.label || m.label || m.id)}">${_fpEsc(s.label || m.label || m.id)}</option>`;
    }).join('');
  meth.value = 'ic_model_comparison';
  _fpMethodChanged();
  document.getElementById('fp-results').style.display = 'none';
  document.getElementById('fp-status').textContent = '';
  // A result stored on THIS tab (its own run, possibly finished while another
  // tab was active) is shown again so it can be applied here.
  const stored = _fpGetLast();
  if (stored && stored.body) {
    _fpRenderResults(stored.body);
    document.getElementById('fp-status').textContent =
      'Showing this tab\u2019s last Find Peaks result (' + (stored.method || '?') + ', regions ' +
      ((stored.regions || []).join(', ') || '?') + ', endpoint averaging ' + (stored.endpointAvg || '?') +
      ') \u2014 apply only if the ROI and peaks are still what that run used.';
  }
  _fpResetModalPosition();
  document.getElementById('find-peaks-overlay').classList.add('open');
}

function closeFindPeaksModal() {
  document.getElementById('find-peaks-overlay').classList.remove('open');
}

// ── Draggable modal (2026-07-11) ────────────────────────────────────────
// Same technique as the Reference palette's _refPaletteDragStart/Move/End
// (static/js/ref_identify_core.js RefCore.clampToViewport is the shared,
// tested clamp math) — but scoped to ONLY the Find Peaks modal: every
// other .xps-modal in the app stays centered/non-draggable.

let _fpModalDrag = null;

// True for the close button (or any future control placed in the header)
// — those must still work; only the bare header background starts a drag.
// (`instanceof Element` guard: a text-node event target lacks .closest —
// see CLAUDE.md Known Issues re: the same class of bug elsewhere.)
function _fpIsDragBlockingTarget(target) {
  return !!(target instanceof Element && target.closest('button, select, input, a, textarea'));
}

function _fpClampModal(left, top) {
6396:async function uploadToBackend(be, inten) {
function _dropStaleAltPreview() {
  if (_historyPreview && typeof _historyPreview.snapId === 'string' && _historyPreview.snapId.startsWith('alt:') &&
      !(state.fitResult && _historyPreview.altKey === state.fitResult.startsModelKey && _startsIfCurrent(state.fitResult, _startsLiveKey()))) {
    _historyPreview = null;
  }
}

// What is persisted with a saved fit: the counts, never the alternatives'
// parameter sets (regenerable: the starts are a pure function of the request).
function _startsForSave(st) {
  if (!st) return null;
  if (!st.ran) return { ran: false, reason: st.reason || null };
  const alts = st.alternatives || [];
  return { ran: true, n_run: st.n_run, n_converged: st.n_converged, n_same_as_fit: st.n_same_as_fit,
           n_not_better_elsewhere: st.n_not_better_elsewhere,
           n_in_alternatives: st.n_in_alternatives ?? alts.reduce((n, a) => n + a.n_starts, 0),
           n_alternatives: alts.length || st.n_alternatives || 0,
           best_alternative_chi2r: alts.length ? alts[0].chi2r : (st.best_alternative_chi2r ?? null) };
}

// Counts STARTS and SOLUTIONS separately: three starts reaching one different
// solution is "3 starts found a DIFFERENT solution", not "one start".
function _startsSummaryText(st) {
  if (!st || !st.ran) return '';
  const nSol = (st.alternatives ? st.alternatives.length : st.n_alternatives) || 0;
  const nIn = st.n_in_alternatives ?? (st.alternatives || []).reduce((n, a) => n + a.n_starts, 0);
  const nb = st.n_not_better_elsewhere || 0, failed = st.n_run - st.n_converged;
  let t = `${st.n_same_as_fit} of ${st.n_run} scattered starts reached this solution`;
  const parts = [];
  if (nSol) parts.push(`${nIn} found ${nSol === 1 ? 'a DIFFERENT solution' : nSol + ' DIFFERENT solutions'} with a lower χ²ᵣ`);
  if (nb) {
    const worst = (st.not_better_chi2r && st.not_better_chi2r.length) ? ` (χ²ᵣ ${st.not_better_chi2r.map(c => c.toFixed(2)).join(', ')})` : '';
    parts.push(`${nb} ended in a solution that is not better${worst}`);
  }
  if (failed > 0) parts.push(`${failed} did not converge`);
  if (parts.length) t += '; ' + parts.join('; ');
  return t + '.' + (nSol ? ' Your fit is unchanged.' : '');
}

// The recorded adoption, for the panel and the exports (only beside current evidence).
function _startsChosenText(fr) {
  const c = fr && fr.chosenAlternative;
  if (!c || !_startsIfCurrent(fr, _startsLiveKey())) return '';
  return `this fit started from a solution chosen from the scattered starts (\u03c7\u00b2\u1d63 ${Number(c.fromChi).toFixed(2)} \u2192 ${Number(c.toChi).toFixed(2)}; largest move from the original start: ${c.shiftName} ${_startsEv(c.shiftEv)})`;
}

function _startsPeakName(id) { const p = getPeak(Number(id)) || getPeak(id); return p ? p.name : String(id); }

function _startsShiftColour(ev) {
  const mag = Math.abs(ev);
  return mag > _STARTS_SHIFT_RED_EV ? 'var(--red,#ef4444)' : mag > _STARTS_SHIFT_AMBER_EV ? 'var(--amber,#f59e0b)' : 'var(--text2)';
}
function _startsEv(ev) { return (ev >= 0 ? '+' : '−') + Math.abs(ev).toFixed(2) + ' eV'; }

function _startsShiftHtml(shift) {
  const bold = Math.abs(shift.ev) > _STARTS_SHIFT_AMBER_EV ? 600 : 400;
  return `<span style="color:${_startsShiftColour(shift.ev)};font-weight:${bold}">${_escHtml(_startsPeakName(shift.id))} ${_startsEv(shift.ev)}</span>`;
}

function _startsPanelHtml(fr) {
  if (!fr || !fr.starts || !fr.starts.ran) return '';
  const st = _startsIfCurrent(fr, _startsLiveKey());
  if (!st) {
    return `<div class="starts-panel" style="margin-top:10px;font-size:11px;line-height:1.5;color:var(--text3)">&#8635; The model has changed since this fit, so its scattered-starts comparison no longer applies. Run the fit again to compare starts.</div>`;
  }
  let html = `<div class="starts-panel" style="margin-top:10px;font-size:11px;line-height:1.5">
    <div data-xps-tip="${_escHtml(_STARTS_TOOLTIP)}" style="color:var(--text2)">&#8635; ${_escHtml(_startsSummaryText(st))}</div>`;
  if (fr.chosenAlternative) {
    const c = fr.chosenAlternative;
    html += `<div style="color:var(--text3);margin-top:2px">This fit started from a solution you chose from the scattered starts (χ²ᵣ ${Number(c.fromChi).toFixed(2)} → ${Number(c.toChi).toFixed(2)}; largest move from your original start: ${_escHtml(c.shiftName)} ${_startsEv(c.shiftEv)}).</div>`;
  }

exec
/bin/zsh -lc "sed -n '13890,14030p' templates/index.html; rg -n 'center\\s*=|center:|\\.center' templates/index.html | tail -65; sed -n '1,135p' tests/test_fit_reproducibility.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
    panel.style.right = '';
    panel.classList.add('open');
  }
}

function _closeHistoryPanel() {
  document.getElementById('history-panel').classList.remove('open');
}

function _renderHistoryList() {
  const tab = tabManager && tabManager.activeId ? tabManager._getTab(tabManager.activeId) : null;
  const snaps = tab && tab.snapshots && tab.snapshots.length ? tab.snapshots : [];
  const list = document.getElementById('history-list');
  const info = document.getElementById('history-compare-info');

  if (!tab) {
    list.innerHTML = '<div style="font-size:11px;color:var(--text3);padding:12px 8px;font-family:var(--mono)">Load a spectrum and run a fit to start recording history.</div>';
    info.textContent = '';
    return;
  }

  if (!snaps.length) {
    list.innerHTML = '<div style="font-size:11px;color:var(--text3);padding:12px 8px;font-family:var(--mono)">No snapshots yet. Snapshots are saved automatically after each fit.</div>';
    info.textContent = '';
    return;
  }

  info.textContent = `${snaps.length} snapshot${snaps.length !== 1 ? 's' : ''} for "${tab.name}"`;

  list.innerHTML = snaps.map(s => `
    <div class="hist-row" id="hist-row-${s.id}">
      <div class="hist-row-main">
        <div class="hist-row-label">${_escHtml(s.label)}</div>
        <div class="hist-row-meta">${s.timestamp} &middot; ${(s.peaks || []).length} peak${(s.peaks || []).length !== 1 ? 's' : ''}${typeof s.chi === 'number' && isFinite(s.chi) ? ' &middot; <span class="hist-row-chi">' + _escHtml(_fitStatLabel(s.fitResult)) + ' = ' + s.chi.toFixed(3) + (_isLocalFit(s.fitResult) ? ' (starting point)' : '') + '</span>' : ''}${typeof s.rFactor === 'number' && isFinite(s.rFactor) ? ', R = ' + s.rFactor.toFixed(1) + '%' : ''}</div>
      </div>
      <div class="hist-row-btns">
        <button class="btn btn-sm" onclick="_historyPreviewSnap(${s.id})" title="Overlay this snapshot on the chart">Preview</button>
        <button class="btn btn-sm btn-accent" onclick="_historyRestoreSnap(${s.id})" title="Restore this snapshot">Restore</button>
        <button class="btn btn-sm" onclick="_historyDeleteSnap(${s.id})" title="Delete this snapshot" style="color:var(--red,#f87171)">&#x2715;</button>
      </div>
    </div>`).join('');
}

function _escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// Attribute-context escape (audit F4). Superset of _escHtml that also
// neutralises the single quote, for values interpolated INSIDE an HTML
// attribute value where escaping for text nodes is insufficient.
function _escAttr(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
                  .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

// ── Load-boundary input validation (audit F1–F5) ──────────────────────
// User-controlled strings from loaded project/spectrum/fit files reach
// innerHTML and onclick=/oninput= JS attributes. Names are escaped at the
// render boundary; ids and colors cannot be safely escaped in a JS-attribute
// context, so they are validated here against the app's own invariants and
// the file is REJECTED on violation (never coerced — ids are references).
const _HEX_COLOR_RE = /^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$/;
const _SLUG_ID_RE   = /^[A-Za-z0-9_-]{1,64}$/;

// Returns an error string if peak `p` carries an unsafe id/link/color,
// else null. Does NOT mutate the peak — a numeric id stays numeric so
// downstream === comparisons and object-key lookups are unaffected.
function _peakLoadError(p) {
  if (!p || typeof p !== 'object') return null;
  if (!/^\d+$/.test(String(p.id)))
    return 'peak id ' + JSON.stringify(p.id) + ' is not a non-negative integer';
  if (p.linked != null && p.linked !== false && !/^\d+$/.test(String(p.linked)))
    return 'peak link target ' + JSON.stringify(p.linked) + ' is not a valid peak id';
  if (p.color != null && p.color !== '' &&
      (typeof p.color !== 'string' || !_HEX_COLOR_RE.test(p.color)))
    return 'peak color ' + JSON.stringify(p.color) + ' is not a valid hex color';
  return null;
}

// Returns an error string for the first unsafe peak in `peaks`, else null.
function _peaksLoadError(peaks) {
  if (!Array.isArray(peaks)) return null;
  for (const p of peaks) { const e = _peakLoadError(p); if (e) return e; }
  return null;
}

function _historyPreviewSnap(snapId) {
  const tab = tabManager._getTab(tabManager.activeId);
  if (!tab || !tab.snapshots) return;
  const snap = tab.snapshots.find(s => s.id === snapId);
  if (!snap) return;

  if (_historyPreview && _historyPreview.snapId === snapId) {
    _historyClearPreview();
    return;
  }

  if (!snap.peaks || !snap.peaks.length) {
    notify('Preview not available for this snapshot.', 'amber');
    return;
  }

  _historyPreview = { snapId, peaks: snap.peaks, fitResult: snap.fitResult };
  _updateLocalModelBanner();
  document.querySelectorAll('.hist-row').forEach(r => r.classList.remove('hist-preview-active'));
  const row = document.getElementById('hist-row-' + snapId);
  if (row) row.classList.add('hist-preview-active');
  updatePlot();
}

function _historyClearPreview() {
  _historyPreview = null;
  _updateLocalModelBanner();
  document.querySelectorAll('.hist-row').forEach(r => r.classList.remove('hist-preview-active'));
  updatePlot();
}

function _historyRestoreSnap(snapId) {
  const tab = tabManager._getTab(tabManager.activeId);
  if (!tab || !tab.snapshots) return;
  const snap = tab.snapshots.find(s => s.id === snapId);
  if (!snap) return;

  pushUndo();
  state.peaks = _normalizePeaksCRef(JSON.parse(JSON.stringify(snap.peaks)));
  state.fitResult = snap.fitResult ? { ...snap.fitResult } : null;
  tab.modelProvenance = null;   // the restored result governs the designation (unit A0)
  tabManager._syncActiveToRecord();

  _historyClearPreview();
  renderPeakList();
  updatePlot();
  renderResults();
  _closeHistoryPanel();
  notify('Snapshot restored.', 'green');
}

function _historyDeleteSnap(snapId) {
  const tab = tabManager._getTab(tabManager.activeId);
  if (!tab || !tab.snapshots) return;
  tab.snapshots = tab.snapshots.filter(s => s.id !== snapId);
3019:    const center = (beMax + beMin) / 2;
4127:  const center = p.center;
4352:    const yArr = laTrueCasaXPS_array(beArr, p.center, p.fwhm, p.caAlpha, p.caBeta, p.caM);
4362:    const yArr = dsgConvolved_array(beArr, p.center, p.laAlpha, p.laBeta, p.laM || 0);
5011:      p.center -= delta;
5131:  return !!(st && st.n > 0 && Number.isFinite(p.center) && (p.center < st.sMin || p.center > st.sMax));
5134:  const tip = `Centre ${p.center.toFixed(2)} eV lies outside the fitted data (${st.sMin.toFixed(2)}–${st.sMax.toFixed(2)} eV). `
5234:    center: 710,
5784:      center: Math.round(beValue * 100) / 100,
5810:      center: Math.round(beValue * 100) / 100,
5815:      center: Math.round((beValue + preset.splitting) * 100) / 100,
5896:  const p1 = addPeak({ name: 'Peak ' + state.nextId + ' (\u2087/\u2082)', center: 380 });
5899:    center: p1.center + 10.9,
5982:      if (key === 'center') parent.center = p.center - p.linkOffset;
5996:      if (key === 'center') child.center = parent.center + child.linkOffset;
6127:        <span class="peak-info">${unsupported ? dash : p.center.toFixed(2) + ' eV'}</span>
6134:        <span class="peak-summary-val">${unsupported ? dash : p.center.toFixed(2)}</span>
6191:        <input type="number" id="pk-center-${p.id}" value="${p.center.toFixed(3)}" step="0.05"
6221:          oninput="getPeak(${p.id}).linkOffset=parseFloat(this.value);getPeak(${p.id}).center=getPeak(${p.linked}).center+parseFloat(this.value);updatePeakParam(${p.id},'center',getPeak(${p.id}).center)">
6421:    center: p.center,
6425:    fix_center: !!p.fixCenter,
6505:  if (par.center    && !p.fixCenter)    p.center    = par.center.value;
6842:    center: 284.50,
6859:    { name: 'Adventitious 1', center: 284.80, fwhm: 1.4 },
6860:    { name: 'Adventitious 2', center: 286.20, fwhm: 1.6 },
6861:    { name: 'Adventitious 3', center: 287.80, fwhm: 1.8 },
6862:    { name: 'π→π* satellite', center: 291.00, fwhm: 2.5 },
6868:      center: a.center,
6886:      center: c1,
6902:      center: c2,
6933:    peaks[i]._afCenterMin = peaks[i].center - 0.80;
6934:    peaks[i]._afCenterMax = peaks[i].center + 0.80;
7218:    if (info) info.textContent = un ? dash : p.center.toFixed(2) + ' eV';
7220:    if (vals[0]) vals[0].textContent = un ? dash : p.center.toFixed(2);
7260:  if (!gPeak || !Number.isFinite(gPeak.center)) {
7284:  if (Math.abs(gPeak.center - 284.50) > 0.30 + 1e-6) {
7290:  const graphiteFittedRaw = gPeak.center + (Number.isFinite(state.ccShift) ? state.ccShift : 0);
7465:      if (Number.isFinite(p._afCenterMin)) spec.center_min = p._afCenterMin;
7466:      if (Number.isFinite(p._afCenterMax)) spec.center_max = p._afCenterMax;
7722:    return `<td style="text-align:right;padding:2px 4px;font-family:var(--mono)">${(c.area_percent * scale).toFixed(1)}<br><span style="color:${_startsShiftColour(c.center_shift_from_start)}">${_startsEv(c.center_shift_from_start)}</span></td>`;
7727:    return eligible.length ? eligible.reduce((m, c) => Math.abs(c.center_shift_from_start) > Math.abs(m.center_shift_from_start) ? c : m) : null;
7737:      <td style="padding:2px 4px">${big ? _startsShiftHtml({ id: big.id, ev: big.center_shift_from_start }) : '&mdash;'}</td><td style="padding:2px 4px;white-space:nowrap">${actions}</td></tr>`; };
7934:      _preFit[p.id] = { center: p.center, fwhm: p.fwhm, amplitude: p.amplitude, glMix: p.glMix };
8162:      if (!p.fixCenter)    { freeParams.push(p.center);    paramMap.push({id: p.id, param: 'center'}); }
8227:      if (Number.isFinite(q.linkOffset)) q.center = parent.center + q.linkOffset;
8615:    const centerSE = par.center ? par.center.stderr : null;
8631:      <td style="font-family:var(--mono)">${fmtVal(p.center, centerSE, 3)} eV</td>
8680:  const center = p.center;
11323:    const cse  = par.center?.stderr  ?? '';
11334:      p.name, (_currentSupport(p) && _currentSupport(p).supported) ? 'supported' : '', p.center.toFixed(4), cse !== '' ? Number(cse).toFixed(5) : '',
11537:  const nameMap = { center: 'center', fwhm: 'fwhm', fwhm_l: 'fwhm', amplitude: 'amplitude', gl_ratio: 'glMix' };
15002:                   fwhm_excess: 'extra width', center: 'position',
15105:    const centers = unassignedPeaks.map(p => (+p.center).toFixed(2)).join(', ');
15847:      const sc = conf.sigma_stat && conf.sigma_stat.values && conf.sigma_stat.values.center;
15850:        `<td style="${td}">${(+p.center).toFixed(3)}</td><td style="${td}">${p.fwhm != null ? (+p.fwhm).toFixed(3) : '—'}</td>` +
15887:  const o = { name: p.role || ('found ' + (i + 1)), center: p.center,
"""An identical fit request must give an identical answer.

Measured 2026-09-19 (docs/findings/2026-09-fit-determinacy.md): the page sends
``n_perturb: 3`` and the server perturbed from an UNSEEDED generator, so five
presses of Run Fit on one committed C 1s scan gave reduced chi-square 70.6,
18.5, 70.6, 38.3, 18.5. A saved project could not regenerate its own figure.
Every random draw in ``run_fit`` is now derived from the request itself.

What that does and does not buy (measured while writing these tests):
Levenberg-Marquardt (MINPACK) and Nelder-Mead are then BYTE-identical from
press to press. Trust-Region (scipy ``least_squares``, the page's default) is
not and cannot be made so by seeding: the BLAS dot product (Apple
Accelerate on the production machine) rounds differently (one unit in the last place) depending on where its argument
sits in memory, and scipy's trust-region iteration amplifies that to ~1e-4
relative in component areas at its stopping tolerance of 1e-8. Worse, the
perturbed restarts start from that jittering solution, and on a model with
several minima a 1e-5 difference in a start can send a restart into another
basin: on the five-component model below two presses of the SEEDED request
differed by 29 percentage points (on the lab's 202 committed targets that
happened once, by 0.30). So for Trust-Region these tests pin what is exactly
true — the seed and the draws — and deliberately assert nothing about the
result; for Levenberg-Marquardt and Nelder-Mead they assert byte identity.
"""

import io
import json

import numpy as np
import pytest

import fitting
from app import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app(upload_folder=str(tmp_path))
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _crowded_c1s(seed=11):
    """Five overlapping components: a model with several minima, where the
    perturbation decides which one is returned."""
    rng = np.random.default_rng(seed)
    x = np.arange(280.0, 296.0, 0.1)

    def g(c, a, w):
        return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)

    y = rng.poisson(400.0 + g(284.4, 9000, 0.7) + g(284.9, 2500, 1.6) + g(286.3, 900, 1.4)
                    + g(288.0, 500, 2.2) + g(291.0, 450, 3.0)).astype(float)
    specs = [
        {"id": 1, "shape": "asymmetric_gl", "center": 284.4, "amplitude": 8000.0, "fwhm": 0.8,
         "gl_ratio": 0.2, "asymmetry": 0.1, "asymmetry_min": 0.1, "asymmetry_max": 0.5, "amplitude_min": 0},
        {"id": 2, "shape": "pseudo_voigt_gl", "center": 284.8, "amplitude": 2000.0, "fwhm": 1.9, "gl_ratio": 0.0, "amplitude_min": 0},
        {"id": 3, "shape": "pseudo_voigt_gl", "center": 286.4, "amplitude": 700.0, "fwhm": 1.4, "gl_ratio": 0.0, "amplitude_min": 0},
        {"id": 4, "shape": "pseudo_voigt_gl", "center": 287.3, "amplitude": 600.0, "fwhm": 3.5, "gl_ratio": 0.0, "amplitude_min": 0},
        {"id": 5, "shape": "pseudo_voigt_gl", "center": 291.1, "amplitude": 500.0, "fwhm": 3.4, "gl_ratio": 0.5, "amplitude_min": 0},
    ]
    return x, y, specs


def _dump(result):
    return json.dumps(result, sort_keys=True)


def _spy_on_fits(monkeypatch):
    records = []
    real_fit = fitting.Model.fit

    def spy(self, data, params, **kw):
        rec = {"start": {n: p.value for n, p in params.items()},
               "bounds": {n: (p.min, p.max) for n, p in params.items()},
               "method": kw.get("method"), "seed": (kw.get("fit_kws") or {}).get("seed")}
        records[-1].append(rec)
        res = real_fit(self, data, params, **kw)
        rec["end"] = {n: p.value for n, p in res.params.items()}
        rec["vary"] = {n: bool(p.vary) and p.expr is None for n, p in res.params.items()}
        return res

    monkeypatch.setattr(fitting.Model, "fit", spy)
    return records


def test_perturbed_starts_are_byte_identical_with_a_deterministic_method(monkeypatch):
    # Levenberg-Marquardt has no alignment-dependent arithmetic, so identical
    # draws show up as byte-identical perturbed starting points.
    records = _spy_on_fits(monkeypatch)
    x, y, specs = _crowded_c1s()
    for _ in range(3):
        records.append([])
        fitting.run_fit(x, y, specs, background_method="shirley", n_perturb=3, fit_kws={"method": "leastsq"})
    starts = [[tuple(sorted(r["start"].items())) for r in run] for run in records]
    assert len(starts[0]) == 4                       # the first fit + three perturbed refits
    assert len(set(starts[0][1:])) == 3              # the three perturbations differ from each other
    assert starts[0] == starts[1] == starts[2]


def test_trust_region_perturbation_draws_are_exactly_identical(monkeypatch):
    # The first Trust-Region solution jitters at ~1e-5 from press to press
    # (see the module docstring), so the perturbed STARTS differ by that much.
    # The DRAWS must not: draw = perturbed start / the solution it perturbed,
    # both taken from the same press, for every parameter the clip left alone.
    records = _spy_on_fits(monkeypatch)
    x, y, specs = _crowded_c1s()
    for _ in range(2):
        records.append([])
        fitting.run_fit(x, y, specs, background_method="shirley", n_perturb=3, fit_kws={"method": "least_squares"})

    def draws(run):
        best, out = run[0]["end"], []
        for k in (1, 2, 3):
            row = {}
            for name, start in run[k]["start"].items():
                lo, hi = run[k]["bounds"][name]
                if run[0]["vary"][name] and best[name] != 0 and lo < start < hi:
                    row[name] = start / best[name]
            out.append(row)
            if run[k].get("end") and fitting_would_adopt(run, k):
                best = run[k]["end"]
        return out

    def fitting_would_adopt(run, k):            # the loop perturbs the FIRST result every time
        return False

    d0, d1 = draws(records[0]), draws(records[1])
    compared = 0
    for a, b in zip(d0, d1):
        for name in set(a) & set(b):
            assert a[name] == pytest.approx(b[name], rel=1e-12), name
            assert 0.85 <= a[name] <= 1.15
            compared += 1
    assert compared >= 20

exec
/bin/zsh -lc 'git status --short; node --test tests/js/*.test.js | tail -12' in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 exited 2 in 1887ms:

==================================== ERRORS ====================================
______________ ERROR collecting tests/test_component_required.py _______________
tests/test_component_required.py:15: in <module>
    import fitting
fitting.py:33: in <module>
    from lmfit import Model, Parameters
../../../venv/lib/python3.12/site-packages/lmfit/__init__.py:38: in <module>
    from .confidence import conf_interval, conf_interval2d
../../../venv/lib/python3.12/site-packages/lmfit/confidence.py:10: in <module>
    from .minimizer import MinimizerException
../../../venv/lib/python3.12/site-packages/lmfit/minimizer.py:41: in <module>
    from .parameter import Parameter, Parameters
../../../venv/lib/python3.12/site-packages/lmfit/parameter.py:14: in <module>
    from .jsonutils import decode4js, encode4js
../../../venv/lib/python3.12/site-packages/lmfit/jsonutils.py:8: in <module>
    import dill
../../../venv/lib/python3.12/site-packages/dill/__init__.py:33: in <module>
    from .session import (
../../../venv/lib/python3.12/site-packages/dill/session.py:25: in <module>
    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                               ^^^^^^^^^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:315: in gettempdir
    return _os.fsdecode(_gettempdir())
                        ^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:308: in _gettempdir
    tempdir = _get_default_tempdir()
              ^^^^^^^^^^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:223: in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
E   FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
=========================== short test summary info ============================
ERROR tests/test_component_required.py - FileNotFoundError: [Errno 2] No usab...
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 1.56s

exec
/bin/zsh -lc "sed -n '6385,6420p' templates/index.html; rg -n 'upload.*json|energy.*body|body.*energy|request.get_json' app.py | head -40; sed -n '7830,7865p' templates/index.html; rg -n 'required|support.*f|\\[.f.\\].*(10|1e)|SUPPORT_MIN_F' tests/test*py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
    if (ds._peakId === peakId) {
      ds.borderWidth = highlight ? 3 : 1.5;
    }
  }
  state.chart.update('none');
}

// ═══════════════════════════════════════════════════
// ═══════════════════════════════════════════════════
// FLASK BACKEND HELPERS
// ═══════════════════════════════════════════════════
async function uploadToBackend(be, inten) {
  const csv = be.map((e, i) => e.toFixed(4) + ',' + inten[i].toFixed(2)).join('\n');
  const form = new FormData();
  form.append('file', new Blob([csv], { type: 'text/plain' }), 'spectrum.csv');
  const resp = await fetch('/api/upload', { method: 'POST', body: form });
  // A server-side failure (HTTP error, error body, or no session id) is not a
  // transport failure: runFit must report it, never switch engines (unit A0).
  const serverError = (msg) => { const err = new Error(msg); err.serverError = true; return err; };
  if (resp.ok === false) {
    let msg = null;
    try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
    throw serverError(msg || ('Upload failed (HTTP ' + resp.status + ').'));
  }
  const json = await resp.json();
  if (!json || typeof json !== 'object') throw serverError('Upload returned an unexpected response.');
  if (json.error) throw serverError(json.error);
  if (!json.session_id) throw serverError('Upload returned no session id.');
  return json.session_id;
}

function peakToBackendSpec(p) {
  // All initial values go at top level — fitting.py reads spec.get("center") etc.
  const spec = {
    id: String(p.id),
    name: p.name,
407:    return Path(upload_folder) / f"{job_id}.job.json"
433:        candidates = list(Path(upload_folder).glob("*.job.json"))
707:        body = request.get_json()
717:        start_idx = _parse_int(body.get("start_idx"), 0, len(energy))
718:        end_idx = _parse_int(body.get("end_idx"), 0, len(energy), default=len(energy))
781:        body = request.get_json()
935:        body = request.get_json(silent=True)
974:        body = request.get_json(silent=True)
    const bgType  = document.getElementById('bg-type').value;
    const bgStart = parseFloat(document.getElementById('bg-start').value);
    const bgEnd   = parseFloat(document.getElementById('bg-end').value);
    // Inclusive bg window — the same point set computeBackgroundCore draws;
    // the backend slices end-exclusive, so the request sends i1 + 1.
    const bgWin = _bgWindowIndices(be, bgStart, bgEnd);
    // EVERY request input is read from the owner before the upload await:
    // peaks, method, endpoint averaging and manual anchors (Codex round 2: a
    // request could carry A's spectrum with B's averaging and anchors).
    // opts.startPeaks: the request starts from an adopted alternative; the live
    // model is still the student's until this fit succeeds (useAlternative).
    const startModel = opts.startPeaks || state.peaks;
    const peakSpecs = startModel.map(peakToBackendSpec);
    // scattered-starts check: decided HERE, with the other request inputs,
    // before the first await (a tab switch during the upload must not turn it off)
    const nStarts = _startsUnlinkedCount(startModel) >= 2 ? _STARTS_N : 0;
    // the live model and its fit context as the student pressed the button: a
    // result must not be written over a model that was edited while it ran
    const ctxAtRequest = _startsLiveKey();
    const fitMethod = document.getElementById('fit-method').value;
    const epAvgVal = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
    const bgPayload = { method: bgType, start_idx: bgWin.i0, end_idx: bgWin.i1 + 1, endpoint_avg: epAvgVal };
    if (bgType === 'manual') {
      // Anchors are stored in corrected-BE space, same frame as the uploaded
      // session data; backend expects [x, y] pairs.
      bgPayload.manual_bg = _getManualAnchors().map(a => [a.x, a.y]);
    }
    // Transport failures (server unreachable, timeout, non-JSON reply) are
    // the ONLY reason to fall back to the local optimiser. A server-side
    // validation error or a non-converged optimisation surfaces its message
    // and leaves the model untouched (unit A0: nothing is shown as a fit
    // result unless it converged; an HTTP 400 is not a reason to silently
    // switch engines).
    // Only a genuine transport failure (network rejection, abort, unparsable
    // 2xx body) is marked for fallback; server errors carry `serverError`.
    const _asTransport = (e) => {
tests/test_fit_reproducibility.py:304:def test_methods_outside_the_supported_five_are_refused_centrally(method):
tests/test_tougaard_background.py:230:    # is required here: the F1 anchor rescales by (ya[0]-c0)/bg[0], so a
tests/test_component_support.py:1:"""Per-component "support" in the /api/fit response (unit step (b), 2026-09-22).
tests/test_component_support.py:53:        assert sup["supported"] is True and sup["f"] > 1000
tests/test_component_support.py:56:def test_a_component_with_nothing_to_fit_is_unsupported_and_still_returned_in_full():
tests/test_component_support.py:65:    assert by["3"]["support"]["delta_chi2"] <= 0 or by["3"]["support"]["f"] < fitting.SUPPORT_MIN_F
tests/test_component_support.py:76:    sup = fitting._component_support(y_sub, fitted, comp, w, n_free_comp=3, n_free_total=3)
tests/test_component_support.py:81:    assert sup["supported"] is (f >= fitting.SUPPORT_MIN_F)
tests/test_component_support.py:83:    zero = fitting._component_support(y_sub, fitted, np.zeros(5), w, 3, 3)
tests/test_component_support.py:84:    assert zero["supported"] is False and zero["f"] == 0.0
tests/test_component_support.py:87:    assert exact["supported"] is True and exact["f"] is None       # infinite, serialised as null
tests/test_component_support.py:96:    assert by["3"]["support"]["follows"] == 2
tests/test_component_support.py:106:    assert all(ip["support"]["supported"] is True for ip in body["individual_peaks"])
tests/test_component_support.py:124:    # unsupported root gave [False, True, True] after a single forward pass.
tests/test_component_support.py:136:        assert by["8"]["support"]["supported"] is False and by["8"]["support"]["follows"] == 7
tests/test_component_support.py:137:        assert by["9"]["support"]["supported"] is False and by["9"]["support"]["follows"] == 7
tests/test_component_required.py:3:`support` holds the other components at their fitted values, so redundancy
tests/test_component_required.py:53:def test_a_redundant_anchor_is_supported_but_not_required(method):
tests/test_component_required.py:78:    assert g["support"]["f"] > 1e6, g["support"]["f"]           # far from the threshold, not on it
tests/test_component_required.py:79:    req = res["required"]
tests/test_component_required.py:82:    assert req["required"] is False
tests/test_component_required.py:85:def test_a_real_graphite_anchor_is_required():
tests/test_component_required.py:90:    req = res["required"]
tests/test_component_required.py:91:    assert req["ran"] and req["required"] is True and req["f"] > 1000
tests/test_component_required.py:102:    strip = lambda r: json.dumps({k: v for k, v in r.items() if k != "required"}, sort_keys=True)  # noqa: E731
tests/test_component_required.py:103:    assert strip(a) == strip(b) and a["required"] is None and b["required"]["ran"] is True
tests/test_component_required.py:118:    assert res["required"]["ran"] is True, res["required"]
tests/test_component_required.py:119:    assert res["required"]["required"] is False
tests/test_component_required.py:124:    assert res2["required"]["ran"] is True, res2["required"]
tests/test_component_required.py:128:    assert res3["required"]["ran"] is True, res3["required"]
tests/test_component_required.py:133:    assert res4["required"]["ran"] is True, res4["required"]
tests/test_component_required.py:141:    assert res["success"] is True and res["required"]["ran"] is True, res["required"]
tests/test_component_required.py:142:    assert res["required"]["required"] is False
tests/test_component_required.py:161:def test_known_limit_noise_free_exact_fit_reports_a_redundant_component_as_required():
tests/test_component_required.py:172:    assert res["required"]["ran"] is True
tests/test_component_required.py:173:    assert res["required"]["chi2_with"] < 1e-12                                # the premise: an exact fit
tests/test_component_required.py:174:    # documented: F is meaningless here and the verdict may read "required"; no rule papers over it
tests/test_component_required.py:175:    # with Poisson noise the same construction is judged on its merits: lossless -> not required
tests/test_component_required.py:179:    assert res_n["required"]["required"] is False, res_n["required"]
tests/test_component_required.py:182:def test_a_resolved_anchor_at_extreme_dynamic_range_is_required():
tests/test_component_required.py:188:        assert res["required"]["ran"] and res["required"]["required"] is True, (big, res["required"])
tests/test_browser_find_peaks_full_window.py:28:behavior is unchanged, as required.

codex
Find Peaks has two concrete gaps: selecting a region writes the ROI fields without refreshing the warnings, and its upload rounds energies to four decimals before the server filters them. Manual fit filters before that rounding, so boundary points can differ despite the plan’s “identical” claim. The focused JS tests pass; Python collection hit the read-only sandbox’s temporary-directory restriction.

 succeeded in 52730ms:
  duration_ms: 5.489235
  type: 'test'
  ...
1..408
# tests 408
# suites 0
# pass 325
# fail 78
# cancelled 0
# skipped 0
# todo 5
# duration_ms 52703.664303

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"-p\", \"no:cacheprovider\", \"--capture=sys\", \"-q\", \"tests/test_component_required.py\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
exec
/bin/zsh -lc "node -e '
const fs=require('\\''fs'\\'');
const lines=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'').split('\\''\\n'\\'');
function fn(name){const start=lines.findIndex(l=>new RegExp('\\''"'^(async )?function '"'\\''+name+'\\''\\\\('\\'').test(l));let n=0; for(let i=start;i<lines.length;i++){for(const c of lines[i]){if(c==='\\''{'\\'')n++;if(c==='\\''}'\\'')n--;}if(n===0)return lines.slice(start,i+1).join('\\''\\n'\\'');}}
const dom={'\\''roi-min'\\'':{value:'\\''280'\\''},'\\''roi-max'\\'':{value:'\\''295'\\''},'\\''roi-hint'\\'':{textContent:'\\'''\\'',style:{display:'\\''none'\\''}},'\\''fp-regions-tier-note'\\'':{},'\\''fp-regions-filter'\\'':{value:'\\'''\\''}};
let badgeHtml='\\'''\\''; const name={querySelector:()=>null,insertAdjacentHTML:(_,h)=>{badgeHtml=h;}};
const document={getElementById:id=>id==='\\''peak-item-1'\\''?{querySelector:()=>name}:dom[id]};
const state={rawBE:Array.from({length:151},(_,i)=>280+i/10),rawIntensity:Array(151).fill(100),ccShift:0,peaks:[{id:1,center:296,support:{supported:false,fitKey:'\\''KEY'\\''}}]};
const names=['\\''getCorrectedBE'\\'','\\''getROIData'\\'','\\''_roiWindowStatus'\\'','\\''_roiHintFor'\\'','\\''_refreshRoiHint'\\'','\\''_centreOutsideData'\\'','\\''_outsideDataBadge'\\'','\\''_patchPeakCardsForCentre'\\'','\\''_escAttr'\\'','\\''_fpSyncSelectionUI'\\''];
const api=new Function('\\''document'\\'','\\''state'\\'','\\''_fpRegionsSelected'\\'','\\''_fpMeta'\\'','\\''_fpTierNoteFor'\\'','\\''_fpRenderPtGrid'\\'','\\''_fpRenderExpandedPanel'\\'',names.map(fn).join('\\''\\n'\\'')+'\\''\\nreturn {'\\''+names.join('\\'','\\'')+'\\''}'\\'')(document,state,new Set(['\\''C 1s'\\'']),{coverage:[{region:'\\''C 1s'\\'',roi:{be_min:278,be_max:298}}]},()=>'\\'''\\'',()=>{},()=>{});
api._refreshRoiHint(api._roiWindowStatus()); api._fpSyncSelectionUI();
console.log('\\''After Find Peaks region pick:'\\'',JSON.stringify({fields:[dom['\\''roi-min'\\''].value,dom['\\''roi-max'\\''].value],hintDisplay:dom['\\''roi-hint'\\''].style.display,hintText:dom['\\''roi-hint'\\''].textContent,actualStatus:api._roiWindowStatus().state}));
api._patchPeakCardsForCentre(api._roiWindowStatus());console.log('\\''Unsupported component badge:'\\'',badgeHtml);
state.rawBE=Array.from({length:20},(_,i)=>280.00004+i/10);state.rawIntensity=Array(20).fill(100);dom['\\''roi-min'\\''].value='\\''280.00002'\\'';dom['\\''roi-max'\\''].value='\\''282.5'\\'';
const manual=api.getROIData().be;const server=state.rawBE.map(x=>Number(x.toFixed(4))).filter(x=>x>=Number(dom['\\''roi-min'\\''].value)&&x<=Number(dom['\\''roi-max'\\''].value));
console.log('\\''Upload-rounding counterexample:'\\'',JSON.stringify({manualN:manual.length,findPeaksN:server.length,manualFirst:manual[0],findPeaksFirst:server[0],hint:api._roiHintFor(api._roiWindowStatus())}));
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
After Find Peaks region pick: {"fields":[278,298],"hintDisplay":"none","hintText":"","actualStatus":"past"}
Unsupported component badge: <span class="outside-data-badge" data-peak-id="1" title="Centre 296.00 eV lies outside the fitted data (280.00–295.00 eV). A component centred outside the measured data is almost always a placement error: the fit sees only its tail. Nothing has been moved.">outside data</span>
Upload-rounding counterexample: {"manualN":20,"findPeaksN":19,"manualFirst":280.00004,"findPeaksFirst":280.1,"hint":{"cls":"","text":"ROI extends past your data — clipped to 280.00–281.90 eV."}}

exec
/bin/zsh -lc "node --test tests/js/*.test.js | rg -A 10 '"'^not ok'"'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
exec
/bin/zsh -lc "sed -n '1360,1470p' fitting.py; rg -n 'function renderEmptyChart' templates/index.html; sed -n '5010,5035p' templates/index.html; sed -n '5158,5192p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
exec
/bin/zsh -lc "rg -n 'spawnSync|execFileSync|execSync|mkdtemp|writeFile|python' tests/js | head -60; sed -n '1,80p' tests/test_component_support.py; nl -ba templates/index.html | sed -n '5090,5162p'; nl -ba docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md | sed -n '30,80p'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
    w2 = np.asarray(weights, float) ** 2
    r = np.asarray(y_sub, float) - np.asarray(fitted_sub, float)
    ok = np.isfinite(r) & np.isfinite(comp_y) & np.isfinite(w2)
    chi_with = float(np.sum(w2[ok] * r[ok] ** 2))
    chi_without = float(np.sum(w2[ok] * (r[ok] + np.asarray(comp_y, float)[ok]) ** 2))
    delta = chi_without - chi_with
    p = max(1, int(n_free_comp))
    dof = max(1, int(ok.sum()) - int(n_free_total))
    if delta <= 0:
        f = 0.0
    elif chi_with == 0:
        f = float("inf")
    else:
        f = (delta / p) / (chi_with / dof)
    return {"f": None if not np.isfinite(f) else f, "delta_chi2": delta,
            "supported": bool(delta > 0 and (chi_with == 0 or f >= SUPPORT_MIN_F))}


# ── "Is this component REQUIRED?" — the refit test ───────────────────────────
# `support` (above) holds the OTHER components at their fitted values, so it
# cannot see redundancy under overlap: a component the others could absorb if
# they were refitted still passes. The test for that is the refit itself:
# remove the component, refit the rest from their fitted values under the
# request's own bounds, and compare the fit to the data with and without it:
#     F = ((chi2_without_refit - chi2_with) / p) / (chi2_with / dof)
# p = the component's free parameters, dof = n - nvarys of the full model.
# One extra fit, so it is done only when asked for (Auto-Fit asks for its
# charge-reference anchor: an anchor that is not required must not set the
# energy reference of a whole spectrum). Same threshold as `support`.
def _component_required(fit_reduced, params_full, removed_prefixes, y_sub, weights,
                        chi2_with, n_free_comp, n_free_total) -> dict[str, Any]:
    """``fit_reduced(params)`` is the run's own fitter for the reduced model
    (the same candidate machinery and seeding the fit used, so differential
    evolution's box/refinement and the request seed apply to the refit too).
    ``removed_prefixes`` is the removed component AND everything linked to it,
    transitively. The reduced start is built in dependency order: plain
    parameters first, expressions after, so a child ordered before its parent
    in the request still resolves."""
    kept = [(name, par) for name, par in params_full.items() if not any(name.startswith(r) for r in removed_prefixes)]
    # ALL retained parameters exist before any expression is assigned, so a
    # chain of links in any request order resolves (lmfit evaluates an
    # expression when it is set).
    start = Parameters()
    for name, par in kept:
        start.add(name, value=par.value, min=par.min, max=par.max, vary=par.vary)
    for name, par in kept:
        if par.expr:
            start[name].set(expr=par.expr)
    refit = fit_reduced(start)
    chi2_without = float(refit.chisqr) if refit.chisqr is not None else float("inf")
    delta = chi2_without - chi2_with
    p = max(1, int(n_free_comp))
    dof = max(1, len(y_sub) - int(n_free_total))
    # No tolerance of any kind (Codex rounds 2-3: a floor on the chi-square
    # change relative to the data's power, and then an "exactness" cutoff on
    # the reduced fit, each masked a resolved anchor at high dynamic range —
    # the same lesson as the DE unit). Known limit, accepted: on NOISE-FREE
    # data whose full fit is numerically exact (chi2_with ~ 1e-28) F is not
    # meaningful and a truly redundant component (two identical half-amplitude
    # components) reports "required"; real data never fit to machine precision.
    if not np.isfinite(chi2_without):
        f, required = None, True                     # the rest could not even be fitted without it
    elif delta <= 0:
        f, required = 0.0, False
    elif chi2_with == 0:
        f, required = None, True
    else:
        f = (delta / p) / (chi2_with / dof)
        required = f >= SUPPORT_MIN_F
    return {"required": bool(required), "f": f, "chi2_with": float(chi2_with), "chi2_without_refit": chi2_without,
            "refit_converged": bool(refit.success)}


# ─────────────────────────────────────────────────────────────────────────────
# Main fitting API
# ─────────────────────────────────────────────────────────────────────────────

def run_fit(
    energy: np.ndarray,
    counts: np.ndarray,
    peak_specs: list[dict[str, Any]],
    background_method: str = "shirley",
    bg_start_idx: int | None = None,
    bg_end_idx: int | None = None,
    charge_shift_ev: float = 0.0,
    fit_kws: dict | None = None,
    n_perturb: int = 0,
    manual_bg: list | None = None,
    endpoint_avg: int = 1,
    n_starts: int = 0,
    require_component=None,
) -> dict[str, Any]:
    """
    Run XPS peak fitting and return a serialisable result dict.

    Parameters
    ----------
    energy            : 1‑D array of binding energies (eV)
    counts            : 1‑D array of intensities (counts / CPS)
    peak_specs        : list of peak specification dicts (see _make_peak_params)
    background_method : 'shirley' | 'linear' | 'none'
    bg_start_idx      : slice start for background region (None → 0)
    bg_end_idx        : slice end for background region   (None → len)
    charge_shift_ev   : shift to apply to energy axis before fitting
    fit_kws           : extra kwargs forwarded to lmfit minimize

    Returns
    -------
    dict with keys: energy, fitted_y, background_y, residuals,
                    individual_peaks, statistics, charge_shift_applied, success
    """
9902:function renderEmptyChart() {
    for (const p of state.peaks) {
      p.center -= delta;
    }

    // Manual background anchors. Anchors are DATA-ATTACHED like peak
    // centers (x = a data point's corrected BE at placement time, y = that
    // point's intensity), so they follow the same -delta migration as the
    // ROI/bg fields and peak centers above — NOT the reference-marker
    // convention (literature markers stay at nominal corrected BE). y is
    // untouched: intensity is unaffected by charge correction. Saved files
    // need no migration — anchors persist alongside the tab's ccShift, so
    // every save is a self-consistent snapshot.
    const ccAnchors = _getManualAnchors();
    for (const a of ccAnchors) {
      a.x -= delta;
    }

    // Background cache is no longer valid after CC shift
    _invalidateBgCache();
  }

  const shift = -state.ccShift;
  document.getElementById('cc-shift-display').textContent = (shift >= 0 ? '+' : '') + shift.toFixed(3) + ' eV';
  updatePlot();
  // Re-render the per-peak panels so the C 1s graphite checkbox
  // appears/disappears reactively when the method changes (and any
  _patchPeakCardsForCentre(st);
  return st;
}

function maxROI() {
  if (!state.rawBE.length) return;
  const be = getCorrectedBE();
  const lo = _arrMin(be);
  const hi = _arrMax(be);
  document.getElementById('roi-min').value = lo.toFixed(1);
  document.getElementById('roi-max').value = hi.toFixed(1);
  document.getElementById('bg-start').value = hi.toFixed(1);
  document.getElementById('bg-end').value = lo.toFixed(1);
  updatePlot();
}

function autoSetROI() {
  if (!state.rawBE.length) return;
  const be = getCorrectedBE();
  const _roiLo = _arrMin(be), _roiHi = _arrMax(be);
  document.getElementById('roi-min').value = _roiLo.toFixed(1);
  document.getElementById('roi-max').value = _roiHi.toFixed(1);
  document.getElementById('bg-start').value = _roiHi.toFixed(1);
  document.getElementById('bg-end').value = _roiLo.toFixed(1);
  updatePlot();
}

// ═══════════════════════════════════════════════════
// PEAKS
// ═══════════════════════════════════════════════════
// Normalize charge-reference flags on a freshly-loaded peak list.
// Old saves do not have `isChargeReference` — default to false.
// If a save somehow has >1 true, keep the first and clear the rest.
function _normalizePeaksCRef(peaks) {
  if (!Array.isArray(peaks)) return peaks;

 succeeded in 0ms:
tests/js/local_lm_descent.test.js:19:const { execFileSync } = require('node:child_process');
tests/js/local_lm_descent.test.js:71:  const py = fs.existsSync(path.join(REPO_ROOT, 'venv/bin/python3')) ? path.join(REPO_ROOT, 'venv/bin/python3')
tests/js/local_lm_descent.test.js:72:    : (fs.existsSync('/Users/skyefortier/xps-app/venv/bin/python3') ? '/Users/skyefortier/xps-app/venv/bin/python3' : 'python3');
tests/js/local_lm_descent.test.js:75:  return JSON.parse(execFileSync(py, ['-c', script, REPO_ROOT, PROJECT], { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }));
tests/js/local_lm_descent.test.js:458:  const py = fs.existsSync(path.join(REPO_ROOT, 'venv/bin/python3')) ? path.join(REPO_ROOT, 'venv/bin/python3')
tests/js/local_lm_descent.test.js:459:    : (fs.existsSync('/Users/skyefortier/xps-app/venv/bin/python3') ? '/Users/skyefortier/xps-app/venv/bin/python3' : 'python3');
tests/js/local_lm_descent.test.js:468:    const server = JSON.parse(execFileSync(py, [bridge, REPO_ROOT], { input: JSON.stringify({ be, inten, peaks: initial, ui }), encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 }));
tests/js/unsupported_components.test.js:185:    XLSX: { utils: { book_new: () => ({}), aoa_to_sheet: a => a, book_append_sheet: (wb, ws) => rows.push(ws) }, writeFile: () => {} },
tests/js/unsupported_components.test.js:228:    XLSX: { utils: { book_new: () => ({}), aoa_to_sheet: a => a, book_append_sheet: (wb, ws) => rows.push(ws) }, writeFile: () => {} },
tests/js/unsupported_components.test.js:268:    XLSX: { utils: { book_new: () => ({}), aoa_to_sheet: a => a, book_append_sheet: (wb, ws) => rows.push(ws) }, writeFile: () => {} },
tests/js/lineshape_parity_backend.py:1:#!/usr/bin/env python3
tests/js/tougaard_twin.test.js:114:  //   venv/bin/python - <<'EOF'
tests/js/tougaard_twin.test.js:139:      `backend/frontend disagree at index ${idx}: js ${got} vs python ${want}`);
tests/js/lineshape_roundtrip_backend.py:1:#!/usr/bin/env python3
tests/js/lineshape_roundtrip.test.js:24:const { execFileSync } = require('node:child_process');
tests/js/lineshape_roundtrip.test.js:50:  for (const c of [process.env.XPS_PYTHON, path.join(REPO_ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3']) {
tests/js/lineshape_roundtrip.test.js:53:  return 'python3';
tests/js/lineshape_roundtrip.test.js:58:  return JSON.parse(execFileSync(PYTHON, [BRIDGE, REPO_ROOT], { input: JSON.stringify(payload), encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }));
tests/js/lineshape_parity.test.js:37:const { execFileSync } = require('node:child_process');
tests/js/lineshape_parity.test.js:64:    path.join(REPO_ROOT, 'venv/bin/python3'),          // main checkout's own venv
tests/js/lineshape_parity.test.js:65:    '/Users/skyefortier/xps-app/venv/bin/python3',      // worktree -> main repo venv
tests/js/lineshape_parity.test.js:66:    'python3',
tests/js/lineshape_parity.test.js:70:      if (c === 'python3' || fs.existsSync(c)) return c;
tests/js/lineshape_parity.test.js:73:  return 'python3';
tests/js/lineshape_parity.test.js:80:  const out = execFileSync(PYTHON, [BRIDGE], { input, encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 });
tests/js/lineshape_parity.test.js:329:  const out = execFileSync(PYTHON, [BRIDGE], { input, encoding: 'utf8', maxBuffer: 256 * 1024 * 1024 });
"""Per-component "support" in the /api/fit response (unit step (b), 2026-09-22).

Owner decision 2026-09-18: a component whose amplitude the fit drove to its
floor is an explicit outcome — NOT SUPPORTED BY THE DATA — and its centre,
width and sigma are not reported. The statistic is the one shipped for the
Auto-Fit anchor (with/without-component F, no intensity floor); the server
computes it once per component so every consumer reads one field.
"""

import io

import numpy as np
import pytest

import fitting
from app import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app(upload_folder=str(tmp_path))
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _g(x, c, a, w):
    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)


def _spectrum():
    rng = np.random.default_rng(3)
    x = np.arange(280.0, 295.0, 0.1)
    y = rng.poisson(200.0 + _g(x, 284.8, 4000.0, 1.1) + _g(x, 288.6, 900.0, 1.4)).astype(float)
    return x, y


def _specs(extra=None):
    s = [{"id": 1, "name": "A", "shape": "pseudo_voigt_gl", "center": 284.6, "amplitude": 3500.0, "fwhm": 1.2, "gl_ratio": 0.3, "amplitude_min": 0},
         {"id": 2, "name": "B", "shape": "pseudo_voigt_gl", "center": 288.9, "amplitude": 700.0, "fwhm": 1.2, "gl_ratio": 0.3, "amplitude_min": 0}]
    return s + (extra or [])


KW = dict(background_method="linear", n_perturb=0, fit_kws={"method": "least_squares"})


def test_every_component_carries_a_support_verdict():
    x, y = _spectrum()
    res = fitting.run_fit(x, y, _specs(), **KW)
    for ip in res["individual_peaks"]:
        sup = ip["support"]
        assert set(sup) >= {"f", "delta_chi2", "supported"}
        assert sup["supported"] is True and sup["f"] > 1000


def test_a_component_with_nothing_to_fit_is_unsupported_and_still_returned_in_full():
    # a third component where the data hold nothing: the fit drives it to its floor
    x, y = _spectrum()
    ghost = {"id": 3, "name": "ghost", "shape": "gaussian", "center": 292.5, "center_min": 291.5, "center_max": 293.5,
             "amplitude": 300.0, "amplitude_min": 0, "fwhm": 1.0}
    res = fitting.run_fit(x, y, _specs([ghost]), **KW)
    assert res["success"] is True
    by = {str(ip["id"]): ip for ip in res["individual_peaks"]}
    assert by["3"]["support"]["supported"] is False
    assert by["3"]["support"]["delta_chi2"] <= 0 or by["3"]["support"]["f"] < fitting.SUPPORT_MIN_F
    assert by["1"]["support"]["supported"] and by["2"]["support"]["supported"]
    # the parameters are still there for anyone who wants them; the PAGE decides what to show
    assert "center" in by["3"]["params"] and "area" in by["3"]["params"]


def test_the_statistic_matches_the_auto_fit_anchor_definition():
    y_sub = np.array([1.0, 2.0, 3.0, 2.0, 1.0])
    fitted = np.array([1.0, 2.0, 2.5, 2.0, 1.0])
    comp = np.array([0.0, 0.0, 2.5, 0.0, 0.0])
    w = np.ones(5)
    sup = fitting._component_support(y_sub, fitted, comp, w, n_free_comp=3, n_free_total=3)
    chi_with = 0.25
    chi_without = (3.0 - 2.5 + 2.5) ** 2      # residual + component at the one differing point
    f = ((chi_without - chi_with) / 3) / (chi_with / (5 - 3))
    assert sup["f"] == pytest.approx(f) and sup["delta_chi2"] == pytest.approx(chi_without - chi_with)
  5090	  let dMin = Infinity, dMax = -Infinity;
  5091	  for (const v of corrBE) { if (v < dMin) dMin = v; if (v > dMax) dMax = v; }
  5092	  const lo = parseFloat(document.getElementById('roi-min').value);
  5093	  const hi = parseFloat(document.getElementById('roi-max').value);
  5094	  const { be } = getROIData();
  5095	  let sMin = Infinity, sMax = -Infinity;
  5096	  for (const v of be) { if (v < sMin) sMin = v; if (v > sMax) sMax = v; }
  5097	  const base = { dMin, dMax, lo, hi, sMin, sMax, n: be.length };
  5098	  if (Number.isFinite(lo) && Number.isFinite(hi) && lo > hi) return { ...base, state: 'inverted' };
  5099	  if (!be.length) return { ...base, state: 'no-overlap' };
  5100	  // one sampling step = median |Δ corrected BE|: within a step there is no
  5101	  // sample the window could have included, so a toFixed(1) rounding of an
  5102	  // edge is not "past the data" (a grid-relative criterion, not a threshold
  5103	  // on intensity)
  5104	  const d = [];
  5105	  for (let i = 1; i < corrBE.length; i++) d.push(Math.abs(corrBE[i] - corrBE[i - 1]));
  5106	  d.sort((a, b) => a - b);
  5107	  const step = d.length ? (d.length % 2 ? d[(d.length - 1) / 2] : 0.5 * (d[d.length / 2 - 1] + d[d.length / 2])) : 0;
  5108	  const past = (Number.isFinite(lo) && lo < dMin - step) || (Number.isFinite(hi) && hi > dMax + step);
  5109	  return { ...base, step, state: past ? 'past' : 'ok' };
  5110	}
  5111	function _roiHintFor(st) {
  5112	  const f = v => v.toFixed(2);
  5113	  if (st.state === 'past') return { cls: '', text: `ROI extends past your data — clipped to ${f(st.sMin)}–${f(st.sMax)} eV.` };
  5114	  if (st.state === 'inverted') return { cls: 'amber', text: 'BE min is above BE max — no data is selected.' };
  5115	  if (st.state === 'no-overlap') return { cls: 'amber', text: `ROI does not overlap your data (${f(st.dMin)}–${f(st.dMax)} eV) — no data is selected.` };
  5116	  return null;
  5117	}
  5118	function _refreshRoiHint(st) {
  5119	  const el = document.getElementById('roi-hint');
  5120	  if (!el) return;
  5121	  const h = st ? _roiHintFor(st) : null;
  5122	  if (!h) { if (el.style.display !== 'none') { el.style.display = 'none'; el.textContent = ''; } return; }
  5123	  if (el.textContent !== h.text) el.textContent = h.text;
  5124	  el.className = 'roi-hint' + (h.cls ? ' ' + h.cls : '');
  5125	  el.style.display = '';
  5126	}
  5127	// A component centred outside the selected data: the fit sees only its tail.
  5128	// Almost always a placement error — and the one way to reach the DS+G
  5129	// normalisation limit (plan 2026-09-22-dsg-page-evaluator §3c).
  5130	function _centreOutsideData(p, st) {
  5131	  return !!(st && st.n > 0 && Number.isFinite(p.center) && (p.center < st.sMin || p.center > st.sMax));
  5132	}
  5133	function _outsideDataBadge(p, st) {
  5134	  const tip = `Centre ${p.center.toFixed(2)} eV lies outside the fitted data (${st.sMin.toFixed(2)}–${st.sMax.toFixed(2)} eV). `
  5135	    + 'A component centred outside the measured data is almost always a placement error: the fit sees only its tail. Nothing has been moved.';
  5136	  return `<span class="outside-data-badge" data-peak-id="${p.id}" title="${_escAttr(tip)}">outside data</span>`;
  5137	}
  5138	// Patched IN PLACE (the student may be typing in a card): add, update or
  5139	// remove each card's badge; never re-render the list.
  5140	function _patchPeakCardsForCentre(st) {
  5141	  for (const p of state.peaks) {
  5142	    const item = document.getElementById('peak-item-' + p.id);
  5143	    if (!item) continue;
  5144	    const name = item.querySelector('.peak-name');
  5145	    if (!name) continue;
  5146	    const badge = name.querySelector('.outside-data-badge');
  5147	    const out = _centreOutsideData(p, st);
  5148	    if (out) {
  5149	      const html = _outsideDataBadge(p, st);
  5150	      if (!badge) name.insertAdjacentHTML('beforeend', html);
  5151	      else { const tmp = document.createElement('span'); tmp.innerHTML = html; const t = tmp.firstChild.getAttribute('title'); if (badge.getAttribute('title') !== t) badge.setAttribute('title', t); }
  5152	    } else if (badge) badge.remove();
  5153	  }
  5154	}
  5155	function _refreshRoiAndCentreWarnings() {
  5156	  const st = _roiWindowStatus();
  5157	  _refreshRoiHint(st);
  5158	  _patchPeakCardsForCentre(st);
  5159	  return st;
  5160	}
  5161	
  5162	function maxROI() {
    30	ROI readers (`roi-min`, `roi-max`, `ui.roiMin`, `ui.roiMax`, `getROIData`):
    31	
    32	| # | site | what it reads | window semantics | this unit |
    33	|---|---|---|---|---|
    34	| 1 | `getROIData` | DOM fields | inclusive filter of corrected BE; empty = ±∞; min > max → EMPTY | unchanged; the hint's source of truth |
    35	| 2 | `runFit` (Run Fit, `/api/fit`) | `getROIData` | as 1 (the request carries the filtered arrays) | unchanged |
    36	| 3 | `runFitLocal` via Batch Fit `runPropagation` | `getROIData` on each target, target keeps its own ROI (`propagateFitUi` keep) | as 1 | unchanged; summary row notes a clipped target |
    37	| 4 | Find Peaks `/api/analyze` payload (`fpMethodMeta` block) | DOM fields as numbers + `getCorrectedBE()` | server `app._validate_analyze_request`: `(corrected >= be_min) & (corrected <= be_max)` — the SAME inclusive mask on the SAME corrected frame | unchanged — verified identical to 1 (§3); an EMPTY field differs (page: full range; server: 400 "must be numbers") — logged, not changed |
    38	| 5 | Find Peaks ROI auto-fill (`coverage` block) | writes `entries[0].roi.be_min/max` (curated nominal window, can exceed the data) | — | unchanged; the hint now fires when the suggested window overshoots |
    39	| 6 | `updatePlot` (chart fitted region, preview) | `getROIData` | as 1 | hosts the hint + centre-warning refresh |
    40	| 7 | `renderPeakList` / `_patchPeakCardsForSupport` (area %) | `getROIData` | as 1 | cards get the centre warning |
    41	| 8 | `renderResults` fallback grid, `exportResults`, figure export, `_doSaveSpectrum`, `applyAutoFitResult`, `runAutoFitC1sGraphite`, `handleChartClick` | `getROIData` | as 1 | unchanged |
    42	| 9 | `zoomToROI` | DOM fields, swapped if min > max | axis only | unchanged |
    43	| 10 | `isC1sTab` (Auto-Fit enable gate) | `ui.roiMin/roiMax` MIDPOINT of the typed values | typed window, not the data it selects | unchanged — logged: with an ROI past the data the gate judges a window the fit never sees |
    44	| 11 | `_buildEntryRenderData` Path B (stack tabs) | `ui.roiMin/roiMax`, SWAPPED if min > max | differs from 1 for an inverted ROI (1 selects nothing) | unchanged — logged; the source tab's hint says "no data selected" |
    45	| 12 | `_captureUI` / `_restoreUI` / `toJSON` / `fromJSON` / `_doSaveFit` / `_autoFitSnapshot` / `_autoFitRestore` | read/write the field values verbatim | — | unchanged: loading a file restores the same numbers and the fit selects the same data as before; the hint is computed from the live fields and data, so an old file only GAINS a message |
    46	| 13 | `updateChargeCorrection` | shifts both fields by the correction delta | ROI follows the data | unchanged; the hint re-evaluates after the redraw |
    47	| 14 | `autoSetROI` / `maxROI` | write fields from the data range (`toFixed(1)`) | may land a rounding step inside or outside the data edge | unchanged; the hint's criterion (§4) ignores sub-step overshoot |
    48	| 15 | `_STARTS_UI_FIELDS` (fit-evidence key) | `roiMin`, `roiMax` | — | unchanged (the hint writes nothing into the model or key) |
    49	| 16 | Python twin `autofit/reference.py` `ReferenceFit._roi_bounds` / `roi_mask` | saved `ui` | inclusive, empty = ±∞ | unchanged |
    50	| 17 | `_getSuggestedPresets` | `bg-start` / `bg-end` (not the ROI) | — | not an ROI reader (named `roiMin` locally) |
    51	
    52	Peak-centre readers relevant to "outside the data": the card header and
    53	summary (`renderPeakList`, patched in place by `_patchPeakCardsForSupport`).
    54	The data window a component is fitted against is the ROI selection of
    55	row 1, so the warning compares `p.center` with min/max of `getROIData().be`
    56	— the grid the request carries.
    57	
    58	## 3. "One fix covers both" — verified
    59	
    60	Manual fit (row 2) and Find Peaks (row 4) apply the same inclusive
    61	[min, max] filter to the same corrected energies (the page sends
    62	`getCorrectedBE()` with `cc_shift: 0`; the server masks those numbers with
    63	the two field values). For any numeric ROI the selected points are
    64	identical, so the one clamped window the hint names is the window both
    65	use. The only divergence is an EMPTY field (row 4): not an ROI past the
    66	data, logged for the fail-open sweep.
    67	
    68	## 4. The hint
    69	
    70	Under the ROI inputs, one line, computed on every redraw of a spectrum tab
    71	(hidden on stack tabs):
    72	
    73	- ROI reaches more than ONE SAMPLING STEP past the data on either side
    74	  (a step = median |Δ corrected BE|; within a step there is no sample the
    75	  window could have included, so a `toFixed(1)` rounding of the edge is not
    76	  "past the data" — a grid-relative criterion, not an intensity threshold):
    77	  quiet — "ROI extends past your data — clipped to X–Y eV." (X, Y = the
    78	  first and last selected energies);
    79	- min > max: amber — "BE min is above BE max — no data is selected.";
    80	- no overlap: amber — "ROI does not overlap your data (X–Y eV) — no data is

 succeeded in 83505ms:
.........                                                                [100%]
9 passed in 83.01s (0:01:23)

exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '9570,9575p'; nl -ba templates/index.html | sed -n '3295,3325p'; sed -n '9902,9920p' templates/index.html; nl -ba tests/js/unsupported_components.test.js | sed -n '134,146p'; nl -ba tests/test_component_required.py | sed -n '70,83p'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
  9570	
  9571	  _refreshStartsEvidence(false, true);   // background / ROI controls only repaint the chart: keep the visible consumers honest (fromPlot: the chart itself is being rebuilt)
  9572	  _refreshRoiAndCentreWarnings();         // ROI past the data / centre outside the data: warn, never move
  9573	  // History snapshot preview overlay (cyan dashed, drawn on top)
  9574	  if (_historyPreview && _historyPreview.peaks && _historyPreview.peaks.length && plotBE.length) {
  9575	    const prevPeakY = evalAllPeaks(plotBE, _historyPreview.peaks);
  3295	      }
  3296	    }
  3297	
  3298	    if (this.tabs.length === 0) {
  3299	      this.activeId = null;
  3300	      _updateUndoButtons();
  3301	      if (typeof _historyPreview !== 'undefined') _historyPreview = null;
  3302	      state.rawBE = []; state.rawIntensity = [];
  3303	      state.peaks = []; state.fitResult = null;
  3304	      state.ccShift = 0; state.nextId = 1;
  3305	      document.getElementById('data-info').textContent = 'no data';
  3306	      const _cl = document.getElementById('spec-combo-label');
  3307	      if (_cl) _cl.textContent = 'no data';
  3308	      document.getElementById('sb-pts').textContent = '\u2014';
  3309	      document.getElementById('sb-range').textContent = '\u2014';
  3310	      renderPeakList();
  3311	      renderEmptyChart();
  3312	      this.renderTabBar();
  3313	      this._updateSurveyPanel();
  3314	      this._updateCCVerifiedUI(true);
  3315	      _updateRFactorUI(null);
  3316	      _updateROIDisplay(null);
  3317	      const notesEl = document.getElementById('spectrum-notes');
  3318	      if (notesEl) notesEl.value = '';
  3319	      return;
  3320	    }
  3321	
  3322	    if (this.activeId === id) {
  3323	      const nextIdx = Math.min(idx, this.tabs.length - 1);
  3324	      this.activeId = null; // force re-activate
  3325	      this.activateTab(this.tabs[nextIdx].id);
function renderEmptyChart() {
  // Reference mode (A7): overlays selected + no spectrum loaded (palette open or
  // closed) → draw markers on a labeled 0–1200 eV axis instead of the onboarding
  // card. No overlays → the onboarding card (the chart is torn down below).
  if (typeof _refReferenceModeWanted === 'function' && _refReferenceModeWanted()) {
    _refRenderReferenceChart();
    return;
  }
  if (state.chart) { state.chart.destroy(); state.chart = null; }
  if (state.residChart) { state.residChart.destroy(); state.residChart = null; }
  document.getElementById('resid-wrap').classList.add('hidden');
  document.getElementById('resid-handle').classList.add('hidden');

  const wrap = document.getElementById('main-chart-wrap');
  const canvas = document.getElementById('mainChart');
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Remove any existing onboarding overlay
   134	  assert.doesNotMatch(cards[0], /unsupported-badge/);
   135	  const total = 86000 * 0.64 + 2600 * 3.5;                      // Unknown 2 excluded from the total
   136	  assert.match(cards[0], new RegExp((86000 * 0.64 / total * 100).toFixed(1) + '%'));
   137	});
   138	
   139	test('results table: greyed row, no centre / width / sigma, area kept, percentage dash, and the note beneath', () => {
   140	  const env = pageEnv(['renderResults', 'fmtVal'].filter(n => lines.some(l => new RegExp('^function ' + n + '\\(').test(l))));
   141	  env.renderResults();
   142	  const h = env.els['results-area'].innerHTML || Object.values(env.els).map(e => e.innerHTML).find(x => /unsupported-row/.test(x));
   143	  assert.ok(h, 'results html');
   144	  const row = h.slice(h.indexOf('unsupported-row'), h.indexOf('</tr>', h.indexOf('unsupported-row')));
   145	  assert.match(row, /Unknown 2/);
   146	  assert.doesNotMatch(row, /282\.25|0\.42|±/);
    70	    y = np.round(1000 + _gl(X, 10000, 284.8, 1.4) + _gl(X, 15000, 283.3, 1.8), 2)
    71	    specs = _autofit_model(1500, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
    72	    specs[0]["fix_amplitude"] = True
    73	    kw = dict(KW, fit_kws={"method": method})
    74	    res = fitting.run_fit(X, y, specs, require_component="1", **kw)
    75	    assert res["success"] is True
    76	    g = next(ip for ip in res["individual_peaks"] if ip["id"] == "1")
    77	    assert g["support"]["supported"] is True, "held-others statistic passes: that is the gap"
    78	    assert g["support"]["f"] > 1e6, g["support"]["f"]           # far from the threshold, not on it
    79	    req = res["required"]
    80	    assert req["ran"] is True and req["refit_converged"] is True
    81	    assert req["chi2_without_refit"] < 1e-2 * req["chi2_with"]
    82	    assert req["required"] is False
    83	

exec
/bin/zsh -lc "git status --short; git log -1 --oneline; rg -n '_roiWindowStatus|_patchPeakCardsForCentre|_fpSyncSelectionUI|_refreshRoiAndCentreWarnings' templates/index.html tests/js/unsupported_components.test.js; git diff --stat" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-lbGACT0z' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-JlG8i3yt' (errno=Operation not permitted)
?? docs/autofit/codex/roi_clamp_review_prompt.txt
?? docs/autofit/codex/roi_clamp_verdict_runA.md
?? docs/autofit/codex/roi_clamp_verdict_runB.md
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-x8SzVp7e' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-XKEKiqpE' (errno=Operation not permitted)
3a33253 test(unsupported): stub the ROI / centre-warning helpers in the renderPeakList environment
tests/js/unsupported_components.test.js:116:    _roiWindowStatus: () => ({ state: 'ok', n: 0 }), _patchPeakCardsForCentre: () => {},   // the ROI / centre warnings: tests/js/roi_clamp_centre_warning.test.js
templates/index.html:5087:function _roiWindowStatus() {
templates/index.html:5140:function _patchPeakCardsForCentre(st) {
templates/index.html:5155:function _refreshRoiAndCentreWarnings() {
templates/index.html:5156:  const st = _roiWindowStatus();
templates/index.html:5158:  _patchPeakCardsForCentre(st);
templates/index.html:6147:  if (state.rawBE && state.rawBE.length) _patchPeakCardsForCentre(_roiWindowStatus());
templates/index.html:9572:  _refreshRoiAndCentreWarnings();         // ROI past the data / centre outside the data: warn, never move
templates/index.html:12093:    const roiSt = _roiWindowStatus();    // warn only: the fit below uses getROIData() exactly as before
templates/index.html:15481:  _fpSyncSelectionUI();
templates/index.html:15484:function _fpSyncSelectionUI() {
templates/index.html:15667:  // submitted (see _fpToggleRegion / _fpSyncSelectionUI).
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-2yGvxXSt' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-XPqh23ij' (errno=Operation not permitted)

 succeeded in 57506ms:
not ok 156 - (A) frontend vs backend parity: Gaussian
  ---
  duration_ms: 1553.39761
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 157 - (A) frontend vs backend parity: Lorentzian
  ---
  duration_ms: 1282.010466
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 158 - (A) frontend vs backend parity: GL
  ---
  duration_ms: 1278.721018
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 159 - (A) frontend vs backend parity: Voigt
  ---
  duration_ms: 1293.402619
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 160 - (A) frontend vs backend parity: DS
  ---
  duration_ms: 1317.539969
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 161 - (A) frontend vs backend parity: asym-GL
  ---
  duration_ms: 1279.744672
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 162 - (A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization) # TODO unit 2 fast-follow: LACX Gaussian-conv kernel mismatch vs backend, grows with m (~0.15% at m=50, measured 2026-08-30)
  ---
  duration_ms: 1274.574911
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:171:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 163 - (A) frontend vs backend parity: LACX at m=0 (no convolution)
  ---
  duration_ms: 1229.005094
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:182:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 164 - (A) frontend vs backend parity: DSG_LA at moderate m (FIXED 2026-09-22: grid-aware convolution, dsgConvolved_array)
  ---
  duration_ms: 1263.691041
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:194:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 165 - (A) frontend vs backend parity: DSG_LA at m=0, center on-grid (delta kernel)
  ---
  duration_ms: 1277.074343
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:218:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 166 - (A) frontend vs backend parity: DSG_LA at m=0, center half-step off-grid (delta kernel)
  ---
  duration_ms: 1233.807583
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:218:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 167 - (A) frontend vs backend parity: DSG_LA at m=0.0009, center on-grid (delta kernel)
  ---
  duration_ms: 1310.272437
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:218:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 168 - (A) frontend vs backend parity: DSG_LA at m=0.0009, center half-step off-grid (delta kernel)
  ---
  duration_ms: 1412.605675
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:218:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 169 - (A) frontend vs backend parity: DSG_LA at m=0, descending grid, off-grid center
  ---
  duration_ms: 1268.333117
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:235:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 176 - (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA # TODO evalPeak() DSG_LA branch is the normalised DS core with m IGNORED (the convolution is a grid operation, dsgConvolved_array via evalPeakArray); no shipped caller reaches it — guard (C)
  ---
  duration_ms: 4.243918
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:265:3'
  failureType: 'testCodeFailure'
  error: 'DSG_LA at x=393.3: evalPeak=7298.4050340345175, evalPeakArray[i]=8703.575517573383, rel diff=7.8969%'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
--
not ok 177 - (B) evalPeak vs evalPeakArray agree pointwise: LACX # TODO evalPeak() LACX branch ignores m; only its call sites are rerouted in unit-1 commit 2, not evalPeak() itself — see file header
  ---
  duration_ms: 1.40559
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:265:3'
  failureType: 'testCodeFailure'
  error: 'LACX at x=393.3: evalPeak=2863.2353955224326, evalPeakArray[i]=7170.363795150584, rel diff=24.2055%'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
--
not ok 179 - (D) sweep across the fitted range: Gaussian
  ---
  duration_ms: 1242.468106
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 180 - (D) sweep across the fitted range: Lorentzian
  ---
  duration_ms: 1247.735168
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 181 - (D) sweep across the fitted range: Voigt
  ---
  duration_ms: 1378.052303
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 182 - (D) sweep across the fitted range: GL
  ---
  duration_ms: 1275.66476
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 183 - (D) sweep across the fitted range: asym-GL
  ---
  duration_ms: 1269.223261
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 184 - (D) sweep across the fitted range: DS
  ---
  duration_ms: 1258.796299
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 185 - (D) sweep across the fitted range: DSG_LA (delta kernel)
  ---
  duration_ms: 1292.756127
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 186 - (D) sweep across the fitted range: LACX (m = 0)
  ---
  duration_ms: 1277.826587
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 187 - (D) sweep across the fitted range: DSG_LA (m > 0)
  ---
  duration_ms: 1219.916333
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
--
not ok 188 - (D) sweep across the fitted range: LACX (m > 0) — KNOWN GAP # TODO convolved shapes: LACX kernel discretisation (unit 2 / caM clamp); DSG_LA page quadrature step ignores the Gaussian kernel width (own unit)
  ---
  duration_ms: 1326.805378
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:389:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
--
not ok 189 - (D′) DS+G convolution converges on another grid: step 0.1 eV, 120 pts
  ---
  duration_ms: 1266.537786
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 190 - (D′) DS+G convolution converges on another grid: step 0.02 eV, 500 pts
  ---
  duration_ms: 1211.180292
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
--
not ok 191 - (D′) DS+G convolution converges on another grid: step 0.05 eV, descending
  ---
  duration_ms: 1273.78126
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
--
not ok 192 - (D′) DS+G convolution converges on another grid: step 0.05 eV, centre half a step off-grid
  ---
  duration_ms: 1267.316664
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
--
not ok 193 - (D′) DS+G convolution converges on another grid: step 0.1 eV, descending, centre 0.03 eV off-grid
  ---
  duration_ms: 1268.920782
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 194 - (D′) DS+G convolution converges on another grid: short window: 30 pts at 0.1 eV (narrower than the pad)
  ---
  duration_ms: 1198.518914
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 195 - (D′) DS+G convolution converges on another grid: irregular-ish step 0.0503 eV (median step), 181 pts
  ---
  duration_ms: 1341.113291
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
--
not ok 196 - (D″) DS+G regression: centre 10 eV outside a [−5, 5] window (a free DS+G centre has no window on the server)
  ---
  duration_ms: 1358.804325
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 197 - (D″) DS+G regression: a 6-point irregular grid
  ---
  duration_ms: 1313.027052
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 198 - (D″) DS+G regression: genuinely irregular steps (0.05 / 0.06 alternating; median ≠ mean)
  ---
  duration_ms: 1344.54
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 199 - (D″) DS+G regression: a 0.001 eV grid over 10 eV at the box corner β 2, m 4, α 0.49 (13 s per curve in the first cut)
  ---
  duration_ms: 1263.986035
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
--
not ok 200 - (D″) DS+G regression: centre 10 eV outside [−5, 5] on a 0.5 eV grid, β 0.05, m 0.05 (Codex round 2 reproducer: was 5e16 × amplitude)
  ---
  duration_ms: 1174.824216
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 201 - (D″) DS+G regression: centre −10 eV on the low-BE side, 201 points at 0.05 eV, m 0.001
  ---
  duration_ms: 1148.973582
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 202 - (D″) DS+G regression: centre just outside the padded grid (6.5 eV, pad 1 eV)
  ---
  duration_ms: 1204.387031
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 203 - (D″) DS+G regression: centre just inside the padded grid (5.999 eV, pad 1 eV)
  ---
  duration_ms: 1202.96846
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 204 - (D″) DS+G regression: a 2-point grid
  ---
  duration_ms: 1271.492567
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 205 - (D″) DS+G regression: a 1-point grid
  ---
  duration_ms: 1185.248507
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 206 - (D″) DS+G at m = 0.001 on a 0.1 eV grid: page equals server (both an all-zero curve — the server kernel underflows; known server limit)
  ---
  duration_ms: 1277.3976
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:471:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 207 - (D″) DS+G at m = 0.002 on a 0.1 eV grid: page equals server (both an all-zero curve — the server kernel underflows; known server limit)
  ---
  duration_ms: 1213.208493
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:471:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 208 - (D″) DS+G at m = 0.02 on a 0.1 eV grid: page equals server
  ---
  duration_ms: 1281.011188
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:471:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 209 - (D″) DS+G at m = 0.05 on a 0.1 eV grid: page equals server
  ---
  duration_ms: 1178.902534
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:471:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
--
not ok 210 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Gaussian
  ---
  duration_ms: 1525.473412
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:122:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 211 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
  ---
  duration_ms: 1279.709627
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:122:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 212 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
  ---
  duration_ms: 1285.353143
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:122:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 213 - page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
  ---
  duration_ms: 1291.252173
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:122:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 214 - page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
  ---
  duration_ms: 1318.26277
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:122:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 215 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
  ---
  duration_ms: 1277.296351
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:122:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 216 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA
  ---
  duration_ms: 1270.378104
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:122:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 217 - page → server → page: what the page draws after applying the result IS the curve the server fitted — LACX # TODO LACX: the page sends m FREE and draws it rounded to an integer kernel (laTrueCasaXPS_array) — the caM clamp unit
  ---
  duration_ms: 1236.548375
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:122:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 218 - Voigt is the fixed 50/50 mix on both sides (A03): request, server parameter, page write-back, drawn curve
  ---
  duration_ms: 1246.684825
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:131:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 219 - a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
  ---
  duration_ms: 1268.920986
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:146:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 220 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 0 locked
  ---
  duration_ms: 1243.919526
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 221 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 100 locked
  ---
  duration_ms: 1321.346729
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 222 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 0 locked
  ---
  duration_ms: 1400.330934
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 223 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 100 locked
  ---
  duration_ms: 1276.557547
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 224 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 0 locked
  ---
  duration_ms: 1267.929668
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 225 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 1 locked
  ---
  duration_ms: 1234.935379
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 226 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0 locked
  ---
  duration_ms: 1382.271765
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 227 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0.5 locked
  ---
  duration_ms: 1274.269101
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 228 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 0 locked
  ---
  duration_ms: 1264.844166
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 229 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 5 locked
  ---
  duration_ms: 1262.059062
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 230 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0 locked (delta kernel)
  ---
  duration_ms: 1290.378424
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 231 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.49 locked (delta kernel)
  ---
  duration_ms: 1280.137458
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 232 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 0.05 locked (delta kernel)
  ---
  duration_ms: 1220.699334
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 233 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 2 locked (delta kernel)
  ---
  duration_ms: 1328.404079
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 234 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 0.1 locked (m = 0)
  ---
  duration_ms: 1268.732588
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 235 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 5 locked (m = 0)
  ---
  duration_ms: 1206.456716
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 236 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 0.1 locked (m = 0)
  ---
  duration_ms: 1270.619791
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 237 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 5 locked (m = 0)
  ---
  duration_ms: 1270.575721
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 238 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.5 locked (delta kernel; both evaluators clip to 0.495)
  ---
  duration_ms: 1267.669374
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 239 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 0.05 locked
  ---
  duration_ms: 1200.294254
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 240 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 4 locked
  ---
  duration_ms: 1340.723745
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 241 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA m 499 locked (request and hold only)
  ---
  duration_ms: 1359.261615
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 242 - a locked GL mix is sent locked, held by the server and drawn at the locked value
  ---
  duration_ms: 1310.295545
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:213:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 243 - autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
  ---
  duration_ms: 1347.122457
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:224:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 244 - autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
  ---
  duration_ms: 1267.454907
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:242:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
--
not ok 269 - server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
  ---
  duration_ms: 1666.027116
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/local_lm_descent.test.js:455:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/local_lm_server_parity_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/local_lm_server_parity_backend.py", line 12, in <module>
        import fitting  # noqa: E402

codex
1. **MAJOR — Find Peaks leaves the new warnings stale.** [templates/index.html:9572](/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/templates/index.html:9572) refreshes warnings through `updatePlot`, but `_fpSyncSelectionUI` writes both ROI fields at lines 15496–15497 without calling it. Reproduced: data 280–295, initially matching ROI, then select a region suggesting 278–298. The fields change, `_roiWindowStatus()` returns `past`, but the hint remains hidden. Closing the modal also does not refresh it. Centre badges can likewise remain stale. This directly contradicts plan §2, row 5.

2. **MAJOR — The claimed identical manual-fit/Find Peaks window is false.** [Plan:63](/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md:63) misses `uploadToBackend`’s `toFixed(4)` at [templates/index.html:6397](/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/templates/index.html:6397). Manual fit filters **before** upload rounding; Find Peaks filters **after** it. Concrete counterexample: 20 energies `280.00004 + i×0.1`, ROI 280.00002–282.5. Manual selection contains 20 points; Find Peaks contains 19 and rejects the request. The hint nevertheless describes the manual selection. This transport discrepancy predates the branch, but invalidates its new assurance and claimed verification.

3. **MAJOR — The badge exposes an unsupported component’s suppressed centre.** [templates/index.html:5134](/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/templates/index.html:5134) always includes the numeric centre; the patcher never checks `_isUnsupported`. Reproduced with a current unsupported verdict, centre 296, selected data 280–295: the card’s centre is suppressed, but the new tooltip reports “Centre 296.00 eV”. Respect the existing suppression rule, including linked children. The changed unsupported-component test stubs out this patcher, so its passing suppression assertion misses the regression.

4. **MINOR — Closing the last spectrum preserves its clipping hint.** [templates/index.html:9572](/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/templates/index.html:9572) is bypassed when `closeTab` calls `renderEmptyChart` directly at line 3311. Close the only tab while its clipping hint is visible: the page says “no data” but still names the closed spectrum’s clipped window. The empty-data early return in `updatePlot` also bypasses clearing.

The warning-only interpretation of “clamp” is reasonable. I found no diff changing ROI fields, peak values, fitting payloads, saves, or `_STARTS_UI_FIELDS`.

Validation: 34 focused JS tests passed; all 9 component-required Python tests passed. The full JS run had 325 passes, 78 Python-backed failures under the sandbox, and 5 TODOs. Holding the anchor stabilizes the constructed premise, but does not reproduce the original freely fitted local minimum; one passing run does not establish absence of flakiness.

**VERDICT: NO-GO**
tokens used
107,568
1. **MAJOR — Find Peaks leaves the new warnings stale.** [templates/index.html:9572](/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/templates/index.html:9572) refreshes warnings through `updatePlot`, but `_fpSyncSelectionUI` writes both ROI fields at lines 15496–15497 without calling it. Reproduced: data 280–295, initially matching ROI, then select a region suggesting 278–298. The fields change, `_roiWindowStatus()` returns `past`, but the hint remains hidden. Closing the modal also does not refresh it. Centre badges can likewise remain stale. This directly contradicts plan §2, row 5.

2. **MAJOR — The claimed identical manual-fit/Find Peaks window is false.** [Plan:63](/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md:63) misses `uploadToBackend`’s `toFixed(4)` at [templates/index.html:6397](/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/templates/index.html:6397). Manual fit filters **before** upload rounding; Find Peaks filters **after** it. Concrete counterexample: 20 energies `280.00004 + i×0.1`, ROI 280.00002–282.5. Manual selection contains 20 points; Find Peaks contains 19 and rejects the request. The hint nevertheless describes the manual selection. This transport discrepancy predates the branch, but invalidates its new assurance and claimed verification.

3. **MAJOR — The badge exposes an unsupported component’s suppressed centre.** [templates/index.html:5134](/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/templates/index.html:5134) always includes the numeric centre; the patcher never checks `_isUnsupported`. Reproduced with a current unsupported verdict, centre 296, selected data 280–295: the card’s centre is suppressed, but the new tooltip reports “Centre 296.00 eV”. Respect the existing suppression rule, including linked children. The changed unsupported-component test stubs out this patcher, so its passing suppression assertion misses the regression.

4. **MINOR — Closing the last spectrum preserves its clipping hint.** [templates/index.html:9572](/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/templates/index.html:9572) is bypassed when `closeTab` calls `renderEmptyChart` directly at line 3311. Close the only tab while its clipping hint is visible: the page says “no data” but still names the closed spectrum’s clipped window. The empty-data early return in `updatePlot` also bypasses clearing.

The warning-only interpretation of “clamp” is reasonable. I found no diff changing ROI fields, peak values, fitting payloads, saves, or `_STARTS_UI_FIELDS`.

Validation: 34 focused JS tests passed; all 9 component-required Python tests passed. The full JS run had 325 passes, 78 Python-backed failures under the sandbox, and 5 TODOs. Holding the anchor stabilizes the constructed premise, but does not reproduce the original freely fitted local minimum; one passing run does not establish absence of flakiness.

**VERDICT: NO-GO**
