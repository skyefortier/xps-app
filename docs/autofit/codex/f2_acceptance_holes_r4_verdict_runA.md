2026-09-27T08:25:24.429540Z ERROR codex_models_manager::manager: failed to load models cache: EOF while parsing a value at line 1 column 0
OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0e1f8-0c51-74d0-9d7e-063b3bda7e65
--------
user
Re-review unit F2 (holes in the acceptance rule), round 4: branch fix-acceptance-holes. Round 3 was GO x2 with one MINOR from both runs (docs/autofit/codex/f2_acceptance_holes_r3_verdict_run{A,B}.md): a minus sign before Infinity counted in _readFitReply's non-finite scan without a boundary before it ("x-Infinity", "--Infinity" read as a non-finite number instead of an unreadable reply). The fix is the commit at HEAD (git diff HEAD~1..HEAD): the sign now needs a boundary before it; a regression test in tests/js/fit_acceptance.test.js. Earlier prompts (brief, sites, rounds 1-3): docs/autofit/codex/f2_acceptance_holes_review_prompt.txt, _recheck_prompt.txt, _recheck2_prompt.txt; plan docs/superpowers/plans/2026-09-26-f2-acceptance-holes.md section 5. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

TRY TO BREAK
a. The one-line change: every token position (start of body, after [ , : { whitespace, after a sign at the start of the body, "-Infinity" at t[0], "-" at i-1 with i-2 undefined), and that nothing else in the scanner or _readFitReply changed.
b. The regression test: real and non-vacuous (would fail on the round-3 code).
c. A last pass over the whole unit (git diff main..HEAD) for anything the earlier rounds could not see because of what they were shown.

Finish with VERDICT: GO or VERDICT: NO-GO.

codex
I’ll check the HEAD fix and whether its regression test fails on round 3, then review the full unit diff for missed acceptance cases. I’ll keep the review read-only and finish with a verdict.

exec
/bin/zsh -lc "pwd; git status --short; rg --files -g AGENTS.md -g '*f2_acceptance*' -g '*fit_acceptance*' -g '*2026-09-26-f2*'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-9eM1tdvh' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-o66Uk583' (errno=Operation not permitted)
?? docs/autofit/codex/f2_acceptance_holes_r4_verdict_runA.md
?? docs/autofit/codex/f2_acceptance_holes_r4_verdict_runB.md
docs/superpowers/plans/2026-09-26-f2-acceptance-holes.md
tests/test_fit_acceptance_holes.py
tests/js/fit_acceptance.test.js
docs/autofit/codex/f2_acceptance_holes_recheck2_prompt.txt
docs/autofit/codex/f2_acceptance_holes_r3_verdict_runA.md
docs/autofit/codex/f2_acceptance_holes_verdict_runB.md
docs/autofit/codex/f2_acceptance_holes_r4_verdict_runA.md
docs/autofit/codex/f2_acceptance_holes_review_prompt.txt
docs/autofit/codex/f2_acceptance_holes_recheck_prompt.txt
docs/autofit/codex/f2_acceptance_holes_r2_verdict_runA.md
docs/autofit/codex/f2_acceptance_holes_r2_verdict_runB.md
docs/autofit/codex/f2_acceptance_holes_recheck3_prompt.txt
docs/autofit/codex/f2_acceptance_holes_r3_verdict_runB.md
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md
docs/autofit/codex/f2_acceptance_holes_r4_verdict_runB.md

exec
/bin/zsh -lc 'git diff HEAD~1..HEAD; git diff --stat main..HEAD' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 7ms:
 CLAUDE.md                                          |    52 +-
 .../codex/f2_acceptance_holes_r2_verdict_runA.md   | 14912 +++++++++++
 .../codex/f2_acceptance_holes_r2_verdict_runB.md   | 24402 +++++++++++++++++++
 .../codex/f2_acceptance_holes_r3_verdict_runA.md   |  3452 +++
 .../codex/f2_acceptance_holes_r3_verdict_runB.md   |  3394 +++
 .../codex/f2_acceptance_holes_recheck2_prompt.txt  |    21 +
 .../codex/f2_acceptance_holes_recheck3_prompt.txt  |     8 +
 .../codex/f2_acceptance_holes_recheck_prompt.txt   |    20 +
 .../codex/f2_acceptance_holes_review_prompt.txt    |    81 +
 .../codex/f2_acceptance_holes_verdict_runA.md      |  5974 +++++
 .../codex/f2_acceptance_holes_verdict_runB.md      |  4646 ++++
 docs/findings/2026-09-26-public-request-ceiling.md |    59 +
 .../plans/2026-09-22-dsg-page-evaluator.md         |     9 +
 .../plans/2026-09-26-f2-acceptance-holes.md        |   121 +
 fitting.py                                         |    82 +-
 templates/index.html                               |    78 +-
 tests/js/autofit_required.test.js                  |    21 +-
 tests/js/fit_acceptance.test.js                    |    77 +-
 tests/js/local_lm_descent.test.js                  |    23 +
 tests/js/stale_statistics.test.js                  |    56 +-
 tests/test_basinhopping_outcome.py                 |   125 +
 tests/test_fit_acceptance_holes.py                 |   116 +
 tests/test_fit_reproducibility.py                  |    17 +-
 23 files changed, 57728 insertions(+), 18 deletions(-)

exec
/bin/zsh -lc 'for p in /AGENTS.md /Users/AGENTS.md /Users/skyefortier/AGENTS.md /Users/skyefortier/xps-app/AGENTS.md /Users/skyefortier/xps-app/.claude/AGENTS.md /Users/skyefortier/xps-app/.claude/worktrees/AGENTS.md AGENTS.md; do if test -f "$p"; then cat "$p"; fi; done; cat docs/autofit/codex/f2_acceptance_holes_review_prompt.txt docs/autofit/codex/f2_acceptance_holes_recheck_prompt.txt docs/autofit/codex/f2_acceptance_holes_recheck2_prompt.txt docs/superpowers/plans/2026-09-26-f2-acceptance-holes.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
Review unit F2 (holes in the acceptance rule): branch fix-acceptance-holes, git diff main..HEAD (fitting.py, templates/index.html, tests/test_fit_acceptance_holes.py, tests/test_basinhopping_outcome.py, tests/test_fit_reproducibility.py, tests/js/fit_acceptance.test.js, tests/js/stale_statistics.test.js, tests/js/autofit_required.test.js, tests/js/local_lm_descent.test.js, CLAUDE.md, docs/superpowers/plans/2026-09-26-f2-acceptance-holes.md). Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

OWNER'S BRIEF (verbatim): "nothing is a fit unless it converged and is determined: basinhopping success from the real scipy result; a NaN in an /api/fit reply is a failed fit with a message, not a local fallback; n_free > n_data is refused as undetermined; the required verdict requires a converged refit."
Owner decisions since (verbatim in the plan, section 2): basinhopping is verified by refinement AND competes with a plain least_squares fit from the same start (the full DE pattern), because scipy's own flag failed 23 of 24 sampled fits that sit at Trust-Region's minimum; refusal at n_free >= n_data (equality accepted); an unconverged required-refit blocks the Auto-Fit anchor.

NOTE — ALSO IN THIS UNIT, BY OWNER INSTRUCTION: BASINHOPPING RUNS NO PERTURBED RESTARTS. Measured with the page's request (n_perturb 3) after the refinement change: 14 of 16 multi-component targets exceeded the production server's 300 s timeout (median 386 s, max 1066 s); without the restarts median 96 s, max 256 s, chi2r identical to 1e-8 on all 16. run_fit skips the perturb loop for basinhopping only. Review that change like the rest.

Out of scope (reported separately, docs/findings/2026-09-26-public-request-ceiling.md; do NOT treat as a finding against F2): the public URL's Cloudflare 524 ceiling between 88 s and 125 s.

PLAN SECTIONS 1-3 (sites, decisions, measurements), verbatim:

## 1. Sites

| # | hole | site | before | after |
|---|---|---|---|---|
| 1 | basinhopping always "converged" (H2) | `fitting.fit_model` → new `_basinhopping_candidate` | lmfit sets `success = True` before minimising and its basinhopping never reads scipy's result | the DE pattern in full (owner decision, §2): search → unconditional `least_squares` refinement from its point under the request's bounds (the refinement's convergence is the verdict; no χ² comparison, no tolerance) → competition with a `least_squares` fit from the same start (verified beats unverified, then lower χ²). An unverifiable search is `success: false` with its own message. `fit_model` is the ONE fitter, so the main fit, every perturbed restart and the required refit all go through it; scattered starts do not run for basinhopping. |
| 2 | a 2xx `/api/fit` reply with NaN switched to the local engine (M1) | page `_readFitReply` (new), used by `runFit` and `runAutoFitC1sGraphite` (the only two `/api/fit` callers) | `resp.json()` threw a SyntaxError, which `_asTransport` classified as a transport failure → `runFitLocal` replaced the server's converged result, verdicts and starts evidence | the body is read as text (a failure THERE is transport: the connection dropped) and parsed by the page; a body that was read but is not JSON is the server's reply → `serverError`, a failed fit with its message ("contains a non-finite number (NaN or Infinity) …" / "could not be read"), previous peaks and result kept, no fallback. Auto-Fit fails closed with the same message (it used to say "failed to converge or produced an unphysical graphite position"). The server is unchanged: the page, not a sanitiser, decides that a non-finite reply is not a fit. |
| 3 | n_data ≤ n_free read as a near-perfect, fully supported fit (M2) | `fitting.run_fit` before the fit; page `runFitLocal` after its free-parameter list | lmfit `redchi = χ²/max(1, nfree)`; the support / required F tests clamp dof to 1; the local engine clamps too | refused: `ValueError` "not determined by these data: N free parameters for M data points leaves no degrees of freedom …" (HTTP 400 on `/api/fit`; the same message through Find Peaks' refit, `/api/analyze`); the local engine fails with the same text, nothing written. A COUNT, not a threshold. Refused at n_free ≥ n_data (§2). |
| 4 | the required verdict ignored its refit's convergence (M3) | `fitting._component_required`; page `applyAutoFitResult` | `required` computed whether or not the refit converged (a refit stopped early read "required", F 992, for a redundant anchor); the page never read `refit_converged` | an unconverged refit returns `required: null, f: null, refit_converged: false, reason: "refit_not_converged"` (+ the solver message); Auto-Fit REFUSES that anchor before any charge-correction input is touched (red notice) — an anchor whose necessity could not be established must not set the energy reference of the whole spectrum. A check that did not RUN at all (older server, exception, nothing left, main fit not converged) still never blocks, as documented. |

| 5 | Auto-Fit parsed a non-2xx reply (owner, 2026-09-27) | page `runAutoFitC1sGraphite` | a Cloudflare 524 or gunicorn 500 reached `_readFitReply` and read as "the server's reply could not be read" — F2's own message misfiring | `resp.ok === false` is a failed REQUEST with its status in the message ("Auto-fit failed: Fit request failed (HTTP 524)."; a JSON `error` body's text when there is one), before any parsing, as Run Fit has done since A0 |

## 2. Decisions

- **Basinhopping (owner, 2026-09-26).** The brief said "success from the real
  scipy result". Measured first (scipy's flag recorded by a pass-through
  wrapper around the name lmfit calls): on a 1-in-8 sample of the 202
  committed targets (24 of 26 run), scipy marks **23 of 24** basinhopping fits
  failed — BFGS "Desired error not necessarily achieved due to precision
  loss" — while their χ²ᵣ equals Trust-Region's from the same start (median
  relative difference 1.3e-9; one 0.14 % worse; several better). Taken
  literally the method would fail on almost every correct fit. Owner chose:
  verify by refinement AND compete with a plain `least_squares` fit from the
  same start — the guarantee differential evolution already has ("never worse
  than the default method from the same start"). The wrapper was removed; no
  monkeypatching remains.
- **n_free = n_data is refused too.** The brief says "n_free > n_data". At
  equality there are zero degrees of freedom: the model interpolates every
  point, reduced χ² is undefined (lmfit divides by max(1, 0)) and the F tests
  run on a clamped dof of 1 — the same fault as the sweep's reproduction. The
  refusal is at n_free ≥ n_data; one degree of freedom is fitted as before.
- **An unconverged required-refit blocks Auto-Fit.** "The required verdict
  requires a converged refit": the server gives no verdict, and the page does
  not let an anchor with no verdict set the charge reference. The documented
  "a check that did not run never blocks" is kept for checks that did not
  run.

- **No perturbed restarts for basinhopping (owner, 2026-09-26).** Measured
  after the refinement change, with the page's request (`n_perturb` 3), on 16
  committed multi-component targets spread over 2–7 components (4 processes,
  8 physical cores — production runs 4 workers): median 386 s, max 1066 s,
  **14 of 16 over the 300 s server timeout**. Without the restarts: median
  96 s, max 256 s, none over 300 s, and χ²ᵣ identical on all 16 (worst
  relative difference 1e-8) — a global search gains nothing from them, the
  reason the scattered-starts check already excludes basinhopping and DE.
  `run_fit` skips the perturb loop for basinhopping (the request's
  `n_perturb` is still hashed into the seed; nothing else changes). DE keeps
  its restarts (2–75 s; not in the brief).

## 3. Measurements

| measurement | before F2 | after F2 |
|---|---|---|
| basinhopping, 1-in-8 sample of the 202 targets (26), `n_perturb` 0 | lmfit `success: true` on all (unconditional); scipy's own flag "failed" on 23 of 24 (BFGS precision loss) at Trust-Region's minimum | 26 of 26 verified; never worse than Trust-Region from the same start; up to 19 % lower χ²ᵣ; median relative difference −1.9e-10 |
| basinhopping wall time, page request, 16 multi-component targets | — | with restarts: median 386 s, max 1066 s, 14/16 > 300 s → restarts skipped: median 96 s, max 256 s, 0/16 > 300 s |

The public URL has a lower ceiling (Cloudflare 524 between 88 s and 125 s):
5 of those 16 still exceed it without restarts. Reported separately, not
fixed here: `docs/findings/2026-09-26-public-request-ceiling.md`.


TRY TO BREAK
a. _basinhopping_candidate: is every basinhopping minimisation (main fit, required refit, anything else that calls fit_model) verified; can an unverified search ever be returned with success true; does the competitor ever get the search's generated state instead of the request's start and bounds; seeding (the search seeded, the two least_squares not; the request seed unchanged; n_perturb still hashed); the 'aborted' case; the message returned; the result's params/stderr/bounds vs what the page stores; a linked (expr) parameter across the refinement; nan_policy.
b. The restart skip: anything else keyed on n_perturb (the seed, perturb_rng stream alignment for OTHER methods, the response, /api/analyze), DE unchanged, the page still sending n_perturb 3.
c. _readFitReply and Auto-Fit's new resp.ok check (site 5): is every 2xx /api/fit body read through it (Run Fit, alternative adoption, Auto-Fit) and every non-2xx one reported with its status before any parsing; can a truncated body (network) be misclassified as a server error or vice versa; the non-finite regex on a body where 'NaN' appears inside a string; the error path's message; _asTransport no longer reachable with a SyntaxError from the fit reply; resp.ok false paths unchanged; Auto-Fit's catch.
d. Determinacy refusal: count vs lmfit's nvarys (expr parameters, fixed parameters, the DE box, n_starts, the required refit's reduced model), NaN / non-finite y excluded consistently with nan_policy omit, the local engine's count vs its dof (caM held, discrete), Batch Fit's per-target message, Find Peaks' refit (/api/analyze) surfacing the ValueError, Auto-Fit.
e. Required: _component_required's new branch vs the existing non-finite branch; the page's refusal ordering (before any charge-correction input); required null from other reasons still non-blocking; the Python twin in autofit/* if any reads 'required'.
f. Tests: real, non-vacuous (would each fail without its fix?); the edited existing tests still test what they tested.
g. Docs vs code vs measurements (CLAUDE.md, plan).

Finish with VERDICT: GO or VERDICT: NO-GO.Re-review unit F2 (holes in the acceptance rule), round 2: branch fix-acceptance-holes. Round-1 commit 9210786; the fixes are the commit after it (git diff 9210786..HEAD); the whole unit is git diff main..HEAD. Round-1 verdicts: docs/autofit/codex/f2_acceptance_holes_verdict_run{A,B}.md; the round-1 prompt (brief, owner decisions, sites, measurements): docs/autofit/codex/f2_acceptance_holes_review_prompt.txt. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

Reminder (owner instruction, in the unit): basinhopping runs no perturbed restarts; Auto-Fit checks the HTTP status before parsing. Out of scope: the public URL's Cloudflare ~100 s ceiling (a separate unit is in progress on another branch).

ROUND-1 FINDINGS AND FIXES (plan section 5, verbatim):

**Round 1 — run A GO, run B NO-GO** (`f2_acceptance_holes_verdict_run{A,B}.md`):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (B): the required-refit guard read only `refit.success`; differential evolution can return `success: true, box_unverified: true` (its boxed search converged, both verifications failed) — reproduced as `required: true, refit_converged: true`, F ≈ 1.2e6 | `_component_required` treats `box_unverified` as not verified: no verdict, `refit_converged: false` (the main fit's acceptance rule already rejects such a candidate). Regression test. |
| 2 | MINOR (A, B): the non-finite diagnosis matched "NaN" inside a JSON string of a malformed body | JSON strings are blanked before the token test; the malformed body now reads "could not be read". Regression test (string, token, escaped quote, valid JSON with the word). |

TRY TO BREAK
a. The required guard: any other way a refit returns success true without being a verified fit of the reduced model (basinhopping's candidate, an aborted DE box, a least_squares competitor that won); does required still run for every method, and is the page's refusal reached for box_unverified too.
b. The token test: escaped quotes, a string containing a backslash at its end, a body cut inside a string, very large bodies (regex cost), Infinity inside a number like 1e999 serialised by Python (Flask writes Infinity).
c. Anything round 1 raised or verified that the fixes changed.
d. Tests: real and non-vacuous.

Finish with VERDICT: GO or VERDICT: NO-GO.Re-review unit F2 (holes in the acceptance rule), round 3: branch fix-acceptance-holes. Round-2 fixes = HEAD (git diff a5a14a0..HEAD); the whole unit is git diff main..HEAD. Earlier verdicts: docs/autofit/codex/f2_acceptance_holes_verdict_run{A,B}.md, f2_acceptance_holes_r2_verdict_run{A,B}.md; the round-1 prompt holds the brief and the sites. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

Out of scope: the public URL's Cloudflare ~100 s ceiling (another branch).

ROUND-2 FINDINGS AND FIXES (plan section 5, verbatim):

**Round 2 — run A GO, run B NO-GO** (`f2_acceptance_holes_r2_verdict_run{A,B}.md`;
both confirmed the round-1 required-refit fix with real solver probes across
all five methods):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (B), MINOR (A): the string-blanking regex was quadratic on an unterminated string of escaped quotes — 128 KB took 10 s on the page's thread | one linear scan tracking string and escape state (no regex); 128 KB stress case in the tests (< 500 ms) |
| 2 | MINOR (A, B): a body cut off INSIDE a string still read "non-finite number" | the scan keeps a string open to the end of the body; the truncated case reads "could not be read" |

TRY TO BREAK
a. The scanner in _readFitReply: linear on every input (unterminated strings, long runs of backslashes, a body of only quotes, 10 MB of digits); the string/escape state machine (\\ then ", \u escapes, a quote right after a backslash pair); token boundaries (NaN at the very start/end, -Infinity, "NaNx", 1e999 serialised as Infinity by Python, Infinity inside an object key position); a valid JSON body always parses first (the scanner only chooses the message of a body that did not parse).
b. Anything earlier rounds raised or verified that this change touched.
c. The tests: real and non-vacuous.

Finish with VERDICT: GO or VERDICT: NO-GO.# F2 — holes in the acceptance rule (2026-09-26)

Branch `fix-acceptance-holes` off main `07e8f46` (F1 deployed). Owner's
brief, second of the three sweep units: "nothing is a fit unless it
converged and is determined":

- basinhopping success from the real scipy result;
- a NaN in an /api/fit reply is a failed fit with a message, not a local
  fallback;
- n_free > n_data is refused as undetermined;
- the required verdict requires a converged refit.

Source findings: `docs/findings/2026-09-25-fail-open-guards-sweep.md` H2, M1,
M2, M3 (`sweep-fail-open-guards`). Medium effort.

## 1. Sites

| # | hole | site | before | after |
|---|---|---|---|---|
| 1 | basinhopping always "converged" (H2) | `fitting.fit_model` → new `_basinhopping_candidate` | lmfit sets `success = True` before minimising and its basinhopping never reads scipy's result | the DE pattern in full (owner decision, §2): search → unconditional `least_squares` refinement from its point under the request's bounds (the refinement's convergence is the verdict; no χ² comparison, no tolerance) → competition with a `least_squares` fit from the same start (verified beats unverified, then lower χ²). An unverifiable search is `success: false` with its own message. `fit_model` is the ONE fitter, so the main fit, every perturbed restart and the required refit all go through it; scattered starts do not run for basinhopping. |
| 2 | a 2xx `/api/fit` reply with NaN switched to the local engine (M1) | page `_readFitReply` (new), used by `runFit` and `runAutoFitC1sGraphite` (the only two `/api/fit` callers) | `resp.json()` threw a SyntaxError, which `_asTransport` classified as a transport failure → `runFitLocal` replaced the server's converged result, verdicts and starts evidence | the body is read as text (a failure THERE is transport: the connection dropped) and parsed by the page; a body that was read but is not JSON is the server's reply → `serverError`, a failed fit with its message ("contains a non-finite number (NaN or Infinity) …" / "could not be read"), previous peaks and result kept, no fallback. Auto-Fit fails closed with the same message (it used to say "failed to converge or produced an unphysical graphite position"). The server is unchanged: the page, not a sanitiser, decides that a non-finite reply is not a fit. |
| 3 | n_data ≤ n_free read as a near-perfect, fully supported fit (M2) | `fitting.run_fit` before the fit; page `runFitLocal` after its free-parameter list | lmfit `redchi = χ²/max(1, nfree)`; the support / required F tests clamp dof to 1; the local engine clamps too | refused: `ValueError` "not determined by these data: N free parameters for M data points leaves no degrees of freedom …" (HTTP 400 on `/api/fit`; the same message through Find Peaks' refit, `/api/analyze`); the local engine fails with the same text, nothing written. A COUNT, not a threshold. Refused at n_free ≥ n_data (§2). |
| 4 | the required verdict ignored its refit's convergence (M3) | `fitting._component_required`; page `applyAutoFitResult` | `required` computed whether or not the refit converged (a refit stopped early read "required", F 992, for a redundant anchor); the page never read `refit_converged` | an unconverged refit returns `required: null, f: null, refit_converged: false, reason: "refit_not_converged"` (+ the solver message); Auto-Fit REFUSES that anchor before any charge-correction input is touched (red notice) — an anchor whose necessity could not be established must not set the energy reference of the whole spectrum. A check that did not RUN at all (older server, exception, nothing left, main fit not converged) still never blocks, as documented. |

| 5 | Auto-Fit parsed a non-2xx reply (owner, 2026-09-27) | page `runAutoFitC1sGraphite` | a Cloudflare 524 or gunicorn 500 reached `_readFitReply` and read as "the server's reply could not be read" — F2's own message misfiring | `resp.ok === false` is a failed REQUEST with its status in the message ("Auto-fit failed: Fit request failed (HTTP 524)."; a JSON `error` body's text when there is one), before any parsing, as Run Fit has done since A0 |

## 2. Decisions

- **Basinhopping (owner, 2026-09-26).** The brief said "success from the real
  scipy result". Measured first (scipy's flag recorded by a pass-through
  wrapper around the name lmfit calls): on a 1-in-8 sample of the 202
  committed targets (24 of 26 run), scipy marks **23 of 24** basinhopping fits
  failed — BFGS "Desired error not necessarily achieved due to precision
  loss" — while their χ²ᵣ equals Trust-Region's from the same start (median
  relative difference 1.3e-9; one 0.14 % worse; several better). Taken
  literally the method would fail on almost every correct fit. Owner chose:
  verify by refinement AND compete with a plain `least_squares` fit from the
  same start — the guarantee differential evolution already has ("never worse
  than the default method from the same start"). The wrapper was removed; no
  monkeypatching remains.
- **n_free = n_data is refused too.** The brief says "n_free > n_data". At
  equality there are zero degrees of freedom: the model interpolates every
  point, reduced χ² is undefined (lmfit divides by max(1, 0)) and the F tests
  run on a clamped dof of 1 — the same fault as the sweep's reproduction. The
  refusal is at n_free ≥ n_data; one degree of freedom is fitted as before.
- **An unconverged required-refit blocks Auto-Fit.** "The required verdict
  requires a converged refit": the server gives no verdict, and the page does
  not let an anchor with no verdict set the charge reference. The documented
  "a check that did not run never blocks" is kept for checks that did not
  run.

- **No perturbed restarts for basinhopping (owner, 2026-09-26).** Measured
  after the refinement change, with the page's request (`n_perturb` 3), on 16
  committed multi-component targets spread over 2–7 components (4 processes,
  8 physical cores — production runs 4 workers): median 386 s, max 1066 s,
  **14 of 16 over the 300 s server timeout**. Without the restarts: median
  96 s, max 256 s, none over 300 s, and χ²ᵣ identical on all 16 (worst
  relative difference 1e-8) — a global search gains nothing from them, the
  reason the scattered-starts check already excludes basinhopping and DE.
  `run_fit` skips the perturb loop for basinhopping (the request's
  `n_perturb` is still hashed into the seed; nothing else changes). DE keeps
  its restarts (2–75 s; not in the brief).

## 3. Measurements

| measurement | before F2 | after F2 |
|---|---|---|
| basinhopping, 1-in-8 sample of the 202 targets (26), `n_perturb` 0 | lmfit `success: true` on all (unconditional); scipy's own flag "failed" on 23 of 24 (BFGS precision loss) at Trust-Region's minimum | 26 of 26 verified; never worse than Trust-Region from the same start; up to 19 % lower χ²ᵣ; median relative difference −1.9e-10 |
| basinhopping wall time, page request, 16 multi-component targets | — | with restarts: median 386 s, max 1066 s, 14/16 > 300 s → restarts skipped: median 96 s, max 256 s, 0/16 > 300 s |

The public URL has a lower ceiling (Cloudflare 524 between 88 s and 125 s):
5 of those 16 still exceed it without restarts. Reported separately, not
fixed here: `docs/findings/2026-09-26-public-request-ceiling.md`.

## 4. Verification

- Python: `tests/test_fit_acceptance_holes.py` (refusal at 6 and 8 points for
  8 free parameters, fitted at 9; locked mixes free the count; `/api/fit`
  400 with the message; unconverged refit → no verdict, converged refit
  unchanged); `tests/test_basinhopping_outcome.py` (never worse than
  Trust-Region; search → refine → compete call sequence; an unverifiable
  search is not converged; a failed refinement rescued by the competitor;
  the required refit verified the same way; no perturbed restarts);
  `test_fit_reproducibility.py` updated (one seeded basinhopping
  minimisation per fit; the call sequence).
- JS: `fit_acceptance` (a 200 reply with NaN, and one that is not JSON, are
  failed fits; a body that cannot be READ is still transport → local);
  `stale_statistics` (Auto-Fit on a NaN reply fails closed, rolls back);
  `autofit_required` (unconverged refit refused before any charge input);
  `local_lm_descent` (the local engine refuses 6 free parameters for 5 and
  6 points, fits 40). Mocks gain `text()` (`withText`).
- Browser (:5151, committed UCl4-graphite project, replies intercepted where
  the case cannot be produced on demand): NaN reply → "Fit failed" with the
  non-finite message, no local overlay, peaks and result unchanged; a
  5-point ROI → "16 free parameters for 5 data points"; Auto-Fit with an
  unconverged refit → refused, charge correction unchanged. No page errors.

## 5. Codex rounds

**Round 1 — run A GO, run B NO-GO** (`f2_acceptance_holes_verdict_run{A,B}.md`):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (B): the required-refit guard read only `refit.success`; differential evolution can return `success: true, box_unverified: true` (its boxed search converged, both verifications failed) — reproduced as `required: true, refit_converged: true`, F ≈ 1.2e6 | `_component_required` treats `box_unverified` as not verified: no verdict, `refit_converged: false` (the main fit's acceptance rule already rejects such a candidate). Regression test. |
| 2 | MINOR (A, B): the non-finite diagnosis matched "NaN" inside a JSON string of a malformed body | JSON strings are blanked before the token test; the malformed body now reads "could not be read". Regression test (string, token, escaped quote, valid JSON with the word). |

**Round 2 — run A GO, run B NO-GO** (`f2_acceptance_holes_r2_verdict_run{A,B}.md`;
both confirmed the round-1 required-refit fix with real solver probes across
all five methods):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (B), MINOR (A): the string-blanking regex was quadratic on an unterminated string of escaped quotes — 128 KB took 10 s on the page's thread | one linear scan tracking string and escape state (no regex); 128 KB stress case in the tests (< 500 ms) |
| 2 | MINOR (A, B): a body cut off INSIDE a string still read "non-finite number" | the scan keeps a string open to the end of the body; the truncated case reads "could not be read" |

**Round 3 — GO ×2** (`f2_acceptance_holes_r3_verdict_run{A,B}.md`; both
measured the round-2 scanner at ~4 ms on the 128 KB stress case, < 124 ms on
10 MB bodies, the old one at 9.6 s). One MINOR from both, fixed: a minus sign
before `Infinity` counted without a boundary before it (`x-Infinity`,
`--Infinity` read "non-finite number"); the sign now needs a boundary too.
Regression test. Round 4 confirms the fix.

exec
/bin/zsh -lc 'git diff main..HEAD -- fitting.py templates/index.html tests/test_fit_acceptance_holes.py tests/test_basinhopping_outcome.py tests/test_fit_reproducibility.py tests/js/fit_acceptance.test.js tests/js/stale_statistics.test.js tests/js/autofit_required.test.js tests/js/local_lm_descent.test.js CLAUDE.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-puwpgsco' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ixtkgqrd' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index 610c751..67207b4 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -196,6 +196,17 @@ must read each field exactly the way its consumer reads it — integers as
 integers, energies through `parseFloat` — never a generic conversion
 (`_fitKeyCanon`). (Owner, 2026-09-26.)
 
+### Timing claims are measured through the public URL
+
+A request from a student reaches the server through Cloudflare, whose edge
+ends a proxied request at ~100 s (HTTP 524; probes through
+xps.fortierlab.org on 2026-09-26: 88 s passed, 125 s gave 524) — well short
+of gunicorn's `--timeout 300`. "300 s covers it" was written for the DS+G
+Run Fit in 2026-09-22 and was true on the i9 and false through the public
+URL. A claim that a request fits inside a limit is measured through
+xps.fortierlab.org, not on 127.0.0.1. (Owner, 2026-09-27;
+`docs/findings/2026-09-26-public-request-ceiling.md`.)
+
 ---
 
 ## Lineshape Physics — Critical Rules
@@ -358,6 +369,34 @@ exhaust DE's evaluation budget in every search and are rescued by the
 refinement). It is not a gold standard: on one 3-component B 1s target it
 returned χ²ᵣ 1.92 where Trust-Region found 1.81.
 
+`basinhopping` follows THE SAME PATTERN since unit F2 (2026-09-26; owner
+decision; plan `docs/superpowers/plans/2026-09-26-f2-acceptance-holes.md`):
+`_basinhopping_candidate` — the search, then an unconditional
+`least_squares` refinement from its point under the request's bounds (the
+refinement's convergence is the verdict, no χ² comparison), then a
+competition with a `least_squares` fit from the same start (verified beats
+unverified, then the lower χ²), for the main fit, every perturbed restart and
+the required refit. Until then basinhopping always reported `success: true`
+(lmfit sets it before minimising and never reads scipy's result), and
+scipy's own flag is no verdict either: it marked 23 of 24 sampled committed
+targets failed (BFGS "precision loss") at points equal to Trust-Region's
+minimum (median relative χ²ᵣ difference 1e-9). An unverifiable search is
+`success: false`. Basinhopping runs NO perturbed restarts (a global search:
+with the page's `n_perturb` 3 they took 14 of 16 multi-component targets past
+the 300 s server timeout, median 386 s, for χ²ᵣ identical to 1e-8; without
+them median 96 s, max 256 s). NOTE: the public URL's ceiling is lower —
+Cloudflare returns 524 between 88 s and 125 s — so the largest basinhopping
+models still fail there
+(`docs/findings/2026-09-26-public-request-ceiling.md`, not yet addressed).
+
+**Determinacy (unit F2).** `run_fit` refuses a model with at least as many
+free parameters as data points (`ValueError`, HTTP 400, "not determined by
+these data: N free parameters for M data points"), and so does the local
+engine: lmfit divides by max(1, nfree) and the F tests clamp dof to 1, so such
+a model read as a near-perfect, fully supported fit (6 points, 2 GL
+components: χ²ᵣ 2.8e-6, both "supported"). A count, not a threshold; one
+degree of freedom is fitted as before.
+
 **Reproducibility (2026-09-21).** Every random draw in `run_fit` — the
 `n_perturb` restarts (the page sends 3; ±15 % on every varying parameter)
 and the populations of `differential_evolution` and `basinhopping`, which
@@ -616,7 +655,13 @@ only if it converged. `runFitLocal` works on a copy and commits only on
 success, returning `{success, iterations, chiReduced}`; `runFit`
 treats `success !== true` from `/api/fit` as a failed fit and falls back to
 the local engine only on a transport failure, never on a server-side
-error. A RESULT IS DISCARDED IF THE MODEL WAS EDITED WHILE THE FIT WAS RUNNING
+error. A 2xx body that was READ but is not JSON is the server's reply, not a
+transport failure (unit F2): `_readFitReply` reads the text (a failure there
+is transport) and parses it; a NaN / Infinity token (Flask serialises a σ it
+could not compute that way) or any unparseable body is a failed fit with its
+message, for Run Fit and Auto-Fit alike — until F2 it sent Run Fit to the
+local engine, replacing the server's converged result, verdicts and starts
+evidence with a starting point. A RESULT IS DISCARDED IF THE MODEL WAS EDITED WHILE THE FIT WAS RUNNING
 (2026-09-22; a correctness fix for EVERY Run Fit, shipped with the
 scattered-starts check but independent of it). The peak controls stay
 editable during a fit. `runFit` captures the model-plus-context key
@@ -749,7 +794,10 @@ mean "zero" independently of the data):
   to machine precision F is meaningless and a truly redundant component can
   read "required"; real data never fit to machine precision) and returns
   `required: {required, f, chi2_with, chi2_without_refit, refit_converged}`
-  with the same F ≥ 10 rule. `applyAutoFitResult` refuses a supported-but-
+  with the same F ≥ 10 rule (a refit that did not converge gives NO verdict
+  since unit F2 — `required: null, refit_converged: false` — and Auto-Fit
+  refuses that anchor too: a refit stopped early had read "required", F 992,
+  for a redundant anchor). `applyAutoFitResult` refuses a supported-but-
   not-required anchor exactly like an unsupported one, before any
   charge-correction input is touched ("refitting the other components
   without it fits the data as well"); the anchor id is captured with the
diff --git a/fitting.py b/fitting.py
index 03a6690..63785a8 100644
--- a/fitting.py
+++ b/fitting.py
@@ -1128,6 +1128,50 @@ def _global_or_local_candidate(model, params, requested, y_sub, x, weights, kws)
 # options.fit_method straight to run_fit, and lmfit also understands e.g.
 # "ampgo", "dual_annealing" and "BasinHopping", which would run with
 # numpy's global generator, unseeded.
+# ── basinhopping: verified by refinement (unit F2, 2026-09-26) ─────────────
+# lmfit 1.3 sets MinimizerResult.success = True before minimising and its
+# basinhopping never reads scipy's result, so a basinhopping fit always
+# "converged" (sweep H2). scipy's own flag is no better a verdict: on 23 of 24
+# sampled committed targets it reports the lowest local minimisation as failed
+# (BFGS "Desired error not necessarily achieved due to precision loss") while
+# the point equals Trust-Region's minimum (median relative chi2r difference
+# 1e-9). Owner decision 2026-09-26: the DE pattern, in full. Basinhopping
+# searches; an UNCONDITIONAL least_squares refinement from its point under the
+# request's bounds decides — a refinement that converged IS the candidate (no
+# chi-square comparison with the search, no tolerance: the DE unit's lesson);
+# then that candidate competes with a least_squares fit from the same start
+# (verified beats unverified, then the lower chi-square), so basinhopping is
+# never worse than the default method from the same start.
+def _basinhopping_candidate(model, params, requested, y_sub, x, weights, kws):
+    nan_policy = kws.get("nan_policy", "omit")
+    start = params.copy()
+    for name, (lo, hi) in requested.items():
+        start[name].set(min=lo, max=hi)
+    found = model.fit(y_sub, start.copy(), x=x, weights=weights, **kws)
+    candidate = None
+    try:   # from wherever the search stopped, even an evaluation-budget abort (as DE)
+        refined = model.fit(y_sub, found.params.copy(), x=x, weights=weights,
+                            method="least_squares", nan_policy=nan_policy)
+        if refined.success:
+            candidate = refined
+    except Exception:
+        log.debug("basin-hopping refinement raised", exc_info=True)
+    if candidate is None:
+        # the search's point could not be verified: it is not a converged fit
+        found.success = False
+        found.message = ("basin-hopping: the local refinement from the point it found did not converge, "
+                         "so the result is not a verified fit")
+        candidate = found
+    try:
+        local = model.fit(y_sub, start.copy(), x=x, weights=weights, method="least_squares", nan_policy=nan_policy)
+    except Exception:
+        log.debug("local candidate from the start raised", exc_info=True)
+        return candidate
+    if local.success and (not candidate.success or local.chisqr < candidate.chisqr):
+        return local
+    return candidate
+
+
 _FIT_METHODS = ("leastsq", "least_squares", "nelder", "differential_evolution", "basinhopping")
 _STOCHASTIC_METHODS = ("differential_evolution", "basinhopping")
 
@@ -1407,6 +1451,17 @@ def _component_required(fit_reduced, params_full, removed_prefixes, y_sub, weigh
             start[name].set(expr=par.expr)
     refit = fit_reduced(start)
     chi2_without = float(refit.chisqr) if refit.chisqr is not None else float("inf")
+    if not refit.success or getattr(refit, "box_unverified", False):
+        # F2 (2026-09-26): a refit that did not converge establishes nothing
+        # (nor does a differential-evolution candidate whose search box no
+        # refinement verified — the main fit's acceptance rule rejects it too;
+        # Codex round 1)
+        # either way — its chi-square is wherever the optimiser stopped (a
+        # redundant anchor read "required", F 992, from a refit stopped early;
+        # F 1.17 once it completed). No verdict; the caller decides.
+        return {"required": None, "f": None, "chi2_with": float(chi2_with), "chi2_without_refit": chi2_without,
+                "refit_converged": False, "reason": "refit_not_converged",
+                "message": str(getattr(refit, "message", "") or "")[:200]}
     delta = chi2_without - chi2_with
     p = max(1, int(n_free_comp))
     dof = max(1, len(y_sub) - int(n_free_total))
@@ -1648,6 +1703,22 @@ def run_fit(
     if isinstance(n_starts, bool) or not isinstance(n_starts, (int, np.integer)) or not 0 <= n_starts <= MAX_N_STARTS:
         raise ValueError(f"n_starts must be an integer between 0 and {MAX_N_STARTS}")
 
+    # ── Determinacy (unit F2, 2026-09-26) ─────────────────────────────────────
+    # "Nothing is a fit unless it converged and is determined." With at least
+    # as many free parameters as data points the model can pass through every
+    # point: lmfit reports redchi = chi2 / max(1, nfree) as if it were a fit,
+    # and the support / required F tests clamp their dof to 1, so such a model
+    # read as a near-perfect, fully supported fit (sweep M2: 6 points, 2 GL
+    # components, chi2r 2.8e-6, both "supported"). A count, not a threshold:
+    # zero or negative degrees of freedom is refused outright.
+    n_free_request = sum(1 for par in all_params.values() if par.vary and not par.expr)
+    n_data_request = int(np.count_nonzero(np.isfinite(y_sub)))
+    if n_free_request >= n_data_request:
+        raise ValueError(
+            f"The model is not determined by these data: {n_free_request} free parameters for "
+            f"{n_data_request} data points leaves no degrees of freedom. Widen the fitted range, "
+            f"remove components or lock parameters.")
+
     # ── Fit ───────────────────────────────────────────────────────────────────
     kws = {"method": "leastsq", "nan_policy": "omit"}
     if fit_kws:
@@ -1676,6 +1747,9 @@ def run_fit(
         if kws.get("method") == "differential_evolution":
             bounds = {name: requested_bounds.get(name, (par.min, par.max)) for name, par in params.items()}
             return _global_or_local_candidate(model, params, bounds, y_sub, x, weights, seeded(kws))
+        if kws.get("method") == "basinhopping":
+            bounds = {name: requested_bounds.get(name, (par.min, par.max)) for name, par in params.items()}
+            return _basinhopping_candidate(model, params, bounds, y_sub, x, weights, seeded(kws))
         return model.fit(y_sub, params, x=x, weights=weights, **seeded(kws))
 
     def fit_once(params):
@@ -1707,7 +1781,13 @@ def run_fit(
                       f"{par.stderr:.6f}" if par.stderr is not None else 'None', delta)
 
     # ── Perturb and refit to escape local minima ─────────────────────────
-    if n_perturb > 0 and result.success:
+    # Not for basinhopping (unit F2, 2026-09-26, owner): it is already a global
+    # search, so perturbed restarts add nothing — the reason the scattered-
+    # starts check excludes it — and with the page's n_perturb 3 they
+    # quadrupled its time past the server's 300 s timeout on 14 of 16 sampled
+    # multi-component targets (median 386 s, max 1066 s; without them median
+    # 96 s, max 256 s, and chi2r identical to 1e-8 on all 16).
+    if n_perturb > 0 and result.success and kws.get("method") != "basinhopping":
         best_result = result
         best_redchi = result.redchi if result.redchi is not None else float('inf')
         rng = perturb_rng
diff --git a/templates/index.html b/templates/index.html
index fedb356..bb740ac 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -7306,6 +7306,14 @@ function applyAutoFitResult(json, graphiteRaw, roi) {
     notify('Auto-fit: the Graphite component is not required by the data — refitting the other components without it fits the data as well' + (req.f != null ? ' (F = ' + Number(req.f).toFixed(1) + ', threshold 10)' : '') + '. No charge correction was derived from it and the fit was not applied. The model gives the other components enough freedom to absorb the graphite line; lock or narrow them and try again.', 'red', true);
     return false;
   }
+  // F2 (2026-09-26): the refit without the anchor did not converge, so the
+  // server could not establish that the anchor is required. The anchor would
+  // set the energy reference of the whole spectrum: refused, like a
+  // redundant one (a check that did not RUN at all still never blocks).
+  if (req && req.ran === true && req.refit_converged === false) {
+    notify('Auto-fit: it could not be established that the data require the Graphite component — refitting the other components without it did not converge. No charge correction was derived from it and the fit was not applied. Try Run Fit, or narrow the ROI, and run Auto-Fit again.', 'red', true);
+    return false;
+  }
   if (!_autoFitGraphiteIsSupported(gPeak, json)) {
     notify('Auto-fit: the data do not support the Graphite component (removing it does not worsen the fit), so no charge correction was derived from it and the fit was not applied.', 'red', true);
     return false;
@@ -7397,6 +7405,46 @@ function applyAutoFitResult(json, graphiteRaw, roi) {
 }
 
 // Top-level entry point. Wired to the Actions menu item.
+// Read a 2xx /api/fit reply (unit F2, 2026-09-26). A failure to READ the body
+// is a transport failure (the caller may fall back to the local engine); a
+// body that was read but is not JSON is the SERVER's reply, so it is a failed
+// fit with a message — never a reason to switch engines. The case seen: an
+// uncertainty that could not be computed, serialised as NaN (Flask writes
+// NaN / Infinity tokens, which JSON.parse rejects).
+async function _readFitReply(resp) {
+  const text = await resp.text();                 // rejects only on transport
+  try { return JSON.parse(text); } catch (_) {
+    // A NaN / Infinity TOKEN, never the word inside a JSON string (Codex
+    // round 1) — one linear pass that tracks string and escape state to the
+    // end of the body, so a string cut off by a truncated body stays a string
+    // and no body, however malformed, costs more than one scan (round 2: a
+    // regex that blanked strings was quadratic on an unterminated escaped
+    // string, 10 s for 128 KB on the page's thread).
+    const nonFinite = (function (t) {
+      const bound = ch => ch === undefined || ch === ' ' || ch === '\n' || ch === '\r' || ch === '\t' ||
+        ch === ',' || ch === ':' || ch === '[' || ch === ']' || ch === '\x7b' || ch === '\x7d';   // \x7b \x7d = braces
+      let inStr = false, esc = false;
+      for (let i = 0; i < t.length; i++) {
+        const ch = t[i];
+        if (inStr) {
+          if (esc) esc = false; else if (ch === '\\') esc = true; else if (ch === '"') inStr = false;
+          continue;
+        }
+        if (ch === '"') { inStr = true; continue; }
+        if (ch === 'N' && t.startsWith('NaN', i) && bound(t[i - 1]) && bound(t[i + 3])) return true;
+        if (ch === 'I' && t.startsWith('Infinity', i) && (bound(t[i - 1]) || (t[i - 1] === '-' && bound(t[i - 2]))) && bound(t[i + 8])) return true;   // a sign only after a boundary (round 3)
+      }
+      return false;
+    })(text);
+    const err = new Error(nonFinite
+      ? 'The server\'s reply contains a non-finite number (NaN or Infinity), usually an uncertainty that could not be computed because these data do not determine the model. The fit is treated as failed.'
+      : 'The server\'s reply could not be read. The fit is treated as failed.');
+    err.serverError = true;
+    err.unreadableReply = true;
+    throw err;
+  }
+}
+
 async function runAutoFitC1sGraphite() {
   // Pre-conditions
   if (!state.rawBE || !state.rawBE.length) { notify('Load a spectrum first.', 'amber'); return; }
@@ -7528,7 +7576,17 @@ async function runAutoFitC1sGraphite() {
       signal: ctrl.signal,
     });
     clearTimeout(timer);
-    const json = await resp.json();
+    // F2: a non-2xx reply is a failed REQUEST with its status in the message,
+    // as Run Fit has done since A0 (a Cloudflare 524 or a gunicorn 500 used to
+    // reach the parser and read as "the server's reply could not be read")
+    if (resp.ok === false) {
+      let msg = null;
+      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
+      const err = new Error(msg || ('Fit request failed (HTTP ' + resp.status + ').'));
+      err.httpStatus = resp.status;
+      throw err;
+    }
+    const json = await _readFitReply(resp);   // F2: an unreadable reply is a failed fit with its own message
     if (json.error) throw new Error(json.error);
     if (json.success !== true) throw new Error(json.message || 'fit did not converge');
     if (!_ownerActive(fittingTab)) {
@@ -7565,6 +7623,8 @@ async function runAutoFitC1sGraphite() {
     let msg;
     if (e && (e.name === 'AbortError' || (e.message && e.message.toLowerCase().includes('aborted')))) {
       msg = 'Auto-fit exceeded the 2-minute timeout.';
+    } else if (e && (e.unreadableReply || e.httpStatus)) {
+      msg = 'Auto-fit failed: ' + e.message;
     } else if (e && e.message) {
       msg = 'Fit failed to converge or produced an unphysical graphite position.';
       console.warn('Auto-fit error:', e);
@@ -7976,8 +8036,9 @@ async function runFit(opts = {}) {
     // and leaves the model untouched (unit A0: nothing is shown as a fit
     // result unless it converged; an HTTP 400 is not a reason to silently
     // switch engines).
-    // Only a genuine transport failure (network rejection, abort, unparsable
-    // 2xx body) is marked for fallback; server errors carry `serverError`.
+    // Only a genuine transport failure (network rejection, abort, a body that
+    // could not be read) is marked for fallback; server errors — including a
+    // 2xx body that was read but is not JSON (F2) — carry `serverError`.
     const _asTransport = (e) => {
       if (e && !e.serverError && (e instanceof TypeError || e.name === 'AbortError' || e instanceof SyntaxError)) e.transportFailure = true;
       throw e;
@@ -8009,7 +8070,9 @@ async function runFit(opts = {}) {
       err.serverError = true;
       throw err;
     }
-    try { json = await resp.json(); } catch (e) { _asTransport(e); }
+    // F2: reading the body can fail in transport; a body that was read but is
+    // not JSON is the server's reply — a failed fit, not a fallback
+    try { json = await _readFitReply(resp); } catch (e) { _asTransport(e); }
     if (json.error) {
       const err = new Error(json.error);
       err.serverError = true;
@@ -8320,6 +8383,13 @@ function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
     }
   }
   if (!freeParams.every(Number.isFinite)) return fail('a free parameter is not a finite number.');
+  // F2 (2026-09-26): with at least as many free parameters as data points the
+  // model passes through every point and reads as a near-perfect fit (the
+  // dof below is clamped to 1) — refused, as the server refuses it. A count.
+  if (freeParams.length >= be.length) {
+    return fail('the model is not determined by these data: ' + freeParams.length + ' free parameters for ' +
+                be.length + ' data points leaves no degrees of freedom. Widen the fitted range, remove components or lock parameters.');
+  }
 
   // Parameter box. The amplitude floor is 0, the server's, since unit step (b)
   // (owner decision 2026-09-18: zero allowed in both engines; a component at
diff --git a/tests/js/autofit_required.test.js b/tests/js/autofit_required.test.js
index 6f81e18..81f9811 100644
--- a/tests/js/autofit_required.test.js
+++ b/tests/js/autofit_required.test.js
@@ -46,7 +46,7 @@ test('a supported but NOT required anchor is refused before any charge-correctio
   assert.match(e.calls.notify[0][1], /No charge correction was derived/);
 });
 
-test('a required anchor proceeds; a check that did not run (older server, error, non-converged) does not block', () => {
+test('a required anchor proceeds; a check that did not RUN (older server, error, main fit not converged) does not block', () => {
   for (const required of [{ ran: true, required: true, f: 6120 }, null, undefined, { ran: false, reason: 'error', error: 'x' }]) {
     const e = env(peaks());
     assert.throws(() => e.f({ ...real.json, required }, 284.9, {}), x => x === PAST, JSON.stringify(required));
@@ -64,3 +64,22 @@ test('the request asks for the Graphite anchor by id, and the gate precedes the
   assert.ok(gate > 0 && gate < apply.indexOf('_autoFitGraphiteIsSupported(gPeak, json)'));
   for (const m of ["getElementById('cc-method')", "getElementById('cc-obs')", 'updateChargeCorrection()']) assert.ok(apply.indexOf(m) > gate, m);
 });
+
+// F2 (2026-09-26): an unconverged refit establishes nothing — the server sends
+// required: null with refit_converged: false; Auto-Fit refuses rather than let
+// an anchor whose necessity is unknown set the charge reference.
+test('a refit that did not converge: no verdict, and Auto-Fit refuses before any charge-correction input is touched', () => {
+  const e = env(peaks());
+  const ok = e.f({ ...real.json, required: { ran: true, required: null, f: null, chi2_with: 1.2, chi2_without_refit: 3.4,
+                                             refit_converged: false, reason: 'refit_not_converged' } }, 284.9, {});
+  assert.strictEqual(ok, false);
+  assert.strictEqual(e.calls.cc, 0);
+  assert.deepStrictEqual(e.dom, {});
+  assert.strictEqual(e.calls.notify.length, 1);
+  assert.strictEqual(e.calls.notify[0][0], 'red');
+  assert.match(e.calls.notify[0][1], /could not be established that the data require the Graphite component/);
+  // the old server shape (a verdict computed from an unconverged refit) is refused too
+  const old = env(peaks());
+  assert.strictEqual(old.f({ ...real.json, required: { ran: true, required: true, f: 992, refit_converged: false } }, 284.9, {}), false);
+  assert.strictEqual(old.calls.cc, 0);
+});
diff --git a/tests/js/fit_acceptance.test.js b/tests/js/fit_acceptance.test.js
index 44acd50..97734af 100644
--- a/tests/js/fit_acceptance.test.js
+++ b/tests/js/fit_acceptance.test.js
@@ -41,14 +41,14 @@ function makeEnv({ fetchImpl, uploadImpl, specImpl, ownerActive }) {
     peaks: [{ id: 1, name: 'p', shape: 'Gaussian', center: 285, fwhm: 1.2, amplitude: 50, glMix: 50, asymmetry: 0 }] };
   const owner = { id: 7 };
   const calls = { notify: [], local: 0, applied: 0 };
-  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n');
+  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n');
   const factory = new Function('document', 'state', 'fetch', 'uploadToBackend', 'notify', 'pushUndo', '_showFitSpinner', '_hideFitSpinner',
     '_opOwner', '_ownerActive', 'getROIData', 'computeBackground', 'peakToBackendSpec', '_getManualAnchors', 'applyBackendResult',
     '_computeRFactor', '_CHISQ_TOOLTIP', '_updateRFactorUI', '_updateROIDisplay', 'renderPeakList', 'updatePlot', 'renderResults',
     '_autoSnapshot', 'runFitLocal', '_snapshotSuppressed', 'console', '_applyStatDisplay', '_activeTab',
     src + '\nreturn { runFit };');
   const noop = () => {};
-  const { runFit } = factory(document, state, fetchImpl, uploadImpl || (async () => 'sid'), (msg, kind) => calls.notify.push({ msg, kind }),
+  const { runFit } = factory(document, state, withText(fetchImpl), uploadImpl || (async () => 'sid'), (msg, kind) => calls.notify.push({ msg, kind }),
     noop, noop, noop, () => owner, ownerActive || (o => o === owner), () => ({ be: state.rawBE.slice(), inten: state.rawIntensity.slice() }),
     b => b.map(() => 0), specImpl || (p => ({ id: p.id, shape: 'gaussian' })), () => [], () => { calls.applied++; },
     () => 0.1, '', noop, noop, noop, noop, noop, noop,
@@ -57,6 +57,15 @@ function makeEnv({ fetchImpl, uploadImpl, specImpl, ownerActive }) {
 }
 
 const okResponse = body => async () => ({ ok: true, status: 200, json: async () => body });
+// F2: the page reads a 2xx /api/fit body as text and parses it itself
+// (_readFitReply). A mock that only defines json() gets the matching text().
+function withText(fetchImpl) {
+  return async (...a) => {
+    const r = await fetchImpl(...a);
+    if (r && typeof r.text !== 'function' && typeof r.json === 'function') r.text = async () => JSON.stringify(await r.json());
+    return r;
+  };
+}
 
 test('A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown', async () => {
   const env = makeEnv({ fetchImpl: okResponse({ success: false, message: 'Fit did not converge: max evaluations', statistics: { reduced_chi_square: 999 }, individual_peaks: [] }) });
@@ -95,7 +104,7 @@ test('a transport failure whose local fallback does NOT converge shows no "local
   failing.calls.local = 0;
   // rebuild with a failing runFitLocal
   const dom = failing.dom;
-  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n');
+  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n');
   const noop = () => {};
   const owner = { id: 1 };
   const state = failing.state;
@@ -645,3 +654,65 @@ test('a transport failure after the model was edited mid-fit runs NO local fit (
   await same.runFit();
   assert.equal(same.calls.local, 1);
 });
+
+// ── F2 (2026-09-26): a 2xx reply that was read but is not JSON is the SERVER's
+// failed fit, never a transport failure (the local engine used to replace the
+// server's converged result, its verdicts and its starts evidence) ──
+test('a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback', async () => {
+  const body = '{"success": true, "statistics": {"reduced_chi_square": 1.1}, "individual_peaks": [{"id": "1", "params": {"center": {"value": 285, "stderr": NaN}}}]}';
+  const env = makeEnv({ fetchImpl: async () => ({ ok: true, status: 200, text: async () => body }) });
+  const before = JSON.stringify(env.state.peaks);
+  await env.runFit();
+  assert.equal(env.calls.local, 0, 'no local fallback');
+  assert.equal(env.calls.applied, 0, 'nothing applied');
+  assert.equal(JSON.stringify(env.state.peaks), before);
+  assert.equal(env.state.fitResult.marker, 'previous');
+  assert.ok(env.calls.notify.some(n => n.kind === 'red' && /non-finite number \(NaN or Infinity\)/.test(n.msg) && /treated as failed/.test(n.msg)), JSON.stringify(env.calls.notify));
+  assert.match(env.dom['sb-msg'].textContent, /Fit failed/);
+});
+
+test('a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure', async () => {
+  const garbled = makeEnv({ fetchImpl: async () => ({ ok: true, status: 200, text: async () => '<html>proxy error</html>' }) });
+  await garbled.runFit();
+  assert.equal(garbled.calls.local, 0);
+  assert.ok(garbled.calls.notify.some(n => n.kind === 'red' && /reply could not be read/.test(n.msg)), JSON.stringify(garbled.calls.notify));
+  const dropped = makeEnv({ fetchImpl: async () => ({ ok: true, status: 200, text: async () => { throw new TypeError('network error'); } }) });
+  await dropped.runFit();
+  assert.equal(dropped.calls.local, 1, 'the connection dropped while reading: the local fallback, as before');
+});
+
+test('the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)', async () => {
+  const read = new Function(extractFn('_readFitReply') + '\nreturn _readFitReply;')();
+  const reply = t => ({ text: async () => t });
+  await assert.rejects(read(reply('{"success":true,"message":"contains NaN in label"')), e => e.unreadableReply && /could not be read/.test(e.message));
+  await assert.rejects(read(reply('{"a": NaN, "m": "x"}')), e => e.unreadableReply && /non-finite number/.test(e.message));
+  await assert.rejects(read(reply('{"m": "say \\"NaN\\"", "v": [1, -Infinity]}')), e => /non-finite number/.test(e.message));
+  assert.deepStrictEqual(await read(reply('{"m":"NaN in a label"}')), { m: 'NaN in a label' });
+});
+
+test('the token scan is linear and keeps a truncated string a string (Codex round 2)', async () => {
+  const read = new Function(extractFn('_readFitReply') + '\nreturn _readFitReply;')();
+  const reply = t => ({ text: async () => t });
+  // a body cut off INSIDE a string: the word is string content, not a token
+  await assert.rejects(read(reply('{"message":"contains NaN in label')), e => e.unreadableReply && /could not be read/.test(e.message));
+  // the round-2 stress case: an unterminated string of escaped quotes, 128 KB
+  const big = '{"m":"' + '\\"'.repeat(64000);
+  const t0 = Date.now();
+  await assert.rejects(read(reply(big)), e => e.unreadableReply && /could not be read/.test(e.message));
+  assert.ok(Date.now() - t0 < 500, `took ${Date.now() - t0} ms`);
+  // tokens still found in any position, incl. after an escaped quote inside a string
+  await assert.rejects(read(reply('{"a":"x\\"y","b":NaN}')), e => /non-finite number/.test(e.message));
+  await assert.rejects(read(reply('[-Infinity]')), e => /non-finite number/.test(e.message));
+  await assert.rejects(read(reply('{"a":1,"b":Infinity}')), e => /non-finite number/.test(e.message));
+});
+
+test('a minus sign counts only after a boundary: "x-Infinity" is malformed, "-Infinity" a token (Codex round 3)', async () => {
+  const read = new Function(extractFn('_readFitReply') + '\nreturn _readFitReply;')();
+  const reply = t => ({ text: async () => t });
+  for (const bad of ['{"a":x-Infinity}', '{"a":--Infinity}', '{"v":foo-Infinity}']) {
+    await assert.rejects(read(reply(bad)), e => e.unreadableReply && /could not be read/.test(e.message), bad);
+  }
+  for (const tok of ['{"a":-Infinity}', '[1, -Infinity]', '{"a": -Infinity }']) {
+    await assert.rejects(read(reply(tok)), e => /non-finite number/.test(e.message), tok);
+  }
+});
diff --git a/tests/js/local_lm_descent.test.js b/tests/js/local_lm_descent.test.js
index 37c2127..0d52331 100644
--- a/tests/js/local_lm_descent.test.js
+++ b/tests/js/local_lm_descent.test.js
@@ -558,3 +558,26 @@ test('recovery from an amplitude of exactly zero (the new floor is not a trap)',
   assert.ok(Math.abs(env.state.peaks[0].amplitude - 0.1) < 1e-3, `amplitude ${env.state.peaks[0].amplitude}`);
   assertConstrainedStationary(env, be, data, 1e-8, 'from zero');
 });
+
+// F2 (2026-09-26): at least as many free parameters as data points is refused
+// as undetermined (it read as a near-perfect fit: dof clamped to 1).
+test('the local engine refuses a model with no degrees of freedom; one more point and it fits', () => {
+  const mk = n => {
+    const env = makeEnv();
+    const be = Array.from({ length: n }, (_, i) => 284 + 0.5 * i);
+    env.state.peaks = [{ id: 1, name: 'a', shape: 'Gaussian', center: 285, fwhm: 1, amplitude: 10, glMix: 50, asymmetry: 0 },
+                       { id: 2, name: 'b', shape: 'Gaussian', center: 286, fwhm: 1, amplitude: 5, glMix: 50, asymmetry: 0 }];
+    const before = JSON.stringify(env.state.peaks);
+    const data = be.map(x => 10 * env.gaussian(x, 285, 1) + 5 * env.gaussian(x, 286, 1));
+    return { env, out: env.runFitLocal(be, data, new Array(n).fill(0)), before };
+  };
+  for (const n of [5, 6]) {                                   // 6 free parameters: 5 and 6 points leave no dof
+    const { env, out, before } = mk(n);
+    assert.strictEqual(out.success, false, n + ' points');
+    assert.match(out.message, /not determined by these data: 6 free parameters for \d+ data points/);
+    assert.strictEqual(JSON.stringify(env.state.peaks), before, 'peaks untouched');
+    assert.strictEqual(env.state.fitResult, null, 'no result written');
+  }
+  const { out } = mk(40);
+  assert.strictEqual(out.success, true, 'a determined model still fits');
+});
diff --git a/tests/js/stale_statistics.test.js b/tests/js/stale_statistics.test.js
index c594984..3b36b46 100644
--- a/tests/js/stale_statistics.test.js
+++ b/tests/js/stale_statistics.test.js
@@ -376,9 +376,9 @@ test('Auto-Fit discards (and rolls back) a response when the model or context wa
       renderPeakList() {}, _showFitSpinner() {}, _hideFitSpinner() {}, AbortController, setTimeout: () => 1, clearTimeout() {},
       peakToBackendSpec: p => ({ ...p }), _getManualAnchors: () => [],
       uploadToBackend: async () => { if (editDuringUpload) document.getElementById('bg-type').value = 'linear'; return 'sid'; },
-      fetch: async () => ({ json: async () => ({ success: true, statistics: { reduced_chi_square: 1 }, fitted_y: [10, 20, 10], residuals: [0, 0, 0] }) }),
+      fetch: async () => ({ text: async () => JSON.stringify({ success: true, statistics: { reduced_chi_square: 1 }, fitted_y: [10, 20, 10], residuals: [0, 0, 0] }) }),
       applyBackendResult: () => { out.applied++; }, applyAutoFitResult: () => true };
-    const src = constants + '\n' + ['runAutoFitC1sGraphite', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
+    const src = constants + '\n' + ['runAutoFitC1sGraphite', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
     await new Function(...Object.keys(deps), src + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
     return out;
   };
@@ -405,3 +405,55 @@ test('reload never installs an edited-model curve or R under the original key, a
   assert.match(extractFn('_doSaveProject'), /rFactor: t\.fitResult\.rFactor \|\| null/, 'project saves keep the fit\'s own R');
   assert.match(extractFn('_doSaveSpectrum'), /rFactor: state\.fitResult\.rFactor \|\| null/, 'spectrum saves keep it too');
 });
+
+test('F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back', async () => {
+  const constants = lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n');
+  const state = { peaks: [], ccShift: 0, rawBE: [285, 284.5, 284], rawIntensity: [10, 20, 10] };
+  const dom = {};
+  const document = { getElementById: id => (dom[id] ??= { value: ({ 'bg-type': 'none', 'bg-start': '285', 'bg-end': '284', 'bg-endpoint-avg': '3', 'fit-method': 'leastsq' })[id] || '', style: {}, textContent: '', setAttribute() {}, classList: { add() {}, remove() {} } }), querySelector: () => ({}) };
+  const tab = { id: 1 };
+  const out = { restored: false, applied: 0, notes: [] };
+  const deps = { state, document, tabManager: { activeId: 1, _getTab: () => tab, _captureUI: () => ({ bgType: 'none' }), _syncActiveToRecord() {} },
+    notify: (m, k) => out.notes.push([m, k]), _opOwner: () => tab, _ownerActive: () => true, isC1sTab: () => true,
+    _autoFitSnapshot: () => ({}), _autoFitRestore: () => { out.restored = true; }, _showAutoFitConfirmModal: async () => true,
+    getROIData: () => ({ be: state.rawBE, inten: state.rawIntensity }), computeBackground: be => be.map(() => 0),
+    findGraphiteRawBE: () => 284.5, assessLowBERegion: () => ({}), pushUndo() {}, updateChargeCorrection() {},
+    buildAutoFitModel: () => [{ id: 1, name: 'Graphite', shape: 'Gaussian', center: 284.5, fwhm: 1, amplitude: 20 }],
+    renderPeakList() {}, _showFitSpinner() {}, _hideFitSpinner() {}, AbortController, setTimeout: () => 1, clearTimeout() {},
+    peakToBackendSpec: p => ({ ...p }), _getManualAnchors: () => [], uploadToBackend: async () => 'sid',
+    fetch: async () => ({ text: async () => '{"success": true, "statistics": {"reduced_chi_square": NaN}}' }),
+    applyBackendResult: () => { out.applied++; }, applyAutoFitResult: () => true, console: { warn() {} } };
+  const src = constants + '\n' + ['runAutoFitC1sGraphite', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
+  await new Function(...Object.keys(deps), src + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
+  assert.strictEqual(out.applied, 0);
+  assert.strictEqual(out.restored, true);
+  assert.ok(out.notes.some(([m, k]) => k === 'red' && /^Auto-fit failed: .*non-finite number/.test(m)), JSON.stringify(out.notes));
+});
+
+for (const [label, reply, expect] of [
+  ['a Cloudflare 524 (plain-text body)', { ok: false, status: 524, json: async () => { throw new SyntaxError('error code: 524'); }, text: async () => 'error code: 524' }, /^Auto-fit failed: Fit request failed \(HTTP 524\)\.$/],
+  ['a 500 with a JSON error', { ok: false, status: 500, json: async () => ({ error: 'Internal fitting error' }) }, /^Auto-fit failed: Internal fitting error$/],
+]) test(`F2: Auto-Fit on ${label} is a failed request with its status, never "could not be read"`, async () => {
+  const constants = lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n');
+  const state = { peaks: [], ccShift: 0, rawBE: [285, 284.5, 284], rawIntensity: [10, 20, 10] };
+  const dom = {};
+  const document = { getElementById: id => (dom[id] ??= { value: ({ 'bg-type': 'none', 'bg-start': '285', 'bg-end': '284', 'bg-endpoint-avg': '3', 'fit-method': 'leastsq' })[id] || '', style: {}, textContent: '', setAttribute() {}, classList: { add() {}, remove() {} } }), querySelector: () => ({}) };
+  const tab = { id: 1 };
+  const out = { restored: false, applied: 0, notes: [] };
+  const deps = { state, document, tabManager: { activeId: 1, _getTab: () => tab, _captureUI: () => ({ bgType: 'none' }), _syncActiveToRecord() {} },
+    notify: (m, k) => out.notes.push([m, k]), _opOwner: () => tab, _ownerActive: () => true, isC1sTab: () => true,
+    _autoFitSnapshot: () => ({}), _autoFitRestore: () => { out.restored = true; }, _showAutoFitConfirmModal: async () => true,
+    getROIData: () => ({ be: state.rawBE, inten: state.rawIntensity }), computeBackground: be => be.map(() => 0),
+    findGraphiteRawBE: () => 284.5, assessLowBERegion: () => ({}), pushUndo() {}, updateChargeCorrection() {},
+    buildAutoFitModel: () => [{ id: 1, name: 'Graphite', shape: 'Gaussian', center: 284.5, fwhm: 1, amplitude: 20 }],
+    renderPeakList() {}, _showFitSpinner() {}, _hideFitSpinner() {}, AbortController, setTimeout: () => 1, clearTimeout() {},
+    peakToBackendSpec: p => ({ ...p }), _getManualAnchors: () => [], uploadToBackend: async () => 'sid',
+    fetch: async () => reply,
+    applyBackendResult: () => { out.applied++; }, applyAutoFitResult: () => true, console: { warn() {} } };
+  const src = constants + '\n' + ['runAutoFitC1sGraphite', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
+  await new Function(...Object.keys(deps), src + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
+  assert.strictEqual(out.applied, 0);
+  assert.strictEqual(out.restored, true);
+  assert.ok(out.notes.some(([m, k]) => k === 'red' && expect.test(m)), JSON.stringify(out.notes));
+  assert.ok(!out.notes.some(([m]) => /could not be read/.test(m)));
+});
diff --git a/tests/test_basinhopping_outcome.py b/tests/test_basinhopping_outcome.py
new file mode 100644
index 0000000..bfd88e3
--- /dev/null
+++ b/tests/test_basinhopping_outcome.py
@@ -0,0 +1,125 @@
+"""Unit F2 (2026-09-26), sweep H2: basinhopping's convergence.
+
+lmfit 1.3 marks every basinhopping fit successful (it sets success before
+minimising and never reads scipy's result). scipy's own flag is no verdict
+either: on 23 of 24 sampled committed targets it reports BFGS "precision
+loss" at a point equal to Trust-Region's minimum. Owner decision: the
+differential-evolution pattern in full — the search, an unconditional
+least_squares refinement from its point under the request's bounds (the
+refinement's convergence is the verdict), then a competition with a
+least_squares fit from the same start (verified beats unverified, then the
+lower chi-square), so basinhopping is never worse than the default method.
+"""
+
+import numpy as np
+import pytest
+
+import fitting
+
+
+def _gl(x, a, c, w):
+    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)
+
+
+X = np.linspace(280.0, 292.0, 121)
+
+
+def _two_peaks():
+    y = np.round(200 + _gl(X, 5000, 284.8, 1.2) + _gl(X, 1800, 286.4, 1.3), 2)
+    specs = [
+        {"id": "1", "shape": "gaussian", "center": 284.6, "fwhm": 1.0, "amplitude": 4000.0, "amplitude_min": 0},
+        {"id": "2", "shape": "gaussian", "center": 286.6, "fwhm": 1.0, "amplitude": 1500.0, "amplitude_min": 0},
+    ]
+    return y, specs
+
+
+def _spy(monkeypatch, fail_methods=()):
+    calls = []
+    real = fitting.Model.fit
+
+    def spy(self, data, params, **kw):
+        res = real(self, data, params, **kw)
+        calls.append(kw.get("method"))
+        if kw.get("method") in fail_methods:
+            res.success = False
+        return res
+
+    monkeypatch.setattr(fitting.Model, "fit", spy)
+    return calls
+
+
+def test_a_basinhopping_fit_is_the_refined_least_squares_result_and_never_worse_than_the_default():
+    y, specs = _two_peaks()
+    kw = dict(background_method="linear", n_perturb=0)
+    bh = fitting.run_fit(X, y, specs, fit_kws={"method": "basinhopping"}, **kw)
+    tr = fitting.run_fit(X, y, specs, fit_kws={"method": "least_squares"}, **kw)
+    assert bh["success"] is True
+    assert bh["statistics"]["reduced_chi_square"] <= tr["statistics"]["reduced_chi_square"] * (1 + 1e-12)
+    # the returned result carries least_squares uncertainties (the refinement or the competitor)
+    assert all(ip["params"]["center"]["stderr"] is not None for ip in bh["individual_peaks"])
+
+
+def test_the_call_sequence_is_search_refine_compete(monkeypatch):
+    calls = _spy(monkeypatch)
+    y, specs = _two_peaks()
+    fitting.run_fit(X, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "basinhopping"})
+    assert calls == ["basinhopping", "least_squares", "least_squares"]
+
+
+def test_an_unverifiable_search_does_not_converge_when_the_competitor_fails_too(monkeypatch):
+    # every least_squares (the refinement AND the competitor) reports failure:
+    # nothing verified the point, so it is not a converged fit — the old
+    # behaviour returned lmfit's unconditional success here
+    _spy(monkeypatch, fail_methods=("least_squares",))
+    y, specs = _two_peaks()
+    res = fitting.run_fit(X, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "basinhopping"})
+    assert res["success"] is False
+    assert "not a verified fit" in res["message"]
+
+
+def test_a_failed_refinement_is_rescued_by_a_converged_competitor(monkeypatch):
+    real = fitting.Model.fit
+    seen = []
+
+    def spy(self, data, params, **kw):
+        res = real(self, data, params, **kw)
+        seen.append(kw.get("method"))
+        if kw.get("method") == "least_squares" and seen.count("least_squares") == 1:
+            res.success = False                  # the refinement from the search's point
+        return res
+
+    monkeypatch.setattr(fitting.Model, "fit", spy)
+    y, specs = _two_peaks()
+    res = fitting.run_fit(X, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "basinhopping"})
+    assert res["success"] is True, res["message"]
+
+
+def test_the_required_refit_goes_through_the_same_verification(monkeypatch):
+    calls = _spy(monkeypatch)
+    y, specs = _two_peaks()
+    res = fitting.run_fit(X, y, specs, background_method="linear", n_perturb=0, require_component="2",
+                          fit_kws={"method": "basinhopping"})
+    # the main fit and the required refit: two verified candidates
+    assert calls.count("basinhopping") == 2
+    assert calls.count("least_squares") == 4
+    assert res["required"]["ran"] is True and res["required"]["refit_converged"] is True
+
+
+def test_basinhopping_runs_no_perturbed_restarts(monkeypatch):
+    # a global search already; with the page's n_perturb 3 the restarts took it
+    # past the 300 s server timeout on 14 of 16 multi-component targets
+    calls = _spy(monkeypatch)
+    y, specs = _two_peaks()
+    with_restarts_asked = fitting.run_fit(X, y, specs, background_method="linear", n_perturb=3,
+                                          fit_kws={"method": "basinhopping"})
+    assert calls.count("basinhopping") == 1
+    assert with_restarts_asked["success"] is True
+    # the answer is the one the same request without restarts gets
+    without = fitting.run_fit(X, y, specs, background_method="linear", n_perturb=0,
+                              fit_kws={"method": "basinhopping"})
+    assert with_restarts_asked["statistics"]["reduced_chi_square"] == pytest.approx(
+        without["statistics"]["reduced_chi_square"], rel=1e-9)
+    # differential evolution and the local methods still run the restarts they are asked for
+    calls.clear()
+    fitting.run_fit(X, y, specs, background_method="linear", n_perturb=2, fit_kws={"method": "leastsq"})
+    assert calls.count("leastsq") == 3
diff --git a/tests/test_fit_acceptance_holes.py b/tests/test_fit_acceptance_holes.py
new file mode 100644
index 0000000..a06aa04
--- /dev/null
+++ b/tests/test_fit_acceptance_holes.py
@@ -0,0 +1,116 @@
+"""Unit F2 (2026-09-26): holes in the acceptance rule — "nothing is a fit
+unless it converged and is determined".
+
+- A model with at least as many free parameters as data points is refused as
+  undetermined (it read as a near-perfect, fully supported fit: sweep M2).
+- The required-anchor verdict needs a CONVERGED refit (sweep M3): an
+  unconverged refit gives no verdict.
+
+The basinhopping outcome (sweep H2) and the page's handling of a NaN reply
+(sweep M1) are pinned in tests/test_basinhopping_outcome.py and
+tests/js/fit_acceptance.test.js.
+"""
+
+import io
+from types import SimpleNamespace
+
+import numpy as np
+import pytest
+from lmfit import Parameters
+
+import fitting
+from app import create_app
+
+
+def _gl(x, c, a, w):
+    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)
+
+
+def _two_gl_specs():
+    # two GL components, every parameter free: centre, fwhm, amplitude, gl mix = 8
+    return [
+        {"id": "1", "shape": "pseudo_voigt_gl", "center": 284.5, "fwhm": 1.0, "amplitude": 1000.0,
+         "gl_ratio": 0.3, "fix_gl_ratio": False, "amplitude_min": 0},
+        {"id": "2", "shape": "pseudo_voigt_gl", "center": 286.0, "fwhm": 1.0, "amplitude": 400.0,
+         "gl_ratio": 0.3, "fix_gl_ratio": False, "amplitude_min": 0},
+    ]
+
+
+def _data(n):
+    x = np.linspace(283.0, 288.0, n)
+    y = 100.0 + _gl(x, 284.5, 1000.0, 1.0) + _gl(x, 286.0, 400.0, 1.0)
+    return x, y
+
+
+@pytest.mark.parametrize("n", [6, 8])          # the sweep's reproduction (6 < 8) and zero dof (8 = 8)
+def test_no_degrees_of_freedom_is_refused_as_undetermined(n):
+    x, y = _data(n)
+    with pytest.raises(ValueError, match=r"not determined by these data: 8 free parameters for %d data points" % n):
+        fitting.run_fit(x, y, _two_gl_specs(), background_method="none", fit_kws={"method": "least_squares"})
+
+
+def test_one_degree_of_freedom_is_still_a_fit_and_linked_or_locked_parameters_do_not_count():
+    x, y = _data(9)                              # 8 free, 9 points: dof 1 — determined, fitted as before
+    res = fitting.run_fit(x, y, _two_gl_specs(), background_method="none", fit_kws={"method": "least_squares"})
+    assert res["statistics"]["n_free_params"] == 8
+    # locking the mixes leaves 6 free: 7 points are then enough
+    x7, y7 = _data(7)
+    specs = _two_gl_specs()
+    for s in specs:
+        s["fix_gl_ratio"] = True
+    res = fitting.run_fit(x7, y7, specs, background_method="none", fit_kws={"method": "least_squares"})
+    assert res["statistics"]["n_free_params"] == 6
+
+
+@pytest.fixture()
+def client(tmp_path):
+    app = create_app(upload_folder=str(tmp_path))
+    app.config["TESTING"] = True
+    with app.test_client() as c:
+        yield c
+
+
+def test_api_fit_returns_the_refusal_as_a_400_with_its_message(client):
+    x, y = _data(6)
+    csv = "\n".join(f"{a:.4f},{b:.2f}" for a, b in zip(x, y))
+    sid = client.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "tiny.csv")}).get_json()["session_id"]
+    resp = client.post("/api/fit", json={"session_id": sid, "background": {"method": "none"},
+                                         "peaks": _two_gl_specs(), "fit_method": "least_squares"})
+    assert resp.status_code == 400
+    assert "not determined by these data" in resp.get_json()["error"]
+
+
+def test_an_unconverged_refit_gives_no_required_verdict():
+    """The sweep's reproduction: a refit stopped early read required: true
+    (F 992) for an anchor that is redundant (F 1.17 once the refit completes)."""
+    params = Parameters()
+    params.add("p1_amplitude", value=1.0)
+    params.add("p2_amplitude", value=1.0)
+    y_sub = np.ones(50)
+    stopped = SimpleNamespace(success=False, chisqr=992.0, message="max evaluations reached")
+    out = fitting._component_required(lambda p: stopped, params, ["p1_"], y_sub, np.ones(50),
+                                      chi2_with=1.0, n_free_comp=1, n_free_total=2)
+    assert out["required"] is None
+    assert out["f"] is None
+    assert out["refit_converged"] is False
+    assert out["reason"] == "refit_not_converged"
+    assert "max evaluations" in out["message"]
+    # a converged refit still gives its verdict, unchanged
+    done = SimpleNamespace(success=True, chisqr=1.0 + 1.17 / 48, message="ok")
+    out = fitting._component_required(lambda p: done, params, ["p1_"], y_sub, np.ones(50),
+                                      chi2_with=1.0, n_free_comp=1, n_free_total=2)
+    assert out["refit_converged"] is True and out["required"] is False
+    assert out["f"] == pytest.approx(1.17)
+
+
+def test_an_unverified_differential_evolution_refit_gives_no_required_verdict():
+    """Codex round 1: DE can return success=True with box_unverified=True (its
+    boxed search converged, both verifications failed); the main fit's
+    acceptance rule rejects that candidate, so the required verdict must too."""
+    params = Parameters()
+    params.add("p1_amplitude", value=1.0)
+    params.add("p2_amplitude", value=1.0)
+    unverified = SimpleNamespace(success=True, box_unverified=True, chisqr=500.0, message="boxed")
+    out = fitting._component_required(lambda p: unverified, params, ["p1_"], np.ones(50), np.ones(50),
+                                      chi2_with=1.0, n_free_comp=1, n_free_total=2)
+    assert out["required"] is None and out["refit_converged"] is False
diff --git a/tests/test_fit_reproducibility.py b/tests/test_fit_reproducibility.py
index 9ca3a77..31809a2 100644
--- a/tests/test_fit_reproducibility.py
+++ b/tests/test_fit_reproducibility.py
@@ -158,8 +158,12 @@ def _two_peaks():
     return x, y, specs
 
 
-@pytest.mark.parametrize("method,n_perturb", [("differential_evolution", 2), ("basinhopping", 1)])
-def test_stochastic_methods_get_request_derived_seeds_not_the_global_generator(monkeypatch, method, n_perturb):
+# basinhopping runs no perturbed restarts since unit F2 (a global search; the
+# restarts took it past the 300 s timeout): one seeded minimisation per fit.
+# That each further minimisation (the required refit) gets its own population
+# is pinned in tests/test_component_required.py.
+@pytest.mark.parametrize("method,n_perturb,n_min", [("differential_evolution", 2, 3), ("basinhopping", 1, 1)])
+def test_stochastic_methods_get_request_derived_seeds_not_the_global_generator(monkeypatch, method, n_perturb, n_min):
     # lmfit passes seed=None to both, i.e. numpy's GLOBAL generator: another
     # request in the same worker, or a restart, changed the answer.
     records = _spy_on_fits(monkeypatch)
@@ -169,9 +173,9 @@ def test_stochastic_methods_get_request_derived_seeds_not_the_global_generator(m
         records.append([])
         fitting.run_fit(x, y, specs, background_method="linear", n_perturb=n_perturb, fit_kws={"method": method})
     seeds = [[r["seed"] for r in run if r["method"] == method] for run in records]
-    assert len(seeds[0]) == n_perturb + 1
+    assert len(seeds[0]) == n_min
     assert all(isinstance(s, int) for s in seeds[0])
-    assert len(set(seeds[0])) == n_perturb + 1       # each minimisation its own population
+    assert len(set(seeds[0])) == n_min               # each minimisation its own population
     assert seeds[0] == seeds[1]                      # and the same ones on every press
     # the local refinement / local candidate never receives a solver seed
     assert all(r["seed"] is None for run in records for r in run if r["method"] != method)
@@ -314,8 +318,11 @@ def test_a_differently_cased_method_name_is_the_same_seeded_method(monkeypatch):
     records.append([])
     x, y, specs = _two_peaks()
     res = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "BasinHopping"})
-    assert [r["method"] for r in records[0]] == ["basinhopping"]
+    # F2 (2026-09-26): the seeded search, then its refinement and the competing
+    # fit from the start (least_squares: deterministic, carry no seed)
+    assert [r["method"] for r in records[0]] == ["basinhopping", "least_squares", "least_squares"]
     assert isinstance(records[0][0]["seed"], int)
+    assert records[0][1]["seed"] is None and records[0][2]["seed"] is None
     assert res["random_seed"] == fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0,
                                                  fit_kws={"method": "basinhopping"})["random_seed"]
 

exec
/bin/zsh -lc 'git diff main..HEAD -- fitting.py templates/index.html' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-PblWLBvq' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-I9VJsVpx' (errno=Operation not permitted)
diff --git a/fitting.py b/fitting.py
index 03a6690..63785a8 100644
--- a/fitting.py
+++ b/fitting.py
@@ -1128,6 +1128,50 @@ def _global_or_local_candidate(model, params, requested, y_sub, x, weights, kws)
 # options.fit_method straight to run_fit, and lmfit also understands e.g.
 # "ampgo", "dual_annealing" and "BasinHopping", which would run with
 # numpy's global generator, unseeded.
+# ── basinhopping: verified by refinement (unit F2, 2026-09-26) ─────────────
+# lmfit 1.3 sets MinimizerResult.success = True before minimising and its
+# basinhopping never reads scipy's result, so a basinhopping fit always
+# "converged" (sweep H2). scipy's own flag is no better a verdict: on 23 of 24
+# sampled committed targets it reports the lowest local minimisation as failed
+# (BFGS "Desired error not necessarily achieved due to precision loss") while
+# the point equals Trust-Region's minimum (median relative chi2r difference
+# 1e-9). Owner decision 2026-09-26: the DE pattern, in full. Basinhopping
+# searches; an UNCONDITIONAL least_squares refinement from its point under the
+# request's bounds decides — a refinement that converged IS the candidate (no
+# chi-square comparison with the search, no tolerance: the DE unit's lesson);
+# then that candidate competes with a least_squares fit from the same start
+# (verified beats unverified, then the lower chi-square), so basinhopping is
+# never worse than the default method from the same start.
+def _basinhopping_candidate(model, params, requested, y_sub, x, weights, kws):
+    nan_policy = kws.get("nan_policy", "omit")
+    start = params.copy()
+    for name, (lo, hi) in requested.items():
+        start[name].set(min=lo, max=hi)
+    found = model.fit(y_sub, start.copy(), x=x, weights=weights, **kws)
+    candidate = None
+    try:   # from wherever the search stopped, even an evaluation-budget abort (as DE)
+        refined = model.fit(y_sub, found.params.copy(), x=x, weights=weights,
+                            method="least_squares", nan_policy=nan_policy)
+        if refined.success:
+            candidate = refined
+    except Exception:
+        log.debug("basin-hopping refinement raised", exc_info=True)
+    if candidate is None:
+        # the search's point could not be verified: it is not a converged fit
+        found.success = False
+        found.message = ("basin-hopping: the local refinement from the point it found did not converge, "
+                         "so the result is not a verified fit")
+        candidate = found
+    try:
+        local = model.fit(y_sub, start.copy(), x=x, weights=weights, method="least_squares", nan_policy=nan_policy)
+    except Exception:
+        log.debug("local candidate from the start raised", exc_info=True)
+        return candidate
+    if local.success and (not candidate.success or local.chisqr < candidate.chisqr):
+        return local
+    return candidate
+
+
 _FIT_METHODS = ("leastsq", "least_squares", "nelder", "differential_evolution", "basinhopping")
 _STOCHASTIC_METHODS = ("differential_evolution", "basinhopping")
 
@@ -1407,6 +1451,17 @@ def _component_required(fit_reduced, params_full, removed_prefixes, y_sub, weigh
             start[name].set(expr=par.expr)
     refit = fit_reduced(start)
     chi2_without = float(refit.chisqr) if refit.chisqr is not None else float("inf")
+    if not refit.success or getattr(refit, "box_unverified", False):
+        # F2 (2026-09-26): a refit that did not converge establishes nothing
+        # (nor does a differential-evolution candidate whose search box no
+        # refinement verified — the main fit's acceptance rule rejects it too;
+        # Codex round 1)
+        # either way — its chi-square is wherever the optimiser stopped (a
+        # redundant anchor read "required", F 992, from a refit stopped early;
+        # F 1.17 once it completed). No verdict; the caller decides.
+        return {"required": None, "f": None, "chi2_with": float(chi2_with), "chi2_without_refit": chi2_without,
+                "refit_converged": False, "reason": "refit_not_converged",
+                "message": str(getattr(refit, "message", "") or "")[:200]}
     delta = chi2_without - chi2_with
     p = max(1, int(n_free_comp))
     dof = max(1, len(y_sub) - int(n_free_total))
@@ -1648,6 +1703,22 @@ def run_fit(
     if isinstance(n_starts, bool) or not isinstance(n_starts, (int, np.integer)) or not 0 <= n_starts <= MAX_N_STARTS:
         raise ValueError(f"n_starts must be an integer between 0 and {MAX_N_STARTS}")
 
+    # ── Determinacy (unit F2, 2026-09-26) ─────────────────────────────────────
+    # "Nothing is a fit unless it converged and is determined." With at least
+    # as many free parameters as data points the model can pass through every
+    # point: lmfit reports redchi = chi2 / max(1, nfree) as if it were a fit,
+    # and the support / required F tests clamp their dof to 1, so such a model
+    # read as a near-perfect, fully supported fit (sweep M2: 6 points, 2 GL
+    # components, chi2r 2.8e-6, both "supported"). A count, not a threshold:
+    # zero or negative degrees of freedom is refused outright.
+    n_free_request = sum(1 for par in all_params.values() if par.vary and not par.expr)
+    n_data_request = int(np.count_nonzero(np.isfinite(y_sub)))
+    if n_free_request >= n_data_request:
+        raise ValueError(
+            f"The model is not determined by these data: {n_free_request} free parameters for "
+            f"{n_data_request} data points leaves no degrees of freedom. Widen the fitted range, "
+            f"remove components or lock parameters.")
+
     # ── Fit ───────────────────────────────────────────────────────────────────
     kws = {"method": "leastsq", "nan_policy": "omit"}
     if fit_kws:
@@ -1676,6 +1747,9 @@ def run_fit(
         if kws.get("method") == "differential_evolution":
             bounds = {name: requested_bounds.get(name, (par.min, par.max)) for name, par in params.items()}
             return _global_or_local_candidate(model, params, bounds, y_sub, x, weights, seeded(kws))
+        if kws.get("method") == "basinhopping":
+            bounds = {name: requested_bounds.get(name, (par.min, par.max)) for name, par in params.items()}
+            return _basinhopping_candidate(model, params, bounds, y_sub, x, weights, seeded(kws))
         return model.fit(y_sub, params, x=x, weights=weights, **seeded(kws))
 
     def fit_once(params):
@@ -1707,7 +1781,13 @@ def run_fit(
                       f"{par.stderr:.6f}" if par.stderr is not None else 'None', delta)
 
     # ── Perturb and refit to escape local minima ─────────────────────────
-    if n_perturb > 0 and result.success:
+    # Not for basinhopping (unit F2, 2026-09-26, owner): it is already a global
+    # search, so perturbed restarts add nothing — the reason the scattered-
+    # starts check excludes it — and with the page's n_perturb 3 they
+    # quadrupled its time past the server's 300 s timeout on 14 of 16 sampled
+    # multi-component targets (median 386 s, max 1066 s; without them median
+    # 96 s, max 256 s, and chi2r identical to 1e-8 on all 16).
+    if n_perturb > 0 and result.success and kws.get("method") != "basinhopping":
         best_result = result
         best_redchi = result.redchi if result.redchi is not None else float('inf')
         rng = perturb_rng
diff --git a/templates/index.html b/templates/index.html
index fedb356..bb740ac 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -7306,6 +7306,14 @@ function applyAutoFitResult(json, graphiteRaw, roi) {
     notify('Auto-fit: the Graphite component is not required by the data — refitting the other components without it fits the data as well' + (req.f != null ? ' (F = ' + Number(req.f).toFixed(1) + ', threshold 10)' : '') + '. No charge correction was derived from it and the fit was not applied. The model gives the other components enough freedom to absorb the graphite line; lock or narrow them and try again.', 'red', true);
     return false;
   }
+  // F2 (2026-09-26): the refit without the anchor did not converge, so the
+  // server could not establish that the anchor is required. The anchor would
+  // set the energy reference of the whole spectrum: refused, like a
+  // redundant one (a check that did not RUN at all still never blocks).
+  if (req && req.ran === true && req.refit_converged === false) {
+    notify('Auto-fit: it could not be established that the data require the Graphite component — refitting the other components without it did not converge. No charge correction was derived from it and the fit was not applied. Try Run Fit, or narrow the ROI, and run Auto-Fit again.', 'red', true);
+    return false;
+  }
   if (!_autoFitGraphiteIsSupported(gPeak, json)) {
     notify('Auto-fit: the data do not support the Graphite component (removing it does not worsen the fit), so no charge correction was derived from it and the fit was not applied.', 'red', true);
     return false;
@@ -7397,6 +7405,46 @@ function applyAutoFitResult(json, graphiteRaw, roi) {
 }
 
 // Top-level entry point. Wired to the Actions menu item.
+// Read a 2xx /api/fit reply (unit F2, 2026-09-26). A failure to READ the body
+// is a transport failure (the caller may fall back to the local engine); a
+// body that was read but is not JSON is the SERVER's reply, so it is a failed
+// fit with a message — never a reason to switch engines. The case seen: an
+// uncertainty that could not be computed, serialised as NaN (Flask writes
+// NaN / Infinity tokens, which JSON.parse rejects).
+async function _readFitReply(resp) {
+  const text = await resp.text();                 // rejects only on transport
+  try { return JSON.parse(text); } catch (_) {
+    // A NaN / Infinity TOKEN, never the word inside a JSON string (Codex
+    // round 1) — one linear pass that tracks string and escape state to the
+    // end of the body, so a string cut off by a truncated body stays a string
+    // and no body, however malformed, costs more than one scan (round 2: a
+    // regex that blanked strings was quadratic on an unterminated escaped
+    // string, 10 s for 128 KB on the page's thread).
+    const nonFinite = (function (t) {
+      const bound = ch => ch === undefined || ch === ' ' || ch === '\n' || ch === '\r' || ch === '\t' ||
+        ch === ',' || ch === ':' || ch === '[' || ch === ']' || ch === '\x7b' || ch === '\x7d';   // \x7b \x7d = braces
+      let inStr = false, esc = false;
+      for (let i = 0; i < t.length; i++) {
+        const ch = t[i];
+        if (inStr) {
+          if (esc) esc = false; else if (ch === '\\') esc = true; else if (ch === '"') inStr = false;
+          continue;
+        }
+        if (ch === '"') { inStr = true; continue; }
+        if (ch === 'N' && t.startsWith('NaN', i) && bound(t[i - 1]) && bound(t[i + 3])) return true;
+        if (ch === 'I' && t.startsWith('Infinity', i) && (bound(t[i - 1]) || (t[i - 1] === '-' && bound(t[i - 2]))) && bound(t[i + 8])) return true;   // a sign only after a boundary (round 3)
+      }
+      return false;
+    })(text);
+    const err = new Error(nonFinite
+      ? 'The server\'s reply contains a non-finite number (NaN or Infinity), usually an uncertainty that could not be computed because these data do not determine the model. The fit is treated as failed.'
+      : 'The server\'s reply could not be read. The fit is treated as failed.');
+    err.serverError = true;
+    err.unreadableReply = true;
+    throw err;
+  }
+}
+
 async function runAutoFitC1sGraphite() {
   // Pre-conditions
   if (!state.rawBE || !state.rawBE.length) { notify('Load a spectrum first.', 'amber'); return; }
@@ -7528,7 +7576,17 @@ async function runAutoFitC1sGraphite() {
       signal: ctrl.signal,
     });
     clearTimeout(timer);
-    const json = await resp.json();
+    // F2: a non-2xx reply is a failed REQUEST with its status in the message,
+    // as Run Fit has done since A0 (a Cloudflare 524 or a gunicorn 500 used to
+    // reach the parser and read as "the server's reply could not be read")
+    if (resp.ok === false) {
+      let msg = null;
+      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
+      const err = new Error(msg || ('Fit request failed (HTTP ' + resp.status + ').'));
+      err.httpStatus = resp.status;
+      throw err;
+    }
+    const json = await _readFitReply(resp);   // F2: an unreadable reply is a failed fit with its own message
     if (json.error) throw new Error(json.error);
     if (json.success !== true) throw new Error(json.message || 'fit did not converge');
     if (!_ownerActive(fittingTab)) {
@@ -7565,6 +7623,8 @@ async function runAutoFitC1sGraphite() {
     let msg;
     if (e && (e.name === 'AbortError' || (e.message && e.message.toLowerCase().includes('aborted')))) {
       msg = 'Auto-fit exceeded the 2-minute timeout.';
+    } else if (e && (e.unreadableReply || e.httpStatus)) {
+      msg = 'Auto-fit failed: ' + e.message;
     } else if (e && e.message) {
       msg = 'Fit failed to converge or produced an unphysical graphite position.';
       console.warn('Auto-fit error:', e);
@@ -7976,8 +8036,9 @@ async function runFit(opts = {}) {
     // and leaves the model untouched (unit A0: nothing is shown as a fit
     // result unless it converged; an HTTP 400 is not a reason to silently
     // switch engines).
-    // Only a genuine transport failure (network rejection, abort, unparsable
-    // 2xx body) is marked for fallback; server errors carry `serverError`.
+    // Only a genuine transport failure (network rejection, abort, a body that
+    // could not be read) is marked for fallback; server errors — including a
+    // 2xx body that was read but is not JSON (F2) — carry `serverError`.
     const _asTransport = (e) => {
       if (e && !e.serverError && (e instanceof TypeError || e.name === 'AbortError' || e instanceof SyntaxError)) e.transportFailure = true;
       throw e;
@@ -8009,7 +8070,9 @@ async function runFit(opts = {}) {
       err.serverError = true;
       throw err;
     }
-    try { json = await resp.json(); } catch (e) { _asTransport(e); }
+    // F2: reading the body can fail in transport; a body that was read but is
+    // not JSON is the server's reply — a failed fit, not a fallback
+    try { json = await _readFitReply(resp); } catch (e) { _asTransport(e); }
     if (json.error) {
       const err = new Error(json.error);
       err.serverError = true;
@@ -8320,6 +8383,13 @@ function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
     }
   }
   if (!freeParams.every(Number.isFinite)) return fail('a free parameter is not a finite number.');
+  // F2 (2026-09-26): with at least as many free parameters as data points the
+  // model passes through every point and reads as a near-perfect fit (the
+  // dof below is clamped to 1) — refused, as the server refuses it. A count.
+  if (freeParams.length >= be.length) {
+    return fail('the model is not determined by these data: ' + freeParams.length + ' free parameters for ' +
+                be.length + ' data points leaves no degrees of freedom. Widen the fitted range, remove components or lock parameters.');
+  }
 
   // Parameter box. The amplitude floor is 0, the server's, since unit step (b)
   // (owner decision 2026-09-18: zero allowed in both engines; a component at

exec
/bin/zsh -lc "sed -n '1,100p' tests/js/fit_acceptance.test.js; sed -n '630,730p' tests/js/fit_acceptance.test.js; tail -35 docs/autofit/codex/f2_acceptance_holes_r3_verdict_runA.md; tail -25 docs/autofit/codex/f2_acceptance_holes_r3_verdict_runB.md; rg --files -g AGENTS.md -g '*pytest*' -g '*package.json' -g '*conftest*'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
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
  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n');
  const factory = new Function('document', 'state', 'fetch', 'uploadToBackend', 'notify', 'pushUndo', '_showFitSpinner', '_hideFitSpinner',
    '_opOwner', '_ownerActive', 'getROIData', 'computeBackground', 'peakToBackendSpec', '_getManualAnchors', 'applyBackendResult',
    '_computeRFactor', '_CHISQ_TOOLTIP', '_updateRFactorUI', '_updateROIDisplay', 'renderPeakList', 'updatePlot', 'renderResults',
    '_autoSnapshot', 'runFitLocal', '_snapshotSuppressed', 'console', '_applyStatDisplay', '_activeTab',
    src + '\nreturn { runFit };');
  const noop = () => {};
  const { runFit } = factory(document, state, withText(fetchImpl), uploadImpl || (async () => 'sid'), (msg, kind) => calls.notify.push({ msg, kind }),
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
  } });
  await env.runFit();
  assert.strictEqual(env.calls.applied, 0, 'the result is not applied over the edited model');
  assert.strictEqual(env.state.fitResult.marker, 'previous');
  assert.strictEqual(env.state.peaks[0].center, 290, 'the edit itself is kept');
  assert.ok(env.calls.notify.some(n => n.kind === 'amber' && /edited while the fit was running/.test(n.msg)), JSON.stringify(env.calls.notify));
  assert.match(env.dom['sb-msg'].textContent, /discarded/);
});

// ── F1 Codex round 1: the local fallback never fits the press-time arrays over an edited model ──
test('a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)', async () => {
  let envRef = null;
  const env = makeEnv({
    uploadImpl: async () => { envRef.state.peaks[0].center = 286; return 'sid'; },   // the student edits while the upload runs
    fetchImpl: async () => { throw new TypeError('Failed to fetch'); },
  });
  envRef = env;
  await env.runFit();
  assert.equal(env.calls.local, 0, 'no local fit over the edited model');
  assert.equal(env.state.fitResult.marker, 'previous', 'previous result kept');
  assert.match(env.dom['sb-msg'].textContent, /discarded \(model edited\)/);
  assert.ok(env.calls.notify.some(n => n.kind === 'amber' && /edited while the fit was running/.test(n.msg)), JSON.stringify(env.calls.notify));
  // unchanged model: the fallback still runs (the earlier test) — and an equivalent ROI spelling is not an edit
  const same = makeEnv({ fetchImpl: async () => { throw new TypeError('Failed to fetch'); } });
  await same.runFit();
  assert.equal(same.calls.local, 1);
});

// ── F2 (2026-09-26): a 2xx reply that was read but is not JSON is the SERVER's
// failed fit, never a transport failure (the local engine used to replace the
// server's converged result, its verdicts and its starts evidence) ──
test('a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback', async () => {
  const body = '{"success": true, "statistics": {"reduced_chi_square": 1.1}, "individual_peaks": [{"id": "1", "params": {"center": {"value": 285, "stderr": NaN}}}]}';
  const env = makeEnv({ fetchImpl: async () => ({ ok: true, status: 200, text: async () => body }) });
  const before = JSON.stringify(env.state.peaks);
  await env.runFit();
  assert.equal(env.calls.local, 0, 'no local fallback');
  assert.equal(env.calls.applied, 0, 'nothing applied');
  assert.equal(JSON.stringify(env.state.peaks), before);
  assert.equal(env.state.fitResult.marker, 'previous');
  assert.ok(env.calls.notify.some(n => n.kind === 'red' && /non-finite number \(NaN or Infinity\)/.test(n.msg) && /treated as failed/.test(n.msg)), JSON.stringify(env.calls.notify));
  assert.match(env.dom['sb-msg'].textContent, /Fit failed/);
});

test('a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure', async () => {
  const garbled = makeEnv({ fetchImpl: async () => ({ ok: true, status: 200, text: async () => '<html>proxy error</html>' }) });
  await garbled.runFit();
  assert.equal(garbled.calls.local, 0);
  assert.ok(garbled.calls.notify.some(n => n.kind === 'red' && /reply could not be read/.test(n.msg)), JSON.stringify(garbled.calls.notify));
  const dropped = makeEnv({ fetchImpl: async () => ({ ok: true, status: 200, text: async () => { throw new TypeError('network error'); } }) });
  await dropped.runFit();
  assert.equal(dropped.calls.local, 1, 'the connection dropped while reading: the local fallback, as before');
});

test('the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)', async () => {
  const read = new Function(extractFn('_readFitReply') + '\nreturn _readFitReply;')();
  const reply = t => ({ text: async () => t });
  await assert.rejects(read(reply('{"success":true,"message":"contains NaN in label"')), e => e.unreadableReply && /could not be read/.test(e.message));
  await assert.rejects(read(reply('{"a": NaN, "m": "x"}')), e => e.unreadableReply && /non-finite number/.test(e.message));
  await assert.rejects(read(reply('{"m": "say \\"NaN\\"", "v": [1, -Infinity]}')), e => /non-finite number/.test(e.message));
  assert.deepStrictEqual(await read(reply('{"m":"NaN in a label"}')), { m: 'NaN in a label' });
});

test('the token scan is linear and keeps a truncated string a string (Codex round 2)', async () => {
  const read = new Function(extractFn('_readFitReply') + '\nreturn _readFitReply;')();
  const reply = t => ({ text: async () => t });
  // a body cut off INSIDE a string: the word is string content, not a token
  await assert.rejects(read(reply('{"message":"contains NaN in label')), e => e.unreadableReply && /could not be read/.test(e.message));
  // the round-2 stress case: an unterminated string of escaped quotes, 128 KB
  const big = '{"m":"' + '\\"'.repeat(64000);
  const t0 = Date.now();
  await assert.rejects(read(reply(big)), e => e.unreadableReply && /could not be read/.test(e.message));
  assert.ok(Date.now() - t0 < 500, `took ${Date.now() - t0} ms`);
  // tokens still found in any position, incl. after an escaped quote inside a string
  await assert.rejects(read(reply('{"a":"x\\"y","b":NaN}')), e => /non-finite number/.test(e.message));
  await assert.rejects(read(reply('[-Infinity]')), e => /non-finite number/.test(e.message));
  await assert.rejects(read(reply('{"a":1,"b":Infinity}')), e => /non-finite number/.test(e.message));
});

test('a minus sign counts only after a boundary: "x-Infinity" is malformed, "-Infinity" a token (Codex round 3)', async () => {
  const read = new Function(extractFn('_readFitReply') + '\nreturn _readFitReply;')();
  const reply = t => ({ text: async () => t });
  for (const bad of ['{"a":x-Infinity}', '{"a":--Infinity}', '{"v":foo-Infinity}']) {
    await assert.rejects(read(reply(bad)), e => e.unreadableReply && /could not be read/.test(e.message), bad);
  }
  for (const tok of ['{"a":-Infinity}', '[1, -Infinity]', '{"a": -Infinity }']) {
    await assert.rejects(read(reply(tok)), e => /non-finite number/.test(e.message), tok);
  }
});
/bin/zsh -lc 'git status --short; git rev-parse --short HEAD' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-PoXmmJ1T' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-8GSm1xcJ' (errno=Operation not permitted)
?? docs/autofit/codex/f2_acceptance_holes_r3_verdict_runA.md
?? docs/autofit/codex/f2_acceptance_holes_r3_verdict_runB.md
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-F0MI2MkA' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-kCbPGzB3' (errno=Operation not permitted)
0224141

codex
- **MINOR — Missing boundary check before `-Infinity`.** [templates/index.html:7435](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7435): a 200 body such as `{"a":x-Infinity}` or `{"a":--Infinity}` incorrectly reports a non-finite number instead of an unreadable reply. The scanner accepts any preceding minus without checking its preceding boundary. Require `bound(t[i - 2])` for that branch and add regression cases. Reproduced through Run Fit: previous state remains intact, with no local fallback.

No BLOCKER or MAJOR findings.

Both round-2 fixes verified: the 128 KB stress case took approximately **4 ms**, and malformed 10 MB probes stayed below **124 ms**. Escaped backslashes, Unicode escapes, truncated strings, and parsing valid JSON first behaved correctly. Restoring the old scanner in memory failed both new regression assertions independently; its stress case took **9.6 seconds**.

Validation: **102 JavaScript tests and 11 Python tests passed**. One Python-backed JavaScript parity test was sandbox-blocked; the upload-fixture test was excluded, with determinacy HTTP 400 verified separately in memory. No files changed.

**VERDICT: GO**
tokens used
67,308
- **MINOR — Missing boundary check before `-Infinity`.** [templates/index.html:7435](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7435): a 200 body such as `{"a":x-Infinity}` or `{"a":--Infinity}` incorrectly reports a non-finite number instead of an unreadable reply. The scanner accepts any preceding minus without checking its preceding boundary. Require `bound(t[i - 2])` for that branch and add regression cases. Reproduced through Run Fit: previous state remains intact, with no local fallback.

No BLOCKER or MAJOR findings.

Both round-2 fixes verified: the 128 KB stress case took approximately **4 ms**, and malformed 10 MB probes stayed below **124 ms**. Escaped backslashes, Unicode escapes, truncated strings, and parsing valid JSON first behaved correctly. Restoring the old scanner in memory failed both new regression assertions independently; its stress case took **9.6 seconds**.

Validation: **102 JavaScript tests and 11 Python tests passed**. One Python-backed JavaScript parity test was sandbox-blocked; the upload-fixture test was excluded, with determinacy HTTP 400 verified separately in memory. No files changed.

**VERDICT: GO**

codex
The stress probes are fast: 128 KB of escaped quotes rejects in about 5 ms, and the malformed 10 MB cases take 70–117 ms here. Escape parity, Unicode escapes, valid-JSON precedence, and Flask’s `Infinity` serialization behave as intended. All 11 selected Python tests passed.

I confirmed one minor diagnostic defect: `foo-Infinity` is reported as a non-finite number because the scanner doesn’t check the boundary before the minus sign. The reply still fails closed.
 succeeded in 9662ms:
round2-baseline stress duration 9664.8ms <500: false

codex
- **MINOR — Missing boundary check before `-Infinity`.** [templates/index.html:7435](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7435). A completed 200 body of `{"v":foo-Infinity}` reports “non-finite number” instead of “could not be read.” Any preceding minus sign qualifies, without checking the character before it. Require a boundary before the sign; add this regression. Acceptance remains closed, with no local fallback.

No BLOCKER or MAJOR findings.

Validation: **74 JavaScript tests and 11 Python tests passed**; the upload-fixture Python test was excluded under read-only restrictions. Additional probes covered escape parity, Unicode escapes, token boundaries, valid-JSON precedence, and 10 MB bodies. Both round-2 regressions are non-vacuous: the previous implementation misdiagnoses truncation and takes **9.66 seconds** on the stress case; HEAD takes **4 ms**. No files changed.

**VERDICT: GO**
tokens used
50,815
- **MINOR — Missing boundary check before `-Infinity`.** [templates/index.html:7435](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7435). A completed 200 body of `{"v":foo-Infinity}` reports “non-finite number” instead of “could not be read.” Any preceding minus sign qualifies, without checking the character before it. Require a boundary before the sign; add this regression. Acceptance remains closed, with no local fallback.

No BLOCKER or MAJOR findings.

Validation: **74 JavaScript tests and 11 Python tests passed**; the upload-fixture Python test was excluded under read-only restrictions. Additional probes covered escape parity, Unicode escapes, token boundaries, valid-JSON precedence, and 10 MB bodies. Both round-2 regressions are non-vacuous: the previous implementation misdiagnoses truncation and takes **9.66 seconds** on the stress case; HEAD takes **4 ms**. No files changed.

**VERDICT: GO**
tests/conftest.py

codex
HEAD changes one scanner line and adds a six-case regression test. I’ll probe the start-of-body cases the test doesn’t cover, then run the regression against the previous scanner in memory to confirm it detects the defect.

exec
/bin/zsh -lc "cat tests/conftest.py; sed -n '1570,1785p' fitting.py; sed -n '1390,1505p' fitting.py; sed -n '8250,8398p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
"""Make the repo root importable regardless of how pytest is invoked."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
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
    weights = 1.0 / sigma

    # ── Build composite lmfit model ───────────────────────────────────────────
    # Sort so unconstrained (master) peaks come before constrained ones
    ordered = sorted(
        peak_specs,
        key=lambda s: 0 if s.get("constrain_to") is None else 1,
    )

    composite_model: Model | None = None
    all_params = Parameters()

    for spec in ordered:
        shape = spec.get("shape", "pseudo_voigt_gl")
        if shape not in _SHAPE_FUNCS:
            raise ValueError(f"Unknown peak shape '{shape}'. Choices: {AVAILABLE_SHAPES}")
        func = _SHAPE_FUNCS[shape]
        prefix = f"p{spec['id']}_"
        m = Model(func, prefix=prefix)
        p = _make_peak_params(m, spec, prefix, ordered)
        all_params.update(p)
        composite_model = m if composite_model is None else composite_model + m

    if composite_model is None:
        raise RuntimeError("No peaks were built")
    if require_component is not None:
        ids = [str(spec["id"]) for spec in peak_specs]
        if str(require_component) not in ids:
            raise ValueError(f"require_component '{require_component}' is not one of the peaks")
        if len(ids) < 2:
            raise ValueError("require_component needs at least two components")

    # Every random draw below (the perturbed restarts; the populations of the
    # two stochastic methods, which lmfit otherwise takes from numpy's GLOBAL
    # generator) comes from this one seed, so an identical request gives
    # identical DRAWS. (Not an identical Trust-Region result: see CLAUDE.md,
    # "Reproducibility".)
    if caller_seed is not None:
        random_seed = int(caller_seed)
    else:
        random_seed = _request_seed(
            x, y, bg, [spec.get("shape", "pseudo_voigt_gl") for spec in ordered],
            [f"p{spec['id']}_" for spec in ordered], all_params,
            fit_kws=fit_kws, n_perturb=n_perturb)
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
        return model.fit(y_sub, params, x=x, weights=weights, **seeded(kws))

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
# ─────────────────────────────────────────────────────────────────────────────

def run_fit(
    energy: np.ndarray,
    counts: np.ndarray,
    peak_specs: list[dict[str, Any]],
    background_method: str = "shirley",
    bg_start_idx: int | None = None,
    bg_end_idx: int | None = None,
    charge_shift_ev: float = 0.0,
    fit_kws: dict | None = None,
    n_perturb: int = 0,
    manual_bg: list | None = None,
    endpoint_avg: int = 1,
    n_starts: int = 0,
    require_component=None,
  if (!modelLocal && !previewLocal && !stackLocal.length) { el.style.display = 'none'; return; }
  el.style.backgroundImage = 'linear-gradient(rgba(245,158,11,0.14), rgba(245,158,11,0.14))';
  const governing = _governingProvenance();
  el.innerHTML = modelLocal
    ? '&#9888; <strong>' + (_isUnweightedLocal(governing) ? 'Local (unweighted) model' : 'Local model (Poisson-weighted, no uncertainties)') +
      ' &mdash; a starting point, not a reportable result.</strong> ' + _localFitDetail(governing) + ' Run Fit before quantifying, exporting or reporting.'
    : stackLocal.length
      ? '&#9888; <strong>Local fit curves shown for: ' + stackLocal.map(_escHtml).join(', ') + '</strong> &mdash; starting points, not reportable results. Run Fit on those spectra before reporting.'
      : '&#9888; <strong>The history preview overlay is a local fit &mdash; a starting point, not a reportable result.</strong>';
  el.style.display = 'block';
}
function _provenanceOf(tab) {
  if (!tab) return null;
  if (tab.modelProvenance) return JSON.parse(JSON.stringify(tab.modelProvenance));
  const fr = tab.fitResult;
  if (!_isLocalFit(fr)) return null;
  return { objective: fr.objective || null, engine: fr.engine || 'local', status: fr.status || null,
           weighting: fr.weighting || null, chiReduced: fr.chiReduced ?? null,
           reportable: false, caveat: _localFitCaveat(fr), derivedFrom: 'local_fit' };
}
function _localFitCaveat(fr) {
  if (!_isLocalFit(fr)) return '';
  return _isUnweightedLocal(fr) ? _LOCAL_FIT_CAVEAT_UNWEIGHTED : _LOCAL_FIT_CAVEAT;
}
function _fitStatusText(fr) {
  const tag = !_isLocalFit(fr) ? '' : (_isUnweightedLocal(fr) ? ' (starting point)' : ' (local, starting point)');
  return _fitStatLabel(fr) + ' = ' + fr.chiReduced.toFixed(2) + tag;
}
function _applyStatCaption(fr) {
  const cap = document.getElementById('sb-chi-caption');
  if (!cap) return;
  cap.innerHTML = !_isLocalFit(fr) ? '&#967;&#178;&#7523;:'
    : (_isUnweightedLocal(fr) ? 'Residual variance (starting point):' : '&#967;&#178;&#7523; (local, starting point):');
}
// The statistic is displayed as ONE unit — header text + tooltip, status-bar
// caption + value — from the same fit result, or all cleared. Refreshing
// any one of them alone can pair a local value with a chi-square caption
// (Codex round 9).
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
  const paramMap = [];
  for (const p of work) {
    if (!p.linked) {
      if (!p.fixCenter)    { freeParams.push(p.center);    paramMap.push({id: p.id, param: 'center'}); }
      if (!p.fixFwhm && p.shape !== 'DSG_LA') { freeParams.push(p.fwhm); paramMap.push({id: p.id, param: 'fwhm'}); }
      if (!p.fixAmplitude) { freeParams.push(p.amplitude); paramMap.push({id: p.id, param: 'amplitude'}); }
      if ((p.shape === 'GL' || p.shape === 'asym-GL') && !p.fixGlMix) {
        freeParams.push(p.glMix); paramMap.push({id: p.id, param: 'glMix'});
      }
      if (p.shape === 'asym-GL' && !p.fixAsymmetry) {
        freeParams.push(p.asymmetry); paramMap.push({id: p.id, param: 'asymmetry'});
      }
      if (p.shape === 'DS' && !p.fixDsAlpha) {
        freeParams.push(p.dsAlpha); paramMap.push({id: p.id, param: 'dsAlpha'});
      }
      if (p.shape === 'DS' && !p.fixDsGamma) {
        freeParams.push(p.dsGamma); paramMap.push({id: p.id, param: 'dsGamma'});
      }
      if (p.shape === 'DSG_LA') {
        if (!p.fixLaAlpha) { freeParams.push(Number.isFinite(p.laAlpha) ? p.laAlpha : 0.10); paramMap.push({id: p.id, param: 'laAlpha'}); }
        if (!p.fixLaBeta)  { freeParams.push(Number.isFinite(p.laBeta)  ? p.laBeta  : 0.3);  paramMap.push({id: p.id, param: 'laBeta'}); }
        if (!p.fixLaM)     { freeParams.push(Number.isFinite(p.laM)     ? p.laM     : 0.4);  paramMap.push({id: p.id, param: 'laM'}); }
      }
      if (p.shape === 'LACX') {
        if (!p.fixCaAlpha) { freeParams.push(Number.isFinite(p.caAlpha) ? p.caAlpha : 1.0); paramMap.push({id: p.id, param: 'caAlpha'}); }
        if (!p.fixCaBeta)  { freeParams.push(Number.isFinite(p.caBeta)  ? p.caBeta  : 1.0); paramMap.push({id: p.id, param: 'caBeta'}); }
        // caM is HELD at its value — exactly, not rounded, not a degree of
        // freedom. LA's curve jumps where its kernel half-width changes
        // (m = 6k/7), and a smooth local optimiser cannot fit a discontinuous
        // parameter: freeing it (caM unit, 2026-09-25) stalled fits at the
        // jumps and a derivative confined to one piece failed next to the
        // no-convolution threshold (Codex rounds 1–2). The server fits m;
        // Batch Fit carries the value it is given.
      }
    }
  }
  if (!freeParams.every(Number.isFinite)) return fail('a free parameter is not a finite number.');
  // F2 (2026-09-26): with at least as many free parameters as data points the
  // model passes through every point and reads as a near-perfect fit (the
  // dof below is clamped to 1) — refused, as the server refuses it. A count.
  if (freeParams.length >= be.length) {
    return fail('the model is not determined by these data: ' + freeParams.length + ' free parameters for ' +
                be.length + ' data points leaves no degrees of freedom. Widen the fitted range, remove components or lock parameters.');
  }

  // Parameter box. The amplitude floor is 0, the server's, since unit step (b)
  // (owner decision 2026-09-18: zero allowed in both engines; a component at
  // its floor is an explicit outcome). The active-set step holds a parameter
  // pushed into the wall, and paramScale is floored at 1, so a zero amplitude
  // is a valid, stationary point rather than a division by zero.

exec
/bin/zsh -lc 'node --test tests/js/fit_acceptance.test.js tests/js/autofit_required.test.js tests/js/local_lm_descent.test.js tests/js/stale_statistics.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
exec
/bin/zsh -lc "git diff main..HEAD -- CLAUDE.md tests/js/autofit_required.test.js tests/js/local_lm_descent.test.js; git diff HEAD~1..HEAD -- templates/index.html tests/js/fit_acceptance.test.js; rg -n 'required|box_unverified|aborted' fitting.py | tail -45" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-bxWBmqwJ' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-z5G53Tsi' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index 610c751..67207b4 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -196,6 +196,17 @@ must read each field exactly the way its consumer reads it — integers as
 integers, energies through `parseFloat` — never a generic conversion
 (`_fitKeyCanon`). (Owner, 2026-09-26.)
 
+### Timing claims are measured through the public URL
+
+A request from a student reaches the server through Cloudflare, whose edge
+ends a proxied request at ~100 s (HTTP 524; probes through
+xps.fortierlab.org on 2026-09-26: 88 s passed, 125 s gave 524) — well short
+of gunicorn's `--timeout 300`. "300 s covers it" was written for the DS+G
+Run Fit in 2026-09-22 and was true on the i9 and false through the public
+URL. A claim that a request fits inside a limit is measured through
+xps.fortierlab.org, not on 127.0.0.1. (Owner, 2026-09-27;
+`docs/findings/2026-09-26-public-request-ceiling.md`.)
+
 ---
 
 ## Lineshape Physics — Critical Rules
@@ -358,6 +369,34 @@ exhaust DE's evaluation budget in every search and are rescued by the
 refinement). It is not a gold standard: on one 3-component B 1s target it
 returned χ²ᵣ 1.92 where Trust-Region found 1.81.
 
+`basinhopping` follows THE SAME PATTERN since unit F2 (2026-09-26; owner
+decision; plan `docs/superpowers/plans/2026-09-26-f2-acceptance-holes.md`):
+`_basinhopping_candidate` — the search, then an unconditional
+`least_squares` refinement from its point under the request's bounds (the
+refinement's convergence is the verdict, no χ² comparison), then a
+competition with a `least_squares` fit from the same start (verified beats
+unverified, then the lower χ²), for the main fit, every perturbed restart and
+the required refit. Until then basinhopping always reported `success: true`
+(lmfit sets it before minimising and never reads scipy's result), and
+scipy's own flag is no verdict either: it marked 23 of 24 sampled committed
+targets failed (BFGS "precision loss") at points equal to Trust-Region's
+minimum (median relative χ²ᵣ difference 1e-9). An unverifiable search is
+`success: false`. Basinhopping runs NO perturbed restarts (a global search:
+with the page's `n_perturb` 3 they took 14 of 16 multi-component targets past
+the 300 s server timeout, median 386 s, for χ²ᵣ identical to 1e-8; without
+them median 96 s, max 256 s). NOTE: the public URL's ceiling is lower —
+Cloudflare returns 524 between 88 s and 125 s — so the largest basinhopping
+models still fail there
+(`docs/findings/2026-09-26-public-request-ceiling.md`, not yet addressed).
+
+**Determinacy (unit F2).** `run_fit` refuses a model with at least as many
+free parameters as data points (`ValueError`, HTTP 400, "not determined by
+these data: N free parameters for M data points"), and so does the local
+engine: lmfit divides by max(1, nfree) and the F tests clamp dof to 1, so such
+a model read as a near-perfect, fully supported fit (6 points, 2 GL
+components: χ²ᵣ 2.8e-6, both "supported"). A count, not a threshold; one
+degree of freedom is fitted as before.
+
 **Reproducibility (2026-09-21).** Every random draw in `run_fit` — the
 `n_perturb` restarts (the page sends 3; ±15 % on every varying parameter)
 and the populations of `differential_evolution` and `basinhopping`, which
@@ -616,7 +655,13 @@ only if it converged. `runFitLocal` works on a copy and commits only on
 success, returning `{success, iterations, chiReduced}`; `runFit`
 treats `success !== true` from `/api/fit` as a failed fit and falls back to
 the local engine only on a transport failure, never on a server-side
-error. A RESULT IS DISCARDED IF THE MODEL WAS EDITED WHILE THE FIT WAS RUNNING
+error. A 2xx body that was READ but is not JSON is the server's reply, not a
+transport failure (unit F2): `_readFitReply` reads the text (a failure there
+is transport) and parses it; a NaN / Infinity token (Flask serialises a σ it
+could not compute that way) or any unparseable body is a failed fit with its
+message, for Run Fit and Auto-Fit alike — until F2 it sent Run Fit to the
+local engine, replacing the server's converged result, verdicts and starts
+evidence with a starting point. A RESULT IS DISCARDED IF THE MODEL WAS EDITED WHILE THE FIT WAS RUNNING
 (2026-09-22; a correctness fix for EVERY Run Fit, shipped with the
 scattered-starts check but independent of it). The peak controls stay
 editable during a fit. `runFit` captures the model-plus-context key
@@ -749,7 +794,10 @@ mean "zero" independently of the data):
   to machine precision F is meaningless and a truly redundant component can
   read "required"; real data never fit to machine precision) and returns
   `required: {required, f, chi2_with, chi2_without_refit, refit_converged}`
-  with the same F ≥ 10 rule. `applyAutoFitResult` refuses a supported-but-
+  with the same F ≥ 10 rule (a refit that did not converge gives NO verdict
+  since unit F2 — `required: null, refit_converged: false` — and Auto-Fit
+  refuses that anchor too: a refit stopped early had read "required", F 992,
+  for a redundant anchor). `applyAutoFitResult` refuses a supported-but-
   not-required anchor exactly like an unsupported one, before any
   charge-correction input is touched ("refitting the other components
   without it fits the data as well"); the anchor id is captured with the
diff --git a/tests/js/autofit_required.test.js b/tests/js/autofit_required.test.js
index 6f81e18..81f9811 100644
--- a/tests/js/autofit_required.test.js
+++ b/tests/js/autofit_required.test.js
@@ -46,7 +46,7 @@ test('a supported but NOT required anchor is refused before any charge-correctio
   assert.match(e.calls.notify[0][1], /No charge correction was derived/);
 });
 
-test('a required anchor proceeds; a check that did not run (older server, error, non-converged) does not block', () => {
+test('a required anchor proceeds; a check that did not RUN (older server, error, main fit not converged) does not block', () => {
   for (const required of [{ ran: true, required: true, f: 6120 }, null, undefined, { ran: false, reason: 'error', error: 'x' }]) {
     const e = env(peaks());
     assert.throws(() => e.f({ ...real.json, required }, 284.9, {}), x => x === PAST, JSON.stringify(required));
@@ -64,3 +64,22 @@ test('the request asks for the Graphite anchor by id, and the gate precedes the
   assert.ok(gate > 0 && gate < apply.indexOf('_autoFitGraphiteIsSupported(gPeak, json)'));
   for (const m of ["getElementById('cc-method')", "getElementById('cc-obs')", 'updateChargeCorrection()']) assert.ok(apply.indexOf(m) > gate, m);
 });
+
+// F2 (2026-09-26): an unconverged refit establishes nothing — the server sends
+// required: null with refit_converged: false; Auto-Fit refuses rather than let
+// an anchor whose necessity is unknown set the charge reference.
+test('a refit that did not converge: no verdict, and Auto-Fit refuses before any charge-correction input is touched', () => {
+  const e = env(peaks());
+  const ok = e.f({ ...real.json, required: { ran: true, required: null, f: null, chi2_with: 1.2, chi2_without_refit: 3.4,
+                                             refit_converged: false, reason: 'refit_not_converged' } }, 284.9, {});
+  assert.strictEqual(ok, false);
+  assert.strictEqual(e.calls.cc, 0);
+  assert.deepStrictEqual(e.dom, {});
+  assert.strictEqual(e.calls.notify.length, 1);
+  assert.strictEqual(e.calls.notify[0][0], 'red');
+  assert.match(e.calls.notify[0][1], /could not be established that the data require the Graphite component/);
+  // the old server shape (a verdict computed from an unconverged refit) is refused too
+  const old = env(peaks());
+  assert.strictEqual(old.f({ ...real.json, required: { ran: true, required: true, f: 992, refit_converged: false } }, 284.9, {}), false);
+  assert.strictEqual(old.calls.cc, 0);
+});
diff --git a/tests/js/local_lm_descent.test.js b/tests/js/local_lm_descent.test.js
index 37c2127..0d52331 100644
--- a/tests/js/local_lm_descent.test.js
+++ b/tests/js/local_lm_descent.test.js
@@ -558,3 +558,26 @@ test('recovery from an amplitude of exactly zero (the new floor is not a trap)',
   assert.ok(Math.abs(env.state.peaks[0].amplitude - 0.1) < 1e-3, `amplitude ${env.state.peaks[0].amplitude}`);
   assertConstrainedStationary(env, be, data, 1e-8, 'from zero');
 });
+
+// F2 (2026-09-26): at least as many free parameters as data points is refused
+// as undetermined (it read as a near-perfect fit: dof clamped to 1).
+test('the local engine refuses a model with no degrees of freedom; one more point and it fits', () => {
+  const mk = n => {
+    const env = makeEnv();
+    const be = Array.from({ length: n }, (_, i) => 284 + 0.5 * i);
+    env.state.peaks = [{ id: 1, name: 'a', shape: 'Gaussian', center: 285, fwhm: 1, amplitude: 10, glMix: 50, asymmetry: 0 },
+                       { id: 2, name: 'b', shape: 'Gaussian', center: 286, fwhm: 1, amplitude: 5, glMix: 50, asymmetry: 0 }];
+    const before = JSON.stringify(env.state.peaks);
+    const data = be.map(x => 10 * env.gaussian(x, 285, 1) + 5 * env.gaussian(x, 286, 1));
+    return { env, out: env.runFitLocal(be, data, new Array(n).fill(0)), before };
+  };
+  for (const n of [5, 6]) {                                   // 6 free parameters: 5 and 6 points leave no dof
+    const { env, out, before } = mk(n);
+    assert.strictEqual(out.success, false, n + ' points');
+    assert.match(out.message, /not determined by these data: 6 free parameters for \d+ data points/);
+    assert.strictEqual(JSON.stringify(env.state.peaks), before, 'peaks untouched');
+    assert.strictEqual(env.state.fitResult, null, 'no result written');
+  }
+  const { out } = mk(40);
+  assert.strictEqual(out.success, true, 'a determined model still fits');
+});
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-gpfcL4zW' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-OFOiNjvk' (errno=Operation not permitted)
diff --git a/templates/index.html b/templates/index.html
index 0f4e530..bb740ac 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -7432,7 +7432,7 @@ async function _readFitReply(resp) {
         }
         if (ch === '"') { inStr = true; continue; }
         if (ch === 'N' && t.startsWith('NaN', i) && bound(t[i - 1]) && bound(t[i + 3])) return true;
-        if (ch === 'I' && t.startsWith('Infinity', i) && (bound(t[i - 1]) || t[i - 1] === '-') && bound(t[i + 8])) return true;
+        if (ch === 'I' && t.startsWith('Infinity', i) && (bound(t[i - 1]) || (t[i - 1] === '-' && bound(t[i - 2]))) && bound(t[i + 8])) return true;   // a sign only after a boundary (round 3)
       }
       return false;
     })(text);
diff --git a/tests/js/fit_acceptance.test.js b/tests/js/fit_acceptance.test.js
index fef5ee5..97734af 100644
--- a/tests/js/fit_acceptance.test.js
+++ b/tests/js/fit_acceptance.test.js
@@ -705,3 +705,14 @@ test('the token scan is linear and keeps a truncated string a string (Codex roun
   await assert.rejects(read(reply('[-Infinity]')), e => /non-finite number/.test(e.message));
   await assert.rejects(read(reply('{"a":1,"b":Infinity}')), e => /non-finite number/.test(e.message));
 });
+
+test('a minus sign counts only after a boundary: "x-Infinity" is malformed, "-Infinity" a token (Codex round 3)', async () => {
+  const read = new Function(extractFn('_readFitReply') + '\nreturn _readFitReply;')();
+  const reply = t => ({ text: async () => t });
+  for (const bad of ['{"a":x-Infinity}', '{"a":--Infinity}', '{"v":foo-Infinity}']) {
+    await assert.rejects(read(reply(bad)), e => e.unreadableReply && /could not be read/.test(e.message), bad);
+  }
+  for (const tok of ['{"a":-Infinity}', '[1, -Infinity]', '{"a": -Infinity }']) {
+    await assert.rejects(read(reply(tok)), e => /non-finite number/.test(e.message), tok);
+  }
+});
1056:    ``box_unverified`` (with the sides we generated, so they are not
1066:    found.box_unverified, found.search_box = bool(generated), generated
1091:        refined.box_unverified, refined.search_box = False, {}
1120:    local.box_unverified, local.search_box = False, {}
1121:    if searched.box_unverified or not searched.success or local.chisqr < searched.chisqr:
1431:# charge-reference anchor: an anchor that is not required must not set the
1433:def _component_required(fit_reduced, params_full, removed_prefixes, y_sub, weights,
1454:    if not refit.success or getattr(refit, "box_unverified", False):
1460:        # redundant anchor read "required", F 992, from a refit stopped early;
1462:        return {"required": None, "f": None, "chi2_with": float(chi2_with), "chi2_without_refit": chi2_without,
1474:    # components) reports "required"; real data never fit to machine precision.
1476:        f, required = None, True                     # the rest could not even be fitted without it
1478:        f, required = 0.0, False
1480:        f, required = None, True
1483:        required = f >= SUPPORT_MIN_F
1484:    return {"required": bool(required), "f": f, "chi2_with": float(chi2_with), "chi2_without_refit": chi2_without,
1534:        raise ValueError("At least one peak specification is required")
1710:    # and the support / required F tests clamp their dof to 1, so such a model
1743:    # scattered starts and the required-component refit go through it too.
1820:                trial_rank = (getattr(trial, "box_unverified", False), trial_redchi)
1821:                best_rank = (getattr(best_result, "box_unverified", False), best_redchi)
1853:    # ── "Is this component required?" (never changes `result`) ─────────────
1854:    required = None
1858:            required = {"ran": False, "reason": "fit_not_converged"}
1877:                    required = {"ran": False, "reason": "nothing_left"}
1881:                    required = {"ran": True, **_component_required(
1885:                log.exception("required-component refit failed")
1886:                required = {"ran": False, "reason": "error", "error": f"{type(exc).__name__}: {exc}"[:200]}
1981:    if getattr(result, "box_unverified", False):
2012:        "required": required,

 exited 1 in 7404ms:
# Subtest: a supported but NOT required anchor is refused before any charge-correction input is touched
ok 1 - a supported but NOT required anchor is refused before any charge-correction input is touched
  ---
  duration_ms: 6.557109
  type: 'test'
  ...
# Subtest: a required anchor proceeds; a check that did not RUN (older server, error, main fit not converged) does not block
ok 2 - a required anchor proceeds; a check that did not RUN (older server, error, main fit not converged) does not block
  ---
  duration_ms: 9.968611
  type: 'test'
  ...
# Subtest: the request asks for the Graphite anchor by id, and the gate precedes the support gate and every cc write
ok 3 - the request asks for the Graphite anchor by id, and the gate precedes the support gate and every cc write
  ---
  duration_ms: 0.99032
  type: 'test'
  ...
# Subtest: a refit that did not converge: no verdict, and Auto-Fit refuses before any charge-correction input is touched
ok 4 - a refit that did not converge: no verdict, and Auto-Fit refuses before any charge-correction input is touched
  ---
  duration_ms: 2.26262
  type: 'test'
  ...
# Subtest: A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
ok 5 - A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
  ---
  duration_ms: 10.162289
  type: 'test'
  ...
# Subtest: a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
ok 6 - a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
  ---
  duration_ms: 7.901822
  type: 'test'
  ...
# Subtest: a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
ok 7 - a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
  ---
  duration_ms: 3.640356
  type: 'test'
  ...
# Subtest: a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
ok 8 - a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
  ---
  duration_ms: 9.678032
  type: 'test'
  ...
# Subtest: a converged backend result is applied (sanity)
ok 9 - a converged backend result is applied (sanity)
  ---
  duration_ms: 3.453216
  type: 'test'
  ...
# Subtest: the engine/objective labels of a fit result survive spectrum and project save/load
ok 10 - the engine/objective labels of a fit result survive spectrum and project save/load
  ---
  duration_ms: 0.876377
  type: 'test'
  ...
# Subtest: an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
ok 11 - an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
  ---
  duration_ms: 3.295139
  type: 'test'
  ...
# Subtest: an HTTP 502 on the upload is a server failure, not a transport failure
ok 12 - an HTTP 502 on the upload is a server failure, not a transport failure
  ---
  duration_ms: 3.051249
  type: 'test'
  ...
# Subtest: uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
ok 13 - uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
  ---
  duration_ms: 1.884575
  type: 'test'
  ...
# Subtest: every consumer that prints the goodness-of-fit statistic routes through the statistic identity
ok 14 - every consumer that prints the goodness-of-fit statistic routes through the statistic identity
  ---
  duration_ms: 0.933446
  type: 'test'
  ...
# Subtest: uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
ok 15 - uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
  ---
  duration_ms: 0.740865
  type: 'test'
  ...
# Subtest: a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
ok 16 - a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
  ---
  duration_ms: 1.566633
  type: 'test'
  ...
# Subtest: starting-point helpers: keyed on the persisted objective, weighted results untouched
ok 17 - starting-point helpers: keyed on the persisted objective, weighted results untouched
  ---
  duration_ms: 3.338302
  type: 'test'
  ...
# Subtest: Quantify shows the starting-point banner for a local result and not for a weighted one
ok 18 - Quantify shows the starting-point banner for a local result and not for a weighted one
  ---
  duration_ms: 5.299542
  type: 'test'
  ...
# Subtest: every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
ok 19 - every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
  ---
  duration_ms: 1.675344
  type: 'test'
  ...
# Subtest: project save derives the designation from the objective for an older local result lacking the new fields
ok 20 - project save derives the designation from the objective for an older local result lacking the new fields
  ---
  duration_ms: 7.798276
  type: 'test'
  ...
# Subtest: stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
ok 21 - stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
  ---
  duration_ms: 1.006575
  type: 'test'
  ...
# Subtest: _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
ok 22 - _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
  ---
  duration_ms: 3.4172
  type: 'test'
  ...
# Subtest: history preview glow is keyed on the dataset flag, not the label text
ok 23 - history preview glow is keyed on the dataset flag, not the label text
  ---
  duration_ms: 0.673517
  type: 'test'
  ...
# Subtest: spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
ok 24 - spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
  ---
  duration_ms: 0.487551
  type: 'test'
  ...
# Subtest: _applyStatDisplay clears header, tooltip, caption and value together on local → none
ok 25 - _applyStatDisplay clears header, tooltip, caption and value together on local → none
  ---
  duration_ms: 3.247228
  type: 'test'
  ...
# Subtest: _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
ok 26 - _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
  ---
  duration_ms: 1.651288
  type: 'test'
  ...
# Subtest: fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
ok 27 - fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
  ---
  duration_ms: 1.445981
  type: 'test'
  ...
# Subtest: undo/redo snapshots carry and restore model provenance
ok 28 - undo/redo snapshots carry and restore model provenance
  ---
  duration_ms: 3.741485
  type: 'test'
  ...
# Subtest: round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
ok 29 - round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
  ---
  duration_ms: 1.198388
  type: 'test'
  ...
# Subtest: _provenanceOf derives a designation from a live local result, and undo snapshots use it
ok 30 - _provenanceOf derives a designation from a live local result, and undo snapshots use it
  ---
  duration_ms: 2.796963
  type: 'test'
  ...
# Subtest: batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
ok 31 - batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
  ---
  duration_ms: 0.371253
  type: 'test'
  ...
# Subtest: the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
ok 32 - the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
  ---
  duration_ms: 2.543609
  type: 'test'
  ...
# Subtest: round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
ok 33 - round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
  ---
  duration_ms: 0.687865
  type: 'test'
  ...
# Subtest: the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
ok 34 - the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
  ---
  duration_ms: 2.740167
  type: 'test'
  ...
# Subtest: the sidebar banner is sticky at the top of the scrolling panel body
ok 35 - the sidebar banner is sticky at the top of the scrolling panel body
  ---
  duration_ms: 0.291881
  type: 'test'
  ...
# Subtest: the sidebar banner shows on a stack tab whose visible entries draw a local source fit
ok 36 - the sidebar banner shows on a stack tab whose visible entries draw a local source fit
  ---
  duration_ms: 2.746343
  type: 'test'
  ...
# Subtest: every stack chart repaint path refreshes the sidebar designation before any early return
ok 37 - every stack chart repaint path refreshes the sidebar designation before any early return
  ---
  duration_ms: 0.420457
  type: 'test'
  ...
# Subtest: closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
ok 38 - closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
  ---
  duration_ms: 0.207211
  type: 'test'
  ...
# Subtest: W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
ok 39 - W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
  ---
  duration_ms: 3.007169
  type: 'test'
  ...
# Subtest: TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
ok 40 - TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
  ---
  duration_ms: 4.263229
  type: 'test'
  ...
# Subtest: adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
ok 41 - adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
  ---
  duration_ms: 4.555551
  type: 'test'
  ...
# Subtest: adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
ok 42 - adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
  ---
  duration_ms: 3.172766
  type: 'test'
  ...
# Subtest: adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
ok 43 - adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
  ---
  duration_ms: 4.535407
  type: 'test'
  ...
# Subtest: adoption: success records the choice, the starts evidence and the key of the model it describes
ok 44 - adoption: success records the choice, the starts evidence and the key of the model it describes
  ---
  duration_ms: 5.85117
  type: 'test'
  ...
# Subtest: an ordinary Run Fit on one unlinked component does not ask for the starts check
ok 45 - an ordinary Run Fit on one unlinked component does not ask for the starts check
  ---
  duration_ms: 4.082708
  type: 'test'
  ...
# Subtest: a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
ok 46 - a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
  ---
  duration_ms: 4.557539
  type: 'test'
  ...
# Subtest: a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
ok 47 - a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
  ---
  duration_ms: 5.982212
  type: 'test'
  ...
# Subtest: a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
ok 48 - a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
  ---
  duration_ms: 3.324997
  type: 'test'
  ...
# Subtest: a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
ok 49 - a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
  ---
  duration_ms: 5.719261
  type: 'test'
  ...
# Subtest: the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)
ok 50 - the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)
  ---
  duration_ms: 0.92207
  type: 'test'
  ...
# Subtest: the token scan is linear and keeps a truncated string a string (Codex round 2)
ok 51 - the token scan is linear and keeps a truncated string a string (Codex round 2)
  ---
  duration_ms: 3.57844
  type: 'test'
  ...
# Subtest: a minus sign counts only after a boundary: "x-Infinity" is malformed, "-Infinity" a token (Codex round 3)
ok 52 - a minus sign counts only after a boundary: "x-Infinity" is malformed, "-Infinity" a token (Codex round 3)
  ---
  duration_ms: 0.808385
  type: 'test'
  ...
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/tests/js/local_lm_server_parity_backend.py", line 12, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/fitting.py", line 33, in <module>
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
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes']
# Subtest: A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
ok 53 - A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
  ---
  duration_ms: 1656.331383
  type: 'test'
  ...
# Subtest: A01 replay: the linked U 4f pair also descends
ok 54 - A01 replay: the linked U 4f pair also descends
  ---
  duration_ms: 319.63712
  type: 'test'
  ...
# Subtest: noiseless Gaussian: amplitude 10 started at 5 is recovered
ok 55 - noiseless Gaussian: amplitude 10 started at 5 is recovered
  ---
  duration_ms: 13.951136
  type: 'test'
  ...
# Subtest: acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
ok 56 - acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
  ---
  duration_ms: 9.92381
  type: 'test'
  ...
# Subtest: a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
ok 57 - a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
  ---
  duration_ms: 13.190985
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
ok 58 - bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
  ---
  duration_ms: 9.411782
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
ok 59 - bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
  ---
  duration_ms: 8.970617
  type: 'test'
  ...
# Subtest: a weak component the data DO hold is no longer forced up to an amplitude of 1
ok 60 - a weak component the data DO hold is no longer forced up to an amplitude of 1
  ---
  duration_ms: 9.243888
  type: 'test'
  ...
# Subtest: derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
ok 61 - derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
  ---
  duration_ms: 44.291284
  type: 'test'
  ...
# Subtest: derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
ok 62 - derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
  ---
  duration_ms: 26.910314
  type: 'test'
  ...
# Subtest: a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
ok 63 - a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
  ---
  duration_ms: 9.00458
  type: 'test'
  ...
# Subtest: linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
ok 64 - linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
  ---
  duration_ms: 15.348567
  type: 'test'
  ...
# Subtest: round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
ok 65 - round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
  ---
  duration_ms: 11.925835
  type: 'test'
  ...
# Subtest: round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
ok 66 - round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
  ---
  duration_ms: 11.498575
  type: 'test'
  ...
# Subtest: round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
ok 67 - round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
  ---
  duration_ms: 13.586138
  type: 'test'
  ...
# Subtest: A01 replay targets converge to constrained stationary points (C1s and U 4f)
ok 68 - A01 replay targets converge to constrained stationary points (C1s and U 4f)
  ---
  duration_ms: 1690.817254
  type: 'test'
  ...
# Subtest: round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
ok 69 - round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
  ---
  duration_ms: 76.211758
  type: 'test'
  ...
# Subtest: round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
ok 70 - round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
  ---
  duration_ms: 25.850504
  type: 'test'
  ...
# Subtest: round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
ok 71 - round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
  ---
  duration_ms: 15.20097
  type: 'test'
  ...
# Subtest: round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
ok 72 - round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
  ---
  duration_ms: 92.185435
  type: 'test'
  ...
# Subtest: round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
ok 73 - round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
  ---
  duration_ms: 1404.616074
  type: 'test'
  ...
# Subtest: round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
ok 74 - round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
  ---
  duration_ms: 24.044791
  type: 'test'
  ...
# Subtest: round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
ok 75 - round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
  ---
  duration_ms: 13.749366
  type: 'test'
  ...
# Subtest: weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
ok 76 - weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
  ---
  duration_ms: 11.22652
  type: 'test'
  ...
# Subtest: server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
not ok 77 - server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
  ---
  duration_ms: 1629.504739
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/tests/js/local_lm_descent.test.js:455:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/tests/js/local_lm_server_parity_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/tests/js/local_lm_server_parity_backend.py", line 12, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/fitting.py", line 33, in <module>
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
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/tests/js/local_lm_descent.test.js:468:31)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom
ok 78 - the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom
  ---
  duration_ms: 22.948638
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
ok 79 - an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
  ---
  duration_ms: 30.751222
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
ok 80 - an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
  ---
  duration_ms: 25.43475
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
ok 81 - round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
  ---
  duration_ms: 11.355901
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
ok 82 - round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
  ---
  duration_ms: 10.937214
  type: 'test'
  ...
# Subtest: recovery from an amplitude of exactly zero (the new floor is not a trap)
ok 83 - recovery from an amplitude of exactly zero (the new floor is not a trap)
  ---
  duration_ms: 11.635865
  type: 'test'
  ...
# Subtest: the local engine refuses a model with no degrees of freedom; one more point and it fits
ok 84 - the local engine refuses a model with no degrees of freedom; one more point and it fits
  ---
  duration_ms: 29.411108
  type: 'test'
  ...
# Subtest: one accessor classifies a result against a key: none / unverified / current / stale
ok 85 - one accessor classifies a result against a key: none / unverified / current / stale
  ---
  duration_ms: 18.190155
  type: 'test'
  ...
# Subtest: the key is the step (b) key: F1 adds no second binding mechanism and no new key field
ok 86 - the key is the step (b) key: F1 adds no second binding mechanism and no new key field
  ---
  duration_ms: 5.337515
  type: 'test'
  ...
# Subtest: Results panel, current: statistic, RMSE, R and sigma are shown
ok 87 - Results panel, current: statistic, RMSE, R and sigma are shown
  ---
  duration_ms: 9.220085
  type: 'test'
  ...
# Subtest: Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
ok 88 - Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
  ---
  duration_ms: 8.363179
  type: 'test'
  ...
# Subtest: Results panel, unverified (older save, no key): values shown with a plain note
ok 89 - Results panel, unverified (older save, no key): values shown with a plain note
  ---
  duration_ms: 7.872211
  type: 'test'
  ...
# Subtest: status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
ok 90 - status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
  ---
  duration_ms: 7.716875
  type: 'test'
  ...
# Subtest: the stored fitted curve is never drawn, saved or stacked as the fit once stale
ok 91 - the stored fitted curve is never drawn, saved or stacked as the fit once stale
  ---
  duration_ms: 3.343008
  type: 'test'
  ...
# Subtest: saves keep the key and say plainly when the statistics are stale or unverified
ok 92 - saves keep the key and say plainly when the statistics are stale or unverified
  ---
  duration_ms: 2.519132
  type: 'test'
  ...
# Subtest: CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
ok 93 - CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
  ---
  duration_ms: 14.879551
  type: 'test'
  ...
# Subtest: XLSX: stale writes a WARNING row instead of the statistic, and no sigma
ok 94 - XLSX: stale writes a WARNING row instead of the statistic, and no sigma
  ---
  duration_ms: 5.043527
  type: 'test'
  ...
# Subtest: TSV: stale says the Model / Residual columns are the current, unfitted model
ok 95 - TSV: stale says the Model / Residual columns are the current, unfitted model
  ---
  duration_ms: 7.922256
  type: 'test'
  ...
# Subtest: the refresh re-renders Results only when its rendered state differs
ok 96 - the refresh re-renders Results only when its rendered state differs
  ---
  duration_ms: 3.375916
  type: 'test'
  ...
# Subtest: an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
ok 97 - an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
  ---
  duration_ms: 3.091467
  type: 'test'
  ...
# Subtest: Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
ok 98 - Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
  ---
  duration_ms: 3.672111
  type: 'test'
  ...
# Subtest: Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
ok 99 - Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
  ---
  duration_ms: 9.960598
  type: 'test'
  ...
# Subtest: closing the last tab clears the Results panel, header and status statistics too
ok 100 - closing the last tab clears the Results panel, header and status statistics too
  ---
  duration_ms: 0.221855
  type: 'test'
  ...
# Subtest: reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
ok 101 - reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
  ---
  duration_ms: 2.402629
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back
ok 102 - F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back
  ---
  duration_ms: 6.843432
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a Cloudflare 524 (plain-text body) is a failed request with its status, never "could not be read"
ok 103 - F2: Auto-Fit on a Cloudflare 524 (plain-text body) is a failed request with its status, never "could not be read"
  ---
  duration_ms: 5.873709
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a 500 with a JSON error is a failed request with its status, never "could not be read"
ok 104 - F2: Auto-Fit on a 500 with a JSON error is a failed request with its status, never "could not be read"
  ---
  duration_ms: 3.705564
  type: 'test'
  ...
1..104
# tests 104
# suites 0
# pass 103
# fail 1
# cancelled 0
# skipped 0
# todo 0
# duration_ms 7451.106433

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"-q\", \"-p\", \"no:cacheprovider\", \"--capture=sys\", \"tests/test_fit_acceptance_holes.py\", \"tests/test_basinhopping_outcome.py\", \"-k\", \"not api_fit_returns\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
exec
/bin/zsh -lc "node --test --test-reporter=spec tests/js/local_lm_descent.test.js 2>&1 | tail -65; sed -n '1433,1488p' fitting.py; sed -n '1845,1890p' fitting.py; sed -n '1955,2002p' fitting.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 7139ms:
✔ round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001 (10.861725ms)
✔ recovery from an amplitude of exactly zero (the new floor is not a trap) (11.718783ms)
✔ the local engine refuses a model with no degrees of freedom; one more point and it fits (29.103768ms)
ℹ tests 32
ℹ suites 0
ℹ pass 31
ℹ fail 1
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 7181.794672

✖ failing tests:

test at tests/js/local_lm_descent.test.js:455:1
✖ server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets) (1637.651138ms)
  Error: Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/tests/js/local_lm_server_parity_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
  Traceback (most recent call last):
    File "/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/tests/js/local_lm_server_parity_backend.py", line 12, in <module>
      import fitting  # noqa: E402
      ^^^^^^^^^^^^^^
    File "/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/fitting.py", line 33, in <module>
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
  FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes']
  
      at genericNodeError (node:internal/errors:983:15)
      at wrappedFn (node:internal/errors:537:14)
      at checkExecSyncError (node:child_process:916:11)
      at execFileSync (node:child_process:952:15)
      at TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/tests/js/local_lm_descent.test.js:468:31)
      at Test.runInAsyncScope (node:async_hooks:214:14)
      at Test.run (node:internal/test_runner/test:1047:25)
      at Test.processPendingSubtests (node:internal/test_runner/test:744:18)
      at Test.postRun (node:internal/test_runner/test:1173:19)
      at Test.run (node:internal/test_runner/test:1101:12) {
    status: 1,
    signal: null,
    output: [ null, '', `Traceback (most recent call last):\n  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/tests/js/local_lm_server_parity_backend.py", line 12, in <module>\n    import fitting  # noqa: E402\n    ^^^^^^^^^^^^^^\n  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/fitting.py", line 33, in <module>\n    from lmfit import Model, Parameters\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>\n    from .confidence import conf_interval, conf_interval2d\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>\n    from .minimizer import MinimizerException\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>\n    from .parameter import Parameter, Parameters\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>\n    from .jsonutils import decode4js, encode4js\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>\n    import dill\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>\n    from .session import (\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>\n    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())\n                               ^^^^^^^^^^^^^^^^^^^^^\n  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir\n    return _os.fsdecode(_gettempdir())\n                        ^^^^^^^^^^^^^\n  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir\n    tempdir = _get_default_tempdir()\n              ^^^^^^^^^^^^^^^^^^^^^^\n  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir\n    raise FileNotFoundError(_errno.ENOENT,\nFileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes']\n` ],
    pid: 33404,
    stdout: '',
    stderr: `Traceback (most recent call last):\n  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/tests/js/local_lm_server_parity_backend.py", line 12, in <module>\n    import fitting  # noqa: E402\n    ^^^^^^^^^^^^^^\n  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/fitting.py", line 33, in <module>\n    from lmfit import Model, Parameters\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>\n    from .confidence import conf_interval, conf_interval2d\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>\n    from .minimizer import MinimizerException\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>\n    from .parameter import Parameter, Parameters\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>\n    from .jsonutils import decode4js, encode4js\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>\n    import dill\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>\n    from .session import (\n  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>\n    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())\n                               ^^^^^^^^^^^^^^^^^^^^^\n  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir\n    return _os.fsdecode(_gettempdir())\n                        ^^^^^^^^^^^^^\n  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir\n    tempdir = _get_default_tempdir()\n              ^^^^^^^^^^^^^^^^^^^^^^\n  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir\n    raise FileNotFoundError(_errno.ENOENT,\nFileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes']\n`
  }
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
    search_box = getattr(result, "search_box", {})
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
    n_free = result.nvarys
    chi_sq = float(result.chisqr) if result.chisqr is not None else None
    red_chi_sq = float(result.redchi) if result.redchi is not None else None

    residuals = (y_sub - fitted_sub).tolist()

    # R‑factor (like in crystallography: sum|obs-calc| / sum|obs|)
    r_factor = (float(np.sum(np.abs(y_sub - fitted_sub)) / np.sum(np.abs(y_sub)))
                if np.sum(np.abs(y_sub)) > 0 else None)

    success, message = result.success, result.message
    if getattr(result, "box_unverified", False):
        # Searched inside limits the request never set, and the refinement
        # that would show they did not matter did not converge to an equal
        # or better solution. The acceptance rule shows this as a failed fit.
        success = False
        message = ("differential_evolution searched inside generated limits for "
                   + ", ".join(sorted(search_box))
                   + " and a local refinement without them did not converge to an equal or better"
                     " solution. Set bounds for those parameters or use another method.")

    return {
        "success": success,
        "message": message,
        "energy": x.tolist(),
        "counts": y.tolist(),
        "fitted_y": fitted_y.tolist(),
        "background_y": bg.tolist(),
        "residuals": residuals,
        "individual_peaks": individual_peaks,
        "statistics": {
            "chi_square": chi_sq,
            "reduced_chi_square": red_chi_sq,

exec
/bin/zsh -lc "node -e '
const fs=require('\\''fs'\\''), cp=require('\\''child_process'\\''), assert=require('\\''assert'\\'');
function extract(h){return h.slice(h.indexOf('\\''async function _readFitReply('\\''),h.indexOf('\\''\\nasync function runAutoFitC1sGraphite('\\''));}
const h=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const current=extract(h), prev=extract(cp.execFileSync('\\''git'\\'',['\\''show'\\'','\\''HEAD~1:templates/index.html'\\''],{encoding:'\\''utf8'\\'',stdio:['\\''ignore'\\'','\\''pipe'\\'','\\''ignore'\\'']}));
const read=new Function(current+'\\'';return _readFitReply'\\'')(), old=new Function(prev+'\\'';return _readFitReply'\\'')();
async function kind(f,s){try {await f({text:async()=>s});return '\\''valid'\\'';}catch(e){assert(e.serverError && e.unreadableReply);return /non-finite number/.test(e.message)?'\\''nf'\\'':'\\''bad'\\'';}}
(async()=>{
let n=0;
const boundaries=['\\'''\\'','\\''['\\'','\\'','\\'','\\'':'\\'','\\''{'\\'','\\'' '\\'','\\''\\t'\\'','\\''\\n'\\'','\\''\\r'\\'','\\'']'\\'','\\''}'\\''];
for(const pre of boundaries) for(const post of boundaries) for(const tok of ['\\''Infinity'\\'','\\''-Infinity'\\'','\\''NaN'\\'']) {assert.equal(await kind(read,pre+tok+post),'\\''nf'\\'',JSON.stringify(pre+tok+post)); n++;}
for(const pre of ['\\''x'\\'','\\''-'\\'','\\''+'\\'','\\''0'\\'','\\''.'\\'','\\''\"x\"'\\'','\\''\\\\'\\'','\\''é'\\'','\\''--'\\'']) for(const post of boundaries) {assert.equal(await kind(read,pre+'\\''-Infinity'\\''+post),'\\''bad'\\'',JSON.stringify(pre+'\\''-Infinity'\\''+post));n++;}
for(const body of ['\\''Infinityx'\\'','\\''-Infinityx'\\'','\\''NaNx'\\'','\\''--Infinity'\\'','\\''+-Infinity'\\'','\\''x-Infinity'\\'','\\''{\"v\":\"-Infinity\"'\\'','\\''{\"v\":\"\\\\\\\"-Infinity\"'\\'']) {assert.equal(await kind(read,body),'\\''bad'\\'',body);n++;}
for(let i=0;i<32;i++){const body='\\''{\"m\":\"'\\''+'\\''\\\\'\\''.repeat(i)+'\\''\",-Infinity'\\'';assert.equal(await kind(read,body),i%2?'\\''bad'\\'':'\\''nf'\\'',body);n++;}
for(const body of ['\\''\"-Infinity\"'\\'','\\''{\"m\":\"NaN Infinity\"}'\\'','\\''{\"x\":1e999}'\\'','\\''[]'\\'','\\''null'\\'']) {assert.equal(await kind(read,body),'\\''valid'\\'',body);n++;}
for(const body of ['\\''{\"a\":x-Infinity}'\\'','\\''{\"a\":--Infinity}'\\'','\\''{\"v\":foo-Infinity}'\\'']){assert.equal(await kind(read,body),'\\''bad'\\'');assert.equal(await kind(old,body),'\\''nf'\\'');}
console.log(n+'\\'' boundary, escape and valid JSON probes passed; all 3 new negative cases fail on round-3 code.'\\'');
const suite=fs.readFileSync('\\''tests/js/fit_acceptance.test.js'\\'','\\''utf8'\\'');
const regression=suite.slice(suite.indexOf(\"test('\\''a minus sign counts only after a boundary\"));
for(const [name,src] of [['\\''HEAD'\\'',current],['\\''HEAD~1'\\'',prev]]){let pending;new Function('\\''test'\\'','\\''assert'\\'','\\''extractFn'\\'',regression)((_,fn)=>pending=fn(),assert,()=>src);try{await pending;console.log(name+'\\'' actual regression PASS'\\'');}catch(e){console.log(name+'\\'' actual regression FAIL: '\\''+e.message);}}
for(const [name,s] of [['\\''escaped'\\'','\\''{\"m\":\"'\\''+'\\''\\\\\"'\\''.repeat(5000000)],['\\''slashes'\\'','\\''{\"m\":\"'\\''+'\\''\\\\'\\''.repeat(10000000)],['\\''quotes'\\'','\\''\"'\\''.repeat(10000000)],['\\''digits'\\'','\\''9'\\''.repeat(10000000)+'\\''x'\\''],['\\''signs'\\'','\\''-'\\''.repeat(10000000)+'\\''Infinity'\\'']]){const t=performance.now();assert.equal(await kind(read,s),'\\''bad'\\'');console.log(name+'\\'': '\\''+(performance.now()-t).toFixed(1)+'\\''ms'\\'');}
})();
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 470ms:
escaped: 111.2ms
slashes: 106.7ms
quotes: 72.3ms
digits: 105.9ms
signs: 76.5ms

exec
/bin/zsh -lc "git diff main..HEAD -- tests/js/fit_acceptance.test.js tests/js/stale_statistics.test.js; sed -n '1510,1572p' fitting.py; sed -n '440,485p' tests/js/local_lm_descent.test.js; sed -n '1,60p' tests/js/local_lm_server_parity_backend.py; git diff --name-only main..HEAD" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-jrSiEdhX' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-uzEQo95r' (errno=Operation not permitted)
diff --git a/tests/js/fit_acceptance.test.js b/tests/js/fit_acceptance.test.js
index 44acd50..97734af 100644
--- a/tests/js/fit_acceptance.test.js
+++ b/tests/js/fit_acceptance.test.js
@@ -41,14 +41,14 @@ function makeEnv({ fetchImpl, uploadImpl, specImpl, ownerActive }) {
     peaks: [{ id: 1, name: 'p', shape: 'Gaussian', center: 285, fwhm: 1.2, amplitude: 50, glMix: 50, asymmetry: 0 }] };
   const owner = { id: 7 };
   const calls = { notify: [], local: 0, applied: 0 };
-  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n');
+  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n');
   const factory = new Function('document', 'state', 'fetch', 'uploadToBackend', 'notify', 'pushUndo', '_showFitSpinner', '_hideFitSpinner',
     '_opOwner', '_ownerActive', 'getROIData', 'computeBackground', 'peakToBackendSpec', '_getManualAnchors', 'applyBackendResult',
     '_computeRFactor', '_CHISQ_TOOLTIP', '_updateRFactorUI', '_updateROIDisplay', 'renderPeakList', 'updatePlot', 'renderResults',
     '_autoSnapshot', 'runFitLocal', '_snapshotSuppressed', 'console', '_applyStatDisplay', '_activeTab',
     src + '\nreturn { runFit };');
   const noop = () => {};
-  const { runFit } = factory(document, state, fetchImpl, uploadImpl || (async () => 'sid'), (msg, kind) => calls.notify.push({ msg, kind }),
+  const { runFit } = factory(document, state, withText(fetchImpl), uploadImpl || (async () => 'sid'), (msg, kind) => calls.notify.push({ msg, kind }),
     noop, noop, noop, () => owner, ownerActive || (o => o === owner), () => ({ be: state.rawBE.slice(), inten: state.rawIntensity.slice() }),
     b => b.map(() => 0), specImpl || (p => ({ id: p.id, shape: 'gaussian' })), () => [], () => { calls.applied++; },
     () => 0.1, '', noop, noop, noop, noop, noop, noop,
@@ -57,6 +57,15 @@ function makeEnv({ fetchImpl, uploadImpl, specImpl, ownerActive }) {
 }
 
 const okResponse = body => async () => ({ ok: true, status: 200, json: async () => body });
+// F2: the page reads a 2xx /api/fit body as text and parses it itself
+// (_readFitReply). A mock that only defines json() gets the matching text().
+function withText(fetchImpl) {
+  return async (...a) => {
+    const r = await fetchImpl(...a);
+    if (r && typeof r.text !== 'function' && typeof r.json === 'function') r.text = async () => JSON.stringify(await r.json());
+    return r;
+  };
+}
 
 test('A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown', async () => {
   const env = makeEnv({ fetchImpl: okResponse({ success: false, message: 'Fit did not converge: max evaluations', statistics: { reduced_chi_square: 999 }, individual_peaks: [] }) });
@@ -95,7 +104,7 @@ test('a transport failure whose local fallback does NOT converge shows no "local
   failing.calls.local = 0;
   // rebuild with a failing runFitLocal
   const dom = failing.dom;
-  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n');
+  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n');
   const noop = () => {};
   const owner = { id: 1 };
   const state = failing.state;
@@ -645,3 +654,65 @@ test('a transport failure after the model was edited mid-fit runs NO local fit (
   await same.runFit();
   assert.equal(same.calls.local, 1);
 });
+
+// ── F2 (2026-09-26): a 2xx reply that was read but is not JSON is the SERVER's
+// failed fit, never a transport failure (the local engine used to replace the
+// server's converged result, its verdicts and its starts evidence) ──
+test('a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback', async () => {
+  const body = '{"success": true, "statistics": {"reduced_chi_square": 1.1}, "individual_peaks": [{"id": "1", "params": {"center": {"value": 285, "stderr": NaN}}}]}';
+  const env = makeEnv({ fetchImpl: async () => ({ ok: true, status: 200, text: async () => body }) });
+  const before = JSON.stringify(env.state.peaks);
+  await env.runFit();
+  assert.equal(env.calls.local, 0, 'no local fallback');
+  assert.equal(env.calls.applied, 0, 'nothing applied');
+  assert.equal(JSON.stringify(env.state.peaks), before);
+  assert.equal(env.state.fitResult.marker, 'previous');
+  assert.ok(env.calls.notify.some(n => n.kind === 'red' && /non-finite number \(NaN or Infinity\)/.test(n.msg) && /treated as failed/.test(n.msg)), JSON.stringify(env.calls.notify));
+  assert.match(env.dom['sb-msg'].textContent, /Fit failed/);
+});
+
+test('a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure', async () => {
+  const garbled = makeEnv({ fetchImpl: async () => ({ ok: true, status: 200, text: async () => '<html>proxy error</html>' }) });
+  await garbled.runFit();
+  assert.equal(garbled.calls.local, 0);
+  assert.ok(garbled.calls.notify.some(n => n.kind === 'red' && /reply could not be read/.test(n.msg)), JSON.stringify(garbled.calls.notify));
+  const dropped = makeEnv({ fetchImpl: async () => ({ ok: true, status: 200, text: async () => { throw new TypeError('network error'); } }) });
+  await dropped.runFit();
+  assert.equal(dropped.calls.local, 1, 'the connection dropped while reading: the local fallback, as before');
+});
+
+test('the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)', async () => {
+  const read = new Function(extractFn('_readFitReply') + '\nreturn _readFitReply;')();
+  const reply = t => ({ text: async () => t });
+  await assert.rejects(read(reply('{"success":true,"message":"contains NaN in label"')), e => e.unreadableReply && /could not be read/.test(e.message));
+  await assert.rejects(read(reply('{"a": NaN, "m": "x"}')), e => e.unreadableReply && /non-finite number/.test(e.message));
+  await assert.rejects(read(reply('{"m": "say \\"NaN\\"", "v": [1, -Infinity]}')), e => /non-finite number/.test(e.message));
+  assert.deepStrictEqual(await read(reply('{"m":"NaN in a label"}')), { m: 'NaN in a label' });
+});
+
+test('the token scan is linear and keeps a truncated string a string (Codex round 2)', async () => {
+  const read = new Function(extractFn('_readFitReply') + '\nreturn _readFitReply;')();
+  const reply = t => ({ text: async () => t });
+  // a body cut off INSIDE a string: the word is string content, not a token
+  await assert.rejects(read(reply('{"message":"contains NaN in label')), e => e.unreadableReply && /could not be read/.test(e.message));
+  // the round-2 stress case: an unterminated string of escaped quotes, 128 KB
+  const big = '{"m":"' + '\\"'.repeat(64000);
+  const t0 = Date.now();
+  await assert.rejects(read(reply(big)), e => e.unreadableReply && /could not be read/.test(e.message));
+  assert.ok(Date.now() - t0 < 500, `took ${Date.now() - t0} ms`);
+  // tokens still found in any position, incl. after an escaped quote inside a string
+  await assert.rejects(read(reply('{"a":"x\\"y","b":NaN}')), e => /non-finite number/.test(e.message));
+  await assert.rejects(read(reply('[-Infinity]')), e => /non-finite number/.test(e.message));
+  await assert.rejects(read(reply('{"a":1,"b":Infinity}')), e => /non-finite number/.test(e.message));
+});
+
+test('a minus sign counts only after a boundary: "x-Infinity" is malformed, "-Infinity" a token (Codex round 3)', async () => {
+  const read = new Function(extractFn('_readFitReply') + '\nreturn _readFitReply;')();
+  const reply = t => ({ text: async () => t });
+  for (const bad of ['{"a":x-Infinity}', '{"a":--Infinity}', '{"v":foo-Infinity}']) {
+    await assert.rejects(read(reply(bad)), e => e.unreadableReply && /could not be read/.test(e.message), bad);
+  }
+  for (const tok of ['{"a":-Infinity}', '[1, -Infinity]', '{"a": -Infinity }']) {
+    await assert.rejects(read(reply(tok)), e => /non-finite number/.test(e.message), tok);
+  }
+});
diff --git a/tests/js/stale_statistics.test.js b/tests/js/stale_statistics.test.js
index c594984..3b36b46 100644
--- a/tests/js/stale_statistics.test.js
+++ b/tests/js/stale_statistics.test.js
@@ -376,9 +376,9 @@ test('Auto-Fit discards (and rolls back) a response when the model or context wa
       renderPeakList() {}, _showFitSpinner() {}, _hideFitSpinner() {}, AbortController, setTimeout: () => 1, clearTimeout() {},
       peakToBackendSpec: p => ({ ...p }), _getManualAnchors: () => [],
       uploadToBackend: async () => { if (editDuringUpload) document.getElementById('bg-type').value = 'linear'; return 'sid'; },
-      fetch: async () => ({ json: async () => ({ success: true, statistics: { reduced_chi_square: 1 }, fitted_y: [10, 20, 10], residuals: [0, 0, 0] }) }),
+      fetch: async () => ({ text: async () => JSON.stringify({ success: true, statistics: { reduced_chi_square: 1 }, fitted_y: [10, 20, 10], residuals: [0, 0, 0] }) }),
       applyBackendResult: () => { out.applied++; }, applyAutoFitResult: () => true };
-    const src = constants + '\n' + ['runAutoFitC1sGraphite', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
+    const src = constants + '\n' + ['runAutoFitC1sGraphite', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
     await new Function(...Object.keys(deps), src + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
     return out;
   };
@@ -405,3 +405,55 @@ test('reload never installs an edited-model curve or R under the original key, a
   assert.match(extractFn('_doSaveProject'), /rFactor: t\.fitResult\.rFactor \|\| null/, 'project saves keep the fit\'s own R');
   assert.match(extractFn('_doSaveSpectrum'), /rFactor: state\.fitResult\.rFactor \|\| null/, 'spectrum saves keep it too');
 });
+
+test('F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back', async () => {
+  const constants = lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n');
+  const state = { peaks: [], ccShift: 0, rawBE: [285, 284.5, 284], rawIntensity: [10, 20, 10] };
+  const dom = {};
+  const document = { getElementById: id => (dom[id] ??= { value: ({ 'bg-type': 'none', 'bg-start': '285', 'bg-end': '284', 'bg-endpoint-avg': '3', 'fit-method': 'leastsq' })[id] || '', style: {}, textContent: '', setAttribute() {}, classList: { add() {}, remove() {} } }), querySelector: () => ({}) };
+  const tab = { id: 1 };
+  const out = { restored: false, applied: 0, notes: [] };
+  const deps = { state, document, tabManager: { activeId: 1, _getTab: () => tab, _captureUI: () => ({ bgType: 'none' }), _syncActiveToRecord() {} },
+    notify: (m, k) => out.notes.push([m, k]), _opOwner: () => tab, _ownerActive: () => true, isC1sTab: () => true,
+    _autoFitSnapshot: () => ({}), _autoFitRestore: () => { out.restored = true; }, _showAutoFitConfirmModal: async () => true,
+    getROIData: () => ({ be: state.rawBE, inten: state.rawIntensity }), computeBackground: be => be.map(() => 0),
+    findGraphiteRawBE: () => 284.5, assessLowBERegion: () => ({}), pushUndo() {}, updateChargeCorrection() {},
+    buildAutoFitModel: () => [{ id: 1, name: 'Graphite', shape: 'Gaussian', center: 284.5, fwhm: 1, amplitude: 20 }],
+    renderPeakList() {}, _showFitSpinner() {}, _hideFitSpinner() {}, AbortController, setTimeout: () => 1, clearTimeout() {},
+    peakToBackendSpec: p => ({ ...p }), _getManualAnchors: () => [], uploadToBackend: async () => 'sid',
+    fetch: async () => ({ text: async () => '{"success": true, "statistics": {"reduced_chi_square": NaN}}' }),
+    applyBackendResult: () => { out.applied++; }, applyAutoFitResult: () => true, console: { warn() {} } };
+  const src = constants + '\n' + ['runAutoFitC1sGraphite', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
+  await new Function(...Object.keys(deps), src + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
+  assert.strictEqual(out.applied, 0);
+  assert.strictEqual(out.restored, true);
+  assert.ok(out.notes.some(([m, k]) => k === 'red' && /^Auto-fit failed: .*non-finite number/.test(m)), JSON.stringify(out.notes));
+});
+
+for (const [label, reply, expect] of [
+  ['a Cloudflare 524 (plain-text body)', { ok: false, status: 524, json: async () => { throw new SyntaxError('error code: 524'); }, text: async () => 'error code: 524' }, /^Auto-fit failed: Fit request failed \(HTTP 524\)\.$/],
+  ['a 500 with a JSON error', { ok: false, status: 500, json: async () => ({ error: 'Internal fitting error' }) }, /^Auto-fit failed: Internal fitting error$/],
+]) test(`F2: Auto-Fit on ${label} is a failed request with its status, never "could not be read"`, async () => {
+  const constants = lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n');
+  const state = { peaks: [], ccShift: 0, rawBE: [285, 284.5, 284], rawIntensity: [10, 20, 10] };
+  const dom = {};
+  const document = { getElementById: id => (dom[id] ??= { value: ({ 'bg-type': 'none', 'bg-start': '285', 'bg-end': '284', 'bg-endpoint-avg': '3', 'fit-method': 'leastsq' })[id] || '', style: {}, textContent: '', setAttribute() {}, classList: { add() {}, remove() {} } }), querySelector: () => ({}) };
+  const tab = { id: 1 };
+  const out = { restored: false, applied: 0, notes: [] };
+  const deps = { state, document, tabManager: { activeId: 1, _getTab: () => tab, _captureUI: () => ({ bgType: 'none' }), _syncActiveToRecord() {} },
+    notify: (m, k) => out.notes.push([m, k]), _opOwner: () => tab, _ownerActive: () => true, isC1sTab: () => true,
+    _autoFitSnapshot: () => ({}), _autoFitRestore: () => { out.restored = true; }, _showAutoFitConfirmModal: async () => true,
+    getROIData: () => ({ be: state.rawBE, inten: state.rawIntensity }), computeBackground: be => be.map(() => 0),
+    findGraphiteRawBE: () => 284.5, assessLowBERegion: () => ({}), pushUndo() {}, updateChargeCorrection() {},
+    buildAutoFitModel: () => [{ id: 1, name: 'Graphite', shape: 'Gaussian', center: 284.5, fwhm: 1, amplitude: 20 }],
+    renderPeakList() {}, _showFitSpinner() {}, _hideFitSpinner() {}, AbortController, setTimeout: () => 1, clearTimeout() {},
+    peakToBackendSpec: p => ({ ...p }), _getManualAnchors: () => [], uploadToBackend: async () => 'sid',
+    fetch: async () => reply,
+    applyBackendResult: () => { out.applied++; }, applyAutoFitResult: () => true, console: { warn() {} } };
+  const src = constants + '\n' + ['runAutoFitC1sGraphite', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
+  await new Function(...Object.keys(deps), src + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
+  assert.strictEqual(out.applied, 0);
+  assert.strictEqual(out.restored, true);
+  assert.ok(out.notes.some(([m, k]) => k === 'red' && expect.test(m)), JSON.stringify(out.notes));
+  assert.ok(!out.notes.some(([m]) => /could not be read/.test(m)));
+});
    Parameters
    ----------
    energy            : 1‑D array of binding energies (eV)
    counts            : 1‑D array of intensities (counts / CPS)
    peak_specs        : list of peak specification dicts (see _make_peak_params)
    background_method : 'shirley' | 'linear' | 'none'
    bg_start_idx      : slice start for background region (None → 0)
    bg_end_idx        : slice end for background region   (None → len)
    charge_shift_ev   : shift to apply to energy axis before fitting
    fit_kws           : extra kwargs forwarded to lmfit minimize

    Returns
    -------
    dict with keys: energy, fitted_y, background_y, residuals,
                    individual_peaks, statistics, charge_shift_applied, success
    """
    # One computation dtype: the weights are a function of the counts AND of
    # the precision they are held in (float32 counts give weights that differ
    # at 1e-8 and a different fit), and the seed hashes float64.
    energy = np.asarray(energy, dtype=float)
    counts = np.asarray(counts, dtype=float)
    if len(energy) != len(counts):
        raise ValueError("energy and counts must have the same length")
    if not peak_specs:
        raise ValueError("At least one peak specification is required")
    # Reject self/cyclic spin-orbit constraints before building lmfit exprs (F11)
    _validate_constraint_graph(peak_specs)

    # Apply charge correction
    energy = energy + charge_shift_ev

    fit_kws = dict(fit_kws or {})
    method = str(fit_kws.get("method", "leastsq")).lower()
    if method not in _FIT_METHODS:
        raise ValueError(f"Unknown fit method '{fit_kws.get('method')}'. Choices: {list(_FIT_METHODS)}")
    fit_kws["method"] = method
    # A caller's seed is consumed HERE: it replaces the request-derived one
    # and is never forwarded as a solver option (least_squares, leastsq and
    # nelder reject a 'seed' keyword).
    solver_kws = dict(fit_kws.pop("fit_kws", None) or {})
    caller_seed = solver_kws.pop("seed", None)
    if solver_kws:
        fit_kws["fit_kws"] = solver_kws
    if caller_seed is not None and (
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
  const be = grid(280, 290, 0.05);
  const g = be.map(x => env.gaussian(x, 285.0, 1.5));
  // data = 1000 * g plus a deliberate misfit on the high-count core, so that weighting changes the answer
  const data = be.map((x, i) => 1000 * g[i] * (Math.abs(x - 285) < 0.4 ? 1.30 : 1.0) + 5);
  const bg = new Array(be.length).fill(0);
  env.state.peaks = [{ id: 1, name: 'g', shape: 'Gaussian', glMix: 50, asymmetry: 0, center: 285.0, fwhm: 1.5, amplitude: 800, fixCenter: true, fixFwhm: true }];
  const out = env.runFitLocal(be, data, bg);
  assert.equal(out.success, true, JSON.stringify(out));
  const w2 = data.map(v => 1 / Math.max(v, 1));
  const aW = data.reduce((s, d, i) => s + w2[i] * d * g[i], 0) / g.reduce((s, gi, i) => s + w2[i] * gi * gi, 0);
  const aU = data.reduce((s, d, i) => s + d * g[i], 0) / g.reduce((s, gi) => s + gi * gi, 0);
  assert.ok(Math.abs(aW / aU - 1) > 0.01, `the construction must separate the two solutions (weighted ${aW}, unweighted ${aU})`);
  assert.ok(Math.abs(env.state.peaks[0].amplitude / aW - 1) < 1e-5, `amplitude ${env.state.peaks[0].amplitude} vs weighted closed form ${aW} (unweighted would be ${aU})`);
});

test('server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)', () => {
  const tabs = loadProjectTabs();
  const bridge = path.join(__dirname, 'local_lm_server_parity_backend.py');
  const py = fs.existsSync(path.join(REPO_ROOT, 'venv/bin/python3')) ? path.join(REPO_ROOT, 'venv/bin/python3')
    : (fs.existsSync('/Users/skyefortier/xps-app/venv/bin/python3') ? '/Users/skyefortier/xps-app/venv/bin/python3' : 'python3');
  for (const target of ['C1s Scan_0', 'C1s Scan_5']) {
    const env = makeEnv();
    const { be, bgSub, bg, initial } = batchTarget(env, tabs, 'C1s Scan', target);
    const src = tabs.find(t => t.name === 'C1s Scan'), tgt = tabs.find(t => t.name === target);
    const ui = BatchPropagation.propagateFitUi({ ...src.ui }, { ...tgt.ui });
    const out = env.runFitLocal(be, bgSub, bg);
    assert.equal(out.success, true, JSON.stringify(out));
    const inten = bgSub.map((v, i) => v + bg[i]);
    const server = JSON.parse(execFileSync(py, [bridge, REPO_ROOT], { input: JSON.stringify({ be, inten, peaks: initial, ui }), encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 }));
    assert.equal(server.success, true);
    assert.ok(Math.abs(out.chiReduced / server.chi2r - 1) < 0.01, `${target}: chi2r local ${out.chiReduced} vs server ${server.chi2r}`);
    env.state.peaks.forEach((p, i) => {
      const q = server.peaks[i];
      assert.ok(Math.abs(p.center - q.center) < 0.010, `${target} ${p.name}: centre ${p.center} vs server ${q.center}`);
      assert.ok(Math.abs(p.fwhm / q.fwhm - 1) < 0.01, `${target} ${p.name}: fwhm ${p.fwhm} vs server ${q.fwhm}`);
      assert.ok(Math.abs(p.amplitude / q.amplitude - 1) < 0.01, `${target} ${p.name}: amplitude ${p.amplitude} vs server ${q.amplitude}`);
    });
  }
});

// ── caM unit (2026-09-25): the local engine HOLDS LA's m, exactly ──
// It used to make a free caM free and then ROUND it in its clamp, so a
// fractional server-fitted 8.2 was silently fitted as 8 and not counted
// as a degree of freedom. Freeing it properly failed on the curve's jumps
// in m (Codex rounds 1–2), so it is held at its exact value.
test('the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom', () => {
"""Bridge for tests/js/local_lm_descent.test.js: run the SERVER fit (fitting.run_fit,
Poisson weights, Trust-Region) from the same scaled starting model the local
engine received, so the JS test can pin local-vs-server parity (unit W1).
stdin: {be, inten, peaks (frontend peak objects), ui}; argv[1]: repo root.
"""
import json
import sys

import numpy as np

sys.path.insert(0, sys.argv[1])
import fitting  # noqa: E402
from autofit.reference import peak_to_backend_spec  # noqa: E402

d = json.load(sys.stdin)
x = np.asarray(d["be"], float)
y = np.asarray(d["inten"], float)
ui = d["ui"]
specs = [peak_to_backend_spec(p, d["peaks"]) for p in d["peaks"]]
if d.get("bg_idx"):
    # the caller selected the window on the page's DISPLAY grid (_bgWindowIndices), before upload rounding
    i0, i1 = int(d["bg_idx"][0]), int(d["bg_idx"][1])
else:
    lo, hi = sorted([float(ui["bgStart"]), float(ui["bgEnd"])])
    idx = [i for i, b in enumerate(x) if lo <= b <= hi]
    i0, i1 = idx[0], idx[-1] + 1
res = fitting.run_fit(x, y, specs, background_method=ui["bgType"], bg_start_idx=i0, bg_end_idx=i1,
                      endpoint_avg=int(ui.get("endpointAvg") or 1), fit_kws={"method": "least_squares"},
                      n_perturb=int(d.get("n_perturb") or 0))   # the page sends 3; the W1 test sends none
print(json.dumps({"success": bool(res["success"]), "chi2r": res["statistics"]["reduced_chi_square"],
                  "peaks": [{k: v["value"] for k, v in ip["params"].items()} for ip in res["individual_peaks"]]}))
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-m0dmxSgM' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-lTLvWoC8' (errno=Operation not permitted)
CLAUDE.md
docs/autofit/codex/f2_acceptance_holes_r2_verdict_runA.md
docs/autofit/codex/f2_acceptance_holes_r2_verdict_runB.md
docs/autofit/codex/f2_acceptance_holes_r3_verdict_runA.md
docs/autofit/codex/f2_acceptance_holes_r3_verdict_runB.md
docs/autofit/codex/f2_acceptance_holes_recheck2_prompt.txt
docs/autofit/codex/f2_acceptance_holes_recheck3_prompt.txt
docs/autofit/codex/f2_acceptance_holes_recheck_prompt.txt
docs/autofit/codex/f2_acceptance_holes_review_prompt.txt
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md
docs/autofit/codex/f2_acceptance_holes_verdict_runB.md
docs/findings/2026-09-26-public-request-ceiling.md
docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md
docs/superpowers/plans/2026-09-26-f2-acceptance-holes.md
fitting.py
templates/index.html
tests/js/autofit_required.test.js
tests/js/fit_acceptance.test.js
tests/js/local_lm_descent.test.js
tests/js/stale_statistics.test.js
tests/test_basinhopping_outcome.py
tests/test_fit_acceptance_holes.py
tests/test_fit_reproducibility.py

codex
The regression passes on HEAD and fails on round 3’s scanner. All 507 boundary and escape probes passed, including bare `-Infinity` where the character before the sign is undefined; malformed 10 MB bodies took 72–112 ms.

The JavaScript run passed 103 tests. One Python-backed parity test stopped at import because the read-only sandbox provides no writable temporary directory. The focused Python tests are still running.

 succeeded in 52652ms:
...........                                                              [100%]
11 passed, 1 deselected in 52.24s

codex
No BLOCKER, MAJOR, or MINOR findings.

- The boundary fix at [templates/index.html:7435](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7435) handles all requested positions, including bare `-Infinity` with `t[i - 2]` undefined. No other scanner or `_readFitReply` behavior changed at HEAD.
- The [regression test:709](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/tests/js/fit_acceptance.test.js:709) is non-vacuous: it passes on HEAD and fails against round 3’s implementation. All three malformed cases independently expose the old defect.
- The full `main..HEAD` unit review revealed no additional actionable issue.

Validation: **507 adversarial probes, 103 JavaScript tests, and 11 Python tests passed**. Malformed 10 MB inputs completed in 72–112 ms. One Python-backed JavaScript parity test was sandbox-blocked; the Python upload-fixture test was excluded under read-only restrictions. No files changed.

**VERDICT: GO**
tokens used
70,594
No BLOCKER, MAJOR, or MINOR findings.

- The boundary fix at [templates/index.html:7435](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7435) handles all requested positions, including bare `-Infinity` with `t[i - 2]` undefined. No other scanner or `_readFitReply` behavior changed at HEAD.
- The [regression test:709](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/tests/js/fit_acceptance.test.js:709) is non-vacuous: it passes on HEAD and fails against round 3’s implementation. All three malformed cases independently expose the old defect.
- The full `main..HEAD` unit review revealed no additional actionable issue.

Validation: **507 adversarial probes, 103 JavaScript tests, and 11 Python tests passed**. Malformed 10 MB inputs completed in 72–112 ms. One Python-backed JavaScript parity test was sandbox-blocked; the Python upload-fixture test was excluded under read-only restrictions. No files changed.

**VERDICT: GO**
