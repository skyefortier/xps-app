# Unit 2 — long fits via start-then-poll (2026-09-27)

Branch `fix-fit-start-poll`, cut from `fix-acceptance-holes` (F2). DEPENDENCY:
F2 deploys first — both change `runFit` and `runAutoFitC1sGraphite`, and this
unit builds on F2's `_readFitReply`, Auto-Fit's `resp.ok` check and the
basinhopping changes.

Owner's brief (2026-09-27): "/api/fit/start returns a job id; the fit runs in
the background; the page polls. Reuse Find Peaks' job infrastructure. Cover
Run Fit and Auto-Fit. Requirements: the async-ownership rule (capture tab and
inputs before the first await; discard results for an edited model or
switched tab); F1's fit key and statistics binding unchanged; seeding
unchanged — a polled fit gives the same result as today's; cancellation, so
abandoned or re-run fits stop consuming workers." Acceptance tonight, dev
server only: basinhopping on the five largest C 1s models completes through
the poll path; no single HTTP request in the poll path lasts longer than a
few seconds; DS+G and DE results unchanged. No interim 524 message.

Why: the public URL ends a proxied request at ~100 s (Cloudflare 524; 88 s
passed, 125 s failed — `docs/findings/2026-09-26-public-request-ceiling.md`);
basinhopping on the large C 1s models takes 183–256 s even without restarts.

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
- **Concurrency (round 1).** One fit runs per worker process at a time; the
  rest wait `queued`; at most 6 running + queued per process, beyond that a
  503. With production's 4 workers, at most 4 concurrent fits — the bound the
  synchronous route had.
- **Supersede (round 1).** A new start for the same tab cancels that tab's
  previous job; the superseded loop returns quietly.
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

## 4. Post-deploy check (the owner, through the PUBLIC URL)

`scripts/public_fit_poll_check.py` does what the page does — upload, start,
poll every 0.5 s — through https://xps.fortierlab.org by default, on the five
largest committed C 1s models (basinhopping, the page's `n_perturb: 3`,
`n_starts: 3`), and records every request's duration. PASS = each job ends
`done` with `success: true` and no request took longer than 10 s.

    venv/bin/python scripts/public_fit_poll_check.py \
        .claude/worktrees/investigate-optimizer-disagreement/docs/findings/optimizer-disagreement/targets.json

(≈ 5 × 3–4 minutes; one production worker thread each, sequentially.) Then
once in a browser on xps.fortierlab.org: the committed UCl4-graphite project,
C1s Scan, Method = Basin-hopping, Run Fit → "Fit complete" after a few
minutes; DevTools → Network: every `/api/fit/*` request short, no 524.

## 5. Verification

- Python `tests/test_fit_start_poll.py` (14): polled = synchronous byte for
  byte (Levenberg-Marquardt), the same answer for DE / basinhopping /
  Trust-Region (same seed, χ²ᵣ to 1e-6); four bad requests refused
  immediately and identically on both routes; a run_fit refusal (F2's
  determinacy) reaches the record with the synchronous message and 400;
  cancel stops a running basinhopping fit in < 10 s; a job nobody polls
  stops itself; the heartbeat moves; malformed / unknown ids; a NaN result
  reaches the page unsanitised.
- JS `tests/js/fit_start_poll.test.js` (11): done / running / error /
  cancelled / NaN / lost heartbeat; a failed start is a transport failure;
  one lost poll retried, five are transport and cancel the job; tab / model
  abandonment cancels and returns the reason with no further poll; the
  Auto-Fit abort cancels; no page path posts to the synchronous `/api/fit`.
  The existing runFit / Auto-Fit sandboxes (`fit_acceptance`,
  `stale_statistics`) serve their scripted single reply as a finished job
  (`jobAdapter` / `pollify`) so they keep testing what they tested;
  `_runningFitJobs` allowlisted (class A) in `per_tab_state`.
- Browser (:5151, committed UCl4-graphite project): Run Fit → 1 start + 53
  polls, no synchronous `/api/fit`, "Fit complete", statistics current; a
  basinhopping fit abandoned by a tab switch and by a centre edit → the usual
  discard messages at the next poll, a cancel POST, the server job
  `cancelled` within 0.5 s; Auto-Fit → start + poll, complete, current; the
  start made unreachable → the local fallback and its overlay, as before. No
  page errors.

## 6. Codex rounds

**Round 1 — NO-GO ×2** (`fit_start_poll_verdict_run{A,B}.md`; the same four
findings in both):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR: a re-run did not supersede — Ctrl/Cmd+F calls `runFit` past the disabled button; two jobs for one tab, the older could finish first and get the newer discarded as "model edited" | `_fitJobByOwner` (WeakMap keyed by the tab record): a new start for the same tab cancels the previous job on the server; the superseded loop returns `{ _abandoned: 'superseded' }` and its caller does NOTHING (the new fit owns spinner and result; Auto-Fit does not roll back, which would overwrite the new fit's model). Run Fit and Auto-Fit both pass their tab as `owner`. |
| 2 | MAJOR: unbounded concurrency — a thread per start, where four sync workers used to bound concurrent fits at four | each worker process runs at most `FIT_JOB_MAX_RUNNING` = 1 fit (a semaphore); the rest wait `queued` (heartbeating, cancellable, a queued job cancelled or abandoned never runs); at most `FIT_JOB_MAX_ADMITTED` = 6 running + queued per process, beyond that `/api/fit/start` answers 503 "The server is busy with other fits" at once (the page shows it as a failed fit). Production: ≤ 4 concurrent fits, as before. |
| 3 | MINOR: a cancellation observed mid-fit could surface as the solver's own error (AttributeError from Levenberg-Marquardt, RuntimeError from Nelder-Mead / DE) — an abandoned job became `error` 500 / 422 | `run_fit(cancel=)` turns any exception raised after cancellation was observed into `FitCancelled`; unrelated errors propagate unchanged |
| 4 | MINOR: `public_fit_poll_check.py` could poll a dead worker's record forever | a heartbeat older than 30 s is FAIL "lost"; a 20-minute deadline per target (the job is cancelled) |



**Round 2 — NO-GO ×2** (`fit_start_poll_r2_verdict_run{A,B}.md`; both confirmed
round 1's cancellation normalisation, checker and concurrency; the same three
findings):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR: ownership was registered when the START RESPONSE arrived, so response order decided it — A pressed first, B second, A's late response cancelled B and A's stale result applied | an OPERATION per tab, claimed BEFORE THE CALLER'S FIRST AWAIT (`_claimFitOp`; runFit right after its context key, Auto-Fit before its upload): the newest claim is current whatever order the responses come in; a claim cancels the previous operation's job; a start response that arrives for a superseded operation cancels its own job |
| 2 | MAJOR: supersession was checked only before a poll, never after its reply — a late `done` applied a stale result, a late `cancelled` threw and Auto-Fit rolled back over the newer fit | `_serverFitJob` rechecks `_fitOpCurrent(op)` after every await and before every exit, and its outer catch turns ANY error of a superseded operation (incl. the Auto-Fit timeout) into `{ _abandoned: 'superseded' }`; both callers' catch paths check it first (runFit: no local fallback; Auto-Fit: no rollback, no message) |
| 3 | MINOR: if the heartbeat thread failed to start after the fit thread had, the admission was released twice (seven outstanding against six) | the heartbeat thread starts FIRST; a failure to start either thread raises before the worker runs (the route releases once); once the worker has started only its finally releases. Fault-injection test fails on round 1's code, passes now. |

Tests: the reproductions as JS tests (response-order reversal; a poll in
flight when a newer claim arrives, for a late `done`, `cancelled` and
`error`; an Auto-Fit timeout after a newer claim) and the callers claim
before their first code await.
