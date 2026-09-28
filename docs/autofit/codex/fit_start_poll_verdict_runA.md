OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0e1e8-681b-72a1-8da6-4050845bc821
--------
user
Review unit 2 (long fits via start-then-poll): branch fix-fit-start-poll, which is stacked on fix-acceptance-holes (F2, deploying first). Review git diff fix-acceptance-holes..HEAD (app.py, fitting.py, templates/index.html, tests/test_fit_start_poll.py, tests/js/fit_start_poll.test.js, tests/js/fit_acceptance.test.js, tests/js/stale_statistics.test.js, tests/js/per_tab_state.test.js, scripts/public_fit_poll_check.py, docs/superpowers/plans/2026-09-27-long-fits-start-poll.md). Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

OWNER'S BRIEF (verbatim): "/api/fit/start returns a job id; the fit runs in the background; the page polls. Reuse Find Peaks' job infrastructure. Cover Run Fit and Auto-Fit. Requirements: the async-ownership rule (capture tab and inputs before the first await; discard results for an edited model or switched tab); F1's fit key and statistics binding unchanged; seeding unchanged — a polled fit gives the same result as today's; cancellation, so abandoned or re-run fits stop consuming workers. ACCEPTANCE: basinhopping on the five largest C 1s models completes through the poll path; no single HTTP request in the poll path lasts longer than a few seconds, so none can hit the ~100 s ceiling; DS+G and DE results unchanged. No interim 524 message."

Context: the public URL (Cloudflare tunnel) ends a proxied request at ~100 s (HTTP 524; 88 s passed, 125 s failed): docs/findings/2026-09-26-public-request-ceiling.md. Production is gunicorn --workers 4 --timeout 300, SYNC workers.

PLAN SECTIONS 1-3 (design, sites table, acceptance), verbatim:

## 1. Design

- **Server.** `/api/fit/start` validates EXACTLY as `/api/fit` does (the
  validation is extracted into one function both routes call, so every 400 /
  404 is still immediate and word-for-word the same), writes a job record
  with Find Peaks' helpers (`_write_job_progress`, `_job_progress_path`,
  `_sweep_expired_jobs`: an atomic JSON file under the upload folder, so a poll
  landing on any gunicorn worker reads it), starts a daemon thread that calls
  the SAME `fitting.run_fit(...)` with the SAME arguments, and returns
  `{job_id}` 202. On completion the record holds `status: done` and
  `result` = exactly the body `/api/fit` returns; on a `ValueError` /
  `RuntimeError` / other exception the record holds `status: error`, the same
  message and the same HTTP status the synchronous route would have
  returned. `/api/fit/progress/<id>` reads the record (short); `/api/fit/cancel/<id>`
  marks it cancelled (short). The synchronous `/api/fit` stays for scripts,
  tests and the Python twins.
- **Heartbeat.** A second daemon thread per job rewrites a heartbeat time
  every 2 s while the fit thread is alive; a poll reports `heartbeat_age`. A
  killed or recycled worker takes both threads down, the heartbeat stops, and
  the page reports the fit as lost instead of polling forever.
- **Cancellation.** `run_fit` gains an optional `cancel` callable, NOT part
  of `fit_kws` (so never hashed into the seed); when given, every
  `model.fit` in fitting.py receives an `iter_cb` that returns True (lmfit's
  abort) once `cancel()` is true, checked at most every 0.25 s. Without it the
  calls are made exactly as today (no `iter_cb` argument at all). The job's
  cancel condition: a cancel marker written by `/api/fit/cancel`, OR no poll
  for 180 s (an abandoned tab, a closed laptop; above the ~1-minute timer throttling browsers apply to a hidden tab, so switching browser tabs does not lose the fit). A cancelled job's record is
  `status: cancelled`.
- **Page.** One helper `_runServerFit(fitReq, { owner, ctxAtRequest, signal })`
  = start → poll (≈ 0.5 s) → the reply body, with the ownership checks INSIDE
  the loop: a switched tab or an edited model cancels the job and discards,
  exactly as today's checks after the single request did. Transport
  semantics kept: a failed START is a transport failure (local fallback as
  today); a poll that fails in transport is retried, and only several in a
  row become a transport failure; a lost heartbeat is a failed fit. The body
  of the final poll is read by F2's `_readFitReply` rules (a reply that is
  read but not JSON is the server's failed fit). `pagehide` sends
  `navigator.sendBeacon('/api/fit/cancel/<id>')` for a running job.

## 2. Sites

Every page path that sends a fit to the server, and every server path it
reaches (enumerated: `grep "fetch('/api/"` on the page — only Run Fit and
Auto-Fit post to `/api/fit`; Find Peaks already starts and polls
`/api/analyze`; Batch Fit is local; upload / parse-vgd / reference / meta are
short):

| # | site | before | after |
|---|---|---|---|
| S1 | app.py `_prepare_fit_request` (new) | the validation inline in `/api/fit` | the SAME lines, moved verbatim (early `return _err(...)` → `return None, _err(...)`); called by `/api/fit` and `/api/fit/start` |
| S2 | app.py `_run_fit_outcome` (new) | the exception → status mapping inline in `/api/fit` | the same mapping (ValueError 400 with its message; RuntimeError 422 "Fit failed — see server log"; other 500), returning `(status, body)`; `FitCancelled` → `(None, None)` |
| S3 | app.py `/api/fit` (synchronous) | validate + run_fit + map | S1 + S2: unchanged behaviour (kept for scripts, tests, the Python twins) |
| S4 | app.py `/api/fit/start` (new) | — | S1 (immediate identical 400 / 404), then a job: 202 `{job_id}` |
| S5 | app.py `/api/fit/progress/<id>` (new) | — | reads the record, touches `<id>.polled`, adds `heartbeat_age_sec`; 400 malformed id, 404 unknown |
| S6 | app.py `/api/fit/cancel/<id>` (new) | — | writes `<id>.cancel` (any worker) |
| S7 | app.py `_fit_job_*`, `_sweep_fit_job_markers` (new) | Find Peaks' `_write_job_progress` / `_job_progress_path` / `_sweep_expired_jobs` | the same record files and TTL sweep; fit records are written WITHOUT sanitising (a NaN must reach the page, which refuses it — F2); a fit thread + a heartbeat thread; markers removed on completion, swept after the TTL otherwise |
| S8 | fitting.py `run_fit(cancel=)`, `_CANCEL`, `_cancel_kw`, `FitCancelled`; the 7 `model.fit` calls | no cancellation | a thread-local cancel callable; each of the 7 calls gets `**_cancel_kw()` (`{}` without a callable: the synchronous calls are made exactly as before; `{iter_cb}` inside a job) |
| P1 | page `_serverFitJob`, `_cancelFitJob`, `_fitHttpError`, `_runningFitJobs`, pagehide beacon (new) | — | start → poll every 0.5 s → the record's `result`; ownership inside the loop; transport retries; lost heartbeat; F2's `_readFitReply` on every body |
| P2 | page `runFit` (incl. "Use this solution": `runFit({startPeaks})`) | one POST `/api/fit`, ownership checked after it returned | `_serverFitJob`; the same two discard messages (tab / model); `backendResult` and everything after it unchanged; F1's key stamping unchanged; a failed START is still a transport failure → the local fallback (and F1's "edited mid-fit → no local fit" rule still applies) |
| P3 | page `runAutoFitC1sGraphite` | one POST `/api/fit` under a 2-minute AbortController | `_serverFitJob` with the same controller (an abort cancels the job and keeps "exceeded the 2-minute timeout"); the tab / model discards inside the loop, then rollback, as before |
| N  | not changed: Batch Fit (local only), Find Peaks (own job), `/api/analyze`, scripts and `autofit/*` calling `fitting.run_fit` directly | | |

## 3. Acceptance (dev server only; no deploy tonight)

Dev gunicorn on :5151 with production's settings (`--workers 4 --timeout
300`), through `scripts/public_fit_poll_check.py` pointed at
http://127.0.0.1:5151 (the page's request: basinhopping, `n_perturb: 3`,
`n_starts: 3`; upload → start → poll every 0.5 s), the five largest committed
C 1s models run IN PARALLEL (with a full pytest run on the same machine, so
wall times are inflated):

| target | components | fit wall time | requests | longest request | χ²ᵣ (= synchronous measurement) | verdict |
|---|---|---|---|---|---|---|
| 496c4edd97af | 6 | 213 s | 383 | 0.18 s | 19.0227 | PASS |
| d2bd62d2f976 | 6 | 231 s | 415 | 0.27 s | 2.5705 | PASS |
| edf39ecb66ce | 7 | 313 s | 578 | 0.21 s | 1.3166 | PASS |
| 8b4c2f656a80 | 6 | 409 s | 764 | 0.26 s | 2.5074 | PASS |
| 0a5f464daf3d | 6 | 414 s | 775 | 0.28 s | 1.3981 | PASS |

Every fit longer than both the public ceiling (~100 s) and gunicorn's 300 s
completed; no single request exceeded 0.28 s.

Results unchanged — the page's own request captured at `/api/fit/start` and
replayed synchronously at `/api/fit` (committed UCl4-graphite C1s Scan):

| model / method | polled χ²ᵣ | synchronous χ²ᵣ | seed | max relative parameter difference |
|---|---|---|---|---|
| DS+G graphite + GL lines, Trust-Region | 4.323666288 | 4.323666301 | same | 3.9e-4 |
| the same, differential evolution | 4.323666286 | 4.323666286 | same | 2.6e-14 |

The Trust-Region difference is Trust-Region's documented run-to-run jitter
(BLAS alignment; CLAUDE.md "Reproducibility"), not the job path: with and
without the cancel hook on six committed targets, Levenberg-Marquardt is
byte-identical 6/6 and Trust-Region differs with the hook only where two
plain runs of the same request differ too (`scratchpad` probe; reproduced in
`tests/test_fit_start_poll.py`: byte-identical Levenberg-Marquardt through
the poll path).


TRY TO BREAK
a. Server: is _prepare_fit_request the verbatim validation (diff the old inline code); every early return; a validation error that used to be 404/400 still is on both routes. Threads in a sync gunicorn worker: does a long CPU-bound fit thread starve the worker's own request loop or heartbeat (gunicorn's worker heartbeat, its 300 s timeout — can gunicorn kill a worker whose MAIN thread is idle but a background thread is running 300+ s?); max concurrent jobs (unbounded threads? a student pressing Run Fit repeatedly); memory; the record written by two threads (fit + heartbeat) — lost updates, the final record overwritten by a late heartbeat; the tmp-file naming; a poll between os.replace calls; markers left behind; the TTL sweep deleting a RUNNING job's record (FIND PEAKS' TTL is 3600 s — a 20-minute fit?); cross-worker visibility.
b. Cancellation: every minimisation reached (the 7 model.fit sites — any lmfit path that ignores iter_cb, e.g. covariance / numdifftools, basinhopping's inner minimizer, least_squares' own loop); the abandon rule (180 s without a poll, chosen above Chrome's ~1-minute timer throttling of hidden tabs) — can a student who switches BROWSER tabs, or whose laptop sleeps briefly, still lose a fit they are waiting for; is 180 s long enough / short enough?; FitCancelled vs a real error; a cancel arriving after completion.
c. Seeding/identity: the sync path makes byte-identical model.fit calls (no iter_cb); the job path adds iter_cb — can that change any numeric result (lmfit behaviour when iter_cb is set, e.g. extra evaluations or a different code path)? the seed (cancel is not in fit_kws).
d. Page: every await in runFit / Auto-Fit and the ownership checks (tab captured before the first await; ctxAtRequest; the checks now INSIDE the loop and still after); the transport classification (a failed start → local fallback as before; poll retries; a 404 progress after a server restart); F2's _readFitReply on poll bodies; F1's stamping; the adoption path runFit({startPeaks}); Auto-Fit's 2-minute controller; pagehide beacon; _runningFitJobs; a second Run Fit while one is running (is the button disabled? if not, two jobs for one tab, which wins?).
e. Tests: real and non-vacuous; the adapters in the old sandboxes keep those tests testing what they tested.
f. Docs vs code.

Finish with VERDICT: GO or VERDICT: NO-GO.
codex
I’ll compare the branch with F2, trace cancellation and browser ownership, and run focused checks where the read-only environment allows. I’ll return ranked findings and a verdict within this run.
exec
/bin/zsh -lc "pwd; git status --short; rg --files -g 'AGENTS.md' -g 'CLAUDE.md'; git diff --stat fix-acceptance-holes..HEAD" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-adcPIUNg' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-tQwpaLrq' (errno=Operation not permitted)
?? docs/autofit/codex/fit_start_poll_verdict_runA.md
?? docs/autofit/codex/fit_start_poll_verdict_runB.md
CLAUDE.md
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-IMr4IrKQ' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-UEMeOjnM' (errno=Operation not permitted)
 CLAUDE.md                                          |  25 ++
 app.py                                             | 373 ++++++++++++++++-----
 .../autofit/codex/fit_start_poll_review_prompt.txt | 116 +++++++
 .../plans/2026-09-27-long-fits-start-poll.md       | 167 +++++++++
 fitting.py                                         |  81 ++++-
 scripts/public_fit_poll_check.py                   |  87 +++++
 templates/index.html                               | 182 ++++++++--
 tests/js/fit_acceptance.test.js                    |  34 +-
 tests/js/fit_start_poll.test.js                    | 143 ++++++++
 tests/js/per_tab_state.test.js                     |   1 +
 tests/js/stale_statistics.test.js                  |  31 +-
 tests/test_browser_bg_window_request.py            |   2 +-
 tests/test_browser_endpoint_avg_default.py         |   2 +-
 tests/test_fit_start_poll.py                       | 175 ++++++++++
 14 files changed, 1280 insertions(+), 139 deletions(-)

exec
/bin/zsh -lc 'cat CLAUDE.md; git diff fix-acceptance-holes..HEAD -- app.py fitting.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
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
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-W2Vim3O9' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-OWDJgbln' (errno=Operation not permitted)
diff --git a/app.py b/app.py
index f689d5a..3271469 100644
--- a/app.py
+++ b/app.py
@@ -58,6 +58,113 @@ MAX_N_PERTURB = 100
 # — no background thread or scheduler.
 SESSION_TTL_DAYS = 7
 
+# ─────────────────────────────────────────────────────────────────────────────
+# /api/fit request handling, shared by /api/fit and /api/fit/start (unit 2)
+# ─────────────────────────────────────────────────────────────────────────────
+
+def _prepare_fit_request(app, body):
+    """/api/fit's request validation, shared VERBATIM with /api/fit/start
+    (unit 2, 2026-09-27): every 400 / 404 is immediate and word-for-word the
+    same on both routes. Returns ``(kwargs_for_run_fit, None)`` or
+    ``(None, error_response)``."""
+    session_id = body.get("session_id", "")
+    _validate_session_id(session_id)
+
+    try:
+        energy, counts = _load_session(session_id, app.config["UPLOAD_FOLDER"])
+    except KeyError:
+        return None, _err(f"Session '{session_id}' not found", 404)
+
+    # Background config
+    bg_cfg = body.get("background", {})
+    bg_method = bg_cfg.get("method", "shirley")
+    bg_start = _parse_int(bg_cfg.get("start_idx"), 0, len(energy))
+    bg_end = _parse_int(bg_cfg.get("end_idx"), 0, len(energy), default=len(energy))
+    # Clean 400 for malformed endpoint_avg instead of a 500 (audit F9).
+    try:
+        endpoint_avg = max(1, int(bg_cfg.get("endpoint_avg", 1)))
+    except (TypeError, ValueError):
+        return None, _err("endpoint_avg must be an integer")
+    manual_bg = bg_cfg.get("manual_bg")
+
+    # Peak specs
+    peak_specs = body.get("peaks", [])
+    if not peak_specs:
+        return None, _err("'peaks' list is empty – provide at least one peak")
+
+    # Validate peak ids are unique
+    ids = [p.get("id") for p in peak_specs]
+    if len(ids) != len(set(ids)):
+        return None, _err("Duplicate peak ids found – each peak must have a unique 'id'")
+
+    _ALLOWED_METHODS = {
+        "leastsq", "least_squares", "nelder",
+        "differential_evolution", "basinhopping",
+    }
+    fit_method = body.get("fit_method", "leastsq")
+    if fit_method not in _ALLOWED_METHODS:
+        return None, _err(f"Unknown fit_method '{fit_method}'")
+
+    # Bounded, type-checked n_perturb (audit F7; also covers the F9
+    # ValueError-on-bad-input case for this field). Reject out-of-range or
+    # non-integer values with a clean 400 instead of a 500 or a worker hang.
+    try:
+        n_perturb = int(body.get("n_perturb", 5))
+    except (TypeError, ValueError):
+        return None, _err(f"n_perturb must be an integer between 0 and {MAX_N_PERTURB}")
+    if n_perturb < 0 or n_perturb > MAX_N_PERTURB:
+        return None, _err(f"n_perturb must be between 0 and {MAX_N_PERTURB}")
+
+    # Scattered-starts check (optional; the page sends 3). Same clean-400
+    # treatment as n_perturb; run_fit validates again for other callers.
+    n_starts = body.get("n_starts", 0)
+    if isinstance(n_starts, bool) or not isinstance(n_starts, int) or not 0 <= n_starts <= fitting.MAX_N_STARTS:
+        return None, _err(f"n_starts must be an integer between 0 and {fitting.MAX_N_STARTS}")
+    # "Is this component required?" (one extra fit; Auto-Fit asks for its anchor)
+    require_component = body.get("require_component")
+    if require_component is not None and not isinstance(require_component, (str, int)):
+        return None, _err("require_component must be a peak id")
+    return dict(
+        energy=energy,
+        counts=counts,
+        peak_specs=peak_specs,
+        background_method=bg_method,
+        bg_start_idx=bg_start,
+        bg_end_idx=bg_end,
+        charge_shift_ev=0.0,
+        fit_kws={"method": fit_method},
+        manual_bg=manual_bg,
+        n_perturb=n_perturb,
+        endpoint_avg=endpoint_avg,
+        n_starts=n_starts,
+        require_component=require_component,
+    ), None
+
+
+def _run_fit_outcome(app, fit_args, cancel=None):
+    """Run the fit; return ``(status_code, body)`` exactly as /api/fit has
+    always answered (a ValueError is our own validation, 400; a RuntimeError
+    a solver-internal failure, 422 without library internals; anything else
+    500). A cancelled job returns ``(None, None)``."""
+    try:
+        result = fitting.run_fit(**fit_args, cancel=cancel)
+    except fitting.FitCancelled:
+        return None, None
+    except ValueError as exc:
+        # Our own validation: unknown shape/method, self/circular constraint,
+        # "Master peak not found", bad numeric field, etc. (audit F10/F11).
+        return 400, {"error": str(exc)}
+    except RuntimeError:
+        # Solver-internal failure (e.g. lmfit non-convergence). Log the
+        # detail; return a generic 422 that leaks no library internals.
+        app.logger.exception("Fit failed")
+        return 422, {"error": "Fit failed — see server log for details."}
+    except Exception:
+        app.logger.exception("Unexpected fitting error")
+        return 500, {"error": "Internal fitting error — see server log."}
+    return 200, result
+
+
 # ─────────────────────────────────────────────────────────────────────────────
 # Application factory
 # ─────────────────────────────────────────────────────────────────────────────
@@ -443,6 +550,129 @@ def _sweep_expired_jobs(upload_folder: str) -> None:
             pass
 
 
+# ── Fit jobs (unit 2, 2026-09-27) ────────────────────────────────────────────
+# Records are the Find Peaks job files (<job>.job.json, the same TTL sweep);
+# two small markers beside each: <job>.cancel (written by /api/fit/cancel,
+# any worker) and <job>.polled (touched by every poll). The fit thread's
+# cancel condition: the cancel marker exists, OR no poll for
+# FIT_JOB_ABANDON_SEC (a closed tab, a sleeping laptop; 180 s, above the ~1 min timer throttling browsers apply to hidden tabs).
+FIT_JOB_ABANDON_SEC = 180   # > Chrome's 1-minute timer throttling in a hidden tab: a student who switches browser tabs keeps the fit
+FIT_JOB_HEARTBEAT_SEC = 2.0
+
+
+def _fit_job_marker(job_id: str, upload_folder: str, kind: str) -> Path:
+    return Path(upload_folder) / f"{job_id}.{kind}"
+
+
+def _fit_job_write(job_id: str, upload_folder: str, data: dict) -> None:
+    """Atomic like _write_job_progress, but WITHOUT sanitising: a result's
+    NaN / Infinity reach the page exactly as /api/fit sends them (the page's
+    _readFitReply refuses them as a failed fit — unit F2)."""
+    path = _job_progress_path(job_id, upload_folder)
+    tmp = path.with_suffix(f".{threading.get_ident()}.tmp")
+    try:
+        tmp.write_text(json.dumps(data, allow_nan=True))
+        os.replace(tmp, path)
+    except OSError:
+        logging.getLogger(__name__).exception("failed to write fit job %s", job_id)
+
+
+def _fit_job_read(job_id: str, upload_folder: str):
+    path = _job_progress_path(job_id, upload_folder)
+    if not path.exists():
+        return None
+    try:
+        _fit_job_marker(job_id, upload_folder, "polled").touch()
+    except OSError:
+        pass
+    try:
+        data = json.loads(path.read_text())
+    except (OSError, ValueError):
+        data = {"status": "running", "elapsed_sec": 0.0}      # a read racing the first write
+    hb = data.get("heartbeat")
+    data["heartbeat_age_sec"] = round(time.time() - hb, 1) if isinstance(hb, (int, float)) else None
+    return data
+
+
+def _sweep_fit_job_markers(upload_folder: str) -> None:
+    """Markers left by a job whose worker died (they are removed when a job
+    finishes): same TTL as the job records, never raises."""
+    cutoff = time.time() - _ANALYZE_JOB_TTL_SEC
+    for pattern in ("*.cancel", "*.polled"):
+        try:
+            for m in Path(upload_folder).glob(pattern):
+                try:
+                    if m.stat().st_mtime < cutoff:
+                        m.unlink(missing_ok=True)
+                except OSError:
+                    pass
+        except OSError:
+            pass
+
+
+def _fit_job_cancel(job_id: str, upload_folder: str) -> None:
+    try:
+        _fit_job_marker(job_id, upload_folder, "cancel").touch()
+    except OSError:
+        pass
+
+
+def _fit_job_start(job_id: str, upload_folder: str, fit_args: dict, run) -> None:
+    """Start the fit thread and its heartbeat thread. ``run(fit_args, cancel)``
+    returns ``(status, body)``; ``(None, None)`` means cancelled."""
+    started = time.time()
+    lock = threading.Lock()
+    rec = {"status": "running", "elapsed_sec": 0.0, "heartbeat": started}
+    _fit_job_write(job_id, upload_folder, rec)
+    _fit_job_marker(job_id, upload_folder, "polled").touch()
+    cancel_path = _fit_job_marker(job_id, upload_folder, "cancel")
+    polled_path = _fit_job_marker(job_id, upload_folder, "polled")
+    finished = threading.Event()
+
+    def cancelled() -> bool:
+        if cancel_path.exists():
+            return True
+        try:
+            return time.time() - polled_path.stat().st_mtime > FIT_JOB_ABANDON_SEC
+        except OSError:
+            return False
+
+    def heartbeat() -> None:
+        while not finished.wait(FIT_JOB_HEARTBEAT_SEC):
+            with lock:
+                if rec["status"] != "running":
+                    return
+                rec["heartbeat"] = time.time()
+                rec["elapsed_sec"] = round(time.time() - started, 1)
+                _fit_job_write(job_id, upload_folder, rec)
+
+    def worker() -> None:
+        try:
+            status, body = run(fit_args, cancelled)
+        except Exception as exc:                       # the record must always leave "running"
+            logging.getLogger(__name__).exception("fit job %s crashed", job_id)
+            status, body = 500, {"error": "Internal fitting error — see server log."}
+        with lock:
+            rec["elapsed_sec"] = round(time.time() - started, 1)
+            rec["heartbeat"] = time.time()
+            if status is None or cancel_path.exists():
+                rec.update(status="cancelled")
+            elif status == 200:
+                rec.update(status="done", result=body)
+            else:
+                rec.update(status="error", error=body.get("error"), http_status=status)
+            finished.set()
+            _fit_job_write(job_id, upload_folder, rec)
+        for kind in ("cancel", "polled"):
+            try:
+                _fit_job_marker(job_id, upload_folder, kind).unlink(missing_ok=True)
+            except OSError:
+                pass
+
+    threading.Thread(target=worker, daemon=True, name=f"fit-{job_id[:8]}").start()
+    threading.Thread(target=heartbeat, daemon=True, name=f"fit-hb-{job_id[:8]}").start()
+
+
 def _require_json(f):
     """Decorator: return 400 if request body is not valid JSON."""
     @wraps(f)
@@ -779,94 +1009,13 @@ def _register_routes(app: Flask) -> None:
         }
         """
         body = request.get_json()
-        session_id = body.get("session_id", "")
-        _validate_session_id(session_id)
-
-        try:
-            energy, counts = _load_session(session_id, app.config["UPLOAD_FOLDER"])
-        except KeyError:
-            return _err(f"Session '{session_id}' not found", 404)
-
-        # Background config
-        bg_cfg = body.get("background", {})
-        bg_method = bg_cfg.get("method", "shirley")
-        bg_start = _parse_int(bg_cfg.get("start_idx"), 0, len(energy))
-        bg_end = _parse_int(bg_cfg.get("end_idx"), 0, len(energy), default=len(energy))
-        # Clean 400 for malformed endpoint_avg instead of a 500 (audit F9).
-        try:
-            endpoint_avg = max(1, int(bg_cfg.get("endpoint_avg", 1)))
-        except (TypeError, ValueError):
-            return _err("endpoint_avg must be an integer")
-        manual_bg = bg_cfg.get("manual_bg")
-
-        # Peak specs
-        peak_specs = body.get("peaks", [])
-        if not peak_specs:
-            return _err("'peaks' list is empty – provide at least one peak")
-
-        # Validate peak ids are unique
-        ids = [p.get("id") for p in peak_specs]
-        if len(ids) != len(set(ids)):
-            return _err("Duplicate peak ids found – each peak must have a unique 'id'")
-
-        _ALLOWED_METHODS = {
-            "leastsq", "least_squares", "nelder",
-            "differential_evolution", "basinhopping",
-        }
-        fit_method = body.get("fit_method", "leastsq")
-        if fit_method not in _ALLOWED_METHODS:
-            return _err(f"Unknown fit_method '{fit_method}'")
-
-        # Bounded, type-checked n_perturb (audit F7; also covers the F9
-        # ValueError-on-bad-input case for this field). Reject out-of-range or
-        # non-integer values with a clean 400 instead of a 500 or a worker hang.
-        try:
-            n_perturb = int(body.get("n_perturb", 5))
-        except (TypeError, ValueError):
-            return _err(f"n_perturb must be an integer between 0 and {MAX_N_PERTURB}")
-        if n_perturb < 0 or n_perturb > MAX_N_PERTURB:
-            return _err(f"n_perturb must be between 0 and {MAX_N_PERTURB}")
-
-        # Scattered-starts check (optional; the page sends 3). Same clean-400
-        # treatment as n_perturb; run_fit validates again for other callers.
-        n_starts = body.get("n_starts", 0)
-        if isinstance(n_starts, bool) or not isinstance(n_starts, int) or not 0 <= n_starts <= fitting.MAX_N_STARTS:
-            return _err(f"n_starts must be an integer between 0 and {fitting.MAX_N_STARTS}")
-        # "Is this component required?" (one extra fit; Auto-Fit asks for its anchor)
-        require_component = body.get("require_component")
-        if require_component is not None and not isinstance(require_component, (str, int)):
-            return _err("require_component must be a peak id")
-
-        try:
-            result = fitting.run_fit(
-                energy=energy,
-                counts=counts,
-                peak_specs=peak_specs,
-                background_method=bg_method,
-                bg_start_idx=bg_start,
-                bg_end_idx=bg_end,
-                charge_shift_ev=0.0,
-                fit_kws={"method": fit_method},
-                manual_bg=manual_bg,
-                n_perturb=n_perturb,
-                endpoint_avg=endpoint_avg,
-                n_starts=n_starts,
-                require_component=require_component,
-            )
-        except ValueError as exc:
-            # Our own validation: unknown shape/method, self/circular constraint,
-            # "Master peak not found", bad numeric field, etc. (audit F10/F11).
-            return _err(str(exc))
-        except RuntimeError:
-            # Solver-internal failure (e.g. lmfit non-convergence). Log the
-            # detail; return a generic 422 that leaks no library internals.
-            app.logger.exception("Fit failed")
-            return _err("Fit failed — see server log for details.", 422)
-        except Exception:
-            app.logger.exception("Unexpected fitting error")
-            return _err("Internal fitting error — see server log.", 500)
-
-        return jsonify(result)
+        fit_args, error = _prepare_fit_request(app, body)
+        if error is not None:
+            return error
+        status, out = _run_fit_outcome(app, fit_args)
+        if status != 200:
+            return _err(out["error"], status)
+        return jsonify(out)
 
     # ── Autofit analyze (opt-in Find Peaks; STRICTLY ADDITIVE — the manual
     #    /api/fit path above is untouched) ──────────────────────────────────
@@ -1060,6 +1209,54 @@ def _register_routes(app: Flask) -> None:
                     "message": "starting analysis…"}
         return jsonify(data)
 
+    # ── Long fits via start-then-poll (unit 2, 2026-09-27) ───────────────────
+    # The public URL ends a proxied request at ~100 s (Cloudflare 524; 88 s
+    # passed, 125 s failed); basinhopping on the large C 1s models takes 3–4
+    # minutes. The fit runs in a background thread on Find Peaks' job
+    # infrastructure (an atomic JSON record under the upload folder, readable
+    # by whichever gunicorn worker serves a poll); every HTTP request is short.
+    # The record: {status: running|done|error|cancelled, elapsed_sec,
+    # heartbeat (epoch s, rewritten every 2 s while the fit thread lives),
+    # result (done: EXACTLY the /api/fit body), error + http_status (error:
+    # exactly what /api/fit would have answered)}.
+
+    @app.post("/api/fit/start")
+    @_require_json
+    def fit_start():
+        body = request.get_json(silent=True)
+        if not isinstance(body, dict):
+            return _err("request body must be a JSON object")
+        fit_args, error = _prepare_fit_request(app, body)
+        if error is not None:
+            return error
+        upload_folder = app.config["UPLOAD_FOLDER"]
+        job_id = str(uuid.uuid4())
+        _sweep_expired_jobs(upload_folder)
+        _sweep_fit_job_markers(upload_folder)
+        _fit_job_start(job_id, upload_folder, fit_args,
+                       lambda args, cancel: _run_fit_outcome(app, args, cancel=cancel))
+        return jsonify({"job_id": job_id}), 202
+
+    @app.get("/api/fit/progress/<job_id>")
+    def fit_progress(job_id):
+        try:
+            uuid.UUID(job_id)
+        except ValueError:
+            return _err("Invalid job_id format (expected UUID)", 400)
+        data = _fit_job_read(job_id, app.config["UPLOAD_FOLDER"])
+        if data is None:
+            return _err(f"Job '{job_id}' not found", 404)
+        return app.response_class(json.dumps(data, allow_nan=True), mimetype="application/json")
+
+    @app.post("/api/fit/cancel/<job_id>")
+    def fit_cancel(job_id):
+        try:
+            uuid.UUID(job_id)
+        except ValueError:
+            return _err("Invalid job_id format (expected UUID)", 400)
+        _fit_job_cancel(job_id, app.config["UPLOAD_FOLDER"])
+        return jsonify({"cancelled": True})
+
     # ── Health check ──────────────────────────────────────────────────────────
 
     @app.get("/api/health")
diff --git a/fitting.py b/fitting.py
index 63785a8..eab9baa 100644
--- a/fitting.py
+++ b/fitting.py
@@ -26,6 +26,8 @@ import hashlib
 import json
 import logging
 import re
+import threading
+import time
 import warnings
 from typing import Any
 
@@ -979,6 +981,44 @@ def _make_peak_params(
     return p
 
 
+# ── Cancellation (unit 2, 2026-09-27: long fits via start-then-poll) ────────
+# A fit started through /api/fit/start runs in a background thread; the page
+# can abandon it (a re-run, a tab switch, an edited model, a closed tab). The
+# job passes ``run_fit(..., cancel=callable)``; inside that thread every
+# model.fit below receives an ``iter_cb`` that returns True — lmfit's abort —
+# once ``cancel()`` is true (checked at most every 0.25 s). Thread-local, so a
+# concurrent fit in another thread of the same worker is untouched; and
+# WITHOUT a cancel callable no ``iter_cb`` argument is passed at all, so every
+# synchronous call is made exactly as before. Never part of fit_kws: the
+# request seed cannot see it.
+_CANCEL = threading.local()
+
+
+class FitCancelled(RuntimeError):
+    """The job was cancelled while run_fit ran."""
+
+
+def _cancel_kw() -> dict:
+    fn = getattr(_CANCEL, "fn", None)
+    if fn is None:
+        return {}
+    state = {"t": 0.0, "hit": False}
+
+    def iter_cb(params, it, resid, *args, **kws):
+        if state["hit"]:
+            return True
+        now = time.monotonic()
+        if now - state["t"] >= 0.25:
+            state["t"] = now
+            if fn():
+                state["hit"] = True
+                _CANCEL.hit = True
+                return True
+        return None
+
+    return {"iter_cb": iter_cb}
+
+
 def _finite_search_box(params: Parameters, x: np.ndarray,
                        y_sub: np.ndarray) -> dict[str, dict[str, float]]:
     """Give every freely varying parameter a finite box, in place.
@@ -1062,7 +1102,7 @@ def _search_then_refine(model, params, requested, y_sub, x, weights, kws):
     for name, (lo, hi) in requested.items():
         boxed[name].set(min=lo, max=hi)
     generated = _finite_search_box(boxed, x, y_sub)
-    found = model.fit(y_sub, boxed, x=x, weights=weights, **kws)
+    found = model.fit(y_sub, boxed, x=x, weights=weights, **kws, **_cancel_kw())
     found.box_unverified, found.search_box = bool(generated), generated
     if not generated:
         return found
@@ -1073,7 +1113,7 @@ def _search_then_refine(model, params, requested, y_sub, x, weights, kws):
     # passed through fit_kws would make least_squares raise.
     refine_kws = {"method": "least_squares", "nan_policy": kws.get("nan_policy", "omit")}
     try:
-        refined = model.fit(y_sub, free, x=x, weights=weights, **refine_kws)
+        refined = model.fit(y_sub, free, x=x, weights=weights, **refine_kws, **_cancel_kw())
     except Exception:
         log.debug("refinement outside the search box raised", exc_info=True)
         return found
@@ -1111,7 +1151,7 @@ def _global_or_local_candidate(model, params, requested, y_sub, x, weights, kws)
         start[name].set(min=lo, max=hi)
     try:
         local = model.fit(y_sub, start, x=x, weights=weights,
-                          method="least_squares", nan_policy=kws.get("nan_policy", "omit"))
+                          method="least_squares", nan_policy=kws.get("nan_policy", "omit"), **_cancel_kw())
     except Exception:
         log.debug("local candidate from the start raised", exc_info=True)
         return searched
@@ -1147,11 +1187,11 @@ def _basinhopping_candidate(model, params, requested, y_sub, x, weights, kws):
     start = params.copy()
     for name, (lo, hi) in requested.items():
         start[name].set(min=lo, max=hi)
-    found = model.fit(y_sub, start.copy(), x=x, weights=weights, **kws)
+    found = model.fit(y_sub, start.copy(), x=x, weights=weights, **kws, **_cancel_kw())
     candidate = None
     try:   # from wherever the search stopped, even an evaluation-budget abort (as DE)
         refined = model.fit(y_sub, found.params.copy(), x=x, weights=weights,
-                            method="least_squares", nan_policy=nan_policy)
+                            method="least_squares", nan_policy=nan_policy, **_cancel_kw())
         if refined.success:
             candidate = refined
     except Exception:
@@ -1163,7 +1203,8 @@ def _basinhopping_candidate(model, params, requested, y_sub, x, weights, kws):
                          "so the result is not a verified fit")
         candidate = found
     try:
-        local = model.fit(y_sub, start.copy(), x=x, weights=weights, method="least_squares", nan_policy=nan_policy)
+        local = model.fit(y_sub, start.copy(), x=x, weights=weights, method="least_squares", nan_policy=nan_policy,
+                          **_cancel_kw())
     except Exception:
         log.debug("local candidate from the start raised", exc_info=True)
         return candidate
@@ -1489,7 +1530,7 @@ def _component_required(fit_reduced, params_full, removed_prefixes, y_sub, weigh
 # Main fitting API
 # ─────────────────────────────────────────────────────────────────────────────
 
-def run_fit(
+def _run_fit_impl(
     energy: np.ndarray,
     counts: np.ndarray,
     peak_specs: list[dict[str, Any]],
@@ -1750,7 +1791,7 @@ def run_fit(
         if kws.get("method") == "basinhopping":
             bounds = {name: requested_bounds.get(name, (par.min, par.max)) for name, par in params.items()}
             return _basinhopping_candidate(model, params, bounds, y_sub, x, weights, seeded(kws))
-        return model.fit(y_sub, params, x=x, weights=weights, **seeded(kws))
+        return model.fit(y_sub, params, x=x, weights=weights, **seeded(kws), **_cancel_kw())
 
     def fit_once(params):
         return fit_model(composite_model, params)
@@ -2048,3 +2089,27 @@ def compute_background_only(
         "background": bg.tolist(),
         "net_counts": (y - bg).tolist(),
     }
+
+
+def run_fit(*args, cancel=None, **kwargs):
+    """Fit peaks — see ``_run_fit_impl`` for every argument and the result.
+
+    ``cancel`` (optional, unit 2): a callable polled during the fit; once it
+    returns true every remaining minimisation aborts and ``FitCancelled`` is
+    raised instead of a result. Without it this is exactly the synchronous fit
+    it always was (no ``iter_cb`` reaches any minimiser)."""
+    if cancel is None:
+        return _run_fit_impl(*args, **kwargs)
+    _CANCEL.fn, _CANCEL.hit = cancel, False
+    try:
+        result = _run_fit_impl(*args, **kwargs)
+    finally:
+        hit = getattr(_CANCEL, "hit", False)
+        _CANCEL.fn, _CANCEL.hit = None, False
+    if hit:
+        raise FitCancelled("the fit was cancelled")
+    return result
+
+
+run_fit.__wrapped__ = _run_fit_impl
+

exec
/bin/zsh -lc 'git diff fix-acceptance-holes..HEAD -- templates/index.html tests/js/fit_start_poll.test.js tests/test_fit_start_poll.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-bFfMt0VP' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ERBmIqvW' (errno=Operation not permitted)
diff --git a/templates/index.html b/templates/index.html
index 0f4e530..72a215e 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -7445,6 +7445,116 @@ async function _readFitReply(resp) {
   }
 }
 
+// ── Long fits via start-then-poll (unit 2, 2026-09-27) ──────────────────────
+// The public URL ends a proxied request at ~100 s (Cloudflare 524); a
+// basinhopping fit of a large C 1s model takes 3–4 minutes. So the fit is
+// STARTED (/api/fit/start: the same validation as /api/fit, an immediate 400
+// for a bad request, else 202 + a job id) and POLLED (/api/fit/progress, a
+// short request every FIT_POLL_MS); no request of this path lasts longer than
+// a poll. The final record's `result` is exactly the body /api/fit returns,
+// read with F2's rules (_readFitReply: a body read but not JSON — a NaN — is
+// the server's failed fit). The caller's ownership rules run INSIDE the loop:
+// `guard.abandoned()` returning a reason ('tab' | 'model') cancels the job on
+// the server and returns { _abandoned: reason } — the caller discards with
+// its usual message. Transport: a START that cannot reach the server is a
+// transport failure (the caller's local fallback, as before); a poll that
+// cannot is retried and only FIT_POLL_TRANSPORT_RETRIES in a row are. A
+// record whose heartbeat stops (a restarted worker takes the fit thread with
+// it) is a failed fit, never an endless spinner. Cancellation also reaches
+// the server when the page is closed (pagehide beacon) and, server-side,
+// when polls stop for three minutes (above the ~1-minute timer throttling of a hidden browser tab).
+const FIT_POLL_MS = 500;
+const FIT_POLL_TRANSPORT_RETRIES = 5;
+const FIT_HEARTBEAT_LOST_SEC = 30;
+const _runningFitJobs = new Set();
+function _cancelFitJob(jobId) {
+  try { fetch('/api/fit/cancel/' + encodeURIComponent(jobId), { method: 'POST', keepalive: true }).catch(() => {}); } catch (_) { /* best effort */ }
+}
+if (typeof window !== 'undefined' && window.addEventListener) {
+  window.addEventListener('pagehide', () => {
+    for (const id of _runningFitJobs) {
+      try { navigator.sendBeacon('/api/fit/cancel/' + encodeURIComponent(id)); } catch (_) { /* best effort */ }
+    }
+  });
+}
+function _fitHttpError(status, msg, prefix) {
+  const err = new Error(msg || ((prefix || 'Fit request failed') + ' (HTTP ' + status + ').'));
+  err.serverError = true;
+  err.httpStatus = status;
+  return err;
+}
+async function _serverFitJob(fitReq, guard) {
+  guard = guard || {};
+  const isTransport = e => e && !e.serverError && (e instanceof TypeError || e.name === 'AbortError');
+  let resp;
+  try {
+    resp = await fetch('/api/fit/start', { method: 'POST', headers: { 'Content-Type': 'application/json' },
+                                           body: JSON.stringify(fitReq), signal: guard.signal });
+  } catch (e) { if (isTransport(e)) e.transportFailure = true; throw e; }
+  if (resp.ok === false) {
+    let msg = null;
+    try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
+    throw _fitHttpError(resp.status, msg);
+  }
+  let started;
+  try { started = await _readFitReply(resp); } catch (e) { if (isTransport(e)) e.transportFailure = true; throw e; }
+  const jobId = started && started.job_id;
+  if (!jobId) throw _fitHttpError(resp.status, 'The server did not start the fit (no job id).');
+  _runningFitJobs.add(jobId);
+  let misses = 0;
+  try {
+    while (true) {
+      await new Promise(r => setTimeout(r, FIT_POLL_MS));
+      if (guard.signal && guard.signal.aborted) {
+        _cancelFitJob(jobId);
+        throw guard.signal.reason || new DOMException('aborted', 'AbortError');
+      }
+      const why = guard.abandoned ? guard.abandoned() : null;
+      if (why) { _cancelFitJob(jobId); return { _abandoned: why }; }
+      let pr, rec;
+      try {
+        pr = await fetch('/api/fit/progress/' + encodeURIComponent(jobId), { signal: guard.signal });
+      } catch (e) {
+        if (e && e.name === 'AbortError') { _cancelFitJob(jobId); throw e; }
+        if (++misses >= FIT_POLL_TRANSPORT_RETRIES) {
+          _cancelFitJob(jobId);
+          const err = new Error('Lost contact with the server during the fit (' + ((e && e.message) || 'network error') + ').');
+          err.transportFailure = true;
+          throw err;
+        }
+        continue;
+      }
+      if (pr.ok === false) {
+        _cancelFitJob(jobId);
+        let msg = null;
+        try { const j = await pr.json(); msg = (j && j.error) || null; } catch (_) { /* non-JSON body */ }
+        throw _fitHttpError(pr.status, msg, 'Lost the fit\'s progress');
+      }
+      try { rec = await _readFitReply(pr); } catch (e) {
+        if (e && e.unreadableReply) { _cancelFitJob(jobId); throw e; }
+        if (++misses >= FIT_POLL_TRANSPORT_RETRIES) {
+          _cancelFitJob(jobId);
+          if (isTransport(e)) e.transportFailure = true;
+          throw e;
+        }
+        continue;
+      }
+      misses = 0;
+      if (rec.status === 'done') return rec.result;
+      if (rec.status === 'error') throw _fitHttpError(rec.http_status || 500, rec.error);
+      if (rec.status === 'cancelled') throw _fitHttpError(409, 'The fit was stopped on the server before it finished. Run it again.');
+      if (Number.isFinite(rec.heartbeat_age_sec) && rec.heartbeat_age_sec > FIT_HEARTBEAT_LOST_SEC) {
+        _cancelFitJob(jobId);
+        throw _fitHttpError(503, 'The server stopped working on the fit (no sign of it for ' + Math.round(rec.heartbeat_age_sec) +
+                                 ' s — it was probably restarted). Run the fit again.');
+      }
+      if (typeof guard.onProgress === 'function') guard.onProgress(rec);
+    }
+  } finally {
+    _runningFitJobs.delete(jobId);
+  }
+}
+
 async function runAutoFitC1sGraphite() {
   // Pre-conditions
   if (!state.rawBE || !state.rawBE.length) { notify('Load a spectrum first.', 'amber'); return; }
@@ -7559,10 +7669,8 @@ async function runAutoFitC1sGraphite() {
       bgPayload.manual_bg = _getManualAnchors().map(a => [a.x, a.y]);
     }
     const sessionId = await uploadToBackend(be2, inten2);   // after EVERY input above is captured
-    const resp = await fetch('/api/fit', {
-      method: 'POST',
-      headers: { 'Content-Type': 'application/json' },
-      body: JSON.stringify({
+    // Unit 2: started and polled, like Run Fit (the 2-minute abort still applies)
+    const json = await _serverFitJob({
         session_id: sessionId,
         background: bgPayload,
         peaks: peakSpecs,
@@ -7572,21 +7680,26 @@ async function runAutoFitC1sGraphite() {
         // the model without it; a redundant anchor must not set the energy
         // reference of a whole spectrum (see applyAutoFitResult).
         require_component: anchorId,
-      }),
+    }, {
       signal: ctrl.signal,
+      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
     });
     clearTimeout(timer);
-    // F2: a non-2xx reply is a failed REQUEST with its status in the message,
-    // as Run Fit has done since A0 (a Cloudflare 524 or a gunicorn 500 used to
-    // reach the parser and read as "the server's reply could not be read")
-    if (resp.ok === false) {
-      let msg = null;
-      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
-      const err = new Error(msg || ('Fit request failed (HTTP ' + resp.status + ').'));
-      err.httpStatus = resp.status;
-      throw err;
+    // F2: a non-2xx reply is a failed REQUEST with its status in the message
+    // (_serverFitJob throws it with httpStatus); an unreadable reply is a
+    // failed fit with its own message (unreadableReply).
+    if (json && json._abandoned === 'tab') {
+      _hideFitSpinner();
+      notify('Auto-fit discarded — tab switched during fit.', 'amber');
+      _autoFitRestore(snap, fittingTab);
+      return;
+    }
+    if (json && json._abandoned === 'model') {
+      _hideFitSpinner();
+      notify('Auto-fit discarded because the model or its background / ROI settings were edited while it was running. Previous peaks and result restored. Run it again.', 'amber', true);
+      _autoFitRestore(snap, fittingTab);
+      return;
     }
-    const json = await _readFitReply(resp);   // F2: an unreadable reply is a failed fit with its own message
     if (json.error) throw new Error(json.error);
     if (json.success !== true) throw new Error(json.message || 'fit did not converge');
     if (!_ownerActive(fittingTab)) {
@@ -8053,26 +8166,27 @@ async function runFit(opts = {}) {
       n_perturb: 3,
       n_starts: nStarts       // the server also skips it for the global methods
     };
-    let resp, json;
-    try {
-      resp = await fetch('/api/fit', {
-        method: 'POST',
-        headers: { 'Content-Type': 'application/json' },
-        body: JSON.stringify(fitReq)
-      });
-    } catch (e) { _asTransport(e); }
-    if (resp.ok === false) {
-      // HTTP failure: read a message if the body is JSON, but a 502 HTML
-      // page is still a SERVER failure, never a reason to switch engines.
-      let msg = null;
-      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
-      const err = new Error(msg || ('Fit request failed (HTTP ' + resp.status + ').'));
-      err.serverError = true;
-      throw err;
+    // Unit 2: started and polled (_serverFitJob) — no request lasts longer than
+    // a poll, so none meets the public URL's ~100 s ceiling. An HTTP failure is
+    // a SERVER failure (serverError), never a reason to switch engines; a
+    // START that cannot reach the server is a transport failure, as the single
+    // request was. The ownership checks below also run inside the poll loop,
+    // so a switched tab or an edited model stops the server's work at once.
+    const json = await _serverFitJob(fitReq, {
+      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
+    });
+    if (json && json._abandoned === 'tab') {
+      _hideFitSpinner();
+      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
+      notify('Fit result discarded because you switched tabs during the fit.', 'amber');
+      return;
+    }
+    if (json && json._abandoned === 'model') {
+      _hideFitSpinner();
+      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
+      notify('Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.', 'amber', true);
+      return;
     }
-    // F2: reading the body can fail in transport; a body that was read but is
-    // not JSON is the server's reply — a failed fit, not a fallback
-    try { json = await _readFitReply(resp); } catch (e) { _asTransport(e); }
     if (json.error) {
       const err = new Error(json.error);
       err.serverError = true;
diff --git a/tests/js/fit_start_poll.test.js b/tests/js/fit_start_poll.test.js
new file mode 100644
index 0000000..89dffa1
--- /dev/null
+++ b/tests/js/fit_start_poll.test.js
@@ -0,0 +1,143 @@
+// Unit 2 (2026-09-27): Run Fit and Auto-Fit start the fit and poll for it
+// (_serverFitJob). Pinned: the result is the /api/fit body; a bad request's
+// message and status are the synchronous route's; ownership (a switched tab,
+// an edited model) cancels the server's job and discards; transport keeps its
+// meaning (a START that cannot reach the server may fall back to the local
+// engine; one lost poll does not; five in a row do); a lost heartbeat, a
+// cancelled or errored record are failed fits; F2's NaN rule applies to the
+// final record; the 2-minute Auto-Fit abort cancels the job.
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
+const constLine = n => { const l = lines.find(x => x.startsWith('const ' + n)); assert.ok(l, n); return l; };
+
+// fetch scripted by URL; every call recorded
+function server(script) {
+  const calls = [];
+  const fetch = async (url, init) => {
+    calls.push({ url, method: (init && init.method) || 'GET' });
+    const h = script(url, init, calls);
+    if (h instanceof Error) throw h;
+    return h;
+  };
+  return { fetch, calls };
+}
+const ok = (obj, status = 200) => ({ ok: true, status, text: async () => (typeof obj === 'string' ? obj : JSON.stringify(obj)) });
+const bad = (status, obj) => ({ ok: false, status, json: async () => { if (obj === undefined) throw new SyntaxError('x'); return obj; } });
+
+function make(fetch) {
+  const src = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
+    'const _runningFitJobs = new Set();',
+    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
+  return new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob, _runningFitJobs };')(
+    fetch, f => f(), class extends Error { constructor(m, n) { super(m); this.name = n; } });
+}
+const START = '/api/fit/start';
+const isProgress = u => u.startsWith('/api/fit/progress/');
+const isCancel = u => u.startsWith('/api/fit/cancel/');
+
+test('start -> running polls -> done: the result is the /api/fit body; no job is left registered', async () => {
+  let n = 0;
+  const s = server(u => u === START ? ok({ job_id: 'J' }, 202)
+    : isProgress(u) ? (++n < 3 ? ok({ status: 'running', heartbeat_age_sec: 0.4 }) : ok({ status: 'done', result: { success: true, x: 1 } }))
+    : ok({}));
+  const { _serverFitJob, _runningFitJobs } = make(s.fetch);
+  assert.deepStrictEqual(await _serverFitJob({ a: 1 }, {}), { success: true, x: 1 });
+  assert.strictEqual(s.calls.filter(c => isProgress(c.url)).length, 3);
+  assert.strictEqual(_runningFitJobs.size, 0);
+  assert.ok(!s.calls.some(c => isCancel(c.url)), 'a finished job is not cancelled');
+});
+
+test('a bad request: the synchronous route\'s message and status, immediately; no poll', async () => {
+  const s = server(u => u === START ? bad(400, { error: 'n_perturb must be between 0 and 10' }) : assert.fail(u));
+  const { _serverFitJob } = make(s.fetch);
+  await assert.rejects(_serverFitJob({}, {}), e => e.serverError && e.httpStatus === 400 && /n_perturb must be between/.test(e.message));
+});
+
+test('a START that cannot reach the server is a transport failure (the caller may fall back to the local engine)', async () => {
+  const s = server(u => new TypeError('Failed to fetch'));
+  const { _serverFitJob } = make(s.fetch);
+  await assert.rejects(_serverFitJob({}, {}), e => e.transportFailure === true && !e.serverError);
+});
+
+test('an error record is a failed fit with the synchronous message and status', async () => {
+  const s = server(u => u === START ? ok({ job_id: 'J' }, 202)
+    : ok({ status: 'error', http_status: 400, error: 'The model is not determined by these data: 8 free parameters for 6 data points' }));
+  const { _serverFitJob } = make(s.fetch);
+  await assert.rejects(_serverFitJob({}, {}), e => e.serverError && e.httpStatus === 400 && /not determined by these data/.test(e.message));
+});
+
+test('a done record carrying NaN is F2\'s failed fit (unreadable reply), not a transport failure', async () => {
+  const s = server(u => u === START ? ok({ job_id: 'J' }, 202)
+    : isProgress(u) ? ok('{"status": "done", "result": {"success": true, "s": NaN}}') : ok({}));
+  const { _serverFitJob } = make(s.fetch);
+  await assert.rejects(_serverFitJob({}, {}), e => e.unreadableReply === true && e.serverError && !e.transportFailure && /non-finite/.test(e.message));
+});
+
+test('one lost poll is retried; five in a row are a transport failure and cancel the job', async () => {
+  let n = 0;
+  const flaky = server(u => u === START ? ok({ job_id: 'J' }, 202)
+    : isProgress(u) ? (++n <= 4 ? new TypeError('network') : ok({ status: 'done', result: { success: true } })) : ok({}));
+  assert.deepStrictEqual(await make(flaky.fetch)._serverFitJob({}, {}), { success: true });
+  const dead = server(u => u === START ? ok({ job_id: 'J' }, 202) : isProgress(u) ? new TypeError('network') : ok({}));
+  await assert.rejects(make(dead.fetch)._serverFitJob({}, {}), e => e.transportFailure === true && /Lost contact/.test(e.message));
+  assert.ok(dead.calls.some(c => isCancel(c.url) && c.method === 'POST'), 'the server is told to stop');
+});
+
+test('a stopped heartbeat (restarted worker) is a failed fit, never an endless spinner', async () => {
+  const s = server(u => u === START ? ok({ job_id: 'J' }, 202) : isProgress(u) ? ok({ status: 'running', heartbeat_age_sec: 45 }) : ok({}));
+  await assert.rejects(make(s.fetch)._serverFitJob({}, {}), e => e.serverError && /stopped working on the fit/.test(e.message));
+});
+
+test('a job cancelled on the server (abandoned) is reported, not waited for', async () => {
+  const s = server(u => u === START ? ok({ job_id: 'J' }, 202) : ok({ status: 'cancelled' }));
+  await assert.rejects(make(s.fetch)._serverFitJob({}, {}), e => e.serverError && /stopped on the server/.test(e.message));
+});
+
+test('ownership inside the loop: a switched tab or an edited model cancels the job and returns the reason', async () => {
+  for (const reason of ['tab', 'model']) {
+    let polls = 0;
+    const s = server(u => u === START ? ok({ job_id: 'J' }, 202) : isProgress(u) ? (polls++, ok({ status: 'running', heartbeat_age_sec: 0 })) : ok({}));
+    let t = 0;
+    const out = await make(s.fetch)._serverFitJob({}, { abandoned: () => (++t > 2 ? reason : null) });
+    assert.deepStrictEqual(out, { _abandoned: reason });
+    assert.ok(s.calls.some(c => isCancel(c.url) && c.method === 'POST'), reason + ': the server is told to stop');
+    assert.strictEqual(polls, 2, 'no poll after the model or tab changed');
+  }
+});
+
+test('the Auto-Fit abort (2 minutes) cancels the job and surfaces as an AbortError', async () => {
+  const ctrl = { aborted: false, reason: null };
+  let polls = 0;
+  const s = server(u => u === START ? ok({ job_id: 'J' }, 202) : isProgress(u) ? (++polls === 2 && (ctrl.aborted = true, ctrl.reason = Object.assign(new Error('timeout'), { name: 'AbortError' })), ok({ status: 'running', heartbeat_age_sec: 0 })) : ok({}));
+  await assert.rejects(make(s.fetch)._serverFitJob({}, { signal: ctrl }), e => e.name === 'AbortError');
+  assert.ok(s.calls.some(c => isCancel(c.url)));
+});
+
+test('Run Fit and Auto-Fit both go through _serverFitJob; nothing on the page posts to the synchronous /api/fit any more', () => {
+  assert.match(extractFn('runFit'), /await _serverFitJob\(fitReq, \{/);
+  assert.match(extractFn('runAutoFitC1sGraphite'), /await _serverFitJob\(\{/);
+  assert.ok(!/fetch\('\/api\/fit'/.test(html), 'no synchronous /api/fit fetch left');
+  // the ownership reasons are the ones the discard messages handle
+  for (const fn of ['runFit', 'runAutoFitC1sGraphite']) {
+    const src = extractFn(fn);
+    assert.match(src, /_abandoned === 'tab'/, fn);
+    assert.match(src, /_abandoned === 'model'/, fn);
+  }
+  assert.match(html, /addEventListener\('pagehide'/, 'a closed page cancels its running fits');
+});
diff --git a/tests/test_fit_start_poll.py b/tests/test_fit_start_poll.py
new file mode 100644
index 0000000..7075008
--- /dev/null
+++ b/tests/test_fit_start_poll.py
@@ -0,0 +1,175 @@
+"""Unit 2 (2026-09-27): long fits via start-then-poll.
+
+/api/fit/start validates exactly as /api/fit, runs the SAME run_fit in a
+background thread on Find Peaks' job records, and the page polls
+/api/fit/progress. Pinned here: a polled fit is the synchronous fit (same
+body; byte-identical for Levenberg-Marquardt); every validation error is
+immediate and word-for-word the same; a run_fit error becomes the same
+message and status in the record; cancel (explicit, or no poll for
+FIT_JOB_ABANDON_SEC) stops the fit within seconds; the heartbeat; every poll
+is a short request.
+"""
+
+import io
+import json
+import time
+
+import numpy as np
+import pytest
+
+import app as app_module
+from app import create_app
+
+
+def _gl(x, c, a, w):
+    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)
+
+
+@pytest.fixture()
+def client(tmp_path):
+    a = create_app(upload_folder=str(tmp_path))
+    a.config["TESTING"] = True
+    with a.test_client() as c:
+        yield c
+
+
+def _upload(client, n=200, comps=((284.5, 5000, 0.9), (286.2, 1500, 1.1)), seed=3):
+    rng = np.random.default_rng(seed)
+    x = np.linspace(281.0, 292.0, n)
+    y = rng.poisson(300 + sum(_gl(x, c, a, w) for c, a, w in comps)).astype(float)
+    csv = "\n".join(f"{a:.4f},{b:.1f}" for a, b in zip(x, y))
+    r = client.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "s.csv")})
+    assert r.status_code == 200, r.get_json()
+    return r.get_json()["session_id"]
+
+
+def _specs(comps):
+    return [{"id": str(i + 1), "shape": "pseudo_voigt_gl", "center": c + 0.1, "fwhm": w * 1.1, "amplitude": a * 0.8,
+             "gl_ratio": 0.3, "amplitude_min": 0} for i, (c, a, w) in enumerate(comps)]
+
+
+def _body(sid, comps, method="leastsq", **extra):
+    return {"session_id": sid, "background": {"method": "shirley"}, "peaks": _specs(comps),
+            "fit_method": method, "n_perturb": 1, "n_starts": 0, **extra}
+
+
+def _poll(client, job_id, limit=300.0):
+    t0, longest = time.time(), 0.0
+    while True:
+        q0 = time.time()
+        r = client.get(f"/api/fit/progress/{job_id}")
+        longest = max(longest, time.time() - q0)
+        assert r.status_code == 200
+        rec = json.loads(r.get_data(as_text=True))
+        if rec["status"] != "running":
+            return rec, longest
+        assert time.time() - t0 < limit, "job did not finish"
+        time.sleep(0.2)
+
+
+COMPS = ((284.5, 5000, 0.9), (286.2, 1500, 1.1))
+
+
+def test_a_polled_fit_is_the_synchronous_fit_byte_for_byte(client):
+    sid = _upload(client)
+    sync = client.post("/api/fit", json=_body(sid, COMPS))
+    assert sync.status_code == 200
+    start = client.post("/api/fit/start", json=_body(sid, COMPS))
+    assert start.status_code == 202
+    rec, longest = _poll(client, start.get_json()["job_id"])
+    assert rec["status"] == "done"
+    # Levenberg-Marquardt is byte-identical request to request (CLAUDE.md): same seed, same body
+    assert json.dumps(rec["result"], sort_keys=True) == json.dumps(sync.get_json(), sort_keys=True)
+    assert longest < 2.0, f"a poll took {longest:.2f} s"
+
+
+@pytest.mark.parametrize("method", ["differential_evolution", "basinhopping", "least_squares"])
+def test_the_stochastic_and_default_methods_give_the_synchronous_answer(client, method):
+    sid = _upload(client)
+    body = _body(sid, COMPS, method=method, n_perturb=0)
+    sync = client.post("/api/fit", json=body).get_json()
+    rec, _ = _poll(client, client.post("/api/fit/start", json=body).get_json()["job_id"])
+    res = rec["result"]
+    assert res["random_seed"] == sync["random_seed"]
+    assert res["success"] == sync["success"] is True
+    # Trust-Region (also DE's and basinhopping's refinement) is not bit-reproducible
+    # across calls (BLAS alignment, CLAUDE.md); the answer is the same fit
+    assert res["statistics"]["reduced_chi_square"] == pytest.approx(sync["statistics"]["reduced_chi_square"], rel=1e-6)
+
+
+@pytest.mark.parametrize("patch,status,fragment", [
+    ({"n_perturb": 101}, 400, "n_perturb must be between"),
+    ({"fit_method": "ampgo"}, 400, "Unknown fit_method"),
+    ({"peaks": []}, 400, "'peaks' list is empty"),
+    ({"session_id": "0" * 32}, 404, "not found"),
+])
+def test_a_bad_request_is_refused_immediately_and_identically(client, patch, status, fragment):
+    sid = _upload(client)
+    body = {**_body(sid, COMPS), **patch}
+    a = client.post("/api/fit", json=body)
+    b = client.post("/api/fit/start", json=body)
+    assert a.status_code == b.status_code == status
+    assert a.get_json() == b.get_json()
+    assert fragment in b.get_json()["error"]
+
+
+def test_a_run_fit_refusal_reaches_the_record_with_the_synchronous_message_and_status(client):
+    sid = _upload(client, n=6)                                    # 8 free parameters, 6 points (unit F2)
+    body = {**_body(sid, COMPS), "n_perturb": 0}
+    sync = client.post("/api/fit", json=body)
+    rec, _ = _poll(client, client.post("/api/fit/start", json=body).get_json()["job_id"])
+    assert rec["status"] == "error"
+    assert rec["http_status"] == sync.status_code == 400
+    assert rec["error"] == sync.get_json()["error"]
+
+
+SLOW = ((283.2, 2000, 0.8), (284.5, 5000, 0.9), (285.4, 1800, 1.0), (286.6, 1500, 1.1), (288.4, 900, 1.4))
+
+
+def test_cancel_stops_a_running_fit_within_seconds(client):
+    sid = _upload(client, n=300, comps=SLOW)
+    job = client.post("/api/fit/start", json=_body(sid, SLOW, method="basinhopping", n_perturb=0)).get_json()["job_id"]
+    time.sleep(1.0)
+    rec = json.loads(client.get(f"/api/fit/progress/{job}").get_data(as_text=True))
+    assert rec["status"] == "running", "the fixture must still be running when cancelled"
+    t0 = time.time()
+    assert client.post(f"/api/fit/cancel/{job}").status_code == 200
+    rec, _ = _poll(client, job, limit=30)
+    assert rec["status"] == "cancelled"
+    assert time.time() - t0 < 10, f"cancel took {time.time() - t0:.1f} s"
+
+
+def test_an_abandoned_job_stops_itself_when_polls_stop(client, monkeypatch):
+    monkeypatch.setattr(app_module, "FIT_JOB_ABANDON_SEC", 1.5)
+    sid = _upload(client, n=300, comps=SLOW)
+    job = client.post("/api/fit/start", json=_body(sid, SLOW, method="basinhopping", n_perturb=0)).get_json()["job_id"]
+    time.sleep(6.0)                                               # nobody polls
+    rec = json.loads(client.get(f"/api/fit/progress/{job}").get_data(as_text=True))
+    assert rec["status"] == "cancelled", rec["status"]
+
+
+def test_the_heartbeat_moves_while_the_fit_runs(client):
+    sid = _upload(client, n=300, comps=SLOW)
+    job = client.post("/api/fit/start", json=_body(sid, SLOW, method="basinhopping", n_perturb=0)).get_json()["job_id"]
+    time.sleep(4.5)
+    rec = json.loads(client.get(f"/api/fit/progress/{job}").get_data(as_text=True))
+    assert rec["status"] == "running"
+    assert rec["heartbeat_age_sec"] is not None and rec["heartbeat_age_sec"] < 3.0
+    assert rec["elapsed_sec"] >= 2.0
+    client.post(f"/api/fit/cancel/{job}")
+    _poll(client, job, limit=30)
+
+
+def test_unknown_and_malformed_job_ids(client):
+    assert client.get("/api/fit/progress/not-a-uuid").status_code == 400
+    assert client.get("/api/fit/progress/00000000-0000-0000-0000-000000000000").status_code == 404
+    assert client.post("/api/fit/cancel/not-a-uuid").status_code == 400
+
+
+def test_a_non_finite_result_reaches_the_page_unsanitised(tmp_path):
+    # the page's _readFitReply refuses NaN as a failed fit (unit F2): the job
+    # record must carry it exactly as /api/fit would, never as null
+    app_module._fit_job_write("11111111-1111-1111-1111-111111111111", str(tmp_path),
+                              {"status": "done", "result": {"x": float("nan")}})
+    text = (tmp_path / "11111111-1111-1111-1111-111111111111.job.json").read_text()
+    assert "NaN" in text

exec
/bin/zsh -lc 'git diff fix-acceptance-holes..HEAD -- app.py fitting.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-QAQsVjIr' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ma4TcCaD' (errno=Operation not permitted)
diff --git a/app.py b/app.py
index f689d5a..3271469 100644
--- a/app.py
+++ b/app.py
@@ -58,6 +58,113 @@ MAX_N_PERTURB = 100
 # — no background thread or scheduler.
 SESSION_TTL_DAYS = 7
 
+# ─────────────────────────────────────────────────────────────────────────────
+# /api/fit request handling, shared by /api/fit and /api/fit/start (unit 2)
+# ─────────────────────────────────────────────────────────────────────────────
+
+def _prepare_fit_request(app, body):
+    """/api/fit's request validation, shared VERBATIM with /api/fit/start
+    (unit 2, 2026-09-27): every 400 / 404 is immediate and word-for-word the
+    same on both routes. Returns ``(kwargs_for_run_fit, None)`` or
+    ``(None, error_response)``."""
+    session_id = body.get("session_id", "")
+    _validate_session_id(session_id)
+
+    try:
+        energy, counts = _load_session(session_id, app.config["UPLOAD_FOLDER"])
+    except KeyError:
+        return None, _err(f"Session '{session_id}' not found", 404)
+
+    # Background config
+    bg_cfg = body.get("background", {})
+    bg_method = bg_cfg.get("method", "shirley")
+    bg_start = _parse_int(bg_cfg.get("start_idx"), 0, len(energy))
+    bg_end = _parse_int(bg_cfg.get("end_idx"), 0, len(energy), default=len(energy))
+    # Clean 400 for malformed endpoint_avg instead of a 500 (audit F9).
+    try:
+        endpoint_avg = max(1, int(bg_cfg.get("endpoint_avg", 1)))
+    except (TypeError, ValueError):
+        return None, _err("endpoint_avg must be an integer")
+    manual_bg = bg_cfg.get("manual_bg")
+
+    # Peak specs
+    peak_specs = body.get("peaks", [])
+    if not peak_specs:
+        return None, _err("'peaks' list is empty – provide at least one peak")
+
+    # Validate peak ids are unique
+    ids = [p.get("id") for p in peak_specs]
+    if len(ids) != len(set(ids)):
+        return None, _err("Duplicate peak ids found – each peak must have a unique 'id'")
+
+    _ALLOWED_METHODS = {
+        "leastsq", "least_squares", "nelder",
+        "differential_evolution", "basinhopping",
+    }
+    fit_method = body.get("fit_method", "leastsq")
+    if fit_method not in _ALLOWED_METHODS:
+        return None, _err(f"Unknown fit_method '{fit_method}'")
+
+    # Bounded, type-checked n_perturb (audit F7; also covers the F9
+    # ValueError-on-bad-input case for this field). Reject out-of-range or
+    # non-integer values with a clean 400 instead of a 500 or a worker hang.
+    try:
+        n_perturb = int(body.get("n_perturb", 5))
+    except (TypeError, ValueError):
+        return None, _err(f"n_perturb must be an integer between 0 and {MAX_N_PERTURB}")
+    if n_perturb < 0 or n_perturb > MAX_N_PERTURB:
+        return None, _err(f"n_perturb must be between 0 and {MAX_N_PERTURB}")
+
+    # Scattered-starts check (optional; the page sends 3). Same clean-400
+    # treatment as n_perturb; run_fit validates again for other callers.
+    n_starts = body.get("n_starts", 0)
+    if isinstance(n_starts, bool) or not isinstance(n_starts, int) or not 0 <= n_starts <= fitting.MAX_N_STARTS:
+        return None, _err(f"n_starts must be an integer between 0 and {fitting.MAX_N_STARTS}")
+    # "Is this component required?" (one extra fit; Auto-Fit asks for its anchor)
+    require_component = body.get("require_component")
+    if require_component is not None and not isinstance(require_component, (str, int)):
+        return None, _err("require_component must be a peak id")
+    return dict(
+        energy=energy,
+        counts=counts,
+        peak_specs=peak_specs,
+        background_method=bg_method,
+        bg_start_idx=bg_start,
+        bg_end_idx=bg_end,
+        charge_shift_ev=0.0,
+        fit_kws={"method": fit_method},
+        manual_bg=manual_bg,
+        n_perturb=n_perturb,
+        endpoint_avg=endpoint_avg,
+        n_starts=n_starts,
+        require_component=require_component,
+    ), None
+
+
+def _run_fit_outcome(app, fit_args, cancel=None):
+    """Run the fit; return ``(status_code, body)`` exactly as /api/fit has
+    always answered (a ValueError is our own validation, 400; a RuntimeError
+    a solver-internal failure, 422 without library internals; anything else
+    500). A cancelled job returns ``(None, None)``."""
+    try:
+        result = fitting.run_fit(**fit_args, cancel=cancel)
+    except fitting.FitCancelled:
+        return None, None
+    except ValueError as exc:
+        # Our own validation: unknown shape/method, self/circular constraint,
+        # "Master peak not found", bad numeric field, etc. (audit F10/F11).
+        return 400, {"error": str(exc)}
+    except RuntimeError:
+        # Solver-internal failure (e.g. lmfit non-convergence). Log the
+        # detail; return a generic 422 that leaks no library internals.
+        app.logger.exception("Fit failed")
+        return 422, {"error": "Fit failed — see server log for details."}
+    except Exception:
+        app.logger.exception("Unexpected fitting error")
+        return 500, {"error": "Internal fitting error — see server log."}
+    return 200, result
+
+
 # ─────────────────────────────────────────────────────────────────────────────
 # Application factory
 # ─────────────────────────────────────────────────────────────────────────────
@@ -443,6 +550,129 @@ def _sweep_expired_jobs(upload_folder: str) -> None:
             pass
 
 
+# ── Fit jobs (unit 2, 2026-09-27) ────────────────────────────────────────────
+# Records are the Find Peaks job files (<job>.job.json, the same TTL sweep);
+# two small markers beside each: <job>.cancel (written by /api/fit/cancel,
+# any worker) and <job>.polled (touched by every poll). The fit thread's
+# cancel condition: the cancel marker exists, OR no poll for
+# FIT_JOB_ABANDON_SEC (a closed tab, a sleeping laptop; 180 s, above the ~1 min timer throttling browsers apply to hidden tabs).
+FIT_JOB_ABANDON_SEC = 180   # > Chrome's 1-minute timer throttling in a hidden tab: a student who switches browser tabs keeps the fit
+FIT_JOB_HEARTBEAT_SEC = 2.0
+
+
+def _fit_job_marker(job_id: str, upload_folder: str, kind: str) -> Path:
+    return Path(upload_folder) / f"{job_id}.{kind}"
+
+
+def _fit_job_write(job_id: str, upload_folder: str, data: dict) -> None:
+    """Atomic like _write_job_progress, but WITHOUT sanitising: a result's
+    NaN / Infinity reach the page exactly as /api/fit sends them (the page's
+    _readFitReply refuses them as a failed fit — unit F2)."""
+    path = _job_progress_path(job_id, upload_folder)
+    tmp = path.with_suffix(f".{threading.get_ident()}.tmp")
+    try:
+        tmp.write_text(json.dumps(data, allow_nan=True))
+        os.replace(tmp, path)
+    except OSError:
+        logging.getLogger(__name__).exception("failed to write fit job %s", job_id)
+
+
+def _fit_job_read(job_id: str, upload_folder: str):
+    path = _job_progress_path(job_id, upload_folder)
+    if not path.exists():
+        return None
+    try:
+        _fit_job_marker(job_id, upload_folder, "polled").touch()
+    except OSError:
+        pass
+    try:
+        data = json.loads(path.read_text())
+    except (OSError, ValueError):
+        data = {"status": "running", "elapsed_sec": 0.0}      # a read racing the first write
+    hb = data.get("heartbeat")
+    data["heartbeat_age_sec"] = round(time.time() - hb, 1) if isinstance(hb, (int, float)) else None
+    return data
+
+
+def _sweep_fit_job_markers(upload_folder: str) -> None:
+    """Markers left by a job whose worker died (they are removed when a job
+    finishes): same TTL as the job records, never raises."""
+    cutoff = time.time() - _ANALYZE_JOB_TTL_SEC
+    for pattern in ("*.cancel", "*.polled"):
+        try:
+            for m in Path(upload_folder).glob(pattern):
+                try:
+                    if m.stat().st_mtime < cutoff:
+                        m.unlink(missing_ok=True)
+                except OSError:
+                    pass
+        except OSError:
+            pass
+
+
+def _fit_job_cancel(job_id: str, upload_folder: str) -> None:
+    try:
+        _fit_job_marker(job_id, upload_folder, "cancel").touch()
+    except OSError:
+        pass
+
+
+def _fit_job_start(job_id: str, upload_folder: str, fit_args: dict, run) -> None:
+    """Start the fit thread and its heartbeat thread. ``run(fit_args, cancel)``
+    returns ``(status, body)``; ``(None, None)`` means cancelled."""
+    started = time.time()
+    lock = threading.Lock()
+    rec = {"status": "running", "elapsed_sec": 0.0, "heartbeat": started}
+    _fit_job_write(job_id, upload_folder, rec)
+    _fit_job_marker(job_id, upload_folder, "polled").touch()
+    cancel_path = _fit_job_marker(job_id, upload_folder, "cancel")
+    polled_path = _fit_job_marker(job_id, upload_folder, "polled")
+    finished = threading.Event()
+
+    def cancelled() -> bool:
+        if cancel_path.exists():
+            return True
+        try:
+            return time.time() - polled_path.stat().st_mtime > FIT_JOB_ABANDON_SEC
+        except OSError:
+            return False
+
+    def heartbeat() -> None:
+        while not finished.wait(FIT_JOB_HEARTBEAT_SEC):
+            with lock:
+                if rec["status"] != "running":
+                    return
+                rec["heartbeat"] = time.time()
+                rec["elapsed_sec"] = round(time.time() - started, 1)
+                _fit_job_write(job_id, upload_folder, rec)
+
+    def worker() -> None:
+        try:
+            status, body = run(fit_args, cancelled)
+        except Exception as exc:                       # the record must always leave "running"
+            logging.getLogger(__name__).exception("fit job %s crashed", job_id)
+            status, body = 500, {"error": "Internal fitting error — see server log."}
+        with lock:
+            rec["elapsed_sec"] = round(time.time() - started, 1)
+            rec["heartbeat"] = time.time()
+            if status is None or cancel_path.exists():
+                rec.update(status="cancelled")
+            elif status == 200:
+                rec.update(status="done", result=body)
+            else:
+                rec.update(status="error", error=body.get("error"), http_status=status)
+            finished.set()
+            _fit_job_write(job_id, upload_folder, rec)
+        for kind in ("cancel", "polled"):
+            try:
+                _fit_job_marker(job_id, upload_folder, kind).unlink(missing_ok=True)
+            except OSError:
+                pass
+
+    threading.Thread(target=worker, daemon=True, name=f"fit-{job_id[:8]}").start()
+    threading.Thread(target=heartbeat, daemon=True, name=f"fit-hb-{job_id[:8]}").start()
+
+
 def _require_json(f):
     """Decorator: return 400 if request body is not valid JSON."""
     @wraps(f)
@@ -779,94 +1009,13 @@ def _register_routes(app: Flask) -> None:
         }
         """
         body = request.get_json()
-        session_id = body.get("session_id", "")
-        _validate_session_id(session_id)
-
-        try:
-            energy, counts = _load_session(session_id, app.config["UPLOAD_FOLDER"])
-        except KeyError:
-            return _err(f"Session '{session_id}' not found", 404)
-
-        # Background config
-        bg_cfg = body.get("background", {})
-        bg_method = bg_cfg.get("method", "shirley")
-        bg_start = _parse_int(bg_cfg.get("start_idx"), 0, len(energy))
-        bg_end = _parse_int(bg_cfg.get("end_idx"), 0, len(energy), default=len(energy))
-        # Clean 400 for malformed endpoint_avg instead of a 500 (audit F9).
-        try:
-            endpoint_avg = max(1, int(bg_cfg.get("endpoint_avg", 1)))
-        except (TypeError, ValueError):
-            return _err("endpoint_avg must be an integer")
-        manual_bg = bg_cfg.get("manual_bg")
-
-        # Peak specs
-        peak_specs = body.get("peaks", [])
-        if not peak_specs:
-            return _err("'peaks' list is empty – provide at least one peak")
-
-        # Validate peak ids are unique
-        ids = [p.get("id") for p in peak_specs]
-        if len(ids) != len(set(ids)):
-            return _err("Duplicate peak ids found – each peak must have a unique 'id'")
-
-        _ALLOWED_METHODS = {
-            "leastsq", "least_squares", "nelder",
-            "differential_evolution", "basinhopping",
-        }
-        fit_method = body.get("fit_method", "leastsq")
-        if fit_method not in _ALLOWED_METHODS:
-            return _err(f"Unknown fit_method '{fit_method}'")
-
-        # Bounded, type-checked n_perturb (audit F7; also covers the F9
-        # ValueError-on-bad-input case for this field). Reject out-of-range or
-        # non-integer values with a clean 400 instead of a 500 or a worker hang.
-        try:
-            n_perturb = int(body.get("n_perturb", 5))
-        except (TypeError, ValueError):
-            return _err(f"n_perturb must be an integer between 0 and {MAX_N_PERTURB}")
-        if n_perturb < 0 or n_perturb > MAX_N_PERTURB:
-            return _err(f"n_perturb must be between 0 and {MAX_N_PERTURB}")
-
-        # Scattered-starts check (optional; the page sends 3). Same clean-400
-        # treatment as n_perturb; run_fit validates again for other callers.
-        n_starts = body.get("n_starts", 0)
-        if isinstance(n_starts, bool) or not isinstance(n_starts, int) or not 0 <= n_starts <= fitting.MAX_N_STARTS:
-            return _err(f"n_starts must be an integer between 0 and {fitting.MAX_N_STARTS}")
-        # "Is this component required?" (one extra fit; Auto-Fit asks for its anchor)
-        require_component = body.get("require_component")
-        if require_component is not None and not isinstance(require_component, (str, int)):
-            return _err("require_component must be a peak id")
-
-        try:
-            result = fitting.run_fit(
-                energy=energy,
-                counts=counts,
-                peak_specs=peak_specs,
-                background_method=bg_method,
-                bg_start_idx=bg_start,
-                bg_end_idx=bg_end,
-                charge_shift_ev=0.0,
-                fit_kws={"method": fit_method},
-                manual_bg=manual_bg,
-                n_perturb=n_perturb,
-                endpoint_avg=endpoint_avg,
-                n_starts=n_starts,
-                require_component=require_component,
-            )
-        except ValueError as exc:
-            # Our own validation: unknown shape/method, self/circular constraint,
-            # "Master peak not found", bad numeric field, etc. (audit F10/F11).
-            return _err(str(exc))
-        except RuntimeError:
-            # Solver-internal failure (e.g. lmfit non-convergence). Log the
-            # detail; return a generic 422 that leaks no library internals.
-            app.logger.exception("Fit failed")
-            return _err("Fit failed — see server log for details.", 422)
-        except Exception:
-            app.logger.exception("Unexpected fitting error")
-            return _err("Internal fitting error — see server log.", 500)
-
-        return jsonify(result)
+        fit_args, error = _prepare_fit_request(app, body)
+        if error is not None:
+            return error
+        status, out = _run_fit_outcome(app, fit_args)
+        if status != 200:
+            return _err(out["error"], status)
+        return jsonify(out)
 
     # ── Autofit analyze (opt-in Find Peaks; STRICTLY ADDITIVE — the manual
     #    /api/fit path above is untouched) ──────────────────────────────────
@@ -1060,6 +1209,54 @@ def _register_routes(app: Flask) -> None:
                     "message": "starting analysis…"}
         return jsonify(data)
 
+    # ── Long fits via start-then-poll (unit 2, 2026-09-27) ───────────────────
+    # The public URL ends a proxied request at ~100 s (Cloudflare 524; 88 s
+    # passed, 125 s failed); basinhopping on the large C 1s models takes 3–4
+    # minutes. The fit runs in a background thread on Find Peaks' job
+    # infrastructure (an atomic JSON record under the upload folder, readable
+    # by whichever gunicorn worker serves a poll); every HTTP request is short.
+    # The record: {status: running|done|error|cancelled, elapsed_sec,
+    # heartbeat (epoch s, rewritten every 2 s while the fit thread lives),
+    # result (done: EXACTLY the /api/fit body), error + http_status (error:
+    # exactly what /api/fit would have answered)}.
+
+    @app.post("/api/fit/start")
+    @_require_json
+    def fit_start():
+        body = request.get_json(silent=True)
+        if not isinstance(body, dict):
+            return _err("request body must be a JSON object")
+        fit_args, error = _prepare_fit_request(app, body)
+        if error is not None:
+            return error
+        upload_folder = app.config["UPLOAD_FOLDER"]
+        job_id = str(uuid.uuid4())
+        _sweep_expired_jobs(upload_folder)
+        _sweep_fit_job_markers(upload_folder)
+        _fit_job_start(job_id, upload_folder, fit_args,
+                       lambda args, cancel: _run_fit_outcome(app, args, cancel=cancel))
+        return jsonify({"job_id": job_id}), 202
+
+    @app.get("/api/fit/progress/<job_id>")
+    def fit_progress(job_id):
+        try:
+            uuid.UUID(job_id)
+        except ValueError:
+            return _err("Invalid job_id format (expected UUID)", 400)
+        data = _fit_job_read(job_id, app.config["UPLOAD_FOLDER"])
+        if data is None:
+            return _err(f"Job '{job_id}' not found", 404)
+        return app.response_class(json.dumps(data, allow_nan=True), mimetype="application/json")
+
+    @app.post("/api/fit/cancel/<job_id>")
+    def fit_cancel(job_id):
+        try:
+            uuid.UUID(job_id)
+        except ValueError:
+            return _err("Invalid job_id format (expected UUID)", 400)
+        _fit_job_cancel(job_id, app.config["UPLOAD_FOLDER"])
+        return jsonify({"cancelled": True})
+
     # ── Health check ──────────────────────────────────────────────────────────
 
     @app.get("/api/health")
diff --git a/fitting.py b/fitting.py
index 63785a8..eab9baa 100644
--- a/fitting.py
+++ b/fitting.py
@@ -26,6 +26,8 @@ import hashlib
 import json
 import logging
 import re
+import threading
+import time
 import warnings
 from typing import Any
 
@@ -979,6 +981,44 @@ def _make_peak_params(
     return p
 
 
+# ── Cancellation (unit 2, 2026-09-27: long fits via start-then-poll) ────────
+# A fit started through /api/fit/start runs in a background thread; the page
+# can abandon it (a re-run, a tab switch, an edited model, a closed tab). The
+# job passes ``run_fit(..., cancel=callable)``; inside that thread every
+# model.fit below receives an ``iter_cb`` that returns True — lmfit's abort —
+# once ``cancel()`` is true (checked at most every 0.25 s). Thread-local, so a
+# concurrent fit in another thread of the same worker is untouched; and
+# WITHOUT a cancel callable no ``iter_cb`` argument is passed at all, so every
+# synchronous call is made exactly as before. Never part of fit_kws: the
+# request seed cannot see it.
+_CANCEL = threading.local()
+
+
+class FitCancelled(RuntimeError):
+    """The job was cancelled while run_fit ran."""
+
+
+def _cancel_kw() -> dict:
+    fn = getattr(_CANCEL, "fn", None)
+    if fn is None:
+        return {}
+    state = {"t": 0.0, "hit": False}
+
+    def iter_cb(params, it, resid, *args, **kws):
+        if state["hit"]:
+            return True
+        now = time.monotonic()
+        if now - state["t"] >= 0.25:
+            state["t"] = now
+            if fn():
+                state["hit"] = True
+                _CANCEL.hit = True
+                return True
+        return None
+
+    return {"iter_cb": iter_cb}
+
+
 def _finite_search_box(params: Parameters, x: np.ndarray,
                        y_sub: np.ndarray) -> dict[str, dict[str, float]]:
     """Give every freely varying parameter a finite box, in place.
@@ -1062,7 +1102,7 @@ def _search_then_refine(model, params, requested, y_sub, x, weights, kws):
     for name, (lo, hi) in requested.items():
         boxed[name].set(min=lo, max=hi)
     generated = _finite_search_box(boxed, x, y_sub)
-    found = model.fit(y_sub, boxed, x=x, weights=weights, **kws)
+    found = model.fit(y_sub, boxed, x=x, weights=weights, **kws, **_cancel_kw())
     found.box_unverified, found.search_box = bool(generated), generated
     if not generated:
         return found
@@ -1073,7 +1113,7 @@ def _search_then_refine(model, params, requested, y_sub, x, weights, kws):
     # passed through fit_kws would make least_squares raise.
     refine_kws = {"method": "least_squares", "nan_policy": kws.get("nan_policy", "omit")}
     try:
-        refined = model.fit(y_sub, free, x=x, weights=weights, **refine_kws)
+        refined = model.fit(y_sub, free, x=x, weights=weights, **refine_kws, **_cancel_kw())
     except Exception:
         log.debug("refinement outside the search box raised", exc_info=True)
         return found
@@ -1111,7 +1151,7 @@ def _global_or_local_candidate(model, params, requested, y_sub, x, weights, kws)
         start[name].set(min=lo, max=hi)
     try:
         local = model.fit(y_sub, start, x=x, weights=weights,
-                          method="least_squares", nan_policy=kws.get("nan_policy", "omit"))
+                          method="least_squares", nan_policy=kws.get("nan_policy", "omit"), **_cancel_kw())
     except Exception:
         log.debug("local candidate from the start raised", exc_info=True)
         return searched
@@ -1147,11 +1187,11 @@ def _basinhopping_candidate(model, params, requested, y_sub, x, weights, kws):
     start = params.copy()
     for name, (lo, hi) in requested.items():
         start[name].set(min=lo, max=hi)
-    found = model.fit(y_sub, start.copy(), x=x, weights=weights, **kws)
+    found = model.fit(y_sub, start.copy(), x=x, weights=weights, **kws, **_cancel_kw())
     candidate = None
     try:   # from wherever the search stopped, even an evaluation-budget abort (as DE)
         refined = model.fit(y_sub, found.params.copy(), x=x, weights=weights,
-                            method="least_squares", nan_policy=nan_policy)
+                            method="least_squares", nan_policy=nan_policy, **_cancel_kw())
         if refined.success:
             candidate = refined
     except Exception:
@@ -1163,7 +1203,8 @@ def _basinhopping_candidate(model, params, requested, y_sub, x, weights, kws):
                          "so the result is not a verified fit")
         candidate = found
     try:
-        local = model.fit(y_sub, start.copy(), x=x, weights=weights, method="least_squares", nan_policy=nan_policy)
+        local = model.fit(y_sub, start.copy(), x=x, weights=weights, method="least_squares", nan_policy=nan_policy,
+                          **_cancel_kw())
     except Exception:
         log.debug("local candidate from the start raised", exc_info=True)
         return candidate
@@ -1489,7 +1530,7 @@ def _component_required(fit_reduced, params_full, removed_prefixes, y_sub, weigh
 # Main fitting API
 # ─────────────────────────────────────────────────────────────────────────────
 
-def run_fit(
+def _run_fit_impl(
     energy: np.ndarray,
     counts: np.ndarray,
     peak_specs: list[dict[str, Any]],
@@ -1750,7 +1791,7 @@ def run_fit(
         if kws.get("method") == "basinhopping":
             bounds = {name: requested_bounds.get(name, (par.min, par.max)) for name, par in params.items()}
             return _basinhopping_candidate(model, params, bounds, y_sub, x, weights, seeded(kws))
-        return model.fit(y_sub, params, x=x, weights=weights, **seeded(kws))
+        return model.fit(y_sub, params, x=x, weights=weights, **seeded(kws), **_cancel_kw())
 
     def fit_once(params):
         return fit_model(composite_model, params)
@@ -2048,3 +2089,27 @@ def compute_background_only(
         "background": bg.tolist(),
         "net_counts": (y - bg).tolist(),
     }
+
+
+def run_fit(*args, cancel=None, **kwargs):
+    """Fit peaks — see ``_run_fit_impl`` for every argument and the result.
+
+    ``cancel`` (optional, unit 2): a callable polled during the fit; once it
+    returns true every remaining minimisation aborts and ``FitCancelled`` is
+    raised instead of a result. Without it this is exactly the synchronous fit
+    it always was (no ``iter_cb`` reaches any minimiser)."""
+    if cancel is None:
+        return _run_fit_impl(*args, **kwargs)
+    _CANCEL.fn, _CANCEL.hit = cancel, False
+    try:
+        result = _run_fit_impl(*args, **kwargs)
+    finally:
+        hit = getattr(_CANCEL, "hit", False)
+        _CANCEL.fn, _CANCEL.hit = None, False
+    if hit:
+        raise FitCancelled("the fit was cancelled")
+    return result
+
+
+run_fit.__wrapped__ = _run_fit_impl
+

exec
/bin/zsh -lc "git diff fix-acceptance-holes..HEAD -- templates/index.html; rg -n 'runFit\\(|async function runFit|async function runAutoFit|fit-btn|btn-fit|_showFitSpinner|_hideFitSpinner|_ownerActive' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Rd4x65sE' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-S2RytztU' (errno=Operation not permitted)
diff --git a/templates/index.html b/templates/index.html
index 0f4e530..72a215e 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -7445,6 +7445,116 @@ async function _readFitReply(resp) {
   }
 }
 
+// ── Long fits via start-then-poll (unit 2, 2026-09-27) ──────────────────────
+// The public URL ends a proxied request at ~100 s (Cloudflare 524); a
+// basinhopping fit of a large C 1s model takes 3–4 minutes. So the fit is
+// STARTED (/api/fit/start: the same validation as /api/fit, an immediate 400
+// for a bad request, else 202 + a job id) and POLLED (/api/fit/progress, a
+// short request every FIT_POLL_MS); no request of this path lasts longer than
+// a poll. The final record's `result` is exactly the body /api/fit returns,
+// read with F2's rules (_readFitReply: a body read but not JSON — a NaN — is
+// the server's failed fit). The caller's ownership rules run INSIDE the loop:
+// `guard.abandoned()` returning a reason ('tab' | 'model') cancels the job on
+// the server and returns { _abandoned: reason } — the caller discards with
+// its usual message. Transport: a START that cannot reach the server is a
+// transport failure (the caller's local fallback, as before); a poll that
+// cannot is retried and only FIT_POLL_TRANSPORT_RETRIES in a row are. A
+// record whose heartbeat stops (a restarted worker takes the fit thread with
+// it) is a failed fit, never an endless spinner. Cancellation also reaches
+// the server when the page is closed (pagehide beacon) and, server-side,
+// when polls stop for three minutes (above the ~1-minute timer throttling of a hidden browser tab).
+const FIT_POLL_MS = 500;
+const FIT_POLL_TRANSPORT_RETRIES = 5;
+const FIT_HEARTBEAT_LOST_SEC = 30;
+const _runningFitJobs = new Set();
+function _cancelFitJob(jobId) {
+  try { fetch('/api/fit/cancel/' + encodeURIComponent(jobId), { method: 'POST', keepalive: true }).catch(() => {}); } catch (_) { /* best effort */ }
+}
+if (typeof window !== 'undefined' && window.addEventListener) {
+  window.addEventListener('pagehide', () => {
+    for (const id of _runningFitJobs) {
+      try { navigator.sendBeacon('/api/fit/cancel/' + encodeURIComponent(id)); } catch (_) { /* best effort */ }
+    }
+  });
+}
+function _fitHttpError(status, msg, prefix) {
+  const err = new Error(msg || ((prefix || 'Fit request failed') + ' (HTTP ' + status + ').'));
+  err.serverError = true;
+  err.httpStatus = status;
+  return err;
+}
+async function _serverFitJob(fitReq, guard) {
+  guard = guard || {};
+  const isTransport = e => e && !e.serverError && (e instanceof TypeError || e.name === 'AbortError');
+  let resp;
+  try {
+    resp = await fetch('/api/fit/start', { method: 'POST', headers: { 'Content-Type': 'application/json' },
+                                           body: JSON.stringify(fitReq), signal: guard.signal });
+  } catch (e) { if (isTransport(e)) e.transportFailure = true; throw e; }
+  if (resp.ok === false) {
+    let msg = null;
+    try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
+    throw _fitHttpError(resp.status, msg);
+  }
+  let started;
+  try { started = await _readFitReply(resp); } catch (e) { if (isTransport(e)) e.transportFailure = true; throw e; }
+  const jobId = started && started.job_id;
+  if (!jobId) throw _fitHttpError(resp.status, 'The server did not start the fit (no job id).');
+  _runningFitJobs.add(jobId);
+  let misses = 0;
+  try {
+    while (true) {
+      await new Promise(r => setTimeout(r, FIT_POLL_MS));
+      if (guard.signal && guard.signal.aborted) {
+        _cancelFitJob(jobId);
+        throw guard.signal.reason || new DOMException('aborted', 'AbortError');
+      }
+      const why = guard.abandoned ? guard.abandoned() : null;
+      if (why) { _cancelFitJob(jobId); return { _abandoned: why }; }
+      let pr, rec;
+      try {
+        pr = await fetch('/api/fit/progress/' + encodeURIComponent(jobId), { signal: guard.signal });
+      } catch (e) {
+        if (e && e.name === 'AbortError') { _cancelFitJob(jobId); throw e; }
+        if (++misses >= FIT_POLL_TRANSPORT_RETRIES) {
+          _cancelFitJob(jobId);
+          const err = new Error('Lost contact with the server during the fit (' + ((e && e.message) || 'network error') + ').');
+          err.transportFailure = true;
+          throw err;
+        }
+        continue;
+      }
+      if (pr.ok === false) {
+        _cancelFitJob(jobId);
+        let msg = null;
+        try { const j = await pr.json(); msg = (j && j.error) || null; } catch (_) { /* non-JSON body */ }
+        throw _fitHttpError(pr.status, msg, 'Lost the fit\'s progress');
+      }
+      try { rec = await _readFitReply(pr); } catch (e) {
+        if (e && e.unreadableReply) { _cancelFitJob(jobId); throw e; }
+        if (++misses >= FIT_POLL_TRANSPORT_RETRIES) {
+          _cancelFitJob(jobId);
+          if (isTransport(e)) e.transportFailure = true;
+          throw e;
+        }
+        continue;
+      }
+      misses = 0;
+      if (rec.status === 'done') return rec.result;
+      if (rec.status === 'error') throw _fitHttpError(rec.http_status || 500, rec.error);
+      if (rec.status === 'cancelled') throw _fitHttpError(409, 'The fit was stopped on the server before it finished. Run it again.');
+      if (Number.isFinite(rec.heartbeat_age_sec) && rec.heartbeat_age_sec > FIT_HEARTBEAT_LOST_SEC) {
+        _cancelFitJob(jobId);
+        throw _fitHttpError(503, 'The server stopped working on the fit (no sign of it for ' + Math.round(rec.heartbeat_age_sec) +
+                                 ' s — it was probably restarted). Run the fit again.');
+      }
+      if (typeof guard.onProgress === 'function') guard.onProgress(rec);
+    }
+  } finally {
+    _runningFitJobs.delete(jobId);
+  }
+}
+
 async function runAutoFitC1sGraphite() {
   // Pre-conditions
   if (!state.rawBE || !state.rawBE.length) { notify('Load a spectrum first.', 'amber'); return; }
@@ -7559,10 +7669,8 @@ async function runAutoFitC1sGraphite() {
       bgPayload.manual_bg = _getManualAnchors().map(a => [a.x, a.y]);
     }
     const sessionId = await uploadToBackend(be2, inten2);   // after EVERY input above is captured
-    const resp = await fetch('/api/fit', {
-      method: 'POST',
-      headers: { 'Content-Type': 'application/json' },
-      body: JSON.stringify({
+    // Unit 2: started and polled, like Run Fit (the 2-minute abort still applies)
+    const json = await _serverFitJob({
         session_id: sessionId,
         background: bgPayload,
         peaks: peakSpecs,
@@ -7572,21 +7680,26 @@ async function runAutoFitC1sGraphite() {
         // the model without it; a redundant anchor must not set the energy
         // reference of a whole spectrum (see applyAutoFitResult).
         require_component: anchorId,
-      }),
+    }, {
       signal: ctrl.signal,
+      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
     });
     clearTimeout(timer);
-    // F2: a non-2xx reply is a failed REQUEST with its status in the message,
-    // as Run Fit has done since A0 (a Cloudflare 524 or a gunicorn 500 used to
-    // reach the parser and read as "the server's reply could not be read")
-    if (resp.ok === false) {
-      let msg = null;
-      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
-      const err = new Error(msg || ('Fit request failed (HTTP ' + resp.status + ').'));
-      err.httpStatus = resp.status;
-      throw err;
+    // F2: a non-2xx reply is a failed REQUEST with its status in the message
+    // (_serverFitJob throws it with httpStatus); an unreadable reply is a
+    // failed fit with its own message (unreadableReply).
+    if (json && json._abandoned === 'tab') {
+      _hideFitSpinner();
+      notify('Auto-fit discarded — tab switched during fit.', 'amber');
+      _autoFitRestore(snap, fittingTab);
+      return;
+    }
+    if (json && json._abandoned === 'model') {
+      _hideFitSpinner();
+      notify('Auto-fit discarded because the model or its background / ROI settings were edited while it was running. Previous peaks and result restored. Run it again.', 'amber', true);
+      _autoFitRestore(snap, fittingTab);
+      return;
     }
-    const json = await _readFitReply(resp);   // F2: an unreadable reply is a failed fit with its own message
     if (json.error) throw new Error(json.error);
     if (json.success !== true) throw new Error(json.message || 'fit did not converge');
     if (!_ownerActive(fittingTab)) {
@@ -8053,26 +8166,27 @@ async function runFit(opts = {}) {
       n_perturb: 3,
       n_starts: nStarts       // the server also skips it for the global methods
     };
-    let resp, json;
-    try {
-      resp = await fetch('/api/fit', {
-        method: 'POST',
-        headers: { 'Content-Type': 'application/json' },
-        body: JSON.stringify(fitReq)
-      });
-    } catch (e) { _asTransport(e); }
-    if (resp.ok === false) {
-      // HTTP failure: read a message if the body is JSON, but a 502 HTML
-      // page is still a SERVER failure, never a reason to switch engines.
-      let msg = null;
-      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
-      const err = new Error(msg || ('Fit request failed (HTTP ' + resp.status + ').'));
-      err.serverError = true;
-      throw err;
+    // Unit 2: started and polled (_serverFitJob) — no request lasts longer than
+    // a poll, so none meets the public URL's ~100 s ceiling. An HTTP failure is
+    // a SERVER failure (serverError), never a reason to switch engines; a
+    // START that cannot reach the server is a transport failure, as the single
+    // request was. The ownership checks below also run inside the poll loop,
+    // so a switched tab or an edited model stops the server's work at once.
+    const json = await _serverFitJob(fitReq, {
+      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
+    });
+    if (json && json._abandoned === 'tab') {
+      _hideFitSpinner();
+      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
+      notify('Fit result discarded because you switched tabs during the fit.', 'amber');
+      return;
+    }
+    if (json && json._abandoned === 'model') {
+      _hideFitSpinner();
+      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
+      notify('Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.', 'amber', true);
+      return;
     }
-    // F2: reading the body can fail in transport; a body that was read but is
-    // not JSON is the server's reply — a failed fit, not a fallback
-    try { json = await _readFitReply(resp); } catch (e) { _asTransport(e); }
     if (json.error) {
       const err = new Error(json.error);
       err.serverError = true;
1904:      <button class="btn btn-green peak-fit-control" id="btn-run-fit" onclick="runFit()">Run Fit</button>
2354:function _ownerActive(owner) {
5894:    if (k === 'f')                 { e.preventDefault(); runFit(); return; }
6688:function _showFitSpinner() {
6697:  _showFitSpinner._timer = setTimeout(() => {
6701:function _hideFitSpinner() {
6705:  clearTimeout(_showFitSpinner._timer);
7343:  // 5. Build state.fitResult exactly as runFit() does.
7362:  // 6. Update the same DOM elements runFit() updates.
7558:async function runAutoFitC1sGraphite() {
7575:    if (!_ownerActive(fittingTab)) {
7627:  _showFitSpinner();
7685:      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
7692:      _hideFitSpinner();
7698:      _hideFitSpinner();
7705:    if (!_ownerActive(fittingTab)) {
7706:      _hideFitSpinner();
7712:      _hideFitSpinner();
7722:      _hideFitSpinner();
7727:    _hideFitSpinner();
7731:    _hideFitSpinner();
8095:  await runFit({ startPeaks: peaks, chosenAlternative: chosen });
8098:async function runFit(opts = {}) {
8103:  _showFitSpinner();
8176:      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
8179:      _hideFitSpinner();
8185:      _hideFitSpinner();
8207:    if (!_ownerActive(fittingTab)) {
8208:      _hideFitSpinner();
8218:      _hideFitSpinner();
8249:    _hideFitSpinner();
8253:    _hideFitSpinner();
8254:    if (!_ownerActive(fittingTab)) {
8269:      _hideFitSpinner();
8442:    _hideFitSpinner();
8803:  _hideFitSpinner();
10810:      if (!_ownerActive(owner)) { notify('Fit file not applied — the tab changed while the file was being read.', 'amber'); return; }
10828:      if (!_ownerActive(owner)) { notify('Fit file not applied — the tab changed while the file was being read.', 'amber'); return; }
16127:    if (!_ownerActive(owner)) {
16310:  if (!_ownerActive(owner)) {

exec
/bin/zsh -lc "sed -n '2335,2370p' templates/index.html; sed -n '6670,6720p' templates/index.html; sed -n '7558,7755p' templates/index.html; sed -n '8098,8295p' templates/index.html; sed -n '1740,1930p' fitting.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
let _undoDebounceTimer = null;

// The one accessor for per-tab runtime state. null when no tab is active.
function _activeTab() {
  return (typeof tabManager !== 'undefined' && tabManager) ? tabManager._getTab(tabManager.activeId) : null;
}
// ASYNC OWNERSHIP RULE (Codex 2026-09-09 round 1, both runs): an operation
// that awaits — a fit, an analysis, a confirmation, a file read, a timer —
// captures the RECORD OBJECT it started on (and its inputs) before the first
// await, and afterwards either writes to that object or checks that it is
// still the active one. Persisted ids are not identity: a closed tab's id
// comes back on a NEW object after a project reload.
function _opOwner() {
  const t = _activeTab();
  return (t && !t.isStack) ? t : null;
}
function _ownerLive(owner) {
  return !!owner && typeof tabManager !== 'undefined' && !!tabManager && tabManager.tabs.includes(owner);
}
function _ownerActive(owner) {
  return _ownerLive(owner) && _activeTab() === owner;
}
// The active SPECTRUM tab with its history containers ensured; null for no
// tab or a stack tab (stack tabs have no peaks and get no history).
function _historyTab() {
  const t = _activeTab();
  if (!t || t.isStack) return null;
  if (!t.undoStack) t.undoStack = [];
  if (!t.redoStack) t.redoStack = [];
  return t;
}

// Undo snapshots are deep copies of state.peaks. An action that ALSO changes
// endpoint averaging (today: applying Find Peaks suggestions, which sets the
// panel to what the engine fitted at) passes { endpointAvg } so the snapshot
// carries the pre-action value as a non-index property; undo/redo restore it
  for (const id of _BG_SUB_DEPENDENT_CONTROL_IDS) {
    const el = document.getElementById(id);
    if (!el) continue;
    el.disabled = subActive;
    // Apply opacity to the wrapping label so the visual disable is
    // obvious — matches the shirley-iter / bg-endpoint-avg pattern.
    const wrap = el.closest('label') || el.parentElement;
    if (wrap) wrap.style.opacity = subActive ? '0.4' : '1';
    if (subActive) {
      el.title = 'Unavailable in subtracted view. Toggle Bkgrd Sub off to enable.';
      if (wrap && wrap !== el) wrap.title = el.title;
    } else {
      el.title = '';
      if (wrap && wrap !== el) wrap.title = '';
    }
  }
}

function _showFitSpinner() {
  const overlay = document.getElementById('fit-spinner-overlay');
  const label = document.getElementById('fit-spinner-label');
  if (overlay) overlay.style.display = 'flex';
  if (label) label.innerHTML = 'Fitting<span class="ellipsis"></span>';
  document.querySelector('.btn-green').disabled = true;
  _bgSubFitInFlight = true;
  _updateBgSubPillEnabled();
  // After 2s, update label to hint at perturbations
  _showFitSpinner._timer = setTimeout(() => {
    if (label) label.innerHTML = 'Running perturbations<span class="ellipsis"></span>';
  }, 2000);
}
function _hideFitSpinner() {
  const overlay = document.getElementById('fit-spinner-overlay');
  if (overlay) overlay.style.display = 'none';
  document.querySelector('.btn-green').disabled = false;
  clearTimeout(_showFitSpinner._timer);
  _bgSubFitInFlight = false;
  _updateBgSubPillEnabled();
}

// Sync the Auto-Fit menu item's disabled state with the active tab.
// Called from activateTab and from ROI-input event handlers.
function _recomputeAutoFitMenuState() {
  const item = document.getElementById('auto-fit-c1s-menu-item');
  if (!item) return;
  const tab = (typeof tabManager !== 'undefined' && tabManager.activeId)
    ? tabManager._getTab(tabManager.activeId)
    : null;
  const enabled = !!tab && isC1sTab(tab);
  item.disabled = !enabled;
  if (enabled) {
async function runAutoFitC1sGraphite() {
  // Pre-conditions
  if (!state.rawBE || !state.rawBE.length) { notify('Load a spectrum first.', 'amber'); return; }
  const tab = tabManager._getTab(tabManager.activeId);
  if (!tab) { notify('No active tab.', 'amber'); return; }
  if (!isC1sTab(tab)) {
    notify('Auto-Fit C1s Graphite is only available for C1s spectra (ROI midpoint 270–315 eV).', 'amber');
    return;
  }
  // OWNER FIRST: the confirmation below is an await; the tab that is active
  // when it resolves may not be the one the user asked to auto-fit.
  const fittingTab = _opOwner();
  if (!fittingTab) { notify('No active spectrum tab.', 'amber'); return; }
  // Confirmation if existing peaks
  if (state.peaks.length >= 1) {
    const proceed = await _showAutoFitConfirmModal(state.peaks.length);
    if (!proceed) return;
    if (!_ownerActive(fittingTab)) {
      notify('Auto-fit cancelled — the tab changed while the confirmation was open.', 'amber');
      return;
    }
  }

  // Snapshot for failure rollback (separate from pushUndo, which only covers peaks).
  const snap = _autoFitSnapshot();

  // Step 1: find graphite in raw BE
  const { be: corrBE, inten } = getROIData();
  if (!corrBE.length) {
    notify('ROI is empty. Set roi-min and roi-max before auto-fit.', 'red', true);
    return;
  }
  const bgI = computeBackground(corrBE, inten);
  const bgSub = inten.map((v, i) => v - bgI[i]);
  // App convention: raw = corrected + state.ccShift
  const curShift = Number.isFinite(state.ccShift) ? state.ccShift : 0;
  const rawBE = corrBE.map(b => b + curShift);
  const graphiteRaw = findGraphiteRawBE(rawBE, bgSub);
  if (graphiteRaw == null) {
    notify('No strong peak found in the C1s ROI; Auto-Fit cannot proceed.', 'red', true);
    return;
  }

  // Step 2: provisional shift (APP CONVENTION).
  const provisionalShift = graphiteRaw - 284.50;

  // Step 3: assess low-BE region using provisional shift (no state mutation yet).
  const assessment = assessLowBERegion(rawBE, bgSub, provisionalShift);

  // Step 4: build the peak model (in corrected frame after provisional shift).
  pushUndo();
  state.peaks = [];
  state.fitResult = null;
  // Apply provisional shift via updateChargeCorrection so ROI/bg DOM fields
  // shift along with state.ccShift.
  const cm = document.getElementById('cc-method');
  const co = document.getElementById('cc-obs');
  const cl = document.getElementById('cc-lit');
  cm.value = 'c1s';
  co.value = graphiteRaw.toFixed(3);
  cl.value = '284.50';
  updateChargeCorrection();
  // Now build the peak list (graphite center 284.50 in this frame).
  const newPeaks = buildAutoFitModel(assessment);
  state.peaks = newPeaks;
  state.nextId = Math.max(0, ...state.peaks.map(p => p.id)) + 1;
  renderPeakList();

  // Step 5: run /api/fit with AbortController + spinner.
  _showFitSpinner();
  const spinLabel = document.getElementById('fit-spinner-label');
  if (spinLabel) spinLabel.textContent = 'Auto-fitting…';
  const runBtn = document.querySelector('.btn-green');
  if (runBtn) runBtn.disabled = true;

  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(new DOMException('timeout', 'AbortError')), 120000);

  try {
    const { be: be2, inten: inten2 } = getROIData();
    const bgType = document.getElementById('bg-type').value;
    const bgStart = parseFloat(document.getElementById('bg-start').value);
    const bgEnd = parseFloat(document.getElementById('bg-end').value);
    // Inclusive bg window — the same point set computeBackgroundCore draws;
    // the backend slices end-exclusive, so the request sends i1 + 1.
    const bgWin = _bgWindowIndices(be2, bgStart, bgEnd);
    const epAvg = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
    const fitMethod = document.getElementById('fit-method').value;

    // The anchor whose necessity the server must test — captured with the
    // other request inputs, before the first await (a tab switch during the
    // upload must not send another tab's id).
    const anchorId = String((state.peaks.find(p => p.name === 'Graphite') || state.peaks[0]).id);
    // the model and its fit context as sent (F1, Codex round 1): a result must
    // not be applied, and stamped current, over a model edited while it ran
    const ctxAtRequest = _startsLiveKey();
    // Build peak specs and overlay the per-peak bounds we attached in buildAutoFitModel.
    const peakSpecs = state.peaks.map(p => {
      const spec = peakToBackendSpec(p);
      if (Number.isFinite(p._afCenterMin)) spec.center_min = p._afCenterMin;
      if (Number.isFinite(p._afCenterMax)) spec.center_max = p._afCenterMax;
      if (Number.isFinite(p._afFwhmMin))   spec.fwhm_min   = p._afFwhmMin;
      if (Number.isFinite(p._afFwhmMax))   spec.fwhm_max   = p._afFwhmMax;
      spec.amplitude_min = 0;
      return spec;
    });

    const bgPayload = { method: bgType, start_idx: bgWin.i0, end_idx: bgWin.i1 + 1, endpoint_avg: epAvg };
    if (bgType === 'manual') {
      // Anchors are stored in corrected-BE space, same frame as the uploaded
      // session data; backend expects [x, y] pairs.
      bgPayload.manual_bg = _getManualAnchors().map(a => [a.x, a.y]);
    }
    const sessionId = await uploadToBackend(be2, inten2);   // after EVERY input above is captured
    // Unit 2: started and polled, like Run Fit (the 2-minute abort still applies)
    const json = await _serverFitJob({
        session_id: sessionId,
        background: bgPayload,
        peaks: peakSpecs,
        fit_method: fitMethod,
        n_perturb: 3,
        // step (c): is the charge-reference anchor REQUIRED? The server refits
        // the model without it; a redundant anchor must not set the energy
        // reference of a whole spectrum (see applyAutoFitResult).
        require_component: anchorId,
    }, {
      signal: ctrl.signal,
      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
    });
    clearTimeout(timer);
    // F2: a non-2xx reply is a failed REQUEST with its status in the message
    // (_serverFitJob throws it with httpStatus); an unreadable reply is a
    // failed fit with its own message (unreadableReply).
    if (json && json._abandoned === 'tab') {
      _hideFitSpinner();
      notify('Auto-fit discarded — tab switched during fit.', 'amber');
      _autoFitRestore(snap, fittingTab);
      return;
    }
    if (json && json._abandoned === 'model') {
      _hideFitSpinner();
      notify('Auto-fit discarded because the model or its background / ROI settings were edited while it was running. Previous peaks and result restored. Run it again.', 'amber', true);
      _autoFitRestore(snap, fittingTab);
      return;
    }
    if (json.error) throw new Error(json.error);
    if (json.success !== true) throw new Error(json.message || 'fit did not converge');
    if (!_ownerActive(fittingTab)) {
      _hideFitSpinner();
      notify('Auto-fit discarded — tab switched during fit.', 'amber');
      _autoFitRestore(snap, fittingTab);
      return;
    }
    if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
      _hideFitSpinner();
      notify('Auto-fit discarded because the model or its background / ROI settings were edited while it was running. Previous peaks and result restored. Run it again.', 'amber', true);
      _autoFitRestore(snap, fittingTab);
      return;
    }

    applyBackendResult(json);

    const ok = applyAutoFitResult(json, graphiteRaw, { be: be2, inten: inten2, bgIntensity: bgI, bgSubtracted: bgSub });
    if (!ok) {
      _hideFitSpinner();
      _autoFitRestore(snap, fittingTab);
      return;
    }

    _hideFitSpinner();
    notify('Auto-fit complete. χ²ᵣ = ' + (state.fitResult?.chiReduced?.toFixed(3) || '?'), 'green');
  } catch (e) {
    clearTimeout(timer);
    _hideFitSpinner();
    // The catch path can also fire after a mid-flight tab switch (fetch
    // error/timeout after the user moved on) — same wrong-tab hazard as
    // the explicit discard branch, so it gets the same tab-aware restore.
    _autoFitRestore(snap, fittingTab);
    let msg;
    if (e && (e.name === 'AbortError' || (e.message && e.message.toLowerCase().includes('aborted')))) {
      msg = 'Auto-fit exceeded the 2-minute timeout.';
    } else if (e && (e.unreadableReply || e.httpStatus)) {
      msg = 'Auto-fit failed: ' + e.message;
    } else if (e && e.message) {
      msg = 'Fit failed to converge or produced an unphysical graphite position.';
      console.warn('Auto-fit error:', e);
    } else {
      msg = 'Auto-fit failed.';
    }
    notify(msg, 'red', true);
  }
}

function isC1sTab(tab) {
  if (!tab || !tab.rawBE || !tab.rawBE.length) return false;
  const ui = tab.ui || {};
  let lo = parseFloat(ui.roiMin);
  let hi = parseFloat(ui.roiMax);
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
  let ctxAtRequest = null;   // set with the other request inputs; read again by the local fallback
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
    ctxAtRequest = _startsLiveKey();
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
    // Only a genuine transport failure (network rejection, abort, a body that
    // could not be read) is marked for fallback; server errors — including a
    // 2xx body that was read but is not JSON (F2) — carry `serverError`.
    const _asTransport = (e) => {
      if (e && !e.serverError && (e instanceof TypeError || e.name === 'AbortError' || e instanceof SyntaxError)) e.transportFailure = true;
      throw e;
    };
    let sessionId;
    try { sessionId = await uploadToBackend(be, inten); } catch (e) { _asTransport(e); }
    const fitReq = {
      session_id: sessionId,
      background: bgPayload,
      peaks: peakSpecs,
      fit_method: fitMethod,
      n_perturb: 3,
      n_starts: nStarts       // the server also skips it for the global methods
    };
    // Unit 2: started and polled (_serverFitJob) — no request lasts longer than
    // a poll, so none meets the public URL's ~100 s ceiling. An HTTP failure is
    // a SERVER failure (serverError), never a reason to switch engines; a
    // START that cannot reach the server is a transport failure, as the single
    // request was. The ownership checks below also run inside the poll loop,
    // so a switched tab or an edited model stops the server's work at once.
    const json = await _serverFitJob(fitReq, {
      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
    });
    if (json && json._abandoned === 'tab') {
      _hideFitSpinner();
      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
      notify('Fit result discarded because you switched tabs during the fit.', 'amber');
      return;
    }
    if (json && json._abandoned === 'model') {
      _hideFitSpinner();
      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
      notify('Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.', 'amber', true);
      return;
    }
    if (json.error) {
      const err = new Error(json.error);
      err.serverError = true;
      throw err;
    }
    // ACCEPTANCE RULE: the backend reports lmfit's own convergence flag. A
    // result that did not converge is a failed fit, not a result (audit A08:
    // until this unit success:false was applied and announced as complete).
    if (json.success !== true) {
      const err = new Error(json.message || 'the optimizer did not converge.');
      err.notConverged = true;
      throw err;
    }
    backendResult = json;

    // If the user switched tabs while the fit was running, discard the result
    // rather than overwriting the now-active tab's peaks.
    if (!_ownerActive(fittingTab)) {
      _hideFitSpinner();
      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
      notify('Fit result discarded because you switched tabs during the fit.', 'amber');
      return;
    }

    // The peak controls stay editable while the fit runs. A result computed for
    // the model as it was must not be applied over an edited one (a newly locked
    // centre would keep its edited value under the server's statistics).
    if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
      _hideFitSpinner();
      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
      notify('Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.', 'amber', true);
      return;
    }

    // Capture pre-fit values for uncertainty validation
    const _preFit = {};
    for (const p of state.peaks) {
      _preFit[p.id] = { center: p.center, fwhm: p.fwhm, amplitude: p.amplitude, glMix: p.glMix };
    }
    applyBackendResult(backendResult);
    { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }   // a new result supersedes imported provenance
    const stats = backendResult.statistics || {};
    const chiReduced = stats.reduced_chi_square || 0;
    const rmse = Math.sqrt((backendResult.residuals || []).reduce((s, v) => s + v * v, 0) / Math.max(1, be.length));
    const roiRange = { min: _arrMin(be).toFixed(1), max: _arrMax(be).toFixed(1) };
    state.fitResult = { chi: chiReduced * Math.max(1, be.length - state.peaks.length * 3),
                        chiReduced, rmse, be, bgSubtracted, bgIntensity, backendResult,
                        fittedY: backendResult.fitted_y, roiRange, _preFit,
                        starts: backendResult.starts || null,
                        startsModelKey: _startsLiveKey(),     // model + context, taken AFTER the result was applied
                        chosenAlternative: opts.chosenAlternative || null };
    // a preview of an alternative always belongs to the PREVIOUS result (an identical
    // key does not make it this one's): clear it unconditionally
    if (_historyPreview && typeof _historyPreview.snapId === 'string' && _historyPreview.snapId.startsWith('alt:')) _historyPreview = null;
    state.fitResult.rFactor = _computeRFactor(state.fitResult);
    _applyStatDisplay(state.fitResult);
    document.getElementById('sb-msg').textContent = 'Fit complete (lmfit)';
    _updateRFactorUI(state.fitResult.rFactor);
    _updateROIDisplay(roiRange);
    _hideFitSpinner();
    notify('Fit complete. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3), 'green');
  } catch (e) {
    // Fall back to local Levenberg-Marquardt
    _hideFitSpinner();
    if (!_ownerActive(fittingTab)) {
      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
      notify('Fit cancelled — tab switched during fit.', 'amber');
      return;
    }
    if (e && e.transportFailure && opts.startPeaks) {
      // Adopting an alternative needs the server: the local engine would start
      // from the live model, not from the alternative. Nothing was changed.
      document.getElementById('sb-msg').textContent = 'Fit failed';
      notify('The server could not be reached, so the alternative was not applied. Previous peaks and result kept.', 'red', true);
      return;
    }
    if (e && e.transportFailure && ctxAtRequest !== null && !_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
      // The fallback would fit the arrays captured at the press over a model or
      // context edited since, and stamp the edited one (F1, Codex round 1).
      _hideFitSpinner();
      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
      notify('The server could not be reached, and the model or its background / ROI settings were edited while the fit was running, so no local fit was run. Previous peaks and result kept. Run the fit again.', 'amber', true);
      return;
    }
    if (e && e.transportFailure) {
      // Server unreachable: the local optimiser is the honest fallback, and
      // the overlay saying so opens only if it actually converged.
      if (e.message) console.warn('Backend unreachable, falling back to local LM:', e.message);
      const local = runFitLocal(be, bgSubtracted, bgIntensity);
      if (local && local.success && !_snapshotSuppressed) {
        document.getElementById('localfit-warn-overlay').classList.add('open');
      }
      return;
    }
    // Server-side error or non-converged optimisation: report it; the
    // previous peaks and fit result stay exactly as they were.
    const notConverged = !!(e && e.notConverged);
    document.getElementById('sb-msg').textContent = notConverged ? 'Fit did not converge' : 'Fit failed';
    notify((notConverged ? 'Fit did not converge: ' : 'Fit failed: ') + ((e && e.message) || 'unknown error') +
           ' Previous peaks and result kept.', 'red', true);
    return;
  }

  renderPeakList();
  updatePlot();
  renderResults();
    # spawn(3) yields the same first two children as spawn(2): adding the
    # scattered-starts stream leaves every existing draw (and its pins) alone.
    perturb_rng, solver_rng, starts_rng = (np.random.default_rng(child)
                                           for child in np.random.SeedSequence(random_seed).spawn(3))
    if isinstance(n_starts, bool) or not isinstance(n_starts, (int, np.integer)) or not 0 <= n_starts <= MAX_N_STARTS:
        raise ValueError(f"n_starts must be an integer between 0 and {MAX_N_STARTS}")

    # ── Determinacy (unit F2, 2026-09-26) ─────────────────────────────────────
    # "Nothing is a fit unless it converged and is determined." With at least
    # as many free parameters as data points the model can pass through every
    # point: lmfit reports redchi = chi2 / max(1, nfree) as if it were a fit,
    # and the support / required F tests clamp their dof to 1, so such a model
    # read as a near-perfect, fully supported fit (sweep M2: 6 points, 2 GL
    # components, chi2r 2.8e-6, both "supported"). A count, not a threshold:
    # zero or negative degrees of freedom is refused outright.
    n_free_request = sum(1 for par in all_params.values() if par.vary and not par.expr)
    n_data_request = int(np.count_nonzero(np.isfinite(y_sub)))
    if n_free_request >= n_data_request:
        raise ValueError(
            f"The model is not determined by these data: {n_free_request} free parameters for "
            f"{n_data_request} data points leaves no degrees of freedom. Widen the fitted range, "
            f"remove components or lock parameters.")

    # ── Fit ───────────────────────────────────────────────────────────────────
    kws = {"method": "leastsq", "nan_policy": "omit"}
    if fit_kws:
        kws.update(fit_kws)

    # Differential evolution needs a finite box and the page leaves amplitudes
    # open above: each candidate is searched in a generated box and then
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
                log.exception("required-component refit failed")
                required = {"ran": False, "reason": "error", "error": f"{type(exc).__name__}: {exc}"[:200]}

    # Sides WE closed on the returned result (non-empty only for a
    # differential-evolution result whose refinement did not take over).

codex
The validation extraction and fit arguments match F2, and the shared lock protects the final record from late heartbeat writes. I’m now checking repeated-run cancellation and failure paths that could leave jobs running; those are not covered by the happy-path timing results.
exec
/bin/zsh -lc "sed -n '1730,1950p' fitting.py; sed -n '5860,5905p' templates/index.html; sed -n '490,550p' app.py; /Users/skyefortier/xps-app/venv/bin/python -B -c 'import lmfit,gunicorn; print(lmfit.__file__); print(gunicorn.__file__)'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
exec
/bin/zsh -lc 'node --test tests/js/fit_start_poll.test.js tests/js/fit_acceptance.test.js tests/js/stale_statistics.test.js tests/js/per_tab_state.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 374ms:
# Subtest: A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
ok 1 - A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
  ---
  duration_ms: 8.5041
  type: 'test'
  ...
# Subtest: a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
ok 2 - a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
  ---
  duration_ms: 4.786117
  type: 'test'
  ...
# Subtest: a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
ok 3 - a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
  ---
  duration_ms: 3.186824
  type: 'test'
  ...
# Subtest: a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
ok 4 - a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
  ---
  duration_ms: 10.331013
  type: 'test'
  ...
# Subtest: a converged backend result is applied (sanity)
ok 5 - a converged backend result is applied (sanity)
  ---
  duration_ms: 3.939867
  type: 'test'
  ...
# Subtest: the engine/objective labels of a fit result survive spectrum and project save/load
ok 6 - the engine/objective labels of a fit result survive spectrum and project save/load
  ---
  duration_ms: 0.764822
  type: 'test'
  ...
# Subtest: an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
ok 7 - an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
  ---
  duration_ms: 3.066777
  type: 'test'
  ...
# Subtest: an HTTP 502 on the upload is a server failure, not a transport failure
ok 8 - an HTTP 502 on the upload is a server failure, not a transport failure
  ---
  duration_ms: 2.968222
  type: 'test'
  ...
# Subtest: uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
ok 9 - uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
  ---
  duration_ms: 2.015027
  type: 'test'
  ...
# Subtest: every consumer that prints the goodness-of-fit statistic routes through the statistic identity
ok 10 - every consumer that prints the goodness-of-fit statistic routes through the statistic identity
  ---
  duration_ms: 0.965261
  type: 'test'
  ...
# Subtest: uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
ok 11 - uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
  ---
  duration_ms: 0.759101
  type: 'test'
  ...
# Subtest: a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
ok 12 - a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
  ---
  duration_ms: 1.677105
  type: 'test'
  ...
# Subtest: starting-point helpers: keyed on the persisted objective, weighted results untouched
ok 13 - starting-point helpers: keyed on the persisted objective, weighted results untouched
  ---
  duration_ms: 3.143304
  type: 'test'
  ...
# Subtest: Quantify shows the starting-point banner for a local result and not for a weighted one
ok 14 - Quantify shows the starting-point banner for a local result and not for a weighted one
  ---
  duration_ms: 5.725769
  type: 'test'
  ...
# Subtest: every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
ok 15 - every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
  ---
  duration_ms: 1.841798
  type: 'test'
  ...
# Subtest: project save derives the designation from the objective for an older local result lacking the new fields
ok 16 - project save derives the designation from the objective for an older local result lacking the new fields
  ---
  duration_ms: 10.207236
  type: 'test'
  ...
# Subtest: stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
ok 17 - stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
  ---
  duration_ms: 1.045647
  type: 'test'
  ...
# Subtest: _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
ok 18 - _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
  ---
  duration_ms: 3.342269
  type: 'test'
  ...
# Subtest: history preview glow is keyed on the dataset flag, not the label text
ok 19 - history preview glow is keyed on the dataset flag, not the label text
  ---
  duration_ms: 0.701461
  type: 'test'
  ...
# Subtest: spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
ok 20 - spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
  ---
  duration_ms: 0.534913
  type: 'test'
  ...
# Subtest: _applyStatDisplay clears header, tooltip, caption and value together on local → none
ok 21 - _applyStatDisplay clears header, tooltip, caption and value together on local → none
  ---
  duration_ms: 3.137065
  type: 'test'
  ...
# Subtest: _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
ok 22 - _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
  ---
  duration_ms: 1.722028
  type: 'test'
  ...
# Subtest: fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
ok 23 - fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
  ---
  duration_ms: 1.580823
  type: 'test'
  ...
# Subtest: undo/redo snapshots carry and restore model provenance
ok 24 - undo/redo snapshots carry and restore model provenance
  ---
  duration_ms: 3.603853
  type: 'test'
  ...
# Subtest: round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
ok 25 - round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
  ---
  duration_ms: 1.177694
  type: 'test'
  ...
# Subtest: _provenanceOf derives a designation from a live local result, and undo snapshots use it
ok 26 - _provenanceOf derives a designation from a live local result, and undo snapshots use it
  ---
  duration_ms: 2.804583
  type: 'test'
  ...
# Subtest: batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
ok 27 - batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
  ---
  duration_ms: 0.461976
  type: 'test'
  ...
# Subtest: the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
ok 28 - the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
  ---
  duration_ms: 2.452356
  type: 'test'
  ...
# Subtest: round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
ok 29 - round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
  ---
  duration_ms: 0.672048
  type: 'test'
  ...
# Subtest: the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
ok 30 - the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
  ---
  duration_ms: 2.668115
  type: 'test'
  ...
# Subtest: the sidebar banner is sticky at the top of the scrolling panel body
ok 31 - the sidebar banner is sticky at the top of the scrolling panel body
  ---
  duration_ms: 0.29306
  type: 'test'
  ...
# Subtest: the sidebar banner shows on a stack tab whose visible entries draw a local source fit
ok 32 - the sidebar banner shows on a stack tab whose visible entries draw a local source fit
  ---
  duration_ms: 3.779822
  type: 'test'
  ...
# Subtest: every stack chart repaint path refreshes the sidebar designation before any early return
ok 33 - every stack chart repaint path refreshes the sidebar designation before any early return
  ---
  duration_ms: 0.503263
  type: 'test'
  ...
# Subtest: closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
ok 34 - closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
  ---
  duration_ms: 0.253868
  type: 'test'
  ...
# Subtest: W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
ok 35 - W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
  ---
  duration_ms: 2.93441
  type: 'test'
  ...
# Subtest: TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
ok 36 - TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
  ---
  duration_ms: 4.110917
  type: 'test'
  ...
# Subtest: adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
ok 37 - adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
  ---
  duration_ms: 3.241908
  type: 'test'
  ...
# Subtest: adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
ok 38 - adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
  ---
  duration_ms: 2.954403
  type: 'test'
  ...
# Subtest: adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
ok 39 - adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
  ---
  duration_ms: 3.055145
  type: 'test'
  ...
# Subtest: adoption: success records the choice, the starts evidence and the key of the model it describes
ok 40 - adoption: success records the choice, the starts evidence and the key of the model it describes
  ---
  duration_ms: 3.526461
  type: 'test'
  ...
# Subtest: an ordinary Run Fit on one unlinked component does not ask for the starts check
ok 41 - an ordinary Run Fit on one unlinked component does not ask for the starts check
  ---
  duration_ms: 3.407242
  type: 'test'
  ...
# Subtest: a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
ok 42 - a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
  ---
  duration_ms: 3.844806
  type: 'test'
  ...
# Subtest: a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
ok 43 - a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
  ---
  duration_ms: 6.206204
  type: 'test'
  ...
# Subtest: a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
ok 44 - a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
  ---
  duration_ms: 3.244966
  type: 'test'
  ...
# Subtest: a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
ok 45 - a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
  ---
  duration_ms: 7.200503
  type: 'test'
  ...
# Subtest: the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)
ok 46 - the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)
  ---
  duration_ms: 0.92056
  type: 'test'
  ...
# Subtest: the token scan is linear and keeps a truncated string a string (Codex round 2)
ok 47 - the token scan is linear and keeps a truncated string a string (Codex round 2)
  ---
  duration_ms: 3.850163
  type: 'test'
  ...
# Subtest: start -> running polls -> done: the result is the /api/fit body; no job is left registered
ok 48 - start -> running polls -> done: the result is the /api/fit body; no job is left registered
  ---
  duration_ms: 10.431885
  type: 'test'
  ...
# Subtest: a bad request: the synchronous route's message and status, immediately; no poll
ok 49 - a bad request: the synchronous route's message and status, immediately; no poll
  ---
  duration_ms: 3.872792
  type: 'test'
  ...
# Subtest: a START that cannot reach the server is a transport failure (the caller may fall back to the local engine)
ok 50 - a START that cannot reach the server is a transport failure (the caller may fall back to the local engine)
  ---
  duration_ms: 3.239462
  type: 'test'
  ...
# Subtest: an error record is a failed fit with the synchronous message and status
ok 51 - an error record is a failed fit with the synchronous message and status
  ---
  duration_ms: 3.31679
  type: 'test'
  ...
# Subtest: a done record carrying NaN is F2's failed fit (unreadable reply), not a transport failure
ok 52 - a done record carrying NaN is F2's failed fit (unreadable reply), not a transport failure
  ---
  duration_ms: 2.932014
  type: 'test'
  ...
# Subtest: one lost poll is retried; five in a row are a transport failure and cancel the job
ok 53 - one lost poll is retried; five in a row are a transport failure and cancel the job
  ---
  duration_ms: 6.119202
  type: 'test'
  ...
# Subtest: a stopped heartbeat (restarted worker) is a failed fit, never an endless spinner
ok 54 - a stopped heartbeat (restarted worker) is a failed fit, never an endless spinner
  ---
  duration_ms: 3.240632
  type: 'test'
  ...
# Subtest: a job cancelled on the server (abandoned) is reported, not waited for
ok 55 - a job cancelled on the server (abandoned) is reported, not waited for
  ---
  duration_ms: 4.082585
  type: 'test'
  ...
# Subtest: ownership inside the loop: a switched tab or an edited model cancels the job and returns the reason
ok 56 - ownership inside the loop: a switched tab or an edited model cancels the job and returns the reason
  ---
  duration_ms: 7.18849
  type: 'test'
  ...
# Subtest: the Auto-Fit abort (2 minutes) cancels the job and surfaces as an AbortError
ok 57 - the Auto-Fit abort (2 minutes) cancels the job and surfaces as an AbortError
  ---
  duration_ms: 3.219414
  type: 'test'
  ...
# Subtest: Run Fit and Auto-Fit both go through _serverFitJob; nothing on the page posts to the synchronous /api/fit any more
ok 58 - Run Fit and Auto-Fit both go through _serverFitJob; nothing on the page posts to the synchronous /api/fit any more
  ---
  duration_ms: 2.309652
  type: 'test'
  ...
# Subtest: every module-level mutable is allowlisted with a valid non-C class
ok 59 - every module-level mutable is allowlisted with a valid non-C class
  ---
  duration_ms: 204.411479
  type: 'test'
  ...
# Subtest: inherited property names and anonymous-class names cannot slip through the allowlist
ok 60 - inherited property names and anonymous-class names cannot slip through the allowlist
  ---
  duration_ms: 84.999639
  type: 'test'
  ...
# Subtest: the known class-C holders are gone from module scope
ok 61 - the known class-C holders are gone from module scope
  ---
  duration_ms: 6.391674
  type: 'test'
  ...
# Subtest: async operations capture their owning record before the first await
ok 62 - async operations capture their owning record before the first await
  ---
  duration_ms: 2.408314
  type: 'test'
  ...
# Subtest: undo/redo and Find Peaks apply read the ACTIVE tab record only
ok 63 - undo/redo and Find Peaks apply read the ACTIVE tab record only
  ---
  duration_ms: 0.664396
  type: 'test'
  ...
# Subtest: one accessor classifies a result against a key: none / unverified / current / stale
ok 64 - one accessor classifies a result against a key: none / unverified / current / stale
  ---
  duration_ms: 13.463193
  type: 'test'
  ...
# Subtest: the key is the step (b) key: F1 adds no second binding mechanism and no new key field
ok 65 - the key is the step (b) key: F1 adds no second binding mechanism and no new key field
  ---
  duration_ms: 4.073769
  type: 'test'
  ...
# Subtest: Results panel, current: statistic, RMSE, R and sigma are shown
ok 66 - Results panel, current: statistic, RMSE, R and sigma are shown
  ---
  duration_ms: 9.167632
  type: 'test'
  ...
# Subtest: Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
ok 67 - Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
  ---
  duration_ms: 9.052144
  type: 'test'
  ...
# Subtest: Results panel, unverified (older save, no key): values shown with a plain note
ok 68 - Results panel, unverified (older save, no key): values shown with a plain note
  ---
  duration_ms: 9.453603
  type: 'test'
  ...
# Subtest: status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
ok 69 - status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
  ---
  duration_ms: 9.634025
  type: 'test'
  ...
# Subtest: the stored fitted curve is never drawn, saved or stacked as the fit once stale
ok 70 - the stored fitted curve is never drawn, saved or stacked as the fit once stale
  ---
  duration_ms: 3.49267
  type: 'test'
  ...
# Subtest: saves keep the key and say plainly when the statistics are stale or unverified
ok 71 - saves keep the key and say plainly when the statistics are stale or unverified
  ---
  duration_ms: 4.456088
  type: 'test'
  ...
# Subtest: CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
ok 72 - CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
  ---
  duration_ms: 21.428765
  type: 'test'
  ...
# Subtest: XLSX: stale writes a WARNING row instead of the statistic, and no sigma
ok 73 - XLSX: stale writes a WARNING row instead of the statistic, and no sigma
  ---
  duration_ms: 4.972914
  type: 'test'
  ...
# Subtest: TSV: stale says the Model / Residual columns are the current, unfitted model
ok 74 - TSV: stale says the Model / Residual columns are the current, unfitted model
  ---
  duration_ms: 8.503622
  type: 'test'
  ...
# Subtest: the refresh re-renders Results only when its rendered state differs
ok 75 - the refresh re-renders Results only when its rendered state differs
  ---
  duration_ms: 3.702415
  type: 'test'
  ...
# Subtest: an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
ok 76 - an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
  ---
  duration_ms: 3.456966
  type: 'test'
  ...
# Subtest: Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
ok 77 - Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
  ---
  duration_ms: 4.142432
  type: 'test'
  ...
# Subtest: Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
ok 78 - Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
  ---
  duration_ms: 12.295236
  type: 'test'
  ...
# Subtest: closing the last tab clears the Results panel, header and status statistics too
ok 79 - closing the last tab clears the Results panel, header and status statistics too
  ---
  duration_ms: 0.217754
  type: 'test'
  ...
# Subtest: reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
ok 80 - reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
  ---
  duration_ms: 1.567588
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back
ok 81 - F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back
  ---
  duration_ms: 5.673825
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a Cloudflare 524 (plain-text body) is a failed request with its status, never "could not be read"
ok 82 - F2: Auto-Fit on a Cloudflare 524 (plain-text body) is a failed request with its status, never "could not be read"
  ---
  duration_ms: 6.409878
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a 500 with a JSON error is a failed request with its status, never "could not be read"
ok 83 - F2: Auto-Fit on a 500 with a JSON error is a failed request with its status, never "could not be read"
  ---
  duration_ms: 4.437273
  type: 'test'
  ...
1..83
# tests 83
# suites 0
# pass 83
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 427.783627

 exited 1 in 1250ms:
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
FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll']

exec
/bin/zsh -lc "rg -n 'iter_cb|_abort|AbortFitException|calc_covar|basinhopping|least_squares' /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py; cat /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/gunicorn/workers/sync.py; rg -n 'fit-spinner-overlay|btn-green' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
27:from scipy.optimize import basinhopping as scipy_basinhopping
31:from scipy.optimize import least_squares
94:class AbortFitException(MinimizerException):
349:                 iter_cb=None, scale_covar=True, nan_policy='raise',
350:                 reduce_fcn=None, calc_covar=True, max_nfev=None, **kws):
367:        iter_cb : callable, optional
371:                iter_cb(params, iter, resid, *fcn_args, **fcn_kws)
407:        calc_covar : bool, optional
409:            for solvers other than ``'leastsq'`` and ``'least_squares'``.
421:        :meth:`least_squares`, this returned value must be an array, with
452:        self.iter_cb = iter_cb
453:        self.calc_covar = calc_covar
460:        self._abort = False
538:            raise AbortFitException(f"fit aborted: too many function evaluations {self.max_nfev}")
542:        if callable(self.iter_cb):
543:            abort = self.iter_cb(params, self.result.nfev, out,
545:            self._abort = self._abort or abort
547:        if self._abort:
552:            raise AbortFitException("fit aborted by user.")
662:        self._abort = False
989:            except AbortFitException:
996:            except AbortFitException:
1014:            self._abort = False
1022:        if (not result.aborted and self.calc_covar and HAS_NUMDIFFTOOLS and
1089:        if callable(self.iter_cb):
1090:            abort = self.iter_cb(params, self.result.nfev, out,
1092:            self._abort = self._abort or abort
1093:        if self._abort:
1096:            raise AbortFitException("fit aborted by user.")
1425:        except AbortFitException:
1500:    def least_squares(self, params=None, max_nfev=None, **kws):
1501:        """Least-squares minimization using :scipydoc:`optimize.least_squares`.
1503:        This method wraps :scipydoc:`optimize.least_squares`, which has
1517:            Minimizer options to pass to :scipydoc:`optimize.least_squares`.
1531:        result.method = 'least_squares'
1543:        least_squares_kws = dict(jac='2-point', method='trf', ftol=1e-08,
1550:        least_squares_kws.update(self.kws)
1551:        least_squares_kws.update(kws)
1553:        if least_squares_kws.get('Dfun', None) is not None:
1554:            least_squares_kws['jac'] = least_squares_kws.pop('Dfun')
1556:        if callable(least_squares_kws['jac']):
1557:            self.jacfcn = least_squares_kws['jac']
1558:            least_squares_kws['jac'] = self._jacobian
1560:        least_squares_kws['kwargs'].update({'apply_bounds_transformation': False})
1561:        result.call_kws = least_squares_kws
1564:            ret = least_squares(self.__residual, start_vals,
1566:                                **least_squares_kws)
1568:        except AbortFitException:
1572:        # Note: scipy.optimize.least_squares is actually returning the
1588:                    outattr = 'least_squares_nfev'
1675:        except AbortFitException:
1693:        except AbortFitException:
1726:    def basinhopping(self, params=None, max_nfev=None, **kws):
1727:        """Use the `basinhopping` algorithm to find the global minimum.
1729:        This method calls :scipydoc:`optimize.basinhopping` using the
1743:            Minimizer options to pass to :scipydoc:`optimize.basinhopping`.
1749:            basinhopping algorithm.
1756:        result.method = 'basinhopping'
1758:        basinhopping_kws = dict(niter=100, T=1.0, stepsize=0.5,
1764:        basinhopping_kws.update(self.kws)
1765:        basinhopping_kws.update(kws)
1768:        result.call_kws = basinhopping_kws
1770:            ret = scipy_basinhopping(self.penalty, x0, **basinhopping_kws)
1771:        except AbortFitException:
1786:        if (not result.aborted and self.calc_covar and HAS_NUMDIFFTOOLS and
1923:        except AbortFitException:
2072:        except AbortFitException:
2095:        if (not result.aborted and self.calc_covar and HAS_NUMDIFFTOOLS and
2153:        except AbortFitException:
2172:        if (not result.aborted and self.calc_covar and HAS_NUMDIFFTOOLS and
2232:        except AbortFitException:
2252:        if (not result.aborted and self.calc_covar and HAS_NUMDIFFTOOLS and
2269:            - `'least_squares'`: Least-Squares minimization, using Trust
2273:            - `'basinhopping'`: basinhopping
2336:            function = self.least_squares
2339:        elif user_method == 'basinhopping':
2340:            function = self.basinhopping
2473:def minimize(fcn, params, method='leastsq', args=None, kws=None, iter_cb=None,
2475:             calc_covar=True, max_nfev=None, **fit_kws):
2487:        '`least_squares`', the objective function should return an array
2501:        - `'least_squares'`: Least-Squares minimization, using Trust Region Reflective method
2504:        - `'basinhopping'`: basinhopping
2537:    iter_cb : callable, optional
2541:            iter_cb(params, iter, resid, *args, **kws),
2560:    calc_covar : bool, optional
2562:        solvers other than `'leastsq'` and `'least_squares'`. Requires the
2606:                           iter_cb=iter_cb, scale_covar=scale_covar,
2608:                           calc_covar=calc_covar, **fit_kws)
2613:                       iter_cb=iter_cb, scale_covar=scale_covar,
2615:                       calc_covar=calc_covar, max_nfev=max_nfev, **fit_kws)
#
# This file is part of gunicorn released under the MIT license.
# See the NOTICE for more information.
#

from datetime import datetime
import errno
import os
import select
import ssl
import sys

from gunicorn import http
from gunicorn.http import wsgi
from gunicorn import sock
from gunicorn import util
from gunicorn.workers import base


class StopWaiting(Exception):
    """ exception raised to stop waiting for a connection """


class SyncWorker(base.Worker):

    def accept(self, listener):
        client, addr = listener.accept()
        client.setblocking(1)
        util.close_on_exec(client)
        self.handle(listener, client, addr)

    def wait(self, timeout):
        try:
            self.notify()
            ret = select.select(self.wait_fds, [], [], timeout)
            if ret[0]:
                if self.PIPE[0] in ret[0]:
                    os.read(self.PIPE[0], 1)
                return ret[0]

        except OSError as e:
            if e.args[0] == errno.EINTR:
                return self.sockets
            if e.args[0] == errno.EBADF:
                if self.nr < 0:
                    return self.sockets
                else:
                    raise StopWaiting
            raise

    def is_parent_alive(self):
        # If our parent changed then we shut down.
        if self.ppid != os.getppid():
            self.log.info("Parent changed, shutting down: %s", self)
            return False
        return True

    def run_for_one(self, timeout):
        listener = self.sockets[0]
        while self.alive:
            self.notify()

            # Accept a connection. If we get an error telling us
            # that no connection is waiting we fall down to the
            # select which is where we'll wait for a bit for new
            # workers to come give us some love.
            try:
                self.accept(listener)
                # Keep processing clients until no one is waiting. This
                # prevents the need to select() for every client that we
                # process.
                continue

            except OSError as e:
                if e.errno not in (errno.EAGAIN, errno.ECONNABORTED,
                                   errno.EWOULDBLOCK):
                    raise

            if not self.is_parent_alive():
                return

            try:
                self.wait(timeout)
            except StopWaiting:
                return

    def run_for_multiple(self, timeout):
        while self.alive:
            self.notify()

            try:
                ready = self.wait(timeout)
            except StopWaiting:
                return

            if ready is not None:
                for listener in ready:
                    if listener == self.PIPE[0]:
                        continue

                    try:
                        self.accept(listener)
                    except OSError as e:
                        if e.errno not in (errno.EAGAIN, errno.ECONNABORTED,
                                           errno.EWOULDBLOCK):
                            raise

            if not self.is_parent_alive():
                return

    def run(self):
        # if no timeout is given the worker will never wait and will
        # use the CPU for nothing. This minimal timeout prevent it.
        timeout = self.timeout or 0.5

        # Warn if HTTP/2 is requested - sync worker doesn't support it
        if 'h2' in self.cfg.http_protocols:
            self.log.warning(
                "HTTP/2 is not supported by the sync worker. "
                "Use gthread, gevent, or asgi workers for HTTP/2 support. "
                "Falling back to HTTP/1.1 only."
            )

        # self.socket appears to lose its blocking status after
        # we fork in the arbiter. Reset it here.
        for s in self.sockets:
            s.setblocking(0)

        if len(self.sockets) > 1:
            self.run_for_multiple(timeout)
        else:
            self.run_for_one(timeout)

    def handle(self, listener, client, addr):
        req = None
        try:
            if self.cfg.is_ssl:
                client = sock.ssl_wrap_socket(client, self.cfg)
            parser = http.get_parser(self.cfg, client, addr)
            req = next(parser)
            self.handle_request(listener, req, client, addr)
        except http.errors.NoMoreData as e:
            self.log.debug("Ignored premature client disconnection. %s", e)
        except StopIteration as e:
            self.log.debug("Closing connection. %s", e)
        except ssl.SSLError as e:
            if e.args[0] == ssl.SSL_ERROR_EOF:
                self.log.debug("ssl connection closed")
                client.close()
            else:
                self.log.debug("Error processing SSL request.")
                self.handle_error(req, client, addr, e)
        except OSError as e:
            if e.errno not in (errno.EPIPE, errno.ECONNRESET, errno.ENOTCONN):
                self.log.exception("Socket error processing request.")
            else:
                if e.errno == errno.ECONNRESET:
                    self.log.debug("Ignoring connection reset")
                elif e.errno == errno.ENOTCONN:
                    self.log.debug("Ignoring socket not connected")
                else:
                    self.log.debug("Ignoring EPIPE")
        except BaseException as e:
            self.handle_error(req, client, addr, e)
        finally:
            util.close_graceful(client)

    def handle_request(self, listener, req, client, addr):
        environ = {}
        resp = None
        try:
            self.cfg.pre_request(self, req)
            request_start = datetime.now()
            resp, environ = wsgi.create(req, client, addr,
                                        listener.getsockname(), self.cfg)
            # Force the connection closed until someone shows
            # a buffering proxy that supports Keep-Alive to
            # the backend.
            resp.force_close()
            self.nr += 1
            if self.nr >= self.max_requests:
                self.log.info("Autorestarting worker after current request.")
                self.alive = False
            respiter = self.wsgi(environ, resp.start_response)
            try:
                if isinstance(respiter, environ['wsgi.file_wrapper']):
                    resp.write_file(respiter)
                else:
                    for item in respiter:
                        resp.write(item)
                resp.close()
            finally:
                request_time = datetime.now() - request_start
                self.log.access(resp, req, environ, request_time)
                if hasattr(respiter, "close"):
                    respiter.close()
        except OSError:
            # pass to next try-except level
            util.reraise(*sys.exc_info())
        except Exception:
            if resp and resp.headers_sent:
                # If the requests have already been sent, we should close the
                # connection to indicate the error.
                self.log.exception("Error handling request")
                util.close_graceful(client)
                raise StopIteration()
            raise
        finally:
            try:
                self.cfg.post_request(self, req, environ, resp)
            except Exception:
                self.log.exception("Exception in post_request hook")
483:  .btn-green {
490:  .btn-green:hover {
494:  .btn-green:hover::after {
1249:  .fit-spinner-overlay {
1272:     modal-covering overlay like .fit-spinner-overlay: the results area
1490:  body.light-theme .btn-green:hover {
1904:      <button class="btn btn-green peak-fit-control" id="btn-run-fit" onclick="runFit()">Run Fit</button>
2159:        <div id="fit-spinner-overlay" class="fit-spinner-overlay" style="display:none">
6689:  const overlay = document.getElementById('fit-spinner-overlay');
6693:  document.querySelector('.btn-green').disabled = true;
6702:  const overlay = document.getElementById('fit-spinner-overlay');
6704:  document.querySelector('.btn-green').disabled = false;
7630:  const runBtn = document.querySelector('.btn-green');

exec
/bin/zsh -lc "/Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile
tempfile.tempdir = '\\''/tmp'\\''
import fitting,numpy as np,time
x=np.linspace(281,291,100); y=300+3000*np.exp(-4*np.log(2)*((x-285)/1.0)**2)
p=[dict(id='\\''1'\\'',shape='\\''pseudo_voigt_gl'\\'',center=284.8,amplitude=2600,fwhm=1.2,gl_ratio=.3)]
for method in ['\\''leastsq'\\'','\\''least_squares'\\'','\\''nelder'\\'','\\''basinhopping'\\'','\\''differential_evolution'\\'']:
    t=time.monotonic()
    try:
        r=fitting.run_fit(x,y,p,fit_kws={'\\''method'\\'':method},n_perturb=0,cancel=lambda:True)
        print(method,'\\''RETURN'\\'',r['\\''success'\\''],flush=True)
    except Exception as e:
        print(method,type(e).__name__,str(e),round(time.monotonic()-t,3),flush=True)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 1507ms:
/Users/skyefortier/.matplotlib is not a writable directory
leastsq AttributeError 'ModelResult' object has no attribute 'aic' 0.004
least_squares FitCancelled the fit was cancelled 0.003
nelder RuntimeError lmfit fitting failed: fit aborted by user. 0.003
basinhopping FitCancelled the fit was cancelled 0.008
differential_evolution RuntimeError lmfit fitting failed: fit aborted by user. 0.004

exec
/bin/zsh -lc "sed -n '1558,1600p' /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py; sed -n '1620,1715p' /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py; sed -n '1765,1798p' /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py; sed -n '990,1030p' /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py; sed -n '1245,1265p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
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


        .. versionchanged:: 0.9.0
           Return value changed to :class:`MinimizerResult`.

        """
        result = self.prepare_fit(params=params)
        result.method = 'leastsq'
        result.nfev -= 2  # correct for "pre-fit" initialization/checks
        variables = result._init_vals_internal

        # Note: we set max number of function evaluations here, and send twice
        # that value to the solver so it essentially never stops on its own
        self.set_max_nfev(max_nfev, 2000*(result.nvarys+1))

        lskws = dict(Dfun=None, full_output=1, col_deriv=0, ftol=1.5e-8,
                     xtol=1.5e-8, gtol=0.0, maxfev=2*self.max_nfev,
                     epsfcn=1.e-10, factor=100, diag=None)

        if 'maxfev' in kws:
            warnings.warn(maxeval_warning.format('maxfev', thisfuncname()),
                          RuntimeWarning)
            kws.pop('maxfev')

        lskws.update(self.kws)
        lskws.update(kws)
        self.col_deriv = False

        if lskws['Dfun'] is not None:
            self.jacfcn = lskws['Dfun']
            self.col_deriv = lskws['col_deriv']
            lskws['Dfun'] = self._jacobian

        # suppress runtime warnings during fit and error analysis
        orig_warn_settings = np.geterr()
        np.seterr(all='ignore')
        result.call_kws = lskws
        try:
            lsout = scipy_leastsq(self.__residual, variables, **lskws)
        except AbortFitException:
            pass

        if not result.aborted:
            _best, _cov, _infodict, errmsg, ier = lsout
        else:
            _best = result.last_internal_values
            _cov = None
            ier = -1
            errmsg = 'Fit aborted.'

        result.nfev -= 1
        if result.nfev >= self.max_nfev:
            result.nfev = self.max_nfev - 1
        self.result.nfev = result.nfev
        try:
            result.residual = self.__residual(_best)
            result._calculate_statistics()
        except AbortFitException:
            pass

        result.ier = ier
        result.lmdif_message = errmsg
        result.success = ier in [1, 2, 3, 4]
        if ier in {1, 2, 3}:
            result.message = 'Fit succeeded.'
        elif ier == 0:
            result.message = ('Invalid Input Parameters. I.e. more variables '
                              'than data points given, tolerance < 0.0, or '
                              'no data provided.')
        elif ier == 4:
            result.message = 'One or more variable did not affect the fit.'
        elif ier == 5:
            result.message = self._err_max_evals.format(lskws['maxfev'])
        else:
            result.message = 'Tolerance seems to be too small.'

        # self.errorbars = error bars were successfully estimated
        result.errorbars = (_cov is not None)
        if result.errorbars:
            # transform the covariance matrix to "external" parameter space
        basinhopping_kws.update(kws)

        x0 = result._init_vals_internal
        result.call_kws = basinhopping_kws
        try:
            ret = scipy_basinhopping(self.penalty, x0, **basinhopping_kws)
        except AbortFitException:
            pass

        if not result.aborted:
            result.message = ret.message
            result.residual = self.__residual(ret.x)
            result.nfev -= 1
        elif result.nfev > self.max_nfev-5:
            result.nfev -= 2
            _best = result.last_internal_values
            result.residual = self.__residual(_best, False)

        result._calculate_statistics()

        # calculate the cov_x and estimate uncertainties/correlations
        if (not result.aborted and self.calc_covar and HAS_NUMDIFFTOOLS and
                len(result.residual) > len(result.var_names)):
            _covar_ndt = self._calculate_covariance_matrix(ret.x)
            if _covar_ndt is not None:
                result.covar = self._int2ext_cov_x(_covar_ndt, ret.x)
                self._calculate_uncertainties_correlations()

        return result

    def brute(self, params=None, Ns=20, keep=50, workers=1, max_nfev=None):
        """Use the `brute` method to find the global minimum of a function.

        The following parameters are passed to :scipydoc:`optimize.brute`
                pass

        else:
            result.call_kws = fmin_kws
            try:
                ret = scipy_minimize(self.penalty, variables, **fmin_kws)
            except AbortFitException:
                pass

        if not result.aborted:
            if isinstance(ret, dict):
                for attr, value in ret.items():
                    setattr(result, attr, value)
            else:
                for attr in dir(ret):
                    if not attr.startswith('_'):
                        setattr(result, attr, getattr(ret, attr))

            result.x = np.atleast_1d(result.x)
            result.residual = self.__residual(result.x)
            result.nfev -= 1
        else:
            result.x = result.last_internal_values
            self.result.nfev -= 2
            self._abort = False
            result.residual = self.__residual(result.x)
            result.nfev += 1

        result._calculate_statistics()

        # calculate the cov_x and estimate uncertainties/correlations
        self.result.uvars = None
        if (not result.aborted and self.calc_covar and HAS_NUMDIFFTOOLS and
                len(result.residual) > len(result.var_names)):
            _covar_ndt = self._calculate_covariance_matrix(result.x)
            if _covar_ndt is not None:
                result.covar = self._int2ext_cov_x(_covar_ndt, result.x)
                self._calculate_uncertainties_correlations()

        return result

  }
  #folder-progress.active { display: block; }

  /* ── Fit spinner overlay ────────────────────────────────── */
  .fit-spinner-overlay {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.5);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 100;
    border-radius: var(--radius);
  }
  .fit-spinner {
    width: 48px;
    height: 48px;
    border: 4px solid var(--border2);
    border-top-color: var(--accent);
    border-radius: 50%;

codex
All 83 targeted JavaScript tests pass. I found two gaps worth reproducing: Ctrl/Cmd+F can launch another fit despite the disabled button, and cancellation can escape as a solver error because the wrapper checks the cancellation flag only after a successful return. I’m checking their impact before ranking them.
exec
/bin/zsh -lc "sed -n '1,112p' tests/js/fit_acceptance.test.js; sed -n '110,185p' app.py; rg -n '"'^def create_app|mkdir|logging|FileHandler|sweep'"' app.py | head -45; nl -ba fitting.py | tail -36; nl -ba app.py | sed -n '633,679p'; nl -ba templates/index.html | sed -n '7482,7557p'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
// Fit acceptance rule for the backend path (unit A0, 2026-09-15): nothing is
// shown, stored or exported as a fit result unless it converged, and a
// server-side error surfaces its message instead of silently handing the
// model to the local optimiser.
//
// Before this unit runFit checked `json.error` only: an lmfit result with
// success:false was applied and announced as "Fit complete (lmfit)" (audit
// A08), and ANY thrown error — a 400 validation error included — fell back
// to runFitLocal, which then returned the starting model (A01).
//
// runFit is extracted verbatim from templates/index.html; its collaborators
// are stubbed at the boundary (DOM, fetch, upload, chart/list renderers).

const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const REPO_ROOT = path.join(__dirname, '../..');
const html = fs.readFileSync(path.join(REPO_ROOT, 'templates/index.html'), 'utf8');
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

// Unit 2: Run Fit starts the fit and polls for it (_serverFitJob). These
// tests script the single /api/fit reply they always did; jobAdapter serves
// that reply as a finished job (start -> 202 + id; progress -> done + result),
// and a start that throws is still a transport failure.
const POLL_SRC = [constLineOf('FIT_POLL_MS'), constLineOf('FIT_POLL_TRANSPORT_RETRIES'), constLineOf('FIT_HEARTBEAT_LOST_SEC'),
  'const _runningFitJobs = new Set();', ...['_cancelFitJob', '_fitHttpError', '_serverFitJob'].map(n => extractFn(n))].join('\n');
function constLineOf(n) { const l = lines.find(x => x.startsWith('const ' + n)); assert.ok(l, n); return l; }
function jobAdapter(fetchImpl) {
  let reply = null;
  return async (url, init) => {
    if (url === '/api/fit/start') {
      const r = await fetchImpl('/api/fit', init);
      if (r && r.ok === false) return r;
      reply = r;
      return { ok: true, status: 202, text: async () => JSON.stringify({ job_id: 'job-1' }) };
    }
    if (url.startsWith('/api/fit/progress/')) {
      const r = reply;
      return { ok: true, status: 200, text: async () => '{"status": "done", "result": ' + (await r.text()) + '}' };
    }
    if (url.startsWith('/api/fit/cancel/')) return { ok: true, status: 200, json: async () => ({}) };
    return fetchImpl(url, init);
  };
}
const immediate = f => { f(); return 0; };

function makeEnv({ fetchImpl, uploadImpl, specImpl, ownerActive }) {
  const dom = {};
  const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, disabled: false,
    setAttribute() {}, removeAttribute() {}, classList: { add(c) { this._c = c; }, remove() { this._c = null; }, contains() { return false; }, _c: null } });
  const document = { getElementById: el, querySelector: () => el('.btn-green'), querySelectorAll: () => [] };
  const be = Array.from({ length: 50 }, (_, i) => 280 + 0.2 * i);
  const state = { rawBE: be.slice(), rawIntensity: be.map(() => 100), ccShift: 0, fitResult: { marker: 'previous' },
    peaks: [{ id: 1, name: 'p', shape: 'Gaussian', center: 285, fwhm: 1.2, amplitude: 50, glMix: 50, asymmetry: 0 }] };
  const owner = { id: 7 };
  const calls = { notify: [], local: 0, applied: 0 };
  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n') + '\n' + POLL_SRC;
  const factory = new Function('setTimeout', 'document', 'state', 'fetch', 'uploadToBackend', 'notify', 'pushUndo', '_showFitSpinner', '_hideFitSpinner',
    '_opOwner', '_ownerActive', 'getROIData', 'computeBackground', 'peakToBackendSpec', '_getManualAnchors', 'applyBackendResult',
    '_computeRFactor', '_CHISQ_TOOLTIP', '_updateRFactorUI', '_updateROIDisplay', 'renderPeakList', 'updatePlot', 'renderResults',
    '_autoSnapshot', 'runFitLocal', '_snapshotSuppressed', 'console', '_applyStatDisplay', '_activeTab',
    src + '\nreturn { runFit };');
  const noop = () => {};
  const { runFit } = factory(immediate, document, state, jobAdapter(withText(fetchImpl)), uploadImpl || (async () => 'sid'), (msg, kind) => calls.notify.push({ msg, kind }),
    noop, noop, noop, () => owner, ownerActive || (o => o === owner), () => ({ be: state.rawBE.slice(), inten: state.rawIntensity.slice() }),
    b => b.map(() => 0), specImpl || (p => ({ id: p.id, shape: 'gaussian' })), () => [], () => { calls.applied++; },
    () => 0.1, '', noop, noop, noop, noop, noop, noop,
    () => { calls.local++; return { success: true, engine: 'local' }; }, false, { warn: noop, error: noop, log: noop }, noop, () => owner);
  return { runFit, state, dom, calls };
}

const okResponse = body => async () => ({ ok: true, status: 200, json: async () => body });
// F2: the page reads a 2xx /api/fit body as text and parses it itself
// (_readFitReply). A mock that only defines json() gets the matching text().
function withText(fetchImpl) {
  return async (...a) => {
    const r = await fetchImpl(...a);
    if (r && typeof r.text !== 'function' && typeof r.json === 'function') r.text = async () => JSON.stringify(await r.json());
    return r;
  };
}

test('A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown', async () => {
  const env = makeEnv({ fetchImpl: okResponse({ success: false, message: 'Fit did not converge: max evaluations', statistics: { reduced_chi_square: 999 }, individual_peaks: [] }) });
  const before = JSON.stringify(env.state.peaks);
  await env.runFit();
  assert.equal(env.calls.applied, 0, 'applyBackendResult must not run');
  assert.equal(env.calls.local, 0, 'no silent local fallback');
  assert.equal(JSON.stringify(env.state.peaks), before, 'peaks unchanged');
  assert.equal(env.state.fitResult.marker, 'previous', 'previous fit result retained');
  assert.ok(env.calls.notify.some(n => n.kind === 'red' && /did not converge/i.test(n.msg)), JSON.stringify(env.calls.notify));
  assert.ok(!/complete/i.test(env.dom['sb-msg'].textContent), env.dom['sb-msg'].textContent);
});

test('a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser', async () => {
  const env = makeEnv({ fetchImpl: async () => ({ ok: false, status: 400, json: async () => ({ error: 'peak 1: fwhm_min must be positive' }) }) });
  const before = JSON.stringify(env.state.peaks);
  await env.runFit();
  assert.equal(env.calls.local, 0, 'a 400 is not a reason to run the local fitter');
    # non-integer values with a clean 400 instead of a 500 or a worker hang.
    try:
        n_perturb = int(body.get("n_perturb", 5))
    except (TypeError, ValueError):
        return None, _err(f"n_perturb must be an integer between 0 and {MAX_N_PERTURB}")
    if n_perturb < 0 or n_perturb > MAX_N_PERTURB:
        return None, _err(f"n_perturb must be between 0 and {MAX_N_PERTURB}")

    # Scattered-starts check (optional; the page sends 3). Same clean-400
    # treatment as n_perturb; run_fit validates again for other callers.
    n_starts = body.get("n_starts", 0)
    if isinstance(n_starts, bool) or not isinstance(n_starts, int) or not 0 <= n_starts <= fitting.MAX_N_STARTS:
        return None, _err(f"n_starts must be an integer between 0 and {fitting.MAX_N_STARTS}")
    # "Is this component required?" (one extra fit; Auto-Fit asks for its anchor)
    require_component = body.get("require_component")
    if require_component is not None and not isinstance(require_component, (str, int)):
        return None, _err("require_component must be a peak id")
    return dict(
        energy=energy,
        counts=counts,
        peak_specs=peak_specs,
        background_method=bg_method,
        bg_start_idx=bg_start,
        bg_end_idx=bg_end,
        charge_shift_ev=0.0,
        fit_kws={"method": fit_method},
        manual_bg=manual_bg,
        n_perturb=n_perturb,
        endpoint_avg=endpoint_avg,
        n_starts=n_starts,
        require_component=require_component,
    ), None


def _run_fit_outcome(app, fit_args, cancel=None):
    """Run the fit; return ``(status_code, body)`` exactly as /api/fit has
    always answered (a ValueError is our own validation, 400; a RuntimeError
    a solver-internal failure, 422 without library internals; anything else
    500). A cancelled job returns ``(None, None)``."""
    try:
        result = fitting.run_fit(**fit_args, cancel=cancel)
    except fitting.FitCancelled:
        return None, None
    except ValueError as exc:
        # Our own validation: unknown shape/method, self/circular constraint,
        # "Master peak not found", bad numeric field, etc. (audit F10/F11).
        return 400, {"error": str(exc)}
    except RuntimeError:
        # Solver-internal failure (e.g. lmfit non-convergence). Log the
        # detail; return a generic 422 that leaks no library internals.
        app.logger.exception("Fit failed")
        return 422, {"error": "Fit failed — see server log for details."}
    except Exception:
        app.logger.exception("Unexpected fitting error")
        return 500, {"error": "Internal fitting error — see server log."}
    return 200, result


# ─────────────────────────────────────────────────────────────────────────────
# Application factory
# ─────────────────────────────────────────────────────────────────────────────

def create_app(upload_folder: str = "uploads", data_folder: str = "data/xps") -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")

    app.config["UPLOAD_FOLDER"] = upload_folder
    app.config["XPS_DATA_DIR"] = data_folder
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB hard limit

    Path(upload_folder).mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

33:import logging
56:# Session .npz files are deleted by an opportunistic sweep this many days after
57:# their last modification (audit F13). The sweep runs on each new session write
172:def create_app(upload_folder: str = "uploads", data_folder: str = "data/xps") -> Flask:
179:    Path(upload_folder).mkdir(parents=True, exist_ok=True)
181:    logging.basicConfig(
182:        level=logging.INFO,
228:def _sweep_expired_sessions(upload_folder: str) -> None:
232:    would risk duplicate sweeps under multi-worker gunicorn. Touches ONLY
263:    _sweep_expired_sessions(upload_folder)
282:    "bayesian_exchange_mc": {"n_replicas": 8, "n_sweeps": 600,
430:        logging.getLogger(__name__).exception("analyze failed")
529:        logging.getLogger(__name__).exception(
533:def _sweep_expired_jobs(upload_folder: str) -> None:
535:    pattern as _sweep_expired_sessions (audit F13): runs on each new job
554:# Records are the Find Peaks job files (<job>.job.json, the same TTL sweep);
577:        logging.getLogger(__name__).exception("failed to write fit job %s", job_id)
597:def _sweep_fit_job_markers(upload_folder: str) -> None:
653:            logging.getLogger(__name__).exception("fit job %s crashed", job_id)
739:                logging.getLogger(__name__).error(
783:            logging.getLogger(__name__).error("XPS reference dataset invalid: %s", e)
1078:        result shape, plus live sweep progress (Find Peaks UI, 2026-07-11).
1133:        _sweep_expired_jobs(upload_folder)
1173:                logging.getLogger(__name__).exception(
1234:        _sweep_expired_jobs(upload_folder)
1235:        _sweep_fit_job_markers(upload_folder)
  2080	    elif method == "linear":
  2081	        bg = linear_background(x, y)
  2082	    elif method in ("none", "flat", "", "manual"):
  2083	        bg = np.zeros_like(y)
  2084	    else:
  2085	        raise ValueError(f"Unknown background method '{method}'")
  2086	
  2087	    return {
  2088	        "energy": x.tolist(),
  2089	        "background": bg.tolist(),
  2090	        "net_counts": (y - bg).tolist(),
  2091	    }
  2092	
  2093	
  2094	def run_fit(*args, cancel=None, **kwargs):
  2095	    """Fit peaks — see ``_run_fit_impl`` for every argument and the result.
  2096	
  2097	    ``cancel`` (optional, unit 2): a callable polled during the fit; once it
  2098	    returns true every remaining minimisation aborts and ``FitCancelled`` is
  2099	    raised instead of a result. Without it this is exactly the synchronous fit
  2100	    it always was (no ``iter_cb`` reaches any minimiser)."""
  2101	    if cancel is None:
  2102	        return _run_fit_impl(*args, **kwargs)
  2103	    _CANCEL.fn, _CANCEL.hit = cancel, False
  2104	    try:
  2105	        result = _run_fit_impl(*args, **kwargs)
  2106	    finally:
  2107	        hit = getattr(_CANCEL, "hit", False)
  2108	        _CANCEL.fn, _CANCEL.hit = None, False
  2109	    if hit:
  2110	        raise FitCancelled("the fit was cancelled")
  2111	    return result
  2112	
  2113	
  2114	run_fit.__wrapped__ = _run_fit_impl
  2115	
   633	        if cancel_path.exists():
   634	            return True
   635	        try:
   636	            return time.time() - polled_path.stat().st_mtime > FIT_JOB_ABANDON_SEC
   637	        except OSError:
   638	            return False
   639	
   640	    def heartbeat() -> None:
   641	        while not finished.wait(FIT_JOB_HEARTBEAT_SEC):
   642	            with lock:
   643	                if rec["status"] != "running":
   644	                    return
   645	                rec["heartbeat"] = time.time()
   646	                rec["elapsed_sec"] = round(time.time() - started, 1)
   647	                _fit_job_write(job_id, upload_folder, rec)
   648	
   649	    def worker() -> None:
   650	        try:
   651	            status, body = run(fit_args, cancelled)
   652	        except Exception as exc:                       # the record must always leave "running"
   653	            logging.getLogger(__name__).exception("fit job %s crashed", job_id)
   654	            status, body = 500, {"error": "Internal fitting error — see server log."}
   655	        with lock:
   656	            rec["elapsed_sec"] = round(time.time() - started, 1)
   657	            rec["heartbeat"] = time.time()
   658	            if status is None or cancel_path.exists():
   659	                rec.update(status="cancelled")
   660	            elif status == 200:
   661	                rec.update(status="done", result=body)
   662	            else:
   663	                rec.update(status="error", error=body.get("error"), http_status=status)
   664	            finished.set()
   665	            _fit_job_write(job_id, upload_folder, rec)
   666	        for kind in ("cancel", "polled"):
   667	            try:
   668	                _fit_job_marker(job_id, upload_folder, kind).unlink(missing_ok=True)
   669	            except OSError:
   670	                pass
   671	
   672	    threading.Thread(target=worker, daemon=True, name=f"fit-{job_id[:8]}").start()
   673	    threading.Thread(target=heartbeat, daemon=True, name=f"fit-hb-{job_id[:8]}").start()
   674	
   675	
   676	def _require_json(f):
   677	    """Decorator: return 400 if request body is not valid JSON."""
   678	    @wraps(f)
   679	    def wrapper(*args, **kwargs):
  7482	  err.serverError = true;
  7483	  err.httpStatus = status;
  7484	  return err;
  7485	}
  7486	async function _serverFitJob(fitReq, guard) {
  7487	  guard = guard || {};
  7488	  const isTransport = e => e && !e.serverError && (e instanceof TypeError || e.name === 'AbortError');
  7489	  let resp;
  7490	  try {
  7491	    resp = await fetch('/api/fit/start', { method: 'POST', headers: { 'Content-Type': 'application/json' },
  7492	                                           body: JSON.stringify(fitReq), signal: guard.signal });
  7493	  } catch (e) { if (isTransport(e)) e.transportFailure = true; throw e; }
  7494	  if (resp.ok === false) {
  7495	    let msg = null;
  7496	    try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
  7497	    throw _fitHttpError(resp.status, msg);
  7498	  }
  7499	  let started;
  7500	  try { started = await _readFitReply(resp); } catch (e) { if (isTransport(e)) e.transportFailure = true; throw e; }
  7501	  const jobId = started && started.job_id;
  7502	  if (!jobId) throw _fitHttpError(resp.status, 'The server did not start the fit (no job id).');
  7503	  _runningFitJobs.add(jobId);
  7504	  let misses = 0;
  7505	  try {
  7506	    while (true) {
  7507	      await new Promise(r => setTimeout(r, FIT_POLL_MS));
  7508	      if (guard.signal && guard.signal.aborted) {
  7509	        _cancelFitJob(jobId);
  7510	        throw guard.signal.reason || new DOMException('aborted', 'AbortError');
  7511	      }
  7512	      const why = guard.abandoned ? guard.abandoned() : null;
  7513	      if (why) { _cancelFitJob(jobId); return { _abandoned: why }; }
  7514	      let pr, rec;
  7515	      try {
  7516	        pr = await fetch('/api/fit/progress/' + encodeURIComponent(jobId), { signal: guard.signal });
  7517	      } catch (e) {
  7518	        if (e && e.name === 'AbortError') { _cancelFitJob(jobId); throw e; }
  7519	        if (++misses >= FIT_POLL_TRANSPORT_RETRIES) {
  7520	          _cancelFitJob(jobId);
  7521	          const err = new Error('Lost contact with the server during the fit (' + ((e && e.message) || 'network error') + ').');
  7522	          err.transportFailure = true;
  7523	          throw err;
  7524	        }
  7525	        continue;
  7526	      }
  7527	      if (pr.ok === false) {
  7528	        _cancelFitJob(jobId);
  7529	        let msg = null;
  7530	        try { const j = await pr.json(); msg = (j && j.error) || null; } catch (_) { /* non-JSON body */ }
  7531	        throw _fitHttpError(pr.status, msg, 'Lost the fit\'s progress');
  7532	      }
  7533	      try { rec = await _readFitReply(pr); } catch (e) {
  7534	        if (e && e.unreadableReply) { _cancelFitJob(jobId); throw e; }
  7535	        if (++misses >= FIT_POLL_TRANSPORT_RETRIES) {
  7536	          _cancelFitJob(jobId);
  7537	          if (isTransport(e)) e.transportFailure = true;
  7538	          throw e;
  7539	        }
  7540	        continue;
  7541	      }
  7542	      misses = 0;
  7543	      if (rec.status === 'done') return rec.result;
  7544	      if (rec.status === 'error') throw _fitHttpError(rec.http_status || 500, rec.error);
  7545	      if (rec.status === 'cancelled') throw _fitHttpError(409, 'The fit was stopped on the server before it finished. Run it again.');
  7546	      if (Number.isFinite(rec.heartbeat_age_sec) && rec.heartbeat_age_sec > FIT_HEARTBEAT_LOST_SEC) {
  7547	        _cancelFitJob(jobId);
  7548	        throw _fitHttpError(503, 'The server stopped working on the fit (no sign of it for ' + Math.round(rec.heartbeat_age_sec) +
  7549	                                 ' s — it was probably restarted). Run the fit again.');
  7550	      }
  7551	      if (typeof guard.onProgress === 'function') guard.onProgress(rec);
  7552	    }
  7553	  } finally {
  7554	    _runningFitJobs.delete(jobId);
  7555	  }
  7556	}
  7557	

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\''), path=require('\\''path'\\'');
let src=fs.readFileSync('\\''tests/js/fit_acceptance.test.js'\\'','\\''utf8'\\'').split(\"\\ntest('\\''A08:\")[0];
src=src.replace('\\''jobAdapter(withText(fetchImpl))'\\'','\\''withText(fetchImpl)'\\'');
const makeEnv=new Function('\\''require'\\'','\\''__dirname'\\'',src+'\\''\\nreturn makeEnv;'\\'')(require,path.resolve('\\''tests/js'\\''));
(async()=>{
let starts=0,cancels=0,pending=[];
const env=makeEnv({fetchImpl:async(url)=>{
 if(url==='\\''/api/fit/start'\\'') return {ok:true,status:202,json:async()=>({job_id:'\\''J'\\''+(++starts)})};
 if(url.startsWith('\\''/api/fit/cancel/'\\'')) {cancels++; return {ok:true,json:async()=>({})};}
 return await new Promise(resolve=>pending.push({url,resolve}));
}});
const first=env.runFit();
await new Promise(setImmediate);
const second=env.runFit();
await new Promise(setImmediate);
console.log(JSON.stringify({starts,cancels,pendingPolls:pending.map(p=>p.url)}));
for(const p of pending) p.resolve({ok:true,status:200,json:async()=>({status:'\\''done'\\'',result:{success:false,message:'\\''end probe'\\''}})});
await Promise.all([first,second]);
})();'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
{"starts":2,"cancels":0,"pendingPolls":["/api/fit/progress/J1","/api/fit/progress/J2"]}

exec
/bin/zsh -lc "/Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile
tempfile.tempdir='\\''/tmp'\\''
import app, threading, time, logging
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
import numpy as np
logging.disable(logging.CRITICAL)
x=np.linspace(281,291,100)
y=300+3000*np.exp(-4*np.log(2)*((x-285)/1.0)**2)
args=dict(energy=x,counts=y,peak_specs=[dict(id='\\''1'\\'',shape='\\''pseudo_voigt_gl'\\'',center=284.8,amplitude=2600,fwhm=1.2,gl_ratio=.3)],n_perturb=0)
a=SimpleNamespace(logger=logging.getLogger('\\''probe'\\''))
for method in ['\\''leastsq'\\'','\\''nelder'\\'','\\''differential_evolution'\\'']:
    records=[]
    marker=MagicMock()
    marker.exists.return_value=False
    marker.stat.return_value=SimpleNamespace(st_mtime=time.time()-181)
    with patch.object(app,'\\''_fit_job_write'\\'',side_effect=lambda j,f,r:records.append(dict(r))),patch.object(app,'\\''_fit_job_marker'\\'',return_value=marker):
        app._fit_job_start('\\''abandon-probe'\\'','\\''unused'\\'',dict(args,fit_kws={'\\''method'\\'':method}),lambda kw,c:app._run_fit_outcome(a,kw,cancel=c))
        deadline=time.monotonic()+5
        while records[-1]['\\''status'\\'']=='\\''running'\\'' and time.monotonic()<deadline: time.sleep(.01)
        print(method,records[-1],flush=True)
gate=threading.Event()
def hold(args,cancel):
    gate.wait(5)
    return 200, {'\\''success'\\'':True}
marker=MagicMock()
marker.exists.return_value=False
marker.stat.return_value=SimpleNamespace(st_mtime=time.time())
with patch.object(app.Path,'\\''mkdir'\\''),patch.object(app,'\\''_prepare_fit_request'\\'',return_value=({},None)),patch.object(app,'\\''_sweep_expired_jobs'\\''),patch.object(app,'\\''_sweep_fit_job_markers'\\''),patch.object(app,'\\''_fit_job_write'\\''),patch.object(app,'\\''_fit_job_marker'\\'',return_value=marker),patch.object(app,'\\''_run_fit_outcome'\\'',side_effect=hold):
    a=app.create_app()
    with a.test_client() as client:
        statuses=[client.post('\\''/api/fit/start'\\'',json={}).status_code for _ in range(12)]
        live=[t for t in threading.enumerate() if t.name.startswith('\\''fit-'\\'')]
        print('\\''12 starts in one worker:'\\'',statuses,'\\''live job threads:'\\'',len(live),flush=True)
        gate.set()
        for t in live: t.join(1)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 1761ms:
/Users/skyefortier/.matplotlib is not a writable directory
leastsq {'status': 'error', 'elapsed_sec': 0.0, 'heartbeat': 1790496675.4042501, 'error': 'Internal fitting error — see server log.', 'http_status': 500}
nelder {'status': 'error', 'elapsed_sec': 0.0, 'heartbeat': 1790496675.408722, 'error': 'Fit failed — see server log for details.', 'http_status': 422}
differential_evolution {'status': 'error', 'elapsed_sec': 0.0, 'heartbeat': 1790496675.4141881, 'error': 'Fit failed — see server log for details.', 'http_status': 422}
12 starts in one worker: [202, 202, 202, 202, 202, 202, 202, 202, 202, 202, 202, 202] live job threads: 0

exec
/bin/zsh -lc "/Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile
tempfile.tempdir='\\''/tmp'\\''
import app,threading,time,logging
from unittest.mock import patch,MagicMock
from types import SimpleNamespace
logging.disable(logging.CRITICAL)
gate=threading.Event()
def hold(appobj,args,cancel=None):
    gate.wait(5)
    return 200, {'\\''success'\\'':True}
marker=MagicMock()
marker.exists.return_value=False
marker.stat.return_value=SimpleNamespace(st_mtime=time.time())
with patch.object(app.Path,'\\''mkdir'\\''),patch.object(app,'\\''_prepare_fit_request'\\'',return_value=({},None)),patch.object(app,'\\''_sweep_expired_jobs'\\''),patch.object(app,'\\''_sweep_fit_job_markers'\\''),patch.object(app,'\\''_fit_job_write'\\''),patch.object(app,'\\''_fit_job_marker'\\'',return_value=marker),patch.object(app,'\\''_run_fit_outcome'\\'',side_effect=hold):
    a=app.create_app()
    with a.test_client() as client:
        statuses=[client.post('\\''/api/fit/start'\\'',json={}).status_code for _ in range(12)]
        live=[t for t in threading.enumerate() if t.name.startswith('\\''fit-'\\'')]
        print('\\''12 starts in one worker:'\\'',statuses,'\\''live job threads:'\\'',len(live),flush=True)
        gate.set()
        for t in live: t.join(1)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 1695ms:
/Users/skyefortier/.matplotlib is not a writable directory
12 starts in one worker: [202, 202, 202, 202, 202, 202, 202, 202, 202, 202, 202, 202] live job threads: 24

exec
/bin/zsh -lc "nl -ba scripts/public_fit_poll_check.py | sed -n '52,73p'; nl -ba templates/index.html | sed -n '8168,8179p'; git status --short" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
    52	               "peaks": t["specs"], "fit_method": "basinhopping", "n_perturb": 3, "n_starts": 3}
    53	    st, body, d = _req(base + "/api/fit/start", json.dumps(payload).encode(), {"Content-Type": "application/json"})
    54	    durations.append(("start", st, d))
    55	    if st != 202:
    56	        return {"id": t["id"], "verdict": "FAIL", "why": f"start returned {st}: {body[:200]!r}", "durations": durations}
    57	    job = json.loads(body)["job_id"]
    58	    t0 = time.time()
    59	    while True:
    60	        time.sleep(0.5)
    61	        st, body, d = _req(base + f"/api/fit/progress/{job}")
    62	        durations.append(("poll", st, d))
    63	        rec = json.loads(body) if st == 200 else {"status": f"http {st}"}
    64	        if rec.get("status") != "running":
    65	            break
    66	    longest = max(x[2] for x in durations)
    67	    res = rec.get("result") or {}
    68	    ok = rec.get("status") == "done" and res.get("success") is True and longest <= MAX_REQUEST_S
    69	    return {"id": t["id"], "verdict": "PASS" if ok else "FAIL", "status": rec.get("status"),
    70	            "success": res.get("success"), "chi2r": (res.get("statistics") or {}).get("reduced_chi_square"),
    71	            "fit_wall_s": round(time.time() - t0, 1), "n_requests": len(durations),
    72	            "longest_request_s": round(longest, 2), "error": rec.get("error")}
    73	
  8168	    };
  8169	    // Unit 2: started and polled (_serverFitJob) — no request lasts longer than
  8170	    // a poll, so none meets the public URL's ~100 s ceiling. An HTTP failure is
  8171	    // a SERVER failure (serverError), never a reason to switch engines; a
  8172	    // START that cannot reach the server is a transport failure, as the single
  8173	    // request was. The ownership checks below also run inside the poll loop,
  8174	    // so a switched tab or an edited model stops the server's work at once.
  8175	    const json = await _serverFitJob(fitReq, {
  8176	      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
  8177	    });
  8178	    if (json && json._abandoned === 'tab') {
  8179	      _hideFitSpinner();
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-mK9QjRJi' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-poz25mqo' (errno=Operation not permitted)
?? docs/autofit/codex/fit_start_poll_verdict_runA.md
?? docs/autofit/codex/fit_start_poll_verdict_runB.md

codex
1. **MAJOR — Re-running does not cancel the previous fit.** [templates/index.html:8176](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8176) checks only tab identity and model equality. Ctrl/Cmd+F calls `runFit()` despite the disabled button. Pressing it again with unchanged inputs starts another job; both remain polled, preventing abandonment cancellation. Reproduced: two starts, two pending polls, zero cancellations. The older fit can finish first and cause the replacement to be discarded as “model edited.” Track a per-owner invocation and cancel its predecessor.

2. **MAJOR — Fit concurrency is unbounded.** [app.py:672](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:672) launches two threads for every accepted start without admission control or a bounded queue. Gunicorn’s four synchronous workers therefore no longer bound concurrent fitting work. A filesystem-mocked probe accepted 12 starts in one process and retained 24 job threads. Repeated submissions or simultaneous students can accumulate CPU-heavy fits and numerical allocations, degrading polling and potentially exhausting memory. Bound active jobs and queued requests.

3. **MINOR — Abandonment cancellation becomes a solver error for several methods.** [fitting.py:2105](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/fitting.py:2105) checks `hit` only after `_run_fit_impl` returns normally. Cancellation-induced exceptions skip that check. Real numerical probes produced an `AttributeError` for Levenberg–Marquardt and `RuntimeError` for Nelder–Mead and DE. With an expired poll marker and no explicit cancel marker, job records consequently became `error` with HTTP 500/422 instead of `cancelled`. Normalize cancellation on exceptional exits while preserving unrelated errors.

4. **MINOR — The public acceptance checker can hang indefinitely.** [scripts/public_fit_poll_check.py:59](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/scripts/public_fit_poll_check.py:59) stops only when status changes. If the owning worker dies, its record remains `running`; subsequent polls succeed with an increasingly stale heartbeat. The script ignores that heartbeat and has no overall deadline, so it never reports failure or advances to the remaining targets.

All **83 targeted JavaScript tests passed**. Read-only Python probes reproduced the cancellation and concurrency findings. Full pytest and gunicorn acceptance measurements were not rerun; no files were changed.

**VERDICT: NO-GO**
tokens used
83,349
1. **MAJOR — Re-running does not cancel the previous fit.** [templates/index.html:8176](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8176) checks only tab identity and model equality. Ctrl/Cmd+F calls `runFit()` despite the disabled button. Pressing it again with unchanged inputs starts another job; both remain polled, preventing abandonment cancellation. Reproduced: two starts, two pending polls, zero cancellations. The older fit can finish first and cause the replacement to be discarded as “model edited.” Track a per-owner invocation and cancel its predecessor.

2. **MAJOR — Fit concurrency is unbounded.** [app.py:672](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:672) launches two threads for every accepted start without admission control or a bounded queue. Gunicorn’s four synchronous workers therefore no longer bound concurrent fitting work. A filesystem-mocked probe accepted 12 starts in one process and retained 24 job threads. Repeated submissions or simultaneous students can accumulate CPU-heavy fits and numerical allocations, degrading polling and potentially exhausting memory. Bound active jobs and queued requests.

3. **MINOR — Abandonment cancellation becomes a solver error for several methods.** [fitting.py:2105](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/fitting.py:2105) checks `hit` only after `_run_fit_impl` returns normally. Cancellation-induced exceptions skip that check. Real numerical probes produced an `AttributeError` for Levenberg–Marquardt and `RuntimeError` for Nelder–Mead and DE. With an expired poll marker and no explicit cancel marker, job records consequently became `error` with HTTP 500/422 instead of `cancelled`. Normalize cancellation on exceptional exits while preserving unrelated errors.

4. **MINOR — The public acceptance checker can hang indefinitely.** [scripts/public_fit_poll_check.py:59](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/scripts/public_fit_poll_check.py:59) stops only when status changes. If the owning worker dies, its record remains `running`; subsequent polls succeed with an increasingly stale heartbeat. The script ignores that heartbeat and has no overall deadline, so it never reports failure or advances to the remaining targets.

All **83 targeted JavaScript tests passed**. Read-only Python probes reproduced the cancellation and concurrency findings. Full pytest and gunicorn acceptance measurements were not rerun; no files were changed.

**VERDICT: NO-GO**
