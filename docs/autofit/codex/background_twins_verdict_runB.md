OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0e227-7a2c-7bd2-a8e9-d77fd62a7629
--------
user
Review unit 4 (the background twins): branch fix-background-twins, stacked on fix-noise-floor-scale-free (F3). Review git diff 895f323..HEAD (895f323 is the F3 commit unit 4 was cut from): templates/index.html (shirleyBackground, smartBackground, one line of computeBackgroundCore), tests/js/background_parity.test.js, tests/js/background_parity_backend.py, CLAUDE.md, docs/superpowers/plans/2026-09-27-background-twins.md. Task 4's investigation: docs/superpowers/plans/2026-09-02-task4-background-twin-parity.md. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

OWNER'S BRIEF (verbatim): "the background parity test plus the two JS fixes (JS shirleyBackground missing the net-signal-at-zero clamp; JS smart clamping against the averaged array instead of raw). shirley_linear is de-listed — pin its divergence as a known gap, don't fix it."

PLAN SECTIONS 1-3 (sites, measurement, tests), verbatim:

## 1. Sites

| # | site | before | after |
|---|---|---|---|
| S4 | `shirleyBackground` (also smart's base) | integrates the raw net signal `intensity − bg`: channels below the background contribute NEGATIVE loss → a different fixed point from fitting.py | `max(intensity − bg, 0)` in both integrals, as `fitting.shirley_background` (Proctor–Sherwood); the iteration scheme is otherwise untouched (the JS was already order-invariant: descending input gives the same curve as fitting.py's ascending copy) |
| S5 | `smartBackground(be, intensity, maxIter, rawIntensity)` + `computeBackgroundCore` | clamps `min(shirley, averaged data)` | clamps against the RAW slice (`rawIntensity`, default `intensity`), as `fitting.smart_background`: averaging only ever moves the background, never the reported net counts |
| — | `shirley_linear` | order-sensitive (27–33 % of the span on descending grids, Task 4 cause 3) | UNCHANGED, de-listed (disabled, hidden); the divergence is pinned as a known gap |
| — | not changed | the UI's Shirley iteration count (default 5) vs the server's convergence (tolerance 1e-6, ≤ 200) — Part 5 of the sealed-fit-record memo | |

Blast radius (Task 4): the JS backgrounds are what the page DRAWS, what it
freezes into `fitResult.bgIntensity` / `bgSubtracted` at fit time and saves,
what the local engine (Batch Fit, fallback) fits against, and what stack
Path B reconstructs. Backend fits, χ², refined parameters and Quantify areas
never touch them.

## 2. Measurement (the parity cases: synthetic C 1s, synthetic U 4f doublet, the committed real U 4f Scan_0; each ascending and descending)

Max |JS − server| as % of the intensity span:

| method | endpoint avg | iterations | before | after |
|---|---|---|---|---|
| shirley | 1 | 200 (converged) | 0.047 % | 0.0000 % |
| shirley | 10 | 200 | 0.078 % | 0.0000 % |
| smart | 1 | 200 | 0.047 % | 0.0000 % |
| smart | 10 | 200 | **1.19 %** | 0.0000 % |
| shirley / smart | 1 / 10 | 5 (the UI default) | 0.047–1.19 % | 0.016–0.019 % (unconverged iteration: Part 5, not this unit) |

## 3. Tests

`tests/js/background_parity.test.js` + `tests/js/background_parity_backend.py`
(fitting.py's own functions, never a reimplementation): shirley, smart,
smart_exp, tougaard, linear × endpoint average 1 and 10, the page's
`computeBackgroundCore` at a converged iteration count, every case within
1e-6 of the span (Task 4's smallest gap was 1.5e-4). On the unfixed page the
four shirley / smart tests FAIL and the rest pass. `shirley_linear`: agrees on
ascending grids, still diverges on descending ones (pinned; the test fails if
the gap closes, so the pin and CLAUDE.md get updated), and stays de-listed.


TRY TO BREAK
a. The clamp: exactly fitting.shirley_background's fixed point (the Python works on an ascending copy, starts from a linear guess and stops at tol; the JS starts from zeros and runs maxIter; the total <= 0 branch — Python breaks keeping the previous B, the JS falls back to an index-linear fraction); non-uniform grids; flat or all-below-background data; n = 2.
b. smart: the raw clamp with averaging, every caller of smartBackground (any that passes 3 arguments and now clamps against the averaged copy?); smart_exp and shirley_linear untouched.
c. Blast radius: every consumer of the JS background (display, fitResult.bgIntensity frozen at fit time, saves, the local engine, stack Path B, Batch Fit, Find Peaks' preview, the ROI hint / anything else) — does anything pin the OLD curve (tests, fixtures, saved-file readers comparing)?
d. The parity test: non-vacuous (fails on the unfixed page), tolerance justified, the bridge calls fitting.py's own functions exactly as run_fit does for the anchor window, the committed real case actually loaded; the shirley_linear pin (would it catch the gap closing? the de-listing assertion).
e. Docs vs code vs measurement.

Finish with VERDICT: GO or VERDICT: NO-GO.
codex
I’ll review the diff and backend call path, then test edge cases and the parity test’s sensitivity to the two fixes. I’ll keep the review read-only and finish with ranked findings and a verdict.
exec
/bin/zsh -lc "pwd; git status --short; git diff --stat 895f323..HEAD; rg --files -g 'AGENTS.md' -g 'CLAUDE.md' -g '*background*parity*' -g '*background-twins*'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-qWURBGxF' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-R94LBUoQ' (errno=Operation not permitted)
?? docs/autofit/codex/background_twins_verdict_runA.md
?? docs/autofit/codex/background_twins_verdict_runB.md
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-6zXeJa6K' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-gvOQx0se' (errno=Operation not permitted)
 CLAUDE.md                                          | 12 +++
 .../codex/background_twins_review_prompt.txt       | 53 +++++++++++++
 .../plans/2026-09-27-background-twins.md           | 55 +++++++++++++
 templates/index.html                               | 22 ++++--
 tests/js/background_parity.test.js                 | 90 ++++++++++++++++++++++
 tests/js/background_parity_backend.py              | 84 ++++++++++++++++++++
 6 files changed, 311 insertions(+), 5 deletions(-)
CLAUDE.md
docs/superpowers/plans/2026-09-02-task4-background-twin-parity.md
docs/superpowers/plans/2026-09-27-background-twins.md
tests/js/background_parity_backend.py
tests/js/background_parity.test.js

exec
/bin/zsh -lc "cat CLAUDE.md; cat docs/superpowers/plans/2026-09-02-task4-background-twin-parity.md; rg --files -g 'AGENTS.md' -g 'package.json' -g '*fitting*' -g '*harness*'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
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
timer throttling of hidden browser tabs). The synchronous `/api/fit` stays
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
fits against) equal fitting.py's to 1e-6 of the intensity span at a converged
iteration count for shirley, smart, smart_exp, tougaard and linear, with
endpoint averaging 1 and 10 (`tests/js/background_parity.test.js`, unit 4
2026-09-27: the JS Shirley now clamps the net signal at zero and smart clamps
against the raw data — Task 4's S4 / S5; smart at averaging 10 was 1.2 % of
the span away). Known gaps, pinned: `shirley_linear` (de-listed) diverges on
descending grids; the UI's Shirley iteration count (default 5) leaves
0.016–0.019 % of the span of unfinished iteration (Part 5 of the
sealed-fit-record memo).

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
# Task 4 — Background JS/Python twin parity (investigation only; NO fixes made)

Harness: the shipped JS functions were regex-extracted from
`templates/index.html` (main) and run in node against `fitting.py`'s twins on
IDENTICAL input arrays — 3 spectra (synthetic narrow C1s 101 pts, synthetic
wide U4f doublet 351 pts, the real U4f Scan_0 from the committed 1-GTA proj,
350 pts) × {ascending, descending} × n_avg {1, 10} × JS iteration {5 = UI
default, 50, 200}; 171 cases + non-uniform-grid and manual-anchor cases.
Calling conventions mirror `computeBackgroundCore` exactly. Scripts + full
row dump: scratchpad/task4/ (parity.py, js_bg_runner.mjs, parity_rows.json).
This isolates ALGORITHM divergence; the request-path window off-by-one is a
separate finding (Task 1 report) and applies ON TOP of everything below.

## Parity table (worst case per method × condition class; % of intensity span)

| method | condition | max divergence | verdict |
|---|---|---|---|
| **shirley_linear** | **descending grid (= all real data)**, any n_avg, any iter | **26.6–33.2% of span** (5077–6396 counts) | **DIVERGED — severe** |
| shirley_linear | ascending grid, iter ≥ 50 | 0.000 (exact) | agrees |
| **smart** | **n_avg = 10**, any direction, any iter | **0.72–1.04% of span** (46–171 counts), localized at the averaged edges | **DIVERGED — moderate** |
| smart | n_avg = 1 | ≤ 0.24% span (≤ 56 counts) — same mechanism as shirley below | diverged (small) |
| **shirley** | any direction, converged (iter ≥ 50) | 0.015–0.24% span (1–56 counts), mid-window | **DIVERGED — small but real** |
| smart_exp | all conditions | ≤ 0.008% span (≤ 1.8 counts) | agrees (within tol differences) |
| linear | uniform grids | 0 (exact) | agrees |
| linear | non-uniform grid | 0.034% span | latent divergence (index- vs BE-interpolation) |
| tougaard | all conditions | 0 (exact) | agrees — pinned twin confirmed locked in |
| manual (fit path) | uniform + non-uniform | 0 (exact vs np.interp) | agrees |

## Root causes — each PROVEN by exact reconstruction, not inferred

1. **shirley (and smart's base): the JS iteration does not clamp net signal
   at zero.** `shirleyBackground` integrates `(intensity − bg)` raw
   (index.html:4038); Python uses `max(y − B, 0)` (fitting.py:369). Noise
   channels below the background contribute NEGATIVE loss weight in JS. This
   is a different fixed point, not an iteration-count issue (identical at 50
   vs 200 iterations). Proof: re-implementing the JS loop in numpy and adding
   ONLY the clamp reproduces fitting.py to 0.000000 counts; without the clamp
   it reproduces the shipped JS to 0.000000 (verify_shirley_clamp.py).
   Python's clamped form is the Proctor–Sherwood-faithful one.

2. **smart at n_avg > 1: the two sides clamp against different data.**
   `computeBackgroundCore` hands the ENDPOINT-AVERAGED array to
   `smartBackground`, which clamps `min(shirley, averagedData)`; Python
   `smart_background` deliberately clamps against the RAW data (its
   docstring calls this out as the F3 design: "averaging only ever moves the
   background — never the reported net counts"). At the averaged edge caps
   (n/4-capped n_avg points) the clamp targets differ by the local
   noise-vs-mean gap. Proof: the clamp-target difference alone reproduces the
   full 161.33-count real-U4f divergence to 1e-12 (verify_smart_clamp.py).

3. **shirley_linear: the JS is order-SENSITIVE; Python is order-invariant.**
   The JS accumulates its Shirley-like correction integral in ARRAY order
   (`sumRight` toward the array end, index.html:4258-4262) and pins the
   step-height at whichever end of the ARRAY is index 0; Python normalizes to
   an ascending copy first, always placing the correction the same way in BE
   space. On ascending input they agree exactly; on DESCENDING input — which
   is every real acquisition — the correction lands on the OPPOSITE side of
   the window, and only the final min(data) clamp keeps the JS curve visually
   plausible ("under the data"), masking a 27–33%-of-span disagreement with
   the background the backend actually fit against.

4. **linear on non-uniform grids:** JS interpolates by index `i/(n−1)`
   (index.html:4135), Python by BE. Identical on uniform instrument grids;
   0.03% span on an alternating-step grid. Latent, low priority.

## Manual anchor background (item 2 — never-audited path)

- It DOES have a backend counterpart in the fit path: `runFit` sends
  `manual_bg = anchors as [x, y]` (index.html:6815) and `run_fit`
  interpolates them with `np.interp` over the full ROI (fitting.py:1038-1046).
  JS `manualAnchorBackground` (index.html:12477) is BE-based piecewise-linear
  with endpoint clamping — measured EXACT vs the backend interpolation on
  uniform and non-uniform grids. No structural mismatch in the fit path.
- Two real quirks: (a) `< 2 anchors` fallback differs — JS falls back to
  `linearBackground` (index-based), backend to `linear_background` (BE-based):
  same uniform-grid result, latent non-uniform divergence; (b)
  `/api/background` (`compute_background_only`) treats 'manual' as ZEROS —
  only `/api/fit` implements it. Nothing currently calls /api/background with
  'manual', so this is a landmine, not a live bug.
- The charge-correction frame problem for anchors is Task 6's report.

## bgSubtracted / display path (item 3)

Confirmed at code level (and numerically in the Task 1 reproduction): after a
backend fit, the drawn background curve (`plotBG`) and the Bkgrd-Sub view
baseline are the frozen **JS** background (`state.fitResult.bgIntensity` /
`.bgSubtracted`, index.html:7955-7963), while χ²/fittedY were computed
against the **Python** background. The residuals panel is internally
consistent (it diffs raw data against backend `fitted_y`), but the displayed
background ≠ the background actually subtracted in the fit, by the amounts in
the table above. For `shirley_linear` on real (descending) data that gap is
~30% of the span — very plausibly the kernel of the "backgrounds don't quite
work the way they should" feeling.

## Which side is likely canonical (NOT decided — for the morning)

- shirley / smart / smart_exp / tougaard: **Python** — Proctor-Sherwood-
  verified this session, order-invariant, and it is what the fit minimizes
  against. The JS signal-clamp and clamp-target gaps look like straight bugs
  to fix toward Python (small blast radius: display + saved bgIntensity).
- shirley_linear: Python is order-invariant and fit-side, so parity argues
  for porting Python's behavior to JS. BUT note both sides place a nonzero
  step at a window END (it is a heuristic hybrid, not literature Shirley), so
  if this method matters scientifically it deserves its own review rather
  than blind twin-alignment. Users on descending data have been LOOKING at
  the JS curve while FITTING against the Python one for as long as this
  method has existed.
- Blast radius of any JS-side alignment: display curves, saved
  bgIntensity/bgSubtracted arrays in .proj/.spec.json, the local-LM fallback
  fit (which fits against the JS bg), and every stack-view Path-B
  reconstruction. Backend fits, χ², refined params, and Quantify areas are
  NOT affected (they never touch the JS backgrounds).
xps-fitting-tool.html
fitting.py

exec
/bin/zsh -lc 'git diff 895f323..HEAD -- templates/index.html tests/js/background_parity.test.js tests/js/background_parity_backend.py CLAUDE.md docs/superpowers/plans/2026-09-27-background-twins.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-z4YataPO' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-H0tq460o' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index 7f03bea..6cd3464 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -743,6 +743,18 @@ starting model as "Fit complete"; see
 | `tougaard` | Single-pass universal cross-section K(T) = B·T/(C+T²)², B = 2866 eV², C = 1643 eV² (Tougaard, *Surf. Interface Anal.* **1988**, 11, 453; kernel max at √(C/3) ≈ 23.4 eV). Order-robust (either BE direction); amplitude anchored to the data at the high-BE edge. JS twin `tougaardBackground` must stay in numerical agreement (pinned by `tests/js/tougaard_twin.test.js`). |
 | `manual` (frontend only) | User-placed anchor points; `manualAnchorBackground` in JS. |
 
+The page's background twins (`computeBackgroundCore`: what it draws, freezes
+into `fitResult.bgIntensity` at fit time, saves, and what the local engine
+fits against) equal fitting.py's to 1e-6 of the intensity span at a converged
+iteration count for shirley, smart, smart_exp, tougaard and linear, with
+endpoint averaging 1 and 10 (`tests/js/background_parity.test.js`, unit 4
+2026-09-27: the JS Shirley now clamps the net signal at zero and smart clamps
+against the raw data — Task 4's S4 / S5; smart at averaging 10 was 1.2 % of
+the span away). Known gaps, pinned: `shirley_linear` (de-listed) diverges on
+descending grids; the UI's Shirley iteration count (default 5) leaves
+0.016–0.019 % of the span of unfinished iteration (Part 5 of the
+sealed-fit-record memo).
+
 Use Shirley for standard core-level regions. Linear only when the
 spectral window is very narrow and featureless.
 
diff --git a/docs/superpowers/plans/2026-09-27-background-twins.md b/docs/superpowers/plans/2026-09-27-background-twins.md
new file mode 100644
index 0000000..14ed507
--- /dev/null
+++ b/docs/superpowers/plans/2026-09-27-background-twins.md
@@ -0,0 +1,55 @@
+# Unit 4 — the background twins: two JS fixes and a pinned parity test (2026-09-27)
+
+Branch `fix-background-twins`, stacked on `fix-noise-floor-scale-free` (F3):
+deploy F2 → unit 2 → F3 → unit 4. It touches only `shirleyBackground`,
+`smartBackground` and one line of `computeBackgroundCore`; it can be rebased
+onto main alone.
+
+Owner's brief (2026-09-27): "the background parity test plus the two JS
+fixes (JS shirleyBackground missing the net-signal-at-zero clamp; JS smart
+clamping against the averaged array instead of raw). shirley_linear is
+de-listed — pin its divergence as a known gap, don't fix it." Source: Task 4
+(`docs/superpowers/plans/2026-09-02-task4-background-twin-parity.md`), whose
+causes S4 and S5 were proven by exact reconstruction.
+
+## 1. Sites
+
+| # | site | before | after |
+|---|---|---|---|
+| S4 | `shirleyBackground` (also smart's base) | integrates the raw net signal `intensity − bg`: channels below the background contribute NEGATIVE loss → a different fixed point from fitting.py | `max(intensity − bg, 0)` in both integrals, as `fitting.shirley_background` (Proctor–Sherwood); the iteration scheme is otherwise untouched (the JS was already order-invariant: descending input gives the same curve as fitting.py's ascending copy) |
+| S5 | `smartBackground(be, intensity, maxIter, rawIntensity)` + `computeBackgroundCore` | clamps `min(shirley, averaged data)` | clamps against the RAW slice (`rawIntensity`, default `intensity`), as `fitting.smart_background`: averaging only ever moves the background, never the reported net counts |
+| — | `shirley_linear` | order-sensitive (27–33 % of the span on descending grids, Task 4 cause 3) | UNCHANGED, de-listed (disabled, hidden); the divergence is pinned as a known gap |
+| — | not changed | the UI's Shirley iteration count (default 5) vs the server's convergence (tolerance 1e-6, ≤ 200) — Part 5 of the sealed-fit-record memo | |
+
+Blast radius (Task 4): the JS backgrounds are what the page DRAWS, what it
+freezes into `fitResult.bgIntensity` / `bgSubtracted` at fit time and saves,
+what the local engine (Batch Fit, fallback) fits against, and what stack
+Path B reconstructs. Backend fits, χ², refined parameters and Quantify areas
+never touch them.
+
+## 2. Measurement (the parity cases: synthetic C 1s, synthetic U 4f doublet, the committed real U 4f Scan_0; each ascending and descending)
+
+Max |JS − server| as % of the intensity span:
+
+| method | endpoint avg | iterations | before | after |
+|---|---|---|---|---|
+| shirley | 1 | 200 (converged) | 0.047 % | 0.0000 % |
+| shirley | 10 | 200 | 0.078 % | 0.0000 % |
+| smart | 1 | 200 | 0.047 % | 0.0000 % |
+| smart | 10 | 200 | **1.19 %** | 0.0000 % |
+| shirley / smart | 1 / 10 | 5 (the UI default) | 0.047–1.19 % | 0.016–0.019 % (unconverged iteration: Part 5, not this unit) |
+
+## 3. Tests
+
+`tests/js/background_parity.test.js` + `tests/js/background_parity_backend.py`
+(fitting.py's own functions, never a reimplementation): shirley, smart,
+smart_exp, tougaard, linear × endpoint average 1 and 10, the page's
+`computeBackgroundCore` at a converged iteration count, every case within
+1e-6 of the span (Task 4's smallest gap was 1.5e-4). On the unfixed page the
+four shirley / smart tests FAIL and the rest pass. `shirley_linear`: agrees on
+ascending grids, still diverges on descending ones (pinned; the test fails if
+the gap closes, so the pin and CLAUDE.md get updated), and stays de-listed.
+
+## 4. Codex rounds
+
+(filled in as they run)
diff --git a/templates/index.html b/templates/index.html
index 5d38496..655a50c 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -4414,13 +4414,18 @@ function shirleyBackground(be, intensity, maxIter) {
   for (let iter = 0; iter < maxIter; iter++) {
     const newBg = new Array(n).fill(0);
     for (let i = 0; i < n; i++) {
+      // Net signal clamped at zero, max(y - B, 0), as fitting.shirley_background
+      // (Proctor–Sherwood): a noise channel below the background contributes
+      // no loss, never NEGATIVE loss (Task 4 S4, unit 4 2026-09-27 — the JS
+      // integrated the raw difference and converged to a different fixed point,
+      // 0.015–0.24 % of the span away from the background the server fits).
       let sumRight = 0;
       for (let j = i; j < n - 1; j++) {
-        sumRight += ((intensity[j] - bg[j]) + (intensity[j + 1] - bg[j + 1])) / 2 * Math.abs(be[j + 1] - be[j]);
+        sumRight += (Math.max(intensity[j] - bg[j], 0) + Math.max(intensity[j + 1] - bg[j + 1], 0)) / 2 * Math.abs(be[j + 1] - be[j]);
       }
       let sumTotal = 0;
       for (let j = 0; j < n - 1; j++) {
-        sumTotal += ((intensity[j] - bg[j]) + (intensity[j + 1] - bg[j + 1])) / 2 * Math.abs(be[j + 1] - be[j]);
+        sumTotal += (Math.max(intensity[j] - bg[j], 0) + Math.max(intensity[j + 1] - bg[j + 1], 0)) / 2 * Math.abs(be[j + 1] - be[j]);
       }
       const frac = sumTotal > 0 ? sumRight / sumTotal : (n - 1 - i) / (n - 1);
       newBg[i] = I1 + (I0 - I1) * frac;
@@ -4430,12 +4435,19 @@ function shirleyBackground(be, intensity, maxIter) {
   return bg;
 }
 
-function smartBackground(be, intensity, maxIter) {
+function smartBackground(be, intensity, maxIter, rawIntensity) {
   // Smart (constrained Shirley): standard Shirley clamped to never exceed data.
+  // The Shirley runs on `intensity` (the endpoint-averaged copy); the clamp is
+  // against the RAW data (`rawIntensity`, defaulting to `intensity`), as
+  // fitting.smart_background does: averaging only ever moves the background,
+  // never the reported net counts (Task 4 S5, unit 4 2026-09-27 — at an
+  // endpoint average of 10 the two sides differed by up to 1 % of the span at
+  // the averaged edges).
   const n = be.length;
   if (n < 2) return new Array(n).fill(0);
+  const raw = rawIntensity || intensity;
   const shir = shirleyBackground(be, intensity, maxIter);
-  for (let i = 0; i < n; i++) shir[i] = Math.min(shir[i], intensity[i]);
+  for (let i = 0; i < n; i++) shir[i] = Math.min(shir[i], raw[i]);
   return shir;
 }
 
@@ -4734,7 +4746,7 @@ function computeBackgroundCore(be, intensity, settings) {
   // Compute background on the sliced region — apply endpoint averaging for Shirley types
   let bgSub;
   if (type === 'shirley') bgSub = shirleyBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
-  else if (type === 'smart') bgSub = smartBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
+  else if (type === 'smart') bgSub = smartBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter, inSub);   // clamp against the raw slice
   else if (type === 'smart_exp') bgSub = smartExperimentalBackground(beSub, inSub, iter, nAvg);
   else if (type === 'shirley_linear') bgSub = shirleyLinearBackground(beSub, inSub, iter, nAvg);
   else if (type === 'linear') bgSub = linearBackground(beSub, inSub);
diff --git a/tests/js/background_parity.test.js b/tests/js/background_parity.test.js
new file mode 100644
index 0000000..8c9e728
--- /dev/null
+++ b/tests/js/background_parity.test.js
@@ -0,0 +1,90 @@
+// Unit 4 (2026-09-27): the page's background twins against fitting.py — the
+// curve the page draws, saves and fits locally against must be the one the
+// server fits against. Task 4 (docs/superpowers/plans/2026-09-02-task4-
+// background-twin-parity.md) measured the gaps and proved their causes;
+// this unit fixes the two JS bugs it found and PINS the parity:
+//   S4 shirley: the JS integrated the raw net signal, fitting.py max(y−B, 0)
+//      (0.015–0.24 % of the span at convergence);
+//   S5 smart at endpoint averaging > 1: the JS clamped against the averaged
+//      copy, fitting.py against the raw data (up to 1 % of the span).
+// shirley_linear is DE-LISTED (not offered): its order-sensitivity on
+// descending grids (27–33 % of the span, Task 4 cause 3) is pinned as a KNOWN
+// GAP, not fixed. Convergence semantics (the UI's Shirley iteration count vs
+// the server's tolerance) are Part 5 of the sealed-fit-record memo, not this
+// unit: the JS runs at a converged iteration count here.
+//
+// The JS runs computeBackgroundCore (the page's own dispatcher) extracted
+// verbatim; the Python side calls fitting.py's own functions through
+// tests/js/background_parity_backend.py.
+const { test } = require('node:test');
+const assert = require('node:assert');
+const fs = require('node:fs');
+const path = require('node:path');
+const { execFileSync } = require('node:child_process');
+
+const REPO_ROOT = path.join(__dirname, '../..');
+const html = fs.readFileSync(path.join(REPO_ROOT, 'templates/index.html'), 'utf8');
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
+const PYTHON = (() => {
+  for (const c of [path.join(REPO_ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3']) {
+    if (fs.existsSync(c)) return c;
+  }
+  return 'python3';
+})();
+const BRIDGE = path.join(__dirname, 'background_parity_backend.py');
+const py = req => JSON.parse(execFileSync(PYTHON, [BRIDGE], { input: JSON.stringify(req), encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }));
+
+const JS = new Function([
+  'shirleyBackground', 'smartBackground', 'smartExperimentalBackground', 'shirleyLinearBackground',
+  'linearBackground', 'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
+].map(extractFn).join('\n') + '\nconst manualAnchorBackground = () => { throw new Error("not in this test"); };' +
+  '\nreturn { computeBackgroundCore };')();
+const CONVERGED_ITER = 200;
+const jsBg = (be, inten, method, nAvg) => JS.computeBackgroundCore(be, inten,
+  { bgType: method, shirleyIter: String(CONVERGED_ITER), endpointAvg: String(nAvg), bgStart: '', bgEnd: '' });
+
+const CASES = py({ mode: 'cases' });
+const span = y => Math.max(...y) - Math.min(...y);
+function maxRelDiff(a, b, sp) { let m = 0; for (let i = 0; i < a.length; i++) m = Math.max(m, Math.abs(a[i] - b[i])); return m / sp; }
+function compare(method, nAvg) {
+  const py_out = py({ mode: 'bg', items: CASES.map(c => ({ method, be: c.be, inten: c.inten, n_avg: nAvg })) });
+  return CASES.map((c, k) => ({ label: c.label, rel: maxRelDiff(jsBg(c.be, c.inten, method, nAvg), py_out[k], span(c.inten)) }));
+}
+
+test('the cases include the committed real U 4f scan, ascending and descending', () => {
+  assert.ok(CASES.length >= 6, CASES.map(c => c.label).join('; '));
+  assert.ok(CASES.some(c => /real U 4f/.test(c.label) && /descending/.test(c.label)));
+});
+
+// Parity tolerance: 1e-6 of the intensity span — far below Task 4's smallest
+// measured gap (1.5e-4 of the span, the unclamped Shirley) and far above the
+// difference between 200 JS iterations and the server's 1e-6-count stopping
+// tolerance.
+const TOL = 1e-6;
+for (const method of ['shirley', 'smart', 'smart_exp', 'tougaard', 'linear']) {
+  for (const nAvg of [1, 10]) {
+    test(`${method}, endpoint average ${nAvg}: the page's background equals the server's within ${TOL} of the span on every case`, () => {
+      for (const r of compare(method, nAvg)) assert.ok(r.rel <= TOL, `${r.label}: ${r.rel.toExponential(2)} of the span`);
+    });
+  }
+}
+
+test('KNOWN GAP (de-listed, not fixed): shirley_linear agrees on ascending grids and diverges on descending ones (Task 4 cause 3)', () => {
+  const rows = compare('shirley_linear', 1);
+  for (const r of rows.filter(r => /ascending/.test(r.label))) assert.ok(r.rel <= 1e-3, `${r.label}: ${r.rel}`);
+  const desc = rows.filter(r => /descending/.test(r.label));
+  assert.ok(desc.some(r => r.rel > 0.05), 'still diverges on descending grids: ' + desc.map(r => r.rel.toFixed(3)).join(', ') +
+    ' — if this starts failing, the gap was closed; update the pin and CLAUDE.md');
+  assert.match(html, /<option value="shirley_linear" disabled hidden/, 'shirley_linear stays de-listed (disabled, hidden; shown only for saved files that use it)');
+});
diff --git a/tests/js/background_parity_backend.py b/tests/js/background_parity_backend.py
new file mode 100644
index 0000000..c321c86
--- /dev/null
+++ b/tests/js/background_parity_backend.py
@@ -0,0 +1,84 @@
+#!/usr/bin/env python3
+"""Backend bridge for tests/js/background_parity.test.js (unit 4, 2026-09-27).
+
+stdin {"mode": "cases"} -> the spectra the parity test runs on: seeded
+synthetic spectra (a narrow C 1s, a wide U 4f doublet) and the committed real
+U 4f Scan_0 (1-GTA UCl4-graphite project), each ascending AND descending.
+stdin {"mode": "bg", "items": [{"method", "be", "inten", "n_avg"}...]} -> the
+background fitting.py's OWN function returns for each (the functions run_fit
+calls for the anchor window, never a reimplementation).
+"""
+import io
+import json
+import os
+import sys
+import zipfile
+
+import numpy as np
+
+ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
+sys.path.insert(0, ROOT)
+import fitting  # noqa: E402
+
+FUNCS = {
+    "shirley": lambda x, y, n: fitting.shirley_background(x, y, n_avg=n),
+    "smart": lambda x, y, n: fitting.smart_background(x, y, n_avg=n),
+    "smart_exp": lambda x, y, n: fitting.smart_experimental_background(x, y, n_avg=n),
+    "shirley_linear": lambda x, y, n: fitting.shirley_linear_background(x, y, n_avg=n),
+    "tougaard": lambda x, y, n: fitting.tougaard_background(x, y, n_avg=n),
+    "linear": lambda x, y, n: fitting.linear_background(x, y),
+}
+
+
+def _g(x, c, a, w):
+    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)
+
+
+def _shirley_step(x, c, a, w, h):
+    # a loss step under each line, high-BE side (makes Shirley non-trivial)
+    return h * a / (1 + np.exp(-(x - c) / (0.4 * w)))
+
+
+def cases():
+    rng = np.random.default_rng(20260927)
+    out = []
+    x = np.linspace(280.0, 295.0, 101)
+    y = rng.poisson(400 + _g(x, 284.5, 6000, 1.0) + _g(x, 286.3, 1200, 1.2) + _shirley_step(x, 284.5, 6000, 1.0, 0.06)).astype(float)
+    out.append(("synthetic C 1s, 101 pts", x, y))
+    x = np.linspace(370.0, 405.0, 351)
+    y = rng.poisson(2000 + _g(x, 380.9, 20000, 1.6) + _g(x, 391.8, 15000, 1.6)
+                    + _shirley_step(x, 380.9, 20000, 1.6, 0.08) + _shirley_step(x, 391.8, 15000, 1.6, 0.08)).astype(float)
+    out.append(("synthetic U 4f doublet, 351 pts", x, y))
+    proj = os.path.join(ROOT, "docs", "autofit", "test_data", "1-GTA UCl4-graphite one set of U doublets.proj.zip")
+    if os.path.exists(proj):
+        with zipfile.ZipFile(proj) as z:
+            man = json.loads(z.read("manifest.json"))
+            for sp in man.get("spectra", []):
+                if sp.get("name") == "U4f Scan_0":
+                    rec = json.loads(z.read(sp["filename"]))
+                    be = np.asarray(rec["rawBE"], float) - float(rec.get("ccShift") or 0)
+                    out.append(("real U 4f Scan_0 (committed project)", be, np.asarray(rec["rawIntensity"], float)))
+                    break
+    res = []
+    for label, x, y in out:
+        asc = np.argsort(x)
+        res.append({"label": label + ", ascending", "be": x[asc].tolist(), "inten": y[asc].tolist()})
+        res.append({"label": label + ", descending", "be": x[asc][::-1].tolist(), "inten": y[asc][::-1].tolist()})
+    return res
+
+
+def main():
+    req = json.load(sys.stdin)
+    if req["mode"] == "cases":
+        json.dump(cases(), sys.stdout)
+        return
+    out = []
+    for it in req["items"]:
+        x = np.asarray(it["be"], float)
+        y = np.asarray(it["inten"], float)
+        out.append([float(v) for v in FUNCS[it["method"]](x, y, int(it["n_avg"]))])
+    json.dump(out, sys.stdout)
+
+
+if __name__ == "__main__":
+    main()

exec
/bin/zsh -lc "rg -n '"'^(def (shirley_background|smart_background|linear_background|smart_experimental_background|run_fit)|function (shirleyBackground|smartBackground|computeBackgroundCore|_applyEndpointAveraging|_bgWindowIndices))|smartBackground'"\\(|computeBackground\\(|computeBackgroundCore\\(|shirleyBackground\\(|bgIntensity|bgSubtracted' fitting.py templates/index.html tests/js | head -230; sed -n '330,545p' fitting.py; sed -n '4398,4458p' templates/index.html; sed -n '4690,4795p' templates/index.html; ls tests/js" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
fitting.py:338:def shirley_background(
fitting.py:402:def smart_background(
fitting.py:422:def linear_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
fitting.py:428:def smart_experimental_background(
fitting.py:2094:def run_fit(*args, cancel=None, **kwargs):
templates/index.html:3464:        // bgSubtractedView is missing from pre-feature saves → falsy default
templates/index.html:3465:        active.ui.bgSubtractedView = !!data.background.bgSubtractedView;
templates/index.html:3841:      bgSubtractedView: !!document.getElementById('bg-sub-toggle')?.checked,
templates/index.html:3896:      const want = !!ui.bgSubtractedView;
templates/index.html:4408:function shirleyBackground(be, intensity, maxIter) {
templates/index.html:4438:function smartBackground(be, intensity, maxIter, rawIntensity) {
templates/index.html:4449:  const shir = shirleyBackground(be, intensity, maxIter);
templates/index.html:4598:function _applyEndpointAveraging(intensity, nAvg) {
templates/index.html:4672:  if (state.fitResult) state.fitResult.bgIntensity = null;
templates/index.html:4708:function _bgWindowIndices(be, bgStart, bgEnd) {
templates/index.html:4726:// computeBackground() below is a thin DOM-reading wrapper for callers
templates/index.html:4728:function computeBackgroundCore(be, intensity, settings) {
templates/index.html:4748:  if (type === 'shirley') bgSub = shirleyBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
templates/index.html:4749:  else if (type === 'smart') bgSub = smartBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter, inSub);   // clamp against the raw slice
templates/index.html:4778:function computeBackground(be, intensity) {
templates/index.html:4779:  return computeBackgroundCore(be, intensity, {
templates/index.html:5820:  const bgIntensity = computeBackground(be, inten);
templates/index.html:5821:  const netAmplitude = Math.max(intensityValue - bgIntensity[closestIdx], 100);
templates/index.html:6670:    if (t && !t.isStack && t.ui) t.ui.bgSubtractedView = toggle.checked;
templates/index.html:7357:  const bgI2 = computeBackground(be2, inten2);
templates/index.html:7366:    be: be2, bgSubtracted: bgSub2, bgIntensity: bgI2,
templates/index.html:7602:  const bgI = computeBackground(corrBE, inten);
templates/index.html:7732:    const ok = applyAutoFitResult(json, graphiteRaw, { be: be2, inten: inten2, bgIntensity: bgI, bgSubtracted: bgSub });
templates/index.html:8139:  const bgIntensity = computeBackground(be, inten);
templates/index.html:8140:  const bgSubtracted = inten.map((v, i) => v - bgIntensity[i]);
templates/index.html:8263:                        chiReduced, rmse, be, bgSubtracted, bgIntensity, backendResult,
templates/index.html:8305:      const local = runFitLocal(be, bgSubtracted, bgIntensity);
templates/index.html:8466:function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
templates/index.html:8475:      !Array.isArray(bgSubtracted) || bgSubtracted.length !== be.length ||
templates/index.html:8476:      !Array.isArray(bgIntensity) || bgIntensity.length !== be.length ||
templates/index.html:8477:      !be.every(Number.isFinite) || !bgSubtracted.every(Number.isFinite) || !bgIntensity.every(Number.isFinite)) {
templates/index.html:8483:  const _w = be.map((_, i) => 1 / Math.sqrt(Math.max(bgSubtracted[i] + bgIntensity[i], 1)));
templates/index.html:8580:    return be.map((_, i) => bgSubtracted[i] - model[i]);
templates/index.html:8805:      verdicts[String(wp.id)] = _componentSupportCore(bgSubtracted, model, comp, _w, nFreeComp, nVaried);
templates/index.html:8814:  state.fitResult = { chi, chiReduced, rmse, be, bgSubtracted, bgIntensity, roiRange,
templates/index.html:9261:  return computeBackgroundCore(be, inten, settings);
templates/index.html:9274://   A2: fitResult.be + fitResult.bgIntensity present, no fittedY (local
templates/index.html:9276://   B:  post-load, neither fr.be nor fr.bgIntensity present → derive be
templates/index.html:9318:      && Array.isArray(fr.bgIntensity)
templates/index.html:9319:      && fr.bgIntensity.length === fr.be.length) {
templates/index.html:9322:    bg = fr.bgIntensity.slice();
templates/index.html:9804:                     Array.isArray(state.fitResult.bgIntensity) &&
templates/index.html:9805:                     state.fitResult.bgIntensity.length === state.fitResult.be.length);
templates/index.html:9811:  const plotBG = haveFit ? state.fitResult.bgIntensity
templates/index.html:9812:                         : (be.length ? computeBackground(be, inten) : []);
templates/index.html:9813:  const plotInten = haveFit && Array.isArray(state.fitResult.bgSubtracted)
templates/index.html:9814:                    ? state.fitResult.bgSubtracted.map((v, i) => v + plotBG[i])
templates/index.html:9816:  const bgSubtracted = haveFit && Array.isArray(state.fitResult.bgSubtracted)
templates/index.html:9817:                       ? state.fitResult.bgSubtracted
templates/index.html:9831:    : bgSubtracted.map((v, i) => v - modelFull[i]);
templates/index.html:9834:    const d = fittedYBacked ? plotInten[i] : bgSubtracted[i];
templates/index.html:10517:      bgSubtractedView: !!document.getElementById('bg-sub-toggle')?.checked,
templates/index.html:10558:  const bgIntensity = computeBackground(be, inten);
templates/index.html:10560:  const bgSub = inten.map((v, i) => v - bgIntensity[i]);
templates/index.html:10565:  const fittedY = (_saveStats !== 'stale' && state.fitResult?.fittedY) || modelFull.map((v, i) => v + bgIntensity[i]);
templates/index.html:10616:    background: bgIntensity,
templates/index.html:10683:        bgIntensity: _roundIntensity(t.fitResult.bgIntensity),
templates/index.html:10684:        bgSubtracted: _roundIntensity(t.fitResult.bgSubtracted),
templates/index.html:11239:  const bgIntensity = computeBackground(be, inten);
templates/index.html:11251:  const bgSub = inten.map((v, i) => v - bgIntensity[i]);
templates/index.html:11256:      be[i].toFixed(4), inten[i].toFixed(2), bgIntensity[i].toFixed(2),
templates/index.html:11300:  const bgArr   = computeBackground(be, inten);
templates/index.html:11812:  const bgSub = fitResult.bgSubtracted;
templates/index.html:11816:    const bgI = fitResult.bgIntensity;
templates/index.html:12491:    const bgI = computeBackground(be, inten);
templates/index.html:14265:      bgSubtracted: [...(state.fitResult.bgSubtracted || [])],
templates/index.html:14266:      bgIntensity: state.fitResult.bgIntensity ? [...state.fitResult.bgIntensity] : null,
templates/index.html:16388:  // OWN be/bgIntensity arrays once a fit exists (updatePlot's "haveFit"
templates/index.html:16395:  // Peaks' own response has no be/fittedY/bgIntensity arrays to rebuild a
templates/index.html:16398:  // unfit-preview path (getROIData() + client-side computeBackground()),
tests/js/fit_acceptance.test.js:303:    fitResult: { chi: 1, chiReduced: 1e4, rmse: 100, objective: 'unweighted_residual_variance', be: [1, 2], bgIntensity: [0, 0], bgSubtracted: [1, 1] } };
tests/js/fit_acceptance.test.js:307:  const weighted = { ...older, fitResult: { chi: 1, chiReduced: 2, rmse: 100, be: [1, 2], bgIntensity: [0, 0], bgSubtracted: [1, 1] } };
tests/js/local_lm_descent.test.js:87:  const bg = env.computeBackgroundCore(be, inten, ui);
tests/js/stale_statistics.test.js:87:    chi: 12, chiReduced: 1.2346, rmse: 7.5, be: [1, 2, 3], bgIntensity: [0, 0, 0], bgSubtracted: [1, 2, 1],
tests/js/tougaard_twin.test.js:180:  const mainOut = computeBackgroundCore(be, intensity, {
tests/js/tougaard_twin.test.js:185:  const fallbackOut = computeBackgroundCore(be, intensity, {
tests/js/scattered_starts.test.js:220:  const rec = { peaks: env.state.peaks, ui: { ...env.ui, ccObs: '279.7', bgSubtractedView: true }, ccShift: -4.74, manualAnchors: [] };
tests/js/background_parity.test.js:54:const jsBg = (be, inten, method, nAvg) => JS.computeBackgroundCore(be, inten,
    if cap < 1:
        return y.copy()
    out = y.copy()
    out[:cap] = np.mean(y[:cap])
    out[-cap:] = np.mean(y[-cap:])
    return out


def shirley_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = 1e-6,
    n_avg: int = 1,
) -> np.ndarray:
    """
    Iterative Shirley background (Proctor & Sherwood, Surf. Sci. 1982).

    Works on ascending or descending binding energy arrays.

    ``n_avg`` averages the first/last ``n_avg`` points before the endpoint
    levels B_low/B_high are read (audit F3, 2026-07-17). Shirley scales the
    ENTIRE background off those two levels, so a single noisy endpoint
    sample propagates straight into the net area. n_avg=1 = raw endpoints =
    previous behaviour. Callers previously had to pre-average the input
    array themselves via _apply_endpoint_averaging; that convention was
    easy to forget (autofit/engine.py did), so the knob now lives here,
    matching smart_experimental_background / shirley_linear_background.

    At each energy Eᵢ the background equals:
        B(Eᵢ) = B_high + (B_low – B_high) · ∫_{Eᵢ}^{E_max} s(E) dE
                                               ─────────────────────────
                                               ∫_{E_min}^{E_max} s(E) dE
    where s(E) = max(y(E) – B(E), 0) is the net signal.
    B_low  = y(E_min),  B_high = y(E_max)  (the endpoint levels).
    """
    if len(x) < 2:
        return np.zeros_like(y)

    if n_avg > 1:
        y = _apply_endpoint_averaging(np.asarray(y, dtype=float), n_avg)

    # Work on ascending copy
    if x[0] > x[-1]:
        xs, ys = x[::-1].copy(), y[::-1].copy()
        flipped = True
    else:
        xs, ys = x.copy(), y.copy()
        flipped = False

    b_low = ys[0]    # background at low‑BE end
    b_high = ys[-1]  # background at high‑BE end

    B = np.linspace(b_low, b_high, len(ys))  # linear initial guess

    for _ in range(n_iter):
        B_prev = B.copy()
        signal = np.maximum(ys - B, 0.0)
        # O(n) cumulative integral from high-x end back to each point
        cum_right = np.zeros(len(ys))
        for i in range(len(ys) - 2, -1, -1):
            cum_right[i] = cum_right[i + 1] + 0.5 * (signal[i] + signal[i + 1]) * (xs[i + 1] - xs[i])
        total = cum_right[0]
        if total <= 0.0:
            break
        B = b_high + (b_low - b_high) * cum_right / total
        if np.max(np.abs(B - B_prev)) < tol:
            break

    return B[::-1] if flipped else B


def smart_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = 1e-6,
    n_avg: int = 1,
) -> np.ndarray:
    """Smart (constrained Shirley): standard Shirley clamped to never exceed data.

    ``n_avg`` is forwarded to shirley_background (audit F3). The clamp is
    applied against the RAW data, not the endpoint-averaged copy, so
    averaging only ever moves the background — never the reported net
    counts.
    """
    if len(x) < 2:
        return np.zeros_like(y)
    shir = shirley_background(x, y, n_iter, tol, n_avg=n_avg)
    return np.minimum(shir, y)


def linear_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Straight‑line background connecting the first and last data points."""
    slope = (y[-1] - y[0]) / (x[-1] - x[0]) if x[-1] != x[0] else 0.0
    return y[0] + slope * (x - x[0])


def smart_experimental_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = 1e-6,
    n_avg: int = 1,
) -> np.ndarray:
    """Experimental constrained Shirley background, closer to public Avantage
    Smart description.  The data constraint is enforced *during* iteration,
    not as a post-hoc clamp.  Where the background would exceed the data it
    locks to the data, effectively moving the Shirley start inward.  Better
    for narrow spectral windows with sloped baselines."""
    if len(x) < 2:
        return np.zeros_like(y)

    # Work on ascending copy
    if x[0] > x[-1]:
        xs, ys = x[::-1].copy(), y[::-1].copy()
        flipped = True
    else:
        xs, ys = x.copy(), y.copy()
        flipped = False

    n = len(ys)
    cap = max(1, min(n_avg, n // 4))
    b_low = float(np.mean(ys[:cap]))      # low-BE endpoint
    b_high = float(np.mean(ys[-cap:]))     # high-BE endpoint
    step = b_low - b_high

    # Linear initial guess
    B = np.linspace(b_low, b_high, n)

    for _ in range(n_iter):
        B_prev = B.copy()
        signal = np.maximum(ys - B, 0.0)
        # Cumulative integral from high-BE end (right) back to each point
        cum_right = np.zeros(n)
        for i in range(n - 2, -1, -1):
            dx = xs[i + 1] - xs[i]
            cum_right[i] = cum_right[i + 1] + (signal[i] + signal[i + 1]) / 2 * dx
        total = cum_right[0]
        if total <= 0.0:
            break

        B = b_high + step * (cum_right / total)

        # Constrain during iteration: lock to data where bg exceeds it
        B = np.minimum(B, ys)

        if np.max(np.abs(B - B_prev)) < tol:
            break

    B = np.minimum(B, ys)  # final safety clamp
    return B[::-1] if flipped else B


def shirley_linear_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = 1e-6,
    n_avg: int = 1,
) -> np.ndarray:
    """Hybrid Shirley + Linear background.

    1. Average *n_avg* points at each endpoint.
    2. Compute a linear baseline between the averaged endpoints.
    3. Subtract the linear baseline → flattened data.
    4. Iteratively compute a Shirley‑like cumulative correction on the
       flattened data, scaled by the endpoint step height.
    5. Add the correction back onto the linear baseline.
    6. Clamp so the background never exceeds the data.
    """
    if len(x) < 2:
        return np.zeros_like(y)

    # Work on ascending copy
    if x[0] > x[-1]:
        xs, ys = x[::-1].copy(), y[::-1].copy()
        flipped = True
    else:
        xs, ys = x.copy(), y.copy()
        flipped = False

    n = len(ys)
    cap = max(1, min(n_avg, n // 4))
    IL = float(np.mean(ys[:cap]))      # low‑BE endpoint
    IH = float(np.mean(ys[-cap:]))     # high‑BE endpoint

    # Linear baseline
    linear = np.linspace(IL, IH, n)

    # Flatten
    flat = ys - linear

    step_h = abs(IL - IH)
    if step_h < 1e-12:
        return linear[::-1] if flipped else linear

    B = np.zeros(n)
    for _ in range(n_iter):
        B_prev = B.copy()
        signal = np.maximum(flat - B, 0.0)
        # O(n) cumulative integral from high-x end back to each point
        cum_right = np.zeros(n)
        for i in range(n - 2, -1, -1):
            cum_right[i] = cum_right[i + 1] + 0.5 * (signal[i] + signal[i + 1]) * (xs[i + 1] - xs[i])
        total = cum_right[0]
        if total <= 0.0:
            break
        B = step_h * cum_right / total
        if np.max(np.abs(B - B_prev)) < tol:
            break

    result = np.minimum(linear + B, ys)
    return result[::-1] if flipped else result


  for (const p of peaks) {
    const yArr = evalPeakArray(beArray, p);
    for (let i = 0; i < N; i++) sums[i] += yArr[i];
  }
  return sums;
}

// ═══════════════════════════════════════════════════
// BACKGROUND SUBTRACTION
// ═══════════════════════════════════════════════════
function shirleyBackground(be, intensity, maxIter) {
  const n = be.length;
  if (n < 2) return new Array(n).fill(0);
  const I0 = intensity[0], I1 = intensity[n - 1];
  let bg = new Array(n).fill(0);

  for (let iter = 0; iter < maxIter; iter++) {
    const newBg = new Array(n).fill(0);
    for (let i = 0; i < n; i++) {
      // Net signal clamped at zero, max(y - B, 0), as fitting.shirley_background
      // (Proctor–Sherwood): a noise channel below the background contributes
      // no loss, never NEGATIVE loss (Task 4 S4, unit 4 2026-09-27 — the JS
      // integrated the raw difference and converged to a different fixed point,
      // 0.015–0.24 % of the span away from the background the server fits).
      let sumRight = 0;
      for (let j = i; j < n - 1; j++) {
        sumRight += (Math.max(intensity[j] - bg[j], 0) + Math.max(intensity[j + 1] - bg[j + 1], 0)) / 2 * Math.abs(be[j + 1] - be[j]);
      }
      let sumTotal = 0;
      for (let j = 0; j < n - 1; j++) {
        sumTotal += (Math.max(intensity[j] - bg[j], 0) + Math.max(intensity[j + 1] - bg[j + 1], 0)) / 2 * Math.abs(be[j + 1] - be[j]);
      }
      const frac = sumTotal > 0 ? sumRight / sumTotal : (n - 1 - i) / (n - 1);
      newBg[i] = I1 + (I0 - I1) * frac;
    }
    bg = newBg;
  }
  return bg;
}

function smartBackground(be, intensity, maxIter, rawIntensity) {
  // Smart (constrained Shirley): standard Shirley clamped to never exceed data.
  // The Shirley runs on `intensity` (the endpoint-averaged copy); the clamp is
  // against the RAW data (`rawIntensity`, defaulting to `intensity`), as
  // fitting.smart_background does: averaging only ever moves the background,
  // never the reported net counts (Task 4 S5, unit 4 2026-09-27 — at an
  // endpoint average of 10 the two sides differed by up to 1 % of the span at
  // the averaged edges).
  const n = be.length;
  if (n < 2) return new Array(n).fill(0);
  const raw = rawIntensity || intensity;
  const shir = shirleyBackground(be, intensity, maxIter);
  for (let i = 0; i < n; i++) shir[i] = Math.min(shir[i], raw[i]);
  return shir;
}

// Experimental constrained Shirley background, closer to the public Avantage
// Smart description: the data-constraint is enforced *during* iteration, not as
// a post-hoc clamp.  Where the background would exceed the data, it locks to
// the data and the effective Shirley start moves inward, improving behaviour on
// narrow windows with sloped baselines.
// rule getROIData uses for the ROI. This is the single definition shared by
// the preview (computeBackgroundCore) and both /api/fit request builders,
// which send end_idx = i1 + 1 because the backend slices Python-end-exclusive
// (unit 1c of docs/superpowers/plans/2026-09-02-background-architecture-
// sealed-fit-record.md, round-5 amendment — before 1c the builders sent the
// nearest grid index per bound and end_idx = i1, so the fit anchored one
// point inside the window the user drew).
// Returns inclusive indices { i0, i1 }. A blank/NaN bound, or fewer than two
// grid points inside the bounds, falls back to the full range.
// Contract notes (Codex round 1, both runs): (a) the window is the contiguous
// index span from the FIRST to the LAST in-range point — exact on a monotonic
// grid, which is what createTab guarantees (it sorts descending) and what
// every saved project written by this app carries; a hand-edited
// non-monotonic rawBE would make the span include out-of-window rows, and
// the preview and the request would still agree. (b) Indices are computed on
// the frontend grid before uploadToBackend rounds BE to 4 decimals; the
// backend only ever applies the indices to that same-length, same-order
// session grid, so rounding cannot change which rows are used.
function _bgWindowIndices(be, bgStart, bgEnd) {
  const n = be.length;
  const full = { i0: 0, i1: n - 1 };
  const a = parseFloat(bgStart), b = parseFloat(bgEnd);
  if (!Number.isFinite(a) || !Number.isFinite(b)) return full;
  const lo = Math.min(a, b), hi = Math.max(a, b);
  let i0 = -1, i1 = -1;
  for (let i = 0; i < n; i++) {
    if (be[i] >= lo && be[i] <= hi) { if (i0 < 0) i0 = i; i1 = i; }
  }
  if (i0 < 0 || i1 - i0 < 1) return full;
  return { i0, i1 };
}

// Pure-functional background computation. Takes explicit `settings`
// (matches the shape of tab.ui — bgType, bgStart, bgEnd, shirleyIter,
// endpointAvg) instead of reading from DOM. Used by stack-view render
// to reproduce a source tab's background from its persisted ui state.
// computeBackground() below is a thin DOM-reading wrapper for callers
// in the single-tab plot path.
function computeBackgroundCore(be, intensity, settings) {
  const type = settings.bgType;
  const iter = parseInt(settings.shirleyIter) || 5;
  const nAvg = parseInt(settings.endpointAvg) || 1;

  // Manual anchor background uses its own anchor points, not bg-start/end
  if (type === 'manual') return manualAnchorBackground(be, intensity);

  // The background window — the one definition shared with both /api/fit
  // request builders (see _bgWindowIndices). A blank bound or a window with
  // fewer than two points falls back to the full range inside the helper;
  // slicing the full range below is then a no-op.
  const { i0, i1 } = _bgWindowIndices(be, settings.bgStart, settings.bgEnd);

  // Slice data to background region
  const beSub = be.slice(i0, i1 + 1);
  const inSub = intensity.slice(i0, i1 + 1);

  // Compute background on the sliced region — apply endpoint averaging for Shirley types
  let bgSub;
  if (type === 'shirley') bgSub = shirleyBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
  else if (type === 'smart') bgSub = smartBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter, inSub);   // clamp against the raw slice
  else if (type === 'smart_exp') bgSub = smartExperimentalBackground(beSub, inSub, iter, nAvg);
  else if (type === 'shirley_linear') bgSub = shirleyLinearBackground(beSub, inSub, iter, nAvg);
  else if (type === 'linear') bgSub = linearBackground(beSub, inSub);
  // Averaged for the same reason as Shirley types: the Tougaard amplitude
  // is anchored at the high-BE edge, so endpoint noise feeds the anchor
  // directly. Mirrors fitting.py's run_fit / compute_background_only.
  else if (type === 'tougaard') bgSub = tougaardBackground(beSub, _applyEndpointAveraging(inSub, nAvg));
  else return new Array(be.length).fill(0);

  // Extend background across full data range:
  // - Points before bg region: hold first bg value (flat)
  // - Points inside bg region: use computed bg
  // - Points after bg region: hold last bg value (flat)
  const full = new Array(be.length).fill(0);
  const bgLeft  = bgSub[0];
  const bgRight = bgSub[bgSub.length - 1];

  for (let i = 0; i < be.length; i++) {
    if (i < i0) full[i] = bgLeft;
    else if (i <= i1) full[i] = bgSub[i - i0];
    else full[i] = bgRight;
  }

  return full;
}

// Thin DOM-reading wrapper used by single-tab updatePlot. Stack render
// path calls computeBackgroundCore directly with source-tab settings.
function computeBackground(be, intensity) {
  return computeBackgroundCore(be, intensity, {
    bgType:      document.getElementById('bg-type').value,
    shirleyIter: document.getElementById('shirley-iter').value,
    endpointAvg: document.getElementById('bg-endpoint-avg').value,
    bgStart:     document.getElementById('bg-start').value,
    bgEnd:       document.getElementById('bg-end').value,
  });
}

// ═══════════════════════════════════════════════════
// FILE PARSING
// ═══════════════════════════════════════════════════
function parseCSV(text) {
  const lines = text.trim().split('\n');
  const be = [], inten = [];
  for (const line of lines) {
    if (!line.trim() || line.startsWith('#') || line.startsWith('%')) continue;
autofit_c1s_gate.test.js
autofit_required.test.js
autofit_zero_graphite.test.js
background_parity.test.js
background_parity_backend.py
batch_propagation.test.js
bg_window_indices.test.js
endpoint_avg_default.test.js
find_peaks_coverage.test.js
find_peaks_endpoint_avg.test.js
find_peaks_periodic_table.test.js
find_peaks_plain_message.test.js
find_peaks_progress.test.js
fit_acceptance.test.js
fit_start_poll.test.js
fixtures
fp_experimental_notice.test.js
fp_material_mixed.test.js
lib
lineshape_parity.test.js
lineshape_parity_backend.py
lineshape_roundtrip.test.js
lineshape_roundtrip_backend.py
local_lm_descent.test.js
local_lm_server_parity_backend.py
module_state_scan.test.js
per_tab_state.test.js
ref_core.test.js
roi_clamp_centre_warning.test.js
scattered_starts.test.js
shape_switch_roundtrip.test.js
stale_statistics.test.js
tougaard_twin.test.js
unsupported_components.test.js

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 node --test tests/js/background_parity.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 exited 1 in 1139ms:
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity_backend.py", line 21, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/fitting.py", line 35, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins']
# node:child_process:955
#     throw err;
#     ^
# Error: Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity_backend.py
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity_backend.py", line 21, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/fitting.py", line 35, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins']
#     at genericNodeError (node:internal/errors:983:15)
#     at wrappedFn (node:internal/errors:537:14)
#     at checkExecSyncError (node:child_process:916:11)
#     at execFileSync (node:child_process:952:15)
#     at py (/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity.test.js:46:30)
#     at Object.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity.test.js:57:15)
#     at Module._compile (node:internal/modules/cjs/loader:1705:14)
#     at Object..js (node:internal/modules/cjs/loader:1838:10)
#     at Module.load (node:internal/modules/cjs/loader:1441:32)
#     at Function._load (node:internal/modules/cjs/loader:1263:12) {
#   status: 1,
#   signal: null,
#   output: [
#     null,
#     '',
#     'Traceback (most recent call last):\\n' +
#       '  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity_backend.py", line 21, in <module>\\n' +
#       '    import fitting  \# noqa: E402\\n' +
#       '    ^^^^^^^^^^^^^^\\n' +
#       '  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/fitting.py", line 35, in <module>\\n' +
#       '    from lmfit import Model, Parameters\\n' +
#       '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>\\n' +
#       '    from .confidence import conf_interval, conf_interval2d\\n' +
#       '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>\\n' +
#       '    from .minimizer import MinimizerException\\n' +
#       '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>\\n' +
#       '    from .parameter import Parameter, Parameters\\n' +
#       '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>\\n' +
#       '    from .jsonutils import decode4js, encode4js\\n' +
#       '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>\\n' +
#       '    import dill\\n' +
#       '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>\\n' +
#       '    from .session import (\\n' +
#       '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>\\n' +
#       '    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())\\n' +
#       '                               ^^^^^^^^^^^^^^^^^^^^^\\n' +
#       '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir\\n' +
#       '    return _os.fsdecode(_gettempdir())\\n' +
#       '                        ^^^^^^^^^^^^^\\n' +
#       '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir\\n' +
#       '    tempdir = _get_default_tempdir()\\n' +
#       '              ^^^^^^^^^^^^^^^^^^^^^^\\n' +
#       '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir\\n' +
#       '    raise FileNotFoundError(_errno.ENOENT,\\n' +
#       "FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins']\\n"
#   ],
#   pid: 56073,
#   stdout: '',
#   stderr: 'Traceback (most recent call last):\\n' +
#     '  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity_backend.py", line 21, in <module>\\n' +
#     '    import fitting  \# noqa: E402\\n' +
#     '    ^^^^^^^^^^^^^^\\n' +
#     '  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/fitting.py", line 35, in <module>\\n' +
#     '    from lmfit import Model, Parameters\\n' +
#     '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>\\n' +
#     '    from .confidence import conf_interval, conf_interval2d\\n' +
#     '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>\\n' +
#     '    from .minimizer import MinimizerException\\n' +
#     '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>\\n' +
#     '    from .parameter import Parameter, Parameters\\n' +
#     '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>\\n' +
#     '    from .jsonutils import decode4js, encode4js\\n' +
#     '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>\\n' +
#     '    import dill\\n' +
#     '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>\\n' +
#     '    from .session import (\\n' +
#     '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>\\n' +
#     '    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())\\n' +
#     '                               ^^^^^^^^^^^^^^^^^^^^^\\n' +
#     '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir\\n' +
#     '    return _os.fsdecode(_gettempdir())\\n' +
#     '                        ^^^^^^^^^^^^^\\n' +
#     '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir\\n' +
#     '    tempdir = _get_default_tempdir()\\n' +
#     '              ^^^^^^^^^^^^^^^^^^^^^^\\n' +
#     '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir\\n' +
#     '    raise FileNotFoundError(_errno.ENOENT,\\n' +
#     "FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins']\\n"
# }
# Node.js v22.22.2
# Subtest: tests/js/background_parity.test.js
not ok 1 - tests/js/background_parity.test.js
  ---
  duration_ms: 1195.499281
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity.test.js:1:1'
  failureType: 'testCodeFailure'
  exitCode: 1
  signal: ~
  error: 'test failed'
  code: 'ERR_TEST_FAILURE'
  ...
1..1
# tests 1
# suites 0
# pass 0
# fail 1
# cancelled 0
# skipped 0
# todo 0
# duration_ms 1203.166379

codex
The smart clamp has one production caller, and it now receives the raw anchor slice. The bridge calls `fitting.py` directly. I’m checking short and non-uniform grids next, especially whether the new zero clamp interacts badly with the existing initialization and zero-integral fallback.
exec
/bin/zsh -lc "rg -n 'bg_func|bg_method|background_type|shirley_background\\(|smart_background\\(|tougaard_background\\(|bg_start|start_idx|end_idx' fitting.py | tail -85; sed -n '1,150p' tests/js/lib/load_app.js; sed -n '12460,12525p' templates/index.html; sed -n '11275,11330p' templates/index.html; sed -n '16400,16450p' templates/index.html; rg -n 'AGENTS|review|must|MUST' CLAUDE.md | head -40" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
338:def shirley_background(
402:def smart_background(
418:    shir = shirley_background(x, y, n_iter, tol, n_avg=n_avg)
546:def tougaard_background(
1538:    bg_start_idx: int | None = None,
1539:    bg_end_idx: int | None = None,
1557:    bg_start_idx      : slice start for background region (None → 0)
1558:    bg_end_idx        : slice end for background region   (None → len)
1599:    # The fit runs on the ENTIRE incoming ROI; bg_start_idx / bg_end_idx
1604:    i0 = bg_start_idx if bg_start_idx is not None else 0
1605:    i1 = bg_end_idx if bg_end_idx is not None else len(energy)
1638:    bg_method = background_method.lower()
1641:    if manual_bg is not None and bg_method == "manual":
1652:    elif bg_method == "shirley":
1653:        bg_inner = shirley_background(x_bg, y_bg, n_avg=endpoint_avg)
1654:    elif bg_method == "smart":
1655:        bg_inner = smart_background(x_bg, y_bg, n_avg=endpoint_avg)
1656:    elif bg_method == "smart_exp":
1658:    elif bg_method == "shirley_linear":
1660:    elif bg_method == "tougaard":
1661:        bg_inner = tougaard_background(x_bg, y_bg, n_avg=endpoint_avg)
1662:    elif bg_method == "linear":
1671:    elif bg_method in ("none", "flat", "", "manual"):
2061:    start_idx: int | None = None,
2062:    end_idx: int | None = None,
2066:    i0 = start_idx if start_idx is not None else 0
2067:    i1 = end_idx if end_idx is not None else len(energy)
2071:        bg = shirley_background(x, y, n_avg=endpoint_avg)
2073:        bg = smart_background(x, y, n_avg=endpoint_avg)
2079:        bg = tougaard_background(x, y, n_avg=endpoint_avg)
sed: tests/js/lib/load_app.js: No such file or directory
    tgt.fitResult = null;
    tgt.modelProvenance = srcProvenance ? { ...srcProvenance, copiedFrom: sourceTab.name } : null;

    // Now activate this tab so state is populated. activateTab is a no-op
    // when the target is ALREADY active (the user switched to it during the
    // previous target's fit): then live state still holds the target's old
    // model and the post-fit sync would overwrite the propagated record —
    // load the record into live state explicitly (Codex round 3, run B).
    if (tabManager.activeId === tid) {
      state.peaks = tgt.peaks; state.nextId = tgt.nextId; state.ccShift = tgt.ccShift;
      state.fitResult = null;   // live copy of tgt.fitResult = null above (unit A0)
      tabManager._restoreUI(tgt.ui);
      renderPeakList();
      _refreshRoiAndCentreWarnings();   // this branch does not redraw: the hint must describe the target's window (Codex round 2)
    } else {
      tabManager.activateTab(tid);
    }

    // Small yield so progress message renders
    await new Promise(r => setTimeout(r, 20));
    if (_activeTab() !== tgt) {
      // The user switched tabs during the yield: fitting would read and
      // write whichever tab is active now. Stop here; targets already
      // fitted keep their results.
      notify('Batch fit stopped at ' + tgt.name + ' — the tab changed while it was running.', 'amber');
      break;
    }

    // Run local fit
    const roiSt = _roiWindowStatus();    // warn only: the fit below uses getROIData() exactly as before
    const { be, inten } = getROIData();
    const bgI = computeBackground(be, inten);
    const bgSub = inten.map((v, idx) => v - bgI[idx]);
    const outcome = runFitLocal(be, bgSub, bgI);

    // Sync result back to record
    tabManager._syncActiveToRecord();

    // Read the statistic from the fit's own return value, not from live
    // state: the active tab can change while the fit runs.
    const ok = !!(outcome && outcome.success);
    results.push({ name: tgt.name, ok, roiHint: _roiHintFor(roiSt),
                   chi: ok && Number.isFinite(outcome.chiReduced) ? outcome.chiReduced : null,
                   message: ok ? null : ((outcome && outcome.message) || 'local fit did not converge') });

    await new Promise(r => setTimeout(r, 10));
  }

  _snapshotSuppressed = false;

  // Return to source tab
  tabManager.activateTab(sourceId);

  const nOk = results.filter(r => r.ok).length;
  const nFail = results.length - nOk;
  prog.textContent = `Batch complete: ${nOk} converged as starting points, ${nFail} not fitted. Run Fit on each spectrum before reporting.`;
  const roiNote = r => r.roiHint ? ` <span class="roi-hint${r.roiHint.cls ? ' ' + r.roiHint.cls : ''}" style="display:inline">${_escHtml(r.roiHint.text)}</span>` : '';
  summary.innerHTML = results.map(r => r.ok
    ? `<div class="prop-row">${_escHtml(r.name)}: converged &mdash; &#967;&#178;<sub>r</sub> = ${r.chi != null ? r.chi.toFixed(3) : 'n/a'} (local fit: a starting point, not a reportable result)${roiNote(r)}</div>`
    : `<div class="prop-row" style="color:var(--red,#f87171)">${_escHtml(r.name)}: NOT fitted &mdash; ${_escHtml(r.message)} (model copied, no result stored)${roiNote(r)}</div>`
  ).join('') + `<div class="prop-row" style="color:var(--red,#f87171);margin-top:4px">&#9888; Charge corrections marked in red need verification</div>`;
  summary.style.display = 'block';
  btn.disabled = false;
}

// ══════════════════════════════════════════════════════════════
}

// ═══════════════════════════════════════════════════
// EXPORT PUBLICATION FIGURE
// ═══════════════════════════════════════════════════
function exportFigure() {
  if (!state.rawBE.length) { notify('No spectrum loaded.', 'red'); return; }
  const activeTab = tabManager.tabs.find(t => t.id === tabManager.activeId);
  const baseName  = (activeTab?.name || activeTab?.label || 'spectrum')
                    .replace(/[^a-zA-Z0-9_.-]/g, '_');
  document.getElementById('expfig-fname').value = baseName + '_spectrum';
  document.getElementById('expfig-residuals').checked = !!state.fitResult;
  document.getElementById('export-figure-modal-overlay').classList.add('open');
}

function _doPublicationExport() {
  const fname      = (document.getElementById('expfig-fname').value.trim() || 'xps_spectrum')
                     .replace(/\.png$/i, '');
  const inclResid  = document.getElementById('expfig-residuals').checked;
  const inclLabels = document.getElementById('expfig-peaklabels').checked;
  document.getElementById('export-figure-modal-overlay').classList.remove('open');

  const { be, inten } = getROIData();
  if (!be.length) { notify('No data in ROI.', 'red'); return; }

  const bgArr   = computeBackground(be, inten);
  // F1: a stale result's fitted curve is the previous model's: not drawn as "Fit"
  const _figStats = _statsLiveState();
  const fittedY = (_figStats !== 'stale' && state.fitResult?.fittedY?.length === be.length) ? state.fitResult.fittedY : null;
  const residArr = fittedY ? inten.map((v, i) => v - fittedY[i]) : null;
  const invert   = document.getElementById('invert-be').checked;
  const showIndiv = document.getElementById('show-individual').checked;

  // ── Canvas dimensions (6×4 in @ 300 DPI) ────────────────────────────────
  const W = 1800, H = 1200;
  // Margins
  const ML = 162, MR = 60, MT = 60, MB = 118;
  const plotX = ML, plotW = W - ML - MR;
  const hasResid = inclResid && residArr;
  const gapH = 28;
  const mainH  = hasResid ? Math.round((H - MT - MB - gapH) * 0.795) : H - MT - MB;
  const residH = hasResid ? (H - MT - MB - gapH - mainH) : 0;
  const mainTop  = MT;
  const residTop = hasResid ? mainTop + mainH + gapH : 0;

  const canvas = document.createElement('canvas');
  canvas.width = W; canvas.height = H;
  const ctx = canvas.getContext('2d');

  // White background
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, W, H);

  // ── Axis ranges ──────────────────────────────────────────────────────────
  const beMin = _arrMin(be), beMax = _arrMax(be);
  let rawYMin = Infinity, rawYMax = -Infinity;
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
49:| `POST`   | `/api/upload`             | Upload a spectrum file; returns `session_id` + downsampled preview. |
51:| `GET`    | `/api/session/<id>`       | Retrieve a stored session's preview data. |
123:**What the page draws must be what the server fitted.** Two harnesses pin
187:When two places read the same input — the page and the server, a preview
188:and a fit, a comparison and the thing it compares — they must read it the
191:a free η to the server (A03); the ROI, the preview background and the fitted
198:must read each field exactly the way its consumer reads it — integers as
241:The DS tail MUST always point toward **higher binding energy** (the left
255:the exponential envelope must decay.
277:were actually being fit against, due to a pre-existing preview/backend
308:- `evalPeak` switch + grid-aware `laTrueCasaXPS_array` evaluator (called via `evalPeakArray`; DS+G's grid-aware twin is `dsgConvolved_array` — a convolved shape's scalar `evalPeak` branch ignores m and must have no caller, parity guard (C))
329:parameters** from its parent. The sync block must cover every shape
443:(in review each such no-op edit moved an area fraction by 15–45 pp
488:second thing (a reviewer tried a deterministic perturbation base: identical
521:the largest move named, amber > 0.5 eV, red > 1 eV) with Preview (the
522:history-preview overlay, on a copy) and "Use this solution": explicit, one
540:the comparison no longer applies, nothing can be previewed or applied, an
541:open alternative preview is dropped (`_dropStaleAltPreview`), and
552:the app must never substitute a chemical interpretation because it scored
622:must make the fit significantly worse — `fitting._component_support`, the
743:| `tougaard` | Single-pass universal cross-section K(T) = B·T/(C+T²)², B = 2866 eV², C = 1643 eV² (Tougaard, *Surf. Interface Anal.* **1988**, 11, 453; kernel max at √(C/3) ≈ 23.4 eV). Order-robust (either BE direction); amplitude anchored to the data at the high-BE edge. JS twin `tougaardBackground` must stay in numerical agreement (pinned by `tests/js/tougaard_twin.test.js`). |
780:"Graphite" component, so the data must SUPPORT that component
782:threshold: removing it from the fitted model must make the fit to the

exec
/bin/zsh -lc "sed -n '1595,1695p' fitting.py; sed -n '90,205p' CLAUDE.md; rg -n 'shirley_linear|smartBackground|shirleyBackground' --glob '"'!docs/**'"' --glob '"'!xps-fitting-tool.html'"' --glob '"'!templates/index.html'"' --glob '"'!fitting.py'"' | head -70; ls tests/js/lib" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
            isinstance(caller_seed, (bool, np.bool_)) or not isinstance(caller_seed, (int, np.integer))
            or not 0 <= int(caller_seed) < 2 ** 32):
        raise ValueError("fit_kws.fit_kws.seed must be an integer in [0, 2**32)")

    # The fit runs on the ENTIRE incoming ROI; bg_start_idx / bg_end_idx
    # narrow only the anchor window used to construct the background
    # curve. Reusing the slice for both was the bug where putting bg
    # anchors inside the ROI silently chopped the fit window — and the
    # reported χ², residuals, and σ — down to that same sub-slice.
    i0 = bg_start_idx if bg_start_idx is not None else 0
    i1 = bg_end_idx if bg_end_idx is not None else len(energy)
    i0 = max(0, i0)
    i1 = min(len(energy), i1)
    # Normalize the user-supplied anchor pair: reversed order is a valid
    # choice — the frontend sends bg-start = higher BE and bg-end = lower
    # BE, so the index order depends on whether the data array is
    # BE-ascending or BE-descending. Treat the pair as an unordered
    # anchor window regardless of direction.
    if i0 > i1:
        i0, i1 = i1, i0
    # Bail to the full ROI only if the normalized window is genuinely
    # unusable (< 2 points): the integral / interp / linear-fit
    # functions below all need at least two distinct anchor points.
    if i1 - i0 < 2:
        i0, i1 = 0, len(energy)

    x = energy
    y = counts
    x_bg = energy[i0:i1]
    y_bg = counts[i0:i1]

    # ── Background ────────────────────────────────────────────────────────────
    # Integral backgrounds (Shirley, Tougaard, Smart variants) are
    # physically defined only between the user's two anchor points: the
    # integral represents inelastic-loss cumulation through the peaks
    # *between* those anchors. Computing them over the full ROI would
    # let peaks outside the anchor window contribute to the loss
    # integral, which violates the model's premise. We therefore
    # compute them on [i0:i1] and flat-hold the endpoint value across
    # the rest of the ROI — Shirley/Tougaard asymptote to the anchor
    # values by construction, so constant extension is the least-bad
    # continuation. Linear backgrounds are extrapolated across the
    # full ROI (the line is well-defined outside the anchor window).
    bg_method = background_method.lower()
    bg_inner: np.ndarray | None = None

    if manual_bg is not None and bg_method == "manual":
        # manual_bg is a list of [be, intensity] anchor points from the
        # frontend. The anchors are BE-anchored (independent of i0/i1),
        # so interpolate them across the full ROI grid.
        anchors = sorted(manual_bg, key=lambda a: a[0])
        if len(anchors) >= 2:
            anchor_x = np.array([a[0] for a in anchors])
            anchor_y = np.array([a[1] for a in anchors])
            bg = np.interp(x, anchor_x, anchor_y)
        else:
            bg = linear_background(x, y)
    elif bg_method == "shirley":
        bg_inner = shirley_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "smart":
        bg_inner = smart_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "smart_exp":
        bg_inner = smart_experimental_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "shirley_linear":
        bg_inner = shirley_linear_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "tougaard":
        bg_inner = tougaard_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "linear":
        # Extrapolate the line through (E[i0], y[i0]) ↔ (E[i1-1], y[i1-1])
        # across the full ROI. The line is well-defined everywhere, so
        # constant extension would discard real information.
        if x[i1 - 1] != x[i0]:
            slope = (y[i1 - 1] - y[i0]) / (x[i1 - 1] - x[i0])
        else:
            slope = 0.0
        bg = y[i0] + slope * (x - x[i0])
    elif bg_method in ("none", "flat", "", "manual"):
        bg = np.zeros_like(y)
    else:
        raise ValueError(f"Unknown background method '{background_method}'")

    if bg_inner is not None:
        # Embed the anchor-window integral background into a full-ROI
        # array; flat-hold the endpoint value outside [i0, i1]. In the
        # common case where the user keeps bg anchors at the ROI edges
        # this is a no-op (i0=0, i1=len(y)).
        bg = np.zeros_like(y)
        if len(bg_inner) > 0:
            bg[i0:i1] = bg_inner
            if i0 > 0:
                bg[:i0] = bg_inner[0]
            if i1 < len(y):
                bg[i1:] = bg_inner[-1]

    y_sub = y - bg

    # Poisson weights: σ = √(raw counts), weight = 1/σ
    # Use raw counts (before background subtraction) for uncertainty estimate,
    # since the noise comes from the total photon counting statistics.
    # Floor at 1.0 to avoid division by zero for zero-count channels.
    sigma = np.sqrt(np.maximum(y, 1.0))

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
CLAUDE.md:741:| `shirley_linear` | Shirley with a linear-fallback bridge. |
CLAUDE.md:753:the span away). Known gaps, pinned: `shirley_linear` (de-listed) diverges on
templates/index.html.pre-audit:1831:function shirleyBackground(be, intensity, maxIter) {
templates/index.html.pre-audit:1856:function smartBackground(be, intensity, maxIter) {
templates/index.html.pre-audit:1934:    if (type === 'shirley') return shirleyBackground(be, intensity, iter);
templates/index.html.pre-audit:1935:    if (type === 'smart') return smartBackground(be, intensity, iter);
templates/index.html.pre-audit:1950:  if (type === 'shirley') bgSub = shirleyBackground(beSub, inSub, iter);
templates/index.html.pre-audit:1951:  else if (type === 'smart') bgSub = smartBackground(beSub, inSub, iter);
scripts/local_server_gap.js:33:  'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
autofit/parity.py:33:    shirley_linear_background,
autofit/parity.py:103:    elif m == "shirley_linear":
autofit/parity.py:104:        bg_inner = shirley_linear_background(xb, yb, n_avg=endpoint_avg)
tests/test_background_n_avg.py:3:used by smart_experimental_background / shirley_linear_background, and
tests/js/local_lm_descent.test.js:39:  'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
tests/js/background_parity.test.js:10:// shirley_linear is DE-LISTED (not offered): its order-sensitivity on
tests/js/background_parity.test.js:49:  'shirleyBackground', 'smartBackground', 'smartExperimentalBackground', 'shirleyLinearBackground',
tests/js/background_parity.test.js:83:test('KNOWN GAP (de-listed, not fixed): shirley_linear agrees on ascending grids and diverges on descending ones (Task 4 cause 3)', () => {
tests/js/background_parity.test.js:84:  const rows = compare('shirley_linear', 1);
tests/js/background_parity.test.js:89:  assert.match(html, /<option value="shirley_linear" disabled hidden/, 'shirley_linear stays de-listed (disabled, hidden; shown only for saved files that use it)');
tests/js/background_parity_backend.py:27:    "shirley_linear": lambda x, y, n: fitting.shirley_linear_background(x, y, n_avg=n),
tests/js/bg_window_indices.test.js:100:    'shirleyBackground', 'smartBackground', 'smartExperimentalBackground',
tests/test_shirley_linear_kept.py:1:"""The shirley_linear implementation is KEPT after the UI de-listing
tests/test_shirley_linear_kept.py:15:def test_backend_still_fits_with_shirley_linear():
tests/test_shirley_linear_kept.py:19:                        background_method="shirley_linear", bg_start_idx=0, bg_end_idx=len(x))
tests/test_shirley_linear_kept.py:27:    assert "type === 'shirley_linear'" in html, "computeBackgroundCore must still route shirley_linear"
tests/test_shirley_linear_kept.py:28:    assert 'option value="shirley_linear"' in html, "the option must stay in the DOM (hidden) for saved files"
tests/test_browser_shirley_linear_delist.py:1:"""Real-browser guard for the SAFE de-listing of the shirley_linear background.
tests/test_browser_shirley_linear_delist.py:8:carries bgType 'shirley_linear' still loads, renders and fits exactly as
tests/test_browser_shirley_linear_delist.py:13:  * a restored tab with ui.bgType == 'shirley_linear' selects it, un-hides
tests/test_browser_shirley_linear_delist.py:116:        const opt = sel.querySelector('option[value="shirley_linear"]');
tests/test_browser_shirley_linear_delist.py:125:def test_fresh_page_cannot_newly_select_shirley_linear(browser, server):
tests/test_browser_shirley_linear_delist.py:136:def test_saved_file_with_shirley_linear_still_loads_renders_and_notes(browser, server):
tests/test_browser_shirley_linear_delist.py:146:            a.ui.bgType = 'shirley_linear'; a.ui.bgStart = '295'; a.ui.bgEnd = '283.1';
tests/test_browser_shirley_linear_delist.py:152:        assert p["value"] == "shirley_linear", p
tests/test_browser_shirley_linear_delist.py:169:            tabManager._getTab(aId).ui.bgType = 'shirley_linear';
tests/test_browser_shirley_linear_delist.py:172:        assert _probe(pg)["value"] == "shirley_linear"
tests/js/tougaard_twin.test.js:156:  const shirleyBackground = () => { throw new Error('unexpected route: shirley'); };
tests/js/tougaard_twin.test.js:157:  const smartBackground = () => { throw new Error('unexpected route: smart'); };
tests/js/tougaard_twin.test.js:159:  const shirleyLinearBackground = () => { throw new Error('unexpected route: shirley_linear'); };
acorn.LICENSE
acorn.js
module_state_scan.js

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const cp=require('\\''node:child_process'\\''); const orig=cp.execFileSync;
cp.execFileSync=(file,args,opts)=>orig(file,file.includes('\\''python'\\'')?['\\''-c'\\'','\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; runpy.run_path(sys.argv[1],run_name=\"__main__\")'\\'',...args]:args,opts);
require('\\''./tests/js/background_parity.test.js'\\'');'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\''),cp=require('\\''child_process'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
function extract(src,name){ const lines=src.split('\\''\\n'\\''); const start=lines.findIndex(l=>l.startsWith('\\''function '\\''+name+'\\''('\\'')); let d=0;for(let i=start;i<lines.length;i++){for(const c of lines[i]){if(c==='\\''{'\\'')d++; if(c==='\\''}'\\'')d--;}if(d===0)return lines.slice(start,i+1).join('\\''\\n'\\'');}}
const names=['\\''shirleyBackground'\\'','\\''smartBackground'\\'','\\''smartExperimentalBackground'\\'','\\''shirleyLinearBackground'\\'','\\''linearBackground'\\'','\\''tougaardBackground'\\'','\\''_applyEndpointAveraging'\\'','\\''_bgWindowIndices'\\'','\\''computeBackgroundCore'\\''];
const current=new Function(names.map(n=>extract(html,n)).join('\\''\\n'\\'')+'\\''; return {shirleyBackground,computeBackgroundCore};'\\'')();
const oldhtml=cp.execFileSync('\\''git'\\'',['\\''show'\\'','\\''895f323:templates/index.html'\\''],{encoding:'\\''utf8'\\'',stdio:['\\''pipe'\\'','\\''pipe'\\'','\\''ignore'\\'']});
const old=new Function(names.map(n=>extract(oldhtml,n)).join('\\''\\n'\\'')+'\\''; return {shirleyBackground,computeBackgroundCore};'\\'')();
const python='\\''/Users/skyefortier/xps-app/venv/bin/python3'\\'';
const bootstrap='\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; runpy.run_path(sys.argv[1],run_name=\"__main__\")'\\'';
function py(req){return JSON.parse(cp.execFileSync(python,['\\''-c'\\'',bootstrap,'\\''tests/js/background_parity_backend.py'\\''],{input:JSON.stringify(req),encoding:'\\''utf8'\\'',maxBuffer:64000000,env:{...process.env,PYTHONDONTWRITEBYTECODE:'\\''1'\\''}}));}

let seed=12;const rand=()=>{seed=(1664525*seed+1013904223)>>>0;return seed/2**32};
const items=[];
for(let k=0;k<500;k++){const n=3+Math.floor(rand()*6);const x=Array.from({length:n},(_,i)=>i);if(k%2){for(let i=1;i<n;i++)x[i]=x[i-1]+0.1+rand()*3}
const y=Array.from({length:n},()=>Math.floor(rand()*30));items.push({method:'\\''shirley'\\'',be:x,inten:y,n_avg:1});}
const expected=py({mode:'\\''bg'\\'',items});
let count=0;
for(let k=0;k<items.length;k++){const c=items[k],a=current.shirleyBackground(c.be,c.inten,200),b=expected[k],o=old.shirleyBackground(c.be,c.inten,200);const diff=v=>Math.max(...v.map((e,i)=>Math.abs(e-b[i])));if(diff(a)>0.01 &&count++<12)console.log(JSON.stringify({c,now:a,python:b,old:o,diff:diff(a),oldDiff:diff(o)}));}
console.log('\\''mismatch count'\\'',count);
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 1986ms:
/Users/skyefortier/.matplotlib is not a writable directory
{"c":{"method":"shirley","be":[0,0.7134628786239773,0.8197083729784935,2.4094027427025138,4.738371536228806],"inten":[29,21,13,2,0],"n_avg":1},"now":[29,3.7587993948206386,0,0,0],"python":[29,21.75,14.5,7.25,0],"old":[29,21.75,14.5,7.25,0],"diff":17.991200605179362,"oldDiff":0}
{"c":{"method":"shirley","be":[0,1,2,3,4,5,6,7],"inten":[29,14,7,1,11,15,11,2],"n_avg":1},"now":[29,29,29,29,29,22.157534246575338,8.657534246575342,2],"python":[29,29,29,29,29,29,15.5,2],"old":[29,25.142857142857142,21.285714285714285,17.428571428571427,13.571428571428571,9.714285714285714,5.857142857142857,2],"diff":6.842465753424662,"oldDiff":19.285714285714285}
{"c":{"method":"shirley","be":[0,1,2,3],"inten":[27,20,7,0],"n_avg":1},"now":[27,13.5,0,0],"python":[27,20.5,7,0],"old":[27,18,9,0],"diff":7,"oldDiff":2.5}
{"c":{"method":"shirley","be":[0,1.466769718239084,1.6402255478780718,3.513259302545339,4.3319507540203634,5.028421137249097,7.701268864469602,8.872624494880437],"inten":[29,27,24,3,1,23,9,8],"n_avg":1},"now":[29,10.220775323937048,8,8,8,8,8,8],"python":[29,29,29,29,29,28.505348840860094,13.66969017205733,8],"old":[29,26,23,20,17,14,11,8],"diff":21,"oldDiff":14.505348840860094}
{"c":{"method":"shirley","be":[0,2.6835121609270574,4.0713831894565375],"inten":[22,14,6],"n_avg":1},"now":[22,11.454150450386816,6],"python":[22,14,6],"old":[22,11.454150450386816,6],"diff":2.545849549613184,"oldDiff":2.545849549613184}
{"c":{"method":"shirley","be":[0,1.975491465209052,2.2148224809672685,4.982031344622374,7.624010777194053,8.747216070303693,9.345933313155546,10.472795212920754],"inten":[0,22,5,14,11,11,2,28],"n_avg":1},"now":[0,19.643763204812963,22.02360735191195,25.080984134304348,28,28,28,28],"python":[0,24.974354153068084,28,28,28,28,28,28],"old":[0,4,8,12,16,20,24,28],"diff":5.976392648088051,"oldDiff":20.974354153068084}
{"c":{"method":"shirley","be":[0,1,2,3,4,5,6,7],"inten":[28,15,0,1,5,20,18,8],"n_avg":1},"now":[28,28,28,28,28,23.31914893617021,13.319148936170212,8],"python":[28,28,28,28,28,28,18,8],"old":[28,25.142857142857142,22.285714285714285,19.428571428571427,16.57142857142857,13.714285714285714,10.857142857142858,8],"diff":4.680851063829792,"oldDiff":14.285714285714286}
{"c":{"method":"shirley","be":[0,1.0081379557028414,1.1470581461209806,3.5852178176399323],"inten":[19,13,7,6],"n_avg":1},"now":[19,7.57442975453603,6,6],"python":[19,14.666666666666668,10.333333333333334,6],"old":[19,14.666666666666666,10.333333333333332,6],"diff":7.0922369121306374,"oldDiff":1.7763568394002505e-15}
{"c":{"method":"shirley","be":[0,0.20475915134884418,3.2393620047252627],"inten":[5,7,24],"n_avg":1},"now":[5,6.200984598187258,24],"python":[5,14.5,24],"old":[5,6.200984598187258,24],"diff":8.299015401812742,"oldDiff":8.299015401812742}
{"c":{"method":"shirley","be":[0,1,2,3,4,5,6],"inten":[5,11,0,21,1,4,28],"n_avg":1},"now":[5,8.7375,12.475000000000001,20.2375,28,28,28],"python":[5,13.60123966942148,22.202479338842956,25.101239669421478,28,28,28],"old":[5,8.833333333333332,12.666666666666668,16.5,20.333333333333336,24.166666666666668,28],"diff":9.727479338842954,"oldDiff":9.535812672176288}
{"c":{"method":"shirley","be":[0,1,2,3,4],"inten":[1,9,15,9,21],"n_avg":1},"now":[1,5.2857142857142865,15.285714285714286,21,21],"python":[1,21,21,21,21],"old":[1,6,11,16,21],"diff":15.714285714285714,"oldDiff":15}
{"c":{"method":"shirley","be":[0,1,2,3,4],"inten":[28,13,16,3,2],"n_avg":1},"now":[28,28,15,2,2],"python":[28,28,21.5,8.5,2],"old":[28,21.5,15,8.5,2],"diff":6.5,"oldDiff":6.5}
mismatch count 14

 succeeded in 23133ms:
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
TAP version 13
# Subtest: the cases include the committed real U 4f scan, ascending and descending
ok 1 - the cases include the committed real U 4f scan, ascending and descending
  ---
  duration_ms: 1.408825
  type: 'test'
  ...
# Subtest: shirley, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
ok 2 - shirley, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 2600.518238
  type: 'test'
  ...
# Subtest: shirley, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
ok 3 - shirley, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 2030.695502
  type: 'test'
  ...
# Subtest: smart, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
ok 4 - smart, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1988.35167
  type: 'test'
  ...
# Subtest: smart, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
ok 5 - smart, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 2026.76111
  type: 'test'
  ...
# Subtest: smart_exp, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
ok 6 - smart_exp, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1668.805144
  type: 'test'
  ...
# Subtest: smart_exp, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
ok 7 - smart_exp, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1755.681845
  type: 'test'
  ...
# Subtest: tougaard, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
ok 8 - tougaard, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1858.249747
  type: 'test'
  ...
# Subtest: tougaard, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
ok 9 - tougaard, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1630.726481
  type: 'test'
  ...
# Subtest: linear, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
ok 10 - linear, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1621.995095
  type: 'test'
  ...
# Subtest: linear, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
ok 11 - linear, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1666.5164
  type: 'test'
  ...
# Subtest: KNOWN GAP (de-listed, not fixed): shirley_linear agrees on ascending grids and diverges on descending ones (Task 4 cause 3)
ok 12 - KNOWN GAP (de-listed, not fixed): shirley_linear agrees on ascending grids and diverges on descending ones (Task 4 cause 3)
  ---
  duration_ms: 1903.719148
  type: 'test'
  ...
1..12
# tests 12
# suites 0
# pass 12
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 20766.318625

exec
/bin/zsh -lc 'node --test tests/js/bg_window_indices.test.js tests/js/endpoint_avg_default.test.js tests/js/tougaard_twin.test.js tests/js/local_lm_descent.test.js tests/js/batch_propagation.test.js tests/js/roi_clamp_centre_warning.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 exited 1 in 6516ms:
# Subtest: source ROI overwrites a different target ROI during propagation
ok 1 - source ROI overwrites a different target ROI during propagation
  ---
  duration_ms: 1.618549
  type: 'test'
  ...
# Subtest: blank source ROI leaves the target ROI unchanged (never wipes it)
ok 2 - blank source ROI leaves the target ROI unchanged (never wipes it)
  ---
  duration_ms: 0.383226
  type: 'test'
  ...
# Subtest: a blank source ROI bound (one side) falls back per-field
ok 3 - a blank source ROI bound (one side) falls back per-field
  ---
  duration_ms: 0.313395
  type: 'test'
  ...
# Subtest: background fields still propagate from source (no regression)
ok 4 - background fields still propagate from source (no regression)
  ---
  duration_ms: 0.253895
  type: 'test'
  ...
# Subtest: blank source bgStart/bgEnd fall back to target (unchanged guard semantics)
ok 5 - blank source bgStart/bgEnd fall back to target (unchanged guard semantics)
  ---
  duration_ms: 0.453741
  type: 'test'
  ...
# Subtest: unrelated target UI fields are preserved untouched
ok 6 - unrelated target UI fields are preserved untouched
  ---
  duration_ms: 1.532263
  type: 'test'
  ...
# Subtest: legacy source without endpointAvg propagates 1, not the target default
ok 7 - legacy source without endpointAvg propagates 1, not the target default
  ---
  duration_ms: 1.250207
  type: 'test'
  ...
# Subtest: window at the ROI bounds covers every point, including the last one
ok 8 - window at the ROI bounds covers every point, including the last one
  ---
  duration_ms: 2.758612
  type: 'test'
  ...
# Subtest: off-grid bound inside the ROI never pulls in a point outside it
ok 9 - off-grid bound inside the ROI never pulls in a point outside it
  ---
  duration_ms: 0.260283
  type: 'test'
  ...
# Subtest: bound order does not matter
ok 10 - bound order does not matter
  ---
  duration_ms: 1.23295
  type: 'test'
  ...
# Subtest: ascending grid gives the same point set as descending
ok 11 - ascending grid gives the same point set as descending
  ---
  duration_ms: 0.275334
  type: 'test'
  ...
# Subtest: blank or NaN bound falls back to the full range
ok 12 - blank or NaN bound falls back to the full range
  ---
  duration_ms: 0.323477
  type: 'test'
  ...
# Subtest: fewer than two points in range falls back to the full range
ok 13 - fewer than two points in range falls back to the full range
  ---
  duration_ms: 0.322172
  type: 'test'
  ...
# Subtest: exactly two points in range is a usable window
ok 14 - exactly two points in range is a usable window
  ---
  duration_ms: 0.331512
  type: 'test'
  ...
# Subtest: computeBackgroundCore uses exactly the helper window
ok 15 - computeBackgroundCore uses exactly the helper window
  ---
  duration_ms: 1.2499
  type: 'test'
  ...
# Subtest: no request builder uses the old nearest-index idiom for the bg window
ok 16 - no request builder uses the old nearest-index idiom for the bg window
  ---
  duration_ms: 0.812783
  type: 'test'
  ...
# Subtest: both /api/fit request builders send the inclusive window as end_idx = i1 + 1
ok 17 - both /api/fit request builders send the inclusive window as end_idx = i1 + 1
  ---
  duration_ms: 1.514621
  type: 'test'
  ...
# Subtest: new tabs default to endpoint averaging 3, via one constant
ok 18 - new tabs default to endpoint averaging 3, via one constant
  ---
  duration_ms: 2.0879
  type: 'test'
  ...
# Subtest: legacy fallbacks resolve a saved ui without endpointAvg to 1
ok 19 - legacy fallbacks resolve a saved ui without endpointAvg to 1
  ---
  duration_ms: 0.968406
  type: 'test'
  ...
# Subtest: no bare endpointAvg || '1' fallback survives outside the constant
ok 20 - no bare endpointAvg || '1' fallback survives outside the constant
  ---
  duration_ms: 1.27872
  type: 'test'
  ...
# Subtest: Find Peaks records the averaging its engine used and applies it on apply
ok 21 - Find Peaks records the averaging its engine used and applies it on apply
  ---
  duration_ms: 0.803418
  type: 'test'
  ...
# Subtest: undo/redo carry the averaging recorded by the Find Peaks apply action
ok 22 - undo/redo carry the averaging recorded by the Find Peaks apply action
  ---
  duration_ms: 0.622731
  type: 'test'
  ...
# Subtest: averaging snapshots live on the tab record: undo/redo read the ACTIVE tab only
ok 23 - averaging snapshots live on the tab record: undo/redo read the ACTIVE tab only
  ---
  duration_ms: 0.401899
  type: 'test'
  ...
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/local_lm_server_parity_backend.py", line 12, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/fitting.py", line 35, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins']
# Subtest: A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
ok 24 - A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
  ---
  duration_ms: 1428.479912
  type: 'test'
  ...
# Subtest: A01 replay: the linked U 4f pair also descends
ok 25 - A01 replay: the linked U 4f pair also descends
  ---
  duration_ms: 273.130131
  type: 'test'
  ...
# Subtest: noiseless Gaussian: amplitude 10 started at 5 is recovered
ok 26 - noiseless Gaussian: amplitude 10 started at 5 is recovered
  ---
  duration_ms: 14.386218
  type: 'test'
  ...
# Subtest: acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
ok 27 - acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
  ---
  duration_ms: 10.001119
  type: 'test'
  ...
# Subtest: a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
ok 28 - a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
  ---
  duration_ms: 13.053868
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
ok 29 - bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
  ---
  duration_ms: 9.565923
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
ok 30 - bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
  ---
  duration_ms: 9.397731
  type: 'test'
  ...
# Subtest: a weak component the data DO hold is no longer forced up to an amplitude of 1
ok 31 - a weak component the data DO hold is no longer forced up to an amplitude of 1
  ---
  duration_ms: 9.646245
  type: 'test'
  ...
# Subtest: derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
ok 32 - derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
  ---
  duration_ms: 50.835407
  type: 'test'
  ...
# Subtest: derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
ok 33 - derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
  ---
  duration_ms: 25.25505
  type: 'test'
  ...
# Subtest: a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
ok 34 - a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
  ---
  duration_ms: 9.375304
  type: 'test'
  ...
# Subtest: linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
ok 35 - linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
  ---
  duration_ms: 13.285786
  type: 'test'
  ...
# Subtest: round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
ok 36 - round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
  ---
  duration_ms: 11.96461
  type: 'test'
  ...
# Subtest: round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
ok 37 - round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
  ---
  duration_ms: 10.28944
  type: 'test'
  ...
# Subtest: round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
ok 38 - round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
  ---
  duration_ms: 10.55563
  type: 'test'
  ...
# Subtest: A01 replay targets converge to constrained stationary points (C1s and U 4f)
ok 39 - A01 replay targets converge to constrained stationary points (C1s and U 4f)
  ---
  duration_ms: 1382.108752
  type: 'test'
  ...
# Subtest: round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
ok 40 - round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
  ---
  duration_ms: 58.668754
  type: 'test'
  ...
# Subtest: round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
ok 41 - round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
  ---
  duration_ms: 21.955246
  type: 'test'
  ...
# Subtest: round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
ok 42 - round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
  ---
  duration_ms: 17.411537
  type: 'test'
  ...
# Subtest: round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
ok 43 - round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
  ---
  duration_ms: 90.223412
  type: 'test'
  ...
# Subtest: round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
ok 44 - round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
  ---
  duration_ms: 1247.255347
  type: 'test'
  ...
# Subtest: round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
ok 45 - round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
  ---
  duration_ms: 29.082532
  type: 'test'
  ...
# Subtest: round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
ok 46 - round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
  ---
  duration_ms: 13.054231
  type: 'test'
  ...
# Subtest: weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
ok 47 - weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
  ---
  duration_ms: 11.909014
  type: 'test'
  ...
# Subtest: server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
not ok 48 - server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
  ---
  duration_ms: 1522.939985
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/local_lm_descent.test.js:455:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/local_lm_server_parity_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/local_lm_server_parity_backend.py", line 12, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/fitting.py", line 35, in <module>
        from lmfit import Model, Parameters
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/local_lm_descent.test.js:468:31)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom
ok 49 - the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom
  ---
  duration_ms: 20.231401
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
ok 50 - an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
  ---
  duration_ms: 20.126962
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
ok 51 - an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
  ---
  duration_ms: 20.497701
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
ok 52 - round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
  ---
  duration_ms: 8.933773
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
ok 53 - round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
  ---
  duration_ms: 10.299191
  type: 'test'
  ...
# Subtest: recovery from an amplitude of exactly zero (the new floor is not a trap)
ok 54 - recovery from an amplitude of exactly zero (the new floor is not a trap)
  ---
  duration_ms: 9.690272
  type: 'test'
  ...
# Subtest: the local engine refuses a model with no degrees of freedom; one more point and it fits
ok 55 - the local engine refuses a model with no degrees of freedom; one more point and it fits
  ---
  duration_ms: 25.283766
  type: 'test'
  ...
# Subtest: an ROI inside the data: no hint
ok 56 - an ROI inside the data: no hint
  ---
  duration_ms: 7.52486
  type: 'test'
  ...
# Subtest: an ROI past the data by more than one step: the quiet hint names the window actually used
ok 57 - an ROI past the data by more than one step: the quiet hint names the window actually used
  ---
  duration_ms: 3.303432
  type: 'test'
  ...
# Subtest: one side past the data is enough; the window named is the selected data
ok 58 - one side past the data is enough; the window named is the selected data
  ---
  duration_ms: 3.036363
  type: 'test'
  ...
# Subtest: a sub-step overshoot (a toFixed(1) rounding of the data edge) is not "past the data"
ok 59 - a sub-step overshoot (a toFixed(1) rounding of the data edge) is not "past the data"
  ---
  duration_ms: 4.275824
  type: 'test'
  ...
# Subtest: min above max: amber, no data selected (getROIData selects nothing)
ok 60 - min above max: amber, no data selected (getROIData selects nothing)
  ---
  duration_ms: 4.312268
  type: 'test'
  ...
# Subtest: an ROI that misses the data entirely: amber, names the data range
ok 61 - an ROI that misses the data entirely: amber, names the data range
  ---
  duration_ms: 2.096232
  type: 'test'
  ...
# Subtest: empty fields mean the full range (as getROIData): no hint
ok 62 - empty fields mean the full range (as getROIData): no hint
  ---
  duration_ms: 2.014712
  type: 'test'
  ...
# Subtest: the window is in the CORRECTED frame (raw − ccShift), as the fit and Find Peaks use it
ok 63 - the window is in the CORRECTED frame (raw − ccShift), as the fit and Find Peaks use it
  ---
  duration_ms: 4.294727
  type: 'test'
  ...
# Subtest: a descending acquisition behaves the same
ok 64 - a descending acquisition behaves the same
  ---
  duration_ms: 2.693728
  type: 'test'
  ...
# Subtest: centre outside the SELECTED data is flagged; inside, at the edges, or with no data selected is not
ok 65 - centre outside the SELECTED data is flagged; inside, at the edges, or with no data selected is not
  ---
  duration_ms: 4.017536
  type: 'test'
  ...
# Subtest: the helpers write nothing: no assignment to a field value, a peak or the fit state
ok 66 - the helpers write nothing: no assignment to a field value, a peak or the fit state
  ---
  duration_ms: 1.717159
  type: 'test'
  ...
# Subtest: the fit and Find Peaks still read the ROI exactly as before (getROIData / the two field values)
ok 67 - the fit and Find Peaks still read the ROI exactly as before (getROIData / the two field values)
  ---
  duration_ms: 1.355074
  type: 'test'
  ...
# Subtest: an unsupported component: the badge warns without reporting its suppressed centre
ok 68 - an unsupported component: the badge warns without reporting its suppressed centre
  ---
  duration_ms: 1.619964
  type: 'test'
  ...
# Subtest: manual fit and Find Peaks select the same points whenever no energy lies within 5e-5 eV of an ROI edge
ok 69 - manual fit and Find Peaks select the same points whenever no energy lies within 5e-5 eV of an ROI edge
  ---
  duration_ms: 7.162048
  type: 'test'
  ...
# Subtest: …and can differ by one edge point, IN EITHER DIRECTION, when an energy lies within 5e-5 eV of an edge (pre-existing, logged, not changed)
ok 70 - …and can differ by one edge point, IN EITHER DIRECTION, when an energy lies within 5e-5 eV of an edge (pre-existing, logged, not changed)
  ---
  duration_ms: 4.260292
  type: 'test'
  ...
# Subtest: loss-kernel response peaks ~23.4 eV above a delta-like peak
ok 71 - loss-kernel response peaks ~23.4 eV above a delta-like peak
  ---
  duration_ms: 21.187707
  type: 'test'
  ...
# Subtest: ascending and descending BE input give the identical background
ok 72 - ascending and descending BE input give the identical background
  ---
  duration_ms: 0.912694
  type: 'test'
  ...
# Subtest: background meets the data at BOTH edges (high-BE anchor, low-BE C0)
ok 73 - background meets the data at BOTH edges (high-BE anchor, low-BE C0)
  ---
  duration_ms: 0.564499
  type: 'test'
  ...
# Subtest: flat window yields no phantom signal (F1 regression pin)
ok 74 - flat window yields no phantom signal (F1 regression pin)
  ---
  duration_ms: 3.854202
  type: 'test'
  ...
# Subtest: agrees with the backend implementation (fitting.py) on the same spectrum
ok 75 - agrees with the backend implementation (fitting.py) on the same spectrum
  ---
  duration_ms: 2.927989
  type: 'test'
  ...
# Subtest: computeBackgroundCore applies endpoint averaging for tougaard (both branches)
ok 76 - computeBackgroundCore applies endpoint averaging for tougaard (both branches)
  ---
  duration_ms: 1.016914
  type: 'test'
  ...
1..76
# tests 76
# suites 0
# pass 75
# fail 1
# cancelled 0
# skipped 0
# todo 0
# duration_ms 6564.156381

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\''),cp=require('\\''child_process'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
function extract(src,name){ const lines=src.split('\\''\\n'\\''); const start=lines.findIndex(l=>l.startsWith('\\''function '\\''+name+'\\''('\\'')); let d=0;for(let i=start;i<lines.length;i++){for(const c of lines[i]){if(c==='\\''{'\\'')d++; if(c==='\\''}'\\'')d--;}if(d===0)return lines.slice(start,i+1).join('\\''\\n'\\'');}}
const names=['\\''shirleyBackground'\\'','\\''smartBackground'\\'','\\''smartExperimentalBackground'\\'','\\''shirleyLinearBackground'\\'','\\''linearBackground'\\'','\\''tougaardBackground'\\'','\\''_applyEndpointAveraging'\\'','\\''_bgWindowIndices'\\'','\\''computeBackgroundCore'\\''];
const current=new Function(names.map(n=>extract(html,n)).join('\\''\\n'\\'')+'\\''; return {shirleyBackground,computeBackgroundCore};'\\'')();
const oldhtml=cp.execFileSync('\\''git'\\'',['\\''show'\\'','\\''895f323:templates/index.html'\\''],{encoding:'\\''utf8'\\'',stdio:['\\''pipe'\\'','\\''pipe'\\'','\\''ignore'\\'']});
const old=new Function(names.map(n=>extract(oldhtml,n)).join('\\''\\n'\\'')+'\\''; return {shirleyBackground,computeBackgroundCore};'\\'')();
const python='\\''/Users/skyefortier/xps-app/venv/bin/python3'\\'';
const bootstrap='\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; runpy.run_path(sys.argv[1],run_name=\"__main__\")'\\'';
function py(req){return JSON.parse(cp.execFileSync(python,['\\''-c'\\'',bootstrap,'\\''tests/js/background_parity_backend.py'\\''],{input:JSON.stringify(req),encoding:'\\''utf8'\\'',maxBuffer:64000000,env:{...process.env,PYTHONDONTWRITEBYTECODE:'\\''1'\\''}}));}

const inputs=[
[[0,1,1.2,4],[19,13,7,6]],
[[0,1,2,5],[19,13,7,6]],
[[0,1,2,3],[27,20,7,0]],
[[0,1,2,3],[100,100,100,100]],
[[0,1],[10,20]],
[[0,1,2,3],[20,0,0,10]],
[[0,1,2,3],[10,20,30,40]]
];
const items=inputs.flatMap(([be,inten])=>['\\''shirley'\\'','\\''smart'\\''].map(method=>({method,be,inten,n_avg:1})));
const expected=py({mode:'\\''bg'\\'',items});
items.forEach((c,k)=>{const out={c,python:expected[k],old:old.computeBackgroundCore(c.be,c.inten,{bgType:c.method,shirleyIter:'\\''200'\\'',endpointAvg:'\\''1'\\''})};for(const iter of [5,199,200,201,2000])out[iter]=current.computeBackgroundCore(c.be,c.inten,{bgType:c.method,shirleyIter:String(iter),endpointAvg:'\\''1'\\''});console.log(JSON.stringify(out));});
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 1749ms:
/Users/skyefortier/.matplotlib is not a writable directory
{"5":[19,14.666666666666666,10.333333333333332,6],"199":[19,14.666666666666666,10.333333333333332,6],"200":[19,14.666666666666666,10.333333333333332,6],"201":[19,14.666666666666666,10.333333333333332,6],"2000":[19,14.666666666666666,10.333333333333332,6],"c":{"method":"shirley","be":[0,1,1.2,4],"inten":[19,13,7,6],"n_avg":1},"python":[19,14.666666666666668,10.333333333333334,6],"old":[19,14.666666666666666,10.333333333333332,6]}
{"5":[19,13,7,6],"199":[19,13,7,6],"200":[19,13,7,6],"201":[19,13,7,6],"2000":[19,13,7,6],"c":{"method":"smart","be":[0,1,1.2,4],"inten":[19,13,7,6],"n_avg":1},"python":[19,13,7,6],"old":[19,13,7,6]}
{"5":[19,14.666666666666666,10.333333333333332,6],"199":[19,14.666666666666666,10.333333333333332,6],"200":[19,14.666666666666666,10.333333333333332,6],"201":[19,14.666666666666666,10.333333333333332,6],"2000":[19,14.666666666666666,10.333333333333332,6],"c":{"method":"shirley","be":[0,1,2,5],"inten":[19,13,7,6],"n_avg":1},"python":[19,14.666666666666668,10.333333333333334,6],"old":[19,14.666666666666666,10.333333333333332,6]}
{"5":[19,13,7,6],"199":[19,13,7,6],"200":[19,13,7,6],"201":[19,13,7,6],"2000":[19,13,7,6],"c":{"method":"smart","be":[0,1,2,5],"inten":[19,13,7,6],"n_avg":1},"python":[19,13,7,6],"old":[19,13,7,6]}
{"5":[27,13.5,0,0],"199":[27,18,9,0],"200":[27,13.5,0,0],"201":[27,20.5,7,0],"2000":[27,13.5,0,0],"c":{"method":"shirley","be":[0,1,2,3],"inten":[27,20,7,0],"n_avg":1},"python":[27,20.5,7,0],"old":[27,18,9,0]}
{"5":[27,13.5,0,0],"199":[27,18,7,0],"200":[27,13.5,0,0],"201":[27,20,7,0],"2000":[27,13.5,0,0],"c":{"method":"smart","be":[0,1,2,3],"inten":[27,20,7,0],"n_avg":1},"python":[27,20,7,0],"old":[27,18,7,0]}
{"5":[100,100,100,100],"199":[100,100,100,100],"200":[100,100,100,100],"201":[100,100,100,100],"2000":[100,100,100,100],"c":{"method":"shirley","be":[0,1,2,3],"inten":[100,100,100,100],"n_avg":1},"python":[100,100,100,100],"old":[100,100,100,100]}
{"5":[100,100,100,100],"199":[100,100,100,100],"200":[100,100,100,100],"201":[100,100,100,100],"2000":[100,100,100,100],"c":{"method":"smart","be":[0,1,2,3],"inten":[100,100,100,100],"n_avg":1},"python":[100,100,100,100],"old":[100,100,100,100]}
{"5":[10,20],"199":[10,20],"200":[10,20],"201":[10,20],"2000":[10,20],"c":{"method":"shirley","be":[0,1],"inten":[10,20],"n_avg":1},"python":[10,20],"old":[10,20]}
{"5":[10,20],"199":[10,20],"200":[10,20],"201":[10,20],"2000":[10,20],"c":{"method":"smart","be":[0,1],"inten":[10,20],"n_avg":1},"python":[10,20],"old":[10,20]}
{"5":[20,16.666666666666664,13.333333333333332,10],"199":[20,16.666666666666664,13.333333333333332,10],"200":[20,16.666666666666664,13.333333333333332,10],"201":[20,16.666666666666664,13.333333333333332,10],"2000":[20,16.666666666666664,13.333333333333332,10],"c":{"method":"shirley","be":[0,1,2,3],"inten":[20,0,0,10],"n_avg":1},"python":[20,16.666666666666668,13.333333333333332,10],"old":[20,16.666666666666664,13.333333333333332,10]}
{"5":[20,0,0,10],"199":[20,0,0,10],"200":[20,0,0,10],"201":[20,0,0,10],"2000":[20,0,0,10],"c":{"method":"smart","be":[0,1,2,3],"inten":[20,0,0,10],"n_avg":1},"python":[20,0,0,10],"old":[20,0,0,10]}
{"5":[10,20,30,40],"199":[10,20,30,40],"200":[10,20,30,40],"201":[10,20,30,40],"2000":[10,20,30,40],"c":{"method":"shirley","be":[0,1,2,3],"inten":[10,20,30,40],"n_avg":1},"python":[10,20,30,40],"old":[10,20,30,40]}
{"5":[10,20,30,40],"199":[10,20,30,40],"200":[10,20,30,40],"201":[10,20,30,40],"2000":[10,20,30,40],"c":{"method":"smart","be":[0,1,2,3],"inten":[10,20,30,40],"n_avg":1},"python":[10,20,30,40],"old":[10,20,30,40]}

codex
The 12 parity tests pass with an in-memory workaround for the read-only sandbox’s Python import issue. But the adversarial cases found a regression: on some short, non-uniform spectra, the new clamp produces a background far from Python’s where the old JS agreed. I’m reducing that to a reproducible case and checking whether more iterations resolve it.
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e '
const cp=require('\\''node:child_process'\\''),fs=require('\\''fs'\\''),Module=require('\\''module'\\''),path=require('\\''path'\\''); const orig=cp.execFileSync;
const old=orig('\\''git'\\'',['\\''show'\\'','\\''895f323:templates/index.html'\\''],{encoding:'\\''utf8'\\'',stdio:['\\''pipe'\\'','\\''pipe'\\'','\\''ignore'\\'']});
cp.execFileSync=(file,args,opts)=>orig(file,file.includes('\\''python'\\'')?['\\''-c'\\'','\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; runpy.run_path(sys.argv[1],run_name=\"__main__\")'\\'',...args]:args,opts);
const filename=path.resolve('\\''tests/js/background_parity.test.js'\\''),m=new Module(filename,module);m.filename=filename;m.paths=module.paths;
m._compile(fs.readFileSync(filename,'\\''utf8'\\'').replace(\"const html = fs.readFileSync(path.join(REPO_ROOT, '\\''templates/index.html'\\''), '\\''utf8'\\'');\",'\\''const html = '\\''+JSON.stringify(old)+'\\'';'\\''),filename);
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 exited 1 in 21403ms:
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
TAP version 13
# Subtest: the cases include the committed real U 4f scan, ascending and descending
ok 1 - the cases include the committed real U 4f scan, ascending and descending
  ---
  duration_ms: 1.142718
  type: 'test'
  ...
# Subtest: shirley, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
not ok 2 - shirley, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 2294.456693
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity.test.js:77:5'
  failureType: 'testCodeFailure'
  error: 'synthetic C 1s, 101 pts, ascending: 3.56e-5 of the span'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity.test.js:78:53)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async startSubtestAfterBootstrap (node:internal/test_runner/harness:296:3)
  ...
# Subtest: shirley, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
not ok 3 - shirley, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1920.998864
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity.test.js:77:5'
  failureType: 'testCodeFailure'
  error: 'synthetic C 1s, 101 pts, ascending: 2.07e-4 of the span'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity.test.js:78:53)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: smart, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
not ok 4 - smart, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1884.121818
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity.test.js:77:5'
  failureType: 'testCodeFailure'
  error: 'synthetic C 1s, 101 pts, ascending: 3.56e-5 of the span'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity.test.js:78:53)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: smart, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
not ok 5 - smart, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 2052.979794
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity.test.js:77:5'
  failureType: 'testCodeFailure'
  error: 'synthetic C 1s, 101 pts, ascending: 7.17e-3 of the span'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/background_parity.test.js:78:53)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: smart_exp, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
ok 6 - smart_exp, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1706.209096
  type: 'test'
  ...
# Subtest: smart_exp, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
ok 7 - smart_exp, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1614.766428
  type: 'test'
  ...
# Subtest: tougaard, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
ok 8 - tougaard, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1576.232532
  type: 'test'
  ...
# Subtest: tougaard, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
ok 9 - tougaard, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1646.053525
  type: 'test'
  ...
# Subtest: linear, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
ok 10 - linear, endpoint average 1: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1618.070181
  type: 'test'
  ...
# Subtest: linear, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
ok 11 - linear, endpoint average 10: the page's background equals the server's within 0.000001 of the span on every case
  ---
  duration_ms: 1587.084847
  type: 'test'
  ...
# Subtest: KNOWN GAP (de-listed, not fixed): shirley_linear agrees on ascending grids and diverges on descending ones (Task 4 cause 3)
ok 12 - KNOWN GAP (de-listed, not fixed): shirley_linear agrees on ascending grids and diverges on descending ones (Task 4 cause 3)
  ---
  duration_ms: 1873.01196
  type: 'test'
  ...
1..12
# tests 12
# suites 0
# pass 8
# fail 4
# cancelled 0
# skipped 0
# todo 0
# duration_ms 19788.34052

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\''),cp=require('\\''child_process'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
function extract(src,name){ const lines=src.split('\\''\\n'\\''); const start=lines.findIndex(l=>l.startsWith('\\''function '\\''+name+'\\''('\\'')); let d=0;for(let i=start;i<lines.length;i++){for(const c of lines[i]){if(c==='\\''{'\\'')d++; if(c==='\\''}'\\'')d--;}if(d===0)return lines.slice(start,i+1).join('\\''\\n'\\'');}}
const names=['\\''shirleyBackground'\\'','\\''smartBackground'\\'','\\''smartExperimentalBackground'\\'','\\''shirleyLinearBackground'\\'','\\''linearBackground'\\'','\\''tougaardBackground'\\'','\\''_applyEndpointAveraging'\\'','\\''_bgWindowIndices'\\'','\\''computeBackgroundCore'\\''];
const current=new Function(names.map(n=>extract(html,n)).join('\\''\\n'\\'')+'\\''; return {shirleyBackground,computeBackgroundCore};'\\'')();
const oldhtml=cp.execFileSync('\\''git'\\'',['\\''show'\\'','\\''895f323:templates/index.html'\\''],{encoding:'\\''utf8'\\'',stdio:['\\''pipe'\\'','\\''pipe'\\'','\\''ignore'\\'']});
const old=new Function(names.map(n=>extract(oldhtml,n)).join('\\''\\n'\\'')+'\\''; return {shirleyBackground,computeBackgroundCore};'\\'')();
const python='\\''/Users/skyefortier/xps-app/venv/bin/python3'\\'';
const bootstrap='\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; runpy.run_path(sys.argv[1],run_name=\"__main__\")'\\'';
function py(req){return JSON.parse(cp.execFileSync(python,['\\''-c'\\'',bootstrap,'\\''tests/js/background_parity_backend.py'\\''],{input:JSON.stringify(req),encoding:'\\''utf8'\\'',maxBuffer:64000000,env:{...process.env,PYTHONDONTWRITEBYTECODE:'\\''1'\\''}}));}

const items=[];
for(const be of [[0,1,1.1,3.5],[0,1,1.1,4],[0,1,1.15,3.6],[0,1,2,3]]){
const y=be[2]===2?[27,20,7,0]:[19,13,7,6];
for(const offset of [0,100])for(const reverse of [false,true]){
let x=be.slice(),inten=y.map(v=>v+offset);if(reverse){x.reverse();inten.reverse()}
items.push({method:'\\''shirley'\\'',be:x,inten,n_avg:1});}}
const expected=py({mode:'\\''bg'\\'',items});
items.forEach((c,k)=>{const now=current.shirleyBackground(c.be,c.inten,200),oldbg=old.shirleyBackground(c.be,c.inten,200);
const d=Math.max(...now.map((v,i)=>Math.abs(v-expected[k][i])));
if(d>1e-5)console.log(JSON.stringify({c,python:expected[k],old:oldbg,now,iter5:current.shirleyBackground(c.be,c.inten,5),iter201:current.shirleyBackground(c.be,c.inten,201),iter2000:current.shirleyBackground(c.be,c.inten,2000)}));});
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const cp=require('\\''node:child_process'\\''); const orig=cp.execFileSync;
cp.execFileSync=(file,args,opts)=>orig(file,file.includes('\\''python'\\'')?['\\''-c'\\'','\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; runpy.run_path(sys.argv[1],run_name=\"__main__\")'\\'',...args]:args,opts);
require('\\''./tests/js/local_lm_descent.test.js'\\'');'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 1631ms:
/Users/skyefortier/.matplotlib is not a writable directory
{"c":{"method":"shirley","be":[0,1,1.1,3.5],"inten":[19,13,7,6],"n_avg":1},"python":[19,14.666666666666668,10.333333333333334,6],"old":[19,14.666666666666666,10.333333333333332,6],"now":[19,7.181818181818183,6,6],"iter5":[19,10.50153217568948,9.50561797752809,6],"iter201":[19,10.50153217568948,9.50561797752809,6],"iter2000":[19,7.181818181818183,6,6]}
{"c":{"method":"shirley","be":[3.5,1.1,1,0],"inten":[6,7,13,19],"n_avg":1},"python":[6,10.333333333333334,14.666666666666668,19],"old":[6,10.333333333333334,14.666666666666668,19],"now":[6,6,7.181818181818182,19],"iter5":[6,9.505617977528088,10.50153217568948,19],"iter201":[6,9.505617977528088,10.50153217568948,19],"iter2000":[6,6,7.181818181818182,19]}
{"c":{"method":"shirley","be":[0,1,1.15,3.6],"inten":[19,13,7,6],"n_avg":1},"python":[19,14.666666666666668,10.333333333333334,6],"old":[19,14.666666666666666,10.333333333333332,6],"now":[19,7.695652173913043,6,6],"iter5":[19,11.073963018490755,9.660919540229886,6],"iter201":[19,11.073963018490755,9.660919540229886,6],"iter2000":[19,7.695652173913043,6,6]}
{"c":{"method":"shirley","be":[3.6,1.15,1,0],"inten":[6,7,13,19],"n_avg":1},"python":[6,10.333333333333334,14.666666666666668,19],"old":[6,10.333333333333334,14.666666666666668,19],"now":[6,6,7.695652173913043,19],"iter5":[6,9.660919540229884,11.073963018490753,19],"iter201":[6,9.660919540229884,11.073963018490753,19],"iter2000":[6,6,7.695652173913043,19]}
{"c":{"method":"shirley","be":[0,1,2,3],"inten":[27,20,7,0],"n_avg":1},"python":[27,20.5,7,0],"old":[27,18,9,0],"now":[27,13.5,0,0],"iter5":[27,13.5,0,0],"iter201":[27,20.5,7,0],"iter2000":[27,13.5,0,0]}
{"c":{"method":"shirley","be":[3,2,1,0],"inten":[0,7,20,27],"n_avg":1},"python":[0,7,20.5,27],"old":[0,9,18,27],"now":[0,0,13.5,27],"iter5":[0,0,13.5,27],"iter201":[0,7,20.5,27],"iter2000":[0,0,13.5,27]}
{"c":{"method":"shirley","be":[0,1,2,3],"inten":[127,120,107,100],"n_avg":1},"python":[127,120.5,107,100],"old":[127,118,109,100],"now":[127,113.5,100,100],"iter5":[127,113.5,100,100],"iter201":[127,120.5,107,100],"iter2000":[127,113.5,100,100]}
{"c":{"method":"shirley","be":[3,2,1,0],"inten":[100,107,120,127],"n_avg":1},"python":[100,107,120.5,127],"old":[100,109,118,127],"now":[100,100,113.5,127],"iter5":[100,100,113.5,127],"iter201":[100,107,120.5,127],"iter2000":[100,100,113.5,127]}

 exited 1 in 2164ms:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "<frozen runpy>", line 286, in run_path
  File "<frozen runpy>", line 254, in _get_code_from_file
FileNotFoundError: [Errno 2] No such file or directory: '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/-c'
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "<frozen runpy>", line 286, in run_path
  File "<frozen runpy>", line 254, in _get_code_from_file
FileNotFoundError: [Errno 2] No such file or directory: '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/-c'
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "<frozen runpy>", line 286, in run_path
  File "<frozen runpy>", line 254, in _get_code_from_file
FileNotFoundError: [Errno 2] No such file or directory: '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/-c'
TAP version 13
# Subtest: A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
not ok 1 - A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
  ---
  duration_ms: 52.753623
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/local_lm_descent.test.js:101:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 -c import tempfile,runpy,sys; tempfile.tempdir="/tmp"; runpy.run_path(sys.argv[1],run_name="__main__") -c import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")])) /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip
    Traceback (most recent call last):
      File "<string>", line 1, in <module>
      File "<frozen runpy>", line 286, in run_path
      File "<frozen runpy>", line 254, in _get_code_from_file
    FileNotFoundError: [Errno 2] No such file or directory: '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/-c'
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    cp.execFileSync ([eval]:2:35)
    loadProjectTabs (/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/local_lm_descent.test.js:75:21)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/local_lm_descent.test.js:102:16)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.start (node:internal/test_runner/test:944:17)
  ...
# Subtest: A01 replay: the linked U 4f pair also descends
not ok 2 - A01 replay: the linked U 4f pair also descends
  ---
  duration_ms: 49.858547
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/local_lm_descent.test.js:117:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 -c import tempfile,runpy,sys; tempfile.tempdir="/tmp"; runpy.run_path(sys.argv[1],run_name="__main__") -c import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")])) /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip
    Traceback (most recent call last):
      File "<string>", line 1, in <module>
      File "<frozen runpy>", line 286, in run_path
      File "<frozen runpy>", line 254, in _get_code_from_file
    FileNotFoundError: [Errno 2] No such file or directory: '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/-c'
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    cp.execFileSync ([eval]:2:35)
    loadProjectTabs (/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/local_lm_descent.test.js:75:21)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/local_lm_descent.test.js:118:16)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: noiseless Gaussian: amplitude 10 started at 5 is recovered
ok 3 - noiseless Gaussian: amplitude 10 started at 5 is recovered
  ---
  duration_ms: 24.107708
  type: 'test'
  ...
# Subtest: acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
ok 4 - acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
  ---
  duration_ms: 12.558589
  type: 'test'
  ...
# Subtest: a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
ok 5 - a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
  ---
  duration_ms: 14.009253
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
ok 6 - bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
  ---
  duration_ms: 10.828307
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
ok 7 - bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
  ---
  duration_ms: 9.961135
  type: 'test'
  ...
# Subtest: a weak component the data DO hold is no longer forced up to an amplitude of 1
ok 8 - a weak component the data DO hold is no longer forced up to an amplitude of 1
  ---
  duration_ms: 9.337694
  type: 'test'
  ...
# Subtest: derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
ok 9 - derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
  ---
  duration_ms: 43.650905
  type: 'test'
  ...
# Subtest: derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
ok 10 - derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
  ---
  duration_ms: 28.872232
  type: 'test'
  ...
# Subtest: a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
ok 11 - a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
  ---
  duration_ms: 8.961981
  type: 'test'
  ...
# Subtest: linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
ok 12 - linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
  ---
  duration_ms: 12.920441
  type: 'test'
  ...
# Subtest: round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
ok 13 - round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
  ---
  duration_ms: 12.745795
  type: 'test'
  ...
# Subtest: round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
ok 14 - round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
  ---
  duration_ms: 9.882538
  type: 'test'
  ...
# Subtest: round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
ok 15 - round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
  ---
  duration_ms: 10.965873
  type: 'test'
  ...
# Subtest: A01 replay targets converge to constrained stationary points (C1s and U 4f)
not ok 16 - A01 replay targets converge to constrained stationary points (C1s and U 4f)
  ---
  duration_ms: 61.463011
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/local_lm_descent.test.js:341:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 -c import tempfile,runpy,sys; tempfile.tempdir="/tmp"; runpy.run_path(sys.argv[1],run_name="__main__") -c import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")])) /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip
    Traceback (most recent call last):
      File "<string>", line 1, in <module>
      File "<frozen runpy>", line 286, in run_path
      File "<frozen runpy>", line 254, in _get_code_from_file
    FileNotFoundError: [Errno 2] No such file or directory: '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/-c'
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    cp.execFileSync ([eval]:2:35)
    loadProjectTabs (/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/local_lm_descent.test.js:75:21)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/local_lm_descent.test.js:342:16)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
ok 17 - round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
  ---
  duration_ms: 140.805514
  type: 'test'
  ...
# Subtest: round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
ok 18 - round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
  ---
  duration_ms: 28.348898
  type: 'test'
  ...
# Subtest: round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
ok 19 - round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
  ---
  duration_ms: 18.387682
  type: 'test'
  ...
# Subtest: round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
ok 20 - round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
  ---
  duration_ms: 83.944223
  type: 'test'
  ...
# Subtest: round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
ok 21 - round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
  ---
  duration_ms: 1305.458357
  type: 'test'
  ...
# Subtest: round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
ok 22 - round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
  ---
  duration_ms: 27.571002
  type: 'test'
  ...
# Subtest: round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
ok 23 - round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
  ---
  duration_ms: 11.702476
  type: 'test'
  ...
# Subtest: weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
ok 24 - weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
  ---
  duration_ms: 9.701826
  type: 'test'
  ...
# Subtest: server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
not ok 25 - server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
  ---
  duration_ms: 55.486051
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/local_lm_descent.test.js:455:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 -c import tempfile,runpy,sys; tempfile.tempdir="/tmp"; runpy.run_path(sys.argv[1],run_name="__main__") -c import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")])) /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip
    Traceback (most recent call last):
      File "<string>", line 1, in <module>
      File "<frozen runpy>", line 286, in run_path
      File "<frozen runpy>", line 254, in _get_code_from_file
    FileNotFoundError: [Errno 2] No such file or directory: '/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/-c'
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    cp.execFileSync ([eval]:2:35)
    loadProjectTabs (/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/local_lm_descent.test.js:75:21)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/tests/js/local_lm_descent.test.js:456:16)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom
ok 26 - the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom
  ---
  duration_ms: 21.172341
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
ok 27 - an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
  ---
  duration_ms: 25.85028
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
ok 28 - an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
  ---
  duration_ms: 22.884607
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
ok 29 - round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
  ---
  duration_ms: 10.484302
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
ok 30 - round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
  ---
  duration_ms: 11.068444
  type: 'test'
  ...
# Subtest: recovery from an amplitude of exactly zero (the new floor is not a trap)
ok 31 - recovery from an amplitude of exactly zero (the new floor is not a trap)
  ---
  duration_ms: 11.835332
  type: 'test'
  ...
# Subtest: the local engine refuses a model with no degrees of freedom; one more point and it fits
ok 32 - the local engine refuses a model with no degrees of freedom; one more point and it fits
  ---
  duration_ms: 34.253207
  type: 'test'
  ...
1..32
# tests 32
# suites 0
# pass 28
# fail 4
# cancelled 0
# skipped 0
# todo 0
# duration_ms 2219.973306

exec
/bin/zsh -lc "sed -n '1,95p' tests/js/local_lm_descent.test.js; sed -n '9235,9355p' templates/index.html; sed -n '11795,11865p' templates/index.html; rg -n 'bgIntensity|background\\]' tests/test* | head -45; git diff --check 895f323..HEAD" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
// Local Levenberg–Marquardt: it must DESCEND and it must never present a
// non-converged attempt as a result (unit A0, 2026-09-15).
//
// Background: from the initial commit (f20d71b) until this unit, runFitLocal
// solved JᵀJ·dp = +Jᵀr with r = data − model, so every step was an ascent
// step, no step was ever accepted, and after 24 rejections λ passed 1e8 and
// the loop exited with the STARTING parameters, announced as "Fit complete
// (local LM)". Every Batch Fit called that path. The empirical proof is in
// docs/superpowers/plans/2026-09-15-a01-local-lm-proof.md; this file is
// that proof turned into a regression test on the SHIPPED functions.
//
// Everything under test is extracted verbatim from templates/index.html by
// function name (brace-matched) — the same functions the browser runs.

const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

const REPO_ROOT = path.join(__dirname, '../..');
const html = fs.readFileSync(path.join(REPO_ROOT, 'templates/index.html'), 'utf8');
const lines = html.split('\n');

function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name.replace(/\$/g, '\\$') + '\\(');
  const start = lines.findIndex(l => re.test(l));
  assert.ok(start >= 0, `function ${name} not found in templates/index.html`);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail(`unbalanced braces extracting ${name}`);
}

const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', '_laKernelHalf', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
  'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
  'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
  'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
  '_computeRFactor', '_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel', '_governingProvenance', '_localFitCaveat', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay', '_updateLocalModelBanner',
  '_componentSupportCore', '_supportRootOf', '_applySupportVerdicts', '_fitKeyCanon', '_sameFitKey', '_statsState', '_statsLiveState'];
const CAVEAT_CONST = (html.match(/^const (_LOCAL_FIT_CAVEAT\w*|_STATS_\w+_NOTE) = .*$/mg) || []).join('\n');

// One isolated environment per test: a fresh `state`, a stub DOM, and the
// extracted functions bound to them.
function makeEnv() {
  const dom = {};
  const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, setAttribute() {}, removeAttribute() {},
    classList: { add() {}, remove() {}, contains: () => false } });
  const document = { getElementById: el, querySelectorAll: () => [] };
  const state = { peaks: [], fitResult: null, rawBE: [], rawIntensity: [], ccShift: 0 };
  const calls = { notify: [] };
  const notify = (msg, kind) => calls.notify.push({ msg, kind });
  const noop = () => {};
  const src = CAVEAT_CONST + '\nconst _SUPPORT_MIN_F = 10; const _startsLiveKey = () => "KEY";\n' + NAMES.map(extractFn).join('\n\n');
  const factory = new Function('document', 'state', 'notify', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_activeTab', '_escHtml', '_historyPreview', 'tabManager', '_updateRFactorUI', '_updateROIDisplay',
    'renderPeakList', 'updatePlot', 'renderResults', '_hideFitSpinner', '_autoSnapshot', 'manualAnchorBackground',
    src + '\nreturn { runFitLocal, computeBackgroundCore, evalAllPeaks, evalPeakArray, gaussian };');
  const fns = factory(document, state, notify, '', '', () => null, x => String(x), null, null, noop, noop, noop, noop, noop, noop, noop,
    be => new Array(be.length).fill(0));
  return { ...fns, state, dom, calls };
}

// ── Committed lab project, replayed exactly as runPropagation does ──────────
const PROJECT = path.join(REPO_ROOT, 'docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip');
const BatchPropagation = require(path.join(REPO_ROOT, 'static/js/batch_propagation.js'));

function loadProjectTabs() {
  const py = fs.existsSync(path.join(REPO_ROOT, 'venv/bin/python3')) ? path.join(REPO_ROOT, 'venv/bin/python3')
    : (fs.existsSync('/Users/skyefortier/xps-app/venv/bin/python3') ? '/Users/skyefortier/xps-app/venv/bin/python3' : 'python3');
  const script = 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; ' +
    'print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))';
  return JSON.parse(execFileSync(py, ['-c', script, REPO_ROOT, PROJECT], { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }));
}

function batchTarget(env, tabs, sourceName, targetName) {
  const src = tabs.find(t => t.name === sourceName), tgt = tabs.find(t => t.name === targetName);
  assert.ok(src && tgt, 'source/target tabs present in committed project');
  const scale = Math.max(...tgt.rawIntensity) / Math.max(...src.rawIntensity);
  const cloned = JSON.parse(JSON.stringify(src.peaks)).map(p => ({ ...p, amplitude: p.linked ? p.amplitude : p.amplitude * scale }));
  const ui = BatchPropagation.propagateFitUi({ ...src.ui }, { ...tgt.ui });
  const roiMin = parseFloat(ui.roiMin), roiMax = parseFloat(ui.roiMax);
  const be = [], inten = [];
  tgt.rawBE.forEach((b, i) => { const c = b - (src.ccShift || 0); if (c >= roiMin && c <= roiMax) { be.push(c); inten.push(tgt.rawIntensity[i]); } });
  const bg = env.computeBackgroundCore(be, inten, ui);
  const bgSub = inten.map((v, i) => v - bg[i]);
  env.state.peaks = cloned;
  env.state.fitResult = null;
  return { be, bgSub, bg, initial: JSON.parse(JSON.stringify(cloned)) };
}

// The objective the local engine minimises since unit W1: the Poisson-weighted
// sum of squares, w = 1/sqrt(max(raw counts, 1)), raw = bgSub + bg.
  const src = tabManager._getTab(entry.sourceTabId);
  return !!(src && src.fitResult && Array.isArray(src.peaks) && src.peaks.length > 0);
}

function _colorWithAlpha(hex, a) {
  if (!/^#[0-9a-fA-F]{6}$/.test(hex)) return hex;
  const alphaHex = Math.round(a * 255).toString(16).padStart(2, '0');
  return hex + alphaHex;
}

// Reproduce a source tab's background using its persisted ui state.
// Falls back to shirley for manual-anchor sources (see follow-up:
// "Stack view of post-load fits: support manual-anchor background
// reconstruction from persisted anchor points").
function _computeBackgroundForSource(be, inten, srcUi) {
  if (!be || !be.length || !inten || !inten.length) {
    return new Array(be ? be.length : 0).fill(0);
  }
  let settings = {
    bgType:      (srcUi && srcUi.bgType)      || 'shirley',
    shirleyIter: (srcUi && srcUi.shirleyIter) || '5',
    endpointAvg: (srcUi && srcUi.endpointAvg) || LEGACY_ENDPOINT_AVG,
    bgStart:     (srcUi && srcUi.bgStart)     || '',
    bgEnd:       (srcUi && srcUi.bgEnd)       || '',
  };
  if (settings.bgType === 'manual') settings = { ...settings, bgType: 'shirley' };
  return computeBackgroundCore(be, inten, settings);
}

// Build all render data for one entry's fit visualization:
//   { be, bg, fittedY, peaks: [{peak, y}] }
// `be` is corrected-BE space; `bg` is raw-level background curve;
// `fittedY` is the raw-level envelope; each peak's `y` is the raw-level
// peak shape (peak height + bg).
//
// Three internal paths, chosen by what the source tab has available:
//   A:  fitResult.be + fitResult.fittedY both present, lengths match
//       → use fittedY directly (already raw-level). Frozen to fit-time
//         ccShift, matching single-tab behavior.
//   A2: fitResult.be + fitResult.bgIntensity present, no fittedY (local
//       LM fit) → fittedY = evalAllPeaks(be, peaks) + bg.
//   B:  post-load, neither fr.be nor fr.bgIntensity present → derive be
//       by ROI-filtering corrBE using src.ui.roiMin/roiMax, recompute
//       bg via _computeBackgroundForSource(be, inten, src.ui).
//       Live ccShift (deliberate asymmetry vs A/A2).
//
// Returns empty arrays if source isn't available or has no fit.
// Align src.rawIntensity to a fit-time `be` array (Path A/A2). fr.be is
// a contiguous slice of corrBE at fit time; if ccShift hasn't drifted,
// we can find the matching window in current rawBE by locating the
// index where (rawBE - shift) is closest to be[0]. Returns rawIntensity
// slice of length matching `be` (or shorter if data runs out).
function _alignRawToFitBe(src, be) {
  if (!Array.isArray(src.rawBE) || !Array.isArray(src.rawIntensity)
      || src.rawBE.length === 0 || !be || be.length === 0) return [];
  const shift = src.ccShift || 0;
  const target = be[0];
  let i0 = 0;
  let minDiff = Math.abs((src.rawBE[0] - shift) - target);
  for (let i = 1; i < src.rawBE.length; i++) {
    const d = Math.abs((src.rawBE[i] - shift) - target);
    if (d < minDiff) { minDiff = d; i0 = i; }
    else if (i0 > 0) break;  // rawBE is monotonic; past the closest match.
  }
  const len = Math.min(be.length, src.rawBE.length - i0);
  return src.rawIntensity.slice(i0, i0 + len);
}

function _buildEntryRenderData(entry) {
  const src = tabManager._getTab(entry.sourceTabId);
  if (!src || !Array.isArray(src.rawBE) || src.rawBE.length < 2) {
    return { be: [], bg: [], rawY: [], fittedY: [], peaks: [] };
  }
  const peaks = Array.isArray(src.peaks) ? src.peaks : [];
  const fr = src.fitResult;
  if (!fr || peaks.length === 0) {
    return { be: [], bg: [], rawY: [], fittedY: [], peaks: [] };
  }
  const shift = src.ccShift || 0;

  // be + bg + rawY
  let be, bg, rawY;
  if (Array.isArray(fr.be) && fr.be.length >= 2
      && Array.isArray(fr.bgIntensity)
      && fr.bgIntensity.length === fr.be.length) {
    // Path A/A2: fit-time be + bg both present (frozen).
    be = fr.be.slice();
    bg = fr.bgIntensity.slice();
    rawY = _alignRawToFitBe(src, be);
  } else {
    // Path B: post-load — derive ROI-window be from rawBE + ui.roiMin/Max,
    // recompute bg from raw via source's persisted bg settings.
    const corrBE = src.rawBE.map(b => b - shift);
    const roiMinV = parseFloat(src.ui && src.ui.roiMin);
    const roiMaxV = parseFloat(src.ui && src.ui.roiMax);
    let i0 = 0, i1 = corrBE.length - 1;
    if (isFinite(roiMinV) && isFinite(roiMaxV)) {
      const lo = Math.min(roiMinV, roiMaxV);
      const hi = Math.max(roiMinV, roiMaxV);
      // corrBE is descending (highest BE first); locate ROI bounds.
      while (i0 < corrBE.length && corrBE[i0] > hi) i0++;
      while (i1 >= 0 && corrBE[i1] < lo) i1--;
      if (i1 < i0) { i0 = 0; i1 = corrBE.length - 1; }
    }
    be = corrBE.slice(i0, i1 + 1);
    rawY = src.rawIntensity.slice(i0, i1 + 1);
    bg = _computeBackgroundForSource(be, rawY, src.ui);
  }

  // Envelope (raw-level)
  let fittedY;
  if (Array.isArray(fr.fittedY) && fr.fittedY.length === be.length && _statsRecordState(src) !== 'stale') {
    // Path A: backend fittedY directly (already raw-level). Never a stale
    // result's curve (F1: judged against the SOURCE record's key).
    fittedY = fr.fittedY.slice();
  } else {
    // Path A2/B: compose envelope from peaks + bg.
    const model = evalAllPeaks(be, peaks);
    fittedY = model.map((v, i) => v + bg[i]);
  }

  for (let i = 1; i < n - 1; i++) {
    const dx = be[i+1] - be[i-1];
    if (Math.abs(dx) > 1e-10) d[i] = (intensity[i+1] - intensity[i-1]) / dx;
  }
  d[0] = d[1]; d[n-1] = d[n-2];
  return d;
}

// ═══════════════════════════════════════════════════
// RUNS TEST — residual randomness diagnostic
// ═══════════════════════════════════════════════════
// R-FACTOR (reliability factor)
// R = Σ|residual| / Σ|data| × 100%
// ═══════════════════════════════════════════════════
function _computeRFactor(fitResult) {
  if (!fitResult || !fitResult.be) return null;
  const be = fitResult.be;
  const bgSub = fitResult.bgSubtracted;
  if (!bgSub || bgSub.length !== be.length) return null;
  let residuals;
  if (fitResult.fittedY && fitResult.fittedY.length === be.length) {
    const bgI = fitResult.bgIntensity;
    if (bgI && bgI.length === be.length) {
      residuals = bgSub.map((v, i) => (v + bgI[i]) - fitResult.fittedY[i]);
    } else {
      residuals = bgSub.map((v, i) => v - (fitResult.fittedY[i] - (bgI ? bgI[i] : 0)));
    }
  } else {
    const modelY = evalAllPeaks(be, state.peaks);
    residuals = bgSub.map((v, i) => v - modelY[i]);
  }
  const sumAbsResid = residuals.reduce((s, v) => s + Math.abs(v), 0);
  const sumAbsData = bgSub.reduce((s, v) => s + Math.abs(v), 0);
  if (sumAbsData === 0) return null;
  const rPct = (sumAbsResid / sumAbsData) * 100;
  let level;
  if (rPct < 5) level = 'good';
  else if (rPct <= 10) level = 'amber';
  else level = 'red';
  return { rPct, level };
}

const _RFACTOR_TOOLTIP = "The R-factor (reliability factor) measures the overall agreement between the fit and the data as a percentage. Computed within the ROI range.\n\nR = \u03a3|residual| / \u03a3|data| \u00d7 100%\n\n\u2022 R < 5% = excellent fit\n\u2022 R = 5\u201310% = acceptable fit, check residuals visually\n\u2022 R > 10% = poor fit, the model is likely incomplete\n\nUnlike chi-squared, the R-factor is intuitive \u2014 it represents the fraction of the total signal that is unexplained by the model.";

function _renderRFactorPanel(rf) {
  if (!rf) return '';
  const pct = rf.rPct.toFixed(1);
  const color = rf.level === 'good' ? 'var(--green)' : rf.level === 'amber' ? 'var(--amber)' : 'var(--red)';
  const label = rf.level === 'good' ? 'Excellent fit' : rf.level === 'amber' ? 'Acceptable \u2014 check residuals' : 'Poor fit \u2014 model likely incomplete';
  return `<div data-xps-tip="${_RFACTOR_TOOLTIP.replace(/"/g, '&quot;')}" style="background:var(--bg3);border:1px solid ${color};border-radius:var(--radius);padding:8px 10px;margin-bottom:12px;font-size:11px;color:${color};cursor:help">
    R-factor: <span style="font-family:var(--mono)">${pct}%</span> \u2014 ${label}
  </div>`;
}

function _updateRFactorUI(rf) {
  const el = document.getElementById('sb-runs');
  if (!el) return;
  if (rf && state.fitResult && rf === state.fitResult.rFactor && _statsLiveState() === 'stale') {
    // F1: the previous model's R-factor is not shown beside the edited model
    el.style.color = 'var(--text3)';
    el.textContent = 'R: \u2014';
    el.setAttribute('data-xps-tip', _STATS_STALE_NOTE);
    return;
  }
  if (!rf) {
    el.textContent = '';
    el.removeAttribute('data-xps-tip');
    return;
  }
  const pct = rf.rPct.toFixed(1);
  el.style.color = rf.level === 'good' ? 'var(--green)' : rf.level === 'amber' ? 'var(--amber)' : 'var(--red)';
tests/test_browser_find_peaks_full_window.py:13:``be``/``bgIntensity`` arrays once ANY fit exists (a prior manual Run
tests/test_browser_find_peaks_full_window.py:150:            be: narrowBE, bgIntensity: narrowBG, bgSubtracted: narrowSub,
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-jJjibYOo' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-1fLjf4mE' (errno=Operation not permitted)

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\''),cp=require('\\''child_process'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
function extract(src,name){ const lines=src.split('\\''\\n'\\''); const start=lines.findIndex(l=>l.startsWith('\\''function '\\''+name+'\\''('\\'')); let d=0;for(let i=start;i<lines.length;i++){for(const c of lines[i]){if(c==='\\''{'\\'')d++; if(c==='\\''}'\\'')d--;}if(d===0)return lines.slice(start,i+1).join('\\''\\n'\\'');}}
const names=['\\''shirleyBackground'\\'','\\''smartBackground'\\'','\\''smartExperimentalBackground'\\'','\\''shirleyLinearBackground'\\'','\\''linearBackground'\\'','\\''tougaardBackground'\\'','\\''_applyEndpointAveraging'\\'','\\''_bgWindowIndices'\\'','\\''computeBackgroundCore'\\''];
const current=new Function(names.map(n=>extract(html,n)).join('\\''\\n'\\'')+'\\''; return {shirleyBackground,computeBackgroundCore};'\\'')();
const oldhtml=cp.execFileSync('\\''git'\\'',['\\''show'\\'','\\''895f323:templates/index.html'\\''],{encoding:'\\''utf8'\\'',stdio:['\\''pipe'\\'','\\''pipe'\\'','\\''ignore'\\'']});
const old=new Function(names.map(n=>extract(oldhtml,n)).join('\\''\\n'\\'')+'\\''; return {shirleyBackground,computeBackgroundCore};'\\'')();
const python='\\''/Users/skyefortier/xps-app/venv/bin/python3'\\'';
const bootstrap='\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; runpy.run_path(sys.argv[1],run_name=\"__main__\")'\\'';
function py(req){return JSON.parse(cp.execFileSync(python,['\\''-c'\\'',bootstrap,'\\''tests/js/background_parity_backend.py'\\''],{input:JSON.stringify(req),encoding:'\\''utf8'\\'',maxBuffer:64000000,env:{...process.env,PYTHONDONTWRITEBYTECODE:'\\''1'\\''}}));}

const cases=py({mode:'\\''cases'\\''}),items=[];
for(const method of ['\\''shirley'\\'','\\''smart'\\''])for(const n_avg of [1,10])for(const c of cases)items.push({method,n_avg,be:c.be,inten:c.inten});
const expected=py({mode:'\\''bg'\\'',items});let k=0;
for(const method of ['\\''shirley'\\'','\\''smart'\\''])for(const avg of [1,10]){const rows={method,avg};for(const iter of [5,200])for(const [name,impl] of [['\\''old'\\'',old],['\\''new'\\'',current]]){let max=0;for(let c=0;c<cases.length;c++){const it=items[k+c],out=impl.computeBackgroundCore(it.be,it.inten,{bgType:method,endpointAvg:String(avg),shirleyIter:String(iter)}),span=Math.max(...it.inten)-Math.min(...it.inten);max=Math.max(max,Math.max(...out.map((v,i)=>Math.abs(v-expected[k+c][i])))/span*100);}rows[name+iter]=max;}console.log(rows);k+=cases.length;}
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const cp=require('\\''node:child_process'\\''); const orig=cp.execFileSync;
cp.execFileSync=(file,args,opts)=>{if(file.includes('\\''python'\\'')){args=args[0]==='\\''-c'\\''?['\\''-c'\\'','\\''import tempfile; tempfile.tempdir=\"/tmp\"; '\\''+args[1],...args.slice(2)]:['\\''-c'\\'','\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; runpy.run_path(sys.argv[1],run_name=\"__main__\")'\\'',...args];}return orig(file,args,opts);};
require('\\''./tests/js/local_lm_descent.test.js'\\'');'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 6791ms:
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
{
  method: 'shirley',
  avg: 1,
  old5: 0.04694991270274284,
  new5: 0.01574944167578243,
  old200: 0.04719173553936161,
  new200: 7.559628125769223e-10
}
{
  method: 'shirley',
  avg: 10,
  old5: 0.07525126701151033,
  new5: 0.018921607034407893,
  old200: 0.07779927310951426,
  new200: 8.882704523414394e-10
}
{
  method: 'smart',
  avg: 1,
  old5: 0.04694991270274284,
  new5: 0.01574944167578243,
  old200: 0.04719173553936161,
  new200: 7.559628125769223e-10
}
{
  method: 'smart',
  avg: 10,
  old5: 1.1886579823029009,
  new5: 0.018921607034407893,
  old200: 1.1886579823029009,
  new200: 8.882704523414394e-10
}

codex
The reduced case keeps cycling even at 2,000 iterations, so it is distinct from the accepted five-iteration convergence gap. Replaying the suite against `895f323` also confirms that exactly the four Shirley/smart tests fail. The regression test is useful, but its current spectra miss this failure mode.
 succeeded in 9149ms:
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
TAP version 13
# Subtest: A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
ok 1 - A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
  ---
  duration_ms: 1572.630119
  type: 'test'
  ...
# Subtest: A01 replay: the linked U 4f pair also descends
ok 2 - A01 replay: the linked U 4f pair also descends
  ---
  duration_ms: 282.318816
  type: 'test'
  ...
# Subtest: noiseless Gaussian: amplitude 10 started at 5 is recovered
ok 3 - noiseless Gaussian: amplitude 10 started at 5 is recovered
  ---
  duration_ms: 13.945503
  type: 'test'
  ...
# Subtest: acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
ok 4 - acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
  ---
  duration_ms: 9.786435
  type: 'test'
  ...
# Subtest: a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
ok 5 - a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
  ---
  duration_ms: 12.762958
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
ok 6 - bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
  ---
  duration_ms: 9.704467
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
ok 7 - bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
  ---
  duration_ms: 9.036859
  type: 'test'
  ...
# Subtest: a weak component the data DO hold is no longer forced up to an amplitude of 1
ok 8 - a weak component the data DO hold is no longer forced up to an amplitude of 1
  ---
  duration_ms: 9.514537
  type: 'test'
  ...
# Subtest: derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
ok 9 - derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
  ---
  duration_ms: 43.527896
  type: 'test'
  ...
# Subtest: derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
ok 10 - derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
  ---
  duration_ms: 25.92329
  type: 'test'
  ...
# Subtest: a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
ok 11 - a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
  ---
  duration_ms: 8.515305
  type: 'test'
  ...
# Subtest: linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
ok 12 - linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
  ---
  duration_ms: 13.057602
  type: 'test'
  ...
# Subtest: round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
ok 13 - round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
  ---
  duration_ms: 12.38443
  type: 'test'
  ...
# Subtest: round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
ok 14 - round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
  ---
  duration_ms: 9.941414
  type: 'test'
  ...
# Subtest: round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
ok 15 - round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
  ---
  duration_ms: 11.696362
  type: 'test'
  ...
# Subtest: A01 replay targets converge to constrained stationary points (C1s and U 4f)
ok 16 - A01 replay targets converge to constrained stationary points (C1s and U 4f)
  ---
  duration_ms: 1500.550192
  type: 'test'
  ...
# Subtest: round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
ok 17 - round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
  ---
  duration_ms: 60.615347
  type: 'test'
  ...
# Subtest: round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
ok 18 - round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
  ---
  duration_ms: 21.638038
  type: 'test'
  ...
# Subtest: round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
ok 19 - round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
  ---
  duration_ms: 12.116567
  type: 'test'
  ...
# Subtest: round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
ok 20 - round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
  ---
  duration_ms: 86.057727
  type: 'test'
  ...
# Subtest: round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
ok 21 - round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
  ---
  duration_ms: 1282.197781
  type: 'test'
  ...
# Subtest: round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
ok 22 - round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
  ---
  duration_ms: 21.872466
  type: 'test'
  ...
# Subtest: round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
ok 23 - round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
  ---
  duration_ms: 12.120813
  type: 'test'
  ...
# Subtest: weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
ok 24 - weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
  ---
  duration_ms: 9.402845
  type: 'test'
  ...
# Subtest: server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
ok 25 - server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
  ---
  duration_ms: 4005.00422
  type: 'test'
  ...
# Subtest: the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom
ok 26 - the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom
  ---
  duration_ms: 25.469415
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
ok 27 - an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
  ---
  duration_ms: 28.650072
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
ok 28 - an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
  ---
  duration_ms: 19.629416
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
ok 29 - round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
  ---
  duration_ms: 8.443699
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
ok 30 - round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
  ---
  duration_ms: 9.325768
  type: 'test'
  ...
# Subtest: recovery from an amplitude of exactly zero (the new floor is not a trap)
ok 31 - recovery from an amplitude of exactly zero (the new floor is not a trap)
  ---
  duration_ms: 9.577526
  type: 'test'
  ...
# Subtest: the local engine refuses a model with no degrees of freedom; one more point and it fits
ok 32 - the local engine refuses a model with no degrees of freedom; one more point and it fits
  ---
  duration_ms: 24.164219
  type: 'test'
  ...
1..32
# tests 32
# suites 0
# pass 32
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 9200.733068

exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '4408,4455p'; nl -ba CLAUDE.md | sed -n '745,758p'; nl -ba tests/js/background_parity.test.js | sed -n '49,90p'; nl -ba docs/superpowers/plans/2026-09-27-background-twins.md | sed -n '24,52p'; git status --short" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 0ms:
  4408	function shirleyBackground(be, intensity, maxIter) {
  4409	  const n = be.length;
  4410	  if (n < 2) return new Array(n).fill(0);
  4411	  const I0 = intensity[0], I1 = intensity[n - 1];
  4412	  let bg = new Array(n).fill(0);
  4413	
  4414	  for (let iter = 0; iter < maxIter; iter++) {
  4415	    const newBg = new Array(n).fill(0);
  4416	    for (let i = 0; i < n; i++) {
  4417	      // Net signal clamped at zero, max(y - B, 0), as fitting.shirley_background
  4418	      // (Proctor–Sherwood): a noise channel below the background contributes
  4419	      // no loss, never NEGATIVE loss (Task 4 S4, unit 4 2026-09-27 — the JS
  4420	      // integrated the raw difference and converged to a different fixed point,
  4421	      // 0.015–0.24 % of the span away from the background the server fits).
  4422	      let sumRight = 0;
  4423	      for (let j = i; j < n - 1; j++) {
  4424	        sumRight += (Math.max(intensity[j] - bg[j], 0) + Math.max(intensity[j + 1] - bg[j + 1], 0)) / 2 * Math.abs(be[j + 1] - be[j]);
  4425	      }
  4426	      let sumTotal = 0;
  4427	      for (let j = 0; j < n - 1; j++) {
  4428	        sumTotal += (Math.max(intensity[j] - bg[j], 0) + Math.max(intensity[j + 1] - bg[j + 1], 0)) / 2 * Math.abs(be[j + 1] - be[j]);
  4429	      }
  4430	      const frac = sumTotal > 0 ? sumRight / sumTotal : (n - 1 - i) / (n - 1);
  4431	      newBg[i] = I1 + (I0 - I1) * frac;
  4432	    }
  4433	    bg = newBg;
  4434	  }
  4435	  return bg;
  4436	}
  4437	
  4438	function smartBackground(be, intensity, maxIter, rawIntensity) {
  4439	  // Smart (constrained Shirley): standard Shirley clamped to never exceed data.
  4440	  // The Shirley runs on `intensity` (the endpoint-averaged copy); the clamp is
  4441	  // against the RAW data (`rawIntensity`, defaulting to `intensity`), as
  4442	  // fitting.smart_background does: averaging only ever moves the background,
  4443	  // never the reported net counts (Task 4 S5, unit 4 2026-09-27 — at an
  4444	  // endpoint average of 10 the two sides differed by up to 1 % of the span at
  4445	  // the averaged edges).
  4446	  const n = be.length;
  4447	  if (n < 2) return new Array(n).fill(0);
  4448	  const raw = rawIntensity || intensity;
  4449	  const shir = shirleyBackground(be, intensity, maxIter);
  4450	  for (let i = 0; i < n; i++) shir[i] = Math.min(shir[i], raw[i]);
  4451	  return shir;
  4452	}
  4453	
  4454	// Experimental constrained Shirley background, closer to the public Avantage
  4455	// Smart description: the data-constraint is enforced *during* iteration, not as
   745	
   746	The page's background twins (`computeBackgroundCore`: what it draws, freezes
   747	into `fitResult.bgIntensity` at fit time, saves, and what the local engine
   748	fits against) equal fitting.py's to 1e-6 of the intensity span at a converged
   749	iteration count for shirley, smart, smart_exp, tougaard and linear, with
   750	endpoint averaging 1 and 10 (`tests/js/background_parity.test.js`, unit 4
   751	2026-09-27: the JS Shirley now clamps the net signal at zero and smart clamps
   752	against the raw data — Task 4's S4 / S5; smart at averaging 10 was 1.2 % of
   753	the span away). Known gaps, pinned: `shirley_linear` (de-listed) diverges on
   754	descending grids; the UI's Shirley iteration count (default 5) leaves
   755	0.016–0.019 % of the span of unfinished iteration (Part 5 of the
   756	sealed-fit-record memo).
   757	
   758	Use Shirley for standard core-level regions. Linear only when the
    49	  'shirleyBackground', 'smartBackground', 'smartExperimentalBackground', 'shirleyLinearBackground',
    50	  'linearBackground', 'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
    51	].map(extractFn).join('\n') + '\nconst manualAnchorBackground = () => { throw new Error("not in this test"); };' +
    52	  '\nreturn { computeBackgroundCore };')();
    53	const CONVERGED_ITER = 200;
    54	const jsBg = (be, inten, method, nAvg) => JS.computeBackgroundCore(be, inten,
    55	  { bgType: method, shirleyIter: String(CONVERGED_ITER), endpointAvg: String(nAvg), bgStart: '', bgEnd: '' });
    56	
    57	const CASES = py({ mode: 'cases' });
    58	const span = y => Math.max(...y) - Math.min(...y);
    59	function maxRelDiff(a, b, sp) { let m = 0; for (let i = 0; i < a.length; i++) m = Math.max(m, Math.abs(a[i] - b[i])); return m / sp; }
    60	function compare(method, nAvg) {
    61	  const py_out = py({ mode: 'bg', items: CASES.map(c => ({ method, be: c.be, inten: c.inten, n_avg: nAvg })) });
    62	  return CASES.map((c, k) => ({ label: c.label, rel: maxRelDiff(jsBg(c.be, c.inten, method, nAvg), py_out[k], span(c.inten)) }));
    63	}
    64	
    65	test('the cases include the committed real U 4f scan, ascending and descending', () => {
    66	  assert.ok(CASES.length >= 6, CASES.map(c => c.label).join('; '));
    67	  assert.ok(CASES.some(c => /real U 4f/.test(c.label) && /descending/.test(c.label)));
    68	});
    69	
    70	// Parity tolerance: 1e-6 of the intensity span — far below Task 4's smallest
    71	// measured gap (1.5e-4 of the span, the unclamped Shirley) and far above the
    72	// difference between 200 JS iterations and the server's 1e-6-count stopping
    73	// tolerance.
    74	const TOL = 1e-6;
    75	for (const method of ['shirley', 'smart', 'smart_exp', 'tougaard', 'linear']) {
    76	  for (const nAvg of [1, 10]) {
    77	    test(`${method}, endpoint average ${nAvg}: the page's background equals the server's within ${TOL} of the span on every case`, () => {
    78	      for (const r of compare(method, nAvg)) assert.ok(r.rel <= TOL, `${r.label}: ${r.rel.toExponential(2)} of the span`);
    79	    });
    80	  }
    81	}
    82	
    83	test('KNOWN GAP (de-listed, not fixed): shirley_linear agrees on ascending grids and diverges on descending ones (Task 4 cause 3)', () => {
    84	  const rows = compare('shirley_linear', 1);
    85	  for (const r of rows.filter(r => /ascending/.test(r.label))) assert.ok(r.rel <= 1e-3, `${r.label}: ${r.rel}`);
    86	  const desc = rows.filter(r => /descending/.test(r.label));
    87	  assert.ok(desc.some(r => r.rel > 0.05), 'still diverges on descending grids: ' + desc.map(r => r.rel.toFixed(3)).join(', ') +
    88	    ' — if this starts failing, the gap was closed; update the pin and CLAUDE.md');
    89	  assert.match(html, /<option value="shirley_linear" disabled hidden/, 'shirley_linear stays de-listed (disabled, hidden; shown only for saved files that use it)');
    90	});
    24	Blast radius (Task 4): the JS backgrounds are what the page DRAWS, what it
    25	freezes into `fitResult.bgIntensity` / `bgSubtracted` at fit time and saves,
    26	what the local engine (Batch Fit, fallback) fits against, and what stack
    27	Path B reconstructs. Backend fits, χ², refined parameters and Quantify areas
    28	never touch them.
    29	
    30	## 2. Measurement (the parity cases: synthetic C 1s, synthetic U 4f doublet, the committed real U 4f Scan_0; each ascending and descending)
    31	
    32	Max |JS − server| as % of the intensity span:
    33	
    34	| method | endpoint avg | iterations | before | after |
    35	|---|---|---|---|---|
    36	| shirley | 1 | 200 (converged) | 0.047 % | 0.0000 % |
    37	| shirley | 10 | 200 | 0.078 % | 0.0000 % |
    38	| smart | 1 | 200 | 0.047 % | 0.0000 % |
    39	| smart | 10 | 200 | **1.19 %** | 0.0000 % |
    40	| shirley / smart | 1 / 10 | 5 (the UI default) | 0.047–1.19 % | 0.016–0.019 % (unconverged iteration: Part 5, not this unit) |
    41	
    42	## 3. Tests
    43	
    44	`tests/js/background_parity.test.js` + `tests/js/background_parity_backend.py`
    45	(fitting.py's own functions, never a reimplementation): shirley, smart,
    46	smart_exp, tougaard, linear × endpoint average 1 and 10, the page's
    47	`computeBackgroundCore` at a converged iteration count, every case within
    48	1e-6 of the span (Task 4's smallest gap was 1.5e-4). On the unfixed page the
    49	four shirley / smart tests FAIL and the rest pass. `shirley_linear`: agrees on
    50	ascending grids, still diverges on descending ones (pinned; the test fails if
    51	the gap closes, so the pin and CLAUDE.md get updated), and stays de-listed.
    52	
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-xYSvXeVg' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-L5r86Iep' (errno=Operation not permitted)
?? docs/autofit/codex/background_twins_verdict_runA.md
?? docs/autofit/codex/background_twins_verdict_runB.md

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\''),cp=require('\\''child_process'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
function extract(src,name){ const lines=src.split('\\''\\n'\\''); const start=lines.findIndex(l=>l.startsWith('\\''function '\\''+name+'\\''('\\'')); let d=0;for(let i=start;i<lines.length;i++){for(const c of lines[i]){if(c==='\\''{'\\'')d++; if(c==='\\''}'\\'')d--;}if(d===0)return lines.slice(start,i+1).join('\\''\\n'\\'');}}
const names=['\\''shirleyBackground'\\'','\\''smartBackground'\\'','\\''smartExperimentalBackground'\\'','\\''shirleyLinearBackground'\\'','\\''linearBackground'\\'','\\''tougaardBackground'\\'','\\''_applyEndpointAveraging'\\'','\\''_bgWindowIndices'\\'','\\''computeBackgroundCore'\\''];
const current=new Function(names.map(n=>extract(html,n)).join('\\''\\n'\\'')+'\\''; return {shirleyBackground,computeBackgroundCore};'\\'')();
const oldhtml=cp.execFileSync('\\''git'\\'',['\\''show'\\'','\\''895f323:templates/index.html'\\''],{encoding:'\\''utf8'\\'',stdio:['\\''pipe'\\'','\\''pipe'\\'','\\''ignore'\\'']});
const old=new Function(names.map(n=>extract(oldhtml,n)).join('\\''\\n'\\'')+'\\''; return {shirleyBackground,computeBackgroundCore};'\\'')();
const python='\\''/Users/skyefortier/xps-app/venv/bin/python3'\\'';
const bootstrap='\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; runpy.run_path(sys.argv[1],run_name=\"__main__\")'\\'';
function py(req){return JSON.parse(cp.execFileSync(python,['\\''-c'\\'',bootstrap,'\\''tests/js/background_parity_backend.py'\\''],{input:JSON.stringify(req),encoding:'\\''utf8'\\'',maxBuffer:64000000,env:{...process.env,PYTHONDONTWRITEBYTECODE:'\\''1'\\''}}));}

const be=[0,1,3],inten=[10,20,40];
console.log(JSON.stringify({case:'\\''nonuniform linear'\\'',js:current.computeBackgroundCore(be,inten,{bgType:'\\''linear'\\'',shirleyIter:'\\''200'\\'',endpointAvg:'\\''1'\\''}),python:py({mode:'\\''bg'\\'',items:[{method:'\\''linear'\\'',be,inten,n_avg:1}]})[0]}));
const x=[3.5,1.1,1,0],y=[6,7,13,19];
console.log(JSON.stringify({case:'\\''nonuniform smart regression'\\'',js:current.computeBackgroundCore(x,y,{bgType:'\\''smart'\\'',shirleyIter:'\\''200'\\'',endpointAvg:'\\''1'\\''}),old:old.computeBackgroundCore(x,y,{bgType:'\\''smart'\\'',shirleyIter:'\\''200'\\'',endpointAvg:'\\''1'\\''}),python:py({mode:'\\''bg'\\'',items:[{method:'\\''smart'\\'',be:x,inten:y,n_avg:1}]})[0]}));
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins
 succeeded in 3346ms:
/Users/skyefortier/.matplotlib is not a writable directory
{"case":"nonuniform linear","js":[10,25,40],"python":[10,20,40]}
/Users/skyefortier/.matplotlib is not a writable directory
{"case":"nonuniform smart regression","js":[6,6,7.181818181818182,19],"old":[6,7,13,19],"python":[6,7,13,19]}

codex
1. **MAJOR — The new clamp interacts with the existing initialization/fallback to produce persistent cycles.** [templates/index.html:4428](/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/templates/index.html:4428), particularly the fallback at line 4430.

   Reproducer: descending `be=[3.5,1.1,1,0]`, `intensity=[6,7,13,19]`, endpoint averaging `1`, iterations `200`.

   | Background | Python and F3 JS | New JS |
   |---|---|---|
   | Shirley | `[6,10.333333,14.666667,19]` | `[6,6,7.181818,19]` |
   | Smart | `[6,7,13,19]` | `[6,6,7.181818,19]` |

   Shirley’s error is **57.6% of the intensity span**, introduced by this change. Both outputs remain wrong at 2,000 iterations. Python starts from a linear background and retains it when the integral vanishes; JS starts from zeros and can enter a cycle involving its linear fallback.

   This also occurs on uniform grids: `be=[3,2,1,0]`, `intensity=[100,107,120,127]` gives Shirley `[100,100,113.5,127]` at both 5 and 200 iterations, versus Python `[100,107,120.5,127]`. Increasing the iteration count does not resolve it. Add these cases and resolve the initialization/zero-integral interaction before shipping. Display, frozen backgrounds, local fitting and stack reconstruction inherit the error.

2. **MINOR — The new documentation overstates the parity guarantee.** [CLAUDE.md:748](/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/CLAUDE.md:748).

   It claims parity for `linear` without preserving Task 4’s known non-uniform-grid exception. With `be=[0,1,3]`, `intensity=[10,20,40]`, JS returns `[10,25,40]`; Python returns `[10,20,40]`: **16.7% of span**. This implementation gap predates the branch; qualify the new claim rather than expanding this unit to fix linear.

Verification: all 12 new tests pass; replaying them against F3 produces exactly the four promised Shirley/smart failures. The real scan loads, the bridge uses the correct backend functions, and the documented measurements reproduce. The smart caller passes the raw slice correctly; `smart_exp` and `shirley_linear` remain untouched. The divergence/de-listing pin is effective. The 76 selected related tests also pass after handling the sandbox’s Python temporary-directory import issue in memory. No files changed.

**VERDICT: NO-GO**
tokens used
74,243
1. **MAJOR — The new clamp interacts with the existing initialization/fallback to produce persistent cycles.** [templates/index.html:4428](/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/templates/index.html:4428), particularly the fallback at line 4430.

   Reproducer: descending `be=[3.5,1.1,1,0]`, `intensity=[6,7,13,19]`, endpoint averaging `1`, iterations `200`.

   | Background | Python and F3 JS | New JS |
   |---|---|---|
   | Shirley | `[6,10.333333,14.666667,19]` | `[6,6,7.181818,19]` |
   | Smart | `[6,7,13,19]` | `[6,6,7.181818,19]` |

   Shirley’s error is **57.6% of the intensity span**, introduced by this change. Both outputs remain wrong at 2,000 iterations. Python starts from a linear background and retains it when the integral vanishes; JS starts from zeros and can enter a cycle involving its linear fallback.

   This also occurs on uniform grids: `be=[3,2,1,0]`, `intensity=[100,107,120,127]` gives Shirley `[100,100,113.5,127]` at both 5 and 200 iterations, versus Python `[100,107,120.5,127]`. Increasing the iteration count does not resolve it. Add these cases and resolve the initialization/zero-integral interaction before shipping. Display, frozen backgrounds, local fitting and stack reconstruction inherit the error.

2. **MINOR — The new documentation overstates the parity guarantee.** [CLAUDE.md:748](/Users/skyefortier/xps-app/.claude/worktrees/fix-background-twins/CLAUDE.md:748).

   It claims parity for `linear` without preserving Task 4’s known non-uniform-grid exception. With `be=[0,1,3]`, `intensity=[10,20,40]`, JS returns `[10,25,40]`; Python returns `[10,20,40]`: **16.7% of span**. This implementation gap predates the branch; qualify the new claim rather than expanding this unit to fix linear.

Verification: all 12 new tests pass; replaying them against F3 produces exactly the four promised Shirley/smart failures. The real scan loads, the bridge uses the correct backend functions, and the documented measurements reproduce. The smart caller passes the raw slice correctly; `smart_exp` and `shirley_linear` remain untouched. The divergence/de-listing pin is effective. The 76 selected related tests also pass after handling the sandbox’s Python temporary-directory import issue in memory. No files changed.

**VERDICT: NO-GO**
