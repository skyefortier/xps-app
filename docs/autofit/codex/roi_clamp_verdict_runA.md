OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0d97a-a4c2-79e2-af0f-d125f2db93c1
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
I’ll read the plan first, then trace the diff and its callers for stale warnings, window mismatches, and weakened tests. I’ll finish with ranked, concrete findings and a verdict.

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
/bin/zsh -lc 'git status --short && git diff --stat main..HEAD && rg --files -g AGENTS.md -g CLAUDE.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-APlzrECD' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-2S2doGPv' (errno=Operation not permitted)
?? docs/autofit/codex/roi_clamp_review_prompt.txt
?? docs/autofit/codex/roi_clamp_verdict_runA.md
?? docs/autofit/codex/roi_clamp_verdict_runB.md
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-V5wc31tc' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-fGzoGzEi' (errno=Operation not permitted)
 CLAUDE.md                                          |  11 ++
 .../2026-09-25-roi-clamp-and-centre-warning.md     | 138 +++++++++++++++++++++
 templates/index.html                               | 101 ++++++++++++++-
 tests/js/roi_clamp_centre_warning.test.js          | 135 ++++++++++++++++++++
 tests/js/unsupported_components.test.js            |   1 +
 tests/test_component_required.py                   |  31 +++--
 6 files changed, 406 insertions(+), 11 deletions(-)
CLAUDE.md

exec
/bin/zsh -lc "cat CLAUDE.md && rg -n 'roi-min|roi-max|roiMin|roiMax|getROIData|be_min|be_max|_patchPeakCardsForSupport|updatePeakParam|renderPeakList|_validate_analyze_request' templates/index.html app.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
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
app.py:207:    assembled once by _validate_analyze_request."""
app.py:220:def _validate_analyze_request(body: dict, upload_folder: str) -> _AnalyzeContext:
app.py:265:        be_min = float(roi.get("be_min", float(corrected.min())))
app.py:266:        be_max = float(roi.get("be_max", float(corrected.max())))
app.py:268:        raise _AnalyzeError("roi.be_min/be_max must be numbers")
app.py:269:    mask = (corrected >= be_min) & (corrected <= be_max)
app.py:911:          "roi":            {"be_min": ..., "be_max": ...},   // corrected frame
app.py:931:        ``_validate_analyze_request``/``_run_analyze_method``/
app.py:939:            ctx = _validate_analyze_request(body, app.config["UPLOAD_FOLDER"])
app.py:979:            ctx = _validate_analyze_request(body, upload_folder)
templates/index.html:2064:                <input type="number" id="roi-min" value="706" step="0.5" oninput="updatePlot();_recomputeAutoFitMenuState()">
templates/index.html:2068:                <input type="number" id="roi-max" value="726" step="0.5" oninput="updatePlot();_recomputeAutoFitMenuState()">
templates/index.html:2459:  renderPeakList();
templates/index.html:2475:  renderPeakList();
templates/index.html:3177:        roiMin: minBE, roiMax: maxBE,
templates/index.html:3210:            endpointAvg: '1', roiMin: '', roiMax: '',
templates/index.html:3262:    renderPeakList();
templates/index.html:3310:      renderPeakList();
templates/index.html:3395:        min: document.getElementById('roi-min').value,
templates/index.html:3396:        max: document.getElementById('roi-max').value
templates/index.html:3465:        active.ui.roiMin = data.roi.min || '';
templates/index.html:3466:        active.ui.roiMax = data.roi.max || '';
templates/index.html:3479:      renderPeakList();
templates/index.html:3831:      roiMin:      document.getElementById('roi-min')?.value || '',
templates/index.html:3832:      roiMax:      document.getElementById('roi-max')?.value || '',
templates/index.html:3851:    set('roi-min', ui.roiMin);
templates/index.html:3852:    set('roi-max', ui.roiMax);
templates/index.html:4652:// rule getROIData uses for the ROI. This is the single definition shared by
templates/index.html:4994:    const roiMinEl = document.getElementById('roi-min');
templates/index.html:4995:    const roiMaxEl = document.getElementById('roi-max');
templates/index.html:4996:    const roiMinVal = parseFloat(roiMinEl.value);
templates/index.html:4997:    const roiMaxVal = parseFloat(roiMaxEl.value);
templates/index.html:4998:    if (!isNaN(roiMinVal)) roiMinEl.value = (roiMinVal - delta).toFixed(1);
templates/index.html:4999:    if (!isNaN(roiMaxVal)) roiMaxEl.value = (roiMaxVal - delta).toFixed(1);
templates/index.html:5036:  // stale isChargeReference flags are cleared by renderPeakList).
templates/index.html:5037:  renderPeakList();
templates/index.html:5044:  // already works around). renderPeakList/_refOnTabChange only refresh panel/legend
templates/index.html:5061:function getROIData() {
templates/index.html:5062:  const roiMinRaw = parseFloat(document.getElementById('roi-min').value);
templates/index.html:5063:  const roiMaxRaw = parseFloat(document.getElementById('roi-max').value);
templates/index.html:5065:  const roiMin = isNaN(roiMinRaw) ? -Infinity : roiMinRaw;
templates/index.html:5066:  const roiMax = isNaN(roiMaxRaw) ?  Infinity : roiMaxRaw;
templates/index.html:5070:    if (corrBE[i] >= roiMin && corrBE[i] <= roiMax) {
templates/index.html:5079:// WARN, NEVER REINTERPRET. getROIData() already selects the corrected
templates/index.html:5080:// energies inside [roi-min, roi-max], so an ROI past the data is clamped to
templates/index.html:5092:  const lo = parseFloat(document.getElementById('roi-min').value);
templates/index.html:5093:  const hi = parseFloat(document.getElementById('roi-max').value);
templates/index.html:5094:  const { be } = getROIData();
templates/index.html:5167:  document.getElementById('roi-min').value = lo.toFixed(1);
templates/index.html:5168:  document.getElementById('roi-max').value = hi.toFixed(1);
templates/index.html:5178:  document.getElementById('roi-min').value = _roiLo.toFixed(1);
templates/index.html:5179:  document.getElementById('roi-max').value = _roiHi.toFixed(1);
templates/index.html:5215:  renderPeakList();
templates/index.html:5442:  const roiMin = parseFloat(document.getElementById('roi-min').value);
templates/index.html:5443:  const roiMax = parseFloat(document.getElementById('roi-max').value);
templates/index.html:5444:  if (isNaN(roiMin) || isNaN(roiMax)) return;
templates/index.html:5445:  const xMin = Math.min(roiMin, roiMax);
templates/index.html:5446:  const xMax = Math.max(roiMin, roiMax);
templates/index.html:5568:  const roiMin = parseFloat(document.getElementById('bg-end')?.value || 0);
templates/index.html:5569:  const roiMax = parseFloat(document.getElementById('bg-start')?.value || 9999);
templates/index.html:5570:  const beMin = Math.min(roiMin, roiMax);
templates/index.html:5571:  const beMax = Math.max(roiMin, roiMax);
templates/index.html:5766:  const { be, inten } = getROIData();
templates/index.html:5824:    renderPeakList();
templates/index.html:5890:  renderPeakList();
templates/index.html:5907:  renderPeakList();
templates/index.html:5919:  renderPeakList();
templates/index.html:5930:  renderPeakList();
templates/index.html:5942:  renderPeakList();
templates/index.html:5961:  updatePeakParam(id, 'amplitude', child.amplitude);
templates/index.html:5964:function updatePeakParam(id, key, value) {
templates/index.html:6040:  renderPeakList();
templates/index.html:6086:function renderPeakList() {
templates/index.html:6105:  const { be: _roiBE } = (typeof getROIData === 'function' && state.rawBE.length) ? getROIData() : { be: [] };
templates/index.html:6156:      <input type="text" value="${_escAttr(p.name)}" oninput="updatePeakParam(${p.id},'name',this.value);document.querySelector('#peak-item-${p.id} .peak-name').childNodes[0].textContent=this.value">
templates/index.html:6193:          oninput="updatePeakParam(${p.id},'center',parseFloat(this.value));_patchPeakCardsForSupport()">
templates/index.html:6200:          ${p.shape === 'DSG_LA' ? 'readonly ' : ''}oninput="updatePeakParam(${p.id},'fwhm',parseFloat(this.value))">
templates/index.html:6209:        oninput="updatePeakParam(${p.id},'amplitude',parseFloat(this.value))">
templates/index.html:6221:          oninput="getPeak(${p.id}).linkOffset=parseFloat(this.value);getPeak(${p.id}).center=getPeak(${p.linked}).center+parseFloat(this.value);updatePeakParam(${p.id},'center',getPeak(${p.id}).center)">
templates/index.html:6242:          oninput="updatePeakParam(${p.id},'asymmetry',parseFloat(this.value))">
templates/index.html:6248:            oninput="updatePeakParam(${p.id},'glMix',parseFloat(this.value));document.getElementById('glmix-${p.id}').textContent=this.value+'%'">
templates/index.html:6260:            oninput="updatePeakParam(${p.id},'glMix',parseFloat(this.value));document.getElementById('glmix-${p.id}').textContent=this.value+'%'">
templates/index.html:6273:          oninput="updatePeakParam(${p.id},'dsAlpha',parseFloat(this.value))">
templates/index.html:6280:          oninput="updatePeakParam(${p.id},'dsGamma',parseFloat(this.value))">
templates/index.html:6294:            oninput="updatePeakParam(${p.id},'laAlpha',parseFloat(this.value))">
templates/index.html:6301:            oninput="updatePeakParam(${p.id},'laBeta',parseFloat(this.value))">
templates/index.html:6309:          oninput="updatePeakParam(${p.id},'laM',parseFloat(this.value))">
templates/index.html:6323:            oninput="updatePeakParam(${p.id},'caAlpha',parseFloat(this.value))">
templates/index.html:6330:            oninput="updatePeakParam(${p.id},'caBeta',parseFloat(this.value))">
templates/index.html:6338:          oninput="updatePeakParam(${p.id},'caM',parseFloat(this.value))">
templates/index.html:6961:    roiMinDom:    document.getElementById('roi-min')?.value || '',
templates/index.html:6962:    roiMaxDom:    document.getElementById('roi-max')?.value || '',
templates/index.html:6998:      roiMin: snap.roiMinDom, roiMax: snap.roiMaxDom,
templates/index.html:7018:  set('roi-min',   snap.roiMinDom);
templates/index.html:7019:  set('roi-max',   snap.roiMaxDom);
templates/index.html:7027:  if (typeof renderPeakList === 'function') renderPeakList();
templates/index.html:7206:function _patchPeakCardsForSupport() {
templates/index.html:7208:  // area % over the components the CURRENT verdicts support (as renderPeakList computes it)
templates/index.html:7209:  const { be: roiBE } = (typeof getROIData === 'function' && state.rawBE && state.rawBE.length) ? getROIData() : { be: [] };
templates/index.html:7306:  const { be: be2, inten: inten2 } = getROIData();
templates/index.html:7345:  if (typeof renderPeakList === 'function') renderPeakList();
templates/index.html:7396:  const { be: corrBE, inten } = getROIData();
templates/index.html:7398:    notify('ROI is empty. Set roi-min and roi-max before auto-fit.', 'red', true);
templates/index.html:7435:  renderPeakList();
templates/index.html:7448:    const { be: be2, inten: inten2 } = getROIData();
templates/index.html:7541:  let lo = parseFloat(ui.roiMin);
templates/index.html:7542:  let hi = parseFloat(ui.roiMax);
templates/index.html:7588:const _STARTS_UI_FIELDS = ['bgType', 'bgStart', 'bgEnd', 'shirleyIter', 'endpointAvg', 'roiMin', 'roiMax'];
templates/index.html:7628:  if (shownIn('#peak-list .unsupported-badge') !== flaggedNow) { _patchPeakCardsForSupport(); rendered = true; }
templates/index.html:7823:  const { be, inten } = getROIData();
templates/index.html:7992:  renderPeakList();
templates/index.html:8482:  renderPeakList();
templates/index.html:8601:  // grid, exactly as renderPeakList already does for its area/percentage column.
templates/index.html:8603:  if ((!be || !be.length) && typeof getROIData === 'function' && state.rawBE.length) {
templates/index.html:8604:    be = getROIData().be;
templates/index.html:8923://       by ROI-filtering corrBE using src.ui.roiMin/roiMax, recompute
templates/index.html:8971:    // Path B: post-load — derive ROI-window be from rawBE + ui.roiMin/Max,
templates/index.html:8974:    const roiMinV = parseFloat(src.ui && src.ui.roiMin);
templates/index.html:8975:    const roiMaxV = parseFloat(src.ui && src.ui.roiMax);
templates/index.html:8977:    if (isFinite(roiMinV) && isFinite(roiMaxV)) {
templates/index.html:8978:      const lo = Math.min(roiMinV, roiMaxV);
templates/index.html:8979:      const hi = Math.max(roiMinV, roiMaxV);
templates/index.html:9432:  const { be, inten } = getROIData();
templates/index.html:10161:      min: document.getElementById('roi-min').value,
templates/index.html:10162:      max: document.getElementById('roi-max').value
templates/index.html:10197:  const { be, inten } = getROIData();
templates/index.html:10555:  renderPeakList();
templates/index.html:10681:              endpointAvg: '1', roiMin: '', roiMax: '',
templates/index.html:10706:        shirleyIter: '5', roiMin: '', roiMax: '',
templates/index.html:10866:  const { be, inten } = getROIData();
templates/index.html:10923:  const { be, inten } = getROIData();
templates/index.html:12077:      renderPeakList();
templates/index.html:12093:    const roiSt = _roiWindowStatus();    // warn only: the fit below uses getROIData() exactly as before
templates/index.html:12094:    const { be, inten } = getROIData();
templates/index.html:14020:  renderPeakList();
templates/index.html:15496:    document.getElementById('roi-min').value = entries[0].roi.be_min;
templates/index.html:15497:    document.getElementById('roi-max').value = entries[0].roi.be_max;
templates/index.html:15714:      roi: { be_min: parseFloat(document.getElementById('roi-min').value),
templates/index.html:15715:             be_max: parseFloat(document.getElementById('roi-max').value) },
templates/index.html:15999:  // unfit-preview path (getROIData() + client-side computeBackground()),
templates/index.html:16001:  // CURRENT #roi-min/#roi-max, i.e., the full window Find Peaks just used.
templates/index.html:16032:  renderPeakList();

exec
/bin/zsh -lc 'git diff main..HEAD -- templates/index.html tests/js/roi_clamp_centre_warning.test.js tests/js/unsupported_components.test.js tests/test_component_required.py CLAUDE.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-0Ax4FfnH' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-pRyiYody' (errno=Operation not permitted)
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
/bin/zsh -lc "sed -n '5940,6150p' templates/index.html; sed -n '7180,7265p' templates/index.html; sed -n '7580,7650p' templates/index.html; sed -n '9405,9455p' templates/index.html; sed -n '15465,15520p' templates/index.html; sed -n '220,283p' app.py; git diff main..HEAD -- tests/test_component_required.py tests/js/unsupported_components.test.js" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
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

function applyAutoFitResult(json, graphiteRaw, roi) {
  // 1. Locate the graphite peak in state.peaks (named "Graphite").
  const gPeak = state.peaks.find(p => p.name === 'Graphite') || state.peaks[0];
  if (!gPeak || !Number.isFinite(gPeak.center)) {
    notify('Auto-fit failed: graphite center not found in fit result.', 'red', true);
    return false;
  }
  // 1b. The charge correction below is derived from this component's fitted
  // centre and then shifts EVERY binding energy in the spectrum, so the
// anchors or the charge correction — or an undo / history restore that brings
// back other values — the panel says the comparison no longer applies,
// nothing can be previewed or applied, and saves/exports carry no counts. A
// name, colour or visibility is not part of a fit and does not invalidate it.
const _STARTS_MODEL_FIELDS = ['id', 'shape', 'center', 'fwhm', 'amplitude', 'glMix', 'asymmetry', 'dsAlpha', 'dsGamma',
  'laAlpha', 'laBeta', 'laM', 'caAlpha', 'caBeta', 'caM', 'linked', 'linkOffset', 'linkRatio', '_afAsymMin', '_afAsymMax',
  'fixCenter', 'fixFwhm', 'fixAmplitude', 'fixGlMix', 'fixAsymmetry', 'fixDsAlpha', 'fixDsGamma',
  'fixLaAlpha', 'fixLaBeta', 'fixLaM', 'fixCaAlpha', 'fixCaBeta', 'fixCaM'];
const _STARTS_UI_FIELDS = ['bgType', 'bgStart', 'bgEnd', 'shirleyIter', 'endpointAvg', 'roiMin', 'roiMax'];
function _startsModelKey(peaks, ui, ccShift, anchors) {
  return JSON.stringify({
    p: (peaks || []).map(q => _STARTS_MODEL_FIELDS.map(k => (q[k] === undefined ? null : q[k]))),
    u: _STARTS_UI_FIELDS.map(k => String((ui || {})[k] ?? '')),
    s: Number(ccShift) || 0,
    a: (anchors || []).map(v => [v.x, v.y]),
  });
}
// The key of the ACTIVE tab as it stands now (live model, live controls).
function _startsLiveKey() {
  const ui = (typeof tabManager !== 'undefined' && tabManager && tabManager._captureUI) ? tabManager._captureUI() : {};
  return _startsModelKey(state.peaks, ui, state.ccShift, typeof _getManualAnchors === 'function' ? _getManualAnchors() : []);
}
// The key of a tab RECORD (project save runs after _syncActiveToRecord).
function _startsRecordKey(t) { return _startsModelKey(t.peaks, t.ui, t.ccShift, t.manualAnchors); }
// The starts evidence of `fr` if it still describes the fit whose key is `key`, else null.
function _startsIfCurrent(fr, key) {
  const st = fr && fr.starts;
  if (!st || !fr.startsModelKey || fr.startsModelKey !== key) return null;
  return st;
}
// After anything that may have changed the model or its context without going
// through a Results re-render (a lock toggle, Lock All, a background or ROI
// control): take a stale alternative overlay off the chart and bring the
// VISIBLE panel up to date (counts -> "the model has changed since this fit").
function _refreshStartsEvidence(repaint, fromPlot) {
  const hadAlt = !!(_historyPreview && typeof _historyPreview.snapId === 'string' && _historyPreview.snapId.startsWith('alt:'));
  _dropStaleAltPreview();
  if (repaint && hadAlt && !_historyPreview && typeof updatePlot === 'function') updatePlot();
  // The support verdicts are keyed the same way. If any is now stale (or
  // current again after an undo), every consumer that renders it must follow:
  // the Results table, the Quantify tab and the sidebar cards, not only the
  // starts panel. Rendered once, only when the visible state would change.
  // Each consumer is compared with ITS OWN rendering (a caller may have
  // redrawn the sidebar already, so the sidebar cannot vouch for the tables).
  const key = _startsLiveKey();
  const flaggedNow = state.peaks.filter(p => _isUnsupported(p, key)).map(p => String(p.id)).sort().join(',');
  const shownIn = sel => Array.from(document.querySelectorAll(sel)).map(e => e.getAttribute('data-peak-id')).sort().join(',');
  let rendered = false;
  if (shownIn('#peak-list .unsupported-badge') !== flaggedNow) { _patchPeakCardsForSupport(); rendered = true; }
  if (state.fitResult && shownIn('.results-table .unsupported-row') !== flaggedNow && typeof renderResults === 'function') { renderResults(); rendered = true; }   // renders Quantify and the starts panel too
  if (!fromPlot && state.chart && state.chart.data && typeof updatePlot === 'function') {
    const chartFlagged = (state.chart.data.datasets || []).filter(d => d._unsupported).map(d => String(d._peakId)).sort().join(',');
    if (chartFlagged !== flaggedNow) { updatePlot(); return; }
  }
  if (rendered) return;
  const el = document.querySelector('.starts-panel');
  if (el && state.fitResult) el.outerHTML = _startsPanelHtml(state.fitResult);
}

// An alternative's preview overlay is only valid beside the result it came from.
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
  // changing ROI never re-draws or recomputes the fit, background, or peaks.
  const haveFit = !!(state.fitResult && Array.isArray(state.fitResult.be) &&
                     state.fitResult.be.length > 0 &&
                     Array.isArray(state.fitResult.bgIntensity) &&
                     state.fitResult.bgIntensity.length === state.fitResult.be.length);

  // plotBE/plotBG/plotInten drive all fit-related curves (peaks, background, envelope).
  // When a fit exists, they come from the frozen fit state — ROI changes don't affect them.
  // Before fitting, they come from the current ROI so live peak previews still work.
  const plotBE = haveFit ? state.fitResult.be : be;
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
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-VIRH0BaU' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-EBYA7BQV' (errno=Operation not permitted)
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
 
 

codex
The ROI masks match for finite numeric bounds, and the diff leaves fitting inputs unchanged. I found a likely refresh gap: Find Peaks’ region picker writes both ROI fields without calling `updatePlot`. I’m tracing that path and checking whether the new badge exposes centres that the unsupported-component UI suppresses.

exec
/bin/zsh -lc "sed -n '15530,15750p' templates/index.html; sed -n '3190,3335p' templates/index.html; sed -n '6990,7040p' templates/index.html; sed -n '5158,5195p' templates/index.html; cat tests/test_component_required.py; rg -n 'F >=|\\[\"f\"\\]|\\[.supported.\\].*True|default_rng|random.seed' tests/test_component* tests/test_*anchor*; rg -n '"'^#|must|MUST|review'"' CLAUDE.md | head -70; rg -n 'function _fpRenderPtGrid|function _fpRenderExpandedPanel|_fpSyncSelectionUI|function renderEmptyChart|function _escAttr|function _fpEnsureSession' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
  const strs = FP_STRINGS.methods[id] || {};
  document.getElementById('fp-method-hint').textContent = strs.hint || '';
  // the Advanced JSON stays the single source of truth for the request —
  // the friendly controls below are a labeled VIEW that writes into it.
  // endpoint_avg is the exception: its source is the Background panel
  // (runFindPeaks injects the panel value unless the JSON names one), so
  // the advertised default of 1 is NOT written here — it would silently
  // shadow the panel (Find Peaks honours the panel, 2026-09-08).
  const shown = { ...((m && m.default_options) || {}) };
  delete shown.endpoint_avg;
  document.getElementById('fp-options').value = JSON.stringify(shown, null, 1);
  _fpBuildSimpleControls(id);
}

function _fpBuildSimpleControls(methodId) {
  const host = document.getElementById('fp-simple-options');
  const defs = FP_STRINGS.controls[methodId] || [];
  host.innerHTML = '';
  if (!defs.length) {
    const p = document.createElement('div');
    p.style.cssText = 'font-size:10px;color:var(--text3)';
    p.textContent = FP_STRINGS.controls._none;
    host.appendChild(p);
    return;
  }
  let opts = {};
  try { opts = JSON.parse(document.getElementById('fp-options').value || '{}'); }
  catch (e) { opts = {}; }
  for (const def of defs) {
    const row = document.createElement('label');
    row.style.cssText = 'display:flex;align-items:center;gap:6px;' +
      'font-size:11px;margin:3px 0';
    row.title = def.tip;
    let input;
    if (def.type === 'checkbox') {
      input = document.createElement('input');
      input.type = 'checkbox';
      input.checked = !!opts[def.key];
    } else if (def.type === 'select') {
      input = document.createElement('select');
      input.className = 'btn';
      for (const [v, text] of def.choices) {
        const o = document.createElement('option');
        o.value = v; o.textContent = text;
        input.appendChild(o);
      }
      if (opts[def.key] != null) input.value = String(opts[def.key]);
    } else {
      input = document.createElement('input');
      input.type = 'number';
      input.min = def.min; input.max = def.max; input.step = def.step;
      input.style.cssText = 'width:72px;font-size:11px;background:var(--bg2);' +
        'color:var(--text1);border:1px solid var(--border);padding:2px 4px';
      if (opts[def.key] != null) input.value = opts[def.key];
    }
    input.id = 'fp-opt-' + def.key;
    input.addEventListener('change', () => _fpSyncOptionsFromControls(methodId));
    const span = document.createElement('span');
    span.textContent = def.label;
    if (def.type === 'checkbox') { row.appendChild(input); row.appendChild(span); }
    else { row.appendChild(span); row.appendChild(input); }
    host.appendChild(row);
  }
}

function _fpSyncOptionsFromControls(methodId) {
  // controls write INTO the JSON (unknown/advanced keys preserved) — the
  // request path is unchanged; this is purely a friendlier way to edit it
  let opts = {};
  try { opts = JSON.parse(document.getElementById('fp-options').value || '{}'); }
  catch (e) { opts = {}; }
  for (const def of (FP_STRINGS.controls[methodId] || [])) {
    const el = document.getElementById('fp-opt-' + def.key);
    if (!el) continue;
    if (def.type === 'checkbox') opts[def.key] = el.checked;
    else if (def.type === 'select') opts[def.key] = el.value;
    else if (el.value !== '') opts[def.key] = Number(el.value);
  }
  document.getElementById('fp-options').value = JSON.stringify(opts, null, 1);
}

// ── Progress indicator (2026-07-11): pure formatting helpers ───────────────
// Kept DOM-free/pure so they're directly unit-testable (extracted the same
// way other pure logic in this file is — see tests/js/).

function _fpFormatElapsed(sec) {
  const s = Math.max(0, Math.round(Number(sec) || 0));
  if (s < 60) return s + 's';
  const m = Math.floor(s / 60), r = s % 60;
  return m + 'm ' + r + 's';
}

// One poll payload -> the on-screen status line. `poll` is the JSON from
// GET /api/analyze/progress/<job_id> — real engine state (candidate N of
// M, screening/stabilizing), never a fake animation.
function _fpProgressText(poll) {
  const elapsed = _fpFormatElapsed(poll && poll.elapsed_sec);
  const msg = (poll && poll.message) || 'working…';
  return 'Analyzing… ' + elapsed + ' — ' + msg;
}

const FP_POLL_INTERVAL_MS = 350;
// Client-side watchdog: the actual analysis has its own server-side budget
// (TOTAL_ANALYSIS_TIMEOUT_SEC, well under this), so this only fires if a
// job's progress file stops updating entirely (e.g. a recycled gunicorn
// worker process taking the background thread down with it) — the
// indicator must NEVER spin forever even in that pathological case.
const FP_POLL_WATCHDOG_SEC = 600;

async function _fpPollJob(jobId) {
  const started = Date.now();
  while (true) {
    const resp = await fetch('/api/analyze/progress/' + encodeURIComponent(jobId));
    if (!resp.ok) {
      throw new Error('Lost the progress channel (HTTP ' + resp.status + ').');
    }
    const poll = await resp.json();
    document.getElementById('fp-status').textContent = _fpProgressText(poll);
    if (poll.status === 'done') return poll;
    if (poll.status === 'error') {
      throw new Error(poll.error || 'Analysis failed.');
    }
    if ((Date.now() - started) / 1000 > FP_POLL_WATCHDOG_SEC) {
      throw new Error('This is taking unusually long — the analysis may ' +
        'have been lost. Try again.');
    }
    await new Promise(r => setTimeout(r, FP_POLL_INTERVAL_MS));
  }
}

async function runFindPeaks() {
  const status = document.getElementById('fp-status');
  const spinner = document.getElementById('fp-spinner');
  const btn = document.getElementById('fp-run');
  // The full preserved selection, NOT anything scraped from the DOM — a
  // co-fit member filtered/collapsed out of view by the search box or the
  // periodic-table picker would be invisible to the DOM but must still be
  // submitted (see _fpToggleRegion / _fpSyncSelectionUI).
  const regions = Array.from(_fpRegionsSelected);
  if (!regions.length) { status.textContent = 'Select at least one region.'; return; }
  let options;
  try {
    options = JSON.parse(document.getElementById('fp-options').value || '{}');
  } catch (e) { status.textContent = 'Options are not valid JSON.'; return; }
  const method = document.getElementById('fp-method').value;
  // Endpoint averaging: the Background panel is the source for every method
  // that fits a background (its /api/analyze/meta default_options advertise
  // endpoint_avg — all four menu methods do); an explicit value in the
  // Advanced JSON wins. Methods that do not advertise it are not sent it
  // (their option whitelists would reject the key). The value actually
  // sent is recorded on the tab's findPeaks.last so applyFindPeaks keeps preview == fit.
  const fpMethodMeta = ((_fpMeta && _fpMeta.methods) || []).find(x => x.id === method);
  const methodTakesEp = !!(fpMethodMeta && fpMethodMeta.default_options
                           && Object.prototype.hasOwnProperty.call(fpMethodMeta.default_options, 'endpoint_avg'));
  if (methodTakesEp && options.endpoint_avg === undefined) {
    options.endpoint_avg = parseInt(document.getElementById('bg-endpoint-avg')?.value) || 1;
  }
  // Strict, mirroring the backend's pop_endpoint_avg: a JSON number that is
  // a whole number >= 1. Anything else (a string like "1_0" that Python would
  // coerce to 10, a boolean, a fraction) is refused HERE, before any request,
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
    return tab;
  }

  createStackTab() {
    const id = 'tab_' + Math.random().toString(36).slice(2, 9);
    const tab = {
      id,
      name: '▦ Stack ' + (_nextStackNum++),
      color: '#7a7a7a',           // inert — stack tabs render no dot
      isStack: true,
      entries: [],
      _nextColorIdx: 0,
      lineWidth: 1.5,
      verticalOffset: 0,
      // Inert spectrum-tab fields kept to satisfy existing lifecycle code paths.
      isSurvey: false, chargeVerified: true,
      rawBE: [], rawIntensity: [], ccShift: 0,
      peaks: [], nextId: 1, fitResult: null,
      markedElements: [], notes: '', sourcePath: null,
      ui: { bgType: 'shirley', bgStart: '', bgEnd: '', shirleyIter: '5',
            endpointAvg: '1', roiMin: '', roiMax: '',
            ccMethod: 'none', ccObs: '', ccLit: '' },
    };
    this.tabs.push(tab);
    this.activateTab(id);
    return tab;
  }

  activateTab(id) {
    if (this.activeId === id) return;
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
tests/test_component_required.py:77:    assert g["support"]["supported"] is True, "held-others statistic passes: that is the gap"
tests/test_component_required.py:78:    assert g["support"]["f"] > 1e6, g["support"]["f"]           # far from the threshold, not on it
tests/test_component_required.py:86:    rng = np.random.default_rng(0)
tests/test_component_required.py:91:    assert req["ran"] and req["required"] is True and req["f"] > 1000
tests/test_component_required.py:176:    rng = np.random.default_rng(3)
tests/test_component_support.py:32:    rng = np.random.default_rng(3)
tests/test_component_support.py:53:        assert sup["supported"] is True and sup["f"] > 1000
tests/test_component_support.py:65:    assert by["3"]["support"]["delta_chi2"] <= 0 or by["3"]["support"]["f"] < fitting.SUPPORT_MIN_F
tests/test_component_support.py:80:    assert sup["f"] == pytest.approx(f) and sup["delta_chi2"] == pytest.approx(chi_without - chi_with)
tests/test_component_support.py:84:    assert zero["supported"] is False and zero["f"] == 0.0
tests/test_component_support.py:87:    assert exact["supported"] is True and exact["f"] is None       # infinite, serialised as null
tests/test_component_support.py:97:    assert by["3"]["support"]["supported"] == by["2"]["support"]["supported"] is True
tests/test_component_support.py:106:    assert all(ip["support"]["supported"] is True for ip in body["individual_peaks"])
1:# XPS Fitting Studio
9:## Stack
19:## Project Layout
37:## Backend API
49:| `POST`   | `/api/upload`             | Upload a spectrum file; returns `session_id` + downsampled preview. |
51:| `GET`    | `/api/session/<id>`       | Retrieve a stored session's preview data. |
56:## Frontend Architecture
58:### State
76:### Tab model
88:### Peak Object Schema — core fields
107:### Lineshapes
120:**What the page draws must be what the server fitted.** Two harnesses pin
156:## Design Rules
158:### Thresholds on data-scaled quantities fail
177:## Lineshape Physics — Critical Rules
179:### DS (Doniach-Šunjić) Asymmetric Lineshape
181:The DS tail MUST always point toward **higher binding energy** (the left
195:the exponential envelope must decay.
197:### DS+G (formerly mislabeled "LA(α, β, m) [CasaXPS]")
217:were actually being fit against, due to a pre-existing preview/backend
220:### LA(α, β, m) [CasaXPS] — true CasaXPS formulation
248:- `evalPeak` switch + grid-aware `laTrueCasaXPS_array` evaluator (called via `evalPeakArray`; DS+G's grid-aware twin is `dsgConvolved_array` — a convolved shape's scalar `evalPeak` branch ignores m and must have no caller, parity guard (C))
251:### UCl4 U 4f Asymmetric Broadening
261:### Satellite Peaks
266:### Linked (Multiplet) Peaks
269:parameters** from its parent. The sync block must cover every shape
284:## Fitting Algorithm
286:### Backend (default)
355:(in review each such no-op edit moved an area fraction by 15–45 pp
400:second thing (a reviewer tried a deterministic perturbation base: identical
433:the largest move named, amber > 0.5 eV, red > 1 eV) with Preview (the
434:history-preview overlay, on a copy) and "Use this solution": explicit, one
452:the comparison no longer applies, nothing can be previewed or applied, an
453:open alternative preview is dropped (`_dropStaleAltPreview`), and
464:the app must never substitute a chemical interpretation because it scored
473:### Client-side fallback
533:must make the fit significantly worse — `fitting._component_support`, the
613:## Background Methods
622:| `tougaard` | Single-pass universal cross-section K(T) = B·T/(C+T²)², B = 2866 eV², C = 1643 eV² (Tougaard, *Surf. Interface Anal.* **1988**, 11, 453; kernel max at √(C/3) ≈ 23.4 eV). Order-robust (either BE direction); amplitude anchored to the data at the high-BE edge. JS twin `tougaardBackground` must stay in numerical agreement (pinned by `tests/js/tougaard_twin.test.js`). |
628:## Quantification
636:## Charge Correction
647:"Graphite" component, so the data must SUPPORT that component
649:threshold: removing it from the fitted model must make the fit to the
733:## File Formats Supported
746:## Multi-Tab + Project Save/Load
761:## Spectrum Stacking
802:## Toolbar Highlights (frontend)
832:## Tests
842:## Reference Energies for Common Regions
854:## Known Issues
866:## Development Workflow
9902:function renderEmptyChart() {
13940:function _escAttr(s) {
15352:function _fpRenderPtGrid(query) {
15398:function _fpRenderExpandedPanel() {
15481:  _fpSyncSelectionUI();
15484:function _fpSyncSelectionUI() {
15667:  // submitted (see _fpToggleRegion / _fpSyncSelectionUI).

exec
/bin/zsh -lc 'node --test tests/js/roi_clamp_centre_warning.test.js tests/js/unsupported_components.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 166ms:
# Subtest: an ROI inside the data: no hint
ok 1 - an ROI inside the data: no hint
  ---
  duration_ms: 5.925687
  type: 'test'
  ...
# Subtest: an ROI past the data by more than one step: the quiet hint names the window actually used
ok 2 - an ROI past the data by more than one step: the quiet hint names the window actually used
  ---
  duration_ms: 3.0405
  type: 'test'
  ...
# Subtest: one side past the data is enough; the window named is the selected data
ok 3 - one side past the data is enough; the window named is the selected data
  ---
  duration_ms: 2.627559
  type: 'test'
  ...
# Subtest: a sub-step overshoot (a toFixed(1) rounding of the data edge) is not "past the data"
ok 4 - a sub-step overshoot (a toFixed(1) rounding of the data edge) is not "past the data"
  ---
  duration_ms: 2.246227
  type: 'test'
  ...
# Subtest: min above max: amber, no data selected (getROIData selects nothing)
ok 5 - min above max: amber, no data selected (getROIData selects nothing)
  ---
  duration_ms: 3.609105
  type: 'test'
  ...
# Subtest: an ROI that misses the data entirely: amber, names the data range
ok 6 - an ROI that misses the data entirely: amber, names the data range
  ---
  duration_ms: 2.05454
  type: 'test'
  ...
# Subtest: empty fields mean the full range (as getROIData): no hint
ok 7 - empty fields mean the full range (as getROIData): no hint
  ---
  duration_ms: 1.725275
  type: 'test'
  ...
# Subtest: the window is in the CORRECTED frame (raw − ccShift), as the fit and Find Peaks use it
ok 8 - the window is in the CORRECTED frame (raw − ccShift), as the fit and Find Peaks use it
  ---
  duration_ms: 3.173115
  type: 'test'
  ...
# Subtest: a descending acquisition behaves the same
ok 9 - a descending acquisition behaves the same
  ---
  duration_ms: 1.906451
  type: 'test'
  ...
# Subtest: centre outside the SELECTED data is flagged; inside, at the edges, or with no data selected is not
ok 10 - centre outside the SELECTED data is flagged; inside, at the edges, or with no data selected is not
  ---
  duration_ms: 3.663917
  type: 'test'
  ...
# Subtest: the helpers write nothing: no assignment to a field value, a peak or the fit state
ok 11 - the helpers write nothing: no assignment to a field value, a peak or the fit state
  ---
  duration_ms: 1.43885
  type: 'test'
  ...
# Subtest: the fit and Find Peaks still read the ROI exactly as before (getROIData / the two field values)
ok 12 - the fit and Find Peaks still read the ROI exactly as before (getROIData / the two field values)
  ---
  duration_ms: 1.349112
  type: 'test'
  ...
# Subtest: the twin reproduces the server verdict on real responses, and defers to the server field when present
ok 13 - the twin reproduces the server verdict on real responses, and defers to the server field when present
  ---
  duration_ms: 9.521901
  type: 'test'
  ...
# Subtest: _applySupport writes every peak, follows ancestry to the root, stamps the fit key, and leaves null where the response says nothing
ok 14 - _applySupport writes every peak, follows ancestry to the root, stamps the fit key, and leaves null where the response says nothing
  ---
  duration_ms: 4.617823
  type: 'test'
  ...
# Subtest: the verdict applies only to the model and context it was computed for
ok 15 - the verdict applies only to the model and context it was computed for
  ---
  duration_ms: 3.844494
  type: 'test'
  ...
# Subtest: the local engine computes the same statistic from its own residuals
ok 16 - the local engine computes the same statistic from its own residuals
  ---
  duration_ms: 4.954139
  type: 'test'
  ...
# Subtest: sidebar card: badge; centre and width shown as a dash; area % excluded and the others renormalised
ok 17 - sidebar card: badge; centre and width shown as a dash; area % excluded and the others renormalised
  ---
  duration_ms: 5.235797
  type: 'test'
  ...
# Subtest: results table: greyed row, no centre / width / sigma, area kept, percentage dash, and the note beneath
ok 18 - results table: greyed row, no centre / width / sigma, area kept, percentage dash, and the note beneath
  ---
  duration_ms: 12.664333
  type: 'test'
  ...
# Subtest: uncertainty panel: one rule-0 warning for the component, no per-parameter alarms and no "locked" note for it
ok 19 - uncertainty panel: one rule-0 warning for the component, no per-parameter alarms and no "locked" note for it
  ---
  duration_ms: 4.284519
  type: 'test'
  ...
# Subtest: Quantify: excluded from the body, listed beneath with the reason; total and percentages over the rest
ok 20 - Quantify: excluded from the body, listed beneath with the reason; total and percentages over the rest
  ---
  duration_ms: 4.337758
  type: 'test'
  ...
# Subtest: CSV / XLSX export: Status column, suppressed cells, At% empty, WARNING line
ok 21 - CSV / XLSX export: Status column, suppressed cells, At% empty, WARNING line
  ---
  duration_ms: 5.839832
  type: 'test'
  ...
# Subtest: publication figure: no label at the (zero) component, legend entry says so; chart and stack labels say so
ok 22 - publication figure: no label at the (zero) component, legend entry says so; chart and stack labels say so
  ---
  duration_ms: 2.32525
  type: 'test'
  ...
# Subtest: write-back: a server result sets support; the local engine and a propagated model reset it
ok 23 - write-back: a server result sets support; the local engine and a propagated model reset it
  ---
  duration_ms: 2.11591
  type: 'test'
  ...
# Subtest: persistence: support travels with the peak object through every save (the peak is spread whole)
ok 24 - persistence: support travels with the peak object through every save (the peak is spread whole)
  ---
  duration_ms: 0.871058
  type: 'test'
  ...
# Subtest: CSV / XLSX: an unsupported DS+G component exports no width of any kind (beta, m)
ok 25 - CSV / XLSX: an unsupported DS+G component exports no width of any kind (beta, m)
  ---
  duration_ms: 4.913995
  type: 'test'
  ...
# Subtest: the scattered-starts table: an unsupported component shows neither area % nor a move in "Your fit", and is not the largest move
ok 26 - the scattered-starts table: an unsupported component shows neither area % nor a move in "Your fit", and is not the largest move
  ---
  duration_ms: 5.477053
  type: 'test'
  ...
# Subtest: exports: a stale or keyless verdict is "not established", never "supported"
ok 27 - exports: a stale or keyless verdict is "not established", never "supported"
  ---
  duration_ms: 6.969617
  type: 'test'
  ...
# Subtest: Auto-Fit finalisation (locks, charge shift) keeps its own verdicts: _restampSupport, called after the locks
ok 28 - Auto-Fit finalisation (locks, charge shift) keeps its own verdicts: _restampSupport, called after the locks
  ---
  duration_ms: 3.916917
  type: 'test'
  ...
# Subtest: a .fit.json import onto this tab's data carries no verdict
ok 29 - a .fit.json import onto this tab's data carries no verdict
  ---
  duration_ms: 0.124308
  type: 'test'
  ...
# Subtest: _isUnsupported is never handed an array index as its key (Array.filter passes one)
ok 30 - _isUnsupported is never handed an array index as its key (Array.filter passes one)
  ---
  duration_ms: 3.670598
  type: 'test'
  ...
# Subtest: a key change re-renders every consumer of the verdict — each compared with ITS OWN rendering
ok 31 - a key change re-renders every consumer of the verdict — each compared with ITS OWN rendering
  ---
  duration_ms: 2.374955
  type: 'test'
  ...
# Subtest: stack tabs judge a source component against the SOURCE record's key
ok 32 - stack tabs judge a source component against the SOURCE record's key
  ---
  duration_ms: 3.20228
  type: 'test'
  ...
# Subtest: "Your fit" percentages are over supported components; an empty Quantify shows no 100 %
ok 33 - "Your fit" percentages are over supported components; an empty Quantify shows no 100 %
  ---
  duration_ms: 9.564476
  type: 'test'
  ...
# Subtest: the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
ok 34 - the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
  ---
  duration_ms: 4.130921
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
# duration_ms 226.997002

exec
/bin/zsh -lc "rg -n 'function uploadToBackend|def parseCSV|toFixed\\(' templates/index.html | tail -45; sed -n '9900,9940p' templates/index.html; sed -n '3250,3330p' templates/index.html; sed -n '15350,15445p' templates/index.html; sed -n '522,554p' CLAUDE.md; rg -n 'seed|def _component_required|chi2_without_refit' fitting.py; rg --files -g '*python*' -g '*pytest*' -g 'pyvenv.cfg' -g '*requirements*' -g 'package.json' -g '*.proj.json' -g '*.proj.zip' | head -40; command -v python3; ls -d .venv venv 2>/dev/null" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 exited 1 in 0ms:
11313:  const chiStr = state.fitResult.chiReduced.toFixed(4);
11330:      return [p.name, _UNSUPPORTED_LABEL, '', '', '', '', p.amplitude.toFixed(2), '', areas[i].toFixed(2),
11331:              p.shape, sc.gl, sc.alpha, '', '', rsfVals[i].toFixed(4), '', ''];
11334:      p.name, (_currentSupport(p) && _currentSupport(p).supported) ? 'supported' : '', p.center.toFixed(4), cse !== '' ? Number(cse).toFixed(5) : '',
11335:      p.fwhm.toFixed(4), fse !== '' ? Number(fse).toFixed(5) : '',
11336:      p.amplitude.toFixed(2), ase !== '' ? Number(ase).toFixed(3) : '',
11337:      areas[i].toFixed(2), p.shape, sc.gl, sc.alpha,
11339:      rsfVals[i].toFixed(4), normAreas[i].toFixed(4), atPcts[i].toFixed(2)
11352:      ['Charge correction (eV)', state.ccShift.toFixed(3)], []
11365:    csv += `# Charge correction: ${state.ccShift.toFixed(3)} eV\n\n`;
11456:  const pct = rf.rPct.toFixed(1);
11472:  const pct = rf.rPct.toFixed(1);
11546:      warnings.push(`<li><b>${_escHtml(p.name)}:</b> ${_UNSUPPORTED_LABEL} — with the other components held as fitted, removing it does not make the fit significantly worse${p.support.f != null ? ' (F = ' + p.support.f.toFixed(1) + ', threshold 10)' : ''}. Its centre, width and uncertainties are not reported. Try another starting position or width, lock the centre where chemistry says it belongs, or drop the component.</li>`);
12122:    ? `<div class="prop-row">${_escHtml(r.name)}: converged &mdash; &#967;&#178;<sub>r</sub> = ${r.chi != null ? r.chi.toFixed(3) : 'n/a'} (local fit: a starting point, not a reportable result)${roiNote(r)}</div>`
12246:      ? m.state + ' ' + m.be.toFixed(1)
12247:      : (m.sym || m.orbital || '') + ' ' + m.be.toFixed(1);
12878:    _refAddCompoundMarker(sym, el.getAttribute('data-state') || (sym + ' ' + be.toFixed(1)), be, el.getAttribute('data-ref') || '');
12909:  notify('Marked ' + sym + ' ' + be.toFixed(1) + ' eV', 'green');
12924:      ? m.state + ' · ' + idLabel + ' ' + m.be.toFixed(1) + ' eV'
12925:      : idLabel + ' ' + m.be.toFixed(1) + ' eV';
13050:      ? 'KE ' + m.t.auger_ke_ev.toFixed(2) + ' → ' + m.be.toFixed(1) + ' eV'
13051:      : (m.t._legacy ? m.be.toFixed(1) + ' eV' : m.t.nominal_be_ev.toFixed(2) + ' eV');
13054:            ? 'Legacy Auger marker — KE ' + m.t.auger_ke_ev.toFixed(2) + ' eV (' +
13183:    hv.toFixed(1) + ' · φ ' + wf.toFixed(1) + ' eV</span></div>' +
13191:      range.lo.toFixed(1) + '–' + range.hi.toFixed(1) + ' eV (corrected BE)</div>';
13336:          c.fillText('identify ' + ident.be.toFixed(1), px, chartArea.bottom - 4);
13580:            partnerTxt = 'not evaluated (expected near ' + pAt.toFixed(1) +
13584:            partnerTxt = 'elevated signal near ' + pAt.toFixed(1) + ' eV';
13587:            partnerTxt = 'no elevated signal near ' + pAt.toFixed(1) +
13636:    if (clash) a.conflictTxt = 'overlapping ' + clash.label + ' at ' + clash.be.toFixed(1) + ' eV';
13725:  if (lbl) lbl.innerHTML = '&plusmn; ' + ev.toFixed(2) + ' eV';
13774:    '<input type="range" id="ref-tol-range" min="0.25" max="5" step="0.25" value="' + tol.toFixed(2) + '" ' +
13776:    '<span class="ref-ident-tol" id="ref-tol-val">&plusmn; ' + tol.toFixed(2) + ' eV</span></div>';
13795:  html += '<div class="ref-context">Clicked: ' + ident.be.toFixed(2) + ' eV &middot; &plusmn;' +
13796:    ident.tol.toFixed(2) + ' eV &mdash; <button type="button" class="ref-note-more" onclick="_refClearIdentify()">clear</button></div>';
13820:      '<span class="ref-cand-ev">' + c.be.toFixed(2) + ' eV &middot; &Delta;' + c.dist.toFixed(2) + '</span></div>' +
13829:      (c.isAuger ? '<div class="ref-cand-line">KE ' + c.ke.toFixed(2) + ' eV &rarr; apparent BE on ' + srcLabel + '</div>' : '') +
13923:        <div class="hist-row-meta">${s.timestamp} &middot; ${(s.peaks || []).length} peak${(s.peaks || []).length !== 1 ? 's' : ''}${typeof s.chi === 'number' && isFinite(s.chi) ? ' &middot; <span class="hist-row-chi">' + _escHtml(_fitStatLabel(s.fitResult)) + ' = ' + s.chi.toFixed(3) + (_isLocalFit(s.fitResult) ? ' (starting point)' : '') + '</span>' : ''}${typeof s.rFactor === 'number' && isFinite(s.rFactor) ? ', R = ' + s.rFactor.toFixed(1) + '%' : ''}</div>
15105:    const centers = unassignedPeaks.map(p => (+p.center).toFixed(2)).join(', ');
15142:      `better by ${(+fda.delta_bic_vs_winner).toFixed(1)} points but was set ` +
15850:        `<td style="${td}">${(+p.center).toFixed(3)}</td><td style="${td}">${p.fwhm != null ? (+p.fwhm).toFixed(3) : '—'}</td>` +
15851:        `<td style="${td}">${p.amplitude != null ? (+p.amplitude).toFixed(0) : '—'}</td>` +
15852:        `<td style="${td}">${sc != null ? (+sc).toFixed(3) : '—'}</td></tr>`;
15878:        `<td style="${td}">${c.reduced_chi_sq != null ? (+c.reduced_chi_sq).toFixed(2) : '—'}</td>` +
15879:        `<td style="${td}">${c.bic_star != null ? (+c.bic_star).toFixed(1) : '—'}</td>` +
}

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
  const existing = wrap.querySelector('.onboard-wrap');
  if (existing) existing.remove();

  const ob = document.createElement('div');
  ob.className = 'onboard-wrap';
  ob.innerHTML = `
    <svg class="onboard-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
      <path d="M9 13h6"/><path d="M9 17h3"/>
    </svg>
    <div class="onboard-title">Load a spectrum to begin</div>
    <div class="onboard-steps">
      <div class="onboard-step">
        <div class="onboard-num">1</div>
        <div class="onboard-label">Drop a file</div>
      </div>
      <div class="onboard-step">
        <div class="onboard-num">2</div>
        <div class="onboard-label">Add peaks</div>
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
// invented coverage. A search query dims (not hides — a co-fit pick stays
// visible even if filtered out) non-matching cells.
function _fpRenderPtGrid(query) {
  const grid = document.getElementById('fp-pt-grid');
  if (!grid) return;
  const q = String(query == null ? '' : query).trim();
  const ql = q.toLowerCase();
  let cells = '';
  for (const el of REF_PT_LAYOUT) {
    const entries = _fpElementCoverage(el.sym);
    const clickable = entries.length > 0;
    const bestTier = _fpBestTier(entries);
    const meta = bestTier ? (FP_TIER_META[bestTier] || FP_TIER_META.structure_only) : null;
    const matchesQuery = !q || entries.some(e => _fpRegionMatchesFilter(e, q)) ||
      el.sym.toLowerCase().includes(ql);
    const hasSelection = entries.some(e => _fpRegionsSelected.has(e.region));
    const isExpanded = _fpExpandedElement === el.sym;
    const cls = 'fp-pt-cell' +
      (clickable ? ' selectable' : '') +
      (isExpanded ? ' expanded' : '') +
      (hasSelection ? ' has-selection' : '') +
      (q && !matchesQuery ? ' dimmed' : '');
    const style = `grid-column:${el.col};grid-row:${el.row}` +
      (meta ? `;--tier-c:${meta.color}` : '');
    const title = clickable
      ? `${el.sym} (Z=${el.z}) — ${meta.label}: click to see available core levels`
      : `${el.sym} (Z=${el.z}) — no practical Find Peaks coverage`;
    cells += `<div class="${_fpEsc(cls)}" style="${style}"` +
      (clickable
        ? ` tabindex="0" role="button" aria-expanded="${isExpanded}" onclick="_fpToggleElementExpand('${el.sym}')"` +
          ` onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();_fpToggleElementExpand('${el.sym}')}"`
        : '') +
      ` title="${_fpEsc(title)}">${el.sym}</div>`;
  }
  cells += '<div class="fp-pt-cell fmarker" style="grid-column:3;grid-row:6" title="Lanthanides — detached row below">57–71</div>';
  cells += '<div class="fp-pt-cell fmarker" style="grid-column:3;grid-row:7" title="Actinides — detached row below">89–103</div>';
  grid.innerHTML = cells;
}

function _fpToggleElementExpand(sym) {
  _fpExpandedElement = (_fpExpandedElement === sym) ? null : sym;
  _fpRenderPtGrid(document.getElementById('fp-regions-filter').value);
  _fpRenderExpandedPanel();
}

// The currently-expanded element's practical levels, as clickable chips —
// each independently colored/tagged by ITS OWN tier (a curated + machine
// level can coexist on one element).
function _fpRenderExpandedPanel() {
  const panel = document.getElementById('fp-expanded-panel');
  if (!panel) return;
  if (!_fpExpandedElement) {
    panel.innerHTML = '<div class="fp-expanded-empty">Click an element above to see its available core levels, or search by element, name, or level.</div>';
    return;
  }
  const entries = _fpElementCoverage(_fpExpandedElement)
    .sort((a, b) => (FP_TIER_RANK[b.tier] - FP_TIER_RANK[a.tier]) || a.level.localeCompare(b.level));
  if (!entries.length) {
    panel.innerHTML = `<div class="fp-expanded-empty">${_fpEsc(_fpExpandedElement)} — no practical Find Peaks coverage.</div>`;
    return;
  }
  const name = entries[0].name;
  const chips = entries.map(e => {
    const meta = FP_TIER_META[e.tier] || FP_TIER_META.structure_only;
    const isSel = _fpRegionsSelected.has(e.region);
    return `<div class="fp-level-chip${isSel ? ' selected' : ''}" style="--tier-c:${meta.color}"` +
      ` tabindex="0" role="button" aria-pressed="${isSel}"` +
      ` onclick="_fpToggleRegion('${_fpEsc(e.region)}', event.ctrlKey||event.metaKey)"` +
      ` onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();_fpToggleRegion('${_fpEsc(e.region)}', event.ctrlKey||event.metaKey)}"` +
      ` title="${_fpEsc(meta.label + ': ' + e.note)}">${meta.tag} ${_fpEsc(e.level)}</div>`;
  }).join('');
  panel.innerHTML = `<div class="fp-expanded-title">${_fpEsc(name)} (Z=${entries[0].z}) — click a level` +
    ` <small style="color:var(--text3)">(ctrl/⌘-click to add a second region)</small></div>` +
    `<div class="fp-level-chips">${chips}</div>`;
}

// Up to 8 direct region matches while typing — a fast alternative to
// clicking through the grid (goal: type-ahead search alongside the grid).
function _fpRenderSearchDropdown(query) {
  const box = document.getElementById('fp-search-dropdown');
  if (!box) return;
  const q = String(query == null ? '' : query).trim();
  if (!q) { box.innerHTML = ''; return; }
  const coverage = ((_fpMeta && _fpMeta.coverage) || []).filter(e => e.practical);
  const opts = _fpBuildRegionOptions(coverage, q).slice(0, 8);
  if (!opts.length) { box.innerHTML = ''; return; }
  const rows = opts.map(o => {
    const meta = FP_TIER_META[o.tier] || FP_TIER_META.structure_only;
    const entry = coverage.find(e => e.region === o.value);
    return `<div class="fp-search-dropdown-item" style="--tier-c:${meta.color}"` +
      ` tabindex="0" role="button"` +
      ` onclick="_fpPickFromSearch('${_fpEsc(o.value)}', event.ctrlKey||event.metaKey)"` +
      ` onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();_fpPickFromSearch('${_fpEsc(o.value)}', event.ctrlKey||event.metaKey)}">` +
      `<span>${meta.tag} ${_fpEsc(o.value)}</span>` +
      `<span class="fp-sdi-name">${_fpEsc(entry ? entry.name : '')}</span></div>`;
  }).join('');
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
1072:    # Only what a local solver understands: DE options (seed, popsize, ...)
1130:# numpy's global generator, unseeded.
1148:def _request_seed(x, counts, background, shapes, prefixes, params, *, fit_kws, n_perturb) -> int:
1149:    """The seed for every random draw of one fit: a pure function of the
1168:    request was hashed as sent.) It is a seed, not an identity: 32 bits
1173:    solver = {k: v for k, v in dict(kws.pop("fit_kws", None) or {}).items() if k != "seed"}
1193:    h = hashlib.sha256(b"xps-fit-seed-v1\0")
1198:    return int.from_bytes(h.digest()[:4], "little")            # 32 bits: what scipy's seed accepts
1384:#     F = ((chi2_without_refit - chi2_with) / p) / (chi2_with / dof)
1389:def _component_required(fit_reduced, params_full, removed_prefixes, y_sub, weights,
1392:    (the same candidate machinery and seeding the fit used, so differential
1393:    evolution's box/refinement and the request seed apply to the refit too).
1429:    return {"required": bool(required), "f": f, "chi2_with": float(chi2_with), "chi2_without_refit": chi2_without,
1473:    # at 1e-8 and a different fit), and the seed hashes float64.
1491:    # A caller's seed is consumed HERE: it replaces the request-derived one
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
requirements-dev.txt
requirements.txt
docs/autofit/test_data/Project9_CasaXPS_newfit.proj.zip
docs/autofit/test_data/8-JT Graphite.proj.zip
docs/autofit/test_data/UCl4_on_graphite.proj.zip
docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip
docs/autofit/test_data/B4C-UCl4.proj.zip
docs/autofit/test_data/Cl2p_projfit_test.proj.zip
docs/autofit/test_data/4-GTA UCl4-BN.proj.zip
/usr/bin/python3

exec
/bin/zsh -lc "rg -n 'async function uploadToBackend' templates/index.html; sed -n '3294,3320p' templates/index.html; sed -n '1389,1435p' fitting.py; sed -n '13934,13950p' templates/index.html; ls -d /Users/skyefortier/xps-app/venv /Users/skyefortier/xps-app/.venv /opt/homebrew/bin/python* 2>/dev/null; rg -n 'def parse|read_csv|loadtxt' parsers.py app.py | head -25; sed -n '1,130p' tests/test_component_support.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
6396:async function uploadToBackend(be, inten) {
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
zsh:1: no matches found: /opt/homebrew/bin/python*
rg: parsers.py: No such file or directory (os error 2)
app.py:617:    def parse_vgd_endpoint():
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
    assert sup["supported"] is (f >= fitting.SUPPORT_MIN_F)
    # removing a component that costs nothing
    zero = fitting._component_support(y_sub, fitted, np.zeros(5), w, 3, 3)
    assert zero["supported"] is False and zero["f"] == 0.0
    # an exact fit that needs the component
    exact = fitting._component_support(y_sub, y_sub, comp, w, 3, 3)
    assert exact["supported"] is True and exact["f"] is None       # infinite, serialised as null


def test_a_linked_component_follows_its_parent():
    x, y = _spectrum()
    specs = _specs() + [{"id": 3, "shape": "pseudo_voigt_gl", "center": 288.0, "amplitude": 100.0, "fwhm": 1.2,
                         "gl_ratio": 0.3, "amplitude_min": 0, "constrain_to": 2, "splitting": -0.9, "area_ratio": 0.001}]
    res = fitting.run_fit(x, y, specs, **KW)
    by = {str(ip["id"]): ip for ip in res["individual_peaks"]}
    assert by["3"]["support"]["follows"] == 2
    assert by["3"]["support"]["supported"] == by["2"]["support"]["supported"] is True


def test_the_page_can_read_it_through_the_api(client):
    x, y = _spectrum()
    csv = "\n".join(f"{a:.3f},{b:.2f}" for a, b in zip(x, y))
    sid = client.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "s.csv")}).get_json()["session_id"]
    body = client.post("/api/fit", json={"session_id": sid, "background": {"method": "linear"}, "peaks": _specs(),
                                          "fit_method": "least_squares", "n_perturb": 3}).get_json()
    assert all(ip["support"]["supported"] is True for ip in body["individual_peaks"])


def test_on_the_committed_targets_the_three_known_unsupported_components_are_the_only_ones():
    # The amplitude-floor measurement (plan §6) found exactly three, on three
    # C 1s re-fits; the server statistic must reproduce that.
    import json
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / "docs/findings/optimizer-disagreement/amplitude_floor.jsonl"
    if not path.exists():
        pytest.skip("measurement file not present")
    R = [json.loads(l) for l in path.read_text().splitlines()]
    flagged = {(r["tab"], c["name"]) for r in R for c in r.get("components", []) if c["unsupported"] and not c["linked"]}
    assert flagged == {("C1s Scan_4", "Unknown 2"), ("C1s Scan_0", "Unknown 2"), ("C1s Scan_6", "Adventitious 2")}


def test_a_grandchild_follows_the_root_whatever_the_request_order():
    # Codex round 1: request order [3, 2, 1] with links 3 -> 2 -> 1 and an
    # unsupported root gave [False, True, True] after a single forward pass.
    x, y = _spectrum()
    root = {"id": 7, "shape": "gaussian", "center": 292.5, "center_min": 291.5, "center_max": 293.5,
            "amplitude": 300.0, "amplitude_min": 0, "fwhm": 1.0}
    child = {"id": 8, "shape": "gaussian", "center": 293.0, "amplitude": 30.0, "fwhm": 1.0, "amplitude_min": 0,
             "constrain_to": 7, "splitting": 0.5, "area_ratio": 0.1}
    grandchild = {"id": 9, "shape": "gaussian", "center": 293.5, "amplitude": 3.0, "fwhm": 1.0, "amplitude_min": 0,

exec
/bin/zsh -lc "sed -n '6390,6435p' templates/index.html; ls -d /Users/skyefortier/xps-app/venv /Users/skyefortier/xps-app/.venv; rg -n 'read_csv|loadtxt|genfromtxt' file_parser.py; sed -n '9558,9579p' templates/index.html; sed -n '1,60p' tests/conftest.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
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
    center: p.center,
    amplitude: p.amplitude,
    fwhm: p.fwhm,
    amplitude_min: 0,
    fix_center: !!p.fixCenter,
    fix_fwhm: !!p.fixFwhm,
    fix_amplitude: !!p.fixAmplitude,
    fix_gl_ratio: !!p.fixGlMix
  };
  const shape = p.shape;
  if (shape === 'Gaussian') {
    spec.shape = 'gaussian';
  } else if (shape === 'Lorentzian') {
    spec.shape = 'lorentzian';
  } else if (shape === 'Voigt') {
ls: /Users/skyefortier/xps-app/.venv: No such file or directory
/Users/skyefortier/xps-app/venv
rg: file_parser.py: IO error for operation on file_parser.py: No such file or directory (os error 2)
  if (showEnvelope && plotBE.length && (fittedYBacked || state.peaks.length)) {
    datasets.push({
      label: _isLocalModel() ? 'Fit (local, starting point)' : 'Fit',
      data: fittedYBacked
        ? plotBE.map((b, i) => ({ x: b, y: fittedYBacked[i] - (bgSubView ? plotBG[i] : 0) }))
        : plotBE.map((b, i) => ({ x: b, y: modelFull[i] + (bgSubView ? 0 : plotBG[i]) })),
      borderColor: '#ff2020',
      borderWidth: Math.min((state.lineWidth ?? 1.5) + 1, 6),
      pointRadius: 0,
      fill: false
    });
  }

  _refreshStartsEvidence(false, true);   // background / ROI controls only repaint the chart: keep the visible consumers honest (fromPlot: the chart itself is being rebuilt)
  _refreshRoiAndCentreWarnings();         // ROI past the data / centre outside the data: warn, never move
  // History snapshot preview overlay (cyan dashed, drawn on top)
  if (_historyPreview && _historyPreview.peaks && _historyPreview.peaks.length && plotBE.length) {
    const prevPeakY = evalAllPeaks(plotBE, _historyPreview.peaks);
    const isLight = document.body.classList.contains('light-theme');
    datasets.push({
      label: _isLocalFit(_historyPreview.fitResult) ? 'Preview (local, starting point)' : 'Preview',
      _historyPreview: true,   // the glow plugin keys on this flag, not on the label text
"""Make the repo root importable regardless of how pytest is invoked."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

codex
The “same window” claim has another gap: `uploadToBackend` rounds energies to four decimals. Manual fit filters before that rounding; Find Peaks filters afterward on the server, so boundary points can differ. The 34 focused JS tests pass, but they don’t exercise that upload path or the region-picker refresh.

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\'');
const lines=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'').split('\\''\\n'\\'');
function extract(name){let s=lines.findIndex(l=>new RegExp('\\''"'^(async )?function '"'\\''+name+'\\''\\\\('\\'').test(l)),d=0;for(let i=s;i<lines.length;i++){for(const c of lines[i]){if(c==='\\''{'\\'')d++;if(c==='\\''}'\\'')d--;}if(d===0)return lines.slice(s,i+1).join('\\''\\n'\\'');}}
const dom={'\\''roi-min'\\'':{value:'\\''282'\\''},'\\''roi-max'\\'':{value:'\\''293'\\''},'\\''roi-hint'\\'':{style:{display:'\\''none'\\''},textContent:'\\'''\\''},'\\''fp-regions-tier-note'\\'':{},'\\''fp-regions-filter'\\'':{value:'\\'''\\''}};
const state={rawBE:Array.from({length:151},(_,i)=>280+i/10),rawIntensity:Array(151).fill(100),ccShift:0,peaks:[]};
const names=['\\''getCorrectedBE'\\'','\\''getROIData'\\'','\\''_roiWindowStatus'\\'','\\''_roiHintFor'\\'','\\''_refreshRoiHint'\\'','\\''_centreOutsideData'\\'','\\''_outsideDataBadge'\\'','\\''_escAttr'\\'','\\''_fpSyncSelectionUI'\\''];
const pre=\"const _fpRegionsSelected=new Set(['\\''C 1s'\\'']); const _fpMeta={coverage:[{region:'\\''C 1s'\\'',roi:{be_min:278,be_max:298}}]}; const _fpTierNoteFor=()=>'\\'''\\'', _fpRenderPtGrid=()=>{}, _fpRenderExpandedPanel=()=>{};\";
const e=new Function('\\''document'\\'','\\''state'\\'',pre+names.map(extract).join('\\''\\n'\\'')+'\\''; return {'\\''+names.join('\\'','\\'')+'\\''};'\\'')({getElementById:id=>dom[id]},state);
e._refreshRoiHint(e._roiWindowStatus()); e._fpSyncSelectionUI();
console.log('\\''After Find Peaks auto-fill:'\\'',JSON.stringify({roi:[dom['\\''roi-min'\\''].value,dom['\\''roi-max'\\''].value],actualStatus:e._roiWindowStatus().state,hint:dom['\\''roi-hint'\\'']}));
console.log('\\''Unsupported centre tooltip:'\\'',e._outsideDataBadge({id:7,center:310,support:{supported:false,fitKey:'\\''current'\\''}},e._roiWindowStatus()));
state.rawBE=Array.from({length:21},(_,i)=>280.00004+i*0.1);state.rawIntensity=state.rawBE.map(()=>100);dom['\\''roi-min'\\''].value='\\''280.00002'\\'';dom['\\''roi-max'\\''].value='\\''282.1'\\'';
const manual=e.getROIData().be;const find=state.rawBE.map(x=>+x.toFixed(4)).filter(x=>x>=280.00002&&x<=282.1);
console.log('\\''Upload boundary mismatch:'\\'',{manual:manual.length,findPeaks:find.length,manualFirst:manual[0],findFirst:find[0]});
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
After Find Peaks auto-fill: {"roi":[278,298],"actualStatus":"past","hint":{"style":{"display":"none"},"textContent":""}}
Unsupported centre tooltip: <span class="outside-data-badge" data-peak-id="7" title="Centre 310.00 eV lies outside the fitted data (280.00–295.00 eV). A component centred outside the measured data is almost always a placement error: the fit sees only its tail. Nothing has been moved.">outside data</span>
Upload boundary mismatch: { manual: 21, findPeaks: 20, manualFirst: 280.00004, findFirst: 280.1 }

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -m pytest -p no:cacheprovider tests/test_component_required.py -k 'redundant_anchor' -q --capture=sys" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 exited 2 in 1514ms:

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
1 error in 1.27s

exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '5098,5155p'; nl -ba docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md | sed -n '54,77p'; sed -n '7800,7860p' templates/index.html; rg -n 'F.*10|SUPPORT_MIN_F|\\[.required.\\].*True|least_squares' tests/test_component_required.py tests/test_autofit* tests/test_fit* | head -60; sed -n '15745,15808p' templates/index.html; rg -n 'read_csv|genfromtxt|loadtxt|def parse_csv' . --glob '*.py' --glob '"'!docs/**'"' | head -30" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
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
  if (!peaks) { notify(_STARTS_STALE_MSG, 'amber', true); return; }
  const shift = alt.largest_centre_shift_from_start;
  const name = _startsPeakName(shift.id);
  if (Math.abs(shift.ev) > _STARTS_SHIFT_RED_EV &&
      !confirm(`This solution moves ${name} by ${_startsEv(shift.ev)} from where you placed it. Apply?`)) return;
  const chosen = { fromChi: state.fitResult.starts.fit.chi2r, toChi: alt.chi2r, shiftName: name, shiftEv: shift.ev };
  if (_historyPreview) _historyClearPreview();
  await runFit({ startPeaks: peaks, chosenAlternative: chosen });
}

async function runFit(opts = {}) {
  if (!state.rawBE.length) { notify('Load a spectrum first.', 'red', true); return; }
  if (!state.peaks.length) { notify('Add at least one peak.', 'red'); return; }
  pushUndo();

  _showFitSpinner();
  document.getElementById('sb-msg').textContent = 'Fitting\u2026';

  // Capture the tab that owns this fit so that if the user switches tabs
  // mid-request, we can discard the stale result instead of corrupting the
  // now-active tab's state.
  const fittingTab = _opOwner();

  const { be, inten } = getROIData();
  const bgIntensity = computeBackground(be, inten);
  const bgSubtracted = inten.map((v, i) => v - bgIntensity[i]);

  // Try Flask backend first
  let backendResult = null;
  try {
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
zsh:1: no matches found: tests/test_autofit*
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
./parser.py:83:def parse_csv(path: Path) -> tuple[np.ndarray, np.ndarray]:
./parser.py:112:        df = pd.read_csv(
./parser.py:137:            df2 = pd.read_csv(

exec
/bin/zsh -lc 'node --test --test-reporter=dot tests/js/*.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"-p\", \"no:cacheprovider\", \"tests/test_component_required.py\", \"-k\", \"redundant_anchor\", \"-q\", \"--capture=sys\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
exec
/bin/zsh -lc "sed -n '108,154p' parser.py; rg -n 'closeFindPeaks|hideFindPeaks|fp-modal.*none|function _fpPickFromSearch' templates/index.html; sed -n '15443,15463p' templates/index.html; rg -n 'seed|jitter|1500|1,500' docs/superpowers/plans/2026-09-25* docs/superpowers/plans/2026-09-22* | head -40" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
    # Detect delimiter from the first non‑empty data‑looking line
    delimiter = _detect_delimiter("\n".join(lines[:20]))

    try:
        df = pd.read_csv(
            io.StringIO("\n".join(lines)),
            sep=delimiter,
            header=None,
            comment="#",
            engine="python",
        )
    except Exception as exc:
        # Clean, non-leaking message (audit F10): a corrupt/unreadable file is a
        # user-fixable problem, so surface a helpful 400 rather than a generic
        # 500 — but never echo the raw pandas text. The original is preserved on
        # the exception chain (`from exc`) for a server-side traceback if needed.
        raise ValueError(
            "Could not parse the file as delimited text. Expected two numeric "
            "columns (binding energy, intensity)."
        ) from exc

    # Drop any entirely‑NaN columns (e.g. trailing delimiter)
    df.dropna(axis=1, how="all", inplace=True)

    # Extract the first two numeric columns
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if len(numeric_cols) < 2:
        # Possibly header row(s) still present – try skiprows
        for skip in range(1, min(20, len(df))):
            df2 = pd.read_csv(
                io.StringIO("\n".join(lines)),
                sep=delimiter,
                header=None,
                skiprows=skip,
                comment="#",
                engine="python",
            )
            df2.dropna(axis=1, how="all", inplace=True)
            nc = [c for c in df2.columns if pd.api.types.is_numeric_dtype(df2[c])]
            if len(nc) >= 2:
                df = df2
                numeric_cols = nc
                break
        else:
            raise ValueError(
                "Could not find two numeric columns in the file. "
                "Expected (energy, counts)."
14595:      <button class="btn btn-sm" onclick="closeFindPeaksModal()" style="float:right">&#x2715;</button>
15230:function closeFindPeaksModal() {
15449:function _fpPickFromSearch(region, additive) {
16034:  closeFindPeaksModal();
      `<span>${meta.tag} ${_fpEsc(o.value)}</span>` +
      `<span class="fp-sdi-name">${_fpEsc(entry ? entry.name : '')}</span></div>`;
  }).join('');
  box.innerHTML = `<div class="fp-search-dropdown">${rows}</div>`;
}

function _fpPickFromSearch(region, additive) {
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
docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md:100:passed 2 of 3 on main. Cause: NOT an unseeded path — every process drew the
docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md:101:identical seed; the variation is Trust-Region's documented last-digit
docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md:102:jitter. It reached the assertion because the construction did not
docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md:108:anchor at 1,500 (inside that range) so the fit must carry it,
docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md:63:determines the request seed) and selects the background window on the
docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md:89:seed hashes each parameter's effective role, so a Voigt request draws
docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md:90:differently from the old one (test `test_seed_reflects_the_held_eta…`).
docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md:114:  returning the 0.5 curve, the seed.
docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md:187:random seed, since the seed hashes the parameters as the fit receives them.
docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md:237:   sets the seed). Both fixed; re-run: median 0.35 → 0.36 pp, max 0.69 pp.

 succeeded in 9372ms:
..                                                                       [100%]
2 passed, 7 deselected in 8.91s

codex
I reproduced the stale Find Peaks hint and the upload boundary mismatch with extracted page functions. The badge tooltip also prints an unsupported component’s suppressed centre, and closing the last tab leaves the ROI hint visible. Both revised Python test cases passed; holding the anchor is a useful deterministic test of the support-versus-required distinction, though it no longer reproduces the original freely fitted optimizer outcome.

 exited 1 in 47205ms:
....................
....................
....................
....................
....................
....................
....................
...............
codex
1. **MAJOR — Find Peaks auto-fill leaves warnings stale.** [templates/index.html:9572](/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/templates/index.html:9572) refreshes warnings through `updatePlot`, but `_fpSyncSelectionUI` writes ROI fields at lines 15496–15497 without invoking it. Reproduced: data 280–295, initial ROI 282–293, then select a region suggesting 278–298. Status becomes `past`, but the hint remains hidden. Closing the modal also performs no refresh. Existing centre badges can likewise describe the previous selection. Refresh after this programmatic write and test the actual selection path.

2. **MAJOR — The claimed manual-fit/Find-Peaks window equivalence is false.** [Plan:60](/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md:60) overlooks `uploadToBackend` rounding energies to four decimals (`templates/index.html:6397`). Manual fit filters **before** uploading; Find Peaks filters rounded energies **after** uploading. Reproduced with 21 energies `280.00004 + i × 0.1` and ROI 280.00002–282.1: manual fit selects 21 points; Find Peaks selects 20. With 20 initial points, Find Peaks instead rejects the 19-point selection. This is pre-existing behavior, but invalidates this unit’s explicit verification requirement. Add transport-aware coverage and resolve or explicitly qualify the discrepancy.

3. **MINOR — The badge reports a suppressed unsupported centre.** [templates/index.html:5134](/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/templates/index.html:5134) unconditionally embeds the numeric centre, and the patcher never checks `_isUnsupported`. A currently unsupported component at 310 eV against 280–295 data displays dashes in its card, yet hovering its new badge reveals “Centre 310.00 eV”. Preserve the warning without reporting the unsupported fitted value. The unsupported-component tests stub out this integration.

4. **MINOR — Closing the last spectrum leaves its clipping hint visible.** [templates/index.html:9572](/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/templates/index.html:9572) cannot clear the hint on this path: `closeTab` clears the data and calls `renderEmptyChart` directly. `updatePlot` also returns before refreshing when data are empty. Reproduction: show a clipping hint, then close the only tab; the old clipped range remains beside “no data”. Clear warnings during empty-state rendering.

The visible-clamping interpretation is consistent with “do not auto-move.” I found no new writes to ROI fields, fitting inputs, saves, or evidence keys.

Validation: all 34 focused JS tests and both revised Python cases passed. The full JS run was stopped to bound review time. Holding the anchor preserves the support-versus-required test distinction, but does not independently establish the claimed original jitter diagnosis.

**VERDICT: NO-GO.**
tokens used
70,225
1. **MAJOR — Find Peaks auto-fill leaves warnings stale.** [templates/index.html:9572](/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/templates/index.html:9572) refreshes warnings through `updatePlot`, but `_fpSyncSelectionUI` writes ROI fields at lines 15496–15497 without invoking it. Reproduced: data 280–295, initial ROI 282–293, then select a region suggesting 278–298. Status becomes `past`, but the hint remains hidden. Closing the modal also performs no refresh. Existing centre badges can likewise describe the previous selection. Refresh after this programmatic write and test the actual selection path.

2. **MAJOR — The claimed manual-fit/Find-Peaks window equivalence is false.** [Plan:60](/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md:60) overlooks `uploadToBackend` rounding energies to four decimals (`templates/index.html:6397`). Manual fit filters **before** uploading; Find Peaks filters rounded energies **after** uploading. Reproduced with 21 energies `280.00004 + i × 0.1` and ROI 280.00002–282.1: manual fit selects 21 points; Find Peaks selects 20. With 20 initial points, Find Peaks instead rejects the 19-point selection. This is pre-existing behavior, but invalidates this unit’s explicit verification requirement. Add transport-aware coverage and resolve or explicitly qualify the discrepancy.

3. **MINOR — The badge reports a suppressed unsupported centre.** [templates/index.html:5134](/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/templates/index.html:5134) unconditionally embeds the numeric centre, and the patcher never checks `_isUnsupported`. A currently unsupported component at 310 eV against 280–295 data displays dashes in its card, yet hovering its new badge reveals “Centre 310.00 eV”. Preserve the warning without reporting the unsupported fitted value. The unsupported-component tests stub out this integration.

4. **MINOR — Closing the last spectrum leaves its clipping hint visible.** [templates/index.html:9572](/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/templates/index.html:9572) cannot clear the hint on this path: `closeTab` clears the data and calls `renderEmptyChart` directly. `updatePlot` also returns before refreshing when data are empty. Reproduction: show a clipping hint, then close the only tab; the old clipped range remains beside “no data”. Clear warnings during empty-state rendering.

The visible-clamping interpretation is consistent with “do not auto-move.” I found no new writes to ROI fields, fitting inputs, saves, or evidence keys.

Validation: all 34 focused JS tests and both revised Python cases passed. The full JS run was stopped to bound review time. Holding the anchor preserves the support-versus-required test distinction, but does not independently establish the claimed original jitter diagnosis.

**VERDICT: NO-GO.**
