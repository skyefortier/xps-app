OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0e6c1-179b-7c72-9350-77b86abf03d2
--------
user
Review the noise-floor unit (Find Peaks occupancy: the server's support F test instead of the absolute 1.0-count floor), round 1: branch fix-occupancy-f-test, git diff main..HEAD. The owner's brief: "switch Find Peaks' occupancy test from the absolute 1.0-count floor to the same F test the server's support check uses, per docs/findings/noise-floor-occupancy/. Scale-free, no tolerance, per the design rule [CLAUDE.md 'Thresholds on data-scaled quantities fail']. Build to ready for deploy only." Plan with the site list, measurements and an OWNER DECISION: docs/superpowers/plans/2026-09-27-occupancy-f-test.md. Starting point: docs/findings/noise-floor-occupancy/ (README + variant_F_support_test.patch, reviewed as F3 rounds 1-3). Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

WHAT CHANGED (plan §1)
- B1-B4: every OCCUPANCY use of noise_floor (slot matching, the proposal gate, detectability, ComponentSlot.contains) now reads the component's own support verdict: fitting._component_support on the lmfit result that produced it (engine._component_supports, carried on FittedComponent.support); no fit behind it -> the sign of the amplitude. The Poisson VARIANCE floor sqrt(max(y, noise_floor)) is kept everywhere (the counting convention of the weights).
- C: match_components_to_slots — an unsupported component occupies no slot AND is not an orphan (returned under "__unsupported__", reporting only); an orphan is a SUPPORTED component no slot's window/width accepts.
- E: a linked slot whose amplitude is an expression of its parent's FOLLOWS its root's verdict (engine._followed_supports), as the server's support check does; a linked slot with a free amplitude keeps its own.
- The stress test test_bg_mismatch_surfaces_loudly is RE-STATED (plan §3 option A, owner decision pending): the winner must be the true model, χ²ᵣ > 10, filtered_dominant_alternative present — no longer `conditional`.
- Tests: tests/autofit/test_occupancy_support.py.

TRY TO BREAK
a. Is the support computed the way the server computes it (data, best fit, component curve, weights, free-parameter counts per component and in total; dof)? lmfit result.weights vs the engine's weights; eval_components keys vs slot prefixes; components with expressions (linked positions / widths) and their free-parameter count; background handling (is the component curve compared against the same residual the fit minimised?); fit_full_window; bound-fixed refits; the Bayesian method (does it read occupancy?).
b. Every site that decided occupancy or orphan status is covered (search beyond the listed ones: persistence, absent slots, the proposal pass, preseed, the decisive override, the confidence payload, /api/analyze payload consumers incl. the page).
c. Orphan split: can a real extra peak now escape the orphan check (e.g. a supported-but-marginal peak outside all windows is still an orphan — but what about one whose F is < 10 only because the fit is poor)? Does "__unsupported__" leak into any iteration over slot_map?
d. follows: chains, cycles, missing parents, a partner whose parent is outside the model, linked area ratio under fwhm_excess.
e. The design rule: any remaining threshold on a data-scaled quantity in the occupancy path; is SUPPORT_MIN_F reused, not copied.
f. The measurements in plan §2 (real-data winner changes; outcome scale-dependence 2/8 -> 6/8) — is the reasoning right, and is anything there a reason this should not ship?
g. The option-A re-statement of the stress test: honest, or a weakened test that hides a regression? Is the plan's recommendation sound?
h. Tests real and non-vacuous.

Finish with VERDICT: GO or VERDICT: NO-GO.

codex
I’ll trace the support calculation and its consumers, check the diff against the plan, and run focused checks where the read-only environment permits. I’ll rank concrete failures and finish with a verdict.

exec
/bin/zsh -lc "pwd; rg --files -g 'AGENTS.md' -g 'CLAUDE.md' -g '*occupancy*' -g '*support*'; git status --short; git diff --stat main..HEAD" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
 autofit/confidence.py                              |  30 ++--
 autofit/engine.py                                  | 112 ++++++++++++-
 autofit/grammar.py                                 |   8 +-
 .../codex/occupancy_f_test_review_prompt.txt       |  20 +++
 .../plans/2026-09-27-occupancy-f-test.md           | 178 +++++++++++++++++++++
 tests/autofit/test_occupancy_support.py            | 161 +++++++++++++++++++
 tests/autofit/test_stress_honesty.py               |  17 +-
 tests/test_browser_find_peaks_full_window.py       |  12 +-
 8 files changed, 517 insertions(+), 21 deletions(-)

exec
/bin/zsh -lc 'cat CLAUDE.md docs/superpowers/plans/2026-09-27-occupancy-f-test.md docs/findings/noise-floor-occupancy/README.md; git diff main..HEAD -- autofit tests' in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
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
| `POST`   | `/api/fit/start`          | The same request and validation as `/api/fit` (an immediate identical 400 / 404); runs the SAME `run_fit` in a background thread; returns `{job_id}` 202 (unit 2, 2026-09-27). |
| `GET`    | `/api/fit/progress/<id>`  | The job record: `status` running / done / error / cancelled, `elapsed_sec`, `heartbeat_age_sec`; `result` = exactly the `/api/fit` body; `error` + `http_status` = exactly what `/api/fit` would answer. |
| `POST`   | `/api/fit/cancel/<id>`    | Stop the job (every minimisation aborts via lmfit's `iter_cb`); also automatic after 180 s without a poll. |

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
| `LACX` | True CasaXPS LA(α,β,m) — asymmetric Lorentzian + Gauss conv with a CONTINUOUS m (data points; σ = m/3, half-width ⌈3.5σ⌉) on both sides since the caM unit (2026-09-25). Frontend params `caAlpha`/`caBeta`/`caM`; backend id `la_casaxps`. |

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
server fitted. No shape carries a tracked gap any more. LACX with m > 0 was
the last (the page drew m rounded to an integer 2m+1 kernel while the
server fits it continuously: up to 0.97 % of amplitude and 1.2 % of area on
the lab's U 4f components) until the `caM` unit, 2026-09-25:
`laTrueCasaXPS_array` now mirrors `_la_casaxps_true` (continuous σ = m/3,
half-width max(1, ⌈3.5σ⌉), `np.convolve` 'same' with the server's trim,
normalisation at the grid point nearest the centre) — ≤ 7e-16 of amplitude
on all 108 committed LA components, pinned across the α/β/m box on seven
grids incl. grids shorter than the kernel
(`docs/superpowers/plans/2026-09-25-cam-continuous.md`). DS+G was the other gap until 2026-09-22 (the page's quadrature
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

### Two readings of one field

When two places read the same input — the page and the server, a preview
and a fit, a comparison and the thing it compares — they must read it the
same way, or equivalent inputs get treated as different and different inputs
as equivalent. The instances so far: a "Voigt" meant η = 0.5 to the page and
a free η to the server (A03); the ROI, the preview background and the fitted
background meant three different point sets until one inclusive-bound
definition (`_bgWindowIndices`, sealed-fit-record memo Part 3); and in F1 the
fit key compared form numbers with `Number()` while the background code reads
the iteration and averaging counts with `parseInt()`, so typing "3e1" (read
as 3) matched a fit made at 30 (Codex round 2,
`docs/autofit/codex/f1_stale_statistics_r2_verdict_run{A,B}.md`). A comparison
must read each field exactly the way its consumer reads it — integers as
integers, energies through `parseFloat` — never a generic conversion
(`_fitKeyCanon`). (Owner, 2026-09-26.)

### Long fits start and poll (unit 2, 2026-09-27)

Run Fit (incl. "Use this solution") and Auto-Fit never hold a request open
for a fit: `_serverFitJob` starts it (`/api/fit/start`), polls every 0.5 s
and reads the finished record's `result` (the `/api/fit` body) with F2's
`_readFitReply` rules. So no request meets the public ~100 s ceiling (the five
largest C 1s basinhopping models completed in 213–414 s through the poll
path with no request longer than 0.28 s). Server: Find Peaks' job records
(atomic JSON under the upload folder, readable by any worker), a fit thread
and a 2 s heartbeat thread per job; `run_fit(cancel=)` gives every
`model.fit` an `iter_cb` that aborts once the job is cancelled — without it
the calls are made exactly as before (Levenberg-Marquardt byte-identical
either way). Page: the ownership rules run INSIDE the poll loop (a switched
tab or an edited model cancels the job and discards with the usual message);
a START that cannot reach the server is still a transport failure (local
fallback); a poll that cannot is retried, five in a row are; a stopped
heartbeat (> 30 s) is a failed fit; a closed page sends a cancel beacon, and
the server cancels a job nobody has polled for 180 s (above the ~1-minute
timer throttling of hidden browser tabs). A new start for the same tab
supersedes (cancels) the previous one — Auto-Fit only once its preflight has
passed, so a refused Auto-Fit leaves a running Run Fit alone; the spinner
belongs to the operation that showed it (Batch Fit shows none and hides none). Each worker process RUNS one fit at a
time (the rest wait `queued`) and admits at most 6, beyond that a 503 — with 4
workers, at most 4 concurrent fits, the bound the synchronous route had. The synchronous `/api/fit` stays
for scripts, tests and the Python twins. Plan:
`docs/superpowers/plans/2026-09-27-long-fits-start-poll.md`.

### Timing claims are measured through the public URL

A request from a student reaches the server through Cloudflare, whose edge
ends a proxied request at ~100 s (HTTP 524; probes through
xps.fortierlab.org on 2026-09-26: 88 s passed, 125 s gave 524) — well short
of gunicorn's `--timeout 300`. "300 s covers it" was written for the DS+G
Run Fit in 2026-09-22 and was true on the i9 and false through the public
URL. A claim that a request fits inside a limit is measured through
xps.fortierlab.org, not on 127.0.0.1. (Owner, 2026-09-27;
`docs/findings/2026-09-26-public-request-ceiling.md`.)

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
| m (`caM`) | Gaussian convolution kernel width in DATA POINTS (not eV); continuous (the server fits it continuously so its derivative exists; the page draws the same continuous value since 2026-09-25 — it drew an integer kernel; the local engine HOLDS it exactly, since LA's curve jumps at m = 6k/7 and a smooth optimiser cannot fit it), default 50, bounds 0–499 |

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

`basinhopping` follows THE SAME PATTERN since unit F2 (2026-09-26; owner
decision; plan `docs/superpowers/plans/2026-09-26-f2-acceptance-holes.md`):
`_basinhopping_candidate` — the search, then an unconditional
`least_squares` refinement from its point under the request's bounds (the
refinement's convergence is the verdict, no χ² comparison), then a
competition with a `least_squares` fit from the same start (verified beats
unverified, then the lower χ²), for the main fit, every perturbed restart and
the required refit. Until then basinhopping always reported `success: true`
(lmfit sets it before minimising and never reads scipy's result), and
scipy's own flag is no verdict either: it marked 23 of 24 sampled committed
targets failed (BFGS "precision loss") at points equal to Trust-Region's
minimum (median relative χ²ᵣ difference 1e-9). An unverifiable search is
`success: false`. Basinhopping runs NO perturbed restarts (a global search:
with the page's `n_perturb` 3 they took 14 of 16 multi-component targets past
the 300 s server timeout, median 386 s, for χ²ᵣ identical to 1e-8; without
them median 96 s, max 256 s). NOTE: the public URL's ceiling is lower —
Cloudflare returns 524 between 88 s and 125 s — so the largest basinhopping
models still fail there
(`docs/findings/2026-09-26-public-request-ceiling.md`, not yet addressed).

**Determinacy (unit F2).** `run_fit` refuses a model with at least as many
free parameters as data points (`ValueError`, HTTP 400, "not determined by
these data: N free parameters for M data points"), and so does the local
engine: lmfit divides by max(1, nfree) and the F tests clamp dof to 1, so such
a model read as a near-perfect, fully supported fit (6 points, 2 GL
components: χ²ᵣ 2.8e-6, both "supported"). A count, not a threshold; one
degree of freedom is fitted as before.

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
and stay labelled "Residual variance". It produces no uncertainties, and it
HOLDS LA's `caM` at its exact value (it used to round it in its clamp; a
free m was tried in the `caM` unit and withdrawn: LA's curve is
discontinuous in m, `docs/superpowers/plans/2026-09-25-cam-continuous.md`).

**A local result is a STARTING POINT, not a reportable result** (keyed on
`engine: 'local'`, helpers `_isLocalFit` / `_isLocalModel` /
`_localFitCaveat`). Measured in unit W1 and RE-MEASURED after A03
(2026-09-22, `docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`,
generator `scripts/local_server_gap.js`): weighted, it matches the server on
GL-type models (≤ 4 meV, ≤ 1.4 % area on the lab's C1s scans) and on Voigt
components (fixed η = 0.5 on both sides since A03: on the 5 of 9 committed
U 4f targets where both engines reach the same minimum every component
agrees within 4.3 meV, 2.6 % FWHM, 2.0 % area, 0.12 pp — W1 had measured up
to 20.8 % area on the Voigt satellites); it still differs on the other U 4f
targets for two reasons, separated by a control arm (the server with LA's
m held at the same value): the `caM` hold (the server fits m, the local
engine holds it — on Scan_6 the whole gap), and the local descent stopping
in a worse minimum (5–13 % χ²ᵣ above the held-m server on Scan_4/5/8) —
the "several minima" case (`docs/findings/cam/local_server_gap_after_cam.json`;
both engines' amplitude floor is 0 since unit step (b)). Both engines weight by
√intensity whether the data are counts or CPS (a convention, not a
calibrated uncertainty for rates); the formula is the same but the inputs
are not bit-identical, because `uploadToBackend` rounds intensities to
2 dp before the server weights them. A03 and the `caM` unit are done and
the designation STAYS on both grounds: fitting m locally needs a
derivative-free search (its own unit), and the worse-minimum outcome
(three of nine U 4f targets) remains; the label is reconsidered only on a
re-measurement after that work. (The amplitude-bound change
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
error. A 2xx body that was READ but is not JSON is the server's reply, not a
transport failure (unit F2): `_readFitReply` reads the text (a failure there
is transport) and parses it; a NaN / Infinity token (Flask serialises a σ it
could not compute that way) or any unparseable body is a failed fit with its
message, for Run Fit and Auto-Fit alike — until F2 it sent Run Fit to the
local engine, replacing the server's converged result, verdicts and starts
evidence with a starting point. A RESULT IS DISCARDED IF THE MODEL WAS EDITED WHILE THE FIT WAS RUNNING
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
STATISTICS AFTER AN EDIT (unit F1, 2026-09-25; plan
`docs/superpowers/plans/2026-09-25-f1-stale-statistics.md`): χ², σ, RMSE,
the R-factor and the stored fitted curve are bound to their fit by the SAME
key (`fitResult.startsModelKey`, now stamped by every creator — `runFit`,
`runFitLocal`, `applyAutoFitResult`, re-stamped by `_restampSupport`); no
second mechanism. One accessor, `_statsState(fr, key)` (`_statsLiveState()`,
`_statsRecordState(t)`): `current` / `stale` (the model or its context
changed since — an edit, a Find Peaks apply in the default window, an undo
or history restore to other values) / `unverified` (no key: saved before
this unit — values shown with a note to re-run). Stale: Results banner
("belong to the previous model"), statistic / RMSE "—", no R panel, no σ;
header "χ²ᵣ — (model changed)", status "—", "R: —"; no per-parameter
uncertainty rule; CSV/XLSX a WARNING instead of the statistic, σ cells
empty; TSV a NOTE (its columns are the current, unfitted model); figure no
χ² and no stored "Fit" curve; chart and stack envelopes composed from the
current peaks; saves keep the key (a reload judges again) and add
`statisticsState` / `statisticsNote`. Refreshed from `updatePlot`
via `_refreshStartsEvidence` (`_refreshStatsState`, Results carries
`data-stats-state`; lock toggles and Lock All reach it too). Keys are
compared by `_sameFitKey` (each form field canonicalised through its
readers' parser: energies parseFloat, "280" = "280.0"; counts parseInt,
"3e1" ≠ "30").
Auto-Fit now discards a response whose model or context was edited while
it ran, and a transport failure after such an edit runs no local fit. A
stale save's curve and R are never re-installed on load. The model
replacement that keeps an older result is thereby covered for the
statistics. Not covered (separate units): loaded files without convergence
provenance; `p._backendParams` still rides in a stale save (not displayed;
the sealed fit record owns it). From the initial commit
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

The page's background twins (`computeBackgroundCore`: what it draws, freezes
into `fitResult.bgIntensity` at fit time, saves, and what the local engine
fits against) equal fitting.py's on the tested cases — shirley, smart and
smart_exp EXACTLY (0 difference, at equal iteration caps), tougaard to
rounding, linear on uniform grids — within the test's 1e-6 of the intensity
span, on uniform and non-uniform grids, both directions, endpoint averaging
1, 3 and 10, repeated energies and data that dip below the baseline
(`tests/js/background_parity.test.js`, unit 4 2026-09-27). The Shirley and
smart_exp twins run fitting.py's iteration operation for operation on an
ascending copy — numpy's linspace start with the endpoint pinned exactly, the
net signal clamped at zero, the background kept when no net signal is left,
the 1e-6 stop; smart clamps against the raw data; every endpoint mean is
numpy's (`_npMean`, numpy's pairwise summation: a sequential sum one rounding
step off became a different fixed point, 62.7 % of the span, Codex round 3);
finite inputs. Before the unit: Task 4's S4 / S5 (smart at averaging 10 was
1.2 % of the span away) and smart_exp 1.4 % (a 1e-4 stop, a descending grid
integrated from the other end). An iterative background is fragile: rounding
differences of one unit in the last place select different fixed points, so a
twin must match its arithmetic, not only its formula. Known gaps, pinned:
`shirley_linear` (de-listed) diverges on descending grids; linear
interpolates by index on the page and by energy on the server, equal only on
uniform grids (Task 4 cause 4); the UI's Shirley iteration count (default 5)
stops before fitting.py's convergence (Part 5 of the sealed-fit-record memo).

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
  with the same F ≥ 10 rule (a refit that did not converge gives NO verdict
  since unit F2 — `required: null, refit_converged: false` — and Auto-Fit
  refuses that anchor too: a refit stopped early had read "required", F 992,
  for a redundant anchor). `applyAutoFitResult` refuses a supported-but-
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
  + charge correction. Enabled only when the midpoint of the DATA the fit
  would use is in 270–315 eV — for the active tab the live selection
  `getROIData()` returns, never the tab record's stale window or a typed
  window reaching past the data (`isC1sTab`, unit F3 2026-09-27, sweep M5).
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
# Find Peaks occupancy: the server's support F test instead of a 1-count floor (2026-09-27)

Owner, 2026-09-27: "switch Find Peaks' occupancy test from the absolute
1.0-count floor to the same F test the server's support check uses, per
docs/findings/noise-floor-occupancy/. Scale-free, no tolerance, per the
design rule. Build to 'ready for deploy' only — do NOT deploy it. Enumerate
sites first; Codex x2."

Starting point: `docs/findings/noise-floor-occupancy/variant_F_support_test.patch`
(measured in F3) plus the README's two required follow-ups.

## 1. Sites — every read of `noise_floor` in the Find Peaks engine (`autofit/`)

`noise_floor` (default 1.0; the page never sends it) had two jobs.

**A. Poisson variance floor, σ = √max(y, noise_floor) — KEPT, unchanged.** Not
a decision threshold: it is the counting convention the server's weights use
(`fitting`: 1/√max(counts, 1)).

| site | what |
|---|---|
| `candidates.py:621–622` | local σ for candidate detection gates |
| `engine.py` `compute_residual_diagnostics` | standardised residuals r/σ |
| `engine.py` preseed local σ (`_detect_*` / `local_sigma`) | preseed SNR gate |
| `engine.py` fit weights (`sigma = sqrt(max(y, noise_floor))`, two sites) | the fit's weights |
| `engine.py` `_attempt_proposal` local σ | the proposal's SNR gate (below) |

**B. Occupancy threshold, `amplitude > noise_floor` — REPLACED by the support F
test.**

| # | site | before | after |
|---|---|---|---|
| B1 | `engine.match_components_to_slots._accepts` | a component occupies a slot if its window/width fit AND amplitude > 1 count | window/width only decide WHICH slot; whether it is THERE is `_occupies(comp)` = `fitting._component_support(...)["supported"]` on the fit that produced it (F ≥ `SUPPORT_MIN_F`) |
| B2 | `engine._attempt_proposal` | a proposed slot is rejected if amplitude ≤ 1 count | rejected if `not _occupies(comp)`; the message names F |
| B3 | `confidence.build_confidence_vector` detectability | `above_floor` ≥ 3 × floor, `present_but_poorly_constrained` > floor | `above_floor` = supported; `present_but_poorly_constrained` = Δχ² > 0 but F < 10; `not_confidently_detected` = removing it costs nothing. Status values unchanged (the payload's consumers: `test_methods_seam`, `test_browser_schema_roundtrip`; the page reads none of the detectability fields) |
| B4 | `grammar.ComponentSlot.contains` | amplitude > noise_floor | amplitude > 0 (sign only; no engine caller) |

Where the support comes from: `engine._component_supports(result)` evaluates
`fitting._component_support` for every component of an lmfit result (data,
best fit, the component's curve, the fit's own weights, its free-parameter
count) once, in `_extract_fitted_components`; it rides on
`FittedComponent.support` through slot matching. A component with no fit
behind it (hand-built in tests) falls back to `amplitude > 0`.

**C. Orphans vs empty slots (README follow-up 1).** Before, a component that
failed occupancy had no accepting slot and became an ORPHAN — counted in
`orphan_rate`, a plausibility violation ("a peak nobody expects"). Under F that
would turn every unsupported in-window component into an extra-peak
violation. Now `match_components_to_slots` sets an unsupported component
aside (`"__unsupported__"`, reporting only): it occupies no slot (that slot's
persistence drops, as it should — the slot is empty) and it is NOT an orphan.
An orphan is a SUPPORTED component no slot's window/width accepts.

**Related, NOT changed: `engine._attempt_proposal`'s SNR gate** (`amplitude <
PROPOSAL_AMPLITUDE_SNR × local σ`, σ the Poisson noise). A signal-to-noise
ratio under the same counting assumption as the weights, not the 1-count
floor; listed so review can challenge it.

**E. Linked components follow their root.** The server's support check makes
a linked component FOLLOW its root (`individual_peaks[].support.follows`). The
engine now does the same for a slot whose amplitude is an expression of its
parent's (a spin-orbit partner at a fixed area ratio): `_followed_supports`
copies the root's verdict with `follows: <root role>`. A linked slot with a
free amplitude (only its position tied) keeps its own verdict.

**D. The model-mismatch honesty signal (README follow-up 2).** See §3 — an
owner decision.

## 2. Measurements

### Stress honesty battery (`tests/autofit/test_stress_honesty.py`)

With F + the orphan split: 11 passed, 1 failed — `test_bg_mismatch_surfaces_loudly`
(a Shirley-shaped truth fitted with straight-line backgrounds), as the README
predicted. Under F the winner is **P2, the TRUE two-peak model**
(`true_candidates=("P2",)`); P3's third component compensated for the wrong
background, F calls it unsupported (its gain divided by the misfit χ²ᵣ ≈ 284),
P3's persistence for that slot drops to 0 and P3 leaves the conditional pool.
The result still carries the winner's χ²ᵣ 308.7 (comparison table), the
winner row's `autocorr_flag`, and `filtered_dominant_alternative` (P3,
ΔBIC* 153 — the page's red "a better-scoring model was set aside" banner); it
is no longer `conditional`.

### Candidate mismatch signals, measured (winner of each run; ×0.1 = the same spectrum as a rate)

| spectrum | scale | χ²ᵣ | residual lag-1 autocorrelation flagged | n_eff / n |
|---|---|---|---|---|
| stress: bg mismatch | ×1 / ×0.1 | 308.7 / 30.9 | yes / yes | 0.0075 / 0.0075 |
| stress: bg matched control | ×1 / ×0.1 | 1.31 / 0.13 | no / no | ~1.0 / ~1.0 |
| 8 real committed C 1s scans (3 gate anchors + 5) | ×1 | 1.30–6.46 | **yes on 8 of 8** | 0.10–0.55 |
| same | ×0.1 | 0.15–3.51 | yes on 8 of 8 | 0.04–0.49 |

* χ²ᵣ is not scale-free (it moves with the counts: ×0.1 divides it by 10), and
  on real data it grows with the counts for a slightly imperfect lineshape — a
  χ²ᵣ cutoff is exactly the design rule's failure.
* The residual lag-1 autocorrelation IS scale-free (n_eff/n identical at ×1 and
  ×0.1), but real XPS fits are not noise-limited: every real winner has
  structured residuals. As a flag it fires on everything; as a number it
  separates the stress case (0.0075) from real fits (≥ 0.04) only by a factor
  of ~5 and only with a chosen constant.
* So no residual- or χ²ᵣ-based signal distinguishes "the background is wrong"
  from "the lineshape is not perfect" without a chosen cutoff.

(Also found, pre-existing and unchanged by this unit: the engine's model
selection itself is not rescale-invariant — on main a ×0.1 rescale changes the
winner or the conditional tier on 2 of the 8 real scans (Scan_8 UCl4, Scan_7 8-JT); BIC with Poisson
weights assumes counts.)

### Real-data gates (`RUN_AUTOFIT_GATE=1`: C 1s, U 4f, B 1s / Cl 2p parity; Bayesian real and U 4f unresolved; candidate-pool real; stress honesty)

| | main (0bb200b) | this branch |
|---|---|---|
| passed / failed | 26 / 1 | 26 / 1 |
| the failure | `test_candidate_pool_real_gate` ds8 "C1s Scan": the detected shoulder is not in the final model — IDENTICAL peaks on both (the sweep hits its 240 s budget after 3 of 6 candidates); PRE-EXISTING, on local-only held-out data never committed (the datasets were symlinked in from the main checkout for this run) | the same |
| stress honesty | 12 / 12 (old wording) | 12 / 12 (option-A wording, §3) |

### What F changes on real Find Peaks results (8 committed C 1s scans, gate options, ×1 and ×0.1; both engines run twice on the differing scans — both reproduce themselves 12 / 12, so every difference below is F's)

Final code (incl. §1 E, re-measured after it — one run changed, Scan_6 ×0.1):
10 of 16 runs unchanged. Changed:

| scan | scale | main | this branch |
|---|---|---|---|
| 1-GTA Scan_6 (gate anchor) | ×1 | MG2 (conditional), χ²ᵣ 2.04 | AG2+preseed (conditional), χ²ᵣ 3.69 — MG2's lowest slot persistence drops to 0.67: in one of its three refits a component was not supported by the data, so MG2 is no longer "stable" (the 1-count floor had counted that component as present). The C 1s gate still passes (graphite centre, satellite, envelope R) |
| 1-GTA Scan_2 | ×1 | MG2, χ²ᵣ 1.54 | MG3, χ²ᵣ 1.50 |
| 8-JT Scan_7 | ×1 | MG2, χ²ᵣ 5.21 | MG3, χ²ᵣ 5.19 |
| 1-GTA Scan_6 | ×0.1 | MG2 (conditional), χ²ᵣ 0.20 | MG3 (conditional), χ²ᵣ 0.22 |
| 8-JT Scan_5 | ×0.1 | MG3 conditional | MG3 not conditional |
| UCl4 Scan_3 | ×0.1 | MG2 | MG3 |

**Scale-dependence of the OUTCOME got WORSE on these scans, not better:** main
changes its result under ×0.1 on 2 of 8 scans, this branch on 6 of 8 (Scan_8,
Scan_6, Scan_5, 1-GTA Scan_2, Scan_3, Scan_7). The occupancy statistic itself
is invariant (pinned in `test_occupancy_support.py`), but the pipeline around
it is not: the candidate-detection and proposal gates are Poisson signal-to-
noise ratios, and BIC* with Poisson weights assumes counts, so ×0.1 changes
the candidate set and the ranking. Under the 1-count floor that never reached
occupancy on real data (every real amplitude is far above 1 count, so the
floor never flipped); under F — the likely mechanism, NOT traced scan by
scan — a MARGINAL component (F near 10) now decides a candidate's stability,
and those small upstream differences push it across.
In words: F makes the occupancy test scale-free and honest about marginal
components, and in doing so exposes that the rest of Find Peaks is not
scale-free. Owner-relevant: it is not a reason for C by itself (the ×1 results
are what students get from counts data), but it is not the "scale-free Find
Peaks" the design rule might suggest.

### A browser test's NOISE-FREE fixture

`tests/test_browser_find_peaks_full_window.py` (two of four) failed on this
branch: its synthetic C 1s spectrum is noise-free (300 + one Gaussian), fitted
to rounding (χ²ᵣ 0.00), where the support F test is meaningless (the
required-refit known limit in CLAUDE.md). The engine's outcome there turns on
the upload's rounding and wall-clock budgets ON MAIN TOO: through the page,
main returned a conditional fit and the branch none; through a direct
`/api/analyze` replay (4-dp upload) main returned NO survivor and the branch a
clean one. The test is about the apply path with the full-window option off,
not the fit, so its fixture now carries fixed pseudo-random Poisson noise
(√counts × a seeded normal): 4 / 4 pass on main AND on this branch. Known
limit, as for the required-refit test: on noise-free data the occupancy
verdicts are not meaningful.

## 3. OWNER DECISION — the background-mismatch honesty test

`test_bg_mismatch_surfaces_loudly` pinned "a wrong background is never a clean
confident result" through the conditional tier, and that tier was reached only
through the component that compensated for the wrong background (P3's third).
The README asked for a mismatch signal that does not ride on it; §2 shows the
signals at hand either are not scale-free (χ²ᵣ) or fire on every real fit
(residual structure). Options:

| | what | cost |
|---|---|---|
| **A (recommended; implemented on this branch)** | Accept F's outcome and re-state the test's contract to what is true and scale-independent in kind: the engine returns the true 2-peak model, the winner's χ²ᵣ is reported and grossly elevated, and the result carries `filtered_dominant_alternative` (the page's red banner). No new rule. The principled mismatch check is a comparison of BACKGROUND models (the matched-control case shows Shirley candidates absorb the integral background) — logged as its own unit | a wrong-background result is no longer marked "conditional"; the red banner remains |
| B | a result-level `model_mismatch` flag from a chosen constant (e.g. n_eff/n < 0.02, between the stress case's 0.0075 and real data's ≥ 0.04) | a new threshold on a data-dependent quantity (n_eff/n also depends on the sampling step) — the design rule's failure; needs calibration; NOT recommended |
| C | keep the 1-count floor until a background-comparison check exists | the occupancy floor stays scale-dependent |

A is what this branch ships; if the owner prefers C the branch waits.
# Find Peaks' 1-count occupancy floor → scale-free: PARKED for an owner decision (2026-09-27)

Part of unit F3 (sweep M9, first bullet). The other half of F3 — the Auto-Fit
C1s gate judging a stale typed window (sweep M5) — ships on its own in
`fix-noise-floor-scale-free` and does not depend on this.

## What was found

`noise_floor` (default 1.0, never sent by the page) does two jobs in
`autofit/`:

1. a Poisson variance floor, `sigma = sqrt(max(y, noise_floor))` — the
   counting convention the server's weights use; not a decision threshold,
   left as is by both variants;
2. an OCCUPANCY threshold, `amplitude > noise_floor` — whether a fitted
   component occupies its slot (`match_components_to_slots`), whether a
   proposed slot survives (`_evaluate_proposal`), the detectability status
   (`build_confidence_vector`). A slot is "occupied" at amplitude 1.5 and not
   at 0.5 whatever the data's scale; persistence, the absent-slot test and the
   stability gate follow from it. This is the design rule's case.

Both variants replace (2) with a statistic on the component's own fit
(computed once when the component is extracted from its lmfit result and
carried on `FittedComponent.support`), leave (1) alone, and fall back to
`amplitude > 0` (a sign test) for a component with no fit behind it. They
differ in ONE line — what "occupied" means:

| variant | occupied when | patch |
|---|---|---|
| **F** — the server's support test | `fitting._component_support` "supported": Δχ² > 0 and F = (Δχ²/p) / (χ²_with/dof) ≥ 10 — the step (b) "not supported by the data" statistic and threshold | `variant_F_support_test.patch` |
| **LR** — the weighted removal gain per parameter (first draft called it a "Poisson likelihood ratio"; it is neither a likelihood nor a refit) | Δχ²/p ≥ 10 on the Poisson-weighted χ², with the other components held, NOT divided by the fit's own misfit χ²_with/dof | `variant_LR_likelihood_ratio.patch` |

Neither carries a tolerance. Only F is a RATIO of χ² quantities and so
invariant to a uniform rescaling of the intensities; LR is not (Codex rounds
1–2: ×0.1 turns Δχ²/p = 32 into 3.2 and flips it, while F stays 16). F's
invariance is itself QUALIFIED by the Poisson variance floor both patches
keep (σ² = max(counts, 1)): a channel at or below 1 count weighs differently
after a rescaling, so F can move (round 2: 11.67 → 3.18, and 10.07 → 9.32,
on data with a channel near 1 count). Exact invariance holds only where every
channel stays above the floor.

## The evidence

| suite | baseline (today) | F | LR |
|---|---|---|---|
| gated real-data parity gates + stress honesty (`RUN_AUTOFIT_GATE=1`: C 1s parity, Bayesian real, candidate-pool real, U 4f unresolved, stress honesty) | 17 passed, 4 skipped | **16 passed, 1 FAILED** | 17 passed, 4 skipped |
| always-on `tests/autofit` (incl. the C 1s / region parity batteries) | green | **1 failed** (the same stress case), 556 passed | 557 passed, 7 skipped |

The failing case, `test_stress_honesty.py::test_bg_mismatch_surfaces_loudly`:
a Shirley-shaped truth fitted with a straight-line background, χ²ᵣ ≈ 280–470
for every candidate. The test requires the mismatch to be machine-visible
("conditional" tier), never a clean confident result. Today the 3-component
candidate P3 is stable but violates plausibility, enters the conditional
pool, and its bound-fixed refit wins via the decisive override →
`conditional: true`. Under F, P3's third component has F < 10 BECAUSE the fit
is so bad: F divides the gain by χ²_with/dof ≈ 284, so a component that
removes a large χ² still reads "unsupported"; it becomes an orphan, P3's
persistence drops to 0, P3 leaves the conditional pool, and P2 (χ²ᵣ 309) is
returned as a CLEAN survivor. Under LR the same component is occupied (its
gain per parameter is far above 10 Poisson units) and the result is
conditional, as today.

## Codex review of this write-up (F3 round 1, `f3_c1s_gate_verdict_run{A,B}.md`) — the recommendation below replaces the first draft's

Both runs reproduced the measurements and the mechanism (P3's third component:
Δχ² ≈ 10 702, F ≈ 9.42 with four free parameters → persistence 0, orphan rate 1,
out of the decisive-override pool). They also found three things wrong with
the first draft's recommendation of LR, all of which hold:

1. **LR is not scale-free.** "Dimensionless" is not "invariant under a change
   of intensity units": with Poisson weights the gain Δχ² scales with the
   counts, so multiplying a spectrum by 0.1 (CPS instead of counts, a
   normalisation) turned Δχ²/p = 32 into 3.2 and flipped the verdict, while F
   stayed at 16 — F is a RATIO of two χ² quantities and is invariant. The
   design rule asks for exactly that invariance. (The statistic is also a
   gain with the other components held fixed, not a refitted likelihood
   ratio; the draft's name overstated it.)
2. **The LR patch is internally inconsistent**: occupancy used Δχ²/p while
   detectability still used `support.supported` and reported
   `basis: support_f_test`, so a component could be "unoccupied" and
   `above_floor` at once, and a proposal rejection could print "F = 32.00 < 10".
3. **The stress case does not show F rejecting a real peak.** The fixture
   (`tests/autofit/stress_cases.py`) has TWO true peaks; P3's third component
   compensates for the wrong background. F calls it unsupported — defensibly —
   and the honesty flag then disappears because the "conditional" tier
   depended on keeping that background-compensating component. The F result
   also still carries `filtered_dominant_alternative` (P3, ΔBIC ≈ 153), which
   the page shows: not a silent clean answer.

Both runs, independently: **start from F** (one support definition across
the app, invariant to intensity units) and fix two things around it before
shipping:

- an unsupported component INSIDE its slot's window must not become an
  "orphan" (an unexplained extra peak) — today (and in both patches) a
  component that fails occupancy has no accepting slot and counts toward
  `orphan_rate`, a plausibility violation; "slot empty" and "peak nobody
  expects" need distinct treatment;
- the model-mismatch honesty signal must not depend on a component that only
  compensates for a wrong background — report the mismatch (χ²ᵣ ≫ 1, the
  residual structure) on its own terms.

## The decision (owner)

- **Adopt F as the occupancy statistic** (recommended, both reviewers), as a
  unit of its own with the two follow-ups above, measured on the gated and
  always-on suites; the honesty test is then re-examined against a
  mismatch signal that does not ride on P3.
- **LR**: withdrawn as a recommendation (not invariant to intensity units).
- Either way `noise_floor` survives only as the Poisson variance floor (both
  patches leave it; it keeps the raw-count assumption the server's weights
  make). That floor is what limits F's invariance to data whose channels stay
  above 1 count (see above) — a property the server's step (b) verdict shares.

The two patches stay here as the measured starting points:
`git apply docs/findings/noise-floor-occupancy/variant_F_support_test.patch`.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-mr0zADlh' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-U8Hz4NlG' (errno=Operation not permitted)
diff --git a/autofit/confidence.py b/autofit/confidence.py
index bb74778..64279b9 100644
--- a/autofit/confidence.py
+++ b/autofit/confidence.py
@@ -25,10 +25,12 @@ from typing import Optional
 
 import numpy as np
 
+from fitting import SUPPORT_MIN_F as _SUPPORT_MIN_F  # the server's support threshold: one definition
+
 from .engine import ModelReport, _slot_prefix, _width_param
 
-# UNVERIFIED tunable (spec §9): detection floor as a multiple of the noise
-# estimate. Calibrate on the labeled set; do not treat as physics.
+# No longer read (noise-floor unit, 2026-09-27): detectability is the support
+# F test (see build_confidence_vector). Kept so the keyword stays accepted.
 DETECTION_FLOOR_MULTIPLE = 5.0
 
 
@@ -89,19 +91,29 @@ def build_confidence_vector(
     noise_floor: float,
     detection_floor_multiple: float = DETECTION_FLOOR_MULTIPLE,
 ) -> dict:
-    """The per-peak `_confidence` payload for one grammar slot."""
+    """The per-peak `_confidence` payload for one grammar slot.
+
+    ``noise_floor`` / ``detection_floor_multiple`` are accepted and not read
+    (the Poisson variance floor lives in the fit's weights, not here)."""
     sstab = report.stability.per_slot.get(role)
     comp = next((c for c in report.primary_fit.components if c.slot_role == role), None)
     boundary = [h for h in report.primary_fit.boundary_hits
                 if h.startswith(f"{role}:")]
 
     amplitude = float(comp.amplitude) if comp is not None else None
-    floor = detection_floor_multiple * noise_floor
+    # Noise-floor unit (2026-09-27): detectability is the support F test on the fit
+    # (fitting._component_support, the server's statistic), not multiples of an
+    # absolute 1-count floor. above_floor = supported (F >= SUPPORT_MIN_F);
+    # present_but_poorly_constrained = the fit gains from it but not
+    # significantly; not_confidently_detected = removing it costs nothing.
+    support = getattr(comp, "support", None) if comp is not None else None
     if amplitude is None:
         detect_status = "not_fitted"
-    elif amplitude >= floor:
+    elif support is None:
+        detect_status = "above_floor" if amplitude > 0 else "not_confidently_detected"
+    elif support.get("supported"):
         detect_status = "above_floor"
-    elif amplitude > noise_floor:
+    elif (support.get("delta_chi2") or 0.0) > 0:
         detect_status = "present_but_poorly_constrained"
     else:
         detect_status = "not_confidently_detected"
@@ -122,9 +134,9 @@ def build_confidence_vector(
         },
         "detectability": {
             "amplitude": amplitude,
-            "noise_floor": noise_floor,
-            "floor_multiple": detection_floor_multiple,
-            "floor_multiple_is_tunable": True,
+            "basis": "support_f_test",       # fitting._component_support, F >= SUPPORT_MIN_F
+            "support_f": (support or {}).get("f"),
+            "support_min_f": _SUPPORT_MIN_F,
             "status": detect_status,
         },
         "identifiability": {
diff --git a/autofit/engine.py b/autofit/engine.py
index dbf4fd7..8877d3c 100644
--- a/autofit/engine.py
+++ b/autofit/engine.py
@@ -39,6 +39,8 @@ from lmfit import Model, Parameters
 from lmfit.model import ModelResult
 from scipy.integrate import trapezoid
 
+import fitting as _fitting  # the server's support statistic: one definition (noise-floor unit)
+
 from fitting import _SHAPE_FUNCS, linear_background, shirley_background, smart_background
 
 from .candidates import (build_candidate_pool, build_detection_candidate,
@@ -637,6 +639,17 @@ class FittedComponent:
     amplitude: float
     shape_params: dict
     line_shape: Optional[LineShape] = None
+    # Noise-floor unit (2026-09-27): does the fit that produced this component need it?
+    # fitting._component_support on that fit — with the other components held
+    # as fitted, removing this one must make the fit significantly worse (F >=
+    # SUPPORT_MIN_F). The occupancy decisions (slot matching, the proposal
+    # gate, detectability) read this instead of an absolute amplitude floor
+    # of 1 count, which judged a slot "occupied" at amplitude 1.5 and not at
+    # 0.5 whatever the data's scale (sweep M9; design rule "thresholds on
+    # data-scaled quantities fail"). None only where no fit is behind the
+    # component (hand-built in tests): then occupancy falls back to amplitude
+    # > 0, a sign test.
+    support: Optional[dict] = None
 
 
 @dataclass
@@ -652,10 +665,79 @@ class FitOutcome:
     boundary_hits: list[str] = field(default_factory=list)
 
 
+def _component_supports(result: ModelResult) -> dict[str, dict]:
+    """``fitting._component_support`` for every peak component of an lmfit
+    result, keyed by prefix — the one definition the server uses (step (b)).
+    Empty when the result carries no data (never raises: occupancy then falls
+    back to the sign test)."""
+    try:
+        comps = result.eval_components()
+        data = np.asarray(result.data, float)
+        fitted = np.asarray(result.best_fit, float)
+        w = result.weights if result.weights is not None else np.ones_like(data)
+        w = np.broadcast_to(np.asarray(w, float), data.shape)
+        n_free_total = int(result.nvarys)
+    except Exception:
+        return {}
+    out = {}
+    for prefix, comp_y in comps.items():
+        n_free_comp = sum(1 for n, par in result.params.items()
+                          if n.startswith(prefix) and par.vary and par.expr is None)
+        try:
+            out[prefix] = _fitting._component_support(data, fitted, np.asarray(comp_y, float), w,
+                                                      n_free_comp, n_free_total)
+        except Exception:
+            continue
+    return out
+
+
+def _followed_supports(result: ModelResult, model: CandidateModel,
+                       supports: dict[str, dict]) -> dict[str, dict]:
+    """A linked slot whose AMPLITUDE is an expression of its parent's (a
+    spin-orbit partner at a fixed area ratio) has no amplitude of its own to
+    judge: it FOLLOWS its root's verdict, as the server's support check makes
+    a linked component follow its root (`individual_peaks[].support.follows`).
+    A linked slot with a free amplitude (only its position tied) keeps its own
+    verdict. Walks the chain to the root; a cycle or a missing parent leaves
+    the slot's own verdict."""
+    by_role = {s.role: s for s in model.slots}
+
+    def _tied(slot: ComponentSlot) -> bool:
+        par = result.params.get(f"{_slot_prefix(slot.role)}amplitude")
+        return (slot.linked_to is not None and slot.linked_to in by_role
+                and par is not None and par.expr is not None)
+
+    out = dict(supports)
+    for slot in model.slots:
+        if not _tied(slot):
+            continue
+        root, seen = slot, {slot.role}
+        while _tied(root):
+            root = by_role[root.linked_to]
+            if root.role in seen:
+                break
+            seen.add(root.role)
+        else:
+            rs = supports.get(_slot_prefix(root.role))
+            if rs is not None:
+                out[_slot_prefix(slot.role)] = {**rs, "follows": root.role}
+    return out
+
+
+def _occupies(comp: "FittedComponent") -> bool:
+    """A slot is occupied by a component the data support. No threshold
+    on any data-scaled quantity: the support F test where a fit is behind the
+    component, else the sign of its amplitude."""
+    if comp.support is not None:
+        return bool(comp.support.get("supported"))
+    return comp.amplitude > 0
+
+
 def _extract_fitted_components(
     result: ModelResult, model: CandidateModel
 ) -> list[FittedComponent]:
     out: list[FittedComponent] = []
+    supports = _followed_supports(result, model, _component_supports(result))
     for slot in model.slots:
         prefix = _slot_prefix(slot.role)
         pars = result.params
@@ -676,6 +758,7 @@ def _extract_fitted_components(
             slot_role=slot.role, position=center, fwhm=fwhm,
             amplitude=amplitude, shape_params=shape_params,
             line_shape=slot.line_shape,
+            support=supports.get(prefix),
         ))
     return out
 
@@ -1045,17 +1128,27 @@ def match_components_to_slots(
     """Assign fitted peaks to grammar slots (role + effective window + width).
 
     ``bound_overrides`` (fit_full_window) — see ``_effective_be_window``.
+
+    Occupancy (noise-floor unit, 2026-09-27): a component OCCUPIES a slot only
+    if the data support it (``_occupies``: the server's support F test on the
+    fit that produced it). A component the data do not support is NOT THERE:
+    it occupies no slot (the slot stays empty for persistence) and it is not
+    an orphan either — an orphan is a supported peak no slot expects, a
+    plausibility violation; "slot empty" is a different outcome. Such
+    components are returned under ``"__unsupported__"`` (reporting only). The
+    1-count floor this replaces made every component at amplitude <= 1 an
+    orphan wherever it sat.
     """
     slot_map: dict[str, Optional[FittedComponent]] = {s.role: None for s in model.slots}
     orphans: list[FittedComponent] = []
+    unsupported: list[FittedComponent] = []
     asym_shapes = {LineShape.ASYM_GL, LineShape.DS, LineShape.DS_G, LineShape.LACX}
 
     def _accepts(slot: ComponentSlot, comp: FittedComponent) -> bool:
         lo, hi = _effective_be_window(slot, components,
                                       (bound_overrides or {}).get(slot.role))
         return (lo <= comp.position <= hi
-                and slot.fwhm_range[0] <= comp.fwhm <= slot.fwhm_range[1]
-                and comp.amplitude > noise_floor)
+                and slot.fwhm_range[0] <= comp.fwhm <= slot.fwhm_range[1])
 
     def _window_center(slot: ComponentSlot) -> float:
         # NEVER the widened bound (Codex-caught, round 2): this is a
@@ -1072,12 +1165,15 @@ def match_components_to_slots(
         return 0.5 * (lo + hi)
 
     for comp in components:
+        if not _occupies(comp):
+            unsupported.append(comp)   # not there: neither an occupant nor an orphan
+            continue
         candidate_slots = [s for s in model.slots if _accepts(s, comp)]
         if not candidate_slots:
             orphans.append(FittedComponent(
                 slot_role="unmatched", position=comp.position, fwhm=comp.fwhm,
                 amplitude=comp.amplitude, shape_params=comp.shape_params,
-                line_shape=comp.line_shape,
+                line_shape=comp.line_shape, support=comp.support,
             ))
             continue
 
@@ -1095,7 +1191,7 @@ def match_components_to_slots(
         claimed = FittedComponent(
             slot_role=best_slot.role, position=comp.position, fwhm=comp.fwhm,
             amplitude=comp.amplitude, shape_params=comp.shape_params,
-            line_shape=comp.line_shape,
+            line_shape=comp.line_shape, support=comp.support,
         )
         if incumbent is None:
             slot_map[best_slot.role] = claimed
@@ -1108,6 +1204,7 @@ def match_components_to_slots(
                 orphans.append(comp)
 
     slot_map["__orphans__"] = orphans  # type: ignore[assignment]
+    slot_map["__unsupported__"] = unsupported  # type: ignore[assignment]
     return slot_map
 
 
@@ -1235,6 +1332,7 @@ def run_stability_analysis(
                                             bound_overrides=bound_overrides)
         if slot_map.pop("__orphans__", []):
             n_with_orphans += 1
+        slot_map.pop("__unsupported__", None)   # reporting only: those slots are empty
         for role, comp in slot_map.items():
             if comp is None:
                 continue
@@ -2229,8 +2327,10 @@ def _attempt_proposal(
     # to a wall (Codex fwhm-cap review, run B BLOCKER).
     width_cap_hit = f"{spec.role}:fwhm@max"
     pr.boundary_hits = _proposed_slot_pegs(primary, spec.role)
-    if comp.amplitude <= noise_floor:
-        return _fast(f"amplitude {comp.amplitude:.1f} ≤ noise_floor {noise_floor:.1f}")
+    if not _occupies(comp):
+        f = (comp.support or {}).get("f")
+        return _fast("not supported by the data (removing it does not make the fit significantly worse"
+                     + (f", F = {f:.2f} < {_fitting.SUPPORT_MIN_F:.0f}" if f is not None else "") + ")")
     spurious_hits = [h for h in pr.boundary_hits if h != width_cap_hit]
     if spurious_hits:
         return _fast(f"proposed slot boundary pegs: {spurious_hits}")
diff --git a/autofit/grammar.py b/autofit/grammar.py
index c9a85cd..2f5909d 100644
--- a/autofit/grammar.py
+++ b/autofit/grammar.py
@@ -181,11 +181,15 @@ class ComponentSlot:
     broad_justification: Optional[str] = None
 
     def contains(self, be: float, fwhm: float, amplitude: float,
-                 noise_floor: float) -> bool:
+                 noise_floor: float = 0.0) -> bool:
+        # Noise-floor unit (2026-09-27): occupancy is decided by the support F test on the
+        # fit (engine._occupies); this geometric check keeps only the sign of
+        # the amplitude. ``noise_floor`` is accepted and ignored (the engine
+        # has no caller of this method).
         return (
             self.be_window[0] <= be <= self.be_window[1]
             and self.fwhm_range[0] <= fwhm <= self.fwhm_range[1]
-            and amplitude > noise_floor
+            and amplitude > 0
         )
 
 
diff --git a/tests/autofit/test_occupancy_support.py b/tests/autofit/test_occupancy_support.py
new file mode 100644
index 0000000..9f637ee
--- /dev/null
+++ b/tests/autofit/test_occupancy_support.py
@@ -0,0 +1,161 @@
+"""Find Peaks occupancy is the server's support F test, not a 1-count floor
+(noise-floor unit, 2026-09-27; plan
+docs/superpowers/plans/2026-09-27-occupancy-f-test.md).
+
+A slot is OCCUPIED by a component the data support: with the other components
+held as fitted, removing it makes the fit significantly worse
+(``fitting._component_support``, F >= SUPPORT_MIN_F) — the statistic Run Fit's
+"not supported by the data" outcome uses. The old rule, ``amplitude > 1.0``,
+judged a slot occupied at 1.5 counts and empty at 0.5 whatever the data's
+scale. Pinned here:
+
+* the verdict is carried on every fitted component and is invariant to a
+  uniform rescaling of the intensities (while every channel stays above the
+  Poisson variance floor), where the old floor flips;
+* residue at high counts (above 1 count, removing it costs nothing) is not an
+  occupant — the old floor accepted it;
+* an unsupported component occupies no slot and is NOT an orphan (an orphan is
+  a supported peak no slot expects); a supported component outside every
+  window still is;
+* the proposal gate and the detectability status read the same verdict.
+"""
+import numpy as np
+import pytest
+
+import fitting
+from autofit.confidence import build_confidence_vector
+from autofit.engine import (FittedComponent, _occupies, fit_candidate,
+                            match_components_to_slots)
+from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot, LineShape
+
+
+def _slot(role, be_window, fwhm_range=(0.5, 2.5)):
+    return ComponentSlot(role=role, region="C 1s", phase_id="p", be_window=be_window,
+                         line_shape=LineShape.GAUSSIAN, fwhm_range=fwhm_range)
+
+
+MODEL = CandidateModel(name="m", background=BackgroundType.LINEAR,
+                       slots=(_slot("main", (284.0, 285.0)), _slot("minor", (286.0, 287.0))))
+X = np.arange(280.0, 292.0, 0.05)
+Z = np.random.default_rng(20260927).standard_normal(X.size)   # one fixed noise pattern
+
+
+def _g(x, c, a, w):
+    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)
+
+
+def _spectrum(baseline, main_amp, minor_amp):
+    truth = baseline + _g(X, 284.5, main_amp, 1.0) + _g(X, 286.5, minor_amp, 1.2)
+    return truth + np.sqrt(truth) * Z
+
+
+def _fit(y):
+    w = 1.0 / np.sqrt(np.maximum(y, 1.0))     # the server's / the engine's Poisson weights
+    out = fit_candidate(X, y, w, MODEL)
+    assert out.converged
+    return {c.slot_role: c for c in out.components}
+
+
+def test_every_fitted_component_carries_the_servers_support_verdict():
+    comps = _fit(_spectrum(1e4, 2e4, 2e3))
+    for role in ("main", "minor"):
+        s = comps[role].support
+        assert s is not None and set(s) >= {"f", "delta_chi2", "supported"}, (role, s)
+        assert s["supported"] is True
+        assert s["f"] >= fitting.SUPPORT_MIN_F
+
+
+def test_the_verdict_is_invariant_to_rescaling_where_the_old_floor_flips():
+    y = _spectrum(1e4, 2e4, 2e3)
+    c = 4e-4          # counts -> a rate: the minor line's amplitude drops from ~2000 to ~0.8
+    assert np.min(c * y) > 1.0, "every channel stays above the Poisson variance floor"
+    a, b = _fit(y), _fit(c * y)
+    assert a["minor"].amplitude > 1.0 > b["minor"].amplitude, "the old rule would flip here"
+    for role in ("main", "minor"):
+        assert a[role].support["supported"] == b[role].support["supported"] is True, role
+        assert b[role].support["f"] == pytest.approx(a[role].support["f"], rel=1e-4), role
+        assert _occupies(a[role]) and _occupies(b[role])
+
+
+def test_residue_above_one_count_is_not_an_occupant():
+    # 5 counts on a 1e5-count baseline: the old floor called it occupied
+    comps = _fit(_spectrum(1e5, 2e5, 5.0))
+    minor = comps["minor"]
+    assert minor.support["supported"] is False, minor.support
+    assert not _occupies(minor)
+
+
+def _comp(pos, amp, support):
+    return FittedComponent(slot_role="?", position=pos, fwhm=1.0, amplitude=amp,
+                           shape_params={}, line_shape=LineShape.GAUSSIAN, support=support)
+
+
+def test_an_unsupported_component_leaves_its_slot_empty_and_is_not_an_orphan():
+    main = _comp(284.5, 1e4, {"f": 1e5, "delta_chi2": 1e6, "supported": True})
+    weak = _comp(286.5, 40.0, {"f": 2.1, "delta_chi2": 12.0, "supported": False})
+    m = match_components_to_slots([main, weak], MODEL, noise_floor=1.0)
+    assert m["main"] is not None and m["main"].support["supported"]
+    assert m["minor"] is None, "the slot is EMPTY"
+    assert m["__orphans__"] == [], "and the component is not an unexpected extra peak"
+    assert m["__unsupported__"] == [weak]
+
+
+def test_a_supported_component_no_slot_accepts_is_still_an_orphan():
+    main = _comp(284.5, 1e4, {"f": 1e5, "delta_chi2": 1e6, "supported": True})
+    stray = _comp(289.0, 900.0, {"f": 300.0, "delta_chi2": 5e3, "supported": True})
+    m = match_components_to_slots([main, stray], MODEL, noise_floor=1.0)
+    assert [o.position for o in m["__orphans__"]] == [289.0]
+    assert m["__unsupported__"] == []
+
+
+def test_without_a_fit_behind_it_occupancy_is_the_sign_of_the_amplitude():
+    assert _occupies(_comp(284.5, 0.3, None)), "0.3 > 0: no floor"
+    assert not _occupies(_comp(284.5, 0.0, None))
+    m = match_components_to_slots([_comp(284.5, 0.0, None)], MODEL, noise_floor=1.0)
+    assert m["main"] is None and m["__orphans__"] == []
+
+
+class _Report:
+    """The fields build_confidence_vector reads."""
+    def __init__(self, comp):
+        class _S:  # stability
+            per_slot = {}
+        class _P:  # primary fit
+            components = [comp]
+            boundary_hits = []
+            lmfit_result = None
+        self.stability, self.primary_fit, self.model = _S(), _P(), MODEL
+
+
+@pytest.mark.parametrize("support,status", [
+    ({"f": 50.0, "delta_chi2": 900.0, "supported": True}, "above_floor"),
+    ({"f": 3.0, "delta_chi2": 40.0, "supported": False}, "present_but_poorly_constrained"),
+    ({"f": 0.0, "delta_chi2": -1.0, "supported": False}, "not_confidently_detected"),
+])
+def test_detectability_reads_the_same_verdict(support, status):
+    comp = FittedComponent(slot_role="minor", position=286.5, fwhm=1.0, amplitude=0.4,
+                           shape_params={}, line_shape=LineShape.GAUSSIAN, support=support)
+    d = build_confidence_vector(_Report(comp), "minor", noise_floor=1.0)["detectability"]
+    assert d["status"] == status
+    assert d["basis"] == "support_f_test" and d["support_min_f"] == fitting.SUPPORT_MIN_F
+
+
+def test_an_amplitude_tied_partner_follows_its_parents_verdict():
+    """A spin-orbit partner at a fixed area ratio has no amplitude of its own:
+    it follows its root, as the server's support check makes a linked
+    component follow its root."""
+    x = np.arange(370.0, 400.0, 0.05)
+    main = ComponentSlot(role="main_7_2", region="U 4f", phase_id="p", be_window=(380.0, 382.0),
+                         line_shape=LineShape.GAUSSIAN, fwhm_range=(0.8, 2.5))
+    partner = ComponentSlot(role="main_5_2", region="U 4f", phase_id="p", be_window=(390.0, 393.5),
+                            line_shape=LineShape.GAUSSIAN, fwhm_range=(0.8, 2.5),
+                            linked_to="main_7_2", linked_offset_range=(10.7, 11.1), area_ratio=0.75)
+    model = CandidateModel(name="d", background=BackgroundType.LINEAR, slots=(main, partner))
+    truth = 500.0 + _g(x, 380.9, 8000.0, 1.6) + _g(x, 391.8, 6000.0, 1.6)
+    y = truth + np.sqrt(truth) * np.random.default_rng(3).standard_normal(x.size)
+    out = fit_candidate(x, y, 1.0 / np.sqrt(np.maximum(y, 1.0)), model)
+    assert out.converged
+    comps = {c.slot_role: c for c in out.components}
+    assert comps["main_5_2"].support["follows"] == "main_7_2"
+    assert comps["main_5_2"].support["supported"] == comps["main_7_2"].support["supported"] is True
+    assert "follows" not in comps["main_7_2"].support
diff --git a/tests/autofit/test_stress_honesty.py b/tests/autofit/test_stress_honesty.py
index 742f1c2..0e22869 100644
--- a/tests/autofit/test_stress_honesty.py
+++ b/tests/autofit/test_stress_honesty.py
@@ -124,14 +124,25 @@ def test_bg_matched_control_recovers():
 
 def test_bg_mismatch_surfaces_loudly():
     """Shirley-shaped truth fit with a straight line: the mismatch must be
-    machine-visible (conditional tier + grossly elevated χ²ᵣ), never a
-    clean confident result."""
+    machine-visible, never a silent clean result.
+
+    Re-stated in the noise-floor unit (2026-09-27; plan
+    docs/superpowers/plans/2026-09-27-occupancy-f-test.md §3, option A —
+    OWNER DECISION PENDING). Occupancy is now the server's support F test, so
+    the third component that only compensated for the wrong background is
+    "not supported" and the engine returns the TRUE two-peak model — which the
+    old conditional flag depended on NOT happening (the flag rode on that
+    compensating component, the README's follow-up 2). What stays visible,
+    without any new threshold: the winner is the true model, its χ²ᵣ is
+    grossly elevated, and the set-aside better-scoring model is flagged
+    (filtered_dominant_alternative — the page's red banner)."""
     case = bg_mismatch_case(seed=61)
     res = _ic(case)
-    assert res.diagnostics["conditional"] is True
+    assert res.diagnostics["winner"] in case.true_candidates
     wc = next(c for c in res.analysis["candidates"]
               if c["name"] == res.diagnostics["winner"])
     assert wc["reduced_chi_sq"] > 10.0
+    assert res.diagnostics["filtered_dominant_alternative"] is not None
 
 
 def test_preseed_catches_isolated_missing_peak():
diff --git a/tests/test_browser_find_peaks_full_window.py b/tests/test_browser_find_peaks_full_window.py
index 079860f..2eed2e2 100644
--- a/tests/test_browser_find_peaks_full_window.py
+++ b/tests/test_browser_find_peaks_full_window.py
@@ -135,11 +135,21 @@ def _load_c1s_with_stale_narrow_fit(pg):
     narrow" scenario exactly."""
     pg.evaluate("""() => {
         const raw = [], inten = [];
+        // Fixed pseudo-random Poisson-like noise (noise-occupancy unit,
+        // 2026-09-27): a NOISE-FREE spectrum is fitted to rounding, where the
+        // support F test that decides Find Peaks' occupancy is meaningless
+        // (CLAUDE.md, the required-refit known limit) and the engine's result
+        // turned on the upload's rounding and wall-clock budgets — on main
+        // too. This test is about the apply path, not the fit.
+        let seed = 20260927;
+        const u = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return (seed + 1) / 2147483649; };
+        const z = () => Math.sqrt(-2 * Math.log(u())) * Math.cos(2 * Math.PI * u());
         for (let i = 0; i <= 400; i++) {
             const be = 275.0 + i * 0.05625;
             raw.push(be);
             const g = (c, a, w) => a * Math.exp(-4 * Math.log(2) * ((be - c) / w) ** 2);
-            inten.push(300 + g(284.5, 6000, 0.8));
+            const truth = 300 + g(284.5, 6000, 0.8);
+            inten.push(truth + Math.sqrt(truth) * z());
         }
         tabManager.createTab('C1s', raw, inten);
         const narrowBE = raw.filter(b => b >= 278.0 && b <= 290.4);

exec
/bin/zsh -lc 'git diff main..HEAD -- autofit/engine.py autofit/confidence.py autofit/grammar.py; cat docs/superpowers/plans/2026-09-27-occupancy-f-test.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Me39NfaR' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-OpalfwAb' (errno=Operation not permitted)
diff --git a/autofit/confidence.py b/autofit/confidence.py
index bb74778..64279b9 100644
--- a/autofit/confidence.py
+++ b/autofit/confidence.py
@@ -25,10 +25,12 @@ from typing import Optional
 
 import numpy as np
 
+from fitting import SUPPORT_MIN_F as _SUPPORT_MIN_F  # the server's support threshold: one definition
+
 from .engine import ModelReport, _slot_prefix, _width_param
 
-# UNVERIFIED tunable (spec §9): detection floor as a multiple of the noise
-# estimate. Calibrate on the labeled set; do not treat as physics.
+# No longer read (noise-floor unit, 2026-09-27): detectability is the support
+# F test (see build_confidence_vector). Kept so the keyword stays accepted.
 DETECTION_FLOOR_MULTIPLE = 5.0
 
 
@@ -89,19 +91,29 @@ def build_confidence_vector(
     noise_floor: float,
     detection_floor_multiple: float = DETECTION_FLOOR_MULTIPLE,
 ) -> dict:
-    """The per-peak `_confidence` payload for one grammar slot."""
+    """The per-peak `_confidence` payload for one grammar slot.
+
+    ``noise_floor`` / ``detection_floor_multiple`` are accepted and not read
+    (the Poisson variance floor lives in the fit's weights, not here)."""
     sstab = report.stability.per_slot.get(role)
     comp = next((c for c in report.primary_fit.components if c.slot_role == role), None)
     boundary = [h for h in report.primary_fit.boundary_hits
                 if h.startswith(f"{role}:")]
 
     amplitude = float(comp.amplitude) if comp is not None else None
-    floor = detection_floor_multiple * noise_floor
+    # Noise-floor unit (2026-09-27): detectability is the support F test on the fit
+    # (fitting._component_support, the server's statistic), not multiples of an
+    # absolute 1-count floor. above_floor = supported (F >= SUPPORT_MIN_F);
+    # present_but_poorly_constrained = the fit gains from it but not
+    # significantly; not_confidently_detected = removing it costs nothing.
+    support = getattr(comp, "support", None) if comp is not None else None
     if amplitude is None:
         detect_status = "not_fitted"
-    elif amplitude >= floor:
+    elif support is None:
+        detect_status = "above_floor" if amplitude > 0 else "not_confidently_detected"
+    elif support.get("supported"):
         detect_status = "above_floor"
-    elif amplitude > noise_floor:
+    elif (support.get("delta_chi2") or 0.0) > 0:
         detect_status = "present_but_poorly_constrained"
     else:
         detect_status = "not_confidently_detected"
@@ -122,9 +134,9 @@ def build_confidence_vector(
         },
         "detectability": {
             "amplitude": amplitude,
-            "noise_floor": noise_floor,
-            "floor_multiple": detection_floor_multiple,
-            "floor_multiple_is_tunable": True,
+            "basis": "support_f_test",       # fitting._component_support, F >= SUPPORT_MIN_F
+            "support_f": (support or {}).get("f"),
+            "support_min_f": _SUPPORT_MIN_F,
             "status": detect_status,
         },
         "identifiability": {
diff --git a/autofit/engine.py b/autofit/engine.py
index dbf4fd7..8877d3c 100644
--- a/autofit/engine.py
+++ b/autofit/engine.py
@@ -39,6 +39,8 @@ from lmfit import Model, Parameters
 from lmfit.model import ModelResult
 from scipy.integrate import trapezoid
 
+import fitting as _fitting  # the server's support statistic: one definition (noise-floor unit)
+
 from fitting import _SHAPE_FUNCS, linear_background, shirley_background, smart_background
 
 from .candidates import (build_candidate_pool, build_detection_candidate,
@@ -637,6 +639,17 @@ class FittedComponent:
     amplitude: float
     shape_params: dict
     line_shape: Optional[LineShape] = None
+    # Noise-floor unit (2026-09-27): does the fit that produced this component need it?
+    # fitting._component_support on that fit — with the other components held
+    # as fitted, removing this one must make the fit significantly worse (F >=
+    # SUPPORT_MIN_F). The occupancy decisions (slot matching, the proposal
+    # gate, detectability) read this instead of an absolute amplitude floor
+    # of 1 count, which judged a slot "occupied" at amplitude 1.5 and not at
+    # 0.5 whatever the data's scale (sweep M9; design rule "thresholds on
+    # data-scaled quantities fail"). None only where no fit is behind the
+    # component (hand-built in tests): then occupancy falls back to amplitude
+    # > 0, a sign test.
+    support: Optional[dict] = None
 
 
 @dataclass
@@ -652,10 +665,79 @@ class FitOutcome:
     boundary_hits: list[str] = field(default_factory=list)
 
 
+def _component_supports(result: ModelResult) -> dict[str, dict]:
+    """``fitting._component_support`` for every peak component of an lmfit
+    result, keyed by prefix — the one definition the server uses (step (b)).
+    Empty when the result carries no data (never raises: occupancy then falls
+    back to the sign test)."""
+    try:
+        comps = result.eval_components()
+        data = np.asarray(result.data, float)
+        fitted = np.asarray(result.best_fit, float)
+        w = result.weights if result.weights is not None else np.ones_like(data)
+        w = np.broadcast_to(np.asarray(w, float), data.shape)
+        n_free_total = int(result.nvarys)
+    except Exception:
+        return {}
+    out = {}
+    for prefix, comp_y in comps.items():
+        n_free_comp = sum(1 for n, par in result.params.items()
+                          if n.startswith(prefix) and par.vary and par.expr is None)
+        try:
+            out[prefix] = _fitting._component_support(data, fitted, np.asarray(comp_y, float), w,
+                                                      n_free_comp, n_free_total)
+        except Exception:
+            continue
+    return out
+
+
+def _followed_supports(result: ModelResult, model: CandidateModel,
+                       supports: dict[str, dict]) -> dict[str, dict]:
+    """A linked slot whose AMPLITUDE is an expression of its parent's (a
+    spin-orbit partner at a fixed area ratio) has no amplitude of its own to
+    judge: it FOLLOWS its root's verdict, as the server's support check makes
+    a linked component follow its root (`individual_peaks[].support.follows`).
+    A linked slot with a free amplitude (only its position tied) keeps its own
+    verdict. Walks the chain to the root; a cycle or a missing parent leaves
+    the slot's own verdict."""
+    by_role = {s.role: s for s in model.slots}
+
+    def _tied(slot: ComponentSlot) -> bool:
+        par = result.params.get(f"{_slot_prefix(slot.role)}amplitude")
+        return (slot.linked_to is not None and slot.linked_to in by_role
+                and par is not None and par.expr is not None)
+
+    out = dict(supports)
+    for slot in model.slots:
+        if not _tied(slot):
+            continue
+        root, seen = slot, {slot.role}
+        while _tied(root):
+            root = by_role[root.linked_to]
+            if root.role in seen:
+                break
+            seen.add(root.role)
+        else:
+            rs = supports.get(_slot_prefix(root.role))
+            if rs is not None:
+                out[_slot_prefix(slot.role)] = {**rs, "follows": root.role}
+    return out
+
+
+def _occupies(comp: "FittedComponent") -> bool:
+    """A slot is occupied by a component the data support. No threshold
+    on any data-scaled quantity: the support F test where a fit is behind the
+    component, else the sign of its amplitude."""
+    if comp.support is not None:
+        return bool(comp.support.get("supported"))
+    return comp.amplitude > 0
+
+
 def _extract_fitted_components(
     result: ModelResult, model: CandidateModel
 ) -> list[FittedComponent]:
     out: list[FittedComponent] = []
+    supports = _followed_supports(result, model, _component_supports(result))
     for slot in model.slots:
         prefix = _slot_prefix(slot.role)
         pars = result.params
@@ -676,6 +758,7 @@ def _extract_fitted_components(
             slot_role=slot.role, position=center, fwhm=fwhm,
             amplitude=amplitude, shape_params=shape_params,
             line_shape=slot.line_shape,
+            support=supports.get(prefix),
         ))
     return out
 
@@ -1045,17 +1128,27 @@ def match_components_to_slots(
     """Assign fitted peaks to grammar slots (role + effective window + width).
 
     ``bound_overrides`` (fit_full_window) — see ``_effective_be_window``.
+
+    Occupancy (noise-floor unit, 2026-09-27): a component OCCUPIES a slot only
+    if the data support it (``_occupies``: the server's support F test on the
+    fit that produced it). A component the data do not support is NOT THERE:
+    it occupies no slot (the slot stays empty for persistence) and it is not
+    an orphan either — an orphan is a supported peak no slot expects, a
+    plausibility violation; "slot empty" is a different outcome. Such
+    components are returned under ``"__unsupported__"`` (reporting only). The
+    1-count floor this replaces made every component at amplitude <= 1 an
+    orphan wherever it sat.
     """
     slot_map: dict[str, Optional[FittedComponent]] = {s.role: None for s in model.slots}
     orphans: list[FittedComponent] = []
+    unsupported: list[FittedComponent] = []
     asym_shapes = {LineShape.ASYM_GL, LineShape.DS, LineShape.DS_G, LineShape.LACX}
 
     def _accepts(slot: ComponentSlot, comp: FittedComponent) -> bool:
         lo, hi = _effective_be_window(slot, components,
                                       (bound_overrides or {}).get(slot.role))
         return (lo <= comp.position <= hi
-                and slot.fwhm_range[0] <= comp.fwhm <= slot.fwhm_range[1]
-                and comp.amplitude > noise_floor)
+                and slot.fwhm_range[0] <= comp.fwhm <= slot.fwhm_range[1])
 
     def _window_center(slot: ComponentSlot) -> float:
         # NEVER the widened bound (Codex-caught, round 2): this is a
@@ -1072,12 +1165,15 @@ def match_components_to_slots(
         return 0.5 * (lo + hi)
 
     for comp in components:
+        if not _occupies(comp):
+            unsupported.append(comp)   # not there: neither an occupant nor an orphan
+            continue
         candidate_slots = [s for s in model.slots if _accepts(s, comp)]
         if not candidate_slots:
             orphans.append(FittedComponent(
                 slot_role="unmatched", position=comp.position, fwhm=comp.fwhm,
                 amplitude=comp.amplitude, shape_params=comp.shape_params,
-                line_shape=comp.line_shape,
+                line_shape=comp.line_shape, support=comp.support,
             ))
             continue
 
@@ -1095,7 +1191,7 @@ def match_components_to_slots(
         claimed = FittedComponent(
             slot_role=best_slot.role, position=comp.position, fwhm=comp.fwhm,
             amplitude=comp.amplitude, shape_params=comp.shape_params,
-            line_shape=comp.line_shape,
+            line_shape=comp.line_shape, support=comp.support,
         )
         if incumbent is None:
             slot_map[best_slot.role] = claimed
@@ -1108,6 +1204,7 @@ def match_components_to_slots(
                 orphans.append(comp)
 
     slot_map["__orphans__"] = orphans  # type: ignore[assignment]
+    slot_map["__unsupported__"] = unsupported  # type: ignore[assignment]
     return slot_map
 
 
@@ -1235,6 +1332,7 @@ def run_stability_analysis(
                                             bound_overrides=bound_overrides)
         if slot_map.pop("__orphans__", []):
             n_with_orphans += 1
+        slot_map.pop("__unsupported__", None)   # reporting only: those slots are empty
         for role, comp in slot_map.items():
             if comp is None:
                 continue
@@ -2229,8 +2327,10 @@ def _attempt_proposal(
     # to a wall (Codex fwhm-cap review, run B BLOCKER).
     width_cap_hit = f"{spec.role}:fwhm@max"
     pr.boundary_hits = _proposed_slot_pegs(primary, spec.role)
-    if comp.amplitude <= noise_floor:
-        return _fast(f"amplitude {comp.amplitude:.1f} ≤ noise_floor {noise_floor:.1f}")
+    if not _occupies(comp):
+        f = (comp.support or {}).get("f")
+        return _fast("not supported by the data (removing it does not make the fit significantly worse"
+                     + (f", F = {f:.2f} < {_fitting.SUPPORT_MIN_F:.0f}" if f is not None else "") + ")")
     spurious_hits = [h for h in pr.boundary_hits if h != width_cap_hit]
     if spurious_hits:
         return _fast(f"proposed slot boundary pegs: {spurious_hits}")
diff --git a/autofit/grammar.py b/autofit/grammar.py
index c9a85cd..2f5909d 100644
--- a/autofit/grammar.py
+++ b/autofit/grammar.py
@@ -181,11 +181,15 @@ class ComponentSlot:
     broad_justification: Optional[str] = None
 
     def contains(self, be: float, fwhm: float, amplitude: float,
-                 noise_floor: float) -> bool:
+                 noise_floor: float = 0.0) -> bool:
+        # Noise-floor unit (2026-09-27): occupancy is decided by the support F test on the
+        # fit (engine._occupies); this geometric check keeps only the sign of
+        # the amplitude. ``noise_floor`` is accepted and ignored (the engine
+        # has no caller of this method).
         return (
             self.be_window[0] <= be <= self.be_window[1]
             and self.fwhm_range[0] <= fwhm <= self.fwhm_range[1]
-            and amplitude > noise_floor
+            and amplitude > 0
         )
 
 
# Find Peaks occupancy: the server's support F test instead of a 1-count floor (2026-09-27)

Owner, 2026-09-27: "switch Find Peaks' occupancy test from the absolute
1.0-count floor to the same F test the server's support check uses, per
docs/findings/noise-floor-occupancy/. Scale-free, no tolerance, per the
design rule. Build to 'ready for deploy' only — do NOT deploy it. Enumerate
sites first; Codex x2."

Starting point: `docs/findings/noise-floor-occupancy/variant_F_support_test.patch`
(measured in F3) plus the README's two required follow-ups.

## 1. Sites — every read of `noise_floor` in the Find Peaks engine (`autofit/`)

`noise_floor` (default 1.0; the page never sends it) had two jobs.

**A. Poisson variance floor, σ = √max(y, noise_floor) — KEPT, unchanged.** Not
a decision threshold: it is the counting convention the server's weights use
(`fitting`: 1/√max(counts, 1)).

| site | what |
|---|---|
| `candidates.py:621–622` | local σ for candidate detection gates |
| `engine.py` `compute_residual_diagnostics` | standardised residuals r/σ |
| `engine.py` preseed local σ (`_detect_*` / `local_sigma`) | preseed SNR gate |
| `engine.py` fit weights (`sigma = sqrt(max(y, noise_floor))`, two sites) | the fit's weights |
| `engine.py` `_attempt_proposal` local σ | the proposal's SNR gate (below) |

**B. Occupancy threshold, `amplitude > noise_floor` — REPLACED by the support F
test.**

| # | site | before | after |
|---|---|---|---|
| B1 | `engine.match_components_to_slots._accepts` | a component occupies a slot if its window/width fit AND amplitude > 1 count | window/width only decide WHICH slot; whether it is THERE is `_occupies(comp)` = `fitting._component_support(...)["supported"]` on the fit that produced it (F ≥ `SUPPORT_MIN_F`) |
| B2 | `engine._attempt_proposal` | a proposed slot is rejected if amplitude ≤ 1 count | rejected if `not _occupies(comp)`; the message names F |
| B3 | `confidence.build_confidence_vector` detectability | `above_floor` ≥ 3 × floor, `present_but_poorly_constrained` > floor | `above_floor` = supported; `present_but_poorly_constrained` = Δχ² > 0 but F < 10; `not_confidently_detected` = removing it costs nothing. Status values unchanged (the payload's consumers: `test_methods_seam`, `test_browser_schema_roundtrip`; the page reads none of the detectability fields) |
| B4 | `grammar.ComponentSlot.contains` | amplitude > noise_floor | amplitude > 0 (sign only; no engine caller) |

Where the support comes from: `engine._component_supports(result)` evaluates
`fitting._component_support` for every component of an lmfit result (data,
best fit, the component's curve, the fit's own weights, its free-parameter
count) once, in `_extract_fitted_components`; it rides on
`FittedComponent.support` through slot matching. A component with no fit
behind it (hand-built in tests) falls back to `amplitude > 0`.

**C. Orphans vs empty slots (README follow-up 1).** Before, a component that
failed occupancy had no accepting slot and became an ORPHAN — counted in
`orphan_rate`, a plausibility violation ("a peak nobody expects"). Under F that
would turn every unsupported in-window component into an extra-peak
violation. Now `match_components_to_slots` sets an unsupported component
aside (`"__unsupported__"`, reporting only): it occupies no slot (that slot's
persistence drops, as it should — the slot is empty) and it is NOT an orphan.
An orphan is a SUPPORTED component no slot's window/width accepts.

**Related, NOT changed: `engine._attempt_proposal`'s SNR gate** (`amplitude <
PROPOSAL_AMPLITUDE_SNR × local σ`, σ the Poisson noise). A signal-to-noise
ratio under the same counting assumption as the weights, not the 1-count
floor; listed so review can challenge it.

**E. Linked components follow their root.** The server's support check makes
a linked component FOLLOW its root (`individual_peaks[].support.follows`). The
engine now does the same for a slot whose amplitude is an expression of its
parent's (a spin-orbit partner at a fixed area ratio): `_followed_supports`
copies the root's verdict with `follows: <root role>`. A linked slot with a
free amplitude (only its position tied) keeps its own verdict.

**D. The model-mismatch honesty signal (README follow-up 2).** See §3 — an
owner decision.

## 2. Measurements

### Stress honesty battery (`tests/autofit/test_stress_honesty.py`)

With F + the orphan split: 11 passed, 1 failed — `test_bg_mismatch_surfaces_loudly`
(a Shirley-shaped truth fitted with straight-line backgrounds), as the README
predicted. Under F the winner is **P2, the TRUE two-peak model**
(`true_candidates=("P2",)`); P3's third component compensated for the wrong
background, F calls it unsupported (its gain divided by the misfit χ²ᵣ ≈ 284),
P3's persistence for that slot drops to 0 and P3 leaves the conditional pool.
The result still carries the winner's χ²ᵣ 308.7 (comparison table), the
winner row's `autocorr_flag`, and `filtered_dominant_alternative` (P3,
ΔBIC* 153 — the page's red "a better-scoring model was set aside" banner); it
is no longer `conditional`.

### Candidate mismatch signals, measured (winner of each run; ×0.1 = the same spectrum as a rate)

| spectrum | scale | χ²ᵣ | residual lag-1 autocorrelation flagged | n_eff / n |
|---|---|---|---|---|
| stress: bg mismatch | ×1 / ×0.1 | 308.7 / 30.9 | yes / yes | 0.0075 / 0.0075 |
| stress: bg matched control | ×1 / ×0.1 | 1.31 / 0.13 | no / no | ~1.0 / ~1.0 |
| 8 real committed C 1s scans (3 gate anchors + 5) | ×1 | 1.30–6.46 | **yes on 8 of 8** | 0.10–0.55 |
| same | ×0.1 | 0.15–3.51 | yes on 8 of 8 | 0.04–0.49 |

* χ²ᵣ is not scale-free (it moves with the counts: ×0.1 divides it by 10), and
  on real data it grows with the counts for a slightly imperfect lineshape — a
  χ²ᵣ cutoff is exactly the design rule's failure.
* The residual lag-1 autocorrelation IS scale-free (n_eff/n identical at ×1 and
  ×0.1), but real XPS fits are not noise-limited: every real winner has
  structured residuals. As a flag it fires on everything; as a number it
  separates the stress case (0.0075) from real fits (≥ 0.04) only by a factor
  of ~5 and only with a chosen constant.
* So no residual- or χ²ᵣ-based signal distinguishes "the background is wrong"
  from "the lineshape is not perfect" without a chosen cutoff.

(Also found, pre-existing and unchanged by this unit: the engine's model
selection itself is not rescale-invariant — on main a ×0.1 rescale changes the
winner or the conditional tier on 2 of the 8 real scans (Scan_8 UCl4, Scan_7 8-JT); BIC with Poisson
weights assumes counts.)

### Real-data gates (`RUN_AUTOFIT_GATE=1`: C 1s, U 4f, B 1s / Cl 2p parity; Bayesian real and U 4f unresolved; candidate-pool real; stress honesty)

| | main (0bb200b) | this branch |
|---|---|---|
| passed / failed | 26 / 1 | 26 / 1 |
| the failure | `test_candidate_pool_real_gate` ds8 "C1s Scan": the detected shoulder is not in the final model — IDENTICAL peaks on both (the sweep hits its 240 s budget after 3 of 6 candidates); PRE-EXISTING, on local-only held-out data never committed (the datasets were symlinked in from the main checkout for this run) | the same |
| stress honesty | 12 / 12 (old wording) | 12 / 12 (option-A wording, §3) |

### What F changes on real Find Peaks results (8 committed C 1s scans, gate options, ×1 and ×0.1; both engines run twice on the differing scans — both reproduce themselves 12 / 12, so every difference below is F's)

Final code (incl. §1 E, re-measured after it — one run changed, Scan_6 ×0.1):
10 of 16 runs unchanged. Changed:

| scan | scale | main | this branch |
|---|---|---|---|
| 1-GTA Scan_6 (gate anchor) | ×1 | MG2 (conditional), χ²ᵣ 2.04 | AG2+preseed (conditional), χ²ᵣ 3.69 — MG2's lowest slot persistence drops to 0.67: in one of its three refits a component was not supported by the data, so MG2 is no longer "stable" (the 1-count floor had counted that component as present). The C 1s gate still passes (graphite centre, satellite, envelope R) |
| 1-GTA Scan_2 | ×1 | MG2, χ²ᵣ 1.54 | MG3, χ²ᵣ 1.50 |
| 8-JT Scan_7 | ×1 | MG2, χ²ᵣ 5.21 | MG3, χ²ᵣ 5.19 |
| 1-GTA Scan_6 | ×0.1 | MG2 (conditional), χ²ᵣ 0.20 | MG3 (conditional), χ²ᵣ 0.22 |
| 8-JT Scan_5 | ×0.1 | MG3 conditional | MG3 not conditional |
| UCl4 Scan_3 | ×0.1 | MG2 | MG3 |

**Scale-dependence of the OUTCOME got WORSE on these scans, not better:** main
changes its result under ×0.1 on 2 of 8 scans, this branch on 6 of 8 (Scan_8,
Scan_6, Scan_5, 1-GTA Scan_2, Scan_3, Scan_7). The occupancy statistic itself
is invariant (pinned in `test_occupancy_support.py`), but the pipeline around
it is not: the candidate-detection and proposal gates are Poisson signal-to-
noise ratios, and BIC* with Poisson weights assumes counts, so ×0.1 changes
the candidate set and the ranking. Under the 1-count floor that never reached
occupancy on real data (every real amplitude is far above 1 count, so the
floor never flipped); under F — the likely mechanism, NOT traced scan by
scan — a MARGINAL component (F near 10) now decides a candidate's stability,
and those small upstream differences push it across.
In words: F makes the occupancy test scale-free and honest about marginal
components, and in doing so exposes that the rest of Find Peaks is not
scale-free. Owner-relevant: it is not a reason for C by itself (the ×1 results
are what students get from counts data), but it is not the "scale-free Find
Peaks" the design rule might suggest.

### A browser test's NOISE-FREE fixture

`tests/test_browser_find_peaks_full_window.py` (two of four) failed on this
branch: its synthetic C 1s spectrum is noise-free (300 + one Gaussian), fitted
to rounding (χ²ᵣ 0.00), where the support F test is meaningless (the
required-refit known limit in CLAUDE.md). The engine's outcome there turns on
the upload's rounding and wall-clock budgets ON MAIN TOO: through the page,
main returned a conditional fit and the branch none; through a direct
`/api/analyze` replay (4-dp upload) main returned NO survivor and the branch a
clean one. The test is about the apply path with the full-window option off,
not the fit, so its fixture now carries fixed pseudo-random Poisson noise
(√counts × a seeded normal): 4 / 4 pass on main AND on this branch. Known
limit, as for the required-refit test: on noise-free data the occupancy
verdicts are not meaningful.

## 3. OWNER DECISION — the background-mismatch honesty test

`test_bg_mismatch_surfaces_loudly` pinned "a wrong background is never a clean
confident result" through the conditional tier, and that tier was reached only
through the component that compensated for the wrong background (P3's third).
The README asked for a mismatch signal that does not ride on it; §2 shows the
signals at hand either are not scale-free (χ²ᵣ) or fire on every real fit
(residual structure). Options:

| | what | cost |
|---|---|---|
| **A (recommended; implemented on this branch)** | Accept F's outcome and re-state the test's contract to what is true and scale-independent in kind: the engine returns the true 2-peak model, the winner's χ²ᵣ is reported and grossly elevated, and the result carries `filtered_dominant_alternative` (the page's red banner). No new rule. The principled mismatch check is a comparison of BACKGROUND models (the matched-control case shows Shirley candidates absorb the integral background) — logged as its own unit | a wrong-background result is no longer marked "conditional"; the red banner remains |
| B | a result-level `model_mismatch` flag from a chosen constant (e.g. n_eff/n < 0.02, between the stress case's 0.0075 and real data's ≥ 0.04) | a new threshold on a data-dependent quantity (n_eff/n also depends on the sampling step) — the design rule's failure; needs calibration; NOT recommended |
| C | keep the 1-count floor until a background-comparison check exists | the occupancy floor stays scale-dependent |

A is what this branch ships; if the owner prefers C the branch waits.

exec
/bin/zsh -lc "cat docs/findings/noise-floor-occupancy/README.md; rg -n 'component_support|SUPPORT_MIN_F|support.*follows|n_free_comp' fitting.py; rg -n 'noise_floor|_occupies|slot_map|\\.contains\\(|support|amplitude [<>]=?' autofit" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
# Find Peaks' 1-count occupancy floor → scale-free: PARKED for an owner decision (2026-09-27)

Part of unit F3 (sweep M9, first bullet). The other half of F3 — the Auto-Fit
C1s gate judging a stale typed window (sweep M5) — ships on its own in
`fix-noise-floor-scale-free` and does not depend on this.

## What was found

`noise_floor` (default 1.0, never sent by the page) does two jobs in
`autofit/`:

1. a Poisson variance floor, `sigma = sqrt(max(y, noise_floor))` — the
   counting convention the server's weights use; not a decision threshold,
   left as is by both variants;
2. an OCCUPANCY threshold, `amplitude > noise_floor` — whether a fitted
   component occupies its slot (`match_components_to_slots`), whether a
   proposed slot survives (`_evaluate_proposal`), the detectability status
   (`build_confidence_vector`). A slot is "occupied" at amplitude 1.5 and not
   at 0.5 whatever the data's scale; persistence, the absent-slot test and the
   stability gate follow from it. This is the design rule's case.

Both variants replace (2) with a statistic on the component's own fit
(computed once when the component is extracted from its lmfit result and
carried on `FittedComponent.support`), leave (1) alone, and fall back to
`amplitude > 0` (a sign test) for a component with no fit behind it. They
differ in ONE line — what "occupied" means:

| variant | occupied when | patch |
|---|---|---|
| **F** — the server's support test | `fitting._component_support` "supported": Δχ² > 0 and F = (Δχ²/p) / (χ²_with/dof) ≥ 10 — the step (b) "not supported by the data" statistic and threshold | `variant_F_support_test.patch` |
| **LR** — the weighted removal gain per parameter (first draft called it a "Poisson likelihood ratio"; it is neither a likelihood nor a refit) | Δχ²/p ≥ 10 on the Poisson-weighted χ², with the other components held, NOT divided by the fit's own misfit χ²_with/dof | `variant_LR_likelihood_ratio.patch` |

Neither carries a tolerance. Only F is a RATIO of χ² quantities and so
invariant to a uniform rescaling of the intensities; LR is not (Codex rounds
1–2: ×0.1 turns Δχ²/p = 32 into 3.2 and flips it, while F stays 16). F's
invariance is itself QUALIFIED by the Poisson variance floor both patches
keep (σ² = max(counts, 1)): a channel at or below 1 count weighs differently
after a rescaling, so F can move (round 2: 11.67 → 3.18, and 10.07 → 9.32,
on data with a channel near 1 count). Exact invariance holds only where every
channel stays above the floor.

## The evidence

| suite | baseline (today) | F | LR |
|---|---|---|---|
| gated real-data parity gates + stress honesty (`RUN_AUTOFIT_GATE=1`: C 1s parity, Bayesian real, candidate-pool real, U 4f unresolved, stress honesty) | 17 passed, 4 skipped | **16 passed, 1 FAILED** | 17 passed, 4 skipped |
| always-on `tests/autofit` (incl. the C 1s / region parity batteries) | green | **1 failed** (the same stress case), 556 passed | 557 passed, 7 skipped |

The failing case, `test_stress_honesty.py::test_bg_mismatch_surfaces_loudly`:
a Shirley-shaped truth fitted with a straight-line background, χ²ᵣ ≈ 280–470
for every candidate. The test requires the mismatch to be machine-visible
("conditional" tier), never a clean confident result. Today the 3-component
candidate P3 is stable but violates plausibility, enters the conditional
pool, and its bound-fixed refit wins via the decisive override →
`conditional: true`. Under F, P3's third component has F < 10 BECAUSE the fit
is so bad: F divides the gain by χ²_with/dof ≈ 284, so a component that
removes a large χ² still reads "unsupported"; it becomes an orphan, P3's
persistence drops to 0, P3 leaves the conditional pool, and P2 (χ²ᵣ 309) is
returned as a CLEAN survivor. Under LR the same component is occupied (its
gain per parameter is far above 10 Poisson units) and the result is
conditional, as today.

## Codex review of this write-up (F3 round 1, `f3_c1s_gate_verdict_run{A,B}.md`) — the recommendation below replaces the first draft's

Both runs reproduced the measurements and the mechanism (P3's third component:
Δχ² ≈ 10 702, F ≈ 9.42 with four free parameters → persistence 0, orphan rate 1,
out of the decisive-override pool). They also found three things wrong with
the first draft's recommendation of LR, all of which hold:

1. **LR is not scale-free.** "Dimensionless" is not "invariant under a change
   of intensity units": with Poisson weights the gain Δχ² scales with the
   counts, so multiplying a spectrum by 0.1 (CPS instead of counts, a
   normalisation) turned Δχ²/p = 32 into 3.2 and flipped the verdict, while F
   stayed at 16 — F is a RATIO of two χ² quantities and is invariant. The
   design rule asks for exactly that invariance. (The statistic is also a
   gain with the other components held fixed, not a refitted likelihood
   ratio; the draft's name overstated it.)
2. **The LR patch is internally inconsistent**: occupancy used Δχ²/p while
   detectability still used `support.supported` and reported
   `basis: support_f_test`, so a component could be "unoccupied" and
   `above_floor` at once, and a proposal rejection could print "F = 32.00 < 10".
3. **The stress case does not show F rejecting a real peak.** The fixture
   (`tests/autofit/stress_cases.py`) has TWO true peaks; P3's third component
   compensates for the wrong background. F calls it unsupported — defensibly —
   and the honesty flag then disappears because the "conditional" tier
   depended on keeping that background-compensating component. The F result
   also still carries `filtered_dominant_alternative` (P3, ΔBIC ≈ 153), which
   the page shows: not a silent clean answer.

Both runs, independently: **start from F** (one support definition across
the app, invariant to intensity units) and fix two things around it before
shipping:

- an unsupported component INSIDE its slot's window must not become an
  "orphan" (an unexplained extra peak) — today (and in both patches) a
  component that fails occupancy has no accepting slot and counts toward
  `orphan_rate`, a plausibility violation; "slot empty" and "peak nobody
  expects" need distinct treatment;
- the model-mismatch honesty signal must not depend on a component that only
  compensates for a wrong background — report the mismatch (χ²ᵣ ≫ 1, the
  residual structure) on its own terms.

## The decision (owner)

- **Adopt F as the occupancy statistic** (recommended, both reviewers), as a
  unit of its own with the two follow-ups above, measured on the gated and
  always-on suites; the honesty test is then re-examined against a
  mismatch signal that does not ride on P3.
- **LR**: withdrawn as a recommendation (not invariant to intensity units).
- Either way `noise_floor` survives only as the Poisson variance floor (both
  patches leave it; it keeps the raw-count assumption the server's weights
  make). That floor is what limits F's invariance to data whose channels stay
  above 1 count (see above) — a property the server's step (b) verdict shares.

The two patches stay here as the measured starting points:
`git apply docs/findings/noise-floor-occupancy/variant_F_support_test.patch`.
1441:SUPPORT_MIN_F = 10.0
1444:def _component_support(y_sub, fitted_sub, comp_y, weights, n_free_comp, n_free_total) -> dict[str, Any]:
1451:    p = max(1, int(n_free_comp))
1460:            "supported": bool(delta > 0 and (chi_with == 0 or f >= SUPPORT_MIN_F))}
1475:                        chi2_with, n_free_comp, n_free_total) -> dict[str, Any]:
1507:    p = max(1, int(n_free_comp))
1524:        required = f >= SUPPORT_MIN_F
1920:                    n_free_comp = sum(1 for n, par in result.params.items()
1924:                        float(result.chisqr), n_free_comp, result.nvarys)}
1979:        n_free_comp = sum(1 for n, par in result.params.items() if n.startswith(prefix) and par.vary and par.expr is None)
1980:        support = _component_support(y_sub, fitted_sub, peak_y, weights, n_free_comp, result.nvarys)
2006:            ip["support"]["follows"] = by_id[root]["id"]
autofit/candidates.py:417:    fit does not support).  Slot geometry scales with each feature's own
autofit/candidates.py:551:    noise_floor: float = 1.0,
autofit/candidates.py:621:            return float(np.median(np.sqrt(np.maximum(y[mask], noise_floor))))
autofit/candidates.py:622:        return float(np.sqrt(max(noise_floor, 1.0)))
autofit/cited_values.py:229:            f"{path}: unsupported schema_version {sv!r} (expected 1)")
autofit/reference.py:56:                    f"{path.name}: unsupported project version "
autofit/noise.py:318:        # the shifted support) contaminate every T row whose smoother
autofit/engine.py:42:import fitting as _fitting  # the server's support statistic: one definition (noise-floor unit)
autofit/engine.py:98:# basin as the best minimum (best_basin_support) — reporting-only honesty
autofit/engine.py:643:    # fitting._component_support on that fit — with the other components held
autofit/engine.py:652:    support: Optional[dict] = None
autofit/engine.py:668:def _component_supports(result: ModelResult) -> dict[str, dict]:
autofit/engine.py:669:    """``fitting._component_support`` for every peak component of an lmfit
autofit/engine.py:687:            out[prefix] = _fitting._component_support(data, fitted, np.asarray(comp_y, float), w,
autofit/engine.py:694:def _followed_supports(result: ModelResult, model: CandidateModel,
autofit/engine.py:695:                       supports: dict[str, dict]) -> dict[str, dict]:
autofit/engine.py:698:    judge: it FOLLOWS its root's verdict, as the server's support check makes
autofit/engine.py:699:    a linked component follow its root (`individual_peaks[].support.follows`).
autofit/engine.py:710:    out = dict(supports)
autofit/engine.py:721:            rs = supports.get(_slot_prefix(root.role))
autofit/engine.py:727:def _occupies(comp: "FittedComponent") -> bool:
autofit/engine.py:728:    """A slot is occupied by a component the data support. No threshold
autofit/engine.py:729:    on any data-scaled quantity: the support F test where a fit is behind the
autofit/engine.py:731:    if comp.support is not None:
autofit/engine.py:732:        return bool(comp.support.get("supported"))
autofit/engine.py:733:    return comp.amplitude > 0
autofit/engine.py:740:    supports = _followed_supports(result, model, _component_supports(result))
autofit/engine.py:761:            support=supports.get(prefix),
autofit/engine.py:1125:    noise_floor: float,
autofit/engine.py:1133:    if the data support it (``_occupies``: the server's support F test on the
autofit/engine.py:1134:    fit that produced it). A component the data do not support is NOT THERE:
autofit/engine.py:1136:    an orphan either — an orphan is a supported peak no slot expects, a
autofit/engine.py:1138:    components are returned under ``"__unsupported__"`` (reporting only). The
autofit/engine.py:1139:    1-count floor this replaces made every component at amplitude <= 1 an
autofit/engine.py:1142:    slot_map: dict[str, Optional[FittedComponent]] = {s.role: None for s in model.slots}
autofit/engine.py:1144:    unsupported: list[FittedComponent] = []
autofit/engine.py:1168:        if not _occupies(comp):
autofit/engine.py:1169:            unsupported.append(comp)   # not there: neither an occupant nor an orphan
autofit/engine.py:1176:                line_shape=comp.line_shape, support=comp.support,
autofit/engine.py:1190:        incumbent = slot_map[best_slot.role]
autofit/engine.py:1194:            line_shape=comp.line_shape, support=comp.support,
autofit/engine.py:1197:            slot_map[best_slot.role] = claimed
autofit/engine.py:1202:                slot_map[best_slot.role] = claimed
autofit/engine.py:1206:    slot_map["__orphans__"] = orphans  # type: ignore[assignment]
autofit/engine.py:1207:    slot_map["__unsupported__"] = unsupported  # type: ignore[assignment]
autofit/engine.py:1208:    return slot_map
autofit/engine.py:1243:    best_basin_support: int = 0
autofit/engine.py:1265:    noise_floor: float,
autofit/engine.py:1331:        slot_map = match_components_to_slots(outcome.components, model, noise_floor,
autofit/engine.py:1333:        if slot_map.pop("__orphans__", []):
autofit/engine.py:1335:        slot_map.pop("__unsupported__", None)   # reporting only: those slots are empty
autofit/engine.py:1336:        for role, comp in slot_map.items():
autofit/engine.py:1364:    basin_support = sum(1 for c in refit_chis
autofit/engine.py:1371:        best_basin_support=basin_support,
autofit/engine.py:1504:    noise_floor: float,
autofit/engine.py:1509:    sigma = np.sqrt(np.maximum(y, noise_floor))
autofit/engine.py:1906:    noise_floor: float = 1.0,
autofit/engine.py:1954:        local_sigma = float(np.median(np.sqrt(np.maximum(y_asc[mask], noise_floor)))) \
autofit/engine.py:1955:            if mask.sum() > 1 else float(np.sqrt(max(noise_floor, 1.0)))
autofit/engine.py:2105:    noise_floor: float,
autofit/engine.py:2112:    sigma = np.sqrt(np.maximum(y, noise_floor))
autofit/engine.py:2261:    noise_floor: float,
autofit/engine.py:2330:    if not _occupies(comp):
autofit/engine.py:2331:        f = (comp.support or {}).get("f")
autofit/engine.py:2332:        return _fast("not supported by the data (removing it does not make the fit significantly worse"
autofit/engine.py:2340:    local_sigma = float(np.median(np.sqrt(np.maximum(y[mask], noise_floor)))) \
autofit/engine.py:2341:        if mask.sum() > 1 else float(np.sqrt(max(noise_floor, 1.0)))
autofit/engine.py:2342:    if comp.amplitude < PROPOSAL_AMPLITUDE_SNR * local_sigma:
autofit/engine.py:2373:        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
autofit/engine.py:2412:    residuals = compute_residual_diagnostics(x, y, y_fit_aug, noise_floor, diagnostic_windows)
autofit/engine.py:2491:    noise_floor: float,
autofit/engine.py:2546:        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
autofit/engine.py:2560:            x, y, y_fit, noise_floor, diagnostic_windows),
autofit/engine.py:2586:    noise_floor: float,
autofit/engine.py:2607:                                   diagnostic_windows, noise_floor,
autofit/engine.py:2654:    noise_floor: float = 1.0,
autofit/engine.py:2727:            noise_floor=noise_floor,
autofit/engine.py:2746:                noise_floor=noise_floor,
autofit/engine.py:2926:            noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
autofit/engine.py:2940:        residuals = compute_residual_diagnostics(x, y, y_fit, noise_floor, diagnostic_windows)
autofit/engine.py:2982:                    x, y, current_y_fit, noise_floor, current.model,
autofit/engine.py:3004:                        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
autofit/engine.py:3054:        noise_floor=noise_floor,
autofit/grammar.py:184:                 noise_floor: float = 0.0) -> bool:
autofit/grammar.py:185:        # Noise-floor unit (2026-09-27): occupancy is decided by the support F test on the
autofit/grammar.py:186:        # fit (engine._occupies); this geometric check keeps only the sign of
autofit/grammar.py:187:        # the amplitude. ``noise_floor`` is accepted and ignored (the engine
autofit/grammar.py:192:            and amplitude > 0
autofit/confidence.py:28:from fitting import SUPPORT_MIN_F as _SUPPORT_MIN_F  # the server's support threshold: one definition
autofit/confidence.py:32:# No longer read (noise-floor unit, 2026-09-27): detectability is the support
autofit/confidence.py:91:    noise_floor: float,
autofit/confidence.py:96:    ``noise_floor`` / ``detection_floor_multiple`` are accepted and not read
autofit/confidence.py:104:    # Noise-floor unit (2026-09-27): detectability is the support F test on the fit
autofit/confidence.py:105:    # (fitting._component_support, the server's statistic), not multiples of an
autofit/confidence.py:106:    # absolute 1-count floor. above_floor = supported (F >= SUPPORT_MIN_F);
autofit/confidence.py:109:    support = getattr(comp, "support", None) if comp is not None else None
autofit/confidence.py:112:    elif support is None:
autofit/confidence.py:113:        detect_status = "above_floor" if amplitude > 0 else "not_confidently_detected"
autofit/confidence.py:114:    elif support.get("supported"):
autofit/confidence.py:116:    elif (support.get("delta_chi2") or 0.0) > 0:
autofit/confidence.py:137:            "basis": "support_f_test",       # fitting._component_support, F >= SUPPORT_MIN_F
autofit/confidence.py:138:            "support_f": (support or {}).get("f"),
autofit/confidence.py:139:            "support_min_f": _SUPPORT_MIN_F,
autofit/regions/u4f.py:128:             "status": "VERIFIED", "source": "Ilton & Bagus 2011 — supports the "
autofit/methods/ic_model_comparison.py:22:    "noise_floor", "n_refits", "rng_seed", "candidate_filter",
autofit/methods/ic_model_comparison.py:57:        noise_floor = float(opts.pop("noise_floor", 1.0))
autofit/methods/ic_model_comparison.py:61:            noise_floor=noise_floor,
autofit/methods/ic_model_comparison.py:107:            slot.role: build_confidence_vector(top, slot.role, noise_floor)
autofit/methods/ic_model_comparison.py:150:                    "supports — treat EVERY component as a low-confidence "
autofit/methods/ic_model_comparison.py:297:            "best_minimum_basin_support": int(r.stability.best_basin_support),
autofit/methods/bayesian_exchange_mc.py:289:    "rng_seed", "candidate_filter", "ci_level", "noise_floor",
autofit/methods/bayesian_exchange_mc.py:328:        opts.pop("noise_floor", None)     # accepted for symmetry; unused
autofit/regions/n1s.py:74:            "Stage-3 minimal N 1s support, not the full cookbook module"
autofit/methods/sparse_map.py:13:the selected support), and heavy overlap/asymmetric shapes are NOT its
autofit/methods/sparse_map.py:26:  of the local FWHM), the support is DEBIASED by non-negative least squares,
autofit/methods/sparse_map.py:148:def _cluster_support(idx: list[int], atoms, amps: np.ndarray, merge_fraction: float):
autofit/methods/sparse_map.py:236:            # debiased amplitudes: NNLS on the raw (un-normalized) support;
autofit/methods/sparse_map.py:237:            # the ACTIVE support is what NNLS keeps nonzero — zero-amplitude
autofit/methods/sparse_map.py:253:            clusters = _cluster_support(act_idx, atoms, amps, cfg["merge_fraction"])
autofit/methods/sparse_map.py:266:                message="no λ on the path produced a non-empty support")
autofit/methods/sparse_map.py:297:                    "note": "L1-selected support; grid-quantized centers/widths; "

exec
/bin/zsh -lc "sed -n '95,190p' docs/superpowers/plans/2026-09-27-occupancy-f-test.md; sed -n '1430,1465p' fitting.py; sed -n '1930,2015p' fitting.py; sed -n '250,630p' autofit/engine.py; sed -n '760,1035p' autofit/engine.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
  χ²ᵣ cutoff is exactly the design rule's failure.
* The residual lag-1 autocorrelation IS scale-free (n_eff/n identical at ×1 and
  ×0.1), but real XPS fits are not noise-limited: every real winner has
  structured residuals. As a flag it fires on everything; as a number it
  separates the stress case (0.0075) from real fits (≥ 0.04) only by a factor
  of ~5 and only with a chosen constant.
* So no residual- or χ²ᵣ-based signal distinguishes "the background is wrong"
  from "the lineshape is not perfect" without a chosen cutoff.

(Also found, pre-existing and unchanged by this unit: the engine's model
selection itself is not rescale-invariant — on main a ×0.1 rescale changes the
winner or the conditional tier on 2 of the 8 real scans (Scan_8 UCl4, Scan_7 8-JT); BIC with Poisson
weights assumes counts.)

### Real-data gates (`RUN_AUTOFIT_GATE=1`: C 1s, U 4f, B 1s / Cl 2p parity; Bayesian real and U 4f unresolved; candidate-pool real; stress honesty)

| | main (0bb200b) | this branch |
|---|---|---|
| passed / failed | 26 / 1 | 26 / 1 |
| the failure | `test_candidate_pool_real_gate` ds8 "C1s Scan": the detected shoulder is not in the final model — IDENTICAL peaks on both (the sweep hits its 240 s budget after 3 of 6 candidates); PRE-EXISTING, on local-only held-out data never committed (the datasets were symlinked in from the main checkout for this run) | the same |
| stress honesty | 12 / 12 (old wording) | 12 / 12 (option-A wording, §3) |

### What F changes on real Find Peaks results (8 committed C 1s scans, gate options, ×1 and ×0.1; both engines run twice on the differing scans — both reproduce themselves 12 / 12, so every difference below is F's)

Final code (incl. §1 E, re-measured after it — one run changed, Scan_6 ×0.1):
10 of 16 runs unchanged. Changed:

| scan | scale | main | this branch |
|---|---|---|---|
| 1-GTA Scan_6 (gate anchor) | ×1 | MG2 (conditional), χ²ᵣ 2.04 | AG2+preseed (conditional), χ²ᵣ 3.69 — MG2's lowest slot persistence drops to 0.67: in one of its three refits a component was not supported by the data, so MG2 is no longer "stable" (the 1-count floor had counted that component as present). The C 1s gate still passes (graphite centre, satellite, envelope R) |
| 1-GTA Scan_2 | ×1 | MG2, χ²ᵣ 1.54 | MG3, χ²ᵣ 1.50 |
| 8-JT Scan_7 | ×1 | MG2, χ²ᵣ 5.21 | MG3, χ²ᵣ 5.19 |
| 1-GTA Scan_6 | ×0.1 | MG2 (conditional), χ²ᵣ 0.20 | MG3 (conditional), χ²ᵣ 0.22 |
| 8-JT Scan_5 | ×0.1 | MG3 conditional | MG3 not conditional |
| UCl4 Scan_3 | ×0.1 | MG2 | MG3 |

**Scale-dependence of the OUTCOME got WORSE on these scans, not better:** main
changes its result under ×0.1 on 2 of 8 scans, this branch on 6 of 8 (Scan_8,
Scan_6, Scan_5, 1-GTA Scan_2, Scan_3, Scan_7). The occupancy statistic itself
is invariant (pinned in `test_occupancy_support.py`), but the pipeline around
it is not: the candidate-detection and proposal gates are Poisson signal-to-
noise ratios, and BIC* with Poisson weights assumes counts, so ×0.1 changes
the candidate set and the ranking. Under the 1-count floor that never reached
occupancy on real data (every real amplitude is far above 1 count, so the
floor never flipped); under F — the likely mechanism, NOT traced scan by
scan — a MARGINAL component (F near 10) now decides a candidate's stability,
and those small upstream differences push it across.
In words: F makes the occupancy test scale-free and honest about marginal
components, and in doing so exposes that the rest of Find Peaks is not
scale-free. Owner-relevant: it is not a reason for C by itself (the ×1 results
are what students get from counts data), but it is not the "scale-free Find
Peaks" the design rule might suggest.

### A browser test's NOISE-FREE fixture

`tests/test_browser_find_peaks_full_window.py` (two of four) failed on this
branch: its synthetic C 1s spectrum is noise-free (300 + one Gaussian), fitted
to rounding (χ²ᵣ 0.00), where the support F test is meaningless (the
required-refit known limit in CLAUDE.md). The engine's outcome there turns on
the upload's rounding and wall-clock budgets ON MAIN TOO: through the page,
main returned a conditional fit and the branch none; through a direct
`/api/analyze` replay (4-dp upload) main returned NO survivor and the branch a
clean one. The test is about the apply path with the full-window option off,
not the fit, so its fixture now carries fixed pseudo-random Poisson noise
(√counts × a seeded normal): 4 / 4 pass on main AND on this branch. Known
limit, as for the required-refit test: on noise-free data the occupancy
verdicts are not meaningful.

## 3. OWNER DECISION — the background-mismatch honesty test

`test_bg_mismatch_surfaces_loudly` pinned "a wrong background is never a clean
confident result" through the conditional tier, and that tier was reached only
through the component that compensated for the wrong background (P3's third).
The README asked for a mismatch signal that does not ride on it; §2 shows the
signals at hand either are not scale-free (χ²ᵣ) or fire on every real fit
(residual structure). Options:

| | what | cost |
|---|---|---|
| **A (recommended; implemented on this branch)** | Accept F's outcome and re-state the test's contract to what is true and scale-independent in kind: the engine returns the true 2-peak model, the winner's χ²ᵣ is reported and grossly elevated, and the result carries `filtered_dominant_alternative` (the page's red banner). No new rule. The principled mismatch check is a comparison of BACKGROUND models (the matched-control case shows Shirley candidates absorb the integral background) — logged as its own unit | a wrong-background result is no longer marked "conditional"; the red banner remains |
| B | a result-level `model_mismatch` flag from a chosen constant (e.g. n_eff/n < 0.02, between the stress case's 0.0075 and real data's ≥ 0.04) | a new threshold on a data-dependent quantity (n_eff/n also depends on the sampling step) — the design rule's failure; needs calibration; NOT recommended |
| C | keep the 1-count floor until a background-comparison check exists | the occupancy floor stays scale-dependent |

A is what this branch ships; if the owner prefers C the branch waits.
#     F = ((chi2_without - chi2_with) / p) / (chi2_with / dof)
# A component driven to its amplitude floor, pinned on a bound or fitted to
# numerical residue has chi2_without <= chi2_with (removing it costs nothing).
# Owner decision 2026-09-18: such a component is an explicit OUTCOME — the fit
# did not determine it — and its centre, width and sigma are not reported.
# Known limits, same as the Auto-Fit anchor: a gross single-channel artefact
# inflates chi2_with and can mark a real component unsupported; redundancy
# under overlap is NOT detected (a refit without the component is the test for
# that; step (c) does it for the Auto-Fit anchor). Threshold F >= 10 (~ p 1e-9
# at these sizes); on the 202 committed targets resolved components have
# F >= 1.1e3 and 3 of 752 components are unsupported (F 0.95-3.9).
SUPPORT_MIN_F = 10.0


def _component_support(y_sub, fitted_sub, comp_y, weights, n_free_comp, n_free_total) -> dict[str, Any]:
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
    # differential-evolution result whose refinement did not take over).
    search_box = getattr(result, "search_box", {})

    fitted_sub = result.best_fit
    fitted_y = fitted_sub + bg

    # ── Per‑peak results ──────────────────────────────────────────────────────
    individual_peaks = []
    for spec in peak_specs:
        pid = spec["id"]
        prefix = f"p{pid}_"
        peak_y = composite_model.components[
            next(i for i, c in enumerate(composite_model.components)
                 if c.prefix == prefix)
        ].eval(result.params, x=x)

        # Area by numerical integration. abs(): real XPS grids are
        # BE-descending, which makes the raw trapezoid integral negative —
        # the area is a magnitude by convention (matches autofit/engine.py).
        area = float(abs(trapezoid(peak_y, x)))

        # Parameter extraction with stderr
        param_info: dict[str, Any] = {}
        for pname in result.params:
            if pname.startswith(prefix):
                short = pname[len(prefix):]
                par = result.params[pname]
                param_info[short] = {
                    "value": float(par.value),
                    "stderr": float(par.stderr) if par.stderr is not None else None,
                    "vary": par.vary,
                    "expr": par.expr,
                    "min": float(par.min) if np.isfinite(par.min) and "min" not in search_box.get(pname, {}) else None,
                    "max": float(par.max) if np.isfinite(par.max) and "max" not in search_box.get(pname, {}) else None,
                }

        param_info["area"] = {"value": area, "stderr": None}

        # Approximate area stderr via amplitude + fwhm propagation
        amp_par = result.params.get(prefix + "amplitude")
        fwhm_par = result.params.get(prefix + "fwhm")
        if (amp_par and fwhm_par and amp_par.stderr and fwhm_par.stderr
                and amp_par.value and fwhm_par.value):
            rel_err = np.sqrt(
                (amp_par.stderr / amp_par.value) ** 2
                + (fwhm_par.stderr / fwhm_par.value) ** 2
            )
            param_info["area"]["stderr"] = abs(area) * rel_err

        n_free_comp = sum(1 for n, par in result.params.items() if n.startswith(prefix) and par.vary and par.expr is None)
        support = _component_support(y_sub, fitted_sub, peak_y, weights, n_free_comp, result.nvarys)
        # A linked component follows its parent: it is supported exactly when the
        # parent is (its own removal test would double-count the parent's role).
        individual_peaks.append({
            "id": pid,
            "y": peak_y.tolist(),
            "params": param_info,
            "support": support,
        })

    # A linked component follows its ROOT ancestor (a grandchild follows the
    # root), whatever the request order; a cycle or a missing master leaves
    # its own verdict.
    by_id = {str(ip["id"]): ip for ip in individual_peaks}
    master_of = {str(spec["id"]): spec.get("constrain_to") for spec in peak_specs}

    def root_of(pid: str) -> str:
        seen = set()
        while master_of.get(pid) is not None and str(master_of[pid]) in by_id and pid not in seen:
            seen.add(pid)
            pid = str(master_of[pid])
        return pid

    for ip in individual_peaks:
        root = root_of(str(ip["id"]))
        if root != str(ip["id"]):
            ip["support"]["follows"] = by_id[root]["id"]
            ip["support"]["supported"] = by_id[root]["support"]["supported"]

    # ── Statistics ────────────────────────────────────────────────────────────
    n_data = len(y_sub)
    n_free = result.nvarys
    chi_sq = float(result.chisqr) if result.chisqr is not None else None
    red_chi_sq = float(result.redchi) if result.redchi is not None else None

    residuals = (y_sub - fitted_sub).tolist()
                                     # the nfev cap); the detection family
                                     # carries the full structure instead

# ── Two-phase sweep: screen → stabilize (unit F3, 2026-07-07) ──────────────
# Measured motivation (PROGRESS.md diagnosis, cause a): a 29-candidate C 1s
# grammar at 25 s/candidate stability budgets + a 30-60 s proposal pass can
# never finish inside TOTAL_ANALYSIS_TIMEOUT_SEC (240 s, deliberately below
# the gunicorn --timeout 300) — the real spectra truncated at 8/29 with the
# expert-structure MG family (candidates #21-24) never evaluated.  When the
# candidate set is larger than SCREEN_TOP_K, compare_models first fits EVERY
# candidate once (primary fit only, SCREEN_MAX_NFEV effort cap), ranks the
# converged screens by BIC, and runs the full pipeline (stability, proposal
# pass, absent slots) ONLY for the top SCREEN_TOP_K — reusing each screen
# fit as that candidate's primary, so no work repeats.  Candidates screened
# out are reported honestly (analysis `screen` record: every candidate's
# screen BIC / non-convergence, nothing silent) and can never become
# survivors — the same contract as truncation, but deterministic and
# best-candidates-first instead of grammar-order-first.  Sweeps of
# ≤ SCREEN_TOP_K candidates (every existing gate/battery/stress case) take
# the classic single-phase path unchanged.  Both UNVERIFIED tunables.
SCREEN_MAX_NFEV = 6000     # measured: converging primaries on real 191-pt
                           # C 1s data use 3-5k evals; hopeless landscapes
                           # burn ≥ 18k without converging
SCREEN_TOP_K = 6
# The screen may spend at most this fraction of TOTAL_ANALYSIS_TIMEOUT_SEC —
# the deep phase must always retain budget, else a very large (joint) grammar
# could burn the whole sweep screening and deep-evaluate NOTHING.
SCREEN_BUDGET_FRACTION = 0.6


def _slot_prefix(role: str) -> str:
    """Slot role → lmfit parameter-name prefix (must match grammar._slot_param_prefix)."""
    return "s_" + re.sub(r"[^A-Za-z0-9_]", "_", role) + "_"


# ─────────────────────────────────────────────────────────────────────────────
# Background
# ─────────────────────────────────────────────────────────────────────────────

def _compute_background(
    x: np.ndarray,
    y: np.ndarray,
    bg: BackgroundType,
    endpoint_avg: int = 1,
) -> np.ndarray:
    """Background for the autofit path.

    ``endpoint_avg`` mirrors the manual /api/fit knob of the same name
    (audit F3, 2026-07-17). Every background here now takes ``n_avg``
    directly rather than requiring the caller to pre-average the array via
    _apply_endpoint_averaging — which is exactly what this function forgot
    to do, leaving Find Peaks unable to express an endpoint_avg the manual
    path honours. Default 1 (raw endpoints) matches both the previous
    behaviour of this function and app.py's own default, so wiring alone
    changes nothing.
    """
    if bg is BackgroundType.SHIRLEY:
        return shirley_background(x, y, n_avg=endpoint_avg)
    if bg is BackgroundType.SMART:
        return smart_background(x, y, n_avg=endpoint_avg)
    if bg is BackgroundType.SMART_EXP:
        from fitting import smart_experimental_background
        return smart_experimental_background(x, y, n_avg=endpoint_avg)
    if bg is BackgroundType.LINEAR:
        return linear_background(x, y)
    if bg is BackgroundType.TOUGAARD:
        from fitting import tougaard_background
        return tougaard_background(x, y, n_avg=endpoint_avg)
    raise ValueError(f"Unknown background type: {bg}")


# ─────────────────────────────────────────────────────────────────────────────
# lmfit model construction
# ─────────────────────────────────────────────────────────────────────────────

def _build_composite_model(model: CandidateModel) -> Model:
    composite: Model | None = None
    for slot in model.slots:
        shape_name = BACKEND_SHAPE[slot.line_shape]
        if shape_name not in _SHAPE_FUNCS:
            raise RuntimeError(
                f"Shape {shape_name!r} not registered in fitting._SHAPE_FUNCS"
            )
        sub = Model(_SHAPE_FUNCS[shape_name], prefix=_slot_prefix(slot.role))
        composite = sub if composite is None else composite + sub
    if composite is None:
        raise ValueError("CandidateModel has no slots")
    return composite


def _peak_estimate_in_window(
    x: np.ndarray, y_net: np.ndarray, window: tuple[float, float]
) -> float:
    mask = (x >= window[0]) & (x <= window[1])
    if mask.any():
        return max(float(np.max(y_net[mask])), 1.0)
    return max(float(np.max(y_net)) * 0.1, 1.0)


# Default (init, lo, hi) for each shape's extra parameters.  Slot-level
# fixed_params / param_ranges override these.
_SHAPE_PARAM_DEFAULTS: dict[LineShape, list[tuple[str, float, float, float]]] = {
    LineShape.GAUSSIAN: [],
    LineShape.LORENTZIAN: [],
    LineShape.PSEUDO_VOIGT: [("gl_ratio", 0.30, 0.0, 1.0)],
    LineShape.ASYM_GL: [("gl_ratio", 0.30, 0.0, 1.0), ("asymmetry", 0.10, 0.0, 1.0)],
    LineShape.DS: [("alpha", 0.10, 0.0, 0.5), ("gamma_asym", 0.0, 0.0, 1.0)],
    # DS+G: fitalg convention — slot.fwhm_range bounds m_gauss (the Gaussian
    # FWHM width knob); beta is the DS Lorentzian HWHM in eV.
    LineShape.DS_G: [("alpha", 0.10, 0.0, 0.49), ("beta", 0.30, 0.05, 2.0)],
    LineShape.LACX: [("alpha", 1.0, 0.1, 5.0), ("beta", 1.0, 0.1, 5.0),
                     ("m", 50.0, 0.0, 499.0)],
}

# Which parameter carries the slot's fwhm_range for each shape.
def _width_param(shape: LineShape) -> str:
    return "m_gauss" if shape is LineShape.DS_G else "fwhm"


def _add_shape_params(
    p: Parameters, prefix: str, slot: ComponentSlot, fwhm_init: float,
    parent_prefix: Optional[str] = None,
) -> None:
    """Width + shape-specific parameters for one slot, with bounds/overrides."""
    flo, fhi = slot.fwhm_range
    fixed = dict(slot.fixed_params)
    ranges = dict(slot.param_ranges)
    shared = set(slot.share_parent_params)
    if shared and parent_prefix is None:
        raise ValueError(
            f"slot {slot.role!r} declares share_parent_params but has no "
            "linked parent"
        )

    # Width parameter (fwhm, or m_gauss for DS+G)
    wname = _width_param(slot.line_shape)
    if slot.fwhm_excess_range is not None:
        # width-inequality linkage: width = parent width + free excess >= 0
        # (Coster-Kronig doublet broadening — grammar.ComponentSlot docs)
        if parent_prefix is None:
            raise ValueError(
                f"slot {slot.role!r} declares fwhm_excess_range but has no "
                "linked parent"
            )
        if wname in shared or wname in fixed or slot.fwhm_linked_to is not None:
            raise ValueError(
                f"slot {slot.role!r}: fwhm_excess_range is mutually exclusive "
                "with sharing/fixing/expression-linking the width"
            )
        elo, ehi = slot.fwhm_excess_range
        if not (0.0 <= elo < ehi):
            raise ValueError(
                f"slot {slot.role!r}: fwhm_excess_range must be a "
                f"non-negative interval, got {slot.fwhm_excess_range}"
            )
        p.add(f"{prefix}fwhm_excess", value=0.5 * (elo + ehi), min=elo, max=ehi)
        p.add(f"{prefix}{wname}", value=0.0,
              expr=f"{parent_prefix}{wname} + {prefix}fwhm_excess")
    elif wname in shared:
        p.add(f"{prefix}{wname}", value=0.0, expr=f"{parent_prefix}{wname}")
    elif wname in fixed:
        p.add(f"{prefix}{wname}", value=float(fixed[wname]), vary=False)
    elif slot.fwhm_linked_to is not None:
        p.add(f"{prefix}{wname}", value=float(np.clip(fwhm_init, flo, fhi)),
              expr=slot.fwhm_linked_to)
    else:
        wlo, whi = ranges.get(wname, (flo, fhi))
        p.add(f"{prefix}{wname}", value=float(np.clip(fwhm_init, wlo, whi)),
              min=wlo, max=whi)

    for name, init, lo, hi in _SHAPE_PARAM_DEFAULTS[slot.line_shape]:
        if name in shared:
            p.add(f"{prefix}{name}", value=0.0, expr=f"{parent_prefix}{name}")
            continue
        if name in fixed:
            p.add(f"{prefix}{name}", value=float(fixed[name]), vary=False)
            continue
        plo, phi = ranges.get(name, (lo, hi))
        p.add(f"{prefix}{name}", value=float(np.clip(init, plo, phi)), min=plo, max=phi)


def _full_window_bound_overrides(
    model: CandidateModel, x: Optional[np.ndarray],
) -> dict[str, tuple[float, float]]:
    """Opt-in "fit the entire window" (unit 1, 2026-07-13): per-slot center
    BOUND overrides — never the starting guess or amplitude estimate,
    both of which stay anchored to the slot's own ``be_window`` (see
    callers below). Branches on how EACH slot was solved, not on whether
    the region as a whole has curated grammar:

    - ``region == "unassigned"`` (a detection/structural-fallback slot —
      Fe 2p, an out-of-grammar preseed) has no cited per-component window
      to preserve: widens fully to the ROI on both sides.
    - Any other (curated, chemically-anchored) slot widens ONLY the outer
      envelope — the lowest-BE slot's lower bound and the highest-BE
      slot's upper bound move to the ROI edges; every interior slot (and
      the untouched side of an outer slot) keeps its literature window
      exactly, so one chemical state can never wander into a
      neighboring one's territory. A model with a single curated primary
      slot has no interior to protect, so it widens on both sides.

    Linked slots (spin-orbit partners, satellites) are never included —
    their offset from the parent is a cited physical splitting, entirely
    unrelated to ROI cropping.
    """
    if x is None or len(x) == 0:
        return {}
    roi_lo, roi_hi = float(np.min(x)), float(np.max(x))
    primary = [s for s in model.slots if s.linked_to is None]
    overrides: dict[str, tuple[float, float]] = {
        s.role: (roi_lo, roi_hi) for s in primary if s.region == "unassigned"
    }
    curated = [s for s in primary if s.region != "unassigned"]
    if curated:
        lo_role = min(curated, key=lambda s: s.be_window[0]).role
        hi_role = max(curated, key=lambda s: s.be_window[1]).role
        for s in curated:
            # min()/max() against the ORIGINAL bound (never a bare ROI edge)
            # so this can only ever widen, never narrow or invert a bound —
            # a ROI that doesn't fully contain the slot's own literature
            # window (Codex-caught: e.g. ROI 287-300 vs a slot window
            # (284, 285)) must leave that side exactly as it was, not
            # produce an inverted (min > max) or narrowed bound.
            lo = min(s.be_window[0], roi_lo) if s.role == lo_role else s.be_window[0]
            hi = max(s.be_window[1], roi_hi) if s.role == hi_role else s.be_window[1]
            overrides[s.role] = (lo, hi)
    return overrides


def _default_params_from_slots(
    model: CandidateModel,
    x: Optional[np.ndarray] = None,
    y_net: Optional[np.ndarray] = None,
    fit_full_window: bool = False,
) -> Parameters:
    """Slot midpoints as starting values, slot bounds as hard constraints.

    ``fit_full_window`` (default False — every existing caller's behavior
    is unchanged unless it opts in) relaxes the primary-slot CENTER bound
    per ``_full_window_bound_overrides``; the starting guess and the
    amplitude-estimate window always stay anchored to the slot's own
    ``be_window``, so relaxing the bound never changes where the search
    starts, only how far it may wander.
    """
    p = Parameters()

    for name, lo_b, hi_b in model.shared_fwhm_params:
        p.add(name, value=0.5 * (lo_b + hi_b), min=lo_b, max=hi_b)

    if y_net is not None and len(y_net) > 0:
        y_peak = max(float(np.max(y_net)), 1.0)
    else:
        y_peak = 1.0e5

    def _amp_bounds(window: tuple[float, float]) -> tuple[float, float]:
        if x is not None and y_net is not None:
            init = _peak_estimate_in_window(x, y_net, window)
            return init, max(2.0 * y_peak, 10.0 * init, 1.0)
        return 1000.0, 1.0e5

    bound_overrides = (_full_window_bound_overrides(model, x)
                       if fit_full_window else {})

    # Pass 1: primary (non-linked) slots
    for slot in model.slots:
        if slot.linked_to is not None:
            continue
        prefix = _slot_prefix(slot.role)
        cmid = 0.5 * (slot.be_window[0] + slot.be_window[1])
        fmid = 0.5 * (slot.fwhm_range[0] + slot.fwhm_range[1])
        amp_init, amp_max = _amp_bounds(slot.be_window)
        bound = bound_overrides.get(slot.role, slot.be_window)
        p.add(f"{prefix}center", value=cmid, min=bound[0], max=bound[1])
        p.add(f"{prefix}amplitude", value=amp_init, min=0.0, max=amp_max)
        _add_shape_params(p, prefix, slot, fmid)

    # Pass 2: linked slots (satellites, chemically-shifted contaminants,
    # spin-orbit partners) — center via offset expression; amplitude either
    # free (satellite) or ratio-linked (doublet).  Processed in dependency
    # order so a chain (main ← sat7/2 ← sat5/2) resolves: lmfit exprs may
    # not reference parameters that do not exist yet.
    done_roles = {s.role for s in model.slots if s.linked_to is None}
    pending = [s for s in model.slots if s.linked_to is not None]
    ordered: list[ComponentSlot] = []
    while pending:
        ready = [s for s in pending if s.linked_to in done_roles]
        if not ready:
            raise ValueError(
                f"unresolvable linkage chain among {[s.role for s in pending]} "
                "(missing parent or cycle)"
            )
        for s in ready:
            ordered.append(s)
            done_roles.add(s.role)
            pending.remove(s)

    for slot in ordered:
        prefix = _slot_prefix(slot.role)
        parent = model.slot_by_role(slot.linked_to)
        if parent is None:
            raise ValueError(f"Slot {slot.role!r} linked to unknown role {slot.linked_to!r}")
        parent_prefix = _slot_prefix(parent.role)
        offs_lo, offs_hi = slot.linked_offset_range or (0.0, 0.0)
        fmid = 0.5 * (slot.fwhm_range[0] + slot.fwhm_range[1])

        if offs_hi > offs_lo:
            p.add(f"{prefix}offset", value=0.5 * (offs_lo + offs_hi),
                  min=offs_lo, max=offs_hi)
            p.add(f"{prefix}center", value=0.0,
                  expr=f"{parent_prefix}center + {prefix}offset")
        else:
            # Degenerate range = fixed offset
            p.add(f"{prefix}center", value=0.0,
                  expr=f"{parent_prefix}center + {offs_lo}")

        # Shape params (incl. the width) BEFORE the amplitude: the width-
        # aware area-ratio expression below references this slot's width.
        _add_shape_params(p, prefix, slot, fmid, parent_prefix=parent_prefix)

        # ``area_ratio`` is an AREA statement (2j+1 statistical intensity).
        # With a shared width, height ratio == area ratio and the plain
        # height link is exact.  Under width-inequality linkage
        # (fwhm_excess_range) the height link must carry the width
        # correction: same-shape peaks have area ∝ amplitude × width (the
        # lineshape factor cancels only when the mixing params are shared —
        # guarded in _add_shape_params/_validate below).
        ratio_expr: Optional[str] = None
        if slot.area_ratio_range is not None:
            rlo, rhi = slot.area_ratio_range
            rinit = slot.area_ratio if slot.area_ratio is not None else 0.5 * (rlo + rhi)
            p.add(f"{prefix}ratio", value=float(np.clip(rinit, rlo, rhi)),
                  min=rlo, max=rhi)
            ratio_expr = f"{prefix}ratio"
        elif slot.area_ratio is not None:
            ratio_expr = repr(float(slot.area_ratio))

        if ratio_expr is None:
            amp_init, amp_max = _amp_bounds(slot.be_window)
            p.add(f"{prefix}amplitude", value=amp_init, min=0.0, max=amp_max)
        elif slot.fwhm_excess_range is not None:
            # Area-ratio linkage under independent widths is implemented
            # ONLY for the pseudo-Voigt with a shared mixing parameter —
            # the one case where area ∝ height × width with a cancelling
            # shape factor.  Other shapes (asym-GL asymmetry, DS α/γ,
            # DS+G's m_gauss-only width, LACX α/β/m) do NOT scale that way;
            # a shape-specific area factor is FUTURE WORK, and silently
            # emitting the height×width link there would enforce a wrong
            # area ratio (Codex adjudication-unit review, both runs).
            if parent.line_shape is not slot.line_shape:
                raise ValueError(
                    f"slot {slot.role!r}: area-ratio linkage under "
                    "fwhm_excess_range requires the parent to share the "
                    "line shape (area ∝ amplitude × width only holds "
                    "within one shape family)"
                )
            if slot.line_shape is not LineShape.PSEUDO_VOIGT:
                raise ValueError(
                    f"slot {slot.role!r}: area-ratio linkage under "
                    "fwhm_excess_range is implemented only for "
                    "PSEUDO_VOIGT (shape-specific area factors for other "
                    "shapes are future work)"
                )
            if "gl_ratio" not in slot.share_parent_params:
                raise ValueError(
                    f"slot {slot.role!r}: area-ratio linkage under "
                    "fwhm_excess_range requires gl_ratio in "
                    "share_parent_params (the pseudo-Voigt area factor "
                    "must cancel in the ratio)"
                )
            wname = _width_param(slot.line_shape)
            p.add(f"{prefix}amplitude", value=0.0,
                  expr=(f"{parent_prefix}amplitude * {ratio_expr} * "
                        f"{parent_prefix}{wname} / {prefix}{wname}"))
        else:
            p.add(f"{prefix}amplitude", value=0.0,
                  expr=f"{parent_prefix}amplitude * {ratio_expr}")

    return p


# ─────────────────────────────────────────────────────────────────────────────
            line_shape=slot.line_shape,
            support=supports.get(prefix),
        ))
    return out


# Shape-parameter names allowed to saturate at bounds per lineshape (shape
# preference, not pathology).  Width-like params are NOT excluded.
_BOUNDARY_EXCLUDED: dict[LineShape, frozenset[str]] = {
    LineShape.GAUSSIAN: frozenset(),
    LineShape.LORENTZIAN: frozenset(),
    LineShape.PSEUDO_VOIGT: frozenset({"gl_ratio"}),
    LineShape.ASYM_GL: frozenset({"gl_ratio", "asymmetry"}),
    LineShape.DS: frozenset({"alpha", "gamma_asym"}),
    LineShape.DS_G: frozenset({"alpha"}),          # beta is a WIDTH here — counted
    LineShape.LACX: frozenset({"alpha", "beta"}),  # both are exponents here
}


def _role_for_param(pname: str, role_by_prefix: dict[str, str]) -> Optional[str]:
    for prefix in sorted(role_by_prefix, key=len, reverse=True):
        if pname.startswith(prefix):
            return role_by_prefix[prefix]
    return None


def _detect_boundary_hits(params: Parameters, model: CandidateModel) -> list[str]:
    """Varying params within 1% of a finite bound → 'role:param@min|max'."""
    hits: list[str] = []
    role_by_prefix = {_slot_prefix(s.role): s.role for s in model.slots}
    shape_by_role = {s.role: s.line_shape for s in model.slots}

    for pname, par in params.items():
        if not par.vary:
            continue
        lo, hi = par.min, par.max
        if not (np.isfinite(lo) and np.isfinite(hi)) or hi <= lo:
            continue
        tol = 0.01 * (hi - lo)
        at_min = (par.value - lo) < tol
        at_max = (hi - par.value) < tol
        if not (at_min or at_max):
            continue
        role = _role_for_param(pname, role_by_prefix)
        short = pname[len(_slot_prefix(role)):] if role is not None else pname
        shape = shape_by_role.get(role)
        if shape is not None and short in _BOUNDARY_EXCLUDED.get(shape, frozenset()):
            continue
        # amplitude at min (=0) → component absent: surfaced via stability
        if short == "amplitude" and at_min:
            continue
        # relaxed doublet ratio at a bound is a real constraint violation —
        # counted (it means the data is fighting the physical ratio window).
        hits.append(f"{role or '?'}:{short}@{'min' if at_min else 'max'}")
    return hits


def _proposed_slot_pegs(outcome: FitOutcome, role: str) -> list[str]:
    """Boundary pegs for one proposed slot, using the SAME detector (and the
    same ``_BOUNDARY_EXCLUDED`` shape-endpoint policy) as every grammar slot.

    Shape endpoints (a pure-Gaussian ``gl_ratio``=0, a pure-Lorentzian
    ``gl_ratio``=1) are LEGITIMATE physics, not constraint violations — the
    grammar excludes them from boundary hits, and treating a proposal that
    reaches one as spurious would drop real pure-Gaussian/Lorentzian peaks
    (measured: the two-narrow-peak F2 case regressed to zero accepted
    proposals when shape pegs were rejected).  So the caller tolerates
    ``{role}:fwhm@max`` (the physical-width ceiling doing its job) and any
    shape endpoint, and rejects on a SUBSTANTIVE peg — ``center`` at a window
    edge, ``amplitude`` at a wall, or ``fwhm@min`` (an implausibly narrow
    spike) (Codex fwhm-cap review, run A: the accurate statement of "which
    pegs reject").
    """
    return [h for h in outcome.boundary_hits if h.startswith(f"{role}:")]


def _unphysical_width_flags(
    components: "list[FittedComponent]", model: CandidateModel
) -> list[str]:
    """Fitted components whose width reaches the ordinary physical FWHM
    ceiling (:data:`FWHM_MAX_ORDINARY_EV`) with NO known-broad justification.

    A slot is grammar-sanctioned-broad — EXEMPT, because its width is region
    physics cited in the region module, not an unphysical stretch — if and
    only if it carries an explicit ``ComponentSlot.broad_justification``
    (C 1s π→π* satellite, U 4f mains, B 1s, …; see each region module for its
    citation or honest UNVERIFIED-empirical disclosure). Any other slot —
    contamination, the aliphatic main, and the region-``unassigned`` F1
    pre-seed / F2-F3 proposal slots — that fits at/above the ordinary
    ceiling is flagged: the optimizer wanted a wider (fatter) peak than an
    ordinary component physically has, the cap held it at the limit, and the
    decomposition must be reported low-confidence (routes to the CONDITIONAL
    tier via rank_and_filter) rather than silently accepted.

    ``broad_justification`` is INDEPENDENT of ``fwhm_range``'s own magnitude
    (2026-07-20 refactor, Codex-caught in the MIXED material-class review):
    the exemption used to be inferred from ``declared_hi >
    FWHM_MAX_ORDINARY_EV`` alone, which conflated "the optimizer may search
    this wide" with "this region module vouches the width is real physics".
    Widening a bound for an unrelated reason (numerical-stability headroom,
    a wider calibration envelope, MIXED material class's relaxed
    contamination ceiling) used to silently grant the vouching exemption as
    a side effect. Region-agnostic: the exemption is driven entirely by
    each slot's own declared field, so no region's cited widths are ever
    mis-flagged, and no bound can ever again disable this safety net merely
    by being wide.
    """
    slots_by_role = {s.role: s for s in model.slots}
    flags: list[str] = []
    for c in components:
        slot = slots_by_role.get(c.slot_role)
        if slot is None:
            continue
        declared_lo, declared_hi = slot.fwhm_range
        vouched = slot.broad_justification is not None
        # EFFECTIVE width (Stage-2 PHYSICAL bar): DS+G's width lives in TWO
        # params — beta (Lorentzian HWHM, eV) and m_gauss (Gaussian FWHM;
        # what comp.fwhm carries) — so the checks below must see the
        # convolved width, not the Gaussian part alone (a component could
        # otherwise be ~3+ eV wide while every width check reads 1.0:
        # exactly the 'neighbor broadened to hide a missed peak' channel).
        # Olivero & Longbothum 1977 Voigt-FWHM approximation (0.02%).
        eff_fwhm = c.fwhm
        if c.line_shape is LineShape.DS_G:
            f_l = 2.0 * float(c.shape_params.get("beta", 0.0))
            eff_fwhm = 0.5346 * f_l + np.sqrt(0.2166 * f_l ** 2 + c.fwhm ** 2)
            if eff_fwhm >= FWHM_MAX_ORDINARY_EV and not vouched:
                flags.append(
                    f"{c.slot_role}:effective fwhm={eff_fwhm:.2f}eV≥"
                    f"{FWHM_MAX_ORDINARY_EV:.1f}eV ordinary cap (DS+G "
                    f"β={c.shape_params.get('beta', 0.0):.2f} + "
                    f"m={c.fwhm:.2f}; no known-broad justification)")
                continue
        elif c.line_shape is LineShape.ASYM_GL:
            # asym-GL broadens its high-BE side to fwhm×(1+asymmetry)
            # (fitting.py convention) — the MEAN effective width
            # fwhm×(1+asym/2) closes the remaining papering-over channel
            # (Codex Stage-2 review, run A MAJOR).
            asym = float(c.shape_params.get("asymmetry", 0.0))
            eff_fwhm = c.fwhm * (1.0 + 0.5 * asym)
            if eff_fwhm >= FWHM_MAX_ORDINARY_EV and not vouched:
                flags.append(
                    f"{c.slot_role}:effective fwhm={eff_fwhm:.2f}eV≥"
                    f"{FWHM_MAX_ORDINARY_EV:.1f}eV ordinary cap (asym-GL "
                    f"fwhm={c.fwhm:.2f}×(1+{asym:.2f}/2); no known-broad "
                    "justification)")
                continue
        # detection-family slots (scale-relative ceilings, usually > the
        # ordinary cap): a component at ≥ DETECTION_WIDTH_ABSORB_FRACTION
        # of its own ceiling (= 1.75× the DETECTED width via the 2.5×
        # ceiling) is absorbing neighboring intensity — the papering-over
        # signature in transferable units. Unaffected by broad_justification
        # (these are engine-constructed proposal/pre-seed slots, not
        # region-module-authored grammar; their ceiling is scale-relative,
        # not a physics vouch).
        if c.slot_role.startswith("detected_peak_"):
            if eff_fwhm >= DETECTION_WIDTH_ABSORB_FRACTION * declared_hi:
                flags.append(
                    f"{c.slot_role}:fwhm={eff_fwhm:.2f}eV≥"
                    f"{DETECTION_WIDTH_ABSORB_FRACTION:.2f}×ceiling "
                    f"({declared_hi:.2f}eV) — ~1.75× its detected width; "
                    "likely absorbing a neighbor")
            continue
        if vouched:
            continue                       # grammar-sanctioned-broad slot
        # pegging the ordinary ceiling — same 1%-of-range tol as boundary
        # detection, so a component held AT the 2.0 cap is caught
        tol = 0.01 * (declared_hi - declared_lo) if declared_hi > declared_lo else 0.0
        if eff_fwhm >= FWHM_MAX_ORDINARY_EV - tol:
            flags.append(
                f"{c.slot_role}:fwhm={eff_fwhm:.2f}eV≥{FWHM_MAX_ORDINARY_EV:.1f}eV "
                "ordinary cap (no known-broad justification)")
    return flags


def fit_candidate(
    x: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray,
    model: CandidateModel,
    initial_params: Optional[Parameters] = None,
    max_nfev: int = FIT_CANDIDATE_MAX_NFEV,
    fit_full_window: bool = False,
    endpoint_avg: int = 1,
) -> FitOutcome:
    """One fit of ``model`` to (x, y, weights); background subtracted first.

    ``max_nfev`` bounds leastsq's own effort per call. lmfit's default
    (200000*(nvars+1), see lmfit.Minimizer) is effectively unbounded: a
    candidate whose params wander to a valid-but-degenerate corner (e.g.
    DS+G's alpha/beta pinned at their bounds — a shape preference, not a
    param error; see _BOUNDARY_EXCLUDED) produces a landscape leastsq can't
    descend, and it spins for tens of thousands of evaluations without
    terminating. Diagnostic run (2026-07-05, Suggest-peaks hang
    investigation) showed a clean bimodal split: converged fits topped out
    at nfev=14890; non-convergent ones started at nfev=21604. This cap sits
    between the two so lmfit's own AbortFitException (caught internally by
    leastsq(), surfacing as result.success=False) cuts off the latter
    deterministically, without clipping legitimate slow-but-converging fits.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    weights = np.asarray(weights, dtype=float)

    bg = _compute_background(x, y, model.background, endpoint_avg=endpoint_avg)
    y_sub = y - bg
    composite = _build_composite_model(model)
    params = initial_params if initial_params is not None else \
        _default_params_from_slots(model, x=x, y_net=y_sub,
                                   fit_full_window=fit_full_window)

    try:
        result = composite.fit(y_sub, params, x=x, weights=weights,
                               method="leastsq", nan_policy="omit",
                               max_nfev=max_nfev)
        if (not result.success and result.chisqr is not None
                and np.isfinite(result.chisqr)):
            # ONE warm restart (Stage-2, measured on the real diagnosis
            # scans): a model whose optimum sits against parameter bounds
            # stalls MINPACK on a flat transformed gradient — it reaches
            # the minimum, then burns the whole nfev budget without
            # satisfying ftol (success=False at a genuinely converged
            # χ²).  Restarting AT the exit point resets leastsq's internal
            # diag scaling and it certifies in tens of evaluations
            # (measured: 6000 nfev burned cold → 33 nfev warm, identical
            # χ²).  Fires ONLY on a failed-but-finite fit, so converging
            # fits are byte-identical; cost is bounded by one
            # WARM_RESTART_MAX_NFEV fit.
            retry = composite.fit(y_sub, result.params.copy(), x=x,
                                  weights=weights, method="leastsq",
                                  nan_policy="omit",
                                  max_nfev=WARM_RESTART_MAX_NFEV)
            if retry.success:
                result = retry
    except Exception as exc:
        log.debug("fit_candidate failed for %s: %s", model.name, exc)
        return FitOutcome(
            converged=False, components=[], residual_sum_sq=float("inf"),
            weighted_chi_sq=float("inf"),
            n_params=len([q for q in params.values() if q.vary]),
            n_data=len(y_sub), lmfit_result=None, background=bg,
        )

    unweighted_r = y_sub - result.best_fit
    return FitOutcome(
        converged=bool(result.success),
        components=_extract_fitted_components(result, model),
        residual_sum_sq=float(np.sum(unweighted_r ** 2)),
        weighted_chi_sq=float(result.chisqr) if result.chisqr is not None else float("inf"),
        n_params=result.nvarys,
        n_data=len(y_sub),
        lmfit_result=result,
        background=bg,
        boundary_hits=_detect_boundary_hits(result.params, model),
    )


def compute_slot_areas(
    model: CandidateModel, primary: FitOutcome, x: np.ndarray
) -> dict[str, float]:
    if primary.lmfit_result is None:
        return {}
    composite = primary.lmfit_result.model
    params = primary.lmfit_result.params
    out: dict[str, float] = {}
    for slot in model.slots:
        prefix = _slot_prefix(slot.role)
        sub = next((c for c in composite.components if c.prefix == prefix), None)
        if sub is None:
            continue
        out[slot.role] = float(abs(trapezoid(sub.eval(params, x=x), x)))
    return out


def perturb_initial_params(
    model: CandidateModel,

codex
The new helper uses the fit’s own background-subtracted data, weights, and parameter counts, and calls the server’s support function directly. I’m checking prefix matching and linked amplitudes next, along with whether the stress-test warning remains visible through the API and page.

exec
/bin/zsh -lc "ls -d venv /Users/skyefortier/xps-app/venv; rg -n 'role=|role =|linked_to=' autofit/regions/c1s.py autofit/regions/u4f.py; sed -n '1250,1395p' autofit/engine.py; sed -n '1,210p' autofit/methods/ic_model_comparison.py; rg -n 'detectability|above_floor|filtered_dominant_alternative|conditional|absent_slots' templates/index.html autofit/engine.py autofit/methods/*.py; sed -n '1,180p' tests/autofit/test_stress_honesty.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
/Users/skyefortier/xps-app/venv
ls: venv: No such file or directory
autofit/regions/u4f.py:198:                role=role, region=REGION, phase_id=pid,
autofit/regions/u4f.py:226:            linked_to="main_u4f72",
autofit/regions/u4f.py:237:            linked_to="main_u4f72",
autofit/regions/u4f.py:244:            linked_to="satellite_u4f72",
autofit/regions/u4f.py:255:            linked_to="satellite_u4f72",
autofit/regions/u4f.py:268:            linked_to="main_u4f72",
autofit/regions/u4f.py:275:            linked_to="main_u4f52",
autofit/regions/c1s.py:310:                role=role, region=REGION, phase_id=pid,
autofit/regions/c1s.py:336:            linked_to="main_graphitic", linked_offset_range=SATELLITE_OFFSET_RANGE,
autofit/regions/c1s.py:426:                        linked_to="main_graphitic",
    timed_out: bool = False

    @property
    def min_persistence(self) -> float:
        if not self.per_slot:
            return 0.0
        return min(s.persistence for s in self.per_slot.values())


def run_stability_analysis(
    x: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray,
    model: CandidateModel,
    primary_fit: FitOutcome,
    noise_floor: float,
    n_refits: int = 20,
    rng_seed: int = 0,
    fixed_param_values: Optional[dict[str, float]] = None,
    deadline: Optional[float] = None,
    fit_full_window: bool = False,
    endpoint_avg: int = 1,
) -> ModelStability:
    """
    ``deadline`` is an absolute ``time.perf_counter()`` timestamp (set by
    the caller from CANDIDATE_TIMEOUT_SEC) shared across this candidate's
    primary fit + all its refits. Once passed, remaining refits are
    skipped — not run and not counted as failures — so one candidate stuck
    in a slow-but-nfev-capped region can't consume the rest of the request.
    """
    rng = np.random.default_rng(rng_seed)
    pos: dict[str, list[float]] = {s.role: [] for s in model.slots}
    fw: dict[str, list[float]] = {s.role: [] for s in model.slots}
    am: dict[str, list[float]] = {s.role: [] for s in model.slots}
    occupied: dict[str, int] = {s.role: 0 for s in model.slots}
    n_converged = 0
    n_with_orphans = 0
    # Same widened bounds every refit was actually built with (constant
    # across this candidate's whole stability pass) — identity-matching
    # must agree with the bound the fit was allowed to search, or a
    # component correctly placed outside its ORIGINAL window becomes an
    # orphan here, tanking persistence for the very slot this option
    # exists to rescue (Codex-caught, see _effective_be_window).
    bound_overrides = _full_window_bound_overrides(model, x) if fit_full_window else None

    # Data-informed perturbation seeds (see perturb_initial_params): reuse
    # the primary fit's background rather than recomputing per refit.
    bg = primary_fit.background
    y_net = y - bg if bg is not None else None

    best_outcome: Optional[FitOutcome] = None
    refit_chis: list[float] = [float(primary_fit.weighted_chi_sq)]
    n_attempted = 0
    timed_out = False
    for _ in range(n_refits):
        if deadline is not None and time.perf_counter() >= deadline:
            timed_out = True
            log.warning(
                "run_stability_analysis: candidate %s hit its %.0fs budget "
                "after %d/%d refits — remaining refits skipped",
                model.name, CANDIDATE_TIMEOUT_SEC, n_attempted, n_refits,
            )
            break
        n_attempted += 1
        seed = int(rng.integers(0, 2**31 - 1))
        init = perturb_initial_params(model, seed=seed, x=x, y_net=y_net,
                                      fit_full_window=fit_full_window)
        if fixed_param_values:
            # bound-fixed refit stability: the constrained parameters stay
            # fixed at their bounds in every multi-start refit
            for pname, val in fixed_param_values.items():
                if pname in init:
                    init[pname].set(value=float(val), vary=False)
        outcome = fit_candidate(x, y, weights, model, initial_params=init,
                                endpoint_avg=endpoint_avg)
        if not outcome.converged:
            continue
        n_converged += 1
        refit_chis.append(float(outcome.weighted_chi_sq))
        if best_outcome is None or outcome.weighted_chi_sq < best_outcome.weighted_chi_sq:
            best_outcome = outcome
        slot_map = match_components_to_slots(outcome.components, model, noise_floor,
                                            bound_overrides=bound_overrides)
        if slot_map.pop("__orphans__", []):
            n_with_orphans += 1
        slot_map.pop("__unsupported__", None)   # reporting only: those slots are empty
        for role, comp in slot_map.items():
            if comp is None:
                continue
            occupied[role] += 1
            pos[role].append(comp.position)
            fw[role].append(comp.fwhm)
            am[role].append(comp.amplitude)

    def _med(v):  # median or None
        return float(np.median(v)) if v else None

    def _mad(v):
        if not v:
            return None
        arr = np.asarray(v)
        return float(np.median(np.abs(arr - np.median(arr))))

    per_slot = {
        role: SlotStability(
            role=role,
            persistence=occupied[role] / max(n_attempted, 1),
            position_median=_med(pos[role]), position_mad=_mad(pos[role]),
            fwhm_median=_med(fw[role]), fwhm_mad=_mad(fw[role]),
            amplitude_median=_med(am[role]), amplitude_mad=_mad(am[role]),
        )
        for role in occupied
    }
    best_chi = min(refit_chis)
    basin_support = sum(1 for c in refit_chis
                        if c <= best_chi * (1.0 + BASIN_SUPPORT_RTOL))
    return ModelStability(
        per_slot=per_slot,
        orphan_rate=n_with_orphans / max(n_attempted, 1),
        convergence_rate=n_converged / max(n_attempted, 1),
        best_outcome=best_outcome,
        best_basin_support=basin_support,
        n_attempted=n_attempted,
        timed_out=timed_out,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Absent slots
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AbsentSlotReport:
    role: str
    persistence: float
    fitted_area: float
    main_area: float
    area_fraction: float
    threshold: float
    removed_n_params: int


def _count_slot_free_params(slot: ComponentSlot, primary: FitOutcome) -> int:
    if primary.lmfit_result is None:
        return 0
    prefix = _slot_prefix(slot.role)
"""
Method 2 — grammar + information-criterion model comparison (fitalg engine).

Runs the full comparison pipeline over a resolved grammar and returns the
top survivor's decomposition, per-slot confidence vectors, and the complete
candidate/criteria record for the ``analysis`` namespace.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

import numpy as np

from ..confidence import build_confidence_vector
from ..criteria import build_criteria_panel
from ..engine import ComparisonResult, ModelReport, compare_models, _slot_prefix
from ..grammar import BACKEND_SHAPE, CandidateGrammar
from .base import MethodResult, PeakFitMethod, poisson_like_weights, pop_endpoint_avg

_ALLOWED_OPTIONS = {
    "noise_floor", "n_refits", "rng_seed", "candidate_filter",
    "enable_proposal_pass", "persistence_threshold", "bic_ambiguity_threshold",
    "absent_slot_area_fraction", "absent_slot_persistence_threshold",
    "enable_preseed", "fit_full_window", "endpoint_avg",
}

ENGINE_VERSION = "autofit-stage2"


class ICModelComparisonMethod(PeakFitMethod):
    id = "ic_model_comparison"
    label = "Auto — model comparison (IC)"
    requires_grammar = True

    def run(
        self,
        x: np.ndarray,
        y: np.ndarray,
        weights: Optional[np.ndarray] = None,
        grammar: Optional[CandidateGrammar] = None,
        peak_specs: Optional[list[dict]] = None,
        options: Optional[dict[str, Any]] = None,
        progress_cb: Optional[Callable[[dict], None]] = None,
    ) -> MethodResult:
        if grammar is None:
            raise ValueError("ic_model_comparison requires a resolved grammar")
        opts = dict(options or {})
        unknown = set(opts) - _ALLOWED_OPTIONS
        if unknown:
            raise ValueError(f"unknown ic_model_comparison options: {sorted(unknown)}")

        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        w = np.asarray(weights, dtype=float) if weights is not None \
            else poisson_like_weights(y)
        noise_floor = float(opts.pop("noise_floor", 1.0))

        result = compare_models(
            x, y, w, grammar,
            noise_floor=noise_floor,
            n_refits=int(opts.pop("n_refits", 20)),
            rng_seed=int(opts.pop("rng_seed", 0)),
            candidate_filter=opts.pop("candidate_filter", None),
            enable_proposal_pass=bool(opts.pop("enable_proposal_pass", True)),
            enable_preseed=bool(opts.pop("enable_preseed", True)),
            persistence_threshold=float(opts.pop("persistence_threshold", 0.7)),
            bic_ambiguity_threshold=float(opts.pop("bic_ambiguity_threshold", 2.0)),
            absent_slot_area_fraction=float(opts.pop("absent_slot_area_fraction", 0.02)),
            absent_slot_persistence_threshold=float(
                opts.pop("absent_slot_persistence_threshold", 0.7)),
            progress_cb=progress_cb,
            fit_full_window=bool(opts.pop("fit_full_window", False)),
            endpoint_avg=pop_endpoint_avg(opts),
        )

        analysis = build_analysis_record(grammar, result)
        truncation_note = (
            f"analysis truncated — {result.n_candidates_evaluated} of "
            f"{result.n_candidates_total} candidates evaluated before the "
            "overall time budget was reached"
            if result.analysis_truncated else None
        )
        if not result.survivors:
            return MethodResult(
                method_id=self.id, success=False, peaks=[], analysis=analysis,
                confidence={}, diagnostics={
                    "n_reports": len(result.reports),
                    "analysis_truncated": result.analysis_truncated,
                    "n_candidates_evaluated": result.n_candidates_evaluated,
                    "n_candidates_total": result.n_candidates_total,
                },
                message=("no candidate survived filter-then-rank — see analysis "
                         "for filtered/non-converged detail (diagnostic, not "
                         "prescriptive: manual attention required)"
                         + (f"; {truncation_note}" if truncation_note else "")),
            )

        top = result.survivors[0]
        # Slots classified "correctly absent" won the BIC*-adjustment benefit
        # precisely because they carry no real signal — emitting them as
        # fitted peaks would contradict that classification (Codex finding
        # #4).  They remain visible in analysis.candidates[].absent_slots.
        absent_roles = {a.role for a in top.absent_slots}
        peaks = _peaks_from_report(top, exclude_roles=absent_roles)
        confidence = {
            slot.role: build_confidence_vector(top, slot.role, noise_floor)
            for slot in top.model.slots
            if slot.role not in absent_roles
        }
        message = ""
        winner_unassigned_roles = sorted(
            slot.role for slot in top.model.slots
            if slot.region == "unassigned"
            and slot.role not in absent_roles
        )
        if winner_unassigned_roles:
            centers = [
                f"{c.position:.2f}" for r in winner_unassigned_roles
                for c in top.primary_fit.components if c.slot_role == r
            ]
            message += (
                f"DATA-DRIVEN component(s) at {', '.join(centers)} eV "
                "(detected/seeded/proposed, region-unassigned): chemical "
                "assignment requires human review; positions are "
                "data-driven, not literature-anchored. "
            )
        if result.conditional:
            # the conditional banner leads, but must not CLOBBER the
            # data-driven/human-review note (Stage-2: a conditional
            # detection-family winner still needs its assignment caveat)
            if result.conditional_reason == "decisive_override":
                message = (
                    "CONDITIONAL result (decisive_override): clean candidates "
                    "exist but a bound-fixed refit of a constraint-limited "
                    f"candidate dominates them — winner {top.model.name} with "
                    f"parameters fixed at bounds: {top.boundary_fixed_params}; "
                    "clean alternatives retained in the ranking "
                    "(see analysis.candidates). "
                ) + message
            elif result.conditional_reason == "unstable_last_resort":
                message = (
                    "UNSTABLE result (last resort): NO candidate passed any "
                    "selection tier — component identities are NOT stable "
                    "across refits (min persistence "
                    f"{top.active_min_persistence:.2f}, orphan rate "
                    f"{top.stability.orphan_rate:.2f}).  Showing the best "
                    f"CONVERGED model ({top.model.name}, χ²ᵣ "
                    f"{top.reduced_chi_sq:.1f}) so you can see what the data "
                    "supports — treat EVERY component as a low-confidence "
                    "suggestion; the data may not distinguish one broad "
                    "feature from several overlapping ones here. "
                ) + message
            else:
                message = (
                    "CONDITIONAL result (no_clean_survivor): no candidate "
                    "passed plausibility cleanly; ranking the stable-but-"
                    f"boundary-limited tier — winner {top.model.name} has "
                    f"constraint violations {top.plausibility.boundary_hits} "
                    "(see analysis.candidates). "
                ) + message
        if top.plausibility.unphysical_widths:
            message += (
                " LOW CONFIDENCE — width(s) held at the ordinary physical "
                f"FWHM cap ({', '.join(top.plausibility.unphysical_widths)}): "
                "the data wants a broader component than an ordinary core line "
                "physically has, but no known-broad class (satellite / plasmon "
                "/ loss) is assigned here. The width is capped at the physical "
                "limit rather than silently widened; a human should identify "
                "the feature (or justify a wider width) before trusting it."
            )
        return MethodResult(
            method_id=self.id, success=True, peaks=peaks, analysis=analysis,
            confidence=confidence,
            diagnostics={
                "winner": top.model.name,
                "conditional": bool(result.conditional),
                "conditional_reason": result.conditional_reason,
                "winner_boundary_hits": list(top.plausibility.boundary_hits),
                "winner_unphysical_widths": list(top.plausibility.unphysical_widths),
                "winner_boundary_fixed_params": list(top.boundary_fixed_params),
                # stress-suite finding 0: buried decisive evidence is a
                # RESULT-level flag, not candidate-table archaeology
                "filtered_dominant_alternative":
                    result.filtered_dominant_alternative,
                "weighted_ic_disagreement": result.weighted_ic_disagreement,
                "preseeded_features": result.preseeded_features,
                "n_survivors": len(result.survivors),
                "n_filtered": len(result.filtered_out),
                "n_non_converged": len(result.non_converged),
                "analysis_truncated": result.analysis_truncated,
                "n_candidates_evaluated": result.n_candidates_evaluated,
                "n_candidates_total": result.n_candidates_total,
            },
            message=(message + (
                f" WARNING: filtered candidate "
                f"{result.filtered_dominant_alternative['name']} beats this "
                f"winner by ΔBIC* "
                f"{result.filtered_dominant_alternative['delta_bic_vs_winner']:.1f} "
                "but did not survive filtering "
                f"({result.filtered_dominant_alternative['filter_reason']})"
                if result.filtered_dominant_alternative else "")
                + (f" {truncation_note}." if truncation_note else "")),
        )


def _peaks_from_report(
    report: ModelReport, exclude_roles: frozenset | set = frozenset()
) -> list[dict]:
    """Winning decomposition as backend-spec-shaped dicts."""
autofit/methods/sparse_map.py:339:            "uses_conditional_or_unverified_constants": non_verified,
autofit/methods/multivariate_mcr.py:56:                               # blocker: unconditional +1 overcounts
autofit/methods/bayesian_exchange_mc.py:464:            "uses_conditional_or_unverified_constants": non_verified,
autofit/methods/ic_model_comparison.py:103:        # #4).  They remain visible in analysis.candidates[].absent_slots.
autofit/methods/ic_model_comparison.py:104:        absent_roles = {a.role for a in top.absent_slots}
autofit/methods/ic_model_comparison.py:128:        if result.conditional:
autofit/methods/ic_model_comparison.py:129:            # the conditional banner leads, but must not CLOBBER the
autofit/methods/ic_model_comparison.py:130:            # data-driven/human-review note (Stage-2: a conditional
autofit/methods/ic_model_comparison.py:132:            if result.conditional_reason == "decisive_override":
autofit/methods/ic_model_comparison.py:141:            elif result.conditional_reason == "unstable_last_resort":
autofit/methods/ic_model_comparison.py:177:                "conditional": bool(result.conditional),
autofit/methods/ic_model_comparison.py:178:                "conditional_reason": result.conditional_reason,
autofit/methods/ic_model_comparison.py:184:                "filtered_dominant_alternative":
autofit/methods/ic_model_comparison.py:185:                    result.filtered_dominant_alternative,
autofit/methods/ic_model_comparison.py:197:                f"{result.filtered_dominant_alternative['name']} beats this "
autofit/methods/ic_model_comparison.py:199:                f"{result.filtered_dominant_alternative['delta_bic_vs_winner']:.1f} "
autofit/methods/ic_model_comparison.py:201:                f"({result.filtered_dominant_alternative['filter_reason']})"
autofit/methods/ic_model_comparison.py:202:                if result.filtered_dominant_alternative else "")
autofit/methods/ic_model_comparison.py:273:            "absent_slots": [
autofit/methods/ic_model_comparison.py:275:                 "area_fraction": float(a.area_fraction)} for a in r.absent_slots
autofit/methods/ic_model_comparison.py:313:        "conditional_tier": bool(result.conditional),
autofit/methods/ic_model_comparison.py:314:        "conditional_reason": result.conditional_reason,
autofit/methods/ic_model_comparison.py:323:        "uses_conditional_or_unverified_constants": non_verified,
autofit/methods/ic_model_comparison.py:341:        "filtered_dominant_alternative": result.filtered_dominant_alternative,
autofit/engine.py:85:# candidate; the result carries conditional_reason='decisive_override'.
autofit/engine.py:115:# conditional/low-confidence), per the fit-quality rail "a defensible fit
autofit/engine.py:646:    # gate, detectability) read this instead of an absolute amplitude floor
autofit/engine.py:1428:def _identify_absent_slots(
autofit/engine.py:1595:    absent_slots: list[AbsentSlotReport] = field(default_factory=list)
autofit/engine.py:1611:        removed = sum(a.removed_n_params for a in self.absent_slots)
autofit/engine.py:1668:        absent_roles = {a.role for a in self.absent_slots}
autofit/engine.py:1701:    conditional: bool = False
autofit/engine.py:1702:    conditional_reason: Optional[str] = None
autofit/engine.py:1711:    filtered_dominant_alternative: Optional[dict] = None
autofit/engine.py:1747:    allow_conditional: bool = True,
autofit/engine.py:1757:    ``result.conditional = True`` and every violation preserved.  Stability
autofit/engine.py:1763:    conditional_pool: list[ModelReport] = []
autofit/engine.py:1775:                conditional_pool.append(r)
autofit/engine.py:1778:            absent_roles = [a.role for a in r.absent_slots]
autofit/engine.py:1785:    conditional = False
autofit/engine.py:1786:    conditional_reason = None
autofit/engine.py:1787:    if allow_conditional and conditional_pool and not survivors:
autofit/engine.py:1788:        survivors = conditional_pool
autofit/engine.py:1789:        conditional = True
autofit/engine.py:1790:        conditional_reason = "no_clean_survivor"
autofit/engine.py:1791:    elif allow_conditional and allow_last_resort and not survivors and reports:
autofit/engine.py:1803:        # conditional are BOTH empty — stability failures are still never
autofit/engine.py:1812:            conditional = True
autofit/engine.py:1813:            conditional_reason = "unstable_last_resort"
autofit/engine.py:1815:    # bound-fixed refit of a conditional candidate dominates) lives in
autofit/engine.py:1839:        conditional=conditional, conditional_reason=conditional_reason,
autofit/engine.py:2414:    absent = _identify_absent_slots(
autofit/engine.py:2427:        absent_slots=absent, augmented_from=base_model.name,
autofit/engine.py:2480:# Bound the number of conditional candidates the override may refit — a
autofit/engine.py:2569:        absent_slots=[],                      # conservative full-k BIC*
autofit/engine.py:2593:    if result.conditional or not result.survivors:
autofit/engine.py:2623:        result.conditional = True
autofit/engine.py:2624:        result.conditional_reason = "decisive_override"
autofit/engine.py:2942:        absent = _identify_absent_slots(
autofit/engine.py:2955:            absent_slots=absent,
autofit/engine.py:3126:            result.filtered_dominant_alternative = {
templates/index.html:7183:// The verdict is a property of THE FIT THAT PRODUCED IT, conditional on the
templates/index.html:7194:const _UNSUPPORTED_TIP = 'With the other components held at their fitted values, removing this component does not make the fit to the data significantly worse (F < 10), so this fit did not determine it: its centre, width and uncertainties are not reported. This is an outcome of the fit, not a bug, and it is conditional on the other components. The data may still contain the species: try a different starting position or width, or lock the centre where chemistry says it belongs, and refit. Known limit: a gross single-channel artefact in the region can produce this verdict for a real component.';
templates/index.html:8370:    // key does not make it this one's): clear it unconditionally
templates/index.html:9495:// tabs, _isBgSubViewActive() returns false unconditionally (state.rawBE
templates/index.html:15576:// plain words — a CONDITIONAL result still reads as conditional here.
templates/index.html:15615:  if (d.conditional) {
templates/index.html:15616:    if (d.conditional_reason === 'decisive_override') {
templates/index.html:15623:    } else if (d.conditional_reason === 'unstable_last_resort') {
templates/index.html:15643:  if (d.filtered_dominant_alternative) {
templates/index.html:15644:    const fda = d.filtered_dominant_alternative;
templates/index.html:16300:  if (d.conditional) {
templates/index.html:16316:  if (d.filtered_dominant_alternative) {
templates/index.html:16317:    const f = d.filtered_dominant_alternative;
templates/index.html:16331:  const nonv = (a.uses_conditional_or_unverified_constants || []).length;
templates/index.html:16490:  if (active) active.ui.endpointAvg = usedEp;   // unconditional: the record must match the fit even if the field was hand-edited
"""
Always-on stress-honesty net — the KEY-CRITERION invariants from the
synthetic hard-case suite (run-brief item 2), pinned on the fast subset
(IC n_refits=4 + LS + sparse; the full battery incl. Bayesian and noise
replicates is scripts/run_stress_battery.py → stress_battery_runs.jsonl,
summarized in docs/autofit/stress-test-report.md).

Where there IS a right answer the engine must recover it; where the truth
is outside the model space the mismatch must be machine-visible; an
over-specified menu must be pruned, not populated.  Values pinned from the
2026-07-04 measurement run.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from stress_cases import (  # noqa: E402
    asym_truth_case,
    bg_matched_control_case,
    bg_mismatch_case,
    isolated_missing_peak_case,
    overlap_case,
    overspecified_case,
    overspecified_decoy_case,
)
from autofit.methods import get_method  # noqa: E402

IC_OPTS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
           "enable_proposal_pass": True}


def _ic(case):
    return get_method("ic_model_comparison").run(
        case.x, case.y, grammar=case.grammar, options=dict(IC_OPTS))


@pytest.fixture(scope="module")
def sep1():
    case = overlap_case(1.0, 9000.0, seed=11, expectation="recover")
    return case, _ic(case)


def test_resolved_doublet_recovered_clean(sep1):
    """Separation 1×FWHM at 9000 counts: distinguishable → must recover."""
    case, res = sep1
    assert res.success
    assert res.diagnostics["winner"] == "P2"
    assert res.diagnostics["conditional"] is False
    by_role = {p["role"]: p for p in res.peaks}
    for t, role in zip(case.truth, ("main_a", "main_b")):
        assert by_role[role]["center"] == pytest.approx(t["center"], abs=0.05)


def test_resolved_doublet_ls_baseline(sep1):
    case, _ = sep1
    res = get_method("least_squares").run(
        case.x, case.y, peak_specs=case.ls_specs,
        options={"background_method": "linear"})
    assert res.success
    for t, p in zip(case.truth, res.peaks):
        assert p["center"] == pytest.approx(t["center"], abs=0.05)
        assert p["fwhm"] == pytest.approx(t["fwhm"], abs=0.1)


def test_resolved_doublet_sparse_count_only():
    """Sparse COUNT-ONLY pin — explicitly NOT a recovery claim: on this
    PV-truth case the selected atoms sit 0.45-0.75 eV off (Gaussian-atom /
    30%-Lorentzian mismatch, its documented weakness; classified
    count_ok_param_biased in the battery, never PASS).  The invariant
    worth pinning is only that the component COUNT does not hallucinate on
    a clean, well-separated doublet."""
    case = overlap_case(1.0, 9000.0, seed=11, expectation="recover")
    res = get_method("sparse_map").run(case.x, case.y, grammar=case.grammar)
    assert res.success
    assert len(res.peaks) == 2


def test_overspecified_menu_prunes_not_invents():
    """Truth 2 peaks, menu offers up to 5: the winner must carry exactly
    the true structure — no invented components."""
    case = overspecified_case(seed=31)
    res = _ic(case)
    assert res.diagnostics["winner"] == "P2"
    assert len(res.peaks) == 2
    by_role = {p["role"]: p for p in res.peaks}
    matched = 0
    for t in case.truth:
        if any(abs(p["center"] - t["center"]) < 0.3 for p in by_role.values()):
            matched += 1
    assert matched == 2


def test_inroi_decoy_pruned_not_populated():
    """The harder over-specification test (Codex stress review): a decoy
    'shoulder' window BETWEEN the true peaks, where real tail intensity
    lives — the winner must carry the true 2-component structure with the
    decoy hypothesis rejected, not a populated 3-component invention.
    Measured 2026-07-04: P2 clean, χ²ᵣ 1.10, exact recovery ON THIS BASE
    DRAW.  The battery shows the prune is noise-draw-DEPENDENT (offset
    2000 promotes the bound-fixed decoy via decisive_override, k=3,
    conditional-flagged) — stress report finding 8; this pin covers the
    base draw only."""
    case = overspecified_decoy_case(seed=32)
    res = _ic(case)
    assert res.diagnostics["winner"] == "P2"
    assert len(res.peaks) == 2
    by_role = {p["role"]: p for p in res.peaks}
    for t, role in zip(case.truth, ("main_a", "main_b")):
        assert by_role[role]["center"] == pytest.approx(t["center"], abs=0.1)


def test_bg_matched_control_recovers():
    case = bg_matched_control_case(seed=62)
    res = _ic(case)
    assert res.diagnostics["winner"] == "P2"
    assert res.diagnostics["conditional"] is False
    wc = next(c for c in res.analysis["candidates"] if c["name"] == "P2")
    assert wc["reduced_chi_sq"] < 2.0


def test_bg_mismatch_surfaces_loudly():
    """Shirley-shaped truth fit with a straight line: the mismatch must be
    machine-visible, never a silent clean result.

    Re-stated in the noise-floor unit (2026-09-27; plan
    docs/superpowers/plans/2026-09-27-occupancy-f-test.md §3, option A —
    OWNER DECISION PENDING). Occupancy is now the server's support F test, so
    the third component that only compensated for the wrong background is
    "not supported" and the engine returns the TRUE two-peak model — which the
    old conditional flag depended on NOT happening (the flag rode on that
    compensating component, the README's follow-up 2). What stays visible,
    without any new threshold: the winner is the true model, its χ²ᵣ is
    grossly elevated, and the set-aside better-scoring model is flagged
    (filtered_dominant_alternative — the page's red banner)."""
    case = bg_mismatch_case(seed=61)
    res = _ic(case)
    assert res.diagnostics["winner"] in case.true_candidates
    wc = next(c for c in res.analysis["candidates"]
              if c["name"] == res.diagnostics["winner"])
    assert wc["reduced_chi_sq"] > 10.0
    assert res.diagnostics["filtered_dominant_alternative"] is not None


def test_preseed_catches_isolated_missing_peak():
    """Unit F1 (2026-07-07): the isolated unmodeled peak (28% of the main —
    above the preseed dominance gate) is now caught by the PRE-FIT seeding
    channel: same honesty contract as the proposal pass (region-unassigned
    component, human adjudication), reached before the fit so the landscape
    is sane.  The peak must be seeded, fitted at the true position, and
    surfaced in analysis.preseeded_features."""
    case = isolated_missing_peak_case(seed=71)
    res = _ic(case)
    assert res.diagnostics["winner"].endswith("+preseed")
    feats = res.analysis["preseeded_features"]
    assert len(feats) == 1
    assert feats[0]["center_be"] == pytest.approx(201.5, abs=0.3)
    seeded = [p for p in res.peaks if p["role"].startswith("preseed_dominant")]
    assert len(seeded) == 1
    assert seeded[0]["center"] == pytest.approx(201.5, abs=0.3)
    assert seeded[0]["region"] == "unassigned"
    assert "human review" in res.message


def test_proposal_pass_fires_on_isolated_missing_peak():
    """The residual-guided proposal pass's designed regime (3d): with the
    preseed channel disabled, a discrete isolated real peak the menu
    doesn't model must still be proposed, accepted, and fitted at the true
    position (measured on every noise draw; 0 false positives across the
    battery's 66 covered rows)."""
    case = isolated_missing_peak_case(seed=71)
    res = get_method("ic_model_comparison").run(
        case.x, case.y, grammar=case.grammar,
        options={**IC_OPTS, "enable_preseed": False})
    assert res.diagnostics["winner"].endswith("+prop")
    accepted = [p for c in res.analysis["candidates"]
                for p in c.get("proposed_peaks", []) if p["accepted"]]

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -m pytest -p no:cacheprovider --capture=sys tests/autofit/test_occupancy_support.py tests/autofit/test_stress_honesty.py -q' in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 exited 2 in 1789ms:

==================================== ERRORS ====================================
___________ ERROR collecting tests/autofit/test_occupancy_support.py ___________
tests/autofit/test_occupancy_support.py:25: in <module>
    import fitting
fitting.py:35: in <module>
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
E   FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test']
____________ ERROR collecting tests/autofit/test_stress_honesty.py _____________
tests/autofit/test_stress_honesty.py:21: in <module>
    from stress_cases import (  # noqa: E402
tests/autofit/stress_cases.py:58: in <module>
    from fitting import _SHAPE_FUNCS
fitting.py:35: in <module>
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
E   FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test']
=========================== short test summary info ============================
ERROR tests/autofit/test_occupancy_support.py - FileNotFoundError: [Errno 2] ...
ERROR tests/autofit/test_stress_honesty.py - FileNotFoundError: [Errno 2] No ...
!!!!!!!!!!!!!!!!!!! Interrupted: 2 errors during collection !!!!!!!!!!!!!!!!!!!!
2 errors in 1.48s

exec
/bin/zsh -lc "sed -n '1390,1475p' autofit/engine.py; sed -n '1560,1685p' autofit/engine.py; sed -n '208,254p' autofit/methods/ic_model_comparison.py; sed -n '2260,2360p' autofit/engine.py; rg -n 'FittedComponent\\(|match_components_to_slots\\(|contains\\(' --glob '*.py'; sed -n '16290,16340p' templates/index.html; sed -n '15595,15665p' templates/index.html; sed -n '300,445p' autofit/regions/c1s.py; sed -n '180,285p' autofit/regions/u4f.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:


def _count_slot_free_params(slot: ComponentSlot, primary: FitOutcome) -> int:
    if primary.lmfit_result is None:
        return 0
    prefix = _slot_prefix(slot.role)
    return sum(1 for pname, par in primary.lmfit_result.params.items()
               if pname.startswith(prefix) and par.vary)


def _is_main_role(role: str) -> bool:
    """Main-slot convention: bare role or region-prefixed role starts 'main'."""
    return role.split("__")[-1].startswith("main")


def _linked_groups(model: CandidateModel) -> list[list[ComponentSlot]]:
    """
    Connected components of non-main slots over ``linked_to`` edges (edges
    touching a main slot do not bind — mains are never absent-eligible, so a
    satellite linked to a main is its own group; a satellite DOUBLET
    (sat5/2 → sat7/2) is one group).
    """
    non_main = [s for s in model.slots if not _is_main_role(s.role)]
    roles = {s.role for s in non_main}
    parent_of = {s.role: s.linked_to for s in non_main
                 if s.linked_to is not None and s.linked_to in roles}

    def root(role: str) -> str:
        while role in parent_of:
            role = parent_of[role]
        return role

    groups: dict[str, list[ComponentSlot]] = {}
    for s in non_main:
        groups.setdefault(root(s.role), []).append(s)
    return list(groups.values())


def _identify_absent_slots(
    model: CandidateModel,
    stability: ModelStability,
    slot_areas: dict[str, float],
    primary: FitOutcome,
    persistence_threshold: float = ABSENT_SLOT_PERSISTENCE_THRESHOLD,
    area_fraction_threshold: float = ABSENT_SLOT_AREA_FRACTION,
) -> list[AbsentSlotReport]:
    """
    Absent classification is ATOMIC per linked group: a slot whose amplitude
    or shape is expression-tied to a partner cannot be absent while the
    partner is present (a spin-orbit satellite pair is one physical feature).
    Every member must individually meet the persistence + area criteria for
    the group to be classified absent.

    The area fraction is normalized against the mains of the SLOT'S OWN
    (region, phase) when any exist — in a joint co-fit, normalizing against
    the global main area would let a huge foreign main (e.g. the BN N 1s
    line in a U 4f + N 1s window) dilute a real satellite of the smaller
    element below the threshold (Codex Stage-3 finding #2).  Falls back to
    the global main area for slots without same-scope mains (e.g. proposals,
    which are region-unassigned).
    """
    global_main_area = sum(a for role, a in slot_areas.items() if _is_main_role(role))
    if global_main_area <= 0:
        return []

    scoped_main_area: dict[tuple[str, str], float] = {}
    for s in model.slots:
        if _is_main_role(s.role):
            key = (s.region, s.phase_id)
            scoped_main_area[key] = scoped_main_area.get(key, 0.0) \
                + float(slot_areas.get(s.role, 0.0))

    def _member_report(slot: ComponentSlot) -> Optional[AbsentSlotReport]:
        sstab = stability.per_slot.get(slot.role)
        if sstab is None or sstab.persistence >= persistence_threshold:
            return None
        main_area = scoped_main_area.get((slot.region, slot.phase_id), 0.0)
        if main_area <= 0:
            main_area = global_main_area
        area = float(slot_areas.get(slot.role, 0.0))
        frac = area / main_area
        if frac >= area_fraction_threshold:
            return None
        return AbsentSlotReport(
            role=slot.role, persistence=sstab.persistence, fitted_area=area,
            main_area=main_area, area_fraction=frac,
    roi_bounds: Optional[tuple[float, float]] = None
    # accepted while PEGGING the ordinary FWHM ceiling — the feature is
    # broader than an ordinary component with no known-broad justification;
    # the fit is held at the physical limit and the result is CONDITIONAL
    width_capped: bool = False


@dataclass
class CoincidenceReport:
    center_be: float
    contributors: list[tuple[str, bool]]


@dataclass
class ProposalPassTiming:
    candidate_name: str
    n_flagged: int
    n_over_cap: int
    n_attempted: int
    n_fast_rejected: int
    n_stability_rejected: int
    n_accepted: int
    wall_time_sec: float
    timed_out: bool


@dataclass
class ModelReport:
    """Complete diagnostics for one candidate — no collapse to one scalar."""
    model: CandidateModel
    primary_fit: FitOutcome
    bic: float
    stability: ModelStability
    residuals: ResidualDiagnostics
    plausibility: PlausibilityFlags
    absent_slots: list[AbsentSlotReport] = field(default_factory=list)
    proposed_peaks: list[ProposedPeakReport] = field(default_factory=list)
    augmented_from: Optional[str] = None
    # Full lmfit param names fixed at their bounds by the decisive-override
    # bound-fixed refit (empty for ordinary reports).  Stability figures on
    # such a report are inherited from the free (pegged) fit — a documented
    # approximation.
    boundary_fixed_params: list[str] = field(default_factory=list)

    @property
    def reduced_chi_sq(self) -> float:
        dof = max(self.primary_fit.n_data - self.primary_fit.n_params, 1)
        return self.primary_fit.weighted_chi_sq / dof

    @property
    def adjusted_n_params(self) -> int:
        removed = sum(a.removed_n_params for a in self.absent_slots)
        return max(self.primary_fit.n_params - removed, 1)

    @property
    def bic_adjusted(self) -> float:
        """BIC* (heuristic — absent-slot params arithmetically subtracted;
        the BIC/IC math review requires the raw full-k and weighted
        counterparts REPORTED beside it: see bic_raw / bic_weighted)."""
        n = self.primary_fit.n_data
        rss = self.primary_fit.residual_sum_sq
        if n <= 0 or rss <= 0:
            return float("inf")
        return n * np.log(rss / n) + self.adjusted_n_params * np.log(n)

    @property
    def bic_raw(self) -> float:
        """Full-k, no absent-slot adjustment — reported beside the labeled
        heuristic so the adjustment can never silently decide alone
        (BIC/IC math review: 'large-model RSS with small-model penalty')."""
        return compute_bic(self.primary_fit)

    @property
    def bic_weighted(self) -> float:
        """Known-σ (weighted-χ²) FULL-k BIC: χ²_w + k·ln n with k = the
        actual free-parameter count (NO absent-slot adjustment — the
        adjustment is the labeled heuristic on BIC*; letting it into the
        companion criterion would let the heuristic shape the
        weighted-vs-RSS disagreement it exists to expose).  This is the
        criterion CONSISTENT with the Poisson-weighted fits; the ranking
        still uses BIC*, and weighted_ic_disagreement fires when the two
        criteria pick different survivors."""
        n = self.primary_fit.n_data
        chi = self.primary_fit.weighted_chi_sq
        if n <= 0 or not np.isfinite(chi):
            return float("inf")
        return chi + self.primary_fit.n_params * np.log(n)

    @property
    def n_eff_lag1(self) -> Optional[float]:
        """Effective sample size from the lag-1 autocorrelation of the
        weighted residuals: n·(1−ρ)/(1+ρ).  Oversampled/correlated spectra
        make the raw n in k·ln(n) (and the ΔBIC thresholds) overconfident
        — reported so consumers can see how far the independence
        assumption is stretched (BIC/IC math review)."""
        lm = self.primary_fit.lmfit_result
        if lm is None or getattr(lm, "residual", None) is None:
            return None
        r = np.asarray(lm.residual, dtype=float)
        if len(r) < 8 or float(np.std(r)) == 0.0:
            return None
        r = r - r.mean()
        rho = float(np.sum(r[:-1] * r[1:]) / np.sum(r * r))
        rho = min(max(rho, -0.99), 0.99)
        return float(len(r) * (1.0 - rho) / (1.0 + rho))

    @property
    def active_min_persistence(self) -> float:
        absent_roles = {a.role for a in self.absent_slots}
        active = [s for s in self.stability.per_slot.values() if s.role not in absent_roles]
        if not active:
            return 0.0
        return min(s.persistence for s in active)


def compute_bic(fit: FitOutcome) -> float:
    """fitalg likelihood convention: BIC = n·ln(RSS/n) + k·ln(n)."""
    n, rss = fit.n_data, fit.residual_sum_sq
    if n <= 0 or rss <= 0:
        return float("inf")
    return n * np.log(rss / n) + fit.n_params * np.log(n)


@dataclass
class ComparisonResult:
    reports: list[ModelReport]
    report: ModelReport, exclude_roles: frozenset | set = frozenset()
) -> list[dict]:
    """Winning decomposition as backend-spec-shaped dicts."""
    peaks = []
    lm = report.primary_fit.lmfit_result
    for slot in report.model.slots:
        if slot.role in exclude_roles:
            continue
        comp = next((c for c in report.primary_fit.components
                     if c.slot_role == slot.role), None)
        if comp is None:
            continue
        rec = {
            "role": slot.role,
            "region": slot.region,
            "phase_id": slot.phase_id,
            "shape": BACKEND_SHAPE[slot.line_shape],
            "center": comp.position,
            "fwhm": comp.fwhm,
            "amplitude": comp.amplitude,
            **comp.shape_params,
        }
        if lm is not None:
            prefix = _slot_prefix(slot.role)
            stderr = {}
            for pname, par in lm.params.items():
                if pname.startswith(prefix) and par.stderr is not None:
                    stderr[pname[len(prefix):]] = float(par.stderr)
            if stderr:
                rec["stderr"] = stderr
        peaks.append(rec)
    return peaks


def build_analysis_record(
    grammar: CandidateGrammar, result: ComparisonResult
) -> dict:
    """
    The tab-level ``analysis`` payload — REGENERABLE ONLY (spec §1: older
    clients drop it on resave; no human decisions may live here).
    """
    filtered_reason = {r.model.name: why for r, why in result.filtered_out}
    survivor_rank = {r.model.name: i + 1 for i, r in enumerate(result.survivors)}

    candidates = []
    for r in result.reports:
        name = r.model.name
    spec: ProposalSpec,
    noise_floor: float,
    n_refits: int,
    rng_seed: int,
    absent_slot_area_fraction: float,
    absent_slot_persistence_threshold: float,
    diagnostic_windows: dict[str, tuple[float, float]],
    budget_remaining: float = float("inf"),
    fit_full_window: bool = False,
    endpoint_avg: int = 1,
) -> tuple[Optional[ModelReport], ProposedPeakReport, str]:
    attempt_start = time.perf_counter()
    base_model = base_report.model
    base_fit = base_report.primary_fit
    aug_model = _augmented_candidate(base_model, spec)

    roi = (float(np.min(x)), float(np.max(x)))
    pr = ProposedPeakReport(
        role=spec.role, detection_windows=list(spec.detection_windows),
        detection_energy=spec.detection_energy, detection_ratio=spec.detection_ratio,
        proposed_center_init=spec.center_init, proposed_fwhm_init=spec.fwhm_init,
        proposed_amplitude_init=spec.amplitude_init, roi_bounds=roi,
    )

    def _fast(reason: str):
        pr.rejection_reason = reason
        return None, pr, "fast_rejected"

    # An augmented fit_candidate has no internal wall clock and runs
    # ~10-12 s worst-case; starting one with less than PROPOSAL_MIN_FIT_
    # BUDGET_SEC of sweep budget left would overrun TOTAL_ANALYSIS_TIMEOUT_SEC
    # and the gunicorn --timeout (Codex c1s-fix review, run B MAJOR).  The
    # caller passes budget_remaining = min(pass budget, sweep budget) left.
    if budget_remaining < PROPOSAL_MIN_FIT_BUDGET_SEC:
        return _fast(
            f"insufficient_budget: {budget_remaining:.1f}s left < "
            f"{PROPOSAL_MIN_FIT_BUDGET_SEC:.0f}s needed for one augmented fit")

    bg = _compute_background(x, y, aug_model.background, endpoint_avg=endpoint_avg)
    try:
        init = _initial_params_for_augmented(aug_model, base_fit, spec, x, y - bg,
                                             fit_full_window=fit_full_window)
    except Exception as exc:
        return _fast(f"init_params_error: {exc}")

    primary = fit_candidate(x, y, weights, aug_model, initial_params=init,
                            endpoint_avg=endpoint_avg)
    if not primary.converged:
        return _fast("augmented_fit_did_not_converge")
    comp = next((c for c in primary.components if c.slot_role == spec.role), None)
    if comp is None:
        return _fast("proposed_slot_did_not_populate")

    pr.fitted_center = comp.position
    pr.fitted_fwhm = comp.fwhm
    pr.fitted_amplitude = comp.amplitude
    # A peg on the WIDTH cap alone (fwhm@max) is the ordinary physical FWHM
    # ceiling doing its job: the feature is broader than an ordinary
    # component with no known-broad justification.  KEEP such a proposal —
    # modelled at the physical limit — and let it flag the augmented report
    # (unphysical_widths + the fwhm@max boundary hit → CONDITIONAL) rather
    # than rejecting it and leaving the intensity unmodelled.  A SUBSTANTIVE
    # peg (center at a window edge, amplitude at a wall, or fwhm@MIN = an
    # implausibly narrow spike) is spurious → reject.  (Shape endpoints like
    # gl_ratio=0/1 are valid physics, excluded by the shared detector — see
    # _proposed_slot_pegs.)  NOTE this is re-evaluated AFTER the stability
    # best-outcome promotion below, since a deeper minimum can move a param
    # to a wall (Codex fwhm-cap review, run B BLOCKER).
    width_cap_hit = f"{spec.role}:fwhm@max"
    pr.boundary_hits = _proposed_slot_pegs(primary, spec.role)
    if not _occupies(comp):
        f = (comp.support or {}).get("f")
        return _fast("not supported by the data (removing it does not make the fit significantly worse"
                     + (f", F = {f:.2f} < {_fitting.SUPPORT_MIN_F:.0f}" if f is not None else "") + ")")
    spurious_hits = [h for h in pr.boundary_hits if h != width_cap_hit]
    if spurious_hits:
        return _fast(f"proposed slot boundary pegs: {spurious_hits}")

    mask = (x >= comp.position - PROPOSAL_WINDOW_WIDTH) & \
           (x <= comp.position + PROPOSAL_WINDOW_WIDTH)
    local_sigma = float(np.median(np.sqrt(np.maximum(y[mask], noise_floor)))) \
        if mask.sum() > 1 else float(np.sqrt(max(noise_floor, 1.0)))
    if comp.amplitude < PROPOSAL_AMPLITUDE_SNR * local_sigma:
        return _fast(f"amplitude {comp.amplitude:.1f} < "
                     f"{PROPOSAL_AMPLITUDE_SNR:.1f} × local σ ({local_sigma:.2f})")

    aug_bic = compute_bic(primary)
    pr.delta_bic_vs_base = aug_bic - base_report.bic_adjusted
    if not (aug_bic + PROPOSAL_DELTABIC_THRESHOLD < base_report.bic_adjusted):
        return _fast(
            f"fast pre-check: augmented primary BIC {aug_bic:.2f} does not beat "
            f"base BIC* {base_report.bic_adjusted:.2f} by {PROPOSAL_DELTABIC_THRESHOLD:.1f}"
        )

    # budget_remaining was a snapshot BEFORE the augmented fit; that fit has
    # since consumed wall time, so the stability deadline must be computed
    # from what's ACTUALLY left, not the stale snapshot (Codex c1s-fix
    # review, run B MAJOR — otherwise the stability pass could run
    # min(stale_budget, 35) s past the fit and overrun the sweep budget).
    # The floor (not just <= 0) matters because run_stability_analysis
    # checks its deadline at the TOP of the loop and then runs an unbounded
autofit/engine.py:757:        out.append(FittedComponent(
autofit/engine.py:1122:def match_components_to_slots(
autofit/engine.py:1173:            orphans.append(FittedComponent(
autofit/engine.py:1191:        claimed = FittedComponent(
autofit/engine.py:1331:        slot_map = match_components_to_slots(outcome.components, model, noise_floor,
tests/test_browser_find_peaks_drag.py:187:            "() => document.getElementById('find-peaks-overlay').classList.contains('open')")
tests/test_browser_find_peaks_drag.py:190:            "() => document.getElementById('find-peaks-modal-box').classList.contains('dragging')")
autofit/grammar.py:183:    def contains(self, be: float, fwhm: float, amplitude: float,
tests/test_browser_palette.py:174:        assert pg.evaluate("() => document.getElementById('ref-panel').classList.contains('collapsed')") is True
tests/test_browser_palette.py:182:            return { collapsed: p.classList.contains('collapsed'),
tests/test_browser_palette.py:204:            const dragging = p.classList.contains('dragging');
tests/test_browser_palette.py:222:            return { passthrough: p.classList.contains('identify-passthrough'),
tests/test_browser_palette.py:241:            return { mode: placeMode, passthrough: p.classList.contains('identify-passthrough'),
tests/test_browser_identify_frame.py:219:        light: document.body.classList.contains('light-theme'),
tests/test_browser_identify_frame.py:229:            light: document.body.classList.contains('light-theme'),
tests/test_browser_identify_frame.py:241:        page.evaluate("""() => { if (document.body.classList.contains('light-theme')) toggleTheme();
tests/test_browser_identify_frame.py:511:        return { mode: placeMode, cls: p.classList.contains('identify-passthrough'),
tests/test_browser_batch_roi.py:237:                toastShown: document.getElementById('prominent-toast').classList.contains('show'),
tests/autofit/test_stage2_completeness.py:298:    fat = FittedComponent(slot_role="main_g", position=200.0, fwhm=1.0,
tests/autofit/test_stage2_completeness.py:303:    thin = FittedComponent(slot_role="main_g", position=200.0, fwhm=0.8,
tests/autofit/test_stage2_completeness.py:324:        return FittedComponent(slot_role="detected_peak_0", position=200.0,
tests/autofit/test_stage2_completeness.py:374:    fat = FittedComponent(slot_role="main_g", position=200.0, fwhm=1.7,
tests/autofit/test_stage2_completeness.py:379:    ok = FittedComponent(slot_role="main_g", position=200.0, fwhm=1.5,
tests/autofit/test_c1s_mixed_material_class.py:222:    comp = FittedComponent(slot_role="contamination_CO", position=286.0,
tests/autofit/test_c1s_mixed_material_class.py:268:        FittedComponent(slot_role=role, position=0.0, fwhm=shared_wide_fwhm,
tests/autofit/test_c1s_mixed_material_class.py:314:    fake_comp = FittedComponent(slot_role="contamination_CO", position=286.0,
tests/autofit/test_occupancy_support.py:89:    return FittedComponent(slot_role="?", position=pos, fwhm=1.0, amplitude=amp,
tests/autofit/test_occupancy_support.py:96:    m = match_components_to_slots([main, weak], MODEL, noise_floor=1.0)
tests/autofit/test_occupancy_support.py:106:    m = match_components_to_slots([main, stray], MODEL, noise_floor=1.0)
tests/autofit/test_occupancy_support.py:114:    m = match_components_to_slots([_comp(284.5, 0.0, None)], MODEL, noise_floor=1.0)
tests/autofit/test_occupancy_support.py:136:    comp = FittedComponent(slot_role="minor", position=286.5, fwhm=1.0, amplitude=0.4,
tests/autofit/test_fit_full_window_option.py:299:    comp = FittedComponent(
tests/autofit/test_fit_full_window_option.py:302:    slot_map = match_components_to_slots([comp], model, noise_floor=1.0,
tests/autofit/test_fit_full_window_option.py:326:    populated = FittedComponent(
tests/autofit/test_preseed_dominants.py:185:        return FittedComponent(slot_role=role, position=200.0, fwhm=fwhm,
tests/autofit/test_preseed_dominants.py:220:    comp = FittedComponent(slot_role="wide_unvouched", position=200.0,
tests/autofit/test_broad_justification.py:227:    return FittedComponent(slot_role=role, position=0.0, fwhm=fwhm,
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
  const d = body.diagnostics || {};
  const parts = [];
  if (!body.success) {
    parts.push('None of the peak models tried held up well enough to trust as-is.');
    if (d.analysis_truncated) {
      parts.push(`Only ${d.n_candidates_evaluated} of ${d.n_candidates_total} ` +
        'candidate models were checked before time ran out.');
    }
    parts.push('See the comparison table below for what was tried and why ' +
      'each option was set aside.');
    return parts.join(' ');
  }
  const unassignedPeaks = (body.peaks || []).filter(p => p.region === 'unassigned');
  if (unassignedPeaks.length) {
    const centers = unassignedPeaks.map(p => (+p.center).toFixed(2)).join(', ');
    parts.push(`Found ${unassignedPeaks.length} extra peak(s) at ${centers} eV ` +
      'that aren’t part of a known chemical assignment for this region — ' +
      'their positions come directly from your data, not a reference table, ' +
      'so please review and assign them yourself.');
  }
  if (d.conditional) {
    if (d.conditional_reason === 'decisive_override') {
      const fixed = (d.winner_boundary_fixed_params || []).map(_fpParamLabel).join(', ');
      parts.unshift(`CONDITIONAL — the best-supported model ` +
        `(${_fpModelLabel(d.winner)}) only fits well with ` +
        `${fixed || 'some parameters'} pinned at their limits. Equally ` +
        'clean alternatives are shown in the comparison table below and ' +
        'are worth a look.');
    } else if (d.conditional_reason === 'unstable_last_resort') {
      parts.unshift('LOW CONFIDENCE — no model held together consistently ' +
        'when re-fit from different starting points, so component ' +
        `identities aren’t reliable here. Showing the best-converged ` +
        `attempt (${_fpModelLabel(d.winner)}) so you can see what the data ` +
        'roughly supports — treat every peak as a rough suggestion; the ' +
        'data may not clearly separate one broad feature from several ' +
        'overlapping ones.');
    } else {
      const hits = (d.winner_boundary_hits || []).map(_fpBoundaryHitLabel).join(', ');
      parts.unshift('CONDITIONAL — no model passed every plausibility ' +
        'check cleanly, so this is the best of the stable-but-limited ' +
        `options (${_fpModelLabel(d.winner)}). It hit some parameter ` +
        `limits (${hits || 'see below'}) — worth double-checking those components.`);
    }
  }
  if ((d.winner_unphysical_widths || []).length) {
    const widths = d.winner_unphysical_widths.map(_fpWidthFlagLabel).join('; ');
    parts.push(`LOW CONFIDENCE: ${widths}.`);
  }
  if (d.filtered_dominant_alternative) {
    const fda = d.filtered_dominant_alternative;
    parts.push(`Note: a different model (${_fpModelLabel(fda.name)}) scored ` +
      `better by ${(+fda.delta_bic_vs_winner).toFixed(1)} points but was set ` +
      `aside (${_fpFilterReasonLabel(fda.filter_reason).toLowerCase()}) — ` +
      'worth a look in the comparison table.');
  }
  if (d.analysis_truncated) {
    parts.push(`Only ${d.n_candidates_evaluated} of ${d.n_candidates_total} ` +
      'candidate models were checked before time ran out.');
  }
  if (!parts.length) {
    parts.push('This model passed every check cleanly — stable across ' +
      're-fits, no parameter limits hit, no unexplained extra peaks.');
  }
  return parts.join(' ');
}

function _fpFmt(tpl, vars) {
  return tpl.replace(/\{(\w+)\}/g, (_, k) => vars[k] != null ? vars[k] : '');
}

async function openFindPeaksModal() {
        if oxidation_state is not None:
            raise KeyError(
                f"C 1s defines no oxidation-state override {oxidation_state!r}"
            )
        pid = phase.id
        main_fwhm = _MAIN_FWHM_BY_MATERIAL.get(phase.material, FWHM_RANGE_GRAPHITIC)
        contam_fwhm = _contamination_fwhm_range(phase.material_class)

        def slot(role, window, shape, fwhm_range, **kw) -> ComponentSlot:
            return ComponentSlot(
                role=role, region=REGION, phase_id=pid,
                be_window=window, line_shape=shape, fwhm_range=fwhm_range, **kw,
            )

        def graphitic_main_dsg() -> ComponentSlot:
            return slot(
                "main_graphitic", C1S_WINDOWS["graphitic"], LineShape.DS_G,
                main_fwhm,
                fixed_params=(("beta", DSG_LORENTZIAN_HWHM_C1S),),
                param_ranges=(("alpha", DSG_ALPHA_RANGE_GRAPHITIC),),
            )

        def graphitic_main_asymgl() -> ComponentSlot:
            return slot(
                "main_graphitic", C1S_WINDOWS["graphitic"], LineShape.ASYM_GL,
                main_fwhm,
                param_ranges=(("asymmetry", ASYMGL_ASYMMETRY_RANGE),),
            )

        def aliphatic_main() -> ComponentSlot:
            return slot("main_aliphatic", C1S_WINDOWS["aliphatic"],
                        LineShape.PSEUDO_VOIGT, contam_fwhm)

        shake_up = slot(
            "satellite_pi", C1S_WINDOWS["shake_up_pi"], LineShape.PSEUDO_VOIGT,
            FWHM_RANGE_SATELLITE,
            linked_to="main_graphitic", linked_offset_range=SATELLITE_OFFSET_RANGE,
            broad_justification=(
                "pi->pi* shake-up satellite: physically broad due to "
                "multi-electron excitation (a genuine broadening "
                "mechanism, not merely calibration); the specific range "
                "is further calibrated to the labeled expert set (44 "
                "fits, 1.9-5.0 eV, CALIBRATED 2026-07-03)"
            ),
        )

        def contam(key, linked_fwhm=None, offset=None,
                   fwhm_range=None) -> ComponentSlot:
            kw = {}
            if linked_fwhm:
                kw["fwhm_linked_to"] = linked_fwhm
            if offset:
                mid, hw = offset
                kw["linked_to"] = "main_graphitic"
                kw["linked_offset_range"] = (mid - hw, mid + hw)
            return slot(f"contamination_{key}", C1S_WINDOWS[key],
                        LineShape.PSEUDO_VOIGT,
                        fwhm_range if fwhm_range is not None else contam_fwhm, **kw)

        shared_decl = ((_SHARED_CONTAM_FWHM, contam_fwhm[0], contam_fwhm[1]),)
        keys = ["CO", "C=O", "OC=O"]

        candidates: list[CandidateModel] = []

        def add(name, slots, shared=()):
            candidates.append(CandidateModel(
                name=name, background=BackgroundType.SHIRLEY,
                slots=tuple(slots), shared_fwhm_params=tuple(shared),
            ))

        # --- A family: DS+G asymmetric main + satellite + contaminants ---
        base_a = [graphitic_main_dsg(), shake_up]
        plain = [contam(k) for k in keys]
        add("A0_graphite_asym_satellite", base_a)
        for n in (1, 2, 3):
            add(f"A{n}_graphite_asym_sat_plus_{'_'.join(keys[:n])}",
                base_a + plain[:n])

        # --- A_linked: shared contamination width (Biesinger 2022) ---
        linked = [contam(k, linked_fwhm=_SHARED_CONTAM_FWHM) for k in keys]
        for n in (1, 2, 3):
            add(f"A{n}_linked", base_a + linked[:n], shared_decl)

        # --- A_linked_offset: + offset-parameterized contaminant centers ---
        offset_linked = [
            contam(k, linked_fwhm=_SHARED_CONTAM_FWHM, offset=CONTAM_OFFSETS[k])
            for k in keys
        ]
        for n in (1, 2, 3):
            add(f"A{n}_linked_offset", base_a + offset_linked[:n], shared_decl)

        # --- AG family: asym-GL graphitic main (expert-fit parity family).
        #     Contamination widths use the UNIFORM adjudicated cap — the
        #     former split lab-practice (0.8, 3.5) convention was replaced
        #     per adjudication #5; AG/MG now differ from A/M only in the
        #     graphitic main lineshape. ---
        base_ag = [graphitic_main_asymgl(), shake_up]
        add("AG0_graphite_asymGL_satellite", base_ag)
        for n in (1, 2, 3):
            add(f"AG{n}_graphite_asymGL_sat_plus_{'_'.join(keys[:n])}",
                base_ag + plain[:n])
        for n in (1, 2, 3):
            add(f"AG{n}_linked", base_ag + linked[:n], shared_decl)

        # --- M family: mixed graphitic (DS+G) + aliphatic (PV) two mains ---
        base_m = [graphitic_main_dsg(), aliphatic_main(), shake_up]
        add("M0_graph_asym_aliph_sym_satellite", base_m)
        for n in (1, 2, 3):
            add(f"M{n}_graph_asym_aliph_sym_sat_{'_'.join(keys[:n])}",
                base_m + plain[:n])

        # --- MG family: the expert-practice STRUCTURE — asym-GL graphitic +
        #     aliphatic + satellite + contaminants (uniform adjudicated
        #     contamination cap).  The
        #     reference C 1s fits are exactly MG2-shaped (graphitic asym-GL
        #     284.5 + adventitious 284.8/285.9/287.6 + π→π* ~290.9).
        #     The aliphatic center is OFFSET-LINKED to the graphitic main
        #     (+0.2…+0.6 eV): with a free center the optimizer slides the
        #     aliphatic into the graphitic flank and pegs the window floor
        #     (overlap degeneracy, fitalg LIMITATIONS §9).  The offset window
        #     brackets both the expert practice (+0.30: 284.8 vs 284.5) and
        #     Biesinger's adventitious C-C/C-H at 284.8 vs graphite 284.4
        #     (+0.4).  UNVERIFIED-empirical (labeled-set + convention). ---
        def aliphatic_main_offset() -> ComponentSlot:
            return slot("main_aliphatic", C1S_WINDOWS["aliphatic"],
                        LineShape.PSEUDO_VOIGT, contam_fwhm,
                        linked_to="main_graphitic",
                        linked_offset_range=(0.2, 0.6))

        base_mg = [graphitic_main_asymgl(), aliphatic_main_offset(), shake_up]
        add("MG0_graphAsymGL_aliph_satellite", base_mg)
        for n in (1, 2, 3):
            add(f"MG{n}_graphAsymGL_aliph_sat_{'_'.join(keys[:n])}",
                base_mg + plain[:n])

        # --- B family: symmetric adventitious-carbon models (no satellite —
        #     admissibility: shake-up requires an asymmetric sp² main) ---
        aliph = aliphatic_main()
        aliph_fwhm_param = "s_main_aliphatic_fwhm"
        blinked = [contam(k, linked_fwhm=aliph_fwhm_param) for k in keys]
        add("B2_linked", [aliph] + blinked[:2])
        add("B3_linked", [aliph] + blinked[:3])
        # plain-window symmetric variants (low-priority but admissible)
        graph_sym = slot("main_graphitic", C1S_WINDOWS["graphitic"],
                         LineShape.PSEUDO_VOIGT, main_fwhm)
        add("B2_graphite_sym_CO_C=O", [graph_sym] + plain[:2])
                                    separation but shape + amplitude still
                                    tied: the clean test of "pair separation
                                    ≠ core splitting"
        - ``U2_mains_satfree``    — two fully independent satellites (each
                                    rides its own main; robustness variant)

        ``oxidation_state`` is accepted for the Layer-C seam; assignment is
        parked (spec §3.2) so no overrides are defined.
        """
        if oxidation_state is not None:
            raise KeyError(
                f"U 4f defines no oxidation-state override {oxidation_state!r} "
                "(oxidation-state assignment is parked, spec §3.2)"
            )
        pid = phase.id

        def slot(role, window, shape, fwhm_range, **kw) -> ComponentSlot:
            return ComponentSlot(
                role=role, region=REGION, phase_id=pid,
                be_window=window, line_shape=shape, fwhm_range=fwhm_range, **kw,
            )

        _main_justification = (
            "U(IV) 5f2 open-shell final state: an unresolved multiplet "
            "manifold of unknown line count is the physically-correct "
            "reading of this width (VERIFIED mechanism, Ilton & Bagus, "
            "Surf. Interface Anal. 43 (2011) 1549, DOI 10.1002/sia.3836; "
            "see module docstring); the specific range is UNVERIFIED-"
            "empirical (labeled set 2.44-2.74 eV)"
        )
        _sat_justification = (
            "the U(IV) shake-up satellite is a real physical feature "
            "(Ilton & Bagus 2011), but this specific WIDTH bound is "
            "UNVERIFIED-empirical (labeled set 2.09-3.30 eV), not itself "
            "derived from a cited broadening magnitude"
        )

        main_72 = slot(
            "main_u4f72", U4F72_WINDOW, LineShape.LACX, U4F_MAIN_FWHM_RANGE,
            param_ranges=(("alpha", U4F_LACX_ALPHA_RANGE),
                          ("beta", U4F_LACX_BETA_RANGE),
                          ("m", U4F_LACX_M_RANGE)),
            broad_justification=_main_justification,
        )
        main_52 = slot(
            "main_u4f52", U4F52_WINDOW, LineShape.LACX, U4F_MAIN_FWHM_RANGE,
            linked_to="main_u4f72",
            linked_offset_range=U4F_SPLITTING_RANGE,
            area_ratio=U4F_RATIO_DEFAULT,
            area_ratio_range=U4F_RATIO_RANGE,
            share_parent_params=("alpha", "beta", "m", "fwhm"),
            broad_justification=_main_justification,
        )

        sat_72 = slot(
            "satellite_u4f72", U4F_SAT72_WINDOW, LineShape.PSEUDO_VOIGT,
            U4F_SAT_FWHM_RANGE,
            linked_to="main_u4f72",
            linked_offset_range=U4F_SAT_OFFSET_RANGE,
            broad_justification=_sat_justification,
        )
        sat_52 = slot(
            "satellite_u4f52", U4F_SAT52_WINDOW, LineShape.PSEUDO_VOIGT,
            U4F_SAT_FWHM_RANGE,
            linked_to="satellite_u4f72",
            linked_offset_range=U4F_SPLITTING_RANGE,
            area_ratio=U4F_RATIO_DEFAULT,
            area_ratio_range=U4F_RATIO_RANGE,
            share_parent_params=("gl_ratio", "fwhm"),
            broad_justification=_sat_justification,
        )
        # Free pair separation, everything else still tied (U1b).
        sat_52_freesep = slot(
            "satellite_u4f52", U4F_SAT52_WINDOW, LineShape.PSEUDO_VOIGT,
            U4F_SAT_FWHM_RANGE,
            linked_to="satellite_u4f72",
            linked_offset_range=U4F_SATPAIR_SEP_RANGE,
            area_ratio=U4F_RATIO_DEFAULT,
            area_ratio_range=U4F_RATIO_RANGE,
            share_parent_params=("gl_ratio", "fwhm"),
            broad_justification=_sat_justification,
        )

        # Robustness variant: satellites ride their own mains independently
        # (free amplitudes, independent offsets — no pair linkage).
        sat_72_free = slot(
            "satellite_u4f72", U4F_SAT72_WINDOW, LineShape.PSEUDO_VOIGT,
            U4F_SAT_FWHM_RANGE,
            linked_to="main_u4f72",
            linked_offset_range=U4F_SAT_OFFSET_RANGE,
            broad_justification=_sat_justification,
        )
        sat_52_free = slot(
            "satellite_u4f52", U4F_SAT52_WINDOW, LineShape.PSEUDO_VOIGT,
            U4F_SAT_FWHM_RANGE,
            linked_to="main_u4f52",
            linked_offset_range=U4F_SAT_OFFSET_RANGE,
            broad_justification=_sat_justification,
        )

        return [
            CandidateModel(name="U0_mains", background=U4F_BACKGROUND,
                           slots=(main_72, main_52)),
            CandidateModel(name="U1_mains_satpair", background=U4F_BACKGROUND,
                           slots=(main_72, main_52, sat_72, sat_52)),
            CandidateModel(name="U1b_mains_satpair_freesep",

exec
/bin/zsh -lc "rg -n 'role=|slot\\(|slots\\(' autofit/regions/fe2p.py autofit/regions/cl2p.py autofit/candidates.py; sed -n '65,100p' docs/superpowers/plans/2026-09-27-occupancy-f-test.md; sed -n '2360,2435p' autofit/engine.py; sed -n '2490,2580p' autofit/engine.py; sed -n '280,405p' autofit/methods/bayesian_exchange_mc.py; rg -n 'noise-floor|noise floor|noise_floor|occup|amplitude.*(1\\.0|[<>])' app.py autofit/adapter.py tests/autofit/test_occupancy_support.py; rg --files tests/autofit | rg 'stability|confidence|proposal|full_window|override|absent|engine'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
rg: autofit/regions/fe2p.py: No such file or directory (os error 2)
autofit/candidates.py:464:            role=f"detected_peak_{i}",
autofit/candidates.py:722:            role=role,
autofit/candidates.py:762:            seeded_role=e.get("seeded_role"),
autofit/regions/cl2p.py:144:                role="main_cl2p32", region=REGION, phase_id=pid,
autofit/regions/cl2p.py:155:                    role="main_cl2p12", region=REGION, phase_id=pid,
autofit/regions/cl2p.py:167:                role="main_cl2p12", region=REGION, phase_id=pid,

**D. The model-mismatch honesty signal (README follow-up 2).** See §3 — an
owner decision.

## 2. Measurements

### Stress honesty battery (`tests/autofit/test_stress_honesty.py`)

With F + the orphan split: 11 passed, 1 failed — `test_bg_mismatch_surfaces_loudly`
(a Shirley-shaped truth fitted with straight-line backgrounds), as the README
predicted. Under F the winner is **P2, the TRUE two-peak model**
(`true_candidates=("P2",)`); P3's third component compensated for the wrong
background, F calls it unsupported (its gain divided by the misfit χ²ᵣ ≈ 284),
P3's persistence for that slot drops to 0 and P3 leaves the conditional pool.
The result still carries the winner's χ²ᵣ 308.7 (comparison table), the
winner row's `autocorr_flag`, and `filtered_dominant_alternative` (P3,
ΔBIC* 153 — the page's red "a better-scoring model was set aside" banner); it
is no longer `conditional`.

### Candidate mismatch signals, measured (winner of each run; ×0.1 = the same spectrum as a rate)

| spectrum | scale | χ²ᵣ | residual lag-1 autocorrelation flagged | n_eff / n |
|---|---|---|---|---|
| stress: bg mismatch | ×1 / ×0.1 | 308.7 / 30.9 | yes / yes | 0.0075 / 0.0075 |
| stress: bg matched control | ×1 / ×0.1 | 1.31 / 0.13 | no / no | ~1.0 / ~1.0 |
| 8 real committed C 1s scans (3 gate anchors + 5) | ×1 | 1.30–6.46 | **yes on 8 of 8** | 0.10–0.55 |
| same | ×0.1 | 0.15–3.51 | yes on 8 of 8 | 0.04–0.49 |

* χ²ᵣ is not scale-free (it moves with the counts: ×0.1 divides it by 10), and
  on real data it grows with the counts for a slightly imperfect lineshape — a
  χ²ᵣ cutoff is exactly the design rule's failure.
* The residual lag-1 autocorrelation IS scale-free (n_eff/n identical at ×1 and
  ×0.1), but real XPS fits are not noise-limited: every real winner has
  structured residuals. As a flag it fires on everything; as a number it
  separates the stress case (0.0075) from real fits (≥ 0.04) only by a factor
  of ~5 and only with a chosen constant.
    # checks its deadline at the TOP of the loop and then runs an unbounded
    # fit_candidate — so starting stability with only a few seconds left
    # would still overrun by ~one worst-case fit (Codex c1s-fix RE-CHECK,
    # run B MAJOR: disposition 2 was not fully closed by the top guard).
    remaining = budget_remaining - (time.perf_counter() - attempt_start)
    if remaining < PROPOSAL_MIN_FIT_BUDGET_SEC:
        pr.rejection_reason = (
            f"insufficient_budget before stability: {remaining:.1f}s left < "
            f"{PROPOSAL_MIN_FIT_BUDGET_SEC:.0f}s (one refit could overrun)")
        return None, pr, "fast_rejected"

    stability = run_stability_analysis(
        x, y, weights, aug_model, primary,
        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
        deadline=time.perf_counter() + min(remaining,
                                           PROPOSAL_STABILITY_TIMEOUT_SEC),
        fit_full_window=fit_full_window,
        endpoint_avg=endpoint_avg,
    )
    if (stability.best_outcome is not None
            and stability.best_outcome.weighted_chi_sq < primary.weighted_chi_sq):
        primary = stability.best_outcome
        comp = next((c for c in primary.components if c.slot_role == spec.role), comp)
        if comp is not None:
            pr.fitted_center = comp.position
            pr.fitted_fwhm = comp.fwhm
            pr.fitted_amplitude = comp.amplitude
    # Re-evaluate the proposed-slot pegs against the FINAL (possibly
    # stability-promoted) outcome — a deeper minimum can move a param to a
    # wall the initial fit did not touch (Codex fwhm-cap review, run B
    # BLOCKER): a stability-promoted center@min must STILL reject, and a
    # stability-INTRODUCED fwhm@max must set width_capped so the payload
    # matches the emitted decomposition.
    pr.boundary_hits = _proposed_slot_pegs(primary, spec.role)
    spurious_hits = [h for h in pr.boundary_hits if h != width_cap_hit]
    if spurious_hits:
        pr.rejection_reason = (
            f"proposed slot boundary pegs (post-stability): {spurious_hits}")
        return None, pr, "stability_rejected"
    pr.width_capped = pr.boundary_hits == [width_cap_hit]
    sstab = stability.per_slot.get(spec.role)
    if sstab is None:
        pr.rejection_reason = "proposed slot missing from stability output"
        return None, pr, "stability_rejected"
    pr.persistence = sstab.persistence
    if sstab.persistence < PROPOSAL_PERSISTENCE_THRESHOLD:
        pr.rejection_reason = (f"persistence {sstab.persistence:.2f} < "
                               f"{PROPOSAL_PERSISTENCE_THRESHOLD:.2f}")
        return None, pr, "stability_rejected"

    y_fit_aug = (primary.lmfit_result.best_fit + primary.background
                 if primary.lmfit_result is not None else np.zeros_like(y))
    residuals = compute_residual_diagnostics(x, y, y_fit_aug, noise_floor, diagnostic_windows)
    slot_areas = compute_slot_areas(aug_model, primary, x)
    absent = _identify_absent_slots(
        aug_model, stability, slot_areas, primary,
        persistence_threshold=absent_slot_persistence_threshold,
        area_fraction_threshold=absent_slot_area_fraction,
    )
    aug_report = ModelReport(
        model=aug_model, primary_fit=primary, bic=compute_bic(primary),
        stability=stability, residuals=residuals,
        plausibility=PlausibilityFlags(
            boundary_hits=list(primary.boundary_hits),
            unphysical_widths=_unphysical_width_flags(primary.components, aug_model),
            orphan_peaks=stability.orphan_rate > 0.1,
        ),
        absent_slots=absent, augmented_from=base_model.name,
    )

    delta = aug_report.bic_adjusted - base_report.bic_adjusted
    pr.delta_bic_vs_base = delta
    if not (delta < -PROPOSAL_DELTABIC_THRESHOLD):
        pr.rejection_reason = (f"ΔBIC* = {delta:+.2f} does not beat "
                               f"-{PROPOSAL_DELTABIC_THRESHOLD:.1f} improvement threshold")
        return None, pr, "stability_rejected"
    diagnostic_windows: dict[str, tuple[float, float]],
    noise_floor: float,
    n_refits: int,
    rng_seed: int,
    fit_full_window: bool = False,
    endpoint_avg: int = 1,
) -> Optional[ModelReport]:
    """
    Refit a boundary-limited candidate with each pegged parameter FIXED at
    the bound it pegged to, so its BIC* uses an honest parameter count (a
    bound-pegged free parameter invalidates the interior-Laplace BIC
    approximation).

    Honesty requirements (Codex re-check blockers/major):
    - the refit must not itself peg any NEW bound — otherwise the
      interior-Laplace comparison is invalid again → return None;
    - a FRESH stability pass runs on the bound-fixed model (the constrained
      parameters stay fixed in every multi-start refit) — no inherited
      figures;
    - NO absent-slot adjustment is applied to the refit: its BIC* uses the
      full varying-parameter count (conservative — errs against promotion).
    """
    import dataclasses

    lm = report.primary_fit.lmfit_result
    if lm is None or not report.plausibility.boundary_hits:
        return None
    params = lm.params.copy()
    fixed: dict[str, float] = {}
    for hit in report.plausibility.boundary_hits:
        try:
            role_param, side = hit.rsplit("@", 1)
            role, pname = role_param.split(":", 1)
        except ValueError:
            continue
        full = _slot_prefix(role) + pname
        par = params.get(full)
        if par is None or not par.vary:
            continue
        val = par.min if side == "min" else par.max
        par.set(value=val, vary=False)
        fixed[full] = float(val)
    if not fixed:
        return None

    outcome = fit_candidate(x, y, weights, report.model, initial_params=params,
                            endpoint_avg=endpoint_avg)
    if not outcome.converged:
        return None
    if outcome.boundary_hits:
        # fixing one wall pushed the fit onto another — still not an
        # interior optimum; no honest BIC* comparison is possible
        return None

    stability = run_stability_analysis(
        x, y, weights, report.model, outcome,
        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
        fixed_param_values=fixed,
        deadline=time.perf_counter() + CANDIDATE_TIMEOUT_SEC,
        fit_full_window=fit_full_window,
        endpoint_avg=endpoint_avg,
    )
    y_fit = (outcome.lmfit_result.best_fit + outcome.background
             if outcome.lmfit_result is not None else np.zeros_like(y))
    return ModelReport(
        model=dataclasses.replace(report.model, name=report.model.name + "+bfix"),
        primary_fit=outcome,
        bic=compute_bic(outcome),
        stability=stability,
        residuals=compute_residual_diagnostics(
            x, y, y_fit, noise_floor, diagnostic_windows),
        plausibility=PlausibilityFlags(
            boundary_hits=[],
            # width pegs that were FIXED at the cap are still at the physical
            # ceiling — a fixed-at-2.0 ordinary component is no more physical
            # than a pegged one, so keep flagging it
            unphysical_widths=_unphysical_width_flags(outcome.components, report.model),
            orphan_peaks=stability.orphan_rate > 0.1,
        ),
        absent_slots=[],                      # conservative full-k BIC*
        boundary_fixed_params=sorted(fixed),
        # carry the proposal lineage forward so a width-capped proposal
        # promoted via decisive-override keeps its width_capped/proposed_peaks
        # record on the winner row (Codex fwhm-cap review, run A MINOR)
        proposed_peaks=list(report.proposed_peaks),
        augmented_from=report.augmented_from,
    )


def _apply_decisive_override(
    x: np.ndarray,
            if rho <= 0.0:
                break
            tau += 2.0 * rho
        out.append(float(n / tau))
    return out


_ALLOWED_OPTIONS = {
    "n_replicas", "beta_min", "n_sweeps", "burn_fraction", "exchange_every",
    "rng_seed", "candidate_filter", "ci_level", "noise_floor",
    "seed_replicates",
    "endpoint_avg",
}


class BayesianExchangeMCMethod(PeakFitMethod):
    id = "bayesian_exchange_mc"
    label = "Bayesian (exchange Monte Carlo)"
    requires_grammar = True

    def run(
        self,
        x: np.ndarray,
        y: np.ndarray,
        weights: Optional[np.ndarray] = None,
        grammar: Optional[CandidateGrammar] = None,
        peak_specs: Optional[list[dict]] = None,
        options: Optional[dict[str, Any]] = None,
        progress_cb: Optional[Callable[[dict], None]] = None,
    ) -> MethodResult:
        if grammar is None:
            raise ValueError("bayesian_exchange_mc requires a resolved grammar")
        opts = dict(options or {})
        unknown = set(opts) - _ALLOWED_OPTIONS
        if unknown:
            raise ValueError(f"unknown bayesian_exchange_mc options: {sorted(unknown)}")

        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        ci = float(opts.pop("ci_level", DEFAULT_CI_LEVEL))
        mc_kwargs = dict(
            n_replicas=int(opts.pop("n_replicas", DEFAULT_N_REPLICAS)),
            beta_min=float(opts.pop("beta_min", DEFAULT_BETA_MIN)),
            n_sweeps=int(opts.pop("n_sweeps", DEFAULT_N_SWEEPS)),
            burn_fraction=float(opts.pop("burn_fraction", DEFAULT_BURN_FRACTION)),
            exchange_every=int(opts.pop("exchange_every", DEFAULT_EXCHANGE_EVERY)),
            rng_seed=int(opts.pop("rng_seed", 0)),
        )
        opts.pop("noise_floor", None)     # accepted for symmetry; unused
        candidates = grammar.candidates
        cand_filter = opts.pop("candidate_filter", None)
        if cand_filter is not None:
            wanted = set(cand_filter)
            candidates = [c for c in candidates if c.name in wanted]

        # Independent seeded evidence replicates (Codex Stage-5 blocker #1,
        # re-check evidence: at reduced budgets a single run can report a
        # confidently-resolved F gap that a different seed flips — the
        # split-half proxy is a LOWER bound and can miss it).  k replicates
        # cost k× runtime; the across-replicate half-range is a genuine
        # independent-run MC error and dominates the split-half bound in the
        # selection warning.  Default 1 = cost-neutral single run.
        seed_replicates = int(opts.pop("seed_replicates", 1))
        if seed_replicates < 1:
            raise ValueError("seed_replicates must be >= 1")

        endpoint_avg = pop_endpoint_avg(opts)
        per_candidate: list[dict] = []
        runs: dict[str, dict] = {}
        for model in candidates:
            bg = _compute_background(x, y, model.background, endpoint_avg=endpoint_avg)
            y_net = y - bg
            try:
                space = _param_space(model, x, y_net)
                run = run_exchange_mc(x, y_net, space, weights=weights, **mc_kwargs)
                rep_fs = [run["free_energy"]]
                for j in range(1, seed_replicates):
                    rep_kwargs = dict(mc_kwargs,
                                      rng_seed=mc_kwargs["rng_seed"] + j)
                    rep_space = _param_space(model, x, y_net)
                    rep = run_exchange_mc(x, y_net, rep_space, weights=weights,
                                          **rep_kwargs)
                    rep_fs.append(rep["free_energy"])
            except Exception as exc:
                per_candidate.append({"name": model.name, "error": str(exc)})
                continue
            runs[model.name] = {"run": run, "model": model, "space": space,
                                "bg": bg, "y_net": y_net}
            min_ess = float(min(run["ess"])) if run["ess"] else 0.0
            rep_spread = ((max(rep_fs) - min(rep_fs)) / 2.0
                          if len(rep_fs) > 1 else None)
            split_err = run["free_energy_split_half_error"]
            mc_error = max([e for e in (split_err, rep_spread) if e is not None],
                           default=None)
            per_candidate.append({
                "name": model.name,
                # replicate-mean F when replicated; the posterior summary
                # (peaks/CIs) stays the BASE seed's run — flagged for
                # consumers below (Codex Stage-5 re-check #2 major)
                "free_energy": (float(np.mean(rep_fs)) if len(rep_fs) > 1
                                else run["free_energy"]),
                "free_energy_is_replicate_mean": len(rep_fs) > 1,
                "free_energy_replicates": (list(map(float, rep_fs))
                                           if len(rep_fs) > 1 else None),
                "free_energy_replicate_spread": rep_spread,
                "free_energy_mc_error": mc_error,
                "free_energy_split_half_error": run["free_energy_split_half_error"],
                "sigma_hat": run["sigma_hat"],
                "n_components": int(model.n_components),
                "swap_acceptance": run["swap_acceptance"],
                "n_posterior_samples": int(run["n_post"]),
                "min_effective_sample_size": min_ess,
                # Honesty gate on the "calibrated uncertainty" claim: with a
                # low ESS the chains are too correlated for the credible
                # intervals to be trusted — increase n_sweeps.
                "ci_reliability_warning": (
                    "LOW effective sample size — credible intervals likely "
                    "underestimate uncertainty; increase n_sweeps"
                ) if min_ess < ESS_RELIABLE_MIN else None,
            })

        scored = [c for c in per_candidate if "free_energy" in c]
        if not scored:
            return MethodResult(
                method_id=self.id, success=False,
                analysis={"method": self.id, "candidates": per_candidate},
rg: autofit/adapter.py: No such file or directory (os error 2)
app.py:52:# value lets a single request occupy a worker for many minutes (audit F7).
tests/autofit/test_occupancy_support.py:1:"""Find Peaks occupancy is the server's support F test, not a 1-count floor
tests/autofit/test_occupancy_support.py:2:(noise-floor unit, 2026-09-27; plan
tests/autofit/test_occupancy_support.py:3:docs/superpowers/plans/2026-09-27-occupancy-f-test.md).
tests/autofit/test_occupancy_support.py:8:"not supported by the data" outcome uses. The old rule, ``amplitude > 1.0``,
tests/autofit/test_occupancy_support.py:9:judged a slot occupied at 1.5 counts and empty at 0.5 whatever the data's
tests/autofit/test_occupancy_support.py:16:  occupant — the old floor accepted it;
tests/autofit/test_occupancy_support.py:17:* an unsupported component occupies no slot and is NOT an orphan (an orphan is
tests/autofit/test_occupancy_support.py:27:from autofit.engine import (FittedComponent, _occupies, fit_candidate,
tests/autofit/test_occupancy_support.py:73:    assert a["minor"].amplitude > 1.0 > b["minor"].amplitude, "the old rule would flip here"
tests/autofit/test_occupancy_support.py:77:        assert _occupies(a[role]) and _occupies(b[role])
tests/autofit/test_occupancy_support.py:80:def test_residue_above_one_count_is_not_an_occupant():
tests/autofit/test_occupancy_support.py:81:    # 5 counts on a 1e5-count baseline: the old floor called it occupied
tests/autofit/test_occupancy_support.py:85:    assert not _occupies(minor)
tests/autofit/test_occupancy_support.py:96:    m = match_components_to_slots([main, weak], MODEL, noise_floor=1.0)
tests/autofit/test_occupancy_support.py:106:    m = match_components_to_slots([main, stray], MODEL, noise_floor=1.0)
tests/autofit/test_occupancy_support.py:111:def test_without_a_fit_behind_it_occupancy_is_the_sign_of_the_amplitude():
tests/autofit/test_occupancy_support.py:112:    assert _occupies(_comp(284.5, 0.3, None)), "0.3 > 0: no floor"
tests/autofit/test_occupancy_support.py:113:    assert not _occupies(_comp(284.5, 0.0, None))
tests/autofit/test_occupancy_support.py:114:    m = match_components_to_slots([_comp(284.5, 0.0, None)], MODEL, noise_floor=1.0)
tests/autofit/test_occupancy_support.py:138:    d = build_confidence_vector(_Report(comp), "minor", noise_floor=1.0)["detectability"]
tests/autofit/test_engine_doublet.py
tests/autofit/test_fit_full_window_option.py

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile, sys; tempfile.tempdir = \"/tmp\"; sys.modules[\"matplotlib\"] = None; import pytest; raise SystemExit(pytest.main([\"-p\", \"no:cacheprovider\", \"--capture=sys\", \"tests/autofit/test_occupancy_support.py\", \"tests/autofit/test_stress_honesty.py\", \"-q\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
codex
I found a possible gap in the proposal path: support is checked before stability refits, but a better refit can replace that fit without another support check. I’m probing whether this can accept a component whose final verdict is unsupported. The first test run failed during imports because of the read-only sandbox; I’ve restarted it with caches disabled and without temporary-file discovery.

exec
/bin/zsh -lc "rg -n 'CandidateGrammar|class Phase|class Sample|def resolve|def build_candidate' autofit/grammar.py autofit/regions/__init__.py autofit/candidates.py; rg -n 'grammar|custom' app.py | tail -35; sed -n '1,125p' tests/autofit/test_fit_full_window_option.py; sed -n '1,120p' tests/autofit/test_engine_doublet.py; sed -n '1,110p' tests/autofit/test_fwhm_cap.py; sed -n '2430,2468p' autofit/engine.py; rg -n 'bg_mismatch_case|def _.*grammar|def .*model' tests/autofit/stress_cases.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
autofit/candidates.py:544:def build_candidate_pool(
autofit/grammar.py:4:``resolve(phases, regions, ...)`` → :class:`CandidateGrammar`.
autofit/grammar.py:38:    "CandidateModel", "CandidateGrammar", "PhaseAmbiguityError",
autofit/grammar.py:95:class Phase:
autofit/grammar.py:217:class CandidateGrammar:
autofit/grammar.py:236:class PhaseAmbiguityError(ValueError):
autofit/grammar.py:268:def resolve(
autofit/grammar.py:275:) -> CandidateGrammar:
autofit/grammar.py:300:                      regions are listed in ``CandidateGrammar.
autofit/grammar.py:500:    grammar = CandidateGrammar(
autofit/grammar.py:529:def _guard_phase_leakage(grammar: CandidateGrammar, phases: list[Phase]) -> None:
autofit/regions/__init__.py:23:    def build_candidates(
316:    __slots__ = ("x", "y", "method_id", "opts", "peak_specs", "grammar")
318:    def __init__(self, x, y, method_id, opts, peak_specs, grammar):
324:        self.grammar = grammar
329:    (session lookup through grammar resolution) — pure extract-method
332:    from autofit.grammar import (MaterialClass, Phase,
396:    grammar = None
405:            grammar = resolve(
411:    return _AnalyzeContext(x, y, method_id, opts, peak_specs, grammar)
422:            ctx.x, ctx.y, grammar=ctx.grammar, peak_specs=ctx.peak_specs,
437:    degradation branch (a region with zero grammar candidates still RUNS
440:    grammar = ctx.grammar
441:    if (grammar is not None and grammar.structural_only
442:            and not grammar.candidates and not res.success):
445:            for slug, entries in grammar.provenance.items()
451:            "structural_only": list(grammar.structural_only),
452:            "structure_report": grammar.provenance,
453:            "notes": grammar.notes,
461:                "curated windows to enable grammar fitting for: "
462:                + ", ".join(grammar.structural_only)),
477:        "structural_only": list(grammar.structural_only) if grammar else [],
490:    if grammar is not None and grammar.structural_only:
493:        payload["structure_report"] = grammar.provenance
494:        payload["notes"] = grammar.notes
1083:        without ever presenting a fallback region as cited grammar."""
1085:        from autofit.grammar import MaterialClass
1104:        Opt-in grammar-driven peak finding (spec §5A/§8).
"""Opt-in "fit the entire window" option (2026-07-13, Find Peaks UI
improvements round 3, unit 1).

Today, a CURATED region's grammar slots each carry a fixed,
literature-anchored ``be_window`` that hard-bounds where lmfit can place
that component's center — independent of how wide the user's ROI is (see
docs/autofit/PROGRESS.md's entry for this unit for the full trace). That's
the right default for a region like C 1s, where each of the 6 chemical
states (graphitic/aliphatic/C-O/C=O/OC=O/shake-up) has its own narrow,
chemically-anchored window — but it means an unusually-shifted extreme
component just outside the outermost window is unreachable no matter how
wide the user's ROI is.

``fit_full_window=True`` widens ONLY the outer envelope for a curated
multi-component model (the lowest-BE slot's lower bound and the
highest-BE slot's upper bound extend to the ROI edges; interior slots
keep their chemically-anchored windows exactly as today — never letting
one chemical state wander into another's territory) — and widens fully
to the ROI for a detection/structural-fallback slot (``region ==
"unassigned"``, e.g. Fe 2p or an out-of-grammar preseed), since those
already have no cited per-component window to preserve. Linked slots
(spin-orbit partners, satellites) are NEVER touched — their offset from
the parent is a cited physical constant, unrelated to ROI cropping.

Default is unchanged (``fit_full_window`` defaults to False everywhere)
so every existing call site's behavior is byte-for-byte identical unless
a caller opts in.
"""

import numpy as np
import pytest

from autofit.engine import (FittedComponent, _default_params_from_slots,
                            _full_window_bound_overrides, _proposal_blocked,
                            _slot_prefix, fit_candidate,
                            match_components_to_slots, run_stability_analysis)
from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot, LineShape


def _slot(role, region, be_window, **kw):
    return ComponentSlot(role=role, region=region, phase_id="p",
                         be_window=be_window, line_shape=LineShape.GAUSSIAN,
                         fwhm_range=(0.6, 2.2), **kw)


def _model(*slots):
    return CandidateModel(name="m", background=BackgroundType.LINEAR, slots=tuple(slots))


def _bounds(params, role):
    par = params[f"{_slot_prefix(role)}center"]
    return par.min, par.max


def _value(params, role):
    return params[f"{_slot_prefix(role)}center"].value


def test_default_leaves_curated_bounds_untouched():
    model = _model(_slot("graphitic", "C 1s", (284.0, 284.8)),
                   _slot("co", "C 1s", (285.8, 286.8)))
    x = np.arange(270.0, 300.0, 0.1)
    params = _default_params_from_slots(model, x=x, y_net=None)
    assert _bounds(params, "graphitic") == (284.0, 284.8)
    assert _bounds(params, "co") == (285.8, 286.8)


def test_fit_full_window_defaults_to_false():
    """Calling without the kwarg at all must behave identically to
    explicit False — no accidental behavior change for any existing
    caller that doesn't know about the new parameter."""
    model = _model(_slot("graphitic", "C 1s", (284.0, 284.8)))
    x = np.arange(270.0, 300.0, 0.1)
    implicit = _default_params_from_slots(model, x=x, y_net=None)
    explicit = _default_params_from_slots(model, x=x, y_net=None, fit_full_window=False)
    assert _bounds(implicit, "graphitic") == _bounds(explicit, "graphitic")


def test_full_window_widens_only_outer_envelope_for_multi_slot_curated_model():
    """The C 1s-shaped case: 3 chemically-anchored slots. Only the
    lowest-BE slot's LOWER bound and the highest-BE slot's UPPER bound
    move to the ROI edges — the interior slot (co) and the untouched
    sides of the outer slots keep their literature windows exactly, so
    a component can never wander into a neighboring chemical state's
    territory."""
    model = _model(
        _slot("graphitic", "C 1s", (284.0, 285.0)),
        _slot("co", "C 1s", (286.0, 287.0)),
        _slot("shake_up", "C 1s", (290.0, 292.0)),
    )
    x = np.arange(270.0, 300.0, 0.1)
    params = _default_params_from_slots(model, x=x, y_net=None, fit_full_window=True)
    lo, hi = _bounds(params, "graphitic")
    assert lo == pytest.approx(270.0) and hi == pytest.approx(285.0)
    assert _bounds(params, "co") == (286.0, 287.0)          # interior: untouched
    lo, hi = _bounds(params, "shake_up")
    assert lo == pytest.approx(290.0) and hi == pytest.approx(299.9, abs=0.05)


def test_full_window_never_narrows_or_inverts_a_bound_when_roi_is_shifted():
    """Regression (2026-07-13 Codex review, round 1 BLOCKER): a ROI that
    does NOT fully contain a slot's own literature window (e.g. the user
    set a narrower/shifted window than the region's full literature
    span) must leave that untouched side EXACTLY as it was — never
    assign a bare ROI edge that could sit on the wrong side of the
    slot's own bound and invert it (min > max), and never narrow an
    already-correct bound."""
    model = _model(
        _slot("graphitic", "C 1s", (284.0, 285.0)),
        _slot("co", "C 1s", (286.0, 287.0)),
        _slot("shake_up", "C 1s", (290.0, 292.0)),
    )
    # ROI's low edge (287.0) sits ABOVE the lowest slot's own upper bound
    # (285.0) — the pre-fix code assigned roi_lo=287.0 as graphitic's
    # lower bound unconditionally, producing (287.0, 285.0): min > max.
    x = np.arange(287.0, 300.0, 0.1)
    params = _default_params_from_slots(model, x=x, y_net=None, fit_full_window=True)
    lo, hi = _bounds(params, "graphitic")
    assert lo <= hi, (lo, hi)
    assert (lo, hi) == (284.0, 285.0)          # untouched: ROI doesn't reach it
    lo, hi = _bounds(params, "shake_up")
    assert lo == 290.0 and hi == pytest.approx(299.9, abs=0.05)  # this side still widens


def test_full_window_widens_a_single_curated_slot_on_both_sides():
"""Engine tests for spin-orbit doublet linkage (amplitude ratio + offset).

C 1s never exercises the area-ratio expression path; U 4f and Cl 2p will.
These tests pin it on a synthetic doublet before those modules land.
"""

import numpy as np
import pytest

from autofit.engine import fit_candidate, run_stability_analysis
from autofit.grammar import (
    BackgroundType,
    CandidateModel,
    ComponentSlot,
    LineShape,
)

SPLIT = 1.6
RATIO = 0.5


def _doublet_model(ratio=RATIO, ratio_range=None):
    p32 = ComponentSlot(
        role="main_p32", region="T 2p", phase_id="t",
        be_window=(196.5, 199.0), line_shape=LineShape.PSEUDO_VOIGT,
        fwhm_range=(0.6, 2.2),
    )
    p12 = ComponentSlot(
        role="main_p12", region="T 2p", phase_id="t",
        be_window=(198.0, 201.0), line_shape=LineShape.PSEUDO_VOIGT,
        fwhm_range=(0.6, 2.2),
        linked_to="main_p32", linked_offset_range=(SPLIT - 0.1, SPLIT + 0.1),
        area_ratio=ratio, area_ratio_range=ratio_range,
        fwhm_linked_to="s_main_p32_fwhm",
    )
    return CandidateModel(name="doublet", background=BackgroundType.LINEAR,
                          slots=(p32, p12))


def _doublet_spectrum(ratio=RATIO, seed=3):
    rng = np.random.default_rng(seed)
    x = np.arange(194.0, 204.0, 0.05)

    def g(c, a, w):
        return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)

    y = 200 + g(197.9, 8000, 1.1) + g(197.9 + SPLIT, 8000 * ratio, 1.1)
    return x, y + rng.normal(0, 12, len(x))


def test_fixed_ratio_doublet():
    x, y = _doublet_spectrum()
    w = 1 / np.sqrt(np.maximum(y, 1))
    model = _doublet_model()
    out = fit_candidate(x, y, w, model)
    assert out.converged
    by_role = {c.slot_role: c for c in out.components}
    p32, p12 = by_role["main_p32"], by_role["main_p12"]
    assert p32.position == pytest.approx(197.9, abs=0.03)
    assert p12.position - p32.position == pytest.approx(SPLIT, abs=0.1)
    # amplitude expression enforced exactly
    assert p12.amplitude == pytest.approx(p32.amplitude * RATIO, rel=1e-9)
    # linked fwhm shared
    assert p12.fwhm == pytest.approx(p32.fwhm, rel=1e-9)


def test_relaxed_ratio_doublet_recovers_true_ratio():
    true_ratio = 0.65
    x, y = _doublet_spectrum(ratio=true_ratio)
    w = 1 / np.sqrt(np.maximum(y, 1))
    model = _doublet_model(ratio=0.75, ratio_range=(0.55, 0.85))
    out = fit_candidate(x, y, w, model)
    assert out.converged
    by_role = {c.slot_role: c for c in out.components}
    fitted_ratio = by_role["main_p12"].amplitude / by_role["main_p32"].amplitude
    assert fitted_ratio == pytest.approx(true_ratio, abs=0.02)


def test_relaxed_ratio_at_bound_is_boundary_hit():
    # true ratio far below the allowed window → ratio pegs at min → counted
    x, y = _doublet_spectrum(ratio=0.2)
    w = 1 / np.sqrt(np.maximum(y, 1))
    model = _doublet_model(ratio=0.75, ratio_range=(0.55, 0.85))
    out = fit_candidate(x, y, w, model)
    assert out.converged
    assert any(h.startswith("main_p12:ratio@min") for h in out.boundary_hits), \
        out.boundary_hits


def test_doublet_stability_persistence():
    x, y = _doublet_spectrum()
    w = 1 / np.sqrt(np.maximum(y, 1))
    model = _doublet_model()
    primary = fit_candidate(x, y, w, model)
    stab = run_stability_analysis(x, y, w, model, primary,
                                  noise_floor=15.0, n_refits=6, rng_seed=0)
    assert stab.per_slot["main_p32"].persistence == 1.0
    assert stab.per_slot["main_p12"].persistence == 1.0
    assert stab.per_slot["main_p32"].position_mad < 0.02


def test_proposed_slot_is_phase_unassigned():
    """Codex Stage-2 blocker #2: proposals must not inherit region/phase."""
    from autofit.engine import ProposalSpec, _augmented_candidate

    base = _doublet_model()
    spec = ProposalSpec(
        role="proposed_peak_0", detection_windows=["proposal_x"],
        detection_energy=10.0, detection_ratio=6.0,
        center_init=202.0, fwhm_init=1.0, amplitude_init=500.0,
        line_shape=LineShape.PSEUDO_VOIGT,
    )
    aug = _augmented_candidate(base, spec)
    prop = aug.slot_by_role("proposed_peak_0")
    assert prop.region == "unassigned"
    assert prop.phase_id == "unassigned"


def test_absent_normalization_is_region_scoped():
    """Codex Stage-3 finding #2: a huge foreign main in a joint co-fit must
sed: tests/autofit/test_fwhm_cap.py: No such file or directory
    delta = aug_report.bic_adjusted - base_report.bic_adjusted
    pr.delta_bic_vs_base = delta
    if not (delta < -PROPOSAL_DELTABIC_THRESHOLD):
        pr.rejection_reason = (f"ΔBIC* = {delta:+.2f} does not beat "
                               f"-{PROPOSAL_DELTABIC_THRESHOLD:.1f} improvement threshold")
        return None, pr, "stability_rejected"

    lo, hi = roi
    pr.near_roi_endpoint = bool(
        abs(comp.position - lo) <= PROPOSAL_ENDPOINT_WARNING_BE
        or abs(comp.position - hi) <= PROPOSAL_ENDPOINT_WARNING_BE
    )
    pr.accepted = True
    aug_report.proposed_peaks = [pr]
    return aug_report, pr, "accepted"


def _cross_candidate_coincidences(
    attempts: list[tuple[str, ProposedPeakReport]],
) -> list[CoincidenceReport]:
    if not attempts:
        return []
    enriched = [{"base": b, "pr": pr,
                 "be": float(pr.fitted_center if pr.fitted_center is not None
                             else pr.proposed_center_init)}
                for b, pr in attempts]
    enriched.sort(key=lambda e: e["be"])
    clusters: list[list[dict]] = [[enriched[0]]]
    for e in enriched[1:]:
        if e["be"] - clusters[-1][-1]["be"] <= PROPOSAL_COINCIDENCE_BE:
            clusters[-1].append(e)
        else:
            clusters.append([e])
    out: list[CoincidenceReport] = []
    for c in clusters:
        bases = {e["base"] for e in c}
        if len(bases) < 2:
            continue
        per_base: dict[str, ProposedPeakReport] = {}
117:def _grammar(candidates, windows=None):
404:def bg_mismatch_case(seed: int) -> StressCase:
489:        bg_mismatch_case(seed=61 + o),

 succeeded in 40106ms:
......................                                                   [100%]
22 passed in 39.79s

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile,sys; tempfile.tempdir=\"/tmp\"; sys.modules[\"matplotlib\"]=None
import numpy as np
from autofit.engine import fit_candidate
from autofit.grammar import ComponentSlot,CandidateModel,BackgroundType,LineShape
import fitting
x=np.arange(280.,292.,.05); z=np.random.default_rng(20260927).standard_normal(x.size)
g=lambda c,a,w:a*np.exp(-4*np.log(2)*((x-c)/w)**2)
for a in [50,75,100,125,150,175,200]:
 y=1e4+g(284.5,a,1)+g(287.5,2e4,1.2)+100*z
 slots=tuple(ComponentSlot(role=r,region=\"C 1s\",phase_id=\"p\",be_window=b,line_shape=LineShape.GAUSSIAN,fwhm_range=(.5,2.5)) for r,b in [(\"main\",(284,285)),(\"main_other\",(287,288))])
 out=fit_candidate(x,y,1/np.sqrt(y),CandidateModel(name=\"m\",background=BackgroundType.LINEAR,slots=slots)); lm=out.lmfit_result
 own=fitting._component_support(lm.data,lm.best_fit,lm.eval_components()[\"s_main_\"],lm.weights,3,lm.nvarys)
 print(a,out.converged,out.components[0].amplitude,out.components[0].support,own)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 1518ms:
50 True 195.19454991847863 {'f': 14.327129351475378, 'delta_chi2': 143.1181982927941, 'supported': True} {'f': 28.654258702950756, 'delta_chi2': 143.1181982927941, 'supported': True}
75 True 207.16085821237996 {'f': 16.189003508427913, 'delta_chi2': 161.01726499868704, 'supported': True} {'f': 32.378007016855825, 'delta_chi2': 161.01726499868704, 'supported': True}
100 True 219.09567876017414 {'f': 18.13077024425737, 'delta_chi2': 179.92029160087327, 'supported': True} {'f': 36.26154048851474, 'delta_chi2': 179.92029160087327, 'supported': True}
125 True 231.01736816479084 {'f': 20.140400850185017, 'delta_chi2': 199.82099467046436, 'supported': True} {'f': 40.280801700370034, 'delta_chi2': 199.82099467046436, 'supported': True}
150 True 242.9173531219738 {'f': 22.204717560308932, 'delta_chi2': 220.71001338278404, 'supported': True} {'f': 44.409435120617864, 'delta_chi2': 220.71001338278404, 'supported': True}
175 True 254.7987995229026 {'f': 24.31016282603155, 'delta_chi2': 242.57984571204253, 'supported': True} {'f': 48.6203256520631, 'delta_chi2': 242.57984571204253, 'supported': True}
200 True 266.6620651769654 {'f': 26.44291219207134, 'delta_chi2': 265.42314941890345, 'supported': True} {'f': 52.88582438414268, 'delta_chi2': 265.42314941890345, 'supported': True}

exec
/bin/zsh -lc "rg -n 'post.stability|best_outcome|_attempt_proposal' tests/autofit; sed -n '360,438p' tests/autofit/stress_cases.py; sed -n '1,150p' tests/autofit/test_proposal_width_cap.py; sed -n '170,210p' autofit/grammar.py; sed -n '2900,2945p' autofit/engine.py; sed -n '454,483p' app.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
tests/autofit/test_endpoint_avg_wiring.py:57:                        "_attempt_proposal", "_bound_fixed_refit", "_apply_decisive_override",
tests/autofit/test_preseed_dominants.py:312:    best_outcome — a stability-promoted center@min (spurious) must still
tests/autofit/test_preseed_dominants.py:329:    # a REAL augmented fit, promoted as a "deeper" best_outcome that carries a
tests/autofit/test_preseed_dominants.py:341:        best_outcome=promoted, best_basin_support=1, n_attempted=2)
tests/autofit/test_preseed_dominants.py:344:    _, pr, outcome = eng._attempt_proposal(
tests/autofit/test_preseed_dominants.py:351:    assert "post-stability" in (pr.rejection_reason or "")
tests/autofit/test_preseed_dominants.py:486:    aug_report, pr, outcome = eng._attempt_proposal(
    truth, and (d) keep the honesty surface intact (region-unassigned roles,
    human-review message).  Positions are synthetic-region scaffolds (SYN),
    not C 1s constants — nothing here encodes the real spectra's energies.
    (Grid extended below the dominant so its tail doesn't load the
    endpoint-anchored linear background.)
    """
    x = _grid(186.0, 205.0)
    truth = [
        {"center": 191.2, "fwhm": 1.3, "height": 40000.0},   # dominant, out-of-window
        {"center": 193.0, "fwhm": 1.7, "height": 9000.0},    # neighbor (ordinary width,
                                                             #   22.5% of max, below gate)
        {"center": 196.6, "fwhm": 1.5, "height": 5000.0},    # in-window ladder...
        {"center": 198.9, "fwhm": 1.7, "height": 8000.0},
        {"center": 201.6, "fwhm": 1.6, "height": 5500.0},
    ]
    sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
    y = _noisy(sig + _linear_bg(x), seed)
    # ordinary-width in-window slots (cap 2.0, mirroring real C 1s
    # contamination) so the whole recovered model has physical widths
    ladder = [
        _slot("main_a", (196.0, 197.2), fwhm=(0.6, 2.0)),
        _slot("comp_b", (198.2, 199.6), fwhm=(0.6, 2.0)),
        _slot("comp_c", (200.8, 202.4), fwhm=(0.6, 2.0)),
    ]
    cands = [
        _cand("L1_main", ladder[:1]),
        _cand("L2_main_b", ladder[:2]),
        _cand("L3_main_b_c", ladder[:3]),
    ]
    return StressCase(
        name="multi_env_low_be_dominant",
        regime="multi_env_low_be", expectation="recover",
        x=x, y=y, truth=truth, truth_n=5,
        grammar=_grammar(cands),
        ls_specs=_ls_specs(truth),
        true_candidates=("L3_main_b_c",),
        notes="dominant + neighbor below every window; ladder in-window — "
              "the F1 preseed + F2 iterative-proposal regression case "
              "(NOT in build_all_cases yet: battery regeneration is a "
              "follow-up; the always-on pin in test_stress_honesty.py "
              "covers it every run)",
    )


def bg_mismatch_case(seed: int) -> StressCase:
    x = _grid()
    truth = [{"center": 197.2, "fwhm": 1.2, "height": 9000.0},
             {"center": 198.9, "fwhm": 1.2, "height": 6300.0}]
    sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
    y = _noisy(sig + _shirley_like_bg(x, sig), seed)
    return StressCase(
        name="bg_shirley_truth_linear_fit",
        regime="bg_mismatch", expectation="honesty",
        x=x, y=y, truth=truth, truth_n=2,
        grammar=_grammar(_n_peak_ladder(197.2, 198.9, n_max=3)),  # LINEAR bg
        ls_specs=_ls_specs(truth),
        true_candidates=("P2",),
        bg="shirley_like",
        notes="integral background fit with a straight line — the mismatch "
              "must surface, not silently vanish",
    )


def bg_matched_control_case(seed: int) -> StressCase:
    """Control for the mismatch case: same truth, Shirley-candidate fits.
    The engine's iterative Shirley should absorb the integral background."""
    x = _grid()
    truth = [{"center": 197.2, "fwhm": 1.2, "height": 9000.0},
             {"center": 198.9, "fwhm": 1.2, "height": 6300.0}]
    sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
    y = _noisy(sig + _shirley_like_bg(x, sig), seed)
    cands = _n_peak_ladder(197.2, 198.9, n_max=3, bg=BackgroundType.SHIRLEY)
    return StressCase(
        name="bg_shirley_truth_shirley_fit",
        regime="bg_mismatch", expectation="recover",
        x=x, y=y, truth=truth, truth_n=2,
        grammar=_grammar(cands),
        ls_specs=_ls_specs(truth),
        true_candidates=("P2",),
sed: tests/autofit/test_proposal_width_cap.py: No such file or directory
    # breadth, or U 4f's unresolved 5f² multiplet manifold. None means the
    # slot's width is ordinary — no known-broad justification exists, so
    # autofit.engine._unphysical_width_flags must not exempt it, REGARDLESS
    # of how wide fwhm_range happens to be. Before this field existed,
    # fwhm_range's upper bound alone served double duty as both the
    # optimizer's search bound AND this semantic claim (declared_hi >
    # FWHM_MAX_ORDINARY_EV granted exemption automatically) — widening a
    # bound for an UNRELATED reason (numerical-stability headroom, a wider
    # calibration envelope) silently asserted "this is vouched-for physics"
    # as a side effect. A region module that just needs search headroom
    # without vouching for width MUST leave this None.
    broad_justification: Optional[str] = None

    def contains(self, be: float, fwhm: float, amplitude: float,
                 noise_floor: float = 0.0) -> bool:
        # Noise-floor unit (2026-09-27): occupancy is decided by the support F test on the
        # fit (engine._occupies); this geometric check keeps only the sign of
        # the amplitude. ``noise_floor`` is accepted and ignored (the engine
        # has no caller of this method).
        return (
            self.be_window[0] <= be <= self.be_window[1]
            and self.fwhm_range[0] <= fwhm <= self.fwhm_range[1]
            and amplitude > 0
        )


@dataclass(frozen=True)
class CandidateModel:
    """A candidate model M = (background, slots) with admissibility built in."""
    name: str
    background: BackgroundType
    slots: tuple[ComponentSlot, ...]
    # (name, min, max) free params referenced by fwhm_linked_to expressions
    shared_fwhm_params: tuple[tuple[str, float, float], ...] = ()

    @property
    def n_components(self) -> int:
        return len(self.slots)

    def slot_by_role(self, role: str) -> Optional[ComponentSlot]:
        for s in self.slots:
        if elapsed > TOTAL_ANALYSIS_TIMEOUT_SEC - CANDIDATE_TIMEOUT_SEC:
            analysis_truncated = True
            log.warning(
                "compare_models: sweep budget cannot fit another candidate "
                "(%.0fs elapsed of %.0fs) after %d/%d — remaining candidates "
                "skipped, returning best-so-far",
                elapsed, TOTAL_ANALYSIS_TIMEOUT_SEC, n_evaluated, len(candidates),
            )
            break
        n_evaluated += 1
        log.info("[%2d/%d] %s: primary fit", idx, len(candidates), model.name)
        _report_progress(progress_cb, "stabilizing", idx, len(candidates),
                         model.name)
        # Shared wall-clock budget for this candidate's primary fit + all its
        # stability refits (CANDIDATE_TIMEOUT_SEC) — see run_stability_analysis.
        candidate_deadline = time.perf_counter() + CANDIDATE_TIMEOUT_SEC
        # reuse the screen fit as this candidate's primary (no repeated work)
        primary = screen_fit.get(model.name) or fit_candidate(
            x, y, weights, model, fit_full_window=fit_full_window,
            endpoint_avg=endpoint_avg)
        if not primary.converged:
            non_converged.append((model, primary))
            continue

        stability = run_stability_analysis(
            x, y, weights, model, primary,
            noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
            deadline=candidate_deadline,
            fit_full_window=fit_full_window,
            endpoint_avg=endpoint_avg,
        )
        # Promote a deeper minimum found by the multi-start pass (see
        # ModelStability.best_outcome).
        if (stability.best_outcome is not None
                and stability.best_outcome.weighted_chi_sq
                < primary.weighted_chi_sq):
            primary = stability.best_outcome
        y_fit = (primary.lmfit_result.best_fit +
                 (primary.background if primary.background is not None else 0.0)
                 if primary.lmfit_result is not None else np.zeros_like(y))
        residuals = compute_residual_diagnostics(x, y, y_fit, noise_floor, diagnostic_windows)
        slot_areas = compute_slot_areas(model, primary, x)
        absent = _identify_absent_slots(
            model, stability, slot_areas, primary,
            persistence_threshold=absent_slot_persistence_threshold,
            area_fraction_threshold=absent_slot_area_fraction,
            "uses_conditional_or_unverified_constants": non_verified,
            "peaks": [],
            "confidence": {},
            "message": (
                "structure known, positions UNVERIFIED — detection "
                "found no fittable features in this window; supply a "
                "cited source (autofit.cited_values schema) and "
                "curated windows to enable grammar fitting for: "
                + ", ".join(grammar.structural_only)),
            "review_gate": {
                "reviewed_by": None,
                "note": "results are candidates + honesty flags, "
                        "not ground truth — a named human review is "
                        "required before export (spec §8)",
            },
        }

    payload = {
        "method": ctx.method_id,
        "success": bool(res.success),
        # Phase D: regions that resolved structure-only in a MIXED
        # request (deep + structural) are flagged here; their derived
        # structure rides in analysis.constants_provenance.
        "structural_only": list(grammar.structural_only) if grammar else [],
        "peaks": res.peaks,
        "confidence": res.confidence,
        "analysis": res.analysis,
        "diagnostics": res.diagnostics,
        "message": res.message,
        "review_gate": {

exec
/bin/zsh -lc "sed -n '285,365p' tests/autofit/test_preseed_dominants.py; sed -n '430,505p' tests/autofit/test_preseed_dominants.py; sed -n '1,90p' tests/autofit/test_preseed_dominants.py; sed -n '1,160p' autofit/confidence.py; sed -n '260,295p' autofit/methods/ic_model_comparison.py; sed -n '3100,3145p' autofit/engine.py; sed -n '1695,1745p' autofit/engine.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
    a spurious peg and must not reject the proposal (rejecting it regressed
    the two-narrow-peak F2 case to zero accepted proposals).  A SUBSTANTIVE
    peg (center at a window edge, fwhm@max, fwhm@min) IS surfaced."""
    from lmfit import Parameters
    from autofit.grammar import (CandidateModel, ComponentSlot, LineShape,
                                 BackgroundType)
    role = "proposed_peak_0"
    prefix = eng._slot_prefix(role)
    slot = ComponentSlot(role=role, region="unassigned", phase_id="unassigned",
                         be_window=(199., 201.), line_shape=LineShape.PSEUDO_VOIGT,
                         fwhm_range=(0.5, 2.0))
    model = CandidateModel(name="M", background=BackgroundType.LINEAR, slots=(slot,))
    p = Parameters()
    p.add(f"{prefix}center", value=200.0, min=199.0, max=201.0)      # interior
    p.add(f"{prefix}amplitude", value=5000.0, min=0.0, max=1e5)      # interior
    p.add(f"{prefix}fwhm", value=2.0, min=0.5, max=2.0)             # fwhm@max
    p.add(f"{prefix}gl_ratio", value=1.0, min=0.0, max=1.0)         # shape endpoint
    hits = eng._detect_boundary_hits(p, model)
    assert f"{role}:gl_ratio@max" not in hits      # valid pure-Lorentzian, excluded
    assert f"{role}:fwhm@max" in hits              # the tolerated width-cap peg
    p[f"{prefix}center"].set(value=199.0)          # drifted to the window edge
    assert f"{role}:center@min" in eng._detect_boundary_hits(p, model)  # substantive


def test_proposal_rejected_when_stability_promotes_spurious_center_peg(monkeypatch):
    """Codex fwhm-cap review, run B BLOCKER: the proposed-slot peg decision
    must be RE-EVALUATED after run_stability_analysis promotes a deeper
    best_outcome — a stability-promoted center@min (spurious) must still
    reject, even though the initial augmented fit was clean."""
    import dataclasses
    from autofit.methods.base import poisson_like_weights
    from stress_cases import isolated_missing_peak_case

    case = isolated_missing_peak_case(seed=71)
    x, y = case.x, case.y
    w = poisson_like_weights(y)
    res = eng.compare_models(x, y, w, case.grammar, n_refits=2, rng_seed=0,
                             enable_proposal_pass=False, enable_preseed=False)
    base = res.reports[0]
    y_fit = (base.primary_fit.lmfit_result.best_fit + base.primary_fit.background)
    spec = eng._detect_residual_proposals(
        x, y, y_fit, 1.0, base.model,
        fitted_components=base.primary_fit.components)[0]

    # a REAL augmented fit, promoted as a "deeper" best_outcome that carries a
    # spurious center@min peg (the detector reads outcome.boundary_hits)
    aug_model = eng._augmented_candidate(base.model, spec)
    bg = eng._compute_background(x, y, aug_model.background)
    init = eng._initial_params_for_augmented(aug_model, base.primary_fit, spec, x, y - bg)
    real = eng.fit_candidate(x, y, w, aug_model, initial_params=init)
    promoted = dataclasses.replace(
        real, weighted_chi_sq=0.0,                       # guarantees promotion
        boundary_hits=[f"{spec.role}:center@min"])       # stability-introduced peg

    fake_stab = eng.ModelStability(
        per_slot={}, orphan_rate=0.0, convergence_rate=1.0,
        best_outcome=promoted, best_basin_support=1, n_attempted=2)
    monkeypatch.setattr(eng, "run_stability_analysis", lambda *a, **k: fake_stab)

    _, pr, outcome = eng._attempt_proposal(
        x=x, y=y, weights=w, base_report=base, spec=spec,
        noise_floor=1.0, n_refits=2, rng_seed=0,
        absent_slot_area_fraction=0.02, absent_slot_persistence_threshold=0.7,
        diagnostic_windows=dict(case.grammar.diagnostic_windows),
        budget_remaining=1e6)
    assert outcome == "stability_rejected"
    assert "post-stability" in (pr.rejection_reason or "")
    assert any("center@min" in h for h in pr.boundary_hits)


# ── F2: iterative rounds add MULTIPLE missing peaks ────────────────────────

def test_iterative_proposals_add_two_missing_peaks():
    """Two discrete unmodeled peaks: round 1 accepts one, detection re-runs
    on the augmented residual, round 2 accepts the other (the old
    single-accept cap structurally could not do this — PROGRESS.md
    diagnosis, cause c).  Stage-2 note: with the recalibrated seeding both
    peaks would PRE-seed, so this pin isolates the F2 iteration machinery
    with enable_preseed=False (the designed escape hatch, same pattern as
    test_proposal_pass_fires_on_isolated_missing_peak)."""
    x = _grid(186.0, 206.0)
    x = _grid()
    truth = [{"center": 196.5, "fwhm": 1.2, "height": 9000.0},
             {"center": 201.5, "fwhm": 1.2, "height": 2500.0}]
    sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
    y = _noisy(sig + _linear_bg(x), 71)
    cands = [_cand("single_main", [_slot("main_a", (195.5, 197.5))])]
    grammar = _grammar(cands)
    res = get_method("ic_model_comparison").run(
        x, y, grammar=grammar,
        options={**IC_OPTS, "enable_preseed": False})
    assert not res.diagnostics["winner"].endswith("+prop")
    reasons = [p["rejection_reason"] for c in res.analysis["candidates"]
               for p in c.get("proposed_peaks", [])]
    assert reasons, "expected at least one attempted-then-rejected proposal"
    assert all("insufficient_budget" in (r or "") for r in reasons), reasons


def test_stability_not_started_without_budget_after_augmented_fit(monkeypatch):
    """Codex c1s-fix RE-CHECK (run B): the top budget guard alone did NOT
    close the overrun — an augmented fit that PASSES the top guard then
    consumes most of the budget must not let run_stability_analysis start
    an unbounded refit with only a few seconds left.  The pre-stability
    guard now fast-rejects when the DYNAMIC remaining budget is below the
    fit floor.  Deterministic via a fake clock: attempt_start = 1000 s,
    every later perf_counter reads 1013 s, so with budget_remaining=20 the
    post-fit remaining is 7 s < 15 s floor — stability must NOT run."""
    from autofit.methods.base import poisson_like_weights
    from stress_cases import isolated_missing_peak_case

    case = isolated_missing_peak_case(seed=71)
    x, y = case.x, case.y
    w = poisson_like_weights(y)
    model = case.grammar.candidates[0]
    # real base report (unpatched clock), proposal + preseed off
    res = eng.compare_models(x, y, w, case.grammar, n_refits=2, rng_seed=0,
                             enable_proposal_pass=False, enable_preseed=False)
    base_report = res.reports[0]
    y_fit = (base_report.primary_fit.lmfit_result.best_fit
             + base_report.primary_fit.background)
    specs = eng._detect_residual_proposals(
        x, y, y_fit, 1.0, model,
        fitted_components=base_report.primary_fit.components)
    assert specs, "expected a residual proposal at the unmodeled peak"

    calls = {"n": 0}

    def fake_pc():
        calls["n"] += 1
        return 1000.0 + (0.0 if calls["n"] == 1 else 13.0)

    def boom(*a, **k):
        raise AssertionError("run_stability_analysis started without budget")

    monkeypatch.setattr(eng.time, "perf_counter", fake_pc)
    monkeypatch.setattr(eng, "run_stability_analysis", boom)

    aug_report, pr, outcome = eng._attempt_proposal(
        x=x, y=y, weights=w, base_report=base_report, spec=specs[0],
        noise_floor=1.0, n_refits=4, rng_seed=0,
        absent_slot_area_fraction=0.02, absent_slot_persistence_threshold=0.7,
        diagnostic_windows=dict(case.grammar.diagnostic_windows),
        budget_remaining=20.0)          # passes the 15 s TOP guard...
    assert outcome == "fast_rejected"   # ...but post-fit remaining 7 s < 15
    assert aug_report is None
    assert "insufficient_budget before stability" in (pr.rejection_reason or "")


# ── F3: two-phase sweep ────────────────────────────────────────────────────

def _many_candidate_grammar(x, y):
    """SCREEN_TOP_K+2 candidates: a ladder of window variants, several of
    which cannot express the data (wrong windows)."""
    good = [
        _cand("G1", [_slot("main_a", (195.5, 197.5))]),
        _cand("G2", [_slot("main_a", (195.5, 197.5)),
                     _slot("comp_b", (198.5, 200.5))]),
"""
Units F1 (pre-fit out-of-grammar dominant seeding), F2 (iterative proposal
rounds), F3 (two-phase screen→stabilize sweep) — always-on pins.

Motivating evidence: PROGRESS.md "Real multi-environment C 1s — MEASURED
DIAGNOSIS (2026-07-07)".  The real spectra stay local-only (privacy rail);
`multi_env_low_be_dominant_case` in stress_cases.py is the committed
ground-truth stand-in for the class.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from stress_cases import (  # noqa: E402
    STEP,
    _cand,
    _grammar,
    _grid,
    _linear_bg,
    _noisy,
    _pv,
    _slot,
    multi_env_low_be_dominant_case,
)

import autofit.engine as eng  # noqa: E402
from autofit.methods import get_method  # noqa: E402

ETA = 0.30
IC_OPTS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
           "enable_proposal_pass": True}


def _ic(case, **extra):
    return get_method("ic_model_comparison").run(
        case.x, case.y, grammar=case.grammar, options={**IC_OPTS, **extra})


def _covered_spectrum(seed=11):
    """Both features inside grammar windows — detection must return []."""
    x = _grid()
    truth = [{"center": 196.5, "fwhm": 1.2, "height": 9000.0},
             {"center": 199.5, "fwhm": 1.4, "height": 4000.0}]
    sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
    y = _noisy(sig + _linear_bg(x), seed)
    cands = [_cand("P2", [_slot("main_a", (195.5, 197.5)),
                          _slot("comp_b", (198.5, 200.5))])]
    return x, y, _grammar(cands)


# ── F1: detection ──────────────────────────────────────────────────────────

def test_no_preseed_on_covered_spectrum():
    """Grammar-covered spectra must run byte-identically: zero detections,
    no '+preseed' candidates, empty preseeded_features."""
    x, y, grammar = _covered_spectrum()
    bg = eng._compute_background(x, y, grammar.candidates[0].background)
    specs = eng.detect_out_of_grammar_dominants(
        x, y, bg, grammar.candidates, dict(grammar.diagnostic_windows))
    assert specs == []

    case_like = type("C", (), {"x": x, "y": y, "grammar": grammar})
    res = _ic(case_like)
    assert res.analysis["preseeded_features"] == []
    assert not any(c["name"].endswith("+preseed")
                   for c in res.analysis["candidates"])


def test_detects_out_of_window_dominant_and_gates_weak_bump():
    """A dominant peak below every window is detected at its position; a
    weak out-of-window bump (below the fraction-of-max gate) is NOT —
    that regime stays the proposal pass's job."""
    x = _grid(186.0, 205.0)
    sig = (_pv(x, 30000.0, 191.0, 1.3, ETA)          # dominant, out-of-window
           + _pv(x, 30000.0 * 0.10, 188.5, 1.2, ETA)  # weak bump, below gate
           + _pv(x, 9000.0, 196.5, 1.2, ETA))         # in-window main
    y = _noisy(sig + _linear_bg(x), 7)
    cands = [_cand("P1", [_slot("main_a", (195.5, 197.5))])]
    grammar = _grammar(cands)
    bg = eng._compute_background(x, y, grammar.candidates[0].background)
    specs = eng.detect_out_of_grammar_dominants(
        x, y, bg, grammar.candidates, dict(grammar.diagnostic_windows))
    assert len(specs) == 1
    assert specs[0].center_init == pytest.approx(191.0, abs=0.3)
    assert specs[0].role == "preseed_dominant_0"
"""
Per-peak, per-parameter confidence vectors (spec v2.1 §5).

Rules encoded:

- **Typed statistical σ** — ``uncertainty_kind ∈ {covariance, stability_mad,
  unavailable}``; kinds are NEVER mixed in one numeric field.  ``covariance``
  = lmfit stderr; ``stability_mad`` = raw median-absolute-deviations from
  the perturbation refits (reported as MADs, not silently rescaled to σ);
  ``unavailable`` otherwise.
- **Stability/persistence** — refit survival fraction + parameter MADs.
- **Detectability** — amplitude vs the noise floor; the ``5×`` floor is a
  TUNABLE validation parameter (UNVERIFIED), not a constant.
- **Identifiability** — boundary hits + max parameter correlation.
- ``reference_sensitivity_range`` is a SEPARATE field (never combined with
  σ_stat, no quadrature).  A single-spectrum fit cannot populate it — it
  needs the corrected-BE spread across admissible references for the phase —
  so it is ``None`` here with an explanatory kind, filled by the (later)
  charge-reference machinery.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from fitting import SUPPORT_MIN_F as _SUPPORT_MIN_F  # the server's support threshold: one definition

from .engine import ModelReport, _slot_prefix, _width_param

# No longer read (noise-floor unit, 2026-09-27): detectability is the support
# F test (see build_confidence_vector). Kept so the keyword stays accepted.
DETECTION_FLOOR_MULTIPLE = 5.0


def _sigma_stat_for_slot(report: ModelReport, role: str) -> dict:
    """σ_stat for center/width/amplitude with an explicit kind."""
    result = report.primary_fit.lmfit_result
    slot = report.model.slot_by_role(role)
    wname = _width_param(slot.line_shape) if slot is not None else "fwhm"
    prefix = _slot_prefix(role)

    if result is not None:
        stderr = {}
        for short, pname in (("center", f"{prefix}center"),
                             ("fwhm", f"{prefix}{wname}"),
                             ("amplitude", f"{prefix}amplitude")):
            par = result.params.get(pname)
            stderr[short] = (float(par.stderr)
                             if par is not None and par.stderr is not None else None)
        if any(v is not None for v in stderr.values()):
            return {"uncertainty_kind": "covariance", "values": stderr}

    sstab = report.stability.per_slot.get(role)
    if sstab is not None and sstab.position_mad is not None:
        return {
            "uncertainty_kind": "stability_mad",
            # raw MADs from the perturbation refits — NOT rescaled to a
            # Gaussian σ; consumers must not compare across kinds.
            "values": {"center": sstab.position_mad,
                       "fwhm": sstab.fwhm_mad,
                       "amplitude": sstab.amplitude_mad},
        }
    return {"uncertainty_kind": "unavailable", "values": None}


def _max_correlation(report: ModelReport, role: str) -> Optional[float]:
    """Max |correlation| between this slot's varying params and any other."""
    result = report.primary_fit.lmfit_result
    if result is None or result.covar is None:
        return None
    var_names = list(result.var_names)
    covar = np.asarray(result.covar, dtype=float)
    d = np.sqrt(np.diag(covar))
    with np.errstate(invalid="ignore", divide="ignore"):
        corr = covar / np.outer(d, d)
    prefix = _slot_prefix(role)
    idx = [i for i, n in enumerate(var_names) if n.startswith(prefix)]
    others = [i for i in range(len(var_names)) if i not in idx]
    if not idx or not others:
        return None
    sub = np.abs(corr[np.ix_(idx, others)])
    sub = sub[np.isfinite(sub)]
    return float(np.max(sub)) if sub.size else None


def build_confidence_vector(
    report: ModelReport,
    role: str,
    noise_floor: float,
    detection_floor_multiple: float = DETECTION_FLOOR_MULTIPLE,
) -> dict:
    """The per-peak `_confidence` payload for one grammar slot.

    ``noise_floor`` / ``detection_floor_multiple`` are accepted and not read
    (the Poisson variance floor lives in the fit's weights, not here)."""
    sstab = report.stability.per_slot.get(role)
    comp = next((c for c in report.primary_fit.components if c.slot_role == role), None)
    boundary = [h for h in report.primary_fit.boundary_hits
                if h.startswith(f"{role}:")]

    amplitude = float(comp.amplitude) if comp is not None else None
    # Noise-floor unit (2026-09-27): detectability is the support F test on the fit
    # (fitting._component_support, the server's statistic), not multiples of an
    # absolute 1-count floor. above_floor = supported (F >= SUPPORT_MIN_F);
    # present_but_poorly_constrained = the fit gains from it but not
    # significantly; not_confidently_detected = removing it costs nothing.
    support = getattr(comp, "support", None) if comp is not None else None
    if amplitude is None:
        detect_status = "not_fitted"
    elif support is None:
        detect_status = "above_floor" if amplitude > 0 else "not_confidently_detected"
    elif support.get("supported"):
        detect_status = "above_floor"
    elif (support.get("delta_chi2") or 0.0) > 0:
        detect_status = "present_but_poorly_constrained"
    else:
        detect_status = "not_confidently_detected"

    return {
        "sigma_stat": _sigma_stat_for_slot(report, role),
        # Systematic reference envelope — SEPARATE from σ_stat by design
        # (spec §4 M2: no quadrature). Not derivable from a single fit.
        "reference_sensitivity_range": {
            "kind": "unavailable_single_fit",
            "range_ev": None,
        },
        "stability": None if sstab is None else {
            "persistence": sstab.persistence,
            "position_mad": sstab.position_mad,
            "fwhm_mad": sstab.fwhm_mad,
            "amplitude_mad": sstab.amplitude_mad,
        },
        "detectability": {
            "amplitude": amplitude,
            "basis": "support_f_test",       # fitting._component_support, F >= SUPPORT_MIN_F
            "support_f": (support or {}).get("f"),
            "support_min_f": _SUPPORT_MIN_F,
            "status": detect_status,
        },
        "identifiability": {
            "boundary_hits": boundary,
            "max_cross_correlation": _max_correlation(report, role),
        },
    }
            # the labeled-heuristic BIC*'s honest companions (BIC/IC math
            # review): full-k raw BIC, the weighted-χ² criterion the fits
            # are actually consistent with, and the effective sample size
            # under residual autocorrelation
            "bic_raw": float(r.bic_raw),
            "bic_weighted": float(r.bic_weighted),
            "n_eff_lag1": (float(r.n_eff_lag1)
                           if r.n_eff_lag1 is not None else None),
            "survived": name in survivor_rank,
            "rank": survivor_rank.get(name),
            "filter_reason": filtered_reason.get(name),
            "augmented_from": r.augmented_from,
            "boundary_fixed_params": list(r.boundary_fixed_params),
            "absent_slots": [
                {"role": a.role, "persistence": float(a.persistence),
                 "area_fraction": float(a.area_fraction)} for a in r.absent_slots
            ],
            "proposed_peaks": [
                {"role": p.role, "accepted": bool(p.accepted),
                 "fitted_center": p.fitted_center,
                 "fitted_fwhm": p.fitted_fwhm,
                 "width_capped": bool(p.width_capped),
                 "rejection_reason": p.rejection_reason,
                 "near_roi_endpoint": bool(p.near_roi_endpoint)}
                for p in r.proposed_peaks
            ],
            "residual_flags": r.residuals.flagged_windows,
            "unphysical_widths": list(r.plausibility.unphysical_widths),
            "autocorr_flag": bool(r.residuals.autocorr_flag),
            "min_active_persistence": float(r.active_min_persistence),
            "boundary_hits": r.plausibility.boundary_hits,
            # full plausibility surface (Codex Stage-2 re-review finding #3 —
            # the orphan flag was recorded but dropped from the payload)
            "unphysical_widths": r.plausibility.unphysical_widths,
            "orphan_peaks": bool(r.plausibility.orphan_peaks),
            # best-minimum honesty (re-review finding #4): how many of the
    # at ΔBIC* +74…+944): a FILTERED candidate whose BIC* decisively beats
    # the emitted winner must be visible at the RESULT level, not only in
    # the candidate table.  Purely additive: ranking, filtering, and the
    # promotion rules are unchanged — this only reports what they buried.
    if result.survivors:
        win_bic = result.survivors[0].bic_adjusted
        # promotion LINEAGE, not just names: a decisive-override winner is
        # renamed "X+bfix" while its free original "X" stays in
        # filtered_out — flagging the original as "buried" would name the
        # very candidate that was promoted (Codex analyze review blocker)
        survivor_names = set()
        for r in result.survivors:
            survivor_names.add(r.model.name)
            if r.model.name.endswith("+bfix"):
                survivor_names.add(r.model.name[:-len("+bfix")])
            if r.augmented_from:
                survivor_names.add(r.augmented_from)
        dominant = None
        for rep, why in result.filtered_out:
            if rep.model.name in survivor_names:
                continue        # promoted members / their free originals
            if win_bic - rep.bic_adjusted > CONDITIONAL_OVERRIDE_DELTA_BIC:
                if dominant is None or rep.bic_adjusted < dominant[0].bic_adjusted:
                    dominant = (rep, why)
        if dominant is not None:
            rep, why = dominant
            result.filtered_dominant_alternative = {
                "name": rep.model.name,
                "bic_star": float(rep.bic_adjusted),
                "delta_bic_vs_winner": float(win_bic - rep.bic_adjusted),
                "filter_reason": why,
            }
    result.weighted_ic_disagreement = _weighted_ic_disagreement(
        result.survivors)
    return result


def _weighted_ic_disagreement(survivors: "list[ModelReport]") -> Optional[dict]:
    """Result-level flag when the weighted-χ² BIC (consistent with the fit
    weights) tops a different survivor than the ranking's RSS-form BIC*."""
    if len(survivors) < 2:
        return None
    weighted_top = min(survivors, key=lambda r: r.bic_weighted)
    if weighted_top.model.name == survivors[0].model.name:
        return None
    return {
    #   'decisive_override'  — clean survivors exist but a bound-fixed refit
    #                          of a boundary-limited candidate dominates them
    #                          (see CONDITIONAL_OVERRIDE_DELTA_BIC); clean
    #                          survivors remain as ranked alternatives.
    # Never silent (spec stance: best-evidenced proposal + honest
    # uncertainty, not a dead end).
    conditional: bool = False
    conditional_reason: Optional[str] = None
    # The ambiguity threshold ACTUALLY used for ambiguous_pairs — consumers
    # (criteria panel) must reuse it so the payload can never disagree with
    # the ranking (Codex Stage-2 re-review finding #1).
    bic_ambiguity_threshold: float = DEFAULT_BIC_AMBIGUITY
    # A filtered candidate whose BIC* beats the winner's by more than the
    # decisive threshold — {name, bic_star, delta_bic_vs_winner,
    # filter_reason} or None.  Stress-suite finding 0: evidence burial must
    # be machine-visible at the result level.
    filtered_dominant_alternative: Optional[dict] = None
    # The weighted-χ² criterion (consistent with the fit weights) prefers a
    # DIFFERENT survivor than the ranking's RSS-form BIC* — {rss_bic_top,
    # weighted_bic_top, note} or None (BIC/IC math review blocker:
    # selection must not silently rest on a likelihood the fits reject).
    weighted_ic_disagreement: Optional[dict] = None
    # Set when the sweep hit TOTAL_ANALYSIS_TIMEOUT_SEC and stopped before
    # evaluating every candidate in the grammar. The candidates evaluated so
    # far are still ranked/reported normally (best-so-far) — this only flags
    # that the comparison is partial, so a slow/pathological spectrum
    # returns an honest incomplete result instead of a request timeout.
    analysis_truncated: bool = False
    n_candidates_evaluated: int = 0
    n_candidates_total: int = 0
    # Pre-fit out-of-grammar dominant seeding (unit F1): the detected
    # features every candidate was augmented with, incl. the gate values
    # (UNVERIFIED tunables) — empty when detection found nothing, in which
    # case the candidate set ran unmodified.
    preseeded_features: list[dict] = field(default_factory=list)
    # Two-phase sweep record (unit F3) — None when the classic single-phase
    # path ran (candidate set ≤ SCREEN_TOP_K).  Otherwise every candidate's
    # screen outcome: {name, converged, bic, selected} — screened-out
    # candidates are visible here and can never be survivors.
    screen: Optional[list[dict]] = None
    # Candidate-generation layer (autofit.candidates): the OVERCOMPLETE,
    # provenance-tagged detection pool payload — every feature any source
    # (local_max / curvature_shoulder / residual_gap / grammar) proposed,
    # with per-feature gate outcomes and seeding decisions.  None when the
    # layer did not run (enable_preseed=False or no candidates).
    candidate_pool: Optional[dict] = None


def rank_and_filter(
    reports: list[ModelReport],
    persistence_threshold: float = DEFAULT_PERSISTENCE_THRESHOLD,

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile,sys
tempfile.tempdir=\"/tmp\"
sys.modules[\"matplotlib\"]=None
import numpy as np
from autofit.engine import fit_candidate, _slot_prefix
from autofit.grammar import ComponentSlot,CandidateModel,BackgroundType,LineShape
import fitting
x=np.arange(280.,292.,.05)
g=lambda c,a,w:a*np.exp(-4*np.log(2)*((x-c)/w)**2)
for seed in range(1,10):
 z=np.random.default_rng(seed).standard_normal(x.size)
 for a in [50,100,150,200,250]:
  y=1e4+g(284.5,a,1)+g(287.5,2e4,1.2)+100*z
  slots=tuple(ComponentSlot(role=r,region=\"C 1s\",phase_id=\"p\",be_window=b,line_shape=LineShape.GAUSSIAN,fwhm_range=(.5,2.5)) for r,b in [(\"main\",(284,285)),(\"main_other\",(287,288))])
  out=fit_candidate(x,y,1/np.sqrt(y),CandidateModel(name=\"m\",background=BackgroundType.LINEAR,slots=slots)); lm=out.lmfit_result
  own=fitting._component_support(lm.data,lm.best_fit,lm.eval_components()[\"s_main_\"],lm.weights,3,lm.nvarys)
  if own[\"supported\"] and not out.components[0].support[\"supported\"]:
   print(\"PREFIX COLLISION\",seed,a,\"fit_amp\",out.components[0].amplitude,\"engine\",out.components[0].support,\"correct\",own,\"nfree\",lm.nvarys,flush=True)
   raise SystemExit
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 1477ms:
PREFIX COLLISION 1 150 fit_amp 160.12596767906533 engine {'f': 7.876318396960685, 'delta_chi2': 44.932300439567825, 'supported': False} correct {'f': 15.75263679392137, 'delta_chi2': 44.932300439567825, 'supported': True} nfree 6

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile,sys; tempfile.tempdir=\"/tmp\"; sys.modules[\"matplotlib\"]=None; import pytest; raise SystemExit(pytest.main([\"-p\",\"no:cacheprovider\",\"--capture=sys\",\"tests/autofit/test_engine_doublet.py\",\"tests/autofit/test_fit_full_window_option.py\",\"tests/autofit/test_methods_seam.py\",\"-q\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 17184ms:
.........................                                                [100%]
25 passed in 16.83s

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile,sys
tempfile.tempdir=\"/tmp\"; sys.modules[\"matplotlib\"]=None
import numpy as np
import autofit.engine as e
from autofit.grammar import *
x=np.arange(280.,292.,.1)
g=lambda c,a,w:a*np.exp(-4*np.log(2)*((x-c)/w)**2)
slots=tuple(ComponentSlot(role=r,region=\"C 1s\",phase_id=\"p\",be_window=b,line_shape=LineShape.GAUSSIAN,fwhm_range=(.5,2.5)) for r,b in [(\"root\",(284.,285.)),(\"shoulder\",(284.7,286.5))])
model=CandidateModel(name=\"m\",background=BackgroundType.LINEAR,slots=slots)
for seed in range(25):
 for amp in [150,350,700]:
  truth=1e4+g(284.5,2e4,1.5)+g(285.5,amp,1.)
  y=truth+np.sqrt(truth)*np.random.default_rng(seed).standard_normal(len(x))
  w=1/np.sqrt(y)
  pri=e.fit_candidate(x,y,w,model)
  stab=e.run_stability_analysis(x,y,w,model,pri,1.,n_refits=4,rng_seed=0)
  best=stab.best_outcome
  if best and best.weighted_chi_sq<pri.weighted_chi_sq and not best.components[1].support[\"supported\"] and stab.per_slot[\"shoulder\"].persistence>=.7:
   print(\"REAL PROMOTION\",seed,amp,\"persistence\",stab.per_slot[\"shoulder\"].persistence,\"initial\",pri.components[1],\"promoted\",best.components[1],\"chi\",pri.weighted_chi_sq,best.weighted_chi_sq,\"boundary\",best.boundary_hits,flush=True)
   raise SystemExit
print(\"no real promotion found\")
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 7136ms:
no real promotion found

exec
/bin/zsh -lc "sed -n '1,125p' autofit/grammar.py; rg -n 'role=|role=' autofit | head -70; sed -n '390,410p' app.py; sed -n '440,520p' autofit/candidates.py; rg -n 'PROPOSAL_PERSISTENCE_THRESHOLD' autofit/engine.py; nl -ba autofit/engine.py | sed -n '665,737p'; nl -ba docs/superpowers/plans/2026-09-27-occupancy-f-test.md | sed -n '130,180p'; nl -ba tests/autofit/test_occupancy_support.py | sed -n '76,86p'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
"""
Composable grammar for the autofit engine (spec v2.1 §2).

``resolve(phases, regions, ...)`` → :class:`CandidateGrammar`.

Three layers:

- **Layer A** — material class (per phase): lineshape family admissibility,
  charge strategy, reference.
- **Layer B** — region/element module (``autofit.regions``): doublet
  Δso/ratio, BE windows, allowed lineshapes, satellites, core-hole width.
- **Layer C** — oxidation-state override (multiplet fingerprint, BE shift).
  Seam only in Stage 2 — region modules may accept it, none require it.

Multi-phase model (v2 B1 fix): a ``phases`` list, never a pairwise
``mixed{analyte, matrix}``.  Every :class:`ComponentSlot` carries a
``phase_id``; when the same region is contributed by more than one phase the
caller MUST disambiguate with ``target_phases`` (Codex precondition 2 — a
region is not a unique key).

Multi-region co-fit ([Skye]): ``regions`` is multi-valued; the grammars of
all requested regions are composed into joint candidates fit together in the
shared window (e.g. U 4f + N 1s overlap).
"""

from __future__ import annotations

import itertools
import re
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Optional

from .fit_physics import provenance_entries as _fit_physics_provenance

__all__ = [
    "LineShape", "BackgroundType", "MaterialClass", "Phase", "ComponentSlot",
    "CandidateModel", "CandidateGrammar", "PhaseAmbiguityError",
    "UnknownRegionError", "resolve", "BACKEND_SHAPE",
]


class LineShape(Enum):
    GAUSSIAN = "gaussian"
    LORENTZIAN = "lorentzian"
    PSEUDO_VOIGT = "pseudo_voigt"    # backend pseudo_voigt_gl
    ASYM_GL = "asym_gl"              # backend asymmetric_gl
    DS = "doniach_sunjic"
    DS_G = "ds_g"                    # DS core ⊗ Gaussian (fitalg's "LA_ASYMMETRIC")
    LACX = "la_casaxps"              # true CasaXPS LA(α, β, m)


# LineShape → fitting.py _SHAPE_FUNCS key
BACKEND_SHAPE: dict[LineShape, str] = {
    LineShape.GAUSSIAN: "gaussian",
    LineShape.LORENTZIAN: "lorentzian",
    LineShape.PSEUDO_VOIGT: "pseudo_voigt_gl",
    LineShape.ASYM_GL: "asymmetric_gl",
    LineShape.DS: "doniach_sunjic",
    LineShape.DS_G: "ds_g",
    LineShape.LACX: "la_casaxps",
}

# Shapes whose asymmetric tail encodes physics (metallic screening or an
# unresolvable multiplet envelope) — admissible only where Layer A allows.
ASYMMETRIC_SHAPES = frozenset({LineShape.ASYM_GL, LineShape.DS, LineShape.DS_G, LineShape.LACX})


class BackgroundType(Enum):
    SHIRLEY = "shirley"
    SMART = "smart"
    SMART_EXP = "smart_exp"      # Avantage-style constrained Shirley
    LINEAR = "linear"
    TOUGAARD = "tougaard"


class MaterialClass(Enum):
    CONDUCTOR = "conductor"
    SEMICONDUCTOR = "semiconductor"
    INSULATOR = "insulator"
    # Analyte embedded in a different matrix (2026-07-20): differential
    # charging between analyte and matrix is possible, which voids the
    # single-species-homogeneity assumption behind some region modules'
    # width ceilings. MIXED only RELAXES existing constraints (region
    # modules opt in — see autofit.regions.c1s) — it asserts no new
    # position or width value, and it must never reach charge-correction
    # (that stays byte-identical to every other material class; see
    # tests/test_api_analyze.py::test_material_class_does_not_affect_charge_correction).
    # Appended LAST so the default dropdown/first-enum-member selection
    # (conductor) is unchanged.
    MIXED = "mixed"


@dataclass(frozen=True)
class Phase:
    """
    One physical phase of the sample (spec §2).  ``regions`` declares which
    core-level regions this phase's material contributes signal to — the
    resolver uses it to detect region↔phase ambiguity.
    """
    id: str
    material_class: MaterialClass
    regions: tuple[str, ...]
    role: str = "analyte"                    # analyte | matrix | phase
    material: Optional[str] = None           # e.g. "graphite" — region-module hint
    # Per-phase charge reference (Layer A default when None):
    #   conductor → internal (graphite C 1s 284.4 eV / Fermi edge)
    #   insulator → adventitious C 1s 284.8 eV (CONDITIONAL, Biesinger 2022)
    #   semiconductor → internal-if-present else adventitious
    charge_reference: Optional[dict] = None
    shift_model: str = "rigid"               # per-phase rigid shift (Stage 2)


@dataclass(frozen=True)
class ComponentSlot:
    """
    A component defined by grammar role — the stable identity used for
    cross-refit matching (never optimizer index).  Ported from fitalg with
    two generalizations: ``phase_id``/``region`` tagging, and generic
    per-parameter fixes/bounds instead of LA-specific fields.
    """
    role: str
    region: str
    phase_id: str
    be_window: tuple[float, float]
autofit/candidates.py:464:            role=f"detected_peak_{i}",
autofit/candidates.py:722:            role=role,
autofit/candidates.py:762:            seeded_role=e.get("seeded_role"),
autofit/grammar.py:622:        role=rename[s.role],
autofit/engine.py:758:            slot_role=slot.role, position=center, fwhm=fwhm,
autofit/engine.py:1174:                slot_role="unmatched", position=comp.position, fwhm=comp.fwhm,
autofit/engine.py:1192:            slot_role=best_slot.role, position=comp.position, fwhm=comp.fwhm,
autofit/engine.py:1355:            role=role,
autofit/engine.py:1474:            role=slot.role, persistence=sstab.persistence, fitted_area=area,
autofit/engine.py:1970:            role="", center_init=center, fwhm_init=fwhm_init,
autofit/engine.py:1986:    return [PreseedSpec(role=f"preseed_dominant_{i}", center_init=s.center_init,
autofit/engine.py:2003:            role=s.role,
autofit/engine.py:2173:            role=f"proposed_peak_{idx}",
autofit/engine.py:2212:        role=spec.role,
autofit/engine.py:2278:        role=spec.role, detection_windows=list(spec.detection_windows),
autofit/engine.py:2763:                    role=s.role, center_init=s.center_be,
autofit/regions/cl2p.py:144:                role="main_cl2p32", region=REGION, phase_id=pid,
autofit/regions/cl2p.py:155:                    role="main_cl2p12", region=REGION, phase_id=pid,
autofit/regions/cl2p.py:167:                role="main_cl2p12", region=REGION, phase_id=pid,
autofit/regions/u4f.py:198:                role=role, region=REGION, phase_id=pid,
autofit/regions/c1s.py:310:                role=role, region=REGION, phase_id=pid,
autofit/regions/b1s.py:93:                role=role, region=REGION, phase_id=pid,
autofit/regions/n1s.py:77:            role="main_n1s", region=REGION, phase_id=pid,
autofit/regions/n1s.py:83:            role="main_n1s", region=REGION, phase_id=pid,
                            "provide 'peak_specs'")

    phase_kwargs = body.get("phase")
    phase_kwargs = {} if phase_kwargs is None else phase_kwargs
    if not isinstance(phase_kwargs, dict):
        raise _AnalyzeError("'phase' must be an object")
    grammar = None
    if method_id != "least_squares":
        phase = Phase(id=str(phase_kwargs.get("id", "sample")),
                      material_class=mclass,
                      regions=tuple(regions),
                      material=phase_kwargs.get("material"))
        try:
            # Phase D: regions without a deep module degrade to derived
            # structure instead of erroring (unparseable labels still 400)
            grammar = resolve(
                [phase], regions if len(regions) > 1 else regions[0],
                allow_structural_fallback=True)
        except (UnknownRegionError, PhaseAmbiguityError, ValueError) as exc:
            raise _AnalyzeError(str(exc))

               for f in ranked[DETECTION_MODEL_MAX_SLOTS:]]
    feats.sort(key=lambda f: f.center_be)
    centers = [f.center_be for f in feats]
    slots = []
    for i, f in enumerate(feats):
        width = float(f.fwhm_est) if f.fwhm_est else max(4.0 * step_ev, 0.5)
        # SPACING-AWARE center bounds: a slot window must never enclose a
        # neighboring slot's center — a merged close pair reads its
        # fwhm_est at the envelope scale (measured: dominant est 2.4 eV vs
        # true 0.7 with a neighbor 0.9 eV away → window swallowed the
        # neighbor → label-switching degeneracy, screens burned all nfev).
        # 0.45×gap keeps adjacent windows disjoint whatever the widths.
        gaps = []
        if i > 0:
            gaps.append(f.center_be - centers[i - 1])
        if i < len(centers) - 1:
            gaps.append(centers[i + 1] - f.center_be)
        half_win = max(DETECTION_SLOT_WINDOW_FRACTION * width, 3.0 * step_ev)
        if gaps:
            half_win = min(half_win, 0.45 * min(gaps))
        half_win = max(half_win, 2.0 * step_ev)     # never below grid sanity
        lo_w = max(DETECTION_SLOT_FWHM_LO_FRACTION * width, 2.0 * step_ev)
        hi_w = max(DETECTION_SLOT_FWHM_HI_FRACTION * width, lo_w + 4.0 * step_ev)
        slots.append(ComponentSlot(
            role=f"detected_peak_{i}",
            region="unassigned",
            phase_id="unassigned",
            be_window=(f.center_be - half_win, f.center_be + half_win),
            line_shape=LineShape.PSEUDO_VOIGT,
            fwhm_range=(lo_w, hi_w),
        ))
    return CandidateModel(name=name, background=background,
                          slots=tuple(slots)), dropped


def merge_residual_attempts(
    pool_payload: dict,
    attempts: list[dict],
    coincidence_ev: float,
    proposal_pass_ran: bool = True,
) -> None:
    """
    Merge the F2 residual-proposal attempts into a pool PAYLOAD (post-fit —
    residual proposals only exist per fitted candidate).  Each attempt is
    ``{"center_be": float, "accepted": bool}``; attempts within
    ``coincidence_ev`` of an existing detection entry annotate that entry
    (provenance += 'residual_gap'), others append a new pool entry.  Every
    annotated entry carries {n_attempts, n_accepted} bookkeeping under the
    ``residual_gap`` key.  Mutates ``pool_payload`` in place.
    """
    if proposal_pass_ran and "residual_gap" not in pool_payload["sources_run"]:
        pool_payload["sources_run"].append("residual_gap")
    features = pool_payload["features"]
    for att in attempts:
        c = float(att["center_be"])
        host = None
        best = None
        for f in features:
            if f.get("window") is not None:
                continue                       # grammar reference entries
            d = abs(float(f["center_be"]) - c)
            if d <= coincidence_ev and (best is None or d < best):
                host, best = f, d
        if host is None:
            host = {
                "center_be": round(c, 3), "provenance": [],
                "in_grammar_window": False, "seeded_role": None,
                "gate_fails": [], "fwhm_est": None, "amplitude_net": None,
                "fraction_of_max": None, "local_snr": None, "prom_z": None,
                "ridge_length": None,
            }
            features.append(host)
        if "residual_gap" not in host["provenance"]:
            host["provenance"].append("residual_gap")
        rg = host.setdefault("residual_gap",
                             {"n_attempts": 0, "n_accepted": 0})
        rg["n_attempts"] += 1
        rg["n_accepted"] += int(bool(att["accepted"]))
    features.sort(key=lambda f: f["center_be"])


126:PROPOSAL_PERSISTENCE_THRESHOLD = ABSENT_SLOT_PERSISTENCE_THRESHOLD
2405:    if sstab.persistence < PROPOSAL_PERSISTENCE_THRESHOLD:
2407:                               f"{PROPOSAL_PERSISTENCE_THRESHOLD:.2f}")
   665	    boundary_hits: list[str] = field(default_factory=list)
   666	
   667	
   668	def _component_supports(result: ModelResult) -> dict[str, dict]:
   669	    """``fitting._component_support`` for every peak component of an lmfit
   670	    result, keyed by prefix — the one definition the server uses (step (b)).
   671	    Empty when the result carries no data (never raises: occupancy then falls
   672	    back to the sign test)."""
   673	    try:
   674	        comps = result.eval_components()
   675	        data = np.asarray(result.data, float)
   676	        fitted = np.asarray(result.best_fit, float)
   677	        w = result.weights if result.weights is not None else np.ones_like(data)
   678	        w = np.broadcast_to(np.asarray(w, float), data.shape)
   679	        n_free_total = int(result.nvarys)
   680	    except Exception:
   681	        return {}
   682	    out = {}
   683	    for prefix, comp_y in comps.items():
   684	        n_free_comp = sum(1 for n, par in result.params.items()
   685	                          if n.startswith(prefix) and par.vary and par.expr is None)
   686	        try:
   687	            out[prefix] = _fitting._component_support(data, fitted, np.asarray(comp_y, float), w,
   688	                                                      n_free_comp, n_free_total)
   689	        except Exception:
   690	            continue
   691	    return out
   692	
   693	
   694	def _followed_supports(result: ModelResult, model: CandidateModel,
   695	                       supports: dict[str, dict]) -> dict[str, dict]:
   696	    """A linked slot whose AMPLITUDE is an expression of its parent's (a
   697	    spin-orbit partner at a fixed area ratio) has no amplitude of its own to
   698	    judge: it FOLLOWS its root's verdict, as the server's support check makes
   699	    a linked component follow its root (`individual_peaks[].support.follows`).
   700	    A linked slot with a free amplitude (only its position tied) keeps its own
   701	    verdict. Walks the chain to the root; a cycle or a missing parent leaves
   702	    the slot's own verdict."""
   703	    by_role = {s.role: s for s in model.slots}
   704	
   705	    def _tied(slot: ComponentSlot) -> bool:
   706	        par = result.params.get(f"{_slot_prefix(slot.role)}amplitude")
   707	        return (slot.linked_to is not None and slot.linked_to in by_role
   708	                and par is not None and par.expr is not None)
   709	
   710	    out = dict(supports)
   711	    for slot in model.slots:
   712	        if not _tied(slot):
   713	            continue
   714	        root, seen = slot, {slot.role}
   715	        while _tied(root):
   716	            root = by_role[root.linked_to]
   717	            if root.role in seen:
   718	                break
   719	            seen.add(root.role)
   720	        else:
   721	            rs = supports.get(_slot_prefix(root.role))
   722	            if rs is not None:
   723	                out[_slot_prefix(slot.role)] = {**rs, "follows": root.role}
   724	    return out
   725	
   726	
   727	def _occupies(comp: "FittedComponent") -> bool:
   728	    """A slot is occupied by a component the data support. No threshold
   729	    on any data-scaled quantity: the support F test where a fit is behind the
   730	    component, else the sign of its amplitude."""
   731	    if comp.support is not None:
   732	        return bool(comp.support.get("supported"))
   733	    return comp.amplitude > 0
   734	
   735	
   736	def _extract_fitted_components(
   737	    result: ModelResult, model: CandidateModel
   130	
   131	**Scale-dependence of the OUTCOME got WORSE on these scans, not better:** main
   132	changes its result under ×0.1 on 2 of 8 scans, this branch on 6 of 8 (Scan_8,
   133	Scan_6, Scan_5, 1-GTA Scan_2, Scan_3, Scan_7). The occupancy statistic itself
   134	is invariant (pinned in `test_occupancy_support.py`), but the pipeline around
   135	it is not: the candidate-detection and proposal gates are Poisson signal-to-
   136	noise ratios, and BIC* with Poisson weights assumes counts, so ×0.1 changes
   137	the candidate set and the ranking. Under the 1-count floor that never reached
   138	occupancy on real data (every real amplitude is far above 1 count, so the
   139	floor never flipped); under F — the likely mechanism, NOT traced scan by
   140	scan — a MARGINAL component (F near 10) now decides a candidate's stability,
   141	and those small upstream differences push it across.
   142	In words: F makes the occupancy test scale-free and honest about marginal
   143	components, and in doing so exposes that the rest of Find Peaks is not
   144	scale-free. Owner-relevant: it is not a reason for C by itself (the ×1 results
   145	are what students get from counts data), but it is not the "scale-free Find
   146	Peaks" the design rule might suggest.
   147	
   148	### A browser test's NOISE-FREE fixture
   149	
   150	`tests/test_browser_find_peaks_full_window.py` (two of four) failed on this
   151	branch: its synthetic C 1s spectrum is noise-free (300 + one Gaussian), fitted
   152	to rounding (χ²ᵣ 0.00), where the support F test is meaningless (the
   153	required-refit known limit in CLAUDE.md). The engine's outcome there turns on
   154	the upload's rounding and wall-clock budgets ON MAIN TOO: through the page,
   155	main returned a conditional fit and the branch none; through a direct
   156	`/api/analyze` replay (4-dp upload) main returned NO survivor and the branch a
   157	clean one. The test is about the apply path with the full-window option off,
   158	not the fit, so its fixture now carries fixed pseudo-random Poisson noise
   159	(√counts × a seeded normal): 4 / 4 pass on main AND on this branch. Known
   160	limit, as for the required-refit test: on noise-free data the occupancy
   161	verdicts are not meaningful.
   162	
   163	## 3. OWNER DECISION — the background-mismatch honesty test
   164	
   165	`test_bg_mismatch_surfaces_loudly` pinned "a wrong background is never a clean
   166	confident result" through the conditional tier, and that tier was reached only
   167	through the component that compensated for the wrong background (P3's third).
   168	The README asked for a mismatch signal that does not ride on it; §2 shows the
   169	signals at hand either are not scale-free (χ²ᵣ) or fire on every real fit
   170	(residual structure). Options:
   171	
   172	| | what | cost |
   173	|---|---|---|
   174	| **A (recommended; implemented on this branch)** | Accept F's outcome and re-state the test's contract to what is true and scale-independent in kind: the engine returns the true 2-peak model, the winner's χ²ᵣ is reported and grossly elevated, and the result carries `filtered_dominant_alternative` (the page's red banner). No new rule. The principled mismatch check is a comparison of BACKGROUND models (the matched-control case shows Shirley candidates absorb the integral background) — logged as its own unit | a wrong-background result is no longer marked "conditional"; the red banner remains |
   175	| B | a result-level `model_mismatch` flag from a chosen constant (e.g. n_eff/n < 0.02, between the stress case's 0.0075 and real data's ≥ 0.04) | a new threshold on a data-dependent quantity (n_eff/n also depends on the sampling step) — the design rule's failure; needs calibration; NOT recommended |
   176	| C | keep the 1-count floor until a background-comparison check exists | the occupancy floor stays scale-dependent |
   177	
   178	A is what this branch ships; if the owner prefers C the branch waits.
    76	        assert b[role].support["f"] == pytest.approx(a[role].support["f"], rel=1e-4), role
    77	        assert _occupies(a[role]) and _occupies(b[role])
    78	
    79	
    80	def test_residue_above_one_count_is_not_an_occupant():
    81	    # 5 counts on a 1e5-count baseline: the old floor called it occupied
    82	    comps = _fit(_spectrum(1e5, 2e5, 5.0))
    83	    minor = comps["minor"]
    84	    assert minor.support["supported"] is False, minor.support
    85	    assert not _occupies(minor)
    86	

codex
The focused suites pass: 47 tests across occupancy, stress honesty, linked doublets, full-window fitting, and method payloads. I reproduced a parameter-count bug with valid roles `main` and `main_other`: the helper counts both components’ parameters for `main`, reducing F from 15.75 to 7.88 and incorrectly marking it unsupported.

exec
/bin/zsh -lc "sed -n '1,170p' tests/autofit/test_c1s_parity_gate.py; rg --files tests/autofit | rg 'parity|real'; rg -n 'Scan_6|1-GTA|load.*project' tests/autofit | head -35; sed -n '1,180p' tests/autofit/test_real_c1s.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 exited 1 in 0ms:
"""
Stage-2 C 1s parity gate (spec §0/§3.1): the resolver + IC engine must
reproduce the expert C 1s reference fits within tolerance.

Parity is defined on what the grammar and the expert fits AGREE on
physically — not peak-by-peak equality, because the expert fits use freer
width conventions than the grammar caps (adventitious FWHM up to 2.66 eV
vs the ADJUDICATED uniform 2.0 eV cap — adjudication-decisions.md #5,
2026-07-03; the cap is the ruling, so exact width parity with the broadest
expert components is not expressible by construction).

Gate assertions per anchor spectrum:
1. the engine finds >= 1 surviving candidate (no forced answer, but the
   anchors are good-quality spectra — zero survivors means the grammar or
   pipeline regressed);
2. the winner's graphitic main lands within MAIN_CENTER_TOL of the expert
   graphite peak;
3. the winner includes the π→π* satellite within SATELLITE_TOL of the
   expert satellite;
4. envelope-level agreement: R-factor between the engine winner's envelope
   and the expert's saved fittedY below ENVELOPE_R_TOL.

Runtime: even reduced (3 candidates, 4 refits, proposal pass off) this takes
several minutes per anchor, so it is gated behind RUN_AUTOFIT_GATE=1 — run it
at stage checkpoints and after grammar/engine changes:

    RUN_AUTOFIT_GATE=1 venv/bin/pytest tests/autofit/test_c1s_parity_gate.py

The always-on fast regression net is tests/autofit/test_c1s_parity_battery.py;
the FULL 25-candidate calibration is scripts/run_c1s_full_calibration.py.
"""

import os

import numpy as np
import pytest

if os.environ.get("RUN_AUTOFIT_GATE") != "1":
    # LOUD skip (Codex Stage-2 finding #8): this is a REQUIRED Stage-2 gate.
    # A default run does not enforce it — the always-on parity net is the
    # characterization battery.  Run this gate at every stage checkpoint and
    # after any grammar/engine change:  RUN_AUTOFIT_GATE=1 pytest <this file>
    pytest.skip(
        "SKIPPING REQUIRED STAGE GATE (C 1s parity) — slow; set "
        "RUN_AUTOFIT_GATE=1 to enforce. Do not treat a run without it as a "
        "full Stage-2 verification.",
        allow_module_level=True,
    )

from autofit.grammar import MaterialClass, Phase, resolve
from autofit.methods import get_method
from autofit.parity import evaluate_model
from autofit.reference import load_reference_fits
from fitting import shirley_background

REPO = os.path.join(os.path.dirname(__file__), "..", "..")
DATA = os.path.join(REPO, "docs", "autofit", "test_data")

ANCHORS = [
    ("UCl4_on_graphite.proj.zip", "C1s Scan_8"),
    ("8-JT Graphite.proj.zip", "C1s Scan_2"),
    ("1-GTA UCl4-graphite one set of U doublets.proj.zip", "C1s Scan_6"),
]

# Reduced representative candidate set: the MG expert-structure family, the
# AG lab-practice family, and a Biesinger-convention A competitor.
GATE_CANDIDATES = [
    "MG2_graphAsymGL_aliph_sat_CO_C=O",
    "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O",
    "AG2_linked",
    "A2_linked",
]

# Calibrated 2026-07-03; RE-calibrated 2026-07-04 under the adjudicated
# uniform 2.0 eV contamination cap (see PROGRESS.md parity-gate calibration
# log).  Measured mains: Scan_2 4 meV (clean MG2), Scan_6 12 meV (clean
# AG2), Scan_8 54 meV — the UCl4-composite anchor's expert adventitious
# widths (median 2.08 eV) exceed the cap, so its MG/AG candidates go
# boundary-limited/unstable and the winner drops to the conditional
# no_clean_survivor tier (A2_linked).  That anchor's degradation is the
# adjudicated convention meeting data that prefers wider components —
# expected, documented, not silently forced.
MAIN_CENTER_TOL_EV = 0.08
SATELLITE_TOL_EV = 0.5
# Measured domain envelope R 2026-07-04 under the adjudicated cap:
# Scan_2/Scan_6 unchanged (0.004–0.014); Scan_8 0.0407 (conditional-tier
# winner — same cap-vs-data cause as the main-center recalibration above).
ENVELOPE_R_TOL = 0.05     # Σ|engine−expert| / Σ|expert|, BE ≥ ENVELOPE_DOMAIN_MIN
# The expert fits model a low-BE 'Unknown' (~283.4 eV) that sits outside every
# grammar window (PROGRESS.md discrepancy #6 — proposal-pass territory, which
# the gate disables for runtime).  Envelope parity is asserted on the
# grammar's domain.
ENVELOPE_DOMAIN_MIN = 284.0

GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
                 regions=("C 1s",), material="graphite")


def _anchor(project, name):
    path = os.path.join(DATA, project)
    rf = next(r for r in load_reference_fits(path) if r.name == name)
    return rf


@pytest.fixture(scope="module")
def grammar():
    return resolve([GRAPHITE], "C 1s")


@pytest.mark.parametrize("project,name", ANCHORS,
                         ids=[f"{p}::{n}" for p, n in ANCHORS])
def test_c1s_parity_gate(grammar, project, name):
    rf = _anchor(project, name)
    expert_by_name = { (p.get("name") or "").lower(): p for p in rf.peaks }
    expert_graphite = next(v for k, v in expert_by_name.items() if "graphit" in k)
    expert_satellite = next((v for k, v in expert_by_name.items()
                             if "satellite" in k or "π" in k), None)

    res = get_method("ic_model_comparison").run(
        rf.roi_be, rf.roi_intensity, grammar=grammar,
        options={"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
                 "candidate_filter": GATE_CANDIDATES,
                 "enable_proposal_pass": False},
    )

    # (1) a survivor exists — clean tier preferred, conditional tier accepted
    # WITH its violations surfaced (two-tier semantics; on these composite
    # samples some lit-convention constraint typically binds somewhere)
    assert res.success, (
        f"{name}: no surviving candidate — {res.message}\n"
        + "\n".join(f"  {c['name']}: {c['filter_reason']}"
                    for c in res.analysis["candidates"])
    )
    if res.diagnostics["conditional"]:
        if res.diagnostics["conditional_reason"] == "decisive_override":
            # winner is a bound-fixed refit: constraint evidence lives in the
            # list of parameters fixed at their bounds
            assert res.diagnostics["winner_boundary_fixed_params"], (
                "override winner must record its bound-fixed parameters"
            )
        else:
            assert res.diagnostics["winner_boundary_hits"], (
                "conditional winner must carry its constraint violations"
            )

    # (2) graphitic main position parity
    main = next(p for p in res.peaks if p["role"] == "main_graphitic")
    dc = abs(main["center"] - expert_graphite["center"])
    assert dc <= MAIN_CENTER_TOL_EV, (
        f"{name}: engine graphitic main {main['center']:.3f} vs expert "
        f"{expert_graphite['center']:.3f} (Δ {dc*1000:.0f} meV)"
    )

    # (3) satellite present and positioned
    if expert_satellite is not None:
        sat = next((p for p in res.peaks if p["role"] == "satellite_pi"), None)
        assert sat is not None, f"{name}: winner has no π→π* satellite slot"
        ds = abs(sat["center"] - expert_satellite["center"])
        assert ds <= SATELLITE_TOL_EV, (
            f"{name}: satellite {sat['center']:.3f} vs expert "
            f"{expert_satellite['center']:.3f} (Δ {ds:.2f} eV)"
        )

    # (4) envelope-level parity vs the expert's saved envelope
    specs = []
    for p in res.peaks:
        spec = dict(p)
        spec.pop("role", None); spec.pop("region", None)
        spec.pop("phase_id", None); spec.pop("stderr", None)
        specs.append(spec)
tests/autofit/test_u4f_parity_gate.py
tests/autofit/test_u4f_parity_battery.py
tests/autofit/test_bayesian_real_gate.py
tests/autofit/test_c1s_parity_gate.py
tests/autofit/test_candidate_pool_real_gate.py
tests/autofit/test_b1s_cl2p_parity_gates.py
tests/autofit/test_c1s_parity_battery.py
tests/autofit/test_browser_schema_roundtrip.py:7:    save → load → save on BOTH project formats (.proj.json < 5 tabs,
tests/autofit/test_u4f_parity_gate.py:53:    return next(r for r in load_reference_fits(os.path.join(DATA, project))
tests/autofit/test_c1s_parity_gate.py:62:    ("1-GTA UCl4-graphite one set of U doublets.proj.zip", "C1s Scan_6"),
tests/autofit/test_c1s_parity_gate.py:76:# log).  Measured mains: Scan_2 4 meV (clean MG2), Scan_6 12 meV (clean
tests/autofit/test_c1s_parity_gate.py:86:# Scan_2/Scan_6 unchanged (0.004–0.014); Scan_8 0.0407 (conditional-tier
tests/autofit/test_u4f_parity_battery.py:30:# Scan_6, a flat alpha/beta/m valley) wobbles at 1.4e-4 relative across
tests/autofit/fixtures/c1s_battery_expected.json:49:   "project": "1-GTA UCl4-graphite one set of U doublets.proj.zip",
tests/autofit/fixtures/c1s_battery_expected.json:100:   "project": "1-GTA UCl4-graphite one set of U doublets.proj.zip",
tests/autofit/fixtures/c1s_battery_expected.json:151:   "project": "1-GTA UCl4-graphite one set of U doublets.proj.zip",
tests/autofit/fixtures/c1s_battery_expected.json:202:   "project": "1-GTA UCl4-graphite one set of U doublets.proj.zip",
tests/autofit/fixtures/c1s_battery_expected.json:253:   "project": "1-GTA UCl4-graphite one set of U doublets.proj.zip",
tests/autofit/fixtures/c1s_battery_expected.json:304:   "project": "1-GTA UCl4-graphite one set of U doublets.proj.zip",
tests/autofit/fixtures/c1s_battery_expected.json:355:   "project": "1-GTA UCl4-graphite one set of U doublets.proj.zip",
tests/autofit/fixtures/c1s_battery_expected.json:361:   "name": "C1s Scan_6",
tests/autofit/fixtures/c1s_battery_expected.json:406:   "project": "1-GTA UCl4-graphite one set of U doublets.proj.zip",
tests/autofit/fixtures/c1s_battery_expected.json:457:   "project": "1-GTA UCl4-graphite one set of U doublets.proj.zip",
tests/autofit/fixtures/c1s_battery_expected.json:508:   "project": "1-GTA UCl4-graphite one set of U doublets.proj.zip",
tests/autofit/fixtures/c1s_battery_expected.json:822:   "name": "C1s Scan_6",
tests/autofit/fixtures/c1s_battery_expected.json:1267:   "name": "C1s Scan_6",
tests/autofit/test_b1s_cl2p_parity_gates.py:43:    return next(r for r in load_reference_fits(os.path.join(DATA, project))
tests/autofit/fixtures/b1s_battery_expected.json:20:   "name": "B1s Scan_6",
tests/autofit/fixtures/b1s_battery_expected.json:154:   "name": "B1s Scan_6",
tests/autofit/fixtures/u4f_battery_expected.json:35:   "project": "1-GTA UCl4-graphite one set of U doublets.proj.zip",
tests/autofit/fixtures/u4f_battery_expected.json:72:   "project": "1-GTA UCl4-graphite one set of U doublets.proj.zip",
tests/autofit/fixtures/u4f_battery_expected.json:109:   "project": "1-GTA UCl4-graphite one set of U doublets.proj.zip",
tests/autofit/fixtures/u4f_battery_expected.json:146:   "project": "1-GTA UCl4-graphite one set of U doublets.proj.zip",
tests/autofit/fixtures/u4f_battery_expected.json:183:   "project": "1-GTA UCl4-graphite one set of U doublets.proj.zip",
tests/autofit/fixtures/u4f_battery_expected.json:220:   "project": "1-GTA UCl4-graphite one set of U doublets.proj.zip",
tests/autofit/fixtures/u4f_battery_expected.json:257:   "project": "1-GTA UCl4-graphite one set of U doublets.proj.zip",
tests/autofit/fixtures/u4f_battery_expected.json:263:   "name": "U4f Scan_6",
tests/autofit/fixtures/u4f_battery_expected.json:294:   "project": "1-GTA UCl4-graphite one set of U doublets.proj.zip",
tests/autofit/fixtures/u4f_battery_expected.json:331:   "project": "1-GTA UCl4-graphite one set of U doublets.proj.zip",
tests/autofit/fixtures/u4f_battery_expected.json:368:   "project": "1-GTA UCl4-graphite one set of U doublets.proj.zip",
tests/autofit/fixtures/u4f_battery_expected.json:462:   "name": "U4f Scan_6",
tests/autofit/fixtures/u4f_battery_expected.json:765:   "name": "U4f Scan_6",
sed: tests/autofit/test_real_c1s.py: No such file or directory

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile,sys
tempfile.tempdir=\"/tmp\"; sys.modules[\"matplotlib\"]=None
import numpy as np
import autofit.engine as e
from autofit.grammar import *
from autofit.reference import load_reference_fits
rf=next(r for r in load_reference_fits(\"docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip\") if r.name==\"C1s Scan_6\")
gr=resolve([Phase(id=\"graphite\",material_class=MaterialClass.CONDUCTOR,regions=(\"C 1s\",),material=\"graphite\")],\"C 1s\")
for model in gr.candidates:
 if model.name not in [\"MG2_graphAsymGL_aliph_sat_CO_C=O\",\"MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O\"]: continue
 x,y=rf.roi_be,rf.roi_intensity; w=1/np.sqrt(np.maximum(y,1))
 pri=e.fit_candidate(x,y,w,model)
 sta=e.run_stability_analysis(x,y,w,model,pri,1,n_refits=4,rng_seed=0)
 best=sta.best_outcome if sta.best_outcome and sta.best_outcome.weighted_chi_sq<pri.weighted_chi_sq else pri
 print(model.name, \"chi\", pri.weighted_chi_sq,best.weighted_chi_sq,\"boundary\",best.boundary_hits,flush=True)
 for c in best.components:
  print(c.slot_role,c.amplitude,c.support,\"persistence\",sta.per_slot[c.slot_role].persistence,flush=True)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile,sys,runpy; tempfile.tempdir=\"/tmp\"; sys.modules[\"matplotlib\"]=None; t=runpy.run_path(\"tests/autofit/test_occupancy_support.py\"); c=t[\"_fit\"](t[\"_spectrum\"](1e5,2e5,5.0))[\"minor\"]; print(c)'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 1552ms:
FittedComponent(slot_role='minor', position=286.69217960011844, fwhm=1.5533524382720865, amplitude=374.7331073553738, shape_params={}, line_shape=<LineShape.GAUSSIAN: 'gaussian'>, support={'f': 5.441003869904107, 'delta_chi2': 32.725466909720524, 'supported': False})

 succeeded in 27463ms:
MG2_graphAsymGL_aliph_sat_CO_C=O chi 7842.253517852832 5705.315057977472 boundary ['main_aliphatic:offset@min', 'main_aliphatic:fwhm@max']
main_graphitic 42310.549890790186 {'f': 881.9656661815435, 'delta_chi2': 148872.54425694357, 'supported': True} persistence 1.0
main_aliphatic 18504.092648642494 {'f': 1611.2471167726571, 'delta_chi2': 217578.04585670598, 'supported': True} persistence 1.0
satellite_pi 1722.4113750944352 {'f': 117.42532414955454, 'delta_chi2': 15856.76852209087, 'supported': True} persistence 1.0
contamination_CO 1861.5992149239873 {'f': 18.93924708684141, 'delta_chi2': 2557.4999193210006, 'supported': True} persistence 0.5
contamination_C=O 1432.446525267696 {'f': 26.883034630651093, 'delta_chi2': 3630.205497807894, 'supported': True} persistence 1.0
MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O chi 7829.722019593231 5641.599726185399 boundary ['contamination_CO:fwhm@min', 'contamination_C=O:center@min', 'contamination_OC=O:center@min', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@max']
main_graphitic 42291.75926871193 {'f': 869.4562918057821, 'delta_chi2': 148640.1326600507, 'supported': True} persistence 1.0
main_aliphatic 18532.4890161417 {'f': 1594.882362249029, 'delta_chi2': 218125.76722817076, 'supported': True} persistence 1.0
satellite_pi 1701.6039958635874 {'f': 108.418746964508, 'delta_chi2': 14828.004198505027, 'supported': True} persistence 1.0
contamination_CO 1832.1732965285764 {'f': 15.836431253031845, 'delta_chi2': 2165.886211414748, 'supported': True} persistence 1.0
contamination_C=O 1652.0566584931769 {'f': 25.477064151281144, 'delta_chi2': 3484.3975306636494, 'supported': True} persistence 1.0
contamination_OC=O 693.7068112595354 {'f': 5.4236832757069955, 'delta_chi2': 741.7757595913918, 'supported': False} persistence 0.0

exec
/bin/zsh -lc "sed -n '1212,1252p' autofit/engine.py; sed -n '110,131p' autofit/engine.py; rg -n 'OWNER|review|approval|agent' CLAUDE.md | tail -25; git diff --check main..HEAD" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
# Stability
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SlotStability:
    role: str
    persistence: float
    position_median: Optional[float]
    position_mad: Optional[float]
    fwhm_median: Optional[float]
    fwhm_mad: Optional[float]
    amplitude_median: Optional[float]
    amplitude_mad: Optional[float] = None


@dataclass
class ModelStability:
    per_slot: dict[str, SlotStability]
    orphan_rate: float
    convergence_rate: float
    # Best converged refit found during the multi-start pass (by weighted χ²).
    # Port improvement over fitalg, which always reported the primary fit even
    # when a perturbed refit found a deeper minimum: the driver promotes this
    # outcome when it beats the primary, so the report describes the best
    # minimum FOUND and the stability numbers describe its robustness.
    best_outcome: Optional[FitOutcome] = None
    # How many multi-start fits (refits + primary) landed within
    # BASIN_SUPPORT_RTOL of the best weighted χ² — an honesty diagnostic for
    # the best-minimum promotion (Codex Stage-2 re-review finding #4: a
    # one-off deeper minimum is a different product than a reproducible one).
    # Reporting-only; never used in ranking.
    best_basin_support: int = 0
    # How many of the requested n_refits were actually attempted before the
    # candidate's wall-clock budget (CANDIDATE_TIMEOUT_SEC) ran out. Equal to
    # n_refits unless timed_out is True — used as the honest denominator for
    # persistence/orphan_rate/convergence_rate instead of silently
    # understating them against the full nominal n_refits.
    n_attempted: int = 0
    timed_out: bool = False

    @property
# B 1s 2.5, …); those declared maxima ABOVE this ceiling mark a slot as
# grammar-sanctioned-broad and exempt it from the unphysical-width flag.  A
# proposed/pre-seeded peak that PEGS this cap (wants wider than physical with
# no known-broad justification) is NOT silently widened: the fit is held at
# the physical limit and the result is flagged (unphysical_widths →
# conditional/low-confidence), per the fit-quality rail "a defensible fit
# with physical widths beats a lower χ² bought with a fat peak".  UNVERIFIED
# numeric bound (a cap, not a target).
FWHM_MAX_ORDINARY_EV = 2.0
# The proposal/pre-seed upper FWHM bound IS the ordinary physical cap (was a
# looser 3.0 that let residual proposals grow to fat, physically indefensible
# widths — e.g. a real-data 281 eV feature fitting at 3.0 eV).
PROPOSAL_FWHM_MAX = FWHM_MAX_ORDINARY_EV
PROPOSED_PEAK_SHAPE = LineShape.PSEUDO_VOIGT
PROPOSAL_GRAMMAR_SEPARATION_FACTOR = 0.5
PROPOSAL_DELTABIC_THRESHOLD = 2.0
PROPOSAL_PERSISTENCE_THRESHOLD = ABSENT_SLOT_PERSISTENCE_THRESHOLD
PROPOSAL_AMPLITUDE_SNR = 5.0
# Unit F2 (2026-07-07): raised 1 → 3 and made ITERATIVE — after an accepted
# proposal, detection re-runs on the AUGMENTED model's residual and another
# proposal may be accepted (same gates each round: SNR, ΔBIC*, persistence,
# boundary cleanliness; same per-candidate wall budget).  Measured
49:| `POST`   | `/api/upload`             | Upload a spectrum file; returns `session_id` + downsampled preview. |
51:| `GET`    | `/api/session/<id>`       | Retrieve a stored session's preview data. |
187:When two places read the same input — the page and the server, a preview
191:a free η to the server (A03); the ROI, the preview background and the fitted
282:were actually being fit against, due to a pre-existing preview/backend
448:(in review each such no-op edit moved an area fraction by 15–45 pp
485:OWNER DECISION 2026-09-21: ACCEPT AND DISCLOSE; no unit for bit-identity.
493:second thing (a reviewer tried a deterministic perturbation base: identical
526:the largest move named, amber > 0.5 eV, red > 1 eV) with Preview (the
527:history-preview overlay, on a copy) and "Use this solution": explicit, one
545:the comparison no longer applies, nothing can be previewed or applied, an
546:open alternative preview is dropped (`_dropStaleAltPreview`), and
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-BlbfuCtE' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-HDUmTNE3' (errno=Operation not permitted)

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile,sys,dataclasses
tempfile.tempdir=\"/tmp\"; sys.modules[\"matplotlib\"]=None
sys.path.insert(0,\"tests/autofit\")
from unittest.mock import patch
import autofit.engine as e
from autofit.methods.base import poisson_like_weights
from stress_cases import isolated_missing_peak_case
case=isolated_missing_peak_case(seed=71); x,y=case.x,case.y; w=poisson_like_weights(y)
res=e.compare_models(x,y,w,case.grammar,n_refits=2,rng_seed=0,enable_proposal_pass=False,enable_preseed=False)
base=res.reports[0]; yf=base.primary_fit.lmfit_result.best_fit+base.primary_fit.background
spec=e._detect_residual_proposals(x,y,yf,1.,base.model,fitted_components=base.primary_fit.components)[0]
aug=e._augmented_candidate(base.model,spec); bg=e._compute_background(x,y,aug.background)
init=e._initial_params_for_augmented(aug,base.primary_fit,spec,x,y-bg)
real=e.fit_candidate(x,y,w,aug,initial_params=init)
comps=[dataclasses.replace(c,support={\"f\":3.,\"delta_chi2\":30.,\"supported\":False}) if c.slot_role==spec.role else c for c in real.components]
promoted=dataclasses.replace(real,weighted_chi_sq=real.weighted_chi_sq*.99,components=comps)
stab=e.ModelStability(per_slot={c.slot_role:e.SlotStability(c.slot_role,.75 if c.slot_role==spec.role else 1.,c.position,0.,c.fwhm,0.,c.amplitude,0.) for c in comps},orphan_rate=0.,convergence_rate=1.,best_outcome=promoted,n_attempted=4)
with patch.object(e,\"run_stability_analysis\",return_value=stab):
 report,pr,status=e._attempt_proposal(x=x,y=y,weights=w,base_report=base,spec=spec,noise_floor=1.,n_refits=4,rng_seed=0,absent_slot_area_fraction=.02,absent_slot_persistence_threshold=.7,diagnostic_windows=dict(case.grammar.diagnostic_windows),budget_remaining=1e6)
 print(\"Injected promotion seam:\",status,\"accepted\",pr.accepted,\"persistence\",pr.persistence,\"initial_support\",next(c.support for c in real.components if c.slot_role==spec.role),\"final_support\",next(c.support for c in report.primary_fit.components if c.slot_role==spec.role) if report else None,flush=True)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 1508ms:
Injected promotion seam: accepted accepted True persistence 0.75 initial_support {'f': 12349.483167865066, 'delta_chi2': 52688.49883361818, 'supported': True} final_support {'f': 3.0, 'delta_chi2': 30.0, 'supported': False}

exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '2325,2341p'; nl -ba autofit/engine.py | sed -n '2374,2410p'; nl -ba autofit/engine.py | sed -n '1610,1632p'; git status --short" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
  2325	    # _proposed_slot_pegs.)  NOTE this is re-evaluated AFTER the stability
  2326	    # best-outcome promotion below, since a deeper minimum can move a param
  2327	    # to a wall (Codex fwhm-cap review, run B BLOCKER).
  2328	    width_cap_hit = f"{spec.role}:fwhm@max"
  2329	    pr.boundary_hits = _proposed_slot_pegs(primary, spec.role)
  2330	    if not _occupies(comp):
  2331	        f = (comp.support or {}).get("f")
  2332	        return _fast("not supported by the data (removing it does not make the fit significantly worse"
  2333	                     + (f", F = {f:.2f} < {_fitting.SUPPORT_MIN_F:.0f}" if f is not None else "") + ")")
  2334	    spurious_hits = [h for h in pr.boundary_hits if h != width_cap_hit]
  2335	    if spurious_hits:
  2336	        return _fast(f"proposed slot boundary pegs: {spurious_hits}")
  2337	
  2338	    mask = (x >= comp.position - PROPOSAL_WINDOW_WIDTH) & \
  2339	           (x <= comp.position + PROPOSAL_WINDOW_WIDTH)
  2340	    local_sigma = float(np.median(np.sqrt(np.maximum(y[mask], noise_floor)))) \
  2341	        if mask.sum() > 1 else float(np.sqrt(max(noise_floor, 1.0)))
  2374	        deadline=time.perf_counter() + min(remaining,
  2375	                                           PROPOSAL_STABILITY_TIMEOUT_SEC),
  2376	        fit_full_window=fit_full_window,
  2377	        endpoint_avg=endpoint_avg,
  2378	    )
  2379	    if (stability.best_outcome is not None
  2380	            and stability.best_outcome.weighted_chi_sq < primary.weighted_chi_sq):
  2381	        primary = stability.best_outcome
  2382	        comp = next((c for c in primary.components if c.slot_role == spec.role), comp)
  2383	        if comp is not None:
  2384	            pr.fitted_center = comp.position
  2385	            pr.fitted_fwhm = comp.fwhm
  2386	            pr.fitted_amplitude = comp.amplitude
  2387	    # Re-evaluate the proposed-slot pegs against the FINAL (possibly
  2388	    # stability-promoted) outcome — a deeper minimum can move a param to a
  2389	    # wall the initial fit did not touch (Codex fwhm-cap review, run B
  2390	    # BLOCKER): a stability-promoted center@min must STILL reject, and a
  2391	    # stability-INTRODUCED fwhm@max must set width_capped so the payload
  2392	    # matches the emitted decomposition.
  2393	    pr.boundary_hits = _proposed_slot_pegs(primary, spec.role)
  2394	    spurious_hits = [h for h in pr.boundary_hits if h != width_cap_hit]
  2395	    if spurious_hits:
  2396	        pr.rejection_reason = (
  2397	            f"proposed slot boundary pegs (post-stability): {spurious_hits}")
  2398	        return None, pr, "stability_rejected"
  2399	    pr.width_capped = pr.boundary_hits == [width_cap_hit]
  2400	    sstab = stability.per_slot.get(spec.role)
  2401	    if sstab is None:
  2402	        pr.rejection_reason = "proposed slot missing from stability output"
  2403	        return None, pr, "stability_rejected"
  2404	    pr.persistence = sstab.persistence
  2405	    if sstab.persistence < PROPOSAL_PERSISTENCE_THRESHOLD:
  2406	        pr.rejection_reason = (f"persistence {sstab.persistence:.2f} < "
  2407	                               f"{PROPOSAL_PERSISTENCE_THRESHOLD:.2f}")
  2408	        return None, pr, "stability_rejected"
  2409	
  2410	    y_fit_aug = (primary.lmfit_result.best_fit + primary.background
  1610	    def adjusted_n_params(self) -> int:
  1611	        removed = sum(a.removed_n_params for a in self.absent_slots)
  1612	        return max(self.primary_fit.n_params - removed, 1)
  1613	
  1614	    @property
  1615	    def bic_adjusted(self) -> float:
  1616	        """BIC* (heuristic — absent-slot params arithmetically subtracted;
  1617	        the BIC/IC math review requires the raw full-k and weighted
  1618	        counterparts REPORTED beside it: see bic_raw / bic_weighted)."""
  1619	        n = self.primary_fit.n_data
  1620	        rss = self.primary_fit.residual_sum_sq
  1621	        if n <= 0 or rss <= 0:
  1622	            return float("inf")
  1623	        return n * np.log(rss / n) + self.adjusted_n_params * np.log(n)
  1624	
  1625	    @property
  1626	    def bic_raw(self) -> float:
  1627	        """Full-k, no absent-slot adjustment — reported beside the labeled
  1628	        heuristic so the adjustment can never silently decide alone
  1629	        (BIC/IC math review: 'large-model RSS with small-model penalty')."""
  1630	        return compute_bic(self.primary_fit)
  1631	
  1632	    @property
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-c6QY5R1s' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-hUQs5pTZ' (errno=Operation not permitted)
?? docs/autofit/codex/occupancy_f_test_verdict_runA.md
?? docs/autofit/codex/occupancy_f_test_verdict_runB.md
?? "docs/autofit/test_data/7 - GTA-2-66 U-naph and COT.DATA"
?? "docs/autofit/test_data/8 GTA-2-46ii U-naph and XeF2, graphite 40%, powder, Cu, 0.4eV, 400 um.DATA"
?? docs/autofit/test_data/Ugly_Fe_2p.spec.json
?? docs/autofit/test_data/Ugly_Fe_2p_2.spec.json

codex
1. **MAJOR — Component-name prefixes corrupt the F statistic.** [autofit/engine.py:684](/Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test/autofit/engine.py:684) counts parameters using `startswith(prefix)`. Valid roles `main` and `main_other` produce overlapping prefixes, so `main` gets both components’ free parameters.

   Reproduced with a real two-Gaussian fit: six total free parameters, three belonging to each component. The weak component’s correct **F = 15.7526, supported** becomes **F = 7.8763, unsupported**. Its fitted amplitude is 160.126 counts. This incorrectly empties its slot and changes persistence. The reproduction uses a custom engine model; I did not find this naming collision among built-in candidates. Assign parameters to their owning component, including auxiliary offset/ratio parameters, rather than using unrestricted prefix matching.

2. **MAJOR — A promoted refit can bypass the proposal’s support gate.** [autofit/engine.py:2330](/Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test/autofit/engine.py:2330) checks the initial augmented fit. [autofit/engine.py:2381](/Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test/autofit/engine.py:2381) can then replace it with a better stability refit, but only boundary pegs are rechecked.

   Failing scenario: three of four refits support the proposal; the lowest-χ² refit does not. Persistence remains 0.75, above the 0.7 gate, and the unsupported final component can be accepted. A controlled probe using a real initial fit and an injected promotion outcome returned **`accepted=True` with final `supported=False`, F=3**. This establishes the control-flow failure; I did not reproduce that transition from an unmodified spectrum. Recheck `_occupies(comp)` after promotion and add a regression test—the new occupancy tests never exercise `_attempt_proposal`.

3. **MINOR — The scale-dependence explanation misidentifies the ranking criterion.** [plan:136](/Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test/docs/superpowers/plans/2026-09-27-occupancy-f-test.md:136) attributes ranking changes to “BIC* with Poisson weights.” Actual BIC* is `n·log(RSS/n) + k·log(n)`. For corresponding scaled fits with unchanged candidates and parameter counts, multiplying intensities by `c` adds the same `2n·log(c)` to every score, preserving ranking. The weighted-χ² companion criterion is different. Detection/proposal gates and changed optimization outcomes remain plausible causes, but the reported 2/8 → 6/8 regression needs that distinction; its mechanism remains untraced.

**Validation:** 47 focused tests passed, covering occupancy, stress honesty, doublets, full-window fitting, and method payloads. No files changed. I did not replay the full real-data sweep or browser suite.

Apart from the parameter-ownership bug, the helper uses the producing fit’s data, background-subtracted best fit, weights, and total free-parameter count correctly. `SUPPORT_MIN_F` is reused. The production slot-map iterator removes `__unsupported__`; Bayesian selection does not consume this occupancy path. Poor global fits suppressing real components remain a documented limitation of the chosen server statistic.

Option A honestly narrows the stress fixture’s contract, and its alternative-model warning reaches the page. It **does not provide an independent background-mismatch signal**: that warning still requires a better-scoring alternative. The pending owner decision should explicitly accept that deferred requirement. The measured outcome-scale regression alone does not establish that F should be abandoned.

**VERDICT: NO-GO.**
tokens used
115,347
1. **MAJOR — Component-name prefixes corrupt the F statistic.** [autofit/engine.py:684](/Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test/autofit/engine.py:684) counts parameters using `startswith(prefix)`. Valid roles `main` and `main_other` produce overlapping prefixes, so `main` gets both components’ free parameters.

   Reproduced with a real two-Gaussian fit: six total free parameters, three belonging to each component. The weak component’s correct **F = 15.7526, supported** becomes **F = 7.8763, unsupported**. Its fitted amplitude is 160.126 counts. This incorrectly empties its slot and changes persistence. The reproduction uses a custom engine model; I did not find this naming collision among built-in candidates. Assign parameters to their owning component, including auxiliary offset/ratio parameters, rather than using unrestricted prefix matching.

2. **MAJOR — A promoted refit can bypass the proposal’s support gate.** [autofit/engine.py:2330](/Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test/autofit/engine.py:2330) checks the initial augmented fit. [autofit/engine.py:2381](/Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test/autofit/engine.py:2381) can then replace it with a better stability refit, but only boundary pegs are rechecked.

   Failing scenario: three of four refits support the proposal; the lowest-χ² refit does not. Persistence remains 0.75, above the 0.7 gate, and the unsupported final component can be accepted. A controlled probe using a real initial fit and an injected promotion outcome returned **`accepted=True` with final `supported=False`, F=3**. This establishes the control-flow failure; I did not reproduce that transition from an unmodified spectrum. Recheck `_occupies(comp)` after promotion and add a regression test—the new occupancy tests never exercise `_attempt_proposal`.

3. **MINOR — The scale-dependence explanation misidentifies the ranking criterion.** [plan:136](/Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test/docs/superpowers/plans/2026-09-27-occupancy-f-test.md:136) attributes ranking changes to “BIC* with Poisson weights.” Actual BIC* is `n·log(RSS/n) + k·log(n)`. For corresponding scaled fits with unchanged candidates and parameter counts, multiplying intensities by `c` adds the same `2n·log(c)` to every score, preserving ranking. The weighted-χ² companion criterion is different. Detection/proposal gates and changed optimization outcomes remain plausible causes, but the reported 2/8 → 6/8 regression needs that distinction; its mechanism remains untraced.

**Validation:** 47 focused tests passed, covering occupancy, stress honesty, doublets, full-window fitting, and method payloads. No files changed. I did not replay the full real-data sweep or browser suite.

Apart from the parameter-ownership bug, the helper uses the producing fit’s data, background-subtracted best fit, weights, and total free-parameter count correctly. `SUPPORT_MIN_F` is reused. The production slot-map iterator removes `__unsupported__`; Bayesian selection does not consume this occupancy path. Poor global fits suppressing real components remain a documented limitation of the chosen server statistic.

Option A honestly narrows the stress fixture’s contract, and its alternative-model warning reaches the page. It **does not provide an independent background-mismatch signal**: that warning still requires a better-scoring alternative. The pending owner decision should explicitly accept that deferred requirement. The measured outcome-scale regression alone does not establish that F should be abandoned.

**VERDICT: NO-GO.**
