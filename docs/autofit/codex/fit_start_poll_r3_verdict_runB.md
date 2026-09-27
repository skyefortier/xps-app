OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0e24f-a566-7803-bb68-e4932fe5634f
--------
user
Re-review unit 2 (long fits via start-then-poll), round 3: branch fix-fit-start-poll. The round-2 fixes are the latest commit (git diff HEAD~1..HEAD); the whole unit is git diff fix-acceptance-holes..HEAD. Earlier verdicts: docs/autofit/codex/fit_start_poll_verdict_run{A,B}.md (round 1), fit_start_poll_r2_verdict_run{A,B}.md (round 2); the round-1 prompt holds the brief, design, sites and acceptance; plan docs/superpowers/plans/2026-09-27-long-fits-start-poll.md section 6 lists every finding and fix. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

ROUND-2 FINDINGS AND FIXES (plan section 6, verbatim):

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

TRY TO BREAK
a. The operation token: claimed before EVERY caller's first await (runFit: before uploadToBackend; Auto-Fit: before uploadToBackend but after its confirm modal — is a Run Fit pressed while the modal is open handled?; "Use this solution" = runFit({startPeaks})); every await inside _serverFitJob followed by a check; the outer catch; cancellation of the right job (an op whose start response arrives after supersession cancels its OWN job; the successor's claim cancels the predecessor's known job); a superseded op never applies, never rolls back, never falls back to the local engine, never hides the newer fit's spinner; two tabs.
b. The admission ownership: heartbeat first, worker second; every exception path (sweeps, marker writes, the first record write) before/after thread starts; the counter under concurrency.
c. Anything earlier rounds verified that these changes touched.
d. The tests: real and non-vacuous (the round-2 reproductions fail on round 1's code).

Finish with VERDICT: GO or VERDICT: NO-GO.
codex
I’ll read the prior verdicts and review criteria, then trace the operation-token and admission changes against concrete race and failure scenarios. I’ll keep the review read-only and finish with a verdict.
exec
/bin/zsh -lc "pwd; git status --short; rg --files -g 'AGENTS.md' -g '*fit_start_poll*' -g '2026-09-27-long-fits-start-poll.md'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-R2BkgnQ0' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-43XWcog4' (errno=Operation not permitted)
?? docs/autofit/codex/fit_start_poll_r3_verdict_runA.md
?? docs/autofit/codex/fit_start_poll_r3_verdict_runB.md
docs/superpowers/plans/2026-09-27-long-fits-start-poll.md
tests/js/fit_start_poll.test.js
tests/test_fit_start_poll.py
docs/autofit/codex/fit_start_poll_verdict_runA.md
docs/autofit/codex/fit_start_poll_r2_verdict_runB.md
docs/autofit/codex/fit_start_poll_r3_verdict_runB.md
docs/autofit/codex/fit_start_poll_recheck2_prompt.txt
docs/autofit/codex/fit_start_poll_recheck_prompt.txt
docs/autofit/codex/fit_start_poll_r2_verdict_runA.md
docs/autofit/codex/fit_start_poll_review_prompt.txt
docs/autofit/codex/fit_start_poll_r3_verdict_runA.md
docs/autofit/codex/fit_start_poll_verdict_runB.md

exec
/bin/zsh -lc 'git diff --stat HEAD~1..HEAD; git diff --stat fix-acceptance-holes..HEAD' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-jBcGO9Na' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-XWZ3tVHk' (errno=Operation not permitted)
 app.py                                             |    10 +-
 .../codex/fit_start_poll_r2_verdict_runA.md        |  4924 ++++++
 .../codex/fit_start_poll_r2_verdict_runB.md        | 15995 +++++++++++++++++++
 .../codex/fit_start_poll_recheck2_prompt.txt       |    26 +
 .../plans/2026-09-27-long-fits-start-poll.md       |    15 +
 templates/index.html                               |    99 +-
 tests/js/fit_acceptance.test.js                    |     2 +-
 tests/js/fit_start_poll.test.js                    |   125 +-
 tests/js/per_tab_state.test.js                     |     2 +-
 tests/js/stale_statistics.test.js                  |     2 +-
 tests/test_fit_start_poll.py                       |    38 +
 11 files changed, 21172 insertions(+), 66 deletions(-)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-1OWJ25bo' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ZUkjB5oD' (errno=Operation not permitted)
 CLAUDE.md                                          |    28 +
 app.py                                             |   430 +-
 .../codex/fit_start_poll_r2_verdict_runA.md        |  4924 ++++++
 .../codex/fit_start_poll_r2_verdict_runB.md        | 15995 +++++++++++++++++++
 .../codex/fit_start_poll_recheck2_prompt.txt       |    26 +
 .../codex/fit_start_poll_recheck_prompt.txt        |    24 +
 .../autofit/codex/fit_start_poll_review_prompt.txt |   116 +
 docs/autofit/codex/fit_start_poll_verdict_runA.md  |  5464 +++++++
 docs/autofit/codex/fit_start_poll_verdict_runB.md  |  5967 +++++++
 .../plans/2026-09-27-long-fits-start-poll.md       |   197 +
 fitting.py                                         |    89 +-
 scripts/public_fit_poll_check.py                   |    97 +
 templates/index.html                               |   236 +-
 tests/js/fit_acceptance.test.js                    |    34 +-
 tests/js/fit_start_poll.test.js                    |   243 +
 tests/js/per_tab_state.test.js                     |     1 +
 tests/js/stale_statistics.test.js                  |    31 +-
 tests/test_browser_bg_window_request.py            |     2 +-
 tests/test_browser_endpoint_avg_default.py         |     2 +-
 tests/test_fit_start_poll.py                       |   254 +
 20 files changed, 34021 insertions(+), 139 deletions(-)

exec
/bin/zsh -lc 'for p in /AGENTS.md /Users/AGENTS.md /Users/skyefortier/AGENTS.md /Users/skyefortier/xps-app/AGENTS.md /Users/skyefortier/xps-app/.claude/AGENTS.md /Users/skyefortier/xps-app/.claude/worktrees/AGENTS.md; do if [ -f "$p" ]; then cat "$p"; fi; done; cat docs/autofit/codex/fit_start_poll_review_prompt.txt; cat docs/superpowers/plans/2026-09-27-long-fits-start-poll.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
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

Finish with VERDICT: GO or VERDICT: NO-GO.# Unit 2 — long fits via start-then-poll (2026-09-27)

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

exec
/bin/zsh -lc 'for p in docs/autofit/codex/fit_start_poll_verdict_runA.md docs/autofit/codex/fit_start_poll_verdict_runB.md docs/autofit/codex/fit_start_poll_r2_verdict_runA.md docs/autofit/codex/fit_start_poll_r2_verdict_runB.md; do tail -n 100 "$p"; done' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
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
(async()=>{
const old=api.runAutoFitC1sGraphite();await tick();waits.shift()();await tick();
const newer=api.runFit();await tick();resolveOld(ok({status:'\\''cancelled'\\''}));await old;waits.splice(0).forEach(f=>f());await newer;
console.log(JSON.stringify({state,out}));
})();
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
{"state":{"peaks":[],"ccShift":0,"rawBE":[285,284.5,284],"rawIntensity":[10,20,10],"fitResult":null,"nextId":2},"out":{"restores":1,"hides":2,"notes":[["Auto-fit failed: The fit was stopped on the server before it finished. Run it again.","red"],["Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.","amber"]],"cancels":["/api/fit/cancel/AUTO","/api/fit/cancel/RUN"]}}

codex
The caller-level probe confirms the rollback failure: a superseded Auto-Fit restores its old snapshot, then the replacement Run Fit cancels itself because the model changed. I also reproduced a double admission release when the fit thread starts but heartbeat-thread startup fails. The three numerical cancellation tests pass; I’m wrapping up with these findings.
exec
/bin/zsh -lc "git status --short; nl -ba app.py | sed -n '1273,1288p'; nl -ba templates/index.html | sed -n '7746,7756p'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-90XAE1es' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-CDDtvbwm' (errno=Operation not permitted)
?? docs/autofit/codex/fit_start_poll_r2_verdict_runA.md
?? docs/autofit/codex/fit_start_poll_r2_verdict_runB.md
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

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c '
import tempfile,sys
tempfile.tempdir=\"/tmp\"
sys.modules[\"matplotlib\"]=None
import fitting
old=fitting._run_fit_impl
error=ValueError(\"unrelated validation error\")
def bad(*a,**kw): raise error
fitting._run_fit_impl=bad
try:
    fitting.run_fit(cancel=lambda: True)
except ValueError as exc:
    assert exc is error
else: raise AssertionError(\"error swallowed\")
assert fitting._cancel_kw()=={}
def observed(*a,**kw):
    fitting._cancel_kw()[\"iter_cb\"](None,0,None)
    raise RuntimeError(\"solver abort\")
fitting._run_fit_impl=observed
try:
    fitting.run_fit(cancel=lambda: True)
except fitting.FitCancelled: pass
else: raise AssertionError(\"not normalized\")
assert fitting._cancel_kw()=={}
fitting._run_fit_impl=old
print(\"Unobserved cancellation preserves unrelated exception; observed cancellation normalized; thread-local cleared on both exceptional paths.\")
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 1380ms:
Unobserved cancellation preserves unrelated exception; observed cancellation normalized; thread-local cleared on both exceptional paths.

codex
1. **MAJOR — Start-response order determines ownership.** [templates/index.html:7511](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7511) registers ownership only after awaiting the start response. Reproduced: invocation A starts first, B’s response arrives first, then A’s delayed response cancels B. B returns `superseded`; A returns its result. Delayed uploads permit the same reversal. Establish an invocation token before the caller’s first await.

2. **MAJOR — Superseded polls still apply results or trigger rollback.** [templates/index.html:7556](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7556) handles terminal responses without rechecking ownership after the fetch/body awaits. Reproduced with the actual callers: Auto-Fit has a poll in flight; Run Fit supersedes it; the old poll returns `cancelled`. Auto-Fit throws and restores its snapshot at [templates/index.html:7754](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7754), causing the replacement to discard itself as “model edited.” A delayed `done` response also returns the obsolete result. Recheck supersession after asynchronous boundaries and before error handling, rollback, or result application; supersession must also precede timeout handling.

3. **MINOR — Partial thread startup releases admission twice.** [app.py:716](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:716), [app.py:1285](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:1285). If the fit thread starts but heartbeat-thread startup raises, the route releases admission although the worker remains alive. Its eventual `finally` releases again. Fault injection reproduced seven outstanding jobs against the six-job cap. Make admission release have exactly one owner after worker startup.

Validation: 86 targeted JavaScript tests and three numerical cancellation tests passed. Additional in-memory probes reproduced all findings and verified unrelated exceptions remain unchanged and cancellation thread-local state clears. Files unchanged; full server acceptance was not rerun in this read-only environment.

**VERDICT: NO-GO**
tokens used
77,361
1. **MAJOR — Start-response order determines ownership.** [templates/index.html:7511](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7511) registers ownership only after awaiting the start response. Reproduced: invocation A starts first, B’s response arrives first, then A’s delayed response cancels B. B returns `superseded`; A returns its result. Delayed uploads permit the same reversal. Establish an invocation token before the caller’s first await.

2. **MAJOR — Superseded polls still apply results or trigger rollback.** [templates/index.html:7556](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7556) handles terminal responses without rechecking ownership after the fetch/body awaits. Reproduced with the actual callers: Auto-Fit has a poll in flight; Run Fit supersedes it; the old poll returns `cancelled`. Auto-Fit throws and restores its snapshot at [templates/index.html:7754](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7754), causing the replacement to discard itself as “model edited.” A delayed `done` response also returns the obsolete result. Recheck supersession after asynchronous boundaries and before error handling, rollback, or result application; supersession must also precede timeout handling.

3. **MINOR — Partial thread startup releases admission twice.** [app.py:716](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:716), [app.py:1285](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:1285). If the fit thread starts but heartbeat-thread startup raises, the route releases admission although the worker remains alive. Its eventual `finally` releases again. Fault injection reproduced seven outstanding jobs against the six-job cap. Make admission release have exactly one owner after worker startup.

Validation: 86 targeted JavaScript tests and three numerical cancellation tests passed. Additional in-memory probes reproduced all findings and verified unrelated exceptions remain unchanged and cancellation thread-local state clears. Files unchanged; full server acceptance was not rerun in this read-only environment.

**VERDICT: NO-GO**
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

exec
/bin/zsh -lc 'git diff HEAD~1..HEAD -- app.py templates/index.html tests/js/fit_start_poll.test.js tests/test_fit_start_poll.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Px0EbMXU' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-MWJ0iqg5' (errno=Operation not permitted)
diff --git a/app.py b/app.py
index 2dd37a5..79c5eb2 100644
--- a/app.py
+++ b/app.py
@@ -712,8 +712,16 @@ def _fit_job_start(job_id: str, upload_folder: str, fit_args: dict, run) -> None
             except OSError:
                 pass
 
-    threading.Thread(target=worker, daemon=True, name=f"fit-{job_id[:8]}").start()
+    # The heartbeat thread starts FIRST: if either thread fails to start this
+    # raises BEFORE the worker runs, and the route returns the admission; once
+    # the worker has started, only the worker's finally returns it (exactly
+    # one owner; Codex round 2).
     threading.Thread(target=heartbeat, daemon=True, name=f"fit-hb-{job_id[:8]}").start()
+    try:
+        threading.Thread(target=worker, daemon=True, name=f"fit-{job_id[:8]}").start()
+    except Exception:
+        finished.set()                # stop the heartbeat of a job that never ran
+        raise
 
 
 def _require_json(f):
diff --git a/templates/index.html b/templates/index.html
index b81fa84..ddbc6d8 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -7467,13 +7467,26 @@ const FIT_POLL_MS = 500;
 const FIT_POLL_TRANSPORT_RETRIES = 5;
 const FIT_HEARTBEAT_LOST_SEC = 30;
 const _runningFitJobs = new Set();
-// The current server fit of each tab record (unit 2, Codex round 1): a new
-// start for the same tab — Ctrl/Cmd+F bypasses the disabled button, and
-// Auto-Fit and Run Fit share a tab — SUPERSEDES the previous job: it is
-// cancelled on the server and its loop returns { _abandoned: 'superseded' },
-// on which the caller does nothing at all (the new fit owns the spinner and
-// the result).
-const _fitJobByOwner = new WeakMap();
+// One fit OPERATION per tab record (unit 2, Codex rounds 1-2). A caller claims
+// its operation BEFORE ITS FIRST AWAIT (_claimFitOp): the newest claim for a
+// tab is the current one, whatever order the server's responses come back in.
+// A claim cancels the previous operation's server job; the previous
+// operation's _serverFitJob, at every step after an await and before every
+// exit — a result, an error, a timeout — sees it is no longer current,
+// cancels its own job if it has one, and returns { _abandoned: 'superseded' },
+// on which its caller does NOTHING (the newer fit owns spinner and result).
+// Ctrl/Cmd+F bypasses the disabled Run Fit button, and Run Fit and Auto-Fit
+// share a tab.
+let _fitOpSeq = 0;
+const _fitOpByOwner = new WeakMap();
+function _claimFitOp(owner) {
+  const prev = owner ? _fitOpByOwner.get(owner) : null;
+  if (prev && prev.jobId) _cancelFitJob(prev.jobId);
+  const op = { seq: ++_fitOpSeq, owner: owner || null, jobId: null };
+  if (owner) _fitOpByOwner.set(owner, op);
+  return op;
+}
+function _fitOpCurrent(op) { return !op || !op.owner || _fitOpByOwner.get(op.owner) === op; }
 function _cancelFitJob(jobId) {
   try { fetch('/api/fit/cancel/' + encodeURIComponent(jobId), { method: 'POST', keepalive: true }).catch(() => {}); } catch (_) { /* best effort */ }
 }
@@ -7492,42 +7505,46 @@ function _fitHttpError(status, msg, prefix) {
 }
 async function _serverFitJob(fitReq, guard) {
   guard = guard || {};
+  const op = guard.op || null;
+  const SUP = { _abandoned: 'superseded' };
+  let jobId = null;
+  const gone = () => !_fitOpCurrent(op);
+  const superseded = () => { if (jobId) _cancelFitJob(jobId); return SUP; };
   const isTransport = e => e && !e.serverError && (e instanceof TypeError || e.name === 'AbortError');
-  let resp;
-  try {
-    resp = await fetch('/api/fit/start', { method: 'POST', headers: { 'Content-Type': 'application/json' },
-                                           body: JSON.stringify(fitReq), signal: guard.signal });
-  } catch (e) { if (isTransport(e)) e.transportFailure = true; throw e; }
-  if (resp.ok === false) {
-    let msg = null;
-    try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
-    throw _fitHttpError(resp.status, msg);
-  }
-  let started;
-  try { started = await _readFitReply(resp); } catch (e) { if (isTransport(e)) e.transportFailure = true; throw e; }
-  const jobId = started && started.job_id;
-  if (!jobId) throw _fitHttpError(resp.status, 'The server did not start the fit (no job id).');
-  _runningFitJobs.add(jobId);
-  if (guard.owner) {
-    const prev = _fitJobByOwner.get(guard.owner);
-    if (prev && prev !== jobId) _cancelFitJob(prev);
-    _fitJobByOwner.set(guard.owner, jobId);
-  }
-  let misses = 0;
   try {
+    if (gone()) return SUP;
+    let resp;
+    try {
+      resp = await fetch('/api/fit/start', { method: 'POST', headers: { 'Content-Type': 'application/json' },
+                                             body: JSON.stringify(fitReq), signal: guard.signal });
+    } catch (e) { if (isTransport(e)) e.transportFailure = true; throw e; }
+    if (resp.ok === false) {
+      let msg = null;
+      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
+      throw _fitHttpError(resp.status, msg);
+    }
+    let started;
+    try { started = await _readFitReply(resp); } catch (e) { if (isTransport(e)) e.transportFailure = true; throw e; }
+    jobId = started && started.job_id;
+    if (!jobId) throw _fitHttpError(resp.status, 'The server did not start the fit (no job id).');
+    _runningFitJobs.add(jobId);
+    if (gone()) return superseded();            // a newer claim came while this start was in flight
+    if (op) op.jobId = jobId;
+    let misses = 0;
     while (true) {
       await new Promise(r => setTimeout(r, FIT_POLL_MS));
+      if (gone()) return superseded();
       if (guard.signal && guard.signal.aborted) {
         _cancelFitJob(jobId);
         throw guard.signal.reason || new DOMException('aborted', 'AbortError');
       }
-      if (guard.owner && _fitJobByOwner.get(guard.owner) !== jobId) return { _abandoned: 'superseded' };   // its successor cancelled it
       const why = guard.abandoned ? guard.abandoned() : null;
       if (why) { _cancelFitJob(jobId); return { _abandoned: why }; }
       let pr, rec;
       try {
         pr = await fetch('/api/fit/progress/' + encodeURIComponent(jobId), { signal: guard.signal });
       } catch (e) {
+        if (gone()) return superseded();
         if (e && e.name === 'AbortError') { _cancelFitJob(jobId); throw e; }
         if (++misses >= FIT_POLL_TRANSPORT_RETRIES) {
           _cancelFitJob(jobId);
@@ -7537,6 +7554,7 @@ async function _serverFitJob(fitReq, guard) {
         }
         continue;
       }
+      if (gone()) return superseded();            // the reply of a poll made before a newer claim
       if (pr.ok === false) {
         _cancelFitJob(jobId);
         let msg = null;
@@ -7544,6 +7562,7 @@ async function _serverFitJob(fitReq, guard) {
         throw _fitHttpError(pr.status, msg, 'Lost the fit\'s progress');
       }
       try { rec = await _readFitReply(pr); } catch (e) {
+        if (gone()) return superseded();
         if (e && e.unreadableReply) { _cancelFitJob(jobId); throw e; }
         if (++misses >= FIT_POLL_TRANSPORT_RETRIES) {
           _cancelFitJob(jobId);
@@ -7552,6 +7571,7 @@ async function _serverFitJob(fitReq, guard) {
         }
         continue;
       }
+      if (gone()) return superseded();
       misses = 0;
       if (rec.status === 'done') return rec.result;
       if (rec.status === 'error') throw _fitHttpError(rec.http_status || 500, rec.error);
@@ -7563,9 +7583,12 @@ async function _serverFitJob(fitReq, guard) {
       }
       if (typeof guard.onProgress === 'function') guard.onProgress(rec);
     }
+  } catch (e) {
+    if (gone()) return superseded();              // superseded wins over any error, incl. a timeout
+    throw e;
   } finally {
-    _runningFitJobs.delete(jobId);
-    if (guard.owner && _fitJobByOwner.get(guard.owner) === jobId) _fitJobByOwner.delete(guard.owner);
+    if (jobId) _runningFitJobs.delete(jobId);
+    if (op && op.jobId === jobId) op.jobId = null;
   }
 }
 
@@ -7645,6 +7668,7 @@ async function runAutoFitC1sGraphite() {
   if (runBtn) runBtn.disabled = true;
 
   const ctrl = new AbortController();
+  let afOp = null;   // unit 2: this tab's fit operation (claimed below, before the first server await)
   const timer = setTimeout(() => ctrl.abort(new DOMException('timeout', 'AbortError')), 120000);
 
   try {
@@ -7665,6 +7689,7 @@ async function runAutoFitC1sGraphite() {
     // the model and its fit context as sent (F1, Codex round 1): a result must
     // not be applied, and stamped current, over a model edited while it ran
     const ctxAtRequest = _startsLiveKey();
+    afOp = _claimFitOp(fittingTab);   // unit 2: before the first server await; the newest claim for a tab is current
     // Build peak specs and overlay the per-peak bounds we attached in buildAutoFitModel.
     const peakSpecs = state.peaks.map(p => {
       const spec = peakToBackendSpec(p);
@@ -7695,7 +7720,7 @@ async function runAutoFitC1sGraphite() {
         // reference of a whole spectrum (see applyAutoFitResult).
         require_component: anchorId,
     }, {
-      owner: fittingTab,
+      op: afOp,
       signal: ctrl.signal,
       abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
     });
@@ -7747,6 +7772,9 @@ async function runAutoFitC1sGraphite() {
     notify('Auto-fit complete. χ²ᵣ = ' + (state.fitResult?.chiReduced?.toFixed(3) || '?'), 'green');
   } catch (e) {
     clearTimeout(timer);
+    // superseded (Run Fit pressed during Auto-Fit): nothing at all — no
+    // rollback (it would overwrite the newer fit's model), no message
+    if (afOp && !_fitOpCurrent(afOp)) return;
     _hideFitSpinner();
     // The catch path can also fire after a mid-flight tab switch (fetch
     // error/timeout after the user moved on) — same wrong-tab hazard as
@@ -8134,6 +8162,7 @@ async function runFit(opts = {}) {
   // Try Flask backend first
   let backendResult = null;
   let ctxAtRequest = null;   // set with the other request inputs; read again by the local fallback
+  let fitOp = null;         // unit 2: this tab's fit operation, claimed before the first await
   try {
     const bgType  = document.getElementById('bg-type').value;
     const bgStart = parseFloat(document.getElementById('bg-start').value);
@@ -8154,6 +8183,7 @@ async function runFit(opts = {}) {
     // the live model and its fit context as the student pressed the button: a
     // result must not be written over a model that was edited while it ran
     ctxAtRequest = _startsLiveKey();
+    fitOp = _claimFitOp(fittingTab);   // before the first await: the newest claim for a tab is current
     const fitMethod = document.getElementById('fit-method').value;
     const epAvgVal = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
     const bgPayload = { method: bgType, start_idx: bgWin.i0, end_idx: bgWin.i1 + 1, endpoint_avg: epAvgVal };
@@ -8192,7 +8222,7 @@ async function runFit(opts = {}) {
     // request was. The ownership checks below also run inside the poll loop,
     // so a switched tab or an edited model stops the server's work at once.
     const json = await _serverFitJob(fitReq, {
-      owner: fittingTab,
+      op: fitOp,
       abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
     });
     if (json && json._abandoned === 'superseded') return;   // a newer fit on this tab owns the spinner and the result
@@ -8270,6 +8300,9 @@ async function runFit(opts = {}) {
     _hideFitSpinner();
     notify('Fit complete. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3), 'green');
   } catch (e) {
+    // superseded (a newer fit on this tab): nothing at all — no message, no
+    // local fallback, the newer fit owns the spinner and the result
+    if (fitOp && !_fitOpCurrent(fitOp)) return;
     // Fall back to local Levenberg-Marquardt
     _hideFitSpinner();
     if (!_ownerActive(fittingTab)) {
diff --git a/tests/js/fit_start_poll.test.js b/tests/js/fit_start_poll.test.js
index a4b7045..c98b683 100644
--- a/tests/js/fit_start_poll.test.js
+++ b/tests/js/fit_start_poll.test.js
@@ -42,9 +42,10 @@ const bad = (status, obj) => ({ ok: false, status, json: async () => { if (obj =
 
 function make(fetch) {
   const src = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
-    'const _runningFitJobs = new Set(); const _fitJobByOwner = new WeakMap();',
-    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
-  return new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob, _runningFitJobs };')(
+    'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap();',
+    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_claimFitOp'), extractFn('_fitOpCurrent'),
+    extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
+  return new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob, _runningFitJobs, _claimFitOp };')(
     fetch, f => f(), class extends Error { constructor(m, n) { super(m); this.name = n; } });
 }
 const START = '/api/fit/start';
@@ -142,35 +143,101 @@ test('Run Fit and Auto-Fit both go through _serverFitJob; nothing on the page po
   assert.match(html, /addEventListener\('pagehide'/, 'a closed page cancels its running fits');
 });
 
-test('a new start for the same tab SUPERSEDES the previous job: cancelled on the server, its loop returns quietly (Codex round 1)', async () => {
-  let n = 0;
-  let releaseFirst;
-  const gate = new Promise(r => { releaseFirst = r; });
-  const s = server(u => u === START ? ok({ job_id: 'J' + (++n) }, 202)
-    : isProgress(u) ? ok({ status: 'running', heartbeat_age_sec: 0 }) : ok({}));
-  // a poll loop that yields between polls, so two jobs can interleave
+// Round 2: ownership is an OPERATION claimed before the caller's first await
+// (_claimFitOp); the newest claim for a tab is current whatever order the
+// server's responses arrive in, and a superseded operation returns
+// { _abandoned: 'superseded' } at every step after an await and before every
+// exit (a result, an error, a timeout).
+function makeAsync(fetch) {
   const src = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
-    'const _runningFitJobs = new Set(); const _fitJobByOwner = new WeakMap();',
-    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
-  const { _serverFitJob } = new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob };')(
-    s.fetch, f => { setImmediate(f); return 0; }, class extends Error {});   // yield to the event loop between polls
+    'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap();',
+    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_claimFitOp'), extractFn('_fitOpCurrent'),
+    extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
+  return new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob, _claimFitOp };')(
+    fetch, f => { setImmediate(f); return 0; }, class extends Error {});   // yield to the event loop between polls
+}
+const deferred = () => { let res; const p = new Promise(r => { res = r; }); return { p, res }; };
+
+test('the NEWEST claim is current whatever order the start responses arrive in (Codex round 2)', async () => {
+  const calls = [];
+  const aStart = deferred();
+  let n = 0;
+  const fetch = async (url, init) => {
+    calls.push({ url, method: (init && init.method) || 'GET' });
+    if (url === '/api/fit/start') {
+      const id = 'J' + (++n);
+      if (id === 'J1') await aStart.p;                 // A's start response is delayed
+      return ok({ job_id: id }, 202);
+    }
+    if (url.startsWith('/api/fit/progress/')) return ok({ status: 'done', result: { which: url.split('/').pop() } });
+    return ok({});
+  };
+  const { _serverFitJob, _claimFitOp } = makeAsync(fetch);
   const owner = { id: 'tab-1' };
-  let polls2 = 0;
-  const first = _serverFitJob({}, { owner });
-  await new Promise(r => setImmediate(r)); await new Promise(r => setImmediate(r));
-  const second = _serverFitJob({}, { owner, abandoned: () => (++polls2 > 3 ? 'tab' : null) });
-  assert.deepStrictEqual(await first, { _abandoned: 'superseded' });
-  assert.ok(s.calls.some(c => c.url === '/api/fit/cancel/J1' && c.method === 'POST'), 'the first job is cancelled on the server');
-  assert.deepStrictEqual(await second, { _abandoned: 'tab' }, 'the second runs on, owning the tab');
-  // another tab's job is not touched
-  const other = _serverFitJob({}, { owner: { id: 'tab-2' }, abandoned: () => 'model' });
-  assert.deepStrictEqual(await other, { _abandoned: 'model' });
+  const opA = _claimFitOp(owner);                      // A pressed first
+  const a = _serverFitJob({}, { op: opA });
+  await new Promise(r => setImmediate(r));
+  const opB = _claimFitOp(owner);                      // B pressed second
+  const b = _serverFitJob({}, { op: opB });
+  assert.deepStrictEqual(await b, { which: 'J2' }, 'B, the newer, gets its result');
+  aStart.res();
+  assert.deepStrictEqual(await a, { _abandoned: 'superseded' }, 'A, older, is superseded though its response came last');
+  assert.ok(calls.some(c => c.url === '/api/fit/cancel/J1' && c.method === 'POST'), "A's late job is cancelled by A itself");
+  assert.ok(!calls.some(c => c.url === '/api/fit/cancel/J2'), "B's job is never cancelled");
 });
 
-test('both callers pass their tab as the owner and do nothing at all when superseded', () => {
-  for (const fn of ['runFit', 'runAutoFitC1sGraphite']) {
-    const src = extractFn(fn);
-    assert.match(src, /owner: fittingTab,/, fn);
-    assert.match(src, /if \(json && json\._abandoned === 'superseded'\) return;/, fn);
+test('a poll in flight when a newer claim arrives: its reply is never applied, never an error (Codex round 2)', async () => {
+  for (const late of [{ status: 'done', result: { stale: true } }, { status: 'cancelled' }, { status: 'error', http_status: 500, error: 'x' }]) {
+    const calls = [];
+    const polled = deferred();
+    const release = deferred();
+    const fetch = async (url, init) => {
+      calls.push({ url, method: (init && init.method) || 'GET' });
+      if (url === '/api/fit/start') return ok({ job_id: 'J1' }, 202);
+      if (url.startsWith('/api/fit/progress/')) { polled.res(); await release.p; return ok(late); }
+      return ok({});
+    };
+    const { _serverFitJob, _claimFitOp } = makeAsync(fetch);
+    const owner = { id: 'tab-1' };
+    const a = _serverFitJob({}, { op: _claimFitOp(owner) });
+    await polled.p;                                    // A's poll is in flight
+    _claimFitOp(owner);                                // B claims the tab
+    release.res();                                     // A's late reply arrives
+    assert.deepStrictEqual(await a, { _abandoned: 'superseded' }, late.status);
+    assert.ok(calls.some(c => c.url === '/api/fit/cancel/J1'), late.status + ': the newer claim cancelled A');
   }
 });
+
+test('an Auto-Fit timeout after a newer claim is superseded, not a timeout (Codex round 2)', async () => {
+  const signal = { aborted: false, reason: null };
+  const polled = deferred();
+  const release = deferred();
+  const fetch = async (url) => {
+    if (url === '/api/fit/start') return ok({ job_id: 'J1' }, 202);
+    if (url.startsWith('/api/fit/progress/')) { polled.res(); await release.p; signal.aborted = true;
+      signal.reason = Object.assign(new Error('timeout'), { name: 'AbortError' }); throw signal.reason; }
+    return ok({});
+  };
+  const { _serverFitJob, _claimFitOp } = makeAsync(fetch);
+  const owner = {};
+  const a = _serverFitJob({}, { op: _claimFitOp(owner), signal });
+  await polled.p;
+  _claimFitOp(owner);
+  release.res();
+  assert.deepStrictEqual(await a, { _abandoned: 'superseded' });
+});
+
+test('both callers claim their operation before the first await and do nothing at all when superseded', () => {
+  const run = extractFn('runFit');
+  assert.ok(run.indexOf('fitOp = _claimFitOp(fittingTab);') > 0 && run.indexOf('fitOp = _claimFitOp(fittingTab);') < run.indexOf('await uploadToBackend('), 'runFit claims before its first await');
+  assert.ok(!/\bawait\s+[\w(]/.test(run.slice(0, run.indexOf('fitOp = _claimFitOp(fittingTab);')).replace(/\/\/[^\n]*/g, '')), 'no code await before the claim');
+  assert.match(run, /op: fitOp,/);
+  assert.match(run, /if \(json && json\._abandoned === 'superseded'\) return;/);
+  assert.match(run, /\} catch \(e\) \{\n(\s*\/\/[^\n]*\n)*\s*if \(fitOp && !_fitOpCurrent\(fitOp\)\) return;/, 'runFit: a superseded operation never reaches the local fallback');
+  const af = extractFn('runAutoFitC1sGraphite');
+  const claim = af.indexOf('afOp = _claimFitOp(fittingTab);');
+  assert.ok(claim > 0 && claim < af.indexOf('await uploadToBackend('), 'Auto-Fit claims before its first server await');
+  assert.match(af, /op: afOp,/);
+  assert.match(af, /if \(json && json\._abandoned === 'superseded'\) return;/);
+  assert.match(af, /if \(afOp && !_fitOpCurrent\(afOp\)\) return;/, 'Auto-Fit: no rollback when superseded');
+});
diff --git a/tests/test_fit_start_poll.py b/tests/test_fit_start_poll.py
index 962bbf3..cb33362 100644
--- a/tests/test_fit_start_poll.py
+++ b/tests/test_fit_start_poll.py
@@ -214,3 +214,41 @@ def test_a_cancel_observed_mid_fit_is_a_cancellation_never_a_solver_error(method
     with pytest.raises(fitting.FitCancelled):
         fitting.run_fit(x, y, _specs(SLOW), background_method="linear", n_perturb=0,
                         fit_kws={"method": method}, cancel=cancel)
+
+
+@pytest.mark.parametrize("failing", ["fit-hb-", "fit-"])
+def test_a_thread_that_fails_to_start_returns_its_admission_exactly_once(client, monkeypatch, failing):
+    """Codex round 2: admission has exactly one owner — the route until the
+    worker thread has started, the worker after."""
+    real_start = app_module.threading.Thread.start
+
+    def start(self):
+        name = self.name or ""
+        if name.startswith(failing) and not (failing == "fit-" and name.startswith("fit-hb-")):
+            raise RuntimeError("cannot start thread")
+        return real_start(self)
+
+    import threading as _th
+    # three run slots, so the faulted (fast) worker can RUN and finish while the
+    # held jobs are still outstanding — the double release is then visible
+    monkeypatch.setattr(app_module, "_FIT_JOB_RUN_SLOTS", _th.BoundedSemaphore(3))
+    sid = _upload(client)
+    # a job held OUTSTANDING (the counter is clamped at 0, so a double release
+    # only shows while another admission is live)
+    slow_sid = _upload(client, n=300, comps=SLOW)
+    slow = [client.post("/api/fit/start", json=_body(slow_sid, SLOW, method="basinhopping", n_perturb=0)).get_json()["job_id"]
+            for _ in range(2)]                     # TWO held: one running, one queued
+    before = app_module._FIT_JOB_ADMITTED[0]
+    assert before >= 2
+    monkeypatch.setattr(app_module.threading.Thread, "start", start)
+    with pytest.raises(RuntimeError):
+        client.post("/api/fit/start", json=_body(sid, COMPS))
+    monkeypatch.setattr(app_module.threading.Thread, "start", real_start)
+    time.sleep(3.0)                                # long enough for a started (fast) worker to finish and release
+    assert app_module._FIT_JOB_ADMITTED[0] == before, "released exactly once, by the route"
+    for j in slow:
+        client.post(f"/api/fit/cancel/{j}")
+    for j in slow:
+        _poll(client, j, limit=60)
+    time.sleep(0.3)
+    assert app_module._FIT_JOB_ADMITTED[0] == before - 2, "and the held jobs released their own, once each"

exec
/bin/zsh -lc 'git diff HEAD~1..HEAD -- app.py templates/index.html tests/js/fit_start_poll.test.js tests/test_fit_start_poll.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-YAAj9QeF' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-FMGolwMP' (errno=Operation not permitted)
diff --git a/app.py b/app.py
index 2dd37a5..79c5eb2 100644
--- a/app.py
+++ b/app.py
@@ -712,8 +712,16 @@ def _fit_job_start(job_id: str, upload_folder: str, fit_args: dict, run) -> None
             except OSError:
                 pass
 
-    threading.Thread(target=worker, daemon=True, name=f"fit-{job_id[:8]}").start()
+    # The heartbeat thread starts FIRST: if either thread fails to start this
+    # raises BEFORE the worker runs, and the route returns the admission; once
+    # the worker has started, only the worker's finally returns it (exactly
+    # one owner; Codex round 2).
     threading.Thread(target=heartbeat, daemon=True, name=f"fit-hb-{job_id[:8]}").start()
+    try:
+        threading.Thread(target=worker, daemon=True, name=f"fit-{job_id[:8]}").start()
+    except Exception:
+        finished.set()                # stop the heartbeat of a job that never ran
+        raise
 
 
 def _require_json(f):
diff --git a/templates/index.html b/templates/index.html
index b81fa84..ddbc6d8 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -7467,13 +7467,26 @@ const FIT_POLL_MS = 500;
 const FIT_POLL_TRANSPORT_RETRIES = 5;
 const FIT_HEARTBEAT_LOST_SEC = 30;
 const _runningFitJobs = new Set();
-// The current server fit of each tab record (unit 2, Codex round 1): a new
-// start for the same tab — Ctrl/Cmd+F bypasses the disabled button, and
-// Auto-Fit and Run Fit share a tab — SUPERSEDES the previous job: it is
-// cancelled on the server and its loop returns { _abandoned: 'superseded' },
-// on which the caller does nothing at all (the new fit owns the spinner and
-// the result).
-const _fitJobByOwner = new WeakMap();
+// One fit OPERATION per tab record (unit 2, Codex rounds 1-2). A caller claims
+// its operation BEFORE ITS FIRST AWAIT (_claimFitOp): the newest claim for a
+// tab is the current one, whatever order the server's responses come back in.
+// A claim cancels the previous operation's server job; the previous
+// operation's _serverFitJob, at every step after an await and before every
+// exit — a result, an error, a timeout — sees it is no longer current,
+// cancels its own job if it has one, and returns { _abandoned: 'superseded' },
+// on which its caller does NOTHING (the newer fit owns spinner and result).
+// Ctrl/Cmd+F bypasses the disabled Run Fit button, and Run Fit and Auto-Fit
+// share a tab.
+let _fitOpSeq = 0;
+const _fitOpByOwner = new WeakMap();
+function _claimFitOp(owner) {
+  const prev = owner ? _fitOpByOwner.get(owner) : null;
+  if (prev && prev.jobId) _cancelFitJob(prev.jobId);
+  const op = { seq: ++_fitOpSeq, owner: owner || null, jobId: null };
+  if (owner) _fitOpByOwner.set(owner, op);
+  return op;
+}
+function _fitOpCurrent(op) { return !op || !op.owner || _fitOpByOwner.get(op.owner) === op; }
 function _cancelFitJob(jobId) {
   try { fetch('/api/fit/cancel/' + encodeURIComponent(jobId), { method: 'POST', keepalive: true }).catch(() => {}); } catch (_) { /* best effort */ }
 }
@@ -7492,42 +7505,46 @@ function _fitHttpError(status, msg, prefix) {
 }
 async function _serverFitJob(fitReq, guard) {
   guard = guard || {};
+  const op = guard.op || null;
+  const SUP = { _abandoned: 'superseded' };
+  let jobId = null;
+  const gone = () => !_fitOpCurrent(op);
+  const superseded = () => { if (jobId) _cancelFitJob(jobId); return SUP; };
   const isTransport = e => e && !e.serverError && (e instanceof TypeError || e.name === 'AbortError');
-  let resp;
-  try {
-    resp = await fetch('/api/fit/start', { method: 'POST', headers: { 'Content-Type': 'application/json' },
-                                           body: JSON.stringify(fitReq), signal: guard.signal });
-  } catch (e) { if (isTransport(e)) e.transportFailure = true; throw e; }
-  if (resp.ok === false) {
-    let msg = null;
-    try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
-    throw _fitHttpError(resp.status, msg);
-  }
-  let started;
-  try { started = await _readFitReply(resp); } catch (e) { if (isTransport(e)) e.transportFailure = true; throw e; }
-  const jobId = started && started.job_id;
-  if (!jobId) throw _fitHttpError(resp.status, 'The server did not start the fit (no job id).');
-  _runningFitJobs.add(jobId);
-  if (guard.owner) {
-    const prev = _fitJobByOwner.get(guard.owner);
-    if (prev && prev !== jobId) _cancelFitJob(prev);
-    _fitJobByOwner.set(guard.owner, jobId);
-  }
-  let misses = 0;
   try {
+    if (gone()) return SUP;
+    let resp;
+    try {
+      resp = await fetch('/api/fit/start', { method: 'POST', headers: { 'Content-Type': 'application/json' },
+                                             body: JSON.stringify(fitReq), signal: guard.signal });
+    } catch (e) { if (isTransport(e)) e.transportFailure = true; throw e; }
+    if (resp.ok === false) {
+      let msg = null;
+      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
+      throw _fitHttpError(resp.status, msg);
+    }
+    let started;
+    try { started = await _readFitReply(resp); } catch (e) { if (isTransport(e)) e.transportFailure = true; throw e; }
+    jobId = started && started.job_id;
+    if (!jobId) throw _fitHttpError(resp.status, 'The server did not start the fit (no job id).');
+    _runningFitJobs.add(jobId);
+    if (gone()) return superseded();            // a newer claim came while this start was in flight
+    if (op) op.jobId = jobId;
+    let misses = 0;
     while (true) {
       await new Promise(r => setTimeout(r, FIT_POLL_MS));
+      if (gone()) return superseded();
       if (guard.signal && guard.signal.aborted) {
         _cancelFitJob(jobId);
         throw guard.signal.reason || new DOMException('aborted', 'AbortError');
       }
-      if (guard.owner && _fitJobByOwner.get(guard.owner) !== jobId) return { _abandoned: 'superseded' };   // its successor cancelled it
       const why = guard.abandoned ? guard.abandoned() : null;
       if (why) { _cancelFitJob(jobId); return { _abandoned: why }; }
       let pr, rec;
       try {
         pr = await fetch('/api/fit/progress/' + encodeURIComponent(jobId), { signal: guard.signal });
       } catch (e) {
+        if (gone()) return superseded();
         if (e && e.name === 'AbortError') { _cancelFitJob(jobId); throw e; }
         if (++misses >= FIT_POLL_TRANSPORT_RETRIES) {
           _cancelFitJob(jobId);
@@ -7537,6 +7554,7 @@ async function _serverFitJob(fitReq, guard) {
         }
         continue;
       }
+      if (gone()) return superseded();            // the reply of a poll made before a newer claim
       if (pr.ok === false) {
         _cancelFitJob(jobId);
         let msg = null;
@@ -7544,6 +7562,7 @@ async function _serverFitJob(fitReq, guard) {
         throw _fitHttpError(pr.status, msg, 'Lost the fit\'s progress');
       }
       try { rec = await _readFitReply(pr); } catch (e) {
+        if (gone()) return superseded();
         if (e && e.unreadableReply) { _cancelFitJob(jobId); throw e; }
         if (++misses >= FIT_POLL_TRANSPORT_RETRIES) {
           _cancelFitJob(jobId);
@@ -7552,6 +7571,7 @@ async function _serverFitJob(fitReq, guard) {
         }
         continue;
       }
+      if (gone()) return superseded();
       misses = 0;
       if (rec.status === 'done') return rec.result;
       if (rec.status === 'error') throw _fitHttpError(rec.http_status || 500, rec.error);
@@ -7563,9 +7583,12 @@ async function _serverFitJob(fitReq, guard) {
       }
       if (typeof guard.onProgress === 'function') guard.onProgress(rec);
     }
+  } catch (e) {
+    if (gone()) return superseded();              // superseded wins over any error, incl. a timeout
+    throw e;
   } finally {
-    _runningFitJobs.delete(jobId);
-    if (guard.owner && _fitJobByOwner.get(guard.owner) === jobId) _fitJobByOwner.delete(guard.owner);
+    if (jobId) _runningFitJobs.delete(jobId);
+    if (op && op.jobId === jobId) op.jobId = null;
   }
 }
 
@@ -7645,6 +7668,7 @@ async function runAutoFitC1sGraphite() {
   if (runBtn) runBtn.disabled = true;
 
   const ctrl = new AbortController();
+  let afOp = null;   // unit 2: this tab's fit operation (claimed below, before the first server await)
   const timer = setTimeout(() => ctrl.abort(new DOMException('timeout', 'AbortError')), 120000);
 
   try {
@@ -7665,6 +7689,7 @@ async function runAutoFitC1sGraphite() {
     // the model and its fit context as sent (F1, Codex round 1): a result must
     // not be applied, and stamped current, over a model edited while it ran
     const ctxAtRequest = _startsLiveKey();
+    afOp = _claimFitOp(fittingTab);   // unit 2: before the first server await; the newest claim for a tab is current
     // Build peak specs and overlay the per-peak bounds we attached in buildAutoFitModel.
     const peakSpecs = state.peaks.map(p => {
       const spec = peakToBackendSpec(p);
@@ -7695,7 +7720,7 @@ async function runAutoFitC1sGraphite() {
         // reference of a whole spectrum (see applyAutoFitResult).
         require_component: anchorId,
     }, {
-      owner: fittingTab,
+      op: afOp,
       signal: ctrl.signal,
       abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
     });
@@ -7747,6 +7772,9 @@ async function runAutoFitC1sGraphite() {
     notify('Auto-fit complete. χ²ᵣ = ' + (state.fitResult?.chiReduced?.toFixed(3) || '?'), 'green');
   } catch (e) {
     clearTimeout(timer);
+    // superseded (Run Fit pressed during Auto-Fit): nothing at all — no
+    // rollback (it would overwrite the newer fit's model), no message
+    if (afOp && !_fitOpCurrent(afOp)) return;
     _hideFitSpinner();
     // The catch path can also fire after a mid-flight tab switch (fetch
     // error/timeout after the user moved on) — same wrong-tab hazard as
@@ -8134,6 +8162,7 @@ async function runFit(opts = {}) {
   // Try Flask backend first
   let backendResult = null;
   let ctxAtRequest = null;   // set with the other request inputs; read again by the local fallback
+  let fitOp = null;         // unit 2: this tab's fit operation, claimed before the first await
   try {
     const bgType  = document.getElementById('bg-type').value;
     const bgStart = parseFloat(document.getElementById('bg-start').value);
@@ -8154,6 +8183,7 @@ async function runFit(opts = {}) {
     // the live model and its fit context as the student pressed the button: a
     // result must not be written over a model that was edited while it ran
     ctxAtRequest = _startsLiveKey();
+    fitOp = _claimFitOp(fittingTab);   // before the first await: the newest claim for a tab is current
     const fitMethod = document.getElementById('fit-method').value;
     const epAvgVal = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
     const bgPayload = { method: bgType, start_idx: bgWin.i0, end_idx: bgWin.i1 + 1, endpoint_avg: epAvgVal };
@@ -8192,7 +8222,7 @@ async function runFit(opts = {}) {
     // request was. The ownership checks below also run inside the poll loop,
     // so a switched tab or an edited model stops the server's work at once.
     const json = await _serverFitJob(fitReq, {
-      owner: fittingTab,
+      op: fitOp,
       abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
     });
     if (json && json._abandoned === 'superseded') return;   // a newer fit on this tab owns the spinner and the result
@@ -8270,6 +8300,9 @@ async function runFit(opts = {}) {
     _hideFitSpinner();
     notify('Fit complete. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3), 'green');
   } catch (e) {
+    // superseded (a newer fit on this tab): nothing at all — no message, no
+    // local fallback, the newer fit owns the spinner and the result
+    if (fitOp && !_fitOpCurrent(fitOp)) return;
     // Fall back to local Levenberg-Marquardt
     _hideFitSpinner();
     if (!_ownerActive(fittingTab)) {
diff --git a/tests/js/fit_start_poll.test.js b/tests/js/fit_start_poll.test.js
index a4b7045..c98b683 100644
--- a/tests/js/fit_start_poll.test.js
+++ b/tests/js/fit_start_poll.test.js
@@ -42,9 +42,10 @@ const bad = (status, obj) => ({ ok: false, status, json: async () => { if (obj =
 
 function make(fetch) {
   const src = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
-    'const _runningFitJobs = new Set(); const _fitJobByOwner = new WeakMap();',
-    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
-  return new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob, _runningFitJobs };')(
+    'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap();',
+    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_claimFitOp'), extractFn('_fitOpCurrent'),
+    extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
+  return new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob, _runningFitJobs, _claimFitOp };')(
     fetch, f => f(), class extends Error { constructor(m, n) { super(m); this.name = n; } });
 }
 const START = '/api/fit/start';
@@ -142,35 +143,101 @@ test('Run Fit and Auto-Fit both go through _serverFitJob; nothing on the page po
   assert.match(html, /addEventListener\('pagehide'/, 'a closed page cancels its running fits');
 });
 
-test('a new start for the same tab SUPERSEDES the previous job: cancelled on the server, its loop returns quietly (Codex round 1)', async () => {
-  let n = 0;
-  let releaseFirst;
-  const gate = new Promise(r => { releaseFirst = r; });
-  const s = server(u => u === START ? ok({ job_id: 'J' + (++n) }, 202)
-    : isProgress(u) ? ok({ status: 'running', heartbeat_age_sec: 0 }) : ok({}));
-  // a poll loop that yields between polls, so two jobs can interleave
+// Round 2: ownership is an OPERATION claimed before the caller's first await
+// (_claimFitOp); the newest claim for a tab is current whatever order the
+// server's responses arrive in, and a superseded operation returns
+// { _abandoned: 'superseded' } at every step after an await and before every
+// exit (a result, an error, a timeout).
+function makeAsync(fetch) {
   const src = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
-    'const _runningFitJobs = new Set(); const _fitJobByOwner = new WeakMap();',
-    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
-  const { _serverFitJob } = new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob };')(
-    s.fetch, f => { setImmediate(f); return 0; }, class extends Error {});   // yield to the event loop between polls
+    'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap();',
+    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_claimFitOp'), extractFn('_fitOpCurrent'),
+    extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
+  return new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob, _claimFitOp };')(
+    fetch, f => { setImmediate(f); return 0; }, class extends Error {});   // yield to the event loop between polls
+}
+const deferred = () => { let res; const p = new Promise(r => { res = r; }); return { p, res }; };
+
+test('the NEWEST claim is current whatever order the start responses arrive in (Codex round 2)', async () => {
+  const calls = [];
+  const aStart = deferred();
+  let n = 0;
+  const fetch = async (url, init) => {
+    calls.push({ url, method: (init && init.method) || 'GET' });
+    if (url === '/api/fit/start') {
+      const id = 'J' + (++n);
+      if (id === 'J1') await aStart.p;                 // A's start response is delayed
+      return ok({ job_id: id }, 202);
+    }
+    if (url.startsWith('/api/fit/progress/')) return ok({ status: 'done', result: { which: url.split('/').pop() } });
+    return ok({});
+  };
+  const { _serverFitJob, _claimFitOp } = makeAsync(fetch);
   const owner = { id: 'tab-1' };
-  let polls2 = 0;
-  const first = _serverFitJob({}, { owner });
-  await new Promise(r => setImmediate(r)); await new Promise(r => setImmediate(r));
-  const second = _serverFitJob({}, { owner, abandoned: () => (++polls2 > 3 ? 'tab' : null) });
-  assert.deepStrictEqual(await first, { _abandoned: 'superseded' });
-  assert.ok(s.calls.some(c => c.url === '/api/fit/cancel/J1' && c.method === 'POST'), 'the first job is cancelled on the server');
-  assert.deepStrictEqual(await second, { _abandoned: 'tab' }, 'the second runs on, owning the tab');
-  // another tab's job is not touched
-  const other = _serverFitJob({}, { owner: { id: 'tab-2' }, abandoned: () => 'model' });
-  assert.deepStrictEqual(await other, { _abandoned: 'model' });
+  const opA = _claimFitOp(owner);                      // A pressed first
+  const a = _serverFitJob({}, { op: opA });
+  await new Promise(r => setImmediate(r));
+  const opB = _claimFitOp(owner);                      // B pressed second
+  const b = _serverFitJob({}, { op: opB });
+  assert.deepStrictEqual(await b, { which: 'J2' }, 'B, the newer, gets its result');
+  aStart.res();
+  assert.deepStrictEqual(await a, { _abandoned: 'superseded' }, 'A, older, is superseded though its response came last');
+  assert.ok(calls.some(c => c.url === '/api/fit/cancel/J1' && c.method === 'POST'), "A's late job is cancelled by A itself");
+  assert.ok(!calls.some(c => c.url === '/api/fit/cancel/J2'), "B's job is never cancelled");
 });
 
-test('both callers pass their tab as the owner and do nothing at all when superseded', () => {
-  for (const fn of ['runFit', 'runAutoFitC1sGraphite']) {
-    const src = extractFn(fn);
-    assert.match(src, /owner: fittingTab,/, fn);
-    assert.match(src, /if \(json && json\._abandoned === 'superseded'\) return;/, fn);
+test('a poll in flight when a newer claim arrives: its reply is never applied, never an error (Codex round 2)', async () => {
+  for (const late of [{ status: 'done', result: { stale: true } }, { status: 'cancelled' }, { status: 'error', http_status: 500, error: 'x' }]) {
+    const calls = [];
+    const polled = deferred();
+    const release = deferred();
+    const fetch = async (url, init) => {
+      calls.push({ url, method: (init && init.method) || 'GET' });
+      if (url === '/api/fit/start') return ok({ job_id: 'J1' }, 202);
+      if (url.startsWith('/api/fit/progress/')) { polled.res(); await release.p; return ok(late); }
+      return ok({});
+    };
+    const { _serverFitJob, _claimFitOp } = makeAsync(fetch);
+    const owner = { id: 'tab-1' };
+    const a = _serverFitJob({}, { op: _claimFitOp(owner) });
+    await polled.p;                                    // A's poll is in flight
+    _claimFitOp(owner);                                // B claims the tab
+    release.res();                                     // A's late reply arrives
+    assert.deepStrictEqual(await a, { _abandoned: 'superseded' }, late.status);
+    assert.ok(calls.some(c => c.url === '/api/fit/cancel/J1'), late.status + ': the newer claim cancelled A');
   }
 });
+
+test('an Auto-Fit timeout after a newer claim is superseded, not a timeout (Codex round 2)', async () => {
+  const signal = { aborted: false, reason: null };
+  const polled = deferred();
+  const release = deferred();
+  const fetch = async (url) => {
+    if (url === '/api/fit/start') return ok({ job_id: 'J1' }, 202);
+    if (url.startsWith('/api/fit/progress/')) { polled.res(); await release.p; signal.aborted = true;
+      signal.reason = Object.assign(new Error('timeout'), { name: 'AbortError' }); throw signal.reason; }
+    return ok({});
+  };
+  const { _serverFitJob, _claimFitOp } = makeAsync(fetch);
+  const owner = {};
+  const a = _serverFitJob({}, { op: _claimFitOp(owner), signal });
+  await polled.p;
+  _claimFitOp(owner);
+  release.res();
+  assert.deepStrictEqual(await a, { _abandoned: 'superseded' });
+});
+
+test('both callers claim their operation before the first await and do nothing at all when superseded', () => {
+  const run = extractFn('runFit');
+  assert.ok(run.indexOf('fitOp = _claimFitOp(fittingTab);') > 0 && run.indexOf('fitOp = _claimFitOp(fittingTab);') < run.indexOf('await uploadToBackend('), 'runFit claims before its first await');
+  assert.ok(!/\bawait\s+[\w(]/.test(run.slice(0, run.indexOf('fitOp = _claimFitOp(fittingTab);')).replace(/\/\/[^\n]*/g, '')), 'no code await before the claim');
+  assert.match(run, /op: fitOp,/);
+  assert.match(run, /if \(json && json\._abandoned === 'superseded'\) return;/);
+  assert.match(run, /\} catch \(e\) \{\n(\s*\/\/[^\n]*\n)*\s*if \(fitOp && !_fitOpCurrent\(fitOp\)\) return;/, 'runFit: a superseded operation never reaches the local fallback');
+  const af = extractFn('runAutoFitC1sGraphite');
+  const claim = af.indexOf('afOp = _claimFitOp(fittingTab);');
+  assert.ok(claim > 0 && claim < af.indexOf('await uploadToBackend('), 'Auto-Fit claims before its first server await');
+  assert.match(af, /op: afOp,/);
+  assert.match(af, /if \(json && json\._abandoned === 'superseded'\) return;/);
+  assert.match(af, /if \(afOp && !_fitOpCurrent\(afOp\)\) return;/, 'Auto-Fit: no rollback when superseded');
+});
diff --git a/tests/test_fit_start_poll.py b/tests/test_fit_start_poll.py
index 962bbf3..cb33362 100644
--- a/tests/test_fit_start_poll.py
+++ b/tests/test_fit_start_poll.py
@@ -214,3 +214,41 @@ def test_a_cancel_observed_mid_fit_is_a_cancellation_never_a_solver_error(method
     with pytest.raises(fitting.FitCancelled):
         fitting.run_fit(x, y, _specs(SLOW), background_method="linear", n_perturb=0,
                         fit_kws={"method": method}, cancel=cancel)
+
+
+@pytest.mark.parametrize("failing", ["fit-hb-", "fit-"])
+def test_a_thread_that_fails_to_start_returns_its_admission_exactly_once(client, monkeypatch, failing):
+    """Codex round 2: admission has exactly one owner — the route until the
+    worker thread has started, the worker after."""
+    real_start = app_module.threading.Thread.start
+
+    def start(self):
+        name = self.name or ""
+        if name.startswith(failing) and not (failing == "fit-" and name.startswith("fit-hb-")):
+            raise RuntimeError("cannot start thread")
+        return real_start(self)
+
+    import threading as _th
+    # three run slots, so the faulted (fast) worker can RUN and finish while the
+    # held jobs are still outstanding — the double release is then visible
+    monkeypatch.setattr(app_module, "_FIT_JOB_RUN_SLOTS", _th.BoundedSemaphore(3))
+    sid = _upload(client)
+    # a job held OUTSTANDING (the counter is clamped at 0, so a double release
+    # only shows while another admission is live)
+    slow_sid = _upload(client, n=300, comps=SLOW)
+    slow = [client.post("/api/fit/start", json=_body(slow_sid, SLOW, method="basinhopping", n_perturb=0)).get_json()["job_id"]
+            for _ in range(2)]                     # TWO held: one running, one queued
+    before = app_module._FIT_JOB_ADMITTED[0]
+    assert before >= 2
+    monkeypatch.setattr(app_module.threading.Thread, "start", start)
+    with pytest.raises(RuntimeError):
+        client.post("/api/fit/start", json=_body(sid, COMPS))
+    monkeypatch.setattr(app_module.threading.Thread, "start", real_start)
+    time.sleep(3.0)                                # long enough for a started (fast) worker to finish and release
+    assert app_module._FIT_JOB_ADMITTED[0] == before, "released exactly once, by the route"
+    for j in slow:
+        client.post(f"/api/fit/cancel/{j}")
+    for j in slow:
+        _poll(client, j, limit=60)
+    time.sleep(0.3)
+    assert app_module._FIT_JOB_ADMITTED[0] == before - 2, "and the held jobs released their own, once each"

exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '7595,7805p'; nl -ba templates/index.html | sed -n '8120,8390p'; nl -ba app.py | sed -n '540,735p'; nl -ba app.py | sed -n '1250,1335p'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
  7595	async function runAutoFitC1sGraphite() {
  7596	  // Pre-conditions
  7597	  if (!state.rawBE || !state.rawBE.length) { notify('Load a spectrum first.', 'amber'); return; }
  7598	  const tab = tabManager._getTab(tabManager.activeId);
  7599	  if (!tab) { notify('No active tab.', 'amber'); return; }
  7600	  if (!isC1sTab(tab)) {
  7601	    notify('Auto-Fit C1s Graphite is only available for C1s spectra (ROI midpoint 270–315 eV).', 'amber');
  7602	    return;
  7603	  }
  7604	  // OWNER FIRST: the confirmation below is an await; the tab that is active
  7605	  // when it resolves may not be the one the user asked to auto-fit.
  7606	  const fittingTab = _opOwner();
  7607	  if (!fittingTab) { notify('No active spectrum tab.', 'amber'); return; }
  7608	  // Confirmation if existing peaks
  7609	  if (state.peaks.length >= 1) {
  7610	    const proceed = await _showAutoFitConfirmModal(state.peaks.length);
  7611	    if (!proceed) return;
  7612	    if (!_ownerActive(fittingTab)) {
  7613	      notify('Auto-fit cancelled — the tab changed while the confirmation was open.', 'amber');
  7614	      return;
  7615	    }
  7616	  }
  7617	
  7618	  // Snapshot for failure rollback (separate from pushUndo, which only covers peaks).
  7619	  const snap = _autoFitSnapshot();
  7620	
  7621	  // Step 1: find graphite in raw BE
  7622	  const { be: corrBE, inten } = getROIData();
  7623	  if (!corrBE.length) {
  7624	    notify('ROI is empty. Set roi-min and roi-max before auto-fit.', 'red', true);
  7625	    return;
  7626	  }
  7627	  const bgI = computeBackground(corrBE, inten);
  7628	  const bgSub = inten.map((v, i) => v - bgI[i]);
  7629	  // App convention: raw = corrected + state.ccShift
  7630	  const curShift = Number.isFinite(state.ccShift) ? state.ccShift : 0;
  7631	  const rawBE = corrBE.map(b => b + curShift);
  7632	  const graphiteRaw = findGraphiteRawBE(rawBE, bgSub);
  7633	  if (graphiteRaw == null) {
  7634	    notify('No strong peak found in the C1s ROI; Auto-Fit cannot proceed.', 'red', true);
  7635	    return;
  7636	  }
  7637	
  7638	  // Step 2: provisional shift (APP CONVENTION).
  7639	  const provisionalShift = graphiteRaw - 284.50;
  7640	
  7641	  // Step 3: assess low-BE region using provisional shift (no state mutation yet).
  7642	  const assessment = assessLowBERegion(rawBE, bgSub, provisionalShift);
  7643	
  7644	  // Step 4: build the peak model (in corrected frame after provisional shift).
  7645	  pushUndo();
  7646	  state.peaks = [];
  7647	  state.fitResult = null;
  7648	  // Apply provisional shift via updateChargeCorrection so ROI/bg DOM fields
  7649	  // shift along with state.ccShift.
  7650	  const cm = document.getElementById('cc-method');
  7651	  const co = document.getElementById('cc-obs');
  7652	  const cl = document.getElementById('cc-lit');
  7653	  cm.value = 'c1s';
  7654	  co.value = graphiteRaw.toFixed(3);
  7655	  cl.value = '284.50';
  7656	  updateChargeCorrection();
  7657	  // Now build the peak list (graphite center 284.50 in this frame).
  7658	  const newPeaks = buildAutoFitModel(assessment);
  7659	  state.peaks = newPeaks;
  7660	  state.nextId = Math.max(0, ...state.peaks.map(p => p.id)) + 1;
  7661	  renderPeakList();
  7662	
  7663	  // Step 5: run /api/fit with AbortController + spinner.
  7664	  _showFitSpinner();
  7665	  const spinLabel = document.getElementById('fit-spinner-label');
  7666	  if (spinLabel) spinLabel.textContent = 'Auto-fitting…';
  7667	  const runBtn = document.querySelector('.btn-green');
  7668	  if (runBtn) runBtn.disabled = true;
  7669	
  7670	  const ctrl = new AbortController();
  7671	  let afOp = null;   // unit 2: this tab's fit operation (claimed below, before the first server await)
  7672	  const timer = setTimeout(() => ctrl.abort(new DOMException('timeout', 'AbortError')), 120000);
  7673	
  7674	  try {
  7675	    const { be: be2, inten: inten2 } = getROIData();
  7676	    const bgType = document.getElementById('bg-type').value;
  7677	    const bgStart = parseFloat(document.getElementById('bg-start').value);
  7678	    const bgEnd = parseFloat(document.getElementById('bg-end').value);
  7679	    // Inclusive bg window — the same point set computeBackgroundCore draws;
  7680	    // the backend slices end-exclusive, so the request sends i1 + 1.
  7681	    const bgWin = _bgWindowIndices(be2, bgStart, bgEnd);
  7682	    const epAvg = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
  7683	    const fitMethod = document.getElementById('fit-method').value;
  7684	
  7685	    // The anchor whose necessity the server must test — captured with the
  7686	    // other request inputs, before the first await (a tab switch during the
  7687	    // upload must not send another tab's id).
  7688	    const anchorId = String((state.peaks.find(p => p.name === 'Graphite') || state.peaks[0]).id);
  7689	    // the model and its fit context as sent (F1, Codex round 1): a result must
  7690	    // not be applied, and stamped current, over a model edited while it ran
  7691	    const ctxAtRequest = _startsLiveKey();
  7692	    afOp = _claimFitOp(fittingTab);   // unit 2: before the first server await; the newest claim for a tab is current
  7693	    // Build peak specs and overlay the per-peak bounds we attached in buildAutoFitModel.
  7694	    const peakSpecs = state.peaks.map(p => {
  7695	      const spec = peakToBackendSpec(p);
  7696	      if (Number.isFinite(p._afCenterMin)) spec.center_min = p._afCenterMin;
  7697	      if (Number.isFinite(p._afCenterMax)) spec.center_max = p._afCenterMax;
  7698	      if (Number.isFinite(p._afFwhmMin))   spec.fwhm_min   = p._afFwhmMin;
  7699	      if (Number.isFinite(p._afFwhmMax))   spec.fwhm_max   = p._afFwhmMax;
  7700	      spec.amplitude_min = 0;
  7701	      return spec;
  7702	    });
  7703	
  7704	    const bgPayload = { method: bgType, start_idx: bgWin.i0, end_idx: bgWin.i1 + 1, endpoint_avg: epAvg };
  7705	    if (bgType === 'manual') {
  7706	      // Anchors are stored in corrected-BE space, same frame as the uploaded
  7707	      // session data; backend expects [x, y] pairs.
  7708	      bgPayload.manual_bg = _getManualAnchors().map(a => [a.x, a.y]);
  7709	    }
  7710	    const sessionId = await uploadToBackend(be2, inten2);   // after EVERY input above is captured
  7711	    // Unit 2: started and polled, like Run Fit (the 2-minute abort still applies)
  7712	    const json = await _serverFitJob({
  7713	        session_id: sessionId,
  7714	        background: bgPayload,
  7715	        peaks: peakSpecs,
  7716	        fit_method: fitMethod,
  7717	        n_perturb: 3,
  7718	        // step (c): is the charge-reference anchor REQUIRED? The server refits
  7719	        // the model without it; a redundant anchor must not set the energy
  7720	        // reference of a whole spectrum (see applyAutoFitResult).
  7721	        require_component: anchorId,
  7722	    }, {
  7723	      op: afOp,
  7724	      signal: ctrl.signal,
  7725	      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
  7726	    });
  7727	    clearTimeout(timer);
  7728	    // superseded by a newer fit on this tab (Run Fit pressed during Auto-Fit):
  7729	    // that fit started from the model now on the tab and owns the result — no
  7730	    // rollback here, which would overwrite it
  7731	    if (json && json._abandoned === 'superseded') return;
  7732	    // F2: a non-2xx reply is a failed REQUEST with its status in the message
  7733	    // (_serverFitJob throws it with httpStatus); an unreadable reply is a
  7734	    // failed fit with its own message (unreadableReply).
  7735	    if (json && json._abandoned === 'tab') {
  7736	      _hideFitSpinner();
  7737	      notify('Auto-fit discarded — tab switched during fit.', 'amber');
  7738	      _autoFitRestore(snap, fittingTab);
  7739	      return;
  7740	    }
  7741	    if (json && json._abandoned === 'model') {
  7742	      _hideFitSpinner();
  7743	      notify('Auto-fit discarded because the model or its background / ROI settings were edited while it was running. Previous peaks and result restored. Run it again.', 'amber', true);
  7744	      _autoFitRestore(snap, fittingTab);
  7745	      return;
  7746	    }
  7747	    if (json.error) throw new Error(json.error);
  7748	    if (json.success !== true) throw new Error(json.message || 'fit did not converge');
  7749	    if (!_ownerActive(fittingTab)) {
  7750	      _hideFitSpinner();
  7751	      notify('Auto-fit discarded — tab switched during fit.', 'amber');
  7752	      _autoFitRestore(snap, fittingTab);
  7753	      return;
  7754	    }
  7755	    if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
  7756	      _hideFitSpinner();
  7757	      notify('Auto-fit discarded because the model or its background / ROI settings were edited while it was running. Previous peaks and result restored. Run it again.', 'amber', true);
  7758	      _autoFitRestore(snap, fittingTab);
  7759	      return;
  7760	    }
  7761	
  7762	    applyBackendResult(json);
  7763	
  7764	    const ok = applyAutoFitResult(json, graphiteRaw, { be: be2, inten: inten2, bgIntensity: bgI, bgSubtracted: bgSub });
  7765	    if (!ok) {
  7766	      _hideFitSpinner();
  7767	      _autoFitRestore(snap, fittingTab);
  7768	      return;
  7769	    }
  7770	
  7771	    _hideFitSpinner();
  7772	    notify('Auto-fit complete. χ²ᵣ = ' + (state.fitResult?.chiReduced?.toFixed(3) || '?'), 'green');
  7773	  } catch (e) {
  7774	    clearTimeout(timer);
  7775	    // superseded (Run Fit pressed during Auto-Fit): nothing at all — no
  7776	    // rollback (it would overwrite the newer fit's model), no message
  7777	    if (afOp && !_fitOpCurrent(afOp)) return;
  7778	    _hideFitSpinner();
  7779	    // The catch path can also fire after a mid-flight tab switch (fetch
  7780	    // error/timeout after the user moved on) — same wrong-tab hazard as
  7781	    // the explicit discard branch, so it gets the same tab-aware restore.
  7782	    _autoFitRestore(snap, fittingTab);
  7783	    let msg;
  7784	    if (e && (e.name === 'AbortError' || (e.message && e.message.toLowerCase().includes('aborted')))) {
  7785	      msg = 'Auto-fit exceeded the 2-minute timeout.';
  7786	    } else if (e && (e.unreadableReply || e.httpStatus)) {
  7787	      msg = 'Auto-fit failed: ' + e.message;
  7788	    } else if (e && e.message) {
  7789	      msg = 'Fit failed to converge or produced an unphysical graphite position.';
  7790	      console.warn('Auto-fit error:', e);
  7791	    } else {
  7792	      msg = 'Auto-fit failed.';
  7793	    }
  7794	    notify(msg, 'red', true);
  7795	  }
  7796	}
  7797	
  7798	function isC1sTab(tab) {
  7799	  if (!tab || !tab.rawBE || !tab.rawBE.length) return false;
  7800	  const ui = tab.ui || {};
  7801	  let lo = parseFloat(ui.roiMin);
  7802	  let hi = parseFloat(ui.roiMax);
  7803	  if (!Number.isFinite(lo) || !Number.isFinite(hi)) {
  7804	    // Fall back to full raw range (no UI ROI set yet)
  7805	    let rmin = Infinity, rmax = -Infinity;
  8120	// Adopting an alternative is the student's decision: explicit, undoable, and
  8121	// recorded. It is ATOMIC by construction: the alternative is only the START of
  8122	// an ordinary server fit (runFit's opts.startPeaks); the live model is written
  8123	// by that fit's success path and by nothing else, so a fit that fails, does
  8124	// not converge, is discarded because the tab changed, or cannot reach the
  8125	// server leaves peaks and result exactly as they were (no local fallback
  8126	// here: the local engine would start from the live model, not from the
  8127	// alternative). runFit's own pushUndo is the single undo entry. A solution
  8128	// that moves a component more than 1 eV from where the student put it is the
  8129	// measured trap (a lower chi-square bought by a chemically absurd relocation),
  8130	// so that case — and only that case — asks first, naming the component and
  8131	// the distance.
  8132	async function useAlternative(k) {
  8133	  const alt = _currentAlternative(k);
  8134	  const peaks = alt && _altPeaks(alt);
  8135	  if (!peaks) { notify(_STARTS_STALE_MSG, 'amber', true); return; }
  8136	  const shift = alt.largest_centre_shift_from_start;
  8137	  const name = _startsPeakName(shift.id);
  8138	  if (Math.abs(shift.ev) > _STARTS_SHIFT_RED_EV &&
  8139	      !confirm(`This solution moves ${name} by ${_startsEv(shift.ev)} from where you placed it. Apply?`)) return;
  8140	  const chosen = { fromChi: state.fitResult.starts.fit.chi2r, toChi: alt.chi2r, shiftName: name, shiftEv: shift.ev };
  8141	  if (_historyPreview) _historyClearPreview();
  8142	  await runFit({ startPeaks: peaks, chosenAlternative: chosen });
  8143	}
  8144	
  8145	async function runFit(opts = {}) {
  8146	  if (!state.rawBE.length) { notify('Load a spectrum first.', 'red', true); return; }
  8147	  if (!state.peaks.length) { notify('Add at least one peak.', 'red'); return; }
  8148	  pushUndo();
  8149	
  8150	  _showFitSpinner();
  8151	  document.getElementById('sb-msg').textContent = 'Fitting\u2026';
  8152	
  8153	  // Capture the tab that owns this fit so that if the user switches tabs
  8154	  // mid-request, we can discard the stale result instead of corrupting the
  8155	  // now-active tab's state.
  8156	  const fittingTab = _opOwner();
  8157	
  8158	  const { be, inten } = getROIData();
  8159	  const bgIntensity = computeBackground(be, inten);
  8160	  const bgSubtracted = inten.map((v, i) => v - bgIntensity[i]);
  8161	
  8162	  // Try Flask backend first
  8163	  let backendResult = null;
  8164	  let ctxAtRequest = null;   // set with the other request inputs; read again by the local fallback
  8165	  let fitOp = null;         // unit 2: this tab's fit operation, claimed before the first await
  8166	  try {
  8167	    const bgType  = document.getElementById('bg-type').value;
  8168	    const bgStart = parseFloat(document.getElementById('bg-start').value);
  8169	    const bgEnd   = parseFloat(document.getElementById('bg-end').value);
  8170	    // Inclusive bg window — the same point set computeBackgroundCore draws;
  8171	    // the backend slices end-exclusive, so the request sends i1 + 1.
  8172	    const bgWin = _bgWindowIndices(be, bgStart, bgEnd);
  8173	    // EVERY request input is read from the owner before the upload await:
  8174	    // peaks, method, endpoint averaging and manual anchors (Codex round 2: a
  8175	    // request could carry A's spectrum with B's averaging and anchors).
  8176	    // opts.startPeaks: the request starts from an adopted alternative; the live
  8177	    // model is still the student's until this fit succeeds (useAlternative).
  8178	    const startModel = opts.startPeaks || state.peaks;
  8179	    const peakSpecs = startModel.map(peakToBackendSpec);
  8180	    // scattered-starts check: decided HERE, with the other request inputs,
  8181	    // before the first await (a tab switch during the upload must not turn it off)
  8182	    const nStarts = _startsUnlinkedCount(startModel) >= 2 ? _STARTS_N : 0;
  8183	    // the live model and its fit context as the student pressed the button: a
  8184	    // result must not be written over a model that was edited while it ran
  8185	    ctxAtRequest = _startsLiveKey();
  8186	    fitOp = _claimFitOp(fittingTab);   // before the first await: the newest claim for a tab is current
  8187	    const fitMethod = document.getElementById('fit-method').value;
  8188	    const epAvgVal = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
  8189	    const bgPayload = { method: bgType, start_idx: bgWin.i0, end_idx: bgWin.i1 + 1, endpoint_avg: epAvgVal };
  8190	    if (bgType === 'manual') {
  8191	      // Anchors are stored in corrected-BE space, same frame as the uploaded
  8192	      // session data; backend expects [x, y] pairs.
  8193	      bgPayload.manual_bg = _getManualAnchors().map(a => [a.x, a.y]);
  8194	    }
  8195	    // Transport failures (server unreachable, timeout, non-JSON reply) are
  8196	    // the ONLY reason to fall back to the local optimiser. A server-side
  8197	    // validation error or a non-converged optimisation surfaces its message
  8198	    // and leaves the model untouched (unit A0: nothing is shown as a fit
  8199	    // result unless it converged; an HTTP 400 is not a reason to silently
  8200	    // switch engines).
  8201	    // Only a genuine transport failure (network rejection, abort, a body that
  8202	    // could not be read) is marked for fallback; server errors — including a
  8203	    // 2xx body that was read but is not JSON (F2) — carry `serverError`.
  8204	    const _asTransport = (e) => {
  8205	      if (e && !e.serverError && (e instanceof TypeError || e.name === 'AbortError' || e instanceof SyntaxError)) e.transportFailure = true;
  8206	      throw e;
  8207	    };
  8208	    let sessionId;
  8209	    try { sessionId = await uploadToBackend(be, inten); } catch (e) { _asTransport(e); }
  8210	    const fitReq = {
  8211	      session_id: sessionId,
  8212	      background: bgPayload,
  8213	      peaks: peakSpecs,
  8214	      fit_method: fitMethod,
  8215	      n_perturb: 3,
  8216	      n_starts: nStarts       // the server also skips it for the global methods
  8217	    };
  8218	    // Unit 2: started and polled (_serverFitJob) — no request lasts longer than
  8219	    // a poll, so none meets the public URL's ~100 s ceiling. An HTTP failure is
  8220	    // a SERVER failure (serverError), never a reason to switch engines; a
  8221	    // START that cannot reach the server is a transport failure, as the single
  8222	    // request was. The ownership checks below also run inside the poll loop,
  8223	    // so a switched tab or an edited model stops the server's work at once.
  8224	    const json = await _serverFitJob(fitReq, {
  8225	      op: fitOp,
  8226	      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
  8227	    });
  8228	    if (json && json._abandoned === 'superseded') return;   // a newer fit on this tab owns the spinner and the result
  8229	    if (json && json._abandoned === 'tab') {
  8230	      _hideFitSpinner();
  8231	      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
  8232	      notify('Fit result discarded because you switched tabs during the fit.', 'amber');
  8233	      return;
  8234	    }
  8235	    if (json && json._abandoned === 'model') {
  8236	      _hideFitSpinner();
  8237	      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
  8238	      notify('Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.', 'amber', true);
  8239	      return;
  8240	    }
  8241	    if (json.error) {
  8242	      const err = new Error(json.error);
  8243	      err.serverError = true;
  8244	      throw err;
  8245	    }
  8246	    // ACCEPTANCE RULE: the backend reports lmfit's own convergence flag. A
  8247	    // result that did not converge is a failed fit, not a result (audit A08:
  8248	    // until this unit success:false was applied and announced as complete).
  8249	    if (json.success !== true) {
  8250	      const err = new Error(json.message || 'the optimizer did not converge.');
  8251	      err.notConverged = true;
  8252	      throw err;
  8253	    }
  8254	    backendResult = json;
  8255	
  8256	    // If the user switched tabs while the fit was running, discard the result
  8257	    // rather than overwriting the now-active tab's peaks.
  8258	    if (!_ownerActive(fittingTab)) {
  8259	      _hideFitSpinner();
  8260	      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
  8261	      notify('Fit result discarded because you switched tabs during the fit.', 'amber');
  8262	      return;
  8263	    }
  8264	
  8265	    // The peak controls stay editable while the fit runs. A result computed for
  8266	    // the model as it was must not be applied over an edited one (a newly locked
  8267	    // centre would keep its edited value under the server's statistics).
  8268	    if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
  8269	      _hideFitSpinner();
  8270	      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
  8271	      notify('Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.', 'amber', true);
  8272	      return;
  8273	    }
  8274	
  8275	    // Capture pre-fit values for uncertainty validation
  8276	    const _preFit = {};
  8277	    for (const p of state.peaks) {
  8278	      _preFit[p.id] = { center: p.center, fwhm: p.fwhm, amplitude: p.amplitude, glMix: p.glMix };
  8279	    }
  8280	    applyBackendResult(backendResult);
  8281	    { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }   // a new result supersedes imported provenance
  8282	    const stats = backendResult.statistics || {};
  8283	    const chiReduced = stats.reduced_chi_square || 0;
  8284	    const rmse = Math.sqrt((backendResult.residuals || []).reduce((s, v) => s + v * v, 0) / Math.max(1, be.length));
  8285	    const roiRange = { min: _arrMin(be).toFixed(1), max: _arrMax(be).toFixed(1) };
  8286	    state.fitResult = { chi: chiReduced * Math.max(1, be.length - state.peaks.length * 3),
  8287	                        chiReduced, rmse, be, bgSubtracted, bgIntensity, backendResult,
  8288	                        fittedY: backendResult.fitted_y, roiRange, _preFit,
  8289	                        starts: backendResult.starts || null,
  8290	                        startsModelKey: _startsLiveKey(),     // model + context, taken AFTER the result was applied
  8291	                        chosenAlternative: opts.chosenAlternative || null };
  8292	    // a preview of an alternative always belongs to the PREVIOUS result (an identical
  8293	    // key does not make it this one's): clear it unconditionally
  8294	    if (_historyPreview && typeof _historyPreview.snapId === 'string' && _historyPreview.snapId.startsWith('alt:')) _historyPreview = null;
  8295	    state.fitResult.rFactor = _computeRFactor(state.fitResult);
  8296	    _applyStatDisplay(state.fitResult);
  8297	    document.getElementById('sb-msg').textContent = 'Fit complete (lmfit)';
  8298	    _updateRFactorUI(state.fitResult.rFactor);
  8299	    _updateROIDisplay(roiRange);
  8300	    _hideFitSpinner();
  8301	    notify('Fit complete. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3), 'green');
  8302	  } catch (e) {
  8303	    // superseded (a newer fit on this tab): nothing at all — no message, no
  8304	    // local fallback, the newer fit owns the spinner and the result
  8305	    if (fitOp && !_fitOpCurrent(fitOp)) return;
  8306	    // Fall back to local Levenberg-Marquardt
  8307	    _hideFitSpinner();
  8308	    if (!_ownerActive(fittingTab)) {
  8309	      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
  8310	      notify('Fit cancelled — tab switched during fit.', 'amber');
  8311	      return;
  8312	    }
  8313	    if (e && e.transportFailure && opts.startPeaks) {
  8314	      // Adopting an alternative needs the server: the local engine would start
  8315	      // from the live model, not from the alternative. Nothing was changed.
  8316	      document.getElementById('sb-msg').textContent = 'Fit failed';
  8317	      notify('The server could not be reached, so the alternative was not applied. Previous peaks and result kept.', 'red', true);
  8318	      return;
  8319	    }
  8320	    if (e && e.transportFailure && ctxAtRequest !== null && !_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
  8321	      // The fallback would fit the arrays captured at the press over a model or
  8322	      // context edited since, and stamp the edited one (F1, Codex round 1).
  8323	      _hideFitSpinner();
  8324	      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
  8325	      notify('The server could not be reached, and the model or its background / ROI settings were edited while the fit was running, so no local fit was run. Previous peaks and result kept. Run the fit again.', 'amber', true);
  8326	      return;
  8327	    }
  8328	    if (e && e.transportFailure) {
  8329	      // Server unreachable: the local optimiser is the honest fallback, and
  8330	      // the overlay saying so opens only if it actually converged.
  8331	      if (e.message) console.warn('Backend unreachable, falling back to local LM:', e.message);
  8332	      const local = runFitLocal(be, bgSubtracted, bgIntensity);
  8333	      if (local && local.success && !_snapshotSuppressed) {
  8334	        document.getElementById('localfit-warn-overlay').classList.add('open');
  8335	      }
  8336	      return;
  8337	    }
  8338	    // Server-side error or non-converged optimisation: report it; the
  8339	    // previous peaks and fit result stay exactly as they were.
  8340	    const notConverged = !!(e && e.notConverged);
  8341	    document.getElementById('sb-msg').textContent = notConverged ? 'Fit did not converge' : 'Fit failed';
  8342	    notify((notConverged ? 'Fit did not converge: ' : 'Fit failed: ') + ((e && e.message) || 'unknown error') +
  8343	           ' Previous peaks and result kept.', 'red', true);
  8344	    return;
  8345	  }
  8346	
  8347	  renderPeakList();
  8348	  updatePlot();
  8349	  renderResults();
  8350	  _autoSnapshot();
  8351	}
  8352	
  8353	// Label for the goodness-of-fit statistic a fit result carries. The server
  8354	// and (since unit W1, 2026-09-18) the local engine both minimise a
  8355	// counting-noise-weighted chi-square; local results saved by unit A0 were
  8356	// UNWEIGHTED and keep the label "Residual variance", never chi-square.
  8357	function _isUnweightedLocal(fr) { return !!(fr && fr.objective === 'unweighted_residual_variance'); }
  8358	function _fitStatLabel(fr) {
  8359	  return _isUnweightedLocal(fr) ? 'Residual variance' : 'χ²ᵣ';
  8360	}
  8361	// A LOCAL result is a STARTING POINT, not a reportable result. Measured in
  8362	// unit W1 (docs/superpowers/plans/2026-09-18-local-engine-poisson-weighting.md):
  8363	// with Poisson weighting the local engine matches the server on GL-type
  8364	// models (<= 4 meV, <= 1.4 % area on the lab's C1s scans) and, since A03
  8365	// (2026-09-22: Voigt = fixed eta 0.5 on BOTH sides), on Voigt components
  8366	// wherever the two engines reach the same minimum (5 of 9 committed U 4f
  8367	// targets: every component within 4.3 meV, 2.6 % FWHM, 2 % area, 0.12 pp);
  8368	// it still differs where an LA component's m moves on the server (held,
  8369	// exactly, at its start locally - LA is discontinuous in m, caM unit) and
  8370	// where the model has several minima; and it gives no uncertainties. Unweighted A0-era results differed by more than 100 %.
  8371	// Every site that shows, exports or saves a fit result carries the
  8372	// designation, keyed on persisted identity so reloaded results are labelled.
  8373	const _LOCAL_FIT_CAVEAT = 'Local fit (Poisson-weighted like the server, no uncertainties): a starting point, not a reportable result. Run Fit before reporting.';
  8374	const _LOCAL_FIT_CAVEAT_UNWEIGHTED = 'Local unweighted fit: a starting point, not a reportable result. Run Fit before reporting.';
  8375	function _isLocalProvenance(p) {
  8376	  return !!(p && (p.engine === 'local' || p.objective === 'unweighted_residual_variance' || p.objective === 'poisson_weighted_chi_square'));
  8377	}
  8378	function _isLocalFit(fr) { return _isLocalProvenance(fr); }
  8379	// The record that governs the active model's designation: its live result,
  8380	// else the provenance it was imported / copied / restored with.
  8381	function _governingProvenance() {
  8382	  if (state.fitResult) return state.fitResult;
  8383	  const t = _activeTab();
  8384	  return (t && t.modelProvenance) || null;
  8385	}
  8386	function _localFitDetail(fr) {
  8387	  return _isUnweightedLocal(fr)
  8388	    ? 'Its areas can differ from the server fit by more than 100&nbsp;%.'
  8389	    : 'It can differ from the server fit for LA components (the page holds the smoothing parameter m at its start; the server fits it) or where the model has several minima.';
  8390	}
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
   551	
   552	
   553	# ── Fit jobs (unit 2, 2026-09-27) ────────────────────────────────────────────
   554	# Records are the Find Peaks job files (<job>.job.json, the same TTL sweep);
   555	# two small markers beside each: <job>.cancel (written by /api/fit/cancel,
   556	# any worker) and <job>.polled (touched by every poll). The fit thread's
   557	# cancel condition: the cancel marker exists, OR no poll for
   558	# FIT_JOB_ABANDON_SEC (a closed tab, a sleeping laptop; 180 s, above the ~1 min timer throttling browsers apply to hidden tabs).
   559	FIT_JOB_ABANDON_SEC = 180   # > Chrome's 1-minute timer throttling in a hidden tab: a student who switches browser tabs keeps the fit
   560	FIT_JOB_HEARTBEAT_SEC = 2.0
   561	# Concurrency (unit 2, Codex round 1). Before start-then-poll, gunicorn's four
   562	# SYNC workers bounded concurrent fits at four; a fit thread per start would
   563	# not. Each worker process runs at most FIT_JOB_MAX_RUNNING fits at once (the
   564	# rest wait "queued", heartbeating, cancellable) and admits at most
   565	# FIT_JOB_MAX_ADMITTED running + queued jobs; beyond that /api/fit/start
   566	# answers 503 "busy" immediately. With production's 4 workers: at most 4
   567	# concurrent fits, as before.
   568	FIT_JOB_MAX_RUNNING = 1
   569	FIT_JOB_MAX_ADMITTED = 6
   570	_FIT_JOB_RUN_SLOTS = threading.BoundedSemaphore(FIT_JOB_MAX_RUNNING)
   571	_FIT_JOB_ADMITTED = [0]
   572	_FIT_JOB_ADMIT_LOCK = threading.Lock()
   573	
   574	
   575	def _fit_job_admit() -> bool:
   576	    with _FIT_JOB_ADMIT_LOCK:
   577	        if _FIT_JOB_ADMITTED[0] >= FIT_JOB_MAX_ADMITTED:
   578	            return False
   579	        _FIT_JOB_ADMITTED[0] += 1
   580	        return True
   581	
   582	
   583	def _fit_job_release() -> None:
   584	    with _FIT_JOB_ADMIT_LOCK:
   585	        _FIT_JOB_ADMITTED[0] = max(0, _FIT_JOB_ADMITTED[0] - 1)
   586	
   587	
   588	def _fit_job_marker(job_id: str, upload_folder: str, kind: str) -> Path:
   589	    return Path(upload_folder) / f"{job_id}.{kind}"
   590	
   591	
   592	def _fit_job_write(job_id: str, upload_folder: str, data: dict) -> None:
   593	    """Atomic like _write_job_progress, but WITHOUT sanitising: a result's
   594	    NaN / Infinity reach the page exactly as /api/fit sends them (the page's
   595	    _readFitReply refuses them as a failed fit — unit F2)."""
   596	    path = _job_progress_path(job_id, upload_folder)
   597	    tmp = path.with_suffix(f".{threading.get_ident()}.tmp")
   598	    try:
   599	        tmp.write_text(json.dumps(data, allow_nan=True))
   600	        os.replace(tmp, path)
   601	    except OSError:
   602	        logging.getLogger(__name__).exception("failed to write fit job %s", job_id)
   603	
   604	
   605	def _fit_job_read(job_id: str, upload_folder: str):
   606	    path = _job_progress_path(job_id, upload_folder)
   607	    if not path.exists():
   608	        return None
   609	    try:
   610	        _fit_job_marker(job_id, upload_folder, "polled").touch()
   611	    except OSError:
   612	        pass
   613	    try:
   614	        data = json.loads(path.read_text())
   615	    except (OSError, ValueError):
   616	        data = {"status": "running", "elapsed_sec": 0.0}      # a read racing the first write
   617	    hb = data.get("heartbeat")
   618	    data["heartbeat_age_sec"] = round(time.time() - hb, 1) if isinstance(hb, (int, float)) else None
   619	    return data
   620	
   621	
   622	def _sweep_fit_job_markers(upload_folder: str) -> None:
   623	    """Markers left by a job whose worker died (they are removed when a job
   624	    finishes): same TTL as the job records, never raises."""
   625	    cutoff = time.time() - _ANALYZE_JOB_TTL_SEC
   626	    for pattern in ("*.cancel", "*.polled"):
   627	        try:
   628	            for m in Path(upload_folder).glob(pattern):
   629	                try:
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
   715	    # The heartbeat thread starts FIRST: if either thread fails to start this
   716	    # raises BEFORE the worker runs, and the route returns the admission; once
   717	    # the worker has started, only the worker's finally returns it (exactly
   718	    # one owner; Codex round 2).
   719	    threading.Thread(target=heartbeat, daemon=True, name=f"fit-hb-{job_id[:8]}").start()
   720	    try:
   721	        threading.Thread(target=worker, daemon=True, name=f"fit-{job_id[:8]}").start()
   722	    except Exception:
   723	        finished.set()                # stop the heartbeat of a job that never ran
   724	        raise
   725	
   726	
   727	def _require_json(f):
   728	    """Decorator: return 400 if request body is not valid JSON."""
   729	    @wraps(f)
   730	    def wrapper(*args, **kwargs):
   731	        if not request.is_json:
   732	            return _err("Request must be JSON (Content-Type: application/json)")
   733	        return f(*args, **kwargs)
   734	    return wrapper
   735	
  1250	        if not path.exists():
  1251	            return _err(f"Job '{job_id}' not found", 404)
  1252	        try:
  1253	            data = json.loads(path.read_text())
  1254	        except (OSError, ValueError):
  1255	            # os.replace() makes writes atomic, but tolerate a read racing
  1256	            # the very first write rather than 500ing a normal poll
  1257	            data = {"status": "running", "phase": "starting",
  1258	                    "candidate_index": None, "candidate_total": None,
  1259	                    "candidate_name": None, "elapsed_sec": 0.0,
  1260	                    "message": "starting analysis…"}
  1261	        return jsonify(data)
  1262	
  1263	    # ── Long fits via start-then-poll (unit 2, 2026-09-27) ───────────────────
  1264	    # The public URL ends a proxied request at ~100 s (Cloudflare 524; 88 s
  1265	    # passed, 125 s failed); basinhopping on the large C 1s models takes 3–4
  1266	    # minutes. The fit runs in a background thread on Find Peaks' job
  1267	    # infrastructure (an atomic JSON record under the upload folder, readable
  1268	    # by whichever gunicorn worker serves a poll); every HTTP request is short.
  1269	    # The record: {status: queued|running|done|error|cancelled, elapsed_sec,
  1270	    # heartbeat (epoch s, rewritten every 2 s while the fit thread lives),
  1271	    # result (done: EXACTLY the /api/fit body), error + http_status (error:
  1272	    # exactly what /api/fit would have answered)}.
  1273	
  1274	    @app.post("/api/fit/start")
  1275	    @_require_json
  1276	    def fit_start():
  1277	        body = request.get_json(silent=True)
  1278	        if not isinstance(body, dict):
  1279	            return _err("request body must be a JSON object")
  1280	        fit_args, error = _prepare_fit_request(app, body)
  1281	        if error is not None:
  1282	            return error
  1283	        upload_folder = app.config["UPLOAD_FOLDER"]
  1284	        if not _fit_job_admit():
  1285	            return _err("The server is busy with other fits. Try again in a moment.", 503)
  1286	        job_id = str(uuid.uuid4())
  1287	        try:
  1288	            _sweep_expired_jobs(upload_folder)
  1289	            _sweep_fit_job_markers(upload_folder)
  1290	            _fit_job_start(job_id, upload_folder, fit_args,
  1291	                           lambda args, cancel: _run_fit_outcome(app, args, cancel=cancel))
  1292	        except Exception:
  1293	            _fit_job_release()          # the job never started: its admission is returned
  1294	            raise
  1295	        return jsonify({"job_id": job_id}), 202
  1296	
  1297	    @app.get("/api/fit/progress/<job_id>")
  1298	    def fit_progress(job_id):
  1299	        try:
  1300	            uuid.UUID(job_id)
  1301	        except ValueError:
  1302	            return _err("Invalid job_id format (expected UUID)", 400)
  1303	        data = _fit_job_read(job_id, app.config["UPLOAD_FOLDER"])
  1304	        if data is None:
  1305	            return _err(f"Job '{job_id}' not found", 404)
  1306	        return app.response_class(json.dumps(data, allow_nan=True), mimetype="application/json")
  1307	
  1308	    @app.post("/api/fit/cancel/<job_id>")
  1309	    def fit_cancel(job_id):
  1310	        try:
  1311	            uuid.UUID(job_id)
  1312	        except ValueError:
  1313	            return _err("Invalid job_id format (expected UUID)", 400)
  1314	        _fit_job_cancel(job_id, app.config["UPLOAD_FOLDER"])
  1315	        return jsonify({"cancelled": True})
  1316	
  1317	    # ── Health check ──────────────────────────────────────────────────────────
  1318	
  1319	    @app.get("/api/health")
  1320	    def health():
  1321	        return jsonify({"status": "ok"})
  1322	
  1323	
  1324	# ─────────────────────────────────────────────────────────────────────────────
  1325	# Error handlers
  1326	# ─────────────────────────────────────────────────────────────────────────────
  1327	
  1328	def _register_error_handlers(app: Flask) -> None:
  1329	
  1330	    @app.errorhandler(404)
  1331	    def not_found(e):
  1332	        return jsonify({"error": "Not found"}), 404
  1333	
  1334	    @app.errorhandler(405)
  1335	    def method_not_allowed(e):

codex
The token checks cover the previously reported start-response and in-flight-poll races. Auto-Fit still claims its token after the confirmation modal resolves, so I’m testing whether an older invocation can then cancel a newer Run Fit. I’m also checking spinner ownership across tabs and admission release on startup failures.
exec
/bin/zsh -lc "tail -n 32 docs/autofit/codex/fit_start_poll_verdict_runA.md; tail -n 30 docs/autofit/codex/fit_start_poll_verdict_runB.md; sed -n '154,205p' docs/superpowers/plans/2026-09-27-long-fits-start-poll.md; sed -n '1,100p' tests/test_fit_start_poll.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
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

exec
/bin/zsh -lc "sed -n '1,180p' tests/js/fit_start_poll.test.js; sed -n '1,155p' tests/js/fit_acceptance.test.js; rg -n 'function _showAutoFitConfirmModal|function _showFitSpinner|function _hideFitSpinner|function _opOwner|function _ownerActive|ctrlKey|metaKey' templates/index.html; cat scripts/public_fit_poll_check.py; git diff fix-acceptance-holes..HEAD -- fitting.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
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
    'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap();',
    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_claimFitOp'), extractFn('_fitOpCurrent'),
    extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
  return new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob, _runningFitJobs, _claimFitOp };')(
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

// Round 2: ownership is an OPERATION claimed before the caller's first await
// (_claimFitOp); the newest claim for a tab is current whatever order the
// server's responses arrive in, and a superseded operation returns
// { _abandoned: 'superseded' } at every step after an await and before every
// exit (a result, an error, a timeout).
function makeAsync(fetch) {
  const src = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
    'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap();',
    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_claimFitOp'), extractFn('_fitOpCurrent'),
    extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
  return new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob, _claimFitOp };')(
    fetch, f => { setImmediate(f); return 0; }, class extends Error {});   // yield to the event loop between polls
}
const deferred = () => { let res; const p = new Promise(r => { res = r; }); return { p, res }; };

test('the NEWEST claim is current whatever order the start responses arrive in (Codex round 2)', async () => {
  const calls = [];
  const aStart = deferred();
  let n = 0;
  const fetch = async (url, init) => {
    calls.push({ url, method: (init && init.method) || 'GET' });
    if (url === '/api/fit/start') {
      const id = 'J' + (++n);
      if (id === 'J1') await aStart.p;                 // A's start response is delayed
      return ok({ job_id: id }, 202);
    }
    if (url.startsWith('/api/fit/progress/')) return ok({ status: 'done', result: { which: url.split('/').pop() } });
    return ok({});
  };
  const { _serverFitJob, _claimFitOp } = makeAsync(fetch);
  const owner = { id: 'tab-1' };
  const opA = _claimFitOp(owner);                      // A pressed first
  const a = _serverFitJob({}, { op: opA });
  await new Promise(r => setImmediate(r));
  const opB = _claimFitOp(owner);                      // B pressed second
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
  'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap();', ...['_cancelFitJob', '_fitHttpError', '_claimFitOp', '_fitOpCurrent', '_serverFitJob'].map(n => extractFn(n))].join('\n');
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
2347:function _opOwner() {
2354:function _ownerActive(owner) {
5865:  if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'p')) {
5887:  if (e.ctrlKey || e.metaKey) {
6688:function _showFitSpinner() {
6701:function _hideFitSpinner() {
6737:function _showAutoFitConfirmModal(peakCount) {
15840:      ` onclick="_fpToggleRegion('${_fpEsc(e.region)}', event.ctrlKey||event.metaKey)"` +
15841:      ` onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();_fpToggleRegion('${_fpEsc(e.region)}', event.ctrlKey||event.metaKey)}"` +
15864:      ` onclick="_fpPickFromSearch('${_fpEsc(o.value)}', event.ctrlKey||event.metaKey)"` +
15865:      ` onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();_fpPickFromSearch('${_fpEsc(o.value)}', event.ctrlKey||event.metaKey)}">` +
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
HEARTBEAT_LOST_S = 30.0      # as the page: a record whose heartbeat stopped is a lost fit
DEADLINE_S = 20 * 60         # per target: never poll forever
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
        if rec.get("status") not in ("running", "queued"):
            break
        hb = rec.get("heartbeat_age_sec")
        if isinstance(hb, (int, float)) and hb > HEARTBEAT_LOST_S:
            rec = {"status": "lost", "error": f"heartbeat stopped {hb:.0f} s ago (worker restarted?)"}
            break
        if time.time() - t0 > DEADLINE_S:
            _req(base + f"/api/fit/cancel/{job}", b"", method="POST")
            rec = {"status": "deadline", "error": f"no result after {DEADLINE_S} s"}
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
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-v04n4bDf' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-3FDrUMg0' (errno=Operation not permitted)
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
/bin/zsh -lc 'node --test tests/js/fit_start_poll.test.js tests/js/fit_acceptance.test.js tests/js/stale_statistics.test.js tests/js/per_tab_state.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 344ms:
# Subtest: A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
ok 1 - A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
  ---
  duration_ms: 9.667964
  type: 'test'
  ...
# Subtest: a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
ok 2 - a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
  ---
  duration_ms: 5.03107
  type: 'test'
  ...
# Subtest: a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
ok 3 - a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
  ---
  duration_ms: 3.181263
  type: 'test'
  ...
# Subtest: a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
ok 4 - a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
  ---
  duration_ms: 10.899406
  type: 'test'
  ...
# Subtest: a converged backend result is applied (sanity)
ok 5 - a converged backend result is applied (sanity)
  ---
  duration_ms: 3.278014
  type: 'test'
  ...
# Subtest: the engine/objective labels of a fit result survive spectrum and project save/load
ok 6 - the engine/objective labels of a fit result survive spectrum and project save/load
  ---
  duration_ms: 0.758147
  type: 'test'
  ...
# Subtest: an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
ok 7 - an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
  ---
  duration_ms: 2.996764
  type: 'test'
  ...
# Subtest: an HTTP 502 on the upload is a server failure, not a transport failure
ok 8 - an HTTP 502 on the upload is a server failure, not a transport failure
  ---
  duration_ms: 3.405363
  type: 'test'
  ...
# Subtest: uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
ok 9 - uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
  ---
  duration_ms: 2.101461
  type: 'test'
  ...
# Subtest: every consumer that prints the goodness-of-fit statistic routes through the statistic identity
ok 10 - every consumer that prints the goodness-of-fit statistic routes through the statistic identity
  ---
  duration_ms: 1.117829
  type: 'test'
  ...
# Subtest: uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
ok 11 - uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
  ---
  duration_ms: 0.711634
  type: 'test'
  ...
# Subtest: a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
ok 12 - a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
  ---
  duration_ms: 1.955269
  type: 'test'
  ...
# Subtest: starting-point helpers: keyed on the persisted objective, weighted results untouched
ok 13 - starting-point helpers: keyed on the persisted objective, weighted results untouched
  ---
  duration_ms: 5.104227
  type: 'test'
  ...
# Subtest: Quantify shows the starting-point banner for a local result and not for a weighted one
ok 14 - Quantify shows the starting-point banner for a local result and not for a weighted one
  ---
  duration_ms: 5.475729
  type: 'test'
  ...
# Subtest: every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
ok 15 - every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
  ---
  duration_ms: 1.857393
  type: 'test'
  ...
# Subtest: project save derives the designation from the objective for an older local result lacking the new fields
ok 16 - project save derives the designation from the objective for an older local result lacking the new fields
  ---
  duration_ms: 9.116216
  type: 'test'
  ...
# Subtest: stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
ok 17 - stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
  ---
  duration_ms: 1.097367
  type: 'test'
  ...
# Subtest: _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
ok 18 - _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
  ---
  duration_ms: 3.692037
  type: 'test'
  ...
# Subtest: history preview glow is keyed on the dataset flag, not the label text
ok 19 - history preview glow is keyed on the dataset flag, not the label text
  ---
  duration_ms: 0.687281
  type: 'test'
  ...
# Subtest: spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
ok 20 - spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
  ---
  duration_ms: 0.472636
  type: 'test'
  ...
# Subtest: _applyStatDisplay clears header, tooltip, caption and value together on local → none
ok 21 - _applyStatDisplay clears header, tooltip, caption and value together on local → none
  ---
  duration_ms: 3.622608
  type: 'test'
  ...
# Subtest: _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
ok 22 - _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
  ---
  duration_ms: 2.310449
  type: 'test'
  ...
# Subtest: fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
ok 23 - fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
  ---
  duration_ms: 1.5039
  type: 'test'
  ...
# Subtest: undo/redo snapshots carry and restore model provenance
ok 24 - undo/redo snapshots carry and restore model provenance
  ---
  duration_ms: 3.848664
  type: 'test'
  ...
# Subtest: round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
ok 25 - round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
  ---
  duration_ms: 1.262138
  type: 'test'
  ...
# Subtest: _provenanceOf derives a designation from a live local result, and undo snapshots use it
ok 26 - _provenanceOf derives a designation from a live local result, and undo snapshots use it
  ---
  duration_ms: 2.938866
  type: 'test'
  ...
# Subtest: batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
ok 27 - batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
  ---
  duration_ms: 0.366388
  type: 'test'
  ...
# Subtest: the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
ok 28 - the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
  ---
  duration_ms: 2.29319
  type: 'test'
  ...
# Subtest: round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
ok 29 - round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
  ---
  duration_ms: 1.239635
  type: 'test'
  ...
# Subtest: the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
ok 30 - the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
  ---
  duration_ms: 2.524132
  type: 'test'
  ...
# Subtest: the sidebar banner is sticky at the top of the scrolling panel body
ok 31 - the sidebar banner is sticky at the top of the scrolling panel body
  ---
  duration_ms: 0.334113
  type: 'test'
  ...
# Subtest: the sidebar banner shows on a stack tab whose visible entries draw a local source fit
ok 32 - the sidebar banner shows on a stack tab whose visible entries draw a local source fit
  ---
  duration_ms: 2.91081
  type: 'test'
  ...
# Subtest: every stack chart repaint path refreshes the sidebar designation before any early return
ok 33 - every stack chart repaint path refreshes the sidebar designation before any early return
  ---
  duration_ms: 0.489232
  type: 'test'
  ...
# Subtest: closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
ok 34 - closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
  ---
  duration_ms: 0.23611
  type: 'test'
  ...
# Subtest: W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
ok 35 - W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
  ---
  duration_ms: 3.172297
  type: 'test'
  ...
# Subtest: TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
ok 36 - TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
  ---
  duration_ms: 4.167846
  type: 'test'
  ...
# Subtest: adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
ok 37 - adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
  ---
  duration_ms: 3.324123
  type: 'test'
  ...
# Subtest: adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
ok 38 - adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
  ---
  duration_ms: 3.142601
  type: 'test'
  ...
# Subtest: adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
ok 39 - adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
  ---
  duration_ms: 2.961315
  type: 'test'
  ...
# Subtest: adoption: success records the choice, the starts evidence and the key of the model it describes
ok 40 - adoption: success records the choice, the starts evidence and the key of the model it describes
  ---
  duration_ms: 3.032257
  type: 'test'
  ...
# Subtest: an ordinary Run Fit on one unlinked component does not ask for the starts check
ok 41 - an ordinary Run Fit on one unlinked component does not ask for the starts check
  ---
  duration_ms: 3.26251
  type: 'test'
  ...
# Subtest: a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
ok 42 - a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
  ---
  duration_ms: 3.435693
  type: 'test'
  ...
# Subtest: a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
ok 43 - a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
  ---
  duration_ms: 6.518759
  type: 'test'
  ...
# Subtest: a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
ok 44 - a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
  ---
  duration_ms: 3.91359
  type: 'test'
  ...
# Subtest: a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
ok 45 - a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
  ---
  duration_ms: 5.66623
  type: 'test'
  ...
# Subtest: the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)
ok 46 - the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)
  ---
  duration_ms: 0.996799
  type: 'test'
  ...
# Subtest: the token scan is linear and keeps a truncated string a string (Codex round 2)
ok 47 - the token scan is linear and keeps a truncated string a string (Codex round 2)
  ---
  duration_ms: 3.670748
  type: 'test'
  ...
# Subtest: a minus sign counts only after a boundary: "x-Infinity" is malformed, "-Infinity" a token (Codex round 3)
ok 48 - a minus sign counts only after a boundary: "x-Infinity" is malformed, "-Infinity" a token (Codex round 3)
  ---
  duration_ms: 0.649904
  type: 'test'
  ...
# Subtest: start -> running polls -> done: the result is the /api/fit body; no job is left registered
ok 49 - start -> running polls -> done: the result is the /api/fit body; no job is left registered
  ---
  duration_ms: 11.505084
  type: 'test'
  ...
# Subtest: a bad request: the synchronous route's message and status, immediately; no poll
ok 50 - a bad request: the synchronous route's message and status, immediately; no poll
  ---
  duration_ms: 4.339699
  type: 'test'
  ...
# Subtest: a START that cannot reach the server is a transport failure (the caller may fall back to the local engine)
ok 51 - a START that cannot reach the server is a transport failure (the caller may fall back to the local engine)
  ---
  duration_ms: 4.004653
  type: 'test'
  ...
# Subtest: an error record is a failed fit with the synchronous message and status
ok 52 - an error record is a failed fit with the synchronous message and status
  ---
  duration_ms: 3.897986
  type: 'test'
  ...
# Subtest: a done record carrying NaN is F2's failed fit (unreadable reply), not a transport failure
ok 53 - a done record carrying NaN is F2's failed fit (unreadable reply), not a transport failure
  ---
  duration_ms: 3.58287
  type: 'test'
  ...
# Subtest: one lost poll is retried; five in a row are a transport failure and cancel the job
ok 54 - one lost poll is retried; five in a row are a transport failure and cancel the job
  ---
  duration_ms: 6.736693
  type: 'test'
  ...
# Subtest: a stopped heartbeat (restarted worker) is a failed fit, never an endless spinner
ok 55 - a stopped heartbeat (restarted worker) is a failed fit, never an endless spinner
  ---
  duration_ms: 2.894952
  type: 'test'
  ...
# Subtest: a job cancelled on the server (abandoned) is reported, not waited for
ok 56 - a job cancelled on the server (abandoned) is reported, not waited for
  ---
  duration_ms: 3.078778
  type: 'test'
  ...
# Subtest: ownership inside the loop: a switched tab or an edited model cancels the job and returns the reason
ok 57 - ownership inside the loop: a switched tab or an edited model cancels the job and returns the reason
  ---
  duration_ms: 6.45345
  type: 'test'
  ...
# Subtest: the Auto-Fit abort (2 minutes) cancels the job and surfaces as an AbortError
ok 58 - the Auto-Fit abort (2 minutes) cancels the job and surfaces as an AbortError
  ---
  duration_ms: 4.225863
  type: 'test'
  ...
# Subtest: Run Fit and Auto-Fit both go through _serverFitJob; nothing on the page posts to the synchronous /api/fit any more
ok 59 - Run Fit and Auto-Fit both go through _serverFitJob; nothing on the page posts to the synchronous /api/fit any more
  ---
  duration_ms: 2.508993
  type: 'test'
  ...
# Subtest: the NEWEST claim is current whatever order the start responses arrive in (Codex round 2)
ok 60 - the NEWEST claim is current whatever order the start responses arrive in (Codex round 2)
  ---
  duration_ms: 11.842669
  type: 'test'
  ...
# Subtest: a poll in flight when a newer claim arrives: its reply is never applied, never an error (Codex round 2)
ok 61 - a poll in flight when a newer claim arrives: its reply is never applied, never an error (Codex round 2)
  ---
  duration_ms: 11.78609
  type: 'test'
  ...
# Subtest: an Auto-Fit timeout after a newer claim is superseded, not a timeout (Codex round 2)
ok 62 - an Auto-Fit timeout after a newer claim is superseded, not a timeout (Codex round 2)
  ---
  duration_ms: 4.269253
  type: 'test'
  ...
# Subtest: both callers claim their operation before the first await and do nothing at all when superseded
ok 63 - both callers claim their operation before the first await and do nothing at all when superseded
  ---
  duration_ms: 1.443892
  type: 'test'
  ...
# Subtest: every module-level mutable is allowlisted with a valid non-C class
ok 64 - every module-level mutable is allowlisted with a valid non-C class
  ---
  duration_ms: 182.972696
  type: 'test'
  ...
# Subtest: inherited property names and anonymous-class names cannot slip through the allowlist
ok 65 - inherited property names and anonymous-class names cannot slip through the allowlist
  ---
  duration_ms: 72.830534
  type: 'test'
  ...
# Subtest: the known class-C holders are gone from module scope
ok 66 - the known class-C holders are gone from module scope
  ---
  duration_ms: 5.456759
  type: 'test'
  ...
# Subtest: async operations capture their owning record before the first await
ok 67 - async operations capture their owning record before the first await
  ---
  duration_ms: 1.947131
  type: 'test'
  ...
# Subtest: undo/redo and Find Peaks apply read the ACTIVE tab record only
ok 68 - undo/redo and Find Peaks apply read the ACTIVE tab record only
  ---
  duration_ms: 0.549012
  type: 'test'
  ...
# Subtest: one accessor classifies a result against a key: none / unverified / current / stale
ok 69 - one accessor classifies a result against a key: none / unverified / current / stale
  ---
  duration_ms: 13.054902
  type: 'test'
  ...
# Subtest: the key is the step (b) key: F1 adds no second binding mechanism and no new key field
ok 70 - the key is the step (b) key: F1 adds no second binding mechanism and no new key field
  ---
  duration_ms: 3.449579
  type: 'test'
  ...
# Subtest: Results panel, current: statistic, RMSE, R and sigma are shown
ok 71 - Results panel, current: statistic, RMSE, R and sigma are shown
  ---
  duration_ms: 9.6389
  type: 'test'
  ...
# Subtest: Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
ok 72 - Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
  ---
  duration_ms: 8.045956
  type: 'test'
  ...
# Subtest: Results panel, unverified (older save, no key): values shown with a plain note
ok 73 - Results panel, unverified (older save, no key): values shown with a plain note
  ---
  duration_ms: 9.143845
  type: 'test'
  ...
# Subtest: status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
ok 74 - status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
  ---
  duration_ms: 8.506386
  type: 'test'
  ...
# Subtest: the stored fitted curve is never drawn, saved or stacked as the fit once stale
ok 75 - the stored fitted curve is never drawn, saved or stacked as the fit once stale
  ---
  duration_ms: 3.568537
  type: 'test'
  ...
# Subtest: saves keep the key and say plainly when the statistics are stale or unverified
ok 76 - saves keep the key and say plainly when the statistics are stale or unverified
  ---
  duration_ms: 2.491487
  type: 'test'
  ...
# Subtest: CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
ok 77 - CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
  ---
  duration_ms: 15.990128
  type: 'test'
  ...
# Subtest: XLSX: stale writes a WARNING row instead of the statistic, and no sigma
ok 78 - XLSX: stale writes a WARNING row instead of the statistic, and no sigma
  ---
  duration_ms: 5.393677
  type: 'test'
  ...
# Subtest: TSV: stale says the Model / Residual columns are the current, unfitted model
ok 79 - TSV: stale says the Model / Residual columns are the current, unfitted model
  ---
  duration_ms: 8.533892
  type: 'test'
  ...
# Subtest: the refresh re-renders Results only when its rendered state differs
ok 80 - the refresh re-renders Results only when its rendered state differs
  ---
  duration_ms: 2.997094
  type: 'test'
  ...
# Subtest: an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
ok 81 - an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
  ---
  duration_ms: 2.886032
  type: 'test'
  ...
# Subtest: Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
ok 82 - Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
  ---
  duration_ms: 3.854823
  type: 'test'
  ...
# Subtest: Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
ok 83 - Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
  ---
  duration_ms: 9.26369
  type: 'test'
  ...
# Subtest: closing the last tab clears the Results panel, header and status statistics too
ok 84 - closing the last tab clears the Results panel, header and status statistics too
  ---
  duration_ms: 0.185056
  type: 'test'
  ...
# Subtest: reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
ok 85 - reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
  ---
  duration_ms: 1.50869
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back
ok 86 - F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back
  ---
  duration_ms: 5.129247
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a Cloudflare 524 (plain-text body) is a failed request with its status, never "could not be read"
ok 87 - F2: Auto-Fit on a Cloudflare 524 (plain-text body) is a failed request with its status, never "could not be read"
  ---
  duration_ms: 4.679177
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a 500 with a JSON error is a failed request with its status, never "could not be read"
ok 88 - F2: Auto-Fit on a 500 with a JSON error is a failed request with its status, never "could not be read"
  ---
  duration_ms: 2.921369
  type: 'test'
  ...
1..88
# tests 88
# suites 0
# pass 88
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 381.065858

exec
/bin/zsh -lc "rg -n 'function .*Auto|function .*Sandbox|function .*sandbox|function _showAutoFitConfirmModal|function _showFitSpinner|function _hideFitSpinner|function _opOwner|function _ownerActive|ctrlKey|metaKey' tests/js/stale_statistics.test.js tests/js/fit_acceptance.test.js templates/index.html; sed -n '55,125p' tests/js/fit_acceptance.test.js; sed -n '390,485p' tests/js/stale_statistics.test.js; sed -n '7405,7467p' templates/index.html; sed -n '11900,11930p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
tests/js/stale_statistics.test.js:48:function sandbox({ liveKey = 'K1' } = {}) {
tests/js/stale_statistics.test.js:209:function exportSandbox(liveKey, fr) {
tests/js/fit_acceptance.test.js:317:  assert.match(grab('function applyAutoFitResult(', 12000), /_applyStatDisplay\(state\.fitResult\)/, 'auto-fit refreshes the statistic display');
tests/js/fit_acceptance.test.js:394:  for (const fn of ['function runFitLocal(', 'async function runFit(', 'function applyAutoFitResult(', 'function clearAllPeaks()']) {
templates/index.html:2347:function _opOwner() {
templates/index.html:2354:function _ownerActive(owner) {
templates/index.html:5865:  if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'p')) {
templates/index.html:5887:  if (e.ctrlKey || e.metaKey) {
templates/index.html:6688:function _showFitSpinner() {
templates/index.html:6701:function _hideFitSpinner() {
templates/index.html:6712:function _recomputeAutoFitMenuState() {
templates/index.html:6737:function _showAutoFitConfirmModal(peakCount) {
templates/index.html:6860:function buildAutoFitModel(assessment) {
templates/index.html:7287:function applyAutoFitResult(json, graphiteRaw, roi) {
templates/index.html:7595:async function runAutoFitC1sGraphite() {
templates/index.html:13902:function _refAutoTolBase() {
templates/index.html:15840:      ` onclick="_fpToggleRegion('${_fpEsc(e.region)}', event.ctrlKey||event.metaKey)"` +
templates/index.html:15841:      ` onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();_fpToggleRegion('${_fpEsc(e.region)}', event.ctrlKey||event.metaKey)}"` +
templates/index.html:15864:      ` onclick="_fpPickFromSearch('${_fpEsc(o.value)}', event.ctrlKey||event.metaKey)"` +
templates/index.html:15865:      ` onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();_fpPickFromSearch('${_fpEsc(o.value)}', event.ctrlKey||event.metaKey)}">` +
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

test('reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model', () => {
  const load = extractFn('_loadSpectrumFile');
  assert.match(load, /if \(data\.fittedY && data\.statistics\.statisticsState !== 'stale'\) fr\.fittedY = data\.fittedY;/);
  assert.match(load, /if \(data\.statistics\.rFactor && data\.statistics\.statisticsState !== 'stale'\) fr\.rFactor = data\.statistics\.rFactor;/);
  assert.match(html, /state\.fitResult\.rFactor == null && _statsLiveState\(\) !== 'stale'\) \{\s*state\.fitResult\.rFactor = _computeRFactor/, 'tab activation');
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
}

// Top-level entry point. Wired to the Actions menu item.
// Read a 2xx /api/fit reply (unit F2, 2026-09-26). A failure to READ the body
// is a transport failure (the caller may fall back to the local engine); a
// body that was read but is not JSON is the SERVER's reply, so it is a failed
// fit with a message — never a reason to switch engines. The case seen: an
// uncertainty that could not be computed, serialised as NaN (Flask writes
// NaN / Infinity tokens, which JSON.parse rejects).
async function _readFitReply(resp) {
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
        if (ch === 'I' && t.startsWith('Infinity', i) && (bound(t[i - 1]) || (t[i - 1] === '-' && bound(t[i - 2]))) && bound(t[i + 8])) return true;   // a sign only after a boundary (round 3)
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
// The public URL ends a proxied request at ~100 s (Cloudflare 524); a
// basinhopping fit of a large C 1s model takes 3–4 minutes. So the fit is
// STARTED (/api/fit/start: the same validation as /api/fit, an immediate 400
// for a bad request, else 202 + a job id) and POLLED (/api/fit/progress, a
// short request every FIT_POLL_MS); no request of this path lasts longer than
// a poll. The final record's `result` is exactly the body /api/fit returns,
// read with F2's rules (_readFitReply: a body read but not JSON — a NaN — is
// the server's failed fit). The caller's ownership rules run INSIDE the loop:
// `guard.abandoned()` returning a reason ('tab' | 'model') cancels the job on
// the server and returns { _abandoned: reason } — the caller discards with
// its usual message. Transport: a START that cannot reach the server is a
// transport failure (the caller's local fallback, as before); a poll that
// cannot is retried and only FIT_POLL_TRANSPORT_RETRIES in a row are. A
// record whose heartbeat stops (a restarted worker takes the fit thread with
// it) is a failed fit, never an endless spinner. Cancellation also reaches
// the server when the page is closed (pagehide beacon) and, server-side,
// when polls stop for three minutes (above the ~1-minute timer throttling of a hidden browser tab).
const FIT_POLL_MS = 500;
const FIT_POLL_TRANSPORT_RETRIES = 5;
  if (!roiRange) { el.textContent = ''; return; }
  el.textContent = `ROI: ${roiRange.min}\u2013${roiRange.max} eV`;
}

const _LOCALFIT_TOOLTIP = "Statistic of the local (in-page) fit. Since unit W1 (2026-09) the local engine is Poisson-weighted like the server, so its \u03c7\u00b2\u1d63 is comparable with the server's, but it gives no parameter uncertainties and can differ from the server fit for LA components (m held at its start locally) or where the model has several minima. Local results saved earlier were unweighted and are labelled 'Residual variance'. Run Fit with the server available for a reportable result.";
const _CHISQ_TOOLTIP = "Reduced chi-squared (\u03c7\u00b2\u1d63) measures the goodness of fit weighted by data uncertainty. Computed within the ROI range.\n\n\u2022 \u03c7\u00b2 \u2248 1.0 = ideal fit (residuals match expected noise)\n\u2022 \u03c7\u00b2 >> 1 = poor fit or underestimated uncertainties\n\u2022 \u03c7\u00b2 << 1 = possible overfitting or overestimated uncertainties\n\nNote: a low \u03c7\u00b2 does not guarantee a correct model \u2014 always check the R-factor and visually inspect residuals.";

// Wire up custom tooltip for data-xps-tip elements (R-factor, chi-squared, etc.)
(function () {
  const DELAY = 300;
  let timer = null;
  document.addEventListener('mouseenter', function (e) {
    const el = e.target instanceof Element ? e.target.closest('[data-xps-tip]') : null;
    if (!el) return;
    clearTimeout(timer);
    timer = setTimeout(() => {
      const tip = document.getElementById('xps-tooltip');
      if (!tip) return;
      tip.textContent = '';
      const lines = el.dataset.xpsTip.split('\n');
      lines.forEach((line, i) => {
        if (i > 0) tip.appendChild(document.createElement('br'));
        tip.appendChild(document.createTextNode(line));
      });
      tip.classList.remove('tip-above', 'visible');
      const rect = el.getBoundingClientRect();
      const tipH = 160;
      const spaceBelow = window.innerHeight - rect.bottom;
      if (spaceBelow < tipH && rect.top > tipH) {
        tip.classList.add('tip-above');
        tip.style.top = (rect.top - tipH - 6) + 'px';

exec
/bin/zsh -lc "sed -n '2343,2360p' templates/index.html; sed -n '5880,5910p' templates/index.html; sed -n '6680,6775p' templates/index.html; git diff fix-acceptance-holes..HEAD -- app.py | tail -n 180; git diff fix-acceptance-holes..HEAD -- fitting.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
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
        const id = parseInt(body.id.replace('peak-body-', ''));
        if (!isNaN(id)) removePeak(id);
      }
      break;
    }
    case '+': case '=': togglePlaceMode('peak'); break;
    case 'm': case 'M': _onMultipletBtnClick(); break;
    case '?': showShortcutsModal(); break;
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
    item.removeAttribute('aria-disabled');
    item.title = 'Auto-Fit C1s Graphite — one-click fit + charge correction';
  } else {
    item.setAttribute('aria-disabled', 'true');
    item.title = 'Auto-Fit C1s Graphite is only available for C1s spectra (ROI midpoint 270–315 eV).';
  }
}

// Late-init for Auto-Fit menu state (in case startup runs before the
// menu item is in the DOM).
window.addEventListener('DOMContentLoaded', () => {
  if (typeof _recomputeAutoFitMenuState === 'function') _recomputeAutoFitMenuState();
});

// Returns a Promise<boolean> — true if user clicks Proceed, false on Cancel/X.
let _autoFitConfirmResolver = null;
function _showAutoFitConfirmModal(peakCount) {
  return new Promise(resolve => {
    _autoFitConfirmResolver = resolve;
    const span = document.getElementById('auto-fit-c1s-confirm-count');
    if (span) span.textContent = String(peakCount);
    const proceed = document.getElementById('auto-fit-c1s-confirm-proceed');
    proceed.onclick = () => {
      document.getElementById('auto-fit-c1s-confirm-overlay').classList.remove('open');
      const r = _autoFitConfirmResolver; _autoFitConfirmResolver = null;
      if (r) r(true);
    };
    document.getElementById('auto-fit-c1s-confirm-overlay').classList.add('open');
  });
}
function _autoFitConfirmCancel() {
  document.getElementById('auto-fit-c1s-confirm-overlay').classList.remove('open');
  const r = _autoFitConfirmResolver; _autoFitConfirmResolver = null;
  if (r) r(false);
}

// Returns true if the tab is a C1s spectrum, defined by ROI midpoint
// in [270.0, 315.0] eV. Uses the tab's persisted UI ROI fields (which
// are corrected-BE values), falling back to the current rawBE range.
// Reads from a tab record, not state, so it works for inactive tabs.
// Find graphite in the raw-BE frame from a background-subtracted spectrum.
//   rawBE      : array of raw BE values (state.rawBE, NOT corrected)
//   bgSubInten : background-subtracted intensity at the same indices
// Returns the BE of the highest-BE strong local maximum, or null.
//
// Algorithm (matches spec §1):
//   1. Find all strict local maxima of bgSubInten (3-point test).
//   2. Filter to "strong" maxima: bgSubInten[i] >= 0.30 * max(bgSubInten).
//   3. Pick the one with the highest rawBE value.
function findGraphiteRawBE(rawBE, bgSubInten) {
  const n = rawBE && rawBE.length;
  if (!n || n !== bgSubInten.length || n < 3) return null;
  let gMax = -Infinity;
  for (const v of bgSubInten) if (v > gMax) gMax = v;
  if (!(gMax > 0)) return null;
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-QfCohOA5' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-IL5l4sp0' (errno=Operation not permitted)
+                pass
+
+    # The heartbeat thread starts FIRST: if either thread fails to start this
+    # raises BEFORE the worker runs, and the route returns the admission; once
+    # the worker has started, only the worker's finally returns it (exactly
+    # one owner; Codex round 2).
+    threading.Thread(target=heartbeat, daemon=True, name=f"fit-hb-{job_id[:8]}").start()
+    try:
+        threading.Thread(target=worker, daemon=True, name=f"fit-{job_id[:8]}").start()
+    except Exception:
+        finished.set()                # stop the heartbeat of a job that never ran
+        raise
+
+
 def _require_json(f):
     """Decorator: return 400 if request body is not valid JSON."""
     @wraps(f)
@@ -779,94 +1060,13 @@ def _register_routes(app: Flask) -> None:
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
@@ -1060,6 +1260,60 @@ def _register_routes(app: Flask) -> None:
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
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-NAXpxBc8' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-T9AAOVHe' (errno=Operation not permitted)
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
/bin/zsh -lc "node -e '
const fs=require('\\''fs'\\''),path=require('\\''path'\\'');
const prefix=fs.readFileSync('\\''tests/js/fit_start_poll.test.js'\\'','\\''utf8'\\'').split(\"test('\\''start ->\")[0];
const {extractFn,constLine,ok}=new Function('\\''require'\\'','\\''__dirname'\\'',prefix+'\\'';return {extractFn,constLine,ok};'\\'')(require,path.resolve('\\''tests/js'\\''));
const src=[constLine('\\''FIT_POLL_MS'\\''),constLine('\\''FIT_POLL_TRANSPORT_RETRIES'\\''),constLine('\\''FIT_HEARTBEAT_LOST_SEC'\\''),'\\''const _runningFitJobs=new Set();let _fitOpSeq=0;const _fitOpByOwner=new WeakMap();const _STARTS_N=3;'\\'',...['\\''_claimFitOp'\\'','\\''_fitOpCurrent'\\'','\\''_cancelFitJob'\\'','\\''_fitHttpError'\\'','\\''_readFitReply'\\'','\\''_serverFitJob'\\'','\\''runFit'\\'','\\''runAutoFitC1sGraphite'\\''].map(extractFn)].join('\\''\\n'\\'');
const flush=async()=>{for(let i=0;i<30;i++)await Promise.resolve();};
function env(){
 const state={peaks:[{id:1,name:'\\''original'\\'',center:284.7}],rawBE:[285,284.5,284],rawIntensity:[10,20,10],ccShift:0};
 const out={notes:[],cancels:[],applied:0,restores:0,hides:0,spinner:false,starts:0}; const tab1={id:1},tab2={id:2}; let active=tab1,confirm;
 const timers=[],polls=[],dom={};
 const deps={state,document:{getElementById:id=>dom[id]??={value:({'\\''bg-type'\\'':'\\''none'\\'','\\''bg-start'\\'':'\\''285'\\'','\\''bg-end'\\'':'\\''284'\\'','\\''fit-method'\\'':'\\''leastsq'\\''})[id]||'\\'''\\'',style:{}},querySelector:()=>({})},tabManager:{activeId:1,_getTab:()=>active},isC1sTab:()=>true,_opOwner:()=>active,_ownerActive:o=>o===active,notify:m=>out.notes.push(m),_autoFitSnapshot:()=>({peaks:state.peaks}),_autoFitRestore:s=>{out.restores++;state.peaks=s.peaks;},_showAutoFitConfirmModal:()=>new Promise(r=>confirm=r),getROIData:()=>({be:state.rawBE,inten:state.rawIntensity}),computeBackground:b=>b.map(()=>0),findGraphiteRawBE:()=>284.5,assessLowBERegion:()=>({}),pushUndo(){},updateChargeCorrection(){},buildAutoFitModel:()=>[{id:1,name:'\\''Graphite'\\'',center:284.5}],renderPeakList(){},_showFitSpinner:()=>out.spinner=true,_hideFitSpinner:()=>{out.hides++;out.spinner=false;},AbortController,DOMException,setTimeout:(f,ms)=>{if(ms===500)timers.push(f);return 1;},clearTimeout(){},_bgWindowIndices:()=>({i0:0,i1:2}),_startsLiveKey:()=>JSON.stringify(state.peaks),_sameFitKey:(a,b)=>a===b,peakToBackendSpec:p=>({...p}),_getManualAnchors:()=>[],uploadToBackend:async()=>'\\''sid'\\'',_startsUnlinkedCount:()=>1,fetch:async u=>{if(u.endsWith('\\''/start'\\''))return ok({job_id:'\\''J'\\''+(++out.starts)});if(u.includes('\\''/cancel/'\\'')){out.cancels.push(u);return ok({});}return new Promise(r=>polls.push({u,r}));},applyBackendResult:()=>out.applied++,applyAutoFitResult:()=>true};
 const api=new Function(...Object.keys(deps),src+'\\'';return {runFit,runAutoFitC1sGraphite};'\\'')(...Object.values(deps));
 return {api,out,state,timers,polls,confirm:()=>confirm(true),switchTab:()=>active=tab2};
}
(async()=>{
 const e=env();const a=e.api.runAutoFitC1sGraphite();await flush();const b=e.api.runFit();await flush();e.timers.shift()();await flush();
 e.confirm();await flush();console.log('\\''Modal A opened before Run B; after confirming A:'\\'',JSON.stringify({out:e.out,peaks:e.state.peaks}));
 e.polls.shift().r(ok({status:'\\''done'\\'',result:{success:true}}));await b;e.timers.shift()();await flush();e.polls.shift().r(ok({status:'\\''done'\\'',result:{success:true}}));await a;
 console.log('\\''Modal final:'\\'',JSON.stringify(e.out));
 const f=env();const first=f.api.runFit();await flush();f.switchTab();const second=f.api.runFit();await flush();f.timers.shift()();await first;
 console.log('\\''Tab A discard while tab B running:'\\'',JSON.stringify(f.out));
 f.timers.shift()();await flush();f.polls.shift().r(ok({status:'\\''error'\\'',http_status:400,error:'\\''cleanup'\\''}));await second;
})();
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
Modal A opened before Run B; after confirming A: {"out":{"notes":[],"cancels":["/api/fit/cancel/J1"],"applied":0,"restores":0,"hides":0,"spinner":true,"starts":2},"peaks":[{"id":1,"name":"Graphite","center":284.5}]}
Modal final: {"notes":["Auto-fit complete. χ²ᵣ = ?"],"cancels":["/api/fit/cancel/J1","/api/fit/cancel/J1"],"applied":1,"restores":0,"hides":1,"spinner":false,"starts":2}
Tab A discard while tab B running: {"notes":["Fit result discarded because you switched tabs during the fit."],"cancels":["/api/fit/cancel/J1"],"applied":0,"restores":0,"hides":1,"spinner":false,"starts":2}

exec
/bin/zsh -lc "sed -n '5830,5897p' templates/index.html; sed -n '180,218p' tests/test_fit_start_poll.py; cat scripts/public_fit_poll_check.py; rg -n '"'^def _prepare_fit_request|''^def _run_fit_outcome'"' app.py; git log -3 --oneline" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
      const lbl = p.label; // e.g. "2p3/2 → 2p1/2"
      const parts = lbl.split(' \u2192 ');
      return isSecond ? (parts[1] || 'b') : (parts[0] || 'a');
    }
    const lbl1 = elemName ? (elemName + ' ' + _spinOrbitLabel(presetKey, false)) : ('Peak ' + state.nextId + ' a');
    const lbl2 = elemName ? (elemName + ' ' + _spinOrbitLabel(presetKey, true)) : ('Peak ' + state.nextId + ' b');

    const p1 = addPeak({
      name: lbl1,
      center: Math.round(beValue * 100) / 100,
      amplitude: Math.round(netAmplitude)
    });
    const p2 = defaultPeak({
      name: lbl2,
      center: Math.round((beValue + preset.splitting) * 100) / 100,
      amplitude: Math.round(netAmplitude * preset.ratio),
      shape: p1.shape,
      color: p1.color,
      linked: p1.id,
      linkOffset: preset.splitting,
      linkRatio: preset.ratio
    });
    state.peaks.push(p2);
    renderPeakList();
    updatePlot();
    notify('Multiplet pair placed at ' + beValue.toFixed(2) + ' eV (' + presetKey + ')', 'green');
  }

  // Exit placement mode after placing
  togglePlaceMode(placeMode);
}

// Global keyboard shortcuts
document.addEventListener('keydown', function(e) {
  // Ctrl+K / Ctrl+P: spectrum switcher (works even from input fields)
  if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'p')) {
    e.preventDefault();
    _ssToggle();
    return;
  }

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
HEARTBEAT_LOST_S = 30.0      # as the page: a record whose heartbeat stopped is a lost fit
DEADLINE_S = 20 * 60         # per target: never poll forever
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
        if rec.get("status") not in ("running", "queued"):
            break
        hb = rec.get("heartbeat_age_sec")
        if isinstance(hb, (int, float)) and hb > HEARTBEAT_LOST_S:
            rec = {"status": "lost", "error": f"heartbeat stopped {hb:.0f} s ago (worker restarted?)"}
            break
        if time.time() - t0 > DEADLINE_S:
            _req(base + f"/api/fit/cancel/{job}", b"", method="POST")
            rec = {"status": "deadline", "error": f"no result after {DEADLINE_S} s"}
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
65:def _prepare_fit_request(app, body):
144:def _run_fit_outcome(app, fit_args, cancel=None):
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-NJ8yBxAM' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-RGi4BmwD' (errno=Operation not permitted)
4046ffb fix(unit 2): Codex round 2 (NO-GO x2) - fit operations claimed before the first await; supersession checked after every await; admission has one owner
5e26c36 Merge branch 'fix-acceptance-holes' into fix-fit-start-poll
0e62a7f fix(unit 2): Codex round 1 (NO-GO x2) - supersede per tab, bounded concurrency, cancellation normalised, checker deadline

codex
The modal race reproduced: Auto-Fit A opens confirmation, Run Fit B starts, then confirming A cancels B and lets A apply its result. A two-tab probe also showed A’s discard hiding B’s active spinner. All 88 focused JavaScript tests pass; they don’t exercise these caller-level interleavings. I’m finishing the server fault checks and checking that the race tests detect the old behavior.
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c '
import ast,pathlib,threading,time,types,logging,uuid,subprocess
logging.disable(logging.CRITICAL)
text=pathlib.Path(\"app.py\").read_text()
def build(source, failure=None):
    tree=ast.parse(source)
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in [\"_fit_job_admit\",\"_fit_job_release\",\"_fit_job_start\"]]
    route=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name==\"fit_start\")
    route.decorator_list=[];nodes.append(route)
    records={};markers={};threads=[];runs=[]
    class Marker:
        def __init__(self,j,k):self.key=(j,k)
        def touch(self):
            if failure==\"marker\":raise OSError(\"marker fault\")
            markers[self.key]=time.time()
        def exists(self):return self.key in markers
        def stat(self):return types.SimpleNamespace(st_mtime=markers[self.key])
        def unlink(self,**kw):markers.pop(self.key,None)
    class Thread(threading.Thread):
        def start(self):
            hb=self.name.startswith(\"fit-hb-\")
            if failure==\"heartbeat\" and hb or failure==\"worker\" and not hb:raise RuntimeError(\"start fault\")
            threads.append(self);super().start()
    def write(j,f,r):
        if failure==\"record\":raise RuntimeError(\"record fault\")
        records[j]=dict(r)
    def sweep(f):
        if failure==\"sweep\":raise RuntimeError(\"sweep fault\")
    def run(app,args,cancel):
        runs.append(1);return 200,{\"success\":True}
    ns=dict(threading=types.SimpleNamespace(Lock=threading.Lock,Event=threading.Event,Thread=Thread),
       _FIT_JOB_ADMIT_LOCK=threading.Lock(),_FIT_JOB_ADMITTED=[2],FIT_JOB_MAX_ADMITTED=6,
       _FIT_JOB_RUN_SLOTS=threading.BoundedSemaphore(1),FIT_JOB_HEARTBEAT_SEC=.005,FIT_JOB_ABANDON_SEC=180,
       _fit_job_marker=lambda j,f,k:Marker(j,k),_fit_job_write=write,
       _sweep_expired_jobs=sweep,_sweep_fit_job_markers=lambda f:None,time=time,logging=logging,uuid=uuid,
       app=types.SimpleNamespace(config={\"UPLOAD_FOLDER\":\"unused\"}),request=types.SimpleNamespace(get_json=lambda **k:{}),
       _prepare_fit_request=lambda a,b:({},None),_run_fit_outcome=run,_err=lambda msg,status=400:(msg,status),jsonify=lambda x:x)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),\"<actual server functions>\",\"exec\"),ns)
    return ns,threads,runs
for f in [\"sweep\",\"record\",\"marker\",\"heartbeat\",\"worker\",None]:
    ns,ts,runs=build(text,f)
    try:ns[\"fit_start\"]()
    except (RuntimeError,OSError):pass
    for t in ts:t.join(2)
    assert ns[\"_FIT_JOB_ADMITTED\"][0]==2,(f,ns[\"_FIT_JOB_ADMITTED\"])
    assert len(runs)==(0 if f else 1),(f,runs)
    assert not any(t.is_alive() for t in ts)
    print(\"current admission\",f or \"success\",\"counter=2; worker runs=\"+str(len(runs)))
old=subprocess.check_output([\"git\",\"show\",\"HEAD~1:app.py\"],text=True,stderr=subprocess.DEVNULL)
ns,ts,runs=build(old,\"heartbeat\")
try:ns[\"fit_start\"]()
except RuntimeError:pass
for t in ts:t.join(2)
print(\"old heartbeat failure counter:\",ns[\"_FIT_JOB_ADMITTED\"][0],\"expected 2; worker runs:\",len(runs))
assert ns[\"_FIT_JOB_ADMITTED\"][0]==1
ns,ts,runs=build(text)
ns[\"_FIT_JOB_ADMITTED\"][0]=0
barrier=threading.Barrier(30);got=[];lock=threading.Lock()
def admit():
    barrier.wait()
    a=ns[\"_fit_job_admit\"]()
    with lock:got.append(a)
workers=[threading.Thread(target=admit) for i in range(30)]
for t in workers:t.start()
for t in workers:t.join()
assert sum(got)==6 and ns[\"_FIT_JOB_ADMITTED\"][0]==6
print(\"30 simultaneous admission attempts: exactly 6 accepted\")
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 76ms:
current admission sweep counter=2; worker runs=0
current admission record counter=2; worker runs=0
current admission marker counter=2; worker runs=0
current admission heartbeat counter=2; worker runs=0
current admission worker counter=2; worker runs=0
current admission success counter=2; worker runs=1
old heartbeat failure counter: 1 expected 2; worker runs: 1
30 simultaneous admission attempts: exactly 6 accepted

exec
/bin/zsh -lc "node -e '
const fs=require('\\''fs'\\''),cp=require('\\''child_process'\\'');
const current=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const old=cp.execFileSync('\\''git'\\'',['\\''show'\\'','\\''HEAD~1:templates/index.html'\\''],{encoding:'\\''utf8'\\'',stdio:['\\''ignore'\\'','\\''pipe'\\'','\\''ignore'\\'']});
const extract=(html,name)=>{const lines=html.split('\\''\\n'\\''),s=lines.findIndex(l=>new RegExp('\\''"'^(async )?function '"'\\''+name+'\\''\\\\('\\'').test(l));let n=0,seen=false;for(let i=s;i<lines.length;i++){for(const c of lines[i]){if(c==='\\''{'\\''){n++;seen=true;}if(c==='\\''}'\\'')n--;}if(seen&&"'!n)return lines.slice(s,i+1).join('"'\\''\\n'\\'');}throw name;};
const ok=x=>({ok:true,text:async()=>JSON.stringify(x)});
const defer=()=>{let r;return {p:new Promise(a=>r=a),r:x=>r(x)}};
function make(html,fetch){
 const modern=html===current;
 const names=['\\''_cancelFitJob'\\'','\\''_fitHttpError'\\'','\\''_readFitReply'\\'','\\''_serverFitJob'\\'',...(modern?['\\''_claimFitOp'\\'','\\''_fitOpCurrent'\\'']:[])];
 const defs='\\''const FIT_POLL_MS=500,FIT_POLL_TRANSPORT_RETRIES=5,FIT_HEARTBEAT_LOST_SEC=30; const _runningFitJobs=new Set();'\\''+
  (modern?'\\''let _fitOpSeq=0;const _fitOpByOwner=new WeakMap();'\\'':'\\''const _fitJobByOwner=new WeakMap();function _claimFitOp(owner){return {owner};}'\\'');
 return new Function('\\''fetch'\\'','\\''setTimeout'\\'',defs+names.map(n=>extract(html,n)).join('\\''\\n'\\'')+'\\'';return {claim:_claimFitOp,job:(r,g)=>_serverFitJob(r,{...g,owner:g.op.owner})};'\\'')(fetch,f=>setImmediate(f));
}
(async()=>{
 for(const [label,html] of [['\\''old'\\'',old],['\\''current'\\'',current]]){
  const gate=defer(),cancels=[];let n=0;const owner={};
  const h=make(html,async u=>{if(u.endsWith('\\''/start'\\'')){const j='\\''J'\\''+(++n);if(n===1)await gate.p;return ok({job_id:j});}if(u.includes('\\''/cancel/'\\'')){cancels.push(u);return ok({});}return ok({status:'\\''done'\\'',result:{which:u.split('\\''/'\\'').pop()}});});
  const a=h.job({},{op:h.claim(owner)});await new Promise(r=>setImmediate(r));
  const b=await h.job({},{op:h.claim(owner)});gate.r();console.log(label,'\\''reversed responses'\\'',JSON.stringify({a:await a,b,cancels}));
  for(const status of ['\\''done'\\'','\\''cancelled'\\'','\\''error'\\'','\\''timeout'\\'']){
   const polled=defer(),release=defer(),o={};
   const k=make(html,async u=>{if(u.endsWith('\\''/start'\\''))return ok({job_id:'\\''A'\\''});if(u.includes('\\''/cancel/'\\''))return ok({});polled.r();await release.p;if(status==='\\''timeout'\\'')throw Object.assign(new Error('\\''timeout'\\''),{name:'\\''AbortError'\\''});return ok({status,result:{stale:true},error:'\\''oops'\\'',http_status:500});});
   const p=k.job({},{op:k.claim(o)}).catch(e=>({threw:e.message}));await polled.p;k.claim(o);
   // On old code a successor only claims ownership when its start response registers.
   if(label==='\\''old'\\''){const b=k.job({},{op:{owner:o},abandoned:()=> '\\''tab'\\''});await new Promise(r=>setImmediate(r));await b;}
   release.r();console.log(label,'\\''late '\\''+status,JSON.stringify(await p));
  }
 }
})();
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 141ms:
old late cancelled {"threw":"The fit was stopped on the server before it finished. Run it again."}
old late error {"threw":"oops"}
old late timeout {"threw":"timeout"}
current reversed responses {"a":{"_abandoned":"superseded"},"b":{"which":"J2"},"cancels":["/api/fit/cancel/J1"]}
current late done {"_abandoned":"superseded"}
current late cancelled {"_abandoned":"superseded"}
current late error {"_abandoned":"superseded"}
current late timeout {"_abandoned":"superseded"}

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c '
import sys,tempfile,time,ast,pathlib,json
tempfile.tempdir=\"/tmp\"
sys.modules[\"matplotlib\"]=None
import fitting,numpy as np
tree=ast.parse(pathlib.Path(\"tests/test_fit_start_poll.py\").read_text())
wanted=[]
for n in tree.body:
    if isinstance(n,ast.FunctionDef) and n.name in [\"_gl\",\"_specs\"]:wanted.append(n)
    if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in [\"SLOW\",\"COMPS\"] for t in n.targets):wanted.append(n)
ns={\"np\":np};exec(compile(ast.Module(body=wanted,type_ignores=[]),\"<test data>\",\"exec\"),ns)
x=np.linspace(281,292,300);y=300+sum(ns[\"_gl\"](x,c,a,w) for c,a,w in ns[\"SLOW\"])
for method in [\"leastsq\",\"least_squares\",\"nelder\",\"differential_evolution\",\"basinhopping\"]:
    start=time.monotonic()
    try:fitting.run_fit(x,y,ns[\"_specs\"](ns[\"SLOW\"]),background_method=\"linear\",n_perturb=0,fit_kws={\"method\":method},cancel=lambda:True)
    except fitting.FitCancelled:pass
    else:raise AssertionError(method)
    assert fitting._cancel_kw()=={}
    print(method,\"cancelled and thread-local cleared\",round(time.monotonic()-start,3),flush=True)
x=np.linspace(281,292,100);y=300+sum(ns[\"_gl\"](x,c,a,w) for c,a,w in ns[\"COMPS\"])
kw=dict(background_method=\"linear\",n_perturb=0,fit_kws={\"method\":\"leastsq\"})
a=fitting.run_fit(x,y,ns[\"_specs\"](ns[\"COMPS\"]),**kw)
b=fitting.run_fit(x,y,ns[\"_specs\"](ns[\"COMPS\"]),cancel=lambda:False,**kw)
assert json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True)
print(\"Levenberg-Marquardt sync vs cancel-hook: byte-identical\",flush=True)
old=fitting._run_fit_impl
error=ValueError(\"unrelated\")
def bad(*a,**k):raise error
fitting._run_fit_impl=bad
try:fitting.run_fit(cancel=lambda:True)
except ValueError as e:assert e is error
else:raise AssertionError(\"swallowed\")
finally:fitting._run_fit_impl=old
assert fitting._cancel_kw()=={}
print(\"unobserved cancellation preserves unrelated errors\")
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 1738ms:
leastsq cancelled and thread-local cleared 0.012
least_squares cancelled and thread-local cleared 0.011
nelder cancelled and thread-local cleared 0.009
differential_evolution cancelled and thread-local cleared 0.013
basinhopping cancelled and thread-local cleared 0.027
Levenberg-Marquardt sync vs cancel-hook: byte-identical
unobserved cancellation preserves unrelated errors

exec
/bin/zsh -lc "git status --short; nl -ba tests/js/fit_start_poll.test.js | tail -n 28; nl -ba templates/index.html | sed -n '7604,7617p'; nl -ba templates/index.html | sed -n '7687,7696p'; nl -ba templates/index.html | sed -n '8224,8236p'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-PH1M2NsV' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-loX6HUjW' (errno=Operation not permitted)
?? docs/autofit/codex/fit_start_poll_r3_verdict_runA.md
?? docs/autofit/codex/fit_start_poll_r3_verdict_runB.md
   216	    if (url === '/api/fit/start') return ok({ job_id: 'J1' }, 202);
   217	    if (url.startsWith('/api/fit/progress/')) { polled.res(); await release.p; signal.aborted = true;
   218	      signal.reason = Object.assign(new Error('timeout'), { name: 'AbortError' }); throw signal.reason; }
   219	    return ok({});
   220	  };
   221	  const { _serverFitJob, _claimFitOp } = makeAsync(fetch);
   222	  const owner = {};
   223	  const a = _serverFitJob({}, { op: _claimFitOp(owner), signal });
   224	  await polled.p;
   225	  _claimFitOp(owner);
   226	  release.res();
   227	  assert.deepStrictEqual(await a, { _abandoned: 'superseded' });
   228	});
   229	
   230	test('both callers claim their operation before the first await and do nothing at all when superseded', () => {
   231	  const run = extractFn('runFit');
   232	  assert.ok(run.indexOf('fitOp = _claimFitOp(fittingTab);') > 0 && run.indexOf('fitOp = _claimFitOp(fittingTab);') < run.indexOf('await uploadToBackend('), 'runFit claims before its first await');
   233	  assert.ok(!/\bawait\s+[\w(]/.test(run.slice(0, run.indexOf('fitOp = _claimFitOp(fittingTab);')).replace(/\/\/[^\n]*/g, '')), 'no code await before the claim');
   234	  assert.match(run, /op: fitOp,/);
   235	  assert.match(run, /if \(json && json\._abandoned === 'superseded'\) return;/);
   236	  assert.match(run, /\} catch \(e\) \{\n(\s*\/\/[^\n]*\n)*\s*if \(fitOp && !_fitOpCurrent\(fitOp\)\) return;/, 'runFit: a superseded operation never reaches the local fallback');
   237	  const af = extractFn('runAutoFitC1sGraphite');
   238	  const claim = af.indexOf('afOp = _claimFitOp(fittingTab);');
   239	  assert.ok(claim > 0 && claim < af.indexOf('await uploadToBackend('), 'Auto-Fit claims before its first server await');
   240	  assert.match(af, /op: afOp,/);
   241	  assert.match(af, /if \(json && json\._abandoned === 'superseded'\) return;/);
   242	  assert.match(af, /if \(afOp && !_fitOpCurrent\(afOp\)\) return;/, 'Auto-Fit: no rollback when superseded');
   243	});
  7604	  // OWNER FIRST: the confirmation below is an await; the tab that is active
  7605	  // when it resolves may not be the one the user asked to auto-fit.
  7606	  const fittingTab = _opOwner();
  7607	  if (!fittingTab) { notify('No active spectrum tab.', 'amber'); return; }
  7608	  // Confirmation if existing peaks
  7609	  if (state.peaks.length >= 1) {
  7610	    const proceed = await _showAutoFitConfirmModal(state.peaks.length);
  7611	    if (!proceed) return;
  7612	    if (!_ownerActive(fittingTab)) {
  7613	      notify('Auto-fit cancelled — the tab changed while the confirmation was open.', 'amber');
  7614	      return;
  7615	    }
  7616	  }
  7617	
  7687	    // upload must not send another tab's id).
  7688	    const anchorId = String((state.peaks.find(p => p.name === 'Graphite') || state.peaks[0]).id);
  7689	    // the model and its fit context as sent (F1, Codex round 1): a result must
  7690	    // not be applied, and stamped current, over a model edited while it ran
  7691	    const ctxAtRequest = _startsLiveKey();
  7692	    afOp = _claimFitOp(fittingTab);   // unit 2: before the first server await; the newest claim for a tab is current
  7693	    // Build peak specs and overlay the per-peak bounds we attached in buildAutoFitModel.
  7694	    const peakSpecs = state.peaks.map(p => {
  7695	      const spec = peakToBackendSpec(p);
  7696	      if (Number.isFinite(p._afCenterMin)) spec.center_min = p._afCenterMin;
  8224	    const json = await _serverFitJob(fitReq, {
  8225	      op: fitOp,
  8226	      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
  8227	    });
  8228	    if (json && json._abandoned === 'superseded') return;   // a newer fit on this tab owns the spinner and the result
  8229	    if (json && json._abandoned === 'tab') {
  8230	      _hideFitSpinner();
  8231	      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
  8232	      notify('Fit result discarded because you switched tabs during the fit.', 'amber');
  8233	      return;
  8234	    }
  8235	    if (json && json._abandoned === 'model') {
  8236	      _hideFitSpinner();

codex
1. **MAJOR — Auto-Fit claims ownership after its first await.** [templates/index.html:7692](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7692)  
   Reproduced with the actual callers: open Auto-Fit A’s confirmation, press Ctrl/Cmd+F to start Run Fit B, then confirm A. A replaces the model, claims ownership and cancels B; A’s result applies. The check after the modal verifies only tab identity. Establish invocation identity before the modal await and reject superseded continuations before model mutation. The test at [fit_start_poll.test.js:239](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/tests/js/fit_start_poll.test.js:239) checks only placement before upload, missing this first await.

2. **MINOR — An abandoned tab’s fit hides another tab’s active spinner.** [templates/index.html:8230](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8230)  
   Reproduced: start A, switch tabs, start B before A’s next poll. A detects tab abandonment and unconditionally hides the shared spinner, re-enables Run Fit and writes “Fit discarded” while B remains running. Auto-Fit has the same unconditional cleanup. Bind shared fitting UI cleanup to the operation that currently owns it.

Validation: **88 focused JavaScript tests passed**. Comparative probes confirmed the previous response-order, late-poll and timeout failures on the old code and their correction here. Admission fault probes passed for sweeps, initial record/marker writes and either thread startup; 30 concurrent admission attempts accepted exactly six. Cancellation passed across all five solvers; Levenberg–Marquardt results with and without the cancellation hook were byte-identical.

No files changed. Filesystem-backed pytest and full timing acceptance were not rerun.

**VERDICT: NO-GO**
tokens used
84,597
1. **MAJOR — Auto-Fit claims ownership after its first await.** [templates/index.html:7692](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7692)  
   Reproduced with the actual callers: open Auto-Fit A’s confirmation, press Ctrl/Cmd+F to start Run Fit B, then confirm A. A replaces the model, claims ownership and cancels B; A’s result applies. The check after the modal verifies only tab identity. Establish invocation identity before the modal await and reject superseded continuations before model mutation. The test at [fit_start_poll.test.js:239](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/tests/js/fit_start_poll.test.js:239) checks only placement before upload, missing this first await.

2. **MINOR — An abandoned tab’s fit hides another tab’s active spinner.** [templates/index.html:8230](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8230)  
   Reproduced: start A, switch tabs, start B before A’s next poll. A detects tab abandonment and unconditionally hides the shared spinner, re-enables Run Fit and writes “Fit discarded” while B remains running. Auto-Fit has the same unconditional cleanup. Bind shared fitting UI cleanup to the operation that currently owns it.

Validation: **88 focused JavaScript tests passed**. Comparative probes confirmed the previous response-order, late-poll and timeout failures on the old code and their correction here. Admission fault probes passed for sweeps, initial record/marker writes and either thread startup; 30 concurrent admission attempts accepted exactly six. Cancellation passed across all five solvers; Levenberg–Marquardt results with and without the cancellation hook were byte-identical.

No files changed. Filesystem-backed pytest and full timing acceptance were not rerun.

**VERDICT: NO-GO**
