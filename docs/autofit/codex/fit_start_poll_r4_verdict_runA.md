OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0e277-8477-7360-a536-b7f23341e024
--------
user
Re-review unit 2 (long fits via start-then-poll), round 4 (the last allowed): branch fix-fit-start-poll. The round-3 fixes are the latest commit (git diff HEAD~1..HEAD); the whole unit is git diff fix-acceptance-holes..HEAD. Earlier verdicts: docs/autofit/codex/fit_start_poll_verdict_run{A,B}.md, _r2_, _r3_; the round-1 prompt holds the brief, design, sites and acceptance; plan docs/superpowers/plans/2026-09-27-long-fits-start-poll.md section 6 lists every finding and fix. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

ROUND-3 FINDINGS AND FIXES (plan section 6, verbatim):

**Round 3 — run A GO, run B NO-GO** (`fit_start_poll_r3_verdict_run{A,B}.md`;
both confirmed round 2's response-order, late-poll, timeout and admission
fixes on the old code vs the new):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (B): Auto-Fit claimed its operation AFTER its confirmation modal (its first await): a Run Fit pressed while the modal was open was cancelled when the student confirmed, and the older Auto-Fit's result applied | an operation is NUMBERED at the press (`_newFitOp`, before the modal) and INSTALLED as the tab's current one after it (`_installFitOp`), only if no newer operation claimed the tab meanwhile — otherwise the confirmed Auto-Fit returns having changed nothing (no snapshot, no request). Claiming at the press would have cancelled a running Run Fit merely for opening the modal. Run Fit, which has no modal, claims = numbers + installs at once. |
| 2 | MINOR (A, B): the fit spinner is page-wide; a fit discarded on tab A hid tab B's running spinner, re-enabled Run Fit and cleared the in-flight flag | the spinner belongs to the operation that showed it (`_fitSpinnerOp`); every hide after a caller's claim is `_hideFitSpinnerFor(op)`, a no-op for any other operation |

TRY TO BREAK
a. Numbered-then-installed operations: every caller path (Run Fit, "Use this solution", Auto-Fit with and without its modal — no peaks = no modal), the install check before ANY change (snapshot, provisional shift, model build, upload), a cancelled modal (the numbered op is never installed and changes nothing), two Auto-Fits, an Auto-Fit numbered BEFORE a Run Fit but confirmed AFTER it, the seq comparison.
b. Spinner ownership: every show and hide in both callers (incl. early returns before the claim, the success path, errors, discards, supersession), Batch Fit or Find Peaks spinners if they share it, a tab closed mid-fit.
c. Anything earlier rounds verified that these changes touched; the six browser scenarios the plan records.
d. The tests: real and non-vacuous.

Finish with VERDICT: GO or VERDICT: NO-GO.
codex
I’ll read the brief and prior findings, trace the operation and spinner changes across every caller, then run focused checks and give a verdict within this review.
exec
/bin/zsh -lc "pwd && rg --files -g 'AGENTS.md' -g '*fit_start_poll*' -g '*long-fits-start-poll*' -g '*round*' docs . 2>/dev/null" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
docs/superpowers/plans/2026-09-02-task4-background-twin-parity.md
docs/superpowers/plans/2026-04-07-manual-spline-background.md
docs/superpowers/plans/2026-09-02-task1-background-residual-diagnosis.md
docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md
docs/superpowers/plans/2026-09-27-long-fits-start-poll.md
./docs/comms/2026-09-03-background-window-fix-student-note.md
./docs/superpowers/plans/2026-09-02-task4-background-twin-parity.md
./docs/superpowers/plans/2026-04-07-manual-spline-background.md
./docs/superpowers/plans/2026-09-02-task1-background-residual-diagnosis.md
./docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md
./docs/superpowers/plans/2026-09-27-long-fits-start-poll.md
docs/comms/2026-09-03-background-window-fix-student-note.md
./tests/test_tougaard_background.py
./tests/test_browser_overlay_zip_roundtrip.py
./tests/test_fit_start_poll.py
./tests/test_background_n_avg.py
./tests/autofit/test_browser_schema_roundtrip.py
./tests/js/lineshape_roundtrip_backend.py
./tests/js/fit_start_poll.test.js
./tests/js/lineshape_roundtrip.test.js
./tests/js/shape_switch_roundtrip.test.js
docs/autofit/codex/plain_english_pass_verdict_round2_runB.md
docs/autofit/codex/full_window_crop_fix_verdict_round2_runA.md
docs/autofit/codex/c1s_badge_fix_verdict_round5_runB.md
./docs/autofit/codex/c1s_badge_fix_verdict_round5_runB.md
docs/autofit/codex/self_citation_removal_verdict_round4_runA.md
docs/autofit/codex/fp_periodic_table_picker_verdict_round1_runB.md
./docs/autofit/codex/self_citation_removal_verdict_round4_runA.md
docs/autofit/codex/self_citation_removal_verdict_round1_runB.md
./docs/autofit/codex/full_window_crop_fix_verdict_round2_runA.md
docs/autofit/codex/fit_start_poll_r3_verdict_runB.md
docs/autofit/codex/tooltip_markup_leak_verdict_round2_runB.md
./docs/autofit/codex/plain_english_pass_verdict_round2_runB.md
docs/autofit/codex/fit_full_window_verdict_round1_runA.md
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md
docs/autofit/codex/region_provenance_honesty_verdict_round2_runB.md
docs/autofit/codex/c1s_badge_fix_verdict_round1_runA.md
./docs/autofit/codex/self_citation_removal_verdict_round1_runB.md
./docs/autofit/codex/fp_periodic_table_picker_verdict_round1_runB.md
docs/autofit/codex/tooltip_markup_leak_verdict_round3_runB.md
./docs/autofit/codex/fit_start_poll_r4_verdict_runB.md
./docs/autofit/codex/fit_full_window_verdict_round1_runA.md
./docs/autofit/codex/tooltip_markup_leak_verdict_round2_runB.md
./docs/autofit/codex/fit_start_poll_r3_verdict_runB.md
./docs/autofit/codex/c1s_badge_fix_verdict_round1_runA.md
./docs/autofit/codex/region_provenance_honesty_verdict_round2_runB.md
./docs/autofit/codex/tooltip_markup_leak_verdict_round3_runB.md
docs/autofit/codex/fit_full_window_verdict_round3_runA.md
docs/autofit/codex/plain_english_pass_verdict_round3_runB.md
docs/autofit/codex/c1s_badge_fix_verdict_round4_runB.md
docs/autofit/codex/full_window_crop_fix_verdict_round3_runA.md
docs/autofit/codex/full_window_crop_fix_verdict_round4_runB.md
docs/autofit/codex/tooltip_markup_leak_verdict_round1_runB.md
docs/autofit/codex/c1s_badge_fix_verdict_round3_runA.md
./docs/autofit/codex/full_window_crop_fix_verdict_round3_runA.md
./docs/autofit/codex/c1s_badge_fix_verdict_round4_runB.md
docs/autofit/codex/fp_periodic_table_picker_verdict_round2_runB.md
docs/autofit/codex/self_citation_removal_verdict_round2_runB.md
./docs/autofit/codex/plain_english_pass_verdict_round3_runB.md
docs/autofit/codex/full_window_crop_fix_verdict_round1_runA.md
docs/autofit/codex/c1s_badge_fix_verdict_round6_runB.md
docs/autofit/codex/c1s_badge_fix_verdict_round2_runB.md
docs/autofit/codex/fit_start_poll_review_prompt.txt
docs/autofit/codex/fit_start_poll_r2_verdict_runA.md
docs/autofit/codex/fit_full_window_verdict_round2_runB.md
docs/autofit/codex/fit_start_poll_recheck_prompt.txt
docs/autofit/codex/findpeaks_unit3_verdict_round2.md
docs/autofit/codex/region_provenance_honesty_verdict_round1_runB.md
docs/autofit/codex/self_citation_removal_verdict_round3_runB.md
docs/autofit/codex/c1s_badge_fix_verdict_round2_runA.md
docs/autofit/codex/fit_start_poll_r2_verdict_runB.md
docs/autofit/codex/fit_full_window_verdict_round2_runA.md
docs/autofit/codex/fit_start_poll_recheck2_prompt.txt
docs/autofit/codex/findpeaks_unit3_verdict_round1.md
docs/autofit/codex/fit_start_poll_verdict_runA.md
docs/autofit/codex/plain_english_pass_verdict_round1_runB.md
docs/autofit/codex/self_citation_removal_verdict_round2_runA.md
docs/autofit/codex/fp_periodic_table_picker_verdict_round2_runA.md
docs/autofit/codex/tooltip_markup_leak_verdict_round1_runA.md
docs/autofit/codex/c1s_badge_fix_verdict_round3_runB.md
docs/autofit/codex/full_window_crop_fix_verdict_round4_runA.md
docs/autofit/codex/fit_full_window_verdict_round3_runB.md
docs/autofit/codex/region_provenance_honesty_verdict_round1_runA.md
docs/autofit/codex/self_citation_removal_verdict_round3_runA.md
docs/autofit/codex/fit_start_poll_r4_verdict_runA.md
docs/autofit/codex/plain_english_pass_verdict_round1_runA.md
docs/autofit/codex/fit_start_poll_verdict_runB.md
docs/autofit/codex/c1s_badge_fix_verdict_round6_runA.md
docs/autofit/codex/full_window_crop_fix_verdict_round1_runB.md
docs/autofit/codex/region_provenance_honesty_verdict_round2_runA.md
docs/autofit/codex/fit_full_window_verdict_round1_runB.md
docs/autofit/codex/tooltip_markup_leak_verdict_round3_runA.md
docs/autofit/codex/c1s_badge_fix_verdict_round1_runB.md
./docs/autofit/codex/self_citation_removal_verdict_round3_runB.md
./docs/autofit/codex/c1s_badge_fix_verdict_round2_runA.md
./docs/autofit/codex/fit_start_poll_r2_verdict_runB.md
./docs/autofit/codex/fit_full_window_verdict_round2_runA.md
./docs/autofit/codex/fit_start_poll_recheck2_prompt.txt
./docs/autofit/codex/findpeaks_unit3_verdict_round1.md
./docs/autofit/codex/fit_start_poll_verdict_runA.md
./docs/autofit/codex/plain_english_pass_verdict_round1_runB.md
./docs/autofit/codex/c1s_badge_fix_verdict_round6_runB.md
./docs/autofit/codex/full_window_crop_fix_verdict_round1_runA.md
./docs/autofit/codex/self_citation_removal_verdict_round2_runB.md
./docs/autofit/codex/fp_periodic_table_picker_verdict_round2_runB.md
./docs/autofit/codex/c1s_badge_fix_verdict_round3_runA.md
./docs/autofit/codex/full_window_crop_fix_verdict_round4_runB.md
./docs/autofit/codex/tooltip_markup_leak_verdict_round1_runB.md
./docs/autofit/codex/fit_full_window_verdict_round3_runA.md
./docs/autofit/codex/self_citation_removal_verdict_round3_runA.md
./docs/autofit/codex/c1s_badge_fix_verdict_round2_runB.md
./docs/autofit/codex/fit_start_poll_review_prompt.txt
./docs/autofit/codex/fit_start_poll_r2_verdict_runA.md
./docs/autofit/codex/fit_full_window_verdict_round2_runB.md
./docs/autofit/codex/fit_start_poll_recheck_prompt.txt
./docs/autofit/codex/findpeaks_unit3_verdict_round2.md
./docs/autofit/codex/region_provenance_honesty_verdict_round1_runB.md
./docs/autofit/codex/tooltip_markup_leak_verdict_round1_runA.md
./docs/autofit/codex/c1s_badge_fix_verdict_round3_runB.md
./docs/autofit/codex/full_window_crop_fix_verdict_round4_runA.md
./docs/autofit/codex/fit_full_window_verdict_round3_runB.md
./docs/autofit/codex/region_provenance_honesty_verdict_round1_runA.md
./docs/autofit/codex/self_citation_removal_verdict_round2_runA.md
./docs/autofit/codex/fp_periodic_table_picker_verdict_round2_runA.md
./docs/autofit/codex/full_window_crop_fix_verdict_round1_runB.md
./docs/autofit/codex/c1s_badge_fix_verdict_round6_runA.md
docs/autofit/codex/full_window_crop_fix_verdict_round3_runB.md
docs/autofit/codex/c1s_badge_fix_verdict_round4_runA.md
docs/autofit/codex/tooltip_markup_leak_verdict_round2_runA.md
docs/autofit/codex/fit_start_poll_r3_verdict_runA.md
docs/autofit/codex/fp_periodic_table_picker_verdict_round1_runA.md
docs/autofit/codex/self_citation_removal_verdict_round1_runA.md
docs/autofit/codex/plain_english_pass_verdict_round2_runA.md
docs/autofit/codex/full_window_crop_fix_verdict_round2_runB.md
docs/autofit/codex/c1s_badge_fix_verdict_round5_runA.md
docs/autofit/codex/self_citation_removal_verdict_round4_runB.md
docs/autofit/codex/plain_english_pass_verdict_round3_runA.md
docs/autofit/codex/fit_start_poll_recheck3_prompt.txt
./docs/autofit/codex/full_window_crop_fix_verdict_round3_runB.md
./docs/autofit/codex/c1s_badge_fix_verdict_round1_runB.md
./docs/autofit/codex/tooltip_markup_leak_verdict_round3_runA.md
./docs/autofit/codex/region_provenance_honesty_verdict_round2_runA.md
./docs/autofit/codex/fit_full_window_verdict_round1_runB.md
./docs/autofit/codex/fit_start_poll_r4_verdict_runA.md
./docs/autofit/codex/plain_english_pass_verdict_round1_runA.md
./docs/autofit/codex/fit_start_poll_verdict_runB.md
./docs/autofit/codex/self_citation_removal_verdict_round4_runB.md
./docs/autofit/codex/plain_english_pass_verdict_round3_runA.md
./docs/autofit/codex/fit_start_poll_recheck3_prompt.txt
./docs/autofit/codex/c1s_badge_fix_verdict_round4_runA.md
./docs/autofit/codex/full_window_crop_fix_verdict_round2_runB.md
./docs/autofit/codex/c1s_badge_fix_verdict_round5_runA.md
./docs/autofit/codex/plain_english_pass_verdict_round2_runA.md
./docs/autofit/codex/tooltip_markup_leak_verdict_round2_runA.md
./docs/autofit/codex/fit_start_poll_r3_verdict_runA.md
./docs/autofit/codex/fp_periodic_table_picker_verdict_round1_runA.md
./docs/autofit/codex/self_citation_removal_verdict_round1_runA.md

exec
/bin/zsh -lc 'git status --short && git branch --show-current && git log -4 --oneline && git diff --stat HEAD~1..HEAD && git diff --stat fix-acceptance-holes..HEAD' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 110ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-34dJFhAF' (errno=Operation not permitted)
 .../codex/fit_start_poll_r3_verdict_runA.md        | 4689 ++++++++++++++++++
 .../codex/fit_start_poll_r3_verdict_runB.md        | 5139 ++++++++++++++++++++
 .../codex/fit_start_poll_recheck3_prompt.txt       |   20 +
 .../plans/2026-09-27-long-fits-start-poll.md       |    9 +
 templates/index.html                               |   68 +-
 tests/js/fit_acceptance.test.js                    |    2 +-
 tests/js/fit_start_poll.test.js                    |   69 +-
 tests/js/per_tab_state.test.js                     |    2 +-
 tests/js/stale_statistics.test.js                  |    2 +-
 9 files changed, 9969 insertions(+), 31 deletions(-)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-PmzmVXjS' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-S0ygvPSG' (errno=Operation not permitted)
 CLAUDE.md                                          |    28 +
 app.py                                             |   430 +-
 .../codex/fit_start_poll_r2_verdict_runA.md        |  4924 ++++++
 .../codex/fit_start_poll_r2_verdict_runB.md        | 15995 +++++++++++++++++++
 .../codex/fit_start_poll_r3_verdict_runA.md        |  4689 ++++++
 .../codex/fit_start_poll_r3_verdict_runB.md        |  5139 ++++++
 .../codex/fit_start_poll_recheck2_prompt.txt       |    26 +
 .../codex/fit_start_poll_recheck3_prompt.txt       |    20 +
 .../codex/fit_start_poll_recheck_prompt.txt        |    24 +
 .../autofit/codex/fit_start_poll_review_prompt.txt |   116 +
 docs/autofit/codex/fit_start_poll_verdict_runA.md  |  5464 +++++++
 docs/autofit/codex/fit_start_poll_verdict_runB.md  |  5967 +++++++
 .../plans/2026-09-27-long-fits-start-poll.md       |   206 +
 fitting.py                                         |    89 +-
 scripts/public_fit_poll_check.py                   |    97 +
 templates/index.html                               |   280 +-
 tests/js/fit_acceptance.test.js                    |    34 +-
 tests/js/fit_start_poll.test.js                    |   300 +
 tests/js/per_tab_state.test.js                     |     1 +
 tests/js/stale_statistics.test.js                  |    31 +-
 tests/test_browser_bg_window_request.py            |     2 +-
 tests/test_browser_endpoint_avg_default.py         |     2 +-
 tests/test_fit_start_poll.py                       |   254 +
 23 files changed, 43969 insertions(+), 149 deletions(-)

exec
/bin/zsh -lc 'cat docs/autofit/codex/fit_start_poll_review_prompt.txt docs/superpowers/plans/2026-09-27-long-fits-start-poll.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
exec
/bin/zsh -lc 'for p in /AGENTS.md /Users/AGENTS.md /Users/skyefortier/AGENTS.md /Users/skyefortier/xps-app/AGENTS.md /Users/skyefortier/xps-app/.claude/AGENTS.md /Users/skyefortier/xps-app/.claude/worktrees/AGENTS.md; do if [ -f "$p" ]; then cat "$p"; fi; done; rg --files --hidden -g AGENTS.md -g '"'"'!node_modules'"' -g '"'!.git'"'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 exited 1 in 0ms:
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

**Round 3 — run A GO, run B NO-GO** (`fit_start_poll_r3_verdict_run{A,B}.md`;
both confirmed round 2's response-order, late-poll, timeout and admission
fixes on the old code vs the new):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (B): Auto-Fit claimed its operation AFTER its confirmation modal (its first await): a Run Fit pressed while the modal was open was cancelled when the student confirmed, and the older Auto-Fit's result applied | an operation is NUMBERED at the press (`_newFitOp`, before the modal) and INSTALLED as the tab's current one after it (`_installFitOp`), only if no newer operation claimed the tab meanwhile — otherwise the confirmed Auto-Fit returns having changed nothing (no snapshot, no request). Claiming at the press would have cancelled a running Run Fit merely for opening the modal. Run Fit, which has no modal, claims = numbers + installs at once. |
| 2 | MINOR (A, B): the fit spinner is page-wide; a fit discarded on tab A hid tab B's running spinner, re-enabled Run Fit and cleared the in-flight flag | the spinner belongs to the operation that showed it (`_fitSpinnerOp`); every hide after a caller's claim is `_hideFitSpinnerFor(op)`, a no-op for any other operation |

exec
/bin/zsh -lc 'git diff HEAD~1..HEAD -- templates/index.html tests/js/fit_start_poll.test.js tests/js/fit_acceptance.test.js tests/js/per_tab_state.test.js tests/js/stale_statistics.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-qGaRCO0Q' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Pouw9GGR' (errno=Operation not permitted)
diff --git a/templates/index.html b/templates/index.html
index ddbc6d8..26f974a 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -7479,14 +7479,32 @@ const _runningFitJobs = new Set();
 // share a tab.
 let _fitOpSeq = 0;
 const _fitOpByOwner = new WeakMap();
-function _claimFitOp(owner) {
-  const prev = owner ? _fitOpByOwner.get(owner) : null;
-  if (prev && prev.jobId) _cancelFitJob(prev.jobId);
-  const op = { seq: ++_fitOpSeq, owner: owner || null, jobId: null };
-  if (owner) _fitOpByOwner.set(owner, op);
-  return op;
+// An operation is NUMBERED when the student presses the button (_newFitOp) and
+// INSTALLED as its tab's current one when it is about to change anything
+// (_installFitOp) — only if no newer operation has claimed the tab meanwhile
+// (Codex round 3: Auto-Fit's confirmation modal sits between the two; a Run
+// Fit pressed while it is open must win, and opening the modal must not kill
+// a running fit the student may still keep by cancelling the modal).
+function _newFitOp(owner) { return { seq: ++_fitOpSeq, owner: owner || null, jobId: null }; }
+function _installFitOp(op) {
+  if (!op || !op.owner) return true;
+  const cur = _fitOpByOwner.get(op.owner);
+  if (cur && cur.seq > op.seq) return false;          // a newer operation owns the tab
+  if (cur && cur !== op && cur.jobId) _cancelFitJob(cur.jobId);
+  _fitOpByOwner.set(op.owner, op);
+  return true;
 }
+function _claimFitOp(owner) { const op = _newFitOp(owner); _installFitOp(op); return op; }
 function _fitOpCurrent(op) { return !op || !op.owner || _fitOpByOwner.get(op.owner) === op; }
+// The fit spinner is page-wide, one per page; the operation that showed it
+// owns it. A fit that ends after another tab's fit took the spinner leaves it
+// alone (Codex round 3: a discarded tab-A fit hid tab B's running spinner).
+let _fitSpinnerOp = null;
+function _hideFitSpinnerFor(op) {
+  if (_fitSpinnerOp !== op) return;
+  _fitSpinnerOp = null;
+  _hideFitSpinner();
+}
 function _cancelFitJob(jobId) {
   try { fetch('/api/fit/cancel/' + encodeURIComponent(jobId), { method: 'POST', keepalive: true }).catch(() => {}); } catch (_) { /* best effort */ }
 }
@@ -7605,6 +7623,9 @@ async function runAutoFitC1sGraphite() {
   // when it resolves may not be the one the user asked to auto-fit.
   const fittingTab = _opOwner();
   if (!fittingTab) { notify('No active spectrum tab.', 'amber'); return; }
+  // unit 2: this press's fit operation, numbered NOW (before the modal) and
+  // installed after it, only if no newer operation claimed the tab meanwhile
+  const afOp = _newFitOp(fittingTab);
   // Confirmation if existing peaks
   if (state.peaks.length >= 1) {
     const proceed = await _showAutoFitConfirmModal(state.peaks.length);
@@ -7615,6 +7636,9 @@ async function runAutoFitC1sGraphite() {
     }
   }
 
+  // a Run Fit pressed while the confirmation was open is newer: it wins, and
+  // this Auto-Fit does nothing at all (nothing has been changed yet)
+  if (!_installFitOp(afOp)) return;
   // Snapshot for failure rollback (separate from pushUndo, which only covers peaks).
   const snap = _autoFitSnapshot();
 
@@ -7662,13 +7686,13 @@ async function runAutoFitC1sGraphite() {
 
   // Step 5: run /api/fit with AbortController + spinner.
   _showFitSpinner();
+  _fitSpinnerOp = afOp;
   const spinLabel = document.getElementById('fit-spinner-label');
   if (spinLabel) spinLabel.textContent = 'Auto-fitting…';
   const runBtn = document.querySelector('.btn-green');
   if (runBtn) runBtn.disabled = true;
 
   const ctrl = new AbortController();
-  let afOp = null;   // unit 2: this tab's fit operation (claimed below, before the first server await)
   const timer = setTimeout(() => ctrl.abort(new DOMException('timeout', 'AbortError')), 120000);
 
   try {
@@ -7689,7 +7713,6 @@ async function runAutoFitC1sGraphite() {
     // the model and its fit context as sent (F1, Codex round 1): a result must
     // not be applied, and stamped current, over a model edited while it ran
     const ctxAtRequest = _startsLiveKey();
-    afOp = _claimFitOp(fittingTab);   // unit 2: before the first server await; the newest claim for a tab is current
     // Build peak specs and overlay the per-peak bounds we attached in buildAutoFitModel.
     const peakSpecs = state.peaks.map(p => {
       const spec = peakToBackendSpec(p);
@@ -7733,13 +7756,13 @@ async function runAutoFitC1sGraphite() {
     // (_serverFitJob throws it with httpStatus); an unreadable reply is a
     // failed fit with its own message (unreadableReply).
     if (json && json._abandoned === 'tab') {
-      _hideFitSpinner();
+      _hideFitSpinnerFor(afOp);
       notify('Auto-fit discarded — tab switched during fit.', 'amber');
       _autoFitRestore(snap, fittingTab);
       return;
     }
     if (json && json._abandoned === 'model') {
-      _hideFitSpinner();
+      _hideFitSpinnerFor(afOp);
       notify('Auto-fit discarded because the model or its background / ROI settings were edited while it was running. Previous peaks and result restored. Run it again.', 'amber', true);
       _autoFitRestore(snap, fittingTab);
       return;
@@ -7747,13 +7770,13 @@ async function runAutoFitC1sGraphite() {
     if (json.error) throw new Error(json.error);
     if (json.success !== true) throw new Error(json.message || 'fit did not converge');
     if (!_ownerActive(fittingTab)) {
-      _hideFitSpinner();
+      _hideFitSpinnerFor(afOp);
       notify('Auto-fit discarded — tab switched during fit.', 'amber');
       _autoFitRestore(snap, fittingTab);
       return;
     }
     if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
-      _hideFitSpinner();
+      _hideFitSpinnerFor(afOp);
       notify('Auto-fit discarded because the model or its background / ROI settings were edited while it was running. Previous peaks and result restored. Run it again.', 'amber', true);
       _autoFitRestore(snap, fittingTab);
       return;
@@ -7763,19 +7786,19 @@ async function runAutoFitC1sGraphite() {
 
     const ok = applyAutoFitResult(json, graphiteRaw, { be: be2, inten: inten2, bgIntensity: bgI, bgSubtracted: bgSub });
     if (!ok) {
-      _hideFitSpinner();
+      _hideFitSpinnerFor(afOp);
       _autoFitRestore(snap, fittingTab);
       return;
     }
 
-    _hideFitSpinner();
+    _hideFitSpinnerFor(afOp);
     notify('Auto-fit complete. χ²ᵣ = ' + (state.fitResult?.chiReduced?.toFixed(3) || '?'), 'green');
   } catch (e) {
     clearTimeout(timer);
     // superseded (Run Fit pressed during Auto-Fit): nothing at all — no
     // rollback (it would overwrite the newer fit's model), no message
     if (afOp && !_fitOpCurrent(afOp)) return;
-    _hideFitSpinner();
+    _hideFitSpinnerFor(afOp);
     // The catch path can also fire after a mid-flight tab switch (fetch
     // error/timeout after the user moved on) — same wrong-tab hazard as
     // the explicit discard branch, so it gets the same tab-aware restore.
@@ -8184,6 +8207,7 @@ async function runFit(opts = {}) {
     // result must not be written over a model that was edited while it ran
     ctxAtRequest = _startsLiveKey();
     fitOp = _claimFitOp(fittingTab);   // before the first await: the newest claim for a tab is current
+    _fitSpinnerOp = fitOp;             // the spinner shown above is this operation's
     const fitMethod = document.getElementById('fit-method').value;
     const epAvgVal = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
     const bgPayload = { method: bgType, start_idx: bgWin.i0, end_idx: bgWin.i1 + 1, endpoint_avg: epAvgVal };
@@ -8227,13 +8251,13 @@ async function runFit(opts = {}) {
     });
     if (json && json._abandoned === 'superseded') return;   // a newer fit on this tab owns the spinner and the result
     if (json && json._abandoned === 'tab') {
-      _hideFitSpinner();
+      _hideFitSpinnerFor(fitOp);
       document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
       notify('Fit result discarded because you switched tabs during the fit.', 'amber');
       return;
     }
     if (json && json._abandoned === 'model') {
-      _hideFitSpinner();
+      _hideFitSpinnerFor(fitOp);
       document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
       notify('Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.', 'amber', true);
       return;
@@ -8256,7 +8280,7 @@ async function runFit(opts = {}) {
     // If the user switched tabs while the fit was running, discard the result
     // rather than overwriting the now-active tab's peaks.
     if (!_ownerActive(fittingTab)) {
-      _hideFitSpinner();
+      _hideFitSpinnerFor(fitOp);
       document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
       notify('Fit result discarded because you switched tabs during the fit.', 'amber');
       return;
@@ -8266,7 +8290,7 @@ async function runFit(opts = {}) {
     // the model as it was must not be applied over an edited one (a newly locked
     // centre would keep its edited value under the server's statistics).
     if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
-      _hideFitSpinner();
+      _hideFitSpinnerFor(fitOp);
       document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
       notify('Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.', 'amber', true);
       return;
@@ -8297,14 +8321,14 @@ async function runFit(opts = {}) {
     document.getElementById('sb-msg').textContent = 'Fit complete (lmfit)';
     _updateRFactorUI(state.fitResult.rFactor);
     _updateROIDisplay(roiRange);
-    _hideFitSpinner();
+    _hideFitSpinnerFor(fitOp);
     notify('Fit complete. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3), 'green');
   } catch (e) {
     // superseded (a newer fit on this tab): nothing at all — no message, no
     // local fallback, the newer fit owns the spinner and the result
     if (fitOp && !_fitOpCurrent(fitOp)) return;
     // Fall back to local Levenberg-Marquardt
-    _hideFitSpinner();
+    _hideFitSpinnerFor(fitOp);
     if (!_ownerActive(fittingTab)) {
       document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
       notify('Fit cancelled — tab switched during fit.', 'amber');
@@ -8320,7 +8344,7 @@ async function runFit(opts = {}) {
     if (e && e.transportFailure && ctxAtRequest !== null && !_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
       // The fallback would fit the arrays captured at the press over a model or
       // context edited since, and stamp the edited one (F1, Codex round 1).
-      _hideFitSpinner();
+      _hideFitSpinnerFor(fitOp);
       document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
       notify('The server could not be reached, and the model or its background / ROI settings were edited while the fit was running, so no local fit was run. Previous peaks and result kept. Run the fit again.', 'amber', true);
       return;
diff --git a/tests/js/fit_acceptance.test.js b/tests/js/fit_acceptance.test.js
index cdf5474..9d4c496 100644
--- a/tests/js/fit_acceptance.test.js
+++ b/tests/js/fit_acceptance.test.js
@@ -36,7 +36,7 @@ function extractFn(name) {
 // that reply as a finished job (start -> 202 + id; progress -> done + result),
 // and a start that throws is still a transport failure.
 const POLL_SRC = [constLineOf('FIT_POLL_MS'), constLineOf('FIT_POLL_TRANSPORT_RETRIES'), constLineOf('FIT_HEARTBEAT_LOST_SEC'),
-  'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap();', ...['_cancelFitJob', '_fitHttpError', '_claimFitOp', '_fitOpCurrent', '_serverFitJob'].map(n => extractFn(n))].join('\n');
+  'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap(); let _fitSpinnerOp = null;', ...['_cancelFitJob', '_fitHttpError', '_newFitOp', '_installFitOp', '_claimFitOp', '_fitOpCurrent', '_hideFitSpinnerFor', '_serverFitJob'].map(n => extractFn(n))].join('\n');
 function constLineOf(n) { const l = lines.find(x => x.startsWith('const ' + n)); assert.ok(l, n); return l; }
 function jobAdapter(fetchImpl) {
   let reply = null;
diff --git a/tests/js/fit_start_poll.test.js b/tests/js/fit_start_poll.test.js
index c98b683..af522b0 100644
--- a/tests/js/fit_start_poll.test.js
+++ b/tests/js/fit_start_poll.test.js
@@ -42,8 +42,8 @@ const bad = (status, obj) => ({ ok: false, status, json: async () => { if (obj =
 
 function make(fetch) {
   const src = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
-    'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap();',
-    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_claimFitOp'), extractFn('_fitOpCurrent'),
+    'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap(); let _fitSpinnerOp = null;',
+    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_newFitOp'), extractFn('_installFitOp'), extractFn('_claimFitOp'), extractFn('_fitOpCurrent'),
     extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
   return new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob, _runningFitJobs, _claimFitOp };')(
     fetch, f => f(), class extends Error { constructor(m, n) { super(m); this.name = n; } });
@@ -150,8 +150,8 @@ test('Run Fit and Auto-Fit both go through _serverFitJob; nothing on the page po
 // exit (a result, an error, a timeout).
 function makeAsync(fetch) {
   const src = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
-    'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap();',
-    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_claimFitOp'), extractFn('_fitOpCurrent'),
+    'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap(); let _fitSpinnerOp = null;',
+    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_newFitOp'), extractFn('_installFitOp'), extractFn('_claimFitOp'), extractFn('_fitOpCurrent'),
     extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
   return new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob, _claimFitOp };')(
     fetch, f => { setImmediate(f); return 0; }, class extends Error {});   // yield to the event loop between polls
@@ -235,9 +235,66 @@ test('both callers claim their operation before the first await and do nothing a
   assert.match(run, /if \(json && json\._abandoned === 'superseded'\) return;/);
   assert.match(run, /\} catch \(e\) \{\n(\s*\/\/[^\n]*\n)*\s*if \(fitOp && !_fitOpCurrent\(fitOp\)\) return;/, 'runFit: a superseded operation never reaches the local fallback');
   const af = extractFn('runAutoFitC1sGraphite');
-  const claim = af.indexOf('afOp = _claimFitOp(fittingTab);');
-  assert.ok(claim > 0 && claim < af.indexOf('await uploadToBackend('), 'Auto-Fit claims before its first server await');
+  const num = af.indexOf('const afOp = _newFitOp(fittingTab);');
+  assert.ok(num > 0 && num < af.indexOf('await _showAutoFitConfirmModal('), 'Auto-Fit numbers its operation before its FIRST await (the modal)');
+  const inst = af.indexOf('if (!_installFitOp(afOp)) return;');
+  assert.ok(inst > af.indexOf('await _showAutoFitConfirmModal(') && inst < af.indexOf('_autoFitSnapshot()') && inst < af.indexOf('await uploadToBackend('),
+    'and installs it after the modal, before anything is changed or sent');
   assert.match(af, /op: afOp,/);
   assert.match(af, /if \(json && json\._abandoned === 'superseded'\) return;/);
   assert.match(af, /if \(afOp && !_fitOpCurrent\(afOp\)\) return;/, 'Auto-Fit: no rollback when superseded');
 });
+
+test('the Auto-Fit modal race: a Run Fit pressed while the confirmation is open WINS; the confirmed Auto-Fit changes nothing (Codex round 3)', async () => {
+  const constants = lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n');
+  const modal = deferred();
+  const tab = { id: 't1' };
+  const out = { starts: 0, restored: 0, snapshots: 0, applied: 0, cancels: [] };
+  const state = { peaks: [{ id: 1 }], ccShift: 0, rawBE: [285, 284.5, 284], rawIntensity: [10, 20, 10] };
+  const deps = {
+    state, tabManager: { activeId: 't1', _getTab: () => tab, _captureUI: () => ({}) },
+    document: { getElementById: () => ({ value: '', style: {}, setAttribute() {}, classList: { add() {}, remove() {} } }) },
+    notify() {}, _opOwner: () => tab, _ownerActive: () => true, isC1sTab: () => true,
+    _showAutoFitConfirmModal: () => modal.p, _autoFitSnapshot: () => { out.snapshots++; return {}; }, _autoFitRestore: () => { out.restored++; },
+    fetch: async (u, i) => { if (u === '/api/fit/start') out.starts++; if (u.startsWith('/api/fit/cancel/')) out.cancels.push(u); return ok({ job_id: 'X' }, 202); },
+    applyBackendResult: () => { out.applied++; }, _showFitSpinner() {}, _hideFitSpinner() {}, setTimeout, clearTimeout, AbortController, DOMException: Error,
+    getROIData: () => ({ be: state.rawBE, inten: state.rawIntensity }), computeBackground: be => be.map(() => 0), findGraphiteRawBE: () => 284.5,
+    uploadToBackend: async () => 'sid', pushUndo() {}, buildAutoFitModel: () => [], renderPeakList() {}, peakToBackendSpec: p => p, _getManualAnchors: () => [],
+  };
+  const src = constants + '\n' + [
+    'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap(); let _fitSpinnerOp = null;',
+    ...['_cancelFitJob', '_fitHttpError', '_newFitOp', '_installFitOp', '_claimFitOp', '_fitOpCurrent', '_hideFitSpinnerFor', '_readFitReply', '_serverFitJob',
+        'runAutoFitC1sGraphite', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn)].join('\n');
+  const api = new Function(...Object.keys(deps), src + '\nreturn { runAutoFitC1sGraphite, _claimFitOp, _fitOpCurrent };')(...Object.values(deps));
+  const af = api.runAutoFitC1sGraphite();             // Auto-Fit pressed: the modal is open
+  await new Promise(r => setImmediate(r));
+  const runFitOp = api._claimFitOp(tab);              // Run Fit pressed (Ctrl/Cmd+F) while the modal is open
+  modal.res(true);                                    // the student confirms Auto-Fit
+  await af;
+  assert.strictEqual(out.snapshots, 0, 'the superseded Auto-Fit took no snapshot (changed nothing)');
+  assert.strictEqual(out.starts, 0, 'and sent nothing');
+  assert.strictEqual(out.applied + out.restored, 0);
+  assert.ok(api._fitOpCurrent(runFitOp), 'the Run Fit still owns the tab');
+  assert.deepStrictEqual(out.cancels, [], "the Run Fit's job was not cancelled");
+});
+
+test("the spinner belongs to the operation that showed it: an ended fit never hides another fit's spinner (Codex round 3)", () => {
+  const hides = [];
+  const api = new Function('_hideFitSpinner', 'let _fitSpinnerOp = null;\n' + extractFn('_hideFitSpinnerFor') +
+    '\nreturn { hideFor: _hideFitSpinnerFor, set: op => { _fitSpinnerOp = op; }, get: () => _fitSpinnerOp };')(() => hides.push('hide'));
+  const a = { seq: 1 }, b = { seq: 2 };
+  api.set(b);                                         // tab B's fit showed the spinner last
+  api.hideFor(a);                                     // tab A's fit ends (discarded)
+  assert.deepStrictEqual(hides, [], "A leaves B's spinner alone");
+  api.hideFor(b);
+  assert.deepStrictEqual(hides, ['hide']);
+  assert.strictEqual(api.get(), null);
+  // and every hide after each caller's claim is an owned hide
+  for (const [fn, op, mark] of [['runFit', 'fitOp', '_fitSpinnerOp = fitOp;'], ['runAutoFitC1sGraphite', 'afOp', '_fitSpinnerOp = afOp;']]) {
+    const src = extractFn(fn);
+    const after = src.slice(src.indexOf(mark));
+    assert.ok(src.indexOf(mark) > 0, fn + ' takes the spinner');
+    assert.ok(!/_hideFitSpinner\(\);/.test(after), fn + ': no unowned hide after the claim');
+    assert.ok(new RegExp('_hideFitSpinnerFor\\(' + op + '\\)').test(after), fn);
+  }
+});
diff --git a/tests/js/per_tab_state.test.js b/tests/js/per_tab_state.test.js
index 48da6c6..2f1a5d0 100644
--- a/tests/js/per_tab_state.test.js
+++ b/tests/js/per_tab_state.test.js
@@ -34,7 +34,7 @@ const ALLOWLIST = {
   _ssFocusIdx: 'A', _ssFiltered: 'A',
   _fpMeta: 'B', _fpModalDrag: 'A', _fpRegionsSelected: 'A', _fpExpandedElement: 'A',
   _findPeaksApplyConfirmResolver: 'A',
-  _runningFitJobs: 'A', _fitOpByOwner: 'A', _fitOpSeq: 'A',   // unit 2: in-flight job ids (pagehide beacon; the current job of each tab record, WeakMap keyed by the record) — no spectrum content       // unit 2: ids of in-flight server fit jobs, for the pagehide cancel beacon — no spectrum content
+  _runningFitJobs: 'A', _fitOpByOwner: 'A', _fitOpSeq: 'A', _fitSpinnerOp: 'A',   // unit 2: in-flight job ids (pagehide beacon; the current job of each tab record, WeakMap keyed by the record) — no spectrum content       // unit 2: ids of in-flight server fit jobs, for the pagehide cancel beacon — no spectrum content
   _undoDebounce: 'A',         // burst buffer: DOES hold a peaks snapshot, but bound to its owner record at burst start and flushed onto that record only — the async-ownership exception to class A's 'no spectrum content'
   // Populated constant catalogues (read-only tables) and the chart plugin
   // object: class B. Listed, not skipped, so a per-tab store hidden in an
diff --git a/tests/js/stale_statistics.test.js b/tests/js/stale_statistics.test.js
index d0920d6..014db6e 100644
--- a/tests/js/stale_statistics.test.js
+++ b/tests/js/stale_statistics.test.js
@@ -306,7 +306,7 @@ test('the refresh re-renders Results only when its rendered state differs', () =
 // as a finished job, and runs the poll loop's short waits at once (the
 // 2-minute Auto-Fit timer is left pending, as before).
 const POLL_SRC = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
-  'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap();', ...['_cancelFitJob', '_fitHttpError', '_claimFitOp', '_fitOpCurrent', '_serverFitJob'].map(extractFn)].join('\n');
+  'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap(); let _fitSpinnerOp = null;', ...['_cancelFitJob', '_fitHttpError', '_newFitOp', '_installFitOp', '_claimFitOp', '_fitOpCurrent', '_hideFitSpinnerFor', '_serverFitJob'].map(extractFn)].join('\n');
 function pollify(deps) {
   const inner = deps.fetch;
   let reply = null;

exec
/bin/zsh -lc "git diff HEAD~1..HEAD -- templates/index.html && sed -n '135,230p' docs/superpowers/plans/2026-09-27-long-fits-start-poll.md && rg -n 'VERDICT:|MAJOR|MINOR|BLOCKER|"'^Findings'"' docs/autofit/codex/fit_start_poll*verdict*md | tail -65" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-x84Ijwca' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-BfZTupRT' (errno=Operation not permitted)
diff --git a/templates/index.html b/templates/index.html
index ddbc6d8..26f974a 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -7479,14 +7479,32 @@ const _runningFitJobs = new Set();
 // share a tab.
 let _fitOpSeq = 0;
 const _fitOpByOwner = new WeakMap();
-function _claimFitOp(owner) {
-  const prev = owner ? _fitOpByOwner.get(owner) : null;
-  if (prev && prev.jobId) _cancelFitJob(prev.jobId);
-  const op = { seq: ++_fitOpSeq, owner: owner || null, jobId: null };
-  if (owner) _fitOpByOwner.set(owner, op);
-  return op;
+// An operation is NUMBERED when the student presses the button (_newFitOp) and
+// INSTALLED as its tab's current one when it is about to change anything
+// (_installFitOp) — only if no newer operation has claimed the tab meanwhile
+// (Codex round 3: Auto-Fit's confirmation modal sits between the two; a Run
+// Fit pressed while it is open must win, and opening the modal must not kill
+// a running fit the student may still keep by cancelling the modal).
+function _newFitOp(owner) { return { seq: ++_fitOpSeq, owner: owner || null, jobId: null }; }
+function _installFitOp(op) {
+  if (!op || !op.owner) return true;
+  const cur = _fitOpByOwner.get(op.owner);
+  if (cur && cur.seq > op.seq) return false;          // a newer operation owns the tab
+  if (cur && cur !== op && cur.jobId) _cancelFitJob(cur.jobId);
+  _fitOpByOwner.set(op.owner, op);
+  return true;
 }
+function _claimFitOp(owner) { const op = _newFitOp(owner); _installFitOp(op); return op; }
 function _fitOpCurrent(op) { return !op || !op.owner || _fitOpByOwner.get(op.owner) === op; }
+// The fit spinner is page-wide, one per page; the operation that showed it
+// owns it. A fit that ends after another tab's fit took the spinner leaves it
+// alone (Codex round 3: a discarded tab-A fit hid tab B's running spinner).
+let _fitSpinnerOp = null;
+function _hideFitSpinnerFor(op) {
+  if (_fitSpinnerOp !== op) return;
+  _fitSpinnerOp = null;
+  _hideFitSpinner();
+}
 function _cancelFitJob(jobId) {
   try { fetch('/api/fit/cancel/' + encodeURIComponent(jobId), { method: 'POST', keepalive: true }).catch(() => {}); } catch (_) { /* best effort */ }
 }
@@ -7605,6 +7623,9 @@ async function runAutoFitC1sGraphite() {
   // when it resolves may not be the one the user asked to auto-fit.
   const fittingTab = _opOwner();
   if (!fittingTab) { notify('No active spectrum tab.', 'amber'); return; }
+  // unit 2: this press's fit operation, numbered NOW (before the modal) and
+  // installed after it, only if no newer operation claimed the tab meanwhile
+  const afOp = _newFitOp(fittingTab);
   // Confirmation if existing peaks
   if (state.peaks.length >= 1) {
     const proceed = await _showAutoFitConfirmModal(state.peaks.length);
@@ -7615,6 +7636,9 @@ async function runAutoFitC1sGraphite() {
     }
   }
 
+  // a Run Fit pressed while the confirmation was open is newer: it wins, and
+  // this Auto-Fit does nothing at all (nothing has been changed yet)
+  if (!_installFitOp(afOp)) return;
   // Snapshot for failure rollback (separate from pushUndo, which only covers peaks).
   const snap = _autoFitSnapshot();
 
@@ -7662,13 +7686,13 @@ async function runAutoFitC1sGraphite() {
 
   // Step 5: run /api/fit with AbortController + spinner.
   _showFitSpinner();
+  _fitSpinnerOp = afOp;
   const spinLabel = document.getElementById('fit-spinner-label');
   if (spinLabel) spinLabel.textContent = 'Auto-fitting…';
   const runBtn = document.querySelector('.btn-green');
   if (runBtn) runBtn.disabled = true;
 
   const ctrl = new AbortController();
-  let afOp = null;   // unit 2: this tab's fit operation (claimed below, before the first server await)
   const timer = setTimeout(() => ctrl.abort(new DOMException('timeout', 'AbortError')), 120000);
 
   try {
@@ -7689,7 +7713,6 @@ async function runAutoFitC1sGraphite() {
     // the model and its fit context as sent (F1, Codex round 1): a result must
     // not be applied, and stamped current, over a model edited while it ran
     const ctxAtRequest = _startsLiveKey();
-    afOp = _claimFitOp(fittingTab);   // unit 2: before the first server await; the newest claim for a tab is current
     // Build peak specs and overlay the per-peak bounds we attached in buildAutoFitModel.
     const peakSpecs = state.peaks.map(p => {
       const spec = peakToBackendSpec(p);
@@ -7733,13 +7756,13 @@ async function runAutoFitC1sGraphite() {
     // (_serverFitJob throws it with httpStatus); an unreadable reply is a
     // failed fit with its own message (unreadableReply).
     if (json && json._abandoned === 'tab') {
-      _hideFitSpinner();
+      _hideFitSpinnerFor(afOp);
       notify('Auto-fit discarded — tab switched during fit.', 'amber');
       _autoFitRestore(snap, fittingTab);
       return;
     }
     if (json && json._abandoned === 'model') {
-      _hideFitSpinner();
+      _hideFitSpinnerFor(afOp);
       notify('Auto-fit discarded because the model or its background / ROI settings were edited while it was running. Previous peaks and result restored. Run it again.', 'amber', true);
       _autoFitRestore(snap, fittingTab);
       return;
@@ -7747,13 +7770,13 @@ async function runAutoFitC1sGraphite() {
     if (json.error) throw new Error(json.error);
     if (json.success !== true) throw new Error(json.message || 'fit did not converge');
     if (!_ownerActive(fittingTab)) {
-      _hideFitSpinner();
+      _hideFitSpinnerFor(afOp);
       notify('Auto-fit discarded — tab switched during fit.', 'amber');
       _autoFitRestore(snap, fittingTab);
       return;
     }
     if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
-      _hideFitSpinner();
+      _hideFitSpinnerFor(afOp);
       notify('Auto-fit discarded because the model or its background / ROI settings were edited while it was running. Previous peaks and result restored. Run it again.', 'amber', true);
       _autoFitRestore(snap, fittingTab);
       return;
@@ -7763,19 +7786,19 @@ async function runAutoFitC1sGraphite() {
 
     const ok = applyAutoFitResult(json, graphiteRaw, { be: be2, inten: inten2, bgIntensity: bgI, bgSubtracted: bgSub });
     if (!ok) {
-      _hideFitSpinner();
+      _hideFitSpinnerFor(afOp);
       _autoFitRestore(snap, fittingTab);
       return;
     }
 
-    _hideFitSpinner();
+    _hideFitSpinnerFor(afOp);
     notify('Auto-fit complete. χ²ᵣ = ' + (state.fitResult?.chiReduced?.toFixed(3) || '?'), 'green');
   } catch (e) {
     clearTimeout(timer);
     // superseded (Run Fit pressed during Auto-Fit): nothing at all — no
     // rollback (it would overwrite the newer fit's model), no message
     if (afOp && !_fitOpCurrent(afOp)) return;
-    _hideFitSpinner();
+    _hideFitSpinnerFor(afOp);
     // The catch path can also fire after a mid-flight tab switch (fetch
     // error/timeout after the user moved on) — same wrong-tab hazard as
     // the explicit discard branch, so it gets the same tab-aware restore.
@@ -8184,6 +8207,7 @@ async function runFit(opts = {}) {
     // result must not be written over a model that was edited while it ran
     ctxAtRequest = _startsLiveKey();
     fitOp = _claimFitOp(fittingTab);   // before the first await: the newest claim for a tab is current
+    _fitSpinnerOp = fitOp;             // the spinner shown above is this operation's
     const fitMethod = document.getElementById('fit-method').value;
     const epAvgVal = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
     const bgPayload = { method: bgType, start_idx: bgWin.i0, end_idx: bgWin.i1 + 1, endpoint_avg: epAvgVal };
@@ -8227,13 +8251,13 @@ async function runFit(opts = {}) {
     });
     if (json && json._abandoned === 'superseded') return;   // a newer fit on this tab owns the spinner and the result
     if (json && json._abandoned === 'tab') {
-      _hideFitSpinner();
+      _hideFitSpinnerFor(fitOp);
       document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
       notify('Fit result discarded because you switched tabs during the fit.', 'amber');
       return;
     }
     if (json && json._abandoned === 'model') {
-      _hideFitSpinner();
+      _hideFitSpinnerFor(fitOp);
       document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
       notify('Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.', 'amber', true);
       return;
@@ -8256,7 +8280,7 @@ async function runFit(opts = {}) {
     // If the user switched tabs while the fit was running, discard the result
     // rather than overwriting the now-active tab's peaks.
     if (!_ownerActive(fittingTab)) {
-      _hideFitSpinner();
+      _hideFitSpinnerFor(fitOp);
       document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
       notify('Fit result discarded because you switched tabs during the fit.', 'amber');
       return;
@@ -8266,7 +8290,7 @@ async function runFit(opts = {}) {
     // the model as it was must not be applied over an edited one (a newly locked
     // centre would keep its edited value under the server's statistics).
     if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
-      _hideFitSpinner();
+      _hideFitSpinnerFor(fitOp);
       document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
       notify('Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.', 'amber', true);
       return;
@@ -8297,14 +8321,14 @@ async function runFit(opts = {}) {
     document.getElementById('sb-msg').textContent = 'Fit complete (lmfit)';
     _updateRFactorUI(state.fitResult.rFactor);
     _updateROIDisplay(roiRange);
-    _hideFitSpinner();
+    _hideFitSpinnerFor(fitOp);
     notify('Fit complete. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3), 'green');
   } catch (e) {
     // superseded (a newer fit on this tab): nothing at all — no message, no
     // local fallback, the newer fit owns the spinner and the result
     if (fitOp && !_fitOpCurrent(fitOp)) return;
     // Fall back to local Levenberg-Marquardt
-    _hideFitSpinner();
+    _hideFitSpinnerFor(fitOp);
     if (!_ownerActive(fittingTab)) {
       document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
       notify('Fit cancelled — tab switched during fit.', 'amber');
@@ -8320,7 +8344,7 @@ async function runFit(opts = {}) {
     if (e && e.transportFailure && ctxAtRequest !== null && !_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
       // The fallback would fit the arrays captured at the press over a model or
       // context edited since, and stamp the edited one (F1, Codex round 1).
-      _hideFitSpinner();
+      _hideFitSpinnerFor(fitOp);
       document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
       notify('The server could not be reached, and the model or its background / ROI settings were edited while the fit was running, so no local fit was run. Previous peaks and result kept. Run the fit again.', 'amber', true);
       return;
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

**Round 3 — run A GO, run B NO-GO** (`fit_start_poll_r3_verdict_run{A,B}.md`;
both confirmed round 2's response-order, late-poll, timeout and admission
fixes on the old code vs the new):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (B): Auto-Fit claimed its operation AFTER its confirmation modal (its first await): a Run Fit pressed while the modal was open was cancelled when the student confirmed, and the older Auto-Fit's result applied | an operation is NUMBERED at the press (`_newFitOp`, before the modal) and INSTALLED as the tab's current one after it (`_installFitOp`), only if no newer operation claimed the tab meanwhile — otherwise the confirmed Auto-Fit returns having changed nothing (no snapshot, no request). Claiming at the press would have cancelled a running Run Fit merely for opening the modal. Run Fit, which has no modal, claims = numbers + installs at once. |
| 2 | MINOR (A, B): the fit spinner is page-wide; a fit discarded on tab A hid tab B's running spinner, re-enabled Run Fit and cleared the in-flight flag | the spinner belongs to the operation that showed it (`_fitSpinnerOp`); every hide after a caller's claim is `_hideFitSpinnerFor(op)`, a no-op for any other operation |
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23435:+**VERDICT: NO-GO**
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23504:+1. **MAJOR — Re-running does not supersede the previous job.** [templates/index.html:8175](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8175)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23507:+2. **MAJOR — Fit execution has no concurrency limit.** [app.py:672](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:672)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23510:+3. **MINOR — Cancellation exceptions bypass `FitCancelled`.** [fitting.py:2105](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/fitting.py:2105)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23513:+4. **MINOR — Acceptance checker can poll a dead worker forever.** [scripts/public_fit_poll_check.py:59](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/scripts/public_fit_poll_check.py:59)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23518:+**VERDICT: NO-GO**
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23521:+1. **MAJOR — Re-running does not supersede the previous job.** [templates/index.html:8175](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8175)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23524:+2. **MAJOR — Fit execution has no concurrency limit.** [app.py:672](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:672)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23527:+3. **MINOR — Cancellation exceptions bypass `FitCancelled`.** [fitting.py:2105](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/fitting.py:2105)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23530:+4. **MINOR — Acceptance checker can poll a dead worker forever.** [scripts/public_fit_poll_check.py:59](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/scripts/public_fit_poll_check.py:59)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23535:+**VERDICT: NO-GO**
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23616:+1. **MAJOR — Start-response order determines ownership.** [templates/index.html:7511](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7511) registers ownership only after awaiting the start response. Reproduced: invocation A starts first, B’s response arrives first, then A’s delayed response cancels B. B returns `superseded`; A returns its result. Delayed uploads permit the same reversal. Establish an invocation token before the caller’s first await.
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23618:+2. **MAJOR — Superseded polls still apply results or trigger rollback.** [templates/index.html:7556](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7556) handles terminal responses without rechecking ownership after the fetch/body awaits. Reproduced with the actual callers: Auto-Fit has a poll in flight; Run Fit supersedes it; the old poll returns `cancelled`. Auto-Fit throws and restores its snapshot at [templates/index.html:7754](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7754), causing the replacement to discard itself as “model edited.” A delayed `done` response also returns the obsolete result. Recheck supersession after asynchronous boundaries and before error handling, rollback, or result application; supersession must also precede timeout handling.
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23620:+3. **MINOR — Partial thread startup releases admission twice.** [app.py:716](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:716), [app.py:1285](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:1285). If the fit thread starts but heartbeat-thread startup raises, the route releases admission although the worker remains alive. Its eventual `finally` releases again. Fault injection reproduced seven outstanding jobs against the six-job cap. Make admission release have exactly one owner after worker startup.
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23624:+**VERDICT: NO-GO**
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23627:+1. **MAJOR — Start-response order determines ownership.** [templates/index.html:7511](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7511) registers ownership only after awaiting the start response. Reproduced: invocation A starts first, B’s response arrives first, then A’s delayed response cancels B. B returns `superseded`; A returns its result. Delayed uploads permit the same reversal. Establish an invocation token before the caller’s first await.
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23629:+2. **MAJOR — Superseded polls still apply results or trigger rollback.** [templates/index.html:7556](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7556) handles terminal responses without rechecking ownership after the fetch/body awaits. Reproduced with the actual callers: Auto-Fit has a poll in flight; Run Fit supersedes it; the old poll returns `cancelled`. Auto-Fit throws and restores its snapshot at [templates/index.html:7754](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7754), causing the replacement to discard itself as “model edited.” A delayed `done` response also returns the obsolete result. Recheck supersession after asynchronous boundaries and before error handling, rollback, or result application; supersession must also precede timeout handling.
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23631:+3. **MINOR — Partial thread startup releases admission twice.** [app.py:716](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:716), [app.py:1285](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:1285). If the fit thread starts but heartbeat-thread startup raises, the route releases admission although the worker remains alive. Its eventual `finally` releases again. Fault injection reproduced seven outstanding jobs against the six-job cap. Make admission release have exactly one owner after worker startup.
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23635:+**VERDICT: NO-GO**
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23710:+1. **MAJOR — Superseded jobs still process in-flight poll responses.** [templates/index.html:7556](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7556)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23713:+2. **MAJOR — Response order determines which operation supersedes which.** [templates/index.html:7511](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7511)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23716:+3. **MINOR — Partial thread startup releases admission twice.** [app.py:715](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:715), [app.py:1285](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:1285)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23721:+VERDICT: NO-GO
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23724:+1. **MAJOR — Superseded jobs still process in-flight poll responses.** [templates/index.html:7556](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7556)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23727:+2. **MAJOR — Response order determines which operation supersedes which.** [templates/index.html:7511](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7511)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23730:+3. **MINOR — Partial thread startup releases admission twice.** [app.py:715](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:715), [app.py:1285](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:1285)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:23735:+VERDICT: NO-GO
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25394:+1. **MAJOR — Re-running does not cancel the previous fit.** [templates/index.html:8176](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8176) checks only tab identity and model equality. Ctrl/Cmd+F calls `runFit()` despite the disabled button. Pressing it again with unchanged inputs starts another job; both remain polled, preventing abandonment cancellation. Reproduced: two starts, two pending polls, zero cancellations. The older fit can finish first and cause the replacement to be discarded as “model edited.” Track a per-owner invocation and cancel its predecessor.
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25396:+2. **MAJOR — Fit concurrency is unbounded.** [app.py:672](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:672) launches two threads for every accepted start without admission control or a bounded queue. Gunicorn’s four synchronous workers therefore no longer bound concurrent fitting work. A filesystem-mocked probe accepted 12 starts in one process and retained 24 job threads. Repeated submissions or simultaneous students can accumulate CPU-heavy fits and numerical allocations, degrading polling and potentially exhausting memory. Bound active jobs and queued requests.
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25398:+3. **MINOR — Abandonment cancellation becomes a solver error for several methods.** [fitting.py:2105](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/fitting.py:2105) checks `hit` only after `_run_fit_impl` returns normally. Cancellation-induced exceptions skip that check. Real numerical probes produced an `AttributeError` for Levenberg–Marquardt and `RuntimeError` for Nelder–Mead and DE. With an expired poll marker and no explicit cancel marker, job records consequently became `error` with HTTP 500/422 instead of `cancelled`. Normalize cancellation on exceptional exits while preserving unrelated errors.
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25400:+4. **MINOR — The public acceptance checker can hang indefinitely.** [scripts/public_fit_poll_check.py:59](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/scripts/public_fit_poll_check.py:59) stops only when status changes. If the owning worker dies, its record remains `running`; subsequent polls succeed with an increasingly stale heartbeat. The script ignores that heartbeat and has no overall deadline, so it never reports failure or advances to the remaining targets.
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25404:+**VERDICT: NO-GO**
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25407:+1. **MAJOR — Re-running does not cancel the previous fit.** [templates/index.html:8176](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8176) checks only tab identity and model equality. Ctrl/Cmd+F calls `runFit()` despite the disabled button. Pressing it again with unchanged inputs starts another job; both remain polled, preventing abandonment cancellation. Reproduced: two starts, two pending polls, zero cancellations. The older fit can finish first and cause the replacement to be discarded as “model edited.” Track a per-owner invocation and cancel its predecessor.
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25409:+2. **MAJOR — Fit concurrency is unbounded.** [app.py:672](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:672) launches two threads for every accepted start without admission control or a bounded queue. Gunicorn’s four synchronous workers therefore no longer bound concurrent fitting work. A filesystem-mocked probe accepted 12 starts in one process and retained 24 job threads. Repeated submissions or simultaneous students can accumulate CPU-heavy fits and numerical allocations, degrading polling and potentially exhausting memory. Bound active jobs and queued requests.
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25411:+3. **MINOR — Abandonment cancellation becomes a solver error for several methods.** [fitting.py:2105](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/fitting.py:2105) checks `hit` only after `_run_fit_impl` returns normally. Cancellation-induced exceptions skip that check. Real numerical probes produced an `AttributeError` for Levenberg–Marquardt and `RuntimeError` for Nelder–Mead and DE. With an expired poll marker and no explicit cancel marker, job records consequently became `error` with HTTP 500/422 instead of `cancelled`. Normalize cancellation on exceptional exits while preserving unrelated errors.
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25413:+4. **MINOR — The public acceptance checker can hang indefinitely.** [scripts/public_fit_poll_check.py:59](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/scripts/public_fit_poll_check.py:59) stops only when status changes. If the owning worker dies, its record remains `running`; subsequent polls succeed with an increasingly stale heartbeat. The script ignores that heartbeat and has no overall deadline, so it never reports failure or advances to the remaining targets.
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25417:+**VERDICT: NO-GO**
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25419:+2. **MAJOR — Fit execution has no concurrency limit.** [app.py:672](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:672)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25422:+3. **MINOR — Cancellation exceptions bypass `FitCancelled`.** [fitting.py:2105](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/fitting.py:2105)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25425:+4. **MINOR — Acceptance checker can poll a dead worker forever.** [scripts/public_fit_poll_check.py:59](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/scripts/public_fit_poll_check.py:59)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25430:+**VERDICT: NO-GO**
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25433:+1. **MAJOR — Re-running does not supersede the previous job.** [templates/index.html:8175](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8175)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25436:+2. **MAJOR — Fit execution has no concurrency limit.** [app.py:672](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:672)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25439:+3. **MINOR — Cancellation exceptions bypass `FitCancelled`.** [fitting.py:2105](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/fitting.py:2105)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25442:+4. **MINOR — Acceptance checker can poll a dead worker forever.** [scripts/public_fit_poll_check.py:59](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/scripts/public_fit_poll_check.py:59)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25447:+**VERDICT: NO-GO**
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25471:+| 1 | MAJOR: a re-run did not supersede — Ctrl/Cmd+F calls `runFit` past the disabled button; two jobs for one tab, the older could finish first and get the newer discarded as "model edited" | `_fitJobByOwner` (WeakMap keyed by the tab record): a new start for the same tab cancels the previous job on the server; the superseded loop returns `{ _abandoned: 'superseded' }` and its caller does NOTHING (the new fit owns spinner and result; Auto-Fit does not roll back, which would overwrite the new fit's model). Run Fit and Auto-Fit both pass their tab as `owner`. |
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25472:+| 2 | MAJOR: unbounded concurrency — a thread per start, where four sync workers used to bound concurrent fits at four | each worker process runs at most `FIT_JOB_MAX_RUNNING` = 1 fit (a semaphore); the rest wait `queued` (heartbeating, cancellable, a queued job cancelled or abandoned never runs); at most `FIT_JOB_MAX_ADMITTED` = 6 running + queued per process, beyond that `/api/fit/start` answers 503 "The server is busy with other fits" at once (the page shows it as a failed fit). Production: ≤ 4 concurrent fits, as before. |
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25473:+| 3 | MINOR: a cancellation observed mid-fit could surface as the solver's own error (AttributeError from Levenberg-Marquardt, RuntimeError from Nelder-Mead / DE) — an abandoned job became `error` 500 / 422 | `run_fit(cancel=)` turns any exception raised after cancellation was observed into `FitCancelled`; unrelated errors propagate unchanged |
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25474:+| 4 | MINOR: `public_fit_poll_check.py` could poll a dead worker's record forever | a heartbeat older than 30 s is FAIL "lost"; a 20-minute deadline per target (the job is cancelled) |
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25484:+| 1 | MAJOR: ownership was registered when the START RESPONSE arrived, so response order decided it — A pressed first, B second, A's late response cancelled B and A's stale result applied | an OPERATION per tab, claimed BEFORE THE CALLER'S FIRST AWAIT (`_claimFitOp`; runFit right after its context key, Auto-Fit before its upload): the newest claim is current whatever order the responses come in; a claim cancels the previous operation's job; a start response that arrives for a superseded operation cancels its own job |
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25485:+| 2 | MAJOR: supersession was checked only before a poll, never after its reply — a late `done` applied a stale result, a late `cancelled` threw and Auto-Fit rolled back over the newer fit | `_serverFitJob` rechecks `_fitOpCurrent(op)` after every await and before every exit, and its outer catch turns ANY error of a superseded operation (incl. the Auto-Fit timeout) into `{ _abandoned: 'superseded' }`; both callers' catch paths check it first (runFit: no local fallback; Auto-Fit: no rollback, no message) |
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:25486:+| 3 | MINOR: if the heartbeat thread failed to start after the fit thread had, the admission was released twice (seven outstanding against six) | the heartbeat thread starts FIRST; a failure to start either thread raises before the worker runs (the route releases once); once the worker has started only its finally releases. Fault-injection test fails on round 1's code, passes now. |
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:28024:+1. **MAJOR — Auto-Fit claims ownership after its first await.** [templates/index.html:7692](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7692)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:28027:+2. **MINOR — An abandoned tab’s fit hides another tab’s active spinner.** [templates/index.html:8230](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8230)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:28034:+**VERDICT: NO-GO**
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:28037:+1. **MAJOR — Auto-Fit claims ownership after its first await.** [templates/index.html:7692](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7692)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:28040:+2. **MINOR — An abandoned tab’s fit hides another tab’s active spinner.** [templates/index.html:8230](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8230)  
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:28047:+**VERDICT: NO-GO**
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:28054:+Re-review unit 2 (long fits via start-then-poll), round 4 (the last allowed): branch fix-fit-start-poll. The round-3 fixes are the latest commit (git diff HEAD~1..HEAD); the whole unit is git diff fix-acceptance-holes..HEAD. Earlier verdicts: docs/autofit/codex/fit_start_poll_verdict_run{A,B}.md, _r2_, _r3_; the round-1 prompt holds the brief, design, sites and acceptance; plan docs/superpowers/plans/2026-09-27-long-fits-start-poll.md section 6 lists every finding and fix. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:28064:+| 1 | MAJOR (B): Auto-Fit claimed its operation AFTER its confirmation modal (its first await): a Run Fit pressed while the modal was open was cancelled when the student confirmed, and the older Auto-Fit's result applied | an operation is NUMBERED at the press (`_newFitOp`, before the modal) and INSTALLED as the tab's current one after it (`_installFitOp`), only if no newer operation claimed the tab meanwhile — otherwise the confirmed Auto-Fit returns having changed nothing (no snapshot, no request). Claiming at the press would have cancelled a running Run Fit merely for opening the modal. Run Fit, which has no modal, claims = numbers + installs at once. |
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:28065:+| 2 | MINOR (A, B): the fit spinner is page-wide; a fit discarded on tab A hid tab B's running spinner, re-enabled Run Fit and cleared the in-flight flag | the spinner belongs to the operation that showed it (`_fitSpinnerOp`); every hide after a caller's claim is `_hideFitSpinnerFor(op)`, a no-op for any other operation |
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:28073:+Finish with VERDICT: GO or VERDICT: NO-GO.
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:28090:+| 1 | MAJOR (B): Auto-Fit claimed its operation AFTER its confirmation modal (its first await): a Run Fit pressed while the modal was open was cancelled when the student confirmed, and the older Auto-Fit's result applied | an operation is NUMBERED at the press (`_newFitOp`, before the modal) and INSTALLED as the tab's current one after it (`_installFitOp`), only if no newer operation claimed the tab meanwhile — otherwise the confirmed Auto-Fit returns having changed nothing (no snapshot, no request). Claiming at the press would have cancelled a running Run Fit merely for opening the modal. Run Fit, which has no modal, claims = numbers + installs at once. |
docs/autofit/codex/fit_start_poll_r4_verdict_runB.md:28091:+| 2 | MINOR (A, B): the fit spinner is page-wide; a fit discarded on tab A hid tab B's running spinner, re-enabled Run Fit and cleared the in-flight flag | the spinner belongs to the operation that showed it (`_fitSpinnerOp`); every hide after a caller's claim is `_hideFitSpinnerFor(op)`, a no-op for any other operation |

codex
The install check now rejects an older Auto-Fit confirmation before it changes state when a newer Run Fit owns the tab. I’m checking early exits and shared spinner paths next, where an operation may end before taking ownership of the spinner.
exec
/bin/zsh -lc "sed -n '7460,7840p' templates/index.html && sed -n '8050,8420p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
// transport failure (the caller's local fallback, as before); a poll that
// cannot is retried and only FIT_POLL_TRANSPORT_RETRIES in a row are. A
// record whose heartbeat stops (a restarted worker takes the fit thread with
// it) is a failed fit, never an endless spinner. Cancellation also reaches
// the server when the page is closed (pagehide beacon) and, server-side,
// when polls stop for three minutes (above the ~1-minute timer throttling of a hidden browser tab).
const FIT_POLL_MS = 500;
const FIT_POLL_TRANSPORT_RETRIES = 5;
const FIT_HEARTBEAT_LOST_SEC = 30;
const _runningFitJobs = new Set();
// One fit OPERATION per tab record (unit 2, Codex rounds 1-2). A caller claims
// its operation BEFORE ITS FIRST AWAIT (_claimFitOp): the newest claim for a
// tab is the current one, whatever order the server's responses come back in.
// A claim cancels the previous operation's server job; the previous
// operation's _serverFitJob, at every step after an await and before every
// exit — a result, an error, a timeout — sees it is no longer current,
// cancels its own job if it has one, and returns { _abandoned: 'superseded' },
// on which its caller does NOTHING (the newer fit owns spinner and result).
// Ctrl/Cmd+F bypasses the disabled Run Fit button, and Run Fit and Auto-Fit
// share a tab.
let _fitOpSeq = 0;
const _fitOpByOwner = new WeakMap();
// An operation is NUMBERED when the student presses the button (_newFitOp) and
// INSTALLED as its tab's current one when it is about to change anything
// (_installFitOp) — only if no newer operation has claimed the tab meanwhile
// (Codex round 3: Auto-Fit's confirmation modal sits between the two; a Run
// Fit pressed while it is open must win, and opening the modal must not kill
// a running fit the student may still keep by cancelling the modal).
function _newFitOp(owner) { return { seq: ++_fitOpSeq, owner: owner || null, jobId: null }; }
function _installFitOp(op) {
  if (!op || !op.owner) return true;
  const cur = _fitOpByOwner.get(op.owner);
  if (cur && cur.seq > op.seq) return false;          // a newer operation owns the tab
  if (cur && cur !== op && cur.jobId) _cancelFitJob(cur.jobId);
  _fitOpByOwner.set(op.owner, op);
  return true;
}
function _claimFitOp(owner) { const op = _newFitOp(owner); _installFitOp(op); return op; }
function _fitOpCurrent(op) { return !op || !op.owner || _fitOpByOwner.get(op.owner) === op; }
// The fit spinner is page-wide, one per page; the operation that showed it
// owns it. A fit that ends after another tab's fit took the spinner leaves it
// alone (Codex round 3: a discarded tab-A fit hid tab B's running spinner).
let _fitSpinnerOp = null;
function _hideFitSpinnerFor(op) {
  if (_fitSpinnerOp !== op) return;
  _fitSpinnerOp = null;
  _hideFitSpinner();
}
function _cancelFitJob(jobId) {
  try { fetch('/api/fit/cancel/' + encodeURIComponent(jobId), { method: 'POST', keepalive: true }).catch(() => {}); } catch (_) { /* best effort */ }
}
if (typeof window !== 'undefined' && window.addEventListener) {
  window.addEventListener('pagehide', () => {
    for (const id of _runningFitJobs) {
      try { navigator.sendBeacon('/api/fit/cancel/' + encodeURIComponent(id)); } catch (_) { /* best effort */ }
    }
  });
}
function _fitHttpError(status, msg, prefix) {
  const err = new Error(msg || ((prefix || 'Fit request failed') + ' (HTTP ' + status + ').'));
  err.serverError = true;
  err.httpStatus = status;
  return err;
}
async function _serverFitJob(fitReq, guard) {
  guard = guard || {};
  const op = guard.op || null;
  const SUP = { _abandoned: 'superseded' };
  let jobId = null;
  const gone = () => !_fitOpCurrent(op);
  const superseded = () => { if (jobId) _cancelFitJob(jobId); return SUP; };
  const isTransport = e => e && !e.serverError && (e instanceof TypeError || e.name === 'AbortError');
  try {
    if (gone()) return SUP;
    let resp;
    try {
      resp = await fetch('/api/fit/start', { method: 'POST', headers: { 'Content-Type': 'application/json' },
                                             body: JSON.stringify(fitReq), signal: guard.signal });
    } catch (e) { if (isTransport(e)) e.transportFailure = true; throw e; }
    if (resp.ok === false) {
      let msg = null;
      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
      throw _fitHttpError(resp.status, msg);
    }
    let started;
    try { started = await _readFitReply(resp); } catch (e) { if (isTransport(e)) e.transportFailure = true; throw e; }
    jobId = started && started.job_id;
    if (!jobId) throw _fitHttpError(resp.status, 'The server did not start the fit (no job id).');
    _runningFitJobs.add(jobId);
    if (gone()) return superseded();            // a newer claim came while this start was in flight
    if (op) op.jobId = jobId;
    let misses = 0;
    while (true) {
      await new Promise(r => setTimeout(r, FIT_POLL_MS));
      if (gone()) return superseded();
      if (guard.signal && guard.signal.aborted) {
        _cancelFitJob(jobId);
        throw guard.signal.reason || new DOMException('aborted', 'AbortError');
      }
      const why = guard.abandoned ? guard.abandoned() : null;
      if (why) { _cancelFitJob(jobId); return { _abandoned: why }; }
      let pr, rec;
      try {
        pr = await fetch('/api/fit/progress/' + encodeURIComponent(jobId), { signal: guard.signal });
      } catch (e) {
        if (gone()) return superseded();
        if (e && e.name === 'AbortError') { _cancelFitJob(jobId); throw e; }
        if (++misses >= FIT_POLL_TRANSPORT_RETRIES) {
          _cancelFitJob(jobId);
          const err = new Error('Lost contact with the server during the fit (' + ((e && e.message) || 'network error') + ').');
          err.transportFailure = true;
          throw err;
        }
        continue;
      }
      if (gone()) return superseded();            // the reply of a poll made before a newer claim
      if (pr.ok === false) {
        _cancelFitJob(jobId);
        let msg = null;
        try { const j = await pr.json(); msg = (j && j.error) || null; } catch (_) { /* non-JSON body */ }
        throw _fitHttpError(pr.status, msg, 'Lost the fit\'s progress');
      }
      try { rec = await _readFitReply(pr); } catch (e) {
        if (gone()) return superseded();
        if (e && e.unreadableReply) { _cancelFitJob(jobId); throw e; }
        if (++misses >= FIT_POLL_TRANSPORT_RETRIES) {
          _cancelFitJob(jobId);
          if (isTransport(e)) e.transportFailure = true;
          throw e;
        }
        continue;
      }
      if (gone()) return superseded();
      misses = 0;
      if (rec.status === 'done') return rec.result;
      if (rec.status === 'error') throw _fitHttpError(rec.http_status || 500, rec.error);
      if (rec.status === 'cancelled') throw _fitHttpError(409, 'The fit was stopped on the server before it finished. Run it again.');
      if (Number.isFinite(rec.heartbeat_age_sec) && rec.heartbeat_age_sec > FIT_HEARTBEAT_LOST_SEC) {
        _cancelFitJob(jobId);
        throw _fitHttpError(503, 'The server stopped working on the fit (no sign of it for ' + Math.round(rec.heartbeat_age_sec) +
                                 ' s — it was probably restarted). Run the fit again.');
      }
      if (typeof guard.onProgress === 'function') guard.onProgress(rec);
    }
  } catch (e) {
    if (gone()) return superseded();              // superseded wins over any error, incl. a timeout
    throw e;
  } finally {
    if (jobId) _runningFitJobs.delete(jobId);
    if (op && op.jobId === jobId) op.jobId = null;
  }
}

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
  // unit 2: this press's fit operation, numbered NOW (before the modal) and
  // installed after it, only if no newer operation claimed the tab meanwhile
  const afOp = _newFitOp(fittingTab);
  // Confirmation if existing peaks
  if (state.peaks.length >= 1) {
    const proceed = await _showAutoFitConfirmModal(state.peaks.length);
    if (!proceed) return;
    if (!_ownerActive(fittingTab)) {
      notify('Auto-fit cancelled — the tab changed while the confirmation was open.', 'amber');
      return;
    }
  }

  // a Run Fit pressed while the confirmation was open is newer: it wins, and
  // this Auto-Fit does nothing at all (nothing has been changed yet)
  if (!_installFitOp(afOp)) return;
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
  _fitSpinnerOp = afOp;
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
      op: afOp,
      signal: ctrl.signal,
      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
    });
    clearTimeout(timer);
    // superseded by a newer fit on this tab (Run Fit pressed during Auto-Fit):
    // that fit started from the model now on the tab and owns the result — no
    // rollback here, which would overwrite it
    if (json && json._abandoned === 'superseded') return;
    // F2: a non-2xx reply is a failed REQUEST with its status in the message
    // (_serverFitJob throws it with httpStatus); an unreadable reply is a
    // failed fit with its own message (unreadableReply).
    if (json && json._abandoned === 'tab') {
      _hideFitSpinnerFor(afOp);
      notify('Auto-fit discarded — tab switched during fit.', 'amber');
      _autoFitRestore(snap, fittingTab);
      return;
    }
    if (json && json._abandoned === 'model') {
      _hideFitSpinnerFor(afOp);
      notify('Auto-fit discarded because the model or its background / ROI settings were edited while it was running. Previous peaks and result restored. Run it again.', 'amber', true);
      _autoFitRestore(snap, fittingTab);
      return;
    }
    if (json.error) throw new Error(json.error);
    if (json.success !== true) throw new Error(json.message || 'fit did not converge');
    if (!_ownerActive(fittingTab)) {
      _hideFitSpinnerFor(afOp);
      notify('Auto-fit discarded — tab switched during fit.', 'amber');
      _autoFitRestore(snap, fittingTab);
      return;
    }
    if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
      _hideFitSpinnerFor(afOp);
      notify('Auto-fit discarded because the model or its background / ROI settings were edited while it was running. Previous peaks and result restored. Run it again.', 'amber', true);
      _autoFitRestore(snap, fittingTab);
      return;
    }

    applyBackendResult(json);

    const ok = applyAutoFitResult(json, graphiteRaw, { be: be2, inten: inten2, bgIntensity: bgI, bgSubtracted: bgSub });
    if (!ok) {
      _hideFitSpinnerFor(afOp);
      _autoFitRestore(snap, fittingTab);
      return;
    }

    _hideFitSpinnerFor(afOp);
    notify('Auto-fit complete. χ²ᵣ = ' + (state.fitResult?.chiReduced?.toFixed(3) || '?'), 'green');
  } catch (e) {
    clearTimeout(timer);
    // superseded (Run Fit pressed during Auto-Fit): nothing at all — no
    // rollback (it would overwrite the newer fit's model), no message
    if (afOp && !_fitOpCurrent(afOp)) return;
    _hideFitSpinnerFor(afOp);
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
  if (!Number.isFinite(lo) || !Number.isFinite(hi)) {
    // Fall back to full raw range (no UI ROI set yet)
    let rmin = Infinity, rmax = -Infinity;
    for (const v of tab.rawBE) {
      if (v < rmin) rmin = v;
      if (v > rmax) rmax = v;
    }
    lo = rmin; hi = rmax;
  }
  if (!Number.isFinite(lo) || !Number.isFinite(hi)) return false;
  const mid = (lo + hi) / 2;
  return mid >= 270.0 && mid <= 315.0;
}

// ── Scattered-starts check (2026-09-21) ───────────────────────────────────────
function _startsEv(ev) { return (ev >= 0 ? '+' : '−') + Math.abs(ev).toFixed(2) + ' eV'; }

function _startsShiftHtml(shift) {
  const bold = Math.abs(shift.ev) > _STARTS_SHIFT_AMBER_EV ? 600 : 400;
  return `<span style="color:${_startsShiftColour(shift.ev)};font-weight:${bold}">${_escHtml(_startsPeakName(shift.id))} ${_startsEv(shift.ev)}</span>`;
}

function _startsPanelHtml(fr) {
  if (!fr || !fr.starts || !fr.starts.ran) return '';
  const st = _startsIfCurrent(fr, _startsLiveKey());
  if (!st) {
    return `<div class="starts-panel" style="margin-top:10px;font-size:11px;line-height:1.5;color:var(--text3)">&#8635; The model has changed since this fit, so its scattered-starts comparison no longer applies. Run the fit again to compare starts.</div>`;
  }
  let html = `<div class="starts-panel" style="margin-top:10px;font-size:11px;line-height:1.5">
    <div data-xps-tip="${_escHtml(_STARTS_TOOLTIP)}" style="color:var(--text2)">&#8635; ${_escHtml(_startsSummaryText(st))}</div>`;
  if (fr.chosenAlternative) {
    const c = fr.chosenAlternative;
    html += `<div style="color:var(--text3);margin-top:2px">This fit started from a solution you chose from the scattered starts (χ²ᵣ ${Number(c.fromChi).toFixed(2)} → ${Number(c.toChi).toFixed(2)}; largest move from your original start: ${_escHtml(c.shiftName)} ${_startsEv(c.shiftEv)}).</div>`;
  }
  const alts = st.alternatives || [];
  if (!alts.length) return html + '</div>';
  const comps = st.fit.components;
  const head = comps.map(c => `<th style="text-align:right;padding:2px 4px">${_escHtml(_startsPeakName(c.id))}<br><span style="font-weight:400;color:var(--text3)">area % &middot; move</span></th>`).join('');
  // every component: its OWN area fraction and its OWN move from the student's start.
  // A component this fit did not support shows neither (the same rule as the
  // Results table); an alternative's components are unjudged (no verdict was
  // computed for that solution) and are shown as they are.
  const cell = (c, judged, scale) => {
    const pk = getPeak(Number(c.id)) || getPeak(c.id);
    if (judged && pk && _isUnsupported(pk)) return `<td style="text-align:right;padding:2px 4px;color:var(--text3)" title="${_escAttr(_UNSUPPORTED_TIP)}">${_UNSUPPORTED_LABEL}</td>`;
    return `<td style="text-align:right;padding:2px 4px;font-family:var(--mono)">${(c.area_percent * scale).toFixed(1)}<br><span style="color:${_startsShiftColour(c.center_shift_from_start)}">${_startsEv(c.center_shift_from_start)}</span></td>`;
  };
  const largest = (cs, judged) => {
    // the largest move among components this fit supports (an unsupported one has no position to move)
    const eligible = cs.filter(c => { const pk = getPeak(Number(c.id)) || getPeak(c.id); return !(judged && pk && _isUnsupported(pk)); });
    return eligible.length ? eligible.reduce((m, c) => Math.abs(c.center_shift_from_start) > Math.abs(m.center_shift_from_start) ? c : m) : null;
  };
  const row = (label, chi, n, cs, judged, actions) => { const big = largest(cs, judged);
    // the judged row's percentages are over the components this fit supports (as in the Results table)
    const supportedPct = judged ? cs.reduce((t, c) => { const pk = getPeak(Number(c.id)) || getPeak(c.id); return t + ((pk && _isUnsupported(pk)) ? 0 : c.area_percent); }, 0) : 100;
    const scale = supportedPct > 0 ? 100 / supportedPct : 1;
    return `<tr style="border-top:1px solid var(--border)">
      <td style="padding:2px 4px">${label}</td><td style="text-align:right;padding:2px 4px;font-family:var(--mono)">${chi.toFixed(2)}</td>
      <td style="text-align:right;padding:2px 4px">${n}</td>
      ${cs.map(c => cell(c, judged, scale)).join('')}
      <td style="padding:2px 4px">${big ? _startsShiftHtml({ id: big.id, ev: big.center_shift_from_start }) : '&mdash;'}</td><td style="padding:2px 4px;white-space:nowrap">${actions}</td></tr>`; };
  html += `<h4 style="font-size:11px;margin:8px 0 4px" title="Solutions other starts reached with a lower reduced chi-square than your fit. A lower value is not a better chemical model: look at where the components went.">Other solutions found</h4>
    <div style="overflow-x:auto"><table style="width:100%;font-size:10px;border-collapse:collapse">
    <thead><tr><th style="text-align:left;padding:2px 4px">solution</th><th style="text-align:right;padding:2px 4px">χ²ᵣ</th><th style="text-align:right;padding:2px 4px" title="how many of the scattered starts ended here">starts here</th>${head}<th style="text-align:left;padding:2px 4px">largest move from your start</th><th></th></tr></thead><tbody>`;
  html += row('<b>Your fit</b>', st.fit.chi2r, st.n_same_as_fit, comps, true, '');
  alts.forEach((a, k) => {
    html += row('Alternative ' + (k + 1), a.chi2r, a.n_starts, a.components, false,
      `<button class="btn btn-sm" onclick="previewAlternative(${k})" title="Overlay this solution on the chart; click again to clear">Preview</button>
       <button class="btn btn-sm" onclick="useAlternative(${k})" title="Run the fit again starting from this solution. Your model changes only if that fit succeeds; you can undo it.">Use this solution</button>`);
  });
  return html + '</tbody></table></div></div>';
}

// The alternative's parameters on a COPY of the current peaks (null when the
// evidence no longer describes the current model).
function _altPeaks(alt) {
  if (!_startsIfCurrent(state.fitResult, _startsLiveKey())) return null;
  const peaks = JSON.parse(JSON.stringify(state.peaks));
  if (peaks.length !== alt.components.length) return null;
  for (const c of alt.components) {
    const p = peaks.find(q => String(q.id) === String(c.id));
    if (!p) return null;
    const par = {};
    for (const k in c.params) par[k] = { value: c.params[k] };
    _applyBackendParams(p, par);
  }
  return peaks;
}

function _currentAlternative(k) {
  const st = _startsIfCurrent(state.fitResult, _startsLiveKey());
  return (st && st.ran && st.alternatives && st.alternatives[k]) || null;
}

const _STARTS_STALE_MSG = 'The model has changed since this fit. Run the fit again to compare solutions.';

function previewAlternative(k) {
  const alt = _currentAlternative(k);
  const peaks = alt && _altPeaks(alt);
  if (!peaks) { notify(_STARTS_STALE_MSG, 'amber', true); return; }
  const key = 'alt:' + k;
  if (_historyPreview && _historyPreview.snapId === key) { _historyClearPreview(); return; }
  _historyPreview = { snapId: key, altKey: state.fitResult.startsModelKey, peaks, fitResult: { chiReduced: alt.chi2r } };
  _updateLocalModelBanner();
  document.querySelectorAll('.hist-row').forEach(r => r.classList.remove('hist-preview-active'));
  updatePlot();
}

// Adopting an alternative is the student's decision: explicit, undoable, and
// recorded. It is ATOMIC by construction: the alternative is only the START of
// an ordinary server fit (runFit's opts.startPeaks); the live model is written
// by that fit's success path and by nothing else, so a fit that fails, does
// not converge, is discarded because the tab changed, or cannot reach the
// server leaves peaks and result exactly as they were (no local fallback
// here: the local engine would start from the live model, not from the
// alternative). runFit's own pushUndo is the single undo entry. A solution
// that moves a component more than 1 eV from where the student put it is the
// measured trap (a lower chi-square bought by a chemically absurd relocation),
// so that case — and only that case — asks first, naming the component and
// the distance.
async function useAlternative(k) {
  const alt = _currentAlternative(k);
  const peaks = alt && _altPeaks(alt);
  if (!peaks) { notify(_STARTS_STALE_MSG, 'amber', true); return; }
  const shift = alt.largest_centre_shift_from_start;
  const name = _startsPeakName(shift.id);
  if (Math.abs(shift.ev) > _STARTS_SHIFT_RED_EV &&
      !confirm(`This solution moves ${name} by ${_startsEv(shift.ev)} from where you placed it. Apply?`)) return;
  const chosen = { fromChi: state.fitResult.starts.fit.chi2r, toChi: alt.chi2r, shiftName: name, shiftEv: shift.ev };
  if (_historyPreview) _historyClearPreview();
  await runFit({ startPeaks: peaks, chosenAlternative: chosen });
}

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
  let fitOp = null;         // unit 2: this tab's fit operation, claimed before the first await
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
    fitOp = _claimFitOp(fittingTab);   // before the first await: the newest claim for a tab is current
    _fitSpinnerOp = fitOp;             // the spinner shown above is this operation's
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
      op: fitOp,
      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
    });
    if (json && json._abandoned === 'superseded') return;   // a newer fit on this tab owns the spinner and the result
    if (json && json._abandoned === 'tab') {
      _hideFitSpinnerFor(fitOp);
      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
      notify('Fit result discarded because you switched tabs during the fit.', 'amber');
      return;
    }
    if (json && json._abandoned === 'model') {
      _hideFitSpinnerFor(fitOp);
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
      _hideFitSpinnerFor(fitOp);
      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
      notify('Fit result discarded because you switched tabs during the fit.', 'amber');
      return;
    }

    // The peak controls stay editable while the fit runs. A result computed for
    // the model as it was must not be applied over an edited one (a newly locked
    // centre would keep its edited value under the server's statistics).
    if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
      _hideFitSpinnerFor(fitOp);
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
    _hideFitSpinnerFor(fitOp);
    notify('Fit complete. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3), 'green');
  } catch (e) {
    // superseded (a newer fit on this tab): nothing at all — no message, no
    // local fallback, the newer fit owns the spinner and the result
    if (fitOp && !_fitOpCurrent(fitOp)) return;
    // Fall back to local Levenberg-Marquardt
    _hideFitSpinnerFor(fitOp);
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
      _hideFitSpinnerFor(fitOp);
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
  _autoSnapshot();
}

// Label for the goodness-of-fit statistic a fit result carries. The server
// and (since unit W1, 2026-09-18) the local engine both minimise a
// counting-noise-weighted chi-square; local results saved by unit A0 were
// UNWEIGHTED and keep the label "Residual variance", never chi-square.
function _isUnweightedLocal(fr) { return !!(fr && fr.objective === 'unweighted_residual_variance'); }
function _fitStatLabel(fr) {
  return _isUnweightedLocal(fr) ? 'Residual variance' : 'χ²ᵣ';
}
// A LOCAL result is a STARTING POINT, not a reportable result. Measured in
// unit W1 (docs/superpowers/plans/2026-09-18-local-engine-poisson-weighting.md):
// with Poisson weighting the local engine matches the server on GL-type
// models (<= 4 meV, <= 1.4 % area on the lab's C1s scans) and, since A03
// (2026-09-22: Voigt = fixed eta 0.5 on BOTH sides), on Voigt components
// wherever the two engines reach the same minimum (5 of 9 committed U 4f
// targets: every component within 4.3 meV, 2.6 % FWHM, 2 % area, 0.12 pp);
// it still differs where an LA component's m moves on the server (held,
// exactly, at its start locally - LA is discontinuous in m, caM unit) and
// where the model has several minima; and it gives no uncertainties. Unweighted A0-era results differed by more than 100 %.
// Every site that shows, exports or saves a fit result carries the
// designation, keyed on persisted identity so reloaded results are labelled.
const _LOCAL_FIT_CAVEAT = 'Local fit (Poisson-weighted like the server, no uncertainties): a starting point, not a reportable result. Run Fit before reporting.';
const _LOCAL_FIT_CAVEAT_UNWEIGHTED = 'Local unweighted fit: a starting point, not a reportable result. Run Fit before reporting.';
function _isLocalProvenance(p) {
  return !!(p && (p.engine === 'local' || p.objective === 'unweighted_residual_variance' || p.objective === 'poisson_weighted_chi_square'));
}
function _isLocalFit(fr) { return _isLocalProvenance(fr); }
// The record that governs the active model's designation: its live result,
// else the provenance it was imported / copied / restored with.
function _governingProvenance() {
  if (state.fitResult) return state.fitResult;
  const t = _activeTab();
  return (t && t.modelProvenance) || null;
}
function _localFitDetail(fr) {
  return _isUnweightedLocal(fr)
    ? 'Its areas can differ from the server fit by more than 100&nbsp;%.'
    : 'It can differ from the server fit for LA components (the page holds the smoothing parameter m at its start; the server fits it) or where the model has several minima.';
}
// The designation follows the MODEL, not only a live fit result: parameters
// imported from a .fit.json that was saved from a local fit are a starting
// point too (tab.modelProvenance, set by fromJSON, cleared by any new fit).
function _isLocalModel() {
  if (state.fitResult) return _isLocalFit(state.fitResult);
  const t = _activeTab();

exec
/bin/zsh -lc "rg -n '_showFitSpinner|_hideFitSpinner|_fitInFlight|_showAutoFitConfirmModal|_autoFitConfirmResolver|async function runBatch|async function.*[Ff]ind|_ownerActive|_opOwner' templates/index.html && cat package.json && sed -n '1,320p' tests/js/fit_start_poll.test.js" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 exited 1 in 0ms:
2347:function _opOwner() {
2354:function _ownerActive(owner) {
6688:function _showFitSpinner() {
6697:  _showFitSpinner._timer = setTimeout(() => {
6701:function _hideFitSpinner() {
6705:  clearTimeout(_showFitSpinner._timer);
6736:let _autoFitConfirmResolver = null;
6737:function _showAutoFitConfirmModal(peakCount) {
6739:    _autoFitConfirmResolver = resolve;
6745:      const r = _autoFitConfirmResolver; _autoFitConfirmResolver = null;
6753:  const r = _autoFitConfirmResolver; _autoFitConfirmResolver = null;
6976:    owner:        _opOwner(),
6985:    modelProvenance: (() => { const o = _opOwner(); return o && o.modelProvenance ? JSON.parse(JSON.stringify(o.modelProvenance)) : null; })(),
7503:function _hideFitSpinnerFor(op) {
7506:  _hideFitSpinner();
7624:  const fittingTab = _opOwner();
7631:    const proceed = await _showAutoFitConfirmModal(state.peaks.length);
7633:    if (!_ownerActive(fittingTab)) {
7688:  _showFitSpinner();
7748:      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
7759:      _hideFitSpinnerFor(afOp);
7765:      _hideFitSpinnerFor(afOp);
7772:    if (!_ownerActive(fittingTab)) {
7773:      _hideFitSpinnerFor(afOp);
7779:      _hideFitSpinnerFor(afOp);
7789:      _hideFitSpinnerFor(afOp);
7794:    _hideFitSpinnerFor(afOp);
7801:    _hideFitSpinnerFor(afOp);
8173:  _showFitSpinner();
8179:  const fittingTab = _opOwner();
8250:      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
8254:      _hideFitSpinnerFor(fitOp);
8260:      _hideFitSpinnerFor(fitOp);
8282:    if (!_ownerActive(fittingTab)) {
8283:      _hideFitSpinnerFor(fitOp);
8293:      _hideFitSpinnerFor(fitOp);
8324:    _hideFitSpinnerFor(fitOp);
8331:    _hideFitSpinnerFor(fitOp);
8332:    if (!_ownerActive(fittingTab)) {
8347:      _hideFitSpinnerFor(fitOp);
8520:    _hideFitSpinner();
8881:  _hideFitSpinner();
10862:  const owner = _opOwner();   // a .fit.json applies to the tab active when the file was chosen
10888:      if (!_ownerActive(owner)) { notify('Fit file not applied — the tab changed while the file was being read.', 'amber'); return; }
10906:      if (!_ownerActive(owner)) { notify('Fit file not applied — the tab changed while the file was being read.', 'amber'); return; }
15136:  const t = owner || _opOwner();
15608:async function openFindPeaksModal() {
16110:async function runFindPeaks() {
16157:    const owner = _opOwner();
16205:    if (!_ownerActive(owner)) {
16357:// _showAutoFitConfirmModal/_autoFitConfirmCancel.
16377:async function applyFindPeaks() {
16378:  const owner = _opOwner();              // the record this apply belongs to
16388:  if (!_ownerActive(owner)) {
cat: package.json: No such file or directory

exec
/bin/zsh -lc 'for p in docs/autofit/codex/fit_start_poll_verdict_runA.md docs/autofit/codex/fit_start_poll_verdict_runB.md docs/autofit/codex/fit_start_poll_r2_verdict_runA.md docs/autofit/codex/fit_start_poll_r2_verdict_runB.md docs/autofit/codex/fit_start_poll_r3_verdict_runA.md docs/autofit/codex/fit_start_poll_r3_verdict_runB.md; do tail -35 "$p"; done' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
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
 const c={setTimeout:f=>{setImmediate(f)},DOMException,fetch:async u=>{
 if(u==='\\''/api/fit/start'\\''){const j='\\''J'\\''+(++n);if(j==='\\''J1'\\''&&"'!latePoll)await gate.p;return ok({job_id:j});}
 if(u.includes('"'\\''/cancel/'\\'')){cancels.push(u);return ok({});}
 const j=u.split('\\''/'\\'').pop();if(j==='\\''J1'\\''&&latePoll){polled.res();await gate.p;}return ok({status:'\\''done'\\'',result:{job:j}});}};
 vm.createContext(c);vm.runInContext('\\''const FIT_POLL_MS=500,FIT_POLL_TRANSPORT_RETRIES=5,FIT_HEARTBEAT_LOST_SEC=30;const _runningFitJobs=new Set(),_fitJobByOwner=new WeakMap(),_fitOpByOwner=new WeakMap();let _fitOpSeq=0;\\n'\\''+['\\''_cancelFitJob'\\'','\\''_fitHttpError'\\'','\\''_readFitReply'\\'','\\''_serverFitJob'\\''].map(n=>extract(src,n)).join('\\''\\n'\\'')+(legacy?'\\'''\\'':extract(src,'\\''_claimFitOp'\\'')+'\\''\\n'\\''+extract(src,'\\''_fitOpCurrent'\\'')),c);
 const guard=()=>legacy?{owner}:{op:c._claimFitOp(owner)};
 const a=c._serverFitJob({},guard());if(latePoll)await polled.p;else await tick();
 const b=c._serverFitJob({},guard());const bv=await b;gate.res();const av=await a;return {a:av,b:bv,cancels};
}
(async()=>{for(const late of [false,true])for(const [src,legacy] of [[old,true],[current,false]])console.log(legacy?'\\''HEAD~1'\\'':'\\''HEAD'\\'',late?'\\''late poll'\\'':'\\''reverse starts'\\'',JSON.stringify(await probe(src,legacy,late)));})();
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 72ms:
HEAD reverse starts {"a":{"_abandoned":"superseded"},"b":{"job":"J2"},"cancels":["/api/fit/cancel/J1"]}
HEAD~1 late poll {"a":{"job":"J1"},"b":{"job":"J2"},"cancels":["/api/fit/cancel/J1"]}
HEAD late poll {"a":{"_abandoned":"superseded"},"b":{"job":"J2"},"cancels":["/api/fit/cancel/J1","/api/fit/cancel/J1"]}

codex
The round-2 failures reproduce against the previous commit and pass with the new code; startup fault injection also confirms a single admission release. Three numerical cancellation tests passed. The remaining finding is the cross-tab spinner issue. Confirming Auto-Fit cancels a Run Fit started while its modal was open, and the cancelled fit’s late reply stays suppressed.
codex
1. **MINOR — A discarded fit hides another tab’s active spinner.** [templates/index.html:8230](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8230). Start a fit on tab A, switch to B, and press Ctrl/Cmd+F before A’s pending poll returns. When A detects the tab change, it unconditionally calls `_hideFitSpinner()`, hiding B’s spinner, enabling Run Fit, and clearing `_bgSubFitInFlight` while B remains running. Reproduced with the actual callers. Spinner cleanup needs its own ownership check; Auto-Fit’s discard paths have the same problem.

No BLOCKER or MAJOR findings. The round-2 ownership and admission fixes held. Confirming Auto-Fit correctly cancels a Run Fit started during its modal; the cancelled fit’s late reply stays suppressed.

Validation: **88 JavaScript tests and 3 numerical cancellation tests passed**. In-memory comparisons reproduced the previous commit’s response-order, late-poll, and double-release failures and confirmed their fixes. Full filesystem-backed server acceptance and long-fit timing were not rerun under the read-only constraint. No files edited.

VERDICT: GO
tokens used
88,907
1. **MINOR — A discarded fit hides another tab’s active spinner.** [templates/index.html:8230](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8230). Start a fit on tab A, switch to B, and press Ctrl/Cmd+F before A’s pending poll returns. When A detects the tab change, it unconditionally calls `_hideFitSpinner()`, hiding B’s spinner, enabling Run Fit, and clearing `_bgSubFitInFlight` while B remains running. Reproduced with the actual callers. Spinner cleanup needs its own ownership check; Auto-Fit’s discard paths have the same problem.

No BLOCKER or MAJOR findings. The round-2 ownership and admission fixes held. Confirming Auto-Fit correctly cancels a Run Fit started during its modal; the cancelled fit’s late reply stays suppressed.

Validation: **88 JavaScript tests and 3 numerical cancellation tests passed**. In-memory comparisons reproduced the previous commit’s response-order, late-poll, and double-release failures and confirmed their fixes. Full filesystem-backed server acceptance and long-fit timing were not rerun under the read-only constraint. No files edited.

VERDICT: GO
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

exec
/bin/zsh -lc "rg -n '_showFitSpinner|_hideFitSpinner|_fitInFlight|_showAutoFitConfirmModal|_autoFitConfirmResolver|async function runBatch|async function.*[Ff]ind' templates/index.html && sed -n '8090,8255p' templates/index.html && sed -n '6990,7070p' templates/index.html && sed -n '1,70p' tests/js/fit_start_poll.test.js && ls -d venv /Users/skyefortier/xps-app/venv 2>/dev/null" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 exited 1 in 0ms:
6688:function _showFitSpinner() {
6697:  _showFitSpinner._timer = setTimeout(() => {
6701:function _hideFitSpinner() {
6705:  clearTimeout(_showFitSpinner._timer);
6736:let _autoFitConfirmResolver = null;
6737:function _showAutoFitConfirmModal(peakCount) {
6739:    _autoFitConfirmResolver = resolve;
6745:      const r = _autoFitConfirmResolver; _autoFitConfirmResolver = null;
6753:  const r = _autoFitConfirmResolver; _autoFitConfirmResolver = null;
7503:function _hideFitSpinnerFor(op) {
7506:  _hideFitSpinner();
7631:    const proceed = await _showAutoFitConfirmModal(state.peaks.length);
7688:  _showFitSpinner();
7759:      _hideFitSpinnerFor(afOp);
7765:      _hideFitSpinnerFor(afOp);
7773:      _hideFitSpinnerFor(afOp);
7779:      _hideFitSpinnerFor(afOp);
7789:      _hideFitSpinnerFor(afOp);
7794:    _hideFitSpinnerFor(afOp);
7801:    _hideFitSpinnerFor(afOp);
8173:  _showFitSpinner();
8254:      _hideFitSpinnerFor(fitOp);
8260:      _hideFitSpinnerFor(fitOp);
8283:      _hideFitSpinnerFor(fitOp);
8293:      _hideFitSpinnerFor(fitOp);
8324:    _hideFitSpinnerFor(fitOp);
8331:    _hideFitSpinnerFor(fitOp);
8347:      _hideFitSpinnerFor(fitOp);
8520:    _hideFitSpinner();
8881:  _hideFitSpinner();
15608:async function openFindPeaksModal() {
16110:async function runFindPeaks() {
16357:// _showAutoFitConfirmModal/_autoFitConfirmCancel.
16377:async function applyFindPeaks() {
    const scale = supportedPct > 0 ? 100 / supportedPct : 1;
    return `<tr style="border-top:1px solid var(--border)">
      <td style="padding:2px 4px">${label}</td><td style="text-align:right;padding:2px 4px;font-family:var(--mono)">${chi.toFixed(2)}</td>
      <td style="text-align:right;padding:2px 4px">${n}</td>
      ${cs.map(c => cell(c, judged, scale)).join('')}
      <td style="padding:2px 4px">${big ? _startsShiftHtml({ id: big.id, ev: big.center_shift_from_start }) : '&mdash;'}</td><td style="padding:2px 4px;white-space:nowrap">${actions}</td></tr>`; };
  html += `<h4 style="font-size:11px;margin:8px 0 4px" title="Solutions other starts reached with a lower reduced chi-square than your fit. A lower value is not a better chemical model: look at where the components went.">Other solutions found</h4>
    <div style="overflow-x:auto"><table style="width:100%;font-size:10px;border-collapse:collapse">
    <thead><tr><th style="text-align:left;padding:2px 4px">solution</th><th style="text-align:right;padding:2px 4px">χ²ᵣ</th><th style="text-align:right;padding:2px 4px" title="how many of the scattered starts ended here">starts here</th>${head}<th style="text-align:left;padding:2px 4px">largest move from your start</th><th></th></tr></thead><tbody>`;
  html += row('<b>Your fit</b>', st.fit.chi2r, st.n_same_as_fit, comps, true, '');
  alts.forEach((a, k) => {
    html += row('Alternative ' + (k + 1), a.chi2r, a.n_starts, a.components, false,
      `<button class="btn btn-sm" onclick="previewAlternative(${k})" title="Overlay this solution on the chart; click again to clear">Preview</button>
       <button class="btn btn-sm" onclick="useAlternative(${k})" title="Run the fit again starting from this solution. Your model changes only if that fit succeeds; you can undo it.">Use this solution</button>`);
  });
  return html + '</tbody></table></div></div>';
}

// The alternative's parameters on a COPY of the current peaks (null when the
// evidence no longer describes the current model).
function _altPeaks(alt) {
  if (!_startsIfCurrent(state.fitResult, _startsLiveKey())) return null;
  const peaks = JSON.parse(JSON.stringify(state.peaks));
  if (peaks.length !== alt.components.length) return null;
  for (const c of alt.components) {
    const p = peaks.find(q => String(q.id) === String(c.id));
    if (!p) return null;
    const par = {};
    for (const k in c.params) par[k] = { value: c.params[k] };
    _applyBackendParams(p, par);
  }
  return peaks;
}

function _currentAlternative(k) {
  const st = _startsIfCurrent(state.fitResult, _startsLiveKey());
  return (st && st.ran && st.alternatives && st.alternatives[k]) || null;
}

const _STARTS_STALE_MSG = 'The model has changed since this fit. Run the fit again to compare solutions.';

function previewAlternative(k) {
  const alt = _currentAlternative(k);
  const peaks = alt && _altPeaks(alt);
  if (!peaks) { notify(_STARTS_STALE_MSG, 'amber', true); return; }
  const key = 'alt:' + k;
  if (_historyPreview && _historyPreview.snapId === key) { _historyClearPreview(); return; }
  _historyPreview = { snapId: key, altKey: state.fitResult.startsModelKey, peaks, fitResult: { chiReduced: alt.chi2r } };
  _updateLocalModelBanner();
  document.querySelectorAll('.hist-row').forEach(r => r.classList.remove('hist-preview-active'));
  updatePlot();
}

// Adopting an alternative is the student's decision: explicit, undoable, and
// recorded. It is ATOMIC by construction: the alternative is only the START of
// an ordinary server fit (runFit's opts.startPeaks); the live model is written
// by that fit's success path and by nothing else, so a fit that fails, does
// not converge, is discarded because the tab changed, or cannot reach the
// server leaves peaks and result exactly as they were (no local fallback
// here: the local engine would start from the live model, not from the
// alternative). runFit's own pushUndo is the single undo entry. A solution
// that moves a component more than 1 eV from where the student put it is the
// measured trap (a lower chi-square bought by a chemically absurd relocation),
// so that case — and only that case — asks first, naming the component and
// the distance.
async function useAlternative(k) {
  const alt = _currentAlternative(k);
  const peaks = alt && _altPeaks(alt);
  if (!peaks) { notify(_STARTS_STALE_MSG, 'amber', true); return; }
  const shift = alt.largest_centre_shift_from_start;
  const name = _startsPeakName(shift.id);
  if (Math.abs(shift.ev) > _STARTS_SHIFT_RED_EV &&
      !confirm(`This solution moves ${name} by ${_startsEv(shift.ev)} from where you placed it. Apply?`)) return;
  const chosen = { fromChi: state.fitResult.starts.fit.chi2r, toChi: alt.chi2r, shiftName: name, shiftEv: shift.ev };
  if (_historyPreview) _historyClearPreview();
  await runFit({ startPeaks: peaks, chosenAlternative: chosen });
}

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
  let fitOp = null;         // unit 2: this tab's fit operation, claimed before the first await
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
    fitOp = _claimFitOp(fittingTab);   // before the first await: the newest claim for a tab is current
    _fitSpinnerOp = fitOp;             // the spinner shown above is this operation's
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
      op: fitOp,
      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
    });
    if (json && json._abandoned === 'superseded') return;   // a newer fit on this tab owns the spinner and the result
    if (json && json._abandoned === 'tab') {
      _hideFitSpinnerFor(fitOp);
      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
    roiMinDom:    document.getElementById('roi-min')?.value || '',
    roiMaxDom:    document.getElementById('roi-max')?.value || '',
    bgStartDom:   document.getElementById('bg-start')?.value || '',
    bgEndDom:     document.getElementById('bg-end')?.value || '',
  };
}

function _autoFitRestore(snap, owner) {
  // owner is the record OBJECT the auto-fit started on — normally the one
  // the snapshot itself carries (taken before the first await). Anything
  // that is not a record object (an id from an older caller, undefined) is
  // ignored in favour of the snapshot's owner. A closed tab's id comes back
  // on a NEW object after a project reload, so an id lookup would restore a
  // stale snapshot into the reopened tab (Codex 2026-09-09).
  if (!snap) return;
  if (!owner || typeof owner !== 'object') owner = snap.owner;
  if (!_ownerLive(owner)) return;
  // If the fitting tab is no longer active (the user switched tabs while
  // the auto-fit request was in flight), restore into that tab's RECORD.
  // Writing the snapshot into live state/DOM here would clobber the newly
  // active tab with the fitting tab's pre-auto-fit state while leaving
  // the fitting tab's record in the provisional cc frame (Codex round-2
  // MAJOR — a pre-existing defect for peaks/ccShift/DOM, not just the
  // newly-migrating anchors). activateTab already synced the provisional
  // live state into the record at switch-away, so overwriting the record
  // fields with the snapshot undoes exactly that.
  if (_activeTab() !== owner) {
    const t = owner;
    if (t.isStack) return;
    t.peaks = snap.peaks;
    t.fitResult = snap.fitResult;
    t.ccShift = snap.ccShift;
    t.manualAnchors = snap.manualAnchors || [];
    t.modelProvenance = snap.modelProvenance || null;
    t.nextId = snap.nextId;
    t.ui = { ...t.ui,
      ccMethod: snap.ccMethodDom, ccObs: snap.ccObsDom, ccLit: snap.ccLitDom,
      roiMin: snap.roiMinDom, roiMax: snap.roiMaxDom,
      bgStart: snap.bgStartDom, bgEnd: snap.bgEndDom };
    return;
  }
  state.peaks     = snap.peaks;
  state.fitResult = snap.fitResult;
  state.ccShift   = snap.ccShift;
  _setManualAnchors(snap.manualAnchors || []);
  { const _t = _activeTab(); if (_t) _t.modelProvenance = snap.modelProvenance || null; }
  state.nextId    = snap.nextId;
  const set = (id, v) => { const el = document.getElementById(id); if (el) el.value = v; };
  set('cc-method', snap.ccMethodDom);
  set('cc-obs',    snap.ccObsDom);
  set('cc-lit',    snap.ccLitDom);
  // The provisional 'c1s' correction hid the custom-target field; putting the
  // method back without its field left Custom with no visible input (same
  // rule as the tab-restore path, no change event).
  { const rf = document.getElementById('cc-ref-field'), tf = document.getElementById('cc-target-field');
    if (rf) rf.style.display = (snap.ccMethodDom === 'none') ? 'none' : 'block';
    if (tf) tf.style.display = (snap.ccMethodDom === 'custom') ? 'block' : 'none'; }
  set('roi-min',   snap.roiMinDom);
  set('roi-max',   snap.roiMaxDom);
  set('bg-start',  snap.bgStartDom);
  set('bg-end',    snap.bgEndDom);
  const disp = document.getElementById('cc-shift-display');
  if (disp) {
    const sh = -state.ccShift;
    disp.textContent = (sh >= 0 ? '+' : '') + sh.toFixed(3) + ' eV';
  }
  if (typeof renderPeakList === 'function') renderPeakList();
  if (typeof updatePlot === 'function') updatePlot();
}

// Apply a successful auto-fit result. Mutates state and DOM so the tab
// ends in a self-consistent corrected frame with graphite at exactly 284.50.
// Pure decision: given (id, area) pairs and graphite's id, decide whether
// to emit the < 40% area-fraction warning toast. Returns null on no-warning,
// or { fractionPct, warning } on warning. Boundary: '< 0.40' so 0.40 itself
// does NOT warn.
//
// This logic is intentionally state-free so the Python port test in
// /tmp/test_autofit_decide_warning.py can validate it without simulating
// state.peaks or the backend.
function _autoFitDecideAreaWarning(peakAreas, graphiteId) {
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
    'const _runningFitJobs = new Set(); let _fitOpSeq = 0; const _fitOpByOwner = new WeakMap(); let _fitSpinnerOp = null;',
    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_newFitOp'), extractFn('_installFitOp'), extractFn('_claimFitOp'), extractFn('_fitOpCurrent'),
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
/Users/skyefortier/xps-app/venv

exec
/bin/zsh -lc 'node --test tests/js/fit_start_poll.test.js tests/js/fit_acceptance.test.js tests/js/stale_statistics.test.js tests/js/per_tab_state.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 302ms:
# Subtest: A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
ok 1 - A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
  ---
  duration_ms: 8.521689
  type: 'test'
  ...
# Subtest: a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
ok 2 - a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
  ---
  duration_ms: 4.815023
  type: 'test'
  ...
# Subtest: a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
ok 3 - a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
  ---
  duration_ms: 3.271113
  type: 'test'
  ...
# Subtest: a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
ok 4 - a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
  ---
  duration_ms: 12.602797
  type: 'test'
  ...
# Subtest: a converged backend result is applied (sanity)
ok 5 - a converged backend result is applied (sanity)
  ---
  duration_ms: 3.789555
  type: 'test'
  ...
# Subtest: the engine/objective labels of a fit result survive spectrum and project save/load
ok 6 - the engine/objective labels of a fit result survive spectrum and project save/load
  ---
  duration_ms: 0.942903
  type: 'test'
  ...
# Subtest: an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
ok 7 - an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
  ---
  duration_ms: 3.295626
  type: 'test'
  ...
# Subtest: an HTTP 502 on the upload is a server failure, not a transport failure
ok 8 - an HTTP 502 on the upload is a server failure, not a transport failure
  ---
  duration_ms: 3.839948
  type: 'test'
  ...
# Subtest: uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
ok 9 - uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
  ---
  duration_ms: 2.211067
  type: 'test'
  ...
# Subtest: every consumer that prints the goodness-of-fit statistic routes through the statistic identity
ok 10 - every consumer that prints the goodness-of-fit statistic routes through the statistic identity
  ---
  duration_ms: 1.024625
  type: 'test'
  ...
# Subtest: uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
ok 11 - uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
  ---
  duration_ms: 0.600028
  type: 'test'
  ...
# Subtest: a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
ok 12 - a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
  ---
  duration_ms: 1.559696
  type: 'test'
  ...
# Subtest: starting-point helpers: keyed on the persisted objective, weighted results untouched
ok 13 - starting-point helpers: keyed on the persisted objective, weighted results untouched
  ---
  duration_ms: 3.278444
  type: 'test'
  ...
# Subtest: Quantify shows the starting-point banner for a local result and not for a weighted one
ok 14 - Quantify shows the starting-point banner for a local result and not for a weighted one
  ---
  duration_ms: 4.957779
  type: 'test'
  ...
# Subtest: every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
ok 15 - every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
  ---
  duration_ms: 1.990568
  type: 'test'
  ...
# Subtest: project save derives the designation from the objective for an older local result lacking the new fields
ok 16 - project save derives the designation from the objective for an older local result lacking the new fields
  ---
  duration_ms: 8.60122
  type: 'test'
  ...
# Subtest: stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
ok 17 - stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
  ---
  duration_ms: 0.884714
  type: 'test'
  ...
# Subtest: _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
ok 18 - _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
  ---
  duration_ms: 3.521064
  type: 'test'
  ...
# Subtest: history preview glow is keyed on the dataset flag, not the label text
ok 19 - history preview glow is keyed on the dataset flag, not the label text
  ---
  duration_ms: 0.648031
  type: 'test'
  ...
# Subtest: spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
ok 20 - spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
  ---
  duration_ms: 0.486977
  type: 'test'
  ...
# Subtest: _applyStatDisplay clears header, tooltip, caption and value together on local → none
ok 21 - _applyStatDisplay clears header, tooltip, caption and value together on local → none
  ---
  duration_ms: 3.01984
  type: 'test'
  ...
# Subtest: _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
ok 22 - _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
  ---
  duration_ms: 1.552743
  type: 'test'
  ...
# Subtest: fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
ok 23 - fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
  ---
  duration_ms: 1.408869
  type: 'test'
  ...
# Subtest: undo/redo snapshots carry and restore model provenance
ok 24 - undo/redo snapshots carry and restore model provenance
  ---
  duration_ms: 3.807024
  type: 'test'
  ...
# Subtest: round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
ok 25 - round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
  ---
  duration_ms: 1.15143
  type: 'test'
  ...
# Subtest: _provenanceOf derives a designation from a live local result, and undo snapshots use it
ok 26 - _provenanceOf derives a designation from a live local result, and undo snapshots use it
  ---
  duration_ms: 2.704316
  type: 'test'
  ...
# Subtest: batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
ok 27 - batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
  ---
  duration_ms: 0.371937
  type: 'test'
  ...
# Subtest: the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
ok 28 - the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
  ---
  duration_ms: 2.721138
  type: 'test'
  ...
# Subtest: round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
ok 29 - round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
  ---
  duration_ms: 0.664172
  type: 'test'
  ...
# Subtest: the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
ok 30 - the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
  ---
  duration_ms: 3.671385
  type: 'test'
  ...
# Subtest: the sidebar banner is sticky at the top of the scrolling panel body
ok 31 - the sidebar banner is sticky at the top of the scrolling panel body
  ---
  duration_ms: 0.438192
  type: 'test'
  ...
# Subtest: the sidebar banner shows on a stack tab whose visible entries draw a local source fit
ok 32 - the sidebar banner shows on a stack tab whose visible entries draw a local source fit
  ---
  duration_ms: 2.687253
  type: 'test'
  ...
# Subtest: every stack chart repaint path refreshes the sidebar designation before any early return
ok 33 - every stack chart repaint path refreshes the sidebar designation before any early return
  ---
  duration_ms: 0.436773
  type: 'test'
  ...
# Subtest: closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
ok 34 - closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
  ---
  duration_ms: 0.235054
  type: 'test'
  ...
# Subtest: W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
ok 35 - W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
  ---
  duration_ms: 2.826842
  type: 'test'
  ...
# Subtest: TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
ok 36 - TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
  ---
  duration_ms: 4.423229
  type: 'test'
  ...
# Subtest: adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
ok 37 - adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
  ---
  duration_ms: 3.121885
  type: 'test'
  ...
# Subtest: adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
ok 38 - adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
  ---
  duration_ms: 3.016274
  type: 'test'
  ...
# Subtest: adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
ok 39 - adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
  ---
  duration_ms: 2.80068
  type: 'test'
  ...
# Subtest: adoption: success records the choice, the starts evidence and the key of the model it describes
ok 40 - adoption: success records the choice, the starts evidence and the key of the model it describes
  ---
  duration_ms: 2.788848
  type: 'test'
  ...
# Subtest: an ordinary Run Fit on one unlinked component does not ask for the starts check
ok 41 - an ordinary Run Fit on one unlinked component does not ask for the starts check
  ---
  duration_ms: 3.157061
  type: 'test'
  ...
# Subtest: a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
ok 42 - a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
  ---
  duration_ms: 2.967309
  type: 'test'
  ...
# Subtest: a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
ok 43 - a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
  ---
  duration_ms: 6.321001
  type: 'test'
  ...
# Subtest: a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
ok 44 - a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
  ---
  duration_ms: 4.023321
  type: 'test'
  ...
# Subtest: a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
ok 45 - a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
  ---
  duration_ms: 7.416286
  type: 'test'
  ...
# Subtest: the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)
ok 46 - the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)
  ---
  duration_ms: 1.134969
  type: 'test'
  ...
# Subtest: the token scan is linear and keeps a truncated string a string (Codex round 2)
ok 47 - the token scan is linear and keeps a truncated string a string (Codex round 2)
  ---
  duration_ms: 3.326166
  type: 'test'
  ...
# Subtest: a minus sign counts only after a boundary: "x-Infinity" is malformed, "-Infinity" a token (Codex round 3)
ok 48 - a minus sign counts only after a boundary: "x-Infinity" is malformed, "-Infinity" a token (Codex round 3)
  ---
  duration_ms: 0.720095
  type: 'test'
  ...
# Subtest: start -> running polls -> done: the result is the /api/fit body; no job is left registered
ok 49 - start -> running polls -> done: the result is the /api/fit body; no job is left registered
  ---
  duration_ms: 10.436453
  type: 'test'
  ...
# Subtest: a bad request: the synchronous route's message and status, immediately; no poll
ok 50 - a bad request: the synchronous route's message and status, immediately; no poll
  ---
  duration_ms: 4.753478
  type: 'test'
  ...
# Subtest: a START that cannot reach the server is a transport failure (the caller may fall back to the local engine)
ok 51 - a START that cannot reach the server is a transport failure (the caller may fall back to the local engine)
  ---
  duration_ms: 4.274114
  type: 'test'
  ...
# Subtest: an error record is a failed fit with the synchronous message and status
ok 52 - an error record is a failed fit with the synchronous message and status
  ---
  duration_ms: 4.358791
  type: 'test'
  ...
# Subtest: a done record carrying NaN is F2's failed fit (unreadable reply), not a transport failure
ok 53 - a done record carrying NaN is F2's failed fit (unreadable reply), not a transport failure
  ---
  duration_ms: 3.930579
  type: 'test'
  ...
# Subtest: one lost poll is retried; five in a row are a transport failure and cancel the job
ok 54 - one lost poll is retried; five in a row are a transport failure and cancel the job
  ---
  duration_ms: 8.081351
  type: 'test'
  ...
# Subtest: a stopped heartbeat (restarted worker) is a failed fit, never an endless spinner
ok 55 - a stopped heartbeat (restarted worker) is a failed fit, never an endless spinner
  ---
  duration_ms: 3.154304
  type: 'test'
  ...
# Subtest: a job cancelled on the server (abandoned) is reported, not waited for
ok 56 - a job cancelled on the server (abandoned) is reported, not waited for
  ---
  duration_ms: 4.014286
  type: 'test'
  ...
# Subtest: ownership inside the loop: a switched tab or an edited model cancels the job and returns the reason
ok 57 - ownership inside the loop: a switched tab or an edited model cancels the job and returns the reason
  ---
  duration_ms: 6.88938
  type: 'test'
  ...
# Subtest: the Auto-Fit abort (2 minutes) cancels the job and surfaces as an AbortError
ok 58 - the Auto-Fit abort (2 minutes) cancels the job and surfaces as an AbortError
  ---
  duration_ms: 4.23719
  type: 'test'
  ...
# Subtest: Run Fit and Auto-Fit both go through _serverFitJob; nothing on the page posts to the synchronous /api/fit any more
ok 59 - Run Fit and Auto-Fit both go through _serverFitJob; nothing on the page posts to the synchronous /api/fit any more
  ---
  duration_ms: 2.533495
  type: 'test'
  ...
# Subtest: the NEWEST claim is current whatever order the start responses arrive in (Codex round 2)
ok 60 - the NEWEST claim is current whatever order the start responses arrive in (Codex round 2)
  ---
  duration_ms: 13.013815
  type: 'test'
  ...
# Subtest: a poll in flight when a newer claim arrives: its reply is never applied, never an error (Codex round 2)
ok 61 - a poll in flight when a newer claim arrives: its reply is never applied, never an error (Codex round 2)
  ---
  duration_ms: 11.386201
  type: 'test'
  ...
# Subtest: an Auto-Fit timeout after a newer claim is superseded, not a timeout (Codex round 2)
ok 62 - an Auto-Fit timeout after a newer claim is superseded, not a timeout (Codex round 2)
  ---
  duration_ms: 3.958488
  type: 'test'
  ...
# Subtest: both callers claim their operation before the first await and do nothing at all when superseded
ok 63 - both callers claim their operation before the first await and do nothing at all when superseded
  ---
  duration_ms: 1.122546
  type: 'test'
  ...
# Subtest: the Auto-Fit modal race: a Run Fit pressed while the confirmation is open WINS; the confirmed Auto-Fit changes nothing (Codex round 3)
ok 64 - the Auto-Fit modal race: a Run Fit pressed while the confirmation is open WINS; the confirmed Auto-Fit changes nothing (Codex round 3)
  ---
  duration_ms: 6.668325
  type: 'test'
  ...
# Subtest: the spinner belongs to the operation that showed it: an ended fit never hides another fit's spinner (Codex round 3)
ok 65 - the spinner belongs to the operation that showed it: an ended fit never hides another fit's spinner (Codex round 3)
  ---
  duration_ms: 1.489359
  type: 'test'
  ...
# Subtest: every module-level mutable is allowlisted with a valid non-C class
ok 66 - every module-level mutable is allowlisted with a valid non-C class
  ---
  duration_ms: 180.822366
  type: 'test'
  ...
# Subtest: inherited property names and anonymous-class names cannot slip through the allowlist
ok 67 - inherited property names and anonymous-class names cannot slip through the allowlist
  ---
  duration_ms: 73.542446
  type: 'test'
  ...
# Subtest: the known class-C holders are gone from module scope
ok 68 - the known class-C holders are gone from module scope
  ---
  duration_ms: 5.533777
  type: 'test'
  ...
# Subtest: async operations capture their owning record before the first await
ok 69 - async operations capture their owning record before the first await
  ---
  duration_ms: 1.955881
  type: 'test'
  ...
# Subtest: undo/redo and Find Peaks apply read the ACTIVE tab record only
ok 70 - undo/redo and Find Peaks apply read the ACTIVE tab record only
  ---
  duration_ms: 0.546729
  type: 'test'
  ...
# Subtest: one accessor classifies a result against a key: none / unverified / current / stale
ok 71 - one accessor classifies a result against a key: none / unverified / current / stale
  ---
  duration_ms: 12.584439
  type: 'test'
  ...
# Subtest: the key is the step (b) key: F1 adds no second binding mechanism and no new key field
ok 72 - the key is the step (b) key: F1 adds no second binding mechanism and no new key field
  ---
  duration_ms: 4.844404
  type: 'test'
  ...
# Subtest: Results panel, current: statistic, RMSE, R and sigma are shown
ok 73 - Results panel, current: statistic, RMSE, R and sigma are shown
  ---
  duration_ms: 8.90104
  type: 'test'
  ...
# Subtest: Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
ok 74 - Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
  ---
  duration_ms: 8.738625
  type: 'test'
  ...
# Subtest: Results panel, unverified (older save, no key): values shown with a plain note
ok 75 - Results panel, unverified (older save, no key): values shown with a plain note
  ---
  duration_ms: 8.621169
  type: 'test'
  ...
# Subtest: status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
ok 76 - status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
  ---
  duration_ms: 10.443877
  type: 'test'
  ...
# Subtest: the stored fitted curve is never drawn, saved or stacked as the fit once stale
ok 77 - the stored fitted curve is never drawn, saved or stacked as the fit once stale
  ---
  duration_ms: 3.18941
  type: 'test'
  ...
# Subtest: saves keep the key and say plainly when the statistics are stale or unverified
ok 78 - saves keep the key and say plainly when the statistics are stale or unverified
  ---
  duration_ms: 2.881843
  type: 'test'
  ...
# Subtest: CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
ok 79 - CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
  ---
  duration_ms: 14.54979
  type: 'test'
  ...
# Subtest: XLSX: stale writes a WARNING row instead of the statistic, and no sigma
ok 80 - XLSX: stale writes a WARNING row instead of the statistic, and no sigma
  ---
  duration_ms: 5.098938
  type: 'test'
  ...
# Subtest: TSV: stale says the Model / Residual columns are the current, unfitted model
ok 81 - TSV: stale says the Model / Residual columns are the current, unfitted model
  ---
  duration_ms: 8.225752
  type: 'test'
  ...
# Subtest: the refresh re-renders Results only when its rendered state differs
ok 82 - the refresh re-renders Results only when its rendered state differs
  ---
  duration_ms: 3.590767
  type: 'test'
  ...
# Subtest: an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
ok 83 - an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
  ---
  duration_ms: 2.943582
  type: 'test'
  ...
# Subtest: Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
ok 84 - Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
  ---
  duration_ms: 4.098748
  type: 'test'
  ...
# Subtest: Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
ok 85 - Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
  ---
  duration_ms: 9.08926
  type: 'test'
  ...
# Subtest: closing the last tab clears the Results panel, header and status statistics too
ok 86 - closing the last tab clears the Results panel, header and status statistics too
  ---
  duration_ms: 0.167516
  type: 'test'
  ...
# Subtest: reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
ok 87 - reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
  ---
  duration_ms: 1.290194
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back
ok 88 - F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back
  ---
  duration_ms: 4.815472
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a Cloudflare 524 (plain-text body) is a failed request with its status, never "could not be read"
ok 89 - F2: Auto-Fit on a Cloudflare 524 (plain-text body) is a failed request with its status, never "could not be read"
  ---
  duration_ms: 4.350317
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a 500 with a JSON error is a failed request with its status, never "could not be read"
ok 90 - F2: Auto-Fit on a 500 with a JSON error is a failed request with its status, never "could not be read"
  ---
  duration_ms: 2.820544
  type: 'test'
  ...
1..90
# tests 90
# suites 0
# pass 90
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 369.459327

exec
/bin/zsh -lc "sed -n '60,150p' tests/js/fit_acceptance.test.js && sed -n '330,415p' tests/js/stale_statistics.test.js && sed -n '1,150p' tests/conftest.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
exec
/bin/zsh -lc "sed -n '6675,6765p' templates/index.html && sed -n '8480,8540p' templates/index.html && sed -n '8835,8895p' templates/index.html && rg -n 'batchFit|fit-spinner|_bgSubFitInFlight' templates/index.html && sed -n '1,270p' tests/test_fit_start_poll.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
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
  assert.ok(!k._sameFitKey(a, k._startsModelKey(peaks, { ...ui, roiMin: '280.5' }, 0, [])), 'a real ROI change');
  assert.ok(!k._sameFitKey(a, k._startsModelKey(peaks, { ...ui, bgType: 'linear' }, 0, [])), 'a background change');
  assert.ok(!k._sameFitKey(a, k._startsModelKey(peaks, { ...ui, roiMin: '' }, 0, [])), 'an emptied field is not "0"');
  assert.strictEqual(k._statsState({ startsModelKey: a }, k._startsModelKey(peaks, { ...ui, roiMin: '280.0' }, 0, [])), 'current');
  // Codex round 2: each field is read as ITS READERS read it — the counts through parseInt
  for (const [field, fitted, typed, same] of [
    ['endpointAvg', '30', '3e1', false],     // Number('3e1') = 30, parseInt('3e1') = 3: a different background
    ['endpointAvg', '10', '1e1', false],
    ['shirleyIter', '5', '5.0', true],       // parseInt: 5 either way
    ['shirleyIter', '5', '5.9', true],       // parseInt reads 5 — the same fit
    ['endpointAvg', '3', '03', true],
    ['roiMin', '280', '2.8e2', true],        // parseFloat reads 280 either way
    ['roiMin', '280', '280abc', true],       // parseFloat reads 280 (what getROIData selects)
    ['bgStart', '295', '295.5', false],
  ]) {
    const fk = k._startsModelKey(peaks, { ...ui, [field]: fitted }, 0, []);
    const lk = k._startsModelKey(peaks, { ...ui, [field]: typed }, 0, []);
    const pf = /Iter|Avg/.test(field) ? parseInt : parseFloat;
    assert.strictEqual(pf(fitted) === pf(typed), same, 'fixture: the reader agrees with the expectation');
    assert.strictEqual(k._sameFitKey(fk, lk), same, `${field} ${fitted} vs ${typed}`);
  }
  assert.ok(!k._sameFitKey(null, null) && !k._sameFitKey(a, null), 'no key never matches');
  assert.ok(!k._sameFitKey('not json', 'not json ') && k._sameFitKey('not json', 'not json'));
});

test('Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone', () => {
  const src = [...STATE_CONSTS.map(constLine), ...['_fitKeyCanon', '_sameFitKey', ...STATE_FNS].map(extractFn), extractFn('_refreshStatsState')].join('\n');
  const doc = makeDoc();
  const env = { renders: 0 };
  const state = { fitResult: null };
  const refresh = new Function('document', 'state', 'env', `
    const _startsLiveKey = () => 'K', _startsRecordKey = t => t.key;
    const renderResults = () => { env.renders++; document.getElementById('results-area').setAttribute('data-stats-state', _statsLiveState()); };
    const _applyStatDisplay = () => {}, _updateRFactorUI = () => {};
    ${src}
    return _refreshStatsState;`)(doc, state, env);
  refresh();
  assert.strictEqual(env.renders, 0, 'fresh page: nothing rendered yet, nothing to clear');
  doc.els['results-area'].setAttribute('data-stats-state', 'current');   // a fit was shown
  refresh();
  assert.strictEqual(env.renders, 1, 'the shown result was cleared: back to the empty state');
  refresh();
  assert.strictEqual(env.renders, 1);
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
"""Make the repo root importable regardless of how pytest is invoked."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

 succeeded in 0ms:
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
function _applyStatDisplay(fr) {
  const fq = document.getElementById('fit-quality');
  const sb = document.getElementById('sb-chi');
  const st = (fr && fr === state.fitResult) ? _statsLiveState() : 'current';
  if (fr && Number.isFinite(fr.chiReduced) && st === 'stale') {
    // F1: the statistic belongs to the previous model: say so, show no number
    if (fq) { fq.textContent = _fitStatLabel(fr) + ' \u2014 (model changed)'; fq.setAttribute('data-xps-tip', _STATS_STALE_NOTE); }
    if (sb) sb.textContent = '\u2014';
  } else if (fr && Number.isFinite(fr.chiReduced)) {
    const tip = (_isLocalFit(fr) ? _LOCALFIT_TOOLTIP : _CHISQ_TOOLTIP) + (st === 'unverified' ? '\n\n' + _STATS_UNVERIFIED_NOTE : '');
    if (fq) { fq.textContent = _fitStatusText(fr); fq.setAttribute('data-xps-tip', tip); }
    if (sb) sb.textContent = fr.chiReduced.toFixed(3);
  } else {
    if (fq) { fq.innerHTML = '&#967;&#178; &mdash;'; fq.removeAttribute('data-xps-tip'); }
    if (sb) sb.textContent = '\u2014';
  }
  _applyStatCaption(fr);
  _updateLocalModelBanner();
}

// Local Levenberg-Marquardt: the fallback engine, and the ONLY engine Batch
// Fit uses.
//
// ACCEPTANCE RULE (unit A0, 2026-09-15): this function never writes to
// state.peaks or state.fitResult unless the optimiser converged. It works on
// a copy of the peak list and commits the copy on success; on
// non-convergence the previous peaks and the previous fit result are left
// exactly as they were and the caller receives { success: false }.
//
// History: from the initial commit (f20d71b) until this unit the update
// step solved JtJ.dp = +Jt.r with r = data - model, i.e. an ASCENT step, so
// every step was rejected, lambda inflated past 1e8 and the loop returned
// the STARTING model announced as "Fit complete (local LM)". The
// convergence test also compared chi-square with itself after acceptance.
// Both are pinned by tests/js/local_lm_descent.test.js, which replays the
// committed lab project; the proof is in
// docs/superpowers/plans/2026-09-15-a01-local-lm-proof.md.
function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
  const maxIter = Number.isFinite(options.maxIterations) ? options.maxIterations : 3000;
  const fail = (message, iterations) => {
    _hideFitSpinner();
    document.getElementById('sb-msg').textContent = 'Local fit failed';
    notify('Local fit did not converge: ' + message + ' Previous peaks and result kept.', 'red', true);
    return { success: false, engine: 'local', message, iterations: iterations || 0 };
  };
  if (!Array.isArray(be) || be.length < 2 ||
      !Array.isArray(bgSubtracted) || bgSubtracted.length !== be.length ||
      !Array.isArray(bgIntensity) || bgIntensity.length !== be.length ||
      !be.every(Number.isFinite) || !bgSubtracted.every(Number.isFinite) || !bgIntensity.every(Number.isFinite)) {
    return fail('invalid or non-finite data in the fitting region.');
  }
  // POISSON WEIGHTS (unit W1): the same weighting fitting.run_fit applies on
  // the server — sigma = sqrt(raw counts), floored at 1, where the raw
  // counts are the background-subtracted signal plus the background.
  const _w = be.map((_, i) => 1 / Math.sqrt(Math.max(bgSubtracted[i] + bgIntensity[i], 1)));
  // Work on copies: live peaks are touched only on success.
  const work = state.peaks.map(p => ({ ...p }));
  if (!work.length) return fail('no peaks to fit.');
  const workPeak = id => work.find(q => q.id === id);

  const freeParams = [];
    // spectrum's fit) and must not travel with this result.
    delete live._backendParams;
  }

  // Degrees of freedom count the parameters this engine varies (caM is held,
  // not one of them; parameters temporarily blocked at a wall still count).
  const nVaried = params.filter((_, j) => !isDiscrete(j)).length;
  const dof = Math.max(1, be.length - nVaried);
  const chiReduced = chi / dof;                       // weighted reduced chi-square, as lmfit's redchi
  const _raw = rawResiduals(params);
  const rmse = Math.sqrt(_raw.reduce((a, v) => a + v * v, 0) / be.length);   // unweighted RMS, as the server path reports
  // "Not supported by the data": the same removal statistic the server
  // computes, from this engine's own residuals and weights (a component driven
  // to the zero floor is an outcome here too, not something to hide).
  {
    const model = evalAllPeaks(be, work);
    const verdicts = {};
    for (const wp of work) {
      if (wp.linked) continue;
      const comp = evalPeakArray(be, wp);
      const nFreeComp = paramMap.filter(d => d.id === wp.id && !isDiscrete(paramMap.indexOf(d))).length;
      verdicts[String(wp.id)] = _componentSupportCore(bgSubtracted, model, comp, _w, nFreeComp, nVaried);
    }
    _applySupportVerdicts(state.peaks, id => verdicts[String(id)] || null, _startsLiveKey());
  }

  // KNOWN LIMITATION: this engine produces no parameter uncertainties; the
  // results panel shows blank sigma for every parameter after a local fit.
  const roiRange = { min: _arrMin(be).toFixed(1), max: _arrMax(be).toFixed(1) };
  { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }   // a new result supersedes imported provenance
  state.fitResult = { chi, chiReduced, rmse, be, bgSubtracted, bgIntensity, roiRange,
                      engine: 'local', status: 'converged',
                      objective: 'poisson_weighted_chi_square', weighting: '1/sqrt(max(counts,1))', iterations,
                      reportable: false, caveat: _LOCAL_FIT_CAVEAT,
                      startsModelKey: _startsLiveKey() };   // F1: the statistics describe the committed model
  state.fitResult.rFactor = _computeRFactor(state.fitResult);

  _applyStatDisplay(state.fitResult);
  document.getElementById('sb-msg').textContent = 'Fit complete (local)';
  _updateRFactorUI(state.fitResult.rFactor);
  _updateROIDisplay(roiRange);

  renderPeakList();
  updatePlot();
  renderResults();

  _hideFitSpinner();
  notify('Local fit converged in ' + iterations + ' iteration' + (iterations === 1 ? '' : 's') +
         '. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3) + ' (Poisson-weighted; no uncertainties). Starting point only: run Fit before reporting.', 'amber');
  _autoSnapshot();
  return { success: true, engine: 'local', iterations, acceptedSteps, chiReduced, certifyRestarts };
}

function solveLinear(A, b, n) {
  const M = A.map((row, i) => [...row, b[i]]);
  for (let col = 0; col < n; col++) {
    let maxRow = col;
    for (let row = col + 1; row < n; row++) {
      if (Math.abs(M[row][col]) > Math.abs(M[maxRow][col])) maxRow = row;
    }
    [M[col], M[maxRow]] = [M[maxRow], M[col]];
1249:  .fit-spinner-overlay {
1260:  .fit-spinner {
1272:     modal-covering overlay like .fit-spinner-overlay: the results area
1377:  .fit-spinner-label {
1384:  .fit-spinner-label .ellipsis::after {
2159:        <div id="fit-spinner-overlay" class="fit-spinner-overlay" style="display:none">
2160:          <div class="fit-spinner"></div>
2161:          <div class="fit-spinner-label" id="fit-spinner-label">Fitting<span class="ellipsis"></span></div>
6577:let _bgSubFitInFlight = false;
6603:  const fitting = _bgSubFitInFlight;
6689:  const overlay = document.getElementById('fit-spinner-overlay');
6690:  const label = document.getElementById('fit-spinner-label');
6694:  _bgSubFitInFlight = true;
6702:  const overlay = document.getElementById('fit-spinner-overlay');
6706:  _bgSubFitInFlight = false;
7690:  const spinLabel = document.getElementById('fit-spinner-label');
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


@pytest.mark.parametrize("failing", ["fit-hb-", "fit-"])
def test_a_thread_that_fails_to_start_returns_its_admission_exactly_once(client, monkeypatch, failing):
    """Codex round 2: admission has exactly one owner — the route until the
    worker thread has started, the worker after."""
    real_start = app_module.threading.Thread.start

    def start(self):
        name = self.name or ""
        if name.startswith(failing) and not (failing == "fit-" and name.startswith("fit-hb-")):
            raise RuntimeError("cannot start thread")
        return real_start(self)

    import threading as _th
    # three run slots, so the faulted (fast) worker can RUN and finish while the
    # held jobs are still outstanding — the double release is then visible
    monkeypatch.setattr(app_module, "_FIT_JOB_RUN_SLOTS", _th.BoundedSemaphore(3))
    sid = _upload(client)
    # a job held OUTSTANDING (the counter is clamped at 0, so a double release
    # only shows while another admission is live)
    slow_sid = _upload(client, n=300, comps=SLOW)
    slow = [client.post("/api/fit/start", json=_body(slow_sid, SLOW, method="basinhopping", n_perturb=0)).get_json()["job_id"]
            for _ in range(2)]                     # TWO held: one running, one queued
    before = app_module._FIT_JOB_ADMITTED[0]
    assert before >= 2
    monkeypatch.setattr(app_module.threading.Thread, "start", start)
    with pytest.raises(RuntimeError):
        client.post("/api/fit/start", json=_body(sid, COMPS))
    monkeypatch.setattr(app_module.threading.Thread, "start", real_start)
    time.sleep(3.0)                                # long enough for a started (fast) worker to finish and release
    assert app_module._FIT_JOB_ADMITTED[0] == before, "released exactly once, by the route"
    for j in slow:
        client.post(f"/api/fit/cancel/{j}")
    for j in slow:
        _poll(client, j, limit=60)
    time.sleep(0.3)
    assert app_module._FIT_JOB_ADMITTED[0] == before - 2, "and the held jobs released their own, once each"

exec
/bin/zsh -lc 'git diff fix-acceptance-holes..HEAD -- app.py fitting.py scripts/public_fit_poll_check.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-vW11nZwf' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-IvML7NgK' (errno=Operation not permitted)
diff --git a/app.py b/app.py
index f689d5a..79c5eb2 100644
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
@@ -443,6 +550,180 @@ def _sweep_expired_jobs(upload_folder: str) -> None:
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

codex
All 90 focused JavaScript tests pass. The spinner tests cover ownership after a new fit takes the spinner, but they don’t exercise Auto-Fit superseding a running fit and then failing its preliminary ROI or peak checks. I’m probing that path and Batch Fit’s calls to the shared spinner cleanup.
exec
/bin/zsh -lc "sed -n '525,780p' app.py && sed -n '1170,1380p' app.py && sed -n '2080,2165p' fitting.py && rg -n 'runFitLocal\\(' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
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

#  (splitting eV, area_ratio = intensity(high‑j) / intensity(low‑j))
#  Convention: the primary peak is the high‑j component (lower BE in BE scale).
SPIN_ORBIT_PRESETS = {
    "Si 2p":  {"splitting": 0.61,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
    "Al 2p":  {"splitting": 0.41,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
    "P 2p":   {"splitting": 0.84,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
    "S 2p":   {"splitting": 1.18,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
    "Cl 2p":  {"splitting": 1.60,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
    "Ti 2p":  {"splitting": 5.54,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
    "Fe 2p":  {"splitting": 13.1,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
    "Co 2p":  {"splitting": 15.0,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
    "Ni 2p":  {"splitting": 17.3,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
    "Cu 2p":  {"splitting": 19.8,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
    "Zn 2p":  {"splitting": 23.1,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
    "Mo 3d":  {"splitting": 3.13,  "area_ratio": 0.667, "description": "3d5/2 → 3d3/2 (3:2)"},
    "Ag 3d":  {"splitting": 6.00,  "area_ratio": 0.667, "description": "3d5/2 → 3d3/2 (3:2)"},
    "Cd 3d":  {"splitting": 6.74,  "area_ratio": 0.667, "description": "3d5/2 → 3d3/2 (3:2)"},
    "Sn 3d":  {"splitting": 8.43,  "area_ratio": 0.667, "description": "3d5/2 → 3d3/2 (3:2)"},
    "W 4f":   {"splitting": 2.18,  "area_ratio": 0.75, "description": "4f7/2 → 4f5/2 (4:3)"},
    "Au 4f":  {"splitting": 3.67,  "area_ratio": 0.75, "description": "4f7/2 → 4f5/2 (4:3)"},
    "Pt 4f":  {"splitting": 3.33,  "area_ratio": 0.75, "description": "4f7/2 → 4f5/2 (4:3)"},
    "Pb 4f":  {"splitting": 4.86,  "area_ratio": 0.75, "description": "4f7/2 → 4f5/2 (4:3)"},
}


# ─────────────────────────────────────────────────────────────────────────────
# Route registration
# ─────────────────────────────────────────────────────────────────────────────

def _register_routes(app: Flask) -> None:

    # ── Index ─────────────────────────────────────────────────────────────────

    @app.route("/")
    def index():
        # Serve index.html from the templates folder when the frontend is ready
        from flask import render_template, send_from_directory
        templates = Path(app.template_folder)
        static = Path(app.static_folder) if app.static_folder else Path("static")
        if templates.exists() and (templates / "index.html").exists():
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
        if error is not None:
            return error
        upload_folder = app.config["UPLOAD_FOLDER"]
        if not _fit_job_admit():
            return _err("The server is busy with other fits. Try again in a moment.", 503)
        job_id = str(uuid.uuid4())
        try:
            _sweep_expired_jobs(upload_folder)
            _sweep_fit_job_markers(upload_folder)
            _fit_job_start(job_id, upload_folder, fit_args,
                           lambda args, cancel: _run_fit_outcome(app, args, cancel=cancel))
        except Exception:
            _fit_job_release()          # the job never started: its admission is returned
            raise
        return jsonify({"job_id": job_id}), 202

    @app.get("/api/fit/progress/<job_id>")
    def fit_progress(job_id):
        try:
            uuid.UUID(job_id)
        except ValueError:
            return _err("Invalid job_id format (expected UUID)", 400)
        data = _fit_job_read(job_id, app.config["UPLOAD_FOLDER"])
        if data is None:
            return _err(f"Job '{job_id}' not found", 404)
        return app.response_class(json.dumps(data, allow_nan=True), mimetype="application/json")

    @app.post("/api/fit/cancel/<job_id>")
    def fit_cancel(job_id):
        try:
            uuid.UUID(job_id)
        except ValueError:
            return _err("Invalid job_id format (expected UUID)", 400)
        _fit_job_cancel(job_id, app.config["UPLOAD_FOLDER"])
        return jsonify({"cancelled": True})

    # ── Health check ──────────────────────────────────────────────────────────

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})


# ─────────────────────────────────────────────────────────────────────────────
# Error handlers
# ─────────────────────────────────────────────────────────────────────────────

def _register_error_handlers(app: Flask) -> None:

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"error": "File too large (limit 50 MB)"}), 413

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.exception("Unhandled 500 error")
        return jsonify({"error": "Internal server error"}), 500


# ─────────────────────────────────────────────────────────────────────────────
# Small utilities
# ─────────────────────────────────────────────────────────────────────────────

def _validate_session_id(session_id: str) -> None:
    """Raise 400 if session_id looks unsafe (path traversal guard)."""
    try:
        uuid.UUID(session_id)
    except (ValueError, AttributeError):
        from flask import abort
        abort(400, description="Invalid session_id format (expected UUID)")


def _parse_int(value, lo: int, hi: int, default: int | None = None) -> int | None:
    """Convert a JSON value to a bounded integer index."""
    if value is None:
        return default
    try:
        v = int(value)
        if v < 0:
            v = max(0, hi + v)  # support negative indexing like Python
        return max(lo, min(hi, v))
    except (TypeError, ValueError):
        return default


def _preview(
    energy: np.ndarray,
    counts: np.ndarray,
    max_pts: int = 2000,
) -> dict:
    """Return (possibly downsampled) energy/counts lists for API responses."""
    n = len(energy)
    elif method == "linear":
        bg = linear_background(x, y)
    elif method in ("none", "flat", "", "manual"):
        bg = np.zeros_like(y)
    else:
        raise ValueError(f"Unknown background method '{method}'")

    return {
        "energy": x.tolist(),
        "background": bg.tolist(),
        "net_counts": (y - bg).tolist(),
    }


def run_fit(*args, cancel=None, **kwargs):
    """Fit peaks — see ``_run_fit_impl`` for every argument and the result.

    ``cancel`` (optional, unit 2): a callable polled during the fit; once it
    returns true every remaining minimisation aborts and ``FitCancelled`` is
    raised instead of a result. Without it this is exactly the synchronous fit
    it always was (no ``iter_cb`` reaches any minimiser)."""
    if cancel is None:
        return _run_fit_impl(*args, **kwargs)
    _CANCEL.fn, _CANCEL.hit = cancel, False
    try:
        result = _run_fit_impl(*args, **kwargs)
    except Exception as exc:
        # An aborted minimisation can surface as the solver's own error (an
        # AttributeError from Levenberg-Marquardt, a RuntimeError from
        # Nelder-Mead or DE): once cancellation was observed it is a
        # cancellation, never a failed fit (unit 2, Codex round 1).
        if getattr(_CANCEL, "hit", False):
            raise FitCancelled("the fit was cancelled") from exc
        raise
    finally:
        hit = getattr(_CANCEL, "hit", False)
        _CANCEL.fn, _CANCEL.hit = None, False
    if hit:
        raise FitCancelled("the fit was cancelled")
    return result


run_fit.__wrapped__ = _run_fit_impl

8356:      const local = runFitLocal(be, bgSubtracted, bgIntensity);
8517:function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
12544:    const outcome = runFitLocal(be, bgSub, bgI);

exec
/bin/zsh -lc "sed -n '6765,6825p' templates/index.html && sed -n '12420,12580p' templates/index.html && sed -n '200,265p' tests/test_fit_start_poll.py && rg -n 'cancel|pytest|venv/bin' docs/autofit/codex/fit_start_poll_r3_verdict_runB.md | tail -12 && git diff fix-acceptance-holes..HEAD -- fitting.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
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
  const threshold = 0.30 * gMax;
  const strong = []; // array of {be, intensity}
  for (let i = 1; i < n - 1; i++) {
    if (bgSubInten[i] < threshold) continue;
    if (bgSubInten[i] >= bgSubInten[i - 1] && bgSubInten[i] >= bgSubInten[i + 1]) {
      strong.push({ be: rawBE[i], intensity: bgSubInten[i] });
    }
  }
  if (!strong.length) return null;
  // Highest-BE strong maximum
  let best = strong[0];
  for (const c of strong) if (c.be > best.be) best = c;
  return best.be;
}

// Decide how many low-BE peaks (0, 1, or 2) the auto-fit model should include.
//   rawBE             : array of raw BE values
//   bgSubInten        : background-subtracted intensity (same length)
//   provisionalShift  : state.ccShift to apply mentally — does NOT mutate state.
//                       App convention: corrected = raw − shift.
// Returns:
//   { count: 0|1|2, locations: number[] of corrected-BE local-max centers,
//     ratio: number, graphiteHeight: number }
function assessLowBERegion(rawBE, bgSubInten, provisionalShift) {
  const n = rawBE.length;
  // 1. Graphite height: closest-corrected-to-284.5 sample
  let gIdx = 0;
  let gDist = Infinity;
  for (let i = 0; i < n; i++) {
    const corr = rawBE[i] - provisionalShift;
    const d = Math.abs(corr - 284.50);
    if (d < gDist) { gDist = d; gIdx = i; }
  }
  const graphiteHeight = bgSubInten[gIdx];
  if (!(graphiteHeight > 0)) {
    return { count: 0, locations: [], ratio: 0, graphiteHeight: 0 };
  }

  // 2. Integrate over 278.0 ≤ corrected ≤ 283.5 (trapezoid in corrected BE)
  let integral = 0;
  const corr = rawBE.map(b => b - provisionalShift);
  for (let i = 1; i < n; i++) {
    const c0 = corr[i - 1], c1 = corr[i];
    if (c1 < 278.0 || c0 > 283.5) continue;
    const lo = Math.max(Math.min(c0, c1), 278.0);
    const hi = Math.min(Math.max(c0, c1), 283.5);
    if (hi <= lo) continue;
    const width = hi - lo;
    const yMid = 0.5 * (bgSubInten[i - 1] + bgSubInten[i]);
    integral += width * Math.max(0, yMid);

  document.getElementById('propagate-run-btn').disabled = false;
  document.getElementById('propagate-modal-overlay').classList.add('open');
}

function _propagateSelectAll(checked) {
  document.querySelectorAll('.prop-chk').forEach(c => c.checked = checked);
}

async function runPropagation() {
  // Loud missing-load guard (mirrors the RefCore guard): batch fit depends on the
  // shipped BatchPropagation module for the source→target settings merge. If its
  // script failed to load, fail clearly and BEFORE mutating any state (button,
  // snapshot suppression, tab records) rather than throwing mid-propagation.
  if (typeof BatchPropagation === 'undefined' || !BatchPropagation.propagateFitUi) {
    notify('Batch-fit module failed to load (static/js/batch_propagation.js). Reload the page and try again.', 'red', true);
    return;
  }
  const sourceId = tabManager.activeId;
  const sourceTab = tabManager._getTab(sourceId);
  if (!sourceTab) return;

  // Sync source state to record before we leave it
  tabManager._syncActiveToRecord();

  const checkedIds = Array.from(document.querySelectorAll('.prop-chk:checked')).map(c => c.dataset.id);
  if (!checkedIds.length) { notify('No tabs selected.', 'amber'); return; }
  // Targets are record OBJECTS resolved now, before the first await: a target
  // closed and reopened from a project during the batch has the same id on a
  // NEW object and must not be written (Codex round 2, both runs).
  const targets = checkedIds.map(id => tabManager._getTab(id)).filter(t => t && !t.isStack);

  const btn = document.getElementById('propagate-run-btn');
  btn.disabled = true;
  const prog = document.getElementById('propagate-progress');
  const summary = document.getElementById('propagate-summary');
  summary.style.display = 'none';
  summary.innerHTML = '';

  // Suppress auto-snapshots during batch propagation
  _snapshotSuppressed = true;

  // Compute source amplitude scale reference (max raw intensity in ROI)
  const srcMaxInten = _arrMax(sourceTab.rawIntensity);
  // SOURCE SNAPSHOT before the first yield: the source record can change
  // between targets (an async rollback, an edit on it), and every target
  // must receive the model the user pressed the button with (Codex round 3).
  const srcPeaks = JSON.parse(JSON.stringify(sourceTab.peaks || []));
  const srcUi = { ...(sourceTab.ui || {}) };
  const srcShift = sourceTab.ccShift;
  // A model copied from a local-derived source stays a starting point on
  // every target until a successful fit supersedes it (unit A0).
  const srcProvenance = _provenanceOf(sourceTab);

  const results = [];

  for (let i = 0; i < targets.length; i++) {
    const tgt = targets[i];
    const tid = tgt.id;
    if (!_ownerLive(tgt)) continue;                 // closed (or replaced by a reload) since the batch started

    prog.textContent = `Fitting spectrum ${i + 1}/${targets.length}: ${tgt.name}…`;

    // Scale factor based on max intensity ratio
    const tgtMaxInten = _arrMax(tgt.rawIntensity);
    const scale = srcMaxInten > 0 ? tgtMaxInten / srcMaxInten : 1;

    // Deep-clone source peaks, scaled
    const clonedPeaks = srcPeaks.map(p => ({
      ...p,
      amplitude: p.linked ? p.amplitude : p.amplitude * scale,
      support: null           // a propagated model has not been fitted: nothing is established (a copied verdict could never match this tab's key anyway)
    }));

    // Copy peak nextId
    const nextId = Math.max(0, ...clonedPeaks.map(p => p.id)) + 1;

    // Propagate background + ROI settings from source (BatchPropagation is the
    // single source of truth for the merge — see static/js/batch_propagation.js).
    // ccShift is copied separately just below.
    const newUi = BatchPropagation.propagateFitUi(srcUi, tgt.ui);

    // Apply to target tab record (without switching UI) — undoable on that record
    _pushUndoFor(tgt, { endpointAvg: tgt.ui && tgt.ui.endpointAvg });
    tgt.peaks = clonedPeaks;
    tgt.nextId = nextId;
    tgt.ui = newUi;
    tgt.ccShift = srcShift;
    tgt.chargeVerified = false;
    // A propagated model has not been fitted yet: the target's previous
    // result belonged to its previous peaks (unit A0 acceptance rule).
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
// FEATURE 2: NIST XPS DATABASE — CHEMICAL STATE LOOKUP
// ══════════════════════════════════════════════════════════════

// Legacy chemical-state constant removed at Stage 9 cutover — NIST-modal
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


@pytest.mark.parametrize("failing", ["fit-hb-", "fit-"])
def test_a_thread_that_fails_to_start_returns_its_admission_exactly_once(client, monkeypatch, failing):
    """Codex round 2: admission has exactly one owner — the route until the
    worker thread has started, the worker after."""
    real_start = app_module.threading.Thread.start

    def start(self):
        name = self.name or ""
        if name.startswith(failing) and not (failing == "fit-" and name.startswith("fit-hb-")):
            raise RuntimeError("cannot start thread")
        return real_start(self)

    import threading as _th
    # three run slots, so the faulted (fast) worker can RUN and finish while the
    # held jobs are still outstanding — the double release is then visible
    monkeypatch.setattr(app_module, "_FIT_JOB_RUN_SLOTS", _th.BoundedSemaphore(3))
    sid = _upload(client)
    # a job held OUTSTANDING (the counter is clamped at 0, so a double release
    # only shows while another admission is live)
    slow_sid = _upload(client, n=300, comps=SLOW)
    slow = [client.post("/api/fit/start", json=_body(slow_sid, SLOW, method="basinhopping", n_perturb=0)).get_json()["job_id"]
            for _ in range(2)]                     # TWO held: one running, one queued
    before = app_module._FIT_JOB_ADMITTED[0]
    assert before >= 2
    monkeypatch.setattr(app_module.threading.Thread, "start", start)
    with pytest.raises(RuntimeError):
        client.post("/api/fit/start", json=_body(sid, COMPS))
    monkeypatch.setattr(app_module.threading.Thread, "start", real_start)
    time.sleep(3.0)                                # long enough for a started (fast) worker to finish and release
    assert app_module._FIT_JOB_ADMITTED[0] == before, "released exactly once, by the route"
    for j in slow:
        client.post(f"/api/fit/cancel/{j}")
    for j in slow:
        _poll(client, j, limit=60)
    time.sleep(0.3)
    assert app_module._FIT_JOB_ADMITTED[0] == before - 2, "and the held jobs released their own, once each"
5034:nelder cancelled and thread-local cleared 0.009
5035:differential_evolution cancelled and thread-local cleared 0.013
5036:basinhopping cancelled and thread-local cleared 0.027
5037:Levenberg-Marquardt sync vs cancel-hook: byte-identical
5038:unobserved cancellation preserves unrelated errors
5086:  7613	      notify('Auto-fit cancelled — the tab changed while the confirmation was open.', 'amber');
5117:   Reproduced with the actual callers: open Auto-Fit A’s confirmation, press Ctrl/Cmd+F to start Run Fit B, then confirm A. A replaces the model, claims ownership and cancels B; A’s result applies. The check after the modal verifies only tab identity. Establish invocation identity before the modal await and reject superseded continuations before model mutation. The test at [fit_start_poll.test.js:239](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/tests/js/fit_start_poll.test.js:239) checks only placement before upload, missing this first await.
5122:Validation: **88 focused JavaScript tests passed**. Comparative probes confirmed the previous response-order, late-poll and timeout failures on the old code and their correction here. Admission fault probes passed for sweeps, initial record/marker writes and either thread startup; 30 concurrent admission attempts accepted exactly six. Cancellation passed across all five solvers; Levenberg–Marquardt results with and without the cancellation hook were byte-identical.
5124:No files changed. Filesystem-backed pytest and full timing acceptance were not rerun.
5130:   Reproduced with the actual callers: open Auto-Fit A’s confirmation, press Ctrl/Cmd+F to start Run Fit B, then confirm A. A replaces the model, claims ownership and cancels B; A’s result applies. The check after the modal verifies only tab identity. Establish invocation identity before the modal await and reject superseded continuations before model mutation. The test at [fit_start_poll.test.js:239](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/tests/js/fit_start_poll.test.js:239) checks only placement before upload, missing this first await.
5135:Validation: **88 focused JavaScript tests passed**. Comparative probes confirmed the previous response-order, late-poll and timeout failures on the old code and their correction here. Admission fault probes passed for sweeps, initial record/marker writes and either thread startup; 30 concurrent admission attempts accepted exactly six. Cancellation passed across all five solvers; Levenberg–Marquardt results with and without the cancellation hook were byte-identical.
5137:No files changed. Filesystem-backed pytest and full timing acceptance were not rerun.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-hUZSZGkP' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-M4uZcTNC' (errno=Operation not permitted)
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
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -m pytest -q -p no:cacheprovider --capture=no tests/test_fit_start_poll.py -k test_a_cancel_observed_mid_fit' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 exited 2 in 1794ms:

==================================== ERRORS ====================================
________________ ERROR collecting tests/test_fit_start_poll.py _________________
tests/test_fit_start_poll.py:20: in <module>
    import app as app_module
app.py:45: in <module>
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
E   FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll']
=========================== short test summary info ============================
ERROR tests/test_fit_start_poll.py - FileNotFoundError: [Errno 2] No usable t...
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 1.49s

exec
/bin/zsh -lc "node -e '
const fs=require('\\''fs'\\''),vm=require('\\''vm'\\''),assert=require('\\''assert'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\''),lines=html.split('\\''\\n'\\'');
function ex(n){let s=lines.findIndex(l=>new RegExp('\\''"'^(async )?function '"'\\''+n+'\\''\\\\('\\'').test(l)),d=0;for(let i=s;i<lines.length;i++){for(const c of lines[i]){if(c==='\\''{'\\'')d++;if(c==='\\''}'\\'')d--;}if(d===0)return lines.slice(s,i+1).join('\\''\\n'\\'');}throw n;}
const names=['\\''runFit'\\'','\\''runAutoFitC1sGraphite'\\'','\\''_newFitOp'\\'','\\''_installFitOp'\\'','\\''_claimFitOp'\\'','\\''_fitOpCurrent'\\'','\\''_hideFitSpinnerFor'\\'','\\''_cancelFitJob'\\'','\\''_fitHttpError'\\'','\\''_readFitReply'\\'','\\''_serverFitJob'\\'','\\''_showFitSpinner'\\'','\\''_hideFitSpinner'\\'','\\''findGraphiteRawBE'\\''];
const init='\\''let _fitOpSeq=0,_fitSpinnerOp=null,_bgSubFitInFlight=false; const _fitOpByOwner=new WeakMap(),_runningFitJobs=new Set(); const FIT_POLL_MS=500,FIT_POLL_TRANSPORT_RETRIES=5,FIT_HEARTBEAT_LOST_SEC=30,_STARTS_N=3;'\\'';
const deferred=()=>{let resolve;return {p:new Promise(r=>resolve=r),resolve:v=>resolve(v)}};
const ok=v=>({ok:true,status:200,text:async()=>JSON.stringify(v)});
function env(){const tab={id:'\\''A'\\''},dom={},notes=[],cancels=[],poll=deferred(),polled=deferred(); let timers=[];
const e=id=>(dom[id]??={value:'\\'''\\'',style:{},classList:{add(){},remove(){}},setAttribute(){}});
const c={console,DOMException,AbortController,document:{getElementById:e,querySelector:()=>e('\\''runButton'\\'')},state:{rawBE:[283,284,285,286,287],rawIntensity:[1,2,3,4,5],peaks:[{id:1}],ccShift:0},tabManager:{activeId:'\\''A'\\'',_getTab:()=>tab},notify:(...a)=>notes.push(a),_opOwner:()=>tab,_ownerActive:()=>true,isC1sTab:()=>true,_showAutoFitConfirmModal:async()=>true,_autoFitSnapshot:()=>({}),_autoFitRestore(){},getROIData:()=>({be:c.state.rawBE,inten:c.state.rawIntensity}),computeBackground:be=>be.map(()=>0),pushUndo(){},_bgWindowIndices:()=>({i0:0,i1:4}),peakToBackendSpec:p=>p,_startsUnlinkedCount:()=>1,_startsLiveKey:()=> '\\''same'\\'',_sameFitKey:(a,b)=>a===b,uploadToBackend:async()=> '\\''sid'\\'',_getManualAnchors:()=>[],_updateBgSubPillEnabled(){},setTimeout:f=>{timers.push(f);return timers.length},clearTimeout(){},fetch:async u=>{if(u.includes('\\''/cancel/'\\'')){cancels.push(u);return ok({});}if(u.endsWith('\\''/start'\\''))return ok({job_id:'\\''J'\\''});polled.resolve();return poll.p;}};
vm.createContext(c);vm.runInContext(init+'\\''\\n'\\''+names.map(ex).join('\\''\\n'\\''),c);return {c,dom,notes,cancels,poll,polled,step:()=>timers.shift()(),tab};}
(async()=>{
 const z=env(); const old=z.c.runFit();await new Promise(r=>setImmediate(r));z.step();z.step();await z.polled.p;
 await z.c.runAutoFitC1sGraphite();z.poll.resolve(ok({status:'\\''cancelled'\\''}));await old;
 const out={cancels:z.cancels,notes:z.notes,spinner:z.dom['\\''fit-spinner-overlay'\\''].style.display,buttonDisabled:z.dom.runButton.disabled,inFlight:vm.runInContext('\\''_bgSubFitInFlight'\\'',z.c),running:vm.runInContext('\\''_runningFitJobs.size'\\'',z.c)};
 console.log('\\''REAL CALLERS, Run Fit superseded by Auto-Fit with monotonically increasing ROI:'\\'',JSON.stringify(out));
 assert.equal(out.running,0);assert.equal(out.spinner,'\\''flex'\\'');assert.equal(out.buttonDisabled,true);assert.equal(out.inFlight,true);assert.match(out.notes[0][0],/No strong peak/);
})();
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
REAL CALLERS, Run Fit superseded by Auto-Fit with monotonically increasing ROI: {"cancels":["/api/fit/cancel/J","/api/fit/cancel/J"],"notes":[["No strong peak found in the C1s ROI; Auto-Fit cannot proceed.","red",true]],"spinner":"flex","buttonDisabled":true,"inFlight":true,"running":0}

exec
/bin/zsh -lc "sed -n '1,105p' app.py && tail -18 app.py && nl -ba templates/index.html | sed -n '7625,7664p' && sed -n '1245,1265p' templates/index.html && rg -n 'auto-fit-c1s|runAutoFitC1sGraphite|runPropagation\\(' templates/index.html | head -25" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
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
    """/api/fit's request validation, shared VERBATIM with /api/fit/start
    (unit 2, 2026-09-27): every 400 / 404 is immediate and word-for-word the
    same on both routes. Returns ``(kwargs_for_run_fit, None)`` or
    ``(None, error_response)``."""
    session_id = body.get("session_id", "")
    _validate_session_id(session_id)

    try:
        energy, counts = _load_session(session_id, app.config["UPLOAD_FOLDER"])
    except KeyError:
        return None, _err(f"Session '{session_id}' not found", 404)

    # Background config
    bg_cfg = body.get("background", {})
    bg_method = bg_cfg.get("method", "shirley")
    bg_start = _parse_int(bg_cfg.get("start_idx"), 0, len(energy))
    bg_end = _parse_int(bg_cfg.get("end_idx"), 0, len(energy), default=len(energy))
    # Clean 400 for malformed endpoint_avg instead of a 500 (audit F9).
    try:
        endpoint_avg = max(1, int(bg_cfg.get("endpoint_avg", 1)))
    except (TypeError, ValueError):
        return None, _err("endpoint_avg must be an integer")
    manual_bg = bg_cfg.get("manual_bg")

    # Peak specs
    peak_specs = body.get("peaks", [])
    if not peak_specs:
        return None, _err("'peaks' list is empty – provide at least one peak")

    # Validate peak ids are unique
    ids = [p.get("id") for p in peak_specs]
    if len(ids) != len(set(ids)):
        return None, _err("Duplicate peak ids found – each peak must have a unique 'id'")

    _ALLOWED_METHODS = {
        "leastsq", "least_squares", "nelder",
        "differential_evolution", "basinhopping",
    }
    fit_method = body.get("fit_method", "leastsq")
    if fit_method not in _ALLOWED_METHODS:
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
  7625	  if (!fittingTab) { notify('No active spectrum tab.', 'amber'); return; }
  7626	  // unit 2: this press's fit operation, numbered NOW (before the modal) and
  7627	  // installed after it, only if no newer operation claimed the tab meanwhile
  7628	  const afOp = _newFitOp(fittingTab);
  7629	  // Confirmation if existing peaks
  7630	  if (state.peaks.length >= 1) {
  7631	    const proceed = await _showAutoFitConfirmModal(state.peaks.length);
  7632	    if (!proceed) return;
  7633	    if (!_ownerActive(fittingTab)) {
  7634	      notify('Auto-fit cancelled — the tab changed while the confirmation was open.', 'amber');
  7635	      return;
  7636	    }
  7637	  }
  7638	
  7639	  // a Run Fit pressed while the confirmation was open is newer: it wins, and
  7640	  // this Auto-Fit does nothing at all (nothing has been changed yet)
  7641	  if (!_installFitOp(afOp)) return;
  7642	  // Snapshot for failure rollback (separate from pushUndo, which only covers peaks).
  7643	  const snap = _autoFitSnapshot();
  7644	
  7645	  // Step 1: find graphite in raw BE
  7646	  const { be: corrBE, inten } = getROIData();
  7647	  if (!corrBE.length) {
  7648	    notify('ROI is empty. Set roi-min and roi-max before auto-fit.', 'red', true);
  7649	    return;
  7650	  }
  7651	  const bgI = computeBackground(corrBE, inten);
  7652	  const bgSub = inten.map((v, i) => v - bgI[i]);
  7653	  // App convention: raw = corrected + state.ccShift
  7654	  const curShift = Number.isFinite(state.ccShift) ? state.ccShift : 0;
  7655	  const rawBE = corrBE.map(b => b + curShift);
  7656	  const graphiteRaw = findGraphiteRawBE(rawBE, bgSub);
  7657	  if (graphiteRaw == null) {
  7658	    notify('No strong peak found in the C1s ROI; Auto-Fit cannot proceed.', 'red', true);
  7659	    return;
  7660	  }
  7661	
  7662	  // Step 2: provisional shift (APP CONVENTION).
  7663	  const provisionalShift = graphiteRaw - 284.50;
  7664	
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
1918:          <button class="save-dropdown-item" id="auto-fit-c1s-menu-item" onclick="runAutoFitC1sGraphite()" title="Available only on C1s spectra (ROI midpoint 270–315 eV)"><span class="dd-icon">&#128293;</span><div>Auto-Fit C1s Graphite<small>One-click fit + charge correction</small></div></button>
6713:  const item = document.getElementById('auto-fit-c1s-menu-item');
6740:    const span = document.getElementById('auto-fit-c1s-confirm-count');
6742:    const proceed = document.getElementById('auto-fit-c1s-confirm-proceed');
6744:      document.getElementById('auto-fit-c1s-confirm-overlay').classList.remove('open');
6748:    document.getElementById('auto-fit-c1s-confirm-overlay').classList.add('open');
6752:  document.getElementById('auto-fit-c1s-confirm-overlay').classList.remove('open');
6942:  // Per-peak bound metadata, consumed in runAutoFitC1sGraphite.
7613:async function runAutoFitC1sGraphite() {
12429:async function runPropagation() {
14965:      <button class="btn btn-accent" id="propagate-run-btn" onclick="runPropagation()">Propagate &amp; Fit</button>
14987:<div id="auto-fit-c1s-confirm-overlay" class="xps-modal-overlay" onclick="if(event.target===this)this.classList.remove('open')">
14993:      This tab has <span id="auto-fit-c1s-confirm-count">0</span> peak(s) and a fit result.
14998:      <button class="btn btn-accent" id="auto-fit-c1s-confirm-proceed">Proceed</button>

exec
/bin/zsh -lc "node -e '
const fs=require('\\''fs'\\''),vm=require('\\''vm'\\''),assert=require('\\''assert'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\''),lines=html.split('\\''\\n'\\'');
function ex(n){let s=lines.findIndex(l=>new RegExp('\\''"'^(async )?function '"'\\''+n+'\\''\\\\('\\'').test(l)),d=0;for(let i=s;i<lines.length;i++){for(const c of lines[i]){if(c==='\\''{'\\'')d++;if(c==='\\''}'\\'')d--;}if(d===0)return lines.slice(s,i+1).join('\\''\\n'\\'');}throw n;}
const names=['\\''runFit'\\'','\\''runAutoFitC1sGraphite'\\'','\\''_newFitOp'\\'','\\''_installFitOp'\\'','\\''_claimFitOp'\\'','\\''_fitOpCurrent'\\'','\\''_hideFitSpinnerFor'\\'','\\''_cancelFitJob'\\'','\\''_fitHttpError'\\'','\\''_readFitReply'\\'','\\''_serverFitJob'\\'','\\''_showFitSpinner'\\'','\\''_hideFitSpinner'\\'','\\''findGraphiteRawBE'\\''];
const init='\\''let _fitOpSeq=0,_fitSpinnerOp=null,_bgSubFitInFlight=false; const _fitOpByOwner=new WeakMap(),_runningFitJobs=new Set(); const FIT_POLL_MS=500,FIT_POLL_TRANSPORT_RETRIES=5,FIT_HEARTBEAT_LOST_SEC=30,_STARTS_N=3;'\\'';
const deferred=()=>{let resolve;return {p:new Promise(r=>resolve=r),resolve:v=>resolve(v)}};
const ok=v=>({ok:true,status:200,text:async()=>JSON.stringify(v)});
function env(){const tab={id:'\\''A'\\''},dom={},notes=[],cancels=[],poll=deferred(),polled=deferred(); let timers=[];
const e=id=>(dom[id]??={value:'\\'''\\'',style:{},classList:{add(){},remove(){}},setAttribute(){}});
const c={console,DOMException,AbortController,document:{getElementById:e,querySelector:()=>e('\\''runButton'\\'')},state:{rawBE:[283,284,285,286,287],rawIntensity:[1,2,3,4,5],peaks:[{id:1}],ccShift:0},tabManager:{activeId:'\\''A'\\'',_getTab:()=>tab},notify:(...a)=>notes.push(a),_opOwner:()=>tab,_ownerActive:()=>true,isC1sTab:()=>true,_showAutoFitConfirmModal:async()=>true,_autoFitSnapshot:()=>({}),_autoFitRestore(){},getROIData:()=>({be:c.state.rawBE,inten:c.state.rawIntensity}),computeBackground:be=>be.map(()=>0),pushUndo(){},_bgWindowIndices:()=>({i0:0,i1:4}),peakToBackendSpec:p=>p,_startsUnlinkedCount:()=>1,_startsLiveKey:()=> '\\''same'\\'',_sameFitKey:(a,b)=>a===b,uploadToBackend:async()=> '\\''sid'\\'',_getManualAnchors:()=>[],_updateBgSubPillEnabled(){},setTimeout:f=>{timers.push(f);return timers.length},clearTimeout(){},fetch:async u=>{if(u.includes('\\''/cancel/'\\'')){cancels.push(u);return ok({});}if(u.endsWith('\\''/start'\\''))return ok({job_id:'\\''J'\\''});polled.resolve();return poll.p;}};
vm.createContext(c);vm.runInContext(init+'\\''\\n'\\''+names.map(ex).join('\\''\\n'\\''),c);return {c,dom,notes,cancels,poll,polled,step:()=>timers.shift()(),tab};}

(async()=>{
 // Cancelling the modal must leave the running fit and its spinner intact.
 let z=env(), modal=deferred(); let old=z.c.runFit();await new Promise(r=>setImmediate(r));z.step();z.step();await z.polled.p;
 z.c._showAutoFitConfirmModal=()=>modal.p;const af=z.c.runAutoFitC1sGraphite();modal.resolve(false);await af;
 assert.equal(z.cancels.length,0);assert.equal(z.dom['\\''fit-spinner-overlay'\\''].style.display,'\\''flex'\\'');
 z.poll.resolve(ok({status:'\\''cancelled'\\''}));await old;assert.equal(z.dom['\\''fit-spinner-overlay'\\''].style.display,'\\''none'\\'');
 console.log('\\''PASS actual callers: cancelled Auto-Fit modal preserves Run Fit; terminal cleanup works.'\\'');
 // The newer Run Fit must win even if the older Auto-Fit confirms later.
 z=env();modal=deferred();z.c._showAutoFitConfirmModal=()=>modal.p;let snapshots=0;z.c._autoFitSnapshot=()=>{snapshots++;return {}};
 const earlier=z.c.runAutoFitC1sGraphite();old=z.c.runFit();await new Promise(r=>setImmediate(r));z.step();z.step();await z.polled.p;
 modal.resolve(true);await earlier;assert.equal(snapshots,0);assert.equal(z.cancels.length,0);
 z.poll.resolve(ok({status:'\\''cancelled'\\''}));await old;
 console.log('\\''PASS actual callers: Auto-Fit numbered before Run Fit, confirmed after it, changes nothing.'\\'');
 // Two in-flight fits on distinct tabs: A'\\''s late failure must leave B'\\''s spinner alone.
 z=env();let active=z.tab;z.c._opOwner=()=>active;z.c._ownerActive=o=>o===active;
 const gates=[deferred(),deferred()], reached=[deferred(),deferred()];let count=0;
 z.c.fetch=async u=>{if(u.endsWith('\\''/start'\\''))return ok({job_id:String(count++)});if(u.includes('\\''/cancel/'\\''))return ok({});const n=+u.split('\\''/'\\'').pop();reached[n].resolve();return gates[n].p;};
 const a=z.c.runFit();await new Promise(r=>setImmediate(r));z.step();z.step();await reached[0].p;
 active={id:'\\''B'\\''};const b=z.c.runFit();await new Promise(r=>setImmediate(r));z.step();z.step();await reached[1].p;
 gates[0].resolve(ok({status:'\\''cancelled'\\''}));await a;
 assert.equal(z.dom['\\''fit-spinner-overlay'\\''].style.display,'\\''flex'\\'');assert.equal(z.dom.runButton.disabled,true);
 gates[1].resolve(ok({status:'\\''cancelled'\\''}));await b;assert.equal(z.dom['\\''fit-spinner-overlay'\\''].style.display,'\\''none'\\'');
 console.log('\\''PASS actual callers: tab A late error leaves tab B spinner; B terminal path clears it.'\\'');
 // Batch'\\''s local fitter still calls the unowned hide.
 z=env();old=z.c.runFit();await new Promise(r=>setImmediate(r));z.step();z.step();await z.polled.p;
 vm.runInContext(ex('\\''runFitLocal'\\''),z.c);z.c.runFitLocal([],[],[]);
 assert.equal(z.dom['\\''fit-spinner-overlay'\\''].style.display,'\\''none'\\'');assert.equal(vm.runInContext('\\''_runningFitJobs.size'\\'',z.c),1);
 console.log('\\''REPRO Batch/local fit failure: live server job = 1, spinner hidden, Run Fit enabled.'\\'');
 z.poll.resolve(ok({status:'\\''cancelled'\\''}));await old;
})();
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 64ms:
PASS actual callers: Auto-Fit numbered before Run Fit, confirmed after it, changes nothing.
PASS actual callers: tab A late error leaves tab B spinner; B terminal path clears it.
REPRO Batch/local fit failure: live server job = 1, spinner hidden, Run Fit enabled.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"-q\", \"-p\", \"no:cacheprovider\", \"--capture=no\", \"tests/test_fit_start_poll.py\", \"-k\", \"test_a_cancel_observed_mid_fit\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 2185ms:
...
3 passed, 17 deselected in 1.73s

codex
I reproduced a new cleanup failure with the actual callers: Auto-Fit cancels a running Run Fit, then rejects an ROI with no strong peak. Both operations finish, but the spinner stays visible and Run Fit stays disabled. Cancelled-modal, late-confirmation, and cross-tab spinner probes pass. Batch Fit also still reaches an unowned spinner hide through the local fitter.
exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '7484,7508p;7747,7758p;8247,8257p;8515,8527p;8877,8886p;12535,12549p' && git status --short" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
  7484	// (_installFitOp) — only if no newer operation has claimed the tab meanwhile
  7485	// (Codex round 3: Auto-Fit's confirmation modal sits between the two; a Run
  7486	// Fit pressed while it is open must win, and opening the modal must not kill
  7487	// a running fit the student may still keep by cancelling the modal).
  7488	function _newFitOp(owner) { return { seq: ++_fitOpSeq, owner: owner || null, jobId: null }; }
  7489	function _installFitOp(op) {
  7490	  if (!op || !op.owner) return true;
  7491	  const cur = _fitOpByOwner.get(op.owner);
  7492	  if (cur && cur.seq > op.seq) return false;          // a newer operation owns the tab
  7493	  if (cur && cur !== op && cur.jobId) _cancelFitJob(cur.jobId);
  7494	  _fitOpByOwner.set(op.owner, op);
  7495	  return true;
  7496	}
  7497	function _claimFitOp(owner) { const op = _newFitOp(owner); _installFitOp(op); return op; }
  7498	function _fitOpCurrent(op) { return !op || !op.owner || _fitOpByOwner.get(op.owner) === op; }
  7499	// The fit spinner is page-wide, one per page; the operation that showed it
  7500	// owns it. A fit that ends after another tab's fit took the spinner leaves it
  7501	// alone (Codex round 3: a discarded tab-A fit hid tab B's running spinner).
  7502	let _fitSpinnerOp = null;
  7503	function _hideFitSpinnerFor(op) {
  7504	  if (_fitSpinnerOp !== op) return;
  7505	  _fitSpinnerOp = null;
  7506	  _hideFitSpinner();
  7507	}
  7508	function _cancelFitJob(jobId) {
  7747	      signal: ctrl.signal,
  7748	      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
  7749	    });
  7750	    clearTimeout(timer);
  7751	    // superseded by a newer fit on this tab (Run Fit pressed during Auto-Fit):
  7752	    // that fit started from the model now on the tab and owns the result — no
  7753	    // rollback here, which would overwrite it
  7754	    if (json && json._abandoned === 'superseded') return;
  7755	    // F2: a non-2xx reply is a failed REQUEST with its status in the message
  7756	    // (_serverFitJob throws it with httpStatus); an unreadable reply is a
  7757	    // failed fit with its own message (unreadableReply).
  7758	    if (json && json._abandoned === 'tab') {
  8247	    // so a switched tab or an edited model stops the server's work at once.
  8248	    const json = await _serverFitJob(fitReq, {
  8249	      op: fitOp,
  8250	      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
  8251	    });
  8252	    if (json && json._abandoned === 'superseded') return;   // a newer fit on this tab owns the spinner and the result
  8253	    if (json && json._abandoned === 'tab') {
  8254	      _hideFitSpinnerFor(fitOp);
  8255	      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
  8256	      notify('Fit result discarded because you switched tabs during the fit.', 'amber');
  8257	      return;
  8515	// committed lab project; the proof is in
  8516	// docs/superpowers/plans/2026-09-15-a01-local-lm-proof.md.
  8517	function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
  8518	  const maxIter = Number.isFinite(options.maxIterations) ? options.maxIterations : 3000;
  8519	  const fail = (message, iterations) => {
  8520	    _hideFitSpinner();
  8521	    document.getElementById('sb-msg').textContent = 'Local fit failed';
  8522	    notify('Local fit did not converge: ' + message + ' Previous peaks and result kept.', 'red', true);
  8523	    return { success: false, engine: 'local', message, iterations: iterations || 0 };
  8524	  };
  8525	  if (!Array.isArray(be) || be.length < 2 ||
  8526	      !Array.isArray(bgSubtracted) || bgSubtracted.length !== be.length ||
  8527	      !Array.isArray(bgIntensity) || bgIntensity.length !== be.length ||
  8877	  renderPeakList();
  8878	  updatePlot();
  8879	  renderResults();
  8880	
  8881	  _hideFitSpinner();
  8882	  notify('Local fit converged in ' + iterations + ' iteration' + (iterations === 1 ? '' : 's') +
  8883	         '. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3) + ' (Poisson-weighted; no uncertainties). Starting point only: run Fit before reporting.', 'amber');
  8884	  _autoSnapshot();
  8885	  return { success: true, engine: 'local', iterations, acceptedSteps, chiReduced, certifyRestarts };
  8886	}
 12535	      notify('Batch fit stopped at ' + tgt.name + ' — the tab changed while it was running.', 'amber');
 12536	      break;
 12537	    }
 12538	
 12539	    // Run local fit
 12540	    const roiSt = _roiWindowStatus();    // warn only: the fit below uses getROIData() exactly as before
 12541	    const { be, inten } = getROIData();
 12542	    const bgI = computeBackground(be, inten);
 12543	    const bgSub = inten.map((v, idx) => v - bgI[idx]);
 12544	    const outcome = runFitLocal(be, bgSub, bgI);
 12545	
 12546	    // Sync result back to record
 12547	    tabManager._syncActiveToRecord();
 12548	
 12549	    // Read the statistic from the fit's own return value, not from live
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-jAN6B4hU' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-vQFYlSFp' (errno=Operation not permitted)
?? docs/autofit/codex/fit_start_poll_r4_verdict_runA.md
?? docs/autofit/codex/fit_start_poll_r4_verdict_runB.md

exec
/bin/zsh -lc "node -e '
const fs=require('\\''fs'\\''),vm=require('\\''vm'\\''),assert=require('\\''assert'\\'');
const html=require('\\''child_process'\\'').execFileSync('\\''git'\\'',['\\''show'\\'','\\''HEAD~1:templates/index.html'\\''],{encoding:'\\''utf8'\\'',stdio:['\\''ignore'\\'','\\''pipe'\\'','\\''ignore'\\'']}),lines=html.split('\\''\\n'\\'');
function ex(n){let s=lines.findIndex(l=>new RegExp('\\''"'^(async )?function '"'\\''+n+'\\''\\\\('\\'').test(l)),d=0;for(let i=s;i<lines.length;i++){for(const c of lines[i]){if(c==='\\''{'\\'')d++;if(c==='\\''}'\\'')d--;}if(d===0)return lines.slice(s,i+1).join('\\''\\n'\\'');}throw n;}
const names=['\\''runFit'\\'','\\''runAutoFitC1sGraphite'\\'','\\''_newFitOp'\\'','\\''_installFitOp'\\'','\\''_claimFitOp'\\'','\\''_fitOpCurrent'\\'','\\''_hideFitSpinnerFor'\\'','\\''_cancelFitJob'\\'','\\''_fitHttpError'\\'','\\''_readFitReply'\\'','\\''_serverFitJob'\\'','\\''_showFitSpinner'\\'','\\''_hideFitSpinner'\\'','\\''findGraphiteRawBE'\\''];
const init='\\''let _fitOpSeq=0,_fitSpinnerOp=null,_bgSubFitInFlight=false; const _fitOpByOwner=new WeakMap(),_runningFitJobs=new Set(); const FIT_POLL_MS=500,FIT_POLL_TRANSPORT_RETRIES=5,FIT_HEARTBEAT_LOST_SEC=30,_STARTS_N=3;'\\'';
const deferred=()=>{let resolve;return {p:new Promise(r=>resolve=r),resolve:v=>resolve(v)}};
const ok=v=>({ok:true,status:200,text:async()=>JSON.stringify(v)});
function env(){const tab={id:'\\''A'\\''},dom={},notes=[],cancels=[],poll=deferred(),polled=deferred(); let timers=[];
const e=id=>(dom[id]??={value:'\\'''\\'',style:{},classList:{add(){},remove(){}},setAttribute(){}});
const c={console,DOMException,AbortController,document:{getElementById:e,querySelector:()=>e('\\''runButton'\\'')},state:{rawBE:[283,284,285,286,287],rawIntensity:[1,2,3,4,5],peaks:[{id:1}],ccShift:0},tabManager:{activeId:'\\''A'\\'',_getTab:()=>tab},notify:(...a)=>notes.push(a),_opOwner:()=>tab,_ownerActive:()=>true,isC1sTab:()=>true,_showAutoFitConfirmModal:async()=>true,_autoFitSnapshot:()=>({}),_autoFitRestore(){},getROIData:()=>({be:c.state.rawBE,inten:c.state.rawIntensity}),computeBackground:be=>be.map(()=>0),pushUndo(){},_bgWindowIndices:()=>({i0:0,i1:4}),peakToBackendSpec:p=>p,_startsUnlinkedCount:()=>1,_startsLiveKey:()=> '\\''same'\\'',_sameFitKey:(a,b)=>a===b,uploadToBackend:async()=> '\\''sid'\\'',_getManualAnchors:()=>[],_updateBgSubPillEnabled(){},setTimeout:f=>{timers.push(f);return timers.length},clearTimeout(){},fetch:async u=>{if(u.includes('\\''/cancel/'\\'')){cancels.push(u);return ok({});}if(u.endsWith('\\''/start'\\''))return ok({job_id:'\\''J'\\''});polled.resolve();return poll.p;}};
vm.createContext(c);vm.runInContext(init+'\\''\\n'\\''+names.filter(n=>lines.some(l=>new RegExp('\\''"'^(async )?function '"'\\''+n+'\\''\\\\('\\'').test(l))).map(ex).join('\\''\\n'\\''),c);return {c,dom,notes,cancels,poll,polled,step:()=>timers.shift()(),tab};}
(async()=>{
 const z=env(); const old=z.c.runFit();await new Promise(r=>setImmediate(r));z.step();z.step();await z.polled.p;
 await z.c.runAutoFitC1sGraphite();z.poll.resolve(ok({status:'\\''cancelled'\\''}));await old;
 const out={cancels:z.cancels,notes:z.notes,spinner:z.dom['\\''fit-spinner-overlay'\\''].style.display,buttonDisabled:z.dom.runButton.disabled,inFlight:vm.runInContext('\\''_bgSubFitInFlight'\\'',z.c),running:vm.runInContext('\\''_runningFitJobs.size'\\'',z.c)};
 console.log('\\''HEAD~1 comparison, same preflight failure followed by old fit terminal reply:'\\'',JSON.stringify(out));
 assert.equal(out.running,0);assert.equal(out.spinner,'\\''none'\\'');assert.equal(out.buttonDisabled,false);assert.equal(z.cancels.length,0);
})();
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 22ms:
HEAD~1 comparison, same preflight failure followed by old fit terminal reply: {"cancels":[],"notes":[["No strong peak found in the C1s ROI; Auto-Fit cannot proceed.","red",true],["Fit failed: The fit was stopped on the server before it finished. Run it again. Previous peaks and result kept.","red",true]],"spinner":"none","buttonDisabled":false,"inFlight":false,"running":0}

codex
1. **MAJOR — Auto-Fit’s preliminary failure strands the fitting UI.** [templates/index.html:7641](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7641). Start Run Fit on a C1s ROI containing a monotonic slope, then confirm Auto-Fit. Installing Auto-Fit cancels the running fit; the “no strong peak” return at line 7659 exits before taking or clearing its spinner. The superseded Run Fit also returns without cleanup. **Reproduced:** zero registered jobs, spinner permanently visible, Run Fit disabled, `_bgSubFitInFlight=true`. The previous commit clears the UI. Every installed operation needs cleanup, including preliminary failures.

2. **MINOR — Batch Fit still bypasses spinner ownership.** [templates/index.html:8520](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8520), [templates/index.html:8881](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8881). While a server fit is pending, Batch Fit’s local fitter unconditionally hides the shared spinner on failure or success. A quick batch returning to the source before its next poll can leave that server fit running with no spinner. The failure-path probe reproduced this.

Validation: **90 JavaScript tests and 3 numerical cancellation tests passed.** Actual-caller probes confirmed cancelled-modal, late-confirmation and cross-tab ownership fixes. Existing tests miss the preliminary-failure cleanup regression. Full browser and long-fit acceptance were not rerun. No files changed.

**VERDICT: NO-GO**
tokens used
100,555
1. **MAJOR — Auto-Fit’s preliminary failure strands the fitting UI.** [templates/index.html:7641](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7641). Start Run Fit on a C1s ROI containing a monotonic slope, then confirm Auto-Fit. Installing Auto-Fit cancels the running fit; the “no strong peak” return at line 7659 exits before taking or clearing its spinner. The superseded Run Fit also returns without cleanup. **Reproduced:** zero registered jobs, spinner permanently visible, Run Fit disabled, `_bgSubFitInFlight=true`. The previous commit clears the UI. Every installed operation needs cleanup, including preliminary failures.

2. **MINOR — Batch Fit still bypasses spinner ownership.** [templates/index.html:8520](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8520), [templates/index.html:8881](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8881). While a server fit is pending, Batch Fit’s local fitter unconditionally hides the shared spinner on failure or success. A quick batch returning to the source before its next poll can leave that server fit running with no spinner. The failure-path probe reproduced this.

Validation: **90 JavaScript tests and 3 numerical cancellation tests passed.** Actual-caller probes confirmed cancelled-modal, late-confirmation and cross-tab ownership fixes. Existing tests miss the preliminary-failure cleanup regression. Full browser and long-fit acceptance were not rerun. No files changed.

**VERDICT: NO-GO**
