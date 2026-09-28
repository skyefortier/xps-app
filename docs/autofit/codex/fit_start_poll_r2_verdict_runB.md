OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0e227-4d3e-73c3-9906-468badea171a
--------
user
Re-review unit 2 (long fits via start-then-poll), round 2: branch fix-fit-start-poll (stacked on fix-acceptance-holes, F2). The round-1 fixes are the latest commit on this branch that is not a merge of fix-acceptance-holes; review git diff fix-acceptance-holes..HEAD for the whole unit. Round-1 verdicts: docs/autofit/codex/fit_start_poll_verdict_run{A,B}.md; the round-1 prompt (brief, design, sites, acceptance): docs/autofit/codex/fit_start_poll_review_prompt.txt. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

ROUND-1 FINDINGS AND FIXES (plan section 6, verbatim):

**Round 1 — NO-GO ×2** (`fit_start_poll_verdict_run{A,B}.md`; the same four
findings in both):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR: a re-run did not supersede — Ctrl/Cmd+F calls `runFit` past the disabled button; two jobs for one tab, the older could finish first and get the newer discarded as "model edited" | `_fitJobByOwner` (WeakMap keyed by the tab record): a new start for the same tab cancels the previous job on the server; the superseded loop returns `{ _abandoned: 'superseded' }` and its caller does NOTHING (the new fit owns spinner and result; Auto-Fit does not roll back, which would overwrite the new fit's model). Run Fit and Auto-Fit both pass their tab as `owner`. |
| 2 | MAJOR: unbounded concurrency — a thread per start, where four sync workers used to bound concurrent fits at four | each worker process runs at most `FIT_JOB_MAX_RUNNING` = 1 fit (a semaphore); the rest wait `queued` (heartbeating, cancellable, a queued job cancelled or abandoned never runs); at most `FIT_JOB_MAX_ADMITTED` = 6 running + queued per process, beyond that `/api/fit/start` answers 503 "The server is busy with other fits" at once (the page shows it as a failed fit). Production: ≤ 4 concurrent fits, as before. |
| 3 | MINOR: a cancellation observed mid-fit could surface as the solver's own error (AttributeError from Levenberg-Marquardt, RuntimeError from Nelder-Mead / DE) — an abandoned job became `error` 500 / 422 | `run_fit(cancel=)` turns any exception raised after cancellation was observed into `FitCancelled`; unrelated errors propagate unchanged |
| 4 | MINOR: `public_fit_poll_check.py` could poll a dead worker's record forever | a heartbeat older than 30 s is FAIL "lost"; a 20-minute deadline per target (the job is cancelled) |



TRY TO BREAK
a. Supersede: the WeakMap keyed by the tab record — is the SAME object passed by Run Fit, "Use this solution" (runFit({startPeaks})) and Auto-Fit; a superseded Auto-Fit that had already built its model and provisional shift (is leaving it correct?); a superseded Run Fit whose successor then fails; the spinner (who hides it); two tabs fitting at once (not superseded); the pagehide beacon; the ownership-reason order (superseded checked before tab/model).
b. Concurrency: the per-process semaphore + admission counter — can the counter leak (an exception between admit and the worker's finally; a worker thread that never starts), can a queued job starve, is the 'queued' status handled by every page path (heartbeat, abandonment, the acceptance script), does a 503 at start reach the page as a failed fit with the message (not a transport failure / local fallback), do polls stay fast while a fit runs in the same process (GIL); is 1 running per process too low (four students in parallel = four fits, as before; a fifth waits)?
c. Cancellation normalisation: FitCancelled only when cancellation was observed; an unrelated exception during a cancel-enabled fit still reports its own error; the thread-local cleared on every path.
d. Anything round 1 verified that these changes touched; the merged F2 changes (only its documents and one scanner line).
e. Tests: real, non-vacuous.

Finish with VERDICT: GO or VERDICT: NO-GO.
codex
I’ll read the round-1 reviews and full unit diff, then probe supersession, queueing, cancellation, and test coverage. I’ll keep the review read-only and finish with a verdict.
exec
/bin/zsh -lc "pwd; git status --short; rg --files -g AGENTS.md -g '*fit_start_poll*' -g '*fit*job*' -g '*fit*poll*'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-yMeLCNB2' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Ki6RcZ5r' (errno=Operation not permitted)
?? docs/autofit/codex/fit_start_poll_r2_verdict_runA.md
?? docs/autofit/codex/fit_start_poll_r2_verdict_runB.md
scripts/public_fit_poll_check.py
docs/superpowers/plans/2026-09-27-long-fits-start-poll.md
tests/test_fit_start_poll.py
tests/js/fit_start_poll.test.js
docs/autofit/codex/fit_start_poll_recheck_prompt.txt
docs/autofit/codex/fit_start_poll_r2_verdict_runB.md
docs/autofit/codex/fit_start_poll_verdict_runA.md
docs/autofit/codex/fit_start_poll_review_prompt.txt
docs/autofit/codex/fit_start_poll_r2_verdict_runA.md
docs/autofit/codex/fit_start_poll_verdict_runB.md

exec
/bin/zsh -lc 'cat docs/autofit/codex/fit_start_poll_review_prompt.txt docs/autofit/codex/fit_start_poll_verdict_runA.md docs/autofit/codex/fit_start_poll_verdict_runB.md; for p in /AGENTS.md /Users/AGENTS.md /Users/skyefortier/AGENTS.md /Users/skyefortier/xps-app/AGENTS.md /Users/skyefortier/xps-app/.claude/AGENTS.md /Users/skyefortier/xps-app/.claude/worktrees/AGENTS.md; do if test -f "$p"; then cat "$p"; fi; done' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
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

Finish with VERDICT: GO or VERDICT: NO-GO.OpenAI Codex v0.153.4
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
OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0e1e8-681e-7251-a1a9-78a5b1031bd0
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
I’ll compare the branch against `fix-acceptance-holes`, check the server and browser failure paths, and run focused tests within the read-only constraint. I’ll finish with ranked findings and a verdict.

exec
/bin/zsh -lc "pwd && rg --files -g 'AGENTS.md' -g 'CLAUDE.md' -g '*fit_start_poll*' -g '*fit_poll_check*' && git status --short && git diff --stat fix-acceptance-holes..HEAD" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
CLAUDE.md
scripts/public_fit_poll_check.py
tests/test_fit_start_poll.py
tests/js/fit_start_poll.test.js
docs/autofit/codex/fit_start_poll_verdict_runB.md
docs/autofit/codex/fit_start_poll_review_prompt.txt
docs/autofit/codex/fit_start_poll_verdict_runA.md
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-fVpk6yb1' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-TmsOq7Hn' (errno=Operation not permitted)
?? docs/autofit/codex/fit_start_poll_verdict_runA.md
?? docs/autofit/codex/fit_start_poll_verdict_runB.md
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-T0rt8l8T' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-vcNN2l8A' (errno=Operation not permitted)
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
git: error: couldn't create cache file '/tmp/xcrun_db-PfgbKA0y' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-yjb7Nqpd' (errno=Operation not permitted)
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
/bin/zsh -lc 'cat tests/test_fit_start_poll.py tests/js/fit_start_poll.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
"""Unit 2 (2026-09-27): long fits via start-then-poll.

/api/fit/start validates exactly as /api/fit, runs the SAME run_fit in a
background thread on Find Peaks' job records, and the page polls
/api/fit/progress. Pinned here: a polled fit is the synchronous fit (same
body; byte-identical for Levenberg-Marquardt); every validation error is
immediate and word-for-word the same; a run_fit error becomes the same
message and status in the record; cancel (explicit, or no poll for
FIT_JOB_ABANDON_SEC) stops the fit within seconds; the heartbeat; every poll
is a short request.
"""

import io
import json
import time

import numpy as np
import pytest

import app as app_module
from app import create_app


def _gl(x, c, a, w):
    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)


@pytest.fixture()
def client(tmp_path):
    a = create_app(upload_folder=str(tmp_path))
    a.config["TESTING"] = True
    with a.test_client() as c:
        yield c


def _upload(client, n=200, comps=((284.5, 5000, 0.9), (286.2, 1500, 1.1)), seed=3):
    rng = np.random.default_rng(seed)
    x = np.linspace(281.0, 292.0, n)
    y = rng.poisson(300 + sum(_gl(x, c, a, w) for c, a, w in comps)).astype(float)
    csv = "\n".join(f"{a:.4f},{b:.1f}" for a, b in zip(x, y))
    r = client.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "s.csv")})
    assert r.status_code == 200, r.get_json()
    return r.get_json()["session_id"]


def _specs(comps):
    return [{"id": str(i + 1), "shape": "pseudo_voigt_gl", "center": c + 0.1, "fwhm": w * 1.1, "amplitude": a * 0.8,
             "gl_ratio": 0.3, "amplitude_min": 0} for i, (c, a, w) in enumerate(comps)]


def _body(sid, comps, method="leastsq", **extra):
    return {"session_id": sid, "background": {"method": "shirley"}, "peaks": _specs(comps),
            "fit_method": method, "n_perturb": 1, "n_starts": 0, **extra}


def _poll(client, job_id, limit=300.0):
    t0, longest = time.time(), 0.0
    while True:
        q0 = time.time()
        r = client.get(f"/api/fit/progress/{job_id}")
        longest = max(longest, time.time() - q0)
        assert r.status_code == 200
        rec = json.loads(r.get_data(as_text=True))
        if rec["status"] != "running":
            return rec, longest
        assert time.time() - t0 < limit, "job did not finish"
        time.sleep(0.2)


COMPS = ((284.5, 5000, 0.9), (286.2, 1500, 1.1))


def test_a_polled_fit_is_the_synchronous_fit_byte_for_byte(client):
    sid = _upload(client)
    sync = client.post("/api/fit", json=_body(sid, COMPS))
    assert sync.status_code == 200
    start = client.post("/api/fit/start", json=_body(sid, COMPS))
    assert start.status_code == 202
    rec, longest = _poll(client, start.get_json()["job_id"])
    assert rec["status"] == "done"
    # Levenberg-Marquardt is byte-identical request to request (CLAUDE.md): same seed, same body
    assert json.dumps(rec["result"], sort_keys=True) == json.dumps(sync.get_json(), sort_keys=True)
    assert longest < 2.0, f"a poll took {longest:.2f} s"


@pytest.mark.parametrize("method", ["differential_evolution", "basinhopping", "least_squares"])
def test_the_stochastic_and_default_methods_give_the_synchronous_answer(client, method):
    sid = _upload(client)
    body = _body(sid, COMPS, method=method, n_perturb=0)
    sync = client.post("/api/fit", json=body).get_json()
    rec, _ = _poll(client, client.post("/api/fit/start", json=body).get_json()["job_id"])
    res = rec["result"]
    assert res["random_seed"] == sync["random_seed"]
    assert res["success"] == sync["success"] is True
    # Trust-Region (also DE's and basinhopping's refinement) is not bit-reproducible
    # across calls (BLAS alignment, CLAUDE.md); the answer is the same fit
    assert res["statistics"]["reduced_chi_square"] == pytest.approx(sync["statistics"]["reduced_chi_square"], rel=1e-6)


@pytest.mark.parametrize("patch,status,fragment", [
    ({"n_perturb": 101}, 400, "n_perturb must be between"),
    ({"fit_method": "ampgo"}, 400, "Unknown fit_method"),
    ({"peaks": []}, 400, "'peaks' list is empty"),
    ({"session_id": "0" * 32}, 404, "not found"),
])
def test_a_bad_request_is_refused_immediately_and_identically(client, patch, status, fragment):
    sid = _upload(client)
    body = {**_body(sid, COMPS), **patch}
    a = client.post("/api/fit", json=body)
    b = client.post("/api/fit/start", json=body)
    assert a.status_code == b.status_code == status
    assert a.get_json() == b.get_json()
    assert fragment in b.get_json()["error"]


def test_a_run_fit_refusal_reaches_the_record_with_the_synchronous_message_and_status(client):
    sid = _upload(client, n=6)                                    # 8 free parameters, 6 points (unit F2)
    body = {**_body(sid, COMPS), "n_perturb": 0}
    sync = client.post("/api/fit", json=body)
    rec, _ = _poll(client, client.post("/api/fit/start", json=body).get_json()["job_id"])
    assert rec["status"] == "error"
    assert rec["http_status"] == sync.status_code == 400
    assert rec["error"] == sync.get_json()["error"]


SLOW = ((283.2, 2000, 0.8), (284.5, 5000, 0.9), (285.4, 1800, 1.0), (286.6, 1500, 1.1), (288.4, 900, 1.4))


def test_cancel_stops_a_running_fit_within_seconds(client):
    sid = _upload(client, n=300, comps=SLOW)
    job = client.post("/api/fit/start", json=_body(sid, SLOW, method="basinhopping", n_perturb=0)).get_json()["job_id"]
    time.sleep(1.0)
    rec = json.loads(client.get(f"/api/fit/progress/{job}").get_data(as_text=True))
    assert rec["status"] == "running", "the fixture must still be running when cancelled"
    t0 = time.time()
    assert client.post(f"/api/fit/cancel/{job}").status_code == 200
    rec, _ = _poll(client, job, limit=30)
    assert rec["status"] == "cancelled"
    assert time.time() - t0 < 10, f"cancel took {time.time() - t0:.1f} s"


def test_an_abandoned_job_stops_itself_when_polls_stop(client, monkeypatch):
    monkeypatch.setattr(app_module, "FIT_JOB_ABANDON_SEC", 1.5)
    sid = _upload(client, n=300, comps=SLOW)
    job = client.post("/api/fit/start", json=_body(sid, SLOW, method="basinhopping", n_perturb=0)).get_json()["job_id"]
    time.sleep(6.0)                                               # nobody polls
    rec = json.loads(client.get(f"/api/fit/progress/{job}").get_data(as_text=True))
    assert rec["status"] == "cancelled", rec["status"]


def test_the_heartbeat_moves_while_the_fit_runs(client):
    sid = _upload(client, n=300, comps=SLOW)
    job = client.post("/api/fit/start", json=_body(sid, SLOW, method="basinhopping", n_perturb=0)).get_json()["job_id"]
    time.sleep(4.5)
    rec = json.loads(client.get(f"/api/fit/progress/{job}").get_data(as_text=True))
    assert rec["status"] == "running"
    assert rec["heartbeat_age_sec"] is not None and rec["heartbeat_age_sec"] < 3.0
    assert rec["elapsed_sec"] >= 2.0
    client.post(f"/api/fit/cancel/{job}")
    _poll(client, job, limit=30)


def test_unknown_and_malformed_job_ids(client):
    assert client.get("/api/fit/progress/not-a-uuid").status_code == 400
    assert client.get("/api/fit/progress/00000000-0000-0000-0000-000000000000").status_code == 404
    assert client.post("/api/fit/cancel/not-a-uuid").status_code == 400


def test_a_non_finite_result_reaches_the_page_unsanitised(tmp_path):
    # the page's _readFitReply refuses NaN as a failed fit (unit F2): the job
    # record must carry it exactly as /api/fit would, never as null
    app_module._fit_job_write("11111111-1111-1111-1111-111111111111", str(tmp_path),
                              {"status": "done", "result": {"x": float("nan")}})
    text = (tmp_path / "11111111-1111-1111-1111-111111111111.job.json").read_text()
    assert "NaN" in text
// Unit 2 (2026-09-27): Run Fit and Auto-Fit start the fit and poll for it
// (_serverFitJob). Pinned: the result is the /api/fit body; a bad request's
// message and status are the synchronous route's; ownership (a switched tab,
// an edited model) cancels the server's job and discards; transport keeps its
// meaning (a START that cannot reach the server may fall back to the local
// engine; one lost poll does not; five in a row do); a lost heartbeat, a
// cancelled or errored record are failed fits; F2's NaN rule applies to the
// final record; the 2-minute Auto-Fit abort cancels the job.
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
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
const constLine = n => { const l = lines.find(x => x.startsWith('const ' + n)); assert.ok(l, n); return l; };

// fetch scripted by URL; every call recorded
function server(script) {
  const calls = [];
  const fetch = async (url, init) => {
    calls.push({ url, method: (init && init.method) || 'GET' });
    const h = script(url, init, calls);
    if (h instanceof Error) throw h;
    return h;
  };
  return { fetch, calls };
}
const ok = (obj, status = 200) => ({ ok: true, status, text: async () => (typeof obj === 'string' ? obj : JSON.stringify(obj)) });
const bad = (status, obj) => ({ ok: false, status, json: async () => { if (obj === undefined) throw new SyntaxError('x'); return obj; } });

function make(fetch) {
  const src = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
    'const _runningFitJobs = new Set();',
    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
  return new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob, _runningFitJobs };')(
    fetch, f => f(), class extends Error { constructor(m, n) { super(m); this.name = n; } });
}
const START = '/api/fit/start';
const isProgress = u => u.startsWith('/api/fit/progress/');
const isCancel = u => u.startsWith('/api/fit/cancel/');

test('start -> running polls -> done: the result is the /api/fit body; no job is left registered', async () => {
  let n = 0;
  const s = server(u => u === START ? ok({ job_id: 'J' }, 202)
    : isProgress(u) ? (++n < 3 ? ok({ status: 'running', heartbeat_age_sec: 0.4 }) : ok({ status: 'done', result: { success: true, x: 1 } }))
    : ok({}));
  const { _serverFitJob, _runningFitJobs } = make(s.fetch);
  assert.deepStrictEqual(await _serverFitJob({ a: 1 }, {}), { success: true, x: 1 });
  assert.strictEqual(s.calls.filter(c => isProgress(c.url)).length, 3);
  assert.strictEqual(_runningFitJobs.size, 0);
  assert.ok(!s.calls.some(c => isCancel(c.url)), 'a finished job is not cancelled');
});

test('a bad request: the synchronous route\'s message and status, immediately; no poll', async () => {
  const s = server(u => u === START ? bad(400, { error: 'n_perturb must be between 0 and 10' }) : assert.fail(u));
  const { _serverFitJob } = make(s.fetch);
  await assert.rejects(_serverFitJob({}, {}), e => e.serverError && e.httpStatus === 400 && /n_perturb must be between/.test(e.message));
});

test('a START that cannot reach the server is a transport failure (the caller may fall back to the local engine)', async () => {
  const s = server(u => new TypeError('Failed to fetch'));
  const { _serverFitJob } = make(s.fetch);
  await assert.rejects(_serverFitJob({}, {}), e => e.transportFailure === true && !e.serverError);
});

test('an error record is a failed fit with the synchronous message and status', async () => {
  const s = server(u => u === START ? ok({ job_id: 'J' }, 202)
    : ok({ status: 'error', http_status: 400, error: 'The model is not determined by these data: 8 free parameters for 6 data points' }));
  const { _serverFitJob } = make(s.fetch);
  await assert.rejects(_serverFitJob({}, {}), e => e.serverError && e.httpStatus === 400 && /not determined by these data/.test(e.message));
});

test('a done record carrying NaN is F2\'s failed fit (unreadable reply), not a transport failure', async () => {
  const s = server(u => u === START ? ok({ job_id: 'J' }, 202)
    : isProgress(u) ? ok('{"status": "done", "result": {"success": true, "s": NaN}}') : ok({}));
  const { _serverFitJob } = make(s.fetch);
  await assert.rejects(_serverFitJob({}, {}), e => e.unreadableReply === true && e.serverError && !e.transportFailure && /non-finite/.test(e.message));
});

test('one lost poll is retried; five in a row are a transport failure and cancel the job', async () => {
  let n = 0;
  const flaky = server(u => u === START ? ok({ job_id: 'J' }, 202)
    : isProgress(u) ? (++n <= 4 ? new TypeError('network') : ok({ status: 'done', result: { success: true } })) : ok({}));
  assert.deepStrictEqual(await make(flaky.fetch)._serverFitJob({}, {}), { success: true });
  const dead = server(u => u === START ? ok({ job_id: 'J' }, 202) : isProgress(u) ? new TypeError('network') : ok({}));
  await assert.rejects(make(dead.fetch)._serverFitJob({}, {}), e => e.transportFailure === true && /Lost contact/.test(e.message));
  assert.ok(dead.calls.some(c => isCancel(c.url) && c.method === 'POST'), 'the server is told to stop');
});

test('a stopped heartbeat (restarted worker) is a failed fit, never an endless spinner', async () => {
  const s = server(u => u === START ? ok({ job_id: 'J' }, 202) : isProgress(u) ? ok({ status: 'running', heartbeat_age_sec: 45 }) : ok({}));
  await assert.rejects(make(s.fetch)._serverFitJob({}, {}), e => e.serverError && /stopped working on the fit/.test(e.message));
});

test('a job cancelled on the server (abandoned) is reported, not waited for', async () => {
  const s = server(u => u === START ? ok({ job_id: 'J' }, 202) : ok({ status: 'cancelled' }));
  await assert.rejects(make(s.fetch)._serverFitJob({}, {}), e => e.serverError && /stopped on the server/.test(e.message));
});

test('ownership inside the loop: a switched tab or an edited model cancels the job and returns the reason', async () => {
  for (const reason of ['tab', 'model']) {
    let polls = 0;
    const s = server(u => u === START ? ok({ job_id: 'J' }, 202) : isProgress(u) ? (polls++, ok({ status: 'running', heartbeat_age_sec: 0 })) : ok({}));
    let t = 0;
    const out = await make(s.fetch)._serverFitJob({}, { abandoned: () => (++t > 2 ? reason : null) });
    assert.deepStrictEqual(out, { _abandoned: reason });
    assert.ok(s.calls.some(c => isCancel(c.url) && c.method === 'POST'), reason + ': the server is told to stop');
    assert.strictEqual(polls, 2, 'no poll after the model or tab changed');
  }
});

test('the Auto-Fit abort (2 minutes) cancels the job and surfaces as an AbortError', async () => {
  const ctrl = { aborted: false, reason: null };
  let polls = 0;
  const s = server(u => u === START ? ok({ job_id: 'J' }, 202) : isProgress(u) ? (++polls === 2 && (ctrl.aborted = true, ctrl.reason = Object.assign(new Error('timeout'), { name: 'AbortError' })), ok({ status: 'running', heartbeat_age_sec: 0 })) : ok({}));
  await assert.rejects(make(s.fetch)._serverFitJob({}, { signal: ctrl }), e => e.name === 'AbortError');
  assert.ok(s.calls.some(c => isCancel(c.url)));
});

test('Run Fit and Auto-Fit both go through _serverFitJob; nothing on the page posts to the synchronous /api/fit any more', () => {
  assert.match(extractFn('runFit'), /await _serverFitJob\(fitReq, \{/);
  assert.match(extractFn('runAutoFitC1sGraphite'), /await _serverFitJob\(\{/);
  assert.ok(!/fetch\('\/api\/fit'/.test(html), 'no synchronous /api/fit fetch left');
  // the ownership reasons are the ones the discard messages handle
  for (const fn of ['runFit', 'runAutoFitC1sGraphite']) {
    const src = extractFn(fn);
    assert.match(src, /_abandoned === 'tab'/, fn);
    assert.match(src, /_abandoned === 'model'/, fn);
  }
  assert.match(html, /addEventListener\('pagehide'/, 'a closed page cancels its running fits');
});

exec
/bin/zsh -lc 'git diff fix-acceptance-holes..HEAD -- app.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-NQq7cPc5' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ksnYgElQ' (errno=Operation not permitted)
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

exec
/bin/zsh -lc 'git diff fix-acceptance-holes..HEAD -- templates/index.html' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-CS4thyF2' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-8wjvoZpo' (errno=Operation not permitted)
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

exec
/bin/zsh -lc 'git diff fix-acceptance-holes..HEAD -- templates/index.html tests/js/fit_acceptance.test.js tests/js/stale_statistics.test.js tests/js/per_tab_state.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-St7Z6HwF' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-6iNXxCma' (errno=Operation not permitted)
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
diff --git a/tests/js/fit_acceptance.test.js b/tests/js/fit_acceptance.test.js
index fef5ee5..15dfed0 100644
--- a/tests/js/fit_acceptance.test.js
+++ b/tests/js/fit_acceptance.test.js
@@ -31,6 +31,32 @@ function extractFn(name) {
   assert.fail('unbalanced ' + name);
 }
 
+// Unit 2: Run Fit starts the fit and polls for it (_serverFitJob). These
+// tests script the single /api/fit reply they always did; jobAdapter serves
+// that reply as a finished job (start -> 202 + id; progress -> done + result),
+// and a start that throws is still a transport failure.
+const POLL_SRC = [constLineOf('FIT_POLL_MS'), constLineOf('FIT_POLL_TRANSPORT_RETRIES'), constLineOf('FIT_HEARTBEAT_LOST_SEC'),
+  'const _runningFitJobs = new Set();', ...['_cancelFitJob', '_fitHttpError', '_serverFitJob'].map(n => extractFn(n))].join('\n');
+function constLineOf(n) { const l = lines.find(x => x.startsWith('const ' + n)); assert.ok(l, n); return l; }
+function jobAdapter(fetchImpl) {
+  let reply = null;
+  return async (url, init) => {
+    if (url === '/api/fit/start') {
+      const r = await fetchImpl('/api/fit', init);
+      if (r && r.ok === false) return r;
+      reply = r;
+      return { ok: true, status: 202, text: async () => JSON.stringify({ job_id: 'job-1' }) };
+    }
+    if (url.startsWith('/api/fit/progress/')) {
+      const r = reply;
+      return { ok: true, status: 200, text: async () => '{"status": "done", "result": ' + (await r.text()) + '}' };
+    }
+    if (url.startsWith('/api/fit/cancel/')) return { ok: true, status: 200, json: async () => ({}) };
+    return fetchImpl(url, init);
+  };
+}
+const immediate = f => { f(); return 0; };
+
 function makeEnv({ fetchImpl, uploadImpl, specImpl, ownerActive }) {
   const dom = {};
   const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, disabled: false,
@@ -41,14 +67,14 @@ function makeEnv({ fetchImpl, uploadImpl, specImpl, ownerActive }) {
     peaks: [{ id: 1, name: 'p', shape: 'Gaussian', center: 285, fwhm: 1.2, amplitude: 50, glMix: 50, asymmetry: 0 }] };
   const owner = { id: 7 };
   const calls = { notify: [], local: 0, applied: 0 };
-  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n');
-  const factory = new Function('document', 'state', 'fetch', 'uploadToBackend', 'notify', 'pushUndo', '_showFitSpinner', '_hideFitSpinner',
+  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n') + '\n' + POLL_SRC;
+  const factory = new Function('setTimeout', 'document', 'state', 'fetch', 'uploadToBackend', 'notify', 'pushUndo', '_showFitSpinner', '_hideFitSpinner',
     '_opOwner', '_ownerActive', 'getROIData', 'computeBackground', 'peakToBackendSpec', '_getManualAnchors', 'applyBackendResult',
     '_computeRFactor', '_CHISQ_TOOLTIP', '_updateRFactorUI', '_updateROIDisplay', 'renderPeakList', 'updatePlot', 'renderResults',
     '_autoSnapshot', 'runFitLocal', '_snapshotSuppressed', 'console', '_applyStatDisplay', '_activeTab',
     src + '\nreturn { runFit };');
   const noop = () => {};
-  const { runFit } = factory(document, state, withText(fetchImpl), uploadImpl || (async () => 'sid'), (msg, kind) => calls.notify.push({ msg, kind }),
+  const { runFit } = factory(immediate, document, state, jobAdapter(withText(fetchImpl)), uploadImpl || (async () => 'sid'), (msg, kind) => calls.notify.push({ msg, kind }),
     noop, noop, noop, () => owner, ownerActive || (o => o === owner), () => ({ be: state.rawBE.slice(), inten: state.rawIntensity.slice() }),
     b => b.map(() => 0), specImpl || (p => ({ id: p.id, shape: 'gaussian' })), () => [], () => { calls.applied++; },
     () => 0.1, '', noop, noop, noop, noop, noop, noop,
@@ -104,7 +130,7 @@ test('a transport failure whose local fallback does NOT converge shows no "local
   failing.calls.local = 0;
   // rebuild with a failing runFitLocal
   const dom = failing.dom;
-  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n');
+  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n') + '\n' + POLL_SRC;
   const noop = () => {};
   const owner = { id: 1 };
   const state = failing.state;
diff --git a/tests/js/per_tab_state.test.js b/tests/js/per_tab_state.test.js
index 7c50461..6a77d10 100644
--- a/tests/js/per_tab_state.test.js
+++ b/tests/js/per_tab_state.test.js
@@ -34,6 +34,7 @@ const ALLOWLIST = {
   _ssFocusIdx: 'A', _ssFiltered: 'A',
   _fpMeta: 'B', _fpModalDrag: 'A', _fpRegionsSelected: 'A', _fpExpandedElement: 'A',
   _findPeaksApplyConfirmResolver: 'A',
+  _runningFitJobs: 'A',       // unit 2: ids of in-flight server fit jobs, for the pagehide cancel beacon — no spectrum content
   _undoDebounce: 'A',         // burst buffer: DOES hold a peaks snapshot, but bound to its owner record at burst start and flushed onto that record only — the async-ownership exception to class A's 'no spectrum content'
   // Populated constant catalogues (read-only tables) and the chart plugin
   // object: class B. Listed, not skipped, so a per-tab store hidden in an
diff --git a/tests/js/stale_statistics.test.js b/tests/js/stale_statistics.test.js
index 3b36b46..7ab1cb8 100644
--- a/tests/js/stale_statistics.test.js
+++ b/tests/js/stale_statistics.test.js
@@ -301,6 +301,31 @@ test('the refresh re-renders Results only when its rendered state differs', () =
   assert.strictEqual(env.renders, 2, 'current again');
 });
 
+// Unit 2: Auto-Fit starts the fit and polls for it (_serverFitJob). Each
+// sandbox scripts the single /api/fit reply it always did; pollify serves it
+// as a finished job, and runs the poll loop's short waits at once (the
+// 2-minute Auto-Fit timer is left pending, as before).
+const POLL_SRC = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
+  'const _runningFitJobs = new Set();', ...['_cancelFitJob', '_fitHttpError', '_serverFitJob'].map(extractFn)].join('\n');
+function pollify(deps) {
+  const inner = deps.fetch;
+  let reply = null;
+  deps.fetch = async (url, init) => {
+    if (url === '/api/fit/start') {
+      const r = await inner('/api/fit', init);
+      if (r && r.ok === false) return r;
+      reply = r;
+      return { ok: true, status: 202, text: async () => JSON.stringify({ job_id: 'job-1' }) };
+    }
+    if (url.startsWith('/api/fit/progress/')) return { ok: true, status: 200, text: async () => '{"status": "done", "result": ' + (await reply.text()) + '}' };
+    if (url.startsWith('/api/fit/cancel/')) return { ok: true, status: 200, json: async () => ({}) };
+    return inner(url, init);
+  };
+  deps.setTimeout = (f, ms) => { if (!(ms >= 60000)) f(); return 1; };
+  deps.DOMException = class extends Error { constructor(m, n) { super(m); this.name = n; } };
+  return deps;
+}
+
 // ── Codex round 1 ───────────────────────────────────────────────────────────
 function keyFns() {
   const src = lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n')
@@ -379,7 +404,7 @@ test('Auto-Fit discards (and rolls back) a response when the model or context wa
       fetch: async () => ({ text: async () => JSON.stringify({ success: true, statistics: { reduced_chi_square: 1 }, fitted_y: [10, 20, 10], residuals: [0, 0, 0] }) }),
       applyBackendResult: () => { out.applied++; }, applyAutoFitResult: () => true };
     const src = constants + '\n' + ['runAutoFitC1sGraphite', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
-    await new Function(...Object.keys(deps), src + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
+    await new Function(...Object.keys(pollify(deps)), src + '\n' + POLL_SRC + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
     return out;
   };
   const edited = await run(true);
@@ -424,7 +449,7 @@ test('F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply mes
     fetch: async () => ({ text: async () => '{"success": true, "statistics": {"reduced_chi_square": NaN}}' }),
     applyBackendResult: () => { out.applied++; }, applyAutoFitResult: () => true, console: { warn() {} } };
   const src = constants + '\n' + ['runAutoFitC1sGraphite', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
-  await new Function(...Object.keys(deps), src + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
+  await new Function(...Object.keys(pollify(deps)), src + '\n' + POLL_SRC + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
   assert.strictEqual(out.applied, 0);
   assert.strictEqual(out.restored, true);
   assert.ok(out.notes.some(([m, k]) => k === 'red' && /^Auto-fit failed: .*non-finite number/.test(m)), JSON.stringify(out.notes));
@@ -451,7 +476,7 @@ for (const [label, reply, expect] of [
     fetch: async () => reply,
     applyBackendResult: () => { out.applied++; }, applyAutoFitResult: () => true, console: { warn() {} } };
   const src = constants + '\n' + ['runAutoFitC1sGraphite', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
-  await new Function(...Object.keys(deps), src + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
+  await new Function(...Object.keys(pollify(deps)), src + '\n' + POLL_SRC + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
   assert.strictEqual(out.applied, 0);
   assert.strictEqual(out.restored, true);
   assert.ok(out.notes.some(([m, k]) => k === 'red' && expect.test(m)), JSON.stringify(out.notes));

codex
The validation extraction and record locking look consistent with the design. I’m checking cancellation and overlapping runs next; the added tests mostly cover one job at a time, so they don’t establish what happens when a fit is superseded.

exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '7550,7775p;8050,8350p'; rg -n 'runFit\\(|runAutoFitC1sGraphite\\(|_showFitSpinner|_hideFitSpinner|_opOwner|_ownerActive' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
  7550	      }
  7551	      if (typeof guard.onProgress === 'function') guard.onProgress(rec);
  7552	    }
  7553	  } finally {
  7554	    _runningFitJobs.delete(jobId);
  7555	  }
  7556	}
  7557	
  7558	async function runAutoFitC1sGraphite() {
  7559	  // Pre-conditions
  7560	  if (!state.rawBE || !state.rawBE.length) { notify('Load a spectrum first.', 'amber'); return; }
  7561	  const tab = tabManager._getTab(tabManager.activeId);
  7562	  if (!tab) { notify('No active tab.', 'amber'); return; }
  7563	  if (!isC1sTab(tab)) {
  7564	    notify('Auto-Fit C1s Graphite is only available for C1s spectra (ROI midpoint 270–315 eV).', 'amber');
  7565	    return;
  7566	  }
  7567	  // OWNER FIRST: the confirmation below is an await; the tab that is active
  7568	  // when it resolves may not be the one the user asked to auto-fit.
  7569	  const fittingTab = _opOwner();
  7570	  if (!fittingTab) { notify('No active spectrum tab.', 'amber'); return; }
  7571	  // Confirmation if existing peaks
  7572	  if (state.peaks.length >= 1) {
  7573	    const proceed = await _showAutoFitConfirmModal(state.peaks.length);
  7574	    if (!proceed) return;
  7575	    if (!_ownerActive(fittingTab)) {
  7576	      notify('Auto-fit cancelled — the tab changed while the confirmation was open.', 'amber');
  7577	      return;
  7578	    }
  7579	  }
  7580	
  7581	  // Snapshot for failure rollback (separate from pushUndo, which only covers peaks).
  7582	  const snap = _autoFitSnapshot();
  7583	
  7584	  // Step 1: find graphite in raw BE
  7585	  const { be: corrBE, inten } = getROIData();
  7586	  if (!corrBE.length) {
  7587	    notify('ROI is empty. Set roi-min and roi-max before auto-fit.', 'red', true);
  7588	    return;
  7589	  }
  7590	  const bgI = computeBackground(corrBE, inten);
  7591	  const bgSub = inten.map((v, i) => v - bgI[i]);
  7592	  // App convention: raw = corrected + state.ccShift
  7593	  const curShift = Number.isFinite(state.ccShift) ? state.ccShift : 0;
  7594	  const rawBE = corrBE.map(b => b + curShift);
  7595	  const graphiteRaw = findGraphiteRawBE(rawBE, bgSub);
  7596	  if (graphiteRaw == null) {
  7597	    notify('No strong peak found in the C1s ROI; Auto-Fit cannot proceed.', 'red', true);
  7598	    return;
  7599	  }
  7600	
  7601	  // Step 2: provisional shift (APP CONVENTION).
  7602	  const provisionalShift = graphiteRaw - 284.50;
  7603	
  7604	  // Step 3: assess low-BE region using provisional shift (no state mutation yet).
  7605	  const assessment = assessLowBERegion(rawBE, bgSub, provisionalShift);
  7606	
  7607	  // Step 4: build the peak model (in corrected frame after provisional shift).
  7608	  pushUndo();
  7609	  state.peaks = [];
  7610	  state.fitResult = null;
  7611	  // Apply provisional shift via updateChargeCorrection so ROI/bg DOM fields
  7612	  // shift along with state.ccShift.
  7613	  const cm = document.getElementById('cc-method');
  7614	  const co = document.getElementById('cc-obs');
  7615	  const cl = document.getElementById('cc-lit');
  7616	  cm.value = 'c1s';
  7617	  co.value = graphiteRaw.toFixed(3);
  7618	  cl.value = '284.50';
  7619	  updateChargeCorrection();
  7620	  // Now build the peak list (graphite center 284.50 in this frame).
  7621	  const newPeaks = buildAutoFitModel(assessment);
  7622	  state.peaks = newPeaks;
  7623	  state.nextId = Math.max(0, ...state.peaks.map(p => p.id)) + 1;
  7624	  renderPeakList();
  7625	
  7626	  // Step 5: run /api/fit with AbortController + spinner.
  7627	  _showFitSpinner();
  7628	  const spinLabel = document.getElementById('fit-spinner-label');
  7629	  if (spinLabel) spinLabel.textContent = 'Auto-fitting…';
  7630	  const runBtn = document.querySelector('.btn-green');
  7631	  if (runBtn) runBtn.disabled = true;
  7632	
  7633	  const ctrl = new AbortController();
  7634	  const timer = setTimeout(() => ctrl.abort(new DOMException('timeout', 'AbortError')), 120000);
  7635	
  7636	  try {
  7637	    const { be: be2, inten: inten2 } = getROIData();
  7638	    const bgType = document.getElementById('bg-type').value;
  7639	    const bgStart = parseFloat(document.getElementById('bg-start').value);
  7640	    const bgEnd = parseFloat(document.getElementById('bg-end').value);
  7641	    // Inclusive bg window — the same point set computeBackgroundCore draws;
  7642	    // the backend slices end-exclusive, so the request sends i1 + 1.
  7643	    const bgWin = _bgWindowIndices(be2, bgStart, bgEnd);
  7644	    const epAvg = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
  7645	    const fitMethod = document.getElementById('fit-method').value;
  7646	
  7647	    // The anchor whose necessity the server must test — captured with the
  7648	    // other request inputs, before the first await (a tab switch during the
  7649	    // upload must not send another tab's id).
  7650	    const anchorId = String((state.peaks.find(p => p.name === 'Graphite') || state.peaks[0]).id);
  7651	    // the model and its fit context as sent (F1, Codex round 1): a result must
  7652	    // not be applied, and stamped current, over a model edited while it ran
  7653	    const ctxAtRequest = _startsLiveKey();
  7654	    // Build peak specs and overlay the per-peak bounds we attached in buildAutoFitModel.
  7655	    const peakSpecs = state.peaks.map(p => {
  7656	      const spec = peakToBackendSpec(p);
  7657	      if (Number.isFinite(p._afCenterMin)) spec.center_min = p._afCenterMin;
  7658	      if (Number.isFinite(p._afCenterMax)) spec.center_max = p._afCenterMax;
  7659	      if (Number.isFinite(p._afFwhmMin))   spec.fwhm_min   = p._afFwhmMin;
  7660	      if (Number.isFinite(p._afFwhmMax))   spec.fwhm_max   = p._afFwhmMax;
  7661	      spec.amplitude_min = 0;
  7662	      return spec;
  7663	    });
  7664	
  7665	    const bgPayload = { method: bgType, start_idx: bgWin.i0, end_idx: bgWin.i1 + 1, endpoint_avg: epAvg };
  7666	    if (bgType === 'manual') {
  7667	      // Anchors are stored in corrected-BE space, same frame as the uploaded
  7668	      // session data; backend expects [x, y] pairs.
  7669	      bgPayload.manual_bg = _getManualAnchors().map(a => [a.x, a.y]);
  7670	    }
  7671	    const sessionId = await uploadToBackend(be2, inten2);   // after EVERY input above is captured
  7672	    // Unit 2: started and polled, like Run Fit (the 2-minute abort still applies)
  7673	    const json = await _serverFitJob({
  7674	        session_id: sessionId,
  7675	        background: bgPayload,
  7676	        peaks: peakSpecs,
  7677	        fit_method: fitMethod,
  7678	        n_perturb: 3,
  7679	        // step (c): is the charge-reference anchor REQUIRED? The server refits
  7680	        // the model without it; a redundant anchor must not set the energy
  7681	        // reference of a whole spectrum (see applyAutoFitResult).
  7682	        require_component: anchorId,
  7683	    }, {
  7684	      signal: ctrl.signal,
  7685	      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
  7686	    });
  7687	    clearTimeout(timer);
  7688	    // F2: a non-2xx reply is a failed REQUEST with its status in the message
  7689	    // (_serverFitJob throws it with httpStatus); an unreadable reply is a
  7690	    // failed fit with its own message (unreadableReply).
  7691	    if (json && json._abandoned === 'tab') {
  7692	      _hideFitSpinner();
  7693	      notify('Auto-fit discarded — tab switched during fit.', 'amber');
  7694	      _autoFitRestore(snap, fittingTab);
  7695	      return;
  7696	    }
  7697	    if (json && json._abandoned === 'model') {
  7698	      _hideFitSpinner();
  7699	      notify('Auto-fit discarded because the model or its background / ROI settings were edited while it was running. Previous peaks and result restored. Run it again.', 'amber', true);
  7700	      _autoFitRestore(snap, fittingTab);
  7701	      return;
  7702	    }
  7703	    if (json.error) throw new Error(json.error);
  7704	    if (json.success !== true) throw new Error(json.message || 'fit did not converge');
  7705	    if (!_ownerActive(fittingTab)) {
  7706	      _hideFitSpinner();
  7707	      notify('Auto-fit discarded — tab switched during fit.', 'amber');
  7708	      _autoFitRestore(snap, fittingTab);
  7709	      return;
  7710	    }
  7711	    if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
  7712	      _hideFitSpinner();
  7713	      notify('Auto-fit discarded because the model or its background / ROI settings were edited while it was running. Previous peaks and result restored. Run it again.', 'amber', true);
  7714	      _autoFitRestore(snap, fittingTab);
  7715	      return;
  7716	    }
  7717	
  7718	    applyBackendResult(json);
  7719	
  7720	    const ok = applyAutoFitResult(json, graphiteRaw, { be: be2, inten: inten2, bgIntensity: bgI, bgSubtracted: bgSub });
  7721	    if (!ok) {
  7722	      _hideFitSpinner();
  7723	      _autoFitRestore(snap, fittingTab);
  7724	      return;
  7725	    }
  7726	
  7727	    _hideFitSpinner();
  7728	    notify('Auto-fit complete. χ²ᵣ = ' + (state.fitResult?.chiReduced?.toFixed(3) || '?'), 'green');
  7729	  } catch (e) {
  7730	    clearTimeout(timer);
  7731	    _hideFitSpinner();
  7732	    // The catch path can also fire after a mid-flight tab switch (fetch
  7733	    // error/timeout after the user moved on) — same wrong-tab hazard as
  7734	    // the explicit discard branch, so it gets the same tab-aware restore.
  7735	    _autoFitRestore(snap, fittingTab);
  7736	    let msg;
  7737	    if (e && (e.name === 'AbortError' || (e.message && e.message.toLowerCase().includes('aborted')))) {
  7738	      msg = 'Auto-fit exceeded the 2-minute timeout.';
  7739	    } else if (e && (e.unreadableReply || e.httpStatus)) {
  7740	      msg = 'Auto-fit failed: ' + e.message;
  7741	    } else if (e && e.message) {
  7742	      msg = 'Fit failed to converge or produced an unphysical graphite position.';
  7743	      console.warn('Auto-fit error:', e);
  7744	    } else {
  7745	      msg = 'Auto-fit failed.';
  7746	    }
  7747	    notify(msg, 'red', true);
  7748	  }
  7749	}
  7750	
  7751	function isC1sTab(tab) {
  7752	  if (!tab || !tab.rawBE || !tab.rawBE.length) return false;
  7753	  const ui = tab.ui || {};
  7754	  let lo = parseFloat(ui.roiMin);
  7755	  let hi = parseFloat(ui.roiMax);
  7756	  if (!Number.isFinite(lo) || !Number.isFinite(hi)) {
  7757	    // Fall back to full raw range (no UI ROI set yet)
  7758	    let rmin = Infinity, rmax = -Infinity;
  7759	    for (const v of tab.rawBE) {
  7760	      if (v < rmin) rmin = v;
  7761	      if (v > rmax) rmax = v;
  7762	    }
  7763	    lo = rmin; hi = rmax;
  7764	  }
  7765	  if (!Number.isFinite(lo) || !Number.isFinite(hi)) return false;
  7766	  const mid = (lo + hi) / 2;
  7767	  return mid >= 270.0 && mid <= 315.0;
  7768	}
  7769	
  7770	// ── Scattered-starts check (2026-09-21) ───────────────────────────────────────
  7771	// Every Run Fit with two or more unlinked components asks the server for three
  7772	// more fits of the SAME method from scattered starts. The student's result
  7773	// stays THE FIT; a solution with a lower reduced chi-square is listed beside it
  7774	// with its own areas and how far each component moved from the student's start
  7775	// (a relocated component must be visible at a glance: on a committed C 1s scan
  8050	  }
  8051	  return peaks;
  8052	}
  8053	
  8054	function _currentAlternative(k) {
  8055	  const st = _startsIfCurrent(state.fitResult, _startsLiveKey());
  8056	  return (st && st.ran && st.alternatives && st.alternatives[k]) || null;
  8057	}
  8058	
  8059	const _STARTS_STALE_MSG = 'The model has changed since this fit. Run the fit again to compare solutions.';
  8060	
  8061	function previewAlternative(k) {
  8062	  const alt = _currentAlternative(k);
  8063	  const peaks = alt && _altPeaks(alt);
  8064	  if (!peaks) { notify(_STARTS_STALE_MSG, 'amber', true); return; }
  8065	  const key = 'alt:' + k;
  8066	  if (_historyPreview && _historyPreview.snapId === key) { _historyClearPreview(); return; }
  8067	  _historyPreview = { snapId: key, altKey: state.fitResult.startsModelKey, peaks, fitResult: { chiReduced: alt.chi2r } };
  8068	  _updateLocalModelBanner();
  8069	  document.querySelectorAll('.hist-row').forEach(r => r.classList.remove('hist-preview-active'));
  8070	  updatePlot();
  8071	}
  8072	
  8073	// Adopting an alternative is the student's decision: explicit, undoable, and
  8074	// recorded. It is ATOMIC by construction: the alternative is only the START of
  8075	// an ordinary server fit (runFit's opts.startPeaks); the live model is written
  8076	// by that fit's success path and by nothing else, so a fit that fails, does
  8077	// not converge, is discarded because the tab changed, or cannot reach the
  8078	// server leaves peaks and result exactly as they were (no local fallback
  8079	// here: the local engine would start from the live model, not from the
  8080	// alternative). runFit's own pushUndo is the single undo entry. A solution
  8081	// that moves a component more than 1 eV from where the student put it is the
  8082	// measured trap (a lower chi-square bought by a chemically absurd relocation),
  8083	// so that case — and only that case — asks first, naming the component and
  8084	// the distance.
  8085	async function useAlternative(k) {
  8086	  const alt = _currentAlternative(k);
  8087	  const peaks = alt && _altPeaks(alt);
  8088	  if (!peaks) { notify(_STARTS_STALE_MSG, 'amber', true); return; }
  8089	  const shift = alt.largest_centre_shift_from_start;
  8090	  const name = _startsPeakName(shift.id);
  8091	  if (Math.abs(shift.ev) > _STARTS_SHIFT_RED_EV &&
  8092	      !confirm(`This solution moves ${name} by ${_startsEv(shift.ev)} from where you placed it. Apply?`)) return;
  8093	  const chosen = { fromChi: state.fitResult.starts.fit.chi2r, toChi: alt.chi2r, shiftName: name, shiftEv: shift.ev };
  8094	  if (_historyPreview) _historyClearPreview();
  8095	  await runFit({ startPeaks: peaks, chosenAlternative: chosen });
  8096	}
  8097	
  8098	async function runFit(opts = {}) {
  8099	  if (!state.rawBE.length) { notify('Load a spectrum first.', 'red', true); return; }
  8100	  if (!state.peaks.length) { notify('Add at least one peak.', 'red'); return; }
  8101	  pushUndo();
  8102	
  8103	  _showFitSpinner();
  8104	  document.getElementById('sb-msg').textContent = 'Fitting\u2026';
  8105	
  8106	  // Capture the tab that owns this fit so that if the user switches tabs
  8107	  // mid-request, we can discard the stale result instead of corrupting the
  8108	  // now-active tab's state.
  8109	  const fittingTab = _opOwner();
  8110	
  8111	  const { be, inten } = getROIData();
  8112	  const bgIntensity = computeBackground(be, inten);
  8113	  const bgSubtracted = inten.map((v, i) => v - bgIntensity[i]);
  8114	
  8115	  // Try Flask backend first
  8116	  let backendResult = null;
  8117	  let ctxAtRequest = null;   // set with the other request inputs; read again by the local fallback
  8118	  try {
  8119	    const bgType  = document.getElementById('bg-type').value;
  8120	    const bgStart = parseFloat(document.getElementById('bg-start').value);
  8121	    const bgEnd   = parseFloat(document.getElementById('bg-end').value);
  8122	    // Inclusive bg window — the same point set computeBackgroundCore draws;
  8123	    // the backend slices end-exclusive, so the request sends i1 + 1.
  8124	    const bgWin = _bgWindowIndices(be, bgStart, bgEnd);
  8125	    // EVERY request input is read from the owner before the upload await:
  8126	    // peaks, method, endpoint averaging and manual anchors (Codex round 2: a
  8127	    // request could carry A's spectrum with B's averaging and anchors).
  8128	    // opts.startPeaks: the request starts from an adopted alternative; the live
  8129	    // model is still the student's until this fit succeeds (useAlternative).
  8130	    const startModel = opts.startPeaks || state.peaks;
  8131	    const peakSpecs = startModel.map(peakToBackendSpec);
  8132	    // scattered-starts check: decided HERE, with the other request inputs,
  8133	    // before the first await (a tab switch during the upload must not turn it off)
  8134	    const nStarts = _startsUnlinkedCount(startModel) >= 2 ? _STARTS_N : 0;
  8135	    // the live model and its fit context as the student pressed the button: a
  8136	    // result must not be written over a model that was edited while it ran
  8137	    ctxAtRequest = _startsLiveKey();
  8138	    const fitMethod = document.getElementById('fit-method').value;
  8139	    const epAvgVal = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
  8140	    const bgPayload = { method: bgType, start_idx: bgWin.i0, end_idx: bgWin.i1 + 1, endpoint_avg: epAvgVal };
  8141	    if (bgType === 'manual') {
  8142	      // Anchors are stored in corrected-BE space, same frame as the uploaded
  8143	      // session data; backend expects [x, y] pairs.
  8144	      bgPayload.manual_bg = _getManualAnchors().map(a => [a.x, a.y]);
  8145	    }
  8146	    // Transport failures (server unreachable, timeout, non-JSON reply) are
  8147	    // the ONLY reason to fall back to the local optimiser. A server-side
  8148	    // validation error or a non-converged optimisation surfaces its message
  8149	    // and leaves the model untouched (unit A0: nothing is shown as a fit
  8150	    // result unless it converged; an HTTP 400 is not a reason to silently
  8151	    // switch engines).
  8152	    // Only a genuine transport failure (network rejection, abort, a body that
  8153	    // could not be read) is marked for fallback; server errors — including a
  8154	    // 2xx body that was read but is not JSON (F2) — carry `serverError`.
  8155	    const _asTransport = (e) => {
  8156	      if (e && !e.serverError && (e instanceof TypeError || e.name === 'AbortError' || e instanceof SyntaxError)) e.transportFailure = true;
  8157	      throw e;
  8158	    };
  8159	    let sessionId;
  8160	    try { sessionId = await uploadToBackend(be, inten); } catch (e) { _asTransport(e); }
  8161	    const fitReq = {
  8162	      session_id: sessionId,
  8163	      background: bgPayload,
  8164	      peaks: peakSpecs,
  8165	      fit_method: fitMethod,
  8166	      n_perturb: 3,
  8167	      n_starts: nStarts       // the server also skips it for the global methods
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
  8180	      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
  8181	      notify('Fit result discarded because you switched tabs during the fit.', 'amber');
  8182	      return;
  8183	    }
  8184	    if (json && json._abandoned === 'model') {
  8185	      _hideFitSpinner();
  8186	      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
  8187	      notify('Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.', 'amber', true);
  8188	      return;
  8189	    }
  8190	    if (json.error) {
  8191	      const err = new Error(json.error);
  8192	      err.serverError = true;
  8193	      throw err;
  8194	    }
  8195	    // ACCEPTANCE RULE: the backend reports lmfit's own convergence flag. A
  8196	    // result that did not converge is a failed fit, not a result (audit A08:
  8197	    // until this unit success:false was applied and announced as complete).
  8198	    if (json.success !== true) {
  8199	      const err = new Error(json.message || 'the optimizer did not converge.');
  8200	      err.notConverged = true;
  8201	      throw err;
  8202	    }
  8203	    backendResult = json;
  8204	
  8205	    // If the user switched tabs while the fit was running, discard the result
  8206	    // rather than overwriting the now-active tab's peaks.
  8207	    if (!_ownerActive(fittingTab)) {
  8208	      _hideFitSpinner();
  8209	      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
  8210	      notify('Fit result discarded because you switched tabs during the fit.', 'amber');
  8211	      return;
  8212	    }
  8213	
  8214	    // The peak controls stay editable while the fit runs. A result computed for
  8215	    // the model as it was must not be applied over an edited one (a newly locked
  8216	    // centre would keep its edited value under the server's statistics).
  8217	    if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
  8218	      _hideFitSpinner();
  8219	      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
  8220	      notify('Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.', 'amber', true);
  8221	      return;
  8222	    }
  8223	
  8224	    // Capture pre-fit values for uncertainty validation
  8225	    const _preFit = {};
  8226	    for (const p of state.peaks) {
  8227	      _preFit[p.id] = { center: p.center, fwhm: p.fwhm, amplitude: p.amplitude, glMix: p.glMix };
  8228	    }
  8229	    applyBackendResult(backendResult);
  8230	    { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }   // a new result supersedes imported provenance
  8231	    const stats = backendResult.statistics || {};
  8232	    const chiReduced = stats.reduced_chi_square || 0;
  8233	    const rmse = Math.sqrt((backendResult.residuals || []).reduce((s, v) => s + v * v, 0) / Math.max(1, be.length));
  8234	    const roiRange = { min: _arrMin(be).toFixed(1), max: _arrMax(be).toFixed(1) };
  8235	    state.fitResult = { chi: chiReduced * Math.max(1, be.length - state.peaks.length * 3),
  8236	                        chiReduced, rmse, be, bgSubtracted, bgIntensity, backendResult,
  8237	                        fittedY: backendResult.fitted_y, roiRange, _preFit,
  8238	                        starts: backendResult.starts || null,
  8239	                        startsModelKey: _startsLiveKey(),     // model + context, taken AFTER the result was applied
  8240	                        chosenAlternative: opts.chosenAlternative || null };
  8241	    // a preview of an alternative always belongs to the PREVIOUS result (an identical
  8242	    // key does not make it this one's): clear it unconditionally
  8243	    if (_historyPreview && typeof _historyPreview.snapId === 'string' && _historyPreview.snapId.startsWith('alt:')) _historyPreview = null;
  8244	    state.fitResult.rFactor = _computeRFactor(state.fitResult);
  8245	    _applyStatDisplay(state.fitResult);
  8246	    document.getElementById('sb-msg').textContent = 'Fit complete (lmfit)';
  8247	    _updateRFactorUI(state.fitResult.rFactor);
  8248	    _updateROIDisplay(roiRange);
  8249	    _hideFitSpinner();
  8250	    notify('Fit complete. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3), 'green');
  8251	  } catch (e) {
  8252	    // Fall back to local Levenberg-Marquardt
  8253	    _hideFitSpinner();
  8254	    if (!_ownerActive(fittingTab)) {
  8255	      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
  8256	      notify('Fit cancelled — tab switched during fit.', 'amber');
  8257	      return;
  8258	    }
  8259	    if (e && e.transportFailure && opts.startPeaks) {
  8260	      // Adopting an alternative needs the server: the local engine would start
  8261	      // from the live model, not from the alternative. Nothing was changed.
  8262	      document.getElementById('sb-msg').textContent = 'Fit failed';
  8263	      notify('The server could not be reached, so the alternative was not applied. Previous peaks and result kept.', 'red', true);
  8264	      return;
  8265	    }
  8266	    if (e && e.transportFailure && ctxAtRequest !== null && !_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
  8267	      // The fallback would fit the arrays captured at the press over a model or
  8268	      // context edited since, and stamp the edited one (F1, Codex round 1).
  8269	      _hideFitSpinner();
  8270	      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
  8271	      notify('The server could not be reached, and the model or its background / ROI settings were edited while the fit was running, so no local fit was run. Previous peaks and result kept. Run the fit again.', 'amber', true);
  8272	      return;
  8273	    }
  8274	    if (e && e.transportFailure) {
  8275	      // Server unreachable: the local optimiser is the honest fallback, and
  8276	      // the overlay saying so opens only if it actually converged.
  8277	      if (e.message) console.warn('Backend unreachable, falling back to local LM:', e.message);
  8278	      const local = runFitLocal(be, bgSubtracted, bgIntensity);
  8279	      if (local && local.success && !_snapshotSuppressed) {
  8280	        document.getElementById('localfit-warn-overlay').classList.add('open');
  8281	      }
  8282	      return;
  8283	    }
  8284	    // Server-side error or non-converged optimisation: report it; the
  8285	    // previous peaks and fit result stay exactly as they were.
  8286	    const notConverged = !!(e && e.notConverged);
  8287	    document.getElementById('sb-msg').textContent = notConverged ? 'Fit did not converge' : 'Fit failed';
  8288	    notify((notConverged ? 'Fit did not converge: ' : 'Fit failed: ') + ((e && e.message) || 'unknown error') +
  8289	           ' Previous peaks and result kept.', 'red', true);
  8290	    return;
  8291	  }
  8292	
  8293	  renderPeakList();
  8294	  updatePlot();
  8295	  renderResults();
  8296	  _autoSnapshot();
  8297	}
  8298	
  8299	// Label for the goodness-of-fit statistic a fit result carries. The server
  8300	// and (since unit W1, 2026-09-18) the local engine both minimise a
  8301	// counting-noise-weighted chi-square; local results saved by unit A0 were
  8302	// UNWEIGHTED and keep the label "Residual variance", never chi-square.
  8303	function _isUnweightedLocal(fr) { return !!(fr && fr.objective === 'unweighted_residual_variance'); }
  8304	function _fitStatLabel(fr) {
  8305	  return _isUnweightedLocal(fr) ? 'Residual variance' : 'χ²ᵣ';
  8306	}
  8307	// A LOCAL result is a STARTING POINT, not a reportable result. Measured in
  8308	// unit W1 (docs/superpowers/plans/2026-09-18-local-engine-poisson-weighting.md):
  8309	// with Poisson weighting the local engine matches the server on GL-type
  8310	// models (<= 4 meV, <= 1.4 % area on the lab's C1s scans) and, since A03
  8311	// (2026-09-22: Voigt = fixed eta 0.5 on BOTH sides), on Voigt components
  8312	// wherever the two engines reach the same minimum (5 of 9 committed U 4f
  8313	// targets: every component within 4.3 meV, 2.6 % FWHM, 2 % area, 0.12 pp);
  8314	// it still differs where an LA component's m moves on the server (held,
  8315	// exactly, at its start locally - LA is discontinuous in m, caM unit) and
  8316	// where the model has several minima; and it gives no uncertainties. Unweighted A0-era results differed by more than 100 %.
  8317	// Every site that shows, exports or saves a fit result carries the
  8318	// designation, keyed on persisted identity so reloaded results are labelled.
  8319	const _LOCAL_FIT_CAVEAT = 'Local fit (Poisson-weighted like the server, no uncertainties): a starting point, not a reportable result. Run Fit before reporting.';
  8320	const _LOCAL_FIT_CAVEAT_UNWEIGHTED = 'Local unweighted fit: a starting point, not a reportable result. Run Fit before reporting.';
  8321	function _isLocalProvenance(p) {
  8322	  return !!(p && (p.engine === 'local' || p.objective === 'unweighted_residual_variance' || p.objective === 'poisson_weighted_chi_square'));
  8323	}
  8324	function _isLocalFit(fr) { return _isLocalProvenance(fr); }
  8325	// The record that governs the active model's designation: its live result,
  8326	// else the provenance it was imported / copied / restored with.
  8327	function _governingProvenance() {
  8328	  if (state.fitResult) return state.fitResult;
  8329	  const t = _activeTab();
  8330	  return (t && t.modelProvenance) || null;
  8331	}
  8332	function _localFitDetail(fr) {
  8333	  return _isUnweightedLocal(fr)
  8334	    ? 'Its areas can differ from the server fit by more than 100&nbsp;%.'
  8335	    : 'It can differ from the server fit for LA components (the page holds the smoothing parameter m at its start; the server fits it) or where the model has several minima.';
  8336	}
  8337	// The designation follows the MODEL, not only a live fit result: parameters
  8338	// imported from a .fit.json that was saved from a local fit are a starting
  8339	// point too (tab.modelProvenance, set by fromJSON, cleared by any new fit).
  8340	function _isLocalModel() {
  8341	  if (state.fitResult) return _isLocalFit(state.fitResult);
  8342	  const t = _activeTab();
  8343	  return !!(t && _isLocalProvenance(t.modelProvenance));
  8344	}
  8345	// The designation a tab's MODEL carries: its stored provenance (imported or
  8346	// copied), else one derived from its live local result — so that undo
  8347	// snapshots and batch copies taken while a local result exists keep it.
  8348	// Persistent designation in the Peaks sidebar (visible whatever panel is
  8349	// open), refreshed with the peak list and the results.
  8350	function _updateLocalModelBanner() {
1904:      <button class="btn btn-green peak-fit-control" id="btn-run-fit" onclick="runFit()">Run Fit</button>
1918:          <button class="save-dropdown-item" id="auto-fit-c1s-menu-item" onclick="runAutoFitC1sGraphite()" title="Available only on C1s spectra (ROI midpoint 270–315 eV)"><span class="dd-icon">&#128293;</span><div>Auto-Fit C1s Graphite<small>One-click fit + charge correction</small></div></button>
2347:function _opOwner() {
2354:function _ownerActive(owner) {
5894:    if (k === 'f')                 { e.preventDefault(); runFit(); return; }
6688:function _showFitSpinner() {
6697:  _showFitSpinner._timer = setTimeout(() => {
6701:function _hideFitSpinner() {
6705:  clearTimeout(_showFitSpinner._timer);
6976:    owner:        _opOwner(),
6985:    modelProvenance: (() => { const o = _opOwner(); return o && o.modelProvenance ? JSON.parse(JSON.stringify(o.modelProvenance)) : null; })(),
7343:  // 5. Build state.fitResult exactly as runFit() does.
7362:  // 6. Update the same DOM elements runFit() updates.
7558:async function runAutoFitC1sGraphite() {
7569:  const fittingTab = _opOwner();
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
8109:  const fittingTab = _opOwner();
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
10784:  const owner = _opOwner();   // a .fit.json applies to the tab active when the file was chosen
10810:      if (!_ownerActive(owner)) { notify('Fit file not applied — the tab changed while the file was being read.', 'amber'); return; }
10828:      if (!_ownerActive(owner)) { notify('Fit file not applied — the tab changed while the file was being read.', 'amber'); return; }
15058:  const t = owner || _opOwner();
16079:    const owner = _opOwner();
16127:    if (!_ownerActive(owner)) {
16300:  const owner = _opOwner();              // the record this apply belongs to
16310:  if (!_ownerActive(owner)) {

exec
/bin/zsh -lc "cat scripts/public_fit_poll_check.py docs/superpowers/plans/2026-09-27-long-fits-start-poll.md; rg -n 'model.fit|except |cancel|n_perturb|n_starts' fitting.py | tail -85; ls -ld venv /Users/skyefortier/xps-app/venv; rg --files -g 'AGENTS.md' /Users/skyefortier/.codex /Users/skyefortier/xps-app 2>/dev/null | head -40" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
#!/usr/bin/env python3
"""Post-deploy check for unit 2 (long fits via start-then-poll), THROUGH THE
PUBLIC URL — the path a student's browser takes, where Cloudflare ends a
single request at ~100 s (HTTP 524).

It does what the page does for Run Fit: upload, POST /api/fit/start, poll
GET /api/fit/progress every 0.5 s until the job leaves "running"; it records
the duration of EVERY request. PASS = the job finishes "done" with
success true, and no request took longer than MAX_REQUEST_S.

Usage:
  python scripts/public_fit_poll_check.py targets.json [BASE_URL] [target_id ...]

targets.json: the optimizer-disagreement target file (branch
investigate-optimizer-disagreement, docs/findings/optimizer-disagreement/
targets.json). Default targets: the five largest committed C 1s models,
the ones that took 183-256 s even without restarts.
"""
import json
import sys
import time
import urllib.error
import urllib.request
import uuid

MAX_REQUEST_S = 10.0
DEFAULT_TARGETS = ["edf39ecb66ce", "d2bd62d2f976", "496c4edd97af", "0a5f464daf3d", "8b4c2f656a80"]


def _req(url, data=None, headers=None, method=None, timeout=60):
    t0 = time.time()
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "xps-poll-check", **(headers or {})}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body, status = r.read(), r.status
    except urllib.error.HTTPError as e:
        body, status = e.read(), e.code
    return status, body, time.time() - t0


def run(base, t):
    durations = []
    csv = "\n".join(f"{a:.4f},{b:.4f}" for a, b in zip(t["be"], t["inten"])).encode()
    bnd = uuid.uuid4().hex
    form = (f"--{bnd}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"t.csv\"\r\n"
            f"Content-Type: text/csv\r\n\r\n").encode() + csv + f"\r\n--{bnd}--\r\n".encode()
    st, body, d = _req(base + "/api/upload", form, {"Content-Type": f"multipart/form-data; boundary={bnd}"})
    durations.append(("upload", st, d))
    sid = json.loads(body)["session_id"]
    bg = t["background"]
    payload = {"session_id": sid, "background": {k: bg[k] for k in ("method", "start_idx", "end_idx", "endpoint_avg")},
               "peaks": t["specs"], "fit_method": "basinhopping", "n_perturb": 3, "n_starts": 3}
    st, body, d = _req(base + "/api/fit/start", json.dumps(payload).encode(), {"Content-Type": "application/json"})
    durations.append(("start", st, d))
    if st != 202:
        return {"id": t["id"], "verdict": "FAIL", "why": f"start returned {st}: {body[:200]!r}", "durations": durations}
    job = json.loads(body)["job_id"]
    t0 = time.time()
    while True:
        time.sleep(0.5)
        st, body, d = _req(base + f"/api/fit/progress/{job}")
        durations.append(("poll", st, d))
        rec = json.loads(body) if st == 200 else {"status": f"http {st}"}
        if rec.get("status") != "running":
            break
    longest = max(x[2] for x in durations)
    res = rec.get("result") or {}
    ok = rec.get("status") == "done" and res.get("success") is True and longest <= MAX_REQUEST_S
    return {"id": t["id"], "verdict": "PASS" if ok else "FAIL", "status": rec.get("status"),
            "success": res.get("success"), "chi2r": (res.get("statistics") or {}).get("reduced_chi_square"),
            "fit_wall_s": round(time.time() - t0, 1), "n_requests": len(durations),
            "longest_request_s": round(longest, 2), "error": rec.get("error")}


def main():
    targets = json.load(open(sys.argv[1]))
    base = sys.argv[2] if len(sys.argv) > 2 else "https://xps.fortierlab.org"
    ids = sys.argv[3:] or DEFAULT_TARGETS
    by_id = {t["id"]: t for t in targets}
    results = [run(base, by_id[i]) for i in ids]
    for r in results:
        print(json.dumps(r))
    print("OVERALL:", "PASS" if all(r["verdict"] == "PASS" for r in results) else "FAIL")


if __name__ == "__main__":
    main()
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

(filled in as they run)

576:    nominal B_coef cancels; C alone sets the kernel shape).  Equivalent to
987:# job passes ``run_fit(..., cancel=callable)``; inside that thread every
988:# model.fit below receives an ``iter_cb`` that returns True — lmfit's abort —
989:# once ``cancel()`` is true (checked at most every 0.25 s). Thread-local, so a
991:# WITHOUT a cancel callable no ``iter_cb`` argument is passed at all, so every
998:    """The job was cancelled while run_fit ran."""
1001:def _cancel_kw() -> dict:
1105:    found = model.fit(y_sub, boxed, x=x, weights=weights, **kws, **_cancel_kw())
1116:        refined = model.fit(y_sub, free, x=x, weights=weights, **refine_kws, **_cancel_kw())
1117:    except Exception:
1153:        local = model.fit(y_sub, start, x=x, weights=weights,
1154:                          method="least_squares", nan_policy=kws.get("nan_policy", "omit"), **_cancel_kw())
1155:    except Exception:
1190:    found = model.fit(y_sub, start.copy(), x=x, weights=weights, **kws, **_cancel_kw())
1193:        refined = model.fit(y_sub, found.params.copy(), x=x, weights=weights,
1194:                            method="least_squares", nan_policy=nan_policy, **_cancel_kw())
1197:    except Exception:
1206:        local = model.fit(y_sub, start.copy(), x=x, weights=weights, method="least_squares", nan_policy=nan_policy,
1207:                          **_cancel_kw())
1208:    except Exception:
1233:def _request_seed(x, counts, background, shapes, prefixes, params, *, fit_kws, n_perturb) -> int:
1238:    solver options and ``n_perturb``.
1277:                       "n_perturb": n_perturb})
1378:def _scattered_starts(n_starts, fit_once, model, start_params, result, peak_specs, x, rng) -> dict[str, Any]:
1385:    for _ in range(n_starts):
1388:        except Exception:
1400:            clusters.append({"chi2r": float(trial.redchi), "n_starts": 1, "components": comps})
1402:            home["n_starts"] += 1
1412:        "ran": True, "n_run": n_starts, "n_converged": n_converged, "n_same_as_fit": n_same,
1414:        "n_in_alternatives": sum(c["n_starts"] for c in lower),
1415:        "n_not_better_elsewhere": sum(c["n_starts"] for c in other),
1542:    n_perturb: int = 0,
1545:    n_starts: int = 0,
1739:            fit_kws=fit_kws, n_perturb=n_perturb)
1744:    if isinstance(n_starts, bool) or not isinstance(n_starts, (int, np.integer)) or not 0 <= n_starts <= MAX_N_STARTS:
1745:        raise ValueError(f"n_starts must be an integer between 0 and {MAX_N_STARTS}")
1794:        return model.fit(y_sub, params, x=x, weights=weights, **seeded(kws), **_cancel_kw())
1810:    except Exception as exc:
1827:    # starts check excludes it — and with the page's n_perturb 3 they
1831:    if n_perturb > 0 and result.success and kws.get("method") != "basinhopping":
1836:        for attempt in range(n_perturb):
1857:                          attempt + 1, n_perturb, trial_redchi, best_redchi)
1867:            except Exception:
1868:                log.debug("  PERTURB %d/%d  failed (exception)", attempt + 1, n_perturb)
1878:    if n_starts:
1888:                starts = _scattered_starts(int(n_starts), fit_once, composite_model, all_params, result,
1890:            except Exception as exc:                              # the check must never cost the student the fit
1925:            except Exception as exc:                              # the check must never cost the student the fit
2094:def run_fit(*args, cancel=None, **kwargs):
2097:    ``cancel`` (optional, unit 2): a callable polled during the fit; once it
2101:    if cancel is None:
2103:    _CANCEL.fn, _CANCEL.hit = cancel, False
2110:        raise FitCancelled("the fit was cancelled")
ls: venv: No such file or directory
drwxr-xr-x  7 skyefortier  staff  224 Jul  7 11:35 /Users/skyefortier/xps-app/venv

exec
/bin/zsh -lc 'node --test tests/js/fit_start_poll.test.js tests/js/fit_acceptance.test.js tests/js/stale_statistics.test.js tests/js/per_tab_state.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 397ms:
# Subtest: A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
ok 1 - A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
  ---
  duration_ms: 8.810683
  type: 'test'
  ...
# Subtest: a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
ok 2 - a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
  ---
  duration_ms: 4.741276
  type: 'test'
  ...
# Subtest: a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
ok 3 - a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
  ---
  duration_ms: 3.171917
  type: 'test'
  ...
# Subtest: a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
ok 4 - a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
  ---
  duration_ms: 12.09828
  type: 'test'
  ...
# Subtest: a converged backend result is applied (sanity)
ok 5 - a converged backend result is applied (sanity)
  ---
  duration_ms: 4.229061
  type: 'test'
  ...
# Subtest: the engine/objective labels of a fit result survive spectrum and project save/load
ok 6 - the engine/objective labels of a fit result survive spectrum and project save/load
  ---
  duration_ms: 0.883869
  type: 'test'
  ...
# Subtest: an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
ok 7 - an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
  ---
  duration_ms: 3.034548
  type: 'test'
  ...
# Subtest: an HTTP 502 on the upload is a server failure, not a transport failure
ok 8 - an HTTP 502 on the upload is a server failure, not a transport failure
  ---
  duration_ms: 2.980185
  type: 'test'
  ...
# Subtest: uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
ok 9 - uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
  ---
  duration_ms: 1.880847
  type: 'test'
  ...
# Subtest: every consumer that prints the goodness-of-fit statistic routes through the statistic identity
ok 10 - every consumer that prints the goodness-of-fit statistic routes through the statistic identity
  ---
  duration_ms: 0.983979
  type: 'test'
  ...
# Subtest: uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
ok 11 - uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
  ---
  duration_ms: 0.70486
  type: 'test'
  ...
# Subtest: a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
ok 12 - a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
  ---
  duration_ms: 1.590119
  type: 'test'
  ...
# Subtest: starting-point helpers: keyed on the persisted objective, weighted results untouched
ok 13 - starting-point helpers: keyed on the persisted objective, weighted results untouched
  ---
  duration_ms: 3.471433
  type: 'test'
  ...
# Subtest: Quantify shows the starting-point banner for a local result and not for a weighted one
ok 14 - Quantify shows the starting-point banner for a local result and not for a weighted one
  ---
  duration_ms: 5.603663
  type: 'test'
  ...
# Subtest: every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
ok 15 - every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
  ---
  duration_ms: 1.90269
  type: 'test'
  ...
# Subtest: project save derives the designation from the objective for an older local result lacking the new fields
ok 16 - project save derives the designation from the objective for an older local result lacking the new fields
  ---
  duration_ms: 9.915657
  type: 'test'
  ...
# Subtest: stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
ok 17 - stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
  ---
  duration_ms: 1.163721
  type: 'test'
  ...
# Subtest: _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
ok 18 - _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
  ---
  duration_ms: 4.23654
  type: 'test'
  ...
# Subtest: history preview glow is keyed on the dataset flag, not the label text
ok 19 - history preview glow is keyed on the dataset flag, not the label text
  ---
  duration_ms: 0.748759
  type: 'test'
  ...
# Subtest: spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
ok 20 - spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
  ---
  duration_ms: 0.511365
  type: 'test'
  ...
# Subtest: _applyStatDisplay clears header, tooltip, caption and value together on local → none
ok 21 - _applyStatDisplay clears header, tooltip, caption and value together on local → none
  ---
  duration_ms: 3.650762
  type: 'test'
  ...
# Subtest: _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
ok 22 - _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
  ---
  duration_ms: 2.643132
  type: 'test'
  ...
# Subtest: fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
ok 23 - fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
  ---
  duration_ms: 1.430625
  type: 'test'
  ...
# Subtest: undo/redo snapshots carry and restore model provenance
ok 24 - undo/redo snapshots carry and restore model provenance
  ---
  duration_ms: 3.698326
  type: 'test'
  ...
# Subtest: round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
ok 25 - round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
  ---
  duration_ms: 1.253875
  type: 'test'
  ...
# Subtest: _provenanceOf derives a designation from a live local result, and undo snapshots use it
ok 26 - _provenanceOf derives a designation from a live local result, and undo snapshots use it
  ---
  duration_ms: 3.023442
  type: 'test'
  ...
# Subtest: batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
ok 27 - batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
  ---
  duration_ms: 0.401729
  type: 'test'
  ...
# Subtest: the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
ok 28 - the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
  ---
  duration_ms: 2.591911
  type: 'test'
  ...
# Subtest: round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
ok 29 - round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
  ---
  duration_ms: 0.676569
  type: 'test'
  ...
# Subtest: the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
ok 30 - the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
  ---
  duration_ms: 2.706506
  type: 'test'
  ...
# Subtest: the sidebar banner is sticky at the top of the scrolling panel body
ok 31 - the sidebar banner is sticky at the top of the scrolling panel body
  ---
  duration_ms: 0.309483
  type: 'test'
  ...
# Subtest: the sidebar banner shows on a stack tab whose visible entries draw a local source fit
ok 32 - the sidebar banner shows on a stack tab whose visible entries draw a local source fit
  ---
  duration_ms: 2.860223
  type: 'test'
  ...
# Subtest: every stack chart repaint path refreshes the sidebar designation before any early return
ok 33 - every stack chart repaint path refreshes the sidebar designation before any early return
  ---
  duration_ms: 0.457608
  type: 'test'
  ...
# Subtest: closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
ok 34 - closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
  ---
  duration_ms: 0.193284
  type: 'test'
  ...
# Subtest: W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
ok 35 - W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
  ---
  duration_ms: 3.826691
  type: 'test'
  ...
# Subtest: TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
ok 36 - TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
  ---
  duration_ms: 4.398666
  type: 'test'
  ...
# Subtest: adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
ok 37 - adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
  ---
  duration_ms: 3.780712
  type: 'test'
  ...
# Subtest: adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
ok 38 - adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
  ---
  duration_ms: 3.106526
  type: 'test'
  ...
# Subtest: adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
ok 39 - adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
  ---
  duration_ms: 2.948679
  type: 'test'
  ...
# Subtest: adoption: success records the choice, the starts evidence and the key of the model it describes
ok 40 - adoption: success records the choice, the starts evidence and the key of the model it describes
  ---
  duration_ms: 3.189124
  type: 'test'
  ...
# Subtest: an ordinary Run Fit on one unlinked component does not ask for the starts check
ok 41 - an ordinary Run Fit on one unlinked component does not ask for the starts check
  ---
  duration_ms: 3.163056
  type: 'test'
  ...
# Subtest: a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
ok 42 - a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
  ---
  duration_ms: 3.194484
  type: 'test'
  ...
# Subtest: a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
ok 43 - a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
  ---
  duration_ms: 5.740928
  type: 'test'
  ...
# Subtest: a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
ok 44 - a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
  ---
  duration_ms: 5.5292
  type: 'test'
  ...
# Subtest: a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
ok 45 - a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
  ---
  duration_ms: 7.266449
  type: 'test'
  ...
# Subtest: the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)
ok 46 - the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)
  ---
  duration_ms: 0.963649
  type: 'test'
  ...
# Subtest: the token scan is linear and keeps a truncated string a string (Codex round 2)
ok 47 - the token scan is linear and keeps a truncated string a string (Codex round 2)
  ---
  duration_ms: 4.061156
  type: 'test'
  ...
# Subtest: start -> running polls -> done: the result is the /api/fit body; no job is left registered
ok 48 - start -> running polls -> done: the result is the /api/fit body; no job is left registered
  ---
  duration_ms: 11.944078
  type: 'test'
  ...
# Subtest: a bad request: the synchronous route's message and status, immediately; no poll
ok 49 - a bad request: the synchronous route's message and status, immediately; no poll
  ---
  duration_ms: 5.676673
  type: 'test'
  ...
# Subtest: a START that cannot reach the server is a transport failure (the caller may fall back to the local engine)
ok 50 - a START that cannot reach the server is a transport failure (the caller may fall back to the local engine)
  ---
  duration_ms: 3.478711
  type: 'test'
  ...
# Subtest: an error record is a failed fit with the synchronous message and status
ok 51 - an error record is a failed fit with the synchronous message and status
  ---
  duration_ms: 4.103769
  type: 'test'
  ...
# Subtest: a done record carrying NaN is F2's failed fit (unreadable reply), not a transport failure
ok 52 - a done record carrying NaN is F2's failed fit (unreadable reply), not a transport failure
  ---
  duration_ms: 3.363584
  type: 'test'
  ...
# Subtest: one lost poll is retried; five in a row are a transport failure and cancel the job
ok 53 - one lost poll is retried; five in a row are a transport failure and cancel the job
  ---
  duration_ms: 8.867139
  type: 'test'
  ...
# Subtest: a stopped heartbeat (restarted worker) is a failed fit, never an endless spinner
ok 54 - a stopped heartbeat (restarted worker) is a failed fit, never an endless spinner
  ---
  duration_ms: 2.580842
  type: 'test'
  ...
# Subtest: a job cancelled on the server (abandoned) is reported, not waited for
ok 55 - a job cancelled on the server (abandoned) is reported, not waited for
  ---
  duration_ms: 3.463259
  type: 'test'
  ...
# Subtest: ownership inside the loop: a switched tab or an edited model cancels the job and returns the reason
ok 56 - ownership inside the loop: a switched tab or an edited model cancels the job and returns the reason
  ---
  duration_ms: 6.182685
  type: 'test'
  ...
# Subtest: the Auto-Fit abort (2 minutes) cancels the job and surfaces as an AbortError
ok 57 - the Auto-Fit abort (2 minutes) cancels the job and surfaces as an AbortError
  ---
  duration_ms: 3.765578
  type: 'test'
  ...
# Subtest: Run Fit and Auto-Fit both go through _serverFitJob; nothing on the page posts to the synchronous /api/fit any more
ok 58 - Run Fit and Auto-Fit both go through _serverFitJob; nothing on the page posts to the synchronous /api/fit any more
  ---
  duration_ms: 3.445384
  type: 'test'
  ...
# Subtest: every module-level mutable is allowlisted with a valid non-C class
ok 59 - every module-level mutable is allowlisted with a valid non-C class
  ---
  duration_ms: 210.877256
  type: 'test'
  ...
# Subtest: inherited property names and anonymous-class names cannot slip through the allowlist
ok 60 - inherited property names and anonymous-class names cannot slip through the allowlist
  ---
  duration_ms: 92.76217
  type: 'test'
  ...
# Subtest: the known class-C holders are gone from module scope
ok 61 - the known class-C holders are gone from module scope
  ---
  duration_ms: 5.882468
  type: 'test'
  ...
# Subtest: async operations capture their owning record before the first await
ok 62 - async operations capture their owning record before the first await
  ---
  duration_ms: 1.983877
  type: 'test'
  ...
# Subtest: undo/redo and Find Peaks apply read the ACTIVE tab record only
ok 63 - undo/redo and Find Peaks apply read the ACTIVE tab record only
  ---
  duration_ms: 0.592519
  type: 'test'
  ...
# Subtest: one accessor classifies a result against a key: none / unverified / current / stale
ok 64 - one accessor classifies a result against a key: none / unverified / current / stale
  ---
  duration_ms: 12.977214
  type: 'test'
  ...
# Subtest: the key is the step (b) key: F1 adds no second binding mechanism and no new key field
ok 65 - the key is the step (b) key: F1 adds no second binding mechanism and no new key field
  ---
  duration_ms: 5.084001
  type: 'test'
  ...
# Subtest: Results panel, current: statistic, RMSE, R and sigma are shown
ok 66 - Results panel, current: statistic, RMSE, R and sigma are shown
  ---
  duration_ms: 12.437991
  type: 'test'
  ...
# Subtest: Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
ok 67 - Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
  ---
  duration_ms: 8.090445
  type: 'test'
  ...
# Subtest: Results panel, unverified (older save, no key): values shown with a plain note
ok 68 - Results panel, unverified (older save, no key): values shown with a plain note
  ---
  duration_ms: 10.386744
  type: 'test'
  ...
# Subtest: status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
ok 69 - status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
  ---
  duration_ms: 13.602319
  type: 'test'
  ...
# Subtest: the stored fitted curve is never drawn, saved or stacked as the fit once stale
ok 70 - the stored fitted curve is never drawn, saved or stacked as the fit once stale
  ---
  duration_ms: 5.139549
  type: 'test'
  ...
# Subtest: saves keep the key and say plainly when the statistics are stale or unverified
ok 71 - saves keep the key and say plainly when the statistics are stale or unverified
  ---
  duration_ms: 2.721045
  type: 'test'
  ...
# Subtest: CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
ok 72 - CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
  ---
  duration_ms: 15.920787
  type: 'test'
  ...
# Subtest: XLSX: stale writes a WARNING row instead of the statistic, and no sigma
ok 73 - XLSX: stale writes a WARNING row instead of the statistic, and no sigma
  ---
  duration_ms: 5.306519
  type: 'test'
  ...
# Subtest: TSV: stale says the Model / Residual columns are the current, unfitted model
ok 74 - TSV: stale says the Model / Residual columns are the current, unfitted model
  ---
  duration_ms: 10.250872
  type: 'test'
  ...
# Subtest: the refresh re-renders Results only when its rendered state differs
ok 75 - the refresh re-renders Results only when its rendered state differs
  ---
  duration_ms: 3.818739
  type: 'test'
  ...
# Subtest: an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
ok 76 - an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
  ---
  duration_ms: 3.357902
  type: 'test'
  ...
# Subtest: Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
ok 77 - Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
  ---
  duration_ms: 4.065738
  type: 'test'
  ...
# Subtest: Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
ok 78 - Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
  ---
  duration_ms: 9.511463
  type: 'test'
  ...
# Subtest: closing the last tab clears the Results panel, header and status statistics too
ok 79 - closing the last tab clears the Results panel, header and status statistics too
  ---
  duration_ms: 0.206514
  type: 'test'
  ...
# Subtest: reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
ok 80 - reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
  ---
  duration_ms: 1.515206
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back
ok 81 - F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back
  ---
  duration_ms: 4.821985
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a Cloudflare 524 (plain-text body) is a failed request with its status, never "could not be read"
ok 82 - F2: Auto-Fit on a Cloudflare 524 (plain-text body) is a failed request with its status, never "could not be read"
  ---
  duration_ms: 5.913639
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a 500 with a JSON error is a failed request with its status, never "could not be read"
ok 83 - F2: Auto-Fit on a 500 with a JSON error is a failed request with its status, never "could not be read"
  ---
  duration_ms: 3.104037
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
# duration_ms 444.392031

exec
/bin/zsh -lc "rg -n 'function _showFitSpinner|function _hideFitSpinner|function _ownerActive|function _opOwner|runFit\\(\\)|runAutoFitC1sGraphite\\(' templates/index.html; nl -ba templates/index.html | sed -n '8188,8290p'; nl -ba fitting.py | sed -n '1720,1935p'; cat scripts/public_fit_poll_check.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
1904:      <button class="btn btn-green peak-fit-control" id="btn-run-fit" onclick="runFit()">Run Fit</button>
1918:          <button class="save-dropdown-item" id="auto-fit-c1s-menu-item" onclick="runAutoFitC1sGraphite()" title="Available only on C1s spectra (ROI midpoint 270–315 eV)"><span class="dd-icon">&#128293;</span><div>Auto-Fit C1s Graphite<small>One-click fit + charge correction</small></div></button>
2347:function _opOwner() {
2354:function _ownerActive(owner) {
5894:    if (k === 'f')                 { e.preventDefault(); runFit(); return; }
6688:function _showFitSpinner() {
6701:function _hideFitSpinner() {
7343:  // 5. Build state.fitResult exactly as runFit() does.
7362:  // 6. Update the same DOM elements runFit() updates.
7558:async function runAutoFitC1sGraphite() {
  8188	      return;
  8189	    }
  8190	    if (json.error) {
  8191	      const err = new Error(json.error);
  8192	      err.serverError = true;
  8193	      throw err;
  8194	    }
  8195	    // ACCEPTANCE RULE: the backend reports lmfit's own convergence flag. A
  8196	    // result that did not converge is a failed fit, not a result (audit A08:
  8197	    // until this unit success:false was applied and announced as complete).
  8198	    if (json.success !== true) {
  8199	      const err = new Error(json.message || 'the optimizer did not converge.');
  8200	      err.notConverged = true;
  8201	      throw err;
  8202	    }
  8203	    backendResult = json;
  8204	
  8205	    // If the user switched tabs while the fit was running, discard the result
  8206	    // rather than overwriting the now-active tab's peaks.
  8207	    if (!_ownerActive(fittingTab)) {
  8208	      _hideFitSpinner();
  8209	      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
  8210	      notify('Fit result discarded because you switched tabs during the fit.', 'amber');
  8211	      return;
  8212	    }
  8213	
  8214	    // The peak controls stay editable while the fit runs. A result computed for
  8215	    // the model as it was must not be applied over an edited one (a newly locked
  8216	    // centre would keep its edited value under the server's statistics).
  8217	    if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
  8218	      _hideFitSpinner();
  8219	      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
  8220	      notify('Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.', 'amber', true);
  8221	      return;
  8222	    }
  8223	
  8224	    // Capture pre-fit values for uncertainty validation
  8225	    const _preFit = {};
  8226	    for (const p of state.peaks) {
  8227	      _preFit[p.id] = { center: p.center, fwhm: p.fwhm, amplitude: p.amplitude, glMix: p.glMix };
  8228	    }
  8229	    applyBackendResult(backendResult);
  8230	    { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }   // a new result supersedes imported provenance
  8231	    const stats = backendResult.statistics || {};
  8232	    const chiReduced = stats.reduced_chi_square || 0;
  8233	    const rmse = Math.sqrt((backendResult.residuals || []).reduce((s, v) => s + v * v, 0) / Math.max(1, be.length));
  8234	    const roiRange = { min: _arrMin(be).toFixed(1), max: _arrMax(be).toFixed(1) };
  8235	    state.fitResult = { chi: chiReduced * Math.max(1, be.length - state.peaks.length * 3),
  8236	                        chiReduced, rmse, be, bgSubtracted, bgIntensity, backendResult,
  8237	                        fittedY: backendResult.fitted_y, roiRange, _preFit,
  8238	                        starts: backendResult.starts || null,
  8239	                        startsModelKey: _startsLiveKey(),     // model + context, taken AFTER the result was applied
  8240	                        chosenAlternative: opts.chosenAlternative || null };
  8241	    // a preview of an alternative always belongs to the PREVIOUS result (an identical
  8242	    // key does not make it this one's): clear it unconditionally
  8243	    if (_historyPreview && typeof _historyPreview.snapId === 'string' && _historyPreview.snapId.startsWith('alt:')) _historyPreview = null;
  8244	    state.fitResult.rFactor = _computeRFactor(state.fitResult);
  8245	    _applyStatDisplay(state.fitResult);
  8246	    document.getElementById('sb-msg').textContent = 'Fit complete (lmfit)';
  8247	    _updateRFactorUI(state.fitResult.rFactor);
  8248	    _updateROIDisplay(roiRange);
  8249	    _hideFitSpinner();
  8250	    notify('Fit complete. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3), 'green');
  8251	  } catch (e) {
  8252	    // Fall back to local Levenberg-Marquardt
  8253	    _hideFitSpinner();
  8254	    if (!_ownerActive(fittingTab)) {
  8255	      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
  8256	      notify('Fit cancelled — tab switched during fit.', 'amber');
  8257	      return;
  8258	    }
  8259	    if (e && e.transportFailure && opts.startPeaks) {
  8260	      // Adopting an alternative needs the server: the local engine would start
  8261	      // from the live model, not from the alternative. Nothing was changed.
  8262	      document.getElementById('sb-msg').textContent = 'Fit failed';
  8263	      notify('The server could not be reached, so the alternative was not applied. Previous peaks and result kept.', 'red', true);
  8264	      return;
  8265	    }
  8266	    if (e && e.transportFailure && ctxAtRequest !== null && !_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
  8267	      // The fallback would fit the arrays captured at the press over a model or
  8268	      // context edited since, and stamp the edited one (F1, Codex round 1).
  8269	      _hideFitSpinner();
  8270	      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
  8271	      notify('The server could not be reached, and the model or its background / ROI settings were edited while the fit was running, so no local fit was run. Previous peaks and result kept. Run the fit again.', 'amber', true);
  8272	      return;
  8273	    }
  8274	    if (e && e.transportFailure) {
  8275	      // Server unreachable: the local optimiser is the honest fallback, and
  8276	      // the overlay saying so opens only if it actually converged.
  8277	      if (e.message) console.warn('Backend unreachable, falling back to local LM:', e.message);
  8278	      const local = runFitLocal(be, bgSubtracted, bgIntensity);
  8279	      if (local && local.success && !_snapshotSuppressed) {
  8280	        document.getElementById('localfit-warn-overlay').classList.add('open');
  8281	      }
  8282	      return;
  8283	    }
  8284	    // Server-side error or non-converged optimisation: report it; the
  8285	    // previous peaks and fit result stay exactly as they were.
  8286	    const notConverged = !!(e && e.notConverged);
  8287	    document.getElementById('sb-msg').textContent = notConverged ? 'Fit did not converge' : 'Fit failed';
  8288	    notify((notConverged ? 'Fit did not converge: ' : 'Fit failed: ') + ((e && e.message) || 'unknown error') +
  8289	           ' Previous peaks and result kept.', 'red', true);
  8290	    return;
  1720	        raise RuntimeError("No peaks were built")
  1721	    if require_component is not None:
  1722	        ids = [str(spec["id"]) for spec in peak_specs]
  1723	        if str(require_component) not in ids:
  1724	            raise ValueError(f"require_component '{require_component}' is not one of the peaks")
  1725	        if len(ids) < 2:
  1726	            raise ValueError("require_component needs at least two components")
  1727	
  1728	    # Every random draw below (the perturbed restarts; the populations of the
  1729	    # two stochastic methods, which lmfit otherwise takes from numpy's GLOBAL
  1730	    # generator) comes from this one seed, so an identical request gives
  1731	    # identical DRAWS. (Not an identical Trust-Region result: see CLAUDE.md,
  1732	    # "Reproducibility".)
  1733	    if caller_seed is not None:
  1734	        random_seed = int(caller_seed)
  1735	    else:
  1736	        random_seed = _request_seed(
  1737	            x, y, bg, [spec.get("shape", "pseudo_voigt_gl") for spec in ordered],
  1738	            [f"p{spec['id']}_" for spec in ordered], all_params,
  1739	            fit_kws=fit_kws, n_perturb=n_perturb)
  1740	    # spawn(3) yields the same first two children as spawn(2): adding the
  1741	    # scattered-starts stream leaves every existing draw (and its pins) alone.
  1742	    perturb_rng, solver_rng, starts_rng = (np.random.default_rng(child)
  1743	                                           for child in np.random.SeedSequence(random_seed).spawn(3))
  1744	    if isinstance(n_starts, bool) or not isinstance(n_starts, (int, np.integer)) or not 0 <= n_starts <= MAX_N_STARTS:
  1745	        raise ValueError(f"n_starts must be an integer between 0 and {MAX_N_STARTS}")
  1746	
  1747	    # ── Determinacy (unit F2, 2026-09-26) ─────────────────────────────────────
  1748	    # "Nothing is a fit unless it converged and is determined." With at least
  1749	    # as many free parameters as data points the model can pass through every
  1750	    # point: lmfit reports redchi = chi2 / max(1, nfree) as if it were a fit,
  1751	    # and the support / required F tests clamp their dof to 1, so such a model
  1752	    # read as a near-perfect, fully supported fit (sweep M2: 6 points, 2 GL
  1753	    # components, chi2r 2.8e-6, both "supported"). A count, not a threshold:
  1754	    # zero or negative degrees of freedom is refused outright.
  1755	    n_free_request = sum(1 for par in all_params.values() if par.vary and not par.expr)
  1756	    n_data_request = int(np.count_nonzero(np.isfinite(y_sub)))
  1757	    if n_free_request >= n_data_request:
  1758	        raise ValueError(
  1759	            f"The model is not determined by these data: {n_free_request} free parameters for "
  1760	            f"{n_data_request} data points leaves no degrees of freedom. Widen the fitted range, "
  1761	            f"remove components or lock parameters.")
  1762	
  1763	    # ── Fit ───────────────────────────────────────────────────────────────────
  1764	    kws = {"method": "leastsq", "nan_policy": "omit"}
  1765	    if fit_kws:
  1766	        kws.update(fit_kws)
  1767	
  1768	    # Differential evolution needs a finite box and the page leaves amplitudes
  1769	    # open above: each candidate is searched in a generated box and then
  1770	    # refined under the request's own bounds (_search_then_refine). Every
  1771	    # other method fits the request's parameters exactly as before.
  1772	    def seeded(call_kws):
  1773	        """``call_kws`` with a fresh solver seed for the stochastic methods
  1774	        (one per minimisation, else every perturbed restart of differential
  1775	        evolution would replay the same population); unchanged otherwise."""
  1776	        if call_kws.get("method") not in _STOCHASTIC_METHODS:
  1777	            return call_kws
  1778	        solver_kws = dict(call_kws.get("fit_kws") or {})
  1779	        solver_kws["seed"] = int(solver_rng.integers(0, 2 ** 32 - 1))
  1780	        return {**call_kws, "fit_kws": solver_kws}
  1781	
  1782	    # One fitter for any (sub)model of this request: the DE candidate machinery
  1783	    # when the method is differential evolution, else a plain seeded fit. The
  1784	    # scattered starts and the required-component refit go through it too.
  1785	    requested_bounds = {name: (par.min, par.max) for name, par in all_params.items()}
  1786	
  1787	    def fit_model(model, params):
  1788	        if kws.get("method") == "differential_evolution":
  1789	            bounds = {name: requested_bounds.get(name, (par.min, par.max)) for name, par in params.items()}
  1790	            return _global_or_local_candidate(model, params, bounds, y_sub, x, weights, seeded(kws))
  1791	        if kws.get("method") == "basinhopping":
  1792	            bounds = {name: requested_bounds.get(name, (par.min, par.max)) for name, par in params.items()}
  1793	            return _basinhopping_candidate(model, params, bounds, y_sub, x, weights, seeded(kws))
  1794	        return model.fit(y_sub, params, x=x, weights=weights, **seeded(kws), **_cancel_kw())
  1795	
  1796	    def fit_once(params):
  1797	        return fit_model(composite_model, params)
  1798	
  1799	    # ── Diagnostic logging: BEFORE optimisation ──────────────────────────────
  1800	    if log.isEnabledFor(logging.DEBUG):
  1801	        log.debug("═══ FIT START ═══  method=%s  n_data=%d", kws.get('method'), len(y_sub))
  1802	        for pname, par in sorted(all_params.items()):
  1803	            log.debug("  BEFORE  %-30s value=%12.6f  vary=%-5s  expr=%s  min=%s  max=%s",
  1804	                      pname, par.value, str(par.vary), par.expr,
  1805	                      f"{par.min:.4f}" if np.isfinite(par.min) else '-inf',
  1806	                      f"{par.max:.4f}" if np.isfinite(par.max) else 'inf')
  1807	
  1808	    try:
  1809	        result = fit_once(all_params)
  1810	    except Exception as exc:
  1811	        raise RuntimeError(f"lmfit fitting failed: {exc}") from exc
  1812	
  1813	    # ── Diagnostic logging: AFTER optimisation ───────────────────────────────
  1814	    if log.isEnabledFor(logging.DEBUG):
  1815	        log.debug("═══ FIT DONE ═══  success=%s  nfev=%s  message=%s",
  1816	                  result.success, result.nfev, result.message)
  1817	        for pname, par in sorted(result.params.items()):
  1818	            init = all_params[pname].value if pname in all_params else None
  1819	            delta = f"  Δ={par.value - init:+.6f}" if init is not None and abs(par.value - init) > 1e-10 else ""
  1820	            log.debug("  AFTER   %-30s value=%12.6f  stderr=%s%s",
  1821	                      pname, par.value,
  1822	                      f"{par.stderr:.6f}" if par.stderr is not None else 'None', delta)
  1823	
  1824	    # ── Perturb and refit to escape local minima ─────────────────────────
  1825	    # Not for basinhopping (unit F2, 2026-09-26, owner): it is already a global
  1826	    # search, so perturbed restarts add nothing — the reason the scattered-
  1827	    # starts check excludes it — and with the page's n_perturb 3 they
  1828	    # quadrupled its time past the server's 300 s timeout on 14 of 16 sampled
  1829	    # multi-component targets (median 386 s, max 1066 s; without them median
  1830	    # 96 s, max 256 s, and chi2r identical to 1e-8 on all 16).
  1831	    if n_perturb > 0 and result.success and kws.get("method") != "basinhopping":
  1832	        best_result = result
  1833	        best_redchi = result.redchi if result.redchi is not None else float('inf')
  1834	        rng = perturb_rng
  1835	
  1836	        for attempt in range(n_perturb):
  1837	            perturbed_params = result.params.copy()
  1838	            for pname, par in perturbed_params.items():
  1839	                if par.vary and par.value != 0:
  1840	                    # Perturb by ±15% random
  1841	                    scale = 1.0 + rng.uniform(-0.15, 0.15)
  1842	                    new_val = par.value * scale
  1843	                    # Respect bounds
  1844	                    if np.isfinite(par.min):
  1845	                        new_val = max(new_val, par.min)
  1846	                    if np.isfinite(par.max):
  1847	                        new_val = min(new_val, par.max)
  1848	                    perturbed_params[pname].set(value=new_val)
  1849	                elif par.vary and par.value == 0:
  1850	                    # For zero-valued params, add small absolute perturbation
  1851	                    perturbed_params[pname].set(value=rng.uniform(0.001, 0.05))
  1852	
  1853	            try:
  1854	                trial = fit_once(perturbed_params)
  1855	                trial_redchi = trial.redchi if trial.redchi is not None else float('inf')
  1856	                log.debug("  PERTURB %d/%d  redchi=%.4f  (best=%.4f)",
  1857	                          attempt + 1, n_perturb, trial_redchi, best_redchi)
  1858	                # A candidate whose search box was never cleared by its
  1859	                # refinement (differential evolution only) does not displace
  1860	                # one that was; for every other method both flags are False.
  1861	                trial_rank = (getattr(trial, "box_unverified", False), trial_redchi)
  1862	                best_rank = (getattr(best_result, "box_unverified", False), best_redchi)
  1863	                if trial.success and trial_rank < best_rank:
  1864	                    best_result = trial
  1865	                    best_redchi = trial_redchi
  1866	                    log.debug("  *** New best found! redchi improved to %.4f", best_redchi)
  1867	            except Exception:
  1868	                log.debug("  PERTURB %d/%d  failed (exception)", attempt + 1, n_perturb)
  1869	                continue
  1870	
  1871	        if best_result is not result:
  1872	            log.debug("═══ PERTURB IMPROVED FIT ═══  redchi: %.4f → %.4f",
  1873	                      result.redchi, best_redchi)
  1874	            result = best_result
  1875	
  1876	    # ── Scattered starts (never changes `result`) ────────────────────────────
  1877	    starts = None
  1878	    if n_starts:
  1879	        n_unlinked = sum(1 for spec in peak_specs if spec.get("constrain_to") is None)
  1880	        if kws.get("method") not in _STARTS_METHODS:
  1881	            starts = {"ran": False, "reason": "method"}          # a global method already searches
  1882	        elif n_unlinked < 2:
  1883	            starts = {"ran": False, "reason": "single_component"}
  1884	        elif not result.success:
  1885	            starts = {"ran": False, "reason": "fit_not_converged"}
  1886	        else:
  1887	            try:
  1888	                starts = _scattered_starts(int(n_starts), fit_once, composite_model, all_params, result,
  1889	                                           peak_specs, x, starts_rng)
  1890	            except Exception as exc:                              # the check must never cost the student the fit
  1891	                log.exception("scattered starts failed")
  1892	                starts = {"ran": False, "reason": "error", "error": f"{type(exc).__name__}: {exc}"[:200]}
  1893	
  1894	    # ── "Is this component required?" (never changes `result`) ─────────────
  1895	    required = None
  1896	    if require_component is not None:
  1897	        rprefix = f"p{require_component}_"
  1898	        if not result.success:
  1899	            required = {"ran": False, "reason": "fit_not_converged"}
  1900	        else:
  1901	            try:
  1902	                # remove the component and everything linked to it, transitively
  1903	                master_of = {str(sp["id"]): sp.get("constrain_to") for sp in peak_specs}
  1904	                removed = {str(require_component)}
  1905	                grew = True
  1906	                while grew:
  1907	                    grew = False
  1908	                    for pid, master in master_of.items():
  1909	                        if master is not None and str(master) in removed and pid not in removed:
  1910	                            removed.add(pid); grew = True
  1911	                removed_prefixes = [f"p{pid}_" for pid in removed]
  1912	                without = None
  1913	                for m in composite_model.components:
  1914	                    if m.prefix in removed_prefixes:
  1915	                        continue
  1916	                    without = m if without is None else without + m
  1917	                if without is None:
  1918	                    required = {"ran": False, "reason": "nothing_left"}
  1919	                else:
  1920	                    n_free_comp = sum(1 for n, par in result.params.items()
  1921	                                      if n.startswith(rprefix) and par.vary and par.expr is None)
  1922	                    required = {"ran": True, **_component_required(
  1923	                        lambda params: fit_model(without, params), result.params, removed_prefixes, y_sub, weights,
  1924	                        float(result.chisqr), n_free_comp, result.nvarys)}
  1925	            except Exception as exc:                              # the check must never cost the student the fit
  1926	                log.exception("required-component refit failed")
  1927	                required = {"ran": False, "reason": "error", "error": f"{type(exc).__name__}: {exc}"[:200]}
  1928	
  1929	    # Sides WE closed on the returned result (non-empty only for a
  1930	    # differential-evolution result whose refinement did not take over).
  1931	    search_box = getattr(result, "search_box", {})
  1932	
  1933	    fitted_sub = result.best_fit
  1934	    fitted_y = fitted_sub + bg
  1935	
#!/usr/bin/env python3
"""Post-deploy check for unit 2 (long fits via start-then-poll), THROUGH THE
PUBLIC URL — the path a student's browser takes, where Cloudflare ends a
single request at ~100 s (HTTP 524).

It does what the page does for Run Fit: upload, POST /api/fit/start, poll
GET /api/fit/progress every 0.5 s until the job leaves "running"; it records
the duration of EVERY request. PASS = the job finishes "done" with
success true, and no request took longer than MAX_REQUEST_S.

Usage:
  python scripts/public_fit_poll_check.py targets.json [BASE_URL] [target_id ...]

targets.json: the optimizer-disagreement target file (branch
investigate-optimizer-disagreement, docs/findings/optimizer-disagreement/
targets.json). Default targets: the five largest committed C 1s models,
the ones that took 183-256 s even without restarts.
"""
import json
import sys
import time
import urllib.error
import urllib.request
import uuid

MAX_REQUEST_S = 10.0
DEFAULT_TARGETS = ["edf39ecb66ce", "d2bd62d2f976", "496c4edd97af", "0a5f464daf3d", "8b4c2f656a80"]


def _req(url, data=None, headers=None, method=None, timeout=60):
    t0 = time.time()
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "xps-poll-check", **(headers or {})}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body, status = r.read(), r.status
    except urllib.error.HTTPError as e:
        body, status = e.read(), e.code
    return status, body, time.time() - t0


def run(base, t):
    durations = []
    csv = "\n".join(f"{a:.4f},{b:.4f}" for a, b in zip(t["be"], t["inten"])).encode()
    bnd = uuid.uuid4().hex
    form = (f"--{bnd}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"t.csv\"\r\n"
            f"Content-Type: text/csv\r\n\r\n").encode() + csv + f"\r\n--{bnd}--\r\n".encode()
    st, body, d = _req(base + "/api/upload", form, {"Content-Type": f"multipart/form-data; boundary={bnd}"})
    durations.append(("upload", st, d))
    sid = json.loads(body)["session_id"]
    bg = t["background"]
    payload = {"session_id": sid, "background": {k: bg[k] for k in ("method", "start_idx", "end_idx", "endpoint_avg")},
               "peaks": t["specs"], "fit_method": "basinhopping", "n_perturb": 3, "n_starts": 3}
    st, body, d = _req(base + "/api/fit/start", json.dumps(payload).encode(), {"Content-Type": "application/json"})
    durations.append(("start", st, d))
    if st != 202:
        return {"id": t["id"], "verdict": "FAIL", "why": f"start returned {st}: {body[:200]!r}", "durations": durations}
    job = json.loads(body)["job_id"]
    t0 = time.time()
    while True:
        time.sleep(0.5)
        st, body, d = _req(base + f"/api/fit/progress/{job}")
        durations.append(("poll", st, d))
        rec = json.loads(body) if st == 200 else {"status": f"http {st}"}
        if rec.get("status") != "running":
            break
    longest = max(x[2] for x in durations)
    res = rec.get("result") or {}
    ok = rec.get("status") == "done" and res.get("success") is True and longest <= MAX_REQUEST_S
    return {"id": t["id"], "verdict": "PASS" if ok else "FAIL", "status": rec.get("status"),
            "success": res.get("success"), "chi2r": (res.get("statistics") or {}).get("reduced_chi_square"),
            "fit_wall_s": round(time.time() - t0, 1), "n_requests": len(durations),
            "longest_request_s": round(longest, 2), "error": rec.get("error")}


def main():
    targets = json.load(open(sys.argv[1]))
    base = sys.argv[2] if len(sys.argv) > 2 else "https://xps.fortierlab.org"
    ids = sys.argv[3:] or DEFAULT_TARGETS
    by_id = {t["id"]: t for t in targets}
    results = [run(base, by_id[i]) for i in ids]
    for r in results:
        print(json.dumps(r))
    print("OVERALL:", "PASS" if all(r["verdict"] == "PASS" for r in results) else "FAIL")


if __name__ == "__main__":
    main()

exec
/bin/zsh -lc "sed -n '2335,2370p;5870,5902p;6675,6720p' templates/index.html; rg -n 'def __residual|iter_cb|def _calculate_covariance_matrix|AbortFitException|def basinhopping' /Users/skyefortier/xps-app/venv/lib/python*/site-packages/lmfit/minimizer.py; nl -ba app.py | sed -n '500,550p'; rg -n 'MAX_CONTENT|MAX.*POINT|limit|rate' app.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
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

  if (e.key === 'Escape') {
    if (document.getElementById('spec-combo-drop').classList.contains('open')) {
      _ssClose(); return;
    }
    document.querySelectorAll('.xps-modal-overlay.open').forEach(m => m.classList.remove('open'));
    if (typeof _closeHistoryPanel === 'function') _closeHistoryPanel();
    const multipletOverlay = document.getElementById('multiplet-modal-overlay');
    if (multipletOverlay && multipletOverlay.classList.contains('open')) {
      _closeMultipletModal();
    }
    if (placeMode) togglePlaceMode(placeMode);
    return;
  }

  if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') return;

  if (e.ctrlKey || e.metaKey) {
    const k = (e.key || '').toLowerCase();   // shifted letters report 'Z', not 'z'
    if (k === 'z' && !e.shiftKey) { e.preventDefault(); undo(); return; }
    if (k === 'z' && e.shiftKey)  { e.preventDefault(); redo(); return; }
    if (k === 'y')                 { e.preventDefault(); redo(); return; }
    if (k === 's' && !e.shiftKey)  { e.preventDefault(); saveFit(); return; }
    if (k === 's' && e.shiftKey)   { e.preventDefault(); saveSpectrum(); return; }
    if (k === 'f')                 { e.preventDefault(); runFit(); return; }
    return;
  }

  switch (e.key) {
    case 'Delete':
    case 'Backspace': {
      const body = document.querySelector('.peak-body.open');
      if (body) {
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
94:class AbortFitException(MinimizerException):
349:                 iter_cb=None, scale_covar=True, nan_policy='raise',
367:        iter_cb : callable, optional
371:                iter_cb(params, iter, resid, *fcn_args, **fcn_kws)
452:        self.iter_cb = iter_cb
493:    def __residual(self, fvars, apply_bounds_transformation=True):
538:            raise AbortFitException(f"fit aborted: too many function evaluations {self.max_nfev}")
542:        if callable(self.iter_cb):
543:            abort = self.iter_cb(params, self.result.nfev, out,
552:            raise AbortFitException("fit aborted by user.")
733:    def _calculate_covariance_matrix(self, fvars):
989:            except AbortFitException:
996:            except AbortFitException:
1089:        if callable(self.iter_cb):
1090:            abort = self.iter_cb(params, self.result.nfev, out,
1096:            raise AbortFitException("fit aborted by user.")
1425:        except AbortFitException:
1568:        except AbortFitException:
1675:        except AbortFitException:
1693:        except AbortFitException:
1726:    def basinhopping(self, params=None, max_nfev=None, **kws):
1771:        except AbortFitException:
1923:        except AbortFitException:
2072:        except AbortFitException:
2153:        except AbortFitException:
2232:        except AbortFitException:
2473:def minimize(fcn, params, method='leastsq', args=None, kws=None, iter_cb=None,
2537:    iter_cb : callable, optional
2541:            iter_cb(params, iter, resid, *args, **kws),
2606:                           iter_cb=iter_cb, scale_covar=scale_covar,
2613:                       iter_cb=iter_cb, scale_covar=scale_covar,
   500	    the exact wording the goal asked for ('candidate 7 of 29 . stabilizing')."""
   501	    phase = evt.get("phase")
   502	    idx, total = evt.get("candidate_index"), evt.get("candidate_total")
   503	    name = evt.get("candidate_name")
   504	    if phase == "screening" and idx and total:
   505	        msg = f"screening candidate {idx} of {total}"
   506	    elif phase == "stabilizing" and idx and total:
   507	        msg = f"candidate {idx} of {total} — stabilizing"
   508	    else:
   509	        return phase or "working…"
   510	    return msg + (f" ({name})" if name else "")
   511	
   512	
   513	def _job_progress_path(job_id: str, upload_folder: str) -> Path:
   514	    return Path(upload_folder) / f"{job_id}.job.json"
   515	
   516	
   517	def _write_job_progress(job_id: str, upload_folder: str, data: dict) -> None:
   518	    """Atomic write (temp file + os.replace) — required because the
   519	    writer (background thread, possibly in a DIFFERENT gunicorn worker
   520	    process than whichever one later serves a poll GET) and the reader
   521	    are never synchronized otherwise; a half-written file must never be
   522	    visible to a concurrent poll."""
   523	    path = _job_progress_path(job_id, upload_folder)
   524	    tmp = path.with_suffix(".tmp")
   525	    try:
   526	        tmp.write_text(json.dumps(_json_sanitize(data)))
   527	        os.replace(tmp, path)
   528	    except OSError:
   529	        logging.getLogger(__name__).exception(
   530	            "failed to write progress for job %s", job_id)
   531	
   532	
   533	def _sweep_expired_jobs(upload_folder: str) -> None:
   534	    """Opportunistic TTL cleanup of stale job progress files — same
   535	    pattern as _sweep_expired_sessions (audit F13): runs on each new job
   536	    start, no scheduler/thread, tolerates a concurrent worker deleting the
   537	    same file first, never raises."""
   538	    cutoff = time.time() - _ANALYZE_JOB_TTL_SEC
   539	    try:
   540	        candidates = list(Path(upload_folder).glob("*.job.json"))
   541	    except OSError:
   542	        return
   543	    for p in candidates:
   544	        try:
   545	            if p.stat().st_mtime < cutoff:
   546	                p.unlink(missing_ok=True)
   547	        except FileNotFoundError:
   548	            pass
   549	        except OSError:
   550	            pass
177:    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB hard limit
200:    inf/NaN (e.g. BIC of a degenerate fit) must not emit non-standard JSON
233:    ``*.npz`` session files (never .vgd scratch or temp uploads), tolerates a
461:                "curated windows to enable grammar fitting for: "
536:    start, no scheduler/thread, tolerates a concurrent worker deleting the
1028:        its form.  ``regions`` is UNCHANGED (still just the 5 curated
1030:        every selectable Z=1..96 region, tiered curated/machine/
1113:        an in-process dict, because gunicorn's workers are separate OS
1204:            # os.replace() makes writes atomic, but tolerate a read racing
1283:        return jsonify({"error": "File too large (limit 50 MB)"}), 413

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import fitting, numpy as np, time
x=np.linspace(281,292,200)
y=300+5000*np.exp(-4*np.log(2)*((x-284.5)/.9)**2)+1500*np.exp(-4*np.log(2)*((x-286.2)/1.1)**2)
p=[dict(id=str(i),shape=\"pseudo_voigt_gl\",center=c+.1,fwhm=w*1.1,amplitude=a*.8,gl_ratio=.3,amplitude_min=0) for i,(c,a,w) in enumerate([(284.5,5000,.9),(286.2,1500,1.1)])]
for method in [\"leastsq\",\"least_squares\",\"nelder\",\"differential_evolution\",\"basinhopping\"]:
 t=time.monotonic()
 try:
  r=fitting.run_fit(energy=x,counts=y,peak_specs=p,background_method=\"shirley\",fit_kws={\"method\":method},n_perturb=0,cancel=lambda:True)
  print(method,\"RETURN\",r[\"success\"])
 except Exception as e:print(method,type(e).__name__,str(e)[:250],round(time.monotonic()-t,3))
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 exited 1 in 1031ms:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/fitting.py", line 35, in <module>
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
FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll']

codex
All 83 focused JavaScript tests pass. I found a reachable gap outside their coverage: Ctrl/Cmd+F bypasses the disabled Run Fit button, and the new helper has no per-tab supersession check. I’m testing that path and cancellation across all five solvers. The Python fixtures need writable temporary storage, so I’m using in-memory probes where possible.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile
tempfile.tempdir=\"/tmp\"
import sys
sys.modules[\"matplotlib\"]=None
import fitting, numpy as np, time
x=np.linspace(281,292,200)
y=300+5000*np.exp(-4*np.log(2)*((x-284.5)/.9)**2)+1500*np.exp(-4*np.log(2)*((x-286.2)/1.1)**2)
p=[dict(id=str(i),shape=\"pseudo_voigt_gl\",center=c+.1,fwhm=w*1.1,amplitude=a*.8,gl_ratio=.3,amplitude_min=0) for i,(c,a,w) in enumerate([(284.5,5000,.9),(286.2,1500,1.1)])]
for method in [\"leastsq\",\"least_squares\",\"nelder\",\"differential_evolution\",\"basinhopping\"]:
 t=time.monotonic()
 try:
  r=fitting.run_fit(energy=x,counts=y,peak_specs=p,background_method=\"shirley\",fit_kws={\"method\":method},n_perturb=0,cancel=lambda:True)
  print(method,\"RETURN\",r[\"success\"])
 except Exception as e:print(method,type(e).__name__,str(e)[:250],round(time.monotonic()-t,3))
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 1411ms:
leastsq AttributeError 'ModelResult' object has no attribute 'aic' 0.005
least_squares FitCancelled the fit was cancelled 0.004
nelder RuntimeError lmfit fitting failed: fit aborted by user. 0.004
differential_evolution RuntimeError lmfit fitting failed: fit aborted by user. 0.006
basinhopping FitCancelled the fit was cancelled 0.013

exec
/bin/zsh -lc "sed -n '520,557p;733,775p;1760,1805p' /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py; sed -n '1,170p' /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/gunicorn/workers/sync.py; nl -ba tests/js/fit_acceptance.test.js | sed -n '105,164p'; nl -ba app.py | sed -n '606,682p'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:

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
    def _calculate_covariance_matrix(self, fvars):
        """Calculate the covariance matrix.

        The ``numdiftoools`` package is used to estimate the Hessian
        matrix, and the covariance matrix is calculated as:

        .. math::

            cov_x = inverse(Hessian) * 2.0

        Parameters
        ----------
        fvars : numpy.ndarray
            Array of the optimal internal, freely variable parameters.

        Returns
        -------
        cov_x : numpy.ndarray or None
            Covariance matrix if successful, otherwise None.

        """
        warnings.filterwarnings(action="ignore", module="scipy",
                                message="^internal gelsd")

        nfev = deepcopy(self.result.nfev)
        best_vals = self.result.params.valuesdict()

        try:
            Hfun = ndt.Hessian(self.penalty, step=1.e-4)
            hessian_ndt = Hfun(fvars)
            cov_x = inv(hessian_ndt) * 2.0

            if cov_x.diagonal().min() < 0:
                # we know the calculated covariance is incorrect, so we set the covariance to None
                cov_x = None
        except (LinAlgError, ValueError):
            cov_x = None
        finally:
            self.result.nfev = nfev

        # restore original values
        for name in self.result.var_names:
            self.result.params[name].value = float(best_vals[name])
                                accept_test=None, callback=None, interval=50,
                                disp=False, niter_success=None, seed=None,
                                target_accept_rate=0.5, stepwise_factor=0.9)

        basinhopping_kws.update(self.kws)
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
        and cannot be changed:

        +-------------------+-------+------------------------------------+
        | :meth:`brute` arg | Value | Description                        |
        +===================+=======+====================================+
        |  `full_output`    | 1     | Return the evaluation grid and the |
        |                   |       | objective function's values on it. |
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
   105	  assert.ok(!/complete/i.test(env.dom['sb-msg'].textContent), env.dom['sb-msg'].textContent);
   106	});
   107	
   108	test('a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser', async () => {
   109	  const env = makeEnv({ fetchImpl: async () => ({ ok: false, status: 400, json: async () => ({ error: 'peak 1: fwhm_min must be positive' }) }) });
   110	  const before = JSON.stringify(env.state.peaks);
   111	  await env.runFit();
   112	  assert.equal(env.calls.local, 0, 'a 400 is not a reason to run the local fitter');
   113	  assert.equal(env.calls.applied, 0);
   114	  assert.equal(JSON.stringify(env.state.peaks), before);
   115	  assert.ok(env.calls.notify.some(n => n.kind === 'red' && /fwhm_min must be positive/.test(n.msg)), JSON.stringify(env.calls.notify));
   116	  assert.notEqual(env.dom['localfit-warn-overlay']?.classList._c, 'open', 'no "local fit performed" overlay');
   117	});
   118	
   119	test('a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay', async () => {
   120	  const env = makeEnv({ fetchImpl: async () => { throw new TypeError('Failed to fetch'); } });
   121	  await env.runFit();
   122	  assert.equal(env.calls.local, 1, 'local fallback used for a genuine network failure');
   123	  assert.equal(env.dom['localfit-warn-overlay'].classList._c, 'open');
   124	});
   125	
   126	test('a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay', async () => {
   127	  const env = makeEnv({ fetchImpl: async () => { throw new TypeError('Failed to fetch'); } });
   128	  // replace the stubbed local fitter with a failing one
   129	  const failing = makeEnv({ fetchImpl: async () => { throw new TypeError('Failed to fetch'); } });
   130	  failing.calls.local = 0;
   131	  // rebuild with a failing runFitLocal
   132	  const dom = failing.dom;
   133	  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n') + '\n' + POLL_SRC;
   134	  const noop = () => {};
   135	  const owner = { id: 1 };
   136	  const state = failing.state;
   137	  const { runFit } = new Function('document', 'state', 'fetch', 'uploadToBackend', 'notify', 'pushUndo', '_showFitSpinner', '_hideFitSpinner',
   138	    '_opOwner', '_ownerActive', 'getROIData', 'computeBackground', 'peakToBackendSpec', '_getManualAnchors', 'applyBackendResult',
   139	    '_computeRFactor', '_CHISQ_TOOLTIP', '_updateRFactorUI', '_updateROIDisplay', 'renderPeakList', 'updatePlot', 'renderResults',
   140	    '_autoSnapshot', 'runFitLocal', '_snapshotSuppressed', 'console', '_applyStatDisplay', '_activeTab', src + '\nreturn { runFit };')(
   141	    { getElementById: id => (dom[id] ||= { value: '', textContent: '', style: {}, setAttribute() {}, classList: { add(c) { this._c = c; }, remove() { this._c = null; }, _c: null } }), querySelector: () => ({}), querySelectorAll: () => [] },
   142	    state, async () => { throw new TypeError('Failed to fetch'); }, async () => 'sid', noop, noop, noop, noop, () => owner, o => o === owner,
   143	    () => ({ be: state.rawBE.slice(), inten: state.rawIntensity.slice() }), b => b.map(() => 0), p => ({ id: p.id }), () => [], noop,
   144	    () => 0.1, '', noop, noop, noop, noop, noop, noop, () => ({ success: false, message: 'did not converge' }), false, { warn: noop }, noop, () => owner);
   145	  await runFit();
   146	  assert.notEqual(dom['localfit-warn-overlay']?.classList._c, 'open', 'overlay must not claim a local fit was performed');
   147	  void env;
   148	});
   149	
   150	test('a converged backend result is applied (sanity)', async () => {
   151	  const env = makeEnv({ fetchImpl: okResponse({ success: true, statistics: { reduced_chi_square: 1.2 }, residuals: [], fitted_y: [], individual_peaks: [] }) });
   152	  await env.runFit();
   153	  assert.equal(env.calls.applied, 1);
   154	  assert.equal(env.calls.local, 0);
   155	  assert.notEqual(env.state.fitResult.marker, 'previous');
   156	  assert.equal(env.dom['sb-msg'].textContent, 'Fit complete (lmfit)', 'the success path must run to completion, not die in an exception');
   157	});
   158	
   159	test('the engine/objective labels of a fit result survive spectrum and project save/load', () => {
   160	  const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
   161	  // spectrum save: statistics block carries objective/engine; loader restores them
   162	  const save = grab('function _doSaveSpectrum()', 2500);
   163	  assert.match(save, /objective: state\.fitResult\.objective/);
   164	  assert.match(save, /engine: state\.fitResult\.engine/);
   606	                        m.unlink(missing_ok=True)
   607	                except OSError:
   608	                    pass
   609	        except OSError:
   610	            pass
   611	
   612	
   613	def _fit_job_cancel(job_id: str, upload_folder: str) -> None:
   614	    try:
   615	        _fit_job_marker(job_id, upload_folder, "cancel").touch()
   616	    except OSError:
   617	        pass
   618	
   619	
   620	def _fit_job_start(job_id: str, upload_folder: str, fit_args: dict, run) -> None:
   621	    """Start the fit thread and its heartbeat thread. ``run(fit_args, cancel)``
   622	    returns ``(status, body)``; ``(None, None)`` means cancelled."""
   623	    started = time.time()
   624	    lock = threading.Lock()
   625	    rec = {"status": "running", "elapsed_sec": 0.0, "heartbeat": started}
   626	    _fit_job_write(job_id, upload_folder, rec)
   627	    _fit_job_marker(job_id, upload_folder, "polled").touch()
   628	    cancel_path = _fit_job_marker(job_id, upload_folder, "cancel")
   629	    polled_path = _fit_job_marker(job_id, upload_folder, "polled")
   630	    finished = threading.Event()
   631	
   632	    def cancelled() -> bool:
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
   680	        if not request.is_json:
   681	            return _err("Request must be JSON (Content-Type: application/json)")
   682	        return f(*args, **kwargs)

exec
/bin/zsh -lc "tail -35 app.py; nl -ba fitting.py | sed -n '2090,2120p'; nl -ba scripts/public_fit_poll_check.py | sed -n '54,88p'; nl -ba templates/index.html | sed -n '7480,7526p'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:


def _preview(
    energy: np.ndarray,
    counts: np.ndarray,
    max_pts: int = 2000,
) -> dict:
    """Return (possibly downsampled) energy/counts lists for API responses."""
    n = len(energy)
    if n <= max_pts:
        return {"energy": energy.tolist(), "counts": counts.tolist()}
    # Uniform stride downsample (preserves endpoints)
    idx = np.round(np.linspace(0, n - 1, max_pts)).astype(int)
    return {
        "energy": energy[idx].tolist(),
        "counts": counts[idx].tolist(),
        "downsampled": True,
        "original_n_points": n,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Module‑level app instance for gunicorn / flask CLI
# ─────────────────────────────────────────────────────────────────────────────

app = create_app()

if __name__ == "__main__":
    # Development server only – gunicorn does NOT call this block.
    # Debug mode defaults OFF to avoid exposing the Werkzeug debugger
    # (which allows arbitrary code execution from the browser). Set
    # FLASK_DEBUG=1 explicitly during local development.
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug)
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
    74	
    75	def main():
    76	    targets = json.load(open(sys.argv[1]))
    77	    base = sys.argv[2] if len(sys.argv) > 2 else "https://xps.fortierlab.org"
    78	    ids = sys.argv[3:] or DEFAULT_TARGETS
    79	    by_id = {t["id"]: t for t in targets}
    80	    results = [run(base, by_id[i]) for i in ids]
    81	    for r in results:
    82	        print(json.dumps(r))
    83	    print("OVERALL:", "PASS" if all(r["verdict"] == "PASS" for r in results) else "FAIL")
    84	
    85	
    86	if __name__ == "__main__":
    87	    main()
  7480	function _fitHttpError(status, msg, prefix) {
  7481	  const err = new Error(msg || ((prefix || 'Fit request failed') + ' (HTTP ' + status + ').'));
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

exec
/bin/zsh -lc "node -e 'const fs=require(\"fs\"),path=require(\"path\");
const testfile=path.resolve(\"tests/js/fit_start_poll.test.js\");
const prefix=fs.readFileSync(testfile,\"utf8\").split(\"test('\\''start ->\")[0];
const {make,server,ok}=new Function(\"require\",\"__dirname\",prefix+\";return {make,server,ok}\")(require,path.dirname(testfile));
let starts=0; const polls={};
const s=server(u=>u===\"/api/fit/start\"?ok({job_id:\"J\"+(++starts)},202):u.includes(\"/progress/\")?((polls[u]=(polls[u]||0)+1)<4?ok({status:\"running\",heartbeat_age_sec:0}):ok({status:\"done\",result:{success:true}})):ok({}));
const { _serverFitJob }=make(s.fetch);
Promise.all([_serverFitJob({}, {abandoned:()=>null}),_serverFitJob({}, {abandoned:()=>null})]).then(r=>console.log(JSON.stringify({starts,polls,cancelCalls:s.calls.filter(c=>c.url.includes(\"/cancel/\")).length,results:r})));
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
{"starts":2,"polls":{"/api/fit/progress/J1":4,"/api/fit/progress/J2":4},"cancelCalls":0,"results":[{"success":true},{"success":true}]}

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile, sys
tempfile.tempdir=\"/tmp\"
sys.modules[\"matplotlib\"]=None
import fitting,numpy as np,time,json
x=np.linspace(281,292,300)
comps=[(283.2,2000,.8),(284.5,5000,.9),(285.4,1800,1),(286.6,1500,1.1),(288.4,900,1.4)]
rng=np.random.default_rng(3)
y=rng.poisson(300+sum(a*np.exp(-4*np.log(2)*((x-c)/w)**2) for c,a,w in comps)).astype(float)
p=[dict(id=str(i),shape=\"pseudo_voigt_gl\",center=c+.1,fwhm=w*1.1,amplitude=a*.8,gl_ratio=.3,amplitude_min=0) for i,(c,a,w) in enumerate(comps)]
for method in [\"leastsq\",\"least_squares\",\"nelder\",\"differential_evolution\",\"basinhopping\"]:
 start=time.monotonic()
 def cancel():return time.monotonic()-start>.3
 try:
  r=fitting.run_fit(energy=x,counts=y,peak_specs=p,background_method=\"shirley\",fit_kws={\"method\":method},n_perturb=3,n_starts=3,cancel=cancel)
  print(method,\"completed before cancel\",round(time.monotonic()-start,3),flush=True)
 except Exception as e:print(method,type(e).__name__,str(e)[:150],round(time.monotonic()-start,3),flush=True)
args=dict(energy=x,counts=y,peak_specs=p,background_method=\"shirley\",fit_kws={\"method\":\"leastsq\"},n_perturb=0,n_starts=0)
a=fitting.run_fit(**args); b=fitting.run_fit(**args,cancel=lambda:False)
print(\"leastsq sync/hook identity\",json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True),flush=True)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 5114ms:
leastsq AttributeError 'ModelResult' object has no attribute 'aic' 0.511
least_squares FitCancelled the fit was cancelled 0.376
nelder RuntimeError lmfit fitting failed: fit aborted by user. 0.509
differential_evolution RuntimeError lmfit fitting failed: fit aborted by user. 0.512
basinhopping FitCancelled the fit was cancelled 0.523
leastsq sync/hook identity True

exec
/bin/zsh -lc "sed -n '7415,7448p' templates/index.html; git diff --check fix-acceptance-holes..HEAD; rg -n 'delegat|sub.agent|parallel agent|review|test' CLAUDE.md | tail -25; nl -ba app.py | sed -n '1224,1247p'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
  const text = await resp.text();                 // rejects only on transport
  try { return JSON.parse(text); } catch (_) {
    // A NaN / Infinity TOKEN, never the word inside a JSON string (Codex
    // round 1) — one linear pass that tracks string and escape state to the
    // end of the body, so a string cut off by a truncated body stays a string
    // and no body, however malformed, costs more than one scan (round 2: a
    // regex that blanked strings was quadratic on an unterminated escaped
    // string, 10 s for 128 KB on the page's thread).
    const nonFinite = (function (t) {
      const bound = ch => ch === undefined || ch === ' ' || ch === '\n' || ch === '\r' || ch === '\t' ||
        ch === ',' || ch === ':' || ch === '[' || ch === ']' || ch === '\x7b' || ch === '\x7d';   // \x7b \x7d = braces
      let inStr = false, esc = false;
      for (let i = 0; i < t.length; i++) {
        const ch = t[i];
        if (inStr) {
          if (esc) esc = false; else if (ch === '\\') esc = true; else if (ch === '"') inStr = false;
          continue;
        }
        if (ch === '"') { inStr = true; continue; }
        if (ch === 'N' && t.startsWith('NaN', i) && bound(t[i - 1]) && bound(t[i + 3])) return true;
        if (ch === 'I' && t.startsWith('Infinity', i) && (bound(t[i - 1]) || t[i - 1] === '-') && bound(t[i + 8])) return true;
      }
      return false;
    })(text);
    const err = new Error(nonFinite
      ? 'The server\'s reply contains a non-finite number (NaN or Infinity), usually an uncertainty that could not be computed because these data do not determine the model. The fit is treated as failed.'
      : 'The server\'s reply could not be read. The fit is treated as failed.');
    err.serverError = true;
    err.unreadableReply = true;
    throw err;
  }
}

// ── Long fits via start-then-poll (unit 2, 2026-09-27) ──────────────────────
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-chr2j6Je' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ORFsGWEd' (errno=Operation not permitted)
docs/superpowers/plans/2026-09-27-long-fits-start-poll.md:167: new blank line at EOF.
fitting.py:2115: new blank line at EOF.
124:it: `tests/js/lineshape_roundtrip.test.js` builds the request with the
129:shape by shape); section (D) of `tests/js/lineshape_parity.test.js` sweeps
173:anchor (answer: a scale-free F test), then two tolerances on that F test
187:When two places read the same input — the page and the server, a preview
191:a free η to the server (A03); the ROI, the preview background and the fitted
221:for scripts, tests and the Python twins. Plan:
277:were actually being fit against, due to a pre-existing preview/backend
420:engine: lmfit divides by max(1, nfree) and the F tests clamp dof to 1, so such
443:(in review each such no-op edit moved an area fraction by 15–45 pp
452:makes (observed through Levenberg-Marquardt) are pinned by tests; numpy does not promise the same `default_rng` stream across
476:(`tests/test_fit_reproducibility.py` docstring). Do not patch scipy
488:second thing (a reviewer tried a deterministic perturbation base: identical
521:the largest move named, amber > 0.5 eV, red > 1 eV) with Preview (the
522:history-preview overlay, on a copy) and "Use this solution": explicit, one
540:the comparison no longer applies, nothing can be previewed or applied, an
541:open alternative preview is dropped (`_dropStaleAltPreview`), and
674:not detected (a refit without the component is the test; step (c) does it
743:| `tougaard` | Single-pass universal cross-section K(T) = B·T/(C+T²)², B = 2866 eV², C = 1643 eV² (Tougaard, *Surf. Interface Anal.* **1988**, 11, 453; kernel max at √(C/3) ≈ 23.4 eV). Order-robust (either BE direction); amplitude anchored to the data at the high-BE edge. JS twin `tougaardBackground` must stay in numerical agreement (pinned by `tests/js/tougaard_twin.test.js`). |
791:`tests/js/fixtures/autofit_anchor.json`. SCOPE: it answers "do the data
833:  the un-committed target file, not a test); the round-6 reproduction (two symmetric GL
959:tests/test_la_continuous_m.py   # LA(α,β,m) continuity across integer-m kernel widths
960:tests/test_la_short_input.py    # LA edge cases on very-short input arrays
961:tests/test_mixed_ds_lacx_e2e.py # End-to-end: a fit with both DS+G and CasaXPS LA peaks
964:Run via `pytest tests/`.
970:Typical regions for hand-testing:
  1224	    @_require_json
  1225	    def fit_start():
  1226	        body = request.get_json(silent=True)
  1227	        if not isinstance(body, dict):
  1228	            return _err("request body must be a JSON object")
  1229	        fit_args, error = _prepare_fit_request(app, body)
  1230	        if error is not None:
  1231	            return error
  1232	        upload_folder = app.config["UPLOAD_FOLDER"]
  1233	        job_id = str(uuid.uuid4())
  1234	        _sweep_expired_jobs(upload_folder)
  1235	        _sweep_fit_job_markers(upload_folder)
  1236	        _fit_job_start(job_id, upload_folder, fit_args,
  1237	                       lambda args, cancel: _run_fit_outcome(app, args, cancel=cancel))
  1238	        return jsonify({"job_id": job_id}), 202
  1239	
  1240	    @app.get("/api/fit/progress/<job_id>")
  1241	    def fit_progress(job_id):
  1242	        try:
  1243	            uuid.UUID(job_id)
  1244	        except ValueError:
  1245	            return _err("Invalid job_id format (expected UUID)", 400)
  1246	        data = _fit_job_read(job_id, app.config["UPLOAD_FOLDER"])
  1247	        if data is None:

codex
The overlap probe confirmed two jobs kept polling through completion with no cancellation. Cancellation also exposes a separate bug: Levenberg–Marquardt raised `AttributeError`, and Nelder–Mead and differential evolution raised `RuntimeError`, instead of `FitCancelled`. Those solvers stopped promptly, but abandoned jobs would be recorded as fitting errors. A direct Levenberg–Marquardt sync-versus-hook comparison was byte-identical.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import ast, pathlib, threading, time, types
tree=ast.parse(pathlib.Path(\"app.py\").read_text())
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==\"_fit_job_start\")
records={}
class Marker:
 def touch(self): pass
 def exists(self): return False
 def stat(self): return types.SimpleNamespace(st_mtime=time.time())
 def unlink(self,**kw): pass
ns=dict(threading=threading,time=time,FIT_JOB_HEARTBEAT_SEC=2,FIT_JOB_ABANDON_SEC=180,
 _fit_job_marker=lambda *a:Marker(),_fit_job_write=lambda j,u,d:records.update({j:dict(d)}))
exec(compile(ast.Module(body=[node],type_ignores=[]),\"<actual _fit_job_start>\",\"exec\"),ns)
gate=threading.Event()
def run(args,cancel):
 gate.wait(5)
 return 200,{\"success\":True}
for i in range(24):ns[\"_fit_job_start\"](f\"probe-{i:03}\",\"unused\",{},run)
threads=[t for t in threading.enumerate() if t.name.startswith((\"fit-probe\",\"fit-hb-probe\"))]
print(\"24 starts accepted; active fit/heartbeat threads:\",len(threads))
gate.set()
for t in threads:t.join(2)
tree=ast.parse(pathlib.Path(\"scripts/public_fit_poll_check.py\").read_text())
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==\"run\")
import json,uuid
polls=0
def req(url,*a,**kw):
 global polls
 if url.endswith(\"/upload\"): return 200,b'\\''{\"session_id\":\"S\"}'\\'',.01
 if url.endswith(\"/start\"): return 202,b'\\''{\"job_id\":\"J\"}'\\'',.01
 polls+=1
 if polls>5:raise RuntimeError(\"probe stopped an unbounded stale-heartbeat loop\")
 return 200,b'\\''{\"status\":\"running\",\"heartbeat_age_sec\":3600}'\\'',.01
ns=dict(uuid=uuid,json=json,time=types.SimpleNamespace(time=time.time,sleep=lambda _:None),_req=req,MAX_REQUEST_S=10)
exec(compile(ast.Module(body=[node],type_ignores=[]),\"<actual acceptance run>\",\"exec\"),ns)
try:ns[\"run\"](\"dummy\",dict(id=\"T\",be=[1],inten=[1],background=dict(method=\"shirley\",start_idx=0,end_idx=1,endpoint_avg=1),specs=[]))
except RuntimeError as e:print(str(e),\"polls:\",polls)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
24 starts accepted; active fit/heartbeat threads: 48
probe stopped an unbounded stale-heartbeat loop polls: 6

codex
1. **MAJOR — Re-running does not supersede the previous job.** [templates/index.html:8175](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8175)  
   Start a long fit, then press Ctrl/Cmd+F: the keyboard handler bypasses the disabled button. Both jobs retain the same owner and model key, so neither cancels. The older fit can finish first, apply its result, and cause the newer request to be discarded as “model edited.” An extracted-helper probe confirmed two completed jobs and zero cancel calls. Add per-owner operation identity and cancel the superseded job.

2. **MAJOR — Fit execution has no concurrency limit.** [app.py:672](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:672)  
   Every accepted start immediately creates two threads and retains its fit inputs. Four synchronous gunicorn workers no longer bound concurrent fits. Repeated shortcuts or concurrent clients can accumulate CPU-heavy jobs; continued polling prevents abandonment cancellation. A probe of the actual function admitted 24 jobs and created 48 threads without backpressure. Bound admission/execution while keeping progress requests responsive.

3. **MINOR — Cancellation exceptions bypass `FitCancelled`.** [fitting.py:2105](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/fitting.py:2105)  
   If `_run_fit_impl` raises, execution leaves after `finally`, skipping the cancellation check below it. Real cancellation probes produced `AttributeError` for Levenberg–Marquardt and `RuntimeError` for Nelder–Mead and differential evolution. Explicit cancel markers mask this in the job record, but automatic abandonment has no marker: those jobs become 500/422 fitting errors instead of `cancelled`. Translate exceptions when cancellation was observed before clearing the thread-local state.

4. **MINOR — Acceptance checker can poll a dead worker forever.** [scripts/public_fit_poll_check.py:59](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/scripts/public_fit_poll_check.py:59)  
   Restart the worker during the first target. Its record remains `running`, but the script ignores stale heartbeats and has no overall deadline. It never reaches the remaining targets or prints its verdict. A mocked stale-heartbeat response confirmed continued polling. Apply heartbeat detection and a bounded failure exit.

Validation: **83 focused JavaScript tests passed**; direct Levenberg–Marquardt sync/hook results were byte-identical. Filesystem-backed pytest and public timing acceptance were not rerun under the read-only constraint.

**VERDICT: NO-GO**
tokens used
85,022
1. **MAJOR — Re-running does not supersede the previous job.** [templates/index.html:8175](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8175)  
   Start a long fit, then press Ctrl/Cmd+F: the keyboard handler bypasses the disabled button. Both jobs retain the same owner and model key, so neither cancels. The older fit can finish first, apply its result, and cause the newer request to be discarded as “model edited.” An extracted-helper probe confirmed two completed jobs and zero cancel calls. Add per-owner operation identity and cancel the superseded job.

2. **MAJOR — Fit execution has no concurrency limit.** [app.py:672](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:672)  
   Every accepted start immediately creates two threads and retains its fit inputs. Four synchronous gunicorn workers no longer bound concurrent fits. Repeated shortcuts or concurrent clients can accumulate CPU-heavy jobs; continued polling prevents abandonment cancellation. A probe of the actual function admitted 24 jobs and created 48 threads without backpressure. Bound admission/execution while keeping progress requests responsive.

3. **MINOR — Cancellation exceptions bypass `FitCancelled`.** [fitting.py:2105](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/fitting.py:2105)  
   If `_run_fit_impl` raises, execution leaves after `finally`, skipping the cancellation check below it. Real cancellation probes produced `AttributeError` for Levenberg–Marquardt and `RuntimeError` for Nelder–Mead and differential evolution. Explicit cancel markers mask this in the job record, but automatic abandonment has no marker: those jobs become 500/422 fitting errors instead of `cancelled`. Translate exceptions when cancellation was observed before clearing the thread-local state.

4. **MINOR — Acceptance checker can poll a dead worker forever.** [scripts/public_fit_poll_check.py:59](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/scripts/public_fit_poll_check.py:59)  
   Restart the worker during the first target. Its record remains `running`, but the script ignores stale heartbeats and has no overall deadline. It never reaches the remaining targets or prints its verdict. A mocked stale-heartbeat response confirmed continued polling. Apply heartbeat detection and a bounded failure exit.

Validation: **83 focused JavaScript tests passed**; direct Levenberg–Marquardt sync/hook results were byte-identical. Filesystem-backed pytest and public timing acceptance were not rerun under the read-only constraint.

**VERDICT: NO-GO**

exec
/bin/zsh -lc 'git diff --stat fix-acceptance-holes..HEAD; git log -6 --oneline; git diff fix-acceptance-holes..HEAD -- server.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 5ms:
exec
/bin/zsh -lc 'git diff fix-acceptance-holes..HEAD -- app.py fitting.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-q0AgFw0v' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-DAqxITkr' (errno=Operation not permitted)
diff --git a/app.py b/app.py
index f689d5a..2dd37a5 100644
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
@@ -443,6 +550,172 @@ def _sweep_expired_jobs(upload_folder: str) -> None:
             pass
 
 
+# ── Fit jobs (unit 2, 2026-09-27) ────────────────────────────────────────────
+# Records are the Find Peaks job files (<job>.job.json, the same TTL sweep);
+# two small markers beside each: <job>.cancel (written by /api/fit/cancel,
+# any worker) and <job>.polled (touched by every poll). The fit thread's
+# cancel condition: the cancel marker exists, OR no poll for
+# FIT_JOB_ABANDON_SEC (a closed tab, a sleeping laptop; 180 s, above the ~1 min timer throttling browsers apply to hidden tabs).
+FIT_JOB_ABANDON_SEC = 180   # > Chrome's 1-minute timer throttling in a hidden tab: a student who switches browser tabs keeps the fit
+FIT_JOB_HEARTBEAT_SEC = 2.0
+# Concurrency (unit 2, Codex round 1). Before start-then-poll, gunicorn's four
+# SYNC workers bounded concurrent fits at four; a fit thread per start would
+# not. Each worker process runs at most FIT_JOB_MAX_RUNNING fits at once (the
+# rest wait "queued", heartbeating, cancellable) and admits at most
+# FIT_JOB_MAX_ADMITTED running + queued jobs; beyond that /api/fit/start
+# answers 503 "busy" immediately. With production's 4 workers: at most 4
+# concurrent fits, as before.
+FIT_JOB_MAX_RUNNING = 1
+FIT_JOB_MAX_ADMITTED = 6
+_FIT_JOB_RUN_SLOTS = threading.BoundedSemaphore(FIT_JOB_MAX_RUNNING)
+_FIT_JOB_ADMITTED = [0]
+_FIT_JOB_ADMIT_LOCK = threading.Lock()
+
+
+def _fit_job_admit() -> bool:
+    with _FIT_JOB_ADMIT_LOCK:
+        if _FIT_JOB_ADMITTED[0] >= FIT_JOB_MAX_ADMITTED:
+            return False
+        _FIT_JOB_ADMITTED[0] += 1
+        return True
+
+
+def _fit_job_release() -> None:
+    with _FIT_JOB_ADMIT_LOCK:
+        _FIT_JOB_ADMITTED[0] = max(0, _FIT_JOB_ADMITTED[0] - 1)
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
+    rec = {"status": "queued", "elapsed_sec": 0.0, "heartbeat": started}
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
+                if rec["status"] not in ("running", "queued"):
+                    return
+                rec["heartbeat"] = time.time()
+                rec["elapsed_sec"] = round(time.time() - started, 1)
+                _fit_job_write(job_id, upload_folder, rec)
+
+    def worker() -> None:
+        try:
+            # queued until a run slot is free; a job cancelled or abandoned
+            # while queued never runs
+            got = False
+            while not got:
+                if cancelled():
+                    status, body = None, None
+                    break
+                got = _FIT_JOB_RUN_SLOTS.acquire(timeout=0.5)
+            if got:
+                try:
+                    with lock:
+                        rec["status"] = "running"
+                        rec["heartbeat"] = time.time()
+                        _fit_job_write(job_id, upload_folder, rec)   # visible at once, not at the next heartbeat
+                    status, body = run(fit_args, cancelled)
+                finally:
+                    _FIT_JOB_RUN_SLOTS.release()
+        except Exception as exc:                       # the record must always leave "running"
+            logging.getLogger(__name__).exception("fit job %s crashed", job_id)
+            status, body = 500, {"error": "Internal fitting error — see server log."}
+        finally:
+            _fit_job_release()
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
@@ -779,94 +1052,13 @@ def _register_routes(app: Flask) -> None:
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
@@ -1060,6 +1252,60 @@ def _register_routes(app: Flask) -> None:
                     "message": "starting analysis…"}
         return jsonify(data)
 
+    # ── Long fits via start-then-poll (unit 2, 2026-09-27) ───────────────────
+    # The public URL ends a proxied request at ~100 s (Cloudflare 524; 88 s
+    # passed, 125 s failed); basinhopping on the large C 1s models takes 3–4
+    # minutes. The fit runs in a background thread on Find Peaks' job
+    # infrastructure (an atomic JSON record under the upload folder, readable
+    # by whichever gunicorn worker serves a poll); every HTTP request is short.
+    # The record: {status: queued|running|done|error|cancelled, elapsed_sec,
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
+        if not _fit_job_admit():
+            return _err("The server is busy with other fits. Try again in a moment.", 503)
+        job_id = str(uuid.uuid4())
+        try:
+            _sweep_expired_jobs(upload_folder)
+            _sweep_fit_job_markers(upload_folder)
+            _fit_job_start(job_id, upload_folder, fit_args,
+                           lambda args, cancel: _run_fit_outcome(app, args, cancel=cancel))
+        except Exception:
+            _fit_job_release()          # the job never started: its admission is returned
+            raise
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
index 63785a8..6b8f511 100644
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
@@ -2048,3 +2089,35 @@ def compute_background_only(
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
+    except Exception as exc:
+        # An aborted minimisation can surface as the solver's own error (an
+        # AttributeError from Levenberg-Marquardt, a RuntimeError from
+        # Nelder-Mead or DE): once cancellation was observed it is a
+        # cancellation, never a failed fit (unit 2, Codex round 1).
+        if getattr(_CANCEL, "hit", False):
+            raise FitCancelled("the fit was cancelled") from exc
+        raise
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
/bin/zsh -lc "cat tests/js/fit_start_poll.test.js tests/test_fit_start_poll.py; rg --files -g 'AGENTS.md' -g 'package.json'; cat docs/superpowers/plans/2026-09-27-long-fits-start-poll.md" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
// Unit 2 (2026-09-27): Run Fit and Auto-Fit start the fit and poll for it
// (_serverFitJob). Pinned: the result is the /api/fit body; a bad request's
// message and status are the synchronous route's; ownership (a switched tab,
// an edited model) cancels the server's job and discards; transport keeps its
// meaning (a START that cannot reach the server may fall back to the local
// engine; one lost poll does not; five in a row do); a lost heartbeat, a
// cancelled or errored record are failed fits; F2's NaN rule applies to the
// final record; the 2-minute Auto-Fit abort cancels the job.
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
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
const constLine = n => { const l = lines.find(x => x.startsWith('const ' + n)); assert.ok(l, n); return l; };

// fetch scripted by URL; every call recorded
function server(script) {
  const calls = [];
  const fetch = async (url, init) => {
    calls.push({ url, method: (init && init.method) || 'GET' });
    const h = script(url, init, calls);
    if (h instanceof Error) throw h;
    return h;
  };
  return { fetch, calls };
}
const ok = (obj, status = 200) => ({ ok: true, status, text: async () => (typeof obj === 'string' ? obj : JSON.stringify(obj)) });
const bad = (status, obj) => ({ ok: false, status, json: async () => { if (obj === undefined) throw new SyntaxError('x'); return obj; } });

function make(fetch) {
  const src = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
    'const _runningFitJobs = new Set(); const _fitJobByOwner = new WeakMap();',
    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
  return new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob, _runningFitJobs };')(
    fetch, f => f(), class extends Error { constructor(m, n) { super(m); this.name = n; } });
}
const START = '/api/fit/start';
const isProgress = u => u.startsWith('/api/fit/progress/');
const isCancel = u => u.startsWith('/api/fit/cancel/');

test('start -> running polls -> done: the result is the /api/fit body; no job is left registered', async () => {
  let n = 0;
  const s = server(u => u === START ? ok({ job_id: 'J' }, 202)
    : isProgress(u) ? (++n < 3 ? ok({ status: 'running', heartbeat_age_sec: 0.4 }) : ok({ status: 'done', result: { success: true, x: 1 } }))
    : ok({}));
  const { _serverFitJob, _runningFitJobs } = make(s.fetch);
  assert.deepStrictEqual(await _serverFitJob({ a: 1 }, {}), { success: true, x: 1 });
  assert.strictEqual(s.calls.filter(c => isProgress(c.url)).length, 3);
  assert.strictEqual(_runningFitJobs.size, 0);
  assert.ok(!s.calls.some(c => isCancel(c.url)), 'a finished job is not cancelled');
});

test('a bad request: the synchronous route\'s message and status, immediately; no poll', async () => {
  const s = server(u => u === START ? bad(400, { error: 'n_perturb must be between 0 and 10' }) : assert.fail(u));
  const { _serverFitJob } = make(s.fetch);
  await assert.rejects(_serverFitJob({}, {}), e => e.serverError && e.httpStatus === 400 && /n_perturb must be between/.test(e.message));
});

test('a START that cannot reach the server is a transport failure (the caller may fall back to the local engine)', async () => {
  const s = server(u => new TypeError('Failed to fetch'));
  const { _serverFitJob } = make(s.fetch);
  await assert.rejects(_serverFitJob({}, {}), e => e.transportFailure === true && !e.serverError);
});

test('an error record is a failed fit with the synchronous message and status', async () => {
  const s = server(u => u === START ? ok({ job_id: 'J' }, 202)
    : ok({ status: 'error', http_status: 400, error: 'The model is not determined by these data: 8 free parameters for 6 data points' }));
  const { _serverFitJob } = make(s.fetch);
  await assert.rejects(_serverFitJob({}, {}), e => e.serverError && e.httpStatus === 400 && /not determined by these data/.test(e.message));
});

test('a done record carrying NaN is F2\'s failed fit (unreadable reply), not a transport failure', async () => {
  const s = server(u => u === START ? ok({ job_id: 'J' }, 202)
    : isProgress(u) ? ok('{"status": "done", "result": {"success": true, "s": NaN}}') : ok({}));
  const { _serverFitJob } = make(s.fetch);
  await assert.rejects(_serverFitJob({}, {}), e => e.unreadableReply === true && e.serverError && !e.transportFailure && /non-finite/.test(e.message));
});

test('one lost poll is retried; five in a row are a transport failure and cancel the job', async () => {
  let n = 0;
  const flaky = server(u => u === START ? ok({ job_id: 'J' }, 202)
    : isProgress(u) ? (++n <= 4 ? new TypeError('network') : ok({ status: 'done', result: { success: true } })) : ok({}));
  assert.deepStrictEqual(await make(flaky.fetch)._serverFitJob({}, {}), { success: true });
  const dead = server(u => u === START ? ok({ job_id: 'J' }, 202) : isProgress(u) ? new TypeError('network') : ok({}));
  await assert.rejects(make(dead.fetch)._serverFitJob({}, {}), e => e.transportFailure === true && /Lost contact/.test(e.message));
  assert.ok(dead.calls.some(c => isCancel(c.url) && c.method === 'POST'), 'the server is told to stop');
});

test('a stopped heartbeat (restarted worker) is a failed fit, never an endless spinner', async () => {
  const s = server(u => u === START ? ok({ job_id: 'J' }, 202) : isProgress(u) ? ok({ status: 'running', heartbeat_age_sec: 45 }) : ok({}));
  await assert.rejects(make(s.fetch)._serverFitJob({}, {}), e => e.serverError && /stopped working on the fit/.test(e.message));
});

test('a job cancelled on the server (abandoned) is reported, not waited for', async () => {
  const s = server(u => u === START ? ok({ job_id: 'J' }, 202) : ok({ status: 'cancelled' }));
  await assert.rejects(make(s.fetch)._serverFitJob({}, {}), e => e.serverError && /stopped on the server/.test(e.message));
});

test('ownership inside the loop: a switched tab or an edited model cancels the job and returns the reason', async () => {
  for (const reason of ['tab', 'model']) {
    let polls = 0;
    const s = server(u => u === START ? ok({ job_id: 'J' }, 202) : isProgress(u) ? (polls++, ok({ status: 'running', heartbeat_age_sec: 0 })) : ok({}));
    let t = 0;
    const out = await make(s.fetch)._serverFitJob({}, { abandoned: () => (++t > 2 ? reason : null) });
    assert.deepStrictEqual(out, { _abandoned: reason });
    assert.ok(s.calls.some(c => isCancel(c.url) && c.method === 'POST'), reason + ': the server is told to stop');
    assert.strictEqual(polls, 2, 'no poll after the model or tab changed');
  }
});

test('the Auto-Fit abort (2 minutes) cancels the job and surfaces as an AbortError', async () => {
  const ctrl = { aborted: false, reason: null };
  let polls = 0;
  const s = server(u => u === START ? ok({ job_id: 'J' }, 202) : isProgress(u) ? (++polls === 2 && (ctrl.aborted = true, ctrl.reason = Object.assign(new Error('timeout'), { name: 'AbortError' })), ok({ status: 'running', heartbeat_age_sec: 0 })) : ok({}));
  await assert.rejects(make(s.fetch)._serverFitJob({}, { signal: ctrl }), e => e.name === 'AbortError');
  assert.ok(s.calls.some(c => isCancel(c.url)));
});

test('Run Fit and Auto-Fit both go through _serverFitJob; nothing on the page posts to the synchronous /api/fit any more', () => {
  assert.match(extractFn('runFit'), /await _serverFitJob\(fitReq, \{/);
  assert.match(extractFn('runAutoFitC1sGraphite'), /await _serverFitJob\(\{/);
  assert.ok(!/fetch\('\/api\/fit'/.test(html), 'no synchronous /api/fit fetch left');
  // the ownership reasons are the ones the discard messages handle
  for (const fn of ['runFit', 'runAutoFitC1sGraphite']) {
    const src = extractFn(fn);
    assert.match(src, /_abandoned === 'tab'/, fn);
    assert.match(src, /_abandoned === 'model'/, fn);
  }
  assert.match(html, /addEventListener\('pagehide'/, 'a closed page cancels its running fits');
});

test('a new start for the same tab SUPERSEDES the previous job: cancelled on the server, its loop returns quietly (Codex round 1)', async () => {
  let n = 0;
  let releaseFirst;
  const gate = new Promise(r => { releaseFirst = r; });
  const s = server(u => u === START ? ok({ job_id: 'J' + (++n) }, 202)
    : isProgress(u) ? ok({ status: 'running', heartbeat_age_sec: 0 }) : ok({}));
  // a poll loop that yields between polls, so two jobs can interleave
  const src = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
    'const _runningFitJobs = new Set(); const _fitJobByOwner = new WeakMap();',
    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
  const { _serverFitJob } = new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob };')(
    s.fetch, f => { setImmediate(f); return 0; }, class extends Error {});   // yield to the event loop between polls
  const owner = { id: 'tab-1' };
  let polls2 = 0;
  const first = _serverFitJob({}, { owner });
  await new Promise(r => setImmediate(r)); await new Promise(r => setImmediate(r));
  const second = _serverFitJob({}, { owner, abandoned: () => (++polls2 > 3 ? 'tab' : null) });
  assert.deepStrictEqual(await first, { _abandoned: 'superseded' });
  assert.ok(s.calls.some(c => c.url === '/api/fit/cancel/J1' && c.method === 'POST'), 'the first job is cancelled on the server');
  assert.deepStrictEqual(await second, { _abandoned: 'tab' }, 'the second runs on, owning the tab');
  // another tab's job is not touched
  const other = _serverFitJob({}, { owner: { id: 'tab-2' }, abandoned: () => 'model' });
  assert.deepStrictEqual(await other, { _abandoned: 'model' });
});

test('both callers pass their tab as the owner and do nothing at all when superseded', () => {
  for (const fn of ['runFit', 'runAutoFitC1sGraphite']) {
    const src = extractFn(fn);
    assert.match(src, /owner: fittingTab,/, fn);
    assert.match(src, /if \(json && json\._abandoned === 'superseded'\) return;/, fn);
  }
});
"""Unit 2 (2026-09-27): long fits via start-then-poll.

/api/fit/start validates exactly as /api/fit, runs the SAME run_fit in a
background thread on Find Peaks' job records, and the page polls
/api/fit/progress. Pinned here: a polled fit is the synchronous fit (same
body; byte-identical for Levenberg-Marquardt); every validation error is
immediate and word-for-word the same; a run_fit error becomes the same
message and status in the record; cancel (explicit, or no poll for
FIT_JOB_ABANDON_SEC) stops the fit within seconds; the heartbeat; every poll
is a short request.
"""

import io
import json
import time

import numpy as np
import pytest

import app as app_module
from app import create_app


def _gl(x, c, a, w):
    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)


@pytest.fixture()
def client(tmp_path):
    a = create_app(upload_folder=str(tmp_path))
    a.config["TESTING"] = True
    with a.test_client() as c:
        yield c


def _upload(client, n=200, comps=((284.5, 5000, 0.9), (286.2, 1500, 1.1)), seed=3):
    rng = np.random.default_rng(seed)
    x = np.linspace(281.0, 292.0, n)
    y = rng.poisson(300 + sum(_gl(x, c, a, w) for c, a, w in comps)).astype(float)
    csv = "\n".join(f"{a:.4f},{b:.1f}" for a, b in zip(x, y))
    r = client.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "s.csv")})
    assert r.status_code == 200, r.get_json()
    return r.get_json()["session_id"]


def _specs(comps):
    return [{"id": str(i + 1), "shape": "pseudo_voigt_gl", "center": c + 0.1, "fwhm": w * 1.1, "amplitude": a * 0.8,
             "gl_ratio": 0.3, "amplitude_min": 0} for i, (c, a, w) in enumerate(comps)]


def _body(sid, comps, method="leastsq", **extra):
    return {"session_id": sid, "background": {"method": "shirley"}, "peaks": _specs(comps),
            "fit_method": method, "n_perturb": 1, "n_starts": 0, **extra}


def _poll(client, job_id, limit=300.0):
    t0, longest = time.time(), 0.0
    while True:
        q0 = time.time()
        r = client.get(f"/api/fit/progress/{job_id}")
        longest = max(longest, time.time() - q0)
        assert r.status_code == 200
        rec = json.loads(r.get_data(as_text=True))
        if rec["status"] not in ("queued", "running"):
            return rec, longest
        assert time.time() - t0 < limit, "job did not finish"
        time.sleep(0.2)


COMPS = ((284.5, 5000, 0.9), (286.2, 1500, 1.1))


def test_a_polled_fit_is_the_synchronous_fit_byte_for_byte(client):
    sid = _upload(client)
    sync = client.post("/api/fit", json=_body(sid, COMPS))
    assert sync.status_code == 200
    start = client.post("/api/fit/start", json=_body(sid, COMPS))
    assert start.status_code == 202
    rec, longest = _poll(client, start.get_json()["job_id"])
    assert rec["status"] == "done"
    # Levenberg-Marquardt is byte-identical request to request (CLAUDE.md): same seed, same body
    assert json.dumps(rec["result"], sort_keys=True) == json.dumps(sync.get_json(), sort_keys=True)
    assert longest < 2.0, f"a poll took {longest:.2f} s"


@pytest.mark.parametrize("method", ["differential_evolution", "basinhopping", "least_squares"])
def test_the_stochastic_and_default_methods_give_the_synchronous_answer(client, method):
    sid = _upload(client)
    body = _body(sid, COMPS, method=method, n_perturb=0)
    sync = client.post("/api/fit", json=body).get_json()
    rec, _ = _poll(client, client.post("/api/fit/start", json=body).get_json()["job_id"])
    res = rec["result"]
    assert res["random_seed"] == sync["random_seed"]
    assert res["success"] == sync["success"] is True
    # Trust-Region (also DE's and basinhopping's refinement) is not bit-reproducible
    # across calls (BLAS alignment, CLAUDE.md); the answer is the same fit
    assert res["statistics"]["reduced_chi_square"] == pytest.approx(sync["statistics"]["reduced_chi_square"], rel=1e-6)


@pytest.mark.parametrize("patch,status,fragment", [
    ({"n_perturb": 101}, 400, "n_perturb must be between"),
    ({"fit_method": "ampgo"}, 400, "Unknown fit_method"),
    ({"peaks": []}, 400, "'peaks' list is empty"),
    ({"session_id": "0" * 32}, 404, "not found"),
])
def test_a_bad_request_is_refused_immediately_and_identically(client, patch, status, fragment):
    sid = _upload(client)
    body = {**_body(sid, COMPS), **patch}
    a = client.post("/api/fit", json=body)
    b = client.post("/api/fit/start", json=body)
    assert a.status_code == b.status_code == status
    assert a.get_json() == b.get_json()
    assert fragment in b.get_json()["error"]


def test_a_run_fit_refusal_reaches_the_record_with_the_synchronous_message_and_status(client):
    sid = _upload(client, n=6)                                    # 8 free parameters, 6 points (unit F2)
    body = {**_body(sid, COMPS), "n_perturb": 0}
    sync = client.post("/api/fit", json=body)
    rec, _ = _poll(client, client.post("/api/fit/start", json=body).get_json()["job_id"])
    assert rec["status"] == "error"
    assert rec["http_status"] == sync.status_code == 400
    assert rec["error"] == sync.get_json()["error"]


SLOW = ((283.2, 2000, 0.8), (284.5, 5000, 0.9), (285.4, 1800, 1.0), (286.6, 1500, 1.1), (288.4, 900, 1.4))


def test_cancel_stops_a_running_fit_within_seconds(client):
    sid = _upload(client, n=300, comps=SLOW)
    job = client.post("/api/fit/start", json=_body(sid, SLOW, method="basinhopping", n_perturb=0)).get_json()["job_id"]
    time.sleep(1.0)
    rec = json.loads(client.get(f"/api/fit/progress/{job}").get_data(as_text=True))
    assert rec["status"] in ("queued", "running"), "the fixture must still be running when cancelled"
    t0 = time.time()
    assert client.post(f"/api/fit/cancel/{job}").status_code == 200
    rec, _ = _poll(client, job, limit=30)
    assert rec["status"] == "cancelled"
    assert time.time() - t0 < 10, f"cancel took {time.time() - t0:.1f} s"


def test_an_abandoned_job_stops_itself_when_polls_stop(client, monkeypatch):
    monkeypatch.setattr(app_module, "FIT_JOB_ABANDON_SEC", 1.5)
    sid = _upload(client, n=300, comps=SLOW)
    job = client.post("/api/fit/start", json=_body(sid, SLOW, method="basinhopping", n_perturb=0)).get_json()["job_id"]
    time.sleep(6.0)                                               # nobody polls
    rec = json.loads(client.get(f"/api/fit/progress/{job}").get_data(as_text=True))
    assert rec["status"] == "cancelled", rec["status"]


def test_the_heartbeat_moves_while_the_fit_runs(client):
    sid = _upload(client, n=300, comps=SLOW)
    job = client.post("/api/fit/start", json=_body(sid, SLOW, method="basinhopping", n_perturb=0)).get_json()["job_id"]
    time.sleep(4.5)
    rec = json.loads(client.get(f"/api/fit/progress/{job}").get_data(as_text=True))
    assert rec["status"] in ("queued", "running")
    assert rec["heartbeat_age_sec"] is not None and rec["heartbeat_age_sec"] < 3.0
    assert rec["elapsed_sec"] >= 2.0
    client.post(f"/api/fit/cancel/{job}")
    _poll(client, job, limit=30)


def test_unknown_and_malformed_job_ids(client):
    assert client.get("/api/fit/progress/not-a-uuid").status_code == 400
    assert client.get("/api/fit/progress/00000000-0000-0000-0000-000000000000").status_code == 404
    assert client.post("/api/fit/cancel/not-a-uuid").status_code == 400


def test_a_non_finite_result_reaches_the_page_unsanitised(tmp_path):
    # the page's _readFitReply refuses NaN as a failed fit (unit F2): the job
    # record must carry it exactly as /api/fit would, never as null
    app_module._fit_job_write("11111111-1111-1111-1111-111111111111", str(tmp_path),
                              {"status": "done", "result": {"x": float("nan")}})
    text = (tmp_path / "11111111-1111-1111-1111-111111111111.job.json").read_text()
    assert "NaN" in text


def test_concurrency_is_bounded_one_fit_runs_per_process_the_rest_queue_and_admission_is_capped(client, monkeypatch):
    """Codex round 1: four sync workers used to bound concurrent fits at four;
    a thread per start would not. One fit runs per worker process; the rest
    wait "queued" (heartbeating, cancellable); beyond FIT_JOB_MAX_ADMITTED the
    start is refused at once with 503."""
    sid = _upload(client, n=300, comps=SLOW)
    body = _body(sid, SLOW, method="basinhopping", n_perturb=0)
    jobs = [client.post("/api/fit/start", json=body).get_json()["job_id"] for _ in range(3)]
    time.sleep(1.5)
    states = [json.loads(client.get(f"/api/fit/progress/{j}").get_data(as_text=True))["status"] for j in jobs]
    assert states.count("running") == 1 and states.count("queued") == 2, states
    monkeypatch.setattr(app_module, "FIT_JOB_MAX_ADMITTED", 3)
    busy = client.post("/api/fit/start", json=body)
    assert busy.status_code == 503 and "busy" in busy.get_json()["error"]
    for j in jobs:
        client.post(f"/api/fit/cancel/{j}")
    for j in jobs:
        rec, _ = _poll(client, j, limit=60)
        assert rec["status"] == "cancelled"
    # the slots are returned: a new start is admitted again
    ok = client.post("/api/fit/start", json=body)
    assert ok.status_code == 202
    client.post(f"/api/fit/cancel/{ok.get_json()['job_id']}")
    _poll(client, ok.get_json()["job_id"], limit=60)


@pytest.mark.parametrize("method", ["leastsq", "nelder", "differential_evolution"])
def test_a_cancel_observed_mid_fit_is_a_cancellation_never_a_solver_error(method):
    """Codex round 1: an aborted minimisation can surface as the solver's own
    error (AttributeError from Levenberg-Marquardt, RuntimeError from
    Nelder-Mead / DE); once cancellation was observed run_fit raises
    FitCancelled."""
    import fitting
    x = np.linspace(281.0, 292.0, 300)
    y = 300 + sum(_gl(x, c, a, w) for c, a, w in SLOW)
    cancel = lambda: True               # observed at the first check: the minimisation is aborted mid-fit
    with pytest.raises(fitting.FitCancelled):
        fitting.run_fit(x, y, _specs(SLOW), background_method="linear", n_perturb=0,
                        fit_kws={"method": method}, cancel=cancel)
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



exec
/bin/zsh -lc 'git diff fix-acceptance-holes..HEAD -- templates/index.html scripts/public_fit_poll_check.py; tail -65 docs/autofit/codex/fit_start_poll_verdict_runA.md; tail -55 docs/autofit/codex/fit_start_poll_verdict_runB.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-HUz325e0' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-NpQzPf4N' (errno=Operation not permitted)
diff --git a/scripts/public_fit_poll_check.py b/scripts/public_fit_poll_check.py
new file mode 100644
index 0000000..49205c6
--- /dev/null
+++ b/scripts/public_fit_poll_check.py
@@ -0,0 +1,97 @@
+#!/usr/bin/env python3
+"""Post-deploy check for unit 2 (long fits via start-then-poll), THROUGH THE
+PUBLIC URL — the path a student's browser takes, where Cloudflare ends a
+single request at ~100 s (HTTP 524).
+
+It does what the page does for Run Fit: upload, POST /api/fit/start, poll
+GET /api/fit/progress every 0.5 s until the job leaves "running"; it records
+the duration of EVERY request. PASS = the job finishes "done" with
+success true, and no request took longer than MAX_REQUEST_S.
+
+Usage:
+  python scripts/public_fit_poll_check.py targets.json [BASE_URL] [target_id ...]
+
+targets.json: the optimizer-disagreement target file (branch
+investigate-optimizer-disagreement, docs/findings/optimizer-disagreement/
+targets.json). Default targets: the five largest committed C 1s models,
+the ones that took 183-256 s even without restarts.
+"""
+import json
+import sys
+import time
+import urllib.error
+import urllib.request
+import uuid
+
+MAX_REQUEST_S = 10.0
+HEARTBEAT_LOST_S = 30.0      # as the page: a record whose heartbeat stopped is a lost fit
+DEADLINE_S = 20 * 60         # per target: never poll forever
+DEFAULT_TARGETS = ["edf39ecb66ce", "d2bd62d2f976", "496c4edd97af", "0a5f464daf3d", "8b4c2f656a80"]
+
+
+def _req(url, data=None, headers=None, method=None, timeout=60):
+    t0 = time.time()
+    req = urllib.request.Request(url, data=data, headers={"User-Agent": "xps-poll-check", **(headers or {})}, method=method)
+    try:
+        with urllib.request.urlopen(req, timeout=timeout) as r:
+            body, status = r.read(), r.status
+    except urllib.error.HTTPError as e:
+        body, status = e.read(), e.code
+    return status, body, time.time() - t0
+
+
+def run(base, t):
+    durations = []
+    csv = "\n".join(f"{a:.4f},{b:.4f}" for a, b in zip(t["be"], t["inten"])).encode()
+    bnd = uuid.uuid4().hex
+    form = (f"--{bnd}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"t.csv\"\r\n"
+            f"Content-Type: text/csv\r\n\r\n").encode() + csv + f"\r\n--{bnd}--\r\n".encode()
+    st, body, d = _req(base + "/api/upload", form, {"Content-Type": f"multipart/form-data; boundary={bnd}"})
+    durations.append(("upload", st, d))
+    sid = json.loads(body)["session_id"]
+    bg = t["background"]
+    payload = {"session_id": sid, "background": {k: bg[k] for k in ("method", "start_idx", "end_idx", "endpoint_avg")},
+               "peaks": t["specs"], "fit_method": "basinhopping", "n_perturb": 3, "n_starts": 3}
+    st, body, d = _req(base + "/api/fit/start", json.dumps(payload).encode(), {"Content-Type": "application/json"})
+    durations.append(("start", st, d))
+    if st != 202:
+        return {"id": t["id"], "verdict": "FAIL", "why": f"start returned {st}: {body[:200]!r}", "durations": durations}
+    job = json.loads(body)["job_id"]
+    t0 = time.time()
+    while True:
+        time.sleep(0.5)
+        st, body, d = _req(base + f"/api/fit/progress/{job}")
+        durations.append(("poll", st, d))
+        rec = json.loads(body) if st == 200 else {"status": f"http {st}"}
+        if rec.get("status") not in ("running", "queued"):
+            break
+        hb = rec.get("heartbeat_age_sec")
+        if isinstance(hb, (int, float)) and hb > HEARTBEAT_LOST_S:
+            rec = {"status": "lost", "error": f"heartbeat stopped {hb:.0f} s ago (worker restarted?)"}
+            break
+        if time.time() - t0 > DEADLINE_S:
+            _req(base + f"/api/fit/cancel/{job}", b"", method="POST")
+            rec = {"status": "deadline", "error": f"no result after {DEADLINE_S} s"}
+            break
+    longest = max(x[2] for x in durations)
+    res = rec.get("result") or {}
+    ok = rec.get("status") == "done" and res.get("success") is True and longest <= MAX_REQUEST_S
+    return {"id": t["id"], "verdict": "PASS" if ok else "FAIL", "status": rec.get("status"),
+            "success": res.get("success"), "chi2r": (res.get("statistics") or {}).get("reduced_chi_square"),
+            "fit_wall_s": round(time.time() - t0, 1), "n_requests": len(durations),
+            "longest_request_s": round(longest, 2), "error": rec.get("error")}
+
+
+def main():
+    targets = json.load(open(sys.argv[1]))
+    base = sys.argv[2] if len(sys.argv) > 2 else "https://xps.fortierlab.org"
+    ids = sys.argv[3:] or DEFAULT_TARGETS
+    by_id = {t["id"]: t for t in targets}
+    results = [run(base, by_id[i]) for i in ids]
+    for r in results:
+        print(json.dumps(r))
+    print("OVERALL:", "PASS" if all(r["verdict"] == "PASS" for r in results) else "FAIL")
+
+
+if __name__ == "__main__":
+    main()
diff --git a/templates/index.html b/templates/index.html
index bb740ac..b81fa84 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -7445,6 +7445,130 @@ async function _readFitReply(resp) {
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
+// The current server fit of each tab record (unit 2, Codex round 1): a new
+// start for the same tab — Ctrl/Cmd+F bypasses the disabled button, and
+// Auto-Fit and Run Fit share a tab — SUPERSEDES the previous job: it is
+// cancelled on the server and its loop returns { _abandoned: 'superseded' },
+// on which the caller does nothing at all (the new fit owns the spinner and
+// the result).
+const _fitJobByOwner = new WeakMap();
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
+  if (guard.owner) {
+    const prev = _fitJobByOwner.get(guard.owner);
+    if (prev && prev !== jobId) _cancelFitJob(prev);
+    _fitJobByOwner.set(guard.owner, jobId);
+  }
+  let misses = 0;
+  try {
+    while (true) {
+      await new Promise(r => setTimeout(r, FIT_POLL_MS));
+      if (guard.signal && guard.signal.aborted) {
+        _cancelFitJob(jobId);
+        throw guard.signal.reason || new DOMException('aborted', 'AbortError');
+      }
+      if (guard.owner && _fitJobByOwner.get(guard.owner) !== jobId) return { _abandoned: 'superseded' };   // its successor cancelled it
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
+    if (guard.owner && _fitJobByOwner.get(guard.owner) === jobId) _fitJobByOwner.delete(guard.owner);
+  }
+}
+
 async function runAutoFitC1sGraphite() {
   // Pre-conditions
   if (!state.rawBE || !state.rawBE.length) { notify('Load a spectrum first.', 'amber'); return; }
@@ -7559,10 +7683,8 @@ async function runAutoFitC1sGraphite() {
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
@@ -7572,21 +7694,31 @@ async function runAutoFitC1sGraphite() {
         // the model without it; a redundant anchor must not set the energy
         // reference of a whole spectrum (see applyAutoFitResult).
         require_component: anchorId,
-      }),
+    }, {
+      owner: fittingTab,
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
+    // superseded by a newer fit on this tab (Run Fit pressed during Auto-Fit):
+    // that fit started from the model now on the tab and owns the result — no
+    // rollback here, which would overwrite it
+    if (json && json._abandoned === 'superseded') return;
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
@@ -8053,26 +8185,29 @@ async function runFit(opts = {}) {
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
+      owner: fittingTab,
+      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
+    });
+    if (json && json._abandoned === 'superseded') return;   // a newer fit on this tab owns the spinner and the result
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
gate.set()
for t in threads:t.join(2)
tree=ast.parse(pathlib.Path(\"scripts/public_fit_poll_check.py\").read_text())
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==\"run\")
import json,uuid
polls=0
def req(url,*a,**kw):
 global polls
 if url.endswith(\"/upload\"): return 200,b'\\''{\"session_id\":\"S\"}'\\'',.01
 if url.endswith(\"/start\"): return 202,b'\\''{\"job_id\":\"J\"}'\\'',.01
 polls+=1
 if polls>5:raise RuntimeError(\"probe stopped an unbounded stale-heartbeat loop\")
 return 200,b'\\''{\"status\":\"running\",\"heartbeat_age_sec\":3600}'\\'',.01
ns=dict(uuid=uuid,json=json,time=types.SimpleNamespace(time=time.time,sleep=lambda _:None),_req=req,MAX_REQUEST_S=10)
exec(compile(ast.Module(body=[node],type_ignores=[]),\"<actual acceptance run>\",\"exec\"),ns)
try:ns[\"run\"](\"dummy\",dict(id=\"T\",be=[1],inten=[1],background=dict(method=\"shirley\",start_idx=0,end_idx=1,endpoint_avg=1),specs=[]))
except RuntimeError as e:print(str(e),\"polls:\",polls)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
24 starts accepted; active fit/heartbeat threads: 48
probe stopped an unbounded stale-heartbeat loop polls: 6

codex
1. **MAJOR — Re-running does not supersede the previous job.** [templates/index.html:8175](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8175)  
   Start a long fit, then press Ctrl/Cmd+F: the keyboard handler bypasses the disabled button. Both jobs retain the same owner and model key, so neither cancels. The older fit can finish first, apply its result, and cause the newer request to be discarded as “model edited.” An extracted-helper probe confirmed two completed jobs and zero cancel calls. Add per-owner operation identity and cancel the superseded job.

2. **MAJOR — Fit execution has no concurrency limit.** [app.py:672](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:672)  
   Every accepted start immediately creates two threads and retains its fit inputs. Four synchronous gunicorn workers no longer bound concurrent fits. Repeated shortcuts or concurrent clients can accumulate CPU-heavy jobs; continued polling prevents abandonment cancellation. A probe of the actual function admitted 24 jobs and created 48 threads without backpressure. Bound admission/execution while keeping progress requests responsive.

3. **MINOR — Cancellation exceptions bypass `FitCancelled`.** [fitting.py:2105](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/fitting.py:2105)  
   If `_run_fit_impl` raises, execution leaves after `finally`, skipping the cancellation check below it. Real cancellation probes produced `AttributeError` for Levenberg–Marquardt and `RuntimeError` for Nelder–Mead and differential evolution. Explicit cancel markers mask this in the job record, but automatic abandonment has no marker: those jobs become 500/422 fitting errors instead of `cancelled`. Translate exceptions when cancellation was observed before clearing the thread-local state.

4. **MINOR — Acceptance checker can poll a dead worker forever.** [scripts/public_fit_poll_check.py:59](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/scripts/public_fit_poll_check.py:59)  
   Restart the worker during the first target. Its record remains `running`, but the script ignores stale heartbeats and has no overall deadline. It never reaches the remaining targets or prints its verdict. A mocked stale-heartbeat response confirmed continued polling. Apply heartbeat detection and a bounded failure exit.

Validation: **83 focused JavaScript tests passed**; direct Levenberg–Marquardt sync/hook results were byte-identical. Filesystem-backed pytest and public timing acceptance were not rerun under the read-only constraint.

**VERDICT: NO-GO**
tokens used
85,022
1. **MAJOR — Re-running does not supersede the previous job.** [templates/index.html:8175](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8175)  
   Start a long fit, then press Ctrl/Cmd+F: the keyboard handler bypasses the disabled button. Both jobs retain the same owner and model key, so neither cancels. The older fit can finish first, apply its result, and cause the newer request to be discarded as “model edited.” An extracted-helper probe confirmed two completed jobs and zero cancel calls. Add per-owner operation identity and cancel the superseded job.

2. **MAJOR — Fit execution has no concurrency limit.** [app.py:672](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:672)  
   Every accepted start immediately creates two threads and retains its fit inputs. Four synchronous gunicorn workers no longer bound concurrent fits. Repeated shortcuts or concurrent clients can accumulate CPU-heavy jobs; continued polling prevents abandonment cancellation. A probe of the actual function admitted 24 jobs and created 48 threads without backpressure. Bound admission/execution while keeping progress requests responsive.

3. **MINOR — Cancellation exceptions bypass `FitCancelled`.** [fitting.py:2105](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/fitting.py:2105)  
   If `_run_fit_impl` raises, execution leaves after `finally`, skipping the cancellation check below it. Real cancellation probes produced `AttributeError` for Levenberg–Marquardt and `RuntimeError` for Nelder–Mead and differential evolution. Explicit cancel markers mask this in the job record, but automatic abandonment has no marker: those jobs become 500/422 fitting errors instead of `cancelled`. Translate exceptions when cancellation was observed before clearing the thread-local state.

4. **MINOR — Acceptance checker can poll a dead worker forever.** [scripts/public_fit_poll_check.py:59](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/scripts/public_fit_poll_check.py:59)  
   Restart the worker during the first target. Its record remains `running`, but the script ignores stale heartbeats and has no overall deadline. It never reaches the remaining targets or prints its verdict. A mocked stale-heartbeat response confirmed continued polling. Apply heartbeat detection and a bounded failure exit.

Validation: **83 focused JavaScript tests passed**; direct Levenberg–Marquardt sync/hook results were byte-identical. Filesystem-backed pytest and public timing acceptance were not rerun under the read-only constraint.

**VERDICT: NO-GO**

exec
/bin/zsh -lc 'git diff fix-acceptance-holes..HEAD -- templates/index.html fitting.py scripts/public_fit_poll_check.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-UJHVhmH9' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Qox4FXqZ' (errno=Operation not permitted)
diff --git a/fitting.py b/fitting.py
index 63785a8..6b8f511 100644
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
@@ -2048,3 +2089,35 @@ def compute_background_only(
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
+    except Exception as exc:
+        # An aborted minimisation can surface as the solver's own error (an
+        # AttributeError from Levenberg-Marquardt, a RuntimeError from
+        # Nelder-Mead or DE): once cancellation was observed it is a
+        # cancellation, never a failed fit (unit 2, Codex round 1).
+        if getattr(_CANCEL, "hit", False):
+            raise FitCancelled("the fit was cancelled") from exc
+        raise
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
diff --git a/scripts/public_fit_poll_check.py b/scripts/public_fit_poll_check.py
new file mode 100644
index 0000000..49205c6
--- /dev/null
+++ b/scripts/public_fit_poll_check.py
@@ -0,0 +1,97 @@
+#!/usr/bin/env python3
+"""Post-deploy check for unit 2 (long fits via start-then-poll), THROUGH THE
+PUBLIC URL — the path a student's browser takes, where Cloudflare ends a
+single request at ~100 s (HTTP 524).
+
+It does what the page does for Run Fit: upload, POST /api/fit/start, poll
+GET /api/fit/progress every 0.5 s until the job leaves "running"; it records
+the duration of EVERY request. PASS = the job finishes "done" with
+success true, and no request took longer than MAX_REQUEST_S.
+
+Usage:
+  python scripts/public_fit_poll_check.py targets.json [BASE_URL] [target_id ...]
+
+targets.json: the optimizer-disagreement target file (branch
+investigate-optimizer-disagreement, docs/findings/optimizer-disagreement/
+targets.json). Default targets: the five largest committed C 1s models,
+the ones that took 183-256 s even without restarts.
+"""
+import json
+import sys
+import time
+import urllib.error
+import urllib.request
+import uuid
+
+MAX_REQUEST_S = 10.0
+HEARTBEAT_LOST_S = 30.0      # as the page: a record whose heartbeat stopped is a lost fit
+DEADLINE_S = 20 * 60         # per target: never poll forever
+DEFAULT_TARGETS = ["edf39ecb66ce", "d2bd62d2f976", "496c4edd97af", "0a5f464daf3d", "8b4c2f656a80"]
+
+
+def _req(url, data=None, headers=None, method=None, timeout=60):
+    t0 = time.time()
+    req = urllib.request.Request(url, data=data, headers={"User-Agent": "xps-poll-check", **(headers or {})}, method=method)
+    try:
+        with urllib.request.urlopen(req, timeout=timeout) as r:
+            body, status = r.read(), r.status
+    except urllib.error.HTTPError as e:
+        body, status = e.read(), e.code
+    return status, body, time.time() - t0
+
+
+def run(base, t):
+    durations = []
+    csv = "\n".join(f"{a:.4f},{b:.4f}" for a, b in zip(t["be"], t["inten"])).encode()
+    bnd = uuid.uuid4().hex
+    form = (f"--{bnd}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"t.csv\"\r\n"
+            f"Content-Type: text/csv\r\n\r\n").encode() + csv + f"\r\n--{bnd}--\r\n".encode()
+    st, body, d = _req(base + "/api/upload", form, {"Content-Type": f"multipart/form-data; boundary={bnd}"})
+    durations.append(("upload", st, d))
+    sid = json.loads(body)["session_id"]
+    bg = t["background"]
+    payload = {"session_id": sid, "background": {k: bg[k] for k in ("method", "start_idx", "end_idx", "endpoint_avg")},
+               "peaks": t["specs"], "fit_method": "basinhopping", "n_perturb": 3, "n_starts": 3}
+    st, body, d = _req(base + "/api/fit/start", json.dumps(payload).encode(), {"Content-Type": "application/json"})
+    durations.append(("start", st, d))
+    if st != 202:
+        return {"id": t["id"], "verdict": "FAIL", "why": f"start returned {st}: {body[:200]!r}", "durations": durations}
+    job = json.loads(body)["job_id"]
+    t0 = time.time()
+    while True:
+        time.sleep(0.5)
+        st, body, d = _req(base + f"/api/fit/progress/{job}")
+        durations.append(("poll", st, d))
+        rec = json.loads(body) if st == 200 else {"status": f"http {st}"}
+        if rec.get("status") not in ("running", "queued"):
+            break
+        hb = rec.get("heartbeat_age_sec")
+        if isinstance(hb, (int, float)) and hb > HEARTBEAT_LOST_S:
+            rec = {"status": "lost", "error": f"heartbeat stopped {hb:.0f} s ago (worker restarted?)"}
+            break
+        if time.time() - t0 > DEADLINE_S:
+            _req(base + f"/api/fit/cancel/{job}", b"", method="POST")
+            rec = {"status": "deadline", "error": f"no result after {DEADLINE_S} s"}
+            break
+    longest = max(x[2] for x in durations)
+    res = rec.get("result") or {}
+    ok = rec.get("status") == "done" and res.get("success") is True and longest <= MAX_REQUEST_S
+    return {"id": t["id"], "verdict": "PASS" if ok else "FAIL", "status": rec.get("status"),
+            "success": res.get("success"), "chi2r": (res.get("statistics") or {}).get("reduced_chi_square"),
+            "fit_wall_s": round(time.time() - t0, 1), "n_requests": len(durations),
+            "longest_request_s": round(longest, 2), "error": rec.get("error")}
+
+
+def main():
+    targets = json.load(open(sys.argv[1]))
+    base = sys.argv[2] if len(sys.argv) > 2 else "https://xps.fortierlab.org"
+    ids = sys.argv[3:] or DEFAULT_TARGETS
+    by_id = {t["id"]: t for t in targets}
+    results = [run(base, by_id[i]) for i in ids]
+    for r in results:
+        print(json.dumps(r))
+    print("OVERALL:", "PASS" if all(r["verdict"] == "PASS" for r in results) else "FAIL")
+
+
+if __name__ == "__main__":
+    main()
diff --git a/templates/index.html b/templates/index.html
index bb740ac..b81fa84 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -7445,6 +7445,130 @@ async function _readFitReply(resp) {
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
+// The current server fit of each tab record (unit 2, Codex round 1): a new
+// start for the same tab — Ctrl/Cmd+F bypasses the disabled button, and
+// Auto-Fit and Run Fit share a tab — SUPERSEDES the previous job: it is
+// cancelled on the server and its loop returns { _abandoned: 'superseded' },
+// on which the caller does nothing at all (the new fit owns the spinner and
+// the result).
+const _fitJobByOwner = new WeakMap();
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
+  if (guard.owner) {
+    const prev = _fitJobByOwner.get(guard.owner);
+    if (prev && prev !== jobId) _cancelFitJob(prev);
+    _fitJobByOwner.set(guard.owner, jobId);
+  }
+  let misses = 0;
+  try {
+    while (true) {
+      await new Promise(r => setTimeout(r, FIT_POLL_MS));
+      if (guard.signal && guard.signal.aborted) {
+        _cancelFitJob(jobId);
+        throw guard.signal.reason || new DOMException('aborted', 'AbortError');
+      }
+      if (guard.owner && _fitJobByOwner.get(guard.owner) !== jobId) return { _abandoned: 'superseded' };   // its successor cancelled it
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
+    if (guard.owner && _fitJobByOwner.get(guard.owner) === jobId) _fitJobByOwner.delete(guard.owner);
+  }
+}
+
 async function runAutoFitC1sGraphite() {
   // Pre-conditions
   if (!state.rawBE || !state.rawBE.length) { notify('Load a spectrum first.', 'amber'); return; }
@@ -7559,10 +7683,8 @@ async function runAutoFitC1sGraphite() {
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
@@ -7572,21 +7694,31 @@ async function runAutoFitC1sGraphite() {
         // the model without it; a redundant anchor must not set the energy
         // reference of a whole spectrum (see applyAutoFitResult).
         require_component: anchorId,
-      }),
+    }, {
+      owner: fittingTab,
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
+    // superseded by a newer fit on this tab (Run Fit pressed during Auto-Fit):
+    // that fit started from the model now on the tab and owns the result — no
+    // rollback here, which would overwrite it
+    if (json && json._abandoned === 'superseded') return;
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
@@ -8053,26 +8185,29 @@ async function runFit(opts = {}) {
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
+      owner: fittingTab,
+      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
+    });
+    if (json && json._abandoned === 'superseded') return;   // a newer fit on this tab owns the spinner and the result
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

codex
The supersession check runs before each poll, but there’s no check after the response arrives. I’m testing whether an older in-flight response can still win, and whether overlapping start requests register in the right order. I’ll also probe admission-counter cleanup when thread startup fails.
exec
/bin/zsh -lc "cat tests/js/fit_start_poll.test.js; nl -ba app.py | sed -n '630,723p;1255,1315p'; nl -ba templates/index.html | sed -n '7570,7625p;7660,7765p;8085,8190p;8220,8315p'; rg -n 'function _autoFitRestore|function _capture|fittingTab =|function _ownerActive|function _showFitSpinner|function _hideFitSpinner' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
// Unit 2 (2026-09-27): Run Fit and Auto-Fit start the fit and poll for it
// (_serverFitJob). Pinned: the result is the /api/fit body; a bad request's
// message and status are the synchronous route's; ownership (a switched tab,
// an edited model) cancels the server's job and discards; transport keeps its
// meaning (a START that cannot reach the server may fall back to the local
// engine; one lost poll does not; five in a row do); a lost heartbeat, a
// cancelled or errored record are failed fits; F2's NaN rule applies to the
// final record; the 2-minute Auto-Fit abort cancels the job.
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
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
const constLine = n => { const l = lines.find(x => x.startsWith('const ' + n)); assert.ok(l, n); return l; };

// fetch scripted by URL; every call recorded
function server(script) {
  const calls = [];
  const fetch = async (url, init) => {
    calls.push({ url, method: (init && init.method) || 'GET' });
    const h = script(url, init, calls);
    if (h instanceof Error) throw h;
    return h;
  };
  return { fetch, calls };
}
const ok = (obj, status = 200) => ({ ok: true, status, text: async () => (typeof obj === 'string' ? obj : JSON.stringify(obj)) });
const bad = (status, obj) => ({ ok: false, status, json: async () => { if (obj === undefined) throw new SyntaxError('x'); return obj; } });

function make(fetch) {
  const src = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
    'const _runningFitJobs = new Set(); const _fitJobByOwner = new WeakMap();',
    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
  return new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob, _runningFitJobs };')(
    fetch, f => f(), class extends Error { constructor(m, n) { super(m); this.name = n; } });
}
const START = '/api/fit/start';
const isProgress = u => u.startsWith('/api/fit/progress/');
const isCancel = u => u.startsWith('/api/fit/cancel/');

test('start -> running polls -> done: the result is the /api/fit body; no job is left registered', async () => {
  let n = 0;
  const s = server(u => u === START ? ok({ job_id: 'J' }, 202)
    : isProgress(u) ? (++n < 3 ? ok({ status: 'running', heartbeat_age_sec: 0.4 }) : ok({ status: 'done', result: { success: true, x: 1 } }))
    : ok({}));
  const { _serverFitJob, _runningFitJobs } = make(s.fetch);
  assert.deepStrictEqual(await _serverFitJob({ a: 1 }, {}), { success: true, x: 1 });
  assert.strictEqual(s.calls.filter(c => isProgress(c.url)).length, 3);
  assert.strictEqual(_runningFitJobs.size, 0);
  assert.ok(!s.calls.some(c => isCancel(c.url)), 'a finished job is not cancelled');
});

test('a bad request: the synchronous route\'s message and status, immediately; no poll', async () => {
  const s = server(u => u === START ? bad(400, { error: 'n_perturb must be between 0 and 10' }) : assert.fail(u));
  const { _serverFitJob } = make(s.fetch);
  await assert.rejects(_serverFitJob({}, {}), e => e.serverError && e.httpStatus === 400 && /n_perturb must be between/.test(e.message));
});

test('a START that cannot reach the server is a transport failure (the caller may fall back to the local engine)', async () => {
  const s = server(u => new TypeError('Failed to fetch'));
  const { _serverFitJob } = make(s.fetch);
  await assert.rejects(_serverFitJob({}, {}), e => e.transportFailure === true && !e.serverError);
});

test('an error record is a failed fit with the synchronous message and status', async () => {
  const s = server(u => u === START ? ok({ job_id: 'J' }, 202)
    : ok({ status: 'error', http_status: 400, error: 'The model is not determined by these data: 8 free parameters for 6 data points' }));
  const { _serverFitJob } = make(s.fetch);
  await assert.rejects(_serverFitJob({}, {}), e => e.serverError && e.httpStatus === 400 && /not determined by these data/.test(e.message));
});

test('a done record carrying NaN is F2\'s failed fit (unreadable reply), not a transport failure', async () => {
  const s = server(u => u === START ? ok({ job_id: 'J' }, 202)
    : isProgress(u) ? ok('{"status": "done", "result": {"success": true, "s": NaN}}') : ok({}));
  const { _serverFitJob } = make(s.fetch);
  await assert.rejects(_serverFitJob({}, {}), e => e.unreadableReply === true && e.serverError && !e.transportFailure && /non-finite/.test(e.message));
});

test('one lost poll is retried; five in a row are a transport failure and cancel the job', async () => {
  let n = 0;
  const flaky = server(u => u === START ? ok({ job_id: 'J' }, 202)
    : isProgress(u) ? (++n <= 4 ? new TypeError('network') : ok({ status: 'done', result: { success: true } })) : ok({}));
  assert.deepStrictEqual(await make(flaky.fetch)._serverFitJob({}, {}), { success: true });
  const dead = server(u => u === START ? ok({ job_id: 'J' }, 202) : isProgress(u) ? new TypeError('network') : ok({}));
  await assert.rejects(make(dead.fetch)._serverFitJob({}, {}), e => e.transportFailure === true && /Lost contact/.test(e.message));
  assert.ok(dead.calls.some(c => isCancel(c.url) && c.method === 'POST'), 'the server is told to stop');
});

test('a stopped heartbeat (restarted worker) is a failed fit, never an endless spinner', async () => {
  const s = server(u => u === START ? ok({ job_id: 'J' }, 202) : isProgress(u) ? ok({ status: 'running', heartbeat_age_sec: 45 }) : ok({}));
  await assert.rejects(make(s.fetch)._serverFitJob({}, {}), e => e.serverError && /stopped working on the fit/.test(e.message));
});

test('a job cancelled on the server (abandoned) is reported, not waited for', async () => {
  const s = server(u => u === START ? ok({ job_id: 'J' }, 202) : ok({ status: 'cancelled' }));
  await assert.rejects(make(s.fetch)._serverFitJob({}, {}), e => e.serverError && /stopped on the server/.test(e.message));
});

test('ownership inside the loop: a switched tab or an edited model cancels the job and returns the reason', async () => {
  for (const reason of ['tab', 'model']) {
    let polls = 0;
    const s = server(u => u === START ? ok({ job_id: 'J' }, 202) : isProgress(u) ? (polls++, ok({ status: 'running', heartbeat_age_sec: 0 })) : ok({}));
    let t = 0;
    const out = await make(s.fetch)._serverFitJob({}, { abandoned: () => (++t > 2 ? reason : null) });
    assert.deepStrictEqual(out, { _abandoned: reason });
    assert.ok(s.calls.some(c => isCancel(c.url) && c.method === 'POST'), reason + ': the server is told to stop');
    assert.strictEqual(polls, 2, 'no poll after the model or tab changed');
  }
});

test('the Auto-Fit abort (2 minutes) cancels the job and surfaces as an AbortError', async () => {
  const ctrl = { aborted: false, reason: null };
  let polls = 0;
  const s = server(u => u === START ? ok({ job_id: 'J' }, 202) : isProgress(u) ? (++polls === 2 && (ctrl.aborted = true, ctrl.reason = Object.assign(new Error('timeout'), { name: 'AbortError' })), ok({ status: 'running', heartbeat_age_sec: 0 })) : ok({}));
  await assert.rejects(make(s.fetch)._serverFitJob({}, { signal: ctrl }), e => e.name === 'AbortError');
  assert.ok(s.calls.some(c => isCancel(c.url)));
});

test('Run Fit and Auto-Fit both go through _serverFitJob; nothing on the page posts to the synchronous /api/fit any more', () => {
  assert.match(extractFn('runFit'), /await _serverFitJob\(fitReq, \{/);
  assert.match(extractFn('runAutoFitC1sGraphite'), /await _serverFitJob\(\{/);
  assert.ok(!/fetch\('\/api\/fit'/.test(html), 'no synchronous /api/fit fetch left');
  // the ownership reasons are the ones the discard messages handle
  for (const fn of ['runFit', 'runAutoFitC1sGraphite']) {
    const src = extractFn(fn);
    assert.match(src, /_abandoned === 'tab'/, fn);
    assert.match(src, /_abandoned === 'model'/, fn);
  }
  assert.match(html, /addEventListener\('pagehide'/, 'a closed page cancels its running fits');
});

test('a new start for the same tab SUPERSEDES the previous job: cancelled on the server, its loop returns quietly (Codex round 1)', async () => {
  let n = 0;
  let releaseFirst;
  const gate = new Promise(r => { releaseFirst = r; });
  const s = server(u => u === START ? ok({ job_id: 'J' + (++n) }, 202)
    : isProgress(u) ? ok({ status: 'running', heartbeat_age_sec: 0 }) : ok({}));
  // a poll loop that yields between polls, so two jobs can interleave
  const src = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
    'const _runningFitJobs = new Set(); const _fitJobByOwner = new WeakMap();',
    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
  const { _serverFitJob } = new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob };')(
    s.fetch, f => { setImmediate(f); return 0; }, class extends Error {});   // yield to the event loop between polls
  const owner = { id: 'tab-1' };
  let polls2 = 0;
  const first = _serverFitJob({}, { owner });
  await new Promise(r => setImmediate(r)); await new Promise(r => setImmediate(r));
  const second = _serverFitJob({}, { owner, abandoned: () => (++polls2 > 3 ? 'tab' : null) });
  assert.deepStrictEqual(await first, { _abandoned: 'superseded' });
  assert.ok(s.calls.some(c => c.url === '/api/fit/cancel/J1' && c.method === 'POST'), 'the first job is cancelled on the server');
  assert.deepStrictEqual(await second, { _abandoned: 'tab' }, 'the second runs on, owning the tab');
  // another tab's job is not touched
  const other = _serverFitJob({}, { owner: { id: 'tab-2' }, abandoned: () => 'model' });
  assert.deepStrictEqual(await other, { _abandoned: 'model' });
});

test('both callers pass their tab as the owner and do nothing at all when superseded', () => {
  for (const fn of ['runFit', 'runAutoFitC1sGraphite']) {
    const src = extractFn(fn);
    assert.match(src, /owner: fittingTab,/, fn);
    assert.match(src, /if \(json && json\._abandoned === 'superseded'\) return;/, fn);
  }
});
   630	                    if m.stat().st_mtime < cutoff:
   631	                        m.unlink(missing_ok=True)
   632	                except OSError:
   633	                    pass
   634	        except OSError:
   635	            pass
   636	
   637	
   638	def _fit_job_cancel(job_id: str, upload_folder: str) -> None:
   639	    try:
   640	        _fit_job_marker(job_id, upload_folder, "cancel").touch()
   641	    except OSError:
   642	        pass
   643	
   644	
   645	def _fit_job_start(job_id: str, upload_folder: str, fit_args: dict, run) -> None:
   646	    """Start the fit thread and its heartbeat thread. ``run(fit_args, cancel)``
   647	    returns ``(status, body)``; ``(None, None)`` means cancelled."""
   648	    started = time.time()
   649	    lock = threading.Lock()
   650	    rec = {"status": "queued", "elapsed_sec": 0.0, "heartbeat": started}
   651	    _fit_job_write(job_id, upload_folder, rec)
   652	    _fit_job_marker(job_id, upload_folder, "polled").touch()
   653	    cancel_path = _fit_job_marker(job_id, upload_folder, "cancel")
   654	    polled_path = _fit_job_marker(job_id, upload_folder, "polled")
   655	    finished = threading.Event()
   656	
   657	    def cancelled() -> bool:
   658	        if cancel_path.exists():
   659	            return True
   660	        try:
   661	            return time.time() - polled_path.stat().st_mtime > FIT_JOB_ABANDON_SEC
   662	        except OSError:
   663	            return False
   664	
   665	    def heartbeat() -> None:
   666	        while not finished.wait(FIT_JOB_HEARTBEAT_SEC):
   667	            with lock:
   668	                if rec["status"] not in ("running", "queued"):
   669	                    return
   670	                rec["heartbeat"] = time.time()
   671	                rec["elapsed_sec"] = round(time.time() - started, 1)
   672	                _fit_job_write(job_id, upload_folder, rec)
   673	
   674	    def worker() -> None:
   675	        try:
   676	            # queued until a run slot is free; a job cancelled or abandoned
   677	            # while queued never runs
   678	            got = False
   679	            while not got:
   680	                if cancelled():
   681	                    status, body = None, None
   682	                    break
   683	                got = _FIT_JOB_RUN_SLOTS.acquire(timeout=0.5)
   684	            if got:
   685	                try:
   686	                    with lock:
   687	                        rec["status"] = "running"
   688	                        rec["heartbeat"] = time.time()
   689	                        _fit_job_write(job_id, upload_folder, rec)   # visible at once, not at the next heartbeat
   690	                    status, body = run(fit_args, cancelled)
   691	                finally:
   692	                    _FIT_JOB_RUN_SLOTS.release()
   693	        except Exception as exc:                       # the record must always leave "running"
   694	            logging.getLogger(__name__).exception("fit job %s crashed", job_id)
   695	            status, body = 500, {"error": "Internal fitting error — see server log."}
   696	        finally:
   697	            _fit_job_release()
   698	        with lock:
   699	            rec["elapsed_sec"] = round(time.time() - started, 1)
   700	            rec["heartbeat"] = time.time()
   701	            if status is None or cancel_path.exists():
   702	                rec.update(status="cancelled")
   703	            elif status == 200:
   704	                rec.update(status="done", result=body)
   705	            else:
   706	                rec.update(status="error", error=body.get("error"), http_status=status)
   707	            finished.set()
   708	            _fit_job_write(job_id, upload_folder, rec)
   709	        for kind in ("cancel", "polled"):
   710	            try:
   711	                _fit_job_marker(job_id, upload_folder, kind).unlink(missing_ok=True)
   712	            except OSError:
   713	                pass
   714	
   715	    threading.Thread(target=worker, daemon=True, name=f"fit-{job_id[:8]}").start()
   716	    threading.Thread(target=heartbeat, daemon=True, name=f"fit-hb-{job_id[:8]}").start()
   717	
   718	
   719	def _require_json(f):
   720	    """Decorator: return 400 if request body is not valid JSON."""
   721	    @wraps(f)
   722	    def wrapper(*args, **kwargs):
   723	        if not request.is_json:
  1255	    # ── Long fits via start-then-poll (unit 2, 2026-09-27) ───────────────────
  1256	    # The public URL ends a proxied request at ~100 s (Cloudflare 524; 88 s
  1257	    # passed, 125 s failed); basinhopping on the large C 1s models takes 3–4
  1258	    # minutes. The fit runs in a background thread on Find Peaks' job
  1259	    # infrastructure (an atomic JSON record under the upload folder, readable
  1260	    # by whichever gunicorn worker serves a poll); every HTTP request is short.
  1261	    # The record: {status: queued|running|done|error|cancelled, elapsed_sec,
  1262	    # heartbeat (epoch s, rewritten every 2 s while the fit thread lives),
  1263	    # result (done: EXACTLY the /api/fit body), error + http_status (error:
  1264	    # exactly what /api/fit would have answered)}.
  1265	
  1266	    @app.post("/api/fit/start")
  1267	    @_require_json
  1268	    def fit_start():
  1269	        body = request.get_json(silent=True)
  1270	        if not isinstance(body, dict):
  1271	            return _err("request body must be a JSON object")
  1272	        fit_args, error = _prepare_fit_request(app, body)
  1273	        if error is not None:
  1274	            return error
  1275	        upload_folder = app.config["UPLOAD_FOLDER"]
  1276	        if not _fit_job_admit():
  1277	            return _err("The server is busy with other fits. Try again in a moment.", 503)
  1278	        job_id = str(uuid.uuid4())
  1279	        try:
  1280	            _sweep_expired_jobs(upload_folder)
  1281	            _sweep_fit_job_markers(upload_folder)
  1282	            _fit_job_start(job_id, upload_folder, fit_args,
  1283	                           lambda args, cancel: _run_fit_outcome(app, args, cancel=cancel))
  1284	        except Exception:
  1285	            _fit_job_release()          # the job never started: its admission is returned
  1286	            raise
  1287	        return jsonify({"job_id": job_id}), 202
  1288	
  1289	    @app.get("/api/fit/progress/<job_id>")
  1290	    def fit_progress(job_id):
  1291	        try:
  1292	            uuid.UUID(job_id)
  1293	        except ValueError:
  1294	            return _err("Invalid job_id format (expected UUID)", 400)
  1295	        data = _fit_job_read(job_id, app.config["UPLOAD_FOLDER"])
  1296	        if data is None:
  1297	            return _err(f"Job '{job_id}' not found", 404)
  1298	        return app.response_class(json.dumps(data, allow_nan=True), mimetype="application/json")
  1299	
  1300	    @app.post("/api/fit/cancel/<job_id>")
  1301	    def fit_cancel(job_id):
  1302	        try:
  1303	            uuid.UUID(job_id)
  1304	        except ValueError:
  1305	            return _err("Invalid job_id format (expected UUID)", 400)
  1306	        _fit_job_cancel(job_id, app.config["UPLOAD_FOLDER"])
  1307	        return jsonify({"cancelled": True})
  1308	
  1309	    # ── Health check ──────────────────────────────────────────────────────────
  1310	
  1311	    @app.get("/api/health")
  1312	    def health():
  1313	        return jsonify({"status": "ok"})
  1314	
  1315	
  7570	}
  7571	
  7572	async function runAutoFitC1sGraphite() {
  7573	  // Pre-conditions
  7574	  if (!state.rawBE || !state.rawBE.length) { notify('Load a spectrum first.', 'amber'); return; }
  7575	  const tab = tabManager._getTab(tabManager.activeId);
  7576	  if (!tab) { notify('No active tab.', 'amber'); return; }
  7577	  if (!isC1sTab(tab)) {
  7578	    notify('Auto-Fit C1s Graphite is only available for C1s spectra (ROI midpoint 270–315 eV).', 'amber');
  7579	    return;
  7580	  }
  7581	  // OWNER FIRST: the confirmation below is an await; the tab that is active
  7582	  // when it resolves may not be the one the user asked to auto-fit.
  7583	  const fittingTab = _opOwner();
  7584	  if (!fittingTab) { notify('No active spectrum tab.', 'amber'); return; }
  7585	  // Confirmation if existing peaks
  7586	  if (state.peaks.length >= 1) {
  7587	    const proceed = await _showAutoFitConfirmModal(state.peaks.length);
  7588	    if (!proceed) return;
  7589	    if (!_ownerActive(fittingTab)) {
  7590	      notify('Auto-fit cancelled — the tab changed while the confirmation was open.', 'amber');
  7591	      return;
  7592	    }
  7593	  }
  7594	
  7595	  // Snapshot for failure rollback (separate from pushUndo, which only covers peaks).
  7596	  const snap = _autoFitSnapshot();
  7597	
  7598	  // Step 1: find graphite in raw BE
  7599	  const { be: corrBE, inten } = getROIData();
  7600	  if (!corrBE.length) {
  7601	    notify('ROI is empty. Set roi-min and roi-max before auto-fit.', 'red', true);
  7602	    return;
  7603	  }
  7604	  const bgI = computeBackground(corrBE, inten);
  7605	  const bgSub = inten.map((v, i) => v - bgI[i]);
  7606	  // App convention: raw = corrected + state.ccShift
  7607	  const curShift = Number.isFinite(state.ccShift) ? state.ccShift : 0;
  7608	  const rawBE = corrBE.map(b => b + curShift);
  7609	  const graphiteRaw = findGraphiteRawBE(rawBE, bgSub);
  7610	  if (graphiteRaw == null) {
  7611	    notify('No strong peak found in the C1s ROI; Auto-Fit cannot proceed.', 'red', true);
  7612	    return;
  7613	  }
  7614	
  7615	  // Step 2: provisional shift (APP CONVENTION).
  7616	  const provisionalShift = graphiteRaw - 284.50;
  7617	
  7618	  // Step 3: assess low-BE region using provisional shift (no state mutation yet).
  7619	  const assessment = assessLowBERegion(rawBE, bgSub, provisionalShift);
  7620	
  7621	  // Step 4: build the peak model (in corrected frame after provisional shift).
  7622	  pushUndo();
  7623	  state.peaks = [];
  7624	  state.fitResult = null;
  7625	  // Apply provisional shift via updateChargeCorrection so ROI/bg DOM fields
  7660	
  7661	    // The anchor whose necessity the server must test — captured with the
  7662	    // other request inputs, before the first await (a tab switch during the
  7663	    // upload must not send another tab's id).
  7664	    const anchorId = String((state.peaks.find(p => p.name === 'Graphite') || state.peaks[0]).id);
  7665	    // the model and its fit context as sent (F1, Codex round 1): a result must
  7666	    // not be applied, and stamped current, over a model edited while it ran
  7667	    const ctxAtRequest = _startsLiveKey();
  7668	    // Build peak specs and overlay the per-peak bounds we attached in buildAutoFitModel.
  7669	    const peakSpecs = state.peaks.map(p => {
  7670	      const spec = peakToBackendSpec(p);
  7671	      if (Number.isFinite(p._afCenterMin)) spec.center_min = p._afCenterMin;
  7672	      if (Number.isFinite(p._afCenterMax)) spec.center_max = p._afCenterMax;
  7673	      if (Number.isFinite(p._afFwhmMin))   spec.fwhm_min   = p._afFwhmMin;
  7674	      if (Number.isFinite(p._afFwhmMax))   spec.fwhm_max   = p._afFwhmMax;
  7675	      spec.amplitude_min = 0;
  7676	      return spec;
  7677	    });
  7678	
  7679	    const bgPayload = { method: bgType, start_idx: bgWin.i0, end_idx: bgWin.i1 + 1, endpoint_avg: epAvg };
  7680	    if (bgType === 'manual') {
  7681	      // Anchors are stored in corrected-BE space, same frame as the uploaded
  7682	      // session data; backend expects [x, y] pairs.
  7683	      bgPayload.manual_bg = _getManualAnchors().map(a => [a.x, a.y]);
  7684	    }
  7685	    const sessionId = await uploadToBackend(be2, inten2);   // after EVERY input above is captured
  7686	    // Unit 2: started and polled, like Run Fit (the 2-minute abort still applies)
  7687	    const json = await _serverFitJob({
  7688	        session_id: sessionId,
  7689	        background: bgPayload,
  7690	        peaks: peakSpecs,
  7691	        fit_method: fitMethod,
  7692	        n_perturb: 3,
  7693	        // step (c): is the charge-reference anchor REQUIRED? The server refits
  7694	        // the model without it; a redundant anchor must not set the energy
  7695	        // reference of a whole spectrum (see applyAutoFitResult).
  7696	        require_component: anchorId,
  7697	    }, {
  7698	      owner: fittingTab,
  7699	      signal: ctrl.signal,
  7700	      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
  7701	    });
  7702	    clearTimeout(timer);
  7703	    // superseded by a newer fit on this tab (Run Fit pressed during Auto-Fit):
  7704	    // that fit started from the model now on the tab and owns the result — no
  7705	    // rollback here, which would overwrite it
  7706	    if (json && json._abandoned === 'superseded') return;
  7707	    // F2: a non-2xx reply is a failed REQUEST with its status in the message
  7708	    // (_serverFitJob throws it with httpStatus); an unreadable reply is a
  7709	    // failed fit with its own message (unreadableReply).
  7710	    if (json && json._abandoned === 'tab') {
  7711	      _hideFitSpinner();
  7712	      notify('Auto-fit discarded — tab switched during fit.', 'amber');
  7713	      _autoFitRestore(snap, fittingTab);
  7714	      return;
  7715	    }
  7716	    if (json && json._abandoned === 'model') {
  7717	      _hideFitSpinner();
  7718	      notify('Auto-fit discarded because the model or its background / ROI settings were edited while it was running. Previous peaks and result restored. Run it again.', 'amber', true);
  7719	      _autoFitRestore(snap, fittingTab);
  7720	      return;
  7721	    }
  7722	    if (json.error) throw new Error(json.error);
  7723	    if (json.success !== true) throw new Error(json.message || 'fit did not converge');
  7724	    if (!_ownerActive(fittingTab)) {
  7725	      _hideFitSpinner();
  7726	      notify('Auto-fit discarded — tab switched during fit.', 'amber');
  7727	      _autoFitRestore(snap, fittingTab);
  7728	      return;
  7729	    }
  7730	    if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
  7731	      _hideFitSpinner();
  7732	      notify('Auto-fit discarded because the model or its background / ROI settings were edited while it was running. Previous peaks and result restored. Run it again.', 'amber', true);
  7733	      _autoFitRestore(snap, fittingTab);
  7734	      return;
  7735	    }
  7736	
  7737	    applyBackendResult(json);
  7738	
  7739	    const ok = applyAutoFitResult(json, graphiteRaw, { be: be2, inten: inten2, bgIntensity: bgI, bgSubtracted: bgSub });
  7740	    if (!ok) {
  7741	      _hideFitSpinner();
  7742	      _autoFitRestore(snap, fittingTab);
  7743	      return;
  7744	    }
  7745	
  7746	    _hideFitSpinner();
  7747	    notify('Auto-fit complete. χ²ᵣ = ' + (state.fitResult?.chiReduced?.toFixed(3) || '?'), 'green');
  7748	  } catch (e) {
  7749	    clearTimeout(timer);
  7750	    _hideFitSpinner();
  7751	    // The catch path can also fire after a mid-flight tab switch (fetch
  7752	    // error/timeout after the user moved on) — same wrong-tab hazard as
  7753	    // the explicit discard branch, so it gets the same tab-aware restore.
  7754	    _autoFitRestore(snap, fittingTab);
  7755	    let msg;
  7756	    if (e && (e.name === 'AbortError' || (e.message && e.message.toLowerCase().includes('aborted')))) {
  7757	      msg = 'Auto-fit exceeded the 2-minute timeout.';
  7758	    } else if (e && (e.unreadableReply || e.httpStatus)) {
  7759	      msg = 'Auto-fit failed: ' + e.message;
  7760	    } else if (e && e.message) {
  7761	      msg = 'Fit failed to converge or produced an unphysical graphite position.';
  7762	      console.warn('Auto-fit error:', e);
  7763	    } else {
  7764	      msg = 'Auto-fit failed.';
  7765	    }
  8085	  if (_historyPreview && _historyPreview.snapId === key) { _historyClearPreview(); return; }
  8086	  _historyPreview = { snapId: key, altKey: state.fitResult.startsModelKey, peaks, fitResult: { chiReduced: alt.chi2r } };
  8087	  _updateLocalModelBanner();
  8088	  document.querySelectorAll('.hist-row').forEach(r => r.classList.remove('hist-preview-active'));
  8089	  updatePlot();
  8090	}
  8091	
  8092	// Adopting an alternative is the student's decision: explicit, undoable, and
  8093	// recorded. It is ATOMIC by construction: the alternative is only the START of
  8094	// an ordinary server fit (runFit's opts.startPeaks); the live model is written
  8095	// by that fit's success path and by nothing else, so a fit that fails, does
  8096	// not converge, is discarded because the tab changed, or cannot reach the
  8097	// server leaves peaks and result exactly as they were (no local fallback
  8098	// here: the local engine would start from the live model, not from the
  8099	// alternative). runFit's own pushUndo is the single undo entry. A solution
  8100	// that moves a component more than 1 eV from where the student put it is the
  8101	// measured trap (a lower chi-square bought by a chemically absurd relocation),
  8102	// so that case — and only that case — asks first, naming the component and
  8103	// the distance.
  8104	async function useAlternative(k) {
  8105	  const alt = _currentAlternative(k);
  8106	  const peaks = alt && _altPeaks(alt);
  8107	  if (!peaks) { notify(_STARTS_STALE_MSG, 'amber', true); return; }
  8108	  const shift = alt.largest_centre_shift_from_start;
  8109	  const name = _startsPeakName(shift.id);
  8110	  if (Math.abs(shift.ev) > _STARTS_SHIFT_RED_EV &&
  8111	      !confirm(`This solution moves ${name} by ${_startsEv(shift.ev)} from where you placed it. Apply?`)) return;
  8112	  const chosen = { fromChi: state.fitResult.starts.fit.chi2r, toChi: alt.chi2r, shiftName: name, shiftEv: shift.ev };
  8113	  if (_historyPreview) _historyClearPreview();
  8114	  await runFit({ startPeaks: peaks, chosenAlternative: chosen });
  8115	}
  8116	
  8117	async function runFit(opts = {}) {
  8118	  if (!state.rawBE.length) { notify('Load a spectrum first.', 'red', true); return; }
  8119	  if (!state.peaks.length) { notify('Add at least one peak.', 'red'); return; }
  8120	  pushUndo();
  8121	
  8122	  _showFitSpinner();
  8123	  document.getElementById('sb-msg').textContent = 'Fitting\u2026';
  8124	
  8125	  // Capture the tab that owns this fit so that if the user switches tabs
  8126	  // mid-request, we can discard the stale result instead of corrupting the
  8127	  // now-active tab's state.
  8128	  const fittingTab = _opOwner();
  8129	
  8130	  const { be, inten } = getROIData();
  8131	  const bgIntensity = computeBackground(be, inten);
  8132	  const bgSubtracted = inten.map((v, i) => v - bgIntensity[i]);
  8133	
  8134	  // Try Flask backend first
  8135	  let backendResult = null;
  8136	  let ctxAtRequest = null;   // set with the other request inputs; read again by the local fallback
  8137	  try {
  8138	    const bgType  = document.getElementById('bg-type').value;
  8139	    const bgStart = parseFloat(document.getElementById('bg-start').value);
  8140	    const bgEnd   = parseFloat(document.getElementById('bg-end').value);
  8141	    // Inclusive bg window — the same point set computeBackgroundCore draws;
  8142	    // the backend slices end-exclusive, so the request sends i1 + 1.
  8143	    const bgWin = _bgWindowIndices(be, bgStart, bgEnd);
  8144	    // EVERY request input is read from the owner before the upload await:
  8145	    // peaks, method, endpoint averaging and manual anchors (Codex round 2: a
  8146	    // request could carry A's spectrum with B's averaging and anchors).
  8147	    // opts.startPeaks: the request starts from an adopted alternative; the live
  8148	    // model is still the student's until this fit succeeds (useAlternative).
  8149	    const startModel = opts.startPeaks || state.peaks;
  8150	    const peakSpecs = startModel.map(peakToBackendSpec);
  8151	    // scattered-starts check: decided HERE, with the other request inputs,
  8152	    // before the first await (a tab switch during the upload must not turn it off)
  8153	    const nStarts = _startsUnlinkedCount(startModel) >= 2 ? _STARTS_N : 0;
  8154	    // the live model and its fit context as the student pressed the button: a
  8155	    // result must not be written over a model that was edited while it ran
  8156	    ctxAtRequest = _startsLiveKey();
  8157	    const fitMethod = document.getElementById('fit-method').value;
  8158	    const epAvgVal = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
  8159	    const bgPayload = { method: bgType, start_idx: bgWin.i0, end_idx: bgWin.i1 + 1, endpoint_avg: epAvgVal };
  8160	    if (bgType === 'manual') {
  8161	      // Anchors are stored in corrected-BE space, same frame as the uploaded
  8162	      // session data; backend expects [x, y] pairs.
  8163	      bgPayload.manual_bg = _getManualAnchors().map(a => [a.x, a.y]);
  8164	    }
  8165	    // Transport failures (server unreachable, timeout, non-JSON reply) are
  8166	    // the ONLY reason to fall back to the local optimiser. A server-side
  8167	    // validation error or a non-converged optimisation surfaces its message
  8168	    // and leaves the model untouched (unit A0: nothing is shown as a fit
  8169	    // result unless it converged; an HTTP 400 is not a reason to silently
  8170	    // switch engines).
  8171	    // Only a genuine transport failure (network rejection, abort, a body that
  8172	    // could not be read) is marked for fallback; server errors — including a
  8173	    // 2xx body that was read but is not JSON (F2) — carry `serverError`.
  8174	    const _asTransport = (e) => {
  8175	      if (e && !e.serverError && (e instanceof TypeError || e.name === 'AbortError' || e instanceof SyntaxError)) e.transportFailure = true;
  8176	      throw e;
  8177	    };
  8178	    let sessionId;
  8179	    try { sessionId = await uploadToBackend(be, inten); } catch (e) { _asTransport(e); }
  8180	    const fitReq = {
  8181	      session_id: sessionId,
  8182	      background: bgPayload,
  8183	      peaks: peakSpecs,
  8184	      fit_method: fitMethod,
  8185	      n_perturb: 3,
  8186	      n_starts: nStarts       // the server also skips it for the global methods
  8187	    };
  8188	    // Unit 2: started and polled (_serverFitJob) — no request lasts longer than
  8189	    // a poll, so none meets the public URL's ~100 s ceiling. An HTTP failure is
  8190	    // a SERVER failure (serverError), never a reason to switch engines; a
  8220	      const err = new Error(json.message || 'the optimizer did not converge.');
  8221	      err.notConverged = true;
  8222	      throw err;
  8223	    }
  8224	    backendResult = json;
  8225	
  8226	    // If the user switched tabs while the fit was running, discard the result
  8227	    // rather than overwriting the now-active tab's peaks.
  8228	    if (!_ownerActive(fittingTab)) {
  8229	      _hideFitSpinner();
  8230	      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
  8231	      notify('Fit result discarded because you switched tabs during the fit.', 'amber');
  8232	      return;
  8233	    }
  8234	
  8235	    // The peak controls stay editable while the fit runs. A result computed for
  8236	    // the model as it was must not be applied over an edited one (a newly locked
  8237	    // centre would keep its edited value under the server's statistics).
  8238	    if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
  8239	      _hideFitSpinner();
  8240	      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
  8241	      notify('Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.', 'amber', true);
  8242	      return;
  8243	    }
  8244	
  8245	    // Capture pre-fit values for uncertainty validation
  8246	    const _preFit = {};
  8247	    for (const p of state.peaks) {
  8248	      _preFit[p.id] = { center: p.center, fwhm: p.fwhm, amplitude: p.amplitude, glMix: p.glMix };
  8249	    }
  8250	    applyBackendResult(backendResult);
  8251	    { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }   // a new result supersedes imported provenance
  8252	    const stats = backendResult.statistics || {};
  8253	    const chiReduced = stats.reduced_chi_square || 0;
  8254	    const rmse = Math.sqrt((backendResult.residuals || []).reduce((s, v) => s + v * v, 0) / Math.max(1, be.length));
  8255	    const roiRange = { min: _arrMin(be).toFixed(1), max: _arrMax(be).toFixed(1) };
  8256	    state.fitResult = { chi: chiReduced * Math.max(1, be.length - state.peaks.length * 3),
  8257	                        chiReduced, rmse, be, bgSubtracted, bgIntensity, backendResult,
  8258	                        fittedY: backendResult.fitted_y, roiRange, _preFit,
  8259	                        starts: backendResult.starts || null,
  8260	                        startsModelKey: _startsLiveKey(),     // model + context, taken AFTER the result was applied
  8261	                        chosenAlternative: opts.chosenAlternative || null };
  8262	    // a preview of an alternative always belongs to the PREVIOUS result (an identical
  8263	    // key does not make it this one's): clear it unconditionally
  8264	    if (_historyPreview && typeof _historyPreview.snapId === 'string' && _historyPreview.snapId.startsWith('alt:')) _historyPreview = null;
  8265	    state.fitResult.rFactor = _computeRFactor(state.fitResult);
  8266	    _applyStatDisplay(state.fitResult);
  8267	    document.getElementById('sb-msg').textContent = 'Fit complete (lmfit)';
  8268	    _updateRFactorUI(state.fitResult.rFactor);
  8269	    _updateROIDisplay(roiRange);
  8270	    _hideFitSpinner();
  8271	    notify('Fit complete. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3), 'green');
  8272	  } catch (e) {
  8273	    // Fall back to local Levenberg-Marquardt
  8274	    _hideFitSpinner();
  8275	    if (!_ownerActive(fittingTab)) {
  8276	      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
  8277	      notify('Fit cancelled — tab switched during fit.', 'amber');
  8278	      return;
  8279	    }
  8280	    if (e && e.transportFailure && opts.startPeaks) {
  8281	      // Adopting an alternative needs the server: the local engine would start
  8282	      // from the live model, not from the alternative. Nothing was changed.
  8283	      document.getElementById('sb-msg').textContent = 'Fit failed';
  8284	      notify('The server could not be reached, so the alternative was not applied. Previous peaks and result kept.', 'red', true);
  8285	      return;
  8286	    }
  8287	    if (e && e.transportFailure && ctxAtRequest !== null && !_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
  8288	      // The fallback would fit the arrays captured at the press over a model or
  8289	      // context edited since, and stamp the edited one (F1, Codex round 1).
  8290	      _hideFitSpinner();
  8291	      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
  8292	      notify('The server could not be reached, and the model or its background / ROI settings were edited while the fit was running, so no local fit was run. Previous peaks and result kept. Run the fit again.', 'amber', true);
  8293	      return;
  8294	    }
  8295	    if (e && e.transportFailure) {
  8296	      // Server unreachable: the local optimiser is the honest fallback, and
  8297	      // the overlay saying so opens only if it actually converged.
  8298	      if (e.message) console.warn('Backend unreachable, falling back to local LM:', e.message);
  8299	      const local = runFitLocal(be, bgSubtracted, bgIntensity);
  8300	      if (local && local.success && !_snapshotSuppressed) {
  8301	        document.getElementById('localfit-warn-overlay').classList.add('open');
  8302	      }
  8303	      return;
  8304	    }
  8305	    // Server-side error or non-converged optimisation: report it; the
  8306	    // previous peaks and fit result stay exactly as they were.
  8307	    const notConverged = !!(e && e.notConverged);
  8308	    document.getElementById('sb-msg').textContent = notConverged ? 'Fit did not converge' : 'Fit failed';
  8309	    notify((notConverged ? 'Fit did not converge: ' : 'Fit failed: ') + ((e && e.message) || 'unknown error') +
  8310	           ' Previous peaks and result kept.', 'red', true);
  8311	    return;
  8312	  }
  8313	
  8314	  renderPeakList();
  8315	  updatePlot();
2354:function _ownerActive(owner) {
6688:function _showFitSpinner() {
6701:function _hideFitSpinner() {
6997:function _autoFitRestore(snap, owner) {
7583:  const fittingTab = _opOwner();
8128:  const fittingTab = _opOwner();

exec
/bin/zsh -lc 'node --test tests/js/fit_start_poll.test.js tests/js/fit_acceptance.test.js tests/js/stale_statistics.test.js tests/js/per_tab_state.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
exec
/bin/zsh -lc "sed -n '2320,2370p' templates/index.html; sed -n '6680,6720p' templates/index.html; sed -n '6950,7045p' templates/index.html; sed -n '7572,7661p' templates/index.html; head -90 tests/test_fit_start_poll.py; git show --stat 0e62a7f" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 64ms:
commit 0e62a7fe4dbce43fb12c448031fd0aef86dfc5ec
Author: Skye Fortier <skyefortier@gmail.com>
Date:   Sun Sep 27 03:16:22 2026 -0600

    fix(unit 2): Codex round 1 (NO-GO x2) - supersede per tab, bounded concurrency, cancellation normalised, checker deadline
    
    - A new start for the same tab cancels that tab's previous job; the
      superseded loop returns quietly (Ctrl/Cmd+F bypassed the disabled
      button; two jobs for one tab could discard the newer as "model edited").
    - One fit RUNS per worker process (the rest wait "queued", heartbeating,
      cancellable), at most 6 admitted per process, beyond that 503 "busy":
      with production's 4 workers, at most 4 concurrent fits, as before. The
      running transition is written at once.
    - run_fit(cancel=) turns an exception raised after cancellation was
      observed into FitCancelled (Levenberg-Marquardt / Nelder-Mead / DE
      surfaced an abort as their own error).
    - public_fit_poll_check.py: a stopped heartbeat is FAIL, a 20-minute
      deadline per target.
    - Carries F2's round-3 scanner line (identical to fix-acceptance-holes).
    
    JS 463 tests: 461 pass, 2 todo (by design). pytest 1024 passed, 7 skipped.
    Browser :5151: a second Run Fit on the same tab supersedes the first.
    
    Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>

 CLAUDE.md                                          |    5 +-
 app.py                                             |   65 +-
 .../codex/fit_start_poll_recheck_prompt.txt        |   24 +
 docs/autofit/codex/fit_start_poll_verdict_runA.md  | 5464 ++++++++++++++++++
 docs/autofit/codex/fit_start_poll_verdict_runB.md  | 5967 ++++++++++++++++++++
 .../plans/2026-09-26-f2-acceptance-holes.md        |    7 +
 .../plans/2026-09-27-long-fits-start-poll.md       |   17 +-
 fitting.py                                         |    8 +
 scripts/public_fit_poll_check.py                   |   12 +-
 templates/index.html                               |   23 +-
 tests/js/fit_acceptance.test.js                    |   13 +-
 tests/js/fit_start_poll.test.js                    |   35 +-
 tests/js/per_tab_state.test.js                     |    2 +-
 tests/js/stale_statistics.test.js                  |    2 +-
 tests/test_fit_start_poll.py                       |   47 +-
 15 files changed, 11672 insertions(+), 19 deletions(-)

 succeeded in 647ms:
TAP version 13
# Subtest: A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
ok 1 - A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
  ---
  duration_ms: 16.864328
  type: 'test'
  ...
# Subtest: a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
ok 2 - a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
  ---
  duration_ms: 8.123431
  type: 'test'
  ...
# Subtest: a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
ok 3 - a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
  ---
  duration_ms: 5.693373
  type: 'test'
  ...
# Subtest: a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
ok 4 - a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
  ---
  duration_ms: 21.057456
  type: 'test'
  ...
# Subtest: a converged backend result is applied (sanity)
ok 5 - a converged backend result is applied (sanity)
  ---
  duration_ms: 6.780248
  type: 'test'
  ...
# Subtest: the engine/objective labels of a fit result survive spectrum and project save/load
ok 6 - the engine/objective labels of a fit result survive spectrum and project save/load
  ---
  duration_ms: 1.029565
  type: 'test'
  ...
# Subtest: an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
ok 7 - an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
  ---
  duration_ms: 6.212327
  type: 'test'
  ...
# Subtest: an HTTP 502 on the upload is a server failure, not a transport failure
ok 8 - an HTTP 502 on the upload is a server failure, not a transport failure
  ---
  duration_ms: 5.330962
  type: 'test'
  ...
# Subtest: uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
ok 9 - uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
  ---
  duration_ms: 2.853228
  type: 'test'
  ...
# Subtest: every consumer that prints the goodness-of-fit statistic routes through the statistic identity
ok 10 - every consumer that prints the goodness-of-fit statistic routes through the statistic identity
  ---
  duration_ms: 1.229713
  type: 'test'
  ...
# Subtest: uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
ok 11 - uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
  ---
  duration_ms: 1.465942
  type: 'test'
  ...
# Subtest: a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
ok 12 - a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
  ---
  duration_ms: 2.466085
  type: 'test'
  ...
# Subtest: starting-point helpers: keyed on the persisted objective, weighted results untouched
ok 13 - starting-point helpers: keyed on the persisted objective, weighted results untouched
  ---
  duration_ms: 5.868526
  type: 'test'
  ...
# Subtest: Quantify shows the starting-point banner for a local result and not for a weighted one
ok 14 - Quantify shows the starting-point banner for a local result and not for a weighted one
  ---
  duration_ms: 7.758843
  type: 'test'
  ...
# Subtest: every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
ok 15 - every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
  ---
  duration_ms: 2.143442
  type: 'test'
  ...
# Subtest: project save derives the designation from the objective for an older local result lacking the new fields
ok 16 - project save derives the designation from the objective for an older local result lacking the new fields
  ---
  duration_ms: 12.1534
  type: 'test'
  ...
# Subtest: stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
ok 17 - stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
  ---
  duration_ms: 1.172496
  type: 'test'
  ...
# Subtest: _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
ok 18 - _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
  ---
  duration_ms: 4.274771
  type: 'test'
  ...
# Subtest: history preview glow is keyed on the dataset flag, not the label text
ok 19 - history preview glow is keyed on the dataset flag, not the label text
  ---
  duration_ms: 0.771777
  type: 'test'
  ...
# Subtest: spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
ok 20 - spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
  ---
  duration_ms: 0.642103
  type: 'test'
  ...
# Subtest: _applyStatDisplay clears header, tooltip, caption and value together on local → none
ok 21 - _applyStatDisplay clears header, tooltip, caption and value together on local → none
  ---
  duration_ms: 4.890583
  type: 'test'
  ...
# Subtest: _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
ok 22 - _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
  ---
  duration_ms: 2.78846
  type: 'test'
  ...
# Subtest: fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
ok 23 - fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
  ---
  duration_ms: 1.713138
  type: 'test'
  ...
# Subtest: undo/redo snapshots carry and restore model provenance
ok 24 - undo/redo snapshots carry and restore model provenance
  ---
  duration_ms: 4.782464
  type: 'test'
  ...
# Subtest: round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
ok 25 - round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
  ---
  duration_ms: 1.229648
  type: 'test'
  ...
# Subtest: _provenanceOf derives a designation from a live local result, and undo snapshots use it
ok 26 - _provenanceOf derives a designation from a live local result, and undo snapshots use it
  ---
  duration_ms: 2.863686
  type: 'test'
  ...
# Subtest: batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
ok 27 - batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
  ---
  duration_ms: 0.485498
  type: 'test'
  ...
# Subtest: the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
ok 28 - the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
  ---
  duration_ms: 2.847605
  type: 'test'
  ...
# Subtest: round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
ok 29 - round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
  ---
  duration_ms: 0.786524
  type: 'test'
  ...
# Subtest: the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
ok 30 - the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
  ---
  duration_ms: 3.168082
  type: 'test'
  ...
# Subtest: the sidebar banner is sticky at the top of the scrolling panel body
ok 31 - the sidebar banner is sticky at the top of the scrolling panel body
  ---
  duration_ms: 1.268973
  type: 'test'
  ...
# Subtest: the sidebar banner shows on a stack tab whose visible entries draw a local source fit
ok 32 - the sidebar banner shows on a stack tab whose visible entries draw a local source fit
  ---
  duration_ms: 3.606187
  type: 'test'
  ...
# Subtest: every stack chart repaint path refreshes the sidebar designation before any early return
ok 33 - every stack chart repaint path refreshes the sidebar designation before any early return
  ---
  duration_ms: 0.654535
  type: 'test'
  ...
# Subtest: closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
ok 34 - closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
  ---
  duration_ms: 0.19107
  type: 'test'
  ...
# Subtest: W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
ok 35 - W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
  ---
  duration_ms: 3.599266
  type: 'test'
  ...
# Subtest: TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
ok 36 - TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
  ---
  duration_ms: 5.93795
  type: 'test'
  ...
# Subtest: adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
ok 37 - adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
  ---
  duration_ms: 4.594433
  type: 'test'
  ...
# Subtest: adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
ok 38 - adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
  ---
  duration_ms: 3.577515
  type: 'test'
  ...
# Subtest: adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
ok 39 - adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
  ---
  duration_ms: 5.423341
  type: 'test'
  ...
# Subtest: adoption: success records the choice, the starts evidence and the key of the model it describes
ok 40 - adoption: success records the choice, the starts evidence and the key of the model it describes
  ---
  duration_ms: 5.593902
  type: 'test'
  ...
# Subtest: an ordinary Run Fit on one unlinked component does not ask for the starts check
ok 41 - an ordinary Run Fit on one unlinked component does not ask for the starts check
  ---
  duration_ms: 6.129279
  type: 'test'
  ...
# Subtest: a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
ok 42 - a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
  ---
  duration_ms: 5.816149
  type: 'test'
  ...
# Subtest: a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
ok 43 - a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
  ---
  duration_ms: 12.719691
  type: 'test'
  ...
# Subtest: a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
ok 44 - a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
  ---
  duration_ms: 7.540081
  type: 'test'
  ...
# Subtest: a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
ok 45 - a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
  ---
  duration_ms: 11.68878
  type: 'test'
  ...
# Subtest: the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)
ok 46 - the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)
  ---
  duration_ms: 1.361
  type: 'test'
  ...
# Subtest: the token scan is linear and keeps a truncated string a string (Codex round 2)
ok 47 - the token scan is linear and keeps a truncated string a string (Codex round 2)
  ---
  duration_ms: 5.758102
  type: 'test'
  ...
# Subtest: a minus sign counts only after a boundary: "x-Infinity" is malformed, "-Infinity" a token (Codex round 3)
ok 48 - a minus sign counts only after a boundary: "x-Infinity" is malformed, "-Infinity" a token (Codex round 3)
  ---
  duration_ms: 1.571097
  type: 'test'
  ...
# Subtest: start -> running polls -> done: the result is the /api/fit body; no job is left registered
ok 49 - start -> running polls -> done: the result is the /api/fit body; no job is left registered
  ---
  duration_ms: 18.193553
  type: 'test'
  ...
# Subtest: a bad request: the synchronous route's message and status, immediately; no poll
ok 50 - a bad request: the synchronous route's message and status, immediately; no poll
  ---
  duration_ms: 7.441611
  type: 'test'
  ...
# Subtest: a START that cannot reach the server is a transport failure (the caller may fall back to the local engine)
ok 51 - a START that cannot reach the server is a transport failure (the caller may fall back to the local engine)
  ---
  duration_ms: 5.611326
  type: 'test'
  ...
# Subtest: an error record is a failed fit with the synchronous message and status
ok 52 - an error record is a failed fit with the synchronous message and status
  ---
  duration_ms: 5.64244
  type: 'test'
  ...
# Subtest: a done record carrying NaN is F2's failed fit (unreadable reply), not a transport failure
ok 53 - a done record carrying NaN is F2's failed fit (unreadable reply), not a transport failure
  ---
  duration_ms: 5.565308
  type: 'test'
  ...
# Subtest: one lost poll is retried; five in a row are a transport failure and cancel the job
ok 54 - one lost poll is retried; five in a row are a transport failure and cancel the job
  ---
  duration_ms: 11.87722
  type: 'test'
  ...
# Subtest: a stopped heartbeat (restarted worker) is a failed fit, never an endless spinner
ok 55 - a stopped heartbeat (restarted worker) is a failed fit, never an endless spinner
  ---
  duration_ms: 4.992267
  type: 'test'
  ...
# Subtest: a job cancelled on the server (abandoned) is reported, not waited for
ok 56 - a job cancelled on the server (abandoned) is reported, not waited for
  ---
  duration_ms: 5.031534
  type: 'test'
  ...
# Subtest: ownership inside the loop: a switched tab or an edited model cancels the job and returns the reason
ok 57 - ownership inside the loop: a switched tab or an edited model cancels the job and returns the reason
  ---
  duration_ms: 9.984369
  type: 'test'
  ...
# Subtest: the Auto-Fit abort (2 minutes) cancels the job and surfaces as an AbortError
ok 58 - the Auto-Fit abort (2 minutes) cancels the job and surfaces as an AbortError
  ---
  duration_ms: 5.658242
  type: 'test'
  ...
# Subtest: Run Fit and Auto-Fit both go through _serverFitJob; nothing on the page posts to the synchronous /api/fit any more
ok 59 - Run Fit and Auto-Fit both go through _serverFitJob; nothing on the page posts to the synchronous /api/fit any more
  ---
  duration_ms: 3.9198
  type: 'test'
  ...
# Subtest: a new start for the same tab SUPERSEDES the previous job: cancelled on the server, its loop returns quietly (Codex round 1)
ok 60 - a new start for the same tab SUPERSEDES the previous job: cancelled on the server, its loop returns quietly (Codex round 1)
  ---
  duration_ms: 20.232616
  type: 'test'
  ...
# Subtest: both callers pass their tab as the owner and do nothing at all when superseded
ok 61 - both callers pass their tab as the owner and do nothing at all when superseded
  ---
  duration_ms: 1.777392
  type: 'test'
  ...
# Subtest: every module-level mutable is allowlisted with a valid non-C class
ok 62 - every module-level mutable is allowlisted with a valid non-C class
  ---
  duration_ms: 308.626536
  type: 'test'
  ...
# Subtest: inherited property names and anonymous-class names cannot slip through the allowlist
ok 63 - inherited property names and anonymous-class names cannot slip through the allowlist
  ---
  duration_ms: 145.426284
  type: 'test'
  ...
# Subtest: the known class-C holders are gone from module scope
ok 64 - the known class-C holders are gone from module scope
  ---
  duration_ms: 9.897514
  type: 'test'
  ...
# Subtest: async operations capture their owning record before the first await
ok 65 - async operations capture their owning record before the first await
  ---
  duration_ms: 3.404227
  type: 'test'
  ...
# Subtest: undo/redo and Find Peaks apply read the ACTIVE tab record only
ok 66 - undo/redo and Find Peaks apply read the ACTIVE tab record only
  ---
  duration_ms: 0.864956
  type: 'test'
  ...
# Subtest: one accessor classifies a result against a key: none / unverified / current / stale
ok 67 - one accessor classifies a result against a key: none / unverified / current / stale
  ---
  duration_ms: 23.989868
  type: 'test'
  ...
# Subtest: the key is the step (b) key: F1 adds no second binding mechanism and no new key field
ok 68 - the key is the step (b) key: F1 adds no second binding mechanism and no new key field
  ---
  duration_ms: 6.601451
  type: 'test'
  ...
# Subtest: Results panel, current: statistic, RMSE, R and sigma are shown
ok 69 - Results panel, current: statistic, RMSE, R and sigma are shown
  ---
  duration_ms: 18.153802
  type: 'test'
  ...
# Subtest: Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
ok 70 - Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
  ---
  duration_ms: 15.364335
  type: 'test'
  ...
# Subtest: Results panel, unverified (older save, no key): values shown with a plain note
ok 71 - Results panel, unverified (older save, no key): values shown with a plain note
  ---
  duration_ms: 15.079601
  type: 'test'
  ...
# Subtest: status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
ok 72 - status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
  ---
  duration_ms: 13.568102
  type: 'test'
  ...
# Subtest: the stored fitted curve is never drawn, saved or stacked as the fit once stale
ok 73 - the stored fitted curve is never drawn, saved or stacked as the fit once stale
  ---
  duration_ms: 4.905284
  type: 'test'
  ...
# Subtest: saves keep the key and say plainly when the statistics are stale or unverified
ok 74 - saves keep the key and say plainly when the statistics are stale or unverified
  ---
  duration_ms: 2.664379
  type: 'test'
  ...
# Subtest: CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
ok 75 - CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
  ---
  duration_ms: 23.599238
  type: 'test'
  ...
# Subtest: XLSX: stale writes a WARNING row instead of the statistic, and no sigma
ok 76 - XLSX: stale writes a WARNING row instead of the statistic, and no sigma
  ---
  duration_ms: 5.375983
  type: 'test'
  ...
# Subtest: TSV: stale says the Model / Residual columns are the current, unfitted model
ok 77 - TSV: stale says the Model / Residual columns are the current, unfitted model
  ---
  duration_ms: 10.546172
  type: 'test'
  ...
# Subtest: the refresh re-renders Results only when its rendered state differs
ok 78 - the refresh re-renders Results only when its rendered state differs
  ---
  duration_ms: 5.567404
  type: 'test'
  ...
# Subtest: an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
ok 79 - an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
  ---
  duration_ms: 3.643129
  type: 'test'
  ...
# Subtest: Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
ok 80 - Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
  ---
  duration_ms: 4.251223
  type: 'test'
  ...
# Subtest: Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
ok 81 - Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
  ---
  duration_ms: 16.177421
  type: 'test'
  ...
# Subtest: closing the last tab clears the Results panel, header and status statistics too
ok 82 - closing the last tab clears the Results panel, header and status statistics too
  ---
  duration_ms: 0.323138
  type: 'test'
  ...
# Subtest: reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
ok 83 - reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
  ---
  duration_ms: 3.570072
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back
ok 84 - F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back
  ---
  duration_ms: 9.716104
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a Cloudflare 524 (plain-text body) is a failed request with its status, never "could not be read"
ok 85 - F2: Auto-Fit on a Cloudflare 524 (plain-text body) is a failed request with its status, never "could not be read"
  ---
  duration_ms: 7.055922
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a 500 with a JSON error is a failed request with its status, never "could not be read"
ok 86 - F2: Auto-Fit on a 500 with a JSON error is a failed request with its status, never "could not be read"
  ---
  duration_ms: 6.487358
  type: 'test'
  ...
1..86
# tests 86
# suites 0
# pass 86
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 659.481104

exec
/bin/zsh -lc "sed -n '1,160p' tests/js/fit_acceptance.test.js; rg -n 'Auto-Fit discards|autoFitSandbox|function .*uto|_autoFitRestore|module.exports|_serverFitJob|makeRunFit' tests/js/stale_statistics.test.js tests/js/fit_acceptance.test.js; nl -ba templates/index.html | sed -n '7488,7571p'; sed -n '1,65p' app.py; ls -d /Users/skyefortier/xps-app/venv/bin/python*" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
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
  'const _runningFitJobs = new Set(); const _fitJobByOwner = new WeakMap();', ...['_cancelFitJob', '_fitHttpError', '_serverFitJob'].map(n => extractFn(n))].join('\n');
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
  assert.equal(env.calls.applied, 0);
  assert.equal(JSON.stringify(env.state.peaks), before);
  assert.ok(env.calls.notify.some(n => n.kind === 'red' && /fwhm_min must be positive/.test(n.msg)), JSON.stringify(env.calls.notify));
  assert.notEqual(env.dom['localfit-warn-overlay']?.classList._c, 'open', 'no "local fit performed" overlay');
});

test('a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay', async () => {
  const env = makeEnv({ fetchImpl: async () => { throw new TypeError('Failed to fetch'); } });
  await env.runFit();
  assert.equal(env.calls.local, 1, 'local fallback used for a genuine network failure');
  assert.equal(env.dom['localfit-warn-overlay'].classList._c, 'open');
});

test('a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay', async () => {
  const env = makeEnv({ fetchImpl: async () => { throw new TypeError('Failed to fetch'); } });
  // replace the stubbed local fitter with a failing one
  const failing = makeEnv({ fetchImpl: async () => { throw new TypeError('Failed to fetch'); } });
  failing.calls.local = 0;
  // rebuild with a failing runFitLocal
  const dom = failing.dom;
  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n') + '\n' + POLL_SRC;
  const noop = () => {};
  const owner = { id: 1 };
  const state = failing.state;
  const { runFit } = new Function('document', 'state', 'fetch', 'uploadToBackend', 'notify', 'pushUndo', '_showFitSpinner', '_hideFitSpinner',
    '_opOwner', '_ownerActive', 'getROIData', 'computeBackground', 'peakToBackendSpec', '_getManualAnchors', 'applyBackendResult',
    '_computeRFactor', '_CHISQ_TOOLTIP', '_updateRFactorUI', '_updateROIDisplay', 'renderPeakList', 'updatePlot', 'renderResults',
    '_autoSnapshot', 'runFitLocal', '_snapshotSuppressed', 'console', '_applyStatDisplay', '_activeTab', src + '\nreturn { runFit };')(
    { getElementById: id => (dom[id] ||= { value: '', textContent: '', style: {}, setAttribute() {}, classList: { add(c) { this._c = c; }, remove() { this._c = null; }, _c: null } }), querySelector: () => ({}), querySelectorAll: () => [] },
    state, async () => { throw new TypeError('Failed to fetch'); }, async () => 'sid', noop, noop, noop, noop, () => owner, o => o === owner,
    () => ({ be: state.rawBE.slice(), inten: state.rawIntensity.slice() }), b => b.map(() => 0), p => ({ id: p.id }), () => [], noop,
    () => 0.1, '', noop, noop, noop, noop, noop, noop, () => ({ success: false, message: 'did not converge' }), false, { warn: noop }, noop, () => owner);
  await runFit();
  assert.notEqual(dom['localfit-warn-overlay']?.classList._c, 'open', 'overlay must not claim a local fit was performed');
  void env;
});

test('a converged backend result is applied (sanity)', async () => {
  const env = makeEnv({ fetchImpl: okResponse({ success: true, statistics: { reduced_chi_square: 1.2 }, residuals: [], fitted_y: [], individual_peaks: [] }) });
  await env.runFit();
  assert.equal(env.calls.applied, 1);
  assert.equal(env.calls.local, 0);
  assert.notEqual(env.state.fitResult.marker, 'previous');
  assert.equal(env.dom['sb-msg'].textContent, 'Fit complete (lmfit)', 'the success path must run to completion, not die in an exception');
});

test('the engine/objective labels of a fit result survive spectrum and project save/load', () => {
  const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
tests/js/fit_acceptance.test.js:34:// Unit 2: Run Fit starts the fit and polls for it (_serverFitJob). These
tests/js/fit_acceptance.test.js:39:  'const _runningFitJobs = new Set(); const _fitJobByOwner = new WeakMap();', ...['_cancelFitJob', '_fitHttpError', '_serverFitJob'].map(n => extractFn(n))].join('\n');
tests/js/fit_acceptance.test.js:317:  assert.match(grab('function applyAutoFitResult(', 12000), /_applyStatDisplay\(state\.fitResult\)/, 'auto-fit refreshes the statistic display');
tests/js/fit_acceptance.test.js:394:  for (const fn of ['function runFitLocal(', 'async function runFit(', 'function applyAutoFitResult(', 'function clearAllPeaks()']) {
tests/js/fit_acceptance.test.js:476:  assert.match(grab('function _autoFitSnapshot()', 1500), /modelProvenance:/, 'auto-fit snapshot carries provenance');
tests/js/fit_acceptance.test.js:477:  assert.match(grab('function _autoFitRestore(', 3000), /modelProvenance = snap\.modelProvenance/, 'auto-fit restore reinstates it');
tests/js/stale_statistics.test.js:304:// Unit 2: Auto-Fit starts the fit and polls for it (_serverFitJob). Each
tests/js/stale_statistics.test.js:309:  'const _runningFitJobs = new Set(); const _fitJobByOwner = new WeakMap();', ...['_cancelFitJob', '_fitHttpError', '_serverFitJob'].map(extractFn)].join('\n');
tests/js/stale_statistics.test.js:387:test('Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies', async () => {
tests/js/stale_statistics.test.js:397:      _autoFitSnapshot: () => ({}), _autoFitRestore: () => { out.restored = true; }, _showAutoFitConfirmModal: async () => true,
tests/js/stale_statistics.test.js:443:    _autoFitSnapshot: () => ({}), _autoFitRestore: () => { out.restored = true; }, _showAutoFitConfirmModal: async () => true,
tests/js/stale_statistics.test.js:470:    _autoFitSnapshot: () => ({}), _autoFitRestore: () => { out.restored = true; }, _showAutoFitConfirmModal: async () => true,
  7488	  const err = new Error(msg || ((prefix || 'Fit request failed') + ' (HTTP ' + status + ').'));
  7489	  err.serverError = true;
  7490	  err.httpStatus = status;
  7491	  return err;
  7492	}
  7493	async function _serverFitJob(fitReq, guard) {
  7494	  guard = guard || {};
  7495	  const isTransport = e => e && !e.serverError && (e instanceof TypeError || e.name === 'AbortError');
  7496	  let resp;
  7497	  try {
  7498	    resp = await fetch('/api/fit/start', { method: 'POST', headers: { 'Content-Type': 'application/json' },
  7499	                                           body: JSON.stringify(fitReq), signal: guard.signal });
  7500	  } catch (e) { if (isTransport(e)) e.transportFailure = true; throw e; }
  7501	  if (resp.ok === false) {
  7502	    let msg = null;
  7503	    try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
  7504	    throw _fitHttpError(resp.status, msg);
  7505	  }
  7506	  let started;
  7507	  try { started = await _readFitReply(resp); } catch (e) { if (isTransport(e)) e.transportFailure = true; throw e; }
  7508	  const jobId = started && started.job_id;
  7509	  if (!jobId) throw _fitHttpError(resp.status, 'The server did not start the fit (no job id).');
  7510	  _runningFitJobs.add(jobId);
  7511	  if (guard.owner) {
  7512	    const prev = _fitJobByOwner.get(guard.owner);
  7513	    if (prev && prev !== jobId) _cancelFitJob(prev);
  7514	    _fitJobByOwner.set(guard.owner, jobId);
  7515	  }
  7516	  let misses = 0;
  7517	  try {
  7518	    while (true) {
  7519	      await new Promise(r => setTimeout(r, FIT_POLL_MS));
  7520	      if (guard.signal && guard.signal.aborted) {
  7521	        _cancelFitJob(jobId);
  7522	        throw guard.signal.reason || new DOMException('aborted', 'AbortError');
  7523	      }
  7524	      if (guard.owner && _fitJobByOwner.get(guard.owner) !== jobId) return { _abandoned: 'superseded' };   // its successor cancelled it
  7525	      const why = guard.abandoned ? guard.abandoned() : null;
  7526	      if (why) { _cancelFitJob(jobId); return { _abandoned: why }; }
  7527	      let pr, rec;
  7528	      try {
  7529	        pr = await fetch('/api/fit/progress/' + encodeURIComponent(jobId), { signal: guard.signal });
  7530	      } catch (e) {
  7531	        if (e && e.name === 'AbortError') { _cancelFitJob(jobId); throw e; }
  7532	        if (++misses >= FIT_POLL_TRANSPORT_RETRIES) {
  7533	          _cancelFitJob(jobId);
  7534	          const err = new Error('Lost contact with the server during the fit (' + ((e && e.message) || 'network error') + ').');
  7535	          err.transportFailure = true;
  7536	          throw err;
  7537	        }
  7538	        continue;
  7539	      }
  7540	      if (pr.ok === false) {
  7541	        _cancelFitJob(jobId);
  7542	        let msg = null;
  7543	        try { const j = await pr.json(); msg = (j && j.error) || null; } catch (_) { /* non-JSON body */ }
  7544	        throw _fitHttpError(pr.status, msg, 'Lost the fit\'s progress');
  7545	      }
  7546	      try { rec = await _readFitReply(pr); } catch (e) {
  7547	        if (e && e.unreadableReply) { _cancelFitJob(jobId); throw e; }
  7548	        if (++misses >= FIT_POLL_TRANSPORT_RETRIES) {
  7549	          _cancelFitJob(jobId);
  7550	          if (isTransport(e)) e.transportFailure = true;
  7551	          throw e;
  7552	        }
  7553	        continue;
  7554	      }
  7555	      misses = 0;
  7556	      if (rec.status === 'done') return rec.result;
  7557	      if (rec.status === 'error') throw _fitHttpError(rec.http_status || 500, rec.error);
  7558	      if (rec.status === 'cancelled') throw _fitHttpError(409, 'The fit was stopped on the server before it finished. Run it again.');
  7559	      if (Number.isFinite(rec.heartbeat_age_sec) && rec.heartbeat_age_sec > FIT_HEARTBEAT_LOST_SEC) {
  7560	        _cancelFitJob(jobId);
  7561	        throw _fitHttpError(503, 'The server stopped working on the fit (no sign of it for ' + Math.round(rec.heartbeat_age_sec) +
  7562	                                 ' s — it was probably restarted). Run the fit again.');
  7563	      }
  7564	      if (typeof guard.onProgress === 'function') guard.onProgress(rec);
  7565	    }
  7566	  } finally {
  7567	    _runningFitJobs.delete(jobId);
  7568	    if (guard.owner && _fitJobByOwner.get(guard.owner) === jobId) _fitJobByOwner.delete(guard.owner);
  7569	  }
  7570	}
  7571	
"""
app.py – XPS Peak Fitting Flask application.

Gunicorn entry point:
    gunicorn "app:create_app()" -w 4 -b 0.0.0.0:5000

Development:
    python app.py          (uses FLASK_ENV / FLASK_DEBUG from environment)
    flask --app app run    (same, using Flask CLI)

Session model
-------------
Each file upload creates a UUID session.  The parsed arrays are saved as a
compressed NumPy archive at  uploads/<session_id>.npz.  Subsequent fit /
background requests reference the session by ID.  No server‑side memory state
is required, making the app compatible with multi‑worker gunicorn.

REST API
--------
POST /api/upload            Upload a data file; returns session_id + preview data
POST /api/background        Compute background for a session
POST /api/fit               Run peak fitting; returns full result
GET  /api/peak-shapes       List available lineshape names
GET  /api/elements          List built‑in spin‑orbit element presets
GET  /api/xps-reference     Validated periodic-table reference dataset (data/xps/)
GET  /api/session/<id>      Retrieve raw session data
DELETE /api/session/<id>    Delete session files
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
import uuid
from functools import wraps
from pathlib import Path

import numpy as np
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename

import fitting
import parser as xps_parser
import vgd_parser
from xps_reference import XPSReferenceError, load_reference_cached

# Upper bound on the Monte-Carlo uncertainty resampling count accepted by
# /api/fit. Each perturbation re-runs the full composite fit, so an unbounded
# value lets a single request occupy a worker for many minutes (audit F7).
# Adjust here if more resampling is ever needed.
MAX_N_PERTURB = 100

# Session .npz files are deleted by an opportunistic sweep this many days after
# their last modification (audit F13). The sweep runs on each new session write
# — no background thread or scheduler.
SESSION_TTL_DAYS = 7

# ─────────────────────────────────────────────────────────────────────────────
# /api/fit request handling, shared by /api/fit and /api/fit/start (unit 2)
# ─────────────────────────────────────────────────────────────────────────────

def _prepare_fit_request(app, body):
/Users/skyefortier/xps-app/venv/bin/python
/Users/skyefortier/xps-app/venv/bin/python3
/Users/skyefortier/xps-app/venv/bin/python3.12

exec
/bin/zsh -lc "node -e '
const fs = require('\\''fs'\\'');
const path = require('\\''path'\\'');
const testfile = path.resolve('\\''tests/js/fit_start_poll.test.js'\\'');
const prefix = fs.readFileSync(testfile, '\\''utf8'\\'').split(\"test('\\''start ->\")[0];
const {extractFn, constLine, ok, bad} = new Function('\\''require'\\'','\\''__dirname'\\'',prefix + '\\''; return {extractFn,constLine,ok,bad};'\\'')(require,path.dirname(testfile));
function env() {
 const starts=[],polls=[],timers=[],cancel=[];
 const fetch=(url)=>{
  if(url.endsWith('\\''/start'\\'')) return new Promise(r=>starts.push(r));
  if(url.includes('\\''/progress/'\\'')) return new Promise(r=>polls.push({id:url.split('\\''/'\\'').pop(),resolve:r}));
  cancel.push(url.split('\\''/'\\'').pop()); return Promise.resolve(ok({}));
 };
 const src=[constLine('\\''FIT_POLL_MS'\\''),constLine('\\''FIT_POLL_TRANSPORT_RETRIES'\\''),constLine('\\''FIT_HEARTBEAT_LOST_SEC'\\''),'\\''const _runningFitJobs=new Set();const _fitJobByOwner=new WeakMap();'\\'',...['\\''_cancelFitJob'\\'','\\''_fitHttpError'\\'','\\''_readFitReply'\\'','\\''_serverFitJob'\\''].map(extractFn)].join('\\''\\n'\\'');
 const run=new Function('\\''fetch'\\'','\\''setTimeout'\\'',src+'\\'';return _serverFitJob;'\\'')(fetch,f=>timers.push(f));
 return {run,starts,polls,timers,cancel};
}
const flush=async()=>{for(let i=0;i<15;i++)await Promise.resolve();};
(async()=>{
 let e=env(),owner={};
 const a=e.run({which:'\\''older'\\''},{owner}); const b=e.run({which:'\\''newer'\\''},{owner});
 e.starts[1](ok({job_id:'\\''newer'\\''}));await flush();
 e.starts[0](ok({job_id:'\\''older'\\''}));await flush();
 e.timers.shift()();await flush();
 console.log('\\''REVERSED STARTS'\\'',JSON.stringify({cancelled:e.cancel,newerResult:await b}));
 e.timers.shift()();await flush();e.polls.shift().resolve(ok({status:'\\''done'\\'',result:{which:'\\''older'\\''}}));console.log('\\''olderResult'\\'',await a);
 for(const status of ['\\''done'\\'','\\''cancelled'\\'']){
  e=env();owner={};
  const first=e.run({}, {owner}).then(x=>({returned:x}),x=>({threw:x.message}));
  e.starts[0](ok({job_id:'\\''old'\\''}));await flush();e.timers.shift()();await flush();
  const second=e.run({}, {owner});e.starts[1](ok({job_id:'\\''new'\\''}));await flush();
  e.polls[0].resolve(ok({status,result:{success:true,which:'\\''old'\\''}}));await flush();
  console.log('\\''OLD POLL AFTER SUPERSEDE'\\'',status,JSON.stringify({cancelled:e.cancel,oldOutcome:await first}));
  e.timers.shift()();await flush();e.polls[1].resolve(ok({status:'\\''done'\\'',result:{which:'\\''new'\\''}}));await second;
 }
})();
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
REVERSED STARTS {"cancelled":["newer"],"newerResult":{"_abandoned":"superseded"}}
olderResult { which: 'older' }
OLD POLL AFTER SUPERSEDE done {"cancelled":["old"],"oldOutcome":{"returned":{"success":true,"which":"old"}}}
OLD POLL AFTER SUPERSEDE cancelled {"cancelled":["old"],"oldOutcome":{"threw":"The fit was stopped on the server before it finished. Run it again."}}

codex
The 86 focused JavaScript tests pass, but controlled probes reproduced two supersession failures: a delayed older start cancels the newer job, and an older poll already in flight can still return a result or throw after supersession. The latter can trigger Auto-Fit’s rollback against the successor’s model. I’m checking the server failure paths and cancellation normalization next.
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c '
import tempfile, sys
tempfile.tempdir=\"/tmp\"
sys.modules[\"matplotlib\"]=None
import fitting,numpy as np,time,json
x=np.linspace(281,292,300)
comps=[(283.2,2000,.8),(284.5,5000,.9),(285.4,1800,1),(286.6,1500,1.1),(288.4,900,1.4)]
rng=np.random.default_rng(3)
y=rng.poisson(300+sum(a*np.exp(-4*np.log(2)*((x-c)/w)**2) for c,a,w in comps)).astype(float)
p=[dict(id=str(i),shape=\"pseudo_voigt_gl\",center=c+.1,fwhm=w*1.1,amplitude=a*.8,gl_ratio=.3,amplitude_min=0) for i,(c,a,w) in enumerate(comps)]
for method in [\"leastsq\",\"least_squares\",\"nelder\",\"differential_evolution\",\"basinhopping\"]:
 start=time.monotonic()
 try:
  fitting.run_fit(energy=x,counts=y,peak_specs=p,background_method=\"shirley\",fit_kws={\"method\":method},n_perturb=3,n_starts=3,cancel=lambda:time.monotonic()-start>.3)
  print(method,\"completed\",round(time.monotonic()-start,3),flush=True)
 except Exception as e:print(method,type(e).__name__,round(time.monotonic()-start,3),\"threadlocal\",fitting._CANCEL.fn,fitting._CANCEL.hit,flush=True)
original=fitting._run_fit_impl
def unrelated(*a,**kw): raise ValueError(\"unrelated validation\")
fitting._run_fit_impl=unrelated
try:fitting.run_fit(cancel=lambda:False)
except Exception as e:print(\"unrelated error\",type(e).__name__,str(e),\"threadlocal\",fitting._CANCEL.fn,fitting._CANCEL.hit,flush=True)
fitting._run_fit_impl=original
args=dict(energy=x,counts=y,peak_specs=p,background_method=\"shirley\",fit_kws={\"method\":\"leastsq\"},n_perturb=0,n_starts=0)
a=fitting.run_fit(**args);b=fitting.run_fit(**args,cancel=lambda:False)
print(\"leastsq sync/hook identity\",json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True),flush=True)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 5182ms:
leastsq FitCancelled 0.511 threadlocal None False
least_squares FitCancelled 0.393 threadlocal None False
nelder FitCancelled 0.512 threadlocal None False
differential_evolution FitCancelled 0.511 threadlocal None False
basinhopping FitCancelled 0.535 threadlocal None False
unrelated error ValueError unrelated validation threadlocal None False
leastsq sync/hook identity True

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c '
import ast,pathlib,threading,time,types,logging,uuid
tree=ast.parse(pathlib.Path(\"app.py\").read_text())
names={\"_fit_job_admit\",\"_fit_job_release\",\"_fit_job_start\"}
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
route=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name==\"fit_start\")
route.decorator_list=[]
nodes.append(route)
records={}
class Marker:
 def touch(self):pass
 def exists(self):return False
 def stat(self):return types.SimpleNamespace(st_mtime=time.time())
 def unlink(self,**kw):pass
fail_hb=[True]
def thread_factory(*a,**kw):
 if fail_hb[0] and kw.get(\"name\",\"\").startswith(\"fit-hb-\"):
  fail_hb[0]=False
  return types.SimpleNamespace(start=lambda:(_ for _ in ()).throw(RuntimeError(\"cannot start heartbeat thread\")))
 return threading.Thread(*a,**kw)
gate=threading.Event();done=threading.Event();secondgate=threading.Event();seconddone=threading.Event()
def first_run(*a,**kw):
 gate.wait(5);return 200,{}
def second_run(*a,**kw):
 secondgate.wait(5);return 200,{}
def record(j,u,d):
 records[j]=dict(d)
 if d[\"status\"]==\"done\":
  (seconddone if j==\"second\" else done).set()
ns=dict(threading=types.SimpleNamespace(Lock=threading.Lock,Event=threading.Event,Thread=thread_factory),time=time,logging=logging,uuid=uuid,
 FIT_JOB_MAX_ADMITTED=6,_FIT_JOB_ADMITTED=[0],_FIT_JOB_ADMIT_LOCK=threading.Lock(),
 _FIT_JOB_RUN_SLOTS=threading.BoundedSemaphore(1),FIT_JOB_HEARTBEAT_SEC=2,FIT_JOB_ABANDON_SEC=180,
 _fit_job_marker=lambda *a:Marker(),_fit_job_write=record,
 request=types.SimpleNamespace(get_json=lambda **kw:{}),app=types.SimpleNamespace(config={\"UPLOAD_FOLDER\":\"unused\"}),
 _prepare_fit_request=lambda *a:({},None),_sweep_expired_jobs=lambda *a:None,_sweep_fit_job_markers=lambda *a:None,
 _run_fit_outcome=first_run,jsonify=lambda x:x)
exec(compile(ast.Module(body=nodes,type_ignores=[]),\"<actual app functions>\",\"exec\"),ns)
try: ns[\"fit_start\"]()
except RuntimeError as e:print(\"start failed after worker launched:\",e)
print(\"admitted after failed heartbeat\",ns[\"_FIT_JOB_ADMITTED\"][0],\"active worker records\",records)
assert ns[\"_fit_job_admit\"]()
ns[\"_fit_job_start\"](\"second\",\"unused\",{},second_run)
gate.set();assert done.wait(3)
print(\"after failed request'\\''s worker finishes: admitted\",ns[\"_FIT_JOB_ADMITTED\"][0],\"second job still outstanding\",not seconddone.is_set())
additional=sum(ns[\"_fit_job_admit\"]() for _ in range(6))
print(\"additional admissions accepted\",additional,\"total outstanding\",additional+1,\"cap\",ns[\"FIT_JOB_MAX_ADMITTED\"])
secondgate.set();assert seconddone.wait(3)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
start failed after worker launched: cannot start heartbeat thread
admitted after failed heartbeat 0 active worker records {'b2ecf828-15fd-4dbf-85a2-4eb7fd4247aa': {'status': 'running', 'elapsed_sec': 0.0, 'heartbeat': 1790500792.219797}}
after failed request's worker finishes: admitted 0 second job still outstanding True
additional admissions accepted 6 total outstanding 7 cap 6

exec
/bin/zsh -lc "sed -n '300,341p' tests/js/stale_statistics.test.js; sed -n '385,423p' tests/js/stale_statistics.test.js; sed -n '430,487p' tests/js/stale_statistics.test.js; git diff fix-acceptance-holes..HEAD -- tests/js/fit_acceptance.test.js tests/js/stale_statistics.test.js tests/js/per_tab_state.test.js tests/test_browser_bg_window_request.py tests/test_browser_endpoint_avg_default.py CLAUDE.md" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
  refresh();
  assert.strictEqual(env.renders, 2, 'current again');
});

// Unit 2: Auto-Fit starts the fit and polls for it (_serverFitJob). Each
// sandbox scripts the single /api/fit reply it always did; pollify serves it
// as a finished job, and runs the poll loop's short waits at once (the
// 2-minute Auto-Fit timer is left pending, as before).
const POLL_SRC = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
  'const _runningFitJobs = new Set(); const _fitJobByOwner = new WeakMap();', ...['_cancelFitJob', '_fitHttpError', '_serverFitJob'].map(extractFn)].join('\n');
function pollify(deps) {
  const inner = deps.fetch;
  let reply = null;
  deps.fetch = async (url, init) => {
    if (url === '/api/fit/start') {
      const r = await inner('/api/fit', init);
      if (r && r.ok === false) return r;
      reply = r;
      return { ok: true, status: 202, text: async () => JSON.stringify({ job_id: 'job-1' }) };
    }
    if (url.startsWith('/api/fit/progress/')) return { ok: true, status: 200, text: async () => '{"status": "done", "result": ' + (await reply.text()) + '}' };
    if (url.startsWith('/api/fit/cancel/')) return { ok: true, status: 200, json: async () => ({}) };
    return inner(url, init);
  };
  deps.setTimeout = (f, ms) => { if (!(ms >= 60000)) f(); return 1; };
  deps.DOMException = class extends Error { constructor(m, n) { super(m); this.name = n; } };
  return deps;
}

// ── Codex round 1 ───────────────────────────────────────────────────────────
function keyFns() {
  const src = lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n')
    + '\n' + ['_startsModelKey', '_fitKeyCanon', '_sameFitKey', '_statsState'].map(extractFn).join('\n');
  return new Function(src + '\nreturn { _startsModelKey, _sameFitKey, _statsState };')();
}

test('an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not', () => {
  const k = keyFns();
  const peaks = [{ id: 1, shape: 'GL', center: 284.5, fwhm: 1, amplitude: 10 }];
  const ui = { bgType: 'shirley', bgStart: '295', bgEnd: '280', shirleyIter: '10', endpointAvg: '3', roiMin: '280', roiMax: '295' };
  const a = k._startsModelKey(peaks, ui, 0, []);
  assert.ok(k._sameFitKey(a, k._startsModelKey(peaks, { ...ui, roiMin: '280.0', roiMax: '295.00' }, 0, [])), 'same data, same request');
});

test('Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies', async () => {
  const constants = lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n');
  const run = async (editDuringUpload) => {
    const state = { peaks: [], ccShift: 0, rawBE: [285, 284.5, 284], rawIntensity: [10, 20, 10] };
    const dom = {};
    const document = { getElementById: id => (dom[id] ??= { value: ({ 'bg-type': 'none', 'bg-start': '285', 'bg-end': '284', 'bg-endpoint-avg': '3', 'fit-method': 'leastsq' })[id] || '', style: {}, textContent: '', setAttribute() {}, classList: { add() {}, remove() {} } }), querySelector: () => ({}) };
    const tab = { id: 1 };
    const out = { restored: false, applied: 0, notes: [] };
    const tabManager = { activeId: 1, _getTab: () => tab, _captureUI: () => ({ bgType: document.getElementById('bg-type').value, roiMin: '284', roiMax: '285' }), _syncActiveToRecord() {} };
    const deps = { state, document, tabManager, notify: (m, k) => out.notes.push([m, k]), _opOwner: () => tab, _ownerActive: () => true, isC1sTab: () => true,
      _autoFitSnapshot: () => ({}), _autoFitRestore: () => { out.restored = true; }, _showAutoFitConfirmModal: async () => true,
      getROIData: () => ({ be: state.rawBE, inten: state.rawIntensity }), computeBackground: be => be.map(() => 0),
      findGraphiteRawBE: () => 284.5, assessLowBERegion: () => ({}), pushUndo() {}, updateChargeCorrection() {},
      buildAutoFitModel: () => [{ id: 1, name: 'Graphite', shape: 'Gaussian', center: 284.5, fwhm: 1, amplitude: 20 }],
      renderPeakList() {}, _showFitSpinner() {}, _hideFitSpinner() {}, AbortController, setTimeout: () => 1, clearTimeout() {},
      peakToBackendSpec: p => ({ ...p }), _getManualAnchors: () => [],
      uploadToBackend: async () => { if (editDuringUpload) document.getElementById('bg-type').value = 'linear'; return 'sid'; },
      fetch: async () => ({ text: async () => JSON.stringify({ success: true, statistics: { reduced_chi_square: 1 }, fitted_y: [10, 20, 10], residuals: [0, 0, 0] }) }),
      applyBackendResult: () => { out.applied++; }, applyAutoFitResult: () => true };
    const src = constants + '\n' + ['runAutoFitC1sGraphite', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
    await new Function(...Object.keys(pollify(deps)), src + '\n' + POLL_SRC + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
    return out;
  };
  const edited = await run(true);
  assert.strictEqual(edited.applied, 0, 'nothing applied over the edited model');
  assert.strictEqual(edited.restored, true, 'rolled back');
  assert.ok(edited.notes.some(([m, k]) => k === 'amber' && /edited while it was running/.test(m)), JSON.stringify(edited.notes));
  const clean = await run(false);
  assert.strictEqual(clean.applied, 1, 'an unedited run is applied as before');
  assert.strictEqual(clean.restored, false);
});

test('closing the last tab clears the Results panel, header and status statistics too', () => {
  const close = html.slice(html.indexOf('  closeTab(id) {'));
  const last = close.slice(close.indexOf('if (this.tabs.length === 0) {'));
  assert.ok(/renderResults\(\)/.test(last.slice(0, last.indexOf('return;'))), 'the no-result render runs before the early return');
});
  assert.match(extractFn('_doSaveProject'), /rFactor: t\.fitResult\.rFactor \|\| null/, 'project saves keep the fit\'s own R');
  assert.match(extractFn('_doSaveSpectrum'), /rFactor: state\.fitResult\.rFactor \|\| null/, 'spectrum saves keep it too');
});

test('F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back', async () => {
  const constants = lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n');
  const state = { peaks: [], ccShift: 0, rawBE: [285, 284.5, 284], rawIntensity: [10, 20, 10] };
  const dom = {};
  const document = { getElementById: id => (dom[id] ??= { value: ({ 'bg-type': 'none', 'bg-start': '285', 'bg-end': '284', 'bg-endpoint-avg': '3', 'fit-method': 'leastsq' })[id] || '', style: {}, textContent: '', setAttribute() {}, classList: { add() {}, remove() {} } }), querySelector: () => ({}) };
  const tab = { id: 1 };
  const out = { restored: false, applied: 0, notes: [] };
  const deps = { state, document, tabManager: { activeId: 1, _getTab: () => tab, _captureUI: () => ({ bgType: 'none' }), _syncActiveToRecord() {} },
    notify: (m, k) => out.notes.push([m, k]), _opOwner: () => tab, _ownerActive: () => true, isC1sTab: () => true,
    _autoFitSnapshot: () => ({}), _autoFitRestore: () => { out.restored = true; }, _showAutoFitConfirmModal: async () => true,
    getROIData: () => ({ be: state.rawBE, inten: state.rawIntensity }), computeBackground: be => be.map(() => 0),
    findGraphiteRawBE: () => 284.5, assessLowBERegion: () => ({}), pushUndo() {}, updateChargeCorrection() {},
    buildAutoFitModel: () => [{ id: 1, name: 'Graphite', shape: 'Gaussian', center: 284.5, fwhm: 1, amplitude: 20 }],
    renderPeakList() {}, _showFitSpinner() {}, _hideFitSpinner() {}, AbortController, setTimeout: () => 1, clearTimeout() {},
    peakToBackendSpec: p => ({ ...p }), _getManualAnchors: () => [], uploadToBackend: async () => 'sid',
    fetch: async () => ({ text: async () => '{"success": true, "statistics": {"reduced_chi_square": NaN}}' }),
    applyBackendResult: () => { out.applied++; }, applyAutoFitResult: () => true, console: { warn() {} } };
  const src = constants + '\n' + ['runAutoFitC1sGraphite', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
  await new Function(...Object.keys(pollify(deps)), src + '\n' + POLL_SRC + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
  assert.strictEqual(out.applied, 0);
  assert.strictEqual(out.restored, true);
  assert.ok(out.notes.some(([m, k]) => k === 'red' && /^Auto-fit failed: .*non-finite number/.test(m)), JSON.stringify(out.notes));
});

for (const [label, reply, expect] of [
  ['a Cloudflare 524 (plain-text body)', { ok: false, status: 524, json: async () => { throw new SyntaxError('error code: 524'); }, text: async () => 'error code: 524' }, /^Auto-fit failed: Fit request failed \(HTTP 524\)\.$/],
  ['a 500 with a JSON error', { ok: false, status: 500, json: async () => ({ error: 'Internal fitting error' }) }, /^Auto-fit failed: Internal fitting error$/],
]) test(`F2: Auto-Fit on ${label} is a failed request with its status, never "could not be read"`, async () => {
  const constants = lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n');
  const state = { peaks: [], ccShift: 0, rawBE: [285, 284.5, 284], rawIntensity: [10, 20, 10] };
  const dom = {};
  const document = { getElementById: id => (dom[id] ??= { value: ({ 'bg-type': 'none', 'bg-start': '285', 'bg-end': '284', 'bg-endpoint-avg': '3', 'fit-method': 'leastsq' })[id] || '', style: {}, textContent: '', setAttribute() {}, classList: { add() {}, remove() {} } }), querySelector: () => ({}) };
  const tab = { id: 1 };
  const out = { restored: false, applied: 0, notes: [] };
  const deps = { state, document, tabManager: { activeId: 1, _getTab: () => tab, _captureUI: () => ({ bgType: 'none' }), _syncActiveToRecord() {} },
    notify: (m, k) => out.notes.push([m, k]), _opOwner: () => tab, _ownerActive: () => true, isC1sTab: () => true,
    _autoFitSnapshot: () => ({}), _autoFitRestore: () => { out.restored = true; }, _showAutoFitConfirmModal: async () => true,
    getROIData: () => ({ be: state.rawBE, inten: state.rawIntensity }), computeBackground: be => be.map(() => 0),
    findGraphiteRawBE: () => 284.5, assessLowBERegion: () => ({}), pushUndo() {}, updateChargeCorrection() {},
    buildAutoFitModel: () => [{ id: 1, name: 'Graphite', shape: 'Gaussian', center: 284.5, fwhm: 1, amplitude: 20 }],
    renderPeakList() {}, _showFitSpinner() {}, _hideFitSpinner() {}, AbortController, setTimeout: () => 1, clearTimeout() {},
    peakToBackendSpec: p => ({ ...p }), _getManualAnchors: () => [], uploadToBackend: async () => 'sid',
    fetch: async () => reply,
    applyBackendResult: () => { out.applied++; }, applyAutoFitResult: () => true, console: { warn() {} } };
  const src = constants + '\n' + ['runAutoFitC1sGraphite', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
  await new Function(...Object.keys(pollify(deps)), src + '\n' + POLL_SRC + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
  assert.strictEqual(out.applied, 0);
  assert.strictEqual(out.restored, true);
  assert.ok(out.notes.some(([m, k]) => k === 'red' && expect.test(m)), JSON.stringify(out.notes));
  assert.ok(!out.notes.some(([m]) => /could not be read/.test(m)));
});
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-X8wuPpgG' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-M4UUfq6M' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index 67207b4..7acfd9a 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -52,6 +52,9 @@ compatible with multi-worker gunicorn.
 | `DELETE` | `/api/session/<id>`       | Delete session files. |
 | `POST`   | `/api/background`         | Compute background curve for a session. |
 | `POST`   | `/api/fit`                | Run lmfit on a session with peak specs; returns chi², bgIntensity, bgSubtracted, fittedY, per-peak refined params + σ. |
+| `POST`   | `/api/fit/start`          | The same request and validation as `/api/fit` (an immediate identical 400 / 404); runs the SAME `run_fit` in a background thread; returns `{job_id}` 202 (unit 2, 2026-09-27). |
+| `GET`    | `/api/fit/progress/<id>`  | The job record: `status` running / done / error / cancelled, `elapsed_sec`, `heartbeat_age_sec`; `result` = exactly the `/api/fit` body; `error` + `http_status` = exactly what `/api/fit` would answer. |
+| `POST`   | `/api/fit/cancel/<id>`    | Stop the job (every minimisation aborts via lmfit's `iter_cb`); also automatic after 180 s without a poll. |
 
 ## Frontend Architecture
 
@@ -196,6 +199,31 @@ must read each field exactly the way its consumer reads it — integers as
 integers, energies through `parseFloat` — never a generic conversion
 (`_fitKeyCanon`). (Owner, 2026-09-26.)
 
+### Long fits start and poll (unit 2, 2026-09-27)
+
+Run Fit (incl. "Use this solution") and Auto-Fit never hold a request open
+for a fit: `_serverFitJob` starts it (`/api/fit/start`), polls every 0.5 s
+and reads the finished record's `result` (the `/api/fit` body) with F2's
+`_readFitReply` rules. So no request meets the public ~100 s ceiling (the five
+largest C 1s basinhopping models completed in 213–414 s through the poll
+path with no request longer than 0.28 s). Server: Find Peaks' job records
+(atomic JSON under the upload folder, readable by any worker), a fit thread
+and a 2 s heartbeat thread per job; `run_fit(cancel=)` gives every
+`model.fit` an `iter_cb` that aborts once the job is cancelled — without it
+the calls are made exactly as before (Levenberg-Marquardt byte-identical
+either way). Page: the ownership rules run INSIDE the poll loop (a switched
+tab or an edited model cancels the job and discards with the usual message);
+a START that cannot reach the server is still a transport failure (local
+fallback); a poll that cannot is retried, five in a row are; a stopped
+heartbeat (> 30 s) is a failed fit; a closed page sends a cancel beacon, and
+the server cancels a job nobody has polled for 180 s (above the ~1-minute
+timer throttling of hidden browser tabs). A new start for the same tab
+supersedes (cancels) the previous one. Each worker process RUNS one fit at a
+time (the rest wait `queued`) and admits at most 6, beyond that a 503 — with 4
+workers, at most 4 concurrent fits, the bound the synchronous route had. The synchronous `/api/fit` stays
+for scripts, tests and the Python twins. Plan:
+`docs/superpowers/plans/2026-09-27-long-fits-start-poll.md`.
+
 ### Timing claims are measured through the public URL
 
 A request from a student reaches the server through Cloudflare, whose edge
diff --git a/tests/js/fit_acceptance.test.js b/tests/js/fit_acceptance.test.js
index 97734af..14882f4 100644
--- a/tests/js/fit_acceptance.test.js
+++ b/tests/js/fit_acceptance.test.js
@@ -31,6 +31,32 @@ function extractFn(name) {
   assert.fail('unbalanced ' + name);
 }
 
+// Unit 2: Run Fit starts the fit and polls for it (_serverFitJob). These
+// tests script the single /api/fit reply they always did; jobAdapter serves
+// that reply as a finished job (start -> 202 + id; progress -> done + result),
+// and a start that throws is still a transport failure.
+const POLL_SRC = [constLineOf('FIT_POLL_MS'), constLineOf('FIT_POLL_TRANSPORT_RETRIES'), constLineOf('FIT_HEARTBEAT_LOST_SEC'),
+  'const _runningFitJobs = new Set(); const _fitJobByOwner = new WeakMap();', ...['_cancelFitJob', '_fitHttpError', '_serverFitJob'].map(n => extractFn(n))].join('\n');
+function constLineOf(n) { const l = lines.find(x => x.startsWith('const ' + n)); assert.ok(l, n); return l; }
+function jobAdapter(fetchImpl) {
+  let reply = null;
+  return async (url, init) => {
+    if (url === '/api/fit/start') {
+      const r = await fetchImpl('/api/fit', init);
+      if (r && r.ok === false) return r;
+      reply = r;
+      return { ok: true, status: 202, text: async () => JSON.stringify({ job_id: 'job-1' }) };
+    }
+    if (url.startsWith('/api/fit/progress/')) {
+      const r = reply;
+      return { ok: true, status: 200, text: async () => '{"status": "done", "result": ' + (await r.text()) + '}' };
+    }
+    if (url.startsWith('/api/fit/cancel/')) return { ok: true, status: 200, json: async () => ({}) };
+    return fetchImpl(url, init);
+  };
+}
+const immediate = f => { f(); return 0; };
+
 function makeEnv({ fetchImpl, uploadImpl, specImpl, ownerActive }) {
   const dom = {};
   const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, disabled: false,
@@ -41,14 +67,14 @@ function makeEnv({ fetchImpl, uploadImpl, specImpl, ownerActive }) {
     peaks: [{ id: 1, name: 'p', shape: 'Gaussian', center: 285, fwhm: 1.2, amplitude: 50, glMix: 50, asymmetry: 0 }] };
   const owner = { id: 7 };
   const calls = { notify: [], local: 0, applied: 0 };
-  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n');
-  const factory = new Function('document', 'state', 'fetch', 'uploadToBackend', 'notify', 'pushUndo', '_showFitSpinner', '_hideFitSpinner',
+  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n') + '\n' + POLL_SRC;
+  const factory = new Function('setTimeout', 'document', 'state', 'fetch', 'uploadToBackend', 'notify', 'pushUndo', '_showFitSpinner', '_hideFitSpinner',
     '_opOwner', '_ownerActive', 'getROIData', 'computeBackground', 'peakToBackendSpec', '_getManualAnchors', 'applyBackendResult',
     '_computeRFactor', '_CHISQ_TOOLTIP', '_updateRFactorUI', '_updateROIDisplay', 'renderPeakList', 'updatePlot', 'renderResults',
     '_autoSnapshot', 'runFitLocal', '_snapshotSuppressed', 'console', '_applyStatDisplay', '_activeTab',
     src + '\nreturn { runFit };');
   const noop = () => {};
-  const { runFit } = factory(document, state, withText(fetchImpl), uploadImpl || (async () => 'sid'), (msg, kind) => calls.notify.push({ msg, kind }),
+  const { runFit } = factory(immediate, document, state, jobAdapter(withText(fetchImpl)), uploadImpl || (async () => 'sid'), (msg, kind) => calls.notify.push({ msg, kind }),
     noop, noop, noop, () => owner, ownerActive || (o => o === owner), () => ({ be: state.rawBE.slice(), inten: state.rawIntensity.slice() }),
     b => b.map(() => 0), specImpl || (p => ({ id: p.id, shape: 'gaussian' })), () => [], () => { calls.applied++; },
     () => 0.1, '', noop, noop, noop, noop, noop, noop,
@@ -104,7 +130,7 @@ test('a transport failure whose local fallback does NOT converge shows no "local
   failing.calls.local = 0;
   // rebuild with a failing runFitLocal
   const dom = failing.dom;
-  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n');
+  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n') + '\n' + POLL_SRC;
   const noop = () => {};
   const owner = { id: 1 };
   const state = failing.state;
diff --git a/tests/js/per_tab_state.test.js b/tests/js/per_tab_state.test.js
index 7c50461..eeea2c1 100644
--- a/tests/js/per_tab_state.test.js
+++ b/tests/js/per_tab_state.test.js
@@ -34,6 +34,7 @@ const ALLOWLIST = {
   _ssFocusIdx: 'A', _ssFiltered: 'A',
   _fpMeta: 'B', _fpModalDrag: 'A', _fpRegionsSelected: 'A', _fpExpandedElement: 'A',
   _findPeaksApplyConfirmResolver: 'A',
+  _runningFitJobs: 'A', _fitJobByOwner: 'A',   // unit 2: in-flight job ids (pagehide beacon; the current job of each tab record, WeakMap keyed by the record) — no spectrum content       // unit 2: ids of in-flight server fit jobs, for the pagehide cancel beacon — no spectrum content
   _undoDebounce: 'A',         // burst buffer: DOES hold a peaks snapshot, but bound to its owner record at burst start and flushed onto that record only — the async-ownership exception to class A's 'no spectrum content'
   // Populated constant catalogues (read-only tables) and the chart plugin
   // object: class B. Listed, not skipped, so a per-tab store hidden in an
diff --git a/tests/js/stale_statistics.test.js b/tests/js/stale_statistics.test.js
index 3b36b46..f902a59 100644
--- a/tests/js/stale_statistics.test.js
+++ b/tests/js/stale_statistics.test.js
@@ -301,6 +301,31 @@ test('the refresh re-renders Results only when its rendered state differs', () =
   assert.strictEqual(env.renders, 2, 'current again');
 });
 
+// Unit 2: Auto-Fit starts the fit and polls for it (_serverFitJob). Each
+// sandbox scripts the single /api/fit reply it always did; pollify serves it
+// as a finished job, and runs the poll loop's short waits at once (the
+// 2-minute Auto-Fit timer is left pending, as before).
+const POLL_SRC = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
+  'const _runningFitJobs = new Set(); const _fitJobByOwner = new WeakMap();', ...['_cancelFitJob', '_fitHttpError', '_serverFitJob'].map(extractFn)].join('\n');
+function pollify(deps) {
+  const inner = deps.fetch;
+  let reply = null;
+  deps.fetch = async (url, init) => {
+    if (url === '/api/fit/start') {
+      const r = await inner('/api/fit', init);
+      if (r && r.ok === false) return r;
+      reply = r;
+      return { ok: true, status: 202, text: async () => JSON.stringify({ job_id: 'job-1' }) };
+    }
+    if (url.startsWith('/api/fit/progress/')) return { ok: true, status: 200, text: async () => '{"status": "done", "result": ' + (await reply.text()) + '}' };
+    if (url.startsWith('/api/fit/cancel/')) return { ok: true, status: 200, json: async () => ({}) };
+    return inner(url, init);
+  };
+  deps.setTimeout = (f, ms) => { if (!(ms >= 60000)) f(); return 1; };
+  deps.DOMException = class extends Error { constructor(m, n) { super(m); this.name = n; } };
+  return deps;
+}
+
 // ── Codex round 1 ───────────────────────────────────────────────────────────
 function keyFns() {
   const src = lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n')
@@ -379,7 +404,7 @@ test('Auto-Fit discards (and rolls back) a response when the model or context wa
       fetch: async () => ({ text: async () => JSON.stringify({ success: true, statistics: { reduced_chi_square: 1 }, fitted_y: [10, 20, 10], residuals: [0, 0, 0] }) }),
       applyBackendResult: () => { out.applied++; }, applyAutoFitResult: () => true };
     const src = constants + '\n' + ['runAutoFitC1sGraphite', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
-    await new Function(...Object.keys(deps), src + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
+    await new Function(...Object.keys(pollify(deps)), src + '\n' + POLL_SRC + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
     return out;
   };
   const edited = await run(true);
@@ -424,7 +449,7 @@ test('F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply mes
     fetch: async () => ({ text: async () => '{"success": true, "statistics": {"reduced_chi_square": NaN}}' }),
     applyBackendResult: () => { out.applied++; }, applyAutoFitResult: () => true, console: { warn() {} } };
   const src = constants + '\n' + ['runAutoFitC1sGraphite', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
-  await new Function(...Object.keys(deps), src + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
+  await new Function(...Object.keys(pollify(deps)), src + '\n' + POLL_SRC + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
   assert.strictEqual(out.applied, 0);
   assert.strictEqual(out.restored, true);
   assert.ok(out.notes.some(([m, k]) => k === 'red' && /^Auto-fit failed: .*non-finite number/.test(m)), JSON.stringify(out.notes));
@@ -451,7 +476,7 @@ for (const [label, reply, expect] of [
     fetch: async () => reply,
     applyBackendResult: () => { out.applied++; }, applyAutoFitResult: () => true, console: { warn() {} } };
   const src = constants + '\n' + ['runAutoFitC1sGraphite', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
-  await new Function(...Object.keys(deps), src + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
+  await new Function(...Object.keys(pollify(deps)), src + '\n' + POLL_SRC + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
   assert.strictEqual(out.applied, 0);
   assert.strictEqual(out.restored, true);
   assert.ok(out.notes.some(([m, k]) => k === 'red' && expect.test(m)), JSON.stringify(out.notes));
diff --git a/tests/test_browser_bg_window_request.py b/tests/test_browser_bg_window_request.py
index ec16a02..3929747 100644
--- a/tests/test_browser_bg_window_request.py
+++ b/tests/test_browser_bg_window_request.py
@@ -133,7 +133,7 @@ def _setup(page, bg_start, bg_end):
 
 
 def _captured_fit_request(page):
-    with page.expect_request("**/api/fit", timeout=30000) as req_info:
+    with page.expect_request("**/api/fit/start", timeout=30000) as req_info:   # unit 2: the same request body, started then polled
         page.evaluate("() => { runFit(); }")
     body = req_info.value.post_data_json
     page.wait_for_timeout(300)
diff --git a/tests/test_browser_endpoint_avg_default.py b/tests/test_browser_endpoint_avg_default.py
index a40ccd4..86f21cd 100644
--- a/tests/test_browser_endpoint_avg_default.py
+++ b/tests/test_browser_endpoint_avg_default.py
@@ -119,7 +119,7 @@ def test_fresh_tab_defaults_to_3_and_the_fit_request_carries_it(browser, server)
             return { tabUi: tabManager._getTab(tabManager.activeId).ui.endpointAvg,
                      dom: document.getElementById('bg-endpoint-avg').value }; }""")
         assert ui == {"tabUi": "3", "dom": "3"}, ui
-        with pg.expect_request("**/api/fit", timeout=30000) as req:
+        with pg.expect_request("**/api/fit/start", timeout=30000) as req:   # unit 2: the same request body, started then polled
             pg.evaluate("() => { runFit(); }")
         assert req.value.post_data_json["background"]["endpoint_avg"] == 3
         pg.wait_for_timeout(300)

exec
/bin/zsh -lc "node -e '
const fs=require('\\''fs'\\''),path=require('\\''path'\\'');
const file=path.resolve('\\''tests/js/fit_start_poll.test.js'\\'');
const prefix=fs.readFileSync(file,'\\''utf8'\\'').split(\"test('\\''start ->\")[0];
const {extractFn,constLine,ok}=new Function('\\''require'\\'','\\''__dirname'\\'',prefix+'\\'';return {extractFn,constLine,ok};'\\'')(require,path.dirname(file));
const state={peaks:[],rawBE:[285,284.5,284],rawIntensity:[10,20,10],ccShift:0};
const dom={},tab={},timers=[],polls=[],cancelled=[],notes=[];
let starts=0,restored=0,hides=0;
const deps={
 state,document:{getElementById:id=>dom[id]??={value:({'\\''bg-type'\\'':'\\''none'\\'','\\''bg-start'\\'':'\\''285'\\'','\\''bg-end'\\'':'\\''284'\\'','\\''fit-method'\\'':'\\''leastsq'\\''})[id]||'\\'''\\'',style:{}},querySelector:()=>({})},
 tabManager:{activeId:1,_getTab:()=>tab},isC1sTab:()=>true,_opOwner:()=>tab,_ownerActive:()=>true,
 notify:m=>notes.push(m),_autoFitSnapshot:()=>({peaks:state.peaks}),_autoFitRestore:s=>{restored++;state.peaks=s.peaks;},
 getROIData:()=>({be:state.rawBE,inten:state.rawIntensity}),computeBackground:b=>b.map(()=>0),
 findGraphiteRawBE:()=>284.5,assessLowBERegion:()=>({}),pushUndo(){},updateChargeCorrection(){},
 buildAutoFitModel:()=>[{id:1,name:'\\''Graphite'\\'',center:284.5}],renderPeakList(){},_showFitSpinner(){},_hideFitSpinner(){hides++;},
 AbortController,DOMException,setTimeout:(f,ms)=>{if(ms===500)timers.push(f);return 1;},clearTimeout(){},
 _bgWindowIndices:()=>({i0:0,i1:2}),_startsLiveKey:()=>JSON.stringify(state.peaks),_sameFitKey:(a,b)=>a===b,
 peakToBackendSpec:p=>({...p}),_getManualAnchors:()=>[],uploadToBackend:async()=>'\\''sid'\\'',
 fetch:async u=>{if(u.endsWith('\\''/start'\\''))return ok({job_id:'\\''J'\\''+(++starts)});if(u.includes('\\''/cancel/'\\'')){cancelled.push(u);return ok({});}return new Promise(r=>polls.push(r));},
 applyBackendResult(){},applyAutoFitResult:()=>true
};
const src=[constLine('\\''FIT_POLL_MS'\\''),constLine('\\''FIT_POLL_TRANSPORT_RETRIES'\\''),constLine('\\''FIT_HEARTBEAT_LOST_SEC'\\''),'\\''const _runningFitJobs=new Set();const _fitJobByOwner=new WeakMap();'\\'',...['\\''_cancelFitJob'\\'','\\''_fitHttpError'\\'','\\''_readFitReply'\\'','\\''_serverFitJob'\\'','\\''runAutoFitC1sGraphite'\\''].map(extractFn)].join('\\''\\n'\\'');
const {auto,job}=new Function(...Object.keys(deps),src+'\\'';return {auto:runAutoFitC1sGraphite,job:_serverFitJob};'\\'')(...Object.values(deps));
const flush=async()=>{for(let i=0;i<20;i++)await Promise.resolve();};
(async()=>{
 const old=auto();await flush();timers.shift()();await flush();
 const key=JSON.stringify(state.peaks);
 const successor=job({}, {owner:tab,abandoned:()=>JSON.stringify(state.peaks)===key?null:'\\''model'\\''});
 await flush();
 polls.shift()(ok({status:'\\''cancelled'\\''}));await old;
 console.log('\\''superseded Auto-Fit'\\'',JSON.stringify({restored,hides,notes,peaks:state.peaks}));
 timers.shift()();await flush();
 console.log('\\''successor result'\\'',JSON.stringify(await successor));
})();
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
superseded Auto-Fit {"restored":1,"hides":1,"notes":["Auto-fit failed: The fit was stopped on the server before it finished. Run it again."],"peaks":[]}
successor result {"_abandoned":"model"}

codex
The Auto-Fit probe confirmed that a late `cancelled` reply triggers rollback and hides the spinner; the successor then discards its fit as “model edited.” I also reproduced double release of an admission slot when the worker starts but its heartbeat thread fails to start. Cancellation normalization passed across all five solvers, preserved an unrelated `ValueError`, and cleared the thread-local state.
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c '
import ast,pathlib,json,uuid,types
tree=ast.parse(pathlib.Path(\"scripts/public_fit_poll_check.py\").read_text())
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==\"run\")
target=dict(id=\"T\",be=[1],inten=[1],background=dict(method=\"shirley\",start_idx=0,end_idx=1,endpoint_avg=1),specs=[])
for mode in [\"lost\",\"deadline\"]:
 now=[0.0];calls=[]
 def req(url,*a,**kw):
  calls.append(url)
  if url.endswith(\"/upload\"):return 200,b'\\''{\"session_id\":\"S\"}'\\'',.01
  if url.endswith(\"/start\"):return 202,b'\\''{\"job_id\":\"J\"}'\\'',.01
  if \"/cancel/\" in url:return 200,b'\\''{}'\\'',.01
  return 200,json.dumps(dict(status=\"queued\",heartbeat_age_sec=45 if mode==\"lost\" else 0)).encode(),.01
 def sleep(s):now[0]+=s
 ns=dict(json=json,uuid=uuid,time=types.SimpleNamespace(time=lambda:now[0],sleep=sleep),_req=req,MAX_REQUEST_S=10,HEARTBEAT_LOST_S=30,DEADLINE_S=1)
 exec(compile(ast.Module(body=[node],type_ignores=[]),\"<actual acceptance checker>\",\"exec\"),ns)
 out=ns[\"run\"](\"unused\",target)
 print(mode,out[\"verdict\"],out[\"status\"],\"cancel_requests\",sum(\"/cancel/\" in c for c in calls))
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
lost FAIL lost cancel_requests 0
deadline FAIL deadline cancel_requests 1

codex
1. **MAJOR — Superseded jobs still process in-flight poll responses.** [templates/index.html:7556](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7556)  
   Supersession is checked before polling, but never after the response arrives. Start B while A’s poll is pending: A’s late `done` response still returns its result, allowing A to overwrite the model and invalidate B. A late `cancelled` response throws instead of returning `superseded`. **Reproduced through Auto-Fit:** its catch path restored the previous model and hid the spinner; B then returned `model` abandonment. Recheck operation ownership after asynchronous responses and before every success/error exit, including timeout handling.

2. **MAJOR — Response order determines which operation supersedes which.** [templates/index.html:7511](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7511)  
   The WeakMap entry is installed only after receiving the start response. Press Run Fit twice; delay A’s response until B has registered. A then cancels B and declares itself current. **Reproduced:** B returned `{_abandoned: "superseded"}`, while older A returned its result. Delayed uploads create the same ordering problem upstream. Allocate an operation token before the first upload/start await and prevent older operations from reclaiming ownership.

3. **MINOR — Partial thread startup releases admission twice.** [app.py:715](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:715), [app.py:1285](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:1285)  
   If the fit thread starts successfully but the heartbeat thread fails to start, the route releases admission while the fit remains alive. The worker releases it again when finishing, subtracting another job’s admission. **Fault-injection reproduction:** the counter reached zero with another job outstanding, then accepted six further admissions—seven outstanding against the cap of six. Transfer admission ownership explicitly and release it exactly once.

Validation: **86 focused JavaScript tests passed**, but they miss these interleavings. Direct cancellation probes passed across all five solvers; unrelated errors propagated, thread-local state cleared, and Levenberg–Marquardt sync/hook results were byte-identical. Checker heartbeat/deadline probes passed. Filesystem-backed pytest and public timing acceptance were not rerun under read-only constraints.

VERDICT: NO-GO
tokens used
85,950
1. **MAJOR — Superseded jobs still process in-flight poll responses.** [templates/index.html:7556](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7556)  
   Supersession is checked before polling, but never after the response arrives. Start B while A’s poll is pending: A’s late `done` response still returns its result, allowing A to overwrite the model and invalidate B. A late `cancelled` response throws instead of returning `superseded`. **Reproduced through Auto-Fit:** its catch path restored the previous model and hid the spinner; B then returned `model` abandonment. Recheck operation ownership after asynchronous responses and before every success/error exit, including timeout handling.

2. **MAJOR — Response order determines which operation supersedes which.** [templates/index.html:7511](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7511)  
   The WeakMap entry is installed only after receiving the start response. Press Run Fit twice; delay A’s response until B has registered. A then cancels B and declares itself current. **Reproduced:** B returned `{_abandoned: "superseded"}`, while older A returned its result. Delayed uploads create the same ordering problem upstream. Allocate an operation token before the first upload/start await and prevent older operations from reclaiming ownership.

3. **MINOR — Partial thread startup releases admission twice.** [app.py:715](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:715), [app.py:1285](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:1285)  
   If the fit thread starts successfully but the heartbeat thread fails to start, the route releases admission while the fit remains alive. The worker releases it again when finishing, subtracting another job’s admission. **Fault-injection reproduction:** the counter reached zero with another job outstanding, then accepted six further admissions—seven outstanding against the cap of six. Transfer admission ownership explicitly and release it exactly once.

Validation: **86 focused JavaScript tests passed**, but they miss these interleavings. Direct cancellation probes passed across all five solvers; unrelated errors propagated, thread-local state cleared, and Levenberg–Marquardt sync/hook results were byte-identical. Checker heartbeat/deadline probes passed. Filesystem-backed pytest and public timing acceptance were not rerun under read-only constraints.

VERDICT: NO-GO
