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
