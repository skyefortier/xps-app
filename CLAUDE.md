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
| `Voigt` | Pseudo-Voigt (Thompson et al.), fixed η = 0.5 |
| `GL` | Pseudo-Voigt with adjustable GL mixing (0–100) |
| `asym-GL` | GL with asymmetric FWHM broadening on high-BE side |
| `DS` | Doniach-Šunjić, `dsAlpha` (0–0.5) + `dsGamma` |
| `DSG_LA` | DS+G — DS asymmetric core convolved with Gaussian. Frontend params `laAlpha`/`laBeta`/`laM`; backend id `ds_g`. |
| `LACX` | True CasaXPS LA(α,β,m) — asymmetric Lorentzian + integer-kernel Gauss conv. Frontend params `caAlpha`/`caBeta`/`caM`; backend id `la_casaxps`. |

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
- `evalPeak` switch + grid-aware `laTrueCasaXPS_array` evaluator (called via `evalPeakArray`)
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
every ordinary request for that method returned HTTP 422. `run_fit` now
closes the open sides of freely varying parameters FOR THAT METHOD ONLY
(`_finite_search_box`); every other method's parameters are unchanged, and
`/api/analyze` reaches the same code through `options.fit_method`. The box
is a SEARCH limit, not a bound the request made: an amplitude ceiling
starts at max(10 × the largest |background-subtracted intensity|,
2 × |start|, 1) (and the floor at minus that when a request leaves
`amplitude_min` open — the page never does), a centre at the fitted energy
range (always a real interval, also beside a one-sided request bound); a
solution resting on a generated side — judged on that side's own scale,
1 % of the limit's magnitude for an amplitude, 1 % of the generated width
for a centre — is re-searched with that side widened (tenfold / one ROI
span; 3 widenings in total, shared by the first search and any winning
perturbed refit) and, if it still rests there, returned as
`success: false` naming the parameter; generated sides are never echoed back as `min`/`max` (the page
saves returned bounds and warns within 1 % of them). Measured on committed
targets with the page's `n_perturb: 3` before the widening logic: 3–47 s
per fit; on 6–7-component C 1s models it exhausted lmfit's evaluation
budget and returned `success: false`, which the acceptance rule shows as a
non-converged fit. It is not a gold standard.

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
`_localFitCaveat`). Measured in unit W1: weighted, it matches the server
on GL-type models (≤ 4 meV, ≤ 1.4 % area on the lab's C1s scans) but still
differs for Voigt components (the server fits their mix free — audit A03),
LA components (`caM` held), very weak components (local amplitude floor 1,
server 0), and where the model has several minima. Both engines weight by
√intensity whether the data are counts or CPS (a convention, not a
calibrated uncertainty for rates); the formula is the same but the inputs
are not bit-identical, because `uploadToBackend` rounds intensities to
2 dp before the server weights them. Retire the designation only on a
re-measurement after A03, the `caM` clamp and a decision ON ITS MERITS
about the amplitude lower bound (0 is degenerate, 1 is unit-dependent —
`docs/findings/2026-09-fit-determinacy.md` §3; do not implement "parity"
with either bound before that decision). The same file records that a
converged server fit is not ground truth: on a committed C 1s scan the
server's default method stopped in a local minimum the local engine
avoided.
See `docs/superpowers/plans/2026-09-18-local-engine-poisson-weighting.md`.

**Acceptance rule for fit outcomes (unit A0, 2026-09-15):** a fit OUTCOME
from Run Fit, Batch Fit or the local engine is shown, stored or exported
only if it converged. `runFitLocal` works on a copy and commits only on
success, returning `{success, iterations, chiReduced}`; `runFit`
treats `success !== true` from `/api/fit` as a failed fit and falls back to
the local engine only on a transport failure, never on a server-side
error. Not covered by this rule (separate units): model replacement that
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
