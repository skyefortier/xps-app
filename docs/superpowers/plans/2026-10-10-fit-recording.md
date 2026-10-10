# Fit recording — what computed each fit, saved with it (owner, 2026-10-10)

Owner: "Do the RECORDING unit first (additive, deployable, no change to fitted numbers)": every
fit response reports the background verdict, the certificate verdict (kept, not discarded), the
fit method, the seed and the software identity; the server accepts the seed over HTTP; the page
saves all of it with the fit in projects, spectra and exports; old saves load exactly as today;
nothing is yet used to decide current / stale. The full sealed record is parked; its v6 design
builds on these fields after this deploys.

## Server (fitting.py, app.py) — additive response fields

| field | what | source |
|---|---|---|
| `fit_method` | the method run | `run_fit`'s validated method |
| `random_seed` (existing) + `seed_source` | the seed and whether it was derived from the request (`"request"`) or given (`"caller"`) | `_request_seed` / the caller seed |
| `background_verdict` | `{method, effect, check, converged, residual, reason}`: `effect` is the background BY ITS EFFECT (`_background_effect` — the seed's own reading: the window where the method reads one, the averaging k as it acts, a manual background's anchors); `check` `defining_statement` (the integral methods: `background_certificate`'s own result, passed out of `compute_background` through a new optional `report` dict — no second certification) or `explicit` (linear, manual, none: nothing to converge; they exist or the request was refused with 422) | `compute_background(..., report=)`, `_background_verdict` |
| `certificate` (existing) | kept whole by the page now (it kept only a > 1 eV move) | `_certificate_report` |
| `software` | `{git_commit, git_dirty, python, numpy, scipy, lmfit, seed_derivation}`, read ONCE at import (`SOFTWARE`) so it names the code this worker LOADED; `git_dirty` = tracked files differ from the commit; null when git is unavailable | `_software_identity` |

`SEED_TAG` is one constant used by both the hash and the record (the hashed bytes are
unchanged: the pinned seed test passes). `/api/fit` and `/api/fit/start` accept `seed` (an
integer in [0, 2**32), the same rule as `run_fit`'s caller seed; anything else 400
"seed must be an integer in [0, 2**32)"), mapped to `fit_kws.fit_kws.seed`. No fitted number
changes: without `seed` the request is exactly as before.

## Page (templates/index.html)

- `fitResult.record` — one object written by the producer: `_fitRecordFrom(response)` for Run Fit
  (and "Use this solution", which is a Run Fit) and Auto-Fit; `_localFitRecord(...)` for the local
  engine and Batch Fit (method `local_lm`, no seed — it draws nothing — its coordinate
  certificate with its restart count, the page's certified background; software null).
- Saved by the project save and the spectrum save (`statistics.record`); restored by the project
  loader (verbatim) and the spectrum loader (explicitly, `_isFitRecord` — its other fields are
  copied only when truthy, which would drop a seed of 0).
- Exported: CSV and TSV header lines and XLSX "Info" rows (`_fitRecordRows`): Fit method, Random
  seed, Background check, Minimum certificate, Software.
- Read by nothing else: no state, note or decision depends on it. A save without a record loads
  exactly as before (the legacy restore rule is untouched).

## Not in this unit (the sealed design's v6)

The request's starting values are not recorded, so "re-run" means re-sending the original
request with the recorded seed — the test captures that request from the page's own fetch.
Recording the request (and binding the record to the displayed model) is the sealed design.

## Tests

`tests/test_fit_recording.py` (server: every field for five backgrounds, the verdict equals the
certificate on the fit's window, a setting the background ignores is not recorded as acting —
found by `test_fit_reproducibility.py` on a first draft that recorded `endpoint_avg` as sent — the
seed tag, global methods, caller seeds, HTTP validation on both routes, a re-run with the
reported seed reproduces the fit within `fit_equality` with perturbed restarts and scattered
starts, the job route); `tests/test_browser_fit_recording.py` (real browser: the record equals the
server's fields; project and spectrum round trips; a seed of 0 through the spectrum loader; CSV /
XLSX / TSV; an older save without a record loads as before; the local engine's record; the saved
seed, read back from a reloaded project, re-runs the page's request to the same fit);
`tests/js/fit_recording.test.js` (producers, saves, loader, export rows). Mutation-checked:
removing the loader copy, the project save field, the CSV lines or the Run Fit record each fails a
test.

## Codex round 1 (NO-GO ×2, the same seven MAJOR findings) — fixed

| finding | fix |
|---|---|
| `/api/analyze` (its least-squares method) dropped the record | `fitting.fit_record(res)` (the `RECORD_KEYS`) carried in its `analysis.record` |
| the local / Batch record lacked "moved / how far", the background residual and the software | the local engine snapshots its parameters where its descent FIRST stops (before any certificate restart): `certificate {certified, restarts, moved, centre_moves, largest_centre_move, check: 'coordinate'}`; the background verdict is the page's own certificate (`computeBackgroundCore` attaches it to the certified curve as a non-index property); the software is the server's identity written into the page (`<meta name="xps-software">`, `role: served_the_page`) |
| `.fit.json` dropped the record | `fitStatistics.record`; an import onto other data keeps it as the parameters' provenance (`modelProvenance = {importedFrom: 'fit.json', record}` — the existing provenance lifecycle: undo, history, Batch copies, saves, both loaders), never a fit (`fitResult` stays null, `_isLocalModel` unaffected) |
| the figure PNG carried nothing | the record's JSON in an `iTXt` chunk (`XPS-Fit-Record`) after IHDR; the PNG stays valid (CRCs checked by the test) |
| CSV / XLSX / TSV lost data (anchors, reasons, every centre move, the largest move's component, unrounded values) | a lossless `Fit record (JSON)` line / row in every export beside the readable summary; the summary no longer rounds a move and names its component |
| no numerical version | `NUMERICS_VERSION` ("2026-10-09", the background math) in `software.numerics`, bumped whenever a change can move a fitted number for the same request |
| the export test checked labels and the in-memory XLSX | the JSON line / row of CSV, TSV and the SERIALISED XLSX (written and read back) must equal the record; the PNG's chunk likewise; `.fit.json` and its import; the analyze method; mutation-checked (each fix removed → a test fails) |

## Codex round 2 (NO-GO ×2) — fixed

Round 1's seven are resolved in both runs (first-stop snapshot bit-identical against main;
the background property, imported provenance, PNG and meta tag inert). Three gaps remained
in the LOCAL record, found once each or by both:

| finding | fix |
|---|---|
| `moved` was inferred from the centres, so a restart that moved only a width or an amplitude (centre locked) read "not moved" (run B) | `moved` = the returned point is not where the descent first stopped, over EVERY parameter — the server's `point is not result`; the centre moves stay a separate measurement |
| `centre_moves` came from the free parameters, leaving out linked components (and locked centres) (run A: committed C1s Scan_4 with a child linked to component 4) | every component's centre is snapshotted at the first stop and compared with the returned one, in model order — the server's list (every `_center` parameter, expressions and fixed ones included) |
| the local background record had no `effect` (both runs, carried from round 1) | `_bgEffect`, the twin of `fitting._background_effect` (window end exclusive as the request sends it, averaging as it acts, anchors in energy order); `computeBackgroundCore` attaches it and the method to the curve it returns, so the record reads the background it was fitted on, not the menu at record time. A browser test fits eight settings (Shirley at two windows and averagings, Smart at averaging 50, Tougaard, Linear, Manual with three anchors and with none, None) on the server and then locally: the two effects are equal |

Mutation-checked: centre-only `moved`, the linked components dropped, no effect, an
inclusive window end and unsorted anchors each fail a test.
