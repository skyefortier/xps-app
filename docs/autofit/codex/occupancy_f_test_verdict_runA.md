OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0e6c1-17ac-7fb3-90bd-8dad0315ab69
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
I’ll read the plan and diff, trace support and orphan handling through the engine and payload consumers, and check the tests. I’ll keep the review read-only and finish with ranked findings and a verdict.

exec
/bin/zsh -lc "pwd && git status --short && git diff --stat main..HEAD && rg --files -g 'AGENTS.md' -g 'CLAUDE.md' -g '*occupancy*' -g '*noise*'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-GQ54hhxp' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-7cZ08FrT' (errno=Operation not permitted)
?? docs/autofit/codex/occupancy_f_test_verdict_runA.md
?? docs/autofit/codex/occupancy_f_test_verdict_runB.md
?? "docs/autofit/test_data/7 - GTA-2-66 U-naph and COT.DATA"
?? "docs/autofit/test_data/8 GTA-2-46ii U-naph and XeF2, graphite 40%, powder, Cu, 0.4eV, 400 um.DATA"
?? docs/autofit/test_data/Ugly_Fe_2p.spec.json
?? docs/autofit/test_data/Ugly_Fe_2p_2.spec.json
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-GTvToryP' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-kimGRCeM' (errno=Operation not permitted)
 autofit/confidence.py                              |  30 ++--
 autofit/engine.py                                  | 112 ++++++++++++-
 autofit/grammar.py                                 |   8 +-
 .../codex/occupancy_f_test_review_prompt.txt       |  20 +++
 .../plans/2026-09-27-occupancy-f-test.md           | 178 +++++++++++++++++++++
 tests/autofit/test_occupancy_support.py            | 161 +++++++++++++++++++
 tests/autofit/test_stress_honesty.py               |  17 +-
 tests/test_browser_find_peaks_full_window.py       |  12 +-
 8 files changed, 517 insertions(+), 21 deletions(-)
CLAUDE.md
autofit/noise.py
scripts/measure_replicate_noise.py
docs/superpowers/plans/2026-09-27-occupancy-f-test.md
docs/autofit/inventory/replicate_noise_survey.json
docs/superpowers/plans/2026-09-27-f3-noise-floor-and-c1s-gate.md
tests/autofit/test_noise_model.py
tests/autofit/test_occupancy_support.py
docs/autofit/codex/occupancy_f_test_review_prompt.txt
docs/autofit/codex/noise_model_recheck2_prompt.txt
docs/autofit/codex/noise_model_verdicts.md
docs/autofit/codex/occupancy_f_test_verdict_runB.md
docs/autofit/codex/occupancy_f_test_verdict_runA.md
docs/autofit/codex/noise_model_math_review_prompt.txt
docs/autofit/codex/noise_model_recheck3_prompt.txt
docs/autofit/codex/noise_model_recheck_prompt.txt

exec
/bin/zsh -lc 'cat CLAUDE.md && cat docs/superpowers/plans/2026-09-27-occupancy-f-test.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
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

exec
/bin/zsh -lc 'cat docs/findings/noise-floor-occupancy/README.md && cat docs/findings/noise-floor-occupancy/variant_F_support_test.patch' in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
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
diff --git a/autofit/confidence.py b/autofit/confidence.py
index bb74778..ab2897f 100644
--- a/autofit/confidence.py
+++ b/autofit/confidence.py
@@ -83,6 +83,9 @@ def _max_correlation(report: ModelReport, role: str) -> Optional[float]:
     return float(np.max(sub)) if sub.size else None
 
 
+from fitting import SUPPORT_MIN_F as _SUPPORT_MIN_F  # F3: one threshold, the server's
+
+
 def build_confidence_vector(
     report: ModelReport,
     role: str,
@@ -96,12 +99,19 @@ def build_confidence_vector(
                 if h.startswith(f"{role}:")]
 
     amplitude = float(comp.amplitude) if comp is not None else None
-    floor = detection_floor_multiple * noise_floor
+    # F3 (2026-09-27): detectability is the support F test on the fit
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
@@ -122,9 +132,9 @@ def build_confidence_vector(
         },
         "detectability": {
             "amplitude": amplitude,
-            "noise_floor": noise_floor,
-            "floor_multiple": detection_floor_multiple,
-            "floor_multiple_is_tunable": True,
+            "basis": "support_f_test",       # F3: fitting._component_support, F >= SUPPORT_MIN_F
+            "support_f": (support or {}).get("f"),
+            "support_min_f": _SUPPORT_MIN_F,
             "status": detect_status,
         },
         "identifiability": {
diff --git a/autofit/engine.py b/autofit/engine.py
index dbf4fd7..9bad455 100644
--- a/autofit/engine.py
+++ b/autofit/engine.py
@@ -36,6 +36,7 @@ from typing import Callable, Optional
 
 import numpy as np
 from lmfit import Model, Parameters
+import fitting as _fitting  # F3: the server's support statistic, one definition
 from lmfit.model import ModelResult
 from scipy.integrate import trapezoid
 
@@ -637,6 +638,17 @@ class FittedComponent:
     amplitude: float
     shape_params: dict
     line_shape: Optional[LineShape] = None
+    # Unit F3 (2026-09-27): does the fit that produced this component need it?
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
@@ -652,10 +664,46 @@ class FitOutcome:
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
+def _occupies(comp: "FittedComponent") -> bool:
+    """A slot is occupied by a component the data support (F3). No threshold
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
+    supports = _component_supports(result)
     for slot in model.slots:
         prefix = _slot_prefix(slot.role)
         pars = result.params
@@ -676,6 +724,7 @@ def _extract_fitted_components(
             slot_role=slot.role, position=center, fwhm=fwhm,
             amplitude=amplitude, shape_params=shape_params,
             line_shape=slot.line_shape,
+            support=supports.get(prefix),
         ))
     return out
 
@@ -1055,7 +1104,7 @@ def match_components_to_slots(
                                       (bound_overrides or {}).get(slot.role))
         return (lo <= comp.position <= hi
                 and slot.fwhm_range[0] <= comp.fwhm <= slot.fwhm_range[1]
-                and comp.amplitude > noise_floor)
+                and _occupies(comp))       # F3: supported by the data, not amplitude > 1 count
 
     def _window_center(slot: ComponentSlot) -> float:
         # NEVER the widened bound (Codex-caught, round 2): this is a
@@ -1077,7 +1126,7 @@ def match_components_to_slots(
             orphans.append(FittedComponent(
                 slot_role="unmatched", position=comp.position, fwhm=comp.fwhm,
                 amplitude=comp.amplitude, shape_params=comp.shape_params,
-                line_shape=comp.line_shape,
+                line_shape=comp.line_shape, support=comp.support,
             ))
             continue
 
@@ -1095,7 +1144,7 @@ def match_components_to_slots(
         claimed = FittedComponent(
             slot_role=best_slot.role, position=comp.position, fwhm=comp.fwhm,
             amplitude=comp.amplitude, shape_params=comp.shape_params,
-            line_shape=comp.line_shape,
+            line_shape=comp.line_shape, support=comp.support,
         )
         if incumbent is None:
             slot_map[best_slot.role] = claimed
@@ -2229,8 +2278,10 @@ def _attempt_proposal(
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
index c9a85cd..bed2606 100644
--- a/autofit/grammar.py
+++ b/autofit/grammar.py
@@ -181,11 +181,15 @@ class ComponentSlot:
     broad_justification: Optional[str] = None
 
     def contains(self, be: float, fwhm: float, amplitude: float,
-                 noise_floor: float) -> bool:
+                 noise_floor: float = 0.0) -> bool:
+        # F3 (2026-09-27): occupancy is decided by the support F test on the
+        # fit (engine._occupies); this geometric check keeps only the sign of
+        # the amplitude. ``noise_floor`` is accepted and ignored (no caller in
+        # the engine passes it any more).
         return (
             self.be_window[0] <= be <= self.be_window[1]
             and self.fwhm_range[0] <= fwhm <= self.fwhm_range[1]
-            and amplitude > noise_floor
+            and amplitude > 0
         )
 
 

exec
/bin/zsh -lc 'git diff main..HEAD -- autofit tests' in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-VPeufU3c' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-jP0KMzLr' (errno=Operation not permitted)
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
/bin/zsh -lc "rg --files -g 'AGENTS.md' -g 'pyproject.toml' -g '*requirements*' -g 'pytest.ini' -g '*lock*' && rg -n 'def _component_support|SUPPORT_MIN_F|noise_floor|slot_map|followed_support' autofit fitting.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
requirements-dev.txt
requirements.txt
autofit/candidates.py:551:    noise_floor: float = 1.0,
autofit/candidates.py:621:            return float(np.median(np.sqrt(np.maximum(y[mask], noise_floor))))
autofit/candidates.py:622:        return float(np.sqrt(max(noise_floor, 1.0)))
fitting.py:1441:SUPPORT_MIN_F = 10.0
fitting.py:1444:def _component_support(y_sub, fitted_sub, comp_y, weights, n_free_comp, n_free_total) -> dict[str, Any]:
fitting.py:1460:            "supported": bool(delta > 0 and (chi_with == 0 or f >= SUPPORT_MIN_F))}
fitting.py:1524:        required = f >= SUPPORT_MIN_F
autofit/engine.py:645:    # SUPPORT_MIN_F). The occupancy decisions (slot matching, the proposal
autofit/engine.py:668:def _component_supports(result: ModelResult) -> dict[str, dict]:
autofit/engine.py:694:def _followed_supports(result: ModelResult, model: CandidateModel,
autofit/engine.py:740:    supports = _followed_supports(result, model, _component_supports(result))
autofit/engine.py:1125:    noise_floor: float,
autofit/engine.py:1142:    slot_map: dict[str, Optional[FittedComponent]] = {s.role: None for s in model.slots}
autofit/engine.py:1190:        incumbent = slot_map[best_slot.role]
autofit/engine.py:1197:            slot_map[best_slot.role] = claimed
autofit/engine.py:1202:                slot_map[best_slot.role] = claimed
autofit/engine.py:1206:    slot_map["__orphans__"] = orphans  # type: ignore[assignment]
autofit/engine.py:1207:    slot_map["__unsupported__"] = unsupported  # type: ignore[assignment]
autofit/engine.py:1208:    return slot_map
autofit/engine.py:1265:    noise_floor: float,
autofit/engine.py:1331:        slot_map = match_components_to_slots(outcome.components, model, noise_floor,
autofit/engine.py:1333:        if slot_map.pop("__orphans__", []):
autofit/engine.py:1335:        slot_map.pop("__unsupported__", None)   # reporting only: those slots are empty
autofit/engine.py:1336:        for role, comp in slot_map.items():
autofit/engine.py:1504:    noise_floor: float,
autofit/engine.py:1509:    sigma = np.sqrt(np.maximum(y, noise_floor))
autofit/engine.py:1906:    noise_floor: float = 1.0,
autofit/engine.py:1954:        local_sigma = float(np.median(np.sqrt(np.maximum(y_asc[mask], noise_floor)))) \
autofit/engine.py:1955:            if mask.sum() > 1 else float(np.sqrt(max(noise_floor, 1.0)))
autofit/engine.py:2105:    noise_floor: float,
autofit/engine.py:2112:    sigma = np.sqrt(np.maximum(y, noise_floor))
autofit/engine.py:2261:    noise_floor: float,
autofit/engine.py:2333:                     + (f", F = {f:.2f} < {_fitting.SUPPORT_MIN_F:.0f}" if f is not None else "") + ")")
autofit/engine.py:2340:    local_sigma = float(np.median(np.sqrt(np.maximum(y[mask], noise_floor)))) \
autofit/engine.py:2341:        if mask.sum() > 1 else float(np.sqrt(max(noise_floor, 1.0)))
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
autofit/confidence.py:28:from fitting import SUPPORT_MIN_F as _SUPPORT_MIN_F  # the server's support threshold: one definition
autofit/confidence.py:91:    noise_floor: float,
autofit/confidence.py:96:    ``noise_floor`` / ``detection_floor_multiple`` are accepted and not read
autofit/confidence.py:106:    # absolute 1-count floor. above_floor = supported (F >= SUPPORT_MIN_F);
autofit/confidence.py:137:            "basis": "support_f_test",       # fitting._component_support, F >= SUPPORT_MIN_F
autofit/confidence.py:139:            "support_min_f": _SUPPORT_MIN_F,
autofit/grammar.py:184:                 noise_floor: float = 0.0) -> bool:
autofit/grammar.py:187:        # the amplitude. ``noise_floor`` is accepted and ignored (the engine
autofit/methods/ic_model_comparison.py:22:    "noise_floor", "n_refits", "rng_seed", "candidate_filter",
autofit/methods/ic_model_comparison.py:57:        noise_floor = float(opts.pop("noise_floor", 1.0))
autofit/methods/ic_model_comparison.py:61:            noise_floor=noise_floor,
autofit/methods/ic_model_comparison.py:107:            slot.role: build_confidence_vector(top, slot.role, noise_floor)
autofit/methods/bayesian_exchange_mc.py:289:    "rng_seed", "candidate_filter", "ci_level", "noise_floor",
autofit/methods/bayesian_exchange_mc.py:328:        opts.pop("noise_floor", None)     # accepted for symmetry; unused

exec
/bin/zsh -lc 'cat docs/superpowers/plans/2026-09-27-occupancy-f-test.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
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
/bin/zsh -lc 'git diff main..HEAD -- autofit/engine.py autofit/confidence.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-6ORFw8j8' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-2RICBsDH' (errno=Operation not permitted)
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

exec
/bin/zsh -lc "cat docs/findings/noise-floor-occupancy/README.md && sed -n '1430,1530p' fitting.py && rg -n '_component_support\\(|follows|n_free_comp' fitting.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
exec
/bin/zsh -lc "sed -n '180,640p' autofit/engine.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
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
    if not refit.success or getattr(refit, "box_unverified", False):
        # F2 (2026-09-26): a refit that did not converge establishes nothing
        # (nor does a differential-evolution candidate whose search box no
        # refinement verified — the main fit's acceptance rule rejects it too;
        # Codex round 1)
        # either way — its chi-square is wherever the optimiser stopped (a
        # redundant anchor read "required", F 992, from a refit stopped early;
        # F 1.17 once it completed). No verdict; the caller decides.
        return {"required": None, "f": None, "chi2_with": float(chi2_with), "chi2_without_refit": chi2_without,
                "refit_converged": False, "reason": "refit_not_converged",
                "message": str(getattr(refit, "message", "") or "")[:200]}
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
1444:def _component_support(y_sub, fitted_sub, comp_y, weights, n_free_comp, n_free_total) -> dict[str, Any]:
1451:    p = max(1, int(n_free_comp))
1475:                        chi2_with, n_free_comp, n_free_total) -> dict[str, Any]:
1507:    p = max(1, int(n_free_comp))
1920:                    n_free_comp = sum(1 for n, par in result.params.items()
1924:                        float(result.chisqr), n_free_comp, result.nvarys)}
1979:        n_free_comp = sum(1 for n, par in result.params.items() if n.startswith(prefix) and par.vary and par.expr is None)
1980:        support = _component_support(y_sub, fitted_sub, peak_y, weights, n_free_comp, result.nvarys)
1981:        # A linked component follows its parent: it is supported exactly when the
1990:    # A linked component follows its ROOT ancestor (a grandchild follows the
2006:            ip["support"]["follows"] = by_id[root]["id"]

 succeeded in 0ms:
# in the grammar. Per-candidate budgets (CANDIDATE_TIMEOUT_SEC,
# PROPOSAL_CANDIDATE_TIMEOUT_SEC) bound any one candidate but not their sum
# — a 29-candidate grammar at ~7s/candidate for ordinary (non-degenerate)
# fits already runs ~3-4 minutes, and several candidates hitting the
# DS+G-style degenerate corner push that further. Checked once per outer
# loop iteration (compare_models): once exceeded, remaining candidates are
# skipped and the sweep returns best-so-far, ranked normally, with
# ComparisonResult.analysis_truncated=True — an honest partial result
# instead of a request timeout. Deliberately below the gunicorn dev
# --timeout so this truncation path always gets to run and respond before
# the worker is aborted (see DEPLOY.md / dev gunicorn --timeout).
TOTAL_ANALYSIS_TIMEOUT_SEC = 240.0
PROPOSAL_ENDPOINT_WARNING_BE = 1.0
PROPOSAL_COINCIDENCE_BE = 0.5

# Component treated as asymmetric during shape-aware slot disambiguation.
ALPHA_SYMMETRY_THRESHOLD = 0.01      # DS / DS+G α, asym-GL asymmetry
LACX_EXPONENT_ASYMMETRY = 0.02       # |α − β| for true CasaXPS LA

# ── Pre-fit out-of-grammar dominant seeding (unit F1, 2026-07-07) ──────────
# Measured motivation (PROGRESS.md "Real multi-environment C 1s — MEASURED
# DIAGNOSIS"): on real low-BE-dominant multi-environment C 1s spectra the
# dominant data feature lies OUTSIDE every grammar window, so every
# candidate faces an unfittable 40k-count residual — fits either burn
# FIT_CANDIDATE_MAX_NFEV without converging or pin their mains at window
# floors (χ²ᵣ ~656), and the post-fit proposal pass can only patch ONE
# missing feature after the damage is done.  The pre-seed pass detects
# prominent smoothed local maxima of the background-subtracted DATA that no
# grammar/diagnostic window can express and augments every candidate with
# absent-eligible, region-`unassigned` slots BEFORE fitting — the proposal
# pass's honesty contract (assignment of an out-of-grammar feature is human
# adjudication, never window inheritance), moved ahead of the fit so the
# optimization landscape is sane.  Detection is data-driven; it fires only
# when such a feature exists, so grammars whose windows cover the data are
# byte-identical (pinned).  All gates are UNVERIFIED engine tunables
# (surfaced per-feature in the result payload):
PRESEED_MIN_FRACTION_OF_MAX = 0.25   # dominance gate: smoothed net height ≥
                                     # this fraction of the global smoothed
                                     # net max (weak features stay
                                     # proposal-pass territory)
PRESEED_AMPLITUDE_SNR = PROPOSAL_AMPLITUDE_SNR   # same detection-floor SNR
PRESEED_SMOOTH_POINTS = 5            # moving-average width for maxima search
PRESEED_MAX = 2                      # most dominants seeded per sweep
PRESEED_MIN_SEPARATION_BE = 1.0      # between two accepted seeds (eV)

# ── Stage-2 curvature-seed operating point (recalibration, 2026-07-10) ────
# The Step-1 diagnosis measured the old operating point (dominance fraction
# 0.25, combined cap 2, window+margin blocking) discarding expert-modeled
# species detected at prom_z 8.5-273.  For a suggest-a-profile tool a
# MISSED resolvable shoulder costs more than a spurious candidate the
# selection layer prunes (goal ruling): curvature seeds are gated by the
# noise wall (prom_z) + detection-floor SNR, with only a TRIVIA floor on
# relative height — expert practice models discrete species down to ~5-8%
# of the window max (measured ds8 reference); below ~2% the residual pass
# remains the honest channel.  Both UNVERIFIED tunables, surfaced in the
# pool payload; selection (absent-slot / persistence / BIC*) prunes.
CURVATURE_SEED_MIN_FRACTION = 0.02   # trivia floor (was the 0.25 dominance
                                     # gate — that gate stays for the F1
                                     # dominant channel only)
SEED_MAX_TOTAL = 6                   # dominant + curvature seeds combined
                                     # (was 2; ds7/Scan_1-class spectra
                                     # carry 5-6 real detected species)
DETECTION_WIDTH_ABSORB_FRACTION = 0.7  # detection-slot papering-over flag:
                                       # fitted width ≥ this × the slot's
                                       # scale-relative ceiling (2.5× the
                                       # detected width) ⇒ ≥1.75× detected —
                                       # absorbing a neighbor.  UNVERIFIED.
GRAMMAR_AUGMENT_MAX_SEEDS = 3        # of those, at most this many augment
                                     # each GRAMMAR family (measured: the
                                     # full set made all 29 screens blow
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
# Fit outcome + component extraction
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class FittedComponent:
    slot_role: str
    position: float
    fwhm: float          # width-parameter value (m_gauss for DS+G — fitalg convention)
    amplitude: float
    shape_params: dict

exec
/bin/zsh -lc "sed -n '765,1070p' autofit/engine.py && sed -n '1260,1440p' autofit/engine.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:

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
    seed: int,
    position_jitter_eV: float = 0.15,
    fwhm_jitter_frac: float = 0.20,
    amplitude_jitter_frac: float = 0.30,
    x: Optional[np.ndarray] = None,
    y_net: Optional[np.ndarray] = None,
    fit_full_window: bool = False,
) -> Parameters:
    """
    Perturbed starting parameters for a multi-start refit (bounds-clipped).

    Port improvement over fitalg: when (x, y_net) are provided the defaults
    are data-informed — in particular the amplitude UPPER bound scales with
    the spectrum instead of the fixed 1e5 fallback, which silently clamped
    (and systematically failed) stability refits on peaks brighter than 1e5
    counts (e.g. the UCl4-BN N 1s line at ~1.06e5).
    """
    rng = np.random.default_rng(seed)
    params = _default_params_from_slots(model, x=x, y_net=y_net,
                                        fit_full_window=fit_full_window)

    def _clip(par, new_val: float) -> None:
        lo = par.min if np.isfinite(par.min) else -np.inf
        hi = par.max if np.isfinite(par.max) else np.inf
        par.set(value=float(np.clip(new_val, lo, hi)))

    for slot in model.slots:
        prefix = _slot_prefix(slot.role)
        if slot.linked_to is None:
            cp = params.get(f"{prefix}center")
            if cp is not None and cp.expr is None:
                _clip(cp, cp.value + rng.normal(0.0, position_jitter_eV))
        else:
            op = params.get(f"{prefix}offset")
            if op is not None:
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

exec
/bin/zsh -lc "rg -n 'occup|amplitude [<>]=?|__orphans__|__unsupported__|match_components_to_slots|FittedComponent\\(|detectability|filtered_dominant_alternative' autofit app.py templates/index.html && ls -ld venv /Users/skyefortier/xps-app/venv" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 exited 1 in 0ms:
app.py:52:# value lets a single request occupy a worker for many minutes (audit F7).
templates/index.html:15643:  if (d.filtered_dominant_alternative) {
templates/index.html:15644:    const fda = d.filtered_dominant_alternative;
templates/index.html:16316:  if (d.filtered_dominant_alternative) {
templates/index.html:16317:    const f = d.filtered_dominant_alternative;
autofit/reference_bridge.py:239:    Raises KeyError for unknown elements or unoccupied subshells (the
autofit/coverage_index.py:6:(Z=1..96 x occupied subshells) and classifies each into the FITTING-
autofit/coverage_index.py:25:                     derived quantum bookkeeping (occupied subshells,
autofit/coverage_index.py:83:    - very deep core: the LOWEST-n occupied level, once the element has
autofit/coverage_index.py:84:      >= ``_DEEP_CORE_MIN_SHELLS`` distinct principal shells occupied,
autofit/cited_values.py:13:  the Z=1..96 table, subshell occupied, component label real);
autofit/cited_values.py:142:        raise _reject(i, f"subshell {subshell!r} is not occupied for "
autofit/confidence.py:32:# No longer read (noise-floor unit, 2026-09-27): detectability is the support
autofit/confidence.py:104:    # Noise-floor unit (2026-09-27): detectability is the support F test on the fit
autofit/confidence.py:113:        detect_status = "above_floor" if amplitude > 0 else "not_confidently_detected"
autofit/confidence.py:135:        "detectability": {
autofit/engine.py:645:    # SUPPORT_MIN_F). The occupancy decisions (slot matching, the proposal
autofit/engine.py:646:    # gate, detectability) read this instead of an absolute amplitude floor
autofit/engine.py:647:    # of 1 count, which judged a slot "occupied" at amplitude 1.5 and not at
autofit/engine.py:650:    # component (hand-built in tests): then occupancy falls back to amplitude
autofit/engine.py:671:    Empty when the result carries no data (never raises: occupancy then falls
autofit/engine.py:727:def _occupies(comp: "FittedComponent") -> bool:
autofit/engine.py:728:    """A slot is occupied by a component the data support. No threshold
autofit/engine.py:733:    return comp.amplitude > 0
autofit/engine.py:757:        out.append(FittedComponent(
autofit/engine.py:1122:def match_components_to_slots(
autofit/engine.py:1133:    if the data support it (``_occupies``: the server's support F test on the
autofit/engine.py:1135:    it occupies no slot (the slot stays empty for persistence) and it is not
autofit/engine.py:1138:    components are returned under ``"__unsupported__"`` (reporting only). The
autofit/engine.py:1139:    1-count floor this replaces made every component at amplitude <= 1 an
autofit/engine.py:1168:        if not _occupies(comp):
autofit/engine.py:1169:            unsupported.append(comp)   # not there: neither an occupant nor an orphan
autofit/engine.py:1173:            orphans.append(FittedComponent(
autofit/engine.py:1191:        claimed = FittedComponent(
autofit/engine.py:1206:    slot_map["__orphans__"] = orphans  # type: ignore[assignment]
autofit/engine.py:1207:    slot_map["__unsupported__"] = unsupported  # type: ignore[assignment]
autofit/engine.py:1284:    occupied: dict[str, int] = {s.role: 0 for s in model.slots}
autofit/engine.py:1331:        slot_map = match_components_to_slots(outcome.components, model, noise_floor,
autofit/engine.py:1333:        if slot_map.pop("__orphans__", []):
autofit/engine.py:1335:        slot_map.pop("__unsupported__", None)   # reporting only: those slots are empty
autofit/engine.py:1339:            occupied[role] += 1
autofit/engine.py:1356:            persistence=occupied[role] / max(n_attempted, 1),
autofit/engine.py:1361:        for role in occupied
autofit/engine.py:1711:    filtered_dominant_alternative: Optional[dict] = None
autofit/engine.py:2330:    if not _occupies(comp):
autofit/engine.py:2342:    if comp.amplitude < PROPOSAL_AMPLITUDE_SNR * local_sigma:
autofit/engine.py:3126:            result.filtered_dominant_alternative = {
autofit/coverage.py:10:- which subshells are occupied (Madelung/Aufbau filling — an algorithm);
autofit/coverage.py:96:    "(no-invention rail). Deviations can shift valence occupancy details "
autofit/coverage.py:136:    covers every occupied subshell through Z = 96 (5g first fills far
autofit/coverage.py:147:    """Madelung filling of ``z`` electrons → ordered occupied subshells."""
autofit/coverage.py:158:            "n": n, "l": l, "occupancy": occ,
autofit/coverage.py:194:    n, l, occ = c["n"], c["l"], c["occupancy"]
autofit/coverage.py:200:        "occupancy": occ, "capacity": capacity,
autofit/coverage.py:220:    occ = {c["subshell"]: c["occupancy"] for c in config}
autofit/coverage.py:289:    multiplet = any(c["l"] >= 2 and 0 < c["occupancy"] < 2 * (2 * c["l"] + 1)
autofit/coverage.py:310:    """One occupied level's derived record ('Cl', '2p'). KeyError when the
autofit/coverage.py:311:    subshell is not occupied for that element."""
autofit/coverage.py:317:        f"{st['symbol']}: subshell {level!r} is not occupied "
autofit/coverage.py:318:        f"(occupied: {[l['level'] for l in st['levels']]})"
autofit/coverage.py:353:    in the Z=1..96 table or the subshell is not occupied.
autofit/coverage.py:361:    lv = level_structure(sym, subshell)      # KeyError when not occupied
autofit/coverage.py:368:                   "occupancy": lv["occupancy"], "capacity": lv["capacity"],
autofit/methods/ic_model_comparison.py:184:                "filtered_dominant_alternative":
autofit/methods/ic_model_comparison.py:185:                    result.filtered_dominant_alternative,
autofit/methods/ic_model_comparison.py:197:                f"{result.filtered_dominant_alternative['name']} beats this "
autofit/methods/ic_model_comparison.py:199:                f"{result.filtered_dominant_alternative['delta_bic_vs_winner']:.1f} "
autofit/methods/ic_model_comparison.py:201:                f"({result.filtered_dominant_alternative['filter_reason']})"
autofit/methods/ic_model_comparison.py:202:                if result.filtered_dominant_alternative else "")
autofit/methods/ic_model_comparison.py:341:        "filtered_dominant_alternative": result.filtered_dominant_alternative,
autofit/grammar.py:185:        # Noise-floor unit (2026-09-27): occupancy is decided by the support F test on the
autofit/grammar.py:186:        # fit (engine._occupies); this geometric check keeps only the sign of
autofit/grammar.py:192:            and amplitude > 0
autofit/grammar.py:314:                          unoccupied subshell)
ls: venv: No such file or directory
drwxr-xr-x  7 skyefortier  staff  224 Jul  7 11:35 /Users/skyefortier/xps-app/venv

exec
/bin/zsh -lc "cat docs/findings/noise-floor-occupancy/README.md && sed -n '1435,1465p' fitting.py && rg -n '_component_support\\(|follows|n_free_comp' fitting.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
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
1444:def _component_support(y_sub, fitted_sub, comp_y, weights, n_free_comp, n_free_total) -> dict[str, Any]:
1451:    p = max(1, int(n_free_comp))
1475:                        chi2_with, n_free_comp, n_free_total) -> dict[str, Any]:
1507:    p = max(1, int(n_free_comp))
1920:                    n_free_comp = sum(1 for n, par in result.params.items()
1924:                        float(result.chisqr), n_free_comp, result.nvarys)}
1979:        n_free_comp = sum(1 for n, par in result.params.items() if n.startswith(prefix) and par.vary and par.expr is None)
1980:        support = _component_support(y_sub, fitted_sub, peak_y, weights, n_free_comp, result.nvarys)
1981:        # A linked component follows its parent: it is supported exactly when the
1990:    # A linked component follows its ROOT ancestor (a grandchild follows the
2006:            ip["support"]["follows"] = by_id[root]["id"]

exec
/bin/zsh -lc "rg -n 'def |decisive|persistence|plausib|orphan' autofit/engine.py | tail -100 && sed -n '540,630p' autofit/engine.py && sed -n '1,120p' tests/conftest.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
1334:            n_with_orphans += 1
1344:    def _med(v):  # median or None
1347:    def _mad(v):
1356:            persistence=occupied[role] / max(n_attempted, 1),
1368:        orphan_rate=n_with_orphans / max(n_attempted, 1),
1384:    persistence: float
1392:def _count_slot_free_params(slot: ComponentSlot, primary: FitOutcome) -> int:
1400:def _is_main_role(role: str) -> bool:
1405:def _linked_groups(model: CandidateModel) -> list[list[ComponentSlot]]:
1417:    def root(role: str) -> str:
1428:def _identify_absent_slots(
1433:    persistence_threshold: float = ABSENT_SLOT_PERSISTENCE_THRESHOLD,
1440:    Every member must individually meet the persistence + area criteria for
1462:    def _member_report(slot: ComponentSlot) -> Optional[AbsentSlotReport]:
1464:        if sstab is None or sstab.persistence >= persistence_threshold:
1474:            role=slot.role, persistence=sstab.persistence, fitted_area=area,
1500:def compute_residual_diagnostics(
1539:    orphan_peaks: bool = False
1554:    persistence: Optional[float] = None
1594:    plausibility: PlausibilityFlags
1598:    # Full lmfit param names fixed at their bounds by the decisive-override
1605:    def reduced_chi_sq(self) -> float:
1610:    def adjusted_n_params(self) -> int:
1615:    def bic_adjusted(self) -> float:
1626:    def bic_raw(self) -> float:
1633:    def bic_weighted(self) -> float:
1649:    def n_eff_lag1(self) -> Optional[float]:
1667:    def active_min_persistence(self) -> float:
1672:        return min(s.persistence for s in active)
1675:def compute_bic(fit: FitOutcome) -> float:
1693:    #   'no_clean_survivor'  — nothing passed plausibility cleanly; the
1695:    #   'decisive_override'  — clean survivors exist but a bound-fixed refit
1708:    # decisive threshold — {name, bic_star, delta_bic_vs_winner,
1743:def rank_and_filter(
1745:    persistence_threshold: float = DEFAULT_PERSISTENCE_THRESHOLD,
1751:    Filter (plausibility, active persistence) then rank (χ²ᵣ, BIC*).
1755:    samples): when NO candidate passes plausibility cleanly but some are
1766:        active_min = r.active_min_persistence
1767:        stable = active_min >= persistence_threshold
1768:        if r.plausibility.boundary_hits or r.plausibility.unphysical_widths \
1769:                or r.plausibility.orphan_peaks:
1770:            # orphan_peaks included (Codex Stage-2 re-review finding #3):
1772:            # plausibility violation, not clean-survivor material.
1773:            filtered_out.append((r, f"plausibility: {r.plausibility}"))
1780:            filtered_out.append((r, f"stability: active min persistence "
1781:                                    f"{active_min:.2f} < {persistence_threshold}{extra}"))
1799:        # label instability (orphan_peaks) on heavily-overlapped low-res
1814:    # NOTE: the decisive-override path (clean survivors exist but a
1861:    def payload(self) -> dict:
1882:def _all_grammar_windows(
1891:def _preseed_window_margin(candidates: list[CandidateModel]) -> float:
1900:def detect_out_of_grammar_dominants(
1937:    def in_any_window(be: float) -> bool:
1992:def _preseed_augmented(
2036:def _proposal_tiles(x: np.ndarray) -> list[tuple[str, tuple[float, float]]]:
2049:def _main_slot_fwhm_midpoint(model: CandidateModel) -> float:
2055:def _proposal_blocked(
2101:def _detect_residual_proposals(
2185:def _next_proposal_index(model: CandidateModel) -> int:
2205:def _augmented_candidate(base: CandidateModel, spec: ProposalSpec) -> CandidateModel:
2227:def _initial_params_for_augmented(
2255:def _attempt_proposal(
2265:    absent_slot_persistence_threshold: float,
2284:    def _fast(reason: str):
2323:    # implausibly narrow spike) is spurious → reject.  (Shape endpoints like
2404:    pr.persistence = sstab.persistence
2405:    if sstab.persistence < PROPOSAL_PERSISTENCE_THRESHOLD:
2406:        pr.rejection_reason = (f"persistence {sstab.persistence:.2f} < "
2416:        persistence_threshold=absent_slot_persistence_threshold,
2422:        plausibility=PlausibilityFlags(
2425:            orphan_peaks=stability.orphan_rate > 0.1,
2447:def _cross_candidate_coincidences(
2485:def _bound_fixed_refit(
2515:    if lm is None or not report.plausibility.boundary_hits:
2519:    for hit in report.plausibility.boundary_hits:
2561:        plausibility=PlausibilityFlags(
2567:            orphan_peaks=stability.orphan_rate > 0.1,
2572:        # promoted via decisive-override keeps its width_capped/proposed_peaks
2579:def _apply_decisive_override(
2584:    persistence_threshold: float,
2601:            if why.startswith("plausibility")
2602:            and r.active_min_persistence >= persistence_threshold]
2614:        if refit.active_min_persistence < persistence_threshold:
2624:        result.conditional_reason = "decisive_override"
2633:def _report_progress(
2649:def compare_models(
2658:    absent_slot_persistence_threshold: float = ABSENT_SLOT_PERSISTENCE_THRESHOLD,
2659:    persistence_threshold: float = DEFAULT_PERSISTENCE_THRESHOLD,
2675:    proposals, bound-fixed refits, decisive override, detection). Default 1
2686:    refits, the proposal pass, and the bound-fixed decisive-override
2944:            persistence_threshold=absent_slot_persistence_threshold,
2950:            plausibility=PlausibilityFlags(
2953:                orphan_peaks=stability.orphan_rate > 0.1,
3006:                        absent_slot_persistence_threshold=absent_slot_persistence_threshold,
3046:        persistence_threshold=persistence_threshold,
3050:    result = _apply_decisive_override(
3052:        persistence_threshold=persistence_threshold,
3100:    # at ΔBIC* +74…+944): a FILTERED candidate whose BIC* decisively beats
3106:        # promotion LINEAGE, not just names: a decisive-override winner is
3137:def _weighted_ic_disagreement(survivors: "list[ModelReport]") -> Optional[dict]:
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
"""Make the repo root importable regardless of how pytest is invoked."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

codex
The new code uses the fit’s background-subtracted data, best fit, weights, and free-parameter count, and calls the server’s support function directly. I’m checking linked-parameter edge cases and whether the stress test’s replacement warning still depends on P3.

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -m pytest -p no:cacheprovider -s -q tests/autofit/test_occupancy_support.py tests/autofit/test_stress_honesty.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
exec
/bin/zsh -lc "sed -n '1930,2010p' fitting.py && sed -n '1,155p' autofit/methods/ic_model_comparison.py && sed -n '1428,1500p' autofit/engine.py && sed -n '3075,3137p' autofit/engine.py && sed -n '100,155p' tests/autofit/test_stress_honesty.py && rg -n 'bg_mismatch_case|def _ic' tests/autofit/{test_stress_honesty,stress_cases}.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
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
            threshold=area_fraction_threshold,
            removed_n_params=_count_slot_free_params(slot, primary),
        )

    absent: list[AbsentSlotReport] = []
    for group in _linked_groups(model):
        reports = [_member_report(s) for s in group]
        if all(r is not None for r in reports):
            absent.extend(reports)  # type: ignore[arg-type]
    return absent


# ─────────────────────────────────────────────────────────────────────────────
# Residual diagnostics
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ResidualDiagnostics:
    autocorrelation_lag1: float
    autocorr_flag: bool
    window_energies: dict[str, float]
    flagged_windows: list[str]


def compute_residual_diagnostics(
        # proposal attempts merged in as the 'residual_gap' source (dedup
        # by the same coincidence tolerance the seeds use)
        pool_payload = pool.payload()
        merge_residual_attempts(
            pool_payload,
            [{"center_be": (pr.fitted_center
                            if pr.fitted_center is not None
                            else pr.proposed_center_init),
              "accepted": bool(pr.accepted)}
             for _, pr in proposal_attempts],
            coincidence_ev=PROPOSAL_COINCIDENCE_BE,
            proposal_pass_ran=enable_proposal_pass,
        )
        # loud detection-family truncation record (Codex Stage-2 MAJOR):
        # names every feature the slot cap dropped (empty = no overflow)
        pool_payload["detection_model_overflow"] = detection_overflow
        result.candidate_pool = pool_payload
    elif pool_error is not None:
        result.candidate_pool = {
            "error": pool_error,
            "note": "candidate-generation layer failed — analysis degraded "
                    "to dominant-channel-only seeding (see server log)",
        }

    # Result-level honesty flag (stress-suite finding 0 — burial measured
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
tests/autofit/stress_cases.py:404:def bg_mismatch_case(seed: int) -> StressCase:
tests/autofit/stress_cases.py:489:        bg_mismatch_case(seed=61 + o),
tests/autofit/test_stress_honesty.py:24:    bg_mismatch_case,
tests/autofit/test_stress_honesty.py:36:def _ic(case):
tests/autofit/test_stress_honesty.py:139:    case = bg_mismatch_case(seed=61)

 exited 2 in 1531ms:

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
2 errors in 1.30s

exec
/bin/zsh -lc "rg -n 'role=|role =' autofit/grammars | head -110 && sed -n '30,53p' tests/autofit/test_stress_honesty.py && sed -n '390,440p' tests/autofit/stress_cases.py && sed -n '15620,15665p' templates/index.html && sed -n '16305,16340p' templates/index.html && sed -n '285,370p' autofit/methods/bayesian_exchange_mc.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
rg: autofit/grammars: IO error for operation on autofit/grammars: No such file or directory (os error 2)
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
        bg="shirley_like",
        notes="control: matched background family",
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

exec
/bin/zsh -lc "rg -n 'role=|role =' autofit/grammar.py | head -100 && rg -n '"'^def |''^class '"' autofit/grammar.py | tail -55 && rg -n 'shared_fwhm_params|fwhm_linked_to' autofit/grammar.py | head -40" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
211:            if s.role == role:
622:        role=rename[s.role],
43:class LineShape(Enum):
69:class BackgroundType(Enum):
77:class MaterialClass(Enum):
95:class Phase:
115:class ComponentSlot:
197:class CandidateModel:
217:class CandidateGrammar:
236:class PhaseAmbiguityError(ValueError):
240:class UnknownRegionError(KeyError):
247:def _parse_region_requests(
268:def resolve(
513:def _guard_slot_tags(candidates: list[CandidateModel], region: str, phase_id: str) -> None:
529:def _guard_phase_leakage(grammar: CandidateGrammar, phases: list[Phase]) -> None:
550:def _compose_joint_candidates(
588:def _retag_slot(
628:def _slot_param_prefix(role: str) -> str:
146:    fwhm_linked_to: Optional[str] = None
202:    # (name, min, max) free params referenced by fwhm_linked_to expressions
203:    shared_fwhm_params: tuple[tuple[str, float, float], ...] = ()
574:            shared_rename = {name: f"{slug}__{name}" for name, _, _ in cand.shared_fwhm_params}
577:            for name, lo, hi in cand.shared_fwhm_params:
583:            shared_fwhm_params=tuple(shared),
593:    """Rewrite role / linked_to / fwhm_linked_to under the region prefix.
608:    fwhm_link = s.fwhm_linked_to
610:        # fwhm_linked_to may reference either a shared param or another
624:        fwhm_linked_to=fwhm_link,

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''; import pytest; raise SystemExit(pytest.main(['\\''-p'\\'','\\''no:cacheprovider'\\'','\\''-s'\\'','\\''-q'\\'','\\''tests/autofit/test_occupancy_support.py'\\'','\\''tests/autofit/test_stress_honesty.py'\\'']))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
exec
/bin/zsh -lc "rg --files autofit | head -65 && rg -n 'role=|role =' autofit/regions | head -80" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
autofit/lint.py
autofit/reference_bridge.py
autofit/candidates.py
autofit/coverage_index.py
autofit/cited_values.py
autofit/reference.py
autofit/noise.py
autofit/engine.py
autofit/grammar.py
autofit/coverage.py
autofit/__init__.py
autofit/parity.py
autofit/confidence.py
autofit/fit_physics.py
autofit/methods/base.py
autofit/methods/ic_model_comparison.py
autofit/methods/__init__.py
autofit/methods/sparse_map.py
autofit/methods/least_squares.py
autofit/methods/bayesian_exchange_mc.py
autofit/methods/multivariate_mcr.py
autofit/methods/max_entropy.py
autofit/regions/u4f.py
autofit/regions/n1s.py
autofit/regions/b1s.py
autofit/regions/c1s.py
autofit/regions/__init__.py
autofit/regions/cl2p.py
autofit/criteria.py
autofit/regions/u4f.py:198:                role=role, region=REGION, phase_id=pid,
autofit/regions/n1s.py:77:            role="main_n1s", region=REGION, phase_id=pid,
autofit/regions/n1s.py:83:            role="main_n1s", region=REGION, phase_id=pid,
autofit/regions/b1s.py:93:                role=role, region=REGION, phase_id=pid,
autofit/regions/c1s.py:310:                role=role, region=REGION, phase_id=pid,
autofit/regions/cl2p.py:144:                role="main_cl2p32", region=REGION, phase_id=pid,
autofit/regions/cl2p.py:155:                    role="main_cl2p12", region=REGION, phase_id=pid,
autofit/regions/cl2p.py:167:                role="main_cl2p12", region=REGION, phase_id=pid,

exec
/bin/zsh -lc "sed -n '290,405p' autofit/regions/c1s.py && sed -n '160,285p' autofit/regions/u4f.py && sed -n '1,90p' autofit/regions/__init__.py && sed -n '245,330p' autofit/grammar.py && sed -n '90,140p' tests/autofit/stress_cases.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
        - A1–A3_linked_offset:  + contaminant centers as bounded offsets
        - AG0–AG3_linked:       asym-GL graphitic main variants (expert-fit
                                parity family; UNVERIFIED-empirical shape)
        - M0–M3:  mixed graphitic (DS+G) + aliphatic (PV) two-main models
        - B2/B3 (+_linked):     symmetric adventitious-carbon models
        - shake-up satellite only with an asymmetric main (admissibility)

        ``oxidation_state`` is accepted for the Layer-C seam; C 1s defines
        no oxidation-state overrides.
        """
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
    def diagnostic_windows(self) -> dict[str, tuple[float, float]]:
        return {
            "main_72": U4F72_WINDOW,
            "main_52": U4F52_WINDOW,
            "satellite_72": U4F_SAT72_WINDOW,
            "satellite_52": U4F_SAT52_WINDOW,
        }

    def build_candidates(
        self, phase: Phase, oxidation_state: Optional[str] = None
    ) -> list[CandidateModel]:
        """
        Candidates (a controlled ladder of satellite-pair freedom, so model
        comparison can isolate WHICH freedom the data pays for — Codex
        Stage-3 finding #1):

        - ``U0_mains``            — main doublet only (reduced model for IC)
        - ``U1_mains_satpair``    — + satellite doublet locked to the core
                                    splitting (shape + amplitude tied)
        - ``U1b_mains_satpair_freesep`` — satellite doublet with FREE pair
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
"""
Region cookbook registry (spec §7).

A region module owns Layer B for one core-level region: candidate model
families, BE windows, FWHM priors, lineshape admissibility, satellites —
every constant lit-cited or flagged UNVERIFIED in the module source.

Modules self-register at import; ``get_region_module`` is the resolver's
lookup.
"""

from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

from ..grammar import CandidateModel, Phase


@runtime_checkable
class RegionModule(Protocol):
    region: str

    def build_candidates(
        self, phase: Phase, oxidation_state: Optional[str] = None
    ) -> list[CandidateModel]:
        ...

    def diagnostic_windows(self) -> dict[str, tuple[float, float]]:
        ...

    def provenance(self) -> list[dict]:
        """
        Machine-readable provenance for every physical constant the module's
        grammar consumes: [{constant, value, status, source}], with status ∈
        {VERIFIED, CONDITIONAL, UNVERIFIED}.  Flows into the `analysis`
        namespace so runtime output can distinguish clean physics from fits
        built on CONDITIONAL/UNVERIFIED constants (comments alone are
        invisible at runtime — Codex cookbook review, blocker 1).
        """
        ...


_REGISTRY: dict[str, RegionModule] = {}


def register_region(module: RegionModule) -> None:
    key = module.region
    if key in _REGISTRY and _REGISTRY[key] is not module:
        raise ValueError(f"region {key!r} already registered")
    _REGISTRY[key] = module


def get_region_module(region: str) -> RegionModule:
    try:
        return _REGISTRY[region]
    except KeyError:
        from ..grammar import UnknownRegionError
        raise UnknownRegionError(
            f"no region module registered for {region!r} "
            f"(registered: {sorted(_REGISTRY)})"
        ) from None


def registered_regions() -> list[str]:
    return sorted(_REGISTRY)


# Import modules for self-registration (order = documentation order).
from . import c1s  # noqa: E402,F401
from . import n1s  # noqa: E402,F401
from . import u4f  # noqa: E402,F401
from . import b1s  # noqa: E402,F401
from . import cl2p  # noqa: E402,F401


def _parse_region_requests(
    regions: "list[str | tuple[str, str]] | str | tuple[str, str]",
) -> list[tuple[str, Optional[str]]]:
    if isinstance(regions, str):
        return [(regions, None)]
    if isinstance(regions, tuple) and len(regions) == 2 \
            and all(isinstance(v, str) for v in regions):
        return [(regions[0], regions[1])]
    out: list[tuple[str, Optional[str]]] = []
    for r in regions:
        if isinstance(r, str):
            out.append((r, None))
        elif isinstance(r, tuple) and len(r) == 2:
            out.append((str(r[0]), str(r[1])))
        else:
            raise ValueError(
                f"region request must be 'Region' or ('Region', 'phase_id'), got {r!r}"
            )
    return out


def resolve(
    phases: list[Phase],
    regions: "list[str | tuple[str, str]] | str",
    oxidation_state: Optional[str] = None,
    target_phases: Optional[dict[str, str]] = None,
    allow_structural_fallback: bool = False,
    cited_values: Optional[list] = None,
) -> CandidateGrammar:
    """
    Compose the candidate grammar for ``regions`` over ``phases``.

    Parameters
    ----------
    phases          : the sample's phase list (length 1 = single-phase default)
    regions         : region requests for one (possibly joint) fit window.
                      Each request is either a region name (``"C 1s"``) or a
                      phase-qualified ``("B 1s", "BN")`` pair.  The SAME
                      region may appear once per phase — that is how a
                      BN/B4C sample co-fits both phases' B 1s contributions
                      in one window (spec §2: phase-scoped slot families).
    oxidation_state : Layer-C override, forwarded to region modules
    target_phases   : {region: phase_id} disambiguation for UNqualified
                      requests of a region contributed by more than one phase
    allow_structural_fallback : Phase D, OPT-IN (default False keeps every
                      existing caller byte-identical).  A region with no
                      registered module that parses as an element/level in
                      the Z=1..96 table resolves to DERIVED STRUCTURE only
                      (autofit.coverage): zero fit candidates, provenance
                      records for the doublet/singlet structure, ratio
                      expectation, multiplet/conductor flags, and an
                      UNVERIFIED value-None position — 'structure known,
                      positions UNVERIFIED, supply a cited source'.  Such
                      regions are listed in ``CandidateGrammar.
                      structural_only`` and excluded from joint candidate
                      composition.
    cited_values    : optional list of autofit.cited_values.CitedValue —
                      cited empirical values whose matching records ride
                      into the structural provenance (they do NOT build
                      candidates; windows/widths remain curation work).

    Raises
    ------
    PhaseAmbiguityError : unqualified region in multiple phases w/o a target
    UnknownRegionError  : region not registered, or not covered by any phase
                          (with fallback enabled: also not derivable —
                          unparseable label, unknown element, or an
                          unoccupied subshell)
    """
    from .regions import get_region_module  # local import: avoid cycle

    requests = _parse_region_requests(regions)
    if not phases:
        raise ValueError("phases must be a non-empty list (single-phase = length 1)")
    if not requests:
        raise ValueError("regions must be a non-empty list")
    target_phases = target_phases or {}

    ids = [p.id for p in phases]
    if len(set(ids)) != len(ids):
        raise ValueError(f"duplicate phase ids: {ids}")

    # Region names occurring in >1 request get phase-qualified slugs so the
    # composed slot roles stay unique across phases.
def _linear_bg(x, b0=300.0, slope=0.0):
    return b0 + slope * (x - x[0])


def _shirley_like_bg(x, signal, k=0.15, b0=300.0):
    """Integral (Shirley-shaped) background: proportional to the signal area
    at higher BE — deliberately NOT a straight line."""
    # BE axis ascends; Shirley steps up on the high-BE side of peaks
    csum = np.cumsum(signal[::-1])[::-1] * STEP
    return b0 + k * (csum.max() - csum)


def _noisy(y_true, seed):
    rng = np.random.default_rng(seed)
    return rng.poisson(np.maximum(y_true, 0.0)).astype(float)


def _slot(role, window, fwhm=(0.6, 2.5), shape=LineShape.PSEUDO_VOIGT, **kw):
    return ComponentSlot(role=role, region=REGION, phase_id=PHASE,
                         be_window=window, line_shape=shape,
                         fwhm_range=fwhm, **kw)


def _cand(name, slots, bg=BackgroundType.LINEAR):
    return CandidateModel(name=name, background=bg, slots=tuple(slots))


def _grammar(candidates, windows=None):
    return CandidateGrammar(
        regions=(REGION,), phase_ids=(PHASE,), candidates=list(candidates),
        diagnostic_windows=windows or {}, notes=["synthetic stress grammar"],
        provenance={},
    )


def _ls_specs(truth, shape="pseudo_voigt_gl"):
    return [{"id": str(i + 1), "shape": shape, "center": t["center"],
             "amplitude": t["height"], "fwhm": t["fwhm"], "glMix": ETA * 100}
            for i, t in enumerate(truth)]


def _n_peak_ladder(c1, c2, n_max=4, fwhm=(0.6, 2.5), half=2.0,
                   bg=BackgroundType.LINEAR):
    """1..n_max-component candidates with DISTINCT slot windows — the
    engine's slot-role identity contract: cross-refit matching identifies
    components BY WINDOW, so identical windows label-switch across refits
    and zero out persistence (measured: minpers=0.00, orphan_peaks=True).
    Real region grammars always give each species its own window; the
    ladder mirrors that.

    P1: one window over the doublet span.  P2: split at the true-centers

exec
/bin/zsh -lc "sed -n '1590,1685p' autofit/engine.py && sed -n '155,235p' autofit/methods/ic_model_comparison.py && sed -n '144,178p' tests/autofit/stress_cases.py && sed -n '1,115p' autofit/criteria.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
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
    lo, hi = c1 - half, c2 + half
    windows = {
        1: [(lo, hi)],
        2: [(lo, mid), (mid, hi)],
        3: [(lo, mid), (mid, hi), (hi, hi + 2.5)],
        4: [(lo - 2.5, lo), (lo, mid), (mid, hi), (hi, hi + 2.5)],
        5: [(lo - 2.5, lo), (lo, mid), (mid, hi), (hi, hi + 2.5),
            (hi + 2.5, hi + 5.0)],
    }
    out = []
    for n in range(1, n_max + 1):
        slots = [_slot(f"main_{chr(97 + i)}", w, fwhm)
                 for i, w in enumerate(windows[n])]
        out.append(_cand(f"P{n}", slots, bg=bg))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Regime 1 — heavy overlap: two equal-width peaks at k×FWHM separation
# ─────────────────────────────────────────────────────────────────────────────

def overlap_case(sep_frac: float, height: float, seed: int,
                 expectation: str) -> StressCase:
    x = _grid()
    fwhm = 1.2
    c1 = 197.2
    c2 = c1 + sep_frac * fwhm
    truth = [{"center": c1, "fwhm": fwhm, "height": height},
             {"center": c2, "fwhm": fwhm, "height": 0.7 * height}]
    sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
    y = _noisy(sig + _linear_bg(x), seed)
    return StressCase(
        name=f"overlap_sep{sep_frac:g}_h{height:g}",
        regime="heavy_overlap", expectation=expectation,
        x=x, y=y, truth=truth, truth_n=2,
"""
Pluralistic model-selection criteria panel (spec v2.1 §6).

From each candidate's shared ``(RSS, k, n)`` compute — near-free — a panel:
weighted χ²ᵣ, BIC* (ranking default), AICc, and nested-model F-tests.

Hard rules encoded here (Codex re-review items):

- ONE likelihood convention throughout: fitalg's
  ``IC = n·ln(RSS/n) + penalty`` (never mix with the ``χ² + penalty`` form).
- The panel is a **diagnostic, not independent corroboration** — all
  members share the Gaussian residual assumption on processed (non-count)
  data.  Every payload carries ``"not independent tests"``.
- F-test only on genuinely nested pairs (same shapes on shared roles,
  strict slot-subset).
- Two distinct flags, never merged: ``bic_ambiguous`` (|ΔBIC*| < τ) and
  ``criteria_conflict`` (top-by-BIC* ≠ top-by-AICc, or an F-test rejects a
  peak BIC* keeps).
- No single scalar decides.  Trust order for this data:
  parity → stability/persistence → residual structure → BIC* tie-break.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy import stats

from .engine import ModelReport

NOT_INDEPENDENT = (
    "not independent tests — BIC*, AICc, χ²ᵣ and F share the Gaussian "
    "residual/noise assumption on processed data; treat as correlated views "
    "of one likelihood"
)

TRUST_ORDER = (
    "parity to expert fits → stability/persistence → residual structure → "
    "BIC* as a relative tie-breaker only"
)

# α for the nested-model F-test — UNVERIFIED tunable (conventional 0.05).
F_TEST_ALPHA = 0.05


def ic_values(rss: float, k: int, n: int) -> dict[str, Optional[float]]:
    """BIC* and AICc in the fitalg likelihood convention."""
    if n <= 0 or rss <= 0:
        return {"bic_star": None, "aicc": None}
    base = n * np.log(rss / n)
    bic = base + k * np.log(n)
    aic = base + 2 * k
    denom = n - k - 1
    aicc = aic + (2.0 * k * (k + 1) / denom) if denom > 0 else None
    return {"bic_star": float(bic), "aicc": (float(aicc) if aicc is not None else None)}


def is_nested(smaller: ModelReport, larger: ModelReport) -> bool:
    """
    True when ``smaller``'s slot set is a strict subset of ``larger``'s with
    identical line shapes on the shared roles (and identical backgrounds).
    Absent-slot-adjusted models and shape swaps are NOT nested.
    """
    if smaller.model.background is not larger.model.background:
        return False
    small = {s.role: s.line_shape for s in smaller.model.slots}
    large = {s.role: s.line_shape for s in larger.model.slots}
    if not (set(small) < set(large)):
        return False
    return all(large[r] is small[r] for r in small)


@dataclass
class FTestResult:
    smaller: str
    larger: str
    f_stat: Optional[float]
    p_value: Optional[float]
    extra_params: int
    rejects_extra_peak: bool     # True → the extra component is NOT justified


def f_test(smaller: ModelReport, larger: ModelReport) -> Optional[FTestResult]:
    """
    Nested-model F-test; None when the pair is not genuinely nested OR when
    either model carries absent-slot adjustments (spec §6 v2.1: absent-slot-
    adjusted models are outside F-test validity — their effective parameter
    count was reduced arithmetically, not by a reduced-model refit).
    """
    if smaller.absent_slots or larger.absent_slots:
        return None
    if not is_nested(smaller, larger):
        return None
    rss_s = smaller.primary_fit.residual_sum_sq
    rss_l = larger.primary_fit.residual_sum_sq
    k_s = smaller.primary_fit.n_params
    k_l = larger.primary_fit.n_params
    n = larger.primary_fit.n_data
    dk = k_l - k_s
    dof = n - k_l
    if dk <= 0 or dof <= 0 or rss_l <= 0:
        return None
    f = ((rss_s - rss_l) / dk) / (rss_l / dof)
    p = float(stats.f.sf(max(f, 0.0), dk, dof))
    return FTestResult(
        smaller=smaller.model.name, larger=larger.model.name,
        f_stat=float(f), p_value=p, extra_params=dk,
        rejects_extra_peak=p >= F_TEST_ALPHA,
    )


def build_criteria_panel(
    reports: list[ModelReport],

exec
/bin/zsh -lc "sed -n '1743,1830p' autofit/engine.py && sed -n '2227,2425p' autofit/engine.py && sed -n '2485,2580p' autofit/engine.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
def rank_and_filter(
    reports: list[ModelReport],
    persistence_threshold: float = DEFAULT_PERSISTENCE_THRESHOLD,
    bic_ambiguity_threshold: float = DEFAULT_BIC_AMBIGUITY,
    allow_conditional: bool = True,
    allow_last_resort: bool = False,
) -> ComparisonResult:
    """
    Filter (plausibility, active persistence) then rank (χ²ᵣ, BIC*).

    Two-tier semantics (departure from fitalg, which returned zero survivors
    whenever every candidate had any boundary hit — routine on real composite
    samples): when NO candidate passes plausibility cleanly but some are
    otherwise stable, those are ranked as a CONDITIONAL tier with
    ``result.conditional = True`` and every violation preserved.  Stability
    failures are never promoted — an unstable fit is pathology, not a
    constraint conflict.
    """
    filtered_out: list[tuple[ModelReport, str]] = []
    survivors: list[ModelReport] = []
    conditional_pool: list[ModelReport] = []

    for r in reports:
        active_min = r.active_min_persistence
        stable = active_min >= persistence_threshold
        if r.plausibility.boundary_hits or r.plausibility.unphysical_widths \
                or r.plausibility.orphan_peaks:
            # orphan_peaks included (Codex Stage-2 re-review finding #3):
            # refits repeatedly producing unmatched components is a
            # plausibility violation, not clean-survivor material.
            filtered_out.append((r, f"plausibility: {r.plausibility}"))
            if stable:
                conditional_pool.append(r)
            continue
        if not stable:
            absent_roles = [a.role for a in r.absent_slots]
            extra = f"  (absent slots excluded: {absent_roles})" if absent_roles else ""
            filtered_out.append((r, f"stability: active min persistence "
                                    f"{active_min:.2f} < {persistence_threshold}{extra}"))
            continue
        survivors.append(r)

    conditional = False
    conditional_reason = None
    if allow_conditional and conditional_pool and not survivors:
        survivors = conditional_pool
        conditional = True
        conditional_reason = "no_clean_survivor"
    elif allow_conditional and allow_last_resort and not survivors and reports:
        # LAST-RESORT tier (Stage-2, 2026-07-10; measured on real low-res
        # Fe 2p): fires ONLY when the caller says detection found real
        # structure (allow_last_resort = detection seeds exist) — its job
        # is rescuing DETECTED structure from selection instability, never
        # forcing an answer on featureless data (a flat-noise grammar fit
        # can converge; the honest result there stays no-survivor).
        # Every candidate failed BOTH tiers — typically cross-refit
        # label instability (orphan_peaks) on heavily-overlapped low-res
        # structure.  For a suggest-a-profile tool an EMPTY answer is the
        # worst answer: emit the single best CONVERGED model, loudly
        # flagged unstable.  This tier exists only when clean and
        # conditional are BOTH empty — stability failures are still never
        # preferred over anything (the original design rule stands).
        viable = [r for r in reports
                  if r.primary_fit.converged
                  and np.isfinite(r.bic_adjusted)]
        if viable:
            best = min(viable,
                       key=lambda r: (r.bic_adjusted, r.reduced_chi_sq))
            survivors = [best]
            conditional = True
            conditional_reason = "unstable_last_resort"
    # NOTE: the decisive-override path (clean survivors exist but a
    # bound-fixed refit of a conditional candidate dominates) lives in
    # compare_models — it needs the spectrum to refit; rank_and_filter is
    # pure ranking.

    # BIC* is the ranking default (spec §6); χ²ᵣ breaks ties only.  fitalg
    # ranked (χ²ᵣ, BIC*) — spec-noncompliant, changed per Codex finding #3.
    survivors.sort(key=lambda r: (r.bic_adjusted, r.reduced_chi_sq))

    ambiguous: list[tuple[str, str, str]] = []
    for i in range(len(survivors)):
        for j in range(i + 1, len(survivors)):
            a, b = survivors[i], survivors[j]
            if abs(a.bic_adjusted - b.bic_adjusted) <= bic_ambiguity_threshold \
               and a.model.n_components != b.model.n_components:
                diff = {s.role for s in a.model.slots} ^ {s.role for s in b.model.slots}
                ambiguous.append((
def _initial_params_for_augmented(
    aug_model: CandidateModel,
    base_fit: FitOutcome,
    spec: ProposalSpec,
    x: np.ndarray,
    y_net: np.ndarray,
    fit_full_window: bool = False,
) -> Parameters:
    params = _default_params_from_slots(aug_model, x=x, y_net=y_net,
                                        fit_full_window=fit_full_window)
    if base_fit.lmfit_result is not None:
        for pname, par in base_fit.lmfit_result.params.items():
            if pname not in params or not params[pname].vary:
                continue
            lo = params[pname].min if np.isfinite(params[pname].min) else -np.inf
            hi = params[pname].max if np.isfinite(params[pname].max) else np.inf
            params[pname].set(value=float(np.clip(par.value, lo, hi)))
    prefix = _slot_prefix(spec.role)
    pc = params[f"{prefix}center"]
    pc.set(value=float(np.clip(spec.center_init, pc.min, pc.max)))
    pa = params[f"{prefix}amplitude"]
    pa.set(value=float(np.clip(spec.amplitude_init, pa.min, pa.max)))
    pf = params.get(f"{prefix}fwhm")
    if pf is not None and pf.expr is None:
        pf.set(value=float(np.clip(spec.fwhm_init, pf.min, pf.max)))
    return params


def _attempt_proposal(
    x: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray,
    base_report: ModelReport,
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

 succeeded in 39238ms:
......................
22 passed in 38.89s

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import numpy as np
from autofit.engine import fit_candidate,_slot_prefix
from autofit.grammar import ComponentSlot,CandidateModel,BackgroundType,LineShape
import fitting
x=np.arange(0.,20.,.05); z=np.random.default_rng(42).standard_normal(x.size)
g=lambda c,a: a*np.exp(-4*np.log(2)*((x-c)/1.2)**2)
slots=tuple(ComponentSlot(role=r,region='\\''C 1s'\\'',phase_id='\\''p'\\'',be_window=(c-.5,c+.5),line_shape=LineShape.GAUSSIAN,fwhm_range=(.7,1.8)) for r,c in [('\\''main'\\'',6.),('\\''main_extra'\\'',14.)])
m=CandidateModel(name='\\''prefix'\\'',background=BackgroundType.LINEAR,slots=slots)
for a in [100,150,200,250]:
 y=10000+g(6,a)+g(14,10000)+100*z
 o=fit_candidate(x,y,1/np.sqrt(y),m); lm=o.lmfit_result
 raw=fitting._component_support(lm.data,lm.best_fit,lm.eval_components()['\\''s_main_'\\''],lm.weights,3,lm.nvarys)
 print(a,o.converged,'\\''own parameters'\\'',len([p for p in lm.model.components[0].param_names if lm.params[p].vary]),'\\''branch'\\'',o.components[0].support,'\\''correct'\\'',raw,flush=True)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import sys; sys.path.insert(0,'\\''tests/autofit'\\'')
from stress_cases import bg_mismatch_case
from autofit.methods import get_method
c=bg_mismatch_case(61)
for filt in [None,['\\''P1'\\'','\\''P2'\\'']]:
 r=get_method('\\''ic_model_comparison'\\'').run(c.x,c.y,grammar=c.grammar,options={'\\''n_refits'\\'':4,'\\''rng_seed'\\'':0,'\\''enable_proposal_pass'\\'':True,'\\''candidate_filter'\\'':filt})
 print('\\''FILTER'\\'',filt,'\\''DIAG'\\'',r.diagnostics,'\\''MESSAGE'\\'',r.message,flush=True)
 for a in r.analysis['\\''candidates'\\'']:
  if a['\\''name'\\'']==r.diagnostics.get('\\''winner'\\''): print('\\''WIN'\\'',a,flush=True)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 1739ms:
/Users/skyefortier/.matplotlib is not a writable directory
100 True own parameters 3 branch {'f': 3.0019709005469397, 'delta_chi2': 17.869789002685764, 'supported': False} correct {'f': 6.003941801093879, 'delta_chi2': 17.869789002685764, 'supported': False}
150 True own parameters 3 branch {'f': 6.423773862696058, 'delta_chi2': 38.254264164482834, 'supported': False} correct {'f': 12.847547725392117, 'delta_chi2': 38.254264164482834, 'supported': True}
200 True own parameters 3 branch {'f': 11.323260987576921, 'delta_chi2': 67.44273217682195, 'supported': True} correct {'f': 22.646521975153842, 'delta_chi2': 67.44273217682195, 'supported': True}
250 True own parameters 3 branch {'f': 17.70064249498482, 'delta_chi2': 105.40135487042903, 'supported': True} correct {'f': 35.40128498996964, 'delta_chi2': 105.40135487042903, 'supported': True}

codex
I found two issues to probe: component parameter counts use a prefix match that can include another slot’s parameters, and the replacement mismatch warning still requires a better-scoring filtered candidate. The plan also attributes scale-dependent ranking to BIC*, but this implementation uses log RSS; its score differences are invariant under uniform rescaling for fixed models and correspondingly scaled fits.

 succeeded in 9691ms:
/Users/skyefortier/.matplotlib is not a writable directory
FILTER None DIAG {'winner': 'P2', 'conditional': False, 'conditional_reason': None, 'winner_boundary_hits': [], 'winner_unphysical_widths': [], 'winner_boundary_fixed_params': [], 'filtered_dominant_alternative': {'name': 'P3', 'bic_star': 3648.466236534472, 'delta_bic_vs_winner': 152.94516771360122, 'filter_reason': "plausibility: PlausibilityFlags(boundary_hits=['main_c:fwhm@max'], unphysical_widths=['main_c:fwhm=2.50eV≥2.0eV ordinary cap (no known-broad justification)'], orphan_peaks=False)"}, 'weighted_ic_disagreement': None, 'preseeded_features': [], 'n_survivors': 1, 'n_filtered': 2, 'n_non_converged': 0, 'analysis_truncated': False, 'n_candidates_evaluated': 3, 'n_candidates_total': 3} MESSAGE  WARNING: filtered candidate P3 beats this winner by ΔBIC* 152.9 but did not survive filtering (plausibility: PlausibilityFlags(boundary_hits=['main_c:fwhm@max'], unphysical_widths=['main_c:fwhm=2.50eV≥2.0eV ordinary cap (no known-broad justification)'], orphan_peaks=False))
WIN {'name': 'P2', 'n_components': 2, 'reduced_chi_sq': 308.7466180222082, 'bic_star': 3801.4114042480733, 'bic_raw': 3801.4114042480733, 'bic_weighted': 90199.64272228205, 'n_eff_lag1': 1.5075376884422125, 'survived': True, 'rank': 1, 'filter_reason': None, 'augmented_from': None, 'boundary_fixed_params': [], 'absent_slots': [], 'proposed_peaks': [], 'residual_flags': [], 'unphysical_widths': [], 'autocorr_flag': True, 'min_active_persistence': 1.0, 'boundary_hits': [], 'orphan_peaks': False, 'best_minimum_basin_support': 4}
FILTER ['P1', 'P2'] DIAG {'winner': 'P2', 'conditional': False, 'conditional_reason': None, 'winner_boundary_hits': [], 'winner_unphysical_widths': [], 'winner_boundary_fixed_params': [], 'filtered_dominant_alternative': None, 'weighted_ic_disagreement': None, 'preseeded_features': [], 'n_survivors': 1, 'n_filtered': 1, 'n_non_converged': 0, 'analysis_truncated': False, 'n_candidates_evaluated': 2, 'n_candidates_total': 2} MESSAGE 
WIN {'name': 'P2', 'n_components': 2, 'reduced_chi_sq': 308.7466180222082, 'bic_star': 3801.4114042480733, 'bic_raw': 3801.4114042480733, 'bic_weighted': 90199.64272228205, 'n_eff_lag1': 1.5075376884422125, 'survived': True, 'rank': 1, 'filter_reason': None, 'augmented_from': None, 'boundary_fixed_params': [], 'absent_slots': [], 'proposed_peaks': [], 'residual_flags': [], 'unphysical_widths': [], 'autocorr_flag': True, 'min_active_persistence': 1.0, 'boundary_hits': [], 'orphan_peaks': False, 'best_minimum_basin_support': 4}

exec
/bin/zsh -lc "rg -n 'match_components_to_slots\\(|\\.contains\\(' --glob '*.py' && rg -n 'support|_occupies|_attempt_proposal' tests/autofit/test_occupancy_support.py && nl -ba autofit/engine.py | sed -n '668,730p' && nl -ba docs/superpowers/plans/2026-09-27-occupancy-f-test.md | sed -n '95,180p'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
autofit/engine.py:1122:def match_components_to_slots(
autofit/engine.py:1331:        slot_map = match_components_to_slots(outcome.components, model, noise_floor,
tests/test_browser_batch_roi.py:237:                toastShown: document.getElementById('prominent-toast').classList.contains('show'),
tests/test_browser_find_peaks_drag.py:187:            "() => document.getElementById('find-peaks-overlay').classList.contains('open')")
tests/test_browser_find_peaks_drag.py:190:            "() => document.getElementById('find-peaks-modal-box').classList.contains('dragging')")
tests/test_browser_identify_frame.py:219:        light: document.body.classList.contains('light-theme'),
tests/test_browser_identify_frame.py:229:            light: document.body.classList.contains('light-theme'),
tests/test_browser_identify_frame.py:241:        page.evaluate("""() => { if (document.body.classList.contains('light-theme')) toggleTheme();
tests/test_browser_identify_frame.py:511:        return { mode: placeMode, cls: p.classList.contains('identify-passthrough'),
tests/test_browser_palette.py:174:        assert pg.evaluate("() => document.getElementById('ref-panel').classList.contains('collapsed')") is True
tests/test_browser_palette.py:182:            return { collapsed: p.classList.contains('collapsed'),
tests/test_browser_palette.py:204:            const dragging = p.classList.contains('dragging');
tests/test_browser_palette.py:222:            return { passthrough: p.classList.contains('identify-passthrough'),
tests/test_browser_palette.py:241:            return { mode: placeMode, passthrough: p.classList.contains('identify-passthrough'),
tests/autofit/test_occupancy_support.py:96:    m = match_components_to_slots([main, weak], MODEL, noise_floor=1.0)
tests/autofit/test_occupancy_support.py:106:    m = match_components_to_slots([main, stray], MODEL, noise_floor=1.0)
tests/autofit/test_occupancy_support.py:114:    m = match_components_to_slots([_comp(284.5, 0.0, None)], MODEL, noise_floor=1.0)
tests/autofit/test_fit_full_window_option.py:302:    slot_map = match_components_to_slots([comp], model, noise_floor=1.0,
1:"""Find Peaks occupancy is the server's support F test, not a 1-count floor
5:A slot is OCCUPIED by a component the data support: with the other components
7:(``fitting._component_support``, F >= SUPPORT_MIN_F) — the statistic Run Fit's
8:"not supported by the data" outcome uses. The old rule, ``amplitude > 1.0``,
17:* an unsupported component occupies no slot and is NOT an orphan (an orphan is
18:  a supported peak no slot expects); a supported component outside every
27:from autofit.engine import (FittedComponent, _occupies, fit_candidate,
59:def test_every_fitted_component_carries_the_servers_support_verdict():
62:        s = comps[role].support
63:        assert s is not None and set(s) >= {"f", "delta_chi2", "supported"}, (role, s)
64:        assert s["supported"] is True
75:        assert a[role].support["supported"] == b[role].support["supported"] is True, role
76:        assert b[role].support["f"] == pytest.approx(a[role].support["f"], rel=1e-4), role
77:        assert _occupies(a[role]) and _occupies(b[role])
84:    assert minor.support["supported"] is False, minor.support
85:    assert not _occupies(minor)
88:def _comp(pos, amp, support):
90:                           shape_params={}, line_shape=LineShape.GAUSSIAN, support=support)
93:def test_an_unsupported_component_leaves_its_slot_empty_and_is_not_an_orphan():
94:    main = _comp(284.5, 1e4, {"f": 1e5, "delta_chi2": 1e6, "supported": True})
95:    weak = _comp(286.5, 40.0, {"f": 2.1, "delta_chi2": 12.0, "supported": False})
97:    assert m["main"] is not None and m["main"].support["supported"]
100:    assert m["__unsupported__"] == [weak]
103:def test_a_supported_component_no_slot_accepts_is_still_an_orphan():
104:    main = _comp(284.5, 1e4, {"f": 1e5, "delta_chi2": 1e6, "supported": True})
105:    stray = _comp(289.0, 900.0, {"f": 300.0, "delta_chi2": 5e3, "supported": True})
108:    assert m["__unsupported__"] == []
112:    assert _occupies(_comp(284.5, 0.3, None)), "0.3 > 0: no floor"
113:    assert not _occupies(_comp(284.5, 0.0, None))
130:@pytest.mark.parametrize("support,status", [
131:    ({"f": 50.0, "delta_chi2": 900.0, "supported": True}, "above_floor"),
132:    ({"f": 3.0, "delta_chi2": 40.0, "supported": False}, "present_but_poorly_constrained"),
133:    ({"f": 0.0, "delta_chi2": -1.0, "supported": False}, "not_confidently_detected"),
135:def test_detectability_reads_the_same_verdict(support, status):
137:                           shape_params={}, line_shape=LineShape.GAUSSIAN, support=support)
140:    assert d["basis"] == "support_f_test" and d["support_min_f"] == fitting.SUPPORT_MIN_F
145:    it follows its root, as the server's support check makes a linked
159:    assert comps["main_5_2"].support["follows"] == "main_7_2"
160:    assert comps["main_5_2"].support["supported"] == comps["main_7_2"].support["supported"] is True
161:    assert "follows" not in comps["main_7_2"].support
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
    95	  χ²ᵣ cutoff is exactly the design rule's failure.
    96	* The residual lag-1 autocorrelation IS scale-free (n_eff/n identical at ×1 and
    97	  ×0.1), but real XPS fits are not noise-limited: every real winner has
    98	  structured residuals. As a flag it fires on everything; as a number it
    99	  separates the stress case (0.0075) from real fits (≥ 0.04) only by a factor
   100	  of ~5 and only with a chosen constant.
   101	* So no residual- or χ²ᵣ-based signal distinguishes "the background is wrong"
   102	  from "the lineshape is not perfect" without a chosen cutoff.
   103	
   104	(Also found, pre-existing and unchanged by this unit: the engine's model
   105	selection itself is not rescale-invariant — on main a ×0.1 rescale changes the
   106	winner or the conditional tier on 2 of the 8 real scans (Scan_8 UCl4, Scan_7 8-JT); BIC with Poisson
   107	weights assumes counts.)
   108	
   109	### Real-data gates (`RUN_AUTOFIT_GATE=1`: C 1s, U 4f, B 1s / Cl 2p parity; Bayesian real and U 4f unresolved; candidate-pool real; stress honesty)
   110	
   111	| | main (0bb200b) | this branch |
   112	|---|---|---|
   113	| passed / failed | 26 / 1 | 26 / 1 |
   114	| the failure | `test_candidate_pool_real_gate` ds8 "C1s Scan": the detected shoulder is not in the final model — IDENTICAL peaks on both (the sweep hits its 240 s budget after 3 of 6 candidates); PRE-EXISTING, on local-only held-out data never committed (the datasets were symlinked in from the main checkout for this run) | the same |
   115	| stress honesty | 12 / 12 (old wording) | 12 / 12 (option-A wording, §3) |
   116	
   117	### What F changes on real Find Peaks results (8 committed C 1s scans, gate options, ×1 and ×0.1; both engines run twice on the differing scans — both reproduce themselves 12 / 12, so every difference below is F's)
   118	
   119	Final code (incl. §1 E, re-measured after it — one run changed, Scan_6 ×0.1):
   120	10 of 16 runs unchanged. Changed:
   121	
   122	| scan | scale | main | this branch |
   123	|---|---|---|---|
   124	| 1-GTA Scan_6 (gate anchor) | ×1 | MG2 (conditional), χ²ᵣ 2.04 | AG2+preseed (conditional), χ²ᵣ 3.69 — MG2's lowest slot persistence drops to 0.67: in one of its three refits a component was not supported by the data, so MG2 is no longer "stable" (the 1-count floor had counted that component as present). The C 1s gate still passes (graphite centre, satellite, envelope R) |
   125	| 1-GTA Scan_2 | ×1 | MG2, χ²ᵣ 1.54 | MG3, χ²ᵣ 1.50 |
   126	| 8-JT Scan_7 | ×1 | MG2, χ²ᵣ 5.21 | MG3, χ²ᵣ 5.19 |
   127	| 1-GTA Scan_6 | ×0.1 | MG2 (conditional), χ²ᵣ 0.20 | MG3 (conditional), χ²ᵣ 0.22 |
   128	| 8-JT Scan_5 | ×0.1 | MG3 conditional | MG3 not conditional |
   129	| UCl4 Scan_3 | ×0.1 | MG2 | MG3 |
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

exec
/bin/zsh -lc "rg -n 'role=|role =|main_' autofit/candidates.py autofit/coverage.py | tail -65 && rg -n 'candidate_filter' app.py templates/index.html && nl -ba tests/autofit/test_stress_honesty.py | sed -n '125,148p' && sed -n '2920,2945p' autofit/engine.py && sed -n '235,260p' autofit/methods/ic_model_comparison.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 exited 1 in 0ms:
autofit/candidates.py:464:            role=f"detected_peak_{i}",
autofit/candidates.py:719:        role = f"preseed_curvature_{k}"
autofit/candidates.py:722:            role=role,
autofit/candidates.py:762:            seeded_role=e.get("seeded_role"),

exec
/bin/zsh -lc "rg --files tests/autofit | rg 'full_window|bound|link|absent|method|proposal' && nl -ba tests/autofit/test_stress_honesty.py | sed -n '125,149p' && sed -n '2908,2946p' autofit/engine.py && sed -n '1,145p' autofit/confidence.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
tests/autofit/test_fit_full_window_option.py
tests/autofit/test_bayesian_method.py
tests/autofit/test_methods_seam.py
   125	def test_bg_mismatch_surfaces_loudly():
   126	    """Shirley-shaped truth fit with a straight line: the mismatch must be
   127	    machine-visible, never a silent clean result.
   128	
   129	    Re-stated in the noise-floor unit (2026-09-27; plan
   130	    docs/superpowers/plans/2026-09-27-occupancy-f-test.md §3, option A —
   131	    OWNER DECISION PENDING). Occupancy is now the server's support F test, so
   132	    the third component that only compensated for the wrong background is
   133	    "not supported" and the engine returns the TRUE two-peak model — which the
   134	    old conditional flag depended on NOT happening (the flag rode on that
   135	    compensating component, the README's follow-up 2). What stays visible,
   136	    without any new threshold: the winner is the true model, its χ²ᵣ is
   137	    grossly elevated, and the set-aside better-scoring model is flagged
   138	    (filtered_dominant_alternative — the page's red banner)."""
   139	    case = bg_mismatch_case(seed=61)
   140	    res = _ic(case)
   141	    assert res.diagnostics["winner"] in case.true_candidates
   142	    wc = next(c for c in res.analysis["candidates"]
   143	              if c["name"] == res.diagnostics["winner"])
   144	    assert wc["reduced_chi_sq"] > 10.0
   145	    assert res.diagnostics["filtered_dominant_alternative"] is not None
   146	
   147	
   148	def test_preseed_catches_isolated_missing_peak():
   149	    """Unit F1 (2026-07-07): the isolated unmodeled peak (28% of the main —
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
        )
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

exec
/bin/zsh -lc "rg -n '"'^def test|tmp_path|client|monkeypatch'"' tests/autofit/test_fit_full_window_option.py && rg -n 'fwhm_excess|follow|chain|bound_fixed|proposal' tests/autofit/test_engine.py | head -75 && ls tests/autofit/test_engine*" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
59:def test_default_leaves_curated_bounds_untouched():
68:def test_fit_full_window_defaults_to_false():
79:def test_full_window_widens_only_outer_envelope_for_multi_slot_curated_model():
100:def test_full_window_never_narrows_or_inverts_a_bound_when_roi_is_shifted():
125:def test_full_window_widens_a_single_curated_slot_on_both_sides():
135:def test_full_window_widens_detection_slot_fully_to_roi():
147:def test_full_window_mixed_model_branches_per_slot_not_per_region():
166:def test_full_window_leaves_linked_slot_offset_and_curated_starting_guess_untouched():
189:def test_full_window_no_op_when_x_is_none():
222:def test_default_clamps_an_out_of_window_component_to_the_bound():
237:def test_full_window_lets_the_fit_reach_the_true_out_of_window_position():
252:def test_full_window_stability_does_not_orphan_a_widened_component():
278:def test_full_window_tie_break_never_uses_the_widened_center():
312:def test_proposal_blocking_never_widens_a_populated_slots_territory():
rg: tests/autofit/test_engine.py: IO error for operation on tests/autofit/test_engine.py: No such file or directory (os error 2)
tests/autofit/test_engine_doublet.py

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''; import pytest; raise SystemExit(pytest.main(['\\''-p'\\'','\\''no:cacheprovider'\\'','\\''-s'\\'','\\''-q'\\'','\\''tests/autofit/test_fit_full_window_option.py'\\'','\\''tests/autofit/test_engine_doublet.py'\\'']))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
exec
/bin/zsh -lc "git diff --check main..HEAD && nl -ba autofit/engine.py | sed -n '2375,2415p' && sed -n '115,155p' autofit/grammar.py && rg -n 'SKIP|skip|"'^def test'"' tests/autofit/test_engine_doublet.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-MB5rxQke' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Yql6tMFb' (errno=Operation not permitted)
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
  2411	                 if primary.lmfit_result is not None else np.zeros_like(y))
  2412	    residuals = compute_residual_diagnostics(x, y, y_fit_aug, noise_floor, diagnostic_windows)
  2413	    slot_areas = compute_slot_areas(aug_model, primary, x)
  2414	    absent = _identify_absent_slots(
  2415	        aug_model, stability, slot_areas, primary,
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
    line_shape: LineShape
    fwhm_range: tuple[float, float]

    # Offset-linkage (satellites, chemically-shifted contaminants):
    linked_to: Optional[str] = None
    linked_offset_range: Optional[tuple[float, float]] = None

    # Amplitude-linkage (spin-orbit doublets):  amplitude = parent × ratio.
    # `area_ratio_range` bounds a *relaxed* ratio parameter around the
    # theoretical default (e.g. U 4f 0.75 with bounded relaxation, spec §3.2).
    area_ratio: Optional[float] = None
    area_ratio_range: Optional[tuple[float, float]] = None

    # Generic per-shape-parameter constraints, e.g. (("beta", 0.05),) to fix
    # the DS+G Lorentzian HWHM at the C 1s core-hole lifetime.
    fixed_params: tuple[tuple[str, float], ...] = ()
    param_ranges: tuple[tuple[str, tuple[float, float]], ...] = ()

    # Width-linkage: this slot's fwhm becomes an lmfit expression referencing
    # another parameter name (Biesinger-style shared contamination width).
    fwhm_linked_to: Optional[str] = None

    # Width-INEQUALITY linkage (spin-orbit doublets whose deeper j-hole is
    # Coster-Kronig broadened, e.g. Cl 2p1/2 — adjudication 2026-07-03,
    # docs/autofit/adjudication-decisions.md #7): this slot's width parameter
    # becomes parent_width + a FREE non-negative excess bounded by this
    # range, enforcing width(child) >= width(parent).  Requires
    # ``linked_to``; mutually exclusive with fixing/sharing/expression-
    # linking the width.  An excess pegged at 0 surfaces as a boundary hit,
    # correctly steering selection toward the nested shared-width candidate.
51:def test_fixed_ratio_doublet():
67:def test_relaxed_ratio_doublet_recovers_true_ratio():
79:def test_relaxed_ratio_at_bound_is_boundary_hit():
90:def test_doublet_stability_persistence():
102:def test_proposed_slot_is_phase_unassigned():
119:def test_absent_normalization_is_region_scoped():

 succeeded in 2351ms:
....................
20 passed in 1.97s

codex
The prefix bug is reproduced: a valid two-Gaussian model with roles `main` and `main_extra` counts six parameters for `main` instead of three, changing F from 12.85 (supported) to 6.42 (unsupported). The 22 occupancy and stress tests pass.

The warning dependency is also confirmed. With the mismatch fixture restricted to P1/P2, P2 still has χ²ᵣ ≈ 308.75, but returns `conditional: false`, no filtered-alternative warning, and an empty message. Option A preserves a warning for the tested candidate set; it does not provide an independent mismatch signal.

exec
/bin/zsh -lc "git status --short && sed -n '15576,15620p' templates/index.html && rg -n 'model_selection_warning|selection_warning|autocorr_flag' templates/index.html autofit/methods/ic_model_comparison.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Xz1Y8Hkt' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-t6l1mOEt' (errno=Operation not permitted)
?? docs/autofit/codex/occupancy_f_test_verdict_runA.md
?? docs/autofit/codex/occupancy_f_test_verdict_runB.md
?? "docs/autofit/test_data/7 - GTA-2-66 U-naph and COT.DATA"
?? "docs/autofit/test_data/8 GTA-2-46ii U-naph and XeF2, graphite 40%, powder, Cu, 0.4eV, 400 um.DATA"
?? docs/autofit/test_data/Ugly_Fe_2p.spec.json
?? docs/autofit/test_data/Ugly_Fe_2p_2.spec.json
// plain words — a CONDITIONAL result still reads as conditional here.
function _fpPlainMessage(body) {
  // The honest "structure known, no fittable features" stub (app.py's
  // early-return branch, _build_analyze_payload) is a COMPLETELY
  // DIFFERENT payload shape from a normal result — it has no
  // `analysis` key at all (a normal payload always does, success or
  // failure, mixed regions or not). That is what distinguishes it from
  // an ordinary result that merely HAS a non-empty structural_only
  // array — e.g. a mixed curated+structural request that still
  // succeeded with real peaks, or one that failed for an unrelated
  // reason (Codex-caught, round 2: a bare non-empty-array check
  // misclassified both of those as the stub).
  if (body.analysis === undefined && Array.isArray(body.structural_only)
      && body.structural_only.length) {
    return 'No fittable peaks were found in this window for ' +
      body.structural_only.join(', ') + ' — there’s no cited reference ' +
      'data for this region yet, and nothing stood out in your data ' +
      'either. Try widening the window, or double-check the region selection.';
  }
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
autofit/methods/ic_model_comparison.py:288:            "autocorr_flag": bool(r.residuals.autocorr_flag),
templates/index.html:16329:  if (a.model_selection_warning || a.selection_warning)
templates/index.html:16330:    flags.push(_fpBanner(_fpEsc(a.model_selection_warning || a.selection_warning), '#e0a030'));

codex
1. **MAJOR — Parameter-prefix overlap changes the support verdict.** [autofit/engine.py:684](/Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test/autofit/engine.py:684)

   `n.startswith(prefix)` counts another component’s parameters when roles are, for example, `main` and `main_extra`. `s_main_extra_*` also starts with `s_main_`.

   Reproduced with two Gaussian components: baseline 10,000, amplitudes 150/10,000, widths 1.2, and deterministic noise (seed 42). The first component has three free parameters, but this code counts six: **correct F = 12.8475, supported; branch F = 6.4238, unsupported**. A supported peak consequently becomes an empty slot and escapes orphan reporting.

   Count parameters by unambiguous slot ownership, including auxiliary offset/ratio/excess parameters. Add a regression with overlapping role prefixes.

2. **MAJOR — Option A does not close the required independent mismatch-warning follow-up.** [tests/autofit/test_stress_honesty.py:145](/Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test/tests/autofit/test_stress_honesty.py:145)

   The replacement assertion still depends on P3: `filtered_dominant_alternative` requires a better-scoring candidate that was evaluated and filtered.

   Reproduced with `bg_mismatch_case(seed=61)` and `candidate_filter=["P1", "P2"]`: P2 wins with **χ²ᵣ = 308.7466**, `conditional=False`, `filtered_dominant_alternative=None`, and an empty message. The page’s plain-language result consequently says the model passed every check cleanly.

   This P1/P2 limitation predates the branch; the finding is an **unclosed requirement**, not a newly introduced regression in that configuration. Option A honestly records the full fixture’s outcome, but weakens the contract instead of providing the README’s requested independent signal. The pending owner decision must explicitly accept that narrower contract, or the follow-up remains unfinished.

3. **MINOR — The scale-dependence explanation incorrectly implicates the ranking BIC*.** [docs/superpowers/plans/2026-09-27-occupancy-f-test.md:136](/Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test/docs/superpowers/plans/2026-09-27-occupancy-f-test.md:136)

   Ranking uses `n·log(RSS/n) + k·log(n)`, not the separately reported weighted-χ² BIC. For fixed candidates and correspondingly scaled fits, multiplying intensities by `c` adds the same `2n·log(c)` to every score; **BIC* differences remain unchanged**.

   The reported 2/8 → 6/8 outcome changes deserve investigation, but this explanation does not establish their cause. Correct the distinction and trace candidate generation, optimization, and persistence before attributing those changes to ranking.

The central wiring otherwise checks out: support uses the producing fit’s data, background-subtracted best fit, weights, and total parameter count; `SUPPORT_MIN_F` is reused; the sole production slot-map iterator removes `__unsupported__`; Bayesian selection does not consume this occupancy path.

**Validation:** 42 tests passed across occupancy, stress honesty, full-window, and doublet suites. `git diff --check` passed. Full real-data and browser gates were not rerun. No files changed.

**VERDICT: NO-GO**
tokens used
95,714
1. **MAJOR — Parameter-prefix overlap changes the support verdict.** [autofit/engine.py:684](/Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test/autofit/engine.py:684)

   `n.startswith(prefix)` counts another component’s parameters when roles are, for example, `main` and `main_extra`. `s_main_extra_*` also starts with `s_main_`.

   Reproduced with two Gaussian components: baseline 10,000, amplitudes 150/10,000, widths 1.2, and deterministic noise (seed 42). The first component has three free parameters, but this code counts six: **correct F = 12.8475, supported; branch F = 6.4238, unsupported**. A supported peak consequently becomes an empty slot and escapes orphan reporting.

   Count parameters by unambiguous slot ownership, including auxiliary offset/ratio/excess parameters. Add a regression with overlapping role prefixes.

2. **MAJOR — Option A does not close the required independent mismatch-warning follow-up.** [tests/autofit/test_stress_honesty.py:145](/Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test/tests/autofit/test_stress_honesty.py:145)

   The replacement assertion still depends on P3: `filtered_dominant_alternative` requires a better-scoring candidate that was evaluated and filtered.

   Reproduced with `bg_mismatch_case(seed=61)` and `candidate_filter=["P1", "P2"]`: P2 wins with **χ²ᵣ = 308.7466**, `conditional=False`, `filtered_dominant_alternative=None`, and an empty message. The page’s plain-language result consequently says the model passed every check cleanly.

   This P1/P2 limitation predates the branch; the finding is an **unclosed requirement**, not a newly introduced regression in that configuration. Option A honestly records the full fixture’s outcome, but weakens the contract instead of providing the README’s requested independent signal. The pending owner decision must explicitly accept that narrower contract, or the follow-up remains unfinished.

3. **MINOR — The scale-dependence explanation incorrectly implicates the ranking BIC*.** [docs/superpowers/plans/2026-09-27-occupancy-f-test.md:136](/Users/skyefortier/xps-app/.claude/worktrees/fix-occupancy-f-test/docs/superpowers/plans/2026-09-27-occupancy-f-test.md:136)

   Ranking uses `n·log(RSS/n) + k·log(n)`, not the separately reported weighted-χ² BIC. For fixed candidates and correspondingly scaled fits, multiplying intensities by `c` adds the same `2n·log(c)` to every score; **BIC* differences remain unchanged**.

   The reported 2/8 → 6/8 outcome changes deserve investigation, but this explanation does not establish their cause. Correct the distinction and trace candidate generation, optimization, and persistence before attributing those changes to ranking.

The central wiring otherwise checks out: support uses the producing fit’s data, background-subtracted best fit, weights, and total parameter count; `SUPPORT_MIN_F` is reused; the sole production slot-map iterator removes `__unsupported__`; Bayesian selection does not consume this occupancy path.

**Validation:** 42 tests passed across occupancy, stress honesty, full-window, and doublet suites. `git diff --check` passed. Full real-data and browser gates were not rerun. No files changed.

**VERDICT: NO-GO**
