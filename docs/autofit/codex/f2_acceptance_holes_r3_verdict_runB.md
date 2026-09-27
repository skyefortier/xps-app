OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0e1cc-d53d-7fb3-8295-c8cf4cd545bd
--------
user
Re-review unit F2 (holes in the acceptance rule), round 3: branch fix-acceptance-holes. Round-2 fixes = HEAD (git diff a5a14a0..HEAD); the whole unit is git diff main..HEAD. Earlier verdicts: docs/autofit/codex/f2_acceptance_holes_verdict_run{A,B}.md, f2_acceptance_holes_r2_verdict_run{A,B}.md; the round-1 prompt holds the brief and the sites. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

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

Finish with VERDICT: GO or VERDICT: NO-GO.
codex
I’ll read the earlier brief and verdicts, then probe the scanner and tests against the requested edge cases. I’ll keep this read-only and finish with a verdict.
exec
/bin/zsh -lc "pwd && rg --files -g AGENTS.md -g '*f2*' -g '*acceptance*' -g 'package.json' -g 'pyproject.toml' -g 'pytest.ini'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
docs/superpowers/plans/2026-09-26-f2-acceptance-holes.md
tests/test_fit_acceptance_holes.py
tests/js/fit_acceptance.test.js
docs/autofit/codex/a0_local_lm_acceptance_r5_verdict_runA.md
docs/autofit/codex/f2_acceptance_holes_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_recheck6_prompt.txt
docs/autofit/codex/f2_acceptance_holes_recheck2_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_r16_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r8_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_recheck18_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_recheck_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_r2_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r19_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_recheck10_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_recheck15_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_r14_verdict_runB.md
docs/autofit/codex/f2_acceptance_holes_r3_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r11_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_recheck3_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_review_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_r7_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r20_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r13_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r9_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_recheck4_prompt.txt
docs/autofit/codex/f2_acceptance_holes_r3_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r11_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_recheck8_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_r5_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_recheck13_prompt.txt
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_recheck5_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_r14_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r13_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r7_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_recheck16_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_r19_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r2_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r16_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r8_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r12_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r6_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r18_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r3_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r17_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_recheck7_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_recheck11_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_r9_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r20_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_recheck2_prompt.txt
docs/autofit/codex/f2_acceptance_holes_r2_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r10_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_recheck14_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_r4_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_recheck19_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_r15_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_recheck17_prompt.txt
docs/autofit/codex/f2_acceptance_holes_r2_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r10_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r4_verdict_runA.md
docs/autofit/codex/f2_acceptance_holes_review_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_r15_verdict_runB.md
docs/autofit/codex/f2_acceptance_holes_recheck_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_r12_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r6_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r18_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_recheck9_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_r3_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r17_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_recheck12_prompt.txt

exec
/bin/zsh -lc 'git status --short && git log -4 --oneline && git diff --stat a5a14a0..HEAD && git diff --stat main..HEAD' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 64ms:
 .../codex/f2_acceptance_holes_r2_verdict_runA.md   | 14912 +++++++++++
 .../codex/f2_acceptance_holes_r2_verdict_runB.md   | 24402 +++++++++++++++++++
 .../codex/f2_acceptance_holes_recheck2_prompt.txt  |    21 +
 .../plans/2026-09-26-f2-acceptance-holes.md        |     9 +
 templates/index.html                               |    25 +-
 tests/js/fit_acceptance.test.js                    |    16 +
 6 files changed, 39382 insertions(+), 3 deletions(-)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Lgt1irkZ' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-wRFJ4Q3t' (errno=Operation not permitted)
 CLAUDE.md                                          |    52 +-
 .../codex/f2_acceptance_holes_r2_verdict_runA.md   | 14912 +++++++++++
 .../codex/f2_acceptance_holes_r2_verdict_runB.md   | 24402 +++++++++++++++++++
 .../codex/f2_acceptance_holes_recheck2_prompt.txt  |    21 +
 .../codex/f2_acceptance_holes_recheck_prompt.txt   |    20 +
 .../codex/f2_acceptance_holes_review_prompt.txt    |    81 +
 .../codex/f2_acceptance_holes_verdict_runA.md      |  5974 +++++
 .../codex/f2_acceptance_holes_verdict_runB.md      |  4646 ++++
 docs/findings/2026-09-26-public-request-ceiling.md |    59 +
 .../plans/2026-09-22-dsg-page-evaluator.md         |     9 +
 .../plans/2026-09-26-f2-acceptance-holes.md        |   114 +
 fitting.py                                         |    82 +-
 templates/index.html                               |    78 +-
 tests/js/autofit_required.test.js                  |    21 +-
 tests/js/fit_acceptance.test.js                    |    66 +-
 tests/js/local_lm_descent.test.js                  |    23 +
 tests/js/stale_statistics.test.js                  |    56 +-
 tests/test_basinhopping_outcome.py                 |   125 +
 tests/test_fit_acceptance_holes.py                 |   116 +
 tests/test_fit_reproducibility.py                  |    17 +-
 20 files changed, 50856 insertions(+), 18 deletions(-)

exec
/bin/zsh -lc 'for p in /AGENTS.md /Users/AGENTS.md /Users/skyefortier/AGENTS.md /Users/skyefortier/xps-app/AGENTS.md /Users/skyefortier/xps-app/.claude/AGENTS.md /Users/skyefortier/xps-app/.claude/worktrees/AGENTS.md; do if [ -f "$p" ]; then cat "$p"; fi; done; cat docs/autofit/codex/f2_acceptance_holes_review_prompt.txt docs/superpowers/plans/2026-09-26-f2-acceptance-holes.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
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

exec
/bin/zsh -lc "rg -n 'VERDICT:|BLOCKER|MAJOR|MINOR|"'^#|''^[-*] '"\\*\\*' docs/autofit/codex/f2_acceptance_holes_verdict_runA.md docs/autofit/codex/f2_acceptance_holes_verdict_runB.md docs/autofit/codex/f2_acceptance_holes_r2_verdict_runA.md docs/autofit/codex/f2_acceptance_holes_r2_verdict_runB.md | tail -160" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:1906:# additionally need a Playwright Chromium build:  playwright install chromium
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:1907:# They self-skip when playwright/gunicorn/chromium are absent.
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4164:# F2 — holes in the acceptance rule (2026-09-26)
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4179:## 1. Sites
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4190:## 2. Decisions
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4192:- **Basinhopping (owner, 2026-09-26).** The brief said "success from the real
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4204:- **n_free = n_data is refused too.** The brief says "n_free > n_data". At
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4209:- **An unconverged required-refit blocks Auto-Fit.** "The required verdict
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4215:- **No perturbed restarts for basinhopping (owner, 2026-09-26).** Measured
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4227:## 3. Measurements
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4238:## 4. Verification
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4261:## 5. Codex rounds
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4268:# Subtest: a supported but NOT required anchor is refused before any charge-correction input is touched
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4274:# Subtest: a required anchor proceeds; a check that did not RUN (older server, error, main fit not converged) does not block
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4280:# Subtest: the request asks for the Graphite anchor by id, and the gate precedes the support gate and every cc write
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4286:# Subtest: a refit that did not converge: no verdict, and Auto-Fit refuses before any charge-correction input is touched
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4292:# Subtest: A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4298:# Subtest: a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4304:# Subtest: a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4310:# Subtest: a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4316:# Subtest: a converged backend result is applied (sanity)
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4322:# Subtest: the engine/objective labels of a fit result survive spectrum and project save/load
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4328:# Subtest: an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4334:# Subtest: an HTTP 502 on the upload is a server failure, not a transport failure
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4340:# Subtest: uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4346:# Subtest: every consumer that prints the goodness-of-fit statistic routes through the statistic identity
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4352:# Subtest: uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4358:# Subtest: a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4364:# Subtest: starting-point helpers: keyed on the persisted objective, weighted results untouched
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4370:# Subtest: Quantify shows the starting-point banner for a local result and not for a weighted one
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4376:# Subtest: every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4382:# Subtest: project save derives the designation from the objective for an older local result lacking the new fields
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4388:# Subtest: stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4394:# Subtest: _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4400:# Subtest: history preview glow is keyed on the dataset flag, not the label text
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4406:# Subtest: spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4412:# Subtest: _applyStatDisplay clears header, tooltip, caption and value together on local → none
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4418:# Subtest: _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4424:# Subtest: fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4430:# Subtest: undo/redo snapshots carry and restore model provenance
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4436:# Subtest: round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4442:# Subtest: _provenanceOf derives a designation from a live local result, and undo snapshots use it
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4448:# Subtest: batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4454:# Subtest: the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4460:# Subtest: round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4466:# Subtest: the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4472:# Subtest: the sidebar banner is sticky at the top of the scrolling panel body
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4478:# Subtest: the sidebar banner shows on a stack tab whose visible entries draw a local source fit
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4484:# Subtest: every stack chart repaint path refreshes the sidebar designation before any early return
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4490:# Subtest: closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4496:# Subtest: W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4502:# Subtest: TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4508:# Subtest: adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4514:# Subtest: adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4520:# Subtest: adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4526:# Subtest: adoption: success records the choice, the starts evidence and the key of the model it describes
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4532:# Subtest: an ordinary Run Fit on one unlinked component does not ask for the starts check
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4538:# Subtest: a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4544:# Subtest: a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4550:# Subtest: a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4556:# Subtest: a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4562:# Traceback (most recent call last):
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4563:#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/tests/js/local_lm_server_parity_backend.py", line 12, in <module>
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4564:#     import fitting  \# noqa: E402
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4565:#     ^^^^^^^^^^^^^^
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4566:#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/fitting.py", line 33, in <module>
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4567:#     from lmfit import Model, Parameters
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4568:#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4569:#     from .confidence import conf_interval, conf_interval2d
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4570:#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4571:#     from .minimizer import MinimizerException
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4572:#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4573:#     from .parameter import Parameter, Parameters
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4574:#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4575:#     from .jsonutils import decode4js, encode4js
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4576:#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4577:#     import dill
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4578:#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4579:#     from .session import (
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4580:#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4581:#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4582:#                                ^^^^^^^^^^^^^^^^^^^^^
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4583:#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4584:#     return _os.fsdecode(_gettempdir())
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4585:#                         ^^^^^^^^^^^^^
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4586:#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4587:#     tempdir = _get_default_tempdir()
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4588:#               ^^^^^^^^^^^^^^^^^^^^^^
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4589:#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4590:#     raise FileNotFoundError(_errno.ENOENT,
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4591:# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes']
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4592:# Subtest: A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4598:# Subtest: A01 replay: the linked U 4f pair also descends
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4604:# Subtest: noiseless Gaussian: amplitude 10 started at 5 is recovered
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4610:# Subtest: acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4616:# Subtest: a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4622:# Subtest: bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4628:# Subtest: bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4634:# Subtest: a weak component the data DO hold is no longer forced up to an amplitude of 1
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4640:# Subtest: derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4646:# Subtest: derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4652:# Subtest: a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4658:# Subtest: linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4664:# Subtest: round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4670:# Subtest: round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4676:# Subtest: round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4682:# Subtest: A01 replay targets converge to constrained stationary points (C1s and U 4f)
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4688:# Subtest: round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4694:# Subtest: round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4700:# Subtest: round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4706:# Subtest: round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4712:# Subtest: round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4718:# Subtest: round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4724:# Subtest: round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4730:# Subtest: weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4736:# Subtest: server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4789:# Subtest: the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4795:# Subtest: an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4801:# Subtest: an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4807:# Subtest: round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4813:# Subtest: round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4819:# Subtest: recovery from an amplitude of exactly zero (the new floor is not a trap)
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4825:# Subtest: the local engine refuses a model with no degrees of freedom; one more point and it fits
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4831:# Subtest: one accessor classifies a result against a key: none / unverified / current / stale
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4837:# Subtest: the key is the step (b) key: F1 adds no second binding mechanism and no new key field
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4843:# Subtest: Results panel, current: statistic, RMSE, R and sigma are shown
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4849:# Subtest: Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4855:# Subtest: Results panel, unverified (older save, no key): values shown with a plain note
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4861:# Subtest: status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4867:# Subtest: the stored fitted curve is never drawn, saved or stacked as the fit once stale
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4873:# Subtest: saves keep the key and say plainly when the statistics are stale or unverified
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4879:# Subtest: CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4885:# Subtest: XLSX: stale writes a WARNING row instead of the statistic, and no sigma
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4891:# Subtest: TSV: stale says the Model / Residual columns are the current, unfitted model
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4897:# Subtest: the refresh re-renders Results only when its rendered state differs
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4903:# Subtest: an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4909:# Subtest: Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4915:# Subtest: Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4921:# Subtest: closing the last tab clears the Results panel, header and status statistics too
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4927:# Subtest: reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4933:# Subtest: F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4939:# Subtest: F2: Auto-Fit on a Cloudflare 524 (plain-text body) is a failed request with its status, never "could not be read"
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4945:# Subtest: F2: Auto-Fit on a 500 with a JSON error is a failed request with its status, never "could not be read"
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4952:# tests 101
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4953:# suites 0
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4954:# pass 100
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4955:# fail 1
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4956:# cancelled 0
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4957:# skipped 0
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4958:# todo 0
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:4959:# duration_ms 6116.305123
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:5152:# ─────────────────────────────────────────────────────────────────────────────
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:5153:# lmfit Model factory
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:5154:# ─────────────────────────────────────────────────────────────────────────────
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:5955:- **MINOR — [templates/index.html:7417](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7417): misleading non-finite diagnostic.** A malformed body such as `{"message":"diagnostic mentioned NaN in text"` triggers the non-finite-number message, although `NaN` occurs only inside a string. Reproduced against `_readFitReply`. Ignore quoted strings when detecting non-finite tokens. Acceptance remains safe: nothing is applied and no local fallback runs.
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:5957:No BLOCKER or MAJOR findings.
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:5963:**VERDICT: GO**
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:5966:- **MINOR — [templates/index.html:7417](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7417): misleading non-finite diagnostic.** A malformed body such as `{"message":"diagnostic mentioned NaN in text"` triggers the non-finite-number message, although `NaN` occurs only inside a string. Reproduced against `_readFitReply`. Ignore quoted strings when detecting non-finite tokens. Acceptance remains safe: nothing is applied and no local fallback runs.
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:5968:No BLOCKER or MAJOR findings.
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md:5974:**VERDICT: GO**

exec
/bin/zsh -lc 'git diff a5a14a0..HEAD -- templates/index.html tests/js/fit_acceptance.test.js && git diff main..HEAD -- fitting.py templates/index.html tests' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-iT9oe6a6' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-WkyLSoNH' (errno=Operation not permitted)
diff --git a/templates/index.html b/templates/index.html
index 998ba54..0f4e530 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -7414,9 +7414,28 @@ function applyAutoFitResult(json, graphiteRaw, roi) {
 async function _readFitReply(resp) {
   const text = await resp.text();                 // rejects only on transport
   try { return JSON.parse(text); } catch (_) {
-    // a NaN / Infinity TOKEN, not the word inside a JSON string (Codex round 1)
-    const unquoted = text.replace(/"(?:[^"\\]|\\.)*"/g, '""');
-    const nonFinite = /(^|[\[,:\s])(-?Infinity|NaN)([\],\x7d\s]|$)/.test(unquoted);   // \x7d = closing brace
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
+        if (ch === 'I' && t.startsWith('Infinity', i) && (bound(t[i - 1]) || t[i - 1] === '-') && bound(t[i + 8])) return true;
+      }
+      return false;
+    })(text);
     const err = new Error(nonFinite
       ? 'The server\'s reply contains a non-finite number (NaN or Infinity), usually an uncertainty that could not be computed because these data do not determine the model. The fit is treated as failed.'
       : 'The server\'s reply could not be read. The fit is treated as failed.');
diff --git a/tests/js/fit_acceptance.test.js b/tests/js/fit_acceptance.test.js
index 91e60fb..fef5ee5 100644
--- a/tests/js/fit_acceptance.test.js
+++ b/tests/js/fit_acceptance.test.js
@@ -689,3 +689,19 @@ test('the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malfo
   await assert.rejects(read(reply('{"m": "say \\"NaN\\"", "v": [1, -Infinity]}')), e => /non-finite number/.test(e.message));
   assert.deepStrictEqual(await read(reply('{"m":"NaN in a label"}')), { m: 'NaN in a label' });
 });
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
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-4N62HAnz' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-JsHA4QXU' (errno=Operation not permitted)
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
index fedb356..0f4e530 100644
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
+        if (ch === 'I' && t.startsWith('Infinity', i) && (bound(t[i - 1]) || t[i - 1] === '-') && bound(t[i + 8])) return true;
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
index 44acd50..fef5ee5 100644
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
@@ -645,3 +654,54 @@ test('a transport failure after the model was edited mid-fit runs NO local fit (
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
/bin/zsh -lc 'for p in docs/autofit/codex/f2_acceptance_holes_verdict_run{A,B}.md docs/autofit/codex/f2_acceptance_holes_r2_verdict_run{A,B}.md; do tail -65 "$p"; done' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
1192:def _request_seed(x, counts, background, shapes, prefixes, params, *, fit_kws, n_perturb) -> int:
1197:    solver options and ``n_perturb``.
1236:                       "n_perturb": n_perturb})
1498:    n_perturb: int = 0,
1695:            fit_kws=fit_kws, n_perturb=n_perturb)
1783:    # starts check excludes it — and with the page's n_perturb 3 they
1787:    if n_perturb > 0 and result.success and kws.get("method") != "basinhopping":
1792:        for attempt in range(n_perturb):
1813:                          attempt + 1, n_perturb, trial_redchi, best_redchi)
1824:                log.debug("  PERTURB %d/%d  failed (exception)", attempt + 1, n_perturb)

exec
/bin/zsh -lc "node -e 'const fs=require(\"node:fs\");const html=fs.readFileSync(\"templates/index.html\",\"utf8\");const start=html.indexOf(\"async function _readFitReply(\");const end=html.indexOf(\"\\nasync function runAutoFitC1sGraphite\",start);const read=new Function(html.slice(start,end)+\";return _readFitReply\")();(async()=>{for(const text of [JSON.stringify({message:\"diagnostic mentioned NaN in text\"}),JSON.stringify({message:\"diagnostic mentioned NaN in text\"}).slice(0,-1)]){try{console.log(await read({text:async()=>text}));}catch(e){console.log(JSON.stringify({body:text,message:e.message,serverError:e.serverError}));}}})();'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
{ message: 'diagnostic mentioned NaN in text' }
{"body":"{\"message\":\"diagnostic mentioned NaN in text\"","message":"The server's reply contains a non-finite number (NaN or Infinity), usually an uncertainty that could not be computed because these data do not determine the model. The fit is treated as failed.","serverError":true}

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c '
import tempfile; tempfile.tempdir=\"/tmp\"
import app,numpy as np
app._load_session=lambda *args:(np.linspace(280,290,20),np.ones(20)*100)
a=app.create_app(); a.config[\"TESTING\"]=True
specs=[dict(id=str(i),shape=\"pseudo_voigt_gl\",center=281+i,amplitude=10,fwhm=1,fix_gl_ratio=False) for i in range(5)]
with a.test_client() as c:
    r=c.post(\"/api/analyze\",json=dict(session_id=\"a\"*32,method=\"least_squares\",material_class=\"conductor\",regions=[\"C 1s\"],peak_specs=specs,options={\"background_method\":\"none\"})); print(r.status_code,r.get_json())
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 64216ms:
.....
5 passed, 39 deselected in 63.76s (0:01:03)

 succeeded in 1962ms:
/Users/skyefortier/.matplotlib is not a writable directory
400 {'error': 'invalid option or spec: The model is not determined by these data: 20 free parameters for 20 data points leaves no degrees of freedom. Widen the fitted range, remove components or lock parameters.'}

codex
I found one minor diagnostic issue: if malformed JSON contains “NaN” only inside a quoted message, the regex reports it as a non-finite number. The fit still fails closed, so this does not block release. The targeted seed and restart checks passed, and both API routes returned HTTP 400 with the determinacy refusal.
 exited 2 in 216149ms:
.............
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! KeyboardInterrupt !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/numpy/_core/_methods.py:113: KeyboardInterrupt
(to show a full traceback on KeyboardInterrupt use --full-trace)
13 passed, 1 deselected in 215.74s (0:03:35)

codex
- **MINOR — [templates/index.html:7417](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7417): misleading non-finite diagnostic.** A malformed body such as `{"message":"diagnostic mentioned NaN in text"` triggers the non-finite-number message, although `NaN` occurs only inside a string. Reproduced against `_readFitReply`. Ignore quoted strings when detecting non-finite tokens. Acceptance remains safe: nothing is applied and no local fallback runs.

No BLOCKER or MAJOR findings.

Verification: 100/101 JavaScript tests passed; the remaining Python-backed parity test was blocked by sandbox temporary-directory restrictions. Python checks recorded 13 passes before the broader run was stopped for time; five targeted reproducibility checks also passed. Additional probes confirmed aborted-search refinement, preserved linked expressions, unchanged competitor starts, and determinacy refusals through both API routes.

Files unchanged. The public Cloudflare timeout ceiling was excluded as instructed.

**VERDICT: GO**
tokens used
98,403
- **MINOR — [templates/index.html:7417](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7417): misleading non-finite diagnostic.** A malformed body such as `{"message":"diagnostic mentioned NaN in text"` triggers the non-finite-number message, although `NaN` occurs only inside a string. Reproduced against `_readFitReply`. Ignore quoted strings when detecting non-finite tokens. Acceptance remains safe: nothing is applied and no local fallback runs.

No BLOCKER or MAJOR findings.

Verification: 100/101 JavaScript tests passed; the remaining Python-backed parity test was blocked by sandbox temporary-directory restrictions. Python checks recorded 13 passes before the broader run was stopped for time; five targeted reproducibility checks also passed. Additional probes confirmed aborted-search refinement, preserved linked expressions, unchanged competitor starts, and determinacy refusals through both API routes.

Files unchanged. The public Cloudflare timeout ceiling was excluded as instructed.

**VERDICT: GO**
import numpy as np, fitting
from unittest.mock import patch
x=np.linspace(280,292,41)
y=100+1000*np.exp(-4*np.log(2)*((x-284.5)/1.)**2)+500*np.exp(-4*np.log(2)*((x-288)/1.)**2)+.5*np.sin(np.arange(41))
s=[dict(id=\"1\",shape=\"gaussian\",center=284.5,fwhm=1,amplitude=950,amplitude_min=0),dict(id=\"2\",shape=\"gaussian\",center=288,fwhm=1,amplitude=450,amplitude_min=0)]
real=fitting.Model.fit; records=[]
def stop_reduced(self,data,params,**kw):
    reduced=len(self.components)==1
    if reduced and kw.get(\"method\")==\"least_squares\": kw[\"max_nfev\"]=1
    r=real(self,data,params,**kw)
    records.append((reduced,kw.get(\"method\"),r.success,r.chisqr))
    return r
with patch.object(fitting.Model,\"fit\",stop_reduced):
    r=fitting.run_fit(x,y,s,background_method=\"linear\",n_perturb=0,require_component=\"1\",fit_kws={\"method\":\"differential_evolution\"})
print(\"REQUIRED\",r[\"success\"],r[\"required\"])
print(\"SOLVERS\",records)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 2857ms:
/Users/skyefortier/.matplotlib is not a writable directory
REQUIRED True {'ran': True, 'required': True, 'f': 1156948.2102037217, 'chi2_with': 0.035806814389341926, 'chi2_without_refit': 3550.889791458332, 'refit_converged': True}
SOLVERS [(False, 'differential_evolution', True, np.float64(0.0358068144041998)), (False, 'least_squares', True, np.float64(0.035806814389342044)), (False, 'least_squares', True, np.float64(0.035806814389341926)), (True, 'differential_evolution', True, np.float64(3550.889791458332)), (True, 'least_squares', False, np.float64(3550.889792503432)), (True, 'least_squares', False, np.float64(2982.9266494998274))]

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir=\"/tmp\"
import app, numpy as np
from unittest.mock import patch
x=np.arange(3.); y=np.ones(3)
with patch.object(app,\"_load_session\",return_value=(x,y)):
    with app.app.test_client() as c:
        r=c.post(\"/api/fit\",json={\"session_id\":\"memory-only\",\"background\":{\"method\":\"none\"},\"fit_method\":\"least_squares\",\"peaks\":[{\"id\":\"1\",\"shape\":\"gaussian\",\"center\":1,\"amplitude\":1,\"fwhm\":1}]})
        print(r.status_code,r.get_json())
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 1850ms:
/Users/skyefortier/.matplotlib is not a writable directory
400 None

codex
- **MAJOR — Required-refit guard accepts an unverified DE candidate.** [fitting.py:1454](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/fitting.py:1454) checks only `refit.success`. Differential evolution can return `success=True, box_unverified=True` when its boxed search converges but both least-squares verification attempts fail. The main-fit acceptance rule rejects that candidate; this guard computes a required verdict from it.

  **Reproduced:** two Gaussian components on 41 noisy points, open amplitude bounds, DE, `require_component="1"`. Limiting only the reduced model’s two least-squares calls to `max_nfev=1` produced two actual solver failures, yet the response reported `required=True`, `refit_converged=True`, and F ≈ **1,156,948**. Auto-Fit’s new refusal therefore does not block this anchor. Treat `box_unverified` as failed verification here and add this regression case.

- **MINOR — Non-finite detection mistakes string contents for numeric tokens.** [templates/index.html:7417](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7417) applies its regex without tracking JSON strings.

  **Reproduced:** a body containing `{"success":true,"message":"contains NaN in label"}` with its final brace missing reports a non-finite number and suggests an undetermined model. There is no non-finite numeric token—only malformed JSON. Acceptance remains closed, but the diagnosis is wrong. Valid JSON containing the same string correctly passes.

No BLOCKER findings.

Validation: 100 JavaScript tests passed; one parity test was blocked by the sandbox’s temporary-directory restriction. Thirteen Python tests passed before I stopped the longer reproducibility run to bound review time. Additional probes verified basinhopping abort recovery, expression/bound preservation, and refusal when finite observations leave zero degrees of freedom. No files changed.

**VERDICT: NO-GO**
tokens used
82,904
- **MAJOR — Required-refit guard accepts an unverified DE candidate.** [fitting.py:1454](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/fitting.py:1454) checks only `refit.success`. Differential evolution can return `success=True, box_unverified=True` when its boxed search converges but both least-squares verification attempts fail. The main-fit acceptance rule rejects that candidate; this guard computes a required verdict from it.

  **Reproduced:** two Gaussian components on 41 noisy points, open amplitude bounds, DE, `require_component="1"`. Limiting only the reduced model’s two least-squares calls to `max_nfev=1` produced two actual solver failures, yet the response reported `required=True`, `refit_converged=True`, and F ≈ **1,156,948**. Auto-Fit’s new refusal therefore does not block this anchor. Treat `box_unverified` as failed verification here and add this regression case.

- **MINOR — Non-finite detection mistakes string contents for numeric tokens.** [templates/index.html:7417](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7417) applies its regex without tracking JSON strings.

  **Reproduced:** a body containing `{"success":true,"message":"contains NaN in label"}` with its final brace missing reports a non-finite number and suggests an undetermined model. There is no non-finite numeric token—only malformed JSON. Acceptance remains closed, but the diagnosis is wrong. Valid JSON containing the same string correctly passes.

No BLOCKER findings.

Validation: 100 JavaScript tests passed; one parity test was blocked by the sandbox’s temporary-directory restriction. Thirteen Python tests passed before I stopped the longer reproducibility run to bound review time. Additional probes verified basinhopping abort recovery, expression/bound preservation, and refusal when finite observations leave zero degrees of freedom. No files changed.

**VERDICT: NO-GO**
const h = require(\"fs\").readFileSync(\"templates/index.html\",\"utf8\");
const f = new Function(h.slice(h.indexOf(\"async function _readFitReply(\"),h.indexOf(\"async function runAutoFitC1sGraphite(\")) + \"; return _readFitReply;\")();
(async()=>{
for(const text of ['\\''{\"v\":['\\''+'\\''1,'\\''.repeat(500000)+'\\''NaN]}'\\'','\\''{\"m\":\"'\\''+String.fromCharCode(92,34).repeat(40000)]) {
const t=performance.now(); try{ await f({text:async()=>text});}catch(e){console.log(text.length, \"bytes\", (performance.now()-t).toFixed(1),\"ms\",e.serverError,e.unreadableReply);}
}
})();'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c '
import tempfile
tempfile.tempdir=\"/tmp\"
import app, fitting, inspect
import numpy as np
from unittest.mock import patch
from types import SimpleNamespace
from lmfit import Parameters
a=app.create_app()
with patch.object(app,\"_load_session\",return_value=(np.arange(3.),np.ones(3))):
    with a.test_client() as c:
        r=c.post(\"/api/fit\",json={\"session_id\":\"a\"*32,\"background\":{\"method\":\"none\"},\"fit_method\":\"least_squares\",\"peaks\":[{\"id\":\"1\",\"shape\":\"gaussian\",\"center\":1,\"amplitude\":1,\"fwhm\":1}]})
        print(\"API:\",r.status_code,r.get_json())
print(\"Flask overflow serialization:\",a.json.dumps({\"v\":float(\"1e999\")}))
p=Parameters();p.add(\"p1_amplitude\",value=1);p.add(\"p2_amplitude\",value=1)
r=SimpleNamespace(success=True,box_unverified=True,chisqr=500.,message=\"boxed\")
args=(lambda p:r,p,[\"p1_\"],np.ones(50),np.ones(50),1.,1,2)
ns=dict(fitting.__dict__)
exec(inspect.getsource(fitting._component_required).replace('\\''if not refit.success or getattr(refit, \"box_unverified\", False):'\\'','\\''if not refit.success:'\\''),ns)
print(\"new regression:\",fitting._component_required(*args))
print(\"round 1 mutation:\",ns[\"_component_required\"](*args))
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 1722ms:
/Users/skyefortier/.matplotlib is not a writable directory
API: 400 {'error': 'The model is not determined by these data: 3 free parameters for 3 data points leaves no degrees of freedom. Widen the fitted range, remove components or lock parameters.'}
Flask overflow serialization: {"v": Infinity}
new regression: {'required': None, 'f': None, 'chi2_with': 1.0, 'chi2_without_refit': 500.0, 'refit_converged': False, 'reason': 'refit_not_converged', 'message': 'boxed'}
round 1 mutation: {'required': True, 'f': 23952.0, 'chi2_with': 1.0, 'chi2_without_refit': 500.0, 'refit_converged': True}

 succeeded in 3566ms:
80006 bytes 3606.6 ms true true

codex
The solver probes confirm the round-1 acceptance hole is closed: failed DE and basinhopping verification now produce no required verdict, while a converged local competitor remains valid. Required checks ran for all five methods. All 11 selected Python tests passed, and restoring the old guard in memory made the new DE regression fail as expected.

I’m treating the remaining parser issues as minor: one mislabels truncated text; the other delays failure reporting on unusually large, quote-heavy malformed bodies. Neither accepts a failed fit.
codex
- **MINOR — Truncated strings still trigger the wrong diagnosis.** [templates/index.html:7418](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7418) strips only closed strings. Reproduced with `{"m":"contains NaN in label` delivered as a completed body: it reports a non-finite number instead of “could not be read.” The fit still fails closed, without local fallback. Track string state through EOF and add this regression.

- **MINOR — String stripping has quadratic runtime on malformed escaped strings.** [templates/index.html:7418](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7418). Reproduction: `'{"m":"' + '\\"'.repeat(40000)`. This 80 KB unterminated string took **3.6 seconds** to reject; smaller probes confirmed quadratic scaling. The synchronous work blocks the page before displaying the failure. A single-pass string/escape scanner addresses both findings.

No BLOCKER or MAJOR findings. The round-1 DE acceptance hole is fixed: actual failed verification fits now yield `required: null, refit_converged: false`, reaching Auto-Fit’s refusal. Probes covered all five methods, aborted DE searches, basinhopping verification failures, and a winning local competitor.

Validation: **11 Python tests passed; 101 JavaScript tests passed**. One Python-backed JavaScript parity test was blocked by sandbox temporary-file restrictions; the upload-fixture Python test was excluded. A memory-only API probe confirmed the determinacy HTTP 400. Files unchanged.

**VERDICT: GO**
tokens used
74,996
- **MINOR — Truncated strings still trigger the wrong diagnosis.** [templates/index.html:7418](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7418) strips only closed strings. Reproduced with `{"m":"contains NaN in label` delivered as a completed body: it reports a non-finite number instead of “could not be read.” The fit still fails closed, without local fallback. Track string state through EOF and add this regression.

- **MINOR — String stripping has quadratic runtime on malformed escaped strings.** [templates/index.html:7418](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7418). Reproduction: `'{"m":"' + '\\"'.repeat(40000)`. This 80 KB unterminated string took **3.6 seconds** to reject; smaller probes confirmed quadratic scaling. The synchronous work blocks the page before displaying the failure. A single-pass string/escape scanner addresses both findings.

No BLOCKER or MAJOR findings. The round-1 DE acceptance hole is fixed: actual failed verification fits now yield `required: null, refit_converged: false`, reaching Auto-Fit’s refusal. Probes covered all five methods, aborted DE searches, basinhopping verification failures, and a winning local competitor.

Validation: **11 Python tests passed; 101 JavaScript tests passed**. One Python-backed JavaScript parity test was blocked by sandbox temporary-file restrictions; the upload-fixture Python test was excluded. A memory-only API probe confirmed the determinacy HTTP 400. Files unchanged.

**VERDICT: GO**
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

codex
The real solver probes closed the round-1 acceptance hole: both DE and basinhopping refuse the required verdict when their verification fits fail, while a converged competitor or refinement can rescue it. Required checks ran for all five methods, and all six basinhopping tests passed.

The parser regression is release-blocking in this review: the 128 KB unterminated-string probe took 10.06 seconds in `_readFitReply`. That work runs synchronously on the page thread. A linear scan that tracks quotes and escapes would address both the freeze and the remaining truncated-string misdiagnosis.
exec
/bin/zsh -lc "node -e '
const n=64000,text='\\''{\"m\":\"'\\''+(String.fromCharCode(92)+'\\''\"'\\'').repeat(n)+'\\'' NaN '\\'';
const t=performance.now();const hit=/("'^|['"\\[,:\\s])(-?Infinity|NaN)([\\],\\x7d\\s]|"'$)/.test(text);
console.log('"'\\''round1-token-only-ms'\\'',performance.now()-t,'\\''matched'\\'',hit);
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
round1-token-only-ms 0.15383400000000336 matched true

exec
/bin/zsh -lc 'git status --short' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-7QJhDY6v' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-uKKijNIf' (errno=Operation not permitted)
?? docs/autofit/codex/f2_acceptance_holes_r2_verdict_runA.md
?? docs/autofit/codex/f2_acceptance_holes_r2_verdict_runB.md

codex
- **MAJOR — Quadratic regex can freeze the page.** [templates/index.html:7418](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7418). A 2xx body consisting of `{"m":"`, repeated `\"` pairs, and no closing quote makes the string-removal regex repeatedly scan the remaining suffix. Reproduced against `_readFitReply`: 32 KB took **613 ms**, 64 KB **2.45 s**, and 128 KB **10.06 s**. This runs synchronously on the browser thread, delaying the failure message and blocking interaction. Replace it with a linear quote/escape scanner; add an unterminated-string stress case.

- **MINOR — Truncated strings still trigger the wrong diagnosis.** [templates/index.html:7419](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7419). The body `{"message":"contains NaN in label` reports a non-finite number although `NaN` is string content. Only completed strings are blanked. Track string state through EOF; add this truncation case. Acceptance still fails closed.

No BLOCKER findings. The required-refit fix passed real solver probes across all five methods, including failed DE/basinhopping verifications, competitor recovery, and aborted DE search recovery. Flask serializes Python’s overflowing `1e999` as `Infinity`, which the reader rejects.

Validation: **11 Python tests passed; 101 JavaScript tests passed**. One JavaScript parity test was blocked by sandbox temporary-directory restrictions; the upload-fixture Python test was excluded. Files unchanged.

**VERDICT: NO-GO**
tokens used
69,048
- **MAJOR — Quadratic regex can freeze the page.** [templates/index.html:7418](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7418). A 2xx body consisting of `{"m":"`, repeated `\"` pairs, and no closing quote makes the string-removal regex repeatedly scan the remaining suffix. Reproduced against `_readFitReply`: 32 KB took **613 ms**, 64 KB **2.45 s**, and 128 KB **10.06 s**. This runs synchronously on the browser thread, delaying the failure message and blocking interaction. Replace it with a linear quote/escape scanner; add an unterminated-string stress case.

- **MINOR — Truncated strings still trigger the wrong diagnosis.** [templates/index.html:7419](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7419). The body `{"message":"contains NaN in label` reports a non-finite number although `NaN` is string content. Only completed strings are blanked. Track string state through EOF; add this truncation case. Acceptance still fails closed.

No BLOCKER findings. The required-refit fix passed real solver probes across all five methods, including failed DE/basinhopping verifications, competitor recovery, and aborted DE search recovery. Flask serializes Python’s overflowing `1e999` as `Infinity`, which the reader rejects.

Validation: **11 Python tests passed; 101 JavaScript tests passed**. One JavaScript parity test was blocked by sandbox temporary-directory restrictions; the upload-fixture Python test was excluded. Files unchanged.

**VERDICT: NO-GO**

exec
/bin/zsh -lc "sed -n '1,145p' tests/js/fit_acceptance.test.js && tail -115 tests/js/fit_acceptance.test.js && cat tests/test_fit_acceptance_holes.py tests/test_basinhopping_outcome.py && command -v node && ls -d venv /Users/skyefortier/xps-app/venv" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 exited 1 in 0ms:
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
  const env = makeEnv({ fetchImpl: async () => { throw new TypeError('Failed to fetch'); } });
  // replace the stubbed local fitter with a failing one
  const failing = makeEnv({ fetchImpl: async () => { throw new TypeError('Failed to fetch'); } });
  failing.calls.local = 0;
  // rebuild with a failing runFitLocal
  const dom = failing.dom;
  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n');
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
  // spectrum save: statistics block carries objective/engine; loader restores them
  const save = grab('function _doSaveSpectrum()', 2500);
  assert.match(save, /objective: state\.fitResult\.objective/);
  assert.match(save, /engine: state\.fitResult\.engine/);
  const load = grab('function _loadSpectrumFile(', 6000);
  assert.match(load, /\['engine', 'objective', 'weighting', 'status', 'caveat', 'starts', 'startsModelKey', 'chosenAlternative'\]/);
  // project save: the whitelisted fitResult record carries them
  const proj = grab('const buildTabData = (t) =>', 3000);
  assert.match(proj, /objective: t\.fitResult\.objective/);
  assert.match(proj, /engine: t\.fitResult\.engine/);
});
  assert.notEqual(env.dom['localfit-warn-overlay']?.classList._c, 'open');
});

test('adoption: a tab switch during the re-fit discards it and leaves the originating model as it was', async () => {
  const env = makeEnv({ specImpl: spec, ownerActive: () => false,
    fetchImpl: okResponse({ success: true, statistics: { reduced_chi_square: 1.16 }, residuals: [], fitted_y: [], individual_peaks: [] }) });
  const before = JSON.stringify(env.state.peaks);
  await env.runFit({ startPeaks: ALT_START, chosenAlternative: CHOSEN });
  assert.strictEqual(env.calls.applied, 0);
  assert.strictEqual(JSON.stringify(env.state.peaks), before);
  assert.strictEqual(env.state.fitResult.marker, 'previous');
});

test('adoption: success records the choice, the starts evidence and the key of the model it describes', async () => {
  const starts = { ran: true, n_run: 3, n_converged: 3, n_same_as_fit: 3, n_in_alternatives: 0, n_not_better_elsewhere: 0, alternatives: [] };
  const env = makeEnv({ specImpl: spec, fetchImpl: okResponse({ success: true, statistics: { reduced_chi_square: 1.16 }, residuals: [], fitted_y: [], individual_peaks: [], starts }) });
  await env.runFit({ startPeaks: ALT_START, chosenAlternative: CHOSEN });
  assert.strictEqual(env.calls.applied, 1);
  assert.deepStrictEqual(env.state.fitResult.chosenAlternative, CHOSEN);
  assert.deepStrictEqual(env.state.fitResult.starts, starts);
  assert.strictEqual(typeof env.state.fitResult.startsModelKey, 'string');
});

test('an ordinary Run Fit on one unlinked component does not ask for the starts check', async () => {
  let body = null;
  const env = makeEnv({ fetchImpl: async (url, init) => { body = JSON.parse(init.body); return { ok: true, status: 200, json: async () => ({ success: true, statistics: {}, residuals: [], fitted_y: [], individual_peaks: [] }) }; } });
  await env.runFit();
  assert.strictEqual(body.n_starts, 0);
  assert.strictEqual(env.state.fitResult.chosenAlternative, null);
});


test('a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server\'s statistics, with a fresh evidence key)', async () => {
  let env;
  env = makeEnv({ specImpl: spec, fetchImpl: async () => {
    env.state.peaks[0].center = 290; env.state.peaks[0].fixCenter = true;          // the student edits while waiting
    return { ok: true, status: 200, json: async () => ({ success: true, statistics: { reduced_chi_square: 1.2 }, residuals: [], fitted_y: [], individual_peaks: [] }) };
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
"""Unit F2 (2026-09-26): holes in the acceptance rule — "nothing is a fit
unless it converged and is determined".

- A model with at least as many free parameters as data points is refused as
  undetermined (it read as a near-perfect, fully supported fit: sweep M2).
- The required-anchor verdict needs a CONVERGED refit (sweep M3): an
  unconverged refit gives no verdict.

The basinhopping outcome (sweep H2) and the page's handling of a NaN reply
(sweep M1) are pinned in tests/test_basinhopping_outcome.py and
tests/js/fit_acceptance.test.js.
"""

import io
from types import SimpleNamespace

import numpy as np
import pytest
from lmfit import Parameters

import fitting
from app import create_app


def _gl(x, c, a, w):
    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)


def _two_gl_specs():
    # two GL components, every parameter free: centre, fwhm, amplitude, gl mix = 8
    return [
        {"id": "1", "shape": "pseudo_voigt_gl", "center": 284.5, "fwhm": 1.0, "amplitude": 1000.0,
         "gl_ratio": 0.3, "fix_gl_ratio": False, "amplitude_min": 0},
        {"id": "2", "shape": "pseudo_voigt_gl", "center": 286.0, "fwhm": 1.0, "amplitude": 400.0,
         "gl_ratio": 0.3, "fix_gl_ratio": False, "amplitude_min": 0},
    ]


def _data(n):
    x = np.linspace(283.0, 288.0, n)
    y = 100.0 + _gl(x, 284.5, 1000.0, 1.0) + _gl(x, 286.0, 400.0, 1.0)
    return x, y


@pytest.mark.parametrize("n", [6, 8])          # the sweep's reproduction (6 < 8) and zero dof (8 = 8)
def test_no_degrees_of_freedom_is_refused_as_undetermined(n):
    x, y = _data(n)
    with pytest.raises(ValueError, match=r"not determined by these data: 8 free parameters for %d data points" % n):
        fitting.run_fit(x, y, _two_gl_specs(), background_method="none", fit_kws={"method": "least_squares"})


def test_one_degree_of_freedom_is_still_a_fit_and_linked_or_locked_parameters_do_not_count():
    x, y = _data(9)                              # 8 free, 9 points: dof 1 — determined, fitted as before
    res = fitting.run_fit(x, y, _two_gl_specs(), background_method="none", fit_kws={"method": "least_squares"})
    assert res["statistics"]["n_free_params"] == 8
    # locking the mixes leaves 6 free: 7 points are then enough
    x7, y7 = _data(7)
    specs = _two_gl_specs()
    for s in specs:
        s["fix_gl_ratio"] = True
    res = fitting.run_fit(x7, y7, specs, background_method="none", fit_kws={"method": "least_squares"})
    assert res["statistics"]["n_free_params"] == 6


@pytest.fixture()
def client(tmp_path):
    app = create_app(upload_folder=str(tmp_path))
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_api_fit_returns_the_refusal_as_a_400_with_its_message(client):
    x, y = _data(6)
    csv = "\n".join(f"{a:.4f},{b:.2f}" for a, b in zip(x, y))
    sid = client.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "tiny.csv")}).get_json()["session_id"]
    resp = client.post("/api/fit", json={"session_id": sid, "background": {"method": "none"},
                                         "peaks": _two_gl_specs(), "fit_method": "least_squares"})
    assert resp.status_code == 400
    assert "not determined by these data" in resp.get_json()["error"]


def test_an_unconverged_refit_gives_no_required_verdict():
    """The sweep's reproduction: a refit stopped early read required: true
    (F 992) for an anchor that is redundant (F 1.17 once the refit completes)."""
    params = Parameters()
    params.add("p1_amplitude", value=1.0)
    params.add("p2_amplitude", value=1.0)
    y_sub = np.ones(50)
    stopped = SimpleNamespace(success=False, chisqr=992.0, message="max evaluations reached")
    out = fitting._component_required(lambda p: stopped, params, ["p1_"], y_sub, np.ones(50),
                                      chi2_with=1.0, n_free_comp=1, n_free_total=2)
    assert out["required"] is None
    assert out["f"] is None
    assert out["refit_converged"] is False
    assert out["reason"] == "refit_not_converged"
    assert "max evaluations" in out["message"]
    # a converged refit still gives its verdict, unchanged
    done = SimpleNamespace(success=True, chisqr=1.0 + 1.17 / 48, message="ok")
    out = fitting._component_required(lambda p: done, params, ["p1_"], y_sub, np.ones(50),
                                      chi2_with=1.0, n_free_comp=1, n_free_total=2)
    assert out["refit_converged"] is True and out["required"] is False
    assert out["f"] == pytest.approx(1.17)


def test_an_unverified_differential_evolution_refit_gives_no_required_verdict():
    """Codex round 1: DE can return success=True with box_unverified=True (its
    boxed search converged, both verifications failed); the main fit's
    acceptance rule rejects that candidate, so the required verdict must too."""
    params = Parameters()
    params.add("p1_amplitude", value=1.0)
    params.add("p2_amplitude", value=1.0)
    unverified = SimpleNamespace(success=True, box_unverified=True, chisqr=500.0, message="boxed")
    out = fitting._component_required(lambda p: unverified, params, ["p1_"], np.ones(50), np.ones(50),
                                      chi2_with=1.0, n_free_comp=1, n_free_total=2)
    assert out["required"] is None and out["refit_converged"] is False
"""Unit F2 (2026-09-26), sweep H2: basinhopping's convergence.

lmfit 1.3 marks every basinhopping fit successful (it sets success before
minimising and never reads scipy's result). scipy's own flag is no verdict
either: on 23 of 24 sampled committed targets it reports BFGS "precision
loss" at a point equal to Trust-Region's minimum. Owner decision: the
differential-evolution pattern in full — the search, an unconditional
least_squares refinement from its point under the request's bounds (the
refinement's convergence is the verdict), then a competition with a
least_squares fit from the same start (verified beats unverified, then the
lower chi-square), so basinhopping is never worse than the default method.
"""

import numpy as np
import pytest

import fitting


def _gl(x, a, c, w):
    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)


X = np.linspace(280.0, 292.0, 121)


def _two_peaks():
    y = np.round(200 + _gl(X, 5000, 284.8, 1.2) + _gl(X, 1800, 286.4, 1.3), 2)
    specs = [
        {"id": "1", "shape": "gaussian", "center": 284.6, "fwhm": 1.0, "amplitude": 4000.0, "amplitude_min": 0},
        {"id": "2", "shape": "gaussian", "center": 286.6, "fwhm": 1.0, "amplitude": 1500.0, "amplitude_min": 0},
    ]
    return y, specs


def _spy(monkeypatch, fail_methods=()):
    calls = []
    real = fitting.Model.fit

    def spy(self, data, params, **kw):
        res = real(self, data, params, **kw)
        calls.append(kw.get("method"))
        if kw.get("method") in fail_methods:
            res.success = False
        return res

    monkeypatch.setattr(fitting.Model, "fit", spy)
    return calls


def test_a_basinhopping_fit_is_the_refined_least_squares_result_and_never_worse_than_the_default():
    y, specs = _two_peaks()
    kw = dict(background_method="linear", n_perturb=0)
    bh = fitting.run_fit(X, y, specs, fit_kws={"method": "basinhopping"}, **kw)
    tr = fitting.run_fit(X, y, specs, fit_kws={"method": "least_squares"}, **kw)
    assert bh["success"] is True
    assert bh["statistics"]["reduced_chi_square"] <= tr["statistics"]["reduced_chi_square"] * (1 + 1e-12)
    # the returned result carries least_squares uncertainties (the refinement or the competitor)
    assert all(ip["params"]["center"]["stderr"] is not None for ip in bh["individual_peaks"])


def test_the_call_sequence_is_search_refine_compete(monkeypatch):
    calls = _spy(monkeypatch)
    y, specs = _two_peaks()
    fitting.run_fit(X, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "basinhopping"})
    assert calls == ["basinhopping", "least_squares", "least_squares"]


def test_an_unverifiable_search_does_not_converge_when_the_competitor_fails_too(monkeypatch):
    # every least_squares (the refinement AND the competitor) reports failure:
    # nothing verified the point, so it is not a converged fit — the old
    # behaviour returned lmfit's unconditional success here
    _spy(monkeypatch, fail_methods=("least_squares",))
    y, specs = _two_peaks()
    res = fitting.run_fit(X, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "basinhopping"})
    assert res["success"] is False
    assert "not a verified fit" in res["message"]


def test_a_failed_refinement_is_rescued_by_a_converged_competitor(monkeypatch):
    real = fitting.Model.fit
    seen = []

    def spy(self, data, params, **kw):
        res = real(self, data, params, **kw)
        seen.append(kw.get("method"))
        if kw.get("method") == "least_squares" and seen.count("least_squares") == 1:
            res.success = False                  # the refinement from the search's point
        return res

    monkeypatch.setattr(fitting.Model, "fit", spy)
    y, specs = _two_peaks()
    res = fitting.run_fit(X, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "basinhopping"})
    assert res["success"] is True, res["message"]


def test_the_required_refit_goes_through_the_same_verification(monkeypatch):
    calls = _spy(monkeypatch)
    y, specs = _two_peaks()
    res = fitting.run_fit(X, y, specs, background_method="linear", n_perturb=0, require_component="2",
                          fit_kws={"method": "basinhopping"})
    # the main fit and the required refit: two verified candidates
    assert calls.count("basinhopping") == 2
    assert calls.count("least_squares") == 4
    assert res["required"]["ran"] is True and res["required"]["refit_converged"] is True


def test_basinhopping_runs_no_perturbed_restarts(monkeypatch):
    # a global search already; with the page's n_perturb 3 the restarts took it
    # past the 300 s server timeout on 14 of 16 multi-component targets
    calls = _spy(monkeypatch)
    y, specs = _two_peaks()
    with_restarts_asked = fitting.run_fit(X, y, specs, background_method="linear", n_perturb=3,
                                          fit_kws={"method": "basinhopping"})
    assert calls.count("basinhopping") == 1
    assert with_restarts_asked["success"] is True
    # the answer is the one the same request without restarts gets
    without = fitting.run_fit(X, y, specs, background_method="linear", n_perturb=0,
                              fit_kws={"method": "basinhopping"})
    assert with_restarts_asked["statistics"]["reduced_chi_square"] == pytest.approx(
        without["statistics"]["reduced_chi_square"], rel=1e-9)
    # differential evolution and the local methods still run the restarts they are asked for
    calls.clear()
    fitting.run_fit(X, y, specs, background_method="linear", n_perturb=2, fit_kws={"method": "leastsq"})
    assert calls.count("leastsq") == 3
/Users/skyefortier/.local/bin/node
ls: venv: No such file or directory
/Users/skyefortier/xps-app/venv

exec
/bin/zsh -lc 'git diff a5a14a0..HEAD -- templates/index.html tests/js/fit_acceptance.test.js && git diff main..HEAD -- fitting.py templates/index.html' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-PeEwG6tv' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-jicyaTTS' (errno=Operation not permitted)
diff --git a/templates/index.html b/templates/index.html
index 998ba54..0f4e530 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -7414,9 +7414,28 @@ function applyAutoFitResult(json, graphiteRaw, roi) {
 async function _readFitReply(resp) {
   const text = await resp.text();                 // rejects only on transport
   try { return JSON.parse(text); } catch (_) {
-    // a NaN / Infinity TOKEN, not the word inside a JSON string (Codex round 1)
-    const unquoted = text.replace(/"(?:[^"\\]|\\.)*"/g, '""');
-    const nonFinite = /(^|[\[,:\s])(-?Infinity|NaN)([\],\x7d\s]|$)/.test(unquoted);   // \x7d = closing brace
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
+        if (ch === 'I' && t.startsWith('Infinity', i) && (bound(t[i - 1]) || t[i - 1] === '-') && bound(t[i + 8])) return true;
+      }
+      return false;
+    })(text);
     const err = new Error(nonFinite
       ? 'The server\'s reply contains a non-finite number (NaN or Infinity), usually an uncertainty that could not be computed because these data do not determine the model. The fit is treated as failed.'
       : 'The server\'s reply could not be read. The fit is treated as failed.');
diff --git a/tests/js/fit_acceptance.test.js b/tests/js/fit_acceptance.test.js
index 91e60fb..fef5ee5 100644
--- a/tests/js/fit_acceptance.test.js
+++ b/tests/js/fit_acceptance.test.js
@@ -689,3 +689,19 @@ test('the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malfo
   await assert.rejects(read(reply('{"m": "say \\"NaN\\"", "v": [1, -Infinity]}')), e => /non-finite number/.test(e.message));
   assert.deepStrictEqual(await read(reply('{"m":"NaN in a label"}')), { m: 'NaN in a label' });
 });
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
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-cBTJxrdq' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-jzktWIGs' (errno=Operation not permitted)
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
index fedb356..0f4e530 100644
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
+        if (ch === 'I' && t.startsWith('Infinity', i) && (bound(t[i - 1]) || t[i - 1] === '-') && bound(t[i + 8])) return true;
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
/bin/zsh -lc 'for p in docs/autofit/codex/f2_acceptance_holes_verdict_run{A,B}.md docs/autofit/codex/f2_acceptance_holes_r2_verdict_run{A,B}.md; do tail -24 "$p"; done' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
(to show a full traceback on KeyboardInterrupt use --full-trace)
13 passed, 1 deselected in 215.74s (0:03:35)

codex
- **MINOR — [templates/index.html:7417](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7417): misleading non-finite diagnostic.** A malformed body such as `{"message":"diagnostic mentioned NaN in text"` triggers the non-finite-number message, although `NaN` occurs only inside a string. Reproduced against `_readFitReply`. Ignore quoted strings when detecting non-finite tokens. Acceptance remains safe: nothing is applied and no local fallback runs.

No BLOCKER or MAJOR findings.

Verification: 100/101 JavaScript tests passed; the remaining Python-backed parity test was blocked by sandbox temporary-directory restrictions. Python checks recorded 13 passes before the broader run was stopped for time; five targeted reproducibility checks also passed. Additional probes confirmed aborted-search refinement, preserved linked expressions, unchanged competitor starts, and determinacy refusals through both API routes.

Files unchanged. The public Cloudflare timeout ceiling was excluded as instructed.

**VERDICT: GO**
tokens used
98,403
- **MINOR — [templates/index.html:7417](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7417): misleading non-finite diagnostic.** A malformed body such as `{"message":"diagnostic mentioned NaN in text"` triggers the non-finite-number message, although `NaN` occurs only inside a string. Reproduced against `_readFitReply`. Ignore quoted strings when detecting non-finite tokens. Acceptance remains safe: nothing is applied and no local fallback runs.

No BLOCKER or MAJOR findings.

Verification: 100/101 JavaScript tests passed; the remaining Python-backed parity test was blocked by sandbox temporary-directory restrictions. Python checks recorded 13 passes before the broader run was stopped for time; five targeted reproducibility checks also passed. Additional probes confirmed aborted-search refinement, preserved linked expressions, unchanged competitor starts, and determinacy refusals through both API routes.

Files unchanged. The public Cloudflare timeout ceiling was excluded as instructed.

**VERDICT: GO**
- **MINOR — Non-finite detection mistakes string contents for numeric tokens.** [templates/index.html:7417](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7417) applies its regex without tracking JSON strings.

  **Reproduced:** a body containing `{"success":true,"message":"contains NaN in label"}` with its final brace missing reports a non-finite number and suggests an undetermined model. There is no non-finite numeric token—only malformed JSON. Acceptance remains closed, but the diagnosis is wrong. Valid JSON containing the same string correctly passes.

No BLOCKER findings.

Validation: 100 JavaScript tests passed; one parity test was blocked by the sandbox’s temporary-directory restriction. Thirteen Python tests passed before I stopped the longer reproducibility run to bound review time. Additional probes verified basinhopping abort recovery, expression/bound preservation, and refusal when finite observations leave zero degrees of freedom. No files changed.

**VERDICT: NO-GO**
tokens used
82,904
- **MAJOR — Required-refit guard accepts an unverified DE candidate.** [fitting.py:1454](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/fitting.py:1454) checks only `refit.success`. Differential evolution can return `success=True, box_unverified=True` when its boxed search converges but both least-squares verification attempts fail. The main-fit acceptance rule rejects that candidate; this guard computes a required verdict from it.

  **Reproduced:** two Gaussian components on 41 noisy points, open amplitude bounds, DE, `require_component="1"`. Limiting only the reduced model’s two least-squares calls to `max_nfev=1` produced two actual solver failures, yet the response reported `required=True`, `refit_converged=True`, and F ≈ **1,156,948**. Auto-Fit’s new refusal therefore does not block this anchor. Treat `box_unverified` as failed verification here and add this regression case.

- **MINOR — Non-finite detection mistakes string contents for numeric tokens.** [templates/index.html:7417](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7417) applies its regex without tracking JSON strings.

  **Reproduced:** a body containing `{"success":true,"message":"contains NaN in label"}` with its final brace missing reports a non-finite number and suggests an undetermined model. There is no non-finite numeric token—only malformed JSON. Acceptance remains closed, but the diagnosis is wrong. Valid JSON containing the same string correctly passes.

No BLOCKER findings.

Validation: 100 JavaScript tests passed; one parity test was blocked by the sandbox’s temporary-directory restriction. Thirteen Python tests passed before I stopped the longer reproducibility run to bound review time. Additional probes verified basinhopping abort recovery, expression/bound preservation, and refusal when finite observations leave zero degrees of freedom. No files changed.

**VERDICT: NO-GO**
The solver probes confirm the round-1 acceptance hole is closed: failed DE and basinhopping verification now produce no required verdict, while a converged local competitor remains valid. Required checks ran for all five methods. All 11 selected Python tests passed, and restoring the old guard in memory made the new DE regression fail as expected.

I’m treating the remaining parser issues as minor: one mislabels truncated text; the other delays failure reporting on unusually large, quote-heavy malformed bodies. Neither accepts a failed fit.
codex
- **MINOR — Truncated strings still trigger the wrong diagnosis.** [templates/index.html:7418](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7418) strips only closed strings. Reproduced with `{"m":"contains NaN in label` delivered as a completed body: it reports a non-finite number instead of “could not be read.” The fit still fails closed, without local fallback. Track string state through EOF and add this regression.

- **MINOR — String stripping has quadratic runtime on malformed escaped strings.** [templates/index.html:7418](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7418). Reproduction: `'{"m":"' + '\\"'.repeat(40000)`. This 80 KB unterminated string took **3.6 seconds** to reject; smaller probes confirmed quadratic scaling. The synchronous work blocks the page before displaying the failure. A single-pass string/escape scanner addresses both findings.

No BLOCKER or MAJOR findings. The round-1 DE acceptance hole is fixed: actual failed verification fits now yield `required: null, refit_converged: false`, reaching Auto-Fit’s refusal. Probes covered all five methods, aborted DE searches, basinhopping verification failures, and a winning local competitor.

Validation: **11 Python tests passed; 101 JavaScript tests passed**. One Python-backed JavaScript parity test was blocked by sandbox temporary-file restrictions; the upload-fixture Python test was excluded. A memory-only API probe confirmed the determinacy HTTP 400. Files unchanged.

**VERDICT: GO**
tokens used
74,996
- **MINOR — Truncated strings still trigger the wrong diagnosis.** [templates/index.html:7418](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7418) strips only closed strings. Reproduced with `{"m":"contains NaN in label` delivered as a completed body: it reports a non-finite number instead of “could not be read.” The fit still fails closed, without local fallback. Track string state through EOF and add this regression.

- **MINOR — String stripping has quadratic runtime on malformed escaped strings.** [templates/index.html:7418](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7418). Reproduction: `'{"m":"' + '\\"'.repeat(40000)`. This 80 KB unterminated string took **3.6 seconds** to reject; smaller probes confirmed quadratic scaling. The synchronous work blocks the page before displaying the failure. A single-pass string/escape scanner addresses both findings.

No BLOCKER or MAJOR findings. The round-1 DE acceptance hole is fixed: actual failed verification fits now yield `required: null, refit_converged: false`, reaching Auto-Fit’s refusal. Probes covered all five methods, aborted DE searches, basinhopping verification failures, and a winning local competitor.

Validation: **11 Python tests passed; 101 JavaScript tests passed**. One Python-backed JavaScript parity test was blocked by sandbox temporary-file restrictions; the upload-fixture Python test was excluded. A memory-only API probe confirmed the determinacy HTTP 400. Files unchanged.

**VERDICT: GO**
?? docs/autofit/codex/f2_acceptance_holes_r2_verdict_runA.md
?? docs/autofit/codex/f2_acceptance_holes_r2_verdict_runB.md

codex
- **MAJOR — Quadratic regex can freeze the page.** [templates/index.html:7418](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7418). A 2xx body consisting of `{"m":"`, repeated `\"` pairs, and no closing quote makes the string-removal regex repeatedly scan the remaining suffix. Reproduced against `_readFitReply`: 32 KB took **613 ms**, 64 KB **2.45 s**, and 128 KB **10.06 s**. This runs synchronously on the browser thread, delaying the failure message and blocking interaction. Replace it with a linear quote/escape scanner; add an unterminated-string stress case.

- **MINOR — Truncated strings still trigger the wrong diagnosis.** [templates/index.html:7419](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7419). The body `{"message":"contains NaN in label` reports a non-finite number although `NaN` is string content. Only completed strings are blanked. Track string state through EOF; add this truncation case. Acceptance still fails closed.

No BLOCKER findings. The required-refit fix passed real solver probes across all five methods, including failed DE/basinhopping verifications, competitor recovery, and aborted DE search recovery. Flask serializes Python’s overflowing `1e999` as `Infinity`, which the reader rejects.

Validation: **11 Python tests passed; 101 JavaScript tests passed**. One JavaScript parity test was blocked by sandbox temporary-directory restrictions; the upload-fixture Python test was excluded. Files unchanged.

**VERDICT: NO-GO**
tokens used
69,048
- **MAJOR — Quadratic regex can freeze the page.** [templates/index.html:7418](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7418). A 2xx body consisting of `{"m":"`, repeated `\"` pairs, and no closing quote makes the string-removal regex repeatedly scan the remaining suffix. Reproduced against `_readFitReply`: 32 KB took **613 ms**, 64 KB **2.45 s**, and 128 KB **10.06 s**. This runs synchronously on the browser thread, delaying the failure message and blocking interaction. Replace it with a linear quote/escape scanner; add an unterminated-string stress case.

- **MINOR — Truncated strings still trigger the wrong diagnosis.** [templates/index.html:7419](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7419). The body `{"message":"contains NaN in label` reports a non-finite number although `NaN` is string content. Only completed strings are blanked. Track string state through EOF; add this truncation case. Acceptance still fails closed.

No BLOCKER findings. The required-refit fix passed real solver probes across all five methods, including failed DE/basinhopping verifications, competitor recovery, and aborted DE search recovery. Flask serializes Python’s overflowing `1e999` as `Infinity`, which the reader rejects.

Validation: **11 Python tests passed; 101 JavaScript tests passed**. One JavaScript parity test was blocked by sandbox temporary-directory restrictions; the upload-fixture Python test was excluded. Files unchanged.

**VERDICT: NO-GO**

exec
/bin/zsh -lc 'node --test tests/js/fit_acceptance.test.js tests/js/autofit_required.test.js tests/js/stale_statistics.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 173ms:
# Subtest: a supported but NOT required anchor is refused before any charge-correction input is touched
ok 1 - a supported but NOT required anchor is refused before any charge-correction input is touched
  ---
  duration_ms: 5.05758
  type: 'test'
  ...
# Subtest: a required anchor proceeds; a check that did not RUN (older server, error, main fit not converged) does not block
ok 2 - a required anchor proceeds; a check that did not RUN (older server, error, main fit not converged) does not block
  ---
  duration_ms: 7.868579
  type: 'test'
  ...
# Subtest: the request asks for the Graphite anchor by id, and the gate precedes the support gate and every cc write
ok 3 - the request asks for the Graphite anchor by id, and the gate precedes the support gate and every cc write
  ---
  duration_ms: 0.975374
  type: 'test'
  ...
# Subtest: a refit that did not converge: no verdict, and Auto-Fit refuses before any charge-correction input is touched
ok 4 - a refit that did not converge: no verdict, and Auto-Fit refuses before any charge-correction input is touched
  ---
  duration_ms: 2.125263
  type: 'test'
  ...
# Subtest: A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
ok 5 - A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
  ---
  duration_ms: 8.869139
  type: 'test'
  ...
# Subtest: a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
ok 6 - a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
  ---
  duration_ms: 7.08983
  type: 'test'
  ...
# Subtest: a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
ok 7 - a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
  ---
  duration_ms: 3.45355
  type: 'test'
  ...
# Subtest: a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
ok 8 - a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
  ---
  duration_ms: 8.905377
  type: 'test'
  ...
# Subtest: a converged backend result is applied (sanity)
ok 9 - a converged backend result is applied (sanity)
  ---
  duration_ms: 2.743505
  type: 'test'
  ...
# Subtest: the engine/objective labels of a fit result survive spectrum and project save/load
ok 10 - the engine/objective labels of a fit result survive spectrum and project save/load
  ---
  duration_ms: 0.626763
  type: 'test'
  ...
# Subtest: an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
ok 11 - an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
  ---
  duration_ms: 2.580334
  type: 'test'
  ...
# Subtest: an HTTP 502 on the upload is a server failure, not a transport failure
ok 12 - an HTTP 502 on the upload is a server failure, not a transport failure
  ---
  duration_ms: 2.418015
  type: 'test'
  ...
# Subtest: uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
ok 13 - uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
  ---
  duration_ms: 1.510486
  type: 'test'
  ...
# Subtest: every consumer that prints the goodness-of-fit statistic routes through the statistic identity
ok 14 - every consumer that prints the goodness-of-fit statistic routes through the statistic identity
  ---
  duration_ms: 0.739515
  type: 'test'
  ...
# Subtest: uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
ok 15 - uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
  ---
  duration_ms: 0.577457
  type: 'test'
  ...
# Subtest: a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
ok 16 - a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
  ---
  duration_ms: 1.264895
  type: 'test'
  ...
# Subtest: starting-point helpers: keyed on the persisted objective, weighted results untouched
ok 17 - starting-point helpers: keyed on the persisted objective, weighted results untouched
  ---
  duration_ms: 2.664884
  type: 'test'
  ...
# Subtest: Quantify shows the starting-point banner for a local result and not for a weighted one
ok 18 - Quantify shows the starting-point banner for a local result and not for a weighted one
  ---
  duration_ms: 4.204368
  type: 'test'
  ...
# Subtest: every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
ok 19 - every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
  ---
  duration_ms: 1.426174
  type: 'test'
  ...
# Subtest: project save derives the designation from the objective for an older local result lacking the new fields
ok 20 - project save derives the designation from the objective for an older local result lacking the new fields
  ---
  duration_ms: 6.365409
  type: 'test'
  ...
# Subtest: stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
ok 21 - stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
  ---
  duration_ms: 0.783445
  type: 'test'
  ...
# Subtest: _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
ok 22 - _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
  ---
  duration_ms: 2.832517
  type: 'test'
  ...
# Subtest: history preview glow is keyed on the dataset flag, not the label text
ok 23 - history preview glow is keyed on the dataset flag, not the label text
  ---
  duration_ms: 0.575393
  type: 'test'
  ...
# Subtest: spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
ok 24 - spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
  ---
  duration_ms: 0.412263
  type: 'test'
  ...
# Subtest: _applyStatDisplay clears header, tooltip, caption and value together on local → none
ok 25 - _applyStatDisplay clears header, tooltip, caption and value together on local → none
  ---
  duration_ms: 2.632525
  type: 'test'
  ...
# Subtest: _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
ok 26 - _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
  ---
  duration_ms: 1.319978
  type: 'test'
  ...
# Subtest: fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
ok 27 - fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
  ---
  duration_ms: 1.273043
  type: 'test'
  ...
# Subtest: undo/redo snapshots carry and restore model provenance
ok 28 - undo/redo snapshots carry and restore model provenance
  ---
  duration_ms: 3.026737
  type: 'test'
  ...
# Subtest: round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
ok 29 - round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
  ---
  duration_ms: 0.999477
  type: 'test'
  ...
# Subtest: _provenanceOf derives a designation from a live local result, and undo snapshots use it
ok 30 - _provenanceOf derives a designation from a live local result, and undo snapshots use it
  ---
  duration_ms: 2.25532
  type: 'test'
  ...
# Subtest: batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
ok 31 - batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
  ---
  duration_ms: 0.303427
  type: 'test'
  ...
# Subtest: the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
ok 32 - the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
  ---
  duration_ms: 2.124244
  type: 'test'
  ...
# Subtest: round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
ok 33 - round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
  ---
  duration_ms: 0.544515
  type: 'test'
  ...
# Subtest: the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
ok 34 - the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
  ---
  duration_ms: 2.460589
  type: 'test'
  ...
# Subtest: the sidebar banner is sticky at the top of the scrolling panel body
ok 35 - the sidebar banner is sticky at the top of the scrolling panel body
  ---
  duration_ms: 0.230013
  type: 'test'
  ...
# Subtest: the sidebar banner shows on a stack tab whose visible entries draw a local source fit
ok 36 - the sidebar banner shows on a stack tab whose visible entries draw a local source fit
  ---
  duration_ms: 2.13126
  type: 'test'
  ...
# Subtest: every stack chart repaint path refreshes the sidebar designation before any early return
ok 37 - every stack chart repaint path refreshes the sidebar designation before any early return
  ---
  duration_ms: 0.331101
  type: 'test'
  ...
# Subtest: closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
ok 38 - closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
  ---
  duration_ms: 0.161412
  type: 'test'
  ...
# Subtest: W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
ok 39 - W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
  ---
  duration_ms: 2.417226
  type: 'test'
  ...
# Subtest: TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
ok 40 - TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
  ---
  duration_ms: 3.703545
  type: 'test'
  ...
# Subtest: adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
ok 41 - adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
  ---
  duration_ms: 2.620774
  type: 'test'
  ...
# Subtest: adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
ok 42 - adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
  ---
  duration_ms: 2.385587
  type: 'test'
  ...
# Subtest: adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
ok 43 - adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
  ---
  duration_ms: 2.497983
  type: 'test'
  ...
# Subtest: adoption: success records the choice, the starts evidence and the key of the model it describes
ok 44 - adoption: success records the choice, the starts evidence and the key of the model it describes
  ---
  duration_ms: 2.728809
  type: 'test'
  ...
# Subtest: an ordinary Run Fit on one unlinked component does not ask for the starts check
ok 45 - an ordinary Run Fit on one unlinked component does not ask for the starts check
  ---
  duration_ms: 2.589997
  type: 'test'
  ...
# Subtest: a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
ok 46 - a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
  ---
  duration_ms: 3.426896
  type: 'test'
  ...
# Subtest: a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
ok 47 - a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
  ---
  duration_ms: 5.508698
  type: 'test'
  ...
# Subtest: a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
ok 48 - a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
  ---
  duration_ms: 2.809787
  type: 'test'
  ...
# Subtest: a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
ok 49 - a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
  ---
  duration_ms: 4.818347
  type: 'test'
  ...
# Subtest: the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)
ok 50 - the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)
  ---
  duration_ms: 0.745235
  type: 'test'
  ...
# Subtest: the token scan is linear and keeps a truncated string a string (Codex round 2)
ok 51 - the token scan is linear and keeps a truncated string a string (Codex round 2)
  ---
  duration_ms: 3.015056
  type: 'test'
  ...
# Subtest: one accessor classifies a result against a key: none / unverified / current / stale
ok 52 - one accessor classifies a result against a key: none / unverified / current / stale
  ---
  duration_ms: 15.820761
  type: 'test'
  ...
# Subtest: the key is the step (b) key: F1 adds no second binding mechanism and no new key field
ok 53 - the key is the step (b) key: F1 adds no second binding mechanism and no new key field
  ---
  duration_ms: 5.112758
  type: 'test'
  ...
# Subtest: Results panel, current: statistic, RMSE, R and sigma are shown
ok 54 - Results panel, current: statistic, RMSE, R and sigma are shown
  ---
  duration_ms: 7.877136
  type: 'test'
  ...
# Subtest: Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
ok 55 - Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
  ---
  duration_ms: 6.33135
  type: 'test'
  ...
# Subtest: Results panel, unverified (older save, no key): values shown with a plain note
ok 56 - Results panel, unverified (older save, no key): values shown with a plain note
  ---
  duration_ms: 6.274307
  type: 'test'
  ...
# Subtest: status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
ok 57 - status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
  ---
  duration_ms: 6.085344
  type: 'test'
  ...
# Subtest: the stored fitted curve is never drawn, saved or stacked as the fit once stale
ok 58 - the stored fitted curve is never drawn, saved or stacked as the fit once stale
  ---
  duration_ms: 2.581002
  type: 'test'
  ...
# Subtest: saves keep the key and say plainly when the statistics are stale or unverified
ok 59 - saves keep the key and say plainly when the statistics are stale or unverified
  ---
  duration_ms: 2.094487
  type: 'test'
  ...
# Subtest: CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
ok 60 - CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
  ---
  duration_ms: 11.854722
  type: 'test'
  ...
# Subtest: XLSX: stale writes a WARNING row instead of the statistic, and no sigma
ok 61 - XLSX: stale writes a WARNING row instead of the statistic, and no sigma
  ---
  duration_ms: 4.051234
  type: 'test'
  ...
# Subtest: TSV: stale says the Model / Residual columns are the current, unfitted model
ok 62 - TSV: stale says the Model / Residual columns are the current, unfitted model
  ---
  duration_ms: 6.518848
  type: 'test'
  ...
# Subtest: the refresh re-renders Results only when its rendered state differs
ok 63 - the refresh re-renders Results only when its rendered state differs
  ---
  duration_ms: 2.767559
  type: 'test'
  ...
# Subtest: an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
ok 64 - an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
  ---
  duration_ms: 2.454665
  type: 'test'
  ...
# Subtest: Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
ok 65 - Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
  ---
  duration_ms: 2.94099
  type: 'test'
  ...
# Subtest: Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
ok 66 - Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
  ---
  duration_ms: 6.837637
  type: 'test'
  ...
# Subtest: closing the last tab clears the Results panel, header and status statistics too
ok 67 - closing the last tab clears the Results panel, header and status statistics too
  ---
  duration_ms: 0.164152
  type: 'test'
  ...
# Subtest: reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
ok 68 - reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
  ---
  duration_ms: 1.20398
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back
ok 69 - F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back
  ---
  duration_ms: 3.893033
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a Cloudflare 524 (plain-text body) is a failed request with its status, never "could not be read"
ok 70 - F2: Auto-Fit on a Cloudflare 524 (plain-text body) is a failed request with its status, never "could not be read"
  ---
  duration_ms: 3.955989
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a 500 with a JSON error is a failed request with its status, never "could not be read"
ok 71 - F2: Auto-Fit on a 500 with a JSON error is a failed request with its status, never "could not be read"
  ---
  duration_ms: 2.442222
  type: 'test'
  ...
1..71
# tests 71
# suites 0
# pass 71
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 238.100641

exec
/bin/zsh -lc "sed -n '1,58p' tests/js/fit_acceptance.test.js && nl -ba templates/index.html | sed -n '7412,7457p' && rg -n 'tempfile|TMPDIR|pytest.main|cacheprovider' docs/autofit/codex/f2_acceptance_holes_r2_verdict_runB.md | tail -12" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
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

  7412	// uncertainty that could not be computed, serialised as NaN (Flask writes
  7413	// NaN / Infinity tokens, which JSON.parse rejects).
  7414	async function _readFitReply(resp) {
  7415	  const text = await resp.text();                 // rejects only on transport
  7416	  try { return JSON.parse(text); } catch (_) {
  7417	    // A NaN / Infinity TOKEN, never the word inside a JSON string (Codex
  7418	    // round 1) — one linear pass that tracks string and escape state to the
  7419	    // end of the body, so a string cut off by a truncated body stays a string
  7420	    // and no body, however malformed, costs more than one scan (round 2: a
  7421	    // regex that blanked strings was quadratic on an unterminated escaped
  7422	    // string, 10 s for 128 KB on the page's thread).
  7423	    const nonFinite = (function (t) {
  7424	      const bound = ch => ch === undefined || ch === ' ' || ch === '\n' || ch === '\r' || ch === '\t' ||
  7425	        ch === ',' || ch === ':' || ch === '[' || ch === ']' || ch === '\x7b' || ch === '\x7d';   // \x7b \x7d = braces
  7426	      let inStr = false, esc = false;
  7427	      for (let i = 0; i < t.length; i++) {
  7428	        const ch = t[i];
  7429	        if (inStr) {
  7430	          if (esc) esc = false; else if (ch === '\\') esc = true; else if (ch === '"') inStr = false;
  7431	          continue;
  7432	        }
  7433	        if (ch === '"') { inStr = true; continue; }
  7434	        if (ch === 'N' && t.startsWith('NaN', i) && bound(t[i - 1]) && bound(t[i + 3])) return true;
  7435	        if (ch === 'I' && t.startsWith('Infinity', i) && (bound(t[i - 1]) || t[i - 1] === '-') && bound(t[i + 8])) return true;
  7436	      }
  7437	      return false;
  7438	    })(text);
  7439	    const err = new Error(nonFinite
  7440	      ? 'The server\'s reply contains a non-finite number (NaN or Infinity), usually an uncertainty that could not be computed because these data do not determine the model. The fit is treated as failed.'
  7441	      : 'The server\'s reply could not be read. The fit is treated as failed.');
  7442	    err.serverError = true;
  7443	    err.unreadableReply = true;
  7444	    throw err;
  7445	  }
  7446	}
  7447	
  7448	async function runAutoFitC1sGraphite() {
  7449	  // Pre-conditions
  7450	  if (!state.rawBE || !state.rawBE.length) { notify('Load a spectrum first.', 'amber'); return; }
  7451	  const tab = tabManager._getTab(tabManager.activeId);
  7452	  if (!tab) { notify('No active tab.', 'amber'); return; }
  7453	  if (!isC1sTab(tab)) {
  7454	    notify('Auto-Fit C1s Graphite is only available for C1s spectra (ROI midpoint 270–315 eV).', 'amber');
  7455	    return;
  7456	  }
  7457	  // OWNER FIRST: the confirmation below is an await; the tab that is active
22661:  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 256, in _mkstemp_inner
22986:#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
22988:#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
22991:#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
22994:#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
23169:        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
23171:      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
23174:      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
23177:      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
23702:/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"-q\", \"-s\", \"-p\", \"no:cacheprovider\", \"tests/test_fit_acceptance_holes.py\", \"-k\", \"not api_fit\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
23973:/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"-q\", \"-s\", \"-p\", \"no:cacheprovider\", \"tests/test_basinhopping_outcome.py\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
23976:import tempfile; tempfile.tempdir=\"/tmp\"

codex
The 71 parser, acceptance, and Auto-Fit tests pass. The scanner has no input-dependent backtracking, and the truncated-string regression passes. I’m checking escape parity and large bodies next; one possible remaining issue is a misleading diagnostic when `-Infinity` appears inside a malformed identifier.
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"-q\", \"-s\", \"-p\", \"no:cacheprovider\", \"tests/test_fit_acceptance_holes.py\", \"tests/test_basinhopping_outcome.py\", \"-k\", \"not api_fit\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
exec
/bin/zsh -lc "node --test --test-name-pattern='no degrees of freedom|noiseless Gaussian|acceptance rule' tests/js/local_lm_descent.test.js | tail -14 && git diff main..HEAD -- tests/js/stale_statistics.test.js tests/js/autofit_required.test.js tests/test_fit_reproducibility.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 130ms:
ok 3 - the local engine refuses a model with no degrees of freedom; one more point and it fits
  ---
  duration_ms: 27.16285
  type: 'test'
  ...
1..3
# tests 3
# suites 0
# pass 3
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 162.679707
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-BSfwxucM' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-rYTO0mEl' (errno=Operation not permitted)
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
/bin/zsh -lc "node -e '
const fs=require('\\''fs'\\''), assert=require('\\''assert'\\''), {performance}=require('\\''perf_hooks'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const source=html.slice(html.indexOf('\\''async function _readFitReply('\\''),html.indexOf('\\''\\nasync function runAutoFitC1sGraphite('\\''));
const read=new Function(source+'\\'';return _readFitReply'\\'')();
async function classify(s) {try{return {type:'\\''valid'\\'',value:await read({text:async()=>s})};}catch(e){assert(e.serverError&&e.unreadableReply);return {type:e.message.includes('\\''non-finite number'\\'')?'\\''nonfinite'\\'':'\\''unreadable'\\''};}}
(async()=>{
const cases=[['\\''NaN'\\'','\\''nonfinite'\\''],['\\''Infinity'\\'','\\''nonfinite'\\''],['\\''-Infinity'\\'','\\''nonfinite'\\''],['\\''[NaN]'\\'','\\''nonfinite'\\''],['\\''{\"x\":NaN}'\\'','\\''nonfinite'\\''],['\\''{Infinity:1}'\\'','\\''nonfinite'\\''],['\\''NaNx'\\'','\\''unreadable'\\''],['\\''xNaN'\\'','\\''unreadable'\\''],['\\''Infinityx'\\'','\\''unreadable'\\''],['\\''xInfinity'\\'','\\''unreadable'\\''],['\\''{\"m\":\"contains NaN in label'\\'','\\''unreadable'\\''],['\\''{\"x\":\"\\\\u004e\\\\u0061\\\\u004e\"'\\'','\\''unreadable'\\''],['\\''{\"x\":1e999}'\\'','\\''valid'\\''],['\\''{\"x\":Infinity}'\\'','\\''nonfinite'\\''],['\\''{\"x\":\"NaN\",\"v\":0}'\\'','\\''valid'\\'']];
for(const [s,want] of cases) assert.equal((await classify(s)).type,want,s);
for(let n=0;n<40;n++){
 const body='\\''{\"m\":\"'\\''+'\\''\\\\'\\''.repeat(n)+'\\''\",NaN'\\'';
 assert.equal((await classify(body)).type,n%2?'\\''unreadable'\\'':'\\''nonfinite'\\'',JSON.stringify(body));
 const valid=JSON.stringify({m:'\\''\\\\'\\''.repeat(n)+'\\''\"NaN Infinity \\\\u0022'\\'',v:42});
 assert.deepStrictEqual((await classify(valid)).value,JSON.parse(valid));
}
console.log('\\''classification cases'\\'',cases.length,'\\''escape and valid-body cases'\\'',80);
for(const s of ['\\''x-Infinity'\\'','\\''--Infinity'\\'','\\''{\"v\":foo-Infinity}'\\'']) console.log('\\''boundary probe'\\'',JSON.stringify(s),await classify(s));
for(const n of [128000,1000000,10000000]){
 const bodies={escaped:'\\''{\"m\":\"'\\''+'\\''\\\\\"'\\''.repeat(n/2),slashes:'\\''{\"m\":\"'\\''+'\\''\\\\'\\''.repeat(n),quotes:'\\''\"'\\''.repeat(n),digits:'\\''9'\\''.repeat(n),badDigits:'\\''9'\\''.repeat(n)+'\\''x'\\'',nearTokens:'\\''Infinityx '\\''.repeat(Math.ceil(n/10))};
 for(const [name,s] of Object.entries(bodies)){const t=performance.now(),r=await classify(s);console.log(name,s.length,r.type,(performance.now()-t).toFixed(1)+'\\''ms'\\'');}
}
})();'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 471ms:
escaped 10000006 unreadable 82.9ms
slashes 10000006 unreadable 79.1ms
quotes 10000000 unreadable 69.5ms
digits 10000000 valid 23.0ms
badDigits 10000001 unreadable 93.1ms
nearTokens 10000000 unreadable 116.7ms

 succeeded in 46450ms:
...........
11 passed, 1 deselected in 46.05s

exec
/bin/zsh -lc "node -e '
const fs=require('\\''fs'\\''),{execFileSync}=require('\\''child_process'\\''),assert=require('\\''assert'\\''),{performance}=require('\\''perf_hooks'\\'');
function extract(html){return html.slice(html.indexOf('\\''async function _readFitReply('\\''),html.indexOf('\\''\\nasync function runAutoFitC1sGraphite('\\''));}
const current=extract(fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\''));
const old=extract(execFileSync('\\''git'\\'',['\\''show'\\'','\\''a5a14a0:templates/index.html'\\''],{encoding:'\\''utf8'\\'',stdio:['\\''ignore'\\'','\\''pipe'\\'','\\''ignore'\\'']}));
(async()=>{
for(const [name,src] of [['\\''HEAD'\\'',current],['\\''round2-baseline'\\'',old]]){
 const read=new Function(src+'\\'';return _readFitReply'\\'')();
 try{await read({text:async()=>'\\''{\"message\":\"contains NaN in label'\\''});}catch(e){console.log(name,'\\''truncation assertion passes:'\\'',e.unreadableReply&&/could not be read/.test(e.message));}
 const big='\\''{\"m\":\"'\\''+'\\''\\\\\"'\\''.repeat(64000),t=performance.now();
 await assert.rejects(read({text:async()=>big}),e=>e.unreadableReply&&/could not be read/.test(e.message));
 console.log(name,'\\''stress duration'\\'',(performance.now()-t).toFixed(1)+'\\''ms'\\'','\\''<500:'\\'',performance.now()-t<500);
}
})();'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile; tempfile.tempdir=\"/tmp\"; from flask import Flask; app=Flask(__name__); print(app.json.dumps({\"x\":1e999}))' && rg -n \"_readFitReply|fetch\\(.*api/fit\" templates/index.html && git status --short" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 164ms:
{"x": Infinity}
7414:async function _readFitReply(resp) {
7562:    const resp = await fetch('/api/fit', {
7589:    const json = await _readFitReply(resp);   // F2: an unreadable reply is a failed fit with its own message
8058:      resp = await fetch('/api/fit', {
8075:    try { json = await _readFitReply(resp); } catch (e) { _asTransport(e); }
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-w1KDtPZ0' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-8fDPg4xL' (errno=Operation not permitted)
?? docs/autofit/codex/f2_acceptance_holes_r3_verdict_runA.md
?? docs/autofit/codex/f2_acceptance_holes_r3_verdict_runB.md

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
