OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0e1f8-0ace-7eb0-913e-5df895aeb5bf
--------
user
Re-review unit F2 (holes in the acceptance rule), round 4: branch fix-acceptance-holes. Round 3 was GO x2 with one MINOR from both runs (docs/autofit/codex/f2_acceptance_holes_r3_verdict_run{A,B}.md): a minus sign before Infinity counted in _readFitReply's non-finite scan without a boundary before it ("x-Infinity", "--Infinity" read as a non-finite number instead of an unreadable reply). The fix is the commit at HEAD (git diff HEAD~1..HEAD): the sign now needs a boundary before it; a regression test in tests/js/fit_acceptance.test.js. Earlier prompts (brief, sites, rounds 1-3): docs/autofit/codex/f2_acceptance_holes_review_prompt.txt, _recheck_prompt.txt, _recheck2_prompt.txt; plan docs/superpowers/plans/2026-09-26-f2-acceptance-holes.md section 5. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

TRY TO BREAK
a. The one-line change: every token position (start of body, after [ , : { whitespace, after a sign at the start of the body, "-Infinity" at t[0], "-" at i-1 with i-2 undefined), and that nothing else in the scanner or _readFitReply changed.
b. The regression test: real and non-vacuous (would fail on the round-3 code).
c. A last pass over the whole unit (git diff main..HEAD) for anything the earlier rounds could not see because of what they were shown.

Finish with VERDICT: GO or VERDICT: NO-GO.

codex
I’ll inspect the HEAD fix and prior review scope, test the token boundaries and regression test, then make a final pass over the full unit diff. I’ll keep the review read-only and finish with a verdict.

exec
/bin/zsh -lc "pwd; git status --short; rg --files -g AGENTS.md -g '*f2_acceptance_holes*' -g '*fit_acceptance*' -g '*2026-09-26-f2*'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-7bZu3ml6' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-DgAfLFUq' (errno=Operation not permitted)
?? docs/autofit/codex/f2_acceptance_holes_r4_verdict_runA.md
?? docs/autofit/codex/f2_acceptance_holes_r4_verdict_runB.md
docs/superpowers/plans/2026-09-26-f2-acceptance-holes.md
tests/test_fit_acceptance_holes.py
tests/js/fit_acceptance.test.js
docs/autofit/codex/f2_acceptance_holes_verdict_runB.md
docs/autofit/codex/f2_acceptance_holes_recheck2_prompt.txt
docs/autofit/codex/f2_acceptance_holes_r3_verdict_runA.md
docs/autofit/codex/f2_acceptance_holes_r4_verdict_runA.md
docs/autofit/codex/f2_acceptance_holes_r3_verdict_runB.md
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md
docs/autofit/codex/f2_acceptance_holes_r4_verdict_runB.md
docs/autofit/codex/f2_acceptance_holes_recheck3_prompt.txt
docs/autofit/codex/f2_acceptance_holes_r2_verdict_runB.md
docs/autofit/codex/f2_acceptance_holes_r2_verdict_runA.md
docs/autofit/codex/f2_acceptance_holes_review_prompt.txt
docs/autofit/codex/f2_acceptance_holes_recheck_prompt.txt

exec
/bin/zsh -lc 'cat docs/autofit/codex/f2_acceptance_holes_review_prompt.txt docs/autofit/codex/f2_acceptance_holes_recheck_prompt.txt docs/autofit/codex/f2_acceptance_holes_recheck2_prompt.txt docs/autofit/codex/f2_acceptance_holes_r3_verdict_runA.md docs/autofit/codex/f2_acceptance_holes_r3_verdict_runB.md docs/superpowers/plans/2026-09-26-f2-acceptance-holes.md; for p in /AGENTS.md /Users/AGENTS.md /Users/skyefortier/AGENTS.md /Users/skyefortier/xps-app/AGENTS.md /Users/skyefortier/xps-app/.claude/AGENTS.md /Users/skyefortier/xps-app/.claude/worktrees/AGENTS.md; do if test -f "$p"; then cat "$p"; fi; done' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
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

Finish with VERDICT: GO or VERDICT: NO-GO.OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0e1cc-d52b-72e0-95b2-089f8f4ccdd2
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
I’ll read the review brief and prior verdicts, inspect the round-2 diff, and probe the scanner’s failure cases and tests before issuing a verdict.
exec
/bin/zsh -lc "pwd; rg --files -g 'AGENTS.md' -g '*f2*' -g '*acceptance*' -g '*round*' docs . 2>/dev/null | head -100" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md
docs/superpowers/plans/2026-09-02-task1-background-residual-diagnosis.md
docs/superpowers/plans/2026-04-07-manual-spline-background.md
docs/superpowers/plans/2026-09-26-f2-acceptance-holes.md
docs/superpowers/plans/2026-09-02-task4-background-twin-parity.md
docs/comms/2026-09-03-background-window-fix-student-note.md
./tests/test_tougaard_background.py
./tests/test_browser_overlay_zip_roundtrip.py
./docs/superpowers/plans/2026-09-26-f2-acceptance-holes.md
./docs/superpowers/plans/2026-09-02-task4-background-twin-parity.md
./docs/superpowers/plans/2026-04-07-manual-spline-background.md
./docs/superpowers/plans/2026-09-02-task1-background-residual-diagnosis.md
./docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md
./docs/comms/2026-09-03-background-window-fix-student-note.md
./tests/test_fit_acceptance_holes.py
./tests/test_background_n_avg.py
./tests/autofit/test_browser_schema_roundtrip.py
./tests/js/fit_acceptance.test.js
./tests/js/shape_switch_roundtrip.test.js
./tests/js/lineshape_roundtrip_backend.py
./tests/js/lineshape_roundtrip.test.js
docs/autofit/codex/tooltip_markup_leak_verdict_round2_runA.md
docs/autofit/codex/f2_acceptance_holes_r3_verdict_runB.md
docs/autofit/codex/fp_periodic_table_picker_verdict_round1_runA.md
docs/autofit/codex/self_citation_removal_verdict_round1_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r11_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_recheck8_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_r5_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_recheck13_prompt.txt
docs/autofit/codex/plain_english_pass_verdict_round2_runA.md
docs/autofit/codex/full_window_crop_fix_verdict_round2_runB.md
docs/autofit/codex/c1s_badge_fix_verdict_round5_runA.md
docs/autofit/codex/f2_acceptance_holes_verdict_runA.md
docs/autofit/codex/self_citation_removal_verdict_round4_runB.md
docs/autofit/codex/a0_local_lm_acceptance_recheck5_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_r14_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r13_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r7_verdict_runA.md
docs/autofit/codex/plain_english_pass_verdict_round3_runA.md
docs/autofit/codex/a0_local_lm_acceptance_recheck16_prompt.txt
docs/autofit/codex/c1s_badge_fix_verdict_round4_runA.md
docs/autofit/codex/full_window_crop_fix_verdict_round3_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r19_verdict_runB.md
docs/autofit/codex/c1s_badge_fix_verdict_round1_runB.md
docs/autofit/codex/tooltip_markup_leak_verdict_round3_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r2_verdict_runB.md
docs/autofit/codex/region_provenance_honesty_verdict_round2_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r16_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r8_verdict_runA.md
docs/autofit/codex/fit_full_window_verdict_round1_runB.md
docs/autofit/codex/plain_english_pass_verdict_round1_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r12_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r6_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r18_verdict_runB.md
docs/autofit/codex/c1s_badge_fix_verdict_round6_runA.md
docs/autofit/codex/full_window_crop_fix_verdict_round1_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r3_verdict_runB.md
docs/autofit/codex/self_citation_removal_verdict_round2_runA.md
docs/autofit/codex/fp_periodic_table_picker_verdict_round2_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r17_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_recheck7_prompt.txt
docs/autofit/codex/tooltip_markup_leak_verdict_round1_runA.md
docs/autofit/codex/c1s_badge_fix_verdict_round3_runB.md
docs/autofit/codex/full_window_crop_fix_verdict_round4_runA.md
docs/autofit/codex/fit_full_window_verdict_round3_runB.md
docs/autofit/codex/a0_local_lm_acceptance_recheck11_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_r9_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r20_verdict_runA.md
docs/autofit/codex/region_provenance_honesty_verdict_round1_runA.md
docs/autofit/codex/self_citation_removal_verdict_round3_runA.md
docs/autofit/codex/a0_local_lm_acceptance_recheck2_prompt.txt
docs/autofit/codex/c1s_badge_fix_verdict_round2_runB.md
docs/autofit/codex/f2_acceptance_holes_r2_verdict_runB.md
docs/autofit/codex/fit_full_window_verdict_round2_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r10_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_recheck14_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_r4_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_recheck19_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_r15_verdict_runA.md
docs/autofit/codex/findpeaks_unit3_verdict_round2.md
docs/autofit/codex/region_provenance_honesty_verdict_round1_runB.md
docs/autofit/codex/self_citation_removal_verdict_round3_runB.md
docs/autofit/codex/a0_local_lm_acceptance_recheck17_prompt.txt
docs/autofit/codex/c1s_badge_fix_verdict_round2_runA.md
docs/autofit/codex/f2_acceptance_holes_r2_verdict_runA.md
docs/autofit/codex/fit_full_window_verdict_round2_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r10_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r4_verdict_runA.md
docs/autofit/codex/f2_acceptance_holes_review_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_r15_verdict_runB.md
docs/autofit/codex/f2_acceptance_holes_recheck_prompt.txt
docs/autofit/codex/findpeaks_unit3_verdict_round1.md
docs/autofit/codex/plain_english_pass_verdict_round1_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r12_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r6_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r18_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_recheck9_prompt.txt
docs/autofit/codex/c1s_badge_fix_verdict_round6_runB.md
docs/autofit/codex/full_window_crop_fix_verdict_round1_runA.md

exec
/bin/zsh -lc 'git status --short; git log -5 --oneline; git diff --stat a5a14a0..HEAD; git diff --stat main..HEAD' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 65ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-J1hxpzgD' (errno=Operation not permitted)
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
/bin/zsh -lc 'for p in /AGENTS.md /Users/AGENTS.md /Users/skyefortier/AGENTS.md /Users/skyefortier/xps-app/AGENTS.md /Users/skyefortier/xps-app/.claude/AGENTS.md /Users/skyefortier/xps-app/.claude/worktrees/AGENTS.md AGENTS.md; do if test -f "$p"; then cat "$p"; fi; done; rg --files -g AGENTS.md -g '"'package.json' -g 'pytest.ini' -g 'pyproject.toml' -g '*requirements*'; cat docs/autofit/codex/f2_acceptance_holes_review_prompt.txt; cat docs/superpowers/plans/2026-09-26-f2-acceptance-holes.md" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
requirements.txt
requirements-dev.txt
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
/bin/zsh -lc 'git diff a5a14a0..HEAD -- templates/index.html tests/js/fit_acceptance.test.js; git diff main..HEAD -- fitting.py templates/index.html; for f in docs/autofit/codex/f2_acceptance_holes_verdict_runA.md docs/autofit/codex/f2_acceptance_holes_verdict_runB.md docs/autofit/codex/f2_acceptance_holes_r2_verdict_runA.md docs/autofit/codex/f2_acceptance_holes_r2_verdict_runB.md; do tail -110 "$f"; done' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-BkdjXj1N' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-0gDBhxtC' (errno=Operation not permitted)
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
git: error: couldn't create cache file '/tmp/xcrun_db-HaJpfFWC' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-CcgvG2M9' (errno=Operation not permitted)
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
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"-q\",\"-s\",\"-p\",\"no:cacheprovider\",\"tests/test_fit_reproducibility.py\",\"-k\",\"stochastic_methods_get or differently_cased or seed_derivation_is_pinned or perturbation_draws_run_fit_makes_are_pinned\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c '
import tempfile; tempfile.tempdir=\"/tmp\"
import app,numpy as np
app._load_session=lambda *args:(np.array([283.,284.5,286.]),np.array([10.,100.,10.]))
a=app.create_app(); a.config[\"TESTING\"]=True
with a.test_client() as c:
    r=c.post(\"/api/analyze\",json=dict(session_id=\"a\"*32,method=\"least_squares\",material_class=\"conductor\",regions=[\"C 1s\"],peak_specs=[dict(id=\"1\",shape=\"gaussian\",center=284.5,amplitude=100,fwhm=1)],options={\"background_method\":\"none\"})); print(r.status_code,r.get_json())
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 1976ms:
/Users/skyefortier/.matplotlib is not a writable directory
400 {'error': 'ROI selects fewer than 20 points'}

exec
/bin/zsh -lc "git status --short; git branch --show-current; nl -ba templates/index.html | sed -n '7412,7428p'; rg -n 'n_perturb' fitting.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-iUd4GI5N' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-nxQPaXbA' (errno=Operation not permitted)
?? docs/autofit/codex/f2_acceptance_holes_verdict_runA.md
?? docs/autofit/codex/f2_acceptance_holes_verdict_runB.md
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-BoDkgH3n' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-JXzF2eEy' (errno=Operation not permitted)
fix-acceptance-holes
  7412	// uncertainty that could not be computed, serialised as NaN (Flask writes
  7413	// NaN / Infinity tokens, which JSON.parse rejects).
  7414	async function _readFitReply(resp) {
  7415	  const text = await resp.text();                 // rejects only on transport
  7416	  try { return JSON.parse(text); } catch (_) {
  7417	    const nonFinite = /(^|[\[,:\s])(-?Infinity|NaN)([\],\x7d\s]|$)/.test(text);   // \x7d = closing brace
  7418	    const err = new Error(nonFinite
  7419	      ? 'The server\'s reply contains a non-finite number (NaN or Infinity), usually an uncertainty that could not be computed because these data do not determine the model. The fit is treated as failed.'
  7420	      : 'The server\'s reply could not be read. The fit is treated as failed.');
  7421	    err.serverError = true;
  7422	    err.unreadableReply = true;
  7423	    throw err;
  7424	  }
  7425	}
  7426	
  7427	async function runAutoFitC1sGraphite() {
  7428	  // Pre-conditions
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
  1473	        f, required = None, True                     # the rest could not even be fitted without it
  1474	    elif delta <= 0:
  1475	        f, required = 0.0, False
  1476	    elif chi2_with == 0:
  1477	        f, required = None, True
  1478	    else:
  1479	        f = (delta / p) / (chi2_with / dof)
  1480	        required = f >= SUPPORT_MIN_F
  1481	    return {"required": bool(required), "f": f, "chi2_with": float(chi2_with), "chi2_without_refit": chi2_without,
  1482	            "refit_converged": bool(refit.success)}
  1483	
  1484	
  1485	# ─────────────────────────────────────────────────────────────────────────────
  1486	# Main fitting API
  1487	# ─────────────────────────────────────────────────────────────────────────────
  1488	
  // is necessary but not sufficient: with strong overlap the OTHER components
  // could absorb the anchor if refitted. The server refits without it when
  // asked (require_component) and reports whether that made the fit
  // significantly worse. A redundant anchor is refused the same way.
  const req = json && json.required;
  if (req && req.ran === true && req.required === false) {
    notify('Auto-fit: the Graphite component is not required by the data — refitting the other components without it fits the data as well' + (req.f != null ? ' (F = ' + Number(req.f).toFixed(1) + ', threshold 10)' : '') + '. No charge correction was derived from it and the fit was not applied. The model gives the other components enough freedom to absorb the graphite line; lock or narrow them and try again.', 'red', true);
    return false;
  }
  // F2 (2026-09-26): the refit without the anchor did not converge, so the
  // server could not establish that the anchor is required. The anchor would
  // set the energy reference of the whole spectrum: refused, like a
  // redundant one (a check that did not RUN at all still never blocks).
  if (req && req.ran === true && req.refit_converged === false) {
    notify('Auto-fit: it could not be established that the data require the Graphite component — refitting the other components without it did not converge. No charge correction was derived from it and the fit was not applied. Try Run Fit, or narrow the ROI, and run Auto-Fit again.', 'red', true);
    return false;
  }
  if (!_autoFitGraphiteIsSupported(gPeak, json)) {
    notify('Auto-fit: the data do not support the Graphite component (removing it does not worsen the fit), so no charge correction was derived from it and the fit was not applied.', 'red', true);
    return false;
  }
  // 2. Validate within ±0.3 of 284.50 (the LA center bound).
  if (Math.abs(gPeak.center - 284.50) > 0.30 + 1e-6) {
    notify('Fit failed to converge or produced an unphysical graphite position.', 'red', true);
rg: autofit/service.py: No such file or directory (os error 2)
rg: autofit/api.py: No such file or directory (os error 2)

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir=\"/tmp\"
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

exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '7412,7427p'; git status --short" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
  7412	// uncertainty that could not be computed, serialised as NaN (Flask writes
  7413	// NaN / Infinity tokens, which JSON.parse rejects).
  7414	async function _readFitReply(resp) {
  7415	  const text = await resp.text();                 // rejects only on transport
  7416	  try { return JSON.parse(text); } catch (_) {
  7417	    // a NaN / Infinity TOKEN, not the word inside a JSON string (Codex round 1)
  7418	    const unquoted = text.replace(/"(?:[^"\\]|\\.)*"/g, '""');
  7419	    const nonFinite = /(^|[\[,:\s])(-?Infinity|NaN)([\],\x7d\s]|$)/.test(unquoted);   // \x7d = closing brace
  7420	    const err = new Error(nonFinite
  7421	      ? 'The server\'s reply contains a non-finite number (NaN or Infinity), usually an uncertainty that could not be computed because these data do not determine the model. The fit is treated as failed.'
  7422	      : 'The server\'s reply could not be read. The fit is treated as failed.');
  7423	    err.serverError = true;
  7424	    err.unreadableReply = true;
  7425	    throw err;
  7426	  }
  7427	}
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-UKPGzhYM' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-njGgM33w' (errno=Operation not permitted)
?? docs/autofit/codex/f2_acceptance_holes_r2_verdict_runA.md
?? docs/autofit/codex/f2_acceptance_holes_r2_verdict_runB.md

exec
/bin/zsh -lc "node -e '
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
/bin/zsh -lc "git diff a5a14a0..HEAD -- templates/index.html tests/js/fit_acceptance.test.js; sed -n '1,300p' tests/js/fit_acceptance.test.js; sed -n '1,210p' tests/test_fit_acceptance_holes.py; sed -n '1,170p' tests/test_basinhopping_outcome.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-0xADl2HL' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-gWS9ioqa' (errno=Operation not permitted)
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

// ── Codex round-1 findings (2026-09-15): HTTP failures with non-JSON bodies ──

function envWithFetch(fetchImpl, uploadImpl) { return makeEnv({ fetchImpl, uploadImpl }); }

test('an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback', async () => {
  const env = envWithFetch(async () => ({ ok: false, status: 502, json: async () => { throw new SyntaxError('Unexpected token <'); } }));
  await env.runFit();
  assert.equal(env.calls.local, 0, 'no fallback on a 502');
  assert.equal(env.calls.applied, 0);
  assert.ok(env.calls.notify.some(n => n.kind === 'red' && /502/.test(n.msg)), JSON.stringify(env.calls.notify));
});

test('an HTTP 502 on the upload is a server failure, not a transport failure', async () => {
  const env = envWithFetch(async () => { throw new Error('fit must not be reached'); }, async () => { const e = new Error('Upload failed (HTTP 502).'); e.serverError = true; throw e; });
  await env.runFit();
  assert.equal(env.calls.local, 0);
  assert.ok(env.calls.notify.some(n => n.kind === 'red' && /502/.test(n.msg)));
});

test('uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id', async () => {
  const src = extractFn('uploadToBackend');
  const make = fetchImpl => new Function('fetch', 'FormData', 'Blob', src + '\nreturn uploadToBackend;')(fetchImpl, class { append() {} }, class {});
  await assert.rejects(make(async () => ({ ok: false, status: 502, json: async () => { throw new SyntaxError('<html>'); } }))([1], [1]), e => e.serverError === true && /502/.test(e.message));
  await assert.rejects(make(async () => ({ ok: true, status: 200, json: async () => ({}) }))([1], [1]), e => e.serverError === true && /session/i.test(e.message));
  await assert.rejects(make(async () => { throw new TypeError('Failed to fetch'); })([1], [1]), e => !e.serverError);
});

test('every consumer that prints the goodness-of-fit statistic routes through the statistic identity', () => {
  const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
  // figure export annotation
  const fig = grab('function exportFigure()', 60000);
  assert.match(fig, /_isLocalFit\(state\.fitResult\)/, 'figure export must label the statistic by engine');
  assert.match(fig, /Residual variance \(local fit, not reportable\)/, 'figure annotation names the legacy unweighted statistic');
  assert.match(fig, /\\u03c7\\u00b2_r \(local fit, not reportable\)/, 'figure annotation designates a weighted local chi-square');
  // fit-history rows
  const hist = grab('function _renderHistoryList(', 3000);
  assert.match(hist, /_fitStatLabel\(/, 'history rows must label the statistic by engine');
  // tab activation tooltip
  const act = grab("// Update chi-squared display for this tab's fit result", 300);
  assert.match(act, /_applyStatDisplay\(state\.fitResult\)/, 'tab activation refreshes the whole statistic display');
});

test('uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure', async () => {
  const src = extractFn('uploadToBackend');
  const make = fetchImpl => new Function('fetch', 'FormData', 'Blob', src + '\nreturn uploadToBackend;')(fetchImpl, class { append() {} }, class {});
  await assert.rejects(make(async () => ({ ok: true, status: 200, json: async () => null }))([1], [1]), e => e.serverError === true);
  await assert.rejects(make(async () => ({ ok: true, status: 200, json: async () => 'nope' }))([1], [1]), e => e.serverError === true);
});

test('a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown', () => {
  const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
  // Results panel banner, keyed on the statistic identity
  const rr = grab('function renderResults()', 6000);
  assert.match(rr, /starting point/i, 'results panel must say the local result is a starting point');
  assert.match(rr, /Run Fit/, 'results panel must tell the user to press Run Fit');
  // batch summary rows
  const rp = grab('async function runPropagation', 9000);
  assert.match(rp, /starting point/i, 'batch summary must say converged rows are starting points');
  // table exports carry the warning
  const ex = grab('function exportFitTable(fmt)', 6000);
  assert.match(ex, /_localFitCaveat\(state\.fitResult\)/, 'CSV/XLSX export must carry the designation text for a local result');
  // figure annotation
  const fig = grab('function exportFigure()', 60000);
  assert.match(fig, /local fit, not reportable/i, 'figure annotation must say not reportable');
  // local-fit overlay
  assert.match(html, /id="localfit-warn-overlay"[\s\S]{0,1500}starting point/i, 'overlay must say starting point');
});

// ── Codex round-7: the starting-point designation at every site, behaviourally ──
test('starting-point helpers: keyed on the persisted objective, weighted results untouched', () => {
  const src = ['_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_localFitCaveat', '_fitStatusText'].map(extractFn).join('\n');
  const constLine = [html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n')]; assert.ok(constLine[0], '_LOCAL_FIT_CAVEAT constants');
  const h = new Function(constLine[0] + '\n' + src + '\nreturn { _fitStatLabel, _isLocalFit, _localFitCaveat, _fitStatusText };')();
  const local = { objective: 'unweighted_residual_variance', chiReduced: 34523.31 };
  const reloaded = { objective: 'unweighted_residual_variance', chiReduced: 1.5 };   // engine field absent, as older saves may be
  const weighted = { chiReduced: 4.97 };
  assert.equal(h._isLocalFit(local), true); assert.equal(h._isLocalFit(reloaded), true); assert.equal(h._isLocalFit(weighted), false);
  assert.match(h._localFitCaveat(local), /starting point, not a reportable result/i);
  assert.equal(h._localFitCaveat(weighted), '');
  assert.match(h._fitStatusText(local), /^Residual variance = 34523\.31 \(starting point\)$/);
  assert.match(h._fitStatusText(weighted), /^χ²ᵣ = 4\.97$/);
});

test('Quantify shows the starting-point banner for a local result and not for a weighted one', () => {
  const src = 'const _UNSUPPORTED_LABEL = "not supported by the data"; const _UNSUPPORTED_TIP = "";\n' + ['renderQuantify', '_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_localFitCaveat', '_isUnsupported'].map(extractFn).join('\n');
  const constLine = html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n');
  const rsf = html.match(/^const SCOFIELD_RSF = \{[\s\S]*?^\};/m); assert.ok(rsf, 'SCOFIELD_RSF table');
  const run = (fitResult) => {
    const el = { innerHTML: '', _rsfSource: 'scofield' };
    const document = { getElementById: () => el, querySelectorAll: () => [] };
    const state = { fitResult, peaks: [{ id: 1, name: 'C 1s', shape: 'Gaussian', center: 284.8, fwhm: 1, amplitude: 10, rsfKey: 'C 1s' }] };
    new Function('document', 'state', '_escHtml', '_detectPeakRSF', 'recalcQuantify', constLine + '\n' + rsf[0] + '\n' + src + '\nrenderQuantify([100], 100);')(
      document, state, s => String(s), () => ({ key: 'C 1s', rsf: 1 }), () => {});
    return el.innerHTML;
  };
  assert.match(run({ objective: 'unweighted_residual_variance', chiReduced: 3e4 }), /starting point, not a reportable result/i);
  assert.doesNotMatch(run({ chiReduced: 2.0 }), /starting point/i);
});

test('every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels', () => {
  const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
  assert.match(grab('function exportResults()', 2500), /_LOCAL_FIT_CAVEAT|_localFitCaveat\(/, 'TSV export');
  assert.match(grab('function _doSaveSpectrum()', 2500), /caveat: _localFitCaveat\(state\.fitResult\) \|\| state\.fitResult\.caveat/, 'spectrum save persists caveat');
  assert.match(grab('function _doSaveSpectrum()', 2500), /reportable: _isLocalFit\(state\.fitResult\) \? false : \(state\.fitResult\.reportable/, 'spectrum save persists reportable');
  assert.match(grab('const buildTabData = (t) =>', 3500), /caveat: _localFitCaveat\(t\.fitResult\) \|\| t\.fitResult\.caveat/, 'project save persists caveat');
  assert.match(grab('function _loadSpectrumFile(', 6000), /'caveat'/, 'spectrum load restores caveat');
  assert.match(grab("// Update chi-squared display for this tab's fit result", 300), /_applyStatDisplay\(/, 'tab activation');
  assert.match(html, /id="sb-chi-caption"/, 'status-bar caption element');
  assert.match(grab('function _renderHistoryList(', 3000), /starting point/, 'history rows');
  assert.match(grab("label: _isLocalModel() ? 'Fit (local, starting point)' : 'Fit'", 100), /Fit \(local/, 'chart envelope label');
  const fig = grab('function exportFigure()', 60000);
  assert.match(fig, /label: _isLocalModel\(\) \? 'Fit \(local, starting point\)' : 'Fit'/, 'figure legend label');
  // the local fit result itself declares it
  const rfl = grab('function runFitLocal(', 20000);
  assert.match(rfl, /reportable: false, caveat: _LOCAL_FIT_CAVEAT/, 'runFitLocal marks its result');
});

// ── Codex round-8: stack/preview labels, save-time normalisation, auto-fit caption ──
test('project save derives the designation from the objective for an older local result lacking the new fields', () => {
  const start = html.indexOf('const buildTabData = (t) =>'); assert.ok(start > 0);
  let depth = 0, seen = false, end = -1;
  for (let i = start; i < html.length; i++) { const ch = html[i]; if (ch === '{') { depth++; seen = true; } else if (ch === '}') { depth--; if (seen && depth === 0) { end = i + 1; break; } } }
  const src = html.slice(start, end) + ';';
  const constLine = html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg).join('\n');
  const fieldsAt = lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS'));
  const helpers = lines.slice(fieldsAt, lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\n' + ['_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_localFitCaveat', '_startsForSave', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent', '_startsModelKey', '_startsRecordKey', '_statsState', '_statsRecordState', '_statsNote', '_statsSaveFields'].map(extractFn).join('\n');
  const statsConsts = html.match(/^const _STATS_\w+_NOTE = .*$/mg).join('\n');
  const build = new Function('RefCore', '_roundBE', '_roundIntensity', constLine + '\n' + statsConsts + '\n' + helpers + '\n' + src + '\nreturn buildTabData;')(
    { serializeRefOverlays: () => null }, a => a, a => a);
  const older = { id: 1, name: 't', rawBE: [1, 2], rawIntensity: [1, 1], ccShift: 0, peaks: [], nextId: 1, ui: {},
    fitResult: { chi: 1, chiReduced: 1e4, rmse: 100, objective: 'unweighted_residual_variance', be: [1, 2], bgIntensity: [0, 0], bgSubtracted: [1, 1] } };
  const rec = build(older);
  assert.strictEqual(rec.fitResult.reportable, false);
  assert.match(rec.fitResult.caveat, /starting point, not a reportable result/i);
  const weighted = { ...older, fitResult: { chi: 1, chiReduced: 2, rmse: 100, be: [1, 2], bgIntensity: [0, 0], bgSubtracted: [1, 1] } };
  assert.strictEqual(build(weighted).fitResult.reportable, null);
  assert.strictEqual(build(weighted).fitResult.caveat, null);
});

test('stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately', () => {
  const grab = (sig, len) => { const i = html.indexOf(sig); assert.ok(i > 0, sig); return html.slice(i, i + len); };
  assert.match(html, /_isLocalFit\(src\.fitResult\) \? ' \(fit: local, starting point\)' : ' \(fit\)'/, 'stack envelope dataset label');
  assert.match(html, /local fit: starting point/, 'stack legend row name');
  assert.match(html, /label: _isLocalFit\(_historyPreview\.fitResult\) \? 'Preview \(local, starting point\)' : 'Preview'/, 'history preview label');
  assert.match(grab('function applyAutoFitResult(', 12000), /_applyStatDisplay\(state\.fitResult\)/, 'auto-fit refreshes the statistic display');
  assert.match(grab('function renderResults()', 800), /_applyStatDisplay\(state\.fitResult\)/, 'renderResults refreshes the statistic display on every result change');
  const spec = grab('function _doSaveSpectrum()', 3000);
  assert.match(spec, /reportable: _isLocalFit\(state\.fitResult\) \? false/, 'spectrum save derives reportable');
  assert.match(spec, /caveat: _localFitCaveat\(state\.fitResult\)/, 'spectrum save derives caveat');
  const ex = grab('function exportFitTable(fmt)', 6000);
  const xlsxPart = ex.slice(ex.indexOf("if (fmt === 'xlsx')"), ex.indexOf('} else {'));
  const csvPart = ex.slice(ex.indexOf('} else {'));
  assert.match(xlsxPart, /WARNING/, 'XLSX warning row');
  assert.match(csvPart, /# WARNING/, 'CSV warning line');
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

codex
The round-2 code change is confined to the reply-diagnosis scanner. Its loop advances once per character and handles escaped quotes and strings truncated at EOF. I’m checking token boundaries and large inputs now, then running the affected tests and checking that they detect the old bugs.
exec
/bin/zsh -lc "git diff main..HEAD -- fitting.py templates/index.html; sed -n '1,200p' tests/conftest.py; rg -n 'parity|python|spawn|mkdtemp' tests/js/local_lm_descent.test.js; ls -ld /Users/skyefortier/xps-app/venv/bin/python" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-l40Gy0w9' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-cx3wrAXL' (errno=Operation not permitted)
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
"""Make the repo root importable regardless of how pytest is invoked."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
71:  const py = fs.existsSync(path.join(REPO_ROOT, 'venv/bin/python3')) ? path.join(REPO_ROOT, 'venv/bin/python3')
72:    : (fs.existsSync('/Users/skyefortier/xps-app/venv/bin/python3') ? '/Users/skyefortier/xps-app/venv/bin/python3' : 'python3');
455:test('server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)', () => {
457:  const bridge = path.join(__dirname, 'local_lm_server_parity_backend.py');
458:  const py = fs.existsSync(path.join(REPO_ROOT, 'venv/bin/python3')) ? path.join(REPO_ROOT, 'venv/bin/python3')
459:    : (fs.existsSync('/Users/skyefortier/xps-app/venv/bin/python3') ? '/Users/skyefortier/xps-app/venv/bin/python3' : 'python3');
lrwxr-xr-x  1 skyefortier  staff  10 May  7 11:22 /Users/skyefortier/xps-app/venv/bin/python -> python3.12

exec
/bin/zsh -lc 'node --test tests/js/fit_acceptance.test.js tests/js/autofit_required.test.js tests/js/stale_statistics.test.js tests/js/local_lm_descent.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 exited 1 in 6089ms:
# Subtest: a supported but NOT required anchor is refused before any charge-correction input is touched
ok 1 - a supported but NOT required anchor is refused before any charge-correction input is touched
  ---
  duration_ms: 5.218786
  type: 'test'
  ...
# Subtest: a required anchor proceeds; a check that did not RUN (older server, error, main fit not converged) does not block
ok 2 - a required anchor proceeds; a check that did not RUN (older server, error, main fit not converged) does not block
  ---
  duration_ms: 8.209353
  type: 'test'
  ...
# Subtest: the request asks for the Graphite anchor by id, and the gate precedes the support gate and every cc write
ok 3 - the request asks for the Graphite anchor by id, and the gate precedes the support gate and every cc write
  ---
  duration_ms: 0.899284
  type: 'test'
  ...
# Subtest: a refit that did not converge: no verdict, and Auto-Fit refuses before any charge-correction input is touched
ok 4 - a refit that did not converge: no verdict, and Auto-Fit refuses before any charge-correction input is touched
  ---
  duration_ms: 2.043083
  type: 'test'
  ...
# Subtest: A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
ok 5 - A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
  ---
  duration_ms: 10.452053
  type: 'test'
  ...
# Subtest: a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
ok 6 - a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
  ---
  duration_ms: 6.881892
  type: 'test'
  ...
# Subtest: a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
ok 7 - a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
  ---
  duration_ms: 2.809382
  type: 'test'
  ...
# Subtest: a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
ok 8 - a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
  ---
  duration_ms: 8.064304
  type: 'test'
  ...
# Subtest: a converged backend result is applied (sanity)
ok 9 - a converged backend result is applied (sanity)
  ---
  duration_ms: 2.807539
  type: 'test'
  ...
# Subtest: the engine/objective labels of a fit result survive spectrum and project save/load
ok 10 - the engine/objective labels of a fit result survive spectrum and project save/load
  ---
  duration_ms: 0.655973
  type: 'test'
  ...
# Subtest: an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
ok 11 - an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
  ---
  duration_ms: 2.667612
  type: 'test'
  ...
# Subtest: an HTTP 502 on the upload is a server failure, not a transport failure
ok 12 - an HTTP 502 on the upload is a server failure, not a transport failure
  ---
  duration_ms: 2.430604
  type: 'test'
  ...
# Subtest: uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
ok 13 - uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
  ---
  duration_ms: 1.513607
  type: 'test'
  ...
# Subtest: every consumer that prints the goodness-of-fit statistic routes through the statistic identity
ok 14 - every consumer that prints the goodness-of-fit statistic routes through the statistic identity
  ---
  duration_ms: 0.772518
  type: 'test'
  ...
# Subtest: uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
ok 15 - uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
  ---
  duration_ms: 1.051118
  type: 'test'
  ...
# Subtest: a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
ok 16 - a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
  ---
  duration_ms: 1.284079
  type: 'test'
  ...
# Subtest: starting-point helpers: keyed on the persisted objective, weighted results untouched
ok 17 - starting-point helpers: keyed on the persisted objective, weighted results untouched
  ---
  duration_ms: 2.709152
  type: 'test'
  ...
# Subtest: Quantify shows the starting-point banner for a local result and not for a weighted one
ok 18 - Quantify shows the starting-point banner for a local result and not for a weighted one
  ---
  duration_ms: 4.007266
  type: 'test'
  ...
# Subtest: every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
ok 19 - every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
  ---
  duration_ms: 1.479774
  type: 'test'
  ...
# Subtest: project save derives the designation from the objective for an older local result lacking the new fields
ok 20 - project save derives the designation from the objective for an older local result lacking the new fields
  ---
  duration_ms: 6.65727
  type: 'test'
  ...
# Subtest: stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
ok 21 - stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
  ---
  duration_ms: 0.959395
  type: 'test'
  ...
# Subtest: _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
ok 22 - _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
  ---
  duration_ms: 2.875319
  type: 'test'
  ...
# Subtest: history preview glow is keyed on the dataset flag, not the label text
ok 23 - history preview glow is keyed on the dataset flag, not the label text
  ---
  duration_ms: 0.544901
  type: 'test'
  ...
# Subtest: spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
ok 24 - spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
  ---
  duration_ms: 0.390759
  type: 'test'
  ...
# Subtest: _applyStatDisplay clears header, tooltip, caption and value together on local → none
ok 25 - _applyStatDisplay clears header, tooltip, caption and value together on local → none
  ---
  duration_ms: 2.784968
  type: 'test'
  ...
# Subtest: _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
ok 26 - _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
  ---
  duration_ms: 1.335721
  type: 'test'
  ...
# Subtest: fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
ok 27 - fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
  ---
  duration_ms: 1.181525
  type: 'test'
  ...
# Subtest: undo/redo snapshots carry and restore model provenance
ok 28 - undo/redo snapshots carry and restore model provenance
  ---
  duration_ms: 3.119761
  type: 'test'
  ...
# Subtest: round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
ok 29 - round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
  ---
  duration_ms: 0.979555
  type: 'test'
  ...
# Subtest: _provenanceOf derives a designation from a live local result, and undo snapshots use it
ok 30 - _provenanceOf derives a designation from a live local result, and undo snapshots use it
  ---
  duration_ms: 2.393739
  type: 'test'
  ...
# Subtest: batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
ok 31 - batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
  ---
  duration_ms: 0.348913
  type: 'test'
  ...
# Subtest: the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
ok 32 - the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
  ---
  duration_ms: 2.30874
  type: 'test'
  ...
# Subtest: round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
ok 33 - round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
  ---
  duration_ms: 0.571288
  type: 'test'
  ...
# Subtest: the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
ok 34 - the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
  ---
  duration_ms: 2.260802
  type: 'test'
  ...
# Subtest: the sidebar banner is sticky at the top of the scrolling panel body
ok 35 - the sidebar banner is sticky at the top of the scrolling panel body
  ---
  duration_ms: 0.238025
  type: 'test'
  ...
# Subtest: the sidebar banner shows on a stack tab whose visible entries draw a local source fit
ok 36 - the sidebar banner shows on a stack tab whose visible entries draw a local source fit
  ---
  duration_ms: 2.463178
  type: 'test'
  ...
# Subtest: every stack chart repaint path refreshes the sidebar designation before any early return
ok 37 - every stack chart repaint path refreshes the sidebar designation before any early return
  ---
  duration_ms: 0.422019
  type: 'test'
  ...
# Subtest: closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
ok 38 - closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
  ---
  duration_ms: 0.165648
  type: 'test'
  ...
# Subtest: W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
ok 39 - W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
  ---
  duration_ms: 2.849524
  type: 'test'
  ...
# Subtest: TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
ok 40 - TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
  ---
  duration_ms: 3.708184
  type: 'test'
  ...
# Subtest: adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
ok 41 - adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
  ---
  duration_ms: 2.864803
  type: 'test'
  ...
# Subtest: adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
ok 42 - adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
  ---
  duration_ms: 2.387874
  type: 'test'
  ...
# Subtest: adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
ok 43 - adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
  ---
  duration_ms: 2.893002
  type: 'test'
  ...
# Subtest: adoption: success records the choice, the starts evidence and the key of the model it describes
ok 44 - adoption: success records the choice, the starts evidence and the key of the model it describes
  ---
  duration_ms: 3.266308
  type: 'test'
  ...
# Subtest: an ordinary Run Fit on one unlinked component does not ask for the starts check
ok 45 - an ordinary Run Fit on one unlinked component does not ask for the starts check
  ---
  duration_ms: 3.271297
  type: 'test'
  ...
# Subtest: a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
ok 46 - a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
  ---
  duration_ms: 3.511222
  type: 'test'
  ...
# Subtest: a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
ok 47 - a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
  ---
  duration_ms: 4.931578
  type: 'test'
  ...
# Subtest: a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
ok 48 - a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
  ---
  duration_ms: 2.63079
  type: 'test'
  ...
# Subtest: a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
ok 49 - a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
  ---
  duration_ms: 4.677695
  type: 'test'
  ...
# Subtest: the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)
ok 50 - the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)
  ---
  duration_ms: 0.743742
  type: 'test'
  ...
# Subtest: the token scan is linear and keeps a truncated string a string (Codex round 2)
ok 51 - the token scan is linear and keeps a truncated string a string (Codex round 2)
  ---
  duration_ms: 3.569969
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
ok 52 - A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
  ---
  duration_ms: 1315.992508
  type: 'test'
  ...
# Subtest: A01 replay: the linked U 4f pair also descends
ok 53 - A01 replay: the linked U 4f pair also descends
  ---
  duration_ms: 249.42846
  type: 'test'
  ...
# Subtest: noiseless Gaussian: amplitude 10 started at 5 is recovered
ok 54 - noiseless Gaussian: amplitude 10 started at 5 is recovered
  ---
  duration_ms: 11.821354
  type: 'test'
  ...
# Subtest: acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
ok 55 - acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
  ---
  duration_ms: 9.292768
  type: 'test'
  ...
# Subtest: a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
ok 56 - a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
  ---
  duration_ms: 11.133952
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
ok 57 - bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
  ---
  duration_ms: 8.845608
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
ok 58 - bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
  ---
  duration_ms: 8.697828
  type: 'test'
  ...
# Subtest: a weak component the data DO hold is no longer forced up to an amplitude of 1
ok 59 - a weak component the data DO hold is no longer forced up to an amplitude of 1
  ---
  duration_ms: 8.944827
  type: 'test'
  ...
# Subtest: derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
ok 60 - derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
  ---
  duration_ms: 41.385515
  type: 'test'
  ...
# Subtest: derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
ok 61 - derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
  ---
  duration_ms: 24.696168
  type: 'test'
  ...
# Subtest: a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
ok 62 - a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
  ---
  duration_ms: 8.966221
  type: 'test'
  ...
# Subtest: linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
ok 63 - linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
  ---
  duration_ms: 13.376362
  type: 'test'
  ...
# Subtest: round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
ok 64 - round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
  ---
  duration_ms: 12.024121
  type: 'test'
  ...
# Subtest: round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
ok 65 - round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
  ---
  duration_ms: 9.515052
  type: 'test'
  ...
# Subtest: round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
ok 66 - round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
  ---
  duration_ms: 10.71232
  type: 'test'
  ...
# Subtest: A01 replay targets converge to constrained stationary points (C1s and U 4f)
ok 67 - A01 replay targets converge to constrained stationary points (C1s and U 4f)
  ---
  duration_ms: 1364.830732
  type: 'test'
  ...
# Subtest: round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
ok 68 - round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
  ---
  duration_ms: 59.7718
  type: 'test'
  ...
# Subtest: round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
ok 69 - round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
  ---
  duration_ms: 21.11947
  type: 'test'
  ...
# Subtest: round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
ok 70 - round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
  ---
  duration_ms: 13.152439
  type: 'test'
  ...
# Subtest: round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
ok 71 - round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
  ---
  duration_ms: 86.442568
  type: 'test'
  ...
# Subtest: round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
ok 72 - round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
  ---
  duration_ms: 1205.292307
  type: 'test'
  ...
# Subtest: round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
ok 73 - round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
  ---
  duration_ms: 24.035096
  type: 'test'
  ...
# Subtest: round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
ok 74 - round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
  ---
  duration_ms: 11.478565
  type: 'test'
  ...
# Subtest: weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
ok 75 - weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
  ---
  duration_ms: 10.034843
  type: 'test'
  ...
# Subtest: server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
not ok 76 - server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
  ---
  duration_ms: 1360.003513
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
ok 77 - the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom
  ---
  duration_ms: 22.625957
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
ok 78 - an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
  ---
  duration_ms: 24.339297
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
ok 79 - an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
  ---
  duration_ms: 19.787813
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
ok 80 - round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
  ---
  duration_ms: 8.332456
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
ok 81 - round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
  ---
  duration_ms: 8.330654
  type: 'test'
  ...
# Subtest: recovery from an amplitude of exactly zero (the new floor is not a trap)
ok 82 - recovery from an amplitude of exactly zero (the new floor is not a trap)
  ---
  duration_ms: 9.939918
  type: 'test'
  ...
# Subtest: the local engine refuses a model with no degrees of freedom; one more point and it fits
ok 83 - the local engine refuses a model with no degrees of freedom; one more point and it fits
  ---
  duration_ms: 24.632499
  type: 'test'
  ...
# Subtest: one accessor classifies a result against a key: none / unverified / current / stale
ok 84 - one accessor classifies a result against a key: none / unverified / current / stale
  ---
  duration_ms: 15.885557
  type: 'test'
  ...
# Subtest: the key is the step (b) key: F1 adds no second binding mechanism and no new key field
ok 85 - the key is the step (b) key: F1 adds no second binding mechanism and no new key field
  ---
  duration_ms: 4.316042
  type: 'test'
  ...
# Subtest: Results panel, current: statistic, RMSE, R and sigma are shown
ok 86 - Results panel, current: statistic, RMSE, R and sigma are shown
  ---
  duration_ms: 10.272813
  type: 'test'
  ...
# Subtest: Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
ok 87 - Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
  ---
  duration_ms: 7.067754
  type: 'test'
  ...
# Subtest: Results panel, unverified (older save, no key): values shown with a plain note
ok 88 - Results panel, unverified (older save, no key): values shown with a plain note
  ---
  duration_ms: 6.969869
  type: 'test'
  ...
# Subtest: status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
ok 89 - status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
  ---
  duration_ms: 6.284885
  type: 'test'
  ...
# Subtest: the stored fitted curve is never drawn, saved or stacked as the fit once stale
ok 90 - the stored fitted curve is never drawn, saved or stacked as the fit once stale
  ---
  duration_ms: 2.631952
  type: 'test'
  ...
# Subtest: saves keep the key and say plainly when the statistics are stale or unverified
ok 91 - saves keep the key and say plainly when the statistics are stale or unverified
  ---
  duration_ms: 2.085679
  type: 'test'
  ...
# Subtest: CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
ok 92 - CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
  ---
  duration_ms: 12.35103
  type: 'test'
  ...
# Subtest: XLSX: stale writes a WARNING row instead of the statistic, and no sigma
ok 93 - XLSX: stale writes a WARNING row instead of the statistic, and no sigma
  ---
  duration_ms: 4.566119
  type: 'test'
  ...
# Subtest: TSV: stale says the Model / Residual columns are the current, unfitted model
ok 94 - TSV: stale says the Model / Residual columns are the current, unfitted model
  ---
  duration_ms: 6.752775
  type: 'test'
  ...
# Subtest: the refresh re-renders Results only when its rendered state differs
ok 95 - the refresh re-renders Results only when its rendered state differs
  ---
  duration_ms: 2.678717
  type: 'test'
  ...
# Subtest: an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
ok 96 - an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
  ---
  duration_ms: 2.598009
  type: 'test'
  ...
# Subtest: Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
ok 97 - Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
  ---
  duration_ms: 3.125917
  type: 'test'
  ...
# Subtest: Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
ok 98 - Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
  ---
  duration_ms: 7.040218
  type: 'test'
  ...
# Subtest: closing the last tab clears the Results panel, header and status statistics too
ok 99 - closing the last tab clears the Results panel, header and status statistics too
  ---
  duration_ms: 0.169488
  type: 'test'
  ...
# Subtest: reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
ok 100 - reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
  ---
  duration_ms: 1.543867
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back
ok 101 - F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back
  ---
  duration_ms: 4.180411
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a Cloudflare 524 (plain-text body) is a failed request with its status, never "could not be read"
ok 102 - F2: Auto-Fit on a Cloudflare 524 (plain-text body) is a failed request with its status, never "could not be read"
  ---
  duration_ms: 3.814953
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a 500 with a JSON error is a failed request with its status, never "could not be read"
ok 103 - F2: Auto-Fit on a 500 with a JSON error is a failed request with its status, never "could not be read"
  ---
  duration_ms: 2.556186
  type: 'test'
  ...
1..103
# tests 103
# suites 0
# pass 102
# fail 1
# cancelled 0
# skipped 0
# todo 0
# duration_ms 6145.607227

exec
/bin/zsh -lc "node -e '
const fs=require('\\''fs'\\''), assert=require('\\''assert'\\'');
const h=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const src=h.slice(h.indexOf('\\''async function _readFitReply('\\''),h.indexOf('\\''async function runAutoFitC1sGraphite('\\''));
const read=new Function(src+'\\'';return _readFitReply'\\'')();
async function probe(t){try{const val=await read({text:async()=>t});return {kind:'\\''parsed'\\'',val}}catch(e){assert(e.serverError&&e.unreadableReply);return {kind:e.message.includes('\\''non-finite number'\\'')?'\\''nonfinite'\\'':'\\''unreadable'\\''}}}
(async()=>{
const cases=['\\''NaN'\\'','\\''Infinity'\\'','\\''-Infinity'\\'','\\''[NaN]'\\'','\\''{\"a\":NaN}'\\'','\\''NaNx'\\'','\\''[NaNx]'\\'','\\''xInfinity'\\'','\\''x-Infinity'\\'','\\''--Infinity'\\'','\\''[1-Infinity]'\\'','\\''{Infinity:1}'\\'','\\''{\"Infinity\":1}'\\'','\\''{\"m\":\"contains NaN in label'\\'','\\''{\"a\":1e999}'\\'','\\''{\"a\":Infinity}'\\''];
for(const t of cases) console.log(JSON.stringify(t),await probe(t));
for(let n=0;n<8;n++){
 const closed='\\''{\"a\":\"x'\\''+'\\''\\\\'\\''.repeat(n)+'\\''\", \"v\":NaN}'\\'';
 console.log('\\''backslashes'\\'',n,await probe(closed));
 assert.equal((await probe(closed)).kind,n%2?'\\''unreadable'\\'':'\\''nonfinite'\\'');
}
for(const t of ['\\''{\"a\":\"\\\\u0022 NaN'\\'','\\''{\"a\":\"\\\\u005c\", \"v\":NaN}'\\'']) console.log(JSON.stringify(t),await probe(t));
for(const [name,maker] of [ ['\\''escaped unterminated'\\'',n=>'\\''{\"m\":\"'\\''+'\\''\\\\\"'\\''.repeat(n/2)],['\\''backslashes in string'\\'',n=>'\\''\"'\\''+'\\''\\\\'\\''.repeat(n)+'\\'' NaN'\\''],['\\''quotes'\\'',n=>'\\''\"'\\''.repeat(n)],['\\''digits valid'\\'',n=>'\\''1'\\''.repeat(n)],['\\''digits invalid'\\'',n=>'\\''1'\\''.repeat(n)+'\\''x'\\''],['\\''tokens with suffix'\\'',n=>'\\'' NaNx'\\''.repeat(n/5)] ]) {
for(const size of [128000,1024000,10485760]){const t=maker(size);const start=performance.now();const r=await probe(t);console.log(name,t.length,(performance.now()-start).toFixed(2)+'\\'' ms'\\'',r.kind)}}
})();'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile
tempfile.tempdir=\"/tmp\"
import pytest
raise SystemExit(pytest.main([\"-q\",\"-p\",\"no:cacheprovider\",\"tests/test_fit_acceptance_holes.py\",\"tests/test_basinhopping_outcome.py\",\"-k\",\"not test_api_fit_returns\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 exited 1 in 106ms:
Traceback (most recent call last):
  File "<string>", line 4, in <module>
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
PermissionError: [Errno 1] Operation not permitted: '/tmp/tmpbjrs3nsu'

 succeeded in 489ms:
escaped unterminated 10485766 82.05 ms unreadable
backslashes in string 128005 1.60 ms unreadable
backslashes in string 1024005 8.54 ms unreadable
backslashes in string 10485765 86.25 ms unreadable
quotes 128000 0.85 ms unreadable
quotes 1024000 6.92 ms unreadable
quotes 10485760 67.10 ms unreadable
digits valid 128000 0.25 ms parsed
digits valid 1024000 2.66 ms parsed
digits valid 10485760 26.61 ms parsed
digits invalid 128001 1.22 ms unreadable
digits invalid 1024001 10.54 ms unreadable
digits invalid 10485761 96.23 ms unreadable
tokens with suffix 128000 1.73 ms unreadable
tokens with suffix 1024000 11.77 ms unreadable
tokens with suffix 10485760 123.28 ms unreadable

exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '7414,7448p'; sed -n '600,730p' tests/js/fit_acceptance.test.js; sed -n '200,360p' tests/test_fit_reproducibility.py; tail -30 docs/autofit/codex/f2_acceptance_holes_verdict_runA.md; rg -n '/api/fit|_readFitReply' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
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
    base = _seed(x, y, specs)
    assert base == _seed(x.copy(), y.copy(), json.loads(json.dumps(specs)))
    # key order, int-vs-float spelling, id spelling, method-name case
    respelt = [dict(reversed(list({**s, "amplitude_min": 0.0, "id": str(s["id"])}.items()))) for s in specs]
    assert base == _seed(x, y, respelt)
    assert base == _seed(x, y, specs, fit_kws={"method": "LeastSq"})
    # NOTHING the fit ignores: presentation fields, and settings that are inert for the shape
    cosmetic = [{**s, "name": "Graphite", "color": "#ff0000", "visible": False, "_rsf": 0.3} for s in specs]
    assert base == _seed(x, y, cosmetic)
    inert = [{**s, "asymmetry": 0.4, "fix_asymmetry": True, "alpha": 0.2, "m": 12, "fix_m": False} for s in specs]
    assert base == _seed(x, y, inert)                       # a GL peak reads none of these
    anchors = [[280.0, 200.0], [287.0, 210.0], [294.9, 205.0]]
    assert (_seed(x, y, specs, background_method="manual", manual_bg=anchors)
            == _seed(x, y, specs, background_method="manual", manual_bg=anchors[::-1]))
    # anything that changes what the optimiser is given changes the seed
    y2 = y.copy(); y2[7] += 1
    variants = [
        _seed(x, y2, specs),
        _seed(x, y, [{**specs[0], "center": 284.61}, specs[1]]),
        _seed(x, y, [{**specs[0], "fix_gl_ratio": True}, specs[1]]),          # active for a GL peak
        _seed(x, y, [{**specs[0], "amplitude_min": None}, specs[1]]),         # null OPENS the floor; absent means 0
        _seed(x, y, [{**specs[0], "shape": "gaussian"}, specs[1]]),
        _seed(x, y, specs, n_perturb=2),
        _seed(x, y, specs, background_method="shirley"),
        _seed(x, y, specs, fit_kws={"method": "least_squares"}),
    ]
    assert len({base, *variants}) == len(variants) + 1


def test_the_seed_derivation_is_pinned():
    # Changing how the seed is derived silently changes the answer every saved
    # project regenerates. If this fails, that is a versioned, announced change.
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y = np.array([10.0, 20.0, 40.0, 20.0, 10.0])
    specs = [{"id": 1, "shape": "gaussian", "center": 3.0, "amplitude": 30.0, "fwhm": 1.5, "amplitude_min": 0}]
    assert _seed(x, y, specs, background_method="none") == PINNED_SEED


PINNED_SEED = 3015826926  # xps-fit-seed-v1; recorded once from the implementation, never edited


def test_the_response_reports_its_seed():
    x, y, specs = _two_peaks()
    res = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=3,
                          fit_kws={"method": "least_squares"})
    assert isinstance(res["random_seed"], int) and 0 <= res["random_seed"] < 2 ** 32
    assert res["random_seed"] == _seed(x, y, specs, fit_kws={"method": "least_squares"})


def test_a_caller_supplied_seed_wins_and_is_reported():
    x, y, specs = _two_peaks()
    kw = {"method": "differential_evolution", "fit_kws": {"seed": 4}}
    a = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=1, fit_kws=kw)
    b = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=1, fit_kws=kw)
    assert kw == {"method": "differential_evolution", "fit_kws": {"seed": 4}}     # the caller's dict is not mutated
    assert a["random_seed"] == b["random_seed"] == 4
    assert a["statistics"]["reduced_chi_square"] == pytest.approx(b["statistics"]["reduced_chi_square"], rel=1e-6)


@pytest.mark.parametrize("method,exact", [("leastsq", True), ("least_squares", False)])
def test_api_fit_from_separate_uploads_repeats(client, method, exact):
    # What "press Run Fit again" is: a new upload of the same points, then
    # the same request.
    x, y, specs = _crowded_c1s()
    csv = "\n".join(f"{a:.3f},{b:.2f}" for a, b in zip(x, y))
    bodies = []
    for _ in range(3):
        up = client.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "c1s.csv")})
        resp = client.post("/api/fit", json={
            "session_id": up.get_json()["session_id"], "background": {"method": "shirley"},
            "peaks": specs, "fit_method": method, "n_perturb": 3})
        assert resp.status_code == 200
        bodies.append(resp.get_data())
    if exact:
        assert bodies[0] == bodies[1] == bodies[2]
        return
    # Trust-Region: the seed is the same on every press; the result is not
    # asserted (module docstring).
    assert len({json.loads(b)["random_seed"] for b in bodies}) == 1


# ── Codex round 1 (both runs NO-GO) ─────────────────────────────────────────

def test_a_cosmetic_rename_does_not_change_the_fit():
    x, y, specs = _crowded_c1s()
    named = [{**s, "name": n} for s, n in zip(specs, ["C-C", "b", "c", "d", "e"])]
    renamed = [{**s, "name": n} for s, n in zip(specs, ["Graphite", "b", "c", "d", "e"])]
    a = fitting.run_fit(x, y, named, background_method="shirley", n_perturb=3, fit_kws={"method": "leastsq"})
    b = fitting.run_fit(x, y, renamed, background_method="shirley", n_perturb=3, fit_kws={"method": "leastsq"})
    assert _dump(a) == _dump(b)


@pytest.mark.parametrize("which", [1, 4])
def test_a_setting_that_is_inert_for_the_shape_does_not_change_the_fit(which):
    # Codex round 2: the page always sends fix_gl_ratio, also after a peak is
    # switched to Gaussian, where nothing reads it. Flipping it changed the
    # seed and moved the third component's area fraction from 8 % to 53 %.
    x, y, specs = _crowded_c1s()
    gaussian = [dict(s) for s in specs]
    gaussian[which].update(shape="gaussian", fix_gl_ratio=False)
    gaussian[which].pop("gl_ratio")
    flipped = [dict(s) for s in gaussian]
    flipped[which]["fix_gl_ratio"] = True
    kw = dict(background_method="shirley", n_perturb=3, fit_kws={"method": "leastsq"})
    assert _dump(fitting.run_fit(x, y, gaussian, **kw)) == _dump(fitting.run_fit(x, y, flipped, **kw))


@pytest.mark.parametrize("method", ["ampgo", "dual_annealing", "shgo", "powell", "emcee"])
def test_methods_outside_the_supported_five_are_refused_centrally(method):
    # /api/analyze forwards options.fit_method straight to run_fit; lmfit knows
    # these and the stochastic ones would draw from numpy's global generator.
    x, y, specs = _two_peaks()
    with pytest.raises(ValueError, match="Unknown fit method"):
        fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": method})


def test_a_differently_cased_method_name_is_the_same_seeded_method(monkeypatch):
    records = _spy_on_fits(monkeypatch)
    records.append([])
    x, y, specs = _two_peaks()
    res = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "BasinHopping"})
    # F2 (2026-09-26): the seeded search, then its refinement and the competing
    # fit from the start (least_squares: deterministic, carry no seed)
    assert [r["method"] for r in records[0]] == ["basinhopping", "least_squares", "least_squares"]
    assert isinstance(records[0][0]["seed"], int)
    assert records[0][1]["seed"] is None and records[0][2]["seed"] is None
    assert res["random_seed"] == fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0,
                                                 fit_kws={"method": "basinhopping"})["random_seed"]


def test_the_analyze_wrapper_cannot_reach_an_unseeded_method():
    from autofit.methods.least_squares import LeastSquaresMethod
    x, y, specs = _two_peaks()
    with pytest.raises(ValueError, match="Unknown fit method"):
        LeastSquaresMethod().run(x, y, peak_specs=specs, options={"fit_method": "ampgo", "background_method": "linear"})


@pytest.mark.parametrize("method", ["leastsq", "least_squares", "nelder"])
def test_a_caller_seed_works_with_the_deterministic_methods(method):
    # it selects the draws and must not be forwarded to a solver that rejects it
    x, y, specs = _two_peaks()
    res = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=2,
                          fit_kws={"method": method, "fit_kws": {"seed": 7}})
    assert res["success"] is True and res["random_seed"] == 7


@pytest.mark.parametrize("seed", [-1, True, 1.5, "4", 2 ** 32])
def test_an_unusable_caller_seed_is_a_validation_error_not_a_silent_fallback(seed):
    x, y, specs = _two_peaks()
    with pytest.raises(ValueError, match="seed must be an integer"):
        fitting.run_fit(x, y, specs, background_method="linear", n_perturb=1,
                        fit_kws={"method": "least_squares", "fit_kws": {"seed": seed}})


def _production_draws(monkeypatch, seed):
    records = _spy_on_fits(monkeypatch)
    records.append([])
    x, y, specs = _two_peaks()
    fitting.run_fit(x, y, specs, background_method="linear", n_perturb=1,
                    fit_kws={"method": "leastsq", "fit_kws": {"seed": seed}})
    first, restart = records[0][0]["end"], records[0][1]["start"]
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
4679:// the preview (computeBackgroundCore) and both /api/fit request builders,
4724:  // The background window — the one definition shared with both /api/fit
7107:// Computed from the /api/fit response alone (counts, fitted_y, the component's
7408:// Read a 2xx /api/fit reply (unit F2, 2026-09-26). A failure to READ the body
7414:async function _readFitReply(resp) {
7516:  // Step 5: run /api/fit with AbortController + spinner.
7562:    const resp = await fetch('/api/fit', {
7589:    const json = await _readFitReply(resp);   // F2: an unreadable reply is a failed fit with its own message
8058:      resp = await fetch('/api/fit', {
8075:    try { json = await _readFitReply(resp); } catch (e) { _asTransport(e); }
14843:     STRICTLY ADDITIVE: the manual fit path (/api/fit, Run Fit, peak

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile
tempfile.tempdir=\"/tmp\"
import pytest
raise SystemExit(pytest.main([\"-q\",\"-s\",\"-p\",\"no:cacheprovider\",\"tests/test_fit_acceptance_holes.py\",\"tests/test_basinhopping_outcome.py\",\"-k\",\"not test_api_fit_returns\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
exec
/bin/zsh -lc "node -e '
const fs=require('\\''fs'\\''),vm=require('\\''vm'\\''),path=require('\\''path'\\''),assert=require('\\''assert'\\''),cp=require('\\''child_process'\\'');
const file=path.resolve('\\''tests/js/fit_acceptance.test.js'\\'');
const code=fs.readFileSync(file,'\\''utf8'\\'');
const old=cp.execFileSync('\\''git'\\'',['\\''show'\\'','\\''a5a14a0:templates/index.html'\\''],{encoding:'\\''utf8'\\'',maxBuffer:5e6});
async function run(skipTruncation) {
 let target;
 let count=0;
 const assertion=Object.create(assert);
 assertion.rejects=async(...args)=>{count++; if(skipTruncation && count===1){await args[0].catch(()=>{});return;}return assert.rejects(...args);};
 const req=name=>name==='\\''node:test'\\''?{test:(name,fn)=>{if(name.startsWith('\\''the token scan is linear'\\''))target=fn}}:name==='\\''node:assert'\\''?assertion:name==='\\''node:fs'\\''?{...fs,readFileSync:(p,...a)=>String(p).endsWith('\\''templates/index.html'\\'')?old:fs.readFileSync(p,...a)}:require(name);
 vm.runInNewContext(code,{require:req,__dirname:path.dirname(file),console});
 const t=performance.now();
 try{await target();console.log('\\''UNEXPECTED PASS'\\'',skipTruncation)}catch(e){console.log(skipTruncation?'\\''old scanner stress assertion'\\'':'\\''old scanner truncated-string assertion'\\'','\\''failed as expected'\\'',e.message.slice(0,300),(performance.now()-t).toFixed(1)+'\\'' ms'\\'');}
}
(async()=>{await run(false);await run(true)})();
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
codex
The 128 KB stress case now rejects in about 4 ms; the 10 MB probes took at most 124 ms and showed linear scaling. I found one minor diagnostic regression: `x-Infinity` and `--Infinity` are labelled as non-finite numbers because the scanner doesn’t check the boundary before the minus sign. They still fail closed.

The JavaScript run recorded 102 passes; one Python-backed parity test was blocked by the read-only sandbox’s temporary-directory restriction. Backend tests and checks against the old scanner are still running.
 succeeded in 9600ms:
old scanner stress assertion failed as expected took 9600 ms 9600.1 ms

exec
/bin/zsh -lc "sed -n '1940,2005p' fitting.py; sed -n '8040,8110p' templates/index.html; rg -n '"'^def test_'"' tests/test_fit_reproducibility.py | head -15; git diff --check a5a14a0..HEAD -- templates/index.html tests/js/fit_acceptance.test.js" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
        # A linked component follows its parent: it is supported exactly when the
        # parent is (its own removal test would double-count the parent's role).
        individual_peaks.append({
            "id": pid,
            "y": peak_y.tolist(),
            "params": param_info,
            "support": support,
        })

    # A linked component follows its ROOT ancestor (a grandchild follows the
    # root), whatever the request order; a cycle or a missing master leaves
    # its own verdict.
    by_id = {str(ip["id"]): ip for ip in individual_peaks}
    master_of = {str(spec["id"]): spec.get("constrain_to") for spec in peak_specs}

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
            "r_factor": r_factor,
            "n_data": n_data,
            "n_free_params": n_free,
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
    let resp, json;
    try {
      resp = await fetch('/api/fit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(fitReq)
      });
    } catch (e) { _asTransport(e); }
    if (resp.ok === false) {
      // HTTP failure: read a message if the body is JSON, but a 502 HTML
      // page is still a SERVER failure, never a reason to switch engines.
      let msg = null;
      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
      const err = new Error(msg || ('Fit request failed (HTTP ' + resp.status + ').'));
      err.serverError = true;
      throw err;
    }
    // F2: reading the body can fail in transport; a body that was read but is
    // not JSON is the server's reply — a failed fit, not a fallback
    try { json = await _readFitReply(resp); } catch (e) { _asTransport(e); }
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
87:def test_perturbed_starts_are_byte_identical_with_a_deterministic_method(monkeypatch):
101:def test_trust_region_perturbation_draws_are_exactly_identical(monkeypatch):
139:def test_repeated_fits_are_byte_identical(method):
166:def test_stochastic_methods_get_request_derived_seeds_not_the_global_generator(monkeypatch, method, n_perturb, n_min):
185:def test_deterministic_methods_receive_no_solver_seed(monkeypatch, method):
198:def test_the_seed_is_a_pure_function_of_what_the_optimiser_is_given():
229:def test_the_seed_derivation_is_pinned():
241:def test_the_response_reports_its_seed():
249:def test_a_caller_supplied_seed_wins_and_is_reported():
260:def test_api_fit_from_separate_uploads_repeats(client, method, exact):
283:def test_a_cosmetic_rename_does_not_change_the_fit():
293:def test_a_setting_that_is_inert_for_the_shape_does_not_change_the_fit(which):
308:def test_methods_outside_the_supported_five_are_refused_centrally(method):
316:def test_a_differently_cased_method_name_is_the_same_seeded_method(monkeypatch):
330:def test_the_analyze_wrapper_cannot_reach_an_unseeded_method():
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ivyGMmaW' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-fddKtCfU' (errno=Operation not permitted)

exec
/bin/zsh -lc "node -e '
const fs=require('\\''fs'\\''),vm=require('\\''vm'\\''),path=require('\\''path'\\''),assert=require('\\''assert'\\'');
const file=path.resolve('\\''tests/js/fit_acceptance.test.js'\\'');
const append=String.raw"'`
;(async()=>{
for(const body of ['"'\\''{\"a\":x-Infinity}'\\'','\\''{\"a\":--Infinity}'\\'','\\''{\"a\":-Infinity}'\\'','\\''{\"a\":NaN}'\\'','\\''{\"m\":\"NaN in truncated string'\\'']) {
const env=makeEnv({fetchImpl:async()=>({ok:true,status:200,text:async()=>body})});
const before=JSON.stringify(env.state);
await env.runFit();
assert.equal(env.calls.local,0);assert.equal(env.calls.applied,0);assert.equal(JSON.stringify(env.state),before);
console.log(body,env.calls.notify.find(n=>n.kind==='\\''red'\\'').msg);
}
})();"'`;
vm.runInNewContext(fs.readFileSync(file,'"'\\''utf8'\\'')+append,{require:n=>n==='\\''node:test'\\''?{test:()=>{}}:require(n),__dirname:path.dirname(file),console});
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
{"a":x-Infinity} Fit failed: The server's reply contains a non-finite number (NaN or Infinity), usually an uncertainty that could not be computed because these data do not determine the model. The fit is treated as failed. Previous peaks and result kept.
{"a":--Infinity} Fit failed: The server's reply contains a non-finite number (NaN or Infinity), usually an uncertainty that could not be computed because these data do not determine the model. The fit is treated as failed. Previous peaks and result kept.
{"a":-Infinity} Fit failed: The server's reply contains a non-finite number (NaN or Infinity), usually an uncertainty that could not be computed because these data do not determine the model. The fit is treated as failed. Previous peaks and result kept.
{"a":NaN} Fit failed: The server's reply contains a non-finite number (NaN or Infinity), usually an uncertainty that could not be computed because these data do not determine the model. The fit is treated as failed. Previous peaks and result kept.
{"m":"NaN in truncated string Fit failed: The server's reply could not be read. The fit is treated as failed. Previous peaks and result kept.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile
tempfile.tempdir=\"/tmp\"
from unittest.mock import patch
import numpy as np
import app
a=app.create_app()
with patch.object(app, \"_load_session\", return_value=(np.arange(3.), np.ones(3))):
    with a.test_client() as c:
        r=c.post(\"/api/fit\",json={\"session_id\":\"a\"*32,\"background\":{\"method\":\"none\"},\"fit_method\":\"least_squares\",\"peaks\":[{\"id\":\"1\",\"shape\":\"gaussian\",\"center\":1,\"amplitude\":1,\"fwhm\":1}]})
        assert r.status_code==400 and \"not determined by these data\" in r.get_json()[\"error\"]
        print(\"API:\",r.status_code,r.get_json())
print(\"Flask overflow:\",a.json.dumps({\"v\":float(\"1e999\")}))
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 1750ms:
/Users/skyefortier/.matplotlib is not a writable directory
API: 400 {'error': 'The model is not determined by these data: 3 free parameters for 3 data points leaves no degrees of freedom. Widen the fitted range, remove components or lock parameters.'}
Flask overflow: {"v": Infinity}

 succeeded in 47364ms:
...........
11 passed, 1 deselected in 46.97s

exec
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
# F2 — holes in the acceptance rule (2026-09-26)

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
/bin/zsh -lc 'git diff HEAD~1..HEAD; git diff --stat main..HEAD; git log -6 --oneline' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 36ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-anzauf1u' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-HKhUCYZY' (errno=Operation not permitted)
63f7e6d fix(F2): Codex round 3 (GO x2) - a minus sign before Infinity counts only after a boundary
0224141 fix(F2): Codex round 2 (A GO, B NO-GO) - linear token scan for the unreadable-reply message
a5a14a0 fix(F2): Codex round 1 (A GO, B NO-GO) - unverified DE refit gives no required verdict; NaN token test ignores strings
9210786 fix(F2): holes in the acceptance rule - basinhopping verified, NaN reply, undetermined models, required refit, Auto-Fit HTTP status
07e8f46 docs(F1): deploy-log entry
2e85ed7 docs(F1): owner's notes at deploy - 'two readings of one field' design rule; legacy verification on load logged in the sealed-fit-record memo

exec
/bin/zsh -lc 'cat docs/autofit/codex/f2_acceptance_holes_review_prompt.txt docs/autofit/codex/f2_acceptance_holes_recheck_prompt.txt docs/autofit/codex/f2_acceptance_holes_recheck2_prompt.txt; tail -35 docs/autofit/codex/f2_acceptance_holes_r3_verdict_runA.md; tail -35 docs/autofit/codex/f2_acceptance_holes_r3_verdict_runB.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
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

Finish with VERDICT: GO or VERDICT: NO-GO./bin/zsh -lc 'git status --short; git rev-parse --short HEAD' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
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

exec
/bin/zsh -lc 'git diff main..HEAD -- fitting.py templates/index.html tests/test_fit_acceptance_holes.py tests/test_basinhopping_outcome.py tests/test_fit_reproducibility.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Xr9fF3Vp' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-vSpkJQni' (errno=Operation not permitted)
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
/bin/zsh -lc "git diff HEAD~1..HEAD -- templates/index.html tests/js/fit_acceptance.test.js; git diff --stat main..HEAD; git log -5 --oneline; rg --files --hidden -g AGENTS.md -g '"'!node_modules'"' -g '"'!.git'"'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 exited 1 in 55ms:
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
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-4uT53Uii' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-azZLBZ3o' (errno=Operation not permitted)
63f7e6d fix(F2): Codex round 3 (GO x2) - a minus sign before Infinity counts only after a boundary
0224141 fix(F2): Codex round 2 (A GO, B NO-GO) - linear token scan for the unreadable-reply message
a5a14a0 fix(F2): Codex round 1 (A GO, B NO-GO) - unverified DE refit gives no required verdict; NaN token test ignores strings
9210786 fix(F2): holes in the acceptance rule - basinhopping verified, NaN reply, undetermined models, required refit, Auto-Fit HTTP status
07e8f46 docs(F1): deploy-log entry

exec
/bin/zsh -lc "git diff main..HEAD -- fitting.py; sed -n '7410,7454p' templates/index.html; sed -n '1,85p' tests/js/fit_acceptance.test.js; cat tests/conftest.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ENfCXyqZ' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-j9mjvn1B' (errno=Operation not permitted)
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

async function runAutoFitC1sGraphite() {
  // Pre-conditions
  if (!state.rawBE || !state.rawBE.length) { notify('Load a spectrum first.', 'amber'); return; }
  const tab = tabManager._getTab(tabManager.activeId);
  if (!tab) { notify('No active tab.', 'amber'); return; }
  if (!isC1sTab(tab)) {
    notify('Auto-Fit C1s Graphite is only available for C1s spectra (ROI midpoint 270–315 eV).', 'amber');
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
"""Make the repo root importable regardless of how pytest is invoked."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

codex
HEAD changes only the Infinity boundary condition in production code. The new check accepts a leading `-Infinity` because the character before its sign is `undefined`, which counts as a boundary. I’ll probe that and the other token positions, then run the regression against the parent revision to verify that it fails there.

exec
/bin/zsh -lc 'node --test tests/js/fit_acceptance.test.js tests/js/stale_statistics.test.js tests/js/autofit_required.test.js tests/js/local_lm_descent.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"-q\", \"-p\", \"no:cacheprovider\", \"-s\", \"tests/test_fit_acceptance_holes.py\", \"tests/test_basinhopping_outcome.py\", \"tests/test_fit_reproducibility.py\", \"-k\", \"not api_fit_returns\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
exec
/bin/zsh -lc 'git diff main..HEAD -- templates/index.html tests/js/autofit_required.test.js tests/js/local_lm_descent.test.js tests/js/stale_statistics.test.js; git diff main..HEAD -- CLAUDE.md docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md docs/findings/2026-09-26-public-request-ceiling.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 28ms:
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
diff --git a/docs/findings/2026-09-26-public-request-ceiling.md b/docs/findings/2026-09-26-public-request-ceiling.md
new file mode 100644
index 0000000..28765b4
--- /dev/null
+++ b/docs/findings/2026-09-26-public-request-ceiling.md
@@ -0,0 +1,59 @@
+# Public request ceiling (xps.fortierlab.org) — REPORT ONLY (2026-09-26)
+
+Owner, during F2: "measure through the PUBLIC URL … verify it rather than
+assume … Report which user-reachable paths exceed whatever the real public
+limit is, and what the page shows when they do. Don't fold it into F2."
+
+## 1. The ceiling
+
+The tunnel (`~/.cloudflared/config.yml`) sets no `originRequest` timeouts, so
+Cloudflare's edge defaults apply. Probes: one `/api/fit` each, from outside,
+production code (main 07e8f46), basinhopping at `n_perturb` 0 on committed
+targets (`scripts`-equivalent probe in the session scratchpad):
+
+| target | request took | returned |
+|---|---|---|
+| 4e5388460b7b | 26.9 s | 200 |
+| 005c6346813e | 88.3 s | 200 |
+| fba7b6facc1a (168 s locally) | **125.1 s** | **HTTP 524** "error code: 524" |
+
+So the public ceiling is between 88 s and 125 s (Cloudflare documents 100 s
+for a proxied response; the 524 arrived at 125 s). Gunicorn's `--timeout 300`
+is not the limit a student behind the public URL meets. The worker is not
+told: it keeps computing a result nobody receives (up to 300 s, then it is
+killed and restarted — one of four production workers is busy meanwhile).
+
+## 2. What the page shows (no silent local fallback)
+
+| failure | Run Fit (incl. "Use this solution") | Auto-Fit C1s Graphite |
+|---|---|---|
+| edge 524 (> ~100–125 s via the public URL) | "Fit failed: Fit request failed (HTTP 524). Previous peaks and result kept." — red, no local fallback (`resp.ok` false is a server error under A0) | main: "Fit failed to converge or produced an unphysical graphite position." (misleading); fixed in F2 (owner, 2026-09-27): Auto-Fit checks `resp.ok` before parsing, "Auto-fit failed: Fit request failed (HTTP 524)." |
+| gunicorn worker timeout (> 300 s; direct :5050 or a slower edge) | "Fit failed: Fit request failed (HTTP 500)." — gunicorn answers 500 when it aborts a sync worker (reproduced with `--timeout 20`), no local fallback | the same unreadable-reply message |
+| Auto-Fit's own 120 s `AbortController` | — | "Auto-fit exceeded the 2-minute timeout." (only reachable if the edge is slower than 120 s; the 524 at ≤ 125 s usually wins) |
+
+The A0 concern ("a timeout is a transport failure → the local engine") does
+not arise: both timeouts arrive as HTTP errors. Only a dropped connection
+(network loss) reaches the local fallback, as designed.
+
+## 3. User-reachable paths against the ceiling
+
+| path | measured | vs ~100–125 s |
+|---|---|---|
+| Run Fit, basinhopping, page request (`n_perturb` 3), main | 16 multi-component targets: median 386 s, max 1066 s; 14 of 16 > 300 s | **exceeds** — always fails publicly on ≥ 3-component models |
+| Run Fit, basinhopping, F2 (no restarts) | median 96 s, max 256 s; 5 of 16 > 125 s (the 6- and 7-component C 1s models, 183–256 s) | **still exceeds on the large models** — F2 fixes the 300 s case, not the public one |
+| Run Fit, DS+G graphite + five GL (committed C1s Scan, Trust-Region, page request) | 78.7 s on the production page, 200 | under, little margin (was ~110 s under load in the DS+G unit; the "covered by 300 s" note there is wrong for public users) |
+| Run Fit, differential evolution | 2–75 s (CLAUDE.md, committed targets, `n_perturb` 3) | under; the 75 s end is close |
+| Auto-Fit C1s Graphite (Trust-Region) | 1.6–1.9 s | far under; its 120 s abort sits above the ceiling and is unreachable in practice |
+| Find Peaks (`/api/analyze/start` → 202, poll `/api/analyze/progress`) | background thread; every request short | **unaffected** — the only long-running page path already built for this |
+| Batch Fit | local engine only | unaffected |
+| Upload, parse-vgd, reference, meta | short | unaffected |
+
+## 4. Suggested unit (not decided)
+
+Long fits on the Find Peaks pattern: `/api/fit/start` (202 + job id, a
+background thread, the same poll file), poll for completion, the result read
+from the progress record. It removes the edge ceiling for every method
+without raising any timeout, lets the page show progress and cancel, and
+frees the worker. Smaller interim options: Auto-Fit to check `resp.ok` and name
+a 524 / 500 as a timeout; the Run Fit message to say "the server took longer
+than the connection allows" for 524.
diff --git a/docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md b/docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md
index 22c75d9..2c26116 100644
--- a/docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md
+++ b/docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md
@@ -172,6 +172,15 @@ takes ~18 s (28,821 evaluations — the perturbed descent runs to the
 optimiser's evaluation budget), and with `n_starts: 3` the request takes
 110 s. Production's gunicorn `--timeout 300` covers it; a dev server on the
 30 s default returns a worker timeout and the page reports "Fit failed".
+
+CORRECTION (2026-09-26, unit F2): "300 s covers it" was true on the i9 and
+FALSE through the public URL. Cloudflare's edge ends a proxied request at
+~100 s (probes through xps.fortierlab.org: 88 s passed, 125 s returned HTTP
+524), well short of gunicorn's 300 s. The same DS+G Run Fit measured on the
+production page through the public URL took 78.7 s and passed — under the
+ceiling today, with little margin
+(`docs/findings/2026-09-26-public-request-ceiling.md`). Timing claims must be
+measured through xps.fortierlab.org, not on 127.0.0.1.
 Every A- and M-family Find Peaks candidate applied and re-fitted pays this.
 Logged for its own look (why the perturbed DS+G descent does not converge;
 whether the restarts should be skipped or capped for this shape).

 exited 1 in 7356ms:
TAP version 13
# Subtest: a supported but NOT required anchor is refused before any charge-correction input is touched
ok 1 - a supported but NOT required anchor is refused before any charge-correction input is touched
  ---
  duration_ms: 7.403408
  type: 'test'
  ...
# Subtest: a required anchor proceeds; a check that did not RUN (older server, error, main fit not converged) does not block
ok 2 - a required anchor proceeds; a check that did not RUN (older server, error, main fit not converged) does not block
  ---
  duration_ms: 14.633763
  type: 'test'
  ...
# Subtest: the request asks for the Graphite anchor by id, and the gate precedes the support gate and every cc write
ok 3 - the request asks for the Graphite anchor by id, and the gate precedes the support gate and every cc write
  ---
  duration_ms: 2.005342
  type: 'test'
  ...
# Subtest: a refit that did not converge: no verdict, and Auto-Fit refuses before any charge-correction input is touched
ok 4 - a refit that did not converge: no verdict, and Auto-Fit refuses before any charge-correction input is touched
  ---
  duration_ms: 3.855145
  type: 'test'
  ...
# Subtest: A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
ok 5 - A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
  ---
  duration_ms: 17.874906
  type: 'test'
  ...
# Subtest: a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
ok 6 - a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
  ---
  duration_ms: 9.701041
  type: 'test'
  ...
# Subtest: a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
ok 7 - a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
  ---
  duration_ms: 6.412247
  type: 'test'
  ...
# Subtest: a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
ok 8 - a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
  ---
  duration_ms: 14.037548
  type: 'test'
  ...
# Subtest: a converged backend result is applied (sanity)
ok 9 - a converged backend result is applied (sanity)
  ---
  duration_ms: 3.559398
  type: 'test'
  ...
# Subtest: the engine/objective labels of a fit result survive spectrum and project save/load
ok 10 - the engine/objective labels of a fit result survive spectrum and project save/load
  ---
  duration_ms: 0.851388
  type: 'test'
  ...
# Subtest: an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
ok 11 - an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
  ---
  duration_ms: 3.427149
  type: 'test'
  ...
# Subtest: an HTTP 502 on the upload is a server failure, not a transport failure
ok 12 - an HTTP 502 on the upload is a server failure, not a transport failure
  ---
  duration_ms: 5.202306
  type: 'test'
  ...
# Subtest: uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
ok 13 - uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
  ---
  duration_ms: 3.303675
  type: 'test'
  ...
# Subtest: every consumer that prints the goodness-of-fit statistic routes through the statistic identity
ok 14 - every consumer that prints the goodness-of-fit statistic routes through the statistic identity
  ---
  duration_ms: 1.118272
  type: 'test'
  ...
# Subtest: uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
ok 15 - uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
  ---
  duration_ms: 1.653977
  type: 'test'
  ...
# Subtest: a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
ok 16 - a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
  ---
  duration_ms: 1.90283
  type: 'test'
  ...
# Subtest: starting-point helpers: keyed on the persisted objective, weighted results untouched
ok 17 - starting-point helpers: keyed on the persisted objective, weighted results untouched
  ---
  duration_ms: 3.533131
  type: 'test'
  ...
# Subtest: Quantify shows the starting-point banner for a local result and not for a weighted one
ok 18 - Quantify shows the starting-point banner for a local result and not for a weighted one
  ---
  duration_ms: 5.697646
  type: 'test'
  ...
# Subtest: every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
ok 19 - every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
  ---
  duration_ms: 2.081866
  type: 'test'
  ...
# Subtest: project save derives the designation from the objective for an older local result lacking the new fields
ok 20 - project save derives the designation from the objective for an older local result lacking the new fields
  ---
  duration_ms: 11.492731
  type: 'test'
  ...
# Subtest: stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
ok 21 - stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
  ---
  duration_ms: 1.231761
  type: 'test'
  ...
# Subtest: _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
ok 22 - _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
  ---
  duration_ms: 3.551161
  type: 'test'
  ...
# Subtest: history preview glow is keyed on the dataset flag, not the label text
ok 23 - history preview glow is keyed on the dataset flag, not the label text
  ---
  duration_ms: 0.728671
  type: 'test'
  ...
# Subtest: spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
ok 24 - spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
  ---
  duration_ms: 0.511869
  type: 'test'
  ...
# Subtest: _applyStatDisplay clears header, tooltip, caption and value together on local → none
ok 25 - _applyStatDisplay clears header, tooltip, caption and value together on local → none
  ---
  duration_ms: 3.279133
  type: 'test'
  ...
# Subtest: _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
ok 26 - _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
  ---
  duration_ms: 2.917366
  type: 'test'
  ...
# Subtest: fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
ok 27 - fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
  ---
  duration_ms: 1.739516
  type: 'test'
  ...
# Subtest: undo/redo snapshots carry and restore model provenance
ok 28 - undo/redo snapshots carry and restore model provenance
  ---
  duration_ms: 4.796416
  type: 'test'
  ...
# Subtest: round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
ok 29 - round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
  ---
  duration_ms: 1.277954
  type: 'test'
  ...
# Subtest: _provenanceOf derives a designation from a live local result, and undo snapshots use it
ok 30 - _provenanceOf derives a designation from a live local result, and undo snapshots use it
  ---
  duration_ms: 3.367873
  type: 'test'
  ...
# Subtest: batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
ok 31 - batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
  ---
  duration_ms: 0.537103
  type: 'test'
  ...
# Subtest: the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
ok 32 - the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
  ---
  duration_ms: 4.400831
  type: 'test'
  ...
# Subtest: round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
ok 33 - round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
  ---
  duration_ms: 0.940666
  type: 'test'
  ...
# Subtest: the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
ok 34 - the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
  ---
  duration_ms: 3.514323
  type: 'test'
  ...
# Subtest: the sidebar banner is sticky at the top of the scrolling panel body
ok 35 - the sidebar banner is sticky at the top of the scrolling panel body
  ---
  duration_ms: 0.459199
  type: 'test'
  ...
# Subtest: the sidebar banner shows on a stack tab whose visible entries draw a local source fit
ok 36 - the sidebar banner shows on a stack tab whose visible entries draw a local source fit
  ---
  duration_ms: 3.952925
  type: 'test'
  ...
# Subtest: every stack chart repaint path refreshes the sidebar designation before any early return
ok 37 - every stack chart repaint path refreshes the sidebar designation before any early return
  ---
  duration_ms: 0.452089
  type: 'test'
  ...
# Subtest: closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
ok 38 - closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
  ---
  duration_ms: 0.205145
  type: 'test'
  ...
# Subtest: W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
ok 39 - W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
  ---
  duration_ms: 4.282162
  type: 'test'
  ...
# Subtest: TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
ok 40 - TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
  ---
  duration_ms: 6.981087
  type: 'test'
  ...
# Subtest: adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
ok 41 - adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
  ---
  duration_ms: 4.250124
  type: 'test'
  ...
# Subtest: adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
ok 42 - adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
  ---
  duration_ms: 3.621969
  type: 'test'
  ...
# Subtest: adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
ok 43 - adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
  ---
  duration_ms: 3.714324
  type: 'test'
  ...
# Subtest: adoption: success records the choice, the starts evidence and the key of the model it describes
ok 44 - adoption: success records the choice, the starts evidence and the key of the model it describes
  ---
  duration_ms: 3.729614
  type: 'test'
  ...
# Subtest: an ordinary Run Fit on one unlinked component does not ask for the starts check
ok 45 - an ordinary Run Fit on one unlinked component does not ask for the starts check
  ---
  duration_ms: 4.40469
  type: 'test'
  ...
# Subtest: a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
ok 46 - a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
  ---
  duration_ms: 3.454641
  type: 'test'
  ...
# Subtest: a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
ok 47 - a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
  ---
  duration_ms: 5.855638
  type: 'test'
  ...
# Subtest: a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
ok 48 - a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
  ---
  duration_ms: 3.138248
  type: 'test'
  ...
# Subtest: a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
ok 49 - a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
  ---
  duration_ms: 7.927693
  type: 'test'
  ...
# Subtest: the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)
ok 50 - the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)
  ---
  duration_ms: 1.458028
  type: 'test'
  ...
# Subtest: the token scan is linear and keeps a truncated string a string (Codex round 2)
ok 51 - the token scan is linear and keeps a truncated string a string (Codex round 2)
  ---
  duration_ms: 4.891495
  type: 'test'
  ...
# Subtest: a minus sign counts only after a boundary: "x-Infinity" is malformed, "-Infinity" a token (Codex round 3)
ok 52 - a minus sign counts only after a boundary: "x-Infinity" is malformed, "-Infinity" a token (Codex round 3)
  ---
  duration_ms: 0.847073
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
  duration_ms: 1722.10797
  type: 'test'
  ...
# Subtest: A01 replay: the linked U 4f pair also descends
ok 54 - A01 replay: the linked U 4f pair also descends
  ---
  duration_ms: 325.756279
  type: 'test'
  ...
# Subtest: noiseless Gaussian: amplitude 10 started at 5 is recovered
ok 55 - noiseless Gaussian: amplitude 10 started at 5 is recovered
  ---
  duration_ms: 17.52512
  type: 'test'
  ...
# Subtest: acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
ok 56 - acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
  ---
  duration_ms: 11.609552
  type: 'test'
  ...
# Subtest: a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
ok 57 - a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
  ---
  duration_ms: 14.343647
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
ok 58 - bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
  ---
  duration_ms: 11.512252
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
ok 59 - bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
  ---
  duration_ms: 11.313924
  type: 'test'
  ...
# Subtest: a weak component the data DO hold is no longer forced up to an amplitude of 1
ok 60 - a weak component the data DO hold is no longer forced up to an amplitude of 1
  ---
  duration_ms: 11.27302
  type: 'test'
  ...
# Subtest: derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
ok 61 - derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
  ---
  duration_ms: 55.184181
  type: 'test'
  ...
# Subtest: derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
ok 62 - derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
  ---
  duration_ms: 30.656829
  type: 'test'
  ...
# Subtest: a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
ok 63 - a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
  ---
  duration_ms: 9.827941
  type: 'test'
  ...
# Subtest: linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
ok 64 - linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
  ---
  duration_ms: 14.662265
  type: 'test'
  ...
# Subtest: round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
ok 65 - round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
  ---
  duration_ms: 14.161569
  type: 'test'
  ...
# Subtest: round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
ok 66 - round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
  ---
  duration_ms: 11.91191
  type: 'test'
  ...
# Subtest: round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
ok 67 - round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
  ---
  duration_ms: 11.146794
  type: 'test'
  ...
# Subtest: A01 replay targets converge to constrained stationary points (C1s and U 4f)
ok 68 - A01 replay targets converge to constrained stationary points (C1s and U 4f)
  ---
  duration_ms: 1514.553859
  type: 'test'
  ...
# Subtest: round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
ok 69 - round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
  ---
  duration_ms: 65.589864
  type: 'test'
  ...
# Subtest: round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
ok 70 - round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
  ---
  duration_ms: 23.431363
  type: 'test'
  ...
# Subtest: round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
ok 71 - round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
  ---
  duration_ms: 18.240109
  type: 'test'
  ...
# Subtest: round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
ok 72 - round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
  ---
  duration_ms: 93.654656
  type: 'test'
  ...
# Subtest: round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
ok 73 - round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
  ---
  duration_ms: 1406.843688
  type: 'test'
  ...
# Subtest: round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
ok 74 - round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
  ---
  duration_ms: 23.66653
  type: 'test'
  ...
# Subtest: round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
ok 75 - round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
  ---
  duration_ms: 12.968157
  type: 'test'
  ...
# Subtest: weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
ok 76 - weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
  ---
  duration_ms: 12.87972
  type: 'test'
  ...
# Subtest: server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
not ok 77 - server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
  ---
  duration_ms: 1594.666289
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
  duration_ms: 23.442643
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
ok 79 - an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
  ---
  duration_ms: 27.818759
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
ok 80 - an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
  ---
  duration_ms: 23.840082
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
ok 81 - round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
  ---
  duration_ms: 10.64801
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
ok 82 - round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
  ---
  duration_ms: 12.80378
  type: 'test'
  ...
# Subtest: recovery from an amplitude of exactly zero (the new floor is not a trap)
ok 83 - recovery from an amplitude of exactly zero (the new floor is not a trap)
  ---
  duration_ms: 12.990661
  type: 'test'
  ...
# Subtest: the local engine refuses a model with no degrees of freedom; one more point and it fits
ok 84 - the local engine refuses a model with no degrees of freedom; one more point and it fits
  ---
  duration_ms: 31.603971
  type: 'test'
  ...
# Subtest: one accessor classifies a result against a key: none / unverified / current / stale
ok 85 - one accessor classifies a result against a key: none / unverified / current / stale
  ---
  duration_ms: 26.303546
  type: 'test'
  ...
# Subtest: the key is the step (b) key: F1 adds no second binding mechanism and no new key field
ok 86 - the key is the step (b) key: F1 adds no second binding mechanism and no new key field
  ---
  duration_ms: 7.171157
  type: 'test'
  ...
# Subtest: Results panel, current: statistic, RMSE, R and sigma are shown
ok 87 - Results panel, current: statistic, RMSE, R and sigma are shown
  ---
  duration_ms: 12.058799
  type: 'test'
  ...
# Subtest: Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
ok 88 - Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
  ---
  duration_ms: 12.729314
  type: 'test'
  ...
# Subtest: Results panel, unverified (older save, no key): values shown with a plain note
ok 89 - Results panel, unverified (older save, no key): values shown with a plain note
  ---
  duration_ms: 9.91831
  type: 'test'
  ...
# Subtest: status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
ok 90 - status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
  ---
  duration_ms: 11.52615
  type: 'test'
  ...
# Subtest: the stored fitted curve is never drawn, saved or stacked as the fit once stale
ok 91 - the stored fitted curve is never drawn, saved or stacked as the fit once stale
  ---
  duration_ms: 4.678075
  type: 'test'
  ...
# Subtest: saves keep the key and say plainly when the statistics are stale or unverified
ok 92 - saves keep the key and say plainly when the statistics are stale or unverified
  ---
  duration_ms: 4.513681
  type: 'test'
  ...
# Subtest: CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
ok 93 - CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
  ---
  duration_ms: 17.8472
  type: 'test'
  ...
# Subtest: XLSX: stale writes a WARNING row instead of the statistic, and no sigma
ok 94 - XLSX: stale writes a WARNING row instead of the statistic, and no sigma
  ---
  duration_ms: 5.439436
  type: 'test'
  ...
# Subtest: TSV: stale says the Model / Residual columns are the current, unfitted model
ok 95 - TSV: stale says the Model / Residual columns are the current, unfitted model
  ---
  duration_ms: 10.7776
  type: 'test'
  ...
# Subtest: the refresh re-renders Results only when its rendered state differs
ok 96 - the refresh re-renders Results only when its rendered state differs
  ---
  duration_ms: 5.699506
  type: 'test'
  ...
# Subtest: an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
ok 97 - an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
  ---
  duration_ms: 3.522304
  type: 'test'
  ...
# Subtest: Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
ok 98 - Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
  ---
  duration_ms: 5.494556
  type: 'test'
  ...
# Subtest: Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
ok 99 - Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
  ---
  duration_ms: 9.493775
  type: 'test'
  ...
# Subtest: closing the last tab clears the Results panel, header and status statistics too
ok 100 - closing the last tab clears the Results panel, header and status statistics too
  ---
  duration_ms: 0.22333
  type: 'test'
  ...
# Subtest: reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
ok 101 - reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
  ---
  duration_ms: 1.574744
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back
ok 102 - F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back
  ---
  duration_ms: 6.639698
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a Cloudflare 524 (plain-text body) is a failed request with its status, never "could not be read"
ok 103 - F2: Auto-Fit on a Cloudflare 524 (plain-text body) is a failed request with its status, never "could not be read"
  ---
  duration_ms: 5.45073
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a 500 with a JSON error is a failed request with its status, never "could not be read"
ok 104 - F2: Auto-Fit on a 500 with a JSON error is a failed request with its status, never "could not be read"
  ---
  duration_ms: 3.084614
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
# duration_ms 7371.402115

exec
/bin/zsh -lc "node -e '
const fs=require('\\''fs'\\''), assert=require('\\''assert'\\''), vm=require('\\''vm'\\''), cp=require('\\''child_process'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const old=cp.execFileSync('\\''git'\\'',['\\''show'\\'','\\''HEAD~1:templates/index.html'\\''],{encoding:'\\''utf8'\\'',stdio:['\\''ignore'\\'','\\''pipe'\\'','\\''ignore'\\'']});
function src(h){return h.slice(h.indexOf('\\''async function _readFitReply('\\''),h.indexOf('\\''\\nasync function runAutoFitC1sGraphite('\\''));}
const read=new Function(src(html)+'\\''; return _readFitReply;'\\'')();
async function kind(s){try{await read({text:async()=>s}); return '\\''valid'\\'';}catch(e){assert(e.serverError&&e.unreadableReply);return /non-finite number/.test(e.message)?'\\''nonfinite'\\'':'\\''unreadable'\\'';}}
(async()=>{
let count=0;
const boundaries=['\\'''\\'','\\''['\\'','\\'','\\'','\\'':'\\'','\\''{'\\'','\\'' '\\'','\\''\\t'\\'','\\''\\r'\\'','\\''\\n'\\'','\\'']'\\'','\\''}'\\''];
for(const pre of boundaries) for(const post of boundaries) for(const token of ['\\''NaN'\\'','\\''Infinity'\\'','\\''-Infinity'\\'']){assert.equal(await kind(pre+token+post),'\\''nonfinite'\\'',JSON.stringify(pre+token+post)); count++;}
for(const pre of ['\\''x'\\'','\\''-'\\'','\\''+'\\'','\\''1'\\'','\\''.'\\'','\\''e'\\'','\\''\"closed\"'\\'']) for(const token of ['\\''NaN'\\'','\\''Infinity'\\'','\\''-Infinity'\\'']) for(const post of ['\\'''\\'','\\'','\\'','\\'']'\\'','\\''}'\\'']) {
 const body=pre+token+post;
 const expected=pre==='\\''-'\\''&&token==='\\''Infinity'\\''?'\\''nonfinite'\\'':'\\''unreadable'\\'';
 assert.equal(await kind(body),expected,JSON.stringify(body));count++;
}
for(const token of ['\\''NaN'\\'','\\''Infinity'\\'','\\''-Infinity'\\'']) for(const suffix of ['\\''x'\\'','\\''0'\\'','\\''-'\\'','\\''+'\\'','\\''.'\\'','\\''\"'\\'']){assert.equal(await kind(token+suffix),'\\''unreadable'\\'');count++;}
for(let n=0;n<40;n++) {assert.equal(await kind('\\''{\"v\":\"'\\''+'\\''\\\\'\\''.repeat(n)+'\\''\", -Infinity'\\''),n%2?'\\''unreadable'\\'':'\\''nonfinite'\\'');count++;}
for(const s of ['\\''{\"v\":\"-Infinity\"}'\\'','\\''{\"v\":\"x-Infinity\"}'\\'','\\''{\"v\":1e999}'\\'','\\''[\"NaN\",\"Infinity\"]'\\'']){assert.equal(await kind(s),'\\''valid'\\'');count++;}
console.log('\\''Boundary, escape and valid-JSON assertions passed:'\\'',count);
const testSource=fs.readFileSync('\\''tests/js/fit_acceptance.test.js'\\'','\\''utf8'\\'');
for(const [name,h] of [['\\''HEAD'\\'',html],['\\''HEAD~1'\\'',old]]){
 let promise, selected=0;
 const req=id=>id==='\\''node:test'\\''?{test:(label,fn)=>{if(label.startsWith('\\''a minus sign counts only'\\'')){selected++;promise=Promise.resolve().then(fn);}}}:id==='\\''node:fs'\\''?{...fs,readFileSync:(p,...args)=>String(p).endsWith('\\''templates/index.html'\\'')?h:fs.readFileSync(p,...args)}:require(id);
 vm.runInNewContext(testSource,{require:req,__dirname:process.cwd()+'\\''/tests/js'\\'',console,performance});
 assert.equal(selected,1);
 let failed=false;try{await promise;}catch(e){failed=true;console.log(name,'\\''exact regression failed:'\\'',e.message.split('\\''\\n'\\'')[0]);}
 assert.equal(failed,name==='\\''HEAD~1'\\'');
 if("'!failed)console.log(name,'"'\\''exact regression passed'\\'');
}
assert.equal(src(html).replace(\"(t[i - 1] === '\\''-'\\'' && bound(t[i - 2]))\", \"t[i - 1] === '\\''-'\\''\").replace('\\''   // a sign only after a boundary (round 3)'\\'','\\'''\\''),src(old));
console.log('\\''Confirmed no other _readFitReply changes.'\\'');
for(const [name,s] of [['\\''escaped'\\'','\\''{\"v\":\"'\\''+'\\''\\\\\"'\\''.repeat(5000000)],['\\''digits'\\'','\\''9'\\''.repeat(10000000)+'\\''x'\\''],['\\''near tokens'\\'','\\''x-Infinity '\\''.repeat(909091)]]){const t=performance.now();assert.equal(await kind(s),'\\''unreadable'\\'');console.log(name,s.length,(performance.now()-t).toFixed(1)+'\\'' ms'\\'');}
})().catch(e=>{console.error(e);process.exitCode=1;});'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 347ms:
escaped 10000006 110.9 ms
digits 10000001 105.2 ms
near tokens 10000001 129.0 ms

exec
/bin/zsh -lc "sed -n '1390,1490p' fitting.py; sed -n '1580,1766p' fitting.py; rg -n 'required|box_unverified|success.*bool|isfinite' fitting.py | tail -65; sed -n '8210,8295p' templates/index.html; git diff main..HEAD -- tests/js/fit_acceptance.test.js" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
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

148:    result = np.where(np.isfinite(result), result, 0.0)
217:        core = np.where(np.isfinite(core), core, 0.0)
315:    return np.where(np.isfinite(result), result, 0.0)
1008:    xf, yf = xf[np.isfinite(xf)], yf[np.isfinite(yf)]
1018:        open_min, open_max = not np.isfinite(par.min), not np.isfinite(par.max)
1056:    ``box_unverified`` (with the sides we generated, so they are not
1066:    found.box_unverified, found.search_box = bool(generated), generated
1091:        refined.box_unverified, refined.search_box = False, {}
1120:    local.box_unverified, local.search_box = False, {}
1121:    if searched.box_unverified or not searched.success or local.chisqr < searched.chisqr:
1276:        both = np.isfinite(lo) and np.isfinite(hi)
1280:            if np.isfinite(lo):
1282:            if np.isfinite(hi):
1350:        if not trial.success or trial.redchi is None or not np.isfinite(trial.redchi):
1406:    ok = np.isfinite(r) & np.isfinite(comp_y) & np.isfinite(w2)
1418:    return {"f": None if not np.isfinite(f) else f, "delta_chi2": delta,
1431:# charge-reference anchor: an anchor that is not required must not set the
1433:def _component_required(fit_reduced, params_full, removed_prefixes, y_sub, weights,
1454:    if not refit.success or getattr(refit, "box_unverified", False):
1460:        # redundant anchor read "required", F 992, from a refit stopped early;
1462:        return {"required": None, "f": None, "chi2_with": float(chi2_with), "chi2_without_refit": chi2_without,
1474:    # components) reports "required"; real data never fit to machine precision.
1475:    if not np.isfinite(chi2_without):
1476:        f, required = None, True                     # the rest could not even be fitted without it
1478:        f, required = 0.0, False
1480:        f, required = None, True
1483:        required = f >= SUPPORT_MIN_F
1484:    return {"required": bool(required), "f": f, "chi2_with": float(chi2_with), "chi2_without_refit": chi2_without,
1534:        raise ValueError("At least one peak specification is required")
1710:    # and the support / required F tests clamp their dof to 1, so such a model
1715:    n_data_request = int(np.count_nonzero(np.isfinite(y_sub)))
1743:    # scattered starts and the required-component refit go through it too.
1764:                      f"{par.min:.4f}" if np.isfinite(par.min) else '-inf',
1765:                      f"{par.max:.4f}" if np.isfinite(par.max) else 'inf')
1803:                    if np.isfinite(par.min):
1805:                    if np.isfinite(par.max):
1820:                trial_rank = (getattr(trial, "box_unverified", False), trial_redchi)
1821:                best_rank = (getattr(best_result, "box_unverified", False), best_redchi)
1853:    # ── "Is this component required?" (never changes `result`) ─────────────
1854:    required = None
1858:            required = {"ran": False, "reason": "fit_not_converged"}
1877:                    required = {"ran": False, "reason": "nothing_left"}
1881:                    required = {"ran": True, **_component_required(
1885:                log.exception("required-component refit failed")
1886:                required = {"ran": False, "reason": "error", "error": f"{type(exc).__name__}: {exc}"[:200]}
1921:                    "min": float(par.min) if np.isfinite(par.min) and "min" not in search_box.get(pname, {}) else None,
1922:                    "max": float(par.max) if np.isfinite(par.max) and "max" not in search_box.get(pname, {}) else None,
1981:    if getattr(result, "box_unverified", False):
2012:        "required": required,
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
  return !!(t && _isLocalProvenance(t.modelProvenance));
}
// The designation a tab's MODEL carries: its stored provenance (imported or
// copied), else one derived from its live local result — so that undo
// snapshots and batch copies taken while a local result exists keep it.
// Persistent designation in the Peaks sidebar (visible whatever panel is
// open), refreshed with the peak list and the results.
function _updateLocalModelBanner() {
  const el = document.getElementById('local-model-banner');
  if (!el) return;
  const t = _activeTab();
  // Stack view: entries that DRAW a local source's fit curves carry the
  // designation too (the stack legend rows scroll; this banner does not).
  let stackLocal = [];
  if (t && t.isStack) {
    const tm = (typeof tabManager !== 'undefined' && tabManager) ? tabManager : null;
    stackLocal = (t.entries || []).filter(e => e.visible && e.showFit).map(e => tm && tm._getTab(e.sourceTabId))
      .filter(src => src && _isLocalFit(src.fitResult)).map(src => src.name);
  }
  const previewLocal = (typeof _historyPreview !== 'undefined') && !!_historyPreview && _isLocalFit(_historyPreview.fitResult);
  const modelLocal = !(t && t.isStack) && _isLocalModel();
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
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ULMWvSHl' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-sksgheQ0' (errno=Operation not permitted)
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

exec
/bin/zsh -lc "rg -n 'execFile|spawn|python|parity|test\\(' tests/js/local_lm_descent.test.js; sed -n '1930,2005p' fitting.py; sed -n '8295,8338p' templates/index.html; sed -n '1718,1760p' fitting.py; tail -20 docs/autofit/codex/f2_acceptance_holes_r3_verdict_runA.md; tail -20 docs/autofit/codex/f2_acceptance_holes_r3_verdict_runB.md" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
19:const { execFileSync } = require('node:child_process');
27:  const start = lines.findIndex(l => re.test(l));
71:  const py = fs.existsSync(path.join(REPO_ROOT, 'venv/bin/python3')) ? path.join(REPO_ROOT, 'venv/bin/python3')
72:    : (fs.existsSync('/Users/skyefortier/xps-app/venv/bin/python3') ? '/Users/skyefortier/xps-app/venv/bin/python3' : 'python3');
75:  return JSON.parse(execFileSync(py, ['-c', script, REPO_ROOT, PROJECT], { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }));
101:test('A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters', () => {
117:test('A01 replay: the linked U 4f pair also descends', () => {
131:test('noiseless Gaussian: amplitude 10 started at 5 is recovered', () => {
146:test('acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result', () => {
161:test('a local fit result is Poisson-weighted: objective, weighting and the designated statistic text', () => {
184:test('bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall', () => {
194:test('bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit', () => {
205:test('a weak component the data DO hold is no longer forced up to an amplitude of 1', () => {
214:test('derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)', () => {
227:test('derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum', () => {
240:test('a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence', () => {
250:test('linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)', () => {
309:test('round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point', () => {
316:  else assert.ok(/stall|sensitivity|iteration/i.test(out.message), out.message);
319:test('round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum', () => {
332:test('round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)', () => {
341:test('A01 replay targets converge to constrained stationary points (C1s and U 4f)', () => {
355:test('round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen', () => {
369:test('round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude', () => {
383:test('round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point', () => {
392:test('round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point', () => {
404:test('round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)', () => {
415:test('round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)', () => {
427:test('round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one', () => {
438:test('weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one', () => {
455:test('server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)', () => {
457:  const bridge = path.join(__dirname, 'local_lm_server_parity_backend.py');
458:  const py = fs.existsSync(path.join(REPO_ROOT, 'venv/bin/python3')) ? path.join(REPO_ROOT, 'venv/bin/python3')
459:    : (fs.existsSync('/Users/skyefortier/xps-app/venv/bin/python3') ? '/Users/skyefortier/xps-app/venv/bin/python3' : 'python3');
468:    const server = JSON.parse(execFileSync(py, [bridge, REPO_ROOT], { input: JSON.stringify({ be, inten, peaks: initial, ui }), encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 }));
485:test('the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom', () => {
517:  test(`an LA fit with m free converges across a kernel-width transition — ${c.label}`, () => {
540:  test(`round-2 reproducer converges with m unlocked (m is held) — ${c.label}`, () => {
552:test('recovery from an amplitude of exactly zero (the new floor is not a trap)', () => {
564:test('the local engine refuses a model with no degrees of freedom; one more point and it fits', () => {
        if (amp_par and fwhm_par and amp_par.stderr and fwhm_par.stderr
                and amp_par.value and fwhm_par.value):
            rel_err = np.sqrt(
                (amp_par.stderr / amp_par.value) ** 2
                + (fwhm_par.stderr / fwhm_par.value) ** 2
            )
            param_info["area"]["stderr"] = abs(area) * rel_err

        n_free_comp = sum(1 for n, par in result.params.items() if n.startswith(prefix) and par.vary and par.expr is None)
        support = _component_support(y_sub, fitted_sub, peak_y, weights, n_free_comp, result.nvarys)
        # A linked component follows its parent: it is supported exactly when the
        # parent is (its own removal test would double-count the parent's role).
        individual_peaks.append({
            "id": pid,
            "y": peak_y.tolist(),
            "params": param_info,
            "support": support,
        })

    # A linked component follows its ROOT ancestor (a grandchild follows the
    # root), whatever the request order; a cycle or a missing master leaves
    # its own verdict.
    by_id = {str(ip["id"]): ip for ip in individual_peaks}
    master_of = {str(spec["id"]): spec.get("constrain_to") for spec in peak_specs}

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
            "r_factor": r_factor,
            "n_data": n_data,
            "n_free_params": n_free,
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

codex
All 509 scanner probes passed, including leading `-Infinity`, delimiter boundaries, repeated signs, and escaped strings. The exact new regression passes on HEAD and fails on HEAD~1 at `{"a":x-Infinity}`. The malformed 10 MB probes took 105–129 ms.

The full-unit review has produced no new finding so far. JavaScript tests passed 103 cases; one Python-backed parity test hit the read-only sandbox’s temporary-directory restriction. I’ll check whether that test can run without writing files while the Python tests finish.

exec
/bin/zsh -lc "node -e '
const cp=require('\\''node:child_process'\\''), original=cp.execFileSync;
cp.execFileSync=function(file,args,opts){
 if(/python/.test(file)&&args[0].endsWith('\\''local_lm_server_parity_backend.py'\\'')){
  args=['\\''-B'\\'','\\''-c'\\'','\\''import tempfile; tempfile.tempdir=\"/tmp\"; import runpy, sys; p=sys.argv.pop(1); sys.argv[0]=p; runpy.run_path(p, run_name=\"__main__\")'\\'',...args];
 }
 return original.call(this,file,args,{...opts,env:{...process.env,PYTHONDONTWRITEBYTECODE:'\\''1'\\''}});
};
const nt=require('\\''node:test'\\''), real=nt.test;
nt.test=(name,fn)=>name.startsWith('\\''server parity on GL-type models:'\\'')?real(name,fn):undefined;
require('\\''./tests/js/local_lm_descent.test.js'\\'');
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 4463ms:
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
TAP version 13
# Subtest: server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
ok 1 - server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
  ---
  duration_ms: 4507.000994
  type: 'test'
  ...
1..1
# tests 1
# suites 0
# pass 1
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 4515.248558

exec
/bin/zsh -lc "sed -n '1840,1915p' fitting.py; sed -n '7575,7645p' templates/index.html; sed -n '8025,8125p' templates/index.html; rg -n '"'^def test_'"' tests/test_fit_reproducibility.py; git diff HEAD~1..HEAD --numstat; git status --short" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
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
    search_box = getattr(result, "search_box", {})

    fitted_sub = result.best_fit
    fitted_y = fitted_sub + bg

    # ── Per‑peak results ──────────────────────────────────────────────────────
    individual_peaks = []
    for spec in peak_specs:
        pid = spec["id"]
        prefix = f"p{pid}_"
        peak_y = composite_model.components[
            next(i for i, c in enumerate(composite_model.components)
                 if c.prefix == prefix)
        ].eval(result.params, x=x)

        # Area by numerical integration. abs(): real XPS grids are
        # BE-descending, which makes the raw trapezoid integral negative —
        # the area is a magnitude by convention (matches autofit/engine.py).
        area = float(abs(trapezoid(peak_y, x)))

        # Parameter extraction with stderr
        param_info: dict[str, Any] = {}
        for pname in result.params:
            if pname.startswith(prefix):
                short = pname[len(prefix):]
                par = result.params[pname]
      }),
      signal: ctrl.signal,
    });
    clearTimeout(timer);
    // F2: a non-2xx reply is a failed REQUEST with its status in the message,
    // as Run Fit has done since A0 (a Cloudflare 524 or a gunicorn 500 used to
    // reach the parser and read as "the server's reply could not be read")
    if (resp.ok === false) {
      let msg = null;
      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
      const err = new Error(msg || ('Fit request failed (HTTP ' + resp.status + ').'));
      err.httpStatus = resp.status;
      throw err;
    }
    const json = await _readFitReply(resp);   // F2: an unreadable reply is a failed fit with its own message
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
  if (!Number.isFinite(lo) || !Number.isFinite(hi)) {
    // Fall back to full raw range (no UI ROI set yet)
    let rmin = Infinity, rmax = -Infinity;
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
    let resp, json;
    try {
      resp = await fetch('/api/fit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(fitReq)
      });
    } catch (e) { _asTransport(e); }
    if (resp.ok === false) {
      // HTTP failure: read a message if the body is JSON, but a 502 HTML
      // page is still a SERVER failure, never a reason to switch engines.
      let msg = null;
      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
      const err = new Error(msg || ('Fit request failed (HTTP ' + resp.status + ').'));
      err.serverError = true;
      throw err;
    }
    // F2: reading the body can fail in transport; a body that was read but is
    // not JSON is the server's reply — a failed fit, not a fallback
    try { json = await _readFitReply(resp); } catch (e) { _asTransport(e); }
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
87:def test_perturbed_starts_are_byte_identical_with_a_deterministic_method(monkeypatch):
101:def test_trust_region_perturbation_draws_are_exactly_identical(monkeypatch):
139:def test_repeated_fits_are_byte_identical(method):
166:def test_stochastic_methods_get_request_derived_seeds_not_the_global_generator(monkeypatch, method, n_perturb, n_min):
185:def test_deterministic_methods_receive_no_solver_seed(monkeypatch, method):
198:def test_the_seed_is_a_pure_function_of_what_the_optimiser_is_given():
229:def test_the_seed_derivation_is_pinned():
241:def test_the_response_reports_its_seed():
249:def test_a_caller_supplied_seed_wins_and_is_reported():
260:def test_api_fit_from_separate_uploads_repeats(client, method, exact):
283:def test_a_cosmetic_rename_does_not_change_the_fit():
293:def test_a_setting_that_is_inert_for_the_shape_does_not_change_the_fit(which):
308:def test_methods_outside_the_supported_five_are_refused_centrally(method):
316:def test_a_differently_cased_method_name_is_the_same_seeded_method(monkeypatch):
330:def test_the_analyze_wrapper_cannot_reach_an_unseeded_method():
338:def test_a_caller_seed_works_with_the_deterministic_methods(method):
347:def test_an_unusable_caller_seed_is_a_validation_error_not_a_silent_fallback(seed):
364:def test_the_perturbation_draws_run_fit_makes_are_pinned(monkeypatch):
374:def test_another_seed_gives_other_draws(monkeypatch):
384:def test_a_background_setting_the_method_ignores_does_not_change_the_fit():
399:def test_bounds_that_cannot_act_and_values_a_constraint_overrides_do_not_change_the_seed():
409:def test_a_broken_constraint_is_still_a_solver_failure_not_a_crash():
433:def test_peak_ids_do_not_change_the_fit(ids):
445:def test_linked_peaks_are_hashed_by_position_too():
452:def test_counts_held_in_float32_give_the_same_fit_as_float64():
458:def test_a_negative_zero_count_is_the_same_request():
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-GRbpPGvj' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-DtB0OGoH' (errno=Operation not permitted)
3452	0	docs/autofit/codex/f2_acceptance_holes_r3_verdict_runA.md
3394	0	docs/autofit/codex/f2_acceptance_holes_r3_verdict_runB.md
8	0	docs/autofit/codex/f2_acceptance_holes_recheck3_prompt.txt
7	0	docs/superpowers/plans/2026-09-26-f2-acceptance-holes.md
1	1	templates/index.html
11	0	tests/js/fit_acceptance.test.js
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-QbVBrbxK' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-GReakliB' (errno=Operation not permitted)
?? docs/autofit/codex/f2_acceptance_holes_r4_verdict_runA.md
?? docs/autofit/codex/f2_acceptance_holes_r4_verdict_runB.md

 exited 2 in 140749ms:
.............
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! KeyboardInterrupt !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/model.py:954: KeyboardInterrupt
(to show a full traceback on KeyboardInterrupt use --full-trace)
13 passed, 1 deselected in 140.19s (0:02:20)

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"-q\", \"-p\", \"no:cacheprovider\", \"-s\", \"tests/test_fit_reproducibility.py::test_stochastic_methods_get_request_derived_seeds_not_the_global_generator\", \"tests/test_fit_reproducibility.py::test_a_differently_cased_method_name_is_the_same_seeded_method\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
codex
The parity test passed after a temporary-directory setting was supplied in memory; no files needed to be written. All 104 JavaScript cases have now passed.

The full-unit pass found no additional issue. All 11 focused Python acceptance and basinhopping tests passed. I stopped the broader reproducibility run to keep this review bounded and am finishing the three reproducibility cases changed by F2.

 succeeded in 62922ms:
...
3 passed in 62.55s (0:01:02)

codex
No BLOCKER, MAJOR, or MINOR findings.

- Confirmed HEAD changes only the Infinity boundary condition in production code.
- All 509 scanner probes passed, including leading `-Infinity`, delimiter/whitespace positions, repeated signs, and escaped strings. Malformed 10 MB bodies completed in 105–129 ms.
- The exact regression test passes on HEAD and fails on HEAD~1 at `{"a":x-Infinity}`.
- Reviewed the full `main..HEAD` unit diff; found no additional acceptance hole.

Validation: 104 JavaScript cases and 16 Python cases passed. The upload-fixture test was excluded under read-only restrictions; the broader Python run was stopped after 13 passes, then all three changed reproducibility cases passed separately. No files changed.

**VERDICT: GO**
tokens used
77,757
No BLOCKER, MAJOR, or MINOR findings.

- Confirmed HEAD changes only the Infinity boundary condition in production code.
- All 509 scanner probes passed, including leading `-Infinity`, delimiter/whitespace positions, repeated signs, and escaped strings. Malformed 10 MB bodies completed in 105–129 ms.
- The exact regression test passes on HEAD and fails on HEAD~1 at `{"a":x-Infinity}`.
- Reviewed the full `main..HEAD` unit diff; found no additional acceptance hole.

Validation: 104 JavaScript cases and 16 Python cases passed. The upload-fixture test was excluded under read-only restrictions; the broader Python run was stopped after 13 passes, then all three changed reproducibility cases passed separately. No files changed.

**VERDICT: GO**
