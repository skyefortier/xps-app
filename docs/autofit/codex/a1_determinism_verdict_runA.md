2026-09-29T18:55:32.739910Z ERROR codex_models_manager::manager: failed to refresh available models: timeout waiting for child process to exit
2026-09-29T18:55:32.778313Z ERROR codex_models_manager::manager: failed to refresh available models: timeout waiting for child process to exit
OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0ee85-abaf-74c0-ad3b-28c37d5a4cb6
--------
user
Review unit A1 (Find Peaks determinism), round 1: branch fix-find-peaks-determinism, git diff main..HEAD (autofit/engine.py; tests/autofit/test_fit_certificate.py; tests/autofit/test_preseed_dominants.py; CLAUDE.md; docs/superpowers/plans/2026-09-29-a1-find-peaks-determinism.md; the scope-check findings under docs/findings/fit-termination-scope/). Owner's brief: "Find Peaks' answer must not depend on server load or on the optimiser's own termination flags. Count refits, not seconds … REMOVE the warm restart from the cap stall point … apply the certificate to refits. Certificate accepted as proposed: restart from the end point until a restart improves chi2 by less than the optimiser's own stopping tolerance; fixed restart count; out of restarts = 'not converged'. No new constant. Acceptance: identical output under light and heavy load; Scan_6 -> MG2." Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

TRY TO BREAK
a. Load independence: any remaining read of the clock (time.*, perf_counter, deadlines, budgets) that can change the OUTPUT of compare_models / run_stability_analysis / _attempt_proposal / fit_candidate / the bound-fixed override / the Bayesian method / app.py's analyze job; any count that depends on time.
b. The certificate (_certify_minimum): its tolerance is least_squares' own ftol read from scipy; the improvement is relative; restarts use least_squares (the plan explains why not leastsq); keeps the lowest-chi2 point; non-finite or raising restart = not converged; chi2 == 0; a restart that returns a HIGHER chi2; max_nfev per restart; interaction with lmfit's params (bounds, expressions), with covariance / stderr (NaN sigma now reaches the payload as null via _json_sanitize), with FitOutcome consumers (converged, lmfit_result, boundary_hits, components' supports).
c. Every former consumer of the success flag / warm restart / budgets now behaves correctly (screen convergence, deep primary reuse, stability refits, proposals, bound-fixed refits, persistence denominators).
d. The plan's measurements and §3 (the page's request on 7 scans: 3 winners differ from main — two via the screen's single-start ranking, one via the absent-slot BIC* credit): is the reasoning right; is anything there a blocker for shipping A1 as specified?
e. Tests: real and non-vacuous (the certificate tests; the clock-independence test).

Finish with VERDICT: GO or VERDICT: NO-GO.

ERROR: Reconnecting... 2/5
ERROR: Reconnecting... 3/5
ERROR: Reconnecting... 4/5
codex
I’ll trace the changed fit paths and their consumers, check the certificate’s failure cases, and assess whether the tests support the acceptance claims. I’ll keep this read-only and finish with a ranked review and verdict.

exec
/bin/zsh -lc 'pwd; git status --short; git diff --stat main..HEAD; rg --files -g AGENTS.md -g CLAUDE.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
CLAUDE.md

exec
/bin/zsh -lc "cat CLAUDE.md; cat docs/superpowers/plans/2026-09-29-a1-find-peaks-determinism.md; cat docs/findings/fit-termination-scope/README.md; ls -d .venv venv 2>/dev/null; rg -n 'time\\.|perf_counter|deadline|budget|\\.success|warm.restart|_certify_minimum|converged' autofit/engine.py app.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
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

### Find Peaks does not read the clock (unit A1, 2026-09-29)

Find Peaks' answer must not depend on server load or on the optimiser's own
termination flags. No wall-clock budget anywhere in `autofit/engine.py`
(the 25 s per-candidate, 240 s sweep, proposal and screen budgets are gone —
on 1-GTA C1s Scan_6 MG2 won or lost on whether its fourth refit started
before 25 s): every candidate is screened, `SCREEN_TOP_K` are evaluated with
exactly `n_refits` refits, and work is bounded by counts and evaluation caps.
A fit's convergence is CERTIFIED (`_certify_minimum`): Trust-Region restarts
from the end point until one improves chi2 by less than Trust-Region's own
ftol (scipy's default, no new constant), at most `CERTIFY_MAX_RESTARTS` = 50
(measured: 2 for most fits, 21 at most on the committed C 1s set); out of
restarts = not converged. The old warm restart from a failed fit's exit point
is gone (it met MINPACK's xtol at the stall and reported success). Under
light and heavy load every structural field of the output is identical; the
numbers carry Trust-Region's arithmetic jitter (≤ 0.25 meV, ≤ 5e-4 relative
amplitude, the same idle-to-idle). Plan:
`docs/superpowers/plans/2026-09-29-a1-find-peaks-determinism.md`.

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
# Unit A1 — Find Peaks determinism (2026-09-29)

Owner: "Find Peaks' answer must not depend on server load or on the
optimiser's own termination flags. Count refits, not seconds … Judge
convergence by whether the refit actually reached the minimum … no new
magnitude threshold. Acceptance: identical output under light and heavy
machine load, and Scan_6 returns MG2." Scope check first:
`docs/findings/fit-termination-scope/README.md` (Run Fit shares the flag
problem; its step is A2).

## 1. What changed (`autofit/engine.py`)

| site | before | after |
|---|---|---|
| `run_stability_analysis` | refits stopped at a 25 s per-candidate deadline (shared with the primary fit) | exactly `n_refits` refits, always |
| `compare_models` screen | stopped at 60 % of a 240 s sweep budget | every candidate screened |
| `compare_models` sweep | stopped starting candidates when 240 s − 25 s had elapsed | every selected candidate evaluated |
| proposal pass | 60 s pass budget, 35 s stability budget, 15 s minimum-fit refusals (`insufficient_budget`) | none — counted work only (≤ 3 accepted rounds × ≤ 3 attempts) |
| bound-fixed refit | 25 s deadline | `n_refits` refits |
| `fit_candidate` convergence | `leastsq`'s `success` flag; on a failed fit ONE warm restart from the exit point whose flag was taken | the CERTIFICATE (`_certify_minimum`); warm restart removed |

Removed constants: `CANDIDATE_TIMEOUT_SEC`, `TOTAL_ANALYSIS_TIMEOUT_SEC`,
`PROPOSAL_CANDIDATE_TIMEOUT_SEC`, `PROPOSAL_STABILITY_TIMEOUT_SEC`,
`PROPOSAL_MIN_FIT_BUDGET_SEC`, `SCREEN_BUDGET_FRACTION`, `WARM_RESTART_MAX_NFEV`.
The clock is read only for the proposal pass's `wall_time_sec` telemetry
(`proposal_pass_timings`, not in the payload). `analysis_truncated` /
`timed_out` are never set (kept for the payload's shape).

**The certificate** (owner-accepted as proposed): after the `leastsq` fit,
restart from its end point with Trust-Region (`least_squares`, native bounds);
repeat from each improved point until a restart improves chi2 by less than
Trust-Region's own `ftol` (1e-8, read from scipy's signature — no new
constant; relative, so scale-free); at most `CERTIFY_MAX_RESTARTS` = 50
restarts (a count); out of restarts or a non-finite restart = not converged.
Trust-Region, not Levenberg-Marquardt, restarts: an LM restart from a stall
point reproduces the stall (the removed warm restart is exactly that).

## 2. Measurements

**What the old "~30-evaluation convergence" was.** 8-JT C1s Scan_7, MG2,
stability refit 0: `leastsq` stalls at chi2 5220 (18 000 evaluations, flag
False); the warm restart met MINPACK's xtol in 30 evaluations and reported
success there. That point is NOT a minimum (a descent still lowers chi2 — the
KKT check in `tests/autofit/test_fit_certificate.py`). The certified point is
chi2 5166, a genuine CONSTRAINED LOCAL minimum (free gradients ~0, all ten
parameters on bounds pushing outward) — a worse basin than the chi2r 5.21
least_squares reaches from the same start along another path. Correction to
the scope report: "37.6 vs 5.21" was a bad basin, not a point far from a
minimum; "converged" is the right verdict for it now.

**Restarts needed** (8 committed C 1s scans × the 4 gate candidates,
primaries + all refits, 208 fits): 1: 10, 2: 173, 3: 14, 4: 5, then one each
at 5, 6, 8, 9, 11, 21 (flat valleys). With 5 allowed four real minima went
uncertified (8-JT Scan_5's MG2 and MG3 primaries → AG2 at chi2r 42.5 won); 50
certifies all 208. 75 fits `leastsq` flagged as FAILED were certified (capped
at a minimum — the Scan_6 case), none of 208 left uncertified.

**Acceptance — Scan_6.** Gate options: MG2 (chi2r 2.03), as main with budgets
off; main under load had given AG2.

**Acceptance — load.** The page's own request (conductor, C 1s, proposals on,
n_refits 4, endpoint average 3; full grammar, 29–30 candidates screened, 6
deep) on 1-GTA Scan_6 and 8-JT Scan_7, idle, idle again, and with 8 CPU
burners (load average 11):

| | structural fields (winner, tier, candidate set, filter reasons, persistence, ranks, peak roles) | max Δcentre | max rel Δamplitude | max Δarea % |
|---|---|---|---|---|
| idle vs idle | identical (both scans) | 0.20 meV | 3.9e-4 | 7.6e-4 pp |
| idle vs heavy | identical (both scans) | 0.24 meV | 4.9e-4 | 9.4e-4 pp |

The residual numeric differences are Trust-Region's arithmetic jitter (the
BLAS alignment effect CLAUDE.md records; owner decision 2026-09-21 accept and
disclose), present idle-to-idle — not load. Find Peaks used only the
byte-reproducible Levenberg-Marquardt before; the certificate's Trust-Region
restarts bring the jitter in. Wall time (page request, idle): main 208–213 s,
A1 236–239 s; under load A1 342–350 s (main would have truncated).

**Screen interaction (found here).** With every screen fit certified to a
genuine local minimum, the screen now compares honest minima — and MG2's
single screen start on 8-JT Scan_7 lands in a poor one (BIC* 2277, as on main)
while most others improve, so MG2 ranks 19th of 28 and is screened out,
though its deep evaluation reaches the best BIC* of all. Page request: main
MG2 (BIC* 1776.8) vs A1 MG3 (1787.6). Measurement on six more scans: §3.

## 3. The page's own Find Peaks request: main vs A1 (7 distinct committed C 1s scans, idle)

4 of 7 winners identical (UCl4 Scan_8, UCl4 Scan_3, 1-GTA Scan, 1-GTA Scan_6 —
the last MG2 on both). 3 differ:

| scan | main (winner, BIC*) | A1 (winner, BIC*) | why |
|---|---|---|---|
| 8-JT Scan_5 | MG2, 1882.6 | MG3, 1901.5 | MG2 SCREENED OUT on A1 (screen rank 21 of 28) — its single screen start lands in a poor local minimum while the certificate carries most other screen fits to much better ones |
| 8-JT Scan_7 | MG2, 1776.8 | MG3, 1787.6 | the same (MG2 screen rank 19 of 28) |
| 1-GTA Scan_2 | MG3, 1803.9 | MG2, 1816.0 | MG3 deep-evaluated on both with the SAME chi2r 1.388; on main one MG3 slot was "absent" (BIC* drops its parameters) because refits the old flag called non-converged counted as empty; certified, the slot is populated in every refit — no credit. A1 is the honest one here |

The two screen cases pick a model with a WORSE BIC* than main's. The screen's
single-start ranking is pre-existing; the certificate changes which candidates
it happens to favour. OWNER DECISION (see the report).
# Do fits stop before the minimum? Scope check for Unit A (2026-09-28)

Owner, Unit A: "Judge convergence by whether the refit actually reached the
minimum, not by the optimiser's success flag … SCOPE CHECK FIRST: does Run
Fit, or the scattered-starts check, share the ~30-evaluation early stopping?"

## Find Peaks: where the "~30 evaluations" comes from

It is not MINPACK stopping early from a cold start. `autofit.engine.fit_candidate`
fits with `leastsq`; when that fit FAILS (the 18 000-evaluation cap) it makes
ONE warm restart from the exit point with a 2 000-evaluation budget and takes
the restart's result if its `success` flag is set. From a stalled point that
restart ends on MINPACK's `xtol` test in ~30 evaluations and reports success.
Example (8-JT C1s Scan_7, MG2, stability refit 0): the cold `leastsq` fit stalls
at χ²ᵣ 37.6 after 18 000 evaluations; the warm restart "succeeds" there in 30;
`least_squares` from the same start reaches χ²ᵣ 5.21 in 507. The code comment
assumes the failed fit had already reached the minimum; here it had not.

## Run Fit and the scattered-starts check

`scripts/fit_termination_scope.py` runs every one of the 202 committed targets
through `/api/fit` exactly as the page sends it (3 perturbed restarts, 3
scattered starts), intercepts every lmfit fit, and refines each result from its
end point with a fresh `least_squares` fit (same model, data, weights, bounds).
A descent from a minimum cannot lower χ² beyond the optimiser's stopping sliver;
from a point short of it, it does. Summary: `scripts/fit_termination_scope_analyze.py`.

| (success-flagged fits; χ² drop on refinement) | Trust-Region (page default) | Levenberg-Marquardt |
|---|---|---|
| **the fit returned to the student** | 202: drop > 1e-6 on 8, > 1e-3 on 5, > 1 % on 2 (5.7 %, 3.8 %) | 196: > 1e-6 on 32, > 1 % on 5, > 10 % on 1 (26 %, 7205f2094254) |
| perturbed restarts | 498: > 10 % on 162 | 576: > 10 % on 198 |
| scattered starts | 532: > 10 % on 29 | 480: > 10 % on 17 |
| scattered starts flagged failed | 2 (0 at a minimum) | 36 (1 at a minimum) |

Consequences: the student's result stops short on 8 / 202 (TR) and 32 / 196
(LM) targets; the perturbed restarts often "succeed" far from a minimum (they
compete by χ², so a poor one loses — but the fit it would have found is lost);
a scattered start that "succeeds" short of its minimum is counted as reaching /
not beating the fit, so the panel's counts and alternatives are affected.

## What a certificate can and cannot be

A strict rule — "a fresh descent from the end point finds no lower χ²" — would
never certify: at genuine minima a restart almost always shaves off a sliver
(TR: of 1 232 success-flagged fits only 27 refine to exactly the same χ²; 513
drop by ≤ 1e-9, 362 by 1e-9 – 1e-6). The sliver is the optimiser's own stopping
rule at work (relative χ² change ftol: 1e-8 TR, 1.5e-8 LM). The only constant
that can separate "stopped at the minimum" from "stopped short" without
introducing a new one is that ftol itself — dimensionless, not data-scaled.
Measured with it: TR returned fits exceeding their own ftol on refinement 11 /
202; LM 88 / 196; all success-flagged fits 374 / 1 232 (TR), 888 / 1 252 (LM).
app.py:237:    cutoff = time.time() - SESSION_TTL_DAYS * 86400
app.py:442:            and not grammar.candidates and not res.success):
app.py:473:        "success": bool(res.success),
app.py:538:    cutoff = time.time() - _ANALYZE_JOB_TTL_SEC
app.py:618:    data["heartbeat_age_sec"] = round(time.time() - hb, 1) if isinstance(hb, (int, float)) else None
app.py:625:    cutoff = time.time() - _ANALYZE_JOB_TTL_SEC
app.py:648:    started = time.time()
app.py:661:            return time.time() - polled_path.stat().st_mtime > FIT_JOB_ABANDON_SEC
app.py:670:                rec["heartbeat"] = time.time()
app.py:671:                rec["elapsed_sec"] = round(time.time() - started, 1)
app.py:688:                        rec["heartbeat"] = time.time()
app.py:699:            rec["elapsed_sec"] = round(time.time() - started, 1)
app.py:700:            rec["heartbeat"] = time.time()
app.py:914:        # Reject non-.vgd before spending the upload budget / writing to disk
app.py:1185:        start_time = time.time()
app.py:1200:                "elapsed_sec": round(time.time() - start_time, 1),
app.py:1210:                    "elapsed_sec": round(time.time() - start_time, 1),
app.py:1217:                    "elapsed_sec": round(time.time() - start_time, 1),
app.py:1228:                    "elapsed_sec": round(time.time() - start_time, 1),
autofit/engine.py:129:# boundary cleanliness; same per-candidate wall budget).  Measured
autofit/engine.py:142:# Unit A1 (2026-09-29): NO wall-clock budget anywhere in the sweep. The
autofit/engine.py:143:# per-candidate 25 s, the 240 s sweep, the 60 s / 35 s proposal budgets, the
autofit/engine.py:144:# 15 s minimum-fit budget and the screen's share of the sweep all made Find
autofit/engine.py:216:# grammar at 25 s/candidate stability budgets + a 30-60 s proposal pass can
autofit/engine.py:217:# never finish inside the then 240 s sweep budget (removed in unit A1; it sat
autofit/engine.py:222:# converged screens by BIC, and runs the full pipeline (stability, proposal
autofit/engine.py:603:    converged: bool
autofit/engine.py:818:# of restarts, or a non-finite restart, is "not converged". No new constant:
autofit/engine.py:833:def _certify_minimum(composite, y_sub, result, x, weights, max_nfev):
autofit/engine.py:877:    investigation) showed a clean bimodal split: converged fits topped out
autofit/engine.py:880:    leastsq(), surfacing as result.success=False) cuts off the latter
autofit/engine.py:899:        # optimiser's flag (_certify_minimum). The old ONE warm restart from a
autofit/engine.py:902:        # non-minimum (8-JT C1s Scan_7: chi2r 37.6 "converged" where
autofit/engine.py:904:        result, certified = _certify_minimum(composite, y_sub, result, x, weights, max_nfev)
autofit/engine.py:908:            converged=False, components=[], residual_sum_sq=float("inf"),
autofit/engine.py:916:        # minimum — reported as not converged, whatever the optimiser's flag
autofit/engine.py:920:        converged=bool(certified),
autofit/engine.py:1133:    # Best converged refit found during the multi-start pass (by weighted χ²).
autofit/engine.py:1146:    # budget); the denominator of persistence / orphan_rate / convergence_rate.
autofit/engine.py:1173:    deadline. The 25 s per-candidate budget this replaced made persistence
autofit/engine.py:1184:    n_converged = 0
autofit/engine.py:1216:        if not outcome.converged:
autofit/engine.py:1218:        n_converged += 1
autofit/engine.py:1259:        convergence_rate=n_converged / max(n_attempted, 1),
autofit/engine.py:1579:    non_converged: list[tuple[CandidateModel, FitOutcome]] = field(default_factory=list)
autofit/engine.py:1607:    # Never set since unit A1 (the sweep budget it reported is gone: every
autofit/engine.py:1620:    # screen outcome: {name, converged, bic, selected} — screened-out
autofit/engine.py:1694:                  if r.primary_fit.converged
autofit/engine.py:2158:    # Unit A1 (2026-09-29): no wall-clock budget — an attempt either runs its
autofit/engine.py:2186:    if not primary.converged:
autofit/engine.py:2395:    if not outcome.converged:
autofit/engine.py:2638:            # the nfev cap (0 converged → no survivor).  Grammar families
autofit/engine.py:2677:                    # phase truncates under its wall budget on rich scans
autofit/engine.py:2679:                    # 21/30) — a budget truncation must never be able to
autofit/engine.py:2694:    non_converged: list[tuple[CandidateModel, FitOutcome]] = []
autofit/engine.py:2702:    #    deep-evaluation budget — every existing gate/battery path is ≤
autofit/engine.py:2709:        # Unit A1: EVERY candidate is screened (no wall-clock screen budget —
autofit/engine.py:2718:            if outcome.converged:
autofit/engine.py:2721:                screen_rows.append({"name": model.name, "converged": True,
autofit/engine.py:2724:                non_converged.append((model, outcome))
autofit/engine.py:2725:                screen_rows.append({"name": model.name, "converged": False,
autofit/engine.py:2741:        # Unit A1: every selected candidate is evaluated — no sweep budget
autofit/engine.py:2750:        if not primary.converged:
autofit/engine.py:2751:            non_converged.append((model, primary))
autofit/engine.py:2793:            # per-candidate wall budget.  Gates are unchanged per round.
autofit/engine.py:2796:            timed_out = False                 # unit A1: never set (no pass budget)
autofit/engine.py:2797:            pass_start = time.perf_counter()  # telemetry only (wall_time_sec)
autofit/engine.py:2855:                wall_time_sec=time.perf_counter() - pass_start, timed_out=timed_out,
autofit/engine.py:2876:    result.non_converged = non_converged

exec
/bin/zsh -lc 'git diff main..HEAD -- autofit/engine.py tests/autofit/test_fit_certificate.py tests/autofit/test_preseed_dominants.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-DHbbmih6' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-gO5X02kb' (errno=Operation not permitted)
diff --git a/autofit/engine.py b/autofit/engine.py
index dbf4fd7..65e2be0 100644
--- a/autofit/engine.py
+++ b/autofit/engine.py
@@ -134,59 +134,22 @@ PROPOSAL_AMPLITUDE_SNR = 5.0
 # keeps those guards and bounds the rounds.  UNVERIFIED tunable.
 PROPOSAL_MAX_PER_CANDIDATE = 3
 PROPOSAL_MAX_ATTEMPTS_PER_CANDIDATE = 3
-# Whole ITERATIVE proposal pass per candidate (all F2 rounds share it).
-# Raised 30 → 60 with F2: the pass may now legitimately do up to
-# PROPOSAL_MAX_PER_CANDIDATE accepted rounds of (augmented fit + stability).
-# UNVERIFIED tunable.
-PROPOSAL_CANDIDATE_TIMEOUT_SEC = 60.0
-# One augmented-model stability pass inside the proposal pass.  Replaces the
-# old min(budget, CANDIDATE_TIMEOUT_SEC) clamp, whose 25 s ceiling cut the
-# n_refits=4 stability of a slow augmented model to 3 attempts and QUANTIZED
-# the persistence gate below its threshold — measured on the real C 1s
-# motivating case (PROGRESS.md diagnosis follow-up): a ΔBIC* −86 proposal
-# with no boundary hits was rejected at persistence 2/3 = 0.67 < 0.70 purely
-# because the 4th refit never ran.  35 s fits n_refits=4 at the measured
-# ~7-8 s worst-case per refit on 191-point real data.  UNVERIFIED tunable.
-PROPOSAL_STABILITY_TIMEOUT_SEC = 35.0
-# Minimum budget (s) that must remain before an augmented-model FIT is
-# started inside the proposal pass.  A single fit_candidate at
-# FIT_CANDIDATE_MAX_NFEV runs ~10-12 s worst-case on 191-point data with no
-# internal wall clock, so starting one with less than this left would
-# overrun TOTAL_ANALYSIS_TIMEOUT_SEC — and hence the gunicorn --timeout
-# (Codex c1s-fix review, run B MAJOR).  A proposal attempt that cannot fit
-# this budget fast-rejects with 'insufficient_budget'.  UNVERIFIED tunable.
-PROPOSAL_MIN_FIT_BUDGET_SEC = 15.0
 
 # See fit_candidate() docstring: deterministic per-call ceiling on lmfit's
 # own effort, replacing its effectively-unbounded default.
 FIT_CANDIDATE_MAX_NFEV = 18000
-WARM_RESTART_MAX_NFEV = 2000     # single retry budget for a failed-but-
-                                 # finite fit (measured need: ~33 evals;
-                                 # generous headroom, still bounded)
-
-# Wall-clock ceiling on ONE candidate's entire primary-fit + stability-refit
-# pass (compare_models -> run_stability_analysis). Mirrors
-# PROPOSAL_CANDIDATE_TIMEOUT_SEC's existing per-candidate budget for the
-# later residual-proposal pass: a candidate that blows this budget stops
-# taking further stability refits rather than consuming the rest of the
-# request's time. FIT_CANDIDATE_MAX_NFEV already bounds any single call to
-# roughly 10-12s on this pipeline's DS+G cost profile, so this allows a
-# couple of such calls (primary + 1-2 refits) before cutting the rest.
-CANDIDATE_TIMEOUT_SEC = 25.0
-
-# Wall-clock ceiling on the ENTIRE compare_models sweep over all candidates
-# in the grammar. Per-candidate budgets (CANDIDATE_TIMEOUT_SEC,
-# PROPOSAL_CANDIDATE_TIMEOUT_SEC) bound any one candidate but not their sum
-# — a 29-candidate grammar at ~7s/candidate for ordinary (non-degenerate)
-# fits already runs ~3-4 minutes, and several candidates hitting the
-# DS+G-style degenerate corner push that further. Checked once per outer
-# loop iteration (compare_models): once exceeded, remaining candidates are
-# skipped and the sweep returns best-so-far, ranked normally, with
-# ComparisonResult.analysis_truncated=True — an honest partial result
-# instead of a request timeout. Deliberately below the gunicorn dev
-# --timeout so this truncation path always gets to run and respond before
-# the worker is aborted (see DEPLOY.md / dev gunicorn --timeout).
-TOTAL_ANALYSIS_TIMEOUT_SEC = 240.0
+
+# Unit A1 (2026-09-29): NO wall-clock budget anywhere in the sweep. The
+# per-candidate 25 s, the 240 s sweep, the 60 s / 35 s proposal budgets, the
+# 15 s minimum-fit budget and the screen's share of the sweep all made Find
+# Peaks' ANSWER depend on server load (1-GTA C1s Scan_6: MG2 won or lost on
+# whether its fourth refit started before 25 s). Work is bounded by counts:
+# every candidate is screened once, SCREEN_TOP_K are deep-evaluated with
+# n_refits refits each, a proposal pass makes at most
+# PROPOSAL_MAX_PER_CANDIDATE × PROPOSAL_MAX_ATTEMPTS_PER_CANDIDATE attempts,
+# every fit is capped at FIT_CANDIDATE_MAX_NFEV / SCREEN_MAX_NFEV evaluations
+# and certified with at most CERTIFY_MAX_RESTARTS restarts. The page runs
+# Find Peaks as a polled job (/api/analyze/start), so no request waits on it.
 PROPOSAL_ENDPOINT_WARNING_BE = 1.0
 PROPOSAL_COINCIDENCE_BE = 0.5
 
@@ -251,8 +214,8 @@ GRAMMAR_AUGMENT_MAX_SEEDS = 3        # of those, at most this many augment
 # ── Two-phase sweep: screen → stabilize (unit F3, 2026-07-07) ──────────────
 # Measured motivation (PROGRESS.md diagnosis, cause a): a 29-candidate C 1s
 # grammar at 25 s/candidate stability budgets + a 30-60 s proposal pass can
-# never finish inside TOTAL_ANALYSIS_TIMEOUT_SEC (240 s, deliberately below
-# the gunicorn --timeout 300) — the real spectra truncated at 8/29 with the
+# never finish inside the then 240 s sweep budget (removed in unit A1; it sat
+# below the gunicorn --timeout 300) — the real spectra truncated at 8/29 with the
 # expert-structure MG family (candidates #21-24) never evaluated.  When the
 # candidate set is larger than SCREEN_TOP_K, compare_models first fits EVERY
 # candidate once (primary fit only, SCREEN_MAX_NFEV effort cap), ranks the
@@ -269,10 +232,6 @@ SCREEN_MAX_NFEV = 6000     # measured: converging primaries on real 191-pt
                            # C 1s data use 3-5k evals; hopeless landscapes
                            # burn ≥ 18k without converging
 SCREEN_TOP_K = 6
-# The screen may spend at most this fraction of TOTAL_ANALYSIS_TIMEOUT_SEC —
-# the deep phase must always retain budget, else a very large (joint) grammar
-# could burn the whole sweep screening and deep-evaluate NOTHING.
-SCREEN_BUDGET_FRACTION = 0.6
 
 
 def _slot_prefix(role: str) -> str:
@@ -849,6 +808,53 @@ def _unphysical_width_flags(
     return flags
 
 
+# ── Convergence certificate (unit A1, 2026-09-29) ─────────────────────────────
+# A fit has reached a minimum when a fresh descent from its end point cannot
+# improve chi2 by more than the descent's OWN stopping tolerance. The descent
+# is Trust-Region (scipy least_squares, native bounds): a Levenberg-Marquardt
+# restart from a stall point reproduces the stall (MINPACK's xtol test fires in
+# ~30 evaluations — the false convergence this replaces). Restarts are repeated
+# from each improved point; a FIXED number of them (a count, not a time); out
+# of restarts, or a non-finite restart, is "not converged". No new constant:
+# the tolerance is scipy's own least_squares ftol default, read from its
+# signature, and the improvement is relative (dimensionless, scale-free).
+import inspect as _inspect
+import scipy.optimize as _scipy_optimize
+CERTIFY_FTOL = float(_inspect.signature(_scipy_optimize.least_squares).parameters["ftol"].default)
+# A COUNT, set from measurement (unit A1, 8 committed C 1s scans × 4 gate
+# candidates, primaries + all refits = 208 fits): restarts needed to certify —
+# 1: 10, 2: 173, 3: 14, 4: 5, then one fit each at 5, 6, 8, 9, 11 and 21 (flat
+# valleys: each Trust-Region run stops on its own ftol while a whole restart
+# still gains more than that). 5 left four real minima uncertified (8-JT
+# Scan_5's MG2 and MG3 primaries, so MG lost to AG2 at chi2r 42.5).
+CERTIFY_MAX_RESTARTS = 50
+
+
+def _certify_minimum(composite, y_sub, result, x, weights, max_nfev):
+    """Return (the lowest-chi2 point reached, certified)."""
+    current = result
+    chi = float(result.chisqr) if result.chisqr is not None else float("nan")
+    if not np.isfinite(chi):
+        return current, False
+    for _ in range(CERTIFY_MAX_RESTARTS):
+        try:
+            r = composite.fit(y_sub, current.params.copy(), x=x, weights=weights,
+                              method="least_squares", nan_policy="omit",
+                              max_nfev=max_nfev)
+        except Exception as exc:
+            log.debug("certificate restart raised: %s", exc)
+            return current, False
+        new = float(r.chisqr) if r.chisqr is not None else float("nan")
+        if not np.isfinite(new):
+            return current, False
+        improvement = (chi - new) / chi if chi > 0 else 0.0
+        if new < chi:
+            current, chi = r, new
+        if improvement < CERTIFY_FTOL:
+            return current, True
+    return current, False
+
+
 def fit_candidate(
     x: np.ndarray,
     y: np.ndarray,
@@ -889,25 +895,13 @@ def fit_candidate(
         result = composite.fit(y_sub, params, x=x, weights=weights,
                                method="leastsq", nan_policy="omit",
                                max_nfev=max_nfev)
-        if (not result.success and result.chisqr is not None
-                and np.isfinite(result.chisqr)):
-            # ONE warm restart (Stage-2, measured on the real diagnosis
-            # scans): a model whose optimum sits against parameter bounds
-            # stalls MINPACK on a flat transformed gradient — it reaches
-            # the minimum, then burns the whole nfev budget without
-            # satisfying ftol (success=False at a genuinely converged
-            # χ²).  Restarting AT the exit point resets leastsq's internal
-            # diag scaling and it certifies in tens of evaluations
-            # (measured: 6000 nfev burned cold → 33 nfev warm, identical
-            # χ²).  Fires ONLY on a failed-but-finite fit, so converging
-            # fits are byte-identical; cost is bounded by one
-            # WARM_RESTART_MAX_NFEV fit.
-            retry = composite.fit(y_sub, result.params.copy(), x=x,
-                                  weights=weights, method="leastsq",
-                                  nan_policy="omit",
-                                  max_nfev=WARM_RESTART_MAX_NFEV)
-            if retry.success:
-                result = retry
+        # Unit A1 (2026-09-29): convergence is CERTIFIED, not read from the
+        # optimiser's flag (_certify_minimum). The old ONE warm restart from a
+        # failed fit's exit point is gone: from a stall point MINPACK's restart
+        # satisfies xtol in ~30 evaluations and reported success at a
+        # non-minimum (8-JT C1s Scan_7: chi2r 37.6 "converged" where
+        # least_squares from the same start reaches 5.21).
+        result, certified = _certify_minimum(composite, y_sub, result, x, weights, max_nfev)
     except Exception as exc:
         log.debug("fit_candidate failed for %s: %s", model.name, exc)
         return FitOutcome(
@@ -917,9 +911,13 @@ def fit_candidate(
             n_data=len(y_sub), lmfit_result=None, background=bg,
         )
 
+    if not certified:
+        # out of restarts (or a non-finite restart): the fit did not reach a
+        # minimum — reported as not converged, whatever the optimiser's flag
+        log.debug("fit_candidate: %s not certified", model.name)
     unweighted_r = y_sub - result.best_fit
     return FitOutcome(
-        converged=bool(result.success),
+        converged=bool(certified),
         components=_extract_fitted_components(result, model),
         residual_sum_sq=float(np.sum(unweighted_r ** 2)),
         weighted_chi_sq=float(result.chisqr) if result.chisqr is not None else float("inf"),
@@ -1144,11 +1142,9 @@ class ModelStability:
     # one-off deeper minimum is a different product than a reproducible one).
     # Reporting-only; never used in ranking.
     best_basin_support: int = 0
-    # How many of the requested n_refits were actually attempted before the
-    # candidate's wall-clock budget (CANDIDATE_TIMEOUT_SEC) ran out. Equal to
-    # n_refits unless timed_out is True — used as the honest denominator for
-    # persistence/orphan_rate/convergence_rate instead of silently
-    # understating them against the full nominal n_refits.
+    # Refits attempted — always n_refits since unit A1 (no wall-clock
+    # budget); the denominator of persistence / orphan_rate / convergence_rate.
+    # timed_out is never set (kept for the payload's shape).
     n_attempted: int = 0
     timed_out: bool = False
 
@@ -1169,16 +1165,16 @@ def run_stability_analysis(
     n_refits: int = 20,
     rng_seed: int = 0,
     fixed_param_values: Optional[dict[str, float]] = None,
-    deadline: Optional[float] = None,
     fit_full_window: bool = False,
     endpoint_avg: int = 1,
 ) -> ModelStability:
     """
-    ``deadline`` is an absolute ``time.perf_counter()`` timestamp (set by
-    the caller from CANDIDATE_TIMEOUT_SEC) shared across this candidate's
-    primary fit + all its refits. Once passed, remaining refits are
-    skipped — not run and not counted as failures — so one candidate stuck
-    in a slow-but-nfev-capped region can't consume the rest of the request.
+    Unit A1 (2026-09-29): exactly ``n_refits`` refits, always — no wall-clock
+    deadline. The 25 s per-candidate budget this replaced made persistence
+    (refits reached / refits attempted) depend on server load: on 1-GTA C1s
+    Scan_6 MG2 got 3 or 4 refits depending on how busy the machine was, and
+    2/3 vs 3/4 decided the winner. Work is bounded by counts (n_refits, each
+    fit's max_nfev, the certificate's restarts).
     """
     rng = np.random.default_rng(rng_seed)
     pos: dict[str, list[float]] = {s.role: [] for s in model.slots}
@@ -1205,14 +1201,6 @@ def run_stability_analysis(
     n_attempted = 0
     timed_out = False
     for _ in range(n_refits):
-        if deadline is not None and time.perf_counter() >= deadline:
-            timed_out = True
-            log.warning(
-                "run_stability_analysis: candidate %s hit its %.0fs budget "
-                "after %d/%d refits — remaining refits skipped",
-                model.name, CANDIDATE_TIMEOUT_SEC, n_attempted, n_refits,
-            )
-            break
         n_attempted += 1
         seed = int(rng.integers(0, 2**31 - 1))
         init = perturb_initial_params(model, seed=seed, x=x, y_net=y_net,
@@ -1616,11 +1604,9 @@ class ComparisonResult:
     # weighted_bic_top, note} or None (BIC/IC math review blocker:
     # selection must not silently rest on a likelihood the fits reject).
     weighted_ic_disagreement: Optional[dict] = None
-    # Set when the sweep hit TOTAL_ANALYSIS_TIMEOUT_SEC and stopped before
-    # evaluating every candidate in the grammar. The candidates evaluated so
-    # far are still ranked/reported normally (best-so-far) — this only flags
-    # that the comparison is partial, so a slow/pathological spectrum
-    # returns an honest incomplete result instead of a request timeout.
+    # Never set since unit A1 (the sweep budget it reported is gone: every
+    # candidate is evaluated); kept so the payload and the page keep their
+    # shape.
     analysis_truncated: bool = False
     n_candidates_evaluated: int = 0
     n_candidates_total: int = 0
@@ -2166,11 +2152,12 @@ def _attempt_proposal(
     absent_slot_area_fraction: float,
     absent_slot_persistence_threshold: float,
     diagnostic_windows: dict[str, tuple[float, float]],
-    budget_remaining: float = float("inf"),
     fit_full_window: bool = False,
     endpoint_avg: int = 1,
 ) -> tuple[Optional[ModelReport], ProposedPeakReport, str]:
-    attempt_start = time.perf_counter()
+    # Unit A1 (2026-09-29): no wall-clock budget — an attempt either runs its
+    # counted work (one augmented fit, n_refits refits) or is rejected on a
+    # data criterion; whether a proposal is accepted must not depend on load.
     base_model = base_report.model
     base_fit = base_report.primary_fit
     aug_model = _augmented_candidate(base_model, spec)
@@ -2187,16 +2174,6 @@ def _attempt_proposal(
         pr.rejection_reason = reason
         return None, pr, "fast_rejected"
 
-    # An augmented fit_candidate has no internal wall clock and runs
-    # ~10-12 s worst-case; starting one with less than PROPOSAL_MIN_FIT_
-    # BUDGET_SEC of sweep budget left would overrun TOTAL_ANALYSIS_TIMEOUT_SEC
-    # and the gunicorn --timeout (Codex c1s-fix review, run B MAJOR).  The
-    # caller passes budget_remaining = min(pass budget, sweep budget) left.
-    if budget_remaining < PROPOSAL_MIN_FIT_BUDGET_SEC:
-        return _fast(
-            f"insufficient_budget: {budget_remaining:.1f}s left < "
-            f"{PROPOSAL_MIN_FIT_BUDGET_SEC:.0f}s needed for one augmented fit")
-
     bg = _compute_background(x, y, aug_model.background, endpoint_avg=endpoint_avg)
     try:
         init = _initial_params_for_augmented(aug_model, base_fit, spec, x, y - bg,
@@ -2251,28 +2228,9 @@ def _attempt_proposal(
             f"base BIC* {base_report.bic_adjusted:.2f} by {PROPOSAL_DELTABIC_THRESHOLD:.1f}"
         )
 
-    # budget_remaining was a snapshot BEFORE the augmented fit; that fit has
-    # since consumed wall time, so the stability deadline must be computed
-    # from what's ACTUALLY left, not the stale snapshot (Codex c1s-fix
-    # review, run B MAJOR — otherwise the stability pass could run
-    # min(stale_budget, 35) s past the fit and overrun the sweep budget).
-    # The floor (not just <= 0) matters because run_stability_analysis
-    # checks its deadline at the TOP of the loop and then runs an unbounded
-    # fit_candidate — so starting stability with only a few seconds left
-    # would still overrun by ~one worst-case fit (Codex c1s-fix RE-CHECK,
-    # run B MAJOR: disposition 2 was not fully closed by the top guard).
-    remaining = budget_remaining - (time.perf_counter() - attempt_start)
-    if remaining < PROPOSAL_MIN_FIT_BUDGET_SEC:
-        pr.rejection_reason = (
-            f"insufficient_budget before stability: {remaining:.1f}s left < "
-            f"{PROPOSAL_MIN_FIT_BUDGET_SEC:.0f}s (one refit could overrun)")
-        return None, pr, "fast_rejected"
-
     stability = run_stability_analysis(
         x, y, weights, aug_model, primary,
         noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
-        deadline=time.perf_counter() + min(remaining,
-                                           PROPOSAL_STABILITY_TIMEOUT_SEC),
         fit_full_window=fit_full_window,
         endpoint_avg=endpoint_avg,
     )
@@ -2445,7 +2403,6 @@ def _bound_fixed_refit(
         x, y, weights, report.model, outcome,
         noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
         fixed_param_values=fixed,
-        deadline=time.perf_counter() + CANDIDATE_TIMEOUT_SEC,
         fit_full_window=fit_full_window,
         endpoint_avg=endpoint_avg,
     )
@@ -2738,7 +2695,6 @@ def compare_models(
     proposal_attempts: list[tuple[str, ProposedPeakReport]] = []
     timings: list[ProposalPassTiming] = []
     n_cand = len(candidates)
-    sweep_start = time.perf_counter()
     n_evaluated = 0
     analysis_truncated = False
 
@@ -2750,16 +2706,9 @@ def compare_models(
     if n_cand > SCREEN_TOP_K:
         screen_rows: list[dict] = []
         screened: list[tuple[CandidateModel, FitOutcome, float]] = []
-        screen_deadline = sweep_start + SCREEN_BUDGET_FRACTION * TOTAL_ANALYSIS_TIMEOUT_SEC
+        # Unit A1: EVERY candidate is screened (no wall-clock screen budget —
+        # which candidates reached the deep phase used to depend on load)
         for idx, model in enumerate(candidates, 1):
-            if time.perf_counter() > screen_deadline:
-                analysis_truncated = True
-                log.warning(
-                    "compare_models: screen budget (%.0f%% of the sweep) "
-                    "exhausted after %d/%d candidates — the deep phase runs "
-                    "on what screened so far",
-                    100 * SCREEN_BUDGET_FRACTION, idx - 1, n_cand)
-                break
             log.info("[screen %2d/%d] %s", idx, n_cand, model.name)
             _report_progress(progress_cb, "screening", idx, n_cand, model.name)
             outcome = fit_candidate(x, y, weights, model,
@@ -2789,30 +2738,11 @@ def compare_models(
             [m.name for m in candidates])
 
     for idx, model in enumerate(candidates, 1):
-        # Pre-check with the candidate's own worst-case budget: a candidate
-        # STARTED just under the wire used to overshoot the sweep budget by
-        # its full stability + proposal cost (measured 310 s wall vs the
-        # 240 s budget on real data — past the gunicorn --timeout 300, i.e.
-        # the exact worker-kill this budget exists to prevent).  Truncating
-        # BEFORE starting a candidate that cannot finish keeps the worst-case
-        # wall ≈ TOTAL_ANALYSIS_TIMEOUT_SEC.
-        elapsed = time.perf_counter() - sweep_start
-        if elapsed > TOTAL_ANALYSIS_TIMEOUT_SEC - CANDIDATE_TIMEOUT_SEC:
-            analysis_truncated = True
-            log.warning(
-                "compare_models: sweep budget cannot fit another candidate "
-                "(%.0fs elapsed of %.0fs) after %d/%d — remaining candidates "
-                "skipped, returning best-so-far",
-                elapsed, TOTAL_ANALYSIS_TIMEOUT_SEC, n_evaluated, len(candidates),
-            )
-            break
+        # Unit A1: every selected candidate is evaluated — no sweep budget
         n_evaluated += 1
         log.info("[%2d/%d] %s: primary fit", idx, len(candidates), model.name)
         _report_progress(progress_cb, "stabilizing", idx, len(candidates),
                          model.name)
-        # Shared wall-clock budget for this candidate's primary fit + all its
-        # stability refits (CANDIDATE_TIMEOUT_SEC) — see run_stability_analysis.
-        candidate_deadline = time.perf_counter() + CANDIDATE_TIMEOUT_SEC
         # reuse the screen fit as this candidate's primary (no repeated work)
         primary = screen_fit.get(model.name) or fit_candidate(
             x, y, weights, model, fit_full_window=fit_full_window,
@@ -2824,7 +2754,6 @@ def compare_models(
         stability = run_stability_analysis(
             x, y, weights, model, primary,
             noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
-            deadline=candidate_deadline,
             fit_full_window=fit_full_window,
             endpoint_avg=endpoint_avg,
         )
@@ -2864,20 +2793,12 @@ def compare_models(
             # per-candidate wall budget.  Gates are unchanged per round.
             counts = dict(n_flagged=0, n_over_cap=0, n_attempted=0,
                           n_fast=0, n_stab=0, n_acc=0)
-            timed_out = False
-            pass_start = time.perf_counter()
-            # the pass never spends beyond the sweep's remaining budget —
-            # same worst-case-wall reasoning as the candidate pre-check
-            pass_budget = min(
-                PROPOSAL_CANDIDATE_TIMEOUT_SEC,
-                TOTAL_ANALYSIS_TIMEOUT_SEC - (pass_start - sweep_start))
+            timed_out = False                 # unit A1: never set (no pass budget)
+            pass_start = time.perf_counter()  # telemetry only (wall_time_sec)
             rejected: list[ProposedPeakReport] = []
             current = base_report
             current_y_fit = y_fit
             while counts["n_acc"] < PROPOSAL_MAX_PER_CANDIDATE:
-                if time.perf_counter() - pass_start > pass_budget:
-                    timed_out = True
-                    break
                 specs = _detect_residual_proposals(
                     x, y, current_y_fit, noise_floor, current.model,
                     fitted_components=current.primary_fit.components,
@@ -2894,10 +2815,6 @@ def compare_models(
                 counts["n_over_cap"] += max(len(specs) - len(attempts), 0)
                 accepted_this_round = False
                 for spec in attempts:
-                    elapsed = time.perf_counter() - pass_start
-                    if elapsed > pass_budget:
-                        timed_out = True
-                        break
                     counts["n_attempted"] += 1
                     aug_report, pr, outcome = _attempt_proposal(
                         x=x, y=y, weights=weights, base_report=current, spec=spec,
@@ -2905,7 +2822,6 @@ def compare_models(
                         absent_slot_area_fraction=absent_slot_area_fraction,
                         absent_slot_persistence_threshold=absent_slot_persistence_threshold,
                         diagnostic_windows=diagnostic_windows,
-                        budget_remaining=pass_budget - elapsed,
                         fit_full_window=fit_full_window,
                         endpoint_avg=endpoint_avg,
                     )
diff --git a/tests/autofit/test_fit_certificate.py b/tests/autofit/test_fit_certificate.py
new file mode 100644
index 0000000..950ac4d
--- /dev/null
+++ b/tests/autofit/test_fit_certificate.py
@@ -0,0 +1,137 @@
+"""Unit A1 (2026-09-29): Find Peaks judges convergence by a CERTIFICATE, not the
+optimiser's flag. A fit has reached a minimum when a fresh Trust-Region descent
+from its end point improves chi2 by less than that descent's own stopping
+tolerance (scipy least_squares' ftol); restarts repeat from each improved point
+up to CERTIFY_MAX_RESTARTS; out of restarts = not converged. The flag was wrong
+both ways: a warm restart from a stall "succeeded" in ~30 evaluations at
+chi2r 37.6 where the minimum is 5.21 (8-JT C1s Scan_7), and a refit capped at
+18 000 evaluations AT the minimum counted as failed (1-GTA C1s Scan_6)."""
+import inspect
+import os
+
+import numpy as np
+import pytest
+import scipy.optimize
+
+import autofit.engine as eng
+from autofit.grammar import MaterialClass, Phase, resolve
+from autofit.methods.base import poisson_like_weights
+from autofit.reference import load_reference_fits
+
+DATA = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "autofit", "test_data")
+G = resolve([Phase(id="graphite", material_class=MaterialClass.CONDUCTOR, regions=("C 1s",), material="graphite")], "C 1s")
+
+
+def _scan(project, name):
+    rf = next(r for r in load_reference_fits(os.path.join(DATA, project)) if r.name == name)
+    x, y = np.asarray(rf.roi_be, float), np.asarray(rf.roi_intensity, float)
+    return x, y, poisson_like_weights(y)
+
+
+def _mg2():
+    return next(c for c in G.candidates if c.name == "MG2_graphAsymGL_aliph_sat_CO_C=O")
+
+
+def test_the_tolerance_is_the_optimisers_own():
+    assert eng.CERTIFY_FTOL == inspect.signature(scipy.optimize.least_squares).parameters["ftol"].default
+    assert isinstance(eng.CERTIFY_MAX_RESTARTS, int) and eng.CERTIFY_MAX_RESTARTS >= 1
+
+
+def _kkt_violations(comp, params, x, y_net, w):
+    """Parameters along which chi2 still descends: a free parameter with a
+    non-negligible gradient, or one on a bound whose gradient points INTO the
+    box. Empty = a (constrained) local minimum."""
+    chi = lambda pp: float(np.sum(((y_net - comp.eval(pp, x=x)) * w) ** 2))
+    c0, bad = chi(params), []
+    for n, p in params.items():
+        if not p.vary or p.expr is not None:
+            continue
+        span = (p.max - p.min) if np.isfinite(p.max) and np.isfinite(p.min) else (abs(p.value) or 1.0)
+        h = 1e-6 * span
+        q = params.copy()
+        if p.value - p.min < 1e-9 * span:
+            q[n].set(value=p.value + h)
+            if chi(q) < c0 - 1e-9 * c0: bad.append(n)
+        elif p.max - p.value < 1e-9 * span:
+            q[n].set(value=p.value - h)
+            if chi(q) < c0 - 1e-9 * c0: bad.append(n)
+        else:
+            q[n].set(value=p.value + h); cp = chi(q); q[n].set(value=p.value - h); cm = chi(q)
+            if abs(cp - cm) / (2 * h) * span > 1e-3 * c0: bad.append(n)
+    return bad
+
+
+def test_a_stall_now_ends_at_a_constrained_local_minimum():
+    """Scan_7 MG2, stability refit 0's start. The removed warm restart
+    reported success at the leastsq stall point (chi2 5220), which is NOT a
+    minimum: a descent still lowers chi2. The certified point satisfies the
+    KKT conditions (free gradients ~0, every parameter on a bound pushing out):
+    a genuine local minimum, pinned on bounds (chi2r ~37 — a worse basin than
+    the 5.21 least_squares finds from the same start by another path)."""
+    x, y, w = _scan("8-JT Graphite.proj.zip", "C1s Scan_7")
+    model = _mg2()
+    primary = eng.fit_candidate(x, y, w, model)
+    y_net = y - primary.background
+    seed = int(np.random.default_rng(0).integers(0, 2**31 - 1))
+    init = eng.perturb_initial_params(model, seed=seed, x=x, y_net=y_net)
+    comp = eng._build_composite_model(model)
+    stall = comp.fit(y_net, init.copy(), x=x, weights=w, method="leastsq", nan_policy="omit",
+                     max_nfev=eng.FIT_CANDIDATE_MAX_NFEV)
+    assert _kkt_violations(comp, stall.params, x, y_net, w), "the stall point is not a minimum"
+    out = eng.fit_candidate(x, y, w, model, initial_params=init.copy())
+    assert out.converged
+    assert out.weighted_chi_sq < stall.chisqr
+    assert _kkt_violations(comp, out.lmfit_result.params, x, y_net, w) == []
+
+
+def _two_peak():
+    x = np.arange(280.0, 292.0, 0.05)
+    t = 500 + 8000 * np.exp(-4 * np.log(2) * ((x - 284.5) / 1.0) ** 2) + 1500 * np.exp(-4 * np.log(2) * ((x - 286.4) / 1.2) ** 2)
+    y = t + np.sqrt(t) * np.random.default_rng(5).standard_normal(x.size)
+    slot = lambda r, win: eng.ComponentSlot(role=r, region="C 1s", phase_id="p", be_window=win,
+                                            line_shape=eng.LineShape.GAUSSIAN, fwhm_range=(0.5, 2.5))
+    model = eng.CandidateModel(name="m", background=eng.BackgroundType.LINEAR,
+                               slots=(slot("a", (284.0, 285.0)), slot("b", (286.0, 287.0))))
+    return x, y, poisson_like_weights(y), model
+
+
+def test_a_fit_capped_at_the_minimum_is_certified():
+    """The Scan_6 case in general form: an optimiser that runs out of
+    evaluations while sitting at the minimum reports failure; the certificate
+    finds no descent and certifies it."""
+    x, y, w, model = _two_peak()
+    good = eng.fit_candidate(x, y, w, model)
+    assert good.converged
+    comp = eng._build_composite_model(model)
+    y_sub = y - good.background
+    capped = comp.fit(y_sub, good.lmfit_result.params.copy(), x=x, weights=w, method="leastsq",
+                      nan_policy="omit", max_nfev=3)          # starts AT the minimum, capped at once
+    assert not capped.success
+    point, certified = eng._certify_minimum(comp, y_sub, capped, x, w, eng.FIT_CANDIDATE_MAX_NFEV)
+    assert certified
+    assert point.chisqr == pytest.approx(good.weighted_chi_sq, rel=1e-6)
+
+
+def test_out_of_restarts_is_not_converged(monkeypatch):
+    """A start far from the minimum needs more than one restart to certify
+    (the first descends a long way); with a single restart allowed it is
+    'not converged' — whatever the optimiser says."""
+    x, y, w, model = _two_peak()
+    comp = eng._build_composite_model(model)
+    good = eng.fit_candidate(x, y, w, model)
+    y_sub = y - good.background
+    far = good.lmfit_result.params.copy()
+    far["s_a_center"].set(value=284.05); far["s_b_amplitude"].set(value=50.0); far["s_a_fwhm"].set(value=2.3)
+    short = comp.fit(y_sub, far, x=x, weights=w, method="leastsq", nan_policy="omit", max_nfev=2)
+    monkeypatch.setattr(eng, "CERTIFY_MAX_RESTARTS", 1)
+    _, certified = eng._certify_minimum(comp, y_sub, short, x, w, eng.FIT_CANDIDATE_MAX_NFEV)
+    assert not certified
+    monkeypatch.setattr(eng, "CERTIFY_MAX_RESTARTS", 5)
+    point, certified = eng._certify_minimum(comp, y_sub, short, x, w, eng.FIT_CANDIDATE_MAX_NFEV)
+    assert certified and point.chisqr == pytest.approx(good.weighted_chi_sq, rel=1e-6)
+
+
+def test_the_warm_restart_is_gone():
+    src = inspect.getsource(eng.fit_candidate)
+    assert "retry" not in src and "WARM_RESTART" not in src
+    assert "converged=bool(certified)" in src
diff --git a/tests/autofit/test_preseed_dominants.py b/tests/autofit/test_preseed_dominants.py
index 74ec475..596c3a6 100644
--- a/tests/autofit/test_preseed_dominants.py
+++ b/tests/autofit/test_preseed_dominants.py
@@ -345,8 +345,7 @@ def test_proposal_rejected_when_stability_promotes_spurious_center_peg(monkeypat
         x=x, y=y, weights=w, base_report=base, spec=spec,
         noise_floor=1.0, n_refits=2, rng_seed=0,
         absent_slot_area_fraction=0.02, absent_slot_persistence_threshold=0.7,
-        diagnostic_windows=dict(case.grammar.diagnostic_windows),
-        budget_remaining=1e6)
+        diagnostic_windows=dict(case.grammar.diagnostic_windows))
     assert outcome == "stability_rejected"
     assert "post-stability" in (pr.rejection_reason or "")
     assert any("center@min" in h for h in pr.boundary_hits)
@@ -418,80 +417,30 @@ def test_next_proposal_index_is_max_suffix_plus_one():
     assert eng._next_proposal_index(m0) == 0
 
 
-def test_proposal_pass_respects_sweep_budget(monkeypatch):
-    """Codex c1s-fix MAJOR (run B): an augmented fit has no internal wall
-    clock, so a proposal attempt must fast-reject when too little sweep
-    budget remains rather than running an unbounded fit past the total
-    timeout.  With the fit-budget floor raised above any real remaining
-    budget, EVERY proposal attempt must be 'insufficient_budget' — no
-    augmented fit runs, no proposal is accepted, and the sweep still
-    returns cleanly."""
-    monkeypatch.setattr(eng, "PROPOSAL_MIN_FIT_BUDGET_SEC", 10_000.0)
+def test_no_wall_clock_can_change_the_answer(monkeypatch):
+    """Unit A1 (2026-09-29): the sweep, screen, stability and proposal
+    budgets were wall-clock and made the answer depend on server load; they
+    are gone. A clock that jumps a million seconds on every read must leave
+    the result IDENTICAL."""
     x = _grid()
     truth = [{"center": 196.5, "fwhm": 1.2, "height": 9000.0},
              {"center": 201.5, "fwhm": 1.2, "height": 2500.0}]
     sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
     y = _noisy(sig + _linear_bg(x), 71)
-    cands = [_cand("single_main", [_slot("main_a", (195.5, 197.5))])]
-    grammar = _grammar(cands)
-    res = get_method("ic_model_comparison").run(
-        x, y, grammar=grammar,
-        options={**IC_OPTS, "enable_preseed": False})
-    assert not res.diagnostics["winner"].endswith("+prop")
-    reasons = [p["rejection_reason"] for c in res.analysis["candidates"]
-               for p in c.get("proposed_peaks", [])]
-    assert reasons, "expected at least one attempted-then-rejected proposal"
-    assert all("insufficient_budget" in (r or "") for r in reasons), reasons
-
-
-def test_stability_not_started_without_budget_after_augmented_fit(monkeypatch):
-    """Codex c1s-fix RE-CHECK (run B): the top budget guard alone did NOT
-    close the overrun — an augmented fit that PASSES the top guard then
-    consumes most of the budget must not let run_stability_analysis start
-    an unbounded refit with only a few seconds left.  The pre-stability
-    guard now fast-rejects when the DYNAMIC remaining budget is below the
-    fit floor.  Deterministic via a fake clock: attempt_start = 1000 s,
-    every later perf_counter reads 1013 s, so with budget_remaining=20 the
-    post-fit remaining is 7 s < 15 s floor — stability must NOT run."""
-    from autofit.methods.base import poisson_like_weights
-    from stress_cases import isolated_missing_peak_case
+    grammar = _grammar([_cand("single_main", [_slot("main_a", (195.5, 197.5))])])
 
-    case = isolated_missing_peak_case(seed=71)
-    x, y = case.x, case.y
-    w = poisson_like_weights(y)
-    model = case.grammar.candidates[0]
-    # real base report (unpatched clock), proposal + preseed off
-    res = eng.compare_models(x, y, w, case.grammar, n_refits=2, rng_seed=0,
-                             enable_proposal_pass=False, enable_preseed=False)
-    base_report = res.reports[0]
-    y_fit = (base_report.primary_fit.lmfit_result.best_fit
-             + base_report.primary_fit.background)
-    specs = eng._detect_residual_proposals(
-        x, y, y_fit, 1.0, model,
-        fitted_components=base_report.primary_fit.components)
-    assert specs, "expected a residual proposal at the unmodeled peak"
-
-    calls = {"n": 0}
+    def run():
+        res = get_method("ic_model_comparison").run(x, y, grammar=grammar, options={**IC_OPTS, "enable_preseed": False})
+        return res.diagnostics, res.peaks, res.analysis, res.confidence
 
-    def fake_pc():
-        calls["n"] += 1
-        return 1000.0 + (0.0 if calls["n"] == 1 else 13.0)
+    normal = run()
+    ticks = {"t": 0.0}
 
-    def boom(*a, **k):
-        raise AssertionError("run_stability_analysis started without budget")
-
-    monkeypatch.setattr(eng.time, "perf_counter", fake_pc)
-    monkeypatch.setattr(eng, "run_stability_analysis", boom)
-
-    aug_report, pr, outcome = eng._attempt_proposal(
-        x=x, y=y, weights=w, base_report=base_report, spec=specs[0],
-        noise_floor=1.0, n_refits=4, rng_seed=0,
-        absent_slot_area_fraction=0.02, absent_slot_persistence_threshold=0.7,
-        diagnostic_windows=dict(case.grammar.diagnostic_windows),
-        budget_remaining=20.0)          # passes the 15 s TOP guard...
-    assert outcome == "fast_rejected"   # ...but post-fit remaining 7 s < 15
-    assert aug_report is None
-    assert "insufficient_budget before stability" in (pr.rejection_reason or "")
+    def jumpy():
+        ticks["t"] += 1.0e6
+        return ticks["t"]
+    monkeypatch.setattr(eng.time, "perf_counter", jumpy)
+    assert run() == normal
 
 
 # ── F3: two-phase sweep ────────────────────────────────────────────────────

exec
/bin/zsh -lc "git diff main..HEAD -- autofit/engine.py | tail -160; cat tests/autofit/test_fit_certificate.py; git diff main..HEAD -- tests/autofit/test_preseed_dominants.py CLAUDE.md; sed -n '500,640p' app.py; sed -n '1150,1280p' app.py; command -v python python3 pytest; ls -a | head -35" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-9vnwRAWI' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-VQVKvmRm' (errno=Operation not permitted)
 
-    # An augmented fit_candidate has no internal wall clock and runs
-    # ~10-12 s worst-case; starting one with less than PROPOSAL_MIN_FIT_
-    # BUDGET_SEC of sweep budget left would overrun TOTAL_ANALYSIS_TIMEOUT_SEC
-    # and the gunicorn --timeout (Codex c1s-fix review, run B MAJOR).  The
-    # caller passes budget_remaining = min(pass budget, sweep budget) left.
-    if budget_remaining < PROPOSAL_MIN_FIT_BUDGET_SEC:
-        return _fast(
-            f"insufficient_budget: {budget_remaining:.1f}s left < "
-            f"{PROPOSAL_MIN_FIT_BUDGET_SEC:.0f}s needed for one augmented fit")
-
     bg = _compute_background(x, y, aug_model.background, endpoint_avg=endpoint_avg)
     try:
         init = _initial_params_for_augmented(aug_model, base_fit, spec, x, y - bg,
@@ -2251,28 +2228,9 @@ def _attempt_proposal(
             f"base BIC* {base_report.bic_adjusted:.2f} by {PROPOSAL_DELTABIC_THRESHOLD:.1f}"
         )
 
-    # budget_remaining was a snapshot BEFORE the augmented fit; that fit has
-    # since consumed wall time, so the stability deadline must be computed
-    # from what's ACTUALLY left, not the stale snapshot (Codex c1s-fix
-    # review, run B MAJOR — otherwise the stability pass could run
-    # min(stale_budget, 35) s past the fit and overrun the sweep budget).
-    # The floor (not just <= 0) matters because run_stability_analysis
-    # checks its deadline at the TOP of the loop and then runs an unbounded
-    # fit_candidate — so starting stability with only a few seconds left
-    # would still overrun by ~one worst-case fit (Codex c1s-fix RE-CHECK,
-    # run B MAJOR: disposition 2 was not fully closed by the top guard).
-    remaining = budget_remaining - (time.perf_counter() - attempt_start)
-    if remaining < PROPOSAL_MIN_FIT_BUDGET_SEC:
-        pr.rejection_reason = (
-            f"insufficient_budget before stability: {remaining:.1f}s left < "
-            f"{PROPOSAL_MIN_FIT_BUDGET_SEC:.0f}s (one refit could overrun)")
-        return None, pr, "fast_rejected"
-
     stability = run_stability_analysis(
         x, y, weights, aug_model, primary,
         noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
-        deadline=time.perf_counter() + min(remaining,
-                                           PROPOSAL_STABILITY_TIMEOUT_SEC),
         fit_full_window=fit_full_window,
         endpoint_avg=endpoint_avg,
     )
@@ -2445,7 +2403,6 @@ def _bound_fixed_refit(
         x, y, weights, report.model, outcome,
         noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
         fixed_param_values=fixed,
-        deadline=time.perf_counter() + CANDIDATE_TIMEOUT_SEC,
         fit_full_window=fit_full_window,
         endpoint_avg=endpoint_avg,
     )
@@ -2738,7 +2695,6 @@ def compare_models(
     proposal_attempts: list[tuple[str, ProposedPeakReport]] = []
     timings: list[ProposalPassTiming] = []
     n_cand = len(candidates)
-    sweep_start = time.perf_counter()
     n_evaluated = 0
     analysis_truncated = False
 
@@ -2750,16 +2706,9 @@ def compare_models(
     if n_cand > SCREEN_TOP_K:
         screen_rows: list[dict] = []
         screened: list[tuple[CandidateModel, FitOutcome, float]] = []
-        screen_deadline = sweep_start + SCREEN_BUDGET_FRACTION * TOTAL_ANALYSIS_TIMEOUT_SEC
+        # Unit A1: EVERY candidate is screened (no wall-clock screen budget —
+        # which candidates reached the deep phase used to depend on load)
         for idx, model in enumerate(candidates, 1):
-            if time.perf_counter() > screen_deadline:
-                analysis_truncated = True
-                log.warning(
-                    "compare_models: screen budget (%.0f%% of the sweep) "
-                    "exhausted after %d/%d candidates — the deep phase runs "
-                    "on what screened so far",
-                    100 * SCREEN_BUDGET_FRACTION, idx - 1, n_cand)
-                break
             log.info("[screen %2d/%d] %s", idx, n_cand, model.name)
             _report_progress(progress_cb, "screening", idx, n_cand, model.name)
             outcome = fit_candidate(x, y, weights, model,
@@ -2789,30 +2738,11 @@ def compare_models(
             [m.name for m in candidates])
 
     for idx, model in enumerate(candidates, 1):
-        # Pre-check with the candidate's own worst-case budget: a candidate
-        # STARTED just under the wire used to overshoot the sweep budget by
-        # its full stability + proposal cost (measured 310 s wall vs the
-        # 240 s budget on real data — past the gunicorn --timeout 300, i.e.
-        # the exact worker-kill this budget exists to prevent).  Truncating
-        # BEFORE starting a candidate that cannot finish keeps the worst-case
-        # wall ≈ TOTAL_ANALYSIS_TIMEOUT_SEC.
-        elapsed = time.perf_counter() - sweep_start
-        if elapsed > TOTAL_ANALYSIS_TIMEOUT_SEC - CANDIDATE_TIMEOUT_SEC:
-            analysis_truncated = True
-            log.warning(
-                "compare_models: sweep budget cannot fit another candidate "
-                "(%.0fs elapsed of %.0fs) after %d/%d — remaining candidates "
-                "skipped, returning best-so-far",
-                elapsed, TOTAL_ANALYSIS_TIMEOUT_SEC, n_evaluated, len(candidates),
-            )
-            break
+        # Unit A1: every selected candidate is evaluated — no sweep budget
         n_evaluated += 1
         log.info("[%2d/%d] %s: primary fit", idx, len(candidates), model.name)
         _report_progress(progress_cb, "stabilizing", idx, len(candidates),
                          model.name)
-        # Shared wall-clock budget for this candidate's primary fit + all its
-        # stability refits (CANDIDATE_TIMEOUT_SEC) — see run_stability_analysis.
-        candidate_deadline = time.perf_counter() + CANDIDATE_TIMEOUT_SEC
         # reuse the screen fit as this candidate's primary (no repeated work)
         primary = screen_fit.get(model.name) or fit_candidate(
             x, y, weights, model, fit_full_window=fit_full_window,
@@ -2824,7 +2754,6 @@ def compare_models(
         stability = run_stability_analysis(
             x, y, weights, model, primary,
             noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
-            deadline=candidate_deadline,
             fit_full_window=fit_full_window,
             endpoint_avg=endpoint_avg,
         )
@@ -2864,20 +2793,12 @@ def compare_models(
             # per-candidate wall budget.  Gates are unchanged per round.
             counts = dict(n_flagged=0, n_over_cap=0, n_attempted=0,
                           n_fast=0, n_stab=0, n_acc=0)
-            timed_out = False
-            pass_start = time.perf_counter()
-            # the pass never spends beyond the sweep's remaining budget —
-            # same worst-case-wall reasoning as the candidate pre-check
-            pass_budget = min(
-                PROPOSAL_CANDIDATE_TIMEOUT_SEC,
-                TOTAL_ANALYSIS_TIMEOUT_SEC - (pass_start - sweep_start))
+            timed_out = False                 # unit A1: never set (no pass budget)
+            pass_start = time.perf_counter()  # telemetry only (wall_time_sec)
             rejected: list[ProposedPeakReport] = []
             current = base_report
             current_y_fit = y_fit
             while counts["n_acc"] < PROPOSAL_MAX_PER_CANDIDATE:
-                if time.perf_counter() - pass_start > pass_budget:
-                    timed_out = True
-                    break
                 specs = _detect_residual_proposals(
                     x, y, current_y_fit, noise_floor, current.model,
                     fitted_components=current.primary_fit.components,
@@ -2894,10 +2815,6 @@ def compare_models(
                 counts["n_over_cap"] += max(len(specs) - len(attempts), 0)
                 accepted_this_round = False
                 for spec in attempts:
-                    elapsed = time.perf_counter() - pass_start
-                    if elapsed > pass_budget:
-                        timed_out = True
-                        break
                     counts["n_attempted"] += 1
                     aug_report, pr, outcome = _attempt_proposal(
                         x=x, y=y, weights=weights, base_report=current, spec=spec,
@@ -2905,7 +2822,6 @@ def compare_models(
                         absent_slot_area_fraction=absent_slot_area_fraction,
                         absent_slot_persistence_threshold=absent_slot_persistence_threshold,
                         diagnostic_windows=diagnostic_windows,
-                        budget_remaining=pass_budget - elapsed,
                         fit_full_window=fit_full_window,
                         endpoint_avg=endpoint_avg,
                     )
"""Unit A1 (2026-09-29): Find Peaks judges convergence by a CERTIFICATE, not the
optimiser's flag. A fit has reached a minimum when a fresh Trust-Region descent
from its end point improves chi2 by less than that descent's own stopping
tolerance (scipy least_squares' ftol); restarts repeat from each improved point
up to CERTIFY_MAX_RESTARTS; out of restarts = not converged. The flag was wrong
both ways: a warm restart from a stall "succeeded" in ~30 evaluations at
chi2r 37.6 where the minimum is 5.21 (8-JT C1s Scan_7), and a refit capped at
18 000 evaluations AT the minimum counted as failed (1-GTA C1s Scan_6)."""
import inspect
import os

import numpy as np
import pytest
import scipy.optimize

import autofit.engine as eng
from autofit.grammar import MaterialClass, Phase, resolve
from autofit.methods.base import poisson_like_weights
from autofit.reference import load_reference_fits

DATA = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "autofit", "test_data")
G = resolve([Phase(id="graphite", material_class=MaterialClass.CONDUCTOR, regions=("C 1s",), material="graphite")], "C 1s")


def _scan(project, name):
    rf = next(r for r in load_reference_fits(os.path.join(DATA, project)) if r.name == name)
    x, y = np.asarray(rf.roi_be, float), np.asarray(rf.roi_intensity, float)
    return x, y, poisson_like_weights(y)


def _mg2():
    return next(c for c in G.candidates if c.name == "MG2_graphAsymGL_aliph_sat_CO_C=O")


def test_the_tolerance_is_the_optimisers_own():
    assert eng.CERTIFY_FTOL == inspect.signature(scipy.optimize.least_squares).parameters["ftol"].default
    assert isinstance(eng.CERTIFY_MAX_RESTARTS, int) and eng.CERTIFY_MAX_RESTARTS >= 1


def _kkt_violations(comp, params, x, y_net, w):
    """Parameters along which chi2 still descends: a free parameter with a
    non-negligible gradient, or one on a bound whose gradient points INTO the
    box. Empty = a (constrained) local minimum."""
    chi = lambda pp: float(np.sum(((y_net - comp.eval(pp, x=x)) * w) ** 2))
    c0, bad = chi(params), []
    for n, p in params.items():
        if not p.vary or p.expr is not None:
            continue
        span = (p.max - p.min) if np.isfinite(p.max) and np.isfinite(p.min) else (abs(p.value) or 1.0)
        h = 1e-6 * span
        q = params.copy()
        if p.value - p.min < 1e-9 * span:
            q[n].set(value=p.value + h)
            if chi(q) < c0 - 1e-9 * c0: bad.append(n)
        elif p.max - p.value < 1e-9 * span:
            q[n].set(value=p.value - h)
            if chi(q) < c0 - 1e-9 * c0: bad.append(n)
        else:
            q[n].set(value=p.value + h); cp = chi(q); q[n].set(value=p.value - h); cm = chi(q)
            if abs(cp - cm) / (2 * h) * span > 1e-3 * c0: bad.append(n)
    return bad


def test_a_stall_now_ends_at_a_constrained_local_minimum():
    """Scan_7 MG2, stability refit 0's start. The removed warm restart
    reported success at the leastsq stall point (chi2 5220), which is NOT a
    minimum: a descent still lowers chi2. The certified point satisfies the
    KKT conditions (free gradients ~0, every parameter on a bound pushing out):
    a genuine local minimum, pinned on bounds (chi2r ~37 — a worse basin than
    the 5.21 least_squares finds from the same start by another path)."""
    x, y, w = _scan("8-JT Graphite.proj.zip", "C1s Scan_7")
    model = _mg2()
    primary = eng.fit_candidate(x, y, w, model)
    y_net = y - primary.background
    seed = int(np.random.default_rng(0).integers(0, 2**31 - 1))
    init = eng.perturb_initial_params(model, seed=seed, x=x, y_net=y_net)
    comp = eng._build_composite_model(model)
    stall = comp.fit(y_net, init.copy(), x=x, weights=w, method="leastsq", nan_policy="omit",
                     max_nfev=eng.FIT_CANDIDATE_MAX_NFEV)
    assert _kkt_violations(comp, stall.params, x, y_net, w), "the stall point is not a minimum"
    out = eng.fit_candidate(x, y, w, model, initial_params=init.copy())
    assert out.converged
    assert out.weighted_chi_sq < stall.chisqr
    assert _kkt_violations(comp, out.lmfit_result.params, x, y_net, w) == []


def _two_peak():
    x = np.arange(280.0, 292.0, 0.05)
    t = 500 + 8000 * np.exp(-4 * np.log(2) * ((x - 284.5) / 1.0) ** 2) + 1500 * np.exp(-4 * np.log(2) * ((x - 286.4) / 1.2) ** 2)
    y = t + np.sqrt(t) * np.random.default_rng(5).standard_normal(x.size)
    slot = lambda r, win: eng.ComponentSlot(role=r, region="C 1s", phase_id="p", be_window=win,
                                            line_shape=eng.LineShape.GAUSSIAN, fwhm_range=(0.5, 2.5))
    model = eng.CandidateModel(name="m", background=eng.BackgroundType.LINEAR,
                               slots=(slot("a", (284.0, 285.0)), slot("b", (286.0, 287.0))))
    return x, y, poisson_like_weights(y), model


def test_a_fit_capped_at_the_minimum_is_certified():
    """The Scan_6 case in general form: an optimiser that runs out of
    evaluations while sitting at the minimum reports failure; the certificate
    finds no descent and certifies it."""
    x, y, w, model = _two_peak()
    good = eng.fit_candidate(x, y, w, model)
    assert good.converged
    comp = eng._build_composite_model(model)
    y_sub = y - good.background
    capped = comp.fit(y_sub, good.lmfit_result.params.copy(), x=x, weights=w, method="leastsq",
                      nan_policy="omit", max_nfev=3)          # starts AT the minimum, capped at once
    assert not capped.success
    point, certified = eng._certify_minimum(comp, y_sub, capped, x, w, eng.FIT_CANDIDATE_MAX_NFEV)
    assert certified
    assert point.chisqr == pytest.approx(good.weighted_chi_sq, rel=1e-6)


def test_out_of_restarts_is_not_converged(monkeypatch):
    """A start far from the minimum needs more than one restart to certify
    (the first descends a long way); with a single restart allowed it is
    'not converged' — whatever the optimiser says."""
    x, y, w, model = _two_peak()
    comp = eng._build_composite_model(model)
    good = eng.fit_candidate(x, y, w, model)
    y_sub = y - good.background
    far = good.lmfit_result.params.copy()
    far["s_a_center"].set(value=284.05); far["s_b_amplitude"].set(value=50.0); far["s_a_fwhm"].set(value=2.3)
    short = comp.fit(y_sub, far, x=x, weights=w, method="leastsq", nan_policy="omit", max_nfev=2)
    monkeypatch.setattr(eng, "CERTIFY_MAX_RESTARTS", 1)
    _, certified = eng._certify_minimum(comp, y_sub, short, x, w, eng.FIT_CANDIDATE_MAX_NFEV)
    assert not certified
    monkeypatch.setattr(eng, "CERTIFY_MAX_RESTARTS", 5)
    point, certified = eng._certify_minimum(comp, y_sub, short, x, w, eng.FIT_CANDIDATE_MAX_NFEV)
    assert certified and point.chisqr == pytest.approx(good.weighted_chi_sq, rel=1e-6)


def test_the_warm_restart_is_gone():
    src = inspect.getsource(eng.fit_candidate)
    assert "retry" not in src and "WARM_RESTART" not in src
    assert "converged=bool(certified)" in src
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-sKSTmNJr' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-L5GhvO5e' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index 44eef1b..32ae229 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -226,6 +226,25 @@ workers, at most 4 concurrent fits, the bound the synchronous route had. The syn
 for scripts, tests and the Python twins. Plan:
 `docs/superpowers/plans/2026-09-27-long-fits-start-poll.md`.
 
+### Find Peaks does not read the clock (unit A1, 2026-09-29)
+
+Find Peaks' answer must not depend on server load or on the optimiser's own
+termination flags. No wall-clock budget anywhere in `autofit/engine.py`
+(the 25 s per-candidate, 240 s sweep, proposal and screen budgets are gone —
+on 1-GTA C1s Scan_6 MG2 won or lost on whether its fourth refit started
+before 25 s): every candidate is screened, `SCREEN_TOP_K` are evaluated with
+exactly `n_refits` refits, and work is bounded by counts and evaluation caps.
+A fit's convergence is CERTIFIED (`_certify_minimum`): Trust-Region restarts
+from the end point until one improves chi2 by less than Trust-Region's own
+ftol (scipy's default, no new constant), at most `CERTIFY_MAX_RESTARTS` = 50
+(measured: 2 for most fits, 21 at most on the committed C 1s set); out of
+restarts = not converged. The old warm restart from a failed fit's exit point
+is gone (it met MINPACK's xtol at the stall and reported success). Under
+light and heavy load every structural field of the output is identical; the
+numbers carry Trust-Region's arithmetic jitter (≤ 0.25 meV, ≤ 5e-4 relative
+amplitude, the same idle-to-idle). Plan:
+`docs/superpowers/plans/2026-09-29-a1-find-peaks-determinism.md`.
+
 ### Timing claims are measured through the public URL
 
 A request from a student reaches the server through Cloudflare, whose edge
diff --git a/tests/autofit/test_preseed_dominants.py b/tests/autofit/test_preseed_dominants.py
index 74ec475..596c3a6 100644
--- a/tests/autofit/test_preseed_dominants.py
+++ b/tests/autofit/test_preseed_dominants.py
@@ -345,8 +345,7 @@ def test_proposal_rejected_when_stability_promotes_spurious_center_peg(monkeypat
         x=x, y=y, weights=w, base_report=base, spec=spec,
         noise_floor=1.0, n_refits=2, rng_seed=0,
         absent_slot_area_fraction=0.02, absent_slot_persistence_threshold=0.7,
-        diagnostic_windows=dict(case.grammar.diagnostic_windows),
-        budget_remaining=1e6)
+        diagnostic_windows=dict(case.grammar.diagnostic_windows))
     assert outcome == "stability_rejected"
     assert "post-stability" in (pr.rejection_reason or "")
     assert any("center@min" in h for h in pr.boundary_hits)
@@ -418,80 +417,30 @@ def test_next_proposal_index_is_max_suffix_plus_one():
     assert eng._next_proposal_index(m0) == 0
 
 
-def test_proposal_pass_respects_sweep_budget(monkeypatch):
-    """Codex c1s-fix MAJOR (run B): an augmented fit has no internal wall
-    clock, so a proposal attempt must fast-reject when too little sweep
-    budget remains rather than running an unbounded fit past the total
-    timeout.  With the fit-budget floor raised above any real remaining
-    budget, EVERY proposal attempt must be 'insufficient_budget' — no
-    augmented fit runs, no proposal is accepted, and the sweep still
-    returns cleanly."""
-    monkeypatch.setattr(eng, "PROPOSAL_MIN_FIT_BUDGET_SEC", 10_000.0)
+def test_no_wall_clock_can_change_the_answer(monkeypatch):
+    """Unit A1 (2026-09-29): the sweep, screen, stability and proposal
+    budgets were wall-clock and made the answer depend on server load; they
+    are gone. A clock that jumps a million seconds on every read must leave
+    the result IDENTICAL."""
     x = _grid()
     truth = [{"center": 196.5, "fwhm": 1.2, "height": 9000.0},
              {"center": 201.5, "fwhm": 1.2, "height": 2500.0}]
     sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
     y = _noisy(sig + _linear_bg(x), 71)
-    cands = [_cand("single_main", [_slot("main_a", (195.5, 197.5))])]
-    grammar = _grammar(cands)
-    res = get_method("ic_model_comparison").run(
-        x, y, grammar=grammar,
-        options={**IC_OPTS, "enable_preseed": False})
-    assert not res.diagnostics["winner"].endswith("+prop")
-    reasons = [p["rejection_reason"] for c in res.analysis["candidates"]
-               for p in c.get("proposed_peaks", [])]
-    assert reasons, "expected at least one attempted-then-rejected proposal"
-    assert all("insufficient_budget" in (r or "") for r in reasons), reasons
-
-
-def test_stability_not_started_without_budget_after_augmented_fit(monkeypatch):
-    """Codex c1s-fix RE-CHECK (run B): the top budget guard alone did NOT
-    close the overrun — an augmented fit that PASSES the top guard then
-    consumes most of the budget must not let run_stability_analysis start
-    an unbounded refit with only a few seconds left.  The pre-stability
-    guard now fast-rejects when the DYNAMIC remaining budget is below the
-    fit floor.  Deterministic via a fake clock: attempt_start = 1000 s,
-    every later perf_counter reads 1013 s, so with budget_remaining=20 the
-    post-fit remaining is 7 s < 15 s floor — stability must NOT run."""
-    from autofit.methods.base import poisson_like_weights
-    from stress_cases import isolated_missing_peak_case
+    grammar = _grammar([_cand("single_main", [_slot("main_a", (195.5, 197.5))])])
 
-    case = isolated_missing_peak_case(seed=71)
-    x, y = case.x, case.y
-    w = poisson_like_weights(y)
-    model = case.grammar.candidates[0]
-    # real base report (unpatched clock), proposal + preseed off
-    res = eng.compare_models(x, y, w, case.grammar, n_refits=2, rng_seed=0,
-                             enable_proposal_pass=False, enable_preseed=False)
-    base_report = res.reports[0]
-    y_fit = (base_report.primary_fit.lmfit_result.best_fit
-             + base_report.primary_fit.background)
-    specs = eng._detect_residual_proposals(
-        x, y, y_fit, 1.0, model,
-        fitted_components=base_report.primary_fit.components)
-    assert specs, "expected a residual proposal at the unmodeled peak"
-
-    calls = {"n": 0}
+    def run():
+        res = get_method("ic_model_comparison").run(x, y, grammar=grammar, options={**IC_OPTS, "enable_preseed": False})
+        return res.diagnostics, res.peaks, res.analysis, res.confidence
 
-    def fake_pc():
-        calls["n"] += 1
-        return 1000.0 + (0.0 if calls["n"] == 1 else 13.0)
+    normal = run()
+    ticks = {"t": 0.0}
 
-    def boom(*a, **k):
-        raise AssertionError("run_stability_analysis started without budget")
-
-    monkeypatch.setattr(eng.time, "perf_counter", fake_pc)
-    monkeypatch.setattr(eng, "run_stability_analysis", boom)
-
-    aug_report, pr, outcome = eng._attempt_proposal(
-        x=x, y=y, weights=w, base_report=base_report, spec=specs[0],
-        noise_floor=1.0, n_refits=4, rng_seed=0,
-        absent_slot_area_fraction=0.02, absent_slot_persistence_threshold=0.7,
-        diagnostic_windows=dict(case.grammar.diagnostic_windows),
-        budget_remaining=20.0)          # passes the 15 s TOP guard...
-    assert outcome == "fast_rejected"   # ...but post-fit remaining 7 s < 15
-    assert aug_report is None
-    assert "insufficient_budget before stability" in (pr.rejection_reason or "")
+    def jumpy():
+        ticks["t"] += 1.0e6
+        return ticks["t"]
+    monkeypatch.setattr(eng.time, "perf_counter", jumpy)
+    assert run() == normal
 
 
 # ── F3: two-phase sweep ────────────────────────────────────────────────────
    the exact wording the goal asked for ('candidate 7 of 29 . stabilizing')."""
    phase = evt.get("phase")
    idx, total = evt.get("candidate_index"), evt.get("candidate_total")
    name = evt.get("candidate_name")
    if phase == "screening" and idx and total:
        msg = f"screening candidate {idx} of {total}"
    elif phase == "stabilizing" and idx and total:
        msg = f"candidate {idx} of {total} — stabilizing"
    else:
        return phase or "working…"
    return msg + (f" ({name})" if name else "")


def _job_progress_path(job_id: str, upload_folder: str) -> Path:
    return Path(upload_folder) / f"{job_id}.job.json"


def _write_job_progress(job_id: str, upload_folder: str, data: dict) -> None:
    """Atomic write (temp file + os.replace) — required because the
    writer (background thread, possibly in a DIFFERENT gunicorn worker
    process than whichever one later serves a poll GET) and the reader
    are never synchronized otherwise; a half-written file must never be
    visible to a concurrent poll."""
    path = _job_progress_path(job_id, upload_folder)
    tmp = path.with_suffix(".tmp")
    try:
        tmp.write_text(json.dumps(_json_sanitize(data)))
        os.replace(tmp, path)
    except OSError:
        logging.getLogger(__name__).exception(
            "failed to write progress for job %s", job_id)


def _sweep_expired_jobs(upload_folder: str) -> None:
    """Opportunistic TTL cleanup of stale job progress files — same
    pattern as _sweep_expired_sessions (audit F13): runs on each new job
    start, no scheduler/thread, tolerates a concurrent worker deleting the
    same file first, never raises."""
    cutoff = time.time() - _ANALYZE_JOB_TTL_SEC
    try:
        candidates = list(Path(upload_folder).glob("*.job.json"))
    except OSError:
        return
    for p in candidates:
        try:
            if p.stat().st_mtime < cutoff:
                p.unlink(missing_ok=True)
        except FileNotFoundError:
            pass
        except OSError:
            pass


# ── Fit jobs (unit 2, 2026-09-27) ────────────────────────────────────────────
# Records are the Find Peaks job files (<job>.job.json, the same TTL sweep);
# two small markers beside each: <job>.cancel (written by /api/fit/cancel,
# any worker) and <job>.polled (touched by every poll). The fit thread's
# cancel condition: the cancel marker exists, OR no poll for
# FIT_JOB_ABANDON_SEC (a closed tab, a sleeping laptop; 180 s, above the ~1 min timer throttling browsers apply to hidden tabs).
FIT_JOB_ABANDON_SEC = 180   # > Chrome's 1-minute timer throttling in a hidden tab: a student who switches browser tabs keeps the fit
FIT_JOB_HEARTBEAT_SEC = 2.0
# Concurrency (unit 2, Codex round 1). Before start-then-poll, gunicorn's four
# SYNC workers bounded concurrent fits at four; a fit thread per start would
# not. Each worker process runs at most FIT_JOB_MAX_RUNNING fits at once (the
# rest wait "queued", heartbeating, cancellable) and admits at most
# FIT_JOB_MAX_ADMITTED running + queued jobs; beyond that /api/fit/start
# answers 503 "busy" immediately. With production's 4 workers: at most 4
# concurrent fits, as before.
FIT_JOB_MAX_RUNNING = 1
FIT_JOB_MAX_ADMITTED = 6
_FIT_JOB_RUN_SLOTS = threading.BoundedSemaphore(FIT_JOB_MAX_RUNNING)
_FIT_JOB_ADMITTED = [0]
_FIT_JOB_ADMIT_LOCK = threading.Lock()


def _fit_job_admit() -> bool:
    with _FIT_JOB_ADMIT_LOCK:
        if _FIT_JOB_ADMITTED[0] >= FIT_JOB_MAX_ADMITTED:
            return False
        _FIT_JOB_ADMITTED[0] += 1
        return True


def _fit_job_release() -> None:
    with _FIT_JOB_ADMIT_LOCK:
        _FIT_JOB_ADMITTED[0] = max(0, _FIT_JOB_ADMITTED[0] - 1)


def _fit_job_marker(job_id: str, upload_folder: str, kind: str) -> Path:
    return Path(upload_folder) / f"{job_id}.{kind}"


def _fit_job_write(job_id: str, upload_folder: str, data: dict) -> None:
    """Atomic like _write_job_progress, but WITHOUT sanitising: a result's
    NaN / Infinity reach the page exactly as /api/fit sends them (the page's
    _readFitReply refuses them as a failed fit — unit F2)."""
    path = _job_progress_path(job_id, upload_folder)
    tmp = path.with_suffix(f".{threading.get_ident()}.tmp")
    try:
        tmp.write_text(json.dumps(data, allow_nan=True))
        os.replace(tmp, path)
    except OSError:
        logging.getLogger(__name__).exception("failed to write fit job %s", job_id)


def _fit_job_read(job_id: str, upload_folder: str):
    path = _job_progress_path(job_id, upload_folder)
    if not path.exists():
        return None
    try:
        _fit_job_marker(job_id, upload_folder, "polled").touch()
    except OSError:
        pass
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        data = {"status": "running", "elapsed_sec": 0.0}      # a read racing the first write
    hb = data.get("heartbeat")
    data["heartbeat_age_sec"] = round(time.time() - hb, 1) if isinstance(hb, (int, float)) else None
    return data


def _sweep_fit_job_markers(upload_folder: str) -> None:
    """Markers left by a job whose worker died (they are removed when a job
    finishes): same TTL as the job records, never raises."""
    cutoff = time.time() - _ANALYZE_JOB_TTL_SEC
    for pattern in ("*.cancel", "*.polled"):
        try:
            for m in Path(upload_folder).glob(pattern):
                try:
                    if m.stat().st_mtime < cutoff:
                        m.unlink(missing_ok=True)
                except OSError:
                    pass
        except OSError:
            pass


def _fit_job_cancel(job_id: str, upload_folder: str) -> None:
    try:
        _fit_job_marker(job_id, upload_folder, "cancel").touch()
        Async twin of POST /api/analyze for the Find Peaks progress
        indicator (2026-07-11).  Same request body; same SYNCHRONOUS
        validation (a malformed request is STILL an immediate 400, never
        a spinner) — only the actual method execution (the genuinely
        slow, honestly-long part) moves to a background thread.

        Why a thread + a poll file, not SSE: production gunicorn runs the
        default SYNC worker class (`--workers 4`, no gthread/gevent — see
        the LaunchAgent plist), so a held-open SSE connection would tie up
        an entire worker for the whole 60-240s analysis, on top of the
        existing synchronous /api/analyze already doing exactly that for
        ITS OWN request. A background thread returns the HTTP response
        immediately (freeing the worker's request loop), and progress is
        written to a small JSON file under the upload folder — file, not
        an in-process dict, because gunicorn's workers are separate OS
        processes and a poll can land on a different one (same reasoning
        as the existing session .npz files: "no server-side memory state
        ... compatible with multi-worker gunicorn").

        Returns {"job_id": "..."} , 202.  Poll
        GET /api/analyze/progress/<job_id> for {status, phase,
        candidate_index, candidate_total, candidate_name, elapsed_sec,
        message, result (once done), error (once errored)}.
        """
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return _err("request body must be a JSON object")
        upload_folder = app.config["UPLOAD_FOLDER"]
        try:
            ctx = _validate_analyze_request(body, upload_folder)
        except _AnalyzeError as exc:
            return _err(str(exc), exc.status)

        job_id = str(uuid.uuid4())
        _sweep_expired_jobs(upload_folder)
        start_time = time.time()
        _write_job_progress(job_id, upload_folder, {
            "status": "running", "phase": "starting",
            "candidate_index": None, "candidate_total": None,
            "candidate_name": None, "elapsed_sec": 0.0,
            "message": "starting analysis…",
        })

        def _progress_cb(evt: dict) -> None:
            _write_job_progress(job_id, upload_folder, {
                "status": "running",
                "phase": evt.get("phase"),
                "candidate_index": evt.get("candidate_index"),
                "candidate_total": evt.get("candidate_total"),
                "candidate_name": evt.get("candidate_name"),
                "elapsed_sec": round(time.time() - start_time, 1),
                "message": _analyze_progress_message(evt),
            })

        def _worker() -> None:
            try:
                res = _run_analyze_method(ctx, progress_cb=_progress_cb)
                payload = _build_analyze_payload(ctx, res)
                _write_job_progress(job_id, upload_folder, {
                    "status": "done", "phase": "done",
                    "elapsed_sec": round(time.time() - start_time, 1),
                    "message": "done",
                    "result": payload,
                })
            except _AnalyzeError as exc:
                _write_job_progress(job_id, upload_folder, {
                    "status": "error", "phase": "done",
                    "elapsed_sec": round(time.time() - start_time, 1),
                    "message": "failed", "error": str(exc),
                    "http_status": exc.status,
                })
            except Exception as exc:      # belt-and-suspenders: the
                # indicator must ALWAYS clear, even on a bug we didn't
                # anticipate — never let a job hang the poll forever.
                logging.getLogger(__name__).exception(
                    "analyze job %s crashed", job_id)
                _write_job_progress(job_id, upload_folder, {
                    "status": "error", "phase": "done",
                    "elapsed_sec": round(time.time() - start_time, 1),
                    "message": "failed",
                    "error": f"internal error: {exc}",
                    "http_status": 500,
                })

        threading.Thread(target=_worker, daemon=True).start()
        return jsonify({"job_id": job_id}), 202

    @app.get("/api/analyze/progress/<job_id>")
    def analyze_progress(job_id):
        """Poll one analyze job's progress (Find Peaks UI, 2026-07-11).
        {status: 'running'|'done'|'error', phase, candidate_index,
        candidate_total, candidate_name, elapsed_sec, message, result
        (done only — the SAME shape /api/analyze returns), error (error
        only)}. 404 for an unknown/expired job_id; 400 for a malformed
        one (path-traversal guard, same convention as _validate_session_id)."""
        try:
            uuid.UUID(job_id)
        except ValueError:
            return _err("Invalid job_id format (expected UUID)", 400)
        path = _job_progress_path(job_id, app.config["UPLOAD_FOLDER"])
        if not path.exists():
            return _err(f"Job '{job_id}' not found", 404)
        try:
            data = json.loads(path.read_text())
        except (OSError, ValueError):
            # os.replace() makes writes atomic, but tolerate a read racing
            # the very first write rather than 500ing a normal poll
            data = {"status": "running", "phase": "starting",
                    "candidate_index": None, "candidate_total": None,
                    "candidate_name": None, "elapsed_sec": 0.0,
                    "message": "starting analysis…"}
        return jsonify(data)

    # ── Long fits via start-then-poll (unit 2, 2026-09-27) ───────────────────
    # The public URL ends a proxied request at ~100 s (Cloudflare 524; 88 s
    # passed, 125 s failed); basinhopping on the large C 1s models takes 3–4
    # minutes. The fit runs in a background thread on Find Peaks' job
    # infrastructure (an atomic JSON record under the upload folder, readable
    # by whichever gunicorn worker serves a poll); every HTTP request is short.
    # The record: {status: queued|running|done|error|cancelled, elapsed_sec,
    # heartbeat (epoch s, rewritten every 2 s while the fit thread lives),
    # result (done: EXACTLY the /api/fit body), error + http_status (error:
    # exactly what /api/fit would have answered)}.

    @app.post("/api/fit/start")
    @_require_json
    def fit_start():
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return _err("request body must be a JSON object")
        fit_args, error = _prepare_fit_request(app, body)
/usr/bin/python3
.
..
.codex
.git
.github
.gitignore
.impeccable
.stage9
CLAUDE.md
DEPLOY.md
DESIGN.md
PRODUCT.md
__pycache__
app.py
autofit
data
docs
fitting.py
parser.py
requirements-dev.txt
requirements.txt
scripts
static
templates
tests
uploads
vgd_parser.py
xps-fitting-tool.html
xps_reference.py

codex
The clock-based fit cutoffs are gone from the engine; the remaining clock reads appear to be telemetry. I’m now checking whether a capped or worsening restart can falsely certify convergence, and how certified results affect screening, stability, and uncertainty reporting.

exec
/bin/zsh -lc "sed -n '590,705p' autofit/engine.py; sed -n '860,945p' autofit/engine.py; sed -n '1160,1300p' autofit/engine.py; sed -n '2680,2885p' autofit/engine.py; rg -n 'success|stderr|sigma|lmfit_result|time\\.|perf_counter|deadline|budget|random' autofit/methods; ls /Users/skyefortier/xps-app/venv/bin/python* /Users/skyefortier/xps-app/.venv/bin/python* /opt/homebrew/bin/python* 2>/dev/null" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 exited 1 in 0ms:

@dataclass
class FittedComponent:
    slot_role: str
    position: float
    fwhm: float          # width-parameter value (m_gauss for DS+G — fitalg convention)
    amplitude: float
    shape_params: dict
    line_shape: Optional[LineShape] = None


@dataclass
class FitOutcome:
    converged: bool
    components: list[FittedComponent]
    residual_sum_sq: float
    weighted_chi_sq: float
    n_params: int
    n_data: int
    lmfit_result: Optional[ModelResult] = None
    background: Optional[np.ndarray] = None
    boundary_hits: list[str] = field(default_factory=list)


def _extract_fitted_components(
    result: ModelResult, model: CandidateModel
) -> list[FittedComponent]:
    out: list[FittedComponent] = []
    for slot in model.slots:
        prefix = _slot_prefix(slot.role)
        pars = result.params
        try:
            center = float(pars[f"{prefix}center"].value)
            amplitude = float(pars[f"{prefix}amplitude"].value)
            fwhm = float(pars[f"{prefix}{_width_param(slot.line_shape)}"].value)
        except KeyError:
            continue
        shape_params = {}
        for name, _, _, _ in _SHAPE_PARAM_DEFAULTS[slot.line_shape]:
            par = pars.get(f"{prefix}{name}")
            if par is not None:
                shape_params[name] = float(par.value)
        if slot.line_shape is LineShape.DS_G:
            shape_params["m_gauss"] = fwhm
        out.append(FittedComponent(
            slot_role=slot.role, position=center, fwhm=fwhm,
            amplitude=amplitude, shape_params=shape_params,
            line_shape=slot.line_shape,
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
        # Unit A1 (2026-09-29): convergence is CERTIFIED, not read from the
        # optimiser's flag (_certify_minimum). The old ONE warm restart from a
        # failed fit's exit point is gone: from a stall point MINPACK's restart
        # satisfies xtol in ~30 evaluations and reported success at a
        # non-minimum (8-JT C1s Scan_7: chi2r 37.6 "converged" where
        # least_squares from the same start reaches 5.21).
        result, certified = _certify_minimum(composite, y_sub, result, x, weights, max_nfev)
    except Exception as exc:
        log.debug("fit_candidate failed for %s: %s", model.name, exc)
        return FitOutcome(
            converged=False, components=[], residual_sum_sq=float("inf"),
            weighted_chi_sq=float("inf"),
            n_params=len([q for q in params.values() if q.vary]),
            n_data=len(y_sub), lmfit_result=None, background=bg,
        )

    if not certified:
        # out of restarts (or a non-finite restart): the fit did not reach a
        # minimum — reported as not converged, whatever the optimiser's flag
        log.debug("fit_candidate: %s not certified", model.name)
    unweighted_r = y_sub - result.best_fit
    return FitOutcome(
        converged=bool(certified),
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
    y: np.ndarray,
    weights: np.ndarray,
    model: CandidateModel,
    primary_fit: FitOutcome,
    noise_floor: float,
    n_refits: int = 20,
    rng_seed: int = 0,
    fixed_param_values: Optional[dict[str, float]] = None,
    fit_full_window: bool = False,
    endpoint_avg: int = 1,
) -> ModelStability:
    """
    Unit A1 (2026-09-29): exactly ``n_refits`` refits, always — no wall-clock
    deadline. The 25 s per-candidate budget this replaced made persistence
    (refits reached / refits attempted) depend on server load: on 1-GTA C1s
    Scan_6 MG2 got 3 or 4 refits depending on how busy the machine was, and
    2/3 vs 3/4 decided the winner. Work is bounded by counts (n_refits, each
    fit's max_nfev, the certificate's restarts).
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
                    # drop the completeness carrier.
                    candidates = [det_model] + candidates
                    log.info(
                        "compare_models: detection family '%s' joins the "
                        "sweep with %d slot(s) at %s",
                        det_model.name, len(det_model.slots),
                        [round(0.5 * (s.be_window[0] + s.be_window[1]), 2)
                         for s in det_model.slots])
        else:
            augment_roles = set()
    else:
        augment_roles = set()

    reports: list[ModelReport] = []
    non_converged: list[tuple[CandidateModel, FitOutcome]] = []
    proposal_attempts: list[tuple[str, ProposedPeakReport]] = []
    timings: list[ProposalPassTiming] = []
    n_cand = len(candidates)
    n_evaluated = 0
    analysis_truncated = False

    # ── Unit F3: screen phase (only for candidate sets larger than the
    #    deep-evaluation budget — every existing gate/battery path is ≤
    #    SCREEN_TOP_K and unchanged) ─────────────────────────────────────
    screen_record: Optional[list[dict]] = None
    screen_fit: dict[str, FitOutcome] = {}
    if n_cand > SCREEN_TOP_K:
        screen_rows: list[dict] = []
        screened: list[tuple[CandidateModel, FitOutcome, float]] = []
        # Unit A1: EVERY candidate is screened (no wall-clock screen budget —
        # which candidates reached the deep phase used to depend on load)
        for idx, model in enumerate(candidates, 1):
            log.info("[screen %2d/%d] %s", idx, n_cand, model.name)
            _report_progress(progress_cb, "screening", idx, n_cand, model.name)
            outcome = fit_candidate(x, y, weights, model,
                                    max_nfev=SCREEN_MAX_NFEV,
                                    fit_full_window=fit_full_window,
                                    endpoint_avg=endpoint_avg)
            if outcome.converged:
                bic = compute_bic(outcome)
                screened.append((model, outcome, bic))
                screen_rows.append({"name": model.name, "converged": True,
                                    "bic": float(bic), "selected": False})
            else:
                non_converged.append((model, outcome))
                screen_rows.append({"name": model.name, "converged": False,
                                    "bic": None, "selected": False})
        screened.sort(key=lambda t: t[2])
        selected_models = screened[:SCREEN_TOP_K]
        selected_names = {m.name for m, _, _ in selected_models}
        for row in screen_rows:
            row["selected"] = row["name"] in selected_names
        screen_record = screen_rows
        screen_fit = {m.name: o for m, o, _ in selected_models}
        candidates = [m for m, _, _ in selected_models]
        log.info(
            "compare_models: screen kept %d/%d candidates for deep "
            "evaluation: %s", len(candidates), n_cand,
            [m.name for m in candidates])

    for idx, model in enumerate(candidates, 1):
        # Unit A1: every selected candidate is evaluated — no sweep budget
        n_evaluated += 1
        log.info("[%2d/%d] %s: primary fit", idx, len(candidates), model.name)
        _report_progress(progress_cb, "stabilizing", idx, len(candidates),
                         model.name)
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
        )
        base_report = ModelReport(
            model=model, primary_fit=primary, bic=compute_bic(primary),
            stability=stability, residuals=residuals,
            plausibility=PlausibilityFlags(
                boundary_hits=list(primary.boundary_hits),
                unphysical_widths=_unphysical_width_flags(primary.components, model),
                orphan_peaks=stability.orphan_rate > 0.1,
            ),
            absent_slots=absent,
        )

        final_report = base_report
        if enable_proposal_pass:
            # Unit F2: ITERATIVE rounds — each accepted proposal makes the
            # augmented report the new base, detection re-runs on ITS
            # residual, and the next round may accept another peak (up to
            # PROPOSAL_MAX_PER_CANDIDATE total), all under ONE shared
            # per-candidate wall budget.  Gates are unchanged per round.
            counts = dict(n_flagged=0, n_over_cap=0, n_attempted=0,
                          n_fast=0, n_stab=0, n_acc=0)
            timed_out = False                 # unit A1: never set (no pass budget)
            pass_start = time.perf_counter()  # telemetry only (wall_time_sec)
            rejected: list[ProposedPeakReport] = []
            current = base_report
            current_y_fit = y_fit
            while counts["n_acc"] < PROPOSAL_MAX_PER_CANDIDATE:
                specs = _detect_residual_proposals(
                    x, y, current_y_fit, noise_floor, current.model,
                    fitted_components=current.primary_fit.components,
                )
                # roles must stay unique across rounds — number this round's
                # specs from one past the HIGHEST existing suffix (never a
                # count: see _next_proposal_index for the collision this
                # avoids)
                base_idx = _next_proposal_index(current.model)
                for j, spec in enumerate(specs):
                    spec.role = f"proposed_peak_{base_idx + j}"
                attempts = specs[:PROPOSAL_MAX_ATTEMPTS_PER_CANDIDATE]
                counts["n_flagged"] += len(specs)
                counts["n_over_cap"] += max(len(specs) - len(attempts), 0)
                accepted_this_round = False
                for spec in attempts:
                    counts["n_attempted"] += 1
                    aug_report, pr, outcome = _attempt_proposal(
                        x=x, y=y, weights=weights, base_report=current, spec=spec,
                        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
                        absent_slot_area_fraction=absent_slot_area_fraction,
                        absent_slot_persistence_threshold=absent_slot_persistence_threshold,
                        diagnostic_windows=diagnostic_windows,
                        fit_full_window=fit_full_window,
                        endpoint_avg=endpoint_avg,
                    )
                    proposal_attempts.append((model.name, pr))
                    if outcome == "accepted" and aug_report is not None:
                        counts["n_acc"] += 1
                        # carry earlier rounds' accepted-peak reports forward
                        # (base_report starts with [], so round 1 is a no-op)
                        aug_report.proposed_peaks = (
                            list(current.proposed_peaks) + aug_report.proposed_peaks)
                        current = aug_report
                        pf = current.primary_fit
                        current_y_fit = (
                            pf.lmfit_result.best_fit + pf.background
                            if pf.lmfit_result is not None else np.zeros_like(y))
                        accepted_this_round = True
                        break
                    rejected.append(pr)
                    counts["n_fast" if outcome == "fast_rejected" else "n_stab"] += 1
                if not accepted_this_round:
                    break
            final_report = current
            if rejected:
                # rejected attempts stay visible on whichever report we emit
                final_report.proposed_peaks = final_report.proposed_peaks + rejected
            timings.append(ProposalPassTiming(
                candidate_name=model.name, n_flagged=counts["n_flagged"],
                n_over_cap=counts["n_over_cap"],
                n_attempted=counts["n_attempted"], n_fast_rejected=counts["n_fast"],
                n_stability_rejected=counts["n_stab"], n_accepted=counts["n_acc"],
                wall_time_sec=time.perf_counter() - pass_start, timed_out=timed_out,
            ))

        reports.append(final_report)

    result = rank_and_filter(
        reports,
        persistence_threshold=persistence_threshold,
        bic_ambiguity_threshold=bic_ambiguity_threshold,
        allow_last_resort=bool(preseed_specs),
    )
    result = _apply_decisive_override(
        x, y, weights, result,
        persistence_threshold=persistence_threshold,
        diagnostic_windows=diagnostic_windows,
        noise_floor=noise_floor,
        n_refits=n_refits,
        rng_seed=rng_seed,
        fit_full_window=fit_full_window,
        endpoint_avg=endpoint_avg,
    )
    result.non_converged = non_converged
    result.cross_candidate_coincidences = _cross_candidate_coincidences(proposal_attempts)
    result.proposal_pass_timings = timings
    result.analysis_truncated = analysis_truncated
    result.n_candidates_evaluated = n_evaluated
    result.n_candidates_total = n_cand
    # honest augmentation bookkeeping: every detected seed is surfaced;
    # the flag says whether it augmented the grammar families or rides in
    # the detection family only (GRAMMAR_AUGMENT_MAX_SEEDS cap)
    result.preseeded_features = [
autofit/methods/base.py:25:    success: bool
autofit/methods/multivariate_mcr.py:263:            method_id=self.id, success=True,
autofit/methods/sparse_map.py:209:            return MethodResult(method_id=self.id, success=False,
autofit/methods/sparse_map.py:264:                method_id=self.id, success=False,
autofit/methods/sparse_map.py:292:                "sigma_stat": {
autofit/methods/sparse_map.py:346:            method_id=self.id, success=True, peaks=peaks, analysis=analysis,
autofit/methods/ic_model_comparison.py:81:            "overall time budget was reached"
autofit/methods/ic_model_comparison.py:86:                method_id=self.id, success=False, peaks=[], analysis=analysis,
autofit/methods/ic_model_comparison.py:173:            method_id=self.id, success=True, peaks=peaks, analysis=analysis,
autofit/methods/ic_model_comparison.py:212:    lm = report.primary_fit.lmfit_result
autofit/methods/ic_model_comparison.py:232:            stderr = {}
autofit/methods/ic_model_comparison.py:234:                if pname.startswith(prefix) and par.stderr is not None:
autofit/methods/ic_model_comparison.py:235:                    stderr[pname[len(prefix):]] = float(par.stderr)
autofit/methods/ic_model_comparison.py:236:            if stderr:
autofit/methods/ic_model_comparison.py:237:                rec["stderr"] = stderr
autofit/methods/least_squares.py:71:            stderr = {name: info.get("stderr") for name, info in par.items()}
autofit/methods/least_squares.py:72:            has_cov = any(v is not None for v in stderr.values())
autofit/methods/least_squares.py:74:                "sigma_stat": {
autofit/methods/least_squares.py:76:                    "values": stderr if has_cov else None,
autofit/methods/least_squares.py:86:            success=bool(res["success"]),
autofit/methods/max_entropy.py:53:_ALLOWED_OPTIONS = set(DEFAULTS) | {"kernel_fwhm_ev", "noise_sigma"}
autofit/methods/max_entropy.py:104:        if "noise_sigma" in opts:
autofit/methods/max_entropy.py:105:            sigma = float(opts.pop("noise_sigma"))
autofit/methods/max_entropy.py:106:            sigma_source = "user"
autofit/methods/max_entropy.py:109:            sigma = float(1.4826 * np.median(np.abs(d2 - np.median(d2))) / np.sqrt(6.0))
autofit/methods/max_entropy.py:110:            sigma = max(sigma, 1e-12)
autofit/methods/max_entropy.py:111:            sigma_source = "estimated (MAD of 2nd difference) — supply noise_sigma for calibrated stopping"
autofit/methods/max_entropy.py:132:            chi_r = float(np.sum(((y_pos - model) / sigma) ** 2) / n)
autofit/methods/max_entropy.py:139:            ratio = conv(y_pos - model) / np.maximum(sigma ** 2, 1e-30)
autofit/methods/max_entropy.py:140:            f = f * np.exp(cfg["step_damping"] * ratio * sigma ** 2
autofit/methods/max_entropy.py:147:        chi_r = float(np.sum(((y_pos - conv(f)) / sigma) ** 2) / n)
autofit/methods/max_entropy.py:171:            "noise_sigma": sigma,
autofit/methods/max_entropy.py:172:            "noise_sigma_source": sigma_source,
autofit/methods/max_entropy.py:190:                        "severity is set by noise_sigma — for production use "
autofit/methods/max_entropy.py:191:                        "supply a repeat-sweep-derived noise_sigma; the MAD "
autofit/methods/max_entropy.py:196:            method_id=self.id, success=True,
autofit/methods/bayesian_exchange_mc.py:137:    rng = np.random.default_rng(rng_seed)
autofit/methods/bayesian_exchange_mc.py:235:    sigma_hat = float(np.median(np.sqrt(rss_samples / n)))
autofit/methods/bayesian_exchange_mc.py:243:        "sigma_hat": sigma_hat,
autofit/methods/bayesian_exchange_mc.py:336:        # re-check evidence: at reduced budgets a single run can report a
autofit/methods/bayesian_exchange_mc.py:387:                "sigma_hat": run["sigma_hat"],
autofit/methods/bayesian_exchange_mc.py:404:                method_id=self.id, success=False,
autofit/methods/bayesian_exchange_mc.py:424:        # is UNRESOLVED at this sweep budget — surfaced, never silent.
autofit/methods/bayesian_exchange_mc.py:457:            "likelihood": "gaussian_sigma_marginalized (processed-data model; "
autofit/methods/bayesian_exchange_mc.py:458:                          "Jeffreys prior on sigma)",
autofit/methods/bayesian_exchange_mc.py:482:            method_id=self.id, success=True, peaks=peaks, analysis=analysis,
autofit/methods/bayesian_exchange_mc.py:488:                "sigma_hat": scored[0]["sigma_hat"],
autofit/methods/bayesian_exchange_mc.py:555:                    "random-walk quantiles likely UNDERESTIMATE uncertainty; "
autofit/methods/bayesian_exchange_mc.py:560:            "sigma_stat": {
zsh:1: no matches found: /Users/skyefortier/xps-app/.venv/bin/python*

exec
/bin/zsh -lc "rg -n 'instructions|review|jitter|BLAS|2026-09-21' CLAUDE.md; sed -n '1,180p' scripts/fit_termination_scope.py; cat scripts/fit_termination_scope_analyze.py; rg -n 'CANDIDATE_TIMEOUT_SEC|TOTAL_ANALYSIS_TIMEOUT_SEC|WARM_RESTART_MAX_NFEV|PROPOSAL_STABILITY_TIMEOUT_SEC|SCREEN_BUDGET_FRACTION|budget_remaining|deadline=' --glob '*.py' .; rg -n 'sigma|stderr|_json_sanitize' app.py templates/index.html autofit/engine.py; ls /Users/skyefortier/xps-app/.claude; cat requirements.txt" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
49:| `POST`   | `/api/upload`             | Upload a spectrum file; returns `session_id` + downsampled preview. |
51:| `GET`    | `/api/session/<id>`       | Retrieve a stored session's preview data. |
187:When two places read the same input — the page and the server, a preview
191:a free η to the server (A03); the ROI, the preview background and the fitted
244:numbers carry Trust-Region's arithmetic jitter (≤ 0.25 meV, ≤ 5e-4 relative
301:were actually being fit against, due to a pre-existing preview/backend
449:**Reproducibility (2026-09-21).** Every random draw in `run_fit` — the
467:(in review each such no-op edit moved an area fraction by 15–45 pp
490:seeding: the BLAS dot product (Apple Accelerate on the i9) rounds one unit
496:perturbed restarts start from that jittering solution, and near a basin
504:OWNER DECISION 2026-09-21: ACCEPT AND DISCLOSE; no unit for bit-identity.
510:jitter flips the answer), so the scattered-starts cross-check unit is
512:second thing (a reviewer tried a deterministic perturbation base: identical
513:starts, results still differed; a reproducible-arithmetic BLAS is a large
521:**Scattered-starts check (step (a) of the 2026-09-21 unit; plan in
522:`docs/superpowers/plans/2026-09-21-scattered-starts-and-unsupported-components.md`).**
545:the largest move named, amber > 0.5 eV, red > 1 eV) with Preview (the
546:history-preview overlay, on a copy) and "Use this solution": explicit, one
564:the comparison no longer applies, nothing can be previewed or applied, an
565:open alternative preview is dropped (`_dropStaleAltPreview`), and
830:input is touched. Until 2026-09-21 only the centre was checked (±0.3 eV of
842:KNOWN LIMITS of that check (owner decision 2026-09-21: shipped with them
"""Scope check: do Run Fit's fits (main, perturbed restarts, scattered starts) end AT a minimum when they report success?
Every lmfit Model.fit call inside /api/fit is intercepted; each result is refined from its end point by a fresh
least_squares fit (same model, data, weights, bounds) and the relative chi2 drop recorded. Usage: OUT.jsonl METHOD"""
import sys, os, io, json, time
sys.path.insert(0, '.')
import numpy as np, lmfit
OUT, METHOD = sys.argv[1], sys.argv[2]
from app import create_app
app = create_app(); cl = app.test_client()
T = json.load(open('/Users/skyefortier/xps-app/.claude/worktrees/investigate-optimizer-disagreement/docs/findings/optimizer-disagreement/targets.json'))
done = set()
if os.path.exists(OUT):
    for l in open(OUT): done.add(json.loads(l)['id'])
orig = lmfit.Model.fit
calls = []
def fit(self, data, params=None, *a, **k):
    r = orig(self, data, params, *a, **k)
    if not calls or calls[-1] is not None:
        try:
            k2 = {kk: vv for kk, vv in k.items() if kk not in ('method', 'fit_kws', 'max_nfev', 'iter_cb')}
            calls.append(None)                     # refinement below must not be recorded
            ref = orig(self, data, r.params.copy(), *a, method='least_squares', **k2)
            calls.pop()
            calls.append({"method": k.get('method'), "success": bool(r.success), "nfev": int(r.nfev), "nvarys": int(r.nvarys),
                          "chisqr": float(r.chisqr), "refined": float(ref.chisqr), "redchi": float(r.redchi) if r.redchi is not None else None})
        except Exception as e:
            if calls and calls[-1] is None: calls.pop()
            calls.append({"method": k.get('method'), "error": str(e)[:80]})
    return r
lmfit.Model.fit = fit
A, B = (int(v) for v in os.environ.get('SCOPE_SLICE', '0:100000').split(':'))
for t in T[A:B]:
    if t['id'] in done: continue
    csv = "\n".join(f"{a:.4f},{b:.4f}" for a, b in zip(t["be"], t["inten"])).encode()
    r = cl.post("/api/upload", data={"file": (io.BytesIO(csv), "t.csv")}, content_type="multipart/form-data")
    sid = r.get_json()["session_id"]
    bg = t["background"]
    body = {"session_id": sid, "background": {k: bg[k] for k in ("method", "start_idx", "end_idx", "endpoint_avg")},
            "peaks": t["specs"], "fit_method": METHOD, "n_perturb": 3, "n_starts": 3}
    calls.clear(); t0 = time.time()
    resp = cl.post("/api/fit", json=body).get_json() or {}
    st = resp.get("starts") or {}
    with open(OUT, 'a') as f:
        f.write(json.dumps({"id": t["id"], "success": resp.get("success"), "starts_ran": st.get("ran"), "sec": round(time.time() - t0, 1),
                            "calls": [c for c in calls if c is not None]}) + "\n")
import json, sys, glob
sp = 'docs/findings/fit-termination-scope/'
for meth, files in (("Trust-Region (least_squares, page default)", ["scope_tr_a.jsonl", "scope_tr_b.jsonl"]), ("Levenberg-Marquardt (leastsq)", ["scope_lm_a.jsonl", "scope_lm_b.jsonl"])):
    rows = [json.loads(l) for f in files for l in open(sp + f)]
    drop = lambda c: (c["chisqr"] - c["refined"]) / c["chisqr"] if c.get("chisqr") else 0.0
    B = {"returned": [], "restart_ok": [], "start_ok": [], "start_failed_at_min": 0, "start_failed": 0}
    worst = []
    for r in rows:
        calls = [c for c in r["calls"] if "chisqr" in c]
        if not calls: continue
        head = calls[:4]; starts = calls[4:] if r.get("starts_ran") else []
        ok = [c for c in head if c["success"]]
        if r.get("success") and ok:
            ret = min(ok, key=lambda c: c["chisqr"])
            B["returned"].append(drop(ret)); worst.append((drop(ret), r["id"], ret["redchi"], ret["nfev"]))
        B["restart_ok"] += [drop(c) for c in head[1:] if c["success"]]
        for c in starts:
            if c["success"]: B["start_ok"].append(drop(c))
            else:
                B["start_failed"] += 1
                B["start_failed_at_min"] += drop(c) < 1e-6
    def dist(v):
        n = len(v)
        return f"n {n}: drop >1e-6 {sum(d > 1e-6 for d in v)}, >1e-3 {sum(d > 1e-3 for d in v)}, >1% {sum(d > 0.01 for d in v)}, >10% {sum(d > 0.1 for d in v)}"
    print("==", meth, f"({len(rows)} targets)")
    print("  returned fit (what the student gets), flagged success:", dist(B["returned"]))
    print("  perturbed restarts flagged success:                ", dist(B["restart_ok"]))
    print("  scattered starts flagged success:                  ", dist(B["start_ok"]))
    print(f"  scattered starts flagged FAILED: {B['start_failed']}, of which already at a minimum (refine drop < 1e-6): {B['start_failed_at_min']}")
    for d, i, rc, nf in sorted(worst, reverse=True)[:6]:
        print(f"     worst returned: {i}  chi2r {rc:.3f}  nfev {nf}  refine lowers chi2 by {100*d:.2f} %")
app.py:197:def _json_sanitize(obj):
app.py:203:        return {str(k): _json_sanitize(v) for k, v in obj.items()}
app.py:205:        return [_json_sanitize(v) for v in obj]
app.py:209:        return [_json_sanitize(v) for v in obj.tolist()]
app.py:526:        tmp.write_text(json.dumps(_json_sanitize(data)))
app.py:1144:        return jsonify(_json_sanitize(payload))
autofit/engine.py:1399:    sigma = np.sqrt(np.maximum(y, noise_floor))
autofit/engine.py:1400:    r_std = r / sigma
autofit/engine.py:1842:        local_sigma = float(np.median(np.sqrt(np.maximum(y_asc[mask], noise_floor)))) \
autofit/engine.py:1844:        if amp < PRESEED_AMPLITUDE_SNR * local_sigma:
autofit/engine.py:1860:            local_snr=amp / max(local_sigma, 1e-12),
autofit/engine.py:2000:    sigma = np.sqrt(np.maximum(y, noise_floor))
autofit/engine.py:2001:    r_std = r / sigma
autofit/engine.py:2217:    local_sigma = float(np.median(np.sqrt(np.maximum(y[mask], noise_floor)))) \
autofit/engine.py:2219:    if comp.amplitude < PROPOSAL_AMPLITUDE_SNR * local_sigma:
autofit/engine.py:2221:                     f"{PROPOSAL_AMPLITUDE_SNR:.1f} × local σ ({local_sigma:.2f})")
templates/index.html:3997:  const sigma = fwhm / (2 * Math.sqrt(2 * Math.log(2)));
templates/index.html:3998:  return Math.exp(-Math.pow(x - center, 2) / (2 * sigma * sigma));
templates/index.html:4120:  const sigma = mc / 3.0;
templates/index.html:4125:  for (let t = 0; t < K; t++) { const k = t - half; kern[t] = Math.exp(-(k * k) / (2.0 * sigma * sigma)); ksum += kern[t]; }
templates/index.html:4323:  const sigma = m / (2 * Math.sqrt(2 * Math.LN2));
templates/index.html:4327:  for (let t = 0; t < nTot; t++) { const kg = (t - kHalf) * step; kernel[t] = Math.exp(-0.5 * (kg / sigma) * (kg / sigma)); ksum += kernel[t]; }
templates/index.html:7172:// or sigma as if they were determined. The statement that needs no intensity
templates/index.html:7980:// Unit F1 (2026-09-25): the fit STATISTICS (chi-square, sigma, R-factor, RMSE
templates/index.html:8023:  // F1: chi-square / sigma / R follow the same key, from every caller (lock
templates/index.html:8589:  // the server — sigma = sqrt(raw counts), floored at 1, where the raw
templates/index.html:8919:  // results panel shows blank sigma for every parameter after a local fit.
templates/index.html:9015:  // F1: a stale result's sigma belongs to the previous model: none is shown
templates/index.html:9016:  const stderrMap = _stale ? {} : _buildStderrMap(state.fitResult);
templates/index.html:9076:    const par = stderrMap[String(p.id)] || {};
templates/index.html:9077:    const centerSE = par.center ? par.center.stderr : null;
templates/index.html:9078:    const fwhmSE   = par.fwhm   ? par.fwhm.stderr   :
templates/index.html:9079:                     par.fwhm_l ? par.fwhm_l.stderr  : null;
templates/index.html:9081:      // the fit did not determine this component: no centre, width or sigma is reported
templates/index.html:11784:  // F1: a stale result's chi-square and sigma belong to the previous model:
templates/index.html:11787:  const stderrMap = _stats === 'stale' ? {} : _buildStderrMap(state.fitResult);
templates/index.html:11811:    const par = stderrMap[String(p.id)] || {};
templates/index.html:11812:    const cse  = par.center?.stderr  ?? '';
templates/index.html:11813:    const fse  = (par.fwhm?.stderr ?? par.fwhm_l?.stderr) ?? '';
templates/index.html:11814:    const ase  = par.amplitude?.stderr ?? '';
templates/index.html:11817:      // the fit did not determine this component: no centre, width or sigma
templates/index.html:12032:  // F1: a stale result's sigma and bounds describe the previous model; the
templates/index.html:12037:  const stderrMap = _buildStderrMap(state.fitResult);
templates/index.html:12042:  for (const [rawId, params] of Object.entries(stderrMap)) {
templates/index.html:12058:      // Locked or linked: skip the alarm-style movement/stderr checks.
templates/index.html:12093:      // stderr AND the value barely moved → covariance matrix singular near
templates/index.html:12095:      // "converged at start with valid stderr" (silent — normal convergence).
templates/index.html:12096:      const se = pData.stderr;
templates/index.html:15313:    sigmaCenter: 'Statistical uncertainty in the fitted peak position (eV).',
templates/index.html:16351:    th('± position (eV)', T.sigmaCenter) + '</tr>' +
templates/index.html:16354:      const sc = conf.sigma_stat && conf.sigma_stat.values && conf.sigma_stat.values.center;
settings.json
settings.local.json
skills
worktrees
# XPS Peak Fitting – Python dependencies
# Install: pip install -r requirements.txt

flask>=3.0,<4
werkzeug>=3.0
gunicorn>=22.0

# Numerics & fitting
numpy>=1.26
scipy>=1.13
lmfit>=1.3

# File parsing
pandas>=2.2
openpyxl>=3.1       # .xlsx read/write

# Reference-data validation (data/xps/ against schema.json)
jsonschema>=4.21

# Optional – uncomment if you need CORS (e.g. separate frontend dev server)
# flask-cors>=4.0
olefile
gunicorn

exec
/bin/zsh -lc "ls /Users/skyefortier/xps-app/venv/bin /opt/homebrew/bin /usr/local/bin 2>/dev/null | rg 'python|pytest'; sed -n '300,395p' autofit/methods/bayesian_exchange_mc.py; sed -n '200,270p' autofit/methods/ic_model_comparison.py; sed -n '2320,2495p' autofit/engine.py; sed -n '480,515p' CLAUDE.md; sed -n '1,100p' tests/conftest.py; ls /Users/skyefortier/xps-app" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
pytest
python
python3
python3.12
python3.12
python3.12-config
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
                "but did not survive filtering "
                f"({result.filtered_dominant_alternative['filter_reason']})"
                if result.filtered_dominant_alternative else "")
                + (f" {truncation_note}." if truncation_note else "")),
        )


def _peaks_from_report(
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
        candidates.append({
            "name": name,
            "n_components": int(r.model.n_components),
            "reduced_chi_sq": float(r.reduced_chi_sq),
            "bic_star": float(r.bic_adjusted),
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
            clusters.append([e])
    out: list[CoincidenceReport] = []
    for c in clusters:
        bases = {e["base"] for e in c}
        if len(bases) < 2:
            continue
        per_base: dict[str, ProposedPeakReport] = {}
        for e in c:
            cur = per_base.get(e["base"])
            if cur is None or (e["pr"].accepted and not cur.accepted):
                per_base[e["base"]] = e["pr"]
        out.append(CoincidenceReport(
            center_be=float(np.median([e["be"] for e in c])),
            contributors=[(b, per_base[b].accepted) for b in sorted(per_base)],
        ))
    return out


# Bound the number of conditional candidates the override may refit — a
# runtime guard, not a statistical constant.
OVERRIDE_MAX_ATTEMPTS = 3


def _bound_fixed_refit(
    x: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray,
    report: ModelReport,
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
    y: np.ndarray,
    weights: np.ndarray,
    result: ComparisonResult,
    persistence_threshold: float,
    diagnostic_windows: dict[str, tuple[float, float]],
    noise_floor: float,
    n_refits: int,
    rng_seed: int,
    fit_full_window: bool = False,
    endpoint_avg: int = 1,
) -> ComparisonResult:
    """Dominance rule — see CONDITIONAL_OVERRIDE_DELTA_BIC block comment."""
    if result.conditional or not result.survivors:
        return result
    clean_best = result.survivors[0]
    # (4) the clean best must itself show residual-structure evidence
    if not (clean_best.residuals.autocorr_flag
            or clean_best.residuals.flagged_windows):
        return result
    pool = [r for r, why in result.filtered_out
            if why.startswith("plausibility")
            and r.active_min_persistence >= persistence_threshold]
    pool.sort(key=lambda r: r.bic_adjusted)

    for candidate in pool[:OVERRIDE_MAX_ATTEMPTS]:
        refit = _bound_fixed_refit(x, y, weights, candidate,
                                   diagnostic_windows, noise_floor,
                                   n_refits=n_refits, rng_seed=rng_seed,
                                   fit_full_window=fit_full_window,
                                   endpoint_avg=endpoint_avg)
        if refit is None:
            continue
        # the bound-fixed model must be STABLE in its own right
        if refit.active_min_persistence < persistence_threshold:
            continue
        # (2) very-strong BIC* margin AND (3) strictly better χ²ᵣ
        if not (refit.bic_adjusted + CONDITIONAL_OVERRIDE_DELTA_BIC
                < clean_best.bic_adjusted
                and refit.reduced_chi_sq < clean_best.reduced_chi_sq):
            continue
        result.reports.append(refit)
        result.survivors = [refit] + result.survivors  # clean kept as alternatives
        result.conditional = True
        result.conditional_reason = "decisive_override"
        return result
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Top-level driver — region-agnostic
# ─────────────────────────────────────────────────────────────────────────────

def _report_progress(
    progress_cb: Optional[Callable[[dict], None]],
    phase: str, idx: int, total: int, name: str,
) -> None:
    """Fire ``progress_cb`` for one candidate transition; never let a
    broken sink (e.g. a full disk on the progress-file writer) break the
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
"""Make the repo root importable regardless of how pytest is invoked."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
CLAUDE.md
DEPLOY.md
DESIGN.md
PRODUCT.md
__pycache__
app.py
autofit
data
docs
fitting.py
parser.py
requirements-dev.txt
requirements.txt
scripts
static
templates
tests
uploads
venv
vgd_parser.py
xps-fitting-tool.html
xps_reference.py

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -m pytest -q -p no:cacheprovider tests/autofit/test_fit_certificate.py tests/autofit/test_preseed_dominants.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 exited 1 in 178ms:
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pytest/__main__.py", line 9, in <module>
    raise SystemExit(pytest.console_main())
                     ^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 223, in console_main
    code = main()
           ^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 193, in main
    config = _prepareconfig(new_args, plugins)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 361, in _prepareconfig
    config: Config = pluginmanager.hook.pytest_cmdline_parse(
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 167, in _multicall
    raise exception
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 139, in _multicall
    teardown.throw(exception)
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/helpconfig.py", line 124, in pytest_cmdline_parse
    config = yield
             ^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 1192, in pytest_cmdline_parse
    self.parse(args)
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 1562, in parse
    self.hook.pytest_load_initial_conftests(
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 167, in _multicall
    raise exception
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 139, in _multicall
    teardown.throw(exception)
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/warnings.py", line 128, in pytest_load_initial_conftests
    return (yield)
            ^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 116, in _multicall
    next(function_gen)  # first yield
    ^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/capture.py", line 170, in pytest_load_initial_conftests
    capman.start_global_capturing()
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/capture.py", line 773, in start_global_capturing
    self._global_capturing = _get_multicapture(self._method)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/capture.py", line 714, in _get_multicapture
    return MultiCapture(in_=FDCapture(0), out=FDCapture(1), err=FDCapture(2))
                                              ^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/capture.py", line 493, in __init__
    TemporaryFile(buffering=0),
    ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 631, in TemporaryFile
    prefix, suffix, dir, output_type = _sanitize_params(prefix, suffix, dir)
                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 126, in _sanitize_params
    dir = gettempdir()
          ^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
    return _os.fsdecode(_gettempdir())
                        ^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
    tempdir = _get_default_tempdir()
              ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism']

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -m pytest -s -q -p no:cacheprovider tests/autofit/test_fit_certificate.py tests/autofit/test_preseed_dominants.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import inspect, lmfit; print(lmfit.__version__); print(inspect.getsource(lmfit.minimizer.Minimizer.least_squares))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 exited 1 in 1328ms:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
    from .confidence import conf_interval, conf_interval2d
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
    from .minimizer import MinimizerException
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
    from .parameter import Parameter, Parameters
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
    from .jsonutils import decode4js, encode4js
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
    import dill
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
    from .session import (
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                               ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
    return _os.fsdecode(_gettempdir())
                        ^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
    tempdir = _get_default_tempdir()
              ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism']

 exited 2 in 2176ms:

==================================== ERRORS ====================================
____________ ERROR collecting tests/autofit/test_fit_certificate.py ____________
tests/autofit/test_fit_certificate.py:16: in <module>
    import autofit.engine as eng
autofit/engine.py:38: in <module>
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
E   FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism']
___________ ERROR collecting tests/autofit/test_preseed_dominants.py ___________
tests/autofit/test_preseed_dominants.py:19: in <module>
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
E   FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism']
=========================== short test summary info ============================
ERROR tests/autofit/test_fit_certificate.py - FileNotFoundError: [Errno 2] No...
ERROR tests/autofit/test_preseed_dominants.py - FileNotFoundError: [Errno 2] ...
!!!!!!!!!!!!!!!!!!! Interrupted: 2 errors during collection !!!!!!!!!!!!!!!!!!!!
2 errors in 1.82s

exec
/bin/zsh -lc "sed -n '1500,1635p' /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py; rg -n 'def least_squares|ftol|_calculate_statistics' /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py; rg -n 'expr=|set\\(expr|update_constraints|support' autofit/engine.py | head -45; sed -n '1,115p' tests/autofit/test_preseed_dominants.py; sed -n '1,110p' autofit/methods/bayesian_exchange_mc.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
    def least_squares(self, params=None, max_nfev=None, **kws):
        """Least-squares minimization using :scipydoc:`optimize.least_squares`.

        This method wraps :scipydoc:`optimize.least_squares`, which has
        built-in support for bounds and robust loss functions. By default
        it uses the Trust Region Reflective algorithm with a linear loss
        function (i.e., the standard least-squares problem).

        Parameters
        ----------
        params : Parameters, optional
            Parameters to use as starting point.
        max_nfev : int or None, optional
            Maximum number of function evaluations. Defaults to
            ``2000*(nvars+1)``, where ``nvars`` is the number of variable
            parameters.
        **kws : dict, optional
            Minimizer options to pass to :scipydoc:`optimize.least_squares`.

        Returns
        -------
        MinimizerResult
            Object containing the optimized parameters and several
            goodness-of-fit statistics.


        .. versionchanged:: 0.9.0
           Return value changed to :class:`MinimizerResult`.

        """
        result = self.prepare_fit(params)
        result.method = 'least_squares'

        replace_none = lambda x, sign: sign*np.inf if x is None else x
        self.set_max_nfev(max_nfev, 2000*(result.nvarys+1))

        start_vals, lower_bounds, upper_bounds = [], [], []
        for vname in result.var_names:
            par = self.params[vname]
            start_vals.append(par.value)
            lower_bounds.append(replace_none(par.min, -1))
            upper_bounds.append(replace_none(par.max, 1))

        least_squares_kws = dict(jac='2-point', method='trf', ftol=1e-08,
                                 xtol=1e-08, gtol=1e-08, x_scale=1.0,
                                 loss='linear', f_scale=1.0, diff_step=None,
                                 tr_solver=None, tr_options={},
                                 jac_sparsity=None, max_nfev=2*self.max_nfev,
                                 verbose=0, kwargs={})

        least_squares_kws.update(self.kws)
        least_squares_kws.update(kws)

        if least_squares_kws.get('Dfun', None) is not None:
            least_squares_kws['jac'] = least_squares_kws.pop('Dfun')

        if callable(least_squares_kws['jac']):
            self.jacfcn = least_squares_kws['jac']
            least_squares_kws['jac'] = self._jacobian

        least_squares_kws['kwargs'].update({'apply_bounds_transformation': False})
        result.call_kws = least_squares_kws

        try:
            ret = least_squares(self.__residual, start_vals,
                                bounds=(lower_bounds, upper_bounds),
                                **least_squares_kws)
            result.residual = ret.fun
        except AbortFitException:
            ret = None
            result.aborted = True

        # Note: scipy.optimize.least_squares is actually returning the
        # "last evaluation", which is not necessarily the "best result"; so we
        # do that here for consistency
        if not result.aborted:
            result.nfev -= 1
            result.residual = self.__residual(ret.x, False)
        elif result.nfev > self.max_nfev-5:
            result.nfev -= 2
            _best = result.last_internal_values
            result.residual = self.__residual(_best, False)
        result._calculate_statistics()

        if not result.aborted:
            for attr in ret:
                outattr = attr
                if attr == 'nfev':
                    outattr = 'least_squares_nfev'
                setattr(result, outattr, ret[attr])

            result.x = np.atleast_1d(result.x)

            # calculate the cov_x and estimate uncertainties/correlations
            try:
                if issparse(ret.jac):
                    hess = (ret.jac.T * ret.jac).toarray()
                elif isinstance(ret.jac, LinearOperator):
                    identity = np.eye(ret.jac.shape[1], dtype=ret.jac.dtype)
                    hess = (ret.jac.T * ret.jac) * identity
                else:
                    hess = np.matmul(ret.jac.T, ret.jac)
                result.covar = np.linalg.inv(hess)
                self._calculate_uncertainties_correlations()
            except LinAlgError:
                pass

        return result

    def leastsq(self, params=None, max_nfev=None, **kws):
        """Use Levenberg-Marquardt minimization to perform a fit.

        It assumes that the input Parameters have been initialized, and a
        function to minimize has been properly set up. When possible, this
        calculates the estimated uncertainties and variable correlations
        from the covariance matrix.

        This method calls :scipydoc:`optimize.leastsq` and, by default,
        numerical derivatives are used.

        Parameters
        ----------
        params : Parameters, optional
            Parameters to use as starting point.
        max_nfev : int or None, optional
            Maximum number of function evaluations. Defaults to
            ``2000*(nvars+1)``, where ``nvars`` is the number of variable
            parameters.
        **kws : dict, optional
            Minimizer options to pass to :scipydoc:`optimize.leastsq`.

        Returns
        -------
        MinimizerResult
            Object containing the optimized parameters and several
            goodness-of-fit statistics.
312:    def _calculate_statistics(self):
1018:        result._calculate_statistics()
1477:            result._calculate_statistics()
1480:        # This should eventually be moved into result._calculate_statistics.
1500:    def least_squares(self, params=None, max_nfev=None, **kws):
1543:        least_squares_kws = dict(jac='2-point', method='trf', ftol=1e-08,
1582:        result._calculate_statistics()
1651:        lskws = dict(Dfun=None, full_output=1, col_deriv=0, ftol=1.5e-8,
1692:            result._calculate_statistics()
1783:        result._calculate_statistics()
1965:        result._calculate_statistics()
2092:        result._calculate_statistics()
2169:        result._calculate_statistics()
2249:        result._calculate_statistics()
96:# basin as the best minimum (best_basin_support) — reporting-only honesty
364:              expr=f"{parent_prefix}{wname} + {prefix}fwhm_excess")
366:        p.add(f"{prefix}{wname}", value=0.0, expr=f"{parent_prefix}{wname}")
371:              expr=slot.fwhm_linked_to)
379:            p.add(f"{prefix}{name}", value=0.0, expr=f"{parent_prefix}{name}")
516:                  expr=f"{parent_prefix}center + {prefix}offset")
520:                  expr=f"{parent_prefix}center + {offs_lo}")
578:                  expr=(f"{parent_prefix}amplitude * {ratio_expr} * "
582:                  expr=f"{parent_prefix}amplitude * {ratio_expr}")
1144:    best_basin_support: int = 0
1254:    basin_support = sum(1 for c in refit_chis
1261:        best_basin_support=basin_support,
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
    # in-window features are never seeded, however large
    assert all(not (195.5 <= s.center_init <= 197.5) for s in specs)


def test_detection_descending_grid_equivalence():
    """Real raw_be grids DESCEND — detection must be order-invariant
    (np.interp-class bug family; the noise-model unit's lesson)."""
    x = _grid(186.0, 205.0)
    sig = (_pv(x, 30000.0, 191.0, 1.3, ETA)
           + _pv(x, 9000.0, 196.5, 1.2, ETA))
    y = _noisy(sig + _linear_bg(x), 7)
    cands = [_cand("P1", [_slot("main_a", (195.5, 197.5))])]
    grammar = _grammar(cands)
    bg = eng._compute_background(x, y, grammar.candidates[0].background)
    asc = eng.detect_out_of_grammar_dominants(
        x, y, bg, grammar.candidates, dict(grammar.diagnostic_windows))
    desc = eng.detect_out_of_grammar_dominants(
        x[::-1], y[::-1], bg[::-1], grammar.candidates,
        dict(grammar.diagnostic_windows))
    assert len(asc) == len(desc) == 1
    assert asc[0].center_init == pytest.approx(desc[0].center_init, abs=1e-9)


# ── F1+F2 end-to-end: the committed multi-environment regression case ─────

"""
Method 3 — Bayesian spectral decomposition by replica-exchange Monte Carlo
(the window flagship; decision matrix entry 3).

Literature basis (all DOIs verified in the decision matrix):
- Nagata, Sugita & Okada, "Bayesian spectral deconvolution with the
  exchange Monte Carlo method", Neural Networks 25 (2012) 82,
  DOI 10.1016/j.neunet.2011.12.001 — replica exchange over an inverse-
  temperature ladder; Bayes free energy by thermodynamic integration /
  stepping-stone across the ladder; model (peak-count) selection by F.
- Tokuda, Nagata & Okada, JPSJ 86 (2017) 024001,
  DOI 10.7566/JPSJ.86.024001 — joint estimation of noise level and number
  of peaks in the same framework.
- Kumazoe/Akai et al., Sci. Rep. 13 (2023) 13221 — XPS application.

Implementation choices (documented; all sampler knobs are UNVERIFIED
tunables in the spec-§9 sense):

- Likelihood: Gaussian iid with UNKNOWN σ, log-marginalized analytically —
  for processed (non-count) XPS intensities a Gaussian model with an
  estimated noise scale is the defensible default (fitalg LIMITATIONS §8;
  spec §5).  With Jeffreys prior p(σ) ∝ 1/σ the σ-marginal log-likelihood
  is  −(n/2)·log RSS(θ) + const,  so the sampler targets RSS directly and
  the noise estimate  σ̂² = RSS/n  is a per-sample by-product (reported
  from the posterior).
- Priors: uniform within each free parameter's grammar bounds — the same
  physically-motivated bounds the least-squares path uses (an explicit,
  honest prior; spec's evidence-engine stance).
- Tempering: β ∈ geometric ladder from β_min to 1 plus β = 0 (the prior
  replica), K replicas.  Random-walk Metropolis within replicas (per-
  parameter Gaussian steps scaled to the prior width), adjacent-pair
  exchange sweeps.  Step sizes adapt toward a target acceptance DURING
  BURN-IN ONLY and are frozen afterwards (detailed balance).
- Bayes free energy: stepping-stone estimator across the ladder,
  F = −log Z(1) + log Z(0) = −Σ_k log⟨exp(−(β_{k+1}−β_k)·nE)⟩_{β_k},
  with E = ½·log-RSS energy from the σ-marginal likelihood (see
  _log_likelihood).  Log-sum-exp stabilized.
- Model (peak-count) selection: run every grammar candidate, compare F;
  report ΔF and the posterior model weights ∝ exp(−F).
- Uncertainty: per-parameter posterior median + central credible interval,
  reported with uncertainty_kind='posterior_ci' — a NEW typed kind, never
  mixed with 'covariance'/'stability_mad' numerics (spec §5 discipline).

Determinism: fully seeded (rng_seed).  Runtime scales with
n_replicas × n_sweeps × n_free_params × cost(model eval); defaults target
minutes on real regions — tests use reduced settings on synthetic spectra.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

import numpy as np

from ..engine import (
    _compute_background,
    _default_params_from_slots,
    _build_composite_model,
    _extract_fitted_components,
    _slot_prefix,
)
from ..grammar import BACKEND_SHAPE, CandidateGrammar, CandidateModel
from .base import MethodResult, PeakFitMethod, pop_endpoint_avg

# ── UNVERIFIED sampler tunables (defaults; all overridable via options) ──────
DEFAULT_N_REPLICAS = 12
DEFAULT_BETA_MIN = 1e-4
DEFAULT_N_SWEEPS = 1500
DEFAULT_BURN_FRACTION = 0.5
DEFAULT_EXCHANGE_EVERY = 5
DEFAULT_TARGET_ACCEPT = 0.30
DEFAULT_CI_LEVEL = 0.68              # central credible interval (1σ-like)
INITIAL_STEP_FRACTION = 0.05         # of each prior width
ESS_RELIABLE_MIN = 50                # CI trust floor — UNVERIFIED tunable


@dataclass
class _ParamSpace:
    """Free-parameter view of a CandidateModel's lmfit Parameters."""
    names: list[str]
    lows: np.ndarray
    highs: np.ndarray
    params: Any                       # lmfit Parameters (exprs resolve here)
    composite: Any                    # lmfit composite Model

    def model_eval(self, x: np.ndarray, theta: np.ndarray) -> np.ndarray:
        for name, v in zip(self.names, theta):
            self.params[name].value = float(v)
        # update_constraints resolves expression-linked params (doublets etc.)
        self.params.update_constraints()
        return self.composite.eval(self.params, x=x)


def _param_space(model: CandidateModel, x, y_net) -> _ParamSpace:
    params = _default_params_from_slots(model, x=x, y_net=y_net)
    composite = _build_composite_model(model)
    names, lows, highs = [], [], []
    for name, par in params.items():
        if not par.vary or par.expr is not None:
            continue
        if not (np.isfinite(par.min) and np.isfinite(par.max)) or par.max <= par.min:
            raise ValueError(
                f"Bayesian sampler requires finite prior bounds; {name} has "
                f"[{par.min}, {par.max}]"
            )
        names.append(name)
        lows.append(par.min)
        highs.append(par.max)
    return _ParamSpace(names=names, lows=np.array(lows), highs=np.array(highs),

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"-s\", \"-q\", \"-p\", \"no:cacheprovider\", \"tests/autofit/test_fit_certificate.py\", \"tests/autofit/test_preseed_dominants.py\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import runpy; t=runpy.run_path(\"tests/autofit/test_fit_certificate.py\"); e=t[\"eng\"]; x,y,w,m=t[\"_two_peak\"](); good=e.fit_candidate(x,y,w,m); print(\"good\",good.weighted_chi_sq); comp=e._build_composite_model(m); p=good.lmfit_result.params.copy(); p[\"s_a_center\"].set(value=284.05); p[\"s_b_amplitude\"].set(value=50.0); p[\"s_a_fwhm\"].set(value=2.3); 
for cap in [1,2,3,5,10,20,6000]:
 o=e.fit_candidate(x,y,w,m,initial_params=p.copy(),max_nfev=cap); print(\"cap\",cap,\"converged\",o.converged,\"chi\",o.weighted_chi_sq,\"nfev\",o.lmfit_result.nfev if o.lmfit_result else None,\"success\",o.lmfit_result.success if o.lmfit_result else None)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 2519ms:
/Users/skyefortier/.matplotlib is not a writable directory
good 284.3481507665295
cap 1 converged False chi 958664.2131176789 nfev 1 success False
cap 2 converged True chi 959072.7404457228 nfev 2 success False
cap 3 converged True chi 959019.3151637658 nfev 3 success False
cap 5 converged True chi 959014.4346318296 nfev 5 success False
cap 10 converged True chi 284.3481507666807 nfev 10 success False
cap 20 converged True chi 284.34815076653103 nfev 14 success True
cap 6000 converged True chi 284.34815076653314 nfev 14 success True

codex
I found a test coverage gap: the clock-independence test uses one candidate, so it never exercises screening. The certificate tests do use real fits, and they’re running now. I’m also probing capped restarts directly. The documented winner changes have distinct causes: two lose MG2 during screening; the third removes an absent-slot credit created by failed-refit counts.

exec
/bin/zsh -lc "rg -n 'max_nfev|success|model.fit\\(' fitting.py | head -60; nl -ba autofit/engine.py | sed -n '812,860p'; nl -ba tests/autofit/test_preseed_dominants.py | sed -n '415,460p'; nl -ba docs/superpowers/plans/2026-09-29-a1-find-peaks-determinism.md | tail -45; rg -n 'Scan_6|MG2' tests/autofit/test_real_c1s* tests/autofit/*gate* 2>/dev/null; rg -n 'test_.*(bound|linked|doublet|cert|screen|clock)' tests/autofit --glob '*.py' | head -65" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
1097:    reported as bounds) and ``run_fit`` does not call it a success.
1105:    found = model.fit(y_sub, boxed, x=x, weights=weights, **kws, **_cancel_kw())
1116:        refined = model.fit(y_sub, free, x=x, weights=weights, **refine_kws, **_cancel_kw())
1130:    if refined.success:
1141:    peak in a wide box it can converge, "successfully", with the component
1153:        local = model.fit(y_sub, start, x=x, weights=weights,
1158:    if not local.success:
1161:    if searched.box_unverified or not searched.success or local.chisqr < searched.chisqr:
1172:# lmfit 1.3 sets MinimizerResult.success = True before minimising and its
1190:    found = model.fit(y_sub, start.copy(), x=x, weights=weights, **kws, **_cancel_kw())
1193:        refined = model.fit(y_sub, found.params.copy(), x=x, weights=weights,
1195:        if refined.success:
1201:        found.success = False
1206:        local = model.fit(y_sub, start.copy(), x=x, weights=weights, method="least_squares", nan_policy=nan_policy,
1211:    if local.success and (not candidate.success or local.chisqr < candidate.chisqr):
1391:        if not trial.success or trial.redchi is None or not np.isfinite(trial.redchi):
1495:    if not refit.success or getattr(refit, "box_unverified", False):
1526:            "refit_converged": bool(refit.success)}
1565:                    individual_peaks, statistics, charge_shift_applied, success
1794:        return model.fit(y_sub, params, x=x, weights=weights, **seeded(kws), **_cancel_kw())
1815:        log.debug("═══ FIT DONE ═══  success=%s  nfev=%s  message=%s",
1816:                  result.success, result.nfev, result.message)
1831:    if n_perturb > 0 and result.success and kws.get("method") != "basinhopping":
1863:                if trial.success and trial_rank < best_rank:
1884:        elif not result.success:
1898:        if not result.success:
2021:    success, message = result.success, result.message
2026:        success = False
2033:        "success": success,
   812	# A fit has reached a minimum when a fresh descent from its end point cannot
   813	# improve chi2 by more than the descent's OWN stopping tolerance. The descent
   814	# is Trust-Region (scipy least_squares, native bounds): a Levenberg-Marquardt
   815	# restart from a stall point reproduces the stall (MINPACK's xtol test fires in
   816	# ~30 evaluations — the false convergence this replaces). Restarts are repeated
   817	# from each improved point; a FIXED number of them (a count, not a time); out
   818	# of restarts, or a non-finite restart, is "not converged". No new constant:
   819	# the tolerance is scipy's own least_squares ftol default, read from its
   820	# signature, and the improvement is relative (dimensionless, scale-free).
   821	import inspect as _inspect
   822	import scipy.optimize as _scipy_optimize
   823	CERTIFY_FTOL = float(_inspect.signature(_scipy_optimize.least_squares).parameters["ftol"].default)
   824	# A COUNT, set from measurement (unit A1, 8 committed C 1s scans × 4 gate
   825	# candidates, primaries + all refits = 208 fits): restarts needed to certify —
   826	# 1: 10, 2: 173, 3: 14, 4: 5, then one fit each at 5, 6, 8, 9, 11 and 21 (flat
   827	# valleys: each Trust-Region run stops on its own ftol while a whole restart
   828	# still gains more than that). 5 left four real minima uncertified (8-JT
   829	# Scan_5's MG2 and MG3 primaries, so MG lost to AG2 at chi2r 42.5).
   830	CERTIFY_MAX_RESTARTS = 50
   831	
   832	
   833	def _certify_minimum(composite, y_sub, result, x, weights, max_nfev):
   834	    """Return (the lowest-chi2 point reached, certified)."""
   835	    current = result
   836	    chi = float(result.chisqr) if result.chisqr is not None else float("nan")
   837	    if not np.isfinite(chi):
   838	        return current, False
   839	    for _ in range(CERTIFY_MAX_RESTARTS):
   840	        try:
   841	            r = composite.fit(y_sub, current.params.copy(), x=x, weights=weights,
   842	                              method="least_squares", nan_policy="omit",
   843	                              max_nfev=max_nfev)
   844	        except Exception as exc:
   845	            log.debug("certificate restart raised: %s", exc)
   846	            return current, False
   847	        new = float(r.chisqr) if r.chisqr is not None else float("nan")
   848	        if not np.isfinite(new):
   849	            return current, False
   850	        improvement = (chi - new) / chi if chi > 0 else 0.0
   851	        if new < chi:
   852	            current, chi = r, new
   853	        if improvement < CERTIFY_FTOL:
   854	            return current, True
   855	    return current, False
   856	
   857	
   858	def fit_candidate(
   859	    x: np.ndarray,
   860	    y: np.ndarray,
   415	    m0 = CandidateModel(name="Y", background=eng.BackgroundType.LINEAR,
   416	                        slots=(slot("main_a"),))
   417	    assert eng._next_proposal_index(m0) == 0
   418	
   419	
   420	def test_no_wall_clock_can_change_the_answer(monkeypatch):
   421	    """Unit A1 (2026-09-29): the sweep, screen, stability and proposal
   422	    budgets were wall-clock and made the answer depend on server load; they
   423	    are gone. A clock that jumps a million seconds on every read must leave
   424	    the result IDENTICAL."""
   425	    x = _grid()
   426	    truth = [{"center": 196.5, "fwhm": 1.2, "height": 9000.0},
   427	             {"center": 201.5, "fwhm": 1.2, "height": 2500.0}]
   428	    sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
   429	    y = _noisy(sig + _linear_bg(x), 71)
   430	    grammar = _grammar([_cand("single_main", [_slot("main_a", (195.5, 197.5))])])
   431	
   432	    def run():
   433	        res = get_method("ic_model_comparison").run(x, y, grammar=grammar, options={**IC_OPTS, "enable_preseed": False})
   434	        return res.diagnostics, res.peaks, res.analysis, res.confidence
   435	
   436	    normal = run()
   437	    ticks = {"t": 0.0}
   438	
   439	    def jumpy():
   440	        ticks["t"] += 1.0e6
   441	        return ticks["t"]
   442	    monkeypatch.setattr(eng.time, "perf_counter", jumpy)
   443	    assert run() == normal
   444	
   445	
   446	# ── F3: two-phase sweep ────────────────────────────────────────────────────
   447	
   448	def _many_candidate_grammar(x, y):
   449	    """SCREEN_TOP_K+2 candidates: a ladder of window variants, several of
   450	    which cannot express the data (wrong windows)."""
   451	    good = [
   452	        _cand("G1", [_slot("main_a", (195.5, 197.5))]),
   453	        _cand("G2", [_slot("main_a", (195.5, 197.5)),
   454	                     _slot("comp_b", (198.5, 200.5))]),
   455	    ]
   456	    bad = [
   457	        _cand(f"B{i}", [_slot("main_a", (200.5 + i * 0.2, 202.5 + i * 0.2))])
   458	        for i in range(eng.SCREEN_TOP_K)
   459	    ]
   460	    return _grammar(good + bad)
    54	uncertified (8-JT Scan_5's MG2 and MG3 primaries → AG2 at chi2r 42.5 won); 50
    55	certifies all 208. 75 fits `leastsq` flagged as FAILED were certified (capped
    56	at a minimum — the Scan_6 case), none of 208 left uncertified.
    57	
    58	**Acceptance — Scan_6.** Gate options: MG2 (chi2r 2.03), as main with budgets
    59	off; main under load had given AG2.
    60	
    61	**Acceptance — load.** The page's own request (conductor, C 1s, proposals on,
    62	n_refits 4, endpoint average 3; full grammar, 29–30 candidates screened, 6
    63	deep) on 1-GTA Scan_6 and 8-JT Scan_7, idle, idle again, and with 8 CPU
    64	burners (load average 11):
    65	
    66	| | structural fields (winner, tier, candidate set, filter reasons, persistence, ranks, peak roles) | max Δcentre | max rel Δamplitude | max Δarea % |
    67	|---|---|---|---|---|
    68	| idle vs idle | identical (both scans) | 0.20 meV | 3.9e-4 | 7.6e-4 pp |
    69	| idle vs heavy | identical (both scans) | 0.24 meV | 4.9e-4 | 9.4e-4 pp |
    70	
    71	The residual numeric differences are Trust-Region's arithmetic jitter (the
    72	BLAS alignment effect CLAUDE.md records; owner decision 2026-09-21 accept and
    73	disclose), present idle-to-idle — not load. Find Peaks used only the
    74	byte-reproducible Levenberg-Marquardt before; the certificate's Trust-Region
    75	restarts bring the jitter in. Wall time (page request, idle): main 208–213 s,
    76	A1 236–239 s; under load A1 342–350 s (main would have truncated).
    77	
    78	**Screen interaction (found here).** With every screen fit certified to a
    79	genuine local minimum, the screen now compares honest minima — and MG2's
    80	single screen start on 8-JT Scan_7 lands in a poor one (BIC* 2277, as on main)
    81	while most others improve, so MG2 ranks 19th of 28 and is screened out,
    82	though its deep evaluation reaches the best BIC* of all. Page request: main
    83	MG2 (BIC* 1776.8) vs A1 MG3 (1787.6). Measurement on six more scans: §3.
    84	
    85	## 3. The page's own Find Peaks request: main vs A1 (7 distinct committed C 1s scans, idle)
    86	
    87	4 of 7 winners identical (UCl4 Scan_8, UCl4 Scan_3, 1-GTA Scan, 1-GTA Scan_6 —
    88	the last MG2 on both). 3 differ:
    89	
    90	| scan | main (winner, BIC*) | A1 (winner, BIC*) | why |
    91	|---|---|---|---|
    92	| 8-JT Scan_5 | MG2, 1882.6 | MG3, 1901.5 | MG2 SCREENED OUT on A1 (screen rank 21 of 28) — its single screen start lands in a poor local minimum while the certificate carries most other screen fits to much better ones |
    93	| 8-JT Scan_7 | MG2, 1776.8 | MG3, 1787.6 | the same (MG2 screen rank 19 of 28) |
    94	| 1-GTA Scan_2 | MG3, 1803.9 | MG2, 1816.0 | MG3 deep-evaluated on both with the SAME chi2r 1.388; on main one MG3 slot was "absent" (BIC* drops its parameters) because refits the old flag called non-converged counted as empty; certified, the slot is populated in every refit — no credit. A1 is the honest one here |
    95	
    96	The two screen cases pick a model with a WORSE BIC* than main's. The screen's
    97	single-start ranking is pre-existing; the certificate changes which candidates
    98	it happens to favour. OWNER DECISION (see the report).
zsh:1: no matches found: tests/autofit/test_real_c1s*
tests/autofit/test_preseed_dominants.py:420:def test_no_wall_clock_can_change_the_answer(monkeypatch):
tests/autofit/test_preseed_dominants.py:463:def test_screen_phase_records_and_selects():
tests/autofit/test_stage2_rereview_findings.py:29:from test_engine_doublet import _doublet_model, _doublet_spectrum
tests/autofit/test_region_provenance_honesty.py:80:def test_c1s_aliphatic_linked_offset_range_has_provenance_entry():
tests/autofit/test_fit_certificate.py:98:def test_a_fit_capped_at_the_minimum_is_certified():
tests/autofit/test_fit_full_window_option.py:59:def test_default_leaves_curated_bounds_untouched():
tests/autofit/test_fit_full_window_option.py:100:def test_full_window_never_narrows_or_inverts_a_bound_when_roi_is_shifted():
tests/autofit/test_fit_full_window_option.py:166:def test_full_window_leaves_linked_slot_offset_and_curated_starting_guess_untouched():
tests/autofit/test_fit_full_window_option.py:222:def test_default_clamps_an_out_of_window_component_to_the_bound():
tests/autofit/test_progress_callback.py:70:def test_progress_cb_reports_screening_then_stabilizing_phase(monkeypatch):
tests/autofit/test_bayesian_method.py:92:def test_uncertainty_typed_and_honest(result):
tests/autofit/test_cwt_detector.py:86:def test_close_doublet_both_detected():
tests/autofit/test_coverage_index.py:175:def test_partially_covered_doublets_never_trust_a_single_position_span(index):
tests/autofit/test_max_entropy.py:52:def test_sharpening_improves_doublet_contrast(result):
tests/autofit/test_max_entropy.py:68:def test_artifact_structure_bounded_relative_to_real_features(result):
tests/autofit/test_max_entropy.py:98:def test_interior_artifacts_bounded_and_true_peaks_dominate(result):
tests/autofit/test_sparse_map.py:79:def test_uncertainty_is_honestly_unavailable(result):
tests/autofit/test_sparse_map.py:129:def test_lambda_max_boundary_behavior():
tests/autofit/test_coverage_structure.py:71:def test_doublet_singlet_structure():
tests/autofit/test_endpoint_avg_wiring.py:198:def test_endpoint_avg_bound_is_shared_with_the_panel_max():
tests/autofit/test_stress_honesty.py:47:def test_resolved_doublet_recovered_clean(sep1):
tests/autofit/test_stress_honesty.py:58:def test_resolved_doublet_ls_baseline(sep1):
tests/autofit/test_stress_honesty.py:69:def test_resolved_doublet_sparse_count_only():
tests/autofit/test_engine_doublet.py:51:def test_fixed_ratio_doublet():
tests/autofit/test_engine_doublet.py:67:def test_relaxed_ratio_doublet_recovers_true_ratio():
tests/autofit/test_engine_doublet.py:79:def test_relaxed_ratio_at_bound_is_boundary_hit():
tests/autofit/test_engine_doublet.py:90:def test_doublet_stability_persistence():

 succeeded in 45314ms:
....................
20 passed in 44.84s

exec
/bin/zsh -lc "sed -n '300,336p' /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py; sed -n '1770,1895p' fitting.py; sed -n '460,510p' tests/autofit/test_preseed_dominants.py; sed -n '1,130p' tests/autofit/test_engine_doublet.py; rg -n 'gate|Scan_6' tests/autofit --glob '*.py' | head -45; sed -n '195,211p' app.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
        if hasattr(self, 'candidates'):
            if candidate_nmb == 'all':
                for i, candidate in enumerate(self.candidates):
                    print(f"\nCandidate #{i + 1}, chisqr = {candidate.score:.3f}")
                    candidate.params.pretty_print()
            elif (candidate_nmb < 1 or candidate_nmb > len(self.candidates)):
                raise ValueError(f"'candidate_nmb' should be between 1 and {len(self.candidates)}.")
            else:
                candidate = self.candidates[candidate_nmb-1]
                print(f"\nCandidate #{candidate_nmb}, chisqr = {candidate.score:.3f}")
                candidate.params.pretty_print()

    def _calculate_statistics(self):
        """Calculate the fitting statistics."""
        self.nvarys = len(self.init_vals)
        if not hasattr(self, 'residual'):
            self.residual = -np.inf
        if isinstance(self.residual, np.ndarray):
            self.chisqr = (self.residual**2).sum()
            self.ndata = len(self.residual)
            self.nfree = self.ndata - self.nvarys
        else:
            self.chisqr = self.residual
            self.ndata = 1
            self.nfree = 1
        self.redchi = self.chisqr / max(1, self.nfree)
        # this is -2*loglikelihood
        self.chisqr = max(self.chisqr, 1.e-250*self.ndata)
        _neg2_log_likel = self.ndata * np.log(self.chisqr / self.ndata)
        self.aic = _neg2_log_likel + 2 * self.nvarys
        self.bic = _neg2_log_likel + np.log(self.ndata) * self.nvarys

    def _repr_html_(self, show_correl=True, min_correl=0.1):
        """Return a HTML representation of parameters data."""
        report = fitreport_html_table(self, show_correl=show_correl,
                                      min_correl=min_correl)
        return f"<h2>Fit Result</h2> {report}"
    # refined under the request's own bounds (_search_then_refine). Every
    # other method fits the request's parameters exactly as before.
    def seeded(call_kws):
        """``call_kws`` with a fresh solver seed for the stochastic methods
        (one per minimisation, else every perturbed restart of differential
        evolution would replay the same population); unchanged otherwise."""
        if call_kws.get("method") not in _STOCHASTIC_METHODS:
            return call_kws
        solver_kws = dict(call_kws.get("fit_kws") or {})
        solver_kws["seed"] = int(solver_rng.integers(0, 2 ** 32 - 1))
        return {**call_kws, "fit_kws": solver_kws}

    # One fitter for any (sub)model of this request: the DE candidate machinery
    # when the method is differential evolution, else a plain seeded fit. The
    # scattered starts and the required-component refit go through it too.
    requested_bounds = {name: (par.min, par.max) for name, par in all_params.items()}

    def fit_model(model, params):
        if kws.get("method") == "differential_evolution":
            bounds = {name: requested_bounds.get(name, (par.min, par.max)) for name, par in params.items()}
            return _global_or_local_candidate(model, params, bounds, y_sub, x, weights, seeded(kws))
        if kws.get("method") == "basinhopping":
            bounds = {name: requested_bounds.get(name, (par.min, par.max)) for name, par in params.items()}
            return _basinhopping_candidate(model, params, bounds, y_sub, x, weights, seeded(kws))
        return model.fit(y_sub, params, x=x, weights=weights, **seeded(kws), **_cancel_kw())

    def fit_once(params):
        return fit_model(composite_model, params)

    # ── Diagnostic logging: BEFORE optimisation ──────────────────────────────
    if log.isEnabledFor(logging.DEBUG):
        log.debug("═══ FIT START ═══  method=%s  n_data=%d", kws.get('method'), len(y_sub))
        for pname, par in sorted(all_params.items()):
            log.debug("  BEFORE  %-30s value=%12.6f  vary=%-5s  expr=%s  min=%s  max=%s",
                      pname, par.value, str(par.vary), par.expr,
                      f"{par.min:.4f}" if np.isfinite(par.min) else '-inf',
                      f"{par.max:.4f}" if np.isfinite(par.max) else 'inf')

    try:
        result = fit_once(all_params)
    except Exception as exc:
        raise RuntimeError(f"lmfit fitting failed: {exc}") from exc

    # ── Diagnostic logging: AFTER optimisation ───────────────────────────────
    if log.isEnabledFor(logging.DEBUG):
        log.debug("═══ FIT DONE ═══  success=%s  nfev=%s  message=%s",
                  result.success, result.nfev, result.message)
        for pname, par in sorted(result.params.items()):
            init = all_params[pname].value if pname in all_params else None
            delta = f"  Δ={par.value - init:+.6f}" if init is not None and abs(par.value - init) > 1e-10 else ""
            log.debug("  AFTER   %-30s value=%12.6f  stderr=%s%s",
                      pname, par.value,
                      f"{par.stderr:.6f}" if par.stderr is not None else 'None', delta)

    # ── Perturb and refit to escape local minima ─────────────────────────
    # Not for basinhopping (unit F2, 2026-09-26, owner): it is already a global
    # search, so perturbed restarts add nothing — the reason the scattered-
    # starts check excludes it — and with the page's n_perturb 3 they
    # quadrupled its time past the server's 300 s timeout on 14 of 16 sampled
    # multi-component targets (median 386 s, max 1066 s; without them median
    # 96 s, max 256 s, and chi2r identical to 1e-8 on all 16).
    if n_perturb > 0 and result.success and kws.get("method") != "basinhopping":
        best_result = result
        best_redchi = result.redchi if result.redchi is not None else float('inf')
        rng = perturb_rng

        for attempt in range(n_perturb):
            perturbed_params = result.params.copy()
            for pname, par in perturbed_params.items():
                if par.vary and par.value != 0:
                    # Perturb by ±15% random
                    scale = 1.0 + rng.uniform(-0.15, 0.15)
                    new_val = par.value * scale
                    # Respect bounds
                    if np.isfinite(par.min):
                        new_val = max(new_val, par.min)
                    if np.isfinite(par.max):
                        new_val = min(new_val, par.max)
                    perturbed_params[pname].set(value=new_val)
                elif par.vary and par.value == 0:
                    # For zero-valued params, add small absolute perturbation
                    perturbed_params[pname].set(value=rng.uniform(0.001, 0.05))

            try:
                trial = fit_once(perturbed_params)
                trial_redchi = trial.redchi if trial.redchi is not None else float('inf')
                log.debug("  PERTURB %d/%d  redchi=%.4f  (best=%.4f)",
                          attempt + 1, n_perturb, trial_redchi, best_redchi)
                # A candidate whose search box was never cleared by its
                # refinement (differential evolution only) does not displace
                # one that was; for every other method both flags are False.
                trial_rank = (getattr(trial, "box_unverified", False), trial_redchi)
                best_rank = (getattr(best_result, "box_unverified", False), best_redchi)
                if trial.success and trial_rank < best_rank:
                    best_result = trial
                    best_redchi = trial_redchi
                    log.debug("  *** New best found! redchi improved to %.4f", best_redchi)
            except Exception:
                log.debug("  PERTURB %d/%d  failed (exception)", attempt + 1, n_perturb)
                continue

        if best_result is not result:
            log.debug("═══ PERTURB IMPROVED FIT ═══  redchi: %.4f → %.4f",
                      result.redchi, best_redchi)
            result = best_result

    # ── Scattered starts (never changes `result`) ────────────────────────────
    starts = None
    if n_starts:
        n_unlinked = sum(1 for spec in peak_specs if spec.get("constrain_to") is None)
        if kws.get("method") not in _STARTS_METHODS:
            starts = {"ran": False, "reason": "method"}          # a global method already searches
        elif n_unlinked < 2:
            starts = {"ran": False, "reason": "single_component"}
        elif not result.success:
            starts = {"ran": False, "reason": "fit_not_converged"}
        else:
            try:
                starts = _scattered_starts(int(n_starts), fit_once, composite_model, all_params, result,
                                           peak_specs, x, starts_rng)
            except Exception as exc:                              # the check must never cost the student the fit
                log.exception("scattered starts failed")
                starts = {"ran": False, "reason": "error", "error": f"{type(exc).__name__}: {exc}"[:200]}

    # ── "Is this component required?" (never changes `result`) ─────────────
    required = None
    return _grammar(good + bad)


def test_screen_phase_records_and_selects():
    """More candidates than SCREEN_TOP_K → the screen runs, every candidate
    appears in the record (nothing silent), at most TOP_K are selected, and
    the winner is still the structurally right model."""
    x, y, _ = _covered_spectrum(seed=13)
    grammar = _many_candidate_grammar(x, y)
    case_like = type("C", (), {"x": x, "y": y, "grammar": grammar})
    res = _ic(case_like)
    screen = res.analysis["screen"]
    assert screen is not None
    assert len(screen) == len(grammar.candidates)
    assert sum(1 for r in screen if r["selected"]) <= eng.SCREEN_TOP_K
    # every non-selected candidate is visible with its screen outcome
    for r in screen:
        assert set(r) >= {"name", "converged", "bic", "selected"}
    assert res.diagnostics["winner"].startswith("G2")


def test_small_candidate_set_takes_classic_path():
    """≤ SCREEN_TOP_K candidates → no screen phase (screen is None) — every
    existing gate/battery path is unchanged."""
    x, y, grammar = _covered_spectrum(seed=13)
    case_like = type("C", (), {"x": x, "y": y, "grammar": grammar})
    res = _ic(case_like)
    assert res.analysis["screen"] is None
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
    not dilute another region's satellite below the absent threshold."""
    from autofit.engine import (FitOutcome, ModelStability, SlotStability,
                                _identify_absent_slots)
    from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot

    def s(role, region, phase, main=False):
        return ComponentSlot(
            role=role, region=region, phase_id=phase,
            be_window=(0.0, 10.0), line_shape=LineShape.PSEUDO_VOIGT,
            fwhm_range=(0.5, 3.0),
tests/autofit/test_stage2_rereview_findings.py:50:# ── finding 3: orphan_peaks gates clean survivorship ─────────────────────────
tests/autofit/test_browser_schema_roundtrip.py:12:    every field — the "fail the build on any silent loss" gate);
tests/autofit/test_u4f_parity_battery.py:30:# Scan_6, a flat alpha/beta/m valley) wobbles at 1.4e-4 relative across
tests/autofit/test_u4f_parity_gate.py:2:Stage-3 U 4f parity gate (spec §3.2): the resolver + IC engine reproduce the
tests/autofit/test_u4f_parity_gate.py:15:Unlike the C 1s gate this one is FAST (3 U-candidates; ~20 s total), so it
tests/autofit/test_u4f_parity_gate.py:156:    # bad-state run) while keeping the χ²ᵣ window this gate stops policing
tests/autofit/test_bayesian_u4f_unresolved_gate.py:2:U 4f UNRESOLVED-model-selection gate (env-gated; Codex Stage-5 re-check
tests/autofit/test_bayesian_u4f_unresolved_gate.py:14:This gate pins that contract on the real spectrum.
tests/autofit/test_bayesian_u4f_unresolved_gate.py:16:    RUN_AUTOFIT_GATE=1 venv/bin/pytest tests/autofit/test_bayesian_u4f_unresolved_gate.py
tests/autofit/test_bayesian_u4f_unresolved_gate.py:25:        "SKIPPING U 4f unresolved-selection gate (~8 min) — set "
tests/autofit/test_c1s_parity_gate.py:2:Stage-2 C 1s parity gate (spec §0/§3.1): the resolver + IC engine must
tests/autofit/test_c1s_parity_gate.py:24:several minutes per anchor, so it is gated behind RUN_AUTOFIT_GATE=1 — run it
tests/autofit/test_c1s_parity_gate.py:27:    RUN_AUTOFIT_GATE=1 venv/bin/pytest tests/autofit/test_c1s_parity_gate.py
tests/autofit/test_c1s_parity_gate.py:39:    # LOUD skip (Codex Stage-2 finding #8): this is a REQUIRED Stage-2 gate.
tests/autofit/test_c1s_parity_gate.py:41:    # characterization battery.  Run this gate at every stage checkpoint and
tests/autofit/test_c1s_parity_gate.py:62:    ("1-GTA UCl4-graphite one set of U doublets.proj.zip", "C1s Scan_6"),
tests/autofit/test_c1s_parity_gate.py:75:# uniform 2.0 eV contamination cap (see PROGRESS.md parity-gate calibration
tests/autofit/test_c1s_parity_gate.py:76:# log).  Measured mains: Scan_2 4 meV (clean MG2), Scan_6 12 meV (clean
tests/autofit/test_c1s_parity_gate.py:86:# Scan_2/Scan_6 unchanged (0.004–0.014); Scan_8 0.0407 (conditional-tier
tests/autofit/test_c1s_parity_gate.py:91:# the gate disables for runtime).  Envelope parity is asserted on the
tests/autofit/test_c1s_parity_gate.py:112:def test_c1s_parity_gate(grammar, project, name):
tests/autofit/test_candidate_pool_wiring.py:10:- the pool (with provenance + gate outcomes + residual-gap merge) lands in
tests/autofit/test_candidate_pool_wiring.py:129:    fraction gate via monkeypatch to force the F2 path while the pool is
tests/autofit/test_cited_values.py:100:    """False-rejection pins for the alphanumeric-collapse placeholder gate
tests/autofit/test_cited_values.py:255:def test_schema_version_gate(tmp_path):
tests/autofit/test_cited_values.py:258:    # True == 1 in Python — a boolean must not satisfy the integer gate
tests/autofit/test_cited_values.py:261:    # 1.0 == 1 too — the gate is a strict INTEGER 1
tests/autofit/test_preseed_dominants.py:74:def test_detects_out_of_window_dominant_and_gates_weak_bump():
tests/autofit/test_preseed_dominants.py:76:    weak out-of-window bump (below the fraction-of-max gate) is NOT —
tests/autofit/test_preseed_dominants.py:80:           + _pv(x, 30000.0 * 0.10, 188.5, 1.2, ETA)  # weak bump, below gate
tests/autofit/test_preseed_dominants.py:123:    neighbor — historically below the 0.25 dominance gate and rescued by
tests/autofit/test_preseed_dominants.py:260:    # path (the channel with the accept gates); with preseed on it would be
tests/autofit/test_preseed_dominants.py:483:    existing gate/battery path is unchanged."""
tests/autofit/test_b1s_cl2p_parity_gates.py:2:B 1s and Cl 2p engine parity gates (region cookbook, spec §7).
tests/autofit/test_b1s_cl2p_parity_gates.py:17:  — expected weak-exemplar ambiguity (spec §3.3), not gated.
tests/autofit/test_b1s_cl2p_parity_gates.py:47:def test_b1s_parity_gate():
tests/autofit/test_b1s_cl2p_parity_gates.py:69:def test_cl2p_parity_gate(name):
tests/autofit/test_bayesian_real_gate.py:2:Bayesian exchange-MC REAL-DATA gate (env-gated like the C 1s parity gate):
tests/autofit/test_bayesian_real_gate.py:15:    RUN_AUTOFIT_GATE=1 venv/bin/pytest tests/autofit/test_bayesian_real_gate.py
tests/autofit/test_bayesian_real_gate.py:24:        "SKIPPING Bayesian real-data gate (~1 min) — set RUN_AUTOFIT_GATE=1 "
tests/autofit/battery_common.py:76:    # round 4 showed that gate accepting a corrupted envelope). A record left
tests/autofit/stress_cases.py:356:    weaker low-BE neighbor (below the preseed dominance gate — it must come
tests/autofit/stress_cases.py:370:                                                             #   22.5% of max, below gate)
tests/autofit/test_fit_certificate.py:8:18 000 evaluations AT the minimum counted as failed (1-GTA C1s Scan_6)."""
tests/autofit/test_fit_certificate.py:99:    """The Scan_6 case in general form: an optimiser that runs out of
# ─────────────────────────────────────────────────────────────────────────────

def _json_sanitize(obj):
    """Defensive numpy→native + non-finite→None conversion for
    /api/analyze payloads: a stray np scalar must not 500 the route, and
    inf/NaN (e.g. BIC of a degenerate fit) must not emit non-standard JSON
    that browsers refuse to parse."""
    if isinstance(obj, dict):
        return {str(k): _json_sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_sanitize(v) for v in obj]
    if isinstance(obj, np.generic):
        obj = obj.item()
    if isinstance(obj, np.ndarray):
        return [_json_sanitize(v) for v in obj.tolist()]
    if isinstance(obj, float) and not np.isfinite(obj):
        return None

exec
/bin/zsh -lc "rg -n 'check_required|n_starts|n_perturb|required_components' fitting.py app.py | tail -45; sed -n '1885,1925p' fitting.py; sed -n '110,150p' tests/autofit/test_c1s_parity_gate.py; sed -n '60,95p' tests/autofit/test_c1s_parity_gate.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
fitting.py:1233:def _request_seed(x, counts, background, shapes, prefixes, params, *, fit_kws, n_perturb) -> int:
fitting.py:1238:    solver options and ``n_perturb``.
fitting.py:1277:                       "n_perturb": n_perturb})
fitting.py:1378:def _scattered_starts(n_starts, fit_once, model, start_params, result, peak_specs, x, rng) -> dict[str, Any]:
fitting.py:1385:    for _ in range(n_starts):
fitting.py:1400:            clusters.append({"chi2r": float(trial.redchi), "n_starts": 1, "components": comps})
fitting.py:1402:            home["n_starts"] += 1
fitting.py:1412:        "ran": True, "n_run": n_starts, "n_converged": n_converged, "n_same_as_fit": n_same,
fitting.py:1414:        "n_in_alternatives": sum(c["n_starts"] for c in lower),
fitting.py:1415:        "n_not_better_elsewhere": sum(c["n_starts"] for c in other),
fitting.py:1542:    n_perturb: int = 0,
fitting.py:1545:    n_starts: int = 0,
fitting.py:1739:            fit_kws=fit_kws, n_perturb=n_perturb)
fitting.py:1744:    if isinstance(n_starts, bool) or not isinstance(n_starts, (int, np.integer)) or not 0 <= n_starts <= MAX_N_STARTS:
fitting.py:1745:        raise ValueError(f"n_starts must be an integer between 0 and {MAX_N_STARTS}")
fitting.py:1827:    # starts check excludes it — and with the page's n_perturb 3 they
fitting.py:1831:    if n_perturb > 0 and result.success and kws.get("method") != "basinhopping":
fitting.py:1836:        for attempt in range(n_perturb):
fitting.py:1857:                          attempt + 1, n_perturb, trial_redchi, best_redchi)
fitting.py:1868:                log.debug("  PERTURB %d/%d  failed (exception)", attempt + 1, n_perturb)
fitting.py:1878:    if n_starts:
fitting.py:1888:                starts = _scattered_starts(int(n_starts), fit_once, composite_model, all_params, result,
app.py:108:    # Bounded, type-checked n_perturb (audit F7; also covers the F9
app.py:112:        n_perturb = int(body.get("n_perturb", 5))
app.py:114:        return None, _err(f"n_perturb must be an integer between 0 and {MAX_N_PERTURB}")
app.py:115:    if n_perturb < 0 or n_perturb > MAX_N_PERTURB:
app.py:116:        return None, _err(f"n_perturb must be between 0 and {MAX_N_PERTURB}")
app.py:119:    # treatment as n_perturb; run_fit validates again for other callers.
app.py:120:    n_starts = body.get("n_starts", 0)
app.py:121:    if isinstance(n_starts, bool) or not isinstance(n_starts, int) or not 0 <= n_starts <= fitting.MAX_N_STARTS:
app.py:122:        return None, _err(f"n_starts must be an integer between 0 and {fitting.MAX_N_STARTS}")
app.py:137:        n_perturb=n_perturb,
app.py:139:        n_starts=n_starts,
            starts = {"ran": False, "reason": "fit_not_converged"}
        else:
            try:
                starts = _scattered_starts(int(n_starts), fit_once, composite_model, all_params, result,
                                           peak_specs, x, starts_rng)
            except Exception as exc:                              # the check must never cost the student the fit
                log.exception("scattered starts failed")
                starts = {"ran": False, "reason": "error", "error": f"{type(exc).__name__}: {exc}"[:200]}

    # ── "Is this component required?" (never changes `result`) ─────────────
    required = None
    if require_component is not None:
        rprefix = f"p{require_component}_"
        if not result.success:
            required = {"ran": False, "reason": "fit_not_converged"}
        else:
            try:
                # remove the component and everything linked to it, transitively
                master_of = {str(sp["id"]): sp.get("constrain_to") for sp in peak_specs}
                removed = {str(require_component)}
                grew = True
                while grew:
                    grew = False
                    for pid, master in master_of.items():
                        if master is not None and str(master) in removed and pid not in removed:
                            removed.add(pid); grew = True
                removed_prefixes = [f"p{pid}_" for pid in removed]
                without = None
                for m in composite_model.components:
                    if m.prefix in removed_prefixes:
                        continue
                    without = m if without is None else without + m
                if without is None:
                    required = {"ran": False, "reason": "nothing_left"}
                else:
                    n_free_comp = sum(1 for n, par in result.params.items()
                                      if n.startswith(rprefix) and par.vary and par.expr is None)
                    required = {"ran": True, **_component_required(
                        lambda params: fit_model(without, params), result.params, removed_prefixes, y_sub, weights,
                        float(result.chisqr), n_free_comp, result.nvarys)}
            except Exception as exc:                              # the check must never cost the student the fit
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

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python scripts/fit_termination_scope_analyze.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
== Trust-Region (least_squares, page default) (202 targets)
  returned fit (what the student gets), flagged success: n 202: drop >1e-6 8, >1e-3 5, >1% 2, >10% 0
  perturbed restarts flagged success:                 n 498: drop >1e-6 220, >1e-3 186, >1% 173, >10% 162
  scattered starts flagged success:                   n 532: drop >1e-6 78, >1e-3 52, >1% 45, >10% 29
  scattered starts flagged FAILED: 2, of which already at a minimum (refine drop < 1e-6): 0
     worst returned: b8082a8d3a48  chi2r 2.636  nfev 161  refine lowers chi2 by 5.72 %
     worst returned: 6d5a6bd78f91  chi2r 4.734  nfev 42  refine lowers chi2 by 3.81 %
     worst returned: 1f8ceab0cf5a  chi2r 19.040  nfev 2105  refine lowers chi2 by 0.39 %
     worst returned: 975e736e57d1  chi2r 8.825  nfev 34  refine lowers chi2 by 0.12 %
     worst returned: 0e8d6d5af1f4  chi2r 6.179  nfev 72  refine lowers chi2 by 0.11 %
     worst returned: a29a6e44640b  chi2r 14.456  nfev 564  refine lowers chi2 by 0.00 %
== Levenberg-Marquardt (leastsq) (202 targets)
  returned fit (what the student gets), flagged success: n 196: drop >1e-6 32, >1e-3 10, >1% 5, >10% 1
  perturbed restarts flagged success:                 n 576: drop >1e-6 522, >1e-3 367, >1% 292, >10% 198
  scattered starts flagged success:                   n 480: drop >1e-6 94, >1e-3 53, >1% 36, >10% 17
  scattered starts flagged FAILED: 36, of which already at a minimum (refine drop < 1e-6): 1
     worst returned: 7205f2094254  chi2r 21.020  nfev 7202  refine lowers chi2 by 26.40 %
     worst returned: 66f258ea2c39  chi2r 1.731  nfev 511  refine lowers chi2 by 4.45 %
     worst returned: 574ece1ffb18  chi2r 7.458  nfev 26  refine lowers chi2 by 1.87 %
     worst returned: 18a1cbf4dbac  chi2r 2.326  nfev 308  refine lowers chi2 by 1.45 %
     worst returned: 0e8d6d5af1f4  chi2r 6.258  nfev 25  refine lowers chi2 by 1.26 %
     worst returned: 3081b83af679  chi2r 4.308  nfev 3706  refine lowers chi2 by 0.56 %

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import runpy; t=runpy.run_path(\"tests/autofit/test_fit_certificate.py\"); e=t[\"eng\"]; x,y,w,m=t[\"_two_peak\"](); good=e.fit_candidate(x,y,w,m); comp=e._build_composite_model(m); p=good.lmfit_result.params.copy(); p[\"s_a_center\"].set(value=284.05); p[\"s_b_amplitude\"].set(value=50.0); p[\"s_a_fwhm\"].set(value=2.3); cold=comp.fit(y-good.background,p.copy(),x=x,weights=w,method=\"leastsq\",nan_policy=\"omit\",max_nfev=2); restart=comp.fit(y-good.background,cold.params.copy(),x=x,weights=w,method=\"least_squares\",nan_policy=\"omit\",max_nfev=2); point,cert=e._certify_minimum(comp,y-good.background,cold,x,w,2); print(\"cold\",cold.chisqr,\"restart\",restart.chisqr,\"relative_improvement\",(cold.chisqr-restart.chisqr)/cold.chisqr,\"aborted\",restart.aborted,\"certificate\",cert,\"kept_cold\",point is cold); print(\"descent_with_full_budget\",e._certify_minimum(comp,y-good.background,point,x,w,6000)[0].chisqr)'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"-s\", \"-q\", \"-p\", \"no:cacheprovider\", \"tests/autofit/test_engine_doublet.py\", \"tests/autofit/test_stage2_rereview_findings.py\", \"tests/autofit/test_progress_callback.py\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 2314ms:
/Users/skyefortier/.matplotlib is not a writable directory
cold 959072.7404457228 restart 959072.7711531647 relative_improvement -3.201784448399288e-08 aborted True certificate True kept_cold True
descent_with_full_budget 284.34815076652956

2026-09-29T19:00:07.752660Z ERROR codex_models_manager::manager: failed to refresh available models: timeout waiting for child process to exit
codex
The 20 tests in the two reviewed files pass. A separate probe found a false certificate: with a two-evaluation cap, the supplied two-peak fixture is marked converged at χ² ≈ 959,073; a normally budgeted restart from that point reaches ≈ 284.35. I’m confirming whether the capped restart worsened χ² or merely made no progress, then finishing the consumer checks.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import runpy; t=runpy.run_path(\"tests/autofit/test_fit_certificate.py\"); from autofit.methods import get_method; x,y,w=t[\"_scan\"](\"1-GTA UCl4-graphite one set of U doublets.proj.zip\",\"C1s Scan_6\"); r=get_method(\"ic_model_comparison\").run(x,y,grammar=t[\"G\"],options={\"n_refits\":4,\"rng_seed\":0,\"noise_floor\":1.0,\"candidate_filter\":[\"MG2_graphAsymGL_aliph_sat_CO_C=O\",\"MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O\",\"AG2_linked\",\"A2_linked\"],\"enable_proposal_pass\":False}); print(\"winner\",r.diagnostics.get(\"winner\"),\"success\",r.success); print([(c[\"name\"],c.get(\"filter_reason\"),c.get(\"reduced_chi_sq\")) for c in r.analysis[\"candidates\"]])'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
exec
/bin/zsh -lc "nl -ba tests/autofit/test_fit_certificate.py | sed -n '96,139p'; nl -ba autofit/engine.py | sed -n '2707,2734p'; rg -n 'time\\.|perf_counter|monotonic|deadline|timeout|budget' autofit/engine.py autofit/methods/bayesian_exchange_mc.py app.py | tail -40; git status --short" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
    96	
    97	
    98	def test_a_fit_capped_at_the_minimum_is_certified():
    99	    """The Scan_6 case in general form: an optimiser that runs out of
   100	    evaluations while sitting at the minimum reports failure; the certificate
   101	    finds no descent and certifies it."""
   102	    x, y, w, model = _two_peak()
   103	    good = eng.fit_candidate(x, y, w, model)
   104	    assert good.converged
   105	    comp = eng._build_composite_model(model)
   106	    y_sub = y - good.background
   107	    capped = comp.fit(y_sub, good.lmfit_result.params.copy(), x=x, weights=w, method="leastsq",
   108	                      nan_policy="omit", max_nfev=3)          # starts AT the minimum, capped at once
   109	    assert not capped.success
   110	    point, certified = eng._certify_minimum(comp, y_sub, capped, x, w, eng.FIT_CANDIDATE_MAX_NFEV)
   111	    assert certified
   112	    assert point.chisqr == pytest.approx(good.weighted_chi_sq, rel=1e-6)
   113	
   114	
   115	def test_out_of_restarts_is_not_converged(monkeypatch):
   116	    """A start far from the minimum needs more than one restart to certify
   117	    (the first descends a long way); with a single restart allowed it is
   118	    'not converged' — whatever the optimiser says."""
   119	    x, y, w, model = _two_peak()
   120	    comp = eng._build_composite_model(model)
   121	    good = eng.fit_candidate(x, y, w, model)
   122	    y_sub = y - good.background
   123	    far = good.lmfit_result.params.copy()
   124	    far["s_a_center"].set(value=284.05); far["s_b_amplitude"].set(value=50.0); far["s_a_fwhm"].set(value=2.3)
   125	    short = comp.fit(y_sub, far, x=x, weights=w, method="leastsq", nan_policy="omit", max_nfev=2)
   126	    monkeypatch.setattr(eng, "CERTIFY_MAX_RESTARTS", 1)
   127	    _, certified = eng._certify_minimum(comp, y_sub, short, x, w, eng.FIT_CANDIDATE_MAX_NFEV)
   128	    assert not certified
   129	    monkeypatch.setattr(eng, "CERTIFY_MAX_RESTARTS", 5)
   130	    point, certified = eng._certify_minimum(comp, y_sub, short, x, w, eng.FIT_CANDIDATE_MAX_NFEV)
   131	    assert certified and point.chisqr == pytest.approx(good.weighted_chi_sq, rel=1e-6)
   132	
   133	
   134	def test_the_warm_restart_is_gone():
   135	    src = inspect.getsource(eng.fit_candidate)
   136	    assert "retry" not in src and "WARM_RESTART" not in src
   137	    assert "converged=bool(certified)" in src
  2707	        screen_rows: list[dict] = []
  2708	        screened: list[tuple[CandidateModel, FitOutcome, float]] = []
  2709	        # Unit A1: EVERY candidate is screened (no wall-clock screen budget —
  2710	        # which candidates reached the deep phase used to depend on load)
  2711	        for idx, model in enumerate(candidates, 1):
  2712	            log.info("[screen %2d/%d] %s", idx, n_cand, model.name)
  2713	            _report_progress(progress_cb, "screening", idx, n_cand, model.name)
  2714	            outcome = fit_candidate(x, y, weights, model,
  2715	                                    max_nfev=SCREEN_MAX_NFEV,
  2716	                                    fit_full_window=fit_full_window,
  2717	                                    endpoint_avg=endpoint_avg)
  2718	            if outcome.converged:
  2719	                bic = compute_bic(outcome)
  2720	                screened.append((model, outcome, bic))
  2721	                screen_rows.append({"name": model.name, "converged": True,
  2722	                                    "bic": float(bic), "selected": False})
  2723	            else:
  2724	                non_converged.append((model, outcome))
  2725	                screen_rows.append({"name": model.name, "converged": False,
  2726	                                    "bic": None, "selected": False})
  2727	        screened.sort(key=lambda t: t[2])
  2728	        selected_models = screened[:SCREEN_TOP_K]
  2729	        selected_names = {m.name for m, _, _ in selected_models}
  2730	        for row in screen_rows:
  2731	            row["selected"] = row["name"] in selected_names
  2732	        screen_record = screen_rows
  2733	        screen_fit = {m.name: o for m, o, _ in selected_models}
  2734	        candidates = [m for m, _, _ in selected_models]
autofit/methods/bayesian_exchange_mc.py:424:        # is UNRESOLVED at this sweep budget — surfaced, never silent.
app.py:237:    cutoff = time.time() - SESSION_TTL_DAYS * 86400
app.py:538:    cutoff = time.time() - _ANALYZE_JOB_TTL_SEC
app.py:618:    data["heartbeat_age_sec"] = round(time.time() - hb, 1) if isinstance(hb, (int, float)) else None
app.py:625:    cutoff = time.time() - _ANALYZE_JOB_TTL_SEC
app.py:648:    started = time.time()
app.py:661:            return time.time() - polled_path.stat().st_mtime > FIT_JOB_ABANDON_SEC
app.py:670:                rec["heartbeat"] = time.time()
app.py:671:                rec["elapsed_sec"] = round(time.time() - started, 1)
app.py:683:                got = _FIT_JOB_RUN_SLOTS.acquire(timeout=0.5)
app.py:688:                        rec["heartbeat"] = time.time()
app.py:699:            rec["elapsed_sec"] = round(time.time() - started, 1)
app.py:700:            rec["heartbeat"] = time.time()
app.py:914:        # Reject non-.vgd before spending the upload budget / writing to disk
app.py:1185:        start_time = time.time()
app.py:1200:                "elapsed_sec": round(time.time() - start_time, 1),
app.py:1210:                    "elapsed_sec": round(time.time() - start_time, 1),
app.py:1217:                    "elapsed_sec": round(time.time() - start_time, 1),
app.py:1228:                    "elapsed_sec": round(time.time() - start_time, 1),
autofit/engine.py:129:# boundary cleanliness; same per-candidate wall budget).  Measured
autofit/engine.py:133:# residual.  fitalg's Iteration B was already capped/timeout-guarded; this
autofit/engine.py:142:# Unit A1 (2026-09-29): NO wall-clock budget anywhere in the sweep. The
autofit/engine.py:143:# per-candidate 25 s, the 240 s sweep, the 60 s / 35 s proposal budgets, the
autofit/engine.py:144:# 15 s minimum-fit budget and the screen's share of the sweep all made Find
autofit/engine.py:216:# grammar at 25 s/candidate stability budgets + a 30-60 s proposal pass can
autofit/engine.py:217:# never finish inside the then 240 s sweep budget (removed in unit A1; it sat
autofit/engine.py:218:# below the gunicorn --timeout 300) — the real spectra truncated at 8/29 with the
autofit/engine.py:1146:    # budget); the denominator of persistence / orphan_rate / convergence_rate.
autofit/engine.py:1173:    deadline. The 25 s per-candidate budget this replaced made persistence
autofit/engine.py:1607:    # Never set since unit A1 (the sweep budget it reported is gone: every
autofit/engine.py:2158:    # Unit A1 (2026-09-29): no wall-clock budget — an attempt either runs its
autofit/engine.py:2677:                    # phase truncates under its wall budget on rich scans
autofit/engine.py:2679:                    # 21/30) — a budget truncation must never be able to
autofit/engine.py:2702:    #    deep-evaluation budget — every existing gate/battery path is ≤
autofit/engine.py:2709:        # Unit A1: EVERY candidate is screened (no wall-clock screen budget —
autofit/engine.py:2741:        # Unit A1: every selected candidate is evaluated — no sweep budget
autofit/engine.py:2793:            # per-candidate wall budget.  Gates are unchanged per round.
autofit/engine.py:2796:            timed_out = False                 # unit A1: never set (no pass budget)
autofit/engine.py:2797:            pass_start = time.perf_counter()  # telemetry only (wall_time_sec)
autofit/engine.py:2855:                wall_time_sec=time.perf_counter() - pass_start, timed_out=timed_out,
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-hXSqynbg' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-q1YQulNU' (errno=Operation not permitted)
?? docs/autofit/codex/a1_determinism_verdict_runA.md
?? docs/autofit/codex/a1_determinism_verdict_runB.md
?? "docs/autofit/test_data/7 - GTA-2-66 U-naph and COT.DATA"
?? "docs/autofit/test_data/8 GTA-2-46ii U-naph and XeF2, graphite 40%, powder, Cu, 0.4eV, 400 um.DATA"
?? docs/autofit/test_data/Ugly_Fe_2p.spec.json
?? docs/autofit/test_data/Ugly_Fe_2p_2.spec.json

 succeeded in 62748ms:
..................
18 passed in 62.27s (0:01:02)

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir=\"/tmp\"; from types import SimpleNamespace as S; from autofit.engine import _certify_minimum; import numpy as np
class C:
 def __init__(self, values): self.values=iter(values); self.calls=[]
 def fit(self,*args,**kw):
  self.calls.append(kw); v=next(self.values)
  if isinstance(v,Exception): raise v
  return S(chisqr=v,params={\"at\":v})
for name,chi,values in [(\"zero\",0,[0]),(\"higher\",10,[12]),(\"nan\",10,[np.nan]),(\"raise\",10,[ValueError(\"restart\")]),(\"improve_then_nan\",10,[5,np.nan]),(\"tiny_gain\",10,[10*(1-1e-9)])]:
 c=C(values); p,ok=_certify_minimum(c,None,S(chisqr=chi,params={\"at\":chi}),None,None,123); print(name,p.chisqr,ok,len(c.calls),all(k[\"method\"]==\"least_squares\" and k[\"max_nfev\"]==123 for k in c.calls))
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 1725ms:
/Users/skyefortier/.matplotlib is not a writable directory
zero 0 True 1 True
higher 10 True 1 True
nan 10 False 1 True
raise 10 False 1 True
improve_then_nan 5 False 2 True
tiny_gain 9.999999990000001 True 1 True

codex
Confirmed: the capped restart increases χ², and the negative relative “improvement” passes the certificate immediately. The best point is preserved, but its convergence label is false. Another 18 consumer tests pass, including linked doublets, stability, and progress callbacks. The scope-report totals also reproduce. I’m waiting on the targeted Scan_6 run before issuing the verdict.

exec
/bin/zsh -lc "sed -n '136,155p' autofit/engine.py; sed -n '330,352p' tests/autofit/test_preseed_dominants.py; sed -n '110,165p' autofit/methods/ic_model_comparison.py; sed -n '272,300p' autofit/methods/ic_model_comparison.py; git branch --show-current" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
PROPOSAL_MAX_ATTEMPTS_PER_CANDIDATE = 3

# See fit_candidate() docstring: deterministic per-call ceiling on lmfit's
# own effort, replacing its effectively-unbounded default.
FIT_CANDIDATE_MAX_NFEV = 18000

# Unit A1 (2026-09-29): NO wall-clock budget anywhere in the sweep. The
# per-candidate 25 s, the 240 s sweep, the 60 s / 35 s proposal budgets, the
# 15 s minimum-fit budget and the screen's share of the sweep all made Find
# Peaks' ANSWER depend on server load (1-GTA C1s Scan_6: MG2 won or lost on
# whether its fourth refit started before 25 s). Work is bounded by counts:
# every candidate is screened once, SCREEN_TOP_K are deep-evaluated with
# n_refits refits each, a proposal pass makes at most
# PROPOSAL_MAX_PER_CANDIDATE × PROPOSAL_MAX_ATTEMPTS_PER_CANDIDATE attempts,
# every fit is capped at FIT_CANDIDATE_MAX_NFEV / SCREEN_MAX_NFEV evaluations
# and certified with at most CERTIFY_MAX_RESTARTS restarts. The page runs
# Find Peaks as a polled job (/api/analyze/start), so no request waits on it.
PROPOSAL_ENDPOINT_WARNING_BE = 1.0
PROPOSAL_COINCIDENCE_BE = 0.5

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
        diagnostic_windows=dict(case.grammar.diagnostic_windows))
    assert outcome == "stability_rejected"
    assert "post-stability" in (pr.rejection_reason or "")
    assert any("center@min" in h for h in pr.boundary_hits)

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
            # multi-start fits reproduced the reported minimum's χ² basin
            "best_minimum_basin_support": int(r.stability.best_basin_support),
        })

    import copy
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-8Zd2XfnB' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-BYNG2Wd2' (errno=Operation not permitted)
fix-find-peaks-determinism

 succeeded in 122728ms:
/Users/skyefortier/.matplotlib is not a writable directory
winner MG2_graphAsymGL_aliph_sat_CO_C=O+preseed success True
[('D0_detected', "plausibility: PlausibilityFlags(boundary_hits=['detected_peak_1:fwhm@min', 'detected_peak_2:center@min', 'detected_peak_2:fwhm@max'], unphysical_widths=['detected_peak_2:fwhm=6.00eV≥0.70×ceiling (6.00eV) — ~1.75× its detected width; likely absorbing a neighbor'], orphan_peaks=False)", 53.58250151123374), ('A2_linked+preseed', "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@min', 'preseed_curvature_0:center@max'], unphysical_widths=[], orphan_peaks=False)", 7.308438917049047), ('AG2_linked+preseed', "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@min'], unphysical_widths=[], orphan_peaks=False)", 3.6901828520316604), ('MG2_graphAsymGL_aliph_sat_CO_C=O+preseed', "plausibility: PlausibilityFlags(boundary_hits=['contamination_C=O:fwhm@max', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@max'], unphysical_widths=['main_aliphatic:fwhm=2.00eV≥2.0eV ordinary cap (no known-broad justification)', 'contamination_C=O:fwhm=2.00eV≥2.0eV ordinary cap (no known-broad justification)'], orphan_peaks=False)", 2.0340513790098473), ('MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O+preseed', "plausibility: PlausibilityFlags(boundary_hits=['contamination_C=O:center@min', 'contamination_OC=O:center@min', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@max'], unphysical_widths=['main_aliphatic:fwhm=2.00eV≥2.0eV ordinary cap (no known-broad justification)'], orphan_peaks=False)", 2.045644926700981)]

exec
/bin/zsh -lc "ps -eo pid,etime,pcpu,command | rg 'python -c|pytest' | head -10" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
zsh:1: operation not permitted: ps

codex
1. **MAJOR — An evaluation-aborted restart can falsely certify a non-minimum.** [autofit/engine.py:850](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/autofit/engine.py:850)

   A higher restart χ² produces a negative “improvement,” which immediately satisfies `< CERTIFY_FTOL`. lmfit catches evaluation exhaustion internally, so this bypasses the exception handler.

   **Reproduced with real fits:** use `_two_peak()` and the displaced parameters from `test_out_of_restarts_is_not_converged`, then call `fit_candidate(..., max_nfev=2)`:
   - Initial χ²: **959072.74045**
   - Aborted restart χ²: **959072.77115**
   - Relative improvement: **−3.20e−8**
   - Returned `converged`: **True**
   - A normally budgeted restart from that supposedly certified point reaches **284.34815**.

   Keeping the lowest-χ² point works; certifying it does not. This false label feeds screening and stability counts. Prevent an aborted, worsening restart from supplying the certificate, without restoring reliance on `success`. Add a regression that caps the **certificate restart**; current tests cap the initial fit but give certification a full budget. This failure was reproduced at the explicit low cap, **not** at production caps of 6000/18000.

2. **MINOR — The clock-independence test never exercises screening.** [tests/autofit/test_preseed_dominants.py:430](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/tests/autofit/test_preseed_dominants.py:430)

   Its grammar contains one candidate and disables preseeding, so `n_cand > SCREEN_TOP_K` is false. **Concrete missed regression:** restoring the old screen deadline would leave this test passing while a full-grammar request again selects different candidates under load. Exercise more than `SCREEN_TOP_K` candidates under the jumping clock and assert complete screening and the requested refit counts.

The remaining inspection was favorable: no clock-based scientific selection branch remains in the engine, Bayesian method, or analyze worker. The certificate reads SciPy’s relative `ftol`, preserves the best point, propagates evaluation caps, and rejects raising/non-finite restarts. Zero χ² is handled. Linked-parameter tests pass; non-finite uncertainty values are sanitized to `null`.

**Plan §3:** the absent-slot explanation is consistent with the code: certifying previously discarded refits changes persistence and removes the BIC* credit. The two screening regressions are real losses from the existing single-start shortlist; certification does not guarantee discovery of the best basin. They warrant explicit acceptance, but do not independently violate A1’s stated determinism contract. The disclosed arithmetic jitter is not evidence of a remaining clock cutoff.

**Validation:** 38 targeted tests passed; the scope-report totals reproduced. The targeted Scan_6 gate returned **MG2 + preseed**, χ²ᵣ **2.03405**. I did not independently repeat the seven-scan or heavy-load measurements. Workspace unchanged.

**VERDICT: NO-GO**
tokens used
92,448
1. **MAJOR — An evaluation-aborted restart can falsely certify a non-minimum.** [autofit/engine.py:850](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/autofit/engine.py:850)

   A higher restart χ² produces a negative “improvement,” which immediately satisfies `< CERTIFY_FTOL`. lmfit catches evaluation exhaustion internally, so this bypasses the exception handler.

   **Reproduced with real fits:** use `_two_peak()` and the displaced parameters from `test_out_of_restarts_is_not_converged`, then call `fit_candidate(..., max_nfev=2)`:
   - Initial χ²: **959072.74045**
   - Aborted restart χ²: **959072.77115**
   - Relative improvement: **−3.20e−8**
   - Returned `converged`: **True**
   - A normally budgeted restart from that supposedly certified point reaches **284.34815**.

   Keeping the lowest-χ² point works; certifying it does not. This false label feeds screening and stability counts. Prevent an aborted, worsening restart from supplying the certificate, without restoring reliance on `success`. Add a regression that caps the **certificate restart**; current tests cap the initial fit but give certification a full budget. This failure was reproduced at the explicit low cap, **not** at production caps of 6000/18000.

2. **MINOR — The clock-independence test never exercises screening.** [tests/autofit/test_preseed_dominants.py:430](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/tests/autofit/test_preseed_dominants.py:430)

   Its grammar contains one candidate and disables preseeding, so `n_cand > SCREEN_TOP_K` is false. **Concrete missed regression:** restoring the old screen deadline would leave this test passing while a full-grammar request again selects different candidates under load. Exercise more than `SCREEN_TOP_K` candidates under the jumping clock and assert complete screening and the requested refit counts.

The remaining inspection was favorable: no clock-based scientific selection branch remains in the engine, Bayesian method, or analyze worker. The certificate reads SciPy’s relative `ftol`, preserves the best point, propagates evaluation caps, and rejects raising/non-finite restarts. Zero χ² is handled. Linked-parameter tests pass; non-finite uncertainty values are sanitized to `null`.

**Plan §3:** the absent-slot explanation is consistent with the code: certifying previously discarded refits changes persistence and removes the BIC* credit. The two screening regressions are real losses from the existing single-start shortlist; certification does not guarantee discovery of the best basin. They warrant explicit acceptance, but do not independently violate A1’s stated determinism contract. The disclosed arithmetic jitter is not evidence of a remaining clock cutoff.

**Validation:** 38 targeted tests passed; the scope-report totals reproduced. The targeted Scan_6 gate returned **MG2 + preseed**, χ²ᵣ **2.03405**. I did not independently repeat the seven-scan or heavy-load measurements. Workspace unchanged.

**VERDICT: NO-GO**
