OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0eeb7-4c98-78a3-be7f-c252b592cf09
--------
user
Review unit A1 (Find Peaks determinism), round 2: branch fix-find-peaks-determinism, git diff main..HEAD (round-1 fixes: git diff HEAD~1..HEAD) (autofit/engine.py; tests/autofit/test_fit_certificate.py; tests/autofit/test_preseed_dominants.py; CLAUDE.md; docs/superpowers/plans/2026-09-29-a1-find-peaks-determinism.md; the scope-check findings under docs/findings/fit-termination-scope/). Owner's brief: "Find Peaks' answer must not depend on server load or on the optimiser's own termination flags. Count refits, not seconds … REMOVE the warm restart from the cap stall point … apply the certificate to refits. Certificate accepted as proposed: restart from the end point until a restart improves chi2 by less than the optimiser's own stopping tolerance; fixed restart count; out of restarts = 'not converged'. No new constant. Acceptance: identical output under light and heavy load; Scan_6 -> MG2." Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

Round-1 verdicts: docs/autofit/codex/a1_determinism_verdict_run{A,B}.md; plan section 5 lists each finding and its fix; section 4 records a measured screen option that is an OWNER DECISION (not built).

TRY TO BREAK
a. The capped-restart rule in _certify_minimum: every exit (capped and lowered / capped and not lowered / not capped), lmfit's `aborted` semantics for least_squares and for max_nfev exhaustion of the INITIAL leastsq fit, the loop's count, the returned point.
b. The analyze job heartbeat (app.py analyze_start): the shared record under a lock, the heartbeat thread's lifetime (stops on done/error, never after the final write, no write racing the final record), a worker that fails to start, crashes, and the progress route's heartbeat_age_sec; the page's _fpPollJob: no total-duration cap anywhere, the stale-heartbeat rule (FIT_HEARTBEAT_LOST_SEC), a first poll without a heartbeat, transport errors, a job whose progress events are minutes apart.
c. The new clock test through the screen.
d. Everything round 1 verified, re-checked against the new commit.
e. Tests real and non-vacuous.

Finish with VERDICT: GO or VERDICT: NO-GO.

codex
I’ll check the full branch and round-1 fixes, then probe the restart certificate, heartbeat lifecycle, polling, and test coverage. I’ll keep the review read-only and finish with ranked findings and a verdict.

exec
/bin/zsh -lc "pwd; rg --files -g 'AGENTS.md' -g 'CLAUDE.md' -g '*a1*' -g '*certificate*' -g '*preseed*' -g '*heartbeat*' -g '*determinism*'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
CLAUDE.md
tests/autofit/test_preseed_dominants.py
tests/autofit/test_fit_certificate.py
docs/superpowers/plans/2026-09-29-a1-find-peaks-determinism.md
docs/autofit/codex/a1_determinism_verdict_runA.md
docs/autofit/codex/a1_determinism_verdict_runB.md
docs/autofit/codex/a1_determinism_recheck_prompt.txt
docs/autofit/codex/a1_determinism_r2_verdict_runA.md
docs/autofit/codex/a1_determinism_review_prompt.txt
docs/autofit/codex/a1_determinism_r2_verdict_runB.md

exec
/bin/zsh -lc 'git status --short; git log -4 --oneline; git diff --stat main..HEAD; git diff --stat HEAD~1..HEAD' in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 122ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-gsfka5MJ' (errno=Operation not permitted)
 CLAUDE.md                                          |   19 +
 app.py                                             |   74 +-
 autofit/engine.py                                  |  282 +-
 .../codex/a1_determinism_recheck_prompt.txt        |   12 +
 .../autofit/codex/a1_determinism_review_prompt.txt |   10 +
 docs/autofit/codex/a1_determinism_verdict_runA.md  | 5700 +++++++++++++++++
 docs/autofit/codex/a1_determinism_verdict_runB.md  | 6697 ++++++++++++++++++++
 docs/findings/fit-termination-scope/README.md      |   51 +
 .../fit-termination-scope/scope_lm_a.jsonl         |  101 +
 .../fit-termination-scope/scope_lm_b.jsonl         |  101 +
 .../fit-termination-scope/scope_tr_a.jsonl         |  101 +
 .../fit-termination-scope/scope_tr_b.jsonl         |  101 +
 .../plans/2026-09-29-a1-find-peaks-determinism.md  |  132 +
 scripts/fit_termination_scope.py                   |   45 +
 scripts/fit_termination_scope_analyze.py           |   31 +
 templates/index.html                               |   23 +-
 tests/autofit/test_fit_certificate.py              |  152 +
 tests/autofit/test_preseed_dominants.py            |  127 +-
 tests/js/find_peaks_poll_liveness.test.js          |   65 +
 tests/test_api_analyze_progress.py                 |   28 +
 20 files changed, 13567 insertions(+), 285 deletions(-)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-iyUsp9kr' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-8oTIghlf' (errno=Operation not permitted)
 app.py                                             |   74 +-
 autofit/engine.py                                  |   16 +-
 .../codex/a1_determinism_recheck_prompt.txt        |   12 +
 docs/autofit/codex/a1_determinism_verdict_runA.md  | 5700 +++++++++++++++++
 docs/autofit/codex/a1_determinism_verdict_runB.md  | 6697 ++++++++++++++++++++
 .../plans/2026-09-29-a1-find-peaks-determinism.md  |   34 +
 templates/index.html                               |   23 +-
 tests/autofit/test_fit_certificate.py              |   15 +
 tests/autofit/test_preseed_dominants.py            |   42 +
 tests/js/find_peaks_poll_liveness.test.js          |   65 +
 tests/test_api_analyze_progress.py                 |   28 +
 11 files changed, 12664 insertions(+), 42 deletions(-)

exec
/bin/zsh -lc 'cat CLAUDE.md; cat docs/superpowers/plans/2026-09-29-a1-find-peaks-determinism.md; cat docs/findings/fit-termination-scope/README.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
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

**Real-data gates** (`RUN_AUTOFIT_GATE=1`: C 1s, U 4f, B 1s / Cl 2p parity;
Bayesian real and U 4f unresolved; candidate-pool real incl. the local-only
held-out datasets, symlinked in for the run; stress honesty): **27 passed, 0
failed** (main: 26 / 1 — the held-out ds8 candidate-pool gate failed there
because the 240 s sweep budget stopped after 3 of 6 candidates; it passes now).
Runtime 36 min against ~18 on main (no truncation, certificate restarts).

## 4. Screen option measured (NOT built — owner decision)

Probe (`screen each candidate from its primary start PLUS 2 seeded perturbed
starts, keep the best certified outcome`), page request:

| scan | main | A1 as built | A1 + 2 extra screen starts |
|---|---|---|---|
| 8-JT Scan_5 | MG2, BIC* 1882.6 | MG3, 1901.5 | **MG2, 1882.7** |
| 8-JT Scan_7 | MG2, 1776.8 | MG3, 1787.6 | **MG2, 1776.5** |
| 1-GTA Scan_6 | MG2+preseed, 1888.8 | MG2+preseed, 1888.4 | MG2+preseed, 1888.4 |

Wall time 386–405 s per run (measured while Codex and the gates were also
running — inflated) against A1's 236–239 s and main's 208–213 s.

## 5. Codex rounds

**Round 1 — NO-GO ×2** (`a1_determinism_verdict_run{A,B}.md`; both: no clock
decision left in the engine, the Bayesian method or the analyze worker; §3's
screen cases need explicit acceptance but do not violate A1's contract; the
jitter is not a clock cutoff; Scan_6 → MG2 reproduced):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A): a certificate restart cut off by its EVALUATION CAP can end a hair ABOVE its start; the negative improvement passed "< ftol" and a point 3000× above the minimum was certified (reproduced at max_nfev = 2, not at the production 6000 / 18000) | a capped restart (lmfit's `aborted` — the budget, not a convergence verdict) never certifies: if it lowered chi2 the next restart continues from there, if not the fit is not converged. Regression caps the certificate's own restarts (fails on 3d419eb) |
| 2 | MAJOR (B): the page's Find Peaks poll gave up after 600 s TOTAL, even while the job progressed; with the server budgets gone, load could turn a result into "Try again" | liveness, not duration: the analyze job now has a heartbeat thread (the fit jobs' pattern, 2 s), `/api/analyze/progress` reports `heartbeat_age_sec`, the page judges a job lost only when the heartbeat is older than `FIT_HEARTBEAT_LOST_SEC` (30 s). Tests: `test_a_running_job_keeps_a_fresh_heartbeat` (Python), `tests/js/find_peaks_poll_liveness.test.js` |
| 3 | MINOR (A, B): the clock-independence test never reached the screen (one candidate) | `test_no_wall_clock_can_change_the_screen_or_the_refit_counts`: > SCREEN_TOP_K candidates under a jumping clock — every candidate screened, exactly n_refits refits each, identical result (fails on main's engine: nothing screened) |
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

exec
/bin/zsh -lc "rg --files -g 'AGENTS.md' /Users/skyefortier/xps-app /Users/skyefortier/.codex 2>/dev/null | head -60; ls -d .venv venv 2>/dev/null; rg -n 'BLOCKER|MAJOR|MINOR|VERDICT' docs/autofit/codex/a1_determinism_verdict_runA.md docs/autofit/codex/a1_determinism_verdict_runB.md | tail -65" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
docs/autofit/codex/a1_determinism_verdict_runA.md:15:Review unit A1 (Find Peaks determinism), round 1: branch fix-find-peaks-determinism, git diff main..HEAD (autofit/engine.py; tests/autofit/test_fit_certificate.py; tests/autofit/test_preseed_dominants.py; CLAUDE.md; docs/superpowers/plans/2026-09-29-a1-find-peaks-determinism.md; the scope-check findings under docs/findings/fit-termination-scope/). Owner's brief: "Find Peaks' answer must not depend on server load or on the optimiser's own termination flags. Count refits, not seconds … REMOVE the warm restart from the cap stall point … apply the certificate to refits. Certificate accepted as proposed: restart from the end point until a restart improves chi2 by less than the optimiser's own stopping tolerance; fixed restart count; out of restarts = 'not converged'. No new constant. Acceptance: identical output under light and heavy load; Scan_6 -> MG2." Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.
docs/autofit/codex/a1_determinism_verdict_runA.md:24:Finish with VERDICT: GO or VERDICT: NO-GO.
docs/autofit/codex/a1_determinism_verdict_runA.md:1342:-# (Codex c1s-fix review, run B MAJOR).  A proposal attempt that cannot fit
docs/autofit/codex/a1_determinism_verdict_runA.md:1605:-    # and the gunicorn --timeout (Codex c1s-fix review, run B MAJOR).  The
docs/autofit/codex/a1_determinism_verdict_runA.md:1622:-    # review, run B MAJOR — otherwise the stability pass could run
docs/autofit/codex/a1_determinism_verdict_runA.md:1628:-    # run B MAJOR: disposition 2 was not fully closed by the top guard).
docs/autofit/codex/a1_determinism_verdict_runA.md:1923:-    """Codex c1s-fix MAJOR (run B): an augmented fit has no internal wall
docs/autofit/codex/a1_determinism_verdict_runA.md:2027:-    # and the gunicorn --timeout (Codex c1s-fix review, run B MAJOR).  The
docs/autofit/codex/a1_determinism_verdict_runA.md:2044:-    # review, run B MAJOR — otherwise the stability pass could run
docs/autofit/codex/a1_determinism_verdict_runA.md:2050:-    # run B MAJOR: disposition 2 was not fully closed by the top guard).
docs/autofit/codex/a1_determinism_verdict_runA.md:2373:-    """Codex c1s-fix MAJOR (run B): an augmented fit has no internal wall
docs/autofit/codex/a1_determinism_verdict_runA.md:3840:        # record on the winner row (Codex fwhm-cap review, run A MINOR)
docs/autofit/codex/a1_determinism_verdict_runA.md:5651:1. **MAJOR — An evaluation-aborted restart can falsely certify a non-minimum.** [autofit/engine.py:850](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/autofit/engine.py:850)
docs/autofit/codex/a1_determinism_verdict_runA.md:5664:2. **MINOR — The clock-independence test never exercises screening.** [tests/autofit/test_preseed_dominants.py:430](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/tests/autofit/test_preseed_dominants.py:430)
docs/autofit/codex/a1_determinism_verdict_runA.md:5674:**VERDICT: NO-GO**
docs/autofit/codex/a1_determinism_verdict_runA.md:5677:1. **MAJOR — An evaluation-aborted restart can falsely certify a non-minimum.** [autofit/engine.py:850](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/autofit/engine.py:850)
docs/autofit/codex/a1_determinism_verdict_runA.md:5690:2. **MINOR — The clock-independence test never exercises screening.** [tests/autofit/test_preseed_dominants.py:430](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/tests/autofit/test_preseed_dominants.py:430)
docs/autofit/codex/a1_determinism_verdict_runA.md:5700:**VERDICT: NO-GO**
docs/autofit/codex/a1_determinism_verdict_runB.md:14:Review unit A1 (Find Peaks determinism), round 1: branch fix-find-peaks-determinism, git diff main..HEAD (autofit/engine.py; tests/autofit/test_fit_certificate.py; tests/autofit/test_preseed_dominants.py; CLAUDE.md; docs/superpowers/plans/2026-09-29-a1-find-peaks-determinism.md; the scope-check findings under docs/findings/fit-termination-scope/). Owner's brief: "Find Peaks' answer must not depend on server load or on the optimiser's own termination flags. Count refits, not seconds … REMOVE the warm restart from the cap stall point … apply the certificate to refits. Certificate accepted as proposed: restart from the end point until a restart improves chi2 by less than the optimiser's own stopping tolerance; fixed restart count; out of restarts = 'not converged'. No new constant. Acceptance: identical output under light and heavy load; Scan_6 -> MG2." Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.
docs/autofit/codex/a1_determinism_verdict_runB.md:23:Finish with VERDICT: GO or VERDICT: NO-GO.
docs/autofit/codex/a1_determinism_verdict_runB.md:69:-# (Codex c1s-fix review, run B MAJOR).  A proposal attempt that cannot fit
docs/autofit/codex/a1_determinism_verdict_runB.md:332:-    # and the gunicorn --timeout (Codex c1s-fix review, run B MAJOR).  The
docs/autofit/codex/a1_determinism_verdict_runB.md:349:-    # review, run B MAJOR — otherwise the stability pass could run
docs/autofit/codex/a1_determinism_verdict_runB.md:355:-    # run B MAJOR: disposition 2 was not fully closed by the top guard).
docs/autofit/codex/a1_determinism_verdict_runB.md:650:-    """Codex c1s-fix MAJOR (run B): an augmented fit has no internal wall
docs/autofit/codex/a1_determinism_verdict_runB.md:2012:-    # and the gunicorn --timeout (Codex c1s-fix review, run B MAJOR).  The
docs/autofit/codex/a1_determinism_verdict_runB.md:2029:-    # review, run B MAJOR — otherwise the stability pass could run
docs/autofit/codex/a1_determinism_verdict_runB.md:2035:-    # run B MAJOR: disposition 2 was not fully closed by the top guard).
docs/autofit/codex/a1_determinism_verdict_runB.md:2328:-    """Codex c1s-fix MAJOR (run B): an augmented fit has no internal wall
docs/autofit/codex/a1_determinism_verdict_runB.md:2837:            # (Codex Stage-2 review, run A MAJOR).
docs/autofit/codex/a1_determinism_verdict_runB.md:3702:    # to a wall (Codex fwhm-cap review, run B BLOCKER).
docs/autofit/codex/a1_determinism_verdict_runB.md:3744:    # BLOCKER): a stability-promoted center@min must STILL reject, and a
docs/autofit/codex/a1_determinism_verdict_runB.md:3887:        # record on the winner row (Codex fwhm-cap review, run A MINOR)
docs/autofit/codex/a1_determinism_verdict_runB.md:4379:        # record on the winner row (Codex fwhm-cap review, run A MINOR)
docs/autofit/codex/a1_determinism_verdict_runB.md:6658:The polling failure is reproduced with the page’s actual function: the same `running → done(MG2)` responses succeed at 599 seconds, but throw “Try again” at 601 seconds without reading the completed result. That is a MAJOR integration gap after removing the server budgets. The additional doublet, stability-consumer, and Bayesian tests passed: 44 tests total so far.
docs/autofit/codex/a1_determinism_verdict_runB.md:6674:- **MAJOR — The browser still abandons valid analyses after 600 seconds.** [templates/index.html:16159](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/templates/index.html:16159), exposed by removing the sweep deadline at [autofit/engine.py:2741](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/autofit/engine.py:2741). This checks total elapsed time, even while progress continues. I executed the actual polling function with identical `running → done(MG2)` responses: at 599 seconds it delivers MG2; at 601 seconds it throws “Try again” before fetching completion. Thus sufficient server load changes the page’s outcome from a result to failure. The watchdog explicitly assumes the removed server budget exists. Replace this total-duration cutoff with job-liveness handling that permits long counted workloads.
docs/autofit/codex/a1_determinism_verdict_runB.md:6676:- **MINOR — The clock-independence test never exercises screening.** [tests/autofit/test_preseed_dominants.py:430](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/tests/autofit/test_preseed_dominants.py:430). Its one-candidate grammar, with preseeding disabled, cannot enter the `> SCREEN_TOP_K` branch. Reintroducing a screen deadline would leave this test passing while loaded full-grammar requests lose candidates. Add a clock-jump case with more than six candidates and assert complete screening and refit counts.
docs/autofit/codex/a1_determinism_verdict_runB.md:6684:VERDICT: NO-GO.
docs/autofit/codex/a1_determinism_verdict_runB.md:6687:- **MAJOR — The browser still abandons valid analyses after 600 seconds.** [templates/index.html:16159](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/templates/index.html:16159), exposed by removing the sweep deadline at [autofit/engine.py:2741](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/autofit/engine.py:2741). This checks total elapsed time, even while progress continues. I executed the actual polling function with identical `running → done(MG2)` responses: at 599 seconds it delivers MG2; at 601 seconds it throws “Try again” before fetching completion. Thus sufficient server load changes the page’s outcome from a result to failure. The watchdog explicitly assumes the removed server budget exists. Replace this total-duration cutoff with job-liveness handling that permits long counted workloads.
docs/autofit/codex/a1_determinism_verdict_runB.md:6689:- **MINOR — The clock-independence test never exercises screening.** [tests/autofit/test_preseed_dominants.py:430](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/tests/autofit/test_preseed_dominants.py:430). Its one-candidate grammar, with preseeding disabled, cannot enter the `> SCREEN_TOP_K` branch. Reintroducing a screen deadline would leave this test passing while loaded full-grammar requests lose candidates. Add a clock-jump case with more than six candidates and assert complete screening and refit counts.
docs/autofit/codex/a1_determinism_verdict_runB.md:6697:VERDICT: NO-GO.

exec
/bin/zsh -lc 'git diff main..HEAD -- autofit/engine.py app.py templates/index.html' in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-eSuO1krp' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-fZYzXyzA' (errno=Operation not permitted)
diff --git a/app.py b/app.py
index 79c5eb2..6219318 100644
--- a/app.py
+++ b/app.py
@@ -1183,21 +1183,42 @@ def _register_routes(app: Flask) -> None:
         job_id = str(uuid.uuid4())
         _sweep_expired_jobs(upload_folder)
         start_time = time.time()
-        _write_job_progress(job_id, upload_folder, {
-            "status": "running", "phase": "starting",
-            "candidate_index": None, "candidate_total": None,
-            "candidate_name": None, "elapsed_sec": 0.0,
-            "message": "starting analysis…",
-        })
+        # Unit A1 (2026-09-29): the record carries a HEARTBEAT, rewritten every
+        # FIT_JOB_HEARTBEAT_SEC while the worker thread lives (fit jobs' pattern,
+        # unit 2). The engine no longer stops on a wall-clock budget, so a long
+        # counted run under load is normal; the page judges the job lost only
+        # when the heartbeat stops (a recycled worker), never by total time.
+        lock = threading.Lock()
+        finished = threading.Event()
+        rec = {"status": "running", "phase": "starting",
+               "candidate_index": None, "candidate_total": None,
+               "candidate_name": None, "elapsed_sec": 0.0,
+               "message": "starting analysis…", "heartbeat": start_time}
+        _write_job_progress(job_id, upload_folder, rec)
+
+        def _publish(update: dict) -> None:
+            with lock:
+                rec.update(update)
+                rec["elapsed_sec"] = round(time.time() - start_time, 1)
+                rec["heartbeat"] = time.time()
+                _write_job_progress(job_id, upload_folder, rec)
+
+        def _heartbeat() -> None:
+            while not finished.wait(FIT_JOB_HEARTBEAT_SEC):
+                with lock:
+                    if rec["status"] != "running":
+                        return
+                    rec["heartbeat"] = time.time()
+                    rec["elapsed_sec"] = round(time.time() - start_time, 1)
+                    _write_job_progress(job_id, upload_folder, rec)
 
         def _progress_cb(evt: dict) -> None:
-            _write_job_progress(job_id, upload_folder, {
+            _publish({
                 "status": "running",
                 "phase": evt.get("phase"),
                 "candidate_index": evt.get("candidate_index"),
                 "candidate_total": evt.get("candidate_total"),
                 "candidate_name": evt.get("candidate_name"),
-                "elapsed_sec": round(time.time() - start_time, 1),
                 "message": _analyze_progress_message(evt),
             })
 
@@ -1205,33 +1226,26 @@ def _register_routes(app: Flask) -> None:
             try:
                 res = _run_analyze_method(ctx, progress_cb=_progress_cb)
                 payload = _build_analyze_payload(ctx, res)
-                _write_job_progress(job_id, upload_folder, {
-                    "status": "done", "phase": "done",
-                    "elapsed_sec": round(time.time() - start_time, 1),
-                    "message": "done",
-                    "result": payload,
-                })
+                final = {"status": "done", "phase": "done", "message": "done", "result": payload}
             except _AnalyzeError as exc:
-                _write_job_progress(job_id, upload_folder, {
-                    "status": "error", "phase": "done",
-                    "elapsed_sec": round(time.time() - start_time, 1),
-                    "message": "failed", "error": str(exc),
-                    "http_status": exc.status,
-                })
+                final = {"status": "error", "phase": "done", "message": "failed",
+                         "error": str(exc), "http_status": exc.status}
             except Exception as exc:      # belt-and-suspenders: the
                 # indicator must ALWAYS clear, even on a bug we didn't
                 # anticipate — never let a job hang the poll forever.
                 logging.getLogger(__name__).exception(
                     "analyze job %s crashed", job_id)
-                _write_job_progress(job_id, upload_folder, {
-                    "status": "error", "phase": "done",
-                    "elapsed_sec": round(time.time() - start_time, 1),
-                    "message": "failed",
-                    "error": f"internal error: {exc}",
-                    "http_status": 500,
-                })
-
-        threading.Thread(target=_worker, daemon=True).start()
+                final = {"status": "error", "phase": "done", "message": "failed",
+                         "error": f"internal error: {exc}", "http_status": 500}
+            finished.set()
+            _publish(final)
+
+        threading.Thread(target=_heartbeat, daemon=True, name=f"fp-hb-{job_id[:8]}").start()
+        try:
+            threading.Thread(target=_worker, daemon=True, name=f"fp-{job_id[:8]}").start()
+        except Exception:
+            finished.set()                # no heartbeat for a job that never ran
+            raise
         return jsonify({"job_id": job_id}), 202
 
     @app.get("/api/analyze/progress/<job_id>")
@@ -1258,6 +1272,8 @@ def _register_routes(app: Flask) -> None:
                     "candidate_index": None, "candidate_total": None,
                     "candidate_name": None, "elapsed_sec": 0.0,
                     "message": "starting analysis…"}
+        hb = data.get("heartbeat")
+        data["heartbeat_age_sec"] = round(time.time() - hb, 1) if isinstance(hb, (int, float)) else None
         return jsonify(data)
 
     # ── Long fits via start-then-poll (unit 2, 2026-09-27) ───────────────────
diff --git a/autofit/engine.py b/autofit/engine.py
index dbf4fd7..333de82 100644
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
@@ -849,6 +808,65 @@ def _unphysical_width_flags(
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
+    """Return (the lowest-chi2 point reached, certified). ``max_nfev`` caps
+    each restart like the fit it certifies."""
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
+        lowered = new < chi
+        if lowered:
+            current, chi = r, new
+        # A restart cut off by its EVALUATION CAP (lmfit's `aborted` — a fact
+        # about the budget, not the optimiser's convergence verdict) never
+        # certifies: an unfinished descent can end a hair ABOVE its start, and
+        # that negative "improvement" passed the test (Codex A1 round 1). If
+        # it still lowered chi2 the next restart continues from there; if not,
+        # no progress is possible within the cap — not converged.
+        if getattr(r, "aborted", False):
+            if not lowered:
+                return current, False
+            continue
+        if improvement < CERTIFY_FTOL:
+            return current, True
+    return current, False
+
+
 def fit_candidate(
     x: np.ndarray,
     y: np.ndarray,
@@ -889,25 +907,13 @@ def fit_candidate(
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
@@ -917,9 +923,13 @@ def fit_candidate(
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
@@ -1144,11 +1154,9 @@ class ModelStability:
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
 
@@ -1169,16 +1177,16 @@ def run_stability_analysis(
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
@@ -1205,14 +1213,6 @@ def run_stability_analysis(
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
@@ -1616,11 +1616,9 @@ class ComparisonResult:
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
@@ -2166,11 +2164,12 @@ def _attempt_proposal(
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
@@ -2187,16 +2186,6 @@ def _attempt_proposal(
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
@@ -2251,28 +2240,9 @@ def _attempt_proposal(
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
@@ -2445,7 +2415,6 @@ def _bound_fixed_refit(
         x, y, weights, report.model, outcome,
         noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
         fixed_param_values=fixed,
-        deadline=time.perf_counter() + CANDIDATE_TIMEOUT_SEC,
         fit_full_window=fit_full_window,
         endpoint_avg=endpoint_avg,
     )
@@ -2738,7 +2707,6 @@ def compare_models(
     proposal_attempts: list[tuple[str, ProposedPeakReport]] = []
     timings: list[ProposalPassTiming] = []
     n_cand = len(candidates)
-    sweep_start = time.perf_counter()
     n_evaluated = 0
     analysis_truncated = False
 
@@ -2750,16 +2718,9 @@ def compare_models(
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
@@ -2789,30 +2750,11 @@ def compare_models(
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
@@ -2824,7 +2766,6 @@ def compare_models(
         stability = run_stability_analysis(
             x, y, weights, model, primary,
             noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
-            deadline=candidate_deadline,
             fit_full_window=fit_full_window,
             endpoint_avg=endpoint_avg,
         )
@@ -2864,20 +2805,12 @@ def compare_models(
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
@@ -2894,10 +2827,6 @@ def compare_models(
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
@@ -2905,7 +2834,6 @@ def compare_models(
                         absent_slot_area_fraction=absent_slot_area_fraction,
                         absent_slot_persistence_threshold=absent_slot_persistence_threshold,
                         diagnostic_windows=diagnostic_windows,
-                        budget_remaining=pass_budget - elapsed,
                         fit_full_window=fit_full_window,
                         endpoint_avg=endpoint_avg,
                     )
diff --git a/templates/index.html b/templates/index.html
index 7a74e29..e44a732 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -16136,15 +16136,15 @@ function _fpProgressText(poll) {
 }
 
 const FP_POLL_INTERVAL_MS = 350;
-// Client-side watchdog: the actual analysis has its own server-side budget
-// (TOTAL_ANALYSIS_TIMEOUT_SEC, well under this), so this only fires if a
-// job's progress file stops updating entirely (e.g. a recycled gunicorn
-// worker process taking the background thread down with it) — the
-// indicator must NEVER spin forever even in that pathological case.
-const FP_POLL_WATCHDOG_SEC = 600;
-
+// Liveness, not total time (unit A1, 2026-09-29): the engine no longer stops
+// on a wall-clock budget, so a counted run under heavy load legitimately takes
+// longer than any fixed limit — a 600 s total cap turned such a run into
+// "Try again" (Codex A1 round 1). The server rewrites the job's heartbeat every
+// 2 s while its thread lives; a heartbeat older than FIT_HEARTBEAT_LOST_SEC
+// means the thread is gone (e.g. a recycled gunicorn worker), and the
+// indicator must never spin forever in that case. A record without a
+// heartbeat age yet (the very first poll) is waited on.
 async function _fpPollJob(jobId) {
-  const started = Date.now();
   while (true) {
     const resp = await fetch('/api/analyze/progress/' + encodeURIComponent(jobId));
     if (!resp.ok) {
@@ -16156,9 +16156,10 @@ async function _fpPollJob(jobId) {
     if (poll.status === 'error') {
       throw new Error(poll.error || 'Analysis failed.');
     }
-    if ((Date.now() - started) / 1000 > FP_POLL_WATCHDOG_SEC) {
-      throw new Error('This is taking unusually long — the analysis may ' +
-        'have been lost. Try again.');
+    const hb = poll.heartbeat_age_sec;
+    if (typeof hb === 'number' && hb > FIT_HEARTBEAT_LOST_SEC) {
+      throw new Error('The analysis stopped responding (its server process was ' +
+        'probably restarted). Try again.');
     }
     await new Promise(r => setTimeout(r, FP_POLL_INTERVAL_MS));
   }

exec
/bin/zsh -lc 'cat docs/superpowers/plans/2026-09-29-a1-find-peaks-determinism.md; cat docs/findings/fit-termination-scope/README.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
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

**Real-data gates** (`RUN_AUTOFIT_GATE=1`: C 1s, U 4f, B 1s / Cl 2p parity;
Bayesian real and U 4f unresolved; candidate-pool real incl. the local-only
held-out datasets, symlinked in for the run; stress honesty): **27 passed, 0
failed** (main: 26 / 1 — the held-out ds8 candidate-pool gate failed there
because the 240 s sweep budget stopped after 3 of 6 candidates; it passes now).
Runtime 36 min against ~18 on main (no truncation, certificate restarts).

## 4. Screen option measured (NOT built — owner decision)

Probe (`screen each candidate from its primary start PLUS 2 seeded perturbed
starts, keep the best certified outcome`), page request:

| scan | main | A1 as built | A1 + 2 extra screen starts |
|---|---|---|---|
| 8-JT Scan_5 | MG2, BIC* 1882.6 | MG3, 1901.5 | **MG2, 1882.7** |
| 8-JT Scan_7 | MG2, 1776.8 | MG3, 1787.6 | **MG2, 1776.5** |
| 1-GTA Scan_6 | MG2+preseed, 1888.8 | MG2+preseed, 1888.4 | MG2+preseed, 1888.4 |

Wall time 386–405 s per run (measured while Codex and the gates were also
running — inflated) against A1's 236–239 s and main's 208–213 s.

## 5. Codex rounds

**Round 1 — NO-GO ×2** (`a1_determinism_verdict_run{A,B}.md`; both: no clock
decision left in the engine, the Bayesian method or the analyze worker; §3's
screen cases need explicit acceptance but do not violate A1's contract; the
jitter is not a clock cutoff; Scan_6 → MG2 reproduced):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A): a certificate restart cut off by its EVALUATION CAP can end a hair ABOVE its start; the negative improvement passed "< ftol" and a point 3000× above the minimum was certified (reproduced at max_nfev = 2, not at the production 6000 / 18000) | a capped restart (lmfit's `aborted` — the budget, not a convergence verdict) never certifies: if it lowered chi2 the next restart continues from there, if not the fit is not converged. Regression caps the certificate's own restarts (fails on 3d419eb) |
| 2 | MAJOR (B): the page's Find Peaks poll gave up after 600 s TOTAL, even while the job progressed; with the server budgets gone, load could turn a result into "Try again" | liveness, not duration: the analyze job now has a heartbeat thread (the fit jobs' pattern, 2 s), `/api/analyze/progress` reports `heartbeat_age_sec`, the page judges a job lost only when the heartbeat is older than `FIT_HEARTBEAT_LOST_SEC` (30 s). Tests: `test_a_running_job_keeps_a_fresh_heartbeat` (Python), `tests/js/find_peaks_poll_liveness.test.js` |
| 3 | MINOR (A, B): the clock-independence test never reached the screen (one candidate) | `test_no_wall_clock_can_change_the_screen_or_the_refit_counts`: > SCREEN_TOP_K candidates under a jumping clock — every candidate screened, exactly n_refits refits each, identical result (fails on main's engine: nothing screened) |
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

exec
/bin/zsh -lc 'git diff HEAD~1..HEAD -- autofit/engine.py app.py templates/index.html tests/test_api_analyze_progress.py tests/js/find_peaks_poll_liveness.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-1HPc1793' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-aGSHfZEN' (errno=Operation not permitted)
diff --git a/app.py b/app.py
index 79c5eb2..6219318 100644
--- a/app.py
+++ b/app.py
@@ -1183,21 +1183,42 @@ def _register_routes(app: Flask) -> None:
         job_id = str(uuid.uuid4())
         _sweep_expired_jobs(upload_folder)
         start_time = time.time()
-        _write_job_progress(job_id, upload_folder, {
-            "status": "running", "phase": "starting",
-            "candidate_index": None, "candidate_total": None,
-            "candidate_name": None, "elapsed_sec": 0.0,
-            "message": "starting analysis…",
-        })
+        # Unit A1 (2026-09-29): the record carries a HEARTBEAT, rewritten every
+        # FIT_JOB_HEARTBEAT_SEC while the worker thread lives (fit jobs' pattern,
+        # unit 2). The engine no longer stops on a wall-clock budget, so a long
+        # counted run under load is normal; the page judges the job lost only
+        # when the heartbeat stops (a recycled worker), never by total time.
+        lock = threading.Lock()
+        finished = threading.Event()
+        rec = {"status": "running", "phase": "starting",
+               "candidate_index": None, "candidate_total": None,
+               "candidate_name": None, "elapsed_sec": 0.0,
+               "message": "starting analysis…", "heartbeat": start_time}
+        _write_job_progress(job_id, upload_folder, rec)
+
+        def _publish(update: dict) -> None:
+            with lock:
+                rec.update(update)
+                rec["elapsed_sec"] = round(time.time() - start_time, 1)
+                rec["heartbeat"] = time.time()
+                _write_job_progress(job_id, upload_folder, rec)
+
+        def _heartbeat() -> None:
+            while not finished.wait(FIT_JOB_HEARTBEAT_SEC):
+                with lock:
+                    if rec["status"] != "running":
+                        return
+                    rec["heartbeat"] = time.time()
+                    rec["elapsed_sec"] = round(time.time() - start_time, 1)
+                    _write_job_progress(job_id, upload_folder, rec)
 
         def _progress_cb(evt: dict) -> None:
-            _write_job_progress(job_id, upload_folder, {
+            _publish({
                 "status": "running",
                 "phase": evt.get("phase"),
                 "candidate_index": evt.get("candidate_index"),
                 "candidate_total": evt.get("candidate_total"),
                 "candidate_name": evt.get("candidate_name"),
-                "elapsed_sec": round(time.time() - start_time, 1),
                 "message": _analyze_progress_message(evt),
             })
 
@@ -1205,33 +1226,26 @@ def _register_routes(app: Flask) -> None:
             try:
                 res = _run_analyze_method(ctx, progress_cb=_progress_cb)
                 payload = _build_analyze_payload(ctx, res)
-                _write_job_progress(job_id, upload_folder, {
-                    "status": "done", "phase": "done",
-                    "elapsed_sec": round(time.time() - start_time, 1),
-                    "message": "done",
-                    "result": payload,
-                })
+                final = {"status": "done", "phase": "done", "message": "done", "result": payload}
             except _AnalyzeError as exc:
-                _write_job_progress(job_id, upload_folder, {
-                    "status": "error", "phase": "done",
-                    "elapsed_sec": round(time.time() - start_time, 1),
-                    "message": "failed", "error": str(exc),
-                    "http_status": exc.status,
-                })
+                final = {"status": "error", "phase": "done", "message": "failed",
+                         "error": str(exc), "http_status": exc.status}
             except Exception as exc:      # belt-and-suspenders: the
                 # indicator must ALWAYS clear, even on a bug we didn't
                 # anticipate — never let a job hang the poll forever.
                 logging.getLogger(__name__).exception(
                     "analyze job %s crashed", job_id)
-                _write_job_progress(job_id, upload_folder, {
-                    "status": "error", "phase": "done",
-                    "elapsed_sec": round(time.time() - start_time, 1),
-                    "message": "failed",
-                    "error": f"internal error: {exc}",
-                    "http_status": 500,
-                })
-
-        threading.Thread(target=_worker, daemon=True).start()
+                final = {"status": "error", "phase": "done", "message": "failed",
+                         "error": f"internal error: {exc}", "http_status": 500}
+            finished.set()
+            _publish(final)
+
+        threading.Thread(target=_heartbeat, daemon=True, name=f"fp-hb-{job_id[:8]}").start()
+        try:
+            threading.Thread(target=_worker, daemon=True, name=f"fp-{job_id[:8]}").start()
+        except Exception:
+            finished.set()                # no heartbeat for a job that never ran
+            raise
         return jsonify({"job_id": job_id}), 202
 
     @app.get("/api/analyze/progress/<job_id>")
@@ -1258,6 +1272,8 @@ def _register_routes(app: Flask) -> None:
                     "candidate_index": None, "candidate_total": None,
                     "candidate_name": None, "elapsed_sec": 0.0,
                     "message": "starting analysis…"}
+        hb = data.get("heartbeat")
+        data["heartbeat_age_sec"] = round(time.time() - hb, 1) if isinstance(hb, (int, float)) else None
         return jsonify(data)
 
     # ── Long fits via start-then-poll (unit 2, 2026-09-27) ───────────────────
diff --git a/autofit/engine.py b/autofit/engine.py
index 65e2be0..333de82 100644
--- a/autofit/engine.py
+++ b/autofit/engine.py
@@ -831,7 +831,8 @@ CERTIFY_MAX_RESTARTS = 50
 
 
 def _certify_minimum(composite, y_sub, result, x, weights, max_nfev):
-    """Return (the lowest-chi2 point reached, certified)."""
+    """Return (the lowest-chi2 point reached, certified). ``max_nfev`` caps
+    each restart like the fit it certifies."""
     current = result
     chi = float(result.chisqr) if result.chisqr is not None else float("nan")
     if not np.isfinite(chi):
@@ -848,8 +849,19 @@ def _certify_minimum(composite, y_sub, result, x, weights, max_nfev):
         if not np.isfinite(new):
             return current, False
         improvement = (chi - new) / chi if chi > 0 else 0.0
-        if new < chi:
+        lowered = new < chi
+        if lowered:
             current, chi = r, new
+        # A restart cut off by its EVALUATION CAP (lmfit's `aborted` — a fact
+        # about the budget, not the optimiser's convergence verdict) never
+        # certifies: an unfinished descent can end a hair ABOVE its start, and
+        # that negative "improvement" passed the test (Codex A1 round 1). If
+        # it still lowered chi2 the next restart continues from there; if not,
+        # no progress is possible within the cap — not converged.
+        if getattr(r, "aborted", False):
+            if not lowered:
+                return current, False
+            continue
         if improvement < CERTIFY_FTOL:
             return current, True
     return current, False
diff --git a/templates/index.html b/templates/index.html
index 7a74e29..e44a732 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -16136,15 +16136,15 @@ function _fpProgressText(poll) {
 }
 
 const FP_POLL_INTERVAL_MS = 350;
-// Client-side watchdog: the actual analysis has its own server-side budget
-// (TOTAL_ANALYSIS_TIMEOUT_SEC, well under this), so this only fires if a
-// job's progress file stops updating entirely (e.g. a recycled gunicorn
-// worker process taking the background thread down with it) — the
-// indicator must NEVER spin forever even in that pathological case.
-const FP_POLL_WATCHDOG_SEC = 600;
-
+// Liveness, not total time (unit A1, 2026-09-29): the engine no longer stops
+// on a wall-clock budget, so a counted run under heavy load legitimately takes
+// longer than any fixed limit — a 600 s total cap turned such a run into
+// "Try again" (Codex A1 round 1). The server rewrites the job's heartbeat every
+// 2 s while its thread lives; a heartbeat older than FIT_HEARTBEAT_LOST_SEC
+// means the thread is gone (e.g. a recycled gunicorn worker), and the
+// indicator must never spin forever in that case. A record without a
+// heartbeat age yet (the very first poll) is waited on.
 async function _fpPollJob(jobId) {
-  const started = Date.now();
   while (true) {
     const resp = await fetch('/api/analyze/progress/' + encodeURIComponent(jobId));
     if (!resp.ok) {
@@ -16156,9 +16156,10 @@ async function _fpPollJob(jobId) {
     if (poll.status === 'error') {
       throw new Error(poll.error || 'Analysis failed.');
     }
-    if ((Date.now() - started) / 1000 > FP_POLL_WATCHDOG_SEC) {
-      throw new Error('This is taking unusually long — the analysis may ' +
-        'have been lost. Try again.');
+    const hb = poll.heartbeat_age_sec;
+    if (typeof hb === 'number' && hb > FIT_HEARTBEAT_LOST_SEC) {
+      throw new Error('The analysis stopped responding (its server process was ' +
+        'probably restarted). Try again.');
     }
     await new Promise(r => setTimeout(r, FP_POLL_INTERVAL_MS));
   }
diff --git a/tests/js/find_peaks_poll_liveness.test.js b/tests/js/find_peaks_poll_liveness.test.js
new file mode 100644
index 0000000..865b5c1
--- /dev/null
+++ b/tests/js/find_peaks_poll_liveness.test.js
@@ -0,0 +1,65 @@
+// Unit A1 (2026-09-29): Find Peaks' poll judges a job lost by LIVENESS (a
+// heartbeat older than FIT_HEARTBEAT_LOST_SEC), never by total time. The
+// engine no longer stops on a wall-clock budget, so a counted run under heavy
+// load can legitimately take longer than the old 600 s cap, which turned it
+// into "Try again" (Codex A1 round 1).
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
+function make(records) {
+  let i = 0, clock = 0;
+  const fetch = async () => {
+    const rec = records(i++);
+    return { ok: true, status: 200, json: async () => rec };
+  };
+  const document = { getElementById: () => ({ textContent: '' }) };
+  const FakeDate = { now: () => (clock += 1000) };          // one second passes per read
+  const src = [constLine('FP_POLL_INTERVAL_MS'), constLine('FIT_HEARTBEAT_LOST_SEC'),
+    extractFn('_fpFormatElapsed'), extractFn('_fpProgressText'), extractFn('_fpPollJob')].join('\n');
+  const api = new Function('fetch', 'document', 'setTimeout', 'Date', src + '\nreturn { _fpPollJob };')(
+    fetch, document, f => setImmediate(f), FakeDate);
+  return { api, polls: () => i };
+}
+
+test('a live job is waited on however long it runs (no total-time cap)', async () => {
+  const { api, polls } = make(k => k < 2000
+    ? { status: 'running', elapsed_sec: k, heartbeat_age_sec: 1.2, message: 'stabilizing' }
+    : { status: 'done', result: { success: true, winner: 'MG2' } });
+  const done = await api._fpPollJob('j');
+  assert.strictEqual(done.status, 'done');
+  assert.strictEqual(polls(), 2001, 'polled through 2000 s of a live job');
+});
+
+test('a stale heartbeat is a lost job, reported — never an endless spinner', async () => {
+  const { api } = make(k => ({ status: 'running', elapsed_sec: k, heartbeat_age_sec: k < 5 ? 1 : 31, message: 'x' }));
+  await assert.rejects(api._fpPollJob('j'), /stopped responding/);
+});
+
+test('the first poll without a heartbeat age yet is waited on', async () => {
+  const { api } = make(k => k === 0 ? { status: 'running', heartbeat_age_sec: null }
+    : { status: 'done', result: {} });
+  assert.strictEqual((await api._fpPollJob('j')).status, 'done');
+});
+
+test('no total-duration watchdog remains in the poll loop', () => {
+  const src = extractFn('_fpPollJob');
+  assert.ok(!/Date\.now\(\)/.test(src) && !/WATCHDOG/.test(src), src);
+  assert.ok(!/FP_POLL_WATCHDOG_SEC/.test(html));
+});
diff --git a/tests/test_api_analyze_progress.py b/tests/test_api_analyze_progress.py
index 5028f26..24a794f 100644
--- a/tests/test_api_analyze_progress.py
+++ b/tests/test_api_analyze_progress.py
@@ -184,3 +184,31 @@ def test_progress_invalid_job_id_format_400(client):
     resp2 = client.get("/api/analyze/progress/not-a-uuid-at-all")
     assert resp2.status_code == 400
 
+
+
+def test_a_running_job_keeps_a_fresh_heartbeat(client, monkeypatch):
+    """Unit A1 (2026-09-29): the engine no longer stops on a wall-clock budget,
+    so the page judges a job lost by LIVENESS, not total time. The record's
+    heartbeat is rewritten every 2 s while the worker thread lives — also
+    between the engine's progress events — and the poll reports its age."""
+    import app as app_module
+    real = app_module._run_analyze_method
+
+    def slow(ctx, progress_cb=None):
+        time.sleep(5.0)                          # a long stretch with no progress event
+        return real(ctx, progress_cb=progress_cb)
+    monkeypatch.setattr(app_module, "_run_analyze_method", slow)
+    sid = _upload_doublet(client)
+    job_id = client.post("/api/analyze/start", json=_BODY(sid)).get_json()["job_id"]
+    ages = []
+    t_end = time.time() + 4.5
+    while time.time() < t_end:
+        rec = client.get(f"/api/analyze/progress/{job_id}").get_json()
+        assert rec["status"] == "running"
+        ages.append(rec["heartbeat_age_sec"])
+        time.sleep(0.25)
+    assert all(isinstance(a, (int, float)) for a in ages), ages
+    assert max(ages) <= 3.0, ages                # 2 s heartbeat, never stale while the thread lives
+    final = _poll_until_terminal(client, job_id, timeout_sec=60.0)
+    assert final["status"] == "done"
+    assert final["result"]["success"] in (True, False)

exec
/bin/zsh -lc "sed -n '790,1120p' autofit/engine.py; sed -n '1320,1485p' autofit/engine.py; cat tests/autofit/test_fit_certificate.py; sed -n '395,565p' tests/autofit/test_preseed_dominants.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
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


# ── Convergence certificate (unit A1, 2026-09-29) ─────────────────────────────
# A fit has reached a minimum when a fresh descent from its end point cannot
# improve chi2 by more than the descent's OWN stopping tolerance. The descent
# is Trust-Region (scipy least_squares, native bounds): a Levenberg-Marquardt
# restart from a stall point reproduces the stall (MINPACK's xtol test fires in
# ~30 evaluations — the false convergence this replaces). Restarts are repeated
# from each improved point; a FIXED number of them (a count, not a time); out
# of restarts, or a non-finite restart, is "not converged". No new constant:
# the tolerance is scipy's own least_squares ftol default, read from its
# signature, and the improvement is relative (dimensionless, scale-free).
import inspect as _inspect
import scipy.optimize as _scipy_optimize
CERTIFY_FTOL = float(_inspect.signature(_scipy_optimize.least_squares).parameters["ftol"].default)
# A COUNT, set from measurement (unit A1, 8 committed C 1s scans × 4 gate
# candidates, primaries + all refits = 208 fits): restarts needed to certify —
# 1: 10, 2: 173, 3: 14, 4: 5, then one fit each at 5, 6, 8, 9, 11 and 21 (flat
# valleys: each Trust-Region run stops on its own ftol while a whole restart
# still gains more than that). 5 left four real minima uncertified (8-JT
# Scan_5's MG2 and MG3 primaries, so MG lost to AG2 at chi2r 42.5).
CERTIFY_MAX_RESTARTS = 50


def _certify_minimum(composite, y_sub, result, x, weights, max_nfev):
    """Return (the lowest-chi2 point reached, certified). ``max_nfev`` caps
    each restart like the fit it certifies."""
    current = result
    chi = float(result.chisqr) if result.chisqr is not None else float("nan")
    if not np.isfinite(chi):
        return current, False
    for _ in range(CERTIFY_MAX_RESTARTS):
        try:
            r = composite.fit(y_sub, current.params.copy(), x=x, weights=weights,
                              method="least_squares", nan_policy="omit",
                              max_nfev=max_nfev)
        except Exception as exc:
            log.debug("certificate restart raised: %s", exc)
            return current, False
        new = float(r.chisqr) if r.chisqr is not None else float("nan")
        if not np.isfinite(new):
            return current, False
        improvement = (chi - new) / chi if chi > 0 else 0.0
        lowered = new < chi
        if lowered:
            current, chi = r, new
        # A restart cut off by its EVALUATION CAP (lmfit's `aborted` — a fact
        # about the budget, not the optimiser's convergence verdict) never
        # certifies: an unfinished descent can end a hair ABOVE its start, and
        # that negative "improvement" passed the test (Codex A1 round 1). If
        # it still lowered chi2 the next restart continues from there; if not,
        # no progress is possible within the cap — not converged.
        if getattr(r, "aborted", False):
            if not lowered:
                return current, False
            continue
        if improvement < CERTIFY_FTOL:
            return current, True
    return current, False


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
                _clip(op, op.value + rng.normal(0.0, position_jitter_eV))

        fp = params.get(f"{prefix}{_width_param(slot.line_shape)}")
        if fp is not None and fp.expr is None and fp.vary:
            _clip(fp, fp.value * max(1.0 + rng.normal(0.0, fwhm_jitter_frac), 0.1))

        ap = params.get(f"{prefix}amplitude")
        if ap is not None and ap.expr is None:
            _clip(ap, ap.value * max(1.0 + rng.normal(0.0, amplitude_jitter_frac), 0.1))
    return params


# ─────────────────────────────────────────────────────────────────────────────
# Component ↔ slot matching
# ─────────────────────────────────────────────────────────────────────────────

def _is_asymmetric_component(comp: FittedComponent) -> bool:
    sp = comp.shape_params
    if comp.line_shape in (LineShape.DS, LineShape.DS_G):
        return float(sp.get("alpha", 0.0)) > ALPHA_SYMMETRY_THRESHOLD
    if comp.line_shape is LineShape.ASYM_GL:
        return float(sp.get("asymmetry", 0.0)) > ALPHA_SYMMETRY_THRESHOLD
    if comp.line_shape is LineShape.LACX:
        return abs(float(sp.get("alpha", 1.0)) - float(sp.get("beta", 1.0))) \
            > LACX_EXPONENT_ASYMMETRY
    return False


def _effective_be_window(
    slot: ComponentSlot, components: list[FittedComponent],
    bound_override: Optional[tuple[float, float]] = None,
) -> tuple[float, float]:
    """``bound_override`` (fit_full_window, unit 1 2026-07-13): the SAME
    widened bound the fit itself was built with
    (``_full_window_bound_overrides``) — a primary slot's fitted position
    identity-matching must agree with the bound it was actually allowed
    to search, or a component the widened fit correctly placed outside
    its ORIGINAL literature window becomes an orphan here (Codex-caught:
    tanks stability/persistence, silently rejecting the very component
    this option exists to rescue). Only applies to a primary slot
    (``linked_to is None`` — a linked slot's effective window is always
    the offset-derived one below, entirely unaffected by this option)."""
    if slot.linked_to is None or slot.linked_offset_range is None:
        return bound_override if bound_override is not None else slot.be_window
    parent = next((c for c in components if c.slot_role == slot.linked_to), None)
    if parent is None:
        return slot.be_window
    lo, hi = slot.linked_offset_range
    return (parent.position + lo, parent.position + hi)


def match_components_to_slots(
    components: list[FittedComponent],
    model: CandidateModel,
    noise_floor: float,
    bound_overrides: Optional[dict[str, tuple[float, float]]] = None,
) -> dict[str, Optional[FittedComponent]]:
    """Assign fitted peaks to grammar slots (role + effective window + width).

    ``bound_overrides`` (fit_full_window) — see ``_effective_be_window``.
    """
    slot_map: dict[str, Optional[FittedComponent]] = {s.role: None for s in model.slots}
    orphans: list[FittedComponent] = []
    asym_shapes = {LineShape.ASYM_GL, LineShape.DS, LineShape.DS_G, LineShape.LACX}

    def _accepts(slot: ComponentSlot, comp: FittedComponent) -> bool:
        lo, hi = _effective_be_window(slot, components,
                                      (bound_overrides or {}).get(slot.role))
        return (lo <= comp.position <= hi
                and slot.fwhm_range[0] <= comp.fwhm <= slot.fwhm_range[1]
                and comp.amplitude > noise_floor)

    def _window_center(slot: ComponentSlot) -> float:
        # NEVER the widened bound (Codex-caught, round 2): this is a
        # TIE-BREAK reference point ("how close is this component to
        # where this slot expects its peak"), not an acceptance test —
        # widening it would drag the reference point far from the
        # slot's true expected position (e.g. a curated slot's own
        # narrow window widened to a whole ROI), making a neighboring
        # slot's UNWIDENED, much-closer center win the tie-break even
        # when the component sits well inside THIS slot's own original
        # window. Acceptance (_accepts, above) is the only place the
        # widened bound belongs.
        lo, hi = _effective_be_window(slot, components)
        return 0.5 * (lo + hi)

    for comp in components:
        candidate_slots = [s for s in model.slots if _accepts(s, comp)]
        if not candidate_slots:
            orphans.append(FittedComponent(
                slot_role="unmatched", position=comp.position, fwhm=comp.fwhm,
                amplitude=comp.amplitude, shape_params=comp.shape_params,
                line_shape=comp.line_shape,
            ))
            continue

        shapes = {s.line_shape for s in candidate_slots}
        if len(shapes) > 1:
            if _is_asymmetric_component(comp):
                preferred = [s for s in candidate_slots if s.line_shape in asym_shapes]
            else:
                preferred = [s for s in candidate_slots if s.line_shape not in asym_shapes]
            if preferred:
                candidate_slots = preferred

        best_slot = min(candidate_slots, key=lambda s: abs(comp.position - _window_center(s)))
        incumbent = slot_map[best_slot.role]
        claimed = FittedComponent(
            slot_role=best_slot.role, position=comp.position, fwhm=comp.fwhm,
            amplitude=comp.amplitude, shape_params=comp.shape_params,
            line_shape=comp.line_shape,
        )
        if incumbent is None:
            slot_map[best_slot.role] = claimed
        else:
            wc = _window_center(best_slot)
            if abs(comp.position - wc) < abs(incumbent.position - wc):
                orphans.append(incumbent)
                slot_map[best_slot.role] = claimed
            else:
                orphans.append(comp)

    slot_map["__orphans__"] = orphans  # type: ignore[assignment]
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
    x: np.ndarray,
    y: np.ndarray,
    y_fit: np.ndarray,
    noise_floor: float,
    diagnostic_windows: dict[str, tuple[float, float]],
    window_flag_ratio: float = 2.0,
) -> ResidualDiagnostics:
    r = y - y_fit
    sigma = np.sqrt(np.maximum(y, noise_floor))
    r_std = r / sigma
    num = np.sum(r_std[:-1] * r_std[1:])
    den = np.sum(r_std ** 2)
    rho_1 = float(num / den) if den > 0 else 0.0
    thr = 2.0 / np.sqrt(len(r_std)) if len(r_std) > 0 else float("inf")

    energies: dict[str, float] = {}
    for label, (lo, hi) in diagnostic_windows.items():
        mask = (x >= lo) & (x <= hi)
        energies[label] = float(np.mean(r_std[mask] ** 2)) if mask.sum() > 0 else 0.0
    gmean = float(np.mean(r_std ** 2)) if len(r_std) > 0 else 0.0
    flagged = [lbl for lbl, e in energies.items()
               if gmean > 0 and e > window_flag_ratio * gmean]
    return ResidualDiagnostics(
        autocorrelation_lag1=rho_1,
        autocorr_flag=abs(rho_1) > thr,
        window_energies=energies,
        flagged_windows=flagged,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Reports, BIC*, ranking
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PlausibilityFlags:
    boundary_hits: list[str] = field(default_factory=list)
    unphysical_widths: list[str] = field(default_factory=list)
    orphan_peaks: bool = False


@dataclass
class ProposedPeakReport:
    role: str
    detection_windows: list[str]
    detection_energy: float
    detection_ratio: float
    proposed_center_init: float
    proposed_fwhm_init: float
    proposed_amplitude_init: float
    fitted_center: Optional[float] = None
    fitted_fwhm: Optional[float] = None
    fitted_amplitude: Optional[float] = None
    persistence: Optional[float] = None
    delta_bic_vs_base: Optional[float] = None
    boundary_hits: list[str] = field(default_factory=list)
    accepted: bool = False
    rejection_reason: Optional[str] = None
    near_roi_endpoint: bool = False
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


def test_a_restart_cut_off_by_its_evaluation_cap_never_certifies():
    """Codex A1 round 1 (MAJOR): with the restart capped, an unfinished descent
    can end a hair ABOVE its start (chi2 959072.771 vs 959072.740); the
    negative improvement passed '< ftol' and a point 3000x above the minimum
    was certified. A capped restart never certifies."""
    x, y, w, model = _two_peak()
    comp = eng._build_composite_model(model)
    good = eng.fit_candidate(x, y, w, model)
    far = good.lmfit_result.params.copy()
    far["s_a_center"].set(value=284.05); far["s_b_amplitude"].set(value=50.0); far["s_a_fwhm"].set(value=2.3)
    out = eng.fit_candidate(x, y, w, model, initial_params=far, max_nfev=2)   # the fit AND its restarts capped
    assert not out.converged, out.weighted_chi_sq
    assert out.weighted_chi_sq > 100 * good.weighted_chi_sq, "really far from the minimum"
    def slot(role):
        return ComponentSlot(role=role, region="unassigned", phase_id="unassigned",
                             be_window=(199.0, 201.0), line_shape=LineShape.PSEUDO_VOIGT,
                             fwhm_range=(0.5, 3.0))
    # a model with proposed_peak_1 present but NOT proposed_peak_0 (the
    # reject-first-accept-later state) — count would say 1, max+1 says 2
    m = CandidateModel(name="X", background=eng.BackgroundType.LINEAR,
                       slots=(slot("main_a"), slot("proposed_peak_1")))
    assert eng._next_proposal_index(m) == 2
    # and after augmenting, all slot roles stay unique (no collision)
    spec = eng.ProposalSpec(
        role=f"proposed_peak_{eng._next_proposal_index(m)}",
        detection_windows=[], detection_energy=1.0, detection_ratio=9.0,
        center_init=200.0, fwhm_init=1.0, amplitude_init=5000.0,
        line_shape=eng.PROPOSED_PEAK_SHAPE)
    aug = eng._augmented_candidate(m, spec)
    aug_roles = [s.role for s in aug.slots]
    assert len(aug_roles) == len(set(aug_roles)), f"role collision: {aug_roles}"
    assert "proposed_peak_2" in aug_roles
    # no-proposal model → index 0
    m0 = CandidateModel(name="Y", background=eng.BackgroundType.LINEAR,
                        slots=(slot("main_a"),))
    assert eng._next_proposal_index(m0) == 0


def test_no_wall_clock_can_change_the_answer(monkeypatch):
    """Unit A1 (2026-09-29): the sweep, screen, stability and proposal
    budgets were wall-clock and made the answer depend on server load; they
    are gone. A clock that jumps a million seconds on every read must leave
    the result IDENTICAL."""
    x = _grid()
    truth = [{"center": 196.5, "fwhm": 1.2, "height": 9000.0},
             {"center": 201.5, "fwhm": 1.2, "height": 2500.0}]
    sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
    y = _noisy(sig + _linear_bg(x), 71)
    grammar = _grammar([_cand("single_main", [_slot("main_a", (195.5, 197.5))])])

    def run():
        res = get_method("ic_model_comparison").run(x, y, grammar=grammar, options={**IC_OPTS, "enable_preseed": False})
        return res.diagnostics, res.peaks, res.analysis, res.confidence

    normal = run()
    ticks = {"t": 0.0}

    def jumpy():
        ticks["t"] += 1.0e6
        return ticks["t"]
    monkeypatch.setattr(eng.time, "perf_counter", jumpy)
    assert run() == normal


# ── F3: two-phase sweep ────────────────────────────────────────────────────

def _many_candidate_grammar(x, y):
    """SCREEN_TOP_K+2 candidates: a ladder of window variants, several of
    which cannot express the data (wrong windows)."""
    good = [
        _cand("G1", [_slot("main_a", (195.5, 197.5))]),
        _cand("G2", [_slot("main_a", (195.5, 197.5)),
                     _slot("comp_b", (198.5, 200.5))]),
    ]
    bad = [
        _cand(f"B{i}", [_slot("main_a", (200.5 + i * 0.2, 202.5 + i * 0.2))])
        for i in range(eng.SCREEN_TOP_K)
    ]
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


def test_no_wall_clock_can_change_the_screen_or_the_refit_counts(monkeypatch):
    """Unit A1, Codex round 1 (MINOR): the clock test above never reached the
    screen (one candidate). With more than SCREEN_TOP_K candidates and a clock
    that jumps a million seconds per read, EVERY candidate is still screened,
    every deep candidate runs exactly n_refits refits, and the result is
    identical to the one under a normal clock."""
    x, y, _ = _covered_spectrum(seed=13)
    grammar = _many_candidate_grammar(x, y)
    assert len(grammar.candidates) > eng.SCREEN_TOP_K
    from autofit.methods.base import poisson_like_weights
    w = poisson_like_weights(y)
    attempted = []
    real_stab = eng.run_stability_analysis

    def stab(*a, **k):
        st = real_stab(*a, **k)
        attempted.append((st.n_attempted, k.get("n_refits")))
        return st
    monkeypatch.setattr(eng, "run_stability_analysis", stab)

    def run():
        attempted.clear()
        r = eng.compare_models(x, y, w, grammar, n_refits=3, rng_seed=0, enable_proposal_pass=False, enable_preseed=False)
        return ([row["name"] for row in r.screen], [(row["converged"], row["selected"]) for row in r.screen],
                [rep.model.name for rep in r.reports], [rep.bic_adjusted for rep in r.reports],
                r.analysis_truncated, list(attempted))

    normal = run()
    ticks = {"t": 0.0}

    def jumpy():
        ticks["t"] += 1.0e6
        return ticks["t"]
    monkeypatch.setattr(eng.time, "perf_counter", jumpy)
    jumped = run()
    assert jumped == normal
    names, _, reports, _, truncated, att = jumped
    assert len(names) == len(grammar.candidates), "every candidate screened"
    assert not truncated
    assert att and all(n == want == 3 for n, want in att), att


def test_small_candidate_set_takes_classic_path():
    """≤ SCREEN_TOP_K candidates → no screen phase (screen is None) — every
    existing gate/battery path is unchanged."""
    x, y, grammar = _covered_spectrum(seed=13)
    case_like = type("C", (), {"x": x, "y": y, "grammar": grammar})
    res = _ic(case_like)
    assert res.analysis["screen"] is None

exec
/bin/zsh -lc "sed -n '1120,1290p' app.py; rg -n '_write_job_progress|_sweep_expired_jobs|JOB_TTL|heartbeat|_fpPollJob|WATCHDOG|timeout' app.py | tail -70; sed -n '16125,16335p' templates/index.html; cat tests/test_api_analyze_progress.py; ls /Users/skyefortier/xps-app/venv/bin/python*; rg -n 'delegat|review|test|rule' CLAUDE.md | tail -35" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:

        Returns the full MethodResult: candidate peaks with the per-peak
        confidence vector, the analysis namespace (ambiguity flags, ranked
        alternatives, constants provenance), diagnostics, and a review-gate
        stub — results are candidates + honesty flags, not ground truth;
        a NAMED human review is required before export (spec §8).

        For a long analysis (60-240s), POST /api/analyze/start + poll
        GET /api/analyze/progress/<job_id> instead — same validation, same
        result shape, plus live sweep progress (Find Peaks UI, 2026-07-11).
        This synchronous route is UNCHANGED: both now share
        ``_validate_analyze_request``/``_run_analyze_method``/
        ``_build_analyze_payload`` under the hood (a pure extract-method
        refactor — tests/test_api_analyze.py pins the contract identical).
        """
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return _err("request body must be a JSON object")
        try:
            ctx = _validate_analyze_request(body, app.config["UPLOAD_FOLDER"])
            res = _run_analyze_method(ctx)
        except _AnalyzeError as exc:
            return _err(str(exc), exc.status)
        payload = _build_analyze_payload(ctx, res)
        return jsonify(_json_sanitize(payload))

    @app.post("/api/analyze/start")
    @_require_json
    def analyze_start():
        """
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
        # Unit A1 (2026-09-29): the record carries a HEARTBEAT, rewritten every
        # FIT_JOB_HEARTBEAT_SEC while the worker thread lives (fit jobs' pattern,
        # unit 2). The engine no longer stops on a wall-clock budget, so a long
        # counted run under load is normal; the page judges the job lost only
        # when the heartbeat stops (a recycled worker), never by total time.
        lock = threading.Lock()
        finished = threading.Event()
        rec = {"status": "running", "phase": "starting",
               "candidate_index": None, "candidate_total": None,
               "candidate_name": None, "elapsed_sec": 0.0,
               "message": "starting analysis…", "heartbeat": start_time}
        _write_job_progress(job_id, upload_folder, rec)

        def _publish(update: dict) -> None:
            with lock:
                rec.update(update)
                rec["elapsed_sec"] = round(time.time() - start_time, 1)
                rec["heartbeat"] = time.time()
                _write_job_progress(job_id, upload_folder, rec)

        def _heartbeat() -> None:
            while not finished.wait(FIT_JOB_HEARTBEAT_SEC):
                with lock:
                    if rec["status"] != "running":
                        return
                    rec["heartbeat"] = time.time()
                    rec["elapsed_sec"] = round(time.time() - start_time, 1)
                    _write_job_progress(job_id, upload_folder, rec)

        def _progress_cb(evt: dict) -> None:
            _publish({
                "status": "running",
                "phase": evt.get("phase"),
                "candidate_index": evt.get("candidate_index"),
                "candidate_total": evt.get("candidate_total"),
                "candidate_name": evt.get("candidate_name"),
                "message": _analyze_progress_message(evt),
            })

        def _worker() -> None:
            try:
                res = _run_analyze_method(ctx, progress_cb=_progress_cb)
                payload = _build_analyze_payload(ctx, res)
                final = {"status": "done", "phase": "done", "message": "done", "result": payload}
            except _AnalyzeError as exc:
                final = {"status": "error", "phase": "done", "message": "failed",
                         "error": str(exc), "http_status": exc.status}
            except Exception as exc:      # belt-and-suspenders: the
                # indicator must ALWAYS clear, even on a bug we didn't
                # anticipate — never let a job hang the poll forever.
                logging.getLogger(__name__).exception(
                    "analyze job %s crashed", job_id)
                final = {"status": "error", "phase": "done", "message": "failed",
                         "error": f"internal error: {exc}", "http_status": 500}
            finished.set()
            _publish(final)

        threading.Thread(target=_heartbeat, daemon=True, name=f"fp-hb-{job_id[:8]}").start()
        try:
            threading.Thread(target=_worker, daemon=True, name=f"fp-{job_id[:8]}").start()
        except Exception:
            finished.set()                # no heartbeat for a job that never ran
            raise
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
        hb = data.get("heartbeat")
        data["heartbeat_age_sec"] = round(time.time() - hb, 1) if isinstance(hb, (int, float)) else None
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
295:_ANALYZE_JOB_TTL_SEC = 3600  # job progress files are short-lived scratch
517:def _write_job_progress(job_id: str, upload_folder: str, data: dict) -> None:
533:def _sweep_expired_jobs(upload_folder: str) -> None:
538:    cutoff = time.time() - _ANALYZE_JOB_TTL_SEC
564:# rest wait "queued", heartbeating, cancellable) and admits at most
593:    """Atomic like _write_job_progress, but WITHOUT sanitising: a result's
617:    hb = data.get("heartbeat")
618:    data["heartbeat_age_sec"] = round(time.time() - hb, 1) if isinstance(hb, (int, float)) else None
625:    cutoff = time.time() - _ANALYZE_JOB_TTL_SEC
646:    """Start the fit thread and its heartbeat thread. ``run(fit_args, cancel)``
650:    rec = {"status": "queued", "elapsed_sec": 0.0, "heartbeat": started}
665:    def heartbeat() -> None:
670:                rec["heartbeat"] = time.time()
683:                got = _FIT_JOB_RUN_SLOTS.acquire(timeout=0.5)
688:                        rec["heartbeat"] = time.time()
689:                        _fit_job_write(job_id, upload_folder, rec)   # visible at once, not at the next heartbeat
700:            rec["heartbeat"] = time.time()
715:    # The heartbeat thread starts FIRST: if either thread fails to start this
719:    threading.Thread(target=heartbeat, daemon=True, name=f"fit-hb-{job_id[:8]}").start()
723:        finished.set()                # stop the heartbeat of a job that never ran
1184:        _sweep_expired_jobs(upload_folder)
1190:        # when the heartbeat stops (a recycled worker), never by total time.
1196:               "message": "starting analysis…", "heartbeat": start_time}
1197:        _write_job_progress(job_id, upload_folder, rec)
1203:                rec["heartbeat"] = time.time()
1204:                _write_job_progress(job_id, upload_folder, rec)
1206:        def _heartbeat() -> None:
1211:                    rec["heartbeat"] = time.time()
1213:                    _write_job_progress(job_id, upload_folder, rec)
1243:        threading.Thread(target=_heartbeat, daemon=True, name=f"fp-hb-{job_id[:8]}").start()
1247:            finished.set()                # no heartbeat for a job that never ran
1275:        hb = data.get("heartbeat")
1276:        data["heartbeat_age_sec"] = round(time.time() - hb, 1) if isinstance(hb, (int, float)) else None
1286:    # heartbeat (epoch s, rewritten every 2 s while the fit thread lives),
1304:            _sweep_expired_jobs(upload_folder)
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
// Liveness, not total time (unit A1, 2026-09-29): the engine no longer stops
// on a wall-clock budget, so a counted run under heavy load legitimately takes
// longer than any fixed limit — a 600 s total cap turned such a run into
// "Try again" (Codex A1 round 1). The server rewrites the job's heartbeat every
// 2 s while its thread lives; a heartbeat older than FIT_HEARTBEAT_LOST_SEC
// means the thread is gone (e.g. a recycled gunicorn worker), and the
// indicator must never spin forever in that case. A record without a
// heartbeat age yet (the very first poll) is waited on.
async function _fpPollJob(jobId) {
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
    const hb = poll.heartbeat_age_sec;
    if (typeof hb === 'number' && hb > FIT_HEARTBEAT_LOST_SEC) {
      throw new Error('The analysis stopped responding (its server process was ' +
        'probably restarted). Try again.');
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
"""
POST /api/analyze/start + GET /api/analyze/progress/<job_id> — the
async job path behind the Find Peaks progress indicator (2026-07-11,
unit 1).  STRICTLY ADDITIVE: /api/analyze itself is a thin wrapper over
the SAME shared validation + method-execution helpers now, so its
existing contract (tests/test_api_analyze.py) stays provably unchanged.

Design (documented here, mirrors PROGRESS.md): gunicorn runs with the
default SYNC worker class (see ~/Library/LaunchAgents' plist: `--workers
4`, no `-k gthread/gevent`), so an SSE connection held open for the
whole analysis would tie up an entire worker for 60-240s — exactly what
the existing synchronous /api/analyze already risks, doubled. Instead:
POST /start does the SAME fast synchronous validation /api/analyze does
(instant 400s, unchanged), then spawns a background THREAD (not a
worker-blocking connection) that runs the method and writes progress to
a small JSON file under the upload folder (per-worker in-memory state
would be invisible to a poll landing on a different gunicorn worker
process — the file is the cross-process-safe channel, same pattern as
session .npz files). GET /progress/<job_id> is a cheap poll of that
file. The indicator clears via the SAME poll on both "done" and "error"
statuses — never spins forever.
"""

import io
import time

import numpy as np
import pytest

from app import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app(upload_folder=str(tmp_path))
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _upload_doublet(client, seed=7):
    rng = np.random.default_rng(seed)
    x = np.arange(192.0, 205.0, 0.05)

    def pv(h, c, w, eta=0.3):
        g = np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)
        lo = (w / 2) ** 2 / ((x - c) ** 2 + (w / 2) ** 2)
        return h * ((1 - eta) * g + eta * lo)

    y = rng.poisson(300.0 + pv(9000.0, 197.9, 1.65)
                    + pv(4950.0, 199.5, 1.65)).astype(float)
    csv = "\n".join(f"{a:.3f},{b:.1f}" for a, b in zip(x, y))
    resp = client.post("/api/upload", data={
        "file": (io.BytesIO(csv.encode()), "doublet.csv")})
    assert resp.status_code == 200, resp.get_json()
    return resp.get_json()["session_id"]


_BODY = lambda sid: {                                          # noqa: E731
    "session_id": sid, "material_class": "insulator",
    "regions": ["Cl 2p"], "method": "ic_model_comparison",
    "roi": {"be_min": 192.0, "be_max": 205.0},
    "options": {"n_refits": 2, "enable_proposal_pass": False},
}


def _poll_until_terminal(client, job_id, timeout_sec=30.0):
    deadline = time.time() + timeout_sec
    last = None
    while time.time() < deadline:
        resp = client.get(f"/api/analyze/progress/{job_id}")
        assert resp.status_code == 200, resp.get_json()
        last = resp.get_json()
        if last["status"] in ("done", "error"):
            return last
        time.sleep(0.05)
    raise AssertionError(f"job {job_id} never reached a terminal state: {last}")


def test_start_returns_job_id_and_202(client):
    sid = _upload_doublet(client)
    resp = client.post("/api/analyze/start", json=_BODY(sid))
    assert resp.status_code == 202, resp.get_json()
    body = resp.get_json()
    assert "job_id" in body
    import uuid
    uuid.UUID(body["job_id"])  # must parse as a real UUID


def test_progress_reaches_done_with_the_same_result_as_sync(client):
    """The async path must produce the EXACT SAME result payload the
    synchronous /api/analyze produces for the identical (seeded,
    deterministic) request — proving the refactor changed nothing about
    the analysis itself."""
    sid = _upload_doublet(client)
    sync_resp = client.post("/api/analyze", json=_BODY(sid))
    assert sync_resp.status_code == 200
    sync_body = sync_resp.get_json()

    start_resp = client.post("/api/analyze/start", json=_BODY(sid))
    assert start_resp.status_code == 202
    job_id = start_resp.get_json()["job_id"]
    final = _poll_until_terminal(client, job_id)
    assert final["status"] == "done"
    assert final["result"] == sync_body


def test_progress_clears_on_success_never_spins_forever(client):
    sid = _upload_doublet(client)
    start_resp = client.post("/api/analyze/start", json=_BODY(sid))
    job_id = start_resp.get_json()["job_id"]
    final = _poll_until_terminal(client, job_id)
    assert final["status"] == "done"
    assert final["phase"] == "done"
    assert isinstance(final["elapsed_sec"], (int, float))
    assert final["elapsed_sec"] >= 0


def test_progress_shows_real_candidate_fields_while_running(client, monkeypatch):
    """Force the two-phase screen->stabilize path so the sweep takes long
    enough to observe a RUNNING poll with real phase/candidate fields —
    never a fake animation."""
    import autofit.engine as eng
    monkeypatch.setattr(eng, "SCREEN_TOP_K", 1)

    sid = _upload_doublet(client)
    start_resp = client.post("/api/analyze/start", json=_BODY(sid))
    job_id = start_resp.get_json()["job_id"]

    saw_running_with_fields = False
    deadline = time.time() + 30.0
    while time.time() < deadline:
        poll = client.get(f"/api/analyze/progress/{job_id}").get_json()
        if poll["status"] == "running" and poll.get("candidate_name"):
            assert poll["phase"] in ("starting", "screening", "stabilizing")
            if poll["phase"] in ("screening", "stabilizing"):
                assert poll["candidate_index"] >= 1
                assert poll["candidate_total"] >= poll["candidate_index"]
                saw_running_with_fields = True
        if poll["status"] in ("done", "error"):
            break
        time.sleep(0.02)
    assert saw_running_with_fields, "never observed a real in-flight progress event"


def test_progress_clears_on_error_never_spins_forever(client):
    """A malformed OPTION VALUE (discovered inside the method's run(),
    same class of error test_analyze_malformed_option_values_are_400s
    pins synchronously) must surface as a terminal 'error' status via
    the SAME poll channel — the indicator must clear, not spin."""
    sid = _upload_doublet(client)
    body = _BODY(sid)
    body["options"] = {"n_refits": []}     # TypeError inside run()
    start_resp = client.post("/api/analyze/start", json=body)
    assert start_resp.status_code == 202     # validation passed; run() will fail
    job_id = start_resp.get_json()["job_id"]
    final = _poll_until_terminal(client, job_id)
    assert final["status"] == "error"
    assert final["phase"] == "done"
    assert "invalid option" in final["error"].lower()


def test_start_validation_errors_are_still_synchronous_400s(client):
    """Cheap, request-shape validation (session/region/roi/material_class)
    stays SYNCHRONOUS on /start too — identical to /api/analyze — so a
    malformed request never even reaches the spinner."""
    resp = client.post("/api/analyze/start", json={
        "session_id": "not-a-uuid", "material_class": "insulator",
        "regions": ["Cl 2p"], "method": "ic_model_comparison"})
    assert resp.status_code == 400
    assert "job_id" not in (resp.get_json() or {})


def test_progress_unknown_job_id_404(client):
    import uuid
    resp = client.get(f"/api/analyze/progress/{uuid.uuid4()}")
    assert resp.status_code == 404


def test_progress_invalid_job_id_format_400(client):
    """Path-traversal guard, same convention as _validate_session_id."""
    resp = client.get("/api/analyze/progress/../../etc/passwd")
    assert resp.status_code in (400, 404)  # Flask routing may itself 404
    resp2 = client.get("/api/analyze/progress/not-a-uuid-at-all")
    assert resp2.status_code == 400



def test_a_running_job_keeps_a_fresh_heartbeat(client, monkeypatch):
    """Unit A1 (2026-09-29): the engine no longer stops on a wall-clock budget,
    so the page judges a job lost by LIVENESS, not total time. The record's
    heartbeat is rewritten every 2 s while the worker thread lives — also
    between the engine's progress events — and the poll reports its age."""
    import app as app_module
    real = app_module._run_analyze_method

    def slow(ctx, progress_cb=None):
        time.sleep(5.0)                          # a long stretch with no progress event
        return real(ctx, progress_cb=progress_cb)
    monkeypatch.setattr(app_module, "_run_analyze_method", slow)
    sid = _upload_doublet(client)
    job_id = client.post("/api/analyze/start", json=_BODY(sid)).get_json()["job_id"]
    ages = []
    t_end = time.time() + 4.5
    while time.time() < t_end:
        rec = client.get(f"/api/analyze/progress/{job_id}").get_json()
        assert rec["status"] == "running"
        ages.append(rec["heartbeat_age_sec"])
        time.sleep(0.25)
    assert all(isinstance(a, (int, float)) for a in ages), ages
    assert max(ages) <= 3.0, ages                # 2 s heartbeat, never stale while the thread lives
    final = _poll_until_terminal(client, job_id, timeout_sec=60.0)
    assert final["status"] == "done"
    assert final["result"]["success"] in (True, False)
/Users/skyefortier/xps-app/venv/bin/python
/Users/skyefortier/xps-app/venv/bin/python3
/Users/skyefortier/xps-app/venv/bin/python3.12
129:shape by shape); section (D) of `tests/js/lineshape_parity.test.js` sweeps
173:anchor (answer: a scale-free F test), then two tolerances on that F test
181:`autofit_required_*`. The DE unit is the same rule seen from the other
187:When two places read the same input — the page and the server, a preview
191:a free η to the server (A03); the ROI, the preview background and the fitted
207:`_readFitReply` rules. So no request meets the public ~100 s ceiling (the five
214:either way). Page: the ownership rules run INSIDE the poll loop (a switched
226:for scripts, tests and the Python twins. Plan:
301:were actually being fit against, due to a pre-existing preview/backend
444:engine: lmfit divides by max(1, nfree) and the F tests clamp dof to 1, so such
467:(in review each such no-op edit moved an area fraction by 15–45 pp
476:makes (observed through Levenberg-Marquardt) are pinned by tests; numpy does not promise the same `default_rng` stream across
500:(`tests/test_fit_reproducibility.py` docstring). Do not patch scipy
512:second thing (a reviewer tried a deterministic perturbation base: identical
545:the largest move named, amber > 0.5 eV, red > 1 eV) with Preview (the
546:history-preview overlay, on a copy) and "Use this solution": explicit, one
564:the comparison no longer applies, nothing can be previewed or applied, an
565:open alternative preview is dropped (`_dropStaleAltPreview`), and
682:uncertainty panel (one rule-0 warning, before the per-parameter alarms and
698:not detected (a refit without the component is the test; step (c) does it
701:**Acceptance rule for fit outcomes (unit A0, 2026-09-15):** a fit OUTCOME
736:uncertainty rule; CSV/XLSX a WARNING instead of the statistic, σ cells
767:| `tougaard` | Single-pass universal cross-section K(T) = B·T/(C+T²)², B = 2866 eV², C = 1643 eV² (Tougaard, *Surf. Interface Anal.* **1988**, 11, 453; kernel max at √(C/3) ≈ 23.4 eV). Order-robust (either BE direction); amplitude anchored to the data at the high-BE edge. JS twin `tougaardBackground` must stay in numerical agreement (pinned by `tests/js/tougaard_twin.test.js`). |
772:fits against) equal fitting.py's on the tested cases — shirley, smart and
774:rounding, linear on uniform grids — within the test's 1e-6 of the intensity
777:(`tests/js/background_parity.test.js`, unit 4 2026-09-27). The Shirley and
839:`tests/js/fixtures/autofit_anchor.json`. SCOPE: it answers "do the data
843:after six Codex rounds, all NO-GO; do NOT write a seventh rule — six
870:  with the same F ≥ 10 rule (a refit that did not converge gives NO verdict
881:  the un-committed target file, not a test); the round-6 reproduction (two symmetric GL
1009:tests/test_la_continuous_m.py   # LA(α,β,m) continuity across integer-m kernel widths
1010:tests/test_la_short_input.py    # LA edge cases on very-short input arrays
1011:tests/test_mixed_ds_lacx_e2e.py # End-to-end: a fit with both DS+G and CasaXPS LA peaks
1014:Run via `pytest tests/`.
1020:Typical regions for hand-testing:

codex
The round-1 fixes are present: capped certificate restarts cannot certify directly, and polling now uses heartbeat age instead of total duration. I’m checking whether capped lmfit results keep their parameters and chi-square consistent, and whether any worker exit can leave a heartbeat running.

exec
/bin/zsh -lc "cat tests/autofit/test_fit_certificate.py; sed -n '397,545p' tests/autofit/test_preseed_dominants.py; rg -n 'def _write_job_progress|def _sweep_expired_jobs|JOB_TTL|FIT_JOB_HEARTBEAT_SEC' app.py; sed -n '1,120p' tests/conftest.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
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


def test_a_restart_cut_off_by_its_evaluation_cap_never_certifies():
    """Codex A1 round 1 (MAJOR): with the restart capped, an unfinished descent
    can end a hair ABOVE its start (chi2 959072.771 vs 959072.740); the
    negative improvement passed '< ftol' and a point 3000x above the minimum
    was certified. A capped restart never certifies."""
    x, y, w, model = _two_peak()
    comp = eng._build_composite_model(model)
    good = eng.fit_candidate(x, y, w, model)
    far = good.lmfit_result.params.copy()
    far["s_a_center"].set(value=284.05); far["s_b_amplitude"].set(value=50.0); far["s_a_fwhm"].set(value=2.3)
    out = eng.fit_candidate(x, y, w, model, initial_params=far, max_nfev=2)   # the fit AND its restarts capped
    assert not out.converged, out.weighted_chi_sq
    assert out.weighted_chi_sq > 100 * good.weighted_chi_sq, "really far from the minimum"
                             be_window=(199.0, 201.0), line_shape=LineShape.PSEUDO_VOIGT,
                             fwhm_range=(0.5, 3.0))
    # a model with proposed_peak_1 present but NOT proposed_peak_0 (the
    # reject-first-accept-later state) — count would say 1, max+1 says 2
    m = CandidateModel(name="X", background=eng.BackgroundType.LINEAR,
                       slots=(slot("main_a"), slot("proposed_peak_1")))
    assert eng._next_proposal_index(m) == 2
    # and after augmenting, all slot roles stay unique (no collision)
    spec = eng.ProposalSpec(
        role=f"proposed_peak_{eng._next_proposal_index(m)}",
        detection_windows=[], detection_energy=1.0, detection_ratio=9.0,
        center_init=200.0, fwhm_init=1.0, amplitude_init=5000.0,
        line_shape=eng.PROPOSED_PEAK_SHAPE)
    aug = eng._augmented_candidate(m, spec)
    aug_roles = [s.role for s in aug.slots]
    assert len(aug_roles) == len(set(aug_roles)), f"role collision: {aug_roles}"
    assert "proposed_peak_2" in aug_roles
    # no-proposal model → index 0
    m0 = CandidateModel(name="Y", background=eng.BackgroundType.LINEAR,
                        slots=(slot("main_a"),))
    assert eng._next_proposal_index(m0) == 0


def test_no_wall_clock_can_change_the_answer(monkeypatch):
    """Unit A1 (2026-09-29): the sweep, screen, stability and proposal
    budgets were wall-clock and made the answer depend on server load; they
    are gone. A clock that jumps a million seconds on every read must leave
    the result IDENTICAL."""
    x = _grid()
    truth = [{"center": 196.5, "fwhm": 1.2, "height": 9000.0},
             {"center": 201.5, "fwhm": 1.2, "height": 2500.0}]
    sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
    y = _noisy(sig + _linear_bg(x), 71)
    grammar = _grammar([_cand("single_main", [_slot("main_a", (195.5, 197.5))])])

    def run():
        res = get_method("ic_model_comparison").run(x, y, grammar=grammar, options={**IC_OPTS, "enable_preseed": False})
        return res.diagnostics, res.peaks, res.analysis, res.confidence

    normal = run()
    ticks = {"t": 0.0}

    def jumpy():
        ticks["t"] += 1.0e6
        return ticks["t"]
    monkeypatch.setattr(eng.time, "perf_counter", jumpy)
    assert run() == normal


# ── F3: two-phase sweep ────────────────────────────────────────────────────

def _many_candidate_grammar(x, y):
    """SCREEN_TOP_K+2 candidates: a ladder of window variants, several of
    which cannot express the data (wrong windows)."""
    good = [
        _cand("G1", [_slot("main_a", (195.5, 197.5))]),
        _cand("G2", [_slot("main_a", (195.5, 197.5)),
                     _slot("comp_b", (198.5, 200.5))]),
    ]
    bad = [
        _cand(f"B{i}", [_slot("main_a", (200.5 + i * 0.2, 202.5 + i * 0.2))])
        for i in range(eng.SCREEN_TOP_K)
    ]
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


def test_no_wall_clock_can_change_the_screen_or_the_refit_counts(monkeypatch):
    """Unit A1, Codex round 1 (MINOR): the clock test above never reached the
    screen (one candidate). With more than SCREEN_TOP_K candidates and a clock
    that jumps a million seconds per read, EVERY candidate is still screened,
    every deep candidate runs exactly n_refits refits, and the result is
    identical to the one under a normal clock."""
    x, y, _ = _covered_spectrum(seed=13)
    grammar = _many_candidate_grammar(x, y)
    assert len(grammar.candidates) > eng.SCREEN_TOP_K
    from autofit.methods.base import poisson_like_weights
    w = poisson_like_weights(y)
    attempted = []
    real_stab = eng.run_stability_analysis

    def stab(*a, **k):
        st = real_stab(*a, **k)
        attempted.append((st.n_attempted, k.get("n_refits")))
        return st
    monkeypatch.setattr(eng, "run_stability_analysis", stab)

    def run():
        attempted.clear()
        r = eng.compare_models(x, y, w, grammar, n_refits=3, rng_seed=0, enable_proposal_pass=False, enable_preseed=False)
        return ([row["name"] for row in r.screen], [(row["converged"], row["selected"]) for row in r.screen],
                [rep.model.name for rep in r.reports], [rep.bic_adjusted for rep in r.reports],
                r.analysis_truncated, list(attempted))

    normal = run()
    ticks = {"t": 0.0}

    def jumpy():
        ticks["t"] += 1.0e6
        return ticks["t"]
    monkeypatch.setattr(eng.time, "perf_counter", jumpy)
    jumped = run()
    assert jumped == normal
    names, _, reports, _, truncated, att = jumped
    assert len(names) == len(grammar.candidates), "every candidate screened"
    assert not truncated
    assert att and all(n == want == 3 for n, want in att), att


def test_small_candidate_set_takes_classic_path():
    """≤ SCREEN_TOP_K candidates → no screen phase (screen is None) — every
    existing gate/battery path is unchanged."""
    x, y, grammar = _covered_spectrum(seed=13)
    case_like = type("C", (), {"x": x, "y": y, "grammar": grammar})
    res = _ic(case_like)
    assert res.analysis["screen"] is None
295:_ANALYZE_JOB_TTL_SEC = 3600  # job progress files are short-lived scratch
517:def _write_job_progress(job_id: str, upload_folder: str, data: dict) -> None:
533:def _sweep_expired_jobs(upload_folder: str) -> None:
538:    cutoff = time.time() - _ANALYZE_JOB_TTL_SEC
560:FIT_JOB_HEARTBEAT_SEC = 2.0
625:    cutoff = time.time() - _ANALYZE_JOB_TTL_SEC
666:        while not finished.wait(FIT_JOB_HEARTBEAT_SEC):
1187:        # FIT_JOB_HEARTBEAT_SEC while the worker thread lives (fit jobs' pattern,
1207:            while not finished.wait(FIT_JOB_HEARTBEAT_SEC):
"""Make the repo root importable regardless of how pytest is invoked."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import lmfit, inspect; import lmfit.minimizer as m; print(lmfit.__version__); print(inspect.getsource(m.Minimizer.least_squares)); print(inspect.getsource(m.Minimizer.leastsq))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 exited 1 in 1082ms:
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

exec
/bin/zsh -lc "git diff main..HEAD -- autofit/engine.py | head -270; sed -n '1150,1290p' autofit/engine.py; rg -n 'time\\.|deadline|timeout|success|\\.fit\\(' autofit/engine.py autofit/methods/ic_model_comparison.py autofit/methods/bayesian*" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-DVZKX47c' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-2uANh9I7' (errno=Operation not permitted)
diff --git a/autofit/engine.py b/autofit/engine.py
index dbf4fd7..333de82 100644
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
@@ -849,6 +808,65 @@ def _unphysical_width_flags(
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
+    """Return (the lowest-chi2 point reached, certified). ``max_nfev`` caps
+    each restart like the fit it certifies."""
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
+        lowered = new < chi
+        if lowered:
+            current, chi = r, new
+        # A restart cut off by its EVALUATION CAP (lmfit's `aborted` — a fact
+        # about the budget, not the optimiser's convergence verdict) never
+        # certifies: an unfinished descent can end a hair ABOVE its start, and
+        # that negative "improvement" passed the test (Codex A1 round 1). If
+        # it still lowered chi2 the next restart continues from there; if not,
+        # no progress is possible within the cap — not converged.
+        if getattr(r, "aborted", False):
+            if not lowered:
+                return current, False
+            continue
+        if improvement < CERTIFY_FTOL:
+            return current, True
+    return current, False
+
+
 def fit_candidate(
     x: np.ndarray,
     y: np.ndarray,
@@ -889,25 +907,13 @@ def fit_candidate(
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
@@ -917,9 +923,13 @@ def fit_candidate(
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
@@ -1144,11 +1154,9 @@ class ModelStability:
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
 
@@ -1169,16 +1177,16 @@ def run_stability_analysis(
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
@@ -1205,14 +1213,6 @@ def run_stability_analysis(
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
@@ -1616,11 +1616,9 @@ class ComparisonResult:
     # weighted_bic_top, note} or None (BIC/IC math review blocker:
     # selection must not silently rest on a likelihood the fits reject).
     weighted_ic_disagreement: Optional[dict] = None
-    # Set when the sweep hit TOTAL_ANALYSIS_TIMEOUT_SEC and stopped before
    best_outcome: Optional[FitOutcome] = None
    # How many multi-start fits (refits + primary) landed within
    # BASIN_SUPPORT_RTOL of the best weighted χ² — an honesty diagnostic for
    # the best-minimum promotion (Codex Stage-2 re-review finding #4: a
    # one-off deeper minimum is a different product than a reproducible one).
    # Reporting-only; never used in ranking.
    best_basin_support: int = 0
    # Refits attempted — always n_refits since unit A1 (no wall-clock
    # budget); the denominator of persistence / orphan_rate / convergence_rate.
    # timed_out is never set (kept for the payload's shape).
    n_attempted: int = 0
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
autofit/methods/bayesian_exchange_mc.py:404:                method_id=self.id, success=False,
autofit/methods/bayesian_exchange_mc.py:482:            method_id=self.id, success=True, peaks=peaks, analysis=analysis,
autofit/methods/ic_model_comparison.py:86:                method_id=self.id, success=False, peaks=[], analysis=analysis,
autofit/methods/ic_model_comparison.py:173:            method_id=self.id, success=True, peaks=peaks, analysis=analysis,
autofit/engine.py:133:# residual.  fitalg's Iteration B was already capped/timeout-guarded; this
autofit/engine.py:218:# below the gunicorn --timeout 300) — the real spectra truncated at 8/29 with the
autofit/engine.py:842:            r = composite.fit(y_sub, current.params.copy(), x=x, weights=weights,
autofit/engine.py:892:    leastsq(), surfacing as result.success=False) cuts off the latter
autofit/engine.py:907:        result = composite.fit(y_sub, params, x=x, weights=weights,
autofit/engine.py:913:        # satisfies xtol in ~30 evaluations and reported success at a
autofit/engine.py:1185:    deadline. The 25 s per-candidate budget this replaced made persistence
autofit/engine.py:2809:            pass_start = time.perf_counter()  # telemetry only (wall_time_sec)
autofit/engine.py:2867:                wall_time_sec=time.perf_counter() - pass_start, timed_out=timed_out,

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"-p\", \"no:cacheprovider\", \"tests/autofit/test_fit_certificate.py\", \"tests/autofit/test_preseed_dominants.py\", \"-q\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
exec
/bin/zsh -lc "node --test tests/js/find_peaks_poll_liveness.test.js; sed -n '517,550p' app.py; sed -n '1250,1281p' app.py; rg -n 'def least_squares|def leastsq|aborted|last_internal_values' /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 exited 1 in 192ms:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
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
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 677, in TemporaryFile
    file = _io.open(dir, mode, buffering=buffering,
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 670, in opener
    fd, name = _mkstemp_inner(dir, prefix, suffix, flags, output_type)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 256, in _mkstemp_inner
    fd = _os.open(file, flags, 0o600)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
PermissionError: [Errno 1] Operation not permitted: '/tmp/tmpij3o704j'

 succeeded in 201ms:
# Subtest: a live job is waited on however long it runs (no total-time cap)
ok 1 - a live job is waited on however long it runs (no total-time cap)
  ---
  duration_ms: 87.950305
  type: 'test'
  ...
# Subtest: a stale heartbeat is a lost job, reported — never an endless spinner
ok 2 - a stale heartbeat is a lost job, reported — never an endless spinner
  ---
  duration_ms: 6.779312
  type: 'test'
  ...
# Subtest: the first poll without a heartbeat age yet is waited on
ok 3 - the first poll without a heartbeat age yet is waited on
  ---
  duration_ms: 4.609574
  type: 'test'
  ...
# Subtest: no total-duration watchdog remains in the poll loop
ok 4 - no total-duration watchdog remains in the poll loop
  ---
  duration_ms: 1.241094
  type: 'test'
  ...
1..4
# tests 4
# suites 0
# pass 4
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 218.848129
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
        hb = data.get("heartbeat")
        data["heartbeat_age_sec"] = round(time.time() - hb, 1) if isinstance(hb, (int, float)) else None
        return jsonify(data)

    # ── Long fits via start-then-poll (unit 2, 2026-09-27) ───────────────────
    # The public URL ends a proxied request at ~100 s (Cloudflare 524; 88 s
    # passed, 125 s failed); basinhopping on the large C 1s models takes 3–4
95:    """Raised when a fit is aborted by the user."""
218:    aborted : bool
219:        Whether the fit was aborted.
532:        self.result.last_internal_values = fvars
534:            self.result.aborted = True
536:            self.result.message = f"Fit aborted: {m}"
538:            raise AbortFitException(f"fit aborted: too many function evaluations {self.max_nfev}")
549:            self.result.aborted = True
550:            self.result.message = "Fit aborted by user callback. Could not estimate error-bars."
552:            raise AbortFitException("fit aborted by user.")
689:        result.aborted = False
999:        if not result.aborted:
1012:            result.x = result.last_internal_values
1022:        if (not result.aborted and self.calc_covar and HAS_NUMDIFFTOOLS and
1096:            raise AbortFitException("fit aborted by user.")
1426:            result.aborted = True
1427:            result.message = "Fit aborted by user callback. Could not estimate error-bars."
1435:        if not result.aborted:
1500:    def least_squares(self, params=None, max_nfev=None, **kws):
1570:            result.aborted = True
1575:        if not result.aborted:
1580:            _best = result.last_internal_values
1584:        if not result.aborted:
1609:    def leastsq(self, params=None, max_nfev=None, **kws):
1678:        if not result.aborted:
1681:            _best = result.last_internal_values
1684:            errmsg = 'Fit aborted.'
1774:        if not result.aborted:
1780:            _best = result.last_internal_values
1786:        if (not result.aborted and self.calc_covar and HAS_NUMDIFFTOOLS and
1926:        if not result.aborted:
1963:            _best = result.last_internal_values
2075:        if not result.aborted:
2089:            _best = result.last_internal_values
2095:        if (not result.aborted and self.calc_covar and HAS_NUMDIFFTOOLS and
2156:        if not result.aborted:
2167:            _best = result.last_internal_values
2172:        if (not result.aborted and self.calc_covar and HAS_NUMDIFFTOOLS and
2235:        if not result.aborted:
2246:            _best = result.last_internal_values
2252:        if (not result.aborted and self.calc_covar and HAS_NUMDIFFTOOLS and

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"-s\", \"-p\", \"no:cacheprovider\", \"tests/autofit/test_fit_certificate.py\", \"tests/autofit/test_preseed_dominants.py\", \"-q\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
exec
/bin/zsh -lc "sed -n '510,560p' /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py; sed -n '1530,1610p' /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py; sed -n '1640,1738p' /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py; sed -n '630,740p' app.py; rg -n 'def create_app|makedirs' app.py; rg --files tests/autofit | sort" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
        Returns
        -------
        numpy.ndarray
             The evaluated function values for given `fvars`.

        """
        params = self.result.params

        if fvars.shape == ():
            fvars = fvars.reshape((1,))

        for name, val in zip(self.result.var_names, fvars):
            if apply_bounds_transformation:
                params[name].value = float(params[name].from_internal(val))
            else:
                params[name].value = float(val)
        params.update_constraints()

        if self.max_nfev is None:
            self.max_nfev = 200000*(len(fvars)+1)

        self.result.nfev += 1
        self.result.last_internal_values = fvars
        if self.result.nfev > self.max_nfev:
            self.result.aborted = True
            m = f"number of function evaluations > {self.max_nfev}"
            self.result.message = f"Fit aborted: {m}"
            self.result.success = False
            raise AbortFitException(f"fit aborted: too many function evaluations {self.max_nfev}")

        out = self.userfcn(params, *self.userargs, **self.userkws)

        if callable(self.iter_cb):
            abort = self.iter_cb(params, self.result.nfev, out,
                                 *self.userargs, **self.userkws)
            self._abort = self._abort or abort

        if self._abort:
            self.result.residual = out
            self.result.aborted = True
            self.result.message = "Fit aborted by user callback. Could not estimate error-bars."
            self.result.success = False
            raise AbortFitException("fit aborted by user.")
        else:
            return coerce_float64(out, nan_policy=self.nan_policy)

    def _jacobian(self, fvars, apply_bounds_transformation=True):
        """Return analytical jacobian to be used with Levenberg-Marquardt.

        modified 02-01-2012 by Glenn Jones, Aberystwyth University
        modified 06-29-2015 by M Newville to apply gradient scaling for
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
            result.covar = self._int2ext_cov_x(_cov, _best)
            # calculate parameter uncertainties and correlations
            self._calculate_uncertainties_correlations()
        else:
            result.message = f'{result.message} Could not estimate error-bars.'

        np.seterr(**orig_warn_settings)

        return result

    def basinhopping(self, params=None, max_nfev=None, **kws):
        """Use the `basinhopping` algorithm to find the global minimum.

        This method calls :scipydoc:`optimize.basinhopping` using the
        default arguments. The default minimizer is ``BFGS``, but since
        lmfit supports parameter bounds for all minimizers, the user can
        choose any of the solvers present in :scipydoc:`optimize.minimize`.

        Parameters
        ----------
        params : Parameters, optional
            Contains the Parameters for the model. If None, then the
            Parameters used to initialize the Minimizer object are used.
                    if m.stat().st_mtime < cutoff:
                        m.unlink(missing_ok=True)
                except OSError:
                    pass
        except OSError:
            pass


def _fit_job_cancel(job_id: str, upload_folder: str) -> None:
    try:
        _fit_job_marker(job_id, upload_folder, "cancel").touch()
    except OSError:
        pass


def _fit_job_start(job_id: str, upload_folder: str, fit_args: dict, run) -> None:
    """Start the fit thread and its heartbeat thread. ``run(fit_args, cancel)``
    returns ``(status, body)``; ``(None, None)`` means cancelled."""
    started = time.time()
    lock = threading.Lock()
    rec = {"status": "queued", "elapsed_sec": 0.0, "heartbeat": started}
    _fit_job_write(job_id, upload_folder, rec)
    _fit_job_marker(job_id, upload_folder, "polled").touch()
    cancel_path = _fit_job_marker(job_id, upload_folder, "cancel")
    polled_path = _fit_job_marker(job_id, upload_folder, "polled")
    finished = threading.Event()

    def cancelled() -> bool:
        if cancel_path.exists():
            return True
        try:
            return time.time() - polled_path.stat().st_mtime > FIT_JOB_ABANDON_SEC
        except OSError:
            return False

    def heartbeat() -> None:
        while not finished.wait(FIT_JOB_HEARTBEAT_SEC):
            with lock:
                if rec["status"] not in ("running", "queued"):
                    return
                rec["heartbeat"] = time.time()
                rec["elapsed_sec"] = round(time.time() - started, 1)
                _fit_job_write(job_id, upload_folder, rec)

    def worker() -> None:
        try:
            # queued until a run slot is free; a job cancelled or abandoned
            # while queued never runs
            got = False
            while not got:
                if cancelled():
                    status, body = None, None
                    break
                got = _FIT_JOB_RUN_SLOTS.acquire(timeout=0.5)
            if got:
                try:
                    with lock:
                        rec["status"] = "running"
                        rec["heartbeat"] = time.time()
                        _fit_job_write(job_id, upload_folder, rec)   # visible at once, not at the next heartbeat
                    status, body = run(fit_args, cancelled)
                finally:
                    _FIT_JOB_RUN_SLOTS.release()
        except Exception as exc:                       # the record must always leave "running"
            logging.getLogger(__name__).exception("fit job %s crashed", job_id)
            status, body = 500, {"error": "Internal fitting error — see server log."}
        finally:
            _fit_job_release()
        with lock:
            rec["elapsed_sec"] = round(time.time() - started, 1)
            rec["heartbeat"] = time.time()
            if status is None or cancel_path.exists():
                rec.update(status="cancelled")
            elif status == 200:
                rec.update(status="done", result=body)
            else:
                rec.update(status="error", error=body.get("error"), http_status=status)
            finished.set()
            _fit_job_write(job_id, upload_folder, rec)
        for kind in ("cancel", "polled"):
            try:
                _fit_job_marker(job_id, upload_folder, kind).unlink(missing_ok=True)
            except OSError:
                pass

    # The heartbeat thread starts FIRST: if either thread fails to start this
    # raises BEFORE the worker runs, and the route returns the admission; once
    # the worker has started, only the worker's finally returns it (exactly
    # one owner; Codex round 2).
    threading.Thread(target=heartbeat, daemon=True, name=f"fit-hb-{job_id[:8]}").start()
    try:
        threading.Thread(target=worker, daemon=True, name=f"fit-{job_id[:8]}").start()
    except Exception:
        finished.set()                # stop the heartbeat of a job that never ran
        raise


def _require_json(f):
    """Decorator: return 400 if request body is not valid JSON."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            return _err("Request must be JSON (Content-Type: application/json)")
        return f(*args, **kwargs)
    return wrapper


# ─────────────────────────────────────────────────────────────────────────────
# Spin‑orbit element presets
# ─────────────────────────────────────────────────────────────────────────────

172:def create_app(upload_folder: str = "uploads", data_folder: str = "data/xps") -> Flask:
tests/autofit/battery_common.py
tests/autofit/fixtures/b1s_battery_expected.json
tests/autofit/fixtures/c1s_battery_expected.json
tests/autofit/fixtures/cl2p_battery_expected.json
tests/autofit/fixtures/example_cited_values.json
tests/autofit/fixtures/u4f_battery_expected.json
tests/autofit/stress_cases.py
tests/autofit/test_b1s_cl2p_batteries.py
tests/autofit/test_b1s_cl2p_parity_gates.py
tests/autofit/test_bayesian_method.py
tests/autofit/test_bayesian_real_gate.py
tests/autofit/test_bayesian_u4f_unresolved_gate.py
tests/autofit/test_bic_companions.py
tests/autofit/test_broad_justification.py
tests/autofit/test_browser_schema_roundtrip.py
tests/autofit/test_c1s_mixed_material_class.py
tests/autofit/test_c1s_parity_battery.py
tests/autofit/test_c1s_parity_gate.py
tests/autofit/test_candidate_pool.py
tests/autofit/test_candidate_pool_real_gate.py
tests/autofit/test_candidate_pool_wiring.py
tests/autofit/test_cited_values.py
tests/autofit/test_cl2p_freewidth.py
tests/autofit/test_coverage_index.py
tests/autofit/test_coverage_structure.py
tests/autofit/test_criteria.py
tests/autofit/test_cwt_detector.py
tests/autofit/test_endpoint_avg_wiring.py
tests/autofit/test_engine_doublet.py
tests/autofit/test_filtered_dominant_flag.py
tests/autofit/test_fit_certificate.py
tests/autofit/test_fit_full_window_option.py
tests/autofit/test_fit_physics.py
tests/autofit/test_fit_physics_wiring.py
tests/autofit/test_max_entropy.py
tests/autofit/test_methods_seam.py
tests/autofit/test_multivariate_mcr.py
tests/autofit/test_noise_model.py
tests/autofit/test_preseed_dominants.py
tests/autofit/test_progress_callback.py
tests/autofit/test_quantification_lint.py
tests/autofit/test_reference_bridge.py
tests/autofit/test_region_provenance_honesty.py
tests/autofit/test_resolver.py
tests/autofit/test_sparse_map.py
tests/autofit/test_stage2_completeness.py
tests/autofit/test_stage2_rereview_findings.py
tests/autofit/test_stress_honesty.py
tests/autofit/test_structural_fallback.py
tests/autofit/test_u4f_parity_battery.py
tests/autofit/test_u4f_parity_gate.py

exec
/bin/zsh -lc "sed -n '172,200p' app.py; sed -n '1,175p' tests/autofit/test_c1s_parity_gate.py; rg -n 'Scan_6|MG2|load|reproduc' tests/autofit/test_c1s_parity_gate.py tests/autofit/test_c1s_parity_battery.py; sed -n '2720,2760p' autofit/engine.py; sed -n '16143,16173p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
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

    # ── Routes ────────────────────────────────────────────────────────────────
    _register_routes(app)
    _register_error_handlers(app)

    return app


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _json_sanitize(obj):
    """Defensive numpy→native + non-finite→None conversion for
    /api/analyze payloads: a stray np scalar must not 500 the route, and
    inf/NaN (e.g. BIC of a degenerate fit) must not emit non-standard JSON
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
    engine_env = evaluate_model(rf.roi_be, specs) + shirley_background(
        rf.roi_be, rf.roi_intensity)
    expert_env = np.asarray(rf.fit_result["fittedY"], dtype=float)
    dom = rf.roi_be >= ENVELOPE_DOMAIN_MIN
    r_factor = float(np.sum(np.abs(engine_env[dom] - expert_env[dom]))
tests/autofit/test_c1s_parity_battery.py:13:   fitting.py's lineshapes + run_fit's background reconstruction reproduces
tests/autofit/test_c1s_parity_battery.py:19:3. ``test_battery_fixture_*`` — the same refit reproduces the frozen
tests/autofit/test_c1s_parity_battery.py:38:from autofit.reference import load_reference_fits
tests/autofit/test_c1s_parity_battery.py:55:        for rf in load_reference_fits(zp):
tests/autofit/test_c1s_parity_battery.py:66:    _EXPECTED = {(r["project"], r["name"]): r for r in json.load(_f)["records"]}
tests/autofit/test_c1s_parity_battery.py:114:    # (3) reproduces the frozen characterization record
tests/autofit/test_c1s_parity_gate.py:3:reproduce the expert C 1s reference fits within tolerance.
tests/autofit/test_c1s_parity_gate.py:53:from autofit.reference import load_reference_fits
tests/autofit/test_c1s_parity_gate.py:62:    ("1-GTA UCl4-graphite one set of U doublets.proj.zip", "C1s Scan_6"),
tests/autofit/test_c1s_parity_gate.py:68:    "MG2_graphAsymGL_aliph_sat_CO_C=O",
tests/autofit/test_c1s_parity_gate.py:76:# log).  Measured mains: Scan_2 4 meV (clean MG2), Scan_6 12 meV (clean
tests/autofit/test_c1s_parity_gate.py:86:# Scan_2/Scan_6 unchanged (0.004–0.014); Scan_8 0.0407 (conditional-tier
tests/autofit/test_c1s_parity_gate.py:101:    rf = next(r for r in load_reference_fits(path) if r.name == name)
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
// 2 s while its thread lives; a heartbeat older than FIT_HEARTBEAT_LOST_SEC
// means the thread is gone (e.g. a recycled gunicorn worker), and the
// indicator must never spin forever in that case. A record without a
// heartbeat age yet (the very first poll) is waited on.
async function _fpPollJob(jobId) {
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
    const hb = poll.heartbeat_age_sec;
    if (typeof hb === 'number' && hb > FIT_HEARTBEAT_LOST_SEC) {
      throw new Error('The analysis stopped responding (its server process was ' +
        'probably restarted). Try again.');
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

 succeeded in 45047ms:
......................
22 passed in 44.59s

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import runpy, numpy as np, lmfit
ns=runpy.run_path('\\''tests/autofit/test_fit_certificate.py'\\''); eng=ns['\\''eng'\\'']
x,y,w,model=ns['\\''_two_peak'\\''](); comp=eng._build_composite_model(model)
bg=eng._compute_background(x,y,model.background); yn=y-bg
p=eng._default_params_from_slots(model,x=x,y_net=yn)
print('\\''lmfit'\\'',lmfit.__version__)
for method in ['\\''leastsq'\\'','\\''least_squares'\\'']:
 for cap in [2,3,6,7,10,20,100,6000]:
  r=comp.fit(yn,p.copy(),x=x,weights=w,method=method,max_nfev=cap,nan_policy='\\''omit'\\'')
  actual=np.sum(((yn-comp.eval(r.params,x=x))*w)**2)
  print(method,cap,'\\''nfev'\\'',r.nfev,'\\''aborted'\\'',r.aborted,'\\''success'\\'',r.success,'\\''reported'\\'',r.chisqr,'\\''actual'\\'',actual,'\\''relerr'\\'',(actual-r.chisqr)/actual)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
exec
/bin/zsh -lc "sed -n '1154,1190p' app.py; sed -n '196,226p' app.py; rg -n 'BaseException|SystemExit|KeyboardInterrupt|sys.exit' autofit app.py; sed -n '487,517p' CLAUDE.md; rg -n '"'^def test_'"' tests/autofit/test_preseed_dominants.py tests/autofit/test_stage2_rereview_findings.py tests/autofit/test_engine_doublet.py tests/autofit/test_bayesian_method.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
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
        # Unit A1 (2026-09-29): the record carries a HEARTBEAT, rewritten every
        # FIT_JOB_HEARTBEAT_SEC while the worker thread lives (fit jobs' pattern,
        # unit 2). The engine no longer stops on a wall-clock budget, so a long
        # counted run under load is normal; the page judges the job lost only
        # when the heartbeat stops (a recycled worker), never by total time.

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
    return obj


def _session_path(session_id: str, upload_folder: str) -> Path:
    return Path(upload_folder) / f"{session_id}.npz"


def _load_session(session_id: str, upload_folder: str) -> tuple[np.ndarray, np.ndarray]:
    """Load energy and counts arrays from a session file."""
    path = _session_path(session_id, upload_folder)
    if not path.exists():
        raise KeyError(session_id)
    archive = np.load(path)
    return archive["energy"], archive["counts"]

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
tests/autofit/test_engine_doublet.py:51:def test_fixed_ratio_doublet():
tests/autofit/test_engine_doublet.py:67:def test_relaxed_ratio_doublet_recovers_true_ratio():
tests/autofit/test_engine_doublet.py:79:def test_relaxed_ratio_at_bound_is_boundary_hit():
tests/autofit/test_engine_doublet.py:90:def test_doublet_stability_persistence():
tests/autofit/test_engine_doublet.py:102:def test_proposed_slot_is_phase_unassigned():
tests/autofit/test_engine_doublet.py:119:def test_absent_normalization_is_region_scoped():
tests/autofit/test_bayesian_method.py:68:def test_selects_true_peak_count(result):
tests/autofit/test_bayesian_method.py:79:def test_posterior_recovers_truth(result):
tests/autofit/test_bayesian_method.py:88:def test_noise_estimated(result):
tests/autofit/test_bayesian_method.py:92:def test_uncertainty_typed_and_honest(result):
tests/autofit/test_bayesian_method.py:108:def test_payload_json_safe_and_documented(result):
tests/autofit/test_bayesian_method.py:116:def test_free_energy_error_bar_and_selection_warning():
tests/autofit/test_bayesian_method.py:137:def test_sigma_stat_reliability_contract(result):
tests/autofit/test_bayesian_method.py:151:def test_zero_variance_ess_is_stuck_not_perfect():
tests/autofit/test_bayesian_method.py:165:def test_analytic_evidence_flat_model():
tests/autofit/test_bayesian_method.py:221:def test_seed_replicates_identity_and_mean_semantics():
tests/autofit/test_bayesian_method.py:251:def test_selection_warning_fires_on_twin_models():
tests/autofit/test_bayesian_method.py:271:def test_determinism_and_option_validation():
tests/autofit/test_stage2_rereview_findings.py:52:def test_orphan_peaks_never_clean_survivor():
tests/autofit/test_stage2_rereview_findings.py:65:def test_orphan_only_pool_is_conditional_tier():
tests/autofit/test_stage2_rereview_findings.py:76:def test_basin_support_counts_reproducible_minimum():
tests/autofit/test_stage2_rereview_findings.py:93:def test_sanitized_slug_collision_raises():
tests/autofit/test_stage2_rereview_findings.py:102:def test_distinct_slugs_still_resolve():
tests/autofit/test_stage2_rereview_findings.py:128:def test_criteria_panel_uses_method_threshold():
tests/autofit/test_preseed_dominants.py:58:def test_no_preseed_on_covered_spectrum():
tests/autofit/test_preseed_dominants.py:74:def test_detects_out_of_window_dominant_and_gates_weak_bump():
tests/autofit/test_preseed_dominants.py:95:def test_detection_descending_grid_equivalence():
tests/autofit/test_preseed_dominants.py:116:def test_multi_env_low_be_dominant_recovered():
tests/autofit/test_preseed_dominants.py:160:def test_unphysical_width_flags_helper():
tests/autofit/test_preseed_dominants.py:206:def test_unphysical_width_flags_wide_range_alone_no_longer_exempts():
tests/autofit/test_preseed_dominants.py:226:def test_preseed_and_proposal_slots_capped_at_ordinary():
tests/autofit/test_preseed_dominants.py:246:def test_wide_proposal_capped_and_flagged():
tests/autofit/test_preseed_dominants.py:281:def test_shape_endpoint_pegs_do_not_reject_proposals():
tests/autofit/test_preseed_dominants.py:309:def test_proposal_rejected_when_stability_promotes_spurious_center_peg(monkeypatch):
tests/autofit/test_preseed_dominants.py:356:def test_iterative_proposals_add_two_missing_peaks():
tests/autofit/test_preseed_dominants.py:386:def test_next_proposal_index_is_max_suffix_plus_one():
tests/autofit/test_preseed_dominants.py:420:def test_no_wall_clock_can_change_the_answer(monkeypatch):
tests/autofit/test_preseed_dominants.py:463:def test_screen_phase_records_and_selects():
tests/autofit/test_preseed_dominants.py:481:def test_no_wall_clock_can_change_the_screen_or_the_refit_counts(monkeypatch):
tests/autofit/test_preseed_dominants.py:523:def test_small_candidate_set_takes_classic_path():

 succeeded in 1862ms:
/Users/skyefortier/.matplotlib is not a writable directory
lmfit 1.3.4
leastsq 2 nfev 2 aborted True success False reported 87287.25701057426 actual 87287.25701057426 relerr 0.0
leastsq 3 nfev 3 aborted True success False reported 87283.03331547689 actual 87283.03331547689 relerr 0.0
leastsq 6 nfev 6 aborted True success False reported 87280.00782696417 actual 87280.00782696417 relerr 0.0
leastsq 7 nfev 7 aborted True success False reported 4890.117209837871 actual 4890.117209837871 relerr 0.0
leastsq 10 nfev 10 aborted True success False reported 4890.282167379334 actual 4890.282167379334 relerr 0.0
leastsq 20 nfev 20 aborted True success False reported 317.0511828220816 actual 317.0511828220816 relerr 0.0
leastsq 100 nfev 36 aborted False success True reported 284.3481507668816 actual 284.3481507668816 relerr 0.0
leastsq 6000 nfev 36 aborted False success True reported 284.3481507668816 actual 284.3481507668816 relerr 0.0
least_squares 2 nfev 2 aborted True success False reported 87279.64305579677 actual 87279.64305579677 relerr 0.0
least_squares 3 nfev 3 aborted True success False reported 87279.64656222935 actual 87279.64656222935 relerr 0.0
least_squares 6 nfev 6 aborted True success False reported 87279.63979980872 actual 87279.63979980872 relerr 0.0
least_squares 7 nfev 7 aborted True success False reported 11937.278093709512 actual 11937.278093709512 relerr 0.0
least_squares 10 nfev 10 aborted True success False reported 11937.279850773739 actual 11937.279850773739 relerr 0.0
least_squares 20 nfev 20 aborted True success False reported 1881.9364665127403 actual 1881.9364665127403 relerr 0.0
least_squares 100 nfev 49 aborted False success True reported 284.34815076655656 actual 284.34815076655656 relerr 0.0
least_squares 6000 nfev 49 aborted False success True reported 284.34815076655656 actual 284.34815076655656 relerr 0.0

codex
All 22 certificate and screening tests pass, along with the four JavaScript liveness tests. Real lmfit probes also confirm that both optimisers mark evaluation-cap exits as `aborted` and return consistent parameters and chi-square. I’m now probing worker failures and repeated polls without a heartbeat; the new tests don’t cover those cases.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import app as mod, threading, time, copy, json
from unittest.mock import patch
app=mod.create_app(upload_folder='\\''.'\\'')
app.config['\\''TESTING'\\'']=True
threads=[]; records=[]
real_thread=threading.Thread
def thread(*a,**kw):
 t=real_thread(*a,**kw); threads.append(t); return t
def write(job,folder,data): records.append(copy.deepcopy(data))
def run_case(kind):
 threads.clear(); records.clear()
 def run(ctx,progress_cb=None):
  time.sleep(.045)
  if kind=='\\''error'\\'': raise RuntimeError('\\''crash probe'\\'')
  if kind=='\\''exit'\\'': raise SystemExit('\\''worker stopped'\\'')
  return {}
 with patch.object(mod,'\\''_validate_analyze_request'\\'',return_value={}), patch.object(mod,'\\''_sweep_expired_jobs'\\''), patch.object(mod,'\\''_write_job_progress'\\'',side_effect=write), patch.object(mod,'\\''_run_analyze_method'\\'',side_effect=run), patch.object(mod,'\\''_build_analyze_payload'\\'',return_value={'\\''success'\\'':True}), patch.object(mod,'\\''FIT_JOB_HEARTBEAT_SEC'\\'',.01), patch.object(mod.threading,'\\''Thread'\\'',side_effect=thread):
  with app.test_client() as c:
   response=c.post('\\''/api/analyze/start'\\'',json={})
  time.sleep(.09)
  count=len(records); hb=records[-1]['\\''heartbeat'\\'']
  time.sleep(.035)
  print(kind,'\\''HTTP'\\'',response.status_code,'\\''state'\\'',records[-1]['\\''status'\\''],'\\''threads'\\'',[(t.name.split('\\''-'\\'')[0:2],t.is_alive()) for t in threads],'\\''writes_after_worker_exit'\\'',len(records)-count,'\\''heartbeat_advanced'\\'',records[-1]['\\''heartbeat'\\'']>hb)
  for t in threads:
   if t.is_alive():
    for cell in t._target.__closure__ or ():
     if isinstance(cell.cell_contents,threading.Event): cell.cell_contents.set()
  for t in threads: t.join(.2)
for k in ['\\''done'\\'','\\''error'\\'','\\''exit'\\'']: run_case(k)
class Unreadable:
 def exists(self): return True
 def read_text(self): raise OSError('\\''read failure'\\'')
with patch.object(mod,'\\''_job_progress_path'\\'',return_value=Unreadable()):
 with app.test_client() as c:
  for i in range(2):
   r=c.get('\\''/api/analyze/progress/00000000-0000-0000-0000-000000000001'\\'')
   print('\\''unreadable poll'\\'',r.status_code,r.get_json())
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import runpy
ns=runpy.run_path('\\''tests/autofit/test_fit_certificate.py'\\'')
from autofit.methods import get_method
x,y,w=ns['\\''_scan'\\'']('\\''1-GTA UCl4-graphite one set of U doublets.proj.zip'\\'','\\''C1s Scan_6'\\'')
r=get_method('\\''ic_model_comparison'\\'').run(x,y,grammar=ns['\\''G'\\''],options={'\\''n_refits'\\'':4,'\\''rng_seed'\\'':0,'\\''noise_floor'\\'':1.0,'\\''candidate_filter'\\'':['\\''MG2_graphAsymGL_aliph_sat_CO_C=O'\\'','\\''MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O'\\'','\\''AG2_linked'\\'','\\''A2_linked'\\''],'\\''enable_proposal_pass'\\'':False})
print('\\''SCAN6'\\'',r.success,r.diagnostics)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"-s\", \"-p\", \"no:cacheprovider\", \"tests/autofit/test_engine_doublet.py\", \"tests/autofit/test_stage2_rereview_findings.py\", \"tests/autofit/test_progress_callback.py\", \"tests/autofit/test_bayesian_method.py\", \"-q\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 2509ms:
/Users/skyefortier/.matplotlib is not a writable directory
2026-09-29 13:52:36,458 ERROR app: analyze job 8509851c-7907-4d3a-97f8-afb3151723c3 crashed
Traceback (most recent call last):
  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/app.py", line 1227, in _worker
    res = _run_analyze_method(ctx, progress_cb=_progress_cb)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py", line 1139, in __call__
    return self._mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py", line 1143, in _mock_call
    return self._execute_mock_call(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/unittest/mock.py", line 1204, in _execute_mock_call
    result = effect(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 15, in run
RuntimeError: crash probe
done HTTP 202 state done threads [(['fp', 'hb'], False), (['fp', 'ef8ef6ec'], False)] writes_after_worker_exit 0 heartbeat_advanced False
error HTTP 202 state error threads [(['fp', 'hb'], False), (['fp', '8509851c'], False)] writes_after_worker_exit 0 heartbeat_advanced False
exit HTTP 202 state running threads [(['fp', 'hb'], True), (['fp', '6b2bb113'], False)] writes_after_worker_exit 3 heartbeat_advanced True
unreadable poll 200 {'candidate_index': None, 'candidate_name': None, 'candidate_total': None, 'elapsed_sec': 0.0, 'heartbeat_age_sec': None, 'message': 'starting analysis…', 'phase': 'starting', 'status': 'running'}
unreadable poll 200 {'candidate_index': None, 'candidate_name': None, 'candidate_total': None, 'elapsed_sec': 0.0, 'heartbeat_age_sec': None, 'message': 'starting analysis…', 'phase': 'starting', 'status': 'running'}

exec
/bin/zsh -lc "nl -ba app.py | sed -n '1190,1280p'; nl -ba templates/index.html | sed -n '16143,16170p'; git diff main..HEAD -- scripts/fit_termination_scope.py scripts/fit_termination_scope_analyze.py; sed -n '2710,2725p' autofit/engine.py; sed -n '2748,2776p' autofit/engine.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
  1190	        # when the heartbeat stops (a recycled worker), never by total time.
  1191	        lock = threading.Lock()
  1192	        finished = threading.Event()
  1193	        rec = {"status": "running", "phase": "starting",
  1194	               "candidate_index": None, "candidate_total": None,
  1195	               "candidate_name": None, "elapsed_sec": 0.0,
  1196	               "message": "starting analysis…", "heartbeat": start_time}
  1197	        _write_job_progress(job_id, upload_folder, rec)
  1198	
  1199	        def _publish(update: dict) -> None:
  1200	            with lock:
  1201	                rec.update(update)
  1202	                rec["elapsed_sec"] = round(time.time() - start_time, 1)
  1203	                rec["heartbeat"] = time.time()
  1204	                _write_job_progress(job_id, upload_folder, rec)
  1205	
  1206	        def _heartbeat() -> None:
  1207	            while not finished.wait(FIT_JOB_HEARTBEAT_SEC):
  1208	                with lock:
  1209	                    if rec["status"] != "running":
  1210	                        return
  1211	                    rec["heartbeat"] = time.time()
  1212	                    rec["elapsed_sec"] = round(time.time() - start_time, 1)
  1213	                    _write_job_progress(job_id, upload_folder, rec)
  1214	
  1215	        def _progress_cb(evt: dict) -> None:
  1216	            _publish({
  1217	                "status": "running",
  1218	                "phase": evt.get("phase"),
  1219	                "candidate_index": evt.get("candidate_index"),
  1220	                "candidate_total": evt.get("candidate_total"),
  1221	                "candidate_name": evt.get("candidate_name"),
  1222	                "message": _analyze_progress_message(evt),
  1223	            })
  1224	
  1225	        def _worker() -> None:
  1226	            try:
  1227	                res = _run_analyze_method(ctx, progress_cb=_progress_cb)
  1228	                payload = _build_analyze_payload(ctx, res)
  1229	                final = {"status": "done", "phase": "done", "message": "done", "result": payload}
  1230	            except _AnalyzeError as exc:
  1231	                final = {"status": "error", "phase": "done", "message": "failed",
  1232	                         "error": str(exc), "http_status": exc.status}
  1233	            except Exception as exc:      # belt-and-suspenders: the
  1234	                # indicator must ALWAYS clear, even on a bug we didn't
  1235	                # anticipate — never let a job hang the poll forever.
  1236	                logging.getLogger(__name__).exception(
  1237	                    "analyze job %s crashed", job_id)
  1238	                final = {"status": "error", "phase": "done", "message": "failed",
  1239	                         "error": f"internal error: {exc}", "http_status": 500}
  1240	            finished.set()
  1241	            _publish(final)
  1242	
  1243	        threading.Thread(target=_heartbeat, daemon=True, name=f"fp-hb-{job_id[:8]}").start()
  1244	        try:
  1245	            threading.Thread(target=_worker, daemon=True, name=f"fp-{job_id[:8]}").start()
  1246	        except Exception:
  1247	            finished.set()                # no heartbeat for a job that never ran
  1248	            raise
  1249	        return jsonify({"job_id": job_id}), 202
  1250	
  1251	    @app.get("/api/analyze/progress/<job_id>")
  1252	    def analyze_progress(job_id):
  1253	        """Poll one analyze job's progress (Find Peaks UI, 2026-07-11).
  1254	        {status: 'running'|'done'|'error', phase, candidate_index,
  1255	        candidate_total, candidate_name, elapsed_sec, message, result
  1256	        (done only — the SAME shape /api/analyze returns), error (error
  1257	        only)}. 404 for an unknown/expired job_id; 400 for a malformed
  1258	        one (path-traversal guard, same convention as _validate_session_id)."""
  1259	        try:
  1260	            uuid.UUID(job_id)
  1261	        except ValueError:
  1262	            return _err("Invalid job_id format (expected UUID)", 400)
  1263	        path = _job_progress_path(job_id, app.config["UPLOAD_FOLDER"])
  1264	        if not path.exists():
  1265	            return _err(f"Job '{job_id}' not found", 404)
  1266	        try:
  1267	            data = json.loads(path.read_text())
  1268	        except (OSError, ValueError):
  1269	            # os.replace() makes writes atomic, but tolerate a read racing
  1270	            # the very first write rather than 500ing a normal poll
  1271	            data = {"status": "running", "phase": "starting",
  1272	                    "candidate_index": None, "candidate_total": None,
  1273	                    "candidate_name": None, "elapsed_sec": 0.0,
  1274	                    "message": "starting analysis…"}
  1275	        hb = data.get("heartbeat")
  1276	        data["heartbeat_age_sec"] = round(time.time() - hb, 1) if isinstance(hb, (int, float)) else None
  1277	        return jsonify(data)
  1278	
  1279	    # ── Long fits via start-then-poll (unit 2, 2026-09-27) ───────────────────
  1280	    # The public URL ends a proxied request at ~100 s (Cloudflare 524; 88 s
 16143	// 2 s while its thread lives; a heartbeat older than FIT_HEARTBEAT_LOST_SEC
 16144	// means the thread is gone (e.g. a recycled gunicorn worker), and the
 16145	// indicator must never spin forever in that case. A record without a
 16146	// heartbeat age yet (the very first poll) is waited on.
 16147	async function _fpPollJob(jobId) {
 16148	  while (true) {
 16149	    const resp = await fetch('/api/analyze/progress/' + encodeURIComponent(jobId));
 16150	    if (!resp.ok) {
 16151	      throw new Error('Lost the progress channel (HTTP ' + resp.status + ').');
 16152	    }
 16153	    const poll = await resp.json();
 16154	    document.getElementById('fp-status').textContent = _fpProgressText(poll);
 16155	    if (poll.status === 'done') return poll;
 16156	    if (poll.status === 'error') {
 16157	      throw new Error(poll.error || 'Analysis failed.');
 16158	    }
 16159	    const hb = poll.heartbeat_age_sec;
 16160	    if (typeof hb === 'number' && hb > FIT_HEARTBEAT_LOST_SEC) {
 16161	      throw new Error('The analysis stopped responding (its server process was ' +
 16162	        'probably restarted). Try again.');
 16163	    }
 16164	    await new Promise(r => setTimeout(r, FP_POLL_INTERVAL_MS));
 16165	  }
 16166	}
 16167	
 16168	async function runFindPeaks() {
 16169	  const status = document.getElementById('fp-status');
 16170	  const spinner = document.getElementById('fp-spinner');
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-NF6fteLk' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-fF4j2tvw' (errno=Operation not permitted)
diff --git a/scripts/fit_termination_scope.py b/scripts/fit_termination_scope.py
new file mode 100644
index 0000000..0b717cb
--- /dev/null
+++ b/scripts/fit_termination_scope.py
@@ -0,0 +1,45 @@
+"""Scope check: do Run Fit's fits (main, perturbed restarts, scattered starts) end AT a minimum when they report success?
+Every lmfit Model.fit call inside /api/fit is intercepted; each result is refined from its end point by a fresh
+least_squares fit (same model, data, weights, bounds) and the relative chi2 drop recorded. Usage: OUT.jsonl METHOD"""
+import sys, os, io, json, time
+sys.path.insert(0, '.')
+import numpy as np, lmfit
+OUT, METHOD = sys.argv[1], sys.argv[2]
+from app import create_app
+app = create_app(); cl = app.test_client()
+T = json.load(open('/Users/skyefortier/xps-app/.claude/worktrees/investigate-optimizer-disagreement/docs/findings/optimizer-disagreement/targets.json'))
+done = set()
+if os.path.exists(OUT):
+    for l in open(OUT): done.add(json.loads(l)['id'])
+orig = lmfit.Model.fit
+calls = []
+def fit(self, data, params=None, *a, **k):
+    r = orig(self, data, params, *a, **k)
+    if not calls or calls[-1] is not None:
+        try:
+            k2 = {kk: vv for kk, vv in k.items() if kk not in ('method', 'fit_kws', 'max_nfev', 'iter_cb')}
+            calls.append(None)                     # refinement below must not be recorded
+            ref = orig(self, data, r.params.copy(), *a, method='least_squares', **k2)
+            calls.pop()
+            calls.append({"method": k.get('method'), "success": bool(r.success), "nfev": int(r.nfev), "nvarys": int(r.nvarys),
+                          "chisqr": float(r.chisqr), "refined": float(ref.chisqr), "redchi": float(r.redchi) if r.redchi is not None else None})
+        except Exception as e:
+            if calls and calls[-1] is None: calls.pop()
+            calls.append({"method": k.get('method'), "error": str(e)[:80]})
+    return r
+lmfit.Model.fit = fit
+A, B = (int(v) for v in os.environ.get('SCOPE_SLICE', '0:100000').split(':'))
+for t in T[A:B]:
+    if t['id'] in done: continue
+    csv = "\n".join(f"{a:.4f},{b:.4f}" for a, b in zip(t["be"], t["inten"])).encode()
+    r = cl.post("/api/upload", data={"file": (io.BytesIO(csv), "t.csv")}, content_type="multipart/form-data")
+    sid = r.get_json()["session_id"]
+    bg = t["background"]
+    body = {"session_id": sid, "background": {k: bg[k] for k in ("method", "start_idx", "end_idx", "endpoint_avg")},
+            "peaks": t["specs"], "fit_method": METHOD, "n_perturb": 3, "n_starts": 3}
+    calls.clear(); t0 = time.time()
+    resp = cl.post("/api/fit", json=body).get_json() or {}
+    st = resp.get("starts") or {}
+    with open(OUT, 'a') as f:
+        f.write(json.dumps({"id": t["id"], "success": resp.get("success"), "starts_ran": st.get("ran"), "sec": round(time.time() - t0, 1),
+                            "calls": [c for c in calls if c is not None]}) + "\n")
diff --git a/scripts/fit_termination_scope_analyze.py b/scripts/fit_termination_scope_analyze.py
new file mode 100644
index 0000000..e965da4
--- /dev/null
+++ b/scripts/fit_termination_scope_analyze.py
@@ -0,0 +1,31 @@
+import json, sys, glob
+sp = 'docs/findings/fit-termination-scope/'
+for meth, files in (("Trust-Region (least_squares, page default)", ["scope_tr_a.jsonl", "scope_tr_b.jsonl"]), ("Levenberg-Marquardt (leastsq)", ["scope_lm_a.jsonl", "scope_lm_b.jsonl"])):
+    rows = [json.loads(l) for f in files for l in open(sp + f)]
+    drop = lambda c: (c["chisqr"] - c["refined"]) / c["chisqr"] if c.get("chisqr") else 0.0
+    B = {"returned": [], "restart_ok": [], "start_ok": [], "start_failed_at_min": 0, "start_failed": 0}
+    worst = []
+    for r in rows:
+        calls = [c for c in r["calls"] if "chisqr" in c]
+        if not calls: continue
+        head = calls[:4]; starts = calls[4:] if r.get("starts_ran") else []
+        ok = [c for c in head if c["success"]]
+        if r.get("success") and ok:
+            ret = min(ok, key=lambda c: c["chisqr"])
+            B["returned"].append(drop(ret)); worst.append((drop(ret), r["id"], ret["redchi"], ret["nfev"]))
+        B["restart_ok"] += [drop(c) for c in head[1:] if c["success"]]
+        for c in starts:
+            if c["success"]: B["start_ok"].append(drop(c))
+            else:
+                B["start_failed"] += 1
+                B["start_failed_at_min"] += drop(c) < 1e-6
+    def dist(v):
+        n = len(v)
+        return f"n {n}: drop >1e-6 {sum(d > 1e-6 for d in v)}, >1e-3 {sum(d > 1e-3 for d in v)}, >1% {sum(d > 0.01 for d in v)}, >10% {sum(d > 0.1 for d in v)}"
+    print("==", meth, f"({len(rows)} targets)")
+    print("  returned fit (what the student gets), flagged success:", dist(B["returned"]))
+    print("  perturbed restarts flagged success:                ", dist(B["restart_ok"]))
+    print("  scattered starts flagged success:                  ", dist(B["start_ok"]))
+    print(f"  scattered starts flagged FAILED: {B['start_failed']}, of which already at a minimum (refine drop < 1e-6): {B['start_failed_at_min']}")
+    for d, i, rc, nf in sorted(worst, reverse=True)[:6]:
+        print(f"     worst returned: {i}  chi2r {rc:.3f}  nfev {nf}  refine lowers chi2 by {100*d:.2f} %")
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

 succeeded in 78080ms:
..............................
30 passed in 77.64s (0:01:17)

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import autofit.engine as e
from types import SimpleNamespace as NS
class Params:
 def __init__(self,tag): self.tag=tag
 def copy(self): return Params(self.tag)
def result(chi,tag,aborted=False,success=True): return NS(chisqr=chi,params=Params(tag),aborted=aborted,success=success)
class Comp:
 def __init__(self,seq): self.seq=iter(seq); self.inputs=[]
 def fit(self,y,p,**kw): self.inputs.append(p.tag); r=next(self.seq); return r
start=result(100,'\\''start'\\'',aborted=True,success=False)
cases=[
 ('\\''capped_lower_then_flat'\\'',[result(90,'\\''lower'\\'',True,False),result(90,'\\''flat'\\'',False,False)],True,'\\''lower'\\'',2),
 ('\\''capped_equal'\\'',[result(100,'\\''equal'\\'',True,False)],False,'\\''start'\\'',1),
 ('\\''capped_higher'\\'',[result(101,'\\''higher'\\'',True,False)],False,'\\''start'\\'',1),
 ('\\''uncapped_lower_within_ftol'\\'',[result(100-1e-8,'\\''tiny'\\'',False,False)],True,'\\''tiny'\\'',1),
 ('\\''uncapped_higher'\\'',[result(101,'\\''higher'\\'',False,False)],True,'\\''start'\\'',1),
 ('\\''nonfinite'\\'',[result(float('\\''nan'\\''),'\\''bad'\\'')],False,'\\''start'\\'',1),
 ('\\''capped_lower_exhausts'\\'',[result(100-i-1,str(i),True,False) for i in range(e.CERTIFY_MAX_RESTARTS)],False,str(e.CERTIFY_MAX_RESTARTS-1),e.CERTIFY_MAX_RESTARTS),
 ('\\''uncapped_lower_exhausts'\\'',[result(100-i-1,str(i)) for i in range(e.CERTIFY_MAX_RESTARTS)],False,str(e.CERTIFY_MAX_RESTARTS-1),e.CERTIFY_MAX_RESTARTS)]
for name,seq,cert,tag,count in cases:
 comp=Comp(seq); p,c=e._certify_minimum(comp,None,start,None,None,6000)
 assert (c,p.params.tag,len(comp.inputs))==(cert,tag,count)
 print(name,'\\''PASS'\\'',c,p.params.tag,len(comp.inputs))
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const start=html.indexOf('\\''async function _fpPollJob('\\'');
const src=html.slice(start,html.indexOf('\\''\\nasync function runFindPeaks'\\'',start));
async function probe(mode) {
 let polls=0, elapsed=0;
 const fetch=async()=>{
  polls++; elapsed+=2;
  if (mode==='\\''transport'\\'') throw new Error('\\''network failure'\\'');
  if (mode==='\\''http'\\'') return {ok:false,status:503};
  if(polls===1001) throw new Error('\\''HARNESS STOP'\\'');
  return {ok:true,json:async()=>({status:'\\''running'\\'',heartbeat_age_sec:null})};
 };
 const poll=new Function('\\''fetch'\\'','\\''document'\\'','\\''_fpProgressText'\\'','\\''setTimeout'\\'','\\''FIT_HEARTBEAT_LOST_SEC'\\'','\\''FP_POLL_INTERVAL_MS'\\'',src+'\\'';return _fpPollJob'\\'')(
 fetch,{getElementById:()=>({})},()=>'\\'''\\'',f=>setImmediate(f),30,350);
 try {await poll('\\''test'\\'');} catch(e){console.log(mode,{polls,elapsed,message:e.message})}
}
(async()=>{await probe('\\''missing_heartbeat'\\'');await probe('\\''transport'\\'');await probe('\\''http'\\'')})();
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
missing_heartbeat { polls: 1001, elapsed: 2002, message: 'HARNESS STOP' }
transport { polls: 1, elapsed: 2, message: 'network failure' }
http {
  polls: 1,
  elapsed: 2,
  message: 'Lost the progress channel (HTTP 503).'
}

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import app as m, threading, time, copy
from unittest.mock import patch
a=m.create_app(upload_folder='\\''.'\\''); a.config['\\''TESTING'\\'']=True
real=threading.Thread; threads=[]; writes=[]
def construct(*args,**kw):
 if not kw['\\''name'\\''].startswith('\\''fp-hb-'\\''): raise RuntimeError('\\''cannot create worker'\\'')
 t=real(*args,**kw);threads.append(t);return t
with patch.object(m,'\\''_validate_analyze_request'\\'',return_value={}),patch.object(m,'\\''_sweep_expired_jobs'\\''),patch.object(m,'\\''_write_job_progress'\\'',side_effect=lambda *args:writes.append(copy.deepcopy(args[-1]))),patch.object(m.threading,'\\''Thread'\\'',side_effect=construct),patch.object(m,'\\''FIT_JOB_HEARTBEAT_SEC'\\'',.01):
 try:
  with a.test_client() as c: c.post('\\''/api/analyze/start'\\'',json={})
 except RuntimeError as e: print(str(e))
 for t in threads:t.join(.1)
 print('\\''heartbeat_alive_after_start_failure'\\'',any(t.is_alive() for t in threads),'\\''writes'\\'',len(writes))
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 2204ms:
/Users/skyefortier/.matplotlib is not a writable directory
capped_lower_then_flat PASS True lower 2
capped_equal PASS False start 1
capped_higher PASS False start 1
uncapped_lower_within_ftol PASS True tiny 1
uncapped_higher PASS True start 1
nonfinite PASS False start 1
capped_lower_exhausts PASS False 49 50
uncapped_lower_exhausts PASS False 49 50

 succeeded in 2265ms:
/Users/skyefortier/.matplotlib is not a writable directory
cannot create worker
heartbeat_alive_after_start_failure False writes 1

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python scripts/fit_termination_scope_analyze.py; git diff --check main..HEAD; git status --short' in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 72ms:
docs/autofit/codex/a1_determinism_verdict_runA.md:1345: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:1390: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:1410: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:1411: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:1415: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:1416: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:1503: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:1529: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:1601: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:1618: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:1659: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:1681: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:1920: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:1921: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:1965: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:1985: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:1991: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:2012: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:2013: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:2023: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:2040: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:2081: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:2103: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:2331: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:2352: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:2370: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:2371: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:2415: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:2435: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:2441: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:2462: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:2463: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runA.md:4546: trailing whitespace.
+/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import runpy; t=runpy.run_path(\"tests/autofit/test_fit_certificate.py\"); e=t[\"eng\"]; x,y,w,m=t[\"_two_peak\"](); good=e.fit_candidate(x,y,w,m); print(\"good\",good.weighted_chi_sq); comp=e._build_composite_model(m); p=good.lmfit_result.params.copy(); p[\"s_a_center\"].set(value=284.05); p[\"s_b_amplitude\"].set(value=50.0); p[\"s_a_fwhm\"].set(value=2.3); 
docs/autofit/codex/a1_determinism_verdict_runA.md:4615: trailing whitespace.
+   831	
docs/autofit/codex/a1_determinism_verdict_runA.md:4616: trailing whitespace.
+   832	
docs/autofit/codex/a1_determinism_verdict_runA.md:4640: trailing whitespace.
+   856	
docs/autofit/codex/a1_determinism_verdict_runA.md:4641: trailing whitespace.
+   857	
docs/autofit/codex/a1_determinism_verdict_runA.md:4648: trailing whitespace.
+   418	
docs/autofit/codex/a1_determinism_verdict_runA.md:4649: trailing whitespace.
+   419	
docs/autofit/codex/a1_determinism_verdict_runA.md:4661: trailing whitespace.
+   431	
docs/autofit/codex/a1_determinism_verdict_runA.md:4665: trailing whitespace.
+   435	
docs/autofit/codex/a1_determinism_verdict_runA.md:4668: trailing whitespace.
+   438	
docs/autofit/codex/a1_determinism_verdict_runA.md:4674: trailing whitespace.
+   444	
docs/autofit/codex/a1_determinism_verdict_runA.md:4675: trailing whitespace.
+   445	
docs/autofit/codex/a1_determinism_verdict_runA.md:4677: trailing whitespace.
+   447	
docs/autofit/codex/a1_determinism_verdict_runA.md:4694: trailing whitespace.
+    57	
docs/autofit/codex/a1_determinism_verdict_runA.md:4697: trailing whitespace.
+    60	
docs/autofit/codex/a1_determinism_verdict_runA.md:4702: trailing whitespace.
+    65	
docs/autofit/codex/a1_determinism_verdict_runA.md:4707: trailing whitespace.
+    70	
docs/autofit/codex/a1_determinism_verdict_runA.md:4714: trailing whitespace.
+    77	
docs/autofit/codex/a1_determinism_verdict_runA.md:4721: trailing whitespace.
+    84	
docs/autofit/codex/a1_determinism_verdict_runA.md:4723: trailing whitespace.
+    86	
docs/autofit/codex/a1_determinism_verdict_runA.md:4726: trailing whitespace.
+    89	
docs/autofit/codex/a1_determinism_verdict_runA.md:4732: trailing whitespace.
+    95	
docs/autofit/codex/a1_determinism_verdict_runA.md:5355: trailing whitespace.
+    96	
docs/autofit/codex/a1_determinism_verdict_runA.md:5356: trailing whitespace.
+    97	
docs/autofit/codex/a1_determinism_verdict_runA.md:5372: trailing whitespace.
+   113	
docs/autofit/codex/a1_determinism_verdict_runA.md:5373: trailing whitespace.
+   114	
docs/autofit/codex/a1_determinism_verdict_runA.md:5391: trailing whitespace.
+   132	
docs/autofit/codex/a1_determinism_verdict_runA.md:5392: trailing whitespace.
+   133	
docs/autofit/codex/a1_determinism_verdict_runB.md:72: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:117: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:137: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:138: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:142: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:143: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:230: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:256: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:328: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:345: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:386: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:408: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:647: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:648: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:692: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:712: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:718: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:739: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:740: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:2008: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:2025: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:2066: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:2088: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:2325: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:2326: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:2370: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:2390: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:2396: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:2417: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:2418: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:4110: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:4131: trailing whitespace.
+ 
docs/autofit/codex/a1_determinism_verdict_runB.md:4992: trailing whitespace.
+    50	
docs/autofit/codex/a1_determinism_verdict_runB.md:4999: trailing whitespace.
+    57	
docs/autofit/codex/a1_determinism_verdict_runB.md:5002: trailing whitespace.
+    60	
docs/autofit/codex/a1_determinism_verdict_runB.md:5007: trailing whitespace.
+    65	
docs/autofit/codex/a1_determinism_verdict_runB.md:5012: trailing whitespace.
+    70	
docs/autofit/codex/a1_determinism_verdict_runB.md:5019: trailing whitespace.
+    77	
docs/autofit/codex/a1_determinism_verdict_runB.md:5026: trailing whitespace.
+    84	
docs/autofit/codex/a1_determinism_verdict_runB.md:5028: trailing whitespace.
+    86	
docs/autofit/codex/a1_determinism_verdict_runB.md:5031: trailing whitespace.
+    89	
docs/autofit/codex/a1_determinism_verdict_runB.md:5037: trailing whitespace.
+    95	
docs/autofit/codex/a1_determinism_verdict_runB.md:5043: trailing whitespace.
+   418	
docs/autofit/codex/a1_determinism_verdict_runB.md:5044: trailing whitespace.
+   419	
docs/autofit/codex/a1_determinism_verdict_runB.md:5056: trailing whitespace.
+   431	
docs/autofit/codex/a1_determinism_verdict_runB.md:5060: trailing whitespace.
+   435	
docs/autofit/codex/a1_determinism_verdict_runB.md:5063: trailing whitespace.
+   438	
docs/autofit/codex/a1_determinism_verdict_runB.md:5069: trailing whitespace.
+   444	
docs/autofit/codex/a1_determinism_verdict_runB.md:5070: trailing whitespace.
+   445	
docs/autofit/codex/a1_determinism_verdict_runB.md:5072: trailing whitespace.
+   447	
docs/autofit/codex/a1_determinism_verdict_runB.md:5086: trailing whitespace.
+   461	
docs/autofit/codex/a1_determinism_verdict_runB.md:5087: trailing whitespace.
+   462	
docs/autofit/codex/a1_determinism_verdict_runB.md:5517: trailing whitespace.
+   831	
docs/autofit/codex/a1_determinism_verdict_runB.md:5518: trailing whitespace.
+   832	
docs/autofit/codex/a1_determinism_verdict_runB.md:5542: trailing whitespace.
+   856	
docs/autofit/codex/a1_determinism_verdict_runB.md:5543: trailing whitespace.
+   857	
docs/autofit/codex/a1_determinism_verdict_runB.md:5868: trailing whitespace.
+     2	
docs/autofit/codex/a1_determinism_verdict_runB.md:5872: trailing whitespace.
+     6	
docs/autofit/codex/a1_determinism_verdict_runB.md:5874: trailing whitespace.
+     8	
docs/autofit/codex/a1_determinism_verdict_runB.md:5884: trailing whitespace.
+    18	
docs/autofit/codex/a1_determinism_verdict_runB.md:5886: trailing whitespace.
+    20	
docs/autofit/codex/a1_determinism_verdict_runB.md:5893: trailing whitespace.
+    27	
docs/autofit/codex/a1_determinism_verdict_runB.md:5904: trailing whitespace.
+    11	
docs/autofit/codex/a1_determinism_verdict_runB.md:5908: trailing whitespace.
+    15	
docs/autofit/codex/a1_determinism_verdict_runB.md:5913: trailing whitespace.
+    20	
docs/autofit/codex/a1_determinism_verdict_runB.md:5916: trailing whitespace.
+    23	
docs/autofit/codex/a1_determinism_verdict_runB.md:5917: trailing whitespace.
+    24	
docs/autofit/codex/a1_determinism_verdict_runB.md:5922: trailing whitespace.
+    29	
docs/autofit/codex/a1_determinism_verdict_runB.md:5923: trailing whitespace.
+    30	
docs/autofit/codex/a1_determinism_verdict_runB.md:5926: trailing whitespace.
+    33	
docs/autofit/codex/a1_determinism_verdict_runB.md:5927: trailing whitespace.
+    34	
docs/autofit/codex/a1_determinism_verdict_runB.md:5931: trailing whitespace.
+    38	
docs/autofit/codex/a1_determinism_verdict_runB.md:5932: trailing whitespace.
+    39	
docs/autofit/codex/a1_determinism_verdict_runB.md:6438: trailing whitespace.
+ 16137	
docs/autofit/codex/a1_determinism_verdict_runB.md:6446: trailing whitespace.
+ 16145	
docs/autofit/codex/a1_determinism_verdict_runB.md:6467: trailing whitespace.
+ 16166	
docs/autofit/codex/a1_determinism_verdict_runB.md:6568: trailing whitespace.
+   141	
docs/autofit/codex/a1_determinism_verdict_runB.md:6582: trailing whitespace.
+   155	
docs/autofit/codex/a1_determinism_verdict_runB.md:6597: trailing whitespace.
+  2739	
docs/autofit/codex/a1_determinism_verdict_runB.md:6611: trailing whitespace.
+  2753	
docs/autofit/codex/a1_determinism_verdict_runB.md:6614: trailing whitespace.
+    96	
docs/autofit/codex/a1_determinism_verdict_runB.md:6615: trailing whitespace.
+    97	
docs/autofit/codex/a1_determinism_verdict_runB.md:6631: trailing whitespace.
+   113	
docs/autofit/codex/a1_determinism_verdict_runB.md:6632: trailing whitespace.
+   114	
docs/autofit/codex/a1_determinism_verdict_runB.md:6650: trailing whitespace.
+   132	
docs/autofit/codex/a1_determinism_verdict_runB.md:6651: trailing whitespace.
+   133	
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-rInL3dZU' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-vYLSAejb' (errno=Operation not permitted)
?? docs/autofit/codex/a1_determinism_r2_verdict_runA.md
?? docs/autofit/codex/a1_determinism_r2_verdict_runB.md

codex
I reproduced two liveness gaps: repeated read failures produce polls with no heartbeat that the page waits on indefinitely, and a worker exiting via `SystemExit` leaves its heartbeat thread running. Normal exceptions, successful completion, and worker-start failure stop the heartbeat correctly. The additional 30 engine and Bayesian tests pass; the Scan_6 recheck is still running.

 succeeded in 119986ms:
/Users/skyefortier/.matplotlib is not a writable directory
SCAN6 True {'winner': 'MG2_graphAsymGL_aliph_sat_CO_C=O+preseed', 'conditional': True, 'conditional_reason': 'no_clean_survivor', 'winner_boundary_hits': ['contamination_C=O:fwhm@max', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@max'], 'winner_unphysical_widths': ['main_aliphatic:fwhm=2.00eV≥2.0eV ordinary cap (no known-broad justification)', 'contamination_C=O:fwhm=2.00eV≥2.0eV ordinary cap (no known-broad justification)'], 'winner_boundary_fixed_params': [], 'filtered_dominant_alternative': None, 'weighted_ic_disagreement': None, 'preseeded_features': [{'role': 'preseed_curvature_0', 'center_be': 283.161, 'amplitude_net': 6750.8, 'fraction_of_max': 0.125, 'local_snr': 68.5, 'fwhm_init': 0.59, 'provenance': 'curvature_shoulder', 'gates': {'min_fraction_of_max': 0.25, 'amplitude_snr': 5.0, 'note': 'UNVERIFIED engine tunables — pre-seeded slots are region-unassigned; assignment requires human review'}, 'prom_z': 30.76, 'augmented_into_grammar': True}], 'n_survivors': 5, 'n_filtered': 5, 'n_non_converged': 0, 'analysis_truncated': False, 'n_candidates_evaluated': 5, 'n_candidates_total': 5}

exec
/bin/zsh -lc "git diff --numstat main..HEAD -- tests/autofit/test_preseed_dominants.py; git diff main..HEAD -- tests/autofit/test_preseed_dominants.py | head -180; rg -n 'time\\.|deadline|timeout' autofit | head -70; sed -n '2820,2873p' autofit/engine.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-CASeHisL' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-GmuemsC8' (errno=Operation not permitted)
59	68	tests/autofit/test_preseed_dominants.py
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-z4VLStCX' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-iqUkRKwC' (errno=Operation not permitted)
diff --git a/tests/autofit/test_preseed_dominants.py b/tests/autofit/test_preseed_dominants.py
index 74ec475..7a99611 100644
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
+    def run():
+        res = get_method("ic_model_comparison").run(x, y, grammar=grammar, options={**IC_OPTS, "enable_preseed": False})
+        return res.diagnostics, res.peaks, res.analysis, res.confidence
 
-    calls = {"n": 0}
+    normal = run()
+    ticks = {"t": 0.0}
 
-    def fake_pc():
-        calls["n"] += 1
-        return 1000.0 + (0.0 if calls["n"] == 1 else 13.0)
-
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
@@ -529,6 +478,48 @@ def test_screen_phase_records_and_selects():
     assert res.diagnostics["winner"].startswith("G2")
 
 
+def test_no_wall_clock_can_change_the_screen_or_the_refit_counts(monkeypatch):
+    """Unit A1, Codex round 1 (MINOR): the clock test above never reached the
+    screen (one candidate). With more than SCREEN_TOP_K candidates and a clock
+    that jumps a million seconds per read, EVERY candidate is still screened,
+    every deep candidate runs exactly n_refits refits, and the result is
+    identical to the one under a normal clock."""
+    x, y, _ = _covered_spectrum(seed=13)
+    grammar = _many_candidate_grammar(x, y)
+    assert len(grammar.candidates) > eng.SCREEN_TOP_K
+    from autofit.methods.base import poisson_like_weights
+    w = poisson_like_weights(y)
+    attempted = []
+    real_stab = eng.run_stability_analysis
+
+    def stab(*a, **k):
+        st = real_stab(*a, **k)
+        attempted.append((st.n_attempted, k.get("n_refits")))
+        return st
+    monkeypatch.setattr(eng, "run_stability_analysis", stab)
+
+    def run():
+        attempted.clear()
+        r = eng.compare_models(x, y, w, grammar, n_refits=3, rng_seed=0, enable_proposal_pass=False, enable_preseed=False)
+        return ([row["name"] for row in r.screen], [(row["converged"], row["selected"]) for row in r.screen],
+                [rep.model.name for rep in r.reports], [rep.bic_adjusted for rep in r.reports],
+                r.analysis_truncated, list(attempted))
+
+    normal = run()
+    ticks = {"t": 0.0}
+
+    def jumpy():
+        ticks["t"] += 1.0e6
+        return ticks["t"]
+    monkeypatch.setattr(eng.time, "perf_counter", jumpy)
+    jumped = run()
+    assert jumped == normal
+    names, _, reports, _, truncated, att = jumped
+    assert len(names) == len(grammar.candidates), "every candidate screened"
+    assert not truncated
+    assert att and all(n == want == 3 for n, want in att), att
+
+
 def test_small_candidate_set_takes_classic_path():
     """≤ SCREEN_TOP_K candidates → no screen phase (screen is None) — every
     existing gate/battery path is unchanged."""
autofit/grammar.py:140:    # the DS+G Lorentzian HWHM at the C 1s core-hole lifetime.
autofit/engine.py:133:# residual.  fitalg's Iteration B was already capped/timeout-guarded; this
autofit/engine.py:218:# below the gunicorn --timeout 300) — the real spectra truncated at 8/29 with the
autofit/engine.py:1185:    deadline. The 25 s per-candidate budget this replaced made persistence
autofit/engine.py:2809:            pass_start = time.perf_counter()  # telemetry only (wall_time_sec)
autofit/engine.py:2867:                wall_time_sec=time.perf_counter() - pass_start, timed_out=timed_out,
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

codex
1. **MAJOR — Missing heartbeats can cause endless polling.** [templates/index.html:16159](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/templates/index.html:16159), [app.py:1268](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/app.py:1268). Persistent record-read or JSON-decoding failures return HTTP 200 with `status="running"` and `heartbeat_age_sec=null`. The page waits indefinitely because only numeric ages can fail. Reproduced the route’s fallback and ran the actual poll function through 1,000 such responses; only the harness stopped it. Allow the first missing heartbeat, but bound time without valid heartbeat evidence using the existing liveness threshold.

2. **MAJOR — An uncaught worker exit leaves a falsely live heartbeat.** [app.py:1240](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/app.py:1240). `finished.set()` is outside a `finally`, while the handler catches only `Exception`. Injecting `SystemExit` into `_run_analyze_method` terminated the worker but left its heartbeat thread writing fresh `running` records. The page therefore never detects the dead job. Guarantee heartbeat shutdown in `finally`; add a regression for this exit path.

Validation: **52 Python tests and four JavaScript tests passed**. Additional probes passed for certificate exit branches, restart counts, returned points, real lmfit cap semantics, ordinary worker exceptions, completion, and worker-start failure. The reduced Scan_6 request returned **MG2+preseed**. The screening clock test exercises real screening and refits.

The existing tests miss both failures above. Lifecycle probes used in-memory storage because the workspace is read-only; the disk-backed API suite and full heavy-load matrix were not rerun. Section 4’s screen option remains an owner decision, not a finding.

**VERDICT: NO-GO**
tokens used
93,969
1. **MAJOR — Missing heartbeats can cause endless polling.** [templates/index.html:16159](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/templates/index.html:16159), [app.py:1268](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/app.py:1268). Persistent record-read or JSON-decoding failures return HTTP 200 with `status="running"` and `heartbeat_age_sec=null`. The page waits indefinitely because only numeric ages can fail. Reproduced the route’s fallback and ran the actual poll function through 1,000 such responses; only the harness stopped it. Allow the first missing heartbeat, but bound time without valid heartbeat evidence using the existing liveness threshold.

2. **MAJOR — An uncaught worker exit leaves a falsely live heartbeat.** [app.py:1240](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/app.py:1240). `finished.set()` is outside a `finally`, while the handler catches only `Exception`. Injecting `SystemExit` into `_run_analyze_method` terminated the worker but left its heartbeat thread writing fresh `running` records. The page therefore never detects the dead job. Guarantee heartbeat shutdown in `finally`; add a regression for this exit path.

Validation: **52 Python tests and four JavaScript tests passed**. Additional probes passed for certificate exit branches, restart counts, returned points, real lmfit cap semantics, ordinary worker exceptions, completion, and worker-start failure. The reduced Scan_6 request returned **MG2+preseed**. The screening clock test exercises real screening and refits.

The existing tests miss both failures above. Lifecycle probes used in-memory storage because the workspace is read-only; the disk-backed API suite and full heavy-load matrix were not rerun. Section 4’s screen option remains an owner decision, not a finding.

**VERDICT: NO-GO**
